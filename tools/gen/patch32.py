import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)

# ---- clouds take the theme's tint ----
rep("  TH = T; HOR.set(T.hor);", "  TH = T; HOR.set(T.hor); cloudMat.color.set(CLOUD_TINT[T.id] || 0xD9D4F2);")
rep("// the sky, fog and moonlight shift with the theme\n", "// the sky, fog and moonlight shift with the theme\nconst CLOUD_TINT = { studio: 0xD9D4F2, crypt: 0xA4C2C8, cathedral: 0xC2CAF0, manor: 0xE0C4E2, garden: 0xA6CCC0 };\n")

# ---- scattered floor marks: four per theme, picked and turned at random so no two canvases match ----
rep("// floor markings: a rune circle, a rose window, a rug, a ring of flowers, a color wheel\nfunction decalMat(T) {", r"""const decalOf = tex => new THREE.MeshToonMaterial({ map: tex, gradientMap: grad, color: 0xE0E0E0, transparent: false, blending: THREE.CustomBlending, blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneMinusSrcAlphaFactor, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });
function scatterMat(T) {
  if (T.scat) return T.scat;
  const tex = makeTex(1024, (g, S) => {
    const r = rng(77 + T.id.length * 13), id = T.id; g.clearRect(0, 0, S, S); g.lineCap = 'round'; g.lineJoin = 'round';
    const cell = (k, fn) => { g.save(); g.translate((k % 2) * 512 + 256, (k >> 1) * 512 + 256); g.beginPath(); g.rect(-246, -246, 492, 492); g.clip(); fn(); g.restore(); };
    const blob = (x, y, rx, ry, col, n) => { polyAt(g, lumpy(r, rx, ry, n || 11), x, y, r() * 6.28); g.fillStyle = col; g.fill(); };
    const disc = (x, y, rr, col) => { g.fillStyle = col; g.beginPath(); g.arc(x, y, rr, 0, 6.2832); g.fill(); };
    const crack = (col, lw) => { g.strokeStyle = col; const br = (x, y, a, L, w, d) => { if (d > 4 || L < 12) return; g.lineWidth = w; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 4; k++) { a += (r() - 0.5) * 0.9; x += Math.cos(a) * L / 4; y += Math.sin(a) * L / 4; g.lineTo(x, y); } g.stroke(); br(x, y, a + 0.45 + r() * 0.4, L * 0.65, w * 0.7, d + 1); if (r() < 0.6) br(x, y, a - 0.45 - r() * 0.4, L * 0.55, w * 0.65, d + 1); }; br(-200, 10, -0.15, 170, lw, 0); br(-200, 10, 2.8, 50, lw * 0.7, 2); };
    const star = (n, R0, R1, rot) => { g.beginPath(); for (let k = 0; k <= n * 2; k++) { const a = k / (n * 2) * 6.2832 + rot, rr = k % 2 ? R1 : R0; k ? g.lineTo(Math.cos(a) * rr, Math.sin(a) * rr) : g.moveTo(Math.cos(a) * rr, Math.sin(a) * rr); } g.closePath(); };
    const leaf = (x, y, L, W, rot, col) => { g.save(); g.translate(x, y); g.rotate(rot); g.fillStyle = col; g.beginPath(); g.moveTo(-L, 0); g.quadraticCurveTo(0, -W * 2, L, 0); g.quadraticCurveTo(0, W * 2, -L, 0); g.fill(); g.strokeStyle = 'rgba(60,40,20,0.45)'; g.lineWidth = 2; g.beginPath(); g.moveTo(-L * 0.9, 0); g.lineTo(L * 0.85, 0); g.stroke(); g.restore(); };
    const flower = (x, y, rr, col) => { for (let p = 0; p < 5; p++) { const a = p / 5 * 6.2832; g.fillStyle = col; g.beginPath(); g.ellipse(x + Math.cos(a) * rr, y + Math.sin(a) * rr, rr * 0.95, rr * 0.55, a, 0, 6.2832); g.fill(); } disc(x, y, rr * 0.55, 'rgba(255,214,90,0.95)'); };
    if (id === 'studio') {
      // a pencil sketch, a taped X, a paint-can ring, a dry brush stroke
      cell(0, () => { g.strokeStyle = 'rgba(52,52,74,0.55)'; for (let l = 0; l < 3; l++) { g.lineWidth = 2.5 + r() * 1.5; g.beginPath(); const ox = (r() - 0.5) * 14, oy = (r() - 0.5) * 14, rr = 140 + r() * 18; for (let k = 0; k <= 44; k++) { const a = k / 40 * 6.2832 + l, w = rr + Math.sin(k * 0.7 + l) * 5; k ? g.lineTo(ox + Math.cos(a) * w, oy + Math.sin(a) * w) : g.moveTo(ox + Math.cos(a) * w, oy + Math.sin(a) * w); } g.stroke(); }
        g.strokeStyle = 'rgba(52,52,74,0.32)'; g.lineWidth = 2; for (const a of [0.3, 1.87]) { g.beginPath(); g.moveTo(Math.cos(a) * -215, Math.sin(a) * -215); g.lineTo(Math.cos(a) * 215, Math.sin(a) * 215); g.stroke(); }
        for (let k = 0; k < 12; k++) { g.beginPath(); g.moveTo(40 + k * 9, 40); g.lineTo(10 + k * 9, 100); g.stroke(); } });
      cell(1, () => { const tape = (rot, col, dx, dy) => { g.save(); g.translate(dx, dy); g.rotate(rot); g.fillStyle = col; g.beginPath(); g.moveTo(-200, -32); g.lineTo(200, -32); for (let k = 1; k <= 6; k++) g.lineTo(200 + (k % 2 ? 9 : 0), -32 + k * 64 / 6); g.lineTo(-200, 32); for (let k = 1; k <= 6; k++) g.lineTo(-200 - (k % 2 ? 9 : 0), 32 - k * 64 / 6); g.closePath(); g.fill(); g.restore(); };
        for (const a of [0.78, -0.78]) tape(a, 'rgba(0,0,0,0.12)', 5, 7); for (const a of [0.78, -0.78]) { tape(a, 'rgba(232,214,168,0.94)', 0, 0); g.save(); g.rotate(a); g.fillStyle = 'rgba(255,255,255,0.22)'; g.fillRect(-196, -28, 392, 8); g.restore(); } });
      cell(2, () => { g.strokeStyle = 'rgba(255,206,60,0.8)'; g.lineWidth = 22; const a0 = r() * 6.28; g.beginPath(); g.arc(0, 0, 150, a0, a0 + 5.5); g.stroke(); g.lineWidth = 7; g.strokeStyle = 'rgba(255,206,60,0.5)'; g.beginPath(); g.arc(12, -8, 168, a0 + 1, a0 + 3.6); g.stroke();
        for (let k = 0; k < 7; k++) { const a = a0 + r() * 5.5, rr = 160 + r() * 40; disc(Math.cos(a) * rr, Math.sin(a) * rr, 5 + r() * 12, 'rgba(255,206,60,0.75)'); } });
      cell(3, () => { const pts = t => [-205 + t * 410, 50 * Math.sin(t * 3.2 + 0.4) - 30 * t]; for (let k = 0; k < 30; k++) { const off = -48 + k * 3.3 + (r() - 0.5) * 3, end = 0.55 + r() * 0.45; g.strokeStyle = `rgba(${50 + r() * 30 | 0},${190 + r() * 40 | 0},${120 + r() * 30 | 0},${0.25 + r() * 0.4})`; g.lineWidth = 2 + r() * 4; g.beginPath(); for (let i = 0; i <= 30; i++) { const t = i / 30 * end, p = pts(t); i ? g.lineTo(p[0], p[1] + off) : g.moveTo(p[0], p[1] + off); } g.stroke(); } });
    } else if (id === 'crypt') {
      // a crack, a moss patch, scattered bones, a small sigil
      cell(0, () => crack('rgba(8,10,16,0.72)', 7));
      cell(1, () => { for (let k = 0; k < 16; k++) { const a = r() * 6.28, d = r() * 140; blob(Math.cos(a) * d, Math.sin(a) * d, 26 + r() * 40, 20 + r() * 34, k % 3 ? 'rgba(58,104,60,0.55)' : 'rgba(92,142,82,0.5)'); } for (let k = 0; k < 140; k++) { const a = r() * 6.28, d = r() * 175; disc(Math.cos(a) * d, Math.sin(a) * d, 1.5 + r() * 2.5, `rgba(${120 + r() * 50 | 0},${170 + r() * 40 | 0},${100 + r() * 30 | 0},0.6)`); } });
      cell(2, () => { const bone = (x, y, L, rot) => { g.save(); g.translate(x, y); g.rotate(rot); for (const [col, e] of [['rgba(30,28,40,0.55)', 4], ['rgba(232,224,200,0.95)', 0]]) { g.fillStyle = col; g.fillRect(-L / 2, -9 - e, L, 18 + e * 2); for (const sx of [-1, 1]) for (const sy of [-1, 1]) { g.beginPath(); g.arc(sx * L / 2, sy * 10, 14 + e, 0, 6.2832); g.fill(); } } g.restore(); };
        bone(-30, -40, 190, 0.5); bone(20, 30, 170, -0.7); bone(-90, 90, 110, 1.9); });
      cell(3, () => { g.strokeStyle = 'rgba(120,230,215,0.5)'; g.lineWidth = 5; g.beginPath(); g.arc(0, 0, 160, 0, 6.2832); g.stroke(); g.lineWidth = 3; g.beginPath(); g.arc(0, 0, 130, 0, 6.2832); g.stroke(); g.lineWidth = 5; star(3, 130, 130 * 0.5, -1.5708); g.stroke(); for (let k = 0; k < 3; k++) { const a = k / 3 * 6.2832 - 1.5708; disc(Math.cos(a) * 130, Math.sin(a) * 130, 12, 'rgba(120,230,215,0.55)'); } g.lineWidth = 4; for (let k = 0; k < 8; k++) { const a = k / 8 * 6.2832 + 0.2; g.beginPath(); g.moveTo(Math.cos(a) * 172, Math.sin(a) * 172); g.lineTo(Math.cos(a + 0.12) * 196, Math.sin(a + 0.12) * 196); g.lineTo(Math.cos(a + 0.2) * 180, Math.sin(a + 0.2) * 180); g.stroke(); } });
    } else if (id === 'cathedral') {
      // colored light from the windows, a gold compass, a hairline crack, a quatrefoil of light
      cell(0, () => { g.beginPath(); g.moveTo(-100, 220); g.lineTo(-100, -40); g.quadraticCurveTo(-100, -170, 0, -226); g.quadraticCurveTo(100, -170, 100, -40); g.lineTo(100, 220); g.closePath(); g.clip();
        const cols = ['rgba(255,214,120,0.34)', 'rgba(120,220,210,0.3)', 'rgba(176,136,255,0.32)', 'rgba(150,230,140,0.28)']; for (let i = 0; i < 3; i++) for (let j = 0; j < 7; j++) { g.fillStyle = cols[(i + j * 2) % 4]; g.fillRect(-100 + i * 68 + 4, -230 + j * 66 + 4, 60, 58); } });
      cell(1, () => { g.fillStyle = 'rgba(214,176,90,0.55)'; star(4, 210, 60, 0); g.fill(); g.strokeStyle = 'rgba(160,120,50,0.85)'; g.lineWidth = 4; g.stroke(); g.fillStyle = 'rgba(214,176,90,0.4)'; star(4, 140, 50, 0.785); g.fill(); g.stroke(); g.lineWidth = 5; g.beginPath(); g.arc(0, 0, 95, 0, 6.2832); g.stroke(); });
      cell(2, () => crack('rgba(80,80,104,0.5)', 4));
      cell(3, () => { const cols = ['rgba(255,196,140,0.3)', 'rgba(120,220,210,0.28)', 'rgba(176,136,255,0.3)', 'rgba(255,214,120,0.3)']; for (let k = 0; k < 4; k++) { const a = k / 4 * 6.2832; disc(Math.cos(a) * 80, Math.sin(a) * 80, 92, cols[k]); } g.fillStyle = 'rgba(255,230,170,0.4)'; star(4, 60, 22, 0); g.fill(); });
    } else if (id === 'manor') {
      // a runner, a round rug, a wood inlay star, a pool of candlelight
      cell(0, () => { g.fillStyle = 'rgba(26,74,58,0.92)'; g.fillRect(-200, -112, 400, 224); g.strokeStyle = 'rgba(214,170,90,0.9)'; g.lineWidth = 9; g.strokeRect(-184, -96, 368, 192); g.lineWidth = 3; g.strokeRect(-166, -78, 332, 156); g.fillStyle = 'rgba(214,170,90,0.75)'; g.beginPath(); g.moveTo(0, -56); g.lineTo(72, 0); g.lineTo(0, 56); g.lineTo(-72, 0); g.closePath(); g.fill();
        g.strokeStyle = 'rgba(236,224,196,0.9)'; g.lineWidth = 3; for (const sx of [-1, 1]) for (let k = 0; k < 18; k++) { const y = -104 + k * 12.2; g.beginPath(); g.moveTo(sx * 200, y); g.lineTo(sx * 222, y + (r() - 0.5) * 4); g.stroke(); } });
      cell(1, () => { disc(0, 0, 214, 'rgba(36,86,98,0.9)'); g.strokeStyle = 'rgba(214,170,90,0.9)'; g.lineWidth = 9; g.beginPath(); g.arc(0, 0, 196, 0, 6.2832); g.stroke(); g.lineWidth = 4; g.beginPath(); g.arc(0, 0, 150, 0, 6.2832); g.stroke(); for (let k = 0; k < 12; k++) { const a = k / 12 * 6.2832; g.fillStyle = 'rgba(214,170,90,0.8)'; g.beginPath(); g.ellipse(Math.cos(a) * 108, Math.sin(a) * 108, 26, 11, a, 0, 6.2832); g.fill(); } disc(0, 0, 44, 'rgba(236,214,170,0.85)'); });
      cell(2, () => { g.fillStyle = 'rgba(226,182,122,0.55)'; star(8, 190, 80, 0); g.fill(); g.strokeStyle = 'rgba(80,40,20,0.5)'; g.lineWidth = 3; g.stroke(); g.beginPath(); g.arc(0, 0, 212, 0, 6.2832); g.lineWidth = 5; g.strokeStyle = 'rgba(226,182,122,0.5)'; g.stroke(); });
      cell(3, () => { const gr = g.createRadialGradient(0, 0, 0, 0, 0, 236); gr.addColorStop(0, 'rgba(255,206,130,0.5)'); gr.addColorStop(0.5, 'rgba(255,190,110,0.22)'); gr.addColorStop(1, 'rgba(255,180,100,0)'); g.fillStyle = gr; g.fillRect(-246, -246, 492, 492); });
    } else {
      // stepping stones, fallen leaves, a clump of flowers, a fairy ring of mushrooms
      cell(0, () => { for (let k = 0; k < 3; k++) { const x = -140 + k * 140, y = 60 - k * 60 + (r() - 0.5) * 30, rx = 62 + r() * 14, ry = 50 + r() * 12, pts = lumpy(r, rx, ry, 12), rot = r() * 6.28; polyAt(g, pts.map(p => [p[0] * 1.08, p[1] * 1.08]), x + 4, y + 6, rot); g.fillStyle = 'rgba(20,30,24,0.5)'; g.fill(); polyAt(g, pts, x, y, rot); g.fillStyle = 'rgba(150,152,162,0.96)'; g.fill(); polyAt(g, pts.map(p => [p[0] * 0.6, p[1] * 0.6]), x - 10, y - 10, rot); g.fillStyle = 'rgba(255,255,255,0.14)'; g.fill(); } });
      cell(1, () => { const cols = ['rgba(222,130,48,0.92)', 'rgba(232,192,70,0.92)', 'rgba(140,146,60,0.92)', 'rgba(196,98,40,0.9)']; for (let k = 0; k < 15; k++) { const a = r() * 6.28, d = r() * 170; leaf(Math.cos(a) * d, Math.sin(a) * d, 26 + r() * 14, 9 + r() * 5, r() * 6.28, cols[k % 4]); } });
      cell(2, () => { for (let k = 0; k < 9; k++) { const a = r() * 6.28, d = r() * 120; blob(Math.cos(a) * d, Math.sin(a) * d, 40 + r() * 30, 26 + r() * 20, 'rgba(46,104,56,0.82)', 9); } const cols = ['rgba(244,244,255,0.95)', 'rgba(255,176,214,0.92)', 'rgba(184,170,255,0.92)']; for (let k = 0; k < 11; k++) { const a = r() * 6.28, d = r() * 150; flower(Math.cos(a) * d, Math.sin(a) * d, 12 + r() * 7, cols[k % 3]); } });
      cell(3, () => { for (let k = 0; k < 11; k++) { const a = k / 11 * 6.2832 + r() * 0.2, d = 160 + (r() - 0.5) * 26, x = Math.cos(a) * d, y = Math.sin(a) * d, cr = 17 + r() * 10; disc(x + 3, y + 4, cr + 4, 'rgba(20,30,24,0.45)'); disc(x, y, cr + 3, 'rgba(40,24,60,0.85)'); disc(x, y, cr, 'rgba(176,126,226,0.96)'); for (let p = 0; p < 3; p++) disc(x + (r() - 0.5) * cr, y + (r() - 0.5) * cr, 2.5 + r() * 2.5, 'rgba(250,244,230,0.95)'); } });
    }
  });
  tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
  T.scat = decalOf(tex); return T.scat;
}
// floor markings: a rune circle, a rose window, a rug, a ring of flowers, a color wheel
function decalMat(T) {""")

