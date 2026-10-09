#!/usr/bin/env python3
"""The winner screen's ribbon is a CSS band: a sharp cream edge, the settings board's splat pattern on a dark field. On top of ui39_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui39_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the shader loses its ribbon
a = s.index("  // the ribbon: a dark stripe across the lower part, its edges torn"); b = s.index("  col *= 1.0 - 0.3 * smoothstep(0.75, 1.6, length(p));", a)
s = s[:a] + s[b:]
# the band is an element behind the winner screen's content
rep('<section class="victory" id="victory" hidden aria-live="polite">\n', '<section class="victory" id="victory" hidden aria-live="polite">\n    <div class="vrib" aria-hidden="true"></div>\n')
rep("vicEl.style.setProperty('--vc', hexCss(TEAMS[lead.team].wet));", "vicEl.style.setProperty('--vc', hexCss(TEAMS[lead.team].wet)); vicEl.style.setProperty('--vrib', '#' + new THREE.Color(TEAMS[lead.team].wet).multiplyScalar(0.3).lerp(new THREE.Color(0x120B1A), 0.7).getHexString());")
css = '''
/* the ribbon under the winner: a dark band on a slant with a sharp cream edge, the settings board's splats on it */
.victory{isolation:isolate}
.vrib{position:absolute;left:-12%;width:124%;bottom:-16%;height:50%;z-index:-1;transform:rotate(-5deg);transform-origin:50% 50%;background:var(--vrib,#2B1232);border-top:7px solid #F4EEE3;box-shadow:0 -4px 0 rgba(0,0,0,.25);animation:vribin .5s .1s cubic-bezier(.2,1.1,.3,1) both}
.vrib::after{content:"";position:absolute;inset:0;background:rgba(255,255,255,.07);-webkit-mask:url(art/m_splat2.webp) 10px 20px/96px 96px repeat,url(art/m_splat.webp) 70px 90px/120px 120px repeat,url(art/m_drip.webp) 40px -10px/70px 90px repeat;mask:url(art/m_splat2.webp) 10px 20px/96px 96px repeat,url(art/m_splat.webp) 70px 90px/120px 120px repeat,url(art/m_drip.webp) 40px -10px/70px 90px repeat;animation:vribdrift 14s linear infinite}
@keyframes vribin{from{transform:rotate(-5deg) translateY(60%)}}
@keyframes vribdrift{to{-webkit-mask-position:106px 20px,166px 90px,110px -10px;mask-position:106px 20px,166px 90px,110px -10px}}
@media (min-aspect-ratio:1/1){.vrib{height:46%;bottom:-20%;transform:rotate(-3.5deg)}}
@media (prefers-reduced-motion:reduce){.vrib,.vrib::after{animation:none}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]
rep('<p class="ver">Version 109</p>', '<p class="ver">Version 110</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
