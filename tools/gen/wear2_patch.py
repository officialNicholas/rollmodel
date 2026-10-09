# accessories: the witch hat from its new model, and a set of everyday ones beside Halloween's: a pirate hat, a top hat, an eye patch, a
# flower by the ear and a bow tie (the hats and the bow tie are models, packed into the page; the patch is fitted to the slime's head)
P = '/home/claude/paint-the-canvas.html'
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

# ---- the packed models ----
pack = open(SP + 'wear_pack.json').read()
rep('<script src="three.r186.min.js"></script>', '<script type="application/json" id="wearPack">' + pack + '</script>\n<script src="three.r186.min.js"></script>')

# ---- decoding them, their materials, the flower ----
rep("// an ink outline for an accessory: its back faces pushed out along the normals, as wide as the body's outline at any distance",
r"""// ---------- the packed accessory models: positions (quantized to their box), normals, smoothed normals for the outline, uvs and indices in
// one base64 blob each, their color and metal/rough maps as JPEGs ----------
const WEAR_PACK = (() => { try { const el = document.getElementById('wearPack'); return el ? JSON.parse(el.textContent) : null; } catch (e) { return null; } })();
function assetGeo(A) {
  const bin = Uint8Array.from(atob(A.b), c => c.charCodeAt(0)).buffer, n = A.n; let o = n * 6; o += (4 - o % 4) % 4;
  const qp = new Uint16Array(bin, 0, n * 3), qn = new Int8Array(bin, o, n * 4), qi = new Int8Array(bin, o + n * 4, n * 4), qu = new Uint16Array(bin, o + n * 8, n * 2), ix = new Uint16Array(bin, o + n * 12, A.ni);
  const Pp = new Float32Array(n * 3), N = new Float32Array(n * 3), NI = new Float32Array(n * 3), UV = new Float32Array(n * 2);
  for (let i = 0; i < n; i++) { for (let k = 0; k < 3; k++) { Pp[i * 3 + k] = A.mn[k] + qp[i * 3 + k] / 65535 * (A.mx[k] - A.mn[k]); N[i * 3 + k] = qn[i * 4 + k] / 127; NI[i * 3 + k] = qi[i * 4 + k] / 127; } for (let k = 0; k < 2; k++) UV[i * 2 + k] = A.umn[k] + qu[i * 2 + k] / 65535 * (A.umx[k] - A.umn[k]); }
  const g = new THREE.BufferGeometry(), idx = new THREE.BufferAttribute(new Uint16Array(ix), 1); g.setAttribute('position', new THREE.BufferAttribute(Pp, 3)); g.setAttribute('normal', new THREE.BufferAttribute(N, 3)); g.setAttribute('uv', new THREE.BufferAttribute(UV, 2)); g.setIndex(idx);
  const ink = new THREE.BufferGeometry(); ink.setAttribute('position', g.attributes.position); ink.setAttribute('normal', new THREE.BufferAttribute(NI, 3)); ink.setIndex(idx);
  g.computeBoundingSphere(); ink.boundingSphere = g.boundingSphere; return { g, ink };
}
function assetTex(b64, srgb) { const im = new Image(), t = new THREE.Texture(im); t.flipY = false; t.anisotropy = 4; if (srgb) t.colorSpace = THREE.SRGBColorSpace; im.onload = () => { t.needsUpdate = true; }; im.src = 'data:image/jpeg;base64,' + b64; return t; }
// a model's look: its own color map; in Graphics mode its metal and roughness maps too, under a light coat of gloss
function assetMat(A, extra) {
  const map = assetTex(A.col, true);
  if (!HI) return new THREE.MeshToonMaterial({ map, gradientMap: grad });
  const mr = assetTex(A.mr, false); return charMat(new THREE.MeshPhysicalMaterial(Object.assign({ map, roughnessMap: mr, metalnessMap: mr, roughness: 1, metalness: 1, clearcoat: 0.35, clearcoatRoughness: 0.22, envMapIntensity: 1.25 }, extra || {})));
}
const WEAR_A = WEAR_PACK ? (() => { const o = {}; for (const k of ['witch', 'pirate', 'top', 'bow', 'patch']) if (WEAR_PACK[k]) o[k] = assetGeo(WEAR_PACK[k]); return o; })() : {};
const WEAR_AM = WEAR_PACK ? { witch: assetMat(WEAR_PACK.witch), pirate: assetMat(WEAR_PACK.pirate), top: assetMat(WEAR_PACK.top), bow: assetMat(WEAR_PACK.bow, { clearcoat: 0.6 }) } : {};
// the patch and its strap: dark leather, a little sheen
const patchMat = glossMat(0x231A2B, { roughness: 0.42, clearcoat: 0.35, clearcoatRoughness: 0.3 });
// the flower: five white petals round a warm yellow heart, a leaf behind (one mesh, colored by vertex)
const flowerG = (() => {
  const parts = [], R = rng(31), col = (g, c) => { const n = g.attributes.position.count, a = new Float32Array(n * 3), cc = new THREE.Color(c); for (let i = 0; i < n; i++) { a[i * 3] = cc.r; a[i * 3 + 1] = cc.g; a[i * 3 + 2] = cc.b; } g.setAttribute('color', new THREE.BufferAttribute(a, 3)); return g; };
  // a petal: a flattened drop, cupped up a little, warmer toward its base
  const petal = (len, wid, c0, c1) => { const g = new THREE.SphereGeometry(1, 14, 10); const p = g.attributes.position, n = p.count, a = new Float32Array(n * 3), A = new THREE.Color(c0), Bc = new THREE.Color(c1), t = new THREE.Color();
    for (let i = 0; i < n; i++) { let x = p.getX(i), y = p.getY(i), z = p.getZ(i); const u = (x + 1) / 2; x = u * len; z *= wid * (0.35 + 0.65 * Math.sin(Math.min(1, u * 1.15) * Math.PI * 0.62)); y = y * 0.075 + 0.16 * u * u * len; p.setXYZ(i, x, y, z); t.copy(Bc).lerp(A, Math.min(1, u * 1.6)); a[i * 3] = t.r; a[i * 3 + 1] = t.g; a[i * 3 + 2] = t.b; }
    g.setAttribute('color', new THREE.BufferAttribute(a, 3)); g.computeVertexNormals(); return g; };
  for (let k = 0; k < 5; k++) { const g = petal(0.62, 0.36, 0xFFFFFF, 0xFFC93A); g.rotateX(0.18); g.rotateY(k / 5 * 6.2832 + 0.3); g.translate(0, k * 0.004, 0); parts.push(g); }
  const heart = col(new THREE.SphereGeometry(0.13, 12, 8).scale(1, 0.55, 1).translate(0, 0.07, 0), 0xFFB21E); parts.push(heart);
  const leaf = petal(0.78, 0.3, 0x45B852, 0x2E8A3E); leaf.rotateY(-2.2); leaf.translate(0, -0.06, 0); const lc = leaf.attributes.color; for (let i = 0; i < lc.count; i++) lc.setXYZ(i, lc.getX(i) * 0.95, lc.getY(i), lc.getZ(i) * 0.95); parts.push(leaf);
  // merge (keeping colors)
  let n = 0; const ps = parts.map(g => { const q = g.index ? g.toNonIndexed() : g; n += q.attributes.position.count; return q; });
  const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), cl = new Float32Array(n * 3); let o = 0;
  for (const q of ps) { const c = q.attributes.position.count; pos.set(q.attributes.position.array, o * 3); nor.set(q.attributes.normal.array, o * 3); cl.set(q.attributes.color.array, o * 3); o += c; }
  const m = new THREE.BufferGeometry(); m.setAttribute('position', new THREE.BufferAttribute(pos, 3)); m.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); m.setAttribute('color', new THREE.BufferAttribute(linArr(cl), 3)); m.computeBoundingSphere(); return m;
})();
const flowerMat = glossMat(0xFFFFFF, { vertexColors: true, roughness: 0.38, clearcoat: 0.5 });
if (!HI) flowerMat.vertexColors = true;
// how each hat sits: its size on the head, how far down it settles, its tilt (back, to the side)
const HAT_FIT = { witch: { s: 1.3, y: -0.27, rx: -0.14, rz: -0.16 }, pirate: { s: 0.92, y: -0.2, rx: -0.1, rz: 0.06 }, top: { s: 0.86, y: -0.13, rx: -0.12, rz: -0.24 } };
// an asset as a mesh with its outline
function assetMesh(key, mat) { const A = WEAR_A[key]; const m = new THREE.Mesh(A.g, mat); m.renderOrder = 33; const o = new THREE.Mesh(A.ink, inkMat); o.renderOrder = 32.6; m.add(o); return m; }
// an ink outline for an accessory: its back faces pushed out along the normals, as wide as the body's outline at any distance""")

