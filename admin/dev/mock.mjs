#!/usr/bin/env node
// Roll Model admin: a zero-dependency development server and Supabase stand-in. For development and tests only.
//
//   node admin/dev/mock.mjs              http://127.0.0.1:8791
//   MOCK=empty node admin/dev/mock.mjs   a brand-new launch: zeros and empty lists
//   MOCK_IAP=1                           made-up in-app purchases, to see the Purchases page filled in
//   PORT=8800  HOST=127.0.0.1  MOCK_DELAY=150 (ms per API answer)  MOCK_TOKEN_SECS=3600
//
// It serves admin/ with the production headers (the CSP with connect-src 'self'), serves js/config.js rewritten to
// point at itself, and answers GoTrue (/auth/v1/...) and PostgREST (/rest/v1/rpc/...) with the real shapes,
// including the errors. Accounts (the authenticator code is always 123456):
//   admin@example.com / correct-horse-9    an admin with no authenticator yet: sign-in sets one up
//   owner@example.com / correct-horse-9    an admin with an authenticator: sign-in asks for the code
//   stale@example.com / correct-horse-9    an admin whose code counts as over 12 hours old
//   player@example.com / player-pass-1     a player, not an admin
//   dusk@example.com / dusk-pass-123       another non-admin (the player Dusk's account)
// Test-only controls: GET /__mock/state, POST /__mock/reset {dataset, iap}, POST /__mock/config {...} (see control()).

import http from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join, normalize, sep, extname } from 'node:path';
import { randomBytes, randomUUID } from 'node:crypto';
import { makeWorld, overview, modes, progress, economy, ads, iapData, CATALOG, ADMIN_IDS, SEEDED_PRICES } from './world.mjs';

const ROOT = normalize(join(dirname(fileURLToPath(import.meta.url)), '..'));
const KEY = 'sb_publishable_mock_dev_only';
const CODE = '123456';
const HOUR = 3600000;

export const CSP = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; " +
  "connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'";
const SECURITY = {
  'Content-Security-Policy': CSP,
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer',
  'X-Frame-Options': 'DENY',
  'Permissions-Policy': 'accelerometer=(), autoplay=(), camera=(), clipboard-read=(), clipboard-write=(self), display-capture=(), ' +
    'encrypted-media=(), fullscreen=(), geolocation=(), gyroscope=(), hid=(), idle-detection=(), magnetometer=(), microphone=(), ' +
    'midi=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), screen-wake-lock=(), serial=(), usb=(), xr-spatial-tracking=()',
  'Cross-Origin-Opener-Policy': 'same-origin',
  'Cross-Origin-Resource-Policy': 'same-origin',
  'Cache-Control': 'no-store',
};
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml' };

// js/config.js as the mock serves it: Supabase is this same origin, and the idle timers can be shortened from the URL
// (?idle_ms=4000&warn_ms=2000). The real js/config.js never has these hooks.
const CONFIG = `// Served by dev/mock.mjs in place of js/config.js. Development only.
export const SUPABASE_URL = location.origin;
export const PUBLISHABLE_KEY = '${KEY}';
const q = new URLSearchParams(location.search);
const ms = (k) => { const v = Number(q.get(k)); return Number.isFinite(v) && v > 0 ? v : null; };
export const DEV = { idleMs: ms('idle_ms'), warnMs: ms('warn_ms') };
`;

const ACCOUNTS = [
  { email: 'admin@example.com', password: 'correct-horse-9', id: ADMIN_IDS['admin@example.com'], listed: true },
  { email: 'owner@example.com', password: 'correct-horse-9', id: ADMIN_IDS['owner@example.com'], listed: true, factor: true },
  { email: 'stale@example.com', password: 'correct-horse-9', id: 'a0000000-0000-4000-8000-00000000ad03', listed: true, factor: true, codeAgeHours: 13 },
  { email: 'player@example.com', password: 'player-pass-1', id: 'b0000000-0000-4000-8000-000000000b01', listed: false },
  { email: 'dusk@example.com', password: 'dusk-pass-123', id: 'b0000000-0000-4000-8000-000000000b02', listed: false },
];

