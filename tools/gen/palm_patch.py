# Palette Island: new palms (curved ringed trunks, crowns of long feathery fronds over a skirt of dry brown ones) and log planters bound
# with rope in place of the tall tan pots
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

MOD = r"""
// ---------- Palette Island's palms and planters: their textures (drawn once), the palm's trunk and fronds, and the log planter it grows in ----------
function isleTex() {
  if (SURF.__isle) return SURF.__isle;
  const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }, R = rng(4242), clampT = t => { t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; return t; };
  // a frond: leaflets fanning off a midrib toward the tip, cut out by their alpha, darker by the rib and yellower at their tips (v runs base to tip)
  const frond = dry => {
    const W = 256, H = 512, c = mk(W, H), g = c.getContext('2d'), r = rng(dry ? 913 : 911);
    const base = dry ? [118, 84, 46] : [84, 128, 40], tip = dry ? [176, 136, 84] : [196, 196, 86], rib = dry ? [196, 160, 110] : [214, 214, 120];
    for (let pass = 0; pass < 2; pass++) for (const sd of [-1, 1]) for (let i = 0; i < 46; i++) {
      if ((i & 1) !== pass) continue;
      const v = 0.05 + (i + r() * 0.6) / 46 * 0.92, wk = Math.pow(Math.sin(Math.PI * Math.min(1, v * 1.06)), 0.65), y0 = (1 - v) * H;
      const len = (W / 2 - 3) * wk * (0.82 + r() * 0.18), ang = 0.52 + v * 0.3 + (r() - 0.5) * 0.12, x1 = W / 2 + sd * Math.cos(ang) * len, y1 = y0 - Math.sin(ang) * len * 0.62;
      const wl = (4.6 + 3.4 * wk) * (dry ? 0.8 : 1), mx = (W / 2 + x1) / 2, my = (y0 + y1) / 2 + 3, nx = -(y1 - y0), ny = x1 - W / 2, nl = Math.hypot(nx, ny) || 1;
      const gr = g.createLinearGradient(W / 2, y0, x1, y1), sh = 0.86 + r() * 0.22;
      gr.addColorStop(0, rgbS(base[0] * sh, base[1] * sh, base[2] * sh)); gr.addColorStop(0.65, rgbS((base[0] + tip[0]) / 2 * sh, (base[1] + tip[1]) / 2 * sh, (base[2] + tip[2]) / 2 * sh)); gr.addColorStop(1, rgbS(tip[0] * sh, tip[1] * sh, tip[2] * sh));
      g.fillStyle = gr; g.beginPath(); g.moveTo(W / 2, y0 - wl * 0.6); g.quadraticCurveTo(mx + nx / nl * wl, my + ny / nl * wl, x1, y1); g.quadraticCurveTo(mx - nx / nl * wl * 0.7, my - ny / nl * wl * 0.7, W / 2, y0 + wl * 0.6); g.closePath(); g.fill();
      g.strokeStyle = 'rgba(255,255,220,0.22)'; g.lineWidth = 1; g.beginPath(); g.moveTo(W / 2, y0); g.quadraticCurveTo(mx, my, x1, y1); g.stroke();
      if (dry && r() < 0.4) { g.fillStyle = 'rgba(70,46,24,0.35)'; g.beginPath(); g.ellipse(mx, my, 6, 2.5, Math.atan2(y1 - y0, x1 - W / 2), 0, 6.2832); g.fill(); }
    }
    const rg = g.createLinearGradient(0, H, 0, 0); rg.addColorStop(0, rgbS(...rib.map(v => v * 0.8))); rg.addColorStop(1, rgbS(...rib)); g.strokeStyle = rg; g.lineCap = 'round';
    for (let y = H; y > 6; y -= 8) { const v = 1 - y / H; g.lineWidth = 7 - 4.5 * v; g.beginPath(); g.moveTo(W / 2, y); g.lineTo(W / 2, y - 9); g.stroke(); }
    const t = texOf(c, true); return clampT(t);
  };
  // the trunk: one ring per repeat, a dark groove under a rounded band, fibers running up it
  const ring = () => { const W = 64, H = 64, c = mk(W, H), h = mk(W, H), g = c.getContext('2d'), gh = h.getContext('2d');
    for (let y = 0; y < H; y++) { const v = 1 - y / H, band = Math.sin(Math.min(1, Math.max(0, (v - 0.12) / 0.86)) * Math.PI), groove = Math.max(0, 1 - v / 0.12);
      const k = 0.7 + 0.32 * Math.pow(band, 0.6) - 0.25 * groove; g.fillStyle = rgbS(204 * k, 160 * k, 104 * k); g.fillRect(0, y, W, 1); gh.fillStyle = gray(0.25 + 0.6 * Math.pow(band, 0.7) - 0.2 * groove); gh.fillRect(0, y, W, 1); }
    for (let i = 0; i < 70; i++) { const x = R() * W, y = R() * H, l = 4 + R() * 14; g.strokeStyle = R() < 0.5 ? 'rgba(110,76,40,0.25)' : 'rgba(240,206,150,0.22)'; g.lineWidth = 1; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (R() - 0.5) * 2, y - l); g.stroke(); }
    for (let i = 0; i < 6; i++) { const x = R() * W; g.fillStyle = 'rgba(96,66,36,0.35)'; g.fillRect(x, H - 9 - R() * 4, 3 + R() * 6, 2); }
    return { map: texOf(c, true), nrm: HI ? heightNormal(h, 2.2) : null }; };
  // a post's side: brown wood, grain running up it, a few cracks and knots
  const wood = () => { const W = 128, H = 256, c = mk(W, H), h = mk(W, H), g = c.getContext('2d'), gh = h.getContext('2d');
    g.fillStyle = '#8E5C33'; g.fillRect(0, 0, W, H); gh.fillStyle = gray(0.6); gh.fillRect(0, 0, W, H);
    for (let i = 0; i < 90; i++) { const x = R() * W, w = 1 + R() * 3, dark = R() < 0.55; g.fillStyle = dark ? `rgba(84,52,26,${0.12 + R() * 0.2})` : `rgba(176,124,78,${0.1 + R() * 0.18})`; g.fillRect(x, 0, w, H); if (x + w > W) g.fillRect(x - W, 0, w, H); gh.fillStyle = grayA(dark ? 0.45 : 0.7, 0.4); gh.fillRect(x, 0, w, H); }
    for (let i = 0; i < 7; i++) { let x = R() * W, y = R() * H; const L = 30 + R() * 140; g.strokeStyle = 'rgba(48,28,12,0.75)'; gh.strokeStyle = gray(0.05); g.lineWidth = gh.lineWidth = 1.2 + R() * 1.4; g.beginPath(); gh.beginPath(); g.moveTo(x, y); gh.moveTo(x, y); for (let s = 0; s < L; s += 6) { x += (R() - 0.5) * 2.2; y += 6; g.lineTo(x, y); gh.lineTo(x, y); } g.stroke(); gh.stroke(); }
    for (let i = 0; i < 3; i++) { const x = 10 + R() * (W - 20), y = 20 + R() * (H - 40), rx = 4 + R() * 5, ry = 7 + R() * 7; g.fillStyle = 'rgba(74,44,20,0.8)'; g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, 6.2832); g.fill(); g.fillStyle = 'rgba(150,100,58,0.9)'; g.beginPath(); g.ellipse(x, y, rx * 0.5, ry * 0.5, 0, 0, 6.2832); g.fill(); gh.fillStyle = gray(0.3); gh.beginPath(); gh.ellipse(x, y, rx, ry, 0, 0, 6.2832); gh.fill(); }
    return { map: texOf(c, true), nrm: HI ? heightNormal(h, 1.6) : null }; };
  // a post's sawn end: rings, a crack, darker bark round the rim
  const endT = () => { const S = 128, c = mk(S, S), g = c.getContext('2d'), m = S / 2; g.fillStyle = '#6E4626'; g.fillRect(0, 0, S, S); g.fillStyle = '#B9875A'; g.beginPath(); g.arc(m, m, m - 7, 0, 6.2832); g.fill();
    for (let k = 1; k < 7; k++) { g.strokeStyle = `rgba(122,82,46,${0.35 + R() * 0.25})`; g.lineWidth = 1.2 + R(); g.beginPath(); for (let a = 0; a <= 6.3; a += 0.2) { const rr = (m - 9) * k / 7 * (1 + (R() - 0.5) * 0.05), x = m + Math.cos(a) * rr, y = m + Math.sin(a) * rr; a ? g.lineTo(x, y) : g.moveTo(x, y); } g.closePath(); g.stroke(); }
    g.strokeStyle = 'rgba(60,36,16,0.8)'; g.lineWidth = 2; g.beginPath(); g.moveTo(m, m); g.lineTo(m + (m - 10) * 0.8, m + 6); g.stroke(); g.fillStyle = 'rgba(70,44,22,0.9)'; g.beginPath(); g.arc(m, m, 3, 0, 6.2832); g.fill();
    return { map: texOf(c, true) }; };
  // rope: three strands twisting round, each rounded and lit along its middle
  const rope = () => { const S = 64, c = mk(S, S), h = mk(S, S), g = c.getContext('2d'), gh = h.getContext('2d'); g.fillStyle = '#8C6A40'; g.fillRect(0, 0, S, S); gh.fillStyle = gray(0.1); gh.fillRect(0, 0, S, S);
    for (let k = -1; k < 4; k++) for (let w = 0; w < 14; w++) { const t = w / 13, col = 0.62 + 0.4 * Math.sin(t * Math.PI); g.strokeStyle = rgbS(212 * col, 172 * col, 112 * col); gh.strokeStyle = gray(0.15 + 0.85 * Math.sin(t * Math.PI)); g.lineWidth = gh.lineWidth = 1.6;
      const o = k * S / 3 + w * (S / 3) / 14; g.beginPath(); gh.beginPath(); g.moveTo(o, S); gh.moveTo(o, S); g.lineTo(o + S, 0); gh.lineTo(o + S, 0); g.stroke(); gh.stroke(); }
    for (let i = 0; i < 40; i++) { const x = R() * S, y = R() * S; g.strokeStyle = 'rgba(250,226,180,0.3)'; g.lineWidth = 0.8; g.beginPath(); g.moveTo(x, y); g.lineTo(x + 3, y - 2); g.stroke(); }
    return { map: texOf(c, true), nrm: HI ? heightNormal(h, 1.8) : null }; };
  return SURF.__isle = { frond: frond(false), dry: frond(true), ring: ring(), wood: wood(), end: endT(), rope: rope() };
}
// the island's own materials for these (sway copies of the palm's are made with the rest)
function isleMats(M) {
  if (M.post) return; const X = isleTex(), pbr = (nrm, n, r) => HI ? Object.assign({ roughness: r }, nrm ? { normalMap: nrm, normalScale: new THREE.Vector2(n, n) } : {}) : null;
  M.frond2 = toon(0xFFFFFF, { map: X.frond, alphaTest: 0.42, side: THREE.DoubleSide }, pbr(null, 1, 0.62));
  M.frondDry = toon(0xFFFFFF, { map: X.dry, alphaTest: 0.42, side: THREE.DoubleSide }, pbr(null, 1, 0.8));
  M.trunk = toon(0xFFFFFF, { map: X.ring.map }, pbr(X.ring.nrm, 1.1, 0.85));
  M.nut2 = toon(0x6F7A34, null, { roughness: 0.55 });
  M.post = toon(0xFFFFFF, { map: X.wood.map }, pbr(X.wood.nrm, 1, 0.82));
  M.postEnd = toon(0xFFFFFF, { map: X.end.map }, { roughness: 0.85 });
  M.rope = toon(0xFFFFFF, { map: X.rope.map }, pbr(X.rope.nrm, 1.2, 0.9));
  M.star = toon(0xF0996A, null, { roughness: 0.7 }); M.pebble = toon(0xB8A88F, null, { roughness: 0.9 }); M.leafBig = toon(0x3E9C42, { side: THREE.DoubleSide }, { roughness: 0.55 });
  if (HI) for (const k of ['frond2', 'frondDry', 'trunk', 'nut2', 'post', 'postEnd', 'rope', 'star', 'pebble', 'leafBig']) aoPatch(M[k]);
}
// a tube along a run of points with a radius at each (u round it, v along it in units of vScale): trunks, ropes
function tubeAlong(pts, radii, nr, vScale, closed) {
  const n = pts.length, pos = [], uv = [], idx = [], up = new THREE.Vector3(0, 1, 0), t = new THREE.Vector3(), a1 = new THREE.Vector3(), a2 = new THREE.Vector3(); let vAcc = 0;
  for (let i = 0; i < n; i++) {
    const p = pts[i], pa = pts[closed ? (i - 1 + n) % n : Math.max(0, i - 1)], pb = pts[closed ? (i + 1) % n : Math.min(n - 1, i + 1)]; t.subVectors(pb, pa).normalize();
    a1.crossVectors(t, Math.abs(t.y) > 0.9 ? XA : up).normalize(); a2.crossVectors(t, a1).normalize();
    if (i > 0) vAcc += p.distanceTo(pts[i - 1]);
    for (let j = 0; j <= nr; j++) { const ph = j / nr * 6.2832, c = Math.cos(ph), s = Math.sin(ph), r = radii[i]; pos.push(p.x + (a1.x * c + a2.x * s) * r, p.y + (a1.y * c + a2.y * s) * r, p.z + (a1.z * c + a2.z * s) * r); uv.push(j / nr, vAcc / vScale); }
  }
  if (closed) { const p = pts[0], last = pts[n - 1]; vAcc += p.distanceTo(last); const o = pos.slice(0, (nr + 1) * 3); pos.push(...o); for (let j = 0; j <= nr; j++) uv.push(j / nr, vAcc / vScale); }
  const rows = closed ? n + 1 : n;
  for (let i = 0; i < rows - 1; i++) for (let j = 0; j < nr; j++) { const a = i * (nr + 1) + j, b = a + nr + 1; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
// a feathery frond: its midrib arcs out of the crown and droops, the leaflets either side angled down off it (a shallow V), hanging lower
// toward their tips. o where it starts, a its heading, el how far up it points, L its length, W its half-width, droop how much it bows
function frondGeo2(o, a, el, L, W, droop) {
  const n = HI ? 13 : 9, E = [-1, -0.55, 0, 0.55, 1], pos = [], uv = [], idx = [], ca = Math.cos(a), sa = Math.sin(a), ce = Math.cos(el), se = Math.sin(el);
  const rib = t => new THREE.Vector3(o.x + ca * ce * L * t, o.y + L * (se * t - droop * t * t), o.z + sa * ce * L * t);
  for (let i = 0; i <= n; i++) {
    const t = i / n, c = rib(t), tg = rib(Math.min(1, t + 0.02)).sub(rib(Math.max(0, t - 0.02))).normalize(), sx = -tg.z, sz = tg.x, sl = Math.hypot(sx, sz) || 1;
    const w = W * Math.pow(Math.sin(Math.PI * Math.min(1, t * 1.04)), 0.55) * Math.min(1, t / 0.1);
    for (const e of E) pos.push(c.x + sx / sl * e * w, c.y - Math.abs(e) * w * 0.32 - e * e * w * 0.2, c.z + sz / sl * e * w), uv.push((e + 1) / 2, t);
  }
  for (let i = 0; i < n; i++) for (let j = 0; j < 4; j++) { const a0 = i * 5 + j, b0 = a0 + 5; idx.push(a0, b0, a0 + 1, b0, b0 + 1, a0 + 1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); g.setIndex(idx); g.computeVertexNormals(); return g;
}
// a palm: a trunk curving up in rings (flared at its foot), a crown of long fronds (two young ones standing up), a skirt of dry ones hanging
// under it, coconuts tucked in. Geometry in world space, sorted by material
function palmParts2(x, y, z, h, s, lean, rot, R) {
  const lx = Math.cos(rot) * lean, lz = Math.sin(rot) * lean, Pt = t => new THREE.Vector3(x + lx * Math.pow(t, 1.7) * h, y + t * h, z + lz * Math.pow(t, 1.7) * h);
  const NS = 16, pts = [], rad = [];
  for (let i = 0; i <= NS; i++) { const t = i / NS; pts.push(Pt(t)); rad.push(s * (0.17 - 0.06 * t) * (1 + 0.45 * Math.pow(Math.max(0, 1 - t / 0.1), 2))); }
  const top = Pt(1), trunk = [tubeAlong(pts, rad, HI ? 12 : 8, 0.12 * s / 1.25, false)];
  { const cap = new THREE.SphereGeometry(rad[NS] * 1.35, HI ? 12 : 8, HI ? 8 : 6); cap.scale(1, 0.9, 1); cap.translate(top.x, top.y + rad[NS] * 0.4, top.z); trunk.push(cap); }
  const fronds = [], dry = [], nuts = [], a0 = R() * 6.2832, nF = HI ? 11 : 8;
  for (let k = 0; k < nF; k++) { const a = a0 + k / nF * 6.2832 + (R() - 0.5) * 0.35, young = k < 2; fronds.push(frondGeo2(top.clone().setY(top.y + 0.06 * s), a, young ? 0.85 + R() * 0.25 : 0.12 + R() * 0.42, s * (young ? 1.05 + R() * 0.25 : 1.55 + R() * 0.55), s * (young ? 0.3 : 0.4), young ? 0.35 : 0.75 + R() * 0.45)); }
  for (let k = 0, nd = HI ? 6 : 4; k < nd; k++) { const a = a0 + (k + 0.5) / nd * 6.2832 + (R() - 0.5) * 0.5; dry.push(frondGeo2(top.clone().setY(top.y - 0.04 * s), a, -0.95 - R() * 0.35, s * (1.05 + R() * 0.35), s * 0.3, 0.12 + R() * 0.12)); }
  for (let k = 0; k < 3; k++) { const a = k * 2.094 + R(), g = new THREE.SphereGeometry(s * 0.085, HI ? 10 : 7, HI ? 8 : 5); g.translate(top.x + Math.cos(a) * s * 0.13, top.y - s * 0.06, top.z + Math.sin(a) * s * 0.13); nuts.push(g); }
  return { trunk, fronds, dry, nuts };
}
// a planter for a palm: a ring of sawn posts of different heights round a heap of sand, bound with two ropes (one knotted, its ends hanging),
// a starfish stuck on, a little sand drifted up round its foot, a few broad leaves and pebbles. Fills the column's footprint
function planterParts(cx, cz, rad, top, R) {
  const out = { post: [], end: [], rope: [], star: [], pebble: [], leaf: [], mound: [], foot: [], hull: [] };
  const pr = Math.min(0.17, Math.max(0.12, rad * 0.2)), ringR = rad - pr * 0.85, n = Math.max(9, Math.round(6.2832 * ringR / (pr * 1.96))), a0 = R() * 6.2832, hs = [];
  for (let i = 0; i < n; i++) hs.push(top + (i % 3 === 0 ? 0.14 + R() * 0.2 : -0.1 + R() * 0.18));
  for (let i = 0; i < n; i++) {
    const a = a0 + i / n * 6.2832, x = cx + Math.cos(a) * ringR, z = cz + Math.sin(a) * ringR, ph = hs[i], r = pr * (0.94 + R() * 0.1), tx = (R() - 0.5) * 0.05, tz = (R() - 0.5) * 0.05;
    const g = new THREE.CylinderGeometry(r * 0.97, r, ph, HI ? 12 : 8, 1, true); const uv = g.attributes.uv; for (let k = 0; k < uv.count; k++) uv.setXY(k, uv.getX(k) + i * 0.37, uv.getY(k) * ph / 0.9);
    const e = new THREE.CircleGeometry(r * 0.97, HI ? 12 : 8); e.rotateX(-Math.PI / 2); e.translate(0, ph / 2, 0); const eu = e.attributes.uv; for (let k = 0; k < eu.count; k++) eu.setXY(k, 0.5 + (eu.getX(k) - 0.5) * 0.96, 0.5 + (eu.getY(k) - 0.5) * 0.96);
    const hl = new THREE.CylinderGeometry(r * 0.97 + 0.035, r + 0.035, ph + 0.04, 10, 1);
    for (const gg of [g, e, hl]) { gg.rotateX(tx); gg.rotateZ(tz); gg.translate(x, ph / 2, z); }
    out.post.push(g); out.end.push(e); out.hull.push(hl);
  }
  // the ropes: round the outside of the posts, pulled in a little between them
  const ropeR = 0.034, ropeAt = (yy, sag) => { const pts = [], rr = []; const Ro = ringR + pr + ropeR * 0.6; for (let i = 0; i < n * 3; i++) { const u = i / 3, a = a0 + u / n * 6.2832, f = (i % 3) / 3, mid = f > 0 ? 1 : 0, rr0 = mid ? Ro * Math.cos(3.1416 / n) * 1.01 : Ro; pts.push(new THREE.Vector3(cx + Math.cos(a) * rr0, yy - sag * mid * Math.sin(f * 3.1416), cz + Math.sin(a) * rr0)); rr.push(ropeR); } return tubeAlong(pts, rr, HI ? 8 : 6, 0.1, true); };
  const y1 = Math.min(top * 0.3, 0.75), y2 = Math.min(top * 0.72, top - 0.25);
  out.rope.push(ropeAt(y1, 0.015), ropeAt(y2, 0.02));
  { const aK = a0 + (R() * n | 0) / n * 6.2832 + 3.1416 / n, Rk = ringR + pr + ropeR * 1.6, kx = cx + Math.cos(aK) * Rk, kz = cz + Math.sin(aK) * Rk;
    const k = new THREE.TorusKnotGeometry(0.05, 0.026, HI ? 48 : 28, HI ? 8 : 6, 2, 3); k.rotateY(-aK + 1.5708); k.translate(kx, y2, kz); out.rope.push(k);
    for (const sdd of [-1, 1]) { const pts = [], rr = []; for (let i = 0; i <= 6; i++) { const t = i / 6; pts.push(new THREE.Vector3(kx + Math.cos(aK + 1.5708) * sdd * (0.03 + t * 0.03) + Math.cos(aK) * t * 0.02, y2 - 0.03 - t * (0.22 + sdd * 0.04), kz + Math.sin(aK + 1.5708) * sdd * (0.03 + t * 0.03) + Math.sin(aK) * t * 0.02)); rr.push(ropeR * (1 - t * 0.25)); } out.rope.push(tubeAlong(pts, rr, HI ? 7 : 5, 0.1, false)); } }
  // a starfish on the side, between the ropes
  { const aS = a0 + R() * 6.2832, sh = new THREE.Shape(), Ro = 0.12, Ri = 0.05; for (let k = 0; k < 10; k++) { const a = k / 10 * 6.2832 - 1.5708, r = k % 2 ? Ri : Ro, px = Math.cos(a) * r, py = Math.sin(a) * r; k ? sh.lineTo(px, py) : sh.moveTo(px, py); } sh.closePath();
    const g = new THREE.ExtrudeGeometry(sh, { depth: 0.02, bevelEnabled: true, bevelThickness: 0.018, bevelSize: 0.022, bevelSegments: 2, curveSegments: 4 }); g.rotateZ(R() * 6.28);
    const ys = (y1 + y2) / 2 + (R() - 0.5) * 0.1, Rs = ringR + pr + 0.02; g.rotateY(-aS + 1.5708); g.translate(cx + Math.cos(aS) * Rs, ys, cz + Math.sin(aS) * Rs); out.star.push(g); }
  // sand heaped in the middle (the palm stands in it) and drifted up round the foot
  { const m = new THREE.SphereGeometry(ringR * 1.02, HI ? 22 : 14, HI ? 8 : 5, 0, 6.2832, 0, Math.PI / 2); m.scale(1, 0.13 / (ringR * 1.02), 1); m.translate(cx, top - 0.03, cz); out.mound.push(m);
    const f = new THREE.TorusGeometry(ringR + pr * 0.9, 0.16, HI ? 8 : 5, HI ? 40 : 24); f.rotateX(Math.PI / 2); f.scale(1, 0.42, 1); f.translate(cx, 0, cz); out.foot.push(f); }
  // pebbles and a couple of clumps of broad leaves at its foot
  for (let i = 0; i < 4 + (R() * 3 | 0); i++) { const a = R() * 6.2832, d = rad + 0.08 + R() * 0.25, g = new THREE.DodecahedronGeometry(0.05 + R() * 0.07, 0); g.scale(1, 0.6, 1); g.rotateY(R() * 6.28); g.translate(cx + Math.cos(a) * d, 0.02, cz + Math.sin(a) * d); out.pebble.push(g); }
  for (let c = 0, nc = 1 + (R() < 0.6 ? 1 : 0); c < nc; c++) { const ac = R() * 6.2832, bx = cx + Math.cos(ac) * (rad + 0.12), bz = cz + Math.sin(ac) * (rad + 0.12);
    for (let k = 0; k < 5; k++) { const a = ac + (k - 2) * 0.42 + (R() - 0.5) * 0.25, el = 0.5 + R() * 0.45, L = 0.38 + R() * 0.2, W = 0.09 + R() * 0.04, pos = [], idx = [];
      for (let i = 0; i <= 6; i++) { const t = i / 6, w = W * Math.pow(Math.sin(Math.PI * t), 0.8), px = bx + Math.cos(a) * Math.cos(el) * L * t, py = 0.04 + L * (Math.sin(el) * t - 0.7 * t * t), pz = bz + Math.sin(a) * Math.cos(el) * L * t, sx = -Math.sin(a), sz = Math.cos(a);
        pos.push(px - sx * w, py - w * 0.25, pz - sz * w, px, py + w * 0.12, pz, px + sx * w, py - w * 0.25, pz + sz * w); }
      for (let i = 0; i < 6; i++) { const q = i * 3; idx.push(q, q + 3, q + 1, q + 3, q + 4, q + 1, q + 1, q + 4, q + 2, q + 4, q + 5, q + 2); }
      const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(new Float32Array(pos.length / 3 * 2), 2)); g.setIndex(idx); g.computeVertexNormals(); out.leaf.push(g); } }
  return out;
}
"""
anchor = "const farIsles = new THREE.Group(), farBlocks = new THREE.Group();"
rep(anchor, MOD + anchor)

