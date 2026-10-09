import sys, re
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:140])); sys.exit(1)
    s = s.replace(a, b)

# the guide arrow gets a material we can recolor
rep("const arrow = new THREE.Group();\n(() => { const cg = new THREE.ConeGeometry(0.26, 0.46, 18).rotateX(Math.PI); const m = new THREE.Mesh(cg, toon(C.ink));",
    "const arrow = new THREE.Group(), arrowMat = toon(C.ink);\n(() => { const cg = new THREE.ConeGeometry(0.26, 0.46, 18).rotateX(Math.PI); const m = new THREE.Mesh(cg, arrowMat);")

# the HUD no longer sets its own --ink: the chosen color lives on the page root
rep(" if (hud._team !== P.team) { hud._team = P.team; hud.style.setProperty('--ink', TEAMS[P.team].css); }", "")
rep("(burning ? 'Hide! ' : 'Safe · ')", "(burning ? 'Hide! ' : 'Safe ')")

# ---------- menus ----------
old_rs = s[s.index('function renderStages() {'):s.index('// a few strokes and splats in both colors')]
s = s.replace(old_rs, r"""// your color: six paints, and the holy water is always blue
const PALETTE = [
  { id: 'red', name: 'Red', hex: 0xE3122F, hi: '#FF6175', lo: '#99091F', dry: 0x7A1522, words: ['Crimson', 'Scarlet', 'Garnet'] },
  { id: 'orange', name: 'Orange', hex: 0xFF6A13, hi: '#FFA463', lo: '#B5440A', dry: 0x8A3A0E, words: ['Amber', 'Tangerine', 'Embers'] },
  { id: 'gold', name: 'Gold', hex: 0xFFC61A, hi: '#FFDB6E', lo: '#A97B00', dry: 0x8E6A0E, words: ['Gold', 'Saffron', 'Honey'] },
  { id: 'green', name: 'Green', hex: 0x2FD15A, hi: '#7DEB98', lo: '#178A36', dry: 0x1C6B32, words: ['Emerald', 'Jade', 'Absinthe'] },
  { id: 'purple', name: 'Purple', hex: 0xA03CFF, hi: '#C99BFF', lo: '#6A1FB8', dry: 0x52217F, words: ['Violet', 'Amethyst', 'Plum'] },
  { id: 'pink', name: 'Pink', hex: 0xFF3FA4, hi: '#FF8CC8', lo: '#B81F6E', dry: 0x8A2259, words: ['Rose', 'Fuchsia', 'Blush'] },
];
let colorId = 'red', menuReact = 0;
const colorOf = () => PALETTE.find(p => p.id === colorId) || PALETTE[0];
function setColor(id) {
  const c = PALETTE.find(p => p.id === id) || PALETTE[0], css = '#' + c.hex.toString(16).padStart(6, '0').toUpperCase(); colorId = c.id;
  TEAMS[0].wet = c.hex; TEAMS[0].dry = c.dry; TEAMS[0].css = css; C.ink = c.hex;
  COL_INK.setHex(c.hex); TEAM_COLS[0].setHex(c.hex);
  paintUniforms.uWetA.value[0].setHex(c.hex); paintUniforms.uDryA.value[0].setHex(c.dry);
  teamMats[0].color.setHex(c.hex); splashMat.color.setHex(c.hex); xrayMat.color.setHex(c.hex); dropMat.color.setHex(c.hex);
  crownMats[0].color.setHex(c.hex); crownMats[0].emissive.setHex(c.hex).multiplyScalar(0.18);
  arrowMat.color.setHex(c.hex); puIconMat.color.setHex(c.hex); confMats[0].color.setHex(c.hex);
  CAN_INK_TOP.setHex(c.hex).multiplyScalar(0.86); CAN_EMPTY_TOP.setHex(c.hex).multiplyScalar(0.25);
  partPool(colMat(c.hex));
  const r = document.documentElement.style;
  r.setProperty('--ink', css); r.setProperty('--ink-hi', c.hi); r.setProperty('--ink-lo', c.lo); r.setProperty('--ink-rgb', [(c.hex >> 16) & 255, (c.hex >> 8) & 255, c.hex & 255].join(','));
  $('logoWord').textContent = c.name; document.title = 'Paint the World ' + c.name; canvas.setAttribute('aria-label', 'Paint the World ' + c.name + ' game view');
  document.querySelectorAll('#swatches .sw').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.c === c.id)));
}
function renderSwatches() {
  let h = ''; for (const c of PALETTE) h += '<button class="sw" type="button" data-c="' + c.id + '" aria-label="' + c.name + '" aria-pressed="' + (c.id === colorId) + '" style="--c:#' + c.hex.toString(16).padStart(6, '0') + '"><i></i></button>';
  $('swatches').innerHTML = h;
}
// picking a color: the logo repaints, your blob hops and splats the floor in it
function pickColor(id) {
  const same = id === colorId; if (!same) { setColor(id); store.color = colorId; save(); kick($('logo'), 'paint'); }
  menuReact = 0.7; AU.pop(); AU.splat(same ? 0.4 : 0.8);
  if (state === 'menu') { addSplat(P.x, P.y, P.z, P.yaw, 0.9, -8, false, false, 0); for (let i = 0; i < 14; i++) { const a = i / 14 * 6.283; spawnPart(P.x, P.y + 0.3, P.z, Math.cos(a) * 2.2, 2 + Math.random() * 1.6, Math.sin(a) * 2.2, 0.5, teamMats[0], 0.7); } }
}
$('swatches').addEventListener('click', e => { const b = e.target.closest('.sw'); if (!b) return; AU.init(); pickColor(b.dataset.c); });
function renderStages() {
  const el = $('stages');
  if (!el.children.length) { let h = ''; for (const [k, name, tag] of DIFFS) h += '<button type="button" data-d="' + k + '" title="' + tag + '">' + name + '</button>'; el.innerHTML = h; }
  for (const b of el.children) b.setAttribute('aria-pressed', String(b.dataset.d === diff));
  $('cvName').textContent = TH.label; $('shuffleBtn').setAttribute('aria-label', 'Shuffle the canvas. Now: ' + TH.label);
}
$('stages').addEventListener('click', e => { const t = e.target.closest('button'); if (!t) return; AU.init(); AU.ui(); diff = t.dataset.d; store.diff = diff; save(); renderStages(); });
// the menu shot: your blob and the holy water side by side at your spawn, facing a camera that looks in across the canvas
const hero = { yaw: 0, mx: 0, mz: 0 }, heroOff = { x: 0, y: 0 }, sideMQ = window.matchMedia ? matchMedia('(min-width:860px) and (min-aspect-ratio:1/1)') : { matches: false };
let heroK = 0, heroT = 0, heroDist = 5.5;
const heroFov = () => camera.aspect < 0.8 ? 50 : 38;
function heroSees(ax, ay, az, bx, by, bz) {
  const n = Math.max(1, Math.ceil(Math.hypot(bx - ax, bz - az) / 0.3));
  for (let k = 0; k <= n; k++) {
    const t = k / n, x = ax + (bx - ax) * t, y = ay + (by - ay) * t, z = az + (bz - az) * t;
    for (const b of BOXES) { const tree = TH.id === 'garden' && b[7] === 'column', pad = tree ? (b[1] - b[0]) * 1.6 + 0.3 : 0.25; if (y > b[4] - 0.2 && y < b[5] + (tree ? 2.8 : 0.25) && inR(x, z, b, pad)) return false; }
    for (const r of RAMPS) if (inR(x, z, r, 0.1) && y < rampH(r, clamp(x, r[0], r[1]), clamp(z, r[2], r[3])) + 0.2) return false;
  }
  return true;
}
function menuPose() {
  const f0 = START.yaw + Math.PI; let best = null;
  outer: for (const da of [0, 0.4, -0.4, 0.8, -0.8, 1.2, -1.2, 1.6, -1.6, 2.1, -2.1, 2.6, -2.6, Math.PI]) {
    const a = f0 + da, dx = Math.sin(a), dz = Math.cos(a), rx = Math.cos(a), rz = -Math.sin(a);
    for (const sd of [1, -1]) {
      const hx = START.x + rx * 0.95 * sd - dx * 0.45, hz = START.z + rz * 0.95 * sd - dz * 0.45;
      if (surfaceUnder(hx, hz, 0.3) !== 0 || blockedAt(hx, hz, 0)) continue;
      const mx = (START.x + hx) / 2, mz = (START.z + hz) / 2, D = 7.5, cx = mx + dx * D, cz = mz + dz * D, cy = 0.42 + D * 0.24;
      if (!heroSees(cx, cy, cz, START.x, 0.45, START.z) || !heroSees(cx, cy, cz, hx, 0.45, hz)) continue;
      best = { a, hx, hz, sd }; break outer;
    }
  }
  if (!best) best = { a: f0, hx: START.x + Math.cos(f0) * 0.95, hz: START.z - Math.sin(f0) * 0.95, sd: 1 };
  P.x = START.x; P.z = START.z; P.y = 0; P.yaw = best.a + 0.22 * best.sd;
  H.x = best.hx; H.z = best.hz; H.y = 0; H.yaw = best.a - 0.3 * best.sd;
  hero.yaw = best.a; hero.mx = (P.x + H.x) / 2; hero.mz = (P.z + H.z) / 2; heroT = 0;
}
// where the pair should sit on screen (the space the logo and the controls leave), and how close the camera needs to be
function heroFrame(rdt) {
  heroT -= rdt; if (heroT > 0) return heroDist; heroT = 0.4;
  const r = stage.getBoundingClientRect(), d = menu.querySelector('.dock').getBoundingClientRect(), l = $('logo').getBoundingClientRect(), W = r.width, Hh = r.height;
  if (!(d.height > 0)) return heroDist;
  const side = sideMQ.matches; let tx, ty, freeW;
  if (side) { const x0 = Math.max(d.right, l.right) - r.left + 24; tx = (x0 + W) / 2; ty = Hh * 0.56; freeW = W - x0; }
  else { const y0 = l.bottom - r.top, y1 = d.top - r.top; tx = W / 2; ty = clamp(y0 + (y1 - y0) * 0.56, Hh * 0.25, Hh * 0.72); freeW = W; }
  heroOff.x = W / 2 - tx; heroOff.y = Hh / 2 - ty;
  const tv = Math.tan(heroFov() * Math.PI / 360), asp = W / Math.max(1, Hh);
  const dW = 1.15 / (tv * asp * Math.min(1, freeW / W) * 0.8), dH = 0.78 / (2 * tv * (side ? 0.24 : 0.17));
  heroDist = clamp(Math.max(dW, dH), 3.2, 9);
  return heroDist;
}
""")

