# Vines and plants: ivy hanging off block corners and edges, climbing columns, planters on ledges (gen/ivy.js)
p = '/home/claude/paint-the-canvas.html'
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

rep("const THEMES = [", open(SP + 'gen/ivy.js').read() + "const THEMES = [")
rep("  floaters.length = 0; flames.length = 0; treeTops.length = 0; LIGHTS.length = 0; GLOWS.length = 0;", "  floaters.length = 0; flames.length = 0; treeTops.length = 0; LIGHTS.length = 0; GLOWS.length = 0; IVY.reset();")
rep("""    // lamps: a lantern or a torch on the face of some walls, a warm uplight at the foot of others, and in the garden a lamp post on some corners
    const LMP = T.lamps;""",
"""    // ivy: strands hanging off a corner or along an edge, and now and then a planter on top with a bush and trailing stems
    const IV = T.ivy;
    if (IV && !grave && !circ && h > 0.45) {
      const openF = (px, pz) => floorAt(px, pz) === 0 && Math.abs(px) < ARENA - 0.15 && Math.abs(pz) < ARENA - 0.15 && !BOXES.some(o => o !== b && o[4] <= 0.05 && inR(px, pz, o, 0.02)) && !RAMPS.some(rp => inR(px, pz, rp, 0.05));
      const o0 = T.trim && T.trim.w ? T.trim.w * 0.3 + 0.02 : 0.02, lenOf = () => Math.min(h - 0.08, 0.3 + R() * Math.min(1.25, h * 0.9));
      if (R() < IV.edge) {
        // a corner: strands down both faces that meet there, starting a little way in from it
        const ix = R() < 0.5 ? 0 : 1, iz = R() < 0.5 ? 0 : 1, kx = ix ? b[1] : b[0], kz = iz ? b[3] : b[2], sx = ix ? 1 : -1, sz = iz ? 1 : -1;
        for (let n = 0, m = 1 + (R() * 2 | 0); n < m; n++) { const u = 0.08 + R() * Math.min(0.7, w * 0.35); if (openF(kx - sx * u, kz + sz * 0.3)) IVY.hang(kx - sx * u, b[5], kz, 0, sz, lenOf(), R, 1, o0); }
        for (let n = 0, m = 1 + (R() * 2 | 0); n < m; n++) { const u = 0.08 + R() * Math.min(0.7, d * 0.35); if (openF(kx + sx * 0.3, kz - sz * u)) IVY.hang(kx, b[5], kz - sz * u, sx, 0, lenOf(), R, 1, o0); }
      }
      if (R() < IV.edge * 0.5) {
        // a run along one edge
        const f = (R() * 4) | 0, along = f < 2 ? w : d, nx = f === 2 ? -1 : f === 3 ? 1 : 0, nz = f === 0 ? -1 : f === 1 ? 1 : 0, fx = f === 2 ? b[0] : f === 3 ? b[1] : cx, fz = f === 0 ? b[2] : f === 1 ? b[3] : cz;
        if (openF(fx + nx * 0.3, fz + nz * 0.3)) for (let n = 0, m = 2 + (R() * 3 | 0); n < m; n++) { const u = (R() - 0.5) * (along - 0.3); IVY.hang(fx + (nz ? u : 0), b[5], fz + (nx ? u : 0), nx, nz, lenOf() * 0.8, R, 1, o0); }
      }
      if (IV.planter && w > 1.5 && d > 1.5 && R() < IV.planter) {
        // a planter set along one edge of the top: dark stone, a gilt rim, a heaped bush with a few stems trailing over its front
        const alongX = w >= d, pl = Math.min(1.35, (alongX ? w : d) - 0.8), pd = 0.36, ph = 0.24, sgn = R() < 0.5 ? -1 : 1, inset = (T.trim && T.trim.w ? T.trim.w : 0.15) + 0.1 + pd / 2;
        const px = alongX ? cx + (R() - 0.5) * Math.max(0, w - pl - 0.9) : (sgn < 0 ? b[0] + inset : b[1] - inset), pz = alongX ? (sgn < 0 ? b[2] + inset : b[3] - inset) : cz + (R() - 0.5) * Math.max(0, d - pl - 0.9);
        const gx = alongX ? pl : pd, gz = alongX ? pd : pl, fx = alongX ? 0 : sgn, fz = alongX ? sgn : 0;
        put(M.foot || M.dark, at(HI ? rbox(gx, ph, gz, 0.03) : new THREE.BoxGeometry(gx, ph, gz), px, b[5] + ph / 2, pz));
        if (HI && M.trim) put(M.trim, at(rbox(gx + 0.05, 0.05, gz + 0.05, 0.02), px, b[5] + ph - 0.005, pz));
        IVY.bush(px, b[5] + ph - 0.03, pz, gx * 0.5, 0.2, gz * 0.5, Math.round(26 + 34 * pl), R);
        for (let n = 0, m = 2 + (R() * 2 | 0); n < m; n++) { const u = (R() - 0.5) * (pl - 0.15); IVY.hang(px + fx * gx / 2 + (alongX ? u : 0), b[5] + ph, pz + fz * gz / 2 + (alongX ? 0 : u), fx, fz, ph * (0.6 + R() * 0.35), R, 0.85, 0.03); }
      }
    }
    // lamps: a lantern or a torch on the face of some walls, a warm uplight at the foot of others, and in the garden a lamp post on some corners
    const LMP = T.lamps;""")
# columns: ivy winding up them, above the base and below the capital
rep("      else if ((T.id === 'cathedral' || T.id === 'crypt') && kind === 'column') { const tm = T.id === 'cathedral' ? M.gold : M.stone;",
    "      else if ((T.id === 'cathedral' || T.id === 'crypt') && kind === 'column') { if (T.ivy && R() < T.ivy.col) IVY.climb(cx, cz, rad, top - 0.42, R, 0.34); const tm = T.id === 'cathedral' ? M.gold : M.stone;")
# climb starts above a base ring when one is given
s = s.replace("  function climb(cx, cz, rad, H, R) {\n    for (let st = 0; st < 2; st++) { const a0 = R() * 6.28, turn = (1.1 + R() * 0.6) * (st ? -1 : 1), top = H * (0.45 + R() * 0.45);\n      for (let y = 0.05; y < top; y += 0.06 + R() * 0.04) {",
              "  function climb(cx, cz, rad, H, R, y0) {\n    y0 = y0 || 0.05;\n    for (let st = 0; st < 2; st++) { const a0 = R() * 6.28, turn = (1.1 + R() * 0.6) * (st ? -1 : 1), top = y0 + (H - y0) * (0.45 + R() * 0.55);\n      for (let y = y0; y < top; y += 0.06 + R() * 0.04) {", 1)
assert "function climb(cx, cz, rad, H, R, y0)" in s
# one mesh for the stage's leaves
rep("  setMotes(T); glowBatch.set(GLOWS);", "  setMotes(T); glowBatch.set(GLOWS);\n  { const ig = IVY.build(T.ivy && T.ivy.tint); if (ig) { const im = new THREE.Mesh(ig, IVY.material()); im.receiveShadow = true; im.renderOrder = 1; stageGroup.add(im); } }")
# the cathedral's ivy
rep("strips: 0.5, candles: 0.42,", "strips: 0.5, candles: 0.42, ivy: { edge: 0.5, col: 0.6, planter: 0.32, tint: 0xE8F0E0 },")
open(p, 'w').write(s)
print('ok')
