// Notifications while the game is closed (v391): a party invite reaches a friend's iPhone through Apple's push service
// (APNs, token-based, HTTP/2). The game server sends it when the friend's game isn't connected:
//   1. the inviting game made the invite in Supabase (rm_invite) and tells this server about it (partyInvite, with the
//      invite's id and the inviter's own Supabase access token);
//   2. this server asks Supabase, as the inviter, for that invite's notification (rm_invite_push: once per invite, only
//      between friends, with the sender's username and the friend's phones);
//   3. and posts one notification to each phone.
// Its settings are environment variables, and the key is never anywhere else: APNS_KEY_ID, APNS_TEAM_ID, APNS_KEY_P8
// (the .p8 key itself, its PEM text), APNS_BUNDLE_ID, APNS_PRODUCTION (1: tokens that don't say which service they
// belong to go to Apple's production service, else to its sandbox), and the game's Supabase project (SUPABASE_URL,
// SUPABASE_KEY: its publishable key, the one in the game; both default to the game's). With no key it sends nothing,
// and says so once in the log.
import http2 from 'node:http2';
import crypto from 'node:crypto';

const GAME_SB = { url: 'https://nbemerxgukwwtrfgirfl.supabase.co', key: 'sb_publishable_9fux5IpOiTei0HvScvqI1g_iAwSCHPc' }; // (public: the game has them)
export const APNS_ORIGINS = Object.freeze({ production: 'https://api.push.apple.com', development: 'https://api.sandbox.push.apple.com' });
const TOKEN_RE = /^[0-9a-f]{64,200}$/, UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const JWT_LIFE_MS = 40 * 60 * 1000; // (Apple takes a provider token for an hour, and wants it renewed no more than every 20 minutes)

// the settings from the environment: { apns: {...} | null, sb: { url, key }, missing: [names] }
export function pushFromEnv(env = process.env) {
  const need = ['APNS_KEY_ID', 'APNS_TEAM_ID', 'APNS_KEY_P8', 'APNS_BUNDLE_ID'], missing = need.filter(k => !String(env[k] || '').trim());
  const sb = { url: String(env.SUPABASE_URL || GAME_SB.url).replace(/\/+$/, ''), key: String(env.SUPABASE_KEY || GAME_SB.key) };
  if (missing.length) return { apns: null, sb, missing };
  // (a key pasted into a one-line secret may come with its line breaks as \n)
  const key = String(env.APNS_KEY_P8).replace(/\\n/g, '\n').trim();
  return { apns: { keyId: String(env.APNS_KEY_ID).trim(), teamId: String(env.APNS_TEAM_ID).trim(), key, bundleId: String(env.APNS_BUNDLE_ID).trim(), production: /^(1|true|yes)$/i.test(String(env.APNS_PRODUCTION || '')) }, sb, missing: [] };
}

const b64u = b => Buffer.from(b).toString('base64url');

// One connection per Apple service, kept open (Apple asks for that), and the provider token renewed every 40 minutes.
// opts: { keyId, teamId, key (PEM), bundleId, production, origins (for tests), now (for tests), log }
export class Apns {
  constructor(opts) {
    this.o = opts; this.origins = Object.assign({}, APNS_ORIGINS, opts.origins || {}); this.now = opts.now || Date.now; this.log = opts.log;
    this.key = crypto.createPrivateKey(opts.key); // (throws now, at start, for a key that isn't one)
    this.sessions = new Map(); this.jwt = null; this.jwtAt = 0;
  }
  // the provider token: an ES256 JWT with the key id and the team id, signed with the .p8 key
  token(fresh) {
    const t = this.now();
    if (!fresh && this.jwt && t - this.jwtAt < JWT_LIFE_MS) return this.jwt;
    const head = b64u(JSON.stringify({ alg: 'ES256', kid: this.o.keyId })), body = b64u(JSON.stringify({ iss: this.o.teamId, iat: Math.floor(t / 1000) }));
    const sig = crypto.sign('sha256', Buffer.from(head + '.' + body), { key: this.key, dsaEncoding: 'ieee-p1363' });
    this.jwt = head + '.' + body + '.' + b64u(sig); this.jwtAt = t; return this.jwt;
  }
  _session(origin) {
    let s = this.sessions.get(origin);
    if (s && !s.closed && !s.destroyed) return s;
    s = http2.connect(origin); this.sessions.set(origin, s);
    const drop = () => { if (this.sessions.get(origin) === s) this.sessions.delete(origin); };
    s.on('error', e => { drop(); if (this.log) this.log.warn('push: connection to Apple failed', { err: e.code || e.message }); });
    s.on('goaway', drop); s.on('close', drop);
    s.setTimeout(5 * 60 * 1000, () => s.close()); // (idle for five minutes: let it go; the next one connects again)
    return s;
  }
  // one notification to one phone. env: 'production' | 'development' (an app run from Xcode); opts: { expiration (s),
  // collapseId }. Resolves { status, reason } (200: Apple has it)
  async send(device, payload, env, opts = {}) {
    if (!TOKEN_RE.test(device)) return { status: 0, reason: 'BadDeviceToken' };
    const which = env === 'development' || env === 'production' ? env : this.o.production ? 'production' : 'development';
    let r = await this._post(this.origins[which], device, payload, opts, false);
    if (r.status === 403 && r.reason === 'ExpiredProviderToken') r = await this._post(this.origins[which], device, payload, opts, true);
    return r;
  }
  _post(origin, device, payload, opts, fresh) {
    return new Promise(resolve => {
      let s; try { s = this._session(origin); } catch (e) { return resolve({ status: 0, reason: e.code || e.message }); }
      const headers = { ':method': 'POST', ':path': '/3/device/' + device, authorization: 'bearer ' + this.token(fresh), 'apns-topic': this.o.bundleId,
        'apns-push-type': 'alert', 'apns-priority': '10', 'content-type': 'application/json' };
      if (opts.expiration) headers['apns-expiration'] = String(Math.max(0, Math.floor(opts.expiration)));
      if (opts.collapseId) headers['apns-collapse-id'] = String(opts.collapseId).slice(0, 64);
      let req; try { req = s.request(headers); } catch (e) { return resolve({ status: 0, reason: e.code || e.message }); }
      let status = 0, body = ''; const t = setTimeout(() => { req.close(http2.constants.NGHTTP2_CANCEL); resolve({ status: 0, reason: 'timeout' }); }, 10000);
      req.on('response', h => { status = h[':status'] | 0; }); req.setEncoding('utf8'); req.on('data', d => { if (body.length < 4096) body += d; });
      req.on('end', () => { clearTimeout(t); let reason = ''; try { reason = body ? JSON.parse(body).reason || '' : ''; } catch (e) {} resolve({ status, reason }); });
      req.on('error', e => { clearTimeout(t); resolve({ status: 0, reason: e.code || e.message }); });
      req.end(JSON.stringify(payload));
    });
  }
  close() { for (const s of this.sessions.values()) try { s.close(); } catch (e) {} this.sessions.clear(); }
}