# shuffle and menu entry pose the pair for the menu shot
rep("""  if (building || state !== 'menu') return; freshMap(); resetRun(); decorate();
  P.x = START.x; P.z = START.z; P.yaw = START.yaw; H.x = CSTART.x; H.z = CSTART.z; H.yaw = CSTART.yaw;
  const n = $('cvName'); n.textContent = TH.label; kick(n, 'pop');""",
"""  if (building || state !== 'menu') return; freshMap(); resetRun(); decorate(); menuPose();
  renderStages(); kick($('cvName'), 'pop');""")
rep("""  state = 'menu'; menu.hidden = false; end.hidden = true; pauseEl.hidden = true; hud.classList.add('off'); hintEl.classList.remove('on'); $('vig').className = 'vig';
  if (mapUsed) freshMap();
  resetRun(); decorate(); renderStages(); AU.music('menu');
  P.x = START.x; P.z = START.z; P.yaw = START.yaw; H.x = CSTART.x; H.z = CSTART.z; H.yaw = CSTART.yaw;""",
"""  state = 'menu'; menu.hidden = false; end.hidden = true; pauseEl.hidden = true; howModal.hidden = true; hud.classList.add('off'); hintEl.classList.remove('on'); $('vig').className = 'vig';
  if (mapUsed) freshMap();
  resetRun(); decorate(); renderStages(); AU.music('menu'); menuPose(); heroT = 0;""")
