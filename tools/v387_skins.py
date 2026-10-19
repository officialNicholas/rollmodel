"""v387: Skins. Five premium looks for the whole body, bought with dabs in the Paint Shop: Galaxy, Lava, Rainbow, Matrix, Glitter.

- A skin repaints the character's whole skin (body, head, gills, tail) in the axolotl's own shader, from its body's own place on the
  model (so a pattern rides along with every squash and stride), and each one moves a little: Galaxy's stars twinkle over still nebulae,
  Lava's cracks glow with heat flowing through them and its plates breathe, Rainbow's bands drift slowly round the body, Matrix's code
  rains down it, Glitter's flakes catch the light as it moves and flash now and then (in your own paint colour).
- The eyes, the mouth and the paint you come out of a refill in are drawn over a skin as before; your paint is still your colour, the ink
  line round you and the see-through copy behind walls keep your team's colour, so a skin never hides whose side you're on.
- Putting one on in the locker sweeps it up over you from the ground with a bright seam, and you spin round once to show it off; in a
  match (and on a portrait) it's simply on.
- In the Paint Shop and the locker, Skins are their own kind (a filter of their own, first after the season's), each card a portrait of
  you in it. One skin at a time; Take off goes back to your paint's own skin. Friends and online rivals see yours.
- The old slime (only if the axolotl never loads) has no skins."""

import json

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

FX_PARS = r"""
// (v387) the skin: uFx x which (0 none, 1 galaxy, 2 lava, 3 rainbow, 4 matrix, 5 glitter), y how far it has swept up over the body
// (0..1), z the time (s); what it gives off (sFxGlow), how much of it there is here (sFxM), and its surface (rough, metal; -1: as it was)
uniform vec4 uFx; vec3 sFxGlow = vec3(0.0); float sFxM = 0.0, sFxRough = -1.0, sFxMetal = -1.0;
vec3 fxHsv(float h, float s, float v) { vec3 k = clamp(abs(mod(h * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0); return v * mix(vec3(1.0), k, s); }
float fxFbm(vec3 p) { return 0.5 * aNoise(p) + 0.3 * aNoise(p * 2.03 + 5.1) + 0.2 * aNoise(p * 4.1 + 1.7); }
// stars: one (or none) to a cell, round with a soft halo; tw how much they twinkle; far off (a cell under a pixel) they fade out
float fxStars(vec3 p, float sc, float dens, float r, float t, float tw, out float hue) {
  vec3 q = p * sc, i = floor(q), f = fract(q), h = aHash3(i + 3.7); hue = h.z; float fw = length(fwidth(q));
  if (aHash(i + 11.3) > dens) return 0.0;
  float d = length(f - (0.25 + 0.5 * h)), rr = r * (0.6 + 0.8 * h.x), aa = 0.5 * fw + 0.01;
  float s = 1.0 - smoothstep(rr - aa, rr + aa, d); s += 0.3 * (1.0 - smoothstep(0.0, rr * 3.2, d));
  float w = mix(1.0, 0.5 + 0.5 * sin(t * (1.1 + 2.4 * h.y) + h.x * 40.0), tw); w *= w;
  return s * w * (1.0 - smoothstep(0.6, 1.3, fw));
}
// cells (the lava's plates): the nearest and second nearest distance, and the nearest one's own random number
vec3 fxVor(vec3 p) { vec3 i = floor(p), f = fract(p); float f1 = 9.0, f2 = 9.0, id = 0.0;
  for (int z = -1; z <= 1; z++) for (int y = -1; y <= 1; y++) for (int x = -1; x <= 1; x++) { vec3 o = vec3(float(x), float(y), float(z)), c = i + o, r = o + 0.15 + 0.7 * aHash3(c) - f; float d = dot(r, r);
    if (d < f1) { f2 = f1; f1 = d; id = aHash(c + 1.9); } else if (d < f2) f2 = d; }
  return vec3(sqrt(f1), sqrt(f2), id); }
"""

