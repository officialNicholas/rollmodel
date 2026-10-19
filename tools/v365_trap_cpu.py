"""v365: CPUs run over paint traps: an easy one about 65% of the time it comes to one, a medium one 40%, a hard one 25%.

- Before, a CPU's steering never took traps into account, and one heading straight at a trap rolled through it harmlessly (30% of the
  time on easy, 55% on medium, 80% on hard). So it only ever got caught when its way happened to cross a trap dead centre and it didn't
  roll, which was rarely.
- Now the first time a rival's trap lies ahead of a CPU rolling along (within TRAP_SEE, and within TRAP_LANE of the line it's on, with
  nothing in between), it rolls the dice once, by its level (TRAP_CATCH). It hasn't seen it: it rolls straight on over it (no hop, roll,
  fling or pound on the way), bending its line a little if the trap is off to one side. Or it has: it steers round it, and rolls through
  it if it's still dead ahead at the last moment (or hops it, with no roll to hand). Once it's well past it forgets, so the next time it
  comes that way is a new roll.
- Its slingshot flings go by the same dice: it won't fling itself onto (or slide over) a rival's trap unless that trap has caught it out.
  (Before, its flings didn't look out for traps at all, so one flung at you could land on the trap you'd just dropped.)
- A giant, a rocket or a CPU in the air is left as it was (a giant or a roll sets a trap off harmlessly; a jump clears it)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "// they're stunned and popped up. A dodge roll through it sets it off harmlessly (a CPU heading for one sometimes knows to); your own can't\n",
               "// they're stunned and popped up. A dodge roll through it sets it off harmlessly (v365: a CPU coming to one has seen it or not: TRAP_CATCH); your own can't\n")
    s = rep(s, "const TRAP_R = 0.92, TRAP_ARM = 0.6, TRAP_LIFE = 45, TRAP_MAX = 2, TRAP_STUN = 1.5, TRAP_SPLAT = SPLAT_R * 1.7;\n",
               "const TRAP_R = 0.92, TRAP_ARM = 0.6, TRAP_LIFE = 45, TRAP_MAX = 2, TRAP_STUN = 1.5, TRAP_SPLAT = SPLAT_R * 1.7;\n"
               "// (v365) a CPU coming to a trap: the first time a rival's lies ahead of it (within TRAP_SEE, and within TRAP_LANE of the line it's rolling\n"
               "// along), it either hasn't seen it, TRAP_CATCH of the time by its level, and rolls on over it, or it has, and goes round it (or rolls\n"
               "// through it or hops it, if it's still dead ahead at the last moment). Once it's well past it forgets, so the next time it comes that way is a\n"
               "// new roll\n"
               "const TRAP_CATCH = { easy: 0.65, medium: 0.4, hard: 0.25 }, TRAP_SEE = 4.2, TRAP_LANE = 1.8;\n")
    s = rep(s, "arm: TRAP_ARM, t: 0, code: tcode(D), dec: {}, seen: false,", "arm: TRAP_ARM, t: 0, code: tcode(D), mind: new Map(), seen: false,")
    s = rep(s, "      // a CPU heading straight for it may roll through (more often the harsher the critics)\n"
               "      if (D.ai && !D.air && !(D.rollT > 0) && d < 1.7 && d > TRAP_R && D.spd > 1.2 && Math.abs(wrapA(Math.atan2(-dx, -dz) - D.yaw)) < 0.6) { const k = 'r' + D.team; if (T.dec[k] === undefined) T.dec[k] = Math.random() < (diff === 'easy' ? 0.3 : diff === 'hard' ? 0.8 : 0.55); if (T.dec[k]) dodgeRoll(D); }\n",
               "      if (D.cpu && D.ai) trapMind(T, D, dx, dz, d); // (v365: has it seen it or not)\n")
    s = rep(s, "function trapPop(T, B, harmless) {\n  const i = trapList.indexOf(T); if (i >= 0) trapList.splice(i, 1); scene.remove(T.g);\n",
               "// (v365) what a CPU makes of a trap it's coming to (TRAP_CATCH): caught out, it's drawn on over it (aiLure); seen, it steers round it\n"
               "// (hazardAt) and rolls through if it's still dead ahead at the last moment, or hops it if its roll isn't back yet\n"
               "function trapMind(T, D, dx, dz, d) {\n"
               "  let c = T.mind.get(D);\n"
               "  if (c !== undefined && d > TRAP_SEE + 1.5) { trapForget(T, D); c = undefined; } // (well past it: the next time is a new roll)\n"
               "  if (c === undefined) {\n"
               "    if (D.air || D.charging || D.giantT > 0 || D.rollT > 0 || D.spd < 1.5 || d > TRAP_SEE || Math.abs(D.y - T.y) > 0.6) return;\n"
               "    const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw);\n"
               "    if (-(dx * fx + dz * fz) < 0.3 || Math.abs(dx * fz - dz * fx) > TRAP_LANE || !lineClear(D, T.x, T.z, T.y)) return; // (ahead, in its lane, nothing in between)\n"
               "    c = Math.random() < (TRAP_CATCH[diff] || TRAP_CATCH.medium); T.mind.set(D, c);\n"
               "    if (!c) (D.ai.avoid || (D.ai.avoid = [])).push(T);\n"
               "  }\n"
               "  if (c) { if (!D.ai.lure) D.ai.lure = T; }\n"
               "  else if (!D.air && !(D.rollT > 0) && d < 1.7 && d > TRAP_R && D.spd > 1.2 && Math.abs(wrapA(Math.atan2(-dx, -dz) - D.yaw)) < 0.6) { if (D.rollCD <= 0 && rollSafe(D)) dodgeRoll(D); else if (d < 1.5 && hopOK(D)) jump(D); } // (no roll to hand: a hop clears it)\n"
               "}\n"
               "// a trap gone, or a CPU well past one: out of its mind (only: that CPU's), its steering and what it's heading for\n"
               "function trapForget(T, only) {\n"
               "  if (only) T.mind.delete(only);\n"
               "  for (const B of only ? [only] : [P, H, H2, H3]) { const ai = B && B.ai; if (!ai) continue; if (ai.lure === T) ai.lure = null; const j = ai.avoid ? ai.avoid.indexOf(T) : -1; if (j >= 0) ai.avoid.splice(j, 1); }\n"
               "}\n"
               "function trapPop(T, B, harmless) {\n  const i = trapList.indexOf(T); if (i >= 0) trapList.splice(i, 1); scene.remove(T.g); trapForget(T);\n")
    s = rep(s, "function clearTraps() { for (const T of trapList) scene.remove(T.g); trapList.length = 0; }",
               "function clearTraps() { for (const T of trapList) { scene.remove(T.g); trapForget(T); } trapList.length = 0; }")
    # ---- seen it: the CPU's look ahead counts it as trouble, so it bends its way round
    s = rep(s, "  let y = D.y, score = 0;\n  for (let d = 0.3; d <= end + 1e-6; d += 0.3) {\n",
               "  let y = D.y, score = 0; const av = D.ai.avoid && D.ai.avoid.length ? D.ai.avoid : null; // (v365: traps it has seen)\n  for (let d = 0.3; d <= end + 1e-6; d += 0.3) {\n")
    s = rep(s, "    if (avoidPots) for (const p of pots) if (potUp(p) && !p.occ && p.ink > 0.02 && p.cool <= 0 && Math.hypot(x - p.x, z - p.z) < 0.85 && Math.abs(p.y - s) < 0.5) { score += 4 * w * 0.5; break; }\n",
               "    if (avoidPots) for (const p of pots) if (potUp(p) && !p.occ && p.ink > 0.02 && p.cool <= 0 && Math.hypot(x - p.x, z - p.z) < 0.85 && Math.abs(p.y - s) < 0.5) { score += 4 * w * 0.5; break; }\n"
               "    if (av) for (const T of av) if (Math.abs(T.y - s) < 0.6 && Math.hypot(x - T.x, z - T.z) < TRAP_R + 0.45) { score += 5 * w * 0.5; break; }\n")
    # ---- a fling that would land on (or slide over) a rival's trap: only for a CPU it has caught out (by the same dice, rolling up to it)
    s = rep(s, "      for (let d = 0.3; d <= slide; d += 0.3) { const px = x + sx * d, pz = z + sz * d; if (blockedAt(px, pz, sy)) break; const s2 = surfaceUnder(px, pz, sy + STEP); if (s2 === -Infinity) return null; sy = s2; }\n      return { x, z, y: g, t, n };\n",
               "      for (let d = 0.3; d <= slide; d += 0.3) { const px = x + sx * d, pz = z + sz * d; if (blockedAt(px, pz, sy)) break; const s2 = surfaceUnder(px, pz, sy + STEP); if (s2 === -Infinity) return null; sy = s2; }\n"
               "      if (trapList.length && !trapLandOK(D, x, z, g, sx, sz, slide)) return null; // (v365)\n"
               "      return { x, z, y: g, t, n };\n")
    s = rep(s, "const m = missileFrom(ax, D.y + f.ap, az, yaw, hh, MISSILE_DIVE, 0.08); if (!m || !safeLand(m.x, m.z, m.y)) continue;",
               "const m = missileFrom(ax, D.y + f.ap, az, yaw, hh, MISSILE_DIVE, 0.08); if (!m || !safeLand(m.x, m.z, m.y) || (trapList.length && !trapLandOK(D, m.x, m.z, m.y, Math.sin(yaw), Math.cos(yaw), 0.6))) continue;")
    s = rep(s, "function flingLanding(D, yaw, c, bold) {\n",
               "// (v365) a CPU's fling lands on (or slides over) a rival's trap only if that trap has caught it out (TRAP_CATCH, rolling up to it): one it\n"
               "// has seen, or hasn't come to yet, it doesn't fling onto\n"
               "function trapLandOK(D, x, z, y, sx, sz, slide) {\n"
               "  for (const T of trapList) {\n"
               "    if (T.owner === D || ally(D, T.owner) || Math.abs(T.y - y) > 0.6 || T.mind.get(D) === true) continue;\n"
               "    for (let d = 0; d <= slide + 1e-6; d += 0.5) if (Math.hypot(x + sx * d - T.x, z + sz * d - T.z) < TRAP_R + 0.5) return false;\n"
               "  }\n"
               "  return true;\n"
               "}\n"
               "function flingLanding(D, yaw, c, bold) {\n")
    # ---- not seen it: on over it
    s = rep(s, "// get clear of your pound, or hop over a ram\n",
               "// (v365) caught out by a trap it hasn't seen: it rolls straight on over it, no hop, roll, fling or pound on the way (it lets go if the\n"
               "// trap goes, or it's carried off or somehow past it)\n"
               "function aiLure(D, dt) {\n"
               "  const ai = D.ai, T = ai.lure, dx = T.x - D.x, dz = T.z - D.z, d = Math.hypot(dx, dz);\n"
               "  if (!trapList.includes(T) || D.giantT > 0 || d > TRAP_SEE + 1 || Math.abs(D.y - T.y) > 0.8 || (d > TRAP_R && Math.sin(D.yaw) * dx + Math.cos(D.yaw) * dz < -0.3) || !lineClear(D, T.x, T.z, T.y)) { ai.lure = null; return false; }\n"
               "  if (D.charging) cancelCharge(D); ai.plan = null; ai.rollWind = 0; ai.evadeT = 0;\n"
               "  D.steer = -clamp(wrapA(Math.atan2(dx, dz) - D.yaw) * 2.6, -1, 1);\n"
               "  return true;\n"
               "}\n"
               "// get clear of your pound, or hop over a ram\n")
    s = rep(s, "  if (D.st === 'ko') { ai.path = null; ai.plan = null; ai.flight = null; ai.evadeT = 0; ai.attackT = 0; ai.wasRdy = false; return; }\n",
               "  if (D.st === 'ko') { ai.path = null; ai.plan = null; ai.flight = null; ai.evadeT = 0; ai.attackT = 0; ai.wasRdy = false; ai.lure = null; return; }\n")
    s = rep(s, "  if (aiEvade(D, dt)) return;\n",
               "  if (ai.lure && aiLure(D, dt)) return; // (v365: a trap it hasn't seen, dead ahead)\n  if (aiEvade(D, dt)) return;\n")
    return s
