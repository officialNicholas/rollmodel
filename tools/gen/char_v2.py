# Character v2: one continuous jelly body that melts into a beaded puddle, its own camera-relative light rig with
# subsurface glow, glossy eyes without the heavy outline, a cavity mouth, and framing that fits the whole blob.
import re
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

def rep_block(start, end_marker, new):
    """replace from `start` through the first `end_marker` after it"""
    global s
    i = s.index(start); assert s.count(start) == 1, start[:60]
    j = s.index(end_marker, i) + len(end_marker)
    s = s[:i] + new + s[j:]

# ---------- 1. the shape ----------
GOO = r'''const GOO_GLSL = `
uniform float gT, gWob, gSpd, gLean, gSquash, gRise, gDrop, gFlat, gRoll, gJelly, gPud;
// the resting shape, as a profile turned round the body. On top, a full round dome. Below the middle (t: 0 at the middle,
// 1 at the bottom) a belly that swells low and then, sitting on the floor, the jelly melting out into its own puddle with
// a fat rounded rim that wobbles as it settles. In the air (gPud 0) it gathers back up into a ball
vec2 crm(vec2 a, vec2 b, vec2 c, vec2 d, float u){ float u2 = u * u; return 0.5 * (2.0 * b + (c - a) * u + (2.0 * a - 5.0 * b + 4.0 * c - d) * u2 + (3.0 * b - a - 3.0 * c + d) * u2 * u); }
vec2 sitK(int i){
  if (i < 0) return vec2(0.988, 0.148);
  if (i == 0) return vec2(1.0, 0.0);
  if (i == 1) return vec2(1.035, -0.165);
  if (i == 2) return vec2(1.068, -0.322);
  if (i == 3) return vec2(1.094, -0.465);
  if (i == 4) return vec2(1.118, -0.59);
  if (i == 5) return vec2(1.185, -0.70);
  if (i == 6) return vec2(1.40, -0.762);
  if (i == 7) return vec2(1.66, -0.774);
  if (i == 8) return vec2(1.87, -0.756);
  if (i == 9) return vec2(1.95, -0.815);
  if (i == 10) return vec2(0.0, -0.82);
  return vec2(-0.2, -0.82);
}
vec2 sitProfile(float t){ float x = clamp(t, 0.0, 0.9999) * 10.0, i = floor(x); int k = int(i); return crm(sitK(k - 1), sitK(k), sitK(k + 1), sitK(k + 2), x - i); }
vec3 jellyShape(vec3 p){
  float rho = length(p); vec3 d = p / max(rho, 1e-5);
  float r = length(d.xz), a = atan(d.z, d.x); vec2 h = r > 1e-5 ? d.xz / r : vec2(0.0, 1.0);
  vec2 RY = vec2(r, d.y * (1.0 - 0.05 * gJelly));
  if (d.y < 0.0) {
    float t = asin(min(-d.y, 1.0)) / 1.5708;
    vec2 air = vec2(cos(t * 1.5708) * (1.0 + 0.06 * sin(t * 3.1416)), -sin(t * 1.5708) * 0.9);
    vec2 sit = sitProfile(t);
    float lob = 0.03 * (sin(a * 3.0 + 0.7) + 0.7 * sin(a * 5.0 + 2.3));
    float wv = 0.07 * sin(a * 3.0 + gT * 1.1) + 0.045 * sin(a * 5.0 - gT * 1.7 + 1.3) + 0.025 * sin(a * 9.0 + gT * 2.3);
    sit.x *= 1.0 + lob * smoothstep(0.05, 0.55, t) + (wv + lob) * smoothstep(0.5, 0.85, t);
    RY = mix(RY, mix(air, sit, gPud), gJelly);
  }
  return vec3(h.x * RY.x, RY.y, h.y * RY.x) * rho;
}
vec3 goo(vec3 p){
  p = jellyShape(p);
  float G = 0.82 * gFlat; // on the floor, the wobble and squash pivot on it, so the puddle stays put
  float ax = abs(p.x);
  p.x = sign(p.x) * mix(ax, pow(ax, 0.42), gRoll) * (1.0 + 1.25 * gRoll); p.y *= 1.0 - 0.1 * gRoll; p.z *= 1.0 - 0.06 * gRoll;
  float wk = 0.06 * gWob * (sin(p.x * 3.1 + gT * 5.3) * sin(p.y * 2.7 + gT * 4.1) + 0.6 * sin(p.z * 3.7 - gT * 6.2 + p.y * 1.3));
  p.xz *= 1.0 + wk; p.y = (p.y + G) * (1.0 + wk) - G;
  p.z *= 1.0 + 0.16 * gSpd; p.y = (p.y + G) * (1.0 - 0.07 * gSpd) - G;
  p.z -= 0.14 * gSpd * (1.0 - smoothstep(-1.0, 0.2, p.y));
  p.x += gLean * 0.16 * (p.y + 1.0);
  p.y = mix(p.y, max(p.y, -0.82), gFlat);
  p.y = (p.y + G) * (1.0 - 0.38 * gSquash + 0.24 * gRise) - G; p.xz *= 1.0 + 0.3 * gSquash - 0.1 * gRise;
  float up = smoothstep(-0.2, 1.0, p.y);
  p.xz *= 1.0 - gDrop * 0.84 * up * up;
  p.y += gDrop * 0.9 * up * up * up;
  return p;
}
vec3 gooN(vec3 p, vec3 n){
  vec3 t1 = normalize(abs(n.y) < 0.95 ? cross(n, vec3(0.0, 1.0, 0.0)) : cross(n, vec3(1.0, 0.0, 0.0)));
  vec3 t2 = cross(n, t1);
  vec3 a = goo(p), b = goo(p + t1 * 0.02), c = goo(p + t2 * 0.02);
  vec3 m = normalize(cross(b - a, c - a));
  return dot(m, n) < 0.0 ? -m : m;
}`;'''
rep_block('const GOO_GLSL = `', '\n}`;', GOO)
rep("const gooU = { gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } };",
    "const gooU = { gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 }, gPud: { value: 1 } };")
