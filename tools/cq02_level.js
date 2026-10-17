// ---------- (cq02) the Season Conquest level: a greybox. The Keep (the reveal, the boss flees), the Aqueduct Run (a raised causeway
// in an S over a slimed canal, the collapse chasing you, the boss slamming and diving ahead), the Sunken Plaza (jellet waves, then the
// turret on the valve pads pins the boss for your pounds). Sections, checkpoints, lives per checkpoint, chip damage by covering slime.
// Everything here is placeholder geometry through the stage pipeline (boxes, holes, pots), to be swapped for the real pieces. ----------
var CQL = null; // the level under way
var CQLV = window.CQLV = { chip: 0.00006, pop: 0.006, bell: 0.07, bellN: 3, frontK: 0.86, frontGrace: 5, slamEvery: 7.5, diveEvery: 13, jelEvery: 11, jelSpd: 1.9, waves: [4, 6, 8], valveK: 0.55, stun: 12 }; // (tunables, for the browser's console)
const CQL_SECS = [
  { id: 'keep', label: 'Sunken Keep', sub: 'Season Conquest · the reveal' },
  { id: 'run', label: 'Aqueduct Run', sub: 'Season Conquest · the chase', arena: 33, theme: 'conq2' },
  { id: 'plaza', label: 'Sunken Plaza', sub: 'Season Conquest · its babies', arena: 26.4, theme: 'conq2' },
];
// the keep's materials and light on a square floor (no ring, no wall, no pool): the runner and the plaza stand on it
THEMES.push(Object.assign({}, THEME_BY.conquest, { id: 'conq2', label: 'Sunken Ruins', ring: undefined, dress: null, noSea: false, slime: false, sea: true, seaCol: [0x2A0A48, 0x8E3CF0], base: { hemiI: 1.45, key: 0xC8DCF4, keyI: 0.95 }, lk: { hemi: 0.85, key: 1.5 }, envRT: null, charRT: null })); THEME_BY.conq2 = THEMES[THEMES.length - 1];
const cqlvM = {}; // shared placeholder materials
function cqlvMat(k) { if (cqlvM[k]) return cqlvM[k]; const c = { jel: 0xB25CFF, jelArm: 0x6A3AA8, gate: 0xFFE070, front: 0x120818, pad: 0x2E9BFF, padOn: 0xFFE070, pin: 0xE8ECEE }[k];
  return cqlvM[k] = k === 'front' ? new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: 0.78, depthWrite: false }) : k === 'gate' ? new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: 0.85 }) : new THREE.MeshStandardMaterial({ color: c, roughness: 0.55, emissive: k === 'jel' ? 0x401070 : 0x000000 }); }