# ---- making them ----
rep("""    const hat = new THREE.Group(), hatIn = new THREE.Group(); hatIn.scale.setScalar(1.3); hat.add(hatIn);
    hatIn.add(lodMesh(P2('cone'), WM.hat, true), lodMesh(P2('brim'), WM.hat, true), lodMesh(P2('band'), WM.band, false), lodMesh([G.buckle, G.buckle], WM.buckle, false));""",
"""    const hat = new THREE.Group(), hatIn = new THREE.Group(); hatIn.scale.setScalar(1.3); hat.add(hatIn);
    if (WEAR_A.witch) hatIn.add(assetMesh('witch', WEAR_AM.witch)); else hatIn.add(lodMesh(P2('cone'), WM.hat, true), lodMesh(P2('brim'), WM.hat, true), lodMesh(P2('band'), WM.band, false), lodMesh([G.buckle, G.buckle], WM.buckle, false));""")
rep("""    const all = [hat, halo, ...horns, ...wings, ...fangs]; for (const m of all) { m.visible = false; body.add(m); }
    return { hat, halo, horns, wings, fangs, body };
  }""",
"""    const all = [hat, halo, ...horns, ...wings, ...fangs]; for (const m of all) { m.visible = false; body.add(m); }
    return Object.assign({ hat, halo, horns, wings, fangs, body }, makeWear2(body));
  }""")
