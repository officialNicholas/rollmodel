// Pop detector, injected into the preview page (needs window.axo). Steps the animation at a fixed dt, CPU-skins every visible mesh each frame
// (world space, squash included) and flags single-frame discontinuities:
//   vel   per-vertex velocity spike: the vertex's second difference |p[t+1] - 2p[t] + p[t-1]| is large (> 5 mm/frame^2) AND an isolated
//         spike: > 4x the median of its own second differences over the 3 frames either side (a pop is a one-off, not a fast oscillation)
//   flip  triangle normal turns by more than 60 deg in one frame (non-degenerate triangles: both frames' areas > 15% of rest)
//   area  triangle area jumps by more than x1.8 (or below /1.8) in one frame (rest area > 2 mm^2)
//   inv   triangle turns inside out in one frame: its normal against the rest normal carried by its dominant bone changes sign
// Everything is reported per body region (the dominant bone of each vertex). Webs are their own region.
window.POP = (() => {
  const { S, C, A, P } = window.axo; const MS = { stand: S, crawl: C };
  const region = nm => {
    if (!nm) return 'body'; const s = nm.match(/\.([LR])(\.|$)/); const sd = s ? s[1] : '';
    if (nm.startsWith('gill')) return 'gills'; if (nm.startsWith('finger')) return 'fingers.' + sd; if (/^toe\d/.test(nm)) return 'toes.' + sd;
    if (nm.startsWith('tail')) return 'tail'; if (nm === 'head' || nm === 'headfront') return 'head'; if (nm === 'neck') return 'neck';
    if (/^(hand)/.test(nm)) return 'hand.' + sd; if (/^(foot|toes)/.test(nm)) return 'foot.' + sd;
    if (/^(upperarm|forearm|shoulder)/.test(nm)) return 'arm.' + sd; if (/^(thigh|shin)/.test(nm)) return 'leg.' + sd; return 'body';
  };
  const prep = {};
  for (const w in MS) {
    const M = MS[w], g = M.mesh.geometry, n = g.attributes.position.count, si = g.attributes.skinIndex.array, swa = g.attributes.skinWeight.array, xt = g.attributes.xtra ? g.attributes.xtra.array : null;
    const reg = new Array(n), dom = new Int32Array(n), W = new Float32Array(n * 4);
    for (let i = 0; i < n; i++) { let b = 0, bw = -1; let s = 0; for (let k = 0; k < 4; k++) { const ww = swa[i * 4 + k] / 255; W[i * 4 + k] = ww; s += ww; if (ww > bw) { bw = ww; b = si[i * 4 + k]; } } for (let k = 0; k < 4; k++) W[i * 4 + k] /= s || 1; dom[i] = b; reg[i] = xt && xt[i * 2 + 1] > 128 ? 'web' : region(M.names[b]); }
    const I = g.index.array, nt = I.length / 3, p0 = g.attributes.position.array, ra = new Float32Array(nt), rn = new Float32Array(nt * 3), treg = new Array(nt), tdom = new Int32Array(nt);
    for (let t = 0; t < nt; t++) { const a = I[t * 3], b = I[t * 3 + 1], c = I[t * 3 + 2]; const ux = p0[b * 3] - p0[a * 3], uy = p0[b * 3 + 1] - p0[a * 3 + 1], uz = p0[b * 3 + 2] - p0[a * 3 + 2], vx = p0[c * 3] - p0[a * 3], vy = p0[c * 3 + 1] - p0[a * 3 + 1], vz = p0[c * 3 + 2] - p0[a * 3 + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx, l = Math.hypot(nx, ny, nz); ra[t] = l / 2; rn[t * 3] = nx / (l || 1); rn[t * 3 + 1] = ny / (l || 1); rn[t * 3 + 2] = nz / (l || 1); treg[t] = reg[a]; tdom[t] = dom[a]; }
    prep[w] = { n, W, si, reg, dom, I, nt, ra, rn, treg, tdom, p0, hist: [], tn: [], ta: [], tinv: [] };
  }
  const H = 9;   // frames of history kept (second differences over a +-3 frame window)
  function skin(w, out) {
    const M = MS[w], R = prep[w], mesh = M.mesh; mesh.updateMatrixWorld(true); mesh.skeleton.update();
    const bm = mesh.skeleton.boneMatrices, bind = mesh.bindMatrix.elements, p0 = R.p0, n = R.n, si = R.si, W = R.W;
    for (let i = 0; i < n; i++) {
      const x0 = p0[i * 3], y0 = p0[i * 3 + 1], z0 = p0[i * 3 + 2];
      const x = bind[0] * x0 + bind[4] * y0 + bind[8] * z0 + bind[12], y = bind[1] * x0 + bind[5] * y0 + bind[9] * z0 + bind[13], z = bind[2] * x0 + bind[6] * y0 + bind[10] * z0 + bind[14];
      let ox = 0, oy = 0, oz = 0;
      for (let k = 0; k < 4; k++) { const ww = W[i * 4 + k]; if (ww <= 0) continue; const o = si[i * 4 + k] * 16;
        ox += ww * (bm[o] * x + bm[o + 4] * y + bm[o + 8] * z + bm[o + 12]); oy += ww * (bm[o + 1] * x + bm[o + 5] * y + bm[o + 9] * z + bm[o + 13]); oz += ww * (bm[o + 2] * x + bm[o + 6] * y + bm[o + 10] * z + bm[o + 14]); }
      out[i * 3] = ox; out[i * 3 + 1] = oy; out[i * 3 + 2] = oz;
    }
    return out;
  }
  // triangle normals / areas of a skinned frame, and the inside-out test against the rest normal carried by the dominant bone's rotation
  function tris(w, p) {
    const R = prep[w], I = R.I, nt = R.nt, nn = new Float32Array(nt * 3), ar = new Float32Array(nt), inv = new Uint8Array(nt), bm = MS[w].mesh.skeleton.boneMatrices, rn = R.rn;
    for (let t = 0; t < nt; t++) { const a = I[t * 3], b = I[t * 3 + 1], c = I[t * 3 + 2];
      const ux = p[b * 3] - p[a * 3], uy = p[b * 3 + 1] - p[a * 3 + 1], uz = p[b * 3 + 2] - p[a * 3 + 2], vx = p[c * 3] - p[a * 3], vy = p[c * 3 + 1] - p[a * 3 + 1], vz = p[c * 3 + 2] - p[a * 3 + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx, l = Math.hypot(nx, ny, nz); ar[t] = l / 2; nn[t * 3] = nx / (l || 1); nn[t * 3 + 1] = ny / (l || 1); nn[t * 3 + 2] = nz / (l || 1);
      // the expected normal: the rest normal carried by the blended (LBS) rotation of the triangle's vertices
      let rx = 0, ry = 0, rz = 0;
      for (const vi of [a, b, c]) for (let k = 0; k < 4; k++) { const ww = R.W[vi * 4 + k]; if (ww <= 0) continue; const o = R.si[vi * 4 + k] * 16;
        rx += ww * (bm[o] * rn[t * 3] + bm[o + 4] * rn[t * 3 + 1] + bm[o + 8] * rn[t * 3 + 2]); ry += ww * (bm[o + 1] * rn[t * 3] + bm[o + 5] * rn[t * 3 + 1] + bm[o + 9] * rn[t * 3 + 2]); rz += ww * (bm[o + 2] * rn[t * 3] + bm[o + 6] * rn[t * 3 + 1] + bm[o + 10] * rn[t * 3 + 2]); }
      const rl = Math.hypot(rx, ry, rz) || 1;
      inv[t] = (rx * nn[t * 3] + ry * nn[t * 3 + 1] + rz * nn[t * 3 + 2]) / rl < -0.2 ? 1 : 0; }
    return { nn, ar, inv };
  }
  let rec = null;
  function reset(label) {
    for (const w in prep) { prep[w].hist = []; prep[w].tn = []; prep[w].vis = []; }
    rec = { label, frame: 0, events: [], counts: {}, worst: {}, series: [], vworst: { stand: new Float32Array(prep.stand.n), crawl: new Float32Array(prep.crawl.n) } };
  }
  const bump = (kind, reg, val, f, w, idx) => {
    const k = kind + ':' + reg; rec.counts[k] = (rec.counts[k] || 0) + 1;
    if (!rec.worst[k] || val > rec.worst[k].v) rec.worst[k] = { v: +val.toFixed(4), f, mesh: w, i: idx, st: A.state };
    if (rec.events.length < 4000) rec.events.push([kind, reg, +val.toFixed(4), f, w, idx]);
  };
  // evaluate the middle frame of the history once enough frames are in (temporal window +-3)
  function evalMid(w) {
    const R = prep[w], h = R.hist; if (h.length < H) return; const m = 4, n = R.n;   // h[m] is the frame being judged
    const f = rec.frame - (H - 1 - m);
    // velocity spikes
    const acc = k => { const a = h[k - 1], b = h[k], c = h[k + 1]; return i => Math.hypot(c[i * 3] - 2 * b[i * 3] + a[i * 3], c[i * 3 + 1] - 2 * b[i * 3 + 1] + a[i * 3 + 1], c[i * 3 + 2] - 2 * b[i * 3 + 2] + a[i * 3 + 2]); };
    const fa = [1, 2, 3, 4, 5, 6, 7].map(acc), loc = new Float32Array(6);
    let maxA = {};
    for (let i = 0; i < n; i++) {
      const a = fa[3](i); if (a > (maxA[R.reg[i]] || 0)) maxA[R.reg[i]] = a;
      if (a < 0.005) continue;
      let j = 0; for (const k of [0, 1, 2, 4, 5, 6]) loc[j++] = fa[k](i); loc.sort(); const med = (loc[2] + loc[3]) / 2;
      if (a > 4 * (med + 0.0005)) { bump('vel', R.reg[i], a, f, w, i); if (a > rec.vworst[w][i]) rec.vworst[w][i] = a; }
    }
    // triangles: normal flips, area jumps, inside-out changes between frame m-1 and m
    const A0 = R.tn[m - 1], A1 = R.tn[m];
    for (let t = 0; t < R.nt; t++) {
      const ra = R.ra[t]; if (ra < 2e-7) continue;
      const a0 = A0.ar[t], a1 = A1.ar[t];
      if (a0 > 0.15 * ra && a1 > 0.15 * ra) { const d = A0.nn[t * 3] * A1.nn[t * 3] + A0.nn[t * 3 + 1] * A1.nn[t * 3 + 1] + A0.nn[t * 3 + 2] * A1.nn[t * 3 + 2]; if (d < 0.5) bump('flip', R.treg[t], Math.acos(Math.max(-1, Math.min(1, d))) * 57.3, f, w, t); }
      if (ra > 2e-6) { const r = (a1 + 1e-9) / (a0 + 1e-9); if (r > 1.8 || r < 1 / 1.8) bump('area', R.treg[t], r > 1 ? r : 1 / r, f, w, t); }
      if (A0.inv[t] !== A1.inv[t]) bump('inv', R.treg[t], 1, f, w, t);
    }
    rec.series.push([f, w, A.state, Object.fromEntries(Object.entries(maxA).map(([k, v]) => [k, +(v * 1000).toFixed(2)]))]);
  }
  // one step: advance the preview by dt, skin whichever meshes are drawn, judge the frame 4 behind
  function step(dt) {
    axo.step(dt, 1); rec.frame++;
    for (const w in MS) {
      const mesh = MS[w].mesh, R = prep[w]; const vis = mesh.visible && (mesh.material.opacity > 0.02 || !mesh.material.transparent);
      if (!vis) { R.hist = []; R.tn = []; continue; }   // a mesh that is not drawn breaks its history (it pops in / out by the swap, judged by the transition sheets)
      const p = skin(w, new Float32Array(R.n * 3)); R.hist.push(p); R.tn.push(tris(w, p)); if (R.hist.length > H) { R.hist.shift(); R.tn.shift(); }
      evalMid(w);
    }
  }
  function run(label, dt, n) { reset(label); for (let i = 0; i < n; i++) step(dt); return summary(); }
  function cont(n, dt = 1 / 60) { for (let i = 0; i < n; i++) step(dt); }
  function summary() {
    const tot = {}; for (const k in rec.counts) { const kind = k.split(':')[0]; tot[kind] = (tot[kind] || 0) + rec.counts[k]; }
    return { label: rec.label, frames: rec.frame, totals: tot, counts: rec.counts, worst: rec.worst };
  }
  return { run, reset, cont, summary, get rec() { return rec; }, prep, region };
})();
