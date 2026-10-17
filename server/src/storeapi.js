// The shared player store for a server spread over several machines. One machine keeps the store (its file, as a single
// machine always has); the others reach it through this small API on Fly's private network, so any machine can sign in
// any player and save their results.
//
// The API listens on its own port (INTERNAL_PORT, never in fly.toml's public service) and needs INTERNAL_KEY in a
// header: POST /internal/store { op, args } -> { ok: true, v } | { ok: false, error }.
import http from 'node:http';
import { timingSafeEqual } from 'node:crypto';

export const STORE_OPS = new Set(['create', 'getByToken', 'get', 'update', 'recordMatch', 'flag', 'claimRoom', 'findRoom', 'releaseRoom']);
const MAX_BODY = 256 * 1024;
const same = (a, b) => { const x = Buffer.from(String(a)), y = Buffer.from(String(b)); return x.length === y.length && timingSafeEqual(x, y); };

export function startStoreApi({ store, key, port, host = '::', log }) {
  const srv = http.createServer((req, res) => {
    const reply = (code, obj) => { const b = JSON.stringify(obj); res.writeHead(code, { 'content-type': 'application/json' }); res.end(b); };
    if (req.method !== 'POST' || req.url !== '/internal/store') return reply(404, { ok: false, error: 'not_found' });
    if (!key || !same(req.headers['x-rm-internal'] || '', key)) return reply(403, { ok: false, error: 'forbidden' });
    let body = '', big = false;
    req.on('data', d => { if (big) return; body += d; if (body.length > MAX_BODY) { big = true; reply(413, { ok: false, error: 'too_large' }); req.destroy(); } });
    req.on('end', async () => {
      if (big) return;
      let m; try { m = JSON.parse(body); } catch (e) { return reply(400, { ok: false, error: 'bad_json' }); }
      if (!m || !STORE_OPS.has(m.op) || !Array.isArray(m.args)) return reply(400, { ok: false, error: 'bad_op' });
      try { reply(200, { ok: true, v: await store[m.op](...m.args) }); } catch (e) { log.error('store op failed', { op: m.op, err: e.message }); reply(500, { ok: false, error: 'store' }); }
    });
  });
  srv.keepAliveTimeout = 65000;
  return new Promise((resolve, reject) => { srv.once('error', reject); srv.listen(port, host, () => { srv.off('error', reject); resolve(srv); }); });
}