rep("""  const all = [hat, halo, ...horns, ...wings, ...fangs]; for (const m of all) { m.visible = false; body.add(m); }
  return { hat, halo, horns, wings, fangs, body };
}""",
"""  if (WEAR_A.witch) { hatIn.clear(); hatIn.scale.setScalar(1.3); hatIn.add(assetMesh('witch', WEAR_AM.witch)); }
  const all = [hat, halo, ...horns, ...wings, ...fangs]; for (const m of all) { m.visible = false; body.add(m); }
  return Object.assign({ hat, halo, horns, wings, fangs, body }, makeWear2(body));
}
// the everyday set: the two hats and the bow tie from their models, the patch fitted to the head, the flower
function makeWear2(body) {
  const grp = (key, s) => { const g = new THREE.Group(), gin = new THREE.Group(); g.add(gin); if (WEAR_A[key]) { gin.add(assetMesh(key, WEAR_AM[key])); gin.scale.setScalar(s); } g.userData.gin = gin; return g; };
  const pirate = grp('pirate', HAT_FIT.pirate.s), top = grp('top', HAT_FIT.top.s), bow = grp('bow', 1);
  const patch = new THREE.Group(); if (WEAR_A.patch) { const m = new THREE.Mesh(WEAR_A.patch.g, patchMat), o = new THREE.Mesh(WEAR_A.patch.ink, inkMat); m.renderOrder = 34.2; o.renderOrder = 32.6; m.add(o); patch.add(m); }
  const flower = new THREE.Group(); { const m = new THREE.Mesh(flowerG, flowerMat), o = new THREE.Mesh(flowerG, inkMat); m.renderOrder = 33; o.renderOrder = 32.6; m.add(o); flower.add(m); }
  for (const m of [pirate, top, bow, patch, flower]) { m.visible = false; body.add(m); }
  return { pirate, top, bow, patch, flower };
}""")

