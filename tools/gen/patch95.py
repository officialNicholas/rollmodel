import json
p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
std = json.load(open('std/standard.json'))
# 1. the standard stage, baked so it never changes
rep("let stageSel = store.stage === 'standard' ? 'standard' : 'season';",
    "let stageSel = store.stage === 'standard' ? 'standard' : 'season';\n// The Studio: the standard stage. Laid out once and kept as data, so it stays exactly the same through every season and update\nconst STANDARD = " + json.dumps(std, separators=(',', ':')) + ";")
rep("function freshMap() { genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id }); mapUsed = false; }",
    """function freshMap() { if (stageSel === 'standard') loadStandard(); else genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id, themes: SEASON.themes }); mapUsed = false; }
function loadStandard() {
  const S = STANDARD[mode === 'trio' ? 'trio' : 'duel'], t0 = performance.now(); GEN.n++;
  genOpt = { easy: false, avoid: null, themes: null };
  applyLayout({ theme: 'studio', holes: S.holes, boxes: S.boxes, ramps: S.ramps, clouds: S.clouds }); rebuildSamples(); buildNav();
  POTS.length = 0; RIVALS.length = 0; POWER_SPOTS.length = 0; COF_SPOTS.length = 0;
  POTS.push(...S.pots.map(a => a.slice())); RIVALS.push(...S.rivals.map(a => a.slice())); POWER_SPOTS.push(...S.powers.map(a => [a[0], a[1], a[2], a[3] || undefined]));
  Object.assign(START, S.start); Object.assign(CSTART, S.cstart); Object.assign(CSTART2, S.cstart2);
  const { core } = navCore(rng(4242)), nearSpawn = n => [START, CSTART, CSTART2].some(q => Math.hypot(n.x - q.x, n.z - q.z) < 3);
  for (const n of NAV.nodes) if (core[n.id] && cofOK(n) && !nearSpawn(n)) COF_SPOTS.push([n.x, n.h, n.z, tuckOf(n)]);
  Object.assign(GEN, { seed: 202, sym: S.sym, arch: S.arch, tries: 1, fallback: false, easy: false, avoid: null, themes: null, key: mapKey(), std: true });
  rebuildStage(); GEN.ms = performance.now() - t0;
}""")
rep("fallback: false, easy, avoid, themes, key: mapKey() });", "fallback: false, easy, avoid, themes, key: mapKey(), std: false });")
rep("fallback: true, easy, avoid, themes, key: mapKey() });", "fallback: true, easy, avoid, themes, key: mapKey(), std: false });")
rep("  const op = { easy: GEN.easy, avoid: GEN.avoid }; setTimeout(() => { genWorld(sd, op); mapUsed = false; building = false; start(); }, 60);",
    "  const std = !!GEN.std, op = { easy: GEN.easy, avoid: GEN.avoid, themes: GEN.themes }; setTimeout(() => { if (std) loadStandard(); else genWorld(sd, op); mapUsed = false; building = false; start(); }, 60);")
rep("if (building) return; const sd = GEN.seed; building = true; AU.init(); menu.hidden = true; end.hidden = true; pauseEl.hidden = true; hud.classList.add('off'); banner('Same canvas');",
    "if (building) return; const sd = GEN.seed; building = true; AU.init(); menu.hidden = true; end.hidden = true; pauseEl.hidden = true; hud.classList.add('off'); banner(GEN.std ? TH.label : 'Same canvas');")
rep("  if (!mapUsed && GEN.easy !== easyOn()) mapUsed = true; // the canvas waiting in the menu was made for the other difficulty",
    "  if (!mapUsed && GEN.key !== mapKey()) mapUsed = true; // the canvas waiting in the menu was made for another stage, mode or difficulty\n  pickRivalNames();")
rep("  if (mapUsed) { building = true; AU.init(); menu.hidden = true; end.hidden = true; pauseEl.hidden = true; banner('New canvas');",
    "  if (mapUsed) { building = true; AU.init(); menu.hidden = true; end.hidden = true; pauseEl.hidden = true; banner(stageSel === 'standard' ? STD_LABEL : 'New canvas');")
rep("const was = easyOn(); diff = t.dataset.d; store.diff = diff; save();\n  if (state === 'menu' && !building && easyOn() !== was) {",
    "diff = t.dataset.d; store.diff = diff; save();\n  if (state === 'menu' && !building && GEN.key !== mapKey()) {")
