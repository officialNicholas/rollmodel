"""v339: the My Locker tab's picture back to the drawn face, in white.

- Since v331 the My Locker tab (on the locker page, beside the Paint Shop's) showed your portrait, the drawn axolotl face only until it
  was made. Now it's always the drawn face, and white whatever your paint. Everything else that shows your portrait keeps it."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the drawn face can be drawn in one tone instead of a paint's
    s = rep(s, "function frFaceSvg(look) {\n  const p = palOf(look && look.c) || PALETTE[0], g = '#' + p.hex.toString(16).padStart(6, '0'), gills = ",
               "function frFaceSvg(look, tone) { // (v339: tone, one colour for the head and gills instead of the paint's)\n"
               "  const p = palOf(look && look.c) || PALETTE[0], g = tone || '#' + p.hex.toString(16).padStart(6, '0'), hi = tone || p.hi, gills = ")
    s = rep(s, "<ellipse cx=\"20\" cy=\"23.5\" rx=\"13\" ry=\"11.2\" fill=\"' + p.hi + '\"",
               "<ellipse cx=\"20\" cy=\"23.5\" rx=\"13\" ry=\"11.2\" fill=\"' + hi + '\"")
    s = rep(s, "$('lkTabMineI').innerHTML = frFace(frLook());",
               "$('lkTabMineI').innerHTML = frFaceSvg(null, '#FFFFFF'); /* (v339: the drawn face in white, not your portrait) */")
    return s
