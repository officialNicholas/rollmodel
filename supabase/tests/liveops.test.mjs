// Tests for supabase/migrations/*_liveops.sql (play stats, live prices, the admin dashboard's functions) on a plain local Postgres,
// with tests/local_stub.sql standing in for Supabase. Calls run the way Supabase runs them: as "authenticated" (or "anon") with
// the caller's JWT claims, here including the assurance level (aal) and how they signed in (amr).
//   PGURL=postgres://postgres@localhost:54329/rmtest node --test supabase/tests/liveops.test.mjs
// It empties the liveops tables first (it's a throwaway test database), so the reports can be checked exactly.
import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import pg from 'pg';

const db = new pg.Pool({ connectionString: process.env.PGURL || 'postgres://postgres@localhost:54329/rmtest', max: 4 });
const uid = () => randomUUID();
const now = () => Math.floor(Date.now() / 1000);
// a caller's claims: a player (aal1, password), or an admin who also entered their authenticator code (aal2, totp) `ago` seconds back
const player = id => ({ sub: id, role: 'authenticated', aal: 'aal1', amr: [{ method: 'anonymous', timestamp: now() }] });
const SID = new Map(); // (each test user's live session, as Supabase keeps them in auth.sessions)
const signedIn = (id, { aal = 'aal2', totpAgo = 60, amr, sid } = {}) => ({ sub: id, role: 'authenticated', aal, session_id: sid || SID.get(id),
  amr: amr || [{ method: 'password', timestamp: now() - totpAgo - 5 }, ...(totpAgo == null ? [] : [{ method: 'totp', timestamp: now() - totpAgo }])] });
async function as(claims, sql, params = [], { role = 'authenticated', tz } = {}) {
  const c = await db.connect();
  try {
    await c.query('begin');
    await c.query('select set_config($1, $2, true)', ['request.jwt.claims', JSON.stringify(claims || { role })]);
    if (tz) await c.query("select set_config('timezone', $1, true)", [tz]);
    await c.query('set local role ' + role);
    const r = await c.query(sql, params); await c.query('commit'); return r.rows;
  } catch (e) { await c.query('rollback').catch(() => {}); throw e; } finally { c.release(); }
}
const call = async (claims, fn, args = [], opts) => (await as(claims, 'select public.' + fn + '(' + args.map((_, i) => '$' + (i + 1)).join(', ') + ') as r', args, opts))[0].r;
const anon = (fn, args) => call(null, fn, args, { role: 'anon' });
const track = (iid, meta, ev, claims) => claims ? call(claims, 'rm_track', [iid, meta, JSON.stringify(ev)]) : anon('rm_track', [iid, meta, JSON.stringify(ev)]);
const q = async (sql, params) => (await db.query(sql, params)).rows;
const today = () => new Date().toISOString().slice(0, 10);
const dayAgo = n => new Date(Date.now() - n * 86400000).toISOString().slice(0, 10);

let seq = 0;
const suffix = () => String(Date.now() * 100 + (seq++ % 100)).slice(-8).replace(/[0-9]/g, d => 'bcdfghjlmn'[d]);
async function newUser(email, anonymous = !email) {
  const id = uid(), sid = uid(); await q('insert into auth.users (id, email, is_anonymous) values ($1, $2, $3)', [id, email || null, anonymous]);
  await q('insert into auth.sessions (id, user_id) values ($1, $2)', [sid, id]); SID.set(id, sid); return id;
}
async function newAdmin() {
  const id = await newUser('boss_' + suffix() + '@example.com');
  await q("insert into public.rm_admins (id, note) values ($1, 'test')", [id]);
  return { id, claims: signedIn(id) };
}
// a player with a username, and with a real account (a password and the details) when asked
async function newPlayer(base = 'Sup', { account = false } = {}) {
  const id = await newUser(account ? 'u' + randomUUID().replace(/-/g, '') + '@rollmodel.invalid' : null, !account);
  const me = await call(player(id), 'rm_me', [base + '_' + suffix(), {}, 3]); assert.equal(me.ok, true, JSON.stringify(me));
  if (account) {
    await q("update auth.users set encrypted_password = 'old', last_sign_in_at = now() where id = $1", [id]);
    const r = await call(player(id), 'rm_account_save', ['Dana', 'Lee', '2001-12-31', '2026-10']); assert.equal(r.ok, true, JSON.stringify(r));
  }
  return { id, name: me.name, code: me.code };
}
const rejects = (p, re) => assert.rejects(p, e => (re.test(e.message) || (assert.fail('unexpected error: ' + e.message), false)));

let A; // the admin most tests act as
test.before(async () => {
  await q('truncate public.rm_installs, public.rm_daily, public.rm_buys, public.rm_audit, public.rm_prices');
  await q('delete from public.rm_admins');
  A = await newAdmin();
});
test.after(() => db.end());

// ------------------------------------------------------------------ who's an admin