# 2. the stage picker
rep('<div class="seg" id="stages" role="group" aria-label="How good the CPUs are"></div>',
    '<div class="seg" id="stages" role="group" aria-label="How good the CPUs are"></div>\n      <div class="seg two" id="stagePick" role="group" aria-label="Stage"><button type="button" data-s="standard">The Studio</button><button type="button" data-s="season"><span class="sdot" aria-hidden="true"></span>Halloween</button></div>')
rep(".seg{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:4px;background:var(--line);border-radius:16px}",
    ".seg{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:4px;background:var(--line);border-radius:16px}\n.seg.two{grid-template-columns:repeat(2,1fr)}\n.sdot{display:inline-block;width:9px;height:9px;margin-right:7px;border-radius:50%;background:var(--pumpkin);box-shadow:0 0 0 2px rgba(255,138,31,.25);vertical-align:1px}\n.season{display:inline-flex;align-items:center;gap:8px;margin-top:-.2em;padding:6px 13px;border-radius:99px;background:rgba(18,10,36,.72);border:2px solid var(--pumpkin);color:var(--bone);font:800 14px/1 var(--font-ui);letter-spacing:.01em;box-shadow:0 3px 0 var(--line)}\n.season b{font-weight:800;color:var(--pumpkin)}")
rep("  --sky:#120A24;", "  --sky:#120A24;\n  --pumpkin:#FF8A1F;")
rep('<span class="cw" id="logoWord">Model</span></span></h1>', '<span class="cw" id="logoWord">Model</span></span><span class="season" id="seasonTag"><b>Season 1</b>Halloween</span></h1>')
rep('<h1 class="logo paint" id="logo" aria-label="Roll Model">', '<h1 class="logo paint" id="logo">')
rep("function renderStages() {\n  const el = $('stages');",
    "const STD_LABEL = 'The Studio';\nfunction renderStages() {\n  const el = $('stages');\n  for (const b of $('stagePick').children) b.setAttribute('aria-pressed', String(b.dataset.s === stageSel));\n  $('shuffleBtn').hidden = stageSel !== 'season';")
