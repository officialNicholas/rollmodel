#!/usr/bin/env python3
"""The Paint Shop no longer pans sideways: the grid can only scroll up and down, its columns can never grow past the screen, and every card's text wraps inside its card. On top of ui83_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui83_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
css = '''
/* the shop scrolls one way only: nothing can push the columns past the screen */
.shop{overflow:hidden}
.shgrid{overflow-x:hidden;overflow-y:auto;grid-template-columns:repeat(auto-fill,minmax(min(148px,100%),minmax(0,1fr)));margin:0;padding-left:0;padding-right:0}
.shitem,.shin,.shpic,.shplate{min-width:0;max-width:100%;box-sizing:border-box}
.shplate{grid-template-columns:minmax(0,1fr)}
.shn,.shw{max-width:100%;overflow-wrap:anywhere;text-wrap:balance}
.shp{max-width:100%;white-space:nowrap}
@media (max-height:520px) and (min-aspect-ratio:1/1){.shgrid{grid-template-columns:repeat(auto-fill,minmax(min(118px,100%),minmax(0,1fr)))}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
