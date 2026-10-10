#!/usr/bin/env python3
"""Two things. The Squid eyes lose their separate leaf brow: the heavy upper lid is the brow now, so there is one, not two. And the power-up and special-move timers float beside the player as a ring: a dial to the blob's left that empties as a roller, turret, giant or rocket runs out, and fills gold as the pound recharges, with the seconds in it. The chip in the corner is gone. On top of ui77_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui77_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# one brow, not two
rep("      vec2 b0 = pc + vec2(sd * 0.02, 0.44), b1 = pc + vec2(sd * 0.3, 0.52); sp = max(sp, fCone(fq, b0, b1, 0.055, 0.01)); } // the brow: a leaf above, thick at the inner end, tapering out and up",
    "    } // (no brow of its own: the heavy upper lid is the brow)")
# the floating timer
rep('  <div class="hud off" id="hud">', '  <div class="ptimer" id="ptimer" hidden aria-hidden="true"><i id="ptRing"></i><b id="ptN"></b></div>\n  <div class="hud off" id="hud">')
rep("  const pwc = $('pw');", r'''  { const pt = $('ptimer'); let frac = -1, n = 0, kind = '';
    if (state === 'play' && P.st === 'play' && drop.visible) {
      if (P.rocket) { const R = P.rocket, left = R.ph === 'hover' ? Math.max(0, ROCKET_HOVER - R.t) : ROCKET_HOVER; frac = left / ROCKET_HOVER; n = Math.ceil(left); kind = 'pw'; }
      else if (P.turret) { frac = P.turret.t / TURRET_T; n = Math.ceil(P.turret.t); kind = 'pw'; }
      else if (P.giantT > 0) { frac = P.giantT / GIANT_T; n = Math.ceil(P.giantT); kind = 'pw'; }
      else if (P.power) { frac = P.power.t / PU[P.power.type].dur; n = Math.ceil(P.power.t); kind = 'pw'; }
      else if (P.slamCD > 0 && P.slamMax > 0) { frac = 1 - P.slamCD / P.slamMax; n = Math.ceil(P.slamCD); kind = 'cd'; }
    }
    if (frac < 0) { if (!pt.hidden) pt.hidden = true; }
    else { tv1.copy(drop.position).project(camera); const sx = (tv1.x + 1) / 2 * viewW, sy = (1 - tv1.y) / 2 * viewH; const on = tv1.z < 1 && sx > -40 && sx < viewW + 40;
      if (!on) { if (!pt.hidden) pt.hidden = true; } else { if (pt.hidden) pt.hidden = false; if (pt.dataset.k !== kind) pt.dataset.k = kind; pt.style.transform = 'translate(' + (sx - 58).toFixed(0) + 'px,' + (sy - 46).toFixed(0) + 'px)';
        const deg = (clamp(frac, 0, 1) * 360).toFixed(0); if (pt.dataset.d !== deg) { pt.dataset.d = deg; $('ptRing').style.background = 'conic-gradient(var(--pc) ' + deg + 'deg, rgba(23,19,32,.35) 0)'; } const ns = String(n); if ($('ptN').textContent !== ns) $('ptN').textContent = ns; } } }
  const pwc = $('pw');''')
css = '''
/* the timer beside the player: a dial that empties as a power-up runs out, and fills as the pound recharges */
.ptimer{position:absolute;left:0;top:0;z-index:6;width:44px;height:44px;pointer-events:none;will-change:transform;--pc:#fff}
.ptimer[hidden]{display:none}
.ptimer i{position:absolute;inset:0;border-radius:50%;background:conic-gradient(var(--pc) 360deg,rgba(23,19,32,.35) 0);border:2.5px solid var(--black);box-shadow:0 2px 0 var(--black),0 0 0 2px rgba(255,255,255,.35)}
.ptimer i::after{content:"";position:absolute;inset:6px;border-radius:50%;background:rgba(23,19,32,.78)}
.ptimer b{position:absolute;inset:0;display:grid;place-items:center;font:400 17px/1 var(--font-display);color:#fff;text-shadow:0 1.5px 0 var(--black)}
.ptimer[data-k="cd"]{--pc:var(--gold)}
.ptimer[data-k="cd"] b{color:var(--gold)}
.chip.pw{display:none}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
