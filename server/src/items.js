// Pick-ups. The server places them at the layout's power spots on its own schedule, decides who picks one up (by the
// validated positions), keeps everyone's pocket, checks each use and tells everyone what happened.
// Effects the referee understands: roller (wide stripes, full paint), whirl (fast and untouchable for a moment),
// turret (planted, full paint), trap (left on the floor, flattens the next rival over it), slam (one free pound),
// giant (big, fast, paints wide; a pound only shrinks it).
import { G } from './constants.js';
import { rng, randomId, nowMs } from './util.js';

export const ITEM_KINDS = ['roller', 'whirl', 'turret', 'trap', 'slam', 'giant'];
const POOL = ['roller', 'roller', 'whirl', 'turret', 'trap', 'slam'];
const PICK_R = 0.95, STALE = 25, TRAP_R = 0.92, TRAP_ARM = 0.6, TRAP_LIFE = 45, TRAP_MAX = 2, DROP_GRACE = 2.5;
const DUR = { roller: 9, whirl: G.WHIRL_T, turret: 7, giant: 6 }; // (giant: 6 s since v401, as in the game)

export class Items {
  constructor(match) {
    this.m = match; this.R = rng((match.seed ^ 0x17e85) >>> 0);
    this.items = new Map(); this.traps = new Map();
    const [a, b] = match.rules.itemFirst; this.nextAt = match.startAt + (a + this.R() * (b - a)) * 1000;
  }
  list() { return [...this.items.values()].map(i => ({ id: i.id, kind: i.kind, x: i.x, y: i.y, z: i.z })); }
  tick(now) {
    const m = this.m, alive = m.P.filter(p => p.st === 'play' || p.st === 'hide');
    for (const it of [...this.items.values()]) if (now - it.at > STALE * 1000) this._gone(it, 'stale');
    for (const tr of [...this.traps.values()]) if (now > tr.until) { this.traps.delete(tr.id); m._all({ t: 'itemGone', id: tr.id, why: 'trap_expired' }); }
    if (now < this.nextAt || now > m.endAt - 6000) return;
    const busy = m.P.filter(p => p.item || Object.values(p.effects).some(v => typeof v === 'number' && v > now)).length;
    const cap = m.info.players > 2 ? 2 : 1;
    if (this.items.size >= cap || this.items.size + busy >= alive.length) { this.nextAt = now + 1000; return; }
    const spots = m.level.powers.filter(sp => alive.every(p => Math.hypot(p.mover.last.x - sp.x, p.mover.last.z - sp.z) > 5) && ![...this.items.values()].some(o => Math.hypot(o.x - sp.x, o.z - sp.z) < 3));
    if (!spots.length) { this.nextAt = now + 2000; return; }
    // nearest to whoever is behind, with some randomness (like the game)
    const cov = m.cov.bySide(); let trail = alive[0];
    for (const p of alive) if ((cov[p.side] || 0) < (cov[trail.side] || 0)) trail = p;
    let best = null, bs = Infinity;
    for (const sp of spots) { const sc = Math.hypot(trail.mover.last.x - sp.x, trail.mover.last.z - sp.z) + this.R() * 9; if (sc < bs) { bs = sc; best = sp; } }
    const kind = best.kind && ITEM_KINDS.includes(best.kind) ? best.kind : POOL[Math.floor(this.R() * POOL.length)];
    this._spawn(kind, best.x, best.y, best.z, now, -1);
    const [a, b] = m.rules.itemEvery; this.nextAt = now + (a + this.R() * (b - a)) * 1000;
  }
  _spawn(kind, x, y, z, now, owner) {
    const it = { id: randomId('i_', 6), kind, x, y, z, at: now, owner, grace: owner >= 0 ? now + DROP_GRACE * 1000 : 0 };
    this.items.set(it.id, it);
    this.m._all({ t: 'itemSpawn', id: it.id, kind, x, y, z, dropped: owner >= 0 ? owner : undefined });
    return it;
  }
  _gone(it, why) { this.items.delete(it.id); this.m._all({ t: 'itemGone', id: it.id, why }); }
  // called with every validated position of a player in play
  onMove(p, cur) {
    const m = this.m, now = cur.tc;
    for (const it of this.items.values()) {
      if (it.owner === p.slot && it.grace > now) continue;
      if (Math.abs(cur.y - it.y) < 1.6 && Math.hypot(cur.x - it.x, cur.z - it.z) < PICK_R) {
        this.items.delete(it.id);
        if (p.item) { const bx = cur.x - Math.sin(p.latest.yaw) * 1.1, bz = cur.z - Math.cos(p.latest.yaw) * 1.1, g = m.level.surfaceUnder(bx, bz, cur.y + 0.5); this._spawn(p.item, bx, g > -Infinity ? g : cur.y, bz, now, p.slot); }
        p.item = it.kind;
        m._all({ t: 'itemTaken', id: it.id, slot: p.slot, kind: it.kind });
        break;
      }
    }
    for (const tr of this.traps.values()) {
      if (tr.side === p.side || now < tr.armAt) continue;
      if (Math.abs(cur.y - tr.y) < 1 && Math.hypot(cur.x - tr.x, cur.z - tr.z) < TRAP_R && !m._safeAt(p, now)) {
        this.traps.delete(tr.id);
        const owner = m.P[tr.owner];
        m.cov.stamp(tr.x, tr.y, tr.z, G.SPLAT_R * 1.7, tr.color);
        m._all({ t: 'itemTrap', id: tr.id, slot: p.slot, by: tr.owner });
        m._flatten(p, owner, nowMs());
        break;
      }
    }
  }
  // returns null when the use is allowed, else the reason it is not
  use(p, ts) {
    const m = this.m;
    if (!p.item) return 'no_item';
    const no = m._canAct(p, ts); if (no) return no;
    const e = p.effects;
    if ((e.whirl || 0) > ts || (e.giant || 0) > ts) return 'busy';
    const kind = p.item, L = p.mover.last;
    if ((kind === 'turret' || kind === 'whirl') && p.mover.airborne) return 'air';
    p.item = null;
    let trap;
    switch (kind) {
      case 'roller': e.roller = ts + DUR.roller * 1000; p.paint = 1; break;
      case 'whirl': e.whirl = ts + DUR.whirl * 1000; p.mover.boost(G.WHIRL_V * 1.1, DUR.whirl * 1000, ts); break;
      case 'turret': e.turret = ts + DUR.turret * 1000; e.turretAt = { x: L.x, z: L.z }; p.paint = 1; break;
      case 'giant': e.giant = ts + DUR.giant * 1000; p.paint = 1; break;
      case 'slam': e.slam = true; break;
      case 'trap': {
        const mine = [...this.traps.values()].filter(t => t.owner === p.slot);
        if (mine.length >= TRAP_MAX) { const old = mine[0]; this.traps.delete(old.id); m._all({ t: 'itemGone', id: old.id, why: 'trap_replaced' }); }
        trap = { id: randomId('t_', 6), owner: p.slot, side: p.side, color: p.color, x: L.x, y: L.y, z: L.z, armAt: ts + TRAP_ARM * 1000, until: ts + TRAP_LIFE * 1000 };
        this.traps.set(trap.id, trap);
        break;
      }
    }
    m._all({ t: 'itemUsed', slot: p.slot, kind, ts, x: L.x, y: L.y, z: L.z, until: DUR[kind] ? ts + DUR[kind] * 1000 : undefined, trap: trap ? trap.id : undefined });
    return null;
  }
  // a pound on a giant shrinks it instead of knocking it out
  unGiant(B, A) { B.effects.giant = 0; B.immuneUntil = Math.max(B.immuneUntil, nowMs() + 800); this.m._all({ t: 'unGiant', slot: B.slot, by: A.slot }); }
  onKo(p) { p.item = null; p.effects = {}; }
}
