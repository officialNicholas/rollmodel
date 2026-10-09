import sys, re
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ---------- one rule for "can't be touched": rolling, or mid air-dash ----------
rep("airSling: false, kod: 0,", "airSling: false, dashT: 0, dashDir: 0, kod: 0,")
rep("const canAct = D => D.st === 'play' && D.flatT <= 0 && !(D.stunT > 0);", "const canAct = D => D.st === 'play' && D.flatT <= 0 && !(D.stunT > 0);\nconst safe = D => D.rollT > 0 || D.dashT > 0; // untouchable: rolling, or in an air dash")
rep("  if (O.rollT > 0) { shockwave(O.x, O.y, O.z, 1.4, 0xFFFFFF); hitStop(0.06, O, D); }", "  if (safe(O)) { shockwave(O.x, O.y, O.z, 1.4, 0xFFFFFF); hitStop(0.06, O, D); }")
rep("if (!t || t.O.rollT > 0) return;", "if (!t || safe(t.O)) return;")
rep("{ if (O.rollT > 0) dodgedPound(O, D); else burstPush(O, p, D); }", "{ if (safe(O)) dodgedPound(O, D); else burstPush(O, p, D); }")
rep("if (B.st === 'play' && !B.air && B.immuneT <= 0 && !(B.rollT > 0) && B.giantT <= 0", "if (B.st === 'play' && !B.air && B.immuneT <= 0 && !safe(B) && B.giantT <= 0")
rep("if (lift > 0.6 || O.rollT > 0) dodgedPound(O, D);", "if (lift > 0.6 || safe(O)) dodgedPound(O, D);")
rep("if (B.st !== 'play' || B.immuneT > 0 || B.rollT > 0 || B.slam", "if (B.st !== 'play' || B.immuneT > 0 || safe(B) || B.slam")
s = s.replace("B.immuneT <= 0 && !(B.rollT > 0)", "B.immuneT <= 0 && !safe(B)")
rep("O.immuneT <= 0 && !(O.rollT > 0) && Math.abs(O.y - D.y) < 0.8)", "O.immuneT <= 0 && !safe(O) && Math.abs(O.y - D.y) < 0.8)")
rep("  if (D.rollT > 0 && D.st === 'play' && Math.random() < dt * 45) spawnPart(", "  if (D.dashT > 0) D.dashT -= dt;\n  if (safe(D) && D.st === 'play' && Math.random() < dt * 45) spawnPart(")
rep("    if (P.rollT > 0 && P.st === 'play') tmpCol.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));", "    if (safe(P) && P.st === 'play') tmpCol.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));")
rep("    if (D.rollT > 0 && D.st === 'play') tmpCol2.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));", "    if (safe(D) && D.st === 'play') tmpCol2.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));")

# ---------- out of a coffin, mid-air: dash forward or back instead of a slingshot ----------
rep("// swipe up: a quick forward roll.", """// out of a coffin, mid-air: a quick dash forward (swipe up) or back (swipe down), about as far as the old mid-air sling went,
// low and fast, and untouchable for a moment. You keep facing the same way either way.
const DASH_T = 0.35, DASH_C = 0.75;
function airDash(D, dir) {
  if (!(D.st === 'play' && D.air && D.airSling && canAct(D)) || D.slam) return false;
  if (D.charging) clearCharge(D);
  const s = airShot(D, DASH_C, dir > 0 ? D.yaw : D.yaw + Math.PI), dist = Math.hypot(s.x - D.x, s.z - D.z), vy = 2.6, gy = s.y > -Infinity ? s.y : D.y - 2;
  const up = vy / GRAV, ap = D.y + vy * vy / (2 * GRAV), T = up + Math.sqrt(2 * Math.max(0.05, ap - gy) / (GRAV * 1.45));
  D.airSling = false; D.vy = vy; D.spd = dist / Math.max(0.2, T); D.kx = D.kz = 0; D.dashDir = dir; D.dashT = DASH_T; D.turn = 0; D.buf = 0; D.squash = 0.35; D.wob = 1;
  const mx = Math.sin(D.yaw) * dir, mz = Math.cos(D.yaw) * dir;
  for (let i = 0; i < 12; i++) { const sd = (Math.random() - 0.5) * 2; spawnPart(D.x - mx * 0.3, D.y + 0.3, D.z - mz * 0.3, -mx * 2.6 + mz * sd, 0.4 + Math.random(), -mz * 2.6 - mx * sd, 0.4, i % 3 ? tmat(D) : puHaloMat, 0.55); }
  if (hearable(D)) AU.dash();
  if (D === P) { buzz(10); fovKick = Math.max(fovKick, 5); }
  return true;
}
// swipe up: a quick forward roll.""")
rep("  if (!canAct(D) || D.slam || D.rollT > 0) return false;\n  if (D.air) { D.rollBuf = 0.18; return false; }",
    "  if (!canAct(D) || D.slam || D.rollT > 0) return false;\n  if (D.air && D.airSling) return airDash(D, 1);\n  if (D.air) { D.rollBuf = 0.18; return false; }")
