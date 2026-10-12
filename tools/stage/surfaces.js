// ---------- the Sludge Sewer's and the Fishing Raft's surfaces ----------
{ const rivet = (c, h, r, x, y, rad, col) => { c.fillStyle = 'rgba(0,0,0,0.35)'; c.beginPath(); c.arc(x + 1, y + 1.4, rad + 0.8, 0, 6.2832); c.fill(); c.fillStyle = col; c.beginPath(); c.arc(x, y, rad, 0, 6.2832); c.fill(); c.fillStyle = 'rgba(255,255,255,0.28)'; c.beginPath(); c.arc(x - rad * 0.3, y - rad * 0.35, rad * 0.45, 0, 6.2832); c.fill();
    const gr = h.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, gray(1)); gr.addColorStop(1, gray(0.82)); h.fillStyle = gr; h.beginPath(); h.arc(x, y, rad, 0, 6.2832); h.fill(); r.fillStyle = gray(0.38); r.beginPath(); r.arc(x, y, rad, 0, 6.2832); r.fill(); };
  // slime: a lumpy glossy puddle, bright at its heart, a darker rim, a few splashes round it, raised a hair
  const slime = (c, h, r, R, x, y, rad) => { const pts = lumpy(R, rad, rad * (0.6 + R() * 0.4), 14), rot = R() * 6.28;
    polyAt(c, pts.map(p => [p[0] * 1.12, p[1] * 1.12]), x, y, rot); c.fillStyle = 'rgba(40,90,20,0.55)'; c.fill();
    polyAt(c, pts, x, y, rot); const gr = c.createRadialGradient(x, y, 0, x, y, rad); gr.addColorStop(0, 'rgba(196,255,96,0.98)'); gr.addColorStop(0.6, 'rgba(120,226,52,0.96)'); gr.addColorStop(1, 'rgba(70,160,30,0.95)'); c.fillStyle = gr; c.fill();
    polyAt(c, pts.map(p => [p[0] * 0.45, p[1] * 0.4]), x - rad * 0.2, y - rad * 0.22, rot); c.fillStyle = 'rgba(240,255,200,0.35)'; c.fill();
    polyAt(h, pts, x, y, rot); h.fillStyle = gray(0.9); h.fill(); polyAt(r, pts, x, y, rot); r.fillStyle = gray(0.06); r.fill();
    for (let k = 0; k < 6; k++) { const a = R() * 6.28, d = rad * (1.15 + R() * 0.6), s = 2 + R() * rad * 0.12; c.fillStyle = 'rgba(140,236,60,0.9)'; c.beginPath(); c.arc(x + Math.cos(a) * d, y + Math.sin(a) * d, s, 0, 6.2832); c.fill(); r.fillStyle = gray(0.1); r.beginPath(); r.arc(x + Math.cos(a) * d, y + Math.sin(a) * d, s, 0, 6.2832); r.fill(); } };
  const rust = (c, r, R, x, y, rad) => { for (let k = 0; k < 7; k++) { const a = R() * 6.28, d = R() * rad * 0.7; blob(c, x + Math.cos(a) * d, y + Math.sin(a) * d, rad * (0.3 + R() * 0.5), `rgba(${92 + R() * 34 | 0},${60 + R() * 22 | 0},${34 + R() * 14 | 0},${0.26 + R() * 0.22})`); blob(r, x + Math.cos(a) * d, y + Math.sin(a) * d, rad * 0.5, grayA(0.85, 0.6)); } };
  const scratches = (c, r, R, x0, y0, w, hh, n) => { for (let k = 0; k < n; k++) { const sx = x0 + R() * w, sy = y0 + R() * hh, a = R() * 6.28, L = 8 + R() * 54; c.strokeStyle = `rgba(${160 + R() * 60 | 0},${168 + R() * 60 | 0},${160 + R() * 50 | 0},${0.1 + R() * 0.2})`; c.lineWidth = 0.5 + R() * 1.1; c.beginPath(); c.moveTo(sx, sy); c.lineTo(sx + Math.cos(a) * L, sy + Math.sin(a) * L); c.stroke(); r.strokeStyle = grayA(0.25, 0.5); r.lineWidth = 1; r.beginPath(); r.moveTo(sx, sy); r.lineTo(sx + Math.cos(a) * L, sy + Math.sin(a) * L); r.stroke(); } };
  Object.assign(SURF_PAINT, {
    // the sewer's floor: big steel plates, riveted round their edges and beveled into dark wet seams, scuffed and scratched, grime and rust
    // blooming on them, one in four a raised diamond tread; puddles of glowing slime here and there, glossy
    steelPlate: () => makeSurf(1024, (c, h, r, S) => {
      const R = rng(611), T = S / 2, G = 5, B = 10;
      c.fillStyle = '#121513'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.04); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.25); r.fillRect(0, 0, S, S);
      for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) {
        const x0 = i * T + G, y0 = j * T + G, w = T - 2 * G, tread = i === 1 && j === 0, l = R(), base = [84 + l * 18, 94 + l * 16, 90 + l * 14];
        clip3([c, h, r], x0, y0, w, w);
        c.fillStyle = rgbS(...base); c.fillRect(x0, y0, w, w); h.fillStyle = gray(0.78); h.fillRect(x0, y0, w, w); r.fillStyle = gray(0.5); r.fillRect(x0, y0, w, w);
        for (let k = 0; k < 46; k++) { const m = 0.74 + R() * 0.34; blob(c, x0 + R() * w, y0 + R() * w, w * (0.04 + R() * 0.22), rgbS(base[0] * m, base[1] * m * (0.98 + R() * 0.06), base[2] * m, 0.32)); }
        for (let k = 0; k < 18; k++) blob(r, x0 + R() * w, y0 + R() * w, w * (0.05 + R() * 0.2), grayA(0.36 + (R() - 0.5) * 0.3, 0.5));
        if (tread) { // a diamond tread plate: little raised bars, alternately leaning
          for (let yy = y0 + 10; yy < y0 + w; yy += 22) for (let xx = x0 + 10 + ((yy - y0) / 22 % 2) * 11; xx < x0 + w; xx += 22) { const a = ((xx + yy) / 11 | 0) % 2 ? 0.7 : -0.7; for (const [g, col] of [[c, 'rgba(150,158,150,0.55)'], [h, gray(1)], [r, gray(0.3)]]) { g.save(); g.translate(xx, yy); g.rotate(a); g.fillStyle = col; g.fillRect(-7, -1.8, 14, 3.6); g.restore(); } } }
        scratches(c, r, R, x0, y0, w, w, 70);
        if (R() < 0.5) rust(c, r, R, x0 + 30 + R() * (w - 60), y0 + 30 + R() * (w - 60), 16 + R() * 20);
        // grime gathered toward the seams
        for (let k = 0; k < 24; k++) { const e = (R() * 4) | 0, t = R() * w, px = e === 0 ? x0 + 6 : e === 1 ? x0 + w - 6 : x0 + t, py = e === 2 ? y0 + 6 : e === 3 ? y0 + w - 6 : y0 + t; blob(c, px, py, 14 + R() * 30, 'rgba(20,26,18,0.35)'); }
        unclip3([c, h, r]);
        bevelRect(h, r, x0, y0, w, w, B, 0.1, 0.78, 0.2, 0.5);
        const nR = 9; for (let k = 0; k < nR; k++) { const t = (k + 0.5) / nR * (w - 28) + 14; for (const [px, py] of [[x0 + 15, y0 + t], [x0 + w - 15, y0 + t], [x0 + t, y0 + 15], [x0 + t, y0 + w - 15]]) rivet(c, h, r, px, py, 4.2, 'rgb(104,112,104)'); }
      }
      // wet seams: a dark gleam
      for (let k = 0; k <= 2; k++) { const v = k * S / 2; r.fillStyle = gray(0.12); r.fillRect(v - 5, 0, 10, S); r.fillRect(0, v - 5, S, 10); }
      // a dark wet stain or two (the glowing puddles are set down over the floor on their own, so they never line up)
      for (let k = 0; k < 2; k++) { const x = 100 + R() * (S - 200), y = 100 + R() * (S - 200); polyAt(c, lumpy(R, 60, 40, 14), x, y, R() * 6.28); c.fillStyle = 'rgba(16,22,14,0.35)'; c.fill(); polyAt(r, lumpy(R, 60, 40, 14), x, y, R() * 6.28); r.fillStyle = gray(0.12); r.fill(); }
    }, 2.3),
    // the sewer's walls: dark steel panels standing up, riveted down their seams, a horizontal brace across, rust running down from the rivets
    steelWall: () => makeSurf(512, (c, h, r, S) => {
      const R = rng(612), P = S / 2;
      c.fillStyle = '#101211'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.05); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.3); r.fillRect(0, 0, S, S);
      for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) { const x0 = i * P + 3, y0 = j * P + 3, w = P - 6, l = R(), base = [56 + l * 16, 64 + l * 16, 60 + l * 12];
        clip3([c, h, r], x0, y0, w, w); c.fillStyle = rgbS(...base); c.fillRect(x0, y0, w, w); h.fillStyle = gray(0.75); h.fillRect(x0, y0, w, w); r.fillStyle = gray(0.48); r.fillRect(x0, y0, w, w);
        for (let k = 0; k < 22; k++) { const m = 0.78 + R() * 0.3; blob(c, x0 + R() * w, y0 + R() * w, w * (0.06 + R() * 0.25), rgbS(base[0] * m, base[1] * m, base[2] * m, 0.3)); }
        scratches(c, r, R, x0, y0, w, w, 26);
        unclip3([c, h, r]); bevelRect(h, r, x0, y0, w, w, 6, 0.1, 0.75, 0.25, 0.48);
        for (let k = 0; k < 6; k++) { const t = (k + 0.5) / 6 * (w - 20) + 10; for (const [px, py] of [[x0 + 10, y0 + t], [x0 + w - 10, y0 + t]]) { rivet(c, h, r, px, py, 3.4, 'rgb(84,92,86)'); if (R() < 0.35) { const L = 20 + R() * 60; const gr = c.createLinearGradient(px, py, px, py + L); gr.addColorStop(0, 'rgba(140,70,30,0.55)'); gr.addColorStop(1, 'rgba(140,70,30,0)'); c.fillStyle = gr; c.fillRect(px - 2.5, py, 5, L); } } } }
      // the brace: a raised flat bar across the middle of each panel row, with bolts
      for (const yy of [S * 0.25, S * 0.75]) { c.fillStyle = 'rgba(40,46,42,0.9)'; c.fillRect(0, yy - 9, S, 18); c.fillStyle = 'rgba(110,118,110,0.35)'; c.fillRect(0, yy - 9, S, 3); h.fillStyle = gray(0.92); h.fillRect(0, yy - 9, S, 18); r.fillStyle = gray(0.4); r.fillRect(0, yy - 9, S, 18); for (let x = 16; x < S; x += 32) rivet(c, h, r, x, yy, 3, 'rgb(90,98,92)'); }
    }, 2.0),
    // hazard paint: yellow and black bands at forty-five degrees, chipped and scuffed, the yellow a little glossy
    hazard: () => makeSurf(256, (c, h, r, S) => {
      const R = rng(613), n = 4, p = S / n;
      c.fillStyle = '#1C1C1A'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.55); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.62); r.fillRect(0, 0, S, S);
      for (let k = -n; k < 2 * n; k++) { const x = k * p; for (const [g, col] of [[c, '#EDB21E'], [h, gray(0.62)], [r, gray(0.4)]]) { g.fillStyle = col; g.beginPath(); g.moveTo(x, 0); g.lineTo(x + p / 2, 0); g.lineTo(x + p / 2 - S, S); g.lineTo(x - S, S); g.closePath(); g.fill(); } }
      for (let k = 0; k < 90; k++) { const x = R() * S, y = R() * S, s = 1 + R() * 4; c.fillStyle = R() < 0.6 ? 'rgba(60,62,58,0.85)' : 'rgba(150,150,140,0.6)'; c.beginPath(); c.ellipse(x, y, s * (1 + R()), s, R() * 3, 0, 6.2832); c.fill(); h.fillStyle = gray(0.52); h.beginPath(); h.arc(x, y, s, 0, 6.2832); h.fill(); }
      scratches(c, r, R, 0, 0, S, S, 40);
      for (let k = 0; k < 10; k++) blob(c, R() * S, R() * S, 10 + R() * 30, 'rgba(30,24,16,0.18)');
    }, 1.6),
    // concrete: grey with a green cast, pitted, with form lines and stains running down
    concrete: () => makeSurf(512, (c, h, r, S) => {
      const R = rng(614);
      c.fillStyle = '#7C847A'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.6); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.92); r.fillRect(0, 0, S, S);
      for (let k = 0; k < 60; k++) blob(c, R() * S, R() * S, 20 + R() * 90, `rgba(${100 + R() * 40 | 0},${110 + R() * 40 | 0},${100 + R() * 34 | 0},0.25)`);
      for (let k = 0; k < 700; k++) { const x = R() * S, y = R() * S, s = 0.6 + R() * 2.2; c.fillStyle = `rgba(40,46,40,${0.2 + R() * 0.4})`; c.beginPath(); c.arc(x, y, s, 0, 6.2832); c.fill(); h.fillStyle = gray(0.35); h.beginPath(); h.arc(x, y, s, 0, 6.2832); h.fill(); }
      for (const yy of [S * 0.33, S * 0.66, S]) { c.fillStyle = 'rgba(50,56,50,0.25)'; c.fillRect(0, yy - 2, S, 3); h.fillStyle = gray(0.45); h.fillRect(0, yy - 2, S, 3); }
      for (let k = 0; k < 14; k++) { const x = R() * S, L = 40 + R() * 200, gr = c.createLinearGradient(x, 0, x, L); gr.addColorStop(0, R() < 0.5 ? 'rgba(80,140,40,0.35)' : 'rgba(40,40,30,0.3)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = gr; c.fillRect(x - 3 - R() * 6, 0, 6 + R() * 12, L); }
    }, 1.8),
    // the raft's deck: weathered planks lengthwise, butt joints staggered, nailed in pairs on the joists, grain, knots, salt stains,
    // the odd sun-bleached grey board and a fleck or two of old boat paint
    deck: () => makeSurf(1024, (c, h, r, S) => {
      const R = rng(621), rows = 13, ph = S / rows, B = 4, J = S / 4;
      c.fillStyle = '#2A1E14'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.08); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.92); r.fillRect(0, 0, S, S);
      for (let j = 0; j < rows; j++) { let x = -J * ((R() * 4) | 0); while (x < S) { const L = J * (1 + ((R() * 3) | 0)), l = R(), grey = R() < 0.18, base = grey ? [168 + l * 30, 160 + l * 26, 146 + l * 22] : [184 + l * 40, 138 + l * 34, 92 + l * 26];
        for (const off of [-S, 0, S]) { const x0 = x + off + 2, y0 = j * ph + 2.5, ww = L - 4, hh = ph - 5; if (x0 > S || x0 + ww < 0) continue;
          clip3([c, h, r], x0, y0, ww, hh);
          c.fillStyle = rgbS(...base); c.fillRect(x0, y0, ww, hh);
          for (let k = 0; k < 14; k++) { const gy = y0 + R() * hh, wv = (R() - 0.5) * 5; c.strokeStyle = `rgba(${R() < 0.6 ? '96,66,40' : '238,214,176'},${0.14 + R() * 0.2})`; c.lineWidth = 0.6 + R() * 1.6; c.beginPath(); c.moveTo(x0, gy); c.bezierCurveTo(x0 + ww * 0.3, gy + wv, x0 + ww * 0.7, gy - wv, x0 + ww, gy + wv * 0.3); c.stroke(); }
          if (R() < 0.5) { const kx = x0 + 20 + R() * (ww - 40), ky = y0 + hh * (0.3 + R() * 0.4); c.fillStyle = 'rgba(92,58,32,0.7)'; c.beginPath(); c.ellipse(kx, ky, 5 + R() * 4, 3 + R() * 2, 0, 0, 6.2832); c.fill(); c.strokeStyle = 'rgba(92,58,32,0.35)'; c.lineWidth = 1; c.beginPath(); c.ellipse(kx, ky, 11, 6, 0, 0, 6.2832); c.stroke(); }
          for (let k = 0; k < 3; k++) blob(c, x0 + R() * ww, y0 + R() * hh, 12 + R() * 34, R() < 0.5 ? 'rgba(70,50,30,0.16)' : 'rgba(255,246,226,0.14)');
          if (R() < 0.08) { c.fillStyle = ['rgba(60,170,170,0.5)', 'rgba(200,60,50,0.45)', 'rgba(240,240,230,0.45)'][(R() * 3) | 0]; c.fillRect(x0 + R() * ww * 0.7, y0 + 2, 20 + R() * 60, hh - 4); }
          h.fillStyle = gray(0.8); h.fillRect(x0, y0, ww, hh); r.fillStyle = gray(0.78 + (R() - 0.5) * 0.12); r.fillRect(x0, y0, ww, hh);
          unclip3([c, h, r]); bevelRect(h, null, x0, y0, ww, hh, B, 0.22, 0.8);
          for (let q = 0; q <= Math.round(ww / J); q++) { const nx = Math.min(x0 + ww - 7, Math.max(x0 + 7, x0 + q * J)); for (const ny of [y0 + hh * 0.3, y0 + hh * 0.7]) { c.fillStyle = 'rgba(58,44,34,0.8)'; c.beginPath(); c.arc(nx, ny, 2.2, 0, 6.2832); c.fill(); c.fillStyle = 'rgba(130,100,70,0.35)'; c.beginPath(); c.arc(nx - 0.6, ny - 0.6, 1, 0, 6.2832); c.fill(); h.fillStyle = gray(0.92); h.beginPath(); h.arc(nx, ny, 2.2, 0, 6.2832); h.fill(); r.fillStyle = gray(0.4); r.beginPath(); r.arc(nx, ny, 2.2, 0, 6.2832); r.fill(); } } }
        x += L; } }
      // salt and water stains over the lot
      for (let k = 0; k < 16; k++) blob(c, R() * S, R() * S, 30 + R() * 90, R() < 0.5 ? 'rgba(60,46,32,0.1)' : 'rgba(255,255,245,0.08)');
    }, 2.0),
    // crate sides: horizontal boards, each its own tone, some faded boat paint (teal, red, white), nailed at the ends
    crate: () => makeSurf(512, (c, h, r, S) => {
      const R = rng(622), rows = 6, ph = S / rows;
      c.fillStyle = '#2C2016'; c.fillRect(0, 0, S, S); h.fillStyle = gray(0.1); h.fillRect(0, 0, S, S); r.fillStyle = gray(0.9); r.fillRect(0, 0, S, S);
      for (let j = 0; j < rows; j++) { let x = -R() * S * 0.5; while (x < S) { const L = S * (0.45 + R() * 0.55), l = R(), pk = R(), base = pk < 0.16 ? [86 + l * 30, 160 + l * 30, 156 + l * 26] : pk < 0.24 ? [188 + l * 30, 78 + l * 20, 60 + l * 16] : pk < 0.3 ? [222 + l * 20, 218 + l * 20, 204 + l * 18] : [172 + l * 40, 126 + l * 32, 84 + l * 24];
        for (const off of [-S, 0, S]) { const x0 = x + off + 2, y0 = j * ph + 2.5, ww = L - 4, hh = ph - 5; if (x0 > S || x0 + ww < 0) continue;
          clip3([c, h, r], x0, y0, ww, hh); c.fillStyle = rgbS(...base); c.fillRect(x0, y0, ww, hh);
          for (let k = 0; k < 8; k++) { const gy = y0 + R() * hh, wv = (R() - 0.5) * 4; c.strokeStyle = `rgba(${R() < 0.6 ? '90,62,38' : '240,220,190'},${0.12 + R() * 0.18})`; c.lineWidth = 0.6 + R() * 1.3; c.beginPath(); c.moveTo(x0, gy); c.bezierCurveTo(x0 + ww * 0.3, gy + wv, x0 + ww * 0.7, gy - wv, x0 + ww, gy + wv * 0.3); c.stroke(); }
          if (pk < 0.3) for (let k = 0; k < 10; k++) blob(c, x0 + R() * ww, y0 + R() * hh, 6 + R() * 16, 'rgba(150,110,70,0.5)'); // (the paint worn through to the wood)
          h.fillStyle = gray(0.8); h.fillRect(x0, y0, ww, hh); r.fillStyle = gray(pk < 0.3 ? 0.6 : 0.82); r.fillRect(x0, y0, ww, hh);
          unclip3([c, h, r]); bevelRect(h, null, x0, y0, ww, hh, 3, 0.2, 0.8);
          for (const nx of [x0 + 7, x0 + ww - 7]) { c.fillStyle = 'rgba(60,46,36,0.8)'; c.beginPath(); c.arc(nx, y0 + hh / 2, 1.8, 0, 6.2832); c.fill(); } }
        x += L; } }
    }, 2.0),
    // corrugated sheet: galvanized ridges, rust bleeding from the screws and gathering in the troughs, a scuffed teal paint job half gone
    corrugated: () => makeSurf(512, (c, h, r, S) => {
      const R = rng(623), n = 16, p = S / n;
      c.fillStyle = '#7F95A0'; c.fillRect(0, 0, S, S); r.fillStyle = gray(0.42); r.fillRect(0, 0, S, S);
      for (let x = 0; x < S; x++) { const t = Math.sin(x / p * 6.2832), v = 0.5 + 0.45 * t; h.fillStyle = gray(v); h.fillRect(x, 0, 1, S); c.fillStyle = `rgba(${t > 0 ? '220,236,240' : '20,30,40'},${Math.abs(t) * 0.16})`; c.fillRect(x, 0, 1, S); }
      for (let k = 0; k < 26; k++) blob(c, R() * S, R() * S, 30 + R() * 80, `rgba(${60 + R() * 40 | 0},${150 + R() * 40 | 0},${150 + R() * 30 | 0},0.18)`);
      for (let k = 0; k < 40; k++) { const x = (Math.floor(R() * n) + 0.5) * p, y = R() * S, L = 20 + R() * 90, gr = c.createLinearGradient(x, y, x, y + L); gr.addColorStop(0, 'rgba(150,76,30,0.5)'); gr.addColorStop(1, 'rgba(150,76,30,0)'); c.fillStyle = gr; c.fillRect(x - 3, y, 6, L); r.fillStyle = grayA(0.8, 0.4); r.fillRect(x - 3, y, 6, L); }
      for (let y = 20; y < S; y += S / 4) for (let k = 0; k < n; k += 2) { const x = (k + 0.25) * p; c.fillStyle = 'rgba(70,80,86,0.9)'; c.beginPath(); c.arc(x, y, 3, 0, 6.2832); c.fill(); }
      scratches(c, r, R, 0, 0, S, S, 30);
    }, 2.2),
  });
}
