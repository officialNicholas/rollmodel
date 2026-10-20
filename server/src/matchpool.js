// Matches on worker threads (src/matchworker.js). The main thread keeps every connection and the lobby; each match runs
// on one of N workers, picked by fewest players. A MatchProxy stands in for the match on the main thread: the server
// calls it exactly as it calls a Match, and it forwards to the worker, keeping a mirror of what the server reads back
// (phase, results, and each player's state, place and knock-outs).
// Messages to a worker go in batches, at most one postMessage a millisecond; movement reports and snapshots packed into
// one buffer each way.
import { Worker } from 'node:worker_threads';
import { performance } from 'node:perf_hooks';
import { codec, MSG } from '../client/rmnet.js';
import { randomId, seed32 } from './util.js';
import { MODE_INFO } from './constants.js';
import { createHost } from './matchworker.js';

const WORKER = new URL('./matchworker.js', import.meta.url), STATE_REC = 12 + codec.STATE_BYTES;

export class MatchPool {
  // inline (the tests): each "worker" runs in this thread, through the same messages, cloned and a turn of the event
  // loop apart as they would be between threads, so the whole suite exercises this path and can still look inside a match
  constructor(srv, n, { inline = false } = {}) {
    this.srv = srv; this.n = n; this.inline = inline; this.workers = []; this.byId = new Map();
    for (let i = 0; i < n; i++) this._spawn(i);
  }
  _spawn(i) {
    const s = this.srv;
    if (this.inline) {
      const W = { i, out: [], flushing: false, players: 0, stats: null, ready: true, dead: false, sbuf: null, slen: 0 };
      W.host = createHost({ index: i, rules: s.rules, log: s.log }, (ops, packed) => { const o = structuredClone(ops), pk = packed ? packed.slice(0) : null; setImmediate(() => this._batch(W, o, pk)); });
      this.workers[i] = W; return;
    }
    const w = new Worker(WORKER, { workerData: { index: i, timeOrigin: performance.timeOrigin, rules: s.rules, logLevel: s.log.levelName ? s.log.levelName() : 'info' } });
    const W = { i, w, out: [], flushing: false, players: 0, stats: null, ready: false, dead: false, sbuf: null, slen: 0 };
    w.on('message', ([ops, packed]) => this._batch(W, ops, packed));
    w.on('error', e => s.log.error('match worker failed', { worker: i, err: e.stack || e.message }));
    w.on('exit', code => this._exit(W, code));
    w.unref();
    this.workers[i] = W;
  }
  // a worker gone (a crash): its matches are lost; tell their players, and start a fresh worker
  _exit(W, code) {
    W.dead = true;
    if (this.stopping) return;
    this.srv.log.error('match worker exited', { worker: W.i, code });
    for (const m of [...this.byId.values()]) if (m.W === W) {
      for (const p of m.P) if (p.sess) this.srv.sendJson(p.sess, { t: 'matchCancelled', matchId: m.id, reason: 'server_error' });
      m.phase = 'closed'; this.byId.delete(m.id); this.srv.onMatchClosed(m, { cancelled: true, reason: 'server_error', culprits: [] });
    }
    this._spawn(W.i);
  }
  send(W, op) { W.out.push(op); this._soon(W); }
  // a movement report: packed into the batch's one buffer (sid, receive time, the 34 bytes), its place in the order kept by
  // an ['S', n] marker: the next n reports in the buffer
  sendState(W, sid, recv, data) {
    if (!W.sbuf || W.slen + STATE_REC > W.sbuf.length) { const nb = Buffer.allocUnsafe(Math.max(4096, (W.sbuf ? W.sbuf.length : 0) * 2)); if (W.sbuf) W.sbuf.copy(nb, 0, 0, W.slen); W.sbuf = nb; }
    const b = W.sbuf, o = W.slen; b.writeUInt32LE(sid >>> 0, o); b.writeDoubleLE(recv, o + 4); b.set(data, o + 12); W.slen += STATE_REC;
    const last = W.out[W.out.length - 1]; if (last && last[0] === 'S') last[1]++; else W.out.push(['S', 1]);
    this._soon(W);
  }
  _soon(W) {
    if (W.flushing) return;
    W.flushing = true;
    // (a millisecond's batch: under load, flushing every turn of the event loop meant a hand-off per incoming message)
    setTimeout(() => {
      W.flushing = false; const o = W.out; W.out = []; if (!o.length || W.dead) return;
      let packed = null; if (W.slen) { packed = W.sbuf.buffer.slice(W.sbuf.byteOffset, W.sbuf.byteOffset + W.slen); W.slen = 0; }
      if (W.host) W.host.receive(structuredClone(o), packed); else W.w.postMessage([o, packed], packed ? [packed] : []);
    }, 1);
  }
  create(srv, { mode, sessions, rated, room, seed }) {
    let W = this.workers[0]; for (const x of this.workers) if (x.players < W.players) W = x;
    const m = new MatchProxy(this, W, { id: randomId('m_', 10), mode, sessions, rated, room, seed: seed === undefined ? seed32() : seed >>> 0 });
    this.byId.set(m.id, m); W.players += m.P.length;
    return m;
  }
  // a batch from a worker: ops in order; ['B', n] is the next n binary sends from the packed buffer (sid, droppable, length,
  // bytes). Every socket written to is corked for the batch, so a player's messages in it go out in one write.
  _batch(W, ops, packed) {
    const s = this.srv, corked = [], cork = sess => { const so = sess.ws && sess.ws._socket; if (so && !sess._corked) { sess._corked = true; so.cork(); corked.push(sess); } };
    const buf = packed ? Buffer.from(packed) : null; let at = 0;
    for (const op of ops) {
      try {
        if (op[0] === 'B') {
          for (let k = 0; k < op[1]; k++) {
            const sid = buf.readUInt32LE(at), drop = buf[at + 4] === 1, len = buf.readUInt16LE(at + 5), bytes = buf.subarray(at + 7, at + 7 + len); at += 7 + len;
            const x = s.bySid.get(sid); if (x) { cork(x); s.sendBinary(x, bytes, drop); }
          }
          continue;
        }
        if (op[0] === 'j') { const x = s.bySid.get(op[1]); if (x) { cork(x); s.sendRaw(x, op[2]); } continue; }
        this._in(W, op);
      } catch (e) { s.log.error('worker message failed', { op: op[0], err: e.stack || e.message }); }
    }
    for (const x of corked) { x._corked = false; const so = x.ws && x.ws._socket; if (so) so.uncork(); }
  }
  _gone(m) { if (this.byId.delete(m.id)) m.W.players -= m.P.length; }
  _in(W, op) {
    const s = this.srv, sess = () => s.bySid.get(op[1]);
    switch (op[0]) {
      case 'bad': { const x = sess(); if (x) s._bad(x, op[2]); return; }
      case 'kick': { const x = sess(); if (x) s.kick(x, op[2]); return; }
      case 'flag': s.flag(op[1], op[2], op[3]); return;
      case 'stats': W.stats = op[1]; s.stats.violations += op[1].violations; return;
      case 'ready': W.ready = true; return;
    }
    const m = this.byId.get(op[1]); if (!m) return;
    switch (op[0]) {
      case 'sync': m.phase = op[2]; m._mirror(op[3]); return;
      case 'end': m.phase = 'ended'; m.results = op[2]; m._mirror(op[4]); s.onMatchEnd(m, op[3] ? new Map(op[3]) : null); return;
      case 'closed': m.phase = 'closed'; m._mirror(op[3]); this._gone(m); s.onMatchClosed(m, op[2]); return;
      case 'rematch': m.phase = 'closed'; m._mirror(op[2]); this._gone(m); s.rematch(m); return;
    }
  }
  // what /health shows about the workers
  health() {
    return this.workers.map(W => {
      if (W.host) return { worker: W.i, players: W.players, matches: W.host.matches.size, inline: true, tick: W.stats ? W.stats.tick : null };
      const now = W.w.performance.eventLoopUtilization(), elu = W.elu0 ? W.w.performance.eventLoopUtilization(now, W.elu0).utilization : now.utilization; W.elu0 = now;
      return { worker: W.i, players: W.players, matches: W.stats ? W.stats.matches : 0, elu: +elu.toFixed(3), cpu: W.stats ? +W.stats.cpu.toFixed(3) : 0, tick: W.stats ? W.stats.tick : null };
    });
  }
  // wait (up to ms) for every match to have closed and said so
  async drain(ms) { const t0 = Date.now(); while (this.byId.size && Date.now() - t0 < ms) await new Promise(r => setTimeout(r, 10)); }
  async stop() { this.stopping = true; await Promise.all(this.workers.map(W => (W.host ? W.host.stop() : W.w.terminate().catch(() => {})))); }
}

