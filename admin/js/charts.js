// Hand-written charts: SVG for time series and columns, plain HTML for horizontal bars and shares.
// The rules they follow: thin marks (bars at most 24px, lines 2px), 4px rounded data ends square at the baseline,
// a 2px surface gap between touching fills and a 2px surface ring on dots, hairline solid gridlines, a legend for
// two or more series, a tooltip on hover AND keyboard focus, and a table view of the same numbers for every chart.
// Colours come from CSS classes (c1..c5, cx for context) so light and dark themes each use their own steps.

import { h, s, icon, mount, card, table } from './ui.js';
import { num, compact, day, dayLong, todayUTC } from './format.js';

const GAP = 2;      // the surface gap between touching marks
const BAR_MAX = 24; // bars never fill their slot
const R = 4;        // rounded data end

let measureCtx = null;
function textW(t, px = 11) {
  if (!measureCtx) {
    measureCtx = document.createElement('canvas').getContext('2d');
    measureCtx.font = px + 'px ' + getComputedStyle(document.body).fontFamily;
  }
  return measureCtx ? measureCtx.measureText(String(t)).width : String(t).length * px * 0.6;
}

function niceStep(raw) {
  const p = Math.pow(10, Math.floor(Math.log10(raw)));
  const f = raw / p;
  return (f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10) * p;
}

// Round tick values from 0 up past max: 0 / 250 / 500 / 750 / 1000.
export function niceTicks(max, { count = 4, integer = true } = {}) {
  if (!(max > 0)) return [0];
  let step = niceStep(max / count);
  if (integer) step = Math.max(1, step);
  const ticks = [];
  for (let v = 0; ticks.length < 12; v += step) {
    ticks.push(Math.round(v * 1e6) / 1e6);
    if (v >= max) break;
  }
  return ticks;
}

// Re-draw at the real pixel width whenever the box changes size (so text never scales).
// The plot box has a fixed height, and drawing waits for the next frame, so a redraw never resizes what's observed.
function observe(el, draw) {
  let w = 0, raf = 0;
  const ro = new ResizeObserver((entries) => {
    const nw = Math.floor(entries[0].contentRect.width);
    if (nw > 0 && nw !== w) {
      w = nw;
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => draw(w));
    }
  });
  ro.observe(el);
}

// A bar with a rounded data end and a square base. Vertical (columns) or horizontal.
function colPath(x, y, w, base) {
  const hgt = base - y;
  if (hgt <= 0 || w <= 0) return '';
  const r = Math.min(R, w / 2, hgt);
  return `M${x},${base}V${y + r}A${r},${r} 0 0 1 ${x + r},${y}H${x + w - r}A${r},${r} 0 0 1 ${x + w},${y + r}V${base}Z`;
}

export function legend(series, kind) {
  if (series.length < 2) return null;
  return h('ul', { class: 'legend', 'aria-label': 'Legend' }, series.map((se) => h('li', { class: 'legend-item c' + se.color },
    s('svg', { class: 'legend-key', viewBox: '0 0 16 10', 'aria-hidden': 'true' },
      kind === 'line' ? s('line', { x1: '1', y1: '5', x2: '15', y2: '5', class: 'key-line' }) : s('rect', { x: '2', y: '0', width: '12', height: '10', rx: '2', class: 'key-rect' })),
    h('span', null, se.name))));
}

// The tooltip: values lead, labels follow; series keyed with a short line.
function tipRows(title, rows) {
  return [h('div', { class: 'tip-title' }, title),
    rows.map((r) => h('div', { class: 'tip-row' + (r.color ? ' c' + r.color : '') },
      r.color ? s('svg', { class: 'tip-key', viewBox: '0 0 12 4', 'aria-hidden': 'true' }, s('line', { x1: '0', y1: '2', x2: '12', y2: '2' })) : h('span', { class: 'tip-key' }),
      h('b', null, r.value), h('span', null, r.name)))];
}

function placeTip(tip, plot, x, top) {
  tip.hidden = false;
  const pw = plot.clientWidth, tw = tip.offsetWidth;
  let left = x + 14;
  if (left + tw > pw - 4) left = x - 14 - tw;
  if (left < 4) left = Math.max(4, Math.min(pw - tw - 4, x - tw / 2));
  tip.style.left = Math.round(left) + 'px';
  tip.style.top = Math.round(top) + 'px';
}

