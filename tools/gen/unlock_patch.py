# accessories are earned: every 4 to 8 matches a rare item turns up somewhere on the stage (only you can grab it), from that stage's set:
# Palette Island the pirate hat, eye patch and flower; Blank Canvas the top hat, bow tie and tiara; the Halloween stages the witch hat,
# halo and fangs. After the win/lose screen a full-screen "new item" moment; in Customize the ones still to find are locked (a code
# unlocks everything). Also: the tiara
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

# ================= the tiara =================
rep("const WEAR_A = WEAR_PACK ? (() => { const o = {}; for (const k of ['witch', 'pirate', 'top', 'bow', 'patch']) if (WEAR_PACK[k]) o[k] = assetGeo(WEAR_PACK[k]); return o; })() : {};",
    "const WEAR_A = WEAR_PACK ? (() => { const o = {}; for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara']) if (WEAR_PACK[k]) o[k] = assetGeo(WEAR_PACK[k]); return o; })() : {};")
rep("top: assetMat(WEAR_PACK.top), bow: assetMat(WEAR_PACK.bow, { clearcoat: 0.6 }) } : {};",
    "top: assetMat(WEAR_PACK.top), bow: assetMat(WEAR_PACK.bow, { clearcoat: 0.6 }), tiara: WEAR_PACK.tiara ? assetMat(WEAR_PACK.tiara, { clearcoat: 0.8, clearcoatRoughness: 0.12, envMapIntensity: 1.6 }) : null } : {};")
rep("top: { s: 0.86, y: -0.13, rx: -0.12, rz: -0.24 } };", "top: { s: 0.86, y: -0.13, rx: -0.12, rz: -0.24 }, tiara: { s: 0.6, y: -0.13, rx: -0.22, rz: 0.05 } };")
rep("  const pirate = grp('pirate', HAT_FIT.pirate.s), top = grp('top', HAT_FIT.top.s), bow = grp('bow', 1);",
    "  const pirate = grp('pirate', HAT_FIT.pirate.s), top = grp('top', HAT_FIT.top.s), bow = grp('bow', 1), tiara = grp('tiara', HAT_FIT.tiara.s);")
rep("  for (const m of [pirate, top, bow, patch, flower]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower };",
    "  for (const m of [pirate, top, bow, patch, flower, tiara]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara };")
rep("W.pirate.visible = !off && look.head === 'pirate'; W.top.visible = !off && look.head === 'tophat';",
    "W.pirate.visible = !off && look.head === 'pirate'; W.top.visible = !off && look.head === 'tophat'; W.tiara.visible = !off && look.head === 'tiara';")
rep("for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }",
    "for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }")
rep("    for (const [o, F] of [[W.hat, HAT_FIT.witch], [W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top]]) if (o.visible) { const fy",
    "    for (const [o, F] of [[W.hat, HAT_FIT.witch], [W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara]]) if (o.visible) { const fy")
rep("  for (const [o, F] of [[W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top]]) if (o.visible) { o.position.copy(gooJS(",
    "  for (const [o, F] of [[W.pirate, HAT_FIT.pirate], [W.top, HAT_FIT.top], [W.tiara, HAT_FIT.tiara]]) if (o.visible) { o.position.copy(gooJS(")
rep("...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower] : [])", "...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara] : [])")
rep("pWearParts = [pWear.hat, pWear.halo, pWear.pirate, pWear.top, pWear.bow, pWear.patch, pWear.flower,", "pWearParts = [pWear.hat, pWear.halo, pWear.pirate, pWear.top, pWear.bow, pWear.patch, pWear.flower, pWear.tiara,")
rep("tall = myLook.head === 'hat' ? 1.25 : myLook.head === 'tophat' ? 1.18 :", "tall = myLook.head === 'hat' ? 1.25 : myLook.head === 'tophat' ? 1.18 : myLook.head === 'tiara' ? 1.05 :")

