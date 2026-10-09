# V66: movement and reactions polish. The camera follows a turn without lagging so far behind; steering answers a touch quicker; one-frame
# hops off tiny drops don't flicker the body into its jump pose; steps up and down ease instead of snapping. And the slime reacts: it
# braces for landings and walls, plants itself as it lands, pushes off as it jumps, curls into a ball to roll, rocks on its base as it
# speeds up, stops, lands or gets knocked, and when it's sent flying it tumbles head over heels (limbs flailing) and always comes down
# upright, then shakes itself off. All of the reactions are only its look: where it goes and how it handles don't change
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:160])
    src = src.replace(old, new)

# ---------- the requests: the simulation asks for a reaction, the look plays it next frame ----------
rep("const tmat = D => teamMats[D.team];\n",
    "const tmat = D => teamMats[D.team];\n"
    "// the slime's reactions, asked for by the simulation and played by its look on the next frame (none of it changes where anything goes):\n"
    "// a jolt in a push's direction (world x, z; k how hard), a push-off, and a tumble when it's sent flying (side: which way it leans)\n"
    "function fxKnock(D, x, z, k) { if (!(k > D.fxK)) return; const l = Math.hypot(x, z); if (l < 1e-4) { x = -Math.sin(D.yaw); z = -Math.cos(D.yaw); } else { x /= l; z /= l; } D.fxK = k; D.fxX = x; D.fxZ = z; }\n"
    "function fxLaunch(D, k) { if (k > D.fxL) D.fxL = k; }\n"
    "function fxTumble(D, k, side) { if (k > D.fxT) { D.fxT = k; D.fxSide = side >= 0 ? 1 : -1; } }\n")
# (on every blob from the start, so its shape never changes)
rep("rocket: null, turret: null, tGuard: 0, ai: null };", "rocket: null, turret: null, tGuard: 0, ai: null, fxK: 0, fxX: 0, fxZ: 0, fxL: 0, fxT: 0, fxSide: 1, stepOff: 0 };")

# ---------- the hits ----------
# rammed by a fling: sent flying, tumbling; the rammer bounces back off it
rep("  B.lastHit = { by: A, t: runT }; emote(B, 'ouch', 0.9); emote(A, 'glee', 1.0);\n  A.spd *= 0.3;",
    "  B.lastHit = { by: A, t: runT }; emote(B, 'ouch', 0.9); emote(A, 'glee', 1.0); fxTumble(B, 1, wrapA(a - A.yaw)); fxKnock(A, -Math.sin(A.yaw), -Math.cos(A.yaw), 0.55);\n  A.spd *= 0.3;")
# blasted out by a burst
rep("  O.knockT = 0.9; O.flung = false; O.flingC = 0; O.wob = 1; O.squash = 0.8; O.lastHit = { by: D, t: runT }; emote(O, 'ouch', 0.9); emote(D, 'glee', 1.0);",
    "  O.knockT = 0.9; O.flung = false; O.flingC = 0; O.wob = 1; O.squash = 0.8; O.lastHit = { by: D, t: runT }; emote(O, 'ouch', 0.9); emote(D, 'glee', 1.0); fxTumble(O, 0.7 + 0.3 * k, Math.random() - 0.5);")
# kicked out of a refill: it tumbles out; the kicker bounces back
rep("  O.yaw = a; O.air = true; O.vy = JUMP_V * 1.15; O.y = p.y + 0.55; O.spd = cfg.speed * 1.2; O.wob = 1; O.squash = 0.7; O.turn = 0;",
    "  O.yaw = a; O.air = true; O.vy = JUMP_V * 1.15; O.y = p.y + 0.55; O.spd = cfg.speed * 1.2; O.wob = 1; O.squash = 0.7; O.turn = 0; fxTumble(O, 0.8, Math.random() - 0.5);")
rep("  D.spd *= 0.35; D.vy = Math.max(D.vy, 4); D.air = true; D.wob = 1; D.squash = 0.6; D.flung = false;\n  shockwave(p.x, p.y, p.z, 1.8, TEAMS[D.team].wet);",
    "  D.spd *= 0.35; D.vy = Math.max(D.vy, 4); D.air = true; D.wob = 1; D.squash = 0.6; D.flung = false; fxKnock(D, -Math.sin(D.yaw), -Math.cos(D.yaw), 0.6);\n  shockwave(p.x, p.y, p.z, 1.8, TEAMS[D.team].wet);")
