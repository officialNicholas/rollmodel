"""v301: a new pick-up, the Paint Boomerang.

- Tap it to throw. It flies out ahead, swings round in a loop and comes back to you, painting a stripe the whole way (wider than
  your trail). Turning as you throw curves it your way; thrown at a rival just ahead, it leans in on them.
- Any rival it clips, going out or coming back, is knocked out ("Boomeranged!"). A jump takes you over it and a dodge roll goes
  through it. A giant swats it away.
- It rides up over low walls and turns back at a tall one. If you're knocked out before it's home, it drops and splats where it is.
  You catch it with a pop.
- CPUs pick it up and throw it at whoever is ahead of them. They duck it as often as their level dodges a pound.
- It spawns with the other pick-ups, about as often as the Whirlwind. It's a start item on the Strokes page from rank 9 (25 minutes
  on the bench), with a painted sticker like the others. The first time a rival's boomerang heads your way there's a tip: jump or roll.
  CPUs sometimes start with one too."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

import base64, os
IMG = base64.b64encode(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'st_boom.webp'), 'rb').read()).decode()

CODE = r"""
// ---------- (v301) the Paint Boomerang: thrown ahead, it swings out in a loop and homes back to you, painting a stripe all the way.
// Any rival it clips is knocked out (a jump or a roll gets you clear); it rides up over low walls, a tall one turns it back, and if you
// go down before it's home it drops where it is ----------
const BOOM_OUT = 0.62, BOOM_V = 15, BOOM_BACK = 16.5, BOOM_TURN = 5.2, BOOM_CURVE = 1.6, BOOM_HOME = 1.6, BOOM_R = 0.62, BOOM_H = 0.55, BOOM_LIFE = 3.2, BOOM_STEP = 0.24, BOOM_W = 1.35;
const booms = []; let boomSide = 1, BOOM_GEO = null;
function boomGeo() {
  if (BOOM_GEO) return BOOM_GEO;
  const curve = new THREE.QuadraticBezierCurve3(new THREE.Vector3(-0.4, 0, 0.12), new THREE.Vector3(0, 0, -0.34), new THREE.Vector3(0.4, 0, 0.12));
  const S = 1.6, part = (r, sy) => { const t = new THREE.TubeGeometry(curve, 28, r, 10, false), a = new THREE.SphereGeometry(r, 12, 8).translate(-0.4, 0, 0.12), b = new THREE.SphereGeometry(r, 12, 8).translate(0.4, 0, 0.12), g = mergeGeos([t, a, b]); g.scale(S, sy * S, S); g.computeVertexNormals(); return g; };
  // the painted tips: the last stretch of each arm, a touch fatter, so the cream body reads as dipped in your paint
  const dip = u => { const pts = []; for (let k = 0; k <= 8; k++) pts.push(curve.getPoint(u[0] + (u[1] - u[0]) * k / 8)); const c = new THREE.CatmullRomCurve3(pts), t = new THREE.TubeGeometry(c, 10, 0.082, 10, false), e = curve.getPoint(u[1] > u[0] ? 1 : 0), cap = new THREE.SphereGeometry(0.082, 12, 8).translate(e.x, e.y, e.z), g = mergeGeos([t, cap]); g.scale(S, 0.46 * S, S); g.computeVertexNormals(); return g; };
  BOOM_GEO = { body: part(0.075, 0.42), hull: part(0.1, 0.54), tips: mergeGeos([dip([0.74, 1]), dip([0.26, 0])]), band: new THREE.TorusGeometry(0.083, 0.024, 6, 16).rotateX(Math.PI / 2).scale(S, 0.62 * S, S).translate(0, 0, -0.11 * S) };
  BOOM_GEO.tips.computeVertexNormals();
  return BOOM_GEO;
}
const boomBodyM = toon(0xFFF4C9);
function boomMesh(mat, plain) {
  const G = boomGeo(), g = new THREE.Group(), spin = new THREE.Group(); g.add(spin);
  const body = new THREE.Mesh(G.body, plain ? mat : boomBodyM), hull = new THREE.Mesh(G.hull, outlineMat), tips = new THREE.Mesh(G.tips, mat), band = new THREE.Mesh(G.band, plain ? boomBodyM : mat);
  body.castShadow = true; spin.add(hull, body, tips); if (plain) spin.add(band); spin.rotation.x = 0.32; return { g, spin };
}
function throwBoom(D) {
  if (D.charging) clearCharge(D); if (D === P) { holdCharge = false; slingOff(); }
  // a rival roughly ahead: thrown straight at them (a CPU squares up to the nearest in front of it)
  let tgt = null, tb = D.ai ? 0.9 : 0.42; for (const F of foes(D)) if (F.st === 'play') { const dx = F.x - D.x, dz = F.z - D.z, d = Math.hypot(dx, dz); if (d < 2 || d > 12) continue; const da = Math.abs(wrapA(Math.atan2(dx, dz) - D.yaw)); if (da < tb) { tb = da; tgt = F; } }
  const yaw = tgt ? Math.atan2(tgt.x - D.x, tgt.z - D.z) : D.yaw, curve = Math.abs(D.turn || 0) > 0.3 ? Math.sign(D.turn) : (boomSide = -boomSide);
  const gy = surfaceUnder(D.x, D.z, D.y + 0.4, true), y0 = (gy > -Infinity ? gy : D.y) + BOOM_H, M = boomMesh(tmat(D));
  const B = { owner: D, x: D.x + Math.sin(yaw) * 0.45, z: D.z + Math.cos(yaw) * 0.45, y: y0, yaw, curve, tgt, ph: 'out', t: 0, spin: 0, vy: 0, hit: new Set(), seen: new Set(), dist: 0, stroke: 1, rb: { stroke: -1 }, swT: 0, warned: false, g: M.g, sp: M.spin };
  B.g.position.set(B.x, B.y, B.z); scene.add(B.g); booms.push(B);
  D.squash = Math.max(D.squash, 0.4); D.wob = Math.max(D.wob, 0.6); emote(D, 'glee', 0.8);
  if (D === P) { AU.whoosh(); buzz(10); shake = Math.max(shake, 0.05); hint('boom', 'It loops out and comes back to you', 2.6); } else if (hearable(D)) AU.whoosh();
}
function boomGone(B) { scene.remove(B.g); const ix = booms.indexOf(B); if (ix >= 0) booms.splice(ix, 1); }
function boomClear() { for (const B of booms) scene.remove(B.g); booms.length = 0; }
function boomCatch(B) {
  const O = B.owner; boomGone(B); O.squash = Math.max(O.squash, 0.3); O.wob = Math.max(O.wob, 0.5);
  for (let i = 0; i < 8; i++) { const a = i / 8 * 6.283; spawnPart(O.x, O.y + 0.5, O.z, Math.cos(a) * 2.2, 1 + Math.random(), Math.sin(a) * 2.2, 0.3, tmat(O), 0.35); }
  if (O === P) { AU.pop(); buzz(8); } else if (hearable(O)) AU.pop();
}
function boomDrop(B) { if (B.ph === 'drop') return; B.ph = 'drop'; B.t = 0; B.vy = 1.5; }
function boomTick(dt) {
  for (let i = booms.length - 1; i >= 0; i--) {
    const B = booms[i], O = B.owner; B.t += dt; B.spin += dt * (B.ph === 'drop' ? 8 : 24); B.sp.rotation.y = B.spin;
    if (B.ph === 'drop') { // falling where it is, then a splat
      if (B.done) { const k = 1 - B.t / 0.3; if (k <= 0) { boomGone(B); continue; } B.g.scale.setScalar(k); continue; }
      B.vy -= GRAV * dt; B.y += B.vy * dt; const g = surfaceUnder(B.x, B.z, B.y + 0.3, true);
      if (g > -Infinity && B.y <= g + 0.06) { B.y = g + 0.06; B.done = true; B.t = 0; addSplat(B.x, g, B.z, B.yaw, 0.9, dryClock, false, false, tcode(O), 0); if (Math.hypot(B.x - P.x, B.z - P.z) < 14) { AU.at(B.x, B.z); AU.plop(); } }
      else if (B.y < -12) { boomGone(B); continue; }
      B.g.position.set(B.x, B.y, B.z); continue;
    }
    const home = O.st === 'play' || O.st === 'hide';
    if (B.ph === 'out') {
      if (B.tgt && B.tgt.st === 'play' && !B.hit.has(B.tgt)) B.yaw += clamp(wrapA(Math.atan2(B.tgt.x - B.x, B.tgt.z - B.z) - B.yaw), -BOOM_HOME * dt, BOOM_HOME * dt); // (a fair aim lands)
      else B.yaw += B.curve * BOOM_CURVE * dt;
      if (B.t >= BOOM_OUT || Math.abs(B.x) > ARENA + 3 || Math.abs(B.z) > ARENA + 3) { B.ph = 'back'; B.t = 0; }
    } else {
      if (!home || B.t > BOOM_LIFE) { boomDrop(B); continue; }
      B.yaw += clamp(wrapA(Math.atan2(O.x - B.x, O.z - B.z) - B.yaw), -BOOM_TURN * dt, BOOM_TURN * dt);
      if (Math.hypot(O.x - B.x, O.z - B.z) < 0.9 && Math.abs(O.y + 0.4 - B.y) < 1.3) { boomCatch(B); continue; }
    }
    const v = B.ph === 'out' ? BOOM_V : BOOM_BACK, nx = B.x + Math.sin(B.yaw) * v * dt, nz = B.z + Math.cos(B.yaw) * v * dt;
    // the ground under it: it rides over low walls; a tall one turns it back on the way out (and it climbs over it on the way home)
    const top = surfaceUnder(nx, nz, 99), want = (top > -Infinity ? top : Math.min(B.y - BOOM_H, 0)) + BOOM_H;
    if (B.ph === 'out' && top > B.y + 0.7) { B.ph = 'back'; B.t = 0; B.yaw = wrapA(B.yaw + Math.PI); if (Math.hypot(B.x - P.x, B.z - P.z) < 14) { AU.at(B.x, B.z); AU.bonk(0.5); } continue; }
    B.x = nx; B.z = nz; B.y += clamp(want - B.y, -6 * dt, (B.ph === 'out' ? 12 : 30) * dt);
    // the stripe
    B.dist += v * dt;
    while (B.dist >= BOOM_STEP) { B.dist -= BOOM_STEP; const gy = surfaceUnder(B.x, B.z, B.y + 0.1); if (gy === -Infinity || B.y - gy > 1.4) { B.stroke++; continue; } addPoint(B.x, gy, B.z, B.yaw, dryClock, B.stroke, BOOM_W, tcode(O), B.rb, [B.x, gy, B.z]); }
    if (Math.random() < dt * 30) spawnPart(B.x, B.y, B.z, (Math.random() - 0.5) * 2, 1 + Math.random(), (Math.random() - 0.5) * 2, 0.4, tmat(O), 0.3 + Math.random() * 0.2);
    // anyone it clips; a CPU that sees it coming may jump or roll
    for (const F of foes(O)) {
      if (B.hit.has(F) || F.st !== 'play') continue;
      const dx = F.x - B.x, dz = F.z - B.z, hx = Math.sin(B.yaw), hz = Math.cos(B.yaw), al = dx * hx + dz * hz;
      if (F.ai && !B.seen.has(F) && al > 0 && al < v * 0.32 && Math.abs(dx * hz - dz * hx) < BOOM_R + PR + 0.25) { B.seen.add(F); if (AI.dodge > 0 && Math.random() < AI.dodge && !F.air && !F.charging) { if (F.rollCD <= 0 && rollSafe(F)) dodgeRoll(F); else if (hopOK(F)) jump(F); } }
      if (F === P && !B.warned && al > 0 && al < 9) { B.warned = true; hint('boomdodge', say('A boomerang! Jump or swipe up to dodge it', 'A boomerang! Jump or Shift to dodge it'), 3); }
      if (safe(F) || F.immuneT > 0 || F.rocket || dx * dx + dz * dz > (BOOM_R + PR) ** 2 || F.y > B.y + 0.12 || F.y + 0.8 < B.y - 0.25) continue;
      B.hit.add(F);
      if (F.giantT > 0) { if (B.ph === 'out') { B.ph = 'back'; B.t = 0; } F.wob = 1; if (hearable(F)) AU.bonk(0.7); continue; } // (a giant swats it away)
      knockOut(F, 'boom', O); if (O === P) { shake = Math.max(shake, 0.2); buzz([12, 20, 12]); }
    }
    B.swT -= dt; if (B.swT <= 0) { B.swT = 0.22; if (Math.hypot(B.x - P.x, B.z - P.z) < 14) { AU.at(B.x, B.z); AU.swish(); } }
    B.g.position.set(B.x, B.y, B.z);
  }
}
"""

ICON = ('<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M4.2 28.6C6 14.5 34 14.5 35.8 28.6c.3 2.2-2.3 3.4-3.9 1.9C27 25.4 13 25.4 8.1 30.5c-1.6 1.5-4.2.3-3.9-1.9z"/>'
        '<path d="M12.5 9.5c4.6-2.4 10.4-2.4 15 0M15.5 5c2.9-1.3 6.1-1.3 9 0" fill="none" stroke-width="2.4" stroke-linecap="round"/></svg>')

def apply(s):
    # the pick-up
    a = "  trap: { name: 'Paint Trap', dur: 0, tip: 'Paint Trap! Drop it, and the next rival over it gets splatted.' },"
    s = rep(s, a, a + "\n  boom: { name: 'Boomerang', dur: 0, tip: 'Boomerang! Throw it out in a loop: it paints its path, knocks out rivals and comes back.' }, // (v301)")
    a = "const puIconMat = toon(0xE3122F), puHaloMat = toon(0xFFFFFF);"
    s = rep(s, a, a + CODE.rstrip('\n'))
    a = "  else if (type === 'whirl') { const t = new THREE.Group(); t.rotation.x = Math.PI / 2; t.scale.setScalar(0.24); t.position.y = -0.17; spin.add(t); const a = new THREE.Mesh(WHIRL_G.paint, whirlPickM), b = new THREE.Mesh(WHIRL_G.streak, whirlStreakM); a.renderOrder = b.renderOrder = 9; t.add(a, b); }"
    s = rep(s, a, a + "\n  else if (type === 'boom') { const M = boomMesh(puIconMat, true); M.g.scale.setScalar(0.5); M.spin.rotation.x = 0.5; spin.add(M.g); } // (v301)")
    a = "  if (type === 'trap') { dropTrap(D); for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return true; }"
    s = rep(s, a, a + "\n  if (type === 'boom') { throwBoom(D); for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return true; } // (v301)")
    # how often it spawns, and what CPUs start with
    s = rep(s, "const w = { roller: 0.42, turret: 0.3, trap: 0.28, whirl: 0.3 };", "const w = { roller: 0.42, turret: 0.3, trap: 0.28, whirl: 0.3, boom: 0.3 };")
    s = rep(s, "cpuItem = () => { const r = Math.random(); return r < 0.32 ? 'roller' : r < 0.56 ? 'turret' : r < 0.78 ? 'trap' : 'whirl'; };",
               "cpuItem = () => { const r = Math.random(); return r < 0.27 ? 'roller' : r < 0.47 ? 'turret' : r < 0.65 ? 'trap' : r < 0.83 ? 'whirl' : 'boom'; };")
    # CPUs throw it at whoever is ahead
    s = rep(s, "|| D.heldT > 8 : D.heldT > 1 + Math.random() * 1.5)) useHeld(D); }",
               "|| D.heldT > 8 : D.held === 'boom' ? (O && O.st === 'play' && Math.hypot(O.x - D.x, O.z - D.z) < 11 && Math.hypot(O.x - D.x, O.z - D.z) > 2.5 && Math.abs(wrapA(Math.atan2(O.x - D.x, O.z - D.z) - D.yaw)) < 0.8 && D.heldT > 0.5) || D.heldT > 8 : D.heldT > 1 + Math.random() * 1.5)) useHeld(D); }")
    # every frame in a match; cleared when a match starts or ends
    s = rep(s, "blobContact(); updateOrb(dt); updateShots(dt);", "blobContact(); updateOrb(dt); updateShots(dt); boomTick(dt);")
    s = rep(s, "function placePowers() {\n  clearTraps();", "function placePowers() {\n  clearTraps(); boomClear();")
    s = rep(s, "qMatchEnd(); for (const D of ACTIVE) if (D.charging) clearCharge(D);", "qMatchEnd(); boomClear(); for (const D of ACTIVE) if (D.charging) clearCharge(D);", 2)
    # the knock-out lines and sound
    s = rep(s, "crush: 'Crushed!', dry: 'Dried up!' };", "crush: 'Crushed!', dry: 'Dried up!', boom: 'Boomeranged!' };")
    s = rep(s, "crush: n => 'Crushed ' + n + '!', dry: n => n + ' dried up!' };", "crush: n => 'Crushed ' + n + '!', dry: n => n + ' dried up!', boom: n => 'Boomeranged ' + n + '!' };")
    s = rep(s, "AU.die(reason === 'coffin' || reason === 'crush' ? 'pound' : reason)", "AU.die(reason === 'coffin' || reason === 'crush' || reason === 'boom' ? 'pound' : reason)")
    # the button, the Strokes page, the warm-up
    a = "ITEM_ICON.whirl = '"
    s = rep(s, a, "ITEM_ICON.boom = '" + ICON + "'; // (v301)\n" + a)
    a = "'Leaves a wide trail and ends in a burst. Steer as you go'] }); // (v271)"
    s = rep(s, a, a + "\nST_ITEMS.push({ id: 'boom', name: 'Boomerang', desc: 'Throw it out in a loop. It comes back.', does: ['Tap it: it flies out ahead, swings round and comes back to you', 'It paints a stripe the whole way and knocks out any rival it clips', 'Turning as you throw curves it your way. Rivals can jump or roll to dodge'] }); // (v301)")
    s = rep(s, "const R = { roller: [1, 0], turret: [3, 10], trap: [5, 15], whirl: [7, 20] };", "const R = { roller: [1, 0], turret: [3, 10], trap: [5, 15], whirl: [7, 20], boom: [9, 25] };")
    a = "ST_IMG.whirl = 'data:image/webp;base64,"
    s = rep(s, a, "ST_IMG.boom = 'data:image/webp;base64," + IMG + "'; STROKE_ICON.boom = stImg('boom'); // (v301: Ludo.ai, in the stickers' style)\n" + a)
    s = rep(s, "for (const t of ['roller', 'turret', 'whirl']) try { makePowerMesh(t).g.visible = false; } catch (e) {}", "for (const t of ['roller', 'turret', 'whirl', 'boom']) try { makePowerMesh(t).g.visible = false; } catch (e) {}")
    return s
