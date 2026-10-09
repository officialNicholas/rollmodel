# The jelly characters: gumdrop body, melting puddle, subsurface glow, studio highlights, new eyes, open smile, blush, glossy wear
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:100], c)
    s = s.replace(a, b)

# ---------- shape: the goo starts from a gumdrop instead of a ball ----------
rep("""const GOO_GLSL = `
uniform float gT, gWob, gSpd, gLean, gSquash, gRise, gDrop, gFlat, gRoll;
vec3 goo(vec3 p){
  float ax = abs(p.x);""", """const GOO_GLSL = `
uniform float gT, gWob, gSpd, gLean, gSquash, gRise, gDrop, gFlat, gRoll, gJelly;
// the resting shape: a lower, rounder dome over a body that swells out toward its base, with soft lobes where it settles
vec3 jellyShape(vec3 p){
  float lo = smoothstep(0.45, -0.95, p.y), a = atan(p.z, p.x);
  p.xz *= 1.0 + gJelly * (0.1 * lo + 0.06 * lo * lo + 0.028 * lo * (sin(a * 3.0 + 0.7) + 0.7 * sin(a * 5.0 + 2.3)));
  p.y *= 1.0 - gJelly * (p.y > 0.0 ? 0.12 : 0.04);
  return p;
}
vec3 goo(vec3 p){
  p = jellyShape(p);
  float ax = abs(p.x);""")
rep("""const gooU = { gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } };
function gooify(mat, outline, key, U) {
  U = U || gooU;
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, U);
    let vs = GOO_GLSL + '\\n' + sh.vertexShader;
    if (outline) vs = vs.replace('#include <begin_vertex>', 'vec3 transformed = goo(position) + gooN(position, normal) * 0.12;');
    else vs = vs.replace('#include <beginnormal_vertex>', 'vec3 objectNormal = gooN(position, normal);').replace('#include <begin_vertex>', 'vec3 transformed = goo(position);');
    sh.vertexShader = vs;
  };
  mat.customProgramCacheKey = () => key || (outline ? 'goo-outline' : 'goo-body');
  return mat;
}
function gooJS(v, U) {
  U = U || gooU; const g = k => U[k].value, p = v.clone();
  const ax""", """const gooU = { gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } };
// every blob shares these: the gumdrop shape, and (Graphics mode) how strongly light glows through the jelly
const JELLY = { value: 1 }, JGLOW = { value: 1 };
// Graphics mode jelly: light soaks through thin edges and the base (a saturated inner glow), a soft bright rim, deeper color in the middle
const JELLY_FS = `
{
  vec3 jv = normalize(vViewPosition); float ndv = saturate(dot(normal, jv)), edge = 1.0 - ndv;
  vec3 base = diffuseColor.rgb, hot = base * (1.12 + 0.55 * base);
  float low = smoothstep(0.2, -0.86, vGooY), key = 0.6, thru = 0.0;
  #if NUM_DIR_LIGHTS > 0
  key = saturate(dot(normal, directionalLights[0].direction) * 0.5 + 0.5);
  thru = pow(saturate(dot(-jv, directionalLights[0].direction)), 2.0);
  #endif
  totalEmissiveRadiance += hot * (0.16 * edge * edge + 0.3 * low * (0.35 + 0.65 * key) + 0.22 * thru * (0.3 + edge)) * gGlow;
  totalEmissiveRadiance += mix(hot, vec3(1.0), 0.35) * pow(edge, 3.2) * 0.5 * gGlow;
  reflectedLight.directDiffuse *= mix(vec3(1.0), base * 1.25, 0.16 * ndv);
}`;
function gooify(mat, outline, key, U) {
  U = U || gooU;
  const jelly = !outline && mat.isMeshPhysicalMaterial;
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, U); sh.uniforms.gJelly = JELLY; sh.uniforms.gGlow = JGLOW;
    let vs = GOO_GLSL + '\\nvarying float vGooY;\\n' + sh.vertexShader;
    if (outline) vs = vs.replace('#include <begin_vertex>', 'vec3 transformed = goo(position) + gooN(position, normal) * 0.12; vGooY = position.y;');
    else vs = vs.replace('#include <beginnormal_vertex>', 'vec3 objectNormal = gooN(position, normal);').replace('#include <begin_vertex>', 'vec3 transformed = goo(position); vGooY = position.y;');
    sh.vertexShader = vs;
    if (jelly) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\nvarying float vGooY; uniform float gGlow;').replace('#include <aomap_fragment>', '#include <aomap_fragment>' + JELLY_FS);
  };
  mat.customProgramCacheKey = () => (key || (outline ? 'goo-outline' : 'goo-body')) + (jelly ? '-jelly' : '');
  return mat;
}
function gooJS(v, U) {
  U = U || gooU; const g = k => U[k].value, p = v.clone();
  { const lo = smoothstep(0.45, -0.95, p.y), a = Math.atan2(p.z, p.x), J = JELLY.value; const k = 1 + J * (0.1 * lo + 0.06 * lo * lo + 0.028 * lo * (Math.sin(a * 3 + 0.7) + 0.7 * Math.sin(a * 5 + 2.3))); p.x *= k; p.z *= k; p.y *= 1 - J * (p.y > 0 ? 0.12 : 0.04); }
  const ax""")

