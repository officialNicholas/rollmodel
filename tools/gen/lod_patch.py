# performance: lighter stage geometry where the detail never shows at play distance. The island's leafy clumps (bushes) drop from ~1900
# triangles each to ~560; the little rounded trims and skirting boards on every stage get one bevel step instead of two; and the stage's
# one-draw shadow caster leaves out what can't cast a visible shadow (skirting, ropes, pebbles, starfish, post ends, glowing flames, leaves
# lying flat). Slimes far from the camera skip their see-through ghost
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:150])
    src = src.replace(old, new)

rep("const lumpBall = (r, x, y, z, sy, Rg) => { const g = new THREE.SphereGeometry(r, 36, 26)", "const lumpBall = (r, x, y, z, sy, Rg) => { const g = new THREE.SphereGeometry(r, 20, 14)")
# trims and skirting: rbox with one bevel step (s = 1)
rep("if (HI && T.lip) { const A = ARENA, t = 0.13; for (const [w2, d2, x, z] of [[2 * A + 2 * t, t, 0, -A - t / 2], [2 * A + 2 * t, t, 0, A + t / 2], [t, 2 * A, -A - t / 2, 0], [t, 2 * A, A + t / 2, 0]]) put(M.trim, at(rbox(w2, 0.17, d2, 0.045), ",
    "if (HI && T.lip) { const A = ARENA, t = 0.13; for (const [w2, d2, x, z] of [[2 * A + 2 * t, t, 0, -A - t / 2], [2 * A + 2 * t, t, 0, A + t / 2], [t, 2 * A, -A - t / 2, 0], [t, 2 * A, A + t / 2, 0]]) put(M.trim, at(rbox(w2, 0.17, d2, 0.045, 1), ")
for side in ["if (sideFree(0)) put(M.trim, at(rbox(w + 2 * ov, th, tw, 0.03), cx, ty, b[2] + tw / 2 - ov));", "if (sideFree(1)) put(M.trim, at(rbox(w + 2 * ov, th, tw, 0.03), cx, ty, b[3] - tw / 2 + ov));"]:
    rep(side, side.replace("0.03)", "0.03, 1)"))
for side in ["if (sideFree(2)) put(M.trim, at(rbox(tw, th, Math.max(0.1, d - 2 * tw + 2 * ov), 0.03), b[0] + tw / 2 - ov, ty, cz));", "if (sideFree(3)) put(M.trim, at(rbox(tw, th, Math.max(0.1, d - 2 * tw + 2 * ov), 0.03), b[1] - tw / 2 + ov, ty, cz));"]:
    rep(side, side.replace("0.03)", "0.03, 1)"))
rep("if (T.foot) put(M.foot, at(rbox(lx, fh, lz, 0.025), fx + nx * 0.02, fh / 2, fz + nz * 0.02));", "if (T.foot) put(M.foot, at(rbox(lx, fh, lz, 0.025, 1), fx + nx * 0.02, fh / 2, fz + nz * 0.02));")
rep("put(M.foot || M.dark, at(HI ? rbox(gx, ph, gz, 0.03) : new THREE.BoxGeometry(gx, ph, gz), px, b[5] + ph / 2, pz));", "put(M.foot || M.dark, at(HI ? rbox(gx, ph, gz, 0.03, 1) : new THREE.BoxGeometry(gx, ph, gz), px, b[5] + ph / 2, pz));")
rep("if (HI && M.trim) put(M.trim, at(rbox(gx + 0.05, 0.05, gz + 0.05, 0.02), px, b[5] + ph - 0.005, pz));", "if (HI && M.trim) put(M.trim, at(rbox(gx + 0.05, 0.05, gz + 0.05, 0.02, 1), px, b[5] + ph - 0.005, pz));")
# the shadow caster: only what can throw a shadow you'd see
rep("  for (const [mat, list] of bag) { const m = new THREE.Mesh(mergeGeos(list, true), mat); m.receiveShadow = true; m.layers.enable(3); stageGroup.add(m); shadowG.push(m.geometry); }",
    "  const noCast = new Set([M.foot, M.rope, M.pebble, M.star, M.postEnd, M.flameCore, M.leafBig, M.strip].filter(Boolean));\n  for (const [mat, list] of bag) { const m = new THREE.Mesh(mergeGeos(list, true), mat); m.receiveShadow = true; m.layers.enable(3); stageGroup.add(m); if (!noCast.has(mat)) shadowG.push(m.geometry); }")
open(P, 'w').write(src)
print('ok', len(src))
