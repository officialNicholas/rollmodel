p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:80]); s=s.replace(a,b)
rep("function measureOutro() {\n  // the stage is framed in the space the results leave: above them on a phone, beside them on a wide screen\n  outroSide = sideMQ.matches && end.offsetLeft > viewW * 0.35;\n  if (outroSide) { outroOffX = (viewW - end.offsetLeft) / 2; outroOffY = 0; outroFrac = clamp(end.offsetLeft / Math.max(1, viewW), 0.3, 1); }\n  else { outroOffX = 0; outroOffY = Math.max(0, (viewH - end.offsetTop) / 2); outroFrac = clamp(end.offsetTop / Math.max(1, viewH), 0.3, 1); }\n}",
"""function measureOutro() {
  // the stage is framed in the space the results leave: above them on a phone, beside them on a wide screen
  outroSide = sideMQ.matches && end.offsetLeft > viewW * 0.35;
  if (outroSide) { outroOffX = (viewW - end.offsetLeft) / 2; outroOffY = 0; outroFrac = clamp(end.offsetLeft / Math.max(1, viewW), 0.3, 1); }
  else { outroOffX = 0; outroOffY = Math.max(0, (viewH - end.offsetTop) / 2); outroFrac = clamp(end.offsetTop / Math.max(1, viewH), 0.3, 1); }
  outroSc = outroFit();
}
// how far the orbiting camera pulls back so the whole canvas, rim and all, stays inside that space at every angle of the turn
const fitCam = new THREE.PerspectiveCamera(60, 1, 1, 500);
function outroFit() {
  fitCam.fov = baseFov; fitCam.aspect = viewW / Math.max(1, viewH); fitCam.updateProjectionMatrix();
  const lx = (outroSide ? outroFrac : 1) * 0.92, ly = (outroSide ? 1 : outroFrac) * 0.9, R = ARENA + 1.2;
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
}""")
rep("outroOffY = 0, outroOffX = 0, outroSide = false, outroFrac = 1, outK = 0,", "outroOffY = 0, outroOffX = 0, outroSide = false, outroFrac = 1, outroSc = 1, outK = 0,")
rep("const tf = Math.tan(camera.fov * Math.PI / 360), sc = ARENA / 26.4 * (outroSide ? clamp(0.62 / (tf * camera.aspect * outroFrac), 1, 1.8) * 1.04 : Math.max(clamp(0.5 / (tf * camera.aspect), 1, 1.7), clamp(0.62 / outroFrac, 1, 1.8))), fx",
    "const sc = end.hidden ? ARENA / 26.4 * Math.max(clamp(0.5 / (Math.tan(camera.fov * Math.PI / 360) * camera.aspect), 1, 1.7), 1.2) : outroSc, fx")
open(p,'w').write(s); print('ok')
