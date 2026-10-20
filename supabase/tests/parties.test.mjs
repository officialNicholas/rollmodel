// Tests for supabase/migrations/*_parties.sql (on top of the migrations before it) on a plain local Postgres, with
// tests/local_stub.sql standing in for Supabase. Each call runs the way Supabase runs an app request.
//   PGURL=postgres://postgres@localhost:54329/rmtest node --test supabase/tests/parties.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import pg from 'pg';

const db = new pg.Pool({ connectionString: process.env.PGURL || 'postgres://postgres@localhost:54329/rmtest', max: 4 });
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
let seq = 0;
const suffix = () => String(Date.now() * 100 + (seq++ % 100)).slice(-8).replace(/[0-9]/g, d => 'bcdfghjlmn'[d]);
async function player(name) {
  const id = randomUUID(); await db.query('insert into auth.users (id) values ($1)', [id]);
  const me = await call(id, 'rm_me', [name + '_' + suffix(), { c: 'red' }, 3]); assert.equal(me.ok, true, JSON.stringify(me)); return { id, ...me };
}
async function friends(a, b) { await call(a.id, 'rm_add_friend', [b.code]); await call(b.id, 'rm_add_friend', [a.code]); }

test.after(() => db.end());

test('party invites: an 8-character code, friends only, the new inbox shows them and the old one does not', async () => {
  const a = await player('Ama'), b = await player('Ben'), c = await player('Cid');
  await friends(a, b);
  const i = await call(a.id, 'rm_invite', [b.id, 'abcd2345', 'party']); assert.equal(i.ok, true);
  const nb = await call(b.id, 'rm_inbox2', ['lobby']);
  assert.equal(nb.invites.length, 1); assert.equal(nb.invites[0].room, 'ABCD2345'); assert.equal(nb.invites[0].mode, 'party'); assert.equal(nb.invites[0].from.name, a.name);
  assert.ok(Date.parse(nb.invites[0].expires) - Date.parse(nb.now) <= 120000, 'two minutes to answer');
  assert.equal((await call(b.id, 'rm_inbox', ['lobby'])).invites.length, 0, 'an older game never sees a party invite');
  assert.equal((await call(a.id, 'rm_inbox2', ['lobby'])).sent[0].mode, 'party');
  assert.deepEqual(await call(a.id, 'rm_invite', [c.id, 'ABCD2345', 'party']), { ok: false, why: 'not_friends' });
  assert.deepEqual(await call(a.id, 'rm_invite', [b.id, 'ABCD', 'party']), { ok: false, why: 'bad_room' });
  assert.deepEqual(await call(a.id, 'rm_invite', [b.id, 'ABCDEFGHJKMNP', 'party']), { ok: false, why: 'bad_room' }, 'at most 12');
  assert.deepEqual(await call(a.id, 'rm_invite', [b.id, 'ABCD2345', 'squad']), { ok: false, why: 'bad_mode' });
  // a yes hands over the code; a second invite to the same friend replaces the first
  const j = await call(a.id, 'rm_invite', [b.id, 'WXYZ6789', 'party']);
  assert.deepEqual(await call(b.id, 'rm_answer_invite', [i.id, true]), { ok: false, why: 'gone' });
  assert.deepEqual(await call(b.id, 'rm_answer_invite', [j.id, true]), { ok: true, room: 'WXYZ6789', mode: 'party' });
  // a no is seen by the one who asked
  const k = await call(a.id, 'rm_invite', [b.id, 'WXYZ6789', 'party']); await call(b.id, 'rm_answer_invite', [k.id, false]);
  assert.equal((await call(a.id, 'rm_inbox2', ['lobby'])).sent.find(s => s.id === k.id).status, 'declined');
});