# ---- wearing them ----
rep("""  W.hat.visible = !off && look.head === 'hat'; W.halo.visible = !off && look.head === 'halo';""",
"""  W.hat.visible = !off && look.head === 'hat'; W.halo.visible = !off && look.head === 'halo'; W.pirate.visible = !off && look.head === 'pirate'; W.top.visible = !off && look.head === 'tophat';
  W.bow.visible = !off && look.neck === 'bowtie'; W.patch.visible = !off && look.eye === 'patch'; W.flower.visible = !off && look.side === 'flower';""")
rep("  if (!W.bs) { W.bs = new Map(); for (const o of [W.hat, W.halo, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }",
    "  if (!W.bs) { W.bs = new Map(); for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }")
rep("""    const hs = SLIME.headSize(SI) * 1.3; SLIME.headTop(SI, tv3, wearQ);
    if (W.hat.visible) { W.hat.position.copy(tv3).add(tv1.set(0, ((HI ? -0.27 : -0.2) + dropIn + S.b * 0.22) * hs, 0)); W.hat.quaternion.copy(wearQ).multiply(wearQ2.setFromEuler(wearE.set(-0.14 + S.tx * 0.9, 0, -0.16 + S.tz * 0.9))); W.hat.scale.multiplyScalar(hs); W.hat.scale.y *= 1 + S.b * 0.45; const w = 1 - S.b * 0.18; W.hat.scale.x *= w; W.hat.scale.z *= w; }""",
"""    const hs = SLIME.headSize(SI) * 1.3; SLIME.headTop(SI, tv3, wearQ);
    for (const [o, F] of [[W.hat, HAT_FIT.witch], [W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top]]) if (o.visible) { const fy = o === W.hat && !WEAR_A.witch ? (HI ? -0.27 : -0.2) : F.y;
      o.position.copy(tv3).add(tv1.set(0, (fy + dropIn + S.b * 0.22) * hs, 0)); o.quaternion.copy(wearQ).multiply(wearQ2.setFromEuler(wearE.set(F.rx + S.tx * 0.9, 0, F.rz + S.tz * 0.9))); o.scale.multiplyScalar(hs); o.scale.y *= 1 + S.b * 0.45; const w = 1 - S.b * 0.18; o.scale.x *= w; o.scale.z *= w; }
    // on the face and the side of the head (the everyday slime only: the other forms have their own heads): the patch over its right eye,
    // the flower tucked in by its left ear (lower when a hat's brim is over it); and the bow tie under its chin
    const plain = SI.form === 'slime' && !SI.st.formNext, mk = SLIME.headSize(SI) / SLIME.S.meta.slime.head[3];
    if (!plain) { W.patch.visible = W.flower.visible = W.bow.visible = false; }
    if (W.patch.visible || W.flower.visible) { SLIME.headTop(SI, wv1, wq1, 0);
      if (W.patch.visible) { W.patch.position.copy(wv1); W.patch.quaternion.copy(wq1); W.patch.scale.multiplyScalar(mk); }
      if (W.flower.visible) { const F = WEAR_PACK && WEAR_PACK.patch ? (look.head ? WEAR_PACK.patch.flowerLow : WEAR_PACK.patch.flower) : { p: [-0.34, 0.24, 0.1], n: [-0.75, 0.59, 0.29] };
        wv2.set(F.p[0], F.p[1], F.p[2]).multiplyScalar(mk).applyQuaternion(wq1); W.flower.position.copy(wv1).add(wv2);
        wq2.setFromUnitVectors(YAX, wv3.set(F.n[0], F.n[1], F.n[2])); W.flower.quaternion.copy(wq1).multiply(wq2).multiply(wearQ2.setFromAxisAngle(YAX, 0.5 + Math.sin(t * 1.7) * 0.04)); W.flower.scale.multiplyScalar(mk * 0.2 * (1 + 0.04 * Math.sin(t * 2.3))); } }
    if (W.bow.visible && SLIME.bodyPoint(SI, 0, -0.03, 0.835, wv1)) { W.bow.position.copy(wv1); W.bow.quaternion.setFromEuler(wearE.set(-0.12 + S.tx * 0.35, 0, Math.sin(t * 2.1) * 0.05 + S.tz * 0.5)); W.bow.scale.multiplyScalar(mk * 0.4); }""")