FX_FS = r"""
if (uFx.x > 0.5) {
  vec3 cp = vCp, col = diffuseColor.rgb, glow = vec3(0.0); float t = uFx.z, k = uFx.x;
  vec3 fxN = normalize(vNormal), fxV = normalize(vViewPosition); float fxFr = pow(1.0 - saturate(dot(fxN, fxV)), 2.2);
  float fFace = smoothstep(0.1, 0.5, vFace.z) * (1.0 - smoothstep(0.35, 0.8, sGill));   // (the face: a little calmer, so it reads)
  if (k < 1.5) {
    // GALAXY: deep space with still nebulae (magenta, blue), a dusty band across it, and two layers of stars that twinkle
    float n1 = fxFbm(cp * 2.4 + 1.3), n2 = fxFbm(cp * 5.2 - 2.1);
    col = mix(vec3(0.006, 0.005, 0.03), vec3(0.04, 0.014, 0.1), smoothstep(0.35, 0.75, n1));
    float a = smoothstep(0.5, 0.82, n1 * 0.65 + n2 * 0.45), b = smoothstep(0.55, 0.85, n2 * 0.7 + (1.0 - n1) * 0.4);
    vec3 neb = vec3(0.42, 0.04, 0.32) * a + vec3(0.03, 0.12, 0.5) * b; col += neb * 0.55;
    float band = exp(-pow((cp.y * 0.8 + cp.x * 1.1 - cp.z * 0.4 - 0.75) / 0.16, 2.0)) * (0.6 + 0.6 * n2); col += vec3(0.25, 0.16, 0.35) * band * 0.3;
    float h1 = 0.0, h2 = 0.0; float s1 = fxStars(cp, 46.0, 0.45, 0.07, t, 0.55, h1); float s2 = fxStars(cp + 7.3, 15.0, 0.32, 0.05, t, 1.0, h2);
    vec3 c1 = mix(vec3(0.75, 0.85, 1.0), vec3(1.0, 0.86, 0.7), h1), c2 = mix(vec3(0.8, 0.9, 1.0), vec3(1.0, 0.75, 0.95), h2);
    col += c1 * s1 * 0.5 + c2 * s2 * 0.6;
    glow = c1 * s1 * 1.1 + c2 * s2 * 2.6 + neb * 0.22 + vec3(0.3, 0.28, 0.9) * fxFr * 0.35;
    sFxRough = 0.22;
  } else if (k < 2.5) {
    // LAVA: near-black basalt broken into uneven plates, the cracks between them molten (a yellow-white core, orange to deep red at
    // their edges), heat flowing up through them so each crack brightens and dims in turn; the plates breathe a little, faint veins glow
    vec3 wp = cp * 4.4 + 0.5 * vec3(aNoise(cp * 2.6), aNoise(cp * 2.6 + 4.3), aNoise(cp * 2.6 + 8.9)) - 0.25;
    vec3 v = fxVor(wp); float e = v.y - v.x, n = aNoise(cp * 11.0), aa = fwidth(e) + 0.008, w = 0.035 + 0.075 * n;
    float crack = 1.0 - smoothstep(w * 0.5 - aa, w + aa, e), core = 1.0 - smoothstep(0.0, w * 0.4 + aa, e);
    float heat = smoothstep(0.25, 0.85, aNoise(cp * 3.2 + vec3(0.0, -t * 0.45, t * 0.12)) * 0.65 + aNoise(cp * 7.0 + vec3(t * 0.3, -t * 0.7, 0.0)) * 0.35);
    float breathe = 0.5 + 0.5 * sin(t * (0.8 + 1.4 * v.z) + v.z * 30.0);
    vec3 crust = vec3(0.016, 0.012, 0.011) * (0.55 + 0.9 * aNoise(cp * 26.0)) + vec3(0.11, 0.022, 0.0) * (1.0 - smoothstep(0.0, 0.16, e)) * (0.25 + 0.75 * heat);
    float vein = smoothstep(0.78, 0.96, aNoise(cp * 17.0 + vec3(0.0, -t * 0.25, 0.0))) * (1.0 - crack) * (0.3 + 0.7 * breathe);
    vec3 hot = mix(vec3(1.1, 0.12, 0.0), vec3(2.0, 0.65, 0.04), heat); hot = mix(hot, vec3(2.6, 1.75, 0.55), core * (0.35 + 0.65 * heat));
    float molten = max(crack * mix(0.35, 1.0, heat) * mix(0.75, 1.0, breathe), vein * 0.45);
    molten = max(molten, sGill * (0.3 + 0.55 * heat));
    col = mix(crust, hot * 0.22, molten);
    glow = hot * molten * 1.5 + vec3(0.5, 0.08, 0.0) * fxFr * 0.22 * heat;
    sFxRough = mix(0.8, 0.35, molten);
  } else if (k < 3.5) {
    // RAINBOW: candy bands of every colour slanting round the body, drifting slowly along it, a softer pastel on the belly
    float u = cp.y * 1.15 + cp.x * 0.55 + cp.z * 0.35 + 0.05 * sin(cp.x * 7.0 + cp.z * 5.0 + t * 0.9);
    float hb = (u * 0.9 - t * 0.08) * 7.0, hf = fract(hb), hq = (floor(hb) + smoothstep(0.78, 1.0, hf)) / 7.0;
    vec3 c = pow(fxHsv(fract(hq), 0.74, 1.0), vec3(2.2));
    float seam = 1.0 - smoothstep(0.0, 0.07, abs(hf - 0.89));   // (a thin light line where one band meets the next)
    c = mix(c, vec3(1.0), 0.28 * sBelly + 0.18 * sGill); c = mix(c, vec3(1.0), 0.35 * seam);
    col = c * 0.92;
    glow = c * 0.12 + mix(c, vec3(1.0), 0.5) * fxFr * 0.35;
    sFxRough = 0.3;
  } else if (k < 4.5) {
    // MATRIX: a black screen of green code: glyphs of lit pixels in cells, streams of them raining down the body in most columns,
    // each stream's head bright white-green and its trail fading behind it; the glyphs flicker as it passes
    vec3 g = cp / vec3(0.075, 0.1, 0.075), ci = floor(g), f = fract(g); float fw = length(fwidth(g));
    float ch = aHash(vec3(ci.x, 7.0, ci.z)), spd = 3.0 + 5.0 * ch, len = 3.0 + 6.0 * fract(ch * 13.7), span = 24.0;
    float d = mod(ci.y - mod(-t * spd + ch * 97.0, span), span), trail = exp(-d / len) * step(0.3, fract(ch * 7.31)), head = (1.0 - step(1.0, d)) * step(0.3, fract(ch * 7.31));
    vec3 sp3 = f * vec3(3.0, 5.0, 3.0), sub = floor(sp3), sf = fract(sp3); float flick = floor(t * (4.0 + 6.0 * ch) + aHash(ci) * 5.0);
    float bit = step(0.5, aHash(ci * 1.7 + sub * 0.31 + flick * 0.13 * (0.3 + trail)));
    float px = step(0.14, sf.x) * step(sf.x, 0.86) * step(0.12, sf.y) * step(sf.y, 0.88) * step(0.14, sf.z) * step(sf.z, 0.86);
    float inner = step(0.1, f.x) * step(f.x, 0.9) * step(0.06, f.y) * step(f.y, 0.94) * step(0.1, f.z) * step(f.z, 0.9);
    float glyph = mix(bit * px * inner, 0.22, smoothstep(0.45, 1.0, fw));
    float calm = 1.0 - 0.45 * fFace, lit = glyph * (trail + 0.06) * calm;
    vec3 green = vec3(0.03, 1.0, 0.2), white = vec3(0.8, 1.0, 0.85);
    col = vec3(0.002, 0.009, 0.004) + green * lit * 0.35;
    glow = mix(green, white, head) * glyph * (trail * 2.2 + head * 2.6 + 0.08) * calm + green * 0.06 * fxFr;
    sFxRough = 0.2;
  } else {
    // GLITTER: flakes in your paint colour, each tilted its own way, so as you move different ones catch the light and flare; some
    // flash on their own now and then; a finer dust of tiny glints between them; a pearly sheen at the edges
    vec3 tc = max(uTeam, vec3(0.0)), q = cp * 62.0, i = floor(q), f = fract(q), h = aHash3(i + 1.3); float fw = length(fwidth(q));
    vec3 fn = normalize(fxN + (h - 0.5) * 1.5), L = normalize(vec3(0.35, 0.8, 0.5)), H = normalize(L + fxV);
    float spec = pow(saturate(dot(fn, H)), 26.0), flash = pow(max(0.0, sin(t * (1.6 + 2.6 * h.y) + h.z * 60.0)), 10.0);
    float r = length(f - (0.3 + 0.4 * h.zxy)), shape = 1.0 - smoothstep(0.16, 0.34, r), far = smoothstep(0.5, 1.1, fw);
    float sp = mix((spec * 3.0 + flash * 2.2) * shape, 0.25, far);
    vec3 q2 = cp * 150.0, h2 = aHash3(floor(q2) + 7.7); float r2 = length(fract(q2) - 0.5), fw2 = length(fwidth(q2));
    float dust = pow(saturate(dot(normalize(fxN + (h2 - 0.5) * 1.6), H)), 40.0) * (1.0 - smoothstep(0.12, 0.3, r2)) * (1.0 - smoothstep(0.5, 1.0, fw2));
    col = tc * (0.38 + 0.5 * h.x) + vec3(0.9, 0.8, 1.0) * 0.05 * fxFr + tc * 0.1 * sBelly;
    glow = mix(tc, vec3(1.0), 0.45) * (sp * 1.6 + dust * 1.2) + mix(tc, vec3(1.0, 0.85, 0.95), 0.3) * fxFr * 0.2;
    sFxRough = 0.28; sFxMetal = 0.55;
  }
  // swept up over the body from the ground, a bright seam where it's arriving (uFx.y 0..1; at 1 it's all on)
  float front = uFx.y * 1.35 - 0.12, fxIn = uFx.y >= 0.999 ? 1.0 : smoothstep(-0.03, 0.03, front - cp.y), seam = (1.0 - smoothstep(0.0, 0.07, abs(cp.y - front))) * step(uFx.y, 0.999);
  sFxM = fxIn; diffuseColor.rgb = mix(diffuseColor.rgb, col, fxIn); sFxGlow = glow * fxIn + vec3(1.0, 0.95, 0.85) * seam * 1.6;
}
"""