const DEFAULT_LIMITS = { delete_player: 30, set_password: 60, signout: 60, set_price: 300 };

// The parameters of every function: PostgREST refuses a call whose names don't match (PGRST202).
const SIG = {
  adm_whoami: [], adm_overview: ['p_days'], adm_modes: ['p_days'], adm_progress: ['p_steps'], adm_economy: ['p_days'],
  adm_ads: ['p_days'], adm_iap: ['p_days'], adm_prices: [], adm_set_price: ['p_item', 'p_price'], adm_find: ['p_q'],
  adm_player: ['p_id'], adm_set_password: ['p_id', 'p_password'], adm_signout: ['p_id'], adm_delete_player: ['p_id', 'p_confirm'],
  adm_audit: ['p_limit'],
};
const REQUIRED = { adm_set_price: ['p_item', 'p_price'], adm_find: ['p_q'], adm_player: ['p_id'], adm_set_password: ['p_id', 'p_password'],
  adm_signout: ['p_id'], adm_delete_player: ['p_id', 'p_confirm'] };

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const iso = (t) => new Date(t).toISOString();
const nowSec = () => Math.floor(Date.now() / 1000);
const b64url = (o) => Buffer.from(JSON.stringify(o)).toString('base64url');

// ---------------------------------------------------------------- state

let S = null;

export function reset({ dataset = process.env.MOCK === 'empty' ? 'empty' : 'full', iap = process.env.MOCK_IAP === '1' } = {}) {
  const now = Date.now();
  const world = makeWorld({ empty: dataset === 'empty', iap, now });
  S = {
    dataset, iap, world,
    prices: new Map(), audit: [],
    sessions: new Map(), refresh: new Map(), factors: new Map(), challenges: new Map(),
    counts: { passwordGrants: 0, refreshes: 0, logouts: 0, verifies: 0, enrolls: 0, rpc: 0 },
    used: new Map(), limits: { ...DEFAULT_LIMITS }, unlisted: new Set(), fail: new Map(), codeAge: new Map(),
    tokenSecs: Number(process.env.MOCK_TOKEN_SECS) || 3600,
    delay: Number(process.env.MOCK_DELAY) || 0,
  };
  for (const a of ACCOUNTS) {
    S.factors.set(a.id, a.factor ? [{ id: randomUUID(), friendly_name: 'Roll Model admin', factor_type: 'totp', status: 'verified', created_at: iso(now - 40 * 86400000), updated_at: iso(now - 40 * 86400000) }] : []);
  }
  if (dataset !== 'empty') {
    // a little history: two live prices, and the changes that made them
    const ago = (h) => iso(now - h * HOUR);
    S.prices.set('cape', { price: SEEDED_PRICES.cape, updated_at: ago(75), updated_by: 'owner@example.com' });
    S.prices.set('tophat', { price: SEEDED_PRICES.tophat, updated_at: ago(49), updated_by: 'admin@example.com' });
    const dusk = world.players.find((p) => p.name === 'Dusk');
    const other = world.players.find((p) => p.name && p.name !== 'Dusk' && p.account);
    S.audit.push(
      { at: ago(20), admin: 'owner@example.com', action: 'signout', target: other.id, detail: { name: other.name, sessions: 2 } },
      { at: ago(26), admin: 'owner@example.com', action: 'set_password', target: other.id, detail: { name: other.name } },
      { at: ago(49), admin: 'admin@example.com', action: 'set_price', target: 'tophat', detail: { from: null, to: SEEDED_PRICES.tophat } },
      { at: ago(75), admin: 'owner@example.com', action: 'set_price', target: 'cape', detail: { from: null, to: SEEDED_PRICES.cape } },
      { at: ago(122), admin: 'owner@example.com', action: 'delete_player', target: 'c3e1a7d2-5b4f-4e8a-9c61-2f7b8d9e0a13', detail: { name: 'Splotch_9', id: 'c3e1a7d2-5b4f-4e8a-9c61-2f7b8d9e0a13' } },
      { at: ago(150), admin: 'owner@example.com', action: 'set_password', target: dusk.id, detail: { name: 'Dusk' } },
    );
  }
  return S;
}

