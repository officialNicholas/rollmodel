#!/usr/bin/env python3
"""v205: the pound and item buttons draw properly on iPhones. Their disc was the sticker used as a mask over a colour with a
luminosity blend, and the icon sat on it in its own layer (a drop shadow, and see-through while the pound recharges). Safari
punched a hole through the disc wherever the icon was, so the game behind showed through the middle of the button (a red square
round the arrow, over a paint trail). The discs are now plain pictures with the shadow baked in (tools/bake_buttons.py), and
neither button uses a mask, a blend or a filter."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui129_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("\n</style>\n", """
/* the round in-match buttons are plain pictures (tools/bake_buttons.py): on iPhones Safari punched a hole in the masked, colour-blended disc wherever the icon sat on it */
.slamBtn,.slamBtn:active,.slamBtn.off,.slamBtn.boost,.slamBtn.locked,.itemBtn{filter:none}
.slamBtn.locked{opacity:.35}
.slamBtn .sdisc,.itemBtn .sdisc{inset:0 -4px -6px 0;border-radius:0;background:url(art/sd_red.webp) 0 0/100% 100% no-repeat;background-blend-mode:normal;-webkit-mask:none;mask:none;transition:none;filter:none}
.slamBtn.off .sdisc{background-image:url(art/sd_off.webp);filter:none}
.slamBtn.boost .sdisc{background:url(art/sd_boost.webp) 0 0/100% 100% no-repeat}
.slamBtn.boost.off .sdisc{background-image:url(art/sd_boostoff.webp)}
.slamBtn.locked .sdisc{background-image:url(art/sd_grey.webp)}
.itemBtn .sdisc{background-image:url(art/sd_cream.webp)}
.slamBtn svg,.itemBtn svg{filter:none}
.itemBtn.in{animation:slamin .4s cubic-bezier(.3,1.7,.5,1)}
.itemBtn::before{content:"";position:absolute;inset:0;border-radius:50%;box-shadow:0 0 12px rgba(var(--ink-rgb),.8);opacity:0;pointer-events:none}
.itemBtn.in::before{animation:itemglow2 1.6s ease-in-out .4s infinite}
@keyframes itemglow2{50%{opacity:1}}
@media (prefers-reduced-motion:reduce){.itemBtn.in::before{animation:none}}
</style>
""")
rep('<p class="ver">Version 204</p>', '<p class="ver">Version 205</p>')
open(DST, 'w').write(s)
print('ui130 ok', n0, '->', len(s))
