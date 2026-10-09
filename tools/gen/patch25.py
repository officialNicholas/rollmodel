import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)

# ---- the orb: meshes and logic ----
rep("// ---------- paintbrush enemies:", r"""// ---------- the giant orb: a glowing, color-shifting orb that drifts around the canvas. Touch it any way you can to grow three times your size for 4 seconds ----------
const GIANT_T = 4, GIANT_K = 3, ORB_R = 0.42;
const ORB_VS = 'varying vec3 vN; varying vec3 vV; varying vec3 vP; void main(){ vP = position; vec4 mv = modelViewMatrix * vec4(position, 1.0); vN = normalize(normalMatrix * normal); vV = normalize(-mv.xyz); gl_Position = projectionMatrix * mv; }';
const ORB_FS = `uniform float uTime; varying vec3 vN; varying vec3 vV; varying vec3 vP;
vec3 hsv(float h, float s, float v){ vec3 p = abs(fract(vec3(h) + vec3(1.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0); return v * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), s); }
void main(){
  vec3 p = normalize(vP); float f = pow(1.0 - max(dot(vN, vV), 0.0), 1.5);
  float sw = 0.5 + 0.5 * sin(p.y * 7.0 + atan(p.z, p.x) * 3.0 - uTime * 4.0), sw2 = 0.5 + 0.5 * sin(p.x * 6.0 - p.z * 5.0 + uTime * 3.0);
  float h = fract(uTime * 0.2 + p.y * 0.18 + sw * 0.08);
  vec3 c = hsv(h, 0.7, 1.0);
  c = mix(c, vec3(1.0), sw * sw2 * 0.45 * (1.0 - f));
  c = mix(c, vec3(1.0), smoothstep(0.35, 0.0, f) * 0.5);
  c += hsv(fract(h + 0.33), 0.8, 1.0) * f * 0.8;
  gl_FragColor = vec4(c, 1.0);
}`;
const orbMat = new THREE.ShaderMaterial({ uniforms: { uTime: paintUniforms.uTime }, vertexShader: ORB_VS, fragmentShader: ORB_FS });
const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32); gr.addColorStop(0, 'rgba(255,255,255,1)'); gr.addColorStop(0.22, 'rgba(255,255,255,0.6)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = gr; g.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
const glowSprite = sz => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false })); sp.scale.setScalar(sz); sp.renderOrder = 9; return sp; };
const orbPartMats = [0xFF4D6D, 0xFFD23F, 0x4DFFB8, 0x4DA6FF, 0xC77DFF].map(c => new THREE.MeshBasicMaterial({ color: c }));
const orb = { on: false, k: 0, x: 0, y: 0, z: 0, base: 0, tx: 0, tz: 0, spawnT: 18, ph: 0, sparks: [], col: new THREE.Color() };
orb.g = new THREE.Group();
orb.core = new THREE.Mesh(new THREE.SphereGeometry(ORB_R, 32, 20), orbMat); orb.g.add(orb.core);
{ const hull = new THREE.Mesh(new THREE.SphereGeometry(ORB_R, 32, 20), new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide })); hull.scale.setScalar(1.1); orb.g.add(hull); }
orb.halo = glowSprite(2.4); orb.g.add(orb.halo);
for (let i = 0; i < 6; i++) { const sp = glowSprite(0.22); orb.g.add(sp); orb.sparks.push(sp); }
orb.ring = new THREE.Mesh(new THREE.RingGeometry(0.5, 0.66, 40), new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, polygonOffset: true, polygonOffsetFactor: -6, polygonOffsetUnits: -6, fog: false }));
orb.ring.rotation.x = -Math.PI / 2; orb.ring.renderOrder = 5;
orb.g.visible = false; orb.ring.visible = false; scene.add(orb.g); scene.add(orb.ring);
function orbReset() { orb.on = false; orb.k = 0; orb.spawnT = 16 + Math.random() * 6; orb.g.visible = false; orb.ring.visible = false; }
// drift toward another reachable spot a few units away, with nothing tall in the way
function orbPickTarget() {
  let best = null;
  for (let tries = 0; tries < 24 && !best; tries++) {
    const c = COF_SPOTS[(Math.random() * COF_SPOTS.length) | 0]; if (!c) break;
    const d = Math.hypot(c[0] - orb.x, c[2] - orb.z); if (d < 3 || d > 11 || Math.max(Math.abs(c[0]), Math.abs(c[2])) > ARENA - 3) continue;
    let ok = true; for (let t = 0.1; t <= 1.001 && ok; t += 0.1) { const x = orb.x + (c[0] - orb.x) * t, z = orb.z + (c[2] - orb.z) * t; if (blockedAt(x, z, Math.max(orb.base, c[1]) + 0.9)) ok = false; }
    if (ok) best = c;
  }
  if (best) { orb.tx = best[0]; orb.tz = best[2]; } else { orb.tx = orb.x; orb.tz = orb.z; }
}
function orbSpawn() {
  let c = null;
  for (let tries = 0; tries < 40 && !c; tries++) { const q = COF_SPOTS[(Math.random() * COF_SPOTS.length) | 0]; if (q && Math.max(Math.abs(q[0]), Math.abs(q[2])) < ARENA - 4 && [P, H].every(D => D.st === 'ko' || Math.hypot(D.x - q[0], D.z - q[2]) > 7)) c = q; }
  if (!c) { orb.spawnT = 2; return; }
  orb.on = true; orb.k = 0; orb.x = c[0]; orb.z = c[2]; orb.base = c[1]; orb.y = c[1] + 1.15; orb.ph = Math.random() * 6.28; orbPickTarget();
  orb.g.visible = true; orb.ring.visible = true; AU.orb();
  for (let i = 0; i < 16; i++) { const a = i / 16 * 6.283; spawnPart(orb.x, orb.y, orb.z, Math.cos(a) * 2.5, (Math.random() - 0.3) * 3, Math.sin(a) * 2.5, 0.5, orbPartMats[i % orbPartMats.length], 0.5); }
  hint('orb', 'Jump or fling into the glowing orb to go giant', 3.2);
}
function updateOrb(dt) {
  if (!orb.on) { orb.spawnT -= dt; if (orb.spawnT <= 0 && matchLeft > 8) orbSpawn(); return; }
  orb.k = Math.min(1, orb.k + dt * 1.8);
  const dx = orb.tx - orb.x, dz = orb.tz - orb.z, d = Math.hypot(dx, dz);
  if (d < 0.4) orbPickTarget(); else { const sp = Math.min(d, 1.3 * dt); orb.x += dx / d * sp; orb.z += dz / d * sp; }
  const g = surfaceUnder(orb.x, orb.z, orb.base + 2.2, true); if (g > -Infinity) orb.base += (g - orb.base) * Math.min(1, dt * 4);
  orb.y = orb.base + 1.15 + Math.sin(runT * 2.2 + orb.ph) * 0.12;
  if (orb.k < 0.5) return;
  // roll, jump, fling, anything: touch it and it's yours
  for (const D of [P, H]) { if (D.st !== 'play' || D.giantT > 0) continue; if (Math.hypot(D.x - orb.x, D.y + 0.3 - orb.y, D.z - orb.z) < PR + ORB_R + 0.12) { takeOrb(D); return; } }
}
// a pound or a coffin burst that goes off right under it takes it too
function orbPound(D, R) { if (orb.on && orb.k > 0.5 && D.giantT <= 0 && Math.hypot(orb.x - D.x, orb.z - D.z) < R * 0.6 && orb.y - D.y < 3 && orb.y - D.y > -0.5) takeOrb(D); }
function takeOrb(D) {
  orb.on = false; orb.g.visible = false; orb.ring.visible = false; orb.spawnT = 16 + Math.random() * 6;
  for (let i = 0; i < 26; i++) { const a = Math.random() * 6.283; spawnPart(orb.x, orb.y, orb.z, Math.cos(a) * 4, 1 + Math.random() * 4, Math.sin(a) * 4, 0.55, orbPartMats[i % orbPartMats.length], 0.6); }
  shockwave(orb.x, D.y, orb.z, 2.6, 0xFFFFFF);
  D.giantT = GIANT_T; D.wob = 1; D.squash = 0.8; AU.grow();
  if (D === P) { shake = Math.max(shake, 0.3); buzz([20, 20, 40]); flashScreen(); banner('Giant!', 'Roll into the holy water to squish it.'); }
  else banner('The holy water went giant!', 'Keep away for 4 seconds.');
  for (const B of [P, H]) if (B.ai) B.ai.thinkT = 0;
}
// ---------- paintbrush enemies:""")
rep("function placeObjects(level) {\n", "function placeObjects(level) {\n  orbReset();\n")
rep("    power() { [523, 659, 784, 1047, 1319].forEach((f, i) => tone('triangle', f, 0, 0.14, 0.12, i * 0.055)); },",
    "    power() { [523, 659, 784, 1047, 1319].forEach((f, i) => tone('triangle', f, 0, 0.14, 0.12, i * 0.055)); },\n    orb() { [1319, 1568, 1976, 2637].forEach((f, i) => tone('sine', f, 0, 0.18, 0.06, i * 0.07)); },\n    grow() { tone('triangle', 196, 784, 0.55, 0.16); tone('sine', 392, 1568, 0.5, 0.08, 0.05); },\n    shrink() { tone('triangle', 660, 220, 0.4, 0.12); },")

