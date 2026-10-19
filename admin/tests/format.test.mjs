// Formatting (js/format.js) and passwords (js/password.js): small, pure, and easy to get subtly wrong.

import test from 'node:test';
import assert from 'node:assert/strict';
import { num, compact, pct, ratio, secs, day, dayLong, ago, round5, median, friendCode, dabs, plural, UUID } from '../js/format.js';
import { generatePassword, passwordProblem, ALPHABET, LENGTH } from '../js/password.js';

test('numbers', () => {
  assert.equal(num(15230), '15,230');
  assert.equal(num(0), '0');
  assert.equal(num(null), '0');
  assert.equal(num(NaN), '0');
  assert.equal(compact(950), '950');
  assert.equal(compact(1000), '1K');
  assert.equal(compact(1500), '1.5K');
  assert.equal(compact(15230), '15K');
  assert.equal(compact(1650000), '1.7M');
  assert.equal(compact(2.5), '2.5');
  assert.equal(dabs(1), '1 dab');
  assert.equal(dabs(1200), '1,200 dabs');
  assert.equal(plural(2, 'session'), '2 sessions');
  assert.equal(plural(1, 'player'), '1 player');
});

test('shares', () => {
  assert.equal(pct(0.4123), '41%');
  assert.equal(pct(0.0412), '4.1%');
  assert.equal(pct(0.004), '0.4%');
  assert.equal(pct(0), '0%');
  assert.equal(pct(null), 'n/a');
  assert.equal(ratio(1, 4), 0.25);
  assert.equal(ratio(1, 0), null);
  assert.equal(pct(ratio(5, 0)), 'n/a');
});

test('durations and days', () => {
  assert.equal(secs(742), '12m 22s');
  assert.equal(secs(59), '59s');
  assert.equal(secs(5400), '1h 30m');
  assert.equal(secs(0), '0s');
  assert.equal(day('2026-09-19'), '19 Sep');
  assert.equal(dayLong('2026-09-19'), 'Sat 19 Sep 2026');
  const now = Date.parse('2026-10-18T12:00:00Z');
  assert.equal(ago('2026-10-18T11:59:50Z', now), 'just now');
  assert.equal(ago('2026-10-18T11:55:00Z', now), '5 min ago');
  assert.equal(ago('2026-10-18T09:00:00Z', now), '3 h ago');
  assert.equal(ago('2026-10-17T10:00:00Z', now), 'yesterday');
  assert.equal(ago('2026-10-10T12:00:00Z', now), '8 days ago');
  assert.equal(ago(null, now), 'never');
});

test('helpers', () => {
  assert.equal(round5(203.5), 205);
  assert.equal(round5(417), 415);
  assert.equal(median([3, 1, 2]), 2);
  assert.equal(median([4, 1, 2, 3]), 2.5);
  assert.equal(median([]), null);
  assert.equal(friendCode('ABCD2345'), 'ABCD 2345');
  assert.ok(UUID.test('a0000000-0000-4000-8000-00000000ad01'));
  assert.ok(!UUID.test('javascript:alert(1)'));
});

test('generated passwords: long, letters and digits, no look-alikes', () => {
  const seen = new Set();
  for (let i = 0; i < 300; i++) {
    const pw = generatePassword();
    assert.equal(pw.length, LENGTH);
    assert.ok(LENGTH >= 12);
    assert.match(pw, /[A-Za-z]/);
    assert.match(pw, /[0-9]/);
    assert.doesNotMatch(pw, /[0O1lIio]/);
    for (const c of pw) assert.ok(ALPHABET.includes(c));
    assert.equal(passwordProblem(pw), null);
    seen.add(pw);
  }
  assert.equal(seen.size, 300);
});

test('generated passwords use crypto.getRandomValues, with no modulo bias', () => {
  // a fake source: first a value past the last whole multiple of 55 (it must be skipped), then small ones
  const values = [0xFFFFFFFF, 0, 54, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
  let i = 0;
  const rng = { getRandomValues(buf) { buf[0] = values[i++ % values.length]; return buf; } };
  const pw = generatePassword(14, rng);
  assert.equal(pw.slice(0, 3), ALPHABET[0] + ALPHABET[54] + ALPHABET[1]); // the 0xFFFFFFFF draw was rejected, not wrapped
  assert.equal(pw.length, 14);
  assert.throws(() => generatePassword(14, {}), /secure random/);
});

test('typed passwords: the database\'s rules, in plain words', () => {
  assert.equal(passwordProblem('abcd1234'), null);
  assert.match(passwordProblem('abc123'), /at least 8/);
  assert.match(passwordProblem('a1'.repeat(37)), /72/);
  assert.match(passwordProblem('é'.repeat(40) + '1'), /72/); // 81 bytes
  assert.match(passwordProblem('12345678'), /letter/);
  assert.match(passwordProblem('abcdefgh'), /digit/);
  assert.match(passwordProblem(' abcd1234'), /space/);
  assert.match(passwordProblem(''), /at least 8/);
});
