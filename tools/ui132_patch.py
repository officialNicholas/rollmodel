#!/usr/bin/env python3
"""v207: a steadier CPU. Measured over simulated AI-vs-AI matches (tools/aisim.py, tools/aitrace.py): most of its hard left-to-right
steering flips came straight after a re-plan, when the route it had picked half a second earlier lost out to one setting off another
way, so it zig-zagged instead of sweeping. Targets are now scored by the way their route actually sets off (not the straight line
to the end), and a re-plan keeps the current target unless the new one is clearly better."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui131_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('const gainT = new Float64Array(16), ownT = new Float64Array(16), topS = new Float64Array(8), topI = new Int32Array(8), topP = new Float64Array(8);',
    'const gainT = new Float64Array(16), ownT = new Float64Array(16), topS = new Float64Array(8), topI = new Int32Array(8), topP = new Float64Array(8), topT = new Float64Array(8);\n'
    '// how far round a route makes you turn as it sets off (0 straight on, 1 right round): the first point of it a couple of steps out,\n'
    '// not the straight line to its end, which can look ahead when the way there starts by turning back\n'
    'function routeTurn(D, id) { let i = id, a = id, g = 0; while (i >= 0 && g++ < 600) { const n = NAV.nodes[i]; if (Math.hypot(n.x - D.x, n.z - D.z) < 2.6) break; a = i; i = nPrev[i]; } const n = NAV.nodes[a]; return Math.abs(wrapA(Math.atan2(n.x - D.x, n.z - D.z) - D.yaw)) / Math.PI; }')
rep('    if (nTop < K || sc > topS[nTop - 1]) { let q = nTop < K ? nTop++ : nTop - 1; while (q > 0 && topS[q - 1] < sc) { topS[q] = topS[q - 1]; topI[q] = topI[q - 1]; topP[q] = topP[q - 1]; q--; } topS[q] = sc; topI[q] = n.id; topP[q] = p; }',
    '    if (nTop < K || sc > topS[nTop - 1]) { let q = nTop < K ? nTop++ : nTop - 1; while (q > 0 && topS[q - 1] < sc) { topS[q] = topS[q - 1]; topI[q] = topI[q - 1]; topP[q] = topP[q - 1]; topT[q] = topT[q - 1]; q--; } topS[q] = sc; topI[q] = n.id; topP[q] = p; topT[q] = turn; }')
rep('  if (!nTop) { ai.path = null; return; }\n  const pq = Math.min(nTop - 1, (Math.random() * Math.min(AI.pick, nTop)) | 0);',
    '  if (!nTop) { ai.path = null; return; }\n'
    '  // the short list, judged by the way each route sets off: one that looks ahead but turns back first loses the turn bonus, one that\n'
    '  // carries straight on keeps it, so the CPU sweeps on instead of zig-zagging\n'
    '  for (let q = 0; q < nTop; q++) topS[q] = topS[q] / (1 - 0.4 * topT[q]) * (1 - 0.4 * routeTurn(D, topI[q]));\n'
    '  for (let q = 1; q < nTop; q++) { const sv = topS[q], iv = topI[q], pv2 = topP[q], tv = topT[q]; let r = q; while (r > 0 && topS[r - 1] < sv) { topS[r] = topS[r - 1]; topI[r] = topI[r - 1]; topP[r] = topP[r - 1]; topT[r] = topT[r - 1]; r--; } topS[r] = sv; topI[r] = iv; topP[r] = pv2; topT[r] = tv; }\n'
    '  const pq = Math.min(nTop - 1, (Math.random() * Math.min(AI.pick, nTop)) | 0);')
rep('const p = ai.poundAt === ai.tgt ? pv(n) : 0, cur = (nAcc[n.id] + 0.7 * v + p) / (nDist[n.id] + 2.5) * (1 - 0.4 * Math.abs(wrapA(Math.atan2(n.x - D.x, n.z - D.z) - D.yaw)) / Math.PI); if (cur > pick[0] * 0.78) pick = [cur, ai.tgt, p];',
    'const p = ai.poundAt === ai.tgt ? pv(n) : 0, cur = (nAcc[n.id] + 0.7 * v + p) / (nDist[n.id] + 2.5) * (1 - 0.4 * routeTurn(D, n.id)); if (cur > pick[0] * 0.66) pick = [cur, ai.tgt, p]; /* (a change of plan costs a turn and a wobble: only for a clearly better spot) */')
rep('<p class="ver">Version 206</p>', '<p class="ver">Version 207</p>')
open(DST, 'w').write(s)
print('ui132 ok', n0, '->', len(s))
