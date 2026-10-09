# Paint on walls: every splash up a wall is a thick, glossy splat cut from a painted atlas (four shapes with flecks), its edge rounded up
# like real paint, and drips that run down from it over a second or two after it lands. Splashes on canopies and other steep-up surfaces
# skip the drips. Visual only, as before.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

i = s.index("const splG = (() => {"); j = s.index("splIM.instanceColor = new THREE.BufferAttribute(new Float32Array(SPL_MAX * 3), 3); splIM.instanceColor.setUsage(THREE.DynamicDrawUsage); scene.add(splIM);")
j2 = j + len("splIM.instanceColor = new THREE.BufferAttribute(new Float32Array(SPL_MAX * 3), 3); splIM.instanceColor.setUsage(THREE.DynamicDrawUsage); scene.add(splIM);")
s = s[:i] + r"""// the atlas: four splats in a 2x2 grid. Each cell: a lumpy blob with arms and flecks near the top, drips below it. Color is white (the
// instance color tints it), alpha is the shape, height is how far in from the edge (so the edge rounds up), aux R is how far down a drip
// a pixel is (0 in the blob), aux G its gloss
const SPLAT = (() => {
  const S = 1024, C = 512, mk = () => { const c = document.createElement('canvas'); c.width = c.height = S; return c; };
  const mask = mk(), aux = mk(), col = mk(), mg = mask.getContext('2d'), ag = aux.getContext('2d'), cg = col.getContext('2d'), R = rng(4242), DMAX = 340;
  mg.fillStyle = '#000'; mg.fillRect(0, 0, S, S); ag.fillStyle = 'rgb(0,140,0)'; ag.fillRect(0, 0, S, S); cg.fillStyle = '#fff'; cg.fillRect(0, 0, S, S);
  for (let k = 0; k < 4; k++) {
    const ox = (k % 2) * C, oy = (k >> 1) * C, cx = ox + 256, cy = oy + 160, R0 = 104 + R() * 22, f1 = R() * 6.28, f2 = R() * 6.28, arms = [];
    for (let a = 0; a < 3 + (R() * 3 | 0); a++) arms.push([R() * 6.2832, 0.18 + R() * 0.3, 0.12 + R() * 0.1]);
    const rad = th => { let r = 1 + 0.1 * Math.sin(th * 5 + f1) + 0.05 * Math.sin(th * 11 + f2) + 0.03 * Math.sin(th * 23 + f1 * 2); for (const [aa, len, wd] of arms) { const d = Math.atan2(Math.sin(th - aa), Math.cos(th - aa)); r += len * Math.exp(-(d * d) / (wd * wd)); } return R0 * r; };
    mg.fillStyle = '#fff'; mg.beginPath(); for (let i = 0; i <= 96; i++) { const th = i / 96 * 6.2832, r = rad(th); i ? mg.lineTo(cx + Math.cos(th) * r, cy + Math.sin(th) * r) : mg.moveTo(cx + Math.cos(th) * r, cy + Math.sin(th) * r); } mg.closePath(); mg.fill();
    for (let i = 0; i < 7 + (R() * 7 | 0); i++) { const th = R() * 6.2832, d = rad(th) * (1.12 + R() * 0.5), r = 4 + R() * 11; if (Math.sin(th) > 0.55 && R() < 0.6) continue; const x = cx + Math.cos(th) * d, y = cy + Math.sin(th) * d; if (x < ox + 14 || x > ox + C - 14 || y < oy + 10) continue; mg.beginPath(); mg.arc(x, y, r, 0, 6.2832); mg.fill(); }
    // drips: from the lower half of the blob, straight down with a slight wander, a little narrower as they go, a bead at the end
    const nd = 2 + (R() * 3 | 0);
    for (let i = 0; i < nd; i++) {
      const th = Math.PI * (0.18 + 0.64 * (i + 0.2 + R() * 0.6) / nd), r0 = rad(th) * 0.7, x0 = cx + Math.cos(th) * r0, y0 = cy + Math.sin(th) * r0, len = (90 + R() * 240) * (0.55 + 0.45 * Math.sin(th)), w0 = 10 + R() * 9;
      const steps = 16, pts = []; let x = x0; for (let t = 0; t <= steps; t++) { x += (R() - 0.5) * 2.2; pts.push([x, y0 + len * t / steps]); }
      for (let t = 0; t < steps; t++) { const w = w0 * (1 - 0.3 * t / steps); mg.lineWidth = w; mg.lineCap = 'round'; mg.strokeStyle = '#fff'; mg.beginPath(); mg.moveTo(pts[t][0], pts[t][1]); mg.lineTo(pts[t + 1][0], pts[t + 1][1]); mg.stroke();
        const v0 = Math.round(255 * Math.max(0, (pts[t][1] - y0 - r0 * 0.25)) / DMAX), v1 = Math.round(255 * Math.max(0, (pts[t + 1][1] - y0 - r0 * 0.25)) / DMAX), gr = ag.createLinearGradient(0, pts[t][1], 0, pts[t + 1][1]);
        gr.addColorStop(0, `rgb(${v0},140,0)`); gr.addColorStop(1, `rgb(${v1},140,0)`); ag.strokeStyle = gr; ag.lineWidth = w + 4; ag.lineCap = 'round'; ag.beginPath(); ag.moveTo(pts[t][0], pts[t][1]); ag.lineTo(pts[t + 1][0], pts[t + 1][1]); ag.stroke(); }
      const e = pts[steps], br = w0 * 0.55; mg.beginPath(); mg.arc(e[0], e[1] + br * 0.2, br, 0, 6.2832); mg.fill();
      const ve = Math.min(255, Math.round(255 * (e[1] + br * 1.2 - y0 - r0 * 0.25) / DMAX)); ag.fillStyle = `rgb(${ve},140,0)`; ag.beginPath(); ag.arc(e[0], e[1] + br * 0.2, br + 2, 0, 6.2832); ag.fill();
    }
    // the blob itself has no drip distance
    ag.fillStyle = 'rgb(0,120,0)'; ag.beginPath(); for (let i = 0; i <= 96; i++) { const th = i / 96 * 6.2832, r = rad(th) + 3; i ? ag.lineTo(cx + Math.cos(th) * r, cy + Math.sin(th) * r) : ag.moveTo(cx + Math.cos(th) * r, cy + Math.sin(th) * r); } ag.closePath(); ag.fill();
  }
  // height: distance in from the edge (two-pass chamfer), rounded over the first few pixels, a touch thicker toward each blob's middle
  const md = mg.getImageData(0, 0, S, S).data, D = new Float32Array(S * S);
  for (let i = 0; i < S * S; i++) D[i] = md[i * 4] > 127 ? 1e4 : 0;
  for (let y = 1; y < S; y++) for (let x = 1; x < S - 1; x++) { const i = y * S + x; if (!D[i]) continue; D[i] = Math.min(D[i], D[i - 1] + 1, D[i - S] + 1, D[i - S - 1] + 1.414, D[i - S + 1] + 1.414); }
  for (let y = S - 2; y >= 0; y--) for (let x = S - 2; x > 0; x--) { const i = y * S + x; if (!D[i]) continue; D[i] = Math.min(D[i], D[i + 1] + 1, D[i + S] + 1, D[i + S + 1] + 1.414, D[i + S - 1] + 1.414); }
  const hc = mk(), hg2 = hc.getContext('2d'), him = hg2.createImageData(S, S), hd = him.data;
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) { const i = y * S + x, k = ((y >> 9) << 1) + (x >> 9), cx = (k % 2) * C + 256, cy = (k >> 1) * C + 160, rr = Math.hypot(x - cx, y - cy) / 140, e = Math.min(1, D[i] / 9), v = D[i] ? (Math.sqrt(1 - (1 - e) * (1 - e)) * 0.78 + 0.16 * Math.max(0, 1 - rr)) : 0, n = Math.round(v * 255), o = i * 4; hd[o] = hd[o + 1] = hd[o + 2] = n; hd[o + 3] = 255; }
  hg2.putImageData(him, 0, 0);
  const map = cutTex(col, mask), auxT = texOf(aux, false); auxT.wrapS = auxT.wrapT = THREE.ClampToEdgeWrapping;
  const nrm = HI ? heightNormal(hc, 3.2) : null; if (nrm) nrm.wrapS = nrm.wrapT = THREE.ClampToEdgeWrapping;
  return { map, aux: auxT, nrm };
})();
// the splat card: blob center at the origin, drips hanging below
const splG = new THREE.PlaneGeometry(2, 2).translate(0, -0.375, 0);
const SPLU = { uTime: { value: 0 }, uAux: { value: SPLAT.aux } };
const splMat = HI ? new THREE.MeshStandardMaterial({ color: 0xFFFFFF, map: SPLAT.map, normalMap: SPLAT.nrm, normalScale: new THREE.Vector2(1, 1), roughness: 0.2, metalness: 0, envMapIntensity: 1.25, alphaTest: 0.5, alphaToCoverage: true, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 })
  : toon(0xFFFFFF, { map: SPLAT.map, alphaTest: 0.5, alphaToCoverage: true, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4 });
splMat.onBeforeCompile = sh => {
  if (HI) aoHook(sh);
  sh.uniforms.uTime = SPLU.uTime; sh.uniforms.uAux = SPLU.uAux;
  sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nattribute vec3 aSpl; varying vec3 vSpl;')
    .replace('#include <uv_vertex>', '#include <uv_vertex>\nvSpl = aSpl; { vec2 o = vec2(mod(aSpl.x, 2.0) * 0.5, 0.5 - floor(aSpl.x / 2.0) * 0.5); vMapUv = uv * 0.5 + o;\n#ifdef USE_NORMALMAP\nvNormalMapUv = vMapUv;\n#endif\n}');
  sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform float uTime; uniform sampler2D uAux; varying vec3 vSpl;')
    .replace('#include <map_fragment>', '#include <map_fragment>\n{ float dd = texture2D(uAux, vMapUv).r, g = clamp((uTime - vSpl.y) * 0.5, 0.0, 1.0); g = 1.0 - (1.0 - g) * (1.0 - g); if (dd > 0.004 && (vSpl.z < 0.5 || dd > g)) discard; }');
};
const splIM = new THREE.InstancedMesh(splG, splMat, SPL_MAX);
const splInfo = new THREE.InstancedBufferAttribute(new Float32Array(SPL_MAX * 3), 3); splInfo.setUsage(THREE.DynamicDrawUsage); splG.setAttribute('aSpl', splInfo);
splIM.count = 0; splIM.frustumCulled = false; splIM.receiveShadow = true; splIM.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
splIM.instanceColor = new THREE.BufferAttribute(new Float32Array(SPL_MAX * 3), 3); splIM.instanceColor.setUsage(THREE.DynamicDrawUsage); scene.add(splIM);""" + s[j2:]

