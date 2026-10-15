// Connections come and go: a reconnect within the window picks the match up again, a player who does not come back
// forfeits, a second device with the same token takes over, and AFK or idle players are removed.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { FLAGS, RMNet } from '../client/rmnet.js';
import { startServer, makeBots, until, sleep, matchOf, metric } from './helpers/harness.js';
import { netSim, PROFILES } from './helpers/netsim.js';

async function duel(rules, opts = {}) {
  const srv = await startServer(rules);
  const [A, B] = makeBots(srv, 2, Object.assign({ profile: 'rtt60', behavior: 'wander', prefix: 'ses' }, opts));
  await Promise.all([A, B].map(b => b.connect()));
  await A.net.queue('duel'); await B.net.queue('duel');
  await Promise.all([A, B].map(b => b.wait('start')));
  await until(() => A.net.serverNow() > A.startAt + 500, 5000);
  return { srv, A, B, close: async () => { A.close(); B.close(); await srv.close(); } };
}

test('a dropped connection that comes back within the window picks the match up again', async () => {
  const c = await duel({ matchT: 9, reconnectWindow: 20 });
  try {
    const away = c.B.wait('playerAway', m => m.slot === c.A.slot), back = c.B.wait('playerBack', m => m.slot === c.A.slot);
    const resumed = c.A.wait('resume', () => true, 10000), t0 = Date.now();
    c.A.net.ws.kill(); // the phone loses its signal
    await away;
    await until(() => { const r = c.B.net.remote(c.A.slot); return r && (r.flags & FLAGS.AWAY); }, 3000);
    const r = await resumed; await back;
    metric('session.resumeMs', Date.now() - t0, 'ms', 'drop to resumed match (SDK reconnect with backoff, 60 ms network)');
    assert.equal(r.matchId, matchOf(c.srv, c.B.id).id); assert.equal(r.you, c.A.slot); assert.ok(r.self && Number.isFinite(r.self.x));
    const end = await c.A.wait('matchEnd', () => true, 15000);
    assert.equal(end.results.find(x => x.slot === c.A.slot).left, false, 'not a forfeit');
    assert.equal(c.A.stats.corrections, 0);
  } finally { await c.close(); }
});

test('a player who does not come back in time forfeits', async () => {
  const c = await duel({ matchT: 30, reconnectWindow: 1.5 });
  try {
    const left = c.B.wait('playerLeft', m => m.slot === c.A.slot, 6000), end = c.B.wait('matchEnd', () => true, 8000);
    c.A.net.autoReconnect = false; c.A.stop(); c.A.net.ws.kill();
    assert.equal((await left).reason, 'disconnected');
    const e = await end; assert.equal(e.reason, 'forfeit'); assert.equal(e.winner, e.results.find(x => x.slot === c.B.slot).side);
    assert.ok(e.results.find(x => x.slot === c.A.slot).rating.after < 1500, 'the forfeit costs rating');
  } finally { await c.close(); }
});

test('quitting a match forfeits it at once', async () => {
  const c = await duel({ matchT: 30 });
  try {
    const slotA = c.A.slot; // (the SDK forgets its slot once it has left)
    const left = c.B.wait('playerLeft', m => m.slot === slotA, 5000), end = c.B.wait('matchEnd', () => true, 5000);
    const r = await c.A.net.leaveMatch();
    assert.equal(r.reason, 'you_left'); assert.equal(c.A.net.match, null); assert.equal(c.A.slot, -1);
    assert.equal((await left).reason, 'quit');
    const e = await end; assert.equal(e.reason, 'forfeit'); assert.equal(e.results.find(x => x.slot === slotA).left, true);
    await assert.rejects(c.A.net.leaveMatch(), e2 => e2.code === 'not_in_match');
    assert.equal((await c.A.net.queue('duel')).mode, 'duel', 'free to queue again');
  } finally { await c.close(); }
});

test('the same token on a new device takes over the session and the match', async () => {
  const c = await duel({ matchT: 30 });
  try {
    const kicked = c.A.wait('kicked');
    const phone2 = new RMNet({ url: c.srv.url, token: c.A.token, name: 'other phone', WebSocket: netSim(PROFILES.rtt60), autoReconnect: false });
    const resumed = new Promise(res => phone2.on('resume', res));
    const w = await phone2.connect();
    assert.equal(w.id, c.A.id, 'same player'); assert.equal(w.resume, matchOf(c.srv, c.B.id).id);
    assert.equal((await kicked).reason, 'replaced');
    const r = await resumed; assert.equal(r.you, c.A.slot);
    phone2.close();
  } finally { await c.close(); }
});

test('AFK: a player whose game stops sending is flagged, then removed', async () => {
  const c = await duel({ matchT: 30, afkWarn: 1, afkForfeit: 2.5 });
  try {
    const afk = c.B.wait('afk', m => m.slot === c.A.slot && m.on), left = c.B.wait('playerLeft', m => m.slot === c.A.slot, 8000);
    c.A.stop(); // connected, but nothing is being sent (the app went to the background)
    await afk;
    assert.equal((await left).reason, 'afk');
    assert.equal((await c.B.wait('matchEnd')).reason, 'forfeit');
  } finally { await c.close(); }
});

test('idle: a player who sends but never moves is removed', async () => {
  const c = await duel({ matchT: 30, idleForfeit: 2 }, {});
  try {
    c.A.o.behavior = 'still';
    const left = await c.B.wait('playerLeft', m => m.slot === c.A.slot, 8000);
    assert.equal(left.reason, 'idle');
  } finally { await c.close(); }
});
