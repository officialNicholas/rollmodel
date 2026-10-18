// Building the page. Everything goes through h() and textContent: nothing from the server is ever parsed as HTML.
// The Content-Security-Policy forbids inline styles, so h() sets styles through the CSSOM (el.style), never an attribute.

import { pct } from './format.js';

const SVG = 'http://www.w3.org/2000/svg';
const PROPS = new Set(['value', 'checked', 'disabled', 'hidden', 'readOnly', 'required', 'selected', 'open', 'multiple']);

function apply(el, props, svg) {
  for (const [k, v] of Object.entries(props || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') el.setAttribute('class', v);
    else if (k === 'text') el.textContent = v;
    else if (k === 'style') {
      for (const [p, val] of Object.entries(v)) p.startsWith('--') ? el.style.setProperty(p, val) : (el.style[p] = val);
    } else if (k === 'dataset') Object.assign(el.dataset, v);
    else if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
    else if (!svg && PROPS.has(k)) el[k] = v;
    else if (/^on/i.test(k) || k === 'innerHTML' || k === 'outerHTML') throw new Error('h(): ' + k + ' is not allowed');
    else {
      if ((k === 'href' || k === 'src') && !/^(#|data:image\/|https?:|\.|[a-z0-9_-]+\.)/i.test(String(v))) throw new Error('h(): unsafe ' + k);
      el.setAttribute(k, v === true ? '' : String(v));
    }
  }
}

function add(el, kids) {
  for (const k of kids.flat(Infinity)) {
    if (k == null || k === false || k === true) continue;
    el.append(k instanceof Node ? k : document.createTextNode(String(k)));
  }
}

// h('p', { class: 'note' }, 'Hello ', h('b', null, name))
export function h(tag, props, ...kids) {
  const el = document.createElement(tag);
  apply(el, props, false);
  add(el, kids);
  return el;
}

// the same for SVG elements
export function s(tag, props, ...kids) {
  const el = document.createElementNS(SVG, tag);
  apply(el, props, true);
  add(el, kids);
  return el;
}

export const $ = (sel, root = document) => root.querySelector(sel);

// A share for a table cell, or a quiet "n/a" when there's nothing to divide by.
export const rate = (x) => (x == null ? h('span', { class: 'muted' }, 'n/a') : pct(x));
export const mount = (el, ...kids) => { el.replaceChildren(); add(el, kids); return el; };

// ---------------------------------------------------------------- messages

// One polite live region for screen readers, plus a visible toast.
export function announce(msg) {
  const live = document.getElementById('live');
  if (!live) return;
  live.textContent = '';
  setTimeout(() => { live.textContent = msg; }, 30);
}

export function toast(msg, tone = 'ok') {
  let box = document.getElementById('toasts');
  if (!box) { box = h('div', { id: 'toasts', class: 'toasts' }); document.body.append(box); }
  const t = h('div', { class: 'toast ' + tone, role: tone === 'error' ? 'alert' : 'status' },
    icon(tone === 'error' ? 'alert' : 'check'), h('span', null, msg),
    h('button', { class: 'toast-x', type: 'button', 'aria-label': 'Dismiss', onclick: () => t.remove() }, icon('x')));
  box.append(t);
  setTimeout(() => t.remove(), tone === 'error' ? 12000 : 7000);
}

// ---------------------------------------------------------------- icons (24px line icons)

const ICONS = {
  overview: 'M4 13h6V4H4zM14 20h6v-9h-6zM4 20h6v-4H4zM14 4v4h6V4z',
  players: 'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM2 21v-1a7 7 0 0 1 14 0v1M16 3.5a4 4 0 0 1 0 7.5M22 21v-1a7 7 0 0 0-4-6.3',
  modes: 'M6 9h4M8 7v4M15 10h.01M18 8h.01M7 4h10a5 5 0 0 1 4.9 6l-1 5a3 3 0 0 1-5.2 1.4L14 15h-4l-1.7 1.4A3 3 0 0 1 3.1 15l-1-5A5 5 0 0 1 7 4z',
  economy: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM15 9.5c-.5-1-1.6-1.5-3-1.5-1.7 0-3 .8-3 2s1.3 1.7 3 2 3 .8 3 2-1.3 2-3 2c-1.4 0-2.5-.5-3-1.5M12 6.5v1.5M12 16v1.5',
  ads: 'M3 5h18v14H3zM10 9l5 3-5 3z',
  purchases: 'M6 7h12l1 14H5zM9 10V6a3 3 0 0 1 6 0v4',
  insights: 'M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0 0 12 3z',
  support: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4',
  audit: 'M8 6h12M8 12h12M8 18h12M4 6h.01M4 12h.01M4 18h.01',
  check: 'M5 12.5l4.5 4.5L19 7.5',
  alert: 'M12 8v5M12 16.5h.01M10.3 3.8L2.4 17.5A2 2 0 0 0 4.1 20.5h15.8a2 2 0 0 0 1.7-3L13.7 3.8a2 2 0 0 0-3.4 0z',
  info: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 11v6M12 7.5h.01',
  x: 'M6 6l12 12M18 6L6 18',
  menu: 'M4 7h16M4 12h16M4 17h16',
  reload: 'M20 12a8 8 0 1 1-2.3-5.7M20 4v4.5h-4.5',
  copy: 'M9 9h11v11H9zM5 15H4V4h11v1',
  back: 'M15 6l-6 6 6 6',
  out: 'M15 4h4v16h-4M10 8l-4 4 4 4M6 12h10',
  lock: 'M6 11h12v9H6zM9 11V8a3 3 0 0 1 6 0v3',
  user: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM5 21a7 7 0 0 1 14 0',
  trash: 'M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3',
  key: 'M14.5 4a5.5 5.5 0 1 0 1.9 10.7L19 17.3V20h3v-3l-5-5.1A5.5 5.5 0 0 0 14.5 4zM15 8.5h.01',
  edit: 'M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4',
  table: 'M3 5h18v14H3zM3 10h18M3 15h18M9 5v14',
  chart: 'M4 4v16h16M8 16v-5M12 16V8M16 16v-3',
  dot: 'M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z',
};

export function icon(name, cls = '') {
  return s('svg', { class: 'icon ' + cls, viewBox: '0 0 24 24', 'aria-hidden': 'true', focusable: 'false' },
    s('path', { d: ICONS[name] || ICONS.dot }));
}

// The brand mark: a red paint blob and the name in heavy caps.
export function brand(sub = 'Admin') {
  return h('div', { class: 'brand' },
    s('svg', { class: 'brand-blob', viewBox: '0 0 32 32', 'aria-hidden': 'true', focusable: 'false' },
      s('path', { d: 'M16 3c6.6 0 12 4.7 12 11.2 0 4.6-2.7 7.3-5.6 8.6-1.6.7-2 1.6-2 3.2 0 1.8-1.3 3-3 3s-2.6-1.2-2.6-2.8c0-1.4-.8-2.2-2.4-2.4C6.5 23.1 4 19.6 4 14.6 4 8 9.4 3 16 3z' }),
      s('circle', { cx: '25.5', cy: '27', r: '2.2' })),
    h('span', { class: 'brand-name' }, 'Roll Model'),
    sub ? h('span', { class: 'brand-sub' }, sub) : null);
}

// ---------------------------------------------------------------- building blocks

export function button(label, { kind = '', onclick, type = 'button', ico, disabled, attrs } = {}) {
  return h('button', { class: 'btn ' + kind, type, onclick, disabled, ...attrs }, ico ? icon(ico) : null, h('span', null, label));
}

// A labelled field: the label is always visible and tied to the input.
let uid = 0;
export function field(label, input, hint) {
  const id = input.id || (input.id = 'f' + ++uid);
  const hintEl = hint ? h('p', { class: 'hint', id: id + '-hint' }, hint) : null;
  if (hintEl) input.setAttribute('aria-describedby', id + '-hint');
  return h('div', { class: 'field' }, h('label', { for: id }, label), input, hintEl);
}

export function card(title, opts, ...body) {
  const { sub, actions, cls = '', id, level = 'h2' } = opts || {};
  return h('section', { class: 'card ' + cls, id },
    title || actions ? h('header', { class: 'card-head' },
      h('div', { class: 'card-titles' }, title ? h(level, { class: 'card-title' }, title) : null, sub ? h('p', { class: 'card-sub' }, sub) : null),
      actions ? h('div', { class: 'card-actions' }, actions) : null) : null,
    body);
}

// A stat tile: label, value, and an optional line under it. Big numbers keep proportional figures.
export function stat(label, value, { sub, hero, tone, title } = {}) {
  return h('div', { class: 'stat' + (hero ? ' hero' : '') + (tone ? ' ' + tone : ''), title },
    h('div', { class: 'stat-label' }, label),
    h('div', { class: 'stat-value' }, value),
    sub ? h('div', { class: 'stat-sub' }, sub) : null);
}

export const tiles = (...kids) => h('div', { class: 'tiles' }, kids);
export const grid = (cls, ...kids) => h('div', { class: 'grid ' + cls }, kids);

// An intentional empty state: what it is, why it's empty, and what will show up.
export function empty(title, body, ico = 'info') {
  return h('div', { class: 'empty' }, icon(ico, 'empty-icon'), h('p', { class: 'empty-title' }, title), body ? h('p', { class: 'empty-body' }, body) : null);
}

// A failed load: a plain sentence and a retry.
export function failure(err, retry) {
  const net = err && err.kind === 'net';
  return h('div', { class: 'failure', role: 'alert' },
    icon('alert', 'failure-icon'),
    h('div', null,
      h('p', { class: 'failure-title' }, net ? "Can't reach the server" : "This didn't load"),
      h('p', { class: 'failure-body' }, net ? 'Check your connection, then try again.' : (err && err.message) || 'Something went wrong. Try again.'),
      retry ? button('Try again', { kind: 'secondary', ico: 'reload', onclick: retry }) : null));
}

export function loading(label = 'Loading') {
  return h('div', { class: 'loading', role: 'status' }, h('span', { class: 'spinner', 'aria-hidden': 'true' }), h('span', null, label));
}

// Severity: always an icon and a word, never colour alone.
export function severity(sev) {
  const words = { high: 'High', medium: 'Medium', low: 'Low' };
  const ico = { high: 'alert', medium: 'info', low: 'dot' };
  return h('span', { class: 'sev sev-' + sev }, icon(ico[sev] || 'dot'), words[sev] || sev);
}

export function chip(text, tone = '') {
  return h('span', { class: 'chip ' + tone }, text);
}

// Key/value list for a record (profile, account details...).
export function facts(rows) {
  return h('dl', { class: 'facts' }, rows.filter(Boolean).map(([k, v]) => h('div', { class: 'fact' }, h('dt', null, k), h('dd', null, v))));
}

// ---------------------------------------------------------------- tables

// cols: [{ key, label, num, cell(row) -> node|string, sort(row) -> value, cls }]
// Sortable headers are buttons with aria-sort on the th. Wide tables scroll inside their own box, never the page.
export function table(cols, rows, { empty: emptyMsg = 'Nothing here yet.', sort, caption, cls = '', rowClass } = {}) {
  let by = sort ? sort[0] : null;
  let dir = sort ? sort[1] : 'desc';
  const tbody = h('tbody');
  const ths = cols.map((c) => {
    const th = h('th', { scope: 'col', class: (c.num ? 'num ' : '') + (c.cls || '') });
    if (c.sort) {
      th.append(h('button', { type: 'button', class: 'th-sort', onclick: () => { dir = by === c.key && dir === 'desc' ? 'asc' : 'desc'; by = c.key; draw(); } },
        h('span', null, c.label), h('span', { class: 'th-arrow', 'aria-hidden': 'true' })));
    } else if (c.hideLabel) th.append(h('span', { class: 'sr-only' }, c.label));
    else th.textContent = c.label;
    return th;
  });
  function draw() {
    let list = rows;
    const col = cols.find((c) => c.key === by);
    if (col && col.sort) {
      list = [...rows].sort((a, b) => {
        const x = col.sort(a), y = col.sort(b);
        const r = typeof x === 'string' || typeof y === 'string' ? String(x ?? '').localeCompare(String(y ?? '')) : (x ?? -Infinity) - (y ?? -Infinity);
        return dir === 'asc' ? r : -r;
      });
    }
    cols.forEach((c, i) => {
      if (c.sort) ths[i].setAttribute('aria-sort', c.key === by ? (dir === 'asc' ? 'ascending' : 'descending') : 'none');
    });
    mount(tbody, list.length ? list.map((r) => h('tr', { class: rowClass ? rowClass(r) : null },
      cols.map((c, i) => {
        const v = c.cell ? c.cell(r) : r[c.key];
        return h(i === 0 ? 'th' : 'td', { class: (c.num ? 'num ' : '') + (c.cls || ''), scope: i === 0 ? 'row' : null }, v);
      })))
      : h('tr', null, h('td', { class: 'table-empty', colspan: String(cols.length) }, emptyMsg)));
  }
  draw();
  return h('div', { class: 'tablewrap ' + cls, tabindex: '0', role: 'region', 'aria-label': caption || 'Table' },
    h('table', { class: 'tbl' }, caption ? h('caption', { class: 'sr-only' }, caption) : null, h('thead', null, h('tr', null, ths)), tbody));
}

// ---------------------------------------------------------------- dialogs

// A modal <dialog>: focus stays inside, Escape closes it. render(api) returns the body and is called again by api.step().
export function dialog(title, render, { danger = false, onClose, wide = false } = {}) {
  const head = h('h2', { class: 'dlg-title', id: 'dlg' + ++uid }, title);
  const body = h('div', { class: 'dlg-body' });
  const dlg = h('dialog', { class: 'dlg' + (danger ? ' danger' : '') + (wide ? ' wide' : ''), 'aria-labelledby': head.id },
    h('div', { class: 'dlg-head' }, head,
      h('button', { type: 'button', class: 'icon-btn', 'aria-label': 'Close', onclick: () => api.close() }, icon('x'))),
    body);
  const api = {
    el: dlg,
    body,
    title: (t) => { head.textContent = t; },
    step: (fn) => {
      mount(body, fn(api));
      const first = body.querySelector('[autofocus], input:not([type=hidden]):not([disabled]), textarea, select, button:not([disabled])');
      if (first) first.focus();
    },
    close: () => { if (dlg.open) dlg.close(); },
  };
  const before = document.activeElement;
  dlg.addEventListener('close', () => {
    dlg.remove();
    if (before && before.isConnected && typeof before.focus === 'function') before.focus();
    if (onClose) onClose();
  });
  document.body.append(dlg);
  dlg.showModal();
  api.step(render);
  return api;
}

export function actionsRow(...kids) {
  return h('div', { class: 'dlg-actions' }, kids);
}

// A line of error text inside a dialog or form, announced as it appears.
export function errorLine() {
  const el = h('p', { class: 'form-error', role: 'alert', hidden: true });
  return {
    el,
    show: (msg) => { el.textContent = msg; el.hidden = !msg; },
    clear: () => { el.textContent = ''; el.hidden = true; },
  };
}

// ---------------------------------------------------------------- copy

export function copyButton(getText, label = 'Copy') {
  const b = button(label, {
    kind: 'secondary small', ico: 'copy',
    onclick: async () => {
      const text = getText();
      let ok = false;
      try { await navigator.clipboard.writeText(text); ok = true; } catch { ok = false; }
      b.querySelector('span').textContent = ok ? 'Copied' : 'Select and copy it';
      announce(ok ? 'Copied.' : "Couldn't copy. Select the text and copy it yourself.");
      setTimeout(() => { b.querySelector('span').textContent = label; }, 2500);
    },
  });
  return b;
}

// ---------------------------------------------------------------- range picker

export const RANGES = [7, 30, 90, 180];

export function rangePicker(days, onPick) {
  return h('div', { class: 'seg', role: 'group', 'aria-label': 'Date range' },
    RANGES.map((d) => h('button', {
      type: 'button', class: 'seg-btn', 'aria-pressed': String(d === days),
      title: 'Last ' + d + ' days', onclick: () => { if (d !== days) onPick(d); },
    }, d + 'd')));
}

// A short visible note under a section, e.g. "Players get the new price within about a minute."
export const note = (...kids) => h('p', { class: 'note' }, kids);
