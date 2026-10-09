# the match starts with each blob down in a basin of its own color: in the countdown its eyes pop up out of the paint and look round,
# and at Go it leaps out onto the floor in front of the basin (a blob left without a basin still drops in from above, as before)
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

# ---- which basin each blob starts in ----
rep("const countEl = $('countN');",
"""const countEl = $('countN');
// a basin each, at random, as far apart as the basins allow (a pair closer than 9 is passed over while there's another choice)
function introBasins() {
  const cand = pots.filter(p => potUp(p) && !p.occ).sort(() => Math.random() - 0.5), got = new Map();
  for (const D of ACTIVE) { if (D.st === 'out') continue;
    const taken = [...got.values()], p = cand.find(q => taken.every(o => Math.hypot(o.x - q.x, o.z - q.z) >= 9)) || cand[0];
    if (p) { got.set(D, p); cand.splice(cand.indexOf(p), 1); } }
  return got;
}
// just up out of the paint: a look one way, then the other, then straight ahead, ready (the CPUs look the other way first)
function introWatch(D) {
  const u = introT - (D.popAt || 0), k = (a, b) => smoothstep(a, b, u), s = D === P ? 1 : D.team === 2 ? 1 : -1;
  const yaw = (0.8 * k(0.32, 0.56) - 1.55 * k(0.82, 1.1) + 0.75 * k(1.38, 1.62)) * s;
  return { yaw, pitch: 0.82 - 0.1 * Math.sin(Math.min(1, Math.max(0, u / 0.4)) * Math.PI), look: [yaw * 0.16, 0.12] };
}""")

# ---- the camera in the countdown: on your basin, from the front and a little to the side (clear of the leap) ----
rep("""  const t = Math.min(1, introT / INTRO_AT[3]), a = P.yaw + 0.55 * (1 - t) * (1 - t) + 0.12, d = 3.1 - 0.75 * t, gy = P.introY0 || 0;
  dPos.set(P.x + Math.sin(a) * d, gy + 1.15 + 0.3 * t, P.z + Math.cos(a) * d); dLook.set(P.x, P.y + INTRO_LK, P.z);""",
"""  const t = Math.min(1, introT / INTRO_AT[3]), gy = P.introY0 || 0;
  if (P.pot) { const a = P.yaw + 0.66 - 0.14 * t, d = 3.3 - 0.5 * t; dPos.set(P.x + Math.sin(a) * d, gy + 1.62 - 0.22 * t, P.z + Math.cos(a) * d); dLook.set(P.x, gy + 0.62, P.z); }
  else { const a = P.yaw + 0.55 * (1 - t) * (1 - t) + 0.12, d = 3.1 - 0.75 * t; dPos.set(P.x + Math.sin(a) * d, gy + 1.15 + 0.3 * t, P.z + Math.cos(a) * d); dLook.set(P.x, P.y + INTRO_LK, P.z); }""")

# ---- each frame of the countdown ----
rep("""  for (const D of ACTIVE) { if (D.st === 'out') continue;
    D.fV += ((D.fT - D.formK) * 170 - D.fV * 13) * Math.min(rdt, 0.033); D.formK = Math.max(0.05, D.formK + D.fV * Math.min(rdt, 0.033));""",
"""  for (const D of ACTIVE) { if (D.st === 'out') continue;
    // in a basin: up come the eyes, with a plop and a ring of paint
    if (D.pot) { if (!D.peeked && introT >= D.popAt) { const p = D.pot; D.peeked = true; p.crT = 0; p.slosh = Math.min(1.4, (p.slosh || 0) + 0.8); if (D === P) { AU.pop(); buzz(6); }
        if (Math.abs(p.x - P.x) + Math.abs(p.z - P.z) < 22) for (let i = 0; i < 8; i++) { const a = Math.random() * 6.283, sp = 0.5 + Math.random() * 0.8; spawnPart(p.x + Math.cos(a) * 0.2, p.y + 0.62, p.z + Math.sin(a) * 0.2, Math.cos(a) * sp, 1.6 + Math.random() * 1.4, Math.sin(a) * sp, 0.45, tmat(D), 0.35 + Math.random() * 0.25); } }
      continue; }
    D.fV += ((D.fT - D.formK) * 170 - D.fV * 13) * Math.min(rdt, 0.033); D.formK = Math.max(0.05, D.formK + D.fV * Math.min(rdt, 0.033));""")
