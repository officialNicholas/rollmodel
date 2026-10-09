# The character, cuter again (like the first builds) and outlined like the stage:
#  - a thin ink outline round every blob in Graphics mode too, drawn after the jelly so it never shows through it; its width is
#    worked out from distance, so it's the same couple of pixels in play as in a close-up
#  - big glossy irises that sit square in the eye and look out at you (they used to be half buried in the white, peeking from
#    its upper edge, which read as a sideways stare); bigger pupils and catchlights
#  - a compact face: eyes a touch higher and closer, a small smile just under them, rosier cheeks
#  - a slightly rounder gumdrop (the dome was stretched tall)
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

# --- outline: view-scaled width in Graphics mode, drawn after the jelly
rep("uniform float gT, gWob, gSpd, gLean, gSquash, gRise, gDrop, gFlat, gRoll, gJelly, gPud;",
    "uniform float gT, gWob, gSpd, gLean, gSquash, gRise, gDrop, gFlat, gRoll, gJelly, gPud, gLine;")
rep("    Object.assign(sh.uniforms, U); sh.uniforms.gJelly = JELLY; sh.uniforms.gGlow = JGLOW;",
    "    Object.assign(sh.uniforms, U); sh.uniforms.gJelly = JELLY; sh.uniforms.gGlow = JGLOW; sh.uniforms.gLine = GLINE;")
rep("    if (outline) vs = vs.replace('#include <begin_vertex>', 'vec3 transformed = goo(position) + gooN(position, normal) * 0.12; vGooY = position.y; vSph = position;');",
    "    if (outline) vs = vs.replace('#include <begin_vertex>', HI ? 'vec3 gq = goo(position); float gD = -(modelViewMatrix * vec4(gq, 1.0)).z, gS = 0.5 * (length(modelMatrix[0].xyz) + length(modelMatrix[1].xyz)); vec3 transformed = gq + gooN(position, normal) * clamp(gLine * gD / max(gS, 1e-3), 0.02, 0.12); vGooY = position.y; vSph = position;' : 'vec3 transformed = goo(position) + gooN(position, normal) * 0.12; vGooY = position.y; vSph = position;');")
rep("const JELLY = { value: 1 }, JGLOW = { value: 1 };",
    "const JELLY = { value: 1 }, JGLOW = { value: 1 }, GLINE = { value: 0.0042 }; // GLINE: the outline's width per unit of distance (Graphics mode)")
rep("dropHull.renderOrder = 31; dropHull.visible = !HI; body.add(dropHull);", "dropHull.renderOrder = HI ? 32.2 : 31; body.add(dropHull);")
rep("cHull.renderOrder = 31; cHull.visible = !HI; cBody.add(cHull);", "cHull.renderOrder = HI ? 32.2 : 31; cBody.add(cHull);")
rep("hull.renderOrder = 31; hull.visible = !HI; body.add(hull);", "hull.renderOrder = HI ? 32.2 : 31; body.add(hull);")
# the outline blinks with the body
rep("const VP = { root: drop, body, mat: dropMat, U: gooU,", "const VP = { root: drop, body, mat: dropMat, hull: dropHull, U: gooU,")
rep("VC = { root: cDrop, body: cBody, mat: cMat, U: gooU2,", "VC = { root: cDrop, body: cBody, mat: cMat, hull: cHull, U: gooU2,")
rep("V: { root: drop, body, mat, U, look, shadow, flatK: 0, gk: 1, puddle: makePuddle(color) }", "V: { root: drop, body, mat, hull, U, look, shadow, flatK: 0, gk: 1, puddle: makePuddle(color) }")
rep("  V.mat.opacity = blink ? 0.45 : 1;", "  V.mat.opacity = blink ? 0.45 : 1; if (V.hull) V.hull.material.opacity = blink ? 0.3 : 1;")

# --- eyes: the white no longer hides the iris; iris, pupil and catchlights bigger
rep("const eyeW = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, vertexColors: true }),",
    "const eyeW = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, vertexColors: true, depthWrite: false }),")
rep("const pupG = shadeGeo(new THREE.SphereGeometry(0.148, 28, 20), (x, y, z) => { const c = Math.max(0, z / 0.148), low = smoothstep(0.3, -0.85, y / 0.148),",
    "const IRIS_R = 0.158, pupG = shadeGeo(new THREE.SphereGeometry(IRIS_R, 32, 24), (x, y, z) => { const c = Math.max(0, z / IRIS_R), low = smoothstep(0.3, -0.85, y / IRIS_R),")
rep("const pupilG = new THREE.SphereGeometry(0.087, 18, 14), shineG = new THREE.SphereGeometry(0.061, 14, 10), shine2G = new THREE.SphereGeometry(0.029, 10, 8);",
    "const pupilG = new THREE.SphereGeometry(0.097, 24, 18), shineG = new THREE.SphereGeometry(0.068, 18, 12), shine2G = new THREE.SphereGeometry(0.032, 12, 8);")
rep("const sh = new THREE.Mesh(shineG, shineM); sh.renderOrder = 35; sh.position.set(0.057, 0.063, 0.128); pu.add(sh);",
    "const sh = new THREE.Mesh(shineG, shineM); sh.renderOrder = 35; sh.position.set(0.06, 0.068, 0.132); pu.add(sh);")
