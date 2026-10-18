// Overview: who's playing now, daily/weekly/monthly actives, installs and accounts, sessions, retention,
// and the daily charts over the chosen range.

import { h, card, stat, grid, note, empty, icon } from '../ui.js';
import { lineChart, chartCard, meter } from '../charts.js';
import { num, compact, pct, secs, hours, ratio, sum } from '../format.js';
import { rpc } from '../api.js';

export default {
  id: 'overview', title: 'Overview', icon: 'overview', range: true,
  sub: "Who's playing, how often, and who comes back.",
  load: (ctx) => rpc('adm_overview', { p_days: ctx.days }),
  view,
};

function view(o, ctx) {
  o = o || {};
  const daysList = o.days || [];
  const col = (k) => daysList.map((d) => Number(d[k]) || 0);
  const span = 'in ' + ctx.days + ' days';
  const fresh = !o.installs;

  const kpis = h('div', { class: 'kpis' },
    stat('Online now', num(o.online), { hero: true, sub: 'Installs heard from in the last 5 minutes' }),
    h('div', { class: 'tiles' },
      stat('Daily active', num(o.dau), { sub: 'Last 24 hours' }),
      stat('Weekly active', num(o.wau), { sub: 'Last 7 days' }),
      stat('Monthly active', num(o.mau), { sub: 'Last 30 days' }),
      stat('Installs', num(o.installs), { sub: 'Every install ever heard from' }),
      stat('Accounts', num(o.accounts), { sub: o.installs ? pct(ratio(o.accounts, o.installs)) + ' of installs have one' : 'Username and password' }),
      stat('New today', num(o.new_today), { sub: num(o.new_7d) + ' in the last 7 days' }),
      stat('Sessions today', num(o.sessions_today), { sub: 'Launches, or back after 30 minutes' }),
      stat('Average session', secs(o.avg_session_secs), { sub: 'Time per session' })));

  const r = o.retention || {};
  const ret = (n, share, cohort, from, to) => h('div', { class: 'ret' },
    h('div', { class: 'ret-head' }, h('span', { class: 'ret-label' }, 'Day ' + n), h('span', { class: 'ret-value' }, share == null ? 'No cohort yet' : pct(share))),
    meter(share, { label: 'Day ' + n + ' retention: ' + (share == null ? 'no cohort yet' : pct(share)) }),
    h('p', { class: 'ret-sub' }, share == null
      ? 'Needs installs that started ' + from + ' to ' + to + ' days ago.'
      : 'Of ' + num(cohort) + ' installs that started ' + from + ' to ' + to + ' days ago'));
  const retention = card('Retention', { sub: 'The share of new installs that came back exactly 1, 7 or 30 days after their first day' },
    h('div', { class: 'rets' },
      ret(1, r.d1, r.cohort_d1, 2, 8),
      ret(7, r.d7, r.cohort_d7, 8, 14),
      ret(30, r.d30, r.cohort_d30, 31, 37)),
    note('Each cohort only counts days that are over, so the newest installs wait a couple of days to be included.'));

  const day = daysList.map((d) => d.day);
  const charts = [
    ['Daily active installs', 'Installs heard from each day (UTC). Average ' + num(avg(col('dau'))) + ' a day', col('dau'), num],
    ['New installs', num(sum(col('new'))) + ' ' + span, col('new'), num],
    ['Sessions', num(sum(col('sessions'))) + ' ' + span, col('sessions'), num],
    ['Matches', num(sum(col('matches'))) + ' played to the end ' + span, col('matches'), num],
    ['Play time', num(hours(sum(col('play_secs')))) + ' hours ' + span, col('play_secs').map((v) => hours(v)), (v) => num(v) + ' h', { integer: false }],
  ].map(([title, sub, values, fmt, extra]) => chartCard(title, sub,
    lineChart({ label: title, days: day, series: [{ name: title, values, color: 1 }], fmt, tick: compact, ...(extra || {}) })));

  return [
    fresh ? h('div', { class: 'banner info' }, icon('info'), h('span', null, "No players yet. Everything here fills in as soon as the game sends its first events.")) : null,
    kpis,
    retention,
    h('div', { class: 'wide' }, charts[0]),
    grid('two', charts.slice(1)),
  ];
}

const avg = (list) => (list.length ? sum(list) / list.length : 0);
