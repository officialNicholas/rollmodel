# Character v3, polish: the jelly lit from above (deeper low down), crisper studio highlights; lacquered accessories (a satin sheen on the
# hat, a thin-film shimmer on the bat wings); soap-film rainbows on the power-up bubbles; jelly beads around the puddle while you're posing.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

rep("    vec3 coreC = mix(deep, sat, 0.55 + 0.45 * wrapK) * (0.36 + 0.5 * wrapK);",
    "    vec3 coreC = mix(deep, sat, 0.55 + 0.45 * wrapK) * (0.36 + 0.5 * wrapK) * (0.72 + 0.4 * smoothstep(-0.7, 0.95, vGooY));")
rep("const blobMat = c => HI ? charMat(new THREE.MeshPhysicalMaterial({ color: c, transparent: true, roughness: 0.2, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.15 })) : toon(c, { transparent: true });",
    "const blobMat = c => HI ? charMat(new THREE.MeshPhysicalMaterial({ color: c, transparent: true, roughness: 0.16, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.02, envMapIntensity: 1.55 })) : toon(c, { transparent: true });")
rep("const WM = { hat: glossMat(0x2F1D52, { roughness: 0.38 }), band: glossMat(0xFF9A1F, { roughness: 0.3 }),",
    "const WM = { hat: glossMat(0x2F1D52, { roughness: 0.16, sheen: 0.7, sheenColor: new THREE.Color(0x9C7AE8), sheenRoughness: 0.32, envMapIntensity: 1.4 }), band: glossMat(0xFF9A1F, { roughness: 0.18, envMapIntensity: 1.3 }),")
rep("horn: glossMat(0xE1283E), wing: glossMat(0x2A1846, { side: THREE.DoubleSide, roughness: 0.3 }),",
    "horn: glossMat(0xE1283E, { roughness: 0.18 }), wing: glossMat(0x2A1846, { side: THREE.DoubleSide, roughness: 0.2, iridescence: 0.65, iridescenceIOR: 1.45, iridescenceThicknessRange: [220, 480] }),")
# bubbles: a thin film of soap, its colors sliding round with the view and drifting slowly
rep("fragmentShader: 'varying vec3 vN; varying vec3 vV; void main(){ float f = pow(1.0 - max(dot(vN, vV), 0.0), 2.2); float hl = smoothstep(0.92, 0.97, dot(vN, normalize(vec3(-0.45, 0.6, 0.66)))); vec3 c = mix(vec3(0.82, 0.94, 1.0), vec3(1.0), hl); gl_FragColor = vec4(c, 0.08 + 0.72 * f + hl * 0.85);",
    "uniforms: { uTime: BUB_T },\n  fragmentShader: 'uniform float uTime; varying vec3 vN; varying vec3 vV; void main(){ float d = max(dot(vN, vV), 0.0), f = pow(1.0 - d, 2.2); float hl = smoothstep(0.92, 0.97, dot(vN, normalize(vec3(-0.45, 0.6, 0.66)))); vec3 film = 0.55 + 0.45 * cos(6.2832 * (vec3(0.0, 0.33, 0.67) + d * 1.7 + vN.y * 0.4 + uTime * 0.06)); vec3 c = mix(mix(vec3(0.82, 0.94, 1.0), film, 0.75 * smoothstep(0.05, 0.75, 1.0 - d)), vec3(1.0), hl); gl_FragColor = vec4(c, 0.1 + 0.72 * f + hl * 0.85);")
rep("const bubbleMat = new THREE.ShaderMaterial({", "const BUB_T = { value: 0 }, bubbleMat = new THREE.ShaderMaterial({")
rep("  glowBatch.mat.uniforms.uTime.value = clock; SPLU.uTime.value = clock;", "  glowBatch.mat.uniforms.uTime.value = clock; SPLU.uTime.value = clock; BUB_T.value = clock;")
# jelly beads round the player's puddle while posing (menu, customize)
rep("const pWear = makeWear(body);",
"""const pWear = makeWear(body);
const beadMat = HI ? charMat(new THREE.MeshPhysicalMaterial({ color: C.ink, roughness: 0.12, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.5 })) : toon(C.ink), beads = new THREE.Group(); body.add(beads); beads.visible = false;
{ const R = rng(606), bg = new THREE.SphereGeometry(1, 16, 12); for (let i = 0; i < 9; i++) { const a = i / 9 * 6.2832 + R() * 0.5, rr = 1.62 + R() * 0.55, s = 0.05 + R() * 0.07, m = new THREE.Mesh(bg, beadMat); m.scale.set(s, s * 0.78, s); m.position.set(Math.cos(a) * rr, -0.815 + s * 0.6, Math.sin(a) * rr); m.renderOrder = 33; beads.add(m); } }""")
open(p, 'w').write(s)
print('ok')
s = open(p).read()
n = s.count("  placeWear(pWear, gooU, myLook, P, false);"); assert n == 1
s = s.replace("  placeWear(pWear, gooU, myLook, P, false);", "  placeWear(pWear, gooU, myLook, P, false); beads.visible = state === 'menu' && !vic && gooU.gPud.value > 0.6; if (beads.visible) beadMat.color.copy(dropMat.color);")
open(p, 'w').write(s); print('ok2')
