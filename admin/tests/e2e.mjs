#!/usr/bin/env node
// The dashboard end to end, in Chromium, against the dev mock (started here on a free port).
//   node admin/tests/e2e.mjs [screenshot folder]
// It fails on any console error, page error or Content-Security-Policy violation (each deliberate failure, like a wrong
// password, is allowed only inside its own step), and on any request to *.supabase.co (they're all blocked).
// It walks: sign-in (password, enrol, code), every page, the range picker, the price editor (set and clear), search,
// a password reset (made and typed), a sign-out, a delete, every refusal, the audit log, a 403 mid-session, a stale
// code, network and server errors, the token refresh, the idle sign-out, Sign out, a non-admin, the empty launch,
// and screenshots of every page at 1440x900 and 390x844, light and dark.

import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { start, reset } from '../dev/mock.mjs';

const SHOTS = process.argv[2] || join(tmpdir(), 'rollmodel-admin-shots');
mkdirSync(SHOTS, { recursive: true });
const PAGES = ['overview', 'players', 'modes', 'economy', 'ads', 'purchases', 'insights', 'support', 'audit'];
const VARIANTS = [
  { name: 'desktop-light', width: 1440, height: 900, scheme: 'light' },
  { name: 'desktop-dark', width: 1440, height: 900, scheme: 'dark' },
  { name: 'phone-light', width: 390, height: 844, scheme: 'light' },
  { name: 'phone-dark', width: 390, height: 844, scheme: 'dark' },
];

function playwright() {
  const require = createRequire(import.meta.url);
  for (const p of ['playwright', '/opt/node-tools/node_modules/playwright', 'playwright-core']) {
    try { return require(p); } catch { /* next */ }
  }
  throw new Error('Playwright not found (it is preinstalled; never run "playwright install").');
}

const problems = [];   // console errors, page errors, CSP violations, Supabase requests
const consoleText = []; // everything logged, to check no token or password ever is
let allowed = [];      // console errors expected inside the current step
let passed = 0;

const server = await start({ port: 0, quiet: true });
const B = 'http://127.0.0.1:' + server.address().port;
const browser = await playwright().chromium.launch();
const control = (path, body) => fetch(B + '/__mock' + path, { method: body ? 'POST' : 'GET', body: body ? JSON.stringify(body) : undefined }).then((r) => r.json());

function check(cond, msg) { if (!cond) throw new Error(msg); }
async function step(name, fn) {
  const t = Date.now();
  await fn();
  passed++;
  console.log('ok  ' + name + ' (' + (Date.now() - t) + ' ms)');
}
// Run fn while console errors matching these patterns are expected (failed requests the step causes on purpose).
async function expecting(patterns, page, fn) {
  allowed = patterns;
  try { return await fn(); } finally { await page.waitForTimeout(150); allowed = []; }
}
const FAILED = (status) => new RegExp('Failed to load resource: the server responded with a status of ' + status);

async function open(v) {
  const ctx = await browser.newContext({ viewport: { width: v.width, height: v.height }, colorScheme: v.scheme, locale: 'en-GB', timezoneId: 'UTC' });
  await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: B });
  await ctx.route('**/*supabase.co/**', (route) => { problems.push('a request to Supabase: ' + route.request().url()); route.abort(); });
  const page = await ctx.newPage();
  await page.addInitScript(() => {
    document.addEventListener('securitypolicyviolation', (e) => console.error('CSP violation: ' + e.violatedDirective + ' ' + e.blockedURI));
  });
  page.on('console', (m) => {
    const text = m.text();
    consoleText.push(text);
    const bad = m.type() === 'error' || (m.type() === 'warning' && /security policy|permissions.policy|CSP/i.test(text));
    if (bad && !allowed.some((re) => re.test(text))) problems.push(`[${v.name}] console ${m.type()}: ${text}`);
  });
  page.on('pageerror', (e) => problems.push(`[${v.name}] page error: ${e.message}`));
  return { ctx, page, v };
}

// ---------------------------------------------------------------- helpers on a page

const settled = (page) => page.waitForFunction(() => {
  const b = document.querySelector('.pagebody');
  return b && b.childElementCount > 0 && !b.querySelector('.loading') && !b.hasAttribute('aria-busy');
}, null, { timeout: 15000 }).then(() => page.waitForTimeout(250));

async function go(page, id) {
  await page.evaluate((h) => { location.hash = h; }, '#' + id);
  await settled(page);
}

