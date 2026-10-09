# V66, second pass: a pound's dive looks determined (not scared); the roll's tuck opens as the spin ends; the brace face doesn't linger once
# it's down; a tumble never carries over past the match; the stub on the outside of a turn plants and pushes; it glances at a rival close
# by; a hard turn at speed throws a spray of paint off its outside edge; no garbage made per frame for where it looks
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:160])
    src = src.replace(old, new)
# the face during a pound: gritted, not scared
rep("(P.air && P.vy < -7 && !P.rocket) || (P.st === 'play' && P.paint < 0.15) || P.exposed), strain = P.charging || P.rollT > 0;",
    "(P.air && P.vy < -7 && !P.rocket && !P.slam) || (P.st === 'play' && P.paint < 0.15) || P.exposed), strain = P.charging || P.rollT > 0 || P.slam;")
rep("L.V.slime.setExpression(state === 'intro' && !D.pot ? 'happy' : D.st === 'hide' ? 'peek' : slimeMood(D, F, false, scared, hunting || (D.charging && D.charge > 0.3), ahead));",
    "L.V.slime.setExpression(state === 'intro' && !D.pot ? 'happy' : D.st === 'hide' ? 'peek' : slimeMood(D, F, false, scared, hunting || (D.charging && D.charge > 0.3) || D.slam, ahead));")
# where it looks: one array each, refilled
rep("    VP.slimeLook = ES2 ? ES2.look : GL ? GL.look : VP.slimeWatchT ? VP.slimeWatchT.look : [(-look.lean * 0.07 + idleLook.x) * 1.3, ((P.air ? (P.vy > 0 ? 0.05 : -0.04) : 0) + idleLook.y) * 1.2];",
    "    const lk = VP.lookA || (VP.lookA = [0, 0]); lk[0] = (-look.lean * 0.07 + idleLook.x) * 1.3; lk[1] = ((VP.vAir ? (P.vy > 0 ? 0.05 : -0.04) : 0) + idleLook.y) * 1.2;\n"
    "    VP.slimeLook = ES2 ? ES2.look : GL ? GL.look : VP.slimeWatchT ? VP.slimeWatchT.look : lk;")
rep("L.V.slimeLook = L.V.slimeWatchT ? L.V.slimeWatchT.look : [-L.look.lean * 0.1, 0];",
    "const lk = L.V.lookA || (L.V.lookA = [0, 0]); lk[0] = -L.look.lean * 0.1; lk[1] = 0; L.V.slimeLook = L.V.slimeWatchT ? L.V.slimeWatchT.look : lk;")
# the tuck opens as the spin ends
rep("o.curl = D.st === 'play' && D.rollT > ROLL_T - ROLL_DASH - 0.03 && !D.air ? 1 : 0;", "o.curl = D.st === 'play' && D.rollT > ROLL_T - ROLL_DASH + 0.05 && !D.air ? 1 : 0;")
# the brace face: only while it's coming
rep("if ((wall > 0.45 && D.spd > 4.5) || (brace > 0.45 && (TM || D.vy < -10))) V.braceT = 0.22; else if (V.braceT > 0) V.braceT -= dt;",
    "if ((wall > 0.45 && D.spd > 4.5) || (brace > 0.45 && (TM || D.vy < -10))) V.braceT = 0.22; else if (V.braceT > 0) V.braceT = D.air ? V.braceT - dt : Math.min(V.braceT - dt, 0.06);")
# a tumble ends with the match
rep("    if (D.st !== 'play' || D.rocket || D.slam) V.tum = null;", "    if (D.st !== 'play' || D.rocket || D.slam || (state !== 'play' && state !== 'dead')) V.tum = null;")
# turning: the outside stub plants and pushes (more the harder the turn, at any pace on the ground); a rival close by gets a glance
rep("  o.shove = clamp((D === P ? idle.sway : 0) + (D.shimNow ? D.shimNow.shove : 0), -1, 1); o.push = clamp((D === P ? idle.push : 0) + (D.shimNow ? D.shimNow.push : 0), -1, 1);",
    "  const tp = live && !vAir && D.spd > 0.4 && !(D.rollT > 0) && !D.charging ? clamp(L.lean * 1.3, -1, 1) * Math.min(1, D.spd / 3) * 0.75 : 0; V.tPush = (V.tPush || 0) + (tp - (V.tPush || 0)) * Math.min(1, dt * 10);\n"
    "  o.shove = clamp((D === P ? idle.sway : 0) + (D.shimNow ? D.shimNow.shove : 0), -1, 1); o.push = clamp((D === P ? idle.push : 0) + (D.shimNow ? D.shimNow.push : 0) + V.tPush, -1, 1);\n"
    "  let gT = 0; if (live && state === 'play') { let bd = 7.5, rel = 0; for (const O of foes(D)) { if (O.st !== 'play') continue; const d = Math.hypot(O.x - D.x, O.z - D.z); if (d < bd) { const r = wrapA(Math.atan2(O.x - D.x, O.z - D.z) - V.root.rotation.y); if (Math.abs(r) < 2.2) { bd = d; rel = r; } } } if (bd < 7.5) gT = clamp(rel, -1.1, 1.1) * Math.min(1, (7.5 - bd) / 3); }\n"
    "  V.glance = (V.glance || 0) + (gT - (V.glance || 0)) * Math.min(1, dt * 6); o.glance = V.glance;")
# a hard turn at speed: paint thrown off the outside edge
rep("      if (D.spd > 2 && !D.charging) { D.dripAcc += dt * 4;",
    "      if (D.spd > 4 && Math.abs(D.turn) > TURN * 0.62 && !D.charging && !D.dry && (D === P || dp0(D) < 16)) { D.fxAcc += dt * 28 * (Math.abs(D.turn) / TURN - 0.5); while (D.fxAcc >= 1) { D.fxAcc -= 1; const sg = Math.sign(D.turn), lx = Math.cos(D.yaw) * sg, lz = -Math.sin(D.yaw) * sg, fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), r = Math.random(); spawnPart(D.x + lx * 0.3 - fx * 0.1, D.y + 0.12, D.z + lz * 0.3 - fz * 0.1, lx * (2 + 1.6 * r) - fx * (0.6 + r) + fx * D.spd * 0.25, 1 + Math.random() * 1.3, lz * (2 + 1.6 * r) - fz * (0.6 + r) + fz * D.spd * 0.25, 0.3 + 0.15 * r, tmat(D), 0.35 + 0.3 * r); } } else if (!D.missile) D.fxAcc = 0;\n"
    "      if (D.spd > 2 && !D.charging) { D.dripAcc += dt * 4;")
open(P, 'w').write(src)
print('ok', len(src))
