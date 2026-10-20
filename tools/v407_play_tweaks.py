"""v407: three asks about play.
- A ground pound busts a rival's paint trap (the user: "If your ground pound is in the radius of a paint mine bomb, then it also sets
  off the bomb, but the ground pound paint covers it mostly. It's another way to disable someone else's paint mine"). A pound landing
  with a rival's trap (armed or still arming) inside its paint sets it off: nobody is caught, its burst is a smaller splat of its
  owner's paint (half the size), laid down before the pound's own, so the pound's paint covers most of it. Your own traps (and a
  teammate's) are left alone: a pound beside your own trap doesn't waste it. A CPU with its pound ready and a rival's trap within
  reach of one pounds it now and then. (Traps are the game's own on each phone, not the server's, so this is too.)
- The heat wave only on the ground (the user: "The heat wave doesn't affect you in the air, it affects you when you are on the
  ground"). Up in the air (a jump, a fling, a pound on its way down) the sun doesn't burn your paint, and you don't flash with it.
- Frozen in ice, a tap crunches (the user: "When you are frozen in ice, tapping on the screen, you should make like a ice crunching
  sound, not a ding"): sfx/ice_crunch.mp3 (Ludo take ice_a1: "a single short crisp crunch of cracking ice, like biting into an ice
  cube, dry and close, no ringing tail", from its onset, under 180 Hz off, 0.34 s), a little higher or lower each tap; and breaking
  out (or thawing) is a shatter, sfx/ice_break.mp3 (take icebrk_a2: "a block of ice shattering apart, a big crunchy crack then small
  ice chunks tinkling and scattering", under 120 Hz off, 0.81 s). Both fetched when a freeze is cast; the tick until they're in."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

BUST = """  // (v407) a rival's trap inside the pound's paint goes off, harmlessly: its burst under, the pound's paint over it
  for (let i = trapList.length - 1; i >= 0; i--) { const T = trapList[i]; if (T.owner === D || ally(D, T.owner) || Math.abs(T.y - D.y) > 0.8 || Math.hypot(T.x - D.x, T.z - D.z) > R * 0.9) continue;
    T.small = true; trapPop(T, null, false); if (D === P) popText('Trap busted!'); else if (T.owner === P) popText(nameOf(D) + ' busted your trap'); }
"""

def apply(s):
    # the pound busts rival traps (before its own paint goes down)
    s = rep(s, "  addSplat(D.x, D.y, D.z, D.yaw, R, dryClock, false, true, tcode(D)); shockwave(D.x, D.y, D.z, R, D === P ? 0xFFFFFF : 0xBFE3FF);",
               BUST + "  addSplat(D.x, D.y, D.z, D.yaw, R, dryClock, false, true, tcode(D)); shockwave(D.x, D.y, D.z, R, D === P ? 0xFFFFFF : 0xBFE3FF);")
    s = rep(s, "  addSplat(T.x, T.y, T.z, Math.random() * 6.283, TRAP_SPLAT, dryClock, false, false, T.code);",
               "  addSplat(T.x, T.y, T.z, Math.random() * 6.283, T.small ? TRAP_SPLAT * 0.5 : TRAP_SPLAT, dryClock, false, false, T.code); // (v407: small when a pound busted it)")
    # a CPU pounds a rival's trap it's on top of, now and then
    s = rep(s, "  if (ai.mode === 'puddle' && ai.puddle && ai.puddle.on && Math.hypot(ai.puddle.x - D.x, ai.puddle.z - D.z) < SLAM_R * 0.5 + ai.puddle.rad - 0.6) {",
               "  if (trapList.length && D.paint > SLAM_COST + 0.12 && !hiding && trapList.some(T => T.owner !== D && !ally(D, T.owner) && Math.abs(T.y - D.y) < 0.4 && Math.hypot(T.x - D.x, T.z - D.z) < SLAM_R * 0.6) && Math.random() < Math.min(1, dt * AI.pound * 0.6)) return useSlam(D); // (v407: bust a rival's trap)\n"
               "  if (ai.mode === 'puddle' && ai.puddle && ai.puddle.on && Math.hypot(ai.puddle.x - D.x, ai.puddle.z - D.z) < SLAM_R * 0.5 + ai.puddle.rad - 0.6) {")
    # the heat wave: on the ground only
    s = rep(s, "  D.exposed = wxPhase === 'sun' && D.skill !== 'repel' && D.giantT <= 0 && !D.turret && !(D.sunGrace > 0) && !inShadow(D.x, D.z, D.y);",
               "  D.exposed = wxPhase === 'sun' && !D.air && D.skill !== 'repel' && D.giantT <= 0 && !D.turret && !(D.sunGrace > 0) && !inShadow(D.x, D.z, D.y); // (v407: not up in the air)")
    # frozen: a crunch per tap, a shatter on the way out
    s = rep(s, "  frzList.push(F); D.wob = 1; D.squash = 0.7; emote(D, 'glee', 1.2); AU.whoosh();",
               "  frzList.push(F); D.wob = 1; D.squash = 0.7; emote(D, 'glee', 1.2); AU.whoosh(); if (AU.xwant) { AU.xwant('ice_crunch'); AU.xwant('ice_break'); } // (v407)")
    s = rep(s, "  if (D === P) { buzz(6); if (AU.tick) AU.tick(); restartCls($('frost'), 'crk'); } else if (hearable(D) && Math.random() < 0.35) { AU.at(D.x, D.z); if (AU.tick) AU.tick(); }",
               "  const crunch = v => (AU.xplay && AU.xplay('ice_crunch', { v, rate: 0.9 + Math.random() * 0.24 })) || (AU.tick && AU.tick()); // (v407: ice, not a ding)\n"
               "  if (D === P) { buzz(6); crunch(1.3); restartCls($('frost'), 'crk'); } else if (hearable(D) && Math.random() < 0.35) { AU.at(D.x, D.z); crunch(clamp(1.1 - Math.hypot(D.x - P.x, D.z - P.z) / 24, 0.35, 0.9)); }")
    s = rep(s, "  if (hearable(D)) AU.pop();\n}\nfunction iceFrame(rdt) {",
               "  if (D === P || hearable(D)) { const v = D === P ? 1 : clamp(1.1 - Math.hypot(D.x - P.x, D.z - P.z) / 24, 0.35, 0.85); if (!(AU.xplay && AU.xplay('ice_break', { v, rate: 0.96 + Math.random() * 0.08 }))) AU.pop(); } // (v407: a shatter)\n}\nfunction iceFrame(rdt) {")
    return s
