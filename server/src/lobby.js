// Matchmaking (one queue per mode; a ticket is one player, or a party that plays together) and the private rooms of
// the v306 game (kept for the builds already out there: the game itself now plays with friends through parties).
import { MODE_INFO, MODES } from './constants.js';
import { nowMs, roomCode } from './util.js';
import { DEFAULT_RATING } from './rating.js';

// ---------------------------------------------------------------------------------------------------------------
// Where a player is, roughly. The game reports its time zone (an IANA name such as "America/Chicago", and the
// offset in minutes as Date.getTimezoneOffset gives it); that is enough to tell regions apart. With one server region
// "near" means the same part of the world and a similar round trip to the server; with several server regions each
// region runs its own matchmaker (see docs/multiplayer.md).
// ---------------------------------------------------------------------------------------------------------------
const SOUTH_AMERICA = new Set(['Sao_Paulo', 'Bahia', 'Belem', 'Fortaleza', 'Recife', 'Maceio', 'Manaus', 'Cuiaba', 'Campo_Grande', 'Porto_Velho',
  'Boa_Vista', 'Rio_Branco', 'Eirunepe', 'Araguaina', 'Santarem', 'Noronha', 'Bogota', 'Lima', 'Santiago', 'Punta_Arenas', 'Caracas', 'La_Paz',
  'Asuncion', 'Montevideo', 'Guayaquil', 'Guyana', 'Paramaribo', 'Cayenne', 'Buenos_Aires', 'Cordoba', 'Mendoza']);
const MIDDLE_EAST = new Set(['Dubai', 'Riyadh', 'Qatar', 'Bahrain', 'Kuwait', 'Muscat', 'Tehran', 'Baghdad', 'Jerusalem', 'Tel_Aviv', 'Amman', 'Beirut',
  'Damascus', 'Gaza', 'Hebron', 'Aden', 'Nicosia', 'Famagusta', 'Baku', 'Tbilisi', 'Yerevan', 'Istanbul']);
export const REGIONS = Object.freeze(['na', 'sa', 'eu', 'af', 'me', 'as', 'oc']);
// regions whose players usually reach each other's servers in well under 150 ms
const NEIGHBOURS = new Set(['na-sa', 'na-eu', 'eu-af', 'eu-me', 'me-af', 'me-as', 'as-oc', 'na-oc']);
export function regionOf(zone) {
  if (typeof zone !== 'string' || zone.length > 64) return '';
  const [area, ...rest] = zone.split('/'), city = rest[rest.length - 1] || '';
  if (area === 'America') return rest[0] === 'Argentina' || SOUTH_AMERICA.has(city) ? 'sa' : 'na';
  if (area === 'US' || area === 'Canada') return 'na';
  if (area === 'Brazil' || area === 'Chile') return 'sa';
  if (area === 'Europe') return MIDDLE_EAST.has(city) ? 'me' : 'eu';
  if (area === 'Africa') return 'af';
  if (area === 'Asia') return MIDDLE_EAST.has(city) ? 'me' : 'as';
  if (area === 'Australia' || area === 'Pacific' || area === 'NZ') return 'oc';
  if (area === 'Atlantic') return city === 'Bermuda' ? 'na' : city === 'Cape_Verde' || city === 'St_Helena' ? 'af' : 'eu';
  if (area === 'Indian') return city === 'Maldives' || city === 'Chagos' ? 'as' : 'af';
  return '';
}
// how far apart two players are: 0 the same region, 1 neighbouring regions, 2 the other side of the world. Without a
// region, the time zone offsets say it roughly; with nothing at all, nothing holds the match back.
export function regionGap(a, b) {
  if (a.region && b.region) return a.region === b.region ? 0 : NEIGHBOURS.has(a.region + '-' + b.region) || NEIGHBOURS.has(b.region + '-' + a.region) ? 1 : 2;
  if (Number.isFinite(a.tzo) && Number.isFinite(b.tzo)) { const h = Math.abs(a.tzo - b.tzo) / 60; return h <= 3 ? 0 : h <= 7 ? 1 : 2; }
  return 0;
}

