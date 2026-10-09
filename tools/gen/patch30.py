import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)
def between(a, b, new):
    global s
    i = s.index(a); j = s.index(b, i)
    s = s[:i] + new + s[j:]

# ================= 1) paint shader: blobby noise edges, pooled color, and the expensive crack pattern only where paint is drying =================
rep("void main(){ vWet = wetness(birth); vEdge = edge; vTeam = team; vN = normal; vec3 p = position + normal * (0.024 * clamp(vWet, 0.0, 1.0)); vec4 w = modelMatrix * vec4(p, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;",
    "void main(){ vWet = wetness(birth); vEdge = edge; vTeam = team; vN = vec3(0.0, 1.0, 0.0); vec3 p = position + vec3(0.0, 0.024 * clamp(vWet, 0.0, 1.0), 0.0); vec4 w = modelMatrix * vec4(p, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;")
between("void main(){\n  vec2 c = cell(vW * 2.2);", "  gl_FragColor = vec4(col * lit, dilA);\n}`;", """float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(h2(i), h2(i + vec2(1.0, 0.0)), f.x), mix(h2(i + vec2(0.0, 1.0)), h2(i + vec2(1.0, 1.0)), f.x), f.y); }
void main(){
  // ragged, blobby edges from two octaves of noise, so no two rims look alike
  float nz = vnoise(vW.xz * 1.6) * 0.62 + vnoise(vW.xz * 4.1 + 7.3) * 0.38;
  float lim = 0.78 + 0.18 * nz;
  if (vEdge > lim) discard;
  float border = smoothstep(lim - 0.16, lim, vEdge);
  vec3 n = vec3(0.0, 1.0, 0.0), L = normalize(uLight), V = normalize(cameraPosition - vW);
  float ndl = dot(n, L); float lit = ndl > 0.35 ? 1.0 : (ndl > 0.0 ? 0.9 : 0.8);
  float wetK = clamp(vWet, 0.0, 1.0), oldK = clamp(-vWet, 0.0, 1.0);
  float tm = mod(vTeam + 0.25, 2.0), dilA = vTeam > 1.5 ? 0.5 : 1.0;
  vec3 wetC = tm < 0.75 ? uWetA[0] : uWetA[1];
  vec3 dryC = tm < 0.75 ? uDryA[0] : uDryA[1];
  // wet: thick glossy blood with a slowly drifting, rippled surface, deeper pools and thinner spots, and small sparkles
  vec3 q = vW * 3.4 + vec3(uTime * 0.3, uTime * 0.2, -uTime * 0.25);
  vec3 rip = vec3(sin(q.x * 1.3 + 2.0 * sin(q.z * 0.7)), sin(q.y * 1.1 + 2.2 * sin(q.x * 0.9)), sin(q.z * 1.2 + 1.8 * sin(q.y * 1.4)));
  vec3 q2 = vW * 9.0 + vec3(-uTime * 0.5, uTime * 0.4, uTime * 0.45);
  rip += 0.45 * vec3(sin(q2.z + sin(q2.y * 1.3)), sin(q2.x * 1.1 + sin(q2.z)), sin(q2.y * 0.9 + sin(q2.x * 1.2)));
  vec3 nb = normalize(n + (rip - n * dot(n, rip)) * 0.22), H = normalize(L + V);
  float sp = pow(max(dot(nb, H), 0.0), 260.0);
  float sparkle = step(0.8, sp) * 0.5, soft = pow(max(dot(nb, H), 0.0), 28.0) * 0.12, fres = pow(1.0 - max(dot(nb, V), 0.0), 3.0) * 0.28;
  float pool = vnoise(vW.xz * 0.6 + 3.3) * 0.7 + vnoise(vW.xz * 1.9 - 5.1) * 0.3;
  vec3 wet = wetC * (0.8 + 0.22 * pool + 0.12 * dot(nb, L)) * (1.0 - 0.3 * border) + vec3(sparkle + soft + fres);
  float drying = (1.0 - wetK) * step(0.0001, vWet);
  wet *= 1.0 - 0.14 * drying * (0.5 + 0.5 * sin(uTime * 16.0));
  vec3 col = wet;
  if (wetK < 0.999) {
    // hard: matte watercolor soaked into the canvas, weave showing through, pigment pooled at the edge, hairline cracks
    vec2 c = cell(vW * 2.2);
    vec3 weave = texture2D(uCanvas, vec2(vW.x, -vW.z) * 0.5).rgb / vec3(0.965, 0.945, 0.9);
    float gran = fract(sin(dot(floor(vW.xz * 16.0), vec2(12.9898, 78.233))) * 43758.5453);
    float bloom = 0.5 + 0.25 * (sin(vW.x * 1.7 + sin(vW.z * 1.3)) + sin(vW.z * 1.9 + sin(vW.x * 1.1)));
    vec3 dry = dryC * weave * (0.9 + 0.1 * bloom) * (0.97 + 0.03 * gran);
    dry *= 1.0 - (0.2 + 0.06 * oldK) * border;
    dry = mix(dry, dry * vec3(0.95, 0.93, 0.95), oldK);
    float patchK = smoothstep(0.35, 0.75, sin(vW.x * 0.8 + 2.0 * sin(vW.z * 0.6)) * sin(vW.z * 0.9 + 1.7 * sin(vW.x * 0.5)));
    float crack = (1.0 - smoothstep(0.004, 0.016, c.y - c.x)) * smoothstep(0.75, 1.0, oldK) * patchK;
    dry *= 1.0 - 0.09 * crack;
    col = mix(dry, wet, smoothstep(0.0, 1.0, wetK));
    float bake = (1.0 - smoothstep(0.004, 0.018, c.y - c.x)) * uHeat * (1.0 - wetK);
    col *= 1.0 - 0.12 * bake;
  }
""")

