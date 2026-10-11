#!/usr/bin/env python3
"""v223: the lesson's basin and its finale.
 - The basin lesson: its basin comes up a little further ahead, and only somewhere on screen; a couple of seconds into "roll into a basin"
   without getting there, a finger shows the swipe up (a roll gets you there faster).
 - The finale (Ol' Bloop's "Now win it!"): ten seconds on the clock, whatever was left. Two rollers pop up close by, either side of you (a
   third if you still have none a few seconds in); with about four seconds to go the orb comes up right in front of you and stays put; the
   clock holds while you ride its rocket (it boosts down by itself if you don't), and the match ends a moment after it lands, so the last
   thing you see is the rocket's blast. The arrow points you at a roller, then the orb."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui150_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- the basin lesson: further ahead, on screen; the swipe-up finger a couple of seconds in
rep("  for (const d of [7, 6, 8, 5]) { for (const da of [0, 0.3, -0.3, 0.6, -0.6, 0.9, -0.9]) { const a = P.yaw + da, x = P.x + Math.sin(a) * d, z = P.z + Math.cos(a) * d; if (ok(x, z)) { spot = [x, P.y, z]; break; } } if (spot) break; }",
    "  const seen = (x, z) => { tv1.set(x, P.y + 0.4, z).project(camera); return tv1.z < 1 && Math.abs(tv1.x) < 0.75 && tv1.y > -0.55 && tv1.y < 0.75; }; // (somewhere on screen)\n"
    "  for (const pass of [0, 1]) { for (const d of pass ? [9.5, 8.5, 7.5, 6.5, 5.5, 5, 4.5] : [9.5, 10.5, 8.5, 11.5, 7.5, 6.5]) { for (const da of [0, 0.25, -0.25, 0.5, -0.5, 0.8, -0.8]) { const a = P.yaw + da, x = P.x + Math.sin(a) * d, z = P.z + Math.cos(a) * d; if (ok(x, z) && (pass || seen(x, z))) { spot = [x, P.y, z]; break; } } if (spot) break; } if (spot) break; }")
rep("{ id: 'basin', max: 55, enter() { tut.slowK = 1; tut.basinTip = false;", "{ id: 'basin', max: 55, enter() { tut.slowK = 1; tut.basinTip = false; tut.basinT = 0; tut.basinSw = false;")
rep("      if (!tut.basinTip && P.paint <= 0.02) { tut.basinTip = true; pingTank(4);",
    "      if (tut.basinTip && !tut.basinSw) { tut.basinT += dt; if (tut.basinT > 2.5 && P.st === 'play') { tut.basinSw = true; tutGest('swipe'); } } /* (not there yet: a finger shows the swipe up, a roll gets you there faster) */\n"
    "      if (!tut.basinTip && P.paint <= 0.02) { tut.basinTip = true; pingTank(4);")
# ---- the finale: ten seconds on the clock at Ol' Bloop's card
rep("  if (on) { el.dataset.mode = 'rest'; tutCardText(TG_REST); tut.card = true;", "  if (on) { el.dataset.mode = 'rest'; tutCardText(TG_REST); matchLeft = 10; tut.card = true;")
rep("if (tut.card) { P.paint = 1; P.slamCD = 0; banner('Paint it ' + colorOf().name.toLowerCase() + '!', TH.label, true); }",
    "if (tut.card) { P.paint = 1; P.slamCD = 0; matchLeft = 10; banner('Paint it ' + colorOf().name.toLowerCase() + '!', TH.label, false, true); tutFinStart(); }")
rep("      const lead = teamCov(0) - teamCov(1), close = lead < 7; TUT_AI.speed = close ? 0.58 : 0.8;",
    "      if (tut.fin) tutFinTick(dt);\n      const lead = teamCov(0) - teamCov(1), close = lead < 7; TUT_AI.speed = close ? 0.58 : 0.8;")
FIN = r"""
// the lesson's finale, the ten seconds after Ol' Bloop's card: rollers close by either side of you to start (one more if you have none a few
// seconds in), then with about four seconds left the orb right in front of you; its rocket's landing is the last big moment (the clock holds
// while you're up there, it boosts down by itself if you don't, and the match ends a moment after the blast)
function tutNearSpot(ds, as, anyView) {
  for (const d of ds) for (const da of as) {
    const a = P.yaw + da, x = P.x + Math.sin(a) * d, z = P.z + Math.cos(a) * d; if (Math.abs(x) > ARENA - 1.5 || Math.abs(z) > ARENA - 1.5) continue;
    const y = surfaceUnder(x, z, P.y + 0.3); if (!(Math.abs(y - P.y) < 0.3) || blockedAt(x, z, y) || !lineClear(P, x, z, P.y)) continue;
    if (pots.some(p => Math.hypot(p.x - x, p.z - z) < 2) || powers.some(o => Math.hypot(o.x - x, o.z - z) < 1.6) || rivals.some(r => Math.hypot(r.x - x, r.z - z) < r.rad + 1.2)) continue;
    tv1.set(x, y + 0.3, z).project(camera); if (!anyView && !(tv1.z < 1 && Math.abs(tv1.x) < 0.8 && tv1.y > -0.7 && tv1.y < 0.8)) continue;
    return [x, y, z]; }
  return null;
}
function tutFinRoller(side) {
  const as = side > 0 ? [side, side + 0.25, side - 0.2, 0.15, 0.7] : side < 0 ? [side, side - 0.25, side + 0.2, -0.15, -0.7] : [0, 0.25, -0.25, 0.5, -0.5];
  const sp = tutNearSpot([3.8, 4.8, 5.8, 3], as) || tutNearSpot([3, 4, 5, 6.5], [0.3, -0.3, 0.6, -0.6, 0.95, -0.95, 1.3, -1.3, 0]) || tutNearSpot([3.5, 5], [0, 0.6, -0.6, 1.3, -1.3, 2, -2, 3.1], true); if (!sp) return false; /* (a cluttered canvas: anywhere close and in view) */
  const pw = { phase: Math.random() * 6, pop: 0, grace: 0, owner: null }; placePower(pw, 'roller', sp); powers.push(pw); AU.spot(); return true;
}
function tutFinStart() {
  tut.fin = { more: false, orb: false, orbT: 0, useTip: false, boostTip: false, rk: false, landed: false, outSw: false }; tut.orbMine = true; tut.items = true;
  if (orb.on) tutOrbOff(); orb.spawnT = 1e9; itemSpawn.t = 1e9; tutFinRoller(0.45); tutFinRoller(-0.45);
}
function tutFinOrb(sp) {
  orb.on = true; orb.k = 0; orb.pull = 0; orb.x = sp[0]; orb.z = sp[2]; orb.base = sp[1]; orb.y = sp[1] + 1.15; orb.ph = Math.random() * 6.28; orb.tx = orb.x; orb.tz = orb.z; orb.stay = true;
  orb.g.visible = true; orb.ring.visible = true; AU.orb(); kick($('orbFlash'), 'on'); popText('Orb!');
  for (let i = 0; i < 16; i++) { const a = i / 16 * 6.283; spawnPart(orb.x, orb.y, orb.z, Math.cos(a) * 2.5, (Math.random() - 0.3) * 3, Math.sin(a) * 2.5, 0.5, orbPartMats[i % orbPartMats.length], 0.5); }
}
function tutFinTick(dt) {
  const F = tut.fin;
  if (!F.more && matchLeft < 7.2 && !P.held && !P.power && !P.rocket && P.st === 'play' && !powers.some(q => q.type === 'roller' && Math.hypot(q.x - P.x, q.z - P.z) < 9)) F.more = tutFinRoller(0);
  if (!F.useTip && P.held === 'roller' && !P.rocket) { F.useTip = true; tutShow(say('*TAP* the roller!', 'Press *F* to roll!'), 'itemBtn', 'finuse', true, true); }
  if (F.useTip && tutTip && tutTip.key === 'finuse' && P.held !== 'roller') tutHide();
  if (!F.orb && matchLeft <= 4.2 && !P.rocket && (P.st === 'play' || P.st === 'hide')) { const sp = tutNearSpot([2.8, 3.4, 2.3, 4], [0, 0.2, -0.2, 0.4, -0.4, 0.7, -0.7]) || tutNearSpot([2.6, 3.4, 4.2], [1, -1, 1.4, -1.4]) || tutNearSpot([2.6, 3.4], [0, 1, -1, 2, -2, 3.1], true); if (sp) { F.orb = true; tutFinOrb(sp); } }
  // (not taken in a moment, it comes to you; still down in a basin, a finger shows the swipe out)
  if (F.orb && orb.on && orb.stay) { F.orbT += dt; if (P.st === 'play' && !P.rocket) { const dx = P.x - orb.x, dz = P.z - orb.z, d = Math.hypot(dx, dz);
      if (F.orbT > 0.8 && d > 0.01) { const st = Math.min(d, dt * 4.5); orb.x += dx / d * st; orb.z += dz / d * st; orb.tx = orb.x; orb.tz = orb.z; }
      if (d < 1.3 && orb.k > 0.45) takeOrb(P); } if (P.st === 'hide' && !F.outSw) { F.outSw = true; tutGest('swipe'); } else if (P.st !== 'hide' && F.outSw) { F.outSw = false; tutGest(null); } }
  if (P.rocket) { F.rk = true; if (matchLeft < 0.9) matchLeft = 0.9; const R = P.rocket;
    if (R.ph === 'hover') { if (!F.boostTip) { F.boostTip = true; tutShow(say('Tap *BOOST* to slam down!', 'Press *E* to slam down!'), 'slamBtn', 'finboost', true, true); } if (R.t > 1.5) rocketDive(P, false); } }
  else if (F.rk && !F.landed) { F.landed = true; tutHide(); matchLeft = Math.min(matchLeft, 1.6); }
}
"""
rep("// the lesson's rival, far off and out of sight:", FIN.lstrip('\n') + "// the lesson's rival, far off and out of sight:")
# the orb put down for you stays where it is (no wandering off) until it's taken
rep("if (d < 0.4) orbPickTarget(); else {", "if (d < 0.4) { if (!orb.stay) orbPickTarget(); } else {")
rep("else if (orb.pull) { orb.pull = Math.max(0, orb.pull - dt * 3); if (!orb.pull) orbPickTarget(); }", "else if (orb.pull) { orb.pull = Math.max(0, orb.pull - dt * 3); if (!orb.pull && !orb.stay) orbPickTarget(); }")
rep("function takeOrb(D) {\n  orb.on = false; orb.pull = 0;", "function takeOrb(D) {\n  orb.on = false; orb.pull = 0; orb.stay = false;")
# the arrow: to a roller, then the orb
rep("  if (id === 'flower' && gift.on && !gift.got) return [gift.x, gift.z];",
    "  if (id === 'rest' && tut.fin) { if (orb.on && !P.rocket) return [orb.x, orb.z]; if (!P.held && !P.power && !P.rocket) { let b = null, bd = 1e9; for (const q of powers) if (q.g && q.type === 'roller') { const d = Math.hypot(q.x - P.x, q.z - P.z); if (d < bd) { bd = d; b = q; } } if (b) return [b.x, b.z]; } return null; }\n"
    "  if (id === 'flower' && gift.on && !gift.got) return [gift.x, gift.z];")
rep('<p class="ver">Version 222</p>', '<p class="ver">Version 223</p>')
open(DST, 'w').write(s)
print('ui151 ok', n0, '->', len(s))
