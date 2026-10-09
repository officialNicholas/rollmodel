import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)
def between(a, b, new):
    global s
    i = s.index(a); j = s.index(b, i)
    s = s[:i] + new + s[j:]

# ================= round shapes: a box tagged 'c' is a cylinder (its square is the bounding box) =================
rep("const inR = (x, z, r, m) => (m = m || 0, x > r[0] - m && x < r[1] + m && z > r[2] - m && z < r[3] + m);",
    "const inR = (x, z, r, m) => (m = m || 0, r[6] === 'c' ? (x - (r[0] + r[1]) * 0.5) ** 2 + (z - (r[2] + r[3]) * 0.5) ** 2 < Math.max(0, (r[1] - r[0]) * 0.5 + m) ** 2 : x > r[0] - m && x < r[1] + m && z > r[2] - m && z < r[3] + m);")
rep("  for (const b of BOXES) for (let x = b[0] + S / 2; x < b[1]; x += S) for (let z = b[2] + S / 2; z < b[3]; z += S) addSample(x, b[5], z);",
    "  for (const b of BOXES) for (let x = b[0] + S / 2; x < b[1]; x += S) for (let z = b[2] + S / 2; z < b[3]; z += S) if (b[6] !== 'c' || inR(x, z, b)) addSample(x, b[5], z);")