# ================= 2) all paint in one buffer, drawn in one call, in the order it was laid down =================
between("// trail ribbon (edge, center, edge across) hugging the surfaces it crosses\n", "const RB0 = { L: null, C: null, R: null, stroke: -1 };", """// trail ribbon (edge, center, edge across) hugging the surfaces it crosses.
// All the paint (trails and splats) lives in one big buffer in the order it was laid down and draws in a single call, so later paint lands on top.
const MAXP = 14000, VPS = 12, MAXV = 700000;
const pX = new Float32Array(MAXP), pY = new Float32Array(MAXP), pZ = new Float32Array(MAXP), pT = new Float32Array(MAXP), pR = new Float32Array(MAXP), pTeam = new Uint8Array(MAXP); let nP = 0, dryP = 0;
const vPos = new Float32Array(MAXV * 3), vBirth = new Float32Array(MAXV), vEdge = new Float32Array(MAXV), vTeamA = new Float32Array(MAXV);
let nV = 0, dirtyV = 0;
const aPos = new THREE.BufferAttribute(vPos, 3), aBirth = new THREE.BufferAttribute(vBirth, 1), aEdge = new THREE.BufferAttribute(vEdge, 1), aTeam = new THREE.BufferAttribute(vTeamA, 1);
[aPos, aBirth, aEdge, aTeam].forEach(at => at.setUsage(THREE.DynamicDrawUsage));
const paintGeo = new THREE.BufferGeometry(); paintGeo.setAttribute('position', aPos); paintGeo.setAttribute('birth', aBirth); paintGeo.setAttribute('edge', aEdge); paintGeo.setAttribute('team', aTeam); paintGeo.setDrawRange(0, 0);
const paintMesh = new THREE.Mesh(paintGeo, paintMat); paintMesh.frustumCulled = false; paintMesh.renderOrder = 10; scene.add(paintMesh);
""")
rep("""  if (stroke === rb.stroke && nSeg < MAXP) {
    const tri = [[rb.L, 1], [rb.C, 0], [L, 1], [rb.C, 0], [Cc, 0], [L, 1], [rb.C, 0], [rb.R, 1], [Cc, 0], [rb.R, 1], [R, 1], [Cc, 0]];
    const o = nSeg * VPS;
    for (let k = 0; k < VPS; k++) { const v = tri[k][0], j = (o + k) * 3; vPos[j] = v[0]; vPos[j + 1] = v[1]; vPos[j + 2] = v[2]; vEdge[o + k] = tri[k][1]; vBirth[o + k] = t; vTeamA[o + k] = team; }
    segT[nSeg] = t; nSeg++;
  }""",
"""  if (stroke === rb.stroke && nV + VPS <= MAXV) {
    const tri = [[rb.L, 1], [rb.C, 0], [L, 1], [rb.C, 0], [Cc, 0], [L, 1], [rb.C, 0], [rb.R, 1], [Cc, 0], [rb.R, 1], [R, 1], [Cc, 0]];
    const o = nV;
    for (let k = 0; k < VPS; k++) { const v = tri[k][0], j = (o + k) * 3; vPos[j] = v[0]; vPos[j + 1] = v[1]; vPos[j + 2] = v[2]; vEdge[o + k] = tri[k][1]; vBirth[o + k] = t; vTeamA[o + k] = team; }
    nV += VPS;
  }""")