# the island's planters replace the plain column; the palm grows from the heap of sand in it
rep("    putAll(g, mats); hulls.push(o);\n    // Graphics mode: a trim along the top edge",
    "    const planter = T.id === 'island' && kind === 'column';\n    if (!planter) { putAll(g, mats); hulls.push(o); }\n    // Graphics mode: a trim along the top edge")
rep("    if (HI && T.trim && !grave) {\n      const tw = T.trim.w || 0.15,", "    if (HI && T.trim && !grave && !planter) {\n      const tw = T.trim.w || 0.15,")
rep("      else if (T.id === 'island' && kind === 'column') { if (T.ivy && R() < T.ivy.col) IVY.climb(cx, cz, rad, top - 0.12, R, 0.3); palmAt(cx, top, cz, 2.4 + R() * 1.4, 1.25, 0.18 + R() * 0.25, R() * 6.28, 'column', rad); for (let k = 0; k < 4; k++) { const a = R() * 6.28; put(M.rock, ball(0.25 + R() * 0.3, cx + Math.cos(a) * rad * 1.02, 0.1, cz + Math.sin(a) * rad * 1.02, 0.6)); } }",
    "      else if (planter) { const pl = planterParts(cx, cz, rad, top, R); pl.post.forEach(g => put(M.post, g)); pl.end.forEach(g => put(M.postEnd, g)); pl.rope.forEach(g => put(M.rope, g)); pl.star.forEach(g => put(M.star, g)); pl.pebble.forEach(g => put(M.pebble, g)); pl.leaf.forEach(g => put(M.leafBig, g)); pl.mound.forEach(g => put(M.top, g)); pl.foot.forEach(g => put(M.floor, g)); hulls.push(...pl.hull);\n        palmAt(cx, top + 0.08, cz, 2.3 + R() * 1.3, 1.25, 0.2 + R() * 0.25, R() * 6.28, 'column', rad); }")