async function signIn(page, email, { code = '123456', expectEnrol } = {}) {
  await page.goto(B + '/');
  await page.waitForSelector('input[type=email]');
  await page.fill('input[type=email]', email);
  await page.fill('input[type=password]', email === 'player@example.com' ? 'player-pass-1' : 'correct-horse-9');
  await page.click('form button[type=submit]');
  await page.waitForSelector('.code-input, .banner, .shell', { timeout: 10000 });
  if (!(await page.$('.code-input'))) return;
  if (expectEnrol != null) check(!!(await page.$('img.qr')) === expectEnrol, 'enrol step shown: expected ' + expectEnrol);
  await page.fill('.code-input', code);
  await page.click('form button[type=submit]');
  await page.waitForSelector('.shell, .banner, .form-error:not([hidden])', { timeout: 10000 });
  if (await page.$('.shell')) await settled(page);
}

// Every page: nothing broken, nothing hidden from screen readers, no sideways page scroll, no em dashes.
async function audit(page, label) {
  const r = await page.evaluate(() => {
    const text = document.body.innerText;
    const unlabeled = [...document.querySelectorAll('input, select, textarea')]
      .filter((el) => el.type !== 'hidden' && !el.labels?.length && !el.getAttribute('aria-label') && !el.getAttribute('aria-labelledby'))
      .map((el) => el.outerHTML.slice(0, 80));
    const nameless = [...document.querySelectorAll('button, a[href]')]
      .filter((el) => !el.textContent.trim() && !el.getAttribute('aria-label')).map((el) => el.outerHTML.slice(0, 80));
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      emDash: text.includes('\u2014'),
      junk: (text.match(/\bundefined\b|\bNaN\b|\[object Object\]|Infinity/) || [])[0] || null,
      failure: !!document.querySelector('.failure'),
      unlabeled, nameless,
    };
  });
  check(r.overflow <= 0, label + ': the page scrolls sideways by ' + r.overflow + 'px');
  check(!r.emDash, label + ': an em dash in the text');
  check(!r.junk, label + ': "' + r.junk + '" in the text');
  check(!r.failure, label + ': an error state');
  check(!r.unlabeled.length, label + ': inputs without a label: ' + r.unlabeled.join(' | '));
  check(!r.nameless.length, label + ': buttons or links without a name: ' + r.nameless.join(' | '));
}

const shot = (page, name) => page.screenshot({ path: join(SHOTS, name + '.png'), fullPage: true });
const text = (page, sel) => page.$eval(sel, (el) => el.textContent.replace(/\s+/g, ' ').trim());
const visible = (page, sel) => page.$(sel).then((el) => el && el.isVisible());

// ---------------------------------------------------------------- the flows