test('only a listed admin, signed in with an authenticator code in the last 12 hours, gets in', async () => {
  const p = await newPlayer('Nosy');
  // the app's anonymous role can't even call them
  await rejects(anon('adm_whoami', []), /permission denied/);
  await rejects(anon('adm_overview', [30]), /permission denied/);
  // a player: not an admin, whatever their token says about codes
  await rejects(call(player(p.id), 'adm_overview', [30]), /not an admin/);
  await rejects(call(signedIn(p.id), 'adm_set_price', ['tophat', 1]), /not an admin/);
  assert.deepEqual(await call(signedIn(p.id), 'adm_whoami').then(w => [w.listed, w.admin, w.why]), [false, false, 'not_listed']);
  // the admin with only a password: asked for the code
  const pw = signedIn(A.id, { aal: 'aal1', totpAgo: null });
  await rejects(call(pw, 'adm_overview', [30]), /not an admin/);
  assert.deepEqual(await call(pw, 'adm_whoami').then(w => [w.listed, w.admin, w.why, w.code_at]), [true, false, 'needs_code', null]);
  // aal2 claimed but no code in amr, or no amr at all: refused
  await rejects(call(signedIn(A.id, { amr: [{ method: 'password', timestamp: now() }] }), 'adm_overview', [30]), /not an admin/);
  await rejects(call({ sub: A.id, role: 'authenticated', aal: 'aal2' }, 'adm_overview', [30]), /not an admin/);
  // the code was entered 13 hours ago: sign in again
  const old = signedIn(A.id, { totpAgo: 13 * 3600 });
  await rejects(call(old, 'adm_overview', [30]), /not an admin/);
  assert.equal((await call(old, 'adm_whoami')).why, 'stale');
  // a code time in the future (a forged or broken clock) doesn't count
  await rejects(call(signedIn(A.id, { totpAgo: -3600 }), 'adm_overview', [30]), /not an admin/);
  // the real thing
  const w = await call(A.claims, 'adm_whoami');
  assert.equal(w.admin, true); assert.equal(w.why, null); assert.equal(w.aal, 'aal2'); assert.equal(w.id, A.id); assert.match(w.email, /@example\.com$/);
  assert.ok(Math.abs(Date.parse(w.code_at) / 1000 - (now() - 60)) < 5);
  assert.equal(typeof (await call(A.claims, 'adm_overview', [30])).installs, 'number');
  // the refusal is SQLSTATE 42501, which PostgREST turns into HTTP 403
  await assert.rejects(call(player(p.id), 'adm_audit', [10]), e => e.code === '42501');
  // signed out (the session gone), or a token with no session: out at once, though the token itself hasn't expired
  const C = await newAdmin(); await call(C.claims, 'adm_prices');
  await q('delete from auth.sessions where user_id = $1', [C.id]);
  await rejects(call(C.claims, 'adm_prices'), /not an admin/);
  assert.equal((await call(C.claims, 'adm_whoami')).why, 'stale');
  await rejects(call(signedIn(A.id, { sid: 'none' }), 'adm_prices'), /not an admin/);
  await rejects(call(signedIn(A.id, { sid: uid() }), 'adm_prices'), /not an admin/);
  // taken off the list: out at once
  const B = await newAdmin(); await call(B.claims, 'adm_prices');
  await q('delete from public.rm_admins where id = $1', [B.id]);
  await rejects(call(B.claims, 'adm_prices'), /not an admin/);
});

test('the helpers and the tables stay closed to the app', async () => {
  const p = await newPlayer('Peek');
  for (const sql of ['select public._adm()', "select public._live('{}')", "select public._audit(null, 'x', 'y', '{}')", "select public._tally('{}', 'k', 1)", 'select public._end_sessions(null)',
    'select public._prices_v()', "select public._code_at('{}')", 'select public._tut_steps()', 'select public._rank_of(1)', 'select public._days(3)']) {
    await rejects(as(A.claims, sql), /permission denied/);
    await rejects(as(null, sql, [], { role: 'anon' }), /permission denied/);
  }
  for (const t of ['rm_admins', 'rm_audit', 'rm_prices', 'rm_installs', 'rm_daily', 'rm_buys']) {
    await rejects(as(A.claims, 'select * from public.' + t), /permission denied/);
    await rejects(as(player(p.id), 'insert into public.' + t + ' default values'), /permission denied/);
    await rejects(as(null, 'select * from public.' + t, [], { role: 'anon' }), /permission denied/);
  }
  // nor can anyone add themselves as an admin through a function: there's none
  await rejects(as(player(p.id), "insert into public.rm_admins (id) values ('" + p.id + "')"), /permission denied/);
});

// ------------------------------------------------------------------ the game's stats

