# v250 gameplay changes, applied by ui190_patch.py: the lesson finale (no rollers, the orb timed to land the rocket on the buzzer), the
# locker's rotate swipe, the kill cam's steering, and blobs settling to the ground after the buzzer
def apply(s):
    def rep(old, new, count=1):
        nonlocal s
        c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
        s = s.replace(old, new)
    def cut(a, b, new):
        nonlocal s
        assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60], s.count(a), s.count(b))
        i = s.index(a); j = s.index(b); assert i < j
        s = s[:i] + new + s[j:]

    # ---- the lesson's finale: a few seconds to roll, then the orb, timed so the rocket comes down right on the buzzer
    cut("// the lesson's finale, the ten seconds after Ol' Bloop's card", "function tutNearSpot(ds, as, anyView) {",
        "// the lesson's finale, the ten seconds after Ol' Bloop's card: a few seconds just to roll and paint, then the orb right in front of you,\n"
        "// timed so its rocket comes down right on the buzzer: the clock waits while you go for it and while you're up there, the boost goes by\n"
        "// itself at the last moment if you haven't hit it, and the blast ends the match\n"
        "const TUT_ORB_AT = 3.4, TUT_HOV = 0.6; // (the orb with this long left; the least time the rocket hangs up there before it comes down)\n"
        "// how long a boosted dive takes to come down h metres, falling at v to start with\n"
        "function rkDiveT(h, v) { v = Math.max(14, v); h = Math.max(0, h); if (v >= ROCKET_DIVE) return h / v; const t1 = (ROCKET_DIVE - v) / 120, d1 = v * t1 + 60 * t1 * t1; return d1 >= h ? (Math.sqrt(v * v + 240 * h) - v) / 120 : t1 + (h - d1) / ROCKET_DIVE; }\n")
    cut("function tutFinRoller(side) {", "function tutFinOrb(sp) {",
        "function tutFinStart() {\n"
        "  tut.fin = { orb: false, orbT: 0, useTip: false, boostTip: false, rk: false, landed: false, outSw: false }; tut.orbMine = true; tut.items = true;\n"
        "  if (orb.on) tutOrbOff(); orb.spawnT = 1e9; itemSpawn.t = 1e9;\n"
        "}\n")
    cut("function tutFinTick(dt) {", "// the lesson's rival, far off and out of sight",
        "function tutFinTick(dt) {\n"
        "  const F = tut.fin;\n"
        "  if (!F.useTip && P.held === 'roller' && !P.rocket) { F.useTip = true; tutShow(say('*TAP* the roller!', 'Press *F* to roll!'), 'itemBtn', 'finuse', true, true); }\n"
        "  if (F.useTip && tutTip && tutTip.key === 'finuse' && P.held !== 'roller') tutHide();\n"
        "  if (!F.orb && matchLeft <= TUT_ORB_AT && !P.rocket && (P.st === 'play' || P.st === 'hide')) { const sp = tutNearSpot([2.8, 3.4, 2.3, 4], [0, 0.2, -0.2, 0.4, -0.4, 0.7, -0.7]) || tutNearSpot([2.6, 3.4, 4.2], [1, -1, 1.4, -1.4]) || tutNearSpot([2.6, 3.4], [0, 1, -1, 2, -2, 3.1], true); if (sp) { F.orb = true; tutFinOrb(sp); } }\n"
        "  // (not taken in a moment, it comes to you; still down in a basin, a finger shows the swipe out)\n"
        "  if (F.orb && orb.on && orb.stay) { F.orbT += dt; if (P.st === 'play' && !P.rocket) { const dx = P.x - orb.x, dz = P.z - orb.z, d = Math.hypot(dx, dz);\n"
        "      if (F.orbT > 0.8 && d > 0.01) { const st = Math.min(d, dt * 4.5); orb.x += dx / d * st; orb.z += dz / d * st; orb.tx = orb.x; orb.tz = orb.z; }\n"
        "      if (d < 1.3 && orb.k > 0.45) takeOrb(P); } if (P.st === 'hide' && !F.outSw) { F.outSw = true; tutGest('swipe'); } else if (P.st !== 'hide' && F.outSw) { F.outSw = false; tutGest(null); } }\n"
        "  // the clock never runs so low that the rocket can't come down right on the buzzer\n"
        "  if (!F.orb) { if (matchLeft < TUT_ORB_AT - 0.4) matchLeft = TUT_ORB_AT - 0.4; } // (nowhere to put it yet, or you're out: it waits for the orb)\n"
        "  else if (!F.rk && !P.rocket) matchLeft = Math.max(matchLeft, ROCKET_UP + TUT_HOV + rkDiveT(ROCKET_ALT - 0.35 * TUT_HOV, 14) + 0.03);\n"
        "  if (P.rocket) { F.rk = true; const R = P.rocket, gy = R.gy > -Infinity ? R.gy : P.y - ROCKET_ALT, h = P.y - gy;\n"
        "    if (R.ph === 'up') matchLeft = Math.max(matchLeft, ROCKET_UP - R.t + TUT_HOV + rkDiveT(R.top - gy - 0.35 * TUT_HOV, 14) + 0.03);\n"
        "    else if (R.ph === 'hover') {\n"
        "      if (!F.boostTip) { F.boostTip = true; tutShow(say('Tap *BOOST* to slam down!', 'Press *E* to slam down!'), 'slamBtn', 'finboost', true, true); }\n"
        "      const need = rkDiveT(h, 14);\n"
        "      if (R.t >= TUT_HOV && (matchLeft <= need + 0.03 || R.t > ROCKET_HOVER - 0.2)) rocketDive(P, false); // (not boosted yet: it boosts itself, just in time to land on the buzzer)\n"
        "      else matchLeft = Math.max(matchLeft, Math.max(0, TUT_HOV - R.t) + need + 0.03);\n"
        "    } else { if (R.slow) rocketDive(P, false); matchLeft = Math.max(matchLeft, rkDiveT(h, -P.vy) + 0.03); } }\n"
        "  else if (F.rk && !F.landed) { F.landed = true; tutHide(); matchLeft = 0; } // (the blast is the buzzer)\n"
        "}\n")

    # ---- the kill cam: it has your steering while it plays (round the other way, onto open floor, never off a drop); none in the lesson's finale
    rep("if (kcamUsed || mode !== 'duel' || state !== 'play' || P.rocket) return; kcamUsed = true;",
        "if (kcamUsed || mode !== 'duel' || state !== 'play' || P.rocket || (tut && tut.fin)) return; kcamUsed = true;")
    rep("kcam = { t: 0, x0: P.x, z0: P.z, gy, fx, fz, side: best.side, dist: best.dist, rev: best.rev, V, endAt: 1e9 };",
        "kcam = { t: 0, x0: P.x, z0: P.z, gy, fx, fz, side: best.side, dist: best.dist, rev: best.rev, V, endAt: 1e9, ...kcamTurn() };")
    rep("function kcamEnd() { if (!kcam) return; kcam = null; camSnap = true;",
        "function kcamEnd() { if (!kcam) return; kcam = null; camSnap = true; camYaw = P.yaw; camYawV = 0; if (P.st === 'play') P.spawnGuard = Math.max(P.spawnGuard, 1.6); /* (back behind you the way you're now facing, and steered clear of drops a moment longer) */")
    rep("function knockOut(D, reason, by) {\n",
        "// while the kill cam plays you can't see where you're going, so it steers for you: round the other way, onto the floor with the most room,\n"
        "// eased off for the turn (yaw: where to; dir: which way round when that's right behind you)\n"
        "function kcamTurn() {\n"
        "  const back = P.yaw + Math.PI; let yaw = back, bs = -1e9;\n"
        "  for (let i = 0; i < 16; i++) { const a = back + (i < 8 ? i : i - 16) / 16 * 6.2832, sc = openRun(P.x, P.z, P.y, a, 0.5, 7) - 1.1 * Math.abs(wrapA(a - back)); if (sc > bs) { bs = sc; yaw = a; } }\n"
        "  return { yaw, dir: openRun(P.x, P.z, P.y, P.yaw + 1.5708, 0.5, 4) >= openRun(P.x, P.z, P.y, P.yaw - 1.5708, 0.5, 4) ? 1 : -1 };\n"
        "}\n"
        "function kcamSteer(D, dt) {\n"
        "  let e = wrapA(kcam.yaw - D.yaw); if (Math.abs(e) > 2.6) e = kcam.dir * Math.abs(e);\n"
        "  if (!D.air && !D.charging) { const cap = cfg.speed * (Math.abs(e) > 0.5 ? 0.45 : 0.75); if (D.spd > cap) D.spd = Math.max(cap, D.spd - D.spd * 6 * dt); }\n"
        "  return clamp(-e * 2.4, -1, 1);\n"
        "}\n"
        "function knockOut(D, reason, by) {\n")
    rep("  let input = D === P ? (keyL || keyR ? (keyR ? 1 : 0) - (keyL ? 1 : 0) : steerIn) : D.steer;\n",
        "  let input = D === P ? (keyL || keyR ? (keyR ? 1 : 0) - (keyL ? 1 : 0) : steerIn) : D.steer;\n"
        "  if (D === P && kcam && kcam.yaw !== undefined && D.st === 'play') { input = kcamSteer(D, dt); if (!D.air && !D.charging && !D.slam) scaleBy = Math.max(scaleBy, 1.25); } // (the kill cam steers)\n")
    rep("let lean = 0; if (D === P && !P.ai && !D.air && !D.charging && Math.abs(input) > 0.4 && D.spd > 0.8) {",
        "let lean = 0; if (D === P && !P.ai && !D.air && !D.charging && !kcam && Math.abs(input) > 0.4 && D.spd > 0.8) {")
    rep("x0 = D.x, z0 = D.z, kx = D.kx * dt, kz = D.kz * dt;\n  let hit = false;\n",
        "x0 = D.x, z0 = D.z, kx = D.kx * dt, kz = D.kz * dt;\n  let hit = false;\n"
        "  if (D === P && kcam && !D.air && D.st === 'play' && surfaceUnder(D.x + fx * (0.3 + d), D.z + fz * (0.3 + d), D.y + STEP, true) === -Infinity) return; // (the kill cam: never rolled off a drop you can't see)\n")

    # ---- after the buzzer nothing else moves the blobs, so anyone caught in the air comes down where they are
    rep("} else if (state === 'dead' && outro) outroAge += dt * 4;",
        "} else if (state === 'dead') { endSettle(dt); if (outro) outroAge += dt * 4; }")
    rep("function step(dt) {\n",
        "// after the buzzer: anyone caught in the air (a hop, a fling, put back after the winner screen) comes down where they are and stays down\n"
        "// (over a hole, drifted back over the nearest floor first)\n"
        "function endSettle(dt) {\n"
        "  if (vic) return;\n"
        "  for (const D of ACTIVE) { if (D.st !== 'play' || D.pot) continue;\n"
        "    const g = surfaceUnder(D.x, D.z, D.y + STEP, true);\n"
        "    if (g === -Infinity) { if (!D.endTo || D.endTo.id !== runId) D.endTo = endFloor(D); const to = D.endTo; if (to.x !== undefined) { const dx = to.x - D.x, dz = to.z - D.z, d = Math.hypot(dx, dz), st = Math.min(d, 5 * dt); if (d > 1e-3) { D.x += dx / d * st; D.z += dz / d * st; } } continue; }\n"
        "    if (D.y <= g + 0.002) { if (D.y < g - 0.3) D.y = g; continue; }\n"
        "    if (!D.air) { D.air = true; D.vy = 0; } D.vy = Math.min(D.vy, 6) - GRAV * 1.45 * dt; D.y += D.vy * dt;\n"
        "    if (D.y <= g) { D.y = g; D.vy = 0; D.air = false; D.squash = Math.max(D.squash, 0.45); D.wob = 1; }\n"
        "  }\n"
        "}\n"
        "function endFloor(D) { for (let r = 0.5; r <= 6; r += 0.5) for (let k = 0; k < 16; k++) { const a = k / 16 * 6.2832, x = D.x + Math.sin(a) * r, z = D.z + Math.cos(a) * r; if (surfaceUnder(x, z, D.y + STEP, true) > -Infinity && !blockedAt(x, z, D.y)) return { id: runId, x, z }; } return { id: runId }; }\n"
        "function step(dt) {\n")

    # ---- the locker: when Ol' Bloop says take a look around, a finger swipes across you to show you can turn yourself round
    rep("  tutGest(state === 'play' ? TUT_GEST[key] : null);\n}",
        "  tutGest(state === 'play' ? TUT_GEST[key] : key === 'browse' && lookOpen ? 'spin' : null);\n}")
    rep("  const k = kind && !keysUI ? kind : ''; if (!tutGestEl.parentNode) stage.appendChild(tutGestEl);",
        "  const k = kind && (!keysUI || kind === 'spin') ? kind : ''; if (!tutGestEl.parentNode) stage.appendChild(tutGestEl);")
    rep("  if (tutGestEl.dataset.g !== k) { tutGestEl.dataset.g = k; tutGestEl.hidden = !k; }",
        "  if (tutGestEl.dataset.g !== k) { tutGestEl.dataset.g = k; tutGestEl.hidden = !k; tutGestEl.style.left = tutGestEl.style.top = ''; if (k === 'spin') { tutSpin0 = lookSwiped; tutSpinTick(); } }")
    rep("function tutFrame(rdt) {\n",
        "// the locker's swipe finger sits on you (wherever the camera has you), and goes once you've had a turn yourself\n"
        "let tutSpin0 = 0, lookSwiped = 0; // (lookSwiped: how far fingers have dragged the character round in the locker, in px)\n"
        "function tutSpinTick() {\n"
        "  if (!lookOpen || lookSwiped - tutSpin0 > 40) return tutGest(null);\n"
        "  tutGV.set(P.x, P.y + 0.2, P.z).project(camera); tutGestEl.style.left = ((tutGV.x + 1) / 2 * viewW).toFixed(0) + 'px'; tutGestEl.style.top = ((1 - tutGV.y) / 2 * viewH).toFixed(0) + 'px';\n"
        "}\n"
        "function tutFrame(rdt) {\n"
        "  if (tutGestEl.dataset.g === 'spin') tutSpinTick();\n")
    rep("shim.tgt += (e.clientX - lookDrag.x) * 0.012; lookDrag.x = e.clientX;", "lookSwiped += Math.abs(e.clientX - lookDrag.x); shim.tgt += (e.clientX - lookDrag.x) * 0.012; lookDrag.x = e.clientX;")
    rep("@media (prefers-reduced-motion:reduce){.tutgest .ghand,.tutgest .gring,.tutgest .gtrail{animation:none!important}.tutgest .gtrail{opacity:.6}}",
        ".tutgest[data-g=\"spin\"] .ghand{animation:gspin 2s ease-in-out infinite}\n"
        ".tutgest[data-g=\"spin\"] .gtrail{left:-62px;top:-4px;width:124px;transform-origin:0 50%;animation:gspintrail 2s ease-in-out infinite}\n"
        ".tutgest[data-g=\"spin\"] .gring{animation:gspinring 2s ease-out infinite}\n"
        "@keyframes gspin{0%{transform:translateX(-58px);opacity:0}10%{transform:translateX(-58px);opacity:1}20%{transform:translateX(-58px) scale(.88)}62%{transform:translateX(58px) scale(.88)}72%{transform:translateX(58px) scale(1);opacity:1}86%,100%{transform:translateX(58px) translateY(-10px);opacity:0}}\n"
        "@keyframes gspintrail{0%,20%{opacity:0;transform:scaleX(0)}62%{opacity:.85;transform:scaleX(1)}80%,100%{opacity:0;transform:scaleX(1)}}\n"
        "@keyframes gspinring{0%,14%{opacity:0;transform:translateX(-58px) scale(.4)}20%{opacity:1;transform:translateX(-58px) scale(.7)}36%,100%{opacity:0;transform:translateX(-58px) scale(1.4)}}\n"
        "@media (prefers-reduced-motion:reduce){.tutgest .ghand,.tutgest .gring,.tutgest .gtrail{animation:none!important}.tutgest .gtrail{opacity:.6}}")
    return s
