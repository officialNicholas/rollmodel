import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# only the clouds in view go into the instance lists
rep("""  for (const c of clouds) { c.m.position.x += c.v * dt; if (c.m.position.x > 160) c.m.position.x -= 320; c.m.updateMatrix(); cloudIMs[c.vi].setMatrixAt(c.k, c.m.matrix); }
  for (const im of cloudIMs) im.instanceMatrix.needsUpdate = true;""",
"""  cloudFr.setFromProjectionMatrix(tmpM4.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse));
  for (const im of cloudIMs) im.count = 0;
  for (const c of clouds) { c.m.position.x += c.v * dt; if (c.m.position.x > 160) c.m.position.x -= 320; cloudSph.center.copy(c.m.position); cloudSph.radius = c.m.scale.x * 3.6; if (!cloudFr.intersectsSphere(cloudSph)) continue; c.m.updateMatrix(); const im = cloudIMs[c.vi]; im.setMatrixAt(im.count++, c.m.matrix); }
  for (const im of cloudIMs) { im.visible = im.count > 0; im.instanceMatrix.needsUpdate = true; }""")
rep("const cloudMat = toon(0xD9D4F2), clouds = [], islands = []; let cloudIMs = [];",
    "const cloudMat = toon(0xD9D4F2), clouds = [], islands = []; let cloudIMs = []; const cloudFr = new THREE.Frustum(), cloudSph = new THREE.Sphere(), tmpM4 = new THREE.Matrix4();")
open(F, 'w').write(s)
print('ok')
