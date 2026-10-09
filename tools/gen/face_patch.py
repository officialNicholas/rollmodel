# The face (mouth, blush, happy eyes) drawn into the jelly's own surface, so it rides every wobble and never sinks in
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:100], c)
    s = s.replace(a, b)

# the mouth atlas: an open smile, a big laugh, an "oh" and a small smile, each with a dark rim, a deep red inside and a pink tongue
rep("""// every blob shares these: the gumdrop shape, and (Graphics mode) how strongly light glows through the jelly
const JELLY = { value: 1 }, JGLOW = { value: 1 };""", """// every blob shares these: the gumdrop shape, and (Graphics mode) how strongly light glows through the jelly
const JELLY = { value: 1 }, JGLOW = { value: 1 };
// mouths, drawn once: [0] an open smile, [1] a big laugh, [2] an "oh", [3] a small smile. Each fills a quarter of the sheet
const faceTex = (() => {
  const S = 512, cv = document.createElement('canvas'); cv.width = cv.height = S; const g = cv.getContext('2d');
  const RIM = '#1A1030', IN = '#5B0A1D', TONGUE = '#FF7193';
  const cell = (c, fn) => { g.save(); g.translate((c % 2) * 256 + 128, (c < 2 ? 384 : 128)); g.scale(118, -118); g.lineJoin = 'round'; g.lineCap = 'round'; fn(); g.restore(); };
  const dPath = (w, top, h, dip) => { g.beginPath(); g.moveTo(-w, top); g.quadraticCurveTo(0, top - dip, w, top); for (let k = 1; k <= 28; k++) { const t = k / 28 * Math.PI; g.lineTo(w * Math.cos(t), top - h * Math.sin(t)); } g.closePath(); };
  const mouth = (w, top, h, dip, tg) => { dPath(w, top, h, dip); g.fillStyle = IN; g.fill(); g.save(); dPath(w, top, h, dip); g.clip(); g.fillStyle = TONGUE; g.beginPath(); g.ellipse(0, top - h * 0.98, w * tg, h * 0.5, 0, 0, Math.PI * 2); g.fill(); g.strokeStyle = 'rgba(200,60,100,0.6)'; g.lineWidth = 0.04; g.beginPath(); g.moveTo(0, top - h * 0.62); g.lineTo(0, top - h * 0.9); g.stroke(); g.restore(); dPath(w, top, h, dip); g.strokeStyle = RIM; g.lineWidth = 0.11; g.stroke(); };
  cell(0, () => mouth(0.62, 0.42, 0.6, 0.12, 0.62));
  cell(1, () => mouth(0.8, 0.52, 0.86, 0.16, 0.6));
  cell(2, () => { g.beginPath(); g.ellipse(0, 0.0, 0.34, 0.42, 0, 0, Math.PI * 2); g.fillStyle = IN; g.fill(); g.save(); g.clip(); g.fillStyle = TONGUE; g.beginPath(); g.ellipse(0, -0.42, 0.26, 0.22, 0, 0, Math.PI * 2); g.fill(); g.restore(); g.beginPath(); g.ellipse(0, 0.0, 0.34, 0.42, 0, 0, Math.PI * 2); g.strokeStyle = RIM; g.lineWidth = 0.11; g.stroke(); });
  cell(3, () => mouth(0.5, 0.36, 0.4, 0.1, 0.55));
  const t = new THREE.CanvasTexture(cv); t.anisotropy = 4; return t;
})();
// where the face sits, in the ball's own coordinates (before the goo shapes it): eyes, mouth (its top edge) and how big a mouth cell is
const FACE = { eyeX: 0.402, eyeY: 0.362, mouthTop: -0.02, cell: 0.27 };
const faceU = () => ({ uFaceTex: { value: faceTex }, uFace: { value: new THREE.Vector4(0, FACE.cell, FACE.mouthTop - 0.42 * FACE.cell, 1) }, uFace2: { value: new THREE.Vector4(0, 1, FACE.eyeX, FACE.eyeY) } });
// which mouth, how big (it grows down from its top edge), happy-eye arcs on or off
function setFace(U, cell, size, arcs) { const f = U.uFace.value; f.x = cell; f.y = FACE.cell * size; f.z = FACE.mouthTop - 0.42 * FACE.cell * size; U.uFace2.value.x = arcs ? 1 : 0; }
// drawn on the body's surface: the mouth from the sheet, soft pink blush under the eyes, and dark arcs for eyes when happy
const FACE_FS = `
float faceInk = 0.0;
if (vSph.z > 0.2) {
  float fk = uFace.w;
  vec2 q = (vSph.xy - vec2(0.0, uFace.z)) / uFace.y;
  if (abs(q.x) < 1.0 && abs(q.y) < 1.0) {
    vec4 m = texture2D(uFaceTex, vec2(mod(uFace.x, 2.0), floor(uFace.x * 0.5 + 0.01)) * 0.5 + (q * 0.5 + 0.5) * 0.5); m.a *= fk;
    diffuseColor.rgb = mix(diffuseColor.rgb, m.rgb, m.a); faceInk = m.a; totalEmissiveRadiance += m.rgb * m.a * 0.25;
  }
  for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 e = (vSph.xy - vec2(sd * uFace2.z * 1.5, uFace2.w - 0.24)) * vec2(1.0, 1.7); float b = smoothstep(0.16, 0.025, length(e)) * uFace2.y * fk; diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0, 0.55, 0.7), b * 0.6); }
  if (uFace2.x > 0.5) for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 e = vSph.xy - vec2(sd * uFace2.z, uFace2.w - 0.03); float a = (1.0 - smoothstep(0.024, 0.037, abs(length(e) - 0.11))) * smoothstep(-0.035, 0.005, e.y) * fk; diffuseColor.rgb = mix(diffuseColor.rgb, vec3(0.1, 0.06, 0.18), a); faceInk = max(faceInk, a); }
}`;""")
# the goo shader carries the ball's coordinates through, and the body gets the face
rep("""function gooify(mat, outline, key, U) {
  U = U || gooU;
  const jelly = !outline && mat.isMeshPhysicalMaterial;""", """function gooify(mat, outline, key, U) {
  U = U || gooU;
  const jelly = !outline && mat.isMeshPhysicalMaterial, face = !outline && key !== 'goo-xray' && !!U.uFace;""")
