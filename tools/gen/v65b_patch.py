# V65, part 2: nerd glasses (a Blank Canvas find, on the eyes: one or the other with the patch); the eye patch painted on the head with
# its strap (no more floating strap or broken rim); eye color, five to pick from; the leap face; and in a basin, just its eyes on the paint
import json, re
P = '/home/claude/paint-the-canvas.html'
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:150])
    src = src.replace(old, new)

# ================= the glasses =================
m = re.search(r'(<script type="application/json" id="wearPack">)(.*?)(</script>)', src, re.S)
pack = json.loads(m.group(2)); pack['glasses'] = json.load(open(SP + 'glasses_in/glasses_asset.json'))
src = src[:m.start(2)] + json.dumps(pack, separators=(',', ':')) + src[m.end(2):]
rep("for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara']) if (WEAR_PACK[k])", "for (const k of ['witch', 'pirate', 'top', 'bow', 'patch', 'tiara', 'glasses']) if (WEAR_PACK[k])")
rep("bow: assetMat(WEAR_PACK.bow, { clearcoat: 0.6 }), tiara:", "bow: assetMat(WEAR_PACK.bow, { clearcoat: 0.6 }), glasses: WEAR_PACK.glasses ? assetMat(WEAR_PACK.glasses, { clearcoat: 0.8, clearcoatRoughness: 0.1 }) : null, tiara:")
rep("  const pirate = grp('pirate', HAT_FIT.pirate.s), top = grp('top', HAT_FIT.top.s), bow = grp('bow', 1), tiara = grp('tiara', HAT_FIT.tiara.s);",
    "  const pirate = grp('pirate', HAT_FIT.pirate.s), top = grp('top', HAT_FIT.top.s), bow = grp('bow', 1), tiara = grp('tiara', HAT_FIT.tiara.s), glasses = grp('glasses', 1);")
rep("  for (const m of [pirate, top, bow, patch, flower, tiara]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara };",
    "  for (const m of [pirate, top, bow, patch, flower, tiara, glasses]) { m.visible = false; body.add(m); }\n  return { pirate, top, bow, patch, flower, tiara, glasses };")
rep("for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }",
    "for (const o of [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses, ...W.horns, ...W.wings, ...W.fangs]) W.bs.set(o, o.scale.clone()); }")
rep("...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara] : [])", "...(W ? [W.hat, W.halo, W.pirate, W.top, W.bow, W.patch, W.flower, W.tiara, W.glasses] : [])")
rep("pWearParts = [pWear.hat, pWear.halo, pWear.pirate, pWear.top, pWear.bow, pWear.patch, pWear.flower, pWear.tiara,", "pWearParts = [pWear.hat, pWear.halo, pWear.pirate, pWear.top, pWear.bow, pWear.patch, pWear.flower, pWear.tiara, pWear.glasses,")
# worn: the patch is painted on now (so its 3D piece never shows); the glasses sit on the face in front of the eyes
rep("W.bow.visible = !off && look.neck === 'bowtie'; W.patch.visible = !off && look.eye === 'patch'; W.flower.visible = !off && look.side === 'flower';",
    "W.bow.visible = !off && look.neck === 'bowtie'; W.patch.visible = false; W.flower.visible = !off && look.side === 'flower'; W.glasses.visible = !off && look.eye === 'glasses';")
rep("""    if (!plain) { W.patch.visible = W.flower.visible = W.bow.visible = false; }
    if (SI.setLashes) { const lk = look.lash === 'lashes' && !off ? Math.min(1, pu * 1.4) : 0; SI.setLashes(lk, W.patch.visible ? 0 : lk); }
    if (W.patch.visible || W.flower.visible) { SLIME.headTop(SI, wv1, wq1, 0);""",
"""    if (!plain) { W.patch.visible = W.flower.visible = W.bow.visible = W.glasses.visible = false; }
    // painted on (every form): the lashes (none under the patch), the patch and its strap, the eyes' color
    if (SI.setLashes) { const k = !off ? Math.min(1, pu * 1.4) : 0, lk = look.lash === 'lashes' ? k : 0, pt = look.eye === 'patch' ? k : 0; SI.setLashes(lk, pt > 0 ? 0 : lk); SI.setPatch(pt); SI.setIris((EYE_COLS[look.iris] || EYE_COLS.brown).lin); }
    if (W.glasses.visible || W.flower.visible) { SLIME.headTop(SI, wv1, wq1, 0);
      if (W.glasses.visible) { W.glasses.position.copy(wv1).add(wv2.set(0, 0.062, 0.448).multiplyScalar(mk).applyQuaternion(wq1)); W.glasses.quaternion.copy(wq1).multiply(wearQ2.setFromEuler(wearE.set(-0.06 + S.tx * 0.2, 0, S.tz * 0.15))); W.glasses.scale.multiplyScalar(mk * 0.56); }""")
