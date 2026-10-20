// A match worker thread: runs matches handed to it by the main thread (src/matchpool.js), on its own clock, so one
// process can referee more players than one core can. The main thread keeps every connection and the lobby; this
// thread keeps the matches. Messages each way go in batches; movement reports in and snapshots out are packed into one
// buffer per batch (['S', n] and ['B', n] mark their places among the other messages).
//
// In:  ['create', spec] ['S', n] (n packed movement reports: sid, receive time, bytes) ['act', mid, pid, m, recv] ['layout', mid, pid, m]
//      ['rematch', mid, pid, vote] ['disc', mid, pid] ['reconn', mid, pid, sid] ['forfeit', mid, pid, why, detach]
//      ['cancel', mid, reason] ['close', mid, reason] ['stop']
// Out: ['j', sid, json] ['B', n] (n packed binary sends: sid, droppable, length, bytes) ['bad', sid, what] ['kick', sid, reason] ['flag', id, reason, details]
//      ['sync', mid, phase, players] ['end', mid, results, ratings, players] ['closed', mid, info, players]
//      ['rematch', mid, players] ['stats', { violations, tick }]
import { isMainThread, parentPort, workerData } from 'node:worker_threads';
import { Match } from './match.js';
import { codec } from '../client/rmnet.js';
import { createLogger } from './log.js';
import { nowMs, Window, summarize } from './util.js';

