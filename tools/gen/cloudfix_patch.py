# the giant clouds over the stage: the ring of clouds round the stage drifted along x forever (wrapping at 160), so in time the ones
# level with it sailed straight across the stage, huge. They now drift round the stage at their own distance instead. Also the drifting
# clouds faded their shadow stand-in instead of their outline (the stand-in then drew depth in the main pass), and one close to the
# camera now goes see-through too
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)
rep("const addCloud = (vi, x, y, z, ry, sc, v) => { const m = new THREE.Object3D(); m.position.set(x, y, z); m.rotation.y = ry; m.scale.setScalar(sc); clouds.push({ m, v, vi, k: cvN[vi]++, y0: y, layer: clouds.length < 18 ? 0 : 1 }); };",
    "const addCloud = (vi, x, y, z, ry, sc, v) => { const m = new THREE.Object3D(); m.position.set(x, y, z); m.rotation.y = ry; m.scale.setScalar(sc); clouds.push({ m, v, vi, k: cvN[vi]++, y0: y, layer: clouds.length < 18 ? 0 : 1, a: Math.atan2(z, x), d: Math.hypot(x, z) }); };")
# the ring round the stage circles it (never across it); the layer far below still drifts straight on
rep("for (const c of clouds) { c.m.position.x += c.v * dt; if (c.m.position.x > 160) c.m.position.x -= 320;",
    "for (const c of clouds) { if (c.layer) { c.a += c.v * dt / c.d; c.m.position.x = Math.cos(c.a) * c.d; c.m.position.z = Math.sin(c.a) * c.d; } else { c.m.position.x += c.v * dt; if (c.m.position.x > 160) c.m.position.x -= 320; }")
rep("""    const occ = !inside && state !== 'menu' && cloudHides(m.cx, 1.17, m.cz);
    g.userData.fade += ((inside ? 0.35 : occ ? 0.14 : 1) - g.userData.fade) * Math.min(1, rdt * (occ ? 12 : 6));
    g.children[0].material.opacity = g.userData.fade; g.children[1].material.opacity = g.userData.fade; g.children[1].visible = g.userData.fade > 0.6;""",
"""    const occ = !inside && state !== 'menu' && cloudHides(m.cx, 1.17, m.cz), near = smoothstep(4.5, 8, camera.position.distanceTo(g.position));
    g.userData.fade += (Math.min(inside ? 0.35 : occ ? 0.14 : 1, 0.1 + 0.9 * near) - g.userData.fade) * Math.min(1, rdt * (occ ? 12 : 6));
    // (its children: the cloud, its shadow stand-in, which only ever draws into the shadow map, and its outline)
    g.children[0].material.opacity = g.userData.fade; g.children[2].material.opacity = g.userData.fade; g.children[2].visible = g.userData.fade > 0.6;""")
open(P, 'w').write(src)
print('ok')
