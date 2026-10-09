import sys, re
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:140])); sys.exit(1)
    s = s.replace(a, b)

# ---------- the dodge roll ----------
rep("airSling: false, ai: null };", "airSling: false, rollT: 0, rollCD: 0, rollBuf: 0, rollV: 0, ai: null };")
rep("""// you jumped roughly toward the orb: turn you onto it and carry you there at the top of the hop""",
"""// swipe up: a quick forward roll. A burst of speed, and nothing can touch you while you tumble (pounds, rams, stomps, splashes, blasts)
const ROLL_T = 0.32, ROLL_CD = 1.3, ROLL_COST = 0.04;
function dodgeRoll(D) {
  if (D.st === 'hide') { exitPot(D); return false; }
  if (!canAct(D) || D.slam || D.rollT > 0) return false;
  if (D.air) { D.rollBuf = 0.18; return false; } // pressed just before landing: roll as you touch down
  if (D.rollCD > 0) { if (D.rollCD < 0.25) D.rollBuf = D.rollCD + 0.03; return false; } // a hair early: roll the moment it's back
  if (D.dry) { if (D === P) { kick($('ttrack'), 'nope'); AU.nope(); popText('No blood'); } return false; }
  if (D.charging) clearCharge(D);
  const base = cfg.speed * speedMul * (D.cpu ? AI.speed : 1);
  D.rollT = ROLL_T; D.rollCD = ROLL_CD; D.rollBuf = 0; D.rollV = Math.max(D.spd, base) + base * 1.15;
  D.spd = D.rollV; D.turn *= 0.3; D.squash = Math.max(D.squash, 0.35); D.wob = Math.max(D.wob, 0.5);
  if (D.giantT <= 0) D.paint = Math.max(0.001, D.paint - ROLL_COST);
  const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw);
  for (let i = 0; i < 10; i++) { const s2 = (Math.random() - 0.5) * 2.4; spawnPart(D.x - fx * 0.25, D.y + 0.2, D.z - fz * 0.25, -fx * 2.2 + fz * s2, 1.2 + Math.random() * 1.6, -fz * 2.2 - fx * s2, 0.4, tmat(D), 0.55); }
  if (hearable(D)) AU.dash();
  if (D === P) { buzz(10); fovKick = Math.max(fovKick, 5); }
  return true;
}
// you jumped roughly toward the orb: turn you onto it and carry you there at the top of the hop""")
rep("function startSlam(D) { cap(D); D.air = true;", "function startSlam(D) { cap(D); D.rollT = 0; D.air = true;")
rep("  D.st = 'ko'; D.dilT = 0;", "  D.st = 'ko'; D.rollT = 0; D.dilT = 0;")

# timers, steering and speed while rolling
rep("  if (D.st === 'ko') { D.koT -= dt; if (D.koT <= 0) respawnBlob(D); return; }\n",
    "  if (D.st === 'ko') { D.koT -= dt; if (D.koT <= 0) respawnBlob(D); return; }\n  if (D.rollCD > 0) D.rollCD -= dt; if (D.rollT > 0) D.rollT = Math.max(0, D.rollT - dt);\n  if (D.rollBuf > 0) { D.rollBuf -= dt; if (D.rollCD <= 0 && !D.air && D.st === 'play') { D.rollBuf = 0; dodgeRoll(D); } }\n")
rep("  else steerAndTurn(D, dt, D.slam ? 0 : D.air ? (D.knockT > 0 ? 0.12 : D.charging ? 0.85 : 0.65) : D.charging ? 0.75 : 1);",
    "  else steerAndTurn(D, dt, D.slam ? 0 : D.air ? (D.knockT > 0 ? 0.12 : D.charging ? 0.85 : 0.65) : D.charging ? 0.75 : D.rollT > 0 ? 0.4 : 1);")
rep("  else if (!D.air) { let tgt = cfg.speed",
    "  else if (!D.air && D.rollT > 0) D.spd = D.rollV * (0.62 + 0.38 * D.rollT / ROLL_T);\n  else if (!D.air) { let tgt = cfg.speed")

