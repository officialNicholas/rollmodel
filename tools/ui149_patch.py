#!/usr/bin/env python3
"""v221: a lesson's praise and the next tip never share the screen. The next lesson waits until the praise has actually gone (and for any
banner it waits behind), then a short beat, instead of counting a fixed time that could end as the praise was still fading (landing in
the basin: the praise and "Full tank! Tap POUND to burst out" were on screen together)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui148_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("  if (tut.gap > 0) { tut.gap -= dt; if (tut.gap <= 0) { tut.gap = 0; tutNext(); } return; }",
    "  if (tut.gap > 0) { tut.gap -= dt; if (tut.gap <= 0) { if (tutPraiseEl.classList.contains('on') || tutPraiseEl._pend) tut.gap = 0.25; else { tut.gap = 0; tutNext(); } } return; } // (the praise gone, and a beat after it)")
rep("go = () => { restartCls(tutPraiseEl, 'on'); tutPraiseEl._t = setTimeout(() => tutPraiseEl.classList.remove('on'), 1150); }; if (bw > 30) { tutPraiseEl.classList.remove('on'); tutPraiseEl._t0 = setTimeout(go, bw); } else go(); }",
    "go = () => { tutPraiseEl._pend = false; restartCls(tutPraiseEl, 'on'); tutPraiseEl._t = setTimeout(() => tutPraiseEl.classList.remove('on'), 1150); }; if (bw > 30) { tutPraiseEl.classList.remove('on'); tutPraiseEl._pend = true; tutPraiseEl._t0 = setTimeout(go, bw); } else go(); }")
# (leaving the lesson drops a praise still waiting on a banner)
rep("function tutLeave() { tut2 = null;", "function tutLeave() { clearTimeout(tutPraiseEl._t0); tutPraiseEl._pend = false; tutPraiseEl.classList.remove('on'); tut2 = null;")
rep('<p class="ver">Version 220</p>', '<p class="ver">Version 221</p>')
open(DST, 'w').write(s)
print('ui149 ok', n0, '->', len(s))