# the roller (the old jelly): hats ride its top like the witch hat; the face pieces aren't worn there
rep("""  const fl = rl * (0.36 + Math.sin(t * 2.6) * 0.035); // on the roller, head pieces hover just over its top instead of sinking into it
  if (W.hat.visible) {""",
"""  const fl = rl * (0.36 + Math.sin(t * 2.6) * 0.035); // on the roller, head pieces hover just over its top instead of sinking into it
  W.patch.visible = W.flower.visible = W.bow.visible = false;
  for (const [o, F] of [[W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top]]) if (o.visible) { o.position.copy(gooJS(tv2.set(0, 1, 0), U)).add(tv1.set(0, F.y * 0.8 + dropIn + fl + S.b * 0.22, 0)); o.rotation.set(F.rx * (1 - 0.8 * rl) + S.tx * 0.9, 0, F.rz * (1 - 0.8 * rl) + S.tz * 0.9); }
  if (W.hat.visible) {""")
rep("let wearDt = 0.016; const wearQ = new THREE.Quaternion(), wearQ2 = new THREE.Quaternion(), wearE = new THREE.Euler();",
    "let wearDt = 0.016; const wearQ = new THREE.Quaternion(), wearQ2 = new THREE.Quaternion(), wearE = new THREE.Euler(), wv1 = new THREE.Vector3(), wv2 = new THREE.Vector3(), wv3 = new THREE.Vector3(), wq1 = new THREE.Quaternion(), wq2 = new THREE.Quaternion();")

# ---- the player's own copies fade in with the rest of its accessories ----
rep("pWearParts = [pWear.hat, pWear.halo, ...pWear.horns, ...pWear.wings, ...pWear.fangs];", "pWearParts = [pWear.hat, pWear.halo, pWear.pirate, pWear.top, pWear.bow, pWear.patch, pWear.flower, ...pWear.horns, ...pWear.wings, ...pWear.fangs];")
rep("  for (const w of pWearParts) { if (pWear.wings.includes(w)) w.scale.set(w.userData.sd * WING_K * s, WING_K * s, WING_K * s); else w.scale.setScalar(s); }",
    "  for (const w of pWearParts) w.scale.multiplyScalar(s); // (placed afresh each frame, so this only shrinks them for the moment)")

# ---- the list, your look, rivals ----
rep("const WEAR = [{ id: 'hat', name: 'Witch hat', slot: 'head' }, { id: 'halo', name: 'Halo', slot: 'head' }, { id: 'fangs', name: 'Fangs', slot: 'mouth' }];",
    "const WEAR = [{ id: 'pirate', name: 'Pirate hat', slot: 'head' }, { id: 'tophat', name: 'Top hat', slot: 'head' }, { id: 'patch', name: 'Eye patch', slot: 'eye' }, { id: 'flower', name: 'Flower', slot: 'side' }, { id: 'bowtie', name: 'Bow tie', slot: 'neck' },\n  { id: 'hat', name: 'Witch hat', slot: 'head', season: 1 }, { id: 'halo', name: 'Halo', slot: 'head', season: 1 }, { id: 'fangs', name: 'Fangs', slot: 'mouth', season: 1 }];")