# shrunk back from giant
rep("  if (!B.air) { B.air = true; B.stroke++; } B.vy = Math.max(B.vy, 5.5); B.slam = false; B.missile = false;\n",
    "  if (!B.air) { B.air = true; B.stroke++; } B.vy = Math.max(B.vy, 5.5); B.slam = false; B.missile = false; fxKnock(B, B.x - A.x, B.z - A.z, 0.8);\n")
# a fling's splash shoves you back
rep("  B.knockT = Math.max(B.knockT, 0.3); B.wob = 1; B.squash = Math.max(B.squash, 0.5); B.turn = 0;\n  B.lastHit = { by: A, t: runT }; emote(B, 'ouch', 0.55);",
    "  B.knockT = Math.max(B.knockT, 0.3); B.wob = 1; B.squash = Math.max(B.squash, 0.5); B.turn = 0; fxKnock(B, nx, nz, 0.45 + 0.4 * fk);\n  B.lastHit = { by: A, t: runT }; emote(B, 'ouch', 0.55);")
# rolled into: stunned
rep("  B.stunT = STUN_T; B.spd = 0; B.turn = 0; B.slam = false; B.squash = 0.8; B.wob = 1; B.kx = B.kz = 0;\n",
    "  B.stunT = STUN_T; B.spd = 0; B.turn = 0; B.slam = false; B.squash = 0.8; B.wob = 1; B.kx = B.kz = 0; fxKnock(B, B.x - A.x, B.z - A.z, 0.75);\n")
# bumping into each other evenly: each jolted away from the other
rep("    if (D.bonkCD <= 0 && D.spd > 1) { D.yaw = Math.atan2(nx * sx, nz * sx) + (Math.random() - 0.5) * 0.8; D.spd *= 0.65;",
    "    if (D.bonkCD <= 0 && D.spd > 1) { fxKnock(D, nx * sx, nz * sx, clamp(D.spd / 10, 0.25, 0.6)); D.yaw = Math.atan2(nx * sx, nz * sx) + (Math.random() - 0.5) * 0.8; D.spd *= 0.65;")
# landing on top of someone: the stomper springs off
rep("{ flatten(B, A, 'stomp'); A.vy = 6.5; A.air = true; A.y = Math.max(A.y, B.y + 0.3); return; }",
    "{ flatten(B, A, 'stomp'); A.vy = 6.5; A.air = true; A.y = Math.max(A.y, B.y + 0.3); fxLaunch(A, 0.8); return; }")
# a turret's shot
rep("  B.kx = nx * SHOT_PUSH * (stunNow ? 1 : 0.6); B.kz = nz * SHOT_PUSH * (stunNow ? 1 : 0.6); B.slam = false; B.missile = false; B.squash = 0.8; B.wob = 1;\n",
    "  B.kx = nx * SHOT_PUSH * (stunNow ? 1 : 0.6); B.kz = nz * SHOT_PUSH * (stunNow ? 1 : 0.6); B.slam = false; B.missile = false; B.squash = 0.8; B.wob = 1; fxKnock(B, nx, nz, stunNow ? 0.65 : 0.4);\n")
# a pound's shockwave pops those near it up
for line in ["B.air = true; B.stroke++; B.vy = 3 + 3.5 * (1 - bd / 16); B.knockT = 0.35; B.wob = 1; B.squash = 0.7; } }"]:
    rep(line, "B.air = true; B.stroke++; B.vy = 3 + 3.5 * (1 - bd / 16); B.knockT = 0.35; B.wob = 1; B.squash = 0.7; fxKnock(B, B.x - D.x, B.z - D.z, 0.35 + 0.35 * (1 - bd / 16)); } }", 2)
