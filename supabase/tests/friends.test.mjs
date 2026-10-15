// Tests for supabase/migrations/*_friends.sql (with *_accounts.sql on top) on a plain local Postgres (with tests/local_stub.sql standing in for Supabase).
// Each call runs the way Supabase runs an app request: as the "authenticated" role, with the caller's id in the JWT claims.
//   PGURL=postgres://postgres@localhost:54329/rmtest node --test supabase/tests/friends.test.mjs
// (needs the `pg` package: NODE_PATH=/path/to/node_modules)
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
    await c.query('select set_config($1, $2, true)', ['request.jwt.claims', user ? JSON.stringify({ sub: user, role }) : '']);
    await c.query('set local role ' + role);
    const r = await c.query(sql, params); await c.query('commit'); return r.rows;
  } catch (e) { await c.query('rollback').catch(() => {}); throw e; } finally { c.release(); }
}
const call = async (user, fn, args = []) => (await as(user, 'select public.' + fn + '(' + args.map((_, i) => '$' + (i + 1)).join(', ') + ') as r', args))[0].r;
// a fresh player with a username nobody else has: the name and a suffix of consonants (which can't spell anything the filter
// would catch), unique for every run against the same database
let seq = 0;
const suffix = () => String(Date.now() * 100 + (seq++ % 100)).slice(-8).replace(/[0-9]/g, d => 'bcdfghjlmn'[d]);
async function player(name) {
  const id = uid(); await db.query('insert into auth.users (id) values ($1)', [id]);
  const me = await call(id, 'rm_me', [name + '_' + suffix(), { eyes: 'round' }, 3]); assert.equal(me.ok, true, JSON.stringify(me)); return { id, ...me };
}

test.after(() => db.end());

test('the tables are closed to the app; only the functions answer', async () => {
  const a = await player('Ada');
  for (const t of ['profiles', 'friend_requests', 'friendships', 'blocks', 'invites', 'trial_scores', 'rate_events'])
    await assert.rejects(as(a.id, 'select * from public.' + t), /permission denied/, t);
  await assert.rejects(as(a.id, "update public.profiles set rank = 999 where id = $1", [a.id]), /permission denied/);
  await assert.rejects(as(null, "select public.rm_me('x')", [], 'anon'), /permission denied/);
  await assert.rejects(as(a.id, 'select public._new_friend_code()'), /permission denied/);
  await assert.rejects(as(null, "select public.rm_inbox('lobby')"), /sign in first/);
});

test('a profile: made once, keeps its code and its username', async () => {
  const a = await player('Bea');
  assert.match(a.code, /^[2-9A-HJKMNP-Z]{8}$/);
  assert.equal(a.anon, true); assert.equal(a.account, false); assert.equal(a.needs_name, false);
  const again = await call(a.id, 'rm_me', ['SomebodyElse', null, 1500]);
  assert.equal(again.code, a.code);
  assert.equal(again.name, a.name); // (a username only changes through rm_rename)
  assert.equal(again.rank, 999);
  await assert.rejects(call(uid(), 'rm_inbox', ['lobby']), /no profile yet/);
});

test('requests by code: send, both ways makes friends, the answers', async () => {
  const a = await player('Cal'), b = await player('Dot');
  assert.deepEqual(await call(a.id, 'rm_add_friend', ['ZZZZZZZZ']), { ok: false, why: 'not_found' });
  assert.deepEqual(await call(a.id, 'rm_add_friend', [a.code]), { ok: false, why: 'self' });
  assert.equal((await call(a.id, 'rm_add_friend', [b.code.slice(0, 4).toLowerCase() + '-' + b.code.slice(4)])).state, 'sent');
  assert.equal((await call(a.id, 'rm_add_friend', [b.code])).state, 'already_sent');
  let ib = await call(b.id, 'rm_inbox', ['lobby']);
  assert.equal(ib.incoming.length, 1); assert.equal(ib.incoming[0].name, a.name);
  let ia = await call(a.id, 'rm_inbox', ['lobby']);
  assert.equal(ia.outgoing.length, 1); assert.equal(ia.outgoing[0].name, b.name);
  assert.equal((await call(b.id, 'rm_add_friend', [a.code])).state, 'friends_now'); // (she'd asked: friends at once)
  assert.equal((await call(a.id, 'rm_add_friend', [b.code])).state, 'already_friends');
  ib = await call(b.id, 'rm_inbox', ['match']); ia = await call(a.id, 'rm_inbox', ['lobby']);
  assert.equal(ia.outgoing.length, 0); assert.equal(ib.incoming.length, 0);
  assert.equal(ia.friends.length, 1); assert.equal(ia.friends[0].name, b.name); assert.equal(ia.friends[0].online, true); assert.equal(ia.friends[0].status, 'match');
  await call(b.id, 'rm_inbox', ['offline']);
  ia = await call(a.id, 'rm_inbox', ['lobby']); assert.equal(ia.friends[0].online, false); assert.equal(ia.friends[0].status, 'offline');
  await db.query("update public.profiles set last_seen = now() - interval '5 minutes', status = 'lobby' where id = $1", [b.id]);
  ia = await call(a.id, 'rm_inbox', ['lobby']); assert.equal(ia.friends[0].online, false);
  assert.ok(!('friend_code' in ia.friends[0]) && !('code' in ia.friends[0]), 'a friend\'s code is not handed out');
});

