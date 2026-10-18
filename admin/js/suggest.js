// What to change: explainable rules over the admin API's answers plus catalog.json.
// Pure functions with no DOM, so node:test runs them too (tests/suggest.test.mjs).
//
// Every rule needs a minimum amount of data first (MIN below), so a quiet launch says nothing rather than noise.
// Each suggestion is { id, area, severity: 'high'|'medium'|'low', title, detail, action }, plus `score` for ranking
// and, for an item price, { item, price } so the page can open the price editor.

import { num, pct, ratio, median, round5, sum, dabs } from './format.js';

// Minimum sample sizes before a rule speaks.
export const MIN = {
  itemViews: 100,     // views of an item before its conversion counts
  itemsForMedian: 4,  // items with enough views before "the median item" means anything
  buysToRaise: 25,    // buys before suggesting a higher price
  groupViews: 100,    // median views of an item's group (regular or seasonal) before "few look at it" can fire
  activePlayers: 50,  // installs active in the last 7 days before the balance rules fire
  dabsEarned: 10000,  // dabs earned in the range before the spend share counts
  stepReached: 100,   // installs that reached a tutorial step before its drop counts
  stuck: 25,          // installs stuck at a step before it's called out
  modePlays: 500,     // plays in the range before mode shares count
  modeResults: 200,   // results in a mode before its win rate counts
  adAsked: 100,       // ad requests before the failure share counts
  adShown: 100,       // ads shown before the completion share counts
  cohort: 100,        // installs in a retention cohort
};

// Where each rule draws its line.
export const LIMIT = {
  cantAfford: 0.4,    // under 40% of views could buy it right then: the price is in the way
  canAfford: 0.6,     // 60% or more could buy it right then: the price isn't the problem
  lowConv: 0.5,       // buys per view under half the median item's
  highConv: 2,        // buys per view over twice the median item's
  lowViews: 0.3,      // views under 30% of its group's median
  maxCut: 0.4,        // never suggest more than 40% off in one go
  raise: 0.1,         // suggest about 10% more
  hoardPrice: 2,      // median balance over twice the median item price...
  hoardSpend: 0.5,    // ...while players spend under half of what they earn
  stepDrop: 0.15,     // 15% or more of a step's installs never reach the next step
  stuckShare: 0.05,   // 5% or more of a step's installs stuck there
  rareMode: 0.05,     // a mode with under 5% of plays
  offline: 0.5,       // a mode counts as a CPU mode when most of its plays are offline
  easyBy: 0.25,       // a win rate this far above an even match is too easy
  hardBy: 0.5,        // under half of an even match's win rate is too hard
  failRate: 0.15,     // 15% or more of ad requests failed
  completion: 0.75,   // under 75% of shown ads watched to the end
  d1: 0.25,           // day-1 retention under 25%
  d7: 0.08,           // day-7 retention under 8%
};

// An even match's win rate: one rival, two rivals, four players, two teams.
export const FAIR = { duel: 1 / 2, trio: 1 / 3, ffa: 1 / 4, duo: 1 / 2 };

export const AREAS = [
  { id: 'retention', label: 'Retention', page: 'overview' },
  { id: 'tutorial', label: 'Tutorial', page: 'players' },
  { id: 'items', label: 'Paint Shop items', page: 'economy' },
  { id: 'economy', label: 'Economy', page: 'economy' },
  { id: 'modes', label: 'Modes', page: 'modes' },
  { id: 'ads', label: 'Ads', page: 'ads' },
];

const SEV = { high: 0, medium: 1, low: 2 };

const names = (list) => new Map((list || []).map((x) => [x.id, x.name]));
const q = (s) => '"' + s + '"';
const make = (id, area, severity, title, detail, action, score, extra) =>
  ({ id, area, severity, title, detail, action, score: Math.round(score || 0), ...extra });

// ---------------------------------------------------------------- Paint Shop items

// The price to suggest for an item viewers can't afford: near what active players hold,
// at most 40% off in one go, at least 5 off, rounded to 5.
export function lowerPrice(price, balance) {
  let target = balance > 0 && balance < price ? balance : price * 0.85;
  target = Math.max(target, price * (1 - LIMIT.maxCut));
  let p = Math.max(5, round5(target));
  if (p >= price) p = Math.max(5, round5(price - 5));
  return p < price ? p : null; // nothing sensible below 5 dabs
}

