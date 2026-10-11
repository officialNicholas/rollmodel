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
LAB.set = (name, opt) => { LAB.scen = SCEN[name](opt || {}); LAB.t = 0; LAB.log = []; };
const SCEN = {
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
    D.yaw += D.turn * dt * (D.air ? 0.3 : 1); D.x += Math.sin(D.yaw) * D.spd * dt; D.z += Math.cos(D.yaw) * D.spd * dt;
    if (D.air) { D.vy -= GRAV * (D.vy < 0 ? 1.45 : 1) * dt; D.y += D.vy * dt; if (D.y <= 0) { D.y = 0; D.air = false; D.landV = D.vy; D.vy = 0; D.flung = false; D.squash = 0.5; } }
    D.squash = Math.max(0, (D.squash || 0) - dt * 3);
    const L = V.L, ke = Math.min(1, dt * 10); L.spd += ((D.air ? 0 : clamp(D.spd / 6.5, 0, 1)) - L.spd) * ke; L.lean += (clamp(D.turn / TURN, -1, 1) - L.lean) * ke;
    const rad = PR; V.root.position.set(D.x, D.y + rad * 0.82, D.z); V.root.rotation.set(0, D.yaw, 0); V.body.scale.setScalar(rad);
    // the slingshot's ball: a long pull, the quick part of the flight
    if (D.flung && D.air && !V.flOn) { V.flOn = true; V.flV0 = Math.max(1, D.vy); } else if (!(D.flung && D.air)) V.flOn = false;
    const flV = V.flOn ? D.vy / V.flV0 : 0, ss = (a, b, x) => { const u = clamp((x - a) / (b - a), 0, 1); return u * u * (3 - 2 * u); }, flK = V.flOn ? ss(0.3, 0.78, D.flingC) * ss(-0.15, 0.55, flV) : 0;
    let brace = 0; if (D.air && D.vy < 0) { const f = -D.vy, g = GRAV * 1.45, hh = Math.max(0, D.y), tt = (Math.sqrt(f * f + 2 * g * hh) - f) / g; brace = 1 - ss(0.06, 0.26, tt); }
    const o = { dt, spd: L.spd, lean: L.lean, inAir: D.air, vy: D.vy, height: D.y, grav: GRAV, pos: [D.x, D.y, D.z], yaw: D.yaw, speed: D.air ? 0 : D.spd, rad, squash: D.squash, rise: 0, glance: 0, watch: null,
      blob: flK, blobSt: 0.3 * flK * clamp(flV, 0, 1), curl: 0, brace, D };
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
  else if (m === 'front') camera.position.copy(c).addScaledVector(f, d).add(new THREE.Vector3(0, 0.9, 0));
  else if (m === 'face') camera.position.copy(c).addScaledVector(f, d * 0.55).addScaledVector(side, -d * 0.18).add(new THREE.Vector3(0, 0.35, 0));
  else if (m === 'back') camera.position.copy(c).addScaledVector(f, -d).add(new THREE.Vector3(0, 1.3, 0));
  else camera.position.copy(c).addScaledVector(f, d * 0.75).addScaledVector(side, -d * 0.7).add(new THREE.Vector3(0, 1.1, 0));
  camera.lookAt(c.x, c.y - 0.05, c.z); camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  sun.target.position.set(D.x, 0, D.z); sun.position.set(D.x + 4, 10, D.z + 3);
  renderer.render(scene, camera);
  document.getElementById('hud').textContent = `t ${LAB.t.toFixed(2)}  spd ${D.spd.toFixed(2)}  air ${D.air}  y ${D.y.toFixed(2)}  state ${LAB.I.ax.A.state}`;
};
