#!/usr/bin/env python3
"""v217: Choose Event shows there's more below. While the list runs on past the bottom of the screen its last card fades softly into the
page and a small arrow bobs at the bottom (a tap scrolls on); scrolled down, the top edge fades too; at the end both go."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui144_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<div class="evgrid" id="evGrid" role="group" aria-labelledby="evTitle">',
    '<button class="evmore" id="evMore" type="button" aria-label="More events below" tabindex="-1"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9.5l6 6 6-6" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></button>'
    '<div class="evgrid" id="evGrid" role="group" aria-labelledby="evTitle">')
CSS = """
/* Choose Event: more below (the list fades into the page at the bottom, an arrow bobs), scrolled (the top fades) */
.evgrid.more-b{-webkit-mask-image:linear-gradient(180deg,#000 calc(100% - 84px),rgba(0,0,0,.06));mask-image:linear-gradient(180deg,#000 calc(100% - 84px),rgba(0,0,0,.06))}
.evgrid.more-t{-webkit-mask-image:linear-gradient(180deg,rgba(0,0,0,.08),#000 28px);mask-image:linear-gradient(180deg,rgba(0,0,0,.08),#000 28px)}
.evgrid.more-t.more-b{-webkit-mask-image:linear-gradient(180deg,rgba(0,0,0,.08),#000 28px,#000 calc(100% - 84px),rgba(0,0,0,.06));mask-image:linear-gradient(180deg,rgba(0,0,0,.08),#000 28px,#000 calc(100% - 84px),rgba(0,0,0,.06))}
.evmore{appearance:none;position:absolute;left:50%;bottom:calc(max(10px,env(safe-area-inset-bottom,0px)) + 6px);z-index:3;display:grid;place-items:center;width:40px;height:40px;margin:0 0 0 -20px;padding:0;border:0;border-radius:50%;background:rgba(23,19,32,.72);box-shadow:0 0 0 2px rgba(255,255,255,.2),0 4px 12px rgba(0,0,0,.4);color:#fff;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .25s;animation:evmore 1.7s ease-in-out infinite;-webkit-tap-highlight-color:transparent}
.evmore.on{opacity:.9;pointer-events:auto}
.evmore svg{width:20px;height:20px}
@keyframes evmore{0%,100%{transform:translateY(0)}50%{transform:translateY(5px)}}
@media (prefers-reduced-motion:reduce){.evmore{animation:none}}
"""
rep("/* abilities: violet construction paper", CSS.lstrip('\n') + "/* abilities: violet construction paper")
JS = """
// Choose Event: a soft fade and a bobbing arrow at the bottom while there's more of the list to scroll to, a fade at the top once scrolled
function evMoreTick() { const g = $('evGrid'), below = g.scrollHeight - g.scrollTop - g.clientHeight > 8, above = g.scrollTop > 4; g.classList.toggle('more-b', below); g.classList.toggle('more-t', above); $('evMore').classList.toggle('on', below); }
$('evGrid').addEventListener('scroll', evMoreTick, { passive: true });
addEventListener('resize', () => { if (menuPage === 'events') evMoreTick(); });
if (window.ResizeObserver) { const ro = new ResizeObserver(() => { if (menuPage === 'events') evMoreTick(); }); for (const c of $('evGrid').children) ro.observe(c); }
$('evMore').addEventListener('click', () => { AU.init(); AU.ui(); const g = $('evGrid'); g.scrollBy({ top: g.clientHeight * 0.7, behavior: reduceMotion ? 'auto' : 'smooth' }); });
"""
rep("evArt(); evFold();", "evArt(); evFold(); requestAnimationFrame(evMoreTick);")
rep("$('lkShop').addEventListener('click', () => { AU.init(); AU.ui(); openShop('look'); });",
    "$('lkShop').addEventListener('click', () => { AU.init(); AU.ui(); openShop('look'); });" + JS.rstrip('\n'))
rep('<p class="ver">Version 216</p>', '<p class="ver">Version 217</p>')
open(DST, 'w').write(s)
print('ui145 ok', n0, '->', len(s))
