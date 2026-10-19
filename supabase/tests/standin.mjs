// A stand-in for the parts of Supabase the game and the admin dashboard use, over the local Postgres with the real migrations
// (and tests/local_stub.sql). Test use only: never point it at the real project.
//   PGURL=postgres://postgres@localhost:54329/rmtest PORT=54330 node supabase/tests/standin.mjs
//
// Sign-in (as Supabase Auth does it, the parts that are used):
//   POST /auth/v1/signup                              an anonymous player
//   POST /auth/v1/token?grant_type=password           { email, password }: checked against auth.users.encrypted_password (bcrypt)
//   POST /auth/v1/token?grant_type=refresh_token      { refresh_token }: only while its session is still in auth.sessions
//   GET  /auth/v1/user, PUT /auth/v1/user             the user and their factors; { email } makes them permanent, { password } sets it
//   POST /auth/v1/logout[?scope=local|global]
//   POST /auth/v1/factors, DELETE /auth/v1/factors/<id>, POST /auth/v1/factors/<id>/challenge, POST /auth/v1/factors/<id>/verify
//        an authenticator app (TOTP, RFC 6238). A verified code lifts the session to aal2, with a totp entry in its amr claim.
// Data (as PostgREST does it): POST /rest/v1/rpc/<fn> with the JSON body as named arguments, run as "authenticated" with the token's
// claims, or as "anon" with no token; errors come back with PostgREST's codes (42501: 403 signed in, 401 anonymous).
// GET /__log: the last calls (rm_track's bodies too), for tests to look at.
import http from 'node:http';
import { createHmac, randomUUID, randomBytes } from 'node:crypto';
import pg from 'pg';

const PORT = +(process.env.PORT || 54330), KEY = process.env.KEY || 'test-publishable-key', TTL = +(process.env.TTL || 3600);
const SECRET = randomBytes(32);
const db = new pg.Pool({ connectionString: process.env.PGURL || 'postgres://postgres@localhost:54329/rmtest', max: 8 });
const b64 = b => Buffer.from(b).toString('base64url');
const sign = c => { const h = b64(JSON.stringify({ alg: 'HS256', typ: 'JWT' })), p = b64(JSON.stringify(c)); return h + '.' + p + '.' + createHmac('sha256', SECRET).update(h + '.' + p).digest('base64url'); };
function verify(t) {
  const [h, p, s] = String(t || '').split('.'); if (!s) return null;
  if (createHmac('sha256', SECRET).update(h + '.' + p).digest('base64url') !== s) return null;
  const c = JSON.parse(Buffer.from(p, 'base64url')); return c.exp > Date.now() / 1000 ? c : null;
}
const now = () => Math.floor(Date.now() / 1000);

// ---- the authenticator app's codes
const B32 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
function toB32(buf) { let bits = 0, v = 0, out = ''; for (const x of buf) { v = (v << 8) | x; bits += 8; while (bits >= 5) { out += B32[(v >>> (bits - 5)) & 31]; bits -= 5; } v &= (1 << bits) - 1; } if (bits) out += B32[(v << (5 - bits)) & 31]; return out; }
function fromB32(s) { let bits = 0, v = 0; const out = []; for (const ch of String(s).replace(/=+$/, '').toUpperCase()) { const i = B32.indexOf(ch); if (i < 0) continue; v = (v << 5) | i; bits += 5; if (bits >= 8) { out.push((v >>> (bits - 8)) & 255); bits -= 8; } v &= (1 << bits) - 1; } return Buffer.from(out); }
function totp(secret, at = Date.now()) {
  const c = Buffer.alloc(8); c.writeBigUInt64BE(BigInt(Math.floor(at / 30000)));
  const h = createHmac('sha1', fromB32(secret)).update(c).digest(), o = h[h.length - 1] & 15;
  return String((((h[o] & 127) << 24) | (h[o + 1] << 16) | (h[o + 2] << 8) | h[o + 3]) % 1e6).padStart(6, '0');
}