// Pointer and keyboard reading of an indexed chart (days or categories).
function interact(plot, n, show, hide) {
  let idx = -1;
  const set = (i) => { idx = Math.max(0, Math.min(n - 1, i)); show(idx); };
  plot.addEventListener('pointermove', (e) => { const i = plot._index ? plot._index(e) : -1; if (i >= 0) set(i); });
  plot.addEventListener('pointerdown', (e) => { const i = plot._index ? plot._index(e) : -1; if (i >= 0) set(i); });
  plot.addEventListener('pointerleave', (e) => { if (e.pointerType === 'mouse' && document.activeElement !== plot) { idx = -1; hide(); } });
  plot.addEventListener('focus', () => set(idx >= 0 ? idx : n - 1));
  plot.addEventListener('blur', () => { idx = -1; hide(); });
  plot.addEventListener('keydown', (e) => {
    const step = { ArrowRight: 1, ArrowLeft: -1, ArrowUp: 1, ArrowDown: -1 }[e.key];
    if (step) { e.preventDefault(); set((idx < 0 ? n - 1 : idx) + step); }
    else if (e.key === 'Home') { e.preventDefault(); set(0); }
    else if (e.key === 'End') { e.preventDefault(); set(n - 1); }
    else if (e.key === 'Escape') { idx = -1; hide(); }
  });
  return { redraw: () => { if (idx >= 0) show(idx); } };
}

function plotBox(label, hint, height) {
  const el = h('div', { class: 'plot', tabindex: '0', role: 'group', 'aria-label': label + (hint ? '. ' + hint : '') });
  el.style.height = height + 34 + 'px'; // the plot, plus the x-axis band
  return el;
}

// The y axis: gridlines, tick labels and the baseline. Returns the scale.
function yAxis(g, { ticks, left, right, top, base, fmt }) {
  const max = ticks[ticks.length - 1] || 1;
  const y = (v) => base - (Math.max(0, v) / max) * (base - top);
  ticks.forEach((t, i) => {
    const yy = Math.round(y(t)) + 0.5;
    g.append(s('line', { x1: String(left), x2: String(right), y1: String(yy), y2: String(yy), class: i === 0 ? 'ax' : 'gl' }));
    g.append(s('text', { x: String(left - 8), y: String(yy + 3.5), class: 'tick', 'text-anchor': 'end' }, fmt(t)));
  });
  return y;
}

function xLabels(g, idxs, xOf, label, { width, y }) {
  for (const i of idxs) {
    const t = label(i);
    const w = textW(t);
    const x = Math.max(w / 2 + 1, Math.min(width - w / 2 - 1, xOf(i)));
    g.append(s('text', { x: String(Math.round(x)), y: String(y), class: 'tick', 'text-anchor': 'middle' }, t));
  }
}

// Evenly spaced label indexes, anchored on the last one, at least minGap px apart.
function pickLabels(n, plotW, minGap) {
  const most = Math.max(1, Math.floor(plotW / minGap));
  const step = Math.max(1, Math.ceil(n / most));
  const out = [];
  for (let i = n - 1; i >= 0; i -= step) out.push(i);
  return out.reverse();
}

function emptyNote(g, width, top, base, text) {
  g.append(s('text', { x: String(width / 2), y: String((top + base) / 2 + 4), class: 'chart-empty', 'text-anchor': 'middle' }, text));
}

function frame(plot, legendEl, twin) {
  twin.hidden = true;
  return h('div', { class: 'chart' }, legendEl, plot, twin);
}

// ---------------------------------------------------------------- time series