# running into a wall: knocked back off it
rep("  if (into > 0.45 && D.spd > 0.8) {\n    D.squash = Math.max(D.squash, 0.2 + 0.3 * k); D.wob = Math.max(D.wob, 0.6);",
    "  if (into > 0.45 && D.spd > 0.8) {\n    D.squash = Math.max(D.squash, 0.2 + 0.3 * k); D.wob = Math.max(D.wob, 0.6); fxKnock(D, n ? n[0] : -fx, n ? n[1] : -fz, 0.25 + 0.55 * k);")
# pushing off: a jump, out of a refill, a fling off the ground
rep("  D.air = true; D.vy = JUMP_V; D.stroke++; D.squash = 0; D.buf = 0; if (D === P) AU.jump();",
    "  D.air = true; D.vy = JUMP_V; D.stroke++; D.squash = 0; D.buf = 0; fxLaunch(D, 1); if (D === P) AU.jump();")
rep("  D.air = true; D.vy = launchV(c); D.spd = launchSpd(c); D.squash = 0; D.buf = 0; D.flung = true; D.flingC = c;",
    "  D.air = true; D.vy = launchV(c); D.spd = launchSpd(c); D.squash = 0; D.buf = 0; D.flung = true; D.flingC = c; fxLaunch(D, 0.7 + 0.3 * c);")
rep("  D.air = true; D.vy = JUMP_V * 1.05; D.y = p.y + 0.55; D.stroke++; D.spd = cfg.speed * 0.8; if (D === P) AU.jump();",
    "  D.air = true; D.vy = JUMP_V * 1.05; D.y = p.y + 0.55; D.stroke++; D.spd = cfg.speed * 0.8; fxLaunch(D, 0.8); if (D === P) AU.jump();")

# ---------- stepping up and down a ledge: the snap in height is kept as an offset the look eases out ----------
rep("    if (g === -Infinity || D.y - g > 0.35) { D.air = true; D.vy = 0; D.stroke++; D.coyote = 0.12; }\n    else D.y = g;",
    "    if (g === -Infinity || D.y - g > 0.35) { D.air = true; D.vy = 0; D.stroke++; D.coyote = 0.12; }\n    else { if (Math.abs(g - D.y) > 0.09 + D.spd * dt * 0.8) D.stepOff = clamp(D.stepOff + D.y - g, -0.6, 0.6); D.y = g; }")
rep("  if (D.wob > 0) D.wob = Math.max(0, D.wob - dt * 2.5); if (D.coyote > 0) D.coyote -= dt;",
    "  if (D.wob > 0) D.wob = Math.max(0, D.wob - dt * 2.5); if (D.coyote > 0) D.coyote -= dt; if (D.stepOff) { D.stepOff *= Math.exp(-dt * 16); if (Math.abs(D.stepOff) < 0.002 || D.air) D.stepOff = 0; }")

# ---------- steering: a quicker turn response ----------
rep("D.turn += (want - D.turn) * Math.min(1, dt * (D === P && !P.ai ? (want * D.turn < 0 ? 40 : 28) : 20));",
    "D.turn += (want - D.turn) * Math.min(1, dt * (D === P && !P.ai ? (want * D.turn < 0 ? 50 : 36) : 20));")

# ---------- the camera: follows the turn it's in (aims a little ahead along it), so it doesn't trail so far behind ----------
rep("    let dy = P.yaw - camYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); camYaw += dy * (1 - Math.exp(-rdt * 5.5));",
    "    camTurnS += ((P.st === 'play' ? P.turn : 0) - camTurnS) * (1 - Math.exp(-rdt * 9));\n"
    "    let dy = P.yaw - camTurnS * 0.085 - camYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); camYaw += dy * (1 - Math.exp(-rdt * 6.5));")
rep("const camVel = new THREE.Vector3(), lookVel = new THREE.Vector3();", "const camVel = new THREE.Vector3(), lookVel = new THREE.Vector3(); let camTurnS = 0;")