# ================= the list: where each is found; owning them =================
rep("const WEAR = [{ id: 'pirate', name: 'Pirate hat', slot: 'head' }, { id: 'tophat', name: 'Top hat', slot: 'head' }, { id: 'patch', name: 'Eye patch', slot: 'eye' }, { id: 'flower', name: 'Flower', slot: 'side' }, { id: 'bowtie', name: 'Bow tie', slot: 'neck' },\n  { id: 'hat', name: 'Witch hat', slot: 'head', season: 1 }, { id: 'halo', name: 'Halo', slot: 'head', season: 1 }, { id: 'fangs', name: 'Fangs', slot: 'mouth', season: 1 }];",
"""const WEAR = [{ id: 'pirate', name: 'Pirate hat', slot: 'head', stage: 'island' }, { id: 'patch', name: 'Eye patch', slot: 'eye', stage: 'island' }, { id: 'flower', name: 'Flower', slot: 'side', stage: 'island' },
  { id: 'tophat', name: 'Top hat', slot: 'head', stage: 'blank' }, { id: 'bowtie', name: 'Bow tie', slot: 'neck', stage: 'blank' }, { id: 'tiara', name: 'Tiara', slot: 'head', stage: 'blank' },
  { id: 'hat', name: 'Witch hat', slot: 'head', season: 1, stage: 'halloween' }, { id: 'halo', name: 'Halo', slot: 'head', season: 1, stage: 'halloween' }, { id: 'fangs', name: 'Fangs', slot: 'mouth', season: 1, stage: 'halloween' }];
const WEAR_WHERE = { island: 'Palette Island', blank: 'Blank Canvas', halloween: 'the Halloween stages' };
// what you've found so far (everything starts locked)
const OWNED = new Set(Array.isArray(store.owned) ? store.owned.filter(id => WEAR.some(w => w.id === id)) : []);
const owns = id => OWNED.has(id);
function unlockItem(id) { if (OWNED.has(id)) return false; OWNED.add(id); store.owned = [...OWNED]; store.seen = store.seen || {}; store.seen.look = 0; save(); $('lookBtn').classList.add('hot'); return true; }
if (typeof store.itemIn !== 'number') store.itemIn = 4 + Math.floor(Math.random() * 5); // matches to go before the next item can turn up""")
rep("const myLook = (() => { const l = store.look || {}, ok = (v, slot) => WEAR.some(w => w.id === v && w.slot === slot) ? v : null;",
    "const myLook = (() => { const l = store.look || {}, ok = (v, slot) => WEAR.some(w => w.id === v && w.slot === slot) && OWNED.has(v) ? v : null;")
rep("const heads = [null, null, 'halo', 'hat', 'pirate', 'tophat'];", "const heads = [null, null, 'halo', 'hat', 'pirate', 'tophat', 'tiara'];")

# ================= Customize: grouped by where they're found, the ones still to find locked =================
rep('    <div class="lgroup"><p class="lhead">Accessories</p><div class="lopts" id="acceOpts" role="group" aria-label="Accessories"></div></div>\n    <div class="lgroup"><p class="lhead"><span class="sdot" aria-hidden="true"></span>Season 1: Halloween</p><div class="lopts" id="wearOpts" role="group" aria-label="Season 1 accessories"></div></div>\n    <button class="btn play sm" id="lookDone" type="button">Done</button>',
    '    <div class="lgroup"><p class="lhead">Palette Island</p><div class="lopts" id="wearIsl" role="group" aria-label="Palette Island accessories"></div></div>\n    <div class="lgroup"><p class="lhead">Blank Canvas</p><div class="lopts" id="wearBlk" role="group" aria-label="Blank Canvas accessories"></div></div>\n    <div class="lgroup"><p class="lhead"><span class="sdot" aria-hidden="true"></span>Season 1: Halloween</p><div class="lopts" id="wearOpts" role="group" aria-label="Season 1 accessories"></div></div>\n    <p class="lnote" id="lookNote" aria-live="polite"></p>\n    <button class="btn play sm" id="lookDone" type="button">Done</button>\n    <div class="ucode"><button class="ulink" id="unlockLink" type="button">Unlock all items</button><form class="uform" id="unlockForm" hidden><input id="unlockCode" type="text" inputmode="numeric" maxlength="8" autocomplete="off" placeholder="Code" aria-label="Unlock code"><button class="ugo" type="submit">Unlock</button></form></div>')
