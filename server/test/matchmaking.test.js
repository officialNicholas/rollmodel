// The search that widens: near first (the same region, a similar round trip, a close rank, a similar rating), the neighbouring
// regions after 4 s, the whole world after 8 s, anyone at all after 12 s. Parties stay together, and in 2v2 a party of
// two is one team. These run on the matchmaker alone, with made-up players and clocks.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { Matchmaker, makeTicket, regionOf, regionGap, stageFor, near, MM } from '../src/lobby.js';
import { MODE_INFO } from '../src/constants.js';

let n = 0;
const player = (o = {}) => {
  const r = o.r ?? 1500;
  return { player: { id: 'p' + (++n), look: o.lv ? { c: 'red', r: o.lv } : null, ratings: Object.fromEntries(['duel', 'trio', 'ffa', 'duo'].map(m => [m, { r, rd: 80 }])) }, region: o.region ?? '', tzo: o.tzo ?? null, rtt: o.rtt ?? 0, name: o.name };
};
const names = g => g.sessions.map(s => s.name);
// the first moment (in 250 ms steps, as the server runs it) the queue forms a match
function firstMatch(mm, from = 0, to = 20000) { for (let t = from; t <= to; t += 250) { const g = mm.form(t); if (g.length) return { t, g }; } return null; }

test('regions from time zones, and how far apart they are', () => {
  const cases = { 'America/Chicago': 'na', 'America/Los_Angeles': 'na', 'America/Mexico_City': 'na', 'America/Sao_Paulo': 'sa', 'America/Argentina/Buenos_Aires': 'sa', 'America/Bogota': 'sa',
    'Europe/London': 'eu', 'Europe/Istanbul': 'me', 'Asia/Dubai': 'me', 'Asia/Tokyo': 'as', 'Asia/Kolkata': 'as', 'Africa/Lagos': 'af', 'Australia/Sydney': 'oc', 'Pacific/Auckland': 'oc',
    'Atlantic/Reykjavik': 'eu', 'UTC': '', 'Etc/GMT+3': '', '': '', ['x'.repeat(80)]: '' };
  for (const [z, r] of Object.entries(cases)) assert.equal(regionOf(z), r, z);
  assert.equal(regionOf(42), '');
  const g = (a, b) => regionGap({ region: a }, { region: b });
  assert.equal(g('na', 'na'), 0); assert.equal(g('na', 'eu'), 1); assert.equal(g('eu', 'na'), 1); assert.equal(g('na', 'as'), 2); assert.equal(g('eu', 'oc'), 2);
  assert.equal(regionGap({ region: '', tzo: 300 }, { region: '', tzo: 360 }), 0, 'no region: the time zone offsets');
  assert.equal(regionGap({ region: '', tzo: 300 }, { region: '', tzo: -60 }), 1); assert.equal(regionGap({ region: '', tzo: 480 }, { region: '', tzo: -540 }), 2);
  assert.equal(regionGap({ region: '' }, { region: 'as' }), 0, 'nothing known: nothing holds the match back');
});

test('the reach widens with the wait, to anyone after 12 s', () => {
  assert.deepEqual([0, 3.9, 4, 8, 11.9, 12, 60].map(w => stageFor(w).region), [0, 0, 1, 2, 2, 2, 2]);
  assert.deepEqual([0, 4, 8, 12].map(w => stageFor(w).rating), [150, 300, 500, Infinity]);
  assert.equal(MM.STAGES[MM.STAGES.length - 1].at, 12, 'nobody waits more than 12 s for want of a close enough opponent');
  const a = makeTicket([player({ region: 'na', rtt: 40 })], 'duel', 0), b = makeTicket([player({ region: 'eu', rtt: 120 })], 'duel', 0);
  assert.equal(near(a, b, 1000), false); assert.equal(near(a, b, 4000), true, 'neighbours after 4 s (and an 80 ms gap in round trip)');
  const c = makeTicket([player({ region: 'na', rtt: 40 })], 'duel', 5000);
  assert.equal(near(c, b, 5000), true, 'a newcomer meets someone who has waited, at once');
});