# ---------- the body material ----------
rep("""const blobMat = c => HI ? new THREE.MeshPhysicalMaterial({ color: c, transparent: true, roughness: 0.34, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.08, envMapIntensity: 1.1 }) : toon(c, { transparent: true });""",
"""// the jelly and everything glossy on a character get a studio light map (soft boxes over the theme's sky) for their highlights
const CHAR_MATS = [];
const charMat = m => { if (m.isMeshStandardMaterial) CHAR_MATS.push(m); return m; };
const blobMat = c => HI ? charMat(new THREE.MeshPhysicalMaterial({ color: c, transparent: true, roughness: 0.22, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.05, envMapIntensity: 1.25 })) : toon(c, { transparent: true });
const glossMat = (c, extra) => HI ? charMat(new THREE.MeshPhysicalMaterial(Object.assign({ color: c, roughness: 0.32, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.08, envMapIntensity: 1.1 }, extra || {}))) : toon(c, extra);""")
rep("""const dropHull = new THREE.Mesh(blobG, gooify(new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), true)); dropHull.renderOrder = 31; body.add(dropHull);""",
    """const dropHull = new THREE.Mesh(blobG, gooify(new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), true)); dropHull.renderOrder = 31; dropHull.visible = !HI; body.add(dropHull);""")

