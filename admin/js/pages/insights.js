// Insights: what to change, from js/suggest.js. Grouped by area and ranked, each with the numbers behind it.

import { h, card, empty, button, severity, icon, note } from '../ui.js';
import { num } from '../format.js';
import { rpc } from '../api.js';
import { catalog, tutorialIds } from '../catalog.js';
import { suggest, group, RULES } from '../suggest.js';
import { priceDialog, itemTable } from './economy.js';

export default {
  id: 'insights', title: 'Insights', icon: 'insights', range: true,
  sub: 'What to change, worked out from the numbers on the other pages.',
  async load(ctx) {
    const days = { p_days: ctx.days };
    const [overview, progress, modes, economy, ads, prices] = await Promise.all([
      rpc('adm_overview', days), rpc('adm_progress', { p_steps: tutorialIds() }), rpc('adm_modes', days),
      rpc('adm_economy', days), rpc('adm_ads', days), rpc('adm_prices'),
    ]);
    return { overview, progress, modes, economy: economy || {}, ads, prices: Array.isArray(prices) ? prices : [] };
  },
  view,
};

const PAGE_NAMES = { overview: 'Overview', players: 'Players', economy: 'Economy', modes: 'Modes', ads: 'Ads' };

function view(d, ctx) {
  const list = suggest({ ...d, catalog: catalog(), days: ctx.days });
  const groups = group(list);
  const count = (sev) => list.filter((x) => x.severity === sev).length;
  const how = h('details', { class: 'how' },
    h('summary', null, 'How suggestions work'),
    h('p', null, 'Each suggestion comes from a simple rule over the last ' + ctx.days + ' days, and only once there\'s enough data, so a quiet launch stays quiet.'),
    h('dl', { class: 'rules' }, RULES.map(([k, v]) => h('div', null, h('dt', null, k), h('dd', null, v)))));

  if (!list.length) {
    return [
      card(null, { cls: 'empty-card' }, empty('Nothing stands out', 'No rule found anything worth changing in the last ' + ctx.days +
        ' days. Rules wait for enough data first, so this is normal soon after launch.', 'insights')),
      how,
    ];
  }

  const rows = itemTable(d.economy, d.prices);
  const summary = h('p', { class: 'summary' },
    h('b', null, num(list.length) + (list.length === 1 ? ' suggestion' : ' suggestions')), ': ',
    [['high', 'high'], ['medium', 'medium'], ['low', 'low']].filter(([s]) => count(s)).map(([s, w], i) =>
      [i ? ', ' : '', num(count(s)) + ' ' + w]), '. Highest first.');

  return [
    summary,
    groups.map((g) => card(g.label, {
      actions: h('a', { class: 'btn ghost small', href: '#' + g.page }, 'Open ' + PAGE_NAMES[g.page], icon('back', 'flip')),
      cls: 'sugg-group',
    }, h('ul', { class: 'suggs' }, g.items.map((s) => h('li', { class: 'sugg sev-' + s.severity, id: 's-' + s.id },
      h('div', { class: 'sugg-head' }, severity(s.severity), h('h3', { class: 'sugg-title' }, s.title)),
      h('p', { class: 'sugg-detail' }, s.detail),
      h('p', { class: 'sugg-action' }, h('span', { class: 'sugg-try' }, 'Next step: '), s.action),
      s.item && s.price != null && rows.find((r) => r.id === s.item)
        ? button('Set price to ' + num(s.price), { kind: 'secondary small', ico: 'edit',
          onclick: () => priceDialog({ row: rows.find((r) => r.id === s.item), suggested: s.price, onDone: () => ctx.reload() }) })
        : null))))),
    how,
    note('Suggestions point at where to look. Check the numbers on the page they link to before changing anything.'),
  ];
}
