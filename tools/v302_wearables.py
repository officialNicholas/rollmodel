"""v302: five new everyday wearables, two of them on the body.

- Propeller cap (head): a six-panel cap in red, yellow and blue with a bill and a little propeller on top that spins, faster the
  faster you go and faster still in the air.
- Bouncy antennae (head): two springy stalks with pink pom-pom tips that splay out, bob and lag behind as you move, land and turn.
- Snorkel mask (face): yellow goggles over both eyes with a strap round the back of the head and an orange snorkel up the side.
- Arm floaties (body): a pair of orange water wings, one on each upper arm, that swing with the crawl.
- Hero cape (body): a royal blue cape with a gold hem and a gold star, lined in red, from the shoulders to the base of the tail. It
  follows the spine as the body bends, ripples, and lifts and streams out behind you at speed.

The face and body pieces are fitted to the axolotl's measured shape (raycast off the model: the face, the back, the waist, the arms),
so they sit on it rather than float or sink. A swim ring was tried first and dropped: the axolotl's belly is on the floor, so
anything round its waist sinks into the ground.

All five are in stock from the start (nothing to find). Prices sit inside the everyday range, from the simplest to the one that
turns heads: antennae 195, arm floaties 245, snorkel mask 295, propeller cap 345, hero cape 480. See docs/wearables-v302.md for how
they were ranked. The cape and the floaties are clothing, so like the scarf, bow tie and pearls you wear one clothing piece at a
time."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

GEO = r"""
// ---------- (v302) five new everyday pieces: a propeller cap, bouncy antennae, a snorkel mask, arm floaties and a hero cape ----------
const vcolGeo = (g, colOf) => { const q = g.index ? g.toNonIndexed() : g, p = q.attributes.position, n = p.count, a = new Float32Array(n * 3), c = new THREE.Color(), cen = new THREE.Vector3();
  for (let i = 0; i < n; i += 3) { cen.set(0, 0, 0); for (let k = 0; k < 3; k++) cen.x += p.getX(i + k) / 3, cen.y += p.getY(i + k) / 3, cen.z += p.getZ(i + k) / 3; c.set(colOf(cen)); for (let k = 0; k < 3; k++) { a[(i + k) * 3] = c.r; a[(i + k) * 3 + 1] = c.g; a[(i + k) * 3 + 2] = c.b; } }
  q.setAttribute('color', new THREE.BufferAttribute(linArr(a), 3)); return q; };
const vcolMat = (extra) => { const m = glossMat(0xFFFFFF, Object.assign({ vertexColors: true }, extra || {})); m.vertexColors = true; return m; };
const capMat = vcolMat({ roughness: 0.6, clearcoat: 0.15 }), _fM = new THREE.Matrix4();
const propCapParts = (() => { const C = [0xE63946, 0xFFD23F, 0x3A86FF];
  const dome = vcolGeo(new THREE.SphereGeometry(0.5, 36, 14, 0, Math.PI * 2, 0, Math.PI * 0.5).scale(1, 0.92, 1), v => C[Math.floor(((Math.atan2(v.z, v.x) / (Math.PI * 2) + 1) % 1) * 6) % 3]);
  const bill = new THREE.CylinderGeometry(0.42, 0.42, 0.045, 28, 1, false, -Math.PI / 2, Math.PI).scale(1, 1, 0.82).translate(0, 0.005, 0.27).rotateX(0.12);
  const button = new THREE.SphereGeometry(0.07, 14, 10).translate(0, 0.46, 0), pin = new THREE.CylinderGeometry(0.022, 0.022, 0.16, 8).translate(0, 0.53, 0);
  return [[dome, capMat], [bill, glossMat(0x3A86FF, { roughness: 0.5, clearcoat: 0.2 })], [button, glossMat(0xFFD23F, { roughness: 0.4 })], [pin, glossMat(0xE8E2F2, { roughness: 0.3 })]]; })();
