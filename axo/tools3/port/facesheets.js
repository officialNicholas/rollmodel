// ---------- the slime's face, drawn once into two sheets (4 across, 5 down) ----------
// cells 0-5 eyes: neutral, happy, angry, hurt, glee, scared; 6 eyes closed (a blink); 7 eyes squeezed shut
// cells 8-13 mouths in the same order; 14-19 the same mouths with fangs
// color sheet: everything but the pupils. mask sheet: red = where the eyeball shows (the shader draws the pupils there, so they can look
// around), green = how much the lid shades it
// face space: a cell spans -1..1 both ways, x to the slime's right as you look at it, y up
export const FACE_EYE = { x: 0.4, y: 0.16, rx: 0.3, ry: 0.33 };
export const FACE_KINDS = ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared'];
// per expression: lid height h (-1 shut .. 1 wide), slant toward the middle k, arch c, cheek (lower lid) height, pupil size, and where the
// pupils rest; L and R can differ (hurt winces one eye shut)
export const FACE_LIDS = {
  neutral: { h: 0.08, k: 0, c: 0.1, ch: -0.95, pu: 1.0, py: -0.1 },
  happy: { h: 0.42, k: 0.04, c: 0.16, ch: -0.42, chc: 0.34, pu: 1.0, py: -0.02, blush: 1 },
  angry: { h: 0.05, k: -0.46, c: -0.02, ch: -0.7, chc: 0.1, pu: 0.88, py: -0.12 },
  hurt: { L: { h: -0.12, k: 0.3, c: 0.0, ch: -0.42, chc: 0.2, pu: 0.85, py: -0.05 }, R: { shut: 'squeeze' }, sweat: 1 },
  glee: { shut: 'arc', blush: 1.2 },
  scared: { h: 0.86, k: 0.08, c: 0.06, ch: -0.97, pu: 0.62, py: -0.02 },
};
export function makeFaceSheets(C) {
  const W = C * 4, H = C * 5, col = document.createElement('canvas'), msk = document.createElement('canvas'); col.width = msk.width = W; col.height = msk.height = H;
  const g = col.getContext('2d'), m = msk.getContext('2d'); m.fillStyle = '#000'; m.fillRect(0, 0, W, H);
  const at = (ctx, cell, fn) => { ctx.save(); ctx.translate((cell % 4) * C + C / 2, Math.floor(cell / 4) * C + C / 2); ctx.scale(C / 2, -C / 2); ctx.lineJoin = 'round'; ctx.lineCap = 'round'; fn(ctx); ctx.restore(); };
  const E = FACE_EYE, INK = '40,6,18';
  // the lid's edge and the lower lid as curves across one eye (sd: -1 the left eye, 1 the right), in face space
  const lidY = (L, sd, x) => { const u = (x - sd * E.x) / E.rx; return E.y + E.ry * (L.h + (L.k || 0) * u * -sd + (L.c || 0) * (1 - u * u)); };
  const cheekY = (L, sd, x) => { const u = (x - sd * E.x) / E.rx; return E.y + E.ry * ((L.ch === undefined ? -1 : L.ch) + (L.chc || 0) * (1 - u * u)); };
  const ell = (ctx, sd, k) => { ctx.beginPath(); ctx.ellipse(sd * E.x, E.y, E.rx * (k || 1), E.ry * (k || 1), 0, 0, Math.PI * 2); };
  const curve = (ctx, f, sd, x0, x1, cont) => { const n = 40; for (let i = 0; i <= n; i++) { const x = x0 + (x1 - x0) * i / n; i || cont ? ctx.lineTo(x, f(x)) : ctx.moveTo(x, f(x)); } };
  // the open part of the eye: inside the eyeball, under the lid, over the lower lid
  const openPath = (ctx, L, sd) => { const x0 = sd * E.x - E.rx * 1.2, x1 = sd * E.x + E.rx * 1.2; ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, x0, x1); curve(ctx, x => cheekY(L, sd, x), sd, x1, x0, true); ctx.closePath(); };
  function openEye(cell, L, sd) {
    at(g, cell, ctx => {
      // the bulge's soft shadow on the skin below it
      const sh = ctx.createRadialGradient(sd * E.x, E.y - E.ry * 0.25, E.rx * 0.6, sd * E.x, E.y - E.ry * 0.25, E.rx * 1.35); sh.addColorStop(0, 'rgba(' + INK + ',0.0)'); sh.addColorStop(0.55, 'rgba(' + INK + ',0.2)'); sh.addColorStop(1, 'rgba(' + INK + ',0)');
      ctx.fillStyle = sh; ctx.beginPath(); ctx.ellipse(sd * E.x, E.y - E.ry * 0.2, E.rx * 1.35, E.ry * 1.25, 0, 0, Math.PI * 2); ctx.fill();
      ctx.save(); ell(ctx, sd); ctx.clip(); openPath(ctx, L, sd); ctx.clip();
      // the white: bright in the middle, cooler toward the rim, a touch of warm skin light bounced in from below
      const wg = ctx.createRadialGradient(sd * E.x - 0.05, E.y + 0.06, 0.02, sd * E.x, E.y, E.rx * 1.08); wg.addColorStop(0, '#FFFFFF'); wg.addColorStop(0.62, '#F4F3F8'); wg.addColorStop(1, '#C9C7D6');
      ctx.fillStyle = wg; ctx.fillRect(sd * E.x - 0.5, E.y - 0.5, 1, 1);
      ctx.restore();
      // the lid's shadow on the white (a band under its edge)
      ctx.save(); ell(ctx, sd); ctx.clip(); openPath(ctx, L, sd); ctx.clip();
      for (let k = 0; k < 6; k++) { ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) - 0.012 * k, sd, sd * E.x - E.rx * 1.2, sd * E.x + E.rx * 1.2); ctx.strokeStyle = 'rgba(60,30,70,' + (0.11 - 0.017 * k).toFixed(3) + ')'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore();
      // the rim where the white meets the skin (strong under the eye, faint up under the lid), the lash line along the lid, and light on the lid's edge
      ctx.save(); openPath(ctx, L, sd); ctx.clip(); ell(ctx, sd); ctx.strokeStyle = 'rgba(' + INK + ',0.62)'; ctx.lineWidth = 0.028; ctx.stroke(); ctx.restore();
      ctx.save(); ell(ctx, sd, 1.002); ctx.clip();
      ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, sd * E.x - E.rx * 1.1, sd * E.x + E.rx * 1.1); ctx.strokeStyle = 'rgba(' + INK + ',0.9)'; ctx.lineWidth = 0.045; ctx.stroke();
      if (L.ch > -0.9) { ctx.beginPath(); curve(ctx, x => cheekY(L, sd, x), sd, sd * E.x - E.rx * 1.1, sd * E.x + E.rx * 1.1); ctx.strokeStyle = 'rgba(' + INK + ',0.55)'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore();
      ctx.save(); ell(ctx, sd, 1.04); ctx.clip(); ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) + 0.04, sd, sd * E.x - E.rx * 0.8, sd * E.x + E.rx * 0.8); ctx.strokeStyle = 'rgba(255,240,235,0.32)'; ctx.lineWidth = 0.035; ctx.stroke();
      // the lid itself: a faint dark contour where its dome meets the face above
      ctx.restore(); ctx.save(); ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, sd * E.x - E.rx * 1.3, sd * E.x + E.rx * 1.3); ctx.lineTo(sd * E.x + E.rx * 1.3, 2); ctx.lineTo(sd * E.x - E.rx * 1.3, 2); ctx.closePath(); ctx.clip();
      ell(ctx, sd, 1.01); ctx.strokeStyle = 'rgba(' + INK + ',0.2)'; ctx.lineWidth = 0.022; ctx.stroke(); ctx.restore();
    });
    at(m, cell, ctx => { ctx.save(); ell(ctx, sd, 0.985); ctx.clip(); openPath(ctx, L, sd); ctx.clip(); ctx.fillStyle = '#FF0000'; ctx.fillRect(-1, -1, 2, 2);
      // green: the lid's shade (strong right under its edge)
      for (let k = 0; k < 8; k++) { ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) - 0.012 * k, sd, sd * E.x - E.rx * 1.2, sd * E.x + E.rx * 1.2); ctx.strokeStyle = 'rgba(255,' + Math.round(255 * (1 - k / 8)) + ',0,1)'; ctx.globalCompositeOperation = 'lighten'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore(); });
  }
  function shutEye(cell, sd, kind) {
    at(g, cell, ctx => { ctx.strokeStyle = 'rgba(' + INK + ',0.92)'; ctx.lineWidth = 0.055; const cx = sd * E.x, cy = E.y - 0.02;
      if (kind === 'arc') { ctx.beginPath(); ctx.arc(cx, cy - 0.08, E.rx * 0.82, 0.18 * Math.PI, 0.82 * Math.PI); ctx.stroke(); }
      else if (kind === 'squeeze') { ctx.beginPath(); ctx.moveTo(cx + sd * 0.2, cy + 0.15); ctx.lineTo(cx - sd * 0.12, cy); ctx.lineTo(cx + sd * 0.2, cy - 0.15); ctx.stroke(); ctx.lineWidth = 0.03; ctx.strokeStyle = 'rgba(' + INK + ',0.45)'; ctx.beginPath(); ctx.moveTo(cx - sd * 0.24, cy + 0.17); ctx.lineTo(cx - sd * 0.16, cy + 0.08); ctx.moveTo(cx - sd * 0.26, cy - 0.15); ctx.lineTo(cx - sd * 0.17, cy - 0.08); ctx.stroke(); }
      else { ctx.beginPath(); ctx.ellipse(cx, cy + 0.02, E.rx * 0.95, E.ry * 0.36, 0, Math.PI * 1.06, Math.PI * 1.94, false); ctx.stroke(); ctx.lineWidth = 0.022; ctx.strokeStyle = 'rgba(255,240,235,0.3)'; ctx.beginPath(); ctx.ellipse(cx, cy + 0.06, E.rx * 0.8, E.ry * 0.3, 0, Math.PI * 1.15, Math.PI * 1.85, false); ctx.stroke(); } });
  }
  const blush = (cell, k) => at(g, cell, ctx => { for (const sd of [-1, 1]) { const bg = ctx.createRadialGradient(sd * 0.66, -0.2, 0.01, sd * 0.66, -0.2, 0.2); bg.addColorStop(0, 'rgba(255,110,150,' + (0.55 * k).toFixed(2) + ')'); bg.addColorStop(1, 'rgba(255,110,150,0)'); ctx.fillStyle = bg; ctx.beginPath(); ctx.ellipse(sd * 0.66, -0.2, 0.22, 0.13, 0, 0, Math.PI * 2); ctx.fill(); } });
  const sweat = cell => at(g, cell, ctx => { const d = (x, y, s) => { ctx.beginPath(); ctx.moveTo(x, y + 0.13 * s); ctx.bezierCurveTo(x + 0.07 * s, y, x + 0.06 * s, y - 0.06 * s, x, y - 0.06 * s); ctx.bezierCurveTo(x - 0.06 * s, y - 0.06 * s, x - 0.07 * s, y, x, y + 0.13 * s); const gr = ctx.createLinearGradient(x, y + 0.12 * s, x, y - 0.06 * s); gr.addColorStop(0, 'rgba(190,232,255,0.95)'); gr.addColorStop(1, 'rgba(110,180,240,0.95)'); ctx.fillStyle = gr; ctx.fill(); ctx.strokeStyle = 'rgba(30,60,110,0.7)'; ctx.lineWidth = 0.018; ctx.stroke(); ctx.fillStyle = 'rgba(255,255,255,0.9)'; ctx.beginPath(); ctx.ellipse(x - 0.018 * s, y - 0.005 * s, 0.014 * s, 0.024 * s, -0.4, 0, Math.PI * 2); ctx.fill(); };
    d(0.84, 0.62, 1.15); d(0.95, 0.4, 0.7); });
  FACE_KINDS.forEach((k, i) => { const F = FACE_LIDS[k];
    for (const sd of [-1, 1]) { const L = F.L ? (sd < 0 ? F.L : F.R) : F; if (L.shut || F.shut) shutEye(i, sd, L.shut || F.shut); else openEye(i, L, sd); }
    if (F.blush) blush(i, F.blush); if (F.sweat) sweat(i); });
  for (const sd of [-1, 1]) { shutEye(6, sd, 'closed'); shutEye(7, sd, 'squeeze'); }
  // ---- the lashes (worn as an accessory): drawn into the mask sheet's blue over every eye cell, so they follow each expression and blink;
  // the shader inks them only when they're worn. A liner along the top of the eye flicking up past its outer corner, and three long
  // lashes sweeping up and out from its outer half, curling at the tips (shut eyes: they hang from the lid and curl up). Drawn for the
  // right eye, mirrored for the left ----
  const clampL = (v, a, b) => Math.max(a, Math.min(b, v));
  const taper = (ctx, pts, wf) => { const n = pts.length, A = [], B = [];
    for (let i = 0; i < n; i++) { const a = pts[Math.max(0, i - 1)], b = pts[Math.min(n - 1, i + 1)], tx = b[0] - a[0], ty = b[1] - a[1], l = Math.hypot(tx, ty) || 1, w = wf(i / (n - 1)) * 0.5;
      A.push([pts[i][0] - ty / l * w, pts[i][1] + tx / l * w]); B.push([pts[i][0] + ty / l * w, pts[i][1] - tx / l * w]); }
    ctx.beginPath(); A.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); for (let i = n - 1; i >= 0; i--) ctx.lineTo(B[i][0], B[i][1]); ctx.closePath(); ctx.fill(); };
  // one lash: from p at angle a, turning by curl along its length (more toward the tip), tapering to a point
  const lash = (ctx, p, a, len, curl, w0) => { const pts = [[p[0], p[1]]], n = 18; let x = p[0], y = p[1];
    for (let i = 1; i <= n; i++) { const u = i / n; a += curl / n * (0.2 + 1.6 * u); x += Math.cos(a) * len / n; y += Math.sin(a) * len / n; pts.push([x, y]); }
    taper(ctx, pts, u => w0 * Math.pow(1 - u, 0.75) + 0.003); };
  // the liner: thin at its start, thickest at the corner, then a flick on past it turning up to a point
  const liner = (ctx, pts, a, w) => { const n = pts.length - 1; let [px, py] = pts[n];
    for (let i = 0; i < 9; i++) { a += 0.07; px += Math.cos(a) * 0.017; py += Math.sin(a) * 0.017; pts.push([px, py]); }
    const m0 = n / (pts.length - 1); taper(ctx, pts, u => u <= m0 ? w * (0.38 + 0.62 * Math.pow(u / m0, 0.6)) : w * Math.pow(1 - (u - m0) / (1 - m0), 0.85) + 0.003); };
  const rimT = x => { const u = (x - E.x) / E.rx; return Math.sqrt(Math.max(0, 1 - u * u)); };
  const topY = (L, x) => Math.min(lidY(L, 1, x), E.y + E.ry * rimT(x)), botY = (L, x) => Math.max(cheekY(L, 1, x), E.y - E.ry * rimT(x));
  const LASHES = [[0.38, 0.31, 1.42, -0.62], [0.65, 0.36, 1.06, -0.68], [0.9, 0.34, 0.76, -0.66]]; // where along the outer half, length, lean, curl
  function lashOpen(ctx, L) {
    let x0 = null, x1 = null; for (let i = 0; i <= 240; i++) { const x = E.x - E.rx + 2 * E.rx * i / 240; if (topY(L, x) > botY(L, x) + 0.012) { if (x0 === null) x0 = x; x1 = x; } }
    if (x0 === null) return; const pts = []; for (let i = 0; i <= 40; i++) { const x = x0 + (x1 - x0) * i / 40; pts.push([x, topY(L, x) + 0.004]); }
    const q = pts[36], z = pts[40]; liner(ctx, pts, clampL(Math.atan2(z[1] - q[1], z[0] - q[0]), -0.25, 0.55) + 0.3, 0.092);
    for (const [t, len, a0, curl] of LASHES) { const x = E.x + (x1 - E.x) * t, y = topY(L, x), sl = (topY(L, x + 0.004) - topY(L, x - 0.004)) / 0.008, a = clampL(a0 + 0.45 * (Math.atan2(1, -sl) - Math.PI / 2), 0.32, 1.65);
      lash(ctx, [x, y + 0.006], a, len, Math.max(curl, -0.12 - a), 0.064); }
  }
  function lashShut(ctx, kind) {
    const cy = E.y - 0.02;
    if (kind === 'arc') { const r = E.rx * 0.82, oy = cy - 0.08, pts = []; for (let i = 0; i <= 40; i++) { const th = 0.82 * Math.PI - 0.64 * Math.PI * i / 40; pts.push([E.x + r * Math.cos(th), oy + r * Math.sin(th)]); }
      liner(ctx, pts, -0.18 * Math.PI - Math.PI / 2 + 0.55, 0.085);
      for (const [t, len, , curl] of LASHES) { const th = 0.5 * Math.PI - 0.32 * Math.PI * t, a = clampL(th + 0.12, 0.32, 1.6); lash(ctx, [E.x + r * Math.cos(th), oy + r * Math.sin(th)], a, len * 0.9, Math.max(curl, -0.12 - a), 0.062); } }
    else if (kind === 'squeeze') { const p0 = [E.x - 0.12, cy], p1 = [E.x + 0.2, cy + 0.15], pts = []; for (let i = 0; i <= 20; i++) pts.push([p0[0] + (p1[0] - p0[0]) * i / 20, p0[1] + (p1[1] - p0[1]) * i / 20]);
      liner(ctx, pts, Math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + 0.15, 0.08);
      for (const [t, len, a] of [[0.55, 0.24, 1.3], [0.82, 0.28, 1.0], [1.0, 0.27, 0.7]]) lash(ctx, [p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t], a, len, -0.58, 0.058); }
    else { const a = E.rx * 0.95, b = E.ry * 0.36, oy = cy + 0.02, pts = []; for (let i = 0; i <= 40; i++) { const th = 1.06 * Math.PI + 0.88 * Math.PI * i / 40; pts.push([E.x + a * Math.cos(th), oy + b * Math.sin(th)]); }
      liner(ctx, pts, 0.42, 0.088);
      for (const [t, len] of [[0.36, 0.25], [0.62, 0.29], [0.86, 0.29]]) { const th = 1.5 * Math.PI + 0.44 * Math.PI * t, nrm = Math.atan2(Math.sin(th) / b, Math.cos(th) / a), an = clampL(nrm + 0.3, -1.45, -0.3);
        lash(ctx, [E.x + a * Math.cos(th), oy + b * Math.sin(th) - 0.004], an, len, 0.72, 0.06); } }
  }
  const lashCell = (cell, sd, fn) => at(m, cell, ctx => { if (sd < 0) ctx.scale(-1, 1); ctx.globalCompositeOperation = 'lighten'; ctx.fillStyle = '#0000FF'; fn(ctx); });
  FACE_KINDS.forEach((k, i) => { const F = FACE_LIDS[k];
    for (const sd of [-1, 1]) { const L = F.L ? (sd < 0 ? F.L : F.R) : F; lashCell(i, sd, ctx => L.shut || F.shut ? lashShut(ctx, L.shut || F.shut) : lashOpen(ctx, L)); } });
  for (const sd of [-1, 1]) { lashCell(6, sd, ctx => lashShut(ctx, 'closed')); lashCell(7, sd, ctx => lashShut(ctx, 'squeeze')); }
  // ---- mouths ----
  const MY = -0.5;
  const cavity = (ctx, path, top, bot, tongue) => {
    path(); const gr = ctx.createLinearGradient(0, top, 0, bot); gr.addColorStop(0, '#2A0410'); gr.addColorStop(0.55, '#5A0C1E'); gr.addColorStop(1, '#7E1A2C'); ctx.fillStyle = gr; ctx.fill();
    ctx.save(); path(); ctx.clip();
    if (tongue) { const [tx, ty, tw, th] = tongue, tg = ctx.createRadialGradient(tx - tw * 0.2, ty + th * 0.35, 0, tx, ty, tw * 1.1); tg.addColorStop(0, '#FF9DB0'); tg.addColorStop(0.6, '#F0607E'); tg.addColorStop(1, '#C23A58'); ctx.fillStyle = tg; ctx.beginPath(); ctx.ellipse(tx, ty, tw, th, 0, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = 'rgba(255,215,225,0.55)'; ctx.beginPath(); ctx.ellipse(tx - tw * 0.32, ty + th * 0.42, tw * 0.22, th * 0.14, -0.3, 0, Math.PI * 2); ctx.fill(); }
    const sh = ctx.createLinearGradient(0, top, 0, top - (top - bot) * 0.45); sh.addColorStop(0, 'rgba(10,0,4,0.75)'); sh.addColorStop(1, 'rgba(10,0,4,0)'); ctx.fillStyle = sh; ctx.fillRect(-2, bot, 4, top - bot + 0.2);
    ctx.restore(); path(); ctx.strokeStyle = 'rgba(' + INK + ',0.85)'; ctx.lineWidth = 0.032; ctx.stroke();
  };
  const fang = (ctx, x, y, s) => { ctx.beginPath(); ctx.moveTo(x - 0.035 * s, y + 0.005); ctx.quadraticCurveTo(x - 0.01 * s, y - 0.07 * s, x + 0.002 * s, y - 0.088 * s); ctx.quadraticCurveTo(x + 0.014 * s, y - 0.06 * s, x + 0.035 * s, y + 0.005); ctx.closePath(); const fg = ctx.createLinearGradient(0, y, 0, y - 0.09 * s); fg.addColorStop(0, '#FFFFFF'); fg.addColorStop(1, '#E9E2F0'); ctx.fillStyle = fg; ctx.fill(); ctx.strokeStyle = 'rgba(' + INK + ',0.7)'; ctx.lineWidth = 0.014; ctx.stroke(); };
  const line = (ctx, pts, w) => { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.strokeStyle = 'rgba(' + INK + ',0.92)'; ctx.lineWidth = w || 0.045; ctx.stroke(); };
  const dPath = (ctx, w, top, h, dip) => () => { ctx.beginPath(); ctx.moveTo(-w, top); ctx.quadraticCurveTo(0, top - dip, w, top); for (let k = 1; k <= 40; k++) { const t = k / 40 * Math.PI; ctx.lineTo(w * Math.cos(t), top - h * Math.sin(t)); } ctx.closePath(); };
  const MOUTHS = {
    neutral: (ctx, f) => { line(ctx, Array.from({ length: 21 }, (_, i) => { const u = i / 20 - 0.5; return [u * 0.2, MY + 0.03 - 0.035 * Math.cos(u * Math.PI)]; }), 0.034); if (f) { fang(ctx, -0.05, MY + 0.0, 0.8); fang(ctx, 0.05, MY + 0.0, 0.8); } },
    happy: (ctx, f) => { cavity(ctx, dPath(ctx, 0.2, MY + 0.08, 0.2, 0.03), MY + 0.08, MY - 0.12, [0, MY - 0.09, 0.11, 0.07]); if (f) { fang(ctx, -0.085, MY + 0.072, 0.95); fang(ctx, 0.085, MY + 0.072, 0.95); } },
    angry: (ctx, f) => { line(ctx, [[-0.12, MY - 0.03], [-0.03, MY + 0.01], [0.05, MY + 0.0], [0.12, MY - 0.035]], 0.04); if (f) { fang(ctx, -0.055, MY + 0.003, 0.85); fang(ctx, 0.045, MY + 0.002, 0.85); } },
    hurt: (ctx, f) => { line(ctx, Array.from({ length: 33 }, (_, i) => { const u = i / 32; return [-0.15 + 0.3 * u, MY + 0.025 * Math.sin(u * Math.PI * 4)]; }), 0.036); if (f) { fang(ctx, -0.06, MY + 0.02, 0.75); fang(ctx, 0.06, MY - 0.005, 0.75); } },
    glee: (ctx, f) => { cavity(ctx, dPath(ctx, 0.27, MY + 0.12, 0.3, 0.05), MY + 0.12, MY - 0.18, [0, MY - 0.14, 0.15, 0.1]); if (f) { fang(ctx, -0.12, MY + 0.11, 1.1); fang(ctx, 0.12, MY + 0.11, 1.1); } },
    scared: (ctx, f) => { cavity(ctx, () => { ctx.beginPath(); ctx.ellipse(0, MY - 0.02, 0.07, 0.1, 0, 0, Math.PI * 2); }, MY + 0.08, MY - 0.12, null); if (f) { fang(ctx, -0.035, MY + 0.07, 0.6); fang(ctx, 0.035, MY + 0.07, 0.6); } },
  };
  const big = (ctx, fn) => { ctx.translate(0, MY); ctx.scale(1.35, 1.35); ctx.translate(0, -MY); fn(); };
  FACE_KINDS.forEach((k, i) => { at(g, 8 + i, ctx => big(ctx, () => MOUTHS[k](ctx, false))); at(g, 14 + i, ctx => big(ctx, () => MOUTHS[k](ctx, true))); });
  return { col, msk };
}