export const higherPrice = (price) => Math.max(round5(price * (1 + LIMIT.raise)), price + 5);

// One row per catalog item that can be sold (gifts are free and never priced).
// afford_views are the views where the player could buy it right then: in stock (sold outright, or already found on
// its canvas, for `find` items) and enough dabs.
export function itemRows(economy, catalog) {
  const byId = new Map(((economy && economy.items) || []).map((r) => [r.item, r]));
  return (catalog.items || []).filter((it) => !it.gift).map((it) => {
    const r = byId.get(it.id) || {};
    const views = r.views || 0;
    const afford = Math.min(r.afford_views || 0, views);
    const buys = r.buys || 0;
    return {
      id: it.id, name: it.name, season: !!it.season, find: !!it.find, stage: it.stage, def: it.price,
      price: r.price ?? it.price, live: r.price != null,
      views, afford, buys, conv: views ? buys / views : 0, affordShare: views ? afford / views : 0,
    };
  });
}

export function itemSuggestions(economy, catalog) {
  const out = [];
  if (!economy || !catalog) return out;
  const rows = itemRows(economy, catalog);
  const balance = economy.totals ? economy.totals.median_balance : null;
  const stage = names(catalog.stages);
  const where = (r) => (stage.get(r.stage) ? 'on ' + stage.get(r.stage) : 'on its canvas');
  const add = (sg) => { if (!out.some((x) => x.id === sg.id)) out.push(sg); };
  // A find item has to be found on its canvas before it can be bought, so few views or buys may only mean
  // few players have found it yet: never call it too expensive or unloved on that alone.
  const unfoundList = [];
  const unfound = (r, detail, score) => {
    if (!unfoundList.some((x) => x.r.id === r.id)) unfoundList.push({ r, detail, score });
  };

  // Against the median of the items with enough views.
  const enough = rows.filter((r) => r.views >= MIN.itemViews);
  const medConv = enough.length >= MIN.itemsForMedian ? median(enough.map((r) => r.conv)) : null;
  if (medConv > 0) {
    const medText = pct(medConv) + ' for the median item';
    for (const r of enough) {
      const conv = pct(r.conv) + ' of views became buys (' + medText + ')';
      const strong = r.views >= 4 * MIN.itemViews && r.conv < medConv / 4;
      const could = pct(r.affordShare) + ' of its ' + num(r.views) + ' views could buy it right then';
      if (r.conv < medConv * LIMIT.lowConv && r.affordShare < LIMIT.cantAfford) {
        if (r.find) {
          unfound(r, 'Only ' + could + ' (found, and enough dabs), and ' + conv + '.' +
            (balance > 0 && balance < r.price ? ' It may also cost more than players hold: ' + dabs(r.price) + ', against a median of ' + dabs(balance) + '.' : ''),
            r.views * (medConv - r.conv) * 100);
          continue;
        }
        const price = lowerPrice(r.price, balance);
        const held = balance > 0 ? ' Active players hold a median of ' + dabs(balance) + '.' : '';
        const cut = price == null ? '' : pct(1 - price / r.price) + ' lower';
        const near = balance > 0 && balance < r.price && Math.abs(price - balance) <= Math.max(10, balance * 0.1);
        const capped = balance > 0 && balance < r.price && !near;
        add(make('item-expensive-' + r.id, 'items', strong ? 'high' : 'medium',
          r.name + ' is likely too expensive',
          'Only ' + could + ', and ' + conv + '. It costs ' + dabs(r.price) + (r.live ? ' (live price)' : '') + '.' + held,
          price == null ? 'Try a lower price.' : 'Try ' + dabs(price) + (near ? ', near what active players hold.' : capped
            ? ' (' + cut + ', the biggest cut this suggests in one go).' : ', ' + cut + '.'),
          r.views * (medConv - r.conv) * 100, { item: r.id, price }));
      } else if (r.conv < medConv * LIMIT.lowConv && r.affordShare >= LIMIT.canAfford) {
        // most viewers could have bought it right then (for a find item: they'd found it) and didn't
        add(make('item-unloved-' + r.id, 'items', strong ? 'high' : 'medium',
          'People can afford ' + r.name + ' but few buy it',
          could + (r.find ? ' (found, and enough dabs)' : '') + ', but ' + conv + '.',
          "Price isn't the problem: look at how it looks, or how it's shown in the Paint Shop.",
          r.views * (medConv - r.conv) * 100, { item: r.id }));
      } else if (r.conv > medConv * LIMIT.highConv && r.affordShare >= LIMIT.canAfford && r.buys >= MIN.buysToRaise) {
        const price = higherPrice(r.price);
        add(make('item-raise-' + r.id, 'items', 'low',
          r.name + ' sells well: room to raise the price',
          num(r.buys) + ' buys: ' + conv + ', and ' + pct(r.affordShare) + ' of views could buy it right then at ' + dabs(r.price) + '.',
          'Try ' + dabs(price) + ', a little higher, and watch its buys for a week.',
          r.buys, { item: r.id, price }));
      }
    }
  }

  // Few people even look at it: against the median views of its own group, so seasonal items
  // aren't compared with the ones that are always in the shop.
  for (const season of [false, true]) {
    const group = rows.filter((r) => r.season === season);
    const med = median(group.map((r) => r.views));
    if (group.length < MIN.itemsForMedian || !(med >= MIN.groupViews)) continue;
    const vs = ' views, against a median of ' + num(med) + ' for ' + (season ? 'seasonal' : 'regular') + ' items.';
    for (const r of group) {
      if (r.views >= med * LIMIT.lowViews) continue;
      if (r.find) unfound(r, num(r.views) + vs, med - r.views);
      else add(make('item-unseen-' + r.id, 'items', 'low',
        'Few people look at ' + r.name,
        num(r.views) + vs,
        'It may be hard to find or not appealing in the list: try moving it up or showing it off.',
        med - r.views, { item: r.id }));
    }
  }

  // Not found yet: one suggestion per item, or one for the group when three or more of a group share it.
  for (const season of [false, true]) {
    const list = unfoundList.filter((x) => x.r.season === season);
    if (list.length >= 3) {
      const shares = list.map((x) => x.r.affordShare);
      const pricey = list.filter((x) => balance > 0 && x.r.price > balance).length;
      add(make('item-unfound-' + (season ? 'seasonal' : 'regular'), 'items', 'low',
        'Few players have found the ' + (season ? 'seasonal' : 'hidden') + ' items yet',
        list.map((x) => x.r.name).join(', ') + ': only ' + pct(Math.min(...shares)) + ' to ' + pct(Math.max(...shares)) +
          ' of their views could buy them right then (found, and enough dabs).' +
          (pricey ? ' ' + (pricey === list.length ? 'All' : pricey + ' of them') + ' also cost more than active players hold (a median of ' + dabs(balance) + ').' : ''),
        'They have to be found on their canvas before they can be bought. If that should happen more often, make them easier to spot; hold off on price changes until more players have found them.',
        list.reduce((a, x) => a + x.score, 0)));
    } else {
      for (const x of list) {
        add(make('item-unfound-' + x.r.id, 'items', 'low', 'Few players have found ' + x.r.name + ' yet', x.detail,
          'It has to be found ' + where(x.r) + ' before it can be bought. If that should happen more often, make it easier to spot; hold off on price changes until more players have found it.',
          x.score, { item: x.r.id }));
      }
    }
  }
  return out;
}

