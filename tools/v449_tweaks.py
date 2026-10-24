"""v449: the pound button a little higher and bigger; no heat wave in Time trial; a ring counts when you clip it; rain's speed-up a bit gentler.

- Ground pound (the user: "make the ground pound button a little higher and larger"): upright 96 to 106 px and 14 px higher off the
  bottom; sideways 84 to 92 px and 12 px higher; on a tablet held sideways 104 px and 12 px higher.
- Time trial (the user: "remove heat from time trial"): the heat wave never comes in a Time trial. Rain still can.
- Rings (the user: "if you are close enough to the ring and you are somewhat touching, give the point to the player"): a pass used to
  need your middle inside the ring's inner edge. Now it counts if any of you goes through: your middle may be out past the ring's
  outer edge by most of your width (1.95 from the ring's middle, the tube's outside edge is 1.75). And brushing into the ring from
  in front, overlapping its plane inside the arch, counts too, even if you turn away before crossing. The lesson's three rings work
  the same way.
- Rain (the user: "slightly reduce the speed of the player that is speed up in the rain"): the rain's speed-up for those it speeds
  (no skill, or Swim faster) goes from +60% to +45%."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """
/* (v449) the pound button: a little bigger, a little higher */
.hud .slamBtn{width:106px;height:106px;margin-bottom:28px}
@media (max-height:520px) and (min-aspect-ratio:1/1){.hud .slamBtn{width:92px;height:92px;bottom:max(34px,calc(env(safe-area-inset-bottom) + 26px))}}
@media (min-height:521px) and (min-aspect-ratio:23/20){.hud .slamBtn{width:104px;height:104px;bottom:max(40px,calc(env(safe-area-inset-bottom) + 30px))}}
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    # no heat wave in a Time trial
    s = rep(s, "if (!sunsSeen && matchLeft > SUN_WARN + SUN_TIME + 6 && roll < SUN_CHANCE)", "if (!sunsSeen && mode !== 'solo' && matchLeft > SUN_WARN + SUN_TIME + 6 && roll < SUN_CHANCE) /* (v449: no heat in Time trial) */")
    # rings: through it with any of you, or brushing into it from in front
    s = rep(s, "      if (Math.abs(lat) < inner - 0.05 && cy - TR.y < Math.sqrt(inner * inner - lat * lat) - 0.15) trialPass(cx, cy, cz);\n    }\n  }",
               "      const reach = TR_R + TR_TUBE + PR * 0.6; /* (v449: any of you through it counts, not just your middle) */ void inner;\n"
               "      if (Math.abs(lat) < reach && cy - TR.y < Math.sqrt(reach * reach - lat * lat) + 0.1) trialPass(cx, cy, cz);\n    }\n"
               "    else { const lat1 = (P.x - TR.x) * ax + (P.z - TR.z) * az; if (Math.abs(s1) < PR + TR_TUBE && Math.abs(lat1) < TR_R - 0.1 && P.y - TR.y < Math.sqrt(TR_R * TR_R - lat1 * lat1)) trialPass(P.x, P.y, P.z); } /* (v449: brushing into it from in front) */\n  }")
    # rain: +45%, not +60%
    s = rep(s, "const MOVE_K = 1.06, REPEL_SPD = 0.8, RAIN_SPD = 1.6,", "const MOVE_K = 1.06, REPEL_SPD = 0.8, RAIN_SPD = 1.45, /* (v449: was 1.6) */")
    return s
