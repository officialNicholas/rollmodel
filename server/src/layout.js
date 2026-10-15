// Map consensus: check an uploaded layout field by field, then reduce it to the canonical form shared with the SDK.
import { canonicalLayout, hashString } from '../client/rmnet.js';
import { LIMITS } from './constants.js';

const fin = v => typeof v === 'number' && Number.isFinite(v);

// Returns { ok: true, canonical, hash, layout } or { ok: false, error }. layout is rebuilt from the canonical form
// (numbers rounded to hundredths), so every server sees exactly the same stage.
export function validateLayout(raw, expect = {}) {
  try {
    if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return bad('layout must be an object');
    const A = raw.arena;
    if (!fin(A) || A < 10 || A > 60) return bad('arena out of range');
    if (expect.arena !== undefined && Math.abs(A - expect.arena) > 0.011) return bad('arena does not match the match');
    const lim = LIMITS.layout, span = A + 10;
    for (const k of ['boxes', 'ramps', 'holes', 'pots', 'powers', 'spawns']) {
      if (!Array.isArray(raw[k])) return bad(k + ' must be an array');
      if (raw[k].length > lim[k]) return bad('too many ' + k);
      for (const e of raw[k]) if (!Array.isArray(e) || e.length > 12) return bad(k + ' entries must be short arrays');
    }
    const xz = (v, what) => { if (!fin(v) || Math.abs(v) > span) throw new Error(what + ' out of range'); };
    const yv = (v, what) => { if (!fin(v) || v < -5 || v > 40) throw new Error(what + ' height out of range'); };
    for (const b of raw.boxes) {
      for (let i = 0; i < 4; i++) xz(b[i], 'box'); yv(b[4], 'box'); yv(b[5], 'box');
      if (!(b[0] < b[1] && b[2] < b[3] && b[4] < b[5])) return bad('box with no size');
      if (b[6] !== undefined && b[6] !== 'c' && b[6] !== 0 && b[6] !== null) return bad('box shape must be c');
    }
    for (const r of raw.ramps) {
      for (let i = 0; i < 4; i++) xz(r[i], 'ramp'); yv(r[5], 'ramp'); yv(r[6], 'ramp');
      if (r[4] !== 'x' && r[4] !== 'z') return bad('ramp axis must be x or z');
      if (!(r[0] < r[1] && r[2] < r[3])) return bad('ramp with no size');
    }
    for (const h of raw.holes) {
      for (let i = 0; i < 4; i++) xz(h[i], 'hole');
      if (!(h[0] < h[1] && h[2] < h[3])) return bad('hole with no size');
      if (h[4] !== undefined && h[4] !== 'c' && h[4] !== 0 && h[4] !== null) return bad('hole shape must be c');
    }
    for (const p of raw.pots) { xz(p[0], 'pot'); yv(p[1], 'pot'); xz(p[2], 'pot'); }
    for (const p of raw.powers) {
      xz(p[0], 'power'); yv(p[1], 'power'); xz(p[2], 'power');
      if (p[3] !== undefined && p[3] !== null && !(typeof p[3] === 'string' && /^[a-z]{1,16}$/.test(p[3]))) return bad('power kind must be a short lowercase word');
    }
    for (const s of raw.spawns) {
      if (!fin(s[0]) || !fin(s[1]) || !fin(s[2]) || Math.abs(s[0]) > A || Math.abs(s[1]) > A || Math.abs(s[2]) > 100) return bad('spawn out of range');
    }
    if (raw.puddles !== undefined && raw.puddles !== null) {
      if (!Array.isArray(raw.puddles)) return bad('puddles must be an array');
      if (raw.puddles.length > lim.puddles) return bad('too many puddles');
      for (const p of raw.puddles) { if (!Array.isArray(p) || p.length > 12) return bad('puddles entries must be short arrays'); xz(p[0], 'puddle'); yv(p[1], 'puddle'); xz(p[2], 'puddle'); }
    }
    if (expect.players && raw.spawns.length < expect.players) return bad('not enough spawns for the players');
    if (raw.pots.length < 1) return bad('a stage needs at least one pot');
    const canonical = canonicalLayout(raw);
    if (canonical.length > LIMITS.maxLayoutJson) return bad('layout too large');
    return { ok: true, canonical, hash: hashString(canonical), layout: fromCanonical(canonical) };
  } catch (e) {
    return bad(e.message || 'bad layout');
  }
}
function bad(error) { return { ok: false, error }; }

// the canonical string back to a layout object (integers of hundredths back to metres)
export function fromCanonical(c) {
  const [A, boxes, ramps, holes, pots, powers, spawns, puddles] = JSON.parse(c.slice(3));
  const m = v => (typeof v === 'number' ? v / 100 : v);
  return {
    arena: A / 100,
    boxes: boxes.map(b => b.map(m)), ramps: ramps.map(r => r.map(m)), holes: holes.map(h => h.map(m)),
    pots: pots.map(p => p.map(m)), powers: powers.map(p => p.map(m)), spawns: spawns.map(s => s.map(m)), puddles: (puddles || []).map(p => p.map(m)),
  };
}
