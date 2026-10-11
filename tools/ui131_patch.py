#!/usr/bin/env python3
"""v206: smoother play.
- The score bar's liquid read its own size every frame, just after the bar's widths were written, so every frame forced a full
  layout (about a fifth of all per-frame script, and worse on phones). It keeps its size from a ResizeObserver now; the bar's widths
  are only written when they change.
- Once the onboarding is done, the tips no longer look through the whole page for open dialogs every frame.
- The look tunes itself for a frame every refresh, not a good average: each second it counts the frames that came late (a refresh
  missed); four or more and it steps down a notch (depth blur, glow, then resolution a step at a time, then lighter shadows); a long
  clean run with the frame's own work well inside its time and it tries a notch back up, backing off for longer each time a notch
  doesn't hold. The old tuning only reacted below about 49 frames a second and, on a 60 a second screen, could never step back up.
  A phone held to 30 a second (Low Power Mode) is recognised and not dragged down. Where it settles is remembered for next time,
  and a phone starts without the depth blur."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui130_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
def cut(start, end, new):
    global s
    assert s.count(start) == 1, f'start x{s.count(start)}: {start[:80]!r}'
    i = s.index(start); j = s.index(end, i); assert j - i < 6000, 'span too long'
    s = s[:i] + new + s[j + len(end):]
# ---- the liquid bar: its size from a ResizeObserver, not a layout read every frame
rep("  L.clear = () => g.clearRect(0, 0, c.width, c.height);\n",
    "  L.clear = () => g.clearRect(0, 0, c.width, c.height);\n"
    "  L.cw = -1; L.ch = 0; L.measure = () => { L.cw = host.clientWidth; L.ch = host.clientHeight; }; // (its size, kept by an observer: reading it every frame forced a layout every frame)\n"
    "  if (typeof ResizeObserver === 'function') new ResizeObserver(() => L.measure()).observe(host); else addEventListener('resize', () => { L.cw = -1; });\n")
rep("    const w = host.clientWidth, h = host.clientHeight; if (!w || !h || !L.segs.length) return;",
    "    if (L.cw < 0) L.measure(); const w = L.cw, h = L.ch; if (!w || !h || !L.segs.length) return;")
rep("        $('tugYou').style.width = (yS * 100).toFixed(2) + '%'; $('tugCpu').style.width = (cS * 100).toFixed(2) + '%';",
    "        { const wy = (yS * 100).toFixed(2) + '%', wc = (cS * 100).toFixed(2) + '%', ey = $('tugYou'), ecu = $('tugCpu'); if (ey.style.width !== wy) ey.style.width = wy; if (ecu.style.width !== wc) ecu.style.width = wc; }")
# ---- the tips: nothing to do once the onboarding is over
rep("function tutMenuTick() {\n  if (bootHold || !booted || !tutBootEl.classList.contains('gone')",
    "function tutMenuTick() {\n  if (tutPh() === 'done') { if (menu.classList.contains('tutoring')) menu.classList.remove('tutoring'); if (!(state === 'play' && tutTip && tutTip.key === 'protip')) tutHide(); return; } /* (the onboarding is over: nothing to point at, so no hunting the page for open dialogs every frame) */\n"
    "  if (bootHold || !booted || !tutBootEl.classList.contains('gone')")
# ---- the frame's own work, for the tuning below
rep("function frameBody(t) {\n", "function frameBody(t) {\n  const cpu0 = performance.now();\n")
rep("  if (!(state === 'menu' && menuPage === 'worlds')) renderFrame();\n}\n",
    "  if (!(state === 'menu' && menuPage === 'worlds')) renderFrame();\n  lastCpu = (performance.now() - cpu0) / 1000;\n}\n")
# ---- the tuning
cut("// keep it smooth: if frames run long, render at a slightly lower resolution; when there's headroom, go back up\n", "  else perfGood = 0;\n}\n", r"""// keep it smooth: the aim is a new frame every refresh (60 a second on a phone), every time, not a good average. Each second it counts the
// frames that came late (a refresh missed). Four or more and the look steps down a notch; after a long clean run, with the frame's own
// work well inside its time, it tries one notch back up, and if that brings late frames back it steps down again and waits twice as
// long before trying that notch again. The notches, best first: reflections, depth blur, glow, then the resolution a step at a time,
// then lighter shadows, then a little under the screen's own resolution. Where it settles is remembered for next time
let curPR = Math.min(PR_CAP, window.devicePixelRatio || 1); const maxPR = curPR;
const Q_LAD = (() => {
  const L = [], q = o => L.push(Object.assign({ mirror: false, dof: !!post, bloom: !!post, grab: !!post, pr: maxPR, sh: 0 }, o)), off = { dof: false, bloom: false };
  if (post && DEV_TIER >= 3) q({ mirror: true });
  q({}); if (post) { q({ dof: false }); q(off); }
  const prs = []; for (let p = maxPR - 0.25; p > 1.001; p -= 0.25) prs.push(Math.round(p * 100) / 100); const lo = Math.min(1, maxPR); if (maxPR > 1) prs.push(lo);
  // the blob's see-through look copies the frame half way through drawing it, which is dear on a phone's graphics chip: it goes after
  // the first step down in resolution
  prs.forEach((pr, i) => { if (i === 1 && post) q(Object.assign({}, off, { pr: prs[0], grab: false })); q(Object.assign({}, off, { pr, grab: !post || i === 0 ? !!post : false })); });
  if (prs.length <= 1 && post) q(Object.assign({}, off, { pr: lo, grab: false }));
  const fl = Object.assign({}, off, { grab: false, pr: lo }); q(Object.assign({}, fl, { sh: 1 })); q(Object.assign({}, fl, { sh: 2 })); q(Object.assign({}, fl, { pr: Math.min(lo, 0.85), sh: 2 }));
  return L; })();
