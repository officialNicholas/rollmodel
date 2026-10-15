// Display names: tidy them up, keep them short, and refuse the obvious bad words.
// The filter is deliberately small; real moderation (reports, a bigger list, a service) is an owner decision.
import { LIMITS } from './constants.js';
import { randomInt } from 'node:crypto';

// bad anywhere inside the name (after leetspeak is undone and everything but letters is dropped)
const SUBSTR = ['fuck', 'shit', 'cunt', 'nigg', 'fagg', 'bitch', 'whore', 'slut', 'twat', 'pussy', 'asshole', 'hitler', 'porn'];
// bad as a whole word only (they hide inside ordinary words: Dickens, peacock, grape, therapist, swank)
const WORDS = ['dick', 'cock', 'rape', 'rapist', 'fag', 'spic', 'penis', 'vagina', 'cum', 'sex', 'ass', 'tits', 'jizz', 'kkk', 'nazi', 'kike', 'chink', 'wank', 'retard'];
// ordinary words that contain one of the strings above
const ALLOW = ['scunthorpe', 'niggle', 'niggling'];
const LEET = { 0: 'o', 1: 'i', 2: 'z', 3: 'e', 4: 'a', 5: 's', 6: 'g', 7: 't', 8: 'b', 9: 'g', '@': 'a', $: 's', '!': 'i', '|': 'i', '+': 't' };

const skeleton = s => s.toLowerCase().replace(/[0-9@$!|+]/g, c => LEET[c] || c);
// control characters, zero-width characters and direction overrides (built from code points so the source stays ASCII)
const INVISIBLE = new RegExp('[' + [[0x00, 0x1f], [0x7f, 0x9f], [0x200b, 0x200f], [0x2028, 0x202e], [0x2060, 0x206f], [0xfeff, 0xfeff]]
  .map(([a, b]) => String.fromCharCode(a) + '-' + String.fromCharCode(b)).join('') + ']', 'g');

export function isProfane(name) {
  let sk = skeleton(name); for (const a of ALLOW) sk = sk.split(a).join(' ');
  const letters = sk.replace(/[^a-z]/g, '');
  if (SUBSTR.some(w => letters.includes(w))) return true;
  const words = sk.split(/[^a-z]+/).filter(Boolean);
  // letters spelled out one at a time ("d.i.c.k") count as a word too
  const runs = []; let run = '';
  for (const w of words) { if (w.length === 1) run += w; else { if (run) runs.push(run); run = ''; } }
  if (run) runs.push(run);
  return [...words, ...runs].some(w => WORDS.includes(w) || SUBSTR.some(s => w.includes(s)));
}

export const defaultName = () => 'Player' + String(1000 + randomInt(9000));

// returns { name, changed, reason }
export function sanitizeName(raw) {
  if (typeof raw !== 'string') return { name: defaultName(), changed: true, reason: 'missing' };
  let s = raw.normalize('NFKC')
    .replace(INVISIBLE, '')
    .replace(/[^\p{L}\p{N} _.\-']/gu, '')
    .replace(/\s+/g, ' ').trim();
  if ([...s].length > LIMITS.nameMax) s = [...s].slice(0, LIMITS.nameMax).join('').trim();
  if ([...s].length < LIMITS.nameMin) return { name: defaultName(), changed: true, reason: 'empty' };
  if (isProfane(s)) return { name: defaultName(), changed: true, reason: 'profanity' };
  return { name: s, changed: s !== raw, reason: s !== raw ? 'cleaned' : null };
}

// "look" is the cosmetic description the game sends (colours, eyes, hats). The server only passes it on, so it just has
// to be small, plain JSON.
export function sanitizeLook(look) {
  if (look === null || look === undefined) return null;
  if (typeof look !== 'object' && typeof look !== 'string') return null;
  let s;
  try { s = JSON.stringify(look); } catch (e) { return null; }
  if (!s || s.length > LIMITS.lookMax) return null;
  return JSON.parse(s);
}
