// Tests for supabase/migrations/*_saves.sql (progress kept with an account) on a plain local Postgres, with tests/local_stub.sql
// standing in for Supabase, after the friends and accounts migrations. Calls run as "authenticated" (or "anon") with the caller's claims.
//   PGURL=postgres://postgres@localhost:54329/rmtest node --test supabase/tests/saves.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import pg from 'pg';

const db = new pg.Pool({ connectionString: process.env.PGURL || 'postgres://postgres@localhost:54329/rmtest', max: 4 });
async function as(user, sql, params = [], role = 'authenticated') {
  const c = await db.connect();
  try {
    await c.query('begin');
    await c.query('select set_config($1, $2, true)', ['request.jwt.claims', user ? JSON.stringify({ sub: user, role }) : JSON.stringify({ role })]);
    await c.query('set local role ' + role);
    const r = await c.query(sql, params); await c.query('commit'); return r.rows;
  } catch (e) { await c.query('rollback').catch(() => {}); throw e; } finally { c.release(); }
}
const call = async (user, fn, args = [], role) => (await as(user, 'select public.' + fn + '(' + args.map((_, i) => '$' + (i + 1)).join(', ') + ') as r', args, role))[0].r;
let seq = 0;
const suffix = () => String(Date.now() * 100 + (seq++ % 100)).slice(-8).replace(/[0-9]/g, d => 'bcdfghjlmn'[d]);
async function player(base) {
  const id = randomUUID(); await db.query('insert into auth.users (id) values ($1)', [id]);
  const me = await call(id, 'rm_me', [base + '_' + suffix(), {}, 1]); assert.equal(me.ok, true, JSON.stringify(me)); return { id, ...me };
}
// a player made into a real account, as the game does it: an email and password set on them, then the details
async function account(base) {
  const p = await player(base);
  await db.query("update auth.users set is_anonymous = false, email = 'u' || replace(id::text, '-', '') || '@rollmodel.invalid' where id = $1", [p.id]);
  const r = await call(p.id, 'rm_account_save', ['Ada', 'Blob', '1990-12-31', 'v306']); assert.equal(r.ok, true, JSON.stringify(r));
  return p;
}
const put = (u, data) => call(u.id, 'rm_save_put', [JSON.stringify(data)]);
const get = u => call(u.id, 'rm_save_get', []);
const prog = (xp, more) => ({ xp, drops: 340, level: 2, owned: ['flower', 'fangs'], tut: { ph: 'done' }, introDone: 1, name: 'Ada', ...more });

test.after(() => db.end());

test('only a real account keeps progress', async () => {
  const anon = await player('Anon');
  assert.deepEqual(await put(anon, prog(10)), { ok: false, why: 'no_account' });
  // a password set but the account never finished (no details): still not an account
  const half = await player('Half');
  await db.query("update auth.users set is_anonymous = false where id = $1", [half.id]);
  assert.deepEqual(await put(half, prog(10)), { ok: false, why: 'no_account' });
  const a = await account('Real');
  assert.equal((await put(a, prog(10))).ok, true);
});

test('what goes up comes back, and nothing kept reads as nothing', async () => {
  const a = await account('Round');
  assert.deepEqual(await get(a), { ok: true, data: null });
  const before = Date.now(), p = prog(1234, { world: { sewer: { best: 61, wins: 3, played: 5 } }, tt: { wk: 1, b: {}, n: {} } });
  const r = await put(a, p); assert.equal(r.ok, true); assert.ok(r.at >= before - 5000 && r.at <= Date.now() + 5000, String(r.at));
  const g = await get(a);
  assert.equal(g.ok, true); assert.deepEqual(g.data, p); assert.equal(Number(g.xp), 1234); assert.equal(Number(g.at), Number(r.at));
  // a newer copy replaces it
  const p2 = prog(1300, { drops: 10 }); assert.equal((await put(a, p2)).ok, true); assert.deepEqual((await get(a)).data, p2);
});

test('a phone left behind cannot wipe out more progress', async () => {
  const a = await account('Two');
  assert.equal((await put(a, prog(500))).ok, true);
  const r = await put(a, prog(300, { drops: 999999 }));
  assert.equal(r.ok, false); assert.equal(r.why, 'behind'); assert.equal(Number(r.xp), 500); assert.ok(r.at > 0);
  assert.equal((await get(a)).data.xp, 500);
  // the same rank: the newer copy wins (a purchase on either phone)
  assert.equal((await put(a, prog(500, { drops: 1 }))).ok, true); assert.equal((await get(a)).data.drops, 1);
  // a copy with no rank at all counts as none
  assert.equal((await put(a, { drops: 5 })).why, 'behind');
  assert.equal((await put(a, prog('9999'))).why, 'behind'); // (a rank must be a number)
});

test('only an object, and not too big', async () => {
  const a = await account('Shape');
  for (const bad of [[1, 2], 'save', 12, true]) assert.deepEqual(await put(a, bad), { ok: false, why: 'bad' }, JSON.stringify(bad));
  assert.deepEqual(await call(a.id, 'rm_save_put', [null]), { ok: false, why: 'bad' });
  assert.deepEqual(await put(a, prog(1, { junk: 'x'.repeat(200001) })), { ok: false, why: 'too_big' });
  assert.equal((await put(a, prog(1, { junk: 'x'.repeat(150000) }))).ok, true); // (a big save is fine)
  // a silly rank is kept in range
  assert.equal((await put(a, prog(1e300))).ok, true); assert.equal(Number((await get(a)).xp), 1e15);
  const b = await account('Neg'); assert.equal((await put(b, prog(-50))).ok, true); assert.equal(Number((await get(b)).xp), 0);
});

test('your progress is yours alone', async () => {
  const a = await account('Mine'), b = await account('Theirs');
  await put(a, prog(77, { secret: 'a' }));
  assert.deepEqual(await get(b), { ok: true, data: null });
  await assert.rejects(as(b.id, 'select * from public.saves'), /permission denied/);
  await assert.rejects(as(b.id, "update public.saves set xp = 0"), /permission denied/);
  await assert.rejects(call(null, 'rm_save_get', [], 'anon'), /permission denied/);
  await assert.rejects(call(null, 'rm_save_put', [JSON.stringify(prog(1))], 'anon'), /permission denied/);
  // signed in as no one (a token without a user): refused
  await assert.rejects(as(null, 'select public.rm_save_get()'), /sign in first/);
});

test('deleting the account deletes its progress', async () => {
  const a = await account('Gone');
  assert.equal((await put(a, prog(42))).ok, true);
  assert.equal((await call(a.id, 'rm_delete_me', [])).ok, true);
  assert.equal((await db.query('select count(*)::int as n from public.saves where id = $1', [a.id])).rows[0].n, 0);
});

test('240 saves an hour at the most', async () => {
  const a = await account('Busy');
  for (let i = 0; i < 240; i++) assert.equal((await put(a, prog(i))).ok, true, 'save ' + i);
  assert.deepEqual(await put(a, prog(240)), { ok: false, why: 'slow_down' });
  assert.equal((await get(a)).data.xp, 239);
});
