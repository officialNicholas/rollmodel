"""v372: the lobby held sideways is a line-up seen from well back.

- In landscape (any screen wider than it is tall: a phone on its side, iPhone Duo, an iPad, a computer) the lobby's camera stands well
  back with a long lens (24 degrees instead of 38), so the character no longer bulges toward the camera, and it is much smaller (about a
  quarter of the screen's height on iPhone Duo and an iPad, where it was half).
- It's framed as a line-up: you in the middle and a party member's spot (the + plates) either side, the three across most of the width
  the side plates leave beside you (centred in it), your character at most 30% of the height, not counting a hat; the three stand in the
  middle of the free space, a little low, with the rank bar over your head.
- The spots stand 1.25 from you instead of 1.05, so three characters would stand clear of each other; on big screens they used to sit
  out at the screen's edges.
- The camera looks down a little more (about 13.5 degrees instead of 7.5), so the floor still shows from further back.
- Upright, and the old locker sheet, are as they were."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the lens: long in the landscape lobby; the locker (lookOpen) and upright keep theirs
    s = rep(s, "const heroFov = () => camera.aspect < 0.8 ? 50 : 38;",
               "// (v372) in landscape the lobby is a line-up, you in the middle and a party member's spot either side, seen through a long lens from well\n"
               "// back: lens (degrees), gap (from you to a spot), wide (the share of the width the three take), tall (your height, at most, as a share of the\n"
               "// screen's), feet (how far down the free space your feet stand), pitch (how much the camera looks down: its height over its distance)\n"
               "const LINEUP = { lens: 24, gap: 1.25, wide: 0.86, tall: 0.3, feet: 0.82, pitch: 0.24 }, lineupOn = () => !lookOpen && viewW > viewH;\n"
               "const heroFov = () => camera.aspect < 0.8 ? 50 : lineupOn() ? LINEUP.lens : 38;")
    # the framing: the three across most of the width, your height capped, through the long lens
    s = rep(s, "  const fw = x1 - x0, fh = y1 - y0, tx = (x0 + x1) / 2, feetY = y0 + fh * (land ? 0.86 : 0.86);\n  const tall = charTall(myLook);\n",
               "  const fw = x1 - x0, fh = y1 - y0, tx = (x0 + x1) / 2, feetY = y0 + fh * (land ? 0.86 : 0.86);\n  const tall = charTall(myLook);\n"
               "  if (land && lineupOn()) { // (v372) the line-up, centred in the width the side plates leave beside the three of you: one that reaches down\n"
               "    // beside you narrows it (iPhone Duo closed, a phone on its side), one that stands higher doesn't; the three stand in the middle of the\n"
               "    // free space, a little low (with the rank bar over your head), never lower than they did\n"
               "    const tv = Math.tan(LINEUP.lens * Math.PI / 360), ext = LINEUP.gap + 0.45, body = charTall({}); let lo = SAI.l + 12, hi = W - SAI.r - 12, ppu = 1, fy = y1;\n"
               "    for (let k = 0; k < 2; k++) {\n"
               "      ppu = Math.min((hi - lo) / 2 * LINEUP.wide / ext, Hh * LINEUP.tall / body, fh * 0.84 / tall); fy = Math.min(y0 + fh * LINEUP.feet, (y0 + y1) / 2 + (tall * ppu + 64) / 2);\n"
               "      const bt = fy - tall * ppu + 16; if (L.width > 0 && L.bottom - r.top > bt && L.top - r.top < fy) lo = Math.max(lo, L.right - r.left + 8); if (R.width > 0 && R.bottom - r.top > bt && R.top - r.top < fy) hi = Math.min(hi, R.left - r.left - 8);\n"
               "      if (hi - lo < 180) { const m = (lo + hi) / 2; lo = m - 90; hi = m + 90; }\n"
               "    }\n"
               "    heroDist = clamp(Hh / (2 * tv * ppu) / Math.hypot(1, LINEUP.pitch), 2, 24); hero.mx = P.x; hero.mz = P.z; heroOff.x = W / 2 - (lo + hi) / 2; heroOff.y = Hh / 2 - (fy - 0.36 * ppu);\n"
               "    return heroDist;\n"
               "  }\n")
    # the camera looks down a touch more from back there
    s = rep(s, "dPos.set(hero.mx + Math.sin(a) * d2, ly + 0.02 + d2 * 0.13 + Math.sin(clock * 0.47) * 0.025, hero.mz + Math.cos(a) * d2);",
               "dPos.set(hero.mx + Math.sin(a) * d2, ly + 0.02 + d2 * (lineupOn() ? LINEUP.pitch : 0.13) + Math.sin(clock * 0.47) * 0.025, hero.mz + Math.cos(a) * d2);")
    # the party members' spots, further out in the line-up
    s = rep(s, "    pbV.set(P.x + pbR.x * s * 1.05, P.y + 0.28, P.z + pbR.z * s * 1.05).project(camera);",
               "    const g = lineupOn() ? LINEUP.gap : 1.05; pbV.set(P.x + pbR.x * s * g, P.y + 0.28, P.z + pbR.z * s * g).project(camera);")
    return s