# ---- the giant ----
rep("reason: null, spawnImm: false, dilT: 0,", "reason: null, spawnImm: false, dilT: 0, giantT: 0,")
rep("D.st = 'ko'; D.dilT = 0;", "D.st = 'ko'; D.dilT = 0; D.giantT = 0;")
rep("  if (D.st === 'ko') { D.koT -= dt; if (D.koT <= 0) respawnBlob(D); return; }\n",
    "  if (D.st === 'ko') { D.koT -= dt; if (D.koT <= 0) respawnBlob(D); return; }\n  if (D.giantT > 0) { D.giantT -= dt; if (D === P && !D.air && D.spd > 2 && Math.sin(runT * 9) > 0.95) shake = Math.max(shake, 0.06); if (D.giantT <= 0) { D.giantT = 0; D.wob = 1; if (hearable(D)) AU.shrink(); if (D === P) popText('Back to size'); } }\n")
rep("D.power && D.power.type === 'roller' ? 2.6 : 1, tcode(D), D.rb); } }", "D.giantT > 0 ? GIANT_K : D.power && D.power.type === 'roller' ? 2.6 : 1, tcode(D), D.rb); } }")
rep("Rr = SPLAT_R * (0.55 + 0.45 * cost / full) * flingSplatK(fk);", "Rr = SPLAT_R * (0.55 + 0.45 * cost / full) * flingSplatK(fk) * (D.giantT > 0 ? 1.7 : 1);")
rep("for (const p of pots) if (potUp(p) && !p.occ && p.ink > 0.02 && p.cool <= 0 && Math.abs(D.y - p.y) < 0.9", "if (D.giantT <= 0) for (const p of pots) if (potUp(p) && !p.occ && p.ink > 0.02 && p.cool <= 0 && Math.abs(D.y - p.y) < 0.9")
# giant squishes on contact and can't be flattened or shoved by a normal-sized blob
rep("""  const dx = H.x - P.x, dz = H.z - P.z, d = Math.hypot(dx, dz), dy = H.y - P.y;
  if (d > PR * 2 + 0.15 || Math.abs(dy) > 1.0) return;""",
"""  const dx = H.x - P.x, dz = H.z - P.z, d = Math.hypot(dx, dz), dy = H.y - P.y, gP = P.giantT > 0, gH = H.giantT > 0;
  if (gP !== gH) { const A = gP ? P : H, B = gP ? H : P; if (d < PR * GIANT_K + PR + 0.1 && Math.abs(dy) < 1.6 && B.flatT <= 0 && B.immuneT <= 0) flatten(B, A, 'giant'); return; }
  if (d > PR * 2 + 0.15 || Math.abs(dy) > 1.0) return;""")
