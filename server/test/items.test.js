// Pick-ups: the server places them on its own schedule at the stage's power spots, decides who picks one up from the
// validated positions, keeps the pockets, checks every use and tells everyone.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { performance } from 'node:perf_hooks';
import { startServer, makeBots, until, sleep, matchOf } from './helpers/harness.js';
import { flatLayout } from './helpers/layouts.js';

async function setup(rules, look) {
  const srv = await startServer(Object.assign({ items: true, matchT: 30, itemFirst: [0.3, 0.4], itemEvery: [0.5, 0.6] }, rules));
  const [A, B] = makeBots(srv, 2, { behavior: 'script', layoutFor: () => flatLayout(26.4), prefix: 'it', look: look || { iv: 2 } });
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

test('a trap knocks out the next rival over it', async () => {
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
    const ko = c.A.wait('ko', x => x.slot === c.B.slot, 15000);
    goTo(c.B, trap.x, trap.z);
    const f = await ko; assert.equal(f.by, c.A.slot); assert.equal(f.reason, 'trap');
  } finally { await c.close(); }
});

// ---------------------------------------------------------------------------------------------- (v427) the game's items online
const still = b => { b.o.script = x => { x.input = { speedK: 0 }; }; };
const live = c => until(() => c.A.net.serverNow() > c.A.startAt + 300, 5000);
// put the two bots a few metres apart, out in the open
async function apart(c, d = 4) {
  goTo(c.A, -d / 2, -8); goTo(c.B, d / 2, -8);
  await until(() => Math.hypot(c.A.body.x + d / 2, c.A.body.z + 8) < 1 && Math.hypot(c.B.body.x - d / 2, c.B.body.z + 8) < 1, 20000); // (round the wall from B's side: it takes a while)
  still(c.A); still(c.B); await sleep(700);
}

test('everyone starts with the item they picked; an older game in the match turns items off', async () => {
  const c = await setup({ itemFirst: [60, 61] }, { iv: 2, it: 'boom', sp: 'storm' });
  try {
    const m = c.m(); assert.ok(m.items, 'items on');
    assert.equal(m.P[c.A.slot].item, 'boom'); assert.equal(m.P[c.A.slot].special, 'storm');
  } finally { await c.close(); }
  const d = await setup({}, {}); // (no iv: a game from before v427)
  try { assert.equal(d.m().items, null, 'no items with a game that cannot show them'); } finally { await d.close(); }
});

test('a boomerang hit, claimed, is ruled a knock-out; with no boomerang out it is refused', async () => {
  const c = await setup({ itemFirst: [60, 61] });
  try {
    const m = c.m(); await live(c); await apart(c, 5);
    const pA = m.P[c.A.slot];
    const none = await c.A.net.action('hit', { k: 'boom', target: c.B.slot, x: c.B.body.x, y: 0, z: c.B.body.z });
    assert.equal(none.ok, false); assert.equal(none.reason, 'no_effect');
    pA.item = 'boom';
    const used = c.B.wait('itemUsed', x => x.slot === c.A.slot && x.kind === 'boom');
    assert.equal((await c.A.net.action('use', { yaw: Math.PI / 2, curve: 1 })).ok, true);
    const u = await used; assert.equal(u.curve, 1);
    await sleep(400);
    const ko = c.B.wait('ko', x => x.slot === c.B.slot);
    const r = await c.A.net.action('hit', { k: 'boom', target: c.B.slot, x: c.B.body.x, y: 0.5, z: c.B.body.z });
    assert.equal(r.ok, true, r.reason);
    const k = await ko; assert.equal(k.by, c.A.slot); assert.equal(k.reason, 'boom');
  } finally { await c.close(); }
});

