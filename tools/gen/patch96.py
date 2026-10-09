p='/home/claude/paint-the-canvas.html'
s=open(p).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n,(s.count(a),a[:90]); s=s.replace(a,b)
# small fixes from the last look: the season tag clears the drips, and the can gets a proper label band
rep(".season{display:inline-flex;align-items:center;gap:8px;margin-top:-.2em;", ".season{display:inline-flex;align-items:center;gap:8px;margin-top:.15em;")
rep("cB = new THREE.Color(0xF4EAD5)", "cB = new THREE.Color(0xFFC23D)")

# ---------- 1. customize panel markup ----------
rep('      <div class="swatches" id="swatches" role="group" aria-label="Your color"></div>\n', '')
rep('<div class="mfoot">\n        <button class="chipbtn" id="shuffleBtn"',
    '<div class="mfoot">\n        <button class="chipbtn hot" id="lookBtn" type="button" aria-haspopup="dialog"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.2c-4.9 0-8.8 3.6-8.8 8.1 0 4.2 3.4 7.5 7.4 7.5 1.4 0 1.9-.8 1.9-1.6 0-1.2-1-1.5-1-2.6 0-.9.7-1.5 1.7-1.5h2.1c3 0 5.5-2.2 5.5-5.2 0-2.6-3.6-4.7-8.8-4.7z" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linejoin="round"/><circle cx="7.6" cy="11" r="1.5" fill="currentColor"/><circle cx="10.6" cy="7.4" r="1.5" fill="currentColor"/><circle cx="15.2" cy="7.6" r="1.5" fill="currentColor"/></svg><span>Customize</span></button>\n        <button class="chipbtn" id="shuffleBtn"')
rep('  <section class="sheet" id="end" hidden>',
    '''  <section class="sheet lookp" id="look" hidden role="dialog" aria-labelledby="lookTitle">
    <h2 class="ctitle" id="lookTitle">Customize</h2>
    <div class="lgroup"><p class="lhead">Color <b id="lookColor">Red</b></p><div class="swatches" id="swatches" role="group" aria-label="Your color"></div></div>
    <div class="lgroup"><p class="lhead">Eyes <b id="lookEyes">Round</b></p><div class="lopts" id="eyeOpts" role="group" aria-label="Eyes"></div></div>
    <div class="lgroup"><p class="lhead"><span class="sdot" aria-hidden="true"></span>Season 1: Halloween</p><div class="lopts" id="wearOpts" role="group" aria-label="Season 1 accessories"></div></div>
    <button class="btn play sm" id="lookDone" type="button">Done</button>
  </section>
  <section class="sheet" id="end" hidden>''')
rep(".seg.two{grid-template-columns:repeat(2,1fr)}",
    """.seg.two{grid-template-columns:repeat(2,1fr)}
.chipbtn.hot{border-color:var(--pumpkin);color:var(--white)}
.chipbtn.hot svg{color:var(--pumpkin)}
.menu.looking .logo,.menu.looking .dock{visibility:hidden}
.lookp{gap:12px;padding-top:16px}
.lookp .ctitle{font-size:26px}
.lgroup{display:grid;gap:8px}
.lhead{margin:0;display:flex;align-items:center;gap:6px;font:800 14px/1 var(--font-ui);color:var(--muted)}
.lhead b{color:var(--bone);font-weight:800}
.lookp .swatches{padding:2px 2px 0}
.lopts{display:flex;gap:6px}
.lopt{appearance:none;flex:1;min-width:0;height:54px;padding:0;border-radius:14px;border:2px solid rgba(255,255,255,.1);background:rgba(255,255,255,.05);display:grid;place-items:center;cursor:pointer;transition:transform .15s,border-color .15s,background .15s}
.lopt svg{width:36px;height:36px;display:block}
.lopt:hover{border-color:rgba(255,255,255,.28)}
.lopt[aria-pressed="true"]{border-color:var(--gold);background:rgba(255,216,107,.14);transform:translateY(-2px)}
.lopt:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.lopt:active{transform:translateY(1px)}""")