// ---- opening and leaving ----
function cqlvOpen() {
  if (state !== 'menu' || building || irisBusy) return;
  CQL = { sec: -1, t: 0, hp: 1, chip: 0, pops: 0, cp: null, cpSec: 0, foe: 0, chipAcc: 0, chipT: 0, jel: [], g: new THREE.Group(), S: {}, hooked: false, deaths: 0, t0: performance.now() };
  scene.add(CQL.g); conqPreview(); // (the keep and the boss demo's entrance: section 0)
}
function cqlvEnd() { if (!CQL) return; cqlvClearJel(); scene.remove(CQL.g); CQL.g.traverse(o => { if (o.geometry) o.geometry.dispose(); }); const h = $('cqlHud'); if (h) h.hidden = true; CQL = null; }
// the player set down somewhere (a checkpoint, the start of a section): a fresh blob, facing the way on, the camera behind
function cqlvPlace(x, z, yaw) {
  const y = Math.max(0, surfaceUnder(x, z, 12, true)); resetBlob(P, x, z, yaw); P.y = y; P.st = 'play'; P.paint = 1; P.immuneT = 1.2; P.slamCD = P.slamMax = 1; P.held = null;
  camYaw = yaw; camYawV = 0; camSnap = true; drop.visible = true; shadowBlob.visible = true; hintEl.classList.remove('on');
}
// a section's world: the layout through the stage pipeline, then its pots; then you and the boss in their places
function cqlvBuild(S) {
  cqlvPurple(); ARENA = S.arena; const L = S.layout(); L.theme = S.theme; L.clouds = []; L.sym = 'free'; L.arch = 'open';
  genOpt = { easy: false, avoid: null, themes: [S.theme], flat: false }; applyLayout(L); rebuildSamples(); buildNav();
  POTS.length = 0; RIVALS.length = 0; POWER_SPOTS.length = 0; COF_SPOTS.length = 0; for (const p of L.pots) POTS.push(p);
  Object.assign(START, L.start); Object.assign(CSTART, { x: -L.start.x, z: -L.start.z, yaw: L.start.yaw + Math.PI });
  Object.assign(GEN, { seed: 400 + CQL.sec, sym: 'free', arch: 'open', tries: 1, fallback: false, easy: false, avoid: null, themes: [S.theme], flat: false, key: S.theme, std: false });
  const t0 = performance.now(); rebuildStage(); GEN.ms = performance.now() - t0; clearTrail(); placeObjects(level); shots.length = 0; drawShots();
  for (const o of CQL.g.children.slice()) { CQL.g.remove(o); if (o.geometry && !o.userData.keep) o.geometry.dispose(); } cqlvClearJel();
  if (L.slime) for (const [x, z, r] of L.slime) addSplat(x, 0, z, 0, r, dryClock - 30, false, true, 1); // (the canal, slimed already)
  CQL.foe = teamN[2] + 0.5 * teamN[6];
}
function cqlvPurple() { const t = { hex: 0xB25CFF, dry: 0x5A2A80, floor: 0xB25CFF }; TEAMS[1].wet = t.hex; TEAMS[1].dry = t.dry; TEAMS[1].css = '#B25CFF'; TEAM_COLS[1].setHex(t.hex); paintUniforms.uWetA.value[1].setHex(t.hex); paintUniforms.uDryA.value[1].setHex(t.dry); teamMats[1].color.setHex(t.hex); }
function cqlvEnter(i) {
  const S = CQL_SECS[i]; if (!S || !CQL) return; CQL.sec = i; CQL.t = 0; CQL.S = {}; CQL.cpSec = i; CQL.loading = true;
  irisClose(() => {
    building = true; cqlvBuild(S); cqlvPlace(START.x, START.z, START.yaw); CQL.cp = { x: START.x, z: START.z, yaw: START.yaw, prog: 0 };
    const Q = CQB; if (Q && Q.boss) { Q.follow = false; Q.lock = false; Q.cut = null; Q.boss.group.visible = true; Q.boss.lookAt(null); if (S.id === 'plaza') Q.auto = false; }
    if (Q && Q.el && !Q.el.classList.contains('fold')) { Q.el.classList.add('fold'); const f = $('cqbFold'); if (f) f.setAttribute('aria-expanded', 'false'); } // (the panel out of the way; its fold button opens it)
    cqlvSetup(S); CQL.loading = false; clearTimeout(warmQ); warmRender(); building = false; irisOpen(); banner(S.label, S.sub, true); AU.whoosh();
  }, null, S.label);
}
// a gate: a glowing ring on the floor with a beam of light; rolling into it takes you on
function cqlvGate(x, z, yaw, next) { const g = new THREE.Group(); const t = new THREE.Mesh(new THREE.TorusGeometry(2.0, 0.16, 8, 40), cqlvMat('gate')); t.rotation.x = Math.PI / 2; t.position.y = 0.12; g.add(t);
  const b = new THREE.Mesh(new THREE.CylinderGeometry(0.35, 0.9, 14, 12, 1, true), new THREE.MeshBasicMaterial({ color: 0xFFE070, transparent: true, opacity: 0.22, depthWrite: false, side: THREE.DoubleSide })); b.position.y = 7; g.add(b);
  g.position.set(x, Math.max(0, surfaceUnder(x, z, 12, true)), z); CQL.g.add(g); CQL.S.gate = { x, z, g, next, r: 2.0 }; return g; }
function cqlvBuoy(x, z, yaw, prog) { const g = new THREE.Mesh(new THREE.SphereGeometry(0.5, 12, 10), new THREE.MeshStandardMaterial({ color: 0x8C9AA4, emissive: 0x000000 })); g.position.set(x, Math.max(0, surfaceUnder(x, z, 12, true)) + 2.6, z); CQL.g.add(g);
  const m = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.6, 6), cqlvMat('pin')); m.position.set(x, g.position.y - 1.3, z); CQL.g.add(m); (CQL.S.cps = CQL.S.cps || []).push({ x, z, yaw, prog, g, on: false }); }
// the boss: where it swims this frame (after its own swim: it keeps to this anchor, high up or down low)
function cqlvBossAt(x, y, z, k) { const Q = CQB, b = Q && Q.boss; if (!b) return; const g = b.group.position, dt = CQL.dt || 0.05; Q.pool.set(x, 0, z); Q.home.copy(Q.pool); const a = 1 - Math.exp(-(k || 2.5) * dt);
  const ox = g.x, oz = g.z; g.x += (x - g.x) * a; g.z += (z - g.z) * a; g.y += (y - g.y) * a; Q.v.set((g.x - ox) / Math.max(dt, 1e-3), 0, (g.z - oz) / Math.max(dt, 1e-3)); }
// the boss's health: chips and big hits both go through here; at none it goes down (the demo's own defeat)
function cqlvDamage(k, big) { const B = CQB && cqbBar(); if (!B || !B.vis || B.hp <= 0) return; if (B.hold <= 0 || big) B.gh = Math.max(B.gh, B.hp); B.hp = Math.max(0, B.hp - k); B.fillT = -1; if (big) { B.hold = 0.5; cqbBarHit(); } CQL.hp = B.hp; if (B.hp <= 0.001) B.defIn = 0.75; }
function cqlvBump(x, z, power, why) { // a sting or a shove: knocked back, no life lost
  if (state !== 'play' || P.st !== 'play' || P.immuneT > 0 || P.rollT > 0 || safe(P)) return false;
  const dx = P.x - x, dz = P.z - z, d = Math.hypot(dx, dz), nx = d > 0.05 ? dx / d : -Math.sin(P.yaw), nz = d > 0.05 ? dz / d : -Math.cos(P.yaw), v = 4.5 + 2 * power;
  if (P.charging) clearCharge(P); holdCharge = false; slingOff(); P.kx = nx * v; P.kz = nz * v; P.spd *= 0.4; if (!P.air) { P.air = true; P.stroke++; P.vy = 3.4; } else P.vy = Math.max(P.vy, 2);
  P.knockT = Math.max(P.knockT, 0.45); P.wob = 1; P.squash = Math.max(P.squash, 0.5); P.immuneT = Math.max(P.immuneT, 0.8); P.paint = Math.max(0, P.paint - 0.1); fxTumble(P, 0.6, Math.random() - 0.5, nx, nz);
  emote(P, 'ouch', 0.7); AU.bonk(0.8); shake = Math.max(shake, 0.2); buzz(15); popText(why || 'Stung!'); return true;
}