rep("""      for (const D of ACTIVE) { if (D.st === 'out') continue; D.fT = [1, 0.8, 0.58][n - 1]; D.fV += 3.2; D.wob = 1; }
      // paint flying in from all round to join the drop
      for (let i = 0; i < 10; i++) {""",
"""      for (const D of ACTIVE) { if (D.st === 'out' || D.pot) continue; D.fT = [1, 0.8, 0.58][n - 1]; D.fV += 3.2; D.wob = 1; }
      // paint flying in from all round to join the drop
      if (!P.pot) for (let i = 0; i < 10; i++) {""")

# ---- Go: out of the basin with a leap (a splat where it lands, its accessories popping on) ----
rep("""  for (const D of ACTIVE) { if (D.st === 'out') continue; D.fT = 1; D.formK = Math.max(D.formK, 0.92); D.vy = -9; D.air = true; D.freeLand = true; D.wob = 0.6; }
  AU.music('play'); AU.go();""",
"""  for (const D of ACTIVE) { if (D.st === 'out') continue;
    if (D.pot) { const p = D.pot; exitPot(D); D.vy = JUMP_V * 1.12; D.spd = cfg.speed * 0.72; D.freeLand = true; D.wob = 0.7; D.squash = 0.4; p.slosh = 1.3;
      if (Math.abs(p.x - P.x) + Math.abs(p.z - P.z) < 22) for (let i = 0; i < 12; i++) { const a = Math.random() * 6.283, sp = 0.8 + Math.random() * 1.4; spawnPart(p.x + Math.cos(a) * 0.25, p.y + 0.6, p.z + Math.sin(a) * 0.25, Math.cos(a) * sp + Math.sin(D.yaw) * 1.2, 2 + Math.random() * 2, Math.sin(a) * sp + Math.cos(D.yaw) * 1.2, 0.5, tmat(D), 0.4 + Math.random() * 0.3); }
      continue; }
    D.fT = 1; D.formK = Math.max(D.formK, 0.92); D.vy = -9; D.air = true; D.freeLand = true; D.wob = 0.6; }
  AU.music('play'); AU.go();""")

# ---- the start: down in the basins ----
rep("""  for (const D of ACTIVE) { D.introY0 = Math.max(0, surfaceUnder(D.x, D.z, 3, true)); D.y = D.introY0 + INTRO_H; D.air = true; D.vy = 0; D.freeLand = true; D.stroke++; D.formK = 0.12; D.fT = 0.34; D.fV = 0; D.wob = 0.8; D.wearOff = true; }
  introCam(true);""",
"""  const basins = introBasins();
  for (const D of ACTIVE) { const p = basins.get(D); D.stroke++; D.wearOff = true; D.peeked = false;
    if (p) { const yw = potYaw(p.x, p.y, p.z); D.st = 'hide'; D.pot = p; p.occ = p.lastOcc = D; D.x = p.x; D.z = p.z; D.y = D.introY0 = p.y; D.yaw = yw !== null ? yw : Math.atan2(-p.x, -p.z); D.air = false; D.vy = 0; D.spd = 0; D.freeLand = false; D.formK = 1; D.fT = 1; D.fV = 0; D.wob = 0;
      potClaim(p, D.team); p.paintC.copy(TEAM_COLS[D.team]); p.slosh = 0; D.popAt = D === P ? 0.5 : 0.62 + Math.random() * 0.35; continue; }
    D.introY0 = Math.max(0, surfaceUnder(D.x, D.z, 3, true)); D.y = D.introY0 + INTRO_H; D.air = true; D.vy = 0; D.freeLand = true; D.formK = 0.12; D.fT = 0.34; D.fV = 0; D.wob = 0.8; }
  camYaw = P.yaw; introCam(true);""")

