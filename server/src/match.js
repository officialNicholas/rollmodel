// One match, from "match found" to the rematch vote. The server is the referee: it checks every movement report,
// rules on every action, keeps the paint meters, paints its own coverage grid, decides knock-outs (with lag
// compensation), and sends everyone snapshots.
import { G, KO_R, MODE_INFO, DEFAULT_RULES } from './constants.js';
import { Level } from './geometry.js';
import { Coverage } from './coverage.js';
import { Mover, MOVE } from './movement.js';
import { validateLayout } from './layout.js';
import { codec, FLAGS, RemoteTrack } from '../client/rmnet.js';
import { LeakyMin, clamp, fin, nowMs, randomId, seed32 } from './util.js';
import { weatherSchedule, rainMulAt, zoneSchedule, zoneSizeAt } from './schedule.js';
import { rateMatch } from './rating.js';
import { Items } from './items.js';

const ACTIONS = new Set(['jump', 'roll', 'fling', 'pound', 'land', 'stomp', 'enterPot', 'exitPot', 'use', 'selfKo']);
const SELF_KO = new Set(['dry', 'fall', 'zone', 'sun']);
const CLIENT_FLAGS = FLAGS.AIR | FLAGS.CHARGE | FLAGS.SLAM | FLAGS.FLUNG | FLAGS.MISSILE;
const SELF_RESPAWN_T = 2, SD_END_T = 1.7, ZONE_KO = 1.1, VHIST = 96, POT_EMPTY_T = 0.8;
const nextCid = c => (c % 255) + 1;
const r2 = v => Math.round(v * 100) / 100;
const dist2 = (a, b) => Math.hypot(a.x - b.x, a.z - b.z);

// a player's own validated states, by the client's time
function sampleHist(h, t) {
  const n = h.length; if (!n) return null;
  if (t <= h[0].tc) return h[0];
  if (t >= h[n - 1].tc) return h[n - 1];
  let lo = 0, hi = n - 1;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (h[m].tc <= t) lo = m; else hi = m; }
  const a = h[lo], b = h[hi], k = (t - a.tc) / (b.tc - a.tc);
  return { tc: t, x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k, z: a.z + (b.z - a.z) * k, grounded: k < 0.5 ? a.grounded : b.grounded };
}

export class Match {
  // sessions: lobby sessions in slot order. sides (optional) are fixed by the mode.
  constructor(srv, { mode, sessions, rated = false, room = null, rules = {}, seed } = {}) {
    this.srv = srv; this.id = randomId('m_', 10); this.mode = mode; this.info = MODE_INFO[mode];
    this.rules = Object.assign({}, DEFAULT_RULES, srv.rules || {}, rules);
    this.log = srv.log.child({ match: this.id, mode });
    this.rated = rated; this.room = room; this.seed = seed === undefined ? seed32() : seed >>> 0;
    this.showdown = this.info.showdown;
    this.opts = { mode, arena: this.info.arena, players: this.info.players };
    this.phase = 'consensus'; this.createdAt = nowMs(); this.layoutDeadline = this.createdAt + this.rules.layoutTimeout * 1000;
    this.P = sessions.map((s, slot) => this._mkPlayer(s, slot));
    this.level = null; this.cov = null; this.pots = []; this.hits = [];
    this.snapSeq = 0; this.nextCovAt = 0; this.startAt = 0; this.endAt = 0; this.endingAt = 0; this.lastTick = nowMs();
    this.weather = []; this.zone = []; this.items = null; this.results = null; this.rematchUntil = 0; this.layoutHash = null; this.otUsed = false;
    this.stats = { states: 0, rejected: 0, corrections: 0, snapshots: 0, bytes: 0 };
  }
  _mkPlayer(sess, slot) {
    const pl = sess.player, now = nowMs();
    return {
      slot, sess, id: pl.id, name: pl.name, look: pl.look, side: this.info.sides[slot], color: slot,
      rating: Object.assign({}, pl.ratings[this.mode]),
      connected: !!sess.ws, awaySince: 0, afk: false, st: 'wait',
      layout: null, layoutHash: null, parsed: null,
      mover: null, vhist: [], track: new RemoteTrack(96), latest: null, lastTau: 0, spawn: null,
      lag: new LeakyMin(20), lagEst: 60, jit: 5, cid: 1, ackSeq: 0, lastStateAt: now, lastMoveAt: now,
      paint: 1, slamCd: 0, rollReadyAt: -1e12, rollStart: -1e12, dashStart: -1e12, immuneUntil: 0, spawnImm: false,
      flatUntil: 0, flatAnchor: null, koAt: 0, koPos: null, respawnAt: 0, outAt: 0, zoneT: 0,
      pot: -1, hiddenAt: -1e12, potExitAt: -1e12, emptyT: 0,
      pound: null, flingC: 0, flingAt: -1e12, flingOpen: false, inkRushUntil: 0, lastHit: null, viewDelay: 120,
      kos: 0, deaths: 0, flats: 0, stomps: 0, slams: 0, hearts: this.showdown ? this.rules.hearts : 0, place: 0, elimAt: 0,
      strikes: 0, strikeAt: 0, violations: {}, item: null, effects: {}, rematch: null,
    };
  }

  // ------------------------------------------------------------------------------------------------ messaging
  _send(p, msg) { if (p.connected && p.sess && p.sess.ws) this.srv.sendJson(p.sess, msg); }
  _all(msg, except) { for (const p of this.P) if (p !== except) this._send(p, msg); }
  _ack(p, n, a, ok, reason, data) { if (Number.isInteger(n)) this._send(p, { t: 'ack', n, a, ok, reason: ok ? undefined : reason, data }); }
  roster() { return this.P.map(p => ({ slot: p.slot, id: p.id, name: p.name, look: p.look, side: p.side, color: p.color, rating: Math.round(p.rating.r) })); }
  publicRules() {
    const r = this.rules;
    return { matchT: r.matchT, sdT: r.sdT, hearts: r.hearts, respawnT: r.respawnT, flatT: r.flatT, slamFirst: r.slamFirst, slamCd: r.slamCd, potShields: r.potShields, items: r.items, weather: r.weather, zone: r.zone, lagCompMaxMs: r.lagCompMaxMs, snapshotHz: r.snapshotHz, koPct: r.koPct, overtime: r.overtime, potDownT: r.potDownT };
  }
  playerById(id) { return this.P.find(p => p.id === id) || null; }
  get active() { return this.phase !== 'closed'; }

