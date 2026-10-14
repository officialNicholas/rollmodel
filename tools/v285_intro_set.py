"""v285: the first launch's desert set, the sandstone rocks and the agaves, remade (a patch over the intro, tools/v257_intro.js).

Rocks: were 80-triangle faceted lumps with flat banded colour. Now weathered sandstone boulders: rounded by the wind (a smooth, lumpy
surface, 320 to 1280 triangles each, about 7k for the lot), with ledges worn along their beds, flat underneath where they sit in the
sand. Painted with a sandstone texture made on the spot: level strata in warm reds, oranges and pale bands with thin dark seams,
mottling, grain, small weathering pits and dark streaks of desert varnish running down, all tiling round the rock so the beds line
up level on every rock; a normal map from the same heights gives the grain, the seams and the pits real relief in the light. Darker
low down where they meet the sand and in their hollows, a touch lighter where sand settles on top.

Agaves: were 13 flat strips each. Now a rosette of thick, channelled leaves laid out in a spiral (the golden angle), 22 to a plant:
the young ones in the middle short and upright, the old ones long and arching out toward the sand. Each leaf is a V-section blade
(32 triangles), widest a third of the way up and drawn to a point, with a leaf texture: pale at the base, glaucous blue-green going
darker to the tip, lighter margins with small dark teeth along them (cut into the outline), a lighter midrib, the faint chevrons a
leaf's neighbours leave on it (bud prints), a dusty bloom, and a dark terminal spine. Shaded darker deep in the rosette. They still
sway in the wind. About 2.8k triangles for the four.

The rocks' and agaves' places and sizes are the same, so the shadows on the sand and the character's way round them are unchanged."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HELPERS = r"""
    // (v285) a smooth surface from non-indexed triangles: each corner gets the average of the faces that meet there (by position)
    const smoothN = g => { const P = g.attributes.position, n = P.count, acc = new Map(), a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), e1 = new THREE.Vector3(), e2 = new THREE.Vector3(), keys = new Array(n);
      for (let i = 0; i < n; i++) keys[i] = Math.round(P.getX(i) * 2e4) + ',' + Math.round(P.getY(i) * 2e4) + ',' + Math.round(P.getZ(i) * 2e4);
      for (let i = 0; i < n; i += 3) { a.fromBufferAttribute(P, i); b.fromBufferAttribute(P, i + 1); c.fromBufferAttribute(P, i + 2); e1.subVectors(b, a); e2.subVectors(c, a); e1.cross(e2);
        for (let j = 0; j < 3; j++) { const k = keys[i + j], v = acc.get(k); if (v) v.add(e1); else acc.set(k, e1.clone()); } }
      const N = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const v = acc.get(keys[i]).clone().normalize(); N[i * 3] = v.x; N[i * 3 + 1] = v.y; N[i * 3 + 2] = v.z; }
      g.setAttribute('normal', new THREE.BufferAttribute(N, 3)); return g; };
    // (value noise, smooth, in 3D; and three octaves of it)
    const h3 = (x, y, z) => { const q = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453; return q - Math.floor(q); };
    const vn = (x, y, z) => { const ix = Math.floor(x), iy = Math.floor(y), iz = Math.floor(z), fx = x - ix, fy = y - iy, fz = z - iz, u = fx * fx * (3 - 2 * fx), v = fy * fy * (3 - 2 * fy), w = fz * fz * (3 - 2 * fz); let r = 0;
      for (let p = 0; p < 2; p++) for (let q = 0; q < 2; q++) for (let t = 0; t < 2; t++) r += h3(ix + p, iy + q, iz + t) * (p ? u : 1 - u) * (q ? v : 1 - v) * (t ? w : 1 - w); return r * 2 - 1; };
    const fbm = (x, y, z) => vn(x, y, z) * 0.6 + vn(x * 2.1 + 5.2, y * 2.1, z * 2.1) * 0.28 + vn(x * 4.3, y * 4.3 + 1.7, z * 4.3) * 0.12;