# ---------- eyes ----------
rep("""const eyeW = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true }), eyeB = new THREE.MeshBasicMaterial({ color: C.outline, transparent: true }), shineM = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true }), eyeRimM = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), eyes = [];
const eyeG = new THREE.SphereGeometry(0.215, 20, 14), pupG = new THREE.SphereGeometry(0.118, 14, 10), shineG = new THREE.SphereGeometry(0.044, 8, 6), shine2G = new THREE.SphereGeometry(0.022, 8, 6);
function makeEye(parent) {
  const e = new THREE.Mesh(eyeG, eyeW); e.renderOrder = 33; parent.add(e);
  const rim = new THREE.Mesh(eyeG, eyeRimM); rim.scale.setScalar(1.17); rim.renderOrder = 32.5; e.add(rim);
  const pu = new THREE.Mesh(pupG, eyeB); pu.renderOrder = 34; parent.add(pu);
  const sh = new THREE.Mesh(shineG, shineM); sh.renderOrder = 35; sh.position.set(0.042, 0.046, 0.1); pu.add(sh);
  const sh2 = new THREE.Mesh(shine2G, shineM); sh2.renderOrder = 35; sh2.position.set(-0.046, -0.042, 0.1); pu.add(sh2);
  return { e, pu };
}
[-1, 1].forEach(sd => { const { e, pu } = makeEye(body); eyes.push({ e, pu, base: new THREE.Vector3(sd * 0.37, 0.45, 0.8).normalize() }); });""",
"""// big glossy eyes: a white ball with a soft shade under the lid and a thin dark rim, a deep warm iris, a black pupil and two catchlights
const shadeGeo = (g, fn) => { const P = g.attributes.position, c = new Float32Array(P.count * 3); for (let i = 0; i < P.count; i++) { const k = fn(P.getX(i), P.getY(i), P.getZ(i)); c[i * 3] = k[0]; c[i * 3 + 1] = k[1]; c[i * 3 + 2] = k[2]; } g.setAttribute('color', new THREE.BufferAttribute(c, 3)); return g; };
const eyeW = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, vertexColors: true }), eyeB = new THREE.MeshBasicMaterial({ color: C.outline, transparent: true }), shineM = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true }), eyeRimM = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), eyes = [];
const irisM = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, vertexColors: true }), pupilM = new THREE.MeshBasicMaterial({ color: 0x0B0407, transparent: true });
const EYE_R = 0.235, eyeG = shadeGeo(new THREE.SphereGeometry(EYE_R, 28, 20), (x, y, z) => { const k = 1 - 0.2 * smoothstep(0.2, 0.95, y / EYE_R) - 0.05 * (1 - Math.max(0, z / EYE_R)); return [k * 0.97, k * 0.96, k]; });
const pupG = shadeGeo(new THREE.SphereGeometry(0.128, 22, 16), (x, y) => { const t = smoothstep(0.75, -0.9, y / 0.128); return [0.2 + 0.4 * t, 0.035 + 0.12 * t, 0.06 + 0.1 * t]; });
const pupilG = new THREE.SphereGeometry(0.072, 16, 12), shineG = new THREE.SphereGeometry(0.047, 10, 8), shine2G = new THREE.SphereGeometry(0.023, 8, 6);
function makeEye(parent) {
  const e = new THREE.Mesh(eyeG, eyeW); e.renderOrder = 33; parent.add(e);
  const rim = new THREE.Mesh(eyeG, eyeRimM); rim.scale.setScalar(1.11); rim.renderOrder = 32.5; e.add(rim);
  const pu = new THREE.Mesh(pupG, irisM); pu.renderOrder = 34; parent.add(pu);
  const pl = new THREE.Mesh(pupilG, pupilM); pl.renderOrder = 34.5; pl.position.set(0, 0.008, 0.074); pu.add(pl);
  const sh = new THREE.Mesh(shineG, shineM); sh.renderOrder = 35; sh.position.set(0.048, 0.052, 0.11); pu.add(sh);
  const sh2 = new THREE.Mesh(shine2G, shineM); sh2.renderOrder = 35; sh2.position.set(-0.05, -0.046, 0.106); pu.add(sh2);
  return { e, pu };
}
const EYE_BASE = sd => new THREE.Vector3(sd * 0.4, 0.36, 0.84).normalize();
[-1, 1].forEach(sd => { const { e, pu } = makeEye(body); eyes.push({ e, pu, base: EYE_BASE(sd) }); });""")

