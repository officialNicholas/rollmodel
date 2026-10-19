"""v375: your turret stays where you point it, locks onto a rival in front, and its shots meet them.

- It turned itself: a rival anywhere within about 43 degrees of where it faced pulled it round at up to 137 degrees a second (fighting
  your steering), and the camera, which follows where you face, swung with it. Now only your steering turns you and the camera.
- It missed: its shots went for the rival only within 26 degrees (between 26 and 43 it was being pulled round but still painting the
  floor), the lead came from where the rival faced and its top speed, not where it was really going, and from a guess at the flight time
  that wasn't the time the lob it then fired really took. And the lob was high and slow (about 0.9 s to 9 units), long enough for a rival
  to turn away.
- Now: a rival within 34 degrees of where you face, on your screen, in reach and in sight, is locked onto (a little buzz, the ring
  jumps onto them). The turret's head swings round onto them, up to 52 degrees either side, and you and the camera stay put. The lock
  holds while they stay within 52 degrees, in reach and on your screen or just past its edge (a moment off it, or behind a wall, doesn't
  break it), so it doesn't flick between rivals. Its shots lead them by where they're really going (their movement over the last
  moments, and their fall if they're in the air), worked out from the time the very shot it fires will take, in a low, quick arc when
  nothing's in the way and the old high lob when a wall is. With no lock, its shots go straight ahead, near to far and back along a
  lane, and the ring sits still in the middle of it instead of running up and down.
- CPU turrets are as they were."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- no pulling you round: the lock and the head's swing instead
    s = rep(s, "  // your range: drag up (or the up key) to lob further, down to drop them closer\n"
               "  // (v309) a rival near your line pulls the turret round onto them (where they're going), less the harder you steer\n"
               "  if (!D.ai && D.st === 'play') { const tg = coneFoe(D, 0.75, TURRET_FAR + 1); if (tg) { const O = tg.O, lead = Math.min(0.6, tg.d / SHOT_V), err = wrapA(Math.atan2(O.x + Math.sin(O.yaw) * O.spd * lead - D.x, O.z + Math.cos(O.yaw) * O.spd * lead - D.z) - D.yaw), r = 2.4 * Math.max(0, 1 - Math.abs(steerIn) * 1.6 - (keyL || keyR ? 1 : 0)) * dt; D.yaw += clamp(err, -r, r); } }\n",
               "  // (v375) yours turns only as you steer it (and the camera with it); a rival in front is locked onto and its head swings onto them\n"
               "  if (!D.ai && D.st === 'play') turretLock(D, dt);\n")
    s = rep(s, "// where a turret's next shot is headed: your shots go the range you've set (onto a foe near that spot, if there is one); a CPU's sweep\n"
               "// near to far and back, or go for a foe in front\n"
               "function turretTarget(D, x0, z0) {\n"
               "  const T = D.turret; let a = D.yaw, d, ty, foe = null;\n",
               "// (v375) your turret's lock: a rival within TUR_IN of where you face, on your screen, in reach and in sight (from about as high as its\n"
               "// lob goes, so a low wall doesn't hide them), is locked onto; the lock holds while they stay within TUR_OUT and in reach, and on your\n"
               "// screen or just past its edge (off it for a moment doesn't count), whatever they duck behind or roll through, so it never flicks between\n"
               "// rivals. Its head swings round onto where its shots will meet them (TUR_SW either side at most, TUR_SWV radians a second); with no lock\n"
               "// it comes back to the middle. Where they're going is their real movement over the last moments\n"
               "const TUR_IN = 0.6, TUR_OUT = 0.9, TUR_SW = 0.9, TUR_SWV = 5, TUR_MID = 10, turV = new THREE.Vector3();\n"
               "function turretLock(D, dt) {\n"
               "  const T = D.turret, ay = D.yaw + (T.sw || 0), cy = Math.cos(ay), sy = Math.sin(ay), tp = TURRET_RIG.tip, x0 = D.x + (tp.x * cy + tp.z * sy) * PR, y0 = D.y + (tp.y + 0.82 + 0.3) * PR, z0 = D.z + (-tp.x * sy + tp.z * cy) * PR;\n"
               "  const can = O => O && O.st === 'play' && !O.rocket && ACTIVE.includes(O) && !ally(O, D), off = O => ({ d: Math.hypot(O.x - D.x, O.z - D.z), err: Math.abs(wrapA(Math.atan2(O.x - D.x, O.z - D.z) - D.yaw)) });\n"
               "  const seen = (O, m) => D !== P || (turV.set(O.x, O.y + 0.3, O.z).project(camera), turV.z < 1 && Math.abs(turV.x) < m && Math.abs(turV.y) < 0.95); // (on your screen, m its width: on an upright phone that's well inside TUR_IN)\n"
               "  let L = T.lk; if (L) { const o = can(L) ? off(L) : null; T.offT = seen(L, 1.5) ? 0 : (T.offT || 0) + dt; if (!o || o.err > TUR_OUT || o.d > TURRET_FAR + 3 || o.d < 0.8 || T.offT > 0.4) L = null; } // (a little past the edge holds)\n"
               "  if (!L) { let best = null, bs = 1e9; for (const O of foes(D)) { if (!can(O) || O.immuneT > 0.3) continue; const o = off(O); if (o.d < 1.2 || o.d > TURRET_FAR + 1 || o.err > TUR_IN || !seen(O, 0.9) || !losClear(D.x, D.y + 2.6, D.z, O.x, O.y + 0.6, O.z)) continue; const sc = o.err + o.d * 0.02; if (sc < bs) { bs = sc; best = O; } } L = best; T.offT = 0; }\n"
               "  if (L !== T.lk) { T.lk = L; T.lv = L ? { x: L.x, z: L.z, vx: Math.sin(L.yaw) * (L.spd || 0), vz: Math.cos(L.yaw) * (L.spd || 0) } : null; if (L && D === P) buzz(8); }\n"
               "  if (L) { const v = T.lv, ix = clamp((L.x - v.x) / Math.max(dt, 1e-3), -25, 25), iz = clamp((L.z - v.z) / Math.max(dt, 1e-3), -25, 25), k = Math.min(1, dt / 0.12); v.vx += (ix - v.vx) * k; v.vz += (iz - v.vz) * k; v.x = L.x; v.z = L.z; }\n"
               "  let want = 0; if (L) { const P2 = turretLead(D, L, x0, y0, z0); want = clamp(wrapA(Math.atan2(P2.tx - x0, P2.tz - z0) - D.yaw), -TUR_SW, TUR_SW); }\n"
               "  T.sw = (T.sw || 0) + clamp(want - (T.sw || 0), -TUR_SWV * dt, TUR_SWV * dt);\n"
               "}\n"
               "// where a locked rival will be when a shot fired now lands on them: found by trying where they'll be after the flight time, and the\n"
               "// flight time to there, a few times over (each time with the very lob the shot will take; a rival in the air, where its jump will have\n"
               "// taken it); lead held to 7 units. The low, quick lob if nothing's in its way, else the usual higher one\n"
               "function turretLead(D, O, x0, y0, z0) {\n"
               "  const v = D.turret.lv || { vx: 0, vz: 0 }; let tx = O.x, tz = O.z, ty = O.y + PR * 0.7, tf = 0, low = true;\n"
               "  for (let pass = 0; pass < 2; pass++) {\n"
               "    tx = O.x; tz = O.z; ty = O.y + PR * 0.7;\n"
               "    for (let i = 0; i < 4; i++) { tf = shotLob(x0, y0, z0, Math.atan2(tx - x0, tz - z0), Math.max(0.5, Math.hypot(tx - x0, tz - z0)), ty, low).tf; const lx = v.vx * tf, lz = v.vz * tf, ll = Math.hypot(lx, lz), c = ll > 7 ? 7 / ll : 1; tx = O.x + lx * c; tz = O.z + lz * c;\n"
               "      if (O.air) { const g = surfaceUnder(tx, tz, O.y + 1, true); ty = Math.max(O.y + (O.vy || 0) * tf - 0.6 * GRAV * tf * tf, g > -Infinity ? g : O.y - 9) + PR * 0.7; } }\n"
               "    if (!low || !lobBlocked(x0, y0, z0, tx, tz, ty, true)) break; low = false;\n"
               "  }\n"
               "  return { tx, tz, ty, tf, low };\n"
               "}\n"
               "// whether a shot's lob to there would run into something on the way (a wall or a box)\n"
               "function lobBlocked(x0, y0, z0, tx, tz, ty, low) {\n"
               "  const a = Math.atan2(tx - x0, tz - z0), d = Math.max(0.5, Math.hypot(tx - x0, tz - z0)), L = shotLob(x0, y0, z0, a, d, ty, low), sa = Math.sin(a), ca = Math.cos(a);\n"
               "  for (let i = 1; i <= 8; i++) { const t = L.tf * i / 9; if (shotBlocked(x0 + sa * L.hv * t, z0 + ca * L.hv * t, y0 + L.vy * t - 0.5 * SHOT_G * t * t)) return true; } return false;\n"
               "}\n"
               "// where a turret's next shot is headed: yours at the rival it has locked onto, where they'll be (else straight ahead, near to far and\n"
               "// back along a lane); a CPU's sweep near to far and back, or go for a foe in front\n"
               "function turretTarget(D, x0, z0) {\n"
               "  const T = D.turret; let a = D.yaw, d, ty, foe = null;\n"
               "  if (!D.ai) { a = D.yaw + (T.sw || 0); if (T.lk && T.lk.st === 'play') { const y0 = D.y + (TURRET_RIG.tip.y + 0.82 + 0.3) * PR, L = turretLead(D, T.lk, x0, y0, z0); return { a: Math.atan2(L.tx - x0, L.tz - z0), d: Math.max(0.5, Math.hypot(L.tx - x0, L.tz - z0)), ty: L.ty, foe: T.lk, low: L.low }; }\n"
               "    d = TUR_MID - 3 + 6 * (0.5 + 0.5 * Math.sin(T.ph * 0.8)); const g = surfaceUnder(x0 + Math.sin(a) * d, z0 + Math.cos(a) * d, D.y + 8, true); return { a, d, ty: g > -Infinity ? g : D.y, foe: null }; }\n")
    # ---- the shot's lob, shared by the shot and the lead (so the lead is worked out from the flight the shot really takes); a locked shot
    # of yours flies lower and quicker
    s = rep(s, "  const T = D.turret, k = PR, cy = Math.cos(D.yaw), sy = Math.sin(D.yaw), tp = TURRET_RIG.tip;\n",
               "  const T = D.turret, k = PR, ay = D.yaw + (T.sw || 0), cy = Math.cos(ay), sy = Math.sin(ay), tp = TURRET_RIG.tip; // (v375: out along the head, swung or not)\n")
    s = rep(s, "  // a lob, not a line: it always arcs well clear of the higher end (so a shot onto a platform drops onto its top instead of hitting its side)\n"
               "  // (but under a low platform it keeps under it: the lob is capped below anything overhead along the first part of its path)\n"
               "  let ceil = Infinity;",
               "  const { tf, vy, hv } = shotLob(x0, y0, z0, a, d, ty, !!tt.low);\n"
               "  shots.push({ x: x0, y: y0, z: z0, vx: Math.sin(a) * hv, vy, vz: Math.cos(a) * hv, by: D, team: D.team, tg: tt.foe, life: 4, acc: 0, ph: Math.random() * 6.28, spin: (Math.random() < 0.5 ? -1 : 1) * (3 + Math.random() * 4) });\n"
               "  T.kick = 1; D.squash = Math.max(D.squash, 0.2); { const Vs = vOf(D); if (Vs && Vs.slime) Vs.slime.fire(); }\n"
               "  for (let i = 0; i < 3; i++) spawnPart(x0, y0, z0, Math.sin(a) * (2 + Math.random() * 3) + (Math.random() - 0.5) * 1.5, 0.5 + Math.random() * 1.5, Math.cos(a) * (2 + Math.random() * 3) + (Math.random() - 0.5) * 1.5, 0.22, tmat(D), 0.4);\n"
               "  if (hearable(D)) AU.shoot();\n"
               "}\n"
               "// a shot's lob from (x0, y0, z0), heading a, to land d out at height ty: its flight time, its speed up and its speed across\n"
               "// a lob, not a line: it always arcs well clear of the higher end (so a shot onto a platform drops onto its top instead of hitting its side)\n"
               "// (but under a low platform it keeps under it: the lob is capped below anything overhead along the first part of its path). low (v375):\n"
               "// a lower, quicker arc, for your shots at a rival you've locked onto\n"
               "function shotLob(x0, y0, z0, a, d, ty, low) {\n"
               "  let ceil = Infinity;")
    s = rep(s, "  let tf = Math.max(0.15, d / SHOT_V), vy = (ty - y0 + 0.5 * SHOT_G * tf * tf) / tf; const top = Math.min(Math.max(y0, ty) + 1.1 + 0.07 * d, ceil - 0.3);\n",
               "  let tf = Math.max(0.15, d / SHOT_V), vy = (ty - y0 + 0.5 * SHOT_G * tf * tf) / tf; const top = Math.min(Math.max(y0, ty) + (low ? 0.45 + 0.035 * d : 1.1 + 0.07 * d), ceil - 0.3);\n")
    s = rep(s, "  for (let k = 0; k < 20 && vy > 0 && y0 + vy * vy / (2 * SHOT_G) > ceil - 0.3 && tf > 0.22; k++) { tf *= 0.92; vy = (ty - y0 + 0.5 * SHOT_G * tf * tf) / tf; } // flatter and quicker to get under it\n"
               "  const hv = d / tf;\n"
               "  shots.push({ x: x0, y: y0, z: z0, vx: Math.sin(a) * hv, vy, vz: Math.cos(a) * hv, by: D, team: D.team, tg: tt.foe, life: 4, acc: 0, ph: Math.random() * 6.28, spin: (Math.random() < 0.5 ? -1 : 1) * (3 + Math.random() * 4) });\n"
               "  T.kick = 1; D.squash = Math.max(D.squash, 0.2); { const Vs = vOf(D); if (Vs && Vs.slime) Vs.slime.fire(); }\n"
               "  for (let i = 0; i < 3; i++) spawnPart(x0, y0, z0, Math.sin(a) * (2 + Math.random() * 3) + (Math.random() - 0.5) * 1.5, 0.5 + Math.random() * 1.5, Math.cos(a) * (2 + Math.random() * 3) + (Math.random() - 0.5) * 1.5, 0.22, tmat(D), 0.4);\n"
               "  if (hearable(D)) AU.shoot();\n"
               "}\n",
               "  for (let k = 0; k < 20 && vy > 0 && y0 + vy * vy / (2 * SHOT_G) > ceil - 0.3 && tf > 0.22; k++) { tf *= 0.92; vy = (ty - y0 + 0.5 * SHOT_G * tf * tf) / tf; } // flatter and quicker to get under it\n"
               "  return { tf, vy, hv: d / tf };\n"
               "}\n")
    # ---- drawn: the turret faces where its head has swung (you and the camera don't)
    s = rep(s, "  if (V.yawD === undefined || D.st !== 'play' || (state !== 'play' && state !== 'dead')) { V.yawD = D.yaw; V.yawSnap = false; }\n"
               "  else { const d = wrapA(D.yaw - V.yawD); if (Math.abs(d) > 0.3 + 8 * dt) V.yawSnap = true; if (V.yawSnap) { V.yawD += d * Math.min(1, dt * 16); if (Math.abs(wrapA(D.yaw - V.yawD)) < 0.03) V.yawSnap = false; } else V.yawD = D.yaw; }\n",
               "  const DY = D.yaw + (D.turret && D.turret.sw ? D.turret.sw : 0); // (v375: a turret faces where its head has swung)\n"
               "  if (V.yawD === undefined || D.st !== 'play' || (state !== 'play' && state !== 'dead')) { V.yawD = DY; V.yawSnap = false; }\n"
               "  else { const d = wrapA(DY - V.yawD); if (Math.abs(d) > 0.3 + 8 * dt) V.yawSnap = true; if (V.yawSnap) { V.yawD += d * Math.min(1, dt * 16); if (Math.abs(wrapA(DY - V.yawD)) < 0.03) V.yawSnap = false; } else V.yawD = DY; }\n")
    # ---- the ring: on the rival you've locked onto, where the shots will meet them; with no lock, still, in the middle of the lane ahead
    s = rep(s, "  if (D === P) { const on = !!D.turret && D.st === 'play' && state === 'play'; turretMark.g.visible = on; if (on) { const k = PR, cy = Math.cos(D.yaw), sy = Math.sin(D.yaw), tp = TURRET_RIG.tip, tt = turretTarget(D, D.x + (tp.x * cy + tp.z * sy) * k, D.z + (-tp.x * sy + tp.z * cy) * k), gy = tt.foe ? tt.foe.y : tt.ty;\n"
               "    turretMark.g.position.set(D.x + Math.sin(tt.a) * tt.d, gy + 0.05, D.z + Math.cos(tt.a) * tt.d);",
               "  if (D === P) { const on = !!D.turret && D.st === 'play' && state === 'play'; turretMark.g.visible = on; if (on) { const k = PR, ay = D.yaw + (D.turret.sw || 0), cy = Math.cos(ay), sy = Math.sin(ay), tp = TURRET_RIG.tip, x0 = D.x + (tp.x * cy + tp.z * sy) * k, z0 = D.z + (-tp.x * sy + tp.z * cy) * k, tt = turretTarget(D, x0, z0), md = tt.foe ? tt.d : TUR_MID, ma = tt.foe ? tt.a : ay, mx = x0 + Math.sin(ma) * md, mz = z0 + Math.cos(ma) * md, mg = tt.foe ? tt.foe.y : surfaceUnder(mx, mz, D.y + 8, true), gy = mg > -Infinity ? mg : D.y; // (v375: still in the lane's middle with no lock)\n"
               "    turretMark.g.position.set(mx, gy + 0.05, mz);")
    return s
