// Notifications while the game is closed (v391): the APNs sender with a made-up key against a stand-in for Apple's push
// service (HTTP/2 on this machine), the settings, and the game server sending one when a friend whose game isn't open is
// invited to a party. Nothing here reaches Apple or Supabase.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import http2 from 'node:http2';
import crypto, { randomUUID } from 'node:crypto';
import { RMNet } from '../client/rmnet.js';
import { Apns, Pusher, pushFromEnv } from '../src/push.js';
import { createLogger } from '../src/log.js';
import { startServer, until } from './helpers/harness.js';

// a made-up key, as Apple's .p8 files are (an EC P-256 key in PKCS #8 PEM)
const { privateKey, publicKey } = crypto.generateKeyPairSync('ec', { namedCurve: 'P-256' });
const P8 = privateKey.export({ type: 'pkcs8', format: 'pem' });
const KEY = { keyId: 'TESTKEY123', teamId: 'TESTTEAM45', key: P8, bundleId: 'com.example.rollmodel', production: false };
const tok = n => n.toString(16).padStart(2, '0').repeat(32);

// a stand-in for Apple's service: checks the provider token, records what came, answers as told
async function fakeApns(answer = () => [200, '']) {
  const got = [], srv = http2.createServer();
  srv.on('stream', (st, h) => {
    let body = ''; st.setEncoding('utf8'); st.on('data', d => { body += d; });
    st.on('end', () => {
      const jwt = String(h.authorization || '').replace(/^bearer /, ''), [a, b, c] = jwt.split('.');
      const ok = !!c && crypto.verify('sha256', Buffer.from(a + '.' + b), { key: publicKey, dsaEncoding: 'ieee-p1363' }, Buffer.from(c, 'base64url'));
      const rec = { path: h[':path'], method: h[':method'], h, jwt, head: a && JSON.parse(Buffer.from(a, 'base64url')), claims: b && JSON.parse(Buffer.from(b, 'base64url')), signed: ok, body: body ? JSON.parse(body) : null };
      got.push(rec); const [status, reason] = ok ? answer(rec) : [403, 'InvalidProviderToken'];
      st.respond({ ':status': status, 'content-type': 'application/json' }); st.end(reason ? JSON.stringify({ reason }) : '');
    });
  });
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  return { got, origin: 'http://127.0.0.1:' + srv.address().port, close: () => new Promise(r => srv.close(r)) };
}
// a stand-in for Supabase's rm_invite_push
async function fakeSb(answer) {
  const got = [], srv = http.createServer((req, res) => { let b = ''; req.on('data', d => { b += d; }); req.on('end', () => {
    got.push({ url: req.url, h: req.headers, body: b ? JSON.parse(b) : null }); const [st, j] = answer(got[got.length - 1]);
    res.writeHead(st, { 'content-type': 'application/json' }); res.end(JSON.stringify(j)); }); });
  await new Promise(r => srv.listen(0, '127.0.0.1', r));
  return { got, url: 'http://127.0.0.1:' + srv.address().port, close: () => new Promise(r => srv.close(r)) };
}
const logs = () => { const recs = []; return { recs, log: createLogger({ level: 'debug', sink: r => recs.push(r) }) }; };

