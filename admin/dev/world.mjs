// Made-up game data for the dev mock (dev/mock.mjs): a few thousand installs simulated day by day with a seeded
// random generator, so the same seed always gives the same shapes. Every number the admin functions return is
// aggregated from these installs, so they agree with each other (actives, retention, the funnel, the economy).
//
// The shapes are tuned so the dashboard's suggestions have something to find: a hard slingshot lesson, a CPU that's
// too easy in 1v1, a rarely played 2v2, an overpriced cape, a hard-to-find pirate hat, a bow tie that sells itself,
// an ad that often fails to load, and so on.

import { readFileSync } from 'node:fs';

export const CATALOG = JSON.parse(readFileSync(new URL('../catalog.json', import.meta.url), 'utf8'));
const MS_DAY = 86400000;
const DAYS = 220; // days of history, today included

// ---------------------------------------------------------------- random helpers

export function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const gauss = (r) => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r());
function poisson(r, lambda) {
  if (!(lambda > 0)) return 0;
  if (lambda > 30) return Math.max(0, Math.round(lambda + Math.sqrt(lambda) * gauss(r)));
  const L = Math.exp(-lambda);
  let k = 0, p = 1;
  do { k++; p *= r(); } while (p > L);
  return k - 1;
}
function pick(r, weights) {
  let t = 0;
  for (const k in weights) t += weights[k];
  let x = r() * t;
  for (const k in weights) { x -= weights[k]; if (x <= 0) return k; }
  return Object.keys(weights).pop();
}
export function uuid(r) {
  let s = '';
  for (let i = 0; i < 32; i++) s += Math.floor(r() * 16).toString(16);
  return s.slice(0, 8) + '-' + s.slice(8, 12) + '-4' + s.slice(13, 16) + '-' + '89ab'[Math.floor(r() * 4)] + s.slice(17, 20) + '-' + s.slice(20, 32);
}
const CODE_CHARS = '23456789ABCDEFGHJKMNPQRSTUVWXYZ'; // the game's friend-code alphabet

// ---------------------------------------------------------------- how the game behaves (made up)

const STEPS = CATALOG.tutorial.map((t) => t.id);
const DONE = STEPS.indexOf('done');
// the chance of going on from a step to the next one, on the first day
const GO_ON = {
  intro: 0.985, match: 0.975, 'l:move': 0.985, 'l:free0': 0.98, 'l:sling': 0.84, 'l:free1': 0.985, 'l:basin': 0.92,
  'l:pound': 0.985, 'l:dodge': 0.98, 'l:item': 0.975, 'l:rollover': 0.985, 'l:orb': 0.985, 'l:free3': 0.99,
  'l:rocketdodge': 0.965, 'l:flower': 0.99, 'l:rest': 0.97, shop: 0.98, locker: 0.985, vote: 0.96, match2: 0.985,
};
const MODES = { solo: 0.15, duel: 0.4, trio: 0.22, ffa: 0.185, duo: 0.045 };
const WIN = { solo: 0.35, duel: 0.81, trio: 0.38, ffa: 0.27, duo: 0.53 };            // against the CPU
const WIN_ONLINE = { solo: 0.35, duel: 0.5, trio: 0.33, ffa: 0.25, duo: 0.5 };
const COV = { solo: 64, duel: 46, trio: 32, ffa: 23, duo: 28 };
const SECS = { solo: 60, duel: 92, trio: 97, ffa: 118, duo: 128 };
const STAGES = { island: 0.28, blank: 0.24, sewer: 0.16, raft: 0.13, crypt: 0.09, cathedral: 0.06, manor: 0.04 };
const DIFFS = { easy: 0.48, normal: 0.34, hard: 0.18 };
const SEASON_DAYS = 25; // the Halloween items have been in the shop this long
// how often an item is looked at, and the chance a view becomes a buy when the player could buy it
const VIEW = { monocle: 0.1, pirate: 1.3, cape: 1.2, tophat: 1.1, bowtie: 1.15 };
const APPEAL = { bowtie: 0.5, flower: 0.3, tiara: 0.02, pirate: 0.32, cape: 0.18, tophat: 0.26, scarf: 0.2, party: 0.22, glasses: 0.2, beanie: 0.2, hat: 0.25, halo: 0.2 };
const FIND = { pirate: 0.03, tophat: 0.25, tiara: 0.6, fangs: 0.04 }; // chance per match on its canvas of finding it (seasonal: 0.35)
// live prices the made-up history already had (someone raised the cape far too much)
export const SEEDED_PRICES = { cape: 980, tophat: 450 };
const IAP = { dabs_500: 499, dabs_1200: 999, starter_pack: 299 };

