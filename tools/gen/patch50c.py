import sys, re
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:140])); sys.exit(1)
    s = s.replace(a, b)

# ---------- the characters: bigger sticker eyes, rosy cheeks and a gloss on you, no halo on the holy water ----------
rep("""const eyeW = toon(0xffffff, { transparent: true }), eyeB = new THREE.MeshBasicMaterial({ color: C.outline, transparent: true }), shineM = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true }), eyes = [];
[-1, 1].forEach(sd => {
  const e = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 12), eyeW); e.renderOrder = 33; body.add(e);
  const pu = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 10), eyeB); pu.renderOrder = 34; body.add(pu);
  const sh = new THREE.Mesh(new THREE.SphereGeometry(0.034, 8, 6), shineM); sh.renderOrder = 35; sh.position.set(0.035, 0.04, 0.085); pu.add(sh);
  eyes.push({ e, pu, base: new THREE.Vector3(sd * 0.36, 0.5, 0.79).normalize() });
});""", """// big sticker eyes: flat white (unshaded, so they stay white at night), a dark rim, glossy pupils with two catchlights
const eyeW = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true }), eyeB = new THREE.MeshBasicMaterial({ color: C.outline, transparent: true }), shineM = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true }), eyeRimM = new THREE.MeshBasicMaterial({ color: C.outline, side: THREE.BackSide, transparent: true }), eyes = [];
const eyeG = new THREE.SphereGeometry(0.215, 20, 14), pupG = new THREE.SphereGeometry(0.118, 14, 10), shineG = new THREE.SphereGeometry(0.044, 8, 6), shine2G = new THREE.SphereGeometry(0.022, 8, 6);
function makeEye(parent) {
  const e = new THREE.Mesh(eyeG, eyeW); e.renderOrder = 33; parent.add(e);
  const rim = new THREE.Mesh(eyeG, eyeRimM); rim.scale.setScalar(1.17); rim.renderOrder = 32.5; e.add(rim);
  const pu = new THREE.Mesh(pupG, eyeB); pu.renderOrder = 34; parent.add(pu);
  const sh = new THREE.Mesh(shineG, shineM); sh.renderOrder = 35; sh.position.set(0.042, 0.046, 0.1); pu.add(sh);
  const sh2 = new THREE.Mesh(shine2G, shineM); sh2.renderOrder = 35; sh2.position.set(-0.046, -0.042, 0.1); pu.add(sh2);
  return { e, pu };
}
[-1, 1].forEach(sd => { const { e, pu } = makeEye(body); eyes.push({ e, pu, base: new THREE.Vector3(sd * 0.37, 0.45, 0.8).normalize() }); });
// rosy cheeks and a glossy highlight
const cheekM = new THREE.MeshBasicMaterial({ color: 0xFF9EC4, transparent: true, opacity: 0.55, depthWrite: false }), cheekG = new THREE.SphereGeometry(0.075, 12, 8), cheeks = [];
[-1, 1].forEach(sd => { const m = new THREE.Mesh(cheekG, cheekM); m.renderOrder = 33; body.add(m); cheeks.push({ m, base: new THREE.Vector3(sd * 0.62, 0.17, 0.77).normalize() }); });
const glintM = new THREE.MeshBasicMaterial({ color: 0xFFFFFF, transparent: true, opacity: 0.8 }), glintG = new THREE.SphereGeometry(0.16, 12, 8), glint2G = new THREE.SphereGeometry(0.06, 8, 6);
const pGlint = new THREE.Mesh(glintG, glintM), pGlint2 = new THREE.Mesh(glint2G, glintM); pGlint.renderOrder = 33; pGlint2.renderOrder = 33; body.add(pGlint); body.add(pGlint2);""")

