#!/usr/bin/env python3
"""v226: the locker. Turned round, the axolotl turns smoothly (eased in and out, gliding on a little after a flick) and its body bends into
the turn, the tail sweeping out behind and swinging back past straight as it stops. A new color: it hops up, dives nose first into a pool of
the new paint that opens under it, and bursts back out of it in the new color with a spin, lands, and shakes the paint off."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/mk_axo_embed.py', S + '/tools/assets/axo_base_v225.js', S + '/tools/assets/axo_embed.js'], check=True)
subprocess.run(['python3', '-I', S + '/tools/ui153_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'M.spin !== undefined' in s and 'A.motion.spin = o.spinV' in s, 'runtime without the locker turn'

# ---- turning round in the locker: smooth for the axolotl (no stub shoves), a flick glides on
rep("function shimStep(S, dt) {\n  dt = Math.min(dt, 0.05);",
    "function shimStep(S, dt) {\n  dt = Math.min(dt, 0.05);\n"
    "  if (AXOC.S.ready) { const d = S.tgt - S.yaw; S.vel += (clamp(d * 4.5, -6, 6) - S.vel) * Math.min(1, dt * 10); S.yaw += S.vel * dt; S.push = S.shove = 0; return; } /* (the axolotl: eased in and out, its body does the rest) */\n ")
rep("canvas.addEventListener('pointermove', e => { if ((lookOpen || lobbyOn()) && lookDrag && lookDrag.id === e.pointerId) { shim.tgt += (e.clientX - lookDrag.x) * 0.012;",
    "canvas.addEventListener('pointermove', e => { if ((lookOpen || lobbyOn()) && lookDrag && lookDrag.id === e.pointerId) { { const now = performance.now(), dm = Math.max(4, now - (lookDrag.tm || now - 16)); lookDrag.v = (lookDrag.v || 0) * 0.5 + 0.5 * (e.clientX - lookDrag.x) / dm; lookDrag.tm = now; } shim.tgt += (e.clientX - lookDrag.x) * 0.012;")
rep("const endLookDrag = e => { if (lookDrag && lookDrag.id === e.pointerId) {",
    "const endLookDrag = e => { if (lookDrag && lookDrag.id === e.pointerId) { if (lookOpen && AXOC.S.ready && e.type === 'pointerup' && performance.now() - (lookDrag.tm || 0) < 90) shim.tgt += clamp((lookDrag.v || 0) * 0.012 * 160, -2.6, 2.6); /* (let go mid-swipe: it glides on round) */")
rep("o.dt = dt; o.spd = U.gSpd.value;", "o.dt = dt; o.spinV = D === P && P.shimNow === shim ? shim.vel : undefined; o.spd = U.gSpd.value;")

# ---- the paint dip
rep("function endIntro() {", r"""// the locker's paint dip: a new color, and it hops up, dives nose first into a pool of the new paint opening under it, and bursts back out in
// the new color (a spin on the way up), lands and shakes the paint off. Its old color holds until it's under; the pool closes after it
let lkDip = null, dipSide = 1;
const DIP = { crouch: 0.12, apex: 0.3, dive: 0.43, swap: 0.76, out: 0.94, top: 1.17, land: 1.38, end: 1.85 };
const dipPool = (() => {
  const U = { uCol: { value: new THREE.Color() }, uT: { value: 0 }, uRip: { value: 0 }, uHole: { value: 0 } };
  const m = new THREE.Mesh(new THREE.CircleGeometry(1, 64).rotateX(-Math.PI / 2), new THREE.ShaderMaterial({ uniforms: U, transparent: true, depthWrite: false,
    vertexShader: 'varying vec2 vP; void main(){ vP = position.xz; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: `uniform vec3 uCol; uniform float uT, uRip, uHole; varying vec2 vP;
void main(){
  float r = length(vP), a = atan(vP.y, vP.x);
  float edge = 0.9 + 0.045 * sin(a * 5.0 + uT * 2.3) + 0.03 * sin(a * 11.0 - uT * 3.1);
  float m = 1.0 - smoothstep(edge - 0.035, edge, r); if (m < 0.004) discard;
  float fall = smoothstep(edge, 0.1, r) * smoothstep(0.0, 0.12, r), w = sin(r * 26.0 - uT * 14.0) * uRip * fall;
  vec3 c = uCol * (0.74 + 0.26 * smoothstep(edge, edge - 0.22, r)) * (1.0 - 0.22 * max(-w, 0.0));
  float hl = smoothstep(0.3, 0.0, length((vP - vec2(-0.34, -0.3)) * vec2(1.0, 1.7)));
  c *= 1.0 - 0.4 * uHole * smoothstep(0.34, 0.0, r);
  c = mix(c, vec3(1.0), clamp(hl * 0.42 + max(w, 0.0) * 0.45, 0.0, 0.8));
  c = mix(c, uCol * 0.45, smoothstep(edge - 0.07, edge - 0.01, r) * 0.55);
  gl_FragColor = vec4(c, m);
  #include <colorspace_fragment>
}` }));
  m.layers.set(4); m.renderOrder = 30; m.visible = false; m.userData.U = U; scene.add(m);
  // (the floor is drawn behind everything: under the pool, a floor of depth alone hides whatever has gone down into it)
  const k = new THREE.Mesh(new THREE.PlaneGeometry(40, 40).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ colorWrite: false })); k.layers.set(4); k.renderOrder = -5; k.visible = false; scene.add(k); m.userData.mask = k;
  return m; })();
const dipEase = u => { u = clamp(u, 0, 1); return u * u * (3 - 2 * u); };
// where it is at time t: up (or down into the paint) from where it stands, its nose down (+) or up (-), its spin, its squash
function dipPose(t) {
  const T = DIP;
  if (t < T.crouch) { const u = t / T.crouch; return { y: 0, pitch: -0.14 * dipEase(u), spin: 0, sq: 0.4 * Math.sin(u * Math.PI / 2), rise: 0 }; }
  if (t < T.swap) { const g = 0.46 / ((T.apex - T.crouch) * (T.apex - T.crouch)), y = Math.max(-2.4, 0.46 - g * (t - T.apex) * (t - T.apex));
    return { y, pitch: -0.14 + 1.66 * dipEase((t - T.crouch - 0.04) / (T.dive - T.crouch - 0.02)), spin: 0, sq: 0, rise: t < T.apex ? 0.5 : 0.25 }; }
  if (t < T.land) { const g = 0.42 / ((T.land - T.top) * (T.land - T.top)), y = Math.max(-2.4, 0.42 - g * (t - T.top) * (t - T.top));
    const p = t < T.out - 0.03 ? -1.52 : -1.52 * (1 - dipEase((t - T.out + 0.03) / (T.top - T.out + 0.03))) + 0.14 * Math.sin(Math.PI * clamp((t - T.top) / (T.land - T.top), 0, 1));
    return { y, pitch: p, spin: dipSide * 6.2832 * dipEase((t - T.out - 0.04) / 0.36), sq: 0, rise: t < T.top ? 0.55 : 0.2 }; }
  const k = t - T.land, osc = 0.55 * Math.exp(-k * 7) * Math.cos(k * 17);
  return { y: 0, pitch: 0, spin: 0, sq: Math.max(0, osc), rise: Math.max(0, -osc) * 0.8 };
}
function dipCrown(n, r, up, out, life) { for (let i = 0; i < n; i++) { const a = i / n * 6.2832 + Math.random() * 0.3, c = Math.cos(a), sn = Math.sin(a), sp = out * (0.7 + 0.6 * Math.random());
  spawnPart(P.x + c * r, 0.06, P.z + sn * r, c * sp, up * (0.75 + 0.5 * Math.random()), sn * sp, life, teamMats[0], 0.55 + 0.45 * Math.random()); } }
function dipStart(oldHex) {
  if (lkDip) { if (!lkDip.swapped) lkDip.nu = TEAMS[0].wet; return; }
  const I = VP && VP.slime, bb = I ? new THREE.Box3().setFromObject(I.root) : null, half = bb && !bb.isEmpty() ? Math.max(bb.max.x - bb.min.x, bb.max.z - bb.min.z) / 2 : 1.2;
  dipSide = -dipSide; lkDip = { t: 0, old: oldHex, oldC: new THREE.Color().setHex(oldHex), nu: TEAMS[0].wet, swapped: false, out: false, R: clamp(half * 0.78, 0.7, 1.6), rip: 0, pose: dipPose(0) };
  idle.act = null; idle.t = Math.max(idle.t, 3); menuReact = 0; AU.vox('hup', 0.8);
}
function dipEnd() { lkDip = null; dipPool.visible = dipPool.userData.mask.visible = false; }
function dipTick(dt) {
  const D = lkDip, pool = dipPool, U = pool.userData.U;
  if (!D) return;
  if (!lookOpen || state !== 'menu' || lookIntro) { dipEnd(); return; }
  const t0 = D.t; D.t += Math.min(dt, 0.05); const t = D.t, at = x => t0 < x && t >= x, I = VP && VP.slime;
  D.pose = dipPose(t);
  // the pool: opens under it as it crouches, ripples with each splash, closes after it's back out
  const open = t < DIP.land ? easeBack(Math.min(1, t / 0.26)) : 1 - dipEase((t - DIP.land - 0.08) / (DIP.end - DIP.land - 0.08));
  pool.visible = pool.userData.mask.visible = open > 0.01; pool.position.set(P.x, 0.006, P.z); pool.scale.setScalar(Math.max(0.01, open) * D.R); pool.userData.mask.position.set(P.x, 0, P.z);
  D.rip = Math.max(0, D.rip - dt * 1.4); U.uRip.value = D.rip; U.uT.value = t; U.uCol.value.setHex(D.nu); U.uHole.value = t > DIP.dive && t < DIP.out + 0.2 ? Math.min(1, (t - DIP.dive) * 6) * (1 - clamp((t - DIP.out) / 0.2, 0, 1)) : 0;
  if (!D.out) lobbyU.uSweep.value = 0; // (the floor keeps its old color until it's out)
  if (at(DIP.crouch)) AU.jump();
  if (at(DIP.dive)) { dipCrown(18, D.R * 0.3, 3.6, 1.8, 0.55); D.rip = 1; AU.splashWater(); AU.splat(0.8); emote(P, 'bonk', 0.5); }
  if (at(DIP.swap)) { D.swapped = true; D.nu = TEAMS[0].wet; if (I && I.coatOn) I.coatOn(); }
  if (at(DIP.out)) { D.out = true; dipCrown(26, D.R * 0.26, 5.2, 1.5, 0.7); D.rip = 1; AU.splashWater(); AU.splat(1); AU.vox('hyah', 0.85); lobbyU.uSweep.value = 0; emote(P, 'glee', 1.1); }
  if (at(DIP.land)) { AU.land(0.4); AU.plop(); D.rip = Math.max(D.rip, 0.5); if (I) { if (I.shake) I.shake(1); if (I.coatBurst) I.coatBurst(0.1); }
    for (let i = 0; i < 16; i++) { const a = i / 16 * 6.2832, c = Math.cos(a), sn = Math.sin(a); spawnPart(P.x + c * 0.3, 0.45, P.z + sn * 0.3, c * (2.4 + Math.random()), 1.4 + Math.random() * 1.6, sn * (2.4 + Math.random()), 0.5, teamMats[0], 0.6); } }
  if (t >= DIP.end) dipEnd();
}
function endIntro() {""")
rep("visuals(dt, rdt); flushTrail(); pbarTick(rdt); lockerTick();", "visuals(dt, rdt); flushTrail(); pbarTick(rdt); lockerTick(); dipTick(rdt);")
# its pose, its old color until it's under, no idle bits meanwhile, its shadow
rep("if (D === P && lookIntro) { const I = introPose(lookIntro.t);",
    "if (D === P && lkDip && lkDip.pose) { const q = lkDip.pose; hop = q.y; sq = q.sq; rise = q.rise; spinY = q.spin; }\n    if (D === P && lookIntro) { const I = introPose(lookIntro.t);")
rep("+ V.pullLean + (IPr ? IPr.pitch : 0)", "+ V.pullLean + (IPr ? IPr.pitch : 0) + (D === P && lkDip && lkDip.pose ? lkDip.pose.pitch : 0)")
rep("I.setPaint(coatCol.setHex(TEAMS[D.team].wet));", "I.setPaint(coatCol.setHex(D === P && lkDip && !lkDip.swapped ? lkDip.old : TEAMS[D.team].wet));")
rep("I.setColor(V.mat.color); const op = V.mat.opacity;", "I.setColor(D === P && lkDip && !lkDip.swapped ? lkDip.oldC : V.mat.color); const op = V.mat.opacity;")
rep("if (state === 'menu' && (lookOpen || menuPage === 'home') && !lookIntro && !vic && menuReact <= 0) {", "if (state === 'menu' && (lookOpen || menuPage === 'home') && !lookIntro && !vic && menuReact <= 0 && !lkDip) {")
rep("lobbyShadow.material.opacity = clamp(1 - P.y * 0.6, 0.3, 1);", "lobbyShadow.material.opacity = clamp(1 - P.y * 0.6, 0.3, 1); if (lkDip && lkDip.pose) { const y = lkDip.pose.y; lobbyShadow.material.opacity *= y < -0.05 ? 0 : clamp(1 - y * 0.7, 0.3, 1); }")
# the pick: in the locker (the axolotl, motion allowed) it dips instead of hopping, and its own splashes come with it
rep("""function pickColor(id) {
  const same = id === colorId; if (!same) { lobbyU.uCol2.value.setHex(TEAMS[0].wet); setColor(id); store.color = colorId; save(); kick($('logo'), 'paint'); if (lookOpen) lobbyU.uSweep.value = 0; }
  { const now = performance.now(); if (!(now - (pickColor.hopAt || -1e9) < 5000)) { menuReact = 0.7; pickColor.hopAt = now; } } AU.pop(); AU.splat(same ? 0.4 : 0.8);""",
    """function pickColor(id) {
  const same = id === colorId, dip = !same && lookOpen && state === 'menu' && !lookIntro && !reduceMotion && AXOC.S.ready && !!(VP && VP.slime), old = TEAMS[0].wet;
  if (!same) { if (!(lkDip && !lkDip.out)) lobbyU.uCol2.value.setHex(TEAMS[0].wet); setColor(id); store.color = colorId; save(); kick($('logo'), 'paint'); if (lookOpen) lobbyU.uSweep.value = 0; }
  if (!same && lookOpen) { const b = $('lc-paint'); if (b) b.innerHTML = '<small>Paint</small><span class="lci"><i class="dab" style="--c:' + TEAMS[0].css + '"></i></span><b>' + colorOf().name + '</b>'; }
  if (dip) { AU.pop(); dipStart(lkDip && !lkDip.swapped ? lkDip.old : old); return; }
  if (lkDip) { AU.pop(); return; }
  { const now = performance.now(); if (!(now - (pickColor.hopAt || -1e9) < 5000)) { menuReact = 0.7; pickColor.hopAt = now; } } AU.pop(); AU.splat(same ? 0.4 : 0.8);""")
rep('<p class="ver">Version 225</p>', '<p class="ver">Version 226</p>')
open(DST, 'w').write(s)
print('ui154 ok', n0, '->', len(s))
