#!/usr/bin/env python3
"""The locker dressed for the season: two jack-o-lanterns and three candles on the floor by the back wall, a bat on the wall, and a sign up on it reading Season One: Halloween. Shown while the locker is open. On top of ui56_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui56_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

rep("const strand = new THREE.Group();\n", r'''const strand = new THREE.Group();
// ---------- the locker's set dressing for the season: jack-o-lanterns and candles along the back wall, a bat, and the sign ----------
const lobbyProps = new THREE.Group(); lobbyProps.visible = false; scene.add(lobbyProps);
const SIGN_TEX = (() => {
  const c = document.createElement('canvas'); c.width = 640; c.height = 280; const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  const draw = () => { const g = c.getContext('2d'); g.clearRect(0, 0, 640, 280);
    g.fillStyle = '#2A1538'; g.beginPath(); g.roundRect(0, 0, 640, 280, 26); g.fill();
    g.fillStyle = '#FF8A1F'; g.beginPath(); for (let i = 0; i <= 40; i++) { const a = i / 40 * 6.2832, r = 112 * (1 + 0.16 * Math.sin(a * 5 + 1) + 0.1 * Math.sin(a * 9)); const x = 500 + Math.cos(a) * r * 1.25, y = 150 + Math.sin(a) * r * 0.8; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.closePath(); g.fill();
    g.fillStyle = '#F4EEE3'; g.font = '800 34px Figtree, "Segoe UI", sans-serif'; g.textAlign = 'left'; g.textBaseline = 'alphabetic'; g.letterSpacing = '6px'; g.fillText('SEASON ONE', 40, 92);
    g.font = '400 118px "Bowlby One", "Arial Black", sans-serif'; g.letterSpacing = '0px'; g.lineJoin = 'round'; g.strokeStyle = '#171320'; g.lineWidth = 16; g.strokeText('HALLOWEEN', 34, 228); g.fillStyle = '#FF8A1F'; g.fillText('HALLOWEEN', 34, 228);
    g.strokeStyle = 'rgba(244,238,227,.25)'; g.lineWidth = 6; g.beginPath(); g.roundRect(12, 12, 616, 256, 18); g.stroke(); t.needsUpdate = true; };
  draw(); if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw); return t;
})();
{
  const outl = g => { const o = new THREE.Mesh(g, outlineMat); o.scale.setScalar(1.06); o.renderOrder = 31; return o; };
  const solid = (g, mat, x, y, z) => { const m = new THREE.Mesh(g, mat); m.position.set(x, y, z); m.castShadow = true; m.renderOrder = 32; if (!HI) m.add(outl(g)); lobbyProps.add(m); return m; };
  // a pumpkin: a squashed sphere with ribs pressed into it, a stem, a face cut out of the front
  const pumpG = (() => { const g = new THREE.SphereGeometry(0.42, 28, 18), P = g.attributes.position; for (let i = 0; i < P.count; i++) { const x = P.getX(i), y = P.getY(i), z = P.getZ(i), a = Math.atan2(z, x), r = 1 + 0.07 * Math.cos(a * 8) - 0.08 * Math.pow(Math.abs(y) / 0.42, 4); P.setXYZ(i, x * r, y * 0.78 * r, z * r); } g.computeVertexNormals(); return g.translate(0, 0.33, 0); })();
  const faceG = (() => { const sh = []; const tri = (cx, cy, w, h, flip) => { const f = new THREE.Shape(); f.moveTo(cx - w, flip ? cy + h : cy - h); f.lineTo(cx + w, flip ? cy + h : cy - h); f.lineTo(cx, flip ? cy - h : cy + h); f.closePath(); sh.push(f); };
    tri(-0.13, 0.4, 0.075, 0.07); tri(0.13, 0.4, 0.075, 0.07); const m = new THREE.Shape(); m.moveTo(-0.2, 0.26); m.lineTo(-0.12, 0.19); m.lineTo(-0.05, 0.25); m.lineTo(0.03, 0.18); m.lineTo(0.11, 0.25); m.lineTo(0.2, 0.2); m.lineTo(0.14, 0.13); m.lineTo(0.0, 0.12); m.lineTo(-0.14, 0.14); m.closePath(); sh.push(m);
    return new THREE.ShapeGeometry(sh); })();
  const orange = toon(0xFF7A1A), stemM = toon(0x5E7A2E), glowM = new THREE.MeshBasicMaterial({ color: 0xFFD66B }), waxM = toon(0xF4EEE3), flameM = new THREE.MeshBasicMaterial({ color: 0xFFB13A }), batM = new THREE.MeshBasicMaterial({ color: 0x171320, side: THREE.DoubleSide });
  const pumpkin = (x, z, sc, yaw) => { const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(sc); g.rotation.y = yaw; const b = new THREE.Mesh(pumpG, orange); b.castShadow = true; b.renderOrder = 32; if (!HI) b.add(outl(pumpG)); g.add(b);
    const st = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.07, 0.17, 8), stemM); st.position.set(0.02, 0.68, 0); st.rotation.z = 0.25; g.add(st);
    const f = new THREE.Mesh(faceG, glowM); f.position.set(0, 0, 0.41); f.renderOrder = 33; g.add(f); const f2 = new THREE.Mesh(faceG, glowM); f2.position.set(0, 0, 0.405); f2.scale.setScalar(1.08); f2.material = new THREE.MeshBasicMaterial({ color: 0x171320 }); f2.renderOrder = 32.5; g.add(f2); lobbyProps.add(g); };
  pumpkin(-1.15, -1.45, 0.9, 0.3); pumpkin(1.05, -1.75, 0.66, -0.4);
  const candle = (x, z, h) => { const g = new THREE.CylinderGeometry(0.065, 0.075, h, 10).translate(0, h / 2, 0); solid(g, waxM, x, 0, z); const fl = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.11, 8).translate(0, h + 0.06, 0), flameM); fl.position.set(x, 0, z); fl.renderOrder = 33; lobbyProps.add(fl); lobbyProps.userData.flames = (lobbyProps.userData.flames || []).concat(fl); };
  candle(-0.7, -2.05, 0.46); candle(-0.5, -2.1, 0.3); candle(1.0, -2.1, 0.38);
  // the sign on the wall, and a bat up by it
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(2.3, 1.0), new THREE.MeshBasicMaterial({ map: SIGN_TEX, transparent: true })); sign.position.set(0, 1.42, -2.33); sign.scale.setScalar(0.6); sign.renderOrder = 32; lobbyProps.add(sign);
  const bat = (() => { const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.lineTo(0.14, 0.1); sh.lineTo(0.3, 0.06); sh.lineTo(0.42, 0.14); sh.lineTo(0.36, -0.02); sh.lineTo(0.3, -0.08); sh.lineTo(0.14, -0.04); sh.lineTo(0.04, -0.09); sh.lineTo(-0.04, -0.09); sh.lineTo(-0.14, -0.04); sh.lineTo(-0.3, -0.08); sh.lineTo(-0.36, -0.02); sh.lineTo(-0.42, 0.14); sh.lineTo(-0.3, 0.06); sh.lineTo(-0.14, 0.1); sh.closePath(); const m = new THREE.Mesh(new THREE.ShapeGeometry(sh), batM); m.position.set(-1.25, 2.15, -2.3); m.renderOrder = 32; lobbyProps.add(m); return m; })();
  lobbyProps.userData.bat = bat; lobbyProps.traverse(o => o.layers.enable(4)); // (the lobby draws layer 4 only)
}
// placed by the back wall, which stands 2.4 behind the blob as seen from the camera (the backdrop shader puts it there)
function lobbyPropsTick() {
  const on = lookOpen && state === 'menu'; lobbyProps.visible = on; if (!on) return;
  const n = lobbyU.uWallN.value; lobbyProps.position.set(P.x, 0, P.z); lobbyProps.rotation.y = Math.atan2(n.x, n.y);
  const fl = lobbyProps.userData.flames || []; for (let i = 0; i < fl.length; i++) { const f = fl[i], k = 0.85 + 0.25 * Math.sin(clock * 13 + i * 2.1) * Math.sin(clock * 7.3 + i); f.scale.set(1 + 0.15 * Math.sin(clock * 17 + i), k, 1); }
  const b = lobbyProps.userData.bat; if (b) { b.rotation.z = 0.12 * Math.sin(clock * 1.7); b.position.y = 2.15 + 0.04 * Math.sin(clock * 2.3); }
}
''')
rep("lobbyU.uWallN.value.set(nx / nl, nz / nl); lobbyU.uTime.value = clock;", "lobbyU.uWallN.value.set(nx / nl, nz / nl); lobbyU.uTime.value = clock; lobbyPropsTick();")

m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