rep("  if (B === P) { shake = Math.max(shake, 0.3); buzz([25, 30, 25]); banner('Flattened!', 'Stuck for 2 seconds'); }\n  else if (A === P) { buzz(15); banner(how === 'stomp' ? 'Stomped it!' : 'Flattened it!', 'Pound it now!'); }",
    "  if (B === P) { shake = Math.max(shake, 0.3); buzz([25, 30, 25]); banner(how === 'giant' ? 'Squished!' : 'Flattened!', 'Stuck for 2 seconds'); }\n  else if (A === P) { buzz(15); banner(how === 'stomp' ? 'Stomped it!' : how === 'giant' ? 'Squished it!' : 'Flattened it!', 'Pound it now!'); }")
rep("  const B = other(A); if (B.st !== 'play' || B.immuneT > 0 || B.slam || B.flatT > 0) return;", "  const B = other(A); if (B.st !== 'play' || B.immuneT > 0 || B.slam || B.flatT > 0 || B.giantT > 0) return;")
# pounds and bursts take the orb
rep("  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < koR && Math.abs(O.y - D.y) < 1.4) knockOut(O, O.st === 'hide' ? 'coffin' : 'pound', D);\n}",
    "  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < koR && Math.abs(O.y - D.y) < 1.4) knockOut(O, O.st === 'hide' ? 'coffin' : 'pound', D);\n  orbPound(D, R);\n}")
