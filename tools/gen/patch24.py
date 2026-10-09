import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)

# ---- smaller splats when jumping and slingshotting ----
rep("const SPLAT_R = 1.6, SPLAT_COST = 0.08,", "const SPLAT_R = 1.35, SPLAT_COST = 0.08,")
rep("const launchV = c => JUMP_V * (0.55 + 0.8 * c), launchSpd = c => cfg.speed * (0.9 + 1.7 * c);",
    "const launchV = c => JUMP_V * (0.55 + 0.8 * c), launchSpd = c => cfg.speed * (0.9 + 1.7 * c);\n// a harder fling lands a bigger splat (up to 1.6x a hop's) and costs a little more blood\nconst flingSplatK = fk => 1 + 0.6 * fk, flingCost = fk => SPLAT_COST * (1 + 0.5 * fk);")
rep("const fk = D.flingC || 0, cost = Math.max(0, Math.min(SPLAT_COST, D.paint - 0.03)), Rr = SPLAT_R * (0.55 + 0.45 * cost / SPLAT_COST) * (1 + 1.25 * fk);",
    "const fk = D.flingC || 0, full = flingCost(fk), cost = Math.max(0, Math.min(full, D.paint - 0.03)), Rr = SPLAT_R * (0.55 + 0.45 * cost / full) * flingSplatK(fk);")

# ---- missile path from any point (the CPU plans with it) ----
rep("""function missileHit(D) {
  const sx = Math.sin(D.yaw), sz = Math.cos(D.yaw), h = D.missile ? D.spd : Math.max(D.spd, cfg.speed * 1.7), v = Math.max(5, h * (D.missile ? D.diveK || MISSILE_DIVE : MISSILE_DIVE)), hang = D.missile ? Math.max(0, D.missileHang || 0) : 0.08;
  let x = D.x + sx * h * hang, z = D.z + sz * h * hang, y = D.y;""",
"""function missileHit(D) {
  const h = D.missile ? D.spd : Math.max(D.spd, cfg.speed * 1.7);
  return missileFrom(D.x, D.y, D.z, D.yaw, h, D.missile ? D.diveK || MISSILE_DIVE : MISSILE_DIVE, D.missile ? Math.max(0, D.missileHang || 0) : 0.08);
}
function missileFrom(x0, y0, z0, yaw, h, k, hang) {
  const sx = Math.sin(yaw), sz = Math.cos(yaw), v = Math.max(5, h * k);
  let x = x0 + sx * h * hang, z = z0 + sz * h * hang, y = y0;""")

# ---- CPU: knows what you're doing in the air ----
rep("ai.o = { x: O.x, z: O.z, y: O.y, yaw: O.yaw, spd: O.charging ? 0 : O.spd, st: O.st, slam: O.slam, air: O.air,",
    "ai.o = { x: O.x, z: O.z, y: O.y, yaw: O.yaw, spd: O.charging ? 0 : O.spd, st: O.st, slam: O.slam, air: O.air, vy: O.vy, flung: !!O.flung,")