// ---- the jellets: the boss's babies, simplified. They drift after you, slime the floor and sting; a pound, a roll, a giant or a
// whirlwind pops them, and each pop sends a spark back into the boss ----
let cqlvJelG = null;
function cqlvJelGeo() { if (cqlvJelG) return cqlvJelG; const parts = []; const bell = new THREE.SphereGeometry(0.46, 14, 10, 0, 6.2832, 0, 1.9); bell.scale(1, 0.75, 1); parts.push(bell);
  for (let i = 0; i < 6; i++) { const a = i / 6 * 6.2832, t = new THREE.CylinderGeometry(0.03, 0.05, 0.9, 5); t.translate(Math.cos(a) * 0.26, -0.5, Math.sin(a) * 0.26); parts.push(t); }
  const G = new THREE.BufferGeometry(), pos = [], nrm = []; for (const g of parts) { const p = g.attributes.position, n = g.attributes.normal, ix = g.index; for (let k = 0; k < ix.count; k++) { const q = ix.getX(k); pos.push(p.getX(q), p.getY(q), p.getZ(q)); nrm.push(n.getX(q), n.getY(q), n.getZ(q)); } }
  G.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); G.setAttribute('normal', new THREE.Float32BufferAttribute(nrm, 3)); return cqlvJelG = G; }
function cqlvJelSpawn(x, z, arm) { const m = new THREE.Mesh(cqlvJelGeo(), arm ? cqlvMat('jelArm') : cqlvMat('jel')); m.castShadow = true; CQL.g.add(m);
  const y0 = Math.max(0, surfaceUnder(x, z, 12, true)); m.position.set(x, y0 + 6, z); const j = { x, z, y: y0 + 6, vx: 0, vz: 0, m, arm: !!arm, hp: arm ? 2 : 1, ph: Math.random() * 6.28, paintT: 0.5 + Math.random(), on: true, t: 0 }; CQL.jel.push(j); return j; }