test('rm_track: an install, its state and its counters', async () => {
  const iid = uid();
  const r = await track(iid, { plat: 'ios', av: '1.1', gv: 354, rank: 4, xp: 900, dabs: 320, tut: 'done', secs: 75 }, [
    { k: 'open' }, { k: 'tut', s: 'intro' }, { k: 'tut', s: 'l:move' }, { k: 'tut', s: 'intro' },
    { k: 'match', m: 'duel', on: false, r: 'win', cov: 61, ko: 2, s: 92, st: 'island', d: 'easy' },
    { k: 'match', m: 'ffa', on: true, r: 'loss', cov: 140, ko: 300, s: 9999, st: 'sewer' },
    { k: 'earn', src: 'match', n: 48 }, { k: 'earn', src: 'comm', n: 60 }, { k: 'earn', n: 5 },
    { k: 'view', i: 'tophat', a: false }, { k: 'view', i: 'tophat', a: true }, { k: 'view', i: 'flower', a: true },
    { k: 'buy', i: 'flower', p: 145 },
    { k: 'craft', i: 'giant' }, { k: 'skip', i: 'giant' },
    { k: 'ad', pl: 'craft', r: 'ask' }, { k: 'ad', pl: 'craft', r: 'shown' }, { k: 'ad', pl: 'craft', r: 'reward' }, { k: 'ad', pl: 'lesson', r: 'fail' },
    { k: 'rank', n: 4 }, { k: 'iap', pr: 'dabs_500', c: 499 },
    { k: 'nope', x: 1 }, 'junk', null, { k: 'ad', pl: 'craft', r: 'maybe' }, { k: 'match', m: 'bad mode!' }, { k: 'view', i: 'v:sneaky' }]);
  assert.equal(r.ok, true); assert.equal(typeof r.v, 'number');
  const [i] = await q('select * from public.rm_installs where iid = $1', [iid]);
  assert.equal(i.platform, 'ios'); assert.equal(i.app_ver, '1.1'); assert.equal(i.game_ver, 354); assert.equal(i.rank, 4); assert.equal(Number(i.xp), 900);
  assert.equal(Number(i.dabs), 320); assert.equal(i.tut, 'done'); assert.equal(i.sessions, 1); assert.equal(i.matches, 2); assert.equal(Number(i.play_secs), 75);
  assert.deepEqual(i.tut_steps, ['intro', 'l:move']); assert.deepEqual(i.modes, ['duel', 'ffa']); assert.deepEqual(i.viewed, ['tophat', 'flower']);
  assert.equal(i.user_id, null); assert.equal(Number(i.days), 1);
  const c = Object.fromEntries((await q('select k, n from public.rm_daily where day = current_date')).map(x => [x.k, Number(x.n)]));
  const want = { new: 1, dau: 1, sessions: 1, matches: 2, play_secs: 75, dabs_earned: 113, 'earn:match': 48, 'earn:comm': 60, 'earn:other': 5,
    'm:duel:0:plays': 1, 'm:duel:0:win': 1, 'm:duel:0:secs': 92, 'm:duel:0:cov': 61, 'm:duel:0:ko': 2,
    'm:ffa:1:plays': 1, 'm:ffa:1:loss': 1, 'm:ffa:1:secs': 600, 'm:ffa:1:cov': 100, 'm:ffa:1:ko': 99, 'st:island': 1, 'st:sewer': 1, 'd:easy': 1,
    'v:tophat': 1, 'v:flower': 1, 'va:flower': 1, buys: 1, dabs_spent: 145, 'b:flower': 1, 'bd:flower': 145, 'craft:giant': 1, 'skip:giant': 1,
    'ad:craft:ask': 1, 'ad:craft:shown': 1, 'ad:craft:reward': 1, 'ad:lesson:fail': 1, ads: 1, 'rank:4': 1, iap: 1, iap_cents: 499, 'iap:dabs_500': 1, 'iapc:dabs_500': 499 };
  for (const [k, n] of Object.entries(want)) assert.equal(c[k], n, k);
  assert.equal(c['va:tophat'], undefined); // (the second look at the top hat that day didn't count again)
  assert.ok(!Object.keys(c).some(k => /sneaky|bad mode|maybe|nope/.test(k)), 'made-up ids and kinds are dropped');
  assert.deepEqual((await q('select item, price from public.rm_buys where iid = $1', [iid])).map(x => [x.item, x.price]), [['flower', 145]]);

  // the same install again: not new, not another daily active, the views already counted stay counted
  await track(iid, { secs: 99999, rank: 5, tut: 'bad step!' }, [{ k: 'open' }, { k: 'view', i: 'tophat', a: true }, { k: 'view', i: 'pirate', a: true }]);
  const c2 = Object.fromEntries((await q('select k, n from public.rm_daily where day = current_date')).map(x => [x.k, Number(x.n)]));
  assert.equal(c2.new, 1); assert.equal(c2.dau, 1); assert.equal(c2.sessions, 2); assert.equal(c2.play_secs, 75 + 3600); // (seconds capped at an hour a call)
  assert.equal(c2['v:tophat'], 1); assert.equal(c2['v:pirate'], 1); assert.equal(c2['va:pirate'], 1);
  const [i2] = await q('select rank, tut, sessions from public.rm_installs where iid = $1', [iid]);
  assert.deepEqual([i2.rank, i2.tut, i2.sessions], [5, 'done', 2]); // (a bad tutorial value keeps the last good one)
});

test('rm_track: bad batches are refused, and a signed-in player is linked by their token only', async () => {
  assert.deepEqual(await track(null, {}, []), { ok: false, why: 'bad' });
  assert.deepEqual(await anon('rm_track', [uid(), {}, JSON.stringify({ k: 'open' })]), { ok: false, why: 'bad' });
  assert.deepEqual(await track(uid(), {}, Array.from({ length: 61 }, () => ({ k: 'open' }))), { ok: false, why: 'bad' });
  assert.equal((await track(uid(), {}, Array.from({ length: 60 }, () => ({ k: 'open' })))).ok, true);
  assert.equal((await anon('rm_track', [uid(), JSON.stringify('not an object'), null])).ok, true); // (no meta, no events: still a ping)
  // a signed-in player: the install is theirs, whatever the body says
  const p = await newPlayer('Link'), other = await newPlayer('Other'), iid = uid();
  await track(iid, { user_id: other.id, uid: other.id }, [{ k: 'open' }], player(p.id));
  assert.equal((await q('select user_id from public.rm_installs where iid = $1', [iid]))[0].user_id, p.id);
  // signed out later: still linked to the last player; another player signs in on it: theirs now
  await track(iid, {}, []);
  assert.equal((await q('select user_id from public.rm_installs where iid = $1', [iid]))[0].user_id, p.id);
  await track(iid, {}, [], player(other.id));
  assert.equal((await q('select user_id from public.rm_installs where iid = $1', [iid]))[0].user_id, other.id);
});

test('rm_track: 120 calls an hour from one install, and a flood of new installs is turned away', async () => {
  const iid = uid();
  await track(iid, {}, []);
  await q("update public.rm_installs set win_n = 119 where iid = $1", [iid]);
  assert.equal((await track(iid, {}, [{ k: 'open' }])).ok, true);
  assert.deepEqual(await track(iid, {}, [{ k: 'open' }]), { ok: false, why: 'rate' });
  assert.equal((await q('select sessions from public.rm_installs where iid = $1', [iid]))[0].sessions, 1); // (the refused call counted nothing)
  await q("update public.rm_installs set win_at = now() - interval '61 minutes' where iid = $1", [iid]);
  assert.equal((await track(iid, {}, [])).ok, true); // (a new hour)
  // 600 new installs in a minute is far beyond the game: the next new one waits
  await q("insert into public.rm_installs (iid, first_at) select gen_random_uuid(), now() from generate_series(1, 600)");
  assert.deepEqual(await track(uid(), {}, [{ k: 'open' }]), { ok: false, why: 'rate' });
  assert.equal((await track(iid, {}, [])).ok, true); // (installs already known carry on)
  await q("update public.rm_installs set first_at = now() - interval '2 minutes' where first_at > now() - interval '1 minute' and sessions = 0 and win_n = 0");
  assert.equal((await track(uid(), {}, [])).ok, true);
  await q('delete from public.rm_installs where win_n = 0');
});

