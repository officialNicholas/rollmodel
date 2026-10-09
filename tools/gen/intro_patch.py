# the circle wipe between screens, the 3-2-1 with each blob forming as a drop and splatting down at Go, and the results sting
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
# ---- markup ----
rep('<div class="banner" id="banner" aria-live="polite"><p id="bannerBig"></p><p id="bannerSmall"></p></div>',
    '<div class="banner" id="banner" aria-live="polite"><p id="bannerBig"></p><p id="bannerSmall"></p></div>\n  <div class="count" id="count" aria-live="assertive"><b id="countN"></b></div>')
rep('  <div class="boot" id="boot" role="status">', '  <div class="iris" id="iris" hidden aria-hidden="true"><i></i><b id="irisText"></b></div>\n  <div class="boot" id="boot" role="status">')
# ---- styles ----
rep('.banner{position:absolute;left:16px;right:16px;top:30%;', """.count{position:absolute;inset:0;display:grid;place-items:center;pointer-events:none;z-index:6}
.count b{font:400 clamp(110px,34vw,190px)/1 var(--font-display);color:#FFF6EA;-webkit-text-stroke:7px var(--outline);paint-order:stroke fill;text-shadow:0 9px 0 var(--outline),0 0 40px rgba(255,255,255,.35);opacity:0;transform:scale(.4)}
.count b.on{animation:cpop .7s cubic-bezier(.2,1.5,.4,1) both}
.count b.go{color:var(--ink-hi);animation:gopop .95s cubic-bezier(.2,1.4,.4,1) both}
@keyframes cpop{0%{opacity:0;transform:scale(2.3) rotate(-10deg)}32%{opacity:1;transform:scale(.9) rotate(3deg)}52%{transform:scale(1.05) rotate(-1deg)}78%{opacity:1;transform:scale(1)}100%{opacity:0;transform:scale(.82) translateY(10px)}}
@keyframes gopop{0%{opacity:0;transform:scale(.3) rotate(8deg)}28%{opacity:1;transform:scale(1.28) rotate(-3deg)}48%{transform:scale(.95)}70%{opacity:1;transform:scale(1.03)}100%{opacity:0;transform:scale(1.7)}}
.iris{position:absolute;inset:0;z-index:38;overflow:hidden;pointer-events:auto}
.iris[hidden]{display:none}
.iris i{position:absolute;left:50%;top:50%;width:0;height:0;border-radius:50%;box-shadow:0 0 0 300vmax #130A1E}
.iris b{position:absolute;left:0;right:0;top:50%;transform:translateY(-50%) scale(.9);text-align:center;font:400 clamp(22px,6vw,30px)/1 var(--font-display);color:#FFF1DF;opacity:0;transition:opacity .2s,transform .3s cubic-bezier(.2,1.5,.4,1)}
.iris.txt b{opacity:.92;transform:translateY(-50%) scale(1)}
@media (prefers-reduced-motion:reduce){.count b.on,.count b.go{animation-duration:.01s}}
.banner{position:absolute;left:16px;right:16px;top:30%;""")
# ---- the wipe, the count, the intro ----
rep("function showMenu() {", """// ---------- the circle wipe between screens: it closes to black, the change happens out of sight, and it opens on the new screen ----------
const irisEl = $('iris'), irisHole = irisEl.firstElementChild; let irisBusy = false, camSnap = false;
const irisR = (cx, cy) => Math.hypot(Math.max(cx, viewW - cx), Math.max(cy, viewH - cy)) + 10;
function irisRun(r0, r1, dur, ease, cx, cy, done) {
  const t0 = performance.now(), go = now => { const u = Math.min(1, (now - t0) / (dur * 1000)), r = Math.max(0, r0 + (r1 - r0) * ease(u)); irisHole.style.cssText = 'width:' + (2 * r).toFixed(1) + 'px;height:' + (2 * r).toFixed(1) + 'px;left:' + (cx - r).toFixed(1) + 'px;top:' + (cy - r).toFixed(1) + 'px'; if (u < 1) requestAnimationFrame(go); else if (done) done(); };
  requestAnimationFrame(go);
}
// close on a point (the middle of the screen unless given), say something while it's dark if asked, then make the change
function irisClose(fn, at, text) {
  if (irisBusy) return false; irisBusy = true; const cx = at ? at[0] : viewW / 2, cy = at ? at[1] : viewH / 2;
  irisEl.hidden = false; irisEl.classList.remove('txt'); $('irisText').textContent = text || ''; AU.swish();
  const run = () => { if (text) irisEl.classList.add('txt'); setTimeout(() => { try { fn(); } catch (e) { console.error(e); irisOpen(); } }, text ? 90 : 20); };
  if (reduceMotion) { irisHole.style.cssText = 'width:0;height:0;left:' + cx + 'px;top:' + cy + 'px'; run(); } else irisRun(irisR(cx, cy), 0, 0.4, u => u * u * (3 - 2 * u) * (0.6 + 0.4 * u), cx, cy, run);
  return true;
}
function irisOpen(at) {
  const cx = at ? at[0] : viewW / 2, cy = at ? at[1] : viewH / 2, fin = () => { irisEl.hidden = true; irisBusy = false; };
  irisEl.classList.remove('txt'); if (reduceMotion) { fin(); return; } irisRun(0, irisR(cx, cy), 0.6, u => 1 - Math.pow(1 - u, 3), cx, cy, fin);
}
const toMenu = () => irisClose(() => { showMenu(); camSnap = true; irisOpen(); });
// ---------- the start of a match: 3, 2, 1, each blob gathering itself into a drop in the air over its spot, and at Go they fall and splat down ----------
const INTRO_AT = [0.4, 1.1, 1.8, 2.5], INTRO_H = 1.9;
let introT = 0, introN = 0, introOut = 0;
const countEl = $('countN');
function showCount(txt, go) { countEl.textContent = txt; countEl.className = ''; void countEl.offsetWidth; countEl.className = go ? 'go' : 'on'; }
function introCam(snap) {
  const t = Math.min(1, introT / INTRO_AT[3]), a = P.yaw + 0.55 * (1 - t) * (1 - t) + 0.12, d = 3.1 - 0.75 * t, gy = P.introY0 || 0;
  dPos.set(P.x + Math.sin(a) * d, gy + 1.15 + 0.3 * t, P.z + Math.cos(a) * d); dLook.set(P.x, P.y + 0.12, P.z);
  if (snap) { camPos.copy(dPos); camLook.copy(dLook); camera.position.copy(camPos); camera.lookAt(camLook); camera.updateMatrixWorld(); }
}
function introStep(rdt) {
  introT += rdt;
  for (const D of ACTIVE) { if (D.st === 'out') continue;
    D.fV += ((D.fT - D.formK) * 170 - D.fV * 13) * Math.min(rdt, 0.033); D.formK = Math.max(0.05, D.formK + D.fV * Math.min(rdt, 0.033));
    D.y = (D.introY0 || 0) + INTRO_H + Math.sin(clock * 2.4 + D.team * 1.7) * 0.05; D.wob = Math.max(0, D.wob - rdt * 1.6); }
  while (introN < 4 && introT >= INTRO_AT[introN]) {
    const n = 3 - introN; introN++;
    if (n > 0) { showCount(String(n)); AU.cd(n); buzz(8);
      for (const D of ACTIVE) { if (D.st === 'out') continue; D.fT = [1, 0.8, 0.58][n - 1]; D.fV += 3.2; D.wob = 1; }
      // paint flying in from all round to join the drop
      for (let i = 0; i < 10; i++) { const a = i / 10 * 6.283 + Math.random() * 0.5, r = 0.75 + Math.random() * 0.4, h = (Math.random() - 0.35) * 0.7, x = P.x + Math.cos(a) * r, y = P.y + 0.12 + h, z = P.z + Math.sin(a) * r, T = 0.15 + Math.random() * 0.06; spawnPart(x, y, z, (P.x - x) / T, (P.y + 0.12 - y) / T, (P.z - z) / T, T, tmat(P), 0.5 + Math.random() * 0.35, 0); }
    } else goTime();
  }
}
function goTime() {
  showCount('Go!', true); state = 'play'; introOut = 1; hud.classList.remove('off');
  for (const D of ACTIVE) { if (D.st === 'out') continue; D.fT = 1; D.formK = Math.max(D.formK, 0.92); D.vy = -9; D.air = true; D.freeLand = true; D.wob = 0.6; }
  AU.music('play'); AU.go(); buzz([12, 30, 18]);
  setTimeout(() => { if (state === 'play') banner('Paint it ' + colorOf().name.toLowerCase() + '!', mode === 'solo' ? '60 seconds' : mode === 'trio' ? 'Everyone for themselves' : TH.label, true); }, 520);
  hint('steer', say('Drag to steer', 'A D or arrows to steer'), 3);
}
function showMenu() {""")
# ---- start: through the wipe, then the intro ----
rep("""  pickRivalNames(); rollRivalLooks();
  // a fresh canvas takes a moment to lay out: put the sheets away and say so first, so the tap feels answered
  if (mapUsed) { building = true; AU.init(); menu.hidden = true; end.hidden = true; pauseEl.hidden = true; banner('New canvas'); setTimeout(() => { freshMap(); clearTimeout(warmQ); warmRender(); building = false; start(); }, 60); return; }
  AU.init(); AI = AI_LV[diff]; mapUsed = true; resetRun(); gyCam = 0; state = 'play'; menu.hidden = true; end.hidden = true; pauseEl.hidden = true; howModal.hidden = true; hud.classList.remove('off');
  for (const D of ACTIVE) { D.y = 6.5; D.air = true; D.vy = -1; D.freeLand = true; D.stroke++; }
  AU.music('play'); AU.go(); banner('Paint it ' + colorOf().name.toLowerCase() + '!', mode === 'solo' ? '60 seconds' : mode === 'trio' ? 'Everyone for themselves' : TH.label, true); hint('steer', say('Drag to steer', 'A D or arrows to steer'), 3);
}""", """  pickRivalNames(); rollRivalLooks(); AU.init(); AU.music('end');
  // through the wipe: a fresh canvas is laid out while it's dark (it says so), then the match opens on your drop forming
  irisClose(() => {
    menu.hidden = true; end.hidden = true; pauseEl.hidden = true; howModal.hidden = true;
    if (mapUsed) { building = true; freshMap(); clearTimeout(warmQ); warmRender(); building = false; }
    beginMatch();
  }, null, mapUsed ? 'New canvas' : '');
}
function beginMatch() {
  AI = AI_LV[diff]; mapUsed = true; resetRun(); gyCam = 0; state = 'intro'; introT = 0; introN = 0; hud.classList.add('off');
  for (const D of ACTIVE) { D.introY0 = Math.max(0, surfaceUnder(D.x, D.z, 3, true)); D.y = D.introY0 + INTRO_H; D.air = true; D.vy = 0; D.freeLand = true; D.stroke++; D.formK = 0.12; D.fT = 0.34; D.fV = 0; D.wob = 0.8; }
  introCam(true); gyCam = P.introY0 || 0; camSnap = true;
  const v = tv1.set(P.x, P.y + 0.1, P.z).project(camera); irisOpen([(v.x * 0.5 + 0.5) * viewW, (0.5 - v.y * 0.5) * viewH]);
}""")
rep("""function replay() {
  if (building) return; const sd = GEN.seed; building = true; AU.init(); menu.hidden = true; end.hidden = true; pauseEl.hidden = true; hud.classList.add('off'); banner('Same canvas');
  const op = { easy: GEN.easy, avoid: GEN.avoid, themes: GEN.themes }; setTimeout(() => { genWorld(sd, op); mapUsed = false; warmRender(); building = false; start(); }, 60);
}""", """function replay() {
  if (building || irisBusy) return; const sd = GEN.seed, op = { easy: GEN.easy, avoid: GEN.avoid, themes: GEN.themes }; AU.init(); AU.music('end');
  irisClose(() => { menu.hidden = true; end.hidden = true; pauseEl.hidden = true; hud.classList.add('off'); building = true; genWorld(sd, op); mapUsed = false; warmRender(); building = false; beginMatch(); }, null, 'Same canvas');
}""")
rep("""$('menuBtn').addEventListener('click', uiClick(showMenu));""", """$('menuBtn').addEventListener('click', uiClick(toMenu));""")
rep("""$('quitBtn').addEventListener('click', uiClick(showMenu));""", """$('quitBtn').addEventListener('click', uiClick(toMenu));""")
rep("else if (endUp && k === 'Escape') showMenu(); else pause(); return; }", "else if (endUp && k === 'Escape') toMenu(); else pause(); return; }")
rep("function start() {\n  if (building) return;", "function start() {\n  if (building || irisBusy) return;")
# ---- the intro runs at the top of each frame's visuals, and has its own camera ----
rep("""function visuals(dt, rdt) {
  if (vic) vicFrame(rdt);""", """function visuals(dt, rdt) {
  if (vic) vicFrame(rdt);
  if (state === 'intro') introStep(rdt);""")
