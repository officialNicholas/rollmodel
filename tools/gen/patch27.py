import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)

# ---- hit stop helper: a short freeze on impacts that involve you or land close by ----
rep("let hold = 0, slow = 0, fovKick = 0,", "let hold = 0, slow = 0, fovKick = 0,")
rep("function kick(el, cls) {", """function hitStop(t, A, B, x, z) { if (A === P || B === P || (x !== undefined && Math.hypot(x - P.x, z - P.z) < 14)) hold = Math.max(hold, t); }
function kick(el, cls) {""")
rep("const GIANT_T = 5, GIANT_K = 3, GIANT_SPD = 2.5, ORB_R = 0.42;", "const GIANT_T = 5, GIANT_K = 3, GIANT_SPD = 2.5, GIANT_SLAM = 1.225, ORB_R = 0.42; // a giant's pound covers 1.5x the area, then it shrinks back\nconst slamRadius = D => (D.missile ? MISSILE_R : SLAM_R) * (D.giantT > 0 ? GIANT_SLAM : 1);")

# ---- giant pound: bigger circle, huge impact, and the giant wears off ----
rep("  const missile = !!D.missile, R = missile ? MISSILE_R : SLAM_R, koR = R + PR;", "  const missile = !!D.missile, giant = D.giantT > 0, R = slamRadius(D), koR = R + PR;")
rep("""  if (D === P) { shake = missile ? 0.65 : 0.45; hold = missile ? 0.1 : 0.07; fovKick = -8; AU.slam(); if (missile) AU.burst(0.8); buzz(missile ? [30, 20, 50] : 25); flashScreen(); if (missile) popText('Missile!'); }
  else if (dp < 18) { shake = Math.max(shake, 0.4 * (1 - dp / 18)); AU.slam(); }""",
"""  if (giant) { D.giantT = 0; D.wob = 1; shockwave(D.x, D.y, D.z, R * 1.15, 0xFFFFFF); shockwave(D.x, D.y, D.z, R * 0.4, TEAMS[D.team].wet); burst(D, TEAMS[D.team].wet, 40); for (let i = 0; i < 20; i++) { const a = Math.random() * 6.283; spawnPart(D.x, D.y + 0.3, D.z, Math.cos(a) * 6, 2 + Math.random() * 4, Math.sin(a) * 6, 0.6, orbPartMats[i % orbPartMats.length], 0.7); } if (hearable(D)) { AU.burst(1); AU.shrink(); } }
  if (D === P) { shake = giant ? 0.95 : missile ? 0.65 : 0.45; hold = giant ? 0.17 : missile ? 0.1 : 0.07; fovKick = giant ? -16 : -8; AU.slam(); if (missile) AU.burst(0.8); buzz(giant ? [45, 25, 70] : missile ? [30, 20, 50] : 25); flashScreen(); if (giant) popText('Giant slam!'); else if (missile) popText('Missile!'); }
  else if (dp < (giant ? 26 : 18)) { shake = Math.max(shake, (giant ? 0.8 : 0.4) * (1 - dp / (giant ? 26 : 18))); AU.slam(); hitStop(giant ? 0.1 : 0.05, D, null, D.x, D.z); }""")
rep("aimRing.scale.setScalar((P.missile ? MISSILE_R : SLAM_R) / 0.84", "aimRing.scale.setScalar(slamRadius(P) / 0.84")
rep("cWarn.scale.setScalar((H.missile ? MISSILE_R + PR : KO_R) *", "cWarn.scale.setScalar((slamRadius(H) + PR) *")
rep("< (H.missile ? MISSILE_R + PR : KO_R) + 1)", "< slamRadius(H) + PR + 1)")
rep("if (d < (O.missile ? MISSILE_R + PR : KO_R) + 1.3", "if (d < slamRadius(O) + PR + 1.3")
# a giant CPU keeps its size for squishing rather than spending it on a coverage pound
rep("if (AI.covPound && ai.covT <= 0 && !reserve && D.dilT <= 0) {", "if (AI.covPound && ai.covT <= 0 && !reserve && D.dilT <= 0 && D.giantT <= 0) {")

# ---- hit stops on the other impacts ----
rep("  if (B === P) { shake = Math.max(shake, 0.35); buzz([20, 25, 30]); popText('Bounced!'); }", "  hitStop(0.08, A, B);\n  if (B === P) { shake = Math.max(shake, 0.35); buzz([20, 25, 30]); popText('Bounced!'); }")
rep("  if (B === P) { shake = Math.max(shake, 0.12); buzz(10); popText('Splashed!'); } else if (A === P) popText('Splashed it!');", "  hitStop(0.04, A, B);\n  if (B === P) { shake = Math.max(shake, 0.12); buzz(10); popText('Splashed!'); } else if (A === P) popText('Splashed it!');")
rep("  if (hearable(B)) AU.squish();\n", "  if (hearable(B)) AU.squish();\n  hitStop(how === 'giant' ? 0.1 : 0.07, A, B); if (how === 'giant' && (A === P || B === P)) shake = Math.max(shake, 0.45);\n")
rep("  if (O === P) { shake = Math.max(shake, 0.35); buzz([25, 30, 25]); banner('Knocked out of your coffin!'); }", "  hitStop(0.07, O, D);\n  if (O === P) { shake = Math.max(shake, 0.35); buzz([25, 30, 25]); banner('Knocked out of your coffin!'); }")
rep("  else if (dp < 20) { shake = Math.max(shake, 0.45 * (1 - dp / 20)); AU.burst(0.6); }", "  else if (dp < 20) { shake = Math.max(shake, 0.45 * (1 - dp / 20)); AU.burst(0.6); hitStop(0.05, D, null, p.x, p.z); }")
# knocking the holy water out freezes for a beat too
rep("  else { cDrop.visible = false; cShadow.visible = false; banner(", "  else { if (by === P) { hold = Math.max(hold, 0.09); shake = Math.max(shake, 0.3); } cDrop.visible = false; cShadow.visible = false; banner(")
# grabbing the orb
rep("  if (D === P) { shake = Math.max(shake, 0.3); buzz([20, 20, 40]); flashScreen(); banner('Giant!',", "  hitStop(0.08, D);\n  if (D === P) { shake = Math.max(shake, 0.3); buzz([20, 20, 40]); flashScreen(); banner('Giant!',")
# a hard slingshot landing and a fast wall bonk get a tiny one
rep("if (D === P) { AU.splat(cost / SPLAT_COST); if (fk > 0.4) { shake = Math.max(shake, 0.12 + 0.15 * fk); buzz(14); } }", "if (D === P) { AU.splat(cost / SPLAT_COST); if (fk > 0.4) { shake = Math.max(shake, 0.12 + 0.15 * fk); buzz(14); } if (fk > 0.6) hold = Math.max(hold, 0.035); }")
rep("    if (D === P) { shake = Math.max(shake, 0.05 + 0.06 * k); buzz(8); }", "    if (D === P) { shake = Math.max(shake, 0.05 + 0.06 * k); buzz(8); if (k > 0.85) hold = Math.max(hold, 0.03); }")
rep("<li><span class=\"dot ink\"></span>Now and then a glowing orb drifts around the canvas.", "<li><span class=\"dot ink\"></span>Now and then a glowing orb drifts around the canvas.")
rep("Roll into the holy water while you're giant to squish it flat.</li>", "Roll into the holy water while you're giant to squish it flat. A pound while giant splats a circle half again as big, but uses up the giant.</li>")
open(F, 'w').write(s)
print('ok')
