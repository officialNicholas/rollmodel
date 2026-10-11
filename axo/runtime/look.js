// The axolotl's look: team-colour recolour of the baked texture, wet goo with clearcoat, the paint coat rising by a per-vertex fill order,
// a soft-body jelly layer in the vertex shader (breathing, lag wobble, squash / stretch, ripple; the head is rigid), rim light and thin-part
// warmth, and the face (eyes, pupils, blink, mouth, fangs) projected onto the front of the head from the rest-space head frame.
import * as THREE from 'three';

// ---------------- the shared face: one definition in head-local units (head radii, angles from the head centre), so both meshes carry the same face ----------------
export const FACE = {
  // eyes: direction from the head centre (yaw out to the side, pitch up), ball radius in head radii, how deep the ball sinks into the skin,
  // how much the gaze turns outward (0 = both eyes dead ahead), a vertical tilt of the gaze, the socket ring and the lid shell radii (in ball radii)
  eye: { yaw: 0.9, height: 0.2, size: 0.25, embed: 0.62, gaze: 0.22, tilt: 0.0, socket: 1.25, lid: 1.07 },
  // mouth / nostril sheet projection: yaw half-width (rad) and half-height (face-frame half heights) of the sheet, the height of its centre
  sheet: { yaw: 1.2, height: 0.7, centre: 0.0 },
};
// ---------------- face sheets (ported from the game's slime: 4 x 5 cells; 0-5 eyes, 6 closed, 7 squeezed, 8-13 mouths, 14-19 mouths with fangs) ----------------
export const FACE_EYE = { x: 0.4, y: 0.16, rx: 0.3, ry: 0.33 };
export const FACE_KINDS = ['neutral', 'happy', 'angry', 'hurt', 'glee', 'scared'];
export const FACE_LIDS = {
  neutral: { h: 0.08, k: 0, c: 0.1, ch: -0.95, pu: 1.0, py: -0.1 },
  happy: { h: 0.42, k: 0.04, c: 0.16, ch: -0.42, chc: 0.34, pu: 1.0, py: -0.02, blush: 1 },
  angry: { h: 0.05, k: -0.46, c: -0.02, ch: -0.7, chc: 0.1, pu: 0.88, py: -0.12 },
  hurt: { L: { h: -0.12, k: 0.3, c: 0.0, ch: -0.42, chc: 0.2, pu: 0.85, py: -0.05 }, R: { shut: 'squeeze' }, sweat: 1 },
  glee: { shut: 'arc', blush: 1.2 },
  scared: { h: 0.86, k: 0.08, c: 0.06, ch: -0.97, pu: 0.62, py: -0.02 },
};
export const EXPR = { neutral: [0, 8], happy: [1, 9], angry: [2, 10], hurt: [3, 11], glee: [4, 12], scared: [5, 13], yawn: [6, 13], dizzy: [7, 11], peek: [5, 13], leap: [5, 9], brace: [7, 11] };
const PUPILS = { peek: { pu: 1.08, py: 0 }, leap: { pu: 1.12, py: 0 } };
export function pupilOf(name) { const F = PUPILS[name] || FACE_LIDS[name]; if (!F) return { pu: 1, py: 0 }; const L = F.L || F; return { pu: L.pu || 1, py: (L.py || 0) * FACE_EYE.ry }; }
export function makeFaceSheets(C) {
  const W = C * 4, H = C * 5, col = document.createElement('canvas'), msk = document.createElement('canvas'); col.width = msk.width = W; col.height = msk.height = H;
  const g = col.getContext('2d'), m = msk.getContext('2d'); m.fillStyle = '#000'; m.fillRect(0, 0, W, H);
  const at = (ctx, cell, fn) => { ctx.save(); ctx.translate((cell % 4) * C + C / 2, Math.floor(cell / 4) * C + C / 2); ctx.scale(C / 2, -C / 2); ctx.lineJoin = 'round'; ctx.lineCap = 'round'; fn(ctx); ctx.restore(); };
  const E = FACE_EYE, INK = '40,6,18';
  const lidY = (L, sd, x) => { const u = (x - sd * E.x) / E.rx; return E.y + E.ry * (L.h + (L.k || 0) * u * -sd + (L.c || 0) * (1 - u * u)); };
  const cheekY = (L, sd, x) => { const u = (x - sd * E.x) / E.rx; return E.y + E.ry * ((L.ch === undefined ? -1 : L.ch) + (L.chc || 0) * (1 - u * u)); };
  const ell = (ctx, sd, k) => { ctx.beginPath(); ctx.ellipse(sd * E.x, E.y, E.rx * (k || 1), E.ry * (k || 1), 0, 0, Math.PI * 2); };
  const curve = (ctx, f, sd, x0, x1, cont) => { const n = 40; for (let i = 0; i <= n; i++) { const x = x0 + (x1 - x0) * i / n; i || cont ? ctx.lineTo(x, f(x)) : ctx.moveTo(x, f(x)); } };
  const openPath = (ctx, L, sd) => { const x0 = sd * E.x - E.rx * 1.2, x1 = sd * E.x + E.rx * 1.2; ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, x0, x1); curve(ctx, x => cheekY(L, sd, x), sd, x1, x0, true); ctx.closePath(); };
  function openEye(cell, L, sd) {
    at(g, cell, ctx => {
      const sh = ctx.createRadialGradient(sd * E.x, E.y - E.ry * 0.25, E.rx * 0.6, sd * E.x, E.y - E.ry * 0.25, E.rx * 1.35); sh.addColorStop(0, 'rgba(' + INK + ',0.0)'); sh.addColorStop(0.55, 'rgba(' + INK + ',0.2)'); sh.addColorStop(1, 'rgba(' + INK + ',0)');
      ctx.fillStyle = sh; ctx.beginPath(); ctx.ellipse(sd * E.x, E.y - E.ry * 0.2, E.rx * 1.35, E.ry * 1.25, 0, 0, Math.PI * 2); ctx.fill();
      ctx.save(); ell(ctx, sd); ctx.clip(); openPath(ctx, L, sd); ctx.clip();
      const wg = ctx.createRadialGradient(sd * E.x - 0.05, E.y + 0.06, 0.02, sd * E.x, E.y, E.rx * 1.08); wg.addColorStop(0, '#FFFFFF'); wg.addColorStop(0.62, '#F4F3F8'); wg.addColorStop(1, '#C9C7D6');
      ctx.fillStyle = wg; ctx.fillRect(sd * E.x - 0.5, E.y - 0.5, 1, 1); ctx.restore();
      ctx.save(); ell(ctx, sd); ctx.clip(); openPath(ctx, L, sd); ctx.clip();
      for (let k = 0; k < 6; k++) { ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) - 0.012 * k, sd, sd * E.x - E.rx * 1.2, sd * E.x + E.rx * 1.2); ctx.strokeStyle = 'rgba(60,30,70,' + (0.11 - 0.017 * k).toFixed(3) + ')'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore();
      ctx.save(); openPath(ctx, L, sd); ctx.clip(); ell(ctx, sd); ctx.strokeStyle = 'rgba(' + INK + ',0.62)'; ctx.lineWidth = 0.028; ctx.stroke(); ctx.restore();
      ctx.save(); ell(ctx, sd, 1.002); ctx.clip();
      ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, sd * E.x - E.rx * 1.1, sd * E.x + E.rx * 1.1); ctx.strokeStyle = 'rgba(' + INK + ',0.9)'; ctx.lineWidth = 0.045; ctx.stroke();
      if (L.ch > -0.9) { ctx.beginPath(); curve(ctx, x => cheekY(L, sd, x), sd, sd * E.x - E.rx * 1.1, sd * E.x + E.rx * 1.1); ctx.strokeStyle = 'rgba(' + INK + ',0.55)'; ctx.lineWidth = 0.03; ctx.stroke(); }
      ctx.restore();
      ctx.save(); ell(ctx, sd, 1.04); ctx.clip(); ctx.beginPath(); curve(ctx, x => lidY(L, sd, x) + 0.04, sd, sd * E.x - E.rx * 0.8, sd * E.x + E.rx * 0.8); ctx.strokeStyle = 'rgba(255,240,235,0.32)'; ctx.lineWidth = 0.035; ctx.stroke();
      ctx.restore(); ctx.save(); ctx.beginPath(); curve(ctx, x => lidY(L, sd, x), sd, sd * E.x - E.rx * 1.3, sd * E.x + E.rx * 1.3); ctx.lineTo(sd * E.x + E.rx * 1.3, 2); ctx.lineTo(sd * E.x - E.rx * 1.3, 2); ctx.closePath(); ctx.clip();
      ell(ctx, sd, 1.01); ctx.strokeStyle = 'rgba(' + INK + ',0.2)'; ctx.lineWidth = 0.022; ctx.stroke(); ctx.restore();
    });
    at(m, cell, ctx => { ctx.save(); ell(ctx, sd, 0.985); ctx.clip(); openPath(ctx, L, sd); ctx.clip(); ctx.fillStyle = '#FF0000'; ctx.fillRect(-1, -1, 2, 2);
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
  const lip = (ctx, path, y0, y1) => { ctx.save(); path(); ctx.clip(); const lg = ctx.createLinearGradient(0, y0, 0, y1); lg.addColorStop(0, 'rgba(255,220,225,0.0)'); lg.addColorStop(1, 'rgba(255,228,232,0.85)'); ctx.fillStyle = lg; ctx.fillRect(-2, y1 - 0.5, 4, 0.5 + (y0 - y1)); ctx.restore(); };
  const smile = (ctx, w, lift, thick, f) => { line(ctx, Array.from({ length: 41 }, (_, i) => { const u = i / 40 - 0.5; return [u * 2 * w, MY + 0.02 + lift * (1 - Math.cos(u * Math.PI * 2)) * 0.5 - 0.02 * Math.cos(u * Math.PI)]; }), thick); if (f) { fang(ctx, -0.16, MY + 0.03, 0.8); fang(ctx, 0.16, MY + 0.03, 0.8); } };
  const MOUTHS = {
    neutral: (ctx, f) => smile(ctx, 0.8, 0.11, 0.03, f),
    happy: (ctx, f) => { const P = dPath(ctx, 0.74, MY + 0.1, 0.24, 0.05); cavity(ctx, P, MY + 0.1, MY - 0.16, [0, MY - 0.1, 0.3, 0.09]); lip(ctx, P, MY - 0.02, MY - 0.16); if (f) { fang(ctx, -0.3, MY + 0.085, 0.95); fang(ctx, 0.3, MY + 0.085, 0.95); } },
    angry: (ctx, f) => { line(ctx, [[-0.62, MY + 0.04], [-0.35, MY - 0.06], [-0.1, MY - 0.09], [0.1, MY - 0.09], [0.35, MY - 0.06], [0.62, MY + 0.04]], 0.036); if (f) { fang(ctx, -0.2, MY - 0.07, 0.85); fang(ctx, 0.2, MY - 0.07, 0.85); } },
    hurt: (ctx, f) => { line(ctx, Array.from({ length: 49 }, (_, i) => { const u = i / 48; return [-0.6 + 1.2 * u, MY - 0.02 + 0.03 * Math.sin(u * Math.PI * 6)]; }), 0.034); if (f) { fang(ctx, -0.2, MY, 0.75); fang(ctx, 0.2, MY - 0.03, 0.75); } },
    glee: (ctx, f) => { const P = dPath(ctx, 0.8, MY + 0.14, 0.34, 0.07); cavity(ctx, P, MY + 0.14, MY - 0.22, [0, MY - 0.15, 0.36, 0.12]); lip(ctx, P, MY - 0.04, MY - 0.22); if (f) { fang(ctx, -0.34, MY + 0.12, 1.1); fang(ctx, 0.34, MY + 0.12, 1.1); } },
    scared: (ctx, f) => { const P = () => { ctx.beginPath(); ctx.ellipse(0, MY - 0.03, 0.13, 0.12, 0, 0, Math.PI * 2); }; cavity(ctx, P, MY + 0.08, MY - 0.15, null); if (f) { fang(ctx, -0.07, MY + 0.07, 0.6); fang(ctx, 0.07, MY + 0.07, 0.6); } },
  };
  const big = (ctx, fn) => { ctx.translate(0, MY); ctx.scale(1.0, 1.0); ctx.translate(0, -MY); fn(); };
  FACE_KINDS.forEach((k, i) => { at(g, 8 + i, ctx => big(ctx, () => MOUTHS[k](ctx, false))); at(g, 14 + i, ctx => big(ctx, () => MOUTHS[k](ctx, true))); });
  return { col, msk };
}
// a tiling height map of bumpy amphibian skin: soft lumps (two octaves of wrapped value noise) with small pits (pores) between them
let BUMP = null;
export function bumpTexture(N = 256) {
  if (BUMP) return BUMP;
  const lat = (n, seed) => { const a = new Float32Array(n * n); let x = seed; for (let i = 0; i < a.length; i++) { x = (x * 1664525 + 1013904223) >>> 0; a[i] = (x >>> 8) / 16777216; } return a; };
  const sm = t => t * t * (3 - 2 * t);
  const noise = (L, n, u, v) => { const x = u * n, y = v * n, x0 = Math.floor(x), y0 = Math.floor(y), fx = sm(x - x0), fy = sm(y - y0); const g = (i, j) => L[((j % n + n) % n) * n + ((i % n + n) % n)];
    return (g(x0, y0) * (1 - fx) + g(x0 + 1, y0) * fx) * (1 - fy) + (g(x0, y0 + 1) * (1 - fx) + g(x0 + 1, y0 + 1) * fx) * fy; };
  const L8 = lat(8, 7), L16 = lat(16, 19), L32 = lat(32, 41); const pts = []; const PN = 14, PL = lat(PN * PN * 2, 5);
  for (let j = 0; j < PN; j++) for (let i = 0; i < PN; i++) pts.push([(i + 0.15 + 0.7 * PL[(j * PN + i) * 2]) / PN, (j + 0.15 + 0.7 * PL[(j * PN + i) * 2 + 1]) / PN]);
  const data = new Uint8Array(N * N);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) { const u = x / N, v = y / N;
    let h = 0.5 * noise(L8, 8, u, v) + 0.32 * noise(L16, 16, u, v) + 0.18 * noise(L32, 32, u, v);
    let pit = 0; for (const [px, py] of pts) { let dx = Math.abs(u - px), dy = Math.abs(v - py); dx = Math.min(dx, 1 - dx); dy = Math.min(dy, 1 - dy); const d2 = (dx * dx + dy * dy) * PN * PN * 9.0; pit = Math.max(pit, Math.exp(-d2)); }
    h = h * 0.8 + 0.1 - 0.28 * pit; data[y * N + x] = Math.max(0, Math.min(255, Math.round(h * 255))); }
  const t = new THREE.DataTexture(data, N, N, THREE.RedFormat, THREE.UnsignedByteType); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.magFilter = THREE.LinearFilter; t.minFilter = THREE.LinearMipmapLinearFilter; t.generateMipmaps = true; t.anisotropy = 4; t.needsUpdate = true;
  return BUMP = t;
}
let SHEETS = null;
export function faceSheets(C = 256) {
  if (SHEETS) return SHEETS; const sh = makeFaceSheets(C);
  const col = new THREE.CanvasTexture(sh.col), msk = new THREE.CanvasTexture(sh.msk); col.colorSpace = THREE.SRGBColorSpace; col.anisotropy = 4; msk.colorSpace = THREE.NoColorSpace;
  for (const t of [col, msk]) { t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; }
  return SHEETS = { col, msk };
}

