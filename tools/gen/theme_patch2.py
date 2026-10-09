# Dressing the new stages: rock stacks with palms, rock outcrops, umbrellas, white abstract props, floor markings, splashes into the sea
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:100], c)
    s = s.replace(a, b)

# materials every theme can use
rep("""metal: toon(0xD6DAE2, null, { metalness: 0.7, roughness: 0.3 }), cream: toon(0xF2E8D2, null, { roughness: 0.55 }),""",
    """metal: toon(0xD6DAE2, null, { metalness: 0.7, roughness: 0.3 }), cream: toon(0xF2E8D2, null, { roughness: 0.55 }), rock: toon(0xC8A378, null, { roughness: 0.9 }), white: toon(0xF2F2F0, null, { roughness: 0.5 }), frond: toon(0x3F9A4C, { side: THREE.DoubleSide }, { roughness: 0.55 }), palm: toon(0xA07C56, null, { roughness: 0.85 }), nut: toon(0x6A4A2C, null, { roughness: 0.6 }),""")
# round pieces on the island are rock, sand on top
rep("""    const mats = circ ? [M.side, M.top, M.dark] : [M.side, M.side, M.top, M.dark, M.side, M.side];""",
    """    const mats = circ ? [T.id === 'island' && kind !== 'rotunda' && kind !== 'rpad' ? M.rock : M.side, M.top, M.dark] : [M.side, M.side, M.top, M.dark, M.side, M.side];""")
# dressing: a palm on each sea stack, boulders round each outcrop; white spheres on the blank world's pillars
rep("""      else if (T.id === 'garden' && kind === 'drum') {""", """      else if (T.id === 'island' && kind === 'column') { const Pm = palmParts(cx, top, cz, 2.4 + R() * 1.4, 1.25, 0.18 + R() * 0.25, R() * 6.28, R); Pm.trunk.forEach(g => put(M.palm, g)); Pm.fronds.forEach(g => put(M.frond, g)); Pm.nuts.forEach(g => put(M.nut, g)); for (let k = 0; k < 4; k++) { const a = R() * 6.28; put(M.rock, ball(0.25 + R() * 0.3, cx + Math.cos(a) * rad * 1.02, 0.1, cz + Math.sin(a) * rad * 1.02, 0.6)); } }
      else if (T.id === 'island' && kind === 'drum') { for (let k = 0; k < 5; k++) { const a = k / 5 * 6.28 + R(); put(M.rock, ball(0.22 + R() * 0.28, cx + Math.cos(a) * rad * 1.0, 0.12, cz + Math.sin(a) * rad * 1.0, 0.65)); } if (R() < 0.5) put(M.frond, frondGeo(new THREE.Vector3(cx, top + 0.02, cz), R() * 6.28, 0.9, 0.22, 0.6)); }
      else if (T.id === 'blank' && kind === 'column') { put(M.white, ball(rad * 0.82, cx, top + rad * 0.8, cz)); }
      else if (T.id === 'garden' && kind === 'drum') {""")
# props on the plinths around the canvas
rep("""    } else {
      if (corner) { put(M.bark, cyl(0.22, 0.3, 2.2, 10, x, y + 1.1, z)); put(M.leaf, ball(1.1, x, y + 2.7, z, 0.9)); put(M.leaf2, ball(0.75, x, y + 3.6, z, 0.9)); }""",
    """    } else if (T.id === 'island') {
      if (corner) { const Pm = palmParts(x, y, z, 3.4 + (i % 2) * 0.8, 1.35, 0.35, i * 1.7 + 0.6, R); Pm.trunk.forEach(g => put(M.palm, g)); Pm.fronds.forEach(g => put(M.frond, g)); Pm.nuts.forEach(g => put(M.nut, g)); }
      else { put(M.white, cyl(0.035, 0.035, 2.3, 8, x, y + 1.15, z)); for (let k = 0; k < 8; k++) put(k % 2 ? M.white : M.pal[i % M.pal.length], at(new THREE.ConeGeometry(1.15, 0.42, SEG(3), 1, true, k * Math.PI / 4, Math.PI / 4), x, y + 2.42, z)); put(M.white, at(new THREE.SphereGeometry(0.07, 10, 8), x, y + 2.66, z)); }
    } else if (T.id === 'blank') {
      if (corner) { put(M.white, cyl(0.42, 0.5, 1.0, 28, x, y + 0.5, z)); put(M.white, ball(0.8, x, y + 1.78, z)); }
      else if (i % 2) put(M.white, at(new THREE.ConeGeometry(0.7, 1.7, SEG(24)), x, y + 0.85, z)); else put(M.white, at(HI ? rbox(1.1, 1.1, 1.1, 0.14) : new THREE.BoxGeometry(1.1, 1.1, 1.1), x, y + 0.55, z));
    } else {
      if (corner) { put(M.bark, cyl(0.22, 0.3, 2.2, 10, x, y + 1.1, z)); put(M.leaf, ball(1.1, x, y + 2.7, z, 0.9)); put(M.leaf2, ball(0.75, x, y + 3.6, z, 0.9)); }""")