"""

ROCKS = r"""    // rocks: (v285) weathered sandstone boulders, rounded by the wind, ledges worn along their beds, painted strata with relief
    { const gs = []; seed = 31;
      // the sandstone, painted once: level beds (tiling round the rock and up it), seams, mottling, grain, pits, desert varnish; and its relief
      const TW = 512, TH = 256, hgt = new Float32Array(TW * TH);
      const bed = new Float32Array(TH * 2); { let y = 0, k = 0; while (y < TH * 2) { const w = 3 + Math.floor(rand() * 14), tone = rand(); for (let i = 0; i < w && y < TH * 2; i++, y++) bed[y] = tone; k++; } for (let i = 0; i < TH; i++) bed[i] = bed[i] * 0.5 + bed[i + TH] * 0.5; }
      const PAL = [[0.50, 0.22, 0.13], [0.66, 0.31, 0.17], [0.78, 0.43, 0.24], [0.86, 0.55, 0.33], [0.91, 0.66, 0.44]];
      const pal = t => { const f = Math.min(0.999, Math.max(0, t)) * (PAL.length - 1), i = Math.floor(f), u = f - i, a = PAL[i], b = PAL[i + 1]; return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u]; };
      const rockTex = canvasTex(TW, TH, (g, W, H) => {
        const im = g.createImageData(W, H), d = im.data, tau = 6.2832;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
          const wob = 3.2 * Math.sin(x / W * tau * 2 + 1.3) + 1.6 * Math.sin(x / W * tau * 5 + y * 0.02) + 0.8 * Math.sin(x / W * tau * 11 + 2.1), yy = ((y + wob) % H + H) % H, i0 = Math.floor(yy), fr = yy - i0;
          const b = bed[i0] * (1 - fr) + bed[(i0 + 1) % H] * fr, seam = Math.max(0, 1 - Math.abs(fr - 0.5) * 2) * (bed[i0] !== bed[(i0 + 1) % H] ? 1 : 0);
          const mot = 0.5 * Math.sin(x / W * tau * 3 + y / H * tau * 2) + 0.3 * Math.sin(x / W * tau * 7 - y / H * tau * 5 + 1.1) + 0.2 * Math.sin(x / W * tau * 13 + y / H * tau * 9);
          const grain = Math.random() - 0.5, c = pal(0.25 + 0.6 * b + 0.08 * mot);
          const v = 1 + 0.12 * grain - 0.28 * seam;
          const o = (y * W + x) * 4; d[o] = Math.min(255, c[0] * v * 255); d[o + 1] = Math.min(255, c[1] * v * 255); d[o + 2] = Math.min(255, c[2] * v * 255); d[o + 3] = 255;
          hgt[y * W + x] = 0.55 * b + 0.12 * mot + 0.18 * grain - 0.6 * seam; }
        g.putImageData(im, 0, 0);
        // desert varnish: dark streaks running down from the tops of ledges; weathering pits (tafoni), each a dark cup with a lit rim
        for (let i = 0; i < 38; i++) { const x = rnd(0, W), y = rnd(0, H), w = rnd(2, 9), l = rnd(20, 90), gr = g.createLinearGradient(0, y, 0, y + l); gr.addColorStop(0, 'rgba(40,16,8,.28)'); gr.addColorStop(1, 'rgba(40,16,8,0)'); g.fillStyle = gr; for (const ox of [0, -W, W]) g.fillRect(x + ox, y, w, l); }
        for (let i = 0; i < 55; i++) { const x = rnd(0, W), y = rnd(0, H), r = rnd(1.5, 6), ry = r * rnd(0.5, 0.85); for (const ox of [0, -W, W]) { g.fillStyle = 'rgba(52,20,10,.5)'; g.beginPath(); g.ellipse(x + ox, y, r, ry, 0, 0, 6.2832); g.fill(); g.fillStyle = 'rgba(255,214,170,.18)'; g.beginPath(); g.ellipse(x + ox, y + ry * 0.7, r * 0.9, ry * 0.35, 0, 0, 3.1416); g.fill(); }
          for (let yy = Math.max(0, Math.floor(y - ry)); yy < Math.min(H, Math.ceil(y + ry)); yy++) for (let xx = Math.floor(x - r); xx < Math.ceil(x + r); xx++) { const q = ((xx - x) / r) ** 2 + ((yy - y) / ry) ** 2; if (q < 1) hgt[yy * W + ((xx % W) + W) % W] -= 0.8 * (1 - q); } } });
      const rockNrm = canvasTex(TW, TH, (g, W, H) => { const im = g.createImageData(W, H), d = im.data, at = (x, y) => hgt[((y + H) % H) * W + ((x + W) % W)], k = 2.2;
        for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const nx = (at(x - 1, y) - at(x + 1, y)) * k, ny = (at(x, y + 1) - at(x, y - 1)) * k, l = Math.hypot(nx, ny, 1), o = (y * W + x) * 4; d[o] = (nx / l * 0.5 + 0.5) * 255; d[o + 1] = (ny / l * 0.5 + 0.5) * 255; d[o + 2] = (1 / l * 0.5 + 0.5) * 255; d[o + 3] = 255; }
        g.putImageData(im, 0, 0); }, false);
      for (const t of [rockTex, rockNrm]) { t.wrapS = t.wrapT = THREE.RepeatWrapping; }
      ROCKS.forEach(([x, z, sx, sy, sz], ri) => { const g = new THREE.IcosahedronGeometry(1, sx > 0.28 ? 3 : 2), P = g.attributes.position, n = P.count, o = ri * 3.7 + 1.3, rot = rnd(0, 6.28), cr = Math.cos(rot), sr = Math.sin(rot), uv = new Float32Array(n * 2);
        for (let i = 0; i < n; i++) { const dx = P.getX(i), dy = P.getY(i), dz = P.getZ(i);
          let k = 1 + 0.2 * fbm(dx * 1.5 + o, dy * 1.5, dz * 1.5 - o);
          k *= 1 - 0.075 * Math.pow(Math.abs(Math.sin((dy + 0.12 * fbm(dx * 3 + o, 0.5, dz * 3)) * 5.2 + o)), 5); // (the softer beds worn back into ledges)
          const px = dx * k * sx, pz = dz * k * sz; let py = Math.max(-0.14, dy * k) * sy + sy * 0.13; // (flat underneath, down in the sand)
          P.setXYZ(i, px * cr - pz * sr + x, py, px * sr + pz * cr + z);
          uv[i * 2] = Math.atan2(dz, dx) / 6.2832 + 0.5; uv[i * 2 + 1] = py / 0.85 + ri * 0.37; }
        for (let i = 0; i < n; i += 3) { const a = uv[i * 2], b = uv[i * 2 + 2], c = uv[i * 2 + 4]; if (Math.max(a, b, c) - Math.min(a, b, c) > 0.5) for (let j = 0; j < 3; j++) if (uv[(i + j) * 2] < 0.5) uv[(i + j) * 2] += 1; } // (a triangle across the seam takes its u from one side)
        { const reps = Math.max(1, Math.round(6.2832 * (sx + sz) * 0.5 / 1.5)); for (let i = 0; i < n; i++) uv[i * 2] *= reps; } // (about as many texels round it as up it: a big rock wraps the picture twice)
        g.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); smoothN(g);
        // darker low down where it meets the sand and in the hollows, a touch lighter and sandier where sand settles on top
        const N = g.attributes.normal, col = new Float32Array(n * 3), tint = 0.94 + 0.12 * rand();
        for (let i = 0; i < n; i++) { const py = P.getY(i), ny = N.getY(i), ao = 0.5 + 0.5 * Math.min(1, py / (0.22 * sy + 0.02)), up = Math.max(0, (ny - 0.55) / 0.45), dust = up * up * 0.22;
          col[i * 3] = ao * tint * (1 + dust * 0.9); col[i * 3 + 1] = ao * tint * (1 + dust * 0.75); col[i * 3 + 2] = ao * tint * (1 + dust * 0.45); }
        g.setAttribute('color', new THREE.BufferAttribute(col, 3)); gs.push(g); });
      const m = dofMap(new THREE.MeshStandardMaterial({ map: rockTex, normalMap: rockNrm, normalScale: new THREE.Vector2(1.1, 1.1), vertexColors: true, roughness: 0.94 })); mats.push(m); set.add(new THREE.Mesh(merge(gs), m)); }
