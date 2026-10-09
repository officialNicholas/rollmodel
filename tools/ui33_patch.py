#!/usr/bin/env python3
"""The locker is a dark stage under a spotlight: a pool of light on the wall and floor behind the blob, the rest falling away, a halo of your colour, and a stronger key and rim on the character. On top of ui32_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui32_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# the floor: in the locker a pool of light under the blob, the ink underfoot glossy in it, the rest of the floor falling to dark,
# your colour spilling faintly into the dark, motes in the light
rep("    c = mix(c, uCol * 0.9, fl * 0.5 * (1.0 - k));\n  } else if (tw > 0.0) {",
    """    c = mix(c, uCol * 0.9, fl * 0.5 * (1.0 - k));
    if (uLook > 0.001) {
      float dl = length(rel * vec2(1.0, 1.3)), pool2 = smoothstep(2.3, 0.2, dl); pool2 *= pool2;
      float pour = 1.0 - smoothstep(-0.15, 0.15, dl - uSweep * 3.5); vec3 ink = mix(uCol2, uCol, pour);
      vec3 dark = vec3(0.07, 0.05, 0.09) * (0.9 + 0.2 * hs(floor(q * 60.0)));
      vec3 lit = mix(dark, vec3(0.8, 0.74, 0.68), pool2 * pool2 * 0.95);
      lit = mix(lit, ink * bristle * (0.12 + 0.88 * pool2), k);
      lit += ink * 0.16 * smoothstep(4.5, 1.0, dl) * (1.0 - pool2);
      lit = mix(lit, vec3(1.0), fl * 0.7 * pool2);
      c = mix(c, lit, uLook);
    }
  } else if (tw > 0.0) {""")
# the wall: the pour is gone. A spotlight from above: a cone down the wall, a pool of light behind the blob, your colour as a halo
# round it (a new colour rings out through the halo when you pick one), the rest of the wall dark
OLD = s[s.index("    if (uLook > 0.001) {\n      // the locker: a fresh coat of your ink"):s.index("  } else { c = paper * 0.78; }")]
NEW = """    if (uLook > 0.001) {
      vec2 rw = wq - vec2(dot(uBlob.xz - W.xz, t2), 1.05); float dw = length(rw);
      float spot = smoothstep(2.7, 0.0, length(rw * vec2(0.85, 1.0)));
      float beam = smoothstep(1.0, 0.0, abs(rw.x) / (0.5 + max(0.0, rw.y) * 0.55)) * smoothstep(-0.6, 2.4, rw.y) * (0.75 + 0.25 * vn(vec2(rw.y * 3.0 - uTime * 0.4, rw.x * 2.0)));
      float pour = 1.0 - smoothstep(-0.15, 0.15, dw - uSweep * 3.5); vec3 ink = mix(uCol2, uCol, pour);
      vec3 dark = vec3(0.06, 0.045, 0.085) * (0.9 + 0.2 * hs(floor(wq * 60.0)));
      vec3 lit = mix(dark, vec3(0.88, 0.82, 0.76), clamp(spot * spot * 0.95 + beam * 0.3, 0.0, 1.0));
      lit += ink * 0.22 * smoothstep(5.0, 0.9, dw) * (1.0 - spot);
      lit = mix(lit, vec3(1.0), smoothstep(0.986, 1.0, vn(wq * 7.0 + vec2(uTime * 0.06, uTime * 0.11))) * spot * 0.5);
      c = mix(c, lit, uLook);
    }
"""
s = s.replace(OLD, NEW)
rep("  } else { c = paper * 0.78; }", "  } else { c = mix(paper * 0.78, vec3(0.05, 0.04, 0.07), uLook); }")
# the character: a harder key, less fill, and a rim in a cool white tinted with your colour, so it stands off the dark
rep("  hemi.intensity = Math.max(hi, 0.8 * LIGHT_K); sun.intensity = Math.max(si, 1.15 * LIGHT_K); sun.color.copy(lobbyKey);\n  sun.position.set(P.x + nx / nl * 3 - nz / nl * 3.2, 5.5,",
    "  const lk = lobbyU.uLook.value; hemi.intensity = Math.max(hi, 0.8 * LIGHT_K) * (1 - 0.32 * lk); sun.intensity = Math.max(si, 1.15 * LIGHT_K) * (1 + 0.3 * lk); sun.color.copy(lobbyKey);\n  lkRimSave.copy(RIG.uRigRimC.value); RIG.uRigRimC.value.set(0xE8F0FF).lerp(lobbyU.uCol.value, 0.3).multiplyScalar(1 + 0.8 * lk);\n  sun.position.set(P.x + nx / nl * 3 - nz / nl * 3.2, 5.5,")
rep("  hemi.intensity = hi; sun.intensity = si; sun.color.copy(keySave); sun.position.copy(lobbySunPos); sun.target.position.copy(lobbyTgt); sun.target.updateMatrixWorld();\n}\n// where the blob stands",
    "  hemi.intensity = hi; sun.intensity = si; sun.color.copy(keySave); sun.position.copy(lobbySunPos); sun.target.position.copy(lobbyTgt); sun.target.updateMatrixWorld(); RIG.uRigRimC.value.copy(lkRimSave);\n}\n// where the blob stands")
rep("const lobbyKey = new THREE.Color(0xFFF1E2), lobbySunPos = new THREE.Vector3(), lobbyTgt = new THREE.Vector3();", "const lobbyKey = new THREE.Color(0xFFF1E2), lobbySunPos = new THREE.Vector3(), lobbyTgt = new THREE.Vector3(), lkRimSave = new THREE.Color();")
rep('<p class="ver">Version 102</p>', '<p class="ver">Version 103</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
