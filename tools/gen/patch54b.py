import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ================= the second CPU's body, built like the holy water's =================
rep("const VP = { root: drop, body, mat: dropMat, U: gooU, look, shadow: shadowBlob, flatK: 0, gk: 1 }, VC = {", "const VP = { root: drop, body, mat: dropMat, U: gooU, look, shadow: shadowBlob, flatK: 0, gk: 1 }, VC = {")
i = s.index("const VP = { root: drop, body, mat: dropMat, U: gooU, look, shadow: shadowBlob, flatK: 0, gk: 1 }, VC = {"); j = s.index("\n", i) + 1
s = s[:j] + r"""// a CPU's whole look in one place: the holy water's is made from the parts above, wolfsbane gets its own copy
const LH = { D: H, drop: cDrop, body: cBody, mat: cMat, xrayMat: cXrayMat, U: gooU2, eyes: cEyes, mouth: cMouth, glint: cGlint, glint2: cGlint2, shadow: cShadow, look: lookC, blinkT: 1.3, blinkK: 0, V: VC, stars: starsC, warn: cWarn, warnFill: cWarnFill, foeMark, mark: cMark, col: COL_HOLY };
function makeCpuLook(D, color) {
  const U = { gRoll: { value: 0 }, gT: { value: 0 }, gWob: { value: 1 }, gSpd: { value: 0 }, gLean: { value: 0 }, gSquash: { value: 0 }, gRise: { value: 0 }, gDrop: { value: 0 }, gFlat: { value: 1 } };
  const drop = new THREE.Group(), body = new THREE.Group(); drop.add(body);
  const xrayMat = gooify(new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.55, depthWrite: false, depthFunc: THREE.GreaterDepth }), false, 'goo-xray', U);
  const xr = new THREE.Mesh(blobG, xrayMat); xr.renderOrder = 30; body.add(xr);
  const mat = gooify(toon(color, { transparent: true }), false, undefined, U); const mesh = new THREE.Mesh(blobG, mat); mesh.castShadow = true; mesh.renderOrder = 32; body.add(mesh);
  const hull = new THREE.Mesh(blobG, gooify(new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), true, undefined, U)); hull.renderOrder = 31; body.add(hull);
  const glint = new THREE.Mesh(glintG, cGlint.material), glint2 = new THREE.Mesh(glint2G, cGlint.material); glint.renderOrder = glint2.renderOrder = 33; body.add(glint); body.add(glint2);
  const eyes = []; [-1, 1].forEach(sd => { const { e, pu } = makeEye(body); const br = new THREE.Mesh(cEyes[0].br.geometry, eyeB); br.renderOrder = 34; body.add(br); eyes.push({ e, pu, br, sd, base: new THREE.Vector3(sd * 0.37, 0.45, 0.8).normalize() }); });
  const mouth = new THREE.Mesh(cMouth.geometry, eyeB); mouth.rotation.z = Math.PI; mouth.renderOrder = 34; body.add(mouth);
  drop.visible = false; scene.add(drop);
  const shadow = new THREE.Mesh(cShadow.geometry, cShadow.material); shadow.rotation.x = -Math.PI / 2; shadow.visible = false; scene.add(shadow);
  const warnCol = new THREE.Color(color).lerp(COL_WHITE, 0.5);
  const warnFill = new THREE.Mesh(cWarnFill.geometry, cWarnFill.material.clone()); warnFill.material.color.copy(warnCol); warnFill.rotation.x = -Math.PI / 2; warnFill.visible = false; scene.add(warnFill);
  const warn = new THREE.Mesh(cWarn.geometry, cWarn.material.clone()); warn.material.color.copy(warnCol); warn.rotation.x = -Math.PI / 2; warn.renderOrder = 6; warn.visible = false; scene.add(warn);
  const fm = new THREE.Mesh(foeMark.geometry, foeMark.material); fm.rotation.x = -Math.PI / 2; fm.visible = false; scene.add(fm);
  const mark = new THREE.Sprite(new THREE.SpriteMaterial({ map: markTexs['!'], depthTest: false, transparent: true, fog: false })); mark.renderOrder = 950; mark.visible = false; scene.add(mark);
  const look = { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 };
  return { D, drop, body, mat, xrayMat, U, eyes, mouth, glint, glint2, shadow, look, blinkT: 1.7, blinkK: 0, V: { root: drop, body, mat, U, look, shadow, flatK: 0, gk: 1 }, stars: makeStars(), warn, warnFill, foeMark: fm, mark, col: new THREE.Color(color) };
}
const L2 = makeCpuLook(H2, TEAMS[2].wet);
H.look = LH; H2.look = L2;
// a CPU's face: stern brows, a smug smile when it's ahead, wide eyes when it's in trouble
function placeFaceCpu(L, dt) {
  const D = L.D, U = L.U, sq = U.gSquash.value;
  L.blinkT -= dt; if (L.blinkT <= 0) { L.blinkK = 0.12; L.blinkT = 2 + Math.random() * 3; } if (L.blinkK > 0) L.blinkK -= dt;
  const ahead = teamCov(D.team) > bestFoeCov(D), hunting = D.ai && D.ai.mode === 'hunt', scared = D.flatT > 0 || D.stunT > 0 || D.exposed || D.st === 'ko';
  for (const it of L.eyes) {
    const p = gooJS(it.base, U); it.e.position.copy(p).multiplyScalar(1.02);
    let sy = 1.1 * (1 - sq * 0.35); if (L.blinkK > 0) sy *= 0.12; else if (hunting) sy *= 0.7;
    it.e.scale.set(1, sy, 0.55); it.pu.visible = L.blinkK <= 0;
    it.pu.position.copy(p).multiplyScalar(1.07).add(tv1.set(-L.look.lean * 0.07, -0.02, 0.02)); it.pu.scale.setScalar(scared ? 0.7 : 1);
    it.br.position.copy(p).multiplyScalar(1.05).add(tv1.set(0, 0.24, 0.02)); it.br.rotation.set(0, 0, it.sd * (hunting ? -0.45 : scared ? 0.35 : -0.15));
  }
  const mp = gooJS(mouthBase, U).multiplyScalar(1.03); L.mouth.position.copy(mp).add(tv1.set(0, 0.06, 0)); L.mouth.scale.set(1, ahead ? 1.2 : scared ? -0.8 : 0.9, 1);
  L.glint.position.copy(gooJS(tv2.set(-0.42, 0.62, 0.55).normalize(), U)); L.glint.scale.set(1, 0.7, 0.4);
  L.glint2.position.copy(gooJS(tv2.set(-0.62, 0.32, 0.6).normalize(), U)); L.glint2.scale.set(1, 1, 0.5);
}
// a CPU each frame: body, face, color, its pound's warning ring, the aim ring when it lines up on you, and the "!" when it spots you
function cpuLook(L, dt, rdt, ke, kf, playing) {
  const D = L.D;
  if (L.drop.visible) {
    blobVisual(D, L.V, dt, ke, kf); placeFaceCpu(L, dt); placeStars(L.stars, D, L.V);
    tmpCol2.copy(L.col); giantTint(D, tmpCol2); if (D.exposed && D.st === 'play') tmpCol2.lerp(COL_WHITE, 0.35 + 0.3 * Math.sin(clock * 28));
    if (D.dilT > 0) tmpCol2.lerp(COL_WHITE, 0.5 * Math.min(1, D.dilT * 2));
    if (D.dry && D.st === 'play') tmpCol2.lerp(COL_DULL, 0.74);
    if (D.rollT > 0 && D.st === 'play') tmpCol2.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));
    L.mat.color.copy(tmpCol2); L.mat.emissive.copy(tmpCol2).multiplyScalar(0.22);
    if (D.slam) { L.warn.visible = true; const hc = slamCenter(D), gy = hc.y !== undefined && hc !== D ? hc.y : surfaceUnder(D.x, D.z, D.y + 0.3, true); L.warn.position.set(hc.x, (gy > -Infinity ? gy : 0) + 0.12, hc.z); L.warn.scale.setScalar((slamRadius(D) + PR) * (0.94 + 0.06 * Math.sin(clock * 20))); L.warnFill.visible = true; L.warnFill.position.copy(L.warn.position); L.warnFill.position.y += 0.005; L.warnFill.scale.setScalar(Math.max(0.01, (slamRadius(D) + PR) * clamp(D.slamT / Math.max(0.2, D.slamEta), 0, 1))); } else { L.warn.visible = false; L.warnFill.visible = false; }
  } else { L.warn.visible = false; L.warnFill.visible = false; L.stars.visible = false; }
  const atYou = mode !== 'trio' || other(D) === P;
  { const aim = playing && atYou && D.st === 'play' && D.charging && D.ai && D.ai.plan && (D.ai.plan.kind === 'attack' || D.ai.plan.kind === 'shove'); L.foeMark.visible = !!aim; if (aim) { L.foeMark.position.set(D.x, D.y + 0.06, D.z); L.foeMark.scale.setScalar(1 + 0.6 * clamp(D.charge, 0, 1) + 0.08 * Math.sin(clock * 18)); } }
  const al = D.ai && D.ai.alert;
  if (al && al.t > 0 && playing && atYou && L.drop.visible && D.st !== 'ko') {
    if (!al.shown) { al.shown = true; if (al.k === '!' && Math.hypot(D.x - P.x, D.z - P.z) < 24) AU.spot(); }
    al.t -= rdt; if (L.mark.material.map !== markTexs[al.k]) { L.mark.material.map = markTexs[al.k]; L.mark.material.needsUpdate = true; }
    const pop = Math.min(1, (1.1 - al.t) * 7), fade = Math.min(1, al.t * 3);
    L.mark.visible = true; L.mark.position.set(D.x, D.y + 1.6 - (1 - pop) * 0.35, D.z); L.mark.scale.setScalar(0.95 * (0.6 + 0.4 * pop)); L.mark.material.opacity = fade;
  } else L.mark.visible = false;
}
""" + s[j:]
bi = s.index("  if (cDrop.visible) {\n    blobVisual(H, VC, dt, ke, kf);"); be = s.index("  } else cMark.visible = false;\n", bi) + len("  } else cMark.visible = false;\n")
s = s[:bi] + "  cpuLook(LH, dt, rdt, ke, kf, playing); cpuLook(L2, dt, rdt, ke, kf, playing);\n" + s[be:]
# the camera keeps whichever rival is closest in frame
rep("    const fdx = H.x - P.x, fdz = H.z - P.z, fd = Math.hypot(fdx, fdz), foeK = H.st === 'play' && P.st === 'play' ? clamp(1 - (fd - 5) / 9, 0, 1) : 0;",
    "    const F = other(P), fdx = F.x - P.x, fdz = F.z - P.z, fd = Math.hypot(fdx, fdz), foeK = F.st === 'play' && P.st === 'play' ? clamp(1 - (fd - 5) / 9, 0, 1) : 0;")