FX_SURF = r"""
if (sFxM > 0.0) { if (sFxRough >= 0.0) roughnessFactor = mix(roughnessFactor, sFxRough, sFxM); if (sFxMetal >= 0.0) metalnessFactor = mix(metalnessFactor, sFxMetal, sFxM); }
"""

FX_GLOW = r"""
totalEmissiveRadiance += sFxGlow * (1.0 - sCoatM) * (1.0 - faceInk);   // (v387: what the skin gives off; never through the paint or the drawn face)
"""

# the skins on sale: [id, name, price, a line about it, a swatch for where its portrait isn't made yet]
SKINS = [
    ('galaxy', 'Galaxy', 2000, 'Deep space, its stars twinkling', '<radialGradient id="skg1" cx="35%" cy="35%" r="75%"><stop offset="0" stop-color="#5B2A9A"/><stop offset=".55" stop-color="#1A0F45"/><stop offset="1" stop-color="#070616"/></radialGradient><circle cx="20" cy="20" r="16" fill="url(#skg1)" stroke="#171320" stroke-width="2.4"/><circle cx="14" cy="15" r="1.4" fill="#fff"/><circle cx="25" cy="12" r="1" fill="#fff"/><circle cx="24" cy="25" r="1.6" fill="#FFE8F7"/><circle cx="12" cy="25" r=".9" fill="#fff"/><circle cx="29" cy="19" r=".8" fill="#fff"/>'),
    ('lava', 'Lava', 1750, 'Molten cracks, glowing as the heat flows', '<radialGradient id="skg2" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#3A2622"/><stop offset="1" stop-color="#140C0A"/></radialGradient><circle cx="20" cy="20" r="16" fill="url(#skg2)" stroke="#171320" stroke-width="2.4"/><path d="M8 17l7 2 4-5 6 4 7-3M12 28l5-6 7 2 3 6M19 19l-1 4" fill="none" stroke="#FF8A1E" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'),
    ('rainbow', 'Rainbow', 1500, 'Every colour, drifting slowly round you', '<clipPath id="skc3"><circle cx="20" cy="20" r="16"/></clipPath><g clip-path="url(#skc3)" transform="rotate(-30 20 20)"><rect x="0" y="2" width="40" height="6" fill="#FF4D6D"/><rect x="0" y="8" width="40" height="6" fill="#FF9F1C"/><rect x="0" y="14" width="40" height="6" fill="#FFE14D"/><rect x="0" y="20" width="40" height="6" fill="#3DDC84"/><rect x="0" y="26" width="40" height="6" fill="#3A86FF"/><rect x="0" y="32" width="40" height="6" fill="#9B5DE5"/></g><circle cx="20" cy="20" r="16" fill="none" stroke="#171320" stroke-width="2.4"/>'),
    ('matrix', 'Matrix', 1750, 'Green code raining down you', '<circle cx="20" cy="20" r="16" fill="#03140A" stroke="#171320" stroke-width="2.4"/><g fill="#2BFF6A"><rect x="11" y="9" width="2.4" height="3"/><rect x="11" y="14" width="2.4" height="3" opacity=".7"/><rect x="11" y="19" width="2.4" height="3" opacity=".4"/><rect x="18" y="13" width="2.4" height="3"/><rect x="18" y="18" width="2.4" height="3" opacity=".7"/><rect x="18" y="23" width="2.4" height="3" opacity=".45"/><rect x="25" y="8" width="2.4" height="3" opacity=".5"/><rect x="25" y="13" width="2.4" height="3" opacity=".8"/><rect x="25" y="18" width="2.4" height="3"/><rect x="25" y="23" width="2.4" height="3" fill="#D8FFE4"/></g>'),
    ('glitter', 'Glitter', 1250, 'Sparkling all over, in your paint colour', '<circle cx="20" cy="20" r="16" fill="#E8457A" stroke="#171320" stroke-width="2.4"/><g fill="#fff"><path d="M14 11l1 3 3 1-3 1-1 3-1-3-3-1 3-1z"/><path d="M26 20l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8z"/><circle cx="18" cy="26" r="1.1"/><circle cx="24" cy="12" r=".9"/><circle cx="11" cy="21" r=".8"/></g>'),
]