const NAME_A = ['Dusk', 'Mango', 'Inky', 'Gloss', 'Smudge', 'Daub', 'Pixel', 'Wren', 'Juno', 'Kiwi', 'Pip', 'Moss', 'Fern', 'Echo',
  'Nova', 'Zest', 'Splat', 'Rolly', 'Blot', 'Drip', 'Tint', 'Hue', 'Sable', 'Ochre', 'Umber', 'Cobalt', 'Coral', 'Plum', 'Olive',
  'Lilac', 'Rusty', 'Sunny', 'Misty', 'Ziggy', 'Bean', 'Taffy', 'Pebble', 'Comet', 'Orbit', 'Maple', 'Basil', 'Clover', 'Tango'];
const NAME_B = ['', '', '', 'Roll', 'Paint', 'Brush', 'Pal', 'Star', 'Bug', 'Fox', 'Cat', 'Toad', 'Bear', 'Bot', 'Kid', 'Pop'];
const FIRST = ['Dana', 'Sam', 'Alex', 'Jordan', 'Riley', 'Casey', 'Morgan', 'Taylor', 'Jamie', 'Avery', 'Quinn', 'Rowan', 'Noor',
  'Mia', 'Leo', 'Ava', 'Kai', 'Zoe', 'Eli', 'Ivy', 'Omar', 'Lena', 'Theo', 'Maya', 'Finn', 'Ruby', 'Hugo', 'Isla', 'Nico', 'Aria'];
const LAST = ['Lee', 'Patel', 'Garcia', 'Smith', 'Nguyen', 'Kim', 'Brown', 'Silva', 'Novak', 'Okafor', 'Rossi', 'Larsen', 'Haddad',
  'Murphy', 'Cohen', 'Tanaka', 'Moreau', 'Kowalski', 'Ali', 'Jensen', 'Dubois', 'Costa', 'Byrne', 'Fischer', 'Ahmed', 'Walsh'];

// The admins' own accounts (the mock's auth uses the same ids).
export const ADMIN_IDS = { 'admin@example.com': 'a0000000-0000-4000-8000-00000000ad01', 'owner@example.com': 'a0000000-0000-4000-8000-00000000ad02' };

// ---------------------------------------------------------------- the world