rep("""  AU.init(); AI = AI_LV[diff]; mapUsed = true; resetRun(); gyCam = 0; state = 'play'; menu.hidden = true; end.hidden = true; pauseEl.hidden = true; hud.classList.remove('off');""",
    """  AU.init(); AI = AI_LV[diff]; mapUsed = true; resetRun(); gyCam = 0; state = 'play'; menu.hidden = true; end.hidden = true; pauseEl.hidden = true; howModal.hidden = true; hud.classList.remove('off');""")
rep("banner('Paint it red!', TH.label, true);", "banner('Paint it ' + colorOf().name.toLowerCase() + '!', TH.label, true);")
rep("""  const [a, b] = fmtPair(teamCov(0), teamCov(1));
  $('pauseNote').textContent = 'You ' + a + ' · Holy water ' + b + ' · ' + fmtClock(matchLeft) + ' left'; pauseEl.hidden = false;""",
    """  const [a, b] = fmtPair(teamCov(0), teamCov(1));
  $('pauseYou').textContent = a; $('pauseCpu').textContent = b; $('pauseClock').textContent = fmtClock(matchLeft) + ' left'; pauseEl.hidden = false;""")

i = s.index("const PT_A = ['Nocturne'"); j = s.index("const uiClick = fn =>")
s = s[:i] + r"""const PT_A = ['Nocturne', 'Requiem', 'Study', 'Elegy', 'Sonata', 'Midnight', 'Duel', 'Etude'];
function showEnd(img) {
  const { you, cpu, win, time } = endInfo, n = store.runs || 1, lv = DIFFS.find(d => d[0] === diff), w = colorOf().words;
  const t = $('endTitle'); t.textContent = win > 0 ? 'You win!' : win < 0 ? 'Holy water wins' : 'Draw'; t.className = 'rtitle' + (win < 0 ? ' lose' : win === 0 ? ' draw' : '');
  const [a, b] = fmtPair(you, cpu); $('endPct').textContent = a; $('endPctC').textContent = b;
  $('chipYou').classList.toggle('win', win > 0); $('chipCpu').classList.toggle('win', win < 0);
  const pair = (y, c) => '<span class="y">' + y + '</span><em>-</em><span class="c">' + c + '</span>';
  $('endStats').innerHTML = '<div class="stat"><b>' + pair(P.kos, H.kos) + '</b><span>Knockouts</span></div><div class="stat"><b>' + pair(H.flats, P.flats) + '</b><span>Flattened</span></div><div class="stat"><b>' + ((store.bestCov && store.bestCov[diff]) || 0) + '%</b><span>Best on ' + lv[1] + '</span></div>';
  $('endPill').hidden = !endInfo.newBest;
  $('frame').hidden = !img; if (img) $('paintImg').src = img;
  const PT_B = ['in ' + w[0] + ' and Blue', 'in ' + w[1], 'in Blood and Holy Water', 'for One Fang', 'in Moonlight and ' + w[2], 'in ' + w[2]];
  $('pTitle').textContent = PT_A[(n * 7) % PT_A.length] + ' ' + PT_B[(n * 3) % PT_B.length] + ', No. ' + n;
  $('pMeta').textContent = TH.label + ', ' + fmtTime(time);
  end.dataset.next = '';
  end.hidden = false;
  setTimeout(() => $('endBtn').focus({ preventScroll: true }), 30);
}
""" + s[j:]

