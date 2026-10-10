#!/usr/bin/env python3
"""v189: slow motion you can hear and see. The short callouts (POUND now, NOW! Swipe up...) sit mid-screen, and going into a slow-mo
moment muffles the music (as the pause does) under a Ludo slow-down whoosh, with a rising one on the way out. The clips are
la/sfx/slowin_1, slowin_2 and slowout_1, built into the sound sheets."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui113_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("    tpour() { P_('tpour', { vary: 0.02, v: 0.9 }); },",
    "    tpour() { P_('tpour', { vary: 0.02, v: 0.9 }); },\n"
    "    // slow motion: the music sinks under a low-pass (as on pause, not as far) and dips; a whoosh going in, a rising one coming out\n"
    "    slow(on, quiet) { if (!ctx) return; const t = T(); musLP.frequency.cancelScheduledValues(t); musLP.frequency.setTargetAtTime(on ? 1100 : 20000, t, on ? 0.07 : 0.18); trkBus.gain.cancelScheduledValues(t); trkBus.gain.setTargetAtTime(on ? 0.72 : 1, t, on ? 0.08 : 0.2);\n"
    "      if (quiet || t - (api._slowAt || -9) < 0.45) return; api._slowAt = t; if (!P_(on ? 'slowin' : 'slowout', { vary: 0.03 })) api.whoosh(); },")
rep("function resume() { if (state !== 'paused') return; state = 'play'; pauseEl.hidden = true; AU.music('play'); }",
    "function resume() { if (state !== 'paused') return; state = 'play'; pauseEl.hidden = true; AU.music('play'); if ($('tutSlow').classList.contains('on')) AU.slow(true, true); }")
rep('<p class="ver">Version 188</p>', '<p class="ver">Version 189</p>')
open(DST, 'w').write(s)
print('ui114 ok', n0, '->', len(s))
