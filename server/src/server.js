// The game server: HTTP (/health), WebSockets, sessions, the lobby, and the clock that drives every match.
import http from 'node:http';
import { WebSocketServer } from 'ws';
import { PROTOCOL_VERSION, MSG, codec } from '../client/rmnet.js';
import { MODE_INFO, DEFAULT_RULES, LIMITS } from './constants.js';
import { createLogger } from './log.js';
import { MemoryStore, JsonFileStore } from './store.js';
import { sanitizeName, sanitizeLook } from './names.js';
import { connectionLimits, noteDrop } from './ratelimit.js';
import { Matchmaker, Room, uniqueCode } from './lobby.js';
import { Match } from './match.js';
import { nowMs, Window, summarize } from './util.js';
import { performance } from 'node:perf_hooks';

const CLOSE = { NORMAL: 1000, AWAY: 1001, VERSION: 4000, REPLACED: 4001, KICKED: 4003, HELLO: 4004, POLICY: 4008 };
const JSON_TYPES = new Set(['hello', 'queue', 'cancelQueue', 'createRoom', 'joinRoom', 'leaveRoom', 'ready', 'setName', 'layout', 'act', 'rematch', 'leaveMatch', 'bye']);

export class GameServer {
  // opts: { port, host, store, dataFile, log, logLevel, rules, allowedOrigins, maxConnections, maxPerIp, trustProxy, shutdownGraceMs }
  constructor(opts = {}) {
    this.opts = opts;
    this.log = opts.log || createLogger({ level: opts.logLevel || 'info', base: { svc: 'rollmodel' } });
    this.rules = Object.assign({}, DEFAULT_RULES, opts.rules || {});
    this.store = opts.store || (opts.dataFile && opts.dataFile !== 'memory' ? new JsonFileStore(opts.dataFile) : new MemoryStore());
    this.sessions = new Set(); this.online = new Map(); this.inMatch = new Map(); this.matches = new Set(); this.rooms = new Map();
    this.mm = new Matchmaker(); this.perIp = new Map(); this.connSeq = 0; this.closing = false;
    this.stats = { connections: 0, messages: 0, violations: 0, kicked: 0, matchesStarted: 0, matchesEnded: 0, matchesCancelled: 0, bytesOut: 0, framesOut: 0 };
    this.tickTimes = new Window(8192); this.tickCpu = new Window(8192); this.startedAt = nowMs(); this._timer = null; this._nextTick = 0; this._lastMM = 0; this._lastPing = 0;
  }

  async listen(port = this.opts.port ?? 8080, host = this.opts.host || '0.0.0.0') {
    await this.store.init();
    this.http = http.createServer((req, res) => this._http(req, res));
    this.wss = new WebSocketServer({ noServer: true, maxPayload: LIMITS.maxPayload, perMessageDeflate: false, clientTracking: false });
    this.http.on('upgrade', (req, socket, head) => this._upgrade(req, socket, head));
    await new Promise((resolve, reject) => { this.http.once('error', reject); this.http.listen(port, host, () => { this.http.off('error', reject); resolve(); }); });
    this.port = this.http.address().port;
    this._nextTick = nowMs(); this._loop();
    this.log.info('listening', { port: this.port, host, proto: PROTOCOL_VERSION });
    return this;
  }

