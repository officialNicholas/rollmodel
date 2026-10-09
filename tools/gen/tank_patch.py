# the paint bar leaves the bottom of the screen: a small upright tank rides beside your blob instead
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:120])
    src = src.replace(old, new)

# ---------- markup ----------
rep('<div class="tube" id="bar"><span class="tdrop"></span><div class="ttrack" id="ttrack"><span><i></i></span><span><i></i></span><span><i></i></span><span><i></i></span><em class="tdry" aria-live="assertive"><span id="tdryW">Find a refill</span> <b id="tdryN">4</b></em></div></div>',
    '<div class="tank gone" id="bar"><div class="ttrack" id="ttrack" role="meter" aria-label="Paint" aria-valuemin="0" aria-valuemax="100" aria-valuenow="100"><span><i></i></span><span><i></i></span><span><i></i></span><span><i></i></span></div><em class="tdry" aria-live="assertive"><span id="tdryW">Find a refill</span> <b id="tdryN">4</b></em></div>')

# ---------- CSS ----------
rep('.hud .top,.hud .tube{transition:transform .55s cubic-bezier(.3,1.55,.5,1)}\n.hud .tube{transition-delay:.09s}\n', '.hud .top{transition:transform .55s cubic-bezier(.3,1.55,.5,1)}\n')
rep('.hud.off .tube{transform:translateY(46px)}\n', '')
a = src.index('.tube{display:flex;align-items:center;width:min(78%,330px)}')
b = src.index('.tube.heat .ttrack span::after{', a)
b = src.index('\n', b) + 1
TANK = r'''/* your paint: a small upright tank riding beside your blob, four cells (a pound's worth each) filling from the bottom, a drop on top */
.tank{position:absolute;left:0;top:0;z-index:2;display:flex;flex-direction:column;align-items:center;transition:opacity .18s;will-change:transform}
.tank.gone{opacity:0;transition:none}
.tank::before{content:"";position:relative;z-index:1;width:9px;height:9px;margin-bottom:-5px;background:var(--ink);border:2.5px solid var(--line);border-radius:50% 50% 50% 0;transform:rotate(135deg);transition:background .3s}
.ttrack{position:relative;display:flex;flex-direction:column-reverse;gap:2px;width:17px;height:54px;box-sizing:border-box;padding:5px 3px 3px;background:var(--glass);border:2.5px solid var(--line);border-radius:8px;box-shadow:0 2px 0 var(--line)}
.ttrack span{position:relative;flex:1;background:rgba(255,255,255,.12);border-radius:2px;overflow:hidden}
.ttrack span:first-child{border-radius:2px 2px 4px 4px}
.ttrack i{display:block;width:100%;height:100%;background:linear-gradient(90deg,rgba(255,255,255,.42) 0 32%,transparent 32%) var(--ink);transform-origin:center bottom;transform:scaleY(0)}
.ttrack span.full{animation:cellpop .4s cubic-bezier(.3,1.8,.5,1)}
.ttrack span.empty{animation:celldrain .45s ease-out}
@keyframes cellpop{40%{transform:scale(1.4,1.15)}}
@keyframes celldrain{30%{transform:translateX(-1.5px) scaleY(.75)}}
.ttrack.nope{animation:nope .35s}
@keyframes nope{25%{transform:translateX(-5px)}50%{transform:translateX(5px)}75%{transform:translateX(-2px)}}
.tank.low .ttrack{border-color:#FF3B5C;animation:lowglow .45s ease-in-out infinite alternate}
@keyframes lowglow{to{box-shadow:0 2px 0 var(--line),0 0 12px 3px rgba(255,59,92,.8)}}
.tank.giant .ttrack i{background:linear-gradient(180deg,#FF4D6D,#FFD23F,#4DFFB8,#4DA6FF,#C77DFF,#FF4D6D);background-size:100% 200%;animation:orbflow .9s linear infinite}
.tank.giant .ttrack{box-shadow:0 2px 0 var(--line),0 0 12px rgba(255,255,255,.6)}
.tank.giant::before{animation:orbhue 1.2s linear infinite}
.tank.dry::before{filter:grayscale(1) brightness(.75)}
.tank.dry .ttrack span{background:rgba(255,255,255,.05)}
@keyframes orbflow{to{background-position:0 -200%}}
@keyframes orbhue{to{filter:hue-rotate(360deg)}}
.tank.fill .ttrack i{background:repeating-linear-gradient(45deg,transparent 0 4px,rgba(255,255,255,.42) 4px 8px) var(--ink);background-size:11.3px 11.3px;animation:stripes .5s linear infinite}
@keyframes stripes{to{background-position:0 -11.3px}}
.tank.heat::before,.tank.heat .ttrack i{background:#FF9A3C;animation:redflash .3s steps(2) infinite}
.tdry{position:absolute;left:calc(100% + 7px);top:50%;display:none;align-items:center;gap:6px;padding:5px 9px 5px 10px;border:2.5px solid var(--line);border-radius:99px;background:#FF3B5C;color:var(--white);font:800 13px/1 var(--font-ui);font-style:normal;white-space:nowrap;transform:translateY(-50%);box-shadow:0 2px 0 var(--line);animation:threatPulse .4s ease-in-out infinite alternate}
.tank.flip .tdry{left:auto;right:calc(100% + 7px)}
.tdry b{font:400 17px/1 var(--font-display);text-shadow:var(--o2)}
.tank.dry .tdry{display:flex}
'''
src = src[:a] + TANK + src[b:]
rep('  .tube{width:min(36vw,270px);align-self:flex-start}\n', '')
rep('  .chip,.chip.wx.sun.burn,.ttrack span.full,.ttrack span.empty,.ttrack.nope,.slamBtn.press::before{animation:none}\n  .hud .top,.hud .tube{transition:none}\n',
    '  .chip,.chip.wx.sun.burn,.ttrack span.full,.ttrack span.empty,.ttrack.nope,.slamBtn.press::before{animation:none}\n  .hud .top{transition:none}\n')