# ---------- blush, glints, mouth ----------
rep("""const cheekM = new THREE.MeshBasicMaterial({ color: 0xFF9EC4, transparent: true, opacity: 0.55, depthWrite: false }), cheekG = new THREE.SphereGeometry(0.075, 12, 8), cheeks = [];
[-1, 1].forEach(sd => { const m = new THREE.Mesh(cheekG, cheekM); m.renderOrder = 33; body.add(m); cheeks.push({ m, base: new THREE.Vector3(sd * 0.62, 0.17, 0.77).normalize() }); });""",
"""// face stickers sit on the curve of the face: flat shapes bent back the way a ball's surface falls away
const bendToFace = (g, r) => { const P = g.attributes.position; for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i); P.setZ(i, P.getZ(i) - (x * x + y * y) / (2 * (r || 1))); } g.computeVertexNormals(); return g; };
const ZA = new THREE.Vector3(0, 0, 1), faceQ = (m, p) => m.quaternion.setFromUnitVectors(ZA, tv3.copy(p).normalize());
const blushTex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 64; const g = cv.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,128,170,0.95)'); gr.addColorStop(0.55, 'rgba(255,128,170,0.6)'); gr.addColorStop(1, 'rgba(255,128,170,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(cv); })();
const cheekM = new THREE.MeshBasicMaterial({ map: blushTex, transparent: true, opacity: 0.85, depthWrite: false }), cheekG = bendToFace(new THREE.CircleGeometry(0.1, 24)), cheeks = [];
const CHEEK_BASE = sd => new THREE.Vector3(sd * 0.62, 0.13, 0.78).normalize();
[-1, 1].forEach(sd => { const m = new THREE.Mesh(cheekG, cheekM); m.renderOrder = 33; body.add(m); cheeks.push({ m, base: CHEEK_BASE(sd) }); });""")
rep("""const pGlint = new THREE.Mesh(glintG, glintM), pGlint2 = new THREE.Mesh(glint2G, glintM); pGlint.renderOrder = 33; pGlint2.renderOrder = 33; body.add(pGlint); body.add(pGlint2);
const mouthSmile = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.028, 6, 16, Math.PI), eyeB); mouthSmile.rotation.z = Math.PI; mouthSmile.renderOrder = 34; body.add(mouthSmile);
const mouthO = new THREE.Mesh(new THREE.SphereGeometry(0.075, 12, 8), eyeB); mouthO.renderOrder = 34; body.add(mouthO);
const mouthBase = new THREE.Vector3(0, 0.1, 1).normalize();""",
"""const pGlint = new THREE.Mesh(glintG, glintM), pGlint2 = new THREE.Mesh(glint2G, glintM); pGlint.renderOrder = 33; pGlint2.renderOrder = 33; body.add(pGlint); body.add(pGlint2);
if (HI) pGlint.visible = pGlint2.visible = false; // real highlights come from the studio light map
// the mouth: an open smile (dark rim, deep red inside, a pink tongue) or a round "oh", with its top edge on the mouth point
const mouthInM = new THREE.MeshBasicMaterial({ color: 0x5B0A1D, transparent: true }), tongueM = new THREE.MeshBasicMaterial({ color: 0xFF7193, transparent: true });
function dShape(w, h) { const sh = new THREE.Shape(); sh.moveTo(-w, 0); sh.quadraticCurveTo(0, -0.14 * h, w, 0); for (let k = 1; k <= 20; k++) { const t = k / 20 * Math.PI; sh.lineTo(w * Math.cos(t), -h * Math.sin(t)); } return sh; }
function tongueShape(w, h) { const k = 0.93, y0 = -0.52 * h, t1 = Math.asin(Math.min(0.99, 0.52 / k)), x0 = k * w * Math.cos(t1), sh = new THREE.Shape(); sh.moveTo(-x0, y0); sh.quadraticCurveTo(0, -0.27 * h, x0, y0); for (let i = 1; i <= 14; i++) { const t = t1 + (Math.PI - 2 * t1) * i / 14; sh.lineTo(k * w * Math.cos(t), -k * h * Math.sin(t)); } return sh; }
function ohShape(w, h) { const sh = new THREE.Shape(); for (let k = 0; k <= 24; k++) { const t = k / 24 * Math.PI * 2; k ? sh.lineTo(w * Math.sin(t), -h - h * Math.cos(t)) : sh.moveTo(0, 0); } return sh; }
const MW = 0.15, MH = 0.13, RIM = 0.032;
const mouthGeos = { rim: bendToFace(new THREE.ShapeGeometry(dShape(MW + RIM, MH + RIM), 1).translate(0, RIM * 0.55, -0.004)), inner: bendToFace(new THREE.ShapeGeometry(dShape(MW, MH), 1)), tongue: bendToFace(new THREE.ShapeGeometry(tongueShape(MW, MH), 1).translate(0, 0, 0.003)),
  ohRim: bendToFace(new THREE.ShapeGeometry(ohShape(0.085 + RIM, 0.085 + RIM * 0.8), 1).translate(0, RIM * 0.8, -0.004)), ohIn: bendToFace(new THREE.ShapeGeometry(ohShape(0.085, 0.085), 1)) };
function makeMouth(parent) {
  const g = new THREE.Group(), smile = new THREE.Group(), oh = new THREE.Group(), ro = (m, o) => { m.renderOrder = o; return m; };
  smile.add(ro(new THREE.Mesh(mouthGeos.rim, eyeB), 34), ro(new THREE.Mesh(mouthGeos.inner, mouthInM), 34.2), ro(new THREE.Mesh(mouthGeos.tongue, tongueM), 34.4));
  oh.add(ro(new THREE.Mesh(mouthGeos.ohRim, eyeB), 34), ro(new THREE.Mesh(mouthGeos.ohIn, mouthInM), 34.2)); oh.visible = false;
  g.add(smile, oh); g.smile = smile; g.oh = oh; parent.add(g); return g;
}
// put a mouth on the face, facing out from it; open = the round "oh"
function placeMouth(M, p, size, open, ohY) { M.position.copy(p); faceQ(M, tv2.set(0, p.y * 0.6, 1)); M.smile.visible = !open; M.oh.visible = open; M.smile.scale.setScalar(size); M.oh.scale.set(1, ohY || 1, 1); }
const pMouth = makeMouth(body);
const mouthBase = new THREE.Vector3(0, -0.01, 1).normalize();""")