  // ------------------------------------------------------------------------------------------------ lifecycle
  start() {
    for (const p of this.P) this._send(p, { t: 'matchFound', matchId: this.id, mode: this.mode, seed: this.seed, opts: this.opts, players: this.roster(), you: p.slot, rated: this.rated, room: this.room ? this.room.code : null, layoutDeadline: this.layoutDeadline });
    this.log.info('match found', { players: this.P.map(p => p.id), seed: this.seed, rated: this.rated });
  }
  onLayout(p, m) {
    if (this.phase !== 'consensus' || p.layout || p.st === 'left') return;
    const v = validateLayout(m.layout, { arena: this.info.arena, players: this.P.length });
    if (!v.ok) { this.log.warn('layout invalid', { player: p.id, error: v.error }); p.layout = '!invalid'; p.layoutHash = '!invalid:' + p.slot; }
    else if (m.hash !== v.hash) { this.log.warn('layout hash differs from its content', { player: p.id, computed: v.hash }); p.layout = v.canonical; p.layoutHash = '!hash:' + p.slot; }
    else { p.layout = v.canonical; p.layoutHash = v.hash; p.parsed = v.layout; }
    if (this.P.every(q => q.layout || q.st === 'left')) this._consensus();
  }
  _consensus() {
    const live = this.P.filter(q => q.st !== 'left');
    if (live.length < 2) return this.cancel('player_left');
    const ref = live[0], agree = live.every(q => q.layout === ref.layout && q.layoutHash === ref.layoutHash) && !ref.layoutHash.startsWith('!');
    if (!agree) {
      // with three or more players a majority shows who is out of step; flag them
      const counts = new Map(); for (const q of live) counts.set(q.layoutHash, (counts.get(q.layoutHash) || 0) + 1);
      let maj = null, mc = 0; for (const [h, c] of counts) if (c > mc) { mc = c; maj = h; }
      const odd = mc > live.length / 2 && !maj.startsWith('!') ? live.filter(q => q.layoutHash !== maj) : live.filter(q => q.layoutHash.startsWith('!'));
      for (const q of odd) this.srv.flag(q.id, 'layout_mismatch', { match: this.id, hash: q.layoutHash });
      this.log.warn('layout mismatch', { hashes: live.map(q => q.layoutHash), odd: odd.map(q => q.id) });
      return this.cancel('layout_mismatch', odd.map(q => q.id));
    }
    this._setup(ref.parsed, ref.layoutHash);
  }
  _setup(layout, hash) {
    this.layoutHash = hash; this.level = new Level(layout); this.cov = new Coverage(this.level, this.info.sides);
    this.pots = this.level.pots.map((q, i) => ({ i, x: q.x, y: q.y, z: q.z, occ: -1, ink: this.rules.potInk, up: true, upAt: 0 }));
    const now = nowMs(), dur = this.showdown ? this.rules.sdT : this.rules.matchT;
    this.startAt = Math.round(now + (this.rules.startLead + this.rules.countdown) * 1000); this.endAt = this.startAt + dur * 1000;
    this.weather = this.rules.weather ? weatherSchedule(this.seed, dur) : [];
    this.zone = this.showdown && this.rules.zone ? zoneSchedule() : [];
    if (this.rules.items && this.level.powers.length) this.items = new Items(this);
    this.phase = 'countdown';
    for (const p of this.P) {
      const sp = this.level.spawns[p.slot];
      p.spawn = { x: sp.x, y: sp.y, z: sp.z, yaw: sp.yaw };
      p.mover = new Mover(this.level); p.mover.reset(p.spawn, now);
      p.latest = { tau: Math.round(now), tc: now, x: sp.x, y: sp.y, z: sp.z, yaw: sp.yaw, spd: 0, vy: 0, flags: 0, aim: 0 };
      p.vhist = [{ tc: now, tau: p.latest.tau, x: sp.x, y: sp.y, z: sp.z, grounded: true }];
      p.lastTau = p.latest.tau; if (p.st !== 'left') p.st = 'play'; p.slamCd = this.rules.slamFirst; p.lastStateAt = now; p.lastMoveAt = this.startAt;
    }
    const spawns = this.P.map(p => ({ slot: p.slot, x: p.spawn.x, y: p.spawn.y, z: p.spawn.z, yaw: p.spawn.yaw }));
    for (const p of this.P) this._send(p, { t: 'start', matchId: this.id, startAt: this.startAt, endAt: this.endAt, countdown: this.rules.countdown, layoutHash: hash, spawns, cid: p.cid, weather: this.weather, zone: this.zone, rules: this.publicRules(), pots: this.pots.length });
    this.log.info('match starting', { startAt: this.startAt, hash });
  }
  // the match never started: tell everyone and let the server put them back in the queue (or the room)
  cancel(reason, culprits = []) {
    if (this.phase === 'closed') return;
    this.phase = 'closed';
    for (const p of this.P) this._send(p, { t: 'matchCancelled', matchId: this.id, reason });
    this.log.info('match cancelled', { reason });
    this.srv.onMatchClosed(this, { cancelled: true, reason, culprits });
  }
  close(reason) {
    if (this.phase === 'closed') return;
    this.phase = 'closed';
    for (const p of this.P) this._send(p, { t: 'matchClosed', matchId: this.id, reason });
    this.srv.onMatchClosed(this, { cancelled: false, reason });
  }

  // ------------------------------------------------------------------------------------------------ connections
  onDisconnect(p) {
    if (p.st === 'left') return;
    p.connected = false; p.sess = null; p.awaySince = nowMs();
    this._all({ t: 'playerAway', slot: p.slot });
    if (this.phase === 'ended') { p.rematch = false; this._rematchCheck(); }
  }
  // the same player came back with their token: pick up where they were
  onReconnect(p, sess) {
    const now = nowMs();
    p.sess = sess; p.connected = true; p.awaySince = 0; p.afk = false; p.lastStateAt = now;
    p.cid = nextCid(p.cid);
    if (p.mover) { p.mover.last.t = now; p.mover.bucket = 0; }
    const L = p.mover ? p.mover.last : p.spawn || { x: 0, y: 0, z: 0, yaw: 0 };
    this._send(p, {
      t: 'resume', matchId: this.id, mode: this.mode, seed: this.seed, opts: this.opts, players: this.roster(), you: p.slot, rated: this.rated,
      phase: this.phase, startAt: this.startAt, endAt: this.endAt, layoutHash: this.layoutHash, weather: this.weather, zone: this.zone, rules: this.publicRules(),
      cid: p.cid, self: { x: L.x, y: L.y, z: L.z, yaw: L.yaw, st: p.st, paint: p.paint, hearts: p.hearts, pot: p.pot, respawnAt: p.respawnAt === Infinity ? null : p.respawnAt },
      others: this.P.filter(q => q !== p).map(q => ({ slot: q.slot, st: q.st, hearts: q.hearts, kos: q.kos, pot: q.pot })),
      pots: this.pots.map(q => ({ i: q.i, occ: q.occ, up: q.up, ink: r2(q.ink) })), cov: this.cov ? this.cov.bySide().map(r2) : [],
      items: this.items ? this.items.list() : [], results: this.results || undefined, needLayout: this.phase === 'consensus' && !p.layout,
    });
    this._all({ t: 'playerBack', slot: p.slot }, p);
  }
  // leaving for good (quit, kicked, gone too long, AFK)
  forfeit(p, why) {
    if (p.st === 'left') return;
    const now = nowMs();
    this.log.info('player left', { player: p.id, why, phase: this.phase });
    if (this.phase === 'consensus' || this.phase === 'countdown') { p.st = 'left'; return this.cancel('player_left'); }
    if (this.phase === 'ended' || this.phase === 'closed') { p.rematch = false; p.st = 'left'; this._rematchCheck(); return; }
    this._freePot(p);
    // (out of a Showdown already, watching: their place stands, from when they went out)
    p.outLeft = p.st === 'out'; if (!p.outLeft) p.elimAt = now;
    p.st = 'left'; p.pound = null; p.hearts = 0;
    if (this.items) this.items.onKo(p);
    this._all({ t: 'playerLeft', slot: p.slot, reason: why });
    const sidesLeft = new Set(this.P.filter(q => q.st !== 'left').map(q => q.side));
    if (sidesLeft.size <= 1) return this._end('forfeit');
    if (this.showdown) this._checkShowdown(now);
  }