# ---- how it looks down there: under the paint until its eyes come up (they bob up past where they settle), shut until then ----
rep("  const inPot = D.st === 'hide'; V.sink = (V.sink || 0) + ((inPot ? 0.4 : 0) - (V.sink || 0)) * Math.min(1, dt * (inPot ? 10 : 18)); I.root.position.y = -V.sink;\n  V.slimeWatchT = inPot ? slimeWatch(D, V) : null;",
    "  const inPot = D.st === 'hide', basin = inPot && state === 'intro', under = basin && !D.peeked;\n  if (under) { V.sink = BASIN_DEEP; V.sinkV = 0; } else if (basin) { const h = Math.min(dt, 0.033); V.sinkV = (V.sinkV || 0) + ((0.4 - V.sink) * 150 - (V.sinkV || 0) * 8.5) * h; V.sink += V.sinkV * h; }\n  else V.sink = (V.sink || 0) + ((inPot ? 0.4 : 0) - (V.sink || 0)) * Math.min(1, dt * (inPot ? 10 : 18));\n  I.root.position.y = -V.sink;\n  V.slimeWatchT = basin ? introWatch(D) : inPot ? slimeWatch(D, V) : null;")
rep("const INTRO_AT = [0.4, 1.1, 1.8, 2.5], INTRO_H = 1.9, INTRO_LK = 0.4;", "const INTRO_AT = [0.4, 1.1, 1.8, 2.5], INTRO_H = 1.9, INTRO_LK = 0.4, BASIN_DEEP = 1.35;")
rep("rise, wob: Math.min(2.2, U.gWob.value) * 0.6,\n    yaw: V.root.rotation.y, aimPitch: V.turPitch || 0, speed: D.air ? 0 : D.spd, rad, look: V.slimeLook || null, hover: state === 'intro',",
    "rise, wob: Math.min(2.2, U.gWob.value) * 0.6,\n    yaw: V.root.rotation.y, aimPitch: V.turPitch || 0, speed: D.air ? 0 : D.spd, rad, look: V.slimeLook || null, hover: state === 'intro' && !D.pot,")
rep("U.gDrop.value = D.missile && D.slam ? 0 : state === 'intro' ? 0.62 + 0.08 * Math.sin(clock * 5 + D.team) : L.drop;",
    "U.gDrop.value = D.missile && D.slam ? 0 : state === 'intro' && !D.pot ? 0.62 + 0.08 * Math.sin(clock * 5 + D.team) : L.drop;")
rep("    VP.slime.setExpression(state === 'intro' ? 'happy' : P.st === 'hide' ? 'peek' : slimeMood(P, F, happy, scared, strain, false)); VP.slime.setFangs(myLook.mouth === 'fangs');\n    if (state === 'intro' && P.formK < 0.7) VP.slime.shut();",
    "    VP.slime.setExpression(state === 'intro' && !P.pot ? 'happy' : P.st === 'hide' ? 'peek' : slimeMood(P, F, happy, scared, strain, false)); VP.slime.setFangs(myLook.mouth === 'fangs');\n    if (state === 'intro' && (P.formK < 0.7 || (P.pot && !P.peeked))) VP.slime.shut();")
rep("    L.V.slime.setExpression(state === 'intro' ? 'happy' : D.st === 'hide' ? 'peek' :", "    L.V.slime.setExpression(state === 'intro' && !D.pot ? 'happy' : D.st === 'hide' ? 'peek' :")
rep("    if (state === 'intro' && D.formK < 0.7) L.V.slime.shut();", "    if (state === 'intro' && (D.formK < 0.7 || (D.pot && !D.peeked))) L.V.slime.shut();")
open(P, 'w').write(src)
print('ok')