# fangs hang from the top edge of the new mouth; the CPU brows and mouths, and the arcs for happy eyes, match the new face
rep("""const arcEyeG = new THREE.TorusGeometry(0.13, 0.036, 6, 18, Math.PI), pArcs""", """const arcEyeG = new THREE.TorusGeometry(0.125, 0.044, 10, 24, Math.PI), pArcs""")

# ---------- wear: glossy, no ink lines in Graphics mode ----------
rep("""const WM = { hat: toon(0x35225C), band: toon(0xFF8A1F), halo: new THREE.MeshBasicMaterial({ color: 0xFFE27A, transparent: true }), horn: toon(0xE1283E), wing: toon(0x2E2048, { side: THREE.DoubleSide }), wingIn: toon(0x6A4AA0, { side: THREE.DoubleSide }), line: new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.DoubleSide }) };""",
"""const WM = { hat: glossMat(0x2F1D52, { roughness: 0.38 }), band: glossMat(0xFF9A1F, { roughness: 0.3 }), halo: new THREE.MeshBasicMaterial({ color: 0xFFE27A, transparent: true }), horn: glossMat(0xE1283E), wing: glossMat(0x2A1846, { side: THREE.DoubleSide, roughness: 0.3 }), wingIn: glossMat(0x6A4AA0, { side: THREE.DoubleSide }), line: new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.DoubleSide }), rib: glossMat(0x150B26, { roughness: 0.4 }) };""")
rep("""function withLine(mesh, lineGeo, k) { const o = new THREE.Mesh(lineGeo || mesh.geometry, outlineMat); if (!lineGeo) o.scale.setScalar(k || 1.12); o.renderOrder = 32.6; mesh.add(o); return mesh; }""",
"""function withLine(mesh, lineGeo, k) { if (HI) return mesh; const o = new THREE.Mesh(lineGeo || mesh.geometry, outlineMat); if (!lineGeo) o.scale.setScalar(k || 1.12); o.renderOrder = 32.6; mesh.add(o); return mesh; }
// Graphics mode bat wings get bones: thin glossy ribs from the shoulder out to each point of the scalloped edge
const wingRibG = (() => { if (!HI) return null; const list = [], A = new THREE.Vector3(0.04, 0.1, 0.004); for (const [x, y] of [[0.86, 0.52], [0.8, 0.12], [0.56, 0.06], [0.3, 0.0]]) { const B = new THREE.Vector3(x, y, 0.004), d = B.clone().sub(A), L = d.length(), g = new THREE.CylinderGeometry(0.012, 0.024, L, 8); g.rotateZ(-Math.atan2(d.x, d.y)); g.translate((A.x + B.x) / 2, (A.y + B.y) / 2, 0.006); list.push(g); } return mergeGeos(list); })();""")
rep("""  const halo = new THREE.Group(); const hr = ro(new THREE.Mesh(haloG, WM.halo)); halo.add(hr); const hl = new THREE.Mesh(haloLineG, outlineMat); hl.renderOrder = 32.6; halo.add(hl);""",
"""  const halo = new THREE.Group(); const hr = ro(new THREE.Mesh(haloG, WM.halo)); halo.add(hr); if (!HI) { const hl = new THREE.Mesh(haloLineG, outlineMat); hl.renderOrder = 32.6; halo.add(hl); }""")
rep("""  const wings = [-1, 1].map(sd => { const g = new THREE.Group(); const m = ro(new THREE.Mesh(wingG, WM.wing)); g.add(m); const l = new THREE.Mesh(wingLineG, WM.line); l.renderOrder = 32.6; g.add(l); g.scale.set(sd * 1.3, 1.3, 1.3); g.userData.sd = sd; return g; });""",
"""  const wings = [-1, 1].map(sd => { const g = new THREE.Group(); const m = ro(new THREE.Mesh(wingG, WM.wing)); g.add(m); if (HI) { const rb = ro(new THREE.Mesh(wingRibG, WM.rib)); g.add(rb); } else { const l = new THREE.Mesh(wingLineG, WM.line); l.renderOrder = 32.6; g.add(l); } g.scale.set(sd * 1.3, 1.3, 1.3); g.userData.sd = sd; return g; });""")
rep("""const fangG = new THREE.ConeGeometry(0.03, 0.085, 10).rotateX(Math.PI).translate(0, -0.042, 0), fangM = toon(0xFFFFFF, { transparent: true }),""",
    """const fangG = new THREE.ConeGeometry(0.03, 0.085, 10).rotateX(Math.PI).translate(0, -0.042, 0), fangM = glossMat(0xFFFFFF, { transparent: true }),""")
