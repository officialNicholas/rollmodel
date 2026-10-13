"""v254: the mid-air dash. A dash curls the character into a ball and tumbles it (forward or back); the backward dash is only for
coming out of a basin (a hop, the roll out over the rim, or the burst), never off an ordinary jump."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:120]); return s.replace(a, b)
def apply(s):
    # every blob carries the flag from the start (one shape for all of them)
    s = rep(s, "lastHit: null, kx: 0, kz: 0, airSling: false, dashT: 0, dashDir: 0, kod: 0,", "lastHit: null, kx: 0, kz: 0, airSling: false, airBack: false, dashT: 0, dashDir: 0, kod: 0,")
    # a jump: the forward dash only
    s = rep(s, "D.air = true; D.vy = JUMP_V; D.airSling = true; D.stroke++;", "D.air = true; D.vy = JUMP_V; D.airSling = true; D.airBack = false; D.stroke++;")
    # out of a basin, any way: both
    s = rep(s, "p.cool = 1.0; p.bounce = 0.7; p.occ = null; D.pot = null; D.st = 'play'; D.stroke++; D.y = p.y + 0.55; D.air = true;", "p.cool = 1.0; p.bounce = 0.7; p.occ = null; D.pot = null; D.st = 'play'; D.stroke++; D.y = p.y + 0.55; D.air = true; D.airSling = true; D.airBack = true;")
    s = rep(s, "D.freeLand = true; D.turn = 0; D.airSling = true; D.kx = D.kz = 0;", "D.freeLand = true; D.turn = 0; D.airSling = true; D.airBack = true; D.kx = D.kz = 0;")
    # the dash itself: back only when allowed; either way it's spent
    s = rep(s, "  if (!(D.st === 'play' && D.air && D.airSling && canAct(D)) || D.slam) return false;\n  if (D.charging) clearCharge(D);\n  const s = airShot(D, DASH_C,",
               "  if (!(D.st === 'play' && D.air && D.airSling && canAct(D)) || D.slam) return false;\n  if (dir < 0 && !D.airBack) return false; // (back only coming out of a basin)\n  if (D.charging) clearCharge(D);\n  const s = airShot(D, DASH_C,")
    s = rep(s, "D.airSling = false; D.vy = vy; D.spd = dist / Math.max(0.2, T);", "D.airSling = false; D.airBack = false; D.vy = vy; D.spd = dist / Math.max(0.2, T);")
    # landing and knock-outs clear it
    s = rep(s, "D.squash = 0.6 + 0.4 * impact; D.airSling = false; D.dashDir = 0;", "D.squash = 0.6 + 0.4 * impact; D.airSling = false; D.airBack = false; D.dashDir = 0;")
    s = rep(s, "D.lastHit = null; D.kx = D.kz = 0; D.airSling = false; D.freeLand = false;", "D.lastHit = null; D.kx = D.kz = 0; D.airSling = false; D.airBack = false; D.freeLand = false;")
    # the controls: a swipe down (or S) mid-air dashes back only when a basin allows it
    s = rep(s, "else if (P.air && P.airSling && -up > 44 && -up > side * 1.5)", "else if (P.air && P.airSling && P.airBack && -up > 44 && -up > side * 1.5)")
    s = rep(s, "if (state === 'play' && P.air && P.airSling) { airDash(P, -1); return; }", "if (state === 'play' && P.air && P.airSling && P.airBack) { airDash(P, -1); return; }")
    # the CPU plays by the same rule
    s = rep(s, "for (const dir of [1, -1]) { const sh = airShot(D, DASH_C,", "for (const dir of D.airBack ? [1, -1] : [1]) { const sh = airShot(D, DASH_C,")
    # the look: a ball for the dash, tumbling the way it goes (forward or back), opening out as it ends
    s = rep(s, "|| D.rollOutT > (V.balled ? 0.1 : 0.16) || D.rollT > (V.balled ? ROLL_T - ROLL_DASH : ROLL_T - ROLL_DASH + 0.06)))",
               "|| D.rollOutT > (V.balled ? 0.1 : 0.16) || D.dashT > (V.balled ? 0.05 : 0.1) || D.rollT > (V.balled ? ROLL_T - ROLL_DASH : ROLL_T - ROLL_DASH + 0.06)))")
    s = rep(s, "+ (D.rollOutT > 0 ? 6.2832 * (1 - Math.pow(D.rollOutT / ROLL_OUT_T, 1.6)) : 0) + V.pullLean",
               "+ (D.rollOutT > 0 ? 6.2832 * (1 - Math.pow(D.rollOutT / ROLL_OUT_T, 1.6)) : 0) + (D.dashT > 0 && D.st === 'play' ? (D.dashDir < 0 ? -1 : 1) * 6.2832 * (1 - Math.pow(D.dashT / DASH_T, 1.5)) : 0) + V.pullLean")
    s = rep(s, "|| D.rollOutT > 0.12 || (D.slam && !D.missile", "|| D.rollOutT > 0.12 || D.dashT > 0.05 || (D.slam && !D.missile")
    # the how-to-play lines
    s = rep(s, "swipe up to roll, swipe up or down mid-jump to dash.", "swipe up to roll, swipe up mid-jump to dash.", 2)
    s = rep(s, "'Hide in a ' + pw + ' to refill. Jump, or burst out of it, then swipe up or down in mid-air to dash forward or back. You can\\'t be touched while you dash.",
               "'Hide in a ' + pw + ' to refill. Swipe up mid-jump to dash forward, curled into a ball. Coming out of a ' + pw + ', you can swipe down to dash back as well. You can\\'t be touched while you dash.")
    return s