# ================= themes: textures and looks =================
rep("// ---------- build the stage ----------\n", r"""// ---------- map themes: every canvas picks a look, with its own floor, walls, sky, pieces and props ----------
function makeTex(S, draw) { const cv = document.createElement('canvas'); cv.width = cv.height = S; const g = cv.getContext('2d'); draw(g, S); const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); return t; }
const wrapAt = (S, x, y, pad, fn) => { for (const dx of [-S, 0, S]) for (const dy of [-S, 0, S]) { const X = x + dx, Y = y + dy; if (X > -pad && X < S + pad && Y > -pad && Y < S + pad) fn(X, Y); } };
const polyAt = (g, pts, X, Y, rot) => { const c = Math.cos(rot), sn = Math.sin(rot); g.beginPath(); pts.forEach((p, i) => { const x = X + p[0] * c - p[1] * sn, y = Y + p[0] * sn + p[1] * c; i ? g.lineTo(x, y) : g.moveTo(x, y); }); g.closePath(); };
const lumpy = (r, rx, ry, n) => { const pts = []; for (let k = 0; k < n; k++) { const a = k / n * 6.2832, m = 0.82 + 0.25 * r(); pts.push([Math.cos(a) * rx * m, Math.sin(a) * ry * m]); } return pts; };
const specks = (g, S, r, n, col) => { for (let i = 0; i < n; i++) { g.fillStyle = col(r()); g.fillRect(r() * S, r() * S, 1 + r() * 2, 1 + r() * 2); } };
// crypt: worn cobbles and dark brick
const cobbleTex = makeTex(256, (g, S) => { const r = rng(31), N = 6, cs = S / N; g.fillStyle = '#2A2C34'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) { const cx = (i + 0.5 + (r() - 0.5) * 0.35) * cs, cy = (j + 0.5 + (r() - 0.5) * 0.35) * cs, pts = lumpy(r, cs * (0.42 + r() * 0.06), cs * (0.4 + r() * 0.06), 12), rot = r() * 3, l = 96 + r() * 44 | 0, col = `rgb(${l},${l + 3},${l + 12})`;
    wrapAt(S, cx, cy, cs, (X, Y) => { polyAt(g, pts, X, Y, rot); g.fillStyle = col; g.fill(); polyAt(g, pts.map(p => [p[0] * 0.62, p[1] * 0.62]), X - cs * 0.06, Y - cs * 0.06, rot); g.fillStyle = 'rgba(255,255,255,0.09)'; g.fill(); }); }
  specks(g, S, r, 380, k => `rgba(70,${110 + k * 40 | 0},80,${0.18 + k * 0.2})`); });
const brickTex = makeTex(256, (g, S) => { const r = rng(32), rows = 8, h = S / rows, w = S / 4; g.fillStyle = '#22232A'; g.fillRect(0, 0, S, S);
  for (let j = 0; j < rows; j++) for (let i = -1; i < 5; i++) { const x = i * w + (j % 2) * w / 2, l = 74 + r() * 34 | 0; g.fillStyle = `rgb(${l},${l + 2},${l + 10})`; g.fillRect(x + 2, j * h + 2, w - 4, h - 4); g.fillStyle = 'rgba(255,255,255,0.07)'; g.fillRect(x + 2, j * h + 2, w - 4, 3); }
  specks(g, S, r, 500, k => `rgba(0,0,0,${0.1 + k * 0.15})`); });
// cathedral: checkered marble with gold grout, pale ashlar
const marbleTex = makeTex(256, (g, S) => { const r = rng(33), T = S / 2;
  for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) { g.fillStyle = (i + j) % 2 ? '#5C6382' : '#EDE6D7'; g.fillRect(i * T, j * T, T, T); }
  for (let k = 0; k < 16; k++) { const x0 = r() * S, y0 = r() * S, a = r() * 6.28, L = 50 + r() * 130, pts = []; for (let t = 0; t <= 12; t++) pts.push([Math.cos(a) * L * t / 12 + Math.sin(t * 1.3 + k) * 7, Math.sin(a) * L * t / 12 + Math.cos(t * 1.7 + k) * 7]);
    g.strokeStyle = k % 2 ? `rgba(110,100,130,${0.16 + r() * 0.2})` : `rgba(255,255,255,${0.1 + r() * 0.14})`; g.lineWidth = 0.6 + r() * 1.5; wrapAt(S, x0, y0, 200, (X, Y) => { g.beginPath(); pts.forEach((p, i) => i ? g.lineTo(X + p[0], Y + p[1]) : g.moveTo(X + p[0], Y + p[1])); g.stroke(); }); }
  g.strokeStyle = '#B8954A'; g.lineWidth = 3; for (const v of [0, T, S]) { g.beginPath(); g.moveTo(v, 0); g.lineTo(v, S); g.stroke(); g.beginPath(); g.moveTo(0, v); g.lineTo(S, v); g.stroke(); } });
const ashlarTex = makeTex(256, (g, S) => { const r = rng(34), rows = 4, h = S / rows, w = S / 2; g.fillStyle = '#9E968A'; g.fillRect(0, 0, S, S);
  for (let j = 0; j < rows; j++) for (let i = -1; i < 3; i++) { const x = i * w + (j % 2) * w / 2, l = r() * 18 | 0; g.fillStyle = `rgb(${206 + l},${198 + l},${186 + l})`; g.fillRect(x + 3, j * h + 3, w - 6, h - 6); g.fillStyle = 'rgba(0,0,0,0.06)'; g.fillRect(x + 3, j * h + h - 9, w - 6, 6); }
  specks(g, S, r, 600, k => `rgba(120,110,95,${0.08 + k * 0.12})`); });
// manor: plank parquet and dark damask
const parquetTex = makeTex(256, (g, S) => { const r = rng(35), cols = 8, w = S / cols; g.fillStyle = '#3A2214'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < cols; i++) { let y = -r() * S * 0.5; while (y < S) { const L = S * (0.28 + r() * 0.4), l = r(), col = `rgb(${112 + l * 46 | 0},${66 + l * 28 | 0},${34 + l * 16 | 0})`;
      for (const off of [-S, 0, S]) { g.fillStyle = col; g.fillRect(i * w + 1.5, y + off + 1.5, w - 3, L - 3); g.strokeStyle = 'rgba(60,30,10,0.25)'; g.lineWidth = 0.8; for (let k = 0; k < 3; k++) { const gx = i * w + 4 + r() * (w - 8); g.beginPath(); g.moveTo(gx, y + off + 3); g.lineTo(gx + (r() - 0.5) * 3, y + off + L - 3); g.stroke(); } }
      y += L; } } });
const damaskTex = makeTex(256, (g, S) => { const r = rng(36), P = S / 4; g.fillStyle = '#3A1B34'; g.fillRect(0, 0, S, S); g.strokeStyle = '#5E2E54'; g.lineWidth = 2.5;
  for (let k = -4; k <= 8; k++) { g.beginPath(); g.moveTo(k * P, 0); g.lineTo(k * P + S, S); g.stroke(); g.beginPath(); g.moveTo(k * P, S); g.lineTo(k * P + S, 0); g.stroke(); }
  for (let i = 0; i <= 4; i++) for (let j = 0; j <= 4; j++) { g.fillStyle = '#8A5A3A'; g.beginPath(); g.arc(i * P, j * P, 3.5, 0, 6.2832); g.fill(); g.fillStyle = 'rgba(200,150,90,0.35)'; g.beginPath(); g.arc(i * P + P / 2, j * P + P / 2, 6, 0, 6.2832); g.fill(); }
  specks(g, S, r, 300, k => `rgba(0,0,0,${0.08 + k * 0.1})`); });
// night garden: moss and clipped hedge
const mossTex = makeTex(256, (g, S) => { const r = rng(37); g.fillStyle = '#2E4A30'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < 70; i++) { const pts = lumpy(r, 10 + r() * 26, 8 + r() * 20, 10), x = r() * S, y = r() * S, col = r() < 0.5 ? 'rgba(62,96,58,0.55)' : 'rgba(30,54,34,0.5)'; wrapAt(S, x, y, 40, (X, Y) => { polyAt(g, pts, X, Y, r() * 3); g.fillStyle = col; g.fill(); }); }
  for (let i = 0; i < 900; i++) { const x = r() * S, y = r() * S; g.strokeStyle = `rgba(${90 + r() * 40 | 0},${140 + r() * 40 | 0},${80 + r() * 20 | 0},${0.35 + r() * 0.3})`; g.lineWidth = 1; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (r() - 0.5) * 4, y - 3 - r() * 4); g.stroke(); } });
const hedgeTex = makeTex(256, (g, S) => { const r = rng(38); g.fillStyle = '#1F4524'; g.fillRect(0, 0, S, S);
  for (let i = 0; i < 1300; i++) { const x = r() * S, y = r() * S, l = r(), col = `rgb(${34 + l * 40 | 0},${84 + l * 60 | 0},${36 + l * 26 | 0})`; wrapAt(S, x, y, 8, (X, Y) => { g.fillStyle = col; g.beginPath(); g.ellipse(X, Y, 3 + r() * 3, 1.6 + r() * 1.4, r() * 3.14, 0, 6.2832); g.fill(); }); } });
const THEMES = [
  { id: 'studio', label: 'The Studio', floor: () => canvasTex, side: () => woodTex, uv: 0.5, ft: 0xBDBDBD, st: 0xB4B4B4, dt: 0x8A8A8A, hor: 0x2A1C52, sky: [0x07051A, 0x160F3E, 0x3B2770], hemi: [0x7672C2, 0x221846], kit: { drum: [1, 3], column: [0, 1], rpad: [0, 1], rotunda: [0, 1], rpit: [0, 1] }, fill: 'drum' },
  { id: 'crypt', label: 'The Crypt', floor: () => cobbleTex, side: () => brickTex, uv: 0.25, ft: 0xD0D4E0, st: 0xC4C8D6, dt: 0x8E92A0, hor: 0x16323A, sky: [0x03090F, 0x0C2027, 0x1D4850], hemi: [0x76AEB6, 0x14262A], kit: { tombs: [2, 4], column: [1, 2], rpit: [0, 1], drum: [0, 1] }, fill: 'tombs' },
  { id: 'cathedral', label: 'The Cathedral', floor: () => marbleTex, side: () => ashlarTex, uv: 0.25, ft: 0xC6C6C6, st: 0xBEBAB2, dt: 0x9A958C, hor: 0x1A2350, sky: [0x03051A, 0x0B1340, 0x243880], hemi: [0x8494DC, 0x1A1E40], kit: { column: [2, 4], rotunda: [0, 1], rpad: [1, 1], drum: [0, 1] }, fill: 'column' },
  { id: 'manor', label: 'The Manor', floor: () => parquetTex, side: () => damaskTex, uv: 0.3, ft: 0xD0D0D0, st: 0xD4D4D4, dt: 0x8A8A8A, hor: 0x33153A, sky: [0x0C0410, 0x290E2E, 0x541F4E], hemi: [0xB27CC2, 0x2A1430], kit: { rpad: [1, 2], drum: [1, 2], rotunda: [0, 1], column: [0, 1] }, fill: 'rpad' },
  { id: 'garden', label: 'The Night Garden', floor: () => mossTex, side: () => hedgeTex, uv: 0.25, ft: 0xD2D2D2, st: 0xD0D0D0, dt: 0x8A9A8A, hor: 0x12343A, sky: [0x020A12, 0x09232E, 0x1B4F58], hemi: [0x74BCAA, 0x10281E], kit: { drum: [2, 3], column: [1, 2], rpit: [0, 1], rpad: [0, 1] }, fill: 'drum' },
];
const THEME_BY = Object.fromEntries(THEMES.map(t => [t.id, t]));
let TH = THEMES[0];
const PAL = [0xE3122F, 0x2E9BFF, 0xFFD23F, 0x8B3DFF, 0x3DDC84, 0xFF6A1A];
function themeMats(T) {
  if (T.mats) return T.mats;
  const fl = T.floor(), sd = T.side(), lighten = (c, k) => new THREE.Color(c).multiplyScalar(k).getHex();
  T.mats = { floor: toon(T.ft, { map: fl }), top: toon(lighten(T.ft, 1.06), { map: fl }), side: toon(T.st, { map: sd }), dark: toon(T.dt, { map: sd }), rampSide: toon(T.st, { map: sd, side: THREE.DoubleSide }),
    stone: toon(0x9A9EAA), gold: toon(0xE2B356), bark: toon(0x5A3A28), leaf: toon(0x2F7A42), leaf2: toon(0x3E9550), metal: toon(0xD6DAE2), cream: toon(0xF2E8D2), glowY: new THREE.MeshBasicMaterial({ color: 0xFFD27A }), pal: PAL.map(c => toon(c)) };
  return T.mats;
}
// the sky, fog and moonlight shift with the theme
function applyThemeLook(T) {
  TH = T; HOR.set(T.hor); skyU.top.value.set(T.sky[0]); skyU.mid.value.set(T.sky[1]); skyU.hor.value.set(T.sky[2]); NIGHT.sky.set(T.hemi[0]); NIGHT.gnd.set(T.hemi[1]);
}
// split a multi-material geometry into one piece per material, so the whole stage can be merged into a handful of draw calls
function splitGroups(g) {
  const ng = g.index ? g.toNonIndexed() : g, out = [];
  for (const gr of ng.groups) { const sub = new THREE.BufferGeometry(); for (const name of ['position', 'normal', 'uv']) { const a = ng.attributes[name]; if (a) sub.setAttribute(name, new THREE.BufferAttribute(a.array.slice(gr.start * a.itemSize, (gr.start + gr.count) * a.itemSize), a.itemSize)); } (out[gr.materialIndex] = out[gr.materialIndex] || []).push(sub); }
  return out;
}
const flames = [];
// ---------- build the stage ----------
""")