  // ------------------------------------------------------------------------------------------------ http
  _http(req, res) {
    const [url, query] = (req.url || '/').split('?');
    if (req.method === 'GET' && url === '/health') {
      const win = parseInt(new URLSearchParams(query || '').get('window'), 10);
      const body = JSON.stringify(this.health(Number.isFinite(win) && win > 0 ? win : 0));
      res.writeHead(this.closing ? 503 : 200, { 'content-type': 'application/json', 'cache-control': 'no-store' }); res.end(body); return;
    }
    if (req.method === 'GET' && url === '/') { res.writeHead(200, { 'content-type': 'text/plain' }); res.end('Roll Model game server\n'); return; }
    res.writeHead(404, { 'content-type': 'text/plain' }); res.end('not found\n');
  }
  // window: only the last N ticks (0: all kept). elu: how busy the event loop was since the previous health call.
  health(window = 0) {
    const vals = this.tickTimes.values(), t = summarize(window ? vals.slice(-window) : vals);
    const cv = this.tickCpu.values(), tc = summarize(window ? cv.slice(-window) : cv);
    const elu = performance.eventLoopUtilization(this._elu); this._elu = performance.eventLoopUtilization();
    // processor time used since the last health call, as a share of one core (unlike elu, not inflated when the machine
    // is busy with other work)
    const cpuNow = process.cpuUsage(), wallNow = nowMs(), c0 = this._cpu || { u: { user: 0, system: 0 }, w: this.startedAt };
    const cpu = ((cpuNow.user - c0.u.user) + (cpuNow.system - c0.u.system)) / 1000 / Math.max(1, wallNow - c0.w); this._cpu = { u: cpuNow, w: wallNow };
    const mem = process.memoryUsage();
    return {
      ok: !this.closing, proto: PROTOCOL_VERSION, uptime: Math.round((nowMs() - this.startedAt) / 1000),
      connections: this.sessions.size, players: this.online.size, matches: this.matches.size, rooms: this.rooms.size, queues: this.mm.sizes(),
      tick: { p50: +t.p50.toFixed(3), p99: +t.p99.toFixed(3), max: +t.max.toFixed(3), n: t.n, cpuP50: +tc.p50.toFixed(3), cpuP99: +tc.p99.toFixed(3) },
      elu: +elu.utilization.toFixed(3), cpu: +cpu.toFixed(3),
      memMB: Math.round(mem.rss / 1048576), stats: this.stats,
    };
  }
  _ip(req) {
    if (this.opts.trustProxy) { const f = req.headers['x-forwarded-for']; if (typeof f === 'string' && f) return f.split(',')[0].trim(); }
    return req.socket.remoteAddress || '?';
  }
  _upgrade(req, socket, head) {
    const reject = (code, text) => { try { socket.write('HTTP/1.1 ' + code + ' ' + text + '\r\nConnection: close\r\nContent-Length: 0\r\n\r\n'); } catch (e) { /* gone */ } socket.destroy(); };
    if (this.closing) return reject(503, 'Service Unavailable');
    if ((req.url || '/').split('?')[0] !== '/ws' && (req.url || '/').split('?')[0] !== '/') return reject(404, 'Not Found');
    const origin = req.headers.origin, allow = this.opts.allowedOrigins || [];
    if (origin && allow.length && !allow.includes(origin)) return reject(403, 'Forbidden');
    const ip = this._ip(req);
    if (this.sessions.size >= (this.opts.maxConnections || 5000)) return reject(503, 'Service Unavailable');
    if ((this.perIp.get(ip) || 0) >= (this.opts.maxPerIp || 64)) return reject(429, 'Too Many Requests');
    this.wss.handleUpgrade(req, socket, head, ws => this._connected(ws, req, ip));
  }

