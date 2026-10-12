#!/usr/bin/env python3
"""v245 batch: the pounded rival ragdolls (about a second) before it pops; a slow-motion kill cam with its own camera angle on the first
pound knockout of a 1v1 match (the clock slows with it); the giant only crawls; the face decals flat and dark (not lit); the Strokes card
line shorter; the roller tip's roller kept alive until the rival is in sight; match 2: the slingshot and missile lesson when the pound
fills; match 3: the orb gives the giant (the CPU leaves it), Ol' Bloop on switching specials, then a slingshot reminder."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui183_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- the Strokes card: "And get even better" goes
rep("'And get even better. You’ve unlocked Strokes:", "'You’ve unlocked Strokes:")

# ---- the giant only crawls (never the swim)
rep("A.motion.dry = !!(D && D.dry && D.st === 'play');", "A.motion.dry = !!(D && (D.dry || D.giantT > 0) && D.st === 'play'); /* (the giant: crawling only too) */")

# ---- the face decals: flat and dark, not lit by the scene (the eye a little lit still, for its gloss and shade)
rep("""  reflectedLight.directDiffuse *= 1.0 - 0.45 * ink; reflectedLight.indirectDiffuse *= 1.0 - 0.45 * ink; reflectedLight.directSpecular *= 1.0 - 0.9 * ink; reflectedLight.indirectSpecular *= 1.0 - 0.9 * ink;
  totalEmissiveRadiance += diffuseColor.rgb * ink * 0.5;""",
"""  reflectedLight.directDiffuse *= 1.0 - ink; reflectedLight.indirectDiffuse *= 1.0 - ink; reflectedLight.directSpecular *= 1.0 - ink; reflectedLight.indirectSpecular *= 1.0 - ink;
#ifdef USE_CLEARCOAT
  clearcoatSpecularIndirect *= 1.0 - ink; clearcoatSpecularDirect *= 1.0 - ink;
#endif
  totalEmissiveRadiance += diffuseColor.rgb * ink * mix(0.3, 0.9, smoothstep(0.35, 0.65, dot(diffuseColor.rgb, vec3(0.2126, 0.7152, 0.0722))));   // (v245: flat and unlit; the dark ink (lines, mouth, brows) darker, the light bits (teeth) as they are)""")
rep("reflectedLight.directDiffuse *= 1.0 - 0.15 * eyeK; reflectedLight.indirectDiffuse *= 1.0 - 0.15 * eyeK; totalEmissiveRadiance += diffuseColor.rgb * eyeK * 0.42;",
    "{ float el = smoothstep(0.25, 0.6, dot(diffuseColor.rgb, vec3(0.2126, 0.7152, 0.0722))), ef = eyeK * smoothstep(0.2, 0.6, sDrawM), eu = ef * mix(1.0, 0.75, el); reflectedLight.directDiffuse *= 1.0 - eu; reflectedLight.indirectDiffuse *= 1.0 - eu; totalEmissiveRadiance += diffuseColor.rgb * ef * mix(0.3, 0.8, el); } /* (only where the eye is drawn: its soft mask reaches onto the cheeks) */   /* (v245: the eye flat: its dark parts (pupil, iris, a closed lid's line) unlit and dark, the white mostly unlit and bright in the shade; its gloss kept) */")

# ---- the roller tip: the roller holds while the rival is brought into sight
rep("if (!tut.rSeen) { if (!tut.rIn) tut.rIn = tutRivalIn(7); if (!have) { tut.rTip = false; }",
    "if (!tut.rSeen) { if (have) P.power.t = Math.max(P.power.t, 3); /* (the roller lasts till the tip has come) */ if (!tut.rIn) tut.rIn = tutRivalIn(7); if (!have) { tut.rTip = false; }")

