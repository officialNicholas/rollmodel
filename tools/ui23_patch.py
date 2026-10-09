#!/usr/bin/env python3
"""The fight-card portrait holds the pose (no idle hop), and the weather chip steps aside while a weather banner is up. On top of ui22_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui22_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# while the portraits are being taken the lobby idle and the tap-hop stand down, and the fight-card pose applies (the card shows in the menu state)
rep("    if (D === P && (lookOpen || menuPage === 'home') && !lookIntro) { sq = idle.sq || 0.04 + 0.035 * Math.sin(clock * 2.3); rise = idle.rise; hop = idle.hop; spinY = idle.spin; }",
    "    if (D === P && (lookOpen || menuPage === 'home') && !lookIntro && !vsSnap) { sq = idle.sq || 0.04 + 0.035 * Math.sin(clock * 2.3); rise = idle.rise; hop = idle.hop; spinY = idle.spin; }")
rep("    if (D === P && menuReact > 0) { const u = 1 - menuReact / 0.7;", "    if (D === P && menuReact > 0 && !vsSnap) { const u = 1 - menuReact / 0.7;")
rep("  if (D.ip && state !== 'menu') { const ip = D.ip; hop += ip.hop;", "  if (D.ip && (state !== 'menu' || vsSnap)) { const ip = D.ip; hop += ip.hop;")
# one weather notice at a time: the chip waits while the banner says it large, and comes back when the banner has gone
rep("const bannerEl = $('banner');", "const bannerEl = $('banner'); let bannerUntil = 0, bannerWx = false;")
rep("function banner(big, small, long) { $('bannerBig').textContent = big;", "function banner(big, small, long) { bannerUntil = performance.now() + (long ? 3400 : 2100); bannerWx = /heat|rain/i.test(big); $('bannerBig').textContent = big;")
rep("    const wx = $('wx'), wxOn = wxPhase !== 'clear';\n", "    const wx = $('wx'), wxOn = wxPhase !== 'clear' && !(bannerWx && performance.now() < bannerUntil);\n")
# the rivals' hats and halos were still mid drop-in from the last match (nothing animates them while they are hidden in the lobby): worn properly for the card
rep("  for (const [D, , pose] of list) { if (D !== P) { D.look.drop.visible = true;", "  for (const [D, , pose] of list) { D.wearPop = 1; D.wearOff = false; D.wearHid = false; if (D !== P) { D.look.drop.visible = true;")
rep('<p class="ver">Version 92</p>', '<p class="ver">Version 93</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