test('the settings come from the environment only; without a key, nothing is sent and the log says so once', async () => {
  const none = pushFromEnv({});
  assert.equal(none.apns, null); assert.deepEqual(none.missing, ['APNS_KEY_ID', 'APNS_TEAM_ID', 'APNS_KEY_P8', 'APNS_BUNDLE_ID']);
  assert.match(none.sb.url, /^https:\/\//); assert.ok(none.sb.key, 'the game\'s own project by default');
  const env = { APNS_KEY_ID: ' TESTKEY123 ', APNS_TEAM_ID: 'TESTTEAM45', APNS_KEY_P8: P8.replace(/\n/g, '\\n'), APNS_BUNDLE_ID: 'com.example.rollmodel', APNS_PRODUCTION: '1', SUPABASE_URL: 'http://127.0.0.1:9/', SUPABASE_KEY: 'k' };
  const c = pushFromEnv(env);
  assert.equal(c.apns.keyId, 'TESTKEY123'); assert.equal(c.apns.production, true); assert.equal(c.apns.key, P8.trim(), 'a key pasted on one line gets its line breaks back');
  assert.deepEqual(c.sb, { url: 'http://127.0.0.1:9', key: 'k' });
  assert.equal(pushFromEnv(Object.assign({}, env, { APNS_PRODUCTION: '0' })).apns.production, false);
  const { recs, log } = logs(), p = new Pusher(none, { log, fetch: () => { throw new Error('must not ask Supabase'); } });
  p.announce(); assert.equal(await p.invite(randomUUID(), 'token'), 0); assert.equal(await p.invite(randomUUID(), 'token'), 0);
  assert.equal(recs.length, 1); assert.match(recs[0].msg, /no APNs key/); assert.deepEqual(recs[0].missing, none.missing);
  // a key that isn't one: refused at start, with one line in the log
  const bad = logs(), q = new Pusher(pushFromEnv(Object.assign({}, env, { APNS_KEY_P8: 'not a key' })), { log: bad.log });
  assert.equal(q.on, false); q.announce(); assert.equal(bad.recs.length, 1); assert.match(bad.recs[0].msg, /not a usable key/);
});

test('APNs: a signed provider token, the right service for each phone, the headers Apple wants', async () => {
  const sand = await fakeApns(), prod = await fakeApns();
  let t = Date.parse('2026-10-20T12:00:00Z');
  const a = new Apns(Object.assign({}, KEY, { origins: { development: sand.origin, production: prod.origin }, now: () => t }));
  try {
    const payload = { aps: { alert: { title: 'Party invite', body: '@ama invited you to their party' } }, rm: { k: 'invite', id: 'x' } };
    assert.deepEqual(await a.send(tok(1), payload, 'development', { expiration: 1790000000, collapseId: 'abc' }), { status: 200, reason: '' });
    assert.deepEqual(await a.send(tok(2), payload, 'production'), { status: 200, reason: '' });
    assert.deepEqual(await a.send(tok(3), payload), { status: 200, reason: '' }, 'no env: the sandbox unless APNS_PRODUCTION');
    assert.equal(sand.got.length, 2); assert.equal(prod.got.length, 1);
    const r = sand.got[0];
    assert.equal(r.signed, true); assert.deepEqual(r.head, { alg: 'ES256', kid: 'TESTKEY123' }); assert.deepEqual(r.claims, { iss: 'TESTTEAM45', iat: t / 1000 });
    assert.equal(r.method, 'POST'); assert.equal(r.path, '/3/device/' + tok(1));
    assert.equal(r.h['apns-topic'], 'com.example.rollmodel'); assert.equal(r.h['apns-push-type'], 'alert'); assert.equal(r.h['apns-priority'], '10');
    assert.equal(r.h['apns-expiration'], '1790000000'); assert.equal(r.h['apns-collapse-id'], 'abc'); assert.deepEqual(r.body, payload);
    assert.equal(prod.got[0].path, '/3/device/' + tok(2));
    // the same provider token for 40 minutes, then a new one
    assert.equal(sand.got[1].jwt, r.jwt);
    t += 41 * 60 * 1000; await a.send(tok(1), payload, 'development');
    assert.notEqual(sand.got[2].jwt, r.jwt); assert.equal(sand.got[2].claims.iat, t / 1000);
    // not a token: never sent
    assert.deepEqual(await a.send('../../etc', payload, 'development'), { status: 0, reason: 'BadDeviceToken' }); assert.equal(sand.got.length, 3);
  } finally { a.close(); await sand.close(); await prod.close(); }
});

test('APNs: an expired provider token is made again once; a phone that is gone is reported', async () => {
  let first = true;
  const f = await fakeApns(rec => rec.path.endsWith(tok(9)) ? [410, 'Unregistered'] : first ? (first = false, [403, 'ExpiredProviderToken']) : [200, '']);
  const a = new Apns(Object.assign({}, KEY, { origins: { development: f.origin, production: f.origin } }));
  try {
    assert.equal((await a.send(tok(1), { aps: {} }, 'development')).status, 200);
    assert.equal(f.got.length, 2, 'tried again with a new token'); assert.notEqual(f.got[0].jwt, f.got[1].jwt);
    assert.deepEqual(await a.send(tok(9), { aps: {} }, 'development'), { status: 410, reason: 'Unregistered' });
  } finally { a.close(); await f.close(); }
});

test('an invite\'s notification: asked of Supabase as the inviter, then one to each of the friend\'s phones', async () => {
  const f = await fakeApns(rec => rec.path.endsWith(tok(7)) ? [410, 'Unregistered'] : [200, '']);
  const inv = randomUUID(), exp = new Date(Date.now() + 110000).toISOString();
  let once = false; // (as the database does it: once per invite)
  const sb = await fakeSb(rec => rec.body.p_id === inv && !once ? (once = true, [200, { ok: true, id: inv, to: randomUUID(), from: 'Ama_Blob', expires: exp, tokens: [{ t: tok(5), env: 'development' }, { t: tok(6), env: 'production' }, { t: tok(7), env: 'production' }] }]) : [200, { ok: false, why: 'sent' }]);
  const { recs, log } = logs();
  const p = new Pusher({ apns: KEY, sb: { url: sb.url, key: 'test-publishable-key' }, missing: [] }, { log, origins: { development: f.origin, production: f.origin } });
  try {
    assert.equal(await p.invite(inv, 'the-inviters-token'), 2, 'two phones took it; one was gone');
    assert.equal(sb.got.length, 1); assert.equal(sb.got[0].url, '/rest/v1/rpc/rm_invite_push'); assert.deepEqual(sb.got[0].body, { p_id: inv });
    assert.equal(sb.got[0].h.apikey, 'test-publishable-key'); assert.equal(sb.got[0].h.authorization, 'Bearer the-inviters-token');
    assert.equal(f.got.length, 3);
    const n = f.got[0].body; assert.equal(n.aps.alert.body, '@ama_blob invited you to their party. Tap to join!'); assert.equal(n.aps.sound, 'default'); assert.deepEqual(n.rm, { k: 'invite', id: inv });
    assert.equal(f.got[0].h['apns-collapse-id'], inv); assert.equal(f.got[0].h['apns-expiration'], String(Math.floor(Date.parse(exp) / 1000)));
    assert.ok(recs.some(r => r.reason === 'Unregistered'));
    // the second time (or any refusal from the database): nothing goes out
    assert.equal(await p.invite(inv, 'the-inviters-token'), 0); assert.equal(f.got.length, 3);
    // not an invite id, or no token: Supabase isn't even asked
    assert.equal(await p.invite('nope', 'x'), 0); assert.equal(await p.invite(randomUUID(), ''), 0); assert.equal(sb.got.length, 2);
  } finally { p.close(); await f.close(); await sb.close(); }
});

test('the game server: a friend whose game is closed gets a notification; one in the game gets the nudge instead', async () => {
  const f = await fakeApns(); let asked = 0;
  const sb = await fakeSb(rec => { asked++; return [200, { ok: true, id: rec.body.p_id, to: 'x', from: 'Pal1', expires: new Date(Date.now() + 120000).toISOString(), tokens: [{ t: tok(4), env: 'development' }] }]; });
  const pusher = new Pusher({ apns: KEY, sb: { url: sb.url, key: 'k' }, missing: [] }, { origins: { development: f.origin, production: f.origin } });
  const srv = await startServer({}, { pusher });
  const mk = (name, sbId) => new RMNet({ url: srv.url, name, look: { c: 'red', e: 'round', r: 3 }, sb: sbId, autoReconnect: false });
  const away = randomUUID(), A = mk('Pal1', randomUUID()), B = mk('Pal2', randomUUID());
  try {
    await A.connect(); await B.connect(); await A.partyCreate();
    // B is in the game: the nudge, no notification
    const poked = new Promise(r => B.on('poke', r));
    await A.partyInvite(B.sb, { name: 'Pal2', inv: randomUUID(), sbt: 'eyJ.' + 'x'.repeat(1400) + '.sig' }); await poked;
    // (a long Supabase token fits: an invite may be bigger than other messages)
    await A.partyInvite(away, { name: 'Pal3', inv: randomUUID(), sbt: 'eyJ.' + 'x'.repeat(1400) + '.sig' });
    await until(() => f.got.length === 1, 5000);
    assert.equal(asked, 1, 'only for the friend who is away'); assert.equal(f.got[0].path, '/3/device/' + tok(4)); assert.equal(f.got[0].body.rm.k, 'invite');
    // an invite without what a notification needs (an older game): the party has it, no notification
    await A.partyInvite(randomUUID(), { name: 'Pal4' }); await new Promise(r => setTimeout(r, 200)); assert.equal(asked, 1);
    assert.equal(A.party.invites.length, 3);
  } finally { A.close(); B.close(); await srv.close(); await f.close(); await sb.close(); }
});