rep("""    let vs = GOO_GLSL + '\\nvarying float vGooY; varying vec3 vGooW;\\n' + sh.vertexShader;
    if (outline) vs = vs.replace('#include <begin_vertex>', 'vec3 transformed = goo(position) + gooN(position, normal) * 0.12; vGooY = position.y;');
    else vs = vs.replace('#include <beginnormal_vertex>', 'vec3 objectNormal = gooN(position, normal);').replace('#include <begin_vertex>', 'vec3 transformed = goo(position); vGooY = position.y;');""",
"""    let vs = GOO_GLSL + '\\nvarying float vGooY; varying vec3 vGooW; varying vec3 vSph;\\n' + sh.vertexShader;
    if (outline) vs = vs.replace('#include <begin_vertex>', 'vec3 transformed = goo(position) + gooN(position, normal) * 0.12; vGooY = position.y; vSph = position;');
    else vs = vs.replace('#include <beginnormal_vertex>', 'vec3 objectNormal = gooN(position, normal);').replace('#include <begin_vertex>', 'vec3 transformed = goo(position); vGooY = position.y; vSph = position;');""")
rep("""    if (jelly) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\nvarying float vGooY; varying vec3 vGooW; uniform float gGlow;\\n' + AO_GLSL).replace('#include <aomap_fragment>', '#include <aomap_fragment>' + JELLY_FS + '\\ntotalEmissiveRadiance += diffuseColor.rgb * stageLit(vGooW, vec3(0.0, 1.0, 0.0)) * 0.45;');""",
"""    if (face) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\nvarying vec3 vSph; uniform sampler2D uFaceTex; uniform vec4 uFace, uFace2;').replace('#include <color_fragment>', '#include <color_fragment>' + FACE_FS);
    if (jelly) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\nvarying float vGooY; varying vec3 vGooW; uniform float gGlow;\\n' + AO_GLSL).replace('#include <aomap_fragment>', '#include <aomap_fragment>' + (face ? '' : '\\nfloat faceInk = 0.0;') + JELLY_FS + '\\ntotalEmissiveRadiance += diffuseColor.rgb * stageLit(vGooW, vec3(0.0, 1.0, 0.0)) * 0.45;');""")
rep("""  mat.customProgramCacheKey = () => (key || (outline ? 'goo-outline' : 'goo-body')) + (jelly ? '-jelly' : '');""",
    """  mat.customProgramCacheKey = () => (key || (outline ? 'goo-outline' : 'goo-body')) + (jelly ? '-jelly' : '') + (face ? '-face' : '');""")
