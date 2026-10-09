#!/usr/bin/env python3
"""The gallery pass: results, the picker, the locker. Runs on top of ui4_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui4_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = '''
/* ===== the gallery pass: results, the picker, the locker ===== */
/* results: the live canvas hangs in a real frame on the wall, a placard under it; the sheet below is the verdict and the record */
.gwall{position:absolute;inset:0;z-index:2;pointer-events:none;background:radial-gradient(ellipse 60% 50% at var(--sx,50%) var(--sy,30%),rgba(255,238,210,.22),rgba(255,238,210,0) 70%),#17131F url(art/m_wall.webp) center top/cover no-repeat;animation:fadein .35s both}
.gwall[hidden]{display:none}
@keyframes fadein{from{opacity:0}}
.gframe{--gb:38px;position:absolute;z-index:3;pointer-events:none;border:var(--gb) solid transparent;border-image:url(art/m_frame.webp) 150 stretch;box-sizing:border-box;filter:drop-shadow(10px 14px 0 rgba(0,0,0,.45)) drop-shadow(0 30px 40px rgba(0,0,0,.5));animation:hang .6s .1s var(--eo) both}
.gframe[hidden]{display:none}
.gframe.noplac .gplac{display:none}
@keyframes hang{from{opacity:0;transform:translateY(-30px) rotate(-1.5deg)}}
.gplac{position:absolute;left:50%;bottom:calc(-1 * var(--gb) - 24px);transform:translateX(-50%);min-width:46%;max-width:calc(100% + 2 * var(--gb) - 16px);box-sizing:border-box;padding:7px 14px 8px;background:#fff url(art/m_paperbg.webp) center/300px;border-radius:2px;box-shadow:3px 4px 0 rgba(0,0,0,.45);text-align:center;color:var(--black);animation:rollin-b .5s .5s var(--eo) both}
.gplac b{display:block;font:900 13px/1.15 var(--font-head);text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.gplac span{display:block;margin-top:2px;font:700 10.5px/1.2 var(--font-ui);color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#end{gap:10px;padding-top:16px}
#end .rhead{padding-top:0;gap:6px}
#end .rhead .ptitle{display:none}
.rtitle{font-size:clamp(44px,13vw,64px)}
.jnums{height:46px}
.jnums b{font:900 44px/1 var(--font-head);font-style:italic;letter-spacing:-.03em;text-shadow:.05em .05em 0 var(--black)}
.jnums b small{font-size:11px;vertical-align:8px}
.jbar{height:18px}
.board{gap:5px}
.bhead{display:none}
.brow{min-height:40px;padding-top:2px;padding-bottom:2px}
.bico{width:34px;height:34px}
.bn b{font-size:14.5px}
.bpct{font-size:20px}
.bko{font-size:18px}
.reprow{padding:6px 10px}
.xpmeter{width:112px;height:63px;background-size:672px 378px}
@media (max-height:720px) and (max-aspect-ratio:1/1){.gframe{--gb:32px}.gplac{padding:5px 12px 6px}.gplac b{font-size:12px}.jnums{height:34px}.jnums b{font-size:32px}.jbar{height:14px}#end{gap:7px;padding-top:10px}#end .rtitle{font-size:clamp(32px,10vw,40px)}#end .brow{min-height:36px}.bico{width:30px;height:30px}.reprow{padding:4px 10px}.xpmeter{width:92px;height:52px;background-size:552px 311px}#end .btn.play{min-height:46px;font-size:24px}#end .row .btn{min-height:38px}}
@media (max-height:520px) and (min-aspect-ratio:1/1){.gframe{--gb:28px}.gplac{padding:5px 12px 6px}.gplac b{font-size:12px}.jnums{height:34px}.jnums b{font-size:30px}.jbar{height:14px}.brow{min-height:36px}.bico{width:30px;height:30px}.xpmeter{width:92px;height:52px;background-size:552px 311px}}
/* the picker: one painting in the spotlight, in a real frame; the others wait in the wings */
.mworld::before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 48% 42% at 50% 36%,rgba(255,244,222,.2),rgba(255,244,222,0) 70%);pointer-events:none}
.whead h2{letter-spacing:-.01em}
.gallery{align-items:center;gap:clamp(10px,3vw,24px)}
.world{transition:transform .35s var(--eo),opacity .3s,filter .3s;transform:scale(.8);opacity:.55;filter:brightness(.8)}
.world[aria-pressed="true"]{transform:scale(1);opacity:1;filter:none}
.frame{padding:0;border:34px solid transparent;border-image:url(art/m_frame.webp) 150 stretch;background:#fff;border-radius:0;box-shadow:none;filter:drop-shadow(8px 12px 0 rgba(0,0,0,.45)) drop-shadow(0 26px 40px rgba(0,0,0,.5))}
.frame::before{display:none}
.frame .art{border-radius:0;box-shadow:inset 0 0 0 1px rgba(0,0,0,.25)}
.world[aria-pressed="true"] .frame{transform:none;box-shadow:none}
.world[aria-pressed="true"] .wcheck{display:none}
.wcheck{display:none}
.plaque{min-width:60%;padding:7px 14px 8px}
.wn{font-size:15px}
.world .wsub{display:none}
.stg .sfr{padding:0;border:16px solid transparent;border-image:url(art/m_frame.webp) 150 stretch;background:#fff;box-shadow:none;filter:drop-shadow(5px 7px 0 rgba(0,0,0,.45))}
.stg .art{border-radius:0}
.stg[aria-pressed="true"] .sfr{box-shadow:none}
.stg[aria-pressed="true"] .wcheck{display:none}
.mworld .seg{background:none;box-shadow:none;padding:0;gap:6px;border:0}
.mworld .seg button{background:url(art/m_tape3.webp) center/100% 100% no-repeat;color:#2A2437;min-height:38px;border-radius:0;transform:rotate(-1deg)}
.mworld .seg button:nth-child(2){transform:rotate(1deg)}
.mworld .seg button[aria-pressed="true"]{background:url(art/m_tape3.webp) center/100% 100% no-repeat;color:var(--ink);text-shadow:none;box-shadow:none}
.mworld .lhead.critics{color:#B8B0C8;letter-spacing:.2em}
.mworld .ibtn{background:#fff url(art/m_paperbg.webp) center/300px;color:var(--black);box-shadow:3px 4px 0 rgba(0,0,0,.45);border-radius:3px}
.wgo .btn.play{color:#fff}
/* the locker: a wardrobe. Paint splats for the colors, tape tabs, white cards on the rail, the blob big under the mirror light */
.lookp{gap:11px}
.lookp .ctitle{font-size:28px}
.sw{width:46px;height:46px}
.sw i{width:38px;height:38px;margin:0;border:0;border-radius:0;transform:none;background:var(--c);-webkit-mask:url(art/m_splat2.webp) center/contain no-repeat;mask:url(art/m_splat2.webp) center/contain no-repeat;box-shadow:none;filter:drop-shadow(1px 2px 0 rgba(23,19,32,.25))}
.sw[aria-pressed="true"]{transform:scale(1.28)}
.sw[aria-pressed="true"] i{box-shadow:none;filter:drop-shadow(0 0 0 var(--black)) drop-shadow(1px 2px 0 rgba(23,19,32,.35))}
.sw[aria-pressed="true"]::after{content:"";position:absolute;left:50%;bottom:-3px;width:8px;height:8px;margin-left:-4px;border-radius:50%;background:var(--black)}
.sw{position:relative}
.seg.lcats{background:none;box-shadow:none;padding:0;gap:6px;border:0}
.seg.lcats button{background:url(art/m_tape3.webp) center/100% 100% no-repeat;color:#2A2437;min-height:38px;border-radius:0;transform:rotate(-1deg)}
.seg.lcats button:nth-child(2){transform:rotate(1deg)}
.seg.lcats button[aria-selected="true"]{background:url(art/m_tape3.webp) center/100% 100% no-repeat;color:var(--ink);box-shadow:none}
.ltile{width:84px;height:88px;border-radius:2px;background:#fff;box-shadow:3px 4px 0 rgba(23,19,32,.18)}
.ltile[aria-pressed="true"]{background:#fff;box-shadow:3px 4px 0 rgba(23,19,32,.25),0 0 0 3px var(--ink);transform:translateY(-3px)}
.ltile.locked{background:#EFE9DD;box-shadow:none;border:2px dashed rgba(23,19,32,.25)}
.ltn{font-size:11.5px}
.lnbtn{background:#fff url(art/m_paperbg.webp) center/300px}
.eyec{width:36px;height:36px}
.lookp>*{flex:none}
@media (max-height:520px) and (min-aspect-ratio:1/1){.lookp{gap:6px}.lookp .ctitle{font-size:22px}.lktop{min-height:36px}.lnbtn{height:36px;font-size:16px}.sw{width:36px;height:36px}.sw i{width:30px;height:30px}.sw[aria-pressed="true"]{transform:scale(1.2)}.eyec{width:30px;height:30px}.leyes{margin:0}.seg.lcats button,.lcats button{min-height:32px;font-size:13px}.ltile{width:58px;height:62px}.ltn{font-size:10px}.lookp .btn.play{min-height:42px;font-size:20px}.ucode{font-size:12px}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]

# the frame on the wall, over the orbiting canvas, with its placard
rep('  <section class="sheet" id="end" hidden>', '  <div class="gwall" id="gwall" hidden aria-hidden="true"></div><div class="gframe" id="gframe" hidden aria-hidden="true"><div class="gplac" id="gPlac"><b id="gpT"></b><span id="gpM"></span></div></div>\n  <section class="sheet" id="end" hidden>')
# placed into the space the camera uses, each time the outro is measured; the camera keeps the canvas inside the mat
rep("""  if (outroSide) { outroOffX = (viewW - end.offsetLeft) / 2; outroOffY = 0; outroFrac = clamp(end.offsetLeft / Math.max(1, viewW), 0.3, 1); }
  else { outroOffX = 0; outroOffY = Math.max(0, (viewH - end.offsetTop) / 2); outroFrac = clamp(end.offsetTop / Math.max(1, viewH), 0.3, 1); }
  outroSc = outroFit();
}""", """  // the wall space the results leave free, the frame border, and the painting fitted inside the mat
  const gf = $('gframe'), gw = $('gwall'), top = Math.max(12, viewH * 0.012 + 12);
  let ax0, ax1, ay0, ay1;
  if (outroSide) { ax0 = 20; ax1 = end.offsetLeft - 20; ay0 = top; ay1 = viewH - 34; outroFrac = clamp(end.offsetLeft / Math.max(1, viewW), 0.3, 1); }
  else { ax0 = 16; ax1 = viewW - 16; ay0 = top; ay1 = end.offsetTop - 30; outroFrac = clamp(end.offsetTop / Math.max(1, viewH), 0.3, 1); }
  const freeMin = Math.min(ax1 - ax0, ay1 - ay0), tiny = freeMin < 120, noPlac = ay1 - ay0 < 190;
  if (noPlac) ay1 += 20;
  gf.style.removeProperty('--gb'); const B = tiny ? 0 : Math.min(parseFloat(getComputedStyle(gf).borderTopWidth) || 38, Math.round(freeMin * 0.16)); gf.classList.toggle('noplac', noPlac);
  const mw = Math.max(60, ax1 - ax0 - 2 * B), mh = Math.max(60, ay1 - ay0 - 2 * B), fit = outroFit(mw * 0.94, mh * 0.9);
  outroSc = fit.s;
  const ww = clamp(fit.bw / 0.94, 60, mw), wh = clamp(fit.bh / 0.9, 60, mh), wcx = (ax0 + ax1) / 2, wcy = (ay0 + ay1) / 2;
  outroOffX = viewW / 2 + fit.cx - wcx; outroOffY = viewH / 2 - fit.cy - wcy;
  if (!end.hidden) {
    gf.hidden = tiny; gw.hidden = tiny;
    const x0 = Math.round(wcx - ww / 2), y0 = Math.round(wcy - wh / 2), x1 = Math.round(wcx + ww / 2), y1 = Math.round(wcy + wh / 2);
    gf.style.cssText = '--gb:' + B + 'px;left:' + (x0 - B) + 'px;top:' + (y0 - B) + 'px;width:' + (x1 - x0 + 2 * B) + 'px;height:' + (y1 - y0 + 2 * B) + 'px';
    gw.style.cssText = '--sx:' + Math.round(wcx / viewW * 100) + '%;--sy:' + Math.round((y0 - B) / viewH * 100 - 4) + '%;clip-path:polygon(evenodd,0 0,100% 0,100% 100%,0 100%,0 0,' + x0 + 'px ' + y0 + 'px,' + x0 + 'px ' + y1 + 'px,' + x1 + 'px ' + y1 + 'px,' + x1 + 'px ' + y0 + 'px,' + x0 + 'px ' + y0 + 'px)';
  }
}""")
rep("""function outroFit() {
  fitCam.fov = baseFov; fitCam.aspect = viewW / Math.max(1, viewH); fitCam.updateProjectionMatrix();
  const lx = outroSide ? outroFrac * 0.95 : 1.04, ly = outroSide ? 0.93 : outroFrac * 0.96, R = ARENA + 1;
  const inside = (x, z, s) => { tv3.set(x / s, 0, z / s).project(fitCam); return tv3.z < 1 && Math.abs(tv3.x) <= lx && Math.abs(tv3.y) <= ly; };
  let need = 1;
  for (let k = 0; k < 24; k++) {
    const yw = k / 24 * Math.PI * 2, fx = Math.sin(yw), fz = Math.cos(yw);
    fitCam.position.set(-fx * 31, 37, -fz * 31); fitCam.up.set(0, 1, 0); fitCam.lookAt(fx * 3, -12, fz * 3); fitCam.updateMatrixWorld();
    for (const [cx, cz] of [[R, R], [R, -R], [-R, R], [-R, -R]]) {
      if (inside(cx, cz, need)) continue;
      let lo = need, hi = 4; for (let i = 0; i < 14; i++) { const m = (lo + hi) / 2; if (inside(cx, cz, m)) hi = m; else lo = m; } need = hi;
    }
  }
  return need;
}""", """function outroFit(tw, th) {
  // the box the turning canvas sweeps on screen, in pixels about the lens centre, at a camera pulled back by s; the smallest s whose box fits the mat
  fitCam.fov = baseFov; fitCam.aspect = viewW / Math.max(1, viewH); fitCam.updateProjectionMatrix();
  const R = ARENA + 1, hx = viewW / 2, hy = viewH / 2;
  const box = s => { let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9, ok = true;
    for (let k = 0; k < 24; k++) {
      const yw = k / 24 * Math.PI * 2, fx = Math.sin(yw), fz = Math.cos(yw);
      fitCam.position.set(-fx * 31, 37, -fz * 31); fitCam.up.set(0, 1, 0); fitCam.lookAt(fx * 3, -12, fz * 3); fitCam.updateMatrixWorld();
      for (const [cx, cz] of [[R, R], [R, -R], [-R, R], [-R, -R]]) { tv3.set(cx / s, 0, cz / s).project(fitCam); if (tv3.z >= 1) ok = false; const px = tv3.x * hx, py = tv3.y * hy; x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py); } }
    return { ok, x0, x1, y0, y1 }; };
  const fits = b => b.ok && b.x1 - b.x0 <= tw && b.y1 - b.y0 <= th;
  let lo = 0.6, hi = 5; if (fits(box(lo))) hi = lo; else for (let i = 0; i < 16; i++) { const m = (lo + hi) / 2; if (fits(box(m))) hi = m; else lo = m; }
  const b = box(hi); return { s: hi, bw: b.x1 - b.x0, bh: b.y1 - b.y0, cx: (b.x0 + b.x1) / 2, cy: (b.y0 + b.y1) / 2 };
}""")
rep("  $('pMeta').textContent = TH.label + ', ' + fmtTime(info.time);", "  $('pMeta').textContent = TH.label + ', ' + fmtTime(info.time); $('gpT').textContent = $('pTitle').textContent; $('gpM').textContent = 'Paint on canvas. ' + TH.label + ', ' + fmtTime(info.time);")
# the frame leaves with the sheet
rep("function showMenu() {\n  pickRivalNames(); state = 'menu';", "function showMenu() {\n  $('gframe').hidden = true; $('gwall').hidden = true; pickRivalNames(); state = 'menu';")
rep("window.addEventListener('resize', () => { if (!end.hidden) measureOutro(); });", "window.addEventListener('resize', () => { if (!end.hidden) measureOutro(); });\nif (window.ResizeObserver) new ResizeObserver(() => { if (!end.hidden) measureOutro(); }).observe(end);")
rep('<p class="ver">Version 73</p>', '<p class="ver">Version 75</p>')
rep("function beginMatch() {", "function beginMatch() {\n  $('gframe').hidden = true; $('gwall').hidden = true;")
# the locker blob, bigger
rep("heroDist = clamp(Math.max(tall * Hh / (2 * tv * 0.78 * fh), wide * W / (2 * tv * asp * 0.94 * fw)), 1.65, 9);", "heroDist = clamp(Math.max(tall * Hh / (2 * tv * 0.92 * fh), wide * W / (2 * tv * asp * 0.98 * fw)), 1.5, 9);")
rep('<h2 class="ctitle" id="lookTitle">Customize</h2>', '<h2 class="ctitle" id="lookTitle">Locker</h2>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