rep("return { eyes: 'round', head: ok(l.head, 'head'), back: ok(l.back, 'back'), mouth: ok(l.mouth, 'mouth') }; })();",
    "return { eyes: 'round', head: ok(l.head, 'head'), back: ok(l.back, 'back'), mouth: ok(l.mouth, 'mouth'), eye: ok(l.eye, 'eye'), side: ok(l.side, 'side'), neck: ok(l.neck, 'neck') }; })();")
rep("LH.wearing = { head: null, back: null, mouth: null }; L2.wearing = { head: null, back: null, mouth: null };",
    "LH.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null }; L2.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null };")
rep("function rollRivalLooks() { const heads = [null, null, 'halo', 'hat']; for (const L of [LH, L2]) L.wearing = { head: heads[Math.random() * heads.length | 0], back: null, mouth: Math.random() < 0.35 ? 'fangs' : null }; }",
    "function rollRivalLooks() { const heads = [null, null, 'halo', 'hat', 'pirate', 'tophat']; for (const L of [LH, L2]) { const head = heads[Math.random() * heads.length | 0]; L.wearing = { head, back: null, mouth: Math.random() < 0.3 ? 'fangs' : null, eye: Math.random() < (head === 'pirate' ? 0.6 : 0.12) ? 'patch' : null, side: Math.random() < 0.15 ? 'flower' : null, neck: Math.random() < (head === 'tophat' ? 0.6 : 0.15) ? 'bowtie' : null }; } }")

# ---- Customize: an Accessories group above this season's ----
rep('<div class="lgroup"><p class="lhead"><span class="sdot" aria-hidden="true"></span>Season 1: Halloween</p><div class="lopts" id="wearOpts" role="group" aria-label="Season 1 accessories"></div></div>',
    '<div class="lgroup"><p class="lhead">Accessories</p><div class="lopts" id="acceOpts" role="group" aria-label="Accessories"></div></div>\n    <div class="lgroup"><p class="lhead"><span class="sdot" aria-hidden="true"></span>Season 1: Halloween</p><div class="lopts" id="wearOpts" role="group" aria-label="Season 1 accessories"></div></div>')
rep("  $('wearOpts').innerHTML = WEAR.map(w => '<button class=\"lopt\" type=\"button\" data-w=\"' + w.id + '\" aria-label=\"' + w.name + '\" title=\"' + w.name + '\" aria-pressed=\"' + (myLook[w.slot] === w.id) + '\"><svg viewBox=\"0 0 40 40\" aria-hidden=\"true\">' + WEAR_ICON[w.id] + '</svg></button>').join('');",
    "  const wBtn = w => '<button class=\"lopt\" type=\"button\" data-w=\"' + w.id + '\" aria-label=\"' + w.name + '\" title=\"' + w.name + '\" aria-pressed=\"' + (myLook[w.slot] === w.id) + '\"><svg viewBox=\"0 0 40 40\" aria-hidden=\"true\">' + WEAR_ICON[w.id] + '</svg></button>';\n  $('acceOpts').innerHTML = WEAR.filter(w => !w.season).map(wBtn).join(''); $('wearOpts').innerHTML = WEAR.filter(w => w.season).map(wBtn).join('');")
rep("$('wearOpts').addEventListener('click', e => { const b = e.target.closest('.lopt'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w); myLook[w.slot] = myLook[w.slot] === w.id ? null : w.id; saveLook(); renderLook(); lookPop(); heroT = 0; if (w.slot === 'back' && myLook.back) shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832 + 2.6; });",
    "const wearPick = e => { const b = e.target.closest('.lopt'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w); myLook[w.slot] = myLook[w.slot] === w.id ? null : w.id; saveLook(); renderLook(); lookPop(); heroT = 0; if (w.slot === 'back' && myLook.back) shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832 + 2.6;\n  if (w.slot === 'side' && myLook.side) shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832 - 0.75; else if (w.slot === 'eye' && myLook.eye) shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832 + 0.35; };\n$('wearOpts').addEventListener('click', wearPick); $('acceOpts').addEventListener('click', wearPick);")