# the sea's shoreline knows the canvas size and where the plinths stand
rep("""  pond.visible = !!T.pond && HOLES.length > 0; pond.scale.set(ARENA, 1, ARENA);""", """  pond.visible = !!T.pond && HOLES.length > 0; pond.scale.set(ARENA, 1, ARENA);
  seaU.uA.value = ARENA; spots.forEach(([x, z], i) => seaU.uPl.value[i].set(x, z));""")

# floor markings
rep("""    else if (T.id === 'garden') { for (let k = 0; k < 28; k++) { const a = k / 28 * 6.2832, rr = 200 + (r() - 0.5) * 30, x = c + Math.cos(a)""",
    """    else if (T.id === 'island') { const star = (n, R0, R1, rot) => { g.beginPath(); for (let k = 0; k <= n * 2; k++) { const a = k / (n * 2) * 6.2832 + rot, rr = k % 2 ? R1 : R0; k ? g.lineTo(c + Math.cos(a) * rr, c + Math.sin(a) * rr) : g.moveTo(c + Math.cos(a) * rr, c + Math.sin(a) * rr); } g.closePath(); };
      g.strokeStyle = 'rgba(70,150,170,0.55)'; g.lineWidth = 6; g.beginPath(); g.arc(c, c, 228, 0, 6.2832); g.stroke(); g.lineWidth = 3; g.beginPath(); g.arc(c, c, 206, 0, 6.2832); g.stroke();
      g.fillStyle = 'rgba(240,120,90,0.55)'; star(4, 200, 46, -1.5708); g.fill(); g.fillStyle = 'rgba(60,170,180,0.5)'; star(4, 140, 36, -0.785); g.fill(); g.fillStyle = 'rgba(255,214,110,0.7)'; g.beginPath(); g.arc(c, c, 30, 0, 6.2832); g.fill(); }
    else if (T.id === 'blank') { g.strokeStyle = 'rgba(110,116,134,0.28)'; g.lineWidth = 3; for (const rr of [226, 150]) { g.beginPath(); g.arc(c, c, rr, 0, 6.2832); g.stroke(); } g.setLineDash([10, 12]); g.beginPath(); g.arc(c, c, 188, 0, 6.2832); g.stroke(); g.setLineDash([]); g.beginPath(); g.moveTo(c - 246, c); g.lineTo(c + 246, c); g.moveTo(c, c - 246); g.lineTo(c, c + 246); g.stroke(); for (let k = 0; k < 24; k++) { const a = k / 24 * 6.2832; g.beginPath(); g.moveTo(c + Math.cos(a) * 226, c + Math.sin(a) * 226); g.lineTo(c + Math.cos(a) * (k % 6 ? 214 : 200), c + Math.sin(a) * (k % 6 ? 214 : 200)); g.stroke(); } }
    else if (T.id === 'garden') { for (let k = 0; k < 28; k++) { const a = k / 28 * 6.2832, rr = 200 + (r() - 0.5) * 30, x = c + Math.cos(a)""")