  // ------------------------------------------------------------------------------------------------ sessions
  _connected(ws, req, ip) {
    if (req.socket.setNoDelay) req.socket.setNoDelay(true); // no Nagle delay: small packets go out at once
    const sess = { id: ++this.connSeq, ws, ip, player: null, lim: connectionLimits(), queued: null, room: null, match: null, slot: -1, bad: 0, rtt: 0, at: nowMs(), lastMsg: nowMs(), bytesOut: 0, closed: false };
    this.sessions.add(sess); this.perIp.set(ip, (this.perIp.get(ip) || 0) + 1); this.stats.connections++;
    sess.helloTimer = setTimeout(() => { if (!sess.player) this._close(sess, CLOSE.HELLO, 'hello timeout'); }, LIMITS.helloTimeoutMs);
    ws.on('message', (data, isBinary) => this._message(sess, data, isBinary));
    ws.on('close', () => this._closed(sess));
    ws.on('error', e => this.log.debug('socket error', { conn: sess.id, err: e.message }));
  }
  _closed(sess) {
    if (sess.closed) return; sess.closed = true;
    clearTimeout(sess.helloTimer); this.sessions.delete(sess);
    const n = (this.perIp.get(sess.ip) || 1) - 1; if (n > 0) this.perIp.set(sess.ip, n); else this.perIp.delete(sess.ip);
    if (!sess.player) return;
    if (this.online.get(sess.player.id) === sess) this.online.delete(sess.player.id);
    this.mm.remove(sess);
    if (sess.match) { const p = sess.match.playerById(sess.player.id); if (p && p.sess === sess) sess.match.onDisconnect(p); }
    else if (sess.room) this._leaveRoom(sess, true);
    sess.ws = null;
  }
  _close(sess, code, reason) { try { if (sess.ws) sess.ws.close(code, reason); } catch (e) { /* already closed */ } }
  sendJson(sess, obj) {
    if (!sess || !sess.ws || sess.ws.readyState !== 1) return false;
    const s = JSON.stringify(obj); sess.bytesOut += s.length; this.stats.bytesOut += s.length + (s.length < 126 ? 2 : 4); this.stats.framesOut++;
    sess.ws.send(s); return true;
  }
  // droppable: a snapshot may be skipped for a connection that is falling behind (the next one supersedes it)
  sendBinary(sess, bytes, droppable = false) {
    if (!sess || !sess.ws || sess.ws.readyState !== 1) return false;
    if (droppable && sess.ws.bufferedAmount > 64 * 1024) { sess.skipped = (sess.skipped || 0) + 1; return false; }
    sess.bytesOut += bytes.byteLength; this.stats.bytesOut += bytes.byteLength + (bytes.byteLength < 126 ? 2 : 4); this.stats.framesOut++;
    sess.ws.send(bytes, { binary: true }); return true;
  }
  sendError(sess, code, message, r, fatal = false) { this.sendJson(sess, { t: 'error', code, message, r, fatal: fatal || undefined }); }
  kick(sess, reason) {
    if (!sess || sess.closed) return;
    this.stats.kicked++; this.log.warn('kicked', { conn: sess.id, player: sess.player && sess.player.id, reason });
    if (sess.match && sess.player) { const p = sess.match.playerById(sess.player.id); if (p) sess.match.forfeit(p, 'kicked'); }
    this.sendJson(sess, { t: 'kicked', reason });
    this._close(sess, CLOSE.KICKED, reason);
  }
  flag(id, reason, details) { this.log.warn('flagged', { player: id, reason }); this.store.flag(id, reason, details).catch(e => this.log.error('store flag failed', { err: e.message })); }
  _bad(sess, what) {
    sess.bad++; if (sess.bad <= 5) this.sendError(sess, 'bad_message', what);
    if (sess.bad > 25) this.kick(sess, 'protocol');
  }

