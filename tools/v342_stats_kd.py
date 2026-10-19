"""v342: Stats shows wins, K/D, matches and win rate (no best coverage).

- The Stats card's four tiles were wins, matches, win rate and best coverage. Now they're wins and K/D on top, matches and win rate
  under them. Best coverage goes from the card (it's still kept for the results' "new best").
- K/D is your knockouts over the times you were knocked out (by a rival or off the edge), in every match but Time trial: kept from now
  on (store.kos and store.outs, added up at the end of each match and Showdown). With none of either yet it shows a dash; with no outs
  it's your knockouts."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, '<div class="stgrid"><div><b id="stWins">0</b><small>Wins</small></div><div><b id="stPlayed">0</b><small>Matches</small></div><div><b id="stRate">0%</b><small>Win rate</small></div><div><b id="stBest">0%</b><small>Best coverage</small></div></div>',
               '<div class="stgrid"><div><b id="stWins">0</b><small>Wins</small></div><div><b id="stKd">–</b><small>K/D</small></div><div><b id="stPlayed">0</b><small>Matches</small></div><div><b id="stRate">0%</b><small>Win rate</small></div></div>')
    s = rep(s, "// your stats: your rank and what's left to the next, wins, matches, win rate, best coverage; your name, and changing it",
               "// your stats: your rank and what's left to the next, wins, K/D, matches, win rate (v342: K/D for best coverage); your name, and changing it")
    s = rep(s, "  const r = repOf(store.xp || 0); let wins = 0, vs = 0, best = 0;", "  const r = repOf(store.xp || 0), ko = store.kos || 0, out = store.outs || 0; let wins = 0, vs = 0;")
    s = rep(s, "  for (const k in store.bestCov || {}) best = Math.max(best, store.bestCov[k] || 0);\n", "")
    s = rep(s, "$('stRate').textContent = (vs ? Math.round(100 * wins / vs) : 0) + '%'; $('stBest').textContent = best + '%';",
               "$('stRate').textContent = (vs ? Math.round(100 * wins / vs) : 0) + '%'; $('stKd').textContent = ko || out ? (ko / Math.max(1, out)).toFixed(2) : '–';")
    # at the end of each match (and of each Showdown) but Time trial: your knockouts, and the times you were knocked out, added up
    s = rep(s, "  store.runs = (store.runs || 0) + 1; if (store.itemIn > 0) store.itemIn--;\n",
               "  store.runs = (store.runs || 0) + 1; if (store.itemIn > 0) store.itemIn--;\n"
               "  if (mode !== 'solo') { store.kos = (store.kos || 0) + (P.kos | 0); store.outs = (store.outs || 0) + (P.outs | 0); } // (v342: for Stats' K/D)\n", 2)
    return s