rep("W.bow.quaternion.setFromEuler(wearE.set(-0.12 + S.tx * 0.35, 0, Math.sin(t * 2.1) * 0.05 + S.tz * 0.5)); W.bow.scale.multiplyScalar(mk * 0.4); }",
    "W.bow.quaternion.setFromEuler(wearE.set(-0.12 + S.tx * 0.35, 0, Math.sin(t * 2.1) * 0.05 + S.tz * 0.5)).premultiply(SI.groups.slime.quaternion); W.bow.scale.multiplyScalar(mk * 0.4); }")
rep("  W.patch.visible = W.flower.visible = W.bow.visible = false;\n  for (const [o, F] of [[W.pirate, HAT_FIT.pirate]", "  W.patch.visible = W.flower.visible = W.bow.visible = W.glasses.visible = false;\n  for (const [o, F] of [[W.pirate, HAT_FIT.pirate]")
rep("{ id: 'lashes', name: 'Lashes', slot: 'lash', stage: 'blank' },", "{ id: 'lashes', name: 'Lashes', slot: 'lash', stage: 'blank' }, { id: 'glasses', name: 'Glasses', slot: 'eye', stage: 'blank' },")
rep("eye: Math.random() < (head === 'pirate' ? 0.6 : 0.12) ? 'patch' : null,", "eye: Math.random() < (head === 'pirate' ? 0.6 : 0.12) ? 'patch' : Math.random() < 0.14 ? 'glasses' : null,")
rep("const WEAR_ICON = {\n", """const WEAR_ICON = {
  glasses: '<path d="M4.5 17.5h31" stroke="#D9C8FF" stroke-width="5.5" stroke-linecap="round"/><rect x="5" y="14" width="13" height="11.5" rx="4" fill="#8FD3FF" fill-opacity=".25" stroke="#D9C8FF" stroke-width="6"/><rect x="22" y="14" width="13" height="11.5" rx="4" fill="#8FD3FF" fill-opacity=".25" stroke="#D9C8FF" stroke-width="6"/>'
    + '<rect x="5" y="14" width="13" height="11.5" rx="4" fill="none" stroke="#231A2B" stroke-width="3"/><rect x="22" y="14" width="13" height="11.5" rx="4" fill="none" stroke="#231A2B" stroke-width="3"/><path d="M18 17.5h4" stroke="#231A2B" stroke-width="3"/><rect x="17.4" y="15" width="5.2" height="5.4" rx="1" fill="#F4EEE4" stroke="#231A2B" stroke-width="1.2"/><path d="M8 17l2.6-1.6" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" opacity=".8"/>',
""")
rep("  if (w.eye === 'patch') s +=", """  if (w.eye === 'glasses') s += '<g fill="none" stroke="#1A1030" stroke-width="1.5"><rect x="16.4" y="21.4" width="7" height="6.6" rx="2"/><rect x="24.6" y="21.4" width="7" height="6.6" rx="2"/><path d="M23.4 23.6h1.2"/></g><rect x="23.3" y="22.6" width="1.4" height="1.8" fill="#F4EEE4"/>';
  if (w.eye === 'patch') s +=""")
rep("  if (w.slot === 'lash' && myLook.lash) {", "  if (w.slot === 'eye' && myLook.eye === 'glasses') shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832;\n  if (w.slot === 'lash' && myLook.lash) {")

# ================= eye color =================
rep("const WEAR_CAT = {", """// the eyes' color: five to pick from (lin: the iris in the shader, css: on the picker and the basin's eyes)
const EYE_COLS = { brown: { name: 'Brown', lin: [0.16, 0.06, 0.035], css: '#8A5636' }, blue: { name: 'Blue', lin: [0.03, 0.1, 0.32], css: '#3B7BE0' }, green: { name: 'Green', lin: [0.04, 0.18, 0.05], css: '#46A853' },
  violet: { name: 'Violet', lin: [0.14, 0.045, 0.28], css: '#8E52DA' }, gold: { name: 'Gold', lin: [0.34, 0.17, 0.016], css: '#D8A41F' } };
const EYE_KEYS = Object.keys(EYE_COLS);
const WEAR_CAT = {""")
rep("neck: ok(l.neck, 'neck'), lash: ok(l.lash, 'lash') }; })();", "neck: ok(l.neck, 'neck'), lash: ok(l.lash, 'lash'), iris: ['brown', 'blue', 'green', 'violet', 'gold'].includes(l.iris) ? l.iris : 'brown' }; })();")
rep("LH.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null }; L2.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null };",
    "LH.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null, iris: 'brown' }; L2.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null, iris: 'brown' };")
