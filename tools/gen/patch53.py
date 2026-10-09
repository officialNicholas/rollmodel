import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:140])); sys.exit(1)
    s = s.replace(a, b)

# ---------- a plain roll into someone stuns them for 2 seconds ----------
rep("airSling: false, rollT: 0,", "airSling: false, stunT: 0, stunGuard: 0, rollT: 0,")
rep("const canAct = D => D.st === 'play' && D.flatT <= 0;", "const canAct = D => D.st === 'play' && D.flatT <= 0 && !(D.stunT > 0);")
rep("  if (D.flatT > 0) { D.flatT -= dt; D.spd = 0; D.turn = 0;",
    "  if (D.stunGuard > 0) D.stunGuard -= dt;\n  if (D.stunT > 0) { D.stunT -= dt; D.spd = 0; D.turn = 0; D.wob = Math.max(D.wob, 0.5); if (D.stunT <= 0) { D.stunT = 0; D.stunGuard = 1.5; D.squash = 0.6; if (hearable(D)) AU.pop(); } }\n  else if (D.flatT > 0) { D.flatT -= dt; D.spd = 0; D.turn = 0;")
rep("  for (const [A, B] of [[P, H], [H, P]]) if (A.rollT > 0 && (A.giantT > 0 || (A.power && A.power.type === 'roller')) && B.immuneT <= 0 && !(B.rollT > 0)) return knockOut(B, 'crush', A);\n",
    "  for (const [A, B] of [[P, H], [H, P]]) if (A.rollT > 0 && (A.giantT > 0 || (A.power && A.power.type === 'roller')) && B.immuneT <= 0 && !(B.rollT > 0)) return knockOut(B, 'crush', A);\n  for (const [A, B] of [[P, H], [H, P]]) if (A.rollT > 0 && B.giantT <= 0 && B.immuneT <= 0 && !(B.rollT > 0) && !(B.stunT > 0) && !(B.stunGuard > 0) && B.flatT <= 0) return stun(B, A);\n")
