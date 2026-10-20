"""v404: Paint Bomb, a special stroke (the user: "do a special stroke that unlocks at level 6 for 600 dabs. you flash then grow as a
bomb then you explode. it makes a paint radius and kills everyone in the radius").

- Rank 6, 600 dabs, on the Strokes page with its own Ludo-drawn picture and 3D demo; the orb brings it like the other specials.
- Use it: a white flash, then for about a second and a half you swell up like a bomb, a fuse sparking over your head, flashing
  faster and faster, while a ring on the floor shows how far the blast will reach. You can still crawl, so you can carry it to
  them. Then you go off: a huge splat of your paint all round you (BOMB_R), a shockwave, and every rival inside the ring is knocked
  out, in the air or not. Only a basin or a rocket keeps them safe (as from a pound). You come out of it your own size, unhurt.
- Knocked out while it swells, the bomb fizzles. CPUs get it from the orb now and then and keep it until someone's near; when they
  see one swelling near them they run out of the ring or roll away (more often on hard). Offline only, as the other specials."""
import base64, os

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets') + '/'

BOMB_JS = r"""
// ---------- (v404) Paint Bomb: a flash, then you swell up like a bomb, a fuse sparking over your head and a ring on the floor
// showing the reach, and you go off: a huge splat of your paint, and every rival inside the ring is out (a basin or a rocket keeps
// them safe). You come out of it your own size ----------
const BOMB_FLASH = 0.25, BOMB_GROW = 1.45, BOMB_R = 5.4, BOMB_K = 2.0, bombList = [];
function startBomb(D) {
  for (const B of bombList) if (B.by === D) return; // (one at a time)
  const ring = new THREE.Mesh(STORM_RING, new THREE.MeshBasicMaterial(stormFlat())), fill = new THREE.Mesh(STORM_DISC, new THREE.MeshBasicMaterial(stormFlat()));
  ring.rotation.x = fill.rotation.x = -Math.PI / 2; ring.renderOrder = 7; fill.renderOrder = 6; ring.material.color.set(TEAMS[D.team].wet); fill.material.color.set(TEAMS[D.team].wet);
  ring.visible = fill.visible = false; scene.add(ring, fill);
  const B = { by: D, t: 0, ring, fill, spark: 0, beep: 0, dodge: [] }; bombList.push(B); D.bombK = 1;
  D.wob = 1; D.squash = 0.6; emote(D, 'glee', 1.2); hitStop(0.06, D); shockwave(D.x, D.y, D.z, 2.2, 0xFFFFFF);
  for (let i = 0; i < 14; i++) { const a = Math.random() * 6.283, s = 1 + Math.random() * 2; spawnPart(D.x, D.y + 0.5, D.z, Math.cos(a) * s, 2 + Math.random() * 3, Math.sin(a) * s, 0.4 + Math.random() * 0.2, puHaloMat, 0.45); }
  if (hearable(D)) { AU.rise ? AU.rise() : AU.whoosh(); }
  if (D === P) { shake = Math.max(shake, 0.2); buzz([10, 20, 10]); flashScreen(); banner('Paint bomb!', 'Get close. Everyone in the ring goes'); }
  else if (ally(D, P)) banner(nameOf(D) + ' is going to blow!', 'It won’t hit you');
  else { banner(nameOf(D) + ' is going to blow!', 'Get out of the ring'); AU.spot && AU.spot(); }
  // CPUs that see it coming run out of the ring, or roll away at the last moment (more often on hard)
  for (const F of foes(D)) if (F.ai && F.st === 'play' && Math.hypot(F.x - D.x, F.z - D.z) < BOMB_R + 2.5 && Math.random() < (diff === 'easy' ? 0.3 : diff === 'hard' ? 0.75 : 0.5)) B.dodge.push(F);
  for (const F of ACTIVE) if (F.ai) F.ai.thinkT = 0;
}
function bombDrop(B) { scene.remove(B.ring, B.fill); B.ring.material.dispose(); B.fill.material.dispose(); if (B.by.bombK) B.by.bombK = 0; }
function clearBombs() { for (const B of bombList) bombDrop(B); bombList.length = 0; }
function bombBlow(B) {
  const D = B.by, x = D.x, z = D.z, gy0 = surfaceUnder(x, z, D.y + STEP, true), gy = gy0 > -Infinity ? gy0 : D.y;
  // the paint: a big splat and a ring of smaller ones round its edge
  addSplat(x, gy, z, Math.random() * 6.2832, BOMB_R, dryClock, false, true, tcode(D));
  const n = 12; for (let k = 0; k < n; k++) { const a = k / n * 6.2832 + Math.random() * 0.3, r = BOMB_R * (0.7 + Math.random() * 0.25), px = x + Math.cos(a) * r, pz = z + Math.sin(a) * r, g = surfaceUnder(px, pz, gy + 1.5, true); if (g > -Infinity && Math.abs(g - gy) < 1.5) addSplat(px, g, pz, a, 1.1 + Math.random() * 0.6, dryClock, false, true, tcode(D)); }
  shockwave(x, gy, z, BOMB_R * 1.15, 0xFFFFFF); shockwave(x, gy, z, BOMB_R * 0.85, TEAMS[D.team].wet); shockwave(x, gy, z, BOMB_R * 0.45, 0xFFFFFF);
  for (let i = 0; i < 46; i++) { const a = Math.random() * 6.283, s = 4 + Math.random() * 7; spawnPart(x + Math.cos(a) * 0.4, gy + 0.5, z + Math.sin(a) * 0.4, Math.cos(a) * s, 3 + Math.random() * 6, Math.sin(a) * s, 0.6 + Math.random() * 0.4, i % 4 ? tmat(D) : puHaloMat, 0.5 + Math.random() * 0.6); }
  if (typeof startQuake === 'function') startQuake(0.45 * Math.max(0.3, 1 - dp0(D) / 30));
  const dp = dp0(D); if (D === P) { shake = Math.max(shake, 0.6); buzz([30, 30, 60]); } else if (dp < 26) shake = Math.max(shake, 0.5 * (1 - dp / 26));
  if (dp < 30) { AU.at(x, z); AU.burst(1); AU.slam(); }
  D.squash = 1; D.wob = 1; D.bombK = 0;
  if (matchLeft <= 0) return;
  let kos = 0;
  for (const O of foes(D)) {
    if (O.st !== 'play' || O.rocket || O.immuneT > 0) continue;
    if (Math.hypot(O.x - x, O.z - z) > BOMB_R + PR) continue;
    const og = O.air ? surfaceUnder(O.x, O.z, O.y + STEP, true) : O.y, base = og > -Infinity ? og : O.y;
    if (Math.abs(base - gy) > 2.2 || safe(O)) continue;
    poundHit(O, D, 'bomb'); kos++;
  }
  if (D === P && kos > 1) popText(kos + ' at once!');
}
function bombTick(dt) {
  for (let i = bombList.length - 1; i >= 0; i--) {
    const B = bombList[i], D = B.by; B.t += dt;
    if (state !== 'play' || D.st !== 'play') { if (D.st !== 'play' && state === 'play') { shockwave(D.x, D.y, D.z, 1.4, 0xFFFFFF); if (D === P) popText('Fizzled'); } bombDrop(B); bombList.splice(i, 1); continue; }
    const g = Math.max(0, B.t - BOMB_FLASH), u = Math.min(1, g / BOMB_GROW), e = 1 - Math.pow(1 - u, 2);
    // swelling, with a throb that quickens toward the end
    const rate = 4 + 18 * u * u; B.ph = (B.ph || 0) + dt * rate; const throb = 0.07 * u * Math.max(0, Math.sin(B.ph * 6.2832));
    D.bombK = 1 + (BOMB_K - 1) * e + throb; D.wob = Math.max(D.wob, 0.25);
    // the reach, on the floor
    const gy = surfaceUnder(D.x, D.z, D.y + STEP, true);
    B.ring.visible = B.fill.visible = gy > -Infinity && B.t > BOMB_FLASH * 0.5;
    if (B.ring.visible) { const pulse = 0.5 + 0.5 * Math.sin(B.ph * 6.2832), grow = 1 - Math.pow(1 - Math.min(1, u / 0.4), 3);
      B.ring.position.set(D.x, gy + 0.07, D.z); B.fill.position.set(D.x, gy + 0.06, D.z); B.ring.scale.setScalar(Math.max(0.01, (0.35 + 0.65 * grow) * BOMB_R)); B.fill.scale.setScalar(Math.max(0.01, BOMB_R * (0.2 + 0.8 * u)));
      B.ring.material.color.set(TEAMS[D.team].wet).lerp(COL_WHITE, 0.25 + 0.5 * pulse); B.ring.material.opacity = 0.6 + 0.4 * u; B.fill.material.opacity = 0.08 + 0.22 * u * (0.6 + 0.4 * pulse); }
    // the fuse: sparks over its head, and a tick as it throbs
    B.spark += dt * (30 + 50 * u); while (B.spark >= 1) { B.spark -= 1; const h = D.y + PR * 2 * D.bombK + 0.15, a = Math.random() * 6.283, s = 0.8 + Math.random() * 1.6; spawnPart(D.x, h, D.z, Math.cos(a) * s, 1.5 + Math.random() * 2, Math.sin(a) * s, 0.25 + Math.random() * 0.15, Math.random() < 0.6 ? puHaloMat : tmat(D), 0.18 + Math.random() * 0.15); }
    if (B.ph - (B.beepPh || 0) >= 1) { B.beepPh = Math.floor(B.ph); if (hearable(D) && AU.tick) AU.tick(0); if (D === P) buzz(4); }
    // the CPUs that saw it coming: run, then roll away at the last moment
    if (B.dodge.length) { for (const F of B.dodge) { if (F.st !== 'play') continue; const dx = F.x - D.x, dz = F.z - D.z; if (Math.hypot(dx, dz) > BOMB_R + PR + 0.4) continue; const away = Math.atan2(dx, dz); F.yaw += wrapA(away - F.yaw) * Math.min(1, dt * 8); if (F.ai) F.ai.thinkT = 0.3;
        if (g > BOMB_GROW - 0.3 && !F.bombRolled) { F.bombRolled = true; F.yaw = away; dodgeRoll(F); } } }
    if (g >= BOMB_GROW) { for (const F of B.dodge) F.bombRolled = false; bombBlow(B); bombDrop(B); bombList.splice(i, 1); }
  }
}
"""