// What the game server calls. cfg: pushFromEnv's; opts: { log, fetch, origins, now } (the last three for tests)
export class Pusher {
  constructor(cfg, opts = {}) {
    this.log = opts.log; this.sb = (cfg && cfg.sb) || pushFromEnv({}).sb; this.fetch = opts.fetch || globalThis.fetch; this.told = false; this.apns = null;
    this.missing = (cfg && cfg.missing) || ['APNS_KEY_ID', 'APNS_TEAM_ID', 'APNS_KEY_P8', 'APNS_BUNDLE_ID'];
    this.stats = { asked: 0, sent: 0, failed: 0 };
    if (cfg && cfg.apns) {
      try { this.apns = new Apns(Object.assign({ log: opts.log, origins: opts.origins, now: opts.now }, cfg.apns)); }
      catch (e) { this.missing = ['APNS_KEY_P8']; if (this.log) this.log.error('push: APNS_KEY_P8 is not a usable key, so no notifications are sent', { err: e.message }); this.told = true; }
    }
  }
  get on() { return !!this.apns; }
  // (once, when the server starts) whether notifications are on, and if not, what's missing
  announce() {
    if (this.told || !this.log) return; this.told = true;
    if (this.apns) this.log.info('push: notifications on', { service: this.apns.o.production ? 'production' : 'sandbox', topic: this.apns.o.bundleId });
    else this.log.info('push: no APNs key set, so party invites reach only games that are open', { missing: this.missing });
  }
  // a party invite to a friend whose game isn't open. inv: the invite's id (from rm_invite); sbt: the inviter's Supabase
  // access token. Resolves with how many phones Apple took it for (never rejects)
  invite(inv, sbt) {
    return this._invite(inv, sbt).catch(e => { if (this.log) this.log.warn('push: invite failed', { err: e && e.message }); return 0; });
  }
  async _invite(inv, sbt) {
    if (!this.apns) { this.announce(); return 0; }
    if (typeof inv !== 'string' || !UUID.test(inv) || typeof sbt !== 'string' || !sbt || sbt.length > 4096) return 0;
    this.stats.asked++;
    let r = null;
    try {
      const ctl = new AbortController(), t = setTimeout(() => ctl.abort(), 8000);
      try {
        const res = await this.fetch(this.sb.url + '/rest/v1/rpc/rm_invite_push', { method: 'POST', signal: ctl.signal,
          headers: { apikey: this.sb.key, authorization: 'Bearer ' + sbt, 'content-type': 'application/json' }, body: JSON.stringify({ p_id: inv }) });
        if (!res.ok) { if (this.log) this.log.warn('push: Supabase turned the invite down', { status: res.status }); return 0; }
        r = await res.json();
      } finally { clearTimeout(t); }
    } catch (e) { if (this.log) this.log.warn('push: could not reach Supabase', { err: e.name === 'AbortError' ? 'timeout' : e.message }); return 0; }
    if (!r || !r.ok || !Array.isArray(r.tokens) || !r.tokens.length) return 0;
    const who = '@' + String(r.from || 'a friend').toLowerCase().replace(/^@/, '').slice(0, 16);
    const payload = { aps: { alert: { title: 'Party invite', body: who + ' invited you to their party. Tap to join!' }, sound: 'default', 'thread-id': 'party' }, rm: { k: 'invite', id: inv } };
    const exp = Date.parse(r.expires); let n = 0;
    for (const x of r.tokens.slice(0, 5)) {
      const out = await this.apns.send(String(x && x.t || ''), payload, x && x.env, { expiration: Number.isFinite(exp) ? exp / 1000 : 0, collapseId: inv });
      if (out.status === 200) { n++; this.stats.sent++; }
      else { this.stats.failed++; if (this.log) this.log.warn('push: Apple refused a notification', { status: out.status, reason: out.reason }); }
    }
    return n;
  }
  close() { if (this.apns) this.apns.close(); }
}