async function flows() {
  reset({ dataset: 'full' });
  const { ctx, page } = await open(VARIANTS[0]);

  await step('sign-in: a wrong password is refused in plain words', async () => {
    await page.goto(B + '/');
    await page.waitForSelector('input[type=email]');
    await audit(page, 'sign-in');
    await page.fill('input[type=email]', 'admin@example.com');
    await page.fill('input[type=password]', 'not-it');
    await expecting([FAILED(400)], page, async () => {
      await page.click('form button[type=submit]');
      await page.waitForSelector('.form-error:not([hidden])');
    });
    check((await text(page, '.form-error')) === 'Wrong email or password.', 'wrong password message');
  });

  await step('sign-in: password, then setting up the authenticator (QR code and key), a wrong code, the right code', async () => {
    await page.fill('input[type=password]', 'correct-horse-9');
    await page.click('form button[type=submit]');
    await page.waitForSelector('img.qr');
    const src = await page.$eval('img.qr', (img) => img.getAttribute('src'));
    check(src.startsWith('data:image/svg+xml'), 'the QR code is a data URI image');
    check(await page.$eval('img.qr', (img) => img.naturalWidth > 0), 'the QR code image loads under the CSP');
    check(/^[A-Z2-7 ]{16,}$/.test(await text(page, 'code.secret')), 'the key is shown as text');
    await audit(page, 'enrol');
    await page.click('button:has-text("Copy key")');
    await page.fill('.code-input', '12345');
    await page.click('form button[type=submit]');
    check((await text(page, '.form-error')) === 'Enter the 6 digits your app shows.', 'short code message');
    await page.fill('.code-input', '000000');
    await expecting([FAILED(422)], page, async () => {
      await page.click('form button[type=submit]');
      await page.waitForFunction(() => /didn't work/.test(document.querySelector('.form-error')?.textContent || ''));
    });
    await page.fill('.code-input', '123 456');
    await page.click('form button[type=submit]');
    await page.waitForSelector('.shell');
    await settled(page);
    check((await text(page, '.pagehead-title')) === 'Overview', 'lands on the Overview');
  });

  await step('the session: in sessionStorage only, its end shown, no secrets in the console', async () => {
    const st = await page.evaluate(() => ({ local: localStorage.length, s: JSON.parse(sessionStorage.getItem('rm_admin_session') || 'null') }));
    check(st.local === 0, 'nothing in localStorage');
    check(st.s && st.s.access_token && st.s.refresh_token, 'the session is in sessionStorage');
    const ends = await text(page, '.session-ends');
    check(/^Session ends (at|tomorrow at) \d\d:\d\d$/.test(ends), 'session end shown: ' + ends);
    const expect = new Date(Date.now() + 12 * 3600000).toISOString().slice(11, 16);
    check(ends.endsWith(expect) || ends.endsWith(new Date(Date.now() + 12 * 3600000 - 60000).toISOString().slice(11, 16)), 'ends 12 hours after the code: ' + ends + ' vs ' + expect);
    check(!consoleText.some((t) => t.includes(st.s.access_token) || t.includes(st.s.refresh_token) || t.includes('correct-horse-9')), 'no token or password logged');
  });

  await step('every page loads, nothing broken', async () => {
    for (const id of PAGES) {
      await page.click(`.nav-link[data-page="${id}"]`);
      await settled(page);
      check(await page.$eval('.nav-link[aria-current="page"]', (a) => a.dataset.page) === id, id + ' is the current page');
      await audit(page, id);
    }
  });

  await step('keyboard: skip link, focus on the page heading, charts read with the arrow keys', async () => {
    await go(page, 'players');
    check(await page.evaluate(() => document.activeElement.classList.contains('pagehead-title')), 'focus moves to the new page\'s heading');
    await page.goto(B + '/?fresh=1#overview'); // a real reload (a hash alone wouldn't reload): focus starts at the top
    await page.waitForSelector('.shell');
    await settled(page);
    await page.keyboard.press('Tab');
    check(await page.evaluate(() => document.activeElement.classList.contains('skip')), 'the first Tab reaches Skip to content');
    check(await visible(page, '.skip'), 'the skip link shows when focused');
    await page.keyboard.press('Enter');
    check(await page.evaluate(() => document.activeElement.id === 'main'), 'skip moves focus to the content');
    await page.focus('.plot');
    await page.keyboard.press('ArrowLeft');
    check(await visible(page, '.plot .tip'), 'a tooltip on keyboard focus');
    check(/\d/.test(await text(page, '.plot .tip')), 'the tooltip has numbers');
    await page.keyboard.press('Escape');
    const outline = await page.$eval('.plot', (el) => getComputedStyle(el).outlineStyle);
    check(outline !== 'none', 'a visible focus outline');
  });

  await step('range picker: 7 days, and the table view of a chart', async () => {
    await page.click('.seg-btn:has-text("7d")');
    await settled(page);
    check(await page.$eval('.seg-btn[aria-pressed="true"]', (b) => b.textContent) === '7d', '7d is pressed');
    const toggle = await page.$('.chart-card .card-actions button');
    await toggle.click();
    check(await toggle.getAttribute('aria-pressed') === 'true', 'the toggle is pressed');
    check(!(await visible(page, '.chart-card .plot')), 'the chart is hidden while its table shows');
    const rows = await page.$$eval('.chart-card .tablewrap >> nth=0', (els) => els[0].querySelectorAll('tbody tr').length);
    check(rows === 7, 'the table has 7 days, not ' + rows);
    await toggle.click();
    check(await visible(page, '.chart-card .plot'), 'back to the chart');
    await page.click('.seg-btn:has-text("30d")');
    await settled(page);
  });

  await step('price editor: set a price (old, new and default shown), then go back to the default', async () => {
    await go(page, 'economy');
    await page.click('button[aria-label="Edit the price of Top hat"]');
    await page.waitForSelector('dialog .price-input');
    await audit(page, 'price dialog');
    await page.fill('dialog .price-input', '4x');
    await page.click('dialog button:has-text("Review")');
    check((await text(page, 'dialog .form-error')) === 'Enter a whole number of dabs.', 'bad number refused');
    await page.fill('dialog .price-input', '425');
    await page.click('dialog button:has-text("Review")');
    await page.waitForSelector('dialog .compare');
    const cmp = await text(page, 'dialog .compare');
    check(/Now\s*450/.test(cmp) && /New\s*425/.test(cmp) && /Default\s*580/.test(cmp), 'old, new and default: ' + cmp);
    await shot(page, 'desktop-light-dialog-price');
    await page.click('dialog button:has-text("Set price")');
    await page.waitForSelector('.toast:has-text("now costs 425 dabs")');
    check(/within about a minute/.test(await text(page, '.toast')), 'says players get it within a minute');
    await settled(page);
    const row = await page.$eval('.items-table tr:has-text("Top hat")', (tr) => tr.textContent);
    check(/425/.test(row) && /Live/.test(row), 'the table shows the live price: ' + row);
    check((await control('/state')).prices.tophat.price === 425, 'the server has it');
    await page.click('button[aria-label="Use the default price of Top hat"]');
    await page.waitForSelector('dialog .compare');
    await page.click('dialog button:has-text("Use the default")');
    await page.waitForSelector('.toast:has-text("back to its default price, 580 dabs")');
    await settled(page);
    check(/580/.test(await page.$eval('.items-table tr:has-text("Top hat")', (tr) => tr.textContent)), 'back to 580');
    check(!(await control('/state')).prices.tophat, 'cleared on the server');
    check(await page.$eval('.items-table tr:has-text("Zombie eyes")', (tr) => /can't be priced/i.test(tr.textContent)), 'gifts can\'t be priced');
  });

  await step('insights: grouped and ranked, and a suggested price opens the editor filled in', async () => {
    await go(page, 'insights');
    const groups = await page.$$eval('.sugg-group .card-title', (els) => els.map((e) => e.textContent));
    check(groups.length >= 5, 'groups: ' + groups.join(', '));
    const sev = await page.$$eval('.sugg-group:first-of-type .sev', (els) => els.map((e) => e.textContent));
    check(sev[0] === 'High', 'the first group leads with a high one');
    const btn = await page.$('button:has-text("Set price to")');
    check(btn, 'a price suggestion');
    const want = (await btn.textContent()).match(/\d[\d,]*/)[0].replace(/,/g, '');
    await btn.click();
    await page.waitForSelector('dialog .price-input');
    check(await page.$eval('dialog .price-input', (i) => i.value) === want, 'the editor starts at the suggested price');
    await page.click('dialog button:has-text("Cancel")');
    await page.waitForSelector('dialog', { state: 'detached' });
    await page.click('.how summary');
    check(await visible(page, '.how .rules'), 'how suggestions work');
  });

  await step('support: search by name and code, open a player, and their account details', async () => {
    await go(page, 'support');
    await page.fill('input[type=search]', 'D');
    await page.click('form button[type=submit]');
    check((await text(page, '.form-error')) === 'Type at least 2 characters.', 'too short');
    await page.fill('input[type=search]', 'abcd 2345');
    await page.click('form button[type=submit]');
    await settled(page);
    check(await page.$eval('.pagebody .tbl tbody', (b) => b.querySelectorAll('tr').length) === 1, 'one player for the friend code');
    await page.fill('input[type=search]', 'Dus');
    await page.click('form button[type=submit]');
    await settled(page);
    await audit(page, 'search results');
    await page.click('.pagebody .tbl a >> text="Dusk"');
    await settled(page);
    check((await text(page, '.player-name')) === 'Dusk', 'Dusk opens');
    const det = await text(page, '.facts');
    check(/Dana/.test(det) && /Lee/.test(det) && /2001/.test(det), 'account details');
    check(/check it's really them/.test(await text(page, '.check')), 'the identity-check note');
    await audit(page, 'player');
  });

  await step('reset password: a strong one made here, shown once with Copy', async () => {
    await page.click('button:has-text("Reset password")');
    await page.waitForSelector('dialog');
    check(!(await visible(page, 'dialog input.mono')), 'no password field until "Type one" is picked');
    await page.click('dialog button:has-text("Next")');
    await page.click('dialog button:has-text("Set password")');
    await page.waitForSelector('dialog .password-out');
    const pw = await page.$eval('dialog .password-out', (i) => i.value);
    check(/^[A-HJ-NP-Za-hjkmnp-z2-9]{14}$/.test(pw) && /[A-Za-z]/.test(pw) && /\d/.test(pw), 'a strong password: ' + pw);
    const note = await text(page, 'dialog .dlg-body');
    check(/signed out everywhere/.test(note) && /username/.test(note) && /only this once/.test(note), 'the note: ' + note);
    await shot(page, 'desktop-light-dialog-password');
    await page.click('dialog button:has-text("Copy")');
    await page.waitForSelector('dialog button:has-text("Copied")'); // the page itself may not read the clipboard back
    await page.click('dialog button:has-text("Done")');
    await settled(page);
    check(/Reset a password/.test(await text(page, '.pagebody')), 'the audit trail shows it');
    check(!consoleText.some((t) => t.includes(pw)), 'the password is never logged');
  });

  await step('reset password: a typed one, checked against the rules first', async () => {
    await page.click('button:has-text("Reset password")');
    await page.click('dialog label:has-text("Type one")');
    await page.fill('dialog input.mono', 'short');
    await page.click('dialog button:has-text("Next")');
    check((await text(page, 'dialog .form-error')) === 'Use at least 8 characters.', 'too short');
    await page.fill('dialog input.mono', 'Dusk2026now');
    await page.click('dialog button:has-text("Next")');
    await page.click('dialog button:has-text("Set password")');
    await page.waitForSelector('dialog .password-out');
    check(await page.$eval('dialog .password-out', (i) => i.value) === 'Dusk2026now', 'shows the typed password');
    await page.click('dialog button:has-text("Done")');
    await settled(page);
  });

  await step('reset link: the email and Confirmed, Send reset link, sent or not; search by email', async () => {
    const det = await text(page, '.facts');
    check(/dusk@example\.com/.test(det) && /Confirmed/.test(det), 'the email and Confirmed: ' + det);
    await page.click('.player-actions button:has-text("Send reset link")');
    await page.waitForSelector('dialog');
    check(/dusk@example\.com/.test(await text(page, 'dialog')), 'the dialog names the address');
    await shot(page, 'desktop-light-dialog-link');
    await page.click('dialog button:has-text("Send link")');
    await page.waitForSelector('dialog .ok-line');
    check(/Sent to dusk@example\.com/.test(await text(page, 'dialog .ok-line')), 'sent');
    await page.click('dialog button:has-text("Done")');
    await settled(page);
    check(/Emailed a reset link/.test(await text(page, '.pagebody')), 'the audit trail shows it');
    await control('/config', { mailOff: true });
    await page.click('.player-actions button:has-text("Send reset link")');
    await page.click('dialog button:has-text("Send link")');
    await page.waitForSelector('dialog .danger-line');
    check(/Nothing was sent/.test(await text(page, 'dialog .danger-line')), 'email switched off: says nothing was sent');
    await page.click('dialog button:has-text("Done")');
    await settled(page);
    await control('/config', { mailOff: false });
    await go(page, 'support');
    await page.fill('input[type=search]', 'DUSK@Example.com');
    await page.click('form button[type=submit]');
    await settled(page);
    check(await page.$eval('.pagebody .tbl tbody', (b) => b.querySelectorAll('tr').length) === 1, 'one player for the email, any case');
    await page.fill('input[type=search]', 'nobody@example.com');
    await page.click('form button[type=submit]');
    await settled(page);
    check(/match exactly/.test(await text(page, '.pagebody')), 'no match says emails match exactly');
    await go(page, 'support?q=Dusk');
    await page.click('.pagebody .tbl a >> text="Dusk"');
    await settled(page);
    check((await text(page, '.player-name')) === 'Dusk', 'back on Dusk');
  });

  await step('sign out everywhere: confirm, then how many sessions ended; and the hourly limit', async () => {
    await page.click('.player-actions button:has-text("Sign out everywhere")');
    await page.click('dialog button:has-text("Sign out everywhere")');
    await page.waitForSelector('dialog .ok-line');
    check(/Ended \d+ sessions?\.|no sessions to end/.test(await text(page, 'dialog .ok-line')), 'sessions ended');
    await page.click('dialog button:has-text("Done")');
    await settled(page);
    await control('/config', { limits: { signout: 0 } });
    await page.click('.player-actions button:has-text("Sign out everywhere")');
    await page.click('dialog button:has-text("Sign out everywhere")');
    await page.waitForSelector('dialog .form-error:not([hidden])');
    check((await text(page, 'dialog .form-error')) === "That's the most you can do in an hour. Try again later.", 'slow_down in plain words');
    await page.click('dialog button:has-text("Cancel")');
    await control('/config', { limits: { signout: 60 } });
  });

  await step('delete account: typed confirmation, disabled until it matches, then back to search', async () => {
    await page.click('button:has-text("Delete account")');
    await page.waitForSelector('dialog.danger');
    const del = 'dialog button:has-text("Delete account")';
    check(await page.$eval(del, (b) => b.disabled), 'disabled at first');
    check(/can't be undone/.test(await text(page, 'dialog')), 'says it can\'t be undone');
    await page.fill('dialog input', 'Dawn');
    check(await page.$eval(del, (b) => b.disabled), 'still disabled for the wrong name');
    await page.fill('dialog input', 'dUsK');
    check(!(await page.$eval(del, (b) => b.disabled)), 'enabled when it matches, any case');
    await page.waitForTimeout(250); // let the button's colour settle
    await shot(page, 'desktop-light-dialog-delete');
    await page.click(del);
    await page.waitForSelector('.toast:has-text("Deleted Dusk")');
    await settled(page);
    check(await page.evaluate(() => location.hash) === '#support', 'back to search');
    await page.fill('input[type=search]', 'Dusk');
    await page.click('form button[type=submit]');
    await settled(page);
    check(!(await page.$('.pagebody .tbl a >> text="Dusk"')), 'Dusk is gone');
  });

  await step('players that can\'t be changed: an admin, and one without an account', async () => {
    await page.fill('input[type=search]', 'RollModelHQ');
    await page.click('form button[type=submit]');
    await settled(page);
    await page.click('.pagebody .tbl a >> text="RollModelHQ"');
    await settled(page);
    check(await page.$$eval('.player-actions button', (bs) => bs.every((b) => b.disabled)), 'every action is off for an admin');
    check(/admin account/.test(await text(page, '.player-head .hint')), 'and says why');
    await go(page, 'support?q=Bramble');
    await page.click('.pagebody .tbl a >> text="Bramble"');
    await settled(page);
    check(await page.$eval('.player-actions button:has-text("Reset password")', (b) => b.disabled), 'no password to reset');
    check(/without an account/.test(await text(page, '.player-head .hint')), 'and says why');
    await go(page, 'support?q=QRST6789');
    await page.click('.pagebody .tbl a');
    await settled(page);
    check((await text(page, '.player-name')) === 'No username', 'a player with no username');
    await page.click('button:has-text("Delete account")');
    check(/user id/.test(await text(page, 'dialog label')), 'confirmed with their user id');
    await page.click('dialog button:has-text("Cancel")');
  });

  await step('before the email SQL is run: no email row or reset link, and email search says so', async () => {
    await control('/config', { nomail: true });
    await expecting([FAILED(404)], page, async () => {
      await go(page, 'support?q=Duskfall');
      await page.click('.pagebody .tbl a >> text="Duskfall"');
      await settled(page);
      check((await text(page, '.player-name')) === 'Duskfall', 'the player still opens');
      check(!(await page.$('.player-actions button:has-text("Send reset link")')), 'no reset link button');
      check(!/Email/.test(await text(page, '.facts')), 'no email row');
      check(!(await page.$eval('.player-actions button:has-text("Reset password")', (b) => b.disabled)), 'Reset password still works');
      await go(page, 'support?q=' + encodeURIComponent('someone@example.com'));
      check(/isn't set up yet/.test(await text(page, '.pagebody')), 'email search says it isn\'t set up');
    });
    await control('/config', { nomail: false });
  });

  await step('audit log: every change in plain words, newest first', async () => {
    await go(page, 'audit');
    const t = await text(page, '.pagebody');
    for (const w of ['Changed a price', 'Reset a password', 'Emailed a reset link', 'Signed a player out everywhere', 'Deleted an account', 'Top hat: 450 → 425', 'Top hat: 425 → the default (580)']) {
      check(t.includes(w), 'audit log has "' + w + '"');
    }
    const first = await text(page, '.pagebody .tbl tbody tr:first-child');
    check(first.includes('Deleted an account') && /A player \([0-9a-f-]{36}\)/.test(first), 'newest first, and the deleted player by id: ' + first);
    check(!/\bDusk\b/.test(t), 'a deleted player\'s name is gone from the log');
    await page.selectOption('.toolbar select >> nth=0', 'set_price');
    check(await page.$$eval('.pagebody .tbl tbody tr', (rs) => rs.every((r) => r.textContent.includes('Changed a price'))), 'the filter works');
  });

  await step('a network error shows a retry, and the retry works', async () => {
    await page.route('**/rest/v1/rpc/adm_ads', (r) => r.abort());
    await expecting([/net::ERR_FAILED/, /Failed to load resource/], page, async () => {
      await go(page, 'ads');
      check(/Can't reach the server/.test(await text(page, '.failure')), 'network failure message');
    });
    await page.unroute('**/rest/v1/rpc/adm_ads');
    await page.click('.failure button:has-text("Try again")');
    await settled(page);
    check(await page.$('.pagebody .tbl'), 'loaded after the retry');
  });

  await step('a server error shows what happened and a retry', async () => {
    await control('/config', { fail: { fn: 'adm_modes', status: 500, count: 1 } });
    await expecting([FAILED(500)], page, async () => {
      await go(page, 'modes');
      check(/The server had a problem \(500/.test(await text(page, '.failure')), 'server failure message');
    });
    await page.click('.failure button:has-text("Try again")');
    await settled(page);
    check(!(await page.$('.failure')), 'loaded after the retry');
  });

  await step('a 403 mid-session (removed from the admins) signs out with the reason', async () => {
    await control('/config', { unlist: 'admin@example.com' });
    await expecting([FAILED(403)], page, async () => {
      await page.click('.reload .btn');
      await page.waitForSelector('.signin .banner');
    });
    check((await text(page, '.signin .banner')) === "This account isn't an admin.", 'not an admin');
    check(await page.evaluate(() => sessionStorage.getItem('rm_admin_session')) === null, 'session forgotten');
    await control('/config', { relist: 'admin@example.com' });
  });

  await step('a code over 12 hours old: signed out with "sign in again"', async () => {
    await signIn(page, 'admin@example.com', { expectEnrol: false });
    check(await page.$('.shell'), 'signed in again, with the code only');
    await control('/config', { codeAge: { email: 'admin@example.com', hours: 13 } });
    await expecting([FAILED(403)], page, async () => {
      await page.click('.reload .btn');
      await page.waitForSelector('.signin .banner');
    });
    check((await text(page, '.signin .banner')) === 'Your sign-in is over 12 hours old. Sign in again.', 'stale');
  });

  await step('a session ended on the server sends you back to sign in, mid-session and on load', async () => {
    await signIn(page, 'admin@example.com');
    await control('/config', { revoke: 'admin@example.com' });
    await expecting([FAILED(403), FAILED(401), FAILED(400)], page, async () => {
      await page.click('.reload .btn');
      await page.waitForSelector('.signin .banner');
    });
    check((await text(page, '.signin .banner')) === 'Your session ended. Sign in again.', 'mid-session');
    await signIn(page, 'admin@example.com');
    await control('/config', { revoke: 'admin@example.com' });
    await expecting([FAILED(403), FAILED(401), FAILED(400)], page, async () => {
      await page.reload();
      await page.waitForSelector('.signin .banner');
    });
    check((await text(page, '.signin .banner')) === 'Your session ended. Sign in again.', 'on load');
    check(!(await page.$('.shell')), 'nothing of the dashboard');
  });

  await step('the token is refreshed a minute before it expires', async () => {
    await control('/config', { tokenSecs: 63 });
    await signIn(page, 'admin@example.com');
    const before = (await control('/state')).counts.refreshes;
    await page.waitForTimeout(5500);
    const after = (await control('/state')).counts.refreshes;
    check(after > before, 'refreshed (' + before + ' -> ' + after + ')');
    await go(page, 'ads');
    check(await page.$('.pagebody .tbl'), 'still working on the new token');
    await control('/config', { tokenSecs: 3600 });
  });

  await step('idle: a warning a minute before (dismissed by moving), then signed out', async () => {
    await page.goto(B + '/?idle_ms=6000&warn_ms=3000#overview'); // the mock's test hook; same tab, same session
    await page.waitForSelector('.shell');
    await page.waitForSelector('.idle-warning', { timeout: 8000 });
    check(/signed out in/.test(await text(page, '.idle-warning')), 'warning text');
    await shot(page, 'desktop-light-idle-warning');
    await page.mouse.move(400, 400);
    await page.mouse.move(420, 420);
    await page.waitForSelector('.idle-warning', { state: 'detached', timeout: 3000 });
    await page.waitForSelector('.signin .banner', { timeout: 12000 });
    check(/15 minutes without input/.test(await text(page, '.signin .banner')), 'idle sign-out message');
  });

  await step('Sign out: the session is ended on the server and forgotten here', async () => {
    await signIn(page, 'admin@example.com');
    const before = (await control('/state')).counts.logouts;
    await page.click('.session .btn:has-text("Sign out")');
    await page.waitForSelector('.signin .banner');
    check((await text(page, '.signin .banner')) === "You're signed out.", 'signed out message');
    check(await page.evaluate(() => sessionStorage.length) === 0, 'nothing left in sessionStorage');
    check((await control('/state')).counts.logouts === before + 1, 'logout sent');
  });

  await step('a database not set up for admin sign-in says so, at sign-in and mid-session', async () => {
    const SETUP = "The database isn't set up for admin sign-in yet. See admin/README.md.";
    await control('/config', { setup: true });
    await signIn(page, 'owner@example.com');
    check((await text(page, '.signin .banner')) === SETUP, 'at sign-in');
    await control('/config', { setup: false });
    await signIn(page, 'owner@example.com');
    check(await page.$('.shell'), 'signed in');
    await control('/config', { setup: true });
    await expecting([FAILED(403)], page, async () => {
      await page.click('.reload .btn');
      await page.waitForSelector('.signin .banner');
    });
    check((await text(page, '.signin .banner')) === SETUP, 'mid-session');
    await control('/config', { setup: false });
  });

  await step('a non-admin is refused before any authenticator is set up', async () => {
    const enrolls = (await control('/state')).counts.enrolls;
    await signIn(page, 'player@example.com');
    check((await text(page, '.signin .banner')) === "This account isn't an admin.", 'refused');
    check(!(await page.$('.shell')), 'nothing of the dashboard');
    check((await control('/state')).counts.enrolls === enrolls, 'no authenticator was enrolled');
  });

  await step('an admin with an authenticator is asked for the code only; a stale one is refused', async () => {
    await signIn(page, 'owner@example.com', { expectEnrol: false });
    check(await page.$('.shell'), 'owner signed in');
    await page.click('.session .btn:has-text("Sign out")');
    await page.waitForSelector('.signin');
    await signIn(page, 'stale@example.com', { expectEnrol: false });
    check((await text(page, '.signin .banner')) === 'Your sign-in is over 12 hours old. Sign in again.', 'stale refused');
  });

  await ctx.close();
}

// ---------------------------------------------------------------- screenshots

async function screenshots(dataset) {
  for (const v of VARIANTS) {
    reset({ dataset, iap: false });
    const { ctx, page } = await open(v);
    await step(`${dataset}: every page, ${v.name}`, async () => {
      const tag = v.name + (dataset === 'empty' ? '-empty' : '');
      if (dataset === 'full') {
        await page.goto(B + '/');
        await page.waitForSelector('input[type=email]');
        await shot(page, tag + '-signin');
        await page.fill('input[type=email]', 'admin@example.com');
        await page.fill('input[type=password]', 'correct-horse-9');
        await page.click('form button[type=submit]');
        await page.waitForSelector('img.qr');
        await shot(page, tag + '-signin-enrol');
        await page.fill('.code-input', '123456');
        await page.click('form button[type=submit]');
        await page.waitForSelector('.shell');
        await settled(page);
      } else {
        await signIn(page, 'admin@example.com');
      }
      if (v.width < 600) {
        // the phone menu
        await page.click('.menu-btn');
        await page.waitForSelector('.menu-open .side .nav-link', { state: 'visible' });
        await page.waitForTimeout(350); // the drawer slides in
        if (dataset === 'full') await page.screenshot({ path: join(SHOTS, tag + '-menu.png') });
        await page.click('.side .nav-link[data-page="players"]');
        await settled(page);
        check(!(await page.$('.menu-open')), 'the menu closes');
        check((await text(page, '.pagehead-title')) === 'Players', 'the menu navigates');
      }
      for (const id of PAGES) {
        await go(page, id);
        await audit(page, tag + ' ' + id);
        await shot(page, tag + '-' + id);
      }
      if (dataset === 'full') {
        await go(page, 'support?q=Dusk');
        await page.click('.pagebody .tbl a >> text="Dusk"');
        await settled(page);
        await audit(page, tag + ' player');
        await shot(page, tag + '-support-player');
        await page.click('button:has-text("Reset password")');
        await page.waitForSelector('dialog');
        await shot(page, tag + '-dialog-reset');
        await page.keyboard.press('Escape');
        await go(page, 'economy');
        await page.click('button[aria-label="Edit the price of Hero cape"]');
        await page.waitForSelector('dialog .price-input');
        await page.screenshot({ path: join(SHOTS, tag + '-dialog-price.png') });
        await page.keyboard.press('Escape');
      } else {
        await go(page, 'support?q=Dusk');
        await audit(page, tag + ' search');
        await shot(page, tag + '-support-search');
      }
    });
    await ctx.close();
  }
}

async function purchasesFilled() {
  reset({ dataset: 'full', iap: true });
  for (const v of [VARIANTS[0], VARIANTS[3]]) {
    const { ctx, page } = await open(v);
    await step('purchases with data (MOCK_IAP), ' + v.name, async () => {
      await signIn(page, 'owner@example.com');
      await go(page, 'purchases');
      await audit(page, 'purchases');
      check(await page.$('.pagebody .tbl'), 'the products table');
      check((await page.$$('.pagebody .chart-card')).length === 2, 'two charts');
      await shot(page, v.name + '-purchases-with-data');
    });
    await ctx.close();
  }
}

// ---------------------------------------------------------------- run

let failed = null;
try {
  await flows();
  await screenshots('full');
  await screenshots('empty');
  await purchasesFilled();
} catch (e) {
  failed = e;
}
await browser.close();
server.close();

if (problems.length) console.log('\nProblems:\n  ' + problems.join('\n  '));
if (failed) console.log('\nFAILED: ' + failed.message.split('\n')[0]);
console.log(`\n${passed} steps passed. Screenshots: ${SHOTS}`);
process.exit(failed || problems.length ? 1 : 0);
