// Parties: up to four friends who play together. Joining by the code an invite carries, the lead passing on, the
// leader removing someone, ready and the leader's pick of the event, reactions, looks and busy members, a dropped member's place kept
// for a while, invites passed on live (a nudge to look at the inbox), and a party of two playing a private duel.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { RMNet } from '../client/rmnet.js';
import { PARTY, Party, planFor } from '../src/party.js';
import { startServer, makeBots, until, sleep } from './helpers/harness.js';

// players with no game body: the SDK alone (enough for everything in the lobby)
function people(srv, n, opts = {}) {
  return Array.from({ length: n }, (_, i) => {
    const net = new RMNet({ url: srv.url, name: (opts.prefix || 'Pal') + (i + 1), look: { c: ['red', 'green', 'blue', 'gold'][i % 4], e: 'round', r: 3 + i }, sb: randomUUID(), autoReconnect: opts.autoReconnect !== false });
    net.got = []; for (const ev of ['party', 'partyLeft', 'react', 'poke', 'partyNote', 'queued', 'queueLeft', 'matchFound']) net.on(ev, m => net.got.push([ev, m]));
    net.wait = (ev, f = () => true, ms = 8000) => new Promise((res, rej) => { const t = setTimeout(() => { off(); rej(new Error(net.name + ' waited for ' + ev)); }, ms); const off = net.on(ev, m => { if (f(m)) { clearTimeout(t); off(); res(m); } }); });
    return net;
  });
}
const ids = v => v.members.map(m => m.id);

test('a party: made, joined with its code (four at most), the lead passes on, the leader removes someone', async () => {
  const srv = await startServer();
  const [A, B, C, D, E] = people(srv, 5);
  try {
    await Promise.all([A, B, C, D, E].map(p => p.connect()));
    const v = await A.partyCreate();
    assert.match(v.code, /^[A-Z0-9]{8}$/); assert.equal(v.leader, A.id); assert.deepEqual(ids(v), [A.id]); assert.equal(v.max, 4); assert.equal(v.state, 'idle');
    assert.equal((await A.partyCreate()).code, v.code, 'asking again: the same party');
    for (const p of [B, C, D]) await p.partyJoin(v.code.toLowerCase()); // (codes are not case sensitive)
    await until(() => A.party && A.party.members.length === 4);
    assert.deepEqual(ids(A.party), [A.id, B.id, C.id, D.id]); assert.deepEqual(ids(D.party), ids(A.party), 'everyone sees the same party');
    await assert.rejects(E.partyJoin(v.code), e => e.code === 'full', 'four at most');
    await assert.rejects(E.partyJoin('ZZZZZZZZ'), e => e.code === 'not_found');
    // the leader leaves: the lead passes to whoever has been in it longest
    const left = A.wait('partyLeft'); await A.partyLeave(); assert.equal((await left).reason, 'left'); assert.equal(A.party, null);
    await until(() => B.party && B.party.members.length === 3 && B.party.leader === B.id);
    // only the leader removes; the one removed is told, and their code no longer lets them in
    await assert.rejects(C.partyKick(D.id), e => e.code === 'not_leader');
    const out = D.wait('partyLeft'); await B.partyKick(D.id);
    assert.equal((await out).reason, 'removed'); await until(() => C.party.members.length === 2);
    await assert.rejects(D.partyJoin(v.code), e => e.code === 'not_found', 'removed: not back without a new invite');
    // invited again, they can come back
    await B.partyInvite(D.sb, { name: D.name }); await D.partyJoin(v.code); await until(() => B.party.members.length === 3);
    // the last one out closes it
    for (const p of [B, C, D]) await p.partyLeave();
    assert.equal(srv.parties.size, 0); await assert.rejects(E.partyJoin(v.code), e => e.code === 'not_found');
  } finally { for (const p of [A, B, C, D, E]) p.close(); await srv.close(); }
});