function cqlvJelPop(j, by) { if (!j.on) return; if (j.arm && j.hp > 1) { j.hp = 1; j.arm = false; j.m.material = cqlvMat('jel'); j.vx *= -1; j.vz *= -1; j.y += 0.8; shockwave(j.x, j.y, j.z, 1.1, 0xFFFFFF); AU.bonk(0.6); popText('Cracked!'); return; }
  j.on = false; CQL.g.remove(j.m); CQL.pops++; shockwave(j.x, j.y, j.z, 1.6, 0xB25CFF); AU.pop(); buzz(10); popText('Popped!');
  for (let i = 0; i < 14; i++) { const a = Math.random() * 6.283; spawnPart(j.x, j.y, j.z, Math.cos(a) * 3, 1 + Math.random() * 3, Math.sin(a) * 3, 0.5, tmat(H), 0.5); }
  const b = CQB && CQB.boss; if (b && b.group.visible) { b.bellPoint(CQB.bell); const bp = CQB.bell, n = 10; for (let i = 0; i < n; i++) { const f = 0.18 + i * 0.06; spawnPart(j.x + (bp.x - j.x) * f, j.y + (bp.y - j.y) * f, j.z + (bp.z - j.z) * f, (bp.x - j.x) * 1.2, (bp.y - j.y) * 1.2 + 1, (bp.z - j.z) * 1.2, 0.45, cqlvSparkMat(), 0.3, 0); } }
  cqlvDamage(CQLV.pop, false); cqlvFlashBar();
}
let cqlvSpark = null; function cqlvSparkMat() { return cqlvSpark || (cqlvSpark = new THREE.MeshBasicMaterial({ color: 0xFFE070 })); }
function cqlvClearJel() { for (const j of CQL.jel) if (j.on) CQL.g.remove(j.m); CQL.jel.length = 0; }
function cqlvJelTick(dt) {
  const live = CQL.jel.filter(j => j.on); if (CQL.jel.length > live.length) CQL.jel = live;
  for (const j of live) { j.t += dt; j.ph += dt * 2.6; const dx = P.x - j.x, dz = P.z - j.z, d = Math.hypot(dx, dz) || 1, chase = P.st === 'play' && d < 26 ? 1 : 0;
    const sp = CQLV.jelSpd * (j.arm ? 0.8 : 1); j.vx += ((dx / d) * sp * chase - j.vx) * Math.min(1, dt * 1.6); j.vz += ((dz / d) * sp * chase - j.vz) * Math.min(1, dt * 1.6);
    const nx = j.x + j.vx * dt, nz = j.z + j.vz * dt; if (Math.abs(nx) < ARENA - 0.5 && Math.abs(nz) < ARENA - 0.5) { j.x = nx; j.z = nz; } else { j.vx *= -1; j.vz *= -1; }
    const g = surfaceUnder(j.x, j.z, j.y + 2, true), fy = (g > -Infinity ? g : 0) + 0.95 + Math.sin(j.ph) * 0.12; j.y += (fy - j.y) * Math.min(1, dt * (j.t < 1.2 ? 1.2 : 3));
    j.m.position.set(j.x, j.y, j.z); j.m.rotation.set(j.vz * 0.08, 0, -j.vx * 0.08); const s = 1 + 0.06 * Math.sin(j.ph * 1.5); j.m.scale.set(s, 1 / s, s);
    if ((j.paintT -= dt) <= 0 && g > -Infinity && j.y - g < 1.3) { j.paintT = 0.55; const before = teamN[2] + 0.5 * teamN[6]; addSplat(j.x, g, j.z, 0, 0.75, dryClock, true, true, 1); CQL.foe += teamN[2] + 0.5 * teamN[6] - before; }
    // you: a roll, a giant, a whirlwind or a pound pops it; otherwise its touch stings
    if (d < PR + 0.62 && Math.abs(P.y - (j.y - 0.6)) < 1.3) { if (P.rollT > 0 || P.giantT > 0 || P.whirl || P.dashT > 0) cqlvJelPop(j, P); else if (P.st === 'play') { j.vx = -dx / d * 3; j.vz = -dz / d * 3; cqlvBump(j.x, j.z, 0.6, 'Stung!'); } }
  }
}
// a pound landed: the jellets in its splat pop; the pinned boss's bell under it takes a big hit
function cqlvSlam(D, R) {
  if (!CQL || D !== P) return; cqlvCrack(D); for (const j of CQL.jel) if (j.on && Math.hypot(j.x - D.x, j.z - D.z) < R + 0.5 && Math.abs(j.y - 0.6 - D.y) < 1.6) cqlvJelPop(j, D);
  const S = CQL.S, b = CQB && CQB.boss; if (S.pinned && b) { b.bellPoint(CQB.bell); const bp = CQB.bell; if (Math.hypot(bp.x - D.x, bp.z - D.z) < b.bellR + R && Math.abs(bp.y - D.y) < 4.5) { S.bellHits = (S.bellHits || 0) + 1; cqlvDamage(CQLV.bell, true); b.play('hurt', { x: D.x, z: D.z }); shake = Math.max(shake, 0.6); popText('Hit! ' + S.bellHits + '/' + CQLV.bellN); if (S.bellHits >= CQLV.bellN) cqlvUnpin(true); } }
}
function cqlvFlashBar() { const B = CQB && CQB.bar; if (B && B.vis && B.hitT <= 0) cqbBarHit(); }

// ---- the course: a polyline the runner follows; where along it you (or the collapse) are ----
function cqlvProg(path, x, z) { let best = 0, bd = 1e9, acc = 0; for (let i = 0; i + 1 < path.length; i++) { const [ax, az] = path[i], [bx, bz] = path[i + 1], ex = bx - ax, ez = bz - az, L = Math.hypot(ex, ez) || 1, t = clamp(((x - ax) * ex + (z - az) * ez) / (L * L), 0, 1), px = ax + ex * t, pz = az + ez * t, d = Math.hypot(x - px, z - pz); if (d < bd) { bd = d; best = acc + L * t; } acc += L; } return best; }
function cqlvPathAt(path, s) { let acc = 0; for (let i = 0; i + 1 < path.length; i++) { const [ax, az] = path[i], [bx, bz] = path[i + 1], L = Math.hypot(bx - ax, bz - az) || 1; if (s <= acc + L || i + 2 === path.length) { const t = clamp((s - acc) / L, 0, 1); return { x: ax + (bx - ax) * t, z: az + (bz - az) * t, dx: (bx - ax) / L, dz: (bz - az) / L }; } acc += L; } return { x: path[0][0], z: path[0][1], dx: 0, dz: 1 }; }