rep("""// ---------- the holy water: a glassy blue blob with a little gold halo ----------""", """// ---------- the holy water: a glassy blue blob with stern little brows ----------""")
rep("""const cGlint = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 8), new THREE.MeshBasicMaterial({ color: 0xFFFFFF, transparent: true, opacity: 0.85 })); cGlint.renderOrder = 33; cBody.add(cGlint);
const cEyes = [];
[-1, 1].forEach(sd => {
  const e = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 12), eyeW); e.renderOrder = 33; cBody.add(e);
  const pu = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 10), eyeB); pu.renderOrder = 34; cBody.add(pu);
  const br = new THREE.Mesh(new THREE.BoxGeometry(0.26, 0.055, 0.05), eyeB); br.renderOrder = 34; cBody.add(br);
  cEyes.push({ e, pu, br, sd, base: new THREE.Vector3(sd * 0.36, 0.5, 0.79).normalize() });
});
const cMouth = new THREE.Mesh(new THREE.TorusGeometry(0.08, 0.026, 6, 14, Math.PI), eyeB); cMouth.rotation.z = Math.PI; cMouth.renderOrder = 34; cBody.add(cMouth);
const haloMat = toon(0xFFD86B, { emissive: 0x6A4A00 }), cHalo = new THREE.Group();
(() => { const tg = new THREE.TorusGeometry(0.34, 0.055, 10, 36).rotateX(Math.PI / 2); cHalo.add(new THREE.Mesh(tg, haloMat)); const o = new THREE.Mesh(tg, outlineMat); o.scale.set(1.08, 1.6, 1.08); cHalo.add(o); })();
cDrop.add(cHalo); scene.add(cDrop);""", """const cGlint = new THREE.Mesh(glintG, new THREE.MeshBasicMaterial({ color: 0xFFFFFF, transparent: true, opacity: 0.85 })); cGlint.renderOrder = 33; cBody.add(cGlint);
const cGlint2 = new THREE.Mesh(glint2G, cGlint.material); cGlint2.renderOrder = 33; cBody.add(cGlint2);
const cEyes = [];
[-1, 1].forEach(sd => {
  const { e, pu } = makeEye(cBody);
  const br = new THREE.Mesh(new THREE.BoxGeometry(0.29, 0.068, 0.05), eyeB); br.renderOrder = 34; cBody.add(br);
  cEyes.push({ e, pu, br, sd, base: new THREE.Vector3(sd * 0.37, 0.45, 0.8).normalize() });
});
const cMouth = new THREE.Mesh(new THREE.TorusGeometry(0.095, 0.033, 8, 16, Math.PI), eyeB); cMouth.rotation.z = Math.PI; cMouth.renderOrder = 34; cBody.add(cMouth);
scene.add(cDrop);""")
rep("    cHalo.position.set(0, PR * 2.05 * VC.gk * (1 - 0.6 * VC.flatK) + Math.sin(clock * 3) * 0.04, 0); cHalo.rotation.set(0.25 + Math.sin(clock * 1.7) * 0.08, clock * 1.2, 0);\n", "")

# faces
rep("  const happy = P.st === 'hide' || celebrating, scared = !happy && (dangerK > 0 || P.wob > 0.6 || P.flatT > 0 || P.st === 'ko' || (P.air && P.vy < -7) || (P.st === 'play' && P.paint < 0.15) || P.exposed), strain = P.charging;",
    "  const happy = P.st === 'hide' || celebrating || menuReact > 0, scared = !happy && (dangerK > 0 || P.wob > 0.6 || P.flatT > 0 || P.st === 'ko' || (P.air && P.vy < -7) || (P.st === 'play' && P.paint < 0.15) || P.exposed), strain = P.charging || P.rollT > 0;")
