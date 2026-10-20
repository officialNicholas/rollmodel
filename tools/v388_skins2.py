"""v388: the skins, second pass (the user: brighter red in the lava, brighter sparkles and stars, a new rainbow).

- Lava: its cracks' red runs hotter and wider: a vivid red edge round every crack and a red glow spilling a little onto the rock beside
  it; even the coolest cracks stay lit.
- Galaxy: more stars, brighter, and their twinkle never drops them out entirely.
- Glitter: more of the flakes catch the light, and they and the dust between them flare much brighter.
- Rainbow: no more stripes. Now holographic foil: every colour, turning with the angle you see it from and swirling slowly across the
  body, pearly, with white glints (picked from three tried: the foil, tie-dye swirls, a smooth head-to-tail rainbow)."""

import json, importlib.util, os

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

RAINBOW = {
  # holographic foil: the colour turns with the angle you see it at and swirls across the body, pearly, with white glints
  1: r"""    float wv = fxFbm(cp * 2.2 + vec3(0.0, t * 0.06, 0.0));
    float hh = fract(1.1 * (1.0 - dot(fxN, fxV)) + wv * 0.9 + cp.y * 0.35 - t * 0.05);
    vec3 c = mix(pow(fxHsv(hh, 0.66, 1.0), vec3(2.2)), vec3(1.0), 0.1);
    float hu = 0.0, gl = fxStars(cp, 52.0, 0.3, 0.06, t, 1.0, hu);
    col = c * 0.9 + gl * 0.4;
    glow = c * 0.22 + vec3(1.0) * gl * 2.2 + c * fxFr * 0.5;
    sFxRough = 0.18; sFxMetal = 0.35;""",
  # tie-dye swirls: every colour marbled together, slowly flowing
  2: r"""    vec3 wp = cp * 1.8, q = vec3(fxFbm(wp + vec3(0.0, 0.0, t * 0.05)), fxFbm(wp + 5.2), fxFbm(wp + 9.7));
    float hh = fract(fxFbm(wp * 1.3 + q * 2.2 + vec3(0.0, -t * 0.08, 0.0)) * 2.4);
    vec3 c = pow(fxHsv(hh, 0.82, 1.0), vec3(2.2));
    col = c * 0.95;
    glow = c * 0.16 + mix(c, vec3(1.0), 0.4) * fxFr * 0.35;
    sFxRough = 0.3;""",
  # a smooth rainbow from head to tail, gently rippling and flowing, a soft sheen sliding along it
  3: r"""    float u = cp.y * 0.95 + 0.06 * sin(cp.x * 5.0 + t * 0.8) + 0.18 * fxFbm(cp * 3.0 + vec3(0.0, t * 0.1, 0.0));
    vec3 c = pow(fxHsv(fract(u * 0.9 - t * 0.04), 0.72, 1.0), vec3(2.2));
    float sh = pow(0.5 + 0.5 * sin((cp.y * 6.0 + cp.x * 3.0 + cp.z * 2.0) - t * 2.0), 14.0);
    c = mix(c, vec3(1.0), 0.18 * sBelly);
    col = c * 0.93 + sh * 0.12;
    glow = c * 0.15 + vec3(1.0) * sh * 0.45 + mix(c, vec3(1.0), 0.5) * fxFr * 0.3;
    sFxRough = 0.22;""",
}

