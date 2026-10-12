// ---- the Sludge Sewer's station: a hazard-yellow steel drum, a black band and a biohazard sticker, green drips down its side, on a steel
// pallet; a pipe comes up behind it with a red valve wheel and bends over the rim, an amber beacon on the bend, and the paint pours from it ----
const DRUM_SIGN_M = toon(0xFFFFFF, { map: SEWER_SIGNS, alphaTest: 0.5, side: THREE.DoubleSide }, { roughness: 0.5 });
const DRUM = (() => {
  const V2 = (x, y) => new THREE.Vector2(x, y), seg = HI ? 56 : 32, pl = [], led = [], R = rng(7310);
  const YE = hexC(0xE6A820), YD = hexC(0xB8861A), BK = hexC(0x1C1E1C), ST = hexC(0x4A524C), STD = hexC(0x2A302C), RD = hexC(0xC4302A), GR = hexC(0x7CD83A), IN = hexC(0x2C302C), PF = hexC(0x5A1426);
  // the pallet: a frame, slats across, yellow corner bumpers
  for (const [w, d, x, z] of [[1.3, 0.1, 0, -0.6], [1.3, 0.1, 0, 0.6], [0.1, 1.3, -0.6, 0], [0.1, 1.3, 0.6, 0]]) pl.push([(HI ? rbox(w, 0.08, d, 0.015) : new THREE.BoxGeometry(w, 0.08, d)).translate(x, 0.04, z), STD]);
  for (let k = -4; k <= 4; k++) pl.push([new THREE.BoxGeometry(1.18, 0.03, 0.07).translate(0, 0.065, k * 0.135), ST]);
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) pl.push([(HI ? rbox(0.14, 0.11, 0.14, 0.03) : new THREE.BoxGeometry(0.14, 0.11, 0.14)).translate(sx * 0.6, 0.055, sz * 0.6), YE]);
  // the drum: rolled hoops, a rolled rim, the inside dark, a black band with yellow chevrons, green drips running from the rim
  const prof = [[0.001, 0.08], [0.49, 0.08], [0.5, 0.09], [0.5, 0.28], [0.516, 0.295], [0.516, 0.315], [0.5, 0.33], [0.5, 0.5], [0.516, 0.515], [0.516, 0.535], [0.5, 0.55], [0.5, 0.7], [0.516, 0.712], [0.513, 0.73], [0.492, 0.735], [0.47, 0.726], [0.47, 0.14], [0.001, 0.14]];
  const drips = []; for (let k = 0; k < 5; k++) drips.push([R() * 6.2832, 0.08 + R() * 0.2, 0.05 + R() * 0.06]);
  pl.push([new THREE.LatheGeometry(prof.map(p => V2(p[0], p[1])), seg), (x, y, z, o, nx, ny) => { const r = Math.hypot(x, z), a = Math.atan2(z, x);
    if (r < 0.48) return o.copy(y < 0.145 ? PF : IN);
    for (const [da, L, w] of drips) { const d = Math.abs(Math.atan2(Math.sin(a - da), Math.cos(a - da))); if (d < w * (1 - Math.min(1, (0.73 - y) / L)) && y > 0.73 - L) return o.copy(GR); }
    if (y > 0.36 && y < 0.47) return o.copy(((a * 2.6 + y * 9) % 1 + 1) % 1 < 0.5 ? BK : YE);
    return o.copy((y > 0.28 && y < 0.34) || (y > 0.5 && y < 0.56) || y > 0.705 ? YD : YE); }]);
  // the pipe: up from the pallet behind the drum, a bend, along over the rim, a nozzle down; a flange, a valve wheel, a beacon
  const PZ = -0.62, PY = 1.06, NZ = -0.26, pr = 0.062;
  pl.push([new THREE.CylinderGeometry(pr, pr, PY - 0.08, HI ? 16 : 10).translate(0, (PY + 0.08) / 2 - 0.04, PZ), ST]);
  pl.push([new THREE.TorusGeometry(0.1, pr, HI ? 10 : 6, HI ? 12 : 8, Math.PI / 2).rotateY(Math.PI / 2).rotateX(0).translate(0, PY - 0.1, PZ + 0.1), ST]);
  pl.push([new THREE.CylinderGeometry(pr, pr, (NZ - PZ) - 0.1, HI ? 16 : 10).rotateX(Math.PI / 2).translate(0, PY, (PZ + 0.1 + NZ) / 2), ST]);
  pl.push([new THREE.CylinderGeometry(0.075, 0.06, 0.12, HI ? 16 : 10).translate(0, PY - 0.08, NZ + 0.02), STD]);
  for (const y of [0.3, 0.9]) pl.push([new THREE.CylinderGeometry(0.085, 0.085, 0.035, HI ? 16 : 10).translate(0, y, PZ), STD]);
  { const w = new THREE.TorusGeometry(0.11, 0.017, 6, 18).rotateY(Math.PI / 2).translate(0.13, 0.6, PZ); pl.push([w, RD]); for (let k = 0; k < 3; k++) pl.push([new THREE.BoxGeometry(0.012, 0.22, 0.016).rotateX(k * 1.0472).translate(0.13, 0.6, PZ), RD]); pl.push([new THREE.CylinderGeometry(0.025, 0.025, 0.1, 8).rotateZ(Math.PI / 2).translate(0.08, 0.6, PZ), STD]); }
  pl.push([new THREE.CylinderGeometry(0.07, 0.08, 0.04, 14).translate(0, PY + 0.08, PZ + 0.02), STD]); led.push(new THREE.SphereGeometry(0.06, 14, 8, 0, 6.2832, 0, Math.PI / 2).scale(1, 1.3, 1).translate(0, PY + 0.1, PZ + 0.02));
  const rc = new THREE.CatmullRomCurve3([[0, PY - 0.13, NZ + 0.02], [0, PY - 0.24, NZ + 0.021], [0, 0.62, NZ + 0.024], [0, 0.32, NZ + 0.026], [0, 0.15, NZ + 0.027]].map(q => new THREE.Vector3(q[0], q[1], q[2])), false, 'centripetal');
  const stream = streamGeo(rc, HI ? 30 : 16, HI ? 12 : 8, t => { const r = 0.046 - 0.012 * Math.min(1, t / 0.6); return [r, r]; }, t => Math.min(1, Math.max(0, (t - 0.08) / 0.15)));
  const tubHull = new THREE.CylinderGeometry(0.535, 0.535, 0.67, 32, 1, true).translate(0, 0.41, 0);
  const hull = mergeGeos([new THREE.BoxGeometry(1.36, 0.12, 1.36).translate(0, 0.05, 0), new THREE.CylinderGeometry(pr + 0.016, pr + 0.016, PY, 12, 1, true).translate(0, PY / 2, PZ)]);
  // the sticker: a strip of the sign atlas's biohazard, curved round the drum's face
  const st = gridGeo(8, 1, (u, v, o) => { const a = Math.PI / 2 - (u - 0.5) * 0.3; o.set(Math.cos(a) * 0.504, 0.565 + v * 0.13, Math.sin(a) * 0.504); }, true); atlasUV(st, 0, 2);
  return { pl: vcGeo(pl), led: mergeGeos(led), sticker: st, stream, src: [0, NZ + 0.027], tubHull, hull, lv0: 0.145, lvK: 0.54, yTop: 0.735, surf: new THREE.RingGeometry(0, 0.468, HI ? 56 : 28, HI ? 6 : 3).rotateX(-Math.PI / 2) };
})();
function makeDrum(x, y, z, seed) {
  const K = DRUM, p = stationBase(x, y, z, seed, 'drum'), { inner, tub } = p;
  const pm = new THREE.Mesh(K.pl, stGlossM); pm.castShadow = true; pm.receiveShadow = true; inner.add(pm); inner.add(new THREE.Mesh(K.led, stLedM)); inner.add(new THREE.Mesh(K.sticker, DRUM_SIGN_M));
  tub.add(new THREE.Mesh(K.tubHull, outlineMat)); inner.add(new THREE.Mesh(K.hull, outlineMat));
  const liq = new THREE.Mesh(K.surf, p.lm); liq.position.y = 0.3; tub.add(liq);
  const drips = new THREE.Mesh(rimDrips(seed, () => 0.506, K.yTop, 2, 0.06, 0.17), p.tm); drips.position.y = K.yTop; tub.add(drips);
  const spill = new THREE.Mesh(spillAt(seed, 0.9, 0.004, 0.22), p.tm); spill.renderOrder = 2; inner.add(spill);
  Object.assign(p, { liq, drips, spill, lv0: K.lv0, lvK: K.lvK, lift: 0.03, sinkD: 0.95, deb: DEB.drum });
  addPour(p, K.stream, K.src, seed); return p;
}
// ---- the Fishing Raft's station: an oak barrel, staves and iron hoops, on a round plank deck; an old iron hand pump behind it pours into it;
// a coil of rope, a fish and a float lie by its foot ----
const BARREL = (() => {
  const V2 = (x, y) => new THREE.Vector2(x, y), seg = HI ? 48 : 28, wood = [], iron = [], R = rng(7320), y0 = 0.06, TH = 0.62, NS = 16;
  const rOf = t => 0.43 + 0.07 * Math.sin(Math.PI * Math.min(1, Math.max(0, t))), WD = [0x9A6A40, 0xA87444, 0x8E5E36, 0xB07C4C].map(hexC), FE = hexC(0x34383A), PF = hexC(0x5A1426);
  // the deck: a round disc of planks
  wood.push([new THREE.CylinderGeometry(0.8, 0.82, y0, seg).translate(0, y0 / 2, 0), (x, y, z, o, nx, ny) => { const f = ((z + 2) / 0.17) % 1, i = Math.floor((z + 2) / 0.17); return o.copy(WD[i % 4]).multiplyScalar((f < 0.1 ? 0.55 : 0.92) * (ny > 0.5 ? 1 : 0.75)); }]);
  // the barrel: bellied staves, each its own tone, dark at the seams; the inside darker, the paint's floor red
  const prof = []; for (let k = 0; k <= 12; k++) { const t = k / 12; prof.push([rOf(t), y0 + t * TH]); } prof.push([rOf(1) - 0.012, y0 + TH + 0.006]); prof.push([rOf(1) - 0.04, y0 + TH]); for (let k = 12; k >= 1; k--) { const t = k / 12; prof.push([rOf(t) - 0.04, y0 + t * TH]); } prof.push([rOf(0.08) - 0.04, y0 + 0.06]); prof.push([0.001, y0 + 0.06]);
  wood.push([new THREE.LatheGeometry(prof.map(p => V2(p[0], p[1])), seg), (x, y, z, o) => { const r = Math.hypot(x, z), a = Math.atan2(z, x), f = ((a / 6.2832 * NS) % 1 + 1) % 1, i = Math.floor(((a / 6.2832 * NS) % NS + NS) % NS);
    if (r < rOf((y - y0) / TH) - 0.03) return o.copy(y < y0 + 0.065 ? PF : WD[2]).multiplyScalar(0.45); return o.copy(WD[(i * 3) % 4]).multiplyScalar((f < 0.05 || f > 0.95 ? 0.6 : 0.95 + 0.1 * Math.sin(i * 2.3)) * (0.75 + 0.25 * Math.min(1, (y - y0) / 0.15))); }]);
  for (const t of [0.1, 0.36, 0.64, 0.9]) iron.push([new THREE.TorusGeometry(rOf(t) + 0.006, 0.013, 5, seg).rotateX(Math.PI / 2).translate(0, y0 + t * TH, 0), FE]);
  // the pump: a plate, a fluted column, a cap, a spout out over the rim, a handle cocked back
  const PZ = -0.66, top = 0.98, IR = hexC(0x2E3A34), BR = hexC(0xC89A4A);
  iron.push([new THREE.CylinderGeometry(0.13, 0.14, 0.04, 14).translate(0, y0 + 0.02, PZ), IR]); iron.push([new THREE.CylinderGeometry(0.07, 0.085, top - y0, 12).translate(0, (top + y0) / 2, PZ), IR]);
  iron.push([new THREE.CylinderGeometry(0.095, 0.08, 0.08, 12).translate(0, top, PZ), IR]); iron.push([new THREE.SphereGeometry(0.06, 12, 8).translate(0, top + 0.07, PZ), BR]);
  iron.push([tubeBetween(new THREE.Vector3(0, top - 0.1, PZ + 0.05), new THREE.Vector3(0, top - 0.16, -0.32), 0.04, 0.034, 10), IR]); iron.push([new THREE.TorusGeometry(0.036, 0.008, 5, 12).translate(0, top - 0.16, -0.32), BR]);
  iron.push([tubeBetween(new THREE.Vector3(0, top + 0.05, PZ), new THREE.Vector3(0, top + 0.38, PZ - 0.3), 0.018, 0.016, 8), IR]); iron.push([new THREE.SphereGeometry(0.03, 10, 8).translate(0, top + 0.39, PZ - 0.31), BR]);
  // a coil of rope, a fish, a float by its foot
  { const g = ropeRing(0.17, 0.028, 5); g.translate(0.45, y0 + 0.03, 0.45); wood.push([g, null]); const g2 = ropeRing(0.14, 0.028, 5); g2.translate(0.45, y0 + 0.08, 0.45); wood.push([g2, null]); }
  iron.push([new THREE.SphereGeometry(0.15, 14, 10).scale(1, 0.4, 0.24).rotateY(0.6).translate(-0.48, y0 + 0.05, 0.42), hexC(0x7E96A8)]); iron.push([new THREE.ConeGeometry(0.06, 0.12, 4).rotateZ(-Math.PI / 2).scale(1, 1, 0.3).rotateY(0.6).translate(-0.6, y0 + 0.05, 0.5), hexC(0x6A8496)]);
  iron.push([new THREE.SphereGeometry(0.09, 12, 10).scale(1, 1.3, 1).translate(0.58, y0 + 0.11, -0.25), (x, y) => hexC(y > y0 + 0.12 ? 0xF4F1EA : 0xF2771E)]);
  const rc = new THREE.CatmullRomCurve3([[0, top - 0.17, -0.32], [0, top - 0.26, -0.3], [0, 0.6, -0.29], [0, 0.35, -0.288], [0, y0 + 0.08, -0.287]].map(q => new THREE.Vector3(q[0], q[1], q[2])), false, 'centripetal');
  const stream = streamGeo(rc, HI ? 30 : 16, HI ? 12 : 8, t => { const r = 0.034 - 0.008 * Math.min(1, t / 0.6); return [r, r]; }, t => Math.min(1, Math.max(0, (t - 0.08) / 0.15)));
  const tubHull = new THREE.CylinderGeometry(rOf(0.5) + 0.03, rOf(0) + 0.03, TH + 0.03, 28, 1, true).translate(0, y0 + TH / 2, 0);
  const hull = mergeGeos([new THREE.CylinderGeometry(0.84, 0.84, y0 + 0.014, 40).translate(0, y0 / 2, 0), new THREE.CylinderGeometry(0.1, 0.1, top - y0, 12, 1, true).translate(0, (top + y0) / 2, PZ)]);
  const lv0 = y0 + 0.065, lv1 = y0 + TH - 0.05;
  return { wood: vcGeo(wood), iron: vcGeo(iron), stream, src: [0, -0.287], tubHull, hull, lv0, lvK: lv1 - lv0, rIn: y => rOf((y - y0) / TH) - 0.044, wallR: y => rOf(Math.max(0, Math.min(1, (y - y0) / TH))), yTop: y0 + TH, surf: new THREE.RingGeometry(0, 1, HI ? 56 : 28, HI ? 6 : 3).rotateX(-Math.PI / 2) };
})();
function makeBarrel(x, y, z, seed) {
  const K = BARREL, p = stationBase(x, y, z, seed, 'barrel'), { inner, tub } = p;
  const wm = new THREE.Mesh(K.wood, cofVC); wm.castShadow = true; wm.receiveShadow = true; inner.add(wm); const im = new THREE.Mesh(K.iron, stGlossM); im.castShadow = true; inner.add(im);
  tub.add(new THREE.Mesh(K.tubHull, outlineMat)); inner.add(new THREE.Mesh(K.hull, outlineMat));
  const liq = new THREE.Mesh(K.surf, p.lm); liq.position.y = 0.3; tub.add(liq);
  const drips = new THREE.Mesh(rimDrips(seed, K.wallR, K.yTop, 3, 0.07, 0.2), p.tm); drips.position.y = K.yTop; tub.add(drips);
  const spill = new THREE.Mesh(spillAt(seed, 0.66, 0.062, 0.2), p.tm); spill.renderOrder = 2; inner.add(spill);
  Object.assign(p, { liq, drips, spill, lv0: K.lv0, lvK: K.lvK, liqR: K.rIn, lift: 0.06, sinkD: 0.95, deb: DEB.barrel });
  addPour(p, K.stream, K.src, seed); return p;
}
{ const chuteG = new THREE.BoxGeometry(0.3, 0.05, 0.3), pipeG = new THREE.CylinderGeometry(0.062, 0.062, 0.5, 10).rotateZ(Math.PI / 2), staveG = new THREE.BoxGeometry(0.1, 0.6, 0.035);
  Object.assign(DEB, {
    drum: { a: toon(0xE6A820, null, { roughness: 0.35, metalness: 0.2 }), b: toon(0x2A302C, null, { roughness: 0.4, metalness: 0.6 }), lid: () => { const g = new THREE.Group(); g.add(new THREE.Mesh(pipeG, toon(0x4A524C, null, { roughness: 0.35, metalness: 0.7 }))); return g; } },
    barrel: { a: toon(0xA87444, { map: woodTex }), b: toon(0x34383A, null, { roughness: 0.4, metalness: 0.6 }), lid: () => { const g = new THREE.Group(); g.add(new THREE.Mesh(staveG, toon(0xA87444, { map: woodTex }))); return g; } },
  }); }
