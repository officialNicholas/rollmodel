"""v389: Galaxy, the user's way: a matte skin, almost pure dark, the galaxy in it (the nebulae, the dusty band) glowing brighter, and the
stars brighter still.

- The skin itself is near black and matte: no gloss, no clearcoat, no sheen, almost no reflection (a skin can now ask for that: sFxMatte,
  applied after the body's own lighting setup, which sets the roughness afresh). The paint coat and the eyes keep their shine.
- The nebulae (magenta, blue, a teal wisp) and the band are light of their own, not a colour lit by the scene, so they glow on the dark
  in any light; only a hint of the colour is in the surface.
- The stars are light only, about twice as bright as before, the big ones brightest; a faint violet rim keeps the shape readable."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

GALAXY = r"""    // GALAXY: matte, almost pure dark; the nebulae (magenta, blue, a teal wisp) and a dusty band glowing on it; two layers of stars,
    // brighter still, twinkling
    float n1 = fxFbm(cp * 2.4 + 1.3), n2 = fxFbm(cp * 5.2 - 2.1), n3 = fxFbm(cp * 3.6 + 7.7);
    float a = smoothstep(0.6, 0.88, n1 * 0.65 + n2 * 0.45), b = smoothstep(0.63, 0.9, n2 * 0.7 + (1.0 - n1) * 0.4), c3 = smoothstep(0.68, 0.93, n3);
    vec3 neb = vec3(0.8, 0.06, 0.6) * a + vec3(0.06, 0.26, 1.0) * b + vec3(0.0, 0.6, 0.65) * c3 * 0.55;
    float band = exp(-pow((cp.y * 0.8 + cp.x * 1.1 - cp.z * 0.4 - 0.75) / 0.11, 2.0)) * smoothstep(0.35, 0.75, n2);
    float h1 = 0.0, h2 = 0.0; float s1 = fxStars(cp, 46.0, 0.58, 0.08, t, 0.55, h1); float s2 = fxStars(cp + 7.3, 15.0, 0.42, 0.06, t, 1.0, h2);
    vec3 c1 = mix(vec3(0.8, 0.88, 1.0), vec3(1.0, 0.88, 0.75), h1), c2 = mix(vec3(0.85, 0.92, 1.0), vec3(1.0, 0.8, 0.96), h2);
    col = vec3(0.004, 0.0035, 0.011) + neb * 0.05 + vec3(0.25, 0.16, 0.35) * band * 0.03;
    glow = neb * 1.2 + vec3(0.42, 0.28, 0.6) * band * 0.5 + c1 * s1 * 4.6 + c2 * s2 * 9.5 + vec3(0.22, 0.18, 0.6) * fxFr * 0.14;
    sFxMatte = 1.0;
"""

FX_MATTE = r"""
{ float fxMt = sFxMatte * sFxM * (1.0 - sCoatM) * (1.0 - sEyeM);   // (v389: a matte skin: no gloss, clearcoat, sheen; the paint and the eyes keep theirs)
  if (fxMt > 0.0) { material.roughness = mix(material.roughness, 1.0, fxMt); material.specularColor *= 1.0 - 0.93 * fxMt; material.specularF90 *= 1.0 - 0.93 * fxMt;
#ifdef USE_CLEARCOAT
    material.clearcoat *= 1.0 - fxMt;
#endif
#ifdef USE_SHEEN
    material.sheenColor *= 1.0 - fxMt;
#endif
  } }
"""

def apply(s):
    s = rep(s, "float sFxM = 0.0, sFxRough = -1.0, sFxMetal = -1.0;", "float sFxM = 0.0, sFxRough = -1.0, sFxMetal = -1.0, sFxMatte = 0.0;")
    i = s.index("    // GALAXY: deep space"); j = s.index("  } else if (k < 2.5) {", i)
    s = s[:i] + GALAXY + s[j:]
    s = rep(s, "`, FX_GLOW = `", "`, FX_MATTE = `" + FX_MATTE + "`, FX_GLOW = `")
    s = rep(s, ".replace('#include <lights_physical_fragment>', '#include <lights_physical_fragment>\\n' + LIT_FS)",
               ".replace('#include <lights_physical_fragment>', '#include <lights_physical_fragment>\\n' + LIT_FS + FX_MATTE)")
    s = rep(s, '"desc": "Deep space, its stars twinkling"', '"desc": "Deep, dark space, its stars twinkling"')
    return s
