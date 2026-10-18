// Temporary passwords for a player's password reset, and the rules the database checks.
// No DOM here, so node:test can import it too.

// Letters and digits without look-alikes: no 0/O/o, no 1/l/I/i.
export const UPPER = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
export const LOWER = 'abcdefghjkmnpqrstuvwxyz';
export const DIGITS = '23456789';
export const ALPHABET = UPPER + LOWER + DIGITS;
export const LENGTH = 14; // 14 picks from 55 characters: about 80 bits

// A uniform pick in 0..n-1 from crypto.getRandomValues (rejection sampling, so no modulo bias).
function pick(n, rng) {
  const limit = Math.floor(0x100000000 / n) * n;
  const buf = new Uint32Array(1);
  do rng.getRandomValues(buf); while (buf[0] >= limit);
  return buf[0] % n;
}

export function generatePassword(length = LENGTH, rng = globalThis.crypto) {
  if (!rng || typeof rng.getRandomValues !== 'function') throw new Error('No secure random source');
  for (;;) {
    let s = '';
    for (let i = 0; i < length; i++) s += ALPHABET[pick(ALPHABET.length, rng)];
    if (!passwordProblem(s)) return s; // needs a letter and a digit, like the database
  }
}

// What's wrong with a typed password, in a plain sentence, or null when it's fine.
// The database wants 8..72 characters with a letter and a digit. 72 is also bcrypt's limit in bytes,
// so a password with accented letters or emoji is measured in bytes too.
export function passwordProblem(pw) {
  const s = String(pw ?? '');
  if (s.length < 8) return 'Use at least 8 characters.';
  if (s.length > 72 || new TextEncoder().encode(s).length > 72) return 'Use 72 characters or fewer.';
  if (!/[A-Za-z]/.test(s)) return 'Add at least one letter.';
  if (!/[0-9]/.test(s)) return 'Add at least one digit.';
  if (/^\s|\s$/.test(s)) return "Don't start or end it with a space.";
  return null;
}
