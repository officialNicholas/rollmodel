// Tests for supabase/migrations/*_accounts.sql (usernames and accounts) on a plain local Postgres, with tests/local_stub.sql
// standing in for Supabase. Calls run the way Supabase runs them: as "authenticated" (or "anon") with the caller's JWT claims.
//   PGURL=postgres://postgres@localhost:54329/rmtest node --test supabase/tests/accounts.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import pg from 'pg';

const db = new pg.Pool({ connectionString: process.env.PGURL || 'postgres://postgres@localhost:54329/rmtest', max: 4 });
const uid = () => randomUUID();
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
const anonCall = (fn, args) => call(null, fn, args, 'anon');
let seq = 0;
const suffix = () => String(Date.now() * 100 + (seq++ % 100)).slice(-8).replace(/[0-9]/g, d => 'bcdfghjlmn'[d]);
async function newUser() { const id = uid(); await db.query('insert into auth.users (id) values ($1)', [id]); return id; }
async function player(base) { const id = await newUser(), name = base + '_' + suffix(); const me = await call(id, 'rm_me', [name, {}, 1]); assert.equal(me.ok, true, JSON.stringify(me)); return { id, ...me }; }
// what Supabase does when the game sets an email and password on an anonymous player
const makePermanent = id => db.query("update auth.users set is_anonymous = false, email = 'u' || replace(id::text, '-', '') || '@rollmodel.invalid' where id = $1", [id]);
const why = async n => (await db.query('select public._uname_why($1) as w', [n])).rows[0].w;

test.after(() => db.end());

test('username rules: length, characters, reserved names', async () => {
  for (const n of ['Bob', 'Blobby_McBlob', 'x_Painter_99', 'ROLLER', 'a1b']) assert.equal(await why(n), null, n);
  assert.equal(await why('ab'), 'short');
  assert.equal(await why('abcdefghijklmnopq'), 'long');
  for (const n of ['Big Blob', 'blob!', 'émile', '1234', '___']) assert.equal(await why(n), 'chars', n);
  for (const n of ['admin', 'Admin7', 'TheAdmin', 'moderator', 'Official_Blob', 'RollModel', 'bloop', 'Player123', 'player_12']) assert.equal(await why(n), 'reserved', n);
  assert.equal(await why('Badminton'), null); // (admin inside a word is fine)
});

test('username rules: bad words, however they are spelled', async () => {
  const bad = ['fuckface', 'FuckFace', 'fUcK', 'Sh1tHead', 'b1tch', 'BigDick', 'big_dick', 'Dick99', 'd_i_c_k', 'BadAss', 'ass_kicker', '4ss_man',
    'xXsexyXx', 'SexyBlob', 'nazi_blob', 'h1tler', 'porn_star', 'tits_mcgee', 'p3nis', 'kys_now', 'The_cum_man', 'Damn_It', 'BloodyHell', 'n1gga'];
  for (const n of bad) assert.equal(await why(n), 'bad', n);
  const fine = ['Scunthorpe', 'Classy', 'Assassin', 'Peacock', 'Cockatoo', 'Dickens', 'Grape_Ape', 'Therapist', 'Hello', 'Shellfish', 'Analyst',
    'Torpedo', 'Thorny', 'Cucumber', 'Titan', 'Raccoon', 'Sussex', 'Hancock', 'Pass_It', 'Butterfly', 'Swanky'];
  for (const n of fine) assert.equal(await why(n), null, n);
});

test('a name check anyone can make, before having an account', async () => {
  const a = await player('Taken');
  assert.deepEqual(await anonCall('rm_name_check', ['Free_' + suffix()]).then(r => r.ok), true);
  assert.deepEqual(await anonCall('rm_name_check', [a.name.toUpperCase()]), { ok: false, why: 'taken' }); // (capitals don't make it different)
  assert.deepEqual(await anonCall('rm_name_check', ['ab']), { ok: false, why: 'short' });
  assert.deepEqual(await anonCall('rm_name_check', ['BigDick']), { ok: false, why: 'bad' });
  assert.equal((await call(a.id, 'rm_name_check', [a.name])).ok, true); // (your own name is yours)
  // the rest stays closed to anonymous callers
  await assert.rejects(anonCall('rm_me', ['Someone', null, null]), /permission denied/);
  await assert.rejects(anonCall('rm_account', []), /permission denied/);
  await assert.rejects(anonCall('_uname_why', ['x']), /permission denied/);
});