// ---- the sections ----
// the Aqueduct Run: one path, a stone causeway half a metre above a sea of slime, in an S across the square; off the path is the
// slime, and the slime is death. Gaps to jump, a basin a leg (at the lane's edge, or on a ledge a hop off it)
const CQL_RUN_PATH = [[-24, -31], [-24, 26], [0, 26], [0, -26], [24, -26], [24, 30]];
function cqlvRunLayout() {
  const H = 0.5, W = 4, boxes = [], leg = (x0, x1, z0, z1) => boxes.push([x0, x1, z0, z1, 0, H]);
  // leg 1 up the left (gaps at z 2 and 14), the top cross, leg 3 down the middle (gaps at 8 and -6), the bottom cross, leg 5 up the right (gaps at -8, 4, 16)
  leg(-24 - W, -24 + W, -33, -0.5); leg(-24 - W, -24 + W, 2.5, 12.5); leg(-24 - W, -24 + W, 15.5, 22);
  leg(-24 - W, 4, 22, 30);
  leg(-W, W, 11, 22); leg(-W, W, -3.5, 8); leg(-W, W, -22, -6.5);
  leg(-W, 28, -30, -22);
  leg(20, 28, -22, -10.5); leg(20, 28, -7.5, 1); leg(20, 28, 4, 13); leg(20, 28, 16, 33);
  // ledges with a basin, a hop off the lane
  boxes.push([-33, -29.5, -14, -10, 0, H], [10, 13.5, -18, -14, 0, H]);
  const pots = [[-31.25, H, -12], [-12, H, 28.8], [11.75, H, -16], [26.8, H, 6]];
  return { boxes, ramps: [], holes: [[-32.9, 32.9, -32.9, 32.9, 0, 0]], pots, slime: [], start: { x: -24, z: -29, yaw: 0 } };
}
// the Sunken Plaza: a square court, blocks to hop, four valve pads up on plinths at the corners (only the turret's lobs reach them)
function cqlvPlazaLayout() {
  const boxes = [], pots = [[-6, 0, -22], [6, 0, 22], [-22, 0, 6], [22, 0, -6]];
  for (const [x, z] of [[-17, -17], [17, -17], [-17, 17], [17, 17]]) boxes.push([x - 1.6, x + 1.6, z - 1.6, z + 1.6, 0, 2.6, undefined, 'plinth']);
  for (const [x, z, w] of [[-8, 0, 1.6], [8, 0, 1.6], [0, -9, 1.6], [0, 9, 1.6], [-13, 7, 1.1], [13, -7, 1.1]]) boxes.push([x - w, x + w, z - w, z + w, 0, 1.0]);
  return { boxes, ramps: [], holes: [], pots, slime: [], start: { x: 0, z: -22, yaw: 0 } };
}
Object.assign(CQL_SECS[1], { layout: cqlvRunLayout }); Object.assign(CQL_SECS[2], { layout: cqlvPlazaLayout });

