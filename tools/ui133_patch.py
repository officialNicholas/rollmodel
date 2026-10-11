#!/usr/bin/env python3
"""v207 (with ui132): a CPU that stops throwing itself off the canvas, and drives smoother.
Measured over simulated AI-vs-AI matches (tools/aisim.py logs the last 2.5 s before every fall, tools/coffintest.py puts a CPU in every
coffin near the edge): most falls were hops out of a coffin by the edge (the check only looked straight down the planned line, and it
leaves while still turning, so it landed on the lip and rolled off), a drained coffin popping it out facing the way it came in, a brake
to turn on the spot sliding it over a hole, and hops (a dodge, a grab for the orb) or mid-air steering with no look at where they land.
Steering: the wanted heading eases round when nothing's pressing (a waypoint popping into view swung it in one step), a detour
round a puddle keeps to the side it picked instead of flicking left, right, left, and a target it has rolled past is let go of
more readily than one still ahead (doubling back for it was a U-turn)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui132_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# --- coffins: a safe way out, whatever ends the stay ---
rep('''function exitYaw(D, want) {
  const p = D.pot, ok = a => { for (let d = 0.5; d <= 4.8; d += 0.35) { const x = p.x + Math.sin(a) * d, z = p.z + Math.cos(a) * d; if (surfaceUnder(x, z, p.y + 1.2) === -Infinity) return false; if (d > 2.4 && rivals.some(r => r.on && Math.abs(r.y - p.y) < 0.4 && Math.hypot(x - r.x, z - r.z) < r.hit)) return false; } return true; };
  if (ok(want)) return want;
  for (let k = 1; k <= 8; k++) for (const sg of [1, -1]) { const a = want + sg * k * 0.393; if (ok(a)) return a; }
  return want;
}''', '''// how far the floor runs from coffin p along heading a (past L: all of it)
function exitRun(p, a, d0, L, boil) { for (let d = d0; d <= L; d += 0.35) { const x = p.x + Math.sin(a) * d, z = p.z + Math.cos(a) * d; if (surfaceUnder(x, z, p.y + 1.2) === -Infinity) return d; if (boil && d > 2.4 && rivals.some(r => r.on && Math.abs(r.y - p.y) < 0.4 && Math.hypot(x - r.x, z - r.z) < r.hit)) return d; } return L + 1; }
// a safe way out: the hop lands about four units out and rolls on, so floor well past that, and a little either side too (it can
// leave while still turning, and lands where it was facing then)
function exitOK(D, a) { return exitRun(D.pot, a, 0.5, 5.9, true) > 5.9 && exitRun(D.pot, a - 0.3, 2.1, 4.9) > 4.9 && exitRun(D.pot, a + 0.3, 2.1, 4.9) > 4.9; }
function exitYaw(D, want) {
  if (exitOK(D, want)) return want;
  for (let k = 1; k <= 8; k++) for (const sg of [1, -1]) { const a = want + sg * k * 0.393; if (exitOK(D, a)) return a; }
  let best = want, bd = -1; for (let k = 0; k < 16; k++) { const a = want + k * 0.393, d = exitRun(D.pot, a, 0.5, 5.9, true); if (d > bd) { bd = d; best = a; } } // (boxed in: the way with the most floor)
  return best;
}''')
# a drained coffin pops you out the safe way (the way you face is usually the way you came in: from the middle, toward the edge)
rep('if (D.emptyT > 0.8) { D.emptyT = 0; if (D.charging) clearCharge(D); if (D === P) { holdCharge = false; slingOff(); } exitPot(D); }',
    'if (D.emptyT > 0.8) { D.emptyT = 0; if (D.charging) clearCharge(D); if (D === P) { holdCharge = false; slingOff(); } D.yaw = exitYaw(D, D.yaw); D.turn = 0; exitPot(D); }')
rep('  if (Math.abs(err) < (ep.flee ? 1.3 : 0.35) || ep.t > (ep.flee ? 0.3 : 1.2)) {',
    '  // lined up before it hops (the way out is only checked a little either side), and never out over a drop: running from a pound it\n'
    '  // goes as soon as it faces a safe way out, and a slow turn only gives up waiting once the way it faces is safe\n'
    '  const safeNow = exitOK(D, D.yaw);\n'
    '  if (ep.flee ? safeNow && (Math.abs(err) < 1.3 || ep.t > 0.3) || Math.abs(err) < 0.25 : Math.abs(err) < 0.25 || ep.t > 1.2 && (safeNow || ep.t > 2.4)) {')
rep("  D.st = 'hide'; D.pot = p; p.occ = D; D.air = false;", "  D.st = 'hide'; D.pot = p; p.occ = D; D.emptyT = 0; D.air = false;")

# --- braking to aim, or to turn on the spot: stop dead at a drop instead of sliding the last bit into it (you, and the CPU) ---
rep('  if (D.charging) { D.spd += (0 - D.spd) * Math.min(1, dt * 16); updateCharge(D, dt); }',
    '  if (D.charging) { D.spd += (0 - D.spd) * Math.min(1, dt * 16); updateCharge(D, dt); if (!D.air && D.spd > 0.05) { const r = 0.3 + D.spd * 0.08; if (surfaceUnder(D.x + Math.sin(D.yaw) * r, D.z + Math.cos(D.yaw) * r, D.y + STEP, true) === -Infinity) D.spd = 0; } } // (holding to aim is a brake: it stops at a hole or the edge rather than sliding into it)')

# --- hops: look where they come down first ---
rep('''// is the straight line from the blob to a point safe to roll
function lineClear(D, x, z, h) {''', '''// solid floor at (x, z) and all round it (radius r) at about height y
function solidAround(x, z, y, r) { if (surfaceUnder(x, z, y + STEP, true) === -Infinity) return false; for (let a = 0; a < 6.28; a += 1.05) if (surfaceUnder(x + Math.sin(a) * r, z + Math.cos(a) * r, y + STEP, true) === -Infinity) return false; return true; }
// a hop from here lands about 0.68 s of rolling ahead: only hop if that's floor (a dodge or a grab is no use off the edge)
function hopOK(D) { return solidAround(D.x + Math.sin(D.yaw) * D.spd * 0.68, D.z + Math.cos(D.yaw) * D.spd * 0.68, D.y, 0.6); }
// mid-air, heading a: does it come down on something (straight on at its speed for the time left to fall to the floor below), with
// nothing in the way at the height it'll be (a wall turns it aside, maybe into a hole), and floor just past where it lands
function airLandOK(D, a) {
  const gy = surfaceUnder(D.x, D.z, D.y + 0.1, true), g0 = gy > -Infinity ? gy : D.y, G1 = GRAV * 1.45, t = clamp((Math.max(0, D.vy) + Math.sqrt(D.vy * D.vy + 2 * G1 * Math.max(0, D.y - g0))) / G1, 0.05, 1.5);
  const sx = Math.sin(a), sz = Math.cos(a), L = D.spd * t;
  for (let k = 1; k <= 4; k++) { const f = k / 4; if (blockedAt(D.x + sx * L * f, D.z + sz * L * f, D.y + (g0 - D.y) * f * f)) return false; }
  return solidAround(D.x + sx * L, D.z + sz * L, g0, 0.8) && solidAround(D.x + sx * (L + 1), D.z + sz * (L + 1), g0, 0.4);
}
// is the straight line from the blob to a point safe to roll
function lineClear(D, x, z, h) {''')
rep("if (Math.hypot(orb.x - D.x, orb.z - D.z) < 2.6 && orb.y - D.y < 2.1 && orb.y - D.y > -0.2 && !D.charging) jump(D);",
    "if (Math.hypot(orb.x - D.x, orb.z - D.z) < 2.6 && orb.y - D.y < 2.1 && orb.y - D.y > -0.2 && !D.charging && solidAround(orb.x, orb.z, D.y, 1.2)) jump(D); /* (not for an orb hanging over a hole: the grab drops it straight down) */")
rep('      if (D.charging) cancelCharge(D); jump(D); return true;\n    } }',
    '      if (hopOK(D)) { if (D.charging) cancelCharge(D); jump(D); return true; }\n    } }')
rep('Math.random() < AI.hop) { if (D.charging) cancelCharge(D); jump(D); return true; }',
    'Math.random() < AI.hop && hopOK(D)) { if (D.charging) cancelCharge(D); jump(D); return true; }')
rep("eta < 0.3 && eta > 0.04 && Math.abs((R.gy || 0) - D.y) < 1.4) { if (D.charging) cancelCharge(D); jump(D); return true; }",
    "eta < 0.3 && eta > 0.04 && Math.abs((R.gy || 0) - D.y) < 1.4 && hopOK(D)) { if (D.charging) cancelCharge(D); jump(D); return true; }")
# mid-air: only bend toward you if it still comes down on something
rep("if (ai.flight === 'attack' || d < 4) { const err = wrapA(Math.atan2(dx, dz) - D.yaw); D.steer = -clamp(err * 2.5, -1, 1); }",
    "if ((ai.flight === 'attack' || d < 4) && airLandOK(D, Math.atan2(dx, dz))) { const err = wrapA(Math.atan2(dx, dz) - D.yaw); D.steer = -clamp(err * 2.5, -1, 1); }")

# --- re-plans: keep a target that's still ahead, let go of one it has rolled past (doubling back for it is a U-turn) ---
rep('cur = (nAcc[n.id] + 0.7 * v + p) / (nDist[n.id] + 2.5) * (1 - 0.4 * routeTurn(D, n.id)); if (cur > pick[0] * 0.66) pick = [cur, ai.tgt, p];',
    'rt = routeTurn(D, n.id), cur = (nAcc[n.id] + 0.7 * v + p) / (nDist[n.id] + 2.5) * (1 - 0.4 * rt); if (cur > pick[0] * (rt < 0.5 ? 0.66 : 0.85)) pick = [cur, ai.tgt, p];')

# --- steering: detours keep their side, and the heading eases round when nothing's pressing ---
rep('''function aiSafe(D, want) {
  const base = hazardAt(D, want); if (base < 0.5) return want;
  let best = want, bs = base;
  for (let i = 0; i < AI_OFFS.length; i++) { const off = AI_OFFS[i], s = hazardAt(D, want + off) + Math.abs(off) * 1.4; if (s < bs) { bs = s; best = want + off; } }
  return best;
}''', '''function aiSafe(D, want) {
  const ai = D.ai, base = hazardAt(D, want); ai.hz = base; if (base < (ai.safeSide ? 0.3 : 0.5)) { ai.safeSide = 0; return want; }
  let best = want, bs = base, side = 0;
  // (going round the same side as last time gets a small edge, so a puddle dead ahead doesn't flick it left, right, left)
  for (let i = 0; i < AI_OFFS.length; i++) { const off = AI_OFFS[i], s = hazardAt(D, want + off) + Math.abs(off) * 1.4 + (ai.safeSide && off * ai.safeSide < 0 ? 0.8 : 0); if (s < bs) { bs = s; best = want + off; side = Math.sign(off); } }
  ai.safeSide = side; return best;
}''')
rep('''  if (!(Math.random() < AI.slip * dt)) want = aiSafe(D, want);
  ai.noisePh += dt * 1.6;''', '''  if (!(Math.random() < AI.slip * dt)) want = aiSafe(D, want); else ai.hz = 0;
  // ease round to a new heading when nothing's pressing: a waypoint popping into view or a change of plan swings the wanted heading
  // in one step, and steering straight at it reads as a twitch (a drop ahead, a chase, a careful approach, or going fast as a giant gets it at once: at
  // double speed the lag carries it past the corner and it circles back)
  if (urgent || precise || D.charging || ai.hz > 30 || D.spd > cfg.speed * 1.2 || !(runT - (ai.wantT || -9) < 0.1)) ai.wantS = want; else ai.wantS += wrapA(want - ai.wantS) * Math.min(1, dt * 8);
  ai.wantT = runT; want = ai.wantS;
  ai.noisePh += dt * 1.6;''')

open(DST, 'w').write(s)
print('ui133 ok', n0, '->', len(s))