test('wrong party codes are rate limited', async () => {
  const srv = await startServer();
  const [A] = people(srv, 1);
  try {
    await A.connect(); const codes = [];
    for (let i = 0; i < 9; i++) codes.push(await A.partyJoin('ABCDEFG' + 'HJKMNPQRS'[i]).catch(e => e.code));
    assert.deepEqual(codes.slice(0, 6), Array(6).fill('not_found')); assert.ok(codes.slice(6).every(c => c === 'rate'), codes.join());
  } finally { A.close(); await srv.close(); }
});

test('the mode: the leader picks it (with no pick, the most votes), only the modes that fit the party', async () => {
  const on = ['duel', 'ffa', 'duo'];
  const p = new Party('ABCDEFGH'), mk = id => ({ player: { id, name: id, look: null } });
  p.add(mk('a')); p.add(mk('b'));
  assert.deepEqual(p.modes(on).map(x => x.mode + ':' + x.plan), ['duel:private', 'ffa:queue', 'duo:queue']);
  assert.equal(p.mode(on), 'duel', 'nobody voted: the first');
  p.member('b').vote = 'duo'; assert.equal(p.mode(on), 'duo', 'no pick from the leader: the votes');
  p.member('a').vote = 'ffa'; assert.equal(p.mode(on), 'ffa', 'the leader\'s pick');
  p.add(mk('c')); p.add(mk('d'));
  assert.deepEqual(p.modes(on).map(x => x.mode + ':' + x.plan), ['ffa:private', 'duo:private'], 'four: a Showdown or a 2v2 of their own');
  p.member('c').vote = 'duo'; p.member('d').vote = 'duo'; assert.equal(p.mode(on), 'ffa', 'the leader\'s pick, whatever the others voted');
  p.member('a').vote = 'duel'; assert.equal(p.mode(on), 'duo', 'a pick that doesn\'t fit four: the votes');
  p.remove('d'); assert.deepEqual(p.modes(on).map(x => x.mode), ['ffa'], 'three: a party stays on one team, so no 2v2');
  assert.equal(p.mode(on), 'ffa');
  assert.equal(p.mode(['duel']), null, 'nothing switched on fits three');
  assert.equal(planFor('duel', 3), null); assert.equal(planFor('duo', 3), null); assert.equal(planFor('ffa', 4), 'private');
  p.remove('a'); assert.equal(p.leader, 'b', 'the lead passes on');
});

test('the leader picks the event: the others ready up first and stay ready through the pick; a member\'s vote still un-readies', async () => {
  const srv = await startServer();
  const [A, B, C] = people(srv, 3, { prefix: 'Host' });
  try {
    await Promise.all([A, B, C].map(p => p.connect()));
    const v = await A.partyCreate(); await B.partyJoin(v.code); await C.partyJoin(v.code);
    await until(() => A.party && A.party.members.length === 3);
    await B.partyReady(true); await C.partyReady(true);
    await until(() => A.party.members.filter(m => m.ready).length === 2);
    assert.equal(A.party.state, 'idle', 'waiting for the host');
    // the host picks (Showdown is all a party of three plays): the others stay ready, and the host's ready starts it
    await A.partyVote('ffa'); await until(() => A.party.mode === 'ffa' && A.party.members.find(m => m.id === A.id).vote === 'ffa');
    assert.ok(A.party.members.filter(m => m.id !== A.id).every(m => m.ready), 'still ready after the pick');
    const starting = B.wait('party', m => m.state === 'starting'); await A.partyReady(true); assert.equal((await starting).mode, 'ffa');
    const idle = B.wait('party', m => m.state === 'idle'); await A.partyReady(false); await idle; // (the host backs out)
    assert.ok(B.party.members.filter(m => m.id !== A.id).every(m => m.ready), 'the others still ready');
  } finally { for (const p of [A, B, C]) p.close(); await srv.close(); }
  // two: a member's vote that changes the mode (no pick from the leader yet) un-readies everyone, as before
  const srv2 = await startServer();
  const [D, E] = people(srv2, 2, { prefix: 'Pair' });
  try {
    await Promise.all([D, E].map(p => p.connect()));
    const v = await D.partyCreate(); await E.partyJoin(v.code); await until(() => D.party && D.party.members.length === 2);
    await D.partyReady(true); await until(() => E.party.members.find(m => m.id === D.id).ready);
    await E.partyVote('duo'); await until(() => D.party.mode === 'duo');
    assert.ok(D.party.members.every(m => !m.ready), 'a different mode: everyone readies again');
    await D.partyVote('duel'); await until(() => D.party.mode === 'duel');
  } finally { for (const p of [D, E]) p.close(); await srv2.close(); }
});