test('a hit claimed from too far is refused', async () => {
  const c = await setup({ itemFirst: [60, 61] });
  try {
    const m = c.m(); await live(c); await apart(c, 8);
    m.P[c.A.slot].item = 'whirl'; assert.equal((await c.A.net.action('use')).ok, true);
    await sleep(1200);
    const r = await c.A.net.action('hit', { k: 'crush', target: c.B.slot });
    assert.equal(r.ok, false); assert.equal(r.reason, 'far', 'a whirlwind reaches about 2.4 m, the rival is 8 m off');
  } finally { await c.close(); }
});

test('turret globs drain the paint tank, three in a row stun, and a dry rival is knocked out', async () => {
  const c = await setup({ itemFirst: [60, 61] });
  try {
    const m = c.m(); await live(c); await apart(c, 6);
    m.P[c.A.slot].item = 'turret'; assert.equal((await c.A.net.action('use')).ok, true);
    const pB = m.P[c.B.slot], p0 = pB.paint, shots = [];
    c.B.on('shot', x => shots.push(x));
    for (let i = 0; i < 3; i++) { assert.equal((await c.A.net.action('hit', { k: 'shot', target: c.B.slot, x: c.B.body.x, y: 0.4, z: c.B.body.z })).ok, true); await sleep(60); }
    await until(() => shots.length >= 3, 3000);
    assert.ok(pB.paint < p0 - 0.15, 'paint ' + p0 + ' -> ' + pB.paint);
    assert.equal(shots[2].stun, true, 'the third in a row stuns');
    await sleep(1700); pB.paint = 0;
    const ko = c.B.wait('ko', x => x.slot === c.B.slot);
    assert.equal((await c.A.net.action('hit', { k: 'shot', target: c.B.slot, x: c.B.body.x, y: 0.4, z: c.B.body.z })).ok, true);
    assert.equal((await ko).reason, 'shot');
  } finally { await c.close(); }
});

test('the orb: whoever reaches it gets their special; a Flash Freeze freezes the rival, who can tap out a second early', async () => {
  const c = await setup({ itemFirst: [60, 61], orbFirst: [0.3, 0.4] }, { iv: 2, sp: 'freeze' });
  try {
    const m = c.m();
    const o = await c.A.wait('orbSpawn', undefined, 6000);
    const taken = c.B.wait('orbTaken', x => x.id === o.id, 15000);
    goTo(c.A, o.x, o.z); still(c.B);
    const t = await taken; assert.equal(t.slot, c.A.slot); assert.equal(t.gift, 'freeze');
    assert.equal(m.P[c.A.slot].orb, 'freeze');
    still(c.A); await sleep(200);
    const fr = c.B.wait('freeze', undefined, 4000);
    assert.equal((await c.A.net.action('use', { orb: 1 })).ok, true);
    const f = await fr; assert.deepEqual(f.slots, [c.B.slot]);
    const pB = m.P[c.B.slot]; assert.ok(pB.frozen);
    const j = await c.B.net.action('jump'); assert.equal(j.ok, false); assert.equal(j.reason, 'frozen');
    assert.equal((await c.B.net.action('thaw')).ok, true);
    assert.ok(pB.frozen.until <= f.until - 900, 'a second sooner at most: ' + (f.until - pB.frozen.until));
  } finally { await c.close(); }
});

test('paint claims stamp the canvas, within what the effect can paint', async () => {
  const c = await setup({ itemFirst: [60, 61] });
  try {
    const m = c.m(); await live(c); await apart(c, 6);
    const before = m.cov.count[c.A.slot];
    const no = await c.A.net.action('paint', { k: 'bomb', pts: [[c.A.body.x, 0, c.A.body.z]] }); assert.equal(no.reason, 'no_effect');
    m.P[c.A.slot].orb = 'bomb'; assert.equal((await c.A.net.action('use', { orb: 1 })).ok, true);
    await sleep(1800);
    assert.equal((await c.A.net.action('paint', { k: 'bomb', pts: [[c.A.body.x, 0, c.A.body.z]] })).ok, true);
    assert.ok(m.cov.count[c.A.slot] > before + 200, 'a bomb paints a wide circle');
    assert.equal((await c.A.net.action('paint', { k: 'bomb', pts: [[c.A.body.x, 0, c.A.body.z]] })).reason, 'budget', 'once');
  } finally { await c.close(); }
});

