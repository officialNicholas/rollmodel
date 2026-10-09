# sand grooves where a blob slides along with no paint to lay, and grains kicked up as blobs move and land on the island
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

MOD = r"""
// ---------- the island's sand: a groove where a blob slides along with no paint to lay (a smoothed channel, a little bank of sand along each
// side, two fine lines down it from its stubs), filling back in after a minute; and grains kicked up as blobs move and land ----------
// The grooves draw as one ribbon mesh under the paint, multiplying the sand's own color (darker in the channel and on the banks' shaded
// faces, brighter on the faces toward the sun), so they take on whatever the sand looks like there
const GRV_SEG = 1600, GRV_V = GRV_SEG * 12, grvPos = new Float32Array(GRV_V * 3), grvG = new Float32Array(GRV_V * 4);
const grvPA = new THREE.BufferAttribute(grvPos, 3).setUsage(THREE.DynamicDrawUsage), grvGA = new THREE.BufferAttribute(grvG, 4).setUsage(THREE.DynamicDrawUsage);
const grvGeo = new THREE.BufferGeometry(); grvGeo.setAttribute('position', grvPA); grvGeo.setAttribute('aG', grvGA); grvGeo.setDrawRange(0, 0);
const grvU = { uNow: { value: 0 }, uL: { value: new THREE.Vector3(0.5, 1, 0.3).normalize() } };
const grvMat = new THREE.ShaderMaterial({ uniforms: grvU, side: THREE.DoubleSide, depthWrite: false, transparent: true, blending: THREE.CustomBlending, blendEquation: THREE.AddEquation, blendSrc: THREE.DstColorFactor, blendDst: THREE.ZeroFactor, blendSrcAlpha: THREE.ZeroFactor, blendDstAlpha: THREE.OneFactor, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
  vertexShader: 'attribute vec4 aG; varying vec4 vG; void main(){ vG = aG; gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position, 1.0); }',
  fragmentShader: `uniform float uNow; uniform vec3 uL; varying vec4 vG;
  // the groove's shape across it (e: -1 at one edge, 0 down the middle, 1 at the other)
  float gh(float e){ float a = abs(e); return -0.55 * (1.0 - smoothstep(0.0, 0.7, a)) + 0.6 * exp(-pow((a - 0.76) / 0.1, 2.0)) - 0.4 * exp(-pow((a - 0.2) / 0.045, 2.0)); }
  void main(){
    float e = vG.x, fade = 1.0 - smoothstep(35.0, 70.0, uNow - vG.y), sl = (gh(e + 0.015) - gh(e - 0.015)) / 0.03;
    vec2 L = uL.xz / max(1e-4, length(uL.xz));
    float shade = 1.0 + clamp(-sl * dot(vG.zw, L) * 0.08, -0.3, 0.24) + gh(e) * 0.08;
    gl_FragColor = vec4(mix(vec3(1.0), shade * vec3(1.0, 0.975, 0.95), fade), 1.0);
  }` });
const grvMesh = new THREE.Mesh(grvGeo, grvMat); grvMesh.frustumCulled = false; grvMesh.renderOrder = 9; scene.add(grvMesh);
let grvN = 0, grvHead = 0, grvLo = -1, grvHi = -1, grvWrap = false;
function grooveSeg(A, B) {
  const i = grvHead; grvHead = (grvHead + 1) % GRV_SEG; grvN = Math.min(GRV_SEG, grvN + 1);
  if (grvLo < 0) { grvLo = grvHi = i; } else if (i < grvLo) grvWrap = true; else grvHi = Math.max(grvHi, i);
  let o = i * 12;
  for (const [S, k] of [[A, 'l'], [B, 'l'], [A, 'c'], [B, 'l'], [B, 'c'], [A, 'c'], [A, 'c'], [B, 'c'], [A, 'r'], [B, 'c'], [B, 'r'], [A, 'r']]) {
    const p = S[k]; grvPos[o * 3] = p[0]; grvPos[o * 3 + 1] = p[1]; grvPos[o * 3 + 2] = p[2];
    grvG[o * 4] = k === 'l' ? -1 : k === 'r' ? 1 : 0; grvG[o * 4 + 1] = clock; grvG[o * 4 + 2] = S.sx; grvG[o * 4 + 3] = S.sz; o++;
  }
}
function flushGrooves() {
  grvU.uNow.value = clock; if (grvLo < 0) return;
  grvPA.clearUpdateRanges(); grvGA.clearUpdateRanges();
  if (grvWrap) { grvPA.addUpdateRange(0, GRV_V * 3); grvGA.addUpdateRange(0, GRV_V * 4); }
  else { grvPA.addUpdateRange(grvLo * 36, (grvHi - grvLo + 1) * 36); grvGA.addUpdateRange(grvLo * 48, (grvHi - grvLo + 1) * 48); }
  grvPA.needsUpdate = grvGA.needsUpdate = true; grvGeo.setDrawRange(0, grvN * 12); grvLo = grvHi = -1; grvWrap = false;
}
function clearGrooves() { grvN = 0; grvHead = 0; grvLo = grvHi = -1; grvWrap = false; grvGeo.setDrawRange(0, 0); for (const D of [P, H, H2]) if (D && D.grv) D.grv.on = false; }
const GRV_W = 0.3, grvPt = (x, y, z, sx, sz) => ({ l: [x - sx * GRV_W, y + 0.006, z - sz * GRV_W], c: [x, y + 0.006, z], r: [x + sx * GRV_W, y + 0.006, z + sz * GRV_W], sx, sz });
// each frame on the ground: lay the groove on while it slides with no paint (a jump, a step up or down, or paint again ends the run)
function grooveStep(D) {
  const g = D.grv || (D.grv = { on: false, x: 0, y: 0, z: 0, P: null });
  if (!(TH.sand && D.dry && D.st === 'play' && D.spd > 0.25)) { g.on = false; return; }
  if (g.on && (Math.abs(D.y - g.y) > 0.2 || Math.hypot(D.x - g.x, D.z - g.z) > 1)) g.on = false;
  if (!g.on) { g.on = true; g.x = D.x; g.y = D.y; g.z = D.z; g.P = null; return; }
  const dx = D.x - g.x, dz = D.z - g.z, L = Math.hypot(dx, dz); if (L < 0.13) return;
  const sx = dz / L, sz = -dx / L, B = grvPt(D.x, D.y, D.z, sx, sz);
  grooveSeg(g.P || grvPt(g.x, g.y, g.z, sx, sz), B); g.P = B; g.x = D.x; g.y = D.y; g.z = D.z;
}
// grains thrown up off the sand: out from its leading edge as it moves (more off its tail when it's dry and scraping along), a little burst
// as it lands, now and then a faint puff of dust
const sandGrainMat = toon(0xD7AA68), sandGrainMat2 = toon(0xEBC88E), sandDustMat = new THREE.MeshBasicMaterial({ color: 0xF2DCB0, transparent: true, opacity: 0.42, depthWrite: false });
function sandKick(D, dt) {
  if (!TH.sand || D.st !== 'play' || D.air || D.spd < 1.1 || D.giantT > 0) return;
  const k = Math.min(1.6, D.spd / cfg.speed); D.sandAcc = (D.sandAcc || 0) + dt * (D.dry ? 24 : 10) * k;
  const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw);
  while (D.sandAcc >= 1) { D.sandAcc -= 1; const sd = Math.random() < 0.5 ? -1 : 1, rear = D.dry && Math.random() < 0.55, u = 0.6 + Math.random() * 1.3;
    const ox = rear ? -fx * 0.3 + fz * (Math.random() - 0.5) * 0.3 : fx * 0.18 + fz * sd * 0.26, oz = rear ? -fz * 0.3 - fx * (Math.random() - 0.5) * 0.3 : fz * 0.18 - fx * sd * 0.26;
    const vx = rear ? -fx * u : fz * sd * u * 0.9 - fx * u * 0.35, vz = rear ? -fz * u : -fx * sd * u * 0.9 - fz * u * 0.35;
    spawnPart(D.x + ox, D.y + 0.05, D.z + oz, vx, 1.1 + Math.random() * 1.5, vz, 0.32 + Math.random() * 0.26, Math.random() < 0.6 ? sandGrainMat : sandGrainMat2, 0.16 + Math.random() * 0.2);
    if (Math.random() < 0.12) spawnPart(D.x + ox, D.y + 0.08, D.z + oz, vx * 0.3, 0.35, vz * 0.3, 0.45 + Math.random() * 0.2, sandDustMat, 0.9 + Math.random() * 0.7, -0.04); }
}
function sandBurst(D, k) {
  if (!TH.sand) return; const n = 6 + Math.round(k * 12);
  for (let i = 0; i < n; i++) { const a = Math.random() * 6.2832, u = 0.9 + Math.random() * 1.8 * (0.5 + k); spawnPart(D.x + Math.cos(a) * 0.3, D.y + 0.05, D.z + Math.sin(a) * 0.3, Math.cos(a) * u, 1.3 + Math.random() * 1.8 * (0.4 + k), Math.sin(a) * u, 0.35 + Math.random() * 0.3, i % 3 ? sandGrainMat : sandGrainMat2, 0.16 + Math.random() * 0.22); }
  for (let i = 0; i < 2 + Math.round(k * 2); i++) { const a = Math.random() * 6.2832; spawnPart(D.x + Math.cos(a) * 0.35, D.y + 0.1, D.z + Math.sin(a) * 0.35, Math.cos(a) * 0.6, 0.4, Math.sin(a) * 0.6, 0.5 + Math.random() * 0.2, sandDustMat, 1 + Math.random() * 0.8, -0.04); }
}
"""
# after the particle helpers (spawnPart and colMat are defined there)
anchor = "const tmat = D => teamMats[D.team];\n"
rep(anchor, anchor + MOD)
# step: the groove while dry, the grains while moving (on the ground), a burst on landing
rep("      if (D.flatT <= 0 && !D.dry) { D.dist += D.spd * dt; while (D.dist >= SPACING) {",
    "      grooveStep(D); sandKick(D, dt);\n      if (D.flatT <= 0 && !D.dry) { D.dist += D.spd * dt; while (D.dist >= SPACING) {")