# ---------- 2. what you're wearing: data, save, and the 3D pieces ----------
rep("let colorId = 'red', menuReact = 0;",
    """let colorId = 'red', menuReact = 0;
// your look: color (above), eye shape, and this season's accessories: one on your head, one on your back, one in your mouth
const EYES = [['round', 'Round'], ['googly', 'Googly'], ['sleepy', 'Sleepy'], ['angry', 'Angry'], ['happy', 'Happy'], ['cyclops', 'Cyclops']];
const WEAR = [{ id: 'fangs', name: 'Fangs', slot: 'mouth' }, { id: 'wings', name: 'Bat wings', slot: 'back' }, { id: 'halo', name: 'Halo', slot: 'head' }, { id: 'hat', name: 'Witch hat', slot: 'head' }, { id: 'horns', name: 'Devil horns', slot: 'head' }];
const myLook = (() => { const l = store.look || {}, ok = (v, slot) => WEAR.some(w => w.id === v && w.slot === slot) ? v : null; return { eyes: EYES.some(e => e[0] === l.eyes) ? l.eyes : 'round', head: ok(l.head, 'head'), back: ok(l.back, 'back'), mouth: ok(l.mouth, 'mouth') }; })();""")
rep("scene.add(drop);\nconst shadowBlob",
    """// eye extras: brows for angry eyes, closed arcs for happy ones
const pBrows = [-1, 1].map(sd => { const br = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.07, 0.05), eyeB); br.renderOrder = 34; br.visible = false; br.userData.sd = sd; body.add(br); return br; });
const arcEyeG = new THREE.TorusGeometry(0.13, 0.036, 6, 18, Math.PI), pArcs = [-1, 1].map(() => { const m = new THREE.Mesh(arcEyeG, eyeB); m.renderOrder = 34; m.visible = false; body.add(m); return m; });
// ---------- this season's accessories (built once per blob, shown by what it's wearing) ----------
const WM = { hat: toon(0x35225C), band: toon(0xFF8A1F), halo: new THREE.MeshBasicMaterial({ color: 0xFFE27A, transparent: true }), horn: toon(0xE1283E), wing: toon(0x2E2048, { side: THREE.DoubleSide }), wingIn: toon(0x6A4AA0, { side: THREE.DoubleSide }), line: new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.DoubleSide }) };
const hatG = new THREE.ConeGeometry(0.4, 0.86, 22).translate(0, 0.47, 0), hatTipG = new THREE.ConeGeometry(0.15, 0.36, 14).translate(0, 0.16, 0), brimG = new THREE.CylinderGeometry(0.76, 0.76, 0.05, 30).translate(0, 0.03, 0), bandG = new THREE.CylinderGeometry(0.415, 0.43, 0.13, 22).translate(0, 0.13, 0);
const haloG = new THREE.TorusGeometry(0.4, 0.06, 8, 36).rotateX(Math.PI / 2), haloLineG = new THREE.TorusGeometry(0.4, 0.088, 8, 36).rotateX(Math.PI / 2);
const hornG = new THREE.ConeGeometry(0.11, 0.32, 12).translate(0, 0.14, 0);
const wingG = (() => { const sh = new THREE.Shape(); sh.moveTo(0, 0.16); sh.quadraticCurveTo(0.32, 0.6, 0.86, 0.52); sh.lineTo(0.98, 0.4); sh.quadraticCurveTo(0.86, 0.3, 0.8, 0.12); sh.quadraticCurveTo(0.7, 0.26, 0.56, 0.06); sh.quadraticCurveTo(0.44, 0.22, 0.3, 0.0); sh.quadraticCurveTo(0.16, 0.14, 0, 0.0); sh.closePath(); return new THREE.ShapeGeometry(sh, 6); })();
const wingLineG = wingG.clone().translate(-0.46, -0.27, 0).scale(1.12, 1.16, 1).translate(0.46, 0.27, -0.012);
function withLine(mesh, lineGeo, k) { const o = new THREE.Mesh(lineGeo || mesh.geometry, outlineMat); if (!lineGeo) o.scale.setScalar(k || 1.12); o.renderOrder = 32.6; mesh.add(o); return mesh; }
function makeWear(body) {
  const ro = m => { m.renderOrder = 33; return m; };
  const hat = new THREE.Group(); hat.add(withLine(ro(new THREE.Mesh(hatG, WM.hat)), null, 1.09)); hat.add(withLine(ro(new THREE.Mesh(brimG, WM.hat)), null, 1.07)); hat.add(ro(new THREE.Mesh(bandG, WM.band)));
  const tip = withLine(ro(new THREE.Mesh(hatTipG, WM.hat)), null, 1.12); tip.position.set(0.02, 0.86, 0); tip.rotation.z = -0.95; hat.add(tip);
  const halo = new THREE.Group(); const hr = ro(new THREE.Mesh(haloG, WM.halo)); halo.add(hr); const hl = new THREE.Mesh(haloLineG, outlineMat); hl.renderOrder = 32.6; halo.add(hl);
  const horns = [-1, 1].map(sd => { const h = withLine(ro(new THREE.Mesh(hornG, WM.horn)), null, 1.3); h.userData.sd = sd; return h; });
  const wings = [-1, 1].map(sd => { const g = new THREE.Group(); const m = ro(new THREE.Mesh(wingG, WM.wing)); g.add(m); const l = new THREE.Mesh(wingLineG, WM.line); l.renderOrder = 32.6; g.add(l); g.scale.set(sd * 1.15, 1.15, 1.15); g.userData.sd = sd; return g; });
  const fangs = [-1, 1].map(sd => { const f = new THREE.Mesh(fangG, fangM); f.renderOrder = 35; const o = new THREE.Mesh(fangG, fangHullM); o.scale.setScalar(1.45); o.renderOrder = 34; f.add(o); f.userData.sd = sd; return f; });
  const all = [hat, halo, ...horns, ...wings, ...fangs]; for (const m of all) { m.visible = false; body.add(m); }
  return { hat, halo, horns, wings, fangs };
}
// pin each piece to the goo surface (it squashes and stretches) every frame
function placeWear(W, U, look, D, withFangs) {
  const t = clock + (D.cpu ? 1.9 * D.team : 0);
  W.hat.visible = look.head === 'hat'; W.halo.visible = look.head === 'halo';
  for (const h of W.horns) h.visible = look.head === 'horns';
  for (const w of W.wings) w.visible = look.back === 'wings';
  for (const f of W.fangs) f.visible = withFangs && look.mouth === 'fangs';
  if (W.hat.visible) { W.hat.position.copy(gooJS(tv2.set(0, 1, 0), U)).add(tv1.set(0.03, -0.1, -0.03)); W.hat.rotation.set(-0.14, 0, -0.16); }
  if (W.halo.visible) { W.halo.position.copy(gooJS(tv2.set(0, 1, 0), U)).add(tv1.set(0, 0.42 + Math.sin(t * 2.3) * 0.05, -0.02)); W.halo.rotation.set(-0.18, 0, Math.sin(t * 1.3) * 0.08); }
  if (W.horns[0].visible) for (const h of W.horns) { const sd = h.userData.sd; h.position.copy(gooJS(tv2.set(sd * 0.43, 0.84, 0.33).normalize(), U)).multiplyScalar(0.97); h.rotation.set(-0.25, 0, -sd * 0.5); }
  if (W.wings[0].visible) { const fast = D.air || D.rollT > 0, flap = Math.sin(t * (fast ? 15 : 5.5)) * (fast ? 0.6 : 0.28);
    for (const w of W.wings) { const sd = w.userData.sd; w.position.copy(gooJS(tv2.set(sd * 0.5, 0.36, -0.78).normalize(), U)).multiplyScalar(0.95); w.rotation.set(0.1, sd * (0.55 + flap), sd * 0.18); } }
  if (withFangs && W.fangs[0].visible) { const mp = gooJS(mouthBase, U).multiplyScalar(1.03); for (const f of W.fangs) f.position.copy(mp).add(tv1.set(f.userData.sd * 0.056, 0.02, 0.016)); }
}
const pWear = makeWear(body);
scene.add(drop);
const shadowBlob""")
rep("const fangG = new THREE.ConeGeometry(0.03, 0.085, 10).rotateX(Math.PI).translate(0, -0.042, 0), fangM = toon(0xFFFFFF, { transparent: true }), fangs = [];\n[-1, 1].forEach(sd => { const f = new THREE.Mesh(fangG, fangM); f.renderOrder = 35; const o = new THREE.Mesh(fangG, new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }));",
    "const fangG = new THREE.ConeGeometry(0.03, 0.085, 10).rotateX(Math.PI).translate(0, -0.042, 0), fangM = toon(0xFFFFFF, { transparent: true }), fangHullM = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), fangs = [];\n[-1, 1].forEach(sd => { const f = new THREE.Mesh(fangG, fangM); f.renderOrder = 35; const o = new THREE.Mesh(fangG, fangHullM);")