const propParts = (() => { const blade = s => new THREE.SphereGeometry(1, 16, 8).scale(0.3, 0.025, 0.075).translate(0.3 * s, 0, 0).rotateX(0.32 * s); return [[mergeGeos([blade(1), blade(-1)]), glossMat(0xE63946, { roughness: 0.35, clearcoat: 0.5 })], [new THREE.SphereGeometry(0.045, 10, 8), glossMat(0xFFD23F, { roughness: 0.4 })]]; })();
const antennaParts = (() => { const pts = [[0, 0, 0], [0.02, 0.22, 0.02], [0.08, 0.42, 0.05], [0.16, 0.56, 0.08]].map(p => new THREE.Vector3(...p)), stalk = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 16, 0.028, 8);
  return [[stalk, glossMat(0x231A2B, { roughness: 0.4, clearcoat: 0.4 })], [new THREE.SphereGeometry(0.1, 16, 12).translate(0.17, 0.6, 0.085), glossMat(0xFF5DA2, { roughness: 0.3, clearcoat: 0.8 })]]; })();
// the snorkel mask in the head's own units (the face sphere's centre, facing +z). Fitted to the axolotl's measured head: the face is 0.44 out
// at the middle and 0.40 at the eyes (0.2 either side, 0.07 up), the sides 0.49 out; the strap runs along the sides and tucks in under the ears
const snorkelParts = (() => { const rubber = glossMat(0xFFC93C, { roughness: 0.45, clearcoat: 0.3 }), dark = glossMat(0x231A2B, { roughness: 0.5 }), tubeM = glossMat(0xFF7A1A, { roughness: 0.35, clearcoat: 0.5 });
  const onEye = (g, s) => g.rotateX(-0.15).rotateY(0.55 * s).translate(0.2 * s, 0.07, 0.435); // (each lens turned out with the curve of the face)
  const lens = s => onEye(new THREE.TorusGeometry(0.115, 0.034, 10, 32).scale(1.15, 1, 1), s), glass = s => onEye(new THREE.CircleGeometry(0.115, 28).scale(1.15, 1, 1).translate(0, 0, 0.004), s);
  const bridge = new THREE.CylinderGeometry(0.028, 0.028, 0.12, 8).rotateZ(Math.PI / 2).translate(0, 0.085, 0.49);
  const sp = [50, 70, 90, 110, 130, 150, 180, -150, -130, -110, -90, -70, -50].map(a => { const b = Math.abs(a), r = b <= 90 ? 0.475 + (b - 50) / 40 * 0.035 : 0.51 + (b - 90) / 90 * 0.05, t = a * Math.PI / 180;
    return new THREE.Vector3(Math.sin(t) * (r + 0.012), 0.07 + 0.06 * Math.pow((b - 50) / 130, 2), Math.cos(t) * (r + 0.012)); });
  const strap = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(sp), 48, 0.022, 6);
  const pts = [[-0.08, -0.21, 0.5], [-0.3, -0.18, 0.41], [-0.47, -0.03, 0.2], [-0.535, 0.2, 0.06], [-0.51, 0.5, -0.01], [-0.48, 0.78, -0.04]].map(p => new THREE.Vector3(...p)), tube = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 28, 0.04, 10);
  const top = new THREE.CylinderGeometry(0.058, 0.052, 0.1, 12).translate(-0.48, 0.81, -0.045), bite = new THREE.SphereGeometry(0.055, 12, 8).scale(1.3, 0.8, 0.8).translate(-0.06, -0.21, 0.5);
  return [[mergeGeos([lens(1), lens(-1)]), rubber], [mergeGeos([glass(1), glass(-1)]), glassMat], [bridge, rubber], [strap, dark], [tube, tubeM], [top, rubber], [bite, dark]]; })();
// the arm floaties: two fat orange chambers round each upper arm with a little white valve (in the body's units: the upper arm is about
// 0.18 thick and 0.48 long, and splays out and back from the shoulder)
const floatParts = (() => { const ch = y => new THREE.TorusGeometry(0.29, 0.085, 12, 30).rotateX(Math.PI / 2).translate(0, y, 0);
  return [[mergeGeos([ch(0.07), ch(-0.07)]), glossMat(0xFF8A1F, { roughness: 0.22, clearcoat: 0.9, clearcoatRoughness: 0.08 })], [new THREE.CylinderGeometry(0.03, 0.034, 0.06, 10).rotateZ(-Math.PI / 2).translate(0.39, 0.07, 0), glossMat(0xFFFFFF, { roughness: 0.35 })]]; })();