export function makeWorld({ empty = false, iap = false, now = Date.now(), seed = 354 } = {}) {
  const r = rng(seed);
  const N = DAYS;
  const todayStart = Math.floor(now / MS_DAY) * MS_DAY;
  const elapsed = Math.max(60000, now - todayStart);
  const todayFrac = elapsed / MS_DAY;
  const dayStart = (d) => todayStart - (N - 1 - d) * MS_DAY;
  const dayKey = (d) => new Date(dayStart(d)).toISOString().slice(0, 10);
  const days = Array.from({ length: N }, (_, d) => dayKey(d));

  const arr = () => new Float64Array(N);
  const per = (keys) => Object.fromEntries(keys.map((k) => [k, arr()]));
  const itemIds = CATALOG.items.map((i) => i.id);
  const w = {
    now, N, days, dayStart, empty, iap,
    daily: per(['dau', 'new', 'sessions', 'matches', 'ads', 'buys', 'dabs_spent', 'dabs_earned', 'play_secs']),
    modeDay: per([...Object.keys(MODES), 'online']),
    mode: Object.fromEntries(Object.keys(MODES).map((m) => [m, per(['wins', 'losses', 'draws', 'secs', 'cov', 'online'])])),
    stageDay: per(Object.keys(STAGES)),
    diffDay: per(Object.keys(DIFFS)),
    item: Object.fromEntries(itemIds.map((i) => [i, per(['views', 'afford', 'buys', 'dabs'])])),
    buyers: Object.fromEntries(itemIds.map((i) => [i, []])), // [day, install]
    lastBuy: {},
    stroke: Object.fromEntries(CATALOG.strokes.map((s) => [s.id, per(['crafts', 'skips'])])),
    earn: per(['match', 'comm', 'board', 'lesson', 'other']),
    ads: Object.fromEntries(CATALOG.ads.map((a) => [a.id, per(['asked', 'shown', 'rewarded', 'failed'])])),
    iapDay: Object.fromEntries(Object.keys(IAP).map((p) => [p, per(['buys', 'cents'])])),
    modePlayers: Object.fromEntries(Object.keys(MODES).map((m) => [m, 0])),
    installs: [],
    players: [],
  };
  if (empty) return w;

  const prices = Object.fromEntries(CATALOG.items.map((i) => [i.id, SEEDED_PRICES[i.id] ?? i.price]));
  const xpFor = (rank) => 75 * rank * (rank - 1); // XP needed for a rank
  const strokesByRank = (rank) => CATALOG.strokes.filter((s) => s.craft_min != null && (s.rank == null || s.rank <= rank)).map((s) => s.id);
  const findStage = (it) => (it.stage === 'halloween' ? ['crypt', 'cathedral', 'manor'] : [it.stage]);
  const findItems = CATALOG.items.filter((i) => i.find);
  const usedNames = new Set();
  const usedCodes = new Set();

  for (let d0 = 0; d0 < N; d0++) {
    const dow = new Date(dayStart(d0)).getUTCDay();
    const base = 9 + 44 * (1 - Math.exp(-d0 / 55)) + 110 * Math.exp(-(((d0 - (N - 46)) / 4) ** 2));
    const count = poisson(r, base * (dow === 0 || dow === 6 ? 1.3 : 1) * (d0 === N - 1 ? todayFrac : 1));
    for (let k = 0; k < count; k++) simulate(d0);
  }

  function earn(ins, d, src, n) {
    n = Math.round(n);
    ins.dabs += n;
    w.earn[src][d] += n;
    w.daily.dabs_earned[d] += n;
  }
  function reach(ins, step) {
    const i = STEPS.indexOf(step);
    if (i > ins.tut) ins.tut = i;
  }
  function ad(ins, d, placement, fill, finish) {
    const a = w.ads[placement];
    a.asked[d]++;
    if (r() >= fill) { a.failed[d]++; return false; }
    a.shown[d]++;
    if (r() >= finish) return false;
    a.rewarded[d]++;
    w.daily.ads[d]++;
    return true;
  }

  function simulate(first) {
    const ins = {
      idx: w.installs.length, iid: uuid(r), first, plat: r() < 0.82 ? 'ios' : 'web',
      e: Math.pow(r(), 1.15), tut: 0, rank: 1, xp: 0, dabs: 50, owned: new Set(), found: new Set(),
      sessions: 0, matches: 0, active: [], last: 0, account: false, profileAt: null, modes: 0,
    };
    ins.app = ins.plat === 'ios' ? (first > N - 40 ? '1.1' : '1.0') : null;
    ins.ver = 330 + Math.floor((first / (N - 1)) * 24);
    w.installs.push(ins);
    w.daily.new[first]++;

    // the first session: the tutorial, step by step
    let s = 0;
    while (s < DONE && r() < GO_ON[STEPS[s]]) s++;
    ins.tut = s;
    const done = s >= DONE;
    const life = done ? -Math.log(1 - r()) * (8 + 190 * ins.e * ins.e) : 0;

    const activeDays = [first];
    for (let k = 1; first + k < N && k <= life; k++) {
      let p = Math.min(0.92, ins.e * 1.05 * Math.pow(1 + k, -0.36));
      if (first + k === N - 1) p *= Math.pow(todayFrac, 0.7);
      if (r() < p) activeDays.push(first + k);
    }
    for (const d of activeDays) day(ins, d, d === first);
    ins.active = activeDays;
    const lastDay = activeDays[activeDays.length - 1];
    ins.last = lastDay === N - 1 ? now - elapsed * Math.pow(r(), 1.8) : dayStart(lastDay) + r() * MS_DAY;
    ins.lastDay = lastDay;
    // an old-style profile without an account, for some early installs
    if (!ins.account && first < N - 60 && r() < 0.03) { ins.profileAt = dayStart(first) + r() * MS_DAY * 0.5; ins.anon = true; }
  }

  function day(ins, d, isFirst) {
    const dow = new Date(dayStart(d)).getUTCDay();
    const season = d >= N - SEASON_DAYS;
    w.daily.dau[d]++;
    const sessions = isFirst ? 1 + (ins.tut >= DONE ? poisson(r, 0.4) : 0) : 1 + poisson(r, 0.5 + 1.2 * ins.e);
    ins.sessions += sessions;
    w.daily.sessions[d] += sessions;
    let secs = sessions * (90 + 240 * r());

    let matches;
    if (isFirst) {
      matches = (ins.tut > STEPS.indexOf('l:rest') ? 1 : 0) + (ins.tut > STEPS.indexOf('match2') ? 1 : 0);
      if (ins.tut >= DONE) { matches += poisson(r, 1.2 + 2 * ins.e); earn(ins, d, 'lesson', 100); }
    } else matches = poisson(r, 1.2 + 4.5 * ins.e);

    for (let m = 0; m < matches; m++) {
      const mode = ins.rank < 2 ? 'duel' : pick(r, MODES);
      const online = ins.rank >= 3 && ins.account && mode !== 'solo' && mode !== 'trio' && r() < 0.3;
      const stage = pick(r, STAGES);
      const wr = online ? WIN_ONLINE[mode] : WIN[mode];
      const x = r();
      const res = mode === 'solo' ? (x < wr ? 'wins' : 'losses') : x < 0.02 ? 'draws' : x < 0.02 + wr ? 'wins' : 'losses';
      const cov = Math.max(1, Math.min(99, COV[mode] + gauss(r) * 9));
      const len = Math.max(20, SECS[mode] + gauss(r) * (mode === 'solo' ? 0 : 16));
      const st = w.mode[mode];
      st[res][d]++; st.secs[d] += len; st.cov[d] += cov;
      if (online) { st.online[d]++; w.modeDay.online[d]++; }
      w.modeDay[mode][d]++;
      w.stageDay[stage][d]++;
      if (!online && mode !== 'solo') w.diffDay[pick(r, DIFFS)][d]++;
      w.daily.matches[d]++;
      ins.matches++;
      ins.modes |= 1 << Object.keys(MODES).indexOf(mode);
      secs += len;
      earn(ins, d, 'match', 12 + cov / 5 + (res === 'wins' ? 10 : 0));
      // finding the items hidden on this canvas
      for (const it of findItems) {
        if (ins.found.has(it.id) || !findStage(it).includes(stage) || (it.season && !season)) continue;
        if (r() < (FIND[it.id] ?? 0.35)) ins.found.add(it.id);
      }
      // ranks, and the steps they open
      ins.xp += 90 + Math.round(r() * 90);
      while (ins.xp >= xpFor(ins.rank + 1)) {
        ins.rank++;
        if (ins.rank === 2) reach(ins, 'rank2');
        if (ins.rank === 3) {
          if (r() < 0.42) { ins.account = true; ins.profileAt = dayStart(d) + r() * MS_DAY * 0.9; }
          if (r() < 0.85) {
            reach(ins, 'strokes');
            if (ins.plat === 'ios' && r() < 0.5) ad(ins, d, 'lesson', 0.78, 0.95);
            if (r() < 0.9) { reach(ins, 'strokes_done'); earn(ins, d, 'lesson', 60); }
          }
        }
      }
    }
    w.daily.play_secs[d] += Math.round(secs);

    // other ways to earn
    if (ins.rank >= 3 && r() < 0.3) earn(ins, d, 'comm', 40 + 60 * r());
    if (ins.account && dow === 1 && r() < 0.25) earn(ins, d, 'board', 100 + 150 * r());
    if (r() < 0.04) earn(ins, d, 'other', 10 + 30 * r());

    // Strokes crafts, some finished early with a rewarded ad (the iPhone app only)
    if (ins.tut >= STEPS.indexOf('strokes_done') && r() < 0.3) {
      const list = strokesByRank(ins.rank);
      const sid = list[Math.floor(r() * list.length)];
      w.stroke[sid].crafts[d]++;
      if (ins.plat === 'ios' && r() < 0.34 && ad(ins, d, 'craft', 0.93, 0.7)) w.stroke[sid].skips[d]++;
    }

    // the Paint Shop
    if (ins.tut >= STEPS.indexOf('shop') && (isFirst || r() < 0.35 + 0.3 * ins.e)) {
      const avail = CATALOG.items.filter((it) => !ins.owned.has(it.id) && (!it.season || season));
      const weights = Object.fromEntries(avail.map((it) => [it.id, VIEW[it.id] ?? 1]));
      const seen = new Set();
      const n = isFirst ? 3 : 2 + poisson(r, 2);
      for (let v = 0; v < n && seen.size < avail.length; v++) {
        const id = pick(r, weights);
        if (seen.has(id)) continue; // once per install per item per day
        seen.add(id);
        const it = CATALOG.items.find((x) => x.id === id);
        const st = w.item[id];
        st.views[d]++;
        if (it.gift) continue;
        const can = (!it.find || ins.found.has(id)) && ins.dabs >= prices[id];
        if (!can) continue;
        st.afford[d]++;
        if (r() < (APPEAL[id] ?? 0.17)) {
          ins.dabs -= prices[id];
          ins.owned.add(id);
          st.buys[d]++; st.dabs[d] += prices[id];
          w.daily.buys[d]++; w.daily.dabs_spent[d] += prices[id];
          w.buyers[id].push([d, ins.idx]);
          w.lastBuy[id] = Math.max(w.lastBuy[id] || 0, d === N - 1 ? now - elapsed * r() : dayStart(d) + r() * MS_DAY);
        }
      }
    }

    // real-money purchases, only when the mock is asked for them (the game has none yet)
    if (iap && ins.plat === 'ios' && ins.account && r() < 0.006) {
      const p = pick(r, { dabs_500: 0.5, dabs_1200: 0.2, starter_pack: 0.3 });
      w.iapDay[p].buys[d]++; w.iapDay[p].cents[d] += IAP[p];
    }
  }

  for (const ins of w.installs) for (const [i, m] of Object.keys(MODES).entries()) if (ins.modes & (1 << i)) w.modePlayers[m]++;

  // ---------------------------------------------------------------- players with a profile

  const nameFor = () => {
    for (;;) {
      const n = NAME_A[Math.floor(r() * NAME_A.length)] + NAME_B[Math.floor(r() * NAME_B.length)] +
        (r() < 0.45 ? (r() < 0.3 ? '_' : '') + Math.floor(r() * 99 + 1) : '');
      if (n.length >= 3 && n.length <= 16 && !usedNames.has(n.toLowerCase()) && n.toLowerCase() !== 'dusk') { usedNames.add(n.toLowerCase()); return n; }
    }
  };
  const codeFor = () => {
    for (;;) {
      let c = '';
      for (let i = 0; i < 8; i++) c += CODE_CHARS[Math.floor(r() * CODE_CHARS.length)];
      if (!usedCodes.has(c) && c !== 'ABCD2345') { usedCodes.add(c); return c; }
    }
  };
  const iso = (t) => new Date(Math.round(t)).toISOString();
  const status = (ins) => (now - ins.last < 90000 ? (r() < 0.5 ? 'match' : 'lobby') : 'offline');
  const installRow = (ins) => ({
    iid: ins.iid, platform: ins.plat, app_ver: ins.app, game_ver: ins.ver, first_at: iso(dayStart(ins.first) + 3600000),
    last_at: iso(ins.last), sessions: ins.sessions, matches: ins.matches, tut: STEPS[ins.tut],
  });
  const makePlayer = (ins, over = {}) => {
    const account = !ins.anon;
    const created = ins.profileAt || dayStart(ins.first);
    const p = {
      id: uuid(r), name: nameFor(), code: codeFor(), rank: ins.rank, look: { paint: Math.floor(r() * 12), eyes: Math.floor(r() * 6) },
      account, anonymous: !account, admin: false,
      created_at: iso(created), last_sign_in_at: account ? iso(Math.max(created, ins.last - r() * 5 * MS_DAY)) : null,
      last_seen: iso(ins.last), status: status(ins),
      friends: Math.min(40, poisson(r, 2 + 8 * ins.e)), blocked_by_them: r() < 0.06 ? 1 + poisson(r, 0.6) : 0,
      details: account ? {
        first_name: FIRST[Math.floor(r() * FIRST.length)], last_name: LAST[Math.floor(r() * LAST.length)],
        birth_year: 1972 + Math.floor(r() * 40), terms: created > now - 20 * MS_DAY ? '2026-10' : '2026-09', agreed_at: iso(created + 60000),
      } : null,
      save: account ? { rank: ins.rank, xp: ins.xp, drops: ins.dabs, items: ins.owned.size, at: iso(ins.last - r() * 600000) } : null,
      installs: [installRow(ins)],
      sessions: now - ins.last < 3600000 * 6 ? 1 + poisson(r, 0.8) : poisson(r, 0.3), // live sessions, for Sign out everywhere
      ...over,
    };
    if (account && r() < 0.12) p.installs.push({ ...installRow(ins), iid: uuid(r), platform: 'web', app_ver: null, sessions: 1 + poisson(r, 3), matches: poisson(r, 6) });
    return p;
  };
  for (const ins of w.installs) if (ins.account || ins.anon) w.players.push(makePlayer(ins));

  // a few players the tests and screenshots rely on
  const regular = w.installs.filter((i) => i.tut >= DONE && i.rank >= 5 && i.last > now - 3 * MS_DAY);
  const pickIns = (k) => regular[Math.floor(regular.length * k)] || w.installs[0];
  const dusk = makePlayer(pickIns(0.5), { name: 'Dusk', code: 'ABCD2345', account: true, anonymous: false, friends: 4, blocked_by_them: 0, sessions: 2 });
  dusk.details = { first_name: 'Dana', last_name: 'Lee', birth_year: 2001, terms: '2026-10', agreed_at: dusk.created_at };
  usedNames.add('dusk');
  const duskSeed = rng(seed + 1);
  w.players.push(dusk,
    makePlayer(pickIns(0.3), { name: 'Duskfall', anonymous: false, account: true }),
    makePlayer(pickIns(0.7), { name: 'DuskyRoller', anonymous: false, account: true }),
    makePlayer(pickIns(0.2), { name: 'Bramble', account: false, anonymous: true, details: null, save: null, last_sign_in_at: null }),
    makePlayer(pickIns(0.6), { name: null, code: 'QRST6789' }),
    makePlayer(pickIns(0.9), { id: ADMIN_IDS['owner@example.com'], name: 'RollModelHQ', admin: true }));
  void duskSeed;
  w.players.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
  return w;
}