# ---- the pounded rival: a ragdoll blast first, then it pops and is out
rep("function knockOut(D, reason, by) {", """// a pound knockout: the one pounded is blasted away limp, tumbling and bouncing, for about a second, and only then pops and is gone
const RAG_T = 1.15;
function koHide(D) { if (D === P) { drop.visible = false; shadowBlob.visible = false; } else { D.look.drop.visible = false; D.look.shadow.visible = false; } }
function ragStart(D, by) { let dx = D.x - by.x, dz = D.z - by.z, l = Math.hypot(dx, dz); if (l < 0.25) { dx = Math.sin(by.yaw); dz = Math.cos(by.yaw); l = 1; } dx /= l; dz /= l;
  const sp = 4.6 + Math.random() * 1.2; D.rag = { t: 0, vx: dx * sp, vz: dz * sp, wx: dx, wz: dz, vy: 7.4, a: 0, w: 10 + Math.random() * 3, side: Math.random() < 0.5 ? -1 : 1, puff: 0 }; D.air = true; D.wob = 1; }
function ragStep(D, dt) { const R = D.rag; R.t += dt; R.vy -= GRAV * 1.3 * dt;
  let nx = D.x + R.vx * dt, nz = D.z + R.vz * dt; if (blockedAt(nx, nz, D.y) || Math.abs(nx) > ARENA + 8 || Math.abs(nz) > ARENA + 8) { R.vx *= -0.35; R.vz *= -0.35; nx = D.x; nz = D.z; } D.x = nx; D.z = nz; D.y += R.vy * dt;
  const g = surfaceUnder(D.x, D.z, D.y + STEP, true); if (g > -Infinity && D.y <= g && R.vy < 0) { D.y = g; if (R.vy < -3) { R.vy *= -0.36; R.vx *= 0.55; R.vz *= 0.55; R.w *= 0.55; if (hearable(D)) AU.land(0.5); splash(D, 0.8); } else { R.vy = 0; R.vx *= 0.8; R.vz *= 0.8; R.w *= 0.85; } }
  R.a += R.w * dt; R.puff -= dt; if (R.puff <= 0 && R.t < 0.7) { R.puff = 0.05; spawnPart(D.x, D.y + 0.4, D.z, (Math.random() - 0.5) * 0.6, 0.3 + Math.random() * 0.5, (Math.random() - 0.5) * 0.6, 0.22, puHaloMat, 0.45); }
  if (R.t >= RAG_T || D.y < -8) ragEnd(D); }
function ragEnd(D) { if (!D.rag) return; D.rag = null; D.air = false; burst(D, deathColor(D, 'pound')); shockwave(D.x, D.y, D.z, 1.3, deathRing('pound')); if (hearable(D)) AU.pop(); koHide(D); if (kcam && kcam.V === D) kcam.endAt = kcam.t + 0.4; }
// ---- the kill cam: the first pound knockout you land in a 1v1 match, in slow motion from a low angle off to the side (the clock slows too)
let kcam = null, kcamUsed = false; const kcBarsEl = document.createElement('div'); kcBarsEl.className = 'kcbars'; kcBarsEl.setAttribute('aria-hidden', 'true');
function kcamStart(V) {
  if (kcamUsed || mode !== 'duel' || state !== 'play' || P.rocket) return; kcamUsed = true;
  const dx = V.x - P.x, dz = V.z - P.z, l = Math.hypot(dx, dz), fx = l > 0.3 ? dx / l : Math.sin(P.yaw), fz = l > 0.3 ? dz / l : Math.cos(P.yaw), mx = (P.x + V.x) / 2, mz = (P.z + V.z) / 2, gy = P.y;
  // the reverse angle: out past the rival, low and a little off the line, looking back at you, so the rival is blasted toward the lens
  // (a wall in the way: nearer in; no room at all: over your shoulder instead)
  let best = null; for (const side of [camSide(fx, fz), -camSide(fx, fz)]) { for (const dist of [7, 5.8, 4.6]) { const nx = fz * side, nz = -fx * side, cx = P.x + fx * dist + nx * 1.9, cz = P.z + fz * dist + nz * 1.9, cy = gy + 1.7;
      if (Math.abs(cx) > ARENA + 1 || Math.abs(cz) > ARENA + 1) continue; let ok = !blockedAt(cx, cz, cy - 0.5); for (let k = 1; k < 9 && ok; k++) { const t = k / 9; if (blockedAt(cx + (P.x - cx) * t, cz + (P.z - cz) * t, cy - 0.5 + (gy - cy + 0.5) * t)) ok = false; }
      if (ok) { best = { side, dist, rev: true }; break; } } if (best) break; }
  if (!best) best = { side: camSide(fx, fz), dist: -3.4, rev: false };
  kcam = { t: 0, x0: P.x, z0: P.z, gy, fx, fz, side: best.side, dist: best.dist, rev: best.rev, V, endAt: 1e9 };
  camSnap = true; if (!kcBarsEl.parentNode) stage.appendChild(kcBarsEl); kcBarsEl.classList.add('on'); $('hud').classList.add('kc'); AU.slow(true); AU.whoosh();
}
const camSide = (fx, fz) => { const cx = camPos.x - P.x, cz = camPos.z - P.z; return (fz * cx - fx * cz) >= 0 ? 1 : -1; }; // (the side the play camera is on: the cut stays on that side of the line)
const kcamK = t => t < 0.1 ? 0.1 : t < 0.9 ? 0.22 : t < 1.6 ? 0.22 + 0.63 * smoothstep(0.9, 1.6, t) : 0.85;
function kcamEnd() { if (!kcam) return; kcam = null; camSnap = true; kcBarsEl.classList.remove('on'); $('hud').classList.remove('kc'); AU.slow(false); }
function knockOut(D, reason, by) {""")
rep("""  const loud = hearable(D);
  if (reason === 'fall') { if (loud) AU.fall(); if (D === P) AU.vox('waah', 0.8); }
  else { burst(D, deathColor(D, reason)); shockwave(D.x, D.y, D.z, 1.6, deathRing(reason));""",
"""  const loud = hearable(D), rag = reason === 'pound' && !!by && state === 'play';
  if (reason === 'fall') { if (loud) AU.fall(); if (D === P) AU.vox('waah', 0.8); }
  else { if (rag) ragStart(D, by); else burst(D, deathColor(D, reason)); shockwave(D.x, D.y, D.z, 1.6, deathRing(reason));""")