# ---- CPU trick 1 and 2: slingshot painting, and missiles for coverage ----
rep("// is the straight line from the blob to a point safe to roll",
    """// slingshot painting: price flings in every direction by the fresh ground their splat lands on, per second spent,
// and (with the pound up) fling-then-missile into the freshest patch in reach, which out-paints a pound on the spot
const safeLand = (x, z, y) => { const n = NAV.at(x, z, y); return !!n && n.edge <= 0.25 && !rivals.some(r => r.on && Math.abs(r.y - y) < 0.3 && Math.hypot(x - r.x, z - r.z) < r.hit + 0.5) && !(hardPhase && dryAt(x, z, y, 0.3, -1)); };
function aiFlingPaint(D, rollRate, need, sunNow) {
  if (!AI.flingPaint || D.dilT > 0 || D.st !== 'play' || D.air) return null;
  const endgame = matchLeft < 10, reserve = endgame ? 0.05 : Math.max(0.18, need + 0.06), spot = { team: D.team, x: 0, z: 0, y: 0 };
  const canMissile = AI.missileCov > 0 && !sunNow && slamReady(D), here = canMissile ? localGain(D, SLAM_R * 0.98) : 0;
  let best = null, bs = rollRate * (1.1 + (1 - AI.flingPaint) * 1.6);
  for (let k = 0; k < 16; k++) {
    const yaw = k / 16 * 6.2832, turnT = Math.abs(wrapA(yaw - D.yaw)) / (TURN * 0.75) + 0.3;
    for (const c of [0.3, 0.55, 0.8, 1]) {
      const cost = flingCost(c); if (D.paint - cost < reserve) continue;
      const L = flingLanding(D, yaw, c); if (!L) continue;
      spot.x = L.x; spot.z = L.z; spot.y = L.y;
      const g = localGain(spot, SPLAT_R * flingSplatK(c) * 0.9), rate = g / (L.t + turnT);
      if (rate > bs) { bs = rate; best = { kind: 'paint', yaw, c, t: 0, missile: false }; }
      if (canMissile && c >= 0.55 && D.paint - cost - SLAM_COST > (endgame ? 0.05 : reserve)) {
        const f = flightFor(c, 0), ax = D.x + Math.sin(yaw) * launchSpd(c) * f.up, az = D.z + Math.cos(yaw) * launchSpd(c) * f.up, hh = Math.max(launchSpd(c), cfg.speed * 1.7);
        const m = missileFrom(ax, D.y + f.ap, az, yaw, hh, MISSILE_DIVE, 0.08); if (!m || !safeLand(m.x, m.z, m.y)) continue;
        spot.x = m.x; spot.z = m.z; spot.y = m.y;
        const mg = localGain(spot, MISSILE_R * 0.98); if (mg < here * 1.3 || mg < (AI.covPound || 120) * 0.8) continue;
        const mr = mg / (f.up + 0.1 + (f.ap + 0.5) / (hh * MISSILE_DIVE) + turnT);
        if (mr > bs) { bs = mr; best = { kind: 'paint', yaw, c, t: 0, missile: true }; }
      }
    }
  }
  return best;
}
// shove you off: a direct slingshot hit sends you about ten units, so look for a hole or the edge that far past you
function aiShovePlan(D) {
  const o = D.ai.o, pl = aiAttackPlan(D); if (!pl) return null;
  const ux = Math.sin(pl.yaw), uz = Math.cos(pl.yaw); let drop = false;
  for (let k = 1; k <= 16 && !drop; k++) { const x = o.x + ux * k * 0.6, z = o.z + uz * k * 0.6; if (blockedAt(x, z, o.y + 0.8)) return null; if (surfaceUnder(x, z, o.y + 0.3) === -Infinity) drop = true; }
  if (!drop) return null;
  // land a little short and slide into you at full speed (landing right on top would only flatten you)
  const od = Math.hypot(o.x - D.x, o.z - D.z), c = solveFling(Math.max(1, od - 1.2), D.y - o.y);
  return c > 0 && flingLanding(D, pl.yaw, c) ? { kind: 'shove', yaw: pl.yaw, c, t: 0 } : null;
}
// is the straight line from the blob to a point safe to roll""")
# keep the plain-route value separate from the pound bonus, for comparing against flings
rep("    cand.push([(nAcc[n.id] + 0.7 * v + p) / (d + 2.5) * (1 - 0.4 * turn), n.id, p]);",
    "    const rv = (nAcc[n.id] + 0.7 * v) / (d + 2.5) * (1 - 0.4 * turn); if (rv > rollBest) rollBest = rv;\n    cand.push([(nAcc[n.id] + 0.7 * v + p) / (d + 2.5) * (1 - 0.4 * turn), n.id, p]);")
rep("  const cand = [], planOK = AI.plan > 0 && !sunNow && D.paint > POUND_MIN + 0.03;", "  let rollBest = 0; const cand = [], planOK = AI.plan > 0 && !sunNow && D.paint > POUND_MIN + 0.03;")
rep("  const tn = NAV.nodes[pick[1]];\n  const poundAt =",
    "  // slingshot around when the splats beat rolling there\n  if (AI.flingPaint && !sunNow) { const fp = aiFlingPaint(D, rollBest * speed, need, sunNow); if (fp) { ai.plan = fp; ai.mode = 'paint'; ai.poundAt = -1; return; } }\n  const tn = NAV.nodes[pick[1]];\n  const poundAt =")
# release a paint fling: remember whether to missile
rep("if (L) { fling(D, pl.c); ai.flight = pl.kind; ai.plan = null; return; } }",
    "if (L) { fling(D, pl.c); ai.flight = pl.kind; ai.flMissile = !!pl.missile; ai.plan = null; return; } }")
rep("function aiAir(D, dt) {\n  const ai = D.ai, o = ai.o;\n  if (D.airSling && aiAirSling(D, dt)) return;",
    "function aiAir(D, dt) {\n  const ai = D.ai, o = ai.o;\n  if (D.airSling && aiAirSling(D, dt)) return;\n  if (ai.flight === 'paint' && ai.flMissile && !D.slam && D.vy < 0.6) { ai.flMissile = false; if (slamReady(D)) { useSlam(D); return; } }")
# right after a landing, pick the next move straight away (chains flings)
rep("  ai.flight = null; ai.airRolled = false;", "  if (ai.flight) ai.thinkT = Math.min(ai.thinkT, 0.04);\n  ai.flight = null; ai.flMissile = false; ai.airRolled = false;")