rep("      D.y = g; D.vy = 0; D.air = false; D.coyote = 0; D.squash = 0.6 + 0.4 * impact; D.airSling = false; D.dashDir = 0;",
    "      D.y = g; D.vy = 0; D.air = false; D.coyote = 0; D.squash = 0.6 + 0.4 * impact; D.airSling = false; D.dashDir = 0; if (impact > 0.25 && D.st === 'play') sandBurst(D, impact);")
# the light the grooves are shaded by follows the sun; a new match starts with smooth sand
rep("paintUniforms.uLight.value.copy(sun.position).normalize(); envU.sunDir.value.copy(sun.position).normalize();",
    "paintUniforms.uLight.value.copy(sun.position).normalize(); envU.sunDir.value.copy(sun.position).normalize(); grvU.uL.value.copy(sun.position).normalize();")
rep("  lastPct = -1; lastPctC = -1; setScore(); tankOn = false;", "  lastPct = -1; lastPctC = -1; setScore(); clearGrooves(); tankOn = false;")
# the grains' and dust's pools are made (and their shaders built) up front
rep("[...teamMats, splashMat, boilPartMat, puHaloMat, ...orbPartMats, steamMat, smokeMat, dustMat, emberMat,", "[...teamMats, splashMat, boilPartMat, puHaloMat, ...orbPartMats, steamMat, smokeMat, dustMat, emberMat, sandGrainMat, sandGrainMat2, sandDustMat,")
rep('  updateParts(dt); updateFx(dt); updateBoom(dt);', '  updateParts(dt); flushGrooves(); updateFx(dt); updateBoom(dt);')
open(P, 'w').write(src)
print('ok')