rep("// two blobs touching: land on top or hit harder to flatten, otherwise bounce apart", """// rolled into: seeing stars for 2 seconds, can't move or act (a pound will finish you), then a moment where it can't happen again
const STUN_T = 2;
function stun(B, A) {
  if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }
  B.stunT = STUN_T; B.spd = 0; B.turn = 0; B.slam = false; B.squash = 0.8; B.wob = 1; B.kx = B.kz = 0;
  const nx = B.x - A.x, nz = B.z - A.z, d = Math.hypot(nx, nz) || 1; A.yaw = Math.atan2(-nx / d, -nz / d) + (Math.random() - 0.5) * 0.6; A.spd *= 0.4; A.squash = Math.max(A.squash, 0.5);
  for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; spawnPart(B.x, B.y + 0.5, B.z, Math.cos(a) * 2.6, 1 + Math.random() * 1.5, Math.sin(a) * 2.6, 0.4, puHaloMat, 0.5); }
  if (hearable(A) || hearable(B)) { AU.bonk(1); AU.pop(); } hitStop(0.07, A, B);
  if (B === P) { shake = Math.max(shake, 0.3); buzz([25, 30, 25]); banner('Stunned!'); }
  else if (A === P) { shake = Math.max(shake, 0.2); buzz(18); banner('Stunned it!', 'Pound it!'); }
}
// two blobs touching: land on top or hit harder to flatten, otherwise bounce apart""")
# the stars over a stunned head
rep("const lookC = { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 };", """const lookC = { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 };
const starG = (() => { const sh = new THREE.Shape(); for (let i = 0; i < 10; i++) { const a = i / 10 * 6.2832 - Math.PI / 2, r = i % 2 ? 0.045 : 0.11; i ? sh.lineTo(Math.cos(a) * r, Math.sin(a) * r) : sh.moveTo(Math.cos(a) * r, Math.sin(a) * r); } return new THREE.ExtrudeGeometry(sh, { depth: 0.03, bevelEnabled: false }); })(), starM = new THREE.MeshBasicMaterial({ color: 0xFFD86B });
function makeStars() { const g = new THREE.Group(); for (let i = 0; i < 3; i++) g.add(new THREE.Mesh(starG, starM)); g.visible = false; scene.add(g); return g; }
const starsP = makeStars(), starsC = makeStars();
function placeStars(g, D, V) { const on = D.stunT > 0 && D.st === 'play'; g.visible = on; if (!on) return; g.position.set(D.x, D.y + PR * 2.2 * V.gk + 0.15, D.z); g.children.forEach((m, i) => { const a = clock * 5 + i / 3 * 6.2832; m.position.set(Math.cos(a) * 0.36, Math.sin(clock * 9 + i) * 0.04, Math.sin(a) * 0.36); m.rotation.set(0, -a, clock * 4); }); }""")
rep("    const gy = blobVisual(P, VP, dt, ke, kf); VP.flatK = VP.flatK; placeFace(dt);", "    const gy = blobVisual(P, VP, dt, ke, kf); VP.flatK = VP.flatK; placeFace(dt); placeStars(starsP, P, VP);")
rep("    blobVisual(H, VC, dt, ke, kf); placeFaceC(dt);", "    blobVisual(H, VC, dt, ke, kf); placeFaceC(dt); placeStars(starsC, H, VC);")
rep("scared = !happy && (dangerK > 0 || P.wob > 0.6 || P.flatT > 0 ||", "scared = !happy && (dangerK > 0 || P.wob > 0.6 || P.flatT > 0 || P.stunT > 0 ||")
rep("scared = H.flatT > 0 || H.exposed || H.st === 'ko';", "scared = H.flatT > 0 || H.stunT > 0 || H.exposed || H.st === 'ko';")
# the holy water treats you seeing stars like you lying flat: its chance to pound
rep("flat: O.flatT, imm: O.immuneT", "flat: Math.max(O.flatT, O.stunT || 0), imm: O.immuneT")
# and it can roll into you too, mostly when its pound is ready to follow up
rep("  if ((D.giantT > 0.4 || (D.power && D.power.type === 'roller')) && D.rollCD <= 0 && !D.air && O.st === 'play' && O.immuneT <= 0 && !(O.rollT > 0) && Math.abs(O.y - D.y) < 0.8) {",
    "  const big = D.giantT > 0.4 || (D.power && D.power.type === 'roller'), stunOK = !big && slamReady(D) && O.giantT <= 0 && !(O.stunT > 0) && !(O.stunGuard > 0) && O.flatT <= 0;\n  if ((big || stunOK) && D.rollCD <= 0 && !D.air && O.st === 'play' && O.immuneT <= 0 && !(O.rollT > 0) && Math.abs(O.y - D.y) < 0.8) {")
rep("if (d < (D.giantT > 0 ? 3.6 : 2.6) && err < 0.4 && rollSafe(D) && Math.random() < dt * 2.5 * AI.ram)", "if (d < (D.giantT > 0 ? 3.6 : big ? 2.6 : 2.3) && err < (big ? 0.4 : 0.3) && rollSafe(D) && Math.random() < dt * (big ? 2.5 : 1.2) * AI.ram)")
rep("<span>Pound to splat a circle.", "<span>Roll into the holy water to stun it for 2 seconds. Pound to splat a circle.")
# the missile's landing marker is orange, not the pound's white
rep("if (!aiming && P.slam) { aimIn.material.color.setHex(0xFFFFFF);", "if (!aiming && P.slam) { aimIn.material.color.setHex(P.missile ? 0xFFB14A : 0xFFFFFF);")
rep("  D.st = 'ko'; D.rollT = 0;", "  D.st = 'ko'; D.rollT = 0; D.stunT = 0;")
open(F, 'w').write(s)
print('ok')
