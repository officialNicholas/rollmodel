#!/usr/bin/env python3
"""The HUD strip shows who is ahead: shares of the paint on the stage, poured in as liquid. On top of ui19_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui19_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

rep("const tugLiq = makeLiquid($('meter'));", "const tugLiq = makeLiquid($('meter')); let tugT = 0; const tugS = { y: 0, c: 0 }; // the strip's shares, eased so paint pours in rather than jumping")
OLD = "    $('tugYou').style.width = you.toFixed(2) + '%'; $('tugCpu').style.width = cpu.toFixed(2) + '%';\n    { const c2 = mode === 'trio' ? teamCov(2) : 0, segs = [{ x0: 0, x1: you / 100, col: TEAMS[0].css }, { x0: 1 - cpu / 100, x1: 1, col: TEAMS[1].css }]; if (mode === 'trio') segs.push({ x0: 1 - (cpu + c2) / 100, x1: 1 - cpu / 100, col: TEAMS[2].css }); tugLiq.set(segs); tugLiq.tick(performance.now()); }\n"
NEW = '''    // the strip is the lead, not the coverage: each colour's share of all the paint down, so the leader's side grows and the bar is always full once anyone has painted
    { const c2 = mode === 'trio' ? teamCov(2) : 0, tot = you + cpu + c2, now = performance.now(), dt = Math.min(0.1, (now - (tugT || now)) / 1000), k = 1 - Math.exp(-dt * 5); tugT = now;
      if (tot < 0.02) { tugS.y = tugS.c = 0; tugLiq.set([]); tugLiq.clear(); $('tugYou').style.width = $('tugCpu').style.width = '0%'; }
      else { tugS.y += (you / tot - tugS.y) * k; tugS.c += (cpu / tot - tugS.c) * k; const snap = v => v > 0.995 ? 1 : v < 0.004 ? 0 : v, yS = snap(tugS.y), cS = snap(tugS.c);
        $('tugYou').style.width = (yS * 100).toFixed(2) + '%'; $('tugCpu').style.width = (cS * 100).toFixed(2) + '%';
        const segs = [{ x0: cS ? Math.max(0, 1 - cS - 0.015) : 1, x1: 1, col: TEAMS[1].css }]; if (mode === 'trio') segs.push({ x0: Math.max(0, yS - 0.015), x1: Math.min(1, 1 - cS + 0.015), col: TEAMS[2].css }); segs.push({ x0: 0, x1: yS, col: TEAMS[0].css });
        tugLiq.set(segs); tugLiq.tick(now); } }
'''
rep(OLD, NEW)
rep("const tc2 = $('tugCpu2'); tc2.style.width = c2.toFixed(2) + '%'; tc2.style.right = cpu.toFixed(2) + '%'; }",
    "const tc2 = $('tugCpu2'); tc2.style.width = (Math.max(0, 1 - tugS.y - tugS.c) * 100).toFixed(2) + '%'; tc2.style.right = (tugS.c * 100).toFixed(2) + '%'; }")
rep("  L.set = segs => {", "  L.clear = () => g.clearRect(0, 0, c.width, c.height);\n  L.set = segs => {")
# a little taller, so the liquid reads
rep(".tug{height:13px;border-radius:0;background:#E6DECF;", ".tug{height:16px;border-radius:0;background:#E6DECF;")
rep('<p class="ver">Version 89</p>', '<p class="ver">Version 90</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
