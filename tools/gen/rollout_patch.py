# The new look on every other stage: the Crypt (ghost-green rims, iron trims, torches and candles, dark ivy), the Manor (varnished parquet
# that reflects, thick gilt trims, candles, planters, warm strips), Palette Island (thicker wood trims, vines on the rock planters) and the
# Blank Canvas (a glossy white floor that reflects, crisp white trims, soft grey rims). The crypt's cobbles get smooth domes.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
def theme_edit(tid, pairs):
    global s
    i = s.index("  { id: '%s'," % tid); j = min(x for x in [s.find('\n  { id:', i + 1), s.find('\n);', i), s.find('\n];', i)] if x > 0); seg = s[i:j]
    for a, b in pairs:
        assert seg.count(a) == 1, (tid, a); seg = seg.replace(a, b)
    s = s[:i] + seg + s[j:]

theme_edit('crypt', [
    ("ft: 0xD0D4E0, st: 0xC4C8D6, dt: 0x8E92A0, hor: 0x16323A, sky: [0x03090F, 0x0C2027, 0x1D4850], hemi: [0x76AEB6, 0x14262A]",
     "ft: 0xD8DCE6, st: 0xC8CCD8, dt: 0x8E92A0, hor: 0x123038, sky: [0x02080E, 0x0A1E26, 0x1B4650], low: 0x0E242C, hemi: [0x80BCC4, 0x16282C]"),
    ("trim: { c: 0x7E8392, m: 0, r: 0.8 }, lamps: { wall: 0.45, up: 0, kind: 'torch', col: 0xFF9A3C } }",
     "trim: { c: 0x4A4F5C, m: 0.75, r: 0.32, w: 0.2, h: 0.14 }, foot: { c: 0x2A2E36, m: 0.1, r: 0.7 }, lamps: { wall: 0.5, up: 0.15, kind: 'torch', col: 0xFF9A3C }, candles: 0.45, strips: 0.2,"
     " edge: 0x7FF0DA, edgeK: 2.2, rimLights: 0.45, ivy: { edge: 0.7, col: 0.6, drum: 0.4, prop: 0.5, tint: 0x9CB894 }, base: { hemiI: 0.62, key: 0xC4E4F0, keyI: 0.58 },"
     " env: { top: 0x1C3E4A, hor: 0x2A5A64, gnd: 0x18262A, sun: 0xC4E4F0, sunK: 0.5 }, lk: { hemi: 0.34, key: 1.25 }, grade: { sat: 1.1, con: 1.08, vig: 0.28, bloom: 0.6, expo: 1.12 } }")])
theme_edit('manor', [
    ("ft: 0xD0D0D0, st: 0xD4D4D4, dt: 0x8A8A8A, hor: 0x33153A, sky: [0x0C0410, 0x290E2E, 0x541F4E], hemi: [0xB27CC2, 0x2A1430]",
     "ft: 0xDADADA, st: 0xD8D8D8, dt: 0x8A8A8A, hor: 0x2E1436, sky: [0x0A0410, 0x260D2C, 0x4E1D4A], low: 0x1E0C24, hemi: [0xC090D0, 0x2C1632]"),
    ("trim: { c: 0xC99A44, m: 0.8, r: 0.35 }, lamps: { wall: 0.4, up: 0.1, col: 0xFFB866 } }",
     "trim: { c: 0xEBB656, m: 1, r: 0.22, w: 0.22, h: 0.16 }, foot: { c: 0x2A1610, m: 0.2, r: 0.4 }, lamps: { wall: 0.45, up: 0.2, col: 0xFFB866 }, candles: 0.55, strips: 0.3,"
     " edge: 0xFFC27A, edgeK: 2.4, rimLights: 0.5, lip: true, mirror: true, ivy: { edge: 0.25, drum: 0.2, planter: 0.45, tint: 0xE8F4E0 }, base: { hemiI: 0.66, key: 0xFFD8B0, keyI: 0.62 },"
     " env: { top: 0x3A2048, hor: 0x6A3A5A, gnd: 0x2A1420, sun: 0xFFD0A0, sunK: 0.6 }, lk: { hemi: 0.32, key: 1.22 }, grade: { sat: 1.1, con: 1.07, vig: 0.26, bloom: 0.6, expo: 1.1 } }")])
theme_edit('island', [("trim: { c: 0x8C6A48, m: 0, r: 0.62 }, cloud: 0xFFFFFF }",
     "trim: { c: 0x9A7650, m: 0, r: 0.55, w: 0.2, h: 0.14 }, foot: { c: 0x6E5238, m: 0, r: 0.8 }, ivy: { drum: 0.45, col: 0.4, tint: 0xD8FFC0 }, edge: 0xFFFFFF, edgeK: 1.1, cloud: 0xFFFFFF }")])
theme_edit('blank', [("trim: { c: 0xF2F2F0, m: 0, r: 0.5 }, cloud: 0xF7F8FA }",
     "trim: { c: 0xF6F6F4, m: 0, r: 0.35, w: 0.18, h: 0.12 }, foot: { c: 0xDADCE0, m: 0, r: 0.5 }, edge: 0xB8BECC, edgeK: 1, mirror: true, cloud: 0xF7F8FA }")])
# the manor's boards are varnished: glossier, so they hold reflections
rep("h.fillStyle = gray(0.8); h.fillRect(x0, y0, ww, hh); r.fillStyle = gray(0.26 + (R() - 0.5) * 0.08); r.fillRect(x0, y0, ww, hh);",
    "h.fillStyle = gray(0.8); h.fillRect(x0, y0, ww, hh); r.fillStyle = gray(0.17 + (R() - 0.5) * 0.06); r.fillRect(x0, y0, ww, hh);")
rep("for (let k = 0; k < 3; k++) blob(r, x0 + R() * ww, y0 + R() * hh, 20 + R() * 50, grayA(0.2 + R() * 0.25, 0.4));", "for (let k = 0; k < 3; k++) blob(r, x0 + R() * ww, y0 + R() * hh, 20 + R() * 50, grayA(0.14 + R() * 0.2, 0.4));")
# the blank canvas: polished plaster
rep("c.fillStyle = '#F4F4F1'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.7); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.5); r.fillRect(0, 0, S, S);",
    "c.fillStyle = '#F4F4F1'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.7); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.2); r.fillRect(0, 0, S, S);")
rep("for (let k = 0; k < 10; k++) blob(r, R() * S, R() * S, 20 + R() * 60, grayA(0.38 + R() * 0.25, 0.4));", "for (let k = 0; k < 10; k++) blob(r, R() * S, R() * S, 20 + R() * 60, grayA(0.16 + R() * 0.16, 0.4));")
# crypt cobbles: smooth domes (many fine steps instead of seven), so their relief doesn't ring
rep("for (let s = 0; s < 7; s++) { const k = 1 - s / 7; polyAt(h, pts.map(p => [p[0] * (0.35 + 0.65 * k), p[1] * (0.35 + 0.65 * k)]), X, Y, rot); h.fillStyle = gray(0.42 + 0.5 * (1 - k * k)); h.fill(); }",
    "for (let s = 0; s < 28; s++) { const k = 1 - s / 28; polyAt(h, pts.map(p => [p[0] * (0.3 + 0.7 * k), p[1] * (0.3 + 0.7 * k)]), X, Y, rot); h.fillStyle = gray(0.4 + 0.52 * Math.sqrt(1 - k * k)); h.fill(); }")
open(p, 'w').write(s)
print('ok')