// A line per series over days; a soft area under a single series.
// series: [{ name, values, color: 1..5 }]
export function lineChart({ label, days, series, fmt = num, tick = compact, height = 170, area, integer = true, emptyText = 'Nothing in this range yet' }) {
  const n = days.length;
  const today = todayUTC();
  const partial = n > 0 && days[n - 1] === today;
  const useArea = area ?? series.length === 1;
  const all = series.flatMap((se) => se.values);
  const max = Math.max(0, ...all);
  const plot = plotBox(label, 'Use the arrow keys to read each day', height);
  const tip = h('div', { class: 'tip', hidden: true });
  const twin = dayTable(label, days, series, fmt);
  let geo = null;

  function draw(width) {
    const ticks = niceTicks(max, { integer });
    const tickW = Math.max(...ticks.map((t) => textW(tick(t))));
    const ends = series.map((se) => fmt(se.values[n - 1] ?? 0));
    const endW = series.length <= 4 && max > 0 ? Math.max(...ends.map((t) => textW(t))) + 12 : 0;
    const left = Math.ceil(tickW) + 12, right = width - Math.max(10, endW), top = 10, base = top + height;
    const svg = s('svg', { width: String(width), height: String(base + 24), class: 'svg', 'aria-hidden': 'true' });
    const g = s('g'); svg.append(g);
    const y = yAxis(g, { ticks, left, right, top, base, fmt: tick });
    const x = (i) => (n === 1 ? (left + right) / 2 : left + (i * (right - left)) / (n - 1));
    xLabels(g, pickLabels(n, right - left, 64), x, (i) => (partial && i === n - 1 ? 'Today' : day(days[i])), { width, y: base + 17 });
    if (max === 0) emptyNote(g, (left + right), top, base, emptyText);
    else {
      // today is still going: the solid line stops at yesterday and a dashed segment reaches today
      const solid = partial && n > 1 ? n - 1 : n;
      series.forEach((se) => {
        const pts = se.values.map((v, i) => [x(i).toFixed(1), y(v ?? 0).toFixed(1)]);
        const d = pts.slice(0, solid).map((p, i) => (i ? 'L' : 'M') + p[0] + ',' + p[1]).join('');
        if (useArea) g.append(s('path', { d: d + `L${pts[solid - 1][0]},${base}L${pts[0][0]},${base}Z`, class: 'ar c' + se.color }));
        g.append(s('path', { d, class: 'ln c' + se.color }));
        if (solid < n) g.append(s('path', { d: `M${pts[n - 2][0]},${pts[n - 2][1]}L${pts[n - 1][0]},${pts[n - 1][1]}`, class: 'ln part c' + se.color }));
      });
      // end dots and selective end labels (dropped when they'd collide)
      const endY = series.map((se) => y(se.values[n - 1] ?? 0));
      const clash = endY.some((a, i) => endY.some((b, j) => j > i && Math.abs(a - b) < 13));
      series.forEach((se, k) => {
        g.append(s('circle', { cx: String(x(n - 1)), cy: String(endY[k]), r: '4', class: 'dot c' + se.color + (partial ? ' hollow' : '') }));
        if (endW && !clash) g.append(s('text', { x: String(x(n - 1) + 8), y: String(endY[k] + 3.5), class: 'end-label' }, ends[k]));
      });
    }
    const hover = s('g', { class: 'hover', visibility: 'hidden' });
    hover.append(s('line', { class: 'xhair', y1: String(top), y2: String(base) }));
    series.forEach((se) => hover.append(s('circle', { r: '4', class: 'dot c' + se.color })));
    svg.append(hover);
    geo = { x, y, left, right, top, base, hover };
    plot._index = (e) => {
      const r = plot.getBoundingClientRect();
      const px = e.clientX - r.left;
      if (n < 1) return -1;
      return n === 1 ? 0 : Math.round(((px - left) / (right - left)) * (n - 1));
    };
    const old = plot.querySelector('svg');
    old ? old.replaceWith(svg) : plot.prepend(svg);
    ui.redraw();
  }

  function show(i) {
    if (!geo || !n) return;
    const xx = geo.x(i);
    geo.hover.setAttribute('visibility', 'visible');
    const [line, ...dots] = geo.hover.children;
    line.setAttribute('x1', xx); line.setAttribute('x2', xx);
    series.forEach((se, k) => { dots[k].setAttribute('cx', xx); dots[k].setAttribute('cy', geo.y(se.values[i] ?? 0)); });
    mount(tip, tipRows(dayLong(days[i]) + (partial && i === n - 1 ? ' (so far)' : ''),
      series.map((se) => ({ color: se.color, value: fmt(se.values[i] ?? 0), name: se.name }))));
    placeTip(tip, plot, xx, geo.top);
  }
  function hide() { tip.hidden = true; if (geo) geo.hover.setAttribute('visibility', 'hidden'); }

  plot.append(tip);
  const ui = interact(plot, n, show, hide);
  observe(plot, draw);
  return { el: frame(plot, legend(series, 'line'), twin), plot, twin };
}

