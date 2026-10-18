// Economy: every Paint Shop item with its price (live or default), views, buys and conversion; the price editor;
// the live prices and who set them; dabs earned against spent; balances; Strokes crafts and ad skips; where dabs come from.

import { h, card, stat, grid, table, empty, note, chip, button, field, dialog, actionsRow, errorLine, toast, facts } from '../ui.js';
import { lineChart, chartCard, hbars, legend } from '../charts.js';
import { num, pct, ratio, sum, ago, dateTime, dabs } from '../format.js';
import { rpc, whyText } from '../api.js';
import { catalog, item as catItem, slotName, stageName, strokeName, earnName } from '../catalog.js';

export default {
  id: 'economy', title: 'Economy', icon: 'economy', range: true,
  sub: 'The Paint Shop, prices, and how dabs flow in and out.',
  async load(ctx) {
    const [e, prices] = await Promise.all([rpc('adm_economy', { p_days: ctx.days }), rpc('adm_prices')]);
    return { e: e || {}, prices: Array.isArray(prices) ? prices : [] };
  },
  view,
};

// Every catalog item, plus anything the database knows that the catalog doesn't.
export function itemTable(e, prices) {
  const api = new Map((e.items || []).map((r) => [r.item, r]));
  const live = new Map(prices.map((p) => [p.item, p]));
  const row = (id, it, r) => {
    const lp = r.price ?? (live.get(id) ? live.get(id).price : null);
    return {
      id, it, known: !!it, name: it ? it.name : id, gift: !!(it && it.gift), find: !!(it && it.find), season: !!(it && it.season),
      def: it ? it.price : null, live: lp ?? null, price: lp ?? (it ? it.price : null), change: live.get(id) || null,
      views: r.views || 0, afford: Math.min(r.afford_views || 0, r.views || 0), buys: r.buys || 0, buyers7: r.buyers_7d || 0,
      dabs: r.dabs || 0, last: r.last_buy || null,
    };
  };
  const rows = catalog().items.map((it) => row(it.id, it, api.get(it.id) || {}));
  for (const r of e.items || []) if (!catItem(r.item)) rows.push(row(r.item, null, r));
  return rows;
}

