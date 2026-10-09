#!/usr/bin/env python3
"""The material pass, on top of ui3_patch (which rebuilds from the pristine v71 first)."""
import subprocess, sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui3_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

css = open(S + '/tools/ui4.css').read()
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]

# the studio set: drifting flecks behind the lobby, a sheen on Play
rep('    <div class="mhome lobby" id="mHome">\n', '    <div class="mhome lobby" id="mHome">\n      <div class="lobbyfx" aria-hidden="true"><i></i><i></i></div>\n')
rep('<button class="playbtn" id="homePlay" type="button"><span class="pbl">Play</span></button>', '<button class="playbtn" id="homePlay" type="button"><span class="sheen" aria-hidden="true"></span><span class="pbl">Play</span></button>')
# loading: a drip runs down the canvas
rep('<div class="boot" id="boot" role="status">', '<div class="boot" id="boot" role="status"><span class="bootdrip" aria-hidden="true"></span>')
# how to play: a stack of Polaroids
a = s.index('      <ul class="rules">'); b = s.index('      <button class="btn play sm" id="howClose"')
POLS = '''      <div class="pols" id="pols">
        <div class="pol"><div class="pic"><span class="ink stroke"></span><span class="glyph">&#8596;</span><span class="cap">Move</span></div><div><b>Steer, jump, roll</b><p id="howCtl">Drag sideways to steer. Tap to jump, swipe up to roll. Hold to stop, then pull down and let go to fling. The arrow button pounds.</p></div></div>
        <div class="pol"><div class="pic"><span class="ink"></span><span class="glyph sm">%</span><span class="cap">The goal</span></div><div><b>Own the canvas</b><p id="howGoal"></p></div></div>
        <div class="pol"><div class="pic"><span class="ink drip"></span><span class="cap">Your paint</span></div><div><b>Stay wet</b><p id="howInk"></p></div></div>
        <div class="pol"><div class="pic" style="--pc:#2E9BFF"><span class="ink"></span><span class="glyph">&#8595;</span><span class="cap">Contact</span></div><div><b>Roll and pound</b><p id="howRoll"></p></div></div>
        <div class="pol"><div class="pic"><span class="ink stroke"></span><span class="glyph">&#10138;</span><span class="cap">Fling</span></div><div><b>Fling and missile</b><p id="howFling"></p></div></div>
        <div class="pol"><div class="pic"><span class="ink drip"></span><span class="glyph">&#8645;</span><span class="cap">Refill</span></div><div><b>Hide and burst</b><p id="howBurst"></p></div></div>
        <div class="pol"><div class="pic" style="--pc:#F29A3A"><span class="ink"></span><span class="glyph sm">&#9728;</span><span class="cap">Weather</span></div><div><b>Heat and rain</b><p id="howSun"></p></div></div>
        <div class="pol"><div class="pic" style="--pc:#C77DFF"><span class="ink"></span><span class="glyph sm">&#9679;</span><span class="cap">The orb</span></div><div><b>Go giant</b><p id="howOrb"></p></div></div>
      </div>
'''
s = s[:a] + POLS + s[b:]
rep('<p class="ver">Version 1.0</p>', '<p class="ver">Version 73</p>')
# the lobby pieces roll out before the opening night
rep("  rollRivalLooks(); AU.init(); AU.music('end');", "  rollRivalLooks(); AU.init(); AU.music('end'); menu.classList.add('leaving'); setTimeout(() => menu.classList.remove('leaving'), 900);")
# the victory stamp: the splat burst sprite plays under the place
rep("  vicEl.classList.remove('out'); vicEl.hidden = false; reAdd.delete(bannerEl);", "  stampBurst($('vPlace')); vicEl.classList.remove('out'); vicEl.hidden = false; reAdd.delete(bannerEl);")
rep("function vicTag(t, dot) {", '''// a splat bursting behind an element (the Ludo sprite sheet, 6x6 frames, played once)
function stampBurst(el, delay) {
  if (reduceMotion) return; const b = document.createElement('i'); b.className = 'burst'; b.style.cssText = 'position:absolute;left:50%;top:50%;width:260px;height:146px;margin:-73px 0 0 -130px;z-index:-1;pointer-events:none;background:url(art/splat_burst.webp) 0 0/1560px 876px no-repeat;filter:hue-rotate(0)';
  const host = el.parentElement; if (getComputedStyle(host).position === 'static') host.style.position = 'relative'; host.insertBefore(b, el);
  let f = 0; const t0 = performance.now() + (delay || 300); const step = () => { const t = performance.now(); if (t < t0) return requestAnimationFrame(step); f = Math.min(35, Math.floor((t - t0) / 42)); b.style.backgroundPosition = (-(f % 6) * 260) + 'px ' + (-Math.floor(f / 6) * 146) + 'px'; if (f < 35) requestAnimationFrame(step); else setTimeout(() => b.remove(), 400); }; requestAnimationFrame(step);
}
function vicTag(t, dot) {''')
# the results numbers count up
rep("function judgeGo() {", '''function countUp(el, to, dur) { const t0 = performance.now(), suf = /%$/.test(el.textContent) ? '%' : ''; const step = () => { const u = clamp((performance.now() - t0) / dur, 0, 1), e = 1 - Math.pow(1 - u, 3); el.textContent = Math.round(to * e) + suf; if (u < 1) requestAnimationFrame(step); }; requestAnimationFrame(step); }
function judgeGo() {''')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
