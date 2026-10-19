// Tests for supabase/migrations/*_email.sql (account emails: the private email, the welcome email and its confirm link, Forgot
// password and its reset link, the "password changed" notice) on a plain local Postgres, with tests/local_stub.sql standing in for
// Supabase, its pg_net (a request is recorded in net.sent, never sent) and its Vault.
//   PGURL=postgres://postgres@localhost:54329/rmtest node --test supabase/tests/email.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import pg from 'pg';

const db = new pg.Pool({ connectionString: process.env.PGURL || 'postgres://postgres@localhost:54329/rmtest', max: 4 });
const uid = () => randomUUID();
const now = () => Math.floor(Date.now() / 1000);
const SID = new Map();
const player = id => ({ sub: id, role: 'authenticated', aal: 'aal1', session_id: SID.get(id) });
const adminClaims = id => ({ sub: id, role: 'authenticated', aal: 'aal2', session_id: SID.get(id), amr: [{ method: 'password', timestamp: now() - 70 }, { method: 'totp', timestamp: now() - 60 }] });
async function as(claims, sql, params = [], role = 'authenticated') {
  const c = await db.connect();
  try {
    await c.query('begin');
    await c.query('select set_config($1, $2, true)', ['request.jwt.claims', JSON.stringify(claims || { role })]);
    await c.query('set local role ' + role);
    const r = await c.query(sql, params); await c.query('commit'); return r.rows;
  } catch (e) { await c.query('rollback').catch(() => {}); throw e; } finally { c.release(); }
}
const call = async (claims, fn, args = []) => (await as(claims, 'select public.' + fn + '(' + args.map((_, i) => '$' + (i + 1)).join(', ') + ') as r', args))[0].r;
const anon = async (fn, args = []) => (await as(null, 'select public.' + fn + '(' + args.map((_, i) => '$' + (i + 1)).join(', ') + ') as r', args, 'anon'))[0].r;
const q = async (sql, params) => (await db.query(sql, params)).rows;
const rejects = (p, re) => assert.rejects(p, e => (re.test(e.message) || (assert.fail('unexpected error: ' + e.message), false)));
let seq = 0;
const suffix = () => String(Date.now() * 100 + (seq++ % 100)).slice(-8).replace(/[0-9]/g, d => 'bcdfghjlmn'[d]);
async function newUser(email = null, anonymous = !email) {
  const id = uid(), sid = uid();
  await q('insert into auth.users (id, email, is_anonymous) values ($1, $2, $3)', [id, email, anonymous]);
  await q('insert into auth.sessions (id, user_id) values ($1, $2)', [sid, id]); SID.set(id, sid); return id;
}
// a player with a username; with a real account (a password and the details) when asked
async function newPlayer(base = 'Mail', { account = true } = {}) {
  const id = await newUser(account ? 'u' + id8() + '@rollmodel.invalid' : null, !account);
  const me = await call(player(id), 'rm_me', [base + '_' + suffix(), {}, 3]); assert.equal(me.ok, true, JSON.stringify(me));
  if (account) {
    await q("update auth.users set encrypted_password = extensions.crypt('OldPass123', extensions.gen_salt('bf')) where id = $1", [id]);
    assert.equal((await call(player(id), 'rm_account_save', ['Dana', 'Lee', '2001-12-31', '2026-10'])).ok, true);
  }
  return { id, name: me.name };
}
function id8() { return randomUUID().replace(/-/g, ''); }
const sent = async () => (await q('select id, url, body, headers from net.sent order by id'));
const lastMail = async () => (await q('select url, body, headers from net.sent order by id desc limit 1'))[0];
const tokenOf = body => /#t=([A-Za-z0-9_-]+)/.exec(body.text)[1];
const mail = (e, n) => `m${n}_${suffix()}@example.com`;

test.before(async () => {
  await q('truncate net.sent');
  await q("insert into vault.secrets_stub (name, decrypted_secret) values ('resend_api_key', 're_test_123') on conflict (name) do update set decrypted_secret = excluded.decrypted_secret");
  await q(`update public.rm_settings set v = v || '{"paused": false, "site": "https://playrollmodel.com/", "sender": "Roll Model <hello@mail.playrollmodel.com>", "support": "support@playrollmodel.com"}' where k = 'mail'`);
});
test.after(() => db.end());