rep("""[-1, 1].forEach(sd => { const f = new THREE.Mesh(fangG, fangM); f.renderOrder = 35; const o = new THREE.Mesh(fangG, fangHullM); o.scale.setScalar(1.45); o.renderOrder = 34; f.add(o); f.userData.sd = sd; body.add(f); fangs.push(f); });""",
    """[-1, 1].forEach(sd => { const f = new THREE.Mesh(fangG, fangM); f.renderOrder = 35; if (!HI) { const o = new THREE.Mesh(fangG, fangHullM); o.scale.setScalar(1.45); o.renderOrder = 34; f.add(o); } f.userData.sd = sd; body.add(f); fangs.push(f); });""")
rep("""  const fangs = [-1, 1].map(sd => { const f = new THREE.Mesh(fangG, fangM); f.renderOrder = 35; const o = new THREE.Mesh(fangG, fangHullM); o.scale.setScalar(1.45); o.renderOrder = 34; f.add(o); f.userData.sd = sd; return f; });""",
    """  const fangs = [-1, 1].map(sd => { const f = new THREE.Mesh(fangG, fangM); f.renderOrder = 35; if (!HI) { const o = new THREE.Mesh(fangG, fangHullM); o.scale.setScalar(1.45); o.renderOrder = 34; f.add(o); } f.userData.sd = sd; return f; });""")
# fangs on a CPU sit at the corners of the new mouth's top edge
rep("""  if (withFangs && W.fangs[0].visible) { const mp = gooJS(mouthBase, U).multiplyScalar(1.03); for (const f of W.fangs) f.position.copy(mp).add(tv1.set(f.userData.sd * 0.056, 0.02, 0.016)); }""",
    """  if (withFangs && W.fangs[0].visible) { const mp = gooJS(mouthBase, U).multiplyScalar(1.03); for (const f of W.fangs) f.position.copy(mp).add(tv1.set(f.userData.sd * 0.07, 0.004, 0.02)); }""")

# ---------- the holy water and the other CPU: same face, no ink outline in Graphics mode ----------
rep("""const cHull = new THREE.Mesh(blobG, gooify(new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), true, undefined, gooU2)); cHull.renderOrder = 31; cBody.add(cHull);""",
    """const cHull = new THREE.Mesh(blobG, gooify(new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), true, undefined, gooU2)); cHull.renderOrder = 31; cHull.visible = !HI; cBody.add(cHull);""")
rep("""const cGlint2 = new THREE.Mesh(glint2G, cGlint.material); cGlint2.renderOrder = 33; cBody.add(cGlint2);""",
    """const cGlint2 = new THREE.Mesh(glint2G, cGlint.material); cGlint2.renderOrder = 33; cBody.add(cGlint2); if (HI) cGlint.visible = cGlint2.visible = false;""")
