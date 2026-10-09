import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
old = open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/old_splash.js').read()
assert s.count(old) == 1
new = r"""function splashObjects(cx, cy, cz, R, t) {
  const reach = R + 1.25, seen = new Set(), up = 0.7 + 0.75 * R;
  // splash one side of a piece: blobs spread along it around the nearest point and up the wall
  const side = (b, px, pz, nx, nz, dist, lo, hi, circ, ox, oz, rr) => {
    if (dist > reach) return;
    const k = 1 - Math.max(0, dist) / reach, n = Math.round((2 + R * 2.4) * k * (0.8 + 0.4 * Math.random())), wallTop = b[6] === 'g' ? b[5] - Math.max(b[1] - b[0], b[3] - b[2]) / 2 : b[5] - 0.08;
    const spread = Math.min(R * 1.7, 2.8);
    for (let i = 0; i < n; i++) {
      let sc = (0.42 + 0.5 * Math.random()) * (0.7 + 0.5 * k) * Math.min(2.2, 0.8 + R * 0.35); if (circ) sc = Math.min(sc, rr * 1.15);
      const along = (Math.random() - 0.5) * 2 * spread * (0.35 + 0.65 * Math.random());
      let x, z, fx = nx, fz = nz;
      if (circ) { const a = Math.atan2(nx, nz) + along / Math.max(0.3, rr); fx = Math.sin(a); fz = Math.cos(a); x = ox + fx * rr; z = oz + fz * rr; }
      else { const hs = Math.min(sc * 0.42, (hi - lo) / 2), u = clamp((nx ? pz : px) + along, lo + hs, hi - hs); x = nx ? px : u; z = nx ? u : pz; }
      const y = Math.min(wallTop - sc * 0.42, cy + 0.15 + Math.pow(Math.random(), 0.8) * up * (0.5 + 0.5 * k));
      if (y < cy + 0.1 || y < b[4] + 0.08) continue;
      putSplash(x, y, z, fx, fz, sc, t);
    }
  };
  for (let gx = cx - reach; gx <= cx + reach + QG_C; gx += QG_C) for (let gz = cz - reach; gz <= cz + reach + QG_C; gz += QG_C) for (const b of qcell(qgB, Math.min(gx, cx + reach), Math.min(gz, cz + reach))) {
    if (seen.has(b)) continue; seen.add(b);
    if (b[4] > 0.05 || b[5] < cy + 0.25) continue; // standing pieces with some wall above the splash
    if (b[6] === 'c') { const ox = (b[0] + b[1]) / 2, oz = (b[2] + b[3]) / 2, rr = (b[1] - b[0]) / 2, dx = cx - ox, dz = cz - oz, d = Math.hypot(dx, dz) || 1e-3; side(b, 0, 0, dx / d, dz / d, d - rr, 0, 0, true, ox, oz, rr); continue; }
    // every side of a block that faces the splash (two of them when it lands off a corner)
    const qz = clamp(cz, b[2], b[3]), qx = clamp(cx, b[0], b[1]);
    if (cx < b[0]) side(b, b[0], qz, -1, 0, Math.hypot(b[0] - cx, qz - cz), b[2], b[3]);
    if (cx > b[1]) side(b, b[1], qz, 1, 0, Math.hypot(cx - b[1], qz - cz), b[2], b[3]);
    if (cz < b[2]) side(b, qx, b[2], 0, -1, Math.hypot(qx - cx, b[2] - cz), b[0], b[1]);
    if (cz > b[3]) side(b, qx, b[3], 0, 1, Math.hypot(qx - cx, cz - b[3]), b[0], b[1]);
  }
}
"""
s = s.replace(old, new)
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
rep("const SPL_MAX = 700,", "const SPL_MAX = 1400,")
# lighter splash shape (it's drawn many times)
rep("const sh = new THREE.Shape(), n = 28;", "const sh = new THREE.Shape(), n = 20;")
rep("new THREE.CircleGeometry(w * 0.72, 10).translate(x, -0.32 - len, 0)", "new THREE.CircleGeometry(w * 0.72, 7).translate(x, -0.32 - len, 0)")
rep("parts.push(new THREE.CircleGeometry(r, 10).translate(x, y, 0));", "parts.push(new THREE.CircleGeometry(r, 7).translate(x, y, 0));")
open(F, 'w').write(s)
print('ok')
