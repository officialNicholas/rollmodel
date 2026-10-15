// Map consensus: every client generates the stage from the server's seed and uploads it; the match starts only when
// all of them match. Anything else cancels it and puts the honest players back in the queue.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { startServer, makeBots, until, sleep } from './helpers/harness.js';

async function setup(n, mode, tampers = {}, rules = {}) {
  const srv = await startServer(rules);
  const bots = makeBots(srv, n, { behavior: 'still' });
  bots.forEach((b, i) => { if (tampers[i]) Object.assign(b.o, tampers[i]); });
  await Promise.all(bots.map(b => b.connect()));
  for (const b of bots) await b.net.queue(mode);
  return { srv, bots };
}
const done = async ({ srv, bots }) => { for (const b of bots) b.close(); await srv.close(); };

test('matching layouts start the match', async () => {
  const ctx = await setup(2, 'duel');
  try {
    const s = await Promise.all(ctx.bots.map(b => b.wait('start')));
    assert.equal(s[0].layoutHash, s[1].layoutHash);
  } finally { await done(ctx); }
});

test('a layout that differs by one box cancels the match; honest players go back to the queue, the odd one is flagged', async () => {
  // three players, so the majority shows who is out of step
  const ctx = await setup(3, 'trio', { 2: { tamper: L => { L.boxes[0][1] += 0.5; return L; } } });
  try {
    const cancelled = Promise.all(ctx.bots.map(b => b.wait('matchCancelled')));
    const requeued = Promise.all(ctx.bots.slice(0, 2).map(b => b.wait('queued', m => m.requeued)));
    const c = await cancelled;
    assert.ok(c.every(m => m.reason === 'layout_mismatch'));
    const re = await requeued; assert.ok(re.every(m => m.mode === 'trio'));
    await sleep(100);
    const odd = await ctx.srv.store.get(ctx.bots[2].id), honest = await ctx.srv.store.get(ctx.bots[0].id);
    assert.ok(odd.flags.some(f => f.reason === 'layout_mismatch'), 'the tamperer is flagged');
    assert.equal(honest.flags.length, 0, 'the others are not');
    assert.equal(ctx.srv.mm.sizes().trio, 2, 'the two honest players are queued again, the tamperer is not');
    assert.equal(ctx.srv.stats.matchesCancelled, 1);
  } finally { await done(ctx); }
});

test('a client that claims the right hash for a different layout is caught (the server hashes it itself)', async () => {
  const ctx = await setup(2, 'duel', { 1: { sendLayout: false } });
  try {
    const f = await ctx.bots[1].wait('matchFound').catch(() => null);
    await until(() => ctx.bots[1].layout, 3000);
    const honest = ctx.bots[1].layout, forged = JSON.parse(JSON.stringify(honest)); forged.holes = [];
    // sends the honest hash with a layout that has no holes
    ctx.bots[1].net._sendJ({ t: 'layout', m: ctx.bots[1].net.match.id, hash: ctx.bots[1].net.layoutHash(honest), layout: forged });
    const c = await ctx.bots[0].wait('matchCancelled'); assert.equal(c.reason, 'layout_mismatch'); assert.ok(f);
  } finally { await done(ctx); }
});

test('a broken layout (NaN, wrong arena) cancels the match', async () => {
  const ctx = await setup(2, 'duel', { 1: { tamper: L => { L.boxes[0][2] = NaN; return L; } } });
  try { const c = await ctx.bots[0].wait('matchCancelled'); assert.equal(c.reason, 'layout_mismatch'); } finally { await done(ctx); }
  const ctx2 = await setup(2, 'duel', { 0: { tamper: L => { L.arena = 33; return L; } } });
  try { const c = await ctx2.bots[1].wait('matchCancelled'); assert.equal(c.reason, 'layout_mismatch'); } finally { await done(ctx2); }
});

test('a client that never sends its layout times out the match', async () => {
  const ctx = await setup(2, 'duel', { 1: { sendLayout: false } }, { layoutTimeout: 1.2 });
  try {
    const requeued = ctx.bots[0].wait('queued', m => m.requeued, 5000);
    const c = await ctx.bots[0].wait('matchCancelled', () => true, 5000); assert.equal(c.reason, 'layout_timeout');
    await requeued;
  } finally { await done(ctx); }
});

test('layouts for a match you are not in are refused', async () => {
  const ctx = await setup(2, 'duel', { 1: { sendLayout: false } });
  try {
    await ctx.bots[1].wait('matchFound');
    const err = ctx.bots[1].wait('error', m => m.code === 'not_in_match');
    ctx.bots[1].net._sendJ({ t: 'layout', m: 'm_somebodyelse', hash: '0', layout: ctx.bots[1].layout });
    await err;
  } finally { await done(ctx); }
});