# nothing lands on you mid-roll
rep("    if (Math.abs(base - D.y) < 1.4) { if (lift > 0.6) dodgedPound(O, D); else",
    "    if (Math.abs(base - D.y) < 1.4) { if (lift > 0.6 || O.rollT > 0) dodgedPound(O, D); else")
rep("  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - p.x, O.z - p.z) < KO_R + 1 && Math.abs(O.y - p.y) < 1.6) burstPush(O, p, D);",
    "  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - p.x, O.z - p.z) < KO_R + 1 && Math.abs(O.y - p.y) < 1.6) { if (O.rollT > 0) dodgedPound(O, D); else burstPush(O, p, D); }")
rep("if (B.st === 'play' && !B.air && B.immuneT <= 0 && B.giantT <= 0 && Math.abs(B.y - D.y) < 3 && bd < 16)",
    "if (B.st === 'play' && !B.air && B.immuneT <= 0 && !(B.rollT > 0) && B.giantT <= 0 && Math.abs(B.y - D.y) < 3 && bd < 16)")
rep("  const B = other(A); if (B.st !== 'play' || B.immuneT > 0 || B.slam || B.flatT > 0 || B.giantT > 0) return;",
    "  const B = other(A); if (B.st !== 'play' || B.immuneT > 0 || B.rollT > 0 || B.slam || B.flatT > 0 || B.giantT > 0) return;")
rep("if (d < PR * GIANT_K + PR + 0.1 && Math.abs(dy) < 1.6 && B.flatT <= 0 && B.immuneT <= 0) flatten(B, A, 'giant'); return; }",
    "if (d < PR * GIANT_K + PR + 0.1 && Math.abs(dy) < 1.6 && B.flatT <= 0 && B.immuneT <= 0 && !(B.rollT > 0)) flatten(B, A, 'giant'); return; }")
rep("A.spd > cfg.speed * speedMul * 1.15 && B.immuneT <= 0 && !(A.air", "A.spd > cfg.speed * speedMul * 1.15 && B.immuneT <= 0 && !(B.rollT > 0) && !(A.air")
rep("&& !A.slam && B.flatT <= 0 && B.immuneT <= 0) { flatten(B, A, 'stomp');", "&& !A.slam && B.flatT <= 0 && B.immuneT <= 0 && !(B.rollT > 0)) { flatten(B, A, 'stomp');")
rep("""  if (H.immuneT <= 0 && vP > 2.2 && vP - vC > RAM_EDGE) return flatten(H, P, 'roll');
  if (P.immuneT <= 0 && vC > 2.2 && vC - vP > RAM_EDGE) return flatten(P, H, 'roll');""",
"""  const rolling = P.rollT > 0 || H.rollT > 0; // a roll bumps, it never flattens (either way)
  if (!rolling && H.immuneT <= 0 && vP > 2.2 && vP - vC > RAM_EDGE) return flatten(H, P, 'roll');
  if (!rolling && P.immuneT <= 0 && vC > 2.2 && vC - vP > RAM_EDGE) return flatten(P, H, 'roll');""")

# the holy water rolls out of your pound when it's already facing away from it, and hops it otherwise
rep("if (ai.dodgeOK) { if (D.charging) cancelCharge(D); jump(D); return true; } }",
    """if (ai.dodgeOK) {
      if (D.rollT > 0) return true;
      const away = Math.sin(D.yaw) * (D.x - sc.x) + Math.cos(D.yaw) * (D.z - sc.z) > 0.2;
      if (away && D.rollCD <= 0 && !D.dry) { if (eta > 0.28) return false; if (D.charging) cancelCharge(D); dodgeRoll(D); return true; }
      if (D.charging) cancelCharge(D); jump(D); return true;
    } }""")

# a first-time tip, at the moment it matters
rep("    if (runT > 16 && slamReady(P) && H.st === 'play'",
    "    if (H.slam && P.st === 'play' && !P.air && Math.hypot(H.x - P.x, H.z - P.z) < slamRadius(H) + PR + 2.5) hint('roll', say('Swipe up to roll clear', 'Shift to roll clear'), 2.4);\n    else if (runT > 26) hint('roll', say('Swipe up to roll', 'Shift to roll'), 2.4);\n    if (runT > 16 && slamReady(P) && H.st === 'play'")