rep("lash: Math.random() < (head === 'tiara' ? 0.65 : 0.18) ? 'lashes' : null }; } }",
    "lash: Math.random() < (head === 'tiara' ? 0.65 : 0.18) ? 'lashes' : null, iris: Math.random() < 0.45 ? 'brown' : EYE_KEYS[1 + (Math.random() * 4 | 0)] }; } }")
rep('''    <div class="swatches" id="swatches" role="group" aria-label="Your color"></div>''',
    '''    <div class="swatches" id="swatches" role="group" aria-label="Your color"></div>
    <div class="leyes"><p class="lhead">Eyes</p><div class="irises" id="irises" role="group" aria-label="Eye color"></div></div>''')
rep("  railEdge(); $('lookNameTxt').textContent = playerName();",
    "  $('irises').innerHTML = EYE_KEYS.map(k => '<button class=\"iris\" type=\"button\" data-i=\"' + k + '\" style=\"--ic:' + EYE_COLS[k].css + '\" aria-label=\"' + EYE_COLS[k].name + ' eyes\" title=\"' + EYE_COLS[k].name + '\" aria-pressed=\"' + (myLook.iris === k) + '\"><i></i></button>').join('');\n  railEdge(); $('lookNameTxt').textContent = playerName();")
rep("$('lookRail').addEventListener('click', wearPick);",
    "$('lookRail').addEventListener('click', wearPick);\n$('irises').addEventListener('click', e => { const b = e.target.closest('.iris'); if (!b || b.dataset.i === myLook.iris) return; AU.init(); myLook.iris = b.dataset.i; saveLook(); const sl = $('lookRail').scrollLeft; renderLook(); $('lookRail').scrollLeft = sl; railEdge(); lookPop(); shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832; });")
rep(".lktop{display:flex;", """.leyes{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:-2px 0 -2px}
.irises{display:flex;gap:10px}
.iris{appearance:none;width:34px;height:34px;padding:0;border-radius:50%;border:3px solid var(--line);background:radial-gradient(circle at 50% 52%,#120A18 0 22%,var(--ic) 24% 62%,#FFFFFF 64%);cursor:pointer;position:relative;transition:transform .2s cubic-bezier(.3,1.6,.5,1)}
.iris i{position:absolute;left:31%;top:28%;width:5px;height:5px;border-radius:50%;background:#FFFFFF}
.iris:hover{transform:translateY(-2px)}
.iris[aria-pressed="true"]{transform:scale(1.18);box-shadow:0 0 0 3px var(--bone),0 0 0 6px var(--line)}
.iris:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.lktop{display:flex;""")

# ================= the leap face =================
rep("  if (F === MOOD.yawn) return 'yawn';", "  if (F === MOOD.yawn) return 'yawn';\n  if (D.air && D.st === 'play' && !D.slam && !D.missile && !D.rocket && !D.turret && !(D.giantT > 0) && !(D.knockT > 0)) return 'leap'; // (wide-eyed, mouth open: up it goes)")