// ---------------------------------------------------------------- answering the admin functions

const sumRange = (a, from, to) => { let t = 0; for (let i = from; i < to; i++) t += a[i]; return t; };
const median = (list) => {
  const v = [...list].sort((a, b) => a - b);
  if (!v.length) return null;
  const m = v.length >> 1;
  return v.length % 2 ? v[m] : Math.round((v[m - 1] + v[m]) / 2);
};
const clampDays = (p) => Math.max(1, Math.min(180, Number.isInteger(p) ? p : 30));

export function overview(w, pDays) {
  const days = clampDays(pDays);
  const { N, now } = w;
  const from = N - days;
  const ins = w.installs;
  const seen = (ms) => ins.filter((i) => i.last >= now - ms).length;
  const today = N - 1;
  const cohort = (lo, hi, k) => {
    const c = ins.filter((i) => i.first >= today - hi && i.first <= today - lo);
    if (!c.length) return { share: null, size: 0 };
    const back = c.filter((i) => i.active.includes(i.first + k)).length;
    return { share: Math.round((back / c.length) * 1000) / 1000, size: c.length };
  };
  const d1 = cohort(2, 8, 1), d7 = cohort(8, 14, 7), d30 = cohort(31, 37, 30);
  return {
    now: new Date(now).toISOString(),
    online: seen(5 * 60000),
    dau: seen(86400000), wau: seen(7 * 86400000), mau: seen(30 * 86400000),
    installs: ins.length,
    accounts: w.players.filter((p) => p.account).length,
    new_today: w.daily.new[today] || 0,
    new_7d: sumRange(w.daily.new, N - 7, N),
    sessions_today: w.daily.sessions[today] || 0,
    avg_session_secs: w.daily.sessions[today] ? Math.round(w.daily.play_secs[today] / w.daily.sessions[today]) : 0,
    retention: { d1: d1.share, d7: d7.share, d30: d30.share, cohort_d1: d1.size, cohort_d7: d7.size, cohort_d30: d30.size },
    days: w.days.slice(from).map((day, j) => {
      const i = from + j;
      const g = (k) => Math.round(w.daily[k][i]);
      return { day, dau: g('dau'), new: g('new'), sessions: g('sessions'), matches: g('matches'), ads: g('ads'), buys: g('buys'),
        dabs_spent: g('dabs_spent'), dabs_earned: g('dabs_earned'), play_secs: g('play_secs') };
    }),
  };
}