# no more charging up in the air
rep("  if (D.st !== 'hide' && (!canAct(D) || (D.air && !D.airSling))) return;", "  if (D.st !== 'hide' && (!canAct(D) || D.air)) return;")
# a back dash moves you backwards (you don't turn around), and doesn't slide you along walls or curl toward the orb
rep("  const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), d = D.spd * dt, x0 = D.x, z0 = D.z, kx = D.kx * dt, kz = D.kz * dt;",
    "  const back = D.dashDir < 0 && D.air, fx = Math.sin(D.yaw) * (back ? -1 : 1), fz = Math.cos(D.yaw) * (back ? -1 : 1), d = D.spd * dt, x0 = D.x, z0 = D.z, kx = D.kx * dt, kz = D.kz * dt;")
rep("  if (!hit || D.slam || D.charging || D.bonkCD > 0 || D.spd < 0.3) return;", "  if (!hit || D.slam || D.charging || back || D.bonkCD > 0 || D.spd < 0.3) return;")
rep("if ((!D.ai || D.ai.mode === 'orb') && orb.on && D.giantT <= 0 && !D.slam) orbHome(D, dt); }", "if ((!D.ai || D.ai.mode === 'orb') && orb.on && D.giantT <= 0 && !D.slam && D.dashDir >= 0) orbHome(D, dt); }")
rep("      D.y = g; D.vy = 0; D.air = false; D.coyote = 0; D.squash = 0.6 + 0.4 * impact; D.airSling = false;", "      D.y = g; D.vy = 0; D.air = false; D.coyote = 0; D.squash = 0.6 + 0.4 * impact; D.airSling = false; D.dashDir = 0;")
rep("hint('airsling', say('Pull on the way down to sling again', 'Hold S on the way down to sling again'), 2.8);", "hint('airdash', say('Swipe up or down to dash', 'Shift or S to dash'), 2.6);")
rep("  D.st = 'ko'; D.rollT = 0;", "  D.st = 'ko'; D.dashT = 0; D.dashDir = 0; D.rollT = 0;")

# controls: a flick down mid-air dashes back; holding and pulling no longer charges a shot up there
rep("  if (!t.rolled && (!P.charging || (holdCharge && pullTgt < 0.05)) && state === 'play') { const h0 = t.hist[0], up = h0[1] - e.clientY; if (up > 44 && up > Math.abs(e.clientX - h0[0]) * 1.5) { t.rolled = true; t.moved = true; t.steered = true; dodgeRoll(P); } }",
    "  if (!t.rolled && (!P.charging || (holdCharge && pullTgt < 0.05)) && state === 'play') { const h0 = t.hist[0], up = h0[1] - e.clientY, side = Math.abs(e.clientX - h0[0]); if (up > 44 && up > side * 1.5) { t.rolled = true; t.moved = true; t.steered = true; dodgeRoll(P); } else if (P.air && P.airSling && -up > 44 && -up > side * 1.5) { t.rolled = true; t.moved = true; t.steered = true; airDash(P, -1); } }")
rep("  if (!P.charging && !t.steered && dy > 18 && dy > Math.abs(sx) * 1.4 && state === 'play' && (P.st === 'play' || P.st === 'hide')) beginHold(t, t.x, t.y);",
    "  if (!P.charging && !t.steered && dy > 18 && dy > Math.abs(sx) * 1.4 && state === 'play' && (P.st === 'play' || P.st === 'hide') && !P.air) beginHold(t, t.x, t.y);")
