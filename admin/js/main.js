// The dashboard: sign-in, then the shell (pages, session, sign out) and a hash router (#overview, #support/<id>...).

import { h, mount, icon, brand, button, toast, loading, failure, rangePicker, RANGES } from './ui.js';
import * as auth from './auth.js';
import { rpc, setDeniedHandler } from './api.js';
import { loadCatalog } from './catalog.js';
import { watchIdle } from './idle.js';
import { clock, dateTime } from './format.js';
import { DEV } from './config.js';
import { showSignIn, decide, staleText, NOT_ADMIN, STALE, SETUP } from './pages/signin.js';
import overview from './pages/overview.js';
import players from './pages/players.js';
import modes from './pages/modes.js';
import economy from './pages/economy.js';
import ads from './pages/ads.js';
import purchases from './pages/purchases.js';
import insights from './pages/insights.js';
import support from './pages/support.js';
import audit from './pages/audit.js';

const PAGES = [overview, players, modes, economy, ads, purchases, insights, support, audit];
const IDLE_MS = (DEV && DEV.idleMs) || 15 * 60 * 1000;
const WARN_MS = Math.min((DEV && DEV.warnMs) || 60 * 1000, IDLE_MS);
const SESSION_MS = 12 * 3600 * 1000;
const DAYS_KEY = 'rm_admin_days';

const app = document.getElementById('app');
let me = null;        // the adm_whoami answer while signed in
let idle = null;
let staleTimer = 0;
let navSeq = 0;
let ui = null;        // the shell's parts
let leaving = false;
let days = readDays();

function readDays() {
  try { const d = Number(sessionStorage.getItem(DAYS_KEY)); return RANGES.includes(d) ? d : 30; } catch { return 30; }
}
function setDays(d) {
  days = d;
  try { sessionStorage.setItem(DAYS_KEY, String(d)); } catch { /* fine */ }
}

// ---------------------------------------------------------------- start

boot();

async function boot() {
  window.addEventListener('unhandledrejection', (e) => { console.error('Unhandled:', e.reason && e.reason.message); toast('Something went wrong. Try again.', 'error'); });
  window.addEventListener('error', (e) => {
    if (/ResizeObserver loop/.test(e.message || '')) return; // a harmless browser notice, not an error
    console.error('Error:', e.message);
    toast('Something went wrong. Reload the page.', 'error');
  });
  try {
    await loadCatalog();
  } catch (e) {
    mount(app, h('main', { class: 'signin', id: 'main' }, h('div', { class: 'signin-card' }, brand('Admin'), failure({ message: e.message }, () => location.reload()))));
    return;
  }
  auth.onLost((message) => signedOut(message));
  setDeniedHandler(denied);
  window.addEventListener('hashchange', route);
  const opts = { onAdmin: enter };
  if (auth.load()) decide(app, opts);
  else showSignIn(app, opts);
}

// ---------------------------------------------------------------- signed in

function enter(who) {
  me = who;
  leaving = false;
  buildShell();
  idle = watchIdle({
    idleMs: IDLE_MS, warnMs: WARN_MS,
    onWarn: showIdleWarning,
    onBack: hideIdleWarning,
    onIdle: () => signedOut('You were signed out after 15 minutes without input.', 'info'),
  });
  const ends = sessionEnds();
  clearTimeout(staleTimer);
  if (ends) staleTimer = setTimeout(() => signedOut(STALE), Math.max(0, Math.min(ends - Date.now(), 2147483647)));
  route();
}

function sessionEnds() {
  const t = me && me.code_at ? Date.parse(me.code_at) : NaN;
  return Number.isFinite(t) ? t + SESSION_MS : null;
}

function endsText() {
  const ends = sessionEnds();
  if (!ends) return 'in 12 hours';
  const d = new Date(ends), now = new Date();
  const iso = d.toISOString();
  if (d.toDateString() === now.toDateString()) return 'at ' + clock(iso);
  const tomorrow = new Date(now); tomorrow.setDate(now.getDate() + 1);
  if (d.toDateString() === tomorrow.toDateString()) return 'tomorrow at ' + clock(iso);
  return dateTime(iso);
}

