// Modes: plays per mode, the favourite, players per mode (all time), results, coverage and length, online share,
// plays per day per mode, canvases and CPU difficulties.

import { h, card, stat, grid, table, empty, note, rate } from '../ui.js';
import { lineChart, stackedDays, chartCard, hbars, shareBars } from '../charts.js';
import { num, pct, ratio, secs, sum } from '../format.js';
import { rpc } from '../api.js';
import { catalog, modeName, stageName, diffName } from '../catalog.js';

export default {
  id: 'modes', title: 'Modes', icon: 'modes', range: true,
  sub: 'What people play, how it goes, and where.',
  load: (ctx) => rpc('adm_modes', { p_days: ctx.days }),
  view,
};

function view(m, ctx) {
  m = m || {};
  const byId = new Map((m.modes || []).map((x) => [x.mode, x]));
  // catalog order first, then any mode the catalog doesn't know
  const ids = [...catalog().modes.map((x) => x.id), ...(m.modes || []).map((x) => x.mode).filter((id) => !catalog().modes.some((c) => c.id === id))];
  const rows = ids.map((id) => ({ mode: id, name: modeName(id), plays: 0, wins: 0, losses: 0, draws: 0, players: 0, avg_secs: 0, avg_cov: 0, online: 0, ...(byId.get(id) || {}) }));
  const total = sum(rows.map((r) => r.plays));
  const fav = total ? rows.reduce((a, b) => (b.plays > a.plays ? b : a)) : null;
  const online = sum(rows.map((r) => r.online));
  const avgLen = total ? sum(rows.map((r) => r.avg_secs * r.plays)) / total : 0;
  const span = 'the last ' + ctx.days + ' days';

  const kpis = h('div', { class: 'tiles' },
    stat('Plays', num(total), { sub: 'Matches played to the end in ' + span }),
    stat('Favourite mode', fav ? fav.name : 'None yet', { sub: fav ? pct(fav.plays / total) + ' of plays' : 'No plays in this range' }),
    stat('Played online', pct(ratio(online, total)), { sub: num(online) + ' of the plays' }),
    stat('Average match', total ? secs(avgLen) : 'n/a', { sub: 'Across every mode' }));

  const playsCard = card('Plays per mode', { sub: 'Matches played to the end in ' + span },
    total ? hbars(rows.map((r) => ({ label: r.name, value: r.plays, note: pct(r.plays / total) })), { label: 'Plays per mode' })
      : empty('No plays in this range', 'Plays show up here once matches are played to the end.'));
  const detail = card('Modes in detail', { sub: 'Players is every install that ever played the mode; the rest is ' + span },
    table([
      { key: 'name', label: 'Mode', sort: (r) => r.name },
      { key: 'plays', label: 'Plays', num: true, sort: (r) => r.plays, cell: (r) => num(r.plays) },
      { key: 'players', label: 'Players (all time)', num: true, sort: (r) => r.players, cell: (r) => num(r.players) },
      { key: 'wr', label: 'Win rate', num: true, sort: (r) => ratio(r.wins, r.wins + r.losses + r.draws), cell: (r) => rate(ratio(r.wins, r.wins + r.losses + r.draws)) },
      { key: 'cov', label: 'Average coverage', num: true, sort: (r) => r.avg_cov, cell: (r) => (r.plays ? (Math.round(r.avg_cov * 10) / 10) + '%' : rate(null)) },
      { key: 'len', label: 'Average length', num: true, sort: (r) => r.avg_secs, cell: (r) => (r.plays ? secs(r.avg_secs) : rate(null)) },
      { key: 'on', label: 'Online', num: true, sort: (r) => ratio(r.online, r.plays), cell: (r) => rate(ratio(r.online, r.plays)) },
    ], rows, { caption: 'Modes in detail' }));

  const results = card('Results', { sub: 'Wins, draws and losses per mode, from the player\'s side' },
    shareBars(rows.map((r) => ({
      label: r.name, totalText: num(r.wins + r.losses + r.draws) + ' results',
      parts: [{ name: 'Win', value: r.wins, color: 1 }, { name: 'Draw', value: r.draws, color: 'x' }, { name: 'Loss', value: r.losses, color: 2 }],
    })), { label: 'Results per mode', legendParts: [{ name: 'Win', color: 1 }, { name: 'Draw', color: 'x' }, { name: 'Loss', color: 2 }] }));

  const days = (m.days || []).map((d) => d.day);
  const perDay = chartCard('Plays per day', 'Each day (UTC), by mode', stackedDays({
    label: 'Plays per day by mode', days,
    series: rows.slice(0, 5).map((r, i) => ({ name: r.name, values: (m.days || []).map((d) => Number(d[r.mode]) || 0), color: i + 1 })),
  }));
  const onlineDay = chartCard('Online plays per day', num(sum((m.days || []).map((d) => d.online || 0))) + ' in ' + span, lineChart({
    label: 'Online plays per day', days, series: [{ name: 'Online plays', values: (m.days || []).map((d) => d.online || 0), color: 1 }],
  }));

  const stages = m.stages || [];
  const stageTotal = sum(stages.map((s) => s.plays));
  const canvases = card('Canvases', { sub: 'Plays per canvas in ' + span },
    stages.length ? hbars(stages.map((s) => ({ label: stageName(s.stage), value: s.plays, note: pct(ratio(s.plays, stageTotal)) })), { label: 'Plays per canvas' })
      : empty('No canvases played yet', 'Each canvas shows up once a match is played on it.'));
  const diffs = m.diffs || [];
  const diffTotal = sum(diffs.map((d) => d.plays));
  const cpu = card('CPU difficulty', { sub: 'Plays against the CPU per difficulty in ' + span },
    diffs.length ? hbars(diffs.map((d) => ({ label: diffName(d.diff), value: d.plays, note: pct(ratio(d.plays, diffTotal)) })), { label: 'Plays per CPU difficulty' })
      : empty('No CPU matches yet', 'Difficulties show up once matches against the CPU are played.'));

  return [
    kpis,
    grid('two', playsCard, results),
    detail,
    perDay,
    grid('three', onlineDay, canvases, cpu),
    note('Win rates count every result in a mode, online or not.'),
  ];
}