rep("  if (t && !t.moved && performance.now() - t.t > HOLD_MS && state === 'play' && (P.st === 'play' || P.st === 'hide')) beginHold(t, t.cx, t.cy);",
    "  if (t && !t.moved && performance.now() - t.t > HOLD_MS && state === 'play' && (P.st === 'play' || P.st === 'hide') && !P.air) beginHold(t, t.cx, t.cy);")
rep("  else if ((k === 'ArrowDown' || k === 's' || k === 'S') && !e.repeat) { e.preventDefault(); if (state === 'play') startCharge(P);",
    "  else if ((k === 'ArrowDown' || k === 's' || k === 'S') && !e.repeat) { e.preventDefault(); if (state === 'play' && P.air && P.airSling) { airDash(P, -1); return; } if (state === 'play') startCharge(P);")

# the holy water: out of a coffin it dashes forward or back if either lands somewhere better than drifting
i = s.index("function aiAirSling(D, dt) {"); j = s.index("function aiAir(D, dt) {")
s = s[:i] + r"""function aiAirSling(D, dt) {
  const ai = D.ai;
  if (D.vy > 3 || ai.airRolled) return false;
  ai.airRolled = true; if (Math.random() > AI.airSling) return false;
  const O = other(D), o = ai.o, near = o && o.st === 'play' && runT - o.t < 1 && !(o.imm > 0.3);
  const fall = (x, z) => { const g = surfaceUnder(x, z, D.y + STEP, true); if (g === -Infinity || g > D.y - 0.2) return null; for (let a = 0; a < 6.28; a += 1.05) if (surfaceUnder(x + Math.sin(a) * 1.1, z + Math.cos(a) * 1.1, D.y + STEP, true) === -Infinity) return null; if (rivals.some(r => r.on && Math.abs(r.y - g) < 0.3 && Math.hypot(x - r.x, z - r.z) < r.hit + 0.5)) return null; return g; };
  const score = (x, z, g) => localGain({ team: D.team, x, z, y: g }, 2.2) + (near && O.slamCD <= 0.5 ? Math.min(12, Math.hypot(x - o.x, z - o.z)) * 3 : 0);
  const tF = (D.vy + Math.sqrt(Math.max(0, D.vy * D.vy + 2 * GRAV * 1.45 * 6))) / (GRAV * 1.45), dx0 = D.x + Math.sin(D.yaw) * D.spd * Math.min(tF, 1.4), dz0 = D.z + Math.cos(D.yaw) * D.spd * Math.min(tF, 1.4), g0 = fall(dx0, dz0);
  let best = 0, bs = (g0 === null ? -1e9 : score(dx0, dz0, g0)) + 6;
  for (const dir of [1, -1]) { const sh = airShot(D, DASH_C, dir > 0 ? D.yaw : D.yaw + Math.PI), g = fall(sh.x, sh.z); if (g === null) continue; const sc = score(sh.x, sh.z, g); if (sc > bs) { bs = sc; best = dir; } }
  if (!best) return false;
  return airDash(D, best);
}
""" + s[j:]

# how to play
rep("""        <li><span class="dot sun"></span>""", """        <li><span class="dot hand">⇅</span><span>Burst out of a coffin, then swipe up or down in mid-air to dash forward or back. You can't be touched while you dash.</span></li>
        <li><span class="dot sun"></span>""")
open(F, 'w').write(s)
print('ok')
s = open(F).read()
a = "  shockwave(D.x, D.y, D.z, R * 0.82, TEAMS[D.team].wet); shockwave(D.x, D.y, D.z, R * 1.25, 0xFFD27A);\n}"
assert s.count(a) == 1
s = s.replace(a, "  shockwave(D.x, D.y, D.z, R * 0.82, TEAMS[D.team].wet); shockwave(D.x, D.y, D.z, R * 1.25, 0xFFD27A);\n  spawnCrown(D, R * 0.9); // the paint crown a giant's pound throws up, sized to the missile's blast (the blast itself is unchanged)\n}")
open(F, 'w').write(s); print('crown ok')