test('duel invites from the older games still work, and stay out of the new inbox', async () => {
  const a = await player('Dee'), b = await player('Eli');
  await friends(a, b);
  const i = await call(a.id, 'rm_invite', [b.id, 'ABC12', 'duel']); assert.equal(i.ok, true);
  assert.equal((await call(b.id, 'rm_inbox', ['lobby'])).invites[0].room, 'ABC12');
  assert.equal((await call(b.id, 'rm_inbox2', ['lobby'])).invites.length, 0);
  const d = await call(a.id, 'rm_invite', [b.id, 'XYZ98']); assert.equal(d.ok, true, 'the mode defaults to a duel');
});

test('blocked players cannot invite, either way', async () => {
  const a = await player('Fay'), b = await player('Gil');
  await friends(a, b); await call(b.id, 'rm_block', [a.id]);
  assert.deepEqual(await call(a.id, 'rm_invite', [b.id, 'ABCD2345', 'party']), { ok: false, why: 'not_friends' });
  assert.deepEqual(await call(b.id, 'rm_invite', [a.id, 'ABCD2345', 'party']), { ok: false, why: 'not_friends' });
  await call(b.id, 'rm_unblock', [a.id]); await friends(a, b);
  const i = await call(a.id, 'rm_invite', [b.id, 'ABCD2345', 'party']); assert.equal(i.ok, true);
  await call(b.id, 'rm_block', [a.id]); // (a block also takes back what was waiting)
  assert.equal((await call(b.id, 'rm_inbox2', ['lobby'])).invites.length, 0);
});

test('a friend request says who it went to (so their game can be nudged)', async () => {
  const a = await player('Hob'), b = await player('Isa');
  const r = await call(a.id, 'rm_add_friend', [b.code]); assert.equal(r.state, 'sent'); assert.equal(r.id, b.id);
  assert.equal((await call(a.id, 'rm_add_friend', [b.code])).id, b.id);
  const s = await call(b.id, 'rm_add_friend', [a.code]); assert.equal(s.state, 'friends_now'); assert.equal(s.id, a.id);
  assert.deepEqual(await call(a.id, 'rm_add_friend', ['ZZZZZZZZ']), { ok: false, why: 'not_found' });
});

test('the inbox helper is not callable from the app', async () => {
  const a = await player('Jud');
  await assert.rejects(as(a.id, "select public._inbox('lobby', array['party'])"), /permission denied/);
  await assert.rejects(as(null, "select public.rm_inbox2('lobby')", [], 'anon'), /permission denied/);
});

// ---- notifications while the game is closed: each phone's token, kept with its player, read once per invite
const tok = n => n.toString(16).padStart(2, '0').repeat(32); // (a made-up 64-character token)

test('a phone\'s token: only its player puts it there or takes it away; one account at a time; five at most', async () => {
  const a = await player('Kit'), b = await player('Lou');
  assert.deepEqual(await call(a.id, 'rm_push_token', [tok(1), 'development']), { ok: true });
  assert.deepEqual(await call(a.id, 'rm_push_token', ['not a token']), { ok: false, why: 'bad_token' });
  assert.deepEqual(await call(a.id, 'rm_push_token', [tok(1).slice(0, 40)]), { ok: false, why: 'bad_token' });
  let rows = (await db.query('select user_id, env from public.push_tokens where token = $1', [tok(1)])).rows;
  assert.equal(rows.length, 1); assert.equal(rows[0].user_id, a.id); assert.equal(rows[0].env, 'development');
  // the same phone signed in to another account: the token goes with it
  await call(b.id, 'rm_push_token', [tok(1).toUpperCase()]);
  rows = (await db.query('select user_id, env from public.push_tokens where token = $1', [tok(1)])).rows;
  assert.equal(rows[0].user_id, b.id); assert.equal(rows[0].env, 'production', 'production unless it says otherwise');
  // only your own can be taken away
  await call(a.id, 'rm_push_forget', [tok(1)]);
  assert.equal((await db.query('select count(*)::int as n from public.push_tokens where token = $1', [tok(1)])).rows[0].n, 1);
  await call(b.id, 'rm_push_forget', [tok(1)]);
  assert.equal((await db.query('select count(*)::int as n from public.push_tokens where token = $1', [tok(1)])).rows[0].n, 0);
  // the newest five phones
  for (let n = 10; n < 17; n++) await call(a.id, 'rm_push_token', [tok(n)]);
  const mine = (await db.query('select token from public.push_tokens where user_id = $1', [a.id])).rows.map(r => r.token).sort();
  assert.deepEqual(mine, [12, 13, 14, 15, 16].map(tok).sort());
  // nobody reads or writes the table itself
  await assert.rejects(as(a.id, 'select * from public.push_tokens'), /permission denied/);
  await assert.rejects(as(a.id, "insert into public.push_tokens (token, user_id) values ($1, $2)", [tok(40), b.id]), /permission denied/);
  await assert.rejects(as(null, 'select public.rm_push_token($1)', [tok(41)], 'anon'), /permission denied/);
  // deleting the account takes its tokens with it
  await call(a.id, 'rm_delete_me');
  assert.equal((await db.query('select count(*)::int as n from public.push_tokens where user_id = $1', [a.id])).rows[0].n, 0);
});