rep("  breakCoffin(p, D);\n  const O = other(D);", "  breakCoffin(p, D); orbPound(D, SLAM_R);\n  const O = other(D);")
rep("    blobContact();\n", "    blobContact(); updateOrb(dt);\n")

# ---- visuals: the blob grows, the camera pulls back, the orb glows and cycles colors ----
rep("const VP = { root: drop, body, mat: dropMat, U: gooU, look, shadow: shadowBlob, flatK: 0 }, VC = { root: cDrop, body: cBody, mat: cMat, U: gooU2, look: lookC, shadow: cShadow, flatK: 0 };",
    "const VP = { root: drop, body, mat: dropMat, U: gooU, look, shadow: shadowBlob, flatK: 0, gk: 1 }, VC = { root: cDrop, body: cBody, mat: cMat, U: gooU2, look: lookC, shadow: cShadow, flatK: 0, gk: 1 };")
rep("  const rad = PR * (0.8 + 0.2 * D.paint) * (hidden ? 0.7 : 1), falling = D.air && D.vy < 0, rising = D.air && D.vy > 0;",
    "  const gt = D.giantT > 0 ? (D.giantT < 0.9 && Math.sin(clock * 40) > 0 ? GIANT_K * 0.75 : GIANT_K) : 1; V.gk += (gt - V.gk) * Math.min(1, dt * (gt > V.gk ? 7 : 9));\n  const rad = PR * (0.8 + 0.2 * D.paint) * (hidden ? 0.7 : 1) * V.gk, falling = D.air && D.vy < 0, rising = D.air && D.vy > 0;")
rep("V.shadow.scale.setScalar((0.8 + 0.2 * D.paint) * (1 + 0.5 * fk) / (1 + (D.y - gy) * 0.6));", "V.shadow.scale.setScalar((0.8 + 0.2 * D.paint) * (1 + 0.5 * fk) * V.gk / (1 + (D.y - gy) * 0.6));")
rep("cHalo.position.set(0, PR * 2.05 * (1 - 0.6 * VC.flatK)", "cHalo.position.set(0, PR * 2.05 * VC.gk * (1 - 0.6 * VC.flatK)")
rep("h = 7.0 + camCharge * 3 + look.roll * 1.2 + (P.slam ? P.y * 0.6 : 0) + ko * 4, back = 6.0 + camCharge * 1.5 + ko * 3;",
    "h = 7.0 + camCharge * 3 + look.roll * 1.2 + (P.slam ? P.y * 0.6 : 0) + ko * 4 + (VP.gk - 1) * 2.4, back = 6.0 + camCharge * 1.5 + ko * 3 + (VP.gk - 1) * 1.8;")
rep("  const pwc = $('pw');\n  if (P.power && pIn) {",
    "  const pwc = $('pw');\n  if (P.giantT > 0 && pIn) { pwc.hidden = false; const tx = 'Giant ' + Math.ceil(P.giantT) + 's'; if ($('pwText').textContent !== tx) $('pwText').textContent = tx; $('pwRing').style.background = 'conic-gradient(#fff ' + (P.giantT / GIANT_T * 360).toFixed(0) + 'deg, rgba(255,255,255,.3) 0)'; }\n  else if (P.power && pIn) {")
