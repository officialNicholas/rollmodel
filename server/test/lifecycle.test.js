// The whole life of a match in every mode, with bots on a 60 ms network: queue, match found, map consensus, the
// synced countdown, play, the end and results, ratings, the rematch vote, and back to the lobby.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { MODES, layoutHash, FLAGS } from '../client/rmnet.js';
import { MODE_INFO } from '../src/constants.js';
import { startServer, makeBots, until, sleep, metric } from './helpers/harness.js';

async function playOnce(bots, { expectRematch }) {
  const ends = await Promise.all(bots.map(b => b.wait('matchEnd', () => true, 40000)));
  const r0 = ends[0];
  for (const e of ends) assert.deepEqual(e.results, r0.results, 'everyone gets the same results');
  if (expectRematch) return { end: r0, next: await Promise.all(bots.map(b => b.wait('matchFound', () => true, 20000))) };
  await Promise.all(bots.map(b => b.wait('matchClosed', () => true, 20000)));
  return { end: r0 };
}

for (const mode of ['duel', 'trio', 'ffa', 'duo']) {
  test('full lifecycle: ' + mode, async () => {
    const srv = await startServer({ matchT: 5, sdT: 6 });
    const n = MODES[mode], bots = makeBots(srv, n, { profile: 'rtt60', behavior: 'chase', rematch: true, prefix: mode });
    try {
      await Promise.all(bots.map(b => b.connect()));
      const found = bots.map(b => b.wait('matchFound'));
      const t0 = Date.now();
      for (const b of bots) assert.equal((await b.net.queue(mode)).mode, mode);
      const f = await Promise.all(found);
      metric('lifecycle.' + mode + '.matchmaking', Date.now() - t0, 'ms', 'queue to match found, ' + { duel: 'duel', trio: 'trio', ffa: 'Showdown', duo: 'Showdown 2v2' }[mode] + ' (' + n + ' players)');
      const id = f[0].matchId;
      assert.ok(f.every(m => m.matchId === id && m.mode === mode && m.players.length === n));
      assert.deepEqual(f.map(m => m.you).sort(), [...Array(n).keys()], 'each player gets its own slot');
      assert.deepEqual(f[0].players.map(p => p.side), MODE_INFO[mode].sides, 'sides as the game has them');
      assert.equal(new Set(f.map(m => m.seed)).size, 1, 'one seed');
      // consensus, then a countdown everyone shares
      const starts = await Promise.all(bots.map(b => b.wait('start')));
      assert.equal(new Set(starts.map(s => s.startAt)).size, 1);
      assert.equal(starts[0].layoutHash, layoutHash(bots[0].layout), 'the server agrees with the SDK hash');
      assert.equal(starts[0].spawns.length, n);
      // play: snapshots at about 30 a second, coverage a few times a second
      let cov = 0; bots[0].on('coverage', c => { if (c.sides.length === new Set(MODE_INFO[mode].sides).size) cov++; });
      await until(() => bots.every(b => b.net.stats().snapshotsPerSec >= 25), 8000);
      await until(() => cov >= 4, 8000);
      const first = await playOnce(bots, { expectRematch: true });
      const e = first.end;
      assert.equal(e.matchId, id); assert.equal(e.results.length, n); assert.equal(e.rated, true);
      for (const r of e.results) { assert.ok(r.place >= 1 && r.place <= n); assert.ok(r.rating && Number.isFinite(r.rating.after)); assert.equal(r.left, false); }
      if (e.winner >= 0) assert.ok(e.results.filter(r => r.side === e.winner).every(r => r.place === 1));
      if (!MODE_INFO[mode].showdown) assert.ok(e.results.some(r => r.coverage > 0), 'the server painted coverage');
      for (const b of bots) assert.equal(b.stats.corrections, 0, b.net.name + ' was corrected: ' + JSON.stringify(b.events));
      // the rematch: same players, a new match
      const re = first.next;
      assert.ok(re.every(m => m.matchId === re[0].matchId && m.matchId !== id));
      assert.deepEqual(re[0].players.map(p => p.id), f[0].players.map(p => p.id));
      await Promise.all(bots.map(b => b.wait('start')));
      for (const b of bots) b.o.rematch = false; // this time say no
      const second = await playOnce(bots, { expectRematch: false });
      assert.equal(second.end.matchId, re[0].matchId);
      // ratings were saved after both matches
      await sleep(50);
      for (const b of bots) { const p = await srv.store.get(b.id); assert.equal(p.ratings[mode].games, 2); assert.equal(p.stats.matches, 2); }
      // back in the lobby: free to queue again
      for (const b of bots) assert.equal(srv.inMatch.has(b.id), false);
      assert.equal((await bots[0].net.queue(mode)).mode, mode);
      assert.equal(srv.matches.size, 0);
    } finally { for (const b of bots) b.close(); await srv.close(); }
  });
}