  // ------------------------------------------------------------------------------------------------ messages
  // never let one message take the process down: anything unexpected is logged and that client is told
  _message(sess, data, isBinary) {
    try { this._onMessage(sess, data, isBinary); } catch (e) {
      this.stats.errors = (this.stats.errors || 0) + 1;
      this.log.error('message failed', { conn: sess.id, err: e.stack || e.message });
      this.sendError(sess, 'server', 'server error');
    }
  }
  _onMessage(sess, data, isBinary) {
    if (sess.closed) return;
    const now = nowMs(); sess.lastMsg = now; this.stats.messages++;
    if (isBinary) return this._binary(sess, data, now);
    const len = data.length;
    // only a layout may be big, and only while that player's match is collecting layouts
    const layoutTime = sess.match && sess.match.phase === 'consensus';
    if (len > (layoutTime ? LIMITS.maxLayoutJson : LIMITS.maxJson)) { if (noteDrop(sess.lim, now)) return this.kick(sess, 'flood'); return this._bad(sess, 'message too large'); }
    if (!sess.lim.json.take(1, now)) { if (noteDrop(sess.lim, now)) this.kick(sess, 'flood'); return; }
    let m; try { m = JSON.parse(data.toString('utf8')); } catch (e) { return this._bad(sess, 'not JSON'); }
    if (!m || typeof m !== 'object' || Array.isArray(m) || typeof m.t !== 'string') return this._bad(sess, 'no type');
    if (!JSON_TYPES.has(m.t)) return this._bad(sess, 'unknown type ' + String(m.t).slice(0, 20));
    if (m.r !== undefined && !(Number.isInteger(m.r) && m.r >= 0 && m.r < 2 ** 31)) return this._bad(sess, 'bad request id');
    if (m.t === 'hello') return this._hello(sess, m);
    if (sess.helloing) { (sess.pending = sess.pending || []).push(m); if (sess.pending.length > 20) this._bad(sess, 'too many messages before welcome'); return; }
    if (!sess.player) return this.sendError(sess, 'no_hello', 'say hello first', m.r);
    this._safeHandle(sess, m, now);
  }
  _safeHandle(sess, m, now) {
    try { this._handle(sess, m, now); } catch (e) { this.log.error('handler failed', { t: m.t, err: e.stack || e.message }); this.sendError(sess, 'server', 'server error', m.r); }
  }
  _binary(sess, data, now) {
    if (!data.length) return this._bad(sess, 'empty');
    const type = data[0];
    if (type === MSG.PING) {
      if (!sess.lim.ping.take(1, now)) { if (noteDrop(sess.lim, now)) this.kick(sess, 'flood'); return; }
      const c = codec.decodePing(data); if (c === null) return this._bad(sess, 'bad ping');
      return this.sendBinary(sess, new Uint8Array(codec.encodePong(c, nowMs())));
    }
    if (!sess.player) return this._bad(sess, 'say hello first');
    if (type === MSG.STATE) {
      if (!sess.lim.state.take(1, now)) { if (noteDrop(sess.lim, now)) this.kick(sess, 'flood'); return; }
      if (!sess.match) return;
      const p = sess.match.playerById(sess.player.id); if (!p || p.sess !== sess) return;
      if (sess.match.onState(p, data, now) === 'malformed') this._bad(sess, 'bad state');
      return;
    }
    if (type === MSG.SPONG) {
      if (!sess.lim.ping.take(1, now)) return;
      const t = codec.decodeSPong(data); if (t === null || t > now || now - t > 30000) return this._bad(sess, 'bad pong');
      const rtt = now - t; sess.rtt = sess.rtt ? sess.rtt + (rtt - sess.rtt) * 0.25 : rtt; return;
    }
    this._bad(sess, 'unknown binary type');
  }
  async _hello(sess, m) {
    if (sess.player || sess.helloing) return this.sendError(sess, 'already', 'already said hello', m.r);
    if (m.v !== PROTOCOL_VERSION) {
      this.sendJson(sess, { t: 'error', code: 'version', message: 'this server speaks protocol ' + PROTOCOL_VERSION + '; please update the game', server: PROTOCOL_VERSION, fatal: true });
      return this._close(sess, CLOSE.VERSION, 'protocol version');
    }
    sess.helloing = true;
    try {
      const nm = sanitizeName(m.name), look = sanitizeLook(m.look);
      let player = null, token = null;
      if (typeof m.token === 'string') { player = await this.store.getByToken(m.token); if (player) token = m.token; }
      if (!player) { const c = await this.store.create({ name: nm.name, look }); player = c.player; token = c.token; }
      else {
        const patch = { lastSeen: Date.now() };
        if (typeof m.name === 'string' && nm.name !== player.name && !(nm.reason === 'profanity' || nm.reason === 'empty' || nm.reason === 'missing')) patch.name = nm.name;
        if (look) patch.look = look;
        player = await this.store.update(player.id, patch);
      }
      if (sess.closed) return;
      if (player.banned) { this.sendJson(sess, { t: 'error', code: 'banned', message: 'this device is banned', fatal: true }); return this._close(sess, CLOSE.KICKED, 'banned'); }
      // one connection per player: a new one replaces the old (a phone that switched networks)
      const old = this.online.get(player.id);
      if (old && old !== sess) {
        this.sendJson(old, { t: 'kicked', reason: 'replaced' });
        this.mm.remove(old); if (old.room) this._leaveRoom(old, true);
        if (old.match) { const op = old.match.playerById(player.id); if (op && op.sess === old) old.match.onDisconnect(op); old.match = null; }
        this.online.delete(player.id); old.player = null; this._close(old, CLOSE.REPLACED, 'replaced');
      }
      sess.player = player; this.online.set(player.id, sess); clearTimeout(sess.helloTimer);
      const match = this.inMatch.get(player.id);
      const ratings = Object.fromEntries(Object.entries(player.ratings).map(([k, v]) => [k, { r: Math.round(v.r), rd: Math.round(v.rd), games: v.games }]));
      this.sendJson(sess, { t: 'welcome', id: player.id, token, name: player.name, nameChanged: nm.changed || undefined, ratings, serverTime: nowMs(), proto: PROTOCOL_VERSION, resume: match && match.active ? match.id : null, modes: Object.keys(MODE_INFO) });
      if (match && match.active) { const p = match.playerById(player.id); if (p && p.st !== 'left') { sess.match = match; sess.slot = p.slot; match.onReconnect(p, sess); } else this.inMatch.delete(player.id); }
    } catch (e) {
      this.log.error('hello failed', { err: e.stack || e.message }); this.sendError(sess, 'server', 'could not sign in', m.r, true); this._close(sess, CLOSE.KICKED, 'server error');
    } finally {
      sess.helloing = false;
      const queued = sess.pending || []; sess.pending = null;
      if (sess.player && !sess.closed) for (const q of queued) this._safeHandle(sess, q, nowMs());
    }
  }
  _handle(sess, m, now) {
    switch (m.t) {
      case 'queue': {
        if (!MODE_INFO[m.mode]) return this.sendError(sess, 'bad_mode', 'unknown mode', m.r);
        if (sess.match) return this.sendError(sess, 'busy', 'already in a match', m.r);
        if (sess.room) return this.sendError(sess, 'busy', 'leave the room first', m.r);
        this.mm.add(sess, m.mode); this.sendJson(sess, { t: 'queued', mode: m.mode, r: m.r }); return;
      }
      case 'cancelQueue': this.mm.remove(sess); this.sendJson(sess, { t: 'queueLeft', r: m.r }); return;
      case 'createRoom': {
        if (!MODE_INFO[m.mode]) return this.sendError(sess, 'bad_mode', 'unknown mode', m.r);
        if (sess.match || sess.room) return this.sendError(sess, 'busy', 'already in a match or room', m.r);
        this.mm.remove(sess);
        const room = new Room(m.mode, sess); room.code = uniqueCode(this.rooms); room.members.push(sess); this.rooms.set(room.code, room); sess.room = room;
        this.sendJson(sess, Object.assign(room.view(), { r: m.r })); return;
      }
      case 'joinRoom': {
        const code = typeof m.code === 'string' ? m.code.toUpperCase().trim() : '';
        if (sess.match || sess.room) return this.sendError(sess, 'busy', 'already in a match or room', m.r);
        const room = /^[A-Z0-9]{5}$/.test(code) ? this.rooms.get(code) : null;
        if (!room) {
          if (!sess.lim.join.take(1, now)) return this.sendError(sess, 'rate', 'too many wrong codes; wait a little', m.r);
          return this.sendError(sess, 'not_found', 'no room with that code', m.r);
        }
        if (room.members.length >= room.need) return this.sendError(sess, 'full', 'that room is full', m.r);
        if (room.match) return this.sendError(sess, 'busy', 'that room is playing', m.r);
        this.mm.remove(sess); room.members.push(sess); room.ready.set(sess.player.id, false); sess.room = room;
        for (const s of room.members) this.sendJson(s, Object.assign(room.view(), s === sess ? { r: m.r } : {}));
        return;
      }
      case 'leaveRoom': if (!sess.room) return this.sendError(sess, 'no_room', 'not in a room', m.r); this._leaveRoom(sess); this.sendJson(sess, { t: 'roomLeft', r: m.r }); return;
      case 'ready': {
        const room = sess.room; if (!room || room.match) return;
        room.ready.set(sess.player.id, m.ready === true);
        for (const s of room.members) this.sendJson(s, room.view());
        if (room.allReady()) this._startMatch(room.mode, room.members.slice(), { room, rated: false });
        return;
      }
      case 'setName': {
        const nm = sanitizeName(m.name);
        this.store.update(sess.player.id, { name: nm.name }).then(p => { if (p) sess.player.name = p.name; this.sendJson(sess, { t: 'name', name: nm.name, changed: nm.changed, r: m.r }); });
        return;
      }
      case 'layout': {
        const match = sess.match; if (!match || m.m !== match.id) return this.sendError(sess, 'not_in_match', 'not in that match', m.r);
        const p = match.playerById(sess.player.id); if (p && p.sess === sess) match.onLayout(p, m); return;
      }
      case 'act': {
        if (!sess.lim.act.take(1, now)) { if (noteDrop(sess.lim, now)) this.kick(sess, 'flood'); return; }
        const match = sess.match; if (!match) return this.sendJson(sess, { t: 'ack', n: Number.isInteger(m.n) ? m.n : undefined, a: m.a, ok: false, reason: 'not_in_match' });
        const p = match.playerById(sess.player.id); if (!p || p.sess !== sess) return;
        if (match.onAction(p, m, now) === 'bad') this._bad(sess, 'bad action');
        return;
      }
      case 'rematch': { const match = sess.match; if (!match) return; const p = match.playerById(sess.player.id); if (p) match.onRematch(p, m.vote === true); return; }
      case 'leaveMatch': { const match = sess.match; if (!match) return; const p = match.playerById(sess.player.id); if (p) match.forfeit(p, 'quit'); this._detach(sess, match); this.sendJson(sess, { t: 'matchClosed', matchId: match.id, reason: 'you_left', r: m.r }); return; }
      case 'bye': this.mm.remove(sess); return;
    }
  }
  _leaveRoom(sess, silent) {
    const room = sess.room; if (!room) return;
    room.members = room.members.filter(s => s !== sess); room.ready.delete(sess.player.id); sess.room = null;
    if (!room.members.length) { this.rooms.delete(room.code); return; }
    if (room.host === sess.player.id) room.host = room.members[0].player.id;
    for (const s of room.members) this.sendJson(s, room.view());
  }

