// The axolotl lab: one character on a checked floor, driven the way the game drives it (the blob's motion, the per-frame `o` the game
// builds), stepped by hand so a probe can film it frame by frame and measure how far planted feet slide.
const GRAV = 15, JUMP_V = 5.6, TURN = 3.9;
const floorTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d');
  for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { g.fillStyle = (x + y) % 2 ? '#cfc6b4' : '#e4dccb'; g.fillRect(x * 32, y * 32, 32, 32); }
  g.strokeStyle = '#a99f8a'; g.lineWidth = 2; g.strokeRect(0, 0, 256, 256); const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(60, 60); t.anisotropy = 4; return t; })();
const floor = new THREE.Mesh(new THREE.PlaneGeometry(240, 240), new THREE.MeshStandardMaterial({ map: floorTex, roughness: 0.9 })); floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
const marks = new THREE.Group(); scene.add(marks);
const LAB = window.LAB = { ready: false, t: 0, I: null, D: null, V: null, log: [], cam: 'side', camD: 4.2 };
(async () => {
  await AXOC.load('axo-pack.txt');
  const I = AXOC.make({ color: 0xE3122F }); const Vroot = new THREE.Group(), Vbody = new THREE.Group(); Vroot.add(Vbody); Vbody.add(I.root); scene.add(Vroot); Vroot.rotation.order = 'YXZ';
  for (const M of [I.ax.S, I.ax.C]) { M.mesh.castShadow = true; }
  I.noGhost = true; // (the x-ray copy is the game's business: drawn here it shows the far side through the near)
  LAB.I = I; LAB.V = { root: Vroot, body: Vbody, L: { spd: 0, lean: 0 }, yaw: 0 };
  LAB.D = { x: 0, y: 0, z: 0, yaw: 0, spd: 0, turn: 0, air: false, vy: 0, st: 'play', flung: false, flingC: 0, charging: false, charge: 0, rollT: 0, slam: false };
  LAB.ready = true; LAB.render();
})();
// a scenario: f(t, D, dt) sets what the blob does (speed, yaw rate, jumps, flings) the way the game's physics would
LAB.scen = null;
LAB.set = (name, opt) => { LAB.D.pinned = false; LAB.D.climb = null; LAB.scen = SCEN[name](opt || {}); LAB.t = 0; LAB.log = []; };
// a basin to climb out of, the game's tub roughly: a wall, a rim on top, the paint inside
LAB.basin = null;
LAB.makeBasin = c => {
  if (LAB.basin) scene.remove(LAB.basin); const g = new THREE.Group(), wallM = new THREE.MeshStandardMaterial({ color: 0xf3efe8, roughness: 0.55 }), paintM = new THREE.MeshStandardMaterial({ color: 0xE3122F, roughness: 0.3 });
  const ring = (r0, r1) => { const sh = new THREE.Shape(); sh.absellipse(0, 0, r1 * c.ao, r1 * c.bo, 0, Math.PI * 2); const hole = new THREE.Path(); hole.absellipse(0, 0, r0 * c.ai, r0 * c.bi, 0, Math.PI * 2, true); sh.holes.push(hole); return sh; };
  const wall = new THREE.Mesh(new THREE.ExtrudeGeometry(ring(1, 1), { depth: c.top, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.025, bevelSegments: 3, curveSegments: 48 }), wallM); wall.rotation.x = -Math.PI / 2; wall.position.y = 0;
  const paint = new THREE.Mesh(new THREE.CircleGeometry(1, 48), paintM); paint.scale.set(c.ai, c.bi, 1); paint.rotation.x = -Math.PI / 2; paint.position.y = c.liq;
  wall.castShadow = wall.receiveShadow = true; paint.receiveShadow = true; g.add(wall, paint); g.position.set(c.cx, 0, c.cz); scene.add(g); LAB.basin = g;
};
// along the way out: up out of the paint toward the rim, slow while it hauls itself over, easing off onto the floor (the game's own)
const sm = (a, b, x) => { const u = Math.max(0, Math.min(1, (x - a) / (b - a))); return u * u * (3 - 2 * u); };
function crawlTable(s0, rw, s1, T) {
  const N = 96, ss = [], ts = [0]; let tt = 0;
  const v = s => (0.3 + 0.7 * sm(s0, s0 + 0.5, s)) * (0.12 + 0.88 * (1 - sm(s1 - 1.0, s1, s))) * (1 - 0.7 * Math.exp(-Math.pow((s - (rw - 0.3)) / 0.45, 2)));
  for (let i = 0; i <= N; i++) ss.push(s0 + (s1 - s0) * i / N);
  for (let i = 1; i <= N; i++) { tt += (ss[i] - ss[i - 1]) / v((ss[i] + ss[i - 1]) / 2); ts.push(tt); }
  for (let i = 0; i <= N; i++) ts[i] *= T / tt;
  return t => { if (t <= 0) return s0; if (t >= T) return s1; let lo = 0, hi = N; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (ts[m] <= t) lo = m; else hi = m; } return ss[lo] + (ss[hi] - ss[lo]) * (t - ts[lo]) / (ts[hi] - ts[lo]); };
}
const SCEN = {
  climb: o => { const c = Object.assign({ cx: 0, cz: 0, ao: 0.62, bo: 0.77, ai: 0.48, bi: 0.63, top: 0.5, liq: 0.42, deep: 0.3, yaw: 0 }, o); LAB.makeBasin(c); c.inv = new THREE.Matrix4().makeTranslation(-c.cx, 0, -c.cz);
    const fx = Math.sin(c.yaw), fz = Math.cos(c.yaw), rw = 1 / Math.hypot(fx / c.ao, fz / c.bo), rin = 1 / Math.hypot(fx / c.ai, fz / c.bi), T = o.T || 2.0, rise = 0.5, s0 = 0.37 - rin, s1 = rw + 2.3, path = crawlTable(s0, rw, s1, T), t0 = rise * 0.45; let sp = s0;
    return (t, D, dt) => { const ur = Math.min(1, t / rise), sink = 1.3 * Math.pow(1 - ur, 3), s = path(t - t0); D.pinned = true; D.yaw = c.yaw; D.x = c.cx + fx * s; D.z = c.cz + fz * s; D.y = 0; D.spd = dt > 0 ? Math.max(0, (s - sp) / dt) : 0; sp = s; D.turn = 0;
      D.climb = t < t0 + T ? Object.assign({}, c, { sink, floor: 0, tailK: sm(rw - 0.45, rw - 0.05, s), curl: 1 - sm(rw - 0.9, rw - 0.3, s) }) : null; }; },
  idle: () => (t, D) => { D.spd = 0; D.turn = 0; },
  walk: o => (t, D) => { D.spd = o.v === undefined ? 5.4 : o.v; D.turn = o.turn || 0; },
  ramp: o => (t, D) => { const T = o.T || 6, u = (t % T) / T; D.spd = (o.v || 8) * Math.sin(Math.PI * u); D.turn = 0; },
  weave: o => (t, D) => { D.spd = o.v === undefined ? 5.4 : o.v; D.turn = TURN * (o.k || 0.8) * Math.sign(Math.sin(t * Math.PI / (o.T || 1.6))); },
  spin: o => (t, D) => { D.spd = 0; D.turn = TURN * (o.k || 0.6); },
  stopgo: o => (t, D) => { const u = t % 4; D.spd = u < 2 ? (o.v || 5.4) : 0; D.turn = 0; },
  jump: o => { let next = o.at || 0.6; return (t, D) => { D.spd = o.v === undefined ? 4 : o.v; D.turn = 0; if (!D.air && t >= next) { D.air = true; D.vy = JUMP_V; next = t + (o.every || 1.6); } }; },
  fling: o => { let next = o.at || 0.5; return (t, D) => { if (!D.air) { D.spd = Math.max(0, D.spd - 30 * LAB.dt); } D.turn = 0; if (!D.air && t >= next) { const c = o.c === undefined ? 1 : o.c; D.air = true; D.vy = JUMP_V * (0.55 + 0.8 * c) * 0.935; D.spd = 5.4 * (0.9 + 1.7 * c) * 0.8; D.flung = true; D.flingC = c; next = t + (o.every || 3.2); } }; },
};
LAB.dt = 1 / 60;
// one frame: the scenario, the blob's physics (gravity, landing), then the game's look state and the call it makes on the character
LAB.step = (n = 1, dt = 1 / 60) => {
  const D = LAB.D, V = LAB.V, I = LAB.I; LAB.dt = dt;
  for (let k = 0; k < n; k++) {
    LAB.t += dt; if (LAB.scen) LAB.scen(LAB.t, D, dt);
    if (!D.pinned) { D.yaw += D.turn * dt * (D.air ? 0.3 : 1); D.x += Math.sin(D.yaw) * D.spd * dt; D.z += Math.cos(D.yaw) * D.spd * dt; }
    if (D.air) { D.vy -= GRAV * (D.vy < 0 ? 1.45 : 1) * dt; D.y += D.vy * dt; if (D.y <= 0) { D.y = 0; D.air = false; D.landV = D.vy; D.vy = 0; D.flung = false; D.squash = 0.5; } }
    D.squash = Math.max(0, (D.squash || 0) - dt * 3);
    const L = V.L, ke = Math.min(1, dt * 10); L.spd += ((D.air ? 0 : clamp(D.spd / 6.5, 0, 1)) - L.spd) * ke; L.lean += (clamp(D.turn / TURN, -1, 1) - L.lean) * ke;
    const rad = PR; V.root.position.set(D.x, D.y + rad * 0.82, D.z); V.root.rotation.set(0, D.yaw, 0); V.body.scale.setScalar(rad);
    // the slingshot's ball: a long pull, the quick part of the flight
    if (D.flung && D.air && !V.flOn) { V.flOn = true; V.flV0 = Math.max(1, D.vy); } else if (!(D.flung && D.air)) V.flOn = false;
    const flV = V.flOn ? D.vy / V.flV0 : 0, ss = (a, b, x) => { const u = clamp((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u); }, flK = V.flOn ? ss(0.3, 0.78, D.flingC) * ss(-0.15, 0.55, flV) : 0;
    let brace = 0; if (D.air && D.vy < 0) { const f = -D.vy, g = GRAV * 1.45, hh = Math.max(0, D.y), tt = (Math.sqrt(f * f + 2 * g * hh) - f) / g; brace = 1 - ss(0.06, 0.26, tt); }
    const o = { dt, spd: L.spd, lean: L.lean, inAir: D.air, vy: D.vy, height: D.y, grav: GRAV, pos: [D.x, D.y, D.z], yaw: D.yaw, speed: D.air ? 0 : D.spd, rad, squash: D.squash, rise: 0, glance: 0, watch: null,
      blob: flK, blobSt: 0.3 * flK * clamp(flV, 0, 1), curl: 0, brace, D, climb: D.climb || null };
    AXOC.update(I, o);
  }
};
LAB.feet = () => { const I = LAB.I, M = I.ax.P.m[I.ax.A.mesh], out = {}; I.root.updateWorldMatrix(true, true);
  for (const n of ['hand.L', 'hand.R', 'foot.L', 'foot.R', 'head', 'hips', 'chest']) { const b = M.byName[n]; if (!b) continue; const v = new THREE.Vector3(); b.getWorldPosition(v); out[n] = [+v.x.toFixed(4), +v.y.toFixed(4), +v.z.toFixed(4)]; }
  const Lc = I.ax.A.loco; out.st = Lc ? Object.fromEntries(Lc.limbs.map(l => [l.en, l.st])) : {}; out.f = Lc ? +Lc.f.toFixed(2) : 0; out.v = Lc ? +Lc.v.toFixed(2) : 0; return out; };
LAB.render = () => {
  const D = LAB.D, f = new THREE.Vector3(Math.sin(D.yaw), 0, Math.cos(D.yaw)), side = new THREE.Vector3(Math.cos(D.yaw), 0, -Math.sin(D.yaw)), c = new THREE.Vector3(D.x, 0.25 + D.y, D.z);
  const d = LAB.camD, m = LAB.cam;
  if (m === 'side') camera.position.copy(c).addScaledVector(side, -d).add(new THREE.Vector3(0, 0.55, 0));
  else if (m === 'top') camera.position.copy(c).add(new THREE.Vector3(0, d * 1.25, 0.001));
  else if (m === 'fixed') { camera.position.fromArray(LAB.camPos); camera.lookAt(...LAB.camAt); camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); sun.target.position.set(D.x, 0, D.z); sun.position.set(D.x + 4, 10, D.z + 3); renderer.render(scene, camera); document.getElementById('hud').textContent = `t ${LAB.t.toFixed(2)}`; return; }
  else if (m === 'front') camera.position.copy(c).addScaledVector(f, d).add(new THREE.Vector3(0, 0.9, 0));
  else if (m === 'face') camera.position.copy(c).addScaledVector(f, d * 0.55).addScaledVector(side, -d * 0.18).add(new THREE.Vector3(0, 0.35, 0));
  else if (m === 'back') camera.position.copy(c).addScaledVector(f, -d).add(new THREE.Vector3(0, 1.3, 0));
  else camera.position.copy(c).addScaledVector(f, d * 0.75).addScaledVector(side, -d * 0.7).add(new THREE.Vector3(0, 1.1, 0));
  camera.lookAt(c.x, c.y - 0.05, c.z); camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  sun.target.position.set(D.x, 0, D.z); sun.position.set(D.x + 4, 10, D.z + 3);
  renderer.render(scene, camera);
  document.getElementById('hud').textContent = `t ${LAB.t.toFixed(2)}  spd ${D.spd.toFixed(2)}  air ${D.air}  y ${D.y.toFixed(2)}  state ${LAB.I.ax.A.state}`;
};
LAB.camPos = [3.0, 0.95, 0.85]; LAB.camAt = [0, 0.42, 0.85];
