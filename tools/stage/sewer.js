// ---------- the Sludge Sewer: a steel platform in a flooded chamber, glowing slime all round it pouring out of tunnel mouths in the brick walls,
// hazard paint, riveted containers with amber vents, manhole drums, a glowing drain, pipes and valves and caged lamps ----------
const SEWER_SIGNS = makeTex(512, (g, S) => {
  const c = S / 4; g.clearRect(0, 0, S, S); g.lineJoin = 'round'; g.textAlign = 'center'; g.textBaseline = 'middle';
  const tri = (x, y, s) => { g.beginPath(); g.moveTo(x, y - s); g.lineTo(x + s * 0.94, y + s * 0.68); g.lineTo(x - s * 0.94, y + s * 0.68); g.closePath(); };
  const trefoil = (x, y, s, col) => { g.fillStyle = col; for (let k = 0; k < 3; k++) { const a = k * 2.0944 - 1.5708; g.beginPath(); g.arc(x + Math.cos(a) * s * 0.42, y + Math.sin(a) * s * 0.42, s * 0.36, 0, 6.2832); g.fill(); } g.globalCompositeOperation = 'destination-out'; for (let k = 0; k < 3; k++) { const a = k * 2.0944 - 1.5708; g.beginPath(); g.arc(x + Math.cos(a) * s * 0.55, y + Math.sin(a) * s * 0.55, s * 0.22, 0, 6.2832); g.fill(); } g.beginPath(); g.arc(x, y, s * 0.12, 0, 6.2832); g.fill(); g.globalCompositeOperation = 'source-over'; g.strokeStyle = col; g.lineWidth = s * 0.08; g.beginPath(); g.arc(x, y, s * 0.3, 0, 6.2832); g.stroke(); g.beginPath(); g.arc(x, y, s * 0.08, 0, 6.2832); g.fill(); };
  const wear = (x0, y0, w, h) => { const r = rng(x0 * 7 + y0 + 3); for (let k = 0; k < 60; k++) { g.fillStyle = `rgba(${40 + r() * 40 | 0},${36 + r() * 30 | 0},${26 + r() * 20 | 0},${0.15 + r() * 0.35})`; g.beginPath(); g.arc(x0 + r() * w, y0 + r() * h, 1 + r() * 4, 0, 6.2832); g.fill(); } };
  // 0: the biohazard triangle
  g.save(); g.translate(0, 0); tri(c, c * 1.08, c * 0.86); g.fillStyle = '#1A1A18'; g.fill(); tri(c, c * 1.08, c * 0.72); g.fillStyle = '#F0B81E'; g.fill(); trefoil(c, c * 1.22, c * 0.42, '#1A1A18'); wear(0, 0, 2 * c, 2 * c); g.restore();
  // 1: NO SWIMMING (a swimmer crossed out)
  g.fillStyle = '#F2EFE6'; g.fillRect(2 * c + 14, 14, 2 * c - 28, 2 * c - 28); g.strokeStyle = '#1A1A18'; g.lineWidth = 6; g.strokeRect(2 * c + 20, 20, 2 * c - 40, 2 * c - 40);
  g.fillStyle = '#1A1A18'; g.font = 'bold 30px sans-serif'; g.fillText('NO', 3 * c, 50); g.fillText('SWIMMING', 3 * c, 2 * c - 46);
  g.fillStyle = '#3FA0D8'; for (let k = 0; k < 3; k++) { g.beginPath(); for (let x = 0; x <= 120; x += 6) { const y = c + 26 + k * 12 + Math.sin(x / 12) * 4; x ? g.lineTo(2 * c + 68 + x, y) : g.moveTo(2 * c + 68 + x, y); } g.lineWidth = 5; g.strokeStyle = '#3FA0D8'; g.stroke(); }
  g.fillStyle = '#1A1A18'; g.beginPath(); g.arc(3 * c - 30, c - 4, 13, 0, 6.2832); g.fill(); g.lineWidth = 9; g.strokeStyle = '#1A1A18'; g.beginPath(); g.moveTo(3 * c - 18, c + 6); g.lineTo(3 * c + 34, c + 14); g.stroke();
  g.strokeStyle = '#D62E26'; g.lineWidth = 14; g.beginPath(); g.arc(3 * c, c + 4, c * 0.58, 0, 6.2832); g.stroke(); g.beginPath(); g.moveTo(3 * c - c * 0.41, c + 4 - c * 0.41); g.lineTo(3 * c + c * 0.41, c + 4 + c * 0.41); g.stroke(); wear(2 * c, 0, 2 * c, 2 * c);
  // 2: DANGER (red oval on black over white)
  g.fillStyle = '#F2EFE6'; g.fillRect(14, 2 * c + 14, 2 * c - 28, 2 * c - 28); g.fillStyle = '#1A1A18'; g.fillRect(14, 2 * c + 14, 2 * c - 28, c * 0.8); g.fillStyle = '#D62E26'; g.beginPath(); g.ellipse(c, 2 * c + 14 + c * 0.4, c * 0.78, c * 0.3, 0, 0, 6.2832); g.fill();
  g.fillStyle = '#F2EFE6'; g.font = 'bold 40px sans-serif'; g.fillText('DANGER', c, 2 * c + 14 + c * 0.42); g.fillStyle = '#1A1A18'; g.font = 'bold 30px sans-serif'; g.fillText('TOXIC', c, 3 * c + 18); g.fillText('SLUDGE', c, 3 * c + 56); wear(0, 2 * c, 2 * c, 2 * c);
  // 3: a yellow and black skull plate
  g.fillStyle = '#F0B81E'; g.fillRect(2 * c + 14, 2 * c + 14, 2 * c - 28, 2 * c - 28); g.fillStyle = '#1A1A18'; g.beginPath(); g.arc(3 * c, 3 * c - 16, 50, 0, 6.2832); g.fill(); g.fillRect(3 * c - 30, 3 * c + 16, 60, 34);
  g.fillStyle = '#F0B81E'; g.beginPath(); g.arc(3 * c - 20, 3 * c - 16, 13, 0, 6.2832); g.arc(3 * c + 20, 3 * c - 16, 13, 0, 6.2832); g.fill(); g.beginPath(); g.moveTo(3 * c, 3 * c); g.lineTo(3 * c - 7, 3 * c + 12); g.lineTo(3 * c + 7, 3 * c + 12); g.fill(); for (let k = -2; k <= 2; k++) g.fillRect(3 * c + k * 11 - 2, 3 * c + 30, 4, 20);
  g.strokeStyle = '#1A1A18'; g.lineWidth = 16; g.lineCap = 'round'; for (const s of [-1, 1]) { g.beginPath(); g.moveTo(3 * c - 80, 3 * c + 60 * s + 10); g.lineTo(3 * c + 80, 3 * c - 60 * s + 10); g.stroke(); } wear(2 * c, 2 * c, 2 * c, 2 * c);
});
// slime puddles for the floor, four shapes (a 2 x 2 atlas), set down one by one so they never line up in a grid
const SEWER_PUDDLES = makeTex(512, (g, S) => {
  const R = rng(617), h = S / 2;
  for (let k = 0; k < 4; k++) { const cx = (k % 2) * h + h / 2, cy = (k >> 1) * h + h / 2, rad = h * 0.29, pts = lumpy(R, rad, rad * (0.6 + R() * 0.3), 16), rot = R() * 6.28;
    polyAt(g, pts.map(p => [p[0] * 1.14, p[1] * 1.14]), cx, cy, rot); g.fillStyle = 'rgba(30,74,14,0.65)'; g.fill();
    polyAt(g, pts, cx, cy, rot); const gr = g.createRadialGradient(cx - rad * 0.15, cy - rad * 0.1, 0, cx, cy, rad * 1.1); gr.addColorStop(0, 'rgba(196,255,96,1)'); gr.addColorStop(0.55, 'rgba(118,222,50,1)'); gr.addColorStop(1, 'rgba(60,146,24,1)'); g.fillStyle = gr; g.fill();
    polyAt(g, pts.map(p => [p[0] * 0.4, p[1] * 0.3]), cx - rad * 0.25, cy - rad * 0.22, rot); g.fillStyle = 'rgba(240,255,210,0.45)'; g.fill();
    for (let j = 0; j < 7; j++) { const a = R() * 6.28, d = rad * (1.22 + R() * 0.4), sz = 3 + R() * rad * 0.09; g.fillStyle = 'rgba(128,228,54,0.95)'; g.beginPath(); g.arc(cx + Math.cos(a) * d, cy + Math.sin(a) * d, sz, 0, 6.2832); g.fill(); } }
});
// the great drain's pool: bright where it wells up in the middle, darker toward the pit's walls, bubbles breaking on it
const SEWER_POOL = makeTex(256, (g, S) => {
  const c = S / 2, R = rng(618), gr = g.createRadialGradient(c, c, 0, c, c, c); gr.addColorStop(0, '#D2FF8A'); gr.addColorStop(0.35, '#8CF03C'); gr.addColorStop(0.8, '#3C9A18'); gr.addColorStop(1, '#173E0A'); g.fillStyle = gr; g.fillRect(0, 0, S, S);
  for (let k = 0; k < 26; k++) { const a = R() * 6.28, d = R() * c * 0.8, x = c + Math.cos(a) * d, y = c + Math.sin(a) * d, r = 3 + R() * 9; g.strokeStyle = 'rgba(220,255,170,0.55)'; g.lineWidth = 1.5; g.beginPath(); g.arc(x, y, r, 0, 6.2832); g.stroke(); }
});
const SEWER_MANHOLE = makeTex(256, (g, S) => {
  const c = S / 2, r = rng(616); g.fillStyle = '#2A2D2B'; g.fillRect(0, 0, S, S);
  const gr = g.createRadialGradient(c, c, 0, c, c, c); gr.addColorStop(0, '#4E5450'); gr.addColorStop(0.92, '#3A403C'); gr.addColorStop(1, '#202422'); g.fillStyle = gr; g.beginPath(); g.arc(c, c, c - 2, 0, 6.2832); g.fill();
  g.strokeStyle = 'rgba(20,24,22,0.9)'; for (const [rr, lw] of [[c - 10, 6], [c - 34, 4], [c * 0.42, 4]]) { g.lineWidth = lw; g.beginPath(); g.arc(c, c, rr, 0, 6.2832); g.stroke(); }
  g.fillStyle = 'rgba(110,118,112,0.75)'; for (let a = 0; a < 6.28; a += 0.26) for (const rr of [c - 22, c - 46]) { g.save(); g.translate(c + Math.cos(a) * rr, c + Math.sin(a) * rr); g.rotate(a); g.fillRect(-6, -2.5, 12, 5); g.restore(); }
  for (let k = -3; k <= 3; k++) { g.fillRect(c - 42, c + k * 11 - 2.5, 84, 5); }
  g.fillStyle = 'rgba(20,24,22,0.85)'; for (const a of [0.6, 3.74]) { g.beginPath(); g.ellipse(c + Math.cos(a) * (c - 60), c + Math.sin(a) * (c - 60), 9, 5, a, 0, 6.2832); g.fill(); }
  for (let k = 0; k < 40; k++) { g.fillStyle = `rgba(${110 + r() * 40 | 0},${60 + r() * 20 | 0},${30},${0.2 + r() * 0.3})`; g.beginPath(); g.arc(r() * S, r() * S, 2 + r() * 10, 0, 6.2832); g.fill(); }
  g.globalCompositeOperation = 'destination-in'; g.beginPath(); g.arc(c, c, c - 1, 0, 6.2832); g.fill(); g.globalCompositeOperation = 'source-over';
});
function sewerMats(M, T) {
  const mk = (c, extra, pbr) => aoPatch(toon(c, extra, pbr)), tex = (s, rep) => { for (const k of ['map', 'normalMap', 'roughnessMap']) if (s[k]) s[k].repeat.set(rep, rep); return s; };
  const hz = tex(surf('hazard'), 1.4), cc = surf('concrete'), br = surf('brick'), sw = surf('steelWall');
  const pb = (s, n, ro) => HI ? (s.normalMap ? { normalMap: s.normalMap, normalScale: new THREE.Vector2(n, n), roughnessMap: s.roughnessMap, roughness: ro || 1 } : { roughness: 0.6 }) : null;
  M.hazard = mk(0xFFFFFF, { map: hz.map }, pb(hz, 1, 1)); M.rampTop = M.hazard;
  M.concrete = mk(0xC4CCC0, { map: cc.map }, pb(cc, 1.2, 1)); M.brick = mk(0x8E9C8A, { map: br.map }, pb(br, 1.4, 1)); M.wall = mk(0xB8C2B6, { map: sw.map }, pb(sw, 1, 1));
  M.vc = mk(0xFFFFFF, { vertexColors: true }, { roughness: 0.58, metalness: 0.15 }); M.vcMetal = mk(0xFFFFFF, { vertexColors: true }, { roughness: 0.34, metalness: 0.72 });
  M.glowA = new THREE.MeshBasicMaterial({ color: new THREE.Color(0xFFB246).multiplyScalar(HI ? 2.7 : 1.35) }); M.glowG = new THREE.MeshBasicMaterial({ color: new THREE.Color(0x8CFF3A).multiplyScalar(HI ? 2.2 : 1.25) });
  M.glowVC = new THREE.MeshBasicMaterial({ vertexColors: true }); M.void = new THREE.MeshBasicMaterial({ color: 0x020403 });
  M.puddle = new THREE.MeshBasicMaterial({ map: SEWER_PUDDLES, color: new THREE.Color(1, 1, 1).multiplyScalar(HI ? 1.2 : 1), blending: THREE.CustomBlending, blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneMinusSrcAlphaFactor, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
  M.pool = new THREE.MeshBasicMaterial({ map: SEWER_POOL, color: new THREE.Color(1, 1, 1).multiplyScalar(HI ? 1.45 : 1.1) });
  M.sign = mk(0xFFFFFF, { map: SEWER_SIGNS, alphaTest: 0.5, side: THREE.DoubleSide }, { roughness: 0.62 }); M.manhole = mk(0xFFFFFF, { map: SEWER_MANHOLE, alphaTest: 0.5 }, { roughness: 0.42, metalness: 0.65 });
}
function sewerDress(K) {
  const { M, R, put, us } = K, vc = K.vc, V = SG.V, A = K.ARENA;
  const C = hexC, Y = C(0xE6A820), BK = C(0x1C1E1C), OR = C(0xF0641E), WH = C(0xF0EEE6), RD = C(0xC4302A), ST = C(0x5E6862), STD = C(0x2C3230), RU = C(0x8C4C28), GR = C(0x7CD83A), BL = C(0x2E62B8), CRM = C(0xE8E2D2);
  const rails = (pts, y, col, mat) => { // a railing along a polyline at height y over its posts
    for (let i = 0; i < pts.length; i++) { const p = pts[i]; vc(mat || M.vcMetal, SG.cyl(0.028, 0.028, y, 8, p.x, p.y + y / 2, p.z), col); vc(mat || M.vcMetal, SG.cyl(0.05, 0.05, 0.03, 10, p.x, p.y + 0.015, p.z), col); }
    for (let i = 0; i + 1 < pts.length; i++) { const a = pts[i], b = pts[i + 1]; vc(mat || M.vcMetal, SG.tube(V(a.x, a.y + y, a.z), V(b.x, b.y + y, b.z), 0.032, 8), col); vc(mat || M.vcMetal, SG.tube(V(a.x, a.y + y * 0.5, a.z), V(b.x, b.y + y * 0.5, b.z), 0.022, 6), col); } };
  const barrel = (x, y, z, col, tilt, ry) => { const lid = SG.shade(col, 0.82), g = [SG.paint(SG.cyl(0.25, 0.25, 0.64, 18, 0, 0.32, 0), (px, py, pz, o, nx, ny) => ny > 0.5 ? lid : col)]; for (const yy of [0.04, 0.22, 0.42, 0.6]) g.push(SG.paint(SG.band(0.256, 0.036, 18).translate(0, yy, 0), SG.shade(col, 0.7))); g.push(SG.paint(SG.cyl(0.035, 0.035, 0.03, 8, 0.12, 0.655, 0.05), STD));
    for (const gg of g) { if (tilt) gg.rotateZ(tilt); if (ry) gg.rotateY(ry); gg.translate(x, y, z); vc(M.vcMetal, gg, null); } };
  const valve = (x, y, z, nx, ny, nz, s) => { s = s || 1; const q = V(nx, ny, nz).normalize(); const w = SG.torus(0.17 * s, 0.026 * s, 0, 0, 0, 0, 0, 20); alignZ(w, q, V(x, y, z)); vc(M.vcMetal, w, RD); for (let k = 0; k < 3; k++) { const a = k * 2.0944, sp = new THREE.BoxGeometry(0.34 * s, 0.028 * s, 0.028 * s).rotateZ(a); alignZ(sp, q, V(x, y, z)); vc(M.vcMetal, sp, RD); } vc(M.vcMetal, alignZ(SG.cyl(0.04 * s, 0.04 * s, 0.12 * s, 10, 0, 0, 0).rotateX(Math.PI / 2), q, V(x - q.x * 0.04, y - q.y * 0.04, z - q.z * 0.04)), STD); };
  const lamp = (x, y, z, k) => { k = k || 1; vc(M.vcMetal, SG.cyl(0.07 * k, 0.09 * k, 0.07 * k, 12, x, y + 0.2 * k, z), STD); vc(M.glowVC, SG.ball(0.1 * k, x, y + 0.06 * k, z, 1, 1.25, 1), C(0xFFB246).multiplyScalar(HI ? 2.6 : 1.3));
    for (let a = 0; a < 6.28; a += 1.5708) vc(M.vcMetal, SG.tube(V(x + Math.cos(a) * 0.12 * k, y + 0.18 * k, z + Math.sin(a) * 0.12 * k), V(x + Math.cos(a) * 0.12 * k, y - 0.08 * k, z + Math.sin(a) * 0.12 * k), 0.012 * k, 5), STD);
    vc(M.vcMetal, SG.torus(0.12 * k, 0.012 * k, x, y + 0.05 * k, z, Math.PI / 2, 0, 16), STD); K.glow(x, y + 0.06 * k, z, 0.9 * k, 0xFFB050); };
  const chain = (a, b, t) => { const d = V(b.x - a.x, b.y - a.y, b.z - a.z), L = d.length(), n = Math.max(2, Math.round(L / 0.11)); d.normalize(); for (let i = 0; i < n; i++) { const p = V(a.x + d.x * L * (i + 0.5) / n, a.y + d.y * L * (i + 0.5) / n, a.z + d.z * L * (i + 0.5) / n), g = new THREE.BoxGeometry(i % 2 ? 0.018 : 0.06, 0.13, i % 2 ? 0.06 : 0.018); alignZ(g.rotateX(Math.PI / 2), d, p); vc(M.vcMetal, g, STD); } };
  const sign = (x, y, z, nx, nz, s, cell) => { const g = atlasUV(new THREE.PlaneGeometry(s, s), cell, 2); g.rotateY(Math.atan2(nx, nz)); g.translate(x + nx * 0.012, y, z + nz * 0.012); put(M.sign, g); };
  const drips = (x, y, z, nx, nz, n, L) => { for (let k = 0; k < n; k++) { const u = (R() - 0.5) * 0.9, px = x + (nz ? u : 0) + nx * 0.02, pz = z + (nx ? u : 0) + nz * 0.02, l = L * (0.4 + R() * 0.6); vc(M.glowVC, new THREE.ConeGeometry(0.03, l, 6).rotateX(Math.PI).translate(px, y - l / 2, pz), C(0x8CFF3A).multiplyScalar(HI ? 1.8 : 1.1)); vc(M.glowVC, SG.ball(0.034, px, y - l, pz, 1, 1.3, 1), C(0x9CFF4A).multiplyScalar(HI ? 2 : 1.2)); } };
  const freeSide = (b, k) => { const near = (a, c) => Math.abs(a - c) < 0.2, ovl = (a0, a1, c0, c1) => a0 < c1 - 0.05 && a1 > c0 + 0.05; return !RAMPS.some(rp => k === 0 ? near(rp[3], b[2]) && ovl(rp[0], rp[1], b[0], b[1]) : k === 1 ? near(rp[2], b[3]) && ovl(rp[0], rp[1], b[0], b[1]) : k === 2 ? near(rp[1], b[0]) && ovl(rp[2], rp[3], b[2], b[3]) : near(rp[0], b[1]) && ovl(rp[2], rp[3], b[2], b[3])); };
  return {
    rampTop: M.hazard,
    box(b, I) {
      const { w, d, h, cx, cz } = I;
      // angle irons up the corners
      for (const sx of [0, 1]) for (const sz of [0, 1]) { const x = sx ? b[1] : b[0], z = sz ? b[3] : b[2], ox = sx ? 1 : -1, oz = sz ? 1 : -1;
        vc(M.vcMetal, SG.box(0.12, h - 0.03, 0.03, x - ox * 0.045, h / 2, z + oz * 0.014), STD); vc(M.vcMetal, SG.box(0.03, h - 0.03, 0.12, x + ox * 0.014, h / 2, z - oz * 0.045), STD); }
      // a low wall gets a hazard band all round
      if (h < 1.05 && Math.min(w, d) < 1.6) put(M.hazard, worldUV(SG.box(w + 0.03, 0.17, d + 0.03, cx, h - 0.24, cz), 0.6));
      const F = K.faces(b);
      for (const f of F) {
        if (f.L >= 1.3 && h >= 0.7 && R() < 0.7) { // a vent: a dark recessed panel, its slits glowing amber, some of them breathing steam
          const vw = Math.min(1.2, f.L * 0.5), vh = Math.min(0.5, h * 0.4), vy = Math.min(h - vh / 2 - 0.22, Math.max(0.36, h * 0.52)), u = (R() - 0.5) * (f.L - vw - 0.4), px = f.fx + f.tx * u, pz = f.fz + f.tz * u, vert = R() < 0.35;
          vc(M.vcMetal, SG.box(f.nx ? 0.03 : vw, vh, f.nx ? vw : 0.03, px + f.nx * 0.012, vy, pz + f.nz * 0.012), STD);
          const n = vert ? Math.max(3, Math.round(vw / 0.14)) : 3;
          for (let k = 0; k < n; k++) { const t = (k + 0.5) / n - 0.5; if (vert) put(M.glowA, SG.box(f.nx ? 0.02 : 0.045, vh - 0.12, f.nx ? 0.045 : 0.02, px + f.nx * 0.03 + f.tx * t * (vw - 0.1), vy, pz + f.nz * 0.03 + f.tz * t * (vw - 0.1))); else put(M.glowA, SG.box(f.nx ? 0.02 : vw - 0.16, 0.05, f.nx ? vw - 0.16 : 0.02, px + f.nx * 0.03, vy + t * (vh - 0.14), pz + f.nz * 0.03)); }
          K.light(px + f.nx * 0.6, 0.2, pz + f.nz * 0.6, 2.6, 0xFFA040, 1.1); if (R() < 0.4) K.steam(px + f.nx * 0.25, vy, pz + f.nz * 0.25, 0.12, 0.55, 0.7, 0.5);
        } else if (f.L >= 1.2 && R() < 0.3) { // a pipe along the face on brackets, with a valve
          const L = f.L - 0.4, py = 0.32 + R() * 0.25, a = V(f.fx - f.tx * L / 2 + f.nx * 0.13, py, f.fz - f.tz * L / 2 + f.nz * 0.13), e = V(f.fx + f.tx * L / 2 + f.nx * 0.13, py, f.fz + f.tz * L / 2 + f.nz * 0.13);
          vc(M.vcMetal, SG.tube(a, e, 0.075, 12), R() < 0.5 ? ST : C(0x3E6E4A)); for (const t of [0.15, 0.85]) { const p = V(a.x + (e.x - a.x) * t, py, a.z + (e.z - a.z) * t); vc(M.vcMetal, SG.box(f.nx ? 0.14 : 0.06, 0.2, f.nx ? 0.06 : 0.14, p.x - f.nx * 0.06, py, p.z - f.nz * 0.06), STD); }
          for (const p of [a, e]) vc(M.vcMetal, alignZ(SG.cyl(0.1, 0.1, 0.05, 14, 0, 0, 0).rotateX(Math.PI / 2), V(f.tx, 0, f.tz), p), STD);
          const vp = V((a.x + e.x) / 2 + f.nx * 0.1, py, (a.z + e.z) / 2 + f.nz * 0.1); vc(M.vcMetal, SG.cyl(0.035, 0.035, 0.18, 8, vp.x, py + 0.1, vp.z), STD); valve(vp.x, py + 0.2, vp.z, 0, 1, 0, 0.7);
        }
        if (h >= 0.9 && R() < 0.22) sign(f.fx + f.tx * (R() - 0.5) * (f.L - 0.8), Math.min(h - 0.4, 1.05), f.fz + f.tz * (R() - 0.5) * (f.L - 0.8), f.nx, f.nz, 0.52, (R() * 4) | 0);
        if (R() < 0.16) { const u = (R() - 0.5) * (f.L - 0.6); drips(f.fx + f.tx * u, h, f.fz + f.tz * u, f.nx, f.nz, 2 + ((R() * 3) | 0), Math.min(0.7, h * 0.6)); K.light(f.fx + f.tx * u + f.nx * 0.4, 0.1, f.fz + f.tz * u + f.nz * 0.4, 1.6, 0x8CFF3A, 0.6); }
      }
      // up top: a yellow railing along a free edge, a traffic cone or a toxic barrel on a corner
      if (h >= 1.15 && Math.min(w, d) >= 2 && R() < 0.5) { const k = (R() * 4) | 0; if (freeSide(b, k)) { const y = b[5], ins = 0.2, L = (k < 2 ? w : d) * (0.45 + R() * 0.3), m = (R() - 0.5) * ((k < 2 ? w : d) - L - 0.6);
        const pts = []; for (let i = 0, n = Math.max(2, Math.round(L / 0.9) + 1); i < n; i++) { const t = -L / 2 + L * i / (n - 1) + m; pts.push(k === 0 ? V(cx + t, y, b[2] + ins) : k === 1 ? V(cx + t, y, b[3] - ins) : k === 2 ? V(b[0] + ins, y, cz + t) : V(b[1] - ins, y, cz + t)); } rails(pts, 0.62, Y); } }
      if (w > 1.3 && d > 1.3 && R() < 0.4) { const ix = R() < 0.5 ? 1 : -1, iz = R() < 0.5 ? 1 : -1, px = cx + ix * (w / 2 - 0.36), pz = cz + iz * (d / 2 - 0.36); if (R() < 0.65) { K.cone(px - ix * 0.08, b[5], pz - iz * 0.08); if (R() < 0.4) K.cone(px - ix * 0.72, b[5], pz - iz * 0.08); } else barrel(px, b[5], pz, [Y, GR, BL][(R() * 3) | 0], 0, R() * 6); }
    },
    float(b, I) { // a steel deck up in the air: bolts at its corners, two beams under it, a caged lamp beneath lighting the floor
      for (const sx of [0, 1]) for (const sz of [0, 1]) { const x = sx ? b[1] - 0.18 : b[0] + 0.18, z = sz ? b[3] - 0.18 : b[2] + 0.18; vc(M.vcMetal, SG.cyl(0.07, 0.07, 0.06, 10, x, b[5] + 0.03, z), STD); }
      for (const t of [-0.3, 0.3]) vc(M.vcMetal, I.w > I.d ? SG.box(I.w - 0.3, 0.16, 0.12, I.cx, b[4] - 0.08, I.cz + t * I.d) : SG.box(0.12, 0.16, I.d - 0.3, I.cx + t * I.w, b[4] - 0.08, I.cz), STD);
      lamp(I.cx, b[4] - 0.28, I.cz, 1.2); K.light(I.cx, 0.2, I.cz, 3.4, 0xFFA040, 1.0);
      put(M.hazard, worldUV(SG.box(I.w + 0.02, 0.1, I.d + 0.02, I.cx, b[5] - 0.07, I.cz), 0.6));
    },
    roundMats(b, kind) { return kind === 'drum' ? [M.concrete, M.top, M.dark] : kind === 'column' ? [M.wall, M.top, M.dark] : kind === 'rpad' ? [M.wall, M.top, M.dark] : null; },
    skipBody(b, kind) { return kind === 'rotunda'; },
    noScatter(x, z, y) { return y > 0.3 && BOXES.some(b => b[6] === 'rotunda' && inR(x, z, b, 0.6)); },
    round(b, kind, cx, cz, rad, h, top) {
      if (kind === 'drum') { // a concrete pipe stood on end, an iron manhole cover on top, slime glowing through the gap round it
        const glowRing = R() < 0.55; const disc = new THREE.CircleGeometry(rad * 0.66, SEG(36)).rotateX(-Math.PI / 2).translate(cx, top + 0.008, cz); put(M.manhole, disc);
        vc(glowRing ? M.glowVC : M.vcMetal, SG.torus(rad * 0.685, 0.03, cx, top + 0.006, cz, Math.PI / 2, 0, 40), glowRing ? C(0x8CFF3A).multiplyScalar(HI ? 2.2 : 1.2) : STD);
        for (const yy of [0.22, h - 0.18]) vc(M.vcMetal, SG.cyl(rad + 0.022, rad + 0.022, 0.1, 40, cx, yy, cz, true), STD);
        for (let k = 0; k < 8; k++) { const a = k / 8 * 6.2832; vc(M.vcMetal, SG.ball(0.035, cx + Math.cos(a) * (rad - 0.12), top + 0.01, cz + Math.sin(a) * (rad - 0.12), 1, 0.6, 1), STD); }
        if (glowRing) { K.steam(cx, top + 0.04, cz, rad * 0.55, 0.7, 0.45, 0.45); const a = R() * 6.28; drips(cx + Math.cos(a) * (rad + 0.01), top, cz + Math.sin(a) * (rad + 0.01), Math.cos(a), Math.sin(a), 3, h * 0.7); K.light(cx, top + 0.3, cz, rad + 1.6, 0x8CFF3A, 0.9); }
      } else if (kind === 'column') {
        if (R() < 0.5) { // a big riser pipe: flanges with bolts, a red valve wheel, a gauge, a vent cap glowing green
          for (let yy = 0.5; yy < h - 0.2; yy += 0.95) { vc(M.vcMetal, SG.cyl(rad + 0.07, rad + 0.07, 0.12, 40, cx, yy, cz), STD); for (let k = 0; k < 12; k++) { const a = k / 12 * 6.2832; vc(M.vcMetal, SG.ball(0.03, cx + Math.cos(a) * (rad + 0.075), yy + 0.07, cz + Math.sin(a) * (rad + 0.075)), ST); } }
          const a = R() * 6.28, nx = Math.cos(a), nz = Math.sin(a); vc(M.vcMetal, alignZ(SG.cyl(0.07, 0.07, 0.3, 10, 0, 0, 0).rotateX(Math.PI / 2), V(nx, 0, nz), V(cx + nx * (rad + 0.12), 1.3, cz + nz * (rad + 0.12))), STD); valve(cx + nx * (rad + 0.3), 1.3, cz + nz * (rad + 0.3), nx, 0, nz, 1.6);
          const g2 = a + 0.9, gx = Math.cos(g2), gz = Math.sin(g2); vc(M.vcMetal, alignZ(SG.cyl(0.13, 0.13, 0.06, 18, 0, 0, 0).rotateX(Math.PI / 2), V(gx, 0, gz), V(cx + gx * (rad + 0.04), 1.85, cz + gz * (rad + 0.04))), STD); vc(M.glowVC, alignZ(new THREE.CircleGeometry(0.105, 18), V(gx, 0, gz), V(cx + gx * (rad + 0.075), 1.85, cz + gz * (rad + 0.075))), C(0xE8F4D8).multiplyScalar(HI ? 1.3 : 1));
          vc(M.vcMetal, alignZ(new THREE.BoxGeometry(0.012, 0.09, 0.006).translate(0, 0.035, 0).rotateZ(-0.6), V(gx, 0, gz), V(cx + gx * (rad + 0.08), 1.85, cz + gz * (rad + 0.08))), RD);
          put(M.glowG, new THREE.CircleGeometry(rad * 0.55, SEG(28)).rotateX(-Math.PI / 2).translate(cx, top + 0.006, cz)); for (let k = -3; k <= 3; k++) vc(M.vcMetal, SG.box(rad * 1.1 * Math.sqrt(Math.max(0, 1 - (k / 3.6) ** 2)), 0.04, 0.05, cx, top + 0.03, cz + k * rad * 0.15), STD);
          vc(M.vcMetal, SG.torus(rad * 0.56, 0.04, cx, top + 0.02, cz, Math.PI / 2, 0, 32), Y); K.light(cx, top + 0.4, cz, 2.2, 0x8CFF3A, 0.7);
        } else { // a chemical tank: hazard bands, a glowing sight glass with level marks, a ladder up the back
          for (const yy of [0.3, h - 0.32]) put(M.hazard, worldUV(SG.cyl(rad + 0.02, rad + 0.02, 0.24, 40, cx, yy, cz, true), 0.6));
          const a = R() * 6.28, nx = Math.cos(a), nz = Math.sin(a), tx = -nz, tz = nx;
          vc(M.vcMetal, alignZ(new THREE.BoxGeometry(0.24, h - 1.0, 0.04), V(nx, 0, nz), V(cx + nx * (rad + 0.02), h / 2, cz + nz * (rad + 0.02))), STD); vc(M.glowVC, alignZ(new THREE.BoxGeometry(0.14, h - 1.2, 0.03), V(nx, 0, nz), V(cx + nx * (rad + 0.04), h / 2, cz + nz * (rad + 0.04))), C(0x8CFF3A).multiplyScalar(HI ? 2 : 1.2));
          for (let k = 0; k < 6; k++) vc(M.vcMetal, alignZ(new THREE.BoxGeometry(0.28, 0.02, 0.02), V(nx, 0, nz), V(cx + nx * (rad + 0.06), 0.7 + k * (h - 1.4) / 5, cz + nz * (rad + 0.06))), STD);
          const lx = cx - nx * (rad + 0.12), lz = cz - nz * (rad + 0.12); for (const s of [-1, 1]) vc(M.vcMetal, SG.box(0.04, h + 0.4, 0.04, lx + tx * 0.22 * s, (h + 0.4) / 2, lz + tz * 0.22 * s), Y); for (let yy = 0.3; yy < h + 0.3; yy += 0.3) vc(M.vcMetal, SG.tube(V(lx - tx * 0.22, yy, lz - tz * 0.22), V(lx + tx * 0.22, yy, lz + tz * 0.22), 0.018, 6), Y);
          K.light(cx + nx * (rad + 0.5), 0.3, cz + nz * (rad + 0.5), 2.2, 0x8CFF3A, 0.8);
        }
      } else if (kind === 'rotunda') { // the great drain in the middle of the map: a riveted steel drum, a heavy yellow lip round a slotted iron
        // grate, the pit under it glowing with slime, amber lamps set into the rim, steam rising through the slots
        put(M.wall, worldUV(SG.cyl(rad, rad, h, 64, cx, h / 2, cz, true), us)); K.hull(SG.cyl(rad + 0.07, rad + 0.07, h + 0.14, 44, cx, h / 2, cz));
        put(M.hazard, worldUV(SG.cyl(rad + 0.02, rad + 0.02, 0.2, 64, cx, h - 0.2, cz, true), 0.6)); vc(M.vcMetal, SG.cyl(rad + 0.025, rad + 0.025, 0.1, 64, cx, 0.24, cz, true), STD);
        for (let k = 0; k < 16; k++) { const a = k / 16 * 6.2832; vc(M.vcMetal, SG.box(0.06, h - 0.6, 0.1, 0, 0, 0).rotateY(-a).translate(cx + Math.cos(a) * (rad + 0.02), h / 2 - 0.08, cz + Math.sin(a) * (rad + 0.02)), STD); }
        const ri = rad * 0.72, rm = (ri + rad) / 2 + 0.06;
        put(M.top, worldUV(new THREE.RingGeometry(ri + 0.1, rad, SEG(64), 1).rotateX(-Math.PI / 2).translate(cx, top, cz), us));
        vc(M.vcMetal, SG.torus(ri + 0.05, 0.08, cx, top + 0.005, cz, Math.PI / 2, 0, 72), Y); vc(M.vcMetal, SG.torus(rad - 0.03, 0.04, cx, top + 0.005, cz, Math.PI / 2, 0, 72), STD);
        vc(M.vcMetal, new THREE.CylinderGeometry(ri, ri, 0.5, SEG(56), 1, true).scale(-1, 1, 1).translate(cx, top - 0.25, cz), STD);
        put(M.pool, new THREE.CircleGeometry(ri, SEG(56)).rotateX(-Math.PI / 2).translate(cx, top - 0.46, cz));
        // the grate: heavy bars straight across, two braces under them, a hub in the middle
        for (let o = -ri + 0.19; o < ri - 0.08; o += 0.22) { const L = 2 * Math.sqrt(Math.max(0, ri * ri - o * o)) - 0.02; if (L > 0.2) vc(M.vc, SG.box(L, 0.1, 0.095, cx, top - 0.05, cz + o), C(0x2A302C)); }
        for (const o of [-ri * 0.48, ri * 0.48]) vc(M.vc, SG.box(0.12, 0.16, 2 * Math.sqrt(ri * ri - o * o) - 0.02, cx + o, top - 0.16, cz), C(0x1E2420));
        vc(M.vcMetal, SG.cyl(0.5, 0.5, 0.06, 32, cx, top - 0.01, cz), Y); vc(M.vcMetal, SG.cyl(0.3, 0.32, 0.08, 24, cx, top + 0.01, cz), STD);
        for (let k = 0; k < 6; k++) { const a = k / 6 * 6.2832; vc(M.vcMetal, SG.ball(0.035, cx + Math.cos(a) * 0.41, top + 0.025, cz + Math.sin(a) * 0.41, 1, 0.6, 1), ST); }
        // bolts round the rim, and amber lamps set into it
        for (let k = 0; k < 32; k++) { const a = k / 32 * 6.2832; vc(M.vcMetal, SG.ball(0.042, cx + Math.cos(a) * (rad - 0.13), top + 0.012, cz + Math.sin(a) * (rad - 0.13), 1, 0.6, 1), ST); }
        for (let k = 0; k < 8; k++) { const a = k / 8 * 6.2832 + 0.39, x = cx + Math.cos(a) * rm, z = cz + Math.sin(a) * rm, ry = -(a + Math.PI / 2);
          vc(M.vcMetal, SG.box(0.42, 0.05, 0.2, 0, 0, 0).rotateY(ry).translate(x, top + 0.02, z), STD); put(M.glowA, SG.box(0.32, 0.03, 0.11, 0, 0, 0).rotateY(ry).translate(x, top + 0.045, z)); K.light(x, top + 0.2, z, 1.4, 0xFFA040, 0.5); }
        for (let k = 0; k < 10; k++) { const a = k / 10 * 6.2832 + 0.2, x = cx + Math.cos(a) * (rad + 0.012), z = cz + Math.sin(a) * (rad + 0.012); vc(M.glowVC, alignZ(SG.box(0.2, 0.06, 0.012, 0, 0, 0), V(Math.cos(a), 0, Math.sin(a)), V(x, h * 0.5, z)), C(0xFFB246).multiplyScalar(HI ? 2.6 : 1.3)); K.light(cx + Math.cos(a) * (rad + 0.6), 0.2, cz + Math.sin(a) * (rad + 0.6), 2, 0xFFA040, 0.6); }
        K.light(cx, top + 0.3, cz, ri + 1.2, 0x8CFF3A, 1.3); K.glow(cx, top + 0.15, cz, ri * 1.5, 0x6CE030);
        for (let k = 0; k < 3; k++) { const a = k * 2.0944 + R(), d = ri * 0.45; K.steam(cx + Math.cos(a) * d, top - 0.1, cz + Math.sin(a) * d, ri * 0.35, 1.25, HI ? 0.8 : 0.5, 0.55); }
      } else if (kind === 'rpad') { for (let k = 0; k < 8; k++) { const a = k / 8 * 6.2832; vc(M.vcMetal, SG.ball(0.04, cx + Math.cos(a) * (rad - 0.1), top + 0.01, cz + Math.sin(a) * (rad - 0.1), 1, 0.6, 1), ST); }
        lamp(cx, b[4] - 0.25, cz, 1.1); K.light(cx, 0.2, cz, 3, 0xFFA040, 0.9); }
    },
    ramp(r) { const [x0, x1, z0, z1] = r, zr = r[4] === 'z', lo = zr ? (r[5] < r[6] ? z0 : z1) : (r[5] < r[6] ? x0 : x1); // a dark steel lip across its foot
      vc(M.vcMetal, zr ? SG.box(x1 - x0, 0.03, 0.08, (x0 + x1) / 2, 0.015, lo) : SG.box(0.08, 0.03, z1 - z0, lo, 0.015, (z0 + z1) / 2), STD); },
    hole(hh) { const cx = (hh[0] + hh[1]) / 2, cz = (hh[2] + hh[3]) / 2, sz = Math.min(hh[1] - hh[0], hh[3] - hh[2]); if (R() < 0.6) K.light(cx, 0.05, cz, Math.max(hh[1] - hh[0], hh[3] - hh[2]) * 0.6 + 1, 0x8CFF3A, 1.1); if (sz > 1.5) K.steam(cx, WATER_Y + 0.15, cz, sz * 0.3, 1.1, HI ? 0.5 : 0.3, 0.6); },
    noPlinth: true,
    spot(x, z, i, corner, y) {
      const out = Math.atan2(x, z), ox = Math.sin(out), oz = Math.cos(out), sx = Math.cos(out), sz = -Math.sin(out);
      if (corner) { // a pump tower rising out of the slime: a big riser, flanges, a valve wheel, a gauge, a caged lamp, a ladder, a platform
        const r0 = 0.62, Ht = 6.4; put(M.wall, worldUV(SG.cyl(r0, r0, Ht + 1, 32, x, Ht / 2 - 0.5, z), us)); K.hull(SG.cyl(r0 + 0.06, r0 + 0.06, Ht + 1.1, 24, x, Ht / 2 - 0.5, z));
        for (const yy of [0.2, 1.6, 3.0, 4.4, 5.8]) { vc(M.vcMetal, SG.cyl(r0 + 0.08, r0 + 0.08, 0.14, 32, x, yy, z), STD); for (let k = 0; k < 10; k++) { const a = k / 10 * 6.2832; vc(M.vcMetal, SG.ball(0.035, x + Math.cos(a) * (r0 + 0.085), yy + 0.08, z + Math.sin(a) * (r0 + 0.085)), ST); } }
        vc(M.vcMetal, SG.cyl(r0 + 0.12, r0 + 0.02, 0.5, 32, x, Ht + 0.25, z), STD); vc(M.vcMetal, SG.cone(r0 + 0.2, 0.5, x, Ht + 0.75, z, 24), ST);
        const ex = x + ox * 1.6, ez = z + oz * 1.6; vc(M.vcMetal, SG.curve([V(x, Ht - 0.6, z), V(x + ox * 0.8, Ht - 0.4, z + oz * 0.8), V(ex, Ht - 1.2, ez), V(ex, -1, ez)], 0.32, 20, 14), ST);
        valve(x - ox * (r0 + 0.32), 1.7, z - oz * (r0 + 0.32), -ox, 0, -oz, 2.2); vc(M.vcMetal, alignZ(SG.cyl(0.09, 0.09, 0.32, 10, 0, 0, 0).rotateX(Math.PI / 2), V(-ox, 0, -oz), V(x - ox * (r0 + 0.14), 1.7, z - oz * (r0 + 0.14))), STD);
        lamp(x + sx * (r0 + 0.22), 3.6, z + sz * (r0 + 0.22), 1.6); vc(M.vcMetal, SG.box(Math.abs(sx) * 0.3 + 0.05, 0.05, Math.abs(sz) * 0.3 + 0.05, x + sx * (r0 + 0.1), 3.9, z + sz * (r0 + 0.1)), STD);
        const lx = x - sx * (r0 + 0.12), lz = z - sz * (r0 + 0.12); for (const s of [-1, 1]) vc(M.vcMetal, SG.box(0.045, 5.4, 0.045, lx + ox * 0.24 * s, 2.2, lz + oz * 0.24 * s), Y); for (let yy = -0.3; yy < 4.9; yy += 0.32) vc(M.vcMetal, SG.tube(V(lx - ox * 0.24, yy, lz - oz * 0.24), V(lx + ox * 0.24, yy, lz + oz * 0.24), 0.02, 6), Y);
        const py = 4.8, pr = r0 + 0.95; vc(M.vcMetal, SG.cyl(pr, pr, 0.08, 32, x, py, z), STD); vc(M.vcMetal, SG.cyl(pr + 0.02, pr + 0.02, 0.1, 32, x, py - 0.02, z, true), Y);
        const rp = []; for (let k = 0; k <= 10; k++) { const a = out + Math.PI * 0.35 + k / 10 * Math.PI * 1.3; rp.push(V(x + Math.cos(a) * (pr - 0.08), py + 0.04, z + Math.sin(a) * (pr - 0.08))); } rails(rp, 0.7, Y);
        sign(x - ox * (r0 + 0.02), 2.6, z - oz * (r0 + 0.02), -ox, -oz, 0.7, i % 4);
        K.glow(x, 0.1, z, 2.4, 0x6CE030);
      } else if (i % 2) { // a tank on legs over the slime: a glowing sight glass, hazard bands, pipes down into it
        const L = 2.8, tr = 0.85, ty = 1.4; const tg = SG.cyl(tr, tr, L, 32, 0, 0, 0).rotateZ(Math.PI / 2); SG.rotY(tg, Math.atan2(-sz, sx), 0, 0); tg.translate(x, ty, z); put(M.wall, worldUV(tg, us));
        const th = SG.cyl(tr + 0.06, tr + 0.06, L + 0.12, 24, 0, 0, 0).rotateZ(Math.PI / 2); SG.rotY(th, Math.atan2(-sz, sx), 0, 0); K.hull(th.translate(x, ty, z));
        for (const s of [-1, 1]) { const cap = SG.ball(tr, 0, 0, 0, 0.35, 1, 1); SG.rotY(cap, Math.atan2(-sz, sx), 0, 0); vc(M.vcMetal, cap.translate(x + sx * s * L / 2, ty, z + sz * s * L / 2), ST); }
        for (const t of [-0.9, 0.9]) { const g = SG.cyl(tr + 0.03, tr + 0.03, 0.24, 32, 0, 0, 0, true).rotateZ(Math.PI / 2); SG.rotY(g, Math.atan2(-sz, sx), 0, 0); put(M.hazard, worldUV(g.translate(x + sx * t, ty, z + sz * t), 0.6)); }
        for (const t of [-1, 1]) for (const s of [-1, 1]) vc(M.vcMetal, SG.box(0.12, ty + 1, 0.12, x + sx * t * 1.0 + ox * s * 0.55, (ty - 1) / 2, z + sz * t * 1.0 + oz * s * 0.55), STD);
        vc(M.glowVC, (() => { const g = SG.box(1.6, 0.16, 0.04, 0, 0, 0); SG.rotY(g, Math.atan2(-sz, sx), 0, 0); return g.translate(x - ox * (tr + 0.01), ty + 0.15, z - oz * (tr + 0.01)); })(), C(0x8CFF3A).multiplyScalar(HI ? 2 : 1.2));
        vc(M.vcMetal, SG.curve([V(x + sx * 0.6, ty - tr, z + sz * 0.6), V(x + sx * 0.6, ty - tr - 0.5, z + sz * 0.6), V(x + sx * 1.2 + ox * 0.5, -0.4, z + sz * 1.2 + oz * 0.5), V(x + sx * 1.3 + ox * 0.6, -1, z + sz * 1.3 + oz * 0.6)], 0.14, 14, 10), C(0x3E6E4A));
        sign(x - ox * (tr + 0.02), ty + 0.7, z - oz * (tr + 0.02), -ox, -oz, 0.6, 2); K.glow(x - ox * tr, ty + 0.15, z - oz * tr, 1.6, 0x6CE030);
      } else { // a dump of toxic drums sinking into the slime, some tipped, one leaking
        const cols = [Y, GR, BL, RU, Y]; for (let k = 0; k < 6; k++) { const a = k / 6 * 6.28 + R(), rr = 0.35 + R() * 0.75; barrel(x + Math.cos(a) * rr, -0.6 + R() * 0.25, z + Math.sin(a) * rr, cols[k % 5], k % 3 === 0 ? 1.2 + R() * 0.4 : (R() - 0.5) * 0.3, R() * 6); }
        barrel(x, 0.1, z, Y, 0, R() * 6); barrel(x + 0.3, 0.75, z - 0.2, GR, 0.25, 1); K.glow(x, 0.1, z, 2.2, 0x6CE030);
      }
    },
    outer() { SG.lod(0.65, () => this.walls()); },
    walls() {
      const W = A + 15.5, TH = 2, H = 19, TY = 5.4, TR = 2.9, nT = 2;
      // the walls: concrete at the slime line, brick above, a ledge between; square pillars in the corners
      for (const [ax, az] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const px = ax * (W + TH / 2), pz = az * (W + TH / 2), len = 2 * W + 2 * TH, lx = ax ? TH : len, lz = az ? TH : len;
        put(M.concrete, worldUV(SG.box(lx, 4.4, lz, px, 1.2, pz), 0.3)); put(M.brick, worldUV(SG.box(lx, H - 3.4, lz, px, 3.4 + (H - 3.4) / 2, pz), 0.35));
        put(M.concrete, worldUV(SG.box(ax ? TH + 0.5 : len, 0.4, az ? TH + 0.5 : len, ax * (W + TH / 2 - 0.25), 3.4, az * (W + TH / 2 - 0.25)), 0.3)); }
      for (const sx of [-1, 1]) for (const sz of [-1, 1]) { const cx = sx * (W - 1.4), cz = sz * (W - 1.4); put(M.concrete, worldUV(SG.box(3, H + 1, 3, cx, H / 2 - 0.5, cz), 0.3)); for (const yy of [2.2, 8.5]) put(M.hazard, worldUV(SG.box(3.04, 0.6, 3.04, cx, yy, cz), 0.5)); lamp(cx - sx * 1.6, 6.2, cz - sz * 1.6, 1.8); }
      // each wall: tunnel mouths pouring slime, pipes along it, a catwalk with a railing, caged lamps, ladders, signs
      const falls = [];
      for (const [ax, az] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = -ax, nz = -az, tx = az, tz = -ax, wx = ax * W, wz = az * W, at = (u, off, y) => V(wx + tx * u + nx * off, y, wz + tz * u + nz * off);
        for (let t = 0; t < nT; t++) { const u = (t - (nT - 1) / 2) * W * 0.72 + (R() - 0.5) * 3, c = at(u, 0, TY), q = V(nx, 0, nz);
          const ring = new THREE.CylinderGeometry(TR + 0.55, TR + 0.55, 1.7, SEG(40), 1, true).rotateX(Math.PI / 2), inner = new THREE.CylinderGeometry(TR, TR, 1.7, SEG(40), 1, true).rotateX(Math.PI / 2);
          put(M.concrete, worldUV(alignZ(ring, q, at(u, 0.85, TY)), 0.3)); put(M.concrete, worldUV(alignZ(inner.scale(-1, 1, 1), q, at(u, 0.85, TY)), 0.3));
          put(M.concrete, worldUV(alignZ(new THREE.RingGeometry(TR, TR + 0.55, SEG(40)), q, at(u, 1.7, TY)), 0.3)); put(M.void, alignZ(new THREE.CircleGeometry(TR, SEG(40)), q, at(u, 0.05, TY)));
          for (let k = 0; k < 14; k++) { const a = k / 14 * 6.2832, p = at(u + Math.cos(a) * (TR + 0.3), 1.72, TY + Math.sin(a) * (TR + 0.3)); vc(M.vcMetal, SG.ball(0.07, p.x, p.y, p.z), ST); }
          for (let k = 0; k < 7; k++) { const a = Math.PI * (0.15 + k / 6 * 0.7); if (k === 3) continue; vc(M.vcMetal, alignZ(SG.cyl(0.05, 0.05, TR * 2 * Math.sin(a), 8, 0, 0, 0).rotateX(Math.PI / 2), V(tx, 0, tz), at(u, 1.0, TY - TR * Math.cos(a) * 0.98)), STD); } // (bars across the mouth, rusted open in the middle)
          falls.push({ x: c.x + nx * 1.7, z: c.z + nz * 1.7, nx, nz, tx, tz, y0: TY - TR + 0.12, w: TR * 1.25 });
          sign(...at(u + TR + 1.4, 0.02, 3.2).toArray(), nx, nz, 1.1, t ? 1 : 2);
        }
        // pipes: a big one low along the wall, a smaller one high, risers between, flanges every few metres
        const L = 2 * W - 6; vc(M.vcMetal, SG.tube(at(-L / 2, 0.75, 0.6), at(L / 2, 0.75, 0.6), 0.5, 18), ST); vc(M.vcMetal, SG.tube(at(-L / 2, 0.5, 10.2), at(L / 2, 0.5, 10.2), 0.3, 14), C(0x4E6E5A));
        for (let u = -L / 2 + 2; u < L / 2; u += 4.6) { vc(M.vcMetal, alignZ(SG.cyl(0.62, 0.62, 0.16, 24, 0, 0, 0).rotateX(Math.PI / 2), V(tx, 0, tz), at(u, 0.75, 0.6)), STD); vc(M.vcMetal, alignZ(SG.cyl(0.4, 0.4, 0.12, 18, 0, 0, 0).rotateX(Math.PI / 2), V(tx, 0, tz), at(u + 2.3, 0.5, 10.2)), STD); }
        for (let u = -L / 2 + 5; u < L / 2 - 3; u += 11) if (!falls.some(f => Math.hypot(f.x - at(u, 0, 0).x, f.z - at(u, 0, 0).z) < TR + 2.5)) { vc(M.vcMetal, SG.tube(at(u, 0.5, 1.2), at(u, 0.5, 10.2), 0.22, 12), C(0x4E6E5A)); valve(...at(u, 0.85, 4.2).toArray(), nx, 0, nz, 1.6); }
        // the catwalk at the ledge: a grating on brackets, a yellow railing, ladders down to the slime; lamps above it
        const cy = 7.6, cw = 1.4; vc(M.vcMetal, SG.box(tx ? L + 4 : cw, 0.1, tz ? L + 4 : cw, ...at(0, cw / 2, cy).toArray()), STD);
        for (let u = -L / 2; u <= L / 2; u += 3.2) { vc(M.vcMetal, SG.tube(at(u, 0.02, cy - 0.9), at(u, cw - 0.1, cy - 0.04), 0.05, 6), STD); }
        const rp = []; for (let u = -L / 2; u <= L / 2 + 0.01; u += 2.2) rp.push(at(u, cw - 0.06, cy + 0.05)); rails(rp, 0.9, Y);
        for (const u of [-W * 0.42, W * 0.12]) { for (const s of [-1, 1]) vc(M.vcMetal, SG.box(0.05, cy + 1.2, 0.05, ...at(u + s * 0.25, 0.12, (cy - 1.2) / 2 + 0.6).toArray()), Y); for (let yy = -0.2; yy < cy; yy += 0.34) vc(M.vcMetal, SG.tube(at(u - 0.25, 0.12, yy), at(u + 0.25, 0.12, yy), 0.022, 6), Y); }
        for (let u = -L / 2 + 3; u < L / 2; u += 7.2) lamp(...at(u, 0.3, 6.0).toArray(), 1.7);
        for (let u = -L / 2 + 6; u < L / 2; u += 9.5) if (R() < 0.6) chain(at(u, 1 + R() * 3, H + 2), at(u, 1 + R() * 3, H - 4 - R() * 5));
      }
      // the slime falls: a heavy sheet curling off each lip and down into the pool, a churning ring of froth where it lands, a green glow
      for (const f of falls) { const g = slimeFallGeo(f), m = new THREE.Mesh(g, SLIME_FALL_MAT); m.renderOrder = 2; K.add(m); const sp = new THREE.Mesh(new THREE.CircleGeometry(f.w * 0.9, 40).rotateX(-Math.PI / 2), SLIME_SPLASH_MAT); sp.position.set(f.x + f.nx * 2.2, WATER_Y + 0.02, f.z + f.nz * 2.2); sp.renderOrder = 3; K.add(sp); K.glow(f.x + f.nx * 2.2, 0.4, f.z + f.nz * 2.2, f.w * 2.4, 0x6CE030); K.steam(f.x + f.nx * 2.4, WATER_Y + 0.3, f.z + f.nz * 2.4, f.w * 0.6, 2.4, HI ? 0.9 : 0.5, 1.0); }
      // the platform's own edge: a hazard strip round its top, pipe elbows coming out of its sides and down into the slime
      for (const [ax, az] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const len = 2 * A, tx = az, tz = -ax;
        put(M.hazard, worldUV(SG.box(ax ? 0.04 : len + 0.08, 0.14, az ? 0.04 : len + 0.08, ax * (A + 0.02), -0.09, az * (A + 0.02)), 0.6));
        for (let u = -A + 4.5 + R() * 3; u < A - 3; u += 9 + R() * 4) { const p = V(ax * A + tx * u, -0.3, az * A + tz * u); vc(M.vcMetal, SG.curve([p, V(p.x + ax * 0.5, p.y, p.z + az * 0.5), V(p.x + ax * 0.9, p.y - 0.3, p.z + az * 0.9), V(p.x + ax * 0.95, -1.2, p.z + az * 0.95)], 0.22, 12, 12), ST); vc(M.vcMetal, alignZ(SG.cyl(0.3, 0.3, 0.1, 18, 0, 0, 0).rotateX(Math.PI / 2), V(ax, 0, az), V(p.x + ax * 0.06, p.y, p.z + az * 0.06)), STD); }
      }
      for (let k = 0; k < 8; k++) { const a = k / 8 * 6.2832 + R() * 0.5, d = A + 3 + R() * 6; K.steam(Math.sin(a) * d, WATER_Y + 0.1, Math.cos(a) * d, 1.4, 1.8, HI ? 0.35 : 0.2, 0.55); }
      K.anim({ tick(dt, t) { SLIME_FALL_MAT.uniforms.uTime.value = t; SLIME_SPLASH_MAT.uniforms.uTime.value = t; } });
    },
    // traffic cones to knock about: in twos and threes by the blocks' feet and along the platform's edge, now and then one up on a block
    props() {
      const want = A > 28 ? 13 : 10, got = []; let tries = 0;
      const free = (x, z, y) => { if (Math.hypot(x, z) < 7 || Math.abs(x) > A - 0.7 || Math.abs(z) > A - 0.7) return false;
        for (const [ox, oz] of [[0, 0], [0.4, 0], [-0.4, 0], [0, 0.4], [0, -0.4]]) { if (Math.abs(surfaceUnder(x + ox, z + oz, y + 0.2) - y) > 0.01 || solidThrough(x + ox, z + oz, y + 0.2)) return false; }
        return !RAMPS.some(r => inR(x, z, r, 0.5)) && !got.some(p => Math.hypot(p[0] - x, p[1] - z) < 0.8); };
      const rects = BOXES.filter(b => !b[6] && b[4] < 0.05);
      // slime puddles, one by one over the floor and the tops of the blocks: never in a grid
      const pl = []; for (let t = 0, n = 0, nP = A > 28 ? 20 : 15; t < 300 && n < nP; t++) { const sz = 0.9 + R() * 1.6, x = (R() * 2 - 1) * (A - 1), z = (R() * 2 - 1) * (A - 1), y = surfaceUnder(x, z, 40);
        if (y < -0.5 || Math.hypot(x, z) < 6.5) continue; let ok = true; for (let a = 0; a < 6.28 && ok; a += 0.9) { const px = x + Math.cos(a) * sz * 0.42, pz = z + Math.sin(a) * sz * 0.42; if (Math.abs(surfaceUnder(px, pz, 40) - y) > 0.01 || RAMPS.some(rp => inR(px, pz, rp, 0.1))) ok = false; }
        if (!ok) continue; const g = atlasUV(new THREE.PlaneGeometry(sz, sz), (R() * 4) | 0, 2); g.rotateX(-Math.PI / 2); g.rotateY(R() * 6.28); g.translate(x, y + 0.01, z); pl.push(g); n++; }
      if (pl.length) { const pm = new THREE.Mesh(mergeGeos(pl, true), M.puddle); pm.renderOrder = 5; pm.layers.set(2); K.add(pm); }
      while (got.length < want && tries++ < 500) { let x, z, y = 0; const r = R();
        if (r < 0.55 && rects.length) { const b = rects[(R() * rects.length) | 0], k = (R() * 4) | 0, u = R(); x = k < 2 ? b[0] + (b[1] - b[0]) * u : k === 2 ? b[0] - 0.5 : b[1] + 0.5; z = k >= 2 ? b[2] + (b[3] - b[2]) * u : k === 0 ? b[2] - 0.5 : b[3] + 0.5; }
        else if (r < 0.85) { const k = (R() * 4) | 0, u = (R() * 2 - 1) * (A - 2); x = k < 2 ? u : (k === 2 ? -1 : 1) * (A - 1.1); z = k >= 2 ? u : (k === 0 ? -1 : 1) * (A - 1.1); }
        else if (rects.length) { const b = rects[(R() * rects.length) | 0]; if (b[5] > 2.2 || b[1] - b[0] < 1.6 || b[3] - b[2] < 1.6) continue; y = b[5]; x = b[0] + 0.5 + R() * (b[1] - b[0] - 1); z = b[2] + 0.5 + R() * (b[3] - b[2] - 1); }
        else continue;
        if (!free(x, z, y)) continue; got.push([x, z]); K.cone(x, y, z);
        for (let k = 0, n = R() < 0.45 ? 1 : R() < 0.5 ? 2 : 0; k < n && got.length < want; k++) { const a = R() * 6.2832, x2 = x + Math.cos(a) * 0.9, z2 = z + Math.sin(a) * 0.9; if (free(x2, z2, y)) { got.push([x2, z2]); K.cone(x2, y, z2); } }
      }
    },
  };
}
// a fall of slime: a sheet over the lip, out and down to the pool (u across it, v from the lip to the bottom)
function slimeFallGeo(f) {
  const nu = 18, nv = 22, pos = [], uv = [], idx = [];
  for (let j = 0; j <= nv; j++) { const v = j / nv, out = 0.35 + 2.0 * Math.sqrt(v) - 0.2 * v, y = f.y0 + 0.08 - (f.y0 - WATER_Y + 0.05) * v * v * (1.05 - 0.05 * v) - 0.05 * v;
    for (let i = 0; i <= nu; i++) { const u = i / nu - 0.5, w = f.w * (1 + 0.25 * v) * u, bulge = 0.12 * Math.cos(u * Math.PI) * (1 - v);
      pos.push(f.x + f.nx * (out + bulge) + f.tx * w, y, f.z + f.nz * (out + bulge) + f.tz * w); uv.push(i / nu, v); } }
  for (let j = 0; j < nv; j++) for (let i = 0; i < nu; i++) { const a = j * (nu + 1) + i, b = a + 1, c = a + nu + 1, d = c + 1; idx.push(a, c, b, b, c, d); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
const SLIME_FALL_MAT = new THREE.ShaderMaterial({ uniforms: Object.assign(THREE.UniformsUtils.clone(THREE.UniformsLib.fog), { uTime: { value: 0 }, uK: { value: HI ? 1.6 : 1.1 } }), fog: true, side: THREE.DoubleSide,
  vertexShader: `varying vec2 vUv;
  #include <fog_pars_vertex>
  void main(){ vUv = uv; vec4 mvPosition = modelViewMatrix * vec4(position, 1.0); gl_Position = projectionMatrix * mvPosition;
  #include <fog_vertex>
  }`,
  fragmentShader: `uniform float uTime, uK; varying vec2 vUv;
  #include <fog_pars_fragment>
  float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(h2(i), h2(i + vec2(1.0, 0.0)), f.x), mix(h2(i + vec2(0.0, 1.0)), h2(i + vec2(1.0, 1.0)), f.x), f.y); }
  void main(){
    float u = vUv.x, v = vUv.y, t = uTime;
    float s1 = vn(vec2(u * 11.0, v * 3.2 - t * 1.7)), s2 = vn(vec2(u * 27.0 + 3.0, v * 6.0 - t * 2.6)), streak = s1 * 0.65 + s2 * 0.35;
    vec3 deep = vec3(0.14, 0.52, 0.05), hot = vec3(0.62, 1.25, 0.22), col = mix(deep, hot, smoothstep(0.25, 0.85, streak));
    float edge = smoothstep(0.0, 0.12, u) * smoothstep(1.0, 0.88, u); col *= 0.55 + 0.45 * edge;
    col = mix(col, vec3(0.85, 1.25, 0.6), smoothstep(0.1, 0.0, v) * 0.7 + smoothstep(0.8, 1.0, v) * 0.45 * vn(vec2(u * 18.0, t * 3.0)));
    gl_FragColor = vec4(col * uK, 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
  #include <fog_fragment>
  }` });
const SLIME_SPLASH_MAT = new THREE.ShaderMaterial({ uniforms: Object.assign(THREE.UniformsUtils.clone(THREE.UniformsLib.fog), { uTime: { value: 0 }, uK: { value: HI ? 1.5 : 1.05 } }), fog: true, transparent: true, depthWrite: false,
  vertexShader: `varying vec2 vUv;
  #include <fog_pars_vertex>
  void main(){ vUv = uv; vec4 mvPosition = modelViewMatrix * vec4(position, 1.0); gl_Position = projectionMatrix * mvPosition;
  #include <fog_vertex>
  }`,
  fragmentShader: `uniform float uTime, uK; varying vec2 vUv;
  #include <fog_pars_fragment>
  float h2(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float vn(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(h2(i), h2(i + vec2(1.0, 0.0)), f.x), mix(h2(i + vec2(0.0, 1.0)), h2(i + vec2(1.0, 1.0)), f.x), f.y); }
  void main(){
    vec2 p = vUv - 0.5; float r = length(p) * 2.0, a = atan(p.y, p.x), t = uTime;
    float rip = 0.5 + 0.5 * sin(r * 22.0 - t * 5.0), froth = vn(vec2(a * 4.0, r * 6.0 - t * 2.0)) * vn(vec2(a * 9.0 + 2.0, r * 11.0 - t * 3.0));
    float al = smoothstep(1.0, 0.55, r) * (0.35 + 0.4 * rip * smoothstep(0.2, 0.6, r) + 0.6 * smoothstep(0.35, 0.7, froth) * smoothstep(0.85, 0.1, r));
    gl_FragColor = vec4(vec3(0.7, 1.15, 0.45) * uK, al);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
  #include <fog_fragment>
  }` });
// the sewer's floor markings: a hazard roundel with the biohazard sign big in it, paint worn through to the steel
function sewerDecal(g, S, c, r) {
  g.lineCap = 'butt'; for (let k = 0; k < 28; k++) { g.strokeStyle = k % 2 ? 'rgba(22,24,22,0.86)' : 'rgba(236,176,30,0.92)'; g.lineWidth = 30; g.beginPath(); g.arc(c, c, 214, k / 28 * 6.2832, (k + 1) / 28 * 6.2832); g.stroke(); }
  g.strokeStyle = 'rgba(236,176,30,0.85)'; g.lineWidth = 7; g.beginPath(); g.arc(c, c, 184, 0, 6.2832); g.stroke();
  g.fillStyle = 'rgba(236,176,30,0.9)'; for (let k = 0; k < 3; k++) { const a = k * 2.0944 - 1.5708; g.beginPath(); g.arc(c + Math.cos(a) * 66, c + Math.sin(a) * 66, 58, 0, 6.2832); g.fill(); }
  g.globalCompositeOperation = 'destination-out'; for (let k = 0; k < 3; k++) { const a = k * 2.0944 - 1.5708; g.beginPath(); g.arc(c + Math.cos(a) * 86, c + Math.sin(a) * 86, 36, 0, 6.2832); g.fill(); } g.beginPath(); g.arc(c, c, 20, 0, 6.2832); g.fill(); g.globalCompositeOperation = 'source-over';
  g.strokeStyle = 'rgba(236,176,30,0.9)'; g.lineWidth = 13; g.beginPath(); g.arc(c, c, 50, 0, 6.2832); g.stroke(); g.fillStyle = 'rgba(236,176,30,0.9)'; g.beginPath(); g.arc(c, c, 13, 0, 6.2832); g.fill();
  g.globalCompositeOperation = 'destination-out'; for (let k = 0; k < 900; k++) { g.fillStyle = `rgba(0,0,0,${0.25 + r() * 0.6})`; g.beginPath(); g.ellipse(r() * S, r() * S, 1 + r() * 5, 1 + r() * 3, r() * 3, 0, 6.2832); g.fill(); }
  for (let k = 0; k < 40; k++) { g.strokeStyle = 'rgba(0,0,0,0.7)'; g.lineWidth = 1 + r() * 2; const x = r() * S, y = r() * S, a = r() * 6.28; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * (20 + r() * 80), y + Math.sin(a) * (20 + r() * 80)); g.stroke(); } g.globalCompositeOperation = 'source-over';
}
// the sewer's scattered markings: a manhole cover, a splat of slime, a floor grate, KEEP OUT stenciled in yellow
function sewerScatter(cell, g, r, H) {
  cell(0, () => { g.fillStyle = 'rgba(16,18,16,0.6)'; g.beginPath(); g.arc(6, 8, 206, 0, 6.2832); g.fill(); const gr = g.createRadialGradient(0, 0, 0, 0, 0, 200); gr.addColorStop(0, 'rgba(84,90,86,0.98)'); gr.addColorStop(1, 'rgba(48,52,50,0.98)'); g.fillStyle = gr; g.beginPath(); g.arc(0, 0, 200, 0, 6.2832); g.fill();
    g.strokeStyle = 'rgba(24,28,26,0.9)'; for (const [rr, lw] of [[188, 8], [150, 5], [80, 5]]) { g.lineWidth = lw; g.beginPath(); g.arc(0, 0, rr, 0, 6.2832); g.stroke(); }
    g.fillStyle = 'rgba(120,126,120,0.7)'; for (let a = 0; a < 6.28; a += 0.21) for (const rr of [170, 118]) { g.save(); g.rotate(a); g.fillRect(rr - 9, -4, 18, 8); g.restore(); } for (let k = -4; k <= 4; k++) g.fillRect(-60, k * 13 - 3, 120, 6);
    for (let k = 0; k < 24; k++) { const a = r() * 6.28, d = r() * 180; g.fillStyle = `rgba(${120 + r() * 40 | 0},62,28,${0.2 + r() * 0.3})`; g.beginPath(); g.arc(Math.cos(a) * d, Math.sin(a) * d, 6 + r() * 20, 0, 6.2832); g.fill(); } });
  cell(1, () => { const blobs = [[0, 0, 120]]; for (let k = 0; k < 9; k++) { const a = r() * 6.28, d = 110 + r() * 90; blobs.push([Math.cos(a) * d, Math.sin(a) * d, 12 + r() * 30]); }
    for (const [x, y, rr] of blobs) { polyAt(g, lumpy(r, rr * 1.12, rr * 1.0, 12), x, y, r() * 6); g.fillStyle = 'rgba(40,96,20,0.6)'; g.fill(); }
    for (const [x, y, rr] of blobs) { polyAt(g, lumpy(r, rr, rr * 0.9, 12), x, y, r() * 6); const gr = g.createRadialGradient(x - rr * 0.2, y - rr * 0.2, 0, x, y, rr); gr.addColorStop(0, 'rgba(206,255,120,0.98)'); gr.addColorStop(0.6, 'rgba(126,230,54,0.97)'); gr.addColorStop(1, 'rgba(72,170,30,0.95)'); g.fillStyle = gr; g.fill(); }
    for (let k = 0; k < 14; k++) { const a = r() * 6.28, d = r() * 90; g.strokeStyle = 'rgba(230,255,190,0.6)'; g.lineWidth = 3; g.beginPath(); g.arc(Math.cos(a) * d, Math.sin(a) * d, 5 + r() * 9, 0, 6.2832); g.stroke(); } });
  cell(2, () => { g.fillStyle = 'rgba(14,16,14,0.55)'; g.fillRect(-176, -116, 360, 240); g.fillStyle = 'rgba(56,62,58,0.98)'; g.fillRect(-180, -120, 360, 240); g.fillStyle = 'rgba(8,10,8,0.98)'; for (let k = 0; k < 11; k++) g.fillRect(-160 + k * 29.5, -100, 16, 200);
    g.fillStyle = 'rgba(110,232,60,0.55)'; for (let k = 0; k < 11; k++) if (r() < 0.5) g.fillRect(-158 + k * 29.5, 40 + r() * 40, 12, 20 + r() * 30); g.strokeStyle = 'rgba(110,116,110,0.8)'; g.lineWidth = 6; g.strokeRect(-180, -120, 360, 240); });
  cell(3, () => { g.fillStyle = 'rgba(236,176,30,0.9)'; g.font = 'bold 86px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('KEEP', 0, -60); g.fillText('OUT', 0, 40);
    g.strokeStyle = 'rgba(236,176,30,0.9)'; g.lineWidth = 16; for (const y of [-150, 140]) { g.beginPath(); g.moveTo(-180, y); g.lineTo(180, y); g.stroke(); }
    g.globalCompositeOperation = 'destination-out'; for (let k = 0; k < 400; k++) { g.fillStyle = `rgba(0,0,0,${0.3 + r() * 0.6})`; g.beginPath(); g.arc((r() - 0.5) * 480, (r() - 0.5) * 480, 1 + r() * 4, 0, 6.2832); g.fill(); } for (const x of [-120, -40, 40, 120]) g.fillRect(x - 3, -110, 6, 30); g.globalCompositeOperation = 'source-over'; });
}
