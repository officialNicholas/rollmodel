#!/usr/bin/env python3
"""Flying on the paint pack the blob hangs from it: its lower body and tail curve down under it and its head tips up a little. The hockey mask sits higher and wider over the face. On top of ui53_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui53_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- the hang ----
rep("uniform vec4 sMove, sShape, sHead, sEar, sBall, sWave, sCoat, sWade, sMicro, sReact, sTilt, sCrawl, sRim, sGait, sBlob, mHead, mNeck, mEar, mBody, mFace;", "uniform float sHang;\nuniform vec4 sMove, sShape, sHead, sEar, sBall, sWave, sCoat, sWade, sMicro, sReact, sTilt, sCrawl, sRim, sGait, sBlob, mHead, mNeck, mEar, mBody, mFace;")
rep("    n = rotA(n, vec3(1.0, 0.0, 0.0), -atan(sl));\n  }", """    n = rotA(n, vec3(1.0, 0.0, 0.0), -atan(sl));
  }
  // hanging from the paint pack (sHang): behind the head the body curves down and under, the tail most of all
  if (sHang > 0.001) { float bw = (1.0 - hw) * sHang, cv = sp * sp; q.y -= bw * (0.2 * cv + 0.34 * cv * sp); q.z += bw * 0.1 * cv; n = rotA(n, vec3(1.0, 0.0, 0.0), -0.6 * atan(bw * (0.4 * sp + 1.0 * cv))); }""")
rep("    const U = I.U = { sT: { value: 0 }, sMove:", "    const U = I.U = { sT: { value: 0 }, sHang: { value: 0 }, sMove:")
rep("pop: 0, ball: 0, bend: 0, tuck: 0,", "pop: 0, ball: 0, bend: 0, tuck: 0, hang: 0,")
rep("    U.sGait.value.set(s.liz, gW, gPh, slug ? clampS(o.tailCurl || 0, 0, 1) : 0);", "    U.sGait.value.set(s.liz, gW, gPh, slug ? clampS(o.tailCurl || 0, 0, 1) : 0);\n    s.hang += ((slug ? (o.hang || 0) : 0) - s.hang) * Math.min(1, dt * 6); U.sHang.value = s.hang;")
rep("    s.tip += (tipT - s.tip) * Math.min(1, dt * 10);", "    s.tip += (tipT + 0.2 * s.hang - s.tip) * Math.min(1, dt * 10); // (hanging from the pack: head up a touch)")
rep("o.maxBall = hopAir ? 0.3 : 1;", "o.maxBall = hopAir ? 0.3 : 1; o.hang = D.rocket && D.st === 'play' ? (D.rocket.ph === 'dive' && !D.rocket.slow ? 0.35 : 1) : 0;")

# ---- the mask, higher and wider ----
rep("const HOCKEY_FIT = window.__hockeyFit || { s: 0.36, y: -0.13, z: 0.43, rx: -0.04 };", "const HOCKEY_FIT = window.__hockeyFit || { s: 0.4, sx: 1.28, y: -0.02, z: 0.42, rx: -0.04 };")
rep("W.hockey.scale.multiplyScalar(mk * HOCKEY_FIT.s); }", "W.hockey.scale.multiplyScalar(mk * HOCKEY_FIT.s); W.hockey.scale.x *= HOCKEY_FIT.sx || 1; }")

m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
