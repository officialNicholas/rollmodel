#!/usr/bin/env python3
"""The stage opens with a sweep: before the count the camera sails high over the canvas and swoops down behind you, the stage's name up big with the mode under it. On top of ui55_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui55_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

rep('  <div class="count" id="count" aria-live="assertive">', '  <div class="reveal" id="reveal" hidden aria-live="polite"><b class="rvn" id="rvName"></b><span class="rvs" id="rvSub"></span></div>\n  <div class="count" id="count" aria-live="assertive">')
rep("const INTRO_AT = [0.6, 1.6, 2.6, 3.6],", "const REVEAL_T = 2.7; let revealT = 0, revealA0 = 0; // the sweep over the canvas before the count\nconst INTRO_AT = [0.6, 1.6, 2.6, 3.6],")
# it starts the match: the sweep first, then the intro as before
rep("  camYaw = P.yaw; camYawV = 0; introCam(true); gyCam = P.introY0 || 0; camSnap = true;\n  const v = tv1.set(P.x, P.y + 0.1, P.z).project(camera); irisOpen([(v.x * 0.5 + 0.5) * viewW, (0.5 - v.y * 0.5) * viewH]);\n}",
    """  camYaw = P.yaw; camYawV = 0; introCam(true); gyCam = P.introY0 || 0; camSnap = true;
  if (!reduceMotion && !window.__noReveal) { state = 'reveal'; revealT = 0; revealA0 = P.yaw + 0.67 + 0.75; revealCam(); camera.position.copy(dPos); camera.lookAt(dLook); camera.updateMatrixWorld(); revealShow(); irisOpen(); AU.whoosh(); return; }
  const v = tv1.set(P.x, P.y + 0.1, P.z).project(camera); irisOpen([(v.x * 0.5 + 0.5) * viewW, (0.5 - v.y * 0.5) * viewH]);
}
// the sweep: high over the far side of the canvas, round and down to where the intro's camera starts
function revealCam() {
  const u = clamp(revealT / REVEAL_T, 0, 1), e = u * u * (3 - 2 * u), R = ARENA * 1.5 - ARENA * 0.3 * e, a = revealA0 - 0.75 * e, Hh = ARENA * 1.0 - ARENA * 0.35 * e;
  const px = Math.sin(a) * R, py = Hh, pz = Math.cos(a) * R, lx = P.x * 0.35, ly = 1.5, lz = P.z * 0.35;
  const w = u < 0.7 ? 0 : (u - 0.7) / 0.3, ww = w * w * (3 - 2 * w); introCam(false);
  dPos.set(px + (dPos.x - px) * ww, py + (dPos.y - py) * ww, pz + (dPos.z - pz) * ww); dLook.set(lx + (dLook.x - lx) * ww, ly + (dLook.y - ly) * ww, lz + (dLook.z - lz) * ww);
}
function revealShow() { const el = $('reveal'); $('rvName').textContent = TH.label; $('rvSub').textContent = (MODES.find(m => m[0] === mode) || MODES[0])[1] + ' \\u00b7 ' + (mode === 'solo' ? 'Solo' : 'CPU ' + (DIFFS.find(d => d[0] === diff) || DIFFS[0])[1]); el.hidden = false; el.className = 'reveal'; void el.offsetWidth; el.className = 'reveal on'; }
function revealStep(rdt) { revealT += rdt; const el = $('reveal'); if (revealT >= REVEAL_T - 0.4 && el.className !== 'reveal out') el.className = 'reveal out'; if (revealT >= REVEAL_T) { state = 'intro'; introT = 0; setTimeout(() => { if (state !== 'reveal') el.hidden = true; }, 400); } }""")
rep("  if (state === 'intro') introStep(rdt);", "  if (state === 'reveal') revealStep(rdt);\n  if (state === 'intro') introStep(rdt);")
rep("  else if (state === 'intro') { rdtCam = rdt; introCam(false); }", "  else if (state === 'reveal') { rdtCam = rdt; revealCam(); }\n  else if (state === 'intro') { rdtCam = rdt; introCam(false); }")
# leaving mid-sweep (the pause key, a quit) ends it cleanly
rep("function abortVictory() {", "function abortReveal() { if (state === 'reveal') { state = 'intro'; introT = 0; } const el = $('reveal'); if (el) el.hidden = true; }\nfunction abortVictory() {")
rep("function resetRun() {\n  abortVictory(); kofEnd();", "function resetRun() {\n  abortVictory(); kofEnd(); abortReveal();")
css = '''
/* the stage reveal: its name over the sweep */
.reveal{position:absolute;left:16px;right:16px;top:16%;display:grid;justify-items:center;gap:10px;pointer-events:none;z-index:6;opacity:0;text-align:center}
.reveal.on{animation:rvin .55s .15s cubic-bezier(.2,1.4,.4,1) both}
.reveal.out{animation:rvout .35s ease-in both}
@keyframes rvin{from{opacity:0;transform:translateY(22px) scale(.8)}to{opacity:1}}
@keyframes rvout{to{opacity:0;transform:translateY(-14px) scale(1.06)}}
.rvn{font:400 clamp(44px,13vw,100px)/1 var(--font-display);color:#FFF6EA;-webkit-text-stroke:6px var(--outline);paint-order:stroke fill;text-shadow:0 8px 0 var(--outline),0 0 30px rgba(0,0,0,.3);transform:rotate(-3deg);max-width:100%}
.rvs{font:800 13px/1 var(--font-ui);letter-spacing:.16em;text-transform:uppercase;color:#fff;padding:8px 15px;border-radius:99px;background:rgba(23,19,32,.62);border:2px solid rgba(255,255,255,.18)}
@media (max-height:520px) and (min-aspect-ratio:1/1){.reveal{top:14%;gap:6px}.rvn{font-size:min(80px,19vh)}.rvs{font-size:12px;padding:6px 12px}}
@media (prefers-reduced-motion:reduce){.reveal.on,.reveal.out{animation:none}.reveal.on{opacity:1}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