# blobby splats: lumpy outlines, fingers with drops at their tips, a forward stretch on a moving landing
between("function addSplat(cx, cy, cz, yaw, R, t, small, round, team) {", "// wetness runs 1 (wet)", r"""function addSplat(cx, cy, cz, yaw, R, t, small, round, team, stretch) {
  team = team || 0; stretch = stretch || 0;
  const r = Math.random, ca = Math.cos(yaw), sa = Math.sin(yaw), pos = [], edg = [], lift = nextLift(8), tips = [];
  const surf = (u, v) => { const x = cx + u * ca + v * sa, z = cz - u * sa + v * ca; const y = surfaceUnder(x, z, cy + 0.35); return (y > cy - 0.45 && !solidThrough(x, z, cy + 0.35)) ? [x, y + 0.02 + lift, z] : null; };
  const fan = (cu, cv, rad, segs, jag, lobes, fingers, str) => {
    // a lumpy outline: a few broad lobes, some smaller bumps and a little grit, then bulges and thin fingers
    const ph = [r() * 6.28, r() * 6.28, r() * 6.28, r() * 6.28], am = [0.05 + 0.08 * r(), 0.04 + 0.05 * r(), 0.025 + 0.035 * r(), 0.015 + 0.02 * r()], hs = [2, 3, 5, 8];
    let sm = []; for (let k = 0; k < segs; k++) { const a = k / segs * 6.2832; let m = 1; for (let h = 0; h < 4; h++) m += am[h] * Math.sin(hs[h] * a + ph[h]); sm.push(rad * m * (1 - jag * 0.5 + jag * r())); }
    for (let pass = 0; pass < 3; pass++) sm = sm.map((v, k) => (v * 2 + sm[(k + 1) % segs] + sm[(k + segs - 1) % segs]) / 4);
    for (let l = 0; l < (lobes || 0); l++) { const c0 = r() * segs, w = segs * (0.045 + r() * 0.035), amp = 0.12 + r() * 0.2; for (let k = 0; k < segs; k++) { let d = Math.abs(k - c0); d = Math.min(d, segs - d); sm[k] *= 1 + amp * Math.exp(-(d * d) / (2 * w * w)); } }
    for (let f = 0; f < (fingers || 0); f++) { const c0 = r() * segs, w = segs * (0.01 + r() * 0.012), amp = 0.22 + r() * 0.38; for (let k = 0; k < segs; k++) { let d = Math.abs(k - c0); d = Math.min(d, segs - d); sm[k] *= 1 + amp * Math.exp(-(d * d) / (2 * w * w)); } tips.push([c0 / segs * 6.2832, rad * (1 + amp) * (1.12 + r() * 0.12), rad * (0.05 + r() * 0.05)]); }
    // a landing on the move smears forward a little
    if (str) for (let k = 0; k < segs; k++) { const sv = Math.sin(k / segs * 6.2832); sm[k] *= 1 + str * (sv > 0 ? sv * sv : 0.25 * sv * sv); }
    const rings = Math.max(1, Math.ceil(rad / 0.45)), cache = new Map();
    const at = (k, j) => { const kk = k % segs, key = j === 0 ? -1 : kk * 1000 + j; if (cache.has(key)) return cache.get(key); const fr = j / rings, ang = kk / segs * 6.2832, rr = sm[kk] * fr, v = surf(cu + Math.cos(ang) * rr, cv + Math.sin(ang) * rr); cache.set(key, v); return v; };
    const ed = (k, j) => clamp(1 - (1 - j / rings) * sm[k % segs] / Math.min(0.55, rad), 0, 1);
    const tri = (a, ea, b, eb, c, ec) => { if (!a || !b || !c) return; if (Math.max(a[1], b[1], c[1]) - Math.min(a[1], b[1], c[1]) > 0.3) return; pos.push(a[0], a[1], a[2], b[0], b[1], b[2], c[0], c[1], c[2]); edg.push(ea, eb, ec); };
    for (let k = 0; k < segs; k++) for (let j = 0; j < rings; j++) {
      const A = at(k, j), B = at(k + 1, j), Cq = at(k, j + 1), D = at(k + 1, j + 1);
      if (j === 0) tri(A, ed(k, 0), Cq, ed(k, 1), D, ed(k + 1, 1));
      else { tri(A, ed(k, j), Cq, ed(k, j + 1), D, ed(k + 1, j + 1)); tri(A, ed(k, j), D, ed(k + 1, j + 1), B, ed(k + 1, j)); }
    }
  };
  const big = R > 2.4;
  fan(0, 0, R, round ? 96 : small ? 24 : 64, round ? 0.06 : small ? 0.1 : 0.2, small ? 0 : round ? 4 + (r() * 3 | 0) : 2 + (r() * 3 | 0), small ? 0 : big ? 6 + (r() * 5 | 0) : 2 + (r() * 3 | 0), stretch);
  // drops at the finger tips, and a scatter of loose ones around the rim
  for (const [a, d, s2] of tips) fan(Math.cos(a) * d, Math.sin(a) * d, Math.max(0.1, s2), 16, 0.1, 0, 0, 0);
  const drops = small ? 0 : (round ? 7 : 3) + (r() * 5 | 0);
  for (let i = 0; i < drops; i++) { const a = r() * 6.2832, d = R * (1.1 + r() * 0.5); fan(Math.cos(a) * d, Math.sin(a) * d, Math.max(0.1, R * (0.03 + r() * 0.06)), 16, 0.08, 0, 0, 0); }
  const nv = pos.length / 3;
  if (nv && nV + nv <= MAXV) { vPos.set(pos, nV * 3); vEdge.set(edg, nV); vBirth.fill(t, nV, nV + nv); vTeamA.fill(team, nV, nV + nv); nV += nv; }
  splats.push({ x: cx, y: cy, z: cz, t, w: 1, hr: R * 0.78 + PR * 0.3, team: team & 1 });
  stamp(cx, cy, cz, R * (round ? 0.98 : 0.9), team);
}
""")
between("function flushTrail() {", "// hard paint lives in a coarse grid", """function flushTrail() {
  if (dirtyV < nV) {
    const o = dirtyV, c = nV - dirtyV;
    aPos.updateRange.offset = o * 3; aPos.updateRange.count = c * 3; aPos.needsUpdate = true;
    aEdge.updateRange.offset = o; aEdge.updateRange.count = c; aEdge.needsUpdate = true;
    aTeam.updateRange.offset = o; aTeam.updateRange.count = c; aTeam.needsUpdate = true;
    aBirth.updateRange.offset = o; aBirth.updateRange.count = c; aBirth.needsUpdate = true;
    dirtyV = nV; paintGeo.setDrawRange(0, nV);
  }
}
function clearTrail() {
  nP = 0; dryP = 0; nV = 0; dirtyV = 0; RB0.stroke = -1; paintSeq = 0; paintGeo.setDrawRange(0, 0); painted.fill(0); paintedN = 0; teamN.fill(0); hardPhase = false; hardGrid.clear();
  splats.length = 0;
}
""")
# slingshot landings smear forward
rep("addSplat(D.x, D.y, D.z, D.yaw, Rr, dryClock, false, false, tcode(D));", "addSplat(D.x, D.y, D.z, D.yaw, Rr, dryClock, false, false, tcode(D), 0.12 + 0.3 * fk);")

