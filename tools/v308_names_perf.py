"""v308: names are only reserved with an account, and the game takes less out of a phone.

- A display name is checked on the phone alone until the player makes an account. The first launch's name card and Rename in the lobby
  check only that a name is allowed (length, letters, nothing rude, nothing reserved), with no request to the server, so the game plays
  fully offline. Nothing is made on the server at first launch any more: no anonymous player, no name held. The name is reserved when
  the player makes an account: the account form checks it against everyone's as it's typed ("Taken. Try another"), and making the
  account claims it. With an account, Rename goes through the server as before. Friends and the Time trial's Friends board ask for an
  account instead of starting a player in the background.
- Performance. Measured against v303 (before online play) the game's own work per frame is the same (about 7.5 ms in a Versus match
  here), so nothing online runs heavily in the background. What the phone pays for regardless is cut back:
  - the 3D lobby holds still behind screens that cover it (Settings, How to play, the terms, the account form, the name card, the
    Time trial board), as it already did under Commissions, Friends and the Online sheet, instead of drawing every frame unseen;
  - the + spots beside you in the lobby no longer blur the live 3D behind them (a blur over a moving picture is redone every frame);
  - when frames are well behind (median slower than about 27 a second), the quality steps down two or three notches at once instead of
    one, so a struggling phone settles in seconds rather than tens of seconds.
- A performance readout for finding where a phone struggles: tap the version line in Settings five times. Top left, once a second:
  frames per second, the median and worst frame, the game's own work per frame, the quality step and what it holds, and the draw
  calls and triangles. Five more taps hide it."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HUD = r"""