rep("gDrop: { value: 0 }, gFlat: { value: 1 } }, faceU());", "gDrop: { value: 0 }, gFlat: { value: 1 }, gPud: { value: 1 } }, faceU());", count=2)

GOOJS = r'''// the same profile on the CPU (knot k sits at SIT_K[k + 1]), so eyes, mouth and accessories ride the surface
const SIT_K = [[0.988, 0.148], [1.0, 0], [1.035, -0.165], [1.068, -0.322], [1.094, -0.465], [1.118, -0.59], [1.185, -0.70], [1.40, -0.762], [1.66, -0.774], [1.87, -0.756], [1.95, -0.815], [0, -0.82], [-0.2, -0.82]];
function sitProfileJS(t) { const x = clamp(t, 0, 0.9999) * 10, i = Math.floor(x), u = x - i, u2 = u * u, A = SIT_K[i], B = SIT_K[i + 1], C = SIT_K[i + 2], D = SIT_K[i + 3], f = (a, b, c, d) => 0.5 * (2 * b + (c - a) * u + (2 * a - 5 * b + 4 * c - d) * u2 + (3 * b - a - 3 * c + d) * u2 * u); return [f(A[0], B[0], C[0], D[0]), f(A[1], B[1], C[1], D[1])]; }
function gooJS(v, U) {
  U = U || gooU; const g = k => U[k].value, p = v.clone(), J = JELLY.value;
  { const rho = p.length() || 1e-5, dx = p.x / rho, dy = p.y / rho, dz = p.z / rho, r = Math.hypot(dx, dz), a = Math.atan2(dz, dx), hx = r > 1e-5 ? dx / r : 0, hz = r > 1e-5 ? dz / r : 1;
    let R = r, Y = dy * (1 - 0.05 * J);
    if (dy < 0) {
      const t = Math.asin(Math.min(-dy, 1)) / 1.5708, ar = Math.cos(t * 1.5708) * (1 + 0.06 * Math.sin(t * 3.1416)), ay = -Math.sin(t * 1.5708) * 0.9, sit = sitProfileJS(t), gt = g('gT');
      const lob = 0.03 * (Math.sin(a * 3 + 0.7) + 0.7 * Math.sin(a * 5 + 2.3)), wv = 0.07 * Math.sin(a * 3 + gt * 1.1) + 0.045 * Math.sin(a * 5 - gt * 1.7 + 1.3) + 0.025 * Math.sin(a * 9 + gt * 2.3);
      sit[0] *= 1 + lob * smoothstep(0.05, 0.55, t) + (wv + lob) * smoothstep(0.5, 0.85, t);
      const pud = g('gPud'), mR = ar + (sit[0] - ar) * pud, mY = ay + (sit[1] - ay) * pud; R += (mR - R) * J; Y += (mY - Y) * J;
    }
    p.set(hx * R * rho, Y * rho, hz * R * rho); }
  const G = 0.82 * g('gFlat');
  const ax = Math.abs(p.x); p.x = Math.sign(p.x) * (ax + (Math.pow(ax, 0.42) - ax) * g('gRoll')) * (1 + 1.25 * g('gRoll')); p.y *= 1 - 0.1 * g('gRoll'); p.z *= 1 - 0.06 * g('gRoll');
  { const t = g('gT'), wk = 0.06 * g('gWob') * (Math.sin(p.x * 3.1 + t * 5.3) * Math.sin(p.y * 2.7 + t * 4.1) + 0.6 * Math.sin(p.z * 3.7 - t * 6.2 + p.y * 1.3)); p.x *= 1 + wk; p.z *= 1 + wk; p.y = (p.y + G) * (1 + wk) - G; } // the same wobble as the shader, so the face rides the surface
  p.z *= 1 + 0.16 * g('gSpd'); p.y = (p.y + G) * (1 - 0.07 * g('gSpd')) - G;
  p.z -= 0.14 * g('gSpd') * (1 - smoothstep(-1, 0.2, p.y));
  p.x += g('gLean') * 0.16 * (p.y + 1);
  p.y += (Math.max(p.y, -0.82) - p.y) * g('gFlat');
  p.y = (p.y + G) * (1 - 0.38 * g('gSquash') + 0.24 * g('gRise')) - G; const sxz = 1 + 0.3 * g('gSquash') - 0.1 * g('gRise'); p.x *= sxz; p.z *= sxz;
  const t = clamp((p.y + 0.2) / 1.2, 0, 1), up = t * t * (3 - 2 * t);
  const pin = 1 - g('gDrop') * 0.84 * up * up; p.x *= pin; p.z *= pin; p.y += g('gDrop') * 0.9 * up * up * up;
  return p;
}'''
rep_block('function gooJS(v, U) {', '\n  return p;\n}', GOOJS)
rep("const blobG = HI ? new THREE.SphereGeometry(1, 80, 56) : new THREE.SphereGeometry(1, 40, 28);",
    "const blobG = HI ? new THREE.SphereGeometry(1, 96, 72) : new THREE.SphereGeometry(1, 48, 40);")