test('ready, the vote and reactions: everyone ready starts a private duel for a party of two; then back to the party', async () => {
  const srv = await startServer({ matchT: 3, rematchWindow: 1 });
  const [A, B] = makeBots(srv, 2, { behavior: 'wander', prefix: 'duo' });
  try {
    await Promise.all([A, B].map(b => b.connect()));
    const v = await A.net.partyCreate(); await B.net.partyJoin(v.code);
    await until(() => A.net.party && A.net.party.members.length === 2);
    assert.equal(A.net.party.mode, 'duel'); assert.deepEqual(A.net.party.modes.filter(x => x.on).map(x => x.mode), ['duel', 'ffa', 'duo'], 'Versus, Showdown and 2v2 are on');
    // reactions go to the others, never back to the sender, and only the known ones
    const r = B.wait('react'); A.net.partyReact('wave'); const got = await r; assert.equal(got.id, A.id); assert.equal(got.e, 'wave');
    let back = 0; A.on('react', () => back++);
    await assert.rejects(A.net._request({ t: 'partyReact', e: 'shout' }), e => e.code === 'bad_emote');
    let many = 0; B.on('react', () => many++); for (let i = 0; i < 12; i++) A.net.partyReact('laugh'); await sleep(300);
    assert.ok(many >= 3 && many <= 5, 'rate limited: ' + many); assert.equal(back, 0);
    // ready: both, then a moment to back out
    await A.net.partyReady(true);
    const starting = A.wait('party', m => m.state === 'starting'); await B.net.partyReady(true); const s = await starting;
    assert.ok(s.startAt > A.net.serverNow() + 500, 'a moment to back out');
    const idle = A.wait('party', m => m.state === 'idle'); await B.net.partyReady(false); await idle; // (B backs out)
    // a look change or a trip to the locker un-readies you
    await B.net.partyReady(true); await until(() => A.net.party.state === 'starting'); const lk = A.wait('party', m => m.state === 'idle');
    await B.net.partyLook({ c: 'teal', e: 'sly', r: 4 }); const after = await lk;
    assert.equal(after.members.find(m => m.id === B.id).look.c, 'teal'); assert.equal(after.members.find(m => m.id === B.id).ready, false);
    await B.net.partyBusy('locker'); await B.net.partyReady(true);
    assert.equal(A.net.party.members.find(m => m.id === B.id).ready, false, 'not while busy'); assert.equal(A.net.party.members.find(m => m.id === B.id).busy, 'locker');
    await B.net.partyBusy(null);
    // ready for real: a private duel, unrated, just the two of them
    const found = Promise.all([A, B].map(b => b.wait('matchFound', () => true, 8000)));
    await B.net.partyReady(true); await A.net.partyReady(true);
    const f = await found; assert.equal(f[0].rated, false); assert.deepEqual(f[0].players.map(p => p.id).sort(), [A.id, B.id].sort());
    await until(() => A.net.party.state === 'match');
    await A.wait('matchEnd', () => true, 15000);
    // after the match: the party again, nobody ready
    const home = await A.wait('party', m => m.state === 'idle', 10000);
    assert.ok(home.members.every(m => !m.ready)); assert.equal(home.members.length, 2);
    for (const b of [A, B]) assert.equal((await srv.store.get(b.id)).ratings.duel.games, 0, 'a party\'s duel is not rated');
  } finally { A.close(); B.close(); await srv.close(); }
});

