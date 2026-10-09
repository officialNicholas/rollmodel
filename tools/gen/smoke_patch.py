# cartoon smoke trails: puffs streaming behind a blob that's been bounced flying, and behind the fast moves (rocket, missile, a fling)
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

MOD = r"""
// ---------- smoke trails: when a blob's been bounced and goes flying, or tears along on the rocket, a missile or a fling, it leaves a trail of
// cartoon smoke: round white puffs that pop up to size, drift up a little and shrink away (behind the rocket and the missile the newest
// ones glow warm first, like the flame is still in them) ----------
const PUFF_N = 220, puffG = new THREE.IcosahedronGeometry(1, HI ? 2 : 1), puffMat = new THREE.MeshToonMaterial({ color: 0xFFFFFF, gradientMap: grad });
const puffIM = new THREE.InstancedMesh(puffG, puffMat, PUFF_N); puffIM.count = 0; puffIM.frustumCulled = false; puffIM.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
puffIM.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(PUFF_N * 3), 3); puffIM.instanceColor.setUsage(THREE.DynamicDrawUsage); puffIM.layers.set(2); scene.add(puffIM);
const puffs = [], puffDummy = new THREE.Object3D(), PUFF_WARM = new THREE.Color(0xFFC46A), PUFF_GREY = new THREE.Color(0xE9E6F0), puffC = new THREE.Color();
function puffAt(x, y, z, sz, life, warm, vx, vz) { if (puffs.length >= PUFF_N) puffs.shift(); puffs.push({ x, y, z, vx: vx || 0, vy: 0.25 + Math.random() * 0.35, vz: vz || 0, age: 0, life, sz, warm, rx: Math.random() * 6.28, ry: Math.random() * 6.28, grey: Math.random() < 0.35 }); }
// per blob each frame: is it going fast enough, in the right way, to smoke? Puffs are laid by distance, so a faster blob strings them out
function smokeStep(D, dt) {
  const s = D.smk || (D.smk = { x: D.x, y: D.y, z: D.z, acc: 0 }), dx = D.x - s.x, dy = D.y - s.y, dz = D.z - s.z, d = Math.hypot(dx, dy, dz), v = dt > 0 ? d / dt : 0;
  const R = D.rocket, rk = !!R && D.st === 'play' && (R.ph === 'up' || (R.ph === 'dive' && !R.slow)), mis = D.missile && D.slam && D.st === 'play';
  const hit = D.st === 'play' && D.knockT > 0 && D.air && v > 4.5, fl = D.st === 'play' && D.flung && D.air && v > 6;
  if (!(rk || mis || hit || fl) || d > 4) { s.x = D.x; s.y = D.y; s.z = D.z; s.acc = 0; return; }
  const big = rk || mis, step = big ? 0.2 : 0.26, sz = big ? 0.3 : 0.22; s.acc += d;
  let n = 0; while (s.acc >= step && n++ < 8) { s.acc -= step; const u = 1 - s.acc / Math.max(d, 1e-4), j = 0.08;
    puffAt(s.x + dx * u + (Math.random() - 0.5) * j, s.y + dy * u + 0.32 + (Math.random() - 0.5) * j, s.z + dz * u + (Math.random() - 0.5) * j, sz * (0.75 + Math.random() * 0.5), (big ? 0.75 : 0.6) + Math.random() * 0.25, big, (Math.random() - 0.5) * 0.4, (Math.random() - 0.5) * 0.4); }
  s.x = D.x; s.y = D.y; s.z = D.z;
}
function updatePuffs(dt) {
  let n = 0; const ca = puffIM.instanceColor.array;
  for (let i = 0; i < puffs.length; i++) {
    const p = puffs[i]; p.age += dt; if (p.age >= p.life) continue;
    p.x += p.vx * dt; p.y += p.vy * dt; p.z += p.vz * dt; const dr = Math.max(0, 1 - 2.4 * dt); p.vx *= dr; p.vz *= dr;
    const u = p.age / p.life, grow = p.age < 0.09 ? 0.35 + 0.65 * (p.age / 0.09) * (1 + 0.25 * Math.sin(p.age / 0.09 * Math.PI)) : 1, k = p.sz * grow * (1 - Math.pow(Math.max(0, (u - 0.35) / 0.65), 1.6)) * (1 + 0.35 * u);
    puffDummy.position.set(p.x, p.y, p.z); puffDummy.rotation.set(p.rx, p.ry + u, 0); puffDummy.scale.setScalar(Math.max(0.001, k)); puffDummy.updateMatrix(); puffIM.setMatrixAt(n, puffDummy.matrix);
    puffC.copy(p.grey ? PUFF_GREY : COL_WHITE); if (p.warm) puffC.lerp(PUFF_WARM, 1 - Math.min(1, p.age / 0.16));
    ca[n * 3] = puffC.r; ca[n * 3 + 1] = puffC.g; ca[n * 3 + 2] = puffC.b; puffs[n++] = p;
  }
  puffs.length = n; puffIM.count = n; puffIM.visible = n > 0;
  if (n) { const mA = puffIM.instanceMatrix, cA = puffIM.instanceColor; mA.clearUpdateRanges(); mA.addUpdateRange(0, n * 16); mA.needsUpdate = true; cA.clearUpdateRanges(); cA.addUpdateRange(0, n * 3); cA.needsUpdate = true; }
}
function clearPuffs() { puffs.length = 0; puffIM.count = 0; puffIM.visible = false; for (const D of [P, H, H2]) if (D) D.smk = null; }
"""
anchor = "const tmat = D => teamMats[D.team];\n"
rep(anchor, anchor + MOD)
# each frame: lay trails for every blob, then age the puffs
rep("  updateParts(dt); flushGrooves(); updateFx(dt); updateBoom(dt);", "  updateParts(dt); flushGrooves(); if (state === 'play' || state === 'dead') for (const D of ACTIVE) smokeStep(D, dt); updatePuffs(dt); updateFx(dt); updateBoom(dt);")
rep("  lastPct = -1; lastPctC = -1; setScore(); clearGrooves(); tankOn = false;", "  lastPct = -1; lastPctC = -1; setScore(); clearGrooves(); clearPuffs(); tankOn = false;")
open(P, 'w').write(src)
print('ok')
