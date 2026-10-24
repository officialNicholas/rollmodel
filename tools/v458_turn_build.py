"""v458: a turn you keep holding tightens up; steer the other way and it's back to normal at once.

- The user: "the more a user turns and is still trying to turn further, they probably need to do a sharper turn, so we start to make
  the character turn a little quicker temporarily... Then when going the other direction, even for a little bit it goes back."
- While you hold a steer one way (stick past about a third), the game counts how far you've turned in that direction. Past about
  30 degrees the turn rate starts to climb, up to 45% quicker by about 125 degrees, easing in over a moment so it never jerks.
- Ease the stick back near the middle, steer the other way even briefly, jump, or charge a slingshot, and the count clears; the extra
  falls away within a few frames. Only your own character on the controls; CPUs and online rivals turn as before.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    a = "  const sr = D.spd / cfg.speed, agile = D.turret && !D.air ?"
    s = rep(s, a,
        "  let tbx = 1; if (D === P && !P.ai && !kcam) { // (v458) a turn held one way builds: the further you've turned, the tighter it gets; the other way resets it\n"
        "    const sg = Math.sign(input), held = Math.abs(input) > 0.35 && !D.air && !D.charging && D.st === 'play';\n"
        "    if (!held || sg !== D.tdir) { D.tacc = 0; D.tdir = held ? sg : 0; } else D.tacc += Math.abs(D.turn) * dt;\n"
        "    const k = clamp((D.tacc - 0.5) / 1.7, 0, 1), tb = held ? 0.45 * k * k * (3 - 2 * k) : 0, cur = D.tbst || 0;\n"
        "    D.tbst = cur + (tb - cur) * Math.min(1, dt * (tb > cur ? 5 : 25)); tbx = 1 + D.tbst; }\n" + a)
    s = rep(s, "want = input * TURN * scaleBy * agile *", "want = input * TURN * scaleBy * agile * tbx *")
    return s
