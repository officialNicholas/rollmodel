#!/usr/bin/env python3
"""The results sheet: no splat behind the verdict, and the share bar as wet paint with a rippling surface, drips and a slow slosh for as long as the sheet is up. The Squid eyes cleaned up to the inspiration: one smooth almond outline heavier over the top, one point at the outer corner, a big iris with a dark ring and one catchlight, a single leaf of a brow. On top of ui50_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui50_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- the results sheet ----
a = s.index('<h2 class="rtitle" id="endTitle"><svg class="rsplat"'); b = s.index('</svg>', a) + 6
s = s[:a] + '<h2 class="rtitle" id="endTitle">' + s[b:]
# the bar: the paint has a surface that ripples and drips, and goes on sloshing
rep("  const L = { segs: [], drops: [], last: 0, host: host };", "  const L = { segs: [], drops: [], last: 0, host: host, surf: !!(host && host.classList.contains('jbar')) }; // (the results bar is a tank of paint: its surface shows)")
rep("      const a0 = sg.x0 <= 0.0005 ? 0 : h * (0.1 + Math.min(0.9, sg.a0 * 40)), a1 = sg.x1 >= 0.9995 ? 0 : h * (0.1 + Math.min(0.9, sg.a1 * 40));\n      if (sg.x1 - sg.x0 <= 0.0005) continue;\n      g.beginPath();\n      for (let i = 0; i <= N; i++) { const y = i / N * h, x = a0 ? edge(sg.x0, a0, sg.ph, y) : -6; i ? g.lineTo(x, y) : g.moveTo(x, y); }\n      for (let i = N; i >= 0; i--) { const y = i / N * h, x = a1 ? edge(sg.x1, a1, sg.ph + 1.3, y) : w + 6; g.lineTo(x, y); }\n      g.closePath(); g.fillStyle = sg.col; g.fill();",
    """      const wild = L.surf ? 2.2 : 1, a0 = sg.x0 <= 0.0005 ? 0 : h * (0.1 * wild + Math.min(0.9, sg.a0 * 40)), a1 = sg.x1 >= 0.9995 ? 0 : h * (0.1 * wild + Math.min(0.9, sg.a1 * 40));
      if (sg.x1 - sg.x0 <= 0.0005) continue;
      // the surface of the paint, when it shows: a little below the top, rolling slowly, with a slosh that builds whenever the paint moves
      const sl = L.surf ? Math.min(1, (sg.a0 + sg.a1) * 30) : 0, surf = x => !L.surf ? 0 : h * (0.16 + 0.07 * Math.sin(x / w * 6.3 + t * 1.9 + sg.ph) + 0.04 * Math.sin(x / w * 13.1 - t * 2.7 + sg.ph * 2.0) + sl * 0.16 * Math.sin(x / w * 9.0 + t * 7.0));
      g.beginPath(); const y0 = surf(sg.x0 * w);
      for (let i = 0; i <= N; i++) { const y = y0 + i / N * (h - y0), x = a0 ? edge(sg.x0, a0, sg.ph, y) : -6; i ? g.lineTo(x, y) : g.moveTo(x, y); }
      for (let i = N; i >= 0; i--) { const y = y0 + i / N * (h - y0), x = a1 ? edge(sg.x1, a1, sg.ph + 1.3, y) : w + 6; g.lineTo(x, y); }
      if (L.surf) { const xa = a1 ? edge(sg.x1, a1, sg.ph + 1.3, y0) : w + 6, xb = a0 ? edge(sg.x0, a0, sg.ph, y0) : -6, M = 16; for (let j = 1; j < M; j++) { const x = xa + (xb - xa) * j / M; g.lineTo(x, surf(x)); } }
      g.closePath(); g.fillStyle = sg.col; g.fill();
      // now and then a drop breaks off the surface and runs down the glass
      if (L.surf && h >= 12 && L.drops.length < 28 && Math.random() < 0.012) { const x = (sg.x0 + Math.random() * (sg.x1 - sg.x0)) * w; L.drops.push({ x, y: surf(x) + 2, vx: 0, vy: 20 + Math.random() * 30, r: 1.5 + Math.random() * (h * 0.11), col: sg.col, life: 0.9 }); }""")
# the bar is taller and glossier for it
rep(".jbar{height:18px}", ".jbar{height:30px;border-radius:5px}")
css = '''
/* the results: the verdict on its own, the paint in a tank */
.rsplat{display:none}
.rtitle{text-shadow:.05em .05em 0 var(--black),.1em .1em 0 rgba(0,0,0,.35)}
#end .jbar{height:30px;border:2.5px solid var(--black);border-radius:5px;background:#2A2338 repeating-linear-gradient(-55deg,rgba(255,255,255,.04) 0 6px,rgba(255,255,255,0) 6px 14px);box-shadow:3px 3px 0 var(--black),inset 0 -2px 6px rgba(0,0,0,.35)}
#end .jbar::after{content:"";position:absolute;left:0;right:0;top:2px;height:5px;border-radius:3px;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.35) 30%,rgba(255,255,255,.35) 70%,rgba(255,255,255,0));pointer-events:none;mix-blend-mode:screen}
@media (max-height:720px) and (max-aspect-ratio:1/1){#end .jbar{height:24px}}
@media (max-height:520px) and (min-aspect-ratio:1/1){#end .jbar{height:20px}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]

# ---- the Squid eyes, cleaned up ----
rep("if (sqd > 0.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; vec2 pc0 = vec2(sd0 * 0.4, 0.16); vec2 l = fq - pc0; l.y = l.y * 1.18 + 0.02; l.x = (l.x + l.y * sd0 * 0.28) * 0.95; fqe = pc0 + l; }",
    "if (sqd > 0.5) { float sd0 = fq.x < 0.0 ? -1.0 : 1.0; vec2 pc0 = vec2(sd0 * 0.4, 0.16); vec2 l = fq - pc0; l.y = l.y * 1.1 + 0.01; l.x = (l.x + l.y * sd0 * 0.2) * 0.97; fqe = pc0 + l; }")
rep("  if (sqd > 0.5) { float d1 = 0.0; for (int k = 0; k < 16; k++) { float a = float(k) * 0.3927; d1 = max(d1, texture2D(fCol, fCell(0.0, cuvE + vec2(cos(a) * 0.064, sin(a) * 0.072))).a); }\n    float hole = texture2D(fCol, fCell(0.0, cuvE)).a, rim = clamp(d1 - hole, 0.0, 1.0), sp = 0.0; // (the mask keeps the open eye's shape whatever the eye inside is doing)\n    for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16);\n      vec2 dw = normalize(vec2(sd, 0.5)); vec2 a = pc + dw * 0.2, b = a + dw * 0.3; sp = max(sp, fCone(fqe, a, b, 0.1, 0.003));\n      vec2 di = normalize(vec2(-sd, -0.75)); a = pc + di * 0.18; b = a + di * 0.19; sp = max(sp, fCone(fqe, a, b, 0.085, 0.003));\n      vec2 b0 = pc + vec2(sd * 0.2, 0.37), b1 = pc + vec2(-sd * 0.04, 0.3); sp = max(sp, fCone(fq, b0, b1, 0.042, 0.018)); }",
    "  if (sqd > 0.5) { float d1 = 0.0; for (int k = 0; k < 16; k++) { float a = float(k) * 0.3927; d1 = max(d1, texture2D(fCol, fCell(0.0, cuvE + vec2(cos(a) * 0.05, sin(a) * 0.052 + 0.026))).a); } // (one smooth outline, heavier over the top)\n    float hole = texture2D(fCol, fCell(0.0, cuvE)).a, rim = clamp(d1 - hole, 0.0, 1.0), sp = 0.0; // (the mask keeps the open eye's shape whatever the eye inside is doing)\n    for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 pc = vec2(sd * 0.4, 0.16);\n      vec2 dw = normalize(vec2(sd, 0.45)); vec2 a = pc + dw * 0.18, b = a + dw * 0.26; sp = max(sp, fCone(fqe, a, b, 0.1, 0.004)); // the one point, out and up at the outer corner\n      vec2 b0 = pc + vec2(sd * 0.02, 0.44), b1 = pc + vec2(sd * 0.3, 0.52); sp = max(sp, fCone(fq, b0, b1, 0.055, 0.01)); } // the brow: a leaf above, thick at the inner end, tapering out and up")
rep("ri = mix(0.165, 0.205, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.92 : 1.14, zmb), rp = mix(0.092, 0.1, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.5 : 0.78, zmb);",
    "ri = mix(0.165, 0.235, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.92 : 1.14, zmb), rp = mix(0.092, 0.11, sqd) * fPupil.z * mix(1.0, i == 0 ? 0.5 : 0.78, zmb);")
rep("    ic = mix(ic, vec3(0.02, 0.008, 0.014), sqd * smoothstep(ri - 0.045, ri - 0.012, r));", "    ic = mix(ic, vec3(0.02, 0.008, 0.014), sqd * smoothstep(ri - 0.032, ri - 0.012, r)); // (a dark ring round the big iris)")
rep("+ 0.8 * (1.0 - smoothstep(0.012, mix(0.02, 0.026, sqd), length(fqe - pc - vec2(0.05, -0.05) * (1.0 + 0.3 * sqd) * fPupil.z)));", "+ 0.8 * (1.0 - sqd) * (1.0 - smoothstep(0.012, mix(0.02, 0.026, sqd), length(fqe - pc - vec2(0.05, -0.05) * (1.0 + 0.3 * sqd) * fPupil.z))); // (one catchlight on the squid)")

m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