  // ------------------------------------------------------------------------------------------------ states
  onState(p, buf, recv) {
    const s = codec.decodeState(buf);
    if (!s) return 'malformed';
    if (this.phase !== 'countdown' && this.phase !== 'play') return null;
    this.stats.states++;
    p.ackSeq = s.seq; p.lastStateAt = recv; if (p.afk) { p.afk = false; this._all({ t: 'afk', slot: p.slot, on: false }); }
    if (p.st !== 'play' && p.st !== 'hide') return null;
    if (s.corrAck !== (p.cid & 0xff)) return null; // sent before the client applied our last correction
    if (s.t > recv + 50) s.t = recv + 50; // a client clock cannot be ahead of ours
    if (s.t < recv - 1000) return null; // far too old
    const lag = p.lag.add(recv - s.t, recv); p.lagEst = lag; p.jit += (Math.abs(recv - s.t - lag) - p.jit) * 0.05;
    if (s.t <= p.mover.last.t) return null;
    const tau = Math.round(clamp(s.t + lag, p.lastTau + 1, recv));
    if (p.st === 'hide') {
      const pot = this.pots[p.pot];
      if (!pot || Math.hypot(s.x - pot.x, s.z - pot.z) > 0.9 || Math.abs(s.y - pot.y) > 1.0) { this._violation(p, 'pot', true); return null; }
      p.mover.last = { x: pot.x, y: pot.y, z: pot.z, yaw: s.yaw, t: s.t };
      this._accept(p, s, tau, { grounded: true }, { x: pot.x, y: pot.y, z: pot.z });
      return null;
    }
    const r = p.mover.check(s, s.t, this._env(p, s));
    if (!r.ok) { if (!r.silent) { this.stats.rejected++; this._violation(p, r.reason, r.hard, r.detail); } return null; }
    this._accept(p, s, tau, r, { x: s.x, y: r.y, z: s.z });
    if (r.fell) this._ko(p, null, 'fall');
    return null;
  }
  _env(p, s) {
    const tS = (s.t - this.startAt) / 1000, fx = Math.sin(s.yaw), fz = Math.cos(s.yaw), e = p.effects;
    const env = {
      rainMul: rainMulAt(this.weather, tS),
      // the game speeds you up when the floor just ahead is your colour; look a little further too, to forgive small
      // differences between the client's paint and ours
      turfOwn: (x, y, z) => this.cov.sideAt(x + fx * 0.55, y, z + fz * 0.55) === p.side || this.cov.sideAt(x + fx, y, z + fz) === p.side,
      giant: (e.giant || 0) > s.t - 300,
      // (a hook for the rocket pick-up, which is not handed out online yet: while it flies, the ceiling is that high)
      ceilExtra: (e.rocket || 0) > s.t - 1000 ? G.ROCKET_ALT + 2 : 0,
      still: false, anchor: null,
    };
    if (s.t < this.startAt - 30) { env.still = true; env.anchor = p.spawn; }
    else if (p.flatUntil && s.t < p.flatUntil - 60) { env.still = true; env.anchor = p.flatAnchor; }
    else if ((e.turret || 0) > s.t + 60) { env.still = true; env.anchor = e.turretAt; }
    return env;
  }
  _accept(p, s, tau, r, pos) {
    const prev = p.vhist[p.vhist.length - 1];
    const cur = { tc: s.t, tau, x: pos.x, y: pos.y, z: pos.z, grounded: !!r.grounded };
    p.vhist.push(cur); if (p.vhist.length > VHIST) p.vhist.shift();
    p.lastTau = tau;
    p.latest = { tau, tc: s.t, x: pos.x, y: pos.y, z: pos.z, yaw: s.yaw, spd: s.spd, vy: s.vy, flags: s.flags, aim: s.aim };
    if (prev && Math.hypot(cur.x - prev.x, cur.z - prev.z) > 0.03) p.lastMoveAt = nowMs();
    if (prev && p.st === 'play') this._paintStep(p, prev, cur, s);
    if (s.paint + 0.03 < p.paint) p.paint = Math.max(0, s.paint + 0.03); // an honest client never claims less than it has
    if (this.items && p.st === 'play') this.items.onMove(p, cur);
  }
  // the paint meter (an upper bound of the client's: drain a little slower, refill a little faster) and the coverage
  _paintStep(p, a, b, s) {
    const dt = Math.min(1.5, (b.tc - a.tc) / 1000); if (!(dt > 0)) return;
    const moved = Math.hypot(b.x - a.x, b.z - a.z), v = moved / dt, flat = p.flatUntil > b.tc;
    if (b.grounded && !flat) {
      const own = this.cov.sideAt(b.x + Math.sin(s.yaw) * 0.55, b.y, b.z + Math.cos(s.yaw) * 0.55) === p.side;
      if (own && v > 0.5) p.paint += G.OWN_REFILL * 1.25 * dt;
      else p.paint -= G.DRAIN * 0.85 * dt * (v < 0.8 ? G.STILL_DRAIN : 1);
    }
    if (p.inkRushUntil > b.tc) p.paint += G.INK_RUSH * dt;
    if ((p.effects.giant || 0) > b.tc || (p.effects.turret || 0) > b.tc) p.paint = 1;
    p.paint = clamp(p.paint, 0, 1);
    // touching down from a fling: the landing splat, which costs paint
    if (b.grounded && !a.grounded && p.flingOpen && !p.pound) {
      const c = p.flingC, full = G.SPLAT_COST * (1 + 0.5 * c), cost = Math.max(0, Math.min(full, p.paint - 0.03));
      if (cost > 0.005) { p.paint -= cost; this.cov.stamp(b.x, b.y, b.z, G.SPLAT_R * (0.55 + 0.45 * cost / full) * (1 + 0.6 * c), p.color); }
      p.flingOpen = false;
    }
    // the trail: only on the ground, with paint, and not flattened
    if (b.grounded && a.grounded && !flat && p.paint > 0 && moved > 0.01) {
      const dash = b.tc >= p.rollStart && b.tc - p.rollStart < G.ROLL_DASH * 1000;
      const w = ((p.effects.giant || 0) > b.tc ? 3 : (p.effects.roller || 0) > b.tc ? 2.6 : 1) * (dash ? 0.45 : 1);
      this.cov.stampPath(a.x, a.y, a.z, b.x, b.y, b.z, G.TW / 2 * w, p.color);
    }
  }
  _violation(p, reason, hard, detail) {
    const now = nowMs(), decay = this.rules.strikeDecay * 1000;
    if (p.strikes > 0 && now - p.strikeAt > decay) p.strikes = Math.max(0, p.strikes - Math.floor((now - p.strikeAt) / decay));
    p.strikes += hard ? 2 : 1; p.strikeAt = now; p.violations[reason] = (p.violations[reason] || 0) + 1;
    this.stats.corrections++; this.srv.stats.violations++;
    this.log.info('violation', { player: p.id, reason, strikes: p.strikes, detail, recent: p.recentActs });
    if (p.mover) {
      p.cid = nextCid(p.cid);
      // back to the last place that passed, and judged afresh from there: put back in the air, the blob falls from that
      // height (judged against the old launch, every report on the way down would fail again until the kick). It only
      // starts to fall once the correction reaches it, so that height holds for about a round trip first.
      const L = p.mover.last, t = Math.max(L.t, now), sup = p.mover.L.supportAt(L.x, L.z, L.y);
      p.mover.reset({ x: L.x, y: L.y, z: L.z, yaw: L.yaw }, t, { airborne: !(sup > -Infinity && L.y - sup <= MOVE.GROUND_GAP), hold: Math.min(600, 2 * p.lagEst + 4 * p.jit + 100) });
      this._send(p, { t: 'correction', cid: p.cid, x: L.x, y: L.y, z: L.z, yaw: L.yaw, reason });
    }
    if (p.strikes >= this.rules.strikesToKick) {
      this.srv.flag(p.id, 'cheating', { match: this.id, violations: p.violations });
      const sess = p.sess; this.forfeit(p, 'kicked'); if (sess) this.srv.kick(sess, 'cheating');
    }
  }

