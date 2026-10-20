// The game server: HTTP (/health), WebSockets, sessions, the lobby, and the clock that drives every match.
import http from 'node:http';
import { WebSocketServer } from 'ws';
import { PROTOCOL_VERSION, MSG, codec } from '../client/rmnet.js';
import { MODE_INFO, DEFAULT_RULES, LIMITS } from './constants.js';
import { createLogger } from './log.js';
import { MemoryStore, JsonFileStore } from './store.js';
import { RemoteStore } from './storeclient.js';
import { startStoreApi } from './storeapi.js';
import { sanitizeName, sanitizeLook } from './names.js';
import { connectionLimits, noteDrop } from './ratelimit.js';
import { Matchmaker, Room, uniqueCode, makeTicket, regionOf } from './lobby.js';
import { Party, PARTY, planFor, newPartyCode, playsTrio } from './party.js';
import { Match } from './match.js';
import { Pusher } from './push.js';
import { MatchPool } from './matchpool.js';
import { availableParallelism } from 'node:os';
import { nowMs, Window, summarize, fin } from './util.js';
import { performance } from 'node:perf_hooks';

const CLOSE = { NORMAL: 1000, AWAY: 1001, VERSION: 4000, REPLACED: 4001, KICKED: 4003, HELLO: 4004, POLICY: 4008 };
const JSON_TYPES = new Set(['hello', 'queue', 'cancelQueue', 'createRoom', 'joinRoom', 'leaveRoom', 'ready', 'setName', 'layout', 'act', 'rematch', 'leaveMatch', 'bye',
  'partyCreate', 'partyJoin', 'partyLeave', 'partyKick', 'partyReady', 'partyVote', 'partyLook', 'partyBusy', 'partyReact', 'partyInvite', 'partyDecline', 'poke']);
// what this server offers beyond the first protocol (the game checks before it shows parties)
const CAPS = ['party'];
// a Supabase user id (the game's friends live there): the address of an invite or a poke
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const POKES = new Set(['invite', 'request', 'answer']);

// a room member: who they are, kept on the connection (a dropped one keeps its place for a while)
const roomMember = sess => Object.assign(sess, { roomPid: sess.player.id, roomName: sess.player.name, roomLook: sess.player.look });

export class GameServer {
  // opts: { port, host, store, dataFile, log, logLevel, rules, allowedOrigins, maxConnections, maxPerIp, trustProxy, shutdownGraceMs }
  constructor(opts = {}) {
    this.opts = opts;
    this.log = opts.log || createLogger({ level: opts.logLevel || 'info', base: { svc: 'rollmodel' } });
    this.rules = Object.assign({}, DEFAULT_RULES, opts.rules || {});
    // several machines: one keeps the store and serves it to the others (storeUrl), see storeapi.js
    this.store = opts.store || (opts.storeUrl ? new RemoteStore(opts.storeUrl, opts.internalKey) : opts.dataFile && opts.dataFile !== 'memory' ? new JsonFileStore(opts.dataFile) : new MemoryStore());
    this.shardId = opts.shardId || 'local'; // (this machine, for routing a player back to it: Fly's machine id)
    this.sessions = new Set(); this.bySid = new Map(); this.online = new Map(); this.inMatch = new Map(); this.matches = new Set(); this.rooms = new Map();
    this.roomAway = new Map(); // player id -> the dropped connection whose place in a room is being kept
    this.parties = new Map(); // join code -> party
    this.partyAway = new Map(); // player id -> the party keeping a dropped member's place
    this.bySb = new Map(); // Supabase user id -> the connections of that player (for invites and pokes)
    this.push = opts.pusher || new Pusher(opts.push || null, { log: this.log }); // (v391: an invite to a friend whose game is closed, as a notification)
    this.mm = new Matchmaker(); this.perIp = new Map(); this.connSeq = 0; this.closing = false;
    this.stats = { connections: 0, messages: 0, violations: 0, kicked: 0, matchesStarted: 0, matchesEnded: 0, matchesCancelled: 0, bytesOut: 0, framesOut: 0 };
    this.tickTimes = new Window(8192); this.tickCpu = new Window(8192); this.startedAt = nowMs(); this._timer = null; this._nextTick = 0; this._lastMM = 0; this._lastPing = 0; this._lastSilent = 0;
  }

