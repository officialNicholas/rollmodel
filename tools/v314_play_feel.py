"""v314: two feel changes in play.

- Sideways (landscape), the play view sits 10% closer: height and distance behind both scaled by 0.9, so you see less of the stage
  and your character is a little bigger. Upright is as before.
- As a giant, your turning is scaled by 0.7. A giant rolls 1.75x as fast, and at full steer it turned about 60% faster than a normal
  roll (4.4 radians a second against 2.8: twitchy). Now it turns at 2.5, about a normal roll's rate, so its turns are wider and
  heavier. (Measured with the game's own steering, stepped by hand.) It's your own turning only; the CPUs are as before."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "const GIANT_T = 5, GIANT_K = 3, GIANT_SPD = 1.75, GIANT_SLAM = 1.5,",
               "const GIANT_T = 5, GIANT_K = 3, GIANT_SPD = 1.75, GIANT_SLAM = 1.5, GIANT_TURN = 0.7, /* (v314: your turning, as a giant) */")
    s = rep(s, "want = input * TURN * scaleBy * agile * (D === P && !P.ai && !kcam ? turnK() : 1);",
               "want = input * TURN * scaleBy * agile * (D === P && !P.ai && !kcam ? turnK() * (D.giantT > 0 ? GIANT_TURN : 1) : 1);")
    s = rep(s, "lean = -clamp(st.err, -1, 1) * TURN * turnK() * 0.6 *",
               "lean = -clamp(st.err, -1, 1) * TURN * turnK() * (D.giantT > 0 ? GIANT_TURN : 1) * 0.6 *")
    s = rep(s, "const ko = P.st === 'ko' ? 1 : 0, fx = Math.sin(camYaw), fz = Math.cos(camYaw), h = 7.75 + camCharge * 3 + look.roll * 1.2 + (P.slam ? P.y * 0.6 : 0) + ko * 4 + (VP.gk - 1) * 2.6 + camFoe * 0.9 + camTur * 2.4 + camPot * 2.2, back = 5.65 + camCharge * 1.5 + ko * 3 + (VP.gk - 1) * 1.6 + camFoe * 1.2 + camTur * 1.4 + camPot * 1.8;",
               "const camIn = viewW > viewH ? 0.9 : 1, ko = P.st === 'ko' ? 1 : 0, fx = Math.sin(camYaw), fz = Math.cos(camYaw), h = (7.75 + camCharge * 3 + look.roll * 1.2 + (P.slam ? P.y * 0.6 : 0) + ko * 4 + (VP.gk - 1) * 2.6 + camFoe * 0.9 + camTur * 2.4 + camPot * 2.2) * camIn, back = (5.65 + camCharge * 1.5 + ko * 3 + (VP.gk - 1) * 1.6 + camFoe * 1.2 + camTur * 1.4 + camPot * 1.8) * camIn; // (v314: sideways, the view sits 10% closer)")
    return s