# ================= the stage builder =================
between("const floaters = [];\nfunction rebuildStage() {", "// ---------- clouds and far-off canvases ----------", r"""const floaters = [];
function rebuildStage() {
  for (const o of stageGroup.children.slice()) { stageGroup.remove(o); if (o.geometry) o.geometry.dispose(); if (o.userData.own) o.material.dispose(); if (o.userData.ownMats) o.userData.ownMats.forEach(m => m.dispose()); }
  floaters.length = 0; flames.length = 0;
  const T = TH, M = themeMats(T), us = T.uv, R = rng(((GEN.seed || 1) * 7 + 13) >>> 0);
  const V = (x, y, z) => new THREE.Vector3(x, y, z), lines = [], hulls = [], frame = [], bag = new Map();
  const put = (mat, g) => { let l = bag.get(mat); if (!l) bag.set(mat, l = []); l.push(g); };
  const putAll = (g, mats) => splitGroups(g).forEach((list, i) => list && list.forEach(pg => put(mats[i], pg)));
  const at = (g, x, y, z) => { g.translate(x, y, z); return g; };
  const cyl = (r0, r1, h, n, x, y, z) => at(new THREE.CylinderGeometry(r0, r1, h, n || 28), x, y, z);
  const ball = (r, x, y, z, sy) => { const g = new THREE.SphereGeometry(r, 16, 12); if (sy) g.scale(1, sy, 1); return at(g, x, y, z); };
  const flame = (x, y, z, sz, col) => { const sp = glowSprite(sz); sp.material.color.set(col || 0xFFB04A); sp.position.set(x, y, z); stageGroup.add(sp); flames.push({ s: sp, base: sz }); };
  const ring = (cx, cz, r, y, t) => { const n = 36; for (let k = 0; k < n; k++) { const a0 = k / n * 6.2832, a1 = (k + 1) / n * 6.2832; lines.push(beamGeo(V(cx + Math.cos(a0) * r, y, cz + Math.sin(a0) * r), V(cx + Math.cos(a1) * r, y, cz + Math.sin(a1) * r), t)); } };
  // floor: one panel with holes (square or round), edged in the theme's wall material
  const shape = new THREE.Shape();
  shape.moveTo(-ARENA, -ARENA); shape.lineTo(ARENA, -ARENA); shape.lineTo(ARENA, ARENA); shape.lineTo(-ARENA, ARENA); shape.lineTo(-ARENA, -ARENA);
  for (const h of HOLES) { const p = new THREE.Path(); if (h[6] === 'c') p.absarc((h[0] + h[1]) / 2, -(h[2] + h[3]) / 2, (h[1] - h[0]) / 2, 0, Math.PI * 2, true); else { p.moveTo(h[0], -h[3]); p.lineTo(h[0], -h[2]); p.lineTo(h[1], -h[2]); p.lineTo(h[1], -h[3]); p.lineTo(h[0], -h[3]); } shape.holes.push(p); }
  const fg = new THREE.ExtrudeGeometry(shape, { depth: 0.7, bevelEnabled: false, curveSegments: 28 }); fg.rotateX(-Math.PI / 2); fg.translate(0, -0.7, 0); worldUV(fg, us);
  const floor = new THREE.Mesh(fg, [M.floor, M.side]); floor.receiveShadow = true; stageGroup.add(floor);
  const rect = (x0, x1, z0, z1, y, t) => { lines.push(beamGeo(V(x0, y, z0), V(x1, y, z0), t), beamGeo(V(x1, y, z0), V(x1, y, z1), t), beamGeo(V(x1, y, z1), V(x0, y, z1), t), beamGeo(V(x0, y, z1), V(x0, y, z0), t)); };
  rect(-ARENA, ARENA, -ARENA, ARENA, 0, 0.09); rect(-ARENA, ARENA, -ARENA, ARENA, -0.7, 0.09);
  for (const [x, z] of [[-ARENA, -ARENA], [ARENA, -ARENA], [ARENA, ARENA], [-ARENA, ARENA]]) lines.push(beamGeo(V(x, -0.7, z), V(x, 0, z), 0.09));
  HOLES.forEach(h => h[6] === 'c' ? ring((h[0] + h[1]) / 2, (h[2] + h[3]) / 2, (h[1] - h[0]) / 2, 0, 0.09) : rect(h[0], h[1], h[2], h[3], 0, 0.09));
  const bar = (x0, x1, z0, z1) => { const g = new THREE.BoxGeometry(x1 - x0, 0.45, z1 - z0); g.translate((x0 + x1) / 2, -0.95, (z0 + z1) / 2); frame.push(g); };
  const IN = ARENA - 0.6; bar(-IN, IN, -IN, -IN + 0.8); bar(-IN, IN, IN - 0.8, IN); bar(-IN, -IN + 0.8, -IN, IN); bar(IN - 0.8, IN, -IN, IN); bar(-7.4, -6.6, -IN, IN); bar(-IN, IN, -8.5, -7.7);
  frame.forEach(g => { worldUV(g, us); put(M.dark, g); });
  // pieces: square blocks, round drums and columns, gravestones, floating slabs and discs
  for (const b of BOXES) {
    const w = b[1] - b[0], d = b[3] - b[2], h = b[5] - b[4], cx = (b[0] + b[1]) / 2, cz = (b[2] + b[3]) / 2, cy = (b[4] + b[5]) / 2, circ = b[6] === 'c', grave = b[6] === 'g', rad = w / 2, kind = b[7] || '';
    if (grave) {
      // a gravestone: a slab with a round top, a little worn
      const along = w > d, sw = along ? w : d, th = along ? d : w, bodyH = h - sw / 2;
      const body = new THREE.BoxGeometry(along ? sw : th, bodyH, along ? th : sw); body.translate(cx, bodyH / 2, cz);
      const cap = new THREE.CylinderGeometry(sw / 2, sw / 2, th, 18, 1, false, 0, Math.PI); if (along) cap.rotateX(Math.PI / 2); else { cap.rotateZ(Math.PI / 2); cap.rotateX(Math.PI / 2); cap.rotateY(Math.PI / 2); } cap.translate(cx, bodyH, cz);
      put(M.stone, body); put(M.stone, cap);
      const hb = new THREE.BoxGeometry((along ? sw : th) + 0.12, bodyH + 0.06, (along ? th : sw) + 0.12); hb.translate(cx, bodyH / 2, cz); hulls.push(hb);
      const hc = new THREE.CylinderGeometry(sw / 2 + 0.06, sw / 2 + 0.06, th + 0.12, 18, 1, false, 0, Math.PI); if (along) hc.rotateX(Math.PI / 2); else { hc.rotateZ(Math.PI / 2); hc.rotateX(Math.PI / 2); hc.rotateY(Math.PI / 2); } hc.translate(cx, bodyH, cz); hulls.push(hc);
      continue;
    }
    const g = circ ? cyl(rad, rad, h, 44, cx, cy, cz) : at(new THREE.BoxGeometry(w, h, d), cx, cy, cz); worldUV(g, us);
    const o = circ ? cyl(rad + 0.07, rad + 0.07, h + 0.14, 44, cx, cy, cz) : at(new THREE.BoxGeometry(w + 0.14, h + 0.14, d + 0.14), cx, cy, cz);
    const mats = circ ? [M.side, M.top, M.dark] : [M.side, M.side, M.top, M.dark, M.side, M.side];
    if (b[4] > 0) {
      // floating: its own materials so it can fade while you're under it (solid, and drawn before the paint, the rest of the time)
      const own = mats.map(mm => mm.clone()), m = new THREE.Mesh(g, own); m.castShadow = true; m.receiveShadow = true; m.userData.ownMats = own; stageGroup.add(m);
      const hm = new THREE.Mesh(o, new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide })); hm.userData.own = true; stageGroup.add(hm);
      floaters.push({ b, mats: own, hull: hm, k: 1, last: 1 });
      continue;
    }
    putAll(g, mats); hulls.push(o);
    // the theme dresses the round pieces
    if (circ) {
      const top = b[5];
      if (T.id === 'studio' && kind === 'drum') { const pm = M.pal[(R() * M.pal.length) | 0]; put(pm, cyl(rad + 0.03, rad + 0.03, h * 0.38, 44, cx, h * 0.45, cz)); const tr = new THREE.TorusGeometry(rad - 0.02, 0.07, 8, 44); tr.rotateX(Math.PI / 2); put(pm, at(tr, cx, top + 0.01, cz)); }
      else if (T.id === 'studio' && kind === 'column') { const pm = M.pal[(R() * M.pal.length) | 0]; put(pm, cyl(rad + 0.02, rad + 0.02, h * 0.8, 44, cx, h * 0.5, cz)); put(M.cream, at(new THREE.ConeGeometry(rad, rad * 1.5, 28), cx, top + rad * 0.75, cz)); put(pm, at(new THREE.ConeGeometry(rad * 0.32, rad * 0.5, 16), cx, top + rad * 1.27, cz)); }
      else if ((T.id === 'cathedral' || T.id === 'crypt') && kind === 'column') { const tm = T.id === 'cathedral' ? M.gold : M.stone; put(tm, cyl(rad + 0.26, rad + 0.18, 0.35, 32, cx, top - 0.17, cz)); put(M.stone, cyl(rad + 0.22, rad + 0.3, 0.3, 32, cx, 0.15, cz)); if (T.id === 'crypt') { put(M.cream, cyl(0.12, 0.12, 0.45, 10, cx, top + 0.22, cz)); flame(cx, top + 0.6, cz, 0.75); } else flame(cx, top + 0.45, cz, 1.1, 0xFFE3A0); }
      else if (T.id === 'garden' && kind === 'column') { put(M.bark, cyl(rad * 0.98, rad * 1.05, h, 18, cx, h / 2, cz)); for (let k = 0; k < 3; k++) { const a = R() * 6.28, rr = rad * 0.9; put(k % 2 ? M.leaf : M.leaf2, ball(rad * (2.1 + R() * 0.6), cx + Math.cos(a) * rr, top + 0.5 + k * 0.55, cz + Math.sin(a) * rr, 0.8)); } }
      else if ((T.id === 'manor' || T.id === 'cathedral') && (kind === 'drum' || kind === 'rotunda')) { const tr = new THREE.TorusGeometry(rad, 0.08, 8, 48); tr.rotateX(Math.PI / 2); put(M.gold, at(tr, cx, top, cz)); }
      else if (T.id === 'garden' && kind === 'drum') { for (let k = 0; k < 6; k++) { const a = k / 6 * 6.28 + R(); put(k % 2 ? M.leaf : M.leaf2, ball(0.32 + R() * 0.16, cx + Math.cos(a) * rad * 0.98, h * (0.3 + R() * 0.5), cz + Math.sin(a) * rad * 0.98)); } }
    }
  }
  // ramps: a sloped top, walled sides, inked edges
  for (const r of RAMPS) {
    const [x0, x1, z0, z1] = r, h = (x, z) => rampH(r, x, z);
    const tg = new THREE.BufferGeometry(), Pp = [x0, h(x0, z0), z0, x1, h(x1, z0), z0, x1, h(x1, z1), z1, x0, h(x0, z1), z1];
    tg.setAttribute('position', new THREE.Float32BufferAttribute(Pp, 3)); tg.setAttribute('uv', new THREE.Float32BufferAttribute([x0 * us, -z0 * us, x1 * us, -z0 * us, x1 * us, -z1 * us, x0 * us, -z1 * us], 2));
    tg.setIndex([0, 2, 1, 0, 3, 2]); tg.computeVertexNormals(); put(M.top, tg);
    const S2 = [], quad = (a, b2, c, d2) => S2.push(...a, ...b2, ...c, ...a, ...c, ...d2), pt = (x, y, z) => [x, y, z];
    quad(pt(x0, 0, z0), pt(x1, 0, z0), pt(x1, h(x1, z0), z0), pt(x0, h(x0, z0), z0));
    quad(pt(x1, 0, z1), pt(x0, 0, z1), pt(x0, h(x0, z1), z1), pt(x1, h(x1, z1), z1));
    quad(pt(x0, 0, z1), pt(x0, 0, z0), pt(x0, h(x0, z0), z0), pt(x0, h(x0, z1), z1));
    quad(pt(x1, 0, z0), pt(x1, 0, z1), pt(x1, h(x1, z1), z1), pt(x1, h(x1, z0), z0));
    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(S2, 3)); sg.computeVertexNormals(); worldUV(sg, us); put(M.rampSide, sg);
    if (r[4] === 'z') { lines.push(beamGeo(V(x0, h(x0, z0), z0), V(x0, h(x0, z1), z1), 0.08), beamGeo(V(x1, h(x1, z0), z0), V(x1, h(x1, z1), z1), 0.08)); }
    else { lines.push(beamGeo(V(x0, h(x0, z0), z0), V(x1, h(x1, z0), z0), 0.08), beamGeo(V(x0, h(x0, z1), z1), V(x1, h(x1, z1), z1), 0.08)); }
    const lowAtStart = r[5] < r[6];
    if (r[4] === 'z') { const zl = lowAtStart ? z0 : z1; lines.push(beamGeo(V(x0, 0, zl), V(x1, 0, zl), 0.08)); }
    else { const xl = lowAtStart ? x0 : x1; lines.push(beamGeo(V(xl, 0, z0), V(xl, 0, z1), 0.08)); }
  }
  // props around the canvas: landmarks on floating plinths, different for every theme
  const E = ARENA + 2.4, spots = [[-E, -E], [E, -E], [E, E], [-E, E], [0, -E], [E, 0], [0, E], [-E, 0]];
  spots.forEach(([x, z], i) => {
    const corner = i < 4;
    put(M.dark, at(new THREE.BoxGeometry(2.6, 0.7, 2.6), x, -0.6, z)); hulls.push(at(new THREE.BoxGeometry(2.74, 0.84, 2.74), x, -0.6, z));
    const y = -0.25;
    if (T.id === 'studio') {
      if (corner) { const pm = M.pal[i % M.pal.length]; put(M.metal, cyl(0.55, 0.55, 3.0, 24, x, y + 1.5, z)); put(pm, cyl(0.57, 0.57, 1.1, 24, x, y + 1.3, z)); put(pm, cyl(0.3, 0.3, 0.5, 16, x, y + 3.25, z)); hulls.push(cyl(0.62, 0.62, 3.14, 24, x, y + 1.5, z)); }
      else { put(M.cream, cyl(0.7, 0.62, 1.2, 24, x, y + 0.6, z)); for (let k = 0; k < 3; k++) { const a = k * 2.1 + i; put(M.bark, at(new THREE.CylinderGeometry(0.06, 0.06, 2.2, 8).rotateZ(Math.cos(a) * 0.25).rotateX(Math.sin(a) * 0.25), x + Math.cos(a) * 0.25, y + 1.6, z + Math.sin(a) * 0.25)); put(M.pal[(i + k) % M.pal.length], at(new THREE.ConeGeometry(0.13, 0.35, 10).rotateX(Math.PI), x + Math.cos(a) * 0.3, y + 2.75, z + Math.sin(a) * 0.3)); } }
    } else if (T.id === 'crypt') {
      if (corner) { put(M.stone, at(new THREE.CylinderGeometry(0.32, 0.75, 4.4, 4).rotateY(Math.PI / 4), x, y + 2.2, z)); put(M.stone, at(new THREE.ConeGeometry(0.4, 0.7, 4).rotateY(Math.PI / 4), x, y + 4.75, z)); hulls.push(at(new THREE.CylinderGeometry(0.38, 0.82, 4.5, 4).rotateY(Math.PI / 4), x, y + 2.2, z)); }
      else for (let k = 0; k < 3; k++) { const ox = (k - 1) * 0.55, hh = 0.5 + k % 2 * 0.35; put(M.cream, cyl(0.13, 0.13, hh, 10, x + ox, y + hh / 2, z)); flame(x + ox, y + hh + 0.22, z, 0.7); }
    } else if (T.id === 'cathedral') {
      put(M.stone, cyl(0.55, 0.55, 4.6, 20, x, y + 2.3, z)); put(M.gold, cyl(0.8, 0.62, 0.4, 20, x, y + 4.7, z)); put(M.stone, cyl(0.75, 0.85, 0.35, 20, x, y + 0.17, z)); hulls.push(cyl(0.62, 0.62, 4.7, 20, x, y + 2.3, z)); flame(x, y + 5.3, z, corner ? 1.6 : 1.1, 0xFFE6A6);
    } else if (T.id === 'manor') {
      put(M.gold, cyl(0.1, 0.16, 2.6, 12, x, y + 1.3, z)); put(M.gold, at(new THREE.BoxGeometry(1.5, 0.1, 0.1), x, y + 2.5, z)); put(M.gold, cyl(0.35, 0.3, 0.16, 12, x, y + 0.08, z));
      for (const ox of [-0.7, 0, 0.7]) { put(M.cream, cyl(0.08, 0.08, 0.42, 8, x + ox, y + 2.76, z)); flame(x + ox, y + 3.08, z, 0.6); }
    } else {
      if (corner) { put(M.bark, cyl(0.22, 0.3, 2.2, 10, x, y + 1.1, z)); put(M.leaf, ball(1.1, x, y + 2.7, z, 0.9)); put(M.leaf2, ball(0.75, x, y + 3.6, z, 0.9)); }
      else { put(M.dark, cyl(0.07, 0.07, 2.3, 8, x, y + 1.15, z)); put(M.glowY, at(new THREE.BoxGeometry(0.34, 0.42, 0.34), x, y + 2.45, z)); flame(x, y + 2.45, z, 1.2, 0xFFD27A); }
    }
  });
  // one big floor marking per canvas, somewhere open (the paint goes on top of it)
  const dm = decalMat(T), ds = 5.5 + R() * 3;
  for (let t = 0; t < 40; t++) {
    const x = (R() - 0.5) * (ARENA * 1.4), z = (R() - 0.5) * (ARENA * 1.4);
    let ok = true; for (let a = 0; a < 6.28 && ok; a += 0.5) for (const rr of [0, ds * 0.25, ds * 0.48]) { const px = x + Math.cos(a) * rr, pz = z + Math.sin(a) * rr; if (floorAt(px, pz) !== 0 || BOXES.some(b => inR(px, pz, b, 0.2)) || RAMPS.some(rp => inR(px, pz, rp, 0.2))) ok = false; }
    if (!ok) continue;
    const pg = new THREE.PlaneGeometry(ds, ds); pg.rotateX(-Math.PI / 2); pg.rotateY(R() * 6.28); pg.translate(x, 0.006, z);
    const dmesh = new THREE.Mesh(pg, dm); dmesh.renderOrder = 5; dmesh.receiveShadow = true; stageGroup.add(dmesh); break;
  }
  for (const [mat, list] of bag) { const m = new THREE.Mesh(mergeGeos(list, true), mat); m.castShadow = true; m.receiveShadow = true; stageGroup.add(m); }
  stageGroup.add(new THREE.Mesh(mergeGeos(lines), lineMat));
  stageGroup.add(new THREE.Mesh(mergeGeos(hulls), outlineMat));
}
// floor markings: a rune circle, a rose window, a rug, a ring of flowers, a color wheel
function decalMat(T) {
  if (T.decal) return T.decal;
  const tex = makeTex(512, (g, S) => {
    const c = S / 2, r = rng(91 + T.id.length);
    g.clearRect(0, 0, S, S); g.lineCap = 'round';
    if (T.id === 'crypt') { g.strokeStyle = 'rgba(120,230,215,0.55)'; for (const [rr, lw] of [[230, 7], [196, 4], [120, 4]]) { g.lineWidth = lw; g.beginPath(); g.arc(c, c, rr, 0, 6.2832); g.stroke(); } for (let k = 0; k < 24; k++) { const a = k / 24 * 6.2832; g.lineWidth = 3; g.beginPath(); g.moveTo(c + Math.cos(a) * 200, c + Math.sin(a) * 200); g.lineTo(c + Math.cos(a) * (k % 2 ? 214 : 226), c + Math.sin(a) * (k % 2 ? 214 : 226)); g.stroke(); } g.lineWidth = 5; g.beginPath(); for (let k = 0; k <= 6; k++) { const a = k / 6 * 6.2832 - 1.5708; k ? g.lineTo(c + Math.cos(a) * 190, c + Math.sin(a) * 190) : g.moveTo(c + Math.cos(a) * 190, c + Math.sin(a) * 190); } g.stroke(); }
    else if (T.id === 'cathedral') { for (let k = 0; k < 12; k++) { const a = k / 12 * 6.2832; g.fillStyle = k % 2 ? 'rgba(60,90,200,0.55)' : 'rgba(170,40,70,0.5)'; g.beginPath(); g.ellipse(c + Math.cos(a) * 140, c + Math.sin(a) * 140, 78, 36, a, 0, 6.2832); g.fill(); } g.strokeStyle = 'rgba(200,160,80,0.85)'; g.lineWidth = 8; for (const rr of [236, 84]) { g.beginPath(); g.arc(c, c, rr, 0, 6.2832); g.stroke(); } g.fillStyle = 'rgba(230,190,90,0.7)'; g.beginPath(); g.arc(c, c, 46, 0, 6.2832); g.fill(); }
    else if (T.id === 'manor') { g.fillStyle = 'rgba(70,30,90,0.82)'; g.beginPath(); g.ellipse(c, c, 240, 170, 0, 0, 6.2832); g.fill(); g.strokeStyle = 'rgba(214,170,90,0.9)'; g.lineWidth = 10; g.beginPath(); g.ellipse(c, c, 222, 152, 0, 0, 6.2832); g.stroke(); g.lineWidth = 4; g.beginPath(); g.ellipse(c, c, 196, 128, 0, 0, 6.2832); g.stroke(); for (let k = 0; k < 16; k++) { const a = k / 16 * 6.2832; g.fillStyle = 'rgba(214,170,90,0.8)'; g.beginPath(); g.arc(c + Math.cos(a) * 160, c + Math.sin(a) * 100, 8, 0, 6.2832); g.fill(); } }
    else if (T.id === 'garden') { for (let k = 0; k < 28; k++) { const a = k / 28 * 6.2832, rr = 200 + (r() - 0.5) * 30, x = c + Math.cos(a) * rr, y = c + Math.sin(a) * rr, col = ['rgba(240,240,255,0.9)', 'rgba(255,170,210,0.85)', 'rgba(170,190,255,0.85)'][k % 3]; for (let p = 0; p < 5; p++) { const pa = p / 5 * 6.2832; g.fillStyle = col; g.beginPath(); g.ellipse(x + Math.cos(pa) * 10, y + Math.sin(pa) * 10, 9, 5, pa, 0, 6.2832); g.fill(); } g.fillStyle = 'rgba(255,220,90,0.9)'; g.beginPath(); g.arc(x, y, 5, 0, 6.2832); g.fill(); } }
    else { for (let k = 0; k < 6; k++) { g.fillStyle = ['rgba(227,18,47,0.5)', 'rgba(255,210,63,0.5)', 'rgba(61,220,132,0.5)', 'rgba(46,155,255,0.5)', 'rgba(139,61,255,0.5)', 'rgba(255,106,26,0.5)'][k]; g.beginPath(); g.moveTo(c, c); g.arc(c, c, 230, k / 6 * 6.2832, (k + 1) / 6 * 6.2832); g.closePath(); g.fill(); } g.globalCompositeOperation = 'destination-out'; g.beginPath(); g.arc(c, c, 120, 0, 6.2832); g.fill(); g.globalCompositeOperation = 'source-over'; }
  });
  tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
  T.decal = new THREE.MeshToonMaterial({ map: tex, gradientMap: grad, color: 0xE0E0E0, transparent: false, blending: THREE.CustomBlending, blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneMinusSrcAlphaFactor, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
  return T.decal;
}

""")

