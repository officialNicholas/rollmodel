p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)
rep("  vicEl.classList.remove('out'); vicEl.hidden = false; flashScreen();",
    "  vicEl.classList.remove('out'); vicEl.hidden = false; bannerEl.classList.remove('on'); vicFit(); flashScreen();")
rep("function vicFrame(rdt) {",
"""// the winner sits in the open space between the place up top and the name below, small enough to fit in it
function vicFit() {
  if (!vic) return; const top = vicEl.querySelector('.vtop'), foot = vicEl.querySelector('.vfoot'), y0 = top.offsetTop + top.offsetHeight, y1 = foot.offsetTop, Hh = Math.max(1, viewH);
  vic.cy = clamp(((y0 + y1) / 2 + 10) / Hh, 0.26, 0.5); vic.room = clamp((y1 - y0) / Hh, 0.12, 1);
}
window.addEventListener('resize', () => { if (vic) vicFit(); });
function vicFrame(rdt) {""")
rep("const cx = land ? 0.66 : 0.5, cy = land ? 0.44 : 0.36;", "const cx = land ? 0.66 : 0.5, cy = land ? 0.44 : vic.cy || 0.36;")
rep("dist = Math.max(0.86 / tv, (n > 1 ? 1.08 : 0.6) / th) * (1.07 - 0.07 * Math.min(1, t / 4))",
    "dist = Math.max(0.86 / tv, (n > 1 ? 1.08 : 0.6) / th, land ? 0 : 0.5 / (tv * (vic.room || 1))) * (1.07 - 0.07 * Math.min(1, t / 4))")
open(p,'w').write(s); print('ok')