function cqlvSetup(S) {
  const X = CQL.S;
  if (S.id === 'run') {
    X.path = CQL_RUN_PATH; X.len = cqlvProg(X.path, 24, 30); X.front = -12; X.grace = CQLV.frontGrace; X.slamT = 4; X.diveT = 9; X.jelT = 6; X.boss = { y: 3, low: 0 };
    cqlvBuoy(-24, 27, Math.PI / 2, cqlvProg(X.path, -24, 27)); cqlvBuoy(0, -27, -Math.PI / 2, cqlvProg(X.path, 0, -27)); cqlvGate(24, 30, 0, 2);
    const fr = new THREE.Mesh(new THREE.BoxGeometry(12, 9, 1.2), cqlvMat('front')); fr.position.y = 3; CQL.g.add(fr); X.frontM = fr;
    X.cracked = BOXES.filter(b => b[7] === 'cracked').map(b => ({ b, f: floaters.find(f => f.b === b), broken: false }));
    cqlvBossAt(-24, 3, -14, 50); banner('After it!', 'Keep ahead of the collapse', true);
  } else if (S.id === 'plaza') {
    X.wave = 0; X.waveT = 2.5; X.pads = BOXES.filter(b => b[7] === 'plinth').map(b => ({ b, k: 0, on: false, m: null })); X.boss = { y: 1.5 };
    for (const p of X.pads) { const m = new THREE.Mesh(new THREE.CylinderGeometry(1.35, 1.35, 0.1, 24), cqlvMat('pad')); m.position.set((p.b[0] + p.b[1]) / 2, p.b[5] + 0.05, (p.b[2] + p.b[3]) / 2); CQL.g.add(m); p.m = m; }
    cqlvBossAt(0, 1.5, 3, 50); X.phase = 'waves'; X.turret = false;
  }
}
// the collapse: a wall of dark water and rubble coming along the causeway behind you; caught on the causeway behind it, the stone
// gives and you fall (the canal below is under it too: nothing behind the front is safe)
function cqlvRunTick(dt) {
  const X = CQL.S, Q = CQB, b = Q && Q.boss, pr = cqlvProg(X.path, P.x, P.z);
  if (X.grace > 0) X.grace -= dt; else X.front += dt * VS_CFG.speed * CQLV.frontK * (pr - X.front > 26 ? 1.25 : 1);
  const fp = cqlvPathAt(X.path, X.front); X.frontM.position.set(fp.x, 3.6, fp.z); X.frontM.rotation.y = Math.atan2(fp.dx, fp.dz); X.frontM.scale.y = 1 + 0.06 * Math.sin(clock * 7);
  if (Math.random() < dt * 30) spawnPart(fp.x + (Math.random() - 0.5) * 9, 0.4 + Math.random() * 3.5, fp.z + (Math.random() - 0.5) * 2, (Math.random() - 0.5) * 2, 1.5 + Math.random() * 2, (Math.random() - 0.5) * 2, 0.7, cqlvMat('front'), 0.4 + Math.random() * 0.4);
  if (pr < X.front - 0.5 && P.st === 'play' && state === 'play') { knockOut(P, 'fall'); popText('The stone gave way!'); }
  // the checkpoints and the gate
  for (const c of X.cps || []) if (!c.on && Math.hypot(P.x - c.x, P.z - c.z) < 4.5) { c.on = true; c.g.material.emissive.set(TEAMS[0].wet); CQL.cp = { x: c.x, z: c.z, yaw: c.yaw, prog: c.prog }; cqlvCheckpoint(); }
  // the boss: ahead and above the course; every so often a slam on the lane ahead (a ring, then the shock), a dive to slime the lane,
  // a pair of jellets dropped in your way
  const ahead = cqlvPathAt(X.path, Math.min(X.len - 2, pr + 13)); X.boss.low = Math.max(0, X.boss.low - dt);
  cqlvBossAt(ahead.x, X.boss.low > 0 ? -2.6 : 3.2, ahead.z, X.boss.low > 0 ? 3 : 1.6);
  if (b && b.isReady && !b.busy && state === 'play') {
    if ((X.slamT -= dt) <= 0) { X.slamT = CQLV.slamEvery; const at = cqlvPathAt(X.path, Math.min(X.len - 2, pr + 7)); const tx = at.x + (Math.random() - 0.5) * 4, tz = at.z + (Math.random() - 0.5) * 4; cqxWarn(tx, tz, 1.1); b.play('slam', { x: tx, z: tz });
      X.pend = { t: 1.1, x: tx, z: tz }; }
    else if ((X.diveT -= dt) <= 0) { X.diveT = CQLV.diveEvery; X.boss.low = 4.2; cqbSfx('b_churn'); }
    else if ((X.jelT -= dt) <= 0) { X.jelT = CQLV.jelEvery; const at = cqlvPathAt(X.path, Math.min(X.len - 2, pr + 16)); cqlvJelSpawn(at.x - at.dz * 2, at.z + at.dx * 2); cqlvJelSpawn(at.x + at.dz * 2, at.z - at.dx * 2); }
  }
  if (X.pend && (X.pend.t -= dt) <= 0) { const p = X.pend; X.pend = null; cqxRing(p.x, p.z, 2, 0.55, 4.6); cqbSfx('b_slam', { at: [p.x, p.z] }) || AU.quake(); shake = Math.max(shake, 0.35); if (Math.hypot(P.x - p.x, P.z - p.z) < 3.4 && !P.air) cqbKnock(p.x, p.z, 1.2); }
  if (X.boss.low > 0 && b && b.group.visible) { X.slimeT = (X.slimeT || 0) - dt; if (X.slimeT <= 0) { X.slimeT = 0.12; const g = b.group.position, y = surfaceUnder(g.x, g.z, 6, true); if (y > -Infinity) { const before = teamN[2] + 0.5 * teamN[6]; addSplat(g.x, y, g.z, 0, 1.5, dryClock, false, true, 1); CQL.foe += teamN[2] + 0.5 * teamN[6] - before; } } }
  // the cracked slabs: broken through by a pound, they drop away into the canal
  for (const c of X.cracked) if (c.broken && c.f && c.f.drop != null) { c.f.drop += dt; const m = stageGroup.children.find(o => o.userData.ownMats === c.f.mats); if (m) { m.position.y = -c.f.drop * c.f.drop * 6; m.visible = c.f.drop < 1.2; } }
}
function cqlvCrack(D) { const X = CQL.S; if (!X.cracked) return; for (const c of X.cracked) if (!c.broken && inR(D.x, D.z, c.b, 0.7) && Math.abs(D.y - c.b[5]) < 0.6) { c.broken = true; const i = BOXES.indexOf(c.b); if (i >= 0) BOXES.splice(i, 1); buildQGrid(); if (c.f) { c.f.hull.visible = false; c.f.drop = 0; } popText('Through!'); AU.quake(); shake = Math.max(shake, 0.3); } }
function cqlvCheckpoint() { popText('Checkpoint'); AU.ready(); const Q = CQB; if (Q && Q.life < 3) { Q.life = 3; cqlShow('gain'); } if (CQL.S.front != null) CQL.S.front = Math.min(CQL.S.front, CQL.cp.prog - 10); }
// the plaza: waves of jellets, then the turret and the valve pads; all four painted, the boss is pinned low in the middle, pound it
function cqlvPlazaTick(dt) {
  const X = CQL.S, Q = CQB, b = Q && Q.boss; if (!b || !b.isReady) return; const live = CQL.jel.length;
  if (X.phase === 'waves') {
    cqlvBossAt(Math.sin(clock * 0.35) * 5, 2.2, 3 + Math.cos(clock * 0.27) * 4, 1.2);
    if (live === 0 && (X.waveT -= dt) <= 0) {
      if (X.wave >= CQLV.waves.length) { X.phase = 'valves'; banner('Arm the valves!', 'Your turret: plant it facing a pad', true); X.turret = true; P.held = 'turret'; }
      else { const n = CQLV.waves[X.wave]; X.wave++; X.waveT = 2.5; banner('Wave ' + X.wave, n + ' of its babies', true); b.play('taunt', {}); cqbSfx('b_taunt');
        for (let i = 0; i < n; i++) { const a = i / n * 6.2832 + X.wave, r = 5 + (i % 3) * 2; cqlvJelSpawn(b.group.position.x + Math.cos(a) * r, b.group.position.z + Math.sin(a) * r, X.wave >= 2 && i % 3 === 0); } }
    }
    if (X.wave === 2 && live > 0 && Math.random() < dt * 0.12 && !b.busy) b.play('rain', { x: P.x, z: P.z });
  } else if (X.phase === 'valves') {
    cqlvBossAt(Math.sin(clock * 0.3) * 3, 1.6, Math.cos(clock * 0.3) * 3, 1.2);
    if (!P.held && !P.turret && !X.turretT) X.turretT = 2.2; if (X.turretT && (X.turretT -= dt) <= 0) { X.turretT = 0; if (!P.turret && P.st === 'play') { P.held = 'turret'; popText('Turret ready again'); } }
    let armed = 0; for (const p of X.pads) { if (!p.on) { let n = 0, on = 0; for (const k of cqlvRectCells(p.b)) if (Math.abs(sY[k] - p.b[5]) < 0.2 && inR(sX[k], sZ[k], p.b)) { n++; if (painted[k] === 1 || painted[k] === 5) on++; } p.k = n ? on / n : 0;
        if (p.k >= CQLV.valveK) { p.on = true; p.m.material = cqlvMat('padOn'); p.m.position.y += 0.4; shockwave(p.m.position.x, p.m.position.y, p.m.position.z, 2.5, 0xFFE070); AU.ready(); popText('Valve armed ' + (X.pads.filter(q => q.on).length) + '/4'); } }
      if (p.on) armed++; }
    if (armed === 4) { X.phase = 'pinned'; X.pinned = true; X.pinT = CQLV.stun; X.bellHits = 0; P.held = null; b.play('stunned', { time: CQLV.stun }); banner('Pinned!', 'Pound its bell, ' + CQLV.bellN + ' times', true); cqbSfx('b_lock'); for (const p of X.pads) { shockwave(p.m.position.x, p.m.position.y, p.m.position.z, 4, 0xFFFFFF); } }
    if (Math.random() < dt * 0.1 && !b.busy && live < 3) { cqlvJelSpawn(b.group.position.x + 4, b.group.position.z); }
  } else if (X.phase === 'pinned') {
    cqlvBossAt(0, -1.2, 0, 2.5); if ((X.pinT -= dt) <= 0) cqlvUnpin(false);
  } else if (X.phase === 'free') {
    cqlvBossAt(0, 2.2, 3, 1.2); if ((X.freeT -= dt) <= 0) { X.phase = 'valves'; for (const p of X.pads) { p.on = false; p.k = 0; p.m.material = cqlvMat('pad'); p.m.position.y -= 0.4; } banner('It shook the nets off', 'Arm the valves again', true); }
    if (live === 0 && Math.random() < dt * 0.5) for (let i = 0; i < 3; i++) cqlvJelSpawn(b.group.position.x + Math.cos(i * 2.1) * 4, b.group.position.z + Math.sin(i * 2.1) * 4);
  } else if (X.phase === 'won') { cqlvBossAt(0, 4 + X.wonT * 3, 20 + X.wonT * 6, 1.5); X.wonT += dt; if (X.wonT > 3 && !X.gateUp) { X.gateUp = true; cqlvGate(0, 22, 0, 'end'); banner('It fled again', 'Roll into the light', true); } }
  if (X.phase !== 'won' && Math.random() < dt * 0.5 && b.group.visible && X.phase !== 'pinned') { X.slimeT = (X.slimeT || 0) - 1; } // (its slime: dropped as it swims)
  if (X.phase !== 'pinned' && X.phase !== 'won' && b.group.visible) { X.dripT = (X.dripT || 0) - dt; if (X.dripT <= 0) { X.dripT = 0.9; const g = b.group.position, y = surfaceUnder(g.x, g.z, 6, true); if (y > -Infinity) { const before = teamN[2] + 0.5 * teamN[6]; addSplat(g.x + (Math.random() - 0.5) * 3, y, g.z + (Math.random() - 0.5) * 3, 0, 1.1, dryClock, false, true, 1); CQL.foe += teamN[2] + 0.5 * teamN[6] - before; } } }
}
function cqlvRectCells(b) { const out = [], i0 = clamp(Math.floor((b[0] + ARENA) / CELL), 0, GN - 1), i1 = clamp(Math.floor((b[1] + ARENA) / CELL), 0, GN - 1), j0 = clamp(Math.floor((b[2] + ARENA) / CELL), 0, GN - 1), j1 = clamp(Math.floor((b[3] + ARENA) / CELL), 0, GN - 1); for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) for (const k of grid[j * GN + i]) out.push(k); return out; }
function cqlvUnpin(done) { const X = CQL.S, b = CQB.boss; X.pinned = false; if (done) { X.phase = 'won'; X.wonT = 0; b.play('hurt', { x: P.x, z: P.z }); banner('Enough!', 'It tears loose', true); } else { X.phase = 'free'; X.freeT = 4; b.play('taunt', {}); } }