SG_JS = r"""
// Paint Bomb: a flash, the blob swells and throbs with a fuse sparking, the ring on the pad, then the blast: a big splat and the
// rival in it knocked out
function sgBombBits() {
  if (SGD.bb) return SGD.bb;
  const ring = new THREE.Mesh(STORM_RING, new THREE.MeshBasicMaterial(stormFlat())); ring.rotation.x = -Math.PI / 2; ring.renderOrder = 7; ring.visible = false; SGD.root.add(ring); sgLayer(ring);
  return (SGD.bb = { ring, ph: 0 });
}
function sgBombOff() { const T = SGD.bb; if (T) T.ring.visible = false; if (SGD.A) SGD.A.D.bombK = 0; }
function sgBomb(dt, t, s) {
  const A = SGD.A, B = SGD.B, DA = A.D, DB = B.D, cA = TEAMS[0].css, T = sgBombBits(), ON = 0.5, GO = 2.3, R = 1.25;
  if (t < ON) { sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'ready'; DA.bombK = 0; }
  else if (sgOnce('flash')) { const x = sgLX(A), z = sgLZ(A); DA.squash = 0.6; DA.wob = 1; emote(DA, 'glee', 1.1); sgRing(x, z, 0.9, 0xFFFFFF); sgBurst(x, z, '#FFFFFF', 10, 3.4, 1.6); sgShk(0.2); T.ring.material.color.set(TEAMS[0].wet); T.ph = 0; }
  if (t >= ON && t < GO) { const u = Math.min(1, (t - ON) / (GO - ON)), e = 1 - Math.pow(1 - u, 2); T.ph += dt * (4 + 18 * u * u);
    DA.bombK = 1 + 0.75 * e + 0.06 * u * Math.max(0, Math.sin(T.ph * 6.2832)); DA.wob = Math.max(DA.wob, 0.25); DA.ip.expr = 'menace'; sgWatch(A, B);
    T.ring.visible = true; T.ring.position.set(sgLX(A), 0.035, sgLZ(A)); T.ring.scale.setScalar(Math.max(0.01, R * (0.4 + 0.6 * Math.min(1, u / 0.4)))); T.ring.material.color.set(TEAMS[0].wet).lerp(COL_WHITE, 0.3 + 0.5 * (0.5 + 0.5 * Math.sin(T.ph * 6.2832)));
    if (Math.random() < dt * 40) sgPart(sgLX(A), 0.62 * DA.bombK, sgLZ(A), (Math.random() - 0.5) * 1.2, 1 + Math.random(), (Math.random() - 0.5) * 1.2, 0.3, '#FFE08A', 0.12);
    if (t > 0.9) { const p = sgCS(-0.2 * s, 0.2); sgGo(A, p[0], p[1], 0.5, dt); } }
  if (t >= GO && sgOnce('boom')) { const x = sgLX(A), z = sgLZ(A); DA.bombK = 0; DA.squash = 1; DA.wob = 1; T.ring.visible = false;
    sgSplat(x, z, R, cA); sgRing(x, z, R * 1.15, 0xFFFFFF); sgRing(x, z, R * 0.8, TEAMS[0].wet); sgBurst(x, z, A.col, 26, 5.5, 2.4); sgShk(0.6);
    if (B.show && Math.hypot(sgLX(B) - x, sgLZ(B) - z) < R + 0.35) { sgKO(B, cA); emote(DA, 'glee', 1.3); } }
  if (B.show && t >= ON && t < GO) { DB.ip.expr = 'scared'; if (t > 1.1) { const p = sgCS(0.75 * s, -0.4); sgGo(B, p[0], p[1], 0.35, dt); } else sgFace(B, sgYawTo(B, A), dt, 4); }
  if (t >= GO + 0.4) { sgHalt(A, dt); sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'glee'; }
  if (t >= 4.4 && sgOnce('back')) { const p = sgCS(0.75 * s, -0.4); sgBack(B, p[0], p[1], sgYawTo(B, A)); }
}
"""