def apply(s):
    # ---- the shader: its uniforms and tools; the skin after the axolotl's own (before the face is drawn over it, and the paint);
    # its surface; what it gives off
    s = rep(s, "  return vec2(m, m > 0.0 ? r * sqrt(max(0.0, 1.0 - dd * dd / (r * r))) / 36.0 * 0.9 : 0.0); }`;",
               "  return vec2(m, m > 0.0 ? r * sqrt(max(0.0, 1.0 - dd * dd / (r * r))) / 36.0 * 0.9 : 0.0); }" + FX_PARS + "`;")
    s = rep(s, ".replace('#include <color_fragment>', '#include <color_fragment>\\n' + SKIN_FS + FACE_FS + COAT_FS)",
               ".replace('#include <color_fragment>', '#include <color_fragment>\\n' + SKIN_FS + FX_FS + FACE_FS + COAT_FS).replace('#include <metalnessmap_fragment>', '#include <metalnessmap_fragment>\\n' + FX_SURF)")
    s = rep(s, ".replace('#include <aomap_fragment>', '#include <aomap_fragment>\\n' + LOOK_FS)\n      .replace('#include <colorspace_fragment>'",
               ".replace('#include <aomap_fragment>', '#include <aomap_fragment>\\n' + LOOK_FS + FX_GLOW)\n      .replace('#include <colorspace_fragment>'")
    s = rep(s, "// the face: the game's slime face shader (eye layer or blink, the eye styles, pupils where the whites show, then the mouth)\nconst FACE_FS = `",
               "// (v387) the skins\nconst FX_FS = `" + FX_FS + "`, FX_SURF = `" + FX_SURF + "`, FX_GLOW = `" + FX_GLOW + "`;\n"
               "// the face: the game's slime face shader (eye layer or blink, the eye styles, pupils where the whites show, then the mouth)\nconst FACE_FS = `")
    # ---- the look: its skin uniform, the sweep and the time; setSkin (sweep: from the ground up, in the menus)
    s = rep(s, "      uTint: { value: new THREE.Vector4(1, 0, 1, 1) }, uTintTo: { value: new THREE.Vector4(1, 0, 1, 0) },\n    };",
               "      uTint: { value: new THREE.Vector4(1, 0, 1, 1) }, uTintTo: { value: new THREE.Vector4(1, 0, 1, 0) },\n"
               "      uFx: { value: new THREE.Vector4(0, 1, 0, 0) },   // (v387) the skin: which, how far it has swept up over the body, the time\n    };")
    s = rep(s, "  setEyeStyle(k) { this.U.fStyle.value = typeof k === 'string' ? (EYE_STYLE_K[k] || 0) : k; return this; }\n  setPaint(level)",
               "  setEyeStyle(k) { this.U.fStyle.value = typeof k === 'string' ? (EYE_STYLE_K[k] || 0) : k; return this; }\n"
               "  // (v387) a skin by its name (none: the paint's own skin); swept on from the ground up, or there at once\n"
               "  setSkin(id, sweep) { const k = { galaxy: 1, lava: 2, rainbow: 3, matrix: 4, glitter: 5 }[id] || 0, u = this.U.uFx.value; if (u.x === k) return this; u.x = k; u.y = sweep && k ? 0 : 1; return this; }\n"
               "  setPaint(level)")
    s = rep(s, "U.uLag.value.w = this.t;\n", "U.uLag.value.w = this.t; { const fx = U.uFx.value; fx.z = this.t; if (fx.y < 1) fx.y = Math.min(1, fx.y + dt * 0.95); } // (v387: the skin's time, and its sweep)\n")
    s = rep(s, "    I.setEyeStyle = k => look.setEyeStyle(k);\n    I.setExpression",
               "    I.setEyeStyle = k => look.setEyeStyle(k);\n    I.setSkin = (id, sweep) => look.setSkin(id, sweep); // (v387)\n    I.setExpression")
    # every character dressed each frame: its skin with the rest (swept on in the menus, there at once in a match or a portrait)
    s = rep(s, "SI.setIris((EYE_COLS[look.iris] || EYE_COLS.brown).lin); if (SI.setEyeStyle) SI.setEyeStyle(EYE_STYLE_K[look.eyes] || 0); }",
               "SI.setIris((EYE_COLS[look.iris] || EYE_COLS.brown).lin); if (SI.setEyeStyle) SI.setEyeStyle(EYE_STYLE_K[look.eyes] || 0); }\n"
               "    if (SI.setSkin) SI.setSkin(look.skin || null, state === 'menu' && lkOn()); // (v387: swept on in the locker, there at once anywhere else)")

    # ---- the items: five skins, their own kind; prices; your look keeps one
    s = rep(s, "const WEAR_WHERE = { island: 'Palette Island',",
               "// (v387) the skins: the whole body's look, one at a time, always in stock\n"
               "const SKINS = " + json.dumps([dict(id=i, name=n, slot='skin', stage='blank', desc=d) for i, n, p, d, sw in SKINS]) + ";\n"
               "WEAR.push(...SKINS);\n"
               "const SKIN_SW = " + json.dumps({i: sw for i, n, p, d, sw in SKINS}) + ";\n"
               "const WEAR_WHERE = { island: 'Palette Island',")
    s = rep(s, "const WEAR_CAT = { head: 'head', side: 'head', eye: 'face', lash: 'face', mouth: 'face', neck: 'cloth', back: 'cloth', arms: 'cloth' };",
               "const WEAR_CAT = { head: 'head', side: 'head', eye: 'face', lash: 'face', mouth: 'face', neck: 'cloth', back: 'cloth', arms: 'cloth', skin: 'skin' };")
    s = rep(s, "hat: 1105, antennae: 195, floaties: 245, snorkel: 295, propcap: 345, cape: 480 };",
               "hat: 1105, antennae: 195, floaties: 245, snorkel: 295, propcap: 345, cape: 480, " + ", ".join('%s: %d' % (i, p) for i, n, p, d, sw in SKINS) + " }; // (v387: the skins)")
    s = rep(s, "lash: ok(l.lash, 'lash'), arms: ok(l.arms, 'arms'), iris: ['brown', 'blue', 'green', 'violet', 'gold'].includes(l.iris) ? l.iris : 'brown' }; })();",
               "lash: ok(l.lash, 'lash'), arms: ok(l.arms, 'arms'), skin: ok(l.skin, 'skin'), iris: ['brown', 'blue', 'green', 'violet', 'gold'].includes(l.iris) ? l.iris : 'brown' }; })();")
    # portraits, friends and online rivals: the skin goes with the rest of what you wear
    s = rep(s, "PT_SLOTS = ['head', 'back', 'mouth', 'eye', 'side', 'neck', 'lash', 'arms'];", "PT_SLOTS = ['head', 'back', 'mouth', 'eye', 'side', 'neck', 'lash', 'arms', 'skin'];")
    s = rep(s, "lash: ok(w.lash, 'lash'), arms: ok(w.arms, 'arms'), iris: EYE_KEYS.includes(w.iris) ? w.iris : 'brown', eyes: EYE_STYLES[L.e] ? L.e : 'round' };",
               "lash: ok(w.lash, 'lash'), arms: ok(w.arms, 'arms'), skin: ok(w.skin, 'skin'), iris: EYE_KEYS.includes(w.iris) ? w.iris : 'brown', eyes: EYE_STYLES[L.e] ? L.e : 'round' };")

    # ---- the locker and the Paint Shop: Skins as a kind of their own
    s = rep(s, "const LK_CAT = { head: 'Headgear', face: 'Facial', cloth: 'Clothing', eyes: 'Eyes' };", "const LK_CAT = { skin: 'Skins', head: 'Headgear', face: 'Facial', cloth: 'Clothing', eyes: 'Eyes' };")
    s = rep(s, "const LK_FILT = [['all', 'All'], ['season', 'Spooky SZN'], ['head', 'Headgear'],", "const LK_FILT = [['all', 'All'], ['season', 'Spooky SZN'], ['skin', 'Skins'], ['head', 'Headgear'],")
    s = rep(s, "const LK_FI = {'all': ", "const LK_FI = {'skin': '<path d=\"M12 3.2l2.2 5.6 5.6 2.2-5.6 2.2L12 18.8l-2.2-5.6L4.2 11l5.6-2.2z\" fill=\"#FFD23F\"/><circle cx=\"18.6\" cy=\"18.4\" r=\"1.9\" fill=\"#FF7BC8\"/><circle cx=\"5.4\" cy=\"18.6\" r=\"1.3\" fill=\"#7CC8FF\"/>', 'all': ")
    s = rep(s, "  for (const c of ['head', 'face', 'cloth']) { const mine = WEAR.filter(w => w.cat === c && bought(w.id))",
               "  for (const c of ['skin', 'head', 'face', 'cloth']) { const mine = WEAR.filter(w => w.cat === c && bought(w.id))")
    s = rep(s, "    if (f === 'all') for (const c of ['head', 'face', 'cloth', 'eyes']) { const l = listed.filter(w => !w.season && w.cat === c).sort(by); if (l.length) h += '<p class=\"lksec\">' + LK_CAT[c] + '</p>' + grid(l); }",
               "    if (f === 'all') for (const c of ['skin', 'head', 'face', 'cloth', 'eyes']) { const l = listed.filter(w => !w.season && w.cat === c).sort(by); if (l.length) h += '<p class=\"lksec' + (c === 'skin' ? ' lkprem' : '') + '\">' + (c === 'skin' ? LK_FSVG + LK_FI.skin + '</svg>' : '') + LK_CAT[c] + '</p>' + grid(l); }")
    # a skin's card: a portrait of you in it (its swatch until that's made)
    s = rep(s, "function lkPic(w) { if (w.slot === 'eyes') return ES_ICON_T[w.id] || '';",
               "function lkPic(w) { if (w.slot === 'eyes') return ES_ICON_T[w.id] || ''; if (w.slot === 'skin') return ptHtml(ptSpec(colorOf().hex, { eyes: myLook.eyes, iris: myLook.iris, skin: w.id }), 'stimg lkskin', '<svg viewBox=\"0 0 40 40\" aria-hidden=\"true\">' + SKIN_SW[w.id] + '</svg>');")
    # now and then a CPU rival wears one too (one in eight, once the lessons are done); in 2v2 only the glitter, which is in its team's colour
    s = rep(s, "lash: Math.random() < (head === 'tiara' ? 0.65 : 0.18) ? 'lashes' : null, iris: Math.random() < 0.45 ? 'brown' : EYE_KEYS[1 + (Math.random() * 4 | 0)], eyes: ['round', 'round', 'edgy', 'dot', 'sly'][(Math.random() * 5) | 0] }; } }",
               "lash: Math.random() < (head === 'tiara' ? 0.65 : 0.18) ? 'lashes' : null, iris: Math.random() < 0.45 ? 'brown' : EYE_KEYS[1 + (Math.random() * 4 | 0)], eyes: ['round', 'round', 'edgy', 'dot', 'sly'][(Math.random() * 5) | 0],\n"
               "    skin: store.tut && store.tut.ph === 'done' && Math.random() < 0.125 ? (mode === 'duo' ? 'glitter' : SKINS[(Math.random() * SKINS.length) | 0].id) : null }; } } // (v387: a skin now and then)")
    # its line: what it is
    s = rep(s, "    kind = w.season ? 'Spooky SZN · ' + LK_CAT[w.cat] : LK_CAT[w.cat]; name = w.name;\n    line = own ? (needFind(w) ? 'Found on ' + where : 'From the Paint Shop') : found ? (owns(w.id) && needFind(w) ? 'You found it on ' + where : 'In stock now') : 'Found on ' + where + ' only';",
               "    kind = w.season ? 'Spooky SZN · ' + LK_CAT[w.cat] : LK_CAT[w.cat]; name = w.name;\n    line = own ? (needFind(w) ? 'Found on ' + where : 'From the Paint Shop') : found ? (owns(w.id) && needFind(w) ? 'You found it on ' + where : 'In stock now') : 'Found on ' + where + ' only';\n"
               "    if (w.slot === 'skin') line = w.desc; // (v387)")
    # putting one on: a twirl to show it all round, a ring and sparkles
    s = rep(s, "  SGD.dV = 0; SGD.dyaw = wrapA(SGD.dyaw); SGD.dyawTo = w.slot === 'back' ? 2.7 : w.slot === 'side' ? -0.8 : w.slot === 'arms' ? 0.75 : 0; SGD.dHold = SGD.dyawTo ? 2.2 : 0;",
               "  SGD.dV = 0; SGD.dyaw = wrapA(SGD.dyaw); SGD.dyawTo = w.slot === 'back' ? 2.7 : w.slot === 'side' ? -0.8 : w.slot === 'arms' ? 0.75 : 0; SGD.dHold = SGD.dyawTo ? 2.2 : 0;\n"
               "  if (w.slot === 'skin') { SGD.popId = null; SGD.dyaw -= 6.2832; SGD.dyawTo = 0; SGD.dHold = 0; sgRing(0, 0, 0.8, 0xFFE23C); } // (v387: a skin: once round, to show it all)")
    # the cards' portraits: square, filling the tag
    s = rep(s, ":is(#mStrokes,#mLocker).sgp .sgcard .sgca svg{position:absolute;inset:12%;z-index:1;width:76%;height:76%}",
               ":is(#mStrokes,#mLocker).sgp .sgcard .sgca svg{position:absolute;inset:12%;z-index:1;width:76%;height:76%}\n"
               "/* (v387) a skin's card: a round portrait of you in it, in a gold rim; the Skins heading in the shop */\n"
               "#mLocker .sgcard .sgca .lkskin{position:absolute;inset:6%;z-index:1;width:88%;height:88%;border-radius:50%;object-fit:cover;background:radial-gradient(circle at 50% 38%,#FFF8E2 0,#FBE3A0 48%,#E9B54A 100%);box-shadow:0 0 0 3px #171320,0 0 0 5.5px #F2C14E,0 3px 0 5.5px #171320}\n"
               "#mLocker .sgcard .sgca i.lkskin{display:block;background:none;box-shadow:none}#mLocker .sgcard .sgca i.lkskin svg{inset:0;width:100%;height:100%}\n"
               "#mLocker .lksec.lkprem{display:flex;align-items:center;gap:6px}#mLocker .lksec.lkprem svg{width:18px;height:18px;flex:none}\n")
    return s