  // ------------------------------------------------------------------------------------------------ actions
  onAction(p, m, recv) {
    const a = m.a, n = Number.isInteger(m.n) && m.n >= 0 ? m.n : undefined;
    if (typeof a !== 'string' || !ACTIONS.has(a)) { this._ack(p, n, a, false, 'unknown'); return 'bad'; }
    if (this.phase !== 'play') { this._ack(p, n, a, false, 'not_playing'); return null; }
    // when it happened (server clock): no later than now, no earlier than this player's measured delay allows
    const earliest = recv - (p.lagEst + 4 * p.jit + 80);
    const ts = fin(m.ts) ? clamp(m.ts, earliest, recv + 50) : recv - p.lagEst;
    let vt = fin(m.vt) ? clamp(m.vt, ts - this.rules.lagCompMaxMs, ts) : ts - p.viewDelay;
    vt = Math.max(vt, recv - this.rules.maxRewindMs);
    let why;
    switch (a) {
      case 'jump': why = this._jump(p, ts); break;
      case 'roll': why = this._roll(p, ts); break;
      case 'fling': why = this._fling(p, ts, m.c, vt); break;
      case 'pound': why = this._pound(p, ts, vt, recv); break;
      case 'land': why = this._land(p, ts, vt, m, recv, n); break;
      case 'stomp': why = this._stomp(p, ts, vt, m.target, recv, n); break;
      case 'enterPot': why = this._enterPot(p, ts, m.pot); break;
      case 'exitPot': why = p.st === 'hide' ? (this._leavePot(p, ts, 'exit'), null) : 'not_hidden'; break;
      case 'use': why = this.items ? this.items.use(p, ts, vt, m) : 'no_items'; break;
      case 'selfKo': why = this._selfKo(p, m.reason); break;
    }
    (p.recentActs = p.recentActs || []).push({ a, why: why || undefined, ts: Math.round(ts), at: Math.round(recv) }); if (p.recentActs.length > 5) p.recentActs.shift(); // (for the logs)
    if (why === 'pending') return null; // a landing or a stomp: answered once it has been judged
    this._ack(p, n, a, !why, why);
    if (!why && a !== 'selfKo' && a !== 'use') this._all({ t: 'act', slot: p.slot, a, ts, c: a === 'fling' ? p.flingC : undefined, pot: a === 'enterPot' ? p.pot : undefined }, p);
    return null;
  }
  // still in the air in a pound (once it has landed the player is free, even while the hits are being judged)
  _inPound(p, ts) { const pd = p.pound; return !!pd && !pd.land && ts < pd.t0 + (pd.air ? 3000 : G.POUND_T * 1000 - 60); }
  _canAct(p, ts) {
    if (p.st !== 'play') return p.st === 'hide' ? 'hidden' : 'state';
    if (p.flatUntil > ts + 60) return 'flat';
    if ((p.effects.turret || 0) > ts + 60) return 'busy';
    return null;
  }
  _jump(p, ts) {
    if (p.st === 'hide') { this._leavePot(p, ts, 'jump'); return null; }
    const no = this._canAct(p, ts); if (no) return no;
    if (this._inPound(p, ts)) return 'busy';
    if (p.mover.airborne && ts - p.mover.groundT > 250) return 'air'; // (a moment of grace after rolling off a ledge, like the game)
    p.mover.onJump(ts); return null;
  }
  _roll(p, ts) {
    if (p.st === 'hide') { this._leavePot(p, ts, 'roll'); return null; }
    const no = this._canAct(p, ts); if (no) return no;
    if (this._inPound(p, ts)) return 'busy';
    if (p.mover.airborne) {
      // a mid-air dash: once per hop, a moment untouchable
      if (p.mover.dashUsed) return 'air';
      p.dashStart = ts; p.mover.onDash(ts);
      return null;
    }
    if (ts < p.rollReadyAt - 80) return 'cooldown';
    p.rollStart = ts; p.rollReadyAt = ts + G.ROLL_CD * 1000;
    if (p.paint > 0) p.paint = Math.max(0.001, p.paint - G.ROLL_COST);
    const env = this._env(p, { t: ts, yaw: p.mover.last.yaw });
    p.mover.onRoll(env, ts);
    return null;
  }
  _fling(p, ts, cIn) {
    const c = clamp(fin(cIn) ? cIn : 1, G.FLING_MIN, 1);
    let air = false;
    if (p.st === 'hide') this._leavePot(p, ts, 'fling'); // flinging out of a pot works even when dry
    else {
      const no = this._canAct(p, ts); if (no) return no;
      if (this._inPound(p, ts)) return 'busy';
      if (p.paint <= 0.001) return 'no_paint';
      // in the air this is the mid-air sling (after a hop or a pot exit): once per hop, shared with the air dash
      if (p.mover.airborne && ts - p.mover.groundT > 250) { if (p.mover.dashUsed) return 'air'; p.mover.dashUsed = true; air = true; }
    }
    p.flingC = c; p.flingAt = ts; p.flingOpen = true;
    p.mover.onFling(c, ts, air);
    return null;
  }
  _pound(p, ts, vt, recv) {
    if (p.st !== 'play' && p.st !== 'hide') return 'state';
    if (ts < this.startAt + 50) return 'not_started';
    if (p.flatUntil > ts + 60) return 'flat';
    if ((p.effects.turret || 0) > ts + 60) return 'busy';
    if (p.pound) return 'busy';
    const saved = p.effects.slam === true; // a saved slam (pick-up): no wait, no paint, a bigger circle
    if (saved) p.effects.slam = false;
    else {
      const no = p.slamCd > 0.2 ? 'cooldown' : p.paint < G.POUND_MIN - 0.01 ? 'no_paint' : null;
      if (no) {
        // refused: it does nothing to anyone, but the phone has already gone up into it, so that height is let through
        // and the player isn't put back for it (at most once every 400 ms)
        if (p.st === 'play' && !(p.bounceAt > ts - 400)) {
          const at = sampleHist(p.vhist, ts) || { grounded: !p.mover.airborne }, air = !at.grounded;
          p.bounceAt = ts; if (air && p.flingOpen && p.flingC > 0.15 && ts - p.flingAt < 3000) p.mover.onMissile(ts); else p.mover.onPound(ts, air);
        }
        return no;
      }
      if ((p.effects.giant || 0) <= ts) p.paint -= Math.min(G.SLAM_COST, p.paint - 0.08);
      p.slamCd = this.rules.slamCd;
    }
    p.slams++; p.viewDelay = clamp(ts - vt, 0, this.rules.lagCompMaxMs);
    if (p.st === 'hide') { this._burst(p, ts, vt); return null; }
    const at = sampleHist(p.vhist, ts) || { x: p.mover.last.x, y: p.mover.last.y, z: p.mover.last.z, grounded: !p.mover.airborne };
    const air = !at.grounded, missile = air && p.flingOpen && p.flingC > 0.15 && ts - p.flingAt < 3000;
    p.pound = { t0: ts, vt0: vt, x: at.x, y: at.y, z: at.z, air, missile, giant: saved || (p.effects.giant || 0) > ts, autoAt: recv + (air ? 3000 : G.POUND_T * 1000 + 700), land: null };
    if (missile) p.mover.onMissile(ts); else p.mover.onPound(ts, air);
    return null;
  }
  _land(p, ts, vt, m, recv, n) {
    const pd = p.pound; if (!pd) return 'no_pound';
    if (pd.land) return 'duplicate';
    const dur = (ts - pd.t0) / 1000;
    if (dur < 0 || (!pd.air && (dur < G.POUND_T - 0.15 || dur > G.POUND_T + 0.4)) || dur > 3) { p.pound = null; return 'timing'; }
    pd.land = { ts, vt, n, recv, waitUntil: recv + 300, claim: fin(m.x) && fin(m.z) ? { x: m.x, z: m.z } : null };
    return 'pending';
  }
  // the pound comes down: the splat, and everyone close enough (where the attacker saw them) is a candidate
  _resolvePound(p, now) {
    const pd = p.pound; p.pound = null; if (p.st !== 'play') return;
    const L = pd.land, ts = L ? L.ts : pd.t0 + G.POUND_T * 1000, vt0 = L ? L.vt : ts - p.viewDelay;
    const pos = pd.air ? (sampleHist(p.vhist, ts) || p.mover.last) : { x: pd.x, y: pd.y, z: pd.z };
    if (L && L.claim && Math.hypot(L.claim.x - pos.x, L.claim.z - pos.z) > (pd.air ? 1.6 : 0.9)) {
      this._ack(p, L.n, 'land', false, 'far'); this._violation(p, 'pound_far', false); return;
    }
    const R = (pd.missile ? G.MISSILE_R : G.SLAM_R) * (pd.giant ? G.GIANT_SLAM : 1), koR = R + G.PR;
    this.cov.stamp(pos.x, pos.y, pos.z, R * 0.98, p.color);
    if (pd.giant) p.effects.giant = 0;
    const vt = Math.max(clamp(vt0, ts - this.rules.lagCompMaxMs, ts), now - this.rules.maxRewindMs), cands = [];
    for (const B of this.P) {
      if (B === p || B.side === p.side || (B.st !== 'play' && B.st !== 'hide')) continue;
      const b = B.track.sample(vt, 250); if (!b || Math.hypot(b.x - pos.x, b.z - pos.z) >= koR) continue;
      const sup = this.level.supportAt(b.x, b.z, b.y), base = sup > -Infinity ? sup : b.y, lift = b.y - base;
      if (Math.abs(base - pos.y) >= 1.4) continue; // a different level
      if (lift > 0.6) { this._all({ t: 'dodged', slot: B.slot, by: p.slot, how: 'air' }); continue; }
      cands.push(B.slot);
      this.hits.push({ kind: 'pound', by: p, B, ts, vt, decideAt: Math.min(now + this.rules.dodgeWaitMs, Math.max(now, ts + B.lagEst + 3 * B.jit + 25)) });
    }
    this._all({ t: 'act', slot: p.slot, a: 'slam', ts, x: r2(pos.x), y: r2(pos.y), z: r2(pos.z), r: R }, p);
    if (L) this._ack(p, L.n, 'land', true, null, { x: r2(pos.x), y: r2(pos.y), z: r2(pos.z), candidates: cands });
    if (pd.missile) p.flingOpen = false;
    this._puddleRefill(p, pos, R, ts);
  }
  // the game refills you in a rush when a pound lands in a boiling-water puddle (puddles are 0.85 to 1.25 m across)
  _puddleRefill(p, pos, R, ts) {
    if (this.level.puddles.some(q => Math.abs(q.y - pos.y) < 0.4 && Math.hypot(q.x - pos.x, q.z - pos.z) < R * 0.5 + 1.25)) p.inkRushUntil = Math.max(p.inkRushUntil, ts + 600);
  }
  // judged once the target's own dodge has had time to arrive
  _decide(h, now) {
    const B = h.B, A = h.by;
    if (B.st !== 'play' && B.st !== 'hide') return;
    const safe = this._safeAt(B, h.ts);
    if (safe) { this._all({ t: 'dodged', slot: B.slot, by: A.slot, how: safe }); if (h.n !== undefined) this._ack(A, h.n, h.kind, false, 'dodged'); return; }
    if (h.kind === 'stomp') { this._flatten(B, A, now); if (h.n !== undefined) this._ack(A, h.n, 'stomp', true); return; }
    if ((B.effects.giant || 0) > h.ts && this.items) { this.items.unGiant(B, A); return; }
    this._ko(B, A, this._hiddenAt(B, h.ts) ? 'coffin' : 'pound');
  }
  _hiddenAt(B, ts) { return B.hiddenAt <= ts + 15 && (B.st === 'hide' || B.potExitAt > ts); }
  // why B could not be hit at ts (B's own time), or null
  _safeAt(B, ts) {
    if (ts >= B.rollStart - 20 && ts <= B.rollStart + G.ROLL_T * 1000 + 20) return 'roll';
    if (ts >= B.dashStart - 20 && ts <= B.dashStart + G.DASH_T * 1000 + 20) return 'dash';
    if (B.immuneUntil > ts) return 'immune';
    if ((B.effects.whirl || 0) > ts) return 'whirl';
    if ((B.effects.rocket || 0) > ts) return 'rocket';
    if (this._hiddenAt(B, ts) && this.rules.potShields) return 'pot';
    return null;
  }
  // pound while hidden: burst out of the pot and blast everyone close away (no knock-out)
  _burst(p, ts, vt) {
    const pot = this.pots[p.pot]; if (!pot) return;
    this._leavePot(p, ts, 'burst'); this._sinkPot(pot); // (the burst breaks it, as in the game; it comes back in the same place)
    p.mover.launch(13.5, ts, pot.y + 0.35); // the game throws you high out of the pot (and you splat where you land)
    this.cov.stamp(pot.x, pot.y, pot.z, G.SLAM_R * 0.7, p.color);
    this._puddleRefill(p, pot, G.SLAM_R, ts);
    const now = nowMs(), vtc = Math.max(clamp(vt, ts - this.rules.lagCompMaxMs, ts), now - this.rules.maxRewindMs);
    for (const B of this.P) {
      if (B === p || B.side === p.side || (B.st !== 'play' && B.st !== 'hide')) continue;
      const b = B.track.sample(vtc, 250); if (!b) continue;
      const d = Math.hypot(b.x - pot.x, b.z - pot.z); if (d > KO_R + 1 || Math.abs(b.y - pot.y) > 1.6 || this._safeAt(B, ts)) continue;
      const k = 1 - clamp(d / (KO_R + 1), 0, 1), dx = d > 0.05 ? (b.x - pot.x) / d : Math.sin(p.mover.last.yaw), dz = d > 0.05 ? (b.z - pot.z) / d : Math.cos(p.mover.last.yaw);
      this._push(B, p, dx, dz, 9 + 5 * k, 6 + 1.5 * k, 'burst');
    }
  }
  // the server knocks someone back: their own client moves them, and the referee allows the extra speed for a while
  _push(B, by, dx, dz, spd, vy, why) {
    const now = nowMs();
    if (B.st === 'hide') this._eject(B, 'blasted', by);
    B.mover.onPush(spd, vy, now); B.lastHit = { by, t: now }; B.pound = null;
    this._all({ t: 'push', slot: B.slot, by: by ? by.slot : -1, dx: r2(dx), dz: r2(dz), spd: r2(spd), vy: r2(vy), why });
  }
  _stomp(A, ts, vt, target, recv, n) {
    const B = Number.isInteger(target) ? this.P[target] : null;
    if (!B || B === A || B.side === A.side) return 'target';
    const no = this._canAct(A, ts); if (no) return no;
    const a = sampleHist(A.vhist, ts), a0 = sampleHist(A.vhist, ts - 60);
    const vtc = Math.max(clamp(vt, ts - this.rules.lagCompMaxMs, ts), recv - this.rules.maxRewindMs), b = B.track.sample(vtc, 250);
    // The game bounces the stomper off at once, before the ruling. A near miss (the two phones saw it a little
    // differently) is refused, but its bounce is let through so the stomper is not put back for it: a hop's height,
    // only from the air close over the rival, at most once every 400 ms.
    const bounce = why => {
      if (a && !a.grounded && b && Math.hypot(a.x - b.x, a.z - b.z) < 2 * G.PR + 1 && a.y - b.y > -0.3 && a.y - b.y < 1.8 && !(A.bounceAt > ts - 400)) { A.bounceAt = ts; A.mover.launch(6.5, ts, Math.max(a.y, b.y + 0.3)); }
      return why;
    };
    if (B.st !== 'play') return bounce('target_state');
    if (!a || a.grounded) return 'grounded';
    if (a0 && a.y > a0.y + 0.02) return bounce('rising');
    if (!b) return 'far';
    const d = Math.hypot(a.x - b.x, a.z - b.z), dy = a.y - b.y;
    if (d > 2 * G.PR + 0.25 || dy < 0.1 || dy > 1.3) return bounce('far');
    if (B.flatUntil > ts) return bounce('flat');
    A.mover.launch(6.5, ts, Math.max(a.y, b.y + 0.3)); // the stomper bounces off at once on its own screen (the game's rule)
    this.hits.push({ kind: 'stomp', by: A, B, ts, vt: vtc, n, decideAt: Math.min(recv + this.rules.dodgeWaitMs, Math.max(recv, ts + B.lagEst + 3 * B.jit + 25)) });
    return 'pending';
  }
  _flatten(B, A, now) {
    if (B.flatUntil > now) return;
    const L = B.mover.last;
    B.flatUntil = now + this.rules.flatT * 1000; B.flatAnchor = { x: L.x, z: L.z }; B.flats++; A.stomps++; B.lastHit = { by: A, t: now }; B.pound = null;
    B.cid = nextCid(B.cid); B.mover.last.t = Math.max(B.mover.last.t, now);
    for (const q of this.P) this._send(q, { t: 'flat', slot: B.slot, by: A.slot, x: L.x, y: L.y, z: L.z, until: B.flatUntil, cid: q === B ? B.cid : undefined });
  }
  _enterPot(p, ts, i) {
    const pot = Number.isInteger(i) ? this.pots[i] : null; if (!pot) return 'bad_pot';
    const no = this._canAct(p, ts); if (no) return no;
    if (!pot.up) return 'down'; if (pot.ink <= 0.02) return 'empty';
    const at = sampleHist(p.vhist, ts) || p.mover.last;
    if (Math.hypot(at.x - pot.x, at.z - pot.z) > G.POT_REACH + 0.45 || Math.abs(at.y - pot.y) > 1.1) return 'far';
    if (pot.occ >= 0 && pot.occ !== p.slot) {
      const O = this.P[pot.occ], rolling = ts >= p.rollStart - 20 && ts <= p.rollStart + G.ROLL_T * 1000 + 20;
      if (!rolling || (O.spawnImm && O.immuneUntil > ts)) return 'occupied';
      this._eject(O, 'bumped', p);
    }
    p.st = 'hide'; p.pot = pot.i; pot.occ = p.slot; p.hiddenAt = ts; p.pound = null; p.emptyT = 0; p.flingOpen = false;
    p.mover.reset({ x: pot.x, y: pot.y, z: pot.z, yaw: p.mover.last.yaw }, Math.max(ts, p.mover.last.t));
    this._all({ t: 'pot', i: pot.i, occ: p.slot, up: pot.up, ink: r2(pot.ink) });
    return null;
  }
  _leavePot(p, ts, why) {
    const pot = this.pots[p.pot];
    if (pot && pot.occ === p.slot) pot.occ = -1;
    p.st = 'play'; p.pot = -1; p.potExitAt = ts; p.slamCd = Math.max(p.slamCd, 0.5); p.emptyT = 0;
    if (p.spawnImm) { p.spawnImm = false; p.immuneUntil = ts + G.SPAWN_GRACE * 1000; }
    if (pot) {
      const t0 = Math.max(ts, p.mover.last.t);
      p.mover.reset({ x: pot.x, y: pot.y + G.POT_POP_Y, z: pot.z, yaw: p.mover.last.yaw }, t0, { airborne: true, groundY: pot.y });
      p.mover.onPopOut(t0, pot.y);
      this._all({ t: 'pot', i: pot.i, occ: -1, up: pot.up, ink: r2(pot.ink), why });
      if (pot.ink <= 0.02) this._sinkPot(pot);
    }
  }
  _eject(O, why, by) { const i = O.pot; this._leavePot(O, nowMs(), why); this._all({ t: 'potEject', slot: O.slot, i, why, by: by ? by.slot : -1 }); }
  _freePot(p) { if (p.pot >= 0) { const pot = this.pots[p.pot]; if (pot && pot.occ === p.slot) { pot.occ = -1; this._all({ t: 'pot', i: pot.i, occ: -1, up: pot.up, ink: r2(pot.ink) }); } p.pot = -1; } }
  _sinkPot(pot) { if (!pot.up) return; pot.up = false; pot.upAt = nowMs() + this.rules.potDownT * 1000; this._all({ t: 'pot', i: pot.i, occ: -1, up: false, ink: 0 }); }
  _selfKo(p, reason) {
    if (!SELF_KO.has(reason)) return 'bad_reason';
    if (p.st !== 'play' && p.st !== 'hide') return 'state';
    this._ko(p, null, reason); return null;
  }
  _ko(p, by, reason) {
    if (p.st !== 'play' && p.st !== 'hide') return;
    const now = nowMs(), L = p.mover.last;
    this._freePot(p);
    if (!by && (reason === 'fall' || reason === 'zone') && p.lastHit && now - p.lastHit.t < 3500 && p.lastHit.by.side !== p.side) by = p.lastHit.by;
    p.st = 'ko'; p.pound = null; p.koAt = now; p.deaths++; p.flatUntil = 0; p.koPos = { x: L.x, y: L.y, z: L.z }; p.flingOpen = false; p.zoneT = 0;
    if (by) by.kos++;
    let out = false;
    if (this.showdown) { p.hearts = Math.max(0, p.hearts - 1); if (!p.hearts) { out = true; p.elimAt = now; p.outAt = now + this.rules.sdOutT * 1000; } }
    p.respawnAt = out ? Infinity : now + (by ? this.rules.respawnT : SELF_RESPAWN_T) * 1000;
    if (this.items) this.items.onKo(p);
    this.log.debug('ko', { player: p.id, by: by && by.id, reason });
    this._all({ t: 'ko', slot: p.slot, by: by ? by.slot : -1, reason, x: r2(L.x), y: r2(L.y), z: r2(L.z), respawnAt: out ? null : p.respawnAt, hearts: this.showdown ? p.hearts : undefined, out });
    if (this.showdown) this._checkShowdown(now);
  }
  _respawn(p, now) {
    let cands = this.pots.filter(q => q.up && q.occ < 0);
    const size = zoneSizeAt(this.zone, (now - this.startAt) / 1000), inz = cands.filter(q => Math.max(Math.abs(q.x), Math.abs(q.z)) <= size);
    if (inz.length) cands = inz;
    if (!cands.length) { p.respawnAt = now + 500; return; }
    let best = null, bs = -Infinity; const ko = p.koPos || p.spawn;
    for (const q of cands) {
      let dO = 14; for (const O of this.P) if (O.side !== p.side && (O.st === 'play' || O.st === 'hide')) dO = Math.min(dO, dist2(O.mover.last, q));
      const sc = (q.ink > 0.3 ? 0 : -40) + dO * 1.5 - dist2(ko, q) * 0.25 + q.i * 1e-6;
      if (sc > bs) { bs = sc; best = q; }
    }
    best.ink = Math.max(best.ink, 1); best.occ = p.slot;
    p.st = 'hide'; p.pot = best.i; p.hiddenAt = now; p.immuneUntil = now + G.SPAWN_SAFE * 1000; p.spawnImm = true; p.paint = Math.max(p.paint, 0.5);
    p.cid = nextCid(p.cid); p.mover.reset({ x: best.x, y: best.y, z: best.z, yaw: p.latest.yaw }, now);
    p.vhist = [{ tc: now, tau: Math.round(now), x: best.x, y: best.y, z: best.z, grounded: true }];
    p.flingOpen = false; p.pound = null; p.flatUntil = 0; p.lastMoveAt = now; p.lastHit = null; if (p.lastStateAt >= p.koAt - 1000) p.lastStateAt = Math.max(p.lastStateAt, now); // (time knocked out isn't time away for someone who was playing when it happened; a game that had already stopped sending stays quiet)
    p.latest = { tau: Math.max(p.lastTau + 1, Math.round(now)), tc: now, x: best.x, y: best.y, z: best.z, yaw: p.latest.yaw, spd: 0, vy: 0, flags: 0, aim: 0 }; p.lastTau = p.latest.tau;
    for (const q of this.P) this._send(q, { t: 'respawn', slot: p.slot, pot: best.i, x: best.x, y: best.y, z: best.z, immuneUntil: p.immuneUntil, cid: q === p ? p.cid : undefined });
    this._all({ t: 'pot', i: best.i, occ: p.slot, up: true, ink: r2(best.ink) });
  }
  _checkShowdown(now) {
    const alive = new Set(this.P.filter(q => q.st !== 'left' && q.st !== 'out' && q.hearts > 0).map(q => q.side));
    // a side with nobody left takes the place after everyone still in
    for (const q of this.P) if (!q.place && !alive.has(q.side)) for (const o of this.P) if (o.side === q.side && !o.place) o.place = alive.size + 1;
    if (alive.size <= 1 && !this.endingAt) this.endingAt = now + SD_END_T * 1000;
  }