LOCK = '<span class="lk" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M4.5 7V5.2a3.5 3.5 0 0 1 7 0V7" fill="none" stroke="currentColor" stroke-width="2"/><rect x="3" y="7" width="10" height="7.5" rx="2" fill="currentColor"/></svg></span>'
rep("""  const wBtn = w => '<button class="lopt" type="button" data-w="' + w.id + '" aria-label="' + w.name + '" title="' + w.name + '" aria-pressed="' + (myLook[w.slot] === w.id) + '"><svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg></button>';
  $('acceOpts').innerHTML = WEAR.filter(w => !w.season).map(wBtn).join(''); $('wearOpts').innerHTML = WEAR.filter(w => w.season).map(wBtn).join('');""",
"""  const wBtn = w => owns(w.id) ? '<button class="lopt" type="button" data-w="' + w.id + '" aria-label="' + w.name + '" title="' + w.name + '" aria-pressed="' + (myLook[w.slot] === w.id) + '"><svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg></button>'
    : '<button class="lopt locked" type="button" data-w="' + w.id + '" aria-disabled="true" aria-label="' + w.name + ', locked" title="' + w.name + ' (locked)"><svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg>""" + LOCK.replace("'", "\\'") + """</button>';
  $('wearIsl').innerHTML = WEAR.filter(w => w.stage === 'island').map(wBtn).join(''); $('wearBlk').innerHTML = WEAR.filter(w => w.stage === 'blank').map(wBtn).join(''); $('wearOpts').innerHTML = WEAR.filter(w => w.stage === 'halloween').map(wBtn).join('');""")
rep("const wearPick = e => { const b = e.target.closest('.lopt'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w); myLook[w.slot]",
    "const lookNote = $('lookNote'); let noteT = 0; const note = (t, bad) => { lookNote.textContent = t; lookNote.classList.toggle('bad', !!bad); restartCls(lookNote, 'on'); clearTimeout(noteT); noteT = setTimeout(() => lookNote.classList.remove('on'), 3200); };\nconst wearPick = e => { const b = e.target.closest('.lopt'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w);\n  if (!owns(w.id)) { AU.nope(); kick(b, 'nope'); note('The ' + w.name.toLowerCase() + ' turns up on ' + WEAR_WHERE[w.stage] + ' now and then. Grab it when you see it.'); return; }\n  myLook[w.slot]")
rep("$('wearOpts').addEventListener('click', wearPick); $('acceOpts').addEventListener('click', wearPick);",
    """$('wearOpts').addEventListener('click', wearPick); $('wearIsl').addEventListener('click', wearPick); $('wearBlk').addEventListener('click', wearPick);
// the code that unlocks everything
$('unlockLink').addEventListener('click', () => { AU.init(); AU.ui(); const f = $('unlockForm'); f.hidden = !f.hidden; if (!f.hidden) setTimeout(() => $('unlockCode').focus(), 30); });
$('unlockCode').addEventListener('keydown', e => e.stopPropagation());
$('unlockForm').addEventListener('submit', e => { e.preventDefault(); const v = $('unlockCode').value.trim();
  if (v === '1234') { for (const w of WEAR) OWNED.add(w.id); store.owned = [...OWNED]; save(); $('unlockCode').value = ''; $('unlockForm').hidden = true; renderLook(); lookPop(); note('Every item is unlocked.'); }
  else { AU.nope(); kick($('unlockForm'), 'nope'); note("That code doesn't work.", true); } });""")