# floaters: solid (opaque, drawn before the paint) unless they are fading
rep("if (Math.abs(f.k - f.last) > 0.004) { f.last = f.k; const solid = f.k > 0.97; for (const m of f.mats) { m.opacity = solid ? 1 : f.k; m.depthWrite = solid; } f.hull.material.opacity = f.k; f.hull.visible = f.k > 0.45; }",
    "if (Math.abs(f.k - f.last) > 0.004) { f.last = f.k; const solid = f.k > 0.97; for (const m of f.mats) { m.opacity = solid ? 1 : f.k; m.depthWrite = solid; m.transparent = !solid; } f.hull.material.opacity = f.k; f.hull.material.transparent = !solid; f.hull.visible = f.k > 0.45; }")
# candle flames flicker
rep("  for (const f of floaters) {\n    const b = f.b; let want = 1;", "  for (let i = 0; i < flames.length; i++) { const f = flames[i]; f.s.scale.setScalar(f.base * (0.86 + 0.12 * Math.sin(clock * 11 + i * 1.7) + 0.06 * Math.sin(clock * 23 + i * 3.1))); }\n  for (const f of floaters) {\n    const b = f.b; let want = 1;")

# ================= the generator: themes, round pieces, gravestones =================
rep("  const sym = pick(['rot', 'rot', 'rot', 'mirror', 'mirror', 'free']);",
    "  const sym = pick(['rot', 'rot', 'rot', 'mirror', 'mirror', 'free']), theme = pick(THEMES), TK = theme.kit;")