test('an email goes with an account only, checked, one account each', async () => {
  const anonP = await newPlayer('NoAcct', { account: false });
  assert.deepEqual(await call(player(anonP.id), 'rm_email_set', ['a@example.com']), { ok: false, why: 'no_account' });
  const p = await newPlayer('Has');
  for (const bad of ['', 'nope', 'a@b', 'a b@c.com', 'x@y.c', '<a@b.com>', 'a@b.com;c@d.com', 'é'.repeat(300) + '@x.com', null]) {
    assert.deepEqual(await call(player(p.id), 'rm_email_set', [bad]), { ok: false, why: 'bad' }, String(bad));
  }
  const em = mail('', 1);
  const r = await call(player(p.id), 'rm_email_set', [em]);
  assert.deepEqual(r, { ok: true, sent: true, verified: false });
  assert.deepEqual(await call(player(p.id), 'rm_email_get'), { email: em, verified: false, mail: true });
  const other = await newPlayer('Other');
  assert.deepEqual(await call(player(other.id), 'rm_email_set', [em.toUpperCase()]), { ok: false, why: 'taken' }); // (any case)
  // 5 an hour
  for (let i = 0; i < 5; i++) assert.equal((await call(player(other.id), 'rm_email_set', [mail('', 10 + i)])).ok, true);
  assert.deepEqual(await call(player(other.id), 'rm_email_set', [mail('', 20)]), { ok: false, why: 'slow_down' });
  // nobody else can read or write the emails
  await rejects(as(player(p.id), 'select * from public.account_emails'), /permission denied/);
  await rejects(as(null, 'select * from public.mail_tokens', [], 'anon'), /permission denied/);
  await rejects(anon('rm_email_get'), /permission denied/);
  for (const sql of ["select public._mail('reset', null, 'x@y.com', '{}')", 'select public._mail_key()', "select public._mail_reset('" + p.id + "')", "select * from public._mail_token()"]) {
    await rejects(as(player(p.id), sql), /permission denied/);
  }
});