// the hero cape: a sheet whose points are laid along the spine every frame (rows down the back, columns across), wrapped over the back
// as a loose oval a little bigger than the body's (in the body's units the back is 0.21-0.26 over the spine and 0.53-0.59 to each side).
// Royal blue with a gold hem and a gold star (it shows on every paint colour), lined in red
const CAPE_R = 10, CAPE_C = 11;
const capeTex = (() => { const cv = document.createElement('canvas'); cv.width = cv.height = 256; const g = cv.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 256, 0); gr.addColorStop(0, '#1C3CB8'); gr.addColorStop(0.5, '#2E5BEA'); gr.addColorStop(1, '#1C3CB8'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  g.fillStyle = '#F2C14E'; g.fillRect(0, 0, 20, 256); g.fillRect(236, 0, 20, 256); g.fillRect(0, 228, 256, 28);
  g.fillStyle = '#231A2B'; g.fillRect(0, 0, 6, 256); g.fillRect(250, 0, 6, 256); g.fillRect(0, 250, 256, 6); g.fillRect(20, 0, 3, 228); g.fillRect(233, 0, 3, 228); g.fillRect(20, 225, 216, 3);
  g.beginPath(); for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? 22 : 50; g.lineTo(128 + Math.cos(a) * r, 112 + Math.sin(a) * r); } g.closePath();
  g.fillStyle = '#F2C14E'; g.fill(); g.lineWidth = 6; g.strokeStyle = '#231A2B'; g.lineJoin = 'round'; g.stroke();
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; })();
const capeMat = glossMat(0xFFFFFF, { side: THREE.FrontSide, roughness: 0.62, clearcoat: 0.12, sheen: 0.5, sheenColor: new THREE.Color(0x9DB4FF) }), capeLining = glossMat(0xC0213A, { side: THREE.BackSide, roughness: 0.7, clearcoat: 0.05 }), claspMat = glossMat(0xE8C25A, { roughness: 0.25, clearcoat: 0.8 });
capeMat.map = capeTex; capeMat.needsUpdate = true;
function capeGeo() { const g = new THREE.BufferGeometry(), n = CAPE_R * CAPE_C, idx = [], uv = new Float32Array(n * 2); g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  for (let r = 0; r < CAPE_R; r++) for (let c = 0; c < CAPE_C; c++) { const i = r * CAPE_C + c; uv[i * 2] = c / (CAPE_C - 1); uv[i * 2 + 1] = 1 - r / (CAPE_R - 1); }
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  for (let r = 0; r < CAPE_R - 1; r++) for (let c = 0; c < CAPE_C - 1; c++) { const a = r * CAPE_C + c, b = a + 1, d = a + CAPE_C, e = d + 1; idx.push(a, d, b, b, d, e); }
  g.setIndex(idx); return g; }
// lay the cape along a centreline (pts: body-space points from the shoulders back): each row an arc of an oval over the back, gathered at
// the neck; at speed the back rows lift and stream out behind, the arc opens and it flutters
const _cv = new THREE.Vector3(), _ct = new THREE.Vector3(), _cs = new THREE.Vector3(), _cu = new THREE.Vector3(0, 1, 0);
function capeLay(g, pts, t, spd) {
  const p = g.attributes.position, L = pts.length - 1, sk = Math.min(1, spd / 6);
  for (let r = 0; r < CAPE_R; r++) { const u = r / (CAPE_R - 1), f = u * L * (1 + 0.16 * sk), i = Math.min(L - 1, Math.floor(f)), k = f - i;
    _cv.copy(pts[i]).lerp(pts[i + 1], k); _ct.copy(pts[i + 1]).sub(pts[i]).normalize(); _cs.crossVectors(_cu, _ct).normalize();
    const q = Math.min(3.999, u * 4), j = Math.floor(q), m = q - j, at = K => K[j] + (K[j + 1] - K[j]) * m, A = at(CAPE_A), B = at(CAPE_B) + sk * 0.32 * u * u;
    const pm = at(CAPE_PM) * (1 - 0.25 * sk * u), fl = Math.sin(t * (5 + spd) - u * 5) * (0.02 + 0.05 * sk) * u;
    for (let c = 0; c < CAPE_C; c++) { const v = c / (CAPE_C - 1) * 2 - 1, ph = v * pm, x = A * Math.sin(ph), y = B * Math.cos(ph) + fl + Math.sin(t * 6 + v * 2.2 + u * 3) * 0.015 * u;
      p.setXYZ(r * CAPE_C + c, _cv.x + _cs.x * x, _cv.y + y, _cv.z + _cs.z * x); } }
  p.needsUpdate = true; g.computeVertexNormals(); g.computeBoundingSphere(); }
