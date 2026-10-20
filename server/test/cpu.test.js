// CPU players online (v404): a party playing against CPUs, matchmaking that fills the empty places with CPUs after a
// wait (two people at least, and only games that drive CPUs), the CPU players riding on one player's game (their states
// and moves come from it, their rulings go back to it), leaving with it, and reactions on a match's results (v405).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { cpuPlan } from '../src/party.js';
import { startServer, makeBots, until, sleep } from './helpers/harness.js';

const NEW = 'rm-404';
// the CPU players' bodies, as the owner's game would move them: on their spots until Go, then a slow walk
function driveCpus(owner) {
  let spawns = null, t0 = 0;
  owner.on('start', m => { spawns = new Map(m.spawns.map(s => [s.slot, s])); t0 = m.startAt; });
  const iv = setInterval(() => {
    if (!spawns || !owner.net.match) return;
    for (const slot of owner.net.bots()) {
      const s = spawns.get(slot); if (!s) continue;
      const dt = Math.max(0, (owner.net.serverNow() - t0) / 1000), d = Math.min(1.5, dt * 0.8);
      owner.net.sendBotState(slot, { x: s.x + Math.sin(s.yaw) * d, y: s.y, z: s.z + Math.cos(s.yaw) * d, yaw: s.yaw, spd: dt > 0 && d < 1.5 ? 0.8 : 0, vy: 0, paint: 1 });
    }
  }, 33);
  return () => clearInterval(iv);
}

test('how many CPUs a party gets: two people at least, and only where there is room', () => {
  assert.equal(cpuPlan('duel', 2), null); assert.equal(cpuPlan('trio', 1), null, 'one alone plays the CPUs offline');
  assert.equal(cpuPlan('trio', 2), 1); assert.equal(cpuPlan('ffa', 2), 2); assert.equal(cpuPlan('ffa', 3), 1); assert.equal(cpuPlan('ffa', 4), null);
  assert.equal(cpuPlan('duo', 2), 2); assert.equal(cpuPlan('duo', 3), 1);
});

test('a party against CPUs: the leader picks it, the match starts at once (unrated) with CPUs driven by one of the party', async () => {
  const srv = await startServer({ sdT: 5 });
  const [A, B] = makeBots(srv, 2, { behavior: 'wander', prefix: 'cpuP', client: NEW });
  let stop = () => {};
  try {
    await Promise.all([A, B].map(b => b.connect()));
    const v = await A.net.partyCreate(); await B.net.partyJoin(v.code);
    await until(() => A.net.party && A.net.party.members.length === 2);
    assert.equal(A.net.party.modes.find(x => x.mode === 'ffa').cpus, 2, 'the Showdown can take two CPUs');
    await A.net._request({ t: 'partyVote', mode: 'ffa', cpu: true });
    await until(() => B.net.party.cpu === true && B.net.party.mode === 'ffa');
    const found = Promise.all([A, B].map(b => b.wait('matchFound', () => true, 8000)));
    await B.net.partyReady(true); await A.net.partyReady(true);
    const [fa, fb] = await found;
    assert.equal(fa.players.length, 4); assert.equal(fa.rated, false);
    const cpus = fa.players.filter(p => p.cpu); assert.equal(cpus.length, 2);
    const owner = cpus[0].owner === A.id ? A : B, other = owner === A ? B : A;
    assert.ok(cpus.every(p => p.owner === owner.id), 'one game drives both');
    assert.ok(fa.players.filter(p => !p.cpu).every(p => p.sb === undefined || typeof p.sb === 'string'));
    assert.deepEqual(owner.net.bots().sort(), cpus.map(p => p.slot).sort()); assert.deepEqual(other.net.bots(), []);
    stop = driveCpus(owner);
    await owner.wait('start', () => true, 8000);
    await until(() => owner.net.serverNow() > owner.net.match.startAt + 600, 8000);
    // the other player sees the CPUs where their owner's game puts them
    const cs = cpus[0].slot; await until(() => other.net.remote(cs), 4000);
    const r = other.net.remote(cs); assert.ok(Number.isFinite(r.x));
    // a CPU's move is refereed and answered to its owner; nobody else may move it
    const j = await owner.net.botAction(cs, 'jump'); assert.equal(j.ok, true, 'jump: ' + j.reason);
    const no = await other.net.botAction(cs, 'jump'); assert.equal(no.ok, false);
    const end = await A.wait('matchEnd', () => true, 15000);
    assert.equal(end.results.length, 4); assert.equal(end.rated, false);
    for (const b of [A, B]) assert.equal((await srv.store.get(b.id)).ratings.ffa.games, 0);
  } finally { stop(); A.close(); B.close(); await srv.close(); }
});