# ---------- 2. the jelly: a light rig of its own, subsurface glow, saturated shade ----------
JELLY = r'''// Graphics mode jelly. The scene's own light is often a dim moon, so every blob also carries a light rig that moves with the
// camera, the way a film lights its characters: a warm soft key from up and to the left, a hot highlight in it, and a bright
// rim from behind. Inside, light soaks through: it comes out softened and brighter at the thin edges and low down where the
// jelly melts out, and the shade side stays a deep, saturated color instead of going grey
const RIG = { uRigK: { value: 1 }, uRigKey: { value: new THREE.Vector3(-0.5, 0.62, 0.6).normalize() }, uRigKeyC: { value: new THREE.Color(1.0, 0.94, 0.84) }, uRigRim: { value: new THREE.Vector3(0.72, 0.42, -0.55).normalize() }, uRigRimC: { value: new THREE.Color(1.0, 0.92, 0.8) } };
const JELLY_FS = `
{
  vec3 jv = normalize(vViewPosition), N = normal;
  float ndv = saturate(dot(N, jv)), edge = 1.0 - ndv;
  vec3 base = diffuseColor.rgb;
  vec3 deep = base * base * 0.9 + base * 0.035;
  vec3 glow = clamp(base * 1.45 + vec3(0.04, 0.1 * base.r, 0.06 * base.b), 0.0, 1.0);
  float low = smoothstep(0.15, -0.8, vGooY), noInk = 1.0 - faceInk;
  vec3 Lk = normalize(uRigKey), Lr = normalize(uRigRim), Hk = normalize(Lk + jv);
  float wrapK = saturate((dot(N, Lk) + 0.42) / 1.42), nh = saturate(dot(N, Hk));
  float spec = pow(nh, 240.0) * 2.6 + pow(nh, 34.0) * 0.2;
  float rim = saturate(dot(N, Lr) + 0.25) * pow(edge, 1.7);
  vec3 rig = glow * uRigKeyC * wrapK * 0.5 + deep * (1.0 - wrapK) * 0.14 + uRigKeyC * spec + mix(glow, vec3(1.0), 0.45) * uRigRimC * rim * 0.95;
  vec3 sss = glow * (0.06 * edge * edge + 0.17 * low * (0.35 + 0.65 * wrapK));
  totalEmissiveRadiance += (rig * uRigK * mix(0.25, 1.0, noInk) + sss * gGlow * noInk);
  reflectedLight.directDiffuse *= 0.62;
  reflectedLight.indirectDiffuse *= mix(vec3(1.0), deep / max(base, vec3(0.03)), 0.4) * 0.8;
}`;'''
rep_block('// Graphics mode jelly: light soaks through thin edges and the base', '\n}`;', JELLY)
rep("if (jelly) { vs = vs.replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\\nvGooW = (modelMatrix * vec4(transformed, 1.0)).xyz;'); sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uLitMap = aoU.uLitMap; sh.uniforms.uAORect = aoU.uAORect; }",
    "if (jelly) { vs = vs.replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\\nvGooW = (modelMatrix * vec4(transformed, 1.0)).xyz;'); sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uLitMap = aoU.uLitMap; sh.uniforms.uAORect = aoU.uAORect; Object.assign(sh.uniforms, RIG); }")
