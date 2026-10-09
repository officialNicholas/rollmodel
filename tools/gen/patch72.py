import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# paint crowns: a few shapes per size are made once and reused, instead of building a new mesh every impact
rep("function spawnCrown(D, R) {\n  const g = new THREE.Group(), geo = crownGeo(R * 0.5, R * 0.95, Math.min(3.4, R * 0.5), (Math.random() * 1e5) | 0);",
    "const crownCache = new Map();\nfunction crownGeoFor(R) { const key = R.toFixed(2); let l = crownCache.get(key); if (!l) crownCache.set(key, l = []); if (l.length < 3) { const g = crownGeo(R * 0.5, R * 0.95, Math.min(3.4, R * 0.5), (Math.random() * 1e5) | 0); l.push(g); return g; } return l[(Math.random() * l.length) | 0]; }\nfunction spawnCrown(D, R) {\n  const g = new THREE.Group(), geo = crownGeoFor(R);")
rep("    if (t > 1.15) { scene.remove(c.g); c.geo.dispose(); crowns.splice(i, 1); }", "    if (t > 1.15) { scene.remove(c.g); crowns.splice(i, 1); }")
open(F, 'w').write(s)
print('ok')
