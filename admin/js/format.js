// Numbers, shares, durations and times, written the same way everywhere.
// No DOM here, so node:test can import it too.

const NF = new Intl.NumberFormat('en-GB');
const ok = (n) => typeof n === 'number' && Number.isFinite(n);

// 15230 -> "15,230"
export const num = (n) => (ok(n) ? NF.format(Math.round(n)) : '0');

// 15230 -> "15K", 1650000 -> "1.7M": for axis ticks and big tiles
export function compact(n) {
  if (!ok(n)) return '0';
  const a = Math.abs(n);
  const s = n < 0 ? '-' : '';
  const one = (v, unit) => s + (v >= 10 ? Math.round(v) : Math.round(v * 10) / 10) + unit;
  if (a >= 1e6) return one(a / 1e6, 'M');
  if (a >= 1e3) return one(a / 1e3, 'K');
  return s + NF.format(Math.round(a * 10) / 10);
}

// part / whole, or null when there's nothing to divide by
export const ratio = (part, whole) => (ok(part) && ok(whole) && whole > 0 ? part / whole : null);

// 0.4123 -> "41%", 0.0412 -> "4.1%", null -> "n/a"
export function pct(x) {
  if (!ok(x)) return 'n/a';
  const v = x * 100;
  if (v === 0) return '0%';
  if (Math.abs(v) < 10) return (Math.round(v * 10) / 10) + '%';
  return Math.round(v) + '%';
}

// 742 -> "12m 22s", 59 -> "59s", 5400 -> "1h 30m"
export function secs(s) {
  if (!ok(s) || s <= 0) return '0s';
  s = Math.round(s);
  if (s < 60) return s + 's';
  if (s < 3600) return Math.floor(s / 60) + 'm ' + (s % 60) + 's';
  return Math.floor(s / 3600) + 'h ' + Math.floor((s % 3600) / 60) + 'm';
}

// play time in hours: 1040000 -> "289"
export const hours = (s) => (ok(s) ? s / 3600 : 0);

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

// API days are UTC dates: "2026-09-19" -> "19 Sep"
export function day(ymd) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ymd || '');
  return m ? Number(m[3]) + ' ' + MONTHS[Number(m[2]) - 1] : String(ymd || '');
}

// "2026-09-19" -> "Sat 19 Sep 2026"
export function dayLong(ymd) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ymd || '');
  if (!m) return String(ymd || '');
  const d = new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
  return WEEKDAYS[d.getUTCDay()] + ' ' + Number(m[3]) + ' ' + MONTHS[Number(m[2]) - 1] + ' ' + m[1];
}

// today's UTC date as the API writes it
export const todayUTC = (now = Date.now()) => new Date(now).toISOString().slice(0, 10);

const toDate = (iso) => {
  if (!iso) return null;
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? null : d;
};
const pad = (n) => String(n).padStart(2, '0');

// times are shown in the browser's own time zone: "18 Oct 2026, 09:12"
export function dateTime(iso) {
  const d = toDate(iso);
  if (!d) return 'n/a';
  return d.getDate() + ' ' + MONTHS[d.getMonth()] + ' ' + d.getFullYear() + ', ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
}

// "09:12"
export function clock(iso) {
  const d = toDate(iso);
  return d ? pad(d.getHours()) + ':' + pad(d.getMinutes()) : 'n/a';
}

// "just now", "5 min ago", "3 h ago", "2 days ago", then the date
export function ago(iso, now = Date.now()) {
  const d = toDate(iso);
  if (!d) return 'never';
  const s = Math.round((now - d.getTime()) / 1000);
  if (s < 45) return 'just now';
  if (s < 3600) return Math.max(1, Math.round(s / 60)) + ' min ago';
  if (s < 86400) return Math.round(s / 3600) + ' h ago';
  const days = Math.round(s / 86400);
  if (days === 1) return 'yesterday';
  if (days < 30) return days + ' days ago';
  return d.getDate() + ' ' + MONTHS[d.getMonth()] + ' ' + d.getFullYear();
}

export const round5 = (x) => Math.round(x / 5) * 5;

export function median(list) {
  const v = list.filter(ok).sort((a, b) => a - b);
  if (!v.length) return null;
  const m = v.length >> 1;
  return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2;
}

export const sum = (list) => list.reduce((a, b) => a + (ok(b) ? b : 0), 0);

// "ABCD2345" -> "ABCD 2345", the way the game shows friend codes
export const friendCode = (c) => (c ? String(c).slice(0, 4) + ' ' + String(c).slice(4) : '');

// "dabs" with the right number: 1 dab, 5 dabs
export const dabs = (n) => num(n) + (Math.round(n) === 1 ? ' dab' : ' dabs');

// "1 install", "2 installs"
export const plural = (n, one, many = one + 's') => num(n) + ' ' + (Math.round(n) === 1 ? one : many);

export const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