// ---------------- shader pieces ----------------
// vertex: the jelly layer on the skinned position, and the face / coat varyings from the REST position (so the face rides the head rigidly)
const VERT_PARS = `
attribute vec4 jelly; attribute vec2 fill; attribute vec2 xtra;
uniform vec4 uJelly;   // x breath (m), y squash (-stretch .. +squash), z body height (m), w ripple (m)
uniform vec4 uLag;     // xyz: lag offset of the soft body (object space, m), w: time
uniform vec4 uFace;    // x yaw half-width (rad), y half-height (head radii), z height of the sheet centre (head radii), w on
uniform vec4 uHead;    // xyz head centre (rest, object space), w head radius
uniform vec2 uHeadF;   // x height of the face frame's centre (object space), y its half height (dome top to chin)
uniform float uCoatMix;
varying vec3 vSkinP, vFace, vRestN; varying vec4 vJelly; varying float vFill; varying vec2 vXtra;`;
const VERT_MAIN = `
{
  vJelly = jelly; vSkinP = position; vRestN = normal; vXtra = xtra; vFill = mix(fill.x, fill.y, uCoatMix);
  vec3 d = position - uHead.xyz; float yw = atan(d.x, d.z), ht = (position.y - uHeadF.x) / uHeadF.y;
  vFace = vec3(yw / uFace.x, (ht - uFace.z) / uFace.y, smoothstep(0.05, 0.4, d.z / uHead.w) * smoothstep(0.6, 0.9, jelly.w) * uFace.w);
  float soft = jelly.y, h = clamp(transformed.y / uJelly.z, 0.0, 1.0);
  transformed += objectNormal * (jelly.x * uJelly.x + uJelly.w * soft * sin(position.x * 23.0 + position.y * 17.0 + uLag.w * 9.0) * sin(position.z * 19.0 - uLag.w * 7.0));
  float s = uJelly.y * soft; transformed.y *= 1.0 - s; transformed.xz *= 1.0 + 0.5 * s;
  transformed += uLag.xyz * soft * h;
}`;
// fragment: the recolour, the coat, the face, the gloss, the rim and the thin-part warmth
const FRAG_PARS = `
uniform vec3 uTeam, uPaint; uniform vec4 uCoat;   // uCoat: x level 0..1, y seed, z wet 0..1, w 0
uniform sampler2D fCol, fMsk; uniform vec4 fCells, fMix, fPupil, fComp; uniform vec3 fIris; uniform float fStyle; uniform vec3 uKeyDir;
uniform sampler2D uBump; uniform vec4 uBumpK; uniform vec3 uAlong; uniform float uDebug;
varying vec3 vSkinP, vFace, vRestN; varying vec4 vJelly; varying float vFill; varying vec2 vXtra;
float sCoatM = 0.0, sGloss = 0.5, faceInk = 0.0, sRed = 0.0, sFil = 0.0;
// skin relief: a tiling bumpy-skin height sampled triplanar in rest space (no seams, the same scale everywhere), perturbing the lit normal
// from its screen-space derivatives (Mikkelsen's unparametrized bump mapping, as three's bumpMap does)
float skinH(vec3 p, vec3 n) { vec3 w = pow(abs(n), vec3(3.0)); w /= (w.x + w.y + w.z + 1e-4); float f = uBumpK.y;
  return texture2D(uBump, p.yz * f).r * w.x + texture2D(uBump, p.xz * f).r * w.y + texture2D(uBump, p.xy * f).r * w.z; }
vec3 axoPerturb(vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection) {
  vec3 vSigmaX = normalize(dFdx(surf_pos.xyz)), vSigmaY = normalize(dFdy(surf_pos.xyz)), vN = surf_norm;
  vec3 R1 = cross(vSigmaY, vN), R2 = cross(vN, vSigmaX); float fDet = dot(vSigmaX, R1) * faceDirection;
  vec3 vGrad = sign(fDet) * (dHdxy.x * R1 + dHdxy.y * R2); return normalize(abs(fDet) * surf_norm - vGrad); }
vec3 sHue(vec3 c, float a){ const vec3 k = vec3(0.57735); float ca = cos(a); return c * ca + cross(k, c) * sin(a) + k * dot(k, c) * (1.0 - ca); }
vec3 rgb2hsv(vec3 c){ vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0); vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g)); vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
  float d = q.x - min(q.w, q.y), e = 1.0e-10; return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x); }
float coatField(vec3 sp, float sy){ vec3 cq = sp * 5.0 + uCoat.y;
  float ch = 0.5 + 0.25 * sin(cq.x * 1.7 + sin(cq.y * 2.3)) * sin(cq.z * 1.9 + sin(cq.x * 1.3)) + 0.25 * sin(cq.y * 3.1 + cq.z * 1.1 + cq.x * 0.7);
  return clamp(0.55 * ch + 0.45 * sy, 0.0, 1.0); }
vec2 fCell(float c, vec2 uv){ float col = mod(c, 4.0), row = floor(c * 0.25 + 0.01); return vec2((col + uv.x) * 0.25, 1.0 - (row + 1.0 - uv.y) * 0.2); }`;
// the recolour: the baked map's pink skin, pale belly, red gills and blue fin each take a member of the team colour's palette, keeping the map's own shading
const MAP_FS = `
{
  const vec3 LW = vec3(0.2126, 0.7152, 0.0722);
  vec4 texel = texture2D(map, vMapUv); vec3 tl = texel.rgb; float lum = dot(tl, LW); vec3 hsv = rgb2hsv(tl);
  vec3 T = max(mix(vec3(dot(uTeam, LW)), uTeam, 1.1), vec3(0.0));   // the team colour, a touch richer than the swatch
  vec3 HA = max(sHue(T, 0.34), vec3(0.0)), HB = max(sHue(T, -0.34), vec3(0.0)); float upA = step(dot(HB, LW), dot(HA, LW));
  vec3 up = mix(HB, HA, upA), dn = mix(HA, HB, upA);
  vec3 skinC = T, bellyC = mix(T, vec3(1.0), 0.26), gillC = clamp(mix(pow(T, vec3(1.7)) * 1.35, dn, 0.3), 0.0, 1.0), finC = mix(up, vec3(1.0), 0.2);
  float redM = smoothstep(0.45, 0.65, hsv.y) * (1.0 - smoothstep(0.04, 0.09, min(hsv.x, 1.0 - hsv.x))) * (1.0 - smoothstep(0.3, 0.5, lum));
  float blueM = smoothstep(0.2, 0.35, hsv.y) * smoothstep(0.5, 0.58, hsv.x) * (1.0 - smoothstep(0.82, 0.9, hsv.x));
  float paleM = (1.0 - smoothstep(0.08, 0.36, hsv.y)) * smoothstep(0.2, 0.45, lum) * (1.0 - redM) * (1.0 - blueM);
  paleM = max(paleM, smoothstep(0.25, 0.8, vJelly.x) * (1.0 - redM) * (1.0 - blueM)); float skinM = max(0.0, 1.0 - redM - blueM - paleM); sRed = redM;
  // the gill filaments: fine feathery stripes across the stalks, denser and deeper at the roots
  sFil = 0.5 + 0.5 * sin(vSkinP.x * 240.0 + vSkinP.z * 50.0 + 2.5 * sin(vSkinP.y * 70.0 + vSkinP.z * 35.0));
  vec3 pal = skinC * clamp(lum / 0.4, 0.5, 1.05) * skinM + bellyC * clamp(lum / 0.5, 0.8, 1.0) * paleM + gillC * clamp(lum / 0.2, 0.7, 1.25) * (1.0 - 0.3 * sFil) * redM + finC * min(1.1, lum / 0.3) * blueM;
  pal = mix(pal, bellyC * 0.95, 0.4 * vXtra.y);   // the webs: a little paler, like the belly
  diffuseColor.rgb = clamp(pal, 0.0, 1.0);
}
if (uCoat.x > 0.001) {
  float ch = coatField(vSkinP, vFill), cv = uCoat.x * 1.08 - 0.04;
  sCoatM = smoothstep(ch - 0.035, ch + 0.035, cv);
  vec3 pc = max(mix(vec3(dot(uPaint, vec3(0.2126, 0.7152, 0.0722))), uPaint, 1.1), vec3(0.0)) * 0.8;   // (the paint: the body's colour, a touch deeper and richer, as wet paint is)
  diffuseColor.rgb = mix(diffuseColor.rgb, pc, sCoatM) * (1.0 - 0.3 * (1.0 - smoothstep(0.0, 0.06, abs(cv - ch))) * step(uCoat.x, 0.995));
}`;
// the skin relief: bumpy amphibian skin and pores everywhere (softer on the face and the belly), costal grooves across the trunk and
// rays along the fin, the gill filaments; flat under the paint coat (wet paint levels it)
const BUMP_FS = `
{
  float dorsal = (1.0 - vJelly.x) * vJelly.y * (1.0 - vJelly.w), web = vXtra.y, along = dot(vSkinP, uAlong);
  float amp = uBumpK.x * (0.55 + 0.45 * dorsal) * (1.0 - 0.5 * vJelly.w) * (1.0 - 0.7 * web) * (1.0 - sCoatM);
  float h = skinH(vSkinP, vRestN) * amp;
  h += uBumpK.z * (1.0 - sCoatM) * (dorsal * (1.0 - vJelly.z) * (0.5 + 0.5 * sin(along * 70.0 + 1.2 * sin(vSkinP.x * 40.0 + vSkinP.y * 25.0)))
     + vJelly.z * (1.0 - sRed) * (1.0 - web) * 0.7 * (0.5 + 0.5 * sin(along * 140.0)) + sRed * 0.8 * sFil);
  normal = axoPerturb(-vViewPosition, normal, vec2(dFdx(h), dFdy(h)), faceDirection);
}`;
const FACE_FS = `
if (vFace.z > 0.01 && abs(vFace.x * fComp.x) < 0.985 && abs(vFace.y * fComp.y) < 0.985) {
  vec2 fq = vFace.xy * fComp.xy; vec2 cuv = fq * 0.5 + 0.5;
  vec4 mA = texture2D(fCol, fCell(fCells.y, cuv)), mB = texture2D(fCol, fCell(fCells.w, cuv)), mo = mix(mA, mB, fMix.x) * fMix.z * (1.0 - sCoatM);
  vec3 c = mix(diffuseColor.rgb, mo.rgb, mo.a);
  // the nostrils: two small soft dots on the top front of the snout, the skin a shade darker
  float nz = 0.0; for (int i = 0; i < 2; i++) { float sd = i == 0 ? -1.0 : 1.0; vec2 d = (fq - vec2(sd * 0.17, -0.06)) * vec2(1.0, 1.35); nz = max(nz, 1.0 - smoothstep(0.028, 0.05, length(d))); }
  c = mix(c, c * vec3(0.72, 0.5, 0.58), nz * (1.0 - sCoatM));
  faceInk = mo.a * vFace.z; diffuseColor.rgb = mix(diffuseColor.rgb, c, vFace.z);
}`;
// the goo's gloss, the face kept crisp, a rim of light along the body's edge, warmth glowing through the thin frills
const LIT_FS = `
{ float belly = vJelly.x * (1.0 - vJelly.w), thin = vJelly.z, web = vXtra.y;
  // regions respond to light differently: the belly a wet satin sheen, the back, the face and the limbs nearly matte, the frills a touch drier;
  // the paint coat is wet and glossy wherever it covers
  float satin = max(belly, 0.6 * web);
  float base = mix(0.8, 0.42, satin); base = mix(base, 0.6, thin * 0.4 * (1.0 - web)) + 0.05 * sRed;
  float wet = max(sCoatM, 0.45 * uCoat.z);
  material.roughness = min(max(mix(base, 0.16, wet), 0.0525) + geometryRoughness, 1.0);
#ifdef USE_CLEARCOAT
  material.clearcoat = mix(0.12 + 0.4 * satin, 1.0, sCoatM) * (1.0 - 0.8 * faceInk);
  material.clearcoatRoughness = min(max(mix(0.5 - 0.3 * satin, 0.07, sCoatM), 0.0525) + geometryRoughness, 1.0);
#endif
}`;
const LOOK_FS = `
{ float ink = faceInk * (1.0 - sCoatM), occ = vXtra.x * (1.0 - 0.3 * sCoatM);
  // baked cavity occlusion: creases, armpits, under the chin, between the toes, the gill roots
  reflectedLight.indirectDiffuse *= 1.0 - 0.9 * occ; reflectedLight.directDiffuse *= 1.0 - 0.5 * occ; reflectedLight.indirectSpecular *= 1.0 - 0.9 * occ; reflectedLight.directSpecular *= 1.0 - 0.6 * occ;
#ifdef USE_CLEARCOAT
  clearcoatSpecularIndirect *= 1.0 - 0.9 * occ; clearcoatSpecularDirect *= 1.0 - 0.6 * occ;
#endif
  reflectedLight.directDiffuse *= 1.0 - 0.5 * ink; reflectedLight.indirectDiffuse *= 1.0 - 0.5 * ink; reflectedLight.directSpecular *= 1.0 - 0.85 * ink; reflectedLight.indirectSpecular *= 1.0 - 0.85 * ink;
  totalEmissiveRadiance += diffuseColor.rgb * ink * 0.55;
  vec3 vd = normalize(vViewPosition), upV = normalize((viewMatrix * vec4(0.0, 1.0, 0.0, 0.0)).xyz), kd = normalize(uKeyDir);
  float edge = 1.0 - saturate(dot(nonPerturbedNormal, vd));
  float rim = pow(edge, 3.0) * (0.5 + 0.5 * saturate(dot(nonPerturbedNormal, upV) + 0.4)) * (1.0 - faceInk) * (1.0 - 0.5 * sCoatM);
  totalEmissiveRadiance += mix(diffuseColor.rgb, vec3(1.0, 0.95, 0.9), 0.4) * rim * 0.3;
  // thin parts: the key light shining through from behind, in the skin's own deeper colour; a soft wrap of warmth on the frills
  float thin = vJelly.z * (1.0 - sCoatM), tr = pow(saturate(dot(vd, -normalize(kd + nonPerturbedNormal * 0.4))), 3.0), wrap = saturate((dot(nonPerturbedNormal, kd) + 0.6) / 1.6);
  vec3 deep = pow(max(diffuseColor.rgb, vec3(0.0)), vec3(1.5)) * 1.6; thin = max(thin, 0.8 * vXtra.y) * (1.0 + 0.4 * sRed);
  totalEmissiveRadiance += deep * thin * (0.6 * tr + 0.14 * wrap) + diffuseColor.rgb * 0.04 * edge * edge * (1.0 - faceInk);
}`;

