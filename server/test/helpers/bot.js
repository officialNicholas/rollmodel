// A headless player: the RMNet SDK plus a Body that moves like the game, with a simple mind (wander, hop, roll,
// fling, chase, pound a rival who comes close, refill in a pot). Tests can also take the wheel (behavior 'script').
import { performance } from 'node:perf_hooks';
import { RMNet, FLAGS } from '../../client/rmnet.js';
import { Level } from '../../src/geometry.js';
import { G } from '../../src/constants.js';
import { rng } from '../../src/util.js';
import { Body, wrapA } from './body.js';
import { genLayout } from './layouts.js';

let botSeq = 0;
export class Bot {
  // opts: { url, name, WebSocket, behavior: 'wander' | 'chase' | 'still' | 'script', hz, seed, layoutFor(match), tamper(layout),
  //         record (keep a trace of true positions), rematch (vote when the match ends), sendLayout (default true),
  //         layoutDelay (ms: a slow phone building the stage), silentAfterGo (ms after Go before the first state: still landing) }
  constructor(opts = {}) {
    this.o = Object.assign({ behavior: 'wander', hz: 60, record: false, rematch: null, sendLayout: true }, opts);
    this.n = ++botSeq; this.R = rng(opts.seed || this.n * 9973);
    this.net = new RMNet({ url: opts.url, name: opts.name || 'Bot' + this.n, WebSocket: opts.WebSocket, token: opts.token, autoReconnect: opts.autoReconnect !== false, client: opts.client });
    this.body = null; this.level = null; this.layout = null; this.match = null; this.startAt = 0; this.rules = null;
    this.timer = null; this.lastFrame = 0; this.dead = false; this.hidden = -1; this.hideUntil = 0; this.out = false; this.ended = null;
    this.input = { yaw: undefined, speedK: 1 }; this.target = null; this.next = {}; this.pots = []; this.potUp = [];
    this.slamReadyAt = Infinity; this.paint = 1; this.trace = []; this.events = []; this.stats = { corrections: 0, kos: 0, deaths: 0, pounds: 0, rejected: 0, sent: 0 };
    this._wire();
  }
  get slot() { return this.net.slot; }
  async connect() { const w = await this.net.connect(); this.id = w.id; this.token = w.token; return w; }
  close() { this.stop(); this.net.close(); }
  stop() { clearInterval(this.timer); this.timer = null; }
  on(ev, fn) { return this.net.on(ev, fn); }
  // resolves with the first event of that type that passes the filter
  wait(ev, filter = () => true, ms = 20000) {
    return new Promise((resolve, reject) => {
      const t = setTimeout(() => { off(); reject(new Error(this.net.name + ' timed out waiting for ' + ev)); }, ms);
      const off = this.net.on(ev, m => { if (filter(m)) { clearTimeout(t); off(); resolve(m); } });
    });
  }
  _wire() {
    const net = this.net;
    net.on('matchFound', m => this._found(m));
    net.on('resume', m => this._resume(m));
    net.on('start', m => this._start(m));
    net.on('correction', m => { this.stats.corrections++; this.events.push(['correction', m.reason]); if (this.body) this.body.place({ x: m.x, y: m.y, z: m.z, yaw: m.yaw }); });
    net.on('ko', m => { if (m.slot === this.slot) { this.dead = true; this.stats.deaths++; if (m.out) this.out = true; if (this.body) { this.body.slam = null; } } else if (m.by === this.slot) this.stats.kos++; });
    net.on('respawn', m => { if (m.slot !== this.slot || !this.body) return; this.dead = false; this.body.place({ x: m.x, y: m.y, z: m.z, yaw: this.body.yaw }); this.hidden = m.pot; this.hideUntil = performance.now() + 900 + this.R() * 900; });
    net.on('flat', m => { if (m.slot !== this.slot || !this.body) return; this.body.place({ x: m.x, y: m.y, z: m.z, yaw: this.body.yaw }); this.body.flatT = Math.max(0, (m.until - net.serverNow()) / 1000); });
    net.on('push', m => { if (m.slot !== this.slot || !this.body) return; const b = this.body; b.yaw = Math.atan2(m.dx, m.dz); b.spd = m.spd; b.vy = m.vy; b.air = true; b.slam = null; });
    net.on('potEject', m => { if (m.slot !== this.slot || !this.body) return; this._popOut(m.i, G.JUMP_V * 1.15, G.SPEED * 1.2); });
    net.on('pot', m => { this.potUp[m.i] = m.up; if (this.pots[m.i]) this.pots[m.i].occ = m.occ; });
    net.on('matchEnd', m => { this.ended = m; this.stop(); if (this.o.rematch !== null) setTimeout(() => net.rematch(this.o.rematch), 50 + this.R() * 100); });
    net.on('matchCancelled', () => { this.stop(); this.match = null; });
    net.on('matchClosed', () => { this.stop(); this.match = null; });
    net.on('kicked', m => { this.kicked = m.reason; this.stop(); });
  }
  _found(m) {
    this.match = m; this.ended = null; this.dead = false; this.out = false; this.hidden = -1;
    const lay = this.o.layoutFor ? this.o.layoutFor(m) : genLayout(m.seed, m.opts.arena, { players: m.players.length });
    this.layout = this.o.tamper ? this.o.tamper(JSON.parse(JSON.stringify(lay))) : lay;
    this.level = new Level(lay);
    this.pots = lay.pots.map(p => ({ x: p[0], y: p[1], z: p[2], occ: -1 })); this.potUp = lay.pots.map(() => true);
    if (this.o.sendLayout) setTimeout(() => {
      // the SDK refuses to hash a broken layout; a modded client would send it anyway
      try { this.net.sendLayout(this.layout); } catch (e) { this.net._sendJ({ t: 'layout', m: m.matchId, hash: 'broken', layout: this.layout }); }
    }, (this.o.layoutDelay || 0) + 5 + this.R() * 20);
  }
  _resume(m) {
    this.match = m; this.startAt = m.startAt; this.rules = m.rules;
    if (!this.level) { const lay = this.o.layoutFor ? this.o.layoutFor(m) : genLayout(m.seed, m.opts.arena, { players: m.players.length }); this.layout = lay; this.level = new Level(lay); this.pots = lay.pots.map(p => ({ x: p[0], y: p[1], z: p[2], occ: -1 })); }
    if (!this.body) this.body = new Body(this.level, m.self); else this.body.place(m.self);
    this.dead = m.self.st === 'ko' || m.self.st === 'out'; this.hidden = m.self.st === 'hide' ? m.self.pot : -1; this.hideUntil = performance.now() + 500;
    if (m.phase === 'countdown' || m.phase === 'play') this._run();
  }
  _start(m) {
    this.startAt = m.startAt; this.rules = m.rules; this.slamReadyAt = m.startAt + m.rules.slamFirst * 1000;
    const sp = m.spawns.find(s => s.slot === this.slot);
    this.body = new Body(this.level, sp); this.paint = 1;
    this._run();
  }
  _run() { this.stop(); this.lastFrame = performance.now(); this.timer = setInterval(() => this._frame(), 1000 / this.o.hz); }
  _popOut(potIndex, vy, spd) {
    if (this.hidden < 0) return; // already out (our own exit and the server's eject can cross)
    const p = this.pots[potIndex], b = this.body; if (!p || !b) { this.hidden = -1; return; }
    this.hidden = -1; b.place({ x: p.x, y: p.y + G.POT_POP_Y, z: p.z, yaw: b.yaw }); b.air = true; b.vy = vy; b.spd = spd;
  }

