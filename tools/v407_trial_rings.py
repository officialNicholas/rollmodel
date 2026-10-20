"""v407: rings in the time trial (the user: "add these half rings around the map. They spawn one after the other ... yellow sort of
half rings that you see in racing games that you have to go through. If you go through it, it adds two seconds of additional time to
the timer ... There's no winner lose here. It's just trying to get to the leaderboard. So there's never any defeat music").

The rings: a gold arch standing on the floor, one at a time. Roll through it (either way, under the arch: jumping over it doesn't
count) and the clock gets 2 more seconds; it bursts, and the next one rises out of the floor somewhere else. Where: a spot you can roll
to from where you are (the CPUs' map of the canvas, so never somewhere only a jump reaches), 9 to 24 steps away by the way you'd go,
on flat open floor wide enough for the arch and its way in and out, turned to face that way in; and among those, mostly where the
canvas is still bare, a little ahead of you, never where one just was. So following them takes you round the canvas, painting. The
first one is close, just ahead. A pointer finds one off screen (or far off), as for the orb.

Going through: a chime (one of its own, made with Ludo and finished like the others; it climbs a step for each ring taken within a few
seconds of the last), a burst of gold, a "+2" where you went through and on the clock, a tick of the phone. The count is on the
results.

No winning or losing in a time trial: whatever the run, the results play the win sting and song (a new best still gets the confetti
and its own words), the blob celebrates, and the results' title never takes the losing look."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """/* (v407) the time trial's rings: the pointer to the next one, the +2 that pops where you went through, and the clock's */
.ringptr i{inset:3px;display:grid;place-items:center;background:radial-gradient(circle at 50% 36%,#FFFFFF,#FFF4C4 55%,#FFD45A);box-shadow:0 0 14px 5px rgba(255,196,40,.75);animation:none}
.ringptr.edge i{animation:orbpulse .7s ease-in-out infinite alternate}
.ringptr i svg{width:24px;height:24px;display:block}
.ringadd{position:absolute;left:0;top:0;z-index:7;pointer-events:none;font:900 34px/1 var(--font-head);font-style:italic;letter-spacing:-.01em;color:#FFD23F;-webkit-text-stroke:2.5px #171320;paint-order:stroke fill;text-shadow:0 3px 0 #171320;opacity:0;white-space:nowrap;transform:translate(var(--x,0),var(--y,0)) translate(-50%,-50%);will-change:transform,opacity}
.ringadd small{font-size:.55em;margin-left:1px}
.ringadd.on{animation:ringadd .95s cubic-bezier(.2,.8,.3,1) forwards}
@keyframes ringadd{0%{opacity:0;transform:translate(var(--x,0),var(--y,0)) translate(-50%,-50%) scale(.4)}16%{opacity:1;transform:translate(var(--x,0),var(--y,0)) translate(-50%,-85%) scale(1.18)}70%{opacity:1;transform:translate(var(--x,0),var(--y,0)) translate(-50%,-150%) scale(1)}100%{opacity:0;transform:translate(var(--x,0),var(--y,0)) translate(-50%,-185%) scale(.96)}}
.clkadd{position:absolute;left:0;top:0;z-index:1;pointer-events:none;font:900 14px/1 var(--font-head);font-style:italic;color:#D99200;opacity:0;white-space:nowrap;transform:translate(-50%,0)}
.clkadd.on{animation:clkadd .9s ease-out forwards}
@keyframes clkadd{0%{opacity:0;transform:translate(-50%,-2px) scale(.6)}18%{opacity:1;transform:translate(-50%,3px) scale(1.15)}100%{opacity:0;transform:translate(-50%,15px) scale(1)}}
.clock.bonus{animation:clkbonus .55s cubic-bezier(.3,1.6,.5,1)}
@keyframes clkbonus{0%{transform:rotate(2deg) scale(1)}35%{transform:rotate(2deg) scale(1.3);color:#C98A00}100%{transform:rotate(2deg) scale(1)}}
@media (prefers-reduced-motion:reduce){.ringadd.on{animation:ringfade .95s linear forwards}.clkadd.on{animation:ringfade .9s linear forwards}.clock.bonus{animation:none}@keyframes ringfade{0%,70%{opacity:1}100%{opacity:0}}}
"""

PTR = ('  <div class="orbptr ringptr" id="ringPtr" aria-hidden="true"><i><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.6 20V13.2a7.4 7.4 0 0 1 14.8 0V20" fill="none" stroke="#1A1030" '
       'stroke-width="5.4" stroke-linecap="round"/><path d="M4.6 20V13.2a7.4 7.4 0 0 1 14.8 0V20" fill="none" stroke="#FFC21A" stroke-width="2.6" stroke-linecap="round"/></svg></i><u><b></b></u></div>\n'
       '  <b class="ringadd" id="ringAdd" aria-hidden="true"></b>\n')

JS = r"""// ---------- (v407) the time trial's rings: a gold arch on the floor, one at a time; through it, 2 more seconds ----------
const TR_R = 1.6, TR_TUBE = 0.15, TR_ADD = 2;
const TR = { on: false, x: 0, y: 0, z: 0, yaw: 0, k: 0, out: 0, wait: 0, n: 0, px: 0, pz: 0, py: 0, have: false, last: [], streak: 0, lastAt: -9, near: 0 };
const trG = new THREE.Group(); trG.visible = false; scene.add(trG);
const trBody = new THREE.Group(); trG.add(trBody);
const trMat = toon(0xFFC21A, { emissive: new THREE.Color(0xFF9800), emissiveIntensity: 0.55 }, { roughness: 0.32, metalness: 0.45 });
const trOutline = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide });
{ const arch = new THREE.Mesh(new THREE.TorusGeometry(TR_R, TR_TUBE, SEG(10), SEG(44), Math.PI), trMat), hull = new THREE.Mesh(new THREE.TorusGeometry(TR_R, TR_TUBE + 0.045, SEG(10), SEG(44), Math.PI), trOutline);
  arch.castShadow = true; trBody.add(arch); trBody.add(hull);
  // its feet: a stubby collar where each end meets the floor
  for (const sx of [-1, 1]) { const f = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.3, 0.16, SEG(14)), trMat), fh = new THREE.Mesh(new THREE.CylinderGeometry(0.29, 0.34, 0.2, SEG(14)), trOutline);
    f.position.set(sx * TR_R, 0.06, 0); fh.position.copy(f.position); trBody.add(f); trBody.add(fh); } }
// the sheen inside the arch: rings of light running out from its middle, faint, so you can see it's a way through
const trFilmU = { uT: { value: 0 }, uK: { value: 0 } };
const trFilm = new THREE.Mesh(new THREE.CircleGeometry(TR_R - TR_TUBE * 0.6, SEG(28), 0, Math.PI), new THREE.ShaderMaterial({ uniforms: trFilmU, transparent: true, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, fog: false,
  vertexShader: 'varying vec2 vP; void main() { vP = position.xy; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: 'uniform float uT, uK; varying vec2 vP; void main() { float r = length(vP) / ' + (TR_R - TR_TUBE * 0.6).toFixed(3) + '; float w = 0.5 + 0.5 * sin(r * 11.0 - uT * 6.0); float a = (0.07 + 0.2 * r * r) * (0.5 + 0.5 * w) * smoothstep(1.0, 0.9, r) * uK; gl_FragColor = vec4(vec3(1.0, 0.8, 0.28) * a, a); }' }));
trFilm.renderOrder = 6; trBody.add(trFilm);
// a warm glow on the floor under it, and sparkles running along it
const trGlow = new THREE.Mesh(new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ map: glowTex, color: 0xFFC83C, transparent: true, opacity: 0.55, depthWrite: false, blending: THREE.AdditiveBlending, polygonOffset: true, polygonOffsetFactor: -4, polygonOffsetUnits: -4, fog: false }));
trGlow.scale.set(TR_R * 2 + 1.6, 1, 2.4); trGlow.position.y = 0.04; trGlow.renderOrder = 5; trG.add(trGlow);
const trSparks = []; for (let i = 0; i < 5; i++) { const sp = glowSprite(0.5); sp.material.color.set(0xFFE27A); trBody.add(sp); trSparks.push(sp); }
const trFlash = glowSprite(4.2); trFlash.material.color.set(0xFFF1B0); trFlash.position.y = TR_R * 0.55; trG.add(trFlash);
const trPartMats = [0xFFD23F, 0xFFF3B8, 0xFFB000].map(c => new THREE.MeshBasicMaterial({ color: c }));
function trialReset() {
  TR.on = false; TR.k = 0; TR.out = 0; TR.n = 0; TR.wait = mode === 'solo' ? 0.25 : 0; TR.last.length = 0; TR.streak = 0; TR.lastAt = -9; TR.have = false; TR.near = 0; trG.visible = false;
  const el = $('ringPtr'); if (el && el._on) { el._on = false; el.classList.remove('on'); }
  if (mode === 'solo' && AU.xwant) AU.xwant('t_ring');
}
// can the arch stand here, turned this way: flat open floor at its height across the arch and a couple of steps either side of it
// (the way in and out), nothing standing through the arch, nothing low over its middle
function trialFits(x, z, h, yaw) {
  const ax = Math.cos(yaw), az = -Math.sin(yaw), fx = Math.sin(yaw), fz = Math.cos(yaw);
  for (let iu = -2; iu <= 2; iu++) { const u = iu / 2 * (TR_R + 0.3);
    for (let iv = -2; iv <= 2; iv++) { const v = iv * 1.15, px = x + ax * u + fx * v, pz = z + az * u + fz * v, g = surfaceUnder(px, pz, h + STEP, true);
      if (!(Math.abs(g - h) < 0.12) || blockedAt(px, pz, h + 0.05)) return false; } }
  for (let k = 0; k <= 8; k++) { const a = k / 8 * Math.PI, c = Math.cos(a) * TR_R, py = h + Math.sin(a) * TR_R, px = x + ax * c, pz = z + az * c;
    if (solidThrough(px, pz, py) || solidThrough(px, pz, py + TR_TUBE)) return false; }
  // the drifting clouds (MOVERS) aren't solid, so nothing above sees them: keep the arch out of the whole run of each one at its height
  for (const m of MOVERS) { if (!m.on || h + TR_R + TR_TUBE < m.y0 - 0.3 || h > m.y1 + 0.3) continue;
    const ex = (m.axis === 'x' ? m.amp : 0) + m.hw + TR_R + 0.9, ez = (m.axis === 'z' ? m.amp : 0) + m.hw + TR_R + 0.9;
    if (Math.abs(x - m.x) < ex && Math.abs(z - m.z) < ez) return false; }
  return !solidThrough(x, z, h + 0.5) && !solidThrough(x, z, h + 1.1);
}
// the next ring: somewhere you can roll to from here, by the CPUs' map (its own distances: the CPUs' costs aren't kept up in a time
// trial), mostly where the canvas is still bare and a little ahead of you, not where one just was; then turned to face the way in
const trD = { dist: null, prev: null, hi: null, hd: null };
function trialSpawn() {
  const nodes = NAV.nodes, NNn = nodes.length; if (!NNn || !NAV.nbOff) { TR.wait = 0.5; return; }
  let src = NAV.at(P.x, P.z, P.y); if (!src) { const g = surfaceUnder(P.x, P.z, P.y + 0.5, true); if (g > -Infinity) src = NAV.at(P.x, P.z, g); }
  if (!src) { TR.wait = 0.3; return; }
  if (!trD.dist || trD.dist.length < NNn) { const c = NNn + 512; trD.dist = new Float32Array(c); trD.prev = new Int32Array(c); trD.hi = new Int32Array(c * 9); trD.hd = new Float32Array(c * 9); }
  const dist = trD.dist, prev = trD.prev, hi = trD.hi, hd = trD.hd, off = NAV.nbOff, to = NAV.nbTo, wt = NAV.nbW; dist.fill(Infinity, 0, NNn); prev.fill(-1, 0, NNn);
  let hn = 0; const push = (i, d) => { let k = hn++; hi[k] = i; hd[k] = d; while (k > 0) { const p = (k - 1) >> 1; if (hd[p] <= hd[k]) break; const ti = hi[p], td = hd[p]; hi[p] = hi[k]; hd[p] = hd[k]; hi[k] = ti; hd[k] = td; k = p; } };
  dist[src.id] = 0; push(src.id, 0);
  while (hn) { const i = hi[0], d = hd[0]; hn--; hi[0] = hi[hn]; hd[0] = hd[hn];
    let k = 0; for (;;) { const l = k * 2 + 1, r = l + 1; let m = k; if (l < hn && hd[l] < hd[m]) m = l; if (r < hn && hd[r] < hd[m]) m = r; if (m === k) break; const ti = hi[m], td = hd[m]; hi[m] = hi[k]; hd[m] = hd[k]; hi[k] = ti; hd[k] = td; k = m; }
    if (d > dist[i] || d > 30) continue;
    for (let e = off[i], e1 = off[i + 1]; e < e1; e++) { const j = to[e], nd = d + wt[e]; if (nd < dist[j]) { dist[j] = nd; prev[j] = i; if (hn < hi.length) push(j, nd); } } }
  const first = TR.n === 0, lo = first ? 6 : 9, hiD = first ? 14 : 24, want = first ? 9 : 15, E = zoneEdge() - 3, fx = Math.sin(P.yaw), fz = Math.cos(P.yaw), cand = [];
  for (const n of nodes) { const d = dist[n.id]; if (!(d >= lo && d <= hiD) || n.edge > 0.5 || Math.abs(n.x) > E || Math.abs(n.z) > E) continue;
    let skip = false; for (const q of TR.last) if (Math.hypot(q[0] - n.x, q[1] - n.z) < 7) { skip = true; break; }
    if (!skip) for (const p of pots) if (Math.hypot(p.x - n.x, p.z - n.z) < TR_R + 1.5) { skip = true; break; }
    if (skip) continue;
    let bare = 0, all = 0; for (let e = NAV.dOff[n.id], e1 = NAV.dOff[n.id + 1]; e < e1; e++) { const m = NAV.dIds[e]; for (let q = NAV.smOff[m], q1 = NAV.smOff[m + 1]; q < q1; q++) { all++; if (!painted[NAV.smIdx[q]]) bare++; } }
    const dx = n.x - P.x, dz = n.z - P.z, ahead = (dx * fx + dz * fz) / (Math.hypot(dx, dz) || 1);
    cand.push([(all ? bare / all : 0.5) * 1.2 + ahead * (first ? 1.4 : 0.35) - Math.abs(d - want) / 18 + Math.random() * 0.3, n]); }
  cand.sort((a, b) => b[0] - a[0]);
  for (let i = 0; i < cand.length && i < 60; i++) { const n = cand[i][1];
    let q = n.id; for (let k = 0; k < 4 && prev[q] >= 0; k++) q = prev[q]; // (the way you'd come in: a few steps back along the way there)
    const qn = nodes[q], base = q !== n.id ? Math.atan2(n.x - qn.x, n.z - qn.z) : Math.atan2(n.x - P.x, n.z - P.z);
    for (const o of [0, 0.4, -0.4, 0.8, -0.8, 1.5708]) if (trialFits(n.x, n.z, n.h, base + o)) return trialPlace(n.x, n.h, n.z, base + o); }
  TR.wait = 0.5; // (nowhere this time: again in a moment)
}
function trialPlace(x, y, z, yaw) {
  Object.assign(TR, { on: true, k: 0, x, y, z, yaw, near: 0 }); TR.last.push([x, z]); if (TR.last.length > 4) TR.last.shift();
  for (let i = 0; i < 14; i++) { const a = i / 13 * Math.PI, c = Math.cos(a) * TR_R, ax = Math.cos(yaw), az = -Math.sin(yaw); spawnPart(x + ax * c, y + 0.1, z + az * c, (Math.random() - 0.5) * 1.4, 2.5 + Math.random() * 2.5, (Math.random() - 0.5) * 1.4, 0.55, trPartMats[i % 3], 0.5, 0.7); }
  if (TR.n === 0) hint('rings', say('Roll through the rings for 2 more seconds', 'Roll through the rings for 2 more seconds'), 3);
}
// through it: under the arch, from one side to the other (either way), going there by rolling, flinging or hopping
function trialTick(dt) {
  if (!TR.on && TR.wait > 0) { TR.wait -= dt; if (TR.wait <= 0) trialSpawn(); }
  const ok = P.st === 'play';
  if (TR.on && TR.k > 0.35 && ok && TR.have) {
    const fx = Math.sin(TR.yaw), fz = Math.cos(TR.yaw), ax = Math.cos(TR.yaw), az = -Math.sin(TR.yaw);
    const s0 = (TR.px - TR.x) * fx + (TR.pz - TR.z) * fz, s1 = (P.x - TR.x) * fx + (P.z - TR.z) * fz;
    if ((s0 < 0) !== (s1 < 0) && Math.hypot(P.x - TR.px, P.z - TR.pz) < 3) { // (a jump across the map, a respawn, is never a pass)
      const t = s0 / (s0 - s1), cx = TR.px + (P.x - TR.px) * t, cz = TR.pz + (P.z - TR.pz) * t, cy = TR.py + (P.y - TR.py) * t;
      const lat = (cx - TR.x) * ax + (cz - TR.z) * az, inner = TR_R - TR_TUBE;
      if (Math.abs(lat) < inner - 0.05 && cy - TR.y < Math.sqrt(inner * inner - lat * lat) - 0.15) trialPass(cx, cy, cz);
    }
  }
  TR.px = P.x; TR.pz = P.z; TR.py = P.y; TR.have = ok;
}
function trialPass(x, y, z) {
  TR.on = false; TR.out = 1; TR.n++; TR.wait = 0.4; matchLeft += TR_ADD;
  TR.streak = runT - TR.lastAt < 9 ? Math.min(TR.streak + 1, 7) : 0; TR.lastAt = runT; // (one after another: the chime climbs a step each)
  if (!(AU.xplay && AU.xplay('t_ring', { v: 0.8, rate: Math.pow(2, TR.streak / 12) }))) AU.power();
  hap('select');
  const ax = Math.cos(TR.yaw), az = -Math.sin(TR.yaw), mx = P.x - TR.px, mz = P.z - TR.pz, ml = Math.hypot(mx, mz) || 1, dx = mx / ml, dz = mz / ml;
  for (let i = 0; i < 30; i++) { const a = (i + 0.5) / 30 * Math.PI, c = Math.cos(a), s = Math.sin(a), sp = 2.5 + Math.random() * 3;
    spawnPart(TR.x + ax * c * TR_R, TR.y + s * TR_R, TR.z + az * c * TR_R, (ax * c) * sp + dx * 2.5, s * sp + 1.5, (az * c) * sp + dz * 2.5, 0.5 + Math.random() * 0.35, trPartMats[i % 3], 0.55 + Math.random() * 0.45, 0.6); }
  // the +2: where you went through, and on the clock
  const el = $('ringAdd'); tv1.set(TR.x, TR.y + TR_R * 0.75, TR.z).project(camera);
  if (tv1.z < 1) { el.innerHTML = '+' + TR_ADD + '<small>s</small>'; el.style.setProperty('--x', ((tv1.x * 0.5 + 0.5) * viewW).toFixed(1) + 'px'); el.style.setProperty('--y', ((-tv1.y * 0.5 + 0.5) * viewH).toFixed(1) + 'px'); restartCls(el, 'on'); }
  const ck = $('clock'), ca = $('clkAdd'); restartCls(ck, 'bonus');
  if (ca) { ca.textContent = '+' + TR_ADD; ca.style.left = (ck.offsetLeft + ck.offsetWidth / 2).toFixed(0) + 'px'; ca.style.top = (ck.offsetTop + ck.offsetHeight + 2).toFixed(0) + 'px'; restartCls(ca, 'on'); }
}
// the look, each frame: rising out of the floor, its glow breathing (brighter as you come close), sparkles running along it; through,
// a flash and it swells and is gone; the pointer to it when it's off screen or far off
let trHudY = 0, trHudAt = -9; const trHudBot = () => { if (clock - trHudAt > 0.5) { trHudAt = clock; const e = document.querySelector('.hud .score'); trHudY = e && e.offsetParent ? e.getBoundingClientRect().bottom : 0; } return trHudY; };
const trBack = u => { const c = 1.9; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
function trialDraw(playing, dt) {
  if (TR.on && (state === 'dead' || state === 'menu')) { TR.on = false; TR.out = 0; } // (the match is over: it goes with it)
  if (TR.on) TR.k = Math.min(1, TR.k + dt / 0.45);
  if (TR.out > 0) TR.out = Math.max(0, TR.out - dt / 0.34);
  const show = TR.on || TR.out > 0; trG.visible = show;
  if (show) {
    const k = TR.on ? TR.k : 1, u = TR.on ? 0 : 1 - TR.out, rise = 1 - Math.pow(1 - k, 3);
    const near = TR.on && P.st === 'play' ? clamp(1 - (Math.hypot(P.x - TR.x, P.z - TR.z) - 2) / 6, 0, 1) : 0; TR.near += (near - TR.near) * Math.min(1, dt * 6);
    const sc = (TR.on ? Math.max(0.01, trBack(k)) : (u < 0.35 ? 1 + 0.45 * Math.sin(u / 0.35 * Math.PI / 2) : 1.45 * (1 - (u - 0.35) / 0.65))) * (1 + 0.025 * Math.sin(clock * 4));
    trG.position.set(TR.x, TR.y, TR.z); trG.rotation.y = TR.yaw; trBody.position.y = -0.55 * (1 - rise); trBody.scale.setScalar(Math.max(0.01, sc));
    trMat.emissiveIntensity = TR.on ? 0.45 + 0.2 * Math.sin(clock * 5) + 0.45 * TR.near : 0.9 + 1.4 * (1 - u);
    trFilmU.uT.value = clock; trFilmU.uK.value = (TR.on ? k * (0.8 + 0.6 * TR.near) : 1 - u);
    trGlow.material.opacity = (TR.on ? 0.45 + 0.15 * Math.sin(clock * 5) + 0.2 * TR.near : 0.7 * (1 - u)) * rise;
    trSparks.forEach((sp, i) => { const a = ((clock * 0.55 + i / trSparks.length) % 1) * Math.PI; sp.position.set(Math.cos(a) * TR_R, Math.sin(a) * TR_R, 0); sp.material.opacity = 0.9 * Math.sin(a) * (TR.on ? 1 : 1 - u); sp.scale.setScalar(0.42 + 0.12 * Math.sin(clock * 9 + i)); });
    trFlash.visible = !TR.on; if (!TR.on) { trFlash.material.opacity = Math.max(0, 1 - u * 1.6); trFlash.scale.setScalar(2.5 + 4 * u); }
  }
  const el = $('ringPtr');
  if (TR.on && TR.k > 0.3 && playing && P.st !== 'ko') { tv1.set(TR.x, TR.y + TR_R + 0.5, TR.z).project(camera); const W = viewW, Hh = viewH, behind = tv1.z > 1; let x = behind ? -tv1.x : tv1.x, y = behind ? -tv1.y : tv1.y;
    const on = !behind && Math.abs(x) < 0.9 && Math.abs(y) < 0.78, far = Math.hypot(TR.x - P.x, TR.z - P.z) > 9;
    if (on && !far) { if (el._on) { el._on = false; el.classList.remove('on'); } }
    else { let px, py, rot; if (on) { px = (x * 0.5 + 0.5) * W; py = Math.max((-y * 0.5 + 0.5) * Hh - 30 - Math.abs(Math.sin(clock * 5)) * 6, trHudBot() + 26); rot = 180; } /* (never over the score card) */ else { const m = Math.max(Math.abs(x) / 0.86, Math.abs(y) / 0.72, 1e-3); x /= m; y /= m; px = (x * 0.5 + 0.5) * W; py = (-y * 0.5 + 0.5) * Hh; rot = Math.atan2(x, y) * 180 / Math.PI; }
      if (!el._on) { el._on = true; el.classList.add('on'); } el.classList.toggle('edge', !on); el.style.transform = 'translate(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px)'; el.children[1].style.transform = 'rotate(' + rot.toFixed(0) + 'deg)'; } }
  else if (el._on) { el._on = false; el.classList.remove('on'); }
}
"""

def apply(s):
    s = rep(s, "  html:not(.fold) .mworld .frame img.art{height:auto;aspect-ratio:320/220}\n}\n</style>",
               "  html:not(.fold) .mworld .frame img.art{height:auto;aspect-ratio:320/220}\n}\n" + CSS + "</style>")
    s = rep(s, '  <div class="foeptr" id="foePtr"><i></i><u><b></b></u></div>', PTR + '  <div class="foeptr" id="foePtr"><i></i><u><b></b></u></div>')
    s = rep(s, '<span class="clock" id="clock" aria-label="Time left">1:00</span>', '<span class="clock" id="clock" aria-label="Time left">1:00</span><b class="clkadd" id="clkAdd" aria-hidden="true"></b>')
    s = rep(s, "function step(dt) {", JS + "function step(dt) {")
    s = rep(s, "    if (NM) netContact(); else { blobContact(); updateOrb(dt); } updateShots(dt);",
               "    if (NM) netContact(); else { blobContact(); updateOrb(dt); if (mode === 'solo' && !tut) trialTick(dt); } updateShots(dt);")
    s = rep(s, "  shots.length = 0; drawShots();", "  shots.length = 0; drawShots(); trialReset();")
    s = rep(s, "  // the holy water off screen: an edge marker", "  trialDraw(playing, dt); // (v407)\n  // the holy water off screen: an edge marker")
    s = rep(s, "endInfo = { you, cpu, cpu2, win, winner, time: runT, mode, kos, tot };", "endInfo = { you, cpu, cpu2, win, winner, time: runT, mode, kos, tot, rings: mode === 'solo' ? TR.n : 0 };")
    # no winning or losing in a time trial: the win's sting, song and pose whatever the run; the title never in the losing look
    s = rep(s, ": solo ? info.newBest : true, lead = feat[0]", ": true, lead = feat[0]")
    s = rep(s, "const won = solo ? info.newBest : info.show ? info.win > 0 : info.winner === P;", "const won = solo ? true : info.show ? info.win > 0 : info.winner === P;")
    s = rep(s, "t.className = 'rtitle' + (solo ? (info.newBest ? '' : ' lose') : ", "t.className = 'rtitle' + (solo ? '' : ")
    s = rep(s, "if (mode === 'solo' ? newBest : win > 0) celebrating = true;", "if (mode === 'solo' || win > 0) celebrating = true;")
    # the rings on the results, and in the words about the time trial
    s = rep(s, "stats: vicStat(you, '%', 'Canvas painted', true) + vicStat(ttOrd(tt.rank), '', 'This week', false) + ",
               "stats: vicStat(you, '%', 'Canvas painted', true) + vicStat(ttOrd(tt.rank), '', 'This week', false) + (info.rings ? vicStat(info.rings, '', info.rings === 1 ? 'Ring' : 'Rings', false) : '') + ")
    s = rep(s, "['solo', 'Time trial', 'Just you, 60 seconds']", "['solo', 'Time trial', 'Just you, 60 seconds + rings']")
    s = rep(s, "<b>Time trial</b><small>Just you, 60 seconds</small>", "<b>Time trial</b><small>60 seconds. Rings add time</small>")
    s = rep(s, "mode === 'solo' ? 'Cover as much of the canvas as you can in 60 seconds, and beat your best.'",
               "mode === 'solo' ? 'Cover as much of the canvas as you can. You start with 60 seconds, and every gold ring you roll through adds 2 more.'")
    s = rep(s, "if (mode === 'solo') sn.textContent = 'Cover as much as you can in 60 seconds. Every canvas has its own board this week.';",
               "if (mode === 'solo') sn.textContent = 'Cover as much as you can in 60 seconds. Every ring you roll through adds 2 more. Every canvas has its own board this week.';")
    return s
