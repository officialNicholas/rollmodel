"""v354: play stats for the admin dashboard, and live prices.

- Play stats: the game sends anonymous stats to its Supabase project (rm_track, supabase/migrations/20261018000000_liveops.sql), so the
  dashboard (admin/) can show how it's played. They carry a random id made for this install (never a name or a device id) and the
  install's state now (rank, xp, dabs, tutorial step, platform and versions), with events: sessions, matches (mode, online, result,
  coverage, knock-outs, length, canvas, difficulty), the tutorial steps reached, Paint Shop looks and buys, dabs earned and where from,
  Strokes crafts and ad skips, rewarded ads (asked, shown, rewarded, failed) and ranks reached. Batched, and sent about once a minute
  while playing and when the app is put away; kept on the phone while offline. While the player is signed in, the batch carries their
  token, so the install is linked to them (the server never takes that from the body). Only the iPhone app sends them (or the
  game pointed at a local test project): the web page is the claude.ai preview, and tests never reach the real project.
- The Privacy Policy explains them, and has a button to turn them off (kept with the phone).
- Live prices: the dashboard can change an item's price. The game asks for the live prices (rm_config) at launch, when it comes back
  (at most every 10 minutes) and whenever a batch says they changed, keeps them with the phone so they hold offline, and applies them
  in PRICE() after the lesson's own prices and the gifts. The Paint Shop redraws if it's open.
- The install id, the opt-out, the live prices and the tutorial steps already sent belong to the phone: never sent up with the
  account's progress or replaced by it, and kept through Restart Game and Log out.
- The iPhone app tells the game its version (DeviceBridge.swift), which goes with the stats."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""// ---------- (v354) play stats for the admin dashboard, and live prices. Anonymous stats go to the game's Supabase project (rm_track):
// a random id for this install (never a name or a device id), the install's state now, and events (sessions, matches, the tutorial
// steps reached, Paint Shop looks and buys, dabs earned, crafts and ad skips, rewarded ads, ranks). Batched, sent about once a minute
// while playing and when the app is put away, kept on the phone while offline. The Privacy Policy turns them off. Live prices set in
// the dashboard (rm_config) override PRICES; kept with the phone, asked for at launch, on coming back (at most every 10 minutes) and
// when a batch says they changed ----------
var ST = { q: [], secs: 0, t0: 0, busy: false, dead: false, next: 0, fails: 0, seen: new Set(), lastStep: -1, hidAt: 0, cfgAt: 0, cfgBusy: false, n: 0, gv: 0, up: false };
const ST_Q = 'rm.stq', ST_MAX = 400, ST_EVERY = 60, ST_CFG_MS = 600000;
// the server's only asked from the iPhone app, or from a local test project (the web page is the claude.ai preview)
function stNet() { try { return !!SB_CFG && !NET_WALLED && (!!NATIVE || !/\.supabase\.co$/i.test(new URL(SB_CFG.url).hostname)); } catch (e) { return false; } }
function stState() { if (!store.st || typeof store.st !== 'object') store.st = {}; const s = store.st; if (!s.iid) { s.iid = stUuid(); save(); } if (!Array.isArray(s.tut)) s.tut = []; return s; }
function stUuid() { try { if (crypto.randomUUID) return crypto.randomUUID(); } catch (e) {} const b = new Uint8Array(16); crypto.getRandomValues(b); b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128; const h = [...b].map(x => x.toString(16).padStart(2, '0')).join(''); return h.slice(0, 8) + '-' + h.slice(8, 12) + '-' + h.slice(12, 16) + '-' + h.slice(16, 20) + '-' + h.slice(20); }
const stOff = () => !!(store.st && store.st.off);
// a live price for this item (or -1): the dashboard's, as last heard
function stLive(id) { const p = store.st && store.st.lp && store.st.lp.prices, v = p && p[id]; return Number.isInteger(v) && v >= 0 && v <= 100000 ? v : -1; }
function stEv(e) { try { if (stOff()) return; ST.q.push(e); if (ST.q.length > ST_MAX) ST.q.splice(0, ST.q.length - ST_MAX); } catch (x) {} }
// a tutorial step reached (each once per install)
function stStep(id) { try { const s = stState(); if (s.tut.includes(id)) return; s.tut.push(id); stEv({ k: 'tut', s: id }); } catch (e) {} }
// an item looked at in the Paint Shop (once a session), and whether it could be bought right then (in stock, and enough dabs)
function stView(w) { try { if (ST.seen.has(w.id)) return; ST.seen.add(w.id); stEv({ k: 'view', i: w.id, a: (owns(w.id) || !needFind(w)) && (store.drops || 0) >= PRICE(w) }); } catch (e) {} }
// a rewarded ad's progress (real ads only: the app's)
function stAd(r) { try { if (ADS.mode === 'app') stEv({ k: 'ad', pl: ADS.pl || 'craft', r }); } catch (e) {} }
// a match played to its end, and the dabs it paid. The first lesson counts by its steps, not as a match
function stMatch() { try {
  const e = endInfo; if (!e) return;
  if (!tut) { const on = !!NM, ev = { k: 'match', m: e.mode, on, cov: Math.round(e.you || 0), ko: P.kos | 0, s: Math.round(e.time || 0), st: TH.id };
    if (e.mode !== 'solo') ev.r = e.win > 0 ? 'win' : e.win < 0 ? 'loss' : 'draw';
    if (!on && e.mode !== 'solo') ev.d = String(diff);
    stEv(ev); }
  if (e.drops > 0) stEv({ k: 'earn', src: 'match', n: e.drops });
} catch (x) {} }
// where the tutorial is now: the intro, a step of the lesson, or the phase after it
function stTutNow() { try { if (FL && FL.live) return 'intro'; if (tut && tut.step >= 0 && TUT_STEPS[tut.step]) return 'l:' + TUT_STEPS[tut.step].id; return String((store.tut && store.tut.ph) || ''); } catch (e) { return ''; } }
// once a second: the tutorial steps and the rank reached
function stWatch() {
  const t = store.tut || {}, ph = t.ph, rk = repOf(store.xp || 0).lv, s = stState();
  if ((FL && (FL.due || FL.live)) || store.introDone) stStep('intro');
  if (tut || ['shop', 'locker', 'vote', 'match2', 'done', 'strokes'].includes(ph)) stStep('match'); // (any phase after it: the lesson was started)
  if (tut) { for (let i = Math.max(0, ST.lastStep + 1); i <= tut.step && i < TUT_STEPS.length; i++) stStep('l:' + TUT_STEPS[i].id); ST.lastStep = Math.max(ST.lastStep, tut.step); } else ST.lastStep = -1;
  if (['shop', 'locker', 'vote', 'match2'].includes(ph)) stStep(ph);
  if (ph === 'done' || ph === 'strokes' || t.strokes) stStep('done');
  if (rk >= 2) stStep('rank2');
  if (t.strokes === 'on' || t.strokes === 1 || ph === 'strokes') stStep('strokes');
  if (t.strokes === 1) stStep('strokes_done');
  if (!(s.rk >= 1)) s.rk = rk; else if (rk > s.rk) { s.rk = rk; stEv({ k: 'rank', n: rk }); }
}
// the seconds played while the game was on screen
function stPlay() { const n = performance.now(); if (ST.t0 && !document.hidden) ST.secs += (n - ST.t0) / 1000; ST.t0 = document.hidden ? 0 : n; }
function stKeep() { try { if (stOff() || (!ST.q.length && ST.secs < 1)) localStorage.removeItem(ST_Q); else localStorage.setItem(ST_Q, JSON.stringify({ q: ST.q, secs: Math.round(ST.secs) })); } catch (e) {} }
function stMeta() { const x = store; return { plat: NATIVE && NATIVE.platform === 'ios' ? 'ios' : 'web', av: (NATIVE && NATIVE.appVersion) || undefined, gv: ST.gv || undefined,
  rank: repOf(x.xp || 0).lv, xp: Math.max(0, Math.floor(+x.xp || 0)), dabs: Math.max(0, Math.floor(+x.drops || 0)), tut: stTutNow() || undefined }; }
// a batch to the server. away: the app's being put away (sent so it gets there)
function stFlush(away) {
  if (!ST.up || ST.busy || ST.dead || stOff() || !stNet() || Date.now() < ST.next) return;
  stPlay(); if (!ST.q.length && ST.secs < (away ? 5 : ST_EVERY)) return;
  const s = stState(), ev = ST.q.splice(0, 60), secs = Math.min(3600, Math.round(ST.secs)), meta = Object.assign(stMeta(), { secs });
  ST.secs -= secs; ST.busy = true; stKeep();
  const back = () => { ST.q = ev.concat(ST.q); ST.secs += secs; if (ST.q.length > ST_MAX) ST.q.splice(0, ST.q.length - ST_MAX); };
  const auth = !!(FR.s && FR.s.access_token && FR.s.expires_at - 60 > Date.now() / 1000); // (signed in: the install is theirs. Never a new sign-in for this)
  return sbFetch('/rest/v1/rpc/rm_track', { p_iid: s.iid, p_meta: meta, p_ev: ev }, auth, !!away).then(r => {
    if (r && r.ok) { ST.fails = 0; const lp = s.lp || {}; if (r.v != null && +r.v !== +(lp.v || 0)) stCfg(true); }
    else if (r && r.why === 'rate') { back(); ST.next = Date.now() + 300000; } // (too many: a while before the next)
    // (bad: the server will never take this batch, so it's dropped)
  }).catch(e => {
    back(); if (e && (e.status === 404 || /PGRST202|Could not find the function/i.test(String(e.message || '')))) ST.dead = true; // (the v354 SQL isn't run yet: nothing more this time)
    else { ST.fails = (ST.fails || 0) + 1; ST.next = Date.now() + Math.min(600000, 30000 * Math.pow(2, ST.fails - 1)); }
  }).finally(() => { ST.busy = false; stKeep(); });
}
// the live prices: asked for at launch, on coming back (at most every 10 minutes), and when a batch says they've changed
function stCfg(now) {
  if (!ST.up || ST.cfgBusy || !stNet() || (!now && Date.now() - ST.cfgAt < ST_CFG_MS)) return;
  ST.cfgBusy = true; ST.cfgAt = Date.now();
  sbFetch('/rest/v1/rpc/rm_config', {}, false).then(r => {
    if (!r || typeof r !== 'object' || !r.prices || typeof r.prices !== 'object') return;
    const p = {}; for (const [k, v] of Object.entries(r.prices)) if (/^[a-z0-9_]{1,32}$/.test(k) && Number.isInteger(v) && v >= 0 && v <= 100000) p[k] = v;
    const s = stState(), was = JSON.stringify((s.lp && s.lp.prices) || {}); s.lp = { v: +r.v || 0, prices: p }; save();
    if (JSON.stringify(p) !== was) { try { if (lkOn()) lkRender(); } catch (e) {} } // (the Paint Shop open: its prices redrawn)
  }).catch(() => {}).finally(() => { ST.cfgBusy = false; });
}
// the Privacy Policy's play stats button: off (and the batches waiting are dropped), or back on
function stPrivPaint() {
  const p = $('statsP'); if (!p) return; let b = $('statsTog');
  if (!b) { b = document.createElement('button'); b.type = 'button'; b.className = 'frb adpriv'; b.id = 'statsTog';
    b.addEventListener('click', () => { AU.init(); AU.ui(); const s = stState(); s.off = !s.off; if (s.off) { ST.q = []; ST.secs = 0; } save(); stKeep(); stPrivPaint(); });
    p.after(b); }
  b.textContent = stOff() ? 'Play stats are off. Turn them on' : 'Turn off play stats';
}
function stBoot() { try {
  ST.up = true; ST.t0 = document.hidden ? 0 : performance.now();
  { const v = document.querySelector('#howModal .ver'), m = v && /(\d+)/.exec(v.textContent); ST.gv = m ? +m[1] : 0; }
  stState();
  if (!stOff()) { try { const o = JSON.parse(localStorage.getItem(ST_Q) || 'null'); if (o && Array.isArray(o.q)) ST.q = o.q.concat(ST.q).slice(-ST_MAX); if (o && o.secs > 0) ST.secs += Math.min(36000, +o.secs || 0); } catch (e) {} } // (what an earlier visit didn't get to send, first)
  stEv({ k: 'open' });
  setInterval(() => { try { stWatch(); if (++ST.n % ST_EVERY === 10) stFlush(false); } catch (e) {} }, 1000);
  setTimeout(() => stCfg(true), 2500);
  document.addEventListener('visibilitychange', () => { try {
    if (document.hidden) { stPlay(); ST.hidAt = Date.now(); stFlush(true); stKeep(); }
    else { ST.t0 = performance.now(); if (ST.hidAt && Date.now() - ST.hidAt > 30 * 60000) stEv({ k: 'open' }); ST.hidAt = 0; stCfg(false); } // (back after half an hour: a new session)
  } catch (e) {} });
} catch (e) {} }
setTimeout(stBoot, 1500); // (once the rest of the page's script has run)
"""