rep("  // rain puddles: a soft rim, and steam curling up while one dries",
    """  // the orb: bobbing, spinning, glowing in whatever color it's cycling through, with sparkles circling it and a ring on the ground below
  if (orb.g.visible) {
    const sc = 1 - Math.pow(1 - orb.k, 3); orb.g.position.set(orb.x, orb.y, orb.z); orb.g.scale.setScalar(Math.max(0.01, sc)); orb.core.rotation.y = clock * 1.4; orb.core.rotation.x = Math.sin(clock * 0.7) * 0.4;
    orb.col.setHSL((clock * 0.2) % 1, 0.9, 0.62); orb.halo.material.color.copy(orb.col); orb.halo.scale.setScalar(2.2 + Math.sin(clock * 5) * 0.25); orb.halo.material.opacity = 0.75 + 0.2 * Math.sin(clock * 7);
    orb.sparks.forEach((sp, i) => { const a = clock * 2.2 + i / orb.sparks.length * 6.283, r = 0.72 + 0.08 * Math.sin(clock * 3 + i); sp.position.set(Math.cos(a) * r, Math.sin(a * 1.5 + i) * 0.35, Math.sin(a) * r); sp.material.color.setHSL(((clock * 0.2) + i / 6) % 1, 0.9, 0.7); });
    const gy = surfaceUnder(orb.x, orb.z, orb.y, true); orb.ring.visible = gy > -Infinity; if (gy > -Infinity) { orb.ring.position.set(orb.x, gy + 0.06, orb.z); orb.ring.material.color.copy(orb.col); orb.ring.material.opacity = 0.55 + 0.25 * Math.sin(clock * 6); orb.ring.scale.setScalar(sc * (1 + 0.1 * Math.sin(clock * 4))); }
  }
  // rain puddles: a soft rim, and steam curling up while one dries""")
rep("  const hide = [drop, shadowBlob, cDrop, cShadow,", "  const hide = [orb.g, orb.ring, drop, shadowBlob, cDrop, cShadow,")

# ---- CPU: goes for the orb, squishes you while giant, keeps clear of you while you're giant ----
rep("  for (const p of pots) if (potUp(p) && p.ink > 0.02 && !p.occ) NAV.near(p.x, p.z, p.y, 1.15, n => { nMult[n.id] += 3; });",
    "  for (const p of pots) if (potUp(p) && p.ink > 0.02 && !p.occ) NAV.near(p.x, p.z, p.y, 1.15, n => { nMult[n.id] += 3; });\n  if (O.giantT > 0.2 && oKnown && D.giantT <= 0) NAV.near(o.x, o.z, o.y, PR * GIANT_K + 3, n => { nMult[n.id] += 6; });")
rep("  // 4) go after you: flattened, stuck, or simply close while the pound is ready\n",
    """  // the giant orb is worth a detour, and once giant it comes to squish you
  if (orb.on && orb.k > 0.5 && D.giantT <= 0 && AI.orb > 0 && !sunNow) { const n = NAV.at(orb.x, orb.z, orb.base); if (n && nDist[n.id] < 22 && (ai.mode === 'orb' || Math.random() < AI.orb)) { aiGo(D, n, 'orb'); return; } }
  if (D.giantT > 0.6 && oKnown && o.imm <= 0.3 && o.st === 'play') { const pn = NAV.at(o.x + Math.sin(o.yaw) * o.spd * 0.4, o.z + Math.cos(o.yaw) * o.spd * 0.4, o.y) || NAV.at(o.x, o.z, o.y); if (pn && nDist[pn.id] < D.giantT * speed) { aiGo(D, pn, 'hunt'); return; } }
  // 4) go after you: flattened, stuck, or simply close while the pound is ready
""")
rep("  if (aiEvade(D, dt)) return;\n  if (aiTryPound(D, dt)) return;",
    "  if (aiEvade(D, dt)) return;\n  if (ai.mode === 'orb') { if (!orb.on) { ai.mode = 'paint'; ai.thinkT = 0; } else { ai.thinkT = Math.min(ai.thinkT, 0.25); if (Math.hypot(orb.x - D.x, orb.z - D.z) < 1.25 && orb.y - D.y < 1.9 && !D.charging) jump(D); } }\n  if (aiTryPound(D, dt)) return;")
rep("memory: 1.5, model: 0, airSling: 0.15, attack: 0.08,", "memory: 1.5, model: 0, airSling: 0.15, attack: 0.08, orb: 0.3,")
rep("memory: 3,   model: 0.3, airSling: 0.5, attack: 0.3,", "memory: 3,   model: 0.3, airSling: 0.5, attack: 0.3, orb: 0.6,")
rep("memory: 6,   model: 1, airSling: 0.95, attack: 0.55,", "memory: 6,   model: 1, airSling: 0.95, attack: 0.55, orb: 1,")

# ---- how to play ----
rep("""        <li><span class="dot sun"></span>Hard paint won't kill you,""",
    """        <li><span class="dot ink"></span>Now and then a glowing orb drifts around the canvas. Touch it any way you can, by jumping, flinging or pounding, to grow three times your size for 4 seconds. Roll into the holy water while you're giant to squish it flat.</li>
        <li><span class="dot sun"></span>Hard paint won't kill you,""")
open(F, 'w').write(s)
print('ok')