# both placers record which splat, when it landed, and whether it may drip
rep("""  splIM.setMatrixAt(i, splDummy.matrix); splTeam[i] = t; splCol(t).toArray(splIM.instanceColor.array, i * 3);
  splIM.count = splN; splIM.instanceMatrix.needsUpdate = true; splIM.instanceColor.needsUpdate = true;
}
function putSplashN(""", """  splIM.setMatrixAt(i, splDummy.matrix); splTeam[i] = t; splCol(t).toArray(splIM.instanceColor.array, i * 3);
  splInfo.setXYZ(i, (Math.random() * 4) | 0, clock - Math.random() * 0.15, 1); splInfo.needsUpdate = true;
  splIM.count = splN; splIM.instanceMatrix.needsUpdate = true; splIM.instanceColor.needsUpdate = true;
}
function putSplashN(""")
rep("""  splIM.setMatrixAt(i, splDummy.matrix); splTeam[i] = t; splCol(t).toArray(splIM.instanceColor.array, i * 3);
  splIM.count = splN; splIM.instanceMatrix.needsUpdate = true; splIM.instanceColor.needsUpdate = true;
}
function recolorSplashes()""", """  splIM.setMatrixAt(i, splDummy.matrix); splTeam[i] = t; splCol(t).toArray(splIM.instanceColor.array, i * 3);
  splInfo.setXYZ(i, (Math.random() * 4) | 0, clock - Math.random() * 0.15, Math.abs(ny) < 0.45 ? 1 : 0); splInfo.needsUpdate = true;
  splIM.count = splN; splIM.instanceMatrix.needsUpdate = true; splIM.instanceColor.needsUpdate = true;
}
function recolorSplashes()""")
rep("  glowBatch.mat.uniforms.uTime.value = clock;", "  glowBatch.mat.uniforms.uTime.value = clock; SPLU.uTime.value = clock;")
open(p, 'w').write(s)
print('ok')
