// The suggestions algorithm (js/suggest.js): each rule fires on clear data, stays quiet below its minimum sample,
// and never suggests a price for a gift. Run: node --test admin/tests/

import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import {
  suggest, rank, group, itemSuggestions, economySuggestions, tutorialSuggestions, modeSuggestions, adSuggestions,
  retentionSuggestions, lowerPrice, higherPrice, tutorialRows, tutorialDrops, MIN, LIMIT, RULES,
} from '../js/suggest.js';

const CATALOG = JSON.parse(readFileSync(new URL('../catalog.json', import.meta.url), 'utf8'));
const byId = (list, id) => list.find((s) => s.id === id);
const ids = (list) => list.map((s) => s.id);

// A shop where every regular item sells normally: 400 views, 90% could buy, 10% of views become buys.
function shop(over = {}, totals = {}) {
  const items = CATALOG.items.filter((i) => !i.gift && !i.season).map((i) => ({
    item: i.id, views: 400, afford_views: 360, buys: 40, dabs: 40 * i.price, buyers_7d: 6, price: null, last_buy: null, ...(over[i.id] || {}),
  }));
  for (const [id, row] of Object.entries(over)) if (!items.some((r) => r.item === id)) items.push({ item: id, views: 0, afford_views: 0, buys: 0, dabs: 0, buyers_7d: 0, price: null, last_buy: null, ...row });
  return { items, totals: { dabs_earned: 0, dabs_spent: 0, buys: 0, median_balance: 410, ...totals }, days: [], strokes: [], earn: [] };
}

// What a brand-new launch answers: zeros and empty lists.
const EMPTY = {
  overview: { now: '2026-10-18T12:00:00Z', online: 0, dau: 0, wau: 0, mau: 0, installs: 0, accounts: 0, new_today: 0, new_7d: 0, sessions_today: 0, avg_session_secs: 0,
    retention: { d1: null, d7: null, d30: null, cohort_d1: 0, cohort_d7: 0, cohort_d30: 0 }, days: [] },
  progress: { ranks: [], tutorial: CATALOG.tutorial.map((t) => ({ step: t.id, reached: 0, stuck: 0 })), active_7d: 0, median_rank: null, done_pct: null },
  modes: { modes: [], days: [], stages: [], diffs: [] },
  economy: { items: [], totals: { dabs_earned: 0, dabs_spent: 0, buys: 0, median_balance: null }, days: [], strokes: [], earn: [] },
  ads: { placements: [], days: [] },
};

test('a brand-new launch suggests nothing', () => {
  assert.deepEqual(suggest({ ...EMPTY, catalog: CATALOG, days: 30 }), []);
  assert.deepEqual(suggest({ catalog: CATALOG }), []);
  assert.deepEqual(suggest({}), []);
});

test('a quiet shop (every item under the view minimum) suggests nothing about items', () => {
  const e = shop(Object.fromEntries(CATALOG.items.map((i) => [i.id, { views: MIN.itemViews - 1, afford_views: 1, buys: 0 }])));
  assert.deepEqual(itemSuggestions(e, CATALOG), []);
});

test('too expensive: viewers can\'t buy it and few do; a lower price rounded to 5, near what players hold', () => {
  const e = shop({ cape: { views: 500, afford_views: 50, buys: 2 } }, { median_balance: 410 });
  const s = byId(itemSuggestions(e, CATALOG), 'item-expensive-cape');
  assert.ok(s, 'fires');
  assert.equal(s.area, 'items');
  assert.equal(s.item, 'cape');
  assert.equal(s.price % 5, 0);
  assert.ok(s.price < 480 && s.price >= 480 * (1 - LIMIT.maxCut));
  assert.equal(s.price, 410);
  assert.match(s.detail, /500 views/);
  assert.match(s.detail, /410 dabs/);
  assert.match(s.action, /410 dabs/);
});