rep("  const imageOf = c => ({ boxes: c.boxes.map(b => [...imgR(b), b[4], b[5]]), ramps: c.ramps.map(imgRamp), holes: c.holes.map(imgR),",
    "  const imageOf = c => ({ boxes: c.boxes.map(b => [...imgR(b), b[4], b[5], ...b.slice(6)]), ramps: c.ramps.map(imgRamp), holes: c.holes.map(h => h[6] ? [...imgR(h), 0, 0, h[6]] : imgR(h)),")
rep("  const B = (x0, x1, z0, z1, y0, y1) => [q(x0), q(x1), q(z0), q(z1), y0, y1];",
    "  const B = (x0, x1, z0, z1, y0, y1) => [q(x0), q(x1), q(z0), q(z1), y0, y1];\n  const O = (cx, cz, r, y0, y1, kind) => { r = q(r); return [q(cx) - r, q(cx) + r, q(cz) - r, q(cz) + r, y0, y1, 'c', kind]; }; // a round piece, boxed by its square\n  // a ramp up to a round top meets it at a chord, slightly inside the circle\n  const innerBox = (b, w) => { const cx = (b[0] + b[1]) / 2, cz = (b[2] + b[3]) / 2, k = Math.sqrt(Math.max(0.5, ((b[1] - b[0]) / 2) ** 2 - (w / 2) ** 2)) - 0.12; return [cx - k, cx + k, cz - k, cz + k, b[4], b[5]]; };")