test('the welcome email: their username, a confirm link, through Resend with the key from the Vault', async () => {
  const p = await newPlayer('Welc'), em = mail('', 2);
  await q('truncate net.sent');
  await call(player(p.id), 'rm_email_set', [em]);
  const m = await lastMail();
  assert.equal(m.url, 'https://api.resend.com/emails');
  assert.equal(m.headers.Authorization, 'Bearer re_test_123');
  assert.deepEqual([m.body.from, m.body.to, m.body.reply_to], ['Roll Model <hello@mail.playrollmodel.com>', [em], 'support@playrollmodel.com']);
  assert.equal(m.body.subject, `Welcome to Roll Model, ${p.name}!`);
  assert.ok(m.body.html.includes(p.name) && m.body.text.includes(p.name));
  assert.match(m.body.text, /https:\/\/playrollmodel\.com\/confirm#t=[A-Za-z0-9_-]{40,}/);
  assert.ok(m.body.html.includes('https://playrollmodel.com/email/logo.png'));
  assert.ok(!/\{\{\w+\}\}/.test(m.body.html + m.body.text + m.body.subject), 'every value filled in');
  const t = tokenOf(m.body);
  assert.equal((await q("select count(*)::int n from public.mail_tokens where encode(hash, 'escape') like '%' || $1 || '%'", [t]))[0].n, 0); // (only its hash is kept)
  assert.equal((await q('select count(*)::int n from public.mail_log where user_id = $1 and kind = $2 and req is not null', [p.id, 'welcome']))[0].n, 1);
});

test('confirming: once, within 24 hours, and only for the email it was sent to', async () => {
  const p = await newPlayer('Conf'), em = mail('', 3);
  await call(player(p.id), 'rm_email_set', [em]);
  const t = tokenOf((await lastMail()).body);
  assert.deepEqual(await anon('rm_email_verify', ['not-a-real-token-at-all-xx']), { ok: false, why: 'bad' });
  assert.deepEqual(await anon('rm_email_verify', ["'; drop table x; --"]), { ok: false, why: 'bad' });
  assert.deepEqual(await anon('rm_email_verify', [t]), { ok: true, username: p.name });
  assert.equal((await call(player(p.id), 'rm_email_get')).verified, true);
  assert.deepEqual(await anon('rm_email_verify', [t]), { ok: false, why: 'used' });
  // the same confirmed email again changes nothing and sends nothing
  const n = (await sent()).length;
  assert.deepEqual(await call(player(p.id), 'rm_email_set', [em]), { ok: true, sent: false, verified: true });
  assert.equal((await sent()).length, n);
  // expired
  const p2 = await newPlayer('Exp'); await call(player(p2.id), 'rm_email_set', [mail('', 4)]);
  const t2 = tokenOf((await lastMail()).body);
  await q("update public.mail_tokens set expires_at = now() - interval '1 minute' where user_id = $1", [p2.id]);
  assert.deepEqual(await anon('rm_email_verify', [t2]), { ok: false, why: 'expired' });
  // the email changed after the link was sent: the old link is no good
  const p3 = await newPlayer('Chg'); await call(player(p3.id), 'rm_email_set', [mail('', 5)]);
  const t3 = tokenOf((await lastMail()).body);
  await call(player(p3.id), 'rm_email_set', [mail('', 6)]);
  assert.deepEqual(await anon('rm_email_verify', [t3]), { ok: false, why: 'bad' });
  assert.equal((await call(player(p3.id), 'rm_email_get')).verified, false);
  // sent again on request, not when confirmed
  assert.equal((await call(player(p3.id), 'rm_email_resend')).ok, true);
  assert.deepEqual(await call(player(p.id), 'rm_email_resend'), { ok: false, why: 'verified' });
});

async function confirmed(base) {
  const p = await newPlayer(base), em = mail('', 7);
  await call(player(p.id), 'rm_email_set', [em]);
  await anon('rm_email_verify', [tokenOf((await lastMail()).body)]);
  return { ...p, email: em };
}

test('Forgot password: never says whether an account exists; a link only to a confirmed email; 3 an hour', async () => {
  const p = await confirmed('Forg'), u = await newPlayer('Unconf');
  await call(player(u.id), 'rm_email_set', [mail('', 8)]); // (not confirmed)
  let n = (await sent()).length;
  for (const who of ['nobody_here_' + suffix(), 'ghost@example.com', '', 'x', u.name, null]) {
    assert.deepEqual(await anon('rm_reset_request', [who]), { ok: true }, String(who));
  }
  assert.equal((await sent()).length, n, 'nothing sent for unknown or unconfirmed accounts');
  assert.deepEqual(await anon('rm_reset_request', [p.name.toUpperCase()]), { ok: true });
  const m = await lastMail();
  assert.deepEqual(m.body.to, [p.email]); assert.equal(m.body.subject, 'Reset your Roll Model password');
  assert.match(m.body.text, /https:\/\/playrollmodel\.com\/reset#t=[A-Za-z0-9_-]{40,}/);
  assert.deepEqual(await anon('rm_reset_request', [p.email.toUpperCase()]), { ok: true }); // (by email too)
  assert.equal((await sent()).length, n + 2);
  assert.deepEqual(await anon('rm_reset_request', [p.name]), { ok: true });
  assert.deepEqual(await anon('rm_reset_request', [p.name]), { ok: true }); // (a 4th within the hour: answered the same, not sent)
  assert.equal((await sent()).length, n + 3);
  // only the newest link works
  assert.equal((await q("select count(*)::int n from public.mail_tokens where user_id = $1 and kind = 'reset'", [p.id]))[0].n, 1);
});

test('the reset link: a strong password, once, within 30 minutes; signed out everywhere; a "changed" email', async () => {
  const p = await confirmed('Rst');
  await q('insert into auth.sessions (id, user_id) values ($1, $2)', [uid(), p.id]);
  await anon('rm_reset_request', [p.name]);
  const t = tokenOf((await lastMail()).body);
  for (const pw of ['short1', 'nodigitshere', '1234567890', null]) assert.deepEqual(await anon('rm_reset_password', [t, pw]), { ok: false, why: 'weak' });
  assert.deepEqual(await anon('rm_reset_password', ['bogus-token-bogus-token-xx', 'GoodPass99']), { ok: false, why: 'bad' });
  const before = (await sent()).length;
  assert.deepEqual(await anon('rm_reset_password', [t, 'Brand-New-Paint-7']), { ok: true, username: p.name }); // (the weak tries didn't use it up)
  assert.equal((await q("select encrypted_password = extensions.crypt('Brand-New-Paint-7', encrypted_password) ok from auth.users where id = $1", [p.id]))[0].ok, true);
  assert.equal((await q('select count(*)::int n from auth.sessions where user_id = $1', [p.id]))[0].n, 0);
  assert.deepEqual(await anon('rm_reset_password', [t, 'Another-Pass-8']), { ok: false, why: 'used' });
  const after = await sent(); assert.equal(after.length, before + 1);
  const ch = after[after.length - 1].body;
  assert.equal(ch.subject, 'Your Roll Model password was changed'); assert.deepEqual(ch.to, [p.email]);
  assert.ok(ch.text.includes(p.name) && /UTC/.test(ch.text) && ch.text.includes('https://playrollmodel.com/forgot'));
  // expired
  await anon('rm_reset_request', [p.email]);
  const t2 = tokenOf((await lastMail()).body);
  await q("update public.mail_tokens set expires_at = now() - interval '1 second' where user_id = $1 and kind = 'reset'", [p.id]);
  assert.deepEqual(await anon('rm_reset_password', [t2, 'GoodPass99']), { ok: false, why: 'expired' });
});

test('"password changed" goes out however it changed, but not when an account first gets its password', async () => {
  const p = await confirmed('Note');
  let n = (await sent()).length;
  await q("update auth.users set encrypted_password = extensions.crypt('Changed-In-Game-1', extensions.gen_salt('bf')) where id = $1", [p.id]); // (the game, or Supabase)
  assert.equal((await sent()).length, n + 1); assert.equal((await lastMail()).body.subject, 'Your Roll Model password was changed');
  // a brand-new account setting its first password: nothing
  const id = await newUser(); n = (await sent()).length;
  await q("update auth.users set encrypted_password = '' where id = $1", [id]);
  await q("update auth.users set encrypted_password = extensions.crypt('First-Pass-1', extensions.gen_salt('bf')), is_anonymous = false where id = $1", [id]);
  assert.equal((await sent()).length, n);
  // nothing to send to: still changed, nothing goes out
  const u = await newPlayer('NoMail'); n = (await sent()).length;
  await q("update auth.users set encrypted_password = extensions.crypt('Whatever-1', extensions.gen_salt('bf')) where id = $1", [u.id]);
  assert.equal((await sent()).length, n);
});

test('emails switched off (no key, no website, or paused): everything still works, nothing is sent, and the game is told', async () => {
  const p = await newPlayer('Off');
  await q("delete from vault.secrets_stub where name = 'resend_api_key'");
  try {
    const n = (await sent()).length;
    assert.deepEqual(await call(player(p.id), 'rm_email_set', [mail('', 9)]), { ok: true, sent: false, verified: false });
    assert.equal((await call(player(p.id), 'rm_email_get')).mail, false);
    assert.equal((await sent()).length, n);
    assert.equal((await q("select note from public.mail_log where user_id = $1 order by id desc limit 1", [p.id]))[0].note, 'mail off');
  } finally { await q("insert into vault.secrets_stub (name, decrypted_secret) values ('resend_api_key', 're_test_123')"); }
  await q(`update public.rm_settings set v = v || '{"paused": true}' where k = 'mail'`);
  try { assert.equal((await call(player(p.id), 'rm_email_resend')).sent, false); }
  finally { await q(`update public.rm_settings set v = v || '{"paused": false}' where k = 'mail'`); }
  await q(`update public.rm_settings set v = v || '{"site": ""}' where k = 'mail'`);
  try { assert.equal((await call(player(p.id), 'rm_email_get')).mail, false); }
  finally { await q(`update public.rm_settings set v = v || '{"site": "https://playrollmodel.com/"}' where k = 'mail'`); }
});

test('the dashboard: a player\'s email, find by email, send a reset link; admins only', async () => {
  const aid = await newUser('boss_' + suffix() + '@example.com');
  await q("insert into public.rm_admins (id, note) values ($1, 'test')", [aid]);
  const A = adminClaims(aid), p = await confirmed('Supp'), u = await newPlayer('SuppNo');
  await rejects(call(player(p.id), 'adm_player_email', [p.id]), /not an admin/);
  await rejects(call(player(p.id), 'adm_email_reset', [p.id]), /not an admin/);
  await rejects(anon('adm_find_email', ['x@y.com']), /permission denied/);
  const e = await call(A, 'adm_player_email', [p.id]);
  assert.equal(e.email, p.email); assert.equal(e.verified, true);
  assert.equal(await call(A, 'adm_player_email', [u.id]), null);
  assert.deepEqual((await call(A, 'adm_find_email', [p.email.toUpperCase()])).map(x => x.name), [p.name]);
  assert.deepEqual(await call(A, 'adm_find_email', ['nobody@example.com']), []);
  assert.deepEqual(await call(A, 'adm_email_reset', [u.id]), { ok: false, why: 'no_email' });
  assert.deepEqual(await call(A, 'adm_email_reset', [aid]), { ok: false, why: 'admin' });
  assert.deepEqual(await call(A, 'adm_email_reset', [uid()]), { ok: false, why: 'missing' });
  assert.deepEqual(await call(A, 'adm_email_reset', [p.id]), { ok: true, sent: true });
  assert.equal((await lastMail()).body.subject, 'Reset your Roll Model password');
  const [log] = await call(A, 'adm_audit', [1]); assert.equal(log.action, 'email_reset'); assert.equal(log.target, p.id);
  await q('delete from public.rm_admins where id = $1', [aid]);
});

test('deleting an account takes its email, its links and its mail log with it', async () => {
  const p = await confirmed('Gone');
  await anon('rm_reset_request', [p.name]);
  assert.deepEqual(await call(player(p.id), 'rm_delete_me'), { ok: true });
  for (const t of ['public.account_emails']) assert.equal((await q(`select count(*)::int n from ${t} where id = $1`, [p.id]))[0].n, 0);
  for (const t of ['public.mail_tokens', 'public.mail_log']) assert.equal((await q(`select count(*)::int n from ${t} where user_id = $1`, [p.id]))[0].n, 0);
  assert.deepEqual(await anon('rm_reset_request', [p.email]), { ok: true }); // (and asking for it now sends nothing)
});