  async listen(port = this.opts.port ?? 8080, host = this.opts.host || '0.0.0.0') {
    await this.store.init();
    this.http = http.createServer((req, res) => this._http(req, res));
    this.wss = new WebSocketServer({ noServer: true, maxPayload: LIMITS.maxPayload, perMessageDeflate: false, clientTracking: false });
    this.http.on('upgrade', (req, socket, head) => this._upgrade(req, socket, head));
    await new Promise((resolve, reject) => { this.http.once('error', reject); this.http.listen(port, host, () => { this.http.off('error', reject); resolve(); }); });
    this.port = this.http.address().port;
    // matches on worker threads: matchWorkers 0 runs them here (the tests' default), 'auto' one per core but this one
    // ('inline': the tests' way to run the same path in this thread, see matchpool.js)
    const mw = this.opts.matchWorkers, nw = mw === 'auto' ? Math.max(1, availableParallelism() - 1) : mw === 'inline' ? 1 : Math.max(0, parseInt(mw, 10) || 0);
    if (nw > 0) this.pool = new MatchPool(this, nw, { inline: mw === 'inline' });
    this._nextTick = nowMs(); this._loop();
    if (this.opts.internalKey && !this.opts.storeUrl && this.opts.internalPort !== undefined) {
      this.storeApi = await startStoreApi({ store: this.store, key: this.opts.internalKey, port: this.opts.internalPort, host: this.opts.internalHost || '::', log: this.log });
      this.internalPort = this.storeApi.address().port;
    }
    this.log.info('listening', { port: this.port, host, proto: PROTOCOL_VERSION, matchWorkers: nw, shard: this.shardId, store: this.opts.storeUrl ? 'remote' : this.storeApi ? 'serving' : 'local' });
    this.push.announce();
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
      connections: this.sessions.size, players: this.online.size, matches: this.matches.size, rooms: this.rooms.size, parties: this.parties.size, queues: this.mm.sizes(),
      tick: { p50: +t.p50.toFixed(3), p99: +t.p99.toFixed(3), max: +t.max.toFixed(3), n: t.n, cpuP50: +tc.p50.toFixed(3), cpuP99: +tc.p99.toFixed(3) },
      elu: +elu.utilization.toFixed(3), cpu: +cpu.toFixed(3),
      memMB: Math.round(mem.rss / 1048576), stats: this.stats, mainCpu: +this._mainCpu(wallNow).toFixed(3), workers: this.pool ? this.pool.health() : undefined,
    };
  }
  // the main thread's own processor time since the last call, as a share of one core (cpu above is the whole process)
  _mainCpu(now) {
    if (!process.threadCpuUsage) return 0;
    const u = process.threadCpuUsage(), c0 = this._mcpu || { u: { user: 0, system: 0 }, w: this.startedAt }; this._mcpu = { u, w: now };
    return ((u.user - c0.u.user) + (u.system - c0.u.system)) / 1000 / Math.max(1, now - c0.w);
  }
  _ip(req) {
    // behind a proxy: Fly.io's own header first (set by its edge, so a client can't fake it), then the usual one
    if (this.opts.trustProxy) { const fc = req.headers['fly-client-ip']; if (typeof fc === 'string' && fc) return fc.trim(); const f = req.headers['x-forwarded-for']; if (typeof f === 'string' && f) return f.split(',')[0].trim(); }
    return req.socket.remoteAddress || '?';
  }
  _upgrade(req, socket, head) {
    const reject = (code, text) => { try { socket.write('HTTP/1.1 ' + code + ' ' + text + '\r\nConnection: close\r\nContent-Length: 0\r\n\r\n'); } catch (e) { /* gone */ } socket.destroy(); };
    if (this.closing) return reject(503, 'Service Unavailable');
    const [path, query] = (req.url || '/').split('?');
    if (path !== '/ws' && path !== '/') return reject(404, 'Not Found');
    // ?s=<machine>: this connection belongs on another machine (a match or a room there): Fly's proxy takes the reply's
    // fly-replay header and hands the connection to that machine
    const want = query ? new URLSearchParams(query).get('s') : null;
    if (want && want !== this.shardId && this.opts.flyReplay && /^[A-Za-z0-9_-]{1,64}$/.test(want)) {
      try { socket.write('HTTP/1.1 409 Conflict\r\nfly-replay: instance=' + want + '\r\nConnection: close\r\nContent-Length: 0\r\n\r\n'); } catch (e) { /* gone */ }
      socket.destroy(); return;
    }
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
    const sess = { id: ++this.connSeq, ws, ip, player: null, lim: connectionLimits(), queued: null, room: null, party: null, match: null, slot: -1, bad: 0, rtt: 0, at: nowMs(), lastMsg: nowMs(), lastPing: 0, busyAt: 0, bytesOut: 0, closed: false, sb: null, region: '', tzo: null };
    this.sessions.add(sess); this.bySid.set(sess.id, sess); this.perIp.set(ip, (this.perIp.get(ip) || 0) + 1); this.stats.connections++;
    sess.helloTimer = setTimeout(() => { if (!sess.player) this._close(sess, CLOSE.HELLO, 'hello timeout'); }, LIMITS.helloTimeoutMs);
    ws.on('message', (data, isBinary) => this._message(sess, data, isBinary));
    ws.on('close', () => this._closed(sess));
    ws.on('error', e => this.log.debug('socket error', { conn: sess.id, err: e.message }));
  }
  // a connection in a match, a queue or a party that is starting (pinged every 2 s; the game pings twice a second)
  _busy(s) { return !!(s.match || s.queued || (s.party && s.party.state !== 'idle')); }
  _closed(sess) {
    if (sess.closed) return; sess.closed = true;
    clearTimeout(sess.helloTimer); this.sessions.delete(sess); this.bySid.delete(sess.id);
    const n = (this.perIp.get(sess.ip) || 1) - 1; if (n > 0) this.perIp.set(sess.ip, n); else this.perIp.delete(sess.ip);
    if (!sess.player) return;
    if (this.online.get(sess.player.id) === sess) this.online.delete(sess.player.id);
    this._sbOff(sess);
    this.mm.remove(sess);
    if (sess.match) { const p = sess.match.playerById(sess.player.id); if (p && p.sess === sess) sess.match.onDisconnect(p); }
    else if (sess.room) this._roomAway(sess);
    if (sess.party) this._partyAway(sess);
    sess.ws = null;
  }
  _close(sess, code, reason) { try { if (sess.ws) sess.ws.close(code, reason); } catch (e) { /* already closed */ } }
  sendJson(sess, obj) {
    if (!sess || !sess.ws || sess.ws.readyState !== 1) return false;
    const s = JSON.stringify(obj); sess.bytesOut += s.length; this.stats.bytesOut += s.length + (s.length < 126 ? 2 : 4); this.stats.framesOut++;
    sess.ws.send(s); return true;
  }
  // a message already in JSON (from a match worker)
  sendRaw(sess, s) {
    if (!sess || !sess.ws || sess.ws.readyState !== 1) return false;
    sess.bytesOut += s.length; this.stats.bytesOut += s.length + (s.length < 126 ? 2 : 4); this.stats.framesOut++;
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
    // only a layout may be big, and only while that player's match is collecting layouts; an invite carries the inviter's
    // Supabase token for its notification, so it may be a little bigger than the rest
    const layoutTime = sess.match && sess.match.phase === 'consensus', invite = len > LIMITS.maxJson && len <= LIMITS.maxInviteJson && data.toString('utf8', 0, 20).startsWith('{"t":"partyInvite"');
    if (len > (layoutTime ? LIMITS.maxLayoutJson : invite ? LIMITS.maxInviteJson : LIMITS.maxJson)) { if (noteDrop(sess.lim, now)) return this.kick(sess, 'flood'); return this._bad(sess, 'message too large'); }
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
      const t = codec.decodeSPong(data); if (t === null || t > now) return this._bad(sess, 'bad pong');
      if (now - t > 30000) return; // (a late answer, from a game that was held up for a while: not a bad message, just no use)
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
        this.mm.remove(old); if (old.room) this._roomAway(old); // (its place in a room goes to the new connection, below)
        if (old.party) this._partyAway(old); // (and its place in a party)
        if (old.match) { const op = old.match.playerById(player.id); if (op && op.sess === old) old.match.onDisconnect(op); old.match = null; }
        this._sbOff(old); this.online.delete(player.id); old.player = null; this._close(old, CLOSE.REPLACED, 'replaced');
      }
      sess.player = player; this.online.set(player.id, sess); clearTimeout(sess.helloTimer);
      // where the player is (for matchmaking: near first) and who they are among friends (for invites)
      if (typeof m.zone === 'string') sess.region = regionOf(m.zone);
      if (fin(m.tzo) && Math.abs(m.tzo) <= 900) sess.tzo = Math.round(m.tzo);
      if (typeof m.sb === 'string' && UUID.test(m.sb)) this._sbOn(sess, m.sb);
      sess.client = typeof m.client === 'string' && m.client.length <= 32 ? m.client : ''; // (which game: what it can play in a party)
      const match = this.inMatch.get(player.id);
      const ratings = Object.fromEntries(Object.entries(player.ratings).map(([k, v]) => [k, { r: Math.round(v.r), rd: Math.round(v.rd), games: v.games }]));
      this.sendJson(sess, { t: 'welcome', id: player.id, token, name: player.name, nameChanged: nm.changed || undefined, ratings, serverTime: nowMs(), proto: PROTOCOL_VERSION, shard: this.shardId, resume: match && match.active ? match.id : null, modes: Object.keys(MODE_INFO), caps: CAPS, partyModes: this.partyModes() });
      if (match && match.active) { const p = match.playerById(player.id); if (p && p.st !== 'left') { sess.match = match; sess.slot = p.slot; match.onReconnect(p, sess); } else this.inMatch.delete(player.id); }
      if (!sess.match) this._roomBack(sess);
      this._partyBack(sess);
    } catch (e) {
      // (not fatal: a store that couldn't be reached is usually back in a moment, and the phone reconnects by itself)
      this.log.error('hello failed', { err: e.stack || e.message }); this.sendError(sess, 'busy', 'could not sign in; trying again', m.r); this._close(sess, CLOSE.AWAY, 'server busy');
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
        if (sess.party && sess.party.size > 1) return this.sendError(sess, 'busy', 'in a party: everyone readies up instead', m.r);
        this.mm.add(sess, m.mode); this.sendJson(sess, { t: 'queued', mode: m.mode, r: m.r }); return;
      }
      case 'cancelQueue': this._unqueue(sess, 'cancelled'); this.sendJson(sess, { t: 'queueLeft', r: m.r }); return;
      case 'createRoom': {
        if (!MODE_INFO[m.mode]) return this.sendError(sess, 'bad_mode', 'unknown mode', m.r);
        if (sess.match || sess.room || sess.creating) return this.sendError(sess, 'busy', 'already in a match or room', m.r);
        this.mm.remove(sess);
        sess.creating = true;
        this._claimCode().then(code => {
          sess.creating = false; if (sess.closed || sess.match || sess.room) { this.store.releaseRoom(code, this.shardId).catch(() => {}); return; }
          const room = new Room(m.mode, sess); room.code = code; room.members.push(roomMember(sess)); this.rooms.set(room.code, room); sess.room = room;
          this.sendJson(sess, Object.assign(room.view(), { r: m.r }));
        }, e => { sess.creating = false; this.log.error('room code failed', { err: e.message }); this.sendError(sess, 'busy', 'could not make a room; try again', m.r); });
        return;
      }
      case 'joinRoom': {
        const code = typeof m.code === 'string' ? m.code.toUpperCase().trim() : '';
        if (sess.room && sess.room.code === code && !sess.match) return this.sendJson(sess, Object.assign(sess.room.view(), { r: m.r })); // (already back in it)
        if (sess.match || sess.room) return this.sendError(sess, 'busy', 'already in a match or room', m.r);
        const room = /^[A-Z0-9]{5}$/.test(code) ? this.rooms.get(code) : null;
        if (!room) {
          if (!sess.lim.join.take(1, now)) return this.sendError(sess, 'rate', 'too many wrong codes; wait a little', m.r);
          if (!/^[A-Z0-9]{5}$/.test(code)) return this.sendError(sess, 'not_found', 'no room with that code', m.r);
          // a room on another machine: the phone reconnects there (?s=) and joins it
          this.store.findRoom(code).then(shard => {
            if (shard && shard !== this.shardId) { sess.lim.join.tokens = Math.min(sess.lim.join.burst, sess.lim.join.tokens + 1); this.sendJson(sess, { t: 'error', code: 'room_elsewhere', message: 'that room is on another server', shard, r: m.r }); }
            else this.sendError(sess, 'not_found', 'no room with that code', m.r);
          }, () => this.sendError(sess, 'busy', 'could not look up the room; try again', m.r));
          return;
        }
        if (room.members.length >= room.need) return this.sendError(sess, 'full', 'that room is full', m.r);
        if (room.match) return this.sendError(sess, 'busy', 'that room is playing', m.r);
        this.mm.remove(sess); room.members.push(roomMember(sess)); room.ready.set(sess.player.id, false); sess.room = room;
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
        // a new name (the game renamed you): the party sees it at once, the next match too. One the filter turns away, or
        // none, leaves the name there is, as at hello
        const nm = sanitizeName(m.name);
        if (nm.reason === 'profanity' || nm.reason === 'empty' || nm.reason === 'missing') return this.sendJson(sess, { t: 'name', name: sess.player.name, changed: true, r: m.r });
        this.store.update(sess.player.id, { name: nm.name }).then(p => {
          if (sess.closed || !sess.player) return;
          if (p) sess.player.name = p.name; this.sendJson(sess, { t: 'name', name: sess.player.name, changed: nm.changed, r: m.r });
          const me = p && sess.party && sess.party.member(sess.player.id); if (me) { me.name = p.name; this._partySend(sess.party); } // (the party sees it too)
        }, e => { this.log.warn('rename failed', { player: sess.player && sess.player.id, err: e && e.message }); this.sendError(sess, 'busy', 'could not change the name; try again', m.r); });
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
      case 'leaveMatch': {
        const match = sess.match; if (!match) return this.sendError(sess, 'not_in_match', 'not in a match', m.r);
        const p = match.playerById(sess.player.id);
        this._detach(sess, match);
        // the match sends nothing more to this connection (it may be in a new match soon); its player forfeits
        if (p && p.sess === sess) { p.sess = null; match.forfeit(p, 'quit'); }
        this.sendJson(sess, { t: 'matchClosed', matchId: match.id, reason: 'you_left', r: m.r }); return;
      }
      case 'bye': this._unqueue(sess, 'left'); return;
      default: return this._partyMsg(sess, m, now);
    }
  }
  // takes a player out of the queue; a party's ticket goes as a whole, and the rest of the party is told
  _unqueue(sess, why) { const t = this.mm.remove(sess); if (t && t.party) this._partyIdle(t.party, why, sess); return t; }

  // ------------------------------------------------------------------------------------------------ parties
  // The modes parties may play on this server (rules.partyModes), from the ones a party can vote for.
  partyModes() { const on = Array.isArray(this.rules.partyModes) ? this.rules.partyModes : PARTY.MODES; return PARTY.MODES.filter(x => on.includes(x)); }
  _partyMsg(sess, m, now) {
    const pid = sess.player.id, party = sess.party, me = party && party.member(pid);
    const need = () => { if (!me) { this.sendError(sess, 'no_party', 'not in a party', m.r); return false; } return true; };
    switch (m.t) {
      case 'partyCreate': {
        if (party) return this.sendJson(sess, Object.assign(party.view(this.partyModes()), { r: m.r })); // (already in one)
        if (sess.match || sess.room) return this.sendError(sess, 'busy', 'in a match or a room', m.r);
        const p = new Party(newPartyCode(this.parties)); this.parties.set(p.code, p);
        p.add(sess); sess.party = p;
        this.log.info('party made', { party: p.id, player: pid });
        return this.sendJson(sess, Object.assign(p.view(this.partyModes()), { r: m.r }));
      }
      case 'partyJoin': {
        const code = typeof m.code === 'string' ? m.code.toUpperCase().trim() : '';
        if (party && party.code === code) return this.sendJson(sess, Object.assign(party.view(this.partyModes()), { r: m.r })); // (already in it)
        const p = /^[A-Z0-9]{8}$/.test(code) ? this.parties.get(code) : null;
        if (!p) { if (!sess.lim.join.take(1, now)) return this.sendError(sess, 'rate', 'too many tries; wait a little', m.r); return this.sendError(sess, 'not_found', 'that party has closed', m.r); }
        if (p.kicked.has(pid) && !p.liveInvites().some(i => i.to === sess.sb)) return this.sendError(sess, 'not_found', 'that party has closed', m.r);
        if (p.size >= PARTY.MAX) return this.sendError(sess, 'full', 'that party is full', m.r);
        if (p.state !== 'idle' || p.members.some(x => x.sess && (x.sess.match || (x.sess.queued && x.sess.queued.party !== p)))) return this.sendError(sess, 'busy', p.state === 'match' ? 'they are playing a match' : 'they are finding a match', m.r);
        if (sess.match) return this.sendError(sess, 'busy', 'already in a match', m.r);
        if (party) this._partyRemove(party, pid, 'left');
        this._unqueue(sess, 'left');
        p.add(sess); sess.party = p; p.kicked.delete(pid);
        if (sess.sb) p.invites = p.invites.filter(i => i.to !== sess.sb);
        p.unready(); this.log.info('party joined', { party: p.id, player: pid, size: p.size });
        return this._partySend(p, { r: m.r, to: sess });
      }
      case 'partyLeave': {
        if (!party) return this.sendJson(sess, { t: 'partyLeft', reason: 'left', r: m.r });
        this._partyRemove(party, pid, 'left', m.r); return;
      }
      case 'partyKick': {
        if (!need()) return;
        if (party.leader !== pid) return this.sendError(sess, 'not_leader', 'only the leader can remove someone', m.r);
        const who = typeof m.id === 'string' && m.id !== pid ? party.member(m.id) : null;
        if (!who) return this.sendError(sess, 'not_found', 'not in the party', m.r);
        party.kicked.add(who.id); this._partyRemove(party, who.id, 'removed');
        return this.sendJson(sess, { t: 'ack', a: 'partyKick', ok: true, r: m.r });
      }
      case 'partyReady': {
        if (!need()) return;
        const on = m.ready === true && !me.busy && !me.away;
        if (me.ready === on) return this.sendJson(sess, Object.assign(party.view(this.partyModes()), { r: m.r }));
        me.ready = on;
        if (!on && party.state !== 'idle' && party.state !== 'match') return this._partyIdle(party, 'unready', sess, m.r);
        this._partySend(party, { r: m.r, to: sess }); this._partyCheck(party); return;
      }
      case 'partyVote': {
        if (!need()) return;
        if (!PARTY.MODES.includes(m.mode)) return this.sendError(sess, 'bad_mode', 'unknown mode', m.r);
        if (party.state === 'match') return this.sendError(sess, 'busy', 'playing', m.r);
        const was = party.mode(this.partyModes()); me.vote = m.mode; me.ready = false;
        // (a different mode: everyone says ready again. Not when it's the leader's pick: the others readied up to wait for it)
        if (party.mode(this.partyModes()) !== was && party.leader !== pid) party.unready();
        if (party.state !== 'idle') return this._partyIdle(party, 'vote', sess, m.r);
        return this._partySend(party, { r: m.r, to: sess });
      }
      case 'partyLook': {
        if (!need()) return;
        const look = sanitizeLook(m.look); if (!look) return this.sendError(sess, 'bad_look', 'look too big or not an object', m.r);
        me.look = look; sess.player.look = look; me.ready = false;
        this.store.update(pid, { look }).catch(e => this.log.error('store look failed', { err: e.message }));
        if (party.state === 'starting' || party.state === 'queued') return this._partyIdle(party, 'look', sess, m.r);
        return this._partySend(party, { r: m.r, to: sess });
      }
      case 'partyBusy': {
        if (!need()) return;
        const what = m.what === null || m.what === undefined || m.what === '' ? null : PARTY.BUSY.includes(m.what) ? m.what : undefined;
        if (what === undefined) return this.sendError(sess, 'bad_busy', 'unknown', m.r);
        if (me.busy === what) return this.sendJson(sess, Object.assign(party.view(this.partyModes()), { r: m.r }));
        me.busy = what; if (what) me.ready = false;
        if (what && (party.state === 'starting' || party.state === 'queued')) return this._partyIdle(party, 'busy', sess, m.r);
        return this._partySend(party, { r: m.r, to: sess });
      }
      case 'partyReact': {
        if (!need()) return;
        if (!PARTY.EMOTES.includes(m.e)) return this.sendError(sess, 'bad_emote', 'unknown reaction', m.r);
        if (!sess.lim.react.take(1, now)) return; // (too quick: dropped quietly)
        for (const x of party.members) if (x !== me && x.sess && !x.away) this.sendJson(x.sess, { t: 'react', id: pid, e: m.e });
        return;
      }
      case 'partyInvite': {
        if (!need()) return;
        if (typeof m.to !== 'string' || !UUID.test(m.to)) return this.sendError(sess, 'bad_invite', 'who to?', m.r);
        if (party.size >= PARTY.MAX) return this.sendError(sess, 'full', 'the party is full', m.r);
        if (party.members.some(x => x.sess && x.sess.sb === m.to)) return this.sendError(sess, 'already', 'already in the party', m.r);
        if (!sess.lim.poke.take(1, now)) return this.sendError(sess, 'rate', 'that is a lot of invites; wait a little', m.r);
        const live = party.liveInvites(now).filter(i => i.to !== m.to);
        if (live.length >= PARTY.MAX_INVITES) return this.sendError(sess, 'rate', 'too many invites waiting', m.r);
        const nm = sanitizeName(m.name);
        live.push({ to: m.to, name: nm.reason === 'missing' || nm.reason === 'empty' ? 'Friend' : nm.name, look: sanitizeLook(m.look), by: pid, exp: now + PARTY.INVITE_S * 1000 });
        party.invites = live; // (someone the leader removed can come back only with an invite like this)
        this._poke(m.to, 'invite', sess);
        // (v391) a friend whose game isn't connected: a notification on their phone, when the invite came with what it needs
        if (!this.bySb.has(m.to) && typeof m.inv === 'string' && typeof m.sbt === 'string') this.push.invite(m.inv, m.sbt);
        return this._partySend(party, { r: m.r, to: sess });
      }
      case 'partyDecline': {
        const code = typeof m.code === 'string' ? m.code.toUpperCase().trim() : '', p = this.parties.get(code);
        if (!p || !sess.sb) return this.sendJson(sess, { t: 'ack', a: 'partyDecline', ok: true, r: m.r });
        const n = p.invites.length; p.invites = p.invites.filter(i => i.to !== sess.sb);
        if (p.invites.length !== n) { this._partySend(p); for (const x of p.members) if (x.sess && !x.away) this.sendJson(x.sess, { t: 'partyNote', k: 'declined', name: sess.player.name, to: sess.sb }); }
        return this.sendJson(sess, { t: 'ack', a: 'partyDecline', ok: true, r: m.r });
      }
      case 'poke': {
        if (typeof m.to !== 'string' || !UUID.test(m.to) || !POKES.has(m.k)) return this._bad(sess, 'bad poke');
        if (!sess.lim.poke.take(1, now)) return;
        this._poke(m.to, m.k, sess); return;
      }
    }
  }
  // a nudge to another player's game: "look at your inbox". It carries nothing else, so who a connection says it is
  // (its Supabase id, from hello) only decides who gets nudged; what shows comes from the database, which checks
  _poke(to, k, from) { const set = this.bySb.get(to); if (set) for (const s of set) if (s !== from && s.player) this.sendJson(s, { t: 'poke', k }); }
  _sbOn(sess, id) { this._sbOff(sess); sess.sb = id; let set = this.bySb.get(id); if (!set) this.bySb.set(id, set = new Set()); set.add(sess); }
  _sbOff(sess) { const set = sess.sb && this.bySb.get(sess.sb); if (set) { set.delete(sess); if (!set.size) this.bySb.delete(sess.sb); } }
  // the party as it is now, to everyone in it (extra: { r, to } answers a request of that member)
  _partySend(party, extra = {}) {
    const v = party.view(this.partyModes());
    for (const x of party.members) if (x.sess && !x.away) this.sendJson(x.sess, x.sess === extra.to && extra.r !== undefined ? Object.assign({}, v, { r: extra.r }) : v);
  }
  // back to the lobby from "starting" or the queue (someone un-readied, changed something, or dropped)
  _partyIdle(party, why, by, r) {
    const was = party.state;
    if (party.ticket) this.mm.drop(party.ticket);
    if (was === 'starting' || was === 'queued') { party.state = 'idle'; party.startAt = 0; party.queuedAt = 0; }
    if (was === 'queued') for (const x of party.members) if (x.sess && !x.away) this.sendJson(x.sess, { t: 'queueLeft', party: true, why });
    this._partySend(party, { r, to: by });
  }
  // everyone ready: a moment to back out, then the match (just the party) or the search (matchmaking fills the rest)
  _partyCheck(party) {
    if (party.state !== 'idle' || !party.allReady()) return;
    const mode = party.mode(this.partyModes()); if (!mode || !planFor(mode, party.size)) return;
    party.state = 'starting'; party.startAt = nowMs() + PARTY.START_MS;
    this._partySend(party);
  }
  _partyGo(party, now) {
    if (party.state !== 'starting' || now < party.startAt) return;
    const mode = party.mode(this.partyModes()), plan = mode && planFor(mode, party.size), sessions = party.members.map(x => x.sess);
    if (!plan || !party.allReady() || sessions.some(s => !s || s.closed || s.match || s.room)) { party.state = 'idle'; party.unready(); return this._partySend(party); }
    if (plan === 'private') {
      // just the party: who plays on which side (in a 2v2 of four, the best and the worst together)
      const order = mode === 'duo' ? party.members.slice().sort((a, b) => b.sess.player.ratings.duo.r - a.sess.player.ratings.duo.r) : party.members;
      const sides = MODE_INFO[mode].sides;
      this.log.info('party match', { party: party.id, mode });
      this._launch(mode, order.map((x, i) => ({ sess: x.sess, team: sides[i] })), { rated: false, parties: [party] });
      return;
    }
    for (const s of sessions) this.mm.remove(s);
    this.mm.addTicket(makeTicket(sessions, mode, now, party));
    party.state = 'queued'; party.queuedAt = now;
    for (const s of sessions) this.sendJson(s, { t: 'queued', mode, party: true });
    this._partySend(party);
  }
  // A member leaves, is removed or was gone too long. The lead passes on; an empty party closes.
  _partyRemove(party, pid, why, r) {
    const m = party.member(pid); if (!m) return;
    if (party.ticket) this.mm.drop(party.ticket);
    party.remove(pid); clearTimeout(m.awayTimer);
    if (this.partyAway.get(pid) && this.partyAway.get(pid).party === party) this.partyAway.delete(pid);
    const s = m.sess; if (s && s.party === party) s.party = null;
    if (s && !s.closed) this.sendJson(s, { t: 'partyLeft', reason: why, r });
    this.log.info('party left', { party: party.id, player: pid, why, size: party.size });
    if (!party.size) { this.parties.delete(party.code); return; }
    const was = party.state; party.unready();
    if (was === 'starting' || was === 'queued') { party.state = 'idle'; party.startAt = 0; party.queuedAt = 0; if (was === 'queued') for (const x of party.members) if (x.sess && !x.away) this.sendJson(x.sess, { t: 'queueLeft', party: true, why: 'left' }); }
    this._partySend(party);
  }
  // A member's connection dropped (the app went to the background, or the signal went): their place is kept for
  // partyGrace seconds, and they come back into the party when they reconnect.
  _partyAway(sess) {
    const party = sess.party, pid = sess.player && sess.player.id; if (!party || !pid) return;
    const m = party.member(pid); if (!m || m.sess !== sess) return;
    m.away = true; m.ready = false; this.partyAway.set(pid, { party, sess });
    clearTimeout(m.awayTimer); m.awayTimer = setTimeout(() => { if (m.away && party.member(pid) === m) this._partyRemove(party, pid, 'gone'); }, (this.rules.partyGrace ?? 60) * 1000);
    if (m.awayTimer.unref) m.awayTimer.unref(); // (a stopped server isn't held open by it)
    if (party.state === 'starting' || party.state === 'queued') return this._partyIdle(party, 'away');
    this._partySend(party);
  }
  _partyBack(sess) {
    const pid = sess.player.id, rec = this.partyAway.get(pid); if (!rec) return;
    this.partyAway.delete(pid);
    const { party } = rec, m = party.member(pid);
    if (!m || this.parties.get(party.code) !== party) return;
    clearTimeout(m.awayTimer); if (rec.sess && rec.sess !== sess && rec.sess.party === party) rec.sess.party = null;
    m.sess = sess; m.away = false; m.name = sess.player.name; m.sb = sess.sb || m.sb; m.trio = playsTrio(sess); if (sess.player.look) m.look = sess.player.look; sess.party = party;
    this._partySend(party);
  }

  // ------------------------------------------------------------------------------------------------ starting a match
  // The one hand-off from parties and the matchmaker to a match: the mode and its players, each with a team (in 2v2
  // a party of two is one team). Slots follow the mode's sides (MODE_INFO: 2v2 is slots 0 and 3 against 1 and 2).
  _launch(mode, players, opts = {}) {
    const sides = MODE_INFO[mode].sides, left = players.slice(), slots = [];
    for (let i = 0; i < players.length; i++) { const k = left.findIndex(p => p.team === sides[i]); slots.push((k >= 0 ? left.splice(k, 1) : left.splice(0, 1))[0].sess); }
    return this._startMatch(mode, slots, opts);
  }
  _leaveRoom(sess, silent, pid = sess.player && sess.player.id) {
    const room = sess.room; if (!room) return;
    room.members = room.members.filter(s => s !== sess); room.ready.delete(pid); sess.room = null;
    if (this.roomAway.get(pid) === sess) { this.roomAway.delete(pid); clearTimeout(sess.awayTimer); }
    if (!room.members.length) { this._dropRoom(room); return; }
    if (room.host === pid) room.host = room.members[0].roomPid;
    for (const s of room.members) this.sendJson(s, room.view());
  }
  // a room code no machine is using: claimed in the shared store, so it is unique across every machine
  async _claimCode() {
    for (let i = 0; i < 8; i++) { const code = uniqueCode(this.rooms); if (await this.store.claimRoom(code, this.shardId)) return code; }
    throw new Error('no free room code');
  }
  _dropRoom(room) { this.rooms.delete(room.code); this.store.releaseRoom(room.code, this.shardId).catch(() => {}); }
  // A member's connection dropped (say a phone that went to another app to send the room code): their place is kept for
  // roomGrace seconds, so the code still works and they come back into the room when they reconnect.
  _roomAway(sess) {
    const room = sess.room, pid = sess.player && sess.player.id; if (!room || !pid) return;
    if (room.match) return this._leaveRoom(sess, true, pid); // (a room that's playing: the match keeps their place)
    room.ready.set(pid, false); sess.roomAwayAt = nowMs(); this.roomAway.set(pid, sess);
    clearTimeout(sess.awayTimer); sess.awayTimer = setTimeout(() => { if (sess.room === room) this._leaveRoom(sess, true, pid); }, (this.rules.roomGrace ?? 60) * 1000);
    for (const s of room.members) this.sendJson(s, room.view());
  }
  _roomBack(sess) {
    const pid = sess.player.id, old = this.roomAway.get(pid); if (!old) return;
    this.roomAway.delete(pid); clearTimeout(old.awayTimer);
    const room = old.room, i = room ? room.members.indexOf(old) : -1;
    if (i < 0 || this.rooms.get(room.code) !== room || room.match) return;
    room.members[i] = roomMember(sess); sess.room = room; old.room = null; room.ready.set(pid, false); this.mm.remove(sess);
    for (const s of room.members) this.sendJson(s, room.view());
  }

  // ------------------------------------------------------------------------------------------------ matches
  // sessions in slot order. parties: the parties playing in it (back to their lobby after); tickets: the queue tickets
  // it was made from (a match called off before it began puts them back in line)
  _startMatch(mode, sessions, { room = null, rated = true, seed, parties = [], tickets = null } = {}) {
    for (const s of sessions) this.mm.remove(s);
    const match = this.pool ? this.pool.create(this, { mode, sessions, rated, room, seed }) : new Match(this, { mode, sessions, rated, room, seed });
    match.parties = parties; match.tickets = tickets;
    this.matches.add(match); this.stats.matchesStarted++;
    if (room) room.match = match;
    for (const s of sessions) { s.match = match; s.slot = sessions.indexOf(s); this.inMatch.set(s.player.id, match); }
    match.start();
    for (const p of parties) { p.state = 'match'; p.match = match; p.ticket = null; p.startAt = 0; p.queuedAt = 0; this._partySend(p); }
    return match;
  }
  // a party's match is over: back to its lobby, everyone to ready up again
  _partyHome(party, match) {
    if (party.match !== match) return;
    party.match = null; if (party.state === 'match') { party.state = 'idle'; party.unready(); }
    for (const x of party.members) if (x.away && x.sess && !x.sess.closed && this.online.get(x.id) === x.sess) x.away = false;
    if (this.parties.get(party.code) === party) this._partySend(party);
  }
  _detach(sess, match) { if (sess.match === match) { sess.match = null; sess.slot = -1; } if (sess.player && this.inMatch.get(sess.player.id) === match) this.inMatch.delete(sess.player.id); }
  // a match ended for good (cancelled, closed after the rematch vote, or replaced by its rematch)
  onMatchClosed(match, { cancelled, reason, culprits = [] }) {
    this.matches.delete(match);
    if (cancelled) this.stats.matchesCancelled++;
    for (const p of match.P) {
      const sess = p.sess;
      if (this.inMatch.get(p.id) === match) this.inMatch.delete(p.id);
      if (!sess || sess.closed || sess.match !== match) continue;
      sess.match = null; sess.slot = -1;
    }
    // back to matchmaking after a cancelled queue match (not the ones who caused it), keeping their place in line; a
    // party goes back together, or not at all
    if (cancelled && !match.room && match.tickets && !this.closing) {
      for (const t of match.tickets) {
        const ps = t.pids.map(id => match.playerById(id)), ses = t.pids.map(id => this.online.get(id));
        if (!ps.every(p => p && p.st !== 'left' && !culprits.includes(p.id)) || !ses.every(s => s && !s.closed && !s.match && !s.room)) continue;
        if (t.party && (this.parties.get(t.party.code) !== t.party || t.party.size !== ses.length)) continue;
        this.mm.addTicket(makeTicket(ses, match.mode, t.at, t.party));
        if (t.party) { t.party.state = 'queued'; t.party.queuedAt = t.at; t.party.match = null; }
        for (const s of ses) this.sendJson(s, { t: 'queued', mode: match.mode, requeued: true, party: t.party ? true : undefined });
        if (t.party) this._partySend(t.party);
      }
    }
    for (const party of match.parties || []) this._partyHome(party, match);
    if (match.room) {
      const room = match.room; room.match = null; room.ready = new Map(room.members.map(s => [s.roomPid, false]));
      room.members = room.members.filter(s => !s.closed);
      if (!room.members.length) this._dropRoom(room); else for (const s of room.members) this.sendJson(s, room.view());
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
    if (sessions.some(s => !s || s.closed)) { for (const s of sessions) if (s && !s.closed) { s.match = null; this.sendJson(s, { t: 'matchClosed', matchId: old.id, reason: 'rematch_failed' }); } for (const p of old.parties || []) this._partyHome(p, old); return; }
    for (const s of sessions) { s.match = null; }
    this._startMatch(old.mode, sessions, { room: old.room, rated: old.rated, parties: old.parties || [], tickets: old.tickets });
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
        const sides = MODE_INFO[g.mode].sides, parties = [...new Set(g.tickets.map(t => t.party).filter(Boolean))];
        // (a party that waited long enough for a Showdown of three plays just itself: unrated, like a party's private match)
        this._launch(g.mode, g.sessions.map((s, i) => ({ sess: s, team: sides[i] })), { rated: !(g.tickets.length === 1 && g.tickets[0].party), parties, tickets: g.tickets });
      }
      for (const p of this.parties.values()) if (p.state === 'starting') this._partyGo(p, now);
    }
    for (const m of [...this.matches]) {
      try { m.tick(now); } catch (e) {
        // one broken match must not stop the others: call it off
        this.stats.errors = (this.stats.errors || 0) + 1;
        this.log.error('match tick failed', { match: m.id, err: e.stack || e.message });
        try { if (m.phase === 'ended') m.close('server_error'); else m.cancel('server_error'); } catch (e2) { this.matches.delete(m); }
      }
    }
    // the server's own pings (they measure each connection's round trip): every 2 s in a match, a queue or a party
    // that is starting; every idlePing seconds for a connection that is only waiting in the lobby, so a phone's radio
    // can rest
    if (now - this._lastPing >= 2000) {
      this._lastPing = now; const b = new Uint8Array(codec.encodeSPing(now)), idle = (this.rules.idlePing ?? 20) * 1000;
      for (const s of this.sessions) {
        if (!s.player || (!this._busy(s) && now - s.lastPing < idle)) continue;
        s.lastPing = now; this.sendBinary(s, b, true);
      }
    }
    // a connection that has said nothing for a while is gone, closed so a match shows the player as away and holds their
    // place: silentMs for one that is busy (pinged every 2 s, and the game pings twice a second), counted from when it got
    // busy at the earliest (the game, on its lobby heartbeat until then, hears a moment later); silentKick seconds for one
    // only waiting in the lobby (a heartbeat every 20 s)
    if (now - this._lastSilent >= 1000) {
      this._lastSilent = now;
      const quick = this.opts.silentMs ?? LIMITS.silentMs, slow = (this.rules.silentKick ?? 75) * 1000;
      for (const s of [...this.sessions]) {
        const busy = this._busy(s); if (!busy) s.busyAt = 0; else if (!s.busyAt) s.busyAt = now;
        const quiet = busy ? quick : slow;
        if (quiet > 0 && now - Math.max(s.lastMsg, s.busyAt) > quiet) { this.stats.silent = (this.stats.silent || 0) + 1; this.log.info('silent connection closed', { conn: s.id, player: s.player && s.player.id }); try { s.ws && s.ws.terminate(); } catch (e) { /* gone */ } this._closed(s); }
      }
    }
  }

  // ------------------------------------------------------------------------------------------------ shutdown
  async close() {
    if (this.closing) return; this.closing = true;
    clearTimeout(this._timer);
    this.log.info('shutting down', { connections: this.sessions.size, matches: this.matches.size });
    for (const p of this.parties.values()) for (const x of p.members) clearTimeout(x.awayTimer);
    for (const m of [...this.matches]) { if (m.phase === 'play' || m.phase === 'countdown' || m.phase === 'consensus') m.cancel('server_shutdown'); else m.close('server_shutdown'); }
    if (this.pool) await this.pool.drain(Math.min(1000, this.opts.shutdownGraceMs ?? 3000)); // (the workers' last words to the players)
    for (const s of [...this.sessions]) { this.sendJson(s, { t: 'server', msg: 'shutdown' }); this._close(s, CLOSE.AWAY, 'server shutdown'); }
    const grace = this.opts.shutdownGraceMs ?? 3000;
    await new Promise(resolve => { const t = setTimeout(resolve, grace); const iv = setInterval(() => { if (!this.sessions.size) { clearTimeout(t); clearInterval(iv); resolve(); } }, 20); setTimeout(() => clearInterval(iv), grace + 10); });
    for (const s of [...this.sessions]) { try { s.ws && s.ws.terminate(); } catch (e) { /* gone */ } this._closed(s); }
    await new Promise(resolve => this.http.close(() => resolve()));
    if (this.storeApi) await new Promise(resolve => this.storeApi.close(() => resolve()));
    if (this.pool) await this.pool.stop();
    await this.store.close(); this.push.close();
    this.log.info('stopped');
  }
}

export async function createGameServer(opts = {}) { const s = new GameServer(opts); await s.listen(opts.port ?? 0, opts.host || '127.0.0.1'); return s; }
