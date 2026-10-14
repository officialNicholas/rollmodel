"""v285: the first launch, two details at the drum (a patch over the intro, tools/v257_intro.js).
- Its ear went into the drum: where its head comes up out of the puddle was a short reach from the tipped drum's mouth, and a floppy
  ear swung through the rim. That spot (the puddle, the ring it comes up through, the ripples and the camera's close shot all go by
  it) is 10 cm further out from the mouth, along the way the paint ran.
- A line of the pearly paint is left along the inside of the drum, down the side it lies on, from the closed end to the mouth and
  thickening toward it, with a wavering edge; darker deep inside, where little light gets. So the paint plainly came out of there."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

STRIP = """const g = new THREE.Group(); g.add(body, lid);
    // (v285) the paint it poured out: a line of it left along the inside, down the side it lies on, thickening toward the mouth; darker
    // deep inside, where little light reaches
    { const dn = new V3(0, -1, 0).applyQuaternion(new THREE.Quaternion().setFromAxisAngle(TIPAX, Math.PI / 2).invert()), a0 = Math.atan2(dn.z, dn.x), rows = 26, cols = 6, pos = [], col = [];
      const at = (u, c) => { const y = 0.07 + u * (H - 0.075), w = (0.03 + 0.085 * u * u) * (1 + 0.18 * Math.sin(y * 37 + 1.3) + 0.1 * Math.sin(y * 91)), sx = c / cols * 2 - 1, ang = a0 + sx * w / R, r = R - 0.013 - 0.006 * (1 - sx * sx); return [Math.cos(ang) * r, y, Math.sin(ang) * r]; };
      for (let i = 0; i < rows; i++) for (let c = 0; c < cols; c++) { const A = at(i / rows, c), B = at(i / rows, c + 1), C = at((i + 1) / rows, c), D = at((i + 1) / rows, c + 1); pos.push(...A, ...C, ...B, ...B, ...C, ...D);
        for (const u of [i, i + 1, i, i, i + 1, i + 1]) { const k = 0.3 + 0.7 * Math.pow(u / rows, 1.3); col.push(k, k, k); } }
      const pg = new THREE.BufferGeometry(); pg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); pg.setAttribute('color', new THREE.Float32BufferAttribute(col, 3)); pg.computeVertexNormals();
      g.add(new THREE.Mesh(pg, dofMap(new THREE.MeshStandardMaterial({ color: PEARL, vertexColors: true, roughness: 0.2, metalness: 0.08, side: THREE.DoubleSide })))); }
    return { g, body, lid };"""

def apply(s):
    # where its head comes up: 10 cm further out from the drum's mouth, along the way the paint ran (TIP is (0.93, 0, 0.36), normalised)
    s = rep(s, "C0 = new V3(0.72, 0, 0.26)", "C0 = new V3(0.813, 0, 0.296)")
    s = rep(s, "const g = new THREE.Group(); g.add(body, lid); return { g, body, lid };", STRIP)
    return s