  // ------------------------------------------------------------------------------------------------ the clock
  tick(now) {
    const dt = Math.min(0.25, Math.max(0, (now - this.lastTick) / 1000)); this.lastTick = now;
    if (this.phase === 'consensus') { if (now > this.layoutDeadline) this.cancel('layout_timeout', this.P.filter(q => !q.layout).map(q => q.id)); return; }
    if (this.phase === 'ended') { if (now >= this.rematchUntil) this.close('rematch_timeout'); return; }
    if (this.phase === 'closed') return;
    if (this.phase === 'countdown' && now >= this.startAt) this.phase = 'play';
    if (this.phase === 'play') this._play(now, dt);
    if (this.phase === 'countdown' || this.phase === 'play') { this._presence(now); this._snapshot(now); }
  }
  _play(now, dt) {
    for (const p of this.P) {
      const pd = p.pound; if (!pd) continue;
      if (pd.land) { const h = p.vhist; if ((h.length && h[h.length - 1].tc >= pd.land.ts) || now >= pd.land.waitUntil) this._resolvePound(p, now); }
      else if (now >= pd.autoAt) { if (pd.air) p.pound = null; else this._resolvePound(p, now); }
    }
    for (let i = this.hits.length - 1; i >= 0; i--) { const h = this.hits[i]; if (now >= h.decideAt) { this.hits.splice(i, 1); this._decide(h, now); } }
    const sideCov = this.cov.bySide(), tS = (now - this.startAt) / 1000, zone = zoneSizeAt(this.zone, tS);
    for (const p of this.P) {
      if (p.st === 'play' || p.st === 'hide') {
        if (p.slamCd > 0) {
          let foe = 0; for (let s = 0; s < sideCov.length; s++) if (s !== p.side) foe = Math.max(foe, sideCov[s]);
          p.slamCd = Math.max(0, p.slamCd - dt * (sideCov[p.side] + 3 < foe ? 1.25 : 1));
        }
        if (zone < Infinity) {
          const L = p.mover.last;
          if (Math.max(Math.abs(L.x), Math.abs(L.z)) > zone) {
            if (p.st === 'hide') this._eject(p, 'zone', null);
            p.paint = Math.max(0, p.paint - G.ZONE_BURN * dt);
            if (p.paint <= 0) { p.zoneT += dt; if (p.zoneT > ZONE_KO) { this._ko(p, null, 'zone'); continue; } }
          } else p.zoneT = 0;
        }
      }
      if (p.st === 'hide') {
        const pot = this.pots[p.pot];
        if (pot) {
          const take = Math.min(G.REGEN * dt, pot.ink, Math.max(0, 1 - p.paint));
          p.paint += take * 1.1; pot.ink -= take; p.paint = Math.min(1, p.paint);
          if (pot.ink <= 0.02) { p.emptyT += dt; if (p.emptyT > POT_EMPTY_T) this._eject(p, 'empty', null); }
        }
      } else if (p.st === 'ko') {
        if (p.respawnAt === Infinity) { if (now >= p.outAt) { p.st = 'out'; this._all({ t: 'out', slot: p.slot, place: p.place || undefined }); } }
        else if (now >= p.respawnAt) this._respawn(p, now);
      }
      if (p.flatUntil && now >= p.flatUntil) p.flatUntil = 0;
    }
    for (const pot of this.pots) if (!pot.up && now >= pot.upAt) { pot.up = true; pot.ink = this.rules.potInk; this._all({ t: 'pot', i: pot.i, occ: -1, up: true, ink: r2(pot.ink) }); }
    if (this.items) this.items.tick(now, dt);
    if (now >= this.nextCovAt) { this.nextCovAt = now + 1000 / this.rules.coverageHz; this._all({ t: 'cov', s: this.cov.bySide().map(r2), c: this.cov.colors().map(r2) }); }
    if (this.showdown) { if (this.endingAt && now >= this.endingAt) return this._end('last_standing'); }
    if (now >= this.endAt) {
      // versus, level at the buzzer (on the whole numbers everyone sees, knock-outs included): play on, once
      if (!this.showdown && !this.otUsed && this.rules.overtime > 0 && this._tied()) { this.otUsed = true; this.endAt = now + this.rules.overtime * 1000; this._all({ t: 'overtime', endAt: this.endAt, secs: this.rules.overtime }); }
      else this._end('time');
    }
  }
  // AFK and disconnects
  _presence(now) {
    for (const p of this.P) {
      if (p.st === 'left') continue;
      if (!p.connected) { if (now - p.awaySince > this.rules.reconnectWindow * 1000) this.forfeit(p, 'disconnected'); continue; }
      if (this.phase !== 'play' || (p.st !== 'play' && p.st !== 'hide')) continue;
      const quiet = now - Math.max(p.lastStateAt, this.startAt); // (counted from Go: building the stage and the countdown don't count)
      if (quiet > this.rules.afkWarn * 1000 && !p.afk) { p.afk = true; this._all({ t: 'afk', slot: p.slot, on: true }); }
      if (quiet > this.rules.afkForfeit * 1000) { this.forfeit(p, 'afk'); continue; }
      if (p.st === 'play' && now - Math.max(p.lastMoveAt, this.startAt) > this.rules.idleForfeit * 1000) this.forfeit(p, 'idle');
    }
  }
  _flags(p, now) {
    const s = p.latest; let f = s.flags & CLIENT_FLAGS;
    if (s.tc >= p.rollStart && s.tc <= p.rollStart + G.ROLL_T * 1000) f |= FLAGS.ROLL;
    if (p.st === 'hide') f |= FLAGS.HIDE;
    if (p.flatUntil > now) f |= FLAGS.FLAT;
    if (p.st === 'ko') f |= FLAGS.KO;
    if (p.immuneUntil > now) f |= FLAGS.IMMUNE;
    if (p.st === 'out' || p.st === 'left' || (this.showdown && p.hearts <= 0)) f |= FLAGS.OUT;
    if (!p.connected) f |= FLAGS.AWAY;
    if (p.afk) f |= FLAGS.AFK;
    if (p.paint <= 0.001) f |= FLAGS.DRY;
    if (p.pound) f |= FLAGS.SLAM;
    if ((p.effects.giant || 0) > now) f |= FLAGS.GIANT;
    if ((p.effects.whirl || 0) > now) f |= FLAGS.WHIRL;
    return f;
  }
  _snapshot(now) {
    const t = Math.round(now), entries = this.P.map(p => {
      const s = p.latest;
      return { slot: p.slot, age: t - s.tau, x: s.x, y: s.y, z: s.z, yaw: s.yaw, spd: s.spd, vy: s.vy, flags: this._flags(p, now), paint: p.paint, aim: s.aim };
    });
    const bytes = codec.encodeSnapshot(++this.snapSeq, t, 0, entries);
    // the lag-compensation history is exactly what the clients were sent (same rounding), so a rewind sees what they saw
    for (const e of codec.decodeSnapshot(bytes).players) this.P[e.slot].track.push(e);
    this.stats.snapshots++;
    for (const p of this.P) {
      if (!p.connected || !p.sess) continue;
      const b = bytes.slice(); codec.setSnapshotAck(b, p.ackSeq);
      this.stats.bytes += b.byteLength; this.srv.sendBinary(p.sess, b, true);
    }
  }