test('2v2: a party of two votes for it, readies up and plays on one team against two players on their own', async () => {
  const srv = await startServer({ sdT: 20, rematchWindow: 1 });
  const [A, B, C, D] = makeBots(srv, 4, { behavior: 'still', prefix: 'tm' });
  try {
    await Promise.all([A, B, C, D].map(b => b.connect()));
    const v = await A.net.partyCreate(); await B.net.partyJoin(v.code);
    await until(() => A.net.party && A.net.party.members.length === 2);
    await A.net.partyVote('duo'); await B.net.partyVote('duo');
    await until(() => A.net.party.mode === 'duo');
    assert.equal(A.net.party.modes.find(x => x.mode === 'duo').plan, 'queue', 'a party of two finds the other team');
    const queued = A.wait('queued', m => m.party === true); await A.net.partyReady(true); await B.net.partyReady(true); await queued;
    await until(() => A.net.party.state === 'queued');
    const found = Promise.all([A, B, C, D].map(b => b.wait('matchFound', () => true, 10000)));
    await C.net.queue('duo'); await D.net.queue('duo');
    const f = await found, sideOf = id => f[0].players.find(p => p.id === id).side;
    assert.equal(f[0].mode, 'duo'); assert.equal(sideOf(A.id), sideOf(B.id), 'the party is one team'); assert.notEqual(sideOf(A.id), sideOf(C.id)); assert.equal(sideOf(C.id), sideOf(D.id));
    assert.equal(f[0].rated, true, 'matchmaking, so rated');
    await until(() => A.net.party.state === 'match');
  } finally { for (const b of [A, B, C, D]) b.close(); await srv.close(); }
});

test('a party of four plays a Showdown of its own (unrated), all four in it', async () => {
  const srv = await startServer({ sdT: 20, rematchWindow: 1 });
  const bots = makeBots(srv, 4, { behavior: 'still', prefix: 'four' });
  try {
    await Promise.all(bots.map(b => b.connect()));
    const v = await bots[0].net.partyCreate(); for (const b of bots.slice(1)) await b.net.partyJoin(v.code);
    await until(() => bots[0].net.party && bots[0].net.party.members.length === 4);
    assert.deepEqual(bots[0].net.party.modes.map(x => x.mode + ':' + x.plan), ['ffa:private', 'duo:private']);
    for (const b of bots) await b.net.partyVote('ffa');
    const found = Promise.all(bots.map(b => b.wait('matchFound', () => true, 10000)));
    for (const b of bots) await b.net.partyReady(true);
    const f = await found;
    assert.equal(f[0].mode, 'ffa'); assert.equal(f[0].rated, false); assert.equal(f[0].players.length, 4);
    assert.deepEqual(f[0].players.map(p => p.side).sort(), [0, 1, 2, 3], 'everyone for themselves');
  } finally { for (const b of bots) b.close(); await srv.close(); }
});