rep("if (D === P) { drop.visible = false; shadowBlob.visible = false; AU.roll(0, 0); hold = 0.08;", "if (D === P) { if (!rag) koHide(D); AU.roll(0, 0); hold = 0.08;")
rep("D.look.drop.visible = false; D.look.shadow.visible = false; if (mode !== 'trio' || by === P) banner(", "if (!rag) koHide(D); if (rag && by === P) kcamStart(D); if (mode !== 'trio' || by === P) banner(")
rep("  if (D.st === 'ko') { D.koT -= dt; if (D.koT <= 0) respawnBlob(D); return; }", "  if (D.st === 'ko') { if (D.rag) ragStep(D, dt); D.koT -= dt; if (D.koT <= 0) { if (D.rag) ragEnd(D); respawnBlob(D); } return; }")
rep("for (const D of [P, H, H2]) { D.slamCD = D.slamMax = SLAM_FIRST;", "kcamEnd(); kcamUsed = false; for (const D of [P, H, H2]) { D.rag = null; D.slamCD = D.slamMax = SLAM_FIRST;")
# the ragdoll's tumble, drawn: head over heels along its flight, rocking a little to one side
rep("""  const L = V.look, U = V.U, hidden = D.st === 'hide';
  V.airT = D.air""", """  const L = V.look, U = V.U, hidden = D.st === 'hide'; if (D.rag && state !== 'play' && state !== 'paused') ragEnd(D); /* (the match ended mid-blast: it pops now) */
  V.airT = D.air""")
rep("""    tumQ.setFromAxisAngle(tumA.set(lz, 0, -lx), tumX); V.root.quaternion.multiply(tumQ); tumQ.setFromAxisAngle(tumA.set(lx, 0, lz), tumZ); V.root.quaternion.multiply(tumQ); }""",
"""    tumQ.setFromAxisAngle(tumA.set(lz, 0, -lx), tumX); V.root.quaternion.multiply(tumQ); tumQ.setFromAxisAngle(tumA.set(lx, 0, lz), tumZ); V.root.quaternion.multiply(tumQ); }
  if (D.rag) { const R = D.rag, c = Math.cos(V.yawDraw), s2 = Math.sin(V.yawDraw), lx = R.wx * c - R.wz * s2, lz = R.wx * s2 + R.wz * c;
    tumQ.setFromAxisAngle(tumA.set(lz, 0, -lx), R.a); V.root.quaternion.multiply(tumQ); tumQ.setFromAxisAngle(tumA.set(lx, 0, lz), R.side * 0.55 * Math.sin(R.a * 0.6)); V.root.quaternion.multiply(tumQ); }""")