rep("$('stages').addEventListener('click', e => {",
    """$('stagePick').addEventListener('click', e => { const t = e.target.closest('button'); if (!t || t.dataset.s === stageSel || building) return; AU.init(); AU.ui(); stageSel = t.dataset.s; store.stage = stageSel; save();
  if (state === 'menu') { freshMap(); resetRun(); decorate(); menuPose(); kick($('cvName'), 'bump'); }
  renderStages(); });
$('stages').addEventListener('click', e => {""")
# 3. results: the standard stage has no "new canvas"
rep("  end.dataset.next = '';", "  end.dataset.next = ''; $('replayBtn').hidden = !!GEN.std; $('endBtn').querySelector('small').textContent = GEN.std ? STD_LABEL : 'New canvas';")
# 4. paint cans on the standard stage, coffins on the season's
rep("function makeCoffin(x, y, z, seed) {",
    """// a paint can: the refill and hiding spot on the standard stage (the lid leans against it, a drip or two down the side)
const CAN_R = 0.5, CAN_H = 0.46;
const PCAN = (() => {
  const V2 = (x, y) => new THREE.Vector2(x, y), R = CAN_R, H = CAN_H;
  const wall = new THREE.LatheGeometry([V2(R, 0), V2(R, H - 0.035), V2(R + 0.035, H - 0.02), V2(R + 0.035, H + 0.012), V2(R - 0.012, H + 0.03), V2(R - 0.05, H - 0.005), V2(R - 0.05, 0.06), V2(0.001, 0.06)], 30);
  const band = new THREE.CylinderGeometry(R + 0.007, R + 0.007, 0.21, 30, 1, true).translate(0, 0.2, 0);
  const lidM = new THREE.Matrix4().compose(new THREE.Vector3(R + 0.13, 0.31, 0.06), new THREE.Quaternion().setFromEuler(new THREE.Euler(0.12, 0.2, -1.22)), new THREE.Vector3(1, 1, 1));
  const lid = new THREE.CylinderGeometry(R + 0.04, R + 0.04, 0.05, 30).applyMatrix4(lidM);
  const knob = new THREE.CylinderGeometry(R - 0.06, R - 0.06, 0.03, 30).translate(0, 0.035, 0).applyMatrix4(lidM);
  const bail = new THREE.TorusGeometry(R + 0.03, 0.02, 6, 24, Math.PI).rotateX(-1.95).translate(0, H - 0.09, 0);
  const cM = new THREE.Color(0xC9D1DE), cB = new THREE.Color(0xF4EAD5), cD = new THREE.Color(0x8E98A8), ni = g => g.index ? g.toNonIndexed() : g;
  const parts = [[ni(wall), cM], [ni(band), cB], [ni(lid), cM], [ni(knob), cD], [ni(bail), cD]];
  let n = 0; for (const [g] of parts) n += g.attributes.position.count;
  const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), col = new Float32Array(n * 3); let o = 0;
  for (const [g, c] of parts) { const k = g.attributes.position.count; pos.set(g.attributes.position.array, o * 3); nor.set(g.attributes.normal.array, o * 3); for (let q = 0; q < k; q++) { col[(o + q) * 3] = c.r; col[(o + q) * 3 + 1] = c.g; col[(o + q) * 3 + 2] = c.b; } o += k; }
  const body = new THREE.BufferGeometry(); body.setAttribute('position', new THREE.BufferAttribute(pos, 3)); body.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); body.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const hull = mergeGeos([new THREE.CylinderGeometry(R * 1.1, R * 1.1, H + 0.07, 30, 1, true).translate(0, (H + 0.07) / 2 - 0.02, 0), new THREE.CylinderGeometry(R + 0.07, R + 0.07, 0.1, 30).applyMatrix4(lidM)]);
  return { body, hull, floor: new THREE.CircleGeometry(R - 0.05, 30).rotateX(-Math.PI / 2) };
})();
const canMat = toon(0xFFFFFF, { vertexColors: true });
const canDrips = seed => { const r = rng(seed), list = []; for (let k = 0; k < 3; k++) { const a = r() * 6.2832, x = Math.cos(a) * (CAN_R + 0.03), z = Math.sin(a) * (CAN_R + 0.03), len = 0.08 + r() * 0.2; list.push(new THREE.CylinderGeometry(0.032, 0.032, len, 8).translate(x, -len / 2, z), new THREE.SphereGeometry(0.046, 10, 8).translate(x, -len, z)); } return mergeGeos(list); };
function makePaintCan(x, y, z, seed) {
  const g = new THREE.Group(), inner = new THREE.Group(); g.add(inner);
  const bm = toon(C.velvet), tm = toon(C.ink);
  const w = new THREE.Mesh(PCAN.body, canMat); w.castShadow = true; inner.add(w);
  inner.add(new THREE.Mesh(PCAN.hull, outlineMat));
  const fl = new THREE.Mesh(PCAN.floor, bm); fl.position.y = 0.065; inner.add(fl);
  const liq = new THREE.Mesh(PCAN.floor, tm); liq.position.y = 0.3; inner.add(liq);
  const drips = new THREE.Mesh(canDrips(seed), tm); drips.position.y = CAN_H + 0.01; inner.add(drips);
  const ring = new THREE.Mesh(ringG, potRingMat()); ring.rotation.x = -Math.PI / 2; ring.position.y = 0.07; ring.renderOrder = 3; g.add(ring);
  g.position.set(x, y, z); g.rotation.y = rng(seed + 3)() * 6.28; scene.add(g);
  return { g, inner, bm, tm, liq, drips, ring, x, y, z };
}
function makeCoffin(x, y, z, seed) {""")
rep("POTS.slice(0, cfg.pots).forEach(([x, y, z], i) => { const c = makeCoffin(x, y, z, 200 + i);",
    "const makePot = TH.pot === 'can' ? makePaintCan : makeCoffin;\n  POTS.slice(0, cfg.pots).forEach(([x, y, z], i) => { const c = makePot(x, y, z, 200 + i);")
rep("popText(lead === P ? 'You lead!' : mode === 'trio' ? nameOf(lead) + ' leads' : 'It leads');", "popText(lead === P ? 'You lead!' : nameOf(lead) + ' leads');")
open(p,'w').write(s); print('ok')