test('an invite\'s notification: only for its sender, once, while it is open, and only between friends', async () => {
  const a = await player('Max'), b = await player('Ned'), c = await player('Oz');
  await friends(a, b); await friends(a, c);
  await call(b.id, 'rm_push_token', [tok(50), 'development']); await call(b.id, 'rm_push_token', [tok(51)]);
  const i = await call(a.id, 'rm_invite', [b.id, 'PUSH2345', 'party']);
  assert.deepEqual(await call(c.id, 'rm_invite_push', [i.id]), { ok: false, why: 'not_open' }, 'not your invite');
  assert.deepEqual(await call(b.id, 'rm_invite_push', [i.id]), { ok: false, why: 'not_open' }, 'not even the one it is to');
  const r = await call(a.id, 'rm_invite_push', [i.id]);
  assert.equal(r.ok, true); assert.equal(r.to, b.id); assert.equal(r.from, a.name); assert.equal(r.id, i.id);
  assert.deepEqual(r.tokens.map(t => t.t).sort(), [tok(50), tok(51)].sort());
  assert.equal(r.tokens.find(t => t.t === tok(50)).env, 'development');
  assert.deepEqual(await call(a.id, 'rm_invite_push', [i.id]), { ok: false, why: 'sent' }, 'once');
  // a friend with no phone signed up: nothing to send to
  const j = await call(a.id, 'rm_invite', [c.id, 'PUSH2345', 'party']);
  assert.deepEqual((await call(a.id, 'rm_invite_push', [j.id])).tokens, []);
  // answered, run out, or a duel invite from an older game: no notification
  const k = await call(a.id, 'rm_invite', [b.id, 'PUSH6789', 'party']); await call(b.id, 'rm_answer_invite', [k.id, false]);
  assert.deepEqual(await call(a.id, 'rm_invite_push', [k.id]), { ok: false, why: 'not_open' });
  const l = await call(a.id, 'rm_invite', [b.id, 'PUSH6789', 'party']); await db.query("update public.invites set expires_at = now() - interval '1 second' where id = $1", [l.id]);
  assert.deepEqual(await call(a.id, 'rm_invite_push', [l.id]), { ok: false, why: 'not_open' });
  const d = await call(a.id, 'rm_invite', [b.id, 'DUEL2', 'duel']);
  assert.deepEqual(await call(a.id, 'rm_invite_push', [d.id]), { ok: false, why: 'not_open' });
  // blocked once the invite was made
  const m = await call(a.id, 'rm_invite', [b.id, 'PUSH6789', 'party']); await call(b.id, 'rm_block', [a.id]);
  assert.equal((await call(a.id, 'rm_invite_push', [m.id])).ok, false);
});
