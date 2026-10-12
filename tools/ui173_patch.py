#!/usr/bin/env python3
"""v240: the axolotl gets the game's ink line like everything else: a back-face hull of its own skinned mesh in the outline colour, pushed
out along the normals, its width tied to the distance from the camera (as the slime's was) so it reads the same close in the locker and far
on the canvas."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui172_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("    const xray = new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.55, depthWrite: false, depthFunc: THREE.GreaterDepth }), ghosts = [];",
    """    const xray = new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.55, depthWrite: false, depthFunc: THREE.GreaterDepth }), ghosts = [];
    // the ink line: a back-face hull of the same skinned mesh, pushed out along the skinned normals by a width that grows with the distance from
    // the camera (clamped), so the line stays about as wide on screen close up and far away
    const INK = window.__axoInk || [0.0011, 0.004, 0.011], inkOf = meta => { const m = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide });
      m.onBeforeCompile = sh => { sh.vertexShader = sh.vertexShader.replace('#include <project_vertex>', '{ float gD = -(modelViewMatrix * vec4(transformed, 1.0)).z, gS = 0.5 * (length(modelMatrix[0].xyz) + length(modelMatrix[1].xyz)); transformed += normalize(objectNormal) * clamp(' + INK[0].toFixed(5) + ' * gD / max(gS, 1e-3), ' + INK[1].toFixed(4) + ', ' + INK[2].toFixed(4) + '); }\\n#include <project_vertex>'); };
      AXO.dqsMaterial(m, meta); m.customProgramCacheKey = () => 'axo-ink'; return m; };""")
rep("      gh.bind(me.skeleton, me.bindMatrix); gh.frustumCulled = false; gh.renderOrder = 30; me.add(gh); ghosts.push(gh); M.ghost = gh; }",
    "      gh.bind(me.skeleton, me.bindMatrix); gh.frustumCulled = false; gh.renderOrder = 30; me.add(gh); ghosts.push(gh); M.ghost = gh;\n      const ink = new THREE.SkinnedMesh(me.geometry, inkOf(M.meta)); ink.bind(me.skeleton, me.bindMatrix); ink.frustumCulled = false; ink.renderOrder = 31; ink.layers.mask = me.layers.mask; me.add(ink); M.ink = ink; }")
rep('<p class="ver">Version 239</p>', '<p class="ver">Version 240</p>')
open(DST, 'w').write(s)
print('ui173 ok', n0, '->', len(s))