let shadowLite = 0, frameNo = 0, lastCpu = 0;
function setShadowLite(k) {
  shadowLite = k; const sz = k ? SH_LITE : SH_FULL;
  if (sun.shadow.mapSize.x !== sz) { sun.shadow.mapSize.set(sz, sz); if (sun.shadow.map) { sun.shadow.map.dispose(); sun.shadow.map = null; } }
  sun.shadow.autoUpdate = k < 2; sun.shadow.needsUpdate = true;
}
const qKey = GFX + (MOBILE ? 'm' : 'd');
let qLvl = 0, qN = 0, qLate = 0, qCpu = 0, qClean = 0, qWin = 0, qUpAt = -99, qSkip = 0, qState = '', qCap = null, qCapped = false; const qIv = [], qBan = [], qBanLen = [];
function setQ(n) {
  n = Math.max(0, Math.min(Q_LAD.length - 1, n)); qLvl = n; const q = Q_LAD[n];
  if (post) { post.mirror = q.mirror; post.dof = q.dof; post.bloom = q.bloom; post.grab = q.grab; }
  if (curPR !== q.pr) { curPR = q.pr; renderer.setPixelRatio(curPR); resize(); }
  if (shadowLite !== q.sh) setShadowLite(q.sh);
  qSkip = 20; // (a resize can hitch: the next few frames don't count)
}
function qSave() { try { store.qLv = [qKey, qLvl]; save(); } catch (e) {} }
// the shell says the phone is in Low Power Mode or running hot: ease off at once (the glow and the blur, then resolution and shadows);
// when it cools down the tuning brings things back
function nativeEase() {
  if (!NATIVE) return; const hot = NATIVE.thermal || 0, low = !!NATIVE.lowPower, cap = hot >= 3 ? 1 : Math.max(1, maxPR * 0.75);
  const ok = q => (!(low || hot >= 2) || (!q.bloom && !q.dof)) && (hot < 2 || q.pr <= cap) && (hot < 3 || q.sh >= 2);
  let n = qLvl; while (n < Q_LAD.length - 1 && !ok(Q_LAD[n])) n++; if (n !== qLvl) setQ(n); qClean = 0;
}
window.addEventListener('nativechange', nativeEase);
// where this phone settled last time, one notch better (it steps straight back if that's too much); a phone's first go is without the depth blur
{ const sv = store.qLv, mine = !!(sv && sv[0] === qKey); let n = mine ? Math.max(0, (sv[1] | 0) - 1) : 0; if (!mine && MOBILE && post) n = Math.max(0, Q_LAD.findIndex(q => !q.mirror && !q.dof && q.bloom)); setQ(n); qSkip = 0; }
nativeEase(); // launched in Low Power Mode, or already warm
let awakeSent = false; // keep the screen on while a match is being played (the iPhone shell does this)
function tunePerf(ft) {
  if (document.hidden || window.__fixedPR) { qN = qLate = qCpu = 0; qIv.length = 0; return; }
  if (state !== qState) { qState = state; qSkip = Math.max(qSkip, 60); } // (a new screen: its first second is loading, not the steady load)
  if (qSkip > 0) { qSkip--; return; }
  if (ft > 0.25) return; // (a stall: away from the tab, or something loading)
  qN++; qCpu += lastCpu; qIv.push(ft); if (ft > 0.0242) qLate++; // (late: a refresh missed at 60 a second)
  if (qN < 60) return;
  qIv.sort((a, b) => a - b); const med = qIv[qN >> 1], p10 = qIv[(qN * 0.1) | 0], cpuK = qCpu / qN * 60, win = () => { qWin++; qN = qLate = qCpu = 0; qIv.length = 0; };
  // a steady 30 a second: either the work, or the phone holding the page to 30 (Low Power Mode). Two notches down settle it: if nothing
  // changes, it's the phone, and the look goes back to where it was
  if (med > 0.0305 && med < 0.0365 && p10 > 0.029) {
    if (!qCapped) { if (!qCap) qCap = { lvl: qLvl, n: 0 }; if (qCap.n >= 2 || qLvl >= Q_LAD.length - 1) { qCapped = true; setQ(qCap.lvl); qCap = null; } else { qCap.n++; setQ(qLvl + 1); } }
    return win();
  }
  qCapped = false; qCap = null;
  if (qLate >= 4 && qLvl < Q_LAD.length - 1) {
    if (qWin - qUpAt <= 3) { const b = qLvl; qBanLen[b] = Math.min(600, (qBanLen[b] || 15) * 2); qBan[b] = qWin + qBanLen[b]; } // (that notch up didn't hold: not again for a while)
    setQ(qLvl + 1); qClean = 0; qSave();
  } else if (qLate === 0) {
    if (++qClean >= 8 && qLvl > 0 && cpuK < 0.5 && qWin >= (qBan[qLvl - 1] || 0)) { setQ(qLvl - 1); qUpAt = qWin; qClean = 0; qSave(); }
  } else qClean = 0;
  win();
}
""")
rep("      grab.on = !vic; grab.done = false; RIG.uGrabK.value = 0;\n", "      grab.on = P0.grab !== false && !vic; grab.done = false; RIG.uGrabK.value = 0; // (the tuning can switch the see-through copy off)\n")
rep('<p class="ver">Version 205</p>', '<p class="ver">Version 206</p>')
open(DST, 'w').write(s)
print('ui131 ok', n0, '->', len(s))
