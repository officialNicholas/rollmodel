"""v285, two things.

1. The Whirlwind gives a second more notice, and shows you when it will go. It winds up for 1.3 s (was 0.3). A lane on the ground
   shows where it will charge (as far as the charge runs: it stops short of a drop or a wall) and fills up as it winds. The whirler
   aims it (a CPU turns toward its nearest rival) until 0.45 s before the charge, when it locks: the lane flashes, a sparkle glints on
   the whirler with a "ting" (Ludo), and from then on it can't turn. That glint is the cue: step out of the lane, or roll through it as
   it arrives (a roll can't be hit). In the charge it steers less and leans toward a rival less than before, so a dodge in time works.
   CPUs read it too: lined up in the lane at the glint they step out (as often as their level dodges a pound), the planner keeps their
   routes out of a winding lane, they stop going at a rival who's whirling, and in the charge they roll through it at the last
   moment (as often as they dodge a pound).

2. Pick-ups by need. Before, one item at a time could be out in a 1v1 (two in bigger matches), each 9 to 13 s apart, on spots chosen
   to be "worth the trip" (up high, out on pads), and CPUs only fetch ones close by: one landed where nobody went, sat there all match
   and blocked every other spawn. In simulated 1v1s both fighters went most of the match with nothing. Now who has one (held, in a
   pocket, or in use) and who doesn't decides when the next comes and where:
   - one comes for whoever has waited longest with nothing, after a wait that's shorter when nobody has one or rivals are holding
     theirs, and longer for the side that's ahead (whoever's behind gets a little help; the leader still gets them, just later);
   - never more out than there are empty hands, so they don't pile up;
   - it lands a short run from them (about 8 steps), ahead of where they're facing when it can, nearer them than any rival, on their
     level, inside the Showdown line, clear of basins and boiling water; anyone can still race them for it;
   - 1.2 s before it appears a beam of light and a closing ring mark the spot (with a ping if it's near you), and while you've got
     nothing an arrow points you to the nearest one when it's off screen or far;
   - one nobody takes in 25 s, or that the Showdown line closes over, pops, and the next goes somewhere useful;
   - a CPU goes and gets one that came for it, and the longer it has waited the further it goes for any other.
   The first lesson keeps its own scripted items."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

WHIRL = r"""
// ---------- v285: the Whirlwind's notice: a lane that fills as it winds, a glint when it locks ----------
const WHIRL_LOCK = 0.45, WHIRL_LANE_W = 2 * (WHIRL_R + 0.25), WL_N = 18;
// the lane: a strip on the ground, rails along its sides, chevrons running the way it will go over the part that has filled
const whirlLaneM = new THREE.ShaderMaterial({ uniforms: { uCol: { value: new THREE.Color(0xE3122F) }, uFill: { value: 0 }, uT: { value: 0 }, uLock: { value: 0 }, uA: { value: 0 }, uLen: { value: 10 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: `uniform vec3 uCol; uniform float uFill, uT, uLock, uA, uLen; varying vec2 vUv;
    void main(){ float u = vUv.x, e = abs(vUv.y * 2.0 - 1.0), d = u * uLen;
      float rail = smoothstep(0.78, 0.86, e) * (1.0 - smoothstep(0.95, 1.0, e)), body = 1.0 - smoothstep(0.9, 1.0, e), filled = step(u, uFill);
      float f = fract(d / 1.4 + e * 0.6 - uT * 1.8), chev = smoothstep(0.5, 0.62, f) * (1.0 - smoothstep(0.78, 0.9, f));
      float ends = smoothstep(0.0, 0.06, u) * (1.0 - smoothstep(0.88, 1.0, u)), flash = uLock;
      float a = (body * (0.14 + 0.24 * filled + 0.18 * flash) + rail * (0.5 + 0.4 * filled) + chev * body * filled * (0.5 + 0.3 * flash)) * ends;
      vec3 c = mix(uCol, vec3(1.0), clamp(max(rail, chev * filled) * 0.8 + 0.25 * flash, 0.0, 1.0));
      gl_FragColor = vec4(c, clamp(a * uA, 0.0, 1.0)); }`,
  transparent: true, depthWrite: false, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: -8, polygonOffsetUnits: -8 });
// the glint: a crisp four-point star, gold with a white heart and a thin dark edge (it has to read over a bright tornado and any
// paint), in a soft gold glow
const WHIRL_SPARK_T = (() => { const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d'), m = 128;
  const gr = g.createRadialGradient(m, m, 0, m, m, 128); gr.addColorStop(0, 'rgba(255,226,120,0.75)'); gr.addColorStop(0.3, 'rgba(255,214,90,0.28)'); gr.addColorStop(1, 'rgba(255,214,90,0)'); g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  const star = (l, w, l2) => { const pts = []; for (let k = 0; k < 8; k++) { const a = -Math.PI / 2 + k * Math.PI / 4, r = k % 2 === 0 ? l : l2, b = a + Math.PI / 8; pts.push([m + Math.cos(a) * r, m + Math.sin(a) * r], [m + Math.cos(b) * w, m + Math.sin(b) * w]); }
    g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (const q of pts.slice(1)) g.lineTo(q[0], q[1]); g.closePath(); }; // (long points up, down and across; short ones between)
  star(122, 15, 52); g.lineJoin = 'round'; g.lineWidth = 7; g.strokeStyle = 'rgba(70,30,0,0.55)'; g.stroke(); g.fillStyle = '#FFD23F'; g.fill();
  star(92, 9, 34); g.fillStyle = '#FFFFFF'; g.fill();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
const whirlSparkM = new THREE.SpriteMaterial({ map: WHIRL_SPARK_T, transparent: true, depthTest: false, depthWrite: false, fog: false });
function whirlLane(D) {
  if (D.wlane) return D.wlane;
  const N = WL_N, pos = new Float32Array((N + 1) * 6), uv = new Float32Array((N + 1) * 4), idx = [];
  for (let i = 0; i <= N; i++) { uv.set([i / N, 0, i / N, 1], i * 4); if (i < N) { const k = i * 2; idx.push(k, k + 1, k + 2, k + 1, k + 3, k + 2); } }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); g.setIndex(idx);
  const m = new THREE.Mesh(g, whirlLaneM.clone()); m.frustumCulled = false; m.renderOrder = 7; m.visible = false; scene.add(m);
  const sp = new THREE.Sprite(whirlSparkM.clone()); sp.renderOrder = 60; sp.frustumCulled = false; sp.visible = false; scene.add(sp);
  return (D.wlane = { m, g, pos, sp });
}
{ const L = whirlLane({}); L.m.visible = false; } // (one hidden in the scene, so the warm-up builds its shader before a match needs it)
// lay it from (x, z) along yaw over the ground, as far as the charge runs: cut where the ground drops away or a wall stands
function whirlLaneLay(D, x, z, y, yaw) {
  const L = whirlLane(D), fx = Math.sin(yaw), fz = Math.cos(yaw), rx = Math.cos(yaw), rz = -Math.sin(yaw), hw = WHIRL_LANE_W / 2, full = whirlV() * WHIRL_DASH + 0.9;
  let len = full; for (let s = 0.9; s <= full; s += 0.45) { const px = x + fx * s, pz = z + fz * s, g = surfaceUnder(px, pz, y + STEP, true); if (g === -Infinity || g < y - 0.6 || blockedAt(px, pz, y)) { len = Math.max(1.2, s); break; } }
  for (let i = 0; i <= WL_N; i++) { const s = len * i / WL_N, px = x + fx * s, pz = z + fz * s; let gy = surfaceUnder(px, pz, y + STEP, true); if (gy === -Infinity || gy < y - 0.8) gy = y;
    L.pos.set([px - rx * hw, gy + 0.05, pz - rz * hw, px + rx * hw, gy + 0.05, pz + rz * hw], i * 6); }
  L.g.attributes.position.needsUpdate = true; L.m.material.uniforms.uLen.value = len; return len;
}
// the wind-up: aim (the player steers; a CPU turns to its nearest rival) until the lock, then the glint and no more turning
function whirlWind(D, W, dt) {
  const L = whirlLane(D), lockAt = WHIRL_WIND - WHIRL_LOCK;
  if (W.aim === undefined) W.aim = D.yaw;
  if (W.t < lockAt) { if (D.ai) { let best = null, bd = 16; for (const O of foes(D)) if (O.st === 'play') { const d = Math.hypot(O.x - D.x, O.z - D.z); if (d < bd) { bd = d; best = O; } }
      if (best) W.aim += clamp(wrapA(Math.atan2(best.x - D.x, best.z - D.z) - W.aim), -2.4 * dt, 2.4 * dt); D.yaw = W.aim; }
    W.len = whirlLaneLay(D, D.x, D.z, D.y, D.yaw); }
  else { if (W.lock === undefined) { W.lock = D.yaw; W.len = whirlLaneLay(D, D.x, D.z, D.y, W.lock); whirlGlint(D, W); } D.yaw = W.lock; }
  const u = L.m.material.uniforms; u.uCol.value.copy(tmat(D).color); u.uFill.value = Math.min(1, W.t / WHIRL_WIND); u.uT.value = clock; u.uA.value = Math.min(1, W.t / 0.15); u.uLock.value = W.lock !== undefined ? Math.max(0.35, 1 - (W.t - lockAt) * 2) : 0; L.m.visible = true;
}
// the lock: a glint on the whirler and a ting; the CPUs lined up in its lane read it and step out (as often as their level dodges)
function whirlGlint(D, W) {
  const L = whirlLane(D), fx = Math.sin(W.lock), fz = Math.cos(W.lock); W.spT = 0;
  L.sp.material.color.set(0xFFFFFF);
  shockwave(D.x, D.y + 0.1, D.z, 1.7, 0xFFFFFF);
  if (D === P) buzz(8);
  if (hearable(D) && !(AU.xplay && AU.xplay('w_ting', { v: D === P ? 0.75 : 0.95 }))) AU.tick && AU.tick();
  for (const B of foes(D)) if (B.ai && B.st === 'play') { B.ai.thinkT = 0; const dx = B.x - D.x, dz = B.z - D.z, al = dx * fx + dz * fz, sd = dx * fz - dz * fx;
    if (al > -1 && al < (W.len || 10) + 1.5 && Math.abs(sd) < WHIRL_R + 1.4 && Math.random() < Math.max(AI.evade, AI.dodge)) { const sg = sd >= 0 ? 1 : -1; B.ai.evadeT = 0.85; B.ai.evX = D.x + fx * al - fz * sg * 2.5; B.ai.evZ = D.z + fz * al + fx * sg * 2.5; } }
}
function whirlGlintTick(D, W, dt) {
  const L = D.wlane; if (!L) return;
  if (W.spT !== undefined) { W.spT += dt; const k = W.spT / 0.55; if (k >= 1) L.sp.visible = false; else { const e = Math.sin(Math.PI * Math.min(1, k * 1.1)), s = 2.6 * Math.pow(Math.max(0, e), 0.6);
    L.sp.visible = true; L.sp.position.set(D.x, D.y + 1.75, D.z); L.sp.scale.set(s, s, 1); L.sp.material.rotation = k * 1.3; L.sp.material.opacity = Math.min(1, 1.7 * e); } }
  if (W.ph === 'dash') { const u = L.m.material.uniforms; u.uFill.value = 1; u.uT.value = clock; u.uLock.value = 0.35; u.uA.value = Math.max(0, 1 - W.t / 0.6); L.m.visible = u.uA.value > 0.01; }
  else if (W.ph === 'end') L.m.visible = false;
}
"""

ITEMS = r"""
// ---------- v285: pick-ups by need: who has one and who doesn't decides when the next comes and where ----------
const ITEM_WARN = 1.2, ITEM_STALE = 25;
const hasItem = D => !!(D.held || D.held2 || D.power || D.turret || D.whirl);
// ahead (1), behind (-1) or level (0): hearts in a Showdown, the canvas otherwise
function itemEdge(R) {
  const F = foes(R).filter(O => O.st !== 'out'); if (!F.length) return 0;
  if (isShow()) { let m = 0; for (const O of F) m = Math.max(m, O.hearts || 0); const h = R.hearts || 0; return h > m ? 1 : h < m ? -1 : 0; }
  let m = 0; for (const O of F) m = Math.max(m, teamCov(O.team)); const d = teamCov(R.team) - m; return d > 4 ? 1 : d < -4 ? -1 : 0;
}
// how long an empty hand waits for the next one: sooner when nobody has one or rivals are holding theirs, later for whoever's ahead
function itemWait(R, nEmpty, nAlive) {
  let w = 6, held = 0; if (nEmpty >= nAlive) w -= 1.5;
  for (const O of foes(R)) if (O.st !== 'out' && hasItem(O)) held++; w -= Math.min(2, held);
  const e = itemEdge(R); w += e > 0 ? 2.5 : e < 0 ? -1.5 : 0;
  return clamp(w, 3, 10);
}
// where: a short run from them, ahead of where they're facing if it can be, nearer them than any rival, on their level, inside the
// Showdown line, clear of everyone, basins, boiling water and the other items
function itemSpot(R) {
  const zc = zoneCut(), F = foes(R).filter(O => O.st !== 'out'), others = ACTIVE.filter(O => O !== R && O.st !== 'out');
  let best = null, bs = -1e9;
  const at = (x, y, z, bonus) => {
    const d = Math.hypot(x - R.x, z - R.z); if (d < 4.5 || d > 17) return;
    if (zc && zoneOutside(x, z, zc - 2.5)) return;
    if (others.some(O => Math.hypot(O.x - x, O.z - z) < 4) || powers.some(o => o.g && Math.hypot(o.x - x, o.z - z) < 3)) return;
    if (pots.some(p => Math.hypot(p.x - x, p.z - z) < 2) || rivals.some(r => r.on && Math.hypot(r.x - x, r.z - z) < r.rad + 1.2)) return;
    let dr = 30; for (const O of F) dr = Math.min(dr, Math.hypot(O.x - x, O.z - z));
    const ahead = Math.cos(wrapA(Math.atan2(x - R.x, z - R.z) - R.yaw));
    const dy = Math.abs(y - R.y); if (dy > 2.2) return; const sc = -Math.abs(d - 8) * 0.55 + clamp(dr - d, -6, 6) * 0.6 + ahead * 1.5 - dy * 2.5 + (dy < 0.4 ? bonus : 0) + Math.random(); // (on their level: a ledge or a pad only when nothing level will do)
    if (sc > bs) { bs = sc; best = [x, y, z]; } };
  for (const sp of POWER_SPOTS) at(sp[0], sp[1], sp[2], 1);
  const ns = NAV.nodes; for (let k = 0; k < ns.length; k += 2) { const n = ns[k]; if (n.edge > 0 || onRampAt(n.x, n.z, 0.3) || overheadAt(n.x, n.z, n.h, 2.3, 0.4)) continue; at(n.x, n.h, n.z, 0); }
  return best;
}
// the spot, 1.2 s ahead: a beam of light and a ring closing in on it, sparkles rising
function itemMarkGet() { return itemMarkGet.m || (itemMarkGet.m = (() => {
  const c = document.createElement('canvas'); c.width = 4; c.height = 64; const g = c.getContext('2d'), gr = g.createLinearGradient(0, 64, 0, 0);
  gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.45)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 4, 64);
  const tx = new THREE.CanvasTexture(c), add = { transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, fog: false };
  const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.62, 5, 24, 1, true).translate(0, 2.5, 0), new THREE.MeshBasicMaterial(Object.assign({ map: tx, color: 0xFFE7A0 }, add)));
  const po = { polygonOffset: true, polygonOffsetFactor: -8, polygonOffsetUnits: -8 };
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.62, 0.8, 48), new THREE.MeshBasicMaterial(Object.assign({ color: 0xFFE7A0 }, add, po))); ring.rotation.x = -Math.PI / 2;
  const disc = new THREE.Mesh(new THREE.CircleGeometry(0.62, 40), new THREE.MeshBasicMaterial(Object.assign({ color: 0xFFF6D8 }, add, po))); disc.rotation.x = -Math.PI / 2;
  for (const m of [beam, ring, disc]) m.renderOrder = 8;
  const grp = new THREE.Group(); grp.add(beam, ring, disc); grp.visible = false; scene.add(grp); return { g: grp, beam, ring, disc };
})()); }
itemMarkGet(); // (made now, hidden, so the warm-up builds its shaders before a match needs them)
function itemMarkTick(q, dt) {
  const M = itemMarkGet(), k = Math.min(1, q.t / ITEM_WARN), e = 1 - Math.pow(1 - k, 2);
  M.g.position.set(q.x, q.y + 0.04, q.z); M.g.visible = true;
  M.ring.scale.setScalar(2.7 - 1.7 * e); M.ring.material.opacity = 0.35 + 0.6 * e; M.disc.material.opacity = 0.1 + 0.25 * e;
  M.beam.material.opacity = (0.3 + 0.55 * e) * (0.85 + 0.15 * Math.sin(clock * 18)); M.beam.scale.set(1, 0.35 + 0.65 * e, 1);
  if (Math.random() < dt * 30) { const a = Math.random() * 6.283, r = 0.25 + Math.random() * 0.5; spawnPart(q.x + Math.cos(a) * r, q.y + 0.2, q.z + Math.sin(a) * r, 0, 2 + Math.random() * 1.5, 0, 0.6, puHaloMat, 0.16 + Math.random() * 0.12, 0); }
}
const itemType = () => __ITEM_TYPE__;
// it pops (nobody took it, or the Showdown line closed over it)
function itemPop(pw) {
  if (pw.g) { for (let i = 0; i < 10; i++) { const a = i / 10 * 6.283; spawnPart(pw.x, pw.y + 1.05, pw.z, Math.cos(a) * 2.5, 0.5 + Math.random(), Math.sin(a) * 2.5, 0.3, puHaloMat, 0.4); } scene.remove(pw.g); pw.g = null; }
  const ix = powers.indexOf(pw); if (ix >= 0) powers.splice(ix, 1);
}
function itemTick(dt) {
  if (tut) return itemTickOld(dt); // (the first lesson keeps its own script)
  const alive = ACTIVE.filter(D => D.st !== 'out'), IS = itemSpawn;
  for (const D of alive) { if (hasItem(D)) D.emptyT = 0; else if (D.st === 'play') D.emptyT = (D.emptyT || 0) + dt; }
  for (const pw of powers) { if (pw.pop < 1) pw.pop = Math.min(1, pw.pop + dt * 3); if (pw.grace > 0) pw.grace -= dt; pw.age = (pw.age || 0) + dt; }
  for (let i = powers.length - 1; i >= 0; i--) { const pw = powers[i]; if (pw.g && (pw.age > ITEM_STALE || zoneLost(pw.x, pw.z))) itemPop(pw); }
  IS.gap = (IS.gap || 0) - dt;
  if (IS.pend) { const q = IS.pend; q.t += dt; itemMarkTick(q, dt);
    if (q.t >= ITEM_WARN) { IS.pend = null; itemMarkGet().g.visible = false; const pw = { phase: Math.random() * 6, pop: 0, grace: 0, owner: null, age: 0, forD: q.R }; placePower(pw, q.type, [q.x, q.y, q.z]); powers.push(pw); IS.last = q.type; IS.gap = 2;
      if (state === 'play' && Math.hypot(P.x - q.x, P.z - q.z) < 16) AU.pop(); }
    return; }
  if (matchLeft <= 6 || IS.gap > 0) return;
  const empty = alive.filter(D => !hasItem(D)); if (empty.length <= powers.filter(pw => pw.g).length) return;
  // for whoever has waited longest (and has nothing already out there for them); on a tie, whoever's behind
  let R = null; for (const D of empty) { if (D.st !== 'play' || powers.some(pw => pw.g && pw.forD === D)) continue; if (!R || D.emptyT > R.emptyT + 0.5 || (Math.abs(D.emptyT - R.emptyT) <= 0.5 && itemEdge(D) < itemEdge(R))) R = D; }
  if (!R || R.emptyT < itemWait(R, empty.length, alive.length)) return;
  const sp = itemSpot(R); if (!sp) { IS.gap = 1; return; }
  IS.pend = { x: sp[0], y: sp[1], z: sp[2], t: 0, R, type: itemType() };
  if (state === 'play' && Math.hypot(P.x - sp[0], P.z - sp[2]) < 18) AU.spot();
}
"""

PTR_HTML = '<div class="orbptr itemptr" id="itemPtr"><i></i><u><b></b></u></div>\n  '
PTR_CSS = ("\n/* (v285) the arrow to the nearest pick-up while you've got nothing: the item's own icon in a white bubble */"
           "\n.itemptr i{inset:4px;display:grid;place-items:center;background:radial-gradient(circle at 50% 38%,#FFFFFF,#F1F4FF 60%,#C9D6F2);box-shadow:0 0 12px 4px rgba(255,255,255,.6);animation:none}"
           "\n.itemptr.edge i{animation:orbpulse .7s ease-in-out infinite alternate}"
           "\n.itemptr i svg{width:20px;height:20px;fill:#E3122F;stroke:#E3122F}\n")
PTR_JS = """  // (v285) the nearest pick-up while you've got nothing (the one coming for you, if one is): over it when it's on screen and far off, on
  // the screen's edge pointing at it when it isn't
  { const el = $('itemPtr'); let tg = null, ty = null;
    if (playing && P.st === 'play' && !tut && !hasItem(P)) { const q = itemSpawn.pend; if (q && q.R === P) { tg = q; ty = q.type; } else { let bd = 40; for (const pw of powers) if (pw.g && pw.pop >= 0.5) { const d = Math.hypot(pw.x - P.x, pw.z - P.z); if (d < bd) { bd = d; tg = pw; ty = pw.type; } } } }
    if (tg) { tv1.set(tg.x, tg.y + 1.05, tg.z).project(camera); const W = viewW, Hh = viewH, behind = tv1.z > 1; let x = behind ? -tv1.x : tv1.x, y = behind ? -tv1.y : tv1.y;
      const on = !behind && Math.abs(x) < 0.9 && Math.abs(y) < 0.78, far = Math.hypot(tg.x - P.x, tg.z - P.z) > 7;
      if (on && !far) { if (el._on) { el._on = false; el.classList.remove('on'); } }
      else { let px, py, rot; if (on) { px = (x * 0.5 + 0.5) * W; py = (-y * 0.5 + 0.5) * Hh - 48 - Math.abs(Math.sin(clock * 5)) * 6; rot = 180; } else { const m = Math.max(Math.abs(x) / 0.86, Math.abs(y) / 0.72, 1e-3); x /= m; y /= m; px = (x * 0.5 + 0.5) * W; py = (-y * 0.5 + 0.5) * Hh; rot = Math.atan2(x, y) * 180 / Math.PI; }
        if (el._ty !== ty) { el._ty = ty; el.children[0].innerHTML = ITEM_ICON[ty] || ''; }
        if (!el._on) { el._on = true; el.classList.add('on'); } el.classList.toggle('edge', !on); el.style.transform = 'translate(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px)'; el.children[1].style.transform = 'rotate(' + rot.toFixed(0) + 'deg)'; } }
    else if (el._on) { el._on = false; el.classList.remove('on'); } }
