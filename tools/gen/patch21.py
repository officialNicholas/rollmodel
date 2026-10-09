import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:90])); sys.exit(1)
    s = s.replace(a, b)

# fresh fields every match (Object.assign keeps stale keys otherwise)
rep("reason: null, spawnImm: false, ai: null };",
    "reason: null, spawnImm: false, knockT: 0, missile: false, flung: false, flingC: 0, lastHit: null, kx: 0, kz: 0, airSling: false, ai: null };")

# knock velocity: a push that moves you without turning you
rep("const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), d = D.spd * dt, x0 = D.x, z0 = D.z;\n  let hit = false;\n  const nx = D.x + fx * d; if (!blockedAt(nx, D.z, D.y)) D.x = nx; else hit = true;\n  const nz = D.z + fz * d; if (!blockedAt(D.x, nz, D.y)) D.z = nz; else hit = true;",
    "const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), d = D.spd * dt, x0 = D.x, z0 = D.z, kx = D.kx * dt, kz = D.kz * dt;\n  let hit = false;\n  const nx = D.x + fx * d + kx; if (!blockedAt(nx, D.z, D.y)) D.x = nx; else { hit = true; D.kx = 0; }\n  const nz = D.z + fz * d + kz; if (!blockedAt(D.x, nz, D.y)) D.z = nz; else { hit = true; D.kz = 0; }")
rep("  if (D.knockT > 0) D.knockT -= dt;\n",
    "  if (D.knockT > 0) D.knockT -= dt;\n  if (D.kx || D.kz) { const f = Math.exp(-dt * (D.air ? 1.2 : 5)); D.kx *= f; D.kz *= f; if (D.kx * D.kx + D.kz * D.kz < 0.01) D.kx = D.kz = 0; }\n")
rep("D.st = 'ko'; D.koT = by ? RESPAWN_T : SELF_RESPAWN_T;",
    "D.st = 'ko'; D.lastHit = null; D.kx = D.kz = 0; D.airSling = false; D.missile = false; D.flung = false; D.flingC = 0; D.koT = by ? RESPAWN_T : SELF_RESPAWN_T;")

# splash push: a slingshot landing near you nudges you back
rep("if (fk > 0.25) shockwave(D.x, D.y, D.z, Rr * 1.1, TEAMS[D.team].wet); }",
    "if (fk > 0.25) shockwave(D.x, D.y, D.z, Rr * 1.1, TEAMS[D.team].wet); }\n          if (fk > 0.2) splashPush(D, Rr, fk);")
rep("function shove(A, B) {",
    """// a slingshot landing splashes anyone close: a small push back (a direct hit is a full shove)
function splashPush(A, R, fk) {
  const B = other(A); if (B.st !== 'play' || B.immuneT > 0 || B.slam || B.flatT > 0) return;
  const dx = B.x - A.x, dz = B.z - A.z, d = Math.hypot(dx, dz), lim = R + PR;
  if (d > lim || Math.abs(B.y - A.y) > 1.2) return;
  const nx = d > 0.05 ? dx / d : Math.sin(A.yaw), nz = d > 0.05 ? dz / d : Math.cos(A.yaw), k = 1 - 0.4 * d / lim, v = (3.5 + 3 * fk) * k;
  if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }
  B.kx = nx * v; B.kz = nz * v; B.spd *= 0.5;
  if (!B.air) { B.air = true; B.stroke++; B.vy = 2.4 + 1.2 * fk; } else B.vy = Math.max(B.vy, 1.5);
  B.knockT = Math.max(B.knockT, 0.3); B.wob = 1; B.squash = Math.max(B.squash, 0.5); B.turn = 0;
  B.lastHit = { by: A, t: runT };
  for (let i = 0; i < 10; i++) { const b = Math.atan2(nx, nz) + (Math.random() - 0.5) * 1.6; spawnPart(B.x - nx * 0.3, B.y + 0.3, B.z - nz * 0.3, Math.sin(b) * 2.6, 1.2 + Math.random() * 1.5, Math.cos(b) * 2.6, 0.4, tmat(A), 0.6); }
  if (hearable(B)) AU.bonk(0.45);
  if (B === P) { shake = Math.max(shake, 0.12); buzz(10); popText('Splashed!'); } else if (A === P) popText('Splashed it!');
}
function shove(A, B) {""")

# the burst sling: after bursting out of a coffin you can aim a small sling on the way down
rep("D.air = true; D.y = p.y + 0.35; D.vy = 13.5; D.spd = cfg.speed * 0.55; D.slam = false; D.squash = 0; D.buf = 0; D.freeLand = true; D.turn = 0;",
    "D.air = true; D.y = p.y + 0.35; D.vy = 13.5; D.spd = cfg.speed * 0.55; D.slam = false; D.squash = 0; D.buf = 0; D.freeLand = true; D.turn = 0; D.airSling = true; D.kx = D.kz = 0;\n  if (D === P) hint('airsling', 'Hold and pull on the way down to sling a little', 3);")
