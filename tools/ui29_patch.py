#!/usr/bin/env python3
"""No see-through refraction in the fight-card portraits: it sampled the main view's grab and ghosted the face. On top of ui28_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui28_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the slime's see-through refracts a grab of the main frame, addressed in main-screen pixels: in an offscreen portrait that is the wrong
# picture at the wrong size, and the blob's own face came back through its skin as a ghost. The portrait renders without it
rep("  renderer.setRenderTarget(portRT); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, portCam);",
    "  const gk = RIG.uGrabK.value, gfn = JELLY_GRAB.fn; RIG.uGrabK.value = 0; JELLY_GRAB.fn = null; // (and no grab taken mid-portrait either)\n  renderer.setRenderTarget(portRT); renderer.setClearColor(0x000000, 0); renderer.clear(); renderer.render(scene, portCam); RIG.uGrabK.value = gk; JELLY_GRAB.fn = gfn;")
rep('<p class="ver">Version 98</p>', '<p class="ver">Version 99</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