# framing for the taller hats
rep("tall = myLook.head === 'hat' ? 1.25 : myLook.head ? 1.05 : 0.88;", "tall = myLook.head === 'hat' ? 1.25 : myLook.head === 'tophat' ? 1.18 : myLook.head === 'pirate' ? 1.12 : myLook.head ? 1.05 : 0.88;")
rep("ly = myLook.head === 'hat' ? 0.44 : 0.36;", "ly = myLook.head === 'hat' ? 0.44 : myLook.head === 'tophat' || myLook.head === 'pirate' ? 0.41 : 0.36;")

# ---- their icons ----
rep("  hat: '<path d=\"M14 26c3-6 5-13 9-19 1 4 2 9 4 13l-1 6z\" fill=\"#4A3378\"",
    """  pirate: '<path d="M4.5 25.5C7 17 13 13.5 20 13s13 4 15.5 12.5c-4-1.6-9-2.4-15.5-2.4S8.5 24 4.5 25.5z" fill="#221A2C" stroke="#E8B64A" stroke-width="1.8" stroke-linejoin="round"/><circle cx="20" cy="18.6" r="2.4" fill="#F4EEE4"/><path d="M17 21.6l6 2.2M23 21.6l-6 2.2" stroke="#F4EEE4" stroke-width="1.3" stroke-linecap="round"/>',
  tophat: '<path d="M12.5 8.5h15v16h-15z" fill="#221A2C" stroke="#D9C8FF" stroke-width="1.6" stroke-linejoin="round"/><path d="M12.5 20h15v4.5h-15z" fill="#E3283E"/><ellipse cx="20" cy="27" rx="13" ry="3.4" fill="#221A2C" stroke="#D9C8FF" stroke-width="1.6"/>',
  patch: '<path d="M7 12.5l26 11.5" stroke="#D9C8FF" stroke-width="2" stroke-linecap="round"/><path d="M12.5 14.5c4.5-1.6 10.5-.6 11.2 3.8.7 4.4-2.7 9.4-6.8 9.6-4.1.2-7-3.6-7.6-7.4-.3-2.6.9-5.2 3.2-6z" fill="#231A2B" stroke="#D9C8FF" stroke-width="1.6" stroke-linejoin="round"/>',
  flower: '<g transform="translate(20 20)">' + [0, 72, 144, 216, 288].map(a => '<ellipse cx="0" cy="-7.4" rx="5" ry="7.4" transform="rotate(' + a + ')" fill="#FFFFFF" stroke="#D9C8FF" stroke-width="1.2"/>').join('') + '<circle r="4" fill="#FFC23A"/></g>',
  bowtie: '<path d="M20 20l-12.5-7.5v15zM20 20l12.5-7.5v15z" fill="#231A2B" stroke="#D9C8FF" stroke-width="1.6" stroke-linejoin="round"/><rect x="16.6" y="16.4" width="6.8" height="7.2" rx="2.2" fill="#231A2B" stroke="#D9C8FF" stroke-width="1.6"/><circle cx="12" cy="17.5" r="1.2" fill="#F4EEE4"/><circle cx="11.4" cy="22.6" r="1.2" fill="#F4EEE4"/><circle cx="28" cy="17.5" r="1.2" fill="#F4EEE4"/><circle cx="28.6" cy="22.6" r="1.2" fill="#F4EEE4"/>',
  hat: '<path d="M14 26c3-6 5-13 9-19 1 4 2 9 4 13l-1 6z" fill="#4A3378\"""")