rep("function startCharge(D) {\n  if (D.st !== 'hide' && (!canAct(D) || D.air)) return;",
    "function startCharge(D) {\n  if (D.st !== 'hide' && (!canAct(D) || (D.air && !D.airSling))) return;")
rep("  D.charging = true; D.charge = 0; D.pullTgt = 0;\n  if (D === P) { pullTgt = 0; pullNotch = 0; kbHold = 0; AU.chargeStart(); if (D.st === 'play') { AU.brake(); buzz(6); } }",
    "  D.charging = true; D.charge = 0; D.pullTgt = 0;\n  if (D === P) { pullTgt = 0; pullNotch = 0; kbHold = 0; AU.chargeStart(); if (D.st === 'play' && !D.air) { AU.brake(); buzz(6); } }")
rep("const launchV = c => JUMP_V * (0.55 + 0.8 * c), launchSpd = c => cfg.speed * (0.9 + 1.7 * c);",
    """const launchV = c => JUMP_V * (0.55 + 0.8 * c), launchSpd = c => cfg.speed * (0.9 + 1.7 * c);
// the mid-air sling after a coffin burst: a little hop that carries you a quarter as far as the same pull on the ground
const AIR_SLING_K = 0.25;
function airShot(D, c, yaw) {
  const v0 = 1.2 + 2.3 * c, dist = AIR_SLING_K * flightFor(c, 0).d, tx = D.x + Math.sin(yaw) * dist, tz = D.z + Math.cos(yaw) * dist;
  const g = surfaceUnder(tx, tz, D.y + STEP, true), gy = g > -Infinity ? g : D.y - 6;
  const up = v0 / GRAV, ap = v0 * v0 / (2 * GRAV), down = Math.sqrt(2 * Math.max(0, ap + D.y - gy) / (GRAV * 1.45)), T = up + down;
  return { v0, up, ap, T, dist, spd: Math.min(launchSpd(c) * 0.7, dist / Math.max(0.15, T)), x: tx, z: tz, y: g };
}""")
rep("  if (D.st === 'hide') exitPot(D); else if (!canAct(D) || D.air) return; else { cap(D); D.stroke++; }",
    """  if (D.st === 'play' && D.air && D.airSling && canAct(D)) {
    const s = airShot(D, c, D.yaw); D.airSling = false; D.vy = s.v0; D.spd = s.spd; D.kx = D.kz = 0; D.squash = 0.3; D.wob = 1; D.buf = 0;
    burst2(D, 6 + (c * 6 | 0));
    if (D === P) { shake = Math.max(shake, 0.04 + 0.04 * c); fovKick = 3 + 3 * c; AU.fling(c * 0.6); buzz(8); } else if (hearable(D)) AU.fling(c * 0.3);
    return;
  }
  if (D.st === 'hide') exitPot(D); else if (!canAct(D) || D.air) return; else { cap(D); D.stroke++; }""")
# aiming in the air: you hang and drift down slowly, and can turn freely
rep("  else steerAndTurn(D, dt, D.slam ? 0 : D.air ? (D.knockT > 0 ? 0.12 : 0.65) : D.charging ? 0.75 : 1);",
    "  else steerAndTurn(D, dt, D.slam ? 0 : D.air ? (D.knockT > 0 ? 0.12 : D.charging ? 0.85 : 0.65) : D.charging ? 0.75 : 1);")
rep("    else { D.y += D.vy * dt; D.vy -= GRAV * (D.slam ? (D.vy < 0 ? 3 : 1.7) : (D.vy < 0 ? 1.45 : 1)) * dt; }",
    "    else { D.y += D.vy * dt; D.vy -= GRAV * (D.slam ? (D.vy < 0 ? 3 : 1.7) : (D.vy < 0 ? 1.45 : 1)) * dt; if (D.charging && D.vy < -3) D.vy = -3; }")
rep("      D.y = g; D.vy = 0; D.air = false; D.coyote = 0; D.squash = 0.6 + 0.4 * impact;",
    "      D.y = g; D.vy = 0; D.air = false; D.coyote = 0; D.squash = 0.6 + 0.4 * impact; D.airSling = false;")

