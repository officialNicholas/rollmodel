#!/usr/bin/env python3
"""The results bar polished: each paint shaded top to bottom like a body of liquid, a wet crest along its surface, a darker rim where the two paints meet, a softer gloss and shadow, calmer waves, and a cleaner dark glass behind it. On top of ui79_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui79_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("function makeLiquid(host) {\n", "const liqShade = (hex, k) => { if (!/^#[0-9a-fA-F]{6}$/.test(hex)) return hex; const n = parseInt(hex.slice(1), 16), m = k > 0 ? 255 : 0, a = Math.abs(k), f = v => Math.round(v + (m - v) * a); return 'rgb(' + f(n >> 16 & 255) + ',' + f(n >> 8 & 255) + ',' + f(n & 255) + ')'; };\nfunction makeLiquid(host) {\n")
rep("surf = x => !L.surf ? 0 : h * (0.16 + 0.07 * Math.sin(x / w * 6.3 + t * 1.9 + sg.ph) + 0.04 * Math.sin(x / w * 13.1 - t * 2.7 + sg.ph * 2.0) + sl * 0.16 * Math.sin(x / w * 9.0 + t * 7.0));",
    "surf = x => !L.surf ? 0 : h * (0.13 + 0.045 * Math.sin(x / w * 6.3 + t * 1.9 + sg.ph) + 0.025 * Math.sin(x / w * 13.1 - t * 2.7 + sg.ph * 2.0) + sl * 0.12 * Math.sin(x / w * 9.0 + t * 7.0));")
rep("      g.closePath(); g.fillStyle = sg.col; g.fill();\n",
    r'''      g.closePath();
      if (L.surf) { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, liqShade(sg.col, 0.2)); gr.addColorStop(0.42, sg.col); gr.addColorStop(1, liqShade(sg.col, -0.32)); g.fillStyle = gr; } else g.fillStyle = sg.col; g.fill();
      if (L.surf) { // a darker rim where this paint meets the next, and a wet crest along its surface
        g.save(); g.clip(); g.lineWidth = 5; g.strokeStyle = 'rgba(0,0,0,.2)';
        for (const [x, a, ph] of [[sg.x0, a0, sg.ph], [sg.x1, a1, sg.ph + 1.3]]) if (a) { g.beginPath(); for (let i = 0; i <= N; i++) { const y = y0 + i / N * (h - y0), ex = edge(x, a, ph, y); i ? g.lineTo(ex, y) : g.moveTo(ex, y); } g.stroke(); }
        const xa = a1 ? edge(sg.x1, a1, sg.ph + 1.3, y0) : w + 6, xb = a0 ? edge(sg.x0, a0, sg.ph, y0) : -6; g.lineWidth = 2; g.strokeStyle = 'rgba(255,255,255,.5)'; g.beginPath(); for (let j = 0; j <= 24; j++) { const x = xb + (xa - xb) * j / 24, y = surf(x) + 1.4; j ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
        g.restore(); }
''')
rep("    g.fillStyle = 'rgba(255,255,255,.26)'; g.fillRect(0, h * 0.08, w, h * 0.22); g.fillStyle = 'rgba(255,255,255,.08)'; g.fillRect(0, h * 0.3, w, h * 0.2);\n    g.fillStyle = 'rgba(0,0,0,.16)'; g.fillRect(0, h * 0.8, w, h * 0.2);",
    "    { const sh = g.createLinearGradient(0, 0, 0, h); sh.addColorStop(0, 'rgba(255,255,255,0)'); sh.addColorStop(L.surf ? 0.2 : 0.1, L.surf ? 'rgba(255,255,255,.24)' : 'rgba(255,255,255,.26)'); sh.addColorStop(L.surf ? 0.48 : 0.42, 'rgba(255,255,255,0)'); sh.addColorStop(0.78, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(0,0,0,.2)'); g.fillStyle = sh; g.fillRect(0, 0, w, h); }")
css = '''
/* the results bar: dark glass behind the paint */
#end .jbar{background:#221B2E;box-shadow:3px 3px 0 var(--black),inset 0 3px 7px rgba(0,0,0,.55),inset 0 -1px 0 rgba(255,255,255,.06)}
#end .jbar::after{opacity:.55;top:2px;height:4px}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
