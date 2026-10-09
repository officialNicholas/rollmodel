#!/usr/bin/env python3
"""The pound button wears your ink: the sticker is tinted with the current colour, and its cooldown dims it instead of going grey. On top of ui34_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui34_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the disc is its own layer inside the button: the sticker's shading laid over your ink, cut to the sticker's shape
rep('<button class="slamBtn" id="slamBtn" type="button" aria-label="Ground pound" hidden><svg viewBox="0 0 40 40" aria-hidden="true">',
    '<button class="slamBtn" id="slamBtn" type="button" aria-label="Ground pound" hidden><i class="sdisc" aria-hidden="true"></i><svg viewBox="0 0 40 40" aria-hidden="true">')
css = '''
/* the pound button in your ink: the sticker's light and curl over the colour, dimmed on cooldown rather than greyed */
.slamBtn,.slamBtn.off,.slamBtn.boost{background:none}
.slamBtn .sdisc{position:absolute;inset:0;border-radius:50%;background:url(art/m_dot.webp) center/100% 100% no-repeat,var(--ink);background-blend-mode:luminosity;-webkit-mask:url(art/m_dot.webp) center/100% 100% no-repeat;mask:url(art/m_dot.webp) center/100% 100% no-repeat;transition:filter .25s}
.slamBtn svg{position:relative;z-index:1}
.slamBtn::after{z-index:1}
.slamBtn.off{filter:drop-shadow(4px 6px 0 rgba(23,19,32,.3))}
.slamBtn.off .sdisc{filter:brightness(.5) saturate(.55)}
.slamBtn.boost{filter:drop-shadow(4px 6px 0 rgba(23,19,32,.3))}
.slamBtn.boost .sdisc{background:url(art/m_dot.webp) center/100% 100% no-repeat,#FF7A1F}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]
rep('<p class="ver">Version 104</p>', '<p class="ver">Version 105</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
