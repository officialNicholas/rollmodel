// Matches on real worker threads (MATCH_WORKERS): the whole of a match through the threads (start on one clock,
// play, results saved), a dropped and a silent connection picked up again, a rematch, a room, a worker that dies,
// and shutting down. (The rest of the suite runs the same path in one thread: RM_MATCH_WORKERS=inline.)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { startServer, makeBots, until, sleep, metric } from './helpers/harness.js';

const W2 = { matchWorkers: 2 };
async function duel(rules = {}, opts = {}) {
  const srv = await startServer(Object.assign({ matchT: 5 }, rules), W2);
  const [A, B] = makeBots(srv, 2, Object.assign({ profile: 'rtt60', behavior: 'wander', prefix: 'wk' }, opts));
  await Promise.all([A, B].map(b => b.connect()));
  await A.net.queue('duel'); await B.net.queue('duel');
  return { srv, A, B, close: async () => { A.close(); B.close(); await srv.close(); } };
}

test('a duel on a worker thread: one clock, snapshots, results and ratings saved', async () => {
  const c = await duel();
  try {
    const starts = await Promise.all([c.A, c.B].map(b => b.wait('start')));
    assert.equal(starts[0].startAt, starts[1].startAt);
    // the worker's times (startAt, snapshots) and the main thread's (pongs) are one clock: each phone counts down to
    // the same moment the server does
    const err = [c.A, c.B].map(b => Math.abs(b.net.serverNow() - (performance.now() + 0) - b.net._clock.offset));
    for (const e of err) assert.ok(e < 1, 'serverNow is our clock plus the offset');
    for (const b of [c.A, c.B]) assert.ok(Math.abs(b.net._clock.offset) < 15, 'clock offset small on one machine (' + b.net._clock.offset + ')');
    await until(() => c.A.net.stats().snapshotsPerSec >= 25, 5000);
    const end = await c.A.wait('matchEnd', () => true, 15000);
    assert.equal(end.results.length, 2); assert.ok(end.results.every(r => r.rating), 'rated');
    assert.ok(end.results.some(r => r.coverage > 0), 'the worker saw them move: paint on the canvas');
    await sleep(200);
    const h = c.srv.health(); assert.equal(h.workers.length, 2); assert.equal(h.stats.matchesEnded, 1);
    const w = await c.A.net.connect(); assert.equal(Math.round(w.ratings.duel.r), end.results.find(r => r.id === c.A.id).rating.after, 'the new rating is saved');
    assert.equal(c.A.stats.corrections + c.B.stats.corrections, 0);
  } finally { await c.close(); }
});

test('on a worker: a dropped connection and a silent one pick the match up again', async () => {
  const c = await duel({ matchT: 14, reconnectWindow: 20 });
  try {
    await Promise.all([c.A, c.B].map(b => b.wait('start')));
    await sleep(800);
    let r = c.A.wait('resume', () => true, 10000); c.A.net.ws.kill(); await r;
    r = c.B.wait('resume', () => true, 10000); const t0 = Date.now(); c.B.net.ws.blackhole(); await r;
    metric('workers.silentResumeMs', Date.now() - t0, 'ms', 'link gone silent to resumed match, match on a worker thread');
    const end = await c.A.wait('matchEnd', () => true, 20000);
    assert.ok(end.results.every(x => !x.left), 'nobody forfeited');
  } finally { await c.close(); }
});

test('on a worker: a rematch starts a new match, and a room goes back to its room', async () => {
  const srv = await startServer({ matchT: 2.5, rematchWindow: 5 }, W2);
  const [A, B] = makeBots(srv, 2, { behavior: 'wander', prefix: 'wr', rematch: true });
  try {
    await Promise.all([A, B].map(b => b.connect()));
    const code = await A.net.createRoom('duel'); await B.net.joinRoom(code);
    A.net.ready(true); B.net.ready(true);
    const f1 = await A.wait('matchFound');
    await A.wait('matchEnd', () => true, 10000);
    const f2 = await A.wait('matchFound', m => m.matchId !== f1.matchId, 10000);
    assert.equal(f2.room, code, 'the rematch is in the same room');
    A.o.rematch = false; B.o.rematch = false;
    await A.wait('matchEnd', () => true, 10000);
    const back = await A.wait('room', m => m.code === code && !m.inMatch, 10000);
    assert.equal(back.players.length, 2, 'both back in the room');
  } finally { A.close(); B.close(); await srv.close(); }
});

test('a worker that dies: its players are told and can play again; a new worker takes its place', async () => {
  const srv = await startServer({ matchT: 30 }, { matchWorkers: 1 });
  const [A, B] = makeBots(srv, 2, { behavior: 'wander', prefix: 'wd' });
  try {
    await Promise.all([A, B].map(b => b.connect()));
    await A.net.queue('duel'); await B.net.queue('duel');
    await A.wait('start');
    const cancelled = A.wait('matchCancelled', () => true, 5000);
    await srv.pool.workers[0].w.terminate();
    assert.equal((await cancelled).reason, 'server_error');
    await until(() => srv.pool.workers[0].ready && !srv.pool.workers[0].dead, 5000);
    await A.net.queue('duel').catch(() => {}); await B.net.queue('duel').catch(() => {});
    const s = await A.wait('start', () => true, 10000); assert.ok(s.startAt > 0, 'a new match on the new worker');
  } finally { A.close(); B.close(); await srv.close(); }
});

test('shutting down with matches on workers: every player hears it, and the workers stop', async () => {
  const srv = await startServer({ matchT: 30 }, W2);
  const bots = makeBots(srv, 4, { behavior: 'wander', prefix: 'ws', autoReconnect: false });
  try {
    await Promise.all(bots.map(b => b.connect()));
    for (const b of bots) await b.net.queue('duel');
    await Promise.all(bots.map(b => b.wait('start')));
    const told = bots.map(b => b.wait('matchCancelled', m => m.reason === 'server_shutdown', 5000));
    await srv.close();
    await Promise.all(told);
    assert.ok(srv.pool.workers.every(W => W.dead), 'workers stopped');
  } finally { for (const b of bots) b.close(); }
});