# ---------- the look ----------
# in the air for a moment (rolling off a low edge) is still on the ground to the look; a real jump or fall shows at once
rep("  const L = V.look, U = V.U, hidden = D.st === 'hide';\n",
    "  const L = V.look, U = V.U, hidden = D.st === 'hide';\n"
    "  V.airT = D.air ? (V.airT || 0) + dt : 0; const vAir = V.vAir = D.air && (V.airT > 0.09 || D.vy > 1 || D.vy < -3 || D.knockT > 0 || D.slam || D.flung || D.missile || D.st !== 'play');\n"
    "  // the reactions asked for since the last frame\n"
    "  const fxK = D.fxK, fxL = D.fxL, fxT = D.fxT; D.fxK = D.fxL = D.fxT = 0;\n")
rep("const rad = PR * (0.8 + 0.2 * D.paint) * (hidden ? 0.7 : 1) * V.gk * (state === 'intro' && D.formK !== undefined ? D.formK : 1), falling = D.air && D.vy < 0, rising = D.air && D.vy > 0;",
    "const rad = PR * (0.8 + 0.2 * D.paint) * (hidden ? 0.7 : 1) * V.gk * (state === 'intro' && D.formK !== undefined ? D.formK : 1), falling = vAir && D.vy < 0, rising = vAir && D.vy > 0;")
rep("  L.spd += ((D.air || D.st !== 'play' || D.flatT > 0 ? 0 : clamp(D.spd / 6.5, 0, 1)) - L.spd) * ke;",
    "  L.spd += ((vAir || D.st !== 'play' || D.flatT > 0 ? 0 : clamp(D.spd / 6.5, 0, 1)) - L.spd) * ke;")
rep("  L.flat += ((D.air ? 0 : 1) - L.flat) * kf;", "  L.flat += ((vAir ? 0 : 1) - L.flat) * kf;")
rep("U.gWob.value = (hidden ? 0.5 : D.air ? 0.4 : 1) + D.wob * 2.2;", "U.gWob.value = (hidden ? 0.5 : vAir ? 0.4 : 1) + D.wob * 2.2;")
# knocked flying: the tumble
rep("  const fk = V.flatK;\n  V.root.position.set(D.x, D.y + rad * isc",
    "  const fk = V.flatK;\n"
    "  // knocked flying: one controlled flip, head over heels along its flight and a little off to one side, timed to finish just before it comes\n"
    "  // down so it always lands upright on its base (coming down early onto something higher, it rolls the rest of the way over quickly)\n"
    "  if (fxT > 0 && D.st === 'play' && D.air && !D.rocket) V.tum = { t: 0, T: clamp(flightTime(D) - 0.1, 0.42, 1.25), side: D.fxSide, k: Math.min(1, fxT), fin: -1, a: 0 };\n"
    "  let tumX = 0, tumZ = 0; const TM = V.tum;\n"
    "  if (TM) {\n"
    "    if (D.st !== 'play' || D.rocket || D.slam) V.tum = null;\n"
    "    else { TM.t += dt; const u = Math.min(1, TM.t / TM.T);\n"
    "      if (!D.air && u < 1 && TM.fin < 0) TM.fin = 0;\n"
    "      if (TM.fin >= 0) { TM.fin += dt / 0.13; const f = Math.min(1, TM.fin); TM.a += (6.2832 - TM.a) * (1 - Math.pow(1 - f, 2)) * (f >= 1 ? 1 : Math.min(1, dt * 30)); tumX = f >= 1 ? 6.2832 : TM.a; }\n"
    "      else { TM.a = 6.2832 * (1 - Math.pow(1 - u, 1.8)); tumX = TM.a; }\n"
    "      tumZ = TM.side * 0.42 * TM.k * Math.sin(Math.PI * Math.min(1, TM.a / 6.2832 * 1.12));\n"
    "      if ((TM.fin >= 1 || (u >= 1 && !D.air)) ) { V.tum = null; if (V.slime && V.slime.shakeOff) V.slime.shakeOff(0.6 + 0.4 * TM.k); } }\n"
    "  }\n"
    "  V.root.position.set(D.x, D.y + D.stepOff + rad * isc")
