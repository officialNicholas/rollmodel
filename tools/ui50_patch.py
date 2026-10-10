#!/usr/bin/env python3
"""The rocket as a paint backpack: a clear canister of the blob's own paint between two metal caps, straps, a gauge and a valve, with a nozzle underneath that fires paint downward to lift it. The jet is for show (it paints nothing) apart from the splat it leaves on blast-off. On top of ui49_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui49_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
def cut(a, b, new):
    global s
    i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j:]

cut("const ROCKET_G = (() => {", "function addRocket(V) {", r'''const ROCKET_G = (() => {
  const r = 0.25, seg = HI ? 28 : 16, SV = hexC(0xD9DEE6), SVD = hexC(0x8E95A3), SVL = hexC(0xF4F6FA), grey = hexC(0x4A4458), red = hexC(0xE3122F), c0 = -0.2;
  // the canister: two metal caps with a clear tank between them, straps either side, a gauge line down the front, a valve on top
  const capT = new THREE.CylinderGeometry(r * 1.14, r * 1.14, 0.1, seg).translate(0, 0.42 + c0, 0), capB = new THREE.CylinderGeometry(r * 1.14, r * 1.1, 0.12, seg).translate(0, -0.3 + c0, 0);
  const ringT = new THREE.TorusGeometry(r * 1.14, 0.022, 8, seg).rotateX(Math.PI / 2).translate(0, 0.36 + c0, 0), ringB = new THREE.TorusGeometry(r * 1.14, 0.022, 8, seg).rotateX(Math.PI / 2).translate(0, -0.23 + c0, 0);
  const strapL = new THREE.BoxGeometry(0.06, 0.78, 0.05).translate(-r * 1.08, 0.06 + c0, 0), strapR = new THREE.BoxGeometry(0.06, 0.78, 0.05).translate(r * 1.08, 0.06 + c0, 0);
  const valve = new THREE.TorusGeometry(0.075, 0.02, 8, 14).rotateX(Math.PI / 2).translate(0, 0.52 + c0, 0), stem = new THREE.CylinderGeometry(0.03, 0.03, 0.1, 8).translate(0, 0.49 + c0, 0);
  const pipe = new THREE.CylinderGeometry(0.03, 0.03, 0.3, 8).rotateZ(Math.PI / 2).translate(r * 0.9, 0.36 + c0, 0), gauge = new THREE.BoxGeometry(0.022, 0.4, 0.012).translate(0, 0.06 + c0, -r - 0.004);
  const noz = new THREE.CylinderGeometry(r * 0.5, r * 0.78, 0.18, seg).translate(0, -0.44 + c0, 0), nozIn = new THREE.CircleGeometry(r * 0.7, seg).rotateX(Math.PI / 2).translate(0, -0.525 + c0, 0);
  const solid = vcGeo([[capT, SV], [capB, SV], [ringT, SVD], [ringB, SVD], [strapL, grey], [strapR, grey], [valve, red], [stem, SVD], [pipe, SVD], [gauge, red], [noz, SVD], [nozIn, grey]]);
  const tank = new THREE.CylinderGeometry(r, r, 0.62, seg, 1, true).translate(0, 0.06 + c0, 0); // (clear)
  const ink = new THREE.CylinderGeometry(r * 0.9, r * 0.9, 0.6, seg).translate(0, 0.3, 0); // (its base at the bottom of the tank, so it can be scaled down as it is spent)
  // the jet: a cone of paint out of the nozzle, lighter in the middle; the colors are shades of white, tinted by the paint
  const fl = (rad, len, a, b) => { const g = new THREE.ConeGeometry(rad, len, 14, 4, true).rotateX(Math.PI).translate(0, -len / 2, 0), P = g.attributes.position, col = new Float32Array(P.count * 3), ca = new THREE.Color(a), cb = new THREE.Color(b); for (let i = 0; i < P.count; i++) { const t = clamp(-P.getY(i) / len, 0, 1), c = ca.clone().lerp(cb, t); col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b; } g.setAttribute('color', new THREE.BufferAttribute(col, 3)); return g; };
  return { solid, tank, ink, inkY: -0.24 + c0, outer: fl(0.21, 1.15, 0xFFFFFF, 0x6A6A6A), inner: fl(0.11, 0.75, 0xFFFFFF, 0xE0E0E0), nozY: -0.52 + c0 };
})();
const jetM = () => new THREE.MeshBasicMaterial({ vertexColors: true, color: 0xE3122F, transparent: true, opacity: 0.92, depthWrite: false, fog: false });
const rkTankM = HI ? charMat(new THREE.MeshPhysicalMaterial({ color: 0xF2F6FF, transparent: true, opacity: 0.22, roughness: 0.05, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 2.2, depthWrite: false, side: THREE.DoubleSide })) : new THREE.MeshToonMaterial({ color: 0xE4ECF8, gradientMap: grad, transparent: true, opacity: 0.2, depthWrite: false, side: THREE.DoubleSide });
''')
cut("function addRocket(V) {", "  V.body.add(g); V.rk = g;", r'''function addRocket(V) {
  const g = new THREE.Group(); g.visible = false; const m = new THREE.Mesh(ROCKET_G.solid, turMetalM); m.castShadow = true; m.renderOrder = 31; g.add(m);
  if (!HI) { const o = new THREE.Mesh(ROCKET_G.solid, new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true })); o.scale.setScalar(1.08); o.renderOrder = 30.5; g.add(o); }
  const ink = new THREE.Mesh(ROCKET_G.ink, toon(0xE3122F, { transparent: true })); ink.position.y = ROCKET_G.inkY; ink.renderOrder = 32; g.add(ink); g.userData.ink = ink;
  const tank = new THREE.Mesh(ROCKET_G.tank, rkTankM); tank.renderOrder = 44; g.add(tank);
  const fl = new THREE.Group(); fl.position.y = ROCKET_G.nozY; const a = new THREE.Mesh(ROCKET_G.outer, jetM()), b = new THREE.Mesh(ROCKET_G.inner, jetM()); b.material.opacity = 0.8; a.renderOrder = b.renderOrder = 36; fl.add(a); fl.add(b); g.add(fl); g.userData.flame = fl;
''')
# the pack holds the blob's own paint, and the jet is that paint; the tank drains as the hover goes on
rep("      const fl = V.rk.userData.flame, pw = !R ? 0 : R.ph === 'up' ? 1.6 : R.ph === 'dive' ? (R.slow ? 0.75 : 1.9) : 0.6; fl.visible = pw > 0.01;",
    "      const fl = V.rk.userData.flame, pw = !R ? 0 : R.ph === 'up' ? 1.6 : R.ph === 'dive' ? (R.slow ? 0.75 : 1.9) : 0.6; fl.visible = pw > 0.01;\n      { const col = TEAMS[D.team].wet; if (V.rkCol !== col) { V.rkCol = col; V.rk.userData.ink.material.color.setHex(col); for (const q of fl.children) q.material.color.setHex(col); } const lv = !R ? 1 : R.ph === 'up' ? 1 : R.ph === 'hover' ? 1 - 0.6 * clamp(R.t / ROCKET_HOVER, 0, 1) : 0.35; V.rkLv = (V.rkLv === undefined ? lv : V.rkLv) + (lv - (V.rkLv === undefined ? lv : V.rkLv)) * Math.min(1, dt * 6); V.rk.userData.ink.scale.y = Math.max(0.04, V.rkLv); }")
# the jet's spray: drops of its paint flung down out of the nozzle (they land on nothing), and a little steam
rep("    spawnPart(bx + Math.cos(a) * 0.08, by, bz + Math.sin(a) * 0.08, Math.cos(a) * s, dir * (5 + Math.random() * 5) + D.vy * 0.3, Math.sin(a) * s, 0.16 + Math.random() * 0.12, emberMat, 0.5 + Math.random() * 0.5, 0);",
    "    spawnPart(bx + Math.cos(a) * 0.08, by, bz + Math.sin(a) * 0.08, Math.cos(a) * s, dir * (5 + Math.random() * 5) + D.vy * 0.3, Math.sin(a) * s, 0.22 + Math.random() * 0.16, jetDropM(D), 0.55 + Math.random() * 0.6, 14);")
rep("    if (Math.random() < 0.45) spawnPart(bx + Math.cos(a) * 0.15, by + dir * 0.3, bz + Math.sin(a) * 0.15, Math.cos(a) * s * 0.6, dir * (1 + Math.random() * 2), Math.sin(a) * s * 0.6, 0.7 + Math.random() * 0.6, steamMat, 0.8 + Math.random() * 0.9, -0.08); }",
    "    if (Math.random() < 0.12) spawnPart(bx + Math.cos(a) * 0.15, by + dir * 0.3, bz + Math.sin(a) * 0.15, Math.cos(a) * s * 0.6, dir * (1 + Math.random() * 2), Math.sin(a) * s * 0.6, 0.5 + Math.random() * 0.4, steamMat, 0.3 + Math.random() * 0.3, -0.08); }")
rep("function rocketFx(D, dt) {", "const JET_DROP_M = {}; const jetDropM = D => JET_DROP_M[D.team] || (JET_DROP_M[D.team] = toon(TEAMS[D.team].wet));\nfunction rocketFx(D, dt) {")

# blast-off: the splat it leaves and a puff, not the old tower of steam
rep("  for (let i = 0; i < 26; i++) { const a = Math.random() * 6.283, s = 2 + Math.random() * 3.5; spawnPart(D.x + Math.cos(a) * 0.3, D.y + 0.15, D.z + Math.sin(a) * 0.3, Math.cos(a) * s, 0.4 + Math.random() * 1.2, Math.sin(a) * s, 0.7 + Math.random() * 0.5, steamMat, 1 + Math.random() * 0.8, -0.1); }",
    "  for (let i = 0; i < 16; i++) { const a = Math.random() * 6.283, s = 2.5 + Math.random() * 3.5; spawnPart(D.x + Math.cos(a) * 0.3, D.y + 0.15, D.z + Math.sin(a) * 0.3, Math.cos(a) * s, 0.2 + Math.random() * 0.6, Math.sin(a) * s, 0.45 + Math.random() * 0.35, jetDropM(D), 0.3 + Math.random() * 0.35, 10); }")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