# time: the kill cam slows the game (and so the clock) on its own curve; the lessons' slow-downs wait
rep("  if (tut && tut.slowK < 1 && state === 'play') dt *= tut.slowK; else if (tut2 && tut2.slowK < 1 && state === 'play') dt *= tut2.slowK;",
    "  if (kcam) { if (state !== 'play' && state !== 'paused') kcamEnd(); else if (state === 'play') { kcam.t += rdt; if (kcam.t >= Math.min(kcam.endAt, 3.4)) kcamEnd(); else if (dt > 0) dt = rdt * kcamK(kcam.t); } }\n  if (kcam) {} else if (tut && tut.slowK < 1 && state === 'play') dt *= tut.slowK; else if (tut2 && tut2.slowK < 1 && state === 'play') dt *= tut2.slowK;")
# the camera: low, off to the side of the pound, easing round and in a little, watching between you and the one blasted away
rep("  else if (state === 'dead' || state === 'paused') {\n    if (state === 'dead' && outro)",
"""  else if (state === 'play' && kcam) {
    const K = kcam, u = smoothstep(0, 2.6, K.t), nx = K.fz * K.side, nz = -K.fx * K.side, V = K.V, d = K.dist * (1 - 0.1 * u), sw = (K.rev ? 1.9 : 1.1) + 0.5 * u; // (a slow drift sideways and in)
    dPos.set(K.x0 + K.fx * d + nx * sw, K.gy + (K.rev ? 1.7 : 2.1) - 0.25 * u, K.z0 + K.fz * d + nz * sw);
    const ax = K.x0 + K.fx * (K.rev ? 1.6 : 3), az = K.z0 + K.fz * (K.rev ? 1.6 : 3), lk = V.rag ? 0.35 : 0.15; dLook.set(ax + (V.x - ax) * lk, K.gy + 0.65 + Math.max(0, V.y - K.gy) * 0.35, az + (V.z - az) * lk);
  }
  else if (state === 'dead' || state === 'paused') {
    if (state === 'dead' && outro)""")
rep(".tutslow{position:absolute;inset:0;z-index:7;", """.hud.kc{opacity:0}.kcbars{position:absolute;inset:0;z-index:7;pointer-events:none}.kcbars::before,.kcbars::after{content:'';position:absolute;left:0;right:0;height:0;background:#0d0a14;transition:height .28s cubic-bezier(.2,.8,.3,1)}.kcbars::before{top:0}.kcbars::after{bottom:0}.kcbars.on::before,.kcbars.on::after{height:9.5%}
.tutslow{position:absolute;inset:0;z-index:7;""")

# ---- match 2: once the pound is full, the slingshot (slowed right down till you fling), then the pound in the air for a missile, then
# (play on) Ol' Bloop in his corner: missiles take players out
rep("function tut2Begin() { tut2 = { ph: 'calm', sub: '', subT: 0, tipT: 0, hold: 0, slowK: 1, slowT: 0, shade: null, held: 0 };",
    "function tut2Begin() { tut2 = { ph: 'calm', sub: '', subT: 0, tipT: 0, hold: 0, slowK: 1, slowT: 0, shade: null, held: 0, ms: '', msT: 0, msN: 0 };")
rep("""  if (t.tipT > 0) { t.tipT -= dt; if (t.tipT <= 0) tutHide(); }
  if (t.ph === 'calm') { wxLeft = Math.max(wxLeft, 1); if (matchLeft <= MATCH_T * 0.5) {""",
"""  if (t.tipT > 0) { t.tipT -= dt; if (t.tipT <= 0) tutHide(); }
  if (tut2Missile(t, dt)) return;
  if (t.ph === 'calm') { wxLeft = Math.max(wxLeft, 1); if (matchLeft <= MATCH_T * 0.5 && !t.ms) {""")