# place them: over the open floor and the big grounded tops, never on a floater or a ramp
rep("""    const dmesh = new THREE.Mesh(pg, dm); dmesh.renderOrder = 5; dmesh.receiveShadow = true; stageGroup.add(dmesh); break;
  }""", """    const dmesh = new THREE.Mesh(pg, dm); dmesh.renderOrder = 5; dmesh.receiveShadow = true; stageGroup.add(dmesh); taken.push([x, z, ds * 0.5]); break;
  }
  const sgs = [], nS = 9 + (R() * 6 | 0), cells = [0, 1, 2, 3, 0, 1, 2, 3].sort(() => R() - 0.5);
  for (let t = 0, n = 0; t < 220 && n < nS; t++) {
    const sz = 2.4 + R() * 2.4, x = (R() - 0.5) * (ARENA * 1.84), z = (R() - 0.5) * (ARENA * 1.84), y = surfaceUnder(x, z, 40);
    if (y < -0.5 || taken.some(o => Math.hypot(o[0] - x, o[1] - z) < o[2] + sz * 0.5)) continue;
    let ok = true; for (let a = 0; a < 6.28 && ok; a += 0.6) for (const rr of [0, sz * 0.3, sz * 0.46]) { const px = x + Math.cos(a) * rr, pz = z + Math.sin(a) * rr; if (Math.abs(surfaceUnder(px, pz, 40) - y) > 0.01 || Math.abs(px) > ARENA - 0.3 || Math.abs(pz) > ARENA - 0.3 || RAMPS.some(rp => inR(px, pz, rp, 0.15)) || BOXES.some(b => b[4] > 0 && inR(px, pz, b, 0.3)) || BOXES.some(b => b[5] > y + 0.01 && b[4] <= y + 0.01 && inR(px, pz, b, 0.12))) ok = false; }
    if (!ok) continue;
    const pg = new THREE.PlaneGeometry(sz, sz), uv = pg.attributes.uv, k = cells[n % cells.length], cu = (k % 2) * 0.5, cv = (1 - (k >> 1)) * 0.5;
    for (let i = 0; i < uv.count; i++) uv.setXY(i, cu + uv.getX(i) * 0.5, cv + uv.getY(i) * 0.5);
    pg.rotateX(-Math.PI / 2); pg.rotateY(R() * 6.28); pg.translate(x, y + 0.008, z); sgs.push(pg); taken.push([x, z, sz * 0.5]); n++;
  }
  if (sgs.length) { const sm = new THREE.Mesh(mergeGeos(sgs, true), scatterMat(T)); sm.renderOrder = 5; sm.receiveShadow = true; stageGroup.add(sm); }
  setMotes(T);""")