rep("""  cEyes.push({ e, pu, br, sd, base: new THREE.Vector3(sd * 0.37, 0.45, 0.8).normalize() });""", """  cEyes.push({ e, pu, br, sd, base: EYE_BASE(sd) });""")
rep("""const cMouth = new THREE.Mesh(new THREE.TorusGeometry(0.105, 0.036, 8, 16, Math.PI), eyeB); cMouth.rotation.z = Math.PI; cMouth.renderOrder = 34; cBody.add(cMouth);""",
    """const cMouth = makeMouth(cBody);""")
rep("""  const hull = new THREE.Mesh(blobG, gooify(new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), true, undefined, U)); hull.renderOrder = 31; body.add(hull);
  const glint = new THREE.Mesh(glintG, cGlint.material), glint2 = new THREE.Mesh(glint2G, cGlint.material); glint.renderOrder = glint2.renderOrder = 33; body.add(glint); body.add(glint2);
  const eyes = []; [-1, 1].forEach(sd => { const { e, pu } = makeEye(body); const br = new THREE.Mesh(cEyes[0].br.geometry, eyeB); br.renderOrder = 34; body.add(br); eyes.push({ e, pu, br, sd, base: new THREE.Vector3(sd * 0.37, 0.45, 0.8).normalize() }); });
  const mouth = new THREE.Mesh(cMouth.geometry, eyeB); mouth.rotation.z = Math.PI; mouth.renderOrder = 34; body.add(mouth);""",
"""  const hull = new THREE.Mesh(blobG, gooify(new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), true, undefined, U)); hull.renderOrder = 31; hull.visible = !HI; body.add(hull);
  const glint = new THREE.Mesh(glintG, cGlint.material), glint2 = new THREE.Mesh(glint2G, cGlint.material); glint.renderOrder = glint2.renderOrder = 33; body.add(glint); body.add(glint2); if (HI) glint.visible = glint2.visible = false;
  const eyes = []; [-1, 1].forEach(sd => { const { e, pu } = makeEye(body); const br = new THREE.Mesh(cEyes[0].br.geometry, eyeB); br.renderOrder = 34; body.add(br); eyes.push({ e, pu, br, sd, base: EYE_BASE(sd) }); });
  const mouth = makeMouth(body);""")
rep("""  const mp = gooJS(mouthBase, gooU2).multiplyScalar(1.03); cMouth.position.copy(mp).add(tv1.set(0, 0.06, 0)); cMouth.scale.set(1, ahead ? 1.2 : scared ? -0.8 : 0.9, 1);""",
    """  const mp = gooJS(mouthBase, gooU2).multiplyScalar(1.02); placeMouth(cMouth, mp, ahead ? 1.1 : 0.85, scared, 1.25);""")
rep("""  const mp = gooJS(mouthBase, U).multiplyScalar(1.03); L.mouth.position.copy(mp).add(tv1.set(0, 0.06, 0)); L.mouth.scale.set(1, ahead ? 1.2 : scared ? -0.8 : 0.9, 1);""",
    """  const mp = gooJS(mouthBase, U).multiplyScalar(1.02); placeMouth(L.mouth, mp, ahead ? 1.1 : 0.85, scared, 1.25);""")