rep("""  else if (state === 'dead' || state === 'paused') {
    if (state === 'dead' && outro) {""", """  else if (state === 'intro') introCam(false);
  else if (state === 'dead' || state === 'paused') {
    if (state === 'dead' && outro) {""")
rep("  const k = 1 - Math.exp(-rdt * (playing ? 12 : lookIntro ? 5 : 2.2));", "  const k = camSnap ? 1 : 1 - Math.exp(-rdt * (state === 'intro' ? 7 : playing ? 12 - 9.5 * introOut * introOut : lookIntro ? 5 : 2.2)); camSnap = false; introOut = Math.max(0, introOut - rdt / 1.1);")
# ---- a forming blob: small and drop-shaped, eyes shut until it's nearly whole ----
rep("  const rad = PR * (0.8 + 0.2 * D.paint) * (hidden ? 0.7 : 1) * V.gk, falling = D.air && D.vy < 0, rising = D.air && D.vy > 0;",
    "  const rad = PR * (0.8 + 0.2 * D.paint) * (hidden ? 0.7 : 1) * V.gk * (state === 'intro' && D.formK !== undefined ? D.formK : 1), falling = D.air && D.vy < 0, rising = D.air && D.vy > 0;")
rep("  U.gSpd.value = D.rollT > ROLL_T - ROLL_DASH ? 0.2 : L.spd; U.gLean.value = L.lean; U.gDrop.value = D.missile && D.slam ? 0 : L.drop; U.gFlat.value = L.flat;",
    "  U.gSpd.value = D.rollT > ROLL_T - ROLL_DASH ? 0.2 : L.spd; U.gLean.value = L.lean; U.gDrop.value = D.missile && D.slam ? 0 : state === 'intro' ? 0.62 + 0.08 * Math.sin(clock * 5 + D.team) : L.drop; U.gFlat.value = L.flat;")
