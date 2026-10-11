#!/usr/bin/env python3
"""v225: the onboarding never darkens or blurs the locker or the shop. There the tip's surround stays clear (you see your character change
and everything on the shelves), only the control it asks for takes a tap, and that control is ringed in a soft pulsing gold instead."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui152_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep(".tutdim.on.noblur>b{-webkit-backdrop-filter:none;backdrop-filter:none}",
    ".tutdim.on.noblur>b{-webkit-backdrop-filter:none;backdrop-filter:none}\n"
    "/* the locker and the shop: nothing darkened or blurred (you watch your character change, you see the shelves); the control asked for, ringed in gold */\n"
    ".tutdim.on.clear>b{background:transparent;-webkit-backdrop-filter:none;backdrop-filter:none}\n"
    ".tutdim::after{content:'';position:absolute;left:var(--wx,0);top:var(--wy,0);width:var(--ww,0);height:var(--wh,0);border-radius:14px;opacity:0;pointer-events:none;box-shadow:0 0 0 3px var(--gold),0 0 0 6px rgba(242,193,78,.35),0 0 22px rgba(242,193,78,.65);transition:opacity .2s}\n"
    ".tutdim.on.clear:not(.nowin)::after{opacity:1;animation:tutring 1.3s ease-in-out infinite}\n"
    "@keyframes tutring{0%,100%{transform:scale(1)}50%{transform:scale(1.04)}}\n"
    "@media (prefers-reduced-motion:reduce){.tutdim.on.clear::after{animation:none}}")
rep("  l.style.top = r.style.top = y0 + 'px'; l.style.height = r.style.height = none ? '0px' : Math.max(0, y1 - y0) + 'px'; l.style.width = Math.max(0, x0) + 'px'; r.style.left = x1 + 'px'; }",
    "  l.style.top = r.style.top = y0 + 'px'; l.style.height = r.style.height = none ? '0px' : Math.max(0, y1 - y0) + 'px'; l.style.width = Math.max(0, x0) + 'px'; r.style.left = x1 + 'px';\n"
    "  tutDim.classList.toggle('nowin', none); if (!none) { tutDim.style.setProperty('--wx', x0 + 'px'); tutDim.style.setProperty('--wy', y0 + 'px'); tutDim.style.setProperty('--ww', (x1 - x0) + 'px'); tutDim.style.setProperty('--wh', (y1 - y0) + 'px'); } }")
rep("  { const nb = shopOpen || lookOpen; if (tutDim.classList.contains('noblur') !== nb) tutDim.classList.toggle('noblur', nb); } // (in the shop and the locker the dim alone, no blur)",
    "  { const nb = shopOpen || lookOpen; if (tutDim.classList.contains('noblur') !== nb) tutDim.classList.toggle('noblur', nb); if (tutDim.classList.contains('clear') !== nb) tutDim.classList.toggle('clear', nb); } // (in the shop and the locker: no dim, no blur, the control ringed)")
rep('<p class="ver">Version 224</p>', '<p class="ver">Version 225</p>')
open(DST, 'w').write(s)
print('ui153 ok', n0, '->', len(s))
