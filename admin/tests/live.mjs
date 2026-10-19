#!/usr/bin/env node
// The dashboard against the real database code: admin/ in Chromium, the migrations on a local Postgres, and
// supabase/tests/standin.mjs in front of them as Supabase (Auth with real authenticator codes, and the database calls).
//   1. Start the local Postgres and the stand-in as supabase/README.md says ("Testing it without the real project").
//   2. node admin/tests/live.mjs [screenshot folder]
//      (STANDIN=http://127.0.0.1:54330  PGURL=postgres://postgres@127.0.0.1:54329/rmtest  KEY=test-publishable-key)
// The dashboard is served here with its production headers, and talks to the stand-in through this server (same origin,
// so the real Content Security Policy applies unchanged). It makes a throwaway admin and players (Zqtest_...) and deletes
// them at the end. It never reaches *.supabase.co.

import http from 'node:http';
import { createRequire } from 'node:module';
import { createHmac, randomUUID } from 'node:crypto';
import { readFile, mkdir } from 'node:fs/promises';
import { join, extname, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const require = createRequire(import.meta.url);
const ROOT = fileURLToPath(new URL('..', import.meta.url)); // admin/
const STANDIN = process.env.STANDIN || 'http://127.0.0.1:54330';
const KEY = process.env.KEY || 'test-publishable-key';
const SHOTS = process.argv[2] || join(tmpdir(), 'rollmodel-admin-live');
await mkdir(SHOTS, { recursive: true });

function load(names) { for (const n of names) { try { return require(n); } catch { /* next */ } } throw new Error('missing: ' + names[0]); }
const pg = load(['pg', join(ROOT, '../supabase/tests/node_modules/pg')]);
const { chromium } = load(['playwright', '/opt/node-tools/node_modules/playwright', 'playwright-core']);
const db = new pg.Pool({ connectionString: process.env.PGURL || 'postgres://postgres@127.0.0.1:54329/rmtest', max: 3 });
const q = async (sql, params) => (await db.query(sql, params)).rows;

// ---------------------------------------------------------------- the authenticator app (RFC 6238)
const B32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
function fromB32(s) {
  let bits = 0, v = 0; const out = [];
  for (const ch of String(s).replace(/[\s=]+/g, '').toUpperCase()) { v = (v << 5) | B32.indexOf(ch); bits += 5; if (bits >= 8) { out.push((v >>> (bits - 8)) & 255); bits -= 8; } v &= (1 << bits) - 1; }
  return Buffer.from(out);
}
function totp(secret, at = Date.now()) {
  const c = Buffer.alloc(8); c.writeBigUInt64BE(BigInt(Math.floor(at / 30000)));
  const h = createHmac('sha1', fromB32(secret)).update(c).digest(), o = h[h.length - 1] & 15;
  return String((((h[o] & 127) << 24) | (h[o + 1] << 16) | (h[o + 2] << 8) | h[o + 3]) % 1e6).padStart(6, '0');
}

// ---------------------------------------------------------------- the site, with its headers, and the stand-in behind it
const HEADERS = {};
for (const line of (await readFile(join(ROOT, 'deploy/_headers'), 'utf8')).split('\n')) {
  const m = /^\s+([A-Za-z-]+):\s*(.+)$/.exec(line); if (m) HEADERS[m[1]] = m[2];
}
delete HEADERS['Strict-Transport-Security']; // (plain http here)
HEADERS['Content-Security-Policy'] = HEADERS['Content-Security-Policy'].replace('; upgrade-insecure-requests', '');
const CONFIG = "export const SUPABASE_URL = location.origin;\nexport const PUBLISHABLE_KEY = '" + KEY + "';\nexport const DEV = null;\n";
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.svg': 'image/svg+xml' };
const SERVED = /^\/(index\.html|app\.css|icon\.svg|catalog\.json|js\/[a-z]+\.js|js\/pages\/[a-z]+\.js)$/;

const server = http.createServer(async (req, res) => {
  const path = new URL(req.url, 'http://x').pathname;
  if (path.startsWith('/auth/v1/') || path.startsWith('/rest/v1/')) {
    const up = http.request(STANDIN + req.url, { method: req.method, headers: { ...req.headers, host: new URL(STANDIN).host } }, (r) => {
      res.writeHead(r.statusCode, r.headers); r.pipe(res);
    });
    up.on('error', () => { res.writeHead(502); res.end(); });
    return req.pipe(up);
  }
  const p = path === '/' ? '/index.html' : path;
  if (p === '/js/config.js') { res.writeHead(200, { ...HEADERS, 'Content-Type': TYPES['.js'] }); return res.end(CONFIG); }
  if (!SERVED.test(p)) { res.writeHead(404, HEADERS); return res.end('not here'); }
  try {
    const body = await readFile(join(ROOT, normalize(p)));
    res.writeHead(200, { ...HEADERS, 'Content-Type': TYPES[extname(p)] || 'application/octet-stream' }); res.end(body);
  } catch { res.writeHead(404, HEADERS); res.end('not here'); }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const B = 'http://127.0.0.1:' + server.address().port;
const rpc = async (fn, args = {}, token) => {
  const r = await fetch(STANDIN + '/rest/v1/rpc/' + fn, { method: 'POST', headers: { apikey: KEY, 'Content-Type': 'application/json', ...(token ? { Authorization: 'Bearer ' + token } : {}) }, body: JSON.stringify(args) });
  return { status: r.status, json: await r.json().catch(() => null) };
};
const signIn = async (email, password) => {
  const r = await fetch(STANDIN + '/auth/v1/token?grant_type=password', { method: 'POST', headers: { apikey: KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ email, password }) });
  return { status: r.status, json: await r.json().catch(() => null) };
};

// ---------------------------------------------------------------- throwaway people
const n = String(Date.now()).slice(-7).replace(/[0-9]/g, (d) => 'bcdfghjlmn'[d]);
const made = [];
async function newUser(email, password) {
  const id = randomUUID(); made.push(id);
  await q("insert into auth.users (id, email, is_anonymous, encrypted_password) values ($1, $2, false, extensions.crypt($3, extensions.gen_salt('bf')))", [id, email, password]);
  return id;
}
// a player with a username, an account (with details), and a confirmed email
async function newPlayer(base, email) {
  const id = await newUser(null, 'Old-pass-' + n + '1');
  await q("update auth.users set email = 'u' || replace(id::text, '-', '') || '@rollmodel.invalid' where id = $1", [id]);
  const as = async (sql, params) => {
    const c = await db.connect();
    try {
      await c.query('begin'); await c.query("select set_config('request.jwt.claims', $1, true)", [JSON.stringify({ sub: id, role: 'authenticated' })]);
      await c.query('set local role authenticated'); const r = await c.query(sql, params); await c.query('commit'); return r.rows[0].r;
    } catch (e) { await c.query('rollback').catch(() => {}); throw e; } finally { c.release(); }
  };
  const me = await as('select public.rm_me($1, $2::jsonb, $3) as r', [base + '_' + n, '{}', 4]);
  if (!me.ok) throw new Error('rm_me: ' + JSON.stringify(me));
  const acc = await as('select public.rm_account_save($1, $2, $3::date, $4) as r', ['Dana', 'Lee', '2001-12-31', '2026-10']);
  if (!acc.ok) throw new Error('rm_account_save: ' + JSON.stringify(acc));
  if (email) {
    const e = await as('select public.rm_email_set($1) as r', [email]);
    if (!e.ok) throw new Error('rm_email_set: ' + JSON.stringify(e));
    await q('update public.account_emails set verified_at = now() where id = $1', [id]);
  }
  const login = (await q('select email from auth.users where id = $1', [id]))[0].email;
  return { id, name: me.name, login, password: 'Old-pass-' + n + '1' };
}

// ---------------------------------------------------------------- checks
let passed = 0;
const problems = [];
let allowed = [];
const check = (cond, msg) => { if (!cond) throw new Error(msg); };
async function step(name, fn) { const t = Date.now(); await fn(); passed++; console.log('ok  ' + name + ' (' + (Date.now() - t) + ' ms)'); }
async function expecting(patterns, page, fn) { allowed = patterns; try { return await fn(); } finally { await page.waitForTimeout(200); allowed = []; } }
const FAILED = (s) => new RegExp('status of ' + s);
const settled = (page) => page.waitForFunction(() => {
  const b = document.querySelector('.pagebody');
  return b && b.childElementCount > 0 && !b.querySelector('.loading') && !b.hasAttribute('aria-busy');
}, null, { timeout: 20000 }).then(() => page.waitForTimeout(250));
const go = async (page, id) => { await page.evaluate((h) => { location.hash = h; }, '#' + id); await settled(page); };
const text = (page, sel) => page.$eval(sel, (el) => el.textContent.replace(/\s+/g, ' ').trim());
const shot = (page, name) => page.screenshot({ path: join(SHOTS, name + '.png'), fullPage: true });

const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
async function open() {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'en-GB', timezoneId: 'UTC' });
  await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: B });
  await ctx.route('**/*supabase.co/**', (route) => { problems.push('a request to Supabase: ' + route.request().url()); route.abort(); });
  const page = await ctx.newPage();
  await page.addInitScript(() => document.addEventListener('securitypolicyviolation', (e) => console.error('CSP violation: ' + e.violatedDirective + ' ' + e.blockedURI)));
  page.on('console', (m) => { if (m.type() === 'error' && !allowed.some((re) => re.test(m.text()))) problems.push('console: ' + m.text()); });
  page.on('pageerror', (e) => problems.push('page error: ' + e.message));
  return { ctx, page };
}
async function passwordStep(page, email, password) {
  await page.goto(B + '/');
  await page.waitForSelector('input[type=email]');
  await page.fill('input[type=email]', email);
  await page.fill('input[type=password]', password);
  await page.click('form button[type=submit]');
}

