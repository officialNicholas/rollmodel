// Players: ranks (latest rank per install, all and active), the median rank, and the tutorial funnel in catalog
// order with where people drop off and get stuck.

import { h, card, stat, note, empty, chip, icon } from '../ui.js';
import { columnChart, chartCard } from '../charts.js';
import { num, pct, sum } from '../format.js';
import { rpc } from '../api.js';
import { catalog, tutorialIds } from '../catalog.js';
import { tutorialRows, tutorialDrops, MIN, LIMIT } from '../suggest.js';

export default {
  id: 'players', title: 'Players', icon: 'players', range: false,
  sub: 'How far players get: their ranks, and the tutorial step by step.',
  load: () => rpc('adm_progress', { p_steps: tutorialIds() }),
  view,
};

function view(p) {
  p = p || {};
  const ranks = (p.ranks || []).filter((r) => r.rank >= 1).sort((a, b) => a.rank - b.rank);
  const total = sum(ranks.map((r) => r.players));
  const active = sum(ranks.map((r) => r.active));
  const rows = tutorialRows(p, catalog());
  const first = rows.length ? rows[0].reached : 0;

  const kpis = h('div', { class: 'tiles' },
    stat('Active in 7 days', num(p.active_7d), { sub: 'Installs heard from' }),
    stat('Median rank', p.median_rank == null ? 'n/a' : num(p.median_rank), { sub: 'Of installs seen in 30 days' }),
    stat('Finished the basics', pct(p.done_pct ?? null), { sub: p.done_pct == null ? 'No installs yet' : 'Of all installs reached "Basics complete"' }),
    stat('Installs with a rank', num(total), { sub: num(active) + ' seen in the last 30 days' }));

  // Ranks 1..50 (50 means 50 and up); every rank up to the highest seen, so gaps show as gaps.
  const top = ranks.length ? Math.max(...ranks.map((r) => r.rank)) : 0;
  const cats = Array.from({ length: Math.max(top, 0) }, (_, i) => i + 1);
  const by = new Map(ranks.map((r) => [r.rank, r]));
  const rankName = (r, long) => (long ? 'Rank ' : '') + (r >= 50 ? '50+' : String(r));
  const rankCard = ranks.length
    ? chartCard('Ranks', 'Installs by their latest rank. Grey is every install, the colour is those seen in the last 30 days.',
      columnChart({
        label: 'Installs by rank', cats, catHead: 'Rank', catName: rankName,
        series: [
          { name: 'All installs', values: cats.map((c) => (by.get(c) || {}).players || 0), color: 'x' },
          { name: 'Seen in 30 days', values: cats.map((c) => (by.get(c) || {}).active || 0), color: 1 },
        ],
      }))
    : card('Ranks', { sub: 'Installs by their latest rank' }, empty('No ranks yet', 'Each install shows up here once it reaches its first rank.'));

  return [kpis, rankCard, funnel(rows, first, p.done_pct)];
}

// The tutorial in catalog order: reached, the share of the first step, lost before the next step, and stuck.
function funnel(rows, first, donePct) {
  if (!rows.length) return card('Tutorial', null, empty('No tutorial steps', 'The catalog lists no tutorial steps.'));
  const drops = tutorialDrops(rows);
  const dropBy = new Map(drops.map((d) => [d.from.step, d]));
  const big = drops.filter((d) => d.from.reached >= MIN.stepReached && d.rate >= LIMIT.stepDrop)
    .sort((a, b) => b.rate - a.rate || b.lost - a.lost).slice(0, 3);
  const bigSet = new Set(big.map((d) => d.from.step));
  const stuckTop = Math.max(0, ...rows.map((r) => r.stuck));

  const callout = big.length
    ? h('div', { class: 'callout' },
      h('p', { class: 'callout-title' }, icon('alert'), 'Biggest drop-offs'),
      h('ol', { class: 'callout-list' }, big.map((d) => h('li', null,
        h('b', null, pct(d.rate)), ' never got from ', h('span', { class: 'quote' }, d.from.name), ' to ', h('span', { class: 'quote' }, d.to.name),
        h('span', { class: 'muted' }, ' (' + num(d.lost) + ' of ' + num(d.from.reached) + ')')))))
    : null;

  const head = h('tr', null, ['#', 'Step', 'Reached', 'Of the first step', 'Lost before the next step', 'Stuck here'].map((t, i) =>
    h('th', { scope: 'col', class: i >= 2 ? 'num' : '' }, t)));
  const body = rows.map((r, i) => {
    const d = dropBy.get(r.step);
    const share = first ? r.reached / first : 0;
    const bar = h('span', { class: 'fbar-fill c1' });
    bar.style.width = (share > 0 ? Math.max(share * 100, 0.6) : 0) + '%';
    return h('tr', { class: bigSet.has(r.step) ? 'flag' : null },
      h('td', { class: 'muted num-left' }, String(i + 1)),
      h('th', { scope: 'row', class: 'step' }, r.name, r.known ? null : chip('Not in the catalog', 'warn'),
        bigSet.has(r.step) ? chip('Big drop', 'alert') : null),
      h('td', { class: 'num reached' }, h('span', { class: 'fbar', 'aria-hidden': 'true' }, bar), h('span', { class: 'fnum' }, num(r.reached))),
      h('td', { class: 'num' }, first ? pct(share) : ''),
      h('td', { class: 'num' }, !first || !d || !r.known ? '' : d.lost > 0 ? num(d.lost) + ' (' + pct(d.rate) + ')' : d.lost < 0 ? 'None (+' + num(-d.lost) + ')' : 'None'),
      h('td', { class: 'num' + (r.stuck && r.stuck === stuckTop ? ' strong' : '') }, r.stuck ? num(r.stuck) : '0'));
  });

  return card('Tutorial', { sub: first ? 'Every step in the order the game teaches it. ' + pct(donePct ?? null) + ' of installs finished the basics.' : 'Every step in the order the game teaches it' },
    first ? callout : empty('Nobody has started the tutorial yet', 'Each step fills in as installs reach it.'),
    h('div', { class: 'tablewrap', tabindex: '0', role: 'region', 'aria-label': 'Tutorial steps' },
      h('table', { class: 'tbl funnel' }, h('caption', { class: 'sr-only' }, 'Tutorial steps, reached and stuck'), h('thead', null, head), h('tbody', null, body))),
    note('Reached: installs that ever got to the step. Stuck: installs whose furthest step it is, that haven\'t been seen for 3 days or more and never finished the basics.'));
}