rep("varying float vGooY; varying vec3 vGooW; uniform float gGlow;\\n' + AO_GLSL)",
    "varying float vGooY; varying vec3 vGooW; uniform float gGlow, uRigK; uniform vec3 uRigKey, uRigKeyC, uRigRim, uRigRimC;\\n' + AO_GLSL)")
# the body is one piece now: a clearer, glossier coat
rep("const blobMat = c => HI ? charMat(new THREE.MeshPhysicalMaterial({ color: c, transparent: true, roughness: 0.22, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 1.25 })) : toon(c, { transparent: true });",
    "const blobMat = c => HI ? charMat(new THREE.MeshPhysicalMaterial({ color: c, transparent: true, roughness: 0.16, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.5 })) : toon(c, { transparent: true });")

# ---------- 3. eyes: no heavy outline, a soft lid shade, a deep iris with a dark ring, bigger catchlights ----------
rep("const EYE_R = 0.235, eyeG = shadeGeo(new THREE.SphereGeometry(EYE_R, 28, 20), (x, y, z) => { const k = 1 - 0.2 * smoothstep(0.2, 0.95, y / EYE_R) - 0.05 * (1 - Math.max(0, z / EYE_R)); return [k * 0.97, k * 0.96, k]; });",
    "const EYE_R = 0.235, eyeG = shadeGeo(new THREE.SphereGeometry(EYE_R, 36, 26), (x, y, z) => { const lid = smoothstep(0.12, 0.98, y / EYE_R), edge = Math.pow(1 - Math.max(0, z / EYE_R), 1.6), sh = Math.min(1, 0.5 * lid + 0.42 * edge); return [1 - sh * 0.3, 1 - sh * 0.28, 1 - sh * 0.15]; });")
rep("const pupG = shadeGeo(new THREE.SphereGeometry(0.128, 22, 16), (x, y) => { const t = smoothstep(0.75, -0.9, y / 0.128); return [0.2 + 0.4 * t, 0.035 + 0.12 * t, 0.06 + 0.1 * t]; });",
    "const pupG = shadeGeo(new THREE.SphereGeometry(0.136, 28, 20), (x, y, z) => { const c = Math.max(0, z / 0.136), low = smoothstep(0.3, -0.85, y / 0.136), limb = smoothstep(0.62, 0.2, c), k = 1 - 0.84 * limb; return [(0.34 + 0.36 * low) * k + 0.03 * limb, (0.09 + 0.14 * low) * k + 0.01 * limb, (0.08 + 0.09 * low) * k + 0.015 * limb]; });")
rep("const pupilG = new THREE.SphereGeometry(0.072, 16, 12), shineG = new THREE.SphereGeometry(0.047, 10, 8), shine2G = new THREE.SphereGeometry(0.023, 8, 6);",
    "const pupilG = new THREE.SphereGeometry(0.08, 18, 14), shineG = new THREE.SphereGeometry(0.056, 14, 10), shine2G = new THREE.SphereGeometry(0.027, 10, 8);")