rep("    island(cx, cz) {", """    drum(cx, cz) { const r = rr(1.1, 2.0), h = q(rr(0.8, 1.0)), c = comp(), b = O(cx, cz, r, 0, h, 'drum'); c.boxes.push(b); fp(c, b, 'g', 0, h); return c; },
    column(cx, cz) { const r = rr(0.7, 1.05), h = q(rr(2.7, 3.4)), c = comp(), b = O(cx, cz, r, 0, h, 'column'); c.boxes.push(b); fp(c, b, 'g', 0, h); return c; },
    rpad(cx, cz) { const r = rr(1.7, 2.6), y0 = q(rr(0.92, 1.0)), c = comp(), b = O(cx, cz, r, y0, q(y0 + 0.3), 'rpad'); c.boxes.push(b); fp(c, b, 'a', b[4], b[5]); return c; },
    rotunda(cx, cz) { const r = rr(2.8, 3.9), h = q(rr(1.2, 1.5)), c = comp(), b = O(cx, cz, r, 0, h, 'rotunda'); c.boxes.push(b); fp(c, b, 'g', 0, h); const w = rr(2.2, 2.7), ib = innerBox(b, w), sd = shuffle(SIDES.slice()); ramp(c, ib, sd[0], 0.42, w, 0.5); if (R() < 0.5) ramp(c, ib, sd[1], 0.42, w, 0.5); return c; },
    rpit(cx, cz) { const r = q(rr(1.8, 3.0)), c = comp(), h = [q(cx) - r, q(cx) + r, q(cz) - r, q(cz) + r, 0, 0, 'c']; c.holes.push(h); fp(c, h, 'h'); return c; },
    tombs(cx, cz) { const n = ri(2, 4), alongX = R() < 0.5, gap = 1.7, c = comp(), h = q(rr(1.05, 1.25));
      for (let i = 0; i < n; i++) { const o = (i - (n - 1) / 2) * gap, x = alongX ? cx + o : cx, z = alongX ? cz : cz + o; const b = alongX ? [q(x - 0.45), q(x + 0.45), q(z - 0.17), q(z + 0.17), 0, h, 'g'] : [q(x - 0.17), q(x + 0.17), q(z - 0.45), q(z + 0.45), 0, h, 'g']; c.boxes.push(b); fp(c, b, 'g', 0, h); }
      return c; },
    island(cx, cz) {""")
