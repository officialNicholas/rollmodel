#!/usr/bin/env python3
"""The settings panel's paint wash drifts: the splats and drips on the orange panel scroll slowly upward without end, on the compositor (a tall tile moved by transform behind the panel's slant), so it costs nothing per frame. On top of ui86_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui86_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<div class="card" role="dialog" aria-modal="true" aria-labelledby="setTitle">', '<div class="card" role="dialog" aria-modal="true" aria-labelledby="setTitle"><i class="swash" aria-hidden="true"><i></i></i>')
css = '''
/* the settings panel's wash drifts upward without end */
#setModal .card::after{display:none}
#setModal .swash{position:absolute;inset:0;clip-path:polygon(66% 0,100% 0,100% 100%,50% 100%);overflow:hidden;pointer-events:none;z-index:0}
#setModal .swash i{position:absolute;left:0;right:0;top:0;height:calc(100% + 1440px);background:rgba(23,19,32,.28);-webkit-mask:url(art/m_splat2.webp) 10px 20px/96px 96px repeat,url(art/m_splat.webp) 70px 90px/120px 120px repeat,url(art/m_drip.webp) 40px -10px/70px 90px repeat;mask:url(art/m_splat2.webp) 10px 20px/96px 96px repeat,url(art/m_splat.webp) 70px 90px/120px 120px repeat,url(art/m_drip.webp) 40px -10px/70px 90px repeat;will-change:transform;animation:swashdrift 72s linear infinite}
@keyframes swashdrift{from{transform:translateY(0)}to{transform:translateY(-1440px)}}
#setModal .card>*:not(.swash){position:relative;z-index:1}
@media (prefers-reduced-motion:reduce){#setModal .swash i{animation:none}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