// Columns per day, stacked by series (plays per day per mode).
export function stackedDays({ label, days, series, fmt = num, tick = compact, height = 170, emptyText = 'Nothing in this range yet' }) {
  const n = days.length;
  const totals = days.map((_, i) => series.reduce((a, se) => a + (se.values[i] || 0), 0));
  const max = Math.max(0, ...totals);
  const plot = plotBox(label, 'Use the arrow keys to read each day', height);
  const tip = h('div', { class: 'tip', hidden: true });
  const twin = dayTable(label, days, [...series, { name: 'Total', values: totals }], fmt);
  const partial = n > 0 && days[n - 1] === todayUTC();
  let geo = null;

  function draw(width) {
    const ticks = niceTicks(max);
    const left = Math.ceil(Math.max(...ticks.map((t) => textW(tick(t))))) + 12, right = width - 10, top = 10, base = top + height;
    const svg = s('svg', { width: String(width), height: String(base + 24), class: 'svg', 'aria-hidden': 'true' });
    const g = s('g'); svg.append(g);
    const band = (right - left) / Math.max(1, n);
    const bw = Math.max(1, Math.min(BAR_MAX, band - GAP));
    const cx = (i) => left + band * (i + 0.5);
    const hoverBand = s('rect', { class: 'hover-band', y: String(top), height: String(height), width: String(band), visibility: 'hidden' });
    g.append(hoverBand);
    const y = yAxis(g, { ticks, left, right, top, base, fmt: tick });
    xLabels(g, pickLabels(n, right - left, 64), cx, (i) => (partial && i === n - 1 ? 'Today' : day(days[i])), { width, y: base + 17 });
    if (max === 0) emptyNote(g, left + right, top, base, emptyText);
    else {
      for (let i = 0; i < n; i++) {
        let cum = 0;
        const segs = series.map((se) => ({ color: se.color, v: se.values[i] || 0 })).filter((sg) => sg.v > 0);
        segs.forEach((sg, k) => {
          const y0 = y(cum), y1 = y(cum + sg.v);
          cum += sg.v;
          const bottom = k === 0 ? y0 : y0 - GAP; // the 2px surface gap between segments
          if (bottom - y1 < 0.5) return;
          const x0 = cx(i) - bw / 2;
          const cls = 'bar c' + sg.color + (partial && i === n - 1 ? ' part' : '');
          g.append(k === segs.length - 1
            ? s('path', { d: colPath(x0, y1, bw, bottom), class: cls })
            : s('rect', { x: String(x0), y: String(y1), width: String(bw), height: String(bottom - y1), class: cls }));
        });
      }
    }
    geo = { cx, band, top, hoverBand, left };
    plot._index = (e) => {
      const r = plot.getBoundingClientRect();
      return Math.floor((e.clientX - r.left - left) / band);
    };
    const old = plot.querySelector('svg');
    old ? old.replaceWith(svg) : plot.prepend(svg);
    ui.redraw();
  }

  function show(i) {
    if (!geo) return;
    geo.hoverBand.setAttribute('x', geo.cx(i) - geo.band / 2);
    geo.hoverBand.setAttribute('visibility', 'visible');
    mount(tip, tipRows(dayLong(days[i]) + (partial && i === n - 1 ? ' (so far)' : ''),
      [...series].reverse().map((se) => ({ color: se.color, value: fmt(se.values[i] || 0), name: se.name }))
        .concat([{ value: fmt(totals[i]), name: 'Total' }])));
    placeTip(tip, plot, geo.cx(i), geo.top);
  }
  function hide() { tip.hidden = true; if (geo) geo.hoverBand.setAttribute('visibility', 'hidden'); }

  plot.append(tip);
  const ui = interact(plot, n, show, hide);
  observe(plot, draw);
  return { el: frame(plot, legend([...series], 'rect'), twin), plot, twin };
}

