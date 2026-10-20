"""v407: hiding in a coffin, the body showed through the coffin's side (the user: "I can see the zombie face coming out of the basin.
I shouldn't see that. only the eyeballs."). Down in a basin the body is only lowered (BASIN_DEEP), and a coffin is narrower than the
body is long, so the head came out through its front panel. Now, once it's down (past about half way), the body isn't drawn at all
in a match: only the basin's pair of eyes shows. Going in and climbing out it's drawn as before; the intro's basin is as it was."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # (it was drawn last frame if it was only hidden for being down in its basin: no pop-in on the way back up)
    s = rep(s, "&& !(D === P && lookIntro && lookIntro.t < (lookIntro.vis !== undefined ? lookIntro.vis : IN_LAND)), was = I.root.visible;",
               "&& !(D === P && lookIntro && lookIntro.t < (lookIntro.vis !== undefined ? lookIntro.vis : IN_LAND)), was = I.root.visible || !!V.potHid;")
    s = rep(s, "  I.root.visible = on; V.oldBlob.visible = !on && !tur && !(D === P && lookIntro && lookIntro.crawl); if (!on) return;",
               "  I.root.visible = on; V.oldBlob.visible = !on && !tur && !(D === P && lookIntro && lookIntro.crawl); if (!on) { V.potHid = false; return; }")
    s = rep(s, "  I.root.position.y = -V.sink;\n",
               "  I.root.position.y = -V.sink;\n  V.potHid = inPot && !basin && V.sink > BASIN_DEEP * 0.5; if (V.potHid) I.root.visible = false; // (v407: down in a coffin or a can, only its eyes show)\n")
    return s
