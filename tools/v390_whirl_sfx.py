"""v390: the Whirlwind sounds like a whirlwind (asked for: a better whirlwind sound, made with Ludo).

- The wind-up: air is sucked in round the whirler and starts to spin, a whirring flutter that quickens and climbs in pitch as it swells,
  loudest just as the charge goes (1 s, the wind-up's length). Before, it was one steady rising whistle at one level. The ting still
  comes at the lock, over it.
- The charge: a roaring tornado whoosh that hits at once (a splashy whump of paint on its first moment), roars for about the charge's
  length and dies away as it ends, under the burst. Before, it was the game's boost and dash, then a swish every quarter second. If the
  charge stops short (a wall, a drop, or stopped dead), the roar fades out in 0.15 s as the burst goes off; if the whirlwind ends early
  (the match over), whatever it is playing fades the same way.
- A rival's whirlwind sounds the same within earshot, quieter further off (as the game's other sounds are). Its wind-up used to play at
  the same level wherever it was.
- Until a file has arrived (they're fetched as a match starts, with the ting), the old sounds play: the rise for the wind-up; the boost,
  dash and swishes for the charge.

Both are Ludo.ai takes, picked by measurement and finished into game/sfx/w_wind2.mp3 and w_dash.mp3 (the prompts, the picks and why:
docs/whirlwind-sfx-v390.md). The old w_wind.mp3 is no longer played. To fade a sound out, xplay now returns a handle with stop(seconds)
(it's truthy, so callers that only check whether it played are unchanged)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

SND = r"""// (v390) the Whirlwind's own sounds (sfx/w_wind2.mp3, w_dash.mp3), for the whirler or a rival within earshot (quieter further off,
// as at() makes the game's other sounds). The handle stays on the whirlwind, so the sound before it fades as the next starts, and the
// charge's can fade if it stops short. False if it hasn't arrived yet: the caller plays the synth
function whirlSnd(D, n) {
  const W = D.whirl, h = AU.xplay && AU.xplay(n, { v: D === P ? 1 : clamp(1.15 - Math.hypot(D.x - P.x, D.z - P.z) / 22, 0.45, 1) }); if (!h) return false;
  if (W) { if (W.snd) W.snd.stop(0.04); W.snd = h; W.sn = n; } return true;
}
"""

def apply(s):
    # xplay hands back a handle: stop(seconds) fades that sound out and ends it (true enough for the callers that only ask if it played)
    s = rep(s, "src.connect(g); g.connect(sfx); src.start(T() + (o.d || 0) + 0.004); } catch (e) { return false; } return true; }\n",
               "src.connect(g); g.connect(sfx); src.start(T() + (o.d || 0) + 0.004); return { stop: f => xStop(src, g, f) }; } catch (e) { return false; } }\n"
               "  // (v390) fade a played file out over f seconds (0.12 by default) and end it; nothing once it has ended\n"
               "  function xStop(src, g, f) { try { const t = T(), t1 = t + Math.max(0.02, f == null ? 0.12 : f); g.gain.cancelScheduledValues(t); g.gain.setValueAtTime(g.gain.value, t); g.gain.linearRampToValueAtTime(0, t1); src.stop(t1 + 0.02); } catch (e) {} }\n")
    # the wind-up
    s = rep(s, "function startWhirl(D) {", SND + "function startWhirl(D) {")
    s = rep(s, "  if (D === P) { if (!(AU.xplay && AU.xplay('w_wind', { v: 0.8 }))) AU.rise(); buzz(10); banner('Whirlwind!', 'Aim it. It charges when the lane fills'); } else if (hearable(D) && !(AU.xplay && AU.xplay('w_wind', { v: 0.9 }))) AU.rise();\n",
               "  if (D === P) { if (!whirlSnd(D, 'w_wind2')) AU.rise(); buzz(10); banner('Whirlwind!', 'Aim it. It charges when the lane fills'); } else if (hearable(D) && !whirlSnd(D, 'w_wind2')) AU.rise();\n")
    # the charge: the roar (the synth and the swishes when it isn't in); faded if it stops short, and anything playing when it ends early
    s = rep(s, "if (D === P) { AU.boost(); AU.dash(); shake = Math.max(shake, 0.12); buzz(14); } else if (hearable(D)) AU.dash(); } }",
               "if (D === P) { if (!whirlSnd(D, 'w_dash')) { AU.boost(); AU.dash(); } shake = Math.max(shake, 0.12); buzz(14); } else if (hearable(D) && !whirlSnd(D, 'w_dash')) AU.dash(); } }")
    s = rep(s, "    W.swT -= dt; if (W.swT <= 0) { W.swT = 0.26; if (D === P || hearable(D)) AU.swish(); }\n",
               "    W.swT -= dt; if (W.swT <= 0) { W.swT = 0.26; if (W.sn !== 'w_dash' && (D === P || hearable(D))) AU.swish(); }\n")
    s = rep(s, "{ if (W.t < WHIRL_DASH) D.spd = 0; W.ph = 'end'; W.t = 0; whirlBurst(D); } }",
               "{ if (W.t < WHIRL_DASH) { D.spd = 0; if (W.snd) W.snd.stop(0.15); } W.ph = 'end'; W.t = 0; whirlBurst(D); } }")
    s = rep(s, "function endWhirl(D) { D.whirl = null;", "function endWhirl(D) { if (D.whirl && D.whirl.snd) D.whirl.snd.stop(0.15); D.whirl = null;")
    # fetched as a match starts, with the ting
    s = rep(s, "  if (AU.xwant) { AU.xwant('w_wind'); AU.xwant('w_ting'); }\n", "  if (AU.xwant) { AU.xwant('w_wind2'); AU.xwant('w_dash'); AU.xwant('w_ting'); }\n")
    return s
