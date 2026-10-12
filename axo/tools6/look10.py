# The v10 look on the axolotl runtime: the slime's head and ears (axo/tools6/slimehead.py) read right by the shader, as exact-text edits
# on the v9b runtime (fable2/out/axo.js: the v227 base plus axo/tools5/look9.py), so every anchor the game's embed builder matches by
# text is kept verbatim. The gill channel (mat.y) now carries the head mask: 0.2 on the skull (fading down the neck), 1.0 on the ears.
#   python3 -I look10.py [base = S/fable2/out/axo.js] [out = S/fable3/out/axo.js] [--B]
# Variant A (default): the ears in the body's own skin material (the texel at the ear's root, the team hue turn, the saturation, a mild
# mottle so they are not flat), as smooth as the face skin; no frill colour and no filament relief on them any more.
# Variant B (--B): on top of A, the head and the ears in the slime's smooth glossy jelly in the team colour (darker over the crown and
# the back of the head, a slow drift of light and dark through it, the face a paler, warmer, skin-like shade in the slime's own oval,
# the ear tips a touch see-through), glass-glossy, no pores; the body keeps its texture and the neck blends over.
import sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
a = [x for x in sys.argv[1:] if not x.startswith('--')]; B = '--B' in sys.argv
SRC = a[0] if len(a) > 0 else S + '/fable2/out/axo.js'
OUT = a[1] if len(a) > 1 else S + ('/fable3/out_B/axo.js' if B else '/fable3/out/axo.js')
s = open(SRC).read()
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:100]!r}'
    s = s.replace(old, new)

# ---- the ear mask (v10): the gill channel is the ear now; the skull carries 0.2 so the look can tell the head from the body ----
rep("float sFaceK = 0.0, sCoatH = 0.0, sCoatT = 0.0, sBead = 0.0, sDbgDm = 0.0, sDbgG = 0.0, sCatch = 0.0, sWetK = 0.0; vec3 sPaintC = vec3(0.0);   // v9: face skin, the coat's height (m) and thickness, beads, the paint colour",
    "float sFaceK = 0.0, sCoatH = 0.0, sCoatT = 0.0, sBead = 0.0, sDbgDm = 0.0, sDbgG = 0.0, sCatch = 0.0, sWetK = 0.0; vec3 sPaintC = vec3(0.0);   // v9: face skin, the coat's height (m) and thickness, beads, the paint colour\n"
    "float sEar = 0.0, sHeadM = 0.0, sJelly = 0.0, sFaceM = 0.0;   // v10: the ears, the head (skull and ears), the jelly look on them, the face's oval")
rep("uniform vec3 uSkin, uBelly, uSpot, uGill, uGillTip, uFinCore, uFinGlow, uPaint; uniform vec4 uCoat, uDetail, uDetail2, uTint, uTintTo; uniform float uCoatMix;",
    "uniform vec3 uSkin, uBelly, uSpot, uGill, uGillTip, uFinCore, uFinGlow, uPaint, uTeam; uniform vec4 uCoat, uDetail, uDetail2, uTint, uTintTo; uniform float uCoatMix;")
# ---- the toon look (v10b, the user: "remove or drastically reduce the shadows", "apply the toon look of the previous character"):
# the diffuse of every light wrapped round the terminator (half-Lambert style) and banded softly in two wide steps, its dark side never
# under a third of the key; the baked occlusion mostly off; a warm fill in the shade; the highlight smaller and crisper. uToon 0..1 ----
rep("      uDetail: { value: new THREE.Vector4(0.0009, 26, 1.0, 0.0007) }, uDetail2: { value: new THREE.Vector4(0, 0, 0, 0) },",
    "      uDetail: { value: new THREE.Vector4(0.0009, 26, 1.0, 0.0007) }, uDetail2: { value: new THREE.Vector4(0, 0, 0, 0) },\n"
    "      uToon: { value: 0.7 },   // v10b: the toon look's strength (0 the plain material, 1 full)")
rep("float sEar = 0.0, sHeadM = 0.0, sJelly = 0.0, sFaceM = 0.0;   // v10: the ears, the head (skull and ears), the jelly look on them, the face's oval",
    "float sEar = 0.0, sHeadM = 0.0, sJelly = 0.0, sFaceM = 0.0;   // v10: the ears, the head (skull and ears), the jelly look on them, the face's oval\n"
    "uniform float uToon;\n"
    "// v10b: the diffuse ramp of each light: wrapped past the terminator, two soft wide bands, a floor so the shade stays a lighter skin\n"
    "float axoRamp(float x) { float w = mix(saturate(x), saturate((x + 0.55) / 1.55), uToon);\n"
    "  float b = 0.5 * smoothstep(0.1, 0.42, w) + 0.5 * smoothstep(0.5, 0.78, w); return mix(w, max(0.3 + 0.7 * b, 0.3), uToon); }")
