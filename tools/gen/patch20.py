f='/home/claude/paint-the-canvas.html'; s=open(f).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n, (a[:90], s.count(a)); s=s.replace(a,b)

# ---------- sun: more often again (still once a match at most) ----------
rep("SUN_CHANCE = 0.22,", "SUN_CHANCE = 0.45,")

# ---------- comebacks: your own mistakes cost 2 seconds, getting taken out by the holy water costs 5 ----------
rep("const OT_T = 10, MATCH_T = 90, RESPAWN_T = 5,", "const OT_T = 10, MATCH_T = 90, SELF_RESPAWN_T = 2, RESPAWN_T = 5,")
rep("  D.st = 'ko'; D.koT = RESPAWN_T; D.reason = reason;", "  D.st = 'ko'; D.koT = by ? RESPAWN_T : SELF_RESPAWN_T; D.reason = reason;")
rep("banner(KO_MSG[reason] || 'Out!', 'Back in 5'); }", "banner((reason === 'fall' && by ? 'Knocked off!' : KO_MSG[reason]) || 'Out!', 'Back in ' + Math.ceil(D.koT)); }")
rep("banner(CPU_KO_MSG[reason] || 'Holy water out!', 'Out for 5 seconds');", "banner((reason === 'fall' && by ? 'Knocked it off!' : CPU_KO_MSG[reason]) || 'Holy water out!', 'Out for ' + Math.ceil(D.koT) + (D.koT > 1.5 ? ' seconds' : ' second'));")
# a fall soon after getting slingshot by the other blob counts as their knockout
rep("    if (D.y < -5) return knockOut(D, 'fall');", "    if (D.y < -5) return knockOut(D, 'fall', D.lastHit && runT - D.lastHit.t < 3.5 ? D.lastHit.by : null);")

# ---------- slingshot landings: the harder the fling, the bigger the splat (never as big as a pound) ----------
rep("  D.air = true; D.vy = launchV(c); D.spd = launchSpd(c); D.squash = 0; D.buf = 0; D.flung = true;", "  D.air = true; D.vy = launchV(c); D.spd = launchSpd(c); D.squash = 0; D.buf = 0; D.flung = true; D.flingC = c;")
rep("""          const cost = Math.max(0, Math.min(SPLAT_COST, D.paint - 0.03)), Rr = SPLAT_R * (0.55 + 0.45 * cost / SPLAT_COST);
          if (cost > 0.005) { D.paint -= cost; addSplat(D.x, D.y, D.z, D.yaw, Rr, dryClock, false, false, D.team); splash(D, cost / SPLAT_COST); if (D === P) AU.splat(cost / SPLAT_COST); }""",
"""          const fk = D.flingC || 0, cost = Math.max(0, Math.min(SPLAT_COST, D.paint - 0.03)), Rr = SPLAT_R * (0.55 + 0.45 * cost / SPLAT_COST) * (1 + 1.25 * fk);
          if (cost > 0.005) { D.paint -= cost; addSplat(D.x, D.y, D.z, D.yaw, Rr, dryClock, false, false, D.team); splash(D, cost / SPLAT_COST * (1 + fk)); if (D === P) { AU.splat(cost / SPLAT_COST); if (fk > 0.4) { shake = Math.max(shake, 0.12 + 0.15 * fk); buzz(14); } } if (fk > 0.25) shockwave(D.x, D.y, D.z, Rr * 1.1, TEAMS[D.team].wet); }""")
rep("      if (D.buf > 0) jump(D);\n    }\n    if (D.y < -5)", "      D.flingC = 0;\n      if (D.buf > 0) jump(D);\n    }\n    if (D.y < -5)")