# ================= the item on the stage =================
MOD = r"""
// ---------- a rare item on the stage: a gift box floating over a glowing ring with a beam of light above it, turning up partway through a
// match (every few matches, see store.itemIn) somewhere open on the floor. Only you can grab it; it's yours for good ----------
const gift = { id: null, at: 0, on: false, x: 0, y: 0, z: 0, t: 0, got: false, pop: 0 };
const giftG = (() => {
  const parts = [], col = (g, c) => { const n = g.attributes.position.count, a = new Float32Array(n * 3), cc = new THREE.Color(c); for (let i = 0; i < n; i++) { a[i * 3] = cc.r; a[i * 3 + 1] = cc.g; a[i * 3 + 2] = cc.b; } g.setAttribute('color', new THREE.BufferAttribute(a, 3)); if (g.attributes.uv) g.deleteAttribute('uv'); return g; };
  const box = (w, h, d, x, y, z, c) => parts.push(col(rbox(w, h, d, Math.min(w, h, d) * 0.18).translate(x, y, z), c));
  box(0.62, 0.48, 0.62, 0, 0.24, 0, 0xFFC61A); box(0.7, 0.15, 0.7, 0, 0.53, 0, 0xFFD54F); // the box and its lid
  box(0.15, 0.5, 0.64, 0, 0.25, 0, 0xFF3FA4); box(0.64, 0.5, 0.15, 0, 0.25, 0, 0xFF3FA4); box(0.16, 0.17, 0.72, 0, 0.53, 0, 0xFF3FA4); box(0.72, 0.17, 0.16, 0, 0.53, 0, 0xFF3FA4); // the ribbon round it
  for (const sd of [-1, 1]) { const t = new THREE.TorusGeometry(0.13, 0.05, 8, 18).scale(1, 0.85, 0.7).rotateZ(sd * 0.55).translate(sd * 0.12, 0.7, 0); parts.push(col(t, 0xFF3FA4)); } // the bow
  parts.push(col(new THREE.SphereGeometry(0.065, 10, 8).translate(0, 0.64, 0), 0xE0218A));
  let n = 0; const ps = parts.map(g => { const q = g.index ? g.toNonIndexed() : g; n += q.attributes.position.count; return q; });
  const pos = new Float32Array(n * 3), nor = new Float32Array(n * 3), cl = new Float32Array(n * 3); let o = 0;
  for (const q of ps) { const c = q.attributes.position.count; pos.set(q.attributes.position.array, o * 3); nor.set(q.attributes.normal.array, o * 3); cl.set(q.attributes.color.array, o * 3); o += c; }
  const m = new THREE.BufferGeometry(); m.setAttribute('position', new THREE.BufferAttribute(pos, 3)); m.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); m.setAttribute('color', new THREE.BufferAttribute(linArr(cl), 3)); return m.translate(0, -0.36, 0);
})();
const giftM = new THREE.Mesh(giftG, ballMat), giftInk = new THREE.Mesh(giftG, inkMat); giftM.renderOrder = 33; giftInk.renderOrder = 32.6; giftM.add(giftInk); giftM.castShadow = true; giftM.visible = false; scene.add(giftM);
const giftRing = new THREE.Mesh(new THREE.RingGeometry(0.55, 0.85, 40).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: 0xFFD54F, transparent: true, opacity: 0.8, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -8, polygonOffsetUnits: -8, fog: false }));
giftRing.renderOrder = 7; giftRing.visible = false; scene.add(giftRing);
const giftBeam = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.62, 10, 24, 1, true).translate(0, 5, 0), new THREE.ShaderMaterial({ transparent: true, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, uniforms: { uT: { value: 0 } },
  vertexShader: 'varying vec2 vU; void main(){ vU = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
  fragmentShader: 'uniform float uT; varying vec2 vU; void main(){ float k = (1.0 - vU.y) * (1.0 - vU.y) * (0.75 + 0.25 * sin(vU.x * 37.7 + uT * 3.0)) * (0.8 + 0.2 * sin(uT * 4.0)); gl_FragColor = vec4(vec3(1.0, 0.86, 0.45) * k * 0.55, 1.0); }' }));
giftBeam.renderOrder = 8; giftBeam.visible = false; giftBeam.frustumCulled = false; scene.add(giftBeam);
const stageSet = () => !TH ? null : TH.id === 'island' ? 'island' : TH.id === 'blank' ? 'blank' : ['crypt', 'cathedral', 'manor'].includes(TH.id) ? 'halloween' : null;
// at the start of a match: if one's due and there's still one here to find, it'll turn up some way in
function giftPlan() {
  Object.assign(gift, { id: null, on: false, got: false, pop: 0 }); giftM.visible = giftRing.visible = giftBeam.visible = false;
  if (store.itemIn > 0) return; const left = WEAR.filter(w => w.stage === stageSet() && !owns(w.id)); if (!left.length) return;
  gift.id = left[Math.floor(Math.random() * left.length)].id; gift.at = (mode === 'solo' ? SOLO_T : MATCH_T) * (0.15 + Math.random() * 0.35);
}
function giftSpot() {
  for (let k = 0; k < 80; k++) {
    const x = (Math.random() * 2 - 1) * (ARENA - 3), z = (Math.random() * 2 - 1) * (ARENA - 3);
    if (surfaceUnder(x, z, 0.3) !== 0 || blockedAt(x, z, 0) || [[1, 0], [-1, 0], [0, 1], [0, -1]].some(([dx, dz]) => surfaceUnder(x + dx, z + dz, 0.3) !== 0 || blockedAt(x + dx, z + dz, 0))) continue;
    if (pots.some(p => Math.hypot(p.x - x, p.z - z) < 2.5) || rivals.some(r => Math.hypot(r.x - x, r.z - z) < r.rad + 1.5) || powers.some(w => Math.hypot(w.x - x, w.z - z) < 2.2) || balls.some(b => b.on && Math.hypot(b.x - x, b.z - z) < 2)) continue;
    if (ACTIVE.some(D => Math.hypot(D.x - x, D.z - z) < 5)) continue; // not right on top of anyone
    return [x, z];
  }
  return null;
}
function stepGift(dt) {
  if (!gift.id || gift.got) return;
  if (state !== 'play') { if (gift.on) { gift.on = false; giftPoof(); } return; }
  if (!gift.on) { if (runT < gift.at || matchLeft < 6) return; const s = giftSpot(); if (!s) { gift.at = runT + 2; return; }
    gift.on = true; gift.x = s[0]; gift.z = s[1]; gift.y = 0; gift.t = 0; gift.pop = 0; banner('Something rare!', 'An item has turned up. Go grab it', true); AU.spot(); buzz([10, 30, 10]); shockwave(gift.x, 0, gift.z, 1.6, 0xFFD54F); }
  gift.t += dt; gift.pop = Math.min(1, gift.pop + dt * 2.2);
  if (P.st === 'play' && Math.hypot(P.x - gift.x, P.z - gift.z) < 1.0 && Math.abs(P.y - gift.y) < 1.2) giftTake();
  else if (Math.random() < dt * 9) { const a = Math.random() * 6.283; spawnPart(gift.x + Math.cos(a) * 0.5, 0.4 + Math.random() * 0.8, gift.z + Math.sin(a) * 0.5, Math.cos(a) * 0.3, 0.8 + Math.random() * 0.8, Math.sin(a) * 0.3, 0.7, puHaloMat, 0.3 + Math.random() * 0.2); }
}
function giftTake() {
  gift.got = true; gift.on = false; giftM.visible = giftRing.visible = giftBeam.visible = false;
  unlockItem(gift.id); store.itemIn = 4 + Math.floor(Math.random() * 5); save(); newItem = gift.id;
  const w = WEAR.find(x => x.id === gift.id); banner('New item!', w ? w.name : '', true); AU.power(); setTimeout(() => AU.pop(), 160); buzz([20, 40, 30]); shake = Math.max(shake, 0.15);
  confetti(gift.x, gift.y + 0.6, gift.z, 70, 3.2); shockwave(gift.x, 0, gift.z, 2, 0xFFD54F);
}
function giftPoof() { giftM.visible = giftRing.visible = giftBeam.visible = false; for (let i = 0; i < 14; i++) { const a = i / 14 * 6.283; spawnPart(gift.x, 0.6, gift.z, Math.cos(a) * 2, 1 + Math.random(), Math.sin(a) * 2, 0.45, puHaloMat, 0.4); } }
function drawGift() {
  const on = gift.on && !!gift.id; giftM.visible = giftRing.visible = giftBeam.visible = on; if (!on) return;
  const t = gift.t, pk = Math.max(0.01, easeElastic(gift.pop)); giftM.position.set(gift.x, gift.y + 0.95 + Math.sin(t * 2.6) * 0.12, gift.z); giftM.rotation.set(Math.sin(t * 1.7) * 0.12, t * 1.6, Math.sin(t * 2.1) * 0.1); giftM.scale.setScalar(pk * 1.05);
  giftRing.position.set(gift.x, gift.y + 0.05, gift.z); giftRing.scale.setScalar(pk * (1 + 0.1 * Math.sin(t * 5))); giftRing.material.opacity = 0.6 + 0.3 * Math.sin(t * 6);
  giftBeam.position.set(gift.x, gift.y, gift.z); giftBeam.scale.set(pk, 1, pk); giftBeam.material.uniforms.uT.value = t;
}
let newItem = null;
"""
anchor = "// sand thrown up where it lands hard"
i = src.index(anchor)
src = src[:i] + MOD + src[i:]
rep("updateParts(dt); flushGrooves(); stepBalls(dt);", "updateParts(dt); flushGrooves(); stepBalls(dt); stepGift(dt);")
# a match counts down to the next item; the gift is planned at the start
rep("  store.runs = (store.runs || 0) + 1;", "  store.runs = (store.runs || 0) + 1; if (store.itemIn > 0) store.itemIn--;")
rep("  const basins = introBasins();", "  giftPlan(); newItem = null;\n  const basins = introBasins();")
# the pointer: rides above it when it's far, sits on the screen edge pointing at it when it's off screen (like the orb's)
rep('  <div class="orbptr" id="orbPtr"><i></i><u><b></b></u></div>', '  <div class="orbptr" id="orbPtr"><i></i><u><b></b></u></div>\n  <div class="orbptr giftptr" id="giftPtr"><i></i><u><b></b></u></div>')
rep("  // the holy water off screen: an edge marker, red when its pound is coming down near you or it's lining up a fling at you",
"""  drawGift();
  { const el = $('giftPtr'); if (gift.on && playing && P.st !== 'ko') { tv1.set(gift.x, gift.y + 1, gift.z).project(camera); const W = viewW, Hh = viewH, behind = tv1.z > 1; let x = behind ? -tv1.x : tv1.x, y = behind ? -tv1.y : tv1.y;
      const on = !behind && Math.abs(x) < 0.9 && Math.abs(y) < 0.78, far = Math.hypot(gift.x - P.x, gift.z - P.z) > 6;
      if (on && !far) { if (el._on) { el._on = false; el.classList.remove('on'); } }
      else { let px, py, rot; if (on) { px = (x * 0.5 + 0.5) * W; py = (-y * 0.5 + 0.5) * Hh - 56 - Math.abs(Math.sin(clock * 5)) * 6; rot = 180; } else { const m = Math.max(Math.abs(x) / 0.86, Math.abs(y) / 0.72, 1e-3); x /= m; y /= m; px = (x * 0.5 + 0.5) * W; py = (-y * 0.5 + 0.5) * Hh; rot = Math.atan2(x, y) * 180 / Math.PI; }
        if (!el._on) { el._on = true; el.classList.add('on'); } el.classList.toggle('edge', !on); el.style.transform = 'translate(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px)'; el.children[1].style.transform = 'rotate(' + rot.toFixed(0) + 'deg)'; } }
    else if (el._on) { el._on = false; el.classList.remove('on'); } }
  // the holy water off screen: an edge marker, red when its pound is coming down near you or it's lining up a fling at you""")