export function modes(w, pDays) {
  const days = clampDays(pDays);
  const from = w.N - days;
  const ids = Object.keys(w.mode);
  const list = ids.map((m) => {
    const st = w.mode[m];
    const s = (k) => sumRange(st[k], from, w.N);
    const plays = s('wins') + s('losses') + s('draws');
    return { mode: m, plays, wins: s('wins'), losses: s('losses'), draws: s('draws'), players: w.modePlayers[m],
      avg_secs: plays ? Math.round(s('secs') / plays) : 0, avg_cov: plays ? Math.round((s('cov') / plays) * 10) / 10 : 0, online: s('online') };
  }).filter((m) => m.plays > 0 || m.players > 0);
  const top = (obj) => Object.keys(obj).map((k) => [k, sumRange(obj[k], from, w.N)]).filter(([, n]) => n > 0).sort((a, b) => b[1] - a[1]);
  return {
    modes: list,
    days: w.days.slice(from).map((day, j) => {
      const row = { day };
      for (const k of Object.keys(w.modeDay)) row[k] = w.modeDay[k][from + j];
      return row;
    }),
    stages: top(w.stageDay).map(([stage, plays]) => ({ stage, plays })),
    diffs: top(w.diffDay).map(([diff, plays]) => ({ diff, plays })),
  };
}