rep("""  for (const f of fangs) { const sd = f.userData.sd; f.position.copy(mp).add(openO ? tv1.set(sd * 0.036, scared ? 0.075 : 0.05, 0.01) : tv1.set(sd * (happy ? 0.07 : 0.052), happy ? -0.035 : -0.012, 0.012)); f.scale.setScalar(happy ? 1.15 : 1); }
}""", """  for (const f of fangs) { const sd = f.userData.sd; f.position.copy(mp).add(openO ? tv1.set(sd * 0.036, scared ? 0.075 : 0.05, 0.01) : tv1.set(sd * (happy ? 0.07 : 0.052), happy ? -0.035 : -0.012, 0.012)); f.scale.setScalar(happy ? 1.15 : 1); }
  for (const c of cheeks) { c.m.position.copy(gooJS(c.base)); c.m.scale.set(1, happy ? 0.5 : 0.62, 0.32); }
  pGlint.position.copy(gooJS(tv2.set(-0.45, 0.6, 0.52).normalize())); pGlint.scale.set(1, 0.68, 0.4);
  pGlint2.position.copy(gooJS(tv2.set(-0.64, 0.3, 0.6).normalize())); pGlint2.scale.set(1, 1, 0.5);
}""")
rep("    it.br.position.copy(p).multiplyScalar(1.05).add(tv1.set(0, 0.2, 0.02));", "    it.br.position.copy(p).multiplyScalar(1.05).add(tv1.set(0, 0.24, 0.02));")
rep("  const gp = gooJS(tv2.set(-0.42, 0.62, 0.55).normalize(), gooU2); cGlint.position.copy(gp).multiplyScalar(1.0); cGlint.scale.set(1, 0.7, 0.4);",
    "  const gp = gooJS(tv2.set(-0.42, 0.62, 0.55).normalize(), gooU2); cGlint.position.copy(gp); cGlint.scale.set(1, 0.7, 0.4);\n  cGlint2.position.copy(gooJS(tv2.set(-0.62, 0.32, 0.6).normalize(), gooU2)); cGlint2.scale.set(1, 1, 0.5);")

# body animation: idle hops in the menu, a spin-hop when you pick a color, a forward tumble when you roll
rep("""  U.gSpd.value = L.spd; U.gLean.value = L.lean; U.gDrop.value = L.drop; U.gFlat.value = L.flat;
  let sq = D.charging ? Math.max(D.squash, 0.15 + 0.48 * D.charge) : D.squash;
  if (state === 'menu') sq = Math.max(0, Math.sin(clock * 3 + (D.cpu ? 1.5 : 0))) * 0.35;
  U.gSquash.value = sq; U.gRise.value = rising ? clamp(D.vy / JUMP_V, 0, 1) : 0;
  if (D.charging) U.gWob.value = 0.6 + D.charge * 1.4;
  const hop = D === P && celebrating ? Math.abs(Math.sin(clock * 7)) * 0.6 : 0, fk = V.flatK;""",
"""  U.gSpd.value = D.rollT > 0 ? 0.2 : L.spd; U.gLean.value = L.lean; U.gDrop.value = L.drop; U.gFlat.value = L.flat;
  let sq = D.charging ? Math.max(D.squash, 0.15 + 0.48 * D.charge) : D.squash, hop = D === P && celebrating ? Math.abs(Math.sin(clock * 7)) * 0.6 : 0, spinY = D === P && celebrating ? clock * 3 : 0, rise = rising ? clamp(D.vy / JUMP_V, 0, 1) : 0;
  if (state === 'menu') {
    // idle: a little hop every second or so, squashing on the landing; picking a color sends you up in a spin
    const ph = (clock * 0.85 + (D.cpu ? 0.47 : 0)) % 1;
    hop = ph < 0.3 ? Math.sin(ph / 0.3 * Math.PI) * 0.16 : 0; rise = ph < 0.15 ? 0.5 : 0;
    sq = ph < 0.3 ? 0 : ph < 0.44 ? (1 - (ph - 0.3) / 0.14) * 0.42 : ph > 0.9 ? (ph - 0.9) / 0.1 * 0.2 : 0;
    if (D === P && menuReact > 0) { const u = 1 - menuReact / 0.7; hop = Math.sin(u * Math.PI) * 0.6; spinY = u * 6.2832; sq = u > 0.85 ? (u - 0.85) / 0.15 * 0.5 : 0; rise = u < 0.4 ? 0.7 : 0; }
  }
  U.gSquash.value = sq; U.gRise.value = rise;
  if (D.charging) U.gWob.value = 0.6 + D.charge * 1.4;
  const fk = V.flatK;""")
rep("  V.root.rotation.set(-0.85 * V.misK, D.yaw + (D === P && celebrating ? clock * 3 : 0), 0);",
    "  V.root.rotation.set(-0.85 * V.misK + (D.rollT > 0 ? 6.2832 * (1 - Math.pow(D.rollT / ROLL_T, 2)) : 0), D.yaw + spinY, 0);")
open(F, 'w').write(s)
print('ok')