# ================= after the win/lose screen: the new item =================
rep("  setTimeout(() => { if (id === runId && state === 'dead') showEnd(endImg); }, 650);\n}",
    "  setTimeout(() => { if (id === runId && state === 'dead') { if (newItem) showNewItem(newItem); else showEnd(endImg); } }, 650);\n}")
rep('  <section class="sheet" id="end" hidden>',
    '''  <section class="newitem" id="newItem" hidden role="dialog" aria-modal="true" aria-labelledby="niName">
    <div class="nirays" aria-hidden="true"></div>
    <div class="niconf" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
    <div class="nibody">
      <p class="nikick">New item!</p>
      <div class="nibadge"><svg id="niIcon" viewBox="0 0 40 40" aria-hidden="true"></svg></div>
      <h2 class="niname" id="niName">Pirate hat</h2>
      <p class="niwhere" id="niWhere">Found on Palette Island</p>
      <div class="nibtns"><button class="btn play sm" id="niTry" type="button">Try it on</button><button class="btn" id="niGo" type="button">Continue</button></div>
    </div>
  </section>
  <section class="sheet" id="end" hidden>''')
rep("function abortVictory() {",
"""function showNewItem(id) {
  const w = WEAR.find(x => x.id === id), el = $('newItem'); if (!w) return showEnd(endImg);
  $('niIcon').innerHTML = WEAR_ICON[w.id]; $('niName').textContent = w.name; $('niWhere').textContent = 'Found on ' + WEAR_WHERE[w.stage].replace(/^the /, 'the ');
  el.hidden = false; void el.offsetWidth; el.classList.add('on'); AU.sting(); setTimeout(() => AU.power(), 260); buzz([20, 40, 20, 40, 30]);
  setTimeout(() => $('niTry').focus({ preventScroll: true }), 60);
}
function hideNewItem() { const el = $('newItem'); el.classList.remove('on'); el.hidden = true; newItem = null; }
$('niGo').addEventListener('click', () => { AU.init(); AU.ui(); hideNewItem(); if (state === 'dead') showEnd(endImg); });
$('niTry').addEventListener('click', () => { AU.init(); AU.ui(); const id = newItem, w = WEAR.find(x => x.id === id); hideNewItem(); if (w) { myLook[w.slot] = w.id; saveLook(); }
  irisClose(() => { end.hidden = true; showMenu(); camSnap = true; irisOpen(); openLook(); }); });
function abortVictory() {""")

