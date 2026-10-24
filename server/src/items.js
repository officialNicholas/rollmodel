// Pick-ups, the orb and the special strokes. The server places the pick-ups at the layout's power spots and the orb on its
// own schedule, decides who picks one up (by the validated positions), keeps everyone's pocket, checks each use and tells
// everyone what happened. Each game plays the effects; the hits they land come back as claims ('hit'), which the server
// checks against what it knows (the effect is live, the place is in its reach, the target was there at the attacker's
// view time) and rules on like a pound, waiting a moment for the target's own dodge. The paint they leave comes back as
// claims too ('paint'), held to what each effect can paint. The Flash Freeze needs nobody's aim: the server rules it.
//
// The game's pick-ups: roller (wide stripes, full paint), turret (planted, firing globs), trap (left on the floor; the next
// rival over it is knocked out), whirl (a wind-up, then a charge that knocks out anyone in its path; untouchable while it
// spins), boom (a boomerang out in a loop and back; knocks out anyone it clips). Two the server still knows from before:
// slam (one free pound) and giant. Specials, from the orb (each player's own, the one they equipped): giant, rocket,
// freeze, storm, bomb.
import { G } from './constants.js';
import { rng, randomId, nowMs, clamp, fin } from './util.js';

export const GAME_ITEMS = ['roller', 'turret', 'trap', 'whirl', 'boom'];
export const ITEM_KINDS = [...GAME_ITEMS, 'slam', 'giant'];
export const SPECIALS = ['giant', 'rocket', 'freeze', 'storm', 'bomb', 'heat']; // (heat: game v468, the clients play it out)
const RARE = ['whirl', 'boom'], RARE_SHARE = 0.12, RARE_P = (GAME_ITEMS.length - RARE.length) * RARE_SHARE / (1 - RARE.length * RARE_SHARE);
const CPU_START = ['roller', 'turret', 'trap'];
// the item protocol a game speaks (its look's iv): 2, this one
export const ITEM_PROTOCOL = 2;

// the game's numbers (game/index.html)
export const T = Object.freeze({
  ROLLER: 9, TURRET: 7, GIANT: 6, GIANT_K: 3,
  WHIRL: G.WHIRL_T, WHIRL_BURST: 2.4,
  BOOM_OUT: 0.62, BOOM_LIFE: 3.2, BOOM_BACK: 16.5, BOOM_R: 0.62, BOOM_W: 1.35,
  TURRET_FAR: 19, SHOT_R: 0.2, SHOT_DMG: 0.07, TURRET_STREAK: 3, TURRET_STUN: 1.5, TURRET_GAP: 0.5, TURRET_RATE: 0.12,
  ROCKET_UP: 0.9, ROCKET_HOVER: 4.5, ROCKET_R: G.SLAM_R * G.GIANT_SLAM,
  FREEZE_WIND: 0.9, FREEZE_T: 5, FREEZE_SWEET: 0.12, ICE_TAP_MAX: 1,
  STORM_FORM: 0.6, STORM_T: 5, STORM_FALL: 0.62, STORM_KO: 1.2, STORM_R: 1.7, STORM_AREA: 5.2, STORM_LEAD: 4.4,
  BOMB_FLASH: 0.25, BOMB_GROW: 1.45, BOMB_R: 5.4,
  WHIRL_TRAIL: 1.9,
  ORB_HOLD: 10, ORB_REACH: 2.4,
});
const PICK_R = 0.95, STALE = 15, TRAP_R = 0.92, TRAP_ARM = 0.6, TRAP_LIFE = 45, TRAP_MAX = 2, DROP_GRACE = 2.5;
const DUR = { roller: T.ROLLER, whirl: T.WHIRL, turret: T.TURRET, giant: T.GIANT };
const ROCKET_MAX = T.ROCKET_UP + T.ROCKET_HOVER + 3.5; // up, the longest hover, the slow fall from the top
const STORM_MAX = T.STORM_FORM + T.STORM_T + T.STORM_FALL + 0.6;
const SLACK = 0.7; // metres of give on a claim's distances (the two views of a moving target)
// what a claimed hit does: the reach of each kind (from the attacker, or from the place claimed) and the level it needs
const HIT_KINDS = new Set(['crush', 'squash', 'boom', 'shot', 'storm', 'bomb', 'rocket']);
// what each kind of paint claim stamps, and how much of it an effect may claim
const PAINT = {
  shot: { r: 1.0 }, boom: { r: T.BOOM_W * G.TW / 2 + 0.05 }, whirl: { r: T.WHIRL_TRAIL * 0.9 }, whirlEnd: { r: T.WHIRL_TRAIL * 1.4 },
  storm: { r: T.STORM_R }, rocket: { r: T.ROCKET_R }, bomb: { r: T.BOMB_R },
};
const FX_MAX = 360; // characters of an effect's relayed detail