test('too expensive uses the live price, and caps the cut at 40%', () => {
  const e = shop({ cape: { views: 500, afford_views: 40, buys: 1, price: 980 } }, { median_balance: 300 });
  const s = byId(itemSuggestions(e, CATALOG), 'item-expensive-cape');
  assert.ok(s);
  assert.equal(s.price, 590); // 980 * 0.6 = 588, rounded to 5
  assert.match(s.detail, /980 dabs \(live price\)/);
  assert.match(s.action, /biggest cut/);
});

test('not liked: viewers could buy it but few do, and no price is suggested', () => {
  const e = shop({ patch: { views: 600, afford_views: 560, buys: 3 } });
  const s = byId(itemSuggestions(e, CATALOG), 'item-unloved-patch');
  assert.ok(s);
  assert.equal(s.price, undefined);
  assert.match(s.action, /isn't the problem/);
});

test('room to raise: sells far above the median and is affordable', () => {
  const e = shop({ bowtie: { views: 400, afford_views: 380, buys: 160 } });
  const s = byId(itemSuggestions(e, CATALOG), 'item-raise-bowtie');
  assert.ok(s);
  assert.equal(s.severity, 'low');
  assert.equal(s.price, 205); // 185 * 1.1 = 203.5, rounded to 5
  assert.ok(s.price > 185 && s.price % 5 === 0);
});

test('room to raise needs enough buys', () => {
  const e = shop({ bowtie: { views: 100, afford_views: 95, buys: MIN.buysToRaise - 1 } }, {});
  // the rest sell 10% of 400 views: 24 buys of 100 is high, but under the minimum
  assert.equal(byId(itemSuggestions(e, CATALOG), 'item-raise-bowtie'), undefined);
});

test('few people look at it: views far under its group\'s median', () => {
  const e = shop({ monocle: { views: 40, afford_views: 36, buys: 4 } });
  const s = byId(itemSuggestions(e, CATALOG), 'item-unseen-monocle');
  assert.ok(s);
  assert.match(s.detail, /40 views, against a median of 400/);
});

test('a gift never gets a price, whatever its numbers', () => {
  const e = shop({ zombie: { views: 5000, afford_views: 5000, buys: 0 } });
  const all = suggest({ economy: e, catalog: CATALOG, days: 30 });
  assert.ok(all.every((s) => s.item !== 'zombie'));
  assert.ok(all.every((s) => !(s.id || '').includes('zombie')));
});

test('a find item that few can buy is "not found yet", never "too expensive", and gets no price', () => {
  const e = shop({ pirate: { views: 600, afford_views: 60, buys: 3 } }, { median_balance: 410 });
  const out = itemSuggestions(e, CATALOG);
  assert.equal(byId(out, 'item-expensive-pirate'), undefined);
  const s = byId(out, 'item-unfound-pirate');
  assert.ok(s);
  assert.equal(s.price, undefined);
  assert.match(s.title, /found/);
  assert.match(s.action, /Palette Island/);
  assert.match(s.detail, /may also cost more than players hold/);
});

test('a find item with few views is "not found yet" too', () => {
  const e = shop({ tophat: { views: 30, afford_views: 10, buys: 1 } });
  const out = itemSuggestions(e, CATALOG);
  assert.equal(byId(out, 'item-unseen-tophat'), undefined);
  assert.ok(byId(out, 'item-unfound-tophat'));
});

test('a find item most viewers could buy (so they found it) can still be "not liked"', () => {
  const e = shop({ tiara: { views: 800, afford_views: 640, buys: 2 } });
  assert.ok(byId(itemSuggestions(e, CATALOG), 'item-unloved-tiara'));
});

test('three or more find items not found in a group become one suggestion', () => {
  const seasonal = Object.fromEntries(CATALOG.items.filter((i) => i.season && !i.gift).map((i) => [i.id, { views: 300, afford_views: 20, buys: 1 }]));
  const e = shop(seasonal, { median_balance: 500 });
  const out = itemSuggestions(e, CATALOG);
  const merged = byId(out, 'item-unfound-seasonal');
  assert.ok(merged);
  assert.match(merged.detail, /Witch hat/);
  assert.equal(out.filter((s) => s.id.startsWith('item-unfound-') && s.id !== 'item-unfound-seasonal' && CATALOG.items.find((i) => i.id === s.id.slice(13))?.season).length, 0);
});

test('item rules need enough items for a median, and a median above zero', () => {
  const few = { items: CATALOG.items.slice(0, MIN.itemsForMedian - 1).map((i) => ({ item: i.id, views: 500, afford_views: 10, buys: 0 })), totals: { median_balance: 100 } };
  assert.deepEqual(itemSuggestions(few, CATALOG).filter((s) => !s.id.startsWith('item-unseen-')), []);
  const none = shop(Object.fromEntries(CATALOG.items.map((i) => [i.id, { buys: 0 }])));
  assert.deepEqual(itemSuggestions(none, CATALOG).filter((s) => /expensive|unloved|raise/.test(s.id)), []);
});

test('lowerPrice and higherPrice', () => {
  assert.equal(lowerPrice(695, 410), 415);   // 695 * 0.6 = 417 -> 415, near 410
  assert.equal(lowerPrice(480, 410), 410);
  assert.equal(lowerPrice(695, null), 590);  // 15% lower when we don't know balances
  assert.equal(lowerPrice(145, 900), 125);   // players hold more: 15% lower
  assert.equal(lowerPrice(5, 0), null);      // nothing sensible below 5
  for (const [p, b] of [[100, 37], [1105, 410], [333, 200], [20, 3]]) {
    const v = lowerPrice(p, b);
    assert.ok(v % 5 === 0 && v < p && v >= 5, p + ' -> ' + v);
  }
  assert.equal(higherPrice(185), 205);
  assert.equal(higherPrice(20), 25);
});

test('economy: a median balance below the cheapest item', () => {
  const e = shop({}, { median_balance: 60, dabs_earned: 50000, dabs_spent: 30000 });
  const s = byId(economySuggestions(e, CATALOG, { active_7d: 300 }), 'economy-poor');
  assert.ok(s);
  assert.equal(s.severity, 'high'); // under half of the cheapest (Flower, 145)
  assert.match(s.detail, /Flower/);
});

test('economy: players sitting on dabs with little to spend them on', () => {
  const e = shop({}, { median_balance: 2000, dabs_earned: 900000, dabs_spent: 200000 });
  const s = byId(economySuggestions(e, CATALOG, { active_7d: 300 }), 'economy-hoard');
  assert.ok(s);
  assert.match(s.detail, /2,000 dabs/);
  assert.match(s.detail, /22%/);
});

test('economy rules wait for enough active players', () => {
  const e = shop({}, { median_balance: 60, dabs_earned: 50000, dabs_spent: 30000 });
  assert.deepEqual(economySuggestions(e, CATALOG, { active_7d: MIN.activePlayers - 1 }), []);
  assert.deepEqual(economySuggestions(e, CATALOG, null, { wau: MIN.activePlayers - 1 }), []);
  assert.ok(economySuggestions(e, CATALOG, null, { wau: MIN.activePlayers }).length);
});

// A funnel: 1000 start, a 20% drop after the slingshot, and 120 stuck there.
function funnel(over = {}) {
  let n = 1000;
  return {
    tutorial: CATALOG.tutorial.map((t) => {
      const row = { step: t.id, reached: n, stuck: 2, ...(over[t.id] || {}) };
      n = Math.round(n * (t.id === 'l:sling' ? 0.8 : 0.99));
      return row;
    }),
    active_7d: 400,
  };
}

test('tutorial: the biggest drop to the next step', () => {
  const out = tutorialSuggestions(funnel(), CATALOG);
  const s = byId(out, 'tutorial-drop-l:sling');
  assert.ok(s);
  assert.equal(s.severity, 'medium');
  assert.match(s.detail, /Lesson: slingshot/);
  assert.match(s.detail, /Lesson: paint freely 2/);
  assert.match(s.detail, /20%/);
});

test('tutorial: the step where the most players are stuck', () => {
  const out = tutorialSuggestions(funnel({ 'l:pound': { stuck: 120 } }), CATALOG);
  const s = byId(out, 'tutorial-stuck-l:pound');
  assert.ok(s);
  assert.match(s.detail, /^120 installs/);
});

test('tutorial rules wait for enough installs, and call out at most three of each', () => {
  const small = { tutorial: funnel().tutorial.map((r) => ({ ...r, reached: Math.round(r.reached / 20), stuck: 1 })) };
  assert.deepEqual(tutorialSuggestions(small, CATALOG), []);
  let n = 2000;
  const steep = { tutorial: CATALOG.tutorial.map((t) => { const r = { step: t.id, reached: n, stuck: 200 }; n = Math.round(n * 0.8); return r; }) };
  const out = tutorialSuggestions(steep, CATALOG);
  assert.equal(out.filter((s) => s.id.startsWith('tutorial-drop-')).length, 3);
  assert.ok(out.filter((s) => s.id.startsWith('tutorial-stuck-')).length <= 3);
});

test('tutorial rows follow the catalog, unknown steps after, missing steps as zeros', () => {
  const rows = tutorialRows({ tutorial: [{ step: 'mystery', reached: 5, stuck: 1 }, { step: 'match', reached: 9, stuck: 0 }] }, CATALOG);
  assert.equal(rows.length, CATALOG.tutorial.length + 1);
  assert.equal(rows[0].step, 'intro');
  assert.equal(rows[0].reached, 0);
  assert.equal(rows[1].reached, 9);
  assert.deepEqual(rows.at(-1), { step: 'mystery', name: 'mystery', known: false, reached: 5, stuck: 1 });
  assert.equal(tutorialDrops(rows).length, CATALOG.tutorial.length - 1); // unknown steps aren't part of the drops
});

const mode = (id, plays, wins, losses, draws, online = 0) => ({ mode: id, plays, wins, losses, draws, players: plays, avg_secs: 90, avg_cov: 40, online });

test('modes: a rarely played mode', () => {
  const m = { modes: [mode('duel', 3000, 1500, 1450, 50), mode('trio', 1500, 500, 980, 20), mode('ffa', 1000, 250, 740, 10), mode('solo', 800, 300, 500, 0), mode('duo', 100, 50, 49, 1)] };
  const out = modeSuggestions(m, CATALOG, 30);
  const s = byId(out, 'mode-rare-duo');
  assert.ok(s);
  assert.match(s.title, /Showdown 2v2/);
  assert.match(s.detail, /in the last 30 days/);
});

test('modes: CPU modes with extreme win rates, too easy and too hard', () => {
  const m = { modes: [mode('duel', 3000, 2500, 450, 50, 300), mode('ffa', 1000, 60, 930, 10), mode('trio', 1200, 400, 780, 20)] };
  const out = modeSuggestions(m, CATALOG, 30);
  assert.ok(byId(out, 'mode-easy-duel'));
  assert.ok(byId(out, 'mode-hard-ffa'));
  assert.equal(byId(out, 'mode-easy-trio'), undefined);
  assert.equal(byId(out, 'mode-hard-trio'), undefined);
});

test('modes: win rates only for modes played mostly offline, with enough results; never Time trial', () => {
  const m = { modes: [mode('duel', 3000, 2500, 450, 50, 2000), mode('ffa', 150, 5, 140, 5), mode('solo', 3000, 2900, 100, 0)] };
  const out = modeSuggestions(m, CATALOG, 30);
  assert.equal(out.filter((s) => /easy|hard/.test(s.id)).length, 0);
});

test('ads: a placement that often fails, and one people quit', () => {
  const a = { placements: [{ placement: 'lesson', asked: 300, shown: 200, rewarded: 195, failed: 100 }, { placement: 'craft', asked: 700, shown: 650, rewarded: 400, failed: 50 }] };
  const out = adSuggestions(a, CATALOG);
  const fail = byId(out, 'ads-fail-lesson');
  assert.ok(fail);
  assert.equal(fail.severity, 'high');
  assert.match(fail.title, /Skip in the Strokes lesson/); // the catalog's name
  assert.ok(byId(out, 'ads-quit-craft'));
  assert.equal(byId(out, 'ads-fail-craft'), undefined);
});

test('ads rules wait for enough requests', () => {
  const a = { placements: [{ placement: 'craft', asked: MIN.adAsked - 1, shown: MIN.adShown - 1, rewarded: 10, failed: 60 }] };
  assert.deepEqual(adSuggestions(a, CATALOG), []);
});

test('retention: weak day 1 with a big enough cohort', () => {
  const r = (d1, cohort, d7 = 0.12, c7 = 500) => ({ retention: { d1, d7, d30: 0.05, cohort_d1: cohort, cohort_d7: c7, cohort_d30: 400 } });
  assert.equal(byId(retentionSuggestions(r(0.2, 300)), 'retention-d1').severity, 'medium');
  assert.equal(byId(retentionSuggestions(r(0.1, 300)), 'retention-d1').severity, 'high');
  assert.deepEqual(retentionSuggestions(r(0.1, MIN.cohort - 1)), []);
  assert.deepEqual(retentionSuggestions(r(null, 0, null, 0)), []);
  assert.deepEqual(retentionSuggestions(r(0.4, 300)), []);
  assert.ok(byId(retentionSuggestions(r(0.4, 300, 0.05, 300)), 'retention-d7'));
});

test('every suggestion has the documented shape, with numbers in its detail', () => {
  const all = suggest({
    overview: { retention: { d1: 0.12, cohort_d1: 300, d7: 0.05, cohort_d7: 300 } },
    progress: funnel({ 'l:pound': { stuck: 120 } }),
    modes: { modes: [mode('duel', 3000, 2500, 450, 50), mode('ffa', 1000, 60, 930, 10), mode('duo', 100, 50, 49, 1)] },
    economy: shop({ cape: { views: 500, afford_views: 50, buys: 2 }, patch: { views: 600, afford_views: 560, buys: 3 }, bowtie: { buys: 160, afford_views: 380 }, monocle: { views: 40 } },
      { median_balance: 60, dabs_earned: 50000, dabs_spent: 30000 }),
    ads: { placements: [{ placement: 'lesson', asked: 300, shown: 200, rewarded: 195, failed: 100 }] },
    catalog: CATALOG, days: 30,
  });
  assert.ok(all.length >= 10);
  assert.equal(new Set(ids(all)).size, all.length, 'ids are unique');
  for (const s of all) {
    for (const k of ['id', 'area', 'severity', 'title', 'detail', 'action']) assert.equal(typeof s[k], 'string', k + ' of ' + s.id);
    assert.ok(['high', 'medium', 'low'].includes(s.severity));
    assert.ok(['retention', 'tutorial', 'items', 'economy', 'modes', 'ads'].includes(s.area));
    assert.match(s.detail, /\d/, 'numbers behind ' + s.id);
    assert.doesNotMatch(s.title + s.detail + s.action, /\u2014/, 'no em dashes');
  }
  // ranked: severity first
  const order = { high: 0, medium: 1, low: 2 };
  for (let i = 1; i < all.length; i++) assert.ok(order[all[i - 1].severity] <= order[all[i].severity]);
  // grouped: each group ranked, the group with the most severe suggestion first
  const groups = group(all);
  assert.ok(groups.length >= 5);
  assert.equal(groups[0].items[0].severity, 'high');
  for (const g of groups) assert.ok(g.items.every((s) => s.area === g.id));
});

test('rank: severity, then the size of the problem', () => {
  const list = [
    { id: 'a', severity: 'low', score: 999 }, { id: 'b', severity: 'high', score: 1 }, { id: 'c', severity: 'high', score: 50 }, { id: 'd', severity: 'medium', score: 5 },
  ];
  assert.deepEqual(ids(rank(list)), ['c', 'b', 'd', 'a']);
});

test('the rules are written down for the page', () => {
  assert.ok(RULES.length >= 8);
  for (const [k, v] of RULES) { assert.ok(k && v); assert.doesNotMatch(v, /NaN|undefined/); }
});
