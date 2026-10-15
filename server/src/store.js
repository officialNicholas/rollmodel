// Persistence behind a small interface, so a real database can replace the JSON file later.
// Players are found by a hash of their device token: the file never holds a usable token.
//
// Interface (all async):
//   init()                         load
//   create({ name, look })        -> { player, token }   new anonymous player with a fresh device token
//   getByToken(token)             -> player | null
//   get(id)                       -> player | null
//   update(id, patch)             -> player             shallow merge
//   recordMatch(summary)                                 keeps the most recent matches
//   flag(id, reason, details)                            anti-cheat and abuse notes
//   flush(), close()
import { promises as fsp } from 'node:fs';
import path from 'node:path';
import { randomId, newToken, tokenKey } from './util.js';
import { DEFAULT_RATING } from './rating.js';
import { MODES } from './constants.js';

const MAX_MATCHES = 2000, MAX_FLAGS = 50;
const freshRatings = () => Object.fromEntries(MODES.map(m => [m, { ...DEFAULT_RATING }]));

export class MemoryStore {
  constructor() { this.players = new Map(); this.byToken = new Map(); this.matches = []; }
  async init() {}
  async create({ name, look = null }) {
    const token = newToken(), now = Date.now();
    const player = { id: randomId('p_', 12), tokenKey: tokenKey(token), name, look, createdAt: now, lastSeen: now, ratings: freshRatings(), stats: { matches: 0, wins: 0, kos: 0 }, flags: [], banned: false };
    this.players.set(player.id, player); this.byToken.set(player.tokenKey, player.id); this._dirty();
    return { player: clone(player), token };
  }
  async getByToken(token) {
    if (typeof token !== 'string' || token.length < 16 || token.length > 128) return null;
    const id = this.byToken.get(tokenKey(token)); return id ? clone(this.players.get(id)) : null;
  }
  async get(id) { const p = this.players.get(id); return p ? clone(p) : null; }
  async update(id, patch) {
    const p = this.players.get(id); if (!p) return null;
    for (const k of Object.keys(patch)) if (k !== 'id' && k !== 'tokenKey') p[k] = clone(patch[k]);
    this._dirty(); return clone(p);
  }
  async recordMatch(summary) { this.matches.push(clone(summary)); if (this.matches.length > MAX_MATCHES) this.matches.splice(0, this.matches.length - MAX_MATCHES); this._dirty(); }
  async flag(id, reason, details = {}) {
    const p = this.players.get(id); if (!p) return;
    p.flags.push({ at: Date.now(), reason, details: clone(details) }); if (p.flags.length > MAX_FLAGS) p.flags.splice(0, p.flags.length - MAX_FLAGS);
    this._dirty();
  }
  async flush() {}
  async close() { await this.flush(); }
  _dirty() {}
}

export class JsonFileStore extends MemoryStore {
  constructor(file, { delayMs = 500 } = {}) { super(); this.file = path.resolve(file); this.delayMs = delayMs; this._timer = null; this._writing = null; this._again = false; }
  async init() {
    let raw = null;
    try { raw = await fsp.readFile(this.file, 'utf8'); } catch (e) { if (e.code !== 'ENOENT') throw e; }
    if (raw) {
      const data = JSON.parse(raw);
      for (const p of data.players || []) { if (!p.ratings) p.ratings = freshRatings(); for (const m of MODES) if (!p.ratings[m]) p.ratings[m] = { ...DEFAULT_RATING }; this.players.set(p.id, p); this.byToken.set(p.tokenKey, p.id); }
      this.matches = data.matches || [];
    }
    await fsp.mkdir(path.dirname(this.file), { recursive: true });
  }
  _dirty() { if (!this._timer) this._timer = setTimeout(() => { this._timer = null; this._write(); }, this.delayMs); }
  async _write() {
    if (this._writing) { this._again = true; return this._writing; }
    const body = JSON.stringify({ version: 1, savedAt: new Date().toISOString(), players: [...this.players.values()], matches: this.matches });
    const tmp = this.file + '.' + process.pid + '.tmp';
    this._writing = (async () => { await fsp.writeFile(tmp, body); await fsp.rename(tmp, this.file); })()
      .finally(() => { this._writing = null; if (this._again) { this._again = false; this._write(); } });
    return this._writing;
  }
  async flush() {
    if (this._timer) { clearTimeout(this._timer); this._timer = null; }
    while (this._writing) await this._writing;
    await this._write();
    while (this._writing) await this._writing;
  }
}

function clone(v) { return v === undefined ? undefined : JSON.parse(JSON.stringify(v)); }
