// replay the sky clouds' layout (same seeded random) and see when the old straight drift carried any of the ring across the stage
const rng = a => () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const r = rng(42);
// the geometry build draws from r first: cloudGeo(n, 1) for [3,4,5,6,5]: each sphere uses 4 draws
for (const n of [3, 4, 5, 6, 5]) for (let i = 0; i < n; i++) { r(); r(); r(); r(); }
const clouds = [];
for (let i = 0; i < 18; i++) { const vi = (r() * 5) | 0, sc = 5 + r() * 4; clouds.push({ L: 0, x: -150 + r() * 300, y: -27 - r() * 10, z: -150 + r() * 300, ry: r() * 6.28, sc, v: 0.5 + r() * 0.6 }); }
for (let i = 0; i < 12; i++) { const vi = (r() * 4) | 0, a = r() * 6.283, d = 62 + r() * 70, sc = 3 + r() * 3; clouds.push({ L: 1, x: Math.cos(a) * d, y: -8 + r() * 26, z: Math.sin(a) * d, ry: r() * 6.28, sc, v: 0.9 + r() * 0.8 }); }
for (const c of clouds.filter(c => c.L === 1)) {
  // first time (seconds) its x passes within the stage's span while |z| is inside it too
  let t = null; if (Math.abs(c.z) < 26.4 + c.sc * 3) { let x = c.x, tt = 0; while (tt < 3600) { if (Math.abs(x) < 26.4 + c.sc * 3) { t = tt; break; } x += c.v; tt += 1; if (x > 160) x -= 320; } }
  console.log('ring cloud z', c.z.toFixed(1), 'y', c.y.toFixed(1), 'scale', c.sc.toFixed(1), 'v', c.v.toFixed(2), 'reaches the stage after', t === null ? 'never' : t + 's');
}