// ---------------------------------------------------------------------------------------------------------------
// How the search widens. A ticket reaches further the longer it has waited (two tickets fit together when they are
// within the reach of the one that has waited longer, so a newcomer is matched at once with someone who has been
// waiting). It starts near (the same region, a similar round trip, a close rank and a similar rating), takes in the
// neighbouring regions and ranks further off after 4 s, the whole world after 8 s, and anyone at all after 12 s.
// Nobody waits long for a game. (The rank is the player's level, the one the game shows: its look's r.)
// ---------------------------------------------------------------------------------------------------------------
export const MM = Object.freeze({
  STAGES: Object.freeze([
    Object.freeze({ at: 0, region: 0, rtt: 50, rating: 150, rank: 2 }),
    Object.freeze({ at: 4, region: 1, rtt: 100, rating: 300, rank: 5 }),
    Object.freeze({ at: 8, region: 2, rtt: 200, rating: 500, rank: 10 }),
    Object.freeze({ at: 12, region: 2, rtt: Infinity, rating: Infinity, rank: Infinity }),
  ]),
  SHORT_HANDED: 20, // seconds: a Showdown still a player short after this starts with three
});
export const stageFor = waitS => { let s = MM.STAGES[0]; for (const t of MM.STAGES) if (waitS >= t.at) s = t; return s; };
export const windowFor = waitS => stageFor(waitS).rating; // (the rating part of the reach)

const waitOf = (t, now) => Math.max(0, now - t.at) / 1000;
// two tickets in reach of each other
export function near(A, B, now = nowMs()) {
  const s = stageFor(Math.max(waitOf(A, now), waitOf(B, now)));
  if (regionGap(A, B) > s.region) return false;
  if (A.rtt > 0 && B.rtt > 0 && Math.abs(A.rtt - B.rtt) > s.rtt) return false;
  if (A.lv && B.lv && Math.abs(A.lv - B.lv) > s.rank) return false;
  return Math.abs(A.r - B.r) <= s.rating;
}
// the better of two possible opponents: nearer first, then the closer rank, round trip and rating (a rank apart weighs
// as much as 25 ms, or 50 rating points)
const lvGap = (A, B) => (A.lv && B.lv ? Math.abs(A.lv - B.lv) : 0);
const cost = (A, B) => regionGap(A, B) * 400 + lvGap(A, B) * 25 + (A.rtt > 0 && B.rtt > 0 ? Math.abs(A.rtt - B.rtt) : 0) + Math.abs(A.r - B.r) * 0.5;
// a player's rank, as their game shows it (their look's r); 0 when it doesn't say (an older game)
export const rankOf = sess => { const r = sess && sess.player && sess.player.look && sess.player.look.r; return Number.isFinite(r) && r >= 1 ? Math.min(999, Math.floor(r)) : 0; };
const fitsAll = (group, B, now) => group.every(A => near(A, B, now));

let ticketSeq = 0;
// a ticket: one player, or a party (it stays together: the same match, and in 2v2 the same team)
export function makeTicket(sessions, mode, at = nowMs(), party = null) {
  const rt = sessions.map(s => (s.player && s.player.ratings && s.player.ratings[mode]) || DEFAULT_RATING);
  const first = sessions[0], rtts = sessions.map(s => s.rtt || 0), lvs = sessions.map(rankOf).filter(x => x > 0);
  return {
    id: ++ticketSeq, mode, sessions, sess: first, party, size: sessions.length, at, pids: sessions.map(s => s.player && s.player.id),
    r: rt.reduce((a, x) => a + x.r, 0) / rt.length, rd: rt.reduce((a, x) => a + x.rd, 0) / rt.length,
    region: first.region || '', tzo: Number.isFinite(first.tzo) ? first.tzo : null, rtt: Math.max(0, ...rtts),
    lv: lvs.length ? lvs.reduce((a, x) => a + x, 0) / lvs.length : 0, // (a party: its average rank)
  };
}