# palms: the new trunk, crown and dry skirt (island only; the far islands keep the simple ones)
rep("  const palmAt = (x, y, z, h, s, lean, rot, kind, r) => { const Pm = palmParts(x, y, z, h, s, lean, rot, R), slot = addSway('palm', x, z, kind === 'corner' ? 0.3 : r, y, h + s * 0.6);\n    Pm.trunk.forEach(g => putSway(M.palm, g, slot, x, z, y, h)); Pm.fronds.forEach(g => putSway(M.frond, g, slot, x, z, y, h)); Pm.nuts.forEach(g => putSway(M.nut, g, slot, x, z, y, h)); };",
    "  const palmAt = (x, y, z, h, s, lean, rot, kind, r) => { const slot = addSway('palm', x, z, kind === 'corner' ? 0.3 : r, y, h + s * 0.6);\n    if (M.trunk) { const Pm = palmParts2(x, y, z, h, s, lean, rot, R); Pm.trunk.forEach(g => putSway(M.trunk, g, slot, x, z, y, h)); Pm.fronds.forEach(g => putSway(M.frond2, g, slot, x, z, y, h)); Pm.dry.forEach(g => putSway(M.frondDry, g, slot, x, z, y, h)); Pm.nuts.forEach(g => putSway(M.nut2, g, slot, x, z, y, h)); return; }\n    const Pm = palmParts(x, y, z, h, s, lean, rot, R); Pm.trunk.forEach(g => putSway(M.palm, g, slot, x, z, y, h)); Pm.fronds.forEach(g => putSway(M.frond, g, slot, x, z, y, h)); Pm.nuts.forEach(g => putSway(M.nut, g, slot, x, z, y, h)); };")