  // ------------------------------------------------------------------------------------------------ matches
  _startMatch(mode, sessions, { room = null, rated = true, seed } = {}) {
    for (const s of sessions) this.mm.remove(s);
    const match = new Match(this, { mode, sessions, rated, room, seed });
    this.matches.add(match); this.stats.matchesStarted++;
    if (room) room.match = match;
    for (const s of sessions) { s.match = match; s.slot = sessions.indexOf(s); this.inMatch.set(s.player.id, match); }
    match.start();
    return match;
  }
  _detach(sess, match) { if (sess.match === match) { sess.match = null; sess.slot = -1; } if (sess.player && this.inMatch.get(sess.player.id) === match) this.inMatch.delete(sess.player.id); }
  // a match ended for good (cancelled, closed after the rematch vote, or replaced by its rematch)
  onMatchClosed(match, { cancelled, reason, culprits = [] }) {
    this.matches.delete(match);
    if (cancelled) this.stats.matchesCancelled++;
    const now = nowMs();
    for (const p of match.P) {
      const sess = p.sess;
      if (this.inMatch.get(p.id) === match) this.inMatch.delete(p.id);
      if (!sess || sess.closed || sess.match !== match) continue;
      sess.match = null; sess.slot = -1;
      // back to matchmaking after a cancelled queue match (not the ones who caused it), keeping their place in line
      if (cancelled && !match.room && p.st !== 'left' && !culprits.includes(p.id) && !this.closing) { this.mm.add(sess, match.mode, p.queuedAt || now); this.sendJson(sess, { t: 'queued', mode: match.mode, requeued: true }); }
    }
    if (match.room) {
      const room = match.room; room.match = null; room.ready = new Map(room.members.map(s => [s.player.id, false]));
      room.members = room.members.filter(s => !s.closed);
      if (!room.members.length) this.rooms.delete(room.code); else for (const s of room.members) this.sendJson(s, room.view());
    }
    this.log.info('match closed', { match: match.id, cancelled, reason });
  }
  // results are in: save ratings and stats
  onMatchEnd(match, ratings) {
    this.stats.matchesEnded++;
    const res = match.results;
    (async () => {
      for (const p of match.P) {
        const cur = await this.store.get(p.id); if (!cur) continue;
        const patch = { stats: Object.assign({}, cur.stats, { matches: (cur.stats.matches || 0) + 1, wins: (cur.stats.wins || 0) + (p.place === 1 && res.winner === p.side ? 1 : 0), kos: (cur.stats.kos || 0) + p.kos }) };
        if (ratings && ratings.get(p.id)) { patch.ratings = Object.assign({}, cur.ratings, { [match.mode]: ratings.get(p.id) }); }
        const upd = await this.store.update(p.id, patch);
        const sess = this.online.get(p.id); if (sess && sess.player && upd) { sess.player.ratings = upd.ratings; sess.player.stats = upd.stats; }
      }
      await this.store.recordMatch(Object.assign({ at: new Date().toISOString(), seed: match.seed, layoutHash: match.layoutHash }, res));
    })().catch(e => this.log.error('saving results failed', { err: e.stack || e.message }));
  }
  rematch(old) {
    this.matches.delete(old);
    const sessions = old.P.map(p => p.sess);
    for (const p of old.P) if (this.inMatch.get(p.id) === old) this.inMatch.delete(p.id);
    if (sessions.some(s => !s || s.closed)) { for (const s of sessions) if (s && !s.closed) { s.match = null; this.sendJson(s, { t: 'matchClosed', matchId: old.id, reason: 'rematch_failed' }); } return; }
    for (const s of sessions) { s.match = null; }
    this._startMatch(old.mode, sessions, { room: old.room, rated: old.rated });
  }