// Columns per category. With `nested`, the first series is context (drawn in grey) and the second sits inside it,
// e.g. all installs at a rank, and the ones active in the last 30 days.
export function columnChart({ label, cats, catHead = 'Category', series, fmt = num, tick = compact, height = 170, catName = (c) => String(c), minGap = 26, emptyText = 'Nothing here yet' }) {
  const n = cats.length;
  const max = Math.max(0, ...series.flatMap((se) => se.values));
  const plot = plotBox(label, 'Use the arrow keys to read each column', height);
  const tip = h('div', { class: 'tip', hidden: true });
  const twin = h('div', null, table(
    [{ key: 'c', label: catHead, cell: (r) => catName(r.c) }, ...series.map((se, k) => ({ key: 's' + k, label: se.name, num: true, cell: (r) => fmt(r.v[k]) }))],
    cats.map((c, i) => ({ c, v: series.map((se) => se.values[i] || 0) })), { caption: label }));
  let geo = null;

  function draw(width) {
    const ticks = niceTicks(max);
    const left = Math.ceil(Math.max(...ticks.map((t) => textW(tick(t))))) + 12, right = width - 10, top = 10, base = top + height;
    const svg = s('svg', { width: String(width), height: String(base + 24), class: 'svg', 'aria-hidden': 'true' });
    const g = s('g'); svg.append(g);
    const band = (right - left) / Math.max(1, n);
    const bw = Math.max(1, Math.min(BAR_MAX, band - GAP - Math.min(6, band * 0.2)));
    const cx = (i) => left + band * (i + 0.5);
    const hoverBand = s('rect', { class: 'hover-band', y: String(top), height: String(height), width: String(band), visibility: 'hidden' });
    g.append(hoverBand);
    const y = yAxis(g, { ticks, left, right, top, base, fmt: tick });
    xLabels(g, pickLabels(n, right - left, minGap), cx, (i) => catName(cats[i]), { width, y: base + 17 });
    if (max === 0) emptyNote(g, left + right, top, base, emptyText);
    else {
      for (let i = 0; i < n; i++) {
        series.forEach((se) => {
          const v = se.values[i] || 0;
          if (v > 0) g.append(s('path', { d: colPath(cx(i) - bw / 2, Math.min(y(v), base - 1), bw, base), class: 'bar c' + se.color }));
        });
      }
    }
    geo = { cx, band, top, hoverBand };
    plot._index = (e) => {
      const r = plot.getBoundingClientRect();
      return Math.floor((e.clientX - r.left - left) / band);
    };
    const old = plot.querySelector('svg');
    old ? old.replaceWith(svg) : plot.prepend(svg);
    ui.redraw();
  }

  function show(i) {
    if (!geo) return;
    geo.hoverBand.setAttribute('x', geo.cx(i) - geo.band / 2);
    geo.hoverBand.setAttribute('visibility', 'visible');
    mount(tip, tipRows(catName(cats[i], true), series.map((se) => ({ color: se.color, value: fmt(se.values[i] || 0), name: se.name }))));
    placeTip(tip, plot, geo.cx(i), geo.top);
  }
  function hide() { tip.hidden = true; if (geo) geo.hoverBand.setAttribute('visibility', 'hidden'); }

  plot.append(tip);
  const ui = interact(plot, n, show, hide);
  observe(plot, draw);
  return { el: frame(plot, legend(series, 'rect'), twin), plot, twin };
}

// The table twin of a day chart: newest day first.
function dayTable(label, days, series, fmt) {
  const rows = days.map((d, i) => ({ d, i })).reverse();
  return h('div', null, table(
    [{ key: 'd', label: 'Day (UTC)', cell: (r) => dayLong(r.d) }, ...series.map((se, k) => ({ key: 's' + k, label: se.name, num: true, cell: (r) => fmt(se.values[r.i] || 0) }))],
    rows, { caption: label, empty: 'No days in this range.' }));
}

// ---------------------------------------------------------------- HTML bars