rep("const sh2 = new THREE.Mesh(shine2G, shineM); sh2.renderOrder = 35; sh2.position.set(-0.061, -0.054, 0.124); pu.add(sh2);",
    "const sh2 = new THREE.Mesh(shine2G, shineM); sh2.renderOrder = 35; sh2.position.set(-0.066, -0.058, 0.128); pu.add(sh2);")
# a compact face: eyes higher and a touch closer, mouth just under them
rep("const EYE_BASE = sd => new THREE.Vector3(sd * 0.34, 0.31, 0.88).normalize();", "const EYE_BASE = sd => new THREE.Vector3(sd * 0.33, 0.39, 0.86).normalize();")
rep("const FACE = { eyeX: 0.342, eyeY: 0.312, mouthTop: -0.05, cell: 0.34 };", "const FACE = { eyeX: 0.33, eyeY: 0.39, mouthTop: 0.0, cell: 0.34 };")
rep("const mouthBase = new THREE.Vector3(0, -0.05, 1).normalize();", "const mouthBase = new THREE.Vector3(0, 0.0, 1).normalize();")
# irises sit square in the eye (just in front of its middle), not out along the face's curve
rep("    it.pu.position.copy(p).multiplyScalar(1.0).add(pd);", "    it.pu.position.copy(p).multiplyScalar(0.965).add(pd);")
rep("ES === 'sleepy' ? tv1.set(lx, ly - 0.05, 0.02) : tv1.set(lx, ly - 0.02, 0.02 + (cyc ? 0.04 : 0));",
    "ES === 'sleepy' ? tv1.set(lx, ly - 0.06, 0.025) : tv1.set(lx, ly - 0.03, 0.025 + (cyc ? 0.04 : 0));")
rep("const pd = ES === 'googly' ? tv1.set(lx + Math.sin(clock * 9 + i * 2.1) * 0.035 * wig, ly - 0.07 + Math.cos(clock * 7.3 + i) * 0.02 * wig, 0.06)",
    "const pd = ES === 'googly' ? tv1.set(lx + Math.sin(clock * 9 + i * 2.1) * 0.035 * wig, ly - 0.07 + Math.cos(clock * 7.3 + i) * 0.02 * wig, 0.065)")
rep("    it.pu.position.copy(p).multiplyScalar(1.0).add(tv1.set(-lookC.lean * 0.07, -0.02, 0.02));", "    it.pu.position.copy(p).multiplyScalar(0.965).add(tv1.set(-lookC.lean * 0.07, -0.03, 0.025));")
rep("    it.pu.position.copy(p).multiplyScalar(1.0).add(tv1.set(-L.look.lean * 0.07, -0.02, 0.02));", "    it.pu.position.copy(p).multiplyScalar(0.965).add(tv1.set(-L.look.lean * 0.07, -0.03, 0.025));")
# a small smile at rest; the big laugh when happy
rep("  setFace(gooU, openO ? 2 : happy ? 1 : 0, openO ? (scared ? 1.2 : strain ? 0.7 : 0.95) : happy ? 1.1 : 1, arcs);",
    "  setFace(gooU, openO ? 2 : happy ? 1 : 3, openO ? (scared ? 1.1 : strain ? 0.65 : 0.85) : happy ? 1.0 : 1.08, arcs);")
rep("f.position.copy(mp).add(openO ? tv1.set(sd * 0.045, 0.012, 0.02) : tv1.set(sd * (happy ? 0.092 : 0.072), 0.004, 0.02));",
    "f.position.copy(mp).add(openO ? tv1.set(sd * 0.042, 0.012, 0.02) : tv1.set(sd * (happy ? 0.085 : 0.058), 0.004, 0.02));")
rep("for (const f of W.fangs) f.position.copy(mp).add(tv1.set(f.userData.sd * 0.07, 0.004, 0.02));", "for (const f of W.fangs) f.position.copy(mp).add(tv1.set(f.userData.sd * 0.058, 0.004, 0.02));")
# rosier cheeks, a little bigger
rep("float b = smoothstep(0.16, 0.02, length(e)) * uFace2.y * fk; diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0, 0.42, 0.56), b * 0.85);",
    "float b = smoothstep(0.18, 0.03, length(e)) * uFace2.y * fk; diffuseColor.rgb = mix(diffuseColor.rgb, vec3(1.0, 0.45, 0.58), b * 0.9);")
# a rounder dome
rep("if (d.y >= 0.0) RY = mix(RY, vec2(r * (1.0 - 0.035 * d.y * d.y), d.y * 1.09), gJelly);", "if (d.y >= 0.0) RY = mix(RY, vec2(r * (1.0 - 0.03 * d.y * d.y), d.y * 1.035), gJelly);")
rep("if (dy >= 0) { R += (r * (1 - 0.035 * dy * dy) - R) * J; Y += (dy * 1.09 - Y) * J; }", "if (dy >= 0) { R += (r * (1 - 0.03 * dy * dy) - R) * J; Y += (dy * 1.035 - Y) * J; }")
open(p, 'w').write(s)
print('ok')
