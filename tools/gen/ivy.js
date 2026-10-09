// ---------- ivy: leaf cards cut from a painted atlas (four leaves, each with its own relief and waxy gloss), hung in strands off block
// edges and corners, wound up columns and heaped in planters. One merged mesh per stage; the leaves are alpha-cut, two-sided ----------
const dataTexOf = (rgba, S, srgb) => { const t = new THREE.DataTexture(rgba, S, S, THREE.RGBAFormat); t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping; t.generateMipmaps = true; t.minFilter = THREE.LinearMipmapLinearFilter; t.magFilter = THREE.LinearFilter; t.anisotropy = 4; if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.needsUpdate = true; return t; };
// a texture whose see-through parts keep the color of what's next to them (so the cut edge never fringes dark when it mips): color from one
// canvas painted solid, alpha from another
const cutTex = (colCv, maskCv) => { const S = colCv.width, c = colCv.getContext('2d').getImageData(0, 0, S, S).data, m = maskCv.getContext('2d').getImageData(0, 0, S, S).data, o = new Uint8Array(S * S * 4);
  for (let y = 0; y < S; y++) { const sr = y * S * 4, dr = (S - 1 - y) * S * 4; for (let x = 0; x < S * 4; x += 4) { o[dr + x] = c[sr + x]; o[dr + x + 1] = c[sr + x + 1]; o[dr + x + 2] = c[sr + x + 2]; o[dr + x + 3] = m[sr + x]; } }
  return dataTexOf(o, S, true); };