# new centerpieces: a round plaza, and a round well with a floating disc in it
rep("  const arch = pick(['plaza', 'plaza', 'pit', 'spire', 'canopy', 'open']);", "  const arch = pick(['plaza', 'plaza', 'pit', 'spire', 'canopy', 'open', 'rotunda', 'well']);")
rep("  if (mid.foot.length && mid.foot.every(inBounds)) placed.push(mid);",
    """  else if (arch === 'rotunda') { const r = rr(4.2, 5.3), h = q(rr(1.3, 1.5)), b = O(0, 0, r, 0, h, 'rotunda'); mid.boxes.push(b); fp(mid, b, 'g', 0, h); const w = rr(2.4, 3.0), s2 = midSide(); twinRamp(mid, ramp(mid, innerBox(b, w), s2, 0.42, w, 0.5)); }
  else if (arch === 'well') { const r = rr(3.8, 4.8), h = [-q(r), q(r), -q(r), q(r), 0, 0, 'c']; mid.holes.push(h); fp(mid, h, 'h'); const gap = rr(1.0, 1.3), y0 = q(rr(0.92, 1.0)), b = O(0, 0, r - gap, y0, q(y0 + 0.3), 'rpad'); mid.boxes.push(b); fp(mid, b, 'a', b[4], b[5]); }
  if (mid.foot.length && mid.foot.every(inBounds)) placed.push(mid);""")