export function progress(w, pSteps) {
  const steps = Array.isArray(pSteps) && pSteps.length ? pSteps.map(String) : CATALOG.tutorial.map((t) => t.id);
  const all = CATALOG.tutorial.map((t) => t.id);
  const order = [...steps, ...all.filter((s) => !steps.includes(s))];
  const { now } = w;
  const active30 = w.installs.filter((i) => i.last >= now - 30 * 86400000);
  const ranks = new Map();
  for (const i of w.installs) {
    const k = Math.min(50, i.rank);
    const row = ranks.get(k) || { rank: k, players: 0, active: 0 };
    row.players++;
    if (i.last >= now - 30 * 86400000) row.active++;
    ranks.set(k, row);
  }
  const doneIdx = all.indexOf('done');
  return {
    ranks: [...ranks.values()].sort((a, b) => a.rank - b.rank),
    tutorial: order.map((step) => {
      const idx = all.indexOf(step);
      if (idx < 0) return { step, reached: 0, stuck: 0 };
      return {
        step,
        reached: w.installs.filter((i) => i.tut >= idx).length,
        stuck: w.installs.filter((i) => i.tut === idx && i.tut < doneIdx && i.last < now - 3 * 86400000).length,
      };
    }),
    active_7d: w.installs.filter((i) => i.last >= now - 7 * 86400000).length,
    median_rank: median(active30.map((i) => i.rank)),
    done_pct: w.installs.length ? Math.round((w.installs.filter((i) => i.tut >= doneIdx).length / w.installs.length) * 1000) / 1000 : null,
  };
}