rep("+ (D.rollT > ROLL_T - ROLL_DASH ? 6.2832 * (1 - Math.pow((D.rollT - ROLL_T + ROLL_DASH) / ROLL_DASH, 2)) : 0) + V.pullLean, D.yaw + spinY, (D === P && idle.sway ? idle.sway * 0.06 : 0) + (D.shimNow ? D.shimNow.shove * 0.05 : 0));",
    "+ (D.rollT > ROLL_T - ROLL_DASH ? 6.2832 * (1 - Math.pow((D.rollT - ROLL_T + ROLL_DASH) / ROLL_DASH, 2)) : 0) + V.pullLean + tumX, D.yaw + spinY, (D === P && idle.sway ? idle.sway * 0.06 : 0) + (D.shimNow ? D.shimNow.shove * 0.05 : 0) + tumZ);")
rep("  if (V.slime) slimeVisual(D, V, dt, sq, rise, rad, gy, hop);\n  return gy;\n}",
    "  if (V.slime) slimeVisual(D, V, dt, sq, rise, rad, gy, hop, fxK, fxL);\n  return gy;\n}\n"
    "// how long until a blob that's just been sent flying comes down: its arc stepped through (the knockback's fade and any steering left out:\n"
    "// close enough to time a flip by)\n"
    "function flightTime(D) {\n"
    "  let x = D.x, y = D.y, z = D.z, vy = D.vy, t = 0; const vx = Math.sin(D.yaw) * D.spd + D.kx * 0.7, vz = Math.cos(D.yaw) * D.spd + D.kz * 0.7, h = 1 / 30;\n"
    "  while (t < 1.6) { y += vy * h; vy -= GRAV * (vy < 0 ? 1.45 : 1) * h; x += vx * h; z += vz * h; t += h; if (vy <= 0) { const g = surfaceUnder(x, z, y + STEP, true); if (g > -Infinity && y <= g) return t; } }\n"
    "  return 1.1;\n"
    "}")

# the face: bracing (eyes screwed shut) and the leap only in a real jump
rep("  if (D.air && D.st === 'play' && !D.slam && !D.missile && !D.rocket && !D.turret && !(D.giantT > 0) && !(D.knockT > 0)) return 'leap'; // (wide-eyed, mouth open: up it goes)",
    "  const V = vOf(D); if (V && V.braceT > 0) return 'brace'; // (screwing its eyes shut: about to hit hard)\n"
    "  if ((V ? V.vAir : D.air) && D.st === 'play' && !D.slam && !D.missile && !D.rocket && !D.turret && !(D.giantT > 0) && !(D.knockT > 0)) return 'leap'; // (wide-eyed, mouth open: up it goes)")

# slimeVisual: the reactions, and one options object per blob (no garbage each frame)
rep("function slimeVisual(D, V, dt, sq, rise, rad, gy, hop) {\n  const I = V.slime, L = V.look, U = V.U; potEyes(D, V, dt);",
    "function slimeVisual(D, V, dt, sq, rise, rad, gy, hop, fxK, fxL) {\n  const I = V.slime, L = V.look, U = V.U; potEyes(D, V, dt);")
old_upd = """  SLIME.update(I, { dt, spd: U.gSpd.value, lean: L.lean, air: hopAir ? 1 : 1 - L.flat, inAir: (!!D.air && D.st === 'play') || hopAir, vy: hopAir ? hv * 2.6 : D.vy || 0, height: hopAir ? mHop * 2.6 : gy > -Infinity ? D.y - gy : 9, grav: GRAV, pos: [D.x + (V.scootX || 0), D.y + mHop, D.z + (V.scootZ || 0)], shove: clamp((D === P ? idle.sway : 0) + (D.shimNow ? D.shimNow.shove : 0), -1, 1), push: clamp((D === P ? idle.push : 0) + (D.shimNow ? D.shimNow.push : 0), -1, 1),
    drop: U.gDrop.value, squash: I.form === 'turret' ? 0.1 * (D.turret ? D.turret.kick : 0) : sq, rise, wob: Math.min(2.2, U.gWob.value) * 0.6,
    yaw: V.root.rotation.y, aimPitch: V.turPitch || 0, speed: D.air ? 0 : D.spd, rad, look: V.slimeLook || null, leap: !!D.air && D.st === 'play' && !hopAir && !D.slam && !D.missile && !D.rocket && !D.turret && !(D.giantT > 0), hover: state === 'intro' && !D.pot && !D.introLeap && !D.introOut, maxBall: hopAir ? 0.3 : 1, watch: V.slimeWatchT ? { yaw: V.slimeWatchT.yaw, pitch: V.slimeWatchT.pitch } : null });"""
