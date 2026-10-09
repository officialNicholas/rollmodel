# Character v2b: a round belly that curves under before the melt, saturated jelly color (warmer, never pastel), a quieter
# puddle, bigger eyes set closer and flush with the face, a lower mouth, and blush that shows
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:100]); s = s.replace(old, new)

# profile knots (GPU and CPU copies)
old_k = ["if (i == 1) return vec2(1.035, -0.165);", "if (i == 2) return vec2(1.068, -0.322);", "if (i == 3) return vec2(1.094, -0.465);", "if (i == 4) return vec2(1.118, -0.59);", "if (i == 5) return vec2(1.185, -0.70);", "if (i == 6) return vec2(1.40, -0.762);", "if (i == 7) return vec2(1.66, -0.774);", "if (i == 8) return vec2(1.87, -0.756);", "if (i == 9) return vec2(1.95, -0.815);"]
K = [(1.045, -0.16), (1.075, -0.31), (1.082, -0.45), (1.058, -0.58), (1.012, -0.684), (1.06, -0.755), (1.30, -0.79), (1.56, -0.785), (1.70, -0.812)]
for i, (o, (r, y)) in enumerate(zip(old_k, K)):
    rep(o, f"if (i == {i + 1}) return vec2({r}, {y});")
rep("const SIT_K = [[0.988, 0.148], [1.0, 0], [1.035, -0.165], [1.068, -0.322], [1.094, -0.465], [1.118, -0.59], [1.185, -0.70], [1.40, -0.762], [1.66, -0.774], [1.87, -0.756], [1.95, -0.815], [0, -0.82], [-0.2, -0.82]];",
    "const SIT_K = [[0.988, 0.148], [1.0, 0], " + ", ".join(f"[{r}, {y}]" for r, y in K) + ", [0, -0.82], [-0.2, -0.82]];")
# a fuller, rounder head
rep("vec2 RY = vec2(r, d.y * (1.0 - 0.05 * gJelly));", "vec2 RY = vec2(r, d.y);")
rep("let R = r, Y = dy * (1 - 0.05 * J);", "let R = r, Y = dy;")

# the jelly, pass two
i = s.index('const JELLY_FS = `'); j = s.index('\n}`;', i) + 4
s = s[:i] + r'''const JELLY_FS = `
{
  vec3 jv = normalize(vViewPosition), N = normal;
  float ndv = saturate(dot(N, jv)), edge = 1.0 - ndv;
  vec3 base = diffuseColor.rgb;
  float lum = dot(base, vec3(0.3, 0.59, 0.11));
  vec3 sat = clamp(mix(vec3(lum), base, 1.2), 0.0, 1.0), deep = sat * sat * 0.85;
  vec3 glow = clamp(vec3(sat.r, sat.g + 0.22 * sat.r * (1.0 - sat.g), sat.b * 0.72) * 1.3, 0.0, 1.0);
  float pud = smoothstep(-0.72, -0.9, vGooY), low = smoothstep(0.2, -0.55, vGooY) * (1.0 - 0.55 * pud), noInk = 1.0 - faceInk;
  vec3 Lk = normalize(uRigKey), Lr = normalize(uRigRim), Hk = normalize(Lk + jv);
  float wrapK = saturate((dot(N, Lk) + 0.35) / 1.35), nh = saturate(dot(N, Hk));
  float spec = pow(nh, 260.0) * 2.4 + pow(nh, 40.0) * 0.16;
  float rim = saturate(dot(N, Lr) + 0.2) * pow(edge, 2.0) * (1.0 - 0.75 * pud);
  vec3 rig = sat * uRigKeyC * wrapK * 0.42 + deep * (1.0 - wrapK) * 0.1 + uRigKeyC * spec * (0.6 + 0.4 * noInk) + mix(glow, vec3(1.0), 0.25) * uRigRimC * rim * 0.8;
  vec3 sss = glow * (0.05 * edge * edge + 0.2 * low * (0.3 + 0.7 * wrapK) + 0.1 * pud);
  totalEmissiveRadiance += rig * uRigK * mix(0.2, 1.0, noInk) + sss * gGlow * noInk;
  reflectedLight.directDiffuse *= 0.5;
  reflectedLight.indirectDiffuse *= mix(vec3(1.0), deep / max(base, vec3(0.03)), 0.45) * 0.7;
}`;''' + s[j:]
rep("roughness: 0.16, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.5 })) : toon(c, { transparent: true });",
    "roughness: 0.2, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.15 })) : toon(c, { transparent: true });")

