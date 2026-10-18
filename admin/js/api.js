// The admin functions: PostgREST remote procedure calls, POST /rest/v1/rpc/<name> with named arguments.
// Errors come back as ApiError with a kind the pages can act on:
//   net     the server couldn't be reached: show a retry
//   denied  403 "not an admin": the app signs out with a reason (see main.js)
//   auth    the session is gone: the app signs out
//   server  anything else: show the message and a retry

import { SUPABASE_URL, PUBLISHABLE_KEY } from './config.js';
import * as auth from './auth.js';

export class ApiError extends Error {
  constructor(kind, message, status = 0, code = '') { super(message); this.name = 'ApiError'; this.kind = kind; this.status = status; this.code = code; }
}

let onDenied = () => {};
export function setDeniedHandler(fn) { onDenied = fn; }

async function post(name, args) {
  const s = auth.session();
  const headers = { apikey: PUBLISHABLE_KEY, 'Content-Type': 'application/json', Accept: 'application/json' };
  if (s) headers.Authorization = 'Bearer ' + s.access_token;
  try {
    return await fetch(SUPABASE_URL + '/rest/v1/rpc/' + name, {
      method: 'POST', headers, body: JSON.stringify(args || {}),
      cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer',
    });
  } catch {
    throw new ApiError('net', "Can't reach the server.");
  }
}

async function body(res) {
  const text = await res.text();
  try { return text ? JSON.parse(text) : null; } catch { return null; }
}

export async function rpc(name, args = {}) {
  try { await auth.fresh(); } catch (e) { if (e.code === 'net') throw new ApiError('net', "Can't reach the server."); }
  if (!auth.session()) throw new ApiError('auth', 'Signed out.');
  let res = await post(name, args);
  if (res.status === 401) {
    // the token expired under us: refresh once and try again
    try { await auth.refresh(); } catch { throw new ApiError('auth', 'Your session ended. Sign in again.', 401); }
    res = await post(name, args);
    if (res.status === 401) throw new ApiError('auth', 'Your session ended. Sign in again.', 401);
  }
  const json = await body(res);
  if (res.status === 403) {
    const err = new ApiError('denied', 'not an admin', 403, (json && json.code) || '42501');
    if (name !== 'adm_whoami') onDenied(err);
    throw err;
  }
  if (!res.ok) {
    // PostgREST answers {"code":"...","message":"...","details":null,"hint":null}
    const code = String((json && json.code) || '');
    const said = json && (json.message || json.msg);
    throw new ApiError('server', 'The server had a problem (' + res.status + (code ? ', ' + code : '') + ')' +
      (said ? ': ' + String(said).slice(0, 160) : '') + '. Try again.', res.status, code);
  }
  return json;
}

// Every "why" an admin function can answer, as a plain sentence.
export const WHY = {
  weak: 'That password is too weak. Use 8 to 72 characters with at least one letter and one digit.',
  missing: "This player doesn't exist any more. They may have deleted their account.",
  anonymous: "This player has no account (they play without one), so there's no password to reset.",
  admin: "That's an admin account. Admin accounts can't be changed from the dashboard.",
  confirm: "That doesn't match. Type their username (any case), or their user id if they have no username.",
  item: "That item id isn't valid.",
  range: 'A price has to be a whole number from 0 to 100,000.',
  slow_down: "That's the most you can do in an hour. Try again later.",
};

export const whyText = (why) => WHY[why] || "The server didn't do it" + (why ? ' (' + String(why).slice(0, 40) + ').' : '.');
