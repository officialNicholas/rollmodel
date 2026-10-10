#!/usr/bin/env python3
"""The loading bar's paint sits in the bar on every phone: the canvas measures the bar against its own box instead of the window, so the notch's safe-area padding no longer pushes the paint below the bar. On top of ui73_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui73_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("const size = () => { dpr = Math.min(2, window.devicePixelRatio || 1); W = innerWidth; H = innerHeight; c.width = W * dpr | 0; c.height = H * dpr | 0; c.style.width = W + 'px'; c.style.height = H + 'px'; };",
    "const size = () => { dpr = Math.min(2, window.devicePixelRatio || 1); W = c.clientWidth || innerWidth; H = c.clientHeight || innerHeight; c.width = W * dpr | 0; c.height = H * dpr | 0; };")
rep("const r = bar ? bar.getBoundingClientRect() : { left: W * 0.2, top: H * 0.6, width: W * 0.6, height: 44 }, L = r.left + 3,",
    "if (c.clientWidth && (c.clientWidth !== W || c.clientHeight !== H)) size(); const cr = c.getBoundingClientRect(), rb = bar ? bar.getBoundingClientRect() : null, r = rb ? { left: rb.left - cr.left, top: rb.top - cr.top, width: rb.width, height: rb.height } : { left: W * 0.2, top: H * 0.6, width: W * 0.6, height: 44 }, L = r.left + 3,")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