// how far out (A) and over (B) the spine it wraps, and how far round (PM, radians from the top), at the chest, the middle of the back,
// the waist, the hips and the base of the tail: the back's measured top plus a little air, gathered at the neck, hanging down the
// flanks, narrower and higher over the hips so the knees come up beside it, and draped down over the tail
const CAPE_A = [0.62, 0.74, 0.72, 0.55, 0.5], CAPE_B = [0.36, 0.32, 0.29, 0.38, 0.3], CAPE_PM = [0.6, 1.45, 1.45, 1.1, 1.45];
const CAPE_REST = [[0, 0, 0], [0, -0.02, -0.53], [0, -0.055, -1.05], [0, -0.076, -1.73], [0, -0.016, -2.23]].map(p => new THREE.Vector3(...p));
// how each sits (window.__*Fit: a tuning hook)
const PROPCAP_FIT = window.__propcapFit || { s: 1.12, y: -0.32, rx: -0.12, rz: 0.06 }, ANTENNA_FIT = window.__antennaFit || { s: 1, y: -0.1, x: 0.26, z: 0.08 };
const FLOAT_FIT = window.__floatFit || { s: 1, k: 0.45 }; // (k of the way down the upper arm)
"""

MAKE = r"""
  // (v302) the five new pieces
  const propcap = simplePiece(propCapParts, PROPCAP_FIT.s), prop = simplePiece(propParts); prop.position.y = 0.62; propcap.userData.gin.add(prop); propcap.userData.prop = prop;
  const antennae = new THREE.Group(); antennae.userData.st = [-1, 1].map(sd => { const a = simplePiece(antennaParts, ANTENNA_FIT.s); a.scale.x = sd; a.position.set(ANTENNA_FIT.x * sd, 0, ANTENNA_FIT.z); antennae.add(a); return a; });
  const snorkel = simplePiece(snorkelParts), floaties = new THREE.Group(); floaties.userData.arm = [1, -1].map(() => { const f = simplePiece(floatParts, FLOAT_FIT.s); floaties.add(f); return f; });
  const cape = new THREE.Group(); { const g = capeGeo(); capeLay(g, CAPE_REST, 0, 0); const m = new THREE.Mesh(g, capeMat), ln = new THREE.Mesh(g, capeLining); m.renderOrder = 33; ln.renderOrder = 33; m.castShadow = true; cape.add(m, ln); cape.userData.geo = g;
    const cl = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.04, 8, 20), claspMat), o = new THREE.Mesh(cl.geometry, inkMat); o.renderOrder = 32.6; cl.add(o); cl.renderOrder = 33; cape.add(cl); cape.userData.clasp = cl; }
  for (const m of [propcap, antennae, snorkel, floaties, cape]) { m.visible = false; body.add(m); }
"""

PLACE = r"""
    // (v302) the propeller cap and the antennae ride the head like the hats; the snorkel mask sits on the face; the floaties on the upper arms; the cape down the back
    if (W.propcap.visible) { const F = PROPCAP_FIT; W.propcap.position.copy(tv3).add(tv1.set(0, (F.y + dropIn + S.b * 0.22) * hs, 0)); W.propcap.quaternion.copy(wearQ).multiply(wearQ2.setFromEuler(wearE.set(F.rx + S.tx * 0.9, 0, F.rz + S.tz * 0.9))); W.propcap.scale.multiplyScalar(hs);
      const pr = W.propcap.userData.prop; pr.rotation.y = (pr.userData.a = (pr.userData.a || 0) + wearDt * (5 + Math.min(1, (D.spd || 0) / 5) * 16 + (D.air ? 8 : 0))); }
    if (W.antennae.visible) { const F = ANTENNA_FIT; W.antennae.position.copy(tv3).add(tv1.set(0, (F.y + dropIn + S.b * 0.3) * hs, 0)); W.antennae.quaternion.copy(wearQ); W.antennae.scale.multiplyScalar(hs);
      for (const a of W.antennae.userData.st) { const sd = Math.sign(a.scale.x); a.rotation.set(-0.12 + S.tx * 1.5 + Math.sin(t * 7.5 + sd) * 0.05, 0, -sd * (0.3 + Math.sin(t * 6.1 + sd * 2) * 0.05) + S.tz * 1.5); } }