// the host: everything a worker does, given where to send its batches. (The tests run one in the main thread, through
// the same messages: src/matchpool.js, 'inline'.)
export function createHost(data, postBatch) {
  const log = data.log || createLogger({ level: data.logLevel || 'info', base: { svc: 'rollmodel', worker: data.index } });
  const matches = new Map(), bySid = new Map(); // (bySid: who a movement report is from, connection id -> [match id, player id])
  let out = [], flushing = false, violations = 0, timer = null;
  const tickTimes = new Window(4096), tickCpu = new Window(4096);

  let bbuf = null, blen = 0;
  function post(op) { out.push(op); if (!flushing) { flushing = true; setImmediate(flush); } }
  // a binary send (snapshots): packed into the batch's one buffer (sid, droppable, length, bytes), its place in the
  // order kept by a ['B', n] marker
  function postBinary(sid, bytes, droppable) {
    const need = 7 + bytes.byteLength;
    if (!bbuf || blen + need > bbuf.length) { const nb = Buffer.allocUnsafe(Math.max(16384, (bbuf ? bbuf.length : 0) * 2, blen + need)); if (bbuf) bbuf.copy(nb, 0, 0, blen); bbuf = nb; }
    bbuf.writeUInt32LE(sid >>> 0, blen); bbuf[blen + 4] = droppable ? 1 : 0; bbuf.writeUInt16LE(bytes.byteLength, blen + 5); bbuf.set(bytes, blen + 7); blen += need;
    const last = out[out.length - 1]; if (last && last[0] === 'B') last[1]++; else out.push(['B', 1]);
    if (!flushing) { flushing = true; setImmediate(flush); }
  }
  function flush() {
    flushing = false; if (!out.length) return; const o = out; out = [];
    let packed = null; if (blen) { packed = bbuf.buffer.slice(bbuf.byteOffset, bbuf.byteOffset + blen); blen = 0; }
    postBatch(o, packed);
  }
  // a player as the main thread mirrors it
  const brief = m => m.P.map(p => [p.st, p.place, p.kos, p.connected]);

  // what a Match calls on its server
  const srv = {
    rules: data.rules, log,
    stats: { get violations() { return violations; }, set violations(v) { violations = v; } },
    sendJson(sess, obj) { if (sess && sess.ws) post(['j', sess.sid, JSON.stringify(obj)]); return true; },
    sendBinary(sess, bytes, droppable = false) { if (sess && sess.ws) postBinary(sess.sid, bytes, droppable); return true; },
    flag(id, reason, details) { post(['flag', id, reason, details]); },
    kick(sess, reason) { if (sess) post(['kick', sess.sid, reason]); },
    onMatchEnd(match, ratings) { post(['end', match.id, match.results, ratings ? [...ratings] : null, brief(match)]); },
    onMatchClosed(match, info) { forget(match); matches.delete(match.id); post(['closed', match.id, info, brief(match)]); },
    rematch(match) { forget(match); matches.delete(match.id); post(['rematch', match.id, brief(match)]); },
  };
  const forget = m => { for (const [sid, w] of bySid) if (w[0] === m.id) bySid.delete(sid); };
  // a connection, as far as a match can tell (the socket stays on the main thread)
  const stub = (sid, player) => ({ sid, ws: true, player });

  function handle(op) {
    const m = op[0] === 'create' ? null : matches.get(op[1]);
    switch (op[0]) {
      case 'create': {
        const s = op[1], match = new Match(srv, { id: s.id, mode: s.mode, rated: s.rated, room: s.room, seed: s.seed, sessions: s.players.map(p => Object.assign(stub(p.sid, p.player), { sb: p.sb || null }, p.bot ? { bot: true, ownerId: p.ownerId } : {})) });
        for (let i = 0; i < s.players.length; i++) if (!s.players[i].connected) { match.P[i].connected = false; match.P[i].sess = null; match.P[i].awaySince = nowMs(); }
        for (const p of s.players) bySid.set(p.sid, [match.id, p.player.id]);
      matches.set(match.id, match); match.start(); return;
      }
      case 'stop': for (const x of [...matches.values()]) { if (x.phase === 'play' || x.phase === 'countdown' || x.phase === 'consensus') x.cancel('server_shutdown'); else x.close('server_shutdown'); } return;
    }
    if (!m) return; // (gone: a message still on its way when it closed)
    const p = m.playerById(op[2]);
    switch (op[0]) {
      case 'state': if (p && m.onState(p, op[3], op[4]) === 'malformed' && p.sess) post(['bad', p.sess.sid, 'bad state']); break;
      case 'act': if (p && m.onAction(p, op[3], op[4]) === 'bad' && p.sess) post(['bad', p.sess.sid, 'bad action']); break;
      case 'layout': if (p) m.onLayout(p, op[3]); break;
      case 'rematch': if (p) m.onRematch(p, op[3]); break;
      case 'disc': if (p) m.onDisconnect(p); break;
      case 'reconn': if (p) { bySid.set(op[3], [m.id, p.id]); m.onReconnect(p, stub(op[3], { id: p.id, name: p.name, look: p.look })); } break;
      case 'forfeit': if (p) { if (op[4]) p.sess = null; m.forfeit(p, op[3]); } break;
      case 'cancel': m.cancel(op[2]); break;
      case 'close': m.close(op[2]); break;
    }
    if (matches.has(m.id) && m.phase !== m._sentPhase) { m._sentPhase = m.phase; post(['sync', m.id, m.phase, brief(m)]); }
  }
  function receive(ops, packed) {
    const buf = packed ? Buffer.from(packed) : null; let at = 0;
    for (const op of ops) {
      try {
        if (op[0] === 'S') {
          for (let k = 0; k < op[1]; k++, at += 12 + codec.STATE_BYTES) {
            const w = bySid.get(buf.readUInt32LE(at)); if (!w) continue;
            handle(['state', w[0], w[1], buf.subarray(at + 12, at + 12 + codec.STATE_BYTES), buf.readDoubleLE(at + 4)]);
          }
          continue;
        }
        handle(op);
      } catch (e) { log.error('match op failed', { op: op[0], err: e.stack || e.message }); }
    }
  }

  // the clock: every match on this thread, snapshotHz times a second (the same loop the main thread runs in-process)
  const step = 1000 / (data.rules.snapshotHz || 30);
  let next = nowMs() + step, lastStats = 0, lastCpu = null;
  function run() {
    const t0 = nowMs(), c0 = process.cpuUsage();
    for (const m of [...matches.values()]) {
      try { m.tick(t0); } catch (e) {
        log.error('match tick failed', { match: m.id, err: e.stack || e.message });
        try { if (m.phase === 'ended') m.close('server_error'); else m.cancel('server_error'); } catch (e2) { matches.delete(m.id); }
      }
      if (matches.has(m.id) && m.phase !== m._sentPhase) { m._sentPhase = m.phase; post(['sync', m.id, m.phase, brief(m)]); }
    }
    const t1 = nowMs(), c1 = process.cpuUsage(c0); tickTimes.push(t1 - t0); tickCpu.push((c1.user + c1.system) / 1000);
    if (t1 - lastStats >= 1000) {
      const uc = process.threadCpuUsage ? process.threadCpuUsage() : null, cpu = uc && lastCpu ? ((uc.user - lastCpu.user) + (uc.system - lastCpu.system)) / 1000 / (t1 - lastStats) : 0; lastCpu = uc;
      lastStats = t1; const tt = summarize(tickTimes.values().slice(-300)), tc = summarize(tickCpu.values().slice(-300));
      post(['stats', { cpu, violations, matches: matches.size, players: [...matches.values()].reduce((a, x) => a + x.P.length, 0), tick: { p50: tt.p50, p99: tt.p99, max: tt.max, cpuP50: tc.p50, cpuP99: tc.p99 } }]);
      violations = 0;
    }
    next += step; if (next < t1 - step) next = t1;
    timer = setTimeout(run, Math.max(0, next - nowMs()));
  }
  timer = setTimeout(run, step);
  return { receive, matches, stop: () => clearTimeout(timer) };
}

if (!isMainThread && parentPort) {
  const host = createHost(workerData, (ops, packed) => parentPort.postMessage([ops, packed], packed ? [packed] : []));
  parentPort.on('message', ([ops, packed]) => host.receive(ops, packed));
  parentPort.postMessage([[['ready']], null]);
}
