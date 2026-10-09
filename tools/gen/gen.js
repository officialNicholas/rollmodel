// ---------- the world generator ----------
// Every match is played on a new canvas, laid out the way a level designer would do it:
//  1) Pick a symmetry so neither side gets the better half (point or mirror symmetry most of the time, otherwise free-form and
//     balanced while placing items), and a centerpiece that gives the map its character: raised plaza, central pit, spire, canopy or open floor.
//  2) Fill in features from a kit whose sizes are all proven against the physics: lips you can hop, ramps you can climb, decks you
//     can stand under, gaps a blob always fits through. Every feature keeps open floor all around it, so the ground can never be cut in two.
//  3) Build the navigation graph on the result and keep the part a blob can really get around.
//  4) Score every reachable spot and put things where they make sense: spawns in open ground far apart, coffins spread out so a refill
//     or shelter is never far (tucked against walls, a couple up high), boiling water pooled at the foot of walls and along busy lanes
//     but never choking a corridor, rollers up on high ground and risky ledges.
const GEN = { seed: 0, sym: '', arch: '', tries: 0, ms: 0, fallback: false, n: 0 };
const GAP = 2.6, RIM = 2.2;
const rectHit = (a, b, m) => a[0] - m < b[1] && a[1] + m > b[0] && a[2] - m < b[3] && a[3] + m > b[2];
const rectGap = (a, b) => Math.hypot(Math.max(0, a[0] - b[1], b[0] - a[1]), Math.max(0, a[2] - b[3], b[2] - a[3]));
function genLayout(seed) {
  const R = rng(seed), rr = (a, b) => a + (b - a) * R(), ri = (a, b) => Math.floor(rr(a, b + 0.999)), pick = a => a[Math.floor(R() * a.length)];
  const q = v => Math.round(v * 20) / 20, shuffle = a => { for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
  const sym = pick(['rot', 'rot', 'rot', 'mirror', 'mirror', 'free']);
  // the symmetry acting on rects and ramps (free-form maps still use the point symmetry for their centerpiece)
  const imgR = r => sym === 'mirror' ? [r[0], r[1], -r[3], -r[2]] : [-r[1], -r[0], -r[3], -r[2]];
  const imgRamp = r => { const m = imgR(r); return sym !== 'mirror' || r[4] === 'z' ? [...m, r[4], r[6], r[5]] : [...m, r[4], r[5], r[6]]; };
  const placed = [], comp = () => ({ boxes: [], ramps: [], holes: [], foot: [], self: false });
  const fp = (c, r, k, y0, y1) => c.foot.push({ r: r.slice(0, 4), k, y0: y0 || 0, y1: y1 || 0 });
  const B = (x0, x1, z0, z1, y0, y1) => [q(x0), q(x1), q(z0), q(z1), y0, y1];
  // footprints: g = solid on the floor, h = hole, a = floating, z = landing zone at the foot of a ramp that has to stay open floor
  function clash(a, b) {
    if (a.k === 'z' && b.k === 'z') return false;
    if (a.k === 'z' || b.k === 'z') { const o = a.k === 'z' ? b : a; return o.k === 'a' && o.y0 > 2 ? false : rectHit(a.r, b.r, 0.3); }
    if (a.k === 'a' || b.k === 'a') { const A = a.k === 'a' ? a : b, O = A === a ? b : a; if (O.k === 'h') return false; return rectHit(a.r, b.r, O.k === 'a' ? 1.8 : 1.0); }
    return rectHit(a.r, b.r, GAP);
  }
  const inBounds = e => { const L = e.k === 'z' ? ARENA - 0.8 : e.k === 'a' ? ARENA - 1.4 : ARENA - RIM; return e.r[0] >= -L && e.r[1] <= L && e.r[2] >= -L && e.r[3] <= L; };
  const fits = (c, others) => c.foot.every(e => inBounds(e) && others.every(o => o.foot.every(f => !clash(e, f))));
  const imageOf = c => ({ boxes: c.boxes.map(b => [...imgR(b), b[4], b[5]]), ramps: c.ramps.map(imgRamp), holes: c.holes.map(imgR), foot: c.foot.map(e => ({ r: imgR(e.r), k: e.k, y0: e.y0, y1: e.y1 })), self: false });
  function place(c) {
    if (!c || !fits(c, placed)) return false;
    if (sym !== 'free' && !c.self) { const m = imageOf(c); if (!fits(m, placed) || !fits(m, [c])) return false; placed.push(c, m); }
    else placed.push(c);
    return true;
  }
  // a ramp from the floor up to the top of box b along one of its sides (at = where along the side, 0..1)
  function ramp(c, b, side, slope, w, at) {
    const top = b[5], L = q(top / slope), alongX = side === '-z' || side === '+z', lo = alongX ? b[0] : b[2], hi = alongX ? b[1] : b[3];
    w = Math.min(w, hi - lo); const m = lo + w / 2 + (hi - lo - w) * (at === undefined ? R() : at), Z = 2.6, e = 0.5;
    let r, z;
    if (side === '+x') { r = [b[1], b[1] + L, m - w / 2, m + w / 2, 'x', top, 0]; z = [r[1], r[1] + Z, r[2] - e, r[3] + e]; }
    else if (side === '-x') { r = [b[0] - L, b[0], m - w / 2, m + w / 2, 'x', 0, top]; z = [r[0] - Z, r[0], r[2] - e, r[3] + e]; }
    else if (side === '+z') { r = [m - w / 2, m + w / 2, b[3], b[3] + L, 'z', top, 0]; z = [r[0] - e, r[1] + e, r[3], r[3] + Z]; }
    else { r = [m - w / 2, m + w / 2, b[2] - L, b[2], 'z', 0, top]; z = [r[0] - e, r[1] + e, r[2] - Z, r[2]]; }
    for (let i = 0; i < 4; i++) r[i] = q(r[i]);
    c.ramps.push(r); fp(c, r, 'g', 0, top); fp(c, z, 'z');
    return r;
  }
  // the matching ramp on the far side of a centerpiece
  function twinRamp(c, r) { const m = imgRamp(r); if (rectHit(m, r, 0.5)) return; c.ramps.push(m); const f = c.foot.slice(-2); for (const e of f) fp(c, imgR(e.r), e.k, e.y0, e.y1); }
  const SIDES = ['-x', '+x', '-z', '+z'];
  const kit = {
    plateau(cx, cz) { const w = rr(5, 9), d = rr(4.4, 7.2), h = q(rr(1.2, 1.6)), c = comp(), b = B(cx - w / 2, cx + w / 2, cz - d / 2, cz + d / 2, 0, h); c.boxes.push(b); fp(c, b, 'g', 0, h); const s = shuffle(SIDES.slice()); ramp(c, b, s[0], 0.4, rr(2.2, 3)); if (R() < 0.5) ramp(c, b, s[1], 0.4, rr(2.2, 3)); return c; },
    tower(cx, cz) { const w = rr(3.3, 5), d = rr(3.3, 5), h = q(rr(1.9, 2.6)), c = comp(), b = B(cx - w / 2, cx + w / 2, cz - d / 2, cz + d / 2, 0, h); c.boxes.push(b); fp(c, b, 'g', 0, h); if (R() < 0.55) ramp(c, b, pick(SIDES), 0.55, rr(2.2, 2.8)); return c; },
    block(cx, cz) { const w = rr(2.2, 4.4), d = rr(2.2, 4.4), h = q(rr(0.8, 1.0)), c = comp(), b = B(cx - w / 2, cx + w / 2, cz - d / 2, cz + d / 2, 0, h); c.boxes.push(b); fp(c, b, 'g', 0, h); return c; },
    wall(cx, cz) { const L = rr(3.3, 6.6), t = rr(0.9, 1.1), h = q(rr(0.85, 0.95)), c = comp(), b = R() < 0.5 ? B(cx - L / 2, cx + L / 2, cz - t / 2, cz + t / 2, 0, h) : B(cx - t / 2, cx + t / 2, cz - L / 2, cz + L / 2, 0, h); c.boxes.push(b); fp(c, b, 'g', 0, h); return c; },
    deck(cx, cz) { const w = rr(5.5, 9), d = rr(4.4, 6.6), y0 = q(rr(2.3, 2.6)), c = comp(), b = B(cx - w / 2, cx + w / 2, cz - d / 2, cz + d / 2, y0, q(y0 + 0.4)); c.boxes.push(b); fp(c, b, 'a', b[4], b[5]); const s = shuffle(SIDES.slice()); ramp(c, b, s[0], 0.62, rr(2.4, 3)); if (R() < 0.25) ramp(c, b, s[1], 0.62, rr(2.4, 3)); return c; },
    pad(cx, cz) { const w = rr(3.3, 5), d = rr(3.3, 5), y0 = q(rr(0.92, 1.0)), c = comp(), b = B(cx - w / 2, cx + w / 2, cz - d / 2, cz + d / 2, y0, q(y0 + 0.3)); c.boxes.push(b); fp(c, b, 'a', b[4], b[5]); return c; },
    pit(cx, cz) { const w = rr(3.3, 7), d = rr(3.3, 6), c = comp(), h = B(cx - w / 2, cx + w / 2, cz - d / 2, cz + d / 2); c.holes.push(h.slice(0, 4)); fp(c, h, 'h'); return c; },
    island(cx, cz) { const w = rr(6, 7.7), d = rr(6, 7.7), g = rr(1.0, 1.35), y0 = q(rr(0.92, 1.0)), c = comp(), h = B(cx - w / 2, cx + w / 2, cz - d / 2, cz + d / 2); c.holes.push(h.slice(0, 4)); fp(c, h, 'h'); const b = B(cx - w / 2 + g, cx + w / 2 - g, cz - d / 2 + g, cz + d / 2 - g, y0, q(y0 + 0.3)); c.boxes.push(b); fp(c, b, 'a', b[4], b[5]); return c; },
  };
  // 1) the centerpiece
  const arch = pick(['plaza', 'plaza', 'pit', 'spire', 'canopy', 'open']);
  const mid = comp(); mid.self = true;
  const midSide = () => sym === 'mirror' ? pick(['-z', '+x']) : pick(['-z', '-x']), midAt = s => sym === 'mirror' && s === '+x' ? 0.5 : undefined;
  if (arch === 'plaza') { const w = rr(7.7, 11), d = rr(6.6, 8.8), h = q(rr(1.3, 1.5)), b = B(-w / 2, w / 2, -d / 2, d / 2, 0, h); mid.boxes.push(b); fp(mid, b, 'g', 0, h); const s = midSide(); twinRamp(mid, ramp(mid, b, s, 0.4, rr(2.4, 3.2), midAt(s))); }
  else if (arch === 'pit') { const w = rr(6.6, 8.8), d = rr(6.6, 8.8), h = B(-w / 2, w / 2, -d / 2, d / 2); mid.holes.push(h.slice(0, 4)); fp(mid, h, 'h'); if (R() < 0.6) { const g = rr(1.0, 1.35), y0 = q(rr(0.92, 1.0)), b = B(-w / 2 + g, w / 2 - g, -d / 2 + g, d / 2 - g, y0, q(y0 + 0.3)); mid.boxes.push(b); fp(mid, b, 'a', b[4], b[5]); } }
  else if (arch === 'spire') { const w = rr(3.6, 4.6), h = q(rr(2.3, 2.6)), b = B(-w / 2, w / 2, -w / 2, w / 2, 0, h); mid.boxes.push(b); fp(mid, b, 'g', 0, h); const s = midSide(); twinRamp(mid, ramp(mid, b, s, 0.55, rr(2.4, 2.8), midAt(s))); }
  else if (arch === 'canopy') { const w = rr(7.7, 9.9), d = rr(5.5, 7.7), y0 = q(rr(2.3, 2.6)), b = B(-w / 2, w / 2, -d / 2, d / 2, y0, q(y0 + 0.4)); mid.boxes.push(b); fp(mid, b, 'a', b[4], b[5]); const s = midSide(); twinRamp(mid, ramp(mid, b, s, 0.62, rr(2.4, 3), midAt(s))); }
  if (mid.foot.length && mid.foot.every(inBounds)) placed.push(mid);
  // 2) the kit pieces, big ones first so the small ones fill in around them
  const per = sym === 'free' ? 2 : 1, want = [];
  const add = (k, a, b) => { for (let n = ri(a, b) * per; n > 0; n--) want.push(k); };
  add('deck', 1, 2); add('tower', 1, 2); add('wall', 1, 2); add('pad', 1, 2); add('block', 0, 2); add('pit', 0, 2); add('island', 0, 1); add('plateau', arch === 'plaza' ? 0 : 1, 1);
  const order = ['deck', 'plateau', 'island', 'tower', 'pit', 'pad', 'block', 'wall'];
  want.sort((a, b) => order.indexOf(a) - order.indexOf(b));
  const spot = () => [rr(-ARENA + 3, ARENA - 3), sym === 'mirror' ? rr(-ARENA + 3, -1.5) : rr(-ARENA + 3, ARENA - 3)];
  for (const k of want) for (let t = 0; t < 60; t++) { const [cx, cz] = spot(); if (place(kit[k](cx, cz))) break; }
  // 3) top up with small pieces until the floor has a decent amount going on
  const area = () => placed.reduce((s, c) => s + c.foot.reduce((t, e) => t + (e.k === 'z' ? 0 : (e.r[1] - e.r[0]) * (e.r[3] - e.r[2])), 0), 0);
  const target = (2 * ARENA) * (2 * ARENA) * rr(0.17, 0.24);
  for (let t = 0; t < 120 && area() < target; t++) { const [cx, cz] = spot(); place(kit[pick(['block', 'wall', 'pad', 'pit', 'tower'])](cx, cz)); }
  // 4) clouds drift over open floor, preferably where nothing else casts shade
  const tall = [], shady = [];
  for (const c of placed) for (const e of c.foot) { if ((e.k === 'g' && e.y1 > 0.5) || (e.k === 'a' && e.y0 < 1.8)) tall.push(e.r); if ((e.k === 'g' && e.y1 > 1.7) || (e.k === 'a' && e.y0 > 1.8)) shady.push(e.r); }
  const clouds = [], nC = sym === 'free' ? ri(2, 4) : ri(1, 2), hw = 1.35;
  for (let i = 0; i < nC && clouds.length < MAX_MOVERS; i++) {
    let best = null, bs = -1;
    for (let t = 0; t < 30; t++) {
      const axis = R() < 0.5 ? 'x' : 'z', amp = q(rr(3.3, 5.5)), [x, z] = spot();
      const sw = axis === 'x' ? [x - amp - hw, x + amp + hw, z - hw, z + hw] : [x - hw, x + hw, z - amp - hw, z + amp + hw];
      if (sw[0] < -ARENA + 1.2 || sw[1] > ARENA - 1.2 || sw[2] < -ARENA + 1.2 || sw[3] > ARENA - 1.2) continue;
      if (tall.some(r => rectHit(r, sw, 0.5)) || clouds.some(o => rectHit(o.sw, sw, 1.5))) continue;
      if (sym !== 'free' && rectHit(sw, imgR(sw), 1.5)) continue;
      let d = 12; for (const r of shady) d = Math.min(d, rectGap(r, sw));
      const s = d + R() * 2; if (s > bs) { bs = s; best = { axis, amp, x, z, sw, period: q(rr(8, 12)), ph: rr(0, 6.28) }; }
    }
    if (!best) continue;
    clouds.push(best);
    if (sym !== 'free' && clouds.length < MAX_MOVERS) { const flip = sym === 'rot' || best.axis === 'z'; clouds.push({ axis: best.axis, amp: best.amp, x: sym === 'rot' ? -best.x : best.x, z: -best.z, sw: imgR(best.sw), period: best.period, ph: best.ph + (flip ? Math.PI : 0) }); }
  }
  const out = { sym, arch, boxes: [], ramps: [], holes: [], clouds };
  for (const c of placed) { out.boxes.push(...c.boxes); out.ramps.push(...c.ramps); out.holes.push(...c.holes); }
  return out;
}
function applyLayout(L) {
  HOLES.length = 0; BOXES.length = 0; RAMPS.length = 0;
  HOLES.push(...L.holes.map(h => h.slice())); BOXES.push(...L.boxes.map(b => b.slice())); RAMPS.push(...L.ramps.map(r => r.slice()));
  MOVERS.forEach((m, i) => { const c = L.clouds[i]; setMover(m, c ? { on: true, x: c.x, z: c.z, axis: c.axis, amp: c.amp, period: c.period, ph: c.ph } : { on: false }); });
}
// ---------- placing things where they make sense ----------
function navField(srcs) {
  const N = NN, d = new Float32Array(N).fill(Infinity), hi = [], hd = [];
  const push = (i, v) => { let k = hi.length; hi.push(i); hd.push(v); while (k > 0) { const p = (k - 1) >> 1; if (hd[p] <= hd[k]) break; [hi[p], hi[k]] = [hi[k], hi[p]]; [hd[p], hd[k]] = [hd[k], hd[p]]; k = p; } };
  const pop = () => { const i = hi[0], v = hd[0], li = hi.pop(), lv = hd.pop(); if (hi.length) { hi[0] = li; hd[0] = lv; let k = 0; for (;;) { const l = 2 * k + 1, r = l + 1; let m = k; if (l < hi.length && hd[l] < hd[m]) m = l; if (r < hi.length && hd[r] < hd[m]) m = r; if (m === k) break; [hi[m], hi[k]] = [hi[k], hi[m]]; [hd[m], hd[k]] = [hd[k], hd[m]]; k = m; } } return [i, v]; };
  for (const [i, v] of srcs) if (v < d[i]) { d[i] = v; push(i, v); }
  while (hi.length) { const [i, v] = pop(); if (v > d[i]) continue; const nb = NAV.nodes[i].nb; for (let e = 0; e < nb.length; e += 2) { const j = nb[e], nv = v + nb[e + 1]; if (nv < d[j]) { d[j] = nv; push(j, nv); } } }
  return d;
}
// the part of the graph you can get around in both directions
function navCore(R) {
  const nodes = NAV.nodes, N = nodes.length, rev = Array.from({ length: N }, () => []);
  for (const n of nodes) for (let e = 0; e < n.nb.length; e += 2) rev[n.nb[e]].push(n.id);
  const reach = (s, fwd) => { const seen = new Uint8Array(N), st = [s]; seen[s] = 1; while (st.length) { const i = st.pop(); if (fwd) { const nb = nodes[i].nb; for (let e = 0; e < nb.length; e += 2) if (!seen[nb[e]]) { seen[nb[e]] = 1; st.push(nb[e]); } } else for (const j of rev[i]) if (!seen[j]) { seen[j] = 1; st.push(j); } } return seen; };
  const ground = nodes.filter(n => n.h === 0 && n.edge === 0); let best = null, bn = 0;
  for (let t = 0; t < 6 && ground.length; t++) {
    const s = ground[Math.floor(R() * ground.length)].id; if (best && best[s]) continue;
    const f = reach(s, true), b = reach(s, false), m = new Uint8Array(N); let c = 0;
    for (let i = 0; i < N; i++) if (f[i] && b[i]) { m[i] = 1; c++; }
    if (c > bn) { bn = c; best = m; }
  }
  return { core: best || new Uint8Array(N), count: bn };
}
const onRampAt = (x, z, m) => RAMPS.some(r => inR(x, z, r, m || 0));
const overheadAt = (x, z, h, clear, m) => BOXES.some(b => b[4] > h + 0.05 && b[4] < h + clear && inR(x, z, b, m === undefined ? 0.5 : m));
const onFloater = (x, z, h) => BOXES.some(b => b[4] > 0 && Math.abs(b[5] - h) < 0.02 && inR(x, z, b));
function ringMask(x, z, h, rad, fn) { let m = 0; for (let k = 0; k < 8; k++) { const a = k / 8 * 6.2832; if (fn(x + Math.sin(a) * rad, z + Math.cos(a) * rad, h)) m |= 1 << k; } return m; }
const wallMask = (x, z, h, rad) => ringMask(x, z, h, rad, blockedAt);
const dropMask = (x, z, h, rad) => ringMask(x, z, h, rad, (px, pz, y) => { const s = surfaceUnder(px, pz, y + 0.3); return s === -Infinity || s < y - 0.2; });
const bits = m => { let c = 0; while (m) { c += m & 1; m >>= 1; } return c; };
const opposite = m => { for (let k = 0; k < 4; k++) if ((m >> k & 1) && (m >> (k + 4) & 1)) return true; return false; };
// coffin spots: level, roomy, not under anything, not on a floating deck (the coffin sinks into the ground when it's used up)
const cofOK = n => !onRampAt(n.x, n.z, 0.6) && n.edge === 0 && !onFloater(n.x, n.z, n.h) && !overheadAt(n.x, n.z, n.h, 3.2, 0.7) && dropMask(n.x, n.z, n.h, 1.1) === 0 && wallMask(n.x, n.z, n.h, 0.85) === 0;
const tuckOf = n => { const m = wallMask(n.x, n.z, n.h, 1.4) | dropMask(n.x, n.z, n.h, 1.5); const c = bits(m); return c === 0 ? 0 : opposite(m) ? 0.3 : c >= 2 ? 1.6 : 1; };
function placeItems(L, R) {
  const nodes = NAV.nodes, { core, count } = navCore(R);
  if (count < nodes.length * 0.7) return false;
  const inC = n => n && core[n.id], sym = L.sym;
  const imgXZ = (x, z) => sym === 'mirror' ? [x, -z] : [-x, -z];
  const imageNode = n => { const [x, z] = imgXZ(n.x, n.z), m = NAV.at(x, z, n.h); return m && Math.abs(m.h - n.h) < 0.05 && Math.hypot(m.x - x, m.z - z) < 0.2 ? m : null; };
  const dist2 = (a, b) => Math.hypot(a.x - b.x, a.z - b.z);
  // spawns: open ground well away from everything, as far apart as the map allows
  const openN = n => { let c = 0; NAV.near(n.x, n.z, 0, 3.2, m => { if (core[m.id] && m.edge === 0) c++; }); return c; };
  const spawnOK = n => inC(n) && n.h === 0 && n.edge === 0 && !BOXES.some(b => b[4] > 0 && inR(n.x, n.z, b, 1.2)) && !onRampAt(n.x, n.z, 1.6) && wallMask(n.x, n.z, 0, 1.6) === 0 && dropMask(n.x, n.z, 0, 1.8) === 0;
  let sP = null, sH = null, bs = -1;
  for (const n of nodes) { if (n.z > -12 || !spawnOK(n)) continue; const s = openN(n) + 0.25 * Math.min(-n.z, 22) + R() * 3; if (s > bs) { const im = sym === 'free' ? n : imageNode(n); if (im && spawnOK(im)) { bs = s; sP = n; sH = sym === 'free' ? null : im; } } }
  if (!sP) return false;
  const dP = navField([[sP.id, 0]]);
  if (sym === 'free') { bs = -1; for (const n of nodes) { if (n.z < 10 || !spawnOK(n) || !(dP[n.id] > 26)) continue; const s = openN(n) + 0.06 * dP[n.id] + R() * 3; if (s > bs) { bs = s; sH = n; } } }
  if (!sH) return false;
  const dH = navField([[sH.id, 0]]);
  Object.assign(START, { x: sP.x, z: sP.z, yaw: Math.atan2(-sP.x, -sP.z) }); Object.assign(CSTART, { x: sH.x, z: sH.z, yaw: Math.atan2(-sH.x, -sH.z) });
  const nearSpawn = (n, r) => dist2(n, sP) < r || dist2(n, sH) < r;
  // free-form maps alternate sides as they place things, so each spawn gets its share
  const sideOK = (n, k) => sym !== 'free' || (k % 2 === 0 ? dP[n.id] <= dH[n.id] : dH[n.id] < dP[n.id]);
  // greedy placement with symmetric twins
  function greedy(cands, want, score, minGap, list, onAdd) {
    for (let k = 0; list.length < want; k++) {
      let best = null, bv = -Infinity;
      for (const n of cands) { if (!sideOK(n, k) || list.some(p => dist2(p, n) < minGap)) continue; const v = score(n); if (v > bv) { bv = v; best = n; } }
      if (!best) { if (sym === 'free' && k < want * 3) continue; break; }
      list.push(best);
      if (sym !== 'free' && list.length < want) { const im = imageNode(best); if (im && dist2(im, best) > minGap && cands.includes(im)) list.push(im); }
      if (onAdd) onAdd();
      if (k > want * 4) break;
    }
    return list;
  }
  // coffins: spread so a refill is never far, filling the gaps the shade leaves, tucked against walls, a couple up high
  const cofC = nodes.filter(n => inC(n) && cofOK(n) && !nearSpawn(n, 3));
  const shadeD = navField(nodes.filter(n => n.shade && core[n.id]).map(n => [n.id, 0]));
  const cofs = []; let dC = navField([[sP.id, 3], [sH.id, 3]]);
  const tuckC = new Map(cofC.map(n => [n, tuckOf(n)]));
  greedy(cofC, VS_CFG.pots, n => { const el = n.h > 0 ? (cofs.filter(p => p.h > 0).length < 2 ? 2.5 : -2) : 0; return Math.min(dC[n.id], 18) + 0.35 * Math.min(shadeD[n.id], 12) + 1.4 * tuckC.get(n) + el + R() * 1.5; }, 5, cofs, () => { dC = navField([[sP.id, 3], [sH.id, 3], ...cofs.map(c => [c.id, 0])]); });
  if (cofs.length < 6) return false;
  // where the traffic goes: sample a lot of shortest routes and count who passes through
  const traffic = new Float32Array(NN), coreList = nodes.filter(n => core[n.id]);
  for (let t = 0; t < 14; t++) {
    const s = coreList[Math.floor(R() * coreList.length)]; nMult.fill(1, 0, NN); dijkstra(s.id);
    for (let u = 0; u < 30; u++) { let i = coreList[Math.floor(R() * coreList.length)].id, g = 0; while (i >= 0 && g++ < 400) { traffic[i]++; i = nPrev[i]; } }
  }
  let tmax = 1; for (let i = 0; i < NN; i++) tmax = Math.max(tmax, traffic[i]);
  // boiling water: pooled against walls and in corners, some along the busy lanes, never right where you spawn and never filling a corridor
  const pudC = nodes.filter(n => inC(n) && !onRampAt(n.x, n.z, 1.8) && n.edge === 0 && !overheadAt(n.x, n.z, n.h, 2.4, 0.9) && dropMask(n.x, n.z, n.h, 1.4) === 0 && wallMask(n.x, n.z, n.h, 1.05) === 0 && !opposite(wallMask(n.x, n.z, n.h, 2.3) | dropMask(n.x, n.z, n.h, 2.3)) && !nearSpawn(n, 6.5) && !cofs.some(c => dist2(c, n) < 3.2));
  const puds = [];
  greedy(pudC, VS_CFG.rivals, n => { const w = wallMask(n.x, n.z, n.h, 1.9), wb = bits(w), t = traffic[n.id] / tmax; let near = 12; for (const p of puds) near = Math.min(near, dist2(p, n)); return (wb ? (wb >= 2 ? 1.6 : 1.2) : 0) + Math.min(t, 0.6) * 1.8 + (n.h === 0 ? 0.4 : 0) + Math.min(near, 10) * 0.16 + R() * 1.2; }, 4.4, puds);
  if (puds.length < 8) return false;
  // rollers: up high, out on the jump-only pads and near ledges: worth the trip
  const pwC = nodes.filter(n => { if (onRampAt(n.x, n.z, 0.6) || overheadAt(n.x, n.z, n.h, 2.6, 0.7) || wallMask(n.x, n.z, n.h, 0.8) || nearSpawn(n, 7) || cofs.some(c => dist2(c, n) < 2.6) || puds.some(c => dist2(c, n) < 2.6)) return false; return inC(n) ? true : onFloater(n.x, n.z, n.h) && n.h < 1.6 && dropMask(n.x, n.z, n.h, 0.7) === 0; });
  const pws = [];
  greedy(pwC, 10, n => { let dc = 14; for (const c of cofs) dc = Math.min(dc, dist2(c, n)); let dp = 14; for (const p of pws) dp = Math.min(dp, dist2(p, n)); return (inC(n) && n.h > 0.5 ? 2.2 : 0) + (!inC(n) ? 2 : 0) + (n.edge > 0 ? 0.6 : 0) + 0.12 * dc + 0.2 * dp + R(); }, 5, pws);
  POTS.length = 0; RIVALS.length = 0; POWER_SPOTS.length = 0; COF_SPOTS.length = 0;
  for (const n of cofs) POTS.push([n.x, n.h, n.z]);
  for (const n of puds) RIVALS.push([n.x, n.h, n.z]);
  pws.forEach((n, i) => POWER_SPOTS.push([n.x, n.h, n.z, i < 4 ? 'roller' : undefined]));
  for (const n of cofC) COF_SPOTS.push([n.x, n.h, n.z, tuckC.get(n)]);
  return true;
}
// a whole new world: lay it out, check it, place everything, build the meshes
function genWorld(seed) {
  const t0 = performance.now(); GEN.n++;
  for (let t = 0; t < 5; t++) {
    const L = genLayout((seed + t * 7919) >>> 0);
    applyLayout(L); rebuildSamples(); buildNav();
    if (placeItems(L, rng(seed * 31 + t))) { Object.assign(GEN, { seed, sym: L.sym, arch: L.arch, tries: t + 1, fallback: false }); rebuildStage(); GEN.ms = performance.now() - t0; return; }
  }
  // never seen it happen, but just in case: the original hand-built stage
  applyLayout({ holes: CLASSIC.holes, boxes: CLASSIC.boxes, ramps: CLASSIC.ramps, clouds: CLASSIC.movers });
  rebuildSamples(); buildNav();
  POTS.length = 0; RIVALS.length = 0; POWER_SPOTS.length = 0; COF_SPOTS.length = 0;
  POTS.push(...CLASSIC.pots); RIVALS.push(...CLASSIC.rivals); POWER_SPOTS.push(...CLASSIC.powers); Object.assign(START, CLASSIC.start); Object.assign(CSTART, CLASSIC.cstart);
  const { core } = navCore(rng(seed)); for (const n of NAV.nodes) if (core[n.id] && cofOK(n)) COF_SPOTS.push([n.x, n.h, n.z, tuckOf(n)]);
  Object.assign(GEN, { seed, sym: 'classic', arch: 'classic', tries: 5, fallback: true }); rebuildStage(); GEN.ms = performance.now() - t0;
}