"""

PLACE2 = r"""
    if (W.snorkel.visible) { CH.headTop(SI, wv1, wq1, 0); W.snorkel.position.copy(wv1); W.snorkel.quaternion.copy(wq1).multiply(wearQ2.setFromEuler(wearE.set(S.tx * 0.2, 0, S.tz * 0.15))); W.snorkel.scale.multiplyScalar(mk); }
    if ((W.floaties.visible || W.cape.visible) && CH.boneAt) {
      if (W.floaties.visible) { const fa = W.floaties.userData.arm; for (let i = 0; i < 2; i++) { const f = fa[i], sd = i ? -1 : 1, a = CH.boneAt(SI, sd > 0 ? 'upperarm.L' : 'upperarm.R', wv1), b = CH.boneAt(SI, sd > 0 ? 'forearm.L' : 'forearm.R', wv2);
        wv3.copy(b).sub(a).normalize(); f.position.copy(a).lerp(b, FLOAT_FIT.k); wv1.set(sd, 0, 0).addScaledVector(wv3, -sd * wv3.x).normalize(); wv2.crossVectors(wv1, wv3); _fM.makeBasis(wv1, wv3, wv2); f.quaternion.setFromRotationMatrix(_fM); f.scale.setScalar(pk * (1 + Math.sin(t * 3.1 + sd) * 0.025)); } } // (round the arm, its valve outward)
      if (W.cape.visible) { const P4 = W.cape.userData.pts || (W.cape.userData.pts = [0, 1, 2, 3, 4].map(() => new THREE.Vector3())); CH.boneAt(SI, 'chest', P4[0]); CH.boneAt(SI, 'spine1', P4[1]); CH.boneAt(SI, 'spine', P4[2]); CH.boneAt(SI, 'hips', P4[3]); CH.boneAt(SI, 'tail1', P4[4]);
        capeLay(W.cape.userData.geo, P4, t, D.spd || 0); W.cape.position.set(0, 0, 0); W.cape.quaternion.identity(); W.cape.userData.clasp.position.copy(P4[0]).add(wv1.set(0, 0.37, 0.02)); W.cape.userData.clasp.rotation.set(-1.2, 0, 0); } }