  // ------------------------------------------------------------------------------------------------ the clock
  _loop() {
    const hz = this.rules.snapshotHz || 30, step = 1000 / hz;
    const run = () => {
      if (this.closing) return;
      const t0 = nowMs(), c0 = process.cpuUsage();
      try { this._tick(t0); } catch (e) { this.log.error('tick failed', { err: e.stack || e.message }); }
      const t1 = nowMs(), c1 = process.cpuUsage(c0); this.tickTimes.push(t1 - t0); this.tickCpu.push((c1.user + c1.system) / 1000);
      this._nextTick += step; if (this._nextTick < t1 - step) this._nextTick = t1; // fell far behind: do not race to catch up
      this._timer = setTimeout(run, Math.max(0, this._nextTick - nowMs()));
    };
    this._timer = setTimeout(run, step);
  }
  _tick(now) {
    if (now - this._lastMM >= 250) {
      this._lastMM = now;
      for (const g of this.mm.form(now)) {
        for (const t of g.tickets) t.sess.queuedAt = t.at;
        const m = this._startMatch(g.mode, g.tickets.map(t => t.sess), { rated: true });
        for (const p of m.P) p.queuedAt = g.tickets[p.slot].at;
      }
    }
    for (const m of [...this.matches]) {
      try { m.tick(now); } catch (e) {
        // one broken match must not stop the others: call it off
        this.stats.errors = (this.stats.errors || 0) + 1;
        this.log.error('match tick failed', { match: m.id, err: e.stack || e.message });
        try { if (m.phase === 'ended') m.close('server_error'); else m.cancel('server_error'); } catch (e2) { this.matches.delete(m); }
      }
    }
    if (now - this._lastPing >= 2000) { this._lastPing = now; const b = new Uint8Array(codec.encodeSPing(now)); for (const s of this.sessions) if (s.player) this.sendBinary(s, b, true); }
  }