"""


def apply(s):
    # ---- 1. the Whirlwind
    s = rep(s, "const WHIRL_WIND = 0.3, WHIRL_DASH = 1.1,", "const WHIRL_WIND = 1.3, WHIRL_DASH = 1.1,") # (v285: a second more notice)
    s = rep(s, "function startWhirl(D) {", WHIRL.lstrip('\n') + "function startWhirl(D) {")
    s = rep(s, "  if (D === P) { AU.rise(); buzz(10); banner('Whirlwind!', 'Steer it into a rival'); } else if (hearable(D)) AU.rise();\n}",
               "  if (D === P) { if (!(AU.xplay && AU.xplay('w_wind', { v: 0.8 }))) AU.rise(); buzz(10); banner('Whirlwind!', 'Aim it. It charges when the lane fills'); } else if (hearable(D) && !(AU.xplay && AU.xplay('w_wind', { v: 0.9 }))) AU.rise();\n}")
    s = rep(s, "function endWhirl(D) { D.whirl = null; if (D.wfx) D.wfx.g.visible = false; }",
               "function endWhirl(D) { D.whirl = null; if (D.wfx) D.wfx.g.visible = false; if (D.wlane) { D.wlane.m.visible = false; D.wlane.sp.visible = false; } }")
    s = rep(s, "  if (W.ph === 'wind') { W.k = Math.min(1, W.t / WHIRL_WIND); W.spinA += dt * (8 + 24 * W.k);\n",
               "  if (W.ph === 'wind') { W.k = Math.min(1, W.t / WHIRL_WIND); W.spinA += dt * (8 + 24 * W.k); whirlWind(D, W, dt);\n")
    # in the charge: it leans toward a rival less, and steers less, so a dodge in time works
    s = rep(s, "let tg = null, tb = 0.55; for (const O of foes(D))", "let tg = null, tb = 0.35; for (const O of foes(D))")
    s = rep(s, "if (tg) D.yaw += clamp(wrapA(Math.atan2(tg.x - D.x, tg.z - D.z) - D.yaw), -1.6 * dt, 1.6 * dt);", "if (tg) D.yaw += clamp(wrapA(Math.atan2(tg.x - D.x, tg.z - D.z) - D.yaw), -0.9 * dt, 0.9 * dt);")
    s = rep(s, "D.whirl ? 0.5 : D.charging ? 0.75", "D.whirl ? (D.whirl.ph === 'dash' ? 0.3 : 0.5) : D.charging ? 0.75")
    s = rep(s, "  // the tornado: on you, along your heading, spinning; it spins up and swells in, and the burst throws it wide as it fades\n",
               "  whirlGlintTick(D, W, dt);\n  // the tornado: on you, along your heading, spinning; it spins up and swells in, and the burst throws it wide as it fades\n")
    # CPUs: routes kept out of a winding lane; in the charge, a roll through it at the last moment
    s = rep(s, "if (zoneOutside(n.x, n.z, zc - 0.6)) nMult[n.id] += 10; } } } // (v256: out past the line)",
               "if (zoneOutside(n.x, n.z, zc - 0.6)) nMult[n.id] += 10; } } } // (v256: out past the line)\n"
               "  if (AI.evade > 0) for (const F of foes(D)) { const W = F.whirl; if (!W || W.ph === 'end') continue; const yw = W.lock !== undefined ? W.lock : F.yaw, fx = Math.sin(yw), fz = Math.cos(yw), L = W.len || whirlV() * WHIRL_DASH; for (let q = 0; q <= L; q += 1.5) NAV.near(F.x + fx * q, F.z + fz * q, F.y, WHIRL_R + 0.9, n => { nMult[n.id] += 8 * AI.evade; }); } // (v285: out of a Whirlwind's lane)")
    s = rep(s, "  if (ai.evadeT > 0) { ai.evadeT -= dt; if (D.charging) cancelCharge(D);",
               "  // (v285) a Whirlwind about to run into it: roll through it at the last moment (as often as its level dodges a pound)\n"
               "  if (AI.dodge > 0 && !D.air && D.rollCD <= 0 && !(D.rollT > 0)) for (const F of foes(D)) { const W = F.whirl; if (!W || W.ph !== 'dash' || (W.seen || (W.seen = new Set())).has(D)) continue;\n"
               "    const fx = Math.sin(F.yaw), fz = Math.cos(F.yaw), dx = D.x - F.x, dz = D.z - F.z, al = dx * fx + dz * fz;\n"
               "    if (al > 0 && Math.abs(dx * fz - dz * fx) < WHIRL_R + 0.3 && al - WHIRL_R < whirlV() * 0.2) { W.seen.add(D); if (Math.random() < AI.dodge && rollSafe(D)) { if (D.charging) cancelCharge(D); dodgeRoll(D); return true; } } }\n"
               "  if (ai.evadeT > 0) { ai.evadeT -= dt; if (D.charging) cancelCharge(D);")
    # a CPU doesn't go at a rival who's whirling (it can't be hit, and it's about to charge): it reads it as untouchable
    s = rep(s, "imm: O.immuneT, charging: O.charging", "imm: O.whirl ? 9 : O.immuneT, charging: O.charging")
    s = rep(s, "if (o && ((o.st === 'play' && runT - o.t < 0.6) || o.st === 'hide') && Math.hypot(o.x - D.x, o.z - D.z) < 3.2)",
               "if (o && o.imm < 5 && ((o.st === 'play' && runT - o.t < 0.6) || o.st === 'hide') && Math.hypot(o.x - D.x, o.z - D.z) < 3.2)")
    s = rep(s, "if (!o || (o.st !== 'play' && !(o.st === 'hide' && AI.coffinHunt > 0))) { ai.mode = 'paint'; ai.thinkT = 0; }",
               "if (!o || o.imm >= 5 || (o.st !== 'play' && !(o.st === 'hide' && AI.coffinHunt > 0))) { ai.mode = 'paint'; ai.thinkT = 0; }")
    # ---- 2. pick-ups by need
    m = s.find("  const type = tut && tut.noTurret ? 'roller' : "); assert m > 0
    e = s.find("; // (the lessons keep to rollers and turrets)", m); assert e > 0
    expr = s[m + len("  const type = "):e]
    s = s[:m] + "  const type = itemType();" + s[e + 1:]
    s = rep(s, "function itemTick(dt) {", "function itemTickOld(dt) {")
    s = rep(s, "// what you hold goes back on the stage when you pick up something else, dropped just behind you\n",
               ITEMS.lstrip('\n').replace('__ITEM_TYPE__', expr) + "// what you hold goes back on the stage when you pick up something else, dropped just behind you\n")
    s = rep(s, "powers = []; itemSpawn.t = 6 + Math.random() * 3; itemSpawn.last = null;\n}",
               "powers = []; itemSpawn.t = 6 + Math.random() * 3; itemSpawn.last = null;\n"
               "  itemSpawn.pend = null; itemSpawn.gap = 0; if (itemMarkGet.m) itemMarkGet.m.g.visible = false; for (const D of [P, H, H2, H3]) if (D) D.emptyT = 0; // (v285)\n"
               "  if (AU.xwant) { AU.xwant('w_wind'); AU.xwant('w_ting'); }\n}")
    # a CPU that has waited a while goes further for one
    s = rep(s, "if (!D.held && Math.random() < AI.grab) { let best = null, bd = 8; for (const pw of powers)",
               "if (!D.held && Math.random() < AI.grab) { let best = null, bd = 8 + Math.min(10, (D.emptyT || 0) * 1.5); for (const pw of powers)")
    # and one that came for it, it goes and gets (as a player would, following the arrow)
    s = rep(s, "const n = NAV.at(pw.x, pw.z, pw.y); if (n && nDist[n.id] < bd) { bd = nDist[n.id]; best = n; } } if (best) return aiGo(D, best, 'grab'); }",
               "const n = NAV.at(pw.x, pw.z, pw.y); if (n && nDist[n.id] < (pw.forD === D ? Math.max(bd, 30) : bd)) { bd = nDist[n.id]; best = n; } } if (best) return aiGo(D, best, 'grab'); }")
    # the arrow to the nearest one
    s = rep(s, '<div class="orbptr giftptr" id="giftPtr">', PTR_HTML + '<div class="orbptr giftptr" id="giftPtr">')
    s = rep(s, "@keyframes giftbob{from{transform:rotate(-8deg)}to{transform:rotate(8deg)}}\n", "@keyframes giftbob{from{transform:rotate(-8deg)}to{transform:rotate(8deg)}}\n" + PTR_CSS.lstrip('\n'))
    s = rep(s, "  // the holy water off screen: an edge marker, red when its pound is coming down near you or it's lining up a fling at you\n",
               PTR_JS + "  // the holy water off screen: an edge marker, red when its pound is coming down near you or it's lining up a fling at you\n")
    return s