rep("vig.classList.toggle('danger', ((dangerK > 0 && P.st === 'play') || (H.slam && (hc => Math.hypot(hc.x - P.x, hc.z - P.z))(slamCenter(H)) < slamRadius(H) + PR + 1)) && !burning);",
    "vig.classList.toggle('danger', ((dangerK > 0 && P.st === 'play') || foes(P).some(F => F.slam && (hc => Math.hypot(hc.x - P.x, hc.z - P.z))(slamCenter(F)) < slamRadius(F) + PR + 1)) && !burning);")
rep("const hide = [orb.g, orb.ring, drop, shadowBlob, cDrop, cShadow, cWarn, cMark,", "const hide = [orb.g, orb.ring, drop, shadowBlob, cDrop, cShadow, cWarn, cMark, L2.drop, L2.shadow, L2.warn, L2.warnFill, L2.mark, L2.foeMark, L2.stars, starsP, starsC,")
rep("  const S = 1024; if (!snapRT) snapRT = new THREE.WebGLRenderTarget(S, S);", "  const S = 1024; if (!snapRT) snapRT = new THREE.WebGLRenderTarget(S, S);\n  snapCam.left = snapCam.bottom = -ARENA - 1.5; snapCam.right = snapCam.top = ARENA + 1.5; snapCam.updateProjectionMatrix();")