# eyes: bigger, closer together, a little lower, pushed into the face and flatter, the iris flattened with them
rep("const EYE_R = 0.235, eyeG", "const EYE_R = 0.255, eyeG")
rep("const pupG = shadeGeo(new THREE.SphereGeometry(0.136, 28, 20), (x, y, z) => { const c = Math.max(0, z / 0.136), low = smoothstep(0.3, -0.85, y / 0.136)",
    "const pupG = shadeGeo(new THREE.SphereGeometry(0.148, 28, 20), (x, y, z) => { const c = Math.max(0, z / 0.148), low = smoothstep(0.3, -0.85, y / 0.148)")
rep("const pupilG = new THREE.SphereGeometry(0.08, 18, 14), shineG = new THREE.SphereGeometry(0.056, 14, 10), shine2G = new THREE.SphereGeometry(0.027, 10, 8);",
    "const pupilG = new THREE.SphereGeometry(0.087, 18, 14), shineG = new THREE.SphereGeometry(0.061, 14, 10), shine2G = new THREE.SphereGeometry(0.029, 10, 8);")
rep("pl.position.set(0, 0.006, 0.074);", "pl.position.set(0, 0.006, 0.08);")
rep("sh.position.set(0.052, 0.058, 0.118);", "sh.position.set(0.057, 0.063, 0.128);")
rep("sh2.position.set(-0.056, -0.05, 0.114);", "sh2.position.set(-0.061, -0.054, 0.124);")
rep("const EYE_BASE = sd => new THREE.Vector3(sd * 0.4, 0.36, 0.84).normalize();", "const EYE_BASE = sd => new THREE.Vector3(sd * 0.34, 0.31, 0.88).normalize();")
rep("const FACE = { eyeX: 0.402, eyeY: 0.362, mouthTop: -0.015, cell: 0.32 };", "const FACE = { eyeX: 0.342, eyeY: 0.312, mouthTop: -0.05, cell: 0.34 };")
rep("const mouthBase = new THREE.Vector3(0, -0.01, 1).normalize();", "const mouthBase = new THREE.Vector3(0, -0.05, 1).normalize();")
rep("it.e.position.copy(p).multiplyScalar(1.02)", "it.e.position.copy(p).multiplyScalar(0.995)", count=3)
rep("it.pu.position.copy(p).multiplyScalar(1.07)", "it.pu.position.copy(p).multiplyScalar(1.035)", count=3)
rep("it.e.scale.set(s, sy * s, 0.55);", "it.e.scale.set(s, sy * s, 0.45);")
rep("it.e.scale.set(1, sy, 0.55);", "it.e.scale.set(1, sy, 0.45);", count=2)
rep("it.pu.scale.setScalar((scared ? 0.72 : strain ? 0.85 : 1) * (ES === 'googly' ? 0.62 : cyc ? 1.4 : ES === 'sleepy' ? 0.85 : 1));",
    "{ const k = (scared ? 0.72 : strain ? 0.85 : 1) * (ES === 'googly' ? 0.62 : cyc ? 1.4 : ES === 'sleepy' ? 0.85 : 1); it.pu.scale.set(k, k, k * 0.62); }")
rep("it.pu.scale.setScalar(scared ? 0.7 : 1);", "{ const k = scared ? 0.7 : 1; it.pu.scale.set(k, k, k * 0.62); }", count=2)

# blush that reads: rosier, a touch lower and further out, glowing a little
rep("vec2 e = (vSph.xy - vec2(sd * uFace2.z * 1.22, uFace2.w - 0.31)) * vec2(1.0, 1.55); float b = smoothstep(0.17, 0.02, length(e)) * uFace2.y * fk; diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0, 0.56, 0.68), b * 0.62); totalEmissiveRadiance += vec3(1.0, 0.5, 0.62) * b * 0.16;",
    "vec2 e = (vSph.xy - vec2(sd * uFace2.z * 1.32, uFace2.w - 0.33)) * vec2(1.0, 1.5); float b = smoothstep(0.16, 0.02, length(e)) * uFace2.y * fk; diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0, 0.5, 0.6), b * 0.78); totalEmissiveRadiance += vec3(1.0, 0.42, 0.55) * b * 0.32; faceInk = max(faceInk, b * 0.6);")
open(p, 'w').write(s)
print('ok')
