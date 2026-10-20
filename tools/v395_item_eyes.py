"""v395: the roller and the turret wear the character's own eyes (the user: "The roller and turret should have the same eyes as the
character. Remove the cute facial features of the roller").

- A blob that turns into the roller (and the quick ball of a long slingshot, the same jelly) no longer has the old jelly's face: no big
  shiny cartoon eyes, no brows, no smile, fang or blush. It has the character's eyes instead: the axolotl's own face shader, its eyes
  alone, drawn on a small curved card on the roller's front. The card shares the character's look as it is (eye style, eye colour,
  lashes or patch), so a Sly-eyed character rolls with Sly eyes, a zombie with zombie eyes; it blinks on its own.
- The turret's dot eyes are the character's eyes too, on the front of its steel pod.
- The roller pick-up on the stage loses its smile and rosy cheeks.
- If the axolotl never loads (the old slime stands in), the old faces stay as they were."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""// ---------- (v395) the character's own eyes on the roller and the turret: the axolotl's face shader, its eyes alone (no mouth), drawn
// on a small curved card. The card shares the character's look (eye style, eye colour, lashes) and blinks on its own. Drawn twice per
// pixel, over black and over white, so it lays only what the eyes add over whatever is under it ----------
const EYE_MID = new THREE.Vector3(0, 0.39, 0.86).normalize();
let eyeProgC = null;
function eyeProg() {
  if (eyeProgC) return eyeProgC;
  const src = AXO.FACE_FS, a = src.indexOf('{') + 1, b = src.indexOf('vec4 mA = texture2D(fCol, fCell(fCells.y, cuv))');
  const vs = 'varying vec2 vUv;\nvoid main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }';
  const fs = 'uniform sampler2D fCol, fMsk; uniform vec4 fCells, fMix, fPupil, fComp, fLash; uniform vec3 fIris; uniform float fStyle, uOp; varying vec2 vUv;\n'
    + 'vec2 fCell(float c, vec2 uv){ float col = mod(c, 4.0), row = floor(c * 0.25 + 0.01); return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) / 10.0); }\n'
    + 'float fCone(vec2 p, vec2 a, vec2 b, float w0, float w1) { vec2 ab = b - a; float t = clamp(dot(p - a, ab) / dot(ab, ab), 0.0, 1.0); float d = length(p - a - ab * t) - mix(w0, w1, t); return 1.0 - smoothstep(-0.004, 0.012, d); }\n'
    + 'vec3 eyesOn(vec3 base, vec2 face) { vec4 diffuseColor = vec4(base, 1.0); vec3 vFace = vec3(face, 1.0); float sCatch = 0.0, sSlyM = 0.0;\n' + src.slice(a, b) + '\nreturn c; }\n'
    + 'void main() { vec2 face = mix(vec2(-0.95, -0.3), vec2(0.95, 0.66), vUv); vec3 c0 = eyesOn(vec3(0.0), face), c1 = eyesOn(vec3(1.0), face), tr = clamp(c1 - c0, 0.0, 1.0);\n'
    + '  float al = clamp(1.0 - (tr.r + tr.g + tr.b) / 3.0, 0.0, 1.0); gl_FragColor = vec4(c0 * 1.08, al) * uOp; // (a touch brighter: unlit, beside the lit body)\n  #include <tonemapping_fragment>\n  #include <colorspace_fragment>\n}';
  return (eyeProgC = { vs, fs });
}
// a card w wide, curved round the surface it sits on (rx across, ry up and down: the roller curves only one way)
function eyeCardGeo(w, rx, ry) { const h = w * 0.96 / 1.9, g = new THREE.PlaneGeometry(w, h, 16, 8), P = g.attributes.position;
  for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i); P.setZ(i, -(x * x) / (2 * rx) - (y * y) / (2 * ry)); } return g; }
// the cards of one blob (one for the roller, one for the turret), on its character's look; null while there's no axolotl
function eyeCards(V) {
  if (V.eyeC) return V.eyeC;
  const I = V.slime; if (!I || I.kind !== 'axo' || !I.ax || !I.ax.look) return null;
  const U = I.ax.look.U, pr = eyeProg(), u = { fCol: U.fCol, fMsk: U.fMsk, fIris: U.fIris, fStyle: U.fStyle, fLash: U.fLash,
    fCells: { value: new THREE.Vector4(0, 8, 0, 8) }, fMix: { value: new THREE.Vector4(0, 0, 0, 6) }, fPupil: { value: new THREE.Vector4(0, -0.03, 1, 0) }, fComp: { value: new THREE.Vector4(1, 1, 0, 0) }, uOp: { value: 1 } };
  const mat = new THREE.ShaderMaterial({ uniforms: u, vertexShader: pr.vs, fragmentShader: pr.fs, transparent: true, depthWrite: false, blending: THREE.CustomBlending,
    blendSrc: THREE.OneFactor, blendDst: THREE.OneMinusSrcAlphaFactor, blendSrcAlpha: THREE.OneFactor, blendDstAlpha: THREE.OneMinusSrcAlphaFactor });
  const mk = (w, rx, ry, parent) => { const m = new THREE.Mesh(eyeCardGeo(w, rx, ry), mat); m.renderOrder = 34; m.visible = false; m.layers.mask = parent.layers.mask; parent.add(m); return m; }; // (on its parent's layers: the Strokes page draws its own)
  return (V.eyeC = { u, mat, mk, bt: 1 + Math.random() * 2, bk: 0, roll: null, tur: null });
}
function eyeBlink(E, dt) { E.bt -= dt; if (E.bt <= 0) { E.bk = 0.13; E.bt = 1.8 + Math.random() * 3.2; } if (E.bk > 0) E.bk -= dt; E.u.fMix.value.y = E.bk > 0 ? 1 : 0; }
// the jelly's face (the roller, and the ball of a long slingshot): its old face parts away, nothing drawn on it, the character's eyes on
// its front instead
function itemEyes(V, U, dt, parts) {
  const E = eyeCards(V); if (!E) return;
  for (const o of parts) if (o) o.visible = false;
  U.uFace.value.w = 0; eyeBlink(E, dt);
  const c = E.roll || (E.roll = E.mk(2.0, 99, 1.15, V.oldBlob)), p = gooJS(faceAt(EYE_MID, U), U), s = 1 - 0.16 * U.gRoll.value;
  c.visible = true; c.position.copy(p).multiplyScalar(1.03); faceQ(c, c.position); c.scale.setScalar(s);
}
"""