# ================= the menu: pick a mode =================
rep('      <div class="seg" id="stages" role="group" aria-label="How good the holy water is"></div>',
    '      <div class="seg" id="modes" role="group" aria-label="Game mode"></div>\n      <div class="seg" id="stages" role="group" aria-label="How good the CPUs are"></div>\n      <p class="snote" id="soloNote" hidden></p>')
rep("""function renderStages() {
  const el = $('stages');""", """function renderModes() {
  const el = $('modes');
  if (!el.children.length) { let h = ''; for (const [k, name, tag] of MODES) h += '<button type="button" data-m="' + k + '" title="' + tag + '">' + name + '</button>'; el.innerHTML = h; }
  for (const b of el.children) b.setAttribute('aria-pressed', String(b.dataset.m === mode));
  $('stages').hidden = mode === 'solo'; const sn = $('soloNote'); sn.hidden = mode !== 'solo';
  if (mode === 'solo') { const best = (store.bestCov && store.bestCov.solo) || 0; sn.textContent = 'Cover as much as you can in 60 seconds.' + (best ? ' Your best is ' + best + '%.' : ''); }
  $('startBtn').textContent = 'Play';
}
// switching mode builds a canvas for it (a 3-way one is bigger) and changes who's standing in the menu
$('modes').addEventListener('click', e => { const t = e.target.closest('button'); if (!t || t.dataset.m === mode || building) return; AU.init(); AU.ui(); mode = t.dataset.m; store.mode = mode; save(); applyMode(); renderModes(); if (state === 'menu') { freshMap(); resetRun(); decorate(); menuPose(); renderStages(); } });
function renderStages() {
  const el = $('stages');""")