rep('.orbptr i,.orbflash.on,.tube.giant .ttrack i,.tube.giant .tdrop,.tube.low,.vig.low,.vig.heat,.sheet,.tube.fill .ttrack i,.slamBtn,.slamBtn.ready,.tube.heat .tdrop,.tube.heat .ttrack i{animation:none}',
    '.orbptr i,.orbflash.on,.tank.giant .ttrack i,.tank.giant::before,.tank.low .ttrack,.vig.low,.vig.heat,.sheet,.tank.fill .ttrack i,.slamBtn,.slamBtn.ready,.tank.heat::before,.tank.heat .ttrack i,.tdry{animation:none}')

# ---------- script ----------
rep("el._f = f; el.style.transform = 'scaleX(' + f.toFixed(3) + ')';", "el._f = f; el.style.transform = 'scaleY(' + f.toFixed(3) + ')';")
rep("    const bar = $('bar'); bar.classList.toggle('heat', burning);", "    placeTank(rdt);\n    const bar = $('bar'); bar.classList.toggle('heat', burning);")
rep("const inkSegs = Array.from(document.querySelectorAll('#ttrack i')), inkSpans = Array.from(document.querySelectorAll('#ttrack span'));",
    r"""const inkSegs = Array.from(document.querySelectorAll('#ttrack i')), inkSpans = Array.from(document.querySelectorAll('#ttrack > span'));
// the tank rides beside your blob: off its right side (its left, near the right edge of the screen), level with its middle, easing after
// it up and down so a jump doesn't jerk it about. Gone while you're knocked out
const tankEl = $('bar'), tankTrack = $('ttrack'); let tankOn = false, tankFlip = false, tankX = -1e4, tankY = -1e4, tankSY = null, tankPct = -1;
function placeTank(rdt) {
  const on = state === 'play' && (P.st === 'play' || P.st === 'hide');
  if (on !== tankOn) { tankOn = on; tankEl.classList.toggle('gone', !on); tankSY = null; }
  if (!on) return;
  const pc = Math.round(P.paint * 100); if (pc !== tankPct) { tankPct = pc; tankTrack.setAttribute('aria-valuenow', String(Math.max(0, pc))); }
  const r = PR * (P.giantT > 0 ? GIANT_K : 1) * (VP.gk || 1), cy = P.y + r * (P.st === 'hide' ? 1.6 : 1);
  camera.updateMatrixWorld(); tv1.set(P.x, cy, P.z).project(camera);
  if (tv1.z > 1 || !Number.isFinite(tv1.x + tv1.y)) return;
  tv2.setFromMatrixColumn(camera.matrixWorld, 0).multiplyScalar(r * 1.25).add(tv3.set(P.x, cy, P.z)).project(camera);
  const sx = (tv1.x * 0.5 + 0.5) * viewW, sy = (0.5 - tv1.y * 0.5) * viewH, rp = Math.abs(tv2.x - tv1.x) * 0.5 * viewW, W = 17, Hh = 58, off = Math.max(20, rp + 8);
  const wide = tankEl.classList.contains('dry') ? 150 : 40; if (!tankFlip && sx + off + W + wide > viewW - 6) tankFlip = true; else if (tankFlip && sx + off + W + wide < viewW - 46) tankFlip = false;
  tankEl.classList.toggle('flip', tankFlip);
  const ty = sy - Hh / 2; tankSY = tankSY === null ? ty : tankSY + (ty - tankSY) * Math.min(1, rdt * 14);
  const x = Math.round(clamp(tankFlip ? sx - off - W : sx + off, 6, viewW - W - 6)), y = Math.round(clamp(tankSY, 70, viewH - Hh - 90));
  if (x !== tankX || y !== tankY) { tankX = x; tankY = y; tankEl.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0)'; }
}""")

# the bar is hidden with the HUD between matches: make sure a new match starts it hidden until placed
rep("  lastPct = -1; lastPctC = -1; setScore();\n}", "  lastPct = -1; lastPctC = -1; setScore(); if (typeof tankEl !== 'undefined') { tankOn = false; tankEl.classList.add('gone'); }\n}")

open(P, 'w').write(src)
print('ok')
