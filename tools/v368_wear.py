"""v368: the scarf, the pearl necklace, the bow tie and the hero cape fitted to the axolotl's neck.

- The neck pieces were pinned "under the chin": a point low on the front of the head, from when the character was a round head on a
  small body. On today's axolotl, with its big head and the neck tucked under the back of it, that point is its mouth. The scarf sat
  round its snout like a muzzle with the end hanging off its lip, the pearls were drawn inside its head (they never showed), and the
  bow tie sat on its chin.
- Now they go round its neck: the line from the chest joint to the head's, under the back of the head. The scarf wraps it, its end
  hanging straight down from the front whichever way the neck is tipped; the pearls hang across the throat and run up the sides of the
  neck; the bow tie sits at the throat. They turn and give with the neck.
- The hero cape started at the chest joint, behind the shoulders, so it lay on the back like a saddle cloth with bare body between it and
  the head. It now starts at the neck, tucked under the back of the head, with a gold cord round the neck and a gold button at the
  throat, turned to face forward (the clasp was a thin ring).
- The scarf's loop is chunkier, a knitted scarf rather than a cord."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the axolotl's neck: a point on the chest-to-head line and a frame on it
    s = rep(s, "  return { S, load, make, update, headTop, headSize, bodyPoint, backPoint, boneAt, headR0: HEAD_R0, faceK: 1.18 };",
               "  // (v368) its neck, for what's worn round it: a point s of the way along the line from the chest joint to the head's, and a frame there\n"
               "  // with its y up that line (toward the head) and its z out of the throat (down, square to the neck), in the body's space. Returns\n"
               "  // the line's length, the unit the neck pieces are sized in\n"
               "  const _nc = new THREE.Vector3(), _nh = new THREE.Vector3(), _nd = new THREE.Vector3(), _nf = new THREE.Vector3(), _nx = new THREE.Vector3(), _nm = new THREE.Matrix4();\n"
               "  function neckFrame(I, s, out, quat) { boneAt(I, 'chest', _nc); boneAt(I, 'head', _nh); _nd.subVectors(_nh, _nc); const L = _nd.length() || 1; _nd.divideScalar(L); out.copy(_nc).addScaledVector(_nd, s * L);\n"
               "    if (quat) { _nf.set(0, -1, 0).addScaledVector(_nd, _nd.y).normalize(); _nx.crossVectors(_nd, _nf); _nm.makeBasis(_nx, _nd, _nf); quat.setFromRotationMatrix(_nm); } return L; }\n"
               "  return { S, load, make, update, headTop, headSize, bodyPoint, backPoint, boneAt, neckFrame, headR0: HEAD_R0, faceK: 1.18 };")

    # how they sit (window.__neckFit: a tuning hook); lengths in neck lengths (the chest-to-head line)
    s = rep(s, "const CAPE_REST = ",
               "// (v368) round the axolotl's neck (in neck lengths, the chest-to-head line): s how far up it they sit; the scarf's size (ss) and its\n"
               "// loop's shape across, along and out of the throat (lx, ly, lz); the pearls' size, how far up and out (ps, py, pz) and their tilt (pt);\n"
               "// the bow tie's likewise (bs, by, bz, bt); the cape's cord: its size across and out (cx, cz) and how far up (cs), and its clasp's tilt up from the throat to face forward (ct)\n"
               "const NECK_FIT = window.__neckFit || { s: 0.6, ss: 0.78, sy: 0, sz: 0, lx: 1, ly: 1, lz: 1, ps: 0.9, py: 0, pz: 0.52, pt: 0, bs: 0.95, by: 0.12, bz: 0.55, bt: 0, cs: 0.6, cx: 0.5, cz: 0.55, ct: -0.6 };\n"
               "// the scarf's end hangs straight down from the front of its loop however the neck is tipped, swinging a little\n"
               "const XAX = new THREE.Vector3(1, 0, 0), SCARF_PIN = new THREE.Vector3(0.26, -0.15, 0.72), _shD = new THREE.Vector3(), _shQ = new THREE.Quaternion(), _shP = new THREE.Vector3(), _shN = new THREE.Vector3();\n"
               "function scarfHang(o, q, t, F) { const gin = o.userData.gin; if (!gin || gin.children.length < 3) return; const loop = gin.children[0]; loop.scale.set(F.lx, F.ly, F.lz);\n"
               "  _shD.set(0, -1, 0).applyQuaternion(_shQ.copy(q).invert()); const a = Math.atan2(-_shD.z, -_shD.y) + Math.sin(t * 2.3) * 0.05, b = Math.sin(t * 1.7 + 1) * 0.06;\n"
               "  _shN.set(SCARF_PIN.x * F.lx, SCARF_PIN.y * F.ly, SCARF_PIN.z * F.lz);\n"
               "  for (const m of [gin.children[1], gin.children[2]]) { m.rotation.set(a, 0, b); m.position.copy(_shN).sub(_shP.copy(SCARF_PIN).applyEuler(m.rotation)); } }\n"
               "const CAPE_REST = ")

    # the neck pieces round the neck on the axolotl (the slime, if it's ever the fallback, keeps them under its chin)
    a = ("    if (W.bow.visible && CH.bodyPoint(SI, 0, -0.03, 0.835, wv1)) {")
    i = s.index(a); j = s.index("\n", s.index("    if (W.pearls.visible && CH.bodyPoint(SI, 0, -0.03, 0.835, wv1))", i)) + 1
    old = s[i:j]; assert old.count("\n") == 3, old.count("\n")
    s = s[:i] + (
        "    // (v368) on the axolotl round its neck, under the back of its head: under its chin they were at its mouth (the scarf round its\n"
        "    // snout, the pearls inside its head)\n"
        "    if (CH.neckFrame && (W.bow.visible || W.scarf.visible || W.pearls.visible)) {\n"
        "      const F = NECK_FIT, L = CH.neckFrame(SI, F.s, wv1, wq1); wq1.multiply(wq2.setFromEuler(wearE.set(S.tx * 0.25, 0, Math.sin(t * 2.1) * 0.03 + S.tz * 0.3)));\n"
        "      if (W.scarf.visible) { W.scarf.position.copy(wv1).add(wv2.set(0, F.sy * L, F.sz * L).applyQuaternion(wq1)); W.scarf.quaternion.copy(wq1); W.scarf.scale.multiplyScalar(F.ss * L); scarfHang(W.scarf, wq1, t, F); }\n"
        "      if (W.pearls.visible) { W.pearls.position.copy(wv1).add(wv2.set(0, F.py * L, F.pz * L).applyQuaternion(wq1)); W.pearls.quaternion.copy(wq1).multiply(wq2.setFromAxisAngle(XAX, F.pt)); W.pearls.scale.multiplyScalar(F.ps * L); }\n"
        "      if (W.bow.visible) { W.bow.position.copy(wv1).add(wv2.set(0, F.by * L, F.bz * L).applyQuaternion(wq1)); W.bow.quaternion.copy(wq1).multiply(wq2.setFromAxisAngle(XAX, F.bt)); W.bow.scale.multiplyScalar(F.bs * L); }\n"
        "    } else {\n"
        + old.replace("    if (", "      if (") +
        "    }\n") + s[j:]

    # the cape from the neck: the neck joint first, then down the spine; a cord round the neck and the clasp at the throat
    s = rep(s, "      if (W.cape.visible) { const P4 = W.cape.userData.pts || (W.cape.userData.pts = [0, 1, 2, 3, 4].map(() => new THREE.Vector3())); CH.boneAt(SI, 'chest', P4[0]); CH.boneAt(SI, 'spine1', P4[1]); CH.boneAt(SI, 'spine', P4[2]); CH.boneAt(SI, 'hips', P4[3]); CH.boneAt(SI, 'tail1', P4[4]);\n"
               "        capeLay(W.cape.userData.geo, P4, t, D.spd || 0); W.cape.position.set(0, 0, 0); W.cape.quaternion.identity(); W.cape.userData.clasp.position.copy(P4[0]).add(wv1.set(0, 0.37, 0.02)); W.cape.userData.clasp.rotation.set(-1.2, 0, 0); } }",
               "      if (W.cape.visible) { const P4 = W.cape.userData.pts || (W.cape.userData.pts = [0, 1, 2, 3, 4, 5].map(() => new THREE.Vector3())); CH.boneAt(SI, 'neck', P4[0]); CH.boneAt(SI, 'chest', P4[1]); CH.boneAt(SI, 'spine1', P4[2]); CH.boneAt(SI, 'spine', P4[3]); CH.boneAt(SI, 'hips', P4[4]); CH.boneAt(SI, 'tail1', P4[5]);\n"
               "        capeLay(W.cape.userData.geo, P4, t, D.spd || 0); W.cape.position.set(0, 0, 0); W.cape.quaternion.identity();\n"
               "        // (v368) tied on: a gold cord round the neck and the clasp at the throat\n"
               "        const cl = W.cape.userData.clasp, cd = W.cape.userData.cord, F = NECK_FIT;\n"
               "        if (CH.neckFrame) { const L = CH.neckFrame(SI, F.cs, wv1, wq1); cd.visible = true; cd.position.copy(wv1); cd.quaternion.copy(wq1); cd.scale.set(F.cx * L, F.cx * L, F.cz * L);\n"
               "          cl.position.copy(wv1).add(wv2.set(0, 0, F.cz * L * 1.02).applyQuaternion(wq1)); cl.quaternion.copy(wq1).multiply(wq2.setFromAxisAngle(XAX, F.ct)); cl.scale.setScalar(L * 0.9); }\n"
               "        else { cd.visible = false; cl.position.copy(P4[1]).add(wv1.set(0, 0.37, 0.02)); cl.rotation.set(-1.2, 0, 0); cl.scale.setScalar(1); } } }")
    s = rep(s, "    const cl = new THREE.Mesh(new THREE.TorusGeometry(0.1, 0.04, 8, 20), claspMat), o = new THREE.Mesh(cl.geometry, inkMat); o.renderOrder = 32.6; cl.add(o); cl.renderOrder = 33; cape.add(cl); cape.userData.clasp = cl; }",
               "    // (v368) the clasp a gold button, a domed boss in a raised rim (it was a thin ring), on a gold cord round the neck\n"
               "    const claspG = new THREE.LatheGeometry([[0, -0.03], [0.1, -0.03], [0.125, -0.006], [0.122, 0.02], [0.104, 0.03], [0.088, 0.022], [0.06, 0.04], [0, 0.05]].map(([x, y]) => new THREE.Vector2(x, y)), 28).rotateX(Math.PI / 2);\n"
               "    const cl = new THREE.Mesh(claspG, claspMat), o = new THREE.Mesh(cl.geometry, inkMat); o.renderOrder = 32.6; cl.add(o); cl.renderOrder = 33; cape.add(cl); cape.userData.clasp = cl;\n"
               "    const cd = new THREE.Mesh(new THREE.TorusGeometry(1, 0.06, 8, 48).rotateX(Math.PI / 2), claspMat), co = new THREE.Mesh(cd.geometry, inkMat); co.renderOrder = 32.6; cd.add(co); cd.renderOrder = 33; cape.add(cd); cape.userData.cord = cd; }")

    # the cape's shape over six points now, the neck first: gathered round the neck, then as before
    s = rep(s, "const q = Math.min(3.999, u * 4), j = Math.floor(q), m = q - j, at = K => K[j] + (K[j + 1] - K[j]) * m",
               "const NK = CAPE_A.length - 1, q = Math.min(NK - 0.001, u * NK), j = Math.floor(q), m = q - j, at = K => K[j] + (K[j + 1] - K[j]) * m")
    s = rep(s, "const CAPE_A = [0.62, 0.74, 0.72, 0.55, 0.5], CAPE_B = [0.36, 0.32, 0.29, 0.38, 0.3], CAPE_PM = [0.6, 1.45, 1.45, 1.1, 1.45];",
               "const CAPE_A = window.__capeA || [0.42, 0.62, 0.74, 0.72, 0.55, 0.5], CAPE_B = window.__capeB || [0.3, 0.36, 0.32, 0.29, 0.38, 0.3], CAPE_PM = window.__capePM || [0.75, 1.0, 1.45, 1.45, 1.1, 1.45]; // (v368: and from the neck, the first)")
    s = rep(s, "const CAPE_REST = [[0, 0, 0], ", "const CAPE_REST = [[0, 0.27, 0.35], [0, 0, 0], ")
    # the scarf's loop chunkier: a fatter tube and a band a little taller along the neck, so it reads as a knitted scarf, not a cord
    s = rep(s, "\nconst scarfParts = (() => { const loop = new THREE.TorusGeometry(0.72, 0.19, 12, 36).rotateX(Math.PI / 2).scale(1, 1, 0.92),",
               "\n// (v368) the scarf's loop chunkier: a fatter tube and a band a little taller along the neck, a knitted scarf rather than a cord\n"
               "const scarfParts = (() => { const loop = new THREE.TorusGeometry(0.72, 0.27, 14, 40).rotateX(Math.PI / 2).scale(1, 1.18, 0.92),")
    # the cape's comments: it starts at the neck now
    s = rep(s, "(pts: body-space points from the shoulders back)", "(pts: body-space points from the neck back)")
    s = rep(s, "how far round (PM, radians from the top), at the chest, the middle of the back,", "how far round (PM, radians from the top), at the neck, the chest, the middle of the back,")
    return s