PRIV = ('<h3>Play stats</h3><p id="statsP">To make the game better, it sends us anonymous stats about how it’s played: the modes and canvases you play '
        'and how matches go, how far you’ve got in the lessons, your rank and dabs, what you look at and buy in the Paint Shop, what you craft, and '
        'whether ads you chose to watch finished. They go with a random number made for this copy of the game, not your name or anything that '
        'identifies your device. While you’re signed in, they’re linked to your account. We use them only to improve the game, never for ads, and we '
        'don’t sell them. You can turn them off here.</p>')

def apply(s):
    # ---- the stats and live prices, just before the Paint Shop's buy (PRICE is defined just above)
    s = rep(s, "function buyItem(id) {", JS + "function buyItem(id) {")
    # live prices: after the lesson's own and the gifts
    s = rep(s, "if (w.gift) return 0; /* (v330: a gift costs nothing) */ return PRICES[w.id]",
               "if (w.gift) return 0; /* (v330: a gift costs nothing) */ { const lp = stLive(w.id); if (lp >= 0) return lp; } /* (v354: a live price from the dashboard) */ return PRICES[w.id]")
    # ---- the events
    s = rep(s, "store.drops -= PRICE(w); OWNED.add(id);", "{ const p = PRICE(w); store.drops -= p; stEv({ k: 'buy', i: id, p }); } OWNED.add(id);")
    s = rep(s, "d.craft = { id, end: Date.now() + sp.craft * 60000 }; save();", "d.craft = { id, end: Date.now() + sp.craft * 60000 }; save(); stEv({ k: 'craft', i: id });")
    s = rep(s, "  else if (!again) { LKR.prev = bought(w.id) ? null : lkWith(myLook, w);",
               "  else if (!again) { if (!bought(w.id)) stView(w); LKR.prev = bought(w.id) ? null : lkWith(myLook, w);")
    s = rep(s, "  else { LKR.sel = 'w:' + id; LKR.prev = LKR.tab === 'shop' && !bought(id) ? lkWith(myLook, w) : null;",
               "  else { LKR.sel = 'w:' + id; if (LKR.tab === 'shop' && !bought(id)) stView(w); LKR.prev = LKR.tab === 'shop' && !bought(id) ? lkWith(myLook, w) : null;")
    s = rep(s, "endInfo.drops = drops;\n  save(); tutEndMatch();", "endInfo.drops = drops;\n  stMatch(); save(); tutEndMatch();", 2)
    s = rep(s, "if (owe) { store.drops = (store.drops || 0) + owe * COMM_DABS;", "if (owe) { store.drops = (store.drops || 0) + owe * COMM_DABS; stEv({ k: 'earn', src: 'comm', n: owe * COMM_DABS });")
    s = rep(s, "const from = store.drops || 0; store.drops = from + COMM_DABS;", "const from = store.drops || 0; store.drops = from + COMM_DABS; stEv({ k: 'earn', src: 'comm', n: COMM_DABS });")
    s = rep(s, "if (won) { store.drops = (store.drops || 0) + won;", "if (won) { store.drops = (store.drops || 0) + won; stEv({ k: 'earn', src: 'board', n: won });")
    s = rep(s, "if (bonus) { store.drops = (store.drops || 0) + bonus;", "if (bonus) { store.drops = (store.drops || 0) + bonus; stEv({ k: 'earn', src: 'lesson', n: bonus });")
    # rewarded ads: asked (and which: the Strokes lesson's own craft, or any other), shown, rewarded, failed; a craft finished by one
    s = rep(s, "ADS.id = d.craft.id; ADS.earned = false; ADS.open = false; AU.ui(); buzz(6); sgSkipPaint();",
               "ADS.id = d.craft.id; ADS.earned = false; ADS.open = false; AU.ui(); buzz(6); sgSkipPaint(); ADS.pl = adLesson() ? 'lesson' : 'craft'; stAd('ask');")
    s = rep(s, "  if (m.e === 'open') { clearTimeout(ADS.t); adWaitHide();", "  if (m.e === 'open') { stAd('shown'); clearTimeout(ADS.t); adWaitHide();")
    s = rep(s, "  ADS.earned = true; const d = store.strokes;", "  if (!ADS.earned) stAd('reward'); ADS.earned = true; const d = store.strokes;")
    s = rep(s, "  const was = ADS.open; adDone(); if (was) {", "  stAd('fail'); const was = ADS.open; adDone(); if (was) {")
    s = rep(s, "function adPayoff() { const id = ADS.id; adDone(); const d = strokesOf(); if (id && d.craft && d.craft.id === id) craftSkip(); else",
               "function adPayoff() { const id = ADS.id; adDone(); const d = strokesOf(); if (id && d.craft && d.craft.id === id) { stEv({ k: 'skip', i: id }); craftSkip(); } else")
    # ---- what belongs to the phone: never sent with the account's progress, kept through Restart Game and Log out
    s = rep(s, "'netTok', 'csHi'], CS_BOOK", "'netTok', 'csHi', 'st'], CS_BOOK")
    s = rep(s, "for (const k of ['muted', 'sfxOff', 'musicOff', 'gfx', 'orient', 'qLv', 'qSt'])", "for (const k of ['muted', 'sfxOff', 'musicOff', 'gfx', 'orient', 'qLv', 'qSt', 'st'])", 2)
    # ---- the Privacy Policy: what the stats are, and the button that turns them off
    s = rep(s, "<p>Updated October 16, 2026.</p>", "<p>Updated October 18, 2026.</p>")
    s = rep(s, "<h3>Who has it</h3>", PRIV + "<h3>Who has it</h3>")
    s = rep(s, "<p>Settings › Delete account removes your account and everything above from our server for good. Restart Game in Settings clears this device.</p>",
               "<p>Settings › Delete account removes your account and everything above from our server for good. The play stats stay, but no longer linked to you. Restart Game in Settings clears this device.</p>")
    s = rep(s, "if (k === 'priv') adPrivPaint();", "if (k === 'priv') { adPrivPaint(); stPrivPaint(); }")
    return s