rep("""    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\n' + FRAG_PARS)""",
    """    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\n' + FRAG_PARS)
      .replace('#include <lights_physical_pars_fragment>', THREE.ShaderChunk.lights_physical_pars_fragment.replace('reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );',
        'reflectedLight.directDiffuse += axoRamp( dot( geometryNormal, directLight.direction ) ) * directLight.color * BRDF_Lambert( material.diffuseColor );'))""")
rep("{ float occ = sAO * (1.0 - 0.3 * sCoatM), ink = clamp(sDrawM - sEyeM, 0.0, 1.0) * (1.0 - sCoatM), eyeK = sEyeM * (1.0 - sCoatM);",
    "{ float occ = sAO * (1.0 - 0.3 * sCoatM) * (1.0 - 0.7 * uToon), ink = clamp(sDrawM - sEyeM, 0.0, 1.0) * (1.0 - sCoatM), eyeK = sEyeM * (1.0 - sCoatM);\n"
    "  reflectedLight.indirectDiffuse += diffuseColor.rgb * vec3(1.0, 0.9, 0.84) * (0.14 * uToon) * (1.0 - sCoatM) * (1.0 - ink);   // (v10b: a warm fill in the shade)")
rep("  rough = mix(rough, 0.4, 0.6 * sFaceK);   // (the face skin a touch smoother)",
    "  rough = mix(rough, 0.4, 0.6 * sFaceK);   // (the face skin a touch smoother)\n  rough = mix(rough, 0.3, 0.45 * uToon);   // (v10b: a smaller, crisper highlight)")
# the textured skin: the ears are skin (the texel at their root), with a mild mottle of their own so they do not read flat
rep("""  gk = smoothstep(0.35, 0.8, gill);   // (the stalks keep the skin's pink; the thin fronds take the frill colour)
#else""",
"""  gk = 0.0; sEar = smoothstep(0.35, 0.8, gill); sHeadM = smoothstep(0.08, 0.2, gill);   // (v10: the gill channel is the ear mask; the skull carries 0.2)
  col *= 1.0 + sEar * (0.12 * (n1 - 0.5) + 0.05 * (n2 - 0.5));
#else""")
rep("  col = mix(col, gc, gk); sGill = gill;", "  col = mix(col, gc, gk); sGill = gk;")
# the ears as smooth as the face skin, not the frills' roughness; no filament relief on them
rep("  float rough = mix(0.52, 0.32, sBelly); rough = mix(rough, 0.52, sGill * 0.7); rough = mix(rough, 0.34, sFin * 0.6);",
    "  float rough = mix(0.52, 0.32, sBelly); rough = mix(rough, 0.52, sGill * 0.7); rough = mix(rough, 0.34, sFin * 0.6); rough = mix(rough, 0.4, 0.6 * sEar);")
rep("  h += 0.05 * uDetail.x * sGill * (0.5 + 0.5 * sin(vAlong * 480.0 + aNoise(cp * 11.0 + 7.1) * 8.0)) * k3 * kg;\n", "")
rep("  material.sheenColor = (uBelly * (0.5 * sBelly + 0.15 * sGill) + mix(diffuseColor.rgb, vec3(1.0), 0.5) * 0.3 * sFaceK) * (1.0 - sCoatM); material.sheenRoughness = 0.42;",
    "  material.sheenColor = (uBelly * (0.5 * sBelly + 0.15 * sGill) + mix(diffuseColor.rgb, vec3(1.0), 0.5) * (0.3 * sFaceK + 0.12 * sEar)) * (1.0 - sCoatM) * (1.0 - sJelly); material.sheenRoughness = 0.42;")
# the drag of the head's own motion on the ears: the v227 gains back (v9b had halved them for its lobes) and a wider soft limit, so a
# nod or a lurch of the head swings the big ears further; the spring's k and c live in the animator (axolife.js)
rep("      const cl = x => 16 * Math.tanh(x / 16);   // a soft limit: the drag saturates instead of clipping",
    "      const cl = x => 28 * Math.tanh(x / 28);   // a soft limit: the drag saturates instead of clipping (v10: wider for the ears)")