# ================= 3) particles: one instanced mesh per material instead of a mesh per drop =================
rep("function spawnPart(x, y, z, vx, vy, vz, life, mat, sz, grav) { const s = new THREE.Mesh(partG, mat || splashMat); s.position.set(x, y, z); scene.add(s); parts.push({ s, v: new THREE.Vector3(vx, vy, vz), life, sz: sz || 1, grav: grav === undefined ? 1 : grav }); }",
    """const PART_CAP = 480, partPools = new Map(), partDummy = new THREE.Object3D();
function partPool(mat) {
  let pl = partPools.get(mat); if (pl) return pl;
  const im = new THREE.InstancedMesh(partG, mat, PART_CAP); im.count = 0; im.frustumCulled = false; im.instanceMatrix.setUsage(THREE.DynamicDrawUsage); if (mat.transparent) im.renderOrder = 8; scene.add(im);
  pl = { im, items: [] }; partPools.set(mat, pl); return pl;
}
function spawnPart(x, y, z, vx, vy, vz, life, mat, sz, grav) {
  const pl = partPool(mat || splashMat); if (pl.items.length >= PART_CAP) pl.items.shift();
  pl.items.push({ x, y, z, vx, vy, vz, life, sz: sz || 1, grav: grav === undefined ? 1 : grav, rest: false });
}""")
between("function updateParts(dt) {\n  for (let i = parts.length - 1; i >= 0; i--) {", "const confs = [], confG", """function updateParts(dt) {
  for (const pl of partPools.values()) {
    const it = pl.items; let n = 0;
    for (let i = 0; i < it.length; i++) {
      const p = it[i]; p.life -= dt; if (p.life <= 0 || p.y < -20) continue;
      if (!p.rest) {
        p.vy -= 12 * p.grav * dt; p.x += p.vx * dt; p.y += p.vy * dt; p.z += p.vz * dt;
        const g = surfaceUnder(p.x, p.z, p.y + 0.2); if (p.y < g + 0.05 && g > -Infinity) { p.y = g + 0.05; p.vx = p.vy = p.vz = 0; p.rest = true; }
      }
      const sc = Math.max(0.01, Math.min(1, p.life * 2)) * p.sz, sp = p.rest ? 0 : Math.hypot(p.vx, p.vy, p.vz);
      partDummy.position.set(p.x, p.y, p.z);
      // drops in flight stretch along their path
      if (sp > 0.6) { partDummy.lookAt(p.x + p.vx, p.y + p.vy, p.z + p.vz); partDummy.scale.set(sc * 0.85, sc * 0.85, sc * (1 + sp * 0.09)); } else { partDummy.rotation.set(0, 0, 0); partDummy.scale.set(sc * 1.15, sc * 0.6, sc * 1.15); }
      partDummy.updateMatrix(); pl.im.setMatrixAt(n, partDummy.matrix); it[n++] = p;
    }
    it.length = n; pl.im.count = n; if (n) pl.im.instanceMatrix.needsUpdate = true;
  }
}
""")
rep("function burst(D, color, n) {\n  const m = toon(color);", "const colMats = new Map(), colMat = c => { let m = colMats.get(c); if (!m) colMats.set(c, m = toon(c)); return m; };\nfunction burst(D, color, n) {\n  const m = colMat(color);")
rep("fxRings.forEach(f => scene.remove(f.m)); fxRings.length = 0; parts.forEach(p => scene.remove(p.s)); parts.length = 0;", "fxRings.forEach(f => { f.m.visible = false; fxFree.push(f); }); fxRings.length = 0; partPools.forEach(pl => { pl.items.length = 0; pl.im.count = 0; });")
rep("...parts.map(p => p.s)", "...[...partPools.values()].map(pl => pl.im)")

