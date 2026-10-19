"""v384: two new strokes bought with dabs, and Swim faster easier to hold on a wet canvas.

- Paint Storm (a special, 600 dabs): the orb brings a storm cloud of your paint. It gathers over you and for 5 seconds hangs a little
  ahead of you wherever you go, dropping big globs of your paint: each lands like a small pound, a splat of your colour, and a rival
  under it is knocked out. A ring on the floor shows where each will land a beat before it does, so a rival can get out of the way, jump
  it or roll through it; anyone down in a basin or up in a rocket is safe. About a third of the drops go looking for the rival nearest
  the storm (half of a CPU's). Coverage first, with a real threat: you lead the storm over their ground, or over them.
- Aftershock (a skill, 400 dabs): your pound lands twice. A beat after it hits, a second ring of your paint bursts out from the spot,
  out to twice the pound's reach (up to 7), and a rival it catches on the ground is knocked off its feet, stunned and spills a fifth of
  its paint; a jump or a roll gets you over it, and a giant shrugs it off. It leaves a ring of paint where it stops. It punishes the usual
  way out of a pound, stepping just outside it. (Offline only, as the other skills; a giant's pound has its own quake instead.)
- Both on the Strokes page with Ludo-painted pictures in the same style as the others, and the Paint Storm with its own 3D demo. CPUs get
  the storm from the orb now and then, hold it until someone's near, and on the receiving end sometimes roll out from under a drop or
  over an aftershock (more often on hard).
- Swim faster in the rain: the rain's speed-up is 1.6x now, not 2x (for everyone it speeds up), and at that speed you turn tighter,
  so a fast roll on a wet canvas holds its line instead of running wide."""
import base64, os

A = os.path.dirname(os.path.abspath(__file__)) + '/assets/'

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

