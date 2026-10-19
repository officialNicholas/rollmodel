"""v351: the game uses more of the iPhone it runs on (with the matching changes in the iOS app).

- Haptics that feel like iOS's own: a win, a purchase, a reward claimed and a finished craft give the "success" feel; a purchase that
  can't go through and an ad that didn't come give the "error" feel; and a choice changing (Settings' switches, the difficulty, the
  tabs, the shop's filters, a paint colour, the canvas in the middle of the vote) gives the light tick of a picker. They follow the
  phone's System Haptics setting. In a browser they fall back to short buzzes.
- The App Store's rating prompt, at a good moment: back in the lobby from a win, once the player has 3 wins and 8 matches, once per
  game build (iOS shows it at most three times a year, and never in TestFlight).
- A nudge when a craft is done. The first craft long enough for one (a minute or more, outside Ol' Bloop's lesson) asks in the
  game's own card, "Get a nudge?", and only a yes brings up iOS's permission prompt. After that each craft schedules a notification
  for when it's done ("The Giant is ready!"), called off if it's finished in the game first (Skip, or the game was open).
- Game Center: the player is signed in from the lobby (never mid-match, and not before the first lesson's done). A Time trial's
  score goes on that canvas's Game Center leaderboard ("rm.trial." and the canvas's id), and the Time trial board gets a
  "Game Center" button once that leaderboard exists. Until the leaderboards are made in App Store Connect, nothing of it shows.
- Ads: a wait the game gives up on also tells the app to stop waiting, so an ad can't come up later; and a reward still counts if
  iOS had to start the game's page over while the ad was up.
- Sound: the page asks for the "ambient" audio session, as the app does: game sound mixes with the player's own music and follows
  the ring/silent switch.
- No long-press menu anywhere but in text boxes.
- The App Store build has no error lines on screen or in Settings ("Error 1: ...", "Last error: ...") and no hidden performance
  readout (five taps on the version line); an Xcode build and the browser keep them."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- the app: what it is, sound, the long-press menu
    s = rep(s, "if (NATIVE && NATIVE.platform === 'ios' && !NATIVE.tester) document.documentElement.classList.add('appstore');\n",
               "if (NATIVE && NATIVE.platform === 'ios' && !NATIVE.tester) document.documentElement.classList.add('appstore');\n"
               "const APPSTORE = document.documentElement.classList.contains('appstore');\n"
               "// (v351) game sound mixes with the player's own music and follows the ring/silent switch, as iOS games do (the app asks the same)\n"
               "try { if (navigator.audioSession) navigator.audioSession.type = 'ambient'; } catch (e) {}\n"
               "// (v351) no long-press menu, but in text boxes\n"
               "document.addEventListener('contextmenu', e => { if (!(e.target && e.target.closest && e.target.closest('input, textarea'))) e.preventDefault(); });\n")
    # ---- haptics that feel like iOS's own
    s = rep(s, "const buzz = p => { try { navigator.vibrate && navigator.vibrate(p); } catch (e) {} };\n",
               "const buzz = p => { try { navigator.vibrate && navigator.vibrate(p); } catch (e) {} };\n"
               "// (v351) a moment named the way iOS names it: \"success\" (a win, a purchase, a reward), \"error\" (it didn't work), \"select\" (a choice\n"
               "// changed). The iPhone app plays iOS's own feel for each; a browser gets a short buzz\n"
               "const HAP_WEB = { success: [12, 50, 18], warning: [20, 40, 20], error: [26, 40, 26, 40, 26], select: 5 };\n"
               "const hap = k => { try { const h = window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.haptic; if (h) { h.postMessage(k); return; } } catch (e) {} buzz(HAP_WEB[k] || 8); };\n")
    # a choice changing: the light tick of a picker (not for one already made)
    s = rep(s, "window.addEventListener('nativead', e => adOn((e && e.detail) || {}));\n",
               "window.addEventListener('nativead', e => adOn((e && e.detail) || {}));\n"
               "// (v351) a choice changing gives the light tick of a picker: Settings' switches, the difficulty, the tabs, the shop's filters, a paint\n"
               "document.addEventListener('click', e => { const b = e.target && e.target.closest && e.target.closest('.seg button, [role=\"tab\"], .lkchip, .sw');\n"
               "  if (b && !b.disabled && b.getAttribute('aria-pressed') !== 'true' && b.getAttribute('aria-selected') !== 'true') hap('select'); }, true);\n")
    s = rep(s, "const b = worldAt(); if (b && b.dataset.s !== 'next' && b.dataset.s !== stageSel) selectWorld(b.dataset.s); else renderGo();",
               "const b = worldAt(); if (b && b.dataset.s !== 'next' && b.dataset.s !== stageSel) { hap('select'); selectWorld(b.dataset.s); } else renderGo();")
    s = rep(s, "$('gPrev').addEventListener('click', () => { AU.init(); stepWorld(-1); }); $('gNext').addEventListener('click', () => { AU.init(); stepWorld(1); });",
               "$('gPrev').addEventListener('click', () => { AU.init(); hap('select'); stepWorld(-1); }); $('gNext').addEventListener('click', () => { AU.init(); hap('select'); stepWorld(1); });")
    # success: a purchase, a claim, a finished craft, a win (or a new best)
    s = rep(s, "  AU.power(); buzz([12, 30, 18]); showDrops(); kick($('lkCoin'), 'bump'); sgDressCheer(); lkToast('Bought! It’s in your locker');",
               "  AU.power(); hap('success'); showDrops(); kick($('lkCoin'), 'bump'); sgDressCheer(); lkToast('Bought! It’s in your locker');")
    s = rep(s, "AU.nope(); kick($('lkDo'), 'nope');", "AU.nope(); hap('error'); kick($('lkDo'), 'nope');", 2)
    s = rep(s, "  AU.xplay('coins', { v: 0.8 }) || AU.power(); buzz([12, 40, 12]);",
               "  AU.xplay('coins', { v: 0.8 }) || AU.power(); hap('success');")
    s = rep(s, "d.craft = null; if (!d.own.includes(c.id)) d.own.push(c.id); d.fresh = c.id; save(); AU.fanfare && AU.fanfare(); return false; }",
               "d.craft = null; if (!d.own.includes(c.id)) d.own.push(c.id); d.fresh = c.id; save(); AU.fanfare && AU.fanfare(); craftDoneNative(); return false; }")
    s = rep(s, "d.craft.end = Date.now(); craftTick(); AU.ui(); buzz([10, 30, 10]); renderStrokes(); stToast(stReady(id)); }",
               "d.craft.end = Date.now(); craftTick(); AU.ui(); renderStrokes(); stToast(stReady(id)); } // (v351: craftTick gives the success feel)")
    s = rep(s, "  paintName(); showRep(info);\n",
               "  paintName(); showRep(info);\n"
               "  if (solo ? info.newBest : info.win > 0) setTimeout(() => hap('success'), 420); // (v351: as the verdict lands)\n")
    # error: the ad didn't come
    s = rep(s, "  clearTimeout(ADW.popT); clearTimeout(ADW.rt); ADW.popT = ADW.rt = 0; const w = $('adWait'), t = AD_WHY[why] || AD_WHY.noads;",
               "  clearTimeout(ADW.popT); clearTimeout(ADW.rt); ADW.popT = ADW.rt = 0; const w = $('adWait'), t = AD_WHY[why] || AD_WHY.noads; hap('error');")
    # ---- ads: a wait given up on tells the app too; a reward counts on a page started over under the ad
    s = rep(s, "clearTimeout(ADS.t); ADS.t = setTimeout(() => adFail('slow', true), AD_WAIT_MS + 15000); // (the app answers well before this: it's in case it never does)",
               "clearTimeout(ADS.t); ADS.t = setTimeout(() => { if (ADS.mode === 'app') nativeSay('ads', { cancel: true }); adFail('slow', true); }, AD_WAIT_MS + 15000); // (the app answers well before this: it's in case it never does; v351: and the app stops waiting too)")
    s = rep(s, "function adReward() {\n  if (!ADS.id) return; ADS.earned = true;",
               "function adReward() {\n  if (!ADS.id) { const d = store.strokes; ADS.id = d && d.craft ? d.craft.id : null; if (!ADS.id) return; } // (v351: a page started over under the ad)\n  ADS.earned = true;")
    # ---- a nudge when a craft is done
    s = rep(s, "d.craft = { id, end: Date.now() + sp.craft * 60000 }; save(); AU.pop(); buzz(10); renderStrokes(); adWarm(); }",
               "d.craft = { id, end: Date.now() + sp.craft * 60000 }; save(); AU.pop(); buzz(10); renderStrokes(); adWarm(); noteSync(); noteOffer(id); }")
    s = rep(s, '\n\n  <div class="modal" id="pause" hidden>',
               '\n\n  <div class="modal" id="noteModal" hidden>\n'
               '    <div class="card" role="dialog" aria-modal="true" aria-labelledby="noteTitle" aria-describedby="noteNote">\n'
               '      <h2 class="ctitle" id="noteTitle">Get a nudge?</h2>\n'
               '      <p class="cnote" id="noteNote"></p>\n'
               '      <button class="btn play sm" id="noteYes" type="button">Nudge me</button>\n'
               '      <button class="btn" id="noteNo" type="button">Not now</button>\n'
               '    </div>\n'
               '  </div>\n\n  <div class="modal" id="pause" hidden>')
    s = rep(s, "#delModal{z-index:13}\n",
               "#delModal{z-index:13}\n"
               "/* (v351) Get a nudge? (the first long craft, in the iPhone app) */\n"
               "#noteModal{z-index:13}\n"
               "#noteModal .card{width:min(100%,360px)}\n"
               "#noteModal .cnote b{font-weight:900;color:inherit}\n")
    s = rep(s, "// ---------- (v335) the ad on its way.",
               "// ---------- (v351) a nudge when a craft is done: a notification from the iPhone app (NotifyBridge.swift). The first craft long enough\n"
               "// for one asks first in the game's own card, and only a yes brings up iOS's permission prompt. Once allowed, each craft schedules\n"
               "// one for when it's done, called off when it's finished in the game first ----------\n"
               "const NOTE = { status: '' };\n"
               "const noteApp = () => !!(window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.notify);\n"
               "window.addEventListener('nativenotify', e => { const d = (e && e.detail) || {}; if (d.status) { NOTE.status = d.status; noteSync(); } });\n"
               "function noteSync() { try {\n"
               "  if (!noteApp() || NOTE.status !== 'allowed') return; const c = (store.strokes || {}).craft;\n"
               "  if (c && c.end - Date.now() > 60000) nativeSay('notify', { id: 'craft', at: c.end, title: stReady(c.id), body: 'Crafting’s done. Come and try it out.' });\n"
               "  else nativeSay('notify', { cancel: 'craft' });\n"
               "} catch (e) {} }\n"
               "// a craft done in the game: the success feel if the Abilities page is up to show it, and its nudge called off\n"
               "function craftDoneNative() { try { if (strokesOpen()) hap('success'); noteSync(); } catch (e) {} }\n"
               "function noteOffer(id) { try {\n"
               "  if (!noteApp() || NOTE.status !== 'ask' || store.noteAsked || tutPh() !== 'done' || (store.tut && store.tut.strokes === 'on') || craftLeft() < 60000) return;\n"
               "  store.noteAsked = 1; save();\n"
               "  setTimeout(() => { if (state !== 'menu' || !strokesOpen()) return; $('noteNote').innerHTML = 'Get a nudge when ' + (stIsSkill(id) ? '' : 'the ') + '<b>' + frEsc(spName(id)) + '</b> is ready, even with the game closed? Only when something you’re crafting is done.';\n"
               "    $('noteModal').hidden = false; setTimeout(() => $('noteYes').focus({ preventScroll: true }), 30); }, 700);\n"
               "} catch (e) {} }\n"
               "function noteClose() { const m = $('noteModal'); if (m.hidden) return; m.hidden = true; }\n"
               "$('noteYes').addEventListener('click', () => { AU.init(); AU.ui(); noteClose(); nativeSay('notify', { ask: true }); });\n"
               "$('noteNo').addEventListener('click', () => { AU.init(); AU.ui(); noteClose(); });\n"
               "$('noteModal').addEventListener('click', e => { if (e.target === $('noteModal')) noteClose(); });\n"
               "document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('noteModal').hidden) { e.preventDefault(); e.stopPropagation(); noteClose(); } }, true);\n"
               "if (noteApp()) nativeSay('notify', { status: true });\n"
               "// ---------- (v335) the ad on its way.")
    # ---- the rating prompt: back in the lobby from a win
    s = rep(s, "$('menuBtn').addEventListener('click', uiClick(toMenu));",
               "$('menuBtn').addEventListener('click', uiClick(() => { const won = !!(endInfo && endInfo.win > 0 && endInfo.mode !== 'solo'); toMenu(); if (won) reviewAfterWin(); }));\n"
               "// (v351) the App Store's rating prompt, at a good moment: back in the lobby from a win, once the player has 3 wins and 8 matches, once\n"
               "// per game build. iOS decides whether it shows (at most three times a year; never in TestFlight)\n"
               "const verTag = () => { const m = /(\\d+)\\)?\\s*$/.exec(((document.querySelector('p.ver') || {}).textContent || '').trim()); return m ? m[1] : ''; };\n"
               "function reviewAfterWin() {\n"
               "  if (!NATIVE || NATIVE.platform !== 'ios' || tutPh() !== 'done') return;\n"
               "  const wins = Object.values(store.wins || {}).reduce((a, b) => a + (+b || 0), 0), v = verTag();\n"
               "  if (wins < 3 || (store.runs | 0) < 8 || !v || store.revAsk === v) return;\n"
               "  // (once the lobby's calm: back from the match, no card or transition up; it gives up after 10 seconds)\n"
               "  let n = 0; const t = setInterval(() => { if (++n > 20) return clearInterval(t); if (n < 3 || state !== 'menu' || !lobbyOn() || irisBusy || document.querySelector('.modal:not([hidden])')) return;\n"
               "    clearInterval(t); store.revAsk = v; save(); nativeSay('device', { review: true }); }, 500);\n"
               "}")
    # ---- Game Center: signed in from the lobby; a Time trial's score on its canvas's leaderboard; a button on the board once it exists
    s = rep(s, '<span>New week in <b id="ttLeft">7d</b></span></p>',
               '<span>New week in <b id="ttLeft">7d</b></span><button class="ttgc" id="ttGc" type="button" hidden>Game Center</button></p>')
    s = rep(s, ".ttfoot svg{width:16px;height:16px}.ttfoot b{color:var(--black)}",
               ".ttfoot svg{width:16px;height:16px}.ttfoot b{color:var(--black)}\n"
               "/* (v351) Game Center's own view of this canvas's leaderboard (the iPhone app, once the leaderboard exists) */\n"
               ".ttgc{appearance:none;position:relative;margin-left:10px;padding:7px 12px;border:0;border-radius:999px;background:#171320;color:#fff;font:800 12px/1 var(--font-ui);letter-spacing:.01em;cursor:pointer;-webkit-tap-highlight-color:transparent}\n"
               ".ttgc::after{content:\"\";position:absolute;inset:-9px -6px}\n"
               ".ttgc:active{transform:translateY(1px)}")
    s = rep(s, "  $('ttBody').innerHTML = h;\n}\nfunction openTT(sid, hiT) {",
               "  $('ttBody').innerHTML = h; gcPaint();\n}\nfunction openTT(sid, hiT) {")
    s = rep(s, "  if (mode === 'solo') { endInfo.sid = TH.id; endInfo.tt = ttAdd(TH.id, ry); frTrial(TH.id, ry); }",
               "  if (mode === 'solo') { endInfo.sid = TH.id; endInfo.tt = ttAdd(TH.id, ry); frTrial(TH.id, ry); gcScore(TH.id, ry); }")
    s = rep(s, "$('ttStrip').addEventListener('click', () => { AU.init(); openTT(ttSid()); });",
               "$('ttStrip').addEventListener('click', () => { AU.init(); openTT(ttSid()); });\n"
               "// (v351) Game Center (GameCenterBridge.swift): the player's signed in from the lobby once the first lesson's done (never mid-match); a\n"
               "// Time trial's score goes on its canvas's leaderboard (rm.trial. and the canvas's id), and the board gets a Game Center button once\n"
               "// that leaderboard exists (made in App Store Connect)\n"
               "const GC = { asked: false, on: false, boards: [] }, gcBoard = sid => 'rm.trial.' + sid;\n"
               "const gcApp = () => !!(window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.gamecenter);\n"
               "window.addEventListener('nativegc', e => { const d = (e && e.detail) || {}; GC.on = !!d.signedIn; GC.boards = Array.isArray(d.boards) ? d.boards : []; gcPaint(); });\n"
               "if (gcApp()) { const iv = setInterval(() => { if (GC.asked) return clearInterval(iv); if (state === 'menu' && lobbyOn() && !irisBusy && tutPh() === 'done') { GC.asked = true; clearInterval(iv); nativeSay('gamecenter', { start: true }); } }, 2500); }\n"
               "function gcScore(sid, p) { if (GC.on) nativeSay('gamecenter', { board: gcBoard(sid), score: Math.max(0, Math.round(p)) }); }\n"
               "function gcPaint() { try { const b = $('ttGc'); if (b) b.hidden = !(GC.on && ttSel && GC.boards.includes(gcBoard(ttSel))); } catch (e) {} }\n"
               "$('ttGc').addEventListener('click', () => { AU.init(); AU.ui(); if (GC.on && ttSel) nativeSay('gamecenter', { show: gcBoard(ttSel) }); });")
    # ---- the App Store build: no error lines, no hidden performance readout
    s = rep(s, "html.appstore .ucode{display:none!important}",
               "html.appstore .ucode{display:none!important}\n"
               "/* (v351) nor error lines on screen or in Settings (they're still kept, for an Xcode build) */\n"
               "html.appstore #errLine,html.appstore #lastErr{display:none!important}")
    s = rep(s, "$('setVer').addEventListener('click', () => { const now = performance.now();",
               "$('setVer').addEventListener('click', () => { if (APPSTORE) return; /* (v351: not in the App Store build) */ const now = performance.now();")
    s = rep(s, "if (store.perfHud) setTimeout(() => perfHudSet(true), 0);",
               "if (store.perfHud && !APPSTORE) setTimeout(() => perfHudSet(true), 0);")
    return s