// ---- sessions: the rows Supabase keeps (auth.sessions, auth.refresh_tokens), with each one's assurance level and sign-in methods here
const SESS = new Map(), FACTORS = new Map(), CHALLENGES = new Map();
async function userOf(id) { return (await db.query('select id, email, is_anonymous, created_at from auth.users where id = $1', [id])).rows[0] || null; }
async function issue(u, sid) {
  const s = SESS.get(sid), rt = randomBytes(16).toString('hex'), t = now();
  await db.query('insert into auth.refresh_tokens (token, user_id, session_id) values ($1, $2, $3)', [rt, u.id, sid]);
  const claims = { sub: u.id, role: 'authenticated', aud: 'authenticated', email: u.email || '', is_anonymous: u.is_anonymous !== false, session_id: sid, aal: s.aal, amr: s.amr, iat: t, exp: t + TTL };
  return { access_token: sign(claims), token_type: 'bearer', expires_in: TTL, expires_at: t + TTL, refresh_token: rt, user: await userJson(u) };
}
async function newSession(u, method) {
  const sid = randomUUID(); await db.query('insert into auth.sessions (id, user_id) values ($1, $2)', [sid, u.id]);
  SESS.set(sid, { aal: 'aal1', amr: [{ method, timestamp: now() }] }); return issue(u, sid);
}
const factorsOf = uid => [...FACTORS.values()].filter(f => f.user === uid).map(f => ({ id: f.id, factor_type: 'totp', status: f.status, friendly_name: f.name, created_at: f.at, updated_at: f.at }));
async function userJson(u) { return { id: u.id, aud: 'authenticated', role: 'authenticated', email: u.email || '', is_anonymous: u.is_anonymous !== false, factors: factorsOf(u.id), created_at: u.created_at }; }

const log = [];
const send = (res, code, obj) => { res.writeHead(code, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }); res.end(obj === undefined ? '' : JSON.stringify(obj)); };
const authErr = (res, code, ec, msg) => send(res, code, { code, error_code: ec, msg });
const ARGS = new Map();
async function argTypes(fn) {
  if (ARGS.has(fn)) return ARGS.get(fn);
  const r = await db.query("select proargnames n, (select array_agg(format_type(t, null) order by i) from unnest(proargtypes) with ordinality u(t, i)) t from pg_proc where proname = $1 and pronamespace = 'public'::regnamespace", [fn]);
  const v = r.rows[0] ? (r.rows[0].n || []).map((n, i) => [n, r.rows[0].t[i]]) : null; ARGS.set(fn, v); return v;
}