rep("    if (happy) sy *= 0.3; else if (blinkK > 0) sy *= 0.12; else if (strain) sy *= 0.6; else if (ES === 'sleepy') sy *= 0.5;",
    "    if (state === 'intro' && P.formK < 0.7) sy *= 0.1; else if (happy) sy *= 0.3; else if (blinkK > 0) sy *= 0.12; else if (strain) sy *= 0.6; else if (ES === 'sleepy') sy *= 0.5;")
# ---- the results: a sting as the winner lands in the sunburst, and the win or lose song starting under it ----
rep("""  AU.whoosh(); setTimeout(() => { if (vic && id === runId) { AU.splat(1.2); buzz(20); } }, 520);
  setTimeout(() => { if (!vic || id !== runId) return; const th = AU.music(happy ? 'win' : 'lost'); if (happy) { if (!th) AU.fanfare(); buzz([30, 40, 30]); } else if (!th) { if (!info.winner) AU.draw(); else AU.lose(); } }, 640);""",
"""  AU.whoosh(); setTimeout(() => { if (!vic || id !== runId) return; AU.splat(1.2); AU.sting(happy ? 'win' : info.winner ? 'lose' : 'draw'); AU.music(happy ? 'win' : 'lost'); buzz(happy ? [30, 40, 30] : 20); }, 500);""")
open(p, 'w').write(s)
print('ok')
