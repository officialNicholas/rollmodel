"""v428: the Time trial's one leaderboard, the orb dropped on a knock-out, a storm keeps your tank full, Shuffle picks a canvas.

- The Time trial leaderboard: one board, everyone's best on the canvas this week (from public.rm_global_board), with your friends
  marked and where you stand if you're further down. The You / Friends / Global tabs are gone. The top three stand on a podium,
  the rest in a list, your own place pinned under it. The top three win dabs when the week turns (350, 200, 100). Before the
  database has the global board (or offline), it shows your friends' board as before, and with no account, your own best.
- The orb: one you're holding and haven't used comes out of you when you're knocked out, where you went down, for anyone to take
  (offline here; online the server does it). Gone over an edge, a new one comes up soon instead.
- The Paint Storm keeps its caster's paint tank full while it rains (offline here; online the server agrees).
- On the canvas picker, Shuffle picks another canvas at random (it rebuilt the same canvas with a new layout).
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v428) the Time trial's one board: a podium for the top three, the rest in a list, your place pinned under it */
#ttModal .tttabs{display:none}
.ttpod{display:grid;grid-template-columns:1fr 1.12fr 1fr;align-items:end;gap:10px;margin:4px 0 4px;padding:26px 9px 12px}
.ttpod .pd{position:relative;display:grid;justify-items:center;gap:3px;min-width:0;padding:22px 6px 10px;border-radius:3px;background:#FFFDF6;
  box-shadow:0 0 0 2px var(--black),3px 4px 0 2px rgba(23,19,32,.85);animation:p17rise var(--d-med) var(--ease-out) both}
.ttpod .pd.p1{padding-top:28px;padding-bottom:14px;background:linear-gradient(180deg,#FFF6CF,#FFE89A);rotate:-1deg;animation-delay:.05s}
.ttpod .pd.p2{rotate:1.5deg;background:linear-gradient(180deg,#FFFFFF,#E6EAF0)}.ttpod .pd.p3{rotate:-1.5deg;background:linear-gradient(180deg,#FFF3E6,#F2D2B4);animation-delay:.1s}
.ttpod .pd.me{box-shadow:0 0 0 2px var(--black),0 0 0 5px #E8364F,3px 4px 0 5px rgba(23,19,32,.85)}
.ttpod .pd .md{position:absolute;top:-14px;left:50%;translate:-50% 0;width:30px;height:30px;display:grid;place-items:center;border-radius:50%;font:400 15px/1 var(--font-display);box-shadow:0 0 0 2px var(--black),2px 2px 0 2px rgba(0,0,0,.25)}
.ttpod .pd.p1 .md{width:36px;height:36px;top:-18px;font-size:18px;background:radial-gradient(circle at 35% 30%,#FFF2B0,#F2C12E 55%,#B88412);color:#3A2600}
.ttpod .pd.p2 .md{background:radial-gradient(circle at 35% 30%,#FFFFFF,#C9CED6 55%,#8A92A0);color:#262A33}
.ttpod .pd.p3 .md{background:radial-gradient(circle at 35% 30%,#FFD9B3,#D08A4E 55%,#8E5326);color:#2E1604}
.ttpod .pd .frface{width:44px;height:44px}.ttpod .pd.p1 .frface{width:54px;height:54px}
.ttpod .pd .nm{max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font:800 12px/1.1 var(--font-ui);color:var(--black)}
.ttpod .pd .pc{font:400 22px/1 var(--font-display)}.ttpod .pd.p1 .pc{font-size:28px}.ttpod .pd .pc small{font-size:12px;margin-left:1px}
.ttpod .pd.empty{opacity:.45;box-shadow:0 0 0 2px rgba(23,19,32,.35);background:transparent}.ttpod .pd.empty .nm{font-weight:600;color:#6E6680}
.ttpod .pd .tg{position:absolute;bottom:-9px;left:50%;translate:-50% 0}
.ttwho .tgf,.ttpod .tg{flex:none;padding:3px 7px 2px;border-radius:999px;background:#3A84D4;color:#fff;font:800 10px/1 var(--font-ui);letter-spacing:.06em;text-transform:uppercase;rotate:-3deg;white-space:nowrap}
.ttpod .tg.you{background:#E8364F}
.ttprz{display:flex;justify-content:center;gap:10px;margin:10px 0 2px;font:700 12px/1.3 var(--font-ui);color:#5E566E;text-align:center}
.ttprz b{color:var(--black)}
.ttmine{position:sticky;bottom:0;display:grid;grid-template-columns:32px minmax(0,1fr) auto;align-items:center;gap:10px;margin:8px 0 0 -2px;padding:7px 10px 7px 6px;border-radius:3px;
  background:#FFE07A;box-shadow:0 0 0 2px var(--black),3px 3px 0 2px rgba(23,19,32,.8)}
.ttmine .ttrk{background:#fff;color:var(--black);width:auto;min-width:28px;padding:0 4px;border-radius:999px;font-size:12px}
.ttmine .ttwho{font-weight:800}
.ttsub{margin:2px 0 0;font:600 12px/1.35 var(--font-ui);color:#6E6680;text-align:center}
"""