test('matchmaking: two people who waited long enough play a 3-way with a CPU; a game that cannot drive CPUs never gets one', async () => {
  const srv = await startServer({ cpuFill: 0.6, sdT: 5, matchT: 3 });
  const [A, B] = makeBots(srv, 2, { behavior: 'wander', prefix: 'cpuQ', client: NEW });
  const [C] = makeBots(srv, 1, { behavior: 'wander', prefix: 'oldQ', client: 'rm-401' });
  let stop = () => {};
  try {
    await Promise.all([A, B, C].map(b => b.connect()));
    // an older game and a new one: no CPUs, so they keep waiting for a third
    await A.net.queue('trio'); await C.net.queue('trio'); await sleep(1500);
    assert.equal(A.net.match, null, 'no match with an older game in it'); await A.net.cancelQueue(); await C.net.cancelQueue();
    const found = Promise.all([A, B].map(b => b.wait('matchFound', () => true, 8000)));
    await A.net.queue('trio'); await B.net.queue('trio');
    const [fa] = await found;
    assert.equal(fa.players.length, 3); assert.equal(fa.players.filter(p => p.cpu).length, 1); assert.equal(fa.rated, false);
    const owner = fa.players.find(p => p.cpu).owner === A.id ? A : B; stop = driveCpus(owner);
    await A.wait('matchEnd', () => true, 15000);
  } finally { stop(); A.close(); B.close(); C.close(); await srv.close(); }
});

test('the CPUs leave with the game that drives them; reactions on the results reach the others', async () => {
  const srv = await startServer({ sdT: 6, rematchWindow: 6 });
  const [A, B, C] = makeBots(srv, 3, { behavior: 'wander', prefix: 'cpuL', client: NEW });
  let stop = () => {};
  try {
    await Promise.all([A, B, C].map(b => b.connect()));
    const v = await A.net.partyCreate(); await B.net.partyJoin(v.code); await C.net.partyJoin(v.code);
    await until(() => A.net.party && A.net.party.members.length === 3);
    await A.net._request({ t: 'partyVote', mode: 'ffa', cpu: true });
    const found = Promise.all([A, B, C].map(b => b.wait('matchFound', () => true, 8000)));
    for (const b of [B, C, A]) await b.net.partyReady(true);
    const [fa] = await found; const cpu = fa.players.find(p => p.cpu); assert.ok(cpu);
    const owner = [A, B, C].find(b => b.id === cpu.owner), rest = [A, B, C].filter(b => b !== owner);
    stop = driveCpus(owner); const mySlot = rest[0].slot;
    await owner.wait('start', () => true, 8000); await sleep(800);
    // a reaction on the results: only once it's over (and the server keeps them to the match)
    const left = rest[0].wait('playerLeft', m => m.slot === cpu.slot, 8000);
    await owner.net.leaveMatch();
    await left; // (its CPU went with it)
    const end = await rest[0].wait('matchEnd', () => true, 40000);
    assert.ok(end.results.find(r => r.slot === cpu.slot).left);
    const got = rest[1].wait('matchReact', () => true, 4000); rest[0].net._sendJ({ t: 'matchReact', e: 'gg' });
    const m = await got; assert.equal(m.e, 'gg'); assert.equal(m.slot, mySlot, 'from the one who sent it (the match had closed: someone left, so no rematch)');
  } finally { stop(); A.close(); B.close(); C.close(); await srv.close(); }
});

// (v413) a match with CPUs can be played again: each CPU goes along with the vote of the game that drives it
for (const extra of [{}, { matchWorkers: 1 }]) test('a rematch with CPUs' + (extra.matchWorkers ? ' (on a match worker)' : ''), async () => {
  const srv = await startServer({ sdT: 4, rematchWindow: 6 }, extra);
  const [A, B] = makeBots(srv, 2, { behavior: 'wander', prefix: 'cpuR', client: 'rm-413' });
  let stop = () => {};
  try {
    await Promise.all([A, B].map(b => b.connect()));
    const v = await A.net.partyCreate(); await B.net.partyJoin(v.code);
    await until(() => A.net.party && A.net.party.members.length === 2);
    await A.net.partyVote('trio', true);
    await until(() => B.net.party.cpu === true && B.net.party.mode === 'trio');
    const found = Promise.all([A, B].map(b => b.wait('matchFound', () => true, 8000)));
    await B.net.partyReady(true); await A.net.partyReady(true);
    const [fa] = await found; const cpu = fa.players.find(p => p.cpu); assert.ok(cpu);
    const owner = [A, B].find(b => b.id === cpu.owner); stop = driveCpus(owner);
    await Promise.all([A, B].map(b => b.wait('matchEnd', () => true, 20000)));
    const votes = A.wait('rematch', m => m.votes.filter(x => x === true).length === 3, 6000);
    const again = Promise.all([A, B].map(b => b.wait('matchFound', m => m.matchId !== fa.matchId, 8000)));
    A.net.rematch(true); B.net.rematch(true);
    await votes; // (the CPU's vote is its owner's)
    const [ra] = await again;
    assert.equal(ra.players.length, 3); assert.equal(ra.players.filter(p => p.cpu).length, 1, 'the CPU plays again');
  } finally { stop(); A.close(); B.close(); await srv.close(); }
});