# CPUs wear something too (picked each match)
rep("H.look = LH; H2.look = L2;", "H.look = LH; H2.look = L2;\nLH.wear = makeWear(LH.body); L2.wear = makeWear(L2.body); LH.wearing = { head: null, back: null, mouth: null }; L2.wearing = { head: null, back: null, mouth: null };\nfunction rollRivalLooks() { const heads = [null, null, 'halo', 'hat', 'horns']; for (const L of [LH, L2]) L.wearing = { head: heads[Math.random() * heads.length | 0], back: Math.random() < 0.3 ? 'wings' : null, mouth: Math.random() < 0.35 ? 'fangs' : null }; }")
rep("  L.glint2.position.copy(gooJS(tv2.set(-0.62, 0.32, 0.6).normalize(), U)); L.glint2.scale.set(1, 1, 0.5);\n}",
    "  L.glint2.position.copy(gooJS(tv2.set(-0.62, 0.32, 0.6).normalize(), U)); L.glint2.scale.set(1, 1, 0.5);\n  placeWear(L.wear, U, L.wearing, D, true);\n}")
rep("  pickRivalNames();", "  pickRivalNames(); rollRivalLooks();")

# ---------- 3. your face: the eye shape you picked ----------
rep("""  const lx = -look.lean * 0.07, ly = P.air ? (P.vy > 0 ? 0.05 : -0.04) : 0;
  for (const it of eyes) {
    const p = gooJS(it.base); it.e.position.copy(p).multiplyScalar(1.02);
    let sy = 1.15 * (1 - sq * 0.35); const s = scared ? 1.22 : 1;
    if (happy) sy *= 0.3; else if (blinkK > 0) sy *= 0.12; else if (strain) sy *= 0.6;
    it.e.scale.set(s, sy * s, 0.55);
    it.pu.visible = !happy && blinkK <= 0;
    it.pu.position.copy(p).multiplyScalar(1.07).add(tv1.set(lx, ly - 0.02, 0.02));
    it.pu.scale.setScalar(scared ? 0.72 : strain ? 0.85 : 1);
  }""",
"""  const lx = -look.lean * 0.07, ly = P.air ? (P.vy > 0 ? 0.05 : -0.04) : 0, ES = myLook.eyes, cyc = ES === 'cyclops', arcs = ES === 'happy';
  const wig = Math.min(1, P.spd / 7 + P.wob + (P.air ? 0.7 : 0) + (state === 'menu' ? 0.35 : 0));
  eyes.forEach((it, i) => {
    const show = !(cyc && i === 1) && !arcs; it.e.visible = show;
    const p = gooJS(cyc ? tv3.set(0, 0.47, 0.88).normalize() : it.base); it.e.position.copy(p).multiplyScalar(1.02);
    let sy = 1.15 * (1 - sq * 0.35), s = (scared ? 1.22 : 1) * (cyc ? 1.55 : ES === 'googly' ? 1.3 : 1);
    if (happy) sy *= 0.3; else if (blinkK > 0) sy *= 0.12; else if (strain) sy *= 0.6; else if (ES === 'sleepy') sy *= 0.5;
    it.e.scale.set(s, sy * s, 0.55);
    it.pu.visible = show && !happy && blinkK <= 0;
    const pd = ES === 'googly' ? tv1.set(lx + Math.sin(clock * 9 + i * 2.1) * 0.035 * wig, ly - 0.07 + Math.cos(clock * 7.3 + i) * 0.02 * wig, 0.06) : ES === 'sleepy' ? tv1.set(lx, ly - 0.05, 0.02) : tv1.set(lx, ly - 0.02, 0.02 + (cyc ? 0.04 : 0));
    it.pu.position.copy(p).multiplyScalar(1.07).add(pd);
    it.pu.scale.setScalar((scared ? 0.72 : strain ? 0.85 : 1) * (ES === 'googly' ? 0.62 : cyc ? 1.4 : ES === 'sleepy' ? 0.85 : 1));
    const br = pBrows[i]; br.visible = ES === 'angry' && !happy; if (br.visible) { br.position.copy(p).multiplyScalar(1.05).add(tv1.set(0, 0.2, 0.03)); br.rotation.set(0, 0, br.userData.sd * (scared ? -0.3 : 0.48)); }
    const ar = pArcs[i]; ar.visible = arcs; if (arcs) { ar.position.copy(p).multiplyScalar(1.04).add(tv1.set(0, -0.02, 0.02)); ar.scale.set(1, (happy ? 1.1 : 0.85) * (1 - sq * 0.3), 1); }
  });""")
rep("  for (const f of fangs) { const sd = f.userData.sd;", "  for (const f of fangs) { f.visible = myLook.mouth === 'fangs'; const sd = f.userData.sd;")
rep("  pGlint2.position.copy(gooJS(tv2.set(-0.64, 0.3, 0.6).normalize())); pGlint2.scale.set(1, 1, 0.5);\n}",
    "  pGlint2.position.copy(gooJS(tv2.set(-0.64, 0.3, 0.6).normalize())); pGlint2.scale.set(1, 1, 0.5);\n  placeWear(pWear, gooU, myLook, P, false);\n}")
open(p,'w').write(s); print('ok')
