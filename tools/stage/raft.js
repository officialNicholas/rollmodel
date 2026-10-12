// ---------- the Fishing Raft: a big plank raft out on open water, crates under nets and strings of floats, cable spools, barrels, tires on
// its sides, cargo lifted by bunches of buoys, and round it a mast with a pennant, a crane with a lobster trap, a bait shack, a fish on a pole ----------
const RAFT_SIGNS = makeTex(512, (g, S) => {
  const c = S / 4; g.clearRect(0, 0, S, S); g.textAlign = 'center'; g.textBaseline = 'middle'; g.lineJoin = 'round'; g.lineCap = 'round';
  const fish = (x, y, s, col, rot) => { g.save(); g.translate(x, y); g.rotate(rot || 0); g.fillStyle = col; g.beginPath(); g.moveTo(-s, 0); g.bezierCurveTo(-s * 0.5, -s * 0.62, s * 0.45, -s * 0.55, s * 0.62, 0); g.bezierCurveTo(s * 0.45, s * 0.55, -s * 0.5, s * 0.62, -s, 0); g.fill();
    g.beginPath(); g.moveTo(s * 0.5, 0); g.lineTo(s * 1.02, -s * 0.42); g.lineTo(s * 0.9, 0); g.lineTo(s * 1.02, s * 0.42); g.closePath(); g.fill(); g.globalCompositeOperation = 'destination-out'; g.beginPath(); g.arc(-s * 0.58, -s * 0.08, s * 0.1, 0, 6.2832); g.fill(); g.lineWidth = s * 0.06; g.beginPath(); g.arc(-s * 0.38, 0, s * 0.3, -1, 1); g.stroke(); g.globalCompositeOperation = 'source-over'; g.restore(); };
  // 0: the spool's emblem: a teal fish in a ring, paint worn
  g.strokeStyle = '#2FA59A'; g.lineWidth = 16; g.beginPath(); g.arc(c, c, c * 0.84, 0, 6.2832); g.stroke(); g.lineWidth = 5; g.beginPath(); g.arc(c, c, c * 0.68, 0, 6.2832); g.stroke(); fish(c, c, c * 0.52, '#2FA59A', 0);
  // 1: the ramps' chevrons, pointing up the slope
  g.strokeStyle = '#2FA59A'; g.lineWidth = 26; for (const dy of [-36, 30]) { g.beginPath(); g.moveTo(3 * c - 70, c + 36 + dy); g.lineTo(3 * c, c - 30 + dy); g.lineTo(3 * c + 70, c + 36 + dy); g.stroke(); }
  // 2: the shack's board: BAIT & TACKLE, white on blue, a hook
  g.fillStyle = '#2E5E8E'; g.fillRect(10, 2 * c + 50, 2 * c - 20, c * 2 - 100); g.strokeStyle = '#F2EEE2'; g.lineWidth = 6; g.strokeRect(20, 2 * c + 60, 2 * c - 40, c * 2 - 120); g.fillStyle = '#F2EEE2'; g.font = 'bold 44px sans-serif'; g.fillText('BAIT &', c, 3 * c - 22); g.fillText('TACKLE', c, 3 * c + 26);
  // 3: FRESH FISH, with a red fish
  g.fillStyle = '#F2EEE2'; g.fillRect(2 * c + 10, 2 * c + 40, 2 * c - 20, 2 * c - 80); g.strokeStyle = '#B83228'; g.lineWidth = 6; g.strokeRect(2 * c + 18, 2 * c + 48, 2 * c - 36, 2 * c - 96); g.fillStyle = '#B83228'; g.font = 'bold 38px sans-serif'; g.fillText('FRESH', 3 * c, 2 * c + 92); g.fillText('FISH', 3 * c, 2 * c + 134); fish(3 * c, 3 * c + 56, 50, '#2E6FB8', 0);
  const r = rng(631); for (let k = 0; k < 500; k++) { g.globalCompositeOperation = 'destination-out'; g.fillStyle = `rgba(0,0,0,${0.2 + r() * 0.5})`; g.beginPath(); g.arc(r() * S, r() * S, 0.8 + r() * 3, 0, 6.2832); g.fill(); } g.globalCompositeOperation = 'source-over';
});
// a fishing net: rope diamonds with knots where they cross, on nothing
const RAFT_NET = makeTex(256, (g, S) => {
  g.clearRect(0, 0, S, S); const n = 8, p = S / n; g.strokeStyle = 'rgba(232,214,170,1)'; g.lineWidth = 3.2; g.lineCap = 'round';
  for (let k = -n; k <= 2 * n; k++) { g.beginPath(); g.moveTo(k * p, 0); g.lineTo(k * p + S, S); g.stroke(); g.beginPath(); g.moveTo(k * p, 0); g.lineTo(k * p - S, S); g.stroke(); }
  g.fillStyle = 'rgba(210,186,140,1)'; for (let i = 0; i <= n; i++) for (let j = 0; j <= n; j++) { g.beginPath(); g.arc(i * p, j * p, 3.6, 0, 6.2832); g.fill(); g.beginPath(); g.arc((i + 0.5) * p, (j + 0.5) * p, 3.6, 0, 6.2832); g.fill(); }
});
// the deck's own clutter, painted flat on it (a 2 x 2 atlas): a coil of rope, a hatch, a fishing net spread out, a wet patch with a fish
const RAFT_DECK = makeTex(512, (g, S) => {
  const h = S / 2, R = rng(719); g.clearRect(0, 0, S, S); g.lineCap = 'round'; g.lineJoin = 'round';
  { const cx = h / 2, cy = h / 2; for (let k = 0; k < 7; k++) { const r = 18 + k * 13; g.strokeStyle = 'rgba(70,46,22,0.92)'; g.lineWidth = 13; g.beginPath(); g.arc(cx, cy, r, 0, 6.2832); g.stroke(); g.strokeStyle = '#D9B47A'; g.lineWidth = 9; g.beginPath(); g.arc(cx, cy, r, 0, 6.2832); g.stroke();
      g.strokeStyle = 'rgba(120,84,40,0.8)'; g.lineWidth = 1.5; for (let a = 0; a < 6.28; a += 0.2) { g.beginPath(); g.moveTo(cx + Math.cos(a) * (r - 4), cy + Math.sin(a) * (r - 4)); g.lineTo(cx + Math.cos(a + 0.12) * (r + 4), cy + Math.sin(a + 0.12) * (r + 4)); g.stroke(); } }
    g.beginPath(); g.moveTo(cx + 96, cy); g.quadraticCurveTo(cx + 116, cy + 60, cx + 66, cy + 112); g.strokeStyle = 'rgba(70,46,22,0.92)'; g.lineWidth = 13; g.stroke(); g.strokeStyle = '#D9B47A'; g.lineWidth = 9; g.stroke(); }
  { const x0 = h + 34, y0 = 34, w = h - 68; g.fillStyle = '#4E3220'; g.fillRect(x0 - 7, y0 - 7, w + 14, w + 14); for (let k = 0; k < 5; k++) { g.fillStyle = k % 2 ? '#9A6A3C' : '#8A5E34'; g.fillRect(x0, y0 + k * w / 5 + 1.5, w, w / 5 - 3); }
    g.strokeStyle = '#2A2A2A'; g.lineWidth = 7; g.beginPath(); g.arc(x0 + w / 2, y0 + w / 2, 18, 0, 6.2832); g.stroke(); g.fillStyle = '#3A3A3A'; for (const yy of [y0 + 18, y0 + w - 32]) g.fillRect(x0 - 9, yy, 36, 14); }
  { const x0 = 20, y0 = h + 20, w = h - 40; g.save(); g.beginPath(); g.ellipse(x0 + w / 2, y0 + w / 2, w / 2, w / 2.6, 0.3, 0, 6.2832); g.clip(); g.strokeStyle = 'rgba(36,50,46,0.85)'; g.lineWidth = 2.4;
    for (let k = -w; k < 2 * w; k += 17) { g.beginPath(); g.moveTo(x0 + k, y0); g.lineTo(x0 + k + w, y0 + w); g.stroke(); g.beginPath(); g.moveTo(x0 + k + w, y0); g.lineTo(x0 + k, y0 + w); g.stroke(); } g.restore();
    for (let k = 0; k < 6; k++) { const a = -0.9 + k * 0.36, x = x0 + w / 2 + Math.cos(a) * w * 0.47, y = y0 + w / 2 + Math.sin(a) * w * 0.38; g.fillStyle = '#F2771E'; g.beginPath(); g.ellipse(x, y, 10, 6.5, a, 0, 6.2832); g.fill(); } }
  { const cx = h + h / 2, cy = h + h / 2; g.fillStyle = 'rgba(56,36,20,0.42)'; polyAt(g, lumpy(R, 95, 70, 16), cx, cy, 0.4); g.fill(); g.fillStyle = 'rgba(255,255,255,0.14)'; polyAt(g, lumpy(R, 40, 22, 12), cx - 30, cy - 20, 0.4); g.fill();
    g.save(); g.translate(cx + 10, cy + 6); g.rotate(-0.5); g.fillStyle = '#7FA8C0'; g.beginPath(); g.ellipse(0, 0, 46, 17, 0, 0, 6.2832); g.fill(); g.beginPath(); g.moveTo(40, 0); g.lineTo(66, -18); g.lineTo(66, 18); g.closePath(); g.fill();
    g.fillStyle = '#DCE8EE'; g.beginPath(); g.ellipse(-4, 6, 34, 7, 0, 0, 6.2832); g.fill(); g.fillStyle = '#1A1A1A'; g.beginPath(); g.arc(-30, -4, 3.6, 0, 6.2832); g.fill(); g.restore(); }
});
function raftMats(M, T) {
  const mk = (c, extra, pbr) => aoPatch(toon(c, extra, pbr)), co = surf('corrugated');
  const pb = (s, n, ro) => HI ? (s.normalMap ? { normalMap: s.normalMap, normalScale: new THREE.Vector2(n, n), roughnessMap: s.roughnessMap, roughness: ro || 1 } : { roughness: 0.6 }) : null;
  M.corr = mk(0xFFFFFF, { map: co.map }, pb(co, 1.4, 1)); M.rampTop = M.corr; M.deckDecal = decalOf(RAFT_DECK);
  M.net = mk(0xFFFFFF, { map: RAFT_NET, alphaTest: 0.45, side: THREE.DoubleSide }, { roughness: 0.85 }); RAFT_NET.repeat.set(1, 1);
  M.vc = mk(0xFFFFFF, { vertexColors: true }, { roughness: 0.5 }); M.vcWood = mk(0xFFFFFF, { map: woodTex, vertexColors: true }, { roughness: 0.82 }); M.vcMetal = mk(0xFFFFFF, { vertexColors: true }, { roughness: 0.36, metalness: 0.65 });
  M.glowVC = new THREE.MeshBasicMaterial({ vertexColors: true }); M.vcFlag = mk(0xFFFFFF, { vertexColors: true, side: THREE.DoubleSide }, { roughness: 0.7 }); M.sign = mk(0xFFFFFF, { map: RAFT_SIGNS, alphaTest: 0.5, side: THREE.DoubleSide }, { roughness: 0.6 });
}
function raftDress(K) {
  const { M, R, put, us } = K, vc = K.vc, V = SG.V, A = K.ARENA, C = hexC;
  const WL = C(0xC89A62), WM = C(0xA87444), WD = C(0x6A4528), RO = C(0xD6AE72), OR = C(0xF2771E), WH = C(0xF4F1EA), RD = C(0xD8352A), BL = C(0x2E6FC8), TL = C(0x2FA59A), RB = C(0x262626), MT = C(0x8A949A), YL = C(0xF2C230), GY = C(0xB8C0C6);
  const wood = (g, col) => vc(M.vcWood, uvXY(g, (x, y, z) => [x * 1.3 + z * 0.7, y * 1.3 + z * 0.3]), col);
  const rope = (a, b, s, r) => vc(M.vc, SG.sag(a, b, s, r || 0.025), RO);
  // a fishing float: white over orange (or red), a little eye on top
  const buoy = (x, y, z, s, col) => { s = s || 1; vc(M.vc, SG.ball(0.13 * s, x, y, z, 1, 1.35, 1), (px, py) => py > y + 0.01 * s ? WH : (col || OR)); vc(M.vc, SG.cyl(0.02 * s, 0.02 * s, 0.06 * s, 6, x, y + 0.19 * s, z), RO); };
  const barrel = (x, y, z, col, lay, ry) => { const parts = [[SG.cyl(0.26, 0.26, 0.66, 20, 0, 0, 0), (px, py, pz) => { const a = Math.atan2(pz, px), f = ((a / 6.2832 * 14) % 1 + 1) % 1; return SG.shade(col, f < 0.06 ? 0.72 : 0.9 + 0.12 * Math.sin(a * 7)); }], [SG.torus(0.268, 0.02, 0, 0.22, 0, Math.PI / 2, 0, 22), MT], [SG.torus(0.268, 0.02, 0, -0.22, 0, Math.PI / 2, 0, 22), MT], [SG.cyl(0.25, 0.25, 0.01, 20, 0, 0.332, 0), SG.shade(col, 0.75)]];
    for (const [g, c] of parts) { if (lay) g.rotateZ(Math.PI / 2); if (ry) g.rotateY(ry); g.translate(x, y, z); vc(M.vc, g, c); } };
  const tire = (x, y, z, nx, nz, s) => { s = s || 1; const g = SG.torus(0.36 * s, 0.13 * s, 0, 0, 0, 0, 0, 26); alignZ(g, V(nx, 0, nz), V(x, y, z)); vc(M.vc, g, (px, py, pz) => SG.shade(RB, 0.85 + 0.3 * (Math.sin(Math.atan2(py - y, (pz - z) * nx - (px - x) * nz) * 30) > 0.6 ? 1 : 0))); };
  const ring = (x, y, z, nx, nz) => { const g = SG.torus(0.3, 0.075, 0, 0, 0, 0, 0, 28); alignZ(g, V(nx, 0, nz), V(x, y, z)); vc(M.vc, g, (px, py, pz) => { const a = Math.atan2(py - y, (px - x) * nz - (pz - z) * nx); return ((a / 1.5708 + 4.5) | 0) % 2 ? RD : WH; }); };
  const lantern = (x, y, z) => { vc(M.vcMetal, SG.cyl(0.07, 0.09, 0.05, 10, x, y + 0.16, z), WD); vc(M.vcMetal, SG.torus(0.05, 0.008, x, y + 0.24, z, 0, 0, 10), WD); vc(M.glowVC, SG.cyl(0.07, 0.07, 0.2, 10, x, y + 0.03, z), C(0xFFD08A).multiplyScalar(HI ? 2 : 1.2)); for (let a = 0; a < 6.28; a += 1.5708) vc(M.vcMetal, SG.box(0.014, 0.22, 0.014, x + Math.cos(a) * 0.075, y + 0.03, z + Math.sin(a) * 0.075), WD); vc(M.vcMetal, SG.cyl(0.09, 0.07, 0.04, 10, x, y - 0.09, z), WD); K.glow(x, y + 0.03, z, 0.7, 0xFFC070); };
  const coil = (x, y, z, n, rr) => { for (let k = 0; k < n; k++) { const g = ropeRing(rr - k * 0.02, 0.035, 5); g.translate(x, y + 0.035 + k * 0.06, z); vc(M.vc, g, null); } };
  const fish = (x, y, z, s, ry, col) => { const parts = [[SG.ball(0.5, 0, 0, 0, 1, 0.42, 0.24), (px, py) => py > 0.02 * s ? (col || C(0x6E8AA6)) : C(0xDDE4E8)], [new THREE.ConeGeometry(0.18, 0.3, 4).rotateZ(-Math.PI / 2).scale(1, 1, 0.25).translate(0.58, 0, 0), col || C(0x6E8AA6)], [SG.ball(0.045, -0.36, 0.05, 0.1), C(0x111111)], [SG.ball(0.045, -0.36, 0.05, -0.1), C(0x111111)]];
    for (const [g, c] of parts) { g.scale(s, s, s); g.rotateY(ry || 0); g.translate(x, y, z); vc(M.vc, g, c); } };
  const gull = (x, y, z, ry) => { const P2 = [[SG.ball(0.13, 0, 0.13, 0, 1.5, 0.95, 0.95), WH], [SG.ball(0.075, -0.17, 0.25, 0), WH], [new THREE.ConeGeometry(0.022, 0.09, 6).rotateZ(Math.PI / 2).translate(-0.27, 0.24, 0), YL], [SG.ball(0.12, 0.03, 0.17, 0.07, 1.6, 0.4, 0.5), GY], [SG.ball(0.12, 0.03, 0.17, -0.07, 1.6, 0.4, 0.5), GY], [new THREE.ConeGeometry(0.06, 0.16, 5).rotateZ(-Math.PI / 2).scale(1, 0.4, 1).translate(0.24, 0.16, 0), C(0x3A3E44)], [SG.ball(0.014, -0.215, 0.27, 0.045), C(0x111111)], [SG.ball(0.014, -0.215, 0.27, -0.045), C(0x111111)], [SG.cyl(0.008, 0.008, 0.1, 5, 0, 0.03, 0.04), OR], [SG.cyl(0.008, 0.008, 0.1, 5, 0, 0.03, -0.04), OR]];
    for (const [g, c] of P2) { g.rotateY(ry || 0); g.translate(x, y, z); vc(M.vc, g, c); } };
  // a net draped over a top: a sagging, rumpled grid; it can spill over one edge and hang down that face
  const netOver = (x0, x1, z0, z1, y, flap) => { const nu = 12, nv = 12, F = flap ? 0.42 : 0, g = gridGeo(nu, nv, (u, v, o) => { let x = x0 + (x1 - x0) * u, z = z0 + (z1 - z0) * v, yy = y + 0.025 + 0.02 * Math.sin(u * 17 + v * 5) * Math.sin(v * 13); if (flap) { const t = flap === 'x0' ? 1 - u : flap === 'x1' ? u : flap === 'z0' ? 1 - v : v; if (t > 0.86) { const k = (t - 0.86) / 0.14, d = k * F; yy = y + 0.02 - d; if (flap === 'x0') x = x0 - 0.03; else if (flap === 'x1') x = x1 + 0.03; else if (flap === 'z0') z = z0 - 0.03; else z = z1 + 0.03; } } o.set(x, yy, z); }); uvXY(g, (x, yv, z) => [x * 1.6 + yv * 0.4, z * 1.6 + yv * 0.4]); put(M.net, g); return g; };
  const balloons = (cx, cz, y0, spread, n) => { const parts = [], cols = [OR, WH, RD, YL]; const top = V(cx, y0 + 2.0, cz);
    for (let k = 0; k < n; k++) { const a = k / n * 6.2832 + 0.4, bx = cx + Math.cos(a) * 0.28, bz = cz + Math.sin(a) * 0.28, by = y0 + 2.25 + (k % 2) * 0.22; parts.push([SG.ball(0.3, bx, by, bz, 1, 1.32, 1), (px, py) => py > by + 0.02 ? WH : cols[k % cols.length]]); parts.push([SG.tube(V(bx, by - 0.38, bz), top, 0.012, 5), RO]); }
    for (const [sx, sz] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) parts.push([SG.tube(V(cx + sx * spread[0], y0 + 0.02, cz + sz * spread[1]), top, 0.018, 5), RO]);
    parts.push([SG.torus(0.07, 0.015, top.x, top.y, top.z, Math.PI / 2, 0, 12), MT]);
    const m = new THREE.Mesh(vcGeo(parts), M.vc); m.castShadow = false; m.receiveShadow = true; K.add(m); const ph = R() * 6.28; K.anim({ tick(dt, t) { m.position.y = 0.035 * Math.sin(t * 1.4 + ph); m.rotation.y = 0.012 * Math.sin(t * 0.9 + ph); } }); };
  const tops = [];
  const crateS = (x, y, z, s, ry, mark) => { const hs = s / 2, parts = [[SG.box(s, s, s, 0, hs, 0), SG.shade(WL, 0.9 + 0.15 * R())]];
    for (const [ex, ez] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) parts.push([SG.box(0.07, s, 0.07, ex * (hs - 0.02), hs, ez * (hs - 0.02)), WD]);
    for (const yy of [0.04, s - 0.04]) { parts.push([SG.box(s + 0.02, 0.07, 0.07, 0, yy, hs - 0.02), WD], [SG.box(s + 0.02, 0.07, 0.07, 0, yy, -hs + 0.02), WD], [SG.box(0.07, 0.07, s + 0.02, hs - 0.02, yy, 0), WD], [SG.box(0.07, 0.07, s + 0.02, -hs + 0.02, yy, 0), WD]); }
    for (const [ex, ez] of [[1, 1], [1, -1], [-1, 1], [-1, -1]]) parts.push([SG.box(0.1, 0.1, 0.1, ex * (hs - 0.01), s - 0.05, ez * (hs - 0.01)), C(0x3A3530)]);
    for (const [g, c] of parts) { g.rotateY(ry || 0); g.translate(x, y, z); wood(g, c); }
    if (mark) { const g = atlasUV(new THREE.PlaneGeometry(s * 0.7, s * 0.7), 0, 2); g.translate(0, hs, hs + 0.012); g.rotateY(ry || 0); g.translate(x, y, z); put(M.sign, g); } };
  // a cargo pontoon floating off the raft's side: a plank deck on drums, crates stacked on it under a net, barrels, a lantern, floats
  const pontoon2 = (x, z, ry) => { const c = Math.cos(ry), sn = Math.sin(ry), at2 = (u, v) => [x + u * c + v * sn, z - u * sn + v * c];
    { const g = SG.box(3.4, 0.22, 2.3, 0, -0.11, 0); g.rotateY(ry); g.translate(x, 0.02, z); wood(g, (px, py, pz) => SG.shade(WL, (((px * c - pz * sn) + 100) / 0.28 % 1) < 0.07 ? 0.62 : 0.95)); }
    for (const [u, v] of [[-1.2, -0.75], [1.2, -0.75], [-1.2, 0.75], [1.2, 0.75]]) { const [bx, bz] = at2(u, v); barrel(bx, -0.42, bz, [BL, RD, WH][(R() * 3) | 0], true, ry); }
    const [ax1, az1] = at2(-0.7, 0.1), [ax2, az2] = at2(0.25, 0.25), [ax3, az3] = at2(-0.65, 0.05); crateS(ax1, 0.02, az1, 0.9, ry, R() < 0.5); crateS(ax2, 0.02, az2, 0.75, ry + 0.2, false); crateS(ax3, 0.92, az3, 0.68, ry - 0.15, R() < 0.4);
    for (let k = 0; k < 2; k++) { const [bx, bz] = at2(1.0 + k * 0.1, -0.55 + k * 0.6); barrel(bx, 0.35, bz, [BL, RD, YL, TL][(R() * 4) | 0], false, R() * 6); }
    { const [lx, lz] = at2(1.4, 0.85); lanternPost(lx, 0.02, lz, x, z); } { const [cx2, cz2] = at2(0.5, -0.6); coil(cx2, 0.02, cz2, 3, 0.24); }
    for (const t of [-1.1, -0.35, 0.4, 1.15]) { const [bx, bz] = at2(t, 1.25); buoy(bx, -0.12, bz, 0.85, t > 0 ? OR : RD); } };
  const lanternPost = (x, y, z, cx, cz) => { const H = 0.85, dx = cx - x, dz = cz - z, dl = Math.hypot(dx, dz) || 1, ax = dx / dl * 0.2, az = dz / dl * 0.2;
    wood(SG.cyl(0.035, 0.045, H, 6, x, y + H / 2, z), WD); wood(SG.tube(V(x, y + H - 0.04, z), V(x + ax, y + H - 0.04, z + az), 0.022, 5), WD); lantern(x + ax, y + H - 0.36, z + az); K.light(x, 0.3 + y * 0.5, z, 2.4, 0xFFB050, 0.55); };
  const crateTop = (x, y, z, ry) => { const g = []; g.push([SG.box(0.62, 0.05, 0.42, 0, 0.025, 0), WM]); for (const [w, d, ox, oz] of [[0.62, 0.03, 0, 0.195], [0.62, 0.03, 0, -0.195], [0.03, 0.42, 0.295, 0], [0.03, 0.42, -0.295, 0]]) g.push([SG.box(w, 0.2, d, ox, 0.12, oz), WL]);
    for (const [gg, c] of g) { gg.rotateY(ry); gg.translate(x, y, z); wood(gg, c); } for (let k = 0; k < 3; k++) fish(x + (k - 1) * 0.16 * Math.cos(ry), y + 0.14 + k * 0.012, z - (k - 1) * 0.16 * Math.sin(ry), 0.36, ry + 1.5708 + (k - 1) * 0.3, [C(0x6E8AA6), C(0xC86A4A), C(0x7A9AAE)][k]); };
  const trap = (x, y, z, ry) => { const parts = []; parts.push([SG.box(0.7, 0.04, 0.45, 0, 0.02, 0), WM]); for (let k = 0; k <= 4; k++) { const a = Math.PI * k / 4; parts.push([new THREE.TorusGeometry(0.22, 0.008, 4, 16, Math.PI).translate(0, 0.04, 0).rotateY(Math.PI / 2).translate(-0.33 + k * 0.165, 0, 0), MT]); }
    for (let k = 0; k < 5; k++) { const a = Math.PI * (k + 0.5) / 5; parts.push([SG.tube(V(-0.33, 0.04 + Math.sin(a) * 0.22, Math.cos(a) * 0.22), V(0.33, 0.04 + Math.sin(a) * 0.22, Math.cos(a) * 0.22), 0.007, 4), MT]); }
    for (const [g, c] of parts) { g.rotateY(ry); g.translate(x, y, z); vc(M.vcMetal, g, c); } };
  return {
    rampTop: M.top,
    box(b, I) { // a cargo crate: corner posts, dark rims top and foot with iron brackets at the corners, and on its open faces floats,
      // rings, lanterns and the fish mark; up top a net, cargo you can knock off, coiled rope, a lantern on a post
      const { w, d, h, cx, cz } = I;
      for (const sx of [0, 1]) for (const sz of [0, 1]) wood(SG.box(0.11, h - 0.02, 0.11, (sx ? b[1] + 0.02 : b[0] - 0.02), h / 2, (sz ? b[3] + 0.02 : b[2] - 0.02)), WD);
      if (h >= 1.2) for (const [lx, lz, x, z] of [[w + 0.06, 0.05, cx, b[2] - 0.02], [w + 0.06, 0.05, cx, b[3] + 0.02], [0.05, d + 0.06, b[0] - 0.02, cz], [0.05, d + 0.06, b[1] + 0.02, cz]]) wood(SG.box(lx, 0.1, lz, x, h * 0.5, z), WD);
      const F = K.faces(b); let floats = 0;
      for (const f of F) {
        const L = f.L, rim = (y0, y1) => wood(SG.box(f.tx ? L + 0.04 : 0.05, y1 - y0, f.tz ? L + 0.04 : 0.05, f.fx + f.nx * 0.028, (y0 + y1) / 2, f.fz + f.nz * 0.028), WD);
        rim(h - 0.13, h - 0.01); rim(0.01, 0.13);
        for (const sd of [-1, 1]) { const u = sd * (L / 2 - 0.12), x = f.fx + f.tx * u + f.nx * 0.058, z = f.fz + f.tz * u + f.nz * 0.058; vc(M.vcMetal, SG.box(f.tx ? 0.22 : 0.012, 0.22, f.tz ? 0.22 : 0.012, x, h - 0.14, z), C(0x3A3530));
          for (const [du, dy] of [[-0.06, 0.06], [0.06, -0.06]]) vc(M.vcMetal, SG.ball(0.018, x + f.tx * du + f.nx * 0.01, h - 0.14 + dy, z + f.tz * du + f.nz * 0.01, 1, 1, 0.5), MT); }
        if (f.L >= 1.5 && floats < 2 && R() < 0.6) { floats++; // a string of floats along the top of the face
          const L2 = f.L - 0.3, y = h - 0.18, a = V(f.fx - f.tx * L2 / 2 + f.nx * 0.07, y, f.fz - f.tz * L2 / 2 + f.nz * 0.07), e = V(f.fx + f.tx * L2 / 2 + f.nx * 0.07, y, f.fz + f.tz * L2 / 2 + f.nz * 0.07), sag = 0.18;
          rope(a, e, sag); const n = Math.max(2, Math.round(L2 / 0.42)); for (let k = 1; k < n; k++) { const t = k / n, pp = V(a.x + (e.x - a.x) * t, y - sag * 4 * t * (1 - t), a.z + (e.z - a.z) * t); vc(M.vc, SG.cyl(0.008, 0.008, 0.12, 4, pp.x, pp.y - 0.06, pp.z), RO); buoy(pp.x, pp.y - 0.26, pp.z, 0.85, k % 3 ? OR : RD); } }
        if (h >= 1.0 && R() < 0.25) ring(f.fx + f.tx * (R() - 0.5) * (f.L - 0.8) + f.nx * 0.09, Math.min(h - 0.5, 0.92), f.fz + f.tz * (R() - 0.5) * (f.L - 0.8) + f.nz * 0.09, f.nx, f.nz);
        if (h >= 0.9 && f.L >= 1.2 && R() < 0.28) { const u = (R() - 0.5) * (f.L - 1.0), g = atlasUV(new THREE.PlaneGeometry(0.62, 0.62), 0, 2); g.rotateY(Math.atan2(f.nx, f.nz)); g.translate(f.fx + f.tx * u + f.nx * 0.03, Math.min(h * 0.5, 0.75), f.fz + f.tz * u + f.nz * 0.03); put(M.sign, g); }
        if (h >= 1.0 && R() < 0.32) { const u = (R() - 0.5) * (f.L - 0.6), x = f.fx + f.tx * u + f.nx * 0.2, z = f.fz + f.tz * u + f.nz * 0.2, y = Math.min(h - 0.24, 1.15); vc(M.vcMetal, SG.box(f.nx ? 0.22 : 0.03, 0.03, f.nx ? 0.03 : 0.22, x - f.nx * 0.1, y + 0.26, z - f.nz * 0.1), WD); lantern(x, y, z); K.light(x + f.nx * 0.5, 0.2, z + f.nz * 0.5, 2.2, 0xFFB050, 0.6); }
      }
      const corners = [[1, 1], [1, -1], [-1, 1], [-1, -1]].sort(() => R() - 0.5); let ci = 0; const cnr = () => { const [ix, iz] = corners[ci++ % 4]; return [cx + ix * (w / 2 - 0.38), cz + iz * (d / 2 - 0.38)]; };
      const free = F.map(f => f.nx === -1 ? 'x0' : f.nx === 1 ? 'x1' : f.nz === -1 ? 'z0' : 'z1');
      if (w >= 1.6 && d >= 1.6 && R() < 0.55) netOver(b[0] + 0.14, b[1] - 0.14, b[2] + 0.14, b[3] - 0.14, b[5], free.length && R() < 0.7 ? free[(R() * free.length) | 0] : null);
      if (w >= 1.3 && d >= 1.3) {
        if (R() < 0.7) { const [x, z] = cnr(); K.prop('barrel', x, b[5], z, [0x2E6FC8, 0xD8352A, 0x2FA59A, 0xF2C230][(R() * 4) | 0]); if (R() < 0.5) { const [x2, z2] = cnr(); K.prop('barrel', x2, b[5], z2, [0x2E6FC8, 0xD8352A][(R() * 2) | 0]); } }
        if (R() < 0.45) { const [x, z] = cnr(); K.prop('crate', x, b[5], z); }
        if (R() < 0.4) { const [x, z] = cnr(); coil(x, b[5], z, 3, 0.26); }
        if (R() < 0.2) { const [x, z] = cnr(); trap(x, b[5], z, R() * 3); }
        if (h >= 0.8 && R() < 0.6) { const [x, z] = cnr(); lanternPost(x, b[5], z, cx, cz); }
      }
    },
    float(b, I) { balloons(I.cx, I.cz, b[5], [I.w / 2 - 0.2, I.d / 2 - 0.2], I.w * I.d > 10 ? 5 : 4); },
    roundMats(b, kind) { return kind === 'rpad' ? [M.side, M.top, M.dark] : null; },
    skipBody(b, kind) { return kind === 'drum' || kind === 'column' || kind === 'rotunda'; },
    round(b, kind, cx, cz, rad, h, top) {
      const flange = (y, th, r, emblem) => { const g = SG.cyl(r, r, th, 48, cx, y, cz); wood(g, (px, py, pz) => { const f = (((px - cx) / 0.24 + 100) % 1); return py > y + th / 2 - 0.01 ? SG.shade(WL, f < 0.07 ? 0.62 : 0.92 + 0.12 * Math.sin((px - cx) * 7)) : WM; }); };
      if (kind === 'rotunda' || (kind === 'drum' && R() < 0.5)) { // a cable spool: plank flanges, dark cable wound on the drum between, bolts, the emblem on top of the big one
        const big = kind === 'rotunda', ft = big ? 0.16 : 0.1, core = rad - (big ? 0.3 : 0.24);
        flange(ft / 2, ft, rad); flange(top - ft / 2, ft, rad);
        wood(SG.cyl(core, core, h - 2 * ft, 40, cx, h / 2, cz), WD);
        for (let y = ft + 0.045; y < top - ft - 0.03; y += 0.085) vc(M.vc, SG.torus(core + 0.045, 0.048, cx, y, cz, Math.PI / 2, 0, 44), (px, py, pz) => SG.shade(C(0x2C2C30), 0.85 + 0.25 * Math.sin(Math.atan2(pz - cz, px - cx) * 9 + y * 40)));
        for (let k = 0; k < (big ? 16 : 8); k++) { const a = k / (big ? 16 : 8) * 6.2832; vc(M.vcMetal, SG.cyl(0.035, 0.035, 0.025, 8, cx + Math.cos(a) * (rad - 0.13), top + 0.012, cz + Math.sin(a) * (rad - 0.13)), MT); }
        if (big) { const g = atlasUV(new THREE.CircleGeometry(rad * 0.46, SEG(40)), 0, 2); g.rotateX(-Math.PI / 2); g.translate(cx, top + 0.008, cz); put(M.sign, g); }
        else vc(M.vc, new THREE.CircleGeometry(0.13, 16).rotateX(-Math.PI / 2).translate(cx, top + 0.006, cz), C(0x2A1C10));
      } else if (kind === 'drum' && R() < 0.5) { // tires stacked up, a round board on top
        const n = Math.max(2, Math.round((h - 0.05) / 0.3)), tr = Math.min(0.17, h / n / 2), R0 = rad - tr;
        for (let k = 0; k < n; k++) vc(M.vc, SG.torus(R0, tr, cx, tr + k * ((h - 0.05 - 2 * tr) / Math.max(1, n - 1)), cz, Math.PI / 2, 0, 36), (px, py, pz) => SG.shade(RB, 0.8 + 0.4 * (Math.sin(Math.atan2(pz - cz, px - cx) * 40) > 0.5 ? 1 : 0)));
        wood(SG.cyl(rad * 0.94, rad * 0.94, 0.05, 40, cx, top - 0.025, cz), (px, py, pz) => SG.shade(WL, ((px - cx) / 0.2 + 100) % 1 < 0.08 ? 0.62 : 1)); vc(M.vc, SG.cyl(R0 - tr * 0.6, R0 - tr * 0.6, h - 0.08, 24, cx, (h - 0.08) / 2, cz), C(0x141414));
      } else if (kind === 'drum') { // a giant coil of hawser, a board on top
        const n = Math.max(2, Math.round((h - 0.05) / 0.27)), sp = (h - 0.05 - 0.27) / (n - 1); for (let k = 0; k < n; k++) { const g = ropeRing(rad - 0.14, 0.135, 4); g.translate(cx, 0.135 + k * sp, cz); vc(M.vc, g, null); }
        wood(SG.cyl(rad * 0.92, rad * 0.92, 0.05, 40, cx, top - 0.025, cz), WL); vc(M.vc, SG.cyl(rad - 0.27, rad - 0.27, h - 0.06, 24, cx, (h - 0.06) / 2, cz), C(0x3A2A1A));
      } else if (kind === 'column' && R() < 0.5) { // a water tank: blue with its seams, a railing round the top, a ladder
        vc(M.vc, SG.cyl(rad, rad, h, 44, cx, h / 2, cz), (px, py) => SG.shade(BL, ((py / 0.62) % 1) < 0.05 ? 0.72 : 1)); vc(M.vc, SG.cyl(rad, rad, 0.02, 44, cx, top - 0.01, cz), SG.shade(BL, 1.15));
        vc(M.vcMetal, SG.cyl(0.08, 0.08, 0.3, 10, cx, top + 0.15, cz), WH); vc(M.vcMetal, SG.cyl(0.13, 0.13, 0.05, 10, cx, top + 0.32, cz), WH);
        const pts = []; for (let k = 0; k <= 14; k++) { const a = k / 14 * 6.2832; pts.push(V(cx + Math.cos(a) * (rad - 0.07), top, cz + Math.sin(a) * (rad - 0.07))); }
        for (let k = 0; k < 14; k++) vc(M.vcMetal, SG.cyl(0.02, 0.02, 0.5, 6, pts[k].x, top + 0.25, pts[k].z), WH); for (let k = 0; k < 14; k++) vc(M.vcMetal, SG.tube(V(pts[k].x, top + 0.5, pts[k].z), V(pts[k + 1].x, top + 0.5, pts[k + 1].z), 0.022, 6), WH);
        const a = R() * 6.28, nx = Math.cos(a), nz = Math.sin(a), lx = cx + nx * (rad + 0.1), lz = cz + nz * (rad + 0.1); for (const s of [-1, 1]) vc(M.vcMetal, SG.box(0.04, h + 0.5, 0.04, lx - nz * 0.22 * s, (h + 0.5) / 2, lz + nx * 0.22 * s), WH); for (let y = 0.3; y < h + 0.4; y += 0.3) vc(M.vcMetal, SG.tube(V(lx + nz * 0.22, y, lz - nx * 0.22), V(lx - nz * 0.22, y, lz + nx * 0.22), 0.016, 6), WH);
        K.hull(SG.cyl(rad + 0.07, rad + 0.07, h + 0.14, 44, cx, h / 2, cz));
      } else if (kind === 'column') { // three pilings lashed together, a gull on top
        const pr = rad * 0.5; for (let k = 0; k < 3; k++) { const a = k / 3 * 6.2832 + 0.3, x = cx + Math.cos(a) * rad * 0.5, z = cz + Math.sin(a) * rad * 0.5; wood(SG.cyl(pr, pr * 0.96, h, 20, x, h / 2, z), (px, py) => py > h - 0.005 ? SG.shade(WL, 1.05) : SG.shade(WM, 0.9 + 0.1 * Math.sin(py * 9 + k))); vc(M.vc, SG.cyl(pr * 0.6, pr * 0.6, 0.004, 16, x, top + 0.003, z), C(0x8A6038)); }
        for (const y of [0.55, h - 0.7]) { vc(M.vc, SG.torus(rad * 0.98, 0.05, cx, y, cz, Math.PI / 2, 0, 40), RO); vc(M.vc, SG.torus(rad * 0.98, 0.05, cx, y + 0.11, cz, Math.PI / 2, 0, 40), RO); }
        if (R() < 0.7) gull(cx + Math.cos(0.3) * rad * 0.5, top, cz + Math.sin(0.3) * rad * 0.5, R() * 6.28);
        K.hull(SG.cyl(rad + 0.07, rad + 0.07, h + 0.14, 44, cx, h / 2, cz));
      } else if (kind === 'rpad') balloons(cx, cz, top, [rad * 0.6, rad * 0.6], 4);
      if (kind === 'drum' || kind === 'rotunda') K.hull(SG.cyl(rad + 0.07, rad + 0.07, h + 0.14, 44, cx, h / 2, cz));
    },
    ramp(r, hf) { // a teal chevron painted up its slope
      const [x0, x1, z0, z1] = r, zr = r[4] === 'z', cx = (x0 + x1) / 2, cz = (z0 + z1) / 2, up = r[6] > r[5] ? 1 : -1, L = zr ? z1 - z0 : x1 - x0, rise = Math.abs(r[6] - r[5]);
      const fwd = (zr ? V(0, rise / L * up, up) : V(up, rise / L * up, 0)).normalize(), side = zr ? V(1, 0, 0) : V(0, 0, -1), nrm = new THREE.Vector3().crossVectors(side, fwd).normalize(); if (nrm.y < 0) { nrm.negate(); side.negate(); }
      const s = Math.min(1.5, (zr ? x1 - x0 : z1 - z0) * 0.72); for (const t of L > 2.6 ? [0.32, 0.68] : [0.5]) { const px = zr ? cx : x0 + (x1 - x0) * t, pz = zr ? z0 + (z1 - z0) * t : cz, g = atlasUV(new THREE.PlaneGeometry(s, s), 1, 2); g.applyMatrix4(new THREE.Matrix4().makeBasis(side, fwd, nrm)); g.translate(px + nrm.x * 0.012, hf(px, pz) + nrm.y * 0.012, pz + nrm.z * 0.012); put(M.sign, g); } },
    hole(hh) { if (hh[6] === 'c') return; const L = Math.min(hh[1] - hh[0], 2.2), x = (hh[0] + hh[1]) / 2, z = hh[2]; // a rope ladder down one side into the water
      for (const s of [-1, 1]) vc(M.vc, SG.tube(V(x + s * 0.25, 0.04, z + 0.04), V(x + s * 0.25, WATER_Y - 0.1, z + 0.12), 0.02, 5), RO); for (let y = -0.08; y > WATER_Y; y -= 0.16) wood(SG.box(0.56, 0.03, 0.07, x, y, z + 0.06 - y * 0.15), WM); },
    noPlinth: true,
    spot(x, z, i, corner, y) {
      const out = Math.atan2(x, z), ox = Math.sin(out), oz = Math.cos(out), sx = Math.cos(out), sz = -Math.sin(out), py = 0.08;
      { const ty = { 0: py + 7.2, 1: py + 4.9, 2: py + 3.3, 3: py + 2.7, 5: WATER_Y + 3.55, 7: WATER_Y + 3.0 }[i]; if (ty !== undefined) tops.push(V(x, ty, z)); }
      const pontoon = (w) => { w = w || 2.5; wood(SG.box(w, 0.2, w, x, py - 0.1, z), (px, pyy, pz) => SG.shade(WL, ((px + 100) / 0.26 % 1) < 0.08 ? 0.6 : 0.95)); for (const s1 of [-1, 1]) for (const s2 of [-1, 1]) barrel(x + s1 * w * 0.3, -0.45, z + s2 * w * 0.3, [BL, WH, RD][(i + s1 + s2 + 3) % 3], true, out); for (const s of [-0.55, 0.55]) tire(x - ox * (w / 2 + 0.1) + sx * s * w, -0.15, z - oz * (w / 2 + 0.1) + sz * s * w, -ox, -oz, 0.7); K.hull(SG.box(w + 0.1, 0.3, w + 0.1, x, py - 0.1, z)); };
      if (i === 0) { // the mast: a pennant flying from its top, a crow's nest, rigging down to the pontoon and across to the raft's corner
        pontoon(); const H2 = 8.2; wood(SG.cyl(0.15, 0.09, H2, 16, x, py + H2 / 2, z), WM); wood(alignZ(SG.cyl(0.06, 0.06, 2.6, 10, 0, 0, 0).rotateX(Math.PI / 2), V(sx, 0, sz), V(x, py + 6.4, z)), WM);
        vc(M.vcWood, SG.cyl(0.6, 0.6, 0.08, 24, x, py + 5.4, z), WM); vc(M.vc, SG.torus(0.6, 0.04, x, py + 5.85, z, Math.PI / 2, 0, 28), WD); for (let k = 0; k < 8; k++) { const a = k / 8 * 6.2832; vc(M.vc, SG.cyl(0.02, 0.02, 0.45, 5, x + Math.cos(a) * 0.6, py + 5.62, z + Math.sin(a) * 0.6), WD); }
        for (const [s1, s2] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) rope(V(x, py + 7.6, z), V(x + s1 * 1.15, py + 0.05, z + s2 * 1.15), 0.05, 0.018);
        rope(V(x, py + 7.0, z), V(Math.sign(x) * (A - 0.4), 0.9, Math.sign(z) * (A - 0.4)), 0.8, 0.02); lantern(x + sx * 0.25, py + 4.2, z + sz * 0.25);
        const flag = new THREE.Mesh(new THREE.PlaneGeometry(1.8, 0.62, 18, 4), new THREE.MeshStandardMaterial({ color: 0xD8352A, side: THREE.DoubleSide, roughness: 0.7 })); flag.userData.own = true; const fp = flag.geometry.attributes.position, base = Float32Array.from(fp.array);
        for (let k = 0; k < fp.count; k++) { const u = (base[k * 3] + 0.9) / 1.8; base[k * 3 + 1] *= 1 - 0.85 * u; base[k * 3] += 0.9; } fp.array.set(base); flag.position.set(x, py + H2 - 0.35, z); flag.rotation.y = Math.atan2(-sz, sx); K.add(flag);
        K.anim({ tick(dt, t) { for (let k = 0; k < fp.count; k++) { const u = base[k * 3] / 1.8; fp.array[k * 3 + 2] = Math.sin(u * 7 - t * 7.5) * 0.13 * u + Math.sin(u * 3 - t * 3) * 0.05 * u; fp.array[k * 3 + 1] = base[k * 3 + 1] - u * u * 0.08; } fp.needsUpdate = true; flag.geometry.computeVertexNormals(); } });
      } else if (i === 1) { // the crane: a post, a boom out over the water, a lobster trap on its rope, swinging; crates for weight
        pontoon(); const PH = 3.6; wood(SG.cyl(0.2, 0.22, PH, 14, x, py + PH / 2, z), WM); const tip = V(x + ox * 3.4, py + PH + 1.4, z + oz * 3.4), root = V(x - ox * 0.6, py + PH - 0.2, z - oz * 0.6);
        wood(SG.tube(root, tip, 0.11, 10), WM); wood(SG.tube(V(x, py + 1.6, z), V(x + ox * 1.6, py + PH + 0.55, z + oz * 1.6), 0.07, 8), WD); vc(M.vcMetal, alignZ(SG.cyl(0.2, 0.2, 0.08, 16, 0, 0, 0).rotateX(Math.PI / 2), V(sx, 0, sz), tip), MT);
        vc(M.vcMetal, alignZ(SG.cyl(0.18, 0.18, 0.42, 14, 0, 0, 0).rotateX(Math.PI / 2), V(sx, 0, sz), V(x - ox * 0.24, py + 1.0, z - oz * 0.24)), RO); rope(V(x - ox * 0.24, py + 1.0, z - oz * 0.24), tip, 0.02, 0.016);
        for (let k = 0; k < 2; k++) wood(SG.box(0.7, 0.45, 0.6, x - ox * 0.75 + sx * (k - 0.5) * 0.7, py + 0.225, z - oz * 0.75 + sz * (k - 0.5) * 0.7), WL);
        const hang = []; hang.push([SG.tube(V(0, 0, 0), V(0, -3.2, 0), 0.016, 5), RO]); const tg = []; tg.push([SG.box(0.8, 0.05, 0.52, 0, -3.95, 0), WM]); for (let k = 0; k <= 4; k++) tg.push([new THREE.TorusGeometry(0.26, 0.01, 4, 16, Math.PI).rotateY(Math.PI / 2).translate(-0.38 + k * 0.19, -3.92, 0), MT]); for (let k = 0; k < 5; k++) { const a = Math.PI * (k + 0.5) / 5; tg.push([SG.tube(V(-0.38, -3.92 + Math.sin(a) * 0.26, Math.cos(a) * 0.26), V(0.38, -3.92 + Math.sin(a) * 0.26, Math.cos(a) * 0.26), 0.008, 4), MT]); }
        for (const [a2, b2] of [[V(-0.36, -3.92, 0.2), V(0, -3.2, 0)], [V(0.36, -3.92, 0.2), V(0, -3.2, 0)], [V(-0.36, -3.92, -0.2), V(0, -3.2, 0)], [V(0.36, -3.92, -0.2), V(0, -3.2, 0)]]) tg.push([SG.tube(a2, b2, 0.01, 4), RO]);
        for (const p of [[0.1, -3.84, 0.05], [-0.15, -3.86, -0.08]]) tg.push([SG.ball(0.09, p[0], p[1], p[2], 1.6, 0.6, 0.8), C(0xC8402A)]);
        const tm = new THREE.Mesh(vcGeo([...hang, ...tg]), M.vcMetal); tm.position.copy(tip); tm.rotation.y = Math.atan2(-sz, sx); K.add(tm); K.anim({ tick(dt, t) { tm.rotation.z = 0.07 * Math.sin(t * 1.15); tm.rotation.x = 0.045 * Math.sin(t * 0.83 + 1.2); } });
      } else if (i === 2) { // the bait shack: plank walls, a corrugated roof, a striped awning facing the raft, a lit window, lanterns, a sign, nets hung up
        pontoon(2.8); const hw = 1.05, hd = 0.85, hh = 1.9; put(M.side, worldUV(SG.box(2 * hw, hh, 2 * hd, x, py + hh / 2, z), us)); K.hull(SG.box(2 * hw + 0.1, hh + 0.1, 2 * hd + 0.1, x, py + hh / 2, z));
        const roof = SG.box(2 * hw + 0.5, 0.08, 2 * hd + 0.6, 0, 0, 0).rotateX(0.18); SG.rotY(roof, out + Math.PI, 0, 0); put(M.corr, worldUV(roof.translate(x, py + hh + 0.12, z), 0.6));
        const fx = x - ox * (hd + 0.01), fz = z - oz * (hd + 0.01); vc(M.vcWood, alignZ(new THREE.BoxGeometry(0.6, 1.25, 0.05), V(-ox, 0, -oz), V(fx + sx * 0.4, py + 0.63, fz + sz * 0.4)), WD); vc(M.glowVC, alignZ(new THREE.PlaneGeometry(0.5, 0.42), V(-ox, 0, -oz), V(fx - sx * 0.45 - ox * 0.012, py + 1.1, fz - sz * 0.45 - oz * 0.012)), C(0xFFD08A).multiplyScalar(HI ? 1.8 : 1.1));
        for (const s of [-1, 1]) vc(M.vcWood, alignZ(new THREE.BoxGeometry(0.06, 0.52, 0.04), V(-ox, 0, -oz), V(fx - sx * 0.45 + sx * s * 0.27, py + 1.1, fz - sz * 0.45 + sz * s * 0.27)), WD);
        const aw = gridGeo(10, 1, (u, v, o) => { const t = u - 0.5; o.set(fx + sx * t * 2.2 - ox * v * 0.9, py + hh - 0.05 - v * 0.45, fz + sz * t * 2.2 - oz * v * 0.9); }); vc(M.vc, aw, (px, pyy, pz) => (Math.floor(((px - x) * sx + (pz - z) * sz + 2) / 0.275) % 2) ? TL : WH);
        const aw2 = gridGeo(10, 1, (u, v, o) => { const t = u - 0.5; o.set(fx + sx * t * 2.2 - ox * 0.9, py + hh - 0.5 - v * 0.15, fz + sz * t * 2.2 - oz * 0.9); }, true); vc(M.vc, aw2, (px, pyy, pz) => (Math.floor(((px - x) * sx + (pz - z) * sz + 2) / 0.275) % 2) ? TL : WH);
        for (const s of [-1, 1]) { vc(M.vcWood, SG.box(0.06, hh - 0.5, 0.06, fx + sx * s * 1.08 - ox * 0.9, py + (hh - 0.5) / 2, fz + sz * s * 1.08 - oz * 0.9), WD); lantern(fx + sx * s * 1.0 - ox * 0.86, py + hh - 0.82, fz + sz * s * 1.0 - oz * 0.86); }
        const sg = atlasUV(new THREE.PlaneGeometry(1.0, 0.62), 2, 2); sg.applyMatrix4(new THREE.Matrix4().makeBasis(V(-sx, 0, -sz), V(0, 1, 0), V(-ox, 0, -oz))); sg.translate(fx - ox * 0.02, py + hh - 0.25, fz - oz * 0.02); put(M.sign, sg);
        const ng = gridGeo(8, 6, (u, v, o) => { o.set(x + sx * (hw + 0.02), py + 1.7 - v * 1.2 + 0.08 * Math.sin(u * 9), z + sz * (hw + 0.02)); o.x += -ox * (u - 0.5) * 1.4; o.z += -oz * (u - 0.5) * 1.4; }); uvXY(ng, (px, pyy, pz) => [(px * ox + pz * oz) * 1.6, pyy * 1.6]); put(M.net, ng);
        barrel(x + sx * (hw + 0.45) - ox * 0.6, py + 0.33, z + sz * (hw + 0.45) - oz * 0.6, BL, false, 1); crateTop(x - sx * (hw + 0.4) - ox * 0.7, py, z - sz * (hw + 0.4) - oz * 0.7, out);
        K.light(fx - ox * 1.2, 0.3, fz - oz * 1.2, 2.6, 0xFFC070, 0.5); wood(SG.cyl(0.04, 0.05, 1.5, 8, x, py + hh + 0.85, z), WD); vc(M.vcFlag, (() => { const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0, 0, -0.42, 0, 0.7, -0.21, 0], 3)); g.computeVertexNormals(); g.rotateY(Math.atan2(-sz, sx)); return g.translate(x, py + hh + 1.58, z); })(), C(0x2FA59A));
      } else if (i === 3) { // a big fish on a pole, like a weathervane, gilled and finned
        pontoon(); wood(SG.cyl(0.11, 0.13, 2.6, 12, x, py + 1.3, z), WD); const fy = py + 2.95, ry = out + 0.6;
        const body = [[SG.ball(1.1, 0, 0, 0, 1, 0.42, 0.26), (px, pyy) => pyy > -0.05 ? SG.shade(C(0x7E96A8), 0.9 + 0.2 * Math.sin(px * 6)) : C(0xDDE6EA)], [new THREE.ConeGeometry(0.5, 0.6, 4).rotateZ(-Math.PI / 2).scale(1, 1.1, 0.2).translate(1.22, 0, 0), C(0x6A8496)], [new THREE.ConeGeometry(0.42, 0.5, 3).scale(1.2, 1, 0.12).translate(0.05, 0.5, 0), C(0x5E7A8C)],
          [SG.ball(0.12, -0.72, 0.1, 0.17, 1, 1, 0.5), WH], [SG.ball(0.07, -0.74, 0.1, 0.21, 1, 1, 0.5), C(0x111111)], [SG.ball(0.12, -0.72, 0.1, -0.17, 1, 1, 0.5), WH], [SG.ball(0.07, -0.74, 0.1, -0.21, 1, 1, 0.5), C(0x111111)], [SG.torus(0.3, 0.018, -0.45, 0, 0.21, 0, 0.3, 12), C(0x4E6878)], [SG.torus(0.3, 0.018, -0.45, 0, -0.21, 0, -0.3, 12), C(0x4E6878)], [SG.box(0.4, 0.03, 0.16, -1.02, -0.08, 0), C(0x3A2A2A)]];
        for (const [g, c] of body) { g.rotateZ(0.12); g.rotateY(ry); g.translate(x, fy, z); vc(M.vc, g, c); } K.hull((() => { const g = SG.ball(1.16, 0, 0, 0, 1, 0.46, 0.3); g.rotateZ(0.12); g.rotateY(ry); return g.translate(x, fy, z); })());
        gull(x + sx * 0.9, py, z + sz * 0.9, out); coil(x - sx * 0.7, py, z - sz * 0.7, 3, 0.28);
      } else if (i === 4 || i === 6) { // a rowing boat tied up, rocking on the swell
        const parts = [], L = 2.3, Wd = 0.95, ry = Math.atan2(-sz, sx);
        const hull = new THREE.SphereGeometry(1, 24, 12, 0, 6.2832, Math.PI / 2, Math.PI / 2).scale(L / 2, 0.55, Wd / 2); parts.push([hull, (px, pyy) => pyy > -0.12 ? WH : (i === 4 ? RD : TL)]);
        parts.push([SG.torus(1, 0.04, 0, 0.0, 0, Math.PI / 2, 0, 40).scale(L / 2, 1, Wd / 2), WD]); for (const t of [-0.35, 0.3]) parts.push([SG.box(0.18, 0.04, Wd * 0.85, t, -0.12, 0), WM]);
        for (const s of [-1, 1]) { parts.push([SG.tube(V(-0.6, 0.05, s * 0.4), V(0.7, -0.05, s * 0.75), 0.022, 6), WM]); parts.push([SG.box(0.36, 0.015, 0.1, 0.78, -0.06, s * 0.8), WM]); }
        parts.push([SG.cyl(0.13, 0.15, 0.2, 10, -0.6, -0.2, 0), C(0x8A949A)]);
        const m = new THREE.Mesh(vcGeo(parts), M.vc), g = m; m.position.set(x, WATER_Y + 0.12, z); m.rotation.y = ry; K.add(m); const ph = i;
        K.anim({ tick(dt, t) { g.position.y = WATER_Y + 0.12 + 0.05 * Math.sin(t * 1.1 + ph); g.rotation.z = 0.05 * Math.sin(t * 0.9 + ph); g.rotation.x = 0.035 * Math.sin(t * 1.3 + ph * 2); } });
        rope(V(x - sx * 1.05, 0.0, z - sz * 1.05), V(x - ox * 0.6 - sx * 2.2, 0.02, z - oz * 0.6 - sz * 2.2), 0.25, 0.018);
      } else if (i === 5) { // a lighthouse buoy, striped, its lamp lit
        vc(M.vc, SG.cyl(0.85, 0.75, 0.6, 28, x, WATER_Y + 0.12, z), RD); vc(M.vc, SG.torus(0.85, 0.06, x, WATER_Y + 0.42, z, Math.PI / 2, 0, 28), WH);
        vc(M.vc, SG.cyl(0.5, 0.32, 2.7, 24, x, WATER_Y + 1.75, z), (px, pyy) => (Math.floor((pyy - WATER_Y) / 0.45) % 2) ? WH : RD);
        vc(M.glowVC, SG.cyl(0.24, 0.24, 0.38, 14, x, WATER_Y + 3.3, z), C(0xFFE0A0).multiplyScalar(HI ? 2.4 : 1.3)); vc(M.vc, SG.cone(0.36, 0.4, x, WATER_Y + 3.7, z, 14), RD); vc(M.vc, SG.torus(0.34, 0.02, x, WATER_Y + 3.1, z, Math.PI / 2, 0, 20), WD);
        K.glow(x, WATER_Y + 3.3, z, 2.2, 0xFFD890); K.hull(SG.cyl(0.55, 0.37, 2.8, 16, x, WATER_Y + 1.75, z));
      } else { // a channel marker: a float, a lattice tower, a bell, a light on top, a gull
        vc(M.vc, SG.cyl(0.75, 0.68, 0.55, 24, x, WATER_Y + 0.1, z), C(0x2E9A5A)); vc(M.vc, SG.torus(0.75, 0.05, x, WATER_Y + 0.38, z, Math.PI / 2, 0, 24), WH);
        for (const [s1, s2] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) vc(M.vcMetal, SG.tube(V(x + s1 * 0.5, WATER_Y + 0.38, z + s2 * 0.5), V(x + s1 * 0.18, WATER_Y + 2.3, z + s2 * 0.18), 0.035, 6), C(0x2E9A5A));
        for (const yy of [0.9, 1.6]) for (const [a, b2] of [[[-1, -1], [1, -1]], [[1, -1], [1, 1]], [[1, 1], [-1, 1]], [[-1, 1], [-1, -1]]]) { const k = 0.5 - (yy - 0.38) / 1.92 * 0.32; vc(M.vcMetal, SG.tube(V(x + a[0] * k, WATER_Y + yy, z + a[1] * k), V(x + b2[0] * k, WATER_Y + yy, z + b2[1] * k), 0.025, 5), C(0x2E9A5A)); }
        vc(M.vcMetal, new THREE.LatheGeometry([[0.001, 0.32], [0.08, 0.31], [0.13, 0.22], [0.16, 0.02], [0.2, 0]].map(p => new THREE.Vector2(p[0], p[1])), 16).translate(x, WATER_Y + 1.05, z), C(0xC8A040));
        vc(M.glowVC, SG.ball(0.1, x, WATER_Y + 2.45, z), C(0x9CFF9C).multiplyScalar(HI ? 2.2 : 1.2)); K.glow(x, WATER_Y + 2.45, z, 1.2, 0xA0FFA0); gull(x, WATER_Y + 2.3, z, out + 1);
      }
    },
    props() {
      // the deck in sections: every other one laid crosswise, dark beams along the joins, an iron plate bolted where four sections meet
      { const SZ = 5.6, n = Math.ceil(A * 2 / SZ), off = -n * SZ / 2, secs = [], clearAt = (x, z) => floorAt(x, z) === 0;
        for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { if ((i + j) % 2 === 0) continue;
          const ax0 = Math.max(off + i * SZ, -A), ax1 = Math.min(off + (i + 1) * SZ, A), az0 = Math.max(off + j * SZ, -A), az1 = Math.min(off + (j + 1) * SZ, A); if (ax1 - ax0 < 0.5 || az1 - az0 < 0.5) continue;
          if (HOLES.some(h => h[0] < ax1 && h[1] > ax0 && h[2] < az1 && h[3] > az0)) continue;
          const g = new THREE.PlaneGeometry(ax1 - ax0, az1 - az0).rotateX(-Math.PI / 2).translate((ax0 + ax1) / 2, 0.003, (az0 + az1) / 2), uv = g.attributes.uv, P = g.attributes.position;
          for (let k = 0; k < uv.count; k++) uv.setXY(k, -P.getZ(k) * us, -P.getX(k) * us); secs.push(g); }
        if (secs.length) { const m = new THREE.Mesh(mergeGeos(secs, true), M.floor); m.receiveShadow = true; K.add(m); }
        const free = (x, z) => clearAt(x, z) && !BOXES.some(b => b[4] < 0.05 && inR(x, z, b, 0.08)) && !RAMPS.some(r => inR(x, z, r, 0.08));
        for (let i = 1; i < n; i++) { const p = off + i * SZ; if (Math.abs(p) >= A - 0.2) continue;
          for (const along of [0, 1]) { let run = null; const flush = t => { if (run !== null && t - run > 0.3) { const L = t - run, c = run + L / 2; wood(along ? SG.box(0.17, 0.007, L, p, 0.0035, c) : SG.box(L, 0.007, 0.17, c, 0.0035, p), WD); } run = null; };
            for (let t = -A; t <= A; t += 0.25) { const x = along ? p : t, z = along ? t : p; if (t < A && free(x, z)) { if (run === null) run = t; } else flush(t); } } }
        for (let i = 1; i < n; i++) for (let j = 1; j < n; j++) { const x = off + i * SZ, z = off + j * SZ; if (Math.abs(x) >= A - 0.4 || Math.abs(z) >= A - 0.4 || !free(x, z)) continue;
          vc(M.vcMetal, SG.box(0.42, 0.008, 0.42, x, 0.004, z), C(0x4A4440)); for (const [bx, bz] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) vc(M.vcMetal, SG.ball(0.025, x + bx * 0.15, 0.008, z + bz * 0.15, 1, 0.5, 1), MT); } }
      // the flat clutter: rope coils, hatches, a net, a wet patch with a fish, here and there over the deck and the tops of the blocks
      const dl = []; for (let t = 0, n = 0, nD = A > 28 ? 30 : 24; t < 400 && n < nD; t++) { const sz = 1.1 + R() * 0.9, x = (R() * 2 - 1) * (A - 1), z = (R() * 2 - 1) * (A - 1), y = surfaceUnder(x, z, 40);
        if (y < -0.5 || Math.hypot(x, z) < 6) continue; let ok = true; for (let a = 0; a < 6.28 && ok; a += 0.9) { const px = x + Math.cos(a) * sz * 0.45, pz = z + Math.sin(a) * sz * 0.45; if (Math.abs(surfaceUnder(px, pz, 40) - y) > 0.01 || RAMPS.some(rp => inR(px, pz, rp, 0.1))) ok = false; }
        if (!ok) continue; const g = atlasUV(new THREE.PlaneGeometry(sz, sz), (R() * 4) | 0, 2); g.rotateX(-Math.PI / 2); g.rotateY(R() * 6.28); g.translate(x, y + 0.009, z); dl.push(g); n++; }
      if (dl.length) { const dm = new THREE.Mesh(mergeGeos(dl, true), M.deckDecal); dm.renderOrder = 5; dm.receiveShadow = true; dm.layers.set(2); K.add(dm); }
      const want = A > 28 ? 30 : 24, got = []; let tries = 0, nb = 0;
      const free = (x, z, y) => { if (Math.hypot(x, z) < 7 || Math.abs(x) > A - 0.9 || Math.abs(z) > A - 0.9) return false;
        for (const [ox, oz] of [[0, 0], [0.45, 0], [-0.45, 0], [0, 0.45], [0, -0.45]]) { if (Math.abs(surfaceUnder(x + ox, z + oz, y + 0.2) - y) > 0.01 || solidThrough(x + ox, z + oz, y + 0.2)) return false; }
        return !RAMPS.some(r => inR(x, z, r, 0.5)) && !CONES.some(c => Math.hypot(c.x - x, c.z - z) < 0.9) && !got.some(p => Math.hypot(p[0] - x, p[1] - z) < 0.9); };
      const rects = BOXES.filter(b => !b[6] && b[4] < 0.05), put1 = (x, z, y) => { const crate = R() < 0.4; K.prop(crate ? 'crate' : 'barrel', x, y, z, crate ? undefined : [0x2E6FC8, 0xD8352A, 0x2FA59A, 0xF2C230, 0xF4F1EA][(R() * 5) | 0]); got.push([x, z]); nb++; };
      while (nb < want && tries++ < 500) { let x, z; const r = R();
        if (r < 0.6 && rects.length) { const b = rects[(R() * rects.length) | 0], k = (R() * 4) | 0, u = R(); x = k < 2 ? b[0] + (b[1] - b[0]) * u : k === 2 ? b[0] - 0.55 : b[1] + 0.55; z = k >= 2 ? b[2] + (b[3] - b[2]) * u : k === 0 ? b[2] - 0.55 : b[3] + 0.55; }
        else { const k = (R() * 4) | 0, u = (R() * 2 - 1) * (A - 2); x = k < 2 ? u : (k === 2 ? -1 : 1) * (A - 1.3); z = k >= 2 ? u : (k === 0 ? -1 : 1) * (A - 1.3); }
        if (!free(x, z, 0)) continue; put1(x, z, 0);
        for (let k = 0, m = R() < 0.5 ? 1 : R() < 0.6 ? 2 : 0; k < m && nb < want; k++) { const a = R() * 6.2832, x2 = x + Math.cos(a) * 0.82, z2 = z + Math.sin(a) * 0.82; if (free(x2, z2, 0)) put1(x2, z2, 0); }
      }
    },
    outer() {
      // round the raft's edge: a border of logs lashed end to end, drums under it for flotation, tires and strings of floats hung on its outside,
      // nets spilling over it into the water, a bollard at each corner moored to its spot
      const LR = 0.3, LO = A + 0.32, LY = -0.28;
      for (const [ax, az] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const tx = az, tz = -ax, at = (u, off, y) => V(ax * A + tx * u + ax * off, y, az * A + tz * u + az * off);
        for (let u = -A - 0.6, k = 0; u < A + 0.6; k++) { const len = Math.min(3.6 + R() * 1.4, A + 0.62 - u); if (len < 0.4) break; const c = at(u + len / 2, LO - A, LY), col = SG.shade(WM, 0.86 + 0.18 * R());
          const g = SG.cyl(LR - 0.01 * (k % 2), LR, len - 0.04, 14, 0, 0, 0).rotateZ(Math.PI / 2); SG.rotY(g, Math.atan2(-tz, tx), 0, 0); g.translate(c.x, c.y, c.z);
          vc(M.vcWood, uvXY(g, (x, y, z) => [(x * tx + z * tz) * 0.6, y * 2.4 + (x * ax + z * az) * 2.4]), (px, py, pz, cc, nx, ny, nz) => Math.abs(nx * tx + nz * tz) > 0.8 ? C(0xE2BE84) : col);
          for (let q = 0.5; q < len - 0.3; q += 1.25) { const lp = at(u + q, LO - A, LY), rg = SG.torus(LR + 0.012, 0.022, 0, 0, 0, 0, 0, 16); alignZ(rg, V(tx, 0, tz), lp); vc(M.vc, rg, RO); }
          u += len; }
        const tires = []; for (let u = -A + 1.8; u < A - 1.6; u += 3.4) { if (Math.abs(u) < 1.6) continue; const p = at(u + (R() - 0.5) * 0.4, LO - A + LR + 0.1, -0.14); tire(p.x, p.y, p.z, ax, az); rope(at(u, LO - A, 0.02), V(p.x, p.y + 0.36, p.z), 0.02, 0.016); tires.push(p); }
        for (let u = -A + 1.2; u < A - 1; u += 2.6) barrel(...at(u + (R() - 0.5) * 0.4, LO - A - 0.1, -0.62).toArray(), [BL, WH, RD, YL][(R() * 4) | 0], true, Math.atan2(-tz, tx));
        for (let k = 0; k + 1 < tires.length; k++) { const a = V(tires[k].x, 0.02, tires[k].z), e = V(tires[k + 1].x, 0.02, tires[k + 1].z); rope(a, e, 0.3, 0.016); for (const t of [0.25, 0.5, 0.75]) { const p = V(a.x + (e.x - a.x) * t, 0.02 - 0.3 * 4 * t * (1 - t) - 0.2, a.z + (e.z - a.z) * t); buoy(p.x, p.y, p.z, 0.9, t === 0.5 ? RD : OR); } }
        for (let n = 0; n < 3; n++) { const u0 = (R() - 0.5) * (2 * A - 6), wN = 2 + R() * 1.4, g = gridGeo(10, 10, (u, v, o) => { const uu = u0 + (u - 0.5) * wN; let off, y;
            if (v < 0.22) { off = -0.35 + 0.37 * v / 0.22; y = 0.03; } else if (v < 0.75) { const ph = Math.PI * 0.9 - (v - 0.22) / 0.53 * Math.PI * 1.0; off = LO - A + (LR + 0.03) * Math.cos(ph); y = LY + (LR + 0.03) * Math.sin(ph); } else { const k = (v - 0.75) / 0.25; off = LO - A + (LR + 0.03) * Math.cos(-0.1 * Math.PI) + 0.05 * k; y = LY + (LR + 0.03) * Math.sin(-0.1 * Math.PI) - 0.45 * k; }
            o.copy(at(uu, off + 0.03 * Math.sin(u * 13 + v * 7), y + 0.02 * Math.sin(u * 11))); });
          uvXY(g, (px, py, pz) => [(px * tx + pz * tz) * 1.6, py * 1.6 + (px * ax + pz * az) * 1.6]); put(M.net, g); }
      }
      for (const [ax, az] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const tx = az, tz = -ax, n = Math.round((2 * A - 1.4) / 4.4), st = (2 * A - 1.4) / n, posts = [];
        for (let k = 0; k <= n; k++) { const u = -A + 0.7 + k * st, x = ax * (A + 0.32) + tx * u, z = az * (A + 0.32) + tz * u; wood(SG.cyl(0.085, 0.1, 1.15, 10, x, 0.17, z), WD); wood(SG.cyl(0.11, 0.11, 0.05, 10, x, 0.76, z), WM); posts.push(V(x, 0.7, z));
          if (k % 3 === 1) { lantern(x + ax * 0.02, 0.84, z + az * 0.02); K.light(x - ax * 0.6, 0.2, z - az * 0.6, 2.2, 0xFFB050, 0.55); } }
        for (let k = 0; k + 1 < posts.length; k++) { const a = posts[k], e = posts[k + 1]; rope(a, e, 0.22, 0.022); for (const t of [0.3, 0.5, 0.7]) { const p = V(a.x + (e.x - a.x) * t, a.y - 0.22 * 4 * t * (1 - t), a.z + (e.z - a.z) * t); vc(M.vc, SG.cyl(0.007, 0.007, 0.1, 4, p.x, p.y - 0.05, p.z), RO); buoy(p.x, p.y - 0.22, p.z, 0.8, t === 0.5 ? RD : OR); } }
      }
      for (const sx of [-1, 1]) for (const sz of [-1, 1]) { const x = sx * (A + 0.05), z = sz * (A + 0.05); wood(SG.cyl(0.28, 0.3, 1.6, 16, x, 0.1, z), WD); wood(SG.cyl(0.31, 0.31, 0.06, 16, x, 0.92, z), WM); for (const y of [0.35, 0.5, 0.65]) vc(M.vc, SG.torus(0.3, 0.035, x, y, z, Math.PI / 2, 0, 20), RO); K.hull(SG.cyl(0.34, 0.36, 1.7, 16, x, 0.1, z)); }
      for (const [ax, az] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) for (const sg of [-1, 1]) { const u = sg * A * 0.52 + (R() - 0.5) * 2, off = A + 2.4; pontoon2(ax * off + az * u, az * off - ax * u, Math.atan2(ax, az) + (R() - 0.5) * 0.3); }
      // bunting: little flags strung on lines between the tall landmarks round the raft, the next one round each time
      { const cols = [RD, YL, TL, WH, OR, BL], ord = tops.slice().sort((p, q) => Math.atan2(p.x, p.z) - Math.atan2(q.x, q.z));
        for (let k = 0; k < ord.length; k++) { const a = ord[k], e = ord[(k + 1) % ord.length], D = Math.hypot(e.x - a.x, e.z - a.z); if (D > 46 || D < 3) continue;
          const sag = 1.0 + D * 0.035; rope(a, e, sag, 0.012); const n = Math.max(4, Math.round(D / 0.55)), dx = (e.x - a.x) / D, dz = (e.z - a.z) / D;
          for (let q = 1; q < n; q++) { const t = q / n, px = a.x + (e.x - a.x) * t, pz = a.z + (e.z - a.z) * t, py2 = a.y + (e.y - a.y) * t - sag * 4 * t * (1 - t);
            const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute([px - dx * 0.16, py2, pz - dz * 0.16, px + dx * 0.16, py2, pz + dz * 0.16, px + dx * 0.02, py2 - 0.36, pz + dz * 0.02], 3)); g.computeVertexNormals(); vc(M.vcFlag, g, cols[(q + k) % cols.length]); } } }
      // a fishing town out on the water: houses on stilts with bright roofs, lit windows, a jetty, boats tied up, an islet of sand and palms
      { const town = (a, d, n, sd) => { const RR = rng(sd), parts = [], glow = [], walls = [WH, C(0xF2DCB0), C(0xA8D8DC), C(0xF4C0A8), C(0xF6E2A0)], roofs = [RD, TL, BL, OR, C(0x6A4AA0)];
          parts.push([new THREE.SphereGeometry(1, 20, 8, 0, 6.2832, 0, Math.PI / 2).scale(9 + n * 1.6, 2.2, 7).translate(0, WATER_Y - 0.9, -3), C(0xE8D4A0)]);
          for (let k = 0; k < 3; k++) { const px = (RR() - 0.5) * n * 2.6, pz = -4 - RR() * 2; parts.push([SG.cyl(0.12, 0.18, 4.2, 6, px, WATER_Y + 2.6, pz), C(0x8A6A44)]); for (let f = 0; f < 5; f++) { const fa = f / 5 * 6.2832; parts.push([SG.ball(1, px + Math.cos(fa) * 0.9, WATER_Y + 4.6, pz + Math.sin(fa) * 0.9, 1.3, 0.18, 0.5).rotateY(-fa), C(0x4E9A4A)]); } }
          for (let k = 0; k < n; k++) { const hx = (k - (n - 1) / 2) * 3.3 + (RR() - 0.5) * 0.8, hz = (RR() - 0.5) * 1.6, w = 2.1 + RR() * 0.8, dd = 2 + RR() * 0.6, hh = 1.8 + RR() * 0.9, y0 = WATER_Y + 1.1 + RR() * 0.4, wc = walls[(RR() * walls.length) | 0], rc = roofs[(RR() * roofs.length) | 0];
            for (const [sx2, sz2] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) parts.push([SG.cyl(0.08, 0.08, y0 - WATER_Y + 0.4, 5, hx + sx2 * (w / 2 - 0.15), (y0 + WATER_Y - 0.4) / 2, hz + sz2 * (dd / 2 - 0.15)), C(0x6A4A30)]);
            parts.push([SG.box(w + 0.3, 0.12, dd + 0.9, hx, y0, hz + 0.3), C(0x9A7048)]); parts.push([SG.box(w, hh, dd, hx, y0 + hh / 2 + 0.06, hz), wc]);
            parts.push([new THREE.ConeGeometry(Math.max(w, dd) * 0.82, 1.1 + RR() * 0.5, 4).rotateY(Math.PI / 4).scale(w / Math.max(w, dd), 1, dd / Math.max(w, dd)).translate(hx, y0 + hh + 0.6, hz), rc]);
            parts.push([SG.box(0.5, 1.0, 0.04, hx - w * 0.22, y0 + 0.56, hz + dd / 2 + 0.02), C(0x5A3A24)]);
            for (const wx of [0.14, 0.34]) glow.push([SG.box(0.36, 0.34, 0.04, hx + w * (wx - 0.5) + 0.5, y0 + hh * 0.62, hz + dd / 2 + 0.03), C(0xFFD890).multiplyScalar(HI ? 1.8 : 1.2)]); }
          for (let k = 0; k < 6; k++) parts.push([SG.box(1.0, 0.08, 0.5, 0, WATER_Y + 0.7, 1.5 + k * 0.52), C(0x9A7048)], [SG.cyl(0.06, 0.06, 1.2, 5, 0.42, WATER_Y + 0.2, 1.5 + k * 0.52), C(0x6A4A30)], [SG.cyl(0.06, 0.06, 1.2, 5, -0.42, WATER_Y + 0.2, 1.5 + k * 0.52), C(0x6A4A30)]);
          for (const [bx, bc] of [[1.8, RD], [-1.9, TL]]) parts.push([new THREE.SphereGeometry(1, 12, 6, 0, 6.2832, Math.PI / 2, Math.PI / 2).scale(0.5, 0.35, 1.3).translate(bx, WATER_Y + 0.25, 3.4), (px, py) => py > WATER_Y + 0.12 ? WH : bc]);
          const m = new THREE.Mesh(vcGeo(parts), M.vc), mg = new THREE.Mesh(vcGeo(glow), M.glowVC);
          for (const o of [m, mg]) { o.position.set(Math.cos(a) * d, 0, Math.sin(a) * d); o.rotation.y = -a - Math.PI / 2; K.add(o); } };
        town(1.55, 108, 6, 801); town(3.35, 122, 5, 802); town(5.95, 98, 4, 803); }
      // out on the water: two sailboats far off, rocking, and a lighthouse on an islet
      const sails = [[0.6, 92], [2.4, 120], [4.1, 84]];
      for (const [a, d] of sails) { const parts = [[new THREE.SphereGeometry(1, 16, 8, 0, 6.2832, Math.PI / 2, Math.PI / 2).scale(3.2, 1.0, 1.1), (px, py) => py > -0.25 ? WH : C(0x2A4E8A)], [SG.cyl(0.07, 0.06, 6.5, 8, 0.3, 3.2, 0), WD]];
        const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.lineTo(0, 5.8); sh.lineTo(2.6, 0.2); sh.closePath(); parts.push([new THREE.ShapeGeometry(sh).translate(0.4, 0.4, 0), WH]); const sh2 = new THREE.Shape(); sh2.moveTo(0, 0); sh2.lineTo(0, 4.6); sh2.lineTo(-2.2, 0.2); sh2.closePath(); parts.push([new THREE.ShapeGeometry(sh2).translate(0.2, 0.4, 0), C(0xF2E6C8)]);
        const m = new THREE.Mesh(vcGeo(parts), toon(0xFFFFFF, { vertexColors: true, side: THREE.DoubleSide }, { roughness: 0.6 })); m.userData.own = true; const g = m; m.position.set(Math.cos(a) * d, WATER_Y + 0.4, Math.sin(a) * d); m.rotation.y = a + 1.2; K.add(m); const ph = a * 3;
        K.anim({ tick(dt, t) { g.rotation.z = 0.06 * Math.sin(t * 0.7 + ph); g.position.y = WATER_Y + 0.4 + 0.25 * Math.sin(t * 0.6 + ph); } }); }
      { const a = 5.2, d = 140, x = Math.cos(a) * d, z = Math.sin(a) * d, parts = [[new THREE.SphereGeometry(1, 20, 8, 0, 6.2832, 0, Math.PI / 2).scale(14, 3, 10).translate(0, WATER_Y - 0.5, 0), C(0x8A8278)], [SG.cyl(1.6, 1.1, 13, 18, 2, 7, 0), (px, py) => (Math.floor(py / 2.2) % 2) ? WH : RD], [SG.cyl(1.0, 1.0, 1.6, 14, 2, 14.3, 0), C(0xFFE6A0)], [SG.cone(1.4, 1.6, 2, 15.9, 0, 14), RD]];
        const m = new THREE.Mesh(vcGeo(parts), toon(0xFFFFFF, { vertexColors: true }, { roughness: 0.8 })); m.userData.own = true; m.position.set(x, 0, z); K.add(m); K.glow(x + 2, 14.3, z, 6, 0xFFE0A0); }
    },
  };
}
// the raft's floor marking: a fish skeleton painted big in white, the paint scuffed
function raftDecal(g, S, c, r) {
  g.strokeStyle = 'rgba(246,244,236,0.92)'; g.fillStyle = 'rgba(246,244,236,0.92)'; g.lineCap = 'round'; g.lineJoin = 'round';
  g.lineWidth = 18; g.beginPath(); g.moveTo(c - 150, c); g.lineTo(c + 170, c); g.stroke();
  for (let k = 0; k < 6; k++) { const x = c - 100 + k * 44, L = 92 - Math.abs(k - 1.5) * 9; g.lineWidth = 13; for (const s of [-1, 1]) { g.beginPath(); g.moveTo(x, c); g.quadraticCurveTo(x + 18, c + s * L * 0.6, x - 4, c + s * L); g.stroke(); } }
  g.lineWidth = 15; g.beginPath(); g.moveTo(c - 150, c - 66); g.quadraticCurveTo(c - 250, c - 40, c - 236, c + 10); g.quadraticCurveTo(c - 220, c + 60, c - 150, c + 70); g.quadraticCurveTo(c - 130, c, c - 150, c - 66); g.stroke();
  g.beginPath(); g.arc(c - 196, c - 14, 15, 0, 6.2832); g.fill(); g.lineWidth = 9; g.beginPath(); g.moveTo(c - 236, c + 26); g.lineTo(c - 206, c + 30); g.stroke();
  g.lineWidth = 16; g.beginPath(); g.moveTo(c + 170, c); g.lineTo(c + 234, c - 72); g.moveTo(c + 170, c); g.lineTo(c + 234, c + 72); g.stroke(); g.lineWidth = 9; g.beginPath(); g.moveTo(c + 234, c - 72); g.quadraticCurveTo(c + 214, c, c + 234, c + 72); g.stroke();
  g.globalCompositeOperation = 'destination-out'; for (let k = 0; k < 1100; k++) { g.fillStyle = `rgba(0,0,0,${0.2 + r() * 0.6})`; g.beginPath(); g.ellipse(r() * S, r() * S, 1 + r() * 6, 1 + r() * 2.5, 0, 0, 6.2832); g.fill(); } g.globalCompositeOperation = 'source-over';
}
// the raft's scattered markings: teal chevrons, a loose coil of rope, a dropped fish in a wet patch, a riveted tin patch
function raftScatter(cell, g, r, H) {
  cell(0, () => { g.strokeStyle = 'rgba(47,165,154,0.9)'; g.lineWidth = 36; g.lineCap = 'round'; g.lineJoin = 'round'; for (const dx of [-70, 50]) { g.beginPath(); g.moveTo(dx - 60, -110); g.lineTo(dx + 50, 0); g.lineTo(dx - 60, 110); g.stroke(); }
    g.globalCompositeOperation = 'destination-out'; for (let k = 0; k < 300; k++) { g.fillStyle = `rgba(0,0,0,${0.3 + r() * 0.6})`; g.beginPath(); g.arc((r() - 0.5) * 480, (r() - 0.5) * 480, 1 + r() * 4, 0, 6.2832); g.fill(); } g.globalCompositeOperation = 'source-over'; });
  cell(1, () => { g.lineCap = 'round'; for (const [col, w] of [['rgba(60,40,20,0.45)', 30], ['rgba(214,174,114,0.98)', 22]]) { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); for (let t = 0; t <= 1; t += 0.004) { const a = t * 6.2832 * 3.2, rr = 40 + t * 150; const x = Math.cos(a) * rr + (col.includes('60') ? 4 : 0), y = Math.sin(a) * rr + (col.includes('60') ? 5 : 0); t ? g.lineTo(x, y) : g.moveTo(x, y); } g.lineTo(220, 180); g.stroke(); }
    g.strokeStyle = 'rgba(120,88,50,0.6)'; g.lineWidth = 3; for (let t = 0; t <= 1; t += 0.01) { const a = t * 6.2832 * 3.2, rr = 40 + t * 150, x = Math.cos(a) * rr, y = Math.sin(a) * rr; g.beginPath(); g.moveTo(x - Math.cos(a + 0.8) * 9, y - Math.sin(a + 0.8) * 9); g.lineTo(x + Math.cos(a + 0.8) * 9, y + Math.sin(a + 0.8) * 9); g.stroke(); } });
  cell(2, () => { polyAt(g, lumpy(r, 190, 140, 14), 0, 0, 0.3); g.fillStyle = 'rgba(60,44,30,0.28)'; g.fill(); g.save(); g.rotate(-0.4); g.fillStyle = 'rgba(126,150,168,0.98)'; g.beginPath(); g.ellipse(0, 0, 120, 46, 0, 0, 6.2832); g.fill(); g.fillStyle = 'rgba(220,228,232,0.98)'; g.beginPath(); g.ellipse(0, 14, 108, 26, 0, 0, 3.1416); g.fill();
    g.fillStyle = 'rgba(100,126,146,0.98)'; g.beginPath(); g.moveTo(108, 0); g.lineTo(170, -44); g.lineTo(156, 0); g.lineTo(170, 44); g.closePath(); g.fill(); g.fillStyle = '#111'; g.beginPath(); g.arc(-82, -8, 8, 0, 6.2832); g.fill(); g.restore(); });
  cell(3, () => { g.fillStyle = 'rgba(30,24,20,0.4)'; g.fillRect(-150, -150, 310, 310); g.fillStyle = 'rgba(150,162,170,0.98)'; g.fillRect(-160, -160, 310, 310); for (let k = 0; k < 18; k++) { g.fillStyle = `rgba(${150 + r() * 40 | 0},${78 + r() * 20 | 0},40,${0.2 + r() * 0.35})`; g.beginPath(); g.arc(-160 + r() * 310, -160 + r() * 310, 10 + r() * 34, 0, 6.2832); g.fill(); }
    g.fillStyle = 'rgba(70,78,84,0.95)'; for (let k = 0; k < 7; k++) for (const [x, y] of [[-145 + k * 46, -145], [-145 + k * 46, 135], [-145, -145 + k * 46], [135, -145 + k * 46]]) { g.beginPath(); g.arc(x, y, 6, 0, 6.2832); g.fill(); } g.strokeStyle = 'rgba(90,98,104,0.9)'; g.lineWidth = 5; g.strokeRect(-160, -160, 310, 310); });
}