# ================= styles =================
rep(".sdot{display:inline-block;", """.lopt.locked{position:relative;background:rgba(0,0,0,.18);border-style:dashed;border-color:rgba(255,255,255,.14)}
.lopt.locked svg{filter:grayscale(1) brightness(.62);opacity:.38}
.lopt .lk{position:absolute;right:5px;bottom:5px;width:17px;height:17px;display:grid;place-items:center;border-radius:6px;background:var(--line);color:var(--muted)}
.lopt .lk svg{width:11px;height:11px;filter:none;opacity:1}
.lopt.locked:hover{border-color:rgba(255,255,255,.24)}
.lnote{margin:-2px 0 0;min-height:0;max-height:0;overflow:hidden;font:700 14px/1.35 var(--font-ui);color:var(--gold);text-align:center;text-wrap:balance;transition:max-height .25s}
.lnote.on{max-height:60px}
.lnote.bad{color:#FF8C9E}
.ucode{display:flex;flex-direction:column;align-items:center;gap:8px;margin-top:-4px}
.ulink{appearance:none;border:0;background:none;padding:4px 8px;color:var(--muted);font:700 13px/1 var(--font-ui);text-decoration:underline;text-underline-offset:3px;cursor:pointer;opacity:.75}
.ulink:hover{opacity:1}
.uform{display:flex;gap:6px}
.uform input{width:96px;height:38px;box-sizing:border-box;padding:0 12px;border-radius:12px;border:2.5px solid var(--line);background:var(--bone);color:var(--outline);font:400 18px/1 var(--font-display);text-align:center;letter-spacing:.12em;outline:none;-webkit-user-select:text;user-select:text}
.uform input:focus{box-shadow:0 0 0 3px var(--gold)}
.ugo{appearance:none;height:38px;padding:0 14px;border-radius:12px;border:2.5px solid var(--line);background:var(--plum-2);color:var(--bone);font:800 14px/1 var(--font-ui);cursor:pointer;box-shadow:0 3px 0 var(--line)}
.giftptr i{background:radial-gradient(circle at 50% 40%,#FFE89A,#FFC61A 60%,#E79A00);animation:none;box-shadow:0 0 14px 6px rgba(255,214,79,.7)}
.giftptr i::after{content:"";position:absolute;inset:9px 5px;border-left:3px solid #FF3FA4;border-right:3px solid #FF3FA4;transform:scaleX(.18)}
.newitem{position:fixed;inset:0;z-index:30;display:grid;place-items:center;overflow:hidden;background:radial-gradient(120% 90% at 50% 42%,#4A2A86 0%,var(--plum) 55%,#120A24 100%);opacity:0;transition:opacity .25s}
.newitem.on{opacity:1}
.nirays{position:absolute;left:50%;top:42%;width:170vmax;height:170vmax;margin:-85vmax 0 0 -85vmax;background:repeating-conic-gradient(rgba(255,216,107,.16) 0 9deg,rgba(255,216,107,0) 9deg 22.5deg);-webkit-mask:radial-gradient(closest-side,#000 18%,transparent 72%);mask:radial-gradient(closest-side,#000 18%,transparent 72%);animation:nirays 24s linear infinite}
@keyframes nirays{to{transform:rotate(360deg)}}
.nibody{position:relative;display:grid;justify-items:center;gap:10px;width:min(360px,calc(100% - 40px));padding:0 0 env(safe-area-inset-bottom)}
.nikick{margin:0;font:400 clamp(38px,12vw,58px)/1 var(--font-display);color:var(--gold);text-shadow:var(--o3),0 7px 0 var(--outline);transform:scale(.3) rotate(-8deg);opacity:0}
.newitem.on .nikick{animation:nikick .55s .12s cubic-bezier(.2,1.8,.4,1) forwards}
@keyframes nikick{to{transform:rotate(-3deg);opacity:1}}
.nibadge{position:relative;width:min(220px,58vw);aspect-ratio:1;margin:6px 0 4px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 50% 38%,#FFFFFF 0%,#FFF2C6 38%,#FFD86B 70%,#E5A100 100%);border:5px solid var(--line);box-shadow:0 0 0 7px var(--gold),0 0 0 12px var(--line),0 0 60px 18px rgba(255,216,107,.55);transform:scale(0)}
.newitem.on .nibadge{animation:nibadge .7s .3s cubic-bezier(.2,1.6,.35,1) forwards,nibob 2.6s 1.1s ease-in-out infinite}
@keyframes nibadge{to{transform:scale(1)}}
@keyframes nibob{0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-8px) rotate(2deg)}}
.nibadge svg{width:68%;height:68%;filter:drop-shadow(0 4px 0 rgba(12,6,32,.35))}
.niname{margin:4px 0 0;font:400 clamp(28px,8.5vw,40px)/1.05 var(--font-display);color:var(--bone);text-align:center;text-shadow:var(--o3),0 5px 0 var(--outline);opacity:0;transform:translateY(12px)}
.niwhere{margin:0;font:700 15px/1.3 var(--font-ui);color:var(--muted);opacity:0;transform:translateY(12px)}
.newitem.on .niname{animation:nirise .4s .62s ease-out forwards}
.newitem.on .niwhere{animation:nirise .4s .72s ease-out forwards}
@keyframes nirise{to{opacity:1;transform:none}}
.nibtns{display:grid;gap:10px;width:100%;margin-top:14px;opacity:0}
.newitem.on .nibtns{animation:nirise .4s .9s ease-out forwards}
.niconf{position:absolute;inset:0;pointer-events:none}
.niconf i{position:absolute;left:50%;top:40%;width:12px;height:18px;border-radius:3px;background:var(--gold);border:2px solid var(--line);opacity:0}
.niconf i:nth-child(3n){background:#FF3FA4}.niconf i:nth-child(3n+1){background:#4DE1FF}.niconf i:nth-child(4n){width:14px;height:14px;border-radius:50%}
.newitem.on .niconf i{animation:niconf 1.6s .35s cubic-bezier(.15,.7,.3,1) forwards}
.niconf i:nth-child(1){--x:-42vw;--y:-30vh;--r:220deg}.niconf i:nth-child(2){--x:38vw;--y:-34vh;--r:-180deg}.niconf i:nth-child(3){--x:-30vw;--y:22vh;--r:140deg}.niconf i:nth-child(4){--x:44vw;--y:18vh;--r:-260deg}
.niconf i:nth-child(5){--x:-12vw;--y:-40vh;--r:300deg}.niconf i:nth-child(6){--x:16vw;--y:-42vh;--r:-120deg}.niconf i:nth-child(7){--x:-46vw;--y:-4vh;--r:90deg}.niconf i:nth-child(8){--x:46vw;--y:-8vh;--r:-90deg}
.niconf i:nth-child(9){--x:-22vw;--y:36vh;--r:200deg}.niconf i:nth-child(10){--x:26vw;--y:34vh;--r:-210deg}.niconf i:nth-child(11){--x:-36vw;--y:-18vh;--r:160deg}.niconf i:nth-child(12){--x:32vw;--y:-20vh;--r:-150deg}
@keyframes niconf{0%{opacity:1;transform:translate(-50%,-50%) scale(.4)}70%{opacity:1}100%{opacity:0;transform:translate(calc(-50% + var(--x)),calc(-50% + var(--y))) rotate(var(--r)) scale(1)}}
@media (prefers-reduced-motion: reduce){.nirays,.newitem.on .nibadge{animation:none;transform:none}.newitem.on .nikick,.newitem.on .niname,.newitem.on .niwhere,.newitem.on .nibtns{animation:none;opacity:1;transform:none}.newitem.on .niconf i{animation:none}}
.sdot{display:inline-block;""")

