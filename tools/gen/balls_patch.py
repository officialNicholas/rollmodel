# beach balls on Palette Island: light, bouncy, knocked about by blobs, pounds, blasts and shots; roll and bounce off the boxes; fall in
# the sea or a hole and pop back somewhere else
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

MOD = r"""
// ---------- beach balls (Palette Island): big light balls that bounce and roll. A blob running into one sends it off ahead of it, any pound,
// blast or landing nearby throws it, a paint shot knocks it; it bounces off the boxes and walls, and anything that falls off the stage or
// down a hole comes back a moment later somewhere else, with a pop ----------
const BALL_R = 0.5, BALL_N = 2, balls = [];
const ballG = (() => {
  const g = new THREE.SphereGeometry(1, 24, 16).toNonIndexed(), p = g.attributes.position, n = p.count, a = new Float32Array(n * 3), cc = new THREE.Color();
  const GORE = [0xE8343B, 0xFFFFFF, 0x2E7CF6, 0xFFFFFF, 0xFFC72C, 0xFFFFFF];
  for (let t = 0; t < n; t += 3) {
    let x = 0, y = 0, z = 0; for (let k = 0; k < 3; k++) { x += p.getX(t + k); y += p.getY(t + k); z += p.getZ(t + k); }
    const lon = (Math.atan2(z, x) + Math.PI) / (Math.PI * 2), cap = Math.abs(y / 3) > 0.9;
    cc.setHex(cap ? 0xFFFFFF : GORE[Math.min(5, Math.floor(lon * 6))]); for (let k = 0; k < 3; k++) { a[(t + k) * 3] = cc.r; a[(t + k) * 3 + 1] = cc.g; a[(t + k) * 3 + 2] = cc.b; }
  }
  g.setAttribute('color', new THREE.BufferAttribute(linArr(a), 3)); g.deleteAttribute('uv'); return g;
})();
const ballMat = glossMat(0xFFFFFF, { vertexColors: true, roughness: 0.3, clearcoat: 0.8 }); if (!HI) ballMat.vertexColors = true;
for (let i = 0; i < BALL_N; i++) {
  const m = new THREE.Mesh(ballG, ballMat), o = new THREE.Mesh(ballG, inkMat); m.castShadow = true; m.renderOrder = 33; o.renderOrder = 32.6; m.add(o); m.visible = false; scene.add(m);
  balls.push({ m, on: false, x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, q: new THREE.Quaternion(), sq: 0, pop: 1, out: 0, hitT: 0, wet: false });
}
const ballAxis = new THREE.Vector3(), ballDq = new THREE.Quaternion();
// somewhere open on the ground: clear of walls, holes, basins, puddles, power-ups and the starting spots
function ballSpot(b) {
  for (let k = 0; k < 60; k++) {
    const x = (Math.random() * 2 - 1) * (ARENA - 3), z = (Math.random() * 2 - 1) * (ARENA - 3);
    if (surfaceUnder(x, z, 0.3) !== 0 || blockedAt(x, z, 0) || [[1.2, 0], [-1.2, 0], [0, 1.2], [0, -1.2]].some(([dx, dz]) => surfaceUnder(x + dx, z + dz, 0.3) !== 0 || blockedAt(x + dx, z + dz, 0))) continue;
    if (pots.some(p => Math.hypot(p.x - x, p.z - z) < 2.4) || rivals.some(r => Math.hypot(r.x - x, r.z - z) < r.rad + 1.4) || powers.some(w => Math.hypot(w.x - x, w.z - z) < 2)) continue;
    if ([START, CSTART, CSTART2].some(s => Math.hypot(s.x - x, s.z - z) < 4) || balls.some(o => o !== b && o.on && Math.hypot(o.x - x, o.z - z) < 4)) continue;
    return [x, z];
  }
  return null;
}
function ballPut(b, pop) { const s = ballSpot(b); if (!s) { b.on = false; b.m.visible = false; return; } b.on = true; b.x = s[0]; b.z = s[1]; b.y = BALL_R + (pop ? 0.6 : 0); b.vx = b.vz = 0; b.vy = 0; b.out = 0; b.pop = pop ? 0 : 1; b.wet = false; b.q.setFromEuler(new THREE.Euler(Math.random() * 6, Math.random() * 6, Math.random() * 6));
  if (pop) { if (Math.hypot(b.x - P.x, b.z - P.z) < 16) { AU.at(b.x, b.z); AU.pop(); } for (let i = 0; i < 10; i++) { const a = Math.random() * 6.283; spawnPart(b.x + Math.cos(a) * 0.4, 0.1, b.z + Math.sin(a) * 0.4, Math.cos(a) * 1.6, 1.5 + Math.random(), Math.sin(a) * 1.6, 0.4, sandGrainMat, 0.25); } } }
function placeBalls() { for (const b of balls) { if (TH && TH.id === 'island') ballPut(b, false); else { b.on = false; b.m.visible = false; } } }
// a shove from a blast (a pound, a missile, a landing: everything that throws up a ring of paint)
function ballBlast(x, y, z, R) {
  for (const b of balls) { if (!b.on || b.out > 0) continue; const dx = b.x - x, dz = b.z - z, d = Math.hypot(dx, dz), reach = R * 1.5 + BALL_R; if (d > reach || Math.abs(b.y - y) > 2.5) continue;
    const k = (1 - d / reach) * (3 + R * 2.6), nx = d > 0.01 ? dx / d : Math.random() - 0.5, nz = d > 0.01 ? dz / d : Math.random() - 0.5; b.vx += nx * k; b.vz += nz * k; b.vy = Math.max(b.vy, 2 + k * 0.7); b.sq = Math.min(1, b.sq + 0.5); }
}
// a paint shot hitting it: knocked along, a splash of the shot's paint
function ballShot(s) {
  for (const b of balls) { if (!b.on || b.out > 0) continue; const dx = b.x - s.x, dy = b.y - s.y, dz = b.z - s.z; if (dx * dx + dy * dy + dz * dz > (BALL_R + SHOT_R) * (BALL_R + SHOT_R)) continue;
    const v = Math.hypot(s.vx, s.vz) || 1; b.vx += s.vx / v * 3.2; b.vz += s.vz / v * 3.2; b.vy = Math.max(b.vy, 2.2); b.sq = 0.6; return true; }
  return false;
}
function stepBalls(dt) {
  for (const b of balls) {
    if (!b.on) continue;
    if (b.out > 0) { b.out -= dt; if (b.out <= 0) ballPut(b, true); else { b.vy -= GRAV * 0.5 * dt; b.y += b.vy * dt; b.m.visible = false; continue; } }
    if (b.pop < 1) b.pop = Math.min(1, b.pop + dt * 2.2);
    if (b.hitT > 0) b.hitT -= dt;
    const px = b.x, pz = b.z; b.vy -= GRAV * 0.62 * dt; // (light: it floats down slowly)
    let nx = b.x + b.vx * dt, nz = b.z + b.vz * dt; b.y += b.vy * dt;
    // walls: anything higher than a small step at its edge turns it back (each way on its own, so it slides along)
    const foot = b.y - BALL_R, wall = (x, z) => { const s = surfaceUnder(x, z, 99); return s > foot + 0.3 && surfaceUnder(x, z, foot + 0.3) < s - 0.05 && Math.abs(x) < ARENA + 0.5 && Math.abs(z) < ARENA + 0.5 ? s : null; };
    const sx = Math.sign(b.vx) || 1, sz = Math.sign(b.vz) || 1;
    if (wall(nx + sx * BALL_R * 0.85, b.z) !== null) { nx = b.x; if (Math.abs(b.vx) > 0.8 && b.hitT <= 0 && Math.hypot(b.x - P.x, b.z - P.z) < 14) { AU.at(b.x, b.z); AU.plop(); b.hitT = 0.15; } b.vx = -b.vx * 0.62; b.sq = Math.min(1, b.sq + Math.abs(b.vx) * 0.08); }
    if (wall(nx, nz + sz * BALL_R * 0.85) !== null) { nz = b.z; if (Math.abs(b.vz) > 0.8 && b.hitT <= 0 && Math.hypot(b.x - P.x, b.z - P.z) < 14) { AU.at(b.x, b.z); AU.plop(); b.hitT = 0.15; } b.vz = -b.vz * 0.62; b.sq = Math.min(1, b.sq + Math.abs(b.vz) * 0.08); }
    b.x = nx; b.z = nz;
    // the ground: a bounce, then rolling (slowing on the sand)
    const g = surfaceUnder(b.x, b.z, foot + 0.3);
    if (g > -Infinity && b.y - BALL_R <= g) { b.y = g + BALL_R; if (b.vy < 0) { const imp = -b.vy; b.vy = imp > 0.9 ? imp * 0.6 : 0; if (imp > 2.2) { b.sq = Math.min(1, b.sq + imp * 0.09); if (TH.sand && imp > 3) sandBurstAt(b.x, g, b.z, Math.min(1, imp / 8)); } } const f = Math.max(0, 1 - (TH.sand ? 0.75 : 0.45) * dt); b.vx *= f; b.vz *= f; }
    // off the edge or down a hole: gone for a moment (with a splash if it's the sea)
    if (!b.wet && b.y < WATER_Y + 0.1 && (Math.abs(b.x) > ARENA || Math.abs(b.z) > ARENA) && sea.visible) { b.wet = true; for (let i = 0; i < 14; i++) { const a = Math.random() * 6.283, v = 1 + Math.random() * 2; spawnPart(b.x, WATER_Y + 0.1, b.z, Math.cos(a) * v, 2 + Math.random() * 2, Math.sin(a) * v, 0.5, steamMat, 0.5 + Math.random() * 0.4); } }
    if (b.y < -2.5) { b.out = 1.4; b.m.visible = false; continue; }
    // blobs: whoever runs into it sends it off ahead of them (a giant much harder), and it pops up a little
    for (const D of ACTIVE) {
      if (D.st !== 'play' && D.st !== 'hide') continue; const gk = D.giantT > 0 ? GIANT_K * 0.7 : 1, rr = BALL_R + PR * 0.9 * gk, dx = b.x - D.x, dz = b.z - D.z, dy = b.y - (D.y + PR * 0.8 * gk), d = Math.hypot(dx, dz, dy * 0.8);
      if (d >= rr || d < 1e-4) continue;
      const ux = dx / d, uz = dz / d; b.x = D.x + ux * rr; b.z = D.z + uz * rr;
      const dvx = (D.air ? 0 : Math.sin(D.yaw) * D.spd) + (D.kx || 0), dvz = (D.air ? 0 : Math.cos(D.yaw) * D.spd) + (D.kz || 0), vn = (dvx - b.vx) * ux + (dvz - b.vz) * uz;
      if (vn > 0) { const k = vn * (1.5 + 0.4 * gk); b.vx += ux * k; b.vz += uz * k; b.vy = Math.max(b.vy, Math.min(6, 1.2 + vn * 0.45)); b.sq = Math.min(1, b.sq + vn * 0.1); if (vn > 2 && b.hitT <= 0) { if (Math.hypot(b.x - P.x, b.z - P.z) < 14) { AU.at(b.x, b.z); AU.plop(); } b.hitT = 0.2; if (D === P) buzz(6); } }
    }
    // the other ball
    for (const o of balls) { if (o === b || !o.on || o.out > 0) continue; const dx = b.x - o.x, dy = b.y - o.y, dz = b.z - o.z, d = Math.hypot(dx, dy, dz); if (d >= BALL_R * 2 || d < 1e-4) continue;
      const ux = dx / d, uy = dy / d, uz = dz / d, push = (BALL_R * 2 - d) / 2; b.x += ux * push; b.y += uy * push; b.z += uz * push; o.x -= ux * push; o.y -= uy * push; o.z -= uz * push;
      const vn = (b.vx - o.vx) * ux + (b.vy - o.vy) * uy + (b.vz - o.vz) * uz; if (vn < 0) { const j = -vn * 0.9; b.vx += ux * j; b.vy += uy * j; b.vz += uz * j; o.vx -= ux * j; o.vy -= uy * j; o.vz -= uz * j; } }
    // rolling: it turns as it travels
    const mx = b.x - px, mz = b.z - pz, ml = Math.hypot(mx, mz);
    if (ml > 1e-5) { ballAxis.set(mz, 0, -mx).normalize(); ballDq.setFromAxisAngle(ballAxis, ml / BALL_R); b.q.premultiply(ballDq); }
    b.sq = Math.max(0, b.sq - dt * 4);
    const s = BALL_R * Math.max(0.01, easeElastic(b.pop)), q = Math.sin(b.sq * Math.PI) * 0.16;
    b.m.visible = true; b.m.position.set(b.x, b.y - q * BALL_R * 0.6, b.z); b.m.quaternion.copy(b.q); b.m.scale.set(s * (1 + q * 0.5), s * (1 - q), s * (1 + q * 0.5));
  }
}
// sand thrown up where it lands hard
function sandBurstAt(x, y, z, k) { const n = 4 + Math.round(k * 8); for (let i = 0; i < n; i++) { const a = Math.random() * 6.2832, u = 0.8 + Math.random() * 1.6 * (0.5 + k); spawnPart(x + Math.cos(a) * 0.3, y + 0.05, z + Math.sin(a) * 0.3, Math.cos(a) * u, 1.2 + Math.random() * 1.6 * (0.4 + k), Math.sin(a) * u, 0.35 + Math.random() * 0.3, i % 3 ? sandGrainMat : sandGrainMat2, 0.16 + Math.random() * 0.2); } }
"""
anchor = "function clearPuffs() {"
i = src.index(anchor); j = src.index("\n", i)
src = src[:j + 1] + MOD + src[j + 1:]
# each step; a blast throws them; a shot knocks one; new stage, new balls
rep("updateParts(dt); flushGrooves(); if (state === 'play' || state === 'dead') for (const D of ACTIVE) smokeStep(D, dt); updatePuffs(dt);",
    "updateParts(dt); flushGrooves(); stepBalls(dt); if (state === 'play' || state === 'dead') for (const D of ACTIVE) smokeStep(D, dt); updatePuffs(dt);")
rep("function shockwave(x, y, z, radius, color) {\n  swayBlast(x, z, radius);", "function shockwave(x, y, z, radius, color) {\n  swayBlast(x, z, radius); ballBlast(x, y, z, radius);")
rep("    else if (shotBlocked(s.x, s.z, s.y)) {", "    else if (ballShot(s)) { shotSplat(s, surfaceUnder(s.x, s.z, s.y + 0.3, true), 0.7); gone = true; }\n    else if (shotBlocked(s.x, s.z, s.y)) {")
rep("  placePowers();\n}", "  placePowers(); placeBalls();\n}")
open(P, 'w').write(src)
print('ok')
