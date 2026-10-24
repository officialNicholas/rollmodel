"""v450: steering with finer control near the middle, a steering pill under the thumb when upright, and the lesson easing back in.

- Steering (the user: "smooth, and snappy, and responsive, not too sensitive ... simple to control, but hard to master"): the stick's
  reach goes from 58 to 64 px and its response bends: a small nudge of the thumb is a gentle line, the full turn is where it was
  (about 55 px out). Half a turn now takes about 34 px of thumb, not 28, so a twitch doesn't throw you off line, and the response
  (the filter and the turn rate) stays as quick as v442 made it.
- Upright (the user: "I like the joystick that appears in horizontal, I think it covers the player in vertical, but some subtle indicator
  of control might be nice"): a slim pill under the steering thumb, just above it so the thumb doesn't hide it: a see-through track
  and a knob in your paint colour that slides left and right as you steer, the whole pill sliding along with the thumb when it runs past
  the end, as the steering centre does. It never shows for a tap, and goes on letting go and while the slingshot's band is out. Held
  sideways, the round stick is as it was.
- The lesson: after a card's Go the game doesn't snap back to full speed, it eases in over half a second (from about 40% speed), so
  picking the action back up feels smooth."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """
/* (v450) upright: the steering pill, slim, just above the thumb, a knob in the paint colour sliding left and right */
@media (orientation:portrait){
  html .joy{display:block;width:132px;height:12px;margin:-6px 0 0 -66px;border-radius:99px;background:rgba(23,19,32,.16);box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.55),0 0 0 1px rgba(23,19,32,.24)}
  html .joy.on{opacity:.82}
  html .joy i{width:22px;height:22px;margin:-11px 0 0 -11px}
}
"""

def apply(s):
    # steering: a little more reach, and a curve that's gentle near the middle
    s = rep(s, "const MAX_DRAG = 58, DEAD = 4, HOLD_MS = 150, TAP_MS = 300;", "const MAX_DRAG = 64, DEAD = 4, HOLD_MS = 150, TAP_MS = 300; /* (v450: 64, was 58) */")
    s = rep(s, "steerIn = t.moved ? Math.sign(dx) * Math.pow(a, 1.1) * (store.steerInv ? -1 : 1) : 0;",
               "steerIn = t.moved ? Math.sign(dx) * a * (0.6 + 0.4 * a) * (store.steerInv ? -1 : 1) : 0; /* (v450: fine near the middle, the same full turn) */")
    # the stick shows upright too, as a pill
    s = rep(s, "if (steerId === null || state !== 'play' || P.charging || innerWidth <= innerHeight) { joyHide(); return; }", "if (steerId === null || state !== 'play' || P.charging) { joyHide(); return; } /* (v450: upright too) */")
    s = rep(s, "if (innerWidth <= innerHeight || state !== 'play' || P.charging || !t.moved || P.st === 'out') { joyHide(); return; }", "if (state !== 'play' || P.charging || !t.moved || P.st === 'out') { joyHide(); return; }")
    s = rep(s, "const r = slingRect(), tr = joyEl.offsetWidth * 0.3;", "const r = slingRect(), port = innerWidth <= innerHeight, tr = port ? joyEl.offsetWidth / 2 - 11 : joyEl.offsetWidth * 0.3; /* (v450: the pill's knob runs its length) */")
    s = rep(s, "ky = clamp((e.clientY - anchorY) / MAX_DRAG, -1, 1) * tr * (P.turret ? 1 : 0.45);", "ky = port ? 0 : clamp((e.clientY - anchorY) / MAX_DRAG, -1, 1) * tr * (P.turret ? 1 : 0.45);")
    s = rep(s, "joyEl.style.transform = 'translate(' + (anchorX - r.left).toFixed(1) + 'px,' + (anchorY - r.top).toFixed(1) + 'px)';",
               "joyEl.style.transform = 'translate(' + (anchorX - r.left).toFixed(1) + 'px,' + (anchorY - r.top - (port ? 46 : 0)).toFixed(1) + 'px)'; /* (v450: upright, just above the thumb) */")
    # the lesson eases back in after a card
    s = rep(s, "lsnFreeze(null); if (tut) tut.ghostT = 0; }", "lsnFreeze(null); if (tut) { tut.ghostT = 0; tut.rampT = 0.45; } /* (v450: eases back in) */ }")
    s = rep(s, "if (tut && tut.lsn && state === 'play') dt = 0;", "if (tut && tut.lsn && state === 'play') dt = 0; else if (tut && tut.rampT > 0 && state === 'play') { const k = Math.min(1, tut.rampT / 0.45); tut.rampT -= dt; dt *= 1 - 0.6 * k * k; } /* (v450: after a card, from about 40% speed to full over half a second) */")
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    return s