rep("// the nearest shade from where you are, on your level and open enough to sit in: a ring at a time outwards\nfunction tutShadeSpot() {",
"""// match 2's missile lesson: true while it holds the floor (the weather's tips wait)
function tut2Missile(t, dt) {
  const real = dt / Math.max(t.slowK, 0.05);
  if (!t.ms) { if (t.ph === 'calm' && !t.sub && !tutTip && P.st === 'play' && !P.air && runT > 4 && slamReady(P)) { t.ms = 'sling'; t.msT = 0; tutShow(say('Don\\u2019t forget to *SLINGSHOT*!', 'Don\\u2019t forget to *SLINGSHOT*! Hold *S*, let go'), null, 'msling', true, true); } else return false; }
  if (t.ms === 'sling') { t.msT += real; t.slowK = t.msT < 8 ? 0.3 : 1; /* (slowed while you line it up; not forever) */
    if (P.st === 'play' && P.air && P.flung && (P.flingC || 0) > 0.15 && slamReady(P)) { t.ms = 'pound'; t.msT = 0; t.slowK = 0.3; tutShow(say('Now press *POUND* to fire a missile!', 'Now press *E* to fire a missile!'), 'slamBtn', 'mpound', true, true); }
    else if (t.msT > 14 || P.st !== 'play') { t.ms = 'done'; t.slowK = 1; tutHide(); }
    return true; }
  if (t.ms === 'pound') { t.msT += real; t.slowK = 0.3;
    if (P.missile && P.slam) { t.ms = 'elim'; t.msT = 0; t.slowK = 1; tutHide(); tutShow('Missiles eliminate players!', null, 'melim', false, true); }
    else if (!P.air || P.st !== 'play') { t.slowK = 1; tutHide(); if (++t.msN < 2 && P.st === 'play') { t.ms = 'again'; t.msT = 0; } else t.ms = 'done'; }
    return true; }
  if (t.ms === 'again') { t.msT += real; if (t.msT > 1.2 && slamReady(P) && !P.air && P.st === 'play') { t.ms = 'sling'; t.msT = 0; tutShow(say('Slingshot, then *POUND* in the air!', 'Slingshot, then press *E* in the air!'), null, 'msling2', true, true); } return t.msT < 6; }
  if (t.ms === 'elim') { t.msT += real; if (t.msT > 4.2) { t.ms = 'done'; tutHide(); } return t.msT <= 4.2; }
  return false;
}
// match 3 (the one after): the orb's for you (the CPU leaves it and it comes up near you), it makes you a giant; when that wears off
// Ol' Bloop says you can swap the giant and the rocket in Strokes; later on, a word on slingshotting
let tut3 = null;
function tut3Begin() { tut3 = { ph: 'orb', tipT: 0, remAt: 0, rem: false }; orb.spawnT = Math.min(orb.spawnT, 9); }
function tut3Step(dt) {
  const t = tut3; if (!t || state !== 'play') return;
  if (t.tipT > 0) { t.tipT -= dt; if (t.tipT <= 0) tutHide(); }
  if (t.ph === 'orb') { if (P.giantT > 0) t.ph = 'giant'; }
  else if (t.ph === 'giant') { if (P.giantT <= 0) { t.ph = 'said'; t.tipT = 4.5; t.remAt = runT + 16;
      tutShow(strokesDue() ? 'You can switch between Giant and Rocket any time in Strokes!' : 'Soon you\\u2019ll pick Giant or Rocket in Strokes!', null, 'm3swap', false, true); } }
  if (!t.rem && P.st === 'play' && !tutTip && matchLeft > 6 && (t.ph === 'said' ? runT > t.remAt : matchLeft < MATCH_T * 0.35)) { t.rem = true; t.tipT = 4.5; tutShow('Slingshotting is the fastest way around the canvas!', null, 'm3sling', false, true); }
}
const tut3Orb = () => !!tut3 && tut3.ph === 'orb'; // (the orb is being saved for you)
// the nearest shade from where you are, on your level and open enough to sit in: a ring at a time outwards
function tutShadeSpot() {""")
rep("const TUT_GEST = { move: 'steertap', sling: 'pull',", "const TUT_GEST = { msling: 'pull', msling2: 'pull', move: 'steertap', sling: 'pull',")
rep("if (tut) tutStep(dt); else if (tut2) tut2Step(dt);", "if (tut) tutStep(dt); else if (tut2) tut2Step(dt); else if (tut3) tut3Step(dt);")
rep("  tut2 = null; if (tutPh() === 'match2') tut2Begin();", "  tut2 = null; if (tutPh() === 'match2') tut2Begin();\n  tut3 = null; if (tutPh() === 'done' && store.tut.m3 === 1) tut3Begin();")
rep("  if (tutPh() === 'match2') { tut2 = null; tutHide(); delete store.tut.price; tutSet('done'); save(); }",
    "  if (tutPh() === 'match2') { tut2 = null; tutHide(); delete store.tut.price; store.tut.m3 = 1; tutSet('done'); save(); }\n  else if (tut3) { tut3 = null; tutHide(); store.tut.m3 = 2; save(); }")