  // ------------------------------------------------------------------------------------------------ the frame
  _frame() {
    const now = performance.now(), dt = Math.min(0.1, (now - this.lastFrame) / 1000); this.lastFrame = now;
    const b = this.body; if (!b || this.dead || this.out) return;
    const sNow = this.net.serverNow();
    if (sNow < this.startAt) { this._send(); return; } // the countdown: stay put
    if (this.hidden >= 0) {
      this.paint = Math.min(1, this.paint + G.REGEN * dt);
      if (this.o.behavior !== 'script' && this.o.behavior !== 'still' && now >= this.hideUntil) { this._popOut(this.hidden, G.JUMP_V * 1.05, G.SPEED * 0.8); this.net.action('exitPot'); }
      this._send(); return;
    }
    if (this.o.behavior === 'script') { if (this.o.script) this.o.script(this, dt, sNow); }
    else if (this.o.behavior !== 'still') this._think(dt, sNow);
    else this.input = { speedK: 0 };
    const r = b.step(dt, this.input);
    if (r.slamLanded) {
      const claim = this.o.onLand ? this.o.onLand(this) : null; // tests look at what this player sees at the moment of landing
      this.lastLand = this.net.action('land', claim || { x: b.x, y: b.y, z: b.z });
      this.lastLand.then(res => { if (!res.ok) this.stats.rejected++; });
    }
    if (!b.air && b.spd > 0.5) this.paint = Math.max(0, this.paint - G.DRAIN * dt);
    if (this.o.record) this.trace.push(now, b.x, b.y, b.z);
    if (b.fell) { this.dead = true; return; }
    this._send();
  }
  _send() {
    if (this.o.silentAfterGo && this.net.serverNow() < this.startAt + this.o.silentAfterGo) return;
    const b = this.body; this.stats.sent++;
    let st = b.state({ hidden: this.hidden >= 0, paint: this.paint });
    if (this.o.cheat) st = this.o.cheat(st, this) || st; // tests: a modded client reports something else
    this.net.sendState(st);
  }