// ---- the frame ----
function cqlvTick(dt, rdt) {
  const L = CQL; if (!L || !CQP || L.loading) return; L.dt = dt; L.t += dt; const Q = CQB, b = Q && Q.boss;
  if (!L.hooked && b) { L.hooked = true; b.on('emergeDone', () => { if (CQL && CQL.sec <= 0) { CQL.S.fleeT = 1.6; } }); }
  // the keep: once the entrance is over, the boss taunts and flees over the wall; the gate lights where it went
  if (L.sec <= 0) { const X = L.S; if (X.fleeT != null && state === 'play') { X.fleeT -= dt; if (!X.taunted && b) { X.taunted = true; b.play('taunt', {}); }
      if (X.fleeT <= 0) { X.fly = (X.fly || 0) + dt; const k = Math.min(1, X.fly / 2.6); if (b) { Q.follow = false; Q.lock = false; cqlvBossAt(0, 2 + k * 14, -k * 26, 6); }
        if (!X.gate && X.fly > 0.4) { cqlvGate(0, -14.5, Math.PI, 1); banner('After it!', 'Roll into the light', true); emote(P, 'glee', 1.2); }
        if (X.fly > 3 && b && b.group.visible) b.group.visible = false; } } }
  else if (state === 'play') { const S = CQL_SECS[L.sec]; if (S.id === 'run') cqlvRunTick(dt); else if (S.id === 'plaza') cqlvPlazaTick(dt); }
  if (state === 'play') cqlvJelTick(dt);
  // the gate
  const G = L.S.gate; if (G) { G.g.rotation.y += rdt * 0.8; G.g.scale.setScalar(1 + 0.05 * Math.sin(clock * 4)); if (P.st === 'play' && state === 'play' && Math.hypot(P.x - G.x, P.z - G.z) < G.r + PR && !irisBusy) { L.S.gate = null; CQL.g.remove(G.g); if (G.next === 'end') cqlvFinish(); else cqlvEnter(G.next); } }
  // chip damage: the boss's slime you've covered this frame
  const foe = teamN[2] + 0.5 * teamN[6], gone = L.foe - foe; L.foe = foe; if (gone > 0.5 && state === 'play') { L.chipAcc += gone; L.chip += gone * CQLV.chip; cqlvDamage(gone * CQLV.chip, false); }
  if (L.chipAcc > 0 && (L.chipT -= rdt) <= 0) { L.chipT = 0.5; if (L.chipAcc >= 6) { cqlvFlashBar(); if (b && b.isReady && b.group.visible && !b.busy && L.chipAcc > 40) b.face('hurt', 0.4); } L.chipAcc = 0; }
  cqlvHud();
}
function cqlvHud() { let h = $('cqlHud'); if (!h) { h = document.createElement('div'); h.id = 'cqlHud'; h.style.cssText = 'position:fixed;left:50%;transform:translateX(-50%);bottom:10px;text-align:center;white-space:pre;z-index:30;font:600 11px/1.3 system-ui;color:#fff;text-shadow:0 1px 2px #000;pointer-events:none;opacity:.85'; document.body.appendChild(h); }
  const on = !!CQL && (state === 'play' || state === 'paused'); if (h.hidden === on) h.hidden = !on; if (!on) return; const L = CQL, S = CQL_SECS[Math.max(0, L.sec)];
  const t = ((performance.now() - L.t0) / 1000) | 0, txt = S.label + ' · ' + Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0') + '\nchip ' + (L.chip * 100).toFixed(1) + '% · pops ' + L.pops + ' · hp ' + Math.round(L.hp * 100) + '%' + (L.S.front != null ? '\ncollapse ' + Math.round(cqlvProg(L.S.path, P.x, P.z) - L.S.front) + ' m back' : '');
  if (h.textContent !== txt) h.textContent = txt; }