def apply(s):
    img = 'data:image/webp;base64,' + base64.b64encode(open(A + 'bomb_flat_256.webp', 'rb').read()).decode()
    s = rep(s, "SKILLS.push({ id: 'shock', name: 'Aftershock',",
               "SPECIALS.push({ id: 'bomb', rank: 6, name: 'Paint Bomb', desc: 'Swell up like a bomb and blow: everyone in the blast is out.', does: ['A flash, then you swell up like a bomb for a second and a half', 'A ring on the floor shows how far the blast will reach', 'Every rival inside it is knocked out, and the ground is yours'] }); // (v404)\n"
               "SKILLS.push({ id: 'shock', name: 'Aftershock',")
    s = rep(s, "shock: 400, storm: 600 };", "shock: 400, storm: 600, bomb: 600 };")
    s = rep(s, "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets', 'storm', 'shock']) STROKE_ICON[k] = stImg(k);",
               "ST_IMG.bomb = '" + img + "'; // (v404: Ludo.ai, the same style)\n"
               "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets', 'storm', 'shock', 'bomb']) STROKE_ICON[k] = stImg(k);")
    s = rep(s, "freeze: 'Freeze', storm: 'Storm' };", "freeze: 'Freeze', storm: 'Storm', bomb: 'Bomb' };")
    s = rep(s, "function cpuGift() { const r = Math.random(); return !tut && !tut2 && !tut3 && r < 0.36 ? (r < 0.18 ? 'freeze' : 'storm') : ['giant', 'rocket'][(Math.random() * 2) | 0]; }",
               "function cpuGift() { const r = Math.random(); return !tut && !tut2 && !tut3 && r < 0.46 ? (r < 0.15 ? 'freeze' : r < 0.31 ? 'storm' : 'bomb') : ['giant', 'rocket'][(Math.random() * 2) | 0]; } // (v404: the bomb too)")
    s = rep(s, "  if (gift === 'storm') { startStorm(D); return; } // (v384)\n", "  if (gift === 'storm') { startStorm(D); return; } // (v384)\n  if (gift === 'bomb') { startBomb(D); return; } // (v404)\n")
    s = rep(s, "if (D.orbSaved === 'storm' && D.orbT > 2.5 && !foes(D).some(F => F.st === 'play' && Math.hypot(F.x - D.x, F.z - D.z) < 11)) D.ai.orbWait = 0.4;",
               "if (D.orbSaved === 'storm' && D.orbT > 2.5 && !foes(D).some(F => F.st === 'play' && Math.hypot(F.x - D.x, F.z - D.z) < 11)) D.ai.orbWait = 0.4; else if (D.orbSaved === 'bomb' && D.orbT > 2 && !foes(D).some(F => F.st === 'play' && Math.hypot(F.x - D.x, F.z - D.z) < BOMB_R * 0.8)) D.ai.orbWait = 0.3; /* (v404: a bomb kept till someone's close) */")
    s = rep(s, "const KO_MSG = { storm: 'Caught in the storm!',", "const KO_MSG = { bomb: 'Blown away!', storm: 'Caught in the storm!',")
    s = rep(s, "const CPU_KO_MSG = { storm: n => 'Stormed ' + n + '!',", "const CPU_KO_MSG = { bomb: n => 'Blew up ' + n + '!', storm: n => 'Stormed ' + n + '!',")
    s = rep(s, "\n// ---------- the giant orb: a glowing, color-shifting orb", BOMB_JS + "\n// ---------- the giant orb: a glowing, color-shifting orb")
    s = rep(s, "freezeTick(dt); stormTick(dt); shockTick(dt);", "freezeTick(dt); stormTick(dt); bombTick(dt); shockTick(dt);")
    s = rep(s, "clearStorms(); clearShocks();", "clearStorms(); clearBombs(); clearShocks();")
    # the swelling: drawn the way a giant's size is
    s = rep(s, "gt = D.giantT > 0 ? (D.giantT < 0.9 && !D.slam && Math.sin(clock * 40) > 0 ? gkTo * 0.75 : gkTo) : 1;",
               "gt = D.giantT > 0 ? (D.giantT < 0.9 && !D.slam && Math.sin(clock * 40) > 0 ? gkTo * 0.75 : gkTo) : D.bombK || 1; /* (v404: a paint bomb swelling) */")
    # the Strokes page demo
    s = rep(s, "freeze: 6.6, storm: 5.8 };", "freeze: 6.6, storm: 5.8, bomb: 5.2 };")
    s = rep(s, "  else if (k === 'storm') { sgAtC(A, -0.7 * s, 0.45); sgAtC(B, 0.55 * s, -0.45); }\n",
               "  else if (k === 'storm') { sgAtC(A, -0.7 * s, 0.45); sgAtC(B, 0.55 * s, -0.45); }\n  else if (k === 'bomb') { sgAtC(A, -0.55 * s, 0.4); sgAtC(B, 0.45 * s, -0.25); }\n")
    s = rep(s, "sgStormOff(); SGD.iceK = 0;", "sgStormOff(); sgBombOff(); SGD.iceK = 0;")
    s = rep(s, "  else if (k === 'storm') sgStorm(dt, t, s);\n", "  else if (k === 'storm') sgStorm(dt, t, s);\n  else if (k === 'bomb') sgBomb(dt, t, s);\n")
    s = rep(s, "\n// the whirlwind's lane: a strip on the pad", SG_JS + "\n// the whirlwind's lane: a strip on the pad")
    return s