# ================= 4) shockwave rings come from a pool =================
rep("const fxRings = [], fxRingG = new THREE.RingGeometry(0.88, 1, 72);", "const fxRings = [], fxFree = [], fxRingG = new THREE.RingGeometry(0.88, 1, 72);")
i = s.index("function shockwave(x, y, z, radius, color) {"); j = s.index("\n", i)
s = s[:i] + """function shockwave(x, y, z, radius, color) {
  let f = fxFree.pop();
  if (!f) { const m = new THREE.Mesh(fxRingG, new THREE.MeshBasicMaterial({ color: 0xFFFFFF, transparent: true, opacity: 1, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -10, polygonOffsetUnits: -10, fog: false })); m.renderOrder = 7; m.rotation.x = -Math.PI / 2; scene.add(m); f = { m }; }
  f.m.material.color.set(color || 0xFFFFFF); f.m.material.opacity = 1; f.m.position.set(x, y + 0.1, z); f.m.scale.setScalar(0.4); f.m.visible = true; f.t = 0; f.r = radius; fxRings.push(f);
}""" + s[j:]
i = s.index("function updateFx(dt) {"); j = s.index("\n", i)
s = s[:i] + "function updateFx(dt) { for (let i = fxRings.length - 1; i >= 0; i--) { const f = fxRings[i]; f.t += dt / 0.6; const k = Math.min(1, f.t), e = 1 - Math.pow(1 - k, 3); f.m.scale.setScalar(0.4 + e * f.r * 1.04); f.m.material.opacity = 1 - k; if (k >= 1) { f.m.visible = false; fxFree.push(f); fxRings.splice(i, 1); } } }" + s[j:]