test('near first: a player in the same region is matched before one far away, even if the far one waited longer', () => {
  const mm = new Matchmaker();
  mm.add(player({ name: 'tokyo', region: 'as', rtt: 160 }), 'duel', 0);
  mm.add(player({ name: 'chicago', region: 'na', rtt: 20 }), 'duel', 500);
  assert.equal(mm.form(1000).length, 0, 'the other side of the world: not yet');
  mm.add(player({ name: 'dallas', region: 'na', rtt: 30 }), 'duel', 1500);
  const g = mm.form(1750); assert.equal(g.length, 1); assert.deepEqual(names(g[0]).sort(), ['chicago', 'dallas']);
  // left alone, the far one is matched with the next player who comes along once the search is global
  mm.add(player({ name: 'paris', region: 'eu', rtt: 110 }), 'duel', 2000);
  const m = firstMatch(mm, 2000); assert.ok(m.t >= 8000 && m.t <= 8250, 'the whole world at 8 s: ' + m.t); assert.deepEqual(names(m.g[0]).sort(), ['paris', 'tokyo']);
});

test('ratings: close first, wider with time, anyone after 12 s', () => {
  const mm = new Matchmaker();
  mm.add(player({ name: 'a', r: 1500 }), 'duel', 0); mm.add(player({ name: 'far', r: 2400 }), 'duel', 0);
  assert.equal(mm.form(1000).length, 0, 'too far apart at first');
  mm.add(player({ name: 'c', r: 1600 }), 'duel', 1000);
  const g = mm.form(1250); assert.equal(g.length, 1); assert.deepEqual(names(g[0]).sort(), ['a', 'c']);
  mm.add(player({ name: 'd', r: 1500 }), 'duel', 1500);
  const m = firstMatch(mm, 1500); assert.ok(m.t >= 12000 && m.t <= 12250, 'after 12 s anyone will do: ' + m.t);
});

test('ranks: close first (2 apart), further with time, anyone after 12 s; the closest rank is picked', () => {
  assert.deepEqual([0, 4, 8, 12].map(w => stageFor(w).rank), [2, 5, 10, Infinity]);
  const mm = new Matchmaker();
  mm.add(player({ name: 'r5', lv: 5 }), 'duel', 0); mm.add(player({ name: 'r30', lv: 30 }), 'duel', 0);
  assert.equal(mm.form(1000).length, 0, 'rank 5 and rank 30: not at first');
  mm.add(player({ name: 'r9', lv: 9 }), 'duel', 1000); assert.equal(mm.form(1250).length, 0, 'four ranks apart: not yet');
  const g = firstMatch(mm, 1250); assert.ok(g.t >= 4000 && g.t <= 4250, 'within five ranks after 4 s: ' + g.t); assert.deepEqual(names(g.g[0]).sort(), ['r5', 'r9']);
  const m = firstMatch(mm, g.t); assert.equal(m, null, 'rank 30 alone: nobody to play');
  mm.add(player({ name: 'r12', lv: 12 }), 'duel', 6000);
  const w = firstMatch(mm, 6000); assert.ok(w.t >= 12000 && w.t <= 12250, 'rank 30 meets rank 12 once anyone will do: ' + w.t);
  // a choice of rivals: the closer rank first, whoever came first
  const mm2 = new Matchmaker();
  mm2.add(player({ name: 'me', lv: 10 }), 'trio', 0); mm2.add(player({ name: 'far', lv: 12 }), 'trio', 100); mm2.add(player({ name: 'mid', lv: 11 }), 'trio', 200); mm2.add(player({ name: 'near', lv: 10 }), 'trio', 300);
  const t = mm2.form(400); assert.equal(t.length, 1); assert.equal(t[0].sessions.length, 3, 'a 3-way: three players');
  assert.deepEqual(names(t[0]).sort(), ['me', 'mid', 'near'], 'the two closest ranks, though rank 12 came sooner');
  // an older game that doesn't say its rank: its rank holds nothing back
  const mm3 = new Matchmaker(); mm3.add(player({ name: 'old' }), 'duel', 0); mm3.add(player({ name: 'r40', lv: 40 }), 'duel', 0);
  assert.equal(mm3.form(0).length, 1);
});

