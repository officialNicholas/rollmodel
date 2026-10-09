#!/usr/bin/env python3
"""Results on the gallery wall (no card), and the painting hung closer: a slow sway instead of a full orbit, no fog, a touch more light. On top of ui18_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui18_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# the results sit straight on the wall: no card, no tape, no shadow, in every layout
css = '''
/* the results live on the gallery wall itself */
#end,#end.sheet{background:none;border:0;border-radius:0;box-shadow:none}
#end::before{display:none}
@media (min-width:700px){#end{bottom:0;padding-bottom:max(18px,env(safe-area-inset-bottom))}}
@media (max-height:520px) and (min-aspect-ratio:1/1){#end{bottom:max(6px,env(safe-area-inset-bottom));top:max(6px,env(safe-area-inset-top));gap:6px;padding:8px 14px 8px}#end .rhead{gap:3px}#end .jnums{height:30px}#end .jnums b{font-size:26px}#end .jbar{height:12px}#end .brow{min-height:36px}#end .bico{width:28px;height:28px}#end .reprow{padding:4px 10px}#end .xpmeter{width:90px;height:51px;background-size:540px 306px}#end .btn.play{min-height:42px;padding-top:5px;padding-bottom:5px}#end .row .btn{min-height:36px}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]

# the wall is always up behind the results; only the frame goes when there's no room for it
rep("    gf.hidden = tiny; gw.hidden = tiny;\n", "    gf.hidden = tiny; gw.hidden = false;\n    if (tiny) { gw.style.cssText = '--sx:50%;--sy:0%;clip-path:none'; return; }\n")

# the painting hangs closer: the camera settles square to the canvas and sways a little, so the mat is fitted to that sway, not a whole turn; the mat may crop the rim a touch
rep("outroSc = 1, outK = 0, celebrating = false, endInfo = null;", "outroSc = 1, outroBase = 0, outK = 0, fogK = 0, celebrating = false, endInfo = null;")
rep("  outro = true; outroT = 0; const id = runId;\n", "  outro = true; outroT = 0; outroBase = Math.round(camYaw / (Math.PI / 2)) * (Math.PI / 2); const id = runId;\n")
rep("if (state === 'dead' && outro) { outroT += rdt; camYaw += rdt * 0.07; const sc",
    "if (state === 'dead' && outro) { outroT += rdt; { const ty = outroBase + Math.sin(outroT * 0.3) * 0.2; camYaw += (ty - camYaw) * (1 - Math.exp(-rdt * 1.4)); } const sc")
rep("    for (let k = 0; k < 24; k++) {\n      const yw = k / 24 * Math.PI * 2, fx = Math.sin(yw), fz = Math.cos(yw);",
    "    for (let k = 0; k < 9; k++) {\n      const yw = outroBase + (k / 8 - 0.5) * 0.5, fx = Math.sin(yw), fz = Math.cos(yw);")
rep("fit = outroFit(mw * 0.94, mh * 0.9);", "fit = outroFit(mw * 1.06, mh * 1.04);")
rep("const ww = clamp(fit.bw / 0.94, 60, mw), wh = clamp(fit.bh / 0.9, 60, mh),", "const ww = clamp(fit.bw / 1.06, 60, mw), wh = clamp(fit.bh / 1.04, 60, mh),")

# no fog on the painting, and a little gallery light on the dark stages
rep("  scene.fog.color.copy(HOR).lerp(HOR_HEAT, dayK).lerp(HOR_RAIN, rainK * (1 - dayK));\n",
    "  scene.fog.color.copy(HOR).lerp(HOR_HEAT, dayK).lerp(HOR_RAIN, rainK * (1 - dayK));\n  fogK += ((state === 'dead' && outro ? 1 : 0) - fogK) * (1 - Math.exp(-rdt * 2)); { const fn = TH.fog ? TH.fog[0] : 70, ff = TH.fog ? TH.fog[1] : 200; scene.fog.near = fn + 4000 * fogK; scene.fog.far = ff + 8000 * fogK; }\n")
rep("hemi.intensity = (NIGHT.hemi + (DAY.hemi - NIGHT.hemi) * dayK - 0.08 * rainK) * LK.hemi * LIGHT_K;",
    "hemi.intensity = (NIGHT.hemi + (DAY.hemi - NIGHT.hemi) * dayK - 0.08 * rainK) * LK.hemi * LIGHT_K * (1 + 0.7 * outK * (1 - dayK));")
rep("sun.intensity = (NIGHT.keyI + (DAY.keyI - NIGHT.keyI) * dayK - 0.18 * rainK) * LK.key * LIGHT_K;",
    "sun.intensity = (NIGHT.keyI + (DAY.keyI - NIGHT.keyI) * dayK - 0.18 * rainK) * LK.key * LIGHT_K * (1 + 0.35 * outK * (1 - dayK));")
rep('<p class="ver">Version 88</p>', '<p class="ver">Version 89</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
