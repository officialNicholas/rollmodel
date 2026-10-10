#!/usr/bin/env python3
"""v187: anything you just bought is highlighted in the locker: its category tab and its tile glow gold with a NEW tag until you pick it."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui111_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# a purchase counts as new until you pick it in the locker
rep("BOUGHT.add(id); store.bought = [...BOUGHT]; save(); return true; }", "BOUGHT.add(id); store.bought = [...BOUGHT]; store.fresh = [...new Set([...(store.fresh || []), id])]; save(); return true; }")
# the eyes tab lights up for new eyes too, and the eye style tile carries the mark
rep("b.classList.toggle('fresh', WEAR.some(w => w.cat === c && bought(w.id) && fresh.has(w.id)));", "b.classList.toggle('fresh', ITEMS.some(w => w.cat === c && bought(w.id) && fresh.has(w.id)));")
rep("return '<button class=\"eyes' + (lk ? ' locked' : '') + '\" type=\"button\" data-es=\"' + k + '\"", "return '<button class=\"eyes' + (lk ? ' locked' : '') + (it && !lk && (store.fresh || []).includes(k) ? ' fresh' : '') + '\" type=\"button\" data-es=\"' + k + '\"")
rep("myLook.eyes = b.dataset.es; saveLook();", "myLook.eyes = b.dataset.es; if (store.fresh && store.fresh.includes(myLook.eyes)) store.fresh = store.fresh.filter(x => x !== myLook.eyes); saveLook();")
# the look: a gold ring and a NEW tag (after every other fresh rule, so it wins)
rep("\n</style>\n", """\n.lcat.fresh,.ltile.fresh,.eyes.fresh{box-shadow:0 0 0 3px var(--gold),0 0 16px 2px rgba(242,193,78,.6)!important;animation:lkfresh 1.5s ease-in-out infinite}
.lcat.fresh::after,.ltile.fresh::after,.eyes.fresh::after{content:"NEW"!important;position:absolute!important;top:-9px!important;right:-7px!important;left:auto!important;width:auto!important;height:auto!important;padding:3px 7px!important;border-radius:6px!important;border:0!important;background:var(--gold)!important;color:#171320!important;font:900 10px/1 var(--font-head)!important;letter-spacing:.08em;box-shadow:0 0 0 2px #171320!important;z-index:2;animation:none!important}
.eyes.fresh{position:relative}
@keyframes lkfresh{50%{box-shadow:0 0 0 3px var(--gold),0 0 26px 6px rgba(242,193,78,.85)}}
@media (prefers-reduced-motion:reduce){.lcat.fresh,.ltile.fresh,.eyes.fresh{animation:none}}
</style>
""")
rep('<p class="ver">Version 186</p>', '<p class="ver">Version 187</p>')
open(DST, 'w').write(s)
print('ui112 ok', n0, '->', len(s))