test('rm_track: a day only takes so many kinds of counter (made-up ids cannot grow the table without end)', async () => {
  await q("insert into public.rm_daily (day, k, n) select current_date, 'zz:' || g, 1 from generate_series(1, 3000) g");
  const iid = uid();
  await track(iid, {}, [{ k: 'open' }, { k: 'view', i: 'never_seen_item' }]);
  const c = Object.fromEntries((await q("select k, n from public.rm_daily where day = current_date and k in ('sessions', 'v:never_seen_item')")).map(x => [x.k, Number(x.n)]));
  assert.ok(c.sessions >= 1); assert.equal(c['v:never_seen_item'], undefined);
  await q("delete from public.rm_daily where k like 'zz:%'");
});

test('rm_track: a new day marks the install active again, for retention', async () => {
  const iid = uid();
  await track(iid, {}, []);
  await q("update public.rm_installs set first_at = now() - interval '8 days', last_at = now() - interval '1 day' where iid = $1", [iid]);
  const before = Number((await q("select coalesce(sum(n), 0) n from public.rm_daily where day = current_date and k = 'dau'"))[0].n);
  await track(iid, {}, []);
  const [i] = await q('select days from public.rm_installs where iid = $1', [iid]);
  assert.equal(Number(i.days), 1 + (1 << 8)); // (day 0 and day 8)
  assert.equal(Number((await q("select sum(n) n from public.rm_daily where day = current_date and k = 'dau'"))[0].n), before + 1);
});

// ------------------------------------------------------------------ the reports

test('adm_overview: active installs, new ones, retention by cohort, and every day of the range', async () => {
  await q('truncate public.rm_installs, public.rm_daily, public.rm_buys');
  const ins = (first, last, days, extra = '') => q(`insert into public.rm_installs (iid, first_at, last_at, days${extra ? ', dabs' : ''}) values (gen_random_uuid(), now() - $1::interval, now() - $2::interval, $3${extra ? ', ' + extra : ''})`, [first, last, days]);
  await ins('1 hour', '1 minute', 1);                 // new today, online
  await ins('3 days', '2 days', 0b11);                 // started 3 days ago, back the next day
  await ins('5 days', '5 days', 0b1);                  // started 5 days ago, never back
  await ins('20 days', '10 days', 1);                  // a month's active, not the week's
  await ins('33 days', '3 days', 1 + 2 ** 30);         // back exactly 30 days after its first
  await ins('40 days', '35 days', 1);                  // gone
  const o = await call(A.claims, 'adm_overview', [7]);
  assert.equal(o.installs, 6); assert.equal(o.online, 1); assert.equal(o.dau, 1); assert.equal(o.wau, 4); assert.equal(o.mau, 5);
  assert.equal(o.new_7d, 3); assert.ok(o.new_today >= 0 && o.new_today <= 1);
  assert.deepEqual(o.retention, { d1: 0.5, cohort_d1: 2, d7: null, cohort_d7: 0, d30: 1, cohort_d30: 1 });
  assert.equal(o.days.length, 7); assert.equal(o.days[6].day, today()); assert.equal(o.days[0].day, dayAgo(6));
  assert.deepEqual(Object.keys(o.days[0]).sort(), ['ads', 'buys', 'dabs_earned', 'dabs_spent', 'dau', 'day', 'matches', 'new', 'play_secs', 'sessions']);
  // counters show on their day; a session's average length over the last week
  await q("insert into public.rm_daily (day, k, n) values (current_date, 'sessions', 4), (current_date, 'play_secs', 2000), (current_date - 2, 'matches', 9), (current_date - 2, 'sessions', 1), (current_date - 2, 'play_secs', 500)");
  const o2 = await call(A.claims, 'adm_overview', [7]);
  assert.equal(o2.sessions_today, 4); assert.equal(o2.avg_session_secs, 500); assert.equal(o2.days[4].matches, 9); assert.equal(o2.days[6].sessions, 4);
  // the range is clamped to 1..180 days
  assert.equal((await call(A.claims, 'adm_overview', [0])).days.length, 1);
  assert.equal((await call(A.claims, 'adm_overview', [9999])).days.length, 180);
  // the days don't shift with the database session's time zone
  const far = await call(A.claims, 'adm_overview', [7], { tz: 'Pacific/Kiritimati' });
  assert.deepEqual(far.days.map(d => d.day), o2.days.map(d => d.day));
});

test('adm_modes: plays, results, players, coverage, online share, canvases and difficulties', async () => {
  await q('truncate public.rm_installs, public.rm_daily');
  const a = uid(), b = uid();
  await track(a, {}, [{ k: 'match', m: 'duel', r: 'win', cov: 60, s: 90, st: 'island', d: 'easy' }, { k: 'match', m: 'duel', r: 'loss', cov: 40, s: 80, st: 'island', d: 'hard' },
    { k: 'match', m: 'solo', cov: 70, s: 60, st: 'blank' }]);
  await track(b, {}, [{ k: 'match', m: 'duel', on: true, r: 'draw', cov: 50, s: 100, st: 'raft' }, { k: 'match', m: 'trio', r: 'win', cov: 45, s: 120, st: 'island', d: 'easy' }]);
  await q("insert into public.rm_daily (day, k, n) values (current_date - 3, 'm:duel:0:plays', 5), (current_date - 3, 'm:duel:0:win', 5), (current_date - 40, 'm:duel:0:plays', 100)");
  const m = await call(A.claims, 'adm_modes', [7]);
  const duel = m.modes.find(x => x.mode === 'duel');
  assert.deepEqual(duel, { mode: 'duel', plays: 8, wins: 6, losses: 1, draws: 1, players: 2, avg_secs: 34, avg_cov: 18.8, online: 1 });
  assert.equal(m.modes[0].mode, 'duel'); // (most played first)
  assert.deepEqual(m.modes.find(x => x.mode === 'solo'), { mode: 'solo', plays: 1, wins: 0, losses: 0, draws: 0, players: 1, avg_secs: 60, avg_cov: 70, online: 0 });
  assert.equal(m.days.length, 7);
  assert.deepEqual(m.days[6], { day: today(), solo: 1, duel: 3, trio: 1, ffa: 0, duo: 0, online: 1 });
  assert.equal(m.days[3].duel, 5);
  assert.deepEqual(m.stages, [{ stage: 'island', plays: 3 }, { stage: 'blank', plays: 1 }, { stage: 'raft', plays: 1 }]);
  assert.deepEqual(m.diffs, [{ diff: 'easy', plays: 2 }, { diff: 'hard', plays: 1 }]);
  const empty = await call(A.claims, 'adm_modes', [1]);
  assert.equal(empty.days.length, 1);
});