// Horizontal bars, value at the tip. rows: [{ label, value, note?, sub? }]. With `inner`, a second value is drawn
// inside the first (e.g. crafts, and those skipped with an ad).
export function hbars(rows, { fmt = num, color = 1, inner, innerColor = 1, outerColor, label = 'Bars', max } = {}) {
  const top = max ?? Math.max(0, ...rows.map((r) => r.value));
  return h('ul', { class: 'hbars', 'aria-label': label }, rows.map((r) => {
    const w = top > 0 ? (r.value / top) * 100 : 0;
    const fill = h('span', { class: 'hbar-fill c' + (inner ? outerColor ?? 'x' : color) });
    fill.style.width = (r.value > 0 ? Math.max(w, 0.8) : 0) + '%';
    const track = h('span', { class: 'hbar-track', 'aria-hidden': 'true' }, fill);
    if (inner) {
      const iv = r[inner] || 0;
      const f2 = h('span', { class: 'hbar-fill inner c' + innerColor });
      f2.style.width = (top > 0 && iv > 0 ? Math.max((iv / top) * 100, 0.8) : 0) + '%';
      track.append(f2);
    }
    return h('li', { class: 'hbar' },
      h('span', { class: 'hbar-label' }, r.label, r.sub ? h('small', null, ' ' + r.sub) : null),
      track,
      h('span', { class: 'hbar-value' }, fmt(r.value), r.note ? h('small', null, r.note) : null));
  }));
}

// 100% bars split into parts, e.g. wins, draws and losses per mode. parts: [{ name, value, color }]
export function shareBars(rows, { label = 'Shares', legendParts } = {}) {
  const leg = legendParts ? legend(legendParts, 'rect') : null;
  return h('div', { class: 'shares' }, leg, h('ul', { class: 'share-list', 'aria-label': label }, rows.map((r) => {
    const total = r.parts.reduce((a, p) => a + (p.value || 0), 0);
    const bar = h('span', { class: 'share-bar', 'aria-hidden': 'true' });
    if (total > 0) {
      r.parts.forEach((p) => {
        if (!p.value) return;
        const seg = h('span', { class: 'share-seg c' + p.color, title: p.name + ': ' + Math.round((p.value / total) * 100) + '%' });
        seg.style.flexGrow = String(p.value);
        bar.append(seg);
      });
    } else bar.classList.add('none');
    const words = total > 0 ? r.parts.filter((p) => p.value > 0).map((p) => p.name + ' ' + Math.round((p.value / total) * 100) + '%').join(' · ') : r.emptyText || 'No results yet';
    return h('li', { class: 'share' },
      h('div', { class: 'share-head' }, h('span', { class: 'share-label' }, r.label), h('span', { class: 'share-total' }, r.totalText ?? num(total))),
      bar,
      h('div', { class: 'share-words' }, words));
  })));
}

// A share against its whole: a track in a lighter step of the same hue.
export function meter(value, { label }) {
  const m = h('div', { class: 'meter', role: 'img', 'aria-label': label });
  const fill = h('div', { class: 'meter-fill' });
  fill.style.width = value == null ? '0%' : Math.max(0, Math.min(100, value * 100)) + '%';
  m.append(fill);
  return m;
}

// A card around a chart, with the Table toggle in its header.
export function chartCard(title, sub, chart, { cls = '', extra } = {}) {
  const label = h('span', null, 'Table');
  const toggle = h('button', {
    type: 'button', class: 'btn ghost small', 'aria-pressed': 'false', title: 'Show these numbers as a table',
    onclick: () => {
      const on = toggle.getAttribute('aria-pressed') !== 'true';
      toggle.setAttribute('aria-pressed', String(on));
      chart.plot.hidden = on;
      chart.twin.hidden = !on;
      const leg = chart.el.querySelector('.legend');
      if (leg) leg.hidden = on;
      label.textContent = on ? 'Chart' : 'Table';
      mount(toggle, icon(on ? 'chart' : 'table'), label);
    },
  }, icon('table'), label);
  return card(title, { sub, actions: toggle, cls: 'chart-card ' + cls }, chart.el, extra || null);
}
