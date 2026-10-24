"""v469: a smoother rocket, and Ol' Bloop's Strokes and Commissions tips are back.

- The user: "Make the rocket feel smoother to control". Up on the rocket you used to move exactly along where you faced, so every
  twitch of the stick jerked your path (and the target under you). Now the rocket carries its own momentum: its drift eases toward
  where you steer over about a third of a second, so turns sweep in smooth arcs and the target glides. The turning itself is a touch
  gentler up there (1.25x the normal rate, was 1.5x), and it picks up speed more gradually after the climb. Boosting down still
  drops you right where the target was.
- The user: "The strokes tooltip and commissions tooltip should still be there". The lobby cards that open the Strokes page and the
  Commissions once you reach rank 3 show again (v441 had switched them off). Players who skipped the tutorial get them too; a save
  that skipped while they were off gets the Commissions card again once.
  The Strokes card no longer says Time trial and Showdown just unlocked (they're open from the start).
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "  if (R.ph !== 'up') steerAndTurn(D, dt, R.ph === 'dive' ? (R.slow ? 1.1 : 0.55) : 1.5);",
               "  if (R.ph !== 'up') steerAndTurn(D, dt, R.ph === 'dive' ? (R.slow ? 1.1 : 0.55) : 1.25); // (v469: 1.25, was 1.5)")
    s = rep(s, "    D.spd += (ROCKET_SPD - D.spd) * Math.min(1, dt * 4);\n    D.y = R.top - 0.35 * R.t",
               "    D.spd += (ROCKET_SPD - D.spd) * Math.min(1, dt * 2.6);\n    D.y = R.top - 0.35 * R.t")
    s = rep(s, "  const lim = ARENA - 0.8, fx = Math.sin(D.yaw), fz = Math.cos(D.yaw); D.x = clamp(D.x + fx * D.spd * dt, -lim, lim); D.z = clamp(D.z + fz * D.spd * dt, -lim, lim);\n  R.gy = surfaceUnder(",
               "  const lim = ARENA - 0.8, fx = Math.sin(D.yaw), fz = Math.cos(D.yaw);\n"
               "  // (v469) the rocket carries its own momentum: its drift eases toward where you face, so turns sweep in smooth arcs (a boost still drops near straight down)\n"
               "  if (R.vx === undefined) { R.vx = fx * D.spd; R.vz = fz * D.spd; } { const kv = Math.min(1, dt * (R.ph === 'dive' && !R.slow ? 12 : 3.2)); R.vx += (fx * D.spd - R.vx) * kv; R.vz += (fz * D.spd - R.vz) * kv; }\n"
               "  D.x = clamp(D.x + R.vx * dt, -lim, lim); D.z = clamp(D.z + R.vz * dt, -lim, lim);\n  R.gy = surfaceUnder(")
    # the Strokes and Commissions cards in the lobby, back on
    s = rep(s, "function tutStrokesDue() { return false && $('friendsModal').hidden &&", "function tutStrokesDue() { return $('friendsModal').hidden &&")
    s = rep(s, "function tutCommsDue() { return false && $('friendsModal').hidden &&", "function tutCommsDue() { return $('friendsModal').hidden &&")
    s = rep(s, "store.tut.skipped = 1; store.tut.m3 = 2; store.tut.comms = 1;", "store.tut.skipped = 1; store.tut.m3 = 2;")
    a = "if (store.tut.skipped && !store.tut.lite) {"
    s = rep(s, a, "if (store.tut.skipped && !store.tut.cm469) { store.tut.cm469 = 1; delete store.tut.comms; save(); } /* (v469: the Commissions card, back for those who skipped) */ " + a)
    s = rep(s, "'Strokes, Time trial and Showdown are unlocked. Let\u2019s start with Strokes.'", "'Strokes are open! Pick a special move and a skill to take into your matches.'") # (the modes are open from the start since v441)
    return s
