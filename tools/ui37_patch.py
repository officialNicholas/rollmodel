#!/usr/bin/env python3
"""The locker sheet as an ink board: dark panel under the spotlight stage, cream type, glossy paint dabs, dark slot cards, framed tiles. On top of ui36_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui36_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
css = '''
/* ===== the locker as an ink board: a dark panel that belongs to the spotlight stage above it, cream type, your colour as the accent ===== */
.sheet.lookp{background:#1B1626 url(art/m_wall.webp) center top/cover no-repeat;color:#F4EEE3;box-shadow:0 -2px 0 #F4EEE3,0 -6px 0 rgba(23,19,32,.5),0 24px 48px rgba(6,2,16,.6)}
.sheet.lookp::before{display:none}
.lookp .ctitle{color:#F4EEE3;text-shadow:.04em .04em 0 var(--ink),.08em .08em 0 rgba(0,0,0,.5)}
.lkbal{background:#2A2338;color:#F4EEE3;box-shadow:0 0 0 2px rgba(244,238,227,.14),3px 4px 0 rgba(0,0,0,.35);font-weight:900}
.lnbtn{background:#F4EEE3;color:#17131F;box-shadow:3px 4px 0 rgba(0,0,0,.4)}
.lnbtn svg{color:#17131F}
/* the paint: glossy dabs, the chosen one on a cream ring */
.sw{width:50px;height:50px}
.sw i{width:42px;height:42px;filter:drop-shadow(1px 2px 0 rgba(0,0,0,.45))}
.sw i::after{content:"";position:absolute;left:30%;top:22%;width:26%;height:18%;border-radius:50%;background:rgba(255,255,255,.55);transform:rotate(-20deg)}
.sw[aria-pressed="true"]{transform:scale(1.22)}
.sw[aria-pressed="true"] i{filter:drop-shadow(0 0 0 #F4EEE3) drop-shadow(0 0 0 #F4EEE3) drop-shadow(1px 2px 0 rgba(0,0,0,.45))}
.sw[aria-pressed="true"]::after{background:#F4EEE3;width:7px;height:7px;bottom:-5px}
/* the eyes: cream chips, the chosen one in your colour */
.lookp .leyes .lhead,.lookp .lhead{color:rgba(244,238,227,.6);letter-spacing:.2em}
.eyes{background:#F4EEE3;box-shadow:2px 3px 0 rgba(0,0,0,.4)}
.eyec{box-shadow:2px 3px 0 rgba(0,0,0,.4)}
.eyes[aria-pressed="true"]{box-shadow:0 0 0 2.5px var(--ink),2px 3px 0 rgba(0,0,0,.45)}
.eyec{border-color:#F4EEE3}
.eyec[aria-pressed="true"]{border-color:var(--ink)}
.irises.off{opacity:.3}
/* the slot cards: dark plates, cream type; the open one in your colour with a cream rim */
.seg.lcats button,.seg.lcats button[aria-selected="true"]{background:#2A2338;color:#F4EEE3;box-shadow:0 0 0 2px rgba(244,238,227,.1),3px 4px 0 rgba(0,0,0,.4);border-radius:5px}
.seg.lcats button small{color:rgba(244,238,227,.55)}
.seg.lcats button .lci svg{filter:drop-shadow(0 1px 0 rgba(0,0,0,.3))}
.seg.lcats button[aria-selected="true"]{background:var(--ink);color:#fff;box-shadow:0 0 0 2.5px #F4EEE3,3px 4px 0 rgba(0,0,0,.45);transform:translateY(-2px)}
.seg.lcats button[aria-selected="true"] small{color:rgba(255,255,255,.8)}
.lcat.fresh::after{background:#F4EEE3;box-shadow:0 0 0 2.5px #1B1626}
/* the tiles: cream, framed, on a hard shadow; the worn one rimmed in your colour; locked ones sunk into the board */
.ltile{background:#F7F2E9;box-shadow:0 0 0 2px rgba(244,238,227,.12),3px 4px 0 rgba(0,0,0,.4);border-radius:5px}
.ltile[aria-pressed="true"]{background:#F7F2E9;box-shadow:0 0 0 2.5px var(--ink),3px 4px 0 rgba(0,0,0,.45);transform:translateY(-3px)}
.ltile.locked{background:rgba(244,238,227,.07);border:2px dashed rgba(244,238,227,.25);box-shadow:none}
.ltile.locked .ltn{color:rgba(244,238,227,.5)}
.ltile.locked .lk{background:#F4EEE3;color:#17131F}
.ltile.sale{border:0;background:#F7F2E9;box-shadow:0 0 0 2px var(--ink),3px 4px 0 rgba(0,0,0,.4)}
.ltile .ltag{background:#F4EEE3;color:#17131F;box-shadow:2px 2px 0 rgba(0,0,0,.4)}
.ltile .ltag .dropi{filter:none}
.ltile.broke .ltag{background:#8E8698;color:#fff}
.ltn{color:#2A2437}
.lrail.more::after{background:linear-gradient(90deg,rgba(27,22,38,0),#1B1626)}
/* the code line */
.ulink{color:rgba(244,238,227,.6)}
.uform input{background:#F4EEE3;color:#17131F}
.lnote{background:#F4EEE3;color:#17131F}
@media (max-height:520px) and (min-aspect-ratio:1/1){.sw{width:40px;height:40px}.sw i{width:33px;height:33px}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]
rep('<p class="ver">Version 106</p>', '<p class="ver">Version 107</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