rep("const rim = new THREE.Mesh(eyeG, eyeRimM); rim.scale.setScalar(1.11); rim.renderOrder = 32.5; e.add(rim);",
    "const rim = new THREE.Mesh(eyeG, eyeRimM); rim.scale.setScalar(1.04); rim.renderOrder = 32.5; e.add(rim);")
rep("const pl = new THREE.Mesh(pupilG, pupilM); pl.renderOrder = 34.5; pl.position.set(0, 0.008, 0.074); pu.add(pl);",
    "const pl = new THREE.Mesh(pupilG, pupilM); pl.renderOrder = 34.5; pl.position.set(0, 0.006, 0.074); pu.add(pl);")
rep("const sh = new THREE.Mesh(shineG, shineM); sh.renderOrder = 35; sh.position.set(0.048, 0.052, 0.11); pu.add(sh);",
    "const sh = new THREE.Mesh(shineG, shineM); sh.renderOrder = 35; sh.position.set(0.052, 0.058, 0.118); pu.add(sh);")
rep("const sh2 = new THREE.Mesh(shine2G, shineM); sh2.renderOrder = 35; sh2.position.set(-0.05, -0.046, 0.106); pu.add(sh2);",
    "const sh2 = new THREE.Mesh(shine2G, shineM); sh2.renderOrder = 35; sh2.position.set(-0.056, -0.05, 0.114); pu.add(sh2);")
rep("eyeRimM = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true })",
    "eyeRimM = new THREE.MeshBasicMaterial({ color: 0x24101A, side: THREE.BackSide, transparent: true })")

# ---------- 4. the mouth sheet: a soft cavity, no heavy rim, a glossy tongue, drawn at twice the size ----------
FACE = r'''const faceTex = (() => {
  const S = 1024, C2 = S / 2, cv = document.createElement('canvas'); cv.width = cv.height = S; const g = cv.getContext('2d');
  const cell = (c, fn) => { g.save(); g.translate((c % 2) * C2 + C2 / 2, (c < 2 ? C2 * 1.5 : C2 / 2)); g.scale(C2 * 0.46, -C2 * 0.46); g.lineJoin = 'round'; g.lineCap = 'round'; fn(); g.restore(); };
  const dPath = (w, top, h, dip) => { g.beginPath(); g.moveTo(-w, top); g.quadraticCurveTo(0, top - dip, w, top); for (let k = 1; k <= 40; k++) { const t = k / 40 * Math.PI; g.lineTo(w * Math.cos(t), top - h * Math.sin(t)); } g.closePath(); };
  // inside: deep at the top under the lip, warmer toward the bottom; a tongue with a soft shine; a thin soft edge and a lit lower lip
  const cavity = (path, top, bot, tongue) => {
    path(); const gr = g.createLinearGradient(0, top, 0, bot); gr.addColorStop(0, '#2A0410'); gr.addColorStop(0.55, '#5A0C1E'); gr.addColorStop(1, '#7E1A2C'); g.fillStyle = gr; g.fill();
    g.save(); path(); g.clip();
    if (tongue) { const [tx, ty, tw, th] = tongue, tg = g.createRadialGradient(tx - tw * 0.2, ty + th * 0.35, 0, tx, ty, tw * 1.1); tg.addColorStop(0, '#FF9DB0'); tg.addColorStop(0.6, '#F0607E'); tg.addColorStop(1, '#C23A58'); g.fillStyle = tg; g.beginPath(); g.ellipse(tx, ty, tw, th, 0, 0, Math.PI * 2); g.fill();
      g.strokeStyle = 'rgba(150,30,60,0.55)'; g.lineWidth = 0.03; g.beginPath(); g.moveTo(tx, ty + th * 0.7); g.lineTo(tx, ty + th * 0.05); g.stroke();
      g.fillStyle = 'rgba(255,215,225,0.55)'; g.beginPath(); g.ellipse(tx - tw * 0.32, ty + th * 0.42, tw * 0.22, th * 0.14, -0.3, 0, Math.PI * 2); g.fill(); }
    const sh = g.createLinearGradient(0, top, 0, top - (top - bot) * 0.4); sh.addColorStop(0, 'rgba(10,0,4,0.75)'); sh.addColorStop(1, 'rgba(10,0,4,0)'); g.fillStyle = sh; g.fillRect(-2, bot, 4, top - bot + 0.2);
    g.restore();
    path(); g.strokeStyle = 'rgba(40,4,14,0.55)'; g.lineWidth = 0.035; g.stroke();
  };
  const smile = (w, top, h, dip, tg) => { cavity(() => dPath(w, top, h, dip), top, top - h, [0, top - h * 0.86, w * tg, h * 0.42]);
    g.strokeStyle = 'rgba(255,235,235,0.28)'; g.lineWidth = 0.04; g.beginPath(); for (let k = 6; k <= 34; k++) { const t = k / 40 * Math.PI, x = w * 1.03 * Math.cos(t), y = top - h * 1.06 * Math.sin(t); k === 6 ? g.moveTo(x, y) : g.lineTo(x, y); } g.stroke(); };
  cell(0, () => smile(0.66, 0.44, 0.66, 0.12, 0.6));
  cell(1, () => smile(0.84, 0.54, 0.9, 0.16, 0.58));
  cell(2, () => cavity(() => { g.beginPath(); g.ellipse(0, 0.0, 0.34, 0.42, 0, 0, Math.PI * 2); }, 0.42, -0.42, [0, -0.36, 0.25, 0.2]));
  cell(3, () => smile(0.52, 0.38, 0.44, 0.1, 0.55));
  const t = new THREE.CanvasTexture(cv); t.anisotropy = 8; return t;
})();'''
rep_block('const faceTex = (() => {', '\n})();', FACE)