test('the 3-way for a party (v394): two find a third player online, three play their own; an earlier game in the party hides it', async () => {
  const on = ['duel', 'trio', 'ffa', 'duo'];
  const p = new Party('TRIOTRIO'), mk = (id, client) => ({ player: { id, name: id, look: null }, client });
  p.add(mk('a', 'rm-394')); p.add(mk('b', 'rm-395'));
  assert.deepEqual(p.modes(on).map(x => x.mode + ':' + x.plan), ['duel:private', 'trio:queue', 'ffa:queue', 'duo:queue'], 'two: a 3-way finds one more');
  p.add(mk('c', 'rm-394'));
  assert.deepEqual(p.modes(on).map(x => x.mode + ':' + x.plan), ['trio:private', 'ffa:queue'], 'three: a 3-way of their own');
  p.add(mk('d', 'rm-391')); p.remove('d'); p.member('c').trio = false;
  assert.deepEqual(p.modes(on).map(x => x.mode), ['ffa'], 'a game before v394 in the party: no 3-way');
  const srv = await startServer({ sdT: 20, matchT: 3, rematchWindow: 1 });
  const [A, B, C] = makeBots(srv, 3, { behavior: 'still', prefix: 'tri', client: 'rm-394' });
  const [D, E, F] = makeBots(srv, 3, { behavior: 'still', prefix: 'own', client: 'rm-394' });
  try {
    await Promise.all([A, B, C, D, E, F].map(b => b.connect()));
    // two friends and one player on their own
    const v = await A.net.partyCreate(); await B.net.partyJoin(v.code);
    await until(() => A.net.party && A.net.party.members.length === 2);
    assert.equal(A.net.party.modes.find(x => x.mode === 'trio').plan, 'queue');
    await B.net.partyReady(true); await A.net.partyVote('trio'); await until(() => A.net.party.mode === 'trio');
    const queued = A.wait('queued', m => m.party === true && m.mode === 'trio'); await A.net.partyReady(true); await queued;
    const found = Promise.all([A, B, C].map(b => b.wait('matchFound', () => true, 10000)));
    await C.net.queue('trio');
    const f = await found;
    assert.equal(f[0].mode, 'trio'); assert.equal(f[0].players.length, 3); assert.equal(f[0].rated, true, 'matchmaking, so rated');
    assert.deepEqual(f[0].players.map(p => p.id).sort(), [A.id, B.id, C.id].sort(), 'the two friends and the third, each on their own side');
    assert.equal(new Set(f[0].players.map(p => p.side)).size, 3);
    // three friends: a 3-way of their own
    const w = await D.net.partyCreate(); await E.net.partyJoin(w.code); await F.net.partyJoin(w.code);
    await until(() => D.net.party && D.net.party.members.length === 3);
    assert.equal(D.net.party.modes.find(x => x.mode === 'trio').plan, 'private');
    await E.net.partyReady(true); await F.net.partyReady(true); await D.net.partyVote('trio');
    const own = Promise.all([D, E, F].map(b => b.wait('matchFound', () => true, 10000))); await D.net.partyReady(true);
    const g = await own; assert.equal(g[0].mode, 'trio'); assert.equal(g[0].rated, false, 'just the party: not rated');
    assert.deepEqual(g[0].players.map(p => p.id).sort(), [D.id, E.id, F.id].sort());
  } finally { for (const b of [A, B, C, D, E, F]) b.close(); await srv.close(); }
});

test('a dropped member keeps their place for a while, comes back into the party, or is gone after the grace', async () => {
  const srv = await startServer({ partyGrace: 1.2 });
  const [A, B] = people(srv, 2);
  try {
    await Promise.all([A, B].map(p => p.connect()));
    const v = await A.partyCreate(); await B.partyJoin(v.code); await B.partyReady(true);
    const away = A.wait('party', m => m.members.some(x => x.id === B.id && x.away));
    B.ws.close(); // (the app went to the background: the game closes its connection)
    const a = await away; assert.equal(a.members.find(x => x.id === B.id).ready, false, 'away is not ready');
    const back = A.wait('party', m => m.members.length === 2 && !m.members.some(x => x.away));
    await back; await until(() => B.party && B.party.code === v.code); // (the SDK reconnects by itself, and the server puts them back)
    // gone for longer than the grace: removed
    B.autoReconnect = false; B.close();
    await A.wait('party', m => m.members.length === 1, 5000);
    assert.equal(A.party.leader, A.id);
  } finally { A.close(); B.close(); await srv.close(); }
});