function buildShell() {
  const links = PAGES.map((p) => h('a', { href: '#' + p.id, class: 'nav-link', dataset: { page: p.id } }, icon(p.icon || p.id), h('span', null, p.title)));
  const session = h('div', { class: 'session' },
    h('div', { class: 'session-who', title: me.email }, icon('user'), h('span', null, me.email || 'Signed in')),
    h('div', { class: 'session-ends', title: 'Twelve hours after you entered your code' }, 'Session ends ' + endsText()),
    button('Sign out', { kind: 'secondary small', ico: 'out', onclick: () => signedOut("You're signed out.", 'info') }));
  const side = h('aside', { class: 'side', id: 'side' },
    h('div', { class: 'side-brand' }, brand('Admin')),
    h('nav', { class: 'nav', 'aria-label': 'Pages' }, h('ul', null, links.map((a) => h('li', null, a)))),
    session);
  const menu = h('button', { type: 'button', class: 'icon-btn menu-btn', 'aria-expanded': 'false', 'aria-controls': 'side', 'aria-label': 'Menu' }, icon('menu'));
  menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
  const topbar = h('header', { class: 'topbar' }, brand('Admin'),
    h('div', { class: 'topbar-tools' },
      h('button', { type: 'button', class: 'btn secondary small', onclick: () => signedOut("You're signed out.", 'info') }, icon('out'), h('span', null, 'Sign out')),
      menu));
  const head = h('div', { class: 'pagehead' });
  const body = h('div', { class: 'pagebody' });
  const main = h('main', { id: 'main', class: 'main', tabindex: '-1' }, head, body);
  const skip = h('button', { type: 'button', class: 'skip', onclick: () => main.focus() }, 'Skip to content');
  const shell = h('div', { class: 'shell' }, skip, topbar, h('div', { class: 'side-col' }, side), h('div', { class: 'scrim', onclick: () => setMenu(false) }), main);
  shell.addEventListener('keydown', (e) => { if (e.key === 'Escape' && shell.classList.contains('menu-open')) { setMenu(false); menu.focus(); } });
  mount(app, shell);
  ui = { shell, side, menu, links, head, body, main };
}

function setMenu(open) {
  if (!ui) return;
  ui.shell.classList.toggle('menu-open', open);
  ui.menu.setAttribute('aria-expanded', String(open));
  if (open) { const cur = ui.links.find((a) => a.getAttribute('aria-current')) || ui.links[0]; cur.focus(); }
}

// ---------------------------------------------------------------- the router

