"""v256: in a Showdown the canvas closes in. A minute in, the edge closes to a normal canvas's size; at two minutes, smaller still.
Fifteen seconds before each, a glowing curtain shows where it will be (a countdown says when), so there's time to get inside; anyone
inside is untouched. Out past it once it has closed, a red haze lies over the lost ground: your paint burns off fast there, and with
none left you're knocked out. Basins and respawns out there are skipped, the orb stays inside, and the CPUs make for the inside when
it's coming (and don't chase anyone out past it)."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
CSS = r"""
/* (v256) the closing canvas: a countdown under the hearts, and red at the edges while you're out past the line */
.zchip{display:flex;align-items:center;gap:6px;margin:3px auto 0;padding:4px 10px 4px 8px;width:max-content;border-radius:99px;background:#E3122F;box-shadow:0 0 0 2.5px var(--line),0 3px 0 var(--line);color:#fff;font:900 12px/1 var(--font-ui);letter-spacing:.06em;text-transform:uppercase;white-space:nowrap}
.zchip[hidden]{display:none}
.zchip svg{width:14px;height:14px;fill:none;stroke:#fff;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}
.zchip b{font:900 15px/1 var(--font-head);font-style:italic;letter-spacing:0;min-width:1.1em;text-align:right}
.zchip.now{animation:zchip .5s ease-in-out infinite alternate}
@keyframes zchip{to{transform:scale(1.08)}}
.zvig{position:absolute;inset:0;z-index:3;pointer-events:none;opacity:0;transition:opacity .35s;background:radial-gradient(ellipse 85% 80% at 50% 50%,transparent 52%,rgba(227,18,47,.38) 82%,rgba(160,8,30,.7) 100%)}
.zvig.on{opacity:1;animation:zvig .6s ease-in-out infinite alternate}
@keyframes zvig{to{opacity:.6}}
"""
JS = r"""
// ---------- (v256) Showdown: the canvas closes in ----------
const ZONE_AT = [60, 120], ZONE_SZ = [26.4, 20], ZONE_WARN = 15, ZONE_BURN = 0.32, ZONE_KO = 1.1;
let zone = null;
const zoneOutside = (x, z, s) => s > 0 && Math.max(Math.abs(x), Math.abs(z)) > s;
// how far in it's safe: the line that's closing if one is (from its warning on), else the one that has closed
function zoneCut() { if (!zone || !isShow()) return 0; return zone.warn ? zone.next : zone.cur < ARENA - 0.01 ? zone.cur : 0; }
const zoneLost = (x, z) => zoneOutside(x, z, zoneCut());
const zoneEdge = () => zoneCut() || ARENA;
const ZONE_VS = 'attribute float aK; attribute float aV; varying float vK; varying float vV; varying vec3 vW; void main(){ vK = aK; vV = aV; vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }';
const ZONE_FS = 'uniform float uT; uniform float uK; uniform float uWarn; varying float vK; varying float vV; varying vec3 vW;\n'
  + 'void main(){ float s = fract((vW.x + vW.z) * 0.16 - uT * 0.55); float st = smoothstep(0.0, 0.06, s) * (1.0 - smoothstep(0.4, 0.46, s)); float pulse = 0.62 + 0.38 * sin(uT * 6.2);\n'
  + '  vec3 hot = vec3(1.0, 0.16, 0.3), dark = vec3(0.3, 0.015, 0.07);\n'
  + '  if (vK < 0.5) { float a = (uWarn > 0.5 ? 0.09 * pulse : 0.4) * uK; gl_FragColor = vec4(mix(dark, hot, 0.22 * st), a + 0.06 * st * uK); }\n'
  + '  else { float v = clamp(vV, 0.0, 1.0), fade = pow(1.0 - v, 1.1), base = exp(-v * 9.0), a = clamp(fade * (0.5 + 0.45 * st) + 0.85 * base, 0.0, 1.0) * uK * (uWarn > 0.5 ? 0.6 + 0.4 * pulse : 1.0); gl_FragColor = vec4(mix(hot, vec3(1.0, 0.9, 0.93), 0.45 * st + 0.55 * base), a); } }';
function zoneMat(warn) { return new THREE.ShaderMaterial({ uniforms: { uT: { value: 0 }, uK: { value: 0 }, uWarn: { value: warn ? 1 : 0 } }, vertexShader: ZONE_VS, fragmentShader: ZONE_FS, transparent: true, depthWrite: false, side: THREE.DoubleSide }); }
// the haze over the ground out past the line (a lid above the tallest thing on the canvas, so it tints everything under it) and the
// glowing curtain along the line itself: one mesh
function zoneMesh(s, warn) {
  let top = 0; for (const b of BOXES) top = Math.max(top, b[5] || 0); const H = clamp(top + 0.9, 2.4, 6.5), A = ARENA + 0.02, y0 = -0.15;
  const P3 = [], K = [], V = [], quad = (a, b, c, d, k, va, vb, vc, vd) => { P3.push(...a, ...b, ...c, ...a, ...c, ...d); K.push(k, k, k, k, k, k); V.push(va, vb, vc, va, vc, vd); };
  quad([-A, H, s], [A, H, s], [A, H, A], [-A, H, A], 0, 0, 0, 0, 0); quad([-A, H, -A], [A, H, -A], [A, H, -s], [-A, H, -s], 0, 0, 0, 0, 0);
  quad([-A, H, -s], [-s, H, -s], [-s, H, s], [-A, H, s], 0, 0, 0, 0, 0); quad([s, H, -s], [A, H, -s], [A, H, s], [s, H, s], 0, 0, 0, 0, 0);
  for (const [ax, az, bx, bz] of [[-s, s, s, s], [s, -s, -s, -s], [s, s, s, -s], [-s, -s, -s, s]]) quad([ax, y0, az], [bx, y0, bz], [bx, H, bz], [ax, H, az], 1, 0, 0, 1, 1);
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P3, 3)); g.setAttribute('aK', new THREE.Float32BufferAttribute(K, 1)); g.setAttribute('aV', new THREE.Float32BufferAttribute(V, 1));
  const m = new THREE.Mesh(g, zoneMat(warn)); m.frustumCulled = false; m.renderOrder = 40; scene.add(m); return m;
}
function zoneDrop(m) { if (!m) return; scene.remove(m); m.geometry.dispose(); m.material.dispose(); }
function zoneClear() { if (zone) { zoneDrop(zone.mNow); zoneDrop(zone.mNext); } zone = isShow() ? { cur: ARENA, step: 0, warn: false, next: 0, mNow: null, mNext: null, shown: -1 } : null; const c = $('zChip'); if (c) c.hidden = true; const v = $('zVig'); if (v) v.classList.remove('on'); }
function zoneTick(dt) {
  if (!zone || !isShow() || state !== 'play') return;
  const i = zone.step;
  if (i < ZONE_AT.length) {
    const t = ZONE_AT[i] - runT;
    if (t <= ZONE_WARN && !zone.warn) { zone.warn = true; zone.next = ZONE_SZ[i]; zone.mNext = zoneMesh(zone.next, true); banner('The canvas is closing in!', 'Get inside the red line'); if (AU.spot) AU.spot(); buzz([15, 40, 15]); for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; }
    if (zone.warn) { const n = Math.max(0, Math.ceil(t)); if (n !== zone.shown) { zone.shown = n; const c = $('zChip'); c.hidden = false; $('zChipN').textContent = n; c.classList.toggle('now', n <= 5); if (n <= 3 && n > 0 && AU.tick) AU.tick(); } }
    if (t <= 0) {
      zone.cur = ZONE_SZ[i]; zone.step++; zone.warn = false; zone.next = 0; zone.shown = -1; zoneDrop(zone.mNow); zoneDrop(zone.mNext); zone.mNext = null; zone.mNow = zoneMesh(zone.cur, false); $('zChip').hidden = true;
      shake = Math.max(shake, 0.25); if (AU.quake) AU.quake(); banner('Closed in!', zoneLost(P.x, P.z) && P.st === 'play' ? 'Get back inside!' : 'Stay inside the line');
      for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0;
    }
  }
  for (const m of [zone.mNow, zone.mNext]) if (m) { const u = m.material.uniforms; u.uT.value += dt; u.uK.value = Math.min(1, u.uK.value + dt * 1.6); }
  // out past a closed line: the paint burns off, and with none left you're out (in a basin out there, you're thrown out of it)
  let pOut = false;
  for (const D of ACTIVE) {
    if (!zoneOutside(D.x, D.z, zone.cur < ARENA - 0.01 ? zone.cur : 0) || D.rocket) { D.zoneT = 0; continue; }
    if (D.st === 'hide' && D.pot) { exitPot(D, false); if (D === P) popText('This basin is out past the line'); continue; }
    if (D.st !== 'play') continue;
    if (D === P) pOut = true;
    D.paint = Math.max(0, D.paint - ZONE_BURN * dt); burnFx(D, dt);
    if (D.paint <= 0) { if (!D.dry) goDry(D); D.zoneT = (D.zoneT || 0) + dt; if (D.zoneT > ZONE_KO) { D.zoneT = 0; knockOut(D, 'zone'); } }
    if (D.ai && D.ai.mode !== 'zone') D.ai.thinkT = 0;
  }
  const v = $('zVig'); if (v.classList.contains('on') !== pOut) { v.classList.toggle('on', pOut); if (pOut) popText('Get back inside the line!'); }
}
"""
def apply(s):
    s = rep(s, "\n</style>\n\n<div id=\"stage\">", "\n" + CSS.strip() + "\n</style>\n\n<div id=\"stage\">")
    s = rep(s, '<div class="sdbar" id="sdBar" hidden role="img" aria-label="Hearts"></div>',
               '<div class="sdbar" id="sdBar" hidden role="img" aria-label="Hearts"></div>\n        <div class="zchip" id="zChip" hidden role="status"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5M9 9l-4-4M15 9l4-4M9 15l-4 4M15 15l4 4"/></svg><span>Closing in</span><b id="zChipN">15</b></div>')
    s = rep(s, '<div class="frost" id="frost" aria-hidden="true"></div>', '<div class="frost" id="frost" aria-hidden="true"></div>\n  <div class="zvig" id="zVig" aria-hidden="true"></div>')
    s = rep(s, "  itemTick(dt); trapTick(dt); freezeTick(dt);", "  itemTick(dt); trapTick(dt); freezeTick(dt); zoneTick(dt);")
    s = rep(s, "sdEndT = 0; sdSpecEnd();", "sdEndT = 0; sdSpecEnd(); zoneClear();")
    s = rep(s, "const KO_MSG = { ", "const KO_MSG = { zone: 'Caught outside!', ")
    s = rep(s, "const CPU_KO_MSG = { ", "const CPU_KO_MSG = { zone: n => n + ' got caught outside', ")
    # ---- the CPUs: the ground out past the line costs a lot to cross; caught outside (or about to be), they make for the inside
    s = rep(s, "  dijkstra(src.id, sunny || wxPhase === 'warn' || AI.sunLead > 0 && timeToSun() < 12 ? 0 : 64);",
               "  { const zc = zoneCut(); if (zc) { const nodes = NAV.nodes; for (let k = 0; k < nodes.length; k++) { const n = nodes[k]; if (zoneOutside(n.x, n.z, zc - 0.6)) nMult[n.id] += 10; } } } // (v256: out past the line)\n"
               "  dijkstra(src.id, sunny || wxPhase === 'warn' || AI.sunLead > 0 && timeToSun() < 12 ? 0 : 64);")
    s = rep(s, "  ai.need = need;\n",
               "  ai.need = need;\n"
               "  { const zc = zoneCut(); if (zc && zoneOutside(D.x, D.z, zc - 0.9)) { let best = null, bd = Infinity; for (const n of NAV.nodes) { if (zoneOutside(n.x, n.z, zc - 2.2) || !(nDist[n.id] < bd)) continue; bd = nDist[n.id]; best = n; } if (best) { aiGo(D, best, 'zone'); return; } } } // (v256: get inside the line)\n")
    s = rep(s, "  for (const p of pots) { if (!potUp(p) || p.ink < 0.25 || p.occ) continue; const n = potNode(p); if (!n) continue;",
               "  for (const p of pots) { if (!potUp(p) || p.ink < 0.25 || p.occ || zoneLost(p.x, p.z)) continue; const n = potNode(p); if (!n) continue;")
    s = rep(s, "  if (isShow() && AI.seek && !sunNow && D.paint > Math.max(0.4, need + 0.12) && O.st === 'play' && O.immuneT <= 0.5 && Math.random() < AI.seek) {",
               "  if (isShow() && AI.seek && !sunNow && D.paint > Math.max(0.4, need + 0.12) && O.st === 'play' && O.immuneT <= 0.5 && !zoneLost(O.x, O.z) && Math.random() < AI.seek) {")
    # ---- coming back: a basin inside the line; the orb stays inside it too
    s = rep(s, "  let cands = pots.filter(p => potUp(p) && !p.occ); if (!cands.length) cands = pots.filter(p => p.st === 'down');",
               "  let cands = pots.filter(p => potUp(p) && !p.occ); if (!cands.length) cands = pots.filter(p => p.st === 'down');\n"
               "  { const inz = cands.filter(p => !zoneLost(p.x, p.z)); if (inz.length) cands = inz; } // (v256: inside the line)")
    s = rep(s, "if (d < 3 || d > 11 || Math.max(Math.abs(c[0]), Math.abs(c[2])) > ARENA - 3) continue;", "if (d < 3 || d > 11 || Math.max(Math.abs(c[0]), Math.abs(c[2])) > zoneEdge() - 3) continue;")
    s = rep(s, "// ---------- Choose Event (v209): Play opens it.", JS.strip() + "\n// ---------- Choose Event (v209): Play opens it.")
    return s