// ---------- (v308) a performance readout: tap the version line in Settings five times (and five more to hide it). Once a second: frames
// per second, the median and worst frame, the game's own work per frame, the quality step and what it holds (resolution, bloom, depth
// blur, the see-through copy, the floor mirror, shadows), and the draw calls and triangles drawn ----------
const PH = { on: false, el: null, iv: [], js: 0, at: 0, taps: 0, tapAt: 0, calls: 0, tris: 0, frames: 0 };
function perfHudSet(on) {
  PH.on = !!on; store.perfHud = PH.on ? 1 : 0; save();
  if (PH.on && !PH.el) { PH.el = document.createElement('pre'); PH.el.className = 'perfhud'; PH.el.setAttribute('aria-hidden', 'true'); document.body.appendChild(PH.el); }
  if (PH.el) PH.el.hidden = !PH.on; try { renderer.info.autoReset = !PH.on; renderer.info.reset(); } catch (e) {}
  PH.iv.length = 0; PH.js = 0; PH.frames = 0; PH.calls = 0; PH.tris = 0; PH.at = performance.now();
}
function perfHudFrame(ft) {
  if (ft > 0 && ft < 2) PH.iv.push(ft * 1000); PH.js += lastCpu * 1000; PH.frames++;
  try { const r = renderer.info.render; PH.calls += r.calls; PH.tris += r.triangles; renderer.info.reset(); } catch (e) {}
  const now = performance.now(); if (now - PH.at < 1000 || !PH.el) return;
  const a = PH.iv.slice().sort((x, y) => x - y), n = a.length, q = Q_LAD[qLvl] || {}, f = Math.max(1, PH.frames);
  PH.el.textContent = Math.round(n * 1000 / (now - PH.at)) + ' fps   median ' + (n ? a[n >> 1].toFixed(1) : '-') + '   worst ' + (n ? a[n - 1].toFixed(0) : '-') + ' ms\n'
    + 'game ' + (PH.js / f).toFixed(1) + ' ms a frame   ' + (GFX === 'hi' ? 'Graphics' : 'Performance') + (NATIVE ? '   app' : '   web') + '\n'
    + 'quality ' + qLvl + '/' + (Q_LAD.length - 1) + '   x' + curPR + (q.bloom ? ' bloom' : '') + (q.dof ? ' blur' : '') + (q.grab ? ' copy' : '') + (q.mirror ? ' mirror' : '') + ' shadows ' + ['full', 'lite', 'still'][shadowLite || 0] + '\n'
    + 'draws ' + Math.round(PH.calls / f) + '   triangles ' + Math.round(PH.tris / f / 1000) + 'k';
  PH.iv.length = 0; PH.js = 0; PH.frames = 0; PH.calls = 0; PH.tris = 0; PH.at = now;
}
$('setVer').addEventListener('click', () => { const now = performance.now(); PH.taps = now - PH.tapAt < 1500 ? PH.taps + 1 : 1; PH.tapAt = now; if (PH.taps >= 5) { PH.taps = 0; perfHudSet(!PH.on); AU.ui(); } });
if (store.perfHud) setTimeout(() => perfHudSet(true), 0);
// (v308) screens that cover the lobby: the 3D lobby holds still behind them instead of drawing every frame for nobody
let LCOV = null;
function lobbyCovered() { if (!LCOV) LCOV = ['setModal', 'howModal', 'docModal', 'acModal', 'nameModal', 'ttModal'].map(id => document.getElementById(id)).filter(Boolean); for (let i = 0; i < LCOV.length; i++) if (!LCOV[i].hidden) return true; return false; }
"""

CSS = r"""
/* (v308) the performance readout */
.perfhud{position:fixed;left:max(6px,env(safe-area-inset-left));top:max(6px,env(safe-area-inset-top));z-index:9999;margin:0;padding:6px 8px;border-radius:6px;background:rgba(10,8,16,.72);color:#9DFFB0;font:600 10.5px/1.35 ui-monospace,Menlo,monospace;white-space:pre;pointer-events:none}
.perfhud[hidden]{display:none}
"""

def apply(s):
    # ---- names: checked on the phone until there's an account
    a = "const UN_W = {}, UN_FREE = new Map();"
    s = rep(s, a, "const UN_ONLINE = id => id === 'acUser' || ((id === 'nameInput' || id === 'frUnIn') && acctReady()); // (v308: a name is only checked against everyone's, and held, with an account)\n" + a)
    s = rep(s, "if (!SB_CFG || navigator.onLine === false) return show('off', 'Looks good');",
               "if (!UN_ONLINE(id)) return show('ok', 'Looks good'); // (v308: allowed is all a name needs before there's an account)\n    if (!SB_CFG || navigator.onLine === false) return show('off', 'Looks good');")
    s = rep(s, "  const r = await Promise.race([unClaim(n, strict),",
               "  const r = !UN_ONLINE(id) ? { ok: true, name: n, off: true } : await Promise.race([unClaim(n, strict),")
    s = rep(s, "  if (!FR.me) { if (!FR.busy && Date.now() > FR.retryAt && store.name && (tutPh() === 'done' || FR.open)) frStart(); return; }",
               "  if (!FR.me) { if (!FR.busy && Date.now() > FR.retryAt && acctReady() && (tutPh() === 'done' || FR.open)) frStart(); return; } // (v308: nothing on the server before an account)")
    s = rep(s, "if (SB_CFG) { if (!FR.me) frStart(); else { FR.at = 0; frPoll(); } }",
               "if (SB_CFG) { if (!FR.me) { if (acctReady()) frStart(); } else { FR.at = 0; frPoll(); } }") # (v308: opening Friends makes nothing on the server without an account)
    s = rep(s, "  else if (!FR.me && FR.need) h = unPickHtml();\n  else if (!FR.me) h = ",
               "  else if (!FR.me && FR.need) h = unPickHtml();\n  else if (!FR.me && !acctReady()) h = acAskHtml(); // (v308: friends come with an account)\n  else if (!FR.me) h = ")
    s = rep(s, "  if (!FR.me) { if (acOut() || FR.need) return '<p class=\"ttnone\"><b>' + (FR.need ? 'Pick your username' : 'Log in') + ' to race your friends here.</b>Your friends are on the lobby’s Friends button.</p>'; if (!FR.busy && Date.now() > FR.retryAt) frStart();",
               "  if (!FR.me) { if (acOut() || FR.need) return '<p class=\"ttnone\"><b>' + (FR.need ? 'Pick your username' : 'Log in') + ' to race your friends here.</b>Your friends are on the lobby’s Friends button.</p>'; if (!acctReady()) return '<p class=\"ttnone\"><b>Make an account to race your friends here.</b>Friends come with an account: Settings, Account.</p>'; if (!FR.busy && Date.now() > FR.retryAt) frStart();")

    s = rep(s, "'Friends are for players with an account. Your username' + (nm ? ' <b>' + frEsc(nm) + '</b>' : '') + ' and friend code come with you.'",
               "'Friends are for players with an account. Make one to keep your username online and get your friend code.'")

    # ---- performance
    s = rep(s, "|| !onModalEl.hidden))) renderFrame();", "|| !onModalEl.hidden || lobbyCovered()))) renderFrame(); // (v308: and behind every screen that covers it)")
    s = rep(s, "  lastCpu = (performance.now() - cpu0) / 1000;\n}\n// a frame that throws must not take the game with it",
               "  lastCpu = (performance.now() - cpu0) / 1000;\n  if (PH.on) perfHudFrame(rawDt);\n}\n// a frame that throws must not take the game with it")
    s = rep(s, "    qDownFrom = qLvl; qDownAt = qWin; setQ(qLvl + 1); qClean = 0;",
               "    qDownFrom = qLvl; qDownAt = qWin; setQ(qLvl + (med > 0.05 ? 3 : med > 0.0365 ? 2 : 1)); qClean = 0; // (v308: well behind, two or three notches at once)")
    s = rep(s, "-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px);-webkit-tap-highlight-color:transparent;transition:background .15s}\n.slot[hidden]{display:none}",
               "-webkit-tap-highlight-color:transparent;transition:background .15s}\n.slot[hidden]{display:none}")
    s = rep(s, "border-radius:6px;background:rgba(255,255,255,.42);box", "border-radius:6px;background:rgba(255,255,255,.55);box")  # (v308: no live blur behind it, a touch more fill instead)
    a = "function paintSettings() {"
    s = rep(s, a, HUD.lstrip('\n') + a)
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
