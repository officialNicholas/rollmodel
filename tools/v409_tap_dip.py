"""v409: the sound dipped and came back on every tap (the user: "every time I interact with the screen the audio dips and increases.
Very jarring"). 407's fix for the blip on coming back shut the output and faded it in again on every wake, and a tap wakes the sound
(after a wake, the next tap checks again). With the sound already running that was a dip for nothing. Now the output is only shut
when the sound really is stopped or about to be (going away, the app's stop-and-start on coming back, or the phone stopping it), and
only faded back in if it was shut; a tap with the sound running leaves it alone."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "  function hush() { if (!ctx || !wakeG) return; const t = ctx.currentTime;",
               "  let shut = false; // (v409: only faded back in if it was shut)\n  function hush() { if (!ctx || !wakeG) return; shut = true; const t = ctx.currentTime;")
    s = rep(s, "  function unhush() { if (!ctx || !wakeG || ctx.state !== 'running') return; const t = ctx.currentTime;",
               "  function unhush() { if (!ctx || !wakeG || ctx.state !== 'running' || !shut) return; shut = false; const t = ctx.currentTime;")
    # a wake with the sound running and no stop-and-start: nothing to shut
    s = rep(s, "      hush(); if (kick && ctx.state === 'running') { const c = ctx;",
               "      if (kick || ctx.state !== 'running') hush(); if (kick && ctx.state === 'running') { const c = ctx;")
    return s