STORM_JS = r"""
// ---------- (v384) Paint Storm: a storm cloud of your paint gathers over you and, for STORM_T seconds, hangs a little ahead of you,
// dropping big globs of your paint wherever you lead it. Each lands like a small pound: a splat of your colour, and a rival under it is
// out. A ring on the floor shows where each will land a beat before it does (get out of the way, jump it, or roll through it); anyone
// down in a basin or up in a rocket is safe. Some of the drops go looking for the rival nearest the storm ----------
const STORM_FORM = 0.6, STORM_T = 5, STORM_EVERY = 0.2, STORM_FALL = 0.62, STORM_R = 1.7, STORM_KO = 1.2, STORM_AREA = 5.2, STORM_LEAD = 4.4, STORM_H = 7.2, STORM_CK = 0.85, STORM_CAM = 7, STORM_SEEK = 0.34, stormList = [], stormPool = [];
const STORM_PUFF = new THREE.IcosahedronGeometry(1, 2), STORM_GLOB = new THREE.LatheGeometry(Array.from({ length: 17 }, (_, i) => { const th = Math.PI * (1 - i / 16); return new THREE.Vector2(0.32 * Math.sin(th) * Math.pow(Math.sin(th / 2), 1.4) + 1e-4, 0.36 * Math.cos(th)); }), 16), /* (a teardrop, point up) */ STORM_RING = new THREE.RingGeometry(0.84, 1, 56), STORM_DISC = new THREE.CircleGeometry(1, 48);
// the cloud: dark puffs underneath, lighter ones on top, each with its ink line
const STORM_PUFFS = [[0, 0, 0, 1.55, 1], [1.5, -0.12, 0.35, 1.15, 0], [-1.55, -0.08, -0.25, 1.2, 0], [0.55, 0.42, -1.15, 1.1, 1], [-0.65, 0.36, 1.05, 1.05, 1], [2.55, -0.4, -0.45, 0.82, 0], [-2.5, -0.35, 0.55, 0.86, 0], [0.25, -0.5, 1.75, 0.82, 0], [0.05, -0.45, -2.0, 0.88, 0], [1.0, 0.95, 0.35, 0.86, 1], [-1.1, 0.8, -0.5, 0.8, 1]];
const stormFlat = () => ({ color: 0xFFFFFF, transparent: true, opacity: 1, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -10, polygonOffsetUnits: -10, fog: false });
function makeStormCloud(team) {
  const c = new THREE.Color(TEAMS[team].wet), dark = toon(c.clone().multiplyScalar(0.58), { emissive: new THREE.Color(0) }), lite = toon(c.clone().lerp(COL_WHITE, 0.2), { emissive: new THREE.Color(0) }), g = new THREE.Group();
  for (const [x, y, z, r, l] of STORM_PUFFS) { const m = new THREE.Mesh(STORM_PUFF, l ? lite : dark), h = new THREE.Mesh(STORM_PUFF, crownHullMat); m.position.set(x, y, z); h.position.set(x, y, z); m.scale.set(r, r * 0.78, r); h.scale.set(r * 1.07, r * 0.84, r * 1.07); g.add(m, h); }
  g.userData.mats = [dark, lite]; return g;
}
function stormTake(D) {
  let d = stormPool.pop();
  if (!d) { const g = new THREE.Group(), m = new THREE.Mesh(STORM_GLOB, tmat(D)), h = new THREE.Mesh(STORM_GLOB, crownHullMat); h.scale.setScalar(1.14); g.add(m, h);
    const ring = new THREE.Mesh(STORM_RING, new THREE.MeshBasicMaterial(stormFlat())), fill = new THREE.Mesh(STORM_DISC, new THREE.MeshBasicMaterial(stormFlat())); ring.rotation.x = fill.rotation.x = -Math.PI / 2; ring.renderOrder = 7; fill.renderOrder = 6;
    d = { g, m, ring, fill }; scene.add(g, ring, fill); }
  d.m.material = tmat(D); d.fill.material.color.set(TEAMS[D.team].wet); d.g.visible = false; d.ring.visible = d.fill.visible = true; return d;
}
function stormGive(d) { d.g.visible = d.ring.visible = d.fill.visible = false; stormPool.push(d); }
function startStorm(D) {
  for (const S of stormList) if (S.by === D) S.end = true; // (one storm each at a time)
  const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), g = makeStormCloud(D.team), sh = new THREE.Mesh(STORM_DISC, new THREE.MeshBasicMaterial(Object.assign(stormFlat(), { color: 0x171320, opacity: 0 })));
  sh.rotation.x = -Math.PI / 2; sh.renderOrder = 5; sh.visible = false;
  const S = { by: D, t: 0, next: STORM_FORM, cx: D.x + fx * STORM_LEAD * 0.6, cz: D.z + fz * STORM_LEAD * 0.6, cy: D.y + STORM_H, g, sh, drops: [], fl: 0, flT: 0.4, fade: 0, end: false, drip: 0 };
  g.position.set(S.cx, S.cy, S.cz); g.scale.setScalar(0.01); scene.add(g, sh); stormList.push(S);
  D.wob = 1; D.squash = 0.7; emote(D, 'glee', 1.2); hitStop(0.05, D); shockwave(D.x, D.y, D.z, 2.6, TEAMS[D.team].wet);
  for (let i = 0; i < 18; i++) { const a = Math.random() * 6.283, s = 0.6 + Math.random() * 1.4; spawnPart(D.x + Math.cos(a) * 0.4, D.y + 0.4, D.z + Math.sin(a) * 0.4, Math.cos(a) * s + fx * 1.5, 6 + Math.random() * 5, Math.sin(a) * s + fz * 1.5, 0.6 + Math.random() * 0.3, tmat(D), 0.5 + Math.random() * 0.4); }
  if (hearable(D)) { AU.whoosh(); AU.thunder(); }
  if (D === P) { shake = Math.max(shake, 0.25); buzz([15, 30, 15]); flashScreen(); banner('Paint storm!', 'Lead it over them'); }
  else if (ally(D, P)) banner(nameOf(D) + '’s paint storm!', 'It won’t hit you');
  else { banner(nameOf(D) + '’s paint storm!', 'Watch for the rings'); AU.spot(); }
  for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0;
}
// a drop: where it'll land (on the floor under it), and which CPUs in its way see it coming
function stormSpawn(S) {
  const D = S.by; let aim = null;
  if (Math.random() < (D.ai ? 0.5 : STORM_SEEK)) { let bd = STORM_AREA + 3.5; for (const F of foes(D)) { if (F.st !== 'play' || F.rocket) continue; const d = Math.hypot(F.x - S.cx, F.z - S.cz); if (d < bd) { bd = d; aim = F; } } }
  for (let k = 0; k < 4; k++) {
    let x, z;
    if (aim && !k) { const lead = 0.3 + Math.random() * 0.3; x = aim.x + Math.sin(aim.yaw) * aim.spd * lead + (Math.random() - 0.5) * 0.9; z = aim.z + Math.cos(aim.yaw) * aim.spd * lead + (Math.random() - 0.5) * 0.9; }
    else { const a = Math.random() * 6.2832, r = STORM_AREA * Math.sqrt(Math.random()); x = S.cx + Math.cos(a) * r; z = S.cz + Math.sin(a) * r; }
    const lim = ARENA - 0.6; x = clamp(x, -lim, lim); z = clamp(z, -lim, lim);
    const gy = surfaceUnder(x, z, S.cy - 1, true); if (gy === -Infinity || gy < S.cy - STORM_H - 5) continue; // (a hole, or a long way down)
    const d = stormTake(D); d.x = x; d.z = z; d.gy = gy; d.t = 0; d.sx = S.cx + (Math.random() - 0.5) * 2.4; d.sz = S.cz + (Math.random() - 0.5) * 2.4; d.sy = S.cy - 0.9; d.dodge = null;
    d.ring.position.set(x, gy + 0.07, z); d.fill.position.set(x, gy + 0.06, z); d.ring.scale.setScalar(0.3); d.fill.scale.setScalar(0.3);
    for (const F of foes(D)) if (F.ai && F.st === 'play' && Math.hypot(F.x - x, F.z - z) < STORM_KO + PR + 1.2 && Math.random() < (diff === 'easy' ? 0.3 : diff === 'hard' ? 0.75 : 0.5)) (d.dodge || (d.dodge = [])).push(F);
    S.drops.push(d); return;
  }
}
// it lands: a splat of the storm's paint, and anyone under it is out (unless in the air over it, or rolling)
function stormLand(S, d) {
  const D = S.by, x = d.x, z = d.z, gy = d.gy;
  addSplat(x, gy, z, Math.random() * 6.2832, STORM_R * (0.9 + Math.random() * 0.2), dryClock, false, true, tcode(D));
  shockwave(x, gy, z, STORM_R * 1.15, TEAMS[D.team].wet); shockwave(x, gy, z, STORM_R * 0.6, 0xFFFFFF);
  for (let i = 0; i < 10; i++) { const a = Math.random() * 6.283, s = 2 + Math.random() * 2.5; spawnPart(x + Math.cos(a) * 0.3, gy + 0.2, z + Math.sin(a) * 0.3, Math.cos(a) * s, 2.5 + Math.random() * 3, Math.sin(a) * s, 0.45 + Math.random() * 0.3, tmat(D), 0.45 + Math.random() * 0.4); }
  const dp = Math.hypot(x - P.x, z - P.z); if (dp < 16) { AU.at(x, z); AU.splat(2.2); if (dp < 9) shake = Math.max(shake, 0.12 * (1 - dp / 9)); if (D === P) buzz(6); }
  if (matchLeft <= 0) return;
  for (const O of foes(D)) {
    if (O.st !== 'play' || O.rocket || O.immuneT > 0) continue;
    const dx = O.x - x, dz = O.z - z; if (dx * dx + dz * dz > (STORM_KO + PR) ** 2) continue;
    const og = O.air ? surfaceUnder(O.x, O.z, O.y + STEP, true) : O.y, base = og > -Infinity ? og : O.y, lift = O.air ? O.y - base : 0;
    if (Math.abs(base - gy) > 1.2) continue;
    if (lift > 0.9 || safe(O)) { dodgedPound(O, D); continue; }
    poundHit(O, D, 'storm');
  }
}
function stormEnd(S) { for (const d of S.drops) stormGive(d); S.drops.length = 0; scene.remove(S.g, S.sh); for (const m of S.g.userData.mats) m.dispose(); S.sh.material.dispose(); }
function clearStorms() { for (const S of stormList) stormEnd(S); stormList.length = 0; }
function stormTick(dt) {
  for (let i = stormList.length - 1; i >= 0; i--) {
    const S = stormList[i], D = S.by; S.t += dt;
    if (state !== 'play') { stormEnd(S); stormList.splice(i, 1); continue; }
    const live = !S.end && D.st === 'play' && S.t < STORM_FORM + STORM_T;
    if (!live && !S.fade) S.fade = 1e-4;
    // the cloud leads its caster, further ahead the faster they go
    if (D.st === 'play') { const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw), lead = STORM_LEAD * (0.55 + 0.45 * clamp(D.spd / cfg.speed, 0, 1.4)), k = 1 - Math.exp(-dt * 2.6), lim = ARENA - 1;
      S.cx += (clamp(D.x + fx * lead, -lim, lim) - S.cx) * k; S.cz += (clamp(D.z + fz * lead, -lim, lim) - S.cz) * k; }
    // never in the way of the view: it sits a little above the camera's eye and keeps its distance from it (a sharp turn would
    // otherwise swing the camera into it), so from the play camera it hangs at the top of the screen
    { const cp = camera.position, dx = S.cx - cp.x, dz = S.cz - cp.z, dc = Math.hypot(dx, dz); if (dc < STORM_CAM) { const k2 = dc > 1e-3 ? STORM_CAM / dc : 0; S.cx = dc > 1e-3 ? cp.x + dx * k2 : cp.x + Math.sin(D.yaw) * STORM_CAM; S.cz = dc > 1e-3 ? cp.z + dz * k2 : cp.z + Math.cos(D.yaw) * STORM_CAM; }
      S.cy += (Math.max(Math.max(D.y, -1) + STORM_H, cp.y + 0.5) - S.cy) * (1 - Math.exp(-dt * 3)); }
    if (S.fade) S.fade += dt;
    const inK = clamp(S.t / STORM_FORM, 0, 1), sc = S.fade ? Math.max(0.01, 1 - S.fade / 0.6) : Math.max(0.01, easeBack(inK)), bob = Math.sin(S.t * 1.7) * 0.15;
    S.g.position.set(S.cx, S.cy + bob, S.cz); S.g.rotation.y += dt * 0.35; S.g.scale.set(sc * STORM_CK, sc * STORM_CK * (0.9 + 0.08 * Math.sin(S.t * 2.3)), sc * STORM_CK);
    // now and then a flash of lightning inside it
    if (live && S.t > STORM_FORM && (S.flT -= dt) <= 0) { S.flT = 0.6 + Math.random() * 0.9; S.fl = 1; if (D === P || dp0(D) < 14) AU.at(S.cx, S.cz); }
    S.fl = Math.max(0, S.fl - dt * 5); { const [dk, lt] = S.g.userData.mats, f = S.fl * S.fl; dk.emissive.setScalar(0.35 * f); lt.emissive.setScalar(0.75 * f); }
    // its shadow on the floor, and a fine drizzle of paint under it
    { const gy = surfaceUnder(S.cx, S.cz, S.cy - 1, true); S.sh.visible = gy > -Infinity && sc > 0.05; if (S.sh.visible) { S.sh.position.set(S.cx, gy + 0.05, S.cz); S.sh.scale.setScalar((STORM_AREA + 0.6) * sc); S.sh.material.opacity = 0.13 * sc; } }
    if (live && S.t > STORM_FORM * 0.6) { S.drip += dt * 16; while (S.drip >= 1) { S.drip -= 1; const a = Math.random() * 6.2832, r = Math.random() * 2.6; spawnPart(S.cx + Math.cos(a) * r, S.cy - 0.9, S.cz + Math.sin(a) * r, 0, -3 - Math.random() * 2, 0, 0.5 + Math.random() * 0.3, tmat(D), 0.18 + Math.random() * 0.12); } }
    // the drops
    while (live && S.t >= S.next) { S.next += STORM_EVERY * (0.8 + Math.random() * 0.4); stormSpawn(S); }
    for (let j = S.drops.length - 1; j >= 0; j--) {
      const d = S.drops[j]; d.t += dt; const k = Math.min(1, d.t / STORM_FALL), pulse = 0.5 + 0.5 * Math.sin(d.t * 26), grow = 1 - Math.pow(1 - Math.min(1, k / 0.45), 3);
      d.ring.scale.setScalar(Math.max(0.01, (0.3 + 0.65 * grow) * STORM_R)); d.fill.scale.setScalar(Math.max(0.01, (0.15 + 0.8 * k) * STORM_R));
      d.ring.material.color.set(TEAMS[D.team].wet).lerp(COL_WHITE, 0.3 + 0.4 * pulse); d.ring.material.opacity = 0.55 + 0.45 * k; d.fill.material.opacity = 0.12 + 0.3 * k;
      if (k > 0.08) { d.g.visible = true; const u = (k - 0.08) / 0.92, e = u * u; d.g.position.set(d.sx + (d.x - d.sx) * u, d.sy + (d.gy + 0.35 - d.sy) * e, d.sz + (d.z - d.sz) * u); d.g.scale.set(1, 1 + 0.9 * u, 1); }
      if (d.dodge && d.t >= STORM_FALL - 0.14) { for (const F of d.dodge) if (F.st === 'play' && Math.hypot(F.x - d.x, F.z - d.z) < STORM_KO + PR + 0.6) dodgeRoll(F); d.dodge = null; }
      if (d.t >= STORM_FALL) { stormLand(S, d); stormGive(d); S.drops.splice(j, 1); }
    }
    if (S.fade > 0.6 && !S.drops.length) { stormEnd(S); stormList.splice(i, 1); }
  }
}

// ---------- (v384) Aftershock (a skill): a beat after your pound lands, the ground answers: a second ring of your paint bursts out from
// where it hit, twice as wide. A rival it catches on the ground is knocked off its feet, stunned, and spills some of its paint; a jump
// or a roll gets you over it, and a giant shrugs it off. It leaves a ring of paint where it stops ----------
const SHOCK_WAIT = 0.3, SHOCK_RUN = 0.42, SHOCK_OUT = 2, SHOCK_MAX = 7, SHOCK_STUN = 1.4, SHOCK_SPILL = 0.2, shockList = [];
const SHOCK_G = crownGeo(0.96, 1.06, 1, 7384);
const shockArrive = (W, d) => { const e = clamp((d - W.r0) / (W.r1 - W.r0), 0, 1); return SHOCK_RUN * (1 - Math.pow(1 - e, 1 / 2.2)); }; // (when the ring reaches d)
function shockQueue(D, R) {
  const W = { by: D, x: D.x, y: D.y, z: D.z, r0: R * 0.85, r1: Math.min(SHOCK_MAX, R * SHOCK_OUT), t: -SHOCK_WAIT, hit: new Set(), g: null, dodge: [] }; shockList.push(W);
  // a CPU that sees it coming hops or rolls over it (more often on hard)
  for (const F of foes(D)) { if (!F.ai || F.st !== 'play') continue; const d = Math.hypot(F.x - W.x, F.z - W.z); if (d > W.r0 && d < W.r1 + 1.2 && Math.random() < (diff === 'easy' ? 0.2 : diff === 'hard' ? 0.6 : 0.4)) W.dodge.push([F, shockArrive(W, d) - 0.12]); }
}
function shockTrip(B, D, W) {
  if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }
  const dx = B.x - W.x, dz = B.z - W.z, l = Math.hypot(dx, dz) || 1, nx = dx / l, nz = dz / l;
  B.stunT = Math.max(B.stunT || 0, SHOCK_STUN); B.spd = 0; B.turn = 0; B.slam = false; B.missile = false; B.rollT = 0;
  B.air = true; B.stroke++; B.vy = 5.2; B.knockT = 0.4; B.kx = nx * 4.5; B.kz = nz * 4.5; B.squash = 0.8; B.wob = 1; B.lastHit = { by: D, t: runT };
  B.paint = Math.max(0, B.paint - SHOCK_SPILL); fxKnock(B, nx, nz, 0.7); fxTumble(B, 0.8, Math.random() - 0.5, nx, nz); emote(B, 'ouch', 1); emote(D, 'glee', 1);
  for (let i = 0; i < 12; i++) { const a = Math.random() * 6.283, s = 1.5 + Math.random() * 2.5; spawnPart(B.x, B.y + 0.4, B.z, Math.cos(a) * s, 2 + Math.random() * 3, Math.sin(a) * s, 0.5 + Math.random() * 0.3, i % 3 ? tmat(B) : puHaloMat, 0.4 + Math.random() * 0.3); }
  hitStop(0.05, D, B); if (hearable(B)) { AU.bonk(0.9); AU.pop(); }
  if (B === P) { shake = Math.max(shake, 0.3); buzz([20, 25, 20]); popText('Aftershock!'); AU.vox('oof'); }
  else if (D === P) { buzz(14); popText('Aftershock! ' + nameOf(B) + ' is down'); }
}
function shockDrop(W) { if (W.g) scene.remove(W.g); W.g = null; }
function clearShocks() { for (const W of shockList) shockDrop(W); shockList.length = 0; }
function shockTick(dt) {
  for (let i = shockList.length - 1; i >= 0; i--) {
    const W = shockList[i], D = W.by; W.t += dt;
    if (state !== 'play') { shockDrop(W); shockList.splice(i, 1); continue; }
    for (const q of W.dodge) if (q[1] !== null && W.t >= q[1]) { if (q[0].st === 'play') dodgeRoll(q[0]); q[1] = null; }
    if (W.t < 0) { // the build: the floor shivers under the blast
      if (Math.random() < dt * 34) { const a = Math.random() * 6.2832, r = W.r0 * (0.5 + Math.random() * 0.5); spawnPart(W.x + Math.cos(a) * r, W.y + 0.1, W.z + Math.sin(a) * r, 0, 1.4 + Math.random() * 1.6, 0, 0.35, tmat(D), 0.35); }
      continue; }
    if (!W.g) { // it goes: a wall of paint racing out, a white ring ahead of it
      const g = new THREE.Group(), m = new THREE.Mesh(SHOCK_G, crownMats[D.team]), h = new THREE.Mesh(SHOCK_G, crownHullMat); h.scale.set(1.02, 1.04, 1.02); g.add(m, h); g.position.set(W.x, W.y + 0.02, W.z); scene.add(g); W.g = g;
      shockwave(W.x, W.y, W.z, W.r1 * 1.05, 0xFFFFFF); shockwave(W.x, W.y, W.z, W.r1 * 0.8, TEAMS[D.team].wet); startQuake(0.25 * Math.max(0.3, 1 - dp0(D) / 30));
      const dp = dp0(D); if (D === P) { shake = Math.max(shake, 0.28); buzz([10, 15, 25]); AU.burst(0.6); } else if (dp < 18) { AU.at(W.x, W.z); AU.burst(0.4); shake = Math.max(shake, 0.25 * (1 - dp / 18)); } }
    const u = Math.min(1, W.t / SHOCK_RUN), e = 1 - Math.pow(1 - u, 2.2), r = W.r0 + (W.r1 - W.r0) * e, h = u < 1 ? 0.35 + 1.15 * Math.sin(Math.PI * Math.min(1, 0.15 + u * 0.85)) : Math.max(0, 0.35 - (W.t - SHOCK_RUN) * 2.2);
    W.g.scale.set(r, Math.max(0.01, h), r);
    if (u < 1 && Math.random() < dt * 40) { const a = Math.random() * 6.2832; spawnPart(W.x + Math.cos(a) * r, W.y + 0.4, W.z + Math.sin(a) * r, Math.cos(a) * 2.5, 2 + Math.random() * 2.5, Math.sin(a) * 2.5, 0.4, tmat(D), 0.4); }
    if (u < 1 && matchLeft > 0) for (const O of foes(D)) {
      if (W.hit.has(O) || O.st !== 'play' || O.rocket || O.immuneT > 0 || O.giantT > 0) continue;
      const d = Math.hypot(O.x - W.x, O.z - W.z); if (d > r + PR || d < r - 0.9 - PR) continue;
      const og = O.air ? surfaceUnder(O.x, O.z, O.y + STEP, true) : O.y, base = og > -Infinity ? og : O.y, lift = O.air ? O.y - base : 0;
      if (Math.abs(base - W.y) > 1.2) continue;
      W.hit.add(O); if (lift > 0.5 || safe(O)) { dodgedPound(O, D); continue; } shockTrip(O, D, W);
    }
    if (u >= 1 && !W.ring) { W.ring = true; const n = Math.round(W.r1 * 2.6); for (let k = 0; k < n; k++) { const a = k / n * 6.2832 + Math.random() * 0.2, px = W.x + Math.cos(a) * W.r1 * 0.93, pz = W.z + Math.sin(a) * W.r1 * 0.93, gy = surfaceUnder(px, pz, W.y + 1.2, true); if (gy > -Infinity && Math.abs(gy - W.y) < 1) addSplat(px, gy, pz, a, 0.75, dryClock, true, true, tcode(D)); } }
    if (W.t > SHOCK_RUN + 0.16) { shockDrop(W); shockList.splice(i, 1); }
  }
}
"""

