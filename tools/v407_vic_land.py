"""v407: the results in landscape: the character a little lower and a touch smaller, so it no longer covers the name (the user: "Lower
the character a bit, so it doesn't cover the name"). Its middle goes from the name's middle plus 14% of the screen to the name's foot
plus 27% (the top of its hat at about the name's foot); it fills 68% of the screen's height, not 74%. A pair is as it was."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "if (land) { vic.cy = clamp((vic.nameTop + vic.nameBot) / 2 / H + (vic.feat.length > 1 ? 0.24 : 0.14), 0.45, 0.68); vic.room = 0.74; }",
               "if (land) { vic.cy = vic.feat.length > 1 ? clamp((vic.nameTop + vic.nameBot) / 2 / H + 0.24, 0.45, 0.68) : clamp(vic.nameBot / H + 0.27, 0.5, 0.66); vic.room = vic.feat.length > 1 ? 0.74 : 0.68; } /* (v407: one alone below its name) */")
    s = rep(s, "if (land) { dist = Math.max(dist, (VIC_HT + 0.05) / (2 * tv * 0.74)); cy = vic.cy || 0.5; }",
               "if (land) { dist = Math.max(dist, (VIC_HT + 0.05) / (2 * tv * (vic.room || 0.74))); cy = vic.cy || 0.5; }")
    return s