rep("function tutLeave() { clearTimeout(tutPraiseEl._t0); tutPraiseEl._pend = false; tutPraiseEl.classList.remove('on'); tut2 = null;", "function tutLeave() { clearTimeout(tutPraiseEl._t0); tutPraiseEl._pend = false; tutPraiseEl.classList.remove('on'); tut2 = null; tut3 = null;")
rep("if (!(tut2 && state === 'play')) tutMenuTick(); }", "if (!((tut2 || tut3) && state === 'play')) tutMenuTick(); }")
rep("(tut2 && tut2.ph !== 'calm' && tut2.ph !== 'done') || matchLeft < 12) return;", "(tut2 && tut2.ph !== 'calm' && tut2.ph !== 'done') || tut3 || matchLeft < 12) return;")
rep("function hint(id, text, dur) { if (tut || (tut2 && tutTip) ||", "function hint(id, text, dur) { if (tut || ((tut2 || tut3) && tutTip) ||")
# the orb: yours in match 3 (giant), near you, and the CPU leaves it
rep("const gift = tut ? 'rocket' : window.__orbKind || (D === P ? strokeSpecial() :", "const gift = tut ? 'rocket' : D === P && tut3Orb() ? 'giant' : window.__orbKind || (D === P ? strokeSpecial() :")
rep("  if (tut2 && (P.st === 'play' || P.st === 'hide')) { let bd = 1e9; for (const q of COF_SPOTS)", "  if ((tut2 || tut3Orb()) && (P.st === 'play' || P.st === 'hide')) { let bd = 1e9; for (const q of COF_SPOTS)")
rep("for (const D of ACTIVE) { if (D.st !== 'play' || D.giantT > 0 || D.rocket || D.turret) continue; if (Math.hypot(D.x - orb.x, D.y + 0.3 - orb.y, D.z - orb.z) < PR + ORB_R + 0.12)",
    "for (const D of ACTIVE) { if (D.st !== 'play' || D.giantT > 0 || D.rocket || D.turret || (D !== P && tut3Orb())) continue; if (Math.hypot(D.x - orb.x, D.y + 0.3 - orb.y, D.z - orb.z) < PR + ORB_R + 0.12)")
rep("function orbPound(D, R) { if (orb.on && orb.k > 0.5 && D.giantT <= 0", "function orbPound(D, R) { if (orb.on && orb.k > 0.5 && D.giantT <= 0 && !(D !== P && tut3Orb())")
rep("if (orb.on && orb.k > 0.5 && D.giantT <= 0 && AI.orb > 0 && !sunNow) {", "if (orb.on && orb.k > 0.5 && D.giantT <= 0 && AI.orb > 0 && !sunNow && !tut3Orb()) {")
rep("if (ai.mode === 'orb') { if (!orb.on) {", "if (ai.mode === 'orb') { if (!orb.on || tut3Orb()) {")
# ---- the versus portrait: the camera rises to meet a face tipped up (the 'glee' pose throws the head back; a level camera looked up under
# the chin, the face crowding the top of the panel)
rep("const dist = ext / (o.fd * tv), a = Math.atan2(fw.x, fw.z) + (o.turn || 0), el = 0.06;",
    "const dist = ext / (o.fd * tv), a = Math.atan2(fw.x, fw.z) + (o.turn || 0), el = clamp(Math.asin(clamp(fw.y, -1, 1)) * 0.9, 0.06, 0.6);")
open(DST, 'w').write(s)
print('ui184 ok', n0, '->', len(s))
