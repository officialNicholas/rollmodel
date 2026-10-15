// Private rooms (codes, ready-up, unrated play, back to the room after) and ratings from queue matches.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { CODE_ALPHABET } from '../src/util.js';
import { JsonFileStore } from '../src/store.js';
import { startServer, makeBots, until, sleep, matchOf } from './helpers/harness.js';

test('private room: code, join, ready, an unrated match, then back to the room', async () => {
  const srv = await startServer({ matchT: 3, rematchWindow: 1 });
  const [H, G, X] = makeBots(srv, 3, { behavior: 'wander', prefix: 'room' });
  try {
    await Promise.all([H, G, X].map(b => b.connect()));
    const code = await H.net.createRoom('duel');
    assert.match(code, /^[A-Z0-9]{5}$/); for (const ch of code) assert.ok(CODE_ALPHABET.includes(ch));
    const joined = await G.net.joinRoom(code.toLowerCase()); // codes are not case sensitive
    assert.equal(joined.code, code); assert.equal(joined.players.length, 2); assert.equal(joined.host, H.id);
    await assert.rejects(X.net.joinRoom(code), e => e.code === 'full', 'a duel room holds two');
    await assert.rejects(H.net.queue('duel'), e => e.code === 'busy', 'no queueing from inside a room');
    // ready up: the match starts when everyone is ready
    const found = Promise.all([H, G].map(b => b.wait('matchFound')));
    H.net.ready(true); await sleep(100);
    assert.equal(srv.matches.size, 0, 'not until everyone is ready');
    G.net.ready(true);
    const f = await found; assert.equal(f[0].rated, false); assert.equal(f[0].room, code);
    const end = await H.wait('matchEnd', () => true, 15000);
    assert.ok(end.results.every(r => r.rating === null), 'private matches are not rated');
    // after the rematch window: back in the room, not ready
    const room = await H.wait('room', m => !m.inMatch, 8000);
    assert.equal(room.code, code); assert.ok(room.players.every(p => !p.ready));
    for (const b of [H, G]) assert.equal((await srv.store.get(b.id)).ratings.duel.games, 0);
    // ready again: another match in the same room
    const again = Promise.all([H, G].map(b => b.wait('matchFound')));
    H.net.ready(true); G.net.ready(true);
    const f2 = await again; assert.notEqual(f2[0].matchId, f[0].matchId);
    await H.wait('matchEnd', () => true, 15000);
  } finally { for (const b of [H, G, X]) b.close(); await srv.close(); }
});

test('rooms: the host can leave (another member takes over), the last one out closes it', async () => {
  const srv = await startServer();
  const [H, G] = makeBots(srv, 2, { prefix: 'host' });
  try {
    await Promise.all([H, G].map(b => b.connect()));
    const code = await H.net.createRoom('trio');
    await G.net.joinRoom(code);
    const update = G.wait('room', m => m.players.length === 1);
    await H.net.leaveRoom();
    assert.equal((await update).host, G.id);
    await G.net.leaveRoom();
    assert.equal(srv.rooms.size, 0);
    await assert.rejects(H.net.joinRoom(code), e => e.code === 'not_found');
  } finally { H.close(); G.close(); await srv.close(); }
});

test('ratings: the winner of a queue match gains, the loser drops, and it is saved to the file', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'rmrate-')), file = path.join(dir, 'store.json');
  const srv = await startServer({ matchT: 4 }, { store: new JsonFileStore(file, { delayMs: 20 }) });
  const [W, L] = makeBots(srv, 2, { prefix: 'rate' });
  W.o.behavior = 'wander'; L.o.behavior = 'still'; // the one who moves paints more
  try {
    await Promise.all([W, L].map(b => b.connect()));
    await W.net.queue('duel'); await L.net.queue('duel');
    const e = await W.wait('matchEnd', () => true, 20000);
    const rw = e.results.find(r => r.id === W.id), rl = e.results.find(r => r.id === L.id);
    assert.equal(rw.place, 1); assert.equal(rl.place, 2);
    assert.ok(rw.rating.after > 1500 && rl.rating.after < 1500);
    assert.ok(Math.abs((rw.rating.after - 1500) - (1500 - rl.rating.after)) <= 1, 'equal and opposite for two new players');
    assert.ok(rw.rating.rd < 350);
    await sleep(100); await srv.store.flush();
    const disk = new JsonFileStore(file); await disk.init();
    const saved = await disk.get(W.id); assert.equal(Math.round(saved.ratings.duel.r), rw.rating.after); assert.equal(saved.ratings.duel.games, 1);
    assert.equal(saved.stats.wins, 1);
    // the next hello reports the new rating
    const w2 = await W.net.connect(); assert.equal(w2.ratings.duel.r, rw.rating.after);
  } finally { W.close(); L.close(); await srv.close(); }
});
