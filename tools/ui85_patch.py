#!/usr/bin/env python3
"""Two things. The pound dial tells the truth: while you lack the paint for a pound it shows a drop and fills with your paint, and only once you have enough does it count the cooldown down. And the shop slides up over the locker and slides back down, instead of cutting. On top of ui84_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui84_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the dial: no paint, no countdown
rep("      else if (P.slamCD > 0 && P.slamMax > 0) { frac = 1 - P.slamCD / P.slamMax; n = Math.ceil(P.slamCD); kind = 'cd'; }",
    "      else if (P.paint < POUND_MIN && !P.slam) { frac = Math.min(1, P.paint / POUND_MIN); n = ''; kind = 'paint'; } // (short of paint: the dial fills with your paint, a drop in it, no count)\n      else if (P.slamCD > 0 && P.slamMax > 0) { frac = 1 - P.slamCD / P.slamMax; n = Math.ceil(P.slamCD); kind = 'cd'; }")
rep("const ns = String(n); if ($('ptN').textContent !== ns) $('ptN').textContent = ns;",
    "const ns = kind === 'paint' ? '<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M12 2.5C9.2 7.2 6.4 10.6 6.4 14.1a5.6 5.6 0 0 0 11.2 0c0-3.5-2.8-6.9-5.6-11.6z\"/></svg>' : String(n); if ($('ptN').dataset.v !== ns) { $('ptN').dataset.v = ns; $('ptN').innerHTML = ns; }")
# the shop slides in over the locker and back out
rep("  renderShop(); $('shop').hidden = false; menu.classList.add('shopping'); AU.music('shop');",
    "  renderShop(); const sh = $('shop'); if (sh._outT) { clearTimeout(sh._outT); sh._outT = 0; } sh.classList.remove('out'); sh.hidden = false; menu.classList.add('shopping'); AU.music('shop');")
rep("  if (!shopOpen) return; shopOpen = false; $('shop').hidden = true; menu.classList.remove('shopping'); $('shopNote').classList.remove('on');",
    "  if (!shopOpen) return; shopOpen = false; { const sh = $('shop'); if (quiet || reduceMotion) sh.hidden = true; else { sh.classList.add('out'); sh._outT = setTimeout(() => { sh._outT = 0; if (!shopOpen) { sh.hidden = true; sh.classList.remove('out'); } }, 240); } } menu.classList.remove('shopping'); $('shopNote').classList.remove('on');")
css = '''
/* the dial short of paint */
.ptimer[data-k="paint"]{--pc:#CFC6E0}
.ptimer[data-k="paint"] b svg{width:16px;height:16px;fill:#fff;filter:drop-shadow(0 1.5px 0 var(--black))}
/* the shop slides up over the locker, and back down */
.shop{animation:shopin .34s cubic-bezier(.2,1.1,.35,1) both}
@keyframes shopin{from{opacity:0;transform:translateY(28px) scale(.985)}}
.shop.out{animation:shopout .22s cubic-bezier(.4,0,.7,1) both;pointer-events:none}
@keyframes shopout{to{opacity:0;transform:translateY(24px) scale(.985)}}
.menu.shopping .mhome{visibility:visible;transition:opacity .25s;opacity:0;pointer-events:none}
@media (prefers-reduced-motion:reduce){.shop,.shop.out{animation:none}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