rep("  add('deck', 1, 2); add('tower', 1, 2); add('wall', 0, 1); add('corner', 0, 2); add('pad', 1, 2); add('block', 0, 2); add('pit', 0, 2); add('island', 0, 1); add('plateau', arch === 'plaza' ? 0 : 1, 1);",
    "  add('deck', 1, 2); add('tower', 1, 2); add('wall', 0, 1); add('corner', 0, 1); add('pad', 0, 2); add('block', 0, 1); add('pit', 0, 1); add('island', 0, 1); add('plateau', arch === 'plaza' || arch === 'rotunda' ? 0 : 1, 1);\n  for (const k in TK) add(k, TK[k][0], TK[k][1]); // the theme's own pieces")
rep("  const order = ['deck', 'plateau', 'island', 'tower', 'pit', 'pad', 'corner', 'block', 'wall'];", "  const order = ['deck', 'plateau', 'rotunda', 'island', 'tower', 'column', 'pit', 'rpit', 'pad', 'rpad', 'corner', 'tombs', 'drum', 'block', 'wall'];")
rep("place(kit[pick(['block', 'corner', 'pad', 'pit', 'tower'])](cx, cz)); }", "place(kit[pick(['block', 'corner', 'pad', 'pit', 'tower', theme.fill, theme.fill])](cx, cz)); }")
rep("  const out = { sym, arch, boxes: [], ramps: [], holes: [], clouds };", "  const out = { sym, arch, theme: theme.id, boxes: [], ramps: [], holes: [], clouds };")
rep("function applyLayout(L) {\n", "function applyLayout(L) {\n  applyThemeLook(THEME_BY[L.theme] || THEMES[0]);\n")
# the start banner names the map
rep("banner('Paint it red!', 'Beat the ' + diff + ' holy water in ' + MATCH_T + ' seconds', true);", "banner('Paint it red!', TH.label + ' · beat the ' + diff + ' holy water in ' + MATCH_T + ' seconds', true);")
open(F, 'w').write(s)
print('ok')