// ---------------------------------------------------------------- answers

// plain text (or nothing, for a 204)
function send(res, status, text, headers = {}) {
  res.writeHead(status, { ...SECURITY, ...(text == null ? {} : { 'Content-Type': 'text/plain; charset=utf-8' }), ...headers });
  res.end(text == null ? undefined : text);
}
function json(res, status, body) {
  res.writeHead(status, { ...SECURITY, 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(body === undefined ? null : body));
}
const gotrueError = (res, status, code, msg) => json(res, status, { code: status, error_code: code, msg });
const pgError = (res, status, code, message, details = null, hint = null) => json(res, status, { code, details, hint, message });

async function readBody(req) {
  const chunks = [];
  let size = 0;
  for await (const c of req) {
    size += c.length;
    if (size > 1e6) throw new Error('too big');
    chunks.push(c);
  }
  const text = Buffer.concat(chunks).toString('utf8');
  return text ? JSON.parse(text) : {};
}

// ---------------------------------------------------------------- GoTrue

const account = (id) => ACCOUNTS.find((a) => a.id === id);

function jwt(payload) {
  return b64url({ alg: 'none', typ: 'JWT' }) + '.' + b64url(payload) + '.';
}

function issue(sess, origin) {
  const a = account(sess.userId);
  const exp = nowSec() + S.tokenSecs;
  for (const [t, sid] of S.refresh) if (sid === sess.id) S.refresh.delete(t); // refresh tokens are used once
  const refresh = randomBytes(18).toString('base64url');
  S.refresh.set(refresh, sess.id);
  return {
    access_token: jwt({
      aud: 'authenticated', exp, iat: nowSec(), iss: origin + '/auth/v1', sub: a.id, email: a.email, phone: '',
      app_metadata: { provider: 'email', providers: ['email'] }, user_metadata: {}, role: 'authenticated',
      aal: sess.aal, amr: sess.amr, session_id: sess.id, is_anonymous: false,
    }),
    token_type: 'bearer', expires_in: S.tokenSecs, expires_at: exp, refresh_token: refresh, user: userObject(a),
  };
}

function userObject(a) {
  const factors = S.factors.get(a.id) || [];
  const u = {
    id: a.id, aud: 'authenticated', role: 'authenticated', email: a.email, email_confirmed_at: '2026-09-01T10:00:00Z', phone: '',
    confirmed_at: '2026-09-01T10:00:00Z', last_sign_in_at: iso(Date.now()), app_metadata: { provider: 'email', providers: ['email'] },
    user_metadata: {}, identities: [], created_at: '2026-09-01T10:00:00Z', updated_at: iso(Date.now()), is_anonymous: false,
  };
  if (factors.length) u.factors = factors.map((f) => ({ ...f }));
  return u;
}

// The session behind a request's Bearer token, or null.
function sessionOf(req) {
  const m = /^Bearer (.+)$/.exec(req.headers.authorization || '');
  if (!m) return null;
  const parts = m[1].split('.');
  let p = null;
  try { p = JSON.parse(Buffer.from(parts[1], 'base64url').toString('utf8')); } catch { return 'bad'; }
  if (!p || !p.exp || p.exp < nowSec()) return 'expired';
  const sess = S.sessions.get(p.session_id);
  return sess && sess.userId === p.sub ? sess : 'bad';
}

function codeAt(sess) {
  const t = (sess.amr || []).find((x) => x.method === 'totp');
  return t ? t.timestamp * 1000 : null;
}

function qrSvg(secret) {
  // a QR-looking placeholder: three finder squares and modules from the secret (it doesn't scan; the key does)
  const n = 25;
  let h = 2166136261;
  const cells = [];
  for (let y = 0; y < n; y++) {
    for (let x = 0; x < n; x++) {
      const finder = (x < 7 && y < 7) || (x >= n - 7 && y < 7) || (x < 7 && y >= n - 7);
      if (finder) {
        const fx = x >= n - 7 ? x - (n - 7) : x, fy = y >= n - 7 ? y - (n - 7) : y;
        const on = fx === 0 || fx === 6 || fy === 0 || fy === 6 || (fx >= 2 && fx <= 4 && fy >= 2 && fy <= 4);
        if (on) cells.push(`M${x + 2} ${y + 2}h1v1h-1z`);
        continue;
      }
      h ^= secret.charCodeAt((x * 7 + y * 13) % secret.length) + x * 31 + y;
      h = Math.imul(h, 16777619) >>> 0;
      if (h % 5 < 2) cells.push(`M${x + 2} ${y + 2}h1v1h-1z`);
    }
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 29 29" shape-rendering="crispEdges"><rect width="29" height="29" fill="white"/><path fill="black" d="${cells.join('')}"/></svg>`;
}

async function gotrue(req, res, path, url) {
  const origin = 'http://' + req.headers.host;
  const body = req.method === 'POST' ? await readBody(req).catch(() => null) : {};
  if (body === null) return gotrueError(res, 400, 'bad_json', 'Could not parse request body as JSON');

  if (req.method === 'POST' && path === '/token') {
    const grant = url.searchParams.get('grant_type');
    if (grant === 'password') {
      S.counts.passwordGrants++;
      const a = ACCOUNTS.find((x) => x.email === String(body.email || '').toLowerCase());
      if (!a || a.password !== body.password) return gotrueError(res, 400, 'invalid_credentials', 'Invalid login credentials');
      const sess = { id: randomUUID(), userId: a.id, aal: 'aal1', amr: [{ method: 'password', timestamp: nowSec() }] };
      S.sessions.set(sess.id, sess);
      return json(res, 200, issue(sess, origin));
    }
    if (grant === 'refresh_token') {
      const sid = S.refresh.get(body.refresh_token);
      const sess = sid && S.sessions.get(sid);
      if (!sess) return gotrueError(res, 400, 'refresh_token_not_found', 'Invalid Refresh Token: Refresh Token Not Found');
      S.counts.refreshes++;
      return json(res, 200, issue(sess, origin));
    }
    return gotrueError(res, 400, 'validation_failed', 'Unsupported grant type');
  }

  const sess = sessionOf(req);
  if (!sess || typeof sess === 'string') {
    return gotrueError(res, 401, 'bad_jwt', 'invalid JWT: unable to parse or verify signature, token is ' + (sess === 'expired' ? 'expired' : 'invalid'));
  }
  const a = account(sess.userId);
  const list = S.factors.get(a.id);

  if (req.method === 'GET' && path === '/user') return json(res, 200, userObject(a));

  if (req.method === 'POST' && path === '/logout') {
    S.counts.logouts++;
    for (const [id, x] of S.sessions) if (x.userId === a.id) S.sessions.delete(id); // scope=global, the default
    return send(res, 204, null);
  }

  if (req.method === 'POST' && path === '/factors') {
    if (body.factor_type !== 'totp') return gotrueError(res, 400, 'validation_failed', 'factor_type needs to be totp');
    if (list.some((f) => f.status === 'verified') && sess.aal !== 'aal2') return gotrueError(res, 422, 'insufficient_aal', 'AAL2 required to enroll a new factor');
    const name = String(body.friendly_name || '');
    if (list.some((f) => f.friendly_name === name)) return gotrueError(res, 422, 'mfa_factor_name_conflict', 'A factor with the friendly name "' + name + '" for this user already exists');
    const secret = randomBytes(20).toString('hex').toUpperCase().replace(/[^A-Z2-7]/g, (c) => 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'[c.charCodeAt(0) % 32]).slice(0, 32);
    const f = { id: randomUUID(), friendly_name: name, factor_type: 'totp', status: 'unverified', created_at: iso(Date.now()), updated_at: iso(Date.now()) };
    list.push(f);
    S.counts.enrolls++;
    return json(res, 200, {
      id: f.id, type: 'totp', friendly_name: name,
      totp: { qr_code: 'data:image/svg+xml;utf-8,' + qrSvg(secret), secret, uri: 'otpauth://totp/Roll%20Model%20admin:' + encodeURIComponent(a.email) + '?secret=' + secret + '&issuer=Roll%20Model%20admin' },
    });
  }

  const fm = /^\/factors\/([^/]+)(\/challenge|\/verify)?$/.exec(path);
  if (fm) {
    const f = list.find((x) => x.id === fm[1]);
    if (!f) return gotrueError(res, 404, 'mfa_factor_not_found', 'Factor not found');
    if (req.method === 'DELETE' && !fm[2]) {
      if (f.status === 'verified' && sess.aal !== 'aal2') return gotrueError(res, 422, 'insufficient_aal', 'AAL2 required to unenroll a verified factor');
      list.splice(list.indexOf(f), 1);
      return json(res, 200, { id: f.id });
    }
    if (req.method === 'POST' && fm[2] === '/challenge') {
      const ch = { id: randomUUID(), factorId: f.id, userId: a.id, expires: nowSec() + 300 };
      S.challenges.set(ch.id, ch);
      return json(res, 200, { id: ch.id, type: 'totp', expires_at: ch.expires });
    }
    if (req.method === 'POST' && fm[2] === '/verify') {
      const ch = S.challenges.get(body.challenge_id);
      if (!ch || ch.factorId !== f.id || ch.userId !== a.id) return gotrueError(res, 404, 'mfa_challenge_expired', 'Challenge not found');
      if (ch.expires < nowSec()) { S.challenges.delete(ch.id); return gotrueError(res, 422, 'mfa_challenge_expired', 'MFA challenge has expired, verify against another challenge or create a new challenge.'); }
      if (String(body.code) !== CODE) return gotrueError(res, 422, 'mfa_verification_failed', 'Invalid TOTP code entered');
      S.challenges.delete(ch.id);
      S.counts.verifies++;
      f.status = 'verified';
      f.updated_at = iso(Date.now());
      const age = S.codeAge.get(a.email) ?? a.codeAgeHours ?? 0;
      sess.aal = 'aal2';
      sess.amr = [{ method: 'totp', timestamp: nowSec() - Math.round(age * 3600) }, ...sess.amr.filter((x) => x.method !== 'totp')];
      return json(res, 200, issue(sess, origin));
    }
  }
  return gotrueError(res, 404, 'not_found', 'Not found');
}

// ---------------------------------------------------------------- PostgREST: the admin functions

function whoami(sess) {
  const a = account(sess.userId);
  const listed = a.listed && !S.unlisted.has(a.email);
  const at = codeAt(sess);
  const stale = at != null && Date.now() - at > 12 * HOUR;
  const why = !listed ? 'not_listed' : sess.aal !== 'aal2' || at == null ? 'needs_code' : stale ? 'stale' : null;
  return { id: a.id, email: a.email, aal: sess.aal, listed, admin: why === null, why, code_at: at == null ? null : iso(at) };
}

// "That's the most you can do in an hour": true when this admin may do one more.
function allowed(email, action) {
  const key = email + ' ' + action;
  const list = (S.used.get(key) || []).filter((t) => t > Date.now() - HOUR);
  S.used.set(key, list);
  if (list.length >= S.limits[action]) return false;
  list.push(Date.now());
  return true;
}

function audit(email, action, target, detail) {
  S.audit.unshift({ at: iso(Date.now()), admin: email, action, target, detail });
}

const isInt = (v) => Number.isInteger(v);
const player = (id) => S.world.players.find((p) => p.id === id) || null;
const publicPlayer = (p) => {
  const { sessions, ...rest } = p;
  return { ...rest, audit: S.audit.filter((r) => r.target === p.id).map(({ target, ...r }) => r) };
};

async function rpc(req, res, fn) {
  S.counts.rpc++;
  if (!SIG[fn]) return pgError(res, 404, 'PGRST202', 'Could not find the function public.' + fn + ' without parameters in the schema cache', null, null);
  let body;
  try { body = await readBody(req); } catch { return pgError(res, 400, 'PGRST102', 'Empty or invalid json'); }
  if (!body || typeof body !== 'object' || Array.isArray(body)) return pgError(res, 400, 'PGRST102', 'Empty or invalid json');
  const keys = Object.keys(body);
  if (keys.some((k) => !SIG[fn].includes(k)) || (REQUIRED[fn] || []).some((k) => !keys.includes(k))) {
    return pgError(res, 404, 'PGRST202', 'Could not find the function public.' + fn + '(' + keys.sort().join(', ') + ') in the schema cache',
      'Searched for the function public.' + fn + ' with parameters ' + keys.sort().join(', ') + ' or with a single unnamed json/jsonb parameter, but no matches were found in the schema cache.');
  }
  const sess = sessionOf(req);
  if (sess === null) return pgError(res, 401, '42501', 'permission denied for function ' + fn);
  if (typeof sess === 'string') return pgError(res, 401, 'PGRST301', sess === 'expired' ? 'JWT expired' : 'JWSError (CompactDecodeError Invalid number of parts: Expected 3 parts; got 2)');
  if (S.delay) await new Promise((r) => setTimeout(r, S.delay));
  const who = whoami(sess);
  if (fn === 'adm_whoami') return json(res, 200, who);
  if (!who.admin) return pgError(res, 403, '42501', 'not an admin');
  const fail = S.fail.get(fn);
  if (fail && fail.count > 0) { fail.count--; return pgError(res, fail.status, 'XX000', 'mock failure for ' + fn); }

  const days = body.p_days;
  if (days != null && !isInt(days)) return pgError(res, 400, '22P02', 'invalid input syntax for type integer: "' + days + '"');
  const id = body.p_id;
  if (id !== undefined && (typeof id !== 'string' || !UUID.test(id))) return pgError(res, 400, '22P02', 'invalid input syntax for type uuid: "' + id + '"');
  const w = S.world;

  switch (fn) {
    case 'adm_overview': return json(res, 200, overview(w, days ?? 30));
    case 'adm_modes': return json(res, 200, modes(w, days ?? 30));
    case 'adm_progress': {
      if (body.p_steps != null && (!Array.isArray(body.p_steps) || body.p_steps.some((x) => typeof x !== 'string'))) return pgError(res, 400, '22P02', 'malformed array literal');
      return json(res, 200, progress(w, body.p_steps));
    }
    case 'adm_economy': return json(res, 200, economy(w, days ?? 30, S.prices));
    case 'adm_ads': return json(res, 200, ads(w, days ?? 30));
    case 'adm_iap': return json(res, 200, iapData(w, days ?? 30));
    case 'adm_prices': return json(res, 200, [...S.prices].map(([item, p]) => ({ item, ...p })).sort((a, b) => b.updated_at.localeCompare(a.updated_at)));
    case 'adm_set_price': {
      const item = body.p_item, price = body.p_price;
      if (typeof item !== 'string' || !/^[a-z0-9_]{1,32}$/.test(item)) return json(res, 200, { ok: false, why: 'item' });
      if (price !== null && (!isInt(price) || price < 0 || price > 100000)) return json(res, 200, { ok: false, why: 'range' });
      if (!allowed(who.email, 'set_price')) return json(res, 200, { ok: false, why: 'slow_down' });
      const from = S.prices.has(item) ? S.prices.get(item).price : null;
      if (price === null) S.prices.delete(item);
      else S.prices.set(item, { price, updated_at: iso(Date.now()), updated_by: who.email });
      audit(who.email, 'set_price', item, { from, to: price });
      return json(res, 200, { ok: true });
    }
    case 'adm_find': {
      const q = String(body.p_q ?? '').trim();
      if (q.length < 2 || q.length > 40) return json(res, 200, []);
      const code = q.replace(/\s+/g, '').toUpperCase();
      const lower = q.toLowerCase();
      const hits = w.players.filter((p) => p.id === q.toLowerCase() || (/^[2-9A-HJKMNP-Z]{8}$/.test(code) && p.code === code) ||
        (p.name && p.name.toLowerCase().startsWith(lower)));
      const score = (p) => (p.id === lower || p.code === code ? 0 : p.name && p.name.toLowerCase() === lower ? 1 : 2);
      hits.sort((a, b) => score(a) - score(b) || (a.name || '').length - (b.name || '').length || (a.name || '').localeCompare(b.name || ''));
      return json(res, 200, hits.slice(0, 25).map((p) => ({ id: p.id, name: p.name, code: p.code, rank: p.rank, account: p.account, created_at: p.created_at, last_seen: p.last_seen })));
    }
    case 'adm_player': {
      const p = player(id);
      return json(res, 200, p ? publicPlayer(p) : null);
    }
    case 'adm_set_password': {
      const p = player(id);
      if (!p) return json(res, 200, { ok: false, why: 'missing' });
      if (p.admin) return json(res, 200, { ok: false, why: 'admin' });
      if (!p.account) return json(res, 200, { ok: false, why: 'anonymous' });
      const pw = body.p_password;
      if (typeof pw !== 'string' || pw.length < 8 || pw.length > 72 || !/[A-Za-z]/.test(pw) || !/[0-9]/.test(pw)) return json(res, 200, { ok: false, why: 'weak' });
      if (!allowed(who.email, 'set_password')) return json(res, 200, { ok: false, why: 'slow_down' });
      p.sessions = 0; // signed out everywhere; the password itself is never kept
      audit(who.email, 'set_password', p.id, { name: p.name });
      return json(res, 200, { ok: true });
    }
    case 'adm_signout': {
      const p = player(id);
      if (!p) return json(res, 200, { ok: false, why: 'missing' });
      if (p.admin) return json(res, 200, { ok: false, why: 'admin' });
      if (!allowed(who.email, 'signout')) return json(res, 200, { ok: false, why: 'slow_down' });
      const n = p.sessions || 0;
      p.sessions = 0;
      audit(who.email, 'signout', p.id, { name: p.name, sessions: n });
      return json(res, 200, { ok: true, sessions: n });
    }
    case 'adm_delete_player': {
      const p = player(id);
      if (!p) return json(res, 200, { ok: false, why: 'missing' });
      if (p.admin) return json(res, 200, { ok: false, why: 'admin' });
      const want = (p.name || p.id).toLowerCase();
      if (String(body.p_confirm ?? '').trim().toLowerCase() !== want) return json(res, 200, { ok: false, why: 'confirm' });
      if (!allowed(who.email, 'delete_player')) return json(res, 200, { ok: false, why: 'slow_down' });
      w.players.splice(w.players.indexOf(p), 1);
      audit(who.email, 'delete_player', p.id, { name: p.name, id: p.id });
      return json(res, 200, { ok: true });
    }
    case 'adm_audit': {
      const limit = body.p_limit == null ? 100 : Math.max(1, Math.min(500, isInt(body.p_limit) ? body.p_limit : 100));
      return json(res, 200, S.audit.slice(0, limit));
    }
  }
  return pgError(res, 404, 'PGRST202', 'Could not find the function public.' + fn);
}

// ---------------------------------------------------------------- test-only controls

async function control(req, res, path) {
  if (req.method === 'GET' && path === '/state') {
    return json(res, 200, {
      dataset: S.dataset, iap: S.iap, counts: S.counts, sessions: S.sessions.size, tokenSecs: S.tokenSecs,
      prices: Object.fromEntries(S.prices), audit: S.audit.length, players: S.world.players.length,
    });
  }
  let body;
  try { body = await readBody(req); } catch { return json(res, 400, { error: 'bad json' }); }
  if (req.method === 'POST' && path === '/reset') { reset({ dataset: body.dataset || 'full', iap: !!body.iap }); return json(res, 200, { ok: true, dataset: S.dataset }); }
  if (req.method === 'POST' && path === '/config') {
    if (body.tokenSecs) S.tokenSecs = Number(body.tokenSecs);
    if (body.delay != null) S.delay = Number(body.delay);
    if (body.unlist) S.unlisted.add(body.unlist);
    if (body.relist) S.unlisted.delete(body.relist);
    if (body.limits) Object.assign(S.limits, body.limits);
    if (body.fail) S.fail.set(body.fail.fn, { status: body.fail.status || 500, count: body.fail.count || 1 });
    if (body.codeAge) { // age the code of an email's live sessions, e.g. { email, hours: 13 }
      for (const sess of S.sessions.values()) {
        if (account(sess.userId).email !== body.codeAge.email) continue;
        sess.amr = sess.amr.map((x) => (x.method === 'totp' ? { ...x, timestamp: nowSec() - Math.round(body.codeAge.hours * 3600) } : x));
      }
    }
    return json(res, 200, { ok: true });
  }
  return json(res, 404, { error: 'unknown control' });
}

// ---------------------------------------------------------------- static files

async function serveStatic(req, res, path) {
  if (req.method !== 'GET' && req.method !== 'HEAD') return send(res, 405, 'Method not allowed', { Allow: 'GET, HEAD' });
  if (path === '/') path = '/index.html';
  if (path === '/js/config.js') return send(res, 200, req.method === 'HEAD' ? '' : CONFIG, { 'Content-Type': TYPES['.js'] });
  // only the app's own files: the shell, the stylesheet, the icon, the catalog and the modules
  const ok = /^\/(index\.html|app\.css|icon\.svg|catalog\.json)$/.test(path) || /^\/js\/([a-z0-9_-]+\/)?[a-z0-9_-]+\.js$/.test(path);
  const file = normalize(join(ROOT, path));
  if (!ok || !file.startsWith(ROOT + sep)) return send(res, 404, 'Not found');
  let data;
  try { data = await readFile(file); } catch { return send(res, 404, 'Not found'); }
  res.writeHead(200, { ...SECURITY, 'Content-Type': TYPES[extname(file)] || 'application/octet-stream', 'Content-Length': data.length });
  res.end(req.method === 'HEAD' ? undefined : data);
}

// ---------------------------------------------------------------- the server

export function createServer() {
  if (!S) reset();
  return http.createServer(async (req, res) => {
    let url;
    try { url = new URL(req.url, 'http://localhost'); } catch { return send(res, 400, 'Bad request'); }
    const path = url.pathname;
    try {
      if (path.startsWith('/__mock/')) return await control(req, res, path.slice(7));
      if (path.startsWith('/auth/v1/') || path.startsWith('/rest/v1/')) {
        if (req.headers.apikey !== KEY) return json(res, 401, { message: 'No API key found in request', hint: 'No `apikey` request header or url param was found.' });
        if (path.startsWith('/auth/v1/')) return await gotrue(req, res, path.slice(8), url);
        const m = /^\/rest\/v1\/rpc\/([a-z0-9_]+)$/.exec(path);
        if (!m || req.method !== 'POST') return pgError(res, 404, 'PGRST125', 'Invalid path specified in request URL');
        return await rpc(req, res, m[1]);
      }
      return await serveStatic(req, res, path);
    } catch (e) {
      console.error('mock error:', e && e.message);
      if (!res.headersSent) send(res, 500, { message: 'mock error' });
    }
  });
}

export function start({ port = Number(process.env.PORT) || 8791, host = process.env.HOST || '127.0.0.1', quiet = false } = {}) {
  const server = createServer();
  return new Promise((resolve) => server.listen(port, host, () => {
    const addr = server.address();
    if (!quiet) {
      console.log(`Roll Model admin mock: http://${host}:${addr.port}/  (data: ${S.dataset}${S.iap ? ', with purchases' : ''})`);
      console.log('  admin@example.com / correct-horse-9 (sets up an authenticator), owner@example.com / correct-horse-9 (has one)');
      console.log('  player@example.com / player-pass-1 (not an admin). Authenticator code: 123456');
    }
    resolve(server);
  }));
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) start();