# the jelly glow stays off the mouth and the arcs
rep("""  totalEmissiveRadiance += hot * (0.085 * edge * edge + 0.15 * low * (0.35 + 0.65 * key) + 0.16 * thru * (0.3 + edge)) * gGlow;
  totalEmissiveRadiance += mix(hot, vec3(1.0), 0.3) * pow(edge, 3.4) * 0.36 * gGlow;""", """  float noInk = 1.0 - faceInk;
  totalEmissiveRadiance += hot * (0.085 * edge * edge + 0.15 * low * (0.35 + 0.65 * key) + 0.16 * thru * (0.3 + edge)) * gGlow * noInk;
  totalEmissiveRadiance += mix(hot, vec3(1.0), 0.3) * pow(edge, 3.4) * 0.36 * gGlow * noInk;""")
# every blob's goo uniforms carry its face
rep("""const gooU = { gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } };
// every blob shares these""", """const gooU = { gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } };
// every blob shares these""")
rep("""const pMouth = makeMouth(body);""", """const pMouth = makeMouth(body); pMouth.visible = false; Object.assign(gooU, faceU()); // the face is drawn on the body now (see FACE_FS)""")
rep("""const gooU2 = { gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } };""",
    """const gooU2 = Object.assign({ gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } }, faceU());""")
rep("""  const U = { gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } };
  const drop = new THREE.Group(), body = new THREE.Group(); drop.add(body);""", """  const U = Object.assign({ gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } }, faceU());
  const drop = new THREE.Group(), body = new THREE.Group(); drop.add(body);""")
rep("""const cMouth = makeMouth(cBody);""", """const cMouth = makeMouth(cBody); cMouth.visible = false;""")
rep("""  const mouth = makeMouth(body);""", """  const mouth = makeMouth(body); mouth.visible = false;""")
# the player's face each frame: mouth and happy arcs go to the shader; happy now closes the eyes into arcs
rep("""  const lx = -look.lean * 0.07, ly = P.air ? (P.vy > 0 ? 0.05 : -0.04) : 0, ES = myLook.eyes, cyc = ES === 'cyclops', arcs = ES === 'happy';""",
    """  const lx = -look.lean * 0.07, ly = P.air ? (P.vy > 0 ? 0.05 : -0.04) : 0, ES = myLook.eyes, cyc = ES === 'cyclops', arcs = ES === 'happy' || (happy && !cyc);""")
rep("""    const ar = pArcs[i]; ar.visible = arcs; if (arcs) { ar.position.copy(p).multiplyScalar(1.03).add(tv1.set(0, -0.03, 0)); faceQ(ar, p); ar.scale.set(1, (happy ? 1.1 : 0.9) * (1 - sq * 0.3), 1); }""",
    """    pArcs[i].visible = false;""")
rep("""  placeMouth(pMouth, mp, happy ? 1.28 : 1, openO, scared ? 1.35 : strain ? 0.62 : 1);""",
    """  setFace(gooU, openO ? 2 : happy ? 1 : 0, openO ? (scared ? 1.2 : strain ? 0.7 : 0.95) : happy ? 1.1 : 1, arcs);""")
rep("""  for (const c of cheeks) { const cp = gooJS(c.base); c.m.position.copy(cp).multiplyScalar(1.012); faceQ(c.m, cp); c.m.scale.set(1.5, happy ? 0.72 : 0.92, 1); }""",
    """  for (const c of cheeks) c.m.visible = false;""")
rep("""placeMouth(cMouth, mp, ahead ? 1.1 : 0.85, scared, 1.25);""", """setFace(gooU2, scared ? 2 : ahead ? 1 : 3, scared ? 1 : ahead ? 0.85 : 1, false);""")
rep("""placeMouth(L.mouth, mp, ahead ? 1.1 : 0.85, scared, 1.25);""", """setFace(U, scared ? 2 : ahead ? 1 : 3, scared ? 1 : ahead ? 0.85 : 1, false);""")
# the customizer intro fades the face in on the surface too
rep("""function introFade(kf, kw) {
  for (const it of pFade.face) it.mat.opacity = it.base * kf;""", """function introFade(kf, kw) {
  gooU.uFace.value.w = kf;
  for (const it of pFade.face) it.mat.opacity = it.base * kf;""")
open(p,'w').write(s); print('face patch ok')
