// Signing in with Supabase Auth (GoTrue), as admin/API.md describes: password, then an authenticator-app code (TOTP).
// The session lives in sessionStorage only, so closing the tab signs out. Tokens are never logged or put in a URL.

import { SUPABASE_URL, PUBLISHABLE_KEY } from './config.js';

const KEY = 'rm_admin_session';
let S = null;            // { access_token, refresh_token, expires_at (unix s), email, id }
let timer = 0;
let refreshing = null;   // one refresh at a time
const lostHandlers = new Set();

export class AuthError extends Error {
  constructor(message, code = '', status = 0) { super(message); this.name = 'AuthError'; this.code = code; this.status = status; }
}

// What GoTrue's error codes mean, in plain words.
const MESSAGES = {
  net: "Can't reach the sign-in server. Check your connection and try again.",
  invalid_credentials: 'Wrong email or password.',
  invalid_grant: 'Wrong email or password.',
  email_not_confirmed: "This email address isn't confirmed yet.",
  user_banned: 'This account is blocked.',
  over_request_rate_limit: 'Too many tries. Wait a minute, then try again.',
  mfa_verification_failed: "That code didn't work. Check your authenticator app and try again.",
  mfa_verification_rejected: "That code didn't work. Check your authenticator app and try again.",
  mfa_challenge_expired: 'That took too long. Enter the current code again.',
  mfa_factor_not_found: 'Your authenticator setup changed. Sign in again.',
  mfa_factor_name_conflict: 'An authenticator is already being set up. Start again.',
  session_not_found: 'Your session ended. Sign in again.',
  refresh_token_not_found: 'Your session ended. Sign in again.',
  refresh_token_already_used: 'Your session ended. Sign in again.',
  bad_jwt: 'Your session ended. Sign in again.',
};

// GoTrue answers {"code":400,"error_code":"invalid_credentials","msg":"..."} (older versions: {"error","error_description"}).
function errorFrom(status, body) {
  const code = String((body && (body.error_code || body.error)) || '');
  const said = body && (body.msg || body.error_description || body.message);
  if (status === 429) return new AuthError(MESSAGES.over_request_rate_limit, 'over_request_rate_limit', status);
  if (MESSAGES[code]) return new AuthError(MESSAGES[code], code, status);
  if (status === 422 && /totp|code/i.test(String(said || ''))) return new AuthError(MESSAGES.mfa_verification_failed, 'mfa_verification_failed', status);
  return new AuthError(said ? 'Sign-in failed: ' + String(said).slice(0, 160) : 'Sign-in failed (' + status + '). Try again.', code, status);
}

// The JWT payload is base64url JSON (only read, never trusted for anything the server doesn't check).
export function decodeJwt(token) {
  try {
    const part = String(token).split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const bin = atob(part + '='.repeat((4 - (part.length % 4)) % 4));
    return JSON.parse(new TextDecoder().decode(Uint8Array.from(bin, (c) => c.charCodeAt(0))));
  } catch {
    return null;
  }
}

async function call(path, { method = 'POST', body, token } = {}) {
  const headers = { apikey: PUBLISHABLE_KEY, 'Content-Type': 'application/json' };
  if (token) headers.Authorization = 'Bearer ' + token;
  let res;
  try {
    res = await fetch(SUPABASE_URL + '/auth/v1' + path, {
      method, headers, body: body ? JSON.stringify(body) : undefined,
      cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer',
    });
  } catch {
    throw new AuthError(MESSAGES.net, 'net', 0);
  }
  const text = await res.text();
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch { json = null; }
  if (!res.ok) throw errorFrom(res.status, json);
  return json;
}

// ---------------------------------------------------------------- the session

function fromTokens(j) {
  if (!j || !j.access_token || !j.refresh_token) throw new AuthError('The sign-in server sent something unexpected. Try again.', 'bad_response');
  const c = decodeJwt(j.access_token) || {};
  const now = Math.floor(Date.now() / 1000);
  return {
    access_token: j.access_token,
    refresh_token: j.refresh_token,
    expires_at: Number(j.expires_at) || (j.expires_in ? now + Number(j.expires_in) : Number(c.exp) || now + 3600),
    email: (j.user && j.user.email) || c.email || '',
    id: (j.user && j.user.id) || c.sub || '',
  };
}