export class Items {
  constructor(match) {
    const m = this.m = match; this.R = rng((match.seed ^ 0x17e85) >>> 0);
    this.items = new Map(); this.traps = new Map(); this.bag = []; this.last = null;
    this.orb = null; this.freezes = [];
    const [a, b] = m.rules.itemFirst; this.nextAt = m.startAt + (a + this.R() * (b - a)) * 1000;
    const [c, d] = m.rules.orbFirst; this.orbAt = m.startAt + (c + this.R() * (d - c)) * 1000;
    // every match starts with something in the pocket: the one each player picked (a CPU's: one of the first three)
    for (const p of m.P) {
      const L = p.kit || p.look || {};
      p.item = p.bot ? CPU_START[Math.floor(this.R() * CPU_START.length)] : GAME_ITEMS.includes(L.it) ? L.it : null;
      p.special = p.bot ? (this.R() < 0.46 ? ['freeze', 'storm', 'bomb', 'heat'][Math.floor(this.R() * 4)] : ['giant', 'rocket'][Math.floor(this.R() * 2)]) : SPECIALS.includes(L.sp) ? L.sp : 'giant';
      p.pockets = !p.bot && L.sk === 'pockets'; // (Deep Pockets: the orb keeps till it's used)
      p.two = p.pockets && (L.iv || 0) >= 3; p.item2 = null; // (and a second pocket, for a game that knows of it: kit iv 3)
      p.orb = null; p.orbUntil = 0; p.hitsBy = new Map();
    }
  }
  pockets() { return this.m.P.map(p => p.item || null); }
  list() { return [...this.items.values()].map(i => ({ id: i.id, kind: i.kind, x: i.x, y: i.y, z: i.z })); }
  orbNow() { const o = this.orb; return o ? { id: o.id, x: o.x, y: o.y, z: o.z } : null; }
  // (the game's turns: each kind in a turn before any comes again, the whirlwind and the boomerang only in some turns)
  _kind() {
    if (!this.bag.length) {
      const ks = GAME_ITEMS.filter(k => !RARE.includes(k) || this.R() < RARE_P);
      for (let i = ks.length - 1; i > 0; i--) { const j = Math.floor(this.R() * (i + 1)); [ks[i], ks[j]] = [ks[j], ks[i]]; }
      if (ks[0] === this.last) ks.push(ks.shift());
      this.bag.push(...ks);
    }
    return this.last = this.bag.shift();
  }
  tick(now) {
    const m = this.m, alive = m.P.filter(p => p.st === 'play' || p.st === 'hide');
    for (const it of [...this.items.values()]) if (now - it.at > STALE * 1000) this._gone(it, 'stale');
    for (const tr of [...this.traps.values()]) if (now > tr.until) { this.traps.delete(tr.id); m._all({ t: 'itemGone', id: tr.id, why: 'trap_expired' }); }
    for (const p of m.P) if (p.orb && now > p.orbUntil) { p.orb = null; m._all({ t: 'orbLost', slot: p.slot }); }
    for (let i = this.freezes.length - 1; i >= 0; i--) if (now >= this.freezes[i].at) this._flash(this.freezes.splice(i, 1)[0], now);
    this._orbTick(now, alive);
    if (now < this.nextAt || now > m.endAt - 6000) return;
    const busy = m.P.filter(p => p.item || p.item2 || Object.values(p.effects).some(v => typeof v === 'number' && v > now)).length;
    const cap = m.info.players > 2 ? 2 : 1;
    if (this.items.size >= cap || this.items.size + busy >= alive.length) { this.nextAt = now + 1000; return; }
    const sp = this._spot(alive);
    if (!sp) { this.nextAt = now + 2000; return; }
    const kind = sp.kind && ITEM_KINDS.includes(sp.kind) ? sp.kind : this._kind();
    this._spawn(kind, sp.x, sp.y, sp.z, now, -1);
    const [a, b] = m.rules.itemEvery; this.nextAt = now + (a + this.R() * (b - a)) * 1000;
  }
  // a power spot clear of everyone and of what's already out, nearest whoever is behind (with some randomness, like the game)
  _spot(alive, avoid) {
    const m = this.m;
    const spots = m.level.powers.filter(sp => alive.every(p => Math.hypot(p.mover.last.x - sp.x, p.mover.last.z - sp.z) > 5) && ![...this.items.values()].some(o => Math.hypot(o.x - sp.x, o.z - sp.z) < 3) && !(avoid && Math.hypot(avoid.x - sp.x, avoid.z - sp.z) < 3));
    if (!spots.length || !alive.length) return null;
    const cov = m.cov.bySide(); let trail = alive[0];
    for (const p of alive) if ((cov[p.side] || 0) < (cov[trail.side] || 0)) trail = p;
    let best = null, bs = Infinity;
    for (const sp of spots) { const sc = Math.hypot(trail.mover.last.x - sp.x, trail.mover.last.z - sp.z) + this.R() * 9; if (sc < bs) { bs = sc; best = sp; } }
    return best;
  }
  _spawn(kind, x, y, z, now, owner) {
    const it = { id: randomId('i_', 6), kind, x, y, z, at: now, owner, grace: owner >= 0 ? now + DROP_GRACE * 1000 : 0 };
    this.items.set(it.id, it);
    this.m._all({ t: 'itemSpawn', id: it.id, kind, x, y, z, dropped: owner >= 0 ? owner : undefined });
    return it;
  }
  _gone(it, why) { this.items.delete(it.id); this.m._all({ t: 'itemGone', id: it.id, why }); }
  // ---------------------------------------------------------------------------------------------- the orb
  _orbTick(now, alive) {
    const m = this.m;
    if (this.orb || now < this.orbAt || now > m.endAt - 8000) return;
    const sp = this._spot(alive);
    if (!sp) { this.orbAt = now + 2000; return; }
    this.orb = { id: randomId('o_', 6), x: sp.x, y: sp.y, z: sp.z, at: now };
    m._all({ t: 'orbSpawn', id: this.orb.id, x: sp.x, y: sp.y, z: sp.z });
  }
  _takeOrb(p, now) {
    const m = this.m, o = this.orb; this.orb = null;
    const [a, b] = m.rules.orbEvery; this.orbAt = now + (a + this.R() * (b - a)) * 1000;
    const gift = p.special;
    m._all({ t: 'orbTaken', id: o.id, slot: p.slot, gift, keep: p.pockets || undefined, at: p.orb ? 'now' : undefined });
    // one already in the slot: the next goes off at once
    if (p.orb) { this._special(p, gift, now, p.mover.last.yaw); return; }
    p.orb = gift; p.orbUntil = p.pockets ? Infinity : now + T.ORB_HOLD * 1000;
  }
  // ---------------------------------------------------------------------------------------------- moving about
  // called with every validated position of a player in play
  onMove(p, cur) {
    const m = this.m, now = cur.tc, e = p.effects;
    for (const it of this.items.values()) {
      if (it.owner === p.slot && it.grace > now) continue;
      if (Math.abs(cur.y - it.y) < 1.6 && Math.hypot(cur.x - it.x, cur.z - it.z) < PICK_R) {
        this.items.delete(it.id);
        const drop = () => { const bx = cur.x - Math.sin(p.latest.yaw) * 1.1, bz = cur.z - Math.cos(p.latest.yaw) * 1.1, g = m.level.surfaceUnder(bx, bz, cur.y + 0.5); this._spawn(p.item, bx, g > -Infinity ? g : cur.y, bz, now, p.slot); };
        // (as in the game: with Deep Pockets a second one goes in the other pocket, and a third drops the older; else the one held drops)
        if (p.two && p.item) { if (p.item2) { drop(); p.item = p.item2; } p.item2 = it.kind; }
        else { if (p.item) drop(); p.item = it.kind; }
        m._all({ t: 'itemTaken', id: it.id, slot: p.slot, kind: it.kind, h1: p.item, h2: p.two ? p.item2 : undefined });
        break;
      }
    }
    const o = this.orb;
    if (o && now > o.at + 500 && !((e.giant || 0) > now) && !((e.rocket || 0) > now) && !((e.turret || 0) > now)) {
      const dy = o.y - cur.y;
      if (dy > -1.1 && dy < 1.3 && Math.hypot(cur.x - o.x, cur.z - o.z) < T.ORB_REACH + 0.3) this._takeOrb(p, nowMs());
    }
    for (const tr of this.traps.values()) {
      if (tr.side === p.side || now < tr.armAt) continue;
      if (Math.abs(cur.y - tr.y) < 1 && Math.hypot(cur.x - tr.x, cur.z - tr.z) < TRAP_R) {
        this.traps.delete(tr.id);
        const owner = m.P[tr.owner], safe = m._safeAt(p, now) || ((p.effects.giant || 0) > now ? 'giant' : null); // (a giant shrugs it off, as in the game)
        m.cov.stamp(tr.x, tr.y, tr.z, G.SPLAT_R * 1.7, tr.color);
        m._all({ t: 'itemTrap', id: tr.id, slot: p.slot, by: tr.owner, safe: safe || undefined });
        // (the game's trap is a knock-out; a roll through it sets it off harmlessly)
        if (!safe) m._ko(p, owner, 'trap');
        break;
      }
    }
  }
  // ---------------------------------------------------------------------------------------------- using one
  // returns null when the use is allowed, else the reason it is not
  use(p, ts, vt, msg = {}) {
    const m = this.m;
    if (msg.orb) {
      if (!p.orb) return 'no_orb';
      const no = m._canAct(p, ts); if (no) return no;
      const e = p.effects;
      if ((e.giant || 0) > ts || (e.rocket || 0) > ts || (e.turret || 0) > ts) return 'busy';
      const gift = p.orb; p.orb = null;
      this._special(p, gift, ts, fin(msg.yaw) ? msg.yaw : p.mover.last.yaw);
      return null;
    }
    const second = !!msg.second && p.two; // (v432: Deep Pockets' other pocket)
    if (!(second ? p.item2 : p.item)) return 'no_item';
    const no = m._canAct(p, ts); if (no) return no;
    const e = p.effects;
    if ((e.whirl || 0) > ts || (e.giant || 0) > ts || (e.rocket || 0) > ts) return 'busy';
    const kind = second ? p.item2 : p.item, L = p.mover.last;
    if ((kind === 'turret' || kind === 'whirl') && p.mover.airborne) return 'air';
    if (second) p.item2 = null; else p.item = null;
    let trap;
    switch (kind) {
      case 'roller': e.roller = ts + DUR.roller * 1000; p.paint = 1; break;
      case 'whirl': e.whirl = ts + DUR.whirl * 1000; e.whirlAt = ts; e.whirlEnd = 0; p.mover.boost(G.WHIRL_V * 1.1, DUR.whirl * 1000, ts); break;
      case 'turret': { const at = m._histAt(p, ts) || L; e.turret = ts + DUR.turret * 1000; e.turretAt = { x: at.x, z: at.z }; e.shots = 0; p.paint = 1; break; } // (where it was planted, on the planter's own clock)
      case 'giant': e.giant = ts + DUR.giant * 1000; p.paint = 1; break;
      case 'slam': e.slam = true; break;
      case 'boom': e.boom = { at: ts, x: L.x, z: L.z, hit: new Set(), paint: 0 }; break;
      case 'trap': {
        const mine = [...this.traps.values()].filter(t => t.owner === p.slot);
        if (mine.length >= TRAP_MAX) { const old = mine[0]; this.traps.delete(old.id); m._all({ t: 'itemGone', id: old.id, why: 'trap_replaced' }); }
        trap = { id: randomId('t_', 6), owner: p.slot, side: p.side, color: p.color, x: L.x, y: L.y, z: L.z, armAt: ts + TRAP_ARM * 1000, until: ts + TRAP_LIFE * 1000 };
        this.traps.set(trap.id, trap);
        break;
      }
    }
    m._all({ t: 'itemUsed', slot: p.slot, kind, ts, x: L.x, y: L.y, z: L.z, yaw: fin(msg.yaw) ? msg.yaw : L.yaw, curve: msg.curve === 1 || msg.curve === -1 ? msg.curve : undefined, tgt: Number.isInteger(msg.tgt) ? msg.tgt : undefined, until: DUR[kind] ? ts + DUR[kind] * 1000 : undefined, trap: trap ? trap.id : undefined, h1: p.two ? p.item : undefined, h2: p.two ? p.item2 : undefined });
    return null;
  }
  // a special stroke goes off
  _special(p, gift, ts, yaw) {
    const m = this.m, e = p.effects, L = p.mover.last;
    switch (gift) {
      case 'giant': e.giant = ts + T.GIANT * 1000; p.paint = 1; break;
      case 'rocket': e.rocket = ts + ROCKET_MAX * 1000; e.rocketLand = 0; p.paint = 1; p.mover.boost(G.ROCKET_SPD * 1.25, ROCKET_MAX * 1000, ts); break;
      case 'freeze': this.freezes.push({ by: p, at: ts + T.FREEZE_WIND * 1000 }); break;
      case 'storm': e.storm = ts + STORM_MAX * 1000; e.stormAt = ts; e.stormPaint = 0; p.paint = 1; break; // (a full tank while it rains: the game keeps it full)
      case 'bomb': e.bomb = ts; e.bombPaint = 0; break;
    }
    m._all({ t: 'itemUsed', slot: p.slot, kind: gift, orb: 1, ts, x: L.x, y: L.y, z: L.z, yaw, until: gift === 'giant' ? e.giant : undefined });
  }
  // the Flash Freeze: everyone else out in the open is frozen where they stand (a roll right at the flash dodges it; down
  // in a pot, or up in a rocket, they're out of it)
  _flash(F, now) {
    const m = this.m, A = F.by, frozen = [], dodged = [];
    if (A.st !== 'play' && A.st !== 'hide') return;
    for (const B of m.P) {
      if (B === A || B.side === A.side || B.st !== 'play' || (B.effects.rocket || 0) > now) continue;
      // (the roll begun just before the flash, on their own clock; a moment's give either side for the two views of it)
      if (B.rollStart >= F.at - T.FREEZE_SWEET * 1000 - 80 && B.rollStart <= F.at + B.lagEst + 80) { dodged.push(B.slot); continue; }
      B.frozen = { at: F.at, until: F.at + T.FREEZE_T * 1000, from: now + B.lagEst * 2 + 4 * B.jit + 150, anchor: null };
      B.pound = null; frozen.push(B.slot);
    }
    m._all({ t: 'freeze', by: A.slot, at: F.at, until: F.at + T.FREEZE_T * 1000, slots: frozen, dodged });
  }
  // tapped out of the ice early (a second sooner at most)
  thaw(p, ts) {
    const f = p.frozen; if (!f || ts >= f.until) return 'not_frozen';
    f.until = Math.max(Math.min(f.until, ts + 60), f.at + (T.FREEZE_T - T.ICE_TAP_MAX) * 1000 - 100);
    return null;
  }
  // ---------------------------------------------------------------------------------------------- claims
  // a hit an item or a special landed, as the attacker's game saw it: { k, target, x, y, z } (x, y, z: where it struck)
  hit(A, ts, vt, msg, recv) {
    const m = this.m, k = msg.k, B = Number.isInteger(msg.target) ? m.P[msg.target] : null, e = A.effects;
    if (!HIT_KINDS.has(k)) return 'kind';
    if (!B || B === A || B.side === A.side) return 'target';
    if (A.st !== 'play') return 'state';
    if (B.st !== 'play' && !(k === 'rocket' && B.st === 'hide')) return 'target_state';
    const a = m._histAt(A, ts) || A.mover.last;
    const pt = fin(msg.x) && fin(msg.z) ? { x: msg.x, y: fin(msg.y) ? msg.y : a.y, z: msg.z } : { x: a.x, y: a.y, z: a.z };
    const far = (q, r) => Math.hypot(q.x - pt.x, q.z - pt.z) > r;
    let reach, from = pt, lift = Infinity, level = 1.6;
    switch (k) {
      case 'crush': {
        const whirl = (e.whirlAt || -1e12) <= ts + 60 && ts <= (e.whirl || 0) + 400, giant = (e.giant || 0) > ts - 300;
        const roll = ts >= A.rollStart - 60 && ts <= A.rollStart + G.ROLL_T * 1000 + 200, roller = (e.roller || 0) > ts - 300 && roll;
        if (!whirl && !(giant && roll) && !roller) return 'no_effect';
        from = a; reach = whirl ? T.WHIRL_BURST : giant ? G.PR * T.GIANT_K + G.PR : 2 * G.PR; level = 1.6; break;
      }
      case 'squash': if (!((e.giant || 0) > ts - 300)) return 'no_effect'; from = a; reach = G.PR * T.GIANT_K + G.PR; break;
      case 'boom': {
        const b = e.boom; if (!b || ts < b.at || ts > b.at + (T.BOOM_OUT + T.BOOM_LIFE + 0.8) * 1000) return 'no_effect';
        if (b.hit.has(B.slot)) return 'again';
        if (far(b, Math.min(17, (ts - b.at) / 1000 * T.BOOM_BACK + 2))) return 'far';
        reach = T.BOOM_R + G.PR; break;
      }
      case 'shot': {
        if (!e.turretAt || ts > (e.turret || 0) + 1600 || ts < (e.turret || 0) - DUR.turret * 1000) return 'no_effect';
        if (far(e.turretAt, T.TURRET_FAR + 3)) return 'far';
        reach = G.PR + T.SHOT_R; break;
      }
      case 'storm': {
        if (!((e.storm || 0) > ts) || ts < (e.stormAt || 0) + (T.STORM_FORM + T.STORM_FALL) * 1000 - 300) return 'no_effect';
        if (far(a, T.STORM_LEAD + T.STORM_AREA + 5)) return 'far';
        reach = T.STORM_KO + G.PR; level = 1.2; lift = 0.9; break;
      }
      case 'bomb': {
        const at = (e.bomb || -1e12) + (T.BOMB_FLASH + T.BOMB_GROW) * 1000; if (ts < at - 400 || ts > at + 1500) return 'no_effect';
        if (far(a, 2)) return 'far';
        reach = T.BOMB_R + G.PR; level = 2.2; break;
      }
      case 'rocket': {
        if (!((e.rocket || 0) > ts - 300)) return 'no_effect';
        if (e.rocketLand && ts > e.rocketLand + 400) return 'no_effect';
        if (far(a, 2.2)) return 'far';
        if (!e.rocketLand) { e.rocketLand = ts; e.rocket = Math.min(e.rocket, ts + 800); }
        reach = T.ROCKET_R + G.PR; level = 1.4; lift = 0.6; break;
      }
    }
    const vtc = Math.max(clamp(vt, ts - m.rules.lagCompMaxMs, ts), recv - m.rules.maxRewindMs), b = B.track.sample(vtc, 250);
    if (!b) return 'far';
    if (Math.hypot(b.x - from.x, b.z - from.z) > reach + SLACK) return 'far';
    const sup = m.level.supportAt(b.x, b.z, b.y), base = sup > -Infinity ? sup : b.y;
    if (Math.abs(base - from.y) >= level + 0.3) return 'level';
    if (b.y - base > lift) { m._all({ t: 'dodged', slot: B.slot, by: A.slot, how: 'air' }); return 'dodged'; }
    // (one ruling at a time for each attacker, target and kind; a turret's globs each count)
    const key = A.slot + ':' + k, last = B.hitsBy.get(key) || -1e12;
    if (k !== 'shot' && ts - last < 600) return 'again';
    B.hitsBy.set(key, ts);
    if (k === 'boom') e.boom.hit.add(B.slot);
    m.hits.push({ kind: 'item', k, by: A, B, ts, vt: vtc, decideAt: Math.min(recv + m.rules.dodgeWaitMs, Math.max(recv, ts + B.lagEst + 3 * B.jit + 25)) });
    return null;
  }
  // a hit ruled on, the target not having dodged it
  decide(h, now) {
    const m = this.m, A = h.by, B = h.B, k = h.k, giant = (B.effects.giant || 0) > h.ts;
    if (k === 'shot') return this._shot(B, A, h.ts, now);
    if (k === 'squash') return m._flatten(B, A, now);
    if (giant) { if (k === 'boom') return; if (k !== 'crush') return this.unGiant(B, A); }
    m._ko(B, A, k === 'crush' ? 'crush' : k === 'rocket' ? (m._hiddenAt(B, h.ts) ? 'coffin' : 'pound') : k);
  }
  // a turret's glob: the paint tank is the health bar; three in a row stun
  _shot(B, A, ts, now) {
    if ((B.effects.giant || 0) > ts) return;
    if (B.paint <= 0.01) return this.m._ko(B, A, 'shot');
    B.paint = Math.max(0, B.paint - T.SHOT_DMG);
    let stun = false;
    if ((B.stunUntil || 0) + 800 > ts) B.streak = null;
    else {
      const s = B.streak = B.streak && B.streak.by === A.slot && ts - B.streak.t < T.TURRET_GAP * 1000 ? B.streak : { by: A.slot, n: 0, t: 0 };
      s.n++; s.t = ts; if (s.n >= T.TURRET_STREAK) { stun = true; B.streak = null; B.stunUntil = now + T.TURRET_STUN * 1000; }
    }
    B.lastHit = { by: A, t: now }; B.mover.boost(B.mover.groundCap(B.mover.last.x, B.mover.last.y, B.mover.last.z, {}) + 2.6, 400, now);
    this.m._all({ t: 'shot', slot: B.slot, by: A.slot, paint: Math.round(B.paint * 1000) / 1000, stun: stun || undefined });
  }
  // paint an effect left: { k, pts: [[x, y, z], ...] }, each stamped as that kind stamps, while the effect is live and in its reach
  paint(A, ts, msg) {
    const m = this.m, k = msg.k, P = PAINT[k], e = A.effects, pts = Array.isArray(msg.pts) ? msg.pts.slice(0, 12) : [];
    if (!P) return 'kind';
    if (A.st !== 'play') return 'state';
    const L = A.mover.last, el = s => Math.max(0, ts - s) / 1000;
    let ok, budget = 0, near = 4;
    const count = e.paintN || (e.paintN = {});
    switch (k) {
      case 'shot': ok = e.turretAt && ts <= (e.turret || 0) + 1600; if (ok) budget = el((e.turret || 0) - DUR.turret * 1000) / T.TURRET_RATE * 1.3 + 8; near = T.TURRET_FAR + 3; break;
      case 'boom': ok = e.boom && ts <= e.boom.at + (T.BOOM_OUT + T.BOOM_LIFE + 0.8) * 1000; if (ok) budget = el(e.boom.at) * T.BOOM_BACK / 0.24 * 1.3 + 20; near = 17; break;
      case 'whirl': ok = (e.whirlAt || -1e12) <= ts + 60 && ts <= (e.whirl || 0) + 400; if (ok) budget = el(e.whirlAt) * 22 + 6; near = 4; break;
      case 'whirlEnd': ok = (e.whirlAt || -1e12) <= ts + 60 && ts <= (e.whirl || 0) + 400; budget = 1; near = 3; break;
      case 'storm': ok = (e.storm || 0) > ts; if (ok) budget = el(e.stormAt) / 0.2 * 1.6 + 6; near = T.STORM_LEAD + T.STORM_AREA + 5; break;
      case 'rocket': ok = (e.rocket || 0) > ts - 1000; budget = 1; near = 3; break;
      case 'bomb': ok = ts >= (e.bomb || -1e12) && ts <= (e.bomb || -1e12) + (T.BOMB_FLASH + T.BOMB_GROW + 1.5) * 1000; budget = 1; near = 3; break;
    }
    if (!ok) return 'no_effect';
    // (each use of an effect starts its own count)
    const tag = k + ':' + (k === 'shot' ? e.turret : k === 'boom' ? e.boom.at : k === 'whirl' || k === 'whirlEnd' ? e.whirlAt : k === 'storm' ? e.stormAt : k === 'rocket' ? e.rocket : e.bomb);
    if (count.tag !== tag) { count.tag = tag; count.n = 0; }
    const from = k === 'shot' ? e.turretAt : k === 'boom' ? e.boom : L;
    for (const q of pts) {
      if (!Array.isArray(q) || !fin(q[0]) || !fin(q[1]) || !fin(q[2])) continue;
      if (count.n >= budget) return 'budget';
      if (Math.hypot(q[0] - from.x, q[2] - from.z) > near) continue;
      count.n++; m.cov.stamp(q[0], q[1], q[2], P.r, A.color);
    }
    if (k === 'rocket' && !e.rocketLand) { e.rocketLand = ts; e.rocket = Math.min(e.rocket, ts + 800); } // (it came down: whether it hit anyone or not)
    return null;
  }
  // an effect's look, relayed to the other games as it is (where a storm's drops fall, where a turret's head is turned)
  fx(A, msg) {
    if (typeof msg.k !== 'string' || msg.k.length > 16) return 'kind';
    let d; try { d = JSON.stringify(msg.d === undefined ? null : msg.d); } catch (err) { return 'bad'; }
    if (d.length > FX_MAX) return 'big';
    this.m._all({ t: 'fx', slot: A.slot, k: msg.k, d: msg.d }, A);
    return null;
  }
  // a pound on a giant shrinks it instead of knocking it out
  unGiant(B, A) { const now = nowMs(); B.effects.giant = 0; B.immuneUntil = Math.max(B.immuneUntil, now + 800); if (B.mover && B.st === 'play') B.mover.launch(5.6, now); /* (the game pops a shrunk giant up off its feet) */ this.m._all({ t: 'unGiant', slot: B.slot, by: A ? A.slot : -1 }); }
  // knocked out: whatever it was doing stops (its item stays, as in the game); an orb it hadn't used comes out of it where it went
  // down, for anyone to take (gone over an edge: a new one comes up soon instead)
  onKo(p) {
    p.effects = {}; p.frozen = null;
    if (!p.orb) return;
    const m = this.m, now = nowMs(), L = (p.st === 'ko' && p.koPos) || (p.mover && p.mover.last); p.orb = null; p.orbUntil = 0;
    m._all({ t: 'orbLost', slot: p.slot, why: 'ko' });
    if (this.orb || !L) return;
    const g = m.level.supportAt(L.x, L.z, L.y + 0.5);
    if (!(g > -Infinity) || Math.abs(g - L.y) > 3) { this.orbAt = Math.min(this.orbAt, now + 1500); return; }
    this.orb = { id: randomId('o_', 6), x: L.x, y: g, z: L.z, at: now };
    m._all({ t: 'orbSpawn', id: this.orb.id, x: L.x, y: g, z: L.z, dropped: p.slot });
  }
}
