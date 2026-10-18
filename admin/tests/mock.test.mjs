// The dev mock (dev/mock.mjs) against admin/API.md: production headers, the sign-in flow, every admin function's
// shape, the errors, the hourly limits, and the empty launch. If the mock drifts from the contract, the dashboard's
// browser tests would be testing the wrong thing, so this keeps it honest.

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { start, reset } from '../dev/mock.mjs';

const CATALOG = JSON.parse(readFileSync(new URL('../catalog.json', import.meta.url), 'utf8'));
const KEY = 'sb_publishable_mock_dev_only';
let server, B;

test.before(async () => {
  reset({ dataset: 'full' });
  server = await start({ port: 0, quiet: true });
  B = 'http://127.0.0.1:' + server.address().port;
});
test.after(() => new Promise((r) => server.close(r)));

async function call(path, { method = 'POST', body, token, key = KEY } = {}) {
  const res = await fetch(B + path, {
    method, headers: { ...(key ? { apikey: key } : {}), 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await res.text();
  let json;
  try { json = text ? JSON.parse(text) : undefined; } catch { json = text; }
  return { status: res.status, json, headers: res.headers };
}
const rpc = (fn, args, token) => call('/rest/v1/rpc/' + fn, { body: args ?? {}, token });
const control = (path, body) => fetch(B + '/__mock' + path, { method: body ? 'POST' : 'GET', body: body ? JSON.stringify(body) : undefined }).then((r) => r.json());

// Sign in all the way: password, then the code (enrolling first when needed). Returns the aal2 tokens.
async function signIn(email = 'owner@example.com', password = 'correct-horse-9') {
  const pw = await call('/auth/v1/token?grant_type=password', { body: { email, password } });
  assert.equal(pw.status, 200, JSON.stringify(pw.json));
  const t = pw.json.access_token;
  const user = await call('/auth/v1/user', { method: 'GET', token: t });
  let factor = (user.json.factors || []).find((f) => f.status === 'verified');
  if (!factor) {
    for (const f of user.json.factors || []) await call('/auth/v1/factors/' + f.id, { method: 'DELETE', token: t });
    factor = (await call('/auth/v1/factors', { body: { factor_type: 'totp', friendly_name: 'Roll Model admin' }, token: t })).json;
  }
  const ch = await call('/auth/v1/factors/' + factor.id + '/challenge', { token: t });
  const v = await call('/auth/v1/factors/' + factor.id + '/verify', { body: { challenge_id: ch.json.id, code: '123456' }, token: t });
  assert.equal(v.status, 200, JSON.stringify(v.json));
  return v.json;
}
const claims = (jwt) => JSON.parse(Buffer.from(jwt.split('.')[1], 'base64url').toString());

test('static files carry the production headers, and only the app is served', async () => {
  const res = await fetch(B + '/');
  assert.equal(res.status, 200);
  assert.equal(res.headers.get('content-security-policy'),
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'");
  assert.equal(res.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(res.headers.get('referrer-policy'), 'no-referrer');
  assert.equal(res.headers.get('x-frame-options'), 'DENY');
  for (const f of ['camera=()', 'microphone=()', 'geolocation=()', 'payment=()', 'usb=()']) assert.ok(res.headers.get('permissions-policy').includes(f), f);
  const html = await res.text();
  assert.doesNotMatch(html, /<script(?![^>]*\bsrc=)[^>]*>/i, 'no inline script');
  assert.doesNotMatch(html, /<style|\sstyle=|\son[a-z]+=/i, 'no inline style or handlers');
  for (const p of ['/app.css', '/js/main.js', '/js/pages/support.js', '/catalog.json', '/icon.svg']) assert.equal((await fetch(B + p)).status, 200, p);
  for (const p of ['/API.md', '/dev/mock.mjs', '/tests/mock.test.mjs', '/js/../dev/world.mjs', '/js/%2e%2e/dev/world.mjs', '/.git/config']) {
    assert.equal((await fetch(B + p)).status, 404, p);
  }
  assert.equal((await fetch(B + '/', { method: 'POST' })).status, 405);
});

test('config.js points at the mock, and never at Supabase', async () => {
  const res = await fetch(B + '/js/config.js');
  assert.match(res.headers.get('content-type'), /javascript/);
  const js = await res.text();
  assert.match(js, /SUPABASE_URL = location\.origin/);
  assert.doesNotMatch(js, /supabase\.co/);
  const real = readFileSync(new URL('../js/config.js', import.meta.url), 'utf8');
  assert.match(real, /https:\/\/nbemerxgukwwtrfgirfl\.supabase\.co/);
  assert.match(real, /export const DEV = null/);
});

test('every request needs the publishable key', async () => {
  const r = await call('/auth/v1/token?grant_type=password', { body: { email: 'owner@example.com', password: 'correct-horse-9' }, key: null });
  assert.equal(r.status, 401);
});

test('sign-in: wrong password, then password, enrol, a wrong code, the right code', async () => {
  reset({ dataset: 'full' });
  const bad = await call('/auth/v1/token?grant_type=password', { body: { email: 'admin@example.com', password: 'nope' } });
  assert.equal(bad.status, 400);
  assert.deepEqual(bad.json, { code: 400, error_code: 'invalid_credentials', msg: 'Invalid login credentials' });

  const pw = await call('/auth/v1/token?grant_type=password', { body: { email: 'admin@example.com', password: 'correct-horse-9' } });
  for (const k of ['access_token', 'refresh_token', 'expires_in', 'expires_at', 'user']) assert.ok(k in pw.json, k);
  const c = claims(pw.json.access_token);
  assert.equal(c.aal, 'aal1');
  for (const k of ['sub', 'email', 'aal', 'amr', 'exp']) assert.ok(k in c, k);
  const t = pw.json.access_token;

  const who = await rpc('adm_whoami', {}, t);
  assert.deepEqual(who.json, { id: c.sub, email: 'admin@example.com', aal: 'aal1', listed: true, admin: false, why: 'needs_code', code_at: null });
  const denied = await rpc('adm_overview', { p_days: 7 }, t);
  assert.equal(denied.status, 403);
  assert.deepEqual(denied.json, { code: '42501', details: null, hint: null, message: 'not an admin' });

  const user = await call('/auth/v1/user', { method: 'GET', token: t });
  assert.ok(!(user.json.factors || []).some((f) => f.status === 'verified'));
  const f = await call('/auth/v1/factors', { body: { factor_type: 'totp', friendly_name: 'Roll Model admin' }, token: t });
  assert.equal(f.json.type, 'totp');
  assert.match(f.json.totp.qr_code, /^data:image\/svg\+xml/);
  assert.match(f.json.totp.secret, /^[A-Z2-7]{16,}$/);
  // a second enrolment with the same name is refused until the unverified one is deleted
  const again = await call('/auth/v1/factors', { body: { factor_type: 'totp', friendly_name: 'Roll Model admin' }, token: t });
  assert.equal(again.json.error_code, 'mfa_factor_name_conflict');
  const ch = await call('/auth/v1/factors/' + f.json.id + '/challenge', { token: t });
  assert.ok(ch.json.id && ch.json.expires_at);
  const wrong = await call('/auth/v1/factors/' + f.json.id + '/verify', { body: { challenge_id: ch.json.id, code: '000000' }, token: t });
  assert.equal(wrong.status, 422);
  assert.deepEqual(wrong.json, { code: 422, error_code: 'mfa_verification_failed', msg: 'Invalid TOTP code entered' });
  const ok = await call('/auth/v1/factors/' + f.json.id + '/verify', { body: { challenge_id: ch.json.id, code: '123456' }, token: t });
  assert.equal(claims(ok.json.access_token).aal, 'aal2');
  const who2 = await rpc('adm_whoami', {}, ok.json.access_token);
  assert.equal(who2.json.admin, true);
  assert.equal(who2.json.why, null);
  assert.ok(Date.now() - Date.parse(who2.json.code_at) < 60000);
});

test('not an admin, and an old code: whoami says why', async () => {
  const p = await call('/auth/v1/token?grant_type=password', { body: { email: 'player@example.com', password: 'player-pass-1' } });
  const who = await rpc('adm_whoami', {}, p.json.access_token);
  assert.equal(who.json.listed, false);
  assert.equal(who.json.why, 'not_listed');
  const stale = await signIn('stale@example.com');
  const w = await rpc('adm_whoami', {}, stale.access_token);
  assert.equal(w.json.why, 'stale');
  assert.equal((await rpc('adm_overview', {}, stale.access_token)).status, 403);
});

test('refresh: the new token keeps aal2, the old refresh token is used up; logout ends the session', async () => {
  const s = await signIn();
  const r = await call('/auth/v1/token?grant_type=refresh_token', { body: { refresh_token: s.refresh_token } });
  assert.equal(r.status, 200);
  assert.equal(claims(r.json.access_token).aal, 'aal2');
  const reused = await call('/auth/v1/token?grant_type=refresh_token', { body: { refresh_token: s.refresh_token } });
  assert.equal(reused.status, 400);
  assert.equal(reused.json.error_code, 'refresh_token_not_found');
  assert.equal((await call('/auth/v1/logout', { token: r.json.access_token })).status, 204);
  // rule 4: the token is still a valid JWT, but its session has ended: whoami says stale, the functions refuse
  const after = await rpc('adm_whoami', {}, r.json.access_token);
  assert.equal(after.status, 200);
  assert.equal(after.json.why, 'stale');
  assert.equal((await rpc('adm_prices', {}, r.json.access_token)).status, 403);
  assert.equal((await call('/auth/v1/user', { method: 'GET', token: r.json.access_token })).json.error_code, 'session_not_found');
});

test('the admin functions answer with the documented shapes', async () => {
  reset({ dataset: 'full' });
  const t = (await signIn()).access_token;

  const o = (await rpc('adm_overview', { p_days: 30 }, t)).json;
  for (const k of ['now', 'online', 'dau', 'wau', 'mau', 'installs', 'accounts', 'new_today', 'new_7d', 'sessions_today', 'avg_session_secs', 'retention', 'days']) assert.ok(k in o, k);
  for (const k of ['d1', 'd7', 'd30', 'cohort_d1', 'cohort_d7', 'cohort_d30']) assert.ok(k in o.retention, k);
  assert.equal(o.days.length, 30);
  assert.ok(o.days[0].day < o.days[29].day, 'oldest first');
  for (const k of ['day', 'dau', 'new', 'sessions', 'matches', 'ads', 'buys', 'dabs_spent', 'dabs_earned', 'play_secs']) assert.ok(k in o.days[0], k);
  assert.ok(o.installs > 2000 && o.dau > 0 && o.wau >= o.dau && o.mau >= o.wau);
  assert.equal((await rpc('adm_overview', { p_days: 999 }, t)).json.days.length, 180, 'p_days is clamped');

  const m = (await rpc('adm_modes', { p_days: 7 }, t)).json;
  for (const k of ['mode', 'plays', 'wins', 'losses', 'draws', 'players', 'avg_secs', 'avg_cov', 'online']) assert.ok(k in m.modes[0], k);
  assert.equal(m.days.length, 7);
  for (const k of ['solo', 'duel', 'trio', 'ffa', 'duo', 'online']) assert.ok(k in m.days[0], k);
  assert.ok(m.stages.length && m.diffs.length);
  assert.ok(m.stages[0].plays >= m.stages.at(-1).plays, 'most first');

  const steps = CATALOG.tutorial.map((x) => x.id);
  const p = (await rpc('adm_progress', { p_steps: steps }, t)).json;
  assert.deepEqual(p.tutorial.map((x) => x.step), steps);
  for (const k of ['ranks', 'tutorial', 'active_7d', 'median_rank', 'done_pct']) assert.ok(k in p, k);
  assert.ok(p.ranks.every((r) => r.rank >= 1 && r.rank <= 50 && r.active <= r.players));
  const partial = (await rpc('adm_progress', { p_steps: ['match', 'intro'] }, t)).json;
  assert.deepEqual(partial.tutorial.slice(0, 2).map((x) => x.step), ['match', 'intro'], 'p_steps order, the rest after');
  assert.equal(partial.tutorial.length, steps.length);

  const e = (await rpc('adm_economy', { p_days: 30 }, t)).json;
  for (const k of ['item', 'views', 'afford_views', 'buys', 'dabs', 'buyers_7d', 'price', 'last_buy']) assert.ok(k in e.items[0], k);
  for (const k of ['dabs_earned', 'dabs_spent', 'buys', 'median_balance']) assert.ok(k in e.totals, k);
  assert.ok(e.items.every((r) => r.afford_views <= r.views));
  assert.ok(e.strokes.length && e.earn.length);
  assert.ok(e.earn.every((x) => ['match', 'comm', 'board', 'lesson', 'other'].includes(x.src)));
  assert.equal(e.items.find((r) => r.item === 'cape').price, 980, 'live price');
  assert.equal(e.items.find((r) => r.item === 'bowtie').price, null, 'no live price: null');

  const a = (await rpc('adm_ads', { p_days: 30 }, t)).json;
  assert.deepEqual(a.placements.map((x) => x.placement).sort(), ['craft', 'lesson']);
  assert.ok(a.placements.every((x) => x.shown <= x.asked && x.rewarded <= x.shown));

  assert.deepEqual((await rpc('adm_iap', { p_days: 30 }, t)).json, { products: [], days: [] });
  const prices = (await rpc('adm_prices', {}, t)).json;
  assert.deepEqual(prices.map((x) => x.item).sort(), ['cape', 'tophat']);
  for (const k of ['item', 'price', 'updated_at', 'updated_by']) assert.ok(k in prices[0], k);
});

test('PostgREST refuses wrong argument names and bad values', async () => {
  const t = (await signIn()).access_token;
  const r = await rpc('adm_overview', { days: 7 }, t);
  assert.equal(r.status, 404);
  assert.equal(r.json.code, 'PGRST202');
  assert.equal((await rpc('adm_set_price', { p_item: 'cape' }, t)).json.code, 'PGRST202', 'p_price is required (null clears)');
  assert.equal((await rpc('adm_player', { p_id: 'not-a-uuid' }, t)).json.code, '22P02');
  assert.equal((await rpc('adm_nope', {}, t)).status, 404);
  assert.equal((await rpc('adm_whoami', {})).status, 401, 'no token');
});

test('prices: set, refuse bad input, clear, all in the audit log', async () => {
  reset({ dataset: 'full' });
  const t = (await signIn()).access_token;
  assert.deepEqual((await rpc('adm_set_price', { p_item: 'tophat', p_price: 425 }, t)).json, { ok: true });
  assert.deepEqual((await rpc('adm_set_price', { p_item: 'Top Hat', p_price: 425 }, t)).json, { ok: false, why: 'item' });
  assert.deepEqual((await rpc('adm_set_price', { p_item: 'tophat', p_price: 100001 }, t)).json, { ok: false, why: 'range' });
  assert.deepEqual((await rpc('adm_set_price', { p_item: 'tophat', p_price: -1 }, t)).json, { ok: false, why: 'range' });
  assert.equal((await rpc('adm_economy', { p_days: 7 }, t)).json.items.find((r) => r.item === 'tophat').price, 425);
  assert.deepEqual((await rpc('adm_set_price', { p_item: 'tophat', p_price: null }, t)).json, { ok: true });
  assert.ok(!(await rpc('adm_prices', {}, t)).json.some((x) => x.item === 'tophat'));
  const log = (await rpc('adm_audit', { p_limit: 2 }, t)).json;
  assert.equal(log.length, 2);
  assert.deepEqual(log.map((r) => [r.action, r.target, r.detail]), [['set_price', 'tophat', { from: 425, to: null }], ['set_price', 'tophat', { from: 450, to: 425 }]]);
  assert.equal(log[0].admin, 'owner@example.com');
});

test('support: find, look, reset, sign out, delete, and every why', async () => {
  reset({ dataset: 'full' });
  const t = (await signIn()).access_token;
  const byName = (await rpc('adm_find', { p_q: 'dus' }, t)).json;
  assert.equal(byName[0].name, 'Dusk');
  assert.ok(byName.length <= 25);
  for (const k of ['id', 'name', 'code', 'rank', 'account', 'created_at', 'last_seen']) assert.ok(k in byName[0], k);
  assert.equal((await rpc('adm_find', { p_q: 'abcd 2345' }, t)).json[0].name, 'Dusk', 'friend code, spaces ignored');
  const dusk = byName[0];
  assert.equal((await rpc('adm_find', { p_q: dusk.id }, t)).json[0].name, 'Dusk', 'user id');
  assert.deepEqual((await rpc('adm_find', { p_q: 'd' }, t)).json, [], 'too short');

  const p = (await rpc('adm_player', { p_id: dusk.id }, t)).json;
  for (const k of ['id', 'name', 'code', 'rank', 'look', 'account', 'anonymous', 'created_at', 'last_sign_in_at', 'last_seen', 'status', 'friends', 'blocked_by_them', 'details', 'save', 'installs', 'audit']) assert.ok(k in p, k);
  assert.deepEqual(Object.keys(p.details).sort(), ['agreed_at', 'birth_year', 'first_name', 'last_name', 'terms']);
  assert.equal((await rpc('adm_player', { p_id: '00000000-0000-4000-8000-000000000000' }, t)).json, null);

  assert.deepEqual((await rpc('adm_set_password', { p_id: dusk.id, p_password: 'short' }, t)).json, { ok: false, why: 'weak' });
  assert.deepEqual((await rpc('adm_set_password', { p_id: dusk.id, p_password: 'Newpass2026x' }, t)).json, { ok: true });
  const anon = (await rpc('adm_find', { p_q: 'Bramble' }, t)).json[0];
  assert.deepEqual((await rpc('adm_set_password', { p_id: anon.id, p_password: 'Newpass2026x' }, t)).json, { ok: false, why: 'anonymous' });
  const admin = (await rpc('adm_find', { p_q: 'RollModelHQ' }, t)).json[0];
  assert.equal((await rpc('adm_player', { p_id: admin.id }, t)).json.admin, true);
  for (const [fn, args] of [['adm_set_password', { p_password: 'Newpass2026x' }], ['adm_signout', {}], ['adm_delete_player', { p_confirm: 'rollmodelhq' }]]) {
    assert.deepEqual((await rpc(fn, { p_id: admin.id, ...args }, t)).json, { ok: false, why: 'admin' }, fn);
  }
  const so = (await rpc('adm_signout', { p_id: dusk.id }, t)).json;
  assert.equal(so.ok, true);
  assert.equal(typeof so.sessions, 'number');
  assert.deepEqual((await rpc('adm_delete_player', { p_id: dusk.id, p_confirm: 'Dawn' }, t)).json, { ok: false, why: 'confirm' });
  assert.deepEqual((await rpc('adm_delete_player', { p_id: dusk.id, p_confirm: 'dUSK' }, t)).json, { ok: true });
  assert.deepEqual((await rpc('adm_signout', { p_id: dusk.id }, t)).json, { ok: false, why: 'missing' });
  assert.ok(!(await rpc('adm_find', { p_q: 'Dusk' }, t)).json.some((x) => x.id === dusk.id));
  // a player with no username is confirmed with their user id
  const nameless = (await rpc('adm_find', { p_q: 'QRST6789' }, t)).json[0];
  assert.equal(nameless.name, null);
  assert.deepEqual((await rpc('adm_delete_player', { p_id: nameless.id, p_confirm: nameless.id.toUpperCase() }, t)).json, { ok: true });

  const log = (await rpc('adm_audit', {}, t)).json;
  assert.deepEqual(log.slice(0, 4).map((r) => r.action), ['delete_player', 'delete_player', 'signout', 'set_password']);
  assert.ok(!JSON.stringify(log).includes('Newpass2026x'), 'the password is never logged');
  assert.deepEqual(log[1].detail, { id: dusk.id });
  assert.ok(!JSON.stringify(log).includes('"Dusk"'), 'a deleted player\'s name comes off the audit log, in every row about them');
});

test('hourly limits answer slow_down and change nothing', async () => {
  reset({ dataset: 'full' });
  const t = (await signIn()).access_token;
  await control('/config', { limits: { set_price: 1 } });
  assert.deepEqual((await rpc('adm_set_price', { p_item: 'flower', p_price: 150 }, t)).json, { ok: true });
  assert.deepEqual((await rpc('adm_set_price', { p_item: 'flower', p_price: 155 }, t)).json, { ok: false, why: 'slow_down' });
  assert.equal((await rpc('adm_prices', {}, t)).json.find((x) => x.item === 'flower').price, 150);
});

test('a database not set up for admin sign-in: whoami says "setup", and no one is an admin', async () => {
  reset({ dataset: 'full' });
  const t = (await signIn()).access_token;
  await control('/config', { setup: true });
  const who = (await rpc('adm_whoami', {}, t)).json;
  assert.equal(who.admin, false);
  assert.equal(who.why, 'setup');
  assert.equal((await rpc('adm_prices', {}, t)).status, 403);
  await control('/config', { setup: false });
  assert.equal((await rpc('adm_prices', {}, t)).status, 200);
});

test('removing someone from the admins shuts them out at once', async () => {
  reset({ dataset: 'full' });
  const t = (await signIn()).access_token;
  assert.equal((await rpc('adm_prices', {}, t)).status, 200);
  await control('/config', { unlist: 'owner@example.com' });
  assert.equal((await rpc('adm_prices', {}, t)).status, 403);
  assert.equal((await rpc('adm_whoami', {}, t)).json.why, 'not_listed');
});

test('a brand-new launch: zeros, nulls and empty lists', async () => {
  reset({ dataset: 'empty' });
  const t = (await signIn()).access_token;
  const o = (await rpc('adm_overview', { p_days: 7 }, t)).json;
  assert.equal(o.installs, 0);
  assert.equal(o.retention.d1, null);
  assert.equal(o.days.length, 7, 'every day present');
  assert.ok(o.days.every((d) => d.dau === 0 && d.new === 0));
  assert.deepEqual((await rpc('adm_modes', { p_days: 7 }, t)).json.modes, []);
  const p = (await rpc('adm_progress', { p_steps: ['intro', 'match'] }, t)).json;
  assert.deepEqual(p.ranks, []);
  assert.ok(p.tutorial.every((r) => r.reached === 0));
  assert.equal(p.median_rank, null);
  const e = (await rpc('adm_economy', { p_days: 7 }, t)).json;
  assert.deepEqual(e.items, []);
  assert.equal(e.totals.median_balance, null);
  assert.deepEqual((await rpc('adm_ads', { p_days: 7 }, t)).json.placements, []);
  assert.deepEqual((await rpc('adm_find', { p_q: 'dusk' }, t)).json, []);
  assert.deepEqual((await rpc('adm_audit', {}, t)).json, []);
  assert.deepEqual((await rpc('adm_prices', {}, t)).json, []);
  reset({ dataset: 'full' });
});
