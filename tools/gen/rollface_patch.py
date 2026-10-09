# a gentler roll morph (a shorter, rounder roller), and the face drawn closer together while rolling so it stays a face
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
rep("  p.x = sign(p.x) * mix(ax, pow(ax, 0.42), gRoll) * (1.0 + 1.25 * gRoll); p.y *= 1.0 - 0.1 * gRoll; p.z *= 1.0 - 0.06 * gRoll;",
    "  p.x = sign(p.x) * mix(ax, pow(ax, 0.5), gRoll) * (1.0 + 0.85 * gRoll); p.y *= 1.0 - 0.08 * gRoll; p.z *= 1.0 - 0.05 * gRoll;")
rep("  const ax = Math.abs(p.x); p.x = Math.sign(p.x) * (ax + (Math.pow(ax, 0.42) - ax) * g('gRoll')) * (1 + 1.25 * g('gRoll')); p.y *= 1 - 0.1 * g('gRoll'); p.z *= 1 - 0.06 * g('gRoll');",
    "  const ax = Math.abs(p.x); p.x = Math.sign(p.x) * (ax + (Math.pow(ax, 0.5) - ax) * g('gRoll')) * (1 + 0.85 * g('gRoll')); p.y *= 1 - 0.08 * g('gRoll'); p.z *= 1 - 0.05 * g('gRoll');")
# the face's sheet coordinates squeezed toward the middle as the body stretches
rep("""const FACE_FS = `
float faceInk = 0.0;
if (vSph.z > 0.2) {""", """const FACE_FS = `
float faceInk = 0.0;
vec2 fsp = vec2(vSph.x * (1.0 + 1.6 * gRoll), vSph.y);
if (vSph.z > 0.2) {""")
a = s.index("const FACE_FS = `"); b = s.index("}`;", a)
body = s[a:b].replace("vSph.xy", "fsp")
s = s[:a] + body + s[b:]
rep("'#include <common>\\nvarying vec3 vSph; uniform sampler2D uFaceTex; uniform vec4 uFace, uFace2;'", "'#include <common>\\nvarying vec3 vSph; uniform sampler2D uFaceTex; uniform vec4 uFace, uFace2; uniform float gRoll;'")
# the 3D eyes follow: their anchors come in toward the middle by the same amount
rep("function setFace(U, cell, size, arcs) {", "const FA = new THREE.Vector3(), faceAt = (v, U) => { const r = U.gRoll.value; if (r < 0.01) return v; FA.copy(v); FA.x /= 1 + 1.6 * r; return FA.normalize(); };\nfunction setFace(U, cell, size, arcs) {")
rep("    const p = gooJS(cyc ? tv3.set(0, 0.47, 0.88).normalize() : it.base, gooU);", "    const p = gooJS(cyc ? tv3.set(0, 0.47, 0.88).normalize() : faceAt(it.base, gooU), gooU);")
rep("    const p = gooJS(it.base, gooU2);", "    const p = gooJS(faceAt(it.base, gooU2), gooU2);")
rep("    const p = gooJS(it.base, U);", "    const p = gooJS(faceAt(it.base, U), U);")
# the rig's caps and arm move in to the new ends
rep("const cap = sd => new THREE.LatheGeometry([[0.001, -0.07], [0.62, -0.07], [0.94, -0.05], [1.0, 0], [0.94, 0.05], [0.6, 0.08], [0.22, 0.09], [0.2, 0.16], [0.001, 0.16]].map(q => V2(q[0], q[1])), seg).rotateZ(-sd * Math.PI / 2).translate(sd * 2.2, 0, 0);",
    "const cap = sd => new THREE.LatheGeometry([[0.001, -0.07], [0.62, -0.07], [0.94, -0.05], [1.0, 0], [0.94, 0.05], [0.6, 0.08], [0.22, 0.09], [0.2, 0.16], [0.001, 0.16]].map(q => V2(q[0], q[1])), seg).rotateZ(-sd * Math.PI / 2).translate(sd * 1.8, 0, 0);")
rep("const wire = new THREE.TubeGeometry(new THREE.CatmullRomCurve3([V3(2.25, 0, 0), V3(2.62, 0, 0), V3(2.78, 0.45, -0.36), V3(2.25, 1.12, -0.95), V3(1.25, 1.42, -1.2), g0.clone().addScaledVector(gd, -0.05)], false, 'centripetal'), HI ? 32 : 16, 0.07, HI ? 8 : 5);",
    "const wire = new THREE.TubeGeometry(new THREE.CatmullRomCurve3([V3(1.85, 0, 0), V3(2.2, 0, 0), V3(2.36, 0.45, -0.36), V3(1.9, 1.12, -0.95), V3(1.05, 1.42, -1.2), g0.clone().addScaledVector(gd, -0.05)], false, 'centripetal'), HI ? 32 : 16, 0.07, HI ? 8 : 5);")
rep("const g0 = V3(0.9, 1.45, -1.25), gd = V3(-0.28, 0.42, -0.86).normalize()", "const g0 = V3(0.72, 1.45, -1.25), gd = V3(-0.28, 0.42, -0.86).normalize()")
open(p, 'w').write(s)
print('ok')
