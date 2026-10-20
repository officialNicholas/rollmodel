// A game machine's view of the shared store (src/storeapi.js) on the store machine: the same interface as the store
// itself (all async), over Fly's private network. Reads and updates are retried a couple of times; a store that cannot
// be reached makes the call fail, and the server tells the player to try again (their phone reconnects by itself).
const RETRY = new Set(['getByToken', 'get', 'update', 'flag', 'findRoom', 'releaseRoom']);

export class RemoteStore {
  constructor(url, key, { timeoutMs = 4000, tries = 3 } = {}) { this.url = url.replace(/\/$/, '') + '/internal/store'; this.key = key; this.timeoutMs = timeoutMs; this.tries = tries; }
  async init() {}
  async _call(op, args) {
    let last;
    for (let i = 0; i < (RETRY.has(op) ? this.tries : 1); i++) {
      try {
        const r = await fetch(this.url, { method: 'POST', headers: { 'content-type': 'application/json', 'x-rm-internal': this.key }, body: JSON.stringify({ op, args }), signal: AbortSignal.timeout(this.timeoutMs) });
        const j = await r.json();
        if (j.ok) return j.v;
        last = new Error('store: ' + j.error); if (r.status < 500) break;
      } catch (e) { last = e; }
      await new Promise(res => setTimeout(res, 100 * (i + 1)));
    }
    throw last;
  }
  create(o) { return this._call('create', [o]); }
  getByToken(t) { return this._call('getByToken', [t]); }
  get(id) { return this._call('get', [id]); }
  update(id, patch) { return this._call('update', [id, patch]); }
  recordMatch(s) { return this._call('recordMatch', [s]); }
  flag(id, reason, details) { return this._call('flag', [id, reason, details]); }
  claimRoom(code, shard) { return this._call('claimRoom', [code, shard]); }
  findRoom(code) { return this._call('findRoom', [code]); }
  releaseRoom(code, shard) { return this._call('releaseRoom', [code, shard]); }
  async flush() {}
  async close() {}
}