# ================= icons and the scoreboard for the tiara =================
rep("  hat: '<path d=\"M14 26c3-6 5-13 9-19 1 4 2 9 4 13l-1 6z\" fill=\"#4A3378\"",
    """  tiara: '<path d="M7 27.5c-.4-5 .5-9 1.8-12.2l4.6 6.2L20 9.5l6.6 12 4.6-6.2c1.3 3.2 2.2 7.2 1.8 12.2C27 26 13 26 7 27.5z" fill="#F2C88A" stroke="#D9C8FF" stroke-width="1.6" stroke-linejoin="round"/><path d="M20 14.5l3.2 4.4L20 23.5l-3.2-4.6z" fill="#FF4FB0" stroke="#7A1E52" stroke-width="1"/><circle cx="9" cy="14.6" r="1.8" fill="#FF4FB0"/><circle cx="31" cy="14.6" r="1.8" fill="#FF4FB0"/>',
  hat: '<path d="M14 26c3-6 5-13 9-19 1 4 2 9 4 13l-1 6z" fill="#4A3378\"""")
rep("pir = w.head === 'pirate', tph = w.head === 'tophat';", "pir = w.head === 'pirate', tph = w.head === 'tophat', tia = w.head === 'tiara';")
rep("  if (tph) s +=", """  if (tia) s += '<path d="M14.6 13.6c-.2-2.6.3-4.8 1-6.4l2.6 3.2L24 4l5.8 6.4 2.6-3.2c.7 1.6 1.2 3.8 1 6.4-5.6-1-13.2-1-18.8 0z" fill="#F2C88A" stroke="' + O + '" stroke-width="1.8" stroke-linejoin="round"/><path d="M24 7.4l1.8 2.4-1.8 2.6-1.8-2.6z" fill="#FF4FB0"/>';
  if (tph) s +=""")
open(P, 'w').write(src)
print('ok', len(src))
