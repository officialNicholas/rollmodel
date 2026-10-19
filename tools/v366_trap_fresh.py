"""v366: a CPU right behind you gets caught by the trap you've just dropped (by v365's odds: easy 65%, medium 40%, hard 25%).

- A trap takes TRAP_ARM (0.6 s) to arm, and a CPU chasing you a few units back had rolled over it by then: nothing happened. That's the
  commonest way you drop one, to stop a chaser. Now a CPU makes up its mind about a trap while it's still arming too (v365's dice), and one
  the trap has caught out sets it off as soon as it's been down TRAP_EARLY (a beat, so it lands first). One that has seen it still rolls
  over it harmlessly while it arms, or goes round it.
- For you nothing changes: a trap still arms before it can catch you.
- A CPU only makes up its mind about a trap within a cone ahead of it (closer in, no more than about 35 degrees off its line), so a trap
  dropped right beside it doesn't pull it round in a hard turn."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "const TRAP_CATCH = { easy: 0.65, medium: 0.4, hard: 0.25 }, TRAP_SEE = 4.2, TRAP_LANE = 1.8;\n",
               "const TRAP_CATCH = { easy: 0.65, medium: 0.4, hard: 0.25 }, TRAP_SEE = 4.2, TRAP_LANE = 1.8;\n"
               "const TRAP_EARLY = 0.15; // (v366: a CPU a trap has caught out sets it off while it's still arming, once it's been down this long)\n")
    s = rep(s, "    if (T.arm > 0 || state !== 'play') continue;\n    if (T.owner !== P && !T.seen && P.st === 'play'",
               "    if (state !== 'play') continue; const armed = !(T.arm > 0);\n    if (armed && T.owner !== P && !T.seen && P.st === 'play'")
    s = rep(s, "      trapPop(T, D, D.rollT > 0 || D.giantT > 0); break;\n",
               "      if (!armed && !(T.t > TRAP_EARLY && D.cpu && D.ai && T.mind.get(D) === true)) continue; // (v366: while it arms, only a CPU it has caught out)\n"
               "      trapPop(T, D, D.rollT > 0 || D.giantT > 0); break;\n")
    s = rep(s, "    if (-(dx * fx + dz * fz) < 0.3 || Math.abs(dx * fz - dz * fx) > TRAP_LANE || !lineClear(D, T.x, T.z, T.y)) return; // (ahead, in its lane, nothing in between)\n",
               "    const ah = -(dx * fx + dz * fz), sd = Math.abs(dx * fz - dz * fx);\n"
               "    if (ah < 0.3 || sd > Math.min(TRAP_LANE, Math.max(0.6, ah * 0.7)) || !lineClear(D, T.x, T.z, T.y)) return; // (ahead, in its lane, nothing in between; v366: closer in, within ~35 degrees of its line)\n")
    return s