# how to play: a card over the menu
rep("$('quitBtn').addEventListener('click', uiClick(showMenu));", """$('quitBtn').addEventListener('click', uiClick(showMenu));
const howModal = $('howModal');
function openHow() { if (state !== 'menu') return; paintHow(); howModal.hidden = false; setTimeout(() => $('howClose').focus({ preventScroll: true }), 30); }
function closeHow() { if (howModal.hidden) return; howModal.hidden = true; $('howBtn').focus({ preventScroll: true }); }
$('howBtn').addEventListener('click', uiClick(openHow));
$('howClose').addEventListener('click', uiClick(closeHow));
howModal.addEventListener('click', e => { if (e.target === howModal) closeHow(); });
pauseEl.addEventListener('click', e => { if (e.target === pauseEl) { AU.ui(); resume(); } });""")
rep("""window.addEventListener('keydown', e => {
  const k = e.key; AU.init();""", """window.addEventListener('keydown', e => {
  const k = e.key; AU.init();
  if (!howModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeHow(); } return; }""")

# start up in your saved color
rep("showMenu();\nrequestAnimationFrame(frame);\n})();", "colorId = PALETTE.some(p => p.id === store.color) ? store.color : 'red'; renderSwatches(); setColor(colorId);\nshowMenu();\nrequestAnimationFrame(frame);\n})();")

# ---------- the menu camera ----------
rep("  if (state === 'menu') { const a = Math.sin(clock * 0.07) * 0.22; dPos.set(Math.sin(a) * 52, 15, -Math.cos(a) * 52); dLook.set(Math.sin(a) * 12, -8.5, -Math.cos(a) * 12); }",
    "  if (state === 'menu') { const dist = heroFrame(rdt), a = hero.yaw + Math.sin(clock * 0.31) * 0.06; dPos.set(hero.mx + Math.sin(a) * dist, 0.42 + dist * 0.24 + Math.sin(clock * 0.47) * 0.04, hero.mz + Math.cos(a) * dist); dLook.set(hero.mx, 0.4, hero.mz); }")
rep("const k = 1 - Math.exp(-rdt * (playing ? 12 : state === 'menu' ? 1.4 : 2.2));", "const k = 1 - Math.exp(-rdt * (playing ? 12 : 2.2));")
rep("  const fovT = baseFov + (playing ?", "  const fovT = state === 'menu' ? heroFov() : baseFov + (playing ?")
rep("  sky.position.copy(camera.position);\n", """  sky.position.copy(camera.position);
  // in the menu the shot is framed into the space the logo and the controls leave
  heroK += ((state === 'menu' ? 1 : 0) - heroK) * (1 - Math.exp(-rdt * 3));
  if (heroK > 0.003) { const vw = canvas.clientWidth || 1, vh = canvas.clientHeight || 1; camera.setViewOffset(vw, vh, heroOff.x * heroK, heroOff.y * heroK, vw, vh); }
  else if (camera.view && camera.view.enabled) camera.clearViewOffset();
  if (menuReact > 0) menuReact = Math.max(0, menuReact - rdt);
""")
open(F, 'w').write(s)
print('ok')
