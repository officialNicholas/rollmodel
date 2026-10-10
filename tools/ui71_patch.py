#!/usr/bin/env python3
"""The locker's jack-o-lanterns get a skin and a glow: a painted pumpkin texture lined up with the ribs (lighter ridges, dark creases, freckles, a green cast at the stem), the face lit from inside with a flickering glow and a warm pool of light on the floor, and a small glow on each candle flame. No real lights, so no shader recompiles. On top of ui70_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui70_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

rep("const orange = toon(0xFF7A1A), stemM = toon(0x5E7A2E), glowM = new THREE.MeshBasicMaterial({ color: 0xFFD66B })",
    r'''const PUMP_TEX = (() => { // the pumpkin's skin: eight ribs round (as the shape has), lighter on the ridges and dark in the creases, freckled, going green up by the stem
    const W = 512, Hh = 256, c = document.createElement('canvas'); c.width = W; c.height = Hh; const g = c.getContext('2d'), R = rng(4242), img = g.createImageData(W, Hh), d = img.data;
    for (let y = 0; y < Hh; y++) for (let x = 0; x < W; x++) { const u = x / W, v = y / Hh, rib = Math.cos(u * 6.2832 * 8), k = 0.74 + 0.26 * Math.max(-1, rib * 1.3), top = Math.max(0, 1 - v * 3.2), i = (y * W + x) * 4;
      d[i] = 255 * k * (1 - 0.25 * top); d[i + 1] = (118 + 36 * Math.max(0, rib)) * k * (1 + 0.5 * top); d[i + 2] = (20 + 12 * Math.max(0, rib)) * k; d[i + 3] = 255; }
    g.putImageData(img, 0, 0);
    for (let i = 0; i < 260; i++) { const x = R() * W, y = 20 + R() * (Hh - 30), r = 1 + R() * 3; g.fillStyle = R() < 0.6 ? 'rgba(150,60,10,' + (0.12 + R() * 0.2) + ')' : 'rgba(255,200,120,' + (0.1 + R() * 0.16) + ')'; g.beginPath(); g.ellipse(x, y, r, r * (1.4 + R()), 0, 0, 6.2832); g.fill(); }
    for (let i = 0; i < 70; i++) { const x = R() * W, y0 = 30 + R() * 120, len = 30 + R() * 90; g.strokeStyle = 'rgba(120,45,8,' + (0.06 + R() * 0.1) + ')'; g.lineWidth = 1 + R() * 2; g.beginPath(); g.moveTo(x, y0); g.lineTo(x + (R() - 0.5) * 6, y0 + len); g.stroke(); }
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.wrapS = THREE.RepeatWrapping; t.anisotropy = 4; return t; })();
  const glowSp = (col, sc, op) => { const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex, color: col, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending, fog: false })); sp.scale.setScalar(sc); sp.renderOrder = 34; sp.userData.op = op; return sp; };
  const pool = (col, sz, op) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(sz, sz).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ map: glowTex, color: col, transparent: true, opacity: op, depthWrite: false, blending: THREE.AdditiveBlending, fog: false })); m.position.y = 0.012; m.renderOrder = 30.5; m.userData.op = op; return m; };
  lobbyProps.userData.glows = [];
  const orange = toon(0xFFFFFF, { map: PUMP_TEX }, { roughness: 0.55 }), stemM = toon(0x5E7A2E), glowM = new THREE.MeshBasicMaterial({ color: 0xFFE9A0 })''')
rep("const f = new THREE.Mesh(faceG, glowM); f.position.set(0, 0, 0.41); f.renderOrder = 33; g.add(f);",
    "const f = new THREE.Mesh(faceG, glowM); f.position.set(0, 0, 0.41); f.renderOrder = 33; g.add(f); const fg = glowSp(0xFF9A2E, 0.85, 0.42); fg.position.set(0, 0.3, 0.5); g.add(fg); const fg2 = glowSp(0xFFD070, 0.38, 0.6); fg2.position.set(0, 0.3, 0.52); g.add(fg2); const pl = pool(0xFF8A20, 2.4, 0.38); g.add(pl); lobbyProps.userData.glows.push(fg, fg2, pl);")
rep("const fl = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.11, 8).translate(0, h + 0.06, 0), flameM); fl.position.set(x, 0, z); fl.renderOrder = 33; lobbyProps.add(fl);",
    "const fl = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.11, 8).translate(0, h + 0.06, 0), flameM); fl.position.set(x, 0, z); fl.renderOrder = 33; lobbyProps.add(fl); const cg = glowSp(0xFFB050, 0.42, 0.6); cg.position.set(x, h + 0.08, z); lobbyProps.add(cg); const cp = pool(0xFFA040, 1.1, 0.3); cp.position.set(x, 0.012, z); lobbyProps.add(cp); lobbyProps.userData.glows.push(cg, cp);")
rep("const b = lobbyProps.userData.bat; if (b) { b.rotation.z = 0.12 * Math.sin(clock * 1.7); b.position.y = 2.15 + 0.04 * Math.sin(clock * 2.3); }",
    "const b = lobbyProps.userData.bat; if (b) { b.rotation.z = 0.12 * Math.sin(clock * 1.7); b.position.y = 2.15 + 0.04 * Math.sin(clock * 2.3); }\n  const gl = lobbyProps.userData.glows || []; for (let i = 0; i < gl.length; i++) { const o = gl[i], k = 0.82 + 0.12 * Math.sin(clock * 9.1 + i * 1.7) * Math.sin(clock * 5.3 + i) + 0.06 * Math.sin(clock * 23 + i * 2.9); o.material.opacity = o.userData.op * k; } // (the candlelight breathes)")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
