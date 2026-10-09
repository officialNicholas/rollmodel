# The paint bucket, rebuilt: a pressed-tin pail with rolled rims and two ribs, a bright striped paint label, riveted ears and a wire
# handle that swings on them, the lid leaning on its side with a splash of paint on it, glossy drips over the lip and a little spill at
# its foot. The paint inside is its own surface now: it ripples, sloshes when someone hops in (and the handle swings, the lid jiggles),
# and bubbles while someone's soaking it up. The coffins share the sloshing paint.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

i = s.index("const PCAN = (() => {"); j = s.index("function makeCoffin(x, y, z, seed) {")
s = s[:i] + r"""const PCAN = (() => {
  const seg = HI ? 72 : 32, V2 = (x, y) => new THREE.Vector2(x, y), R = CAN_R, H = CAN_H;
  // the tin: from the foot (a rolled bead) up a slightly flared wall with two pressed ribs, over the rolled lip, down inside to the floor
  const prof = [[R - 0.02, 0], [R + 0.006, 0.004], [R + 0.02, 0.018], [R + 0.022, 0.034], [R + 0.01, 0.048], [R + 0.004, 0.06], [R + 0.006, 0.104], [R + 0.017, 0.114], [R + 0.008, 0.126], [R + 0.008, 0.14],
    [R + 0.012, 0.35], [R + 0.012, 0.362], [R + 0.023, 0.372], [R + 0.013, 0.384], [R + 0.014, H - 0.046], [R + 0.03, H - 0.026], [R + 0.039, H - 0.006], [R + 0.035, H + 0.012], [R + 0.019, H + 0.022], [R, H + 0.018], [R - 0.022, H + 0.004],
    [R - 0.03, H - 0.02], [R - 0.03, 0.07], [0.001, 0.07]];
  const wall = new THREE.LatheGeometry(prof.map(q => V2(q[0], q[1])), seg);
  // riveted ears either side, the handle's pivots
  const EAR_Y = H - 0.085, ears = [-1, 1].map(sd => new THREE.CylinderGeometry(0.036, 0.04, 0.024, 16).rotateZ(Math.PI / 2).translate(sd * (R + 0.026), EAR_Y, 0));
  const rivets = [-1, 1].map(sd => new THREE.SphereGeometry(0.016, 10, 8).translate(sd * (R + 0.04), EAR_Y, 0));
  const cM = new THREE.Color(0xCDD5E2), cD = new THREE.Color(0x8C96A8), ni = g => g.index ? g.toNonIndexed() : g;
  const parts = [[ni(wall), cM], ...ears.map(g => [ni(g), cD]), ...rivets.map(g => [ni(g), cD])];
  let n = 0; for (const [g] of parts) n += g.attributes.position.count;
  const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), col = new Float32Array(n * 3); let o = 0;
  for (const [g, c] of parts) { const k = g.attributes.position.count; pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3); for (let q = 0; q < k; q++) { col[(o + q) * 3] = c.r; col[(o + q) * 3 + 1] = c.g; col[(o + q) * 3 + 2] = c.b; } o += k; }
  const body = new THREE.BufferGeometry(); body.setAttribute('position', new THREE.BufferAttribute(pos, 3)); body.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); body.setAttribute('color', new THREE.BufferAttribute(linArr(col), 3));
  // the label, between the ribs
  const label = new THREE.CylinderGeometry(R + 0.015, R + 0.013, 0.205, seg, 1, true).translate(0, 0.244, 0);
  // the wire handle: an arc from ear to ear, pivoting on them (its own mesh, so it can swing)
  const bail = new THREE.TorusGeometry(R + 0.052, 0.012, HI ? 10 : 6, HI ? 56 : 24, Math.PI);
  // the lid: a pressed disc with a groove round it, leaning on the bucket's side
  const lidM = new THREE.Matrix4().compose(new THREE.Vector3(R + 0.14, 0.3, 0.05), new THREE.Quaternion().setFromEuler(new THREE.Euler(0.12, 0.2, -1.22)), new THREE.Vector3(1, 1, 1));
  const lid = new THREE.LatheGeometry([[0.001, 0.034], [R * 0.55, 0.033], [R - 0.05, 0.026], [R - 0.038, 0.038], [R - 0.012, 0.043], [R + 0.02, 0.041], [R + 0.046, 0.03], [R + 0.048, 0.006], [R + 0.034, -0.01], [R - 0.02, -0.012], [0.001, -0.012]].map(q => V2(q[0], q[1])), seg);
  // a splash of paint on the lid, a lumpy round blob
  const smear = (() => { const g = new THREE.CircleGeometry(1, 40), P = g.attributes.position, r = rng(77); const f = []; for (let k = 0; k < 4; k++) f.push([1 + r() * 4 | 0, r() * 6.28, 0.05 + r() * 0.1]);
    for (let q = 1; q < P.count; q++) { const x = P.getX(q), y = P.getY(q), a = Math.atan2(y, x); let k = 1; for (const [m, ph, am] of f) k += am * Math.sin(a * m + ph); P.setXY(q, x * k * R * 0.5, y * k * R * 0.5); }
    g.rotateX(-Math.PI / 2); g.translate(0.04, 0.036, -0.02); return g; })();
  const hull = mergeGeos([new THREE.CylinderGeometry(R * 1.1, R * 1.1, H + 0.07, 30, 1, true).translate(0, (H + 0.07) / 2 - 0.02, 0), new THREE.CylinderGeometry(R + 0.07, R + 0.07, 0.1, 30).applyMatrix4(lidM)]);
  // the paint's surface: rings of vertices so it can ripple
  const surf = new THREE.RingGeometry(0.0, R - 0.028, HI ? 56 : 28, HI ? 7 : 3).rotateX(-Math.PI / 2);
  return { body, label, bail, EAR_Y, lid, lidM, smear, hull, surf, floor: new THREE.CircleGeometry(R - 0.03, 30).rotateX(-Math.PI / 2) };
})();
// the label: a cream band, drippy stripes in every paint, a little splat badge
const canLabelTex = (() => { const W = 1024, H = 256, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const g = cv.getContext('2d'), r = rng(515);
  g.fillStyle = '#FFF4DE'; g.fillRect(0, 0, W, H);
  const cols = ['#E3122F', '#FF6A1A', '#FFD23F', '#3DDC84', '#2E9BFF', '#8B3DFF'], bh = 24, y0 = 62;
  cols.forEach((c, k) => { const y = y0 + k * bh; g.fillStyle = c; g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= W; x += 16) g.lineTo(x, y + Math.sin(x / W * 6.2832 * 3 + k) * 4); for (let x = W; x >= 0; x -= 16) g.lineTo(x, y + bh + Math.sin(x / W * 6.2832 * 3 + k + 0.6) * 4); g.closePath(); g.fill(); });
  // drips off the bottom stripe
  g.fillStyle = cols[5]; for (let k = 0; k < 14; k++) { const x = r() * W, w = 8 + r() * 12, len = 10 + r() * 34, yb = y0 + 6 * bh - 2; g.beginPath(); g.moveTo(x - w / 2, yb); g.lineTo(x - w / 2, yb + len); g.arc(x, yb + len, w / 2, Math.PI, 0, true); g.lineTo(x + w / 2, yb); g.fill(); }
  // badges: a white splat with a paint drop in it, twice round the tin
  for (const cx of [W * 0.25, W * 0.75]) { g.fillStyle = '#FFFFFF'; g.beginPath(); for (let k = 0; k <= 48; k++) { const a = k / 48 * 6.2832, rr = 58 + 9 * Math.sin(a * 7 + cx) + 5 * Math.sin(a * 3); g.lineTo(cx + Math.cos(a) * rr, 128 + Math.sin(a) * rr); } g.fill(); g.lineWidth = 6; g.strokeStyle = '#2A1840'; g.stroke();
    g.fillStyle = '#E3122F'; g.beginPath(); g.moveTo(cx, 86); g.bezierCurveTo(cx + 30, 122, cx + 34, 150, cx, 162); g.bezierCurveTo(cx - 34, 150, cx - 30, 122, cx, 86); g.fill(); g.stroke(); g.fillStyle = 'rgba(255,255,255,0.75)'; g.beginPath(); g.ellipse(cx - 9, 138, 6, 11, -0.4, 0, 6.2832); g.fill(); }
  g.fillStyle = '#2A1840'; g.fillRect(0, 0, W, 7); g.fillRect(0, H - 7, W, 7);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = THREE.RepeatWrapping; t.anisotropy = 4; return t; })();
const canMat = toon(0xFFFFFF, { vertexColors: true }, { roughness: 0.28, metalness: 0.78 }), canLabelMat = toon(0xFFFFFF, { map: canLabelTex }, { roughness: 0.42 }), canWireMat = toon(0x8C96A8, null, { roughness: 0.3, metalness: 0.85 });
// drips over the lip and down the side: thick where they leave the rim, a bead at the end; and a little spill at the foot
const canDrips = seed => { const r = rng(seed), list = []; for (let k = 0; k < 5; k++) { const a = r() * 6.2832, c = Math.cos(a), s2 = Math.sin(a), len = 0.07 + r() * 0.24, rw = CAN_R + 0.03;
    list.push(new THREE.CylinderGeometry(0.03, 0.022, len, 10).translate(c * rw, -len / 2, s2 * rw), new THREE.SphereGeometry(0.036, 12, 10).scale(1, 1.25, 1).translate(c * rw, -len - 0.01, s2 * rw), new THREE.SphereGeometry(0.042, 12, 8).scale(1.3, 0.6, 1.3).translate(c * (CAN_R + 0.018), 0.012, s2 * (CAN_R + 0.018))); }
  return mergeGeos(list); };
const canSpill = seed => { const r = rng(seed + 5), g = new THREE.CircleGeometry(1, 36), P = g.attributes.position, f = [[3, r() * 6, 0.18], [5, r() * 6, 0.1], [2, r() * 6, 0.14]];
  for (let q = 1; q < P.count; q++) { const x = P.getX(q), y = P.getY(q), a = Math.atan2(y, x); let k = 1; for (const [m, ph, am] of f) k += am * Math.sin(a * m + ph); P.setXY(q, x * k * 0.3, y * k * 0.3); }
  g.rotateX(-Math.PI / 2); const a = r() * 6.28; g.translate(Math.cos(a) * (CAN_R + 0.12), 0.006, Math.sin(a) * (CAN_R + 0.12)); return g; };
// paint that ripples, and sloshes when something lands in it (uSlosh, set per bucket); the coffins' blood uses it too
const PAINT_WAVE = `float pw(vec2 p){ float r = length(p); return 0.005 * sin(r * 26.0 - uTime * 3.2 + uPh) + uSlosh * (0.05 * (p.x * cos(uTime * 7.0 + uPh) + p.y * sin(uTime * 7.0 + uPh)) + 0.02 * sin(r * 30.0 - uTime * 13.0)); }`;
function paintSurf(m, seed) {
  const U = { uSlosh: { value: 0 }, uPh: { value: (seed || 0) * 1.7 } }; m.userData.wave = U;
  m.onBeforeCompile = sh => { Object.assign(sh.uniforms, U); sh.uniforms.uTime = paintUniforms.uTime;
    sh.vertexShader = 'uniform float uTime, uSlosh, uPh;\n' + PAINT_WAVE + '\n' + sh.vertexShader.replace('#include <beginnormal_vertex>', '#include <beginnormal_vertex>\n{ float e = 0.02, h0 = pw(position.xz); objectNormal = normalize(vec3(-(pw(position.xz + vec2(e, 0.0)) - h0) / e, 1.0, -(pw(position.xz + vec2(0.0, e)) - h0) / e)); }').replace('#include <begin_vertex>', '#include <begin_vertex>\ntransformed.y += pw(position.xz);'); };
  m.customProgramCacheKey = () => 'paint-surf-' + m.type; return m;
}
const CAN_BUB_G = new THREE.SphereGeometry(0.045, 12, 8, 0, 6.2832, 0, Math.PI / 2);
function makePaintCan(x, y, z, seed) {
  const g = new THREE.Group(), inner = new THREE.Group(); g.add(inner);
  const bm = toon(C.velvet), tm = toon(C.ink, null, { roughness: 0.22 }), lm = paintSurf(toon(C.ink, null, { roughness: 0.1 }), seed);
  const w = new THREE.Mesh(PCAN.body, canMat); w.castShadow = true; inner.add(w);
  const lb = new THREE.Mesh(PCAN.label, canLabelMat); lb.rotation.y = rng(seed)() * 6.28; inner.add(lb);
  const lidG = new THREE.Group(); inner.add(lidG); const lid = new THREE.Mesh(PCAN.lid, canMat); lid.castShadow = true; lid.applyMatrix4(PCAN.lidM); lidG.add(lid); const sm = new THREE.Mesh(PCAN.smear, tm); sm.applyMatrix4(PCAN.lidM); lidG.add(sm);
  const bail = new THREE.Group(); bail.position.y = PCAN.EAR_Y; bail.rotation.x = -1.32; inner.add(bail); bail.add(new THREE.Mesh(PCAN.bail, canWireMat));
  inner.add(new THREE.Mesh(PCAN.hull, outlineMat));
  const fl = new THREE.Mesh(PCAN.floor, bm); fl.position.y = 0.072; inner.add(fl);
  const liq = new THREE.Mesh(PCAN.surf, lm); liq.position.y = 0.3; inner.add(liq);
  const bubs = []; for (let k = 0; k < 5; k++) { const b = new THREE.Mesh(CAN_BUB_G, tm); b.visible = false; liq.add(b); bubs.push({ m: b, t: Math.random(), dur: 0.5 + Math.random() * 0.4 }); }
  const drips = new THREE.Mesh(canDrips(seed), tm); drips.position.y = CAN_H + 0.01; inner.add(drips);
  const spill = new THREE.Mesh(canSpill(seed), tm); spill.renderOrder = 2; inner.add(spill);
  const ring = new THREE.Mesh(ringG, potRingMat()); ring.rotation.x = -Math.PI / 2; ring.position.y = 0.07; ring.renderOrder = 3; g.add(ring);
  g.position.set(x, y, z); g.rotation.y = rng(seed + 3)() * 6.28; scene.add(g);
  return { g, inner, bm, tm, lm, liq, drips, spill, bubs, bail, lidG, ring, x, y, z, bA: 0, bV: 0, lastB: 0, slosh: 0 };
}
""" + s[j:]
# the coffins' blood sloshes too
rep("  const liq = new THREE.Mesh(cofFloorG, tm); liq.position.y = 0.3; liq.scale.set(1.01, 1, 1.01); inner.add(liq);",
    "  const lm = paintSurf(toon(C.ink, null, { roughness: 0.14 }), seed), liq = new THREE.Mesh(cofFloorG, lm); liq.position.y = 0.3; liq.scale.set(1.01, 1, 1.01); inner.add(liq);")