// debug views (the material breakdown sheet): 1 roughness, 2 the detail normal lit by one light, 3 occlusion, 4 regions (belly / head / thin / web)
const DEBUG_FS = `
if (uDebug > 0.5) {
  if (uDebug < 1.5) gl_FragColor = vec4(vec3(material.roughness), 1.0);
  else if (uDebug < 2.5) { float l = 0.15 + 0.85 * max(0.0, dot(normal, normalize(vec3(0.4, 0.7, 0.6)))); gl_FragColor = vec4(vec3(l), 1.0); }
  else if (uDebug < 3.5) gl_FragColor = vec4(vec3(1.0 - vXtra.x), 1.0);
  else gl_FragColor = vec4(vJelly.x, vJelly.w, max(vJelly.z, vXtra.y), 1.0);
}`;
// ---------------- the material and its per-character state ----------------
export class Look {
  constructor(opts = {}) {
    const sh = faceSheets(opts.faceCell || 256);
    this.U = {
      uTeam: { value: new THREE.Color(opts.color || 0xff6b8a) }, uPaint: { value: new THREE.Color(opts.color || 0xff6b8a) }, uCoat: { value: new THREE.Vector4(0, Math.random() * 40, 0, 0) }, uCoatMix: { value: 1 },
      uJelly: { value: new THREE.Vector4(0, 0, 1.6, 0) }, uLag: { value: new THREE.Vector4(0, 0, 0, 0) }, uFace: { value: new THREE.Vector4(FACE.sheet.yaw, FACE.sheet.height, FACE.sheet.centre, 1) }, uHead: { value: new THREE.Vector4(0, 1.37, 0.64, 0.38) },
      fCol: { value: sh.col }, fMsk: { value: sh.msk }, fCells: { value: new THREE.Vector4(0, 8, 0, 8) }, fMix: { value: new THREE.Vector4(0, 0, 1, 6) }, fPupil: { value: new THREE.Vector4(0, -0.03, 1, 0) }, fComp: { value: new THREE.Vector4(1, 1, 0, 0) },
      fIris: { value: new THREE.Vector3(0.16, 0.06, 0.035) }, fStyle: { value: 0 }, uKeyDir: { value: new THREE.Vector3(0.3, 0.6, 0.7) },
      uDebug: { value: 0 }, uBump: { value: bumpTexture() }, uBumpK: { value: new THREE.Vector4(0.035, 7.0, 0.006, 0) },   // skin detail: amplitude, tiles per metre, groove / filament amplitude
    };
    this.fangs = false; this.expr = 'neutral'; this.exprB = 'neutral'; this.exprK = 1; this.blinkT = 1 + Math.random() * 2; this.blinkK = 0; this.look = [0, 0]; this.lookT = [0, 0];
    this.att = { t: 1 + Math.random() * 2, eye: [0, 0] }; this.t = 0;
  }
  setColor(c) { this.U.uTeam.value.set(c); this.U.uPaint.value.set(c); return this; }
  setPaint(level) { this.U.uCoat.value.x = level; return this; }
  setFangs(on) { this.fangs = !!on; return this; }
  setEyeStyle(k) { this.U.fStyle.value = k; return this; }
  setExpression(name) { if (!(name in EXPR)) name = 'neutral'; if (name === this.exprB) return this; if (this.exprK < 1) this.expr = this.exprK > 0.5 ? this.exprB : this.expr; this.exprB = name; this.exprK = 0; return this; }
  blink() { this.blinkK = 0.13; }
  // 3D eyes on a mesh's head bone (place: eye centre offsets in head radii, from the head centre)
  attachEyes(EyeRigClass, meshRec) { this.rigs = this.rigs || {}; this.rigs[meshRec.meta.name || Object.keys(this.rigs).length] = new EyeRigClass(this, meshRec); return this; }
  setFade(which, fade) { this.fades = this.fades || {}; this.fades[which] = fade; }
  // per frame: expression crossfade, blinks, pupils drifting toward the look target (x right, y up, in face units), head squash compensation
  update(dt, look, squash = 0) {
    this.t += dt;
    if (this.exprK < 1) { this.exprK = Math.min(1, this.exprK + dt / 0.12); if (this.exprK >= 1) this.expr = this.exprB; }
    this.blinkT -= dt; if (this.blinkT <= 0) { this.blinkK = 0.13; this.blinkT = Math.random() < 0.22 ? 0.26 : 1.6 + Math.random() * 3.4; } if (this.blinkK > 0) this.blinkK -= dt;
    const A = this.att; A.t -= dt; if (A.t <= 0) { A.t = 1.2 + Math.random() * 2.8; A.eye[0] = (Math.random() * 2 - 1) * 0.12; A.eye[1] = (Math.random() * 2 - 1) * 0.05; }
    const lx = (look ? look[0] : 0) + A.eye[0], ly = (look ? look[1] : 0) + A.eye[1];
    this.look[0] += (lx - this.look[0]) * Math.min(1, dt * 26); this.look[1] += (ly - this.look[1]) * Math.min(1, dt * 26);
    const NO_SHUT = { glee: 1, hurt: 1, yawn: 1, dizzy: 1, brace: 1 }; const shut = this.blinkK > 0 && !NO_SHUT[this.exprB];
    const pa = pupilOf(this.expr), pb = pupilOf(this.exprB), k = this.exprK, fang = this.fangs ? 6 : 0, ea = EXPR[this.expr], eb = EXPR[this.exprB];
    this.U.fCells.value.set(ea[0], ea[1] + fang, eb[0], eb[1] + fang); this.U.fMix.value.set(k, shut ? 1 : 0, 1, 6);
    this.U.fPupil.value.set(this.look[0], this.look[1], pa.pu + (pb.pu - pa.pu) * k, pa.py + (pb.py - pa.py) * k);
    this.U.fComp.value.set(1, 1 - 0.3 * squash, 0, 0); this.U.uLag.value.w = this.t;
    if (this.rigs) for (const w in this.rigs) this.rigs[w].update(this.expr, this.exprB, k, this.blinkK, this.look, this.U.fStyle.value, this.U.uTeam.value, this.fades && this.fades[w] !== undefined ? this.fades[w] : 1);
    if (this.coatMixT !== undefined) this.U.uCoatMix.value += (this.coatMixT - this.U.uCoatMix.value) * Math.min(1, dt * 3);   // the coat's fill order glides between the crawl's and the stand's
  }
}
// the body material for one mesh of one character (the look's uniforms are shared by the character's two meshes)
export function axoMaterial(tex, look, meta) {
  const mat = new THREE.MeshPhysicalMaterial({ map: tex, roughness: 0.7, metalness: 0, clearcoat: 0.3, clearcoatRoughness: 0.3, envMapIntensity: 1.0 });
  mat.onBeforeCompile = sh => {
    Object.assign(sh.uniforms, look.U);
    sh.vertexShader = VERT_PARS + '\n' + sh.vertexShader.replace('#include <skinning_vertex>', '#include <skinning_vertex>\n' + VERT_MAIN);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\n' + FRAG_PARS)
      .replace('#include <map_fragment>', MAP_FS).replace('#include <color_fragment>', '#include <color_fragment>\n' + FACE_FS)
      .replace('#include <normal_fragment_maps>', '#include <normal_fragment_maps>\n' + BUMP_FS)
      .replace('#include <lights_physical_fragment>', '#include <lights_physical_fragment>\n' + LIT_FS)
      .replace('#include <aomap_fragment>', '#include <aomap_fragment>\n' + LOOK_FS)
      .replace('#include <colorspace_fragment>', '#include <colorspace_fragment>\n' + DEBUG_FS);
    // this mesh's own head frame (rest space): centre and radius from the meta
    sh.uniforms.uHead = { value: new THREE.Vector4(...meta.headAbs, meta.headr) }; sh.uniforms.uHeadF = { value: new THREE.Vector2(meta.headMid, meta.headH) };
    sh.uniforms.uAlong = { value: new THREE.Vector3(...(meta.bbox[1][1] > 1.2 ? [0, 1, 0] : [0, 0, 1])) };   // the body's long axis in rest space (the standing mesh is upright)
  };
  mat.customProgramCacheKey = () => 'axo-body';
  return mat;
}