test('adm_progress: ranks, the tutorial funnel with who is stuck where, and the share done', async () => {
  await q('truncate public.rm_installs');
  const ins = (rank, steps, lastAgo) => q("insert into public.rm_installs (iid, rank, tut_steps, last_at) values (gen_random_uuid(), $1, $2, now() - $3::interval)", [rank, steps, lastAgo]);
  await ins(1, ['intro'], '5 days');                                         // stuck after the intro
  await ins(1, ['intro', 'match', 'l:move', 'l:free0', 'l:sling'], '4 days'); // stuck at the slingshot
  await ins(2, ['intro', 'match', 'l:move', 'l:free0', 'l:sling'], '1 hour'); // there now, still playing: not stuck
  await ins(3, ['intro', 'match', 'l:move', 'shop', 'done'], '9 days');      // finished the basics: never stuck
  await ins(75, ['intro', 'match', 'done', 'strokes', 'mystery_step'], '2 days');
  await ins(null, [], '40 days');
  const p = await call(A.claims, 'adm_progress', [null]);
  assert.deepEqual(p.ranks, [{ rank: 1, players: 2, active: 2 }, { rank: 2, players: 1, active: 1 }, { rank: 3, players: 1, active: 1 }, { rank: 50, players: 1, active: 1 }]);
  const t = Object.fromEntries(p.tutorial.map(x => [x.step, [x.reached, x.stuck]]));
  assert.deepEqual(t.intro, [5, 1]); assert.deepEqual(t.match, [4, 0]); assert.deepEqual(t['l:sling'], [2, 1]); assert.deepEqual(t.done, [2, 0]);
  assert.deepEqual(t['l:rest'], [0, 0]);
  assert.equal(p.tutorial[0].step, 'intro'); assert.equal(p.tutorial[23].step, 'strokes_done');
  assert.deepEqual(p.tutorial[24], { step: 'mystery_step', reached: 1, stuck: 0 }); // (steps seen that aren't in the list come after it)
  assert.equal(p.active_7d, 4); assert.equal(p.median_rank, 2); assert.equal(p.done_pct, 0.3333);
  // the order from the dashboard (catalog.json) wins
  const p2 = await call(A.claims, 'adm_progress', [['match', 'intro']]);
  assert.deepEqual(p2.tutorial.slice(0, 2).map(x => x.step), ['match', 'intro']);
  assert.equal(p2.tutorial.find(x => x.step === 'intro').stuck, 2); // (the furthest step in that list: the one stuck at the slingshot is past both, so at "intro")
});

test('adm_economy: views, affordable views, buys, buyers this week, live prices, balances, Strokes and where dabs come from', async () => {
  await q('truncate public.rm_installs, public.rm_daily, public.rm_buys');
  await q("delete from public.rm_prices");
  const a = uid(), b = uid(), c = uid();
  await track(a, { dabs: 100 }, [{ k: 'view', i: 'tophat', a: false }, { k: 'view', i: 'flower', a: true }, { k: 'buy', i: 'flower', p: 145 }, { k: 'earn', src: 'match', n: 40 }, { k: 'craft', i: 'giant' }]);
  await track(b, { dabs: 900 }, [{ k: 'view', i: 'tophat', a: true }, { k: 'buy', i: 'tophat', p: 580 }, { k: 'earn', src: 'comm', n: 60 }, { k: 'craft', i: 'giant' }, { k: 'skip', i: 'giant' }, { k: 'craft', i: 'freeze' }]);
  await track(c, { dabs: 400 }, [{ k: 'view', i: 'tophat', a: false }]);
  await q("insert into public.rm_buys (at, iid, item, price) values (now() - interval '10 days', gen_random_uuid(), 'tophat', 580)");
  await q("insert into public.rm_daily (day, k, n) values (current_date - 10, 'b:tophat', 1), (current_date - 10, 'bd:tophat', 580), (current_date - 10, 'buys', 1), (current_date - 10, 'dabs_spent', 580)");
  await call(A.claims, 'adm_set_price', ['tophat', 450]);
  await call(A.claims, 'adm_set_price', ['halo', 700]); // (priced, never seen)
  const e = await call(A.claims, 'adm_economy', [30]);
  const it = Object.fromEntries(e.items.map(x => [x.item, x]));
  assert.deepEqual(Object.keys(it).sort(), ['flower', 'halo', 'tophat']);
  const th = it.tophat;
  assert.deepEqual([th.views, th.afford_views, th.buys, th.dabs, th.buyers_7d, th.price], [3, 1, 2, 1160, 1, 450]);
  assert.ok(Date.now() - Date.parse(th.last_buy) < 60000);
  assert.deepEqual([it.flower.views, it.flower.afford_views, it.flower.buys, it.flower.price], [1, 1, 1, null]);
  assert.deepEqual([it.halo.views, it.halo.buys, it.halo.price, it.halo.last_buy], [0, 0, 700, null]);
  assert.deepEqual(e.totals, { dabs_earned: 100, dabs_spent: 725 + 580, buys: 3, median_balance: 400 });
  assert.equal(e.days.length, 30); assert.deepEqual(e.days[29], { day: today(), buys: 2, dabs_spent: 725, dabs_earned: 100 });
  assert.deepEqual(e.strokes, [{ stroke: 'giant', crafts: 2, skips: 1 }, { stroke: 'freeze', crafts: 1, skips: 0 }]);
  assert.deepEqual(e.earn, [{ src: 'comm', dabs: 60 }, { src: 'match', dabs: 40 }]);
  // a week's window leaves out the old buy
  assert.equal((await call(A.claims, 'adm_economy', [7])).items.find(x => x.item === 'tophat').buys, 1);
});