rep("  return { g, inner, bm, tm, liq, drips, ring, x, y, z };\n}\n// boiling water",
    "  return { g, inner, bm, tm, lm, liq, drips, ring, x, y, z, bA: 0, bV: 0, lastB: 0, slosh: 0 };\n}\n// boiling water")
# the animation, each frame
rep("    p.bm.color.copy(CAN_EMPTY).lerp(CAN_INK, p.ink); p.tm.color.copy(CAN_EMPTY_TOP).lerp(CAN_INK_TOP, p.ink);",
    """    p.bm.color.copy(CAN_EMPTY).lerp(CAN_INK, p.ink); p.tm.color.copy(CAN_EMPTY_TOP).lerp(CAN_INK_TOP, p.ink); if (p.lm) p.lm.color.copy(p.tm.color);
    // a landing (or a leap out) sloshes the paint, swings the handle and jiggles the lid; it all settles back
    if (bo > p.lastB + 0.05) { p.slosh = Math.min(1.2, p.slosh + 0.9); p.bV += (Math.random() < 0.5 ? -1 : 1) * (4 + Math.random() * 3); } p.lastB = bo;
    p.slosh = Math.max(draining ? 0.25 : 0, p.slosh - rdt * 1.3); if (p.lm) p.lm.userData.wave.uSlosh.value = p.slosh;
    if (p.bail) { p.bV += (-46 * p.bA - 2.6 * p.bV) * Math.min(rdt, 0.05); p.bA += p.bV * Math.min(rdt, 0.05); p.bail.rotation.x = -1.32 + p.bA + (draining ? Math.sin(clock * 22) * 0.04 : 0); p.lidG.rotation.z = Math.sin(bo * 26) * bo * 0.06; }
    // bubbles while someone soaks it up (and now and then on their own), each swelling and popping on the surface
    if (p.bubs) for (const b of p.bubs) { b.t += rdt / b.dur * (draining ? 1 : 0.12); if (b.t >= 1) { b.t -= 1; const a = Math.random() * 6.28, rr = Math.random() * (CAN_R - 0.12); b.m.position.set(Math.cos(a) * rr, 0, Math.sin(a) * rr); b.dur = 0.35 + Math.random() * 0.4; }
      const k = b.t < 0.8 ? b.t / 0.8 : 0; b.m.visible = p.ink > 0.05 && k > 0.02; b.m.scale.setScalar(0.3 + 0.9 * k); }
    if (p.spill) p.spill.scale.set(0.4 + 0.6 * p.ink, 1, 0.4 + 0.6 * p.ink);""")
open(p, 'w').write(s)
print('ok')
