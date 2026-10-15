"""v298: the first match (the lesson) is on an open Blank Canvas: a flat floor with a few obstacles dotted about.

- The lesson's canvas has no centrepiece, no ramps, no holes, no floating decks or pads and no drifting cloud platforms. Just the
  floor with two to three pairs of round pieces on it: a pair of the Blank Canvas columns (the tall white posts with a ball on
  top) and one or two pairs of low drums. Round pieces only, so nothing has a corner to snag on.
- They're spread out: at least 11 apart from each other, none within 8 of the middle and none within 6 of the edge. They cover
  about 1% of the floor (0.4 to 1.9%). A lesson canvas used to have 15 to 30 pieces on 5 to 13% of it, plus about 8 ramps and
  3 cloud platforms (60 layouts each way).
- The refill tanks and the boiling puddles spread out over the open floor. They used to settle against walls, which here would
  have bunched them two to a drum.
- Only the lesson. Every other match on Blank Canvas, easy ones included, is laid out as before. "Same canvas" replays the
  lesson's layout as it was."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

FLAT_KIT = r"""  // (v298) the lesson's canvas: open floor with a few round pieces spread well apart (no centrepiece, ramps, holes, decks or clouds)
  if (FLAT) {
    const cen = [], far = (x, z) => { const ix = sym === 'mirror' ? x : -x, iz = -z, r = Math.hypot(x, z); return r > 8 && r < ARENA - 6 && Math.hypot(x - ix, z - iz) > 11 && cen.every(p => Math.hypot(x - p[0], z - p[1]) > 11 && Math.hypot(ix - p[0], iz - p[1]) > 11); };
    for (const k of ['column', 'drum', ...(R() < 0.6 ? ['drum'] : [])]) for (let t = 0; t < 80; t++) { const [cx, cz] = spot(); if (!far(cx, cz) || !place(kit[k](cx, cz))) continue; cen.push([cx, cz], [sym === 'mirror' ? cx : -cx, -cz]); break; }
  }