rep("  state = 'menu'; menu.hidden = false;", "  state = 'menu'; applyMode(); renderModes(); menu.hidden = false;")
# in the menu shot: the holy water beside you, wolfsbane on your other side in a 3-way, nobody else in solo
rep("  H.x = best.hx; H.z = best.hz; H.y = 0; H.yaw = best.a - 0.3 * best.sd;\n  hero.yaw = best.a; hero.mx = (P.x + H.x) / 2; hero.mz = (P.z + H.z) / 2; heroT = 0;",
    """  H.x = best.hx; H.z = best.hz; H.y = 0; H.yaw = best.a - 0.3 * best.sd;
  const rx = Math.cos(best.a), rz = -Math.sin(best.a), dx = Math.sin(best.a), dz = Math.cos(best.a);
  H2.x = START.x - rx * 0.95 * best.sd - dx * 0.45; H2.z = START.z - rz * 0.95 * best.sd - dz * 0.45; H2.y = 0; H2.yaw = best.a + 0.3 * best.sd;
  if (mode === 'trio' && (surfaceUnder(H2.x, H2.z, 0.3) !== 0 || blockedAt(H2.x, H2.z, 0))) { H2.x = START.x - dx * 1.4; H2.z = START.z - dz * 1.4; }
  hero.yaw = best.a; hero.mx = mode === 'solo' ? P.x : mode === 'trio' ? (H.x + H2.x) / 2 * 0.5 + P.x * 0.5 : (P.x + H.x) / 2; hero.mz = mode === 'solo' ? P.z : mode === 'trio' ? (H.z + H2.z) / 2 * 0.5 + P.z * 0.5 : (P.z + H.z) / 2; heroT = 0;""")
rep("  const dW = 1.15 / (tv * asp * Math.min(1, freeW / W) * (side ? 0.8 : 0.92))", "  const dW = (mode === 'trio' ? 1.65 : mode === 'solo' ? 0.75 : 1.15) / (tv * asp * Math.min(1, freeW / W) * (side ? 0.8 : 0.92))")
rep("banner('Paint it ' + colorOf().name.toLowerCase() + '!', TH.label, true);", "banner('Paint it ' + colorOf().name.toLowerCase() + '!', mode === 'solo' ? '60 seconds' : TH.label, true);")
rep("for (let k = 0; k < 4; k++) {\n    const n = open[Math.floor(r() * open.length)], pts = [];", "for (let k = 0; k < 4; k++) {\n    const n = open[Math.floor(r() * open.length)], pts = [];")
rep("    paintPath(u => pts[Math.min(pts.length - 1, Math.floor(u * (pts.length - 1)))], -7 + k, k % 2);", "    paintPath(u => pts[Math.min(pts.length - 1, Math.floor(u * (pts.length - 1)))], -7 + k, mode === 'solo' ? 0 : k % (mode === 'trio' ? 3 : 2));")
rep("i % 3 === 0 ? 0 : -8, false, false, i % 2); }", "i % 3 === 0 ? 0 : -8, false, false, mode === 'solo' ? 0 : i % (mode === 'trio' ? 3 : 2)); }")
# startup: the saved mode decides the first canvas's size
rep("colorId = PALETTE.some(p => p.id === store.color) ? store.color : 'red'; renderSwatches(); setColor(colorId);", "colorId = PALETTE.some(p => p.id === store.color) ? store.color : 'red'; renderSwatches(); setColor(colorId); applyMode(); if (ARENA !== 26.4) mapUsed = true;")