function store(next) {
  S = next;
  try {
    if (next) sessionStorage.setItem(KEY, JSON.stringify(next));
    else sessionStorage.removeItem(KEY);
  } catch { /* storage blocked: the session still works for this page */ }
  schedule();
}

export function load() {
  try { S = JSON.parse(sessionStorage.getItem(KEY) || 'null'); } catch { S = null; }
  if (!S || !S.access_token || !S.refresh_token) S = null;
  schedule();
  return S;
}

export const session = () => S;
export const claims = () => (S ? decodeJwt(S.access_token) : null);
export const aal = () => (claims() || {}).aal || null;

// Something ended the session from underneath us (refresh refused, token gone): tell the app.
export function onLost(fn) { lostHandlers.add(fn); }
function lost(message) {
  if (!S) return;
  store(null);
  for (const fn of lostHandlers) fn(message);
}

// ---------------------------------------------------------------- the sign-in steps

// 1. email and password: a session at aal1
export async function signIn(email, password) {
  const j = await call('/token?grant_type=password', { body: { email, password } });
  store(fromTokens(j));
  return S;
}

// 2. the account's TOTP factors
export async function factors() {
  const u = await call('/user', { method: 'GET', token: S.access_token });
  return ((u && u.factors) || []).filter((f) => (f.factor_type || f.type) === 'totp');
}

// 3. no verified factor yet: remove any half-made one, then enrol a new one
export async function enroll() {
  for (const f of await factors()) {
    if (f.status !== 'verified') await call('/factors/' + encodeURIComponent(f.id), { method: 'DELETE', token: S.access_token });
  }
  const j = await call('/factors', { body: { factor_type: 'totp', friendly_name: 'Roll Model admin' }, token: S.access_token });
  const t = (j && j.totp) || {};
  // only ever show the QR code as an image from a data: URI
  const qr = typeof t.qr_code === 'string' && /^data:image\/(svg\+xml|png)[;,]/i.test(t.qr_code) ? t.qr_code : '';
  return { id: j && j.id, qr, secret: String(t.secret || ''), uri: String(t.uri || '') };
}

// 4. a code: challenge, then verify; the new session is at aal2
export async function verify(factorId, code) {
  const id = encodeURIComponent(factorId);
  const ch = await call('/factors/' + id + '/challenge', { token: S.access_token });
  const j = await call('/factors/' + id + '/verify', { body: { challenge_id: ch && ch.id, code }, token: S.access_token });
  store(fromTokens(j));
  return S;
}

// 6. keep it fresh: a minute before it expires, and whenever a call finds it nearly expired
export function refresh() {
  if (!S) return Promise.reject(new AuthError(MESSAGES.session_not_found, 'session_not_found'));
  if (refreshing) return refreshing;
  const rt = S.refresh_token;
  refreshing = call('/token?grant_type=refresh_token', { body: { refresh_token: rt } })
    .then((j) => { if (S && S.refresh_token === rt) store(fromTokens(j)); return S; })
    .catch((e) => {
      if (e.code !== 'net') lost(MESSAGES.session_not_found);
      else if (S && S.expires_at * 1000 <= Date.now()) lost("Your session ended because the server couldn't be reached. Sign in again.");
      else schedule(15000); // offline for now: try again soon, while the token still works
      throw e;
    })
    .finally(() => { refreshing = null; });
  return refreshing;
}

function schedule(retryMs) {
  clearTimeout(timer);
  if (!S) return;
  const left = S.expires_at * 1000 - Date.now();
  // a minute before it expires; a token with less than that to live is refreshed halfway, never in a tight loop
  const ms = retryMs ?? (left > 60000 ? left - 60000 : left / 2);
  timer = setTimeout(() => { refresh().catch(() => {}); }, Math.max(0, ms));
}

// Before a data call: refresh first if the token has under 30 seconds left.
export async function fresh() {
  if (S && S.expires_at * 1000 - Date.now() < 30000) await refresh();
  return S;
}

// Timers sleep in a background tab: check again when the tab comes back.
if (typeof document !== 'undefined') {
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && S) {
      if (S.expires_at * 1000 - Date.now() < 90000) refresh().catch(() => {});
      else schedule();
    }
  });
}

// 7. sign out: forget the session here first, then tell the server.
export async function signOut() {
  const token = S && S.access_token;
  store(null);
  if (token) {
    try { await call('/logout', { token }); } catch { /* signed out here either way */ }
  }
}
