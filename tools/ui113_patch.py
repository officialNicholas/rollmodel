#!/usr/bin/env python3
"""v188: no focus ring drawn while you play by touch (it showed as a black box round the Select button), and the orientation chooser
gets cleaner spacing: the card tape clears the text above, both cards are the same height with their labels lined up, and the button
has room under the cards."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui112_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("const touchy = () => matchMedia('(pointer: coarse)').matches;",
    "const touchy = () => matchMedia('(pointer: coarse)').matches;\n"
    "/* focus rings are for keyboards: while you play by touch none is drawn (a phone showed one as a black box round a focused button) */\n"
    "{ const R = document.documentElement; if (touchy()) R.classList.add('touchnav'); addEventListener('pointerdown', e => { if (e.pointerType !== 'mouse') R.classList.add('touchnav'); }, true); addEventListener('keydown', e => { if (e.key === 'Tab' || e.key.startsWith('Arrow')) R.classList.remove('touchnav'); }, true); }")
rep("\n</style>\n", """
html.touchnav :focus-visible{outline:none!important}
.orient .obody{gap:18px}
.orient .ocards{margin-top:12px;align-items:stretch}
.orient .ocard{grid-template-rows:1fr auto auto;align-content:stretch}
.orient .ocard .oart{align-self:center}
.orient #orientOk{margin-top:4px}
@media (min-aspect-ratio:1/1) and (max-height:520px){.orient .obody{gap:12px}.orient .ocards{margin-top:14px;width:min(100%,520px)}.orient #orientOk{margin-top:0}}
</style>
""")
rep('<p class="ver">Version 187</p>', '<p class="ver">Version 188</p>')
open(DST, 'w').write(s)
print('ui113 ok', n0, '->', len(s))