export function economy(w, pDays, prices) {
  const days = clampDays(pDays);
  const from = w.N - days;
  const items = [];
  for (const it of CATALOG.items) {
    const st = w.item[it.id];
    const s = (k) => sumRange(st[k], from, w.N);
    const live = prices.get(it.id);
    if (!s('views') && !s('buys') && !live) continue;
    items.push({
      item: it.id, views: s('views'), afford_views: s('afford'), buys: s('buys'), dabs: s('dabs'),
      buyers_7d: new Set(w.buyers[it.id].filter(([d]) => d >= w.N - 7).map(([, i]) => i)).size,
      price: live ? live.price : null,
      last_buy: w.lastBuy[it.id] ? new Date(Math.round(w.lastBuy[it.id])).toISOString() : null,
    });
  }
  // live prices for items the catalog doesn't know
  for (const [id, p] of prices) if (!CATALOG.items.some((i) => i.id === id)) items.push({ item: id, views: 0, afford_views: 0, buys: 0, dabs: 0, buyers_7d: 0, price: p.price, last_buy: null });
  const t = (k) => sumRange(w.daily[k], from, w.N);
  const active = w.installs.filter((i) => i.last >= w.now - 7 * 86400000);
  return {
    items,
    totals: { dabs_earned: t('dabs_earned'), dabs_spent: t('dabs_spent'), buys: t('buys'), median_balance: median(active.map((i) => i.dabs)) },
    days: w.days.slice(from).map((day, j) => ({ day, buys: w.daily.buys[from + j], dabs_spent: w.daily.dabs_spent[from + j], dabs_earned: w.daily.dabs_earned[from + j] })),
    strokes: Object.keys(w.stroke).map((id) => ({ stroke: id, crafts: sumRange(w.stroke[id].crafts, from, w.N), skips: sumRange(w.stroke[id].skips, from, w.N) }))
      .filter((x) => x.crafts > 0),
    earn: Object.keys(w.earn).map((src) => ({ src, dabs: sumRange(w.earn[src], from, w.N) })).filter((x) => x.dabs > 0),
  };
}