test('adm_ads and adm_iap', async () => {
  await q('truncate public.rm_daily');
  await track(uid(), {}, [{ k: 'ad', pl: 'craft', r: 'ask' }, { k: 'ad', pl: 'craft', r: 'shown' }, { k: 'ad', pl: 'craft', r: 'reward' },
    { k: 'ad', pl: 'craft', r: 'ask' }, { k: 'ad', pl: 'craft', r: 'fail' }, { k: 'ad', pl: 'lesson', r: 'ask' }, { k: 'ad', pl: 'lesson', r: 'shown' }]);
  const a = await call(A.claims, 'adm_ads', [7]);
  assert.deepEqual(a.placements, [{ placement: 'craft', asked: 2, shown: 1, rewarded: 1, failed: 1 }, { placement: 'lesson', asked: 1, shown: 1, rewarded: 0, failed: 0 }]);
  assert.equal(a.days.length, 7); assert.deepEqual(a.days[6], { day: today(), asked: 3, shown: 2, rewarded: 1, failed: 1 });
  const none = await call(A.claims, 'adm_iap', [7]);
  assert.deepEqual(none.products, []); assert.equal(none.days.length, 7); assert.equal(none.days[6].buys, 0);
  await track(uid(), {}, [{ k: 'iap', pr: 'dabs_500', c: 499 }, { k: 'iap', pr: 'dabs_500', c: 499 }, { k: 'iap', pr: 'com.rollmodel.pack', c: 999 }]);
  const i = await call(A.claims, 'adm_iap', [7]);
  assert.deepEqual(i.products, [{ product: 'com.rollmodel.pack', buys: 1, revenue_cents: 999 }, { product: 'dabs_500', buys: 2, revenue_cents: 998 }]);
  assert.deepEqual(i.days[6], { day: today(), buys: 3, revenue_cents: 1997 });
});

// ------------------------------------------------------------------ live prices

test('live prices: set, read by the game, cleared, and every change in the audit log', async () => {
  await q('delete from public.rm_prices');
  const before = await anon('rm_config', []);
  assert.deepEqual(await call(A.claims, 'adm_set_price', ['Top Hat', 10]), { ok: false, why: 'item' });
  assert.deepEqual(await call(A.claims, 'adm_set_price', ['x'.repeat(33), 10]), { ok: false, why: 'item' });
  assert.deepEqual(await call(A.claims, 'adm_set_price', ['tophat', -1]), { ok: false, why: 'range' });
  assert.deepEqual(await call(A.claims, 'adm_set_price', ['tophat', 100001]), { ok: false, why: 'range' });
  assert.deepEqual(await call(A.claims, 'adm_set_price', ['tophat', 450]), { ok: true });
  assert.deepEqual(await call(A.claims, 'adm_set_price', ['tophat', 500]), { ok: true });
  assert.deepEqual(await call(A.claims, 'adm_set_price', ['flower', 0]), { ok: true });
  const cfg = await anon('rm_config', []);
  assert.deepEqual(cfg.prices, { flower: 0, tophat: 500 }); assert.ok(cfg.v > before.v && Math.abs(cfg.v - Date.now()) < 60000);
  assert.equal((await track(uid(), {}, [])).v, cfg.v); // (the game sees the version on every batch)
  const list = await call(A.claims, 'adm_prices');
  assert.deepEqual(list.map(x => [x.item, x.price]), [['flower', 0], ['tophat', 500]]); assert.match(list[0].updated_by, /@example\.com$/);
  assert.deepEqual(await call(A.claims, 'adm_set_price', ['tophat', null]), { ok: true });
  const cfg2 = await call(player(await newUser()), 'rm_config');
  assert.deepEqual(cfg2.prices, { flower: 0 }); assert.ok(cfg2.v >= cfg.v);
  const log = (await call(A.claims, 'adm_audit', [10])).filter(x => x.action === 'set_price' && x.target === 'tophat');
  assert.deepEqual(log.slice(0, 3).map(x => x.detail), [{ from: 500, to: null }, { from: 450, to: 500 }, { from: null, to: 450 }]);
  assert.match(log[0].admin, /@example\.com$/);
});

// ------------------------------------------------------------------ support