// "#support/<id>" or "#support?q=dusk": the path is decoded on its own so a "?" inside a query can't split it.
function parse() {
  const raw = location.hash.replace(/^#/, '');
  const i = raw.indexOf('?');
  let path = i < 0 ? raw : raw.slice(0, i);
  try { path = decodeURIComponent(path); } catch { path = ''; }
  const [id, ...rest] = path.split('/');
  return { id: id || 'overview', arg: rest.join('/'), q: new URLSearchParams(i < 0 ? '' : raw.slice(i + 1)), raw };
}

// e is the hashchange event; the first page after signing in leaves focus at the top, so Tab reaches "Skip to content".
function route(e) {
  if (!me || !ui) return;
  const r = parse();
  const page = PAGES.find((p) => p.id === r.id) || PAGES[0];
  ui.links.forEach((a) => (a.dataset.page === page.id ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current')));
  const menuWasOpen = ui.shell.classList.contains('menu-open');
  setMenu(false);
  // later pages: focus moves to the new heading, for keyboards and screen readers
  render(page, r, { focus: e || menuWasOpen ? 'h1' : null });
}

async function render(page, r, { keep = false, focus = null } = {}) {
  const seq = ++navSeq;
  const ctx = {
    days, route: r, me,
    go: (hash) => { if (location.hash === hash) render(page, parse(), { keep: true }); else location.hash = hash; },
    reload: () => render(page, r, { keep: true }),
  };
  document.title = page.title + ' · Roll Model admin';
  const h1 = h('h1', { class: 'pagehead-title', tabindex: '-1' }, page.title);
  const stamp = h('span', { class: 'updated', 'aria-live': 'off' });
  mount(ui.head,
    h('div', { class: 'pagehead-titles' }, h1, page.sub ? h('p', { class: 'pagehead-sub' }, page.sub) : null),
    h('div', { class: 'pagehead-tools' },
      page.range ? rangePicker(days, (d) => { setDays(d); render(page, r, { keep: true, focus: 'range' }); }) : null,
      h('div', { class: 'reload' }, stamp,
        button('Reload', { kind: 'ghost small', ico: 'reload', onclick: () => render(page, r, { keep: true, focus: 'reload' }) }))));
  if (focus === 'h1') h1.focus({ preventScroll: false });
  else if (focus === 'range') { const b = ui.head.querySelector('.seg-btn[aria-pressed="true"]'); if (b) b.focus(); }
  else if (focus === 'reload') { const b = ui.head.querySelector('.reload .btn'); if (b) b.focus(); }

  const body = ui.body;
  const key = page.id + '/' + r.arg + '?' + r.q.toString();
  if (keep && body.dataset.key === key && body.childElementCount) {
    body.classList.add('is-loading'); // keep the frame while it reloads
    body.setAttribute('aria-busy', 'true');
  } else {
    body.dataset.key = key;
    mount(body, loading());
  }
  try {
    const data = await page.load(ctx);
    if (seq !== navSeq || !me) return;
    mount(body, page.view(data, ctx));
    stamp.textContent = 'Updated ' + clock(new Date().toISOString());
  } catch (e) {
    if (seq !== navSeq || !me) return;
    if (e && (e.kind === 'denied' || e.kind === 'auth')) return; // signing out
    if (!e || !e.kind) console.error('Page failed:', e && e.message);
    mount(body, failure(e, () => render(page, r, {})));
  } finally {
    if (seq === navSeq) { body.classList.remove('is-loading'); body.removeAttribute('aria-busy'); }
  }
}

// ---------------------------------------------------------------- leaving

// A 403 from any admin function: ask adm_whoami why, then sign out with that reason.
async function denied() {
  if (leaving || !me) return;
  leaving = true;
  let msg = "You're not allowed to do that any more. Sign in again.";
  try {
    const who = await rpc('adm_whoami');
    if (who && who.why === 'stale') msg = staleText(who);
    else if (who && who.why === 'not_listed') msg = NOT_ADMIN;
    else if (who && who.why === 'needs_code') msg = 'Your sign-in needs your authenticator code again. Sign in again.';
    else if (who && who.why === 'setup') msg = SETUP;
  } catch { /* keep the general message */ }
  signedOut(msg);
}

let signingOut = false;
async function signedOut(message, tone = 'error') {
  if (signingOut) return; // one reason is enough
  signingOut = true;
  leaving = true;
  navSeq++;
  if (idle) { idle.stop(); idle = null; }
  clearTimeout(staleTimer);
  hideIdleWarning();
  document.querySelectorAll('dialog').forEach((d) => d.close());
  me = null;
  ui = null;
  days = 30;
  try { sessionStorage.removeItem(DAYS_KEY); } catch { /* fine */ }
  try { await auth.signOut(); } finally { signingOut = false; }
  showSignIn(app, { onAdmin: enter, message, tone });
}

// ---------------------------------------------------------------- the idle warning

function showIdleWarning(msLeft) {
  hideIdleWarning();
  const secs = Math.max(1, Math.round(msLeft / 1000));
  const left = secs >= 55 ? 'a minute' : secs + ' seconds';
  document.body.append(h('div', { class: 'idle-warning', id: 'idle-warning', role: 'alert' },
    icon('lock'),
    h('div', null,
      h('p', { class: 'idle-title' }, 'Still there?'),
      h('p', null, "You'll be signed out in " + left + ' without input. Move the pointer or press a key to stay signed in.')),
    button('Stay signed in', { kind: 'primary small', onclick: hideIdleWarning })));
}

function hideIdleWarning() {
  const el = document.getElementById('idle-warning');
  if (el) el.remove();
}