const adminEmail = 'zqadmin_' + n + '@example.com', adminPw = 'Live-admin-' + n + '7';
let adminId, dusk, dawn, secret = '';
try {
  await step('setup: a throwaway admin, and two players with accounts and confirmed emails', async () => {
    adminId = await newUser(adminEmail, adminPw);
    await q("insert into public.rm_admins (id, note) values ($1, 'live test')", [adminId]);
    dusk = await newPlayer('Zqtest', 'zqdusk_' + n + '@example.com');
    dawn = await newPlayer('Zqgone', 'zqdawn_' + n + '@example.com');
    await q("insert into vault.secrets_stub (name, decrypted_secret) values ('resend_api_key', 're_test_live') on conflict (name) do nothing");
    const mail = (await q("select v from public.rm_settings where k = 'mail'"))[0].v;
    check(mail.site && mail.sender && !mail.paused, 'the mail settings are set (run supabase/tests first): ' + JSON.stringify(mail));
  });

  const { page } = await open();

  await step('a player (not an admin) is refused after the password, before any authenticator', async () => {
    await passwordStep(page, dusk.login, dusk.password);
    await page.waitForSelector('.form-error:not([hidden]), .banner', { timeout: 15000 });
    const t = await page.evaluate(() => document.body.innerText);
    check(/not an admin|isn't an admin|admin/i.test(t), 'refused: ' + t.slice(0, 200));
    check(!(await page.$('img.qr')), 'no authenticator set up for a player');
  });

  await step('the admin: password, then the authenticator set up with a real code', async () => {
    await passwordStep(page, adminEmail, adminPw);
    await page.waitForSelector('img.qr', { timeout: 15000 });
    check(await page.$eval('img.qr', (img) => img.naturalWidth > 0), 'the QR code loads under the CSP');
    secret = (await text(page, 'code.secret')).replace(/\s+/g, '');
    check(/^[A-Z2-7]{16,}$/.test(secret), 'the key: ' + secret);
    await page.fill('.code-input', String((Number(totp(secret)) + 1) % 1e6).padStart(6, '0'));
    await expecting([FAILED(422)], page, async () => {
      await page.click('form button[type=submit]');
      await page.waitForFunction(() => /didn't work/.test(document.querySelector('.form-error')?.textContent || ''));
    });
    await page.fill('.code-input', totp(secret));
    await page.click('form button[type=submit]');
    await page.waitForSelector('.shell', { timeout: 15000 });
    await settled(page);
    const who = (await q('select count(*)::int as c from auth.sessions where user_id = $1', [adminId]))[0].c;
    check(who >= 1, 'a live session for the admin');
  });

  await step('every page loads from the real functions, with nothing broken', async () => {
    for (const id of ['overview', 'players', 'modes', 'economy', 'ads', 'purchases', 'insights', 'support', 'audit']) {
      await go(page, id);
      check(!(await page.$('.failure')), id + ': an error state: ' + (await page.evaluate(() => document.querySelector('.failure')?.innerText || '')));
      await shot(page, 'live-' + id);
    }
  });

  await step('a price set here reaches the game (rm_config), then back to the default', async () => {
    await go(page, 'economy');
    await page.click('button[aria-label="Edit the price of Top hat"]');
    await page.waitForSelector('dialog .price-input');
    await page.fill('dialog .price-input', '425');
    await page.click('dialog button:has-text("Review")');
    await page.waitForSelector('dialog .compare');
    await page.click('dialog button:has-text("Set price")');
    await page.waitForSelector('.toast:has-text("now costs 425 dabs")');
    const cfg = (await rpc('rm_config')).json;
    check(cfg && cfg.prices && cfg.prices.tophat === 425, 'the game gets 425: ' + JSON.stringify(cfg));
    await settled(page);
    await page.click('button[aria-label="Use the default price of Top hat"]');
    await page.waitForSelector('dialog .compare');
    await page.click('dialog button:has-text("Use the default")');
    await page.waitForSelector('.toast:has-text("back to its default price")');
    const cfg2 = (await rpc('rm_config')).json;
    check(!cfg2.prices || cfg2.prices.tophat == null, 'the default again: ' + JSON.stringify(cfg2));
  });

  await step('support: find the player by name and by email; their details and confirmed email', async () => {
    await go(page, 'support?q=' + encodeURIComponent(dusk.name));
    await page.click('.pagebody .tbl a >> text="' + dusk.name + '"');
    await settled(page);
    check((await text(page, '.player-name')) === dusk.name, 'the player opens');
    const facts = await text(page, '.facts');
    check(facts.includes('zqdusk_' + n + '@example.com') && /Confirmed/.test(facts) && /Dana/.test(facts) && /2001/.test(facts), 'details and email: ' + facts);
    await go(page, 'support?q=' + encodeURIComponent('ZQDUSK_' + n + '@Example.com'));
    check(await page.$eval('.pagebody .tbl tbody', (b) => b.querySelectorAll('tr').length) === 1, 'one player for the email');
    await page.click('.pagebody .tbl a >> text="' + dusk.name + '"');
    await settled(page);
    await shot(page, 'live-support-player');
  });

  await step('Send reset link: the reset email goes to their confirmed address', async () => {
    await q('truncate net.sent');
    await page.click('.player-actions button:has-text("Send reset link")');
    await page.click('dialog button:has-text("Send link")');
    await page.waitForSelector('dialog .ok-line');
    await page.click('dialog button:has-text("Done")');
    await settled(page);
    const sent = await q('select body from net.sent order by id');
    check(sent.length === 1, 'one email: ' + sent.length);
    const b = sent[0].body;
    check(JSON.stringify(b.to).includes('zqdusk_' + n + '@example.com') && /reset/i.test(b.subject) && /#t=/.test(b.text), 'a reset email to them: ' + b.subject);
  });

  await step('Reset password: a strong one, which logs in, and their old sessions end', async () => {
    const before = await signIn(dusk.login, dusk.password);
    check(before.status === 200, 'the old password worked before');
    await page.click('.player-actions button:has-text("Reset password")');
    await page.click('dialog button:has-text("Next")');
    await page.click('dialog button:has-text("Set password")');
    await page.waitForSelector('dialog .password-out');
    const pw = await page.$eval('dialog .password-out', (i) => i.value);
    await page.click('dialog button:has-text("Done")');
    await settled(page);
    check((await signIn(dusk.login, pw)).status === 200, 'the new password logs in');
    check((await signIn(dusk.login, dusk.password)).status !== 200, 'the old one no longer does');
    const r = await fetch(STANDIN + '/auth/v1/token?grant_type=refresh_token', { method: 'POST', headers: { apikey: KEY, 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh_token: before.json.refresh_token }) });
    check(r.status !== 200, 'the session from before is ended');
  });

  await step('Sign out everywhere: their sessions end', async () => {
    // (the new password's sign-in in the step before left them a session)
    const live = (await q('select count(*)::int as c from auth.sessions where user_id = $1', [dusk.id]))[0].c;
    await page.click('.player-actions button:has-text("Sign out everywhere")');
    await page.click('dialog button:has-text("Sign out everywhere")');
    await page.waitForSelector('dialog .ok-line');
    await page.click('dialog button:has-text("Done")');
    await settled(page);
    check((await q('select count(*)::int as c from auth.sessions where user_id = $1', [dusk.id]))[0].c === 0, 'no sessions left (there were ' + live + ')');
  });

  await step('Delete account: typed confirmation, and everything of theirs is gone', async () => {
    await go(page, 'support?q=' + encodeURIComponent(dawn.name));
    await page.click('.pagebody .tbl a >> text="' + dawn.name + '"');
    await settled(page);
    await page.click('button:has-text("Delete account")');
    await page.fill('dialog input', dawn.name.toLowerCase());
    await page.click('dialog button:has-text("Delete account")');
    await page.waitForSelector('.toast:has-text("Deleted")');
    check((await q('select count(*)::int as c from auth.users where id = $1', [dawn.id]))[0].c === 0, 'the user is gone');
    check((await q('select count(*)::int as c from public.account_emails where id = $1', [dawn.id]))[0].c === 0, 'their email is gone');
  });

  await step('the audit log shows every change, in plain words', async () => {
    await go(page, 'audit');
    const t = await text(page, '.pagebody');
    for (const w of ['Changed a price', 'Emailed a reset link', 'Reset a password', 'Signed a player out everywhere', 'Deleted an account']) check(t.includes(w), 'audit has "' + w + '"');
    check(!t.includes(dawn.name), "a deleted player's name is gone from the log");
    await shot(page, 'live-audit');
  });

  await step('a database not set up for admin sign-in says so (sign-ins unreadable to the admin check)', async () => {
    // as when the database's owner can't read auth.sessions: _sessions_ok() answers false for a moment, then is put back as it was
    const def = (await q("select pg_get_functiondef('public._sessions_ok()'::regprocedure) as d"))[0].d;
    await q("create or replace function public._sessions_ok() returns boolean language sql stable security definer set search_path = '' as $$ select false $$");
    try {
      await expecting([FAILED(403)], page, async () => {
        await page.reload();
        await page.waitForFunction(() => /set up/i.test(document.body.innerText), null, { timeout: 15000 });
      });
    } finally { await q(def); }
    check((await q('select public._sessions_ok() as ok'))[0].ok === true, 'put back');
  });

  await step('Sign out ends the session on the server', async () => {
    // (the "set up" step above signed the dashboard out; sign in again with a fresh code, then sign out)
    await passwordStep(page, adminEmail, adminPw);
    await page.waitForSelector('.code-input', { timeout: 15000 });
    await page.waitForTimeout(31000 - (Date.now() % 30000)); // (a new 30-second window: the stand-in takes each code once per challenge)
    await page.fill('.code-input', totp(secret));
    await page.click('form button[type=submit]');
    await page.waitForSelector('.shell', { timeout: 15000 });
    const live = (await q('select count(*)::int as c from auth.sessions where user_id = $1', [adminId]))[0].c;
    await page.locator('button:has-text("Sign out"):visible').first().click();
    await page.waitForSelector('input[type=email]');
    await page.waitForTimeout(500);
    check((await q('select count(*)::int as c from auth.sessions where user_id = $1', [adminId]))[0].c === live - 1, 'one session fewer');
  });

  check(!problems.length, 'problems:\n  ' + problems.join('\n  '));
  console.log('\n' + passed + ' steps passed. Screenshots: ' + SHOTS);
} catch (e) {
  console.error('\nFAILED after ' + passed + ' steps: ' + e.message + (problems.length ? '\n  ' + problems.join('\n  ') : ''));
  process.exitCode = 1;
} finally {
  // the throwaway people go, with everything of theirs
  for (const id of made) {
    await q('delete from public.rm_admins where id = $1', [id]).catch(() => {});
    await q('delete from auth.users where id = $1', [id]).catch(() => {});
  }
  await browser.close(); server.close(); await db.end();
}
