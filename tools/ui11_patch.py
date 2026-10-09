#!/usr/bin/env python3
"""Settings in the ARMS layout: stacked bars on the dark left, the live one in your ink, a splat-patterned ink panel cutting in on the right. On top of ui10_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui10_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = '''
/* ===== settings: the dark board, bars that run off the left, the ink field cutting in on the right ===== */
#setModal{padding:0;background:#17131F;backdrop-filter:none;-webkit-backdrop-filter:none;place-items:stretch}
#setModal .card{position:relative;width:auto;max-width:none;max-height:none;height:100%;margin:0;padding:0;border:0;border-radius:0;background:#17131F;box-shadow:none;display:block;overflow:hidden;animation:fadein .2s ease-out}
#setModal .card::before{content:"";display:block;opacity:1;position:absolute;inset:0;width:auto;height:auto;margin:0;border:0;border-radius:0;transform:none;box-shadow:none;background:var(--ink);clip-path:polygon(80% 0,100% 0,100% 100%,56% 100%)}
#setModal .card::after{content:"";position:absolute;inset:0;width:auto;height:auto;margin:0;border:0;border-radius:0;transform:none;box-shadow:none;clip-path:polygon(80% 0,100% 0,100% 100%,56% 100%);background:rgba(23,19,32,.28);-webkit-mask:url(art/m_splat2.webp) 10px 20px/96px 96px repeat,url(art/m_splat.webp) 70px 90px/120px 120px repeat,url(art/m_drip.webp) 40px -10px/70px 90px repeat;mask:url(art/m_splat2.webp) 10px 20px/96px 96px repeat,url(art/m_splat.webp) 70px 90px/120px 120px repeat,url(art/m_drip.webp) 40px -10px/70px 90px repeat;pointer-events:none}
#setModal .ctitle{position:absolute;left:22px;top:max(16px,env(safe-area-inset-top));margin:0;z-index:2;font:900 44px/1 var(--font-head);font-style:italic;text-transform:uppercase;color:#fff;text-shadow:.06em .06em 0 rgba(0,0,0,.6),0 0 0 var(--black)}
.srows{position:absolute;left:0;right:7%;top:max(84px,calc(env(safe-area-inset-top) + 70px));bottom:max(90px,calc(env(safe-area-inset-bottom) + 76px));z-index:2;display:grid;align-content:start;gap:12px}
.sgrp{display:grid;grid-template-columns:auto minmax(0,1fr);align-items:center;gap:6px 10px;margin-left:-16px;padding:11px 14px 11px 32px;background:#241E2E;color:#fff;border-radius:0 6px 6px 0;transform:skewX(-9deg);transition:background .2s}
.sgrp>*{transform:skewX(9deg)}
.sgrp .lhead{margin:0;justify-content:start;white-space:nowrap;font:900 21px/1 var(--font-head);font-style:italic;letter-spacing:0;text-transform:uppercase;color:#fff}
.sgrp.on{background:var(--ink);box-shadow:4px 4px 0 rgba(0,0,0,.4)}
.sgrp .gnote{grid-column:1/-1;margin:0;font:700 11px/1.3 var(--font-ui);color:rgba(255,255,255,.72);text-align:left}
.sgrp .seg{background:none;box-shadow:none;border:0;padding:0;gap:5px;justify-self:end}
.sgrp .seg button{min-height:34px;padding:6px 9px;font-size:12px;border-radius:0;background:url(art/m_tape3.webp) center/100% 100% no-repeat;color:#2A2437;transform:rotate(-1deg)}
.sgrp .seg button:nth-child(2){transform:rotate(1deg)}
.sgrp .seg button[aria-pressed="true"]{color:var(--ink);text-shadow:none;box-shadow:none}
.sgrp.on .seg button[aria-pressed="true"]{color:var(--black);background-color:#fff;box-shadow:0 0 0 2px var(--black)}
.sgrp .seg button svg{width:16px;height:16px}
#setModal #setDone{position:absolute;right:16px;bottom:max(16px,env(safe-area-inset-bottom));z-index:3;width:auto;min-width:150px;margin:0;filter:drop-shadow(0 0 0 #fff) drop-shadow(2px 2px 0 #F4EEE3) drop-shadow(-2px -2px 0 #F4EEE3)}
@media (min-aspect-ratio:1/1){#setModal .card::before,#setModal .card::after{clip-path:polygon(66% 0,100% 0,100% 100%,50% 100%)}.srows{right:44%;top:max(70px,calc(env(safe-area-inset-top) + 58px));bottom:max(70px,calc(env(safe-area-inset-bottom) + 60px));gap:8px;left:max(0px,env(safe-area-inset-left))}#setModal .ctitle{font-size:34px;left:max(22px,calc(env(safe-area-inset-left) + 16px))}.sgrp{padding:8px 12px 8px 34px}.sgrp .lhead{font-size:18px}#setModal #setDone{right:max(16px,calc(env(safe-area-inset-right) + 12px))}}
@media (max-height:520px) and (min-aspect-ratio:1/1){.sgrp .seg button{min-height:30px;padding:4px 8px;font-size:11px}.sgrp .gnote{font-size:10px}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]

rep('''      <h2 class="ctitle" id="setTitle">Settings</h2>
      <div class="sgrp">''', '''      <h2 class="ctitle" id="setTitle">Settings</h2>
      <div class="srows" id="srows">
      <div class="sgrp on">''')
rep('''        <p class="gnote" id="gfxNote" aria-live="polite"></p>
      </div>
      <button class="btn play sm" id="setDone" type="button">Done</button>''', '''        <p class="gnote" id="gfxNote" aria-live="polite"></p>
      </div>
      </div>
      <button class="btn play sm" id="setDone" type="button">Done</button>''')
# the bar you touch lights up in your ink
rep("$('setDone').addEventListener('click'", "$('srows').addEventListener('pointerdown', e => { const g = e.target.closest('.sgrp'); if (!g) return; for (const x of $('srows').children) x.classList.toggle('on', x === g); });\n$('setDone').addEventListener('click'")
rep('<p class="ver">Version 80</p>', '<p class="ver">Version 81</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