// ---------------------------------------------------------------- the economy

export function economySuggestions(economy, catalog, progress, overview) {
  const out = [];
  if (!economy || !economy.totals || !catalog) return out;
  const t = economy.totals;
  const active = (progress && progress.active_7d) ?? (overview && overview.wau) ?? 0;
  const bal = t.median_balance;
  if (!(active >= MIN.activePlayers) || bal == null) return out;
  const rows = itemRows(economy, catalog);
  if (!rows.length) return out;
  const cheapest = rows.reduce((a, b) => (b.price < a.price ? b : a));
  const medPrice = median(rows.map((r) => r.price));
  const spend = t.dabs_earned >= MIN.dabsEarned ? ratio(t.dabs_spent, t.dabs_earned) : null;

  if (bal < cheapest.price) {
    out.push(make('economy-poor', 'economy', bal < cheapest.price / 2 ? 'high' : 'medium',
      "Most active players can't afford anything",
      'The ' + num(active) + ' installs active in the last 7 days hold a median of ' + dabs(bal) +
        '; the cheapest item, ' + cheapest.name + ', costs ' + dabs(cheapest.price) + '.',
      'Pay a little more per match, or add a cheaper item so new players can buy something early.',
      (cheapest.price - bal) * 10));
  } else if (bal >= medPrice * LIMIT.hoardPrice && spend != null && spend < LIMIT.hoardSpend) {
    out.push(make('economy-hoard', 'economy', spend < LIMIT.hoardSpend / 2 ? 'high' : 'medium',
      'Players are sitting on dabs',
      'Active players hold a median of ' + dabs(bal) + ', ' + (Math.round((bal / medPrice) * 10) / 10) +
        ' times the typical item price (' + dabs(medPrice) + '), and spent ' + pct(spend) + ' of the ' +
        num(t.dabs_earned) + ' dabs earned.',
      'Give them more to spend on: new items, or lower prices on the items they look at most.',
      bal / medPrice * 100));
  }
  return out;
}

