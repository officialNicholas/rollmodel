"""v329: orange makes way for the intro's light grey, and the intro picks it for you.

- The paint you come up out of the barrel's puddle in (the intro's pearly light grey) is a real paint now, in orange's place: Red, Grey,
  Gold, Green, Purple, Pink. On you and on the floor it is the intro's own colour; it dries to a softer grey so the floor you've covered
  still reads on the light canvases.
- The intro's "Pick your paint." card opens with Grey already picked and Next ready, so keeping the colour you came up in is one tap.
  Picking another and coming back to Grey brings the pearly puddle back.
- The page's accents (buttons, the play ball, labels in your colour) take a deeper pewter of it, so text on and in your colour stays
  readable. The 3D paint, the swatches and the dabs keep the true light grey.
- A save that had Orange moves to Grey. Orange stays on as a colour the CPU rivals can wear, and so an online rival on an older build who
  picked Orange still shows in it. The CPUs never wear Grey (an online rival who picked it does)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the paint itself, in orange's place (ui: the page's accents; floor: a shade deeper on the canvas, so a trail stands out on the light
    # floors as well as the dark ones; noCpu: not one for the CPUs)
    s = rep(s, "  { id: 'orange', name: 'Orange', hex: 0xFF6A13, hi: '#FFA463', lo: '#B5440A', dry: 0x8A3A0E, words: ['Amber', 'Tangerine', 'Embers'] },\n",
               "  { id: 'grey', name: 'Grey', hex: 0xE6DEF2, hi: '#F4F0FA', lo: '#6E6688', dry: 0x9A92B0, ui: '#9A92B3', floor: 0xCCC4E0, words: ['Pearl', 'Silver', 'Ash'], noCpu: 1 }, // (v329: the intro's pearl, in orange's place)\n")
    s = rep(s, "let colorId = 'red', menuReact = 0;\n",
               "// (v329) orange, no longer one of yours: still a rival's, and how a friend's or an online rival's old pick is shown\n"
               "const PAL_ORANGE = { id: 'orange', name: 'Orange', hex: 0xFF6A13, hi: '#FFA463', lo: '#B5440A', dry: 0x8A3A0E, words: ['Amber', 'Tangerine', 'Embers'] };\n"
               "const palOf = id => PALETTE.find(p => p.id === id) || (id === 'orange' ? PAL_ORANGE : null);\n"
               "let colorId = 'red', menuReact = 0;\n")
    # the page's accents: the paint's ui tone when it has one (the light grey would vanish on the paper, and under white text)
    s = rep(s, "  r.setProperty('--ink', css); edgeRGB(css, EDGE.ink); r.setProperty('--ink-hi', c.hi); r.setProperty('--ink-lo', c.lo); r.setProperty('--ink-rgb', [(c.hex >> 16) & 255, (c.hex >> 8) & 255, c.hex & 255].join(','));\n",
               "  { const u = c.ui || css, uh = parseInt(u.slice(1), 16); r.setProperty('--ink', u); edgeRGB(u, EDGE.ink); r.setProperty('--ink-hi', c.hi); r.setProperty('--ink-lo', c.lo); r.setProperty('--ink-rgb', [(uh >> 16) & 255, (uh >> 8) & 255, uh & 255].join(',')); }\n", 2)
    # a friend's face in their paint, an old Orange pick included
    s = rep(s, "  const p = PALETTE.find(q => q.id === (look && look.c)) || PALETTE[0], g = '#' + p.hex",
               "  const p = palOf(look && look.c) || PALETTE[0], g = '#' + p.hex")
    # the rivals' colours: orange stays one; grey is there to show an online rival in it, but the CPUs don't wear it
    s = rep(s, "const RIVAL_COLS = [...PALETTE.map(p => ({ id: p.id, hex: p.hex, dry: p.dry, hi: p.hi, lo: p.lo })),\n",
               "const RIVAL_COLS = [...PALETTE.map(p => ({ id: p.id, hex: p.hex, dry: p.dry, hi: p.hi, lo: p.lo, floor: p.floor, noCpu: p.noCpu })), { id: 'orange', hex: 0xFF6A13, dry: 0x8A3A0E, hi: '#FFA463', lo: '#B5440A' },\n")
    s = rep(s, "function rollRivalCols() { const pool = RIVAL_COLS.slice();",
               "function rollRivalCols() { const pool = RIVAL_COLS.filter(c => !c.noCpu);")
    s = rep(s, "let best = c, bd = -1; for (const o of RIVAL_COLS) { const d = Math.min(",
               "let best = c, bd = -1; for (const o of RIVAL_COLS) { if (o.noCpu) continue; const d = Math.min(")
    # a save from before: Orange is Grey now
    s = rep(s, "colorId = PALETTE.some(p => p.id === store.color) ? store.color : 'red'; renderSwatches();",
               "if (store.color === 'orange') store.color = 'grey'; // (v329)\ncolorId = PALETTE.some(p => p.id === store.color) ? store.color : 'red'; renderSwatches();")
    # the intro: the paint card opens with the grey you came up in already picked (quietly: no splash, the puddle stays pearly), Next
    # ready; picking it again after another brings the pearl back
    s = rep(s, "    const c = PALETTE.find(p => p.id === id); if (!c) return; X.paintTo = new THREE.Color(c.hex); X.paintId = id; X.pearlTo = 0;\n",
               "    const c = PALETTE.find(p => p.id === id); if (!c) return; X.paintTo = new THREE.Color(c.hex); X.paintId = id; X.pearlTo = id === 'grey' ? 1 : 0; // (v329: the grey is the pearl)\n")
    s = rep(s, "    else if (ph === 'paint') { shot(look || 'paint'); card('flPaint'); AU.flm.layer(3); }\n",
               "    else if (ph === 'paint') { if (!X.paintId) { X.paintId = 'grey'; setColor('grey'); pressed('flPaintO', 'data-c', 'grey'); $('flPaintGo').disabled = false; } shot(look || 'paint'); card('flPaint'); AU.flm.layer(3); } // (v329: what you came up in, picked for you)\n")
    # the character in it: its skin, ears, belly and fins come from the paint's hue at a set strength, which turns a pale grey into a
    # strong purple. A paint near grey (by its spread) now gets the greys of its hue instead, and the baked texture's pink goes grey too
    s = rep(s, """function palette(team) {
  _c.set(team); _c.getHSL(_hsl); const h = _hsl.h, s = _hsl.s, l = _hsl.l;
  const slate = 0.64;   // blue-grey
  return {
""", """// (v329) how near grey a colour is: 1 for a pale grey like the intro's pearl, 0 for every bright paint (by its spread in linear RGB)
function paleK(c) { const t = Math.min(1, Math.max(0, (Math.max(c.r, c.g, c.b) - Math.min(c.r, c.g, c.b) - 0.2) / 0.25)); return 1 - t * t * (3 - 2 * t); }
const PALE = { skin: [0.1, 0.6], belly: [0.08, 0.8], spot: [0.1, 0.26], gill: [0.16, 0.5], gillTip: [0.12, 0.8], finCore: [0.1, 0.24], finGlow: [0.18, 0.68] }; // (saturation, lightness)
function palette(team) {
  _c.set(team); _c.getHSL(_hsl); const h = _hsl.h, s = _hsl.s, l = _hsl.l, g = paleK(_c);
  const slate = 0.64;   // blue-grey
  const p = {
""")
    s = rep(s, """    finGlow: hsl(mixHue(h, 0.04, 0.45), 0.85, 0.58),
  };
}
""", """    finGlow: hsl(mixHue(h, 0.04, 0.45), 0.85, 0.58),
  };
  if (g > 0) for (const k in PALE) p[k].lerp(hsl(h, PALE[k][0], PALE[k][1]), g); // (v329: a grey paint, a grey axolotl)
  return p;
}
""")
    s = rep(s, "    U.uTint.value.set(d0[0], d0[1], 1, 1); U.uTintTo.value.set(cs * d0[0] - sn * d0[1], sn * d0[0] + cs * d0[1], 1, 0);\n",
               "    { const g = paleK(_c); U.uTint.value.set(d0[0], d0[1], 1 - 0.85 * g, 1); U.uTintTo.value.set(cs * d0[0] - sn * d0[1], sn * d0[0] + cs * d0[1], 1 + 1.1 * g, g); } // (v329: a grey paint: the pink goes grey, and lighter)\n")
    # (uTintTo.w, spare till now: how grey the paint is. The texture's paler pinks sit outside the turn, so a grey paint takes the
    # texture's colour to the paint's own (uTeam, set but unused till now) at the texture's lightness, and lifts it a little)
    s = rep(s, "  col = max(mix(vec3(dot(col, vec3(0.2126, 0.7152, 0.0722))), col, 1.14), vec3(0.0));\n",
               "  col = max(mix(vec3(dot(col, vec3(0.2126, 0.7152, 0.0722))), col, 1.14), vec3(0.0));\n"
               "  if (uTintTo.w > 0.0) { float Yc = dot(col, vec3(0.2126, 0.7152, 0.0722)); col = mix(col, Yc * uTeam / max(dot(uTeam, vec3(0.2126, 0.7152, 0.0722)), 1e-3), 0.85 * uTintTo.w); col = mix(col, col * 0.6 + 0.4, 0.5 * uTintTo.w); } // (v329: a grey paint: the texture in the paint's own pearl, a little lighter)\n")
    s = rep(s, "M.ink.material.color.setHSL(inkHSL.h, Math.min(0.8, 0.3 + 0.55 * inkHSL.s), 0.12, THREE.SRGBColorSpace)",
               "M.ink.material.color.setHSL(inkHSL.h, Math.min(0.8, 0.3 + 0.55 * inkHSL.s) * (0.3 + 0.7 * Math.min(1, Math.max(0, (Math.max(c.r, c.g, c.b) - Math.min(c.r, c.g, c.b) - 0.2) / 0.25))), 0.12, THREE.SRGBColorSpace)") # (paleK lives in the look module: the same measure, inline)
    # (for tests: the paint picked, and how pearly the puddle is)
    s = rep(s, "dust: X.dust.P.length, calls: renderer.info.render.calls,", "dust: X.dust.P.length, paintId: X.paintId || null, pearl: X.pearl, calls: renderer.info.render.calls,")
    # the paint on the canvas, and on things, in the paint's floor tone where it has one (TEAMS[i].fl)
    s = rep(s, "  paintUniforms.uWetA.value[0].setHex(c.hex); paintUniforms.uDryA.value[0].setHex(c.dry);\n",
               "  paintUniforms.uWetA.value[0].setHex(c.floor || c.hex); paintUniforms.uDryA.value[0].setHex(c.dry); TEAMS[0].fl = c.floor || c.hex;\n", 2)
    s = rep(s, "paintUniforms.uWetA.value[i].setHex(t.hex);", "paintUniforms.uWetA.value[i].setHex(t.floor || t.hex); TEAMS[i].fl = t.floor || t.hex;")
    s = rep(s, "const splCol = t => { splTmp.set(TEAMS[t % 4].wet);", "const splCol = t => { splTmp.set(TEAMS[t % 4].fl || TEAMS[t % 4].wet);")
    return s