// a life gone to a fall: back at the last checkpoint (the demo's own respawn picks a basin; here it's the buoy you passed)
function cqlvRespawn(D) { const c = CQL.cp; if (!c) return respawnBlob(D); CQL.deaths++; cqlvPlace(c.x, c.z, c.yaw); D.immuneT = SPAWN_SAFE; D.spawnImm = true; D.paint = 0.7; if (CQL.S.front != null) { CQL.S.front = c.prog - 12; CQL.S.grace = 3; } if (kof) kofOpen(); else flashScreen(); AU.flip(); }
function cqlvLost(reason) { const Q = CQB; if (!Q || reason === 'boom') return; Q.life = Math.max(0, (Q.life == null ? 3 : Q.life) - 1); cqlShow(true); }
// the milestone's end: a card with the run's numbers, then the menu
function cqlvFinish() { const L = CQL, t = ((performance.now() - L.t0) / 1000) | 0; banner('Section cleared!', Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0') + ' · chip ' + (L.chip * 100).toFixed(1) + '% · ' + L.pops + ' pops · ' + L.deaths + ' falls', true); cqiWin(); AU.sting('win'); setTimeout(() => { if (CQL) toMenu(); }, 4200); }
// the boss panel's own row for the level: jump to a section
function cqlvPanel() { const el = $('cqbPanel'); if (!el || el.querySelector('.cqlrow')) return; const row = document.createElement('div'); row.className = 'cqbs cqlrow'; row.innerHTML = '<button type="button" data-sec="0">Keep</button><button type="button" data-sec="1">Aqueduct</button><button type="button" data-sec="2">Plaza</button>'; el.appendChild(row);
  row.addEventListener('click', e => { const t = e.target.closest('button'); if (!t || !CQL) return; e.stopPropagation(); const i = +t.dataset.sec; if (i === 0) { toMenu(); setTimeout(() => cqlvOpen(), 1400); } else cqlvEnter(i); }); }
window.cqlvOpen = cqlvOpen; window.cqlvEnter = cqlvEnter;
