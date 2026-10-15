/*
 * RMNet: the Roll Model multiplayer client SDK.
 *
 * One file with no imports. Works in browsers (including the iOS WKWebView) and in Node 22+ (globalThis.WebSocket).
 *
 *   As an ES module:        import { RMNet } from './rmnet.js'
 *   In a classic <script>:  paste the whole file except its last line (the export line). It then defines a single
 *                           global, RMNetSDK, and sets window.RMNet.
 *
 * Times: every time the SDK sends or reports is in the server clock, in milliseconds (see serverNow()).
 * Units: metres, metres per second, radians (yaw uses the game's convention: forward is (sin yaw, cos yaw)).
 * The server is the referee. This SDK never decides a knock-out, a pick-up or a score; it reports what the server says.
 */
const RMNetSDK = (() => {
  'use strict';

  const PROTOCOL_VERSION = 1;
  // players per match for each mode
  const MODES = Object.freeze({ duel: 2, trio: 3, ffa: 4, duo: 4 });
  // state flags (bitfield). The server keeps its own copy of the ones that matter (roll, hide, flat, ko, immune, out).
  const FLAGS = Object.freeze({
    AIR: 1 << 0, ROLL: 1 << 1, CHARGE: 1 << 2, SLAM: 1 << 3, HIDE: 1 << 4, FLUNG: 1 << 5, DRY: 1 << 6, FLAT: 1 << 7,
    GIANT: 1 << 8, WHIRL: 1 << 9, MISSILE: 1 << 10, KO: 1 << 11, IMMUNE: 1 << 12, OUT: 1 << 13, AWAY: 1 << 14, AFK: 1 << 15,
  });
  const FLAG_NAMES = { air: FLAGS.AIR, rolling: FLAGS.ROLL, charging: FLAGS.CHARGE, slam: FLAGS.SLAM, hidden: FLAGS.HIDE, flung: FLAGS.FLUNG, dry: FLAGS.DRY, missile: FLAGS.MISSILE };
  // binary message types (first byte)
  const MSG = Object.freeze({ STATE: 1, PING: 2, PONG: 3, SPING: 4, SPONG: 5, SNAP: 16 });
  const STATE_BYTES = 34, PING_BYTES = 9, PONG_BYTES = 17, SNAP_HEAD = 14, SNAP_ENTRY = 19;
  const TAU = Math.PI * 2;
  const GRAV = 15, FALL_K = 1.45;
  const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
  const wrapA = a => { a = (a + Math.PI) % TAU; if (a < 0) a += TAU; return a - Math.PI; };
  const fin = v => typeof v === 'number' && Number.isFinite(v);

  // ---------------------------------------------------------------------------------------------------------------
  // Layout canonical form and hash. The server runs exactly this code too (it imports this file).
  //
  // layout = { arena, boxes: [[x0,x1,z0,z1,y0,y1,shape?]], ramps: [[x0,x1,z0,z1,axis,h0,h1]], holes: [[x0,x1,z0,z1,shape?]],
  //            pots: [[x,y,z]], powers: [[x,y,z,kind?]], spawns: [[x,z,yaw]] }
  // Canonical form: the prefix "RM1" followed by JSON of
  //   [arena, boxes, ramps, holes, pots, powers, spawns]
  // where every number becomes Math.round(n * 100) (an integer count of hundredths, -0 written as 0), a box or hole
  // shape is kept only when it is 'c' (round), a ramp axis is 'x' or 'z', and a power kind is kept only when it is a
  // non-empty string. Arrays keep their order. The hash is a 64-bit FNV-1a style mix (two 32-bit lanes) of that string,
  // written as 16 lowercase hex digits.
  // ---------------------------------------------------------------------------------------------------------------
  function q100(v, what) {
    if (!fin(v)) throw new TypeError('layout: ' + what + ' is not a finite number');
    return Math.round(v * 100) || 0;
  }
  function arr(a, what) { if (!Array.isArray(a)) throw new TypeError('layout: ' + what + ' must be an array'); return a; }
  function canonicalParts(L) {
    if (!L || typeof L !== 'object') throw new TypeError('layout: not an object');
    const nums = (e, n, what) => { arr(e, what); if (e.length < n) throw new TypeError('layout: ' + what + ' needs ' + n + ' numbers'); const o = []; for (let i = 0; i < n; i++) o.push(q100(e[i], what)); return o; };
    const boxes = arr(L.boxes, 'boxes').map((b, i) => { const o = nums(b, 6, 'boxes[' + i + ']'); if (b[6] === 'c') o.push('c'); return o; });
    const ramps = arr(L.ramps, 'ramps').map((r, i) => {
      arr(r, 'ramps[' + i + ']'); if (r.length < 7) throw new TypeError('layout: ramps[' + i + '] needs 7 fields');
      if (r[4] !== 'x' && r[4] !== 'z') throw new TypeError('layout: ramps[' + i + '] axis must be x or z');
      return [q100(r[0], 'ramp'), q100(r[1], 'ramp'), q100(r[2], 'ramp'), q100(r[3], 'ramp'), r[4], q100(r[5], 'ramp'), q100(r[6], 'ramp')];
    });
    const holes = arr(L.holes, 'holes').map((h, i) => { const o = nums(h, 4, 'holes[' + i + ']'); if (h[4] === 'c') o.push('c'); return o; });
    const pots = arr(L.pots, 'pots').map((p, i) => nums(p, 3, 'pots[' + i + ']'));
    const powers = arr(L.powers, 'powers').map((p, i) => { const o = nums(p, 3, 'powers[' + i + ']'); if (typeof p[3] === 'string' && p[3].length) o.push(p[3]); return o; });
    const spawns = arr(L.spawns, 'spawns').map((s, i) => nums(s, 3, 'spawns[' + i + ']'));
    return [q100(L.arena, 'arena'), boxes, ramps, holes, pots, powers, spawns];
  }
  function canonicalLayout(L) { return 'RM1' + JSON.stringify(canonicalParts(L)); }
  function hashString(s) {
    let h1 = 0x811c9dc5 | 0, h2 = 0x01000193 ^ 0x5bd1e995;
    for (let i = 0; i < s.length; i++) {
      const c = s.charCodeAt(i);
      h1 = Math.imul(h1 ^ c, 0x01000193);
      h2 = Math.imul(h2 ^ c, 0x5bd1e995); h2 ^= h2 >>> 15;
    }
    h1 ^= s.length; h1 = Math.imul(h1 ^ (h1 >>> 16), 0x85ebca6b); h1 = Math.imul(h1 ^ (h1 >>> 13), 0xc2b2ae35); h1 ^= h1 >>> 16;
    h2 ^= h1; h2 = Math.imul(h2 ^ (h2 >>> 16), 0x85ebca6b); h2 = Math.imul(h2 ^ (h2 >>> 13), 0xc2b2ae35); h2 ^= h2 >>> 16;
    return (h2 >>> 0).toString(16).padStart(8, '0') + (h1 >>> 0).toString(16).padStart(8, '0');
  }
  function layoutHash(L) { return hashString(canonicalLayout(L)); }
  // Build the layout object from the game's own stage arrays. Holes in the game keep 'c' at index 6 and boxes may carry
  // an extra kind at index 7; this writes them in the layout format above. spawns: [{x,z,yaw}, ...] for the match's players.
  function layoutFromStage({ arena, boxes, ramps, holes, pots, powers, spawns }) {
    return {
      arena: +arena,
      boxes: boxes.map(b => (b[6] === 'c' ? [b[0], b[1], b[2], b[3], b[4], b[5], 'c'] : [b[0], b[1], b[2], b[3], b[4], b[5]])),
      ramps: ramps.map(r => [r[0], r[1], r[2], r[3], r[4], r[5], r[6]]),
      holes: holes.map(h => (h[6] === 'c' || h[4] === 'c' ? [h[0], h[1], h[2], h[3], 'c'] : [h[0], h[1], h[2], h[3]])),
      pots: pots.map(p => [p[0], p[1], p[2]]),
      powers: powers.map(p => (typeof p[3] === 'string' && p[3] ? [p[0], p[1], p[2], p[3]] : [p[0], p[1], p[2]])),
      spawns: spawns.filter(Boolean).map(s => (Array.isArray(s) ? [s[0], s[1], s[2]] : [s.x, s.z, s.yaw])),
    };
  }

  // ---------------------------------------------------------------------------------------------------------------
  // Binary codec (little-endian). Shared with the server.
  // STATE (client to server, 34 bytes): u8 type=1, u8 corrAck, u16 seq, f64 t, f32 x, f32 y, f32 z, u16 yaw,
  //   i16 spd (cm/s), i16 vy (cm/s), u16 flags, u8 paint (0..255), u8 aim (0..255)
  // PING (9): u8 type=2, f64 client clock       PONG (17): u8 type=3, f64 echoed client clock, f64 server time
  // SPING (9): u8 type=4, f64 server time       SPONG (9): u8 type=5, f64 echoed server time
  // SNAP (server to client): u8 type=16, u8 count, u16 seq, f64 server time, u16 ack (your last state seq the server
  //   processed), then per player 19 bytes: u8 slot, u16 age (ms before the snapshot time), i16 x, i16 y, i16 z (cm),
  //   u16 yaw, i16 spd (cm/s), i16 vy (cm/s), u16 flags, u8 paint, u8 aim
  // ---------------------------------------------------------------------------------------------------------------
  const yawToU16 = y => Math.round(((y % TAU) + TAU) % TAU / TAU * 65536) & 0xffff;
  const u16ToYaw = u => u / 65536 * TAU;
  const i16 = v => clamp(Math.round(v), -32768, 32767);
  const u8 = v => clamp(Math.round(v), 0, 255);
  function view(buf) {
    if (buf instanceof ArrayBuffer) return new DataView(buf);
    if (ArrayBuffer.isView(buf)) return new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
    return null;
  }
  function encodeState(s, seq, t, corrAck) {
    const b = new ArrayBuffer(STATE_BYTES), d = new DataView(b);
    d.setUint8(0, MSG.STATE); d.setUint8(1, corrAck & 0xff); d.setUint16(2, seq & 0xffff, true); d.setFloat64(4, t, true);
    d.setFloat32(12, s.x, true); d.setFloat32(16, s.y, true); d.setFloat32(20, s.z, true);
    d.setUint16(24, yawToU16(s.yaw || 0), true); d.setInt16(26, i16((s.spd || 0) * 100), true); d.setInt16(28, i16((s.vy || 0) * 100), true);
    d.setUint16(30, (s.flags || 0) & 0xffff, true); d.setUint8(32, u8((s.paint === undefined ? 1 : s.paint) * 255)); d.setUint8(33, u8((s.aim || 0) * 255));
    return b;
  }
  // returns null for anything malformed (wrong size, NaN, infinities)
  function decodeState(buf) {
    const d = view(buf); if (!d || d.byteLength !== STATE_BYTES || d.getUint8(0) !== MSG.STATE) return null;
    const t = d.getFloat64(4, true), x = d.getFloat32(12, true), y = d.getFloat32(16, true), z = d.getFloat32(20, true);
    if (!fin(t) || !fin(x) || !fin(y) || !fin(z)) return null;
    return {
      corrAck: d.getUint8(1), seq: d.getUint16(2, true), t, x, y, z, yaw: u16ToYaw(d.getUint16(24, true)),
      spd: d.getInt16(26, true) / 100, vy: d.getInt16(28, true) / 100, flags: d.getUint16(30, true),
      paint: d.getUint8(32) / 255, aim: d.getUint8(33) / 255,
    };
  }
  function encodeTime(type, t) { const b = new ArrayBuffer(PING_BYTES), d = new DataView(b); d.setUint8(0, type); d.setFloat64(1, t, true); return b; }
  function decodeTime(buf, type) { const d = view(buf); if (!d || d.byteLength !== PING_BYTES || d.getUint8(0) !== type) return null; const t = d.getFloat64(1, true); return fin(t) ? t : null; }
  function encodePong(c, s) { const b = new ArrayBuffer(PONG_BYTES), d = new DataView(b); d.setUint8(0, MSG.PONG); d.setFloat64(1, c, true); d.setFloat64(9, s, true); return b; }
  function decodePong(buf) { const d = view(buf); if (!d || d.byteLength !== PONG_BYTES || d.getUint8(0) !== MSG.PONG) return null; const c = d.getFloat64(1, true), s = d.getFloat64(9, true); return fin(c) && fin(s) ? { c, s } : null; }
  // entries: [{slot, age, x, y, z, yaw, spd, vy, flags, paint, aim}]
  function encodeSnapshot(seq, t, ack, entries) {
    const n = Math.min(entries.length, 255), b = new Uint8Array(SNAP_HEAD + n * SNAP_ENTRY), d = new DataView(b.buffer);
    d.setUint8(0, MSG.SNAP); d.setUint8(1, n); d.setUint16(2, seq & 0xffff, true); d.setFloat64(4, t, true); d.setUint16(12, ack & 0xffff, true);
    for (let i = 0; i < n; i++) {
      const e = entries[i], o = SNAP_HEAD + i * SNAP_ENTRY;
      d.setUint8(o, e.slot); d.setUint16(o + 1, clamp(Math.round(e.age), 0, 65535), true);
      d.setInt16(o + 3, i16(e.x * 100), true); d.setInt16(o + 5, i16(e.y * 100), true); d.setInt16(o + 7, i16(e.z * 100), true);
      d.setUint16(o + 9, yawToU16(e.yaw || 0), true); d.setInt16(o + 11, i16((e.spd || 0) * 100), true); d.setInt16(o + 13, i16((e.vy || 0) * 100), true);
      d.setUint16(o + 15, (e.flags || 0) & 0xffff, true); d.setUint8(o + 17, u8((e.paint || 0) * 255)); d.setUint8(o + 18, u8((e.aim || 0) * 255));
    }
    return b;
  }
  function setSnapshotAck(bytes, ack) { new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength).setUint16(12, ack & 0xffff, true); }
  function decodeSnapshot(buf) {
    const d = view(buf); if (!d || d.byteLength < SNAP_HEAD || d.getUint8(0) !== MSG.SNAP) return null;
    const n = d.getUint8(1); if (d.byteLength !== SNAP_HEAD + n * SNAP_ENTRY) return null;
    const t = d.getFloat64(4, true); if (!fin(t)) return null;
    const players = [];
    for (let i = 0; i < n; i++) {
      const o = SNAP_HEAD + i * SNAP_ENTRY, age = d.getUint16(o + 1, true);
      players.push({
        slot: d.getUint8(o), age, t: t - age, x: d.getInt16(o + 3, true) / 100, y: d.getInt16(o + 5, true) / 100, z: d.getInt16(o + 7, true) / 100,
        yaw: u16ToYaw(d.getUint16(o + 9, true)), spd: d.getInt16(o + 11, true) / 100, vy: d.getInt16(o + 13, true) / 100,
        flags: d.getUint16(o + 15, true), paint: d.getUint8(o + 17) / 255, aim: d.getUint8(o + 18) / 255,
      });
    }
    return { seq: d.getUint16(2, true), t, ack: d.getUint16(12, true), players };
  }
  const codec = {
    encodeState, decodeState, encodeSnapshot, decodeSnapshot, setSnapshotAck, encodePong, decodePong,
    encodePing: t => encodeTime(MSG.PING, t), decodePing: b => decodeTime(b, MSG.PING),
    encodeSPing: t => encodeTime(MSG.SPING, t), decodeSPing: b => decodeTime(b, MSG.SPING),
    encodeSPong: t => encodeTime(MSG.SPONG, t), decodeSPong: b => decodeTime(b, MSG.SPONG),
    yawToU16, u16ToYaw, STATE_BYTES, PING_BYTES, PONG_BYTES, SNAP_HEAD, SNAP_ENTRY,
  };

  // ---------------------------------------------------------------------------------------------------------------
  // Remote players: a short buffer of states per player, sampled at a render time (interpolation, then a short
  // extrapolation when snapshots are late, then hold). The server rewinds hits with exactly this sampling.
  // ---------------------------------------------------------------------------------------------------------------
  const TELEPORT_M = 5; // two states further apart than this are a jump (respawn, correction): never slide between them
  class RemoteTrack {
    constructor(max = 96) { this.s = []; this.max = max; }
    push(st) {
      const s = this.s, last = s[s.length - 1];
      if (last && st.t <= last.t) return false; // old or duplicate
      s.push(st); if (s.length > this.max) s.shift();
      return true;
    }
    get newest() { return this.s[this.s.length - 1] || null; }
    clear() { this.s.length = 0; }
    // returns a fresh object, or null when there is nothing yet
    sample(R, maxExtrap = 250) {
      const s = this.s, n = s.length; if (!n) return null;
      if (R <= s[0].t) return Object.assign({}, s[0], { t: R, extrapolated: false, held: false });
      const last = s[n - 1];
      if (R >= last.t) {
        const dtMs = Math.min(R - last.t, maxExtrap), dt = dtMs / 1000, prev = n > 1 ? s[n - 2] : null;
        let vx, vz;
        const gap = prev ? last.t - prev.t : 0;
        if (prev && gap >= 8 && gap <= 250 && Math.hypot(last.x - prev.x, last.z - prev.z) < TELEPORT_M) { vx = (last.x - prev.x) / gap * 1000; vz = (last.z - prev.z) / gap * 1000; }
        else { vx = Math.sin(last.yaw) * last.spd; vz = Math.cos(last.yaw) * last.spd; }
        const o = Object.assign({}, last, { t: R, extrapolated: dtMs > 0, held: R - last.t > maxExtrap });
        if ((last.flags & (FLAGS.KO | FLAGS.HIDE | FLAGS.FLAT)) === 0) {
          o.x = last.x + vx * dt; o.z = last.z + vz * dt;
          if (last.flags & FLAGS.AIR) { const g = last.vy > 0 ? GRAV : GRAV * FALL_K; o.y = last.y + last.vy * dt - 0.5 * g * dt * dt; o.vy = last.vy - g * dt; if (o.y < last.y - 3) o.y = last.y - 3; }
        }
        return o;
      }
      // binary search for s[i].t <= R < s[i+1].t
      let lo = 0, hi = n - 1;
      while (hi - lo > 1) { const m = (lo + hi) >> 1; if (s[m].t <= R) lo = m; else hi = m; }
      const a = s[lo], b = s[hi], k = (R - a.t) / (b.t - a.t);
      if (Math.hypot(b.x - a.x, b.z - a.z) > TELEPORT_M) return Object.assign({}, k < 1 ? a : b, { t: R, extrapolated: false, held: false });
      return {
        slot: a.slot, t: R, x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k, z: a.z + (b.z - a.z) * k,
        yaw: a.yaw + wrapA(b.yaw - a.yaw) * k, spd: a.spd + (b.spd - a.spd) * k, vy: a.vy + (b.vy - a.vy) * k,
        flags: k < 0.5 ? a.flags : b.flags, paint: a.paint + (b.paint - a.paint) * k, aim: a.aim + (b.aim - a.aim) * k,
        extrapolated: false, held: false,
      };
    }
  }

  // Clock: ping/pong. Each sample gives an offset (server time + half the round trip - our time) whose error is half
  // the difference between the two directions' delays, which is smallest when the round trip is smallest. So the
  // estimate averages the offsets of the quickest quarter of the recent samples (min-RTT filtering).
  class ClockSync {
    constructor() { this.samples = []; this.offset = 0; this.rtt = 0; this.minRtt = 0; this.jitter = 0; this.n = 0; this._last = null; this.locked = false; }
    add(sent, server, recv) {
      const rtt = recv - sent; if (!(rtt >= 0) || rtt > 30000 || !fin(server)) return false;
      this.samples.push({ rtt, off: server + rtt / 2 - recv }); if (this.samples.length > 32) this.samples.shift();
      const best = this.samples.slice().sort((a, b) => a.rtt - b.rtt).slice(0, Math.max(1, Math.min(this.samples.length, Math.max(3, this.samples.length >> 2))));
      let est = 0; for (const s of best) est += s.off; est /= best.length;
      // before a match (or a big disagreement) jump straight to the estimate; during a match, slew a few ms per sample
      // so the render clock never jumps under the player's eyes
      if (!this.locked || this.n < 6 || Math.abs(est - this.offset) > 250) this.offset = est;
      else this.offset += clamp(est - this.offset, -3, 3);
      this.n++;
      this.rtt = this.n === 1 ? rtt : this.rtt + (rtt - this.rtt) * 0.2;
      if (this._last !== null) this.jitter += (Math.abs(rtt - this._last) - this.jitter) / 8;
      this._last = rtt; this.minRtt = best[0].rtt;
      return true;
    }
  }

  // The interpolation delay: how far behind the server clock remote players are drawn. It covers the measured age of
  // states when they arrive (95th percentile over the last 2 s, so jitter is included) plus one snapshot interval, kept
  // between minDelay and maxDelay, and it eases (never jumps) so remote motion stays smooth.
  class InterpDelay {
    constructor(min, max) { this.min = min; this.max = max; this.delay = null; this.target = 100; this.ages = []; this.interval = 33; this.lastArr = null; this.lastUpd = null; this.jitter = 0; this.meanAge = 0; }
    onSnapshot(local, serverAtArrival, stamps) {
      if (this.lastArr !== null) { const iv = local - this.lastArr; if (iv > 0 && iv < 1000) this.interval += (iv - this.interval) * 0.1; }
      this.lastArr = local;
      for (const st of stamps) this.ages.push(local, serverAtArrival - st);
      while (this.ages.length > 2 && local - this.ages[0] > 2000) this.ages.splice(0, 2);
      const a = []; for (let i = 1; i < this.ages.length; i += 2) a.push(this.ages[i]);
      if (!a.length) return;
      a.sort((x, y) => x - y);
      const p95 = a[Math.min(a.length - 1, Math.floor(a.length * 0.95))];
      let m = 0; for (const v of a) m += v; m /= a.length; let dev = 0; for (const v of a) dev += Math.abs(v - m); dev /= a.length;
      this.meanAge = m; this.jitter = dev;
      this.target = clamp(p95 + this.interval + 5, this.min, this.max);
    }
    value(local) {
      if (this.delay === null) { this.delay = this.target; this.lastUpd = local; return this.delay; }
      const dt = Math.max(0, local - this.lastUpd); this.lastUpd = local;
      const step = dt * (this.target > this.delay ? 0.1 : 0.04);
      this.delay += clamp(this.target - this.delay, -step, step);
      return this.delay;
    }
  }

  // ---------------------------------------------------------------------------------------------------------------
  // RMNet
  // ---------------------------------------------------------------------------------------------------------------
  class RMNet {
    // opts: { url, name, look, token, WebSocket?, now?, autoReconnect = true, sendHz = 30, minInterp = 60, maxInterp = 200,
    //         maxExtrapolate = 250, client? }
    constructor(opts = {}) {
      this.url = opts.url; this.name = opts.name || 'Player'; this.look = opts.look === undefined ? null : opts.look;
      this.token = opts.token || null; this.client = opts.client || null;
      this.WS = opts.WebSocket || globalThis.WebSocket;
      this._now = opts.now || (() => (globalThis.performance && performance.now ? performance.now() : Date.now()));
      this.autoReconnect = opts.autoReconnect !== false;
      this.sendInterval = 1000 / (opts.sendHz || 30);
      this.maxExtrapolate = opts.maxExtrapolate === undefined ? 250 : opts.maxExtrapolate;
      this.id = null; this.rating = null; this.connected = false; this.match = null; this.slot = -1; this.room = null;
      this.ws = null; this._h = new Map(); this._closing = false; this._attempt = 0; this._retryTimer = null;
      this._clock = new ClockSync(); this._interp = new InterpDelay(opts.minInterp || 60, opts.maxInterp || 200);
      this._tracks = new Map(); this._seq = 0; this._nextSend = 0; this._corr = 0; this._ack = 0;
      this._req = 0; this._waits = new Map(); this._act = 0; this._acts = new Map(); this._pingTimer = null; this._pingsSent = 0;
      this._snapTimes = []; this._extrap = 0; this._samples = 0;
      this._st = { corrections: 0, snapshots: 0, rejected: 0, bytesIn: 0, bytesOut: 0 };
    }

    // ---- events ----
    on(ev, fn) { if (!this._h.has(ev)) this._h.set(ev, new Set()); this._h.get(ev).add(fn); return () => this.off(ev, fn); }
    off(ev, fn) { const s = this._h.get(ev); if (s) s.delete(fn); }
    _emit(ev, data) { const s = this._h.get(ev); if (s) for (const fn of [...s]) { try { fn(data); } catch (e) { if (ev !== 'error') this._emit('error', { code: 'handler', message: String(e && e.message || e) }); } } }

    // ---- connection ----
    // resolves with the welcome message; rejects if the server refuses (for example a protocol version mismatch)
    connect() {
      this._closing = false;
      return new Promise((resolve, reject) => {
        const offW = this.on('welcome', w => { offW(); offE(); resolve(w); });
        const offE = this.on('fatal', e => { offW(); offE(); reject(Object.assign(new Error(e.message || e.code), { code: e.code })); });
        this._open();
      });
    }
    close() {
      this._closing = true; clearTimeout(this._retryTimer); this._stopPings();
      if (this.ws) { try { this._sendJ({ t: 'bye' }); this.ws.close(1000, 'bye'); } catch (e) { /* already closed */ } }
    }
    _open() {
      let ws;
      try { ws = new this.WS(this.url); } catch (e) { this._scheduleReconnect(); return; }
      this.ws = ws; ws.binaryType = 'arraybuffer';
      ws.onopen = () => {
        if (this.ws !== ws) return;
        this._attempt = 0; this.connected = true; this._emit('open', {});
        this._sendJ({ t: 'hello', v: PROTOCOL_VERSION, token: this.token || undefined, name: this.name, look: this.look, client: this.client || undefined });
        this._startPings();
      };
      ws.onmessage = ev => { if (this.ws === ws) this._onMessage(ev.data); };
      ws.onerror = () => { /* followed by close */ };
      ws.onclose = ev => {
        if (this.ws !== ws) return;
        this.connected = false; this.ws = null; this._stopPings();
        for (const [, w] of this._waits) w.reject(Object.assign(new Error('disconnected'), { code: 'disconnected' }));
        this._waits.clear();
        const again = !this._closing && this.autoReconnect && !this._noRetry;
        this._emit('close', { code: ev && ev.code, reason: ev && ev.reason, willReconnect: again });
        if (again) this._scheduleReconnect();
      };
    }
    _scheduleReconnect() {
      if (this._closing || !this.autoReconnect) return;
      const base = Math.min(8000, 400 * Math.pow(2, this._attempt)), delay = Math.round(base * (0.75 + Math.random() * 0.5));
      this._attempt++; this._emit('reconnecting', { attempt: this._attempt, delay });
      clearTimeout(this._retryTimer); this._retryTimer = setTimeout(() => this._open(), delay);
    }
    _sendJ(o) { if (!this.ws || this.ws.readyState !== 1) return false; const s = JSON.stringify(o); this._st.bytesOut += s.length; this.ws.send(s); return true; }
    _sendB(b) { if (!this.ws || this.ws.readyState !== 1) return false; this._st.bytesOut += b.byteLength; this.ws.send(b); return true; }
    // sends a request; the server answers with the same r (or an error carrying it)
    _request(msg) {
      const r = ++this._req; msg.r = r;
      return new Promise((resolve, reject) => {
        if (!this._sendJ(msg)) { reject(Object.assign(new Error('not connected'), { code: 'disconnected' })); return; }
        const timer = setTimeout(() => { this._waits.delete(r); reject(Object.assign(new Error('timeout'), { code: 'timeout' })); }, 10000);
        this._waits.set(r, { resolve: v => { clearTimeout(timer); resolve(v); }, reject: e => { clearTimeout(timer); reject(e); } });
      });
    }

    // ---- clock ----
    localNow() { return this._now(); }
    serverNow() { return this._now() + this._clock.offset; }
    _startPings() {
      this._stopPings(); this._pingsSent = 0;
      // a quick burst to start with, then two a second (9 bytes each way: cheap, and it keeps a phone's radio awake)
      const tick = () => { this._sendB(codec.encodePing(this._now())); this._pingsSent++; this._pingTimer = setTimeout(tick, this._pingsSent < 8 ? 100 : 500); };
      tick();
    }
    _stopPings() { clearTimeout(this._pingTimer); this._pingTimer = null; }

    // ---- lobby ----
    queue(mode) { return this._request({ t: 'queue', mode }); }
    cancelQueue() { return this._request({ t: 'cancelQueue' }); }
    createRoom(mode) { return this._request({ t: 'createRoom', mode }).then(r => r.code); }
    joinRoom(code) { return this._request({ t: 'joinRoom', code: String(code || '').toUpperCase() }); }
    leaveRoom() { return this._request({ t: 'leaveRoom' }); }
    ready(on = true) { return this._sendJ({ t: 'ready', ready: !!on }); }
    rematch(vote = true) { return this._sendJ({ t: 'rematch', vote: !!vote }); }
    setName(name) { return this._request({ t: 'setName', name }).then(r => { this.name = r.name; return r.name; }); }

    // ---- map consensus ----
    layoutHash(layout) { return layoutHash(layout); }
    sendLayout(layout) {
      if (!this.match) return false;
      const hash = layoutHash(layout); this.match.layoutHash = hash;
      return this._sendJ({ t: 'layout', m: this.match.id, hash, layout });
    }

    // ---- play ----
    // state: { x, y, z, yaw, spd, vy, paint, aim, flags } or booleans { air, rolling, charging, slam, hidden, flung, dry, missile }
    // Call every frame; the SDK sends at most sendHz times a second (force = true sends now).
    sendState(state, force = false) {
      const now = this._now();
      if (!force && now < this._nextSend) return false;
      // keep a steady cadence: the next slot is one interval after this one, unless that is already past (no bursts)
      this._nextSend = this._nextSend + this.sendInterval > now ? this._nextSend + this.sendInterval : now + this.sendInterval;
      let flags = state.flags;
      if (flags === undefined) { flags = 0; for (const k in FLAG_NAMES) if (state[k]) flags |= FLAG_NAMES[k]; }
      if (!fin(state.x) || !fin(state.y) || !fin(state.z)) return false;
      this._seq = (this._seq + 1) & 0xffff;
      return this._sendB(codec.encodeState(Object.assign({}, state, { flags }), this._seq, this.serverNow(), this._corr));
    }
    // type: 'jump' | 'roll' | 'fling' | 'pound' | 'land' | 'stomp' | 'enterPot' | 'exitPot' | 'use' | 'selfKo'
    // data may include ts (when it happened, server clock; default now) and vt (the render time you were seeing).
    // Resolves { ok, reason? } once the server rules on it. Apply the effect at once; undo it if ok is false.
    action(type, data = {}) {
      const n = ++this._act, msg = Object.assign({}, data, { t: 'act', a: type, n });
      if (msg.ts === undefined) msg.ts = this.serverNow();
      if (msg.vt === undefined) msg.vt = this.renderTime();
      return new Promise(resolve => {
        if (!this._sendJ(msg)) { resolve({ ok: false, reason: 'disconnected' }); return; }
        const timer = setTimeout(() => { this._acts.delete(n); resolve({ ok: false, reason: 'timeout' }); }, 5000);
        this._acts.set(n, r => { clearTimeout(timer); resolve(r); });
      });
    }
    renderTime() { return this.serverNow() - this._interp.value(this._now()); }
    // id: a player id or a slot number. Returns the remote player's state at renderTime (default: now minus the
    // interpolation delay), or null if nothing has arrived yet.
    remote(id, renderTime) {
      const slot = typeof id === 'number' ? id : this._slotOf(id); const tr = this._tracks.get(slot); if (!tr) return null;
      const R = renderTime === undefined ? this.renderTime() : renderTime;
      const o = tr.sample(R, this.maxExtrapolate); if (!o) return null;
      this._samples++; if (o.extrapolated) this._extrap++;
      o.slot = slot; o.id = this._idOf(slot); return o;
    }
    players() { return this.match ? this.match.players.slice() : []; }
    _slotOf(id) { if (!this.match) return -1; const p = this.match.players.find(q => q.id === id); return p ? p.slot : -1; }
    _idOf(slot) { if (!this.match) return null; const p = this.match.players.find(q => q.slot === slot); return p ? p.id : null; }

    stats() {
      const now = this._now(); while (this._snapTimes.length && now - this._snapTimes[0] > 1000) this._snapTimes.shift();
      return {
        rtt: this._clock.rtt, minRtt: this._clock.minRtt, jitter: this._clock.jitter, offset: this._clock.offset,
        interpDelay: this._interp.delay === null ? this._interp.target : this._interp.delay, interpTarget: this._interp.target,
        transitJitter: this._interp.jitter, snapshotAge: this._interp.meanAge, snapshotInterval: this._interp.interval,
        snapshotsPerSec: this._snapTimes.length, corrections: this._st.corrections, rejectedActions: this._st.rejected,
        extrapolatedShare: this._samples ? this._extrap / this._samples : 0, lastAck: this._ack, bytesIn: this._st.bytesIn, bytesOut: this._st.bytesOut,
      };
    }

    // ---- incoming ----
    _onMessage(data) {
      if (typeof data === 'string') {
        this._st.bytesIn += data.length;
        let m; try { m = JSON.parse(data); } catch (e) { return; }
        if (m && typeof m.t === 'string') this._onJson(m);
        return;
      }
      const d = view(data); if (!d || d.byteLength < 1) return;
      this._st.bytesIn += d.byteLength;
      const type = d.getUint8(0);
      if (type === MSG.SNAP) this._onSnap(data);
      else if (type === MSG.PONG) { const p = decodePong(data); if (p && this._clock.add(p.c, p.s, this._now()) && this._clock.n % 5 === 1) this._emit('latency', this.stats()); }
      else if (type === MSG.SPING) { const t = codec.decodeSPing(data); if (t !== null) this._sendB(codec.encodeSPong(t)); }
    }
    _onSnap(data) {
      const s = decodeSnapshot(data); if (!s) return;
      const local = this._now(), sn = local + this._clock.offset, stamps = [];
      this._snapTimes.push(local); this._st.snapshots++; this._ack = s.ack;
      for (const p of s.players) {
        let tr = this._tracks.get(p.slot); if (!tr) { tr = new RemoteTrack(); this._tracks.set(p.slot, tr); }
        if (tr.push(p) && p.slot !== this.slot) stamps.push(p.t);
      }
      this._interp.onSnapshot(local, sn, stamps);
      this._emit('snapshot', s);
    }
    _onJson(m) {
      if (m.r !== undefined && this._waits.has(m.r)) {
        const w = this._waits.get(m.r); this._waits.delete(m.r);
        if (m.t === 'error') w.reject(Object.assign(new Error(m.message || m.code), { code: m.code })); else w.resolve(m);
      }
      switch (m.t) {
        case 'welcome':
          this.id = m.id; this.token = m.token; this.name = m.name; this.rating = m.rating || null; this._noRetry = false;
          this._emit('welcome', m); if (m.token) this._emit('token', { token: m.token });
          break;
        case 'error':
          if (m.fatal) { this._noRetry = true; this._emit('fatal', m); }
          this._emit('error', m);
          break;
        case 'kicked': this._noRetry = true; this._emit('kicked', m); this._emit('fatal', { code: 'kicked', message: m.reason }); break;
        case 'room': this.room = m; this._emit('room', m); break;
        case 'roomLeft': this.room = null; this._emit('roomLeft', m); break;
        case 'matchFound': case 'resume':
          this.match = { id: m.matchId, mode: m.mode, seed: m.seed, opts: m.opts, players: m.players, layoutHash: null, startAt: m.startAt || null, endAt: m.endAt || null };
          this.slot = m.you; this._tracks.clear(); this._clock.locked = true;
          if (m.cid !== undefined) this._corr = m.cid & 0xff;
          this._emit(m.t, m);
          break;
        case 'start':
          if (this.match && this.match.id === m.matchId) { this.match.startAt = m.startAt; this.match.endAt = m.endAt; }
          if (m.cid !== undefined) this._corr = m.cid & 0xff;
          this._emit('start', m);
          break;
        case 'correction': this._corr = m.cid & 0xff; this._st.corrections++; this._emit('correction', m); break;
        case 'respawn': if (m.slot === this.slot && m.cid !== undefined) this._corr = m.cid & 0xff; this._emit('respawn', m); break;
        case 'ack': {
          const f = this._acts.get(m.n); if (f) { this._acts.delete(m.n); if (!m.ok) this._st.rejected++; f({ ok: !!m.ok, reason: m.reason, a: m.a, data: m.data }); }
          this._emit('actionResult', m);
          break;
        }
        case 'matchEnd': this._clock.locked = false; this._emit('matchEnd', m); break;
        case 'matchCancelled': case 'matchClosed':
          this._emit(m.t, m); this.match = null; this.slot = -1; this._clock.locked = false; this._tracks.clear();
          break;
        default: this._emit(m.t, m);
      }
    }
  }
  RMNet.PROTOCOL_VERSION = PROTOCOL_VERSION; RMNet.MODES = MODES; RMNet.FLAGS = FLAGS;
  RMNet.layoutHash = layoutHash; RMNet.canonicalLayout = canonicalLayout; RMNet.layoutFromStage = layoutFromStage;

  if (typeof window !== 'undefined' && window && !window.RMNet) window.RMNet = RMNet;
  return { RMNet, PROTOCOL_VERSION, MODES, FLAGS, MSG, codec, canonicalLayout, layoutHash, hashString, layoutFromStage, RemoteTrack, ClockSync, InterpDelay };
})();
export const { RMNet, PROTOCOL_VERSION, MODES, FLAGS, MSG, codec, canonicalLayout, layoutHash, hashString, layoutFromStage, RemoteTrack, ClockSync, InterpDelay } = RMNetSDK; export default RMNetSDK.RMNet;
