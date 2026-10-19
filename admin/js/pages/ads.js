// Ads: the rewarded ads per placement (asked, shown, rewarded, failed, fill and completion), and per day.

import { h, card, stat, table, empty, note, rate } from '../ui.js';
import { lineChart, chartCard } from '../charts.js';
import { num, pct, ratio, sum } from '../format.js';
import { rpc } from '../api.js';
import { catalog, adName } from '../catalog.js';

export default {
  id: 'ads', title: 'Ads', icon: 'ads', range: true,
  sub: 'Rewarded ads: how often they load and get watched to the end.',
  load: (ctx) => rpc('adm_ads', { p_days: ctx.days }),
  view,
};

function view(a, ctx) {
  a = a || {};
  const by = new Map((a.placements || []).map((p) => [p.placement, p]));
  const ids = [...catalog().ads.map((x) => x.id), ...(a.placements || []).map((p) => p.placement).filter((id) => !catalog().ads.some((x) => x.id === id))];
  const rows = ids.map((id) => ({ id, name: adName(id), asked: 0, shown: 0, rewarded: 0, failed: 0, ...(by.get(id) || {}) }));
  const tot = (k) => sum(rows.map((r) => r[k]));
  const asked = tot('asked'), shown = tot('shown'), rewarded = tot('rewarded'), failed = tot('failed');
  const span = 'in the last ' + ctx.days + ' days';

  const kpis = h('div', { class: 'tiles' },
    stat('Asked for', num(asked), { sub: 'Players who tapped to watch ' + span }),
    stat('Shown', num(shown), { sub: 'Fill rate ' + pct(ratio(shown, asked)) }),
    stat('Watched to the end', num(rewarded), { sub: 'Completion ' + pct(ratio(rewarded, shown)) }),
    stat('Failed', num(failed), { sub: pct(ratio(failed, asked)) + ' of requests' }));

  const placements = card('Per placement', { sub: 'Fill rate: shown out of asked. Completion: watched to the end out of shown.' },
    table([
      { key: 'name', label: 'Placement', sort: (r) => r.name },
      { key: 'asked', label: 'Asked', num: true, sort: (r) => r.asked, cell: (r) => num(r.asked) },
      { key: 'shown', label: 'Shown', num: true, sort: (r) => r.shown, cell: (r) => num(r.shown) },
      { key: 'rewarded', label: 'Rewarded', num: true, sort: (r) => r.rewarded, cell: (r) => num(r.rewarded) },
      { key: 'failed', label: 'Failed', num: true, sort: (r) => r.failed, cell: (r) => num(r.failed) },
      { key: 'fill', label: 'Fill rate', num: true, sort: (r) => ratio(r.shown, r.asked), cell: (r) => rate(ratio(r.shown, r.asked)) },
      { key: 'done', label: 'Completion', num: true, sort: (r) => ratio(r.rewarded, r.shown), cell: (r) => rate(ratio(r.rewarded, r.shown)) },
    ], rows, { caption: 'Ads per placement' }),
    asked ? null : empty('No ads yet', 'Rewarded ads only run in the iPhone app. They show up here once players watch them.'));

  const days = (a.days || []).map((d) => d.day);
  const col = (k) => (a.days || []).map((d) => d[k] || 0);
  const perDay = chartCard('Ads per day', 'Every placement together, per day (UTC)', lineChart({
    label: 'Ads per day', days, area: false,
    series: [
      { name: 'Asked', values: col('asked'), color: 1 },
      { name: 'Shown', values: col('shown'), color: 2 },
      { name: 'Rewarded', values: col('rewarded'), color: 3 },
      { name: 'Failed', values: col('failed'), color: 4 },
    ],
  }));

  return [kpis, placements, perDay, note('These are rewarded ads only: the game has no other ads, and the web version shows none.')];
}