"""

def apply(s):
    # the flag: set while the lesson has the stage, part of the map's key so the canvas waiting in the menu isn't reused for it
    s = rep(s, "const mapKey = () => (STAGE_KEY[stageSel] || 'sea') + ':' + mode + ':' + (easyOn() ? 1 : 0);",
               "let tutFlat = false; // (v298) the lesson is on: its Blank Canvas is laid out flat\nconst mapKey = () => (STAGE_KEY[stageSel] || 'sea') + ':' + mode + ':' + (easyOn() ? 1 : 0) + (tutFlat ? ':flat' : '');")
    s = rep(s, "function tutPrep() { if (!tutMatchDue()) return; if (!tutPrev) tutPrev = { mode, diff, stageSel }; mode = 'duel'; diff = 'easy'; stageSel = 'blank'; applyMode(); }",
               "function tutPrep() { if (!tutMatchDue()) return; if (!tutPrev) tutPrev = { mode, diff, stageSel }; mode = 'duel'; diff = 'easy'; stageSel = 'blank'; tutFlat = true; applyMode(); }")
    s = rep(s, "function tutRestore() { if (!tutPrev) return; mode = tutPrev.mode; diff = tutPrev.diff; stageSel = tutPrev.stageSel; tutPrev = null; applyMode(); }",
               "function tutRestore() { tutFlat = false; if (!tutPrev) return; mode = tutPrev.mode; diff = tutPrev.diff; stageSel = tutPrev.stageSel; tutPrev = null; applyMode(); }")
    # genWorld passes it on (only for a Blank Canvas map), GEN keeps it, and a replay of the same canvas brings it back
    s = rep(s, "opt = opt || {}; const easy = opt.easy !== undefined ? !!opt.easy : easyOn(), avoid = opt.avoid || null, themes = opt.themes || null;\n  genOpt = { easy, avoid, themes };",
               "opt = opt || {}; const easy = opt.easy !== undefined ? !!opt.easy : easyOn(), avoid = opt.avoid || null, themes = opt.themes || null;\n  const flat = opt.flat !== undefined ? !!opt.flat : tutFlat && !!themes && themes.length === 1 && themes[0] === 'blank'; // (v298)\n  genOpt = { easy, avoid, themes, flat };")
    s = rep(s, "Object.assign(GEN, { seed, sym: L.sym, arch: L.arch, tries: t + 1, fallback: false, easy, avoid, themes, key: mapKey(), std: false });",
               "Object.assign(GEN, { seed, sym: L.sym, arch: L.arch, tries: t + 1, fallback: false, easy, avoid, themes, flat, key: mapKey(), std: false });")
    s = rep(s, "Object.assign(GEN, { seed, sym: 'classic', arch: 'classic', tries: 5, fallback: true, easy, avoid, themes, key: mapKey(), std: false });",
               "Object.assign(GEN, { seed, sym: 'classic', arch: 'classic', tries: 5, fallback: true, easy, avoid, themes, flat, key: mapKey(), std: false });")
    s = rep(s, "const sd = GEN.seed, op = { easy: GEN.easy, avoid: GEN.avoid, themes: GEN.themes };",
               "const sd = GEN.seed, op = { easy: GEN.easy, avoid: GEN.avoid, themes: GEN.themes, flat: !!GEN.flat };")
    # genLayout: point symmetry or a mirror (never free-form), no centrepiece, only the few pieces, no top-up, no clouds
    s = rep(s, "const sym = pick(['rot', 'rot', 'rot', 'mirror', 'mirror', 'free']), TP =",
               "const FLAT = !!genOpt.flat, sym = pick(FLAT ? ['rot', 'rot', 'mirror'] : ['rot', 'rot', 'rot', 'mirror', 'mirror', 'free']), TP =")
    s = rep(s, "const arch = theme.arch || pick(EZ ? ['plaza', 'plaza', 'spire', 'open', 'open', 'rotunda'] : ['plaza', 'plaza', 'pit', 'spire', 'canopy', 'open', 'rotunda', 'well']);",
               "const arch = FLAT ? 'open' : theme.arch || pick(EZ ? ['plaza', 'plaza', 'spire', 'open', 'open', 'rotunda'] : ['plaza', 'plaza', 'pit', 'spire', 'canopy', 'open', 'rotunda', 'well']);")
    s = rep(s, "  const per = sym === 'free' ? 2 : 1, want = [];\n  const add = (k, a, b) => { for (let n = ri(a, b) * per; n > 0; n--) want.push(k); };\n  if (EZ) {",
               "  const per = sym === 'free' ? 2 : 1, want = [];\n  const add = (k, a, b) => { for (let n = ri(a, b) * per; n > 0; n--) want.push(k); };\n  if (FLAT) {}\n  else if (EZ) {")
    s = rep(s, "  for (const k in TK) { if (EZ && k === 'rpit') continue;", "  if (!FLAT) for (const k in TK) { if (EZ && k === 'rpit') continue;")
    a = "  for (const k of want) for (let t = 0; t < 60; t++) { const [cx, cz] = spot(); if (place(kit[k](cx, cz))) break; }\n"
    s = rep(s, a, a + FLAT_KIT)
    s = rep(s, "const target = (2 * ARENA) * (2 * ARENA) * (EZ ? rr(0.11, 0.15) : rr(0.13, 0.19)) * (theme.fillMul || 1),",
               "const target = FLAT ? 0 : (2 * ARENA) * (2 * ARENA) * (EZ ? rr(0.11, 0.15) : rr(0.13, 0.19)) * (theme.fillMul || 1),")
    s = rep(s, "const clouds = [], nC = theme.noClouds ? 0 : sym === 'free' ? ri(2, 4) : ri(1, 2), hw = 1.35;",
               "const clouds = [], nC = theme.noClouds || FLAT ? 0 : sym === 'free' ? ri(2, 4) : ri(1, 2), hw = 1.35;")
    # with so little to tuck against, the tanks and the boiling puddles spread over the floor instead of hugging the few pieces
    s = rep(s, "+ 1.4 * tuckC.get(n) + el + R() * 1.5; }, 5, cofs", "+ (genOpt.flat ? 0 : 1.4) * tuckC.get(n) + el + R() * 1.5; }, 5, cofs")
    s = rep(s, "return (wb ? (wb >= 2 ? 1.6 : 1.2) : 0) + Math.min(t, 0.6) * 1.8", "return (wb && !genOpt.flat ? (wb >= 2 ? 1.6 : 1.2) : 0) + Math.min(t, 0.6) * 1.8")
    return s