test('an effect\'s look is relayed to the others, and big ones are refused', async () => {
  const c = await setup({ itemFirst: [60, 61] });
  try {
    await live(c);
    const got = c.B.wait('fx', x => x.slot === c.A.slot && x.k === 'drop');
    c.A.net.tell('fx', { k: 'drop', d: [1.5, 0, -2] });
    assert.deepEqual((await got).d, [1.5, 0, -2]);
    const big = await c.A.net.action('fx', { k: 'drop', d: 'x'.repeat(500) }); assert.equal(big.reason, 'big');
  } finally { await c.close(); }
});

test('an orb its holder never used comes out of them when they are knocked out, for anyone to take', async () => {
  const c = await setup({ itemFirst: [60, 61], orbFirst: [60, 61] });
  try {
    const m = c.m(); await live(c); await apart(c, 5);
    const pB = m.P[c.B.slot]; pB.orb = 'rocket'; pB.orbUntil = Infinity;
    const spawned = c.A.wait('orbSpawn', x => x.dropped === c.B.slot, 4000);
    m._ko(pB, m.P[c.A.slot], 'pound');
    const o = await spawned; assert.ok(Math.hypot(o.x - c.B.body.x, o.z - c.B.body.z) < 1.5, 'where they went down');
    assert.equal(pB.orb, null);
    const taken = c.B.wait('orbTaken', x => x.id === o.id, 10000);
    goTo(c.A, o.x, o.z);
    const t = await taken; assert.equal(t.slot, c.A.slot);
  } finally { await c.close(); }
});

test('Deep Pockets online: a second item goes in the other pocket, a third drops the older, and either pocket can be used', async () => {
  const c = await setup({ itemFirst: [60, 61] }, { iv: 3, it: 'roller', sk: 'pockets' }); // (no automatic items: placed by hand)
  try {
    const m = c.m(), items = m.items, p = m.P[c.A.slot];
    assert.equal(p.two, true, 'a Deep Pockets player with a game that knows of the second pocket');
    assert.equal(p.item, 'roller', 'starts with the item picked');
    await until(() => c.A.net.serverNow() > c.A.startAt + 200, 4000);
    const grab = async kind => {
      const at = { x: c.A.body.x + 1.6, z: c.A.body.z };
      const it = items._spawn(kind, at.x, 0, at.z, performance.now(), -1);
      const taken = c.B.wait('itemTaken', x => x.id === it.id, 8000);
      goTo(c.A, at.x, at.z); const t = await taken; c.A.o.script = b => { b.input = { speedK: 0 }; }; await sleep(250); return t;
    };
    const t1 = await grab('trap');
    assert.deepEqual([t1.h1, t1.h2], ['roller', 'trap'], 'both pockets full');
    assert.deepEqual([p.item, p.item2], ['roller', 'trap']);
    const dropped = c.B.wait('itemSpawn', x => x.kind === 'roller' && x.dropped === c.A.slot, 15000);
    const t2 = await grab('whirl');
    assert.deepEqual([t2.h1, t2.h2], ['trap', 'whirl'], 'a third: the older goes');
    assert.equal((await dropped).kind, 'roller', 'the older is dropped on the stage');
    // the second pocket
    const used = c.B.wait('itemUsed', x => x.slot === c.A.slot);
    const u = await c.A.net.action('use', { second: 1 }); assert.equal(u.ok, true, u.reason);
    const um = await used; assert.equal(um.kind, 'whirl'); assert.deepEqual([um.h1, um.h2 ?? null], ['trap', null]);
    assert.deepEqual([p.item, p.item2], ['trap', null]);
  } finally { await c.close(); }
});