test('a round trip far from the others waits a little, but not long', () => {
  const mm = new Matchmaker();
  mm.add(player({ name: 'wifi', rtt: 25 }), 'duel', 0); mm.add(player({ name: 'slow', rtt: 160 }), 'duel', 0);
  const m = firstMatch(mm); assert.ok(m.t >= 8000 && m.t <= 8250, 'a 135 ms gap: matched once the search is global (' + m.t + ')');
  mm.add(player({ name: 'x', rtt: 25 }), 'duel', 0); mm.add(player({ name: 'y', rtt: 60 }), 'duel', 0);
  assert.equal(mm.form(0).length, 1, 'a 35 ms gap: at once');
});

test('parties stay together: a Showdown filled around a party, 2v2 with a party as one team', () => {
  const mm = new Matchmaker();
  const p2 = [player({ name: 'pa' }), player({ name: 'pb' })], party = { ticket: null };
  mm.addTicket(makeTicket(p2, 'ffa', 0, party)); mm.add(player({ name: 's1' }), 'ffa', 100);
  assert.equal(party.ticket.size, 2); assert.equal(mm.sizes().ffa, 3);
  assert.equal(mm.form(1000).length, 0, 'three of four');
  mm.add(player({ name: 's2' }), 'ffa', 200);
  const g = mm.form(1000); assert.equal(g.length, 1); assert.equal(g[0].sessions.length, 4);
  assert.deepEqual(names(g[0]).slice(0, 2), ['pa', 'pb'], 'the party together, in its order'); assert.equal(party.ticket, null, 'the party is out of the queue');
  for (const s of p2) assert.equal(s.queued, null);
  // 2v2: a party of two is one team (slots 0 and 3: the same side), against two players on their own
  const tm = new Matchmaker(), q = [player({ name: 'qa' }), player({ name: 'qb' })];
  tm.addTicket(makeTicket(q, 'duo', 0, { ticket: null })); tm.add(player({ name: 'x' }), 'duo', 0);
  assert.equal(tm.form(500).length, 0);
  tm.add(player({ name: 'y' }), 'duo', 0);
  const d = tm.form(500)[0], sides = MODE_INFO.duo.sides;
  assert.equal(sides[d.sessions.findIndex(s => s.name === 'qa')], sides[d.sessions.findIndex(s => s.name === 'qb')], 'the party on one side');
  assert.notEqual(sides[d.sessions.findIndex(s => s.name === 'x')], sides[d.sessions.findIndex(s => s.name === 'qa')]);
  // a party plays a party when one is there
  const pm = new Matchmaker(), A2 = [player({ name: 'a1' }), player({ name: 'a2' })], B2 = [player({ name: 'b1' }), player({ name: 'b2' })];
  pm.addTicket(makeTicket(A2, 'duo', 0, { ticket: null })); pm.add(player({ name: 'solo1' }), 'duo', 10); pm.add(player({ name: 'solo2' }), 'duo', 20); pm.addTicket(makeTicket(B2, 'duo', 30, { ticket: null }));
  const e = pm.form(500)[0]; assert.deepEqual(names(e).sort(), ['a1', 'a2', 'b1', 'b2']);
  // leaving: one member's leaving takes the whole party out
  const lm = new Matchmaker(), L = [player(), player()], lp = { ticket: null }; lm.addTicket(makeTicket(L, 'ffa', 0, lp));
  lm.remove(L[1]); assert.equal(lm.sizes().ffa, 0); assert.equal(L[0].queued, null); assert.equal(lp.ticket, null);
});

test('a Showdown still a player short after 20 s starts with three', () => {
  const mm = new Matchmaker();
  for (const nm of ['a', 'b', 'c']) mm.add(player({ name: nm }), 'ffa', 0);
  const m = firstMatch(mm, 0, 30000); assert.ok(m.t >= MM.SHORT_HANDED * 1000 && m.t <= MM.SHORT_HANDED * 1000 + 250, String(m.t)); assert.equal(m.g[0].sessions.length, 3);
  const d = new Matchmaker(); d.add(player(), 'duo', 0); d.add(player(), 'duo', 0); d.add(player(), 'duo', 0);
  assert.equal(firstMatch(d, 0, 40000), null, '2v2 needs all four');
});