// ---------------------------------------------------------------- the tutorial

// The tutorial in catalog order, with any steps the database saw that aren't in the catalog after.
export function tutorialRows(progress, catalog) {
  const seen = new Map(((progress && progress.tutorial) || []).map((r) => [r.step, r]));
  const rows = (catalog.tutorial || []).map((s) => {
    const r = seen.get(s.id) || {};
    return { step: s.id, name: s.name, known: true, reached: r.reached || 0, stuck: r.stuck || 0 };
  });
  for (const r of (progress && progress.tutorial) || []) {
    if (!rows.some((x) => x.step === r.step)) rows.push({ step: r.step, name: r.step, known: false, reached: r.reached || 0, stuck: r.stuck || 0 });
  }
  return rows;
}

// Drop from each step to the next one in the catalog: installs that reached it but never the next.
export function tutorialDrops(rows) {
  const known = rows.filter((r) => r.known);
  const drops = [];
  for (let i = 0; i + 1 < known.length; i++) {
    const a = known[i], b = known[i + 1];
    const lost = a.reached - b.reached;
    drops.push({ from: a, to: b, lost, rate: a.reached ? lost / a.reached : 0 });
  }
  return drops;
}

export function tutorialSuggestions(progress, catalog) {
  const out = [];
  if (!progress || !catalog) return out;
  const rows = tutorialRows(progress, catalog);

  tutorialDrops(rows)
    .filter((d) => d.from.reached >= MIN.stepReached && d.rate >= LIMIT.stepDrop)
    .sort((a, b) => b.rate - a.rate || b.lost - a.lost)
    .slice(0, 3)
    .forEach((d) => out.push(make('tutorial-drop-' + d.from.step, 'tutorial', d.rate >= 0.3 ? 'high' : 'medium',
      'Big drop after ' + q(d.from.name),
      num(d.lost) + ' of the ' + num(d.from.reached) + ' installs (' + pct(d.rate) + ') that reached ' + d.from.name +
        ' never reached ' + d.to.name + '.',
      'Watch a few new players at this step: it may be unclear or too hard. Make it easier, or explain it better.',
      d.lost)));

  rows
    .filter((r) => r.stuck >= MIN.stuck && r.reached > 0 && r.stuck / r.reached >= LIMIT.stuckShare)
    .sort((a, b) => b.stuck - a.stuck)
    .slice(0, 3)
    .forEach((r) => {
      const share = r.stuck / r.reached;
      out.push(make('tutorial-stuck-' + r.step, 'tutorial', share >= 0.15 ? 'high' : 'medium',
        'Players get stuck at ' + q(r.name),
        num(r.stuck) + ' installs (' + pct(share) + ' of the ' + num(r.reached) + ' that reached it) stopped here: ' +
          "it's their furthest step, they haven't played for 3 days or more, and never finished the basics.",
        'This is where people give up. Look at what this step asks of them and whether they know how to do it.',
        r.stuck));
    });
  return out;
}

// ---------------------------------------------------------------- modes