# ---------- the missile: pound in the middle of a slingshot and you dive in at speed for an even bigger splash ----------
rep("  if (D.air) { D.slam = true; D.vy = Math.max(D.vy, 3); D.slamHang = 0.1; D.spd = 0; D.turn = 0; D.buf = 0; if (hearable(D)) AU.whoosh(); }",
    "  if (D.air && (D.flingC || 0) > 0.15) { D.slam = true; D.missile = true; D.vy = Math.min(D.vy, -5); D.slamHang = 0; D.spd = Math.max(D.spd * 0.95, cfg.speed * 1.3); D.turn = 0; D.buf = 0; if (hearable(D)) { AU.whoosh(); AU.fling(1); } if (D === P) { fovKick = 14; shake = Math.max(shake, 0.15); } }\n  else if (D.air) { D.slam = true; D.vy = Math.max(D.vy, 3); D.slamHang = 0.1; D.spd = 0; D.turn = 0; D.buf = 0; if (hearable(D)) AU.whoosh(); }")
rep("  else if (D.slam || D.flatT > 0) D.spd = 0;", "  else if ((D.slam && !D.missile) || D.flatT > 0) D.spd = 0;")
rep("""    if (D.slam && D.vy <= 0 && D.slamHang > 0) { D.slamHang -= dt; D.vy = 0; if (D.slamHang <= 0) D.vy = -20; }""",
"""    if (D.missile) { D.fxAcc += dt * 70; while (D.fxAcc >= 1) { D.fxAcc -= 1; const a = Math.random() * 6.283, fx = Math.sin(D.yaw), fz = Math.cos(D.yaw); spawnPart(D.x - fx * 0.3 + Math.cos(a) * 0.12, D.y + 0.3 + Math.random() * 0.2, D.z - fz * 0.3 + Math.sin(a) * 0.12, -fx * 2 + Math.cos(a) * 0.8, 1.5 + Math.random(), -fz * 2 + Math.sin(a) * 0.8, 0.45 + Math.random() * 0.25, tmat(D), 0.7 + Math.random() * 0.6); } }
    if (D.slam && D.vy <= 0 && D.slamHang > 0) { D.slamHang -= dt; D.vy = 0; if (D.slamHang <= 0) D.vy = -20; }""")
rep("""function slamLand(D) {
  D.slam = false; D.squash = 1; D.spd = 0;
  const hitP = rivals.filter(r => r.on && Math.abs(r.y - D.y) < 0.3 && Math.hypot(r.x - D.x, r.z - D.z) < SLAM_R * 0.5 + r.rad);""",
"""function slamLand(D) {
  const missile = !!D.missile, R = missile ? MISSILE_R : SLAM_R, koR = R + PR;
  D.slam = false; D.missile = false; D.flingC = 0; D.squash = 1; D.spd = 0;
  const hitP = rivals.filter(r => r.on && Math.abs(r.y - D.y) < 0.3 && Math.hypot(r.x - D.x, r.z - D.z) < R * 0.5 + r.rad);""")
rep("  addSplat(D.x, D.y, D.z, D.yaw, SLAM_R, dryClock, false, true, D.team); shockwave(D.x, D.y, D.z, SLAM_R, D === P ? 0xFFFFFF : 0xBFE3FF); shockwave(D.x, D.y, D.z, SLAM_R * 0.6); splash(D, 2); burst2(D, 30);",
    "  addSplat(D.x, D.y, D.z, D.yaw, R, dryClock, false, true, D.team); shockwave(D.x, D.y, D.z, R, D === P ? 0xFFFFFF : 0xBFE3FF); shockwave(D.x, D.y, D.z, R * 0.6); splash(D, missile ? 3.5 : 2); burst2(D, missile ? 50 : 30);\n  if (missile) { shockwave(D.x, D.y, D.z, R * 0.82, TEAMS[D.team].wet); burst(D, TEAMS[D.team].wet, 30); }")
rep("  if (D === P) { shake = 0.45; hold = 0.07; fovKick = -8; AU.slam(); buzz(25); flashScreen(); }", "  if (D === P) { shake = missile ? 0.65 : 0.45; hold = missile ? 0.1 : 0.07; fovKick = -8; AU.slam(); if (missile) AU.burst(0.8); buzz(missile ? [30, 20, 50] : 25); flashScreen(); if (missile) popText('Missile!'); }")
rep("  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < KO_R && Math.abs(O.y - D.y) < 1.4) knockOut(O, O.st === 'hide' ? 'coffin' : 'pound', D);\n}",
    "  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < koR && Math.abs(O.y - D.y) < 1.4) knockOut(O, O.st === 'hide' ? 'coffin' : 'pound', D);\n}")