  // ------------------------------------------------------------------------------------------------ shutdown
  async close() {
    if (this.closing) return; this.closing = true;
    clearTimeout(this._timer);
    this.log.info('shutting down', { connections: this.sessions.size, matches: this.matches.size });
    for (const m of [...this.matches]) { if (m.phase === 'play' || m.phase === 'countdown' || m.phase === 'consensus') m.cancel('server_shutdown'); else m.close('server_shutdown'); }
    for (const s of [...this.sessions]) { this.sendJson(s, { t: 'server', msg: 'shutdown' }); this._close(s, CLOSE.AWAY, 'server shutdown'); }
    const grace = this.opts.shutdownGraceMs ?? 3000;
    await new Promise(resolve => { const t = setTimeout(resolve, grace); const iv = setInterval(() => { if (!this.sessions.size) { clearTimeout(t); clearInterval(iv); resolve(); } }, 20); setTimeout(() => clearInterval(iv), grace + 10); });
    for (const s of [...this.sessions]) { try { s.ws && s.ws.terminate(); } catch (e) { /* gone */ } this._closed(s); }
    await new Promise(resolve => this.http.close(() => resolve()));
    await this.store.close();
    this.log.info('stopped');
  }
}

export async function createGameServer(opts = {}) { const s = new GameServer(opts); await s.listen(opts.port ?? 0, opts.host || '127.0.0.1'); return s; }
