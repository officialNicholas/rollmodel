// Parties: up to four friends in one lobby who play together. The game server keeps them: who is in it, who leads, each
// member's look, ready flag and mode vote (the leader's is the party's pick), the invites still waiting for an answer, and the party's place in the
// matchmaking queue. Invites themselves are made in the game's Supabase project (only friends can invite each other,
// and blocks are honoured there); the game server only passes the word along live and lets the invited player in.
import { nowMs, randomId, roomCode } from './util.js';

export const PARTY = Object.freeze({
  MAX: 4,
  // the modes a party can play, in the order the game shows them: 1v1, 3-way (v394), Showdown (everyone for themselves), 2v2
  MODES: Object.freeze(['duel', 'trio', 'ffa', 'duo']),
  // the reactions (the game draws them; the server only lets these through)
  EMOTES: Object.freeze(['wave', 'laugh', 'wow', 'love', 'cool', 'cry', 'angry', 'gg']),
  // what a member can be busy with in their own game (it un-readies them, and the others see it)
  BUSY: Object.freeze(['locker', 'shop', 'strokes', 'settings', 'cpu', 'menu']),
  CODE_LEN: 8, // the join code: never typed, it travels inside an invite (31^8 codes, and wrong ones are rate limited)
  INVITE_S: 120, // an invite runs out after this long (the database's own expiry is the same)
  MAX_INVITES: 8, // waiting at once
  START_MS: 1500, // everyone ready: this long to back out before the match (or the search) starts
});

// how a party of n plays a mode: 'private' (just the party: two in a duel, three in a 3-way, four in a Showdown or a
// 2v2), 'queue' (matchmaking finds the rest: a party keeps together, and in 2v2 a party of two is a team) or null (not
// for that size)
export function planFor(mode, n) {
  if (mode === 'duel') return n === 1 ? 'queue' : n === 2 ? 'private' : null;
  if (mode === 'trio') return n === 1 || n === 2 ? 'queue' : n === 3 ? 'private' : null;
  if (mode === 'ffa') return n >= 1 && n <= 3 ? 'queue' : n === 4 ? 'private' : null;
  if (mode === 'duo') return n === 1 || n === 2 ? 'queue' : n === 4 ? 'private' : null;
  return null;
}

// a game that plays the 3-way online in a party: it says so in its hello (client 'rm-394' or later)
export function playsTrio(sess) { const v = /^rm-(\d{1,6})$/.exec(String((sess && sess.client) || '')); return !!v && +v[1] >= 394; }

export const newPartyCode = taken => { for (let i = 0; i < 50; i++) { const c = roomCode(PARTY.CODE_LEN); if (!taken.has(c)) return c; } throw new Error('no free party code'); };

export class Party {
  constructor(code) {
    this.id = randomId('pt_', 10); this.code = code; this.leader = null; this.members = []; this.invites = []; this.kicked = new Set();
    // idle (in the lobby), starting (everyone ready: a moment to back out), queued (matchmaking) or match (playing)
    this.state = 'idle'; this.startAt = 0; this.ticket = null; this.match = null; this.queuedAt = 0; this.createdAt = nowMs(); this.note = null;
  }
  get size() { return this.members.length; }
  member(pid) { return this.members.find(m => m.id === pid) || null; }
  add(sess) {
    const pl = sess.player, m = { id: pl.id, sess, sb: sess.sb || null, name: pl.name, look: pl.look, ready: false, vote: null, busy: null, away: false, at: nowMs(), trio: playsTrio(sess) };
    this.members.push(m); if (!this.leader) this.leader = m.id;
    return m;
  }
  // leaves (or is removed); the lead passes to whoever has been in the party longest
  remove(pid) {
    const i = this.members.findIndex(m => m.id === pid); if (i < 0) return null;
    const [m] = this.members.splice(i, 1);
    if (this.leader === pid) this.leader = this.members.length ? this.members.slice().sort((a, b) => a.at - b.at)[0].id : null;
    return m;
  }
  // the modes this party can play now, each with how: [{ mode, plan }] (on: the modes switched on for parties). A 3-way
  // only when every member's game plays one online (v394 and later): an earlier game in the party doesn't see it
  modes(on) {
    const trio = this.members.every(m => m.trio);
    return PARTY.MODES.map(mode => ({ mode, plan: planFor(mode, this.size), on: on.includes(mode) })).filter(x => x.plan && (x.mode !== 'trio' || trio));
  }
  // the mode the party plays: the leader's pick (v392: the leader picks the event, the others ready up and wait for it); with no
  // pick from the leader, the most votes among the modes it can play (a party with an earlier game in it), and nobody voted, the first
  mode(on) {
    const ok = this.modes(on).filter(x => x.on).map(x => x.mode); if (!ok.length) return null;
    const lead = this.member(this.leader); if (lead && ok.includes(lead.vote)) return lead.vote;
    const n = new Map(ok.map(m => [m, 0])); for (const m of this.members) if (n.has(m.vote)) n.set(m.vote, n.get(m.vote) + 1);
    const top = Math.max(...n.values()); return ok.find(m => n.get(m) === top);
  }
  allReady() { return this.members.length > 0 && this.members.every(m => m.ready && !m.away && !m.busy); }
  unready() { let any = false; for (const m of this.members) if (m.ready) { m.ready = false; any = true; } return any; }
  // invites still waiting (they run out after PARTY.INVITE_S)
  liveInvites(now = nowMs()) { this.invites = this.invites.filter(i => i.exp > now); return this.invites; }
  view(on, now = nowMs()) {
    return {
      t: 'party', id: this.id, code: this.code, leader: this.leader, max: PARTY.MAX, state: this.state,
      startAt: this.state === 'starting' ? Math.round(this.startAt) : undefined, queuedAt: this.state === 'queued' ? Math.round(this.queuedAt) : undefined,
      mode: this.mode(on), modes: this.modes(on),
      members: this.members.map(m => ({ id: m.id, sb: m.sb || undefined, name: m.name, look: m.look, ready: m.ready, vote: m.vote || null, busy: m.busy || undefined, away: m.away || undefined })),
      invites: this.liveInvites(now).map(i => ({ to: i.to, name: i.name, look: i.look, by: i.by, left: Math.max(0, Math.round(i.exp - now)) })),
    };
  }
}