# (the signs follow the ears' frames: X the hinge along +x on both sides, Z back, Y down. A positive flex swings both tips back, a positive
# swing moves both tips to -x. The head moving forward (v along -Z) trails them back; speeding up (accS.z > 0) trails them back and
# stopping swings them forward; a left turn (accS.x > 0) throws them to the outside, -x; the old stalks' mirrored sign is gone. The
# sideways swing comes from the turn alone: the head joint's sideways velocity in the crawl carries a drift of the gait's own (negative
# in a turn either way), which threw one turn's swing away and doubled the other's)
rep("this.gillTarget[j * 2] = cl(flutter - _v.z * 15 - this.accS.z * 6); this.gillTarget[j * 2 + 1] = cl(-_v.x * 15 - this.accS.x * 5 * sgn);",
    "this.gillTarget[j * 2] = cl(flutter - _v.z * 22 + this.accS.z * 8); this.gillTarget[j * 2 + 1] = cl(this.accS.x * 6);")
# the debug region view shows the ears where the gills were
rep("  else if (uDebug < 4.5) gl_FragColor = vec4(sBelly, vJelly.z, sGill, 1.0);", "  else if (uDebug < 4.5) gl_FragColor = vec4(sBelly, vJelly.z, max(sEar, 0.5 * sHeadM), 1.0);")

if B:
    # ---- variant B: the slime's jelly on the head and the ears, after the texture's colour and before the face is drawn ----
    rep("""  col *= 1.0 + sEar * (0.12 * (n1 - 0.5) + 0.05 * (n2 - 0.5));
#else""",
"""  col *= 1.0 + sEar * (0.12 * (n1 - 0.5) + 0.05 * (n2 - 0.5));
  // the slime's jelly (v10 B): the team colour a touch softened, deeper over the crown and down the back of the head (darker above, as
  // animals are), a slow drift of light and dark through it; the face a paler, warmer, skin-like shade in the slime's own oval
  if (sHeadM > 0.001) { vec3 lw = vec3(0.2126, 0.7152, 0.0722), bc = max(mix(vec3(dot(uTeam, lw)), uTeam, 0.9), vec3(0.0));
    vec3 deep = max(mix(vec3(dot(bc, lw)), bc, 1.3), vec3(0.0)) * 0.3, lite = mix(bc, vec3(1.0, 0.86, 0.72), 0.07) * 1.1;
    float mot = aNoise(cp * 2.7 + 3.1) * 0.62 + aNoise(cp * 6.1 - 1.7) * 0.38;
    float dors = smoothstep(-0.1, 0.9, dot(normalize(vNormal), normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz)));
    vec3 jel = mix(bc, mix(bc, deep, 0.6), dors * 0.65) * (0.88 + 0.24 * mot);
    jel = mix(jel, lite, (1.0 - dors) * 0.12);
    vec2 fq = vFace.xy * fComp.xy, fe = vec2(fq.x / 0.98, (fq.y + 0.14) / 0.94); sFaceM = (1.0 - smoothstep(0.6, 1.0, length(fe))) * smoothstep(0.08, 0.4, vFace.z);
    vec3 skinC = mix(bc, vec3(1.0, 0.78, 0.66), 0.42); skinC = mix(vec3(dot(skinC, lw)), skinC, 0.85);
    jel = mix(jel, skinC, sFaceM);
    sJelly = sHeadM; col = mix(col, jel, sJelly); }
#else""")
    # glass-glossy jelly, the face's oval a little less so; no pores on it
    rep("  rough = mix(rough, 0.4, 0.6 * sFaceK);   // (the face skin a touch smoother)",
        "  rough = mix(rough, 0.4, 0.6 * sFaceK);   // (the face skin a touch smoother)\n  rough = mix(rough, mix(0.13, 0.3, sFaceM), sJelly);   // (v10 B: the jelly)")
    rep("  material.clearcoat = mix(0.12 + 0.28 * sBelly + 0.12 * sFin + 0.2 * sFaceK, 1.0, max(max(sCoatM, 0.45 * sEyeM), 0.7 * sWetK)) * (1.0 - 0.9 * inkM);",
        "  material.clearcoat = mix(0.12 + 0.28 * sBelly + 0.12 * sFin + 0.2 * sFaceK + 0.75 * sJelly * (1.0 - 0.5 * sFaceM), 1.0, max(max(sCoatM, 0.45 * sEyeM), 0.7 * sWetK)) * (1.0 - 0.9 * inkM);")
    rep("  material.clearcoatRoughness = min(max(mix(0.46 - 0.18 * sBelly - 0.1 * sFaceK, 0.03, max(max(sCoatM, sEyeM), sWetK)), 0.0525) + geometryRoughness, 1.0);",
        "  material.clearcoatRoughness = min(max(mix(0.46 - 0.18 * sBelly - 0.1 * sFaceK - 0.3 * sJelly, 0.03, max(max(sCoatM, sEyeM), sWetK)), 0.0525) + geometryRoughness, 1.0);")
    rep("  float amp = uDetail.x * (1.0 - 0.6 * sBelly) * (1.0 - 0.8 * faceInk) * (1.0 - sCoatM);",
        "  float amp = uDetail.x * (1.0 - 0.6 * sBelly) * (1.0 - 0.8 * faceInk) * (1.0 - sCoatM) * (1.0 - 0.85 * sJelly);")
    # the face keeps a soft light of its own on the jelly, as the slime's did
    rep("  totalEmissiveRadiance += deep * sFaceK * (1.0 - sCoatM) * (0.1 * wrap + 0.07 * back);",
        "  totalEmissiveRadiance += deep * sFaceK * (1.0 - sCoatM) * (0.1 * wrap + 0.07 * back) + diffuseColor.rgb * sFaceM * sJelly * (1.0 - ink) * (1.0 - sCoatM) * 0.1;")