def apply(s):
    # the face shader, for the cards
    s = rep(s, "return { FACE, EYE_COLS, EYE_STYLES, EYE_STYLE_K, EXPR, FACE_X, FACE_MX, pupilOf, FACE_EYE, FACE_KINDS, FACE_LIDS, makeFaceSheets, palette, Look, axoMaterial };",
               "return { FACE, EYE_COLS, EYE_STYLES, EYE_STYLE_K, EXPR, FACE_X, FACE_MX, pupilOf, FACE_EYE, FACE_KINDS, FACE_LIDS, makeFaceSheets, palette, Look, axoMaterial, FACE_FS };")
    s = rep(s, "return { DEG, loadMesh, texFromBytes,", "return { FACE_FS: __look.FACE_FS, DEG, loadMesh, texFromBytes,")
    s = rep(s, "function placeFace(dt) {", JS + "function placeFace(dt) {")
    # your jelly (the roller, the ball): the character's eyes
    s = rep(s, "  for (const c of cheeks) c.m.visible = false;\n  pGlint.position.copy(",
               "  for (const c of cheeks) c.m.visible = false;\n  itemEyes(VP, gooU, dt, VP.oldFace || (VP.oldFace = [...eyes.map(it => it.e), ...pBrows, ...pArcs, ...fangs]));\n  pGlint.position.copy(")
    # a rival's
    s = rep(s, "  const mp = gooJS(mouthBase, U).multiplyScalar(1.02); setFace(U, cell, size, mL + 8 * mR);\n  L.glint.position.copy(",
               "  const mp = gooJS(mouthBase, U).multiplyScalar(1.02); setFace(U, cell, size, mL + 8 * mR);\n  itemEyes(L.V, U, dt, L.V.oldFace || (L.V.oldFace = [...L.eyes.map(it => it.e), ...L.eyes.map(it => it.br)]));\n  L.glint.position.copy(")
    # the turret: the character's eyes on the front of its pod (where its dot eyes were)
    s = rep(s, "      const ey = V.tur.userData.eyes; if (ey) {",
               "      const ey = V.tur.userData.eyes, EC = eyeCards(V);\n"
               "      if (EC) { if (ey) ey.visible = false; let t = EC.tur; if (!t) { t = EC.tur = EC.mk(1.85, 0.98, 0.98, V.tur); const n = new THREE.Vector3(0, 0.35, Math.sqrt(0.95 * 0.95 - 0.35 * 0.35)).normalize(); t.position.set(0, 0.05, 0).addScaledVector(n, 0.98); faceQ(t, n); }\n"
               "        t.visible = true; eyeBlink(EC, dt); }\n"
               "      else if (ey) {")
    # the roller pick-up: no smile, no rosy cheeks
    s = rep(s, "const fm = new THREE.Mesh(K.mouth, K.faceM); fm.renderOrder = 34; rl.add(fm); ", "")
    return s