test('accept, decline, cancel, remove', async () => {
  const a = await player('Eve'), b = await player('Fin'), c = await player('Gus');
  await call(a.id, 'rm_add_friend', [b.code]); await call(c.id, 'rm_add_friend', [b.code]);
  assert.equal((await call(b.id, 'rm_answer_request', [a.id, true])).state, 'friends_now');
  assert.equal((await call(b.id, 'rm_answer_request', [c.id, false])).state, 'declined');
  assert.deepEqual(await call(b.id, 'rm_answer_request', [c.id, true]), { ok: false, why: 'gone' });
  assert.equal((await call(b.id, 'rm_inbox')).friends.length, 1);
  await call(c.id, 'rm_add_friend', [a.code]); await call(c.id, 'rm_cancel_request', [a.id]);
  assert.equal((await call(a.id, 'rm_inbox')).incoming.length, 0);
  await call(a.id, 'rm_remove_friend', [b.id]);
  assert.equal((await call(b.id, 'rm_inbox')).friends.length, 0);
});

test('blocking: friendship and requests gone, and they cannot reach you again (without being told)', async () => {
  const a = await player('Hal'), b = await player('Ivy');
  await call(a.id, 'rm_add_friend', [b.code]); await call(b.id, 'rm_answer_request', [a.id, true]);
  assert.deepEqual(await call(b.id, 'rm_block', [a.id]), { ok: true });
  assert.equal((await call(a.id, 'rm_inbox')).friends.length, 0);
  assert.equal((await call(a.id, 'rm_add_friend', [b.code])).state, 'sent'); // (looks sent...)
  assert.equal((await call(b.id, 'rm_inbox')).incoming.length, 0); // (...but never arrives)
  assert.equal((await call(a.id, 'rm_inbox')).outgoing.length, 0);
  assert.equal((await call(b.id, 'rm_inbox')).blocked[0].name, a.name);
  await call(b.id, 'rm_unblock', [a.id]);
  assert.equal((await call(a.id, 'rm_add_friend', [b.code])).state, 'sent');
  assert.equal((await call(b.id, 'rm_inbox')).incoming.length, 1);
});

test('invites: friends only, one open at a time, accept gives the room, they run out', async () => {
  const a = await player('Jo'), b = await player('Kit'), c = await player('Lu');
  await call(a.id, 'rm_add_friend', [b.code]); await call(b.id, 'rm_add_friend', [a.code]);
  assert.deepEqual(await call(a.id, 'rm_invite', [c.id, 'ABC12', 'duel']), { ok: false, why: 'not_friends' });
  assert.deepEqual(await call(a.id, 'rm_invite', [b.id, 'nope', 'duel']), { ok: false, why: 'bad_room' });
  const i1 = await call(a.id, 'rm_invite', [b.id, 'abc12', 'duel']); assert.equal(i1.ok, true);
  const i2 = await call(a.id, 'rm_invite', [b.id, 'XYZ98', 'duel']); assert.equal(i2.ok, true);
  let ib = await call(b.id, 'rm_inbox');
  assert.equal(ib.invites.length, 1); assert.equal(ib.invites[0].room, 'XYZ98'); assert.equal(ib.invites[0].from.name, a.name);
  assert.deepEqual(await call(b.id, 'rm_answer_invite', [i1.id, true]), { ok: false, why: 'gone' }); // (replaced by the newer one)
  assert.deepEqual(await call(c.id, 'rm_answer_invite', [i2.id, true]), { ok: false, why: 'gone' }); // (not hers)
  assert.deepEqual(await call(b.id, 'rm_answer_invite', [i2.id, true]), { ok: true, room: 'XYZ98', mode: 'duel' });
  assert.equal((await call(a.id, 'rm_inbox')).sent.find(s => s.id === i2.id).status, 'accepted');
  const i3 = await call(a.id, 'rm_invite', [b.id, 'QQQ11', 'duel']);
  await db.query("update public.invites set expires_at = now() - interval '1 second' where id = $1", [i3.id]);
  assert.equal((await call(b.id, 'rm_inbox')).invites.length, 0);
  assert.deepEqual(await call(b.id, 'rm_answer_invite', [i3.id, true]), { ok: false, why: 'gone' });
  const i4 = await call(a.id, 'rm_invite', [b.id, 'RRR22', 'duel']); await call(a.id, 'rm_cancel_invite', [i4.id]);
  assert.equal((await call(b.id, 'rm_inbox')).invites.length, 0);
});

test('rate limits: wrong codes run out after 30 an hour', async () => {
  const a = await player('Max');
  for (let k = 0; k < 30; k++) assert.equal((await call(a.id, 'rm_add_friend', ['WRONG' + String(k).padStart(3, '2')])).why, 'not_found');
  assert.deepEqual(await call(a.id, 'rm_add_friend', ['ANYTHING']), { ok: false, why: 'slow_down' });
});

test('Time trial: your best of the week, and a board of you and your friends only', async () => {
  const a = await player('Ned'), b = await player('Oli'), c = await player('Pia');
  await call(a.id, 'rm_add_friend', [b.code]); await call(b.id, 'rm_add_friend', [a.code]);
  assert.equal((await call(a.id, 'rm_trial', ['blank', 31])).best, 31);
  assert.equal((await call(a.id, 'rm_trial', ['blank', 22])).best, 31);
  await call(b.id, 'rm_trial', ['blank', 40]); await call(c.id, 'rm_trial', ['blank', 90]);
  assert.deepEqual(await call(a.id, 'rm_trial', ['blank', 101]), { ok: false, why: 'bad_run' });
  assert.deepEqual(await call(a.id, 'rm_trial', ['Bad Stage!', 50]), { ok: false, why: 'bad_run' });
  const board = await call(a.id, 'rm_friends_board', ['blank', null]);
  assert.deepEqual(board.rows.map(r => [r.name, r.best, r.runs, r.me]), [[b.name, 40, 1, false], [a.name, 31, 2, true]]);
});