"""

AGAVES = r"""    // agaves: (v285) a rosette of thick channelled leaves in a spiral, young ones upright in the middle, old ones arching out; toothed margins,
    // bud prints, a dusty bloom, a dark spine at each tip
    { const gs = []; seed = 77;
      const leafTex = canvasTex(128, 256, (g, W, H) => {
        // (u across the leaf, v up it: v = 0, the base, at the bottom of the picture; the blade fills u 0.08 to 0.92, its teeth stand out past that)
        const L = 0.08 * W, R = 0.92 * W, Y = v => H * (1 - v);
        g.clearRect(0, 0, W, H); g.save(); g.beginPath(); g.rect(L, 0, R - L, H);
        for (let v = 0.16; v < 0.88; v += 0.065) for (const [e, s] of [[L, -1], [R, 1]]) { const y = Y(v); g.moveTo(e, y + 5); g.lineTo(e + s * L * 0.95, y - 3); g.lineTo(e, y - 1); g.closePath(); }
        g.clip();
        const gr = g.createLinearGradient(0, H, 0, 0); gr.addColorStop(0, '#D7DEC4'); gr.addColorStop(0.12, '#A9C2B0'); gr.addColorStop(0.3, '#6C9890'); gr.addColorStop(0.65, '#557F7B'); gr.addColorStop(0.9, '#3F6662'); gr.addColorStop(1, '#3A2A1E');
        g.fillStyle = gr; g.fillRect(0, 0, W, H);
        // lighter margins and midrib, the leaf's channel darker either side of it
        const ac = g.createLinearGradient(0, 0, W, 0); ac.addColorStop(0, 'rgba(228,236,206,.75)'); ac.addColorStop(0.16, 'rgba(228,236,206,.0)'); ac.addColorStop(0.36, 'rgba(20,40,40,.16)'); ac.addColorStop(0.5, 'rgba(210,228,214,.22)'); ac.addColorStop(0.64, 'rgba(20,40,40,.16)'); ac.addColorStop(0.84, 'rgba(228,236,206,0)'); ac.addColorStop(1, 'rgba(228,236,206,.75)');
        g.fillStyle = ac; g.fillRect(0, 0, W, H);
        // bud prints: the faint outlines of the leaves it grew pressed against
        g.lineWidth = 2.2; for (const [v0, a] of [[0.34, 0.2], [0.52, 0.16], [0.7, 0.12]]) { g.strokeStyle = 'rgba(230,240,226,' + a + ')'; g.beginPath(); g.moveTo(L + 4, Y(v0 - 0.12)); g.quadraticCurveTo(W * 0.5, Y(v0 + 0.08), R - 4, Y(v0 - 0.12)); g.stroke();
          g.strokeStyle = 'rgba(25,45,45,' + (a * 0.8) + ')'; g.beginPath(); g.moveTo(L + 6, Y(v0 - 0.14)); g.quadraticCurveTo(W * 0.5, Y(v0 + 0.06), R - 6, Y(v0 - 0.14)); g.stroke(); }
        // the waxy bloom: a fine pale dust over it
        for (let i = 0; i < 260; i++) { g.fillStyle = 'rgba(235,242,236,' + rnd(0.04, 0.14).toFixed(2) + ')'; g.fillRect(rnd(0, W), rnd(0, H * 0.9), rnd(1, 2.5), rnd(1, 3)); }
        // the teeth, dark red-brown, and the spine at the tip
        g.fillStyle = '#5A2E1C'; g.fillRect(0, 0, L + 1.5, H); g.fillRect(R - 1.5, 0, W - R + 1.5, H);
        const sp = g.createLinearGradient(0, Y(0.86), 0, 0); sp.addColorStop(0, 'rgba(70,40,26,0)'); sp.addColorStop(0.45, 'rgba(70,40,26,.9)'); sp.addColorStop(1, '#2E1A10'); g.fillStyle = sp; g.fillRect(0, 0, W, Y(0.86));
        g.restore(); });
      leafTex.wrapS = leafTex.wrapT = THREE.ClampToEdgeWrapping;
      for (const [x, z, s] of AGAVES) { const nL = 22, a0 = rnd(0, 6.28), lean = rnd(0.85, 1.1);
        for (let li = 0; li < nL; li++) { const t = li / (nL - 1), a = a0 + li * 2.39996, old = 1 - t; // (inner leaves last: young, short, upright)
          const lift = 0.42 + 0.95 * t + rnd(-0.08, 0.08), droop = (0.55 + 0.5 * old) * lean, len = s * (0.55 + 0.6 * old) * rnd(0.9, 1.08), wid = s * (0.085 + 0.03 * old) / 0.84, y0 = 0.015 + 0.04 * t * s;
          const dx = Math.cos(a), dz = Math.sin(a), rows = 8, pos = [], uv = [], cen = [];
          let cx = x + dx * 0.02 * s, cy = y0, cz = z + dz * 0.02 * s, ang = lift;
          for (let r = 0; r <= rows; r++) { const u = r / rows; cen.push([cx, cy, cz, ang, u]); const st = len / rows; ang = lift - droop * u * u * 1.4; const hz = Math.cos(ang) * st, vy = Math.sin(ang) * st; cx += dx * hz; cz += dz * hz; cy = Math.max(0.012, cy + vy); }
          const sxv = -dz, szv = dx; // (across the leaf, level)
          const ring = cen.map(([px, py, pz, an, u]) => { const w = wid * (u < 0.32 ? 0.62 + 0.38 * u / 0.32 : Math.max(0, 1 - Math.pow((u - 0.32) / 0.68, 1.35))), nyx = -Math.sin(an), nyy = Math.cos(an), ch = w * 0.42; // (the edges raised, the middle down: a channel)
            return [[px + sxv * w + dx * nyx * ch * 0.4, py + nyy * ch * 0.4, pz + szv * w + dz * nyx * ch * 0.4, 0, u], [px - dx * nyx * ch * 0.25, py - nyy * ch * 0.25, pz - dz * nyx * ch * 0.25, 0.5, u], [px - sxv * w + dx * nyx * ch * 0.4, py + nyy * ch * 0.4, pz - szv * w + dz * nyx * ch * 0.4, 1, u]]; });
          for (let r = 0; r < rows; r++) for (let c = 0; c < 2; c++) { const A = ring[r][c], B = ring[r][c + 1], C2 = ring[r + 1][c], D = ring[r + 1][c + 1];
            for (const q of [A, B, D, A, D, C2]) { pos.push(q[0], q[1], q[2]); uv.push(q[3], q[4]); } }
          const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.Float32BufferAttribute(uv, 2)); smoothN(g);
          // deep in the rosette, darker; the youngest a little fresher
          const n = pos.length / 3, col = new Float32Array(n * 3);
          for (let i = 0; i < n; i++) { const v = uv[i * 2 + 1], k = (0.55 + 0.45 * Math.min(1, v * 1.6)) * (0.9 + 0.12 * t); col[i * 3] = k * (0.97 + 0.05 * t); col[i * 3 + 1] = k; col[i * 3 + 2] = k * (0.98 - 0.04 * t); }
          g.setAttribute('color', new THREE.BufferAttribute(col, 3)); gs.push(g); } }
      // (they sway in the wind, the tips most, more in a gust)
      const m = dofMap(new THREE.MeshStandardMaterial({ map: leafTex, alphaTest: 0.5, vertexColors: true, roughness: 0.6, side: THREE.DoubleSide }), { key: 'agave2', head: '', body: 'float k = position.y * position.y * 4.0, g = 0.6 + 0.9 * uWind.y; transformed.x += (sin(uWind.x * 1.9 + position.x * 1.7 + position.z * 1.3) * g + 0.35 * sin(uWind.x * 4.1 + position.x * 9.0 + position.z * 7.0)) * 0.03 * k; transformed.z += sin(uWind.x * 1.4 + position.z * 2.3 + 0.7) * 0.012 * k;' });
      mats.push(m); set.add(new THREE.Mesh(merge(gs), m)); }
"""


def apply(s):
    a = s.find("    // rocks: chunky faceted sandstone, banded light and dark\n"); b = s.find("    // agaves: stiff blue-green blades fanning out of the sand\n"); c = s.find("    // corrugated iron leaning on the big rock\n")
    assert 0 < a < b < c, (a, b, c)
    assert s.count("    // rocks: chunky faceted sandstone, banded light and dark\n") == 1
    s = s[:a] + HELPERS.lstrip('\n') + ROCKS + AGAVES + s[c:]
    return s