export function ads(w, pDays) {
  const days = clampDays(pDays);
  const from = w.N - days;
  const placements = Object.keys(w.ads).map((id) => {
    const a = w.ads[id];
    const s = (k) => sumRange(a[k], from, w.N);
    return { placement: id, asked: s('asked'), shown: s('shown'), rewarded: s('rewarded'), failed: s('failed') };
  }).filter((p) => p.asked > 0);
  return {
    placements,
    days: w.days.slice(from).map((day, j) => {
      const row = { day, asked: 0, shown: 0, rewarded: 0, failed: 0 };
      for (const a of Object.values(w.ads)) for (const k of ['asked', 'shown', 'rewarded', 'failed']) row[k] += a[k][from + j];
      return row;
    }),
  };
}

export function iapData(w, pDays) {
  const days = clampDays(pDays);
  const from = w.N - days;
  const products = Object.keys(w.iapDay).map((p) => ({ product: p, buys: sumRange(w.iapDay[p].buys, from, w.N), revenue_cents: sumRange(w.iapDay[p].cents, from, w.N) }))
    .filter((p) => p.buys > 0);
  if (!products.length) return { products: [], days: [] };
  return {
    products,
    days: w.days.slice(from).map((day, j) => {
      let buys = 0, cents = 0;
      for (const p of Object.values(w.iapDay)) { buys += p.buys[from + j]; cents += p.cents[from + j]; }
      return { day, buys, revenue_cents: cents };
    }),
  };
}