def apply(s):
    # ---- lava: a hotter, wider red
    s = rep(s, "vec3(0.11, 0.022, 0.0) * (1.0 - smoothstep(0.0, 0.16, e)) * (0.25 + 0.75 * heat);",
               "vec3(0.42, 0.035, 0.0) * (1.0 - smoothstep(0.0, 0.2, e)) * (0.45 + 0.55 * heat);")
    s = rep(s, "vec3 hot = mix(vec3(1.1, 0.12, 0.0), vec3(2.0, 0.65, 0.04), heat);", "vec3 hot = mix(vec3(2.4, 0.16, 0.01), vec3(2.6, 0.8, 0.05), heat);")
    s = rep(s, "float molten = max(crack * mix(0.35, 1.0, heat) * mix(0.75, 1.0, breathe), vein * 0.45);",
               "float molten = max(crack * mix(0.6, 1.0, heat) * mix(0.8, 1.0, breathe), vein * 0.55), halo = (1.0 - smoothstep(w, w + 0.12, e)) * (1.0 - crack);")
    s = rep(s, "glow = hot * molten * 1.5 + vec3(0.5, 0.08, 0.0) * fxFr * 0.22 * heat;",
               "glow = hot * molten * 1.7 + vec3(1.1, 0.06, 0.0) * halo * (0.35 + 0.45 * heat) + vec3(0.6, 0.08, 0.0) * fxFr * 0.3 * heat;")
    # ---- galaxy: more, brighter stars that never twinkle out
    s = rep(s, "float w = mix(1.0, 0.5 + 0.5 * sin(t * (1.1 + 2.4 * h.y) + h.x * 40.0), tw); w *= w;",
               "float w = mix(1.0, 0.55 + 0.45 * sin(t * (1.1 + 2.4 * h.y) + h.x * 40.0), tw); w = 0.25 + 0.75 * w * w;")
    s = rep(s, "float s1 = fxStars(cp, 46.0, 0.45, 0.07, t, 0.55, h1); float s2 = fxStars(cp + 7.3, 15.0, 0.32, 0.05, t, 1.0, h2);",
               "float s1 = fxStars(cp, 46.0, 0.58, 0.08, t, 0.55, h1); float s2 = fxStars(cp + 7.3, 15.0, 0.42, 0.06, t, 1.0, h2);")
    s = rep(s, "col += c1 * s1 * 0.5 + c2 * s2 * 0.6;\n    glow = c1 * s1 * 1.1 + c2 * s2 * 2.6 +",
               "col += c1 * s1 * 0.7 + c2 * s2 * 0.8;\n    glow = c1 * s1 * 2.4 + c2 * s2 * 5.0 +")
    # ---- glitter: more flakes catch the light, all of it brighter
    s = rep(s, "float spec = pow(saturate(dot(fn, H)), 26.0), flash = pow(max(0.0, sin(t * (1.6 + 2.6 * h.y) + h.z * 60.0)), 10.0);",
               "float spec = pow(saturate(dot(fn, H)), 18.0), flash = pow(max(0.0, sin(t * (1.6 + 2.6 * h.y) + h.z * 60.0)), 8.0);")
    s = rep(s, "glow = mix(tc, vec3(1.0), 0.45) * (sp * 1.6 + dust * 1.2) +", "glow = mix(tc, vec3(1.0), 0.5) * (sp * 3.2 + dust * 2.6) +")
    # ---- rainbow: holographic foil
    i = s.index("    // RAINBOW: candy bands"); j = s.index("  } else if (k < 4.5) {", i)
    s = s[:i] + "    // RAINBOW: holographic foil: the colour turns with the angle it's seen from and swirls slowly across the body, pearly, white glints\n" + RAINBOW[1] + "\n" + s[j:]
    # its line, and its swatch on the card until its portrait is made
    s = rep(s, '"desc": "Every colour, drifting slowly round you"', '"desc": "Holographic, its colours shifting as you move"')
    spec = importlib.util.spec_from_file_location('v387s', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v387_skins.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    old = [sw for i2, n, p, d, sw in m.SKINS if i2 == 'rainbow'][0]
    new = ('<linearGradient id="skg3" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FF9AD5"/><stop offset=".3" stop-color="#9FE8FF"/><stop offset=".55" stop-color="#B9FFB0"/>'
           '<stop offset=".8" stop-color="#FFF09A"/><stop offset="1" stop-color="#C9A6FF"/></linearGradient><circle cx="20" cy="20" r="16" fill="url(#skg3)" stroke="#171320" stroke-width="2.4"/>'
           '<path d="M10 22c4-6 9-8 15-6M13 28c5-3 10-4 14-2" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" opacity=".8"/><circle cx="26" cy="12" r="1.5" fill="#fff"/>')
    s = rep(s, json.dumps(old)[1:-1], json.dumps(new)[1:-1])
    return s
