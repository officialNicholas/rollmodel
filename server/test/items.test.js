// Pick-ups: the server places them on its own schedule at the stage's power spots, decides who picks one up from the
// validated positions, keeps the pockets, checks every use and tells everyone.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { performance } from 'node:perf_hooks';
import { startServer, makeBots, until, sleep, matchOf } from './helpers/harness.js';
import { flatLayout } from './helpers/layouts.js';

async function setup(rules) {
  const srv = await startServer(Object.assign({ items: true, matchT: 30, itemFirst: [0.3, 0.4], itemEvery: [0.5, 0.6] }, rules));
  const [A, B] = makeBots(srv, 2, { behavior: 'script', layoutFor: () => flatLayout(26.4), prefix: 'it' });
  A.o.script = bot => { bot.input = { speedK: 0 }; }; B.o.script = bot => { bot.input = { speedK: 0 }; };
  await Promise.all([A, B].map(b => b.connect()));
  const spawned = [];
  A.on('itemSpawn', m => spawned.push(m));
  await A.net.queue('duel'); await B.net.queue('duel');
  await Promise.all([A, B].map(b => b.wait('start')));
  return { srv, A, B, spawned, m: () => matchOf(srv, A.id), close: async () => { A.close(); B.close(); await srv.close(); } };
}
// drive a bot to a point
const goTo = (bot, x, z) => { bot.o.script = b => { const d = Math.hypot(x - b.body.x, z - b.body.z); b.input = d < 0.3 ? { speedK: 0 } : { yaw: Math.atan2(x - b.body.x, z - b.body.z), speedK: d < 1.5 ? 0.4 : 1 }; }; };

test('an item appears at a power spot, the player who reaches it gets it, and can use it once', async () => {
  const c = await setup();
  try {
    const it = (await until(() => c.spawned[0], 6000));
    const spots = flatLayout(26.4).powers; assert.ok(spots.some(p => p[0] === it.x && p[2] === it.z), 'at one of the layout\'s power spots');
    // the nearer player walks to it
    const d = b => Math.hypot(b.body.x - it.x, b.body.z - it.z), P = d(c.A) < d(c.B) ? c.A : c.B, Q = P === c.A ? c.B : c.A;
    const using = await Q.net.action('use'); assert.equal(using.ok, false); assert.equal(using.reason, 'no_item', 'nothing in the pocket yet');
    const taken = Q.wait('itemTaken', m => m.id === it.id, 10000);
    goTo(P, it.x, it.z);
    const t = await taken; assert.equal(t.slot, P.slot); assert.equal(t.kind, it.kind);
    assert.equal(c.m().P[P.slot].item, it.kind);
    // using it: everyone hears about it; a second use finds the pocket empty
    P.o.script = b => { b.input = { speedK: 0 }; };
    await sleep(200);
    const used = Q.wait('itemUsed', m => m.slot === P.slot);
    const u = await P.net.action('use'); assert.equal(u.ok, true, u.reason);
    assert.equal((await used).kind, it.kind);
    assert.equal((await P.net.action('use')).reason, 'no_item');
  } finally { await c.close(); }
});

test('a client cannot pick up an item from afar, and a roller widens the trail', async () => {
  const c = await setup({ itemFirst: [60, 61] }); // no automatic items: place one by hand
  try {
    const m = c.m(), items = m.items;
    await until(() => c.A.net.serverNow() > c.A.startAt + 200, 4000);
    const far = items._spawn('roller', 10, 0, 0, performance.now(), -1);
    // a modded client claims to be standing on it: the move is refused, so is the pick-up
    c.A.o.cheat = st => Object.assign(st, { x: 10, z: 0 });
    await c.A.wait('correction'); c.A.o.cheat = null;
    await sleep(300);
    assert.ok(items.items.has(far.id), 'still there'); assert.equal(m.P[c.A.slot].item, null);
    // a roller in the pocket: the trail paints about 2.6 times as wide
    const p = m.P[c.A.slot]; p.item = 'roller';
    const paintRun = async () => { const before = m.cov.count[c.A.slot]; c.A.o.script = b => { b.input = { yaw: Math.PI / 2, speedK: 1 }; }; await sleep(900); c.A.o.script = b => { b.input = { speedK: 0 }; }; await sleep(200); return m.cov.count[c.A.slot] - before; };
    const plain = await paintRun();
    assert.equal((await c.A.net.action('use')).ok, true);
    const wide = await paintRun();
    assert.ok(wide > plain * 1.8, 'roller trail ' + wide + ' cells vs ' + plain);
  } finally { await c.close(); }
});

test('a trap flattens the next rival over it', async () => {
  const c = await setup({ itemFirst: [60, 61] });
  try {
    const m = c.m(); await until(() => c.A.net.serverNow() > c.A.startAt + 200, 4000);
    // walk out to open floor and leave the trap there
    goTo(c.A, 6, -6); await until(() => Math.hypot(c.A.body.x - 6, c.A.body.z + 6) < 0.5, 8000);
    m.P[c.A.slot].item = 'trap';
    const used = await c.A.net.action('use'); assert.equal(used.ok, true);
    goTo(c.A, 12, -2);
    const trap = [...m.items.traps.values()][0]; assert.ok(trap);
    // the rival walks over it
    const flat = c.A.wait('flat', x => x.slot === c.B.slot, 15000);
    goTo(c.B, trap.x, trap.z);
    const f = await flat; assert.equal(f.by, c.A.slot);
    assert.ok(m.P[c.B.slot].flatUntil > 0);
  } finally { await c.close(); }
});