export function modeSuggestions(modes, catalog, days) {
  const out = [];
  if (!modes || !catalog) return out;
  const label = names(catalog.modes);
  const list = modes.modes || [];
  const total = sum(list.map((m) => m.plays));
  const span = days ? ' in the last ' + num(days) + ' days' : '';

  if (total >= MIN.modePlays) {
    for (const m of catalog.modes || []) {
      const plays = (list.find((x) => x.mode === m.id) || {}).plays || 0;
      const share = plays / total;
      if (share >= LIMIT.rareMode) continue;
      out.push(make('mode-rare-' + m.id, 'modes', 'low',
        m.name + ' is rarely played',
        num(plays) + ' of ' + num(total) + ' plays (' + pct(share) + ')' + span + '.',
        'Make it easier to find or more rewarding, or decide whether it earns its place.',
        (LIMIT.rareMode - share) * 1000));
    }
  }

  // Win rates of the modes played mostly against the CPU, against an even match.
  for (const m of list) {
    const fair = FAIR[m.mode];
    const results = (m.wins || 0) + (m.losses || 0) + (m.draws || 0);
    if (!fair || results < MIN.modeResults || !m.plays) continue;
    const offline = 1 - (m.online || 0) / m.plays;
    if (offline < LIMIT.offline) continue;
    const wr = (m.wins || 0) / results;
    const name = label.get(m.mode) || m.mode;
    const facts = 'Players win ' + pct(wr) + ' of ' + name + ' matches (' + num(m.wins) + ' of ' + num(results) + '); ' +
      pct(offline) + ' of its plays are against the CPU. An even match would be about ' + pct(fair) + '.';
    if (wr >= fair + LIMIT.easyBy) {
      out.push(make('mode-easy-' + m.mode, 'modes', wr >= fair + 0.35 ? 'high' : 'medium',
        name + ' against the CPU may be too easy', facts,
        'Make the CPU a little sharper, or steer players toward a harder difficulty sooner.',
        (wr - fair) * 1000));
    } else if (wr <= fair * LIMIT.hardBy) {
      out.push(make('mode-hard-' + m.mode, 'modes', wr <= fair * 0.3 ? 'high' : 'medium',
        name + ' against the CPU may be too hard', facts,
        'Ease the CPU off a little, or make the easier difficulty the default.',
        (fair - wr) * 1000));
    }
  }
  return out;
}

// ---------------------------------------------------------------- ads

export function adSuggestions(ads, catalog) {
  const out = [];
  if (!ads || !catalog) return out;
  const label = names(catalog.ads);
  for (const p of ads.placements || []) {
    const name = label.get(p.placement) || p.placement;
    if ((p.asked || 0) >= MIN.adAsked) {
      const fail = (p.failed || 0) / p.asked;
      if (fail >= LIMIT.failRate) {
        out.push(make('ads-fail-' + p.placement, 'ads', fail >= 0.3 ? 'high' : 'medium',
          'Ads often fail to load for ' + q(name),
          num(p.failed) + ' of ' + num(p.asked) + ' ad requests (' + pct(fail) + ') failed.',
          "That's a fill problem: check the ad network setup, and what the player gets when no ad is available.",
          p.failed));
      }
    }
    if ((p.shown || 0) >= MIN.adShown) {
      const done = (p.rewarded || 0) / p.shown;
      if (done < LIMIT.completion) {
        out.push(make('ads-quit-' + p.placement, 'ads', done < 0.5 ? 'high' : 'medium',
          'People quit the ad for ' + q(name),
          'Only ' + num(p.rewarded) + ' of ' + num(p.shown) + ' shown ads (' + pct(done) + ') were watched to the end.',
          'The ad may feel too long for what it gives. Make the reward clearer or bigger.',
          p.shown - p.rewarded));
      }
    }
  }
  return out;
}

// ---------------------------------------------------------------- retention