# ================= in a basin: just its eyes, poking up out of the paint =================
rep("// each frame, after the blob's own animation has worked out its squash, lean and the rest\nfunction slimeVisual(D, V, dt, sq, rise, rad, gy, hop) {\n  const I = V.slime, L = V.look, U = V.U;",
r"""// in a basin (a refill, or at the start of a match) all you see of a blob is its eyes: two eyeballs bobbing at the top of the paint with a
// ring of paint drawn up round each, popping up once it's under, glancing about (at the nearest rival, mid-match), blinking now and then
const potEyeTex = {}, potEyeV = new THREE.Vector3(), potEyeG = new THREE.SphereGeometry(0.13, HI ? 28 : 18, HI ? 18 : 12), potCollarG = new THREE.TorusGeometry(0.128, 0.042, HI ? 10 : 6, HI ? 30 : 18).rotateX(Math.PI / 2);
function eyeTexFor(k) {
  if (potEyeTex[k]) return potEyeTex[k]; const c = document.createElement('canvas'); c.width = 256; c.height = 128; const g = c.getContext('2d'), col = (EYE_COLS[k] || EYE_COLS.brown).css;
  const wg = g.createLinearGradient(0, 0, 0, 128); wg.addColorStop(0, '#FFFFFF'); wg.addColorStop(0.55, '#F6F4FA'); wg.addColorStop(1, '#C9C6D8'); g.fillStyle = wg; g.fillRect(0, 0, 256, 128);
  const ig = g.createRadialGradient(64, 66, 4, 64, 64, 27); ig.addColorStop(0, col); ig.addColorStop(0.7, col); ig.addColorStop(1, 'rgba(10,6,14,0.9)'); g.fillStyle = ig; g.beginPath(); g.arc(64, 64, 27, 0, 6.2832); g.fill();
  g.fillStyle = '#0A0610'; g.beginPath(); g.arc(64, 64, 14, 0, 6.2832); g.fill();
  g.fillStyle = '#FFFFFF'; g.beginPath(); g.arc(57, 55, 6, 0, 6.2832); g.fill(); g.globalAlpha = 0.8; g.beginPath(); g.arc(71, 72, 2.6, 0, 6.2832); g.fill();
  return potEyeTex[k] = texOf(c, true);
}
function makePotEyes(D) {
  const g = new THREE.Group(), mat = toon(0xFFFFFF, { map: eyeTexFor('brown') }, { roughness: 0.12 }), cmat = toon(TEAMS[D.team].wet, null, { roughness: 0.14 }), eyes = [];
  for (const sd of [-1, 1]) { const e = new THREE.Group(), ball = new THREE.Mesh(potEyeG, mat), ink = new THREE.Mesh(potEyeG, inkMat), col = new THREE.Mesh(potCollarG, cmat);
    ball.renderOrder = 33; ink.renderOrder = 32.6; e.add(ball, ink); e.position.x = sd * 0.165; col.position.x = sd * 0.165; g.add(e, col); eyes.push({ e, col, sd }); }
  g.visible = false; scene.add(g); return { g, mat, cmat, eyes, k: 0, t: 0, blink: 1.5, iris: 'brown', x: 0, y: 0, z: 0 };
}
function potEyes(D, V, dt) {
  const E = D.potEyes || (D.potEyes = makePotEyes(D)), p = D.pot, show = D.st === 'hide' && !!p && (state !== 'intro' || D.peeked);
  if (show) { E.t += dt; const lq = p.liq ? p.liq.getWorldPosition(potEyeV) : potEyeV.set(p.x, p.y + 0.4, p.z); E.x = p.x; E.y = lq.y; E.z = p.z; } else E.t = 0;
  E.k = show ? Math.min(1, Math.max(0, (E.t - (state === 'intro' ? 0 : 0.28)) / 0.36)) : Math.max(0, E.k - dt / 0.08);
  E.g.visible = E.k > 0.001; if (!E.g.visible) return;
  const look = D === P ? myLook : (V.slime && D.look ? D.look.wearing : null), ik = (look && look.iris) || 'brown';
  if (ik !== E.iris) { E.iris = ik; E.mat.map = eyeTexFor(ik); }
  if (p && p.paintC) E.cmat.color.copy(p.paintC); else E.cmat.color.setHex(TEAMS[D.team].wet);
  // the pair turned to face the camera, so they always read; each eye looks where the blob is looking (glancing about in the countdown)
  const camA = Math.atan2(camera.position.x - E.x, camera.position.z - E.z), W = V.slimeWatchT, wy = W ? V.root.rotation.y + W.yaw : D.yaw;
  let rel = wy - camA; rel = Math.atan2(Math.sin(rel), Math.cos(rel));
  E.blink -= dt; if (E.blink < -0.12) E.blink = 1.6 + Math.random() * 2.8; const shut = E.blink < 0 ? 0.14 : 1;
  const pk = Math.max(0.001, easeElastic(E.k)), bob = Math.sin(clock * 2.4 + D.team * 1.9) * 0.012;
  E.g.position.set(E.x, E.y - 0.035 + bob, E.z); E.g.rotation.y = camA;
  for (const o of E.eyes) { o.e.scale.set(pk, pk * shut, pk); o.e.rotation.set(-0.32 - (W ? clamp(W.pitch - 0.85, -0.3, 0.3) : 0), clamp(rel, -0.75, 0.75), 0); o.col.scale.set(pk, pk * 0.55, pk); o.col.position.y = 0.012 - 0.01 * Math.sin(clock * 3.1 + o.sd); }
}
// each frame, after the blob's own animation has worked out its squash, lean and the rest
function slimeVisual(D, V, dt, sq, rise, rad, gy, hop) {
  const I = V.slime, L = V.look, U = V.U; potEyes(D, V, dt);""")
# under the paint the whole time it's in one (diving down into it mid-match; it bursts back up out of it when it leaps)
rep("  if (under) { V.sink = BASIN_DEEP; V.sinkV = 0; } else if (basin) { const h = Math.min(dt, 0.033); V.sinkV = (V.sinkV || 0) + ((0.4 - V.sink) * 150 - (V.sinkV || 0) * 8.5) * h; V.sink += V.sinkV * h; }\n  else V.sink = (V.sink || 0) + ((inPot ? 0.4 : 0) - (V.sink || 0)) * Math.min(1, dt * (inPot ? 10 : 18));",
    "  if (inPot) { V.sink = basin ? BASIN_DEEP : (V.sink || 0) + (BASIN_DEEP - (V.sink || 0)) * Math.min(1, dt * 7); V.sinkV = 0; }\n  else V.sink = (V.sink || 0) + (0 - (V.sink || 0)) * Math.min(1, dt * 18);")
open(P, 'w').write(src)
print('ok', len(src))
