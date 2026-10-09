#!/usr/bin/env python3
"""The floating-ledge nudge: a fling about to clip a floating slab is read for what it meant and eased onto it or under it. On top of ui21_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui21_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CODE = r'''
// ---------- the floating-ledge nudge (your flings only) ----------
// A fling about to clip a floating slab is read for what it meant: onto the slab (the arc would have risen over its top, or the lip is
// just out of reach) or under it (it would have carried on past, or the slab sits well above the arc). Within reach of a small nudge
// the flight is eased that way as it arrives. Too far off either way, or thrown from right beside the slab, and it hits like before.
// The read is taken from the live flight every few steps, since a fling can bend toward holy water on the way.
const LEDGE_M = 0.45, LEDGE_NEAR = 1.0, LEDGE_IN = 0.36; // the most it lifts or presses; how close is too close; where the easing must be done by
function ledgeFace(x, z, b) { // how far outside a slab's footprint, horizontally (negative inside)
  if (b[6] === 'c') return Math.hypot(x - (b[0] + b[1]) * 0.5, z - (b[2] + b[3]) * 0.5) - (b[1] - b[0]) * 0.5;
  return Math.max(b[0] - x, x - b[1], b[2] - z, z - b[3]);
}
function ledgePlan(D) {
  if (D.ai || window.__noLedge) return null;
  const hs = D.spd, sx = Math.sin(D.yaw), sz = Math.cos(D.yaw), m = PR * 0.9, dt = 0.02;
  // walk the flight on from here, the way the physics will (lighter gravity going up, heavier coming down)
  let x = D.x, y = D.y, z = D.z, vy = D.vy, hit = null, yHit = 0;
  const pts = [];
  for (let t = 0; t < 3 && !hit; t += dt) {
    y += vy * dt; vy -= GRAV * (vy < 0 ? 1.45 : 1) * dt; x += sx * hs * dt; z += sz * hs * dt; pts.push([x, y, z, vy]);
    if (vy < 0) { const g = surfaceUnder(x, z, y + STEP, true); if (g > -Infinity && y <= g) { if (window.__ledgeDbg) window.__ledgeLast = { why: 'lands', t: +t.toFixed(2), y: +y.toFixed(2), g: +g.toFixed(2) }; return null; } }
    for (const b of qcell(qgB, x, z)) if (b[4] > 0 && inR(x, z, b, m) && y < b[5] - STEP && y + 0.8 > b[4]) { hit = b; yHit = y; break; }
  }
  if (!hit || D.ledgeNo === hit) { if (window.__ledgeDbg) window.__ledgeLast = { why: hit ? 'declined' : 'nohit' }; return null; }
  const b = hit, fd0 = ledgeFace(D.flingX, D.flingZ, b);
  if (fd0 >= 0 && fd0 < LEDGE_NEAR) { D.ledgeNo = b; return null; } // thrown from right beside it: that one's on you
  // what it was going for: carry the arc on through the slab. Rising over its top while above it means it wanted on; else it wanted past
  let overTop = false, yMax = -Infinity;
  for (let t = pts.length * dt; t < 3; t += dt) {
    y += vy * dt; vy -= GRAV * (vy < 0 ? 1.45 : 1) * dt; x += sx * hs * dt; z += sz * hs * dt;
    const inside = inR(x, z, b, m); if (inside) { yMax = Math.max(yMax, y); if (y >= b[5]) overTop = true; }
    if (!inside && ledgeFace(x, z, b) > 0.5 && vy < 0) break;
    if (vy < 0) { const g = surfaceUnder(x, z, Math.min(y + STEP, b[4] - 0.01), true); if (g > -Infinity && y <= g) break; }
  }
  const go = (b[5] - STEP + 0.03) - yHit, gu = (yMax + 0.8) - (b[4] - 0.03); // the lift to clear the lip; the press to pass under
  const canOver = fd0 >= 0 && go > 0 && go <= LEDGE_M, canUnder = gu > 0 && gu <= LEDGE_M;
  if (window.__ledgeDbg) window.__ledgeLast = { go: +go.toFixed(2), gu: +gu.toFixed(2), overTop, fd0: +fd0.toFixed(2), yHit: +yHit.toFixed(2), yMax: +yMax.toFixed(2), b: b.slice(0, 6) };
  let plan = null;
  if (overTop) plan = canOver ? 'over' : null;
  else if (canOver && (!canUnder || go <= gu)) plan = 'over';
  else if (canUnder) plan = 'under';
  if (!plan) { D.ledgeNo = b; return null; }
  return { b, mode: plan, y: plan === 'over' ? b[5] - STEP + 0.03 : b[4] - 0.8 - 0.03 };
}
function ledgeNudge(D, dt) {
  if (!D.air || !D.flung || D.st !== 'play' || D.slam) { D.ledge = null; return; }
  if (!D.ledge) { if (stepNo % 3 === 0) D.ledge = ledgePlan(D); if (!D.ledge) return; }
  const L = D.ledge, b = L.b, fd = ledgeFace(D.x, D.z, b), reach = D.spd * 0.35 + 0.8; if (fd > reach) return;
  const tArr = Math.max(dt, (fd - LEDGE_IN) / Math.max(0.5, D.spd)), k = Math.min(1, dt / tArr); // eased so it is done by the face
  if (L.mode === 'over') { if (D.y < L.y) D.y += (L.y - D.y) * k; else if (fd < 0) D.ledge = null; }
  else { if (D.y > L.y) { D.y += (L.y - D.y) * k; if (D.vy > 0) D.vy = 0; } if (fd < 0) L.in = true; else if (L.in) D.ledge = null; }
}
'''
rep("function flightFor(c, dy) {", CODE.lstrip('\n') + "function flightFor(c, dy) {")
rep("  if (!D.ai) { const as = assistShot(D, D.yaw, c); D.yaw = as.yaw; c = as.c; }\n  D.air = true; D.vy = launchV(c); D.spd = launchSpd(c);",
    "  if (!D.ai) { const as = assistShot(D, D.yaw, c); D.yaw = as.yaw; c = as.c; }\n  D.air = true; D.vy = launchV(c); D.spd = launchSpd(c); D.ledge = null; D.ledgeNo = null; D.flingX = D.x; D.flingZ = D.z;\n  if (!D.ai) D.ledge = ledgePlan(D);")
rep("  moveFlat(D, dt);\n  if (D.buf > 0) D.buf -= dt;", "  if (!D.ai && D.flung && D.air) ledgeNudge(D, dt);\n  moveFlat(D, dt);\n  if (D.buf > 0) D.buf -= dt;")
rep('<p class="ver">Version 91</p>', '<p class="ver">Version 92</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
