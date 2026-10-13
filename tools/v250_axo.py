"""Roll Model v250: the axolotl's look (fable5). Exact-replacement patch on the game html, character runtime only:
  1. the ink line (the existing back-face hull, still one draw): its width a fixed share of the screen whatever the camera's lens (it
     was about half a pixel in a match under the 80 degree camera), clamped in the body's own units, pushed back from the camera so it
     only shows on the outline (no ink leaking through where the body folds), and inked in a deep shade of the team's colour
  2. the toon shading: crisper two-step light bands, a lighter, richer shade, a clean rim of light inside the outline
usage: from v250_axo import apply; s = apply(s)"""

def _rep(s, old, new, n=1):
    assert s.count(old) == n, f'expected {n}, found {s.count(old)}: {old[:100]!r}'
    return s.replace(old, new)

def apply(s):
    # ---- 1. the ink line ----
    s = _rep(s, """    const INK = window.__axoInk || [0.0011, 0.004, 0.011], inkOf = meta => { const m = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide });
      m.onBeforeCompile = sh => { sh.vertexShader = sh.vertexShader.replace('#include <project_vertex>', '{ float gD = -(modelViewMatrix * vec4(transformed, 1.0)).z, gS = 0.5 * (length(modelMatrix[0].xyz) + length(modelMatrix[1].xyz)); transformed += normalize(objectNormal) * clamp(' + INK[0].toFixed(5) + ' * gD / max(gS, 1e-3), ' + INK[1].toFixed(4) + ', ' + INK[2].toFixed(4) + '); }\\n#include <project_vertex>'); };""",
             """    // (v250: its width a share of the screen's height whatever the camera's lens (the match's wide one, the victory's and the portraits'
    // narrow ones): INK[0] of the half height, about 3.5 px of a phone's 800; clamped in the body's own units (INK[1], INK[2]) so a far one
    // thins and a close one never balloons; then pushed back from the camera INK[3] times its own width, so where the body folds in on
    // itself (under the chin, the armpits, a tucked leg) the hull stays behind the skin and only the outline shows; inked in a deep shade
    // of the team's colour (inkTint, from setColor))
    const INK = window.__axoInk || [0.009, 0.004, 0.06, 2.5], inkOf = meta => { const m = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide });
      m.onBeforeCompile = sh => { sh.vertexShader = sh.vertexShader.replace('#include <project_vertex>', 'float gS = 0.5 * (length(modelMatrix[0].xyz) + length(modelMatrix[1].xyz)), gW = 0.0; { float gD = -(modelViewMatrix * vec4(transformed, 1.0)).z; gW = clamp(' + INK[0].toFixed(5) + ' * gD / (max(projectionMatrix[1][1], 1e-3) * max(gS, 1e-3)), ' + INK[1].toFixed(4) + ', ' + INK[2].toFixed(4) + '); transformed += normalize(objectNormal) * gW; }\\n#include <project_vertex>\\nmvPosition.z -= ' + (INK[3] === undefined ? 2.5 : INK[3]).toFixed(2) + ' * gW * gS; gl_Position = projectionMatrix * mvPosition;'); };""")
    s = _rep(s, """    I.setColor = c => { if (I.color.equals(c)) return; I.color.copy(c); look.setColor(c.getHex()); for (const gh of ghosts) gh.material.color.copy(c); };""",
             """    const ink0 = new THREE.Color(C.outline), inkHSL = {}, inkTint = c => { c.getHSL(inkHSL, THREE.SRGBColorSpace); for (const M of [Sm, Cm]) M.ink.material.color.setHSL(inkHSL.h, Math.min(0.8, 0.3 + 0.55 * inkHSL.s), 0.12, THREE.SRGBColorSpace).lerp(ink0, 0.3); }; inkTint(col); // (v250: the ink a deep shade of its colour)
    I.setColor = c => { if (I.color.equals(c)) return; I.color.copy(c); look.setColor(c.getHex()); for (const gh of ghosts) gh.material.color.copy(c); inkTint(c); };""")
    # ---- 2. the toon shading ----
    s = _rep(s, """  float b = 0.5 * smoothstep(0.1, 0.42, w) + 0.5 * smoothstep(0.5, 0.78, w); return mix(w, max(0.3 + 0.7 * b, 0.3), uToon); }""",
             """  float b = 0.45 * smoothstep(0.14, 0.3, w) + 0.55 * smoothstep(0.52, 0.66, w); return mix(w, 0.38 + 0.62 * b, uToon); }   // (v250: crisper bands, a lighter shade)""")
    s = _rep(s, """      uToon: { value: 0.7 },   // v10b: the toon look's strength (0 the plain material, 1 full)""",
             """      uToon: { value: 0.82 },   // v10b: the toon look's strength (0 the plain material, 1 full) (v250: 0.7 -> 0.82)""")
    s = _rep(s, """  reflectedLight.indirectDiffuse += diffuseColor.rgb * vec3(1.0, 0.9, 0.84) * (0.14 * uToon) * (1.0 - sCoatM) * (1.0 - ink);   // (v10b: a warm fill in the shade)""",
             """  reflectedLight.indirectDiffuse += pow(max(diffuseColor.rgb, vec3(0.0)), vec3(1.15)) * vec3(1.04, 0.9, 0.92) * (0.16 * uToon) * (1.0 - sCoatM) * (1.0 - ink);   // (v10b: a warm fill in the shade; v250: in the skin's own deeper colour)""")
    s = _rep(s, """  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0, 0.95, 0.92), 0.35) * pow(edge, 3.0) * (0.5 + 0.5 * upk) * 0.22 * (1.0 - ink) * (1.0 - 0.5 * sCoatM);""",
             """  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0, 0.95, 0.92), 0.35) * pow(edge, 3.0) * (0.5 + 0.5 * upk) * 0.22 * (1.0 - ink) * (1.0 - 0.5 * sCoatM);
  // (v250: the toon rim: a clean band of light just inside the ink line, on the side toward the sky)
  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0, 0.97, 0.95), 0.5) * smoothstep(0.62, 0.76, edge) * smoothstep(0.45, 1.0, upk) * 0.2 * uToon * (1.0 - ink) * (1.0 - 0.6 * sCoatM);""")
    return s

if __name__ == '__main__':
    import sys
    src = open(sys.argv[1]).read(); out = apply(src); open(sys.argv[2], 'w').write(out); print('applied', len(src), '->', len(out))
