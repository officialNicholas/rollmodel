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

// On disk: a snapshot (the file: every player and recent match, as before) plus a journal beside it (file + '.log': one
// JSON line per change since the snapshot: a player's whole record, or a match). A change costs one short line, not a
// rewrite of everyone: building the whole file takes the main thread about 30 ms at 10,000 players and 180 ms at 50,000,
// which would freeze every match each time. When the journal outgrows the snapshot (or 64 MB), the snapshot is written
// again a few hundred players at a time between other work, and the journal starts over. Loading reads the snapshot and
// replays the journal (a player's last line wins; a match already in the snapshot is not added twice).
export class JsonFileStore extends MemoryStore {
  constructor(file, { delayMs = 500, chunk = 500, compactBytes = 64 * 1024 * 1024 } = {}) {
    super(); this.file = path.resolve(file); this.log = this.file + '.log'; this.delayMs = delayMs; this.chunk = chunk; this.compactBytes = compactBytes;
    this._timer = null; this._changed = new Set(); this._newMatches = []; this._writing = null; this._logBytes = 0; this._snapBytes = 0; this._compacting = null;
  }
  async init() {
    let raw = null;
    try { raw = await fsp.readFile(this.file, 'utf8'); } catch (e) { if (e.code !== 'ENOENT') throw e; }
    const seen = new Set();
    const add = p => { if (!p.ratings) p.ratings = freshRatings(); for (const m of MODES) if (!p.ratings[m]) p.ratings[m] = { ...DEFAULT_RATING }; this.players.set(p.id, p); this.byToken.set(p.tokenKey, p.id); };
    if (raw) { const data = JSON.parse(raw); for (const p of data.players || []) add(p); this.matches = data.matches || []; for (const m of this.matches) if (m.matchId) seen.add(m.matchId); this._snapBytes = raw.length; }
    let lines = null;
    try { lines = await fsp.readFile(this.log, 'utf8'); } catch (e) { if (e.code !== 'ENOENT') throw e; }
    if (lines) {
      this._logBytes = lines.length;
      for (const l of lines.split('\n')) {
        if (!l) continue; let r; try { r = JSON.parse(l); } catch (e) { continue; } // (a line cut short by a crash)
        if (r.p) add(r.p); else if (r.m && !(r.m.matchId && seen.has(r.m.matchId))) { this.matches.push(r.m); if (r.m.matchId) seen.add(r.m.matchId); }
      }
      if (this.matches.length > MAX_MATCHES) this.matches.splice(0, this.matches.length - MAX_MATCHES);
    }
    await fsp.mkdir(path.dirname(this.file), { recursive: true });
  }
  async create(o) { const r = await super.create(o); this._changed.add(r.player.id); this._soon(); return r; }
  async update(id, patch) { const r = await super.update(id, patch); if (r) { this._changed.add(id); this._soon(); } return r; }
  async flag(id, reason, details) { await super.flag(id, reason, details); this._changed.add(id); this._soon(); }
  async recordMatch(summary) { await super.recordMatch(summary); this._newMatches.push(this.matches[this.matches.length - 1]); this._soon(); }
  _soon() { if (!this._timer) this._timer = setTimeout(() => { this._timer = null; this._append(); }, this.delayMs); }
  // the changes since the last append, as journal lines
  _append() {
    if (this._writing) { this._soon(); return this._writing; }
    if (!this._changed.size && !this._newMatches.length) return null;
    let body = '';
    for (const id of this._changed) { const p = this.players.get(id); if (p) body += JSON.stringify({ p }) + '\n'; }
    for (const m of this._newMatches) body += JSON.stringify({ m }) + '\n';
    this._changed.clear(); this._newMatches = [];
    this._logBytes += body.length;
    this._writing = fsp.appendFile(this.log, body).finally(() => {
      this._writing = null;
      if (!this._compacting && this._logBytes > Math.max(this.compactBytes, this._snapBytes)) this._compacting = this._compact().catch(() => {}).finally(() => { this._compacting = null; });
    });
    return this._writing;
  }
  // the snapshot again, a few hundred players at a time, then a fresh journal. Changes made meanwhile go to the new journal
  // (started first) and may also be in the snapshot: replaying them again is harmless.
  async _compact() {
    while (this._writing) await this._writing;
    const old = this.log + '.' + process.pid + '.old', tmp = this.file + '.' + process.pid + '.tmp';
    try { await fsp.rename(this.log, old); } catch (e) { if (e.code !== 'ENOENT') throw e; }
    this._logBytes = 0;
    const fh = await fsp.open(tmp, 'w'); let size = 0;
    try {
      const w = async str => { size += str.length; await fh.write(str); };
      await w('{"version":1,"savedAt":' + JSON.stringify(new Date().toISOString()) + ',"players":[');
      const ids = [...this.players.keys()];
      for (let i = 0; i < ids.length; i += this.chunk) {
        let part = '';
        for (let j = i; j < Math.min(ids.length, i + this.chunk); j++) { const p = this.players.get(ids[j]); if (p) part += (part || i ? ',' : '') + JSON.stringify(p); }
        await w(part); await new Promise(r => setImmediate(r)); // (other work between chunks)
      }
      await w('],"matches":' + JSON.stringify(this.matches) + '}');
    } finally { await fh.close(); }
    await fsp.rename(tmp, this.file); this._snapBytes = size;
    await fsp.rm(old, { force: true });
  }
  // everything changed so far is on disk (in the journal)
  async flush() {
    if (this._timer) { clearTimeout(this._timer); this._timer = null; }
    while (this._writing || this._compacting) await (this._writing || this._compacting);
    await this._append();
    while (this._writing) await this._writing;
  }
  // shutting down: the journal folded into a fresh snapshot
  async close() { await this.flush(); while (this._compacting) await this._compacting; await this._compact(); }
}

function clone(v) { return v === undefined ? undefined : JSON.parse(JSON.stringify(v)); }