rep("const SPLAT_R = 1.6, SPLAT_COST = 0.08, SLAM_R = 5,", "const SPLAT_R = 1.6, SPLAT_COST = 0.08, SLAM_R = 5, MISSILE_R = 6.75,")
# the warning ring under a diving holy water shows the bigger circle
rep("cWarn.scale.setScalar(KO_R * (0.94 + 0.06 * Math.sin(clock", "cWarn.scale.setScalar((H.missile ? MISSILE_R + PR : KO_R) * (0.94 + 0.06 * Math.sin(clock")
rep("(H.slam && Math.hypot(H.x - P.x, H.z - P.z) < KO_R + 1)", "(H.slam && Math.hypot(H.x - P.x, H.z - P.z) < (H.missile ? MISSILE_R + PR : KO_R) + 1)")

# ---------- slingshot into each other: the one you hit goes flying (off the edge, if you aim it right) ----------
rep("""  const dx = H.x - P.x, dz = H.z - P.z, d = Math.hypot(dx, dz), dy = H.y - P.y;
  if (d > PR * 2 || Math.abs(dy) > 0.95) return;""", """  const dx = H.x - P.x, dz = H.z - P.z, d = Math.hypot(dx, dz), dy = H.y - P.y;
  if (d > PR * 2 + 0.15 || Math.abs(dy) > 1.0) return;
  for (const [A, B] of [[P, H], [H, P]]) if (A.flung && !A.slam && A.spd > cfg.speed * speedMul * 1.15 && B.immuneT <= 0 && !(A.air && A.vy < -0.5 && A.y > B.y + 0.25)) return shove(A, B);
  if (d > PR * 2 || Math.abs(dy) > 0.95) return;""")
rep("// two blobs touching: land on top or hit harder to flatten, otherwise bounce apart", """function shove(A, B) {
  const a = Math.atan2(B.x - A.x, B.z - A.z), sx = Math.sin(A.yaw) * 0.6 + Math.sin(a) * 0.4, sz = Math.cos(A.yaw) * 0.6 + Math.cos(a) * 0.4;
  if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }
  B.yaw = Math.atan2(sx, sz); B.spd = Math.min(13, A.spd * 0.85 + 3); B.vy = 6.8; B.air = true; B.slam = false; B.missile = false; B.flatT = 0; B.turn = 0; B.wob = 1; B.squash = 0.8; B.stroke++; B.knockT = 0.9; B.flung = false; B.flingC = 0;
  B.lastHit = { by: A, t: runT };
  A.spd *= 0.3; A.vy = Math.max(A.vy, 3.5); A.air = true; A.flung = false; A.flingC = 0; A.wob = 1; A.squash = 0.6;
  shockwave(B.x, B.y, B.z, 1.7, TEAMS[A.team].wet);
  for (let i = 0; i < 20; i++) { const b = Math.random() * 6.283; spawnPart(B.x, B.y + 0.4, B.z, Math.cos(b) * 3.6, 1.5 + Math.random() * 2.5, Math.sin(b) * 3.6, 0.5, i % 2 ? tmat(A) : tmat(B), 0.75); }
  if (hearable(A) || hearable(B)) { AU.bonk(1); AU.whoosh(); }
  if (B === P) { shake = Math.max(shake, 0.35); buzz([20, 25, 30]); popText('Bounced!'); }
  else if (A === P) { shake = Math.max(shake, 0.25); buzz(18); popText('Bounced it!'); }
}
// two blobs touching: land on top or hit harder to flatten, otherwise bounce apart""")
# a blob that just got bounced has little air control
rep("  else steerAndTurn(D, dt, D.slam ? 0 : D.air ? 0.65 : D.charging ? 0.75 : 1);", "  else steerAndTurn(D, dt, D.slam ? 0 : D.air ? (D.knockT > 0 ? 0.12 : 0.65) : D.charging ? 0.75 : 1);\n  if (D.knockT > 0) D.knockT -= dt;")

