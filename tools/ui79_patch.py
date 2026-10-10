#!/usr/bin/env python3
"""The lobby speech bubble as a comic bubble: a fat rounded white bubble with the UI's ink outline and hard shadow, a curved tail that grows out of it in one piece (no seam), a bolder line of text, and a pop in that lands with a little bounce. On top of ui78_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui78_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
tail = open('/tmp/tail_svg.txt').read()
css = '''
/* the speech bubble: a comic bubble with its tail grown out of it */
.lsay{max-width:min(64vw,240px);padding:11px 16px 12px;background:#fff;border:2.5px solid var(--black);border-radius:20px;box-shadow:4px 4px 0 var(--black);font:800 15px/1.25 var(--font-ui);color:var(--black);letter-spacing:.005em;transform-origin:var(--tx,18px) 100%}
.lsay::after{content:"";position:absolute;left:calc(var(--tx,18px) + 2px);bottom:-30px;width:38px;height:36px;border:0;background:''' + tail + ''' 0 0/38px 36px no-repeat;box-shadow:none;transform:none}
.lsay.flip{transform-origin:calc(var(--tx,18px) + 18px) 100%}
.lsay.flip::after{left:calc(var(--tx,18px) - 16px);transform:scaleX(-1)}
@keyframes sayin{0%{opacity:0;transform:translate(0,-100%) scale(.4)}60%{opacity:1;transform:translate(0,-100%) scale(1.08)}100%{opacity:1;transform:translate(0,-100%) scale(1)}}
@keyframes sayinf{0%{opacity:0;transform:translate(0,-100%) scale(.4)}60%{opacity:1;transform:translate(0,-100%) scale(1.08)}100%{opacity:1;transform:translate(0,-100%) scale(1)}}
.lsay{animation:sayin .42s cubic-bezier(.2,1.2,.4,1) both}
.lsay.flip{animation-name:sayinf}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