rep("""    } else {
      // stepping stones, fallen leaves, a clump of flowers, a fairy ring of mushrooms""", """    } else if (id === 'island') {
      // a starfish, a scatter of shells, footprints wandering off, a striped beach towel
      cell(0, () => { g.fillStyle = 'rgba(70,40,20,0.25)'; star(5, 150, 58, -1.5708); g.save(); g.translate(6, 8); g.fill(); g.restore(); g.fillStyle = 'rgba(246,128,84,0.95)'; star(5, 150, 58, -1.5708); g.fill(); g.fillStyle = 'rgba(255,190,140,0.9)'; for (let k = 0; k < 40; k++) { const a = r() * 6.28, d = r() * 110; disc(Math.cos(a) * d, Math.sin(a) * d, 3 + r() * 3, 'rgba(255,214,170,0.9)'); } });
      cell(1, () => { for (let k = 0; k < 9; k++) { const x = (r() - 0.5) * 360, y = (r() - 0.5) * 360, s2 = 18 + r() * 22, rot = r() * 6.28; g.save(); g.translate(x, y); g.rotate(rot); g.fillStyle = ['rgba(255,236,226,0.95)', 'rgba(250,206,196,0.95)', 'rgba(236,226,206,0.95)'][k % 3]; g.beginPath(); g.moveTo(0, s2 * 0.4); for (let f = 0; f <= 8; f++) { const a = Math.PI + f / 8 * Math.PI; g.lineTo(Math.cos(a) * s2, Math.sin(a) * s2); } g.closePath(); g.fill(); g.strokeStyle = 'rgba(160,110,90,0.5)'; g.lineWidth = 2; for (let f = 1; f < 8; f++) { const a = Math.PI + f / 8 * Math.PI; g.beginPath(); g.moveTo(0, s2 * 0.3); g.lineTo(Math.cos(a) * s2 * 0.95, Math.sin(a) * s2 * 0.95); g.stroke(); } g.restore(); } });
      cell(2, () => { for (let k = 0; k < 7; k++) { const x = -180 + k * 58, y = 60 * Math.sin(k * 0.8) + (k % 2 ? 22 : -22); g.save(); g.translate(x, y); g.rotate(0.25 * Math.sin(k)); g.fillStyle = 'rgba(150,110,66,0.4)'; g.beginPath(); g.ellipse(0, 0, 14, 24, 0, 0, 6.2832); g.fill(); for (let t = 0; t < 5; t++) { g.beginPath(); g.arc(-10 + t * 5, -28 - (t === 0 ? 4 : 0), 4.5 - t * 0.4, 0, 6.2832); g.fill(); } g.restore(); } });
      cell(3, () => { g.save(); g.rotate(-0.3); const cols = ['rgba(255,94,120,0.95)', 'rgba(255,255,255,0.95)', 'rgba(60,180,200,0.95)', 'rgba(255,255,255,0.95)', 'rgba(255,200,70,0.95)']; for (let k = 0; k < 10; k++) { g.fillStyle = cols[k % cols.length]; g.fillRect(-120, -200 + k * 40, 240, 40); } g.fillStyle = 'rgba(0,0,0,0.1)'; g.fillRect(-120, -200, 8, 400); g.restore(); });
    } else if (id === 'blank') {
      // drafting marks in light pencil: a dimension line, a dashed circle, a cross, a little hatching
      const pen = (w) => { g.strokeStyle = 'rgba(112,118,136,0.42)'; g.lineWidth = w || 3; };
      cell(0, () => { pen(); g.beginPath(); g.moveTo(-190, 0); g.lineTo(190, 0); g.stroke(); for (const sx of [-1, 1]) { g.beginPath(); g.moveTo(sx * 190, -30); g.lineTo(sx * 190, 30); g.stroke(); g.beginPath(); g.moveTo(sx * 190, 0); g.lineTo(sx * 160, -12); g.moveTo(sx * 190, 0); g.lineTo(sx * 160, 12); g.stroke(); } });
      cell(1, () => { pen(); g.setLineDash([14, 12]); g.beginPath(); g.arc(0, 0, 170, 0, 6.2832); g.stroke(); g.setLineDash([]); g.beginPath(); g.arc(0, 0, 8, 0, 6.2832); g.stroke(); });
      cell(2, () => { pen(5); g.beginPath(); g.moveTo(-120, -120); g.lineTo(120, 120); g.moveTo(120, -120); g.lineTo(-120, 120); g.stroke(); });
      cell(3, () => { pen(2); for (let k = -10; k <= 10; k++) { g.beginPath(); g.moveTo(k * 18 - 90, -150); g.lineTo(k * 18 + 90, 150); g.stroke(); } g.globalCompositeOperation = 'destination-in'; g.beginPath(); g.arc(0, 0, 150, 0, 6.2832); g.fill(); g.globalCompositeOperation = 'source-over'; });
    } else {
      // stepping stones, fallen leaves, a clump of flowers, a fairy ring of mushrooms""")