# ---------- the CPU: when it has its pound and blood to spare, it comes at you ----------
rep("function aiReset(D) { D.ai = { om:", "function aiReset(D) { D.ai = { attackT: 0, attackRoll: 0, om:")
rep("""  if (oKnown && o.imm <= 0.5) {
    const od = Math.hypot(o.x - D.x, o.z - D.z), behind = lead > 0;""", """  // feeling confident (pound ready, blood to spare, you in sight and in reach): every few seconds it may decide to come at you
  const confident = slamReady(D) && D.paint > Math.max(0.45, need + 0.15) && !sunNow && oKnown;
  ai.attackRoll -= AI.think;
  if (confident && ai.attackT <= 0 && ai.attackRoll <= 0) { ai.attackRoll = 2.5; if (Math.random() < Math.min(0.75, AI.hunt * 2)) ai.attackT = 3.5 + Math.random() * 1.5; }
  if (ai.attackT > 0) ai.attackT -= AI.think;
  if (!confident) ai.attackT = 0;
  if (oKnown && o.imm <= 0.5) {
    const od = Math.hypot(o.x - D.x, o.z - D.z), behind = lead > 0;""")
rep("    if (slamReady(D) && pd < 14 && (o.flat > 0.4 || Math.random() < AI.hunt * aggro || (stuck && Math.random() < AI.ram))) {",
    "    if (slamReady(D) && pd < (ai.attackT > 0 ? 18 : 14) && (o.flat > 0.4 || ai.attackT > 0 || Math.random() < AI.hunt * aggro || (stuck && Math.random() < AI.ram))) {")
rep("if (oThreat && AI.evade > 0 && ai.mode !== 'hunt') NAV.near(", "if (oThreat && AI.evade > 0 && ai.mode !== 'hunt' && !(slamReady(D) && D.paint > 0.45)) NAV.near(")
# hard knocks you off the edge: if you're near a drop, it slingshots into you from the other side
rep("    // with a model of you, aim for where you're going to be, not where you are", """    if (AI.model > 0.8 && AI.flingAtk && od > 3.5 && od < 10 && D.paint > need + 0.12 && Math.random() < 0.35) {
      const ux = (o.x - D.x) / od, uz = (o.z - D.z) / od; let drop = false;
      for (let k = 1; k <= 7; k++) { const x = o.x + ux * k * 0.6, z = o.z + uz * k * 0.6; if (blockedAt(x, z, o.y)) break; if (surfaceUnder(x, z, o.y + 0.3) === -Infinity) { drop = true; break; } }
      if (drop) { const yaw = Math.atan2(o.x - D.x, o.z - D.z), c = solveFling(Math.max(1, od - 1.2), D.y - o.y); if (c > 0 && flingLanding(D, yaw, c)) { ai.plan = { kind: 'shove', yaw, c, t: 0 }; ai.mode = 'hunt'; return; } }
    }
    // with a model of you, aim for where you're going to be, not where you are""")
rep("  if (pl.kind === 'evict' && other(D).st !== 'hide') { ai.plan = null; if (D.charging) cancelCharge(D); return; }",
    "  if (pl.kind === 'evict' && other(D).st !== 'hide') { ai.plan = null; if (D.charging) cancelCharge(D); return; }\n  if (pl.kind === 'shove' && other(D).st !== 'play') { ai.plan = null; if (D.charging) cancelCharge(D); return; }")
# from the air: a missile reaches farther
rep("if (!D.slam && slamReady(D) && d < AI.poundR * 0.85 && D.vy < 2 &&", "if (!D.slam && slamReady(D) && d < ((D.flingC || 0) > 0.15 ? MISSILE_R + PR - 1.2 : AI.poundR * 0.85) && D.vy < 2 &&")
open(f,'w').write(s)
print('patched')
