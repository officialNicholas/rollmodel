// Audit log: every change made from the dashboard (adm_audit), newest first, in plain words.

import { h, card, table, empty, field } from '../ui.js';
import { num, dateTime, ago, UUID } from '../format.js';
import { rpc } from '../api.js';
import { priced } from '../catalog.js';

export default {
  id: 'audit', title: 'Audit log', icon: 'audit', range: false,
  sub: 'Every change made from the dashboard, newest first.',
  load: (ctx) => rpc('adm_audit', { p_limit: limitOf(ctx) }),
  view,
};

const LIMITS = [100, 500];
const limitOf = (ctx) => (LIMITS.includes(Number(ctx.route.q.get('n'))) ? Number(ctx.route.q.get('n')) : 100);

export const ACTIONS = {
  set_price: 'Changed a price',
  set_password: 'Reset a password',
  signout: 'Signed a player out everywhere',
  delete_player: 'Deleted an account',
  email_reset: 'Emailed a reset link',
};
export const actionText = (a) => ACTIONS[a] || String(a || 'Unknown');

const isObj = (v) => v && typeof v === 'object' && !Array.isArray(v);
const priceText = (v, def) => (v == null ? 'the default' + (def != null ? ' (' + num(def) + ')' : '') : num(v));

// What happened, in a sentence: never HTML, every value from the server goes in as text.
export function detailText(row) {
  const d = isObj(row.detail) ? row.detail : {};
  const who = d.name || (row.target && !UUID.test(row.target) ? row.target : null);
  switch (row.action) {
    case 'set_price': {
      const it = priced(row.target);
      const def = it ? it.price : null;
      return (it ? it.name : row.target || 'An item') + ': ' + priceText(d.from, def) + ' → ' + priceText(d.to, def);
    }
    case 'set_password': return (who ? who + ': ' : '') + 'new password, signed out everywhere';
    case 'email_reset': return (who ? who + ': ' : '') + (d.sent === false ? "not sent (the game's email is off)" : 'reset link sent to their confirmed email');
    case 'signout': return (who ? who + ': ' : '') + (d.sessions != null ? num(d.sessions) + (Number(d.sessions) === 1 ? ' session' : ' sessions') + ' ended' : 'signed out');
    case 'delete_player': return (who || 'A player') + (d.id || row.target ? ' (' + (d.id || row.target) + ')' : '');
    default: {
      const parts = Object.entries(d).slice(0, 6).map(([k, v]) => k + ': ' + (isObj(v) || Array.isArray(v) ? JSON.stringify(v).slice(0, 60) : String(v)));
      return parts.join(', ') || (row.target ? String(row.target) : '');
    }
  }
}

// A link to the player when the target is a user id (it may since have been deleted).
export function targetCell(row) {
  if (row.action !== 'set_price' && row.target && UUID.test(row.target) && row.action !== 'delete_player') {
    return h('a', { href: '#support/' + row.target }, detailText(row));
  }
  return detailText(row);
}

function view(rows, ctx) {
  rows = Array.isArray(rows) ? rows : [];
  const limit = limitOf(ctx);
  let filter = '';
  const box = h('div');
  const draw = () => {
    const list = filter ? rows.filter((r) => r.action === filter) : rows;
    box.replaceChildren(list.length || rows.length
      ? table([
        { key: 'at', label: 'When', cell: (r) => h('span', { title: dateTime(r.at) }, dateTime(r.at), h('small', { class: 'muted block' }, ago(r.at))) },
        { key: 'admin', label: 'Who', cell: (r) => r.admin || 'n/a' },
        { key: 'action', label: 'What', cell: (r) => actionText(r.action) },
        { key: 'detail', label: 'Details', cls: 'wrapcell', cell: targetCell },
      ], list, { caption: 'Audit log', empty: 'No changes of this kind in the last ' + num(limit) + '.' })
      : empty('No changes yet', 'Price changes, password resets, sign-outs and deleted accounts show up here, with who did them and when.', 'audit'));
  };
  const kind = h('select', { onchange: () => { filter = kind.value; draw(); } },
    h('option', { value: '' }, 'All changes'), Object.entries(ACTIONS).map(([k, v]) => h('option', { value: k }, v)));
  const count = h('select', { onchange: () => ctx.go('#audit?n=' + count.value) },
    LIMITS.map((n) => h('option', { value: String(n), selected: n === limit }, 'Last ' + n)));
  draw();
  return card(null, { cls: 'audit' },
    rows.length ? h('div', { class: 'toolbar' }, field('Show', kind), field('How many', count),
      h('p', { class: 'toolbar-note' }, num(rows.length) + (rows.length === 1 ? ' entry' : ' entries'))) : null,
    box);
}