# aim ring / arc for the mid-air sling
rep("    if (aiming) {\n      const c = Math.max(FLING_MIN, P.charge), v0 = launchV(c)",
    """    if (aiming && P.air && P.airSling) {
      const c = Math.max(FLING_MIN, P.charge), s = airShot(P, c, P.yaw), fx = fwdX(), fz = fwdZ(), pop = Math.min(1, P.charge / 0.12);
      aimRing.position.set(s.x, (s.y > -Infinity ? s.y : P.y - 6) + 0.11, s.z); aimRing.scale.setScalar((0.5 + 0.35 * pop) * (0.94 + 0.06 * Math.sin(clock * 10))); aimRing.visible = s.y > -Infinity;
      const ph = (clock * 1.6) % 1;
      for (let i = 0; i < ARC_N; i++) {
        const u = (i + ph) / ARC_N, t = u * s.T * 0.94, h = t < s.up ? s.v0 * t - 0.5 * GRAV * t * t : s.ap - 0.5 * GRAV * 1.45 * (t - s.up) * (t - s.up), d = arcDots[i];
        d.position.set(P.x + fx * s.spd * t, P.y + 0.35 + h, P.z + fz * s.spd * t); d.scale.setScalar(pop * (1 - 0.45 * u) * Math.min(1, u * 6)); d.visible = true;
      }
    } else if (aiming) {
      const c = Math.max(FLING_MIN, P.charge), v0 = launchV(c)""")

# the CPU uses the burst sling too: steer clear of trouble or toward fresh canvas
rep("function aiAir(D, dt) {\n  const ai = D.ai, o = ai.o;",
    """function aiAirSling(D, dt) {
  const ai = D.ai;
  if (!ai.airAim) {
    if (D.vy > 3 || ai.airRolled) return false;
    ai.airRolled = true; if (Math.random() > AI.airSling) return false;
    const O = other(D), o = ai.o, near = o && o.st === 'play' && runT - o.t < 1 && !(o.imm > 0.3);
    const fall = (x, z) => { const g = surfaceUnder(x, z, D.y + STEP, true); if (g === -Infinity || g > D.y - 0.2) return null; for (let a = 0; a < 6.28; a += 1.05) if (surfaceUnder(x + Math.sin(a) * 1.1, z + Math.cos(a) * 1.1, D.y + STEP, true) === -Infinity) return null; if (rivals.some(r => r.on && Math.abs(r.y - g) < 0.3 && Math.hypot(x - r.x, z - r.z) < r.hit + 0.5)) return null; return g; };
    const score = (x, z, g) => localGain({ team: D.team, x, z, y: g }, 2.2) + (near && O.slamCD <= 0.5 ? Math.min(12, Math.hypot(x - o.x, z - o.z)) * 3 : 0);
    // where the current drift lands
    const tF = (D.vy + Math.sqrt(Math.max(0, D.vy * D.vy + 2 * GRAV * 1.45 * 6))) / (GRAV * 1.45), dx0 = D.x + Math.sin(D.yaw) * D.spd * Math.min(tF, 1.4), dz0 = D.z + Math.cos(D.yaw) * D.spd * Math.min(tF, 1.4), g0 = fall(dx0, dz0);
    const base = g0 === null ? -1e9 : score(dx0, dz0, g0);
    let best = null, bs = base + 6;
    for (let k = 0; k < 12; k++) for (const c of [0.55, 1]) { const yaw = k / 12 * 6.2832, s = airShot(D, c, yaw), g = fall(s.x, s.z); if (g === null) continue; const sc = score(s.x, s.z, g); if (sc > bs) { bs = sc; best = { yaw, c, t: 0 }; } }
    if (!best) return false;
    ai.airAim = best; startCharge(D);
  }
  const pl = ai.airAim; pl.t += dt;
  if (!D.charging || !D.airSling) { ai.airAim = null; return false; }
  const err = wrapA(pl.yaw - D.yaw); D.steer = -clamp(err * 3.4, -1, 1); D.pullTgt = pl.c;
  if ((Math.abs(err) < 0.1 && Math.abs(D.charge - pl.c) < 0.05) || pl.t > 0.9) { fling(D, D.charge > FLING_MIN ? D.charge : pl.c); ai.airAim = null; }
  return true;
}
function aiAir(D, dt) {
  const ai = D.ai, o = ai.o;
  if (D.airSling && aiAirSling(D, dt)) return;""")
rep("  if (D.air) return aiAir(D, dt);\n  ai.flight = null;",
    "  if (D.air) return aiAir(D, dt);\n  ai.flight = null; ai.airRolled = false; if (ai.airAim) { ai.airAim = null; if (D.charging) cancelCharge(D); }")
# levels
rep("memory: 1.5, model: 0 },", "memory: 1.5, model: 0, airSling: 0.15 },")
rep("memory: 3,   model: 0.3 },", "memory: 3,   model: 0.3, airSling: 0.5 },")
rep("memory: 6,   model: 1 },", "memory: 6,   model: 1, airSling: 0.95 },", 1)

open(F, 'w').write(s)
print('ok')
s = open(F).read()
rep("function aiCoffin(D, dt) {\n  const ai = D.ai, p = D.pot, O = other(D); D.steer = 0;", "function aiCoffin(D, dt) {\n  const ai = D.ai, p = D.pot, O = other(D); D.steer = 0; ai.airRolled = false; ai.airAim = null;")
open(F, 'w').write(s)
print('ok2')