# blush: a little lower and closer in than before, so it reads from the front; a soft shade round each eye socket
rep("for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 e = (vSph.xy - vec2(sd * uFace2.z * 1.5, uFace2.w - 0.24)) * vec2(1.0, 1.7); float b = smoothstep(0.18, 0.03, length(e)) * uFace2.y * fk; diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0, 0.6, 0.74), b * 0.75); totalEmissiveRadiance += vec3(1.0, 0.45, 0.6) * b * 0.12; }",
    "for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 e = (vSph.xy - vec2(sd * uFace2.z * 1.22, uFace2.w - 0.31)) * vec2(1.0, 1.55); float b = smoothstep(0.17, 0.02, length(e)) * uFace2.y * fk; diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0, 0.56, 0.68), b * 0.62); totalEmissiveRadiance += vec3(1.0, 0.5, 0.62) * b * 0.16;\n    vec2 o = (vSph.xy - vec2(sd * uFace2.z, uFace2.w)) * vec2(1.0, 0.86); float so = smoothstep(0.34, 0.25, length(o)) * smoothstep(0.2, 0.26, length(o)) * fk * (1.0 - uFace2.x); diffuseColor.rgb *= 1.0 - 0.2 * so; }")

# ---------- 5. the separate puddle goes: the body melts out into its own. It still decides how much puddle there is ----------
rep("    const on = V.root.visible && !hidden && D.st !== 'ko' && gy > -Infinity, want = on ? clamp(1 - (D.y - gy) * 1.6, 0, 1) * L.flat : 0;",
    "    const on = V.root.visible && !hidden && D.st !== 'ko' && gy > -Infinity, want = on ? clamp(1 - (D.y - gy) * 1.6, 0, 1) * L.flat * clamp(1 - hop * 7, 0, 1) : 0;")
rep("    const pk = pd.userData.k * isc; pd.visible = pk > 0.04;\n    if (pd.visible) {",
    "    const pk = pd.userData.k * isc; U.gPud.value = pd.userData.k; pd.visible = false;\n    if (pk > 0.04) {")
# the menu idle: a jelly bounce in place (stretch and squash on the floor) instead of a hop, so the puddle stays put
rep("hop = ph < 0.3 ? Math.sin(ph / 0.3 * Math.PI) * 0.16 : 0; rise = ph < 0.15 ? 0.5 : 0;",
    "hop = 0; rise = ph < 0.3 ? Math.sin(ph / 0.3 * Math.PI) * 0.55 : 0;")
# the drip-in landing makes a smaller splat, so the floor under it isn't one big pancake
rep("addSplat(P.x, P.y, P.z, P.yaw, 1.05, -8, false, false, 0);", "addSplat(P.x, P.y, P.z, P.yaw, 0.72, -8, false, false, 0);")

open(p, 'w').write(s)
print('ok')
