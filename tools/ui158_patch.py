#!/usr/bin/env python3
"""v226: the onboarding's shop and locker tips keep what they point at in reach. Turned sideways and back (the shop laid out again in more
columns and kept its scroll), the flower the tip pointed at had gone off the bottom of the screen, and with every other tap held back by
the tip there was no way to scroll back to it. Now, whenever the card or tile the tip is about is mostly out of its own scroller, it is
brought back to the middle of it (and after a turn of the phone too)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui157_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("  const vis = el && !el.closest('[hidden]') && el.getClientRects().length > 0;\n  if (!vis) { if (tutEl.dataset.pos !== 'top')",
    "  const vis = el && !el.closest('[hidden]') && el.getClientRects().length > 0;\n"
    "  if (vis && block) { const sc = el.closest('.shgrid, .lrail'); if (sc) { const a = el.getBoundingClientRect(), g = sc.getBoundingClientRect(), lr = sc.classList.contains('lrail'), lo = lr ? Math.max(a.left, g.left) : Math.max(a.top, g.top), hi = lr ? Math.min(a.right, g.right) : Math.min(a.bottom, g.bottom);\n"
    "    if (Math.max(0, hi - lo) < 0.6 * (lr ? a.width : a.height)) tutReveal(el); } } // (what the tip is about, mostly out of its scroller (a turn of the phone, a scroll): back in the middle of it)\n"
    "  if (!vis) { if (tutEl.dataset.pos !== 'top')")
open(DST, 'w').write(s)
print('ui158 ok', n0, '->', len(s))