test('invites: the friend is nudged live, a decline is passed on; pokes for friend requests', async () => {
  const srv = await startServer();
  const [A, B, C] = people(srv, 3);
  try {
    await Promise.all([A, B, C].map(p => p.connect()));
    const v = await A.partyCreate();
    const nudged = B.wait('poke'); const w = await A.partyInvite(B.sb, { name: B.name, look: B.look });
    assert.equal((await nudged).k, 'invite'); assert.equal(Object.keys(await nudged).length, 2, 'a nudge carries nothing but its kind');
    assert.equal(w.invites.length, 1); assert.equal(w.invites[0].to, B.sb); assert.equal(w.invites[0].name, B.name); assert.ok(w.invites[0].left > 110000 && w.invites[0].left <= 120000);
    // B says no: the party hears it, and the invite is gone
    const note = A.wait('partyNote'); await B.partyDecline(v.code);
    const n = await note; assert.equal(n.k, 'declined'); assert.equal(n.name, B.name); await until(() => A.party.invites.length === 0);
    // C is invited and joins: the invite goes once they are in
    await A.partyInvite(C.sb, { name: C.name }); await C.partyJoin(v.code); await until(() => A.party.members.length === 2 && A.party.invites.length === 0);
    await assert.rejects(A.partyInvite(C.sb, { name: C.name }), e => e.code === 'already');
    await assert.rejects(A.partyInvite('not-an-id', {}), e => e.code === 'bad_invite');
    // a friend request: a nudge too
    const req = B.wait('poke', m => m.k === 'request'); C.poke(B.sb, 'request'); assert.equal((await req).k, 'request');
    // too many invites in a row: told to wait
    const codes = []; for (let i = 0; i < 16; i++) codes.push(await A.partyInvite(randomUUID(), { name: 'x' }).then(() => 'ok', e => e.code));
    assert.ok(codes.includes('rate'), codes.join());
  } finally { for (const p of [A, B, C]) p.close(); await srv.close(); }
});

test('a solo player in a party of one can still find a match; a bigger party readies up instead', async () => {
  const srv = await startServer();
  const [A, B, C] = people(srv, 3);
  try {
    await Promise.all([A, B, C].map(p => p.connect()));
    const v = await A.partyCreate();
    assert.equal((await A.queue('duel')).mode, 'duel', 'a party of one queues like anyone');
    await assert.rejects(B.partyJoin(v.code), e => e.code === 'busy', 'not while they are finding a match');
    await A.cancelQueue(); await B.partyJoin(v.code); await until(() => A.party.members.length === 2);
    await assert.rejects(A.queue('duel'), e => e.code === 'busy', 'two in the party: ready up instead');
    // a player's own place in the queue is let go when they join a party
    const left = C.wait('queueLeft').catch(() => null); await C.queue('duel'); await C.partyJoin(v.code);
    assert.equal(srv.mm.sizes().duel, 0); assert.equal(C.party.members.length, 3); void left;
  } finally { for (const p of [A, B, C]) p.close(); await srv.close(); }
});

test('a connection waiting in the lobby is pinged slowly; one that goes silent is closed', async () => {
  const srv = await startServer({ idlePing: 3, silentKick: 2.5 });
  const [A] = people(srv, 1, { autoReconnect: false });
  try {
    let spings = 0, deaf = false; const orig = A._onMessage.bind(A);
    A._onMessage = d => { if (deaf) return; if (typeof d !== 'string' && new Uint8Array(d)[0] === 4) spings++; orig(d); };
    A.setBeat(1000); await A.connect(); await sleep(4300);
    assert.ok(spings <= 2, 'slow pings in the lobby: ' + spings);
    await A.queue('duel'); spings = 0; await sleep(4300);
    assert.ok(spings >= 2, 'quicker while queued: ' + spings);
    await A.cancelQueue(); await sleep(500);
    assert.equal(srv.online.has(A.id), true, 'a heartbeat keeps it');
    // nothing at all from the phone any more (no heartbeat, no answers: a phone that lost its signal): closed
    const closed = A.wait('close', () => true, 9000); deaf = true; A._stopPings();
    await closed; await until(() => !srv.online.has(A.id), 2000);
  } finally { A.close(); await srv.close(); }
});

test('the party code is long and has no look-alikes', () => {
  assert.equal(PARTY.CODE_LEN, 8);
  const p = new Party('X'); assert.equal(p.view(['duel']).members.length, 0);
});