# the island's materials, and sway copies of the new palm's
rep("  if (T.id === 'island') T.mats.sway = new Map(['palm', 'frond', 'nut', 'leaf', 'leaf2', 'canopy'].filter(k => T.mats[k]).map(k => [T.mats[k], swayMat(T.mats[k])]));",
    "  if (T.id === 'island') isleMats(T.mats);\n  if (T.id === 'island') T.mats.sway = new Map(['palm', 'frond', 'nut', 'leaf', 'leaf2', 'canopy', 'trunk', 'frond2', 'frondDry', 'nut2'].filter(k => T.mats[k]).map(k => [T.mats[k], swayMat(T.mats[k])]));")
# fronds cast their own (feathery, cut-out) shadows rather than going into the one solid shadow caster
rep("  for (const [mat, list] of swayBag) { const m = new THREE.Mesh(mergeSway(list), mat); m.receiveShadow = true; m.layers.enable(3); stageGroup.add(m); shadowG.push(m.geometry); }",
    "  for (const [mat, list] of swayBag) { const m = new THREE.Mesh(mergeSway(list), mat); m.receiveShadow = true; m.layers.enable(3); stageGroup.add(m); if (mat.alphaTest > 0) m.castShadow = true; else shadowG.push(m.geometry); }")
open(P, 'w').write(src)
print('ok')
