"""v405: the feel pass (the user: "tighten up controls, make the gameplay feel very solid. easy to control ... groundpounds, dodging,
being a giant, squishing people ... balanced and fair ... FPS needs to be smooth and consistent").

Controls
- A tap always jumps. Holding still for 150 ms starts the brake (and the slingshot), so a tap that lasted 150 to 260 ms used to come out
  as a short brake and no jump. Now a release inside the tap time (300 ms, was 260), with no drag and no pull, is a jump, at the speed
  you had before the brake caught it. Holding longer is still the brake.
- A second finger's tap always jumps. Resting the steering finger still for a moment starts the brake, and the brake used to swallow
  the jump; now the tap lets go of the brake and jumps (not while the slingshot is pulled back: that's a fling being aimed).
- The impact freeze (a few frames held on a hit) for someone else's pound now only happens when it lands where you can see it; a
  pound behind the camera used to freeze the game for 50 to 100 ms, which read as a hitch.
- The perfect dodge: a roll started in the last 0.15 s before a pound lands gets your roll straight back (and a gold ring, "Perfect
  dodge!"), so a well-read pound can be turned round on the one who threw it. Online the game server rules on it too.
- Inputs pressed a hair early come out on time: the pound pressed in the last moment of its cooldown, or in the last moment of being
  flattened or stunned, goes off the instant it can (no dead press, no "nope"); a dodge roll pressed in the last moment of a flatten or
  a stun rolls you out the instant you're free.

Balance (measured first: 144 offline matches with the game's own AI in every seat, hard, 36 each of 1v1, 3-way, Showdown and 2v2)
- What knocks players out: the pound, 58 to 63% of knock-outs in every mode. A pound with someone inside its ring knocks them out about
  55% of the time; the rest dodge it, by a jump (most) or a roll. Seats are fair: your seat won 19 of 36 1v1s, 31% of 3-ways (a third
  expected), a quarter-ish of Showdown places, 19 of 36 2v2s. Squishes: a giant's squish is followed by a knock-out 79% of the time, a
  stomp's 25%, a head-on flatten's 48% (Showdown).
- CPU giants wasted the spell: they pounded the floor for paint within 3 s (the pound ends the giant), and 20 of 24 got nothing. A CPU
  giant now keeps its pound for someone till the spell's last moment: more of them last the full 6 s and squish more (0.38 to 0.52 a
  spell), knock-outs a spell about the same. A human giant was never limited this way."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- a tap always jumps (even one the brake's timer caught), at the pace you had
    s = rep(s, "function beginHold(t, x, y) { slR = null; startCharge(P);",
               "function beginHold(t, x, y) { slR = null; P.holdSpd = P.st === 'play' && !P.air ? P.spd : 0; startCharge(P);")
    s = rep(s, "  if (P.charging && holdCharge) { if (pullTgt >= FLING_MIN) fling(P, pullTgt); else { cancelCharge(P); if (P.st === 'hide' && !t.moved && performance.now() - t.t < 450 && state === 'play') jump(P); } }\n"
               "  else if (!t.moved && performance.now() - t.t < 260 && state === 'play') jump(P);",
               "  if (P.charging && holdCharge) { if (pullTgt >= FLING_MIN) fling(P, pullTgt); else {\n"
               "    // (v405) let go inside the tap time, no drag, no pull: that was a tap the brake caught. A jump, at the pace you had\n"
               "    const tap = !t.moved && !t.pulled && performance.now() - t.t < TAP_MS && state === 'play';\n"
               "    if (tap && P.st === 'play' && !P.air) P.spd = Math.max(P.spd, P.holdSpd || 0);\n"
               "    cancelCharge(P); if (P.st === 'hide' ? !t.moved && performance.now() - t.t < 450 && state === 'play' : tap) jump(P); } }\n"
               "  else if (!t.moved && performance.now() - t.t < TAP_MS && state === 'play') jump(P);")
    s = rep(s, "const MAX_DRAG = 70, DEAD = 6, HOLD_MS = 150;", "const MAX_DRAG = 70, DEAD = 6, HOLD_MS = 150, TAP_MS = 300;")
    # ---- a second finger's tap always jumps: resting the steering finger still had started the brake, and the brake swallowed the jump
    #      (not while the band is pulled back: that's a fling being aimed). The resting finger's own lift is then no tap.
    s = rep(s, "/* (it may be a jump: a crouch at once) */ } else if (state === 'play') jump(P);",
               "/* (it may be a jump: a crouch at once) */ } else if (state === 'play') { if (P.charging && holdCharge && pullTgt < FLING_MIN && P.st === 'play') { cancelCharge(P); const t0 = touches.get(steerId); if (t0) t0.noTap = true; } jump(P); } // (v405)")
    s = rep(s, "  else if (!t.moved && performance.now() - t.t < TAP_MS && state === 'play') jump(P);",
               "  else if (!t.moved && !t.noTap && performance.now() - t.t < TAP_MS && state === 'play') jump(P);")
    # ---- pressed a hair early: the pound goes off the instant it's back (the end of its cooldown, a flatten, a stun)
    s = rep(s, "  if (!slamReady(D)) { if (D === P && (canAct(D) || D.st === 'hide') && !D.slam && D.slamCD <= 0) {",
               "  if (!slamReady(D) && D === P && !D.ai && !D.slam && !D.rocket && D.paint >= POUND_MIN && (D.st === 'play' || D.st === 'hide') && Math.max(D.slamCD, D.flatT, D.stunT || 0) > 0 && Math.max(D.slamCD, D.flatT, D.stunT || 0) < PRESS_EARLY) { D.slamBuf = PRESS_EARLY + 0.04; return false; } // (v405)\n"
               "  if (!slamReady(D)) { if (D === P && (canAct(D) || D.st === 'hide') && !D.slam && D.slamCD <= 0) {")
    s = rep(s, "  if (D.rollBuf > 0) { D.rollBuf -= dt; if (D.rollCD <= 0 && !D.air && D.st === 'play') { D.rollBuf = 0; dodgeRoll(D); } }",
               "  if (D.rollBuf > 0) { D.rollBuf -= dt; if (D.rollCD <= 0 && !D.air && D.st === 'play') { D.rollBuf = 0; dodgeRoll(D); } }\n"
               "  if (D.slamBuf > 0) { D.slamBuf -= dt; if (slamReady(D)) { D.slamBuf = 0; if (state === 'play') useSlam(D); } } // (v405: a pound pressed a hair early)")
    # ---- and the dodge roll pressed in the last moment of a flatten or a stun
    s = rep(s, "  if (!canAct(D) || D.slam || D.rollT > 0) return false;\n  if (D.air && D.airSling) return airDash(D, 1);",
               "  if (D === P && !D.ai && D.st === 'play' && !D.rocket && !D.turret && Math.max(D.flatT, D.stunT || 0) > 0 && Math.max(D.flatT, D.stunT || 0) < PRESS_EARLY) { D.rollBuf = Math.max(D.flatT, D.stunT || 0) + 0.06; return false; } // (v405: rolls you out the instant you're free)\n"
               "  if (!canAct(D) || D.slam || D.rollT > 0) return false;\n  if (D.air && D.airSling) return airDash(D, 1);")
    s = rep(s, "const ROLL_T = 0.5, ROLL_DASH = 0.32, ROLL_CD = 1.5, ROLL_COST = 0.03;",
               "const ROLL_T = 0.5, ROLL_DASH = 0.32, ROLL_CD = 1.5, ROLL_COST = 0.03, PRESS_EARLY = 0.2; // (v405: PRESS_EARLY, how early a pound or a roll can be pressed and still come out)")
    # ---- the impact freeze (a few frames held on a hit): for someone else's pound it only happens when you can see it land. Behind the
    #      camera it read as a hitch, not a hit
    s = rep(s, "function hitStop(t, A, B, x, z) { if (A === P || B === P || (x !== undefined && Math.hypot(x - P.x, z - P.z) < 14)) hold = Math.max(hold, t); }",
               "function hitStop(t, A, B, x, z) { if (A === P || B === P || (x !== undefined && Math.hypot(x - P.x, z - P.z) < 14 && onScreen(x, P.y, z))) hold = Math.max(hold, t); }\n"
               "const _osV = new THREE.Vector3(), onScreen = (x, y, z) => { _osV.set(x, y + 0.4, z).project(camera); return _osV.z < 1 && Math.abs(_osV.x) < 1.05 && Math.abs(_osV.y) < 1.05; }; // (v405)")
    # ---- the perfect dodge: a roll started in the last moment before a pound lands (PERFECT_DODGE) gets the roll straight back, so you
    #      can turn the dodge into a counter. Online the server rules on it (it says so in its 'dodged')
    s = rep(s, "function dodgedPound(O, D) {\n  O.immuneT = Math.max(O.immuneT, 0.25); O.wob = 1; emote(O, 'smug', 0.9);",
               "function dodgedPound(O, D, perfectNet) {\n  const perfect = NM ? !!perfectNet : safe(O) && O.rollT > ROLL_T - PERFECT_DODGE; if (perfect) { O.rollCD = 0; O.rollBuf = 0; } // (v405)\n  O.immuneT = Math.max(O.immuneT, 0.25); O.wob = 1; emote(O, 'smug', 0.9);")
    s = rep(s, "  if (O === P) { popText('Dodged!'); buzz(12); AU.ready(); } else if (D === P) popText('It dodged!');\n}\nfunction poundHit(",
               "  if (perfect) { shockwave(O.x, O.y, O.z, 2.2, 0xFFE07A); for (let i = 0; i < 14; i++) { const a = i / 14 * 6.283; spawnPart(O.x, O.y + 0.3, O.z, Math.cos(a) * 3.4, 1 + Math.random() * 1.5, Math.sin(a) * 3.4, 0.4, orbPartMats[i % orbPartMats.length], 0.6); } }\n"
               "  if (O === P) { popText(perfect ? 'Perfect dodge!' : 'Dodged!'); buzz(perfect ? [10, 25, 30] : 12); AU.ready(); if (perfect) slow = Math.max(slow, 0.22); } else if (D === P) popText(perfect ? 'Perfect dodge!' : 'It dodged!');\n}\nfunction poundHit(")
    s = rep(s, "function netDodged(m) { const D = netBlob(m.slot), A = netBlob(m.by); if (D && A && D.st !== 'ko') dodgedPound(D, A); }",
               "function netDodged(m) { const D = netBlob(m.slot), A = netBlob(m.by); if (D && A && D.st !== 'ko') dodgedPound(D, A, m.perfect); }")
    s = rep(s, "PRESS_EARLY = 0.2; // (v405: PRESS_EARLY, how early a pound or a roll can be pressed and still come out)",
               "PRESS_EARLY = 0.2, PERFECT_DODGE = 0.15; // (v405: PRESS_EARLY, how early a pound or a roll can be pressed and still come out; PERFECT_DODGE, a roll this close before a pound lands gets the roll straight back)")
    # ---- a CPU giant keeps its pound for someone (the pound ends the giant): no pounding the floor for paint until the spell's last moment
    s = rep(s, "if (n && Math.hypot(n.x - D.x, n.z - D.z) < 0.95 && Math.abs(n.h - D.y) < 0.3) { ai.poundAt = -1; ai.thinkT = 0; if (pudNear[n.id] || D.paint - SLAM_COST > Math.max(0.3, ai.need + 0.04)) return useSlam(D); }",
               "if (n && Math.hypot(n.x - D.x, n.z - D.z) < 0.95 && Math.abs(n.h - D.y) < 0.3) { ai.poundAt = -1; ai.thinkT = 0; if (!(D.giantT > 0.8) && (pudNear[n.id] || D.paint - SLAM_COST > Math.max(0.3, ai.need + 0.04))) return useSlam(D); } // (v405: a giant keeps its pound for someone)")
    return s