test('adm_find: username prefix, friend code, user id; nothing for a too-short search', async () => {
  const tag = suffix().slice(0, 4);
  const a = await newPlayer('Z' + tag), b = await newPlayer('Z' + tag + 'q'), c = await newPlayer('Zq' + tag);
  const names = r => r.map(x => x.name);
  const r1 = await call(A.claims, 'adm_find', ['z' + tag]);
  assert.deepEqual(names(r1).sort(), [a.name, b.name].sort());
  assert.deepEqual(names(await call(A.claims, 'adm_find', ['Z' + tag + '_'])), [a.name]); // (the _ is a letter here, not a wildcard)
  assert.deepEqual(Object.keys(r1[0]).sort(), ['account', 'code', 'created_at', 'id', 'last_seen', 'name', 'rank']);
  assert.deepEqual(names(await call(A.claims, 'adm_find', [b.name.toUpperCase()])), [b.name]);
  const spaced = b.code.slice(0, 4) + ' ' + b.code.slice(4).toLowerCase();
  assert.deepEqual(names(await call(A.claims, 'adm_find', [spaced])), [b.name]);
  assert.deepEqual(names(await call(A.claims, 'adm_find', [c.id])), [c.name]);
  assert.deepEqual(names(await call(A.claims, 'adm_find', [c.id.toUpperCase()])), [c.name]);
  assert.deepEqual(await call(A.claims, 'adm_find', ['z']), []);
  assert.deepEqual(await call(A.claims, 'adm_find', ['   ']), []);
  assert.deepEqual(await call(A.claims, 'adm_find', ['z'.repeat(41)]), []);
  assert.deepEqual(await call(A.claims, 'adm_find', ["%' or 1=1 --"]), []);
  assert.deepEqual(await call(A.claims, 'adm_find', ['%%']), []);
  assert.ok((await call(A.claims, 'adm_find', ['Ze'])).length <= 25);
});

test('adm_player: the whole picture of one player, or null', async () => {
  const p = await newPlayer('Look', { account: true });
  await call(player(p.id), 'rm_save_put', [{ xp: 250, drops: 333, owned: ['flower', 'tophat'], name: 'x' }]);
  const iid = uid(); await track(iid, { plat: 'ios', av: '1.1', gv: 354, tut: 'done' }, [{ k: 'open' }], player(p.id));
  await q("insert into auth.sessions (id, user_id) values (gen_random_uuid(), $1)", [p.id]);
  const x = await call(A.claims, 'adm_player', [p.id]);
  assert.equal(x.id, p.id); assert.equal(x.name, p.name); assert.equal(x.code, p.code); assert.equal(x.rank, 3);
  assert.equal(x.account, true); assert.equal(x.anonymous, false); assert.equal(x.admin, false); assert.equal(x.friends, 0); assert.equal(x.blocked_by_them, 0);
  assert.deepEqual([x.details.first_name, x.details.last_name, x.details.birth_year, x.details.terms], ['Dana', 'Lee', 2001, '2026-10']);
  assert.deepEqual([x.save.rank, x.save.xp, x.save.drops, x.save.items], [3, 250, 333, 2]); // (250 xp: 100 for rank 2, 145 more for rank 3)
  assert.equal(x.installs.length, 1); assert.deepEqual([x.installs[0].iid, x.installs[0].platform, x.installs[0].game_ver, x.installs[0].sessions, x.installs[0].tut], [iid, 'ios', 354, 1, 'done']);
  assert.ok(x.last_sign_in_at && x.created_at && x.last_seen);
  assert.deepEqual(x.audit, []);
  assert.equal(await call(A.claims, 'adm_player', [uid()]), null);
  // an anonymous player with no username yet: still found by id
  const anonId = await newUser();
  const y = await call(A.claims, 'adm_player', [anonId]);
  assert.deepEqual([y.name, y.account, y.anonymous, y.details, y.save], [null, false, true, null, null]);
});

test('adm_set_password: a new password, the player signed out everywhere, and nothing of it logged', async () => {
  const p = await newPlayer('Lost', { account: true });
  const s1 = uid(), s2 = uid();
  await q('delete from auth.sessions where user_id = $1', [p.id]); // (just these two)
  await q('insert into auth.sessions (id, user_id) values ($1, $3), ($2, $3)', [s1, s2, p.id]);
  await q("insert into auth.refresh_tokens (token, user_id, session_id) values ('t1', $1, $2), ('t2', $1, $3)", [p.id, s1, s2]);
  for (const pw of ['short1', 'longbutnodigits', '123456789', 'a1' + 'é'.repeat(36), null]) assert.deepEqual(await call(A.claims, 'adm_set_password', [p.id, pw]), { ok: false, why: 'weak' }, String(pw));
  assert.deepEqual(await call(A.claims, 'adm_set_password', [uid(), 'GoodPass99']), { ok: false, why: 'missing' });
  assert.deepEqual(await call(A.claims, 'adm_set_password', [(await newPlayer('Anon')).id, 'GoodPass99']), { ok: false, why: 'anonymous' });
  const B = await newAdmin();
  assert.deepEqual(await call(A.claims, 'adm_set_password', [B.id, 'GoodPass99']), { ok: false, why: 'admin' });
  assert.deepEqual(await call(A.claims, 'adm_set_password', [A.id, 'GoodPass99']), { ok: false, why: 'admin' });
  assert.equal((await q('select encrypted_password from auth.users where id = $1', [p.id]))[0].encrypted_password, 'old'); // (nothing changed yet)
  assert.deepEqual(await call(A.claims, 'adm_set_password', [p.id, 'Purple-Paint-42']), { ok: true });
  const [u] = await q('select encrypted_password, encrypted_password = extensions.crypt($2, encrypted_password) as ok, updated_at from auth.users where id = $1', [p.id, 'Purple-Paint-42']);
  assert.equal(u.ok, true); assert.match(u.encrypted_password, /^\$2a\$10\$/); assert.ok(u.updated_at);
  assert.equal((await q('select count(*)::int n from auth.sessions where user_id = $1', [p.id]))[0].n, 0);
  assert.equal((await q('select count(*)::int n from auth.refresh_tokens where user_id = $1', [p.id]))[0].n, 0);
  const [log] = (await call(A.claims, 'adm_audit', [5])).filter(x => x.target === p.id);
  assert.equal(log.action, 'set_password'); assert.deepEqual(log.detail, { name: p.name, sessions: 2 });
  assert.ok(!JSON.stringify(await q('select * from public.rm_audit')).includes('Purple-Paint-42'));
  assert.equal((await call(A.claims, 'adm_player', [p.id])).audit[0].action, 'set_password');
});

