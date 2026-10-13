"""v254: turned round on the spot (the locker's drag, the winner's twirl, an intro's spin, an idle wiggle, the end-of-match spin), the
body answers it: the lower trunk and the tail lag into a deep C and swing back past straight when it stops, and the ears trail and
flare out with it. Outside a match the turn rate is read from the drawn heading itself, so every way of turning it counts."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
SPIN_K = 1.0   # (how strongly; 1 = the tuned amount)
def apply(s):
    # the turn rate, everywhere but a match (a match's turns are the crawl's own)
    s = rep(s, "o.dt = dt; o.spinV = D === P && P.shimNow === shim ? shim.vel : undefined;",
               "o.dt = dt; { const yd = V.yawDraw, pv = V.spinPrev; V.spinPrev = yd; const dy = pv === undefined ? 0 : wrapA(yd - pv), w = !(dt > 0) || Math.abs(dy) > 0.3 ? 0 : dy / dt; /* (a jump to a new heading, not a turn: ignored) */ V.spinW = (V.spinW || 0) + (clamp(w, -12, 12) - (V.spinW || 0)) * Math.min(1, dt * 16); }\n"
               "  o.spinV = D === P && P.shimNow === shim ? shim.vel : (state !== 'play' || vic) && D.st !== 'hide' ? V.spinW : undefined; // (v254: any turning on the spot outside a match)")
    # the trunk: a deeper C, eased in a little slower and swinging back past straight when the turning stops
    s = rep(s, "bend = L.bend = spr(L.bd, (spun ? 66 * Math.tanh(M.spin / 1.9) : Math.max(-78, Math.min(78, kap * 118))) * on, spun ? 48 : 55, spun ? 10 : 11, dt);",
               "bend = L.bend = spr(L.bd, (spun ? %s * Math.tanh(M.spin / 1.7) : Math.max(-78, Math.min(78, kap * 118))) * on, spun ? 38 : 55, spun ? 7.2 : 11, dt);" % round(80 * SPIN_K, 1))
    # the lower trunk takes more of it on a spin (the hips swing out behind), the chest less
    s = rep(s, "  this.worldTurn(out, sp[1], T * 0.34, 0);\n  this.worldTurn(out, sp[2], T * 0.37, -L.steer * 3 * act);\n  this.worldTurn(out, sp[3], T * 0.29, 0);",
               "  const spk = spun ? Math.min(1, Math.abs(bend) / 40) : 0; // (v254: on a spin the bend sits low, round the hips)\n  this.worldTurn(out, sp[1], T * (0.34 + 0.16 * spk), 0);\n  this.worldTurn(out, sp[2], T * (0.37 + 0.03 * spk), -L.steer * 3 * act);\n  this.worldTurn(out, sp[3], T * (0.29 - 0.12 * spk), 0);")
    # the tail: lagging well behind on its own slower spring, curling, and whipping past when it stops
    s = rep(s, "L.tlg = spr(L.tg || (L.tg = { x: 0, v: 0 }), bend, 24, 4, dt);", "L.tlg = spr(L.tg || (L.tg = { x: 0, v: 0 }), bend, spun ? 18 : 24, spun ? 2.6 : 4, dt);")
    s = rep(s, "(this.motion.spin !== undefined ? L.tlg * 0.27 : 0)", "(this.motion.spin !== undefined ? L.tlg * %s : 0)" % round(0.52 * SPIN_K, 2))
    # the ears: thrown out to the sides and back by the spin, trailing it
    s = rep(s, "add[j * 2] = -fl * 1.0 * (1 - L.act) + Math.min(1, L.v / 4) * 9 + 34 * lift - 62 * cov; add[j * 2 + 1] = -swing * 34 + fl * 2 * (1 - L.act) + sd * 24 * lift - sd * 30 * cov; }",
               "add[j * 2] = -fl * 1.0 * (1 - L.act) + Math.min(1, L.v / 4) * 9 + 34 * lift - 62 * cov + 22 * spf; add[j * 2 + 1] = -swing * (34 + 18 * spf) + fl * 2 * (1 - L.act) + sd * 24 * lift - sd * 30 * cov + sd * 26 * spf; }")
    s = rep(s, "const cov = (this.earCovF || (this.earCovF = new Follow(9))).step(clamp01(this.earCover || 0), dt);\n",
               "const cov = (this.earCovF || (this.earCovF = new Follow(9))).step(clamp01(this.earCover || 0), dt);\n"
               "      // (v254) spun round: flung out and back by it, and trailing it (on a slower follow, so they lag in and flop back)\n"
               "      const sp0 = M && M.spin !== undefined ? M.spin : 0, spf = (this.spinF || (this.spinF = new Follow(7))).step(clamp01(Math.abs(sp0) / 4.5), dt) * %s;\n" % SPIN_K)
    return s
