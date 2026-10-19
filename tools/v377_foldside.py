"""v377: iPhone Duo partly folded, held wide (the fold down the middle): you stand on one side of the fold in the lobby, not across it.

- The lobby centred you (and the two places beside you for a party) in the width the side plates leave, which on iPhone Duo held wide put
  you straight across the fold. Now, with the fold down the middle, you, the places beside you and the rank bar over your head all keep to
  one half: the one with more room once the side plates are counted (the right on a tie, where the rank bar already went), sized to fit it, with
  the places beside you a little closer in (0.8 apart, not 1.25) so you keep more of your size.
- Held upright (the fold across) you already stood below it, and without a fold nothing changes."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- which half: the roomier one once the side plates are counted, the right on a tie
    s = rep(s, "// where the blob stands: the space the top bar, the side plates and the dock leave, its feet low in it\nfunction lobbyFrame() {\n",
               "// (v377) iPhone Duo partly folded, held wide: the half of the screen you stand in (and the rank bar over you), 'l' or 'r'; '' with no fold\n"
               "// down the middle. The roomier one once the side plates are counted, the right on a tie (where the rank bar went before)\n"
               "let lobbySide = '';\n"
               "function lobbyHalf(r, L, R) {\n"
               "  if (!(FOLD.on && FOLD.axis === 'v')) return '';\n"
               "  const lw = FOLD.a - r.left - (L.width > 0 ? L.right - r.left + 8 : SAI.l + 12), rw = (R.width > 0 ? R.left - r.left - 8 : r.width - SAI.r - 12) - (FOLD.b - r.left);\n"
               "  return lw > rw * 1.1 ? 'l' : 'r';\n"
               "}\n"
               "// where the blob stands: the space the top bar, the side plates and the dock leave, its feet low in it\nfunction lobbyFrame() {\n")
    s = rep(s, "  const x0 = (L.right || r.left) - r.left + 6, x1 = (R.left || r.right) - r.left - 6, y0 = Math.max(top.bottom, logoBottom()) - r.top + 58, y1 = (bot.top || r.bottom) - r.top;\n",
               "  let x0 = (L.right || r.left) - r.left + 6, x1 = (R.left || r.right) - r.left - 6; const y0 = Math.max(top.bottom, logoBottom()) - r.top + 58, y1 = (bot.top || r.bottom) - r.top;\n"
               "  lobbySide = lobbyHalf(r, L, R); if (lobbySide === 'l') x1 = Math.min(x1, FOLD.a - r.left); else if (lobbySide === 'r') x0 = Math.max(x0, FOLD.b - r.left); // (v377: one side of the fold)\n")
    s = rep(s, "    const tv = Math.tan(LINEUP.lens * Math.PI / 360), ext = LINEUP.gap + 0.45, body = charTall({}); let lo = SAI.l + 12, hi = W - SAI.r - 12, ppu = 1, fy = y1;\n",
               "    const tv = Math.tan(LINEUP.lens * Math.PI / 360), ext = LINEUP.gap + 0.45, body = charTall({}); let lo = SAI.l + 12, hi = W - SAI.r - 12, ppu = 1, fy = y1;\n"
               "    if (lobbySide === 'l') hi = Math.min(hi, FOLD.a - r.left - 6); else if (lobbySide === 'r') lo = Math.max(lo, FOLD.b - r.left + 6); // (v377: the three of you in one half)\n")
    s = rep(s, "const tv = Math.tan(LINEUP.lens * Math.PI / 360), ext = LINEUP.gap + 0.45, body = charTall({});", "const tv = Math.tan(LINEUP.lens * Math.PI / 360), ext = lineGap() + 0.45, body = charTall({});")
    s = rep(s, "ppu = Math.min((hi - lo) / 2 * LINEUP.wide / ext,", "ppu = Math.min((hi - lo) / 2 * (lobbySide ? 0.95 : LINEUP.wide) / ext,")
    s = rep(s, "const g = lineupOn() ? LINEUP.gap : 1.05;", "const g = lineupOn() ? lineGap() : 1.05;")
    # (in half the width the places beside you come in closer, so you keep more of your size)
    s = rep(s, "const LINEUP = { lens: 24, gap: 1.25, wide: 0.86, tall: 0.3, feet: 0.82, pitch: 0.24 }, lineupOn = () => !lookOpen && viewW > viewH;",
               "const LINEUP = { lens: 24, gap: 1.25, wide: 0.86, tall: 0.3, feet: 0.82, pitch: 0.24 }, lineupOn = () => !lookOpen && viewW > viewH, lineGap = () => FOLD.on && FOLD.axis === 'v' ? 0.8 : LINEUP.gap; // (v377: in half the screen, the places beside you a little closer)")
    # ---- the rank bar over your head keeps to your half
    s = rep(s, "  if (FOLD.on && FOLD.axis === 'v') lo = Math.max(lo, FOLD.b - sr.left); // (v371: iPhone Duo partly folded)\n",
               "  if (FOLD.on && FOLD.axis === 'v') { if (lobbySide === 'l') hi = Math.min(hi, FOLD.a - sr.left); else lo = Math.max(lo, FOLD.b - sr.left); } // (v371: iPhone Duo partly folded; v377: over you, whichever half you're in)\n")
    return s