  // the mind
  _think(dt, sNow) {
    const b = this.body, L = this.level, A = L.arena, now = performance.now();
    // a rival close by and on our level: pound it when we can
    let near = null, nd = Infinity;
    for (const p of this.net.players()) {
      if (p.slot === this.slot || (this.match && p.side === this.match.players[this.slot].side)) continue;
      const r = this.net.remote(p.slot); if (!r || r.flags & (FLAGS.KO | FLAGS.OUT | FLAGS.HIDE)) continue;
      const d = Math.hypot(r.x - b.x, r.z - b.z); if (d < nd && Math.abs(r.y - b.y) < 0.6) { nd = d; near = r; }
    }
    if (near && nd < 2.6 && !b.air && sNow >= this.slamReadyAt && this.paint >= 0.32 && !(near.flags & FLAGS.IMMUNE)) {
      if (b.pound()) { this.stats.pounds++; this.paint -= Math.min(0.25, this.paint - 0.08); this.slamReadyAt = sNow + this.rules.slamCd * 1000 + 100; this.net.action('pound'); }
      return;
    }
    if (b.slam) return;
    // low on paint: head for a free pot and dive in
    if (this.paint < 0.28) {
      let best = -1, bd = Infinity;
      this.pots.forEach((p, i) => { if (this.potUp[i] === false || (p.occ >= 0 && p.occ !== this.slot)) return; const d = Math.hypot(p.x - b.x, p.z - b.z); if (d < bd) { bd = d; best = i; } });
      if (best >= 0) {
        const p = this.pots[best]; this.target = { x: p.x, z: p.z };
        if (bd < 0.7 && !b.air && Math.abs(p.y - b.y) < 0.5) { this.hidden = best; this.hideUntil = now + 1500 + this.R() * 1200; b.place({ x: p.x, y: p.y, z: p.z, yaw: b.yaw }); this.net.action('enterPot', { pot: best }).then(r => { if (!r.ok && this.hidden === best) { this.hidden = -1; } }); return; }
      }
    }
    // where to go: a wander point, or the nearest rival when chasing
    if (this.o.behavior === 'chase' && near && nd < 14) this.target = { x: near.x, z: near.z };
    if (!this.target || Math.hypot(this.target.x - b.x, this.target.z - b.z) < 2) this.target = this._pickSpot();
    let want = Math.atan2(this.target.x - b.x, this.target.z - b.z);
    // look ahead for walls, holes and the edge, and swerve
    if (!b.air && this._danger(b.x, b.z, b.y, b.yaw)) {
      let best = null;
      for (const off of [0.6, -0.6, 1.2, -1.2, 1.9, -1.9, 2.6, -2.6, Math.PI]) { const yaw = b.yaw + off; if (!this._danger(b.x, b.z, b.y, yaw)) { best = yaw; break; } }
      want = best !== null ? best : b.yaw + Math.PI; this.target = null;
    }
    this.input = { yaw: want, speedK: 1 };
    // now and then: a hop, a roll, a fling
    const roll = (k, lo, hi) => { if (!this.next[k]) this.next[k] = now + (lo + this.R() * (hi - lo)) * 1000; if (now >= this.next[k]) { this.next[k] = 0; return true; } return false; };
    if (!b.air && roll('jump', 2, 5) && !this._danger(b.x, b.z, b.y, b.yaw, 3.2)) { if (b.jump()) this.net.action('jump'); }
    else if (!b.air && roll('roll', 3, 6) && !this._danger(b.x, b.z, b.y, b.yaw, 3)) { if (b.roll()) { this.paint = Math.max(0.001, this.paint - G.ROLL_COST); this.net.action('roll'); } }
    else if (!b.air && this.paint > 0.2 && roll('fling', 5, 9)) { const c = 0.3 + this.R() * 0.5; if (!this._danger(b.x, b.z, b.y, b.yaw, 2 + c * 6)) { if (b.fling(c)) { this.paint = Math.max(0, this.paint - 0.07); this.net.action('fling', { c }); } } }
  }
  _danger(x, z, y, yaw, reach = 1.8) {
    const L = this.level;
    for (const d of [0.7, reach * 0.6, reach]) {
      const px = x + Math.sin(yaw) * d, pz = z + Math.cos(yaw) * d;
      if (Math.abs(px) > L.arena - 1.2 || Math.abs(pz) > L.arena - 1.2) return true;
      if (L.blockedAt(px, pz, y)) return true;
      const g = L.surfaceUnder(px, pz, y + G.STEP); if (g === -Infinity || y - g > 0.5) return true;
    }
    return false;
  }
  _pickSpot() {
    const L = this.level, A = L.arena;
    for (let t = 0; t < 50; t++) { const x = (this.R() * 2 - 1) * (A - 4), z = (this.R() * 2 - 1) * (A - 4); if (L.surfaceUnder(x, z, 0.3) === 0 && !L.blockedAt(x, z, 0)) return { x, z }; }
    return { x: 0, z: 0 };
  }
  // true position at a real time (from the recorded trace)
  truthAt(t) {
    const a = this.trace; const n = a.length / 4; if (!n) return null;
    if (t <= a[0]) return { x: a[1], y: a[2], z: a[3] };
    if (t >= a[(n - 1) * 4]) { const i = (n - 1) * 4; return { x: a[i + 1], y: a[i + 2], z: a[i + 3] }; }
    let lo = 0, hi = n - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (a[m * 4] <= t) lo = m; else hi = m; }
    const i = lo * 4, j = hi * 4, k = (t - a[i]) / (a[j] - a[i]);
    return { x: a[i + 1] + (a[j + 1] - a[i + 1]) * k, y: a[i + 2] + (a[j + 2] - a[i + 2]) * k, z: a[i + 3] + (a[j + 3] - a[i + 3]) * k };
  }
}