  // ------------------------------------------------------------------------------------------------ the end
  _end(reason) {
    if (this.phase === 'ended' || this.phase === 'closed') return;
    this.phase = 'ended';
    const now = nowMs(), sideCov = this.cov ? this.cov.bySide() : [], colCov = this.cov ? this.cov.colors() : [];
    const places = this._places(sideCov);
    for (const p of this.P) p.place = places.get(p.slot);
    const ratings = this.rated ? rateMatch(this.P.map(p => ({ id: p.id, rating: p.rating, side: p.side, place: p.place }))) : null;
    const best = Math.min(...this.P.map(p => p.place)), winners = new Set(this.P.filter(p => p.place === best).map(p => p.side));
    const winner = winners.size === 1 ? [...winners][0] : -1;
    this.results = {
      matchId: this.id, mode: this.mode, reason, winner, rated: this.rated, duration: Math.max(0, Math.round((now - this.startAt) / 100) / 10),
      results: this.P.map(p => ({
        slot: p.slot, id: p.id, name: p.name, side: p.side, coverage: r2(colCov[p.slot] || 0), sideCoverage: r2(sideCov[p.side] || 0), score: this.showdown ? undefined : this._score(p.side, sideCov),
        kos: p.kos, deaths: p.deaths, flats: p.flats, stomps: p.stomps, hearts: p.hearts, place: p.place, left: p.st === 'left',
        rating: ratings ? { before: Math.round(p.rating.r), after: Math.round(ratings.get(p.id).r), rd: Math.round(ratings.get(p.id).rd) } : null,
      })),
    };
    this.rematchUntil = now + this.rules.rematchWindow * 1000;
    for (const p of this.P) this._send(p, Object.assign({ t: 'matchEnd', rematchUntil: this.rematchUntil }, this.results));
    this.log.info('match ended', { reason, winner, cov: sideCov.map(r2) });
    this.srv.onMatchEnd(this, ratings);
    // a player who left won't play again: no rematch to wait for
    for (const p of this.P) if (p.st === 'left') p.rematch = false;
    this._rematchCheck();
  }
  // a side's versus score, as the game counts it: its coverage in whole percent, plus koPct for each knock-out
  _score(side, sideCov) { let kos = 0; for (const p of this.P) if (p.side === side) kos += p.kos; return Math.round(sideCov[side] || 0) + this.rules.koPct * kos; }
  _tied() {
    const sideCov = this.cov ? this.cov.bySide() : [], live = [...new Set(this.P.filter(p => p.st !== 'left').map(p => p.side))];
    if (live.length < 2) return false;
    const sc = live.map(s => this._score(s, sideCov)).sort((a, b) => b - a); return sc[0] === sc[1];
  }
  // 1 is best. Versus: by score (side coverage, plus the knock-out bonus). Showdown: whoever is still in (most hearts, then knock-outs), then the order
  // sides went out. Anyone who left is last (in a Showdown, unless they were already out: then where they went out).
  _places(sideCov) {
    const sides = [...new Set(this.info.sides)], of = s => this.P.filter(p => p.side === s);
    const gone = s => of(s).every(p => p.st === 'left' && !p.outLeft);
    let order;
    if (!this.showdown) {
      order = sides.filter(s => !gone(s)).map(s => ({ s, k: [this._score(s, sideCov)] }));
    } else {
      const alive = sides.filter(s => of(s).some(p => p.st !== 'left' && p.st !== 'out' && p.hearts > 0));
      order = alive.map(s => ({ s, k: [1e9, of(s).reduce((a, p) => a + p.hearts, 0), of(s).reduce((a, p) => a + p.kos, 0)] }));
      for (const s of sides) if (!alive.includes(s) && !gone(s)) order.push({ s, k: [Math.max(...of(s).map(p => p.elimAt || 0))] });
    }
    order.sort((a, b) => { for (let i = 0; i < Math.max(a.k.length, b.k.length); i++) { const d = (b.k[i] || 0) - (a.k[i] || 0); if (Math.abs(d) > 1e-9) return d; } return 0; });
    const placeOf = new Map(); let place = 0, prev = null;
    order.forEach((o, i) => { if (!prev || prev.k.join() !== o.k.join()) place = i + 1; placeOf.set(o.s, place); prev = o; });
    const last = sides.length;
    const out = new Map();
    for (const p of this.P) out.set(p.slot, p.st === 'left' && !p.outLeft ? last : placeOf.get(p.side) || last);
    return out;
  }
  onRematch(p, vote) {
    if (this.phase !== 'ended' || p.st === 'left') return;
    p.rematch = !!vote;
    this._all({ t: 'rematch', votes: this.P.map(q => q.rematch), until: this.rematchUntil });
    this._rematchCheck();
  }
  _rematchCheck() {
    if (this.phase !== 'ended') return;
    if (this.P.some(q => q.rematch === false)) return this.close('rematch_declined');
    if (this.P.every(q => q.rematch === true && q.connected)) { this.phase = 'closed'; this.srv.rematch(this); }
  }
  // what /health and the tests look at
  summary() { return { id: this.id, mode: this.mode, phase: this.phase, players: this.P.map(p => ({ id: p.id, st: p.st, connected: p.connected })) }; }
}
