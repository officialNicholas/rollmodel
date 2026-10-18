// In-app purchases. The game sells nothing for real money yet, so this is honestly empty until adm_iap returns data;
// the tiles, charts and table are ready for when it does.

import { h, card, stat, table, empty, grid } from '../ui.js';
import { lineChart, chartCard } from '../charts.js';
import { num, sum, ratio } from '../format.js';
import { rpc } from '../api.js';

const money = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
const usd = (cents) => money.format((Number(cents) || 0) / 100);

export default {
  id: 'purchases', title: 'Purchases', icon: 'purchases', range: true,
  sub: 'Real-money purchases in the app.',
  load: (ctx) => rpc('adm_iap', { p_days: ctx.days }),
  view,
};

function view(d, ctx) {
  d = d || {};
  const products = [...(d.products || [])].sort((a, b) => (b.revenue_cents || 0) - (a.revenue_cents || 0));
  const days = d.days || [];
  const buys = sum(products.map((p) => p.buys));
  const revenue = sum(products.map((p) => p.revenue_cents));
  const span = 'in the last ' + ctx.days + ' days';

  if (!products.length && !sum(days.map((x) => x.buys))) {
    return card(null, { cls: 'empty-card' },
      empty('No purchases yet',
        "The game doesn't sell anything for real money yet. When it does, purchases, revenue per day and each product show up here.", 'purchases'));
  }

  return [
    h('div', { class: 'tiles' },
      stat('Purchases', num(buys), { sub: span }),
      stat('Revenue', usd(revenue), { sub: 'What players paid, as the game reports it' }),
      stat('Average purchase', buys ? usd(revenue / buys) : 'n/a', { sub: 'Revenue per purchase' }),
      stat('Products sold', num(products.filter((p) => p.buys > 0).length), { sub: 'Of ' + num(products.length) + ' with any sales' })),
    grid('two',
      chartCard('Revenue per day', usd(revenue) + ' ' + span, lineChart({
        label: 'Revenue per day', days: days.map((x) => x.day), integer: false,
        series: [{ name: 'Revenue', values: days.map((x) => (x.revenue_cents || 0) / 100), color: 1 }],
        fmt: (v) => money.format(v), tick: (v) => '$' + num(v),
      })),
      chartCard('Purchases per day', num(buys) + ' ' + span, lineChart({
        label: 'Purchases per day', days: days.map((x) => x.day),
        series: [{ name: 'Purchases', values: days.map((x) => x.buys || 0), color: 1 }],
      }))),
    card('Products', { sub: span },
      table([
        { key: 'product', label: 'Product', sort: (p) => p.product, cell: (p) => p.product },
        { key: 'buys', label: 'Purchases', num: true, sort: (p) => p.buys, cell: (p) => num(p.buys) },
        { key: 'rev', label: 'Revenue', num: true, sort: (p) => p.revenue_cents, cell: (p) => usd(p.revenue_cents) },
        { key: 'avg', label: 'Average', num: true, sort: (p) => ratio(p.revenue_cents, p.buys), cell: (p) => (p.buys ? usd(p.revenue_cents / p.buys) : 'n/a') },
        { key: 'share', label: 'Share of revenue', num: true, sort: (p) => ratio(p.revenue_cents, revenue), cell: (p) => (revenue ? Math.round((p.revenue_cents / revenue) * 100) + '%' : 'n/a') },
      ], products, { caption: 'Products', sort: ['rev', 'desc'] })),
  ];
}