// the main thread's stand-in for a match running on a worker
export class MatchProxy {
  constructor(pool, W, { id, mode, sessions, rated, room, seed }) {
    this.pool = pool; this.W = W; this.id = id; this.mode = mode; this.rated = rated; this.room = room; this.seed = seed;
    this.phase = 'consensus'; this.results = null; this.layoutHash = null;
    this.P = sessions.map((s, slot) => ({ slot, sess: s, id: s.player.id, side: MODE_INFO[mode].sides[slot], st: 'wait', place: 0, kos: 0, connected: !!s.ws, queuedAt: 0 }));
    this.spec = { id, mode, rated, seed, room: room ? { code: room.code } : null, players: sessions.map(s => ({ sid: s.id, connected: !!s.ws, player: { id: s.player.id, name: s.player.name, look: s.player.look, ratings: s.player.ratings } })) };
  }
  get active() { return this.phase !== 'closed'; }
  playerById(id) { return this.P.find(p => p.id === id) || null; }
  _mirror(ps) { ps.forEach((x, i) => { const p = this.P[i]; if (p) { p.st = x[0]; p.place = x[1]; p.kos = x[2]; p.connected = x[3]; } }); }
  _send(op) { this.pool.send(this.W, op); }
  start() { this._send(['create', this.spec]); this.spec = null; }
  tick() {} // (the worker keeps the match's clock)
  onState(p, data, recv) {
    // the obviously broken are turned away here; the rest is the worker's to judge. (Copied: the socket's buffer can be a
    // slice of a much bigger one, and a worker would be sent all of it.)
    if (data.length !== codec.STATE_BYTES || data[0] !== MSG.STATE) return 'malformed';
    this.pool.sendState(this.W, p.sess.id, recv, data);
  }
  onAction(p, m, recv) { this._send(['act', this.id, p.id, m, recv]); }
  onLayout(p, m) { this._send(['layout', this.id, p.id, m]); }
  onRematch(p, vote) { this._send(['rematch', this.id, p.id, vote]); }
  onDisconnect(p) { if (p.st === 'left') return; p.sess = null; p.connected = false; this._send(['disc', this.id, p.id]); }
  onReconnect(p, sess) { p.sess = sess; p.connected = true; this._send(['reconn', this.id, p.id, sess.id]); }
  forfeit(p, why) { this._send(['forfeit', this.id, p.id, why, !p.sess]); }
  cancel(reason) { this._send(['cancel', this.id, reason]); }
  close(reason) { this._send(['close', this.id, reason]); }
  summary() { return { id: this.id, mode: this.mode, phase: this.phase, players: this.P.map(p => ({ id: p.id, st: p.st, connected: p.connected })) }; }
}