s = s.replace("// Roll Model axolotl runtime v9 (v7 + the baked texture of v8 + the v9 face material and paint coat, axo/tools5/look9.py), single module:",
              "// Roll Model axolotl runtime v10" + (" B" if B else "") + " (v9b + the slime's head and ears, axo/tools6/slimehead.py and look10.py), single module:", 1)
# ---- the idle eyes (v10c, the coordinator: the glances every 1 to 2 s "read busy in the lobby"): a glance 2.5 to 6 s after the last,
# now and then a longer hold, and the eyes easing to the new spot on a critically damped spring (settled in about 0.12 s) instead of the
# snap of the old per-frame lerp; blinks and the glance-plus-blink pairing as they were ----
rep("this.look = [0, 0]; this.dart = [0, 0]; this.dartT = 0.5; this.att = { t: 1 + Math.random() * 2, eye: [0, 0] };",
    "this.look = [0, 0]; this.lookV = [0, 0]; this.dart = [0, 0]; this.dartT = 0.5; this.att = { t: 2 + Math.random() * 3, eye: [0, 0] };")
rep("const A = this.att; A.t -= dt; if (A.t <= 0) { A.t = 1.2 + Math.random() * 2.8;",
    "const A = this.att; A.t -= dt; if (A.t <= 0) { A.t = Math.random() < 0.2 ? 6 + Math.random() * 4 : 2.5 + Math.random() * 3.5;")
rep("    this.look[0] += (lx - this.look[0]) * Math.min(1, dt * 26); this.look[1] += (ly - this.look[1]) * Math.min(1, dt * 26);",
    "    { const w = 40, e = Math.exp(-w * dt);   // v10c: a critically damped ease to the new spot, settled in about 0.12 s, no snap\n"
    "      for (let i = 0; i < 2; i++) { const g = i ? ly : lx, x = this.look[i] - g, c = this.lookV[i] + w * x; this.look[i] = g + (x + c * dt) * e; this.lookV[i] = (this.lookV[i] - c * w * dt) * e; } }")
rep("if (N.holdT > 0 || Math.random() < 0.35) { N.glance = [0, 0, 0]; N.holdT = 0; N.glanceT = 1.8 + Math.random() * 3.5; }",
    "if (N.holdT > 0 || Math.random() < 0.35) { N.glance = [0, 0, 0]; N.holdT = 0; N.glanceT = Math.random() < 0.15 ? 6 + Math.random() * 4 : 2.5 + Math.random() * 3.5; }   // (v10c: rarer)")
rep("N.holdT = 1; N.glanceT = 0.7 + Math.random() * 1.6; }", "N.holdT = 1; N.glanceT = 1.0 + Math.random() * 1.6; }")
# the darts (the small saccades between glances, ±0.035 x ±0.02 every 0.35 to 1.25 s) were the busiest part: measured in the lab they moved
# the eyes to a new spot every 0.8 s, more often than the glances did. A third of their size now, so they read as a live tremor, not a move
rep("this.dart[0] = (Math.random() * 2 - 1) * 0.035; this.dart[1] = (Math.random() * 2 - 1) * 0.02; }",
    "this.dart[0] = (Math.random() * 2 - 1) * 0.012; this.dart[1] = (Math.random() * 2 - 1) * 0.007; }   // (v10c: a third of the old size)")
open(OUT, 'w').write(s); print('ok', OUT, len(s))
