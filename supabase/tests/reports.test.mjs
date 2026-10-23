// Tests for supabase/migrations/*_reports.sql (reporting a player, and the dashboard's side of it) on a plain local Postgres, with
// tests/local_stub.sql standing in for Supabase and every migration before it run. Calls run the way Supabase runs them.
//   PGURL=postgres://postgres@localhost:54329/rmtest node --test supabase/tests/reports.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import pg from 'pg';

const db = new pg.Pool({ connectionString: process.env.PGURL || 'postgres://postgres@localhost:54329/rmtest', max: 4 });
const uid = () => randomUUID();
const now = () => Math.floor(Date.now() / 1000);
const player = id => ({ sub: id, role: 'authenticated', aal: 'aal1', amr: [{ method: 'anonymous', timestamp: now() }] });
const SID = new Map();
const signedIn = id => ({ sub: id, role: 'authenticated', aal: 'aal2', session_id: SID.get(id), amr: [{ method: 'password', timestamp: now() - 65 }, { method: 'totp', timestamp: now() - 60 }] });
async function as(claims, sql, params = [], role = 'authenticated') {
  const c = await db.connect();
  try {
    await c.query('begin');
    await c.query('select set_config($1, $2, true)', ['request.jwt.claims', JSON.stringify(claims || { role })]);
    await c.query('set local role ' + role);
    const r = await c.query(sql, params); await c.query('commit'); return r.rows;
  } catch (e) { await c.query('rollback').catch(() => {}); throw e; } finally { c.release(); }
}
const call = async (claims, fn, args = [], role) => (await as(claims, 'select public.' + fn + '(' + args.map((_, i) => '$' + (i + 1)).join(', ') + ') as r', args, role))[0].r;
const q = async (sql, params) => (await db.query(sql, params)).rows;
let seq = 0;
const suffix = () => String(Date.now() * 100 + (seq++ % 100)).slice(-8).replace(/[0-9]/g, d => 'bcdfghjlmn'[d]);
async function newUser(email) {
  const id = uid(), sid = uid(); await q('insert into auth.users (id, email, is_anonymous) values ($1, $2, $3)', [id, email || null, !email]);
  await q('insert into auth.sessions (id, user_id) values ($1, $2)', [sid, id]); SID.set(id, sid); return id;
}
async function newPlayer(base) {
  const id = await newUser(null);
  const me = await call(player(id), 'rm_me', [base + '_' + suffix(), {}, 3]); assert.equal(me.ok, true, JSON.stringify(me));
  return { id, name: me.name, code: me.code, c: player(id) };
}
const rejects = (p, re) => assert.rejects(p, e => (re.test(e.message) || (assert.fail('unexpected error: ' + e.message), false)));
let A;
test.before(async () => {
  const id = await newUser('boss_' + suffix() + '@example.com'); await q("insert into public.rm_admins (id, note) values ($1, 'test')", [id]);
  A = { id, c: signedIn(id) };
});
test.after(() => db.end());

test('the reports table is closed to the app; reporting goes through rm_report only', async () => {
  const a = await newPlayer('Ada');
  await rejects(as(a.c, 'select * from public.reports'), /permission denied/);
  await rejects(as(a.c, "insert into public.reports (reported, reported_name, reason, place) values ($1, 'x', 'name', 'friends')", [a.id]), /permission denied/);
  await rejects(call(null, 'rm_report', [a.id, 'name'], 'anon'), /permission denied/);
  await rejects(call(a.c, 'adm_reports', ['open', 10]), /not an admin/);
  await rejects(call(a.c, 'adm_reset_name', [a.id]), /not an admin/);
});

test('a report is kept with the name at the time, once per open pair, and can block in the same step', async () => {
  const a = await newPlayer('Ada'), b = await newPlayer('Bob');
  assert.deepEqual(await call(a.c, 'rm_report', [b.id, 'cheating', 'recent', 'kept flying through walls']), { ok: true, blocked: false });
  assert.deepEqual(await call(a.c, 'rm_report', [b.id, 'bullying', 'match', null]), { ok: true, blocked: false }); // (the same open report, updated)
  let rows = await q('select * from public.reports where reporter = $1', [a.id]);
  assert.equal(rows.length, 1); assert.equal(rows[0].reason, 'bullying'); assert.equal(rows[0].place, 'match'); assert.equal(rows[0].note, 'kept flying through walls'); assert.equal(rows[0].reported_name, b.name);
  // reporting with Block: they're blocked, and a friendship between them ends
  const c = await newPlayer('Cy');
  await call(a.c, 'rm_add_friend', [c.code]); await call(c.c, 'rm_add_friend', [a.code]);
  assert.equal((await q('select count(*)::int n from public.friendships where (a = $1 and b = $2) or (a = $2 and b = $1)', [a.id, c.id]))[0].n, 1);
  assert.deepEqual(await call(a.c, 'rm_report', [c.id, 'name', 'friends', '', true]), { ok: true, blocked: true });
  assert.equal((await q('select count(*)::int n from public.blocks where blocker = $1 and blocked = $2', [a.id, c.id]))[0].n, 1);
  assert.equal((await q('select count(*)::int n from public.friendships where (a = $1 and b = $2) or (a = $2 and b = $1)', [a.id, c.id]))[0].n, 0);
  assert.equal((await q("select note from public.reports where reporter = $1 and reported = $2", [a.id, c.id]))[0].note, null); // (an empty line is no line)
});