# ---- the scoreboard's faces wear them too ----
rep("const c = mixHex(hex, 0, 0), lo = mixHex(hex, 0x0C0620, 0.3), face = mixHex(hex, 0xFFF1E6, 0.42), O = '#0C0620', w = look || {}, hat = w.head === 'hat', halo = w.head === 'halo', fangs = w.mouth === 'fangs';\n  const g = '<g transform=\"translate(0 ' + (hat ? 4 : halo ? 3 : 1) + ')\"';",
    "const c = mixHex(hex, 0, 0), lo = mixHex(hex, 0x0C0620, 0.3), face = mixHex(hex, 0xFFF1E6, 0.42), O = '#0C0620', w = look || {}, hat = w.head === 'hat', halo = w.head === 'halo', fangs = w.mouth === 'fangs', pir = w.head === 'pirate', tph = w.head === 'tophat';\n  const g = '<g transform=\"translate(0 ' + (hat || tph ? 4 : halo || pir ? 3 : 1) + ')\"';")
rep("  if (halo) s += '<ellipse cx=\"24\" cy=\"6.6\" rx=\"8.6\" ry=\"2.7\" fill=\"none\" stroke=\"' + O + '\" stroke-width=\"4.6\"/><ellipse cx=\"24\" cy=\"6.6\" rx=\"8.6\" ry=\"2.7\" fill=\"none\" stroke=\"#FFD86B\" stroke-width=\"2.2\"/>';",
    """  if (halo) s += '<ellipse cx="24" cy="6.6" rx="8.6" ry="2.7" fill="none" stroke="' + O + '" stroke-width="4.6"/><ellipse cx="24" cy="6.6" rx="8.6" ry="2.7" fill="none" stroke="#FFD86B" stroke-width="2.2"/>';
  if (w.eye === 'patch') s += '<path d="M15 16.5l18 6" stroke="' + O + '" stroke-width="1.6" stroke-linecap="round"/><path d="M25.2 21c2.6-1 5.6 0 5.8 2.6.2 2.6-1.6 5-3.8 5-2.2 0-3.8-1.8-4-3.8-.2-1.6.6-3.2 2-3.8z" fill="#231A2B" stroke="' + O + '" stroke-width="1.2"/>';
  if (w.side === 'flower') s += '<g transform="translate(13.4 15.2)" stroke="' + O + '" stroke-width="0.9">' + [0, 72, 144, 216, 288].map(a => '<ellipse cx="0" cy="-2.6" rx="1.9" ry="2.6" transform="rotate(' + a + ')" fill="#FFFFFF"/>').join('') + '<circle r="1.5" fill="#FFC23A"/></g>';
  if (w.neck === 'bowtie') s += '<g stroke="' + O + '" stroke-width="1.2" stroke-linejoin="round"><path d="M24 36.6l-5.6-3.2v6.4zM24 36.6l5.6-3.2v6.4z" fill="#231A2B"/><rect x="22.4" y="35" width="3.2" height="3.2" rx="1" fill="#231A2B"/></g>';
  if (pir) s += '<g stroke="' + O + '" stroke-width="2" stroke-linejoin="round"><path d="M8.5 15.5C11 8 17 5 24 5s13 3 15.5 10.5c-4.4-1.6-9.6-2.2-15.5-2.2S12.9 13.9 8.5 15.5z" fill="#221A2C"/></g><path d="M10.4 14.4C15 12.8 19.4 12.4 24 12.4s9 .4 13.6 2" fill="none" stroke="#E8B64A" stroke-width="1.3"/><circle cx="24" cy="9.2" r="1.7" fill="#F4EEE4"/>';
  if (tph) s += '<g stroke="' + O + '" stroke-width="2" stroke-linejoin="round"><path d="M17 0.5h14v13H17z" fill="#221A2C"/><ellipse cx="24" cy="14.2" rx="11.6" ry="2.8" fill="#221A2C"/></g><path d="M17.9 10.2h12.2v2.6H17.9z" fill="#E3283E"/>';""")
open(P, 'w').write(src)
print('ok', len(src))
