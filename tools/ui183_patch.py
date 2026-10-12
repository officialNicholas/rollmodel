#!/usr/bin/env python3
"""v245: the lesson's roller: once it's in your hands the rival is brought round in front of you, and only when it is in your line of sight
(ahead, on screen, nothing in the way) does the tip come: swipe up and roll over him to get him."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui182_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("function tutRivalIn(dist) {", """// the roller lesson's driver: the rival makes for a spot a few metres ahead of you (its own route there if a wall's in the way), so it
// comes into your view in front of you, and once it's there, on in toward you
function tutAhead(D) {
  const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw), rx = D.x - P.x, rz = D.z - P.z, ahead = rx * fx + rz * fz, side = Math.abs(rx * fz - rz * fx), ai = D.ai;
  if (ahead > 2.5 && side < 0.6 * ahead + 1) { TUT_AI.speed = 0.8; return tutApproach(D); } /* (in front of you: on in) */
  const k = clamp(Math.hypot(rx, rz) * 0.5, 4, 7), tx = P.x + fx * k, tz = P.z + fz * k, dx = tx - D.x, dz = tz - D.z, d = Math.hypot(dx, dz); TUT_AI.speed = clamp(0.9 + d / 12, 0.9, 1.6);
  if (d > 4 && !lineClear(D, tx, tz, D.y)) { if (!ai.tutNavAt || runT - ai.tutNavAt > 0.5 || !ai.path) { ai.tutNavAt = runT; const s0 = NAV.at(D.x, D.z, D.y), g = NAV.at(tx, tz, D.y); if (s0 && g) { nMult.fill(1, 0, NN); dijkstra(s0.id); if (nDist[g.id] < Infinity) aiGo(D, g, 'hunt'); else ai.path = null; } }
    const w = aiFollow(D); if (w) return aiSteer(D, w.x, w.z, 1 / 60, true); }
  if (D.charging) cancelCharge(D);
  D.steer = -clamp(wrapA(Math.atan2(dx, dz) - D.yaw) * 3, -1, 1);
}
// the rival in your line of sight: ahead of you, on screen, not too far, nothing in the way
function tutRivalSeen(maxD) { const D = H; if (!D || D.st !== 'play' || P.st !== 'play') return false; const dx = D.x - P.x, dz = D.z - P.z, d = Math.hypot(dx, dz); if (d > maxD || d < 3.2) return false; /* (too close to react: it waits for the next pass) */
  if (Math.sin(P.yaw) * dx + Math.cos(P.yaw) * dz < d * 0.3) return false; tv1.set(D.x, D.y + 0.3, D.z).project(camera); return tv1.z < 1 && Math.abs(tv1.x) < 0.82 && Math.abs(tv1.y) < 0.82 && lineClear(P, D.x, D.z, P.y); }
function tutRivalIn(dist) {""")
rep("  { id: 'free2', max: 99, enter() { tutHide(); tut.slowK = 1; tut.wait = 6; tut.rTip = !!(P.power && P.power.type === 'roller'); tut.rTipT = 3.4; if (tut.rTip) tutShow(say('*SWIPE UP* to roll over the rival!', 'Press *SHIFT* to roll over the rival!'), null, 'rroll', true, true); }, /* (now a roller: a quick word on rolling over the rival, at full speed) */\n    tick(dt) { if (tut.rTip) { tut.rTipT -= dt; if (tut.rTipT <= 0 || P.rollT > 0 || !(P.power && P.power.type === 'roller')) { tut.rTip = false; tutHide(); } } tut.wait -= dt; return tut.wait <= 0; } },",
    """  { id: 'free2', max: 30, enter() { tutHide(); tut.slowK = 1; tut.wait = 6; tut.rTip = !!(P.power && P.power.type === 'roller'); tut.rTipT = 0; tut.rSeen = false; if (tut.rTip) { tut.drive = H; tut.driveMode = 'ahead'; if (H.ai) { H.ai.plan = null; H.ai.path = null; } tut.rIn = tutRivalIn(7); } }, /* (now a roller: the rival comes round in front of you, and once he's in your sights, a word on rolling over him) */
    exit() { if (tut.driveMode === 'ahead') { tut.drive = null; tut.driveMode = null; TUT_AI.speed = 0.8; } },
    tick(dt) { if (tut.rTip) { const have = !!(P.power && P.power.type === 'roller');
        if (!tut.rSeen) { if (!tut.rIn) tut.rIn = tutRivalIn(7); if (!have) { tut.rTip = false; } else if (tutRivalSeen(9)) { tut.rSeen = true; tut.rTipT = 3.6; tut.wait = 6; tutShow(say('*SWIPE UP* and roll over him to get him!', 'Press *SHIFT* and roll over him to get him!'), null, 'rroll', true, true); } else { tut.wait = Math.max(tut.wait, 2); return false; } } /* (the tip waits for him to be in your line of sight) */
        else { tut.rLost = tutRivalSeen(14) || Math.hypot(H.x - P.x, H.z - P.z) < 3.2 ? 0 : (tut.rLost || 0) + dt; tut.rTipT -= dt; if (tut.rTipT <= 0 || P.rollT > 0 || !have || tut.rLost > 0.6) { /* (he's gone out of sight: the tip goes) */ tut.rTip = false; tutHide(); if (tut.driveMode === 'ahead') { tut.drive = null; tut.driveMode = null; TUT_AI.speed = 0.8; } } } }
      tut.wait -= dt; return tut.wait <= 0; } },""")
rep("  if (tut.driveMode === 'cross') return tutToCross(D);", "  if (tut.driveMode === 'cross') return tutToCross(D);\n  if (tut.driveMode === 'ahead') return tutAhead(D);")
rep('<p class="ver">Version 244</p>', '<p class="ver">Version 245</p>')
open(DST, 'w').write(s)
print('ui183 ok', n0, '->', len(s))
