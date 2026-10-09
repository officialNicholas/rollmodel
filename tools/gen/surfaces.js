// ---------- surfaces: each one is painted three times at once (color, height, gloss), so its relief and shine line up with
// what you see. Height becomes a normal map; gloss is the roughness three reads. Made the first time a theme needs them ----------
const gray = v => { const n = Math.round(Math.min(1, Math.max(0, v)) * 255); return 'rgb(' + n + ',' + n + ',' + n + ')'; };
const grayA = (v, a) => { const n = Math.round(Math.min(1, Math.max(0, v)) * 255); return 'rgba(' + n + ',' + n + ',' + n + ',' + a + ')'; };
const rgbS = (r, g, b, a) => a == null ? 'rgb(' + (r | 0) + ',' + (g | 0) + ',' + (b | 0) + ')' : 'rgba(' + (r | 0) + ',' + (g | 0) + ',' + (b | 0) + ',' + a + ')';
const texOf = (cv, srgb) => { const t = new THREE.CanvasTexture(cv); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = renderer.capabilities.getMaxAnisotropy(); if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
function heightNormal(cv, k) {
  const S = cv.width, d = cv.getContext('2d').getImageData(0, 0, S, S).data, hh = new Float32Array(S * S);
  for (let i = 0; i < S * S; i++) hh[i] = d[i * 4] / 255;
  const W = (x, y) => ((y + S) % S) * S + (x + S) % S, out = document.createElement('canvas'); out.width = out.height = S;
  const g = out.getContext('2d'), im = g.createImageData(S, S), o = im.data, kk = k * S / 1024;
  for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
    const gx = hh[W(x + 1, y - 1)] + 2 * hh[W(x + 1, y)] + hh[W(x + 1, y + 1)] - hh[W(x - 1, y - 1)] - 2 * hh[W(x - 1, y)] - hh[W(x - 1, y + 1)];
    const gy = hh[W(x - 1, y + 1)] + 2 * hh[W(x, y + 1)] + hh[W(x + 1, y + 1)] - hh[W(x - 1, y - 1)] - 2 * hh[W(x, y - 1)] - hh[W(x + 1, y - 1)];
    const nx = -gx * kk, ny = gy * kk, l = Math.hypot(nx, ny, 1), i = (y * S + x) * 4;
    o[i] = (nx / l * 0.5 + 0.5) * 255; o[i + 1] = (ny / l * 0.5 + 0.5) * 255; o[i + 2] = (1 / l * 0.5 + 0.5) * 255; o[i + 3] = 255;
  }
  g.putImageData(im, 0, 0); return texOf(out, false);
}
function makeSurf(S, paint, k) {
  const mk = n => { const c = document.createElement('canvas'); c.width = c.height = n; return c; };
  const C = mk(S), Hc = mk(HI ? S : 2), Rc = mk(HI ? S : 2);
  paint(C.getContext('2d'), Hc.getContext('2d'), Rc.getContext('2d'), S);
  return HI ? { map: texOf(C, true), normalMap: heightNormal(Hc, k || 2), roughnessMap: texOf(Rc, false) } : { map: texOf(C, true) };
}
// small painting helpers shared by the surfaces
const blob = (g, x, y, rad, col) => { const gr = g.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, col); gr.addColorStop(1, col.replace(/[\d.]+\)$/, '0)')); g.fillStyle = gr; g.fillRect(x - rad, y - rad, rad * 2, rad * 2); };
const walk = (R, x, y, a, len, n, wig) => { const pts = [[x, y]]; for (let t = 0; t < n; t++) { a += (R() - 0.5) * wig; x += Math.cos(a) * len / n; y += Math.sin(a) * len / n; pts.push([x, y]); } return pts; };
const pathOf = (g, pts) => { g.beginPath(); pts.forEach((p, n) => n ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); };
const bevelRect = (h, r, x0, y0, w, hh, B, lo, hi, rlo, rhi) => { for (let b = 0; b < B; b++) { const k = b / B, e = k * k * (3 - 2 * k); h.strokeStyle = gray(lo + (hi - lo) * e); h.lineWidth = 1; h.strokeRect(x0 + b + 0.5, y0 + b + 0.5, w - 2 * b - 1, hh - 2 * b - 1); if (r) { r.strokeStyle = gray(rlo + (rhi - rlo) * e); r.lineWidth = 1; r.strokeRect(x0 + b + 0.5, y0 + b + 0.5, w - 2 * b - 1, hh - 2 * b - 1); } } };
const clip3 = (gs, x, y, w, h) => { for (const g of gs) { g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); } };
const unclip3 = gs => { for (const g of gs) g.restore(); };
const SURF_PAINT = {
  // the Cathedral floor: polished checkered marble, cream and slate, veined and here and there cracked, each tile beveled down into dark grout
  marble: () => makeSurf(1024, (c, h, r, S) => {
    const R = rng(133), T = S / 2, G = 5, B = 13, px = S / 1024;
    c.fillStyle = '#2A2932'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.08); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.92); r.fillRect(0, 0, S, S);
    for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) {
      const dark = (i + j) % 2 === 1, x0 = i * T + G, y0 = j * T + G, w = T - 2 * G, base = dark ? [66, 74, 108] : [234, 227, 213], rb = dark ? 0.2 : 0.14;
      clip3([c, h, r], x0, y0, w, w);
      c.fillStyle = rgbS(...base); c.fillRect(x0, y0, w, w); h.fillStyle = gray(0.86); h.fillRect(x0, y0, w, w); r.fillStyle = gray(rb); r.fillRect(x0, y0, w, w);
      for (let k = 0; k < 34; k++) { const m = 0.82 + R() * 0.32; blob(c, x0 + R() * w, y0 + R() * w, w * (0.07 + R() * 0.3), rgbS(base[0] * m, base[1] * m, Math.min(255, base[2] * m * (dark ? 1.04 : 1)), 0.3)); }
      for (let k = 0; k < 16; k++) blob(r, x0 + R() * w, y0 + R() * w, w * (0.05 + R() * 0.22), grayA(rb + (R() - 0.35) * 0.18, 0.55));
      for (let k = 0; k < 10; k++) blob(h, x0 + R() * w, y0 + R() * w, w * (0.1 + R() * 0.3), grayA(0.86 + (R() - 0.5) * 0.04, 0.5));
      const vein = (pts, wid, col, al) => { c.lineCap = c.lineJoin = 'round';
        pathOf(c, pts); c.strokeStyle = rgbS(...col, al * 0.16); c.lineWidth = wid * 6; c.stroke(); pathOf(c, pts); c.strokeStyle = rgbS(...col, al); c.lineWidth = wid; c.stroke();
        pathOf(h, pts); h.strokeStyle = gray(0.83); h.lineWidth = wid * 1.4; h.stroke(); pathOf(r, pts); r.strokeStyle = gray(rb + 0.16); r.lineWidth = wid * 2; r.stroke(); };
      for (let k = 0; k < (dark ? 6 : 8); k++) {
        const col = dark ? (R() < 0.6 ? [146, 156, 198] : [214, 220, 242]) : (R() < 0.74 ? [118, 114, 128] : [192, 160, 102]);
        const pts = walk(R, x0 + R() * w, y0 + R() * w, R() * 6.28, w * (0.5 + R() * 0.8), 26, 0.7); vein(pts, (1 + R() * 2.2) * px, col, 0.32 + R() * 0.4);
        for (let b = 0; b < 2; b++) { const p = pts[(R() * pts.length) | 0]; vein(walk(R, p[0], p[1], R() * 6.28, w * (0.12 + R() * 0.3), 12, 0.9), (0.6 + R()) * px, col, 0.22 + R() * 0.3); }
      }
      for (let k = 0; k < (R() < 0.7 ? 2 : 1); k++) { const pts = walk(R, x0 + R() * w, y0 + R() * w, R() * 6.28, w * 0.3, 9, 1.6);
        pathOf(c, pts); c.strokeStyle = 'rgba(38,34,46,0.6)'; c.lineWidth = 1.3 * px; c.stroke(); pathOf(h, pts); h.strokeStyle = gray(0.48); h.lineWidth = 2.6 * px; h.stroke(); pathOf(r, pts); r.strokeStyle = gray(0.72); r.lineWidth = 2.6 * px; r.stroke(); }
      unclip3([c, h, r]);
      bevelRect(h, r, x0, y0, w, w, B, 0.22, 0.86, 0.42, rb);
      for (let b = 0; b < 4; b++) { c.strokeStyle = `rgba(0,0,0,${0.18 * (1 - b / 4)})`; c.lineWidth = 1; c.strokeRect(x0 + b + 0.5, y0 + b + 0.5, w - 2 * b - 1, w - 2 * b - 1); }
    }
  }, 2.6),
  // the Cathedral walls: pale dressed limestone, weathered toward the foot of each block, corners knocked, set in recessed mortar
  ashlar: () => makeSurf(512, (c, h, r, S) => {
    const rows = 4, bh = S / rows, bw = S / 2, G = 4, B = 7;
    c.fillStyle = '#7D766A'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.1); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.95); r.fillRect(0, 0, S, S);
    for (let j = 0; j < rows; j++) for (let i = -1; i < 3; i++) {
      const R = rng(500 + j * 17 + ((i % 2 + 2) % 2) * 5), x0 = i * bw + (j % 2) * bw / 2 + G, y0 = j * bh + G, w = bw - 2 * G, hh = bh - 2 * G, l = (R() - 0.5) * 24, base = [212 + l, 204 + l, 190 + l * 0.8];
      clip3([c, h, r], x0, y0, w, hh);
      c.fillStyle = rgbS(...base); c.fillRect(x0, y0, w, hh);
      const gd = c.createLinearGradient(0, y0, 0, y0 + hh); gd.addColorStop(0, 'rgba(255,250,240,0.12)'); gd.addColorStop(1, 'rgba(70,58,44,0.16)'); c.fillStyle = gd; c.fillRect(x0, y0, w, hh);
      for (let k = 0; k < 8; k++) blob(c, x0 + R() * w, y0 + R() * hh, 10 + R() * 40, rgbS(120 + R() * 40, 108 + R() * 36, 90 + R() * 30, 0.12));
      for (let k = 0; k < 260; k++) { c.fillStyle = R() < 0.5 ? 'rgba(90,80,64,0.22)' : 'rgba(255,250,236,0.25)'; c.fillRect(x0 + R() * w, y0 + R() * hh, 1 + R() * 1.5, 1 + R() * 1.5); }
      h.fillStyle = gray(0.8); h.fillRect(x0, y0, w, hh); for (let k = 0; k < 6; k++) blob(h, x0 + R() * w, y0 + R() * hh, 12 + R() * 30, grayA(0.8 + (R() - 0.5) * 0.08, 0.6));
      r.fillStyle = gray(0.8 + (R() - 0.5) * 0.08); r.fillRect(x0, y0, w, hh);
      unclip3([c, h, r]);
      for (let k = 0; k < 3; k++) { const cx = x0 + (R() < 0.5 ? 2 : w - 2), cy = y0 + (R() < 0.5 ? 2 : hh - 2), pts = lumpy(R, 5 + R() * 9, 4 + R() * 7, 7), rot = R() * 3; polyAt(c, pts, cx, cy, rot); c.fillStyle = rgbS(base[0] * 0.74, base[1] * 0.74, base[2] * 0.72); c.fill(); polyAt(h, pts, cx, cy, rot); h.fillStyle = gray(0.42); h.fill(); }
      bevelRect(h, null, x0, y0, w, hh, B, 0.18, 0.8);
    }
  }, 2.2),
  // the Crypt floor: domed cobbles, damp in places, moss in the dark joints
  cobble: () => makeSurf(1024, (c, h, r, S) => {
    const R = rng(131), N = 8, cs = S / N;
    c.fillStyle = '#1C1E24'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.06); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.95); r.fillRect(0, 0, S, S);
    for (let k = 0; k < 900; k++) { c.fillStyle = `rgba(${40 + R() * 30 | 0},${70 + R() * 50 | 0},${44 + R() * 20 | 0},${0.25 + R() * 0.3})`; c.fillRect(R() * S, R() * S, 1 + R() * 3, 1 + R() * 3); }
    for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
      const cx = (i + 0.5 + (R() - 0.5) * 0.3) * cs, cy = (j + 0.5 + (R() - 0.5) * 0.3) * cs, pts = lumpy(R, cs * (0.43 + R() * 0.05), cs * (0.41 + R() * 0.05), 14), rot = R() * 3, l = 92 + R() * 46, wet = R() < 0.25;
      wrapAt(S, cx, cy, cs, (X, Y) => {
        polyAt(c, pts, X, Y, rot); c.fillStyle = rgbS(l, l + 3, l + 12); c.fill();
        for (let k = 0; k < 4; k++) blob(c, X + (R() - 0.5) * cs * 0.6, Y + (R() - 0.5) * cs * 0.6, cs * (0.12 + R() * 0.2), rgbS(l * (0.8 + R() * 0.3), l * (0.8 + R() * 0.3), (l + 12) * (0.8 + R() * 0.3), 0.35));
        polyAt(c, pts.map(p => [p[0] * 0.6, p[1] * 0.6]), X - cs * 0.06, Y - cs * 0.07, rot); c.fillStyle = 'rgba(255,255,255,0.06)'; c.fill();
        for (let s = 0; s < 7; s++) { const k = 1 - s / 7; polyAt(h, pts.map(p => [p[0] * (0.35 + 0.65 * k), p[1] * (0.35 + 0.65 * k)]), X, Y, rot); h.fillStyle = gray(0.42 + 0.5 * (1 - k * k)); h.fill(); }
        polyAt(r, pts, X, Y, rot); r.fillStyle = gray(wet ? 0.34 : 0.7 + R() * 0.12); r.fill();
      });
    }
  }, 3.0),
  // the Crypt walls: sooty dark brick in deep mortar
  brick: () => makeSurf(512, (c, h, r, S) => {
    const rows = 8, bh = S / rows, bw = S / 4, G = 3, B = 4;
    c.fillStyle = '#15161B'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.1); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.95); r.fillRect(0, 0, S, S);
    for (let j = 0; j < rows; j++) for (let i = -1; i < 5; i++) {
      const R = rng(700 + j * 13 + ((i % 4 + 4) % 4) * 3), x0 = i * bw + (j % 2) * bw / 2 + G, y0 = j * bh + G, w = bw - 2 * G, hh = bh - 2 * G, l = 66 + R() * 36;
      clip3([c, h, r], x0, y0, w, hh);
      c.fillStyle = rgbS(l, l + 2, l + 10); c.fillRect(x0, y0, w, hh);
      for (let k = 0; k < 3; k++) blob(c, x0 + R() * w, y0 + R() * hh, 8 + R() * 22, rgbS(l * 0.6, l * 0.6, l * 0.68, 0.35));
      for (let k = 0; k < 80; k++) { c.fillStyle = R() < 0.6 ? 'rgba(0,0,0,0.25)' : 'rgba(255,255,255,0.08)'; c.fillRect(x0 + R() * w, y0 + R() * hh, 1 + R() * 2, 1); }
      h.fillStyle = gray(0.78); h.fillRect(x0, y0, w, hh); r.fillStyle = gray(0.82 + (R() - 0.5) * 0.1); r.fillRect(x0, y0, w, hh);
      unclip3([c, h, r]); bevelRect(h, null, x0, y0, w, hh, B, 0.2, 0.78);
    }
  }, 2.4),
  // the Manor floor: varnished oak planks, grain running along each, the seams beveled and dark
  parquet: () => makeSurf(1024, (c, h, r, S) => {
    const R = rng(135), cols = 8, w = S / cols, B = 4;
    c.fillStyle = '#2C190E'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.12); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.8); r.fillRect(0, 0, S, S);
    for (let i = 0; i < cols; i++) { let y = -R() * S * 0.5; while (y < S) { const L = S * (0.26 + R() * 0.36), l = R(), base = [118 + l * 44, 70 + l * 28, 36 + l * 16];
      for (const off of [-S, 0, S]) { const x0 = i * w + 2, y0 = y + off + 2, ww = w - 4, hh = L - 4; if (y0 > S || y0 + hh < 0) continue;
        clip3([c, h, r], x0, y0, ww, hh);
        c.fillStyle = rgbS(...base); c.fillRect(x0, y0, ww, hh);
        for (let k = 0; k < 16; k++) { const gx = x0 + R() * ww, wv = (R() - 0.5) * 6; c.strokeStyle = `rgba(${R() < 0.5 ? '60,32,14' : '170,110,64'},${0.12 + R() * 0.2})`; c.lineWidth = 0.6 + R() * 1.6; c.beginPath(); c.moveTo(gx, y0); c.bezierCurveTo(gx + wv, y0 + hh * 0.3, gx - wv, y0 + hh * 0.7, gx + wv * 0.4, y0 + hh); c.stroke(); }
        if (R() < 0.3) { const kx = x0 + ww * (0.3 + R() * 0.4), ky = y0 + R() * hh; for (let q = 4; q > 0; q--) { c.strokeStyle = `rgba(70,38,18,${0.18})`; c.lineWidth = 1; c.beginPath(); c.ellipse(kx, ky, q * 2.4, q * 4.2, 0, 0, 6.2832); c.stroke(); } }
        h.fillStyle = gray(0.8); h.fillRect(x0, y0, ww, hh); r.fillStyle = gray(0.26 + (R() - 0.5) * 0.08); r.fillRect(x0, y0, ww, hh);
        for (let k = 0; k < 3; k++) blob(r, x0 + R() * ww, y0 + R() * hh, 20 + R() * 50, grayA(0.2 + R() * 0.25, 0.4));
        unclip3([c, h, r]); bevelRect(h, r, x0, y0, ww, hh, B, 0.2, 0.8, 0.5, 0.26); }
      y += L; } }
  }, 2.0),
  // the Manor walls: dark damask, the pattern a hair proud of the paper
  damask: () => makeSurf(512, (c, h, r, S) => {
    const R = rng(136), P = S / 4;
    c.fillStyle = '#3A1B34'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.5); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.7); r.fillRect(0, 0, S, S);
    for (const g of [c, h, r]) { g.lineWidth = 3; g.strokeStyle = g === c ? '#5E2E54' : g === h ? gray(0.62) : gray(0.45); for (let k = -4; k <= 8; k++) { g.beginPath(); g.moveTo(k * P, 0); g.lineTo(k * P + S, S); g.stroke(); g.beginPath(); g.moveTo(k * P, S); g.lineTo(k * P + S, 0); g.stroke(); } }
    for (let i = 0; i <= 4; i++) for (let j = 0; j <= 4; j++) for (const [x, y, rad, col, hv] of [[i * P, j * P, 4, '#8A5A3A', 0.66], [i * P + P / 2, j * P + P / 2, 9, 'rgba(200,150,90,0.4)', 0.6]]) {
      c.fillStyle = col; c.beginPath(); c.arc(x, y, rad, 0, 6.2832); c.fill(); h.fillStyle = gray(hv); h.beginPath(); h.arc(x, y, rad, 0, 6.2832); h.fill(); r.fillStyle = gray(0.4); r.beginPath(); r.arc(x, y, rad, 0, 6.2832); r.fill(); }
    for (let k = 0; k < 400; k++) { c.fillStyle = 'rgba(0,0,0,0.12)'; c.fillRect(R() * S, R() * S, 1 + R() * 2, 1 + R() * 2); }
  }, 1.6),
  // the Night Garden lawn: leafy groundcover, every leaf a little raised and a little glossy, clover and the odd flower
  moss: () => makeSurf(1024, (c, h, r, S) => {
    const R = rng(137), px = S / 512;
    c.fillStyle = '#2C4E2E'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.3); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.8); r.fillRect(0, 0, S, S);
    for (let i = 0; i < 90; i++) { const pts = lumpy(R, (30 + R() * 70) * px, (24 + R() * 60) * px, 10), x = R() * S, y = R() * S, rot = R() * 3, col = R() < 0.5 ? 'rgba(74,116,62,0.38)' : 'rgba(22,44,26,0.42)'; wrapAt(S, x, y, 120 * px, (X, Y) => { polyAt(c, pts, X, Y, rot); c.fillStyle = col; c.fill(); }); }
    for (let i = 0; i < 6400; i++) { const x = R() * S, y = R() * S, L = (5 + R() * 7) * px, W = L * (0.38 + R() * 0.2), a = R() * 6.283, l = R(), col = rgbS(44 + l * 66, 94 + l * 90, 38 + l * 42);
      wrapAt(S, x, y, 16 * px, (X, Y) => { leafAt(c, X, Y, L, W, a, col, 'rgba(16,34,16,0.4)'); leafAt(h, X, Y, L, W, a, gray(0.45 + 0.4 * l), null); leafAt(r, X, Y, L, W, a, gray(0.55 - 0.15 * l), null); }); }
    for (let i = 0; i < 220; i++) { const x = R() * S, y = R() * S, a = R() * 6.283; wrapAt(S, x, y, 14 * px, (X, Y) => { for (let k = 0; k < 3; k++) { const b = a + k * 2.094, ox = X + Math.cos(b) * 3.2 * px, oy = Y + Math.sin(b) * 3.2 * px; c.fillStyle = 'rgba(98,164,80,0.92)'; c.beginPath(); c.arc(ox, oy, 3.4 * px, 0, 6.2832); c.fill(); h.fillStyle = gray(0.9); h.beginPath(); h.arc(ox, oy, 3.4 * px, 0, 6.2832); h.fill(); r.fillStyle = gray(0.4); r.beginPath(); r.arc(ox, oy, 3.4 * px, 0, 6.2832); r.fill(); } }); }
    for (let i = 0; i < 150; i++) { const x = R() * S, y = R() * S; wrapAt(S, x, y, 5 * px, (X, Y) => { c.fillStyle = R() < 0.5 ? 'rgba(250,246,230,0.92)' : 'rgba(255,222,120,0.88)'; c.beginPath(); c.arc(X, Y, 1.6 * px, 0, 6.2832); c.fill(); h.fillStyle = gray(1); h.beginPath(); h.arc(X, Y, 1.6 * px, 0, 6.2832); h.fill(); }); }
  }, 2.4),
  // clipped hedge: dense leaves with dark gaps between them, so the sides read deep
  hedge: () => makeSurf(512, (c, h, r, S) => {
    const R = rng(138);
    c.fillStyle = '#10261A'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.12); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.9); r.fillRect(0, 0, S, S);
    for (let i = 0; i < 5200; i++) { const x = R() * S, y = R() * S, L = 4 + R() * 6, W = L * (0.48 + R() * 0.2), a = R() * 6.283, l = R(), col = rgbS(28 + l * 62, 74 + l * 104, 30 + l * 40);
      wrapAt(S, x, y, 12, (X, Y) => { leafAt(c, X, Y, L, W, a, col, l > 0.55 ? 'rgba(10,30,14,0.35)' : null); leafAt(h, X, Y, L, W, a, gray(0.3 + 0.62 * l), null); leafAt(r, X, Y, L, W, a, gray(0.62 - 0.22 * l), null); }); }
  }, 2.6),
  // Palette Island sand: wind ripples you can feel, a few shells
  sand: () => makeSurf(512, (c, h, r, S) => {
    const R = rng(141);
    c.fillStyle = '#E9D2A2'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.5); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.96); r.fillRect(0, 0, S, S);
    for (let i = 0; i < 34; i++) { const y0 = R() * S, a = 3 + R() * 5, k = 1 + (R() * 2 | 0), ph = R() * 6.28, w = 3 + R() * 4;
      for (const [g, col, dy] of [[c, rgbS(178 + R() * 18, 138 + R() * 18, 90 + R() * 12, 0.2 + R() * 0.12), 0], [c, 'rgba(255,247,226,0.24)', -3], [h, grayA(0.32, 0.8), 2], [h, grayA(0.72, 0.8), -2.5]]) {
        g.strokeStyle = col; g.lineWidth = w; for (const off of [-S, 0, S]) { g.beginPath(); for (let x = 0; x <= S; x += 4) { const y = y0 + off + dy + Math.sin(x / S * 6.2832 * k + ph) * a; x ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke(); } } }
    for (let i = 0; i < 2600; i++) { const v = R(); c.fillStyle = v < 0.5 ? `rgba(150,112,70,${0.14 + v * 0.3})` : `rgba(255,250,236,${0.2 + v * 0.3})`; c.fillRect(R() * S, R() * S, 1 + R() * 2, 1 + R() * 2); }
    for (let i = 0; i < 34; i++) { const x = R() * S, y = R() * S, col = ['rgba(255,232,224,0.92)', 'rgba(250,246,236,0.92)', 'rgba(205,192,180,0.88)'][i % 3], rx = 2 + R() * 2.4, ry = 1.2 + R() * 1.4, rot = R() * 3;
      wrapAt(S, x, y, 7, (X, Y) => { c.fillStyle = col; c.beginPath(); c.ellipse(X, Y, rx, ry, rot, 0, 6.2832); c.fill(); h.fillStyle = gray(0.9); h.beginPath(); h.ellipse(X, Y, rx, ry, rot, 0, 6.2832); h.fill(); r.fillStyle = gray(0.4); r.beginPath(); r.ellipse(X, Y, rx, ry, rot, 0, 6.2832); r.fill(); }); }
  }, 1.6),
  // boardwalk planks, bleached by the sun, grain and nail heads, dark gaps
  plank: () => makeSurf(512, (c, h, r, S) => {
    const R = rng(142), rows = 6, ph = S / rows, B = 4;
    c.fillStyle = '#4A3624'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.12); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.9); r.fillRect(0, 0, S, S);
    for (let j = 0; j < rows; j++) { let x = -R() * S * 0.4; while (x < S) { const L = S * (0.34 + R() * 0.5), l = R(), base = [176 + l * 42, 148 + l * 36, 110 + l * 30];
      for (const off of [-S, 0, S]) { const x0 = x + off + 2, y0 = j * ph + 2, ww = L - 4, hh = ph - 4; if (x0 > S || x0 + ww < 0) continue;
        clip3([c, h, r], x0, y0, ww, hh);
        c.fillStyle = rgbS(...base); c.fillRect(x0, y0, ww, hh);
        for (let k = 0; k < 9; k++) { const gy = y0 + R() * hh, wv = (R() - 0.5) * 4; c.strokeStyle = `rgba(${R() < 0.6 ? '110,84,56' : '235,215,180'},${0.18 + R() * 0.2})`; c.lineWidth = 0.7 + R() * 1.4; c.beginPath(); c.moveTo(x0, gy); c.bezierCurveTo(x0 + ww * 0.3, gy + wv, x0 + ww * 0.7, gy - wv, x0 + ww, gy + wv * 0.3); c.stroke(); }
        h.fillStyle = gray(0.78); h.fillRect(x0, y0, ww, hh); r.fillStyle = gray(0.8 + (R() - 0.5) * 0.1); r.fillRect(x0, y0, ww, hh);
        unclip3([c, h, r]); bevelRect(h, null, x0, y0, ww, hh, B, 0.2, 0.78);
        for (const nx of [x0 + 7, x0 + ww - 7]) { c.fillStyle = 'rgba(64,50,36,0.75)'; c.beginPath(); c.arc(nx, y0 + hh / 2, 2, 0, 6.2832); c.fill(); h.fillStyle = gray(0.9); h.beginPath(); h.arc(nx, y0 + hh / 2, 2, 0, 6.2832); h.fill(); r.fillStyle = gray(0.35); r.beginPath(); r.arc(nx, y0 + hh / 2, 2, 0, 6.2832); r.fill(); } }
      x += L; } }
  }, 2.0),
  // the Blank Canvas: smooth white plaster in big panels, the seams just pressed in, a faint drafting grid
  blank: () => makeSurf(512, (c, h, r, S) => {
    const R = rng(143);
    c.fillStyle = '#F4F4F1'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.7); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.5); r.fillRect(0, 0, S, S);
    for (let k = 0; k < 18; k++) blob(c, R() * S, R() * S, 30 + R() * 90, `rgba(${226 + R() * 20 | 0},${226 + R() * 20 | 0},${230 + R() * 20 | 0},0.25)`);
    for (let k = 0; k < 1600; k++) { const v = R(); c.fillStyle = `rgba(150,150,160,${0.03 + v * 0.05})`; c.fillRect(R() * S, R() * S, 1 + R() * 2, 1 + R() * 2); }
    for (let k = 0; k < 10; k++) blob(r, R() * S, R() * S, 20 + R() * 60, grayA(0.38 + R() * 0.25, 0.4));
    c.strokeStyle = 'rgba(120,124,140,0.06)'; c.lineWidth = 1; for (let k = 0; k < 16; k++) { const v = (k + 0.5) * S / 16; c.beginPath(); c.moveTo(v, 0); c.lineTo(v, S); c.stroke(); c.beginPath(); c.moveTo(0, v); c.lineTo(S, v); c.stroke(); }
    for (let k = 0; k <= 2; k++) { const v = k * S / 2; for (const [g, col, wd] of [[c, 'rgba(120,124,140,0.18)', 2], [h, gray(0.25), 4], [r, gray(0.75), 4]]) { g.strokeStyle = col; g.lineWidth = wd; g.beginPath(); g.moveTo(v, 0); g.lineTo(v, S); g.stroke(); g.beginPath(); g.moveTo(0, v); g.lineTo(S, v); g.stroke(); } }
  }, 1.4),
  blankSide: () => makeSurf(512, (c, h, r, S) => {
    const R = rng(144);
    c.fillStyle = '#F1F1EE'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.7); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.55); r.fillRect(0, 0, S, S);
    for (let k = 0; k < 1200; k++) { const v = R(); c.fillStyle = `rgba(150,150,160,${0.03 + v * 0.05})`; c.fillRect(R() * S, R() * S, 1 + R() * 2, 1 + R() * 2); }
    for (let k = 0; k < 4; k++) { const y = k * S / 4; for (const [g, col, wd] of [[c, 'rgba(120,124,140,0.14)', 2], [h, gray(0.3), 3], [r, gray(0.75), 3]]) { g.fillStyle = col; g.fillRect(0, y, S, wd); } c.fillStyle = 'rgba(255,255,255,0.5)'; c.fillRect(0, y + 2, S, 2); }
  }, 1.4)
};
const SURF = {};
const surf = id => SURF[id] || (SURF[id] = SURF_PAINT[id]());