JS = r"""
// ---------- (v428) the Time trial's one leaderboard: everyone's best on the canvas this week, your friends marked, your place under it.
// rm_global_board on the database; before it has that (or with the call refused), your friends' board as before ----------
const TTB = {}; // sid -> { at, rows: [{ id, name, look, best, rank, me, friend }], me: { rank, best } | null, total, src, err }
async function ttBoardLoad(sid) {
  if (TTB.busy === sid) return; TTB.busy = sid; await frFlushTrials();
  try {
    let r, src = 'global';
    try { r = await sbRpc('rm_global_board', { p_stage: sid, p_week: null }); }
    catch (e) { if (!(e && (e.status === 404 || e.status === 400))) throw e; src = 'friends'; const f = await sbRpc('rm_friends_board', { p_stage: sid, p_week: null }); r = { rows: (f.rows || []).map((x, i) => Object.assign({ rank: i + 1, friend: !x.me }, x)) }; }
    const rows = r.rows || [], mine = r.me || (rows.find(x => x.me) ? { rank: rows.find(x => x.me).rank, best: rows.find(x => x.me).best } : null);
    TTB[sid] = { at: Date.now(), rows, me: mine, total: r.total || rows.length, src };
  } catch (e) { const old = TTB[sid]; TTB[sid] = { at: Date.now() - 20000, rows: old ? old.rows : [], me: old ? old.me : null, total: old ? old.total : 0, src: old ? old.src : 'global', err: frErrText(e) }; }
  finally { TTB.busy = ''; }
  if (!$('ttModal').hidden && ttSel === sid) ttRender();
}
function ttBoardHtml(sid) {
  const L = ttRuns(sid), myBest = L.length ? L[0].p : null, P3 = TT_PRIZE.global;
  const mineRow = (rank, best, sub) => '<div class="ttmine"><b class="ttrk">' + (rank ? ttOrd(rank) : '–') + '</b><span class="ttwho">' + frFace(frLook()) + 'You' + (sub ? '<em>' + escAttr(sub) + '</em>' : '') + '</span><b class="ttpc">' + (best == null ? '–' : (best | 0) + '<small>%</small>') + '</b></div>';
  const local = (title, why) => '<p class="ttnone"><b>' + title + '</b>' + why + '</p>' + (myBest != null ? mineRow(0, myBest, 'Not on the board') : '');
  if (!SB_CFG) return local('The leaderboard comes with online play.', 'Your best here this week is kept on this phone.');
  if (!FR.me) { if (acOut() || FR.need) return local(FR.need ? 'Pick your username to go on the board.' : 'Log in to go on the board.', 'Everyone’s best on this canvas, every week.'); if (!acctReady()) return local('Make an account to go on the board.', 'Make one in the menu: then your runs count.'); if (!FR.busy && Date.now() > FR.retryAt) frStart(); return FR.err && !FR.busy ? local('Can’t load the board.', frEsc(FR.err)) : '<p class="ttnone"><b>Loading the board…</b></p>'; }
  const c = TTB[sid]; if (!c || Date.now() - c.at > 30000) ttBoardLoad(sid);
  if (!c) return '<p class="ttnone"><b>Loading the board…</b></p>';
  if (c.err && !c.rows.length) return local('Can’t load the board.', frEsc(c.err));
  if (!c.rows.length) return '<p class="ttnone"><b>Nobody’s on this canvas yet this week.</b>Play a Time trial here to be first.</p>' + '<p class="ttprz">Top three win <b>' + P3[0] + '</b>, <b>' + P3[1] + '</b> and <b>' + P3[2] + '</b> dabs</p>';
  const who = r => frEsc(r.me ? 'You' : hdOf(r.name)), tag = r => r.me ? '<i class="tg you">You</i>' : r.friend ? '<i class="tg">Friend</i>' : '';
  let h = '<div class="ttpod">';
  for (const k of [1, 0, 2]) { const r = c.rows[k];
    h += r ? '<div class="pd p' + (k + 1) + (r.me ? ' me' : '') + '"><b class="md">' + (k + 1) + '</b>' + frFace(r.look) + '<span class="nm">' + who(r) + '</span><b class="pc">' + (r.best | 0) + '<small>%</small></b>' + tag(r) + '</div>'
      : '<div class="pd p' + (k + 1) + ' empty"><b class="md">' + (k + 1) + '</b><span class="nm">Open</span></div>'; }
  h += '</div><p class="ttprz">When the week turns: <b>' + P3[0] + '</b> · <b>' + P3[1] + '</b> · <b>' + P3[2] + '</b> dabs</p>';
  if (c.rows.length > 3) h += '<ol class="ttlist">' + c.rows.slice(3, 25).map(r => '<li class="ttrow' + (r.me ? ' me' : '') + '"><b class="ttrk" aria-label="' + ttOrd(r.rank) + '">' + r.rank + '</b><span class="ttwho">' + frFace(r.look) + who(r) + (r.friend ? '<i class="tgf">Friend</i>' : '') + '</span><b class="ttpc">' + (r.best | 0) + '<small>%</small></b></li>').join('') + '</ol>';
  const inTop = c.rows.some(r => r.me);
  if (!inTop) h += c.me ? mineRow(c.me.rank, c.me.best) : myBest != null ? mineRow(0, myBest, 'Sending…') : mineRow(0, null, 'No run yet');
  h += '<p class="ttsub">' + (c.src === 'friends' ? 'You and your friends this week.' : (c.total || c.rows.length) + (c.total === 1 ? ' player' : ' players') + ' on ' + escAttr(ttName(sid)) + ' this week.') + '</p>';
  return h;
}
// the orb you were holding comes out of you where you went down (offline: online the server does it)
function orbDrop(D) {
  D.orbSaved = null; D.orbT = 0; if (orb.on) return;
  const g = surfaceUnder(D.x, D.z, D.y + 0.5, true);
  if (!(g > -Infinity) || Math.abs(g - D.y) > 3) { orb.spawnT = Math.min(orb.spawnT, 1.5); return; } // (over an edge: a new one soon)
  orb.on = true; orb.k = 0; orb.pull = 0; orb.stay = false; orb.inT = 0; orb.x = orb.tx = D.x; orb.z = orb.tz = D.z; orb.base = g; orb.y = g + 1.15; orb.ph = Math.random() * 6.28;
  orb.g.visible = true; orb.ring.visible = true; AU.orb && AU.orb(); popText(D === P ? 'You dropped your orb!' : nameOf(D) + ' dropped an orb!');
  for (let i = 0; i < 16; i++) { const a = i / 16 * 6.283; spawnPart(orb.x, orb.y, orb.z, Math.cos(a) * 2.5, (Math.random() - 0.3) * 3, Math.sin(a) * 2.5, 0.5, orbPartMats[i % orbPartMats.length], 0.5); }
}
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    # ---- the leaderboard: one board
    s = rep(s, "let ttSel = null, ttTab = 'you', ttHi = 0, ttTick = 0;", "let ttSel = null, ttTab = 'board', ttHi = 0, ttTick = 0;" + JS)
    s = rep(s, "  $('ttModal').dataset.tab = ttTab; let h = '';\n  if (ttTab === 'you') {", "  $('ttModal').dataset.tab = ttTab; let h = '';\n  if (ttTab === 'board') h = ttBoardHtml(sid); // (v428: the one board)\n  else if (ttTab === 'you') {")
    s = rep(s, "ttSel = TT_STAGES.includes(sid) ? sid : ttSid(); ttTab = 'you';", "ttSel = TT_STAGES.includes(sid) ? sid : ttSid(); ttTab = 'board';")
    s = rep(s, "<h3 id=\"ttTitle\">Leaderboard</h3>", "<h3 id=\"ttTitle\">Leaderboard</h3>")
    # your run reaches the board: the board's copy goes stale
    s = rep(s, "function frTrial(sid, p) { if (!SB_CFG) return; store.ttq = (store.ttq || []).concat([{ s: sid, p: Math.round(p), w: ttWeek() }]).slice(-30); save(); delete FR.board[sid]; frFlushTrials(); }",
               "function frTrial(sid, p) { if (!SB_CFG) return; store.ttq = (store.ttq || []).concat([{ s: sid, p: Math.round(p), w: ttWeek() }]).slice(-30); save(); delete FR.board[sid]; delete TTB[sid]; frFlushTrials(); }")
    # the week's prizes: the top three of the one board (the friends board's while the database hasn't the global one)
    s = rep(s, "  try { for (const sid of Object.keys(o.prev.best)) { const r = await sbRpc('rm_friends_board', { p_stage: sid, p_week: wk }), rows = r.rows || [], i = rows.findIndex(x => x.me);\n      if (rows.length >= TT_FRIENDS_MIN && i >= 0 && i < 3) { won += TT_PRIZE.friends[i]; line = ttOrd(i + 1) + ' on ' + ttName(sid); } }",
               "  try { for (const sid of Object.keys(o.prev.best)) { let r, P3 = TT_PRIZE.global; try { r = await sbRpc('rm_global_board', { p_stage: sid, p_week: wk }); } catch (e) { if (!(e && (e.status === 404 || e.status === 400))) throw e; r = await sbRpc('rm_friends_board', { p_stage: sid, p_week: wk }); P3 = TT_PRIZE.friends; } // (v428: the one board)\n      const rows = r.rows || [], i = rows.findIndex(x => x.me);\n      if (rows.length >= TT_FRIENDS_MIN && i >= 0 && i < 3) { won += P3[i]; line = ttOrd(i + 1) + ' on ' + ttName(sid); } }")
    s = rep(s, "frToast('<span>Friends board: <b>'", "frToast('<span>Leaderboard: <b>'")
    # ---- the orb comes out of whoever's knocked out holding it
    s = rep(s, "  if (D.charging) clearCharge(D);\n  D.st = 'ko'; D.fxK = D.fxL = D.fxT = D.fxShk = 0;", "  if (D.charging) clearCharge(D);\n  if (D.orbSaved) orbDrop(D); // (v428)\n  D.st = 'ko'; D.fxK = D.fxL = D.fxT = D.fxShk = 0;")
    s = rep(s, "function netOrbLost(m) { const D = netBlob(m.slot); if (D && D.orbSaved) orbFade(D); }",
               "function netOrbLost(m) { const D = netBlob(m.slot); if (!D || !D.orbSaved) return; if (m.why === 'ko') { D.orbSaved = null; D.orbT = 0; } else orbFade(D); } // (v428: knocked out: it came out of them)")
    s = rep(s, "  orb.g.visible = true; orb.ring.visible = true; if (state === 'play') { AU.orb(); kick($('orbFlash'), 'on'); popText('Orb!'); }",
               "  orb.g.visible = true; orb.ring.visible = true; if (state === 'play') { AU.orb(); kick($('orbFlash'), 'on'); const dd = Number.isInteger(m.dropped) ? netBlob(m.dropped) : null; popText(dd ? (dd === P ? 'You dropped your orb!' : nameOf(dd) + ' dropped an orb!') : 'Orb!'); }")
    # ---- a Paint Storm keeps its caster's tank full while it rains
    s = rep(s, "  if (D.orbSaved && state === 'play') {", "  if (stormList.length && stormList.some(S => S.by === D && !S.fade)) D.paint = 1; // (v428: your storm keeps your tank full)\n  if (D.orbSaved && state === 'play') {")
    # ---- Shuffle on the canvas picker: another canvas, at random
    s = rep(s, "function shuffleCanvas() {\n  if (building || state !== 'menu') return;",
               "function shuffleCanvas() {\n  if (building || state !== 'menu') return;\n"
               "  if (menuPage === 'worlds') { // (v428) another canvas, at random: any open one but this\n"
               "    const pool = [...worldBtns.map(b => b.dataset.s).filter(s => s !== 'next' && s !== 'season'), ...[...$('seasonGrid').children].map(b => b.dataset.s)].filter((s, i, a) => s && s !== stageSel && a.indexOf(s) === i && STAGE_THEMES[s]);\n"
               "    if (pool.length) { const s = pool[Math.floor(Math.random() * pool.length)]; closeSeason(); selectWorld(s); shufT = performance.now(); centerWorld(worldBtns.find(b => b.dataset.s === s) || worldBtns.find(b => b.dataset.s === 'season'), true); renderWorlds(); return; } }")
    s = rep(s, "gallery.addEventListener('scroll', () => { if (galT) return;", "let shufT = 0; // (v428: a shuffle's glide to its canvas passes others: they aren't picked on the way)\ngallery.addEventListener('scroll', () => { if (galT || performance.now() - shufT < 1100) return;")
    return s