rep("  const dm = decalMat(T), ds = 5.5 + R() * 3;", "  const dm = decalMat(T), ds = 5.5 + R() * 3, taken = [];")
rep("""  T.decal = new THREE.MeshToonMaterial({ map: tex, gradientMap: grad, color: 0xE0E0E0, transparent: false, blending: THREE.CustomBlending, blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneMinusSrcAlphaFactor, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 });""",
    "  T.decal = decalOf(tex);")

# ---- ambient motes: pigment dust, crypt wisps, gold dust, candle embers, fireflies ----
rep("const glowSprite = sz => {", r"""const MOTE_N = 64, moteGeo = new THREE.BufferGeometry(), motePos = new Float32Array(MOTE_N * 3), moteCol = new Float32Array(MOTE_N * 3), moteSeed = [];
moteGeo.setAttribute('position', new THREE.BufferAttribute(motePos, 3)); moteGeo.setAttribute('color', new THREE.BufferAttribute(moteCol, 3));
const moteMat = new THREE.PointsMaterial({ map: glowTex, size: 0.5, sizeAttenuation: true, vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false });
const motes = new THREE.Points(moteGeo, moteMat); motes.frustumCulled = false; motes.renderOrder = 9; scene.add(motes);
const MOTE_LOOK = {
  studio: { cols: [0xFFD23F, 0xB98CFF, 0x6CF0A8, 0xFF9A5A], size: 0.34, rise: 0.12, blink: 0.15, sway: 0.6 },
  crypt: { cols: [0x7FF0DA, 0x4FC8B4, 0xB8FFF0], size: 0.62, rise: 0.32, blink: 0.45, sway: 0.9 },
  cathedral: { cols: [0xFFE3A0, 0xFFF4D6], size: 0.28, rise: 0.05, blink: 0.25, sway: 0.35 },
  manor: { cols: [0xFFB04A, 0xFF8A3A, 0xFFD27A], size: 0.3, rise: 0.55, blink: 0.35, sway: 0.45 },
  garden: { cols: [0xD8FF6A, 0xFFF07A, 0xB0FF8A], size: 0.5, rise: 0.04, blink: 1, sway: 1.2 },
};
let moteLook = MOTE_LOOK.studio;
function setMotes(T) {
  moteLook = MOTE_LOOK[T.id] || MOTE_LOOK.studio; moteMat.size = moteLook.size; const r = rng(((GEN.seed || 1) * 3 + 5) >>> 0), c = new THREE.Color(); moteSeed.length = 0;
  for (let i = 0; i < MOTE_N; i++) { c.set(moteLook.cols[i % moteLook.cols.length]); moteSeed.push({ x: (r() - 0.5) * ARENA * 2.3, z: (r() - 0.5) * ARENA * 2.3, y: 0.4 + r() * 6.4, p: r() * 6.28, f: 0.55 + r() * 0.9, cr: c.r, cg: c.g, cb: c.b }); }
}
function updateMotes(dt) {
  const L = moteLook, t = clock;
  for (let i = 0; i < moteSeed.length; i++) {
    const m = moteSeed[i]; m.y += L.rise * m.f * dt; if (m.y > 7.2) m.y = 0.3;
    motePos[i * 3] = m.x + Math.sin(t * 0.5 * m.f + m.p) * L.sway; motePos[i * 3 + 1] = m.y + Math.sin(t * 1.1 * m.f + m.p) * 0.25; motePos[i * 3 + 2] = m.z + Math.cos(t * 0.42 * m.f + m.p * 1.3) * L.sway;
    const fade = Math.max(0, Math.min(1, m.y / 0.9, (7.2 - m.y) / 0.9)), w = Math.sin(t * 1.9 * m.f + m.p * 3), bl = 1 - L.blink + L.blink * (L.blink >= 1 ? Math.pow(Math.max(0, w), 3) : 0.5 + 0.5 * w), k = fade * bl;
    moteCol[i * 3] = m.cr * k; moteCol[i * 3 + 1] = m.cg * k; moteCol[i * 3 + 2] = m.cb * k;
  }
  moteGeo.attributes.position.needsUpdate = true; moteGeo.attributes.color.needsUpdate = true;
}
const glowSprite = sz => {""")
rep("  for (let i = 0; i < flames.length; i++) { const f = flames[i];", "  updateMotes(rdt);\n  for (let i = 0; i < flames.length; i++) { const f = flames[i];")
rep("sky, ...moverMeshes,", "sky, motes, ...moverMeshes,")
open(F, 'w').write(s)
print('ok')