http.createServer(async (req, res) => {
  if (req.method === 'OPTIONS') { res.writeHead(204, { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'apikey, authorization, content-type, x-client-info, prefer', 'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS', 'Access-Control-Max-Age': '600' }); return res.end(); }
  if (req.url.startsWith('/__log')) return send(res, 200, log.slice(-200));
  let body = ''; for await (const c of req) body += c;
  let j = {}; try { j = body ? JSON.parse(body) : {}; } catch (e) { return send(res, 400, { message: 'bad json' }); }
  if (req.headers.apikey !== KEY) return send(res, 401, { message: 'Invalid API key' });
  const u = new URL(req.url, 'http://x'), path = u.pathname, bearer = (req.headers.authorization || '').replace(/^Bearer /, ''), claims = bearer ? verify(bearer) : null;
  log.push({ at: Date.now(), m: req.method, path: path + u.search, body: /rm_track|rm_config/.test(path) ? j : undefined, auth: !!claims });
  try {
    // ---------------------------------------------------------------- sign-in
    if (path === '/auth/v1/signup' && req.method === 'POST') {
      const id = randomUUID(); await db.query('insert into auth.users (id) values ($1)', [id]);
      return send(res, 200, await newSession(await userOf(id), 'anonymous'));
    }
    if (path === '/auth/v1/token' && u.searchParams.get('grant_type') === 'password') {
      const r = await db.query('select id from auth.users where lower(email) = lower($1) and encrypted_password is not null and encrypted_password = extensions.crypt($2, encrypted_password)', [String(j.email || ''), String(j.password || '')]);
      if (!r.rows[0]) return authErr(res, 400, 'invalid_credentials', 'Invalid login credentials');
      await db.query('update auth.users set last_sign_in_at = now() where id = $1', [r.rows[0].id]);
      return send(res, 200, await newSession(await userOf(r.rows[0].id), 'password'));
    }
    if (path === '/auth/v1/token' && u.searchParams.get('grant_type') === 'refresh_token') {
      const r = await db.query("update auth.refresh_tokens set revoked = true where token = $1 and not revoked returning user_id, session_id", [String(j.refresh_token || '')]);
      const row = r.rows[0], ok = row && SESS.has(row.session_id) && (await db.query('select 1 from auth.sessions where id = $1', [row.session_id])).rows.length;
      if (!ok) return authErr(res, 400, 'refresh_token_not_found', 'Invalid Refresh Token: Refresh Token Not Found');
      const us = await userOf(row.user_id); if (!us) return authErr(res, 400, 'refresh_token_not_found', 'Invalid Refresh Token: Refresh Token Not Found');
      return send(res, 200, await issue(us, row.session_id));
    }
    // everything below needs a live session
    const live = claims && SESS.has(claims.session_id) && (await db.query('select 1 from auth.sessions where id = $1', [claims.session_id])).rows.length;
    if (path.startsWith('/auth/v1/') && !live) return authErr(res, 401, 'session_not_found', 'Session from session_id claim in JWT does not exist');
    if (path === '/auth/v1/user' && req.method === 'GET') return send(res, 200, await userJson(await userOf(claims.sub)));
    if (path === '/auth/v1/user' && req.method === 'PUT') {
      if (j.email) {
        if ((await db.query('select 1 from auth.users where lower(email) = lower($1) and id <> $2', [j.email, claims.sub])).rows.length) return authErr(res, 422, 'email_exists', 'A user with this email address has already been registered');
        await db.query('update auth.users set email = $1, is_anonymous = false where id = $2', [j.email, claims.sub]);
      }
      if (j.password) {
        if (String(j.password).length < 6) return authErr(res, 422, 'weak_password', 'Password should be at least 6 characters.');
        await db.query("update auth.users set encrypted_password = extensions.crypt($1, extensions.gen_salt('bf')) where id = $2", [String(j.password), claims.sub]);
      }
      return send(res, 200, await userJson(await userOf(claims.sub)));
    }
    if (path === '/auth/v1/logout') {
      if (u.searchParams.get('scope') === 'global') { await db.query('delete from auth.sessions where user_id = $1', [claims.sub]); }
      else await db.query('delete from auth.sessions where id = $1', [claims.session_id]);
      res.writeHead(204, { 'Access-Control-Allow-Origin': '*' }); return res.end();
    }
    if (path === '/auth/v1/factors' && req.method === 'POST') {
      if (j.factor_type !== 'totp') return authErr(res, 422, 'validation_failed', 'factor_type needs to be totp');
      const us = await userOf(claims.sub), id = randomUUID(), secret = toB32(randomBytes(20)), name = String(j.friendly_name || '');
      if (factorsOf(us.id).some(f => f.friendly_name === name && name)) return authErr(res, 422, 'mfa_factor_name_conflict', 'A factor with the friendly name "' + name + '" for this user already exists');
      FACTORS.set(id, { id, user: us.id, secret, status: 'unverified', name, at: new Date().toISOString() });
      const uri = 'otpauth://totp/localhost:' + encodeURIComponent(us.email || us.id) + '?secret=' + secret + '&issuer=localhost';
      const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 29 29" shape-rendering="crispEdges"><rect width="29" height="29" fill="#fff"/><path d="M1 1h7v7H1zM21 1h7v7h-7zM1 21h7v7H1z" fill="none" stroke="#000" stroke-width="2"/><path d="M11 3h2v2h-2zM14 6h3v2h-3zM10 11h9v2h-9zM12 15h2v6h-2zM16 17h5v2h-5zM22 12h2v4h-2z"/></svg>';
      return send(res, 200, { id, type: 'totp', friendly_name: name, totp: { qr_code: 'data:image/svg+xml;utf-8,' + svg, secret, uri } });
    }
    const fm = /^\/auth\/v1\/factors\/([0-9a-f-]{36})(\/challenge|\/verify)?$/.exec(path);
    if (fm) {
      const f = FACTORS.get(fm[1]); if (!f || f.user !== claims.sub) return authErr(res, 404, 'mfa_factor_not_found', 'Factor not found');
      if (!fm[2] && req.method === 'DELETE') {
        if (f.status === 'verified' && SESS.get(claims.session_id).aal !== 'aal2') return authErr(res, 403, 'insufficient_aal', 'AAL2 required to unenroll verified factor');
        FACTORS.delete(f.id); return send(res, 200, { id: f.id });
      }
      if (fm[2] === '/challenge') { const id = randomUUID(), exp = now() + 300; CHALLENGES.set(id, { factor: f.id, exp }); return send(res, 200, { id, type: 'totp', expires_at: exp }); }
      if (fm[2] === '/verify') {
        const ch = CHALLENGES.get(String(j.challenge_id || '')); CHALLENGES.delete(String(j.challenge_id || ''));
        if (!ch || ch.factor !== f.id || ch.exp < now()) return authErr(res, 422, 'mfa_challenge_expired', 'MFA challenge has expired, verify against another challenge or create a new challenge.');
        const code = String(j.code || ''), t = Date.now();
        if (![t - 30000, t, t + 30000].some(x => totp(f.secret, x) === code)) return authErr(res, 422, 'mfa_verification_failed', 'Invalid TOTP code entered');
        f.status = 'verified'; const s = SESS.get(claims.session_id); s.aal = 'aal2'; s.amr = [{ method: 'totp', timestamp: now() }, ...s.amr.filter(x => x.method !== 'totp')];
        return send(res, 200, await issue(await userOf(claims.sub), claims.session_id));
      }
    }
    // ---------------------------------------------------------------- data
    const m = /^\/rest\/v1\/rpc\/([a-z_][a-z0-9_]*)$/.exec(path);
    if (m && req.method === 'POST') {
      if (bearer && !claims) return send(res, 401, { code: 'PGRST301', message: 'JWT expired', details: null, hint: null });
      const role = claims ? 'authenticated' : 'anon', ty = await argTypes(m[1]);
      if (!ty) return send(res, 404, { code: 'PGRST202', message: 'Could not find the function public.' + m[1] + ' in the schema cache', details: null, hint: null });
      const names = Object.keys(j), args = [], vals = [];
      for (const n of names) {
        const t = ty.find(x => x[0] === n); if (!t) return send(res, 404, { code: 'PGRST202', message: 'Could not find the function public.' + m[1] + '(' + names.join(', ') + ') in the schema cache', details: null, hint: null });
        const v = j[n]; vals.push(v === null ? null : t[1].endsWith('[]') && Array.isArray(v) ? v : typeof v === 'object' || t[1] === 'jsonb' || t[1] === 'json' ? JSON.stringify(v) : v);
        args.push(n + ' => $' + vals.length + '::' + t[1]);
      }
      const c = await db.connect();
      try {
        await c.query('begin'); await c.query("select set_config('request.jwt.claims', $1, true)", [JSON.stringify(claims || { role: 'anon' })]); await c.query('set local role ' + role);
        const r = await c.query('select public.' + m[1] + '(' + args.join(', ') + ') as r', vals); await c.query('commit'); return send(res, 200, r.rows[0].r);
      } catch (e) {
        await c.query('rollback').catch(() => {});
        if (e.code === '42883') { ARGS.delete(m[1]); return send(res, 404, { code: 'PGRST202', message: 'Could not find the function public.' + m[1] + ' in the schema cache', details: null, hint: null }); } // (as PostgREST after its schema cache reloads)
        const code = e.code === '42501' ? (claims ? 403 : 401) : e.code === '28000' ? 403 : e.code === 'P0001' ? 400 : 400;
        return send(res, code, { code: e.code, message: e.message, details: null, hint: null });
      } finally { c.release(); }
    }
    send(res, 404, { message: 'not here: ' + req.method + ' ' + path });
  } catch (e) { send(res, 500, { message: String(e.message || e) }); }
}).listen(PORT, '127.0.0.1', () => console.log('supabase stand-in on', PORT));