# ---- the Strokes page demo for the Paint Storm: a little cloud over the pad, drops falling with their rings, one on the rival
SG_JS = r"""
// Paint Storm: the cloud gathers over the pad, drops rain down on their rings (and leave splats), the rival can't get out from under
// the one that finds it, and the cloud melts away
function sgStormBits() {
  if (SGD.st) return SGD.st;
  const cloud = makeStormCloud(0); cloud.scale.setScalar(0.01); cloud.visible = false; SGD.root.add(cloud);
  const drops = []; for (let i = 0; i < 4; i++) { const g = new THREE.Group(), m = new THREE.Mesh(STORM_GLOB, tmat(SGD.A.D)), h = new THREE.Mesh(STORM_GLOB, crownHullMat); h.scale.setScalar(1.14); g.add(m, h); g.scale.setScalar(0.32); g.visible = false;
    const ring = new THREE.Mesh(STORM_RING, new THREE.MeshBasicMaterial(stormFlat())), fill = new THREE.Mesh(STORM_DISC, new THREE.MeshBasicMaterial(stormFlat())); ring.rotation.x = fill.rotation.x = -Math.PI / 2; ring.renderOrder = 7; fill.renderOrder = 6; ring.visible = fill.visible = false;
    SGD.root.add(g, ring, fill); drops.push({ on: false, g, ring, fill, x: 0, z: 0, t: 0, sx: 0, sz: 0, kill: false }); }
  sgLayer(cloud); for (const d of drops) { sgLayer(d.g); sgLayer(d.ring); sgLayer(d.fill); }
  return (SGD.st = { cloud, drops, cx: 0, cz: 0, next: 0, n: 0 });
}
function sgStormOff() { const T = SGD.st; if (!T) return; T.cloud.visible = false; for (const d of T.drops) { d.on = false; d.g.visible = d.ring.visible = d.fill.visible = false; } }
const SG_ST_H = 1.3, SG_ST_FALL = 0.45;
function sgStorm(dt, t, s) {
  const A = SGD.A, B = SGD.B, DA = A.D, DB = B.D, cA = TEAMS[0].css, T = sgStormBits(), ON = 0.55, OFF = 3.9;
  if (t < ON) { sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'ready'; T.cx = sgLX(A) * 0.5; T.cz = sgLZ(A) * 0.5; T.next = ON + 0.35; T.n = 0; }
  else if (sgOnce('gather')) { const x = sgLX(A), z = sgLZ(A); T.cloud.visible = true; DA.squash = 0.7; DA.wob = 1; emote(DA, 'glee', 1.1); sgRing(x, z, 1.3, TEAMS[0].wet); sgBurst(x, z, A.col, 12, 4.4, 1.2); sgShk(0.3); for (const d of T.drops) d.ring.material.color.set(TEAMS[0].wet), d.fill.material.color.set(TEAMS[0].wet); }
  // the cloud: grows in, drifts over toward the rival, bobs and turns, melts away at the end
  if (T.cloud.visible) { const k = t < OFF ? easeBack(clamp((t - ON) / 0.5, 0, 1)) : Math.max(0, 1 - (t - OFF) / 0.5), tx = t < 2.0 ? sgLX(A) * 0.4 + sgLX(B) * 0.3 : sgLX(B) * 0.7, tz = t < 2.0 ? sgLZ(A) * 0.4 + sgLZ(B) * 0.3 : sgLZ(B) * 0.7, kk = Math.min(1, dt * 1.6);
    T.cx += (tx - T.cx) * kk; T.cz += (tz - T.cz) * kk; T.cloud.position.set(T.cx, SG_ST_H + Math.sin(t * 2) * 0.05, T.cz); T.cloud.rotation.y += dt * 0.5; const sc = 0.2 * Math.max(0.01, k); T.cloud.scale.set(sc, sc * 0.9, sc);
    if (k <= 0.01 && t >= OFF) T.cloud.visible = false;
    if (k > 0.5 && Math.random() < dt * 14) { const a = Math.random() * 6.2832, r = Math.random() * 0.6; sgPart(T.cx + Math.cos(a) * r, SG_ST_H - 0.15, T.cz + Math.sin(a) * r, 0, -1.2, 0, 0.5, A.col, 0.3); } }
  // the drops: one every so often, the fourth on the rival
  if (t >= T.next && t < OFF - 0.2) { T.next = t + 0.36 + Math.random() * 0.12; const d = T.drops.find(q => !q.on); if (d) { T.n++; const hitB = T.n === 4 && B.show; let x, z;
      if (hitB) { x = sgLX(B); z = sgLZ(B); } else { for (let k = 0; k < 6; k++) { const a = Math.random() * 6.2832, r = 0.25 + Math.random() * 0.55; x = T.cx + Math.cos(a) * r; z = T.cz + Math.sin(a) * r; if (Math.hypot(x - sgLX(B), z - sgLZ(B)) > 0.55 && Math.hypot(x, z) < SG_R - 0.35) break; } }
      Object.assign(d, { on: true, x, z, t: 0, sx: T.cx + (Math.random() - 0.5) * 0.4, sz: T.cz + (Math.random() - 0.5) * 0.4, kill: hitB }); d.ring.position.set(x, 0.035, z); d.fill.position.set(x, 0.03, z); d.ring.visible = d.fill.visible = true; } }
  for (const d of T.drops) { if (!d.on) continue; d.t += dt; const k = Math.min(1, d.t / SG_ST_FALL), pulse = 0.5 + 0.5 * Math.sin(d.t * 26), grow = 1 - Math.pow(1 - Math.min(1, k / 0.45), 3);
    d.ring.scale.setScalar(Math.max(0.01, (0.3 + 0.65 * grow) * 0.42)); d.fill.scale.setScalar(Math.max(0.01, (0.15 + 0.8 * k) * 0.42)); d.ring.material.color.set(TEAMS[0].wet).lerp(COL_WHITE, 0.3 + 0.4 * pulse); d.ring.material.opacity = 0.55 + 0.45 * k; d.fill.material.opacity = 0.12 + 0.3 * k;
    if (k > 0.08) { const u = (k - 0.08) / 0.92; d.g.visible = true; d.g.position.set(d.sx + (d.x - d.sx) * u, SG_ST_H - 0.2 + (0.08 - SG_ST_H + 0.2) * u * u, d.sz + (d.z - d.sz) * u); d.g.scale.set(0.3, 0.3 + 0.27 * u, 0.3); }
    if (k >= 1) { d.on = false; d.g.visible = d.ring.visible = d.fill.visible = false; sgSplat(d.x, d.z, 0.42, cA); sgRing(d.x, d.z, 0.75, TEAMS[0].wet); sgBurst(d.x, d.z, A.col, 8, 2.6, 1.8); sgShk(0.25);
      if (B.show && (d.kill || Math.hypot(sgLX(B) - d.x, sgLZ(B) - d.z) < 0.4)) { sgKO(B, cA); emote(DA, 'glee', 1.3); } } }
  // you: a few steps under it, painting; the rival: eyes up, a step aside that doesn't help
  if (t >= ON + 0.3 && t < 2.6) { const p = sgCS(-0.15 * s, 0.25), lx = sgLX(A), lz = sgLZ(A); sgGo(A, p[0], p[1], 0.9, dt); sgStripe(lx, lz, sgLX(A), sgLZ(A), 0.5, cA); sgWatch(A, B); DA.ip.expr = 'menace'; }
  if (B.show && t >= ON) { DB.ip.expr = 'scared'; if (t > 1.2 && t < 2.1) { const p = sgCS(0.95 * s, -0.25); sgGo(B, p[0], p[1], 0.8, dt); } else sgFace(B, sgYawTo(B, A), dt, 4); }
  if (t >= 2.6) { sgHalt(A, dt); sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'glee'; }
  if (t >= 4.6 && sgOnce('back')) { const p = sgCS(0.75 * s, -0.55); sgBack(B, p[0], p[1], sgYawTo(B, A)); }
}
"""