# ---------- the player's face each frame ----------
rep("""  const mp = gooJS(mouthBase).multiplyScalar(1.03), openO = !happy && (P.air || scared || strain);
  mouthO.visible = openO; mouthSmile.visible = !openO;
  mouthO.position.copy(mp); mouthO.scale.set(1, scared ? 1.5 : strain ? 0.6 : 1.1, 0.4);
  mouthSmile.position.copy(mp).add(tv1.set(0, 0.07, 0)); mouthSmile.scale.setScalar(happy ? 1.35 : 1);
  for (const f of fangs) { f.visible = myLook.mouth === 'fangs'; const sd = f.userData.sd; f.position.copy(mp).add(openO ? tv1.set(sd * 0.036, scared ? 0.075 : 0.05, 0.01) : tv1.set(sd * (happy ? 0.07 : 0.052), happy ? -0.035 : -0.012, 0.012)); f.scale.setScalar(happy ? 1.15 : 1); }
  for (const c of cheeks) { c.m.position.copy(gooJS(c.base)); c.m.scale.set(1, happy ? 0.5 : 0.62, 0.32); }""",
"""  const mp = gooJS(mouthBase).multiplyScalar(1.02), openO = !happy && (P.air || scared || strain);
  placeMouth(pMouth, mp, happy ? 1.28 : 1, openO, scared ? 1.35 : strain ? 0.62 : 1);
  for (const f of fangs) { f.visible = myLook.mouth === 'fangs'; const sd = f.userData.sd; f.position.copy(mp).add(openO ? tv1.set(sd * 0.045, 0.012, 0.02) : tv1.set(sd * (happy ? 0.092 : 0.072), 0.004, 0.02)); f.scale.setScalar(happy ? 1.15 : 1); }
  for (const c of cheeks) { const cp = gooJS(c.base); c.m.position.copy(cp).multiplyScalar(1.012); faceQ(c.m, cp); c.m.scale.set(1.5, happy ? 0.72 : 0.92, 1); }""")
rep("""const pFaceParts = [...eyes.flatMap(it => [it.e, it.pu]), ...cheeks.map(c => c.m), mouthSmile, mouthO, ...fangs, ...pBrows, ...pArcs]""",
    """const pFaceParts = [...eyes.flatMap(it => [it.e, it.pu]), ...cheeks.map(c => c.m), pMouth, ...fangs, ...pBrows, ...pArcs]""")
# faded copies of glossy parts keep the studio light map
rep("""  for (const o of objs) o.traverse(m => { if (!m.isMesh) return; let c = seen.get(m.material); if (!c) { c = m.material.clone(); c.transparent = true; seen.set(m.material, c); list.push({ mat: c, base: m.material.opacity }); } m.material = c; });""",
    """  for (const o of objs) o.traverse(m => { if (!m.isMesh) return; let c = seen.get(m.material); if (!c) { c = m.material.clone(); c.transparent = true; seen.set(m.material, c); list.push({ mat: c, base: m.material.opacity }); if (CHAR_MATS.includes(m.material)) charMat(c); } m.material = c; });""")
# the drip strand in the customizer intro has no outline in Graphics mode
rep("""{ const g = new THREE.CylinderGeometry(1, 1, 1, 12, 1, true).translate(0, 0.5, 0), m = new THREE.Mesh(g, teamMats[0]), o = new THREE.Mesh(g, outlineMat); m.renderOrder = 32; o.scale.set(1.5, 1, 1.5); o.renderOrder = 31; strand.add(m); strand.add(o); strand.visible = false; scene.add(strand); }""",
    """{ const g = new THREE.CylinderGeometry(1, 1, 1, 12, 1, true).translate(0, 0.5, 0), m = new THREE.Mesh(g, teamMats[0]), o = new THREE.Mesh(g, outlineMat); m.renderOrder = 32; o.scale.set(1.5, 1, 1.5); o.renderOrder = 31; o.visible = !HI; strand.add(m); strand.add(o); strand.visible = false; scene.add(strand); }""")
# droplets: glossy jelly in Graphics mode, and rounder
rep("""const parts = [], partG = new THREE.SphereGeometry(0.11, 8, 6), splashMat = toon(C.ink, null, { roughness: 0.25 }), teamMats = TEAMS.map(t => toon(t.wet, null, { roughness: 0.25 })), teamPartMat = () => teamMats[P.team];""",
    """const parts = [], partG = new THREE.SphereGeometry(0.11, HI ? 14 : 8, HI ? 10 : 6), splashMat = HI ? glossMat(C.ink, { roughness: 0.2, clearcoatRoughness: 0.05 }) : toon(C.ink), teamMats = TEAMS.map(t => HI ? glossMat(t.wet, { roughness: 0.2, clearcoatRoughness: 0.05 }) : toon(t.wet)), teamPartMat = () => teamMats[P.team];""")
open(p,'w').write(s); print('char patch 1 ok')