export class Matchmaker {
  constructor() { this.q = new Map(MODES.map(m => [m, []])); }
  // one player (at: keep a player's place when they are put back after a cancelled match)
  add(sess, mode, at = nowMs()) { return this.addTicket(makeTicket([sess], mode, at)); }
  addTicket(t) {
    for (const s of t.sessions) this.remove(s);
    this.q.get(t.mode).push(t); for (const s of t.sessions) s.queued = t;
    if (t.party) t.party.ticket = t;
    return t;
  }
  // takes the session's whole ticket out of the queue (a party leaves together); returns the ticket
  remove(sess) { const t = sess && sess.queued; if (!t) return null; this.drop(t); return t; }
  drop(t) {
    const list = this.q.get(t.mode), i = list ? list.indexOf(t) : -1; if (i >= 0) list.splice(i, 1);
    for (const s of t.sessions) if (s.queued === t) s.queued = null;
    if (t.party && t.party.ticket === t) t.party.ticket = null;
  }
  sizes() { return Object.fromEntries([...this.q].map(([m, l]) => [m, l.reduce((n, t) => n + t.size, 0)])); }
  // returns [{ mode, tickets, sessions }] ready to start (sessions in slot order); those tickets leave the queue
  form(now = nowMs()) {
    const out = [];
    for (const [mode, list] of this.q) {
      if (!list.length) continue;
      const need = MODE_INFO[mode].players;
      if (list.reduce((n, t) => n + t.size, 0) < Math.min(need, 3)) continue;
      list.sort((a, b) => a.at - b.at);
      const used = new Set();
      for (const A of list) {
        if (used.has(A)) continue;
        const pool = list.filter(B => B !== A && !used.has(B) && near(A, B, now)).sort((x, y) => cost(A, x) - cost(A, y));
        const g = mode === 'duo' ? teamUp(A, pool, now) : fill(mode, A, pool, need, now);
        if (!g) continue;
        for (const t of g.tickets) used.add(t);
        out.push({ mode, tickets: g.tickets, sessions: g.sessions });
      }
      if (used.size) { this.q.set(mode, list.filter(t => !used.has(t))); for (const t of used) for (const s of t.sessions) if (s.queued === t) s.queued = null; }
      for (const t of used) if (t.party && t.party.ticket === t) t.party.ticket = null;
    }
    return out;
  }
}

// everyone for itself (duel, trio, Showdown): tickets that add up to the players the mode needs, all in reach of each
// other. A Showdown that has waited long enough starts with three.
function fill(mode, A, pool, need, now) {
  const group = [A]; let n = A.size;
  for (const B of pool) { if (n === need) break; if (n + B.size <= need && fitsAll(group, B, now)) { group.push(B); n += B.size; } }
  const short = mode === 'ffa' && n === need - 1 && n >= 3 && waitOf(A, now) >= MM.SHORT_HANDED;
  if (n !== need && !short) return null;
  const tickets = group.slice().sort((a, b) => a.at - b.at);
  return { tickets, sessions: tickets.flatMap(t => t.sessions) };
}

// 2v2: two teams of two, each a party of two or two players on their own. A party plays a party when it can. The game's
// 2v2 sides are slots [0,3] against [1,2].
function teamUp(A, pool, now) {
  if (A.size > 2) return null;
  const T1 = A.size === 2 ? [A] : null, mate = T1 ? null : pool.find(B => B.size === 1);
  const one = T1 || (mate ? [A, mate] : null); if (!one) return null;
  const rest = pool.filter(B => !one.includes(B) && B.size <= 2 && fitsAll(one, B, now));
  const pair = rest.find(B => B.size === 2), solos = rest.filter(B => B.size === 1);
  let two = null;
  if (one.length === 1 && pair) two = [pair];
  else { for (const B of solos) { const C = solos.find(x => x !== B && near(B, x, now)); if (C) { two = [B, C]; break; } } if (!two && pair) two = [pair]; }
  if (!two) return null;
  const tickets = [...one, ...two], ses = t => t.flatMap(x => x.sessions);
  // four players on their own: the best and the worst against the two in the middle (arrangeSides); otherwise each team as it is
  if (tickets.every(t => t.size === 1)) { const s = arrangeSides('duo', tickets); return { tickets, sessions: s.map(t => t.sess) }; }
  const a = ses(one), b = ses(two);
  return { tickets, sessions: [a[0], b[0], b[1], a[1]] };
}

// slot order for a group of players on their own. In 2v2 the sides are slots [0,3] against [1,2]: the best and the
// worst together.
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
      players: this.members.map(s => ({ id: s.roomPid, name: s.roomName, look: s.roomLook, ready: !!this.ready.get(s.roomPid), away: !!s.closed || undefined })) };
  }
  allReady() { return this.members.length === this.need && this.members.every(s => !s.closed && this.ready.get(s.roomPid)); }
}

export function uniqueCode(taken, len = 5) { for (let i = 0; i < 50; i++) { const c = roomCode(len); if (!taken.has(c)) return c; } throw new Error('no free code'); }