test('a profile is made only with a free, clean username', async () => {
  const a = await player('First');
  const id = await newUser();
  assert.deepEqual(await call(id, 'rm_me', [a.name.toLowerCase(), {}, 1]), { ok: false, why: 'taken' });
  assert.deepEqual(await call(id, 'rm_me', ['b1tch_' + suffix(), {}, 1]), { ok: false, why: 'bad' });
  assert.deepEqual(await call(id, 'rm_me', [null, {}, 1]), { ok: false, why: 'short' });
  await assert.rejects(call(id, 'rm_inbox', ['lobby']), /no profile yet/);
  const ok = await call(id, 'rm_me', ['Second_' + suffix(), {}, 1]); assert.equal(ok.ok, true);
});

test('renaming: free and clean only, and the old name is free again', async () => {
  const a = await player('Ren'), b = await player('Other');
  assert.deepEqual(await call(a.id, 'rm_rename', [b.name]), { ok: false, why: 'taken' });
  assert.deepEqual(await call(a.id, 'rm_rename', ['ShitHead']), { ok: false, why: 'bad' });
  const nn = 'Renamed_' + suffix();
  assert.deepEqual(await call(a.id, 'rm_rename', [nn]), { ok: true, name: nn });
  assert.equal((await call(a.id, 'rm_me', [null, null, null])).name, nn);
  assert.equal((await anonCall('rm_name_check', [a.name])).ok, true);
  // a player with no profile yet makes one by renaming
  const id = await newUser(), nm = 'Fresh_' + suffix();
  assert.equal((await call(id, 'rm_rename', [nm])).name, nm);
});

test('accounts: only for real (not anonymous) players, 13 or older, details kept private', async () => {
  const a = await player('Acc');
  assert.deepEqual(await call(a.id, 'rm_account_save', ['Ada', 'Lovelace', '2000-01-02', 'v1']), { ok: false, why: 'not_signed_up' });
  assert.equal(await anonCall('rm_login_email', [a.name]), null); // (no account yet: nothing to log in to)
  await makePermanent(a.id);
  const young = new Date(Date.now() - 12 * 365.25 * 864e5).toISOString().slice(0, 10);
  assert.deepEqual(await call(a.id, 'rm_account_save', ['Ada', 'Lovelace', young, 'v1']), { ok: false, why: 'age' });
  assert.deepEqual(await call(a.id, 'rm_account_save', ['', 'Lovelace', '2000-01-02', 'v1']), { ok: false, why: 'first' });
  assert.deepEqual(await call(a.id, 'rm_account_save', ['Ada', 'Love<3', '2000-01-02', 'v1']), { ok: false, why: 'last' });
  assert.deepEqual(await call(a.id, 'rm_account_save', ['Ada', 'Lovelace', '2000-01-02', 'Bad Terms!']), { ok: false, why: 'terms' });
  assert.deepEqual(await call(a.id, 'rm_account_save', ['  Ada  Maria ', "O'Brien-Lovelace", '2000-01-02', 'tos-2026-10']), { ok: true });
  const acc = await call(a.id, 'rm_account', []);
  assert.equal(acc.username, a.name); assert.equal(acc.first_name, 'Ada Maria'); assert.equal(acc.last_name, "O'Brien-Lovelace"); assert.equal(acc.birthday, '2000-01-02');
  const me = await call(a.id, 'rm_me', [null, null, null]); assert.equal(me.account, true); assert.equal(me.anon, false);
  assert.match(await anonCall('rm_login_email', [a.name.toUpperCase()]), /^u[0-9a-f]{32}@rollmodel\.invalid$/);
  await assert.rejects(as(a.id, 'select * from public.accounts'), /permission denied/);
  const b = await player('Snoop'); assert.equal(await call(b.id, 'rm_account', []), null); // (someone else sees nothing)
});

test('deleting an account takes everything with it, and frees the username', async () => {
  const a = await player('Gone'), b = await player('Stay');
  await call(a.id, 'rm_add_friend', [b.code]); await call(b.id, 'rm_add_friend', [a.code]);
  await makePermanent(a.id); await call(a.id, 'rm_account_save', ['Gone', 'Soon', '1990-05-05', 'v1']);
  assert.equal((await call(b.id, 'rm_inbox', ['lobby'])).friends.length, 1);
  assert.deepEqual(await call(a.id, 'rm_delete_me', []), { ok: true });
  assert.equal((await db.query('select count(*)::int as n from auth.users where id = $1', [a.id])).rows[0].n, 0);
  assert.equal((await db.query('select count(*)::int as n from public.accounts where id = $1', [a.id])).rows[0].n, 0);
  assert.equal((await call(b.id, 'rm_inbox', ['lobby'])).friends.length, 0);
  assert.equal((await anonCall('rm_name_check', [a.name])).ok, true);
});