def apply(s):
    img = {k: 'data:image/webp;base64,' + base64.b64encode(open(A + k + '_flat_256.webp', 'rb').read()).decode() for k in ['storm', 'shock']}
    # ---- the strokes themselves
    s = rep(s, "  { id: 'pockets', name: 'Deep Pockets', desc: 'Carry more, use it when you like.', craft: 20, does: ['Hold two power-ups and use either one', 'Your orb stays in its slot until you use it'] }];\n",
               "  { id: 'pockets', name: 'Deep Pockets', desc: 'Carry more, use it when you like.', craft: 20, does: ['Hold two power-ups and use either one', 'Your orb stays in its slot until you use it'] }];\n"
               "// (v384) the Paint Storm (a special) and Aftershock (a skill), bought with dabs\n"
               "SPECIALS.push({ id: 'storm', name: 'Paint Storm', desc: 'A storm cloud of your paint rains big splats wherever you lead it.', does: ['A storm cloud of your paint follows you for 5 seconds', 'Big drops of your paint rain down a little ahead of you', 'A drop that lands on a rival knocks it out. Rings show where they\\u2019ll fall'] });\n"
               "SKILLS.push({ id: 'shock', name: 'Aftershock', desc: 'Your pound lands twice.', does: ['A beat after your pound, a ring of paint bursts out twice as wide', 'Rivals it catches on the ground are knocked down and stunned', 'They spill some paint, and it leaves a ring of yours'] });\n")
    s = rep(s, "  { id: 'swim', name: 'Swim faster', desc: 'Built for speed, wet or dry.', does: ['8% more pace every time you glide', 'Twice as fast when the rain comes'] },",
               "  { id: 'swim', name: 'Swim faster', desc: 'Built for speed, wet or dry.', does: ['8% more pace every time you glide', 'Much faster in the rain, with a sure grip on the wet'] }, // (v384: 1.6x in the rain, and a tighter turn at that speed)")
    s = rep(s, "const ST_PRICE = { turret: 200, repel: 300, trap: 300, pockets: 400, whirl: 400, freeze: 500, boom: 500 };",
               "const ST_PRICE = { turret: 200, repel: 300, trap: 300, pockets: 400, whirl: 400, freeze: 500, boom: 500, shock: 400, storm: 600 }; // (v384: the Aftershock and the Paint Storm)")
    s = rep(s, "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets']) STROKE_ICON[k] = stImg(k);",
               "ST_IMG.storm = '" + img['storm'] + "'; ST_IMG.shock = '" + img['shock'] + "'; // (v384: Ludo.ai, the same style)\n"
               "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets', 'storm', 'shock']) STROKE_ICON[k] = stImg(k);")
    s = rep(s, "ORB_LBL = { rocket: 'Rocket', giant: 'Giant', freeze: 'Freeze' };", "ORB_LBL = { rocket: 'Rocket', giant: 'Giant', freeze: 'Freeze', storm: 'Storm' };")
    # ---- the storm from the orb (CPUs too, now and then), and how a CPU holds it till someone's near
    s = rep(s, "function cpuGift() { return !tut && !tut2 && !tut3 && Math.random() < 0.2 ? 'freeze' : ['giant', 'rocket'][(Math.random() * 2) | 0]; }",
               "function cpuGift() { const r = Math.random(); return !tut && !tut2 && !tut3 && r < 0.36 ? (r < 0.18 ? 'freeze' : 'storm') : ['giant', 'rocket'][(Math.random() * 2) | 0]; } // (v384: the storm, as often as the freeze)")
    s = rep(s, "  if (gift === 'freeze') { startFreeze(D); return; }\n", "  if (gift === 'freeze') { startFreeze(D); return; }\n  if (gift === 'storm') { startStorm(D); return; } // (v384)\n")
    s = rep(s, "if (D.orbSaved && D.ai && (D.ai.orbWait = (D.ai.orbWait || 0) - dt) <= 0 && !useOrb(D)) D.ai.orbWait = 0.3; }",
               "if (D.orbSaved && D.ai && (D.ai.orbWait = (D.ai.orbWait || 0) - dt) <= 0) { if (D.orbSaved === 'storm' && D.orbT > 2.5 && !foes(D).some(F => F.st === 'play' && Math.hypot(F.x - D.x, F.z - D.z) < 11)) D.ai.orbWait = 0.4; else if (!useOrb(D)) D.ai.orbWait = 0.3; } } // (v384: a storm kept till someone's near)")
    s = rep(s, "const KO_MSG = { trap: 'Trapped!',", "const KO_MSG = { storm: 'Caught in the storm!', trap: 'Trapped!',")
    s = rep(s, "const CPU_KO_MSG = { trap: n => 'Trapped ' + n + '!',", "const CPU_KO_MSG = { storm: n => 'Stormed ' + n + '!', trap: n => 'Trapped ' + n + '!',")
    # ---- the code, after the freeze's; ticked with it, cleared with the traps
    s = rep(s, "\n// ---------- the giant orb: a glowing, color-shifting orb", STORM_JS + "\n// ---------- the giant orb: a glowing, color-shifting orb")
    s = rep(s, "  if (!NM) itemTick(dt); trapTick(dt); freezeTick(dt); zoneTick(dt);", "  if (!NM) itemTick(dt); trapTick(dt); freezeTick(dt); stormTick(dt); shockTick(dt); zoneTick(dt);")
    s = rep(s, "function placePowers() {\n  clearTraps(); boomClear();", "function placePowers() {\n  clearTraps(); boomClear(); clearStorms(); clearShocks();")
    # ---- Aftershock: queued as a pound lands (not a giant's: that has its own quake; offline, as the other skills)
    s = rep(s, "  orbPound(D, R);\n}\nfunction collectPower(D, pw) {",
               "  orbPound(D, R);\n  if (D.skill === 'shock' && !giant && !NM && !tut && matchLeft > 0) shockQueue(D, R); // (v384: Aftershock)\n}\nfunction collectPower(D, pw) {")
    # ---- Swim faster in the rain: 1.6x, not 2x, and a firmer grip at that pace
    s = rep(s, "    speedMul += ((wxPhase === 'rain' ? 2.0 : 1) - speedMul) * Math.min(1, dt * 3);",
               "    speedMul += ((wxPhase === 'rain' ? RAIN_SPD : 1) - speedMul) * Math.min(1, dt * 3); // (v384: 1.6x, was 2x)")
    s = rep(s, "const MOVE_K = 1.06, REPEL_SPD = 0.8,", "const MOVE_K = 1.06, REPEL_SPD = 0.8, RAIN_SPD = 1.6, RAIN_GRIP = 0.8,")
    s = rep(s, ": D.air ? 1 : sr < 1 ? Math.min(D.charging ? 1.35 : 1.6, 1 + 0.6 * (1 - Math.max(0, sr))) : Math.min(1.3, sr),",
               ": D.air ? 1 : sr < 1 ? Math.min(D.charging ? 1.35 : 1.6, 1 + 0.6 * (1 - Math.max(0, sr))) : Math.min(1.3 + (rainFast(D) ? Math.max(0, speedMul - 1) * RAIN_GRIP : 0), sr), /* (v384: the rain's extra pace comes with a tighter turn) */")
    # ---- the Strokes page: the storm's demo
    s = rep(s, "const SG_T = { roller: 6.2, turret: 5.6, trap: 6.4, whirl: 6.0, boom: 5.4, rocket: 5.8, giant: 5.8, freeze: 6.6 };",
               "const SG_T = { roller: 6.2, turret: 5.6, trap: 6.4, whirl: 6.0, boom: 5.4, rocket: 5.8, giant: 5.8, freeze: 6.6, storm: 5.8 }; // (v384: the Paint Storm)")
    s = rep(s, "  else if (k === 'freeze') { sgAtC(A, -0.9 * s, 0.45); sgAtC(B, 0.85 * s, -0.75); }\n",
               "  else if (k === 'freeze') { sgAtC(A, -0.9 * s, 0.45); sgAtC(B, 0.85 * s, -0.75); }\n  else if (k === 'storm') { sgAtC(A, -0.7 * s, 0.45); sgAtC(B, 0.55 * s, -0.45); }\n")
    s = rep(s, "SGD.mk.visible = SGD.mkF.visible = SGD.mkB.visible = SGD.ice.visible = false; SGD.iceK = 0; SGD.sp = {};",
               "SGD.mk.visible = SGD.mkF.visible = SGD.mkB.visible = SGD.ice.visible = false; sgStormOff(); SGD.iceK = 0; SGD.sp = {};")
    s = rep(s, "  else if (k === 'freeze') sgFreeze(dt, t, s);\n", "  else if (k === 'freeze') sgFreeze(dt, t, s);\n  else if (k === 'storm') sgStorm(dt, t, s);\n")
    s = rep(s, "\n// the whirlwind's lane: a strip on the pad", SG_JS + "\n// the whirlwind's lane: a strip on the pad")
    # the name over the window shrinks to fit; on the page's first frame it has no width yet, so it tries again (it was cut short then)
    s = rep(s, "function sgFitName() { const nb = $('sgName'); nb.style.fontSize = ''; if (!nb.clientWidth) return;",
               "function sgFitName() { const nb = $('sgName'); nb.style.fontSize = ''; if (!nb.clientWidth) { if ((sgFitName.n = (sgFitName.n || 0) + 1) < 40) requestAnimationFrame(sgFitName); return; } sgFitName.n = 0; clearTimeout(sgFitName.t); sgFitName.t = setTimeout(sgFitNow, 420); sgFitNow(); }\nfunction sgFitNow() { const nb = $('sgName'); if (!nb.clientWidth) return; nb.style.fontSize = '';")
    return s