function view({ e, prices }, ctx) {
  const t = e.totals || {};
  const span = 'in the last ' + ctx.days + ' days';
  const rows = itemTable(e, prices);
  const reload = () => ctx.reload();

  const kpis = h('div', { class: 'tiles' },
    stat('Dabs earned', num(t.dabs_earned), { sub: span }),
    stat('Dabs spent', num(t.dabs_spent), { sub: pct(ratio(t.dabs_spent, t.dabs_earned)) + ' of what was earned' }),
    stat('Items bought', num(t.buys), { sub: span }),
    stat('Median balance', t.median_balance == null ? 'n/a' : num(t.median_balance), { sub: 'Dabs held by installs active in 7 days' }));

  const editCell = (r) => {
    if (r.gift) return h('span', { class: 'muted small' }, "Can't be priced");
    if (!r.known) return h('span', { class: 'muted small' }, 'Not in the catalog');
    return button('Edit', { kind: 'ghost small', ico: 'edit', attrs: { 'aria-label': 'Edit the price of ' + r.name },
      onclick: () => priceDialog({ row: r, onDone: reload }) });
  };
  const items = card('Paint Shop items', { sub: 'Views, buys and dabs are ' + span + '. Change a price with Edit: players get it within about a minute.' },
    table([
      { key: 'name', label: 'Item', sort: (r) => r.name, cell: (r) => h('span', { class: 'item-cell' },
        h('span', { class: 'item-name' }, r.name),
        h('span', { class: 'item-meta' }, r.it ? slotName(r.it.slot) + ' · ' + (stageName(r.it.stage) || r.it.stage) : r.id),
        r.find ? chip('Find first', 'find') : null, r.season ? chip('Season') : null, !r.known ? chip('Not in the catalog', 'warn') : null) },
      { key: 'price', label: 'Price', num: true, sort: (r) => (r.gift ? -1 : r.price), cell: (r) => (r.gift
        ? h('span', { class: 'price' }, 'Free', chip('Gift'))
        : h('span', { class: 'price', title: r.def != null ? 'Default ' + num(r.def) : null }, r.price == null ? 'n/a' : num(r.price),
          r.live != null ? chip('Live', 'live') : chip('Default', 'muted'))) },
      { key: 'views', label: 'Views', num: true, sort: (r) => r.views, cell: (r) => num(r.views) },
      { key: 'afford', label: 'Could buy', num: true, sort: (r) => ratio(r.afford, r.views), cell: (r) => pct(ratio(r.afford, r.views)) },
      { key: 'buys', label: 'Buys', num: true, sort: (r) => r.buys, cell: (r) => num(r.buys) },
      { key: 'conv', label: 'Buys per view', num: true, sort: (r) => ratio(r.buys, r.views), cell: (r) => pct(ratio(r.buys, r.views)) },
      { key: 'buyers7', label: 'Buyers in 7 days', num: true, sort: (r) => r.buyers7, cell: (r) => num(r.buyers7) },
      { key: 'dabs', label: 'Dabs', num: true, sort: (r) => r.dabs, cell: (r) => num(r.dabs) },
      { key: 'last', label: 'Last bought', sort: (r) => (r.last ? Date.parse(r.last) : 0), cell: (r) => (r.last ? h('span', { title: dateTime(r.last) }, ago(r.last)) : h('span', { class: 'muted' }, 'Never')) },
      { key: 'edit', label: 'Price', cls: 'act', cell: editCell },
    ], rows, { caption: 'Paint Shop items', cls: 'items-table' }),
    note('Could buy: the share of views where the player could have bought it right then (in stock and enough dabs). ',
      h('b', null, 'Find first'), ' items have to be found on their canvas before they can be bought. Gifts are free and can\'t be priced.'));

  const live = card('Live prices', { sub: 'Prices set here that override the game\'s defaults, and who set them' },
    prices.length ? table([
      { key: 'item', label: 'Item', sort: (p) => (catItem(p.item) || {}).name || p.item, cell: (p) => (catItem(p.item) || {}).name || p.item },
      { key: 'price', label: 'Live price', num: true, sort: (p) => p.price, cell: (p) => num(p.price) },
      { key: 'def', label: 'Default', num: true, cell: (p) => (catItem(p.item) ? num(catItem(p.item).price) : 'n/a') },
      { key: 'chg', label: 'Change', num: true, cell: (p) => change(catItem(p.item) ? catItem(p.item).price : null, p.price) },
      { key: 'at', label: 'Set', sort: (p) => Date.parse(p.updated_at) || 0, cell: (p) => h('span', { title: dateTime(p.updated_at) }, ago(p.updated_at)) },
      { key: 'by', label: 'By', sort: (p) => p.updated_by || '', cell: (p) => p.updated_by || 'n/a' },
      { key: 'clear', label: 'Default', cls: 'act', cell: (p) => {
        const r = rows.find((x) => x.id === p.item);
        return r && r.known && !r.gift ? button('Use default', { kind: 'ghost small', attrs: { 'aria-label': 'Use the default price of ' + r.name },
          onclick: () => priceDialog({ row: r, onDone: reload, clear: true }) }) : null;
      } },
    ], prices, { caption: 'Live prices', sort: ['at', 'desc'] })
      : empty('No live prices', 'Every item uses its default price from the catalog. Prices you set show up here.'));

  const days = (e.days || []).map((d) => d.day);
  const flow = chartCard('Dabs earned and spent', 'Per day (UTC) ' + span, lineChart({
    label: 'Dabs earned and spent per day', days,
    series: [
      { name: 'Earned', values: (e.days || []).map((d) => d.dabs_earned || 0), color: 1 },
      { name: 'Spent', values: (e.days || []).map((d) => d.dabs_spent || 0), color: 2 },
    ],
  }));
  const buys = chartCard('Items bought per day', num(sum((e.days || []).map((d) => d.buys || 0))) + ' ' + span, lineChart({
    label: 'Items bought per day', days, series: [{ name: 'Items bought', values: (e.days || []).map((d) => d.buys || 0), color: 1 }],
  }));

  const earn = [...(e.earn || [])].sort((a, b) => (b.dabs || 0) - (a.dabs || 0));
  const earnTotal = sum(earn.map((x) => x.dabs));
  const sources = card('Where dabs come from', { sub: 'Dabs earned ' + span + ', by source' },
    earnTotal ? hbars(earn.map((x) => ({ label: earnName(x.src), value: x.dabs || 0, note: pct(ratio(x.dabs, earnTotal)) })), { label: 'Dabs earned by source' })
      : empty('No dabs earned yet', 'Matches, Commissions, the Friends board and lessons pay dabs; they show up here.'));

  // Strokes that can be crafted, in catalog order, plus any the catalog doesn't know.
  const sBy = new Map((e.strokes || []).map((x) => [x.stroke, x]));
  const strokeRows = catalog().strokes.filter((x) => x.craft_min != null || sBy.has(x.id)).map((x) => ({ id: x.id, name: x.name, kind: x.kind, ...(sBy.get(x.id) || {}) }));
  for (const x of e.strokes || []) if (!strokeRows.some((r) => r.id === x.stroke)) strokeRows.push({ id: x.stroke, name: strokeName(x.stroke), kind: '', ...x });
  const craftTotal = sum(strokeRows.map((x) => x.crafts || 0));
  const strokes = card('Strokes crafts', { sub: 'Crafts started ' + span + ', and how many were finished early with an ad' },
    craftTotal ? [
      legend([{ name: 'Crafts started', color: 'x' }, { name: 'Skipped with an ad', color: 1 }], 'rect'),
      hbars(strokeRows.map((x) => ({ label: x.name, value: x.crafts || 0, skips: x.skips || 0, note: (x.crafts ? pct(ratio(x.skips || 0, x.crafts)) + ' skipped' : '') })),
        { label: 'Strokes crafts and ad skips', inner: 'skips', innerColor: 1 }),
    ] : empty('No crafts yet', 'Strokes crafts show up here once players start them.'));

  return [
    kpis,
    items,
    live,
    grid('two', flow, buys),
    grid('two', sources, strokes),
  ];
}

