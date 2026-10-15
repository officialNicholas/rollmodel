// Matchmaking queues (one per mode) and private rooms.
import { MODE_INFO, MODES } from './constants.js';
import { nowMs, roomCode } from './util.js';

// The rating window: how far apart two players' ratings may be to be matched. It starts narrow and widens the longer
// the player waits; after WIDE_AFTER seconds anyone in the same mode will do.
export const MM = Object.freeze({ BASE: 100, GROW: 20, MAX: 600, WIDE_AFTER: 45 });
export const windowFor = waitS => (waitS >= MM.WIDE_AFTER ? Infinity : Math.min(MM.MAX, MM.BASE + MM.GROW * waitS));

export class Matchmaker {
  constructor() { this.q = new Map(MODES.map(m => [m, []])); }
  // at: keep a player's place when they are put back after a cancelled match
  add(sess, mode, at = nowMs()) {
    this.remove(sess);
    const rt = sess.player.ratings[mode];
    const t = { sess, mode, r: rt.r, rd: rt.rd, at };
    this.q.get(mode).push(t); sess.queued = t;
    return t;
  }
  remove(sess) {
    const t = sess.queued; if (!t) return false;
    const list = this.q.get(t.mode), i = list.indexOf(t); if (i >= 0) list.splice(i, 1);
    sess.queued = null; return true;
  }
  sizes() { return Object.fromEntries([...this.q].map(([m, l]) => [m, l.length])); }
  // returns [{ mode, tickets }] ready to start; the tickets are taken out of the queue
  form(now = nowMs()) {
    const out = [];
    for (const [mode, list] of this.q) {
      const need = MODE_INFO[mode].players; if (list.length < need) continue;
      list.sort((a, b) => a.at - b.at);
      const used = new Set();
      for (const A of list) {
        if (used.has(A)) continue;
        const winA = windowFor((now - A.at) / 1000);
        const cands = list.filter(B => B !== A && !used.has(B) && Math.abs(B.r - A.r) <= Math.min(winA, windowFor((now - B.at) / 1000)))
          .sort((x, y) => Math.abs(x.r - A.r) - Math.abs(y.r - A.r));
        if (cands.length < need - 1) continue;
        const group = [A, ...cands.slice(0, need - 1)];
        // everyone must also be within everyone else's window
        const ok = group.every(x => group.every(y => Math.abs(x.r - y.r) <= Math.min(windowFor((now - x.at) / 1000), windowFor((now - y.at) / 1000))));
        if (!ok) continue;
        for (const g of group) used.add(g);
        out.push({ mode, tickets: arrangeSides(mode, group) });
      }
      if (used.size) this.q.set(mode, list.filter(t => !used.has(t)));
      for (const t of used) t.sess.queued = null;
    }
    return out;
  }
}

// slot order for a group. In 2v2 the sides are slots [0,3] against [1,2]: put the best and the worst together.
export function arrangeSides(mode, group) {
  if (mode !== 'duo') return group.slice().sort((a, b) => a.at - b.at);
  const s = group.slice().sort((a, b) => b.r - a.r); // s0 >= s1 >= s2 >= s3
  return [s[0], s[1], s[2], s[3]]; // sides [0,1,1,0]: s0 + s3 against s1 + s2
}

export class Room {
  constructor(mode, host) {
    this.code = null; this.mode = mode; this.need = MODE_INFO[mode].players; this.members = []; this.ready = new Map();
    this.host = host.player.id; this.match = null; this.createdAt = nowMs();
  }
  view() {
    return { t: 'room', code: this.code, mode: this.mode, host: this.host, need: this.need, inMatch: !!this.match,
      players: this.members.map(s => ({ id: s.player.id, name: s.player.name, look: s.player.look, ready: !!this.ready.get(s.player.id) })) };
  }
  allReady() { return this.members.length === this.need && this.members.every(s => this.ready.get(s.player.id)); }
}

export function uniqueCode(taken) { for (let i = 0; i < 50; i++) { const c = roomCode(); if (!taken.has(c)) return c; } throw new Error('no free room code'); }
