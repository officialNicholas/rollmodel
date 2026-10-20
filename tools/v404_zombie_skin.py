"""v404: a Zombie skin (the user: "look at the skins we have. Make a zombie skin"), the sixth of v387's skins, drawn the same way
(in the axolotl's own shader, riding along with every squash and stride, swept on in the locker, in the Paint Shop's Skins).

Grey-green rotting skin, mottled lighter and darker, with sunken patches of decay and purple bruising; stitched-up scars across the
body (a dark seam with its cross-stitches); dark green veins under the skin with a faint slow pulse, as if something still beats in
there; a damp sheen. 1,500 dabs. The face, your paint and your team's ink line are drawn over it as with every skin."""
import json

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

ZOMBIE_FS = r"""
  } else {
    // ZOMBIE: grey-green rotting skin, mottled, with sunken patches of decay and purple bruises; stitched-up scars across it (a dark
    // seam and its cross-stitches); sickly green veins under the skin, pulsing slowly; a damp sheen
    float n1 = fxFbm(cp * 3.1 + 2.0), n2 = fxFbm(cp * 7.5 - 1.3), n3 = aNoise(cp * 24.0);
    vec3 zc = mix(vec3(0.085, 0.115, 0.065), vec3(0.21, 0.25, 0.14), smoothstep(0.3, 0.75, n1)) * (0.85 + 0.3 * n3);
    float rot = smoothstep(0.6, 0.82, n2); zc = mix(zc, vec3(0.022, 0.03, 0.012), rot * 0.85);
    float bruise = smoothstep(0.62, 0.86, fxFbm(cp * 2.2 + 9.0)); zc = mix(zc, vec3(0.07, 0.02, 0.08), bruise * 0.55);
    zc = mix(zc, vec3(0.3, 0.33, 0.2), 0.32 * sBelly) * (1.0 - 0.15 * fFace);
    // the scars: two seams across the body, each only along part of it, with cross-stitches
    float st = 0.0, sm = 0.0;
    for (int j = 0; j < 2; j++) {
      vec3 dir = j == 0 ? normalize(vec3(0.82, 0.48, 0.3)) : normalize(vec3(-0.35, 0.6, 0.72)), per = normalize(cross(dir, vec3(0.0, 0.2, 1.0) + vec3(0.6, 0.0, 0.0) * float(j)));
      float u = dot(cp, dir) * 1.7 + (j == 0 ? 0.25 : 0.6), l = abs(fract(u) - 0.5) / 1.7, aa = fwidth(l) + 0.002;
      float on = smoothstep(0.45, 0.6, aNoise(cp * 1.4 + float(j) * 5.3));
      float seam = (1.0 - smoothstep(0.006, 0.006 + aa, l)) * on, wound = (1.0 - smoothstep(0.012, 0.03 + aa, l)) * on;
      float v = dot(cp, per) * 26.0, tick = (1.0 - smoothstep(0.08, 0.16, abs(fract(v) - 0.5))) * (1.0 - smoothstep(0.03, 0.045 + aa, l)) * on;
      st = max(st, max(seam, tick)); sm = max(sm, wound);
    }
    zc = mix(zc, vec3(0.16, 0.035, 0.04), sm * 0.7); zc = mix(zc, vec3(0.02, 0.015, 0.012), st);
    // veins: thin lines in the noise, faintly green, a slow pulse running through them
    float vn = abs(aNoise(cp * 8.5 + vec3(0.0, -t * 0.05, 0.0)) - 0.5), va = fwidth(vn) + 0.004, vein = (1.0 - smoothstep(0.012, 0.03 + va, vn)) * (1.0 - rot) * (1.0 - st);
    float pulse = 0.5 + 0.5 * sin(t * 2.0 - dot(cp, vec3(0.0, 3.0, 1.0)) * 2.5);
    vec3 sick = vec3(0.25, 0.85, 0.12);
    col = mix(zc, vec3(0.03, 0.09, 0.02), vein * 0.55);
    glow = sick * vein * (0.012 + 0.05 * pulse) + vec3(0.2, 0.45, 0.12) * fxFr * 0.1;
    sFxRough = mix(0.42, 0.75, rot);
  }
"""

SWATCH = ('<radialGradient id="skg6" cx="38%" cy="35%" r="75%"><stop offset="0" stop-color="#7E9A55"/><stop offset="1" stop-color="#34452A"/></radialGradient>'
          '<circle cx="20" cy="20" r="16" fill="url(#skg6)" stroke="#171320" stroke-width="2.4"/><circle cx="26" cy="25" r="4.5" fill="#4A2A4E" opacity=".55"/>'
          '<path d="M9 16l16-6" stroke="#2A1620" stroke-width="1.6" stroke-linecap="round"/><path d="M11 13.6l1 3.6M14.4 12.4l1 3.6M17.8 11.2l1 3.6M21.2 10l1 3.6" stroke="#2A1620" stroke-width="1.2" stroke-linecap="round"/>'
          '<path d="M12 27c3-2 5 1 8-1" fill="none" stroke="#9BFF6A" stroke-width="1" opacity=".8"/>')

def apply(s):
    s = rep(s, "  } else {\n    // GLITTER", "  } else if (k < 5.5) {\n    // GLITTER")
    s = rep(s, "    sFxRough = 0.28; sFxMetal = 0.55;\n  }", "    sFxRough = 0.28; sFxMetal = 0.55;" + ZOMBIE_FS.rstrip('\n'))
    s = rep(s, "galaxy: 1, lava: 2, rainbow: 3, matrix: 4, glitter: 5 }", "galaxy: 1, lava: 2, rainbow: 3, matrix: 4, glitter: 5, zombie: 6 }")
    s = rep(s, "WEAR.push(...SKINS);", "SKINS.push({ id: 'zombie', name: 'Zombie', slot: 'skin', stage: 'blank', desc: 'Stitched together, still twitching' }); // (v404)\nWEAR.push(...SKINS);")
    s = rep(s, "const SKIN_SW = {", "const SKIN_SW = {\"zombie\": " + json.dumps(SWATCH) + ", ")
    s = rep(s, "glitter: 1250 }", "glitter: 1250, zombie: 1500 }")
    return s