new_upd = """  // bracing: the ground coming up (how soon it lands), or a wall straight ahead at speed; tumbling (knocked flying) it flails
  const live = D.st === 'play' && state !== 'menu' && !D.slam && !D.rocket && !D.turret && !(D.giantT > 0), vAir = V.vAir;
  let brace = 0, wall = 0;
  if (live && vAir && D.vy < 0 && gy > -Infinity) { const f = -D.vy, g = GRAV * 1.45, hh = Math.max(0, D.y - gy), t = (Math.sqrt(f * f + 2 * g * hh) - f) / g; brace = 1 - smoothstep(0.06, 0.26, t); }
  else if (live && !D.air && D.spd > 3.2 && !D.charging && !(D.rollT > 0) && camera.position.distanceToSquared(V.root.position) < 520) { const run = clearRun(D, D.yaw, 1.5), need = 0.25 + D.spd * 0.07; if (run < need) wall = clamp((need - run) / need * 1.6, 0, 1); }
  const TM = V.tum, flail = TM && TM.fin < 0 ? TM.k * (1 - smoothstep(0.62, 0.86, TM.t / TM.T)) : 0;
  if ((wall > 0.45 && D.spd > 4.5) || (brace > 0.45 && (TM || D.vy < -10))) V.braceT = 0.22; else if (V.braceT > 0) V.braceT -= dt;
  if (fxK > 0) { const ry = V.root.rotation.y, c = Math.cos(ry), s = Math.sin(ry); I.impact(D.fxX * c - D.fxZ * s, D.fxX * s + D.fxZ * c, fxK); }
  if (fxL > 0) I.launch(fxL);
  const o = V.so || (V.so = { pos: [0, 0, 0], wt: { yaw: 0, pitch: 0 } }), W = V.slimeWatchT;
  o.dt = dt; o.spd = U.gSpd.value; o.lean = L.lean; o.air = hopAir ? 1 : 1 - L.flat; o.inAir = (vAir && D.st === 'play') || hopAir; o.vy = hopAir ? hv * 2.6 : D.vy || 0; o.height = hopAir ? mHop * 2.6 : gy > -Infinity ? D.y - gy : 9; o.grav = GRAV;
  o.pos[0] = D.x + (V.scootX || 0); o.pos[1] = D.y + D.stepOff + mHop; o.pos[2] = D.z + (V.scootZ || 0);
  o.shove = clamp((D === P ? idle.sway : 0) + (D.shimNow ? D.shimNow.shove : 0), -1, 1); o.push = clamp((D === P ? idle.push : 0) + (D.shimNow ? D.shimNow.push : 0), -1, 1);
  o.drop = U.gDrop.value; o.squash = I.form === 'turret' ? 0.1 * (D.turret ? D.turret.kick : 0) : sq; o.rise = rise; o.wob = Math.min(2.2, U.gWob.value) * 0.6;
  o.yaw = V.root.rotation.y; o.aimPitch = V.turPitch || 0; o.speed = vAir ? 0 : D.spd; o.rad = rad; o.look = V.slimeLook || null;
  o.leap = vAir && D.st === 'play' && !hopAir && !D.slam && !D.missile && !D.rocket && !D.turret && !(D.giantT > 0) && !TM; o.hover = state === 'intro' && !D.pot && !D.introLeap && !D.introOut; o.maxBall = hopAir ? 0.3 : 1;
  o.brace = brace; o.wall = wall; o.flail = flail; o.curl = D.st === 'play' && D.rollT > ROLL_T - ROLL_DASH - 0.03 && !D.air ? 1 : 0;
  if (W) { o.wt.yaw = W.yaw; o.wt.pitch = W.pitch; o.watch = o.wt; } else o.watch = null;
  SLIME.update(I, o);"""
rep(old_upd, new_upd)
open(P, 'w').write(src)
print('ok', len(src))