test('bad reports are refused', async () => {
  const a = await newPlayer('Ada'), b = await newPlayer('Bob');
  assert.deepEqual(await call(a.c, 'rm_report', [a.id, 'name']), { ok: false, why: 'self' });
  assert.deepEqual(await call(a.c, 'rm_report', [uid(), 'name']), { ok: false, why: 'not_found' });
  assert.deepEqual(await call(a.c, 'rm_report', [b.id, 'spam']), { ok: false, why: 'reason' });
  const long = 'x'.repeat(500); assert.equal((await call(a.c, 'rm_report', [b.id, 'other', 'party', long])).ok, true);
  assert.equal((await q('select char_length(note) n, place from public.reports where reporter = $1', [a.id]))[0].n, 200);
  // at most 20 reports an hour from one player
  let last; for (let i = 0; i < 21; i++) { const x = await newPlayer('Rep'); last = await call(a.c, 'rm_report', [x.id, 'other']); }
  assert.deepEqual(last, { ok: false, why: 'slow_down' });
});

test('three different players reporting a name swaps it for a neutral one and asks for a new one', async () => {
  const bad = await newPlayer('Meanie'), r = [await newPlayer('R1'), await newPlayer('R2'), await newPlayer('R3')];
  await call(r[0].c, 'rm_report', [bad.id, 'name']); await call(r[1].c, 'rm_report', [bad.id, 'cheating']); await call(r[2].c, 'rm_report', [bad.id, 'name']);
  assert.equal((await q('select name from public.profiles where id = $1', [bad.id]))[0].name, bad.name); // (two name reports, one cheating: not yet)
  await call(r[1].c, 'rm_report', [bad.id, 'name']);
  const [p] = await q('select name, needs_name from public.profiles where id = $1', [bad.id]);
  assert.match(p.name, /^player_[0-9a-f]{8}$/); assert.equal(p.needs_name, true);
  const me = await call(player(bad.id), 'rm_me', [null, null, null]); assert.equal(me.needs_name, true);
  assert.equal((await call(player(bad.id), 'rm_rename', ['Nicer_' + suffix()])).ok, true);
});

test('the dashboard lists open reports, closes them, and resets a name', async () => {
  const bad = await newPlayer('Grump'), a = await newPlayer('Ada'), b = await newPlayer('Bob');
  await call(a.c, 'rm_report', [bad.id, 'bullying', 'match', 'rude emotes every round']); await call(b.c, 'rm_report', [bad.id, 'name', 'recent']);
  const list = await call(A.c, 'adm_reports', ['open', 500]), mine = list.filter(x => x.reported === bad.id);
  assert.equal(mine.length, 2); assert.equal(mine[0].open_on_them, 2); assert.equal(mine[0].reported_name, bad.name);
  assert.ok(mine.some(x => x.reporter_name === a.name && x.note === 'rude emotes every round'));
  const r = await call(A.c, 'adm_reset_name', [bad.id]); assert.equal(r.ok, true); assert.match(r.name, /^player_/);
  assert.equal((await q('select needs_name from public.profiles where id = $1', [bad.id]))[0].needs_name, true);
  assert.deepEqual(await call(A.c, 'adm_report_close', [mine[0].id, 'renamed', true]), { ok: true, closed: 2 });
  assert.equal((await call(A.c, 'adm_reports', ['open', 500])).filter(x => x.reported === bad.id).length, 0);
  const closed = (await call(A.c, 'adm_reports', ['closed', 500])).filter(x => x.reported === bad.id);
  assert.equal(closed.length, 2); assert.ok(closed.every(x => x.outcome === 'renamed' && x.name_when_reported === bad.name));
  assert.deepEqual(await call(A.c, 'adm_report_close', [mine[0].id, 'banished']), { ok: false, why: 'outcome' });
  const log = await q("select action from public.rm_audit where target = $1 order by id", [bad.id]); assert.deepEqual(log.map(x => x.action), ['reset_name', 'report_close']);
  assert.deepEqual(await call(A.c, 'adm_reset_name', [A.id]), { ok: false, why: 'missing' }); // (an admin with no profile)
});

test('deleting a player takes their reports with them; a reporter who goes leaves the report', async () => {
  const bad = await newPlayer('Gone'), a = await newPlayer('Ada');
  await call(a.c, 'rm_report', [bad.id, 'other']);
  await q('delete from auth.users where id = $1', [a.id]);
  const [r] = await q('select reporter from public.reports where reported = $1', [bad.id]); assert.equal(r.reporter, null);
  await q('delete from auth.users where id = $1', [bad.id]);
  assert.equal((await q('select count(*)::int n from public.reports where reported = $1', [bad.id]))[0].n, 0);
});