# ================= 5) the giant slam's crown reuses its materials (no shader compile mid-game) =================
rep("function spawnCrown(D, R) {", "const crownMats = TEAMS.map(t => toon(t.wet, { side: THREE.DoubleSide, emissive: new THREE.Color(t.wet).multiplyScalar(0.18) })), crownHullMat = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide });\nfunction spawnCrown(D, R) {")
rep("  const m = new THREE.Mesh(geo, toon(TEAMS[D.team].wet, { side: THREE.DoubleSide, emissive: new THREE.Color(TEAMS[D.team].wet).multiplyScalar(0.18) }));\n  const hull = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide })); hull.scale.set(1.03, 1.01, 1.03);",
    "  const m = new THREE.Mesh(geo, crownMats[D.team]);\n  const hull = new THREE.Mesh(geo, crownHullMat); hull.scale.set(1.03, 1.01, 1.03);")
rep("  crowns.push({ g, t: 0, geo, mats: [m.material, hull.material] });", "  crowns.push({ g, t: 0, geo });")
rep("if (t > 1.15) { scene.remove(c.g); c.geo.dispose(); c.mats.forEach(m => m.dispose()); crowns.splice(i, 1); }", "if (t > 1.15) { scene.remove(c.g); c.geo.dispose(); crowns.splice(i, 1); }")
open(F, 'w').write(s)
print('ok')