# ---------- splashing into water: the sea, or the garden's pond ----------
rep("""for (let i = 0; i < 34; i++) { const m = new THREE.Mesh(rippleG, new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -12, polygonOffsetUnits: -12, fog: false })); m.rotation.x = -Math.PI / 2; m.visible = false; m.renderOrder = 4; scene.add(m); ripples.push({ m, t: 1 }); }""",
    """for (let i = 0; i < 34; i++) { const m = new THREE.Mesh(rippleG, new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -12, polygonOffsetUnits: -12, fog: false })); m.rotation.x = -Math.PI / 2; m.visible = false; m.renderOrder = 4; scene.add(m); ripples.push({ m, t: 1, big: 1, dur: 0.45 }); }
// something drops into the water: a white burst of droplets and rings spreading out
const waterDrop = colMat(0xEAF8FF);
function seaSplash(x, z, loud) {
  for (let i = 0; i < 26; i++) { const a = Math.random() * 6.283, sp = 1.5 + Math.random() * 3.5; spawnPart(x, WATER_Y + 0.1, z, Math.cos(a) * sp, 4 + Math.random() * 4, Math.sin(a) * sp, 0.6 + Math.random() * 0.4, waterDrop, 0.6 + Math.random() * 0.7); }
  for (let k = 0; k < 2; k++) { const rp = ripples.find(q => q.t >= 1); if (!rp) break; rp.t = -k * 0.25; rp.big = 5 + k * 3; rp.dur = 1.1; rp.m.position.set(x, WATER_Y + 0.04, z); rp.m.visible = false; }
  if (loud) AU.splashWater();
}""")
rep("""    if (y === -Infinity) continue; rp.t = 0; rp.m.position.set(x, y + 0.08, z); rp.m.visible = true;
  }
  for (const rp of ripples) if (rp.t < 1) { rp.t += dt / 0.45; const e = Math.min(1, rp.t); rp.m.scale.setScalar(0.05 + e * 0.34); rp.m.material.opacity = 0.7 * (1 - e); if (rp.t >= 1) rp.m.visible = false; }""",
    """    if (y === -Infinity) continue; rp.t = 0; rp.big = 1; rp.dur = 0.45; rp.m.position.set(x, y + 0.08, z); rp.m.visible = true;
  }
  for (const rp of ripples) if (rp.t < 1) { rp.t += dt / rp.dur; const e = clamp(rp.t, 0, 1); rp.m.visible = rp.t > 0; rp.m.scale.setScalar((0.05 + e * 0.34) * rp.big); rp.m.material.opacity = 0.7 * (1 - e); if (rp.t >= 1) rp.m.visible = false; }""")
rep("""  const gy = surfaceUnder(D.x, D.z, D.y + 0.3, true);
  // the puddle:""", """  const gy = surfaceUnder(D.x, D.z, D.y + 0.3, true);
  // dropping into water (off the island, or into the garden's pond) makes a splash
  if ((TH.sea || pond.visible) && V.lastY !== undefined && V.lastY >= WATER_Y && D.y < WATER_Y && D.st !== 'hide') seaSplash(D.x, D.z, D === P || hearable(D));
  V.lastY = D.y;
  // the puddle:""")
open(p,'w').write(s); print('theme patch 2 ok')