# ---- CPU trick 3: up close it gets rough, and tries to knock you off the map ----
rep("""    if (AI.model > 0.8 && AI.flingAtk && od > 3.5 && od < 10 && D.paint > need + 0.12 && Math.random() < 0.35) {
      const ux = (o.x - D.x) / od, uz = (o.z - D.z) / od; let drop = false;
      for (let k = 1; k <= 7; k++) { const x = o.x + ux * k * 0.6, z = o.z + uz * k * 0.6; if (blockedAt(x, z, o.y)) break; if (surfaceUnder(x, z, o.y + 0.3) === -Infinity) { drop = true; break; } }
      if (drop) { const yaw = Math.atan2(o.x - D.x, o.z - D.z), c = solveFling(Math.max(1, od - 1.2), D.y - o.y); if (c > 0 && flingLanding(D, yaw, c)) { ai.plan = { kind: 'shove', yaw, c, t: 0 }; ai.mode = 'hunt'; return; } }
    }""",
"""    if (AI.model > 0.8 && AI.flingAtk && od > 3.2 && od < 11 && D.paint > need + 0.1 && o.flat <= 0 && Math.random() < (od < 8 ? AI.shove : AI.shove * 0.5)) {
      const pl = aiShovePlan(D); if (pl) { ai.plan = pl; ai.mode = 'hunt'; return; }
    }""")

# ---- CPU trick 4: the landing trap. You're mid-fling and coming down next to it: pound so it lands as you do ----
rep("  if (!slamReady(D) || D.air) return false;\n  const sunny = wxPhase === 'warn' || wxPhase === 'sun', hiding = ai.mode === 'shelter' && sunny;",
    """  if (!slamReady(D) || D.air) return false;
  const sunny = wxPhase === 'warn' || wxPhase === 'sun', hiding = ai.mode === 'shelter' && sunny;
  if (AI.trap && o && o.st === 'play' && o.air && runT - o.t < 0.2 && o.imm <= 0.3 && !hiding) {
    const G1 = GRAV * 1.45, gy = surfaceUnder(o.x, o.z, o.y + 0.3, true), dh = o.y - (gy > -Infinity ? gy : D.y), vy = o.vy || 0;
    const tl = vy > 0 ? vy / GRAV + Math.sqrt(2 * Math.max(0, dh + vy * vy / (2 * GRAV)) / G1) : (vy + Math.sqrt(vy * vy + 2 * G1 * Math.max(0, dh))) / G1;
    const lx = o.x + Math.sin(o.yaw) * o.spd * tl, lz = o.z + Math.cos(o.yaw) * o.spd * tl;
    if (tl > 0.3 && tl < 0.85 && Math.hypot(lx - D.x, lz - D.z) < KO_R - 0.7 && Math.random() < Math.min(1, dt * AI.pound)) return useSlam(D);
  }""")
# don't waste a coverage pound while watered down
rep("if (AI.covPound && ai.covT <= 0 && !reserve) {", "if (AI.covPound && ai.covT <= 0 && !reserve && D.dilT <= 0) {")

# ---- difficulty knobs ----
rep("memory: 1.5, model: 0, airSling: 0.15, attack: 0.08 },", "memory: 1.5, model: 0, airSling: 0.15, attack: 0.08, flingPaint: 0, missileCov: 0, trap: 0, shove: 0 },")
rep("memory: 3,   model: 0.3, airSling: 0.5, attack: 0.3 },", "memory: 3,   model: 0.3, airSling: 0.5, attack: 0.3, flingPaint: 0.35, missileCov: 0, trap: 0, shove: 0.35 },")
rep("memory: 6,   model: 1, airSling: 0.95, attack: 0.55 },", "memory: 6,   model: 1, airSling: 0.95, attack: 0.55, flingPaint: 1, missileCov: 1, trap: 1, shove: 0.8 },")
rep("AI_LV.hardOld = Object.assign({}, AI_LV.hard, { plan: 0, econ: 0, coffinHunt: 0, coffinFlee: 0, model: 0 }); // the previous hard CPU, kept for testing",
    "AI_LV.hardOld = Object.assign({}, AI_LV.hard, { plan: 0, econ: 0, coffinHunt: 0, coffinFlee: 0, model: 0, flingPaint: 0, missileCov: 0, trap: 0, shove: 0.35 }); // an older hard CPU, kept for testing\nAI_LV.hard22 = Object.assign({}, AI_LV.hard, { flingPaint: 0, missileCov: 0, trap: 0, shove: 0.35 }); // hard before slingshot painting, for testing")
open(F, 'w').write(s)
print('ok')