test('Showdown: hearts, elimination order, last one standing', async () => {
  const srv = await startServer({ sdT: 60, respawnT: 0.5 });
  const bots = makeBots(srv, 4, { behavior: 'still', prefix: 'sd' });
  try {
    await Promise.all(bots.map(b => b.connect()));
    for (const b of bots) await b.net.queue('ffa');
    await Promise.all(bots.map(b => b.wait('start')));
    await until(() => bots[0].net.serverNow() > bots[0].startAt + 100, 5000);
    // three of them knock themselves out twice each (a fall): two hearts gone, then out
    const order = [bots[3], bots[1], bots[2]];
    for (const b of order) {
      for (let k = 0; k < 2; k++) {
        const ko = b.wait('ko', m => m.slot === b.slot);
        assert.equal((await b.net.action('selfKo', { reason: 'fall' })).ok, true);
        const m = await ko; assert.equal(m.hearts, 1 - k);
        if (k === 0) await b.wait('respawn', r => r.slot === b.slot); else assert.equal(m.out, true);
      }
    }
    const end = await bots[0].wait('matchEnd', () => true, 10000);
    assert.equal(end.reason, 'last_standing');
    const place = slot => end.results.find(r => r.slot === slot).place;
    assert.equal(place(bots[0].slot), 1); assert.equal(place(bots[2].slot), 2); assert.equal(place(bots[1].slot), 3); assert.equal(place(bots[3].slot), 4);
    assert.equal(end.winner, end.results.find(r => r.slot === bots[0].slot).side);
    // an eliminated player's snapshots say so
    const s = bots[0].net.remote(bots[3].slot); assert.ok(s.flags & FLAGS.OUT);
  } finally { for (const b of bots) b.close(); await srv.close(); }
});

test('Showdown 2v2: a side is out only when both are out', async () => {
  const srv = await startServer({ sdT: 60, respawnT: 0.5 });
  const bots = makeBots(srv, 4, { behavior: 'still', prefix: 'duo' });
  try {
    await Promise.all(bots.map(b => b.connect()));
    for (const b of bots) await b.net.queue('duo');
    await Promise.all(bots.map(b => b.wait('start')));
    await until(() => bots[0].net.serverNow() > bots[0].startAt + 100, 5000);
    const bySlot = s => bots.find(b => b.slot === s); // sides [0,1,1,0]
    const out = async b => { for (let k = 0; k < 2; k++) { const ko = b.wait('ko', m => m.slot === b.slot); await b.net.action('selfKo', { reason: 'fall' }); await ko; if (k === 0) await b.wait('respawn', r => r.slot === b.slot); } };
    await out(bySlot(1));
    await sleep(300);
    assert.equal(bots[0].ended, null, 'one of a pair out: the match goes on');
    await out(bySlot(2));
    const end = await bots[0].wait('matchEnd', () => true, 10000);
    assert.equal(end.winner, 0);
    for (const r of end.results) assert.equal(r.place, r.side === 0 ? 1 : 2);
  } finally { for (const b of bots) b.close(); await srv.close(); }
});