function change(from, to) {
  if (from == null || to == null) return 'n/a';
  if (!from) return to ? '+' + num(to) : 'None';
  const r = (to - from) / from;
  return (r > 0 ? '+' : '') + Math.round(r * 100) + '%';
}

// ---------------------------------------------------------------- the price editor

// Edit a price: see the old and new and the default, confirm, then adm_set_price. Or clear the live price.
// row: an itemTable() row. suggested: a price to start from (from Insights).
export function priceDialog({ row, onDone, suggested, clear = false }) {
  const now = row.price;
  const nowText = row.live != null ? dabs(row.live) + ' (live price)' : dabs(row.def) + ' (default)';
  let next = suggested ?? now;

  const save = async (price, api, err, btn) => {
    err.clear();
    btn.disabled = true;
    let res;
    try {
      res = await rpc('adm_set_price', { p_item: row.id, p_price: price });
    } catch (e) {
      btn.disabled = false;
      if (e.kind === 'denied' || e.kind === 'auth') return api.close();
      return err.show(e.kind === 'net' ? "Can't reach the server. Nothing changed; try again." : e.message);
    }
    if (!res || res.ok !== true) { btn.disabled = false; return err.show(whyText(res && res.why)); }
    api.close();
    toast(price == null
      ? row.name + ' is back to its default price, ' + dabs(row.def) + '. Players get it within about a minute.'
      : row.name + ' now costs ' + dabs(price) + '. Players get the new price within about a minute.');
    if (onDone) onDone();
  };

  const editStep = (api) => {
    const input = h('input', { type: 'text', inputmode: 'numeric', autocomplete: 'off', value: String(next ?? ''), class: 'price-input', spellcheck: 'false' });
    const preview = h('p', { class: 'preview', 'aria-live': 'polite' });
    const err = errorLine();
    const parse = () => {
      const v = input.value.trim();
      if (!/^\d{1,6}$/.test(v)) return { error: 'Enter a whole number of dabs.' };
      const n = Number(v);
      if (n > 100000) return { error: 'A price can be at most 100,000 dabs.' };
      return { n };
    };
    const update = () => {
      const p = parse();
      preview.textContent = p.error ? '' : num(now) + ' → ' + num(p.n) + ' dabs' + (now ? ' (' + change(now, p.n) + ')' : '') + (p.n === 0 ? '. 0 makes it free.' : '');
    };
    input.addEventListener('input', () => { err.clear(); update(); });
    update();
    return h('form', { class: 'form', novalidate: true, onsubmit: (ev) => {
      ev.preventDefault();
      const p = parse();
      if (p.error) return err.show(p.error);
      if (p.n === now) return err.show("That's the price it has now.");
      next = p.n;
      api.step(reviewStep);
    } },
    facts([['Now', nowText], ['Default', dabs(row.def)], row.change ? ['Last set', ago(row.change.updated_at) + ' by ' + (row.change.updated_by || 'n/a')] : null]),
    field('New price (dabs)', input, 'A whole number from 0 to 100,000.'),
    preview,
    err.el,
    actionsRow(
      button('Cancel', { kind: 'ghost', onclick: () => api.close() }),
      row.live != null ? button('Use the default (' + num(row.def) + ')', { kind: 'secondary', onclick: () => api.step(clearStep) }) : null,
      button('Review', { kind: 'primary', type: 'submit' })));
  };

  const reviewStep = (api) => {
    const err = errorLine();
    const go = button('Set price', { kind: 'primary', ico: 'check', onclick: () => save(next, api, err, go) });
    return [
      h('p', null, 'Change the price of ', h('b', null, row.name), '?'),
      h('div', { class: 'compare' },
        h('div', null, h('span', { class: 'compare-label' }, 'Now'), h('span', { class: 'compare-value' }, num(now)), h('span', { class: 'compare-sub' }, row.live != null ? 'Live price' : 'Default')),
        h('div', { class: 'compare-arrow', 'aria-hidden': 'true' }, '→'),
        h('div', { class: 'compare-new' }, h('span', { class: 'compare-label' }, 'New'), h('span', { class: 'compare-value' }, num(next)), h('span', { class: 'compare-sub' }, change(now, next))),
        h('div', null, h('span', { class: 'compare-label' }, 'Default'), h('span', { class: 'compare-value' }, num(row.def)), h('span', { class: 'compare-sub' }, 'From the catalog'))),
      h('p', { class: 'hint' }, 'Players get the new price within about a minute.'),
      err.el,
      actionsRow(button('Back', { kind: 'ghost', onclick: () => api.step(editStep) }), go),
    ];
  };

  const clearStep = (api) => {
    const err = errorLine();
    const go = button('Use the default', { kind: 'primary', onclick: () => save(null, api, err, go) });
    return [
      h('p', null, 'Go back to the default price for ', h('b', null, row.name), '?'),
      h('div', { class: 'compare' },
        h('div', null, h('span', { class: 'compare-label' }, 'Now'), h('span', { class: 'compare-value' }, num(row.live)), h('span', { class: 'compare-sub' }, 'Live price')),
        h('div', { class: 'compare-arrow', 'aria-hidden': 'true' }, '→'),
        h('div', { class: 'compare-new' }, h('span', { class: 'compare-label' }, 'Default'), h('span', { class: 'compare-value' }, num(row.def)), h('span', { class: 'compare-sub' }, 'From the catalog'))),
      h('p', { class: 'hint' }, 'This removes the live price. Players get the default within about a minute.'),
      err.el,
      actionsRow(button(clear ? 'Cancel' : 'Back', { kind: 'ghost', onclick: () => (clear ? api.close() : api.step(editStep)) }), go),
    ];
  };

  return dialog('Price of ' + row.name, clear ? clearStep : editStep);
}