# controls: a quick flick up rolls; Shift or Q on a keyboard
rep("  touches.set(e.pointerId, { x: e.clientX, y: e.clientY, cx: e.clientX, cy: e.clientY, t: performance.now(), moved: false });",
    "  touches.set(e.pointerId, { x: e.clientX, y: e.clientY, cx: e.clientX, cy: e.clientY, t: performance.now(), moved: false, hist: [[e.clientX, e.clientY, performance.now()]] });")
rep("""  if (Math.abs(sx) > 9 || Math.abs(dy) > 9) t.moved = true;""",
    """  if (Math.abs(sx) > 9 || Math.abs(dy) > 9) t.moved = true;
  // a quick flick up: roll
  const now = performance.now(); t.hist.push([e.clientX, e.clientY, now]); while (t.hist.length > 2 && now - t.hist[0][2] > 180) t.hist.shift();
  if (!t.rolled && !P.charging && state === 'play') { const h0 = t.hist[0], up = h0[1] - e.clientY; if (up > 44 && up > Math.abs(e.clientX - h0[0]) * 1.5) { t.rolled = true; t.moved = true; t.steered = true; dodgeRoll(P); } }""")
rep("  if (!keysUI && (k.startsWith('Arrow') || (k.length === 1 && 'wasdeWASDE '.includes(k)))) { keysUI = true; paintHow(); }",
    "  if (!keysUI && (k.startsWith('Arrow') || k === 'Shift' || (k.length === 1 && 'wasdeqWASDEQ '.includes(k)))) { keysUI = true; paintHow(); }")
rep("  if ((k === 'e' || k === 'E' || k === 'Shift') && !e.repeat) { e.preventDefault(); if (state === 'play') useSlam(P); return; }",
    "  if ((k === 'e' || k === 'E') && !e.repeat) { e.preventDefault(); if (state === 'play') useSlam(P); return; }\n  if ((k === 'Shift' || k === 'q' || k === 'Q') && !e.repeat) { e.preventDefault(); if (state === 'play') dodgeRoll(P); return; }")
rep("""'<kbd>A</kbd> <kbd>D</kbd> or the arrows steer. <kbd>Space</kbd> jumps. Hold <kbd>S</kbd> to stop and load a fling, let go to fling. <kbd>E</kbd> pounds. <kbd>P</kbd> pauses, <kbd>M</kbd> mutes.' : 'Drag sideways to steer. Tap to jump. Hold to stop, then pull down and let go to fling. The arrow button pounds.'""",
    """'<kbd>A</kbd> <kbd>D</kbd> or the arrows steer. <kbd>Space</kbd> jumps, <kbd>Shift</kbd> rolls. Hold <kbd>S</kbd> to stop and load a fling, let go to fling. <kbd>E</kbd> pounds. <kbd>P</kbd> pauses, <kbd>M</kbd> mutes.' : 'Drag sideways to steer. Tap to jump, swipe up to roll. Hold to stop, then pull down and let go to fling. The arrow button pounds.'""")

# the roll's sound: a short rising swish with a soft bloop
rep("flip: 2, flipBack: 2 };", "flip: 2, flipBack: 2, dash: 2.4 };")
rep("    swish() { hiss({ k: 'p', type: 'bandpass', f: 700, f1: 2800, glide: 0.25, q: 1.8, dur: 0.28, v: 0.18 }); },",
    "    swish() { hiss({ k: 'p', type: 'bandpass', f: 700, f1: 2800, glide: 0.25, q: 1.8, dur: 0.28, v: 0.18 }); },\n    dash() { const k = rnd(0.95, 1.05); hiss({ k: 'p', type: 'bandpass', f: 420 * k, f1: 2400 * k, glide: 0.16, q: 1.6, dur: 0.22, v: 0.2 }); tone({ type: 'triangle', f: 260 * k, f1: 760 * k, glide: 0.09, dur: 0.11, v: 0.1, a: 0.002 }); tone({ d: 0.15, f: 190 * k, f1: 120 * k, glide: 0.07, dur: 0.09, v: 0.08 }); },")
open(F, 'w').write(s)
print('ok')