"""

def apply(s):
    # the pieces' shapes and materials, after the v238 set
    a = "// how each sits (window.__*Fit: a tuning hook)\nconst BEANIE_FIT ="
    s = rep(s, a, GEO.lstrip('\n') + a)
    # built with the everyday set
    a = "  for (const m of [pirate, top, bow, pearls, patch, flower, tiara, glasses, hockey, bunny, skull, beanie, party, scarf, monocle, stache]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, pearls, patch, flower, tiara, glasses, hockey, bunny, skull, beanie, party, scarf, monocle, stache };"
    s = rep(s, a, a.replace("\n  return {", MAKE.rstrip('\n') + "\n  return {").replace("monocle, stache };", "monocle, stache, propcap, antennae, snorkel, floaties, cape };"))
    # the axolotl's bones, for the body pieces
    s = rep(s, "return { S, load, make, update, headTop, headSize, bodyPoint, backPoint, headR0: HEAD_R0, faceK: 1.18 };",
               "function boneAt(I, name, out) { const X = I.ax, M = X.P.m[X.A.mesh], b = M.byName[name] || M.byName.chest; b.updateWorldMatrix(true, false); _mi.copy(I.root.matrixWorld).invert(); _m.multiplyMatrices(_mi, b.matrixWorld).premultiply(I.root.matrix); return out.setFromMatrixPosition(_m); } // (v302: a bone's place, in the body's space)\n  return { S, load, make, update, headTop, headSize, bodyPoint, backPoint, boneAt, headR0: HEAD_R0, faceK: 1.18 };")
    # what's on, and the pop-in scale
    a = "W.stache.visible = !off && look.mouth === 'stache';"
    s = rep(s, a, a + " W.propcap.visible = !off && look.head === 'propcap'; W.antennae.visible = !off && look.head === 'antennae'; W.snorkel.visible = !off && look.eye === 'snorkel'; W.floaties.visible = !off && look.arms === 'floaties'; W.cape.visible = !off && look.back === 'cape'; // (v302)")
    s = rep(s, "W.beanie, W.party, W.scarf, W.monocle, W.stache, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }",
               "W.beanie, W.party, W.scarf, W.monocle, W.stache, W.propcap, W.antennae, W.snorkel, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }") # (the floaties pop in on their own; the cape is laid in the body's space, so no pop)
    # placing them (on the axolotl); the face and body ones only on its everyday form, and none on the old blob
    a = "    // on the face and the side of the head (the everyday slime only: the other forms have their own heads): the patch over its right eye,"
    s = rep(s, a, PLACE.lstrip('\n') + a)
    s = rep(s, "    if (!plain) { W.patch.visible = W.flower.visible = W.bow.visible = W.pearls.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = W.scarf.visible = W.monocle.visible = W.stache.visible = false; }",
               "    if (!plain) { W.patch.visible = W.flower.visible = W.bow.visible = W.pearls.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = W.scarf.visible = W.monocle.visible = W.stache.visible = W.snorkel.visible = W.floaties.visible = W.cape.visible = false; }")
    a = "    if (W.halo.visible) { W.halo.position.copy(tv3).add(tv1.set(-S.tz * 0.45 * hs,"
    s = rep(s, a, PLACE2.lstrip('\n') + a)
    s = rep(s, "  W.patch.visible = W.flower.visible = W.bow.visible = W.pearls.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = W.scarf.visible = W.monocle.visible = W.stache.visible = false;\n  for (const [o, F] of",
               "  W.patch.visible = W.flower.visible = W.bow.visible = W.pearls.visible = W.glasses.visible = W.hockey.visible = W.skull.visible = W.scarf.visible = W.monocle.visible = W.stache.visible = W.propcap.visible = W.antennae.visible = W.snorkel.visible = W.floaties.visible = W.cape.visible = false;\n  for (const [o, F] of")
    # the shop: the list, the slots, the prices (all in stock from the start), the pictures and the tile icons
    a = "{ id: 'scarf', name: 'Scarf', slot: 'neck', stage: 'blank' },"
    s = rep(s, a, a + " { id: 'antennae', name: 'Bouncy antennae', slot: 'head', stage: 'blank' }, { id: 'snorkel', name: 'Snorkel mask', slot: 'eye', stage: 'blank' }, { id: 'propcap', name: 'Propeller cap', slot: 'head', stage: 'blank' }, { id: 'floaties', name: 'Arm floaties', slot: 'arms', stage: 'blank' }, { id: 'cape', name: 'Hero cape', slot: 'back', stage: 'blank' },")
    s = rep(s, "const WEAR_CAT = { head: 'head', side: 'head', eye: 'face', lash: 'face', mouth: 'face', neck: 'cloth', back: 'cloth' };",
               "const WEAR_CAT = { head: 'head', side: 'head', eye: 'face', lash: 'face', mouth: 'face', neck: 'cloth', back: 'cloth', arms: 'cloth' };")
    s = rep(s, "zombie: 975, hat: 1105 };", "zombie: 975, hat: 1105, antennae: 195, floaties: 245, snorkel: 295, propcap: 345, cape: 480 }; // (v302: the five new everyday pieces; see docs/wearables-v302.md)")
    s = rep(s, "const OUTRIGHT = new Set(['flower', 'lashes', 'bowtie', 'pearls', 'beanie', 'party', 'monocle', 'stache', 'scarf']),",
               "const OUTRIGHT = new Set(['flower', 'lashes', 'bowtie', 'pearls', 'beanie', 'party', 'monocle', 'stache', 'scarf', 'antennae', 'snorkel', 'propcap', 'floaties', 'cape']),")
    s = rep(s, "monocle: () => pWear.monocle, stache: () => pWear.stache };",
               "monocle: () => pWear.monocle, stache: () => pWear.stache, propcap: () => pWear.propcap, antennae: () => pWear.antennae, snorkel: () => pWear.snorkel, floaties: () => pWear.floaties.userData.pic || (pWear.floaties.userData.pic = (() => { const g = new THREE.Group(); for (const sd of [-1, 1]) { const f = simplePiece(floatParts, FLOAT_FIT.s); f.position.x = sd * 0.42; f.rotation.set(0.5, 0, sd * 0.3); g.add(f); } return g; })()), cape: () => pWear.cape.userData.pic || (pWear.cape.userData.pic = (() => { const g = new THREE.Group(), r = new THREE.Group(), cg = capeGeo(); capeLay(cg, CAPE_REST, 1.2, 2.5); r.add(new THREE.Mesh(cg, capeMat), new THREE.Mesh(cg, capeLining)); r.rotation.set(-1.2, Math.PI, 0, 'YXZ'); g.add(r); return g; })()) };")
    s = rep(s, "neck: ok(l.neck, 'neck'), lash: ok(l.lash, 'lash'),", "neck: ok(l.neck, 'neck'), lash: ok(l.lash, 'lash'), arms: ok(l.arms, 'arms'),")
    a = "const WEAR_ICON = {\n"
    s = rep(s, a, a + ICONS)
    # the axolotl moves everything it doesn't know into the hidden old blob: it keeps these too
    s = rep(s, "W.beanie, W.party, W.scarf, W.monocle, W.stache] : [])].filter(Boolean)), old = new THREE.Group();",
               "W.beanie, W.party, W.scarf, W.monocle, W.stache, W.propcap, W.antennae, W.snorkel, W.floaties, W.cape] : [])].filter(Boolean)), old = new THREE.Group();")
    return s

ICONS = ("  antennae: '<path d=\"M15 30c-1-8-3-13-7-17M25 30c1-8 3-13 7-17\" fill=\"none\" stroke=\"#231A2B\" stroke-width=\"2.6\" stroke-linecap=\"round\"/><circle cx=\"8\" cy=\"11\" r=\"4.6\" fill=\"#FF5DA2\" stroke=\"#D9C8FF\" stroke-width=\"1.4\"/><circle cx=\"32\" cy=\"11\" r=\"4.6\" fill=\"#FF5DA2\" stroke=\"#D9C8FF\" stroke-width=\"1.4\"/>',\n"
         "  snorkel: '<rect x=\"5\" y=\"15\" width=\"13\" height=\"10\" rx=\"5\" fill=\"#BFE6FF\" stroke=\"#FFC93C\" stroke-width=\"2.6\"/><rect x=\"20\" y=\"15\" width=\"13\" height=\"10\" rx=\"5\" fill=\"#BFE6FF\" stroke=\"#FFC93C\" stroke-width=\"2.6\"/><path d=\"M35 30V6\" stroke=\"#FF7A1A\" stroke-width=\"3.4\" stroke-linecap=\"round\"/>',\n"
         "  propcap: '<path d=\"M7 28c0-8 6-13 13-13s13 5 13 13z\" fill=\"#E63946\" stroke=\"#D9C8FF\" stroke-width=\"1.4\"/><path d=\"M16 15.6L18 28h4l2-12.4\" fill=\"#FFD23F\"/><path d=\"M20 15v-5\" stroke=\"#E8E2F2\" stroke-width=\"2\"/><path d=\"M10 9h20\" stroke=\"#E63946\" stroke-width=\"3.4\" stroke-linecap=\"round\"/><path d=\"M27 28h9\" stroke=\"#3A86FF\" stroke-width=\"3.4\" stroke-linecap=\"round\"/>',\n"
         "  floaties: '<g fill=\"#FF8A1F\" stroke=\"#D9C8FF\" stroke-width=\"1.4\"><ellipse cx=\"11\" cy=\"16\" rx=\"7.5\" ry=\"5\"/><ellipse cx=\"11\" cy=\"24\" rx=\"7.5\" ry=\"5\"/><ellipse cx=\"29\" cy=\"16\" rx=\"7.5\" ry=\"5\"/><ellipse cx=\"29\" cy=\"24\" rx=\"7.5\" ry=\"5\"/></g><path d=\"M8 20h6M26 20h6\" stroke=\"#fff\" stroke-width=\"2\" stroke-linecap=\"round\"/><circle cx=\"17\" cy=\"15\" r=\"1.6\" fill=\"#fff\"/><circle cx=\"35\" cy=\"15\" r=\"1.6\" fill=\"#fff\"/>',\n"
         "  cape: '<path d=\"M12 8h16l6 26c-5 2-23 2-28 0z\" fill=\"#D62839\" stroke=\"#D9C8FF\" stroke-width=\"1.4\" stroke-linejoin=\"round\"/><circle cx=\"20\" cy=\"9\" r=\"3\" fill=\"#E8C25A\"/>',\n")
