#!/usr/bin/env python3
"""The orb's arrival no longer stalls the frame. Its screen-edge flash animated a full-screen blurred inset box-shadow through five colours for 1.8 s, which the browser had to repaint every frame; it is now five static edge-glow layers, one per colour, that only fade (opacity, composited). On top of ui69_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui69_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<div class="orbflash" id="orbFlash">', '<div class="orbflash" id="orbFlash"><i></i><i></i><i></i><i></i><i></i>')
a = s.index('@keyframes orbflash{'); b = s.index('}}', a) + 2
s = s[:a] + '@keyframes orbflash{0%{opacity:1}100%{opacity:0}}' + s[b:]
def glow(c): return 'linear-gradient(to right,' + c + ' 0,rgba(0,0,0,0) 16%,rgba(0,0,0,0) 84%,' + c + ' 100%),linear-gradient(to bottom,' + c + ' 0,rgba(0,0,0,0) 12%,rgba(0,0,0,0) 88%,' + c + ' 100%)'
cols = ['#FF4D6D', '#FFD23F', '#4DA6FF', '#C77DFF', '#4DFFB8']
css = '\n/* the orb\'s flash: five edge glows, one per colour, that only fade (a blurred inset shadow animated across the whole screen was a repaint every frame) */\n.orbflash{opacity:1;will-change:opacity}\n.orbflash i{position:absolute;inset:0;opacity:0;will-change:opacity}\n'
for k, c in enumerate(cols): css += '.orbflash i:nth-child(' + str(k + 1) + '){background:' + glow(c) + '}\n'
# each colour takes its turn: a peak a quarter of the way after the last, the first full on at the start, all gone by the end
peaks = [[(0, 1), (25, 0)], [(0, 0), (25, .9), (50, 0)], [(25, 0), (50, .75), (75, 0)], [(50, 0), (75, .5), (100, 0)], [(75, 0), (100, 0)]]
for k, pk in enumerate(peaks):
    css += '@keyframes orbf' + str(k + 1) + '{' + ''.join('%d%%{opacity:%s}' % (p, str(o).lstrip('0') or '0') for p, o in pk) + '}\n'
    css += '.orbflash.on i:nth-child(' + str(k + 1) + '){animation:orbf' + str(k + 1) + ' 1.8s ease-out}\n'
css += '@media (prefers-reduced-motion:reduce){.orbflash.on i{animation:none}}\n'
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