# ================= wolfsbane's color steps aside if you pick purple =================
rep("  partPool(colMat(c.hex));\n", """  partPool(colMat(c.hex));
  const wolf = c.id === 'purple' ? { wet: 0x19C9A6, dry: 0x0E6B58, css: '#19C9A6', hi: '#7FE8D3' } : { wet: 0x8E5CFF, dry: 0x46297F, css: '#8E5CFF', hi: '#C4A8FF' };
  TEAMS[2].wet = wolf.wet; TEAMS[2].dry = wolf.dry; TEAMS[2].css = wolf.css; TEAM_COLS[2].setHex(wolf.wet); paintUniforms.uWetA.value[2].setHex(wolf.wet); paintUniforms.uDryA.value[2].setHex(wolf.dry);
  teamMats[2].color.setHex(wolf.wet); crownMats[2].color.setHex(wolf.wet); crownMats[2].emissive.setHex(wolf.wet).multiplyScalar(0.18); L2.col.setHex(wolf.wet); L2.xrayMat.color.setHex(wolf.wet);
  const wc = new THREE.Color(wolf.wet).lerp(COL_WHITE, 0.5); L2.warn.material.color.copy(wc); L2.warnFill.material.color.copy(wc); partPool(colMat(wolf.wet));
  document.documentElement.style.setProperty('--wolf', wolf.css); document.documentElement.style.setProperty('--wolf-hi', wolf.hi);
""")

# ================= markup and styles for the extra rival =================
rep('<div class="pchip cpu" id="chipCpu"><i></i><div><b id="endPctC">0%</b><span>Holy water</span></div>',
    '<div class="pchip cpu" id="chipCpu"><i></i><div><b id="endPctC">0%</b><span id="chipCpuName">Holy water</span></div>')
rep('<span class="pill" id="endPill" hidden>New best</span>', '<div class="pchip cpu2" id="chipCpu2" hidden><i></i><div><b id="endPctC2">0%</b><span>Wolfsbane</span></div>' + s[s.index('<svg viewBox="0 0 30 24"'):s.index('</svg>', s.index('<svg viewBox="0 0 30 24"')) + 6] + '</div>\n        <span class="pill" id="endPill" hidden>New best</span>')
rep("  --holy-hi:#7CC4FF;", "  --holy-hi:#7CC4FF;\n  --wolf:#8E5CFF;\n  --wolf-hi:#C4A8FF;")
rep(".vsn.cpu{text-align:left;color:var(--holy-hi)}", """.vsn.cpu{text-align:left;color:var(--holy-hi)}
.vsr{display:flex;align-items:center;gap:8px;justify-content:flex-start}
.vsn.cpu2{display:none;color:var(--wolf-hi)}
.hud.trio .vsn{font-size:22px}
.hud.trio .vsn.cpu2{display:block}
.hud.solo .vsn.cpu{color:var(--gold);font-size:20px}
.hud.solo .vsn.cpu::before{content:"Best ";font:800 12px/1 var(--font-ui);color:var(--muted);vertical-align:3px}
.hud.solo .tug .tYou{border-radius:99px}""")
rep(".tug .tCpu{right:0;background:var(--holy)}", ".tug .tCpu{right:0;background:var(--holy)}\n.tug .tCpu2{right:0;width:0;background:var(--wolf);display:none}\n.hud.trio .tug .tCpu2{display:block}")
rep(".foeptr.warn b{border-bottom-color:#FF3B5C}", ".foeptr.warn b{border-bottom-color:#FF3B5C}\n.foeptr.two i{background:var(--wolf)}")
rep(".pchip.cpu b{color:var(--holy-hi)}", ".pchip.cpu b{color:var(--holy-hi)}\n.pchip.cpu2 i{background:var(--wolf)}\n.pchip.cpu2 b{color:var(--wolf-hi)}\n.pchip.best i{background:var(--gold)}\n.pchip.best b{color:var(--gold)}\n.scores:has(#chipCpu2:not([hidden])) .pchip{padding-top:7px;padding-bottom:7px}\n.scores:has(#chipCpu2:not([hidden])) .pchip b{font-size:clamp(24px,7vw,30px)}")
rep(".stat b .c{color:var(--holy-hi)}", ".stat b .c{color:var(--holy-hi)}\n.stat b .m{color:var(--muted)}")
rep(".rtitle.lose{color:var(--holy-hi)}", ".rtitle.lose{color:var(--holy-hi)}\n.rtitle.lose2{color:var(--wolf-hi)}")
rep(".note{margin:0;font-size:14px;", ".snote{margin:0;min-height:42px;display:grid;place-items:center;text-align:center;font-size:14px;line-height:1.35;font-weight:700;color:var(--muted);text-wrap:balance}\n.note{margin:0;font-size:14px;")
open(F, 'w').write(s)
print('ok part 2')