export function retentionSuggestions(overview) {
  const out = [];
  const r = overview && overview.retention;
  if (!r) return out;
  if (r.d1 != null && r.cohort_d1 >= MIN.cohort && r.d1 < LIMIT.d1) {
    out.push(make('retention-d1', 'retention', r.d1 < 0.15 ? 'high' : 'medium',
      'Few new players come back the next day',
      pct(r.d1) + ' of the ' + num(r.cohort_d1) + ' installs that started 2 to 8 days ago came back the day after they started.',
      "Look at the first session: the tutorial's biggest drops, and how the first match feels.",
      (LIMIT.d1 - r.d1) * r.cohort_d1));
  }
  if (r.d7 != null && r.cohort_d7 >= MIN.cohort && r.d7 < LIMIT.d7) {
    out.push(make('retention-d7', 'retention', 'medium',
      'Few players are still around after a week',
      pct(r.d7) + ' of the ' + num(r.cohort_d7) + ' installs that started 8 to 14 days ago came back on day 7.',
      'Give players a reason to return in their first week: goals, rewards or new things to unlock.',
      (LIMIT.d7 - r.d7) * r.cohort_d7));
  }
  return out;
}

// ---------------------------------------------------------------- all of it

export function rank(list) {
  return [...list].sort((a, b) => SEV[a.severity] - SEV[b.severity] || b.score - a.score || a.id.localeCompare(b.id));
}

export function suggest({ overview, progress, modes, economy, ads, catalog, days } = {}) {
  if (!catalog) return [];
  return rank([
    ...retentionSuggestions(overview),
    ...tutorialSuggestions(progress, catalog),
    ...itemSuggestions(economy, catalog),
    ...economySuggestions(economy, catalog, progress, overview),
    ...modeSuggestions(modes, catalog, days),
    ...adSuggestions(ads, catalog),
  ]);
}

// Grouped by area: groups with the most severe suggestion first, each group ranked.
export function group(list) {
  return AREAS.map((a) => ({ ...a, items: rank(list.filter((s) => s.area === a.id)) }))
    .filter((g) => g.items.length)
    .sort((a, b) => SEV[a.items[0].severity] - SEV[b.items[0].severity] ||
      AREAS.findIndex((x) => x.id === a.id) - AREAS.findIndex((x) => x.id === b.id));
}

// The rules in words, for the "How suggestions work" note on the Insights page.
export const RULES = [
  ['Too expensive', 'An item with ' + MIN.itemViews + '+ views where under ' + pct(LIMIT.cantAfford) + ' of views could buy it right then and buys per view are under half the median item\'s. Suggests a lower price near what active players hold, at most ' + pct(LIMIT.maxCut) + ' off, rounded to 5.'],
  ['Not found yet', 'The same for an item that has to be found on its canvas first, or one of those with few views: it may only mean few players have found it, so no price is suggested.'],
  ['Not liked', 'An item with ' + MIN.itemViews + '+ views where ' + pct(LIMIT.canAfford) + '+ of views could buy it right then but buys per view are under half the median item\'s.'],
  ['Hard to find', 'An item with under ' + pct(LIMIT.lowViews) + ' of the median views of its group (regular or seasonal), once that median is ' + MIN.groupViews + '+.'],
  ['Room to raise', 'An item with ' + MIN.buysToRaise + '+ buys, over twice the median buys per view, that ' + pct(LIMIT.canAfford) + '+ of viewers could buy right then. Suggests about ' + pct(LIMIT.raise) + ' more.'],
  ['Balances', 'With ' + MIN.activePlayers + '+ installs active in 7 days: a median balance below the cheapest item, or over twice the median price while players spend under half of what they earn.'],
  ['Tutorial', 'Steps where ' + pct(LIMIT.stepDrop) + '+ of ' + MIN.stepReached + '+ installs never reach the next step, and steps where ' + MIN.stuck + '+ installs (' + pct(LIMIT.stuckShare) + '+) are stuck. Up to three of each.'],
  ['Modes', 'With ' + MIN.modePlays + '+ plays: modes under ' + pct(LIMIT.rareMode) + ' of plays. Modes played mostly offline with ' + MIN.modeResults + '+ results whose win rate is far from an even match.'],
  ['Ads', 'Placements with ' + MIN.adAsked + '+ requests where ' + pct(LIMIT.failRate) + '+ failed, or ' + MIN.adShown + '+ shown where under ' + pct(LIMIT.completion) + ' were watched to the end.'],
  ['Retention', 'Day-1 retention under ' + pct(LIMIT.d1) + ' or day-7 under ' + pct(LIMIT.d7) + ', with ' + MIN.cohort + '+ installs in the cohort.'],
];