const IVY = (() => {
  let tex = null;
  const paint = () => {
    const S = 512, C = S / 2, mk = () => { const c = document.createElement('canvas'); c.width = c.height = S; return c; };
    const col = mk(), mask = mk(), hgt = mk(), rgh = mk(), g = col.getContext('2d'), mg = mask.getContext('2d'), hg = hgt.getContext('2d'), rg = rgh.getContext('2d'), R = rng(919);
    mg.fillStyle = '#000'; mg.fillRect(0, 0, S, S); hg.fillStyle = gray(0.3); hg.fillRect(0, 0, S, S); rg.fillStyle = gray(0.5); rg.fillRect(0, 0, S, S);
    // each cell: an English ivy leaf, five pointed lobes (the last one three), the stem at the bottom middle of the cell
    const shapes = [[[0, 0.47], [0.36, 0.2], [0.44, -0.14], 0.15, 0.3], [[0, 0.44], [0.4, 0.16], [0.4, -0.18], 0.17, 0.26], [[0, 0.46], [0.33, 0.24], [0.42, -0.1], 0.13, 0.32], [[0, 0.42], [0.43, 0.08], null, 0.2, 0.3]];
    const tones = [[46, 92, 40], [58, 112, 46], [72, 128, 50], [40, 84, 44]];
    shapes.forEach((sh, k) => {
      const ox = (k % 2) * C + C / 2, oy = (k >> 1) * C + C * 0.58, sc = C * 0.9, P = (x, y) => [ox + x * sc, oy - y * sc];
      const [tip, upper, lower, notch, base] = sh, pts = [];
      // outline: from the stem round the right side to the top and back down the left, notches between the lobes
      const right = [[0.06, -base * 0.55], lower ? [lower[0], lower[1]] : null, lower ? [lower[0] * 0.62, lower[1] * 0.25 + upper[1] * 0.25] : null, [upper[0], upper[1]], [notch * 0.95, (upper[1] + tip[1]) * 0.48], [tip[0], tip[1]]].filter(Boolean);
      const outline = right.concat(right.slice(0, -1).reverse().map(([x, y]) => [-x, y]));
      const path = ctx => { ctx.beginPath(); const s0 = P(0, -base * 0.4); ctx.moveTo(s0[0], s0[1]);
        for (let i = 0; i < outline.length; i++) { const [x, y] = outline[i], q = P(x, y), pv = i ? outline[i - 1] : [0, -base * 0.4], m = P((pv[0] + x) / 2 * 0.9, (pv[1] + y) / 2 * 0.9 + 0.02); ctx.quadraticCurveTo(m[0], m[1], q[0], q[1]); }
        const pv = outline[outline.length - 1], m = P(pv[0] * 0.45, pv[1] * 0.6 - 0.04); ctx.quadraticCurveTo(m[0], m[1], s0[0], s0[1]); ctx.closePath(); };
      // the mask, a hair grown so the cut edge isn't eaten by mips, and the color painted solid around the leaf too
      path(mg); mg.fillStyle = '#fff'; mg.fill(); mg.strokeStyle = '#fff'; mg.lineWidth = 1.5; mg.stroke();
      const t = tones[k]; g.fillStyle = rgbS(t[0] * 0.8, t[1] * 0.8, t[2] * 0.8); g.fillRect((k % 2) * C, (k >> 1) * C, C, C);
      g.save(); path(g); g.clip();
      const gr = g.createRadialGradient(ox, oy - sc * 0.08, sc * 0.05, ox, oy, sc * 0.55); gr.addColorStop(0, rgbS(t[0] * 1.25, t[1] * 1.2, t[2] * 1.15)); gr.addColorStop(1, rgbS(t[0] * 0.78, t[1] * 0.8, t[2] * 0.82)); g.fillStyle = gr; g.fillRect(ox - C / 2, oy - C * 0.6, C, C);
      for (let i = 0; i < 24; i++) blob(g, ox + (R() - 0.5) * sc * 0.8, oy - (R() - 0.3) * sc * 0.7, sc * (0.05 + R() * 0.12), rgbS(t[0] * (0.8 + R() * 0.4), t[1] * (0.8 + R() * 0.4), t[2] * (0.8 + R() * 0.3), 0.35));
      g.restore();
      // height: a gentle dome, the midrib and side veins pressed in; gloss: waxy, the veins a little duller
      hg.save(); path(hg); hg.clip(); const hr = hg.createRadialGradient(ox, oy - sc * 0.05, 0, ox, oy, sc * 0.5); hr.addColorStop(0, gray(0.78)); hr.addColorStop(1, gray(0.5)); hg.fillStyle = hr; hg.fillRect(ox - C / 2, oy - C * 0.6, C, C); hg.restore();
      rg.save(); path(rg); rg.clip(); rg.fillStyle = gray(0.34); rg.fillRect(ox - C / 2, oy - C * 0.6, C, C); rg.restore();
      const veins = [tip, upper, lower].filter(Boolean).flatMap(v => v === tip ? [v] : [v, [-v[0], v[1]]]), v0 = P(0, -base * 0.3);
      for (const [x, y] of veins) { const q = P(x * 0.86, y * 0.86), mq = P(x * 0.35, y * 0.5 - 0.05);
        for (const [ctx, st, lw] of [[g, 'rgba(196,224,150,0.55)', 2.2], [hg, gray(0.42), 3.2], [rg, gray(0.5), 3]]) { ctx.strokeStyle = st; ctx.lineWidth = lw * (x === 0 ? 1.25 : 1); ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(v0[0], v0[1]); ctx.quadraticCurveTo(mq[0], mq[1], q[0], q[1]); ctx.stroke(); } }
    });
    const map = cutTex(col, mask);
    return HI ? { map, normalMap: heightNormal(hgt, 2.2), roughnessMap: texOf(rgh, false) } : { map };
  };
  const get = () => tex || (tex = paint());
  // the leaves of a stage, gathered while it's built: [x, y, z, ux, uy, uz (stem to tip), nx, ny, nz (facing), size, cell, tint]
  const L = [];
  const v3 = new THREE.Vector3(), up = new THREE.Vector3(), nn = new THREE.Vector3(), sd = new THREE.Vector3(), tmpC = new THREE.Color();
  function build(tint) {
    if (!L.length) return null;
    const n = L.length, pos = new Float32Array(n * 36), nor = new Float32Array(n * 36), uv = new Float32Array(n * 24), colA = new Float32Array(n * 36); let o = 0;
    const base = new THREE.Color(tint || 0xFFFFFF);
    for (const q of L) {
      up.set(q[3], q[4], q[5]).normalize(); nn.set(q[6], q[7], q[8]); sd.crossVectors(up, nn).normalize(); nn.crossVectors(sd, up).normalize();
      const s = q[9], cu = (q[10] % 2) * 0.5, cv = 0.5 - (q[10] >> 1) * 0.5, x = q[0], y = q[1], z = q[2];
      // folded along the midrib: two halves, their outer edges set back behind the fold
      const corner = (a, b, f) => [x + up.x * a * s + sd.x * b * s - nn.x * f * s, y + up.y * a * s + sd.y * b * s - nn.y * f * s, z + up.z * a * s + sd.z * b * s - nn.z * f * s];
      const S0 = corner(-0.3, 0, 0), T0 = corner(0.7, 0, 0), L0 = corner(-0.3, -0.5, 0.16), L1 = corner(0.7, -0.5, 0.16), R0 = corner(-0.3, 0.5, 0.16), R1 = corner(0.7, 0.5, 0.16);
      const vs = [L0, S0, T0, L0, T0, L1, S0, R0, R1, S0, R1, T0], us = [[0, 0], [0.5, 0], [0.5, 1], [0, 0], [0.5, 1], [0, 1], [0.5, 0], [1, 0], [1, 1], [0.5, 0], [1, 1], [0.5, 1]];
      const nl = [nn.x - sd.x * 0.35, nn.y - sd.y * 0.35, nn.z - sd.z * 0.35], nr = [nn.x + sd.x * 0.35, nn.y + sd.y * 0.35, nn.z + sd.z * 0.35];
      tmpC.copy(base).multiplyScalar(q[11]);
      for (let k = 0; k < 12; k++) {
        const v = vs[k], nm = k < 6 ? nl : nr; pos[o * 3] = v[0]; pos[o * 3 + 1] = v[1]; pos[o * 3 + 2] = v[2]; nor[o * 3] = nm[0]; nor[o * 3 + 1] = nm[1]; nor[o * 3 + 2] = nm[2];
        uv[o * 2] = cu + us[k][0] * 0.5; uv[o * 2 + 1] = cv + us[k][1] * 0.5; colA[o * 3] = tmpC.r; colA[o * 3 + 1] = tmpC.g; colA[o * 3 + 2] = tmpC.b; o++;
      }
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos.subarray(0, o * 3), 3)); g.setAttribute('normal', new THREE.BufferAttribute(nor.subarray(0, o * 3), 3)); g.setAttribute('uv', new THREE.BufferAttribute(uv.subarray(0, o * 2), 2)); g.setAttribute('color', new THREE.BufferAttribute(colA.subarray(0, o * 3), 3));
    g.computeBoundingSphere(); return g;
  }
  let mat = null;
  const material = () => { if (mat) return mat; const t = get(); mat = toon(0xFFFFFF, { map: t.map, alphaTest: 0.5, side: THREE.DoubleSide, vertexColors: true, alphaToCoverage: true }, t.normalMap ? { normalMap: t.normalMap, normalScale: new THREE.Vector2(1, 1), roughnessMap: t.roughnessMap, roughness: 1, envMapIntensity: 1.1 } : null); return aoPatch(mat); };
  // ---- placing leaves ----
  const leaf = (x, y, z, ux, uy, uz, nx, ny, nz, s, R, dark) => L.push([x, y, z, ux, uy, uz, nx, ny, nz, s, (R() * 4) | 0, (0.72 + R() * 0.5) * (dark || 1)]);
  // a strand hanging from a top edge point: a few leaves spilling over the top, then down the face, swinging side to side
  function hang(x, top, z, fx, fz, len, R, k, o0) {
    k = k || 1; o0 = o0 || 0;
    for (let i = 0, n = 2 + (R() * 3 | 0); i < n; i++) { const a = R() * 6.2832, r = 0.04 + R() * 0.2, s = (0.13 + R() * 0.06) * k; leaf(x - fx * r * 0.9 + fz * (R() - 0.5) * 0.3, top + 0.025 + R() * 0.03, z - fz * r * 0.9 - fx * (R() - 0.5) * 0.3, Math.cos(a) * 0.9 + fx * 0.6, 0.15, Math.sin(a) * 0.9 + fz * 0.6, (R() - 0.5) * 0.4, 1, (R() - 0.5) * 0.4, s, R); }
    const ph = R() * 6.28, sw = 0.04 + R() * 0.05, tx = -fz, tz = fx; let side = R() < 0.5 ? 1 : -1;
    for (let t = 0.02; t < len; t += 0.065 + R() * 0.05) {
      const f = t / len, w = Math.sin(t * 6.5 + ph) * sw, out = 0.025 + R() * 0.035 + (1 - f) * 0.02 + o0 * Math.max(0, 1 - t / 0.22), px = x + fx * out + tx * w, pz = z + fz * out + tz * w, py = top - t, s = (0.12 + R() * 0.07) * (1 - f * 0.35) * k, a = (0.45 + R() * 0.6) * side;
      side = -side;
      // the leaf hangs from its stem: tip down and out to the side, its face turned out from the wall and up toward the sky
      leaf(px, py, pz, tx * Math.sin(a) + fx * 0.35, -Math.cos(a), tz * Math.sin(a) + fz * 0.35, fx + (R() - 0.5) * 0.5, 0.55 + R() * 0.4, fz + (R() - 0.5) * 0.5, s, R);
      if (R() < 0.18 && f < 0.7) hang(px - fx * out, py, pz - fz * out, fx, fz, (len - t) * (0.3 + R() * 0.4), R, k * 0.85);
    }
  }
  // two strands winding up a column from its foot
  function climb(cx, cz, rad, H, R) {
    for (let st = 0; st < 2; st++) { const a0 = R() * 6.28, turn = (1.1 + R() * 0.6) * (st ? -1 : 1), top = H * (0.45 + R() * 0.45);
      for (let y = 0.05; y < top; y += 0.06 + R() * 0.04) { const a = a0 + y * turn + Math.sin(y * 5 + a0) * 0.12, nx = Math.cos(a), nz = Math.sin(a), r = rad + 0.025 + R() * 0.03, s = (0.12 + R() * 0.07) * (1 - y / top * 0.3), b = (R() - 0.5) * 2.2;
        leaf(cx + nx * r, y, cz + nz * r, -nz * Math.sin(b) * 0.8, 0.6 + Math.cos(b) * 0.4, nx * Math.sin(b) * 0.8, nx * 0.9, 0.35 + R() * 0.3, nz * 0.9, s, R); } }
  }
  // a heaped bush (a planter's): leaves all over a low dome
  function bush(cx, y, cz, rx, ry, rz, n, R) {
    for (let i = 0; i < n; i++) { const a = R() * 6.2832, e = Math.acos(1 - R() * 0.95), nx = Math.sin(e) * Math.cos(a), ny = Math.cos(e), nz = Math.sin(e) * Math.sin(a), t = R() * 6.2832;
      leaf(cx + nx * rx, y + ny * ry, cz + nz * rz, Math.cos(t) * (1 - ny) + nx * 0.5, ny * 0.3 + 0.2, Math.sin(t) * (1 - ny) + nz * 0.5, nx, ny + 0.3, nz, 0.14 + R() * 0.08, R); }
  }
  return { L, get, build, material, hang, climb, bush, reset() { L.length = 0; } };
})();