test('adm_signout: every session ends; admins are left alone', async () => {
  const p = await newPlayer('Out');
  await q('delete from auth.sessions where user_id = $1', [p.id]); // (just these three)
  await q('insert into auth.sessions (id, user_id) values (gen_random_uuid(), $1), (gen_random_uuid(), $1), (gen_random_uuid(), $1)', [p.id]);
  assert.deepEqual(await call(A.claims, 'adm_signout', [p.id]), { ok: true, sessions: 3 });
  assert.deepEqual(await call(A.claims, 'adm_signout', [p.id]), { ok: true, sessions: 0 });
  assert.deepEqual(await call(A.claims, 'adm_signout', [uid()]), { ok: false, why: 'missing' });
  assert.deepEqual(await call(A.claims, 'adm_signout', [A.id]), { ok: false, why: 'admin' });
  assert.equal((await q('select count(*)::int n from auth.sessions where user_id = $1', [A.id]))[0].n, 1); // (the admin's own session stays)
  const log = (await call(A.claims, 'adm_audit', [10])).filter(x => x.target === p.id && x.action === 'signout');
  assert.deepEqual(log.map(x => x.detail.sessions), [0, 3]);
});

test('adm_delete_player: a typed confirmation, then everything of theirs goes; their stats stay, unlinked', async () => {
  const p = await newPlayer('Gone', { account: true }), f = await newPlayer('Pal');
  await call(player(p.id), 'rm_add_friend', [f.code]); await call(player(f.id), 'rm_add_friend', [p.code]);
  await call(player(p.id), 'rm_save_put', [{ xp: 10 }]);
  const iid = uid(); await track(iid, {}, [{ k: 'open' }], player(p.id));
  assert.deepEqual(await call(A.claims, 'adm_delete_player', [p.id, 'someone else']), { ok: false, why: 'confirm' });
  assert.deepEqual(await call(A.claims, 'adm_delete_player', [p.id, null]), { ok: false, why: 'confirm' });
  assert.deepEqual(await call(A.claims, 'adm_delete_player', [uid(), 'x']), { ok: false, why: 'missing' });
  assert.deepEqual(await call(A.claims, 'adm_delete_player', [A.id, '']), { ok: false, why: 'admin' });
  assert.equal((await q('select count(*)::int n from public.profiles where id = $1', [p.id]))[0].n, 1);
  assert.deepEqual(await call(A.claims, 'adm_delete_player', [p.id, '  ' + p.name.toLowerCase() + ' ']), { ok: true });
  for (const t of ['public.profiles', 'public.accounts', 'public.saves', 'auth.users']) assert.equal((await q(`select count(*)::int n from ${t} where id = $1`, [p.id]))[0].n, 0, t);
  assert.equal((await q('select count(*)::int n from public.friendships where a = $1 or b = $1', [p.id]))[0].n, 0);
  const [i] = await q('select user_id, sessions from public.rm_installs where iid = $1', [iid]);
  assert.deepEqual([i.user_id, i.sessions], [null, 1]);
  assert.equal(await call(A.claims, 'adm_player', [p.id]), null);
  const [log] = (await call(A.claims, 'adm_audit', [5])).filter(x => x.target === p.id);
  assert.equal(log.action, 'delete_player'); assert.deepEqual(log.detail, { name: p.name });
  // a player with no username yet is confirmed with their id
  const n = await newUser();
  assert.deepEqual(await call(A.claims, 'adm_delete_player', [n, 'anything']), { ok: false, why: 'confirm' });
  assert.deepEqual(await call(A.claims, 'adm_delete_player', [n, n.toUpperCase()]), { ok: true });
});

test('each admin can only do so much an hour', async () => {
  const B = await newAdmin();
  await q("insert into public.rate_events (user_id, kind, at) select $1, 'adm_delete', now() from generate_series(1, 30)", [B.id]);
  const p = await newPlayer('Safe');
  assert.deepEqual(await call(B.claims, 'adm_delete_player', [p.id, p.name]), { ok: false, why: 'slow_down' });
  assert.equal((await q('select count(*)::int n from public.profiles where id = $1', [p.id]))[0].n, 1); // (still there)
  assert.deepEqual(await call(A.claims, 'adm_delete_player', [p.id, p.name]), { ok: true }); // (another admin's hour is their own)
  await q("insert into public.rate_events (user_id, kind, at) select $1, k, now() from (values ('adm_password'), ('adm_signout')) v(k), generate_series(1, 60)", [B.id]);
  await q("insert into public.rate_events (user_id, kind, at) select $1, 'adm_price', now() from generate_series(1, 300)", [B.id]);
  const r = await newPlayer('Safe2', { account: true });
  assert.deepEqual(await call(B.claims, 'adm_set_password', [r.id, 'GoodPass99']), { ok: false, why: 'slow_down' });
  assert.deepEqual(await call(B.claims, 'adm_signout', [r.id]), { ok: false, why: 'slow_down' });
  assert.deepEqual(await call(B.claims, 'adm_set_price', ['tophat', 10]), { ok: false, why: 'slow_down' });
  await q('delete from public.rate_events where user_id = $1', [B.id]);
});

test('adm_audit: newest first, a sane limit', async () => {
  for (let i = 0; i < 3; i++) await call(A.claims, 'adm_set_price', ['audit_probe', 100 + i]);
  const a = await call(A.claims, 'adm_audit', [3]);
  assert.equal(a.length, 3); assert.deepEqual(a.map(x => x.detail.to), [102, 101, 100]);
  assert.deepEqual(Object.keys(a[0]).sort(), ['action', 'admin', 'at', 'detail', 'target']);
  assert.equal((await call(A.claims, 'adm_audit', [0])).length, 1);
  assert.ok((await call(A.claims, 'adm_audit', [100000])).length <= 500);
  await call(A.claims, 'adm_set_price', ['audit_probe', null]);
});
