import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ---------- coffin ring: a 4-segment circular meter of how many bars of blood are left in it ----------
rep("ringG = new THREE.RingGeometry(0.98, 1.2, 40);", """ringG = new THREE.RingGeometry(0.95, 1.27, 72);
// the fill starts at the top of the screen and runs clockwise, one segment per bar of a full tank
const ringFwd = { value: new THREE.Vector2(0, -1) };
function potRingMat() {
  const u = { uColor: { value: new THREE.Color(C.ink) }, uOp: { value: 0.6 }, uFill: { value: 1 }, uFwd: ringFwd };
  const m = new THREE.ShaderMaterial({ uniforms: u, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -6, polygonOffsetUnits: -6,
    vertexShader: 'varying vec2 vP; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vec4 c = modelMatrix * vec4(0.0, 0.0, 0.0, 1.0); vP = w.xz - c.xz; gl_Position = projectionMatrix * viewMatrix * w; }',
    fragmentShader: `uniform vec3 uColor; uniform float uOp, uFill; uniform vec2 uFwd; varying vec2 vP;
void main(){
  vec2 d = normalize(vP);
  float f = fract(atan(d.y * uFwd.x - d.x * uFwd.y, dot(d, uFwd)) / 6.2831853 + 1.0);
  float w = fract(f * 4.0); if (w < 0.05 || w > 0.95) discard;
  float on = step(f, uFill);
  gl_FragColor = vec4(mix(uColor * 0.45, uColor, on), uOp * mix(0.32, 1.0, on));
}` });
  m.color = u.uColor.value; Object.defineProperty(m, 'opacity', { get: () => u.uOp.value, set: v => { u.uOp.value = v; } });
  return m;
}""")
rep("  const ring = new THREE.Mesh(ringG, new THREE.MeshBasicMaterial({ color: C.ink, transparent: true, opacity: 0.45, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -6, polygonOffsetUnits: -6 }));",
    "  const ring = new THREE.Mesh(ringG, potRingMat());")
rep("p.ring.visible = p.ink > 0.02 && potUp(p); p.ring.material.opacity = (low ? 0.55 : 0.32) + Math.sin(clock * (low ? 7 : 3) + p.phase) * 0.12;",
    "p.ring.visible = p.ink > 0.02 && potUp(p); p.ring.material.uniforms.uFill.value = Math.min(1, p.ink); p.ring.material.opacity = (low ? 0.9 : 0.72) + Math.sin(clock * (low ? 7 : 3) + p.phase) * 0.1;")
rep("    const draining = !!p.occ && p.ink > 0.02,", "    if (p === pots[0]) { camera.getWorldDirection(tv2); if (Math.abs(tv2.x) + Math.abs(tv2.z) > 1e-4) ringFwd.value.set(tv2.x, tv2.z).normalize(); }\n    const draining = !!p.occ && p.ink > 0.02,")

# ---------- the main menu shows the canvas, not the blobs ----------
rep("  resetRun(); decorate(); renderStages(); AU.music('menu'); menuPose(); heroT = 0;",
    "  resetRun(); decorate(); renderStages(); AU.music('menu'); menuPose(); heroT = 0;\n  drop.visible = shadowBlob.visible = false; LH.drop.visible = LH.shadow.visible = false; L2.drop.visible = L2.shadow.visible = false;")
rep("  if (gy > -Infinity && !hidden && D.st !== 'ko') { V.shadow.visible = true;", "  if (gy > -Infinity && !hidden && D.st !== 'ko' && state !== 'menu') { V.shadow.visible = true;")
open(F, 'w').write(s)
print('ok')
