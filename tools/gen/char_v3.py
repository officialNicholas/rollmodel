# Character v3: a round gumdrop with no waist (the body only ever widens down into its puddle), a taller dome, alive (it breathes and
# its upper body slowly shifts shape), and in Graphics mode real see-through jelly: the frame behind each blob is grabbed just before the
# blobs draw, and the body shows it bent through the jelly, tinted deeper the thicker the jelly is, around a soft glowing core, under the
# clear glossy outer layer.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

# ---- shape: knots of the lower profile, monotonic all the way into the puddle ----
rep("""  if (i == 1) return vec2(1.04, -0.15);
  if (i == 2) return vec2(1.055, -0.3);
  if (i == 3) return vec2(1.035, -0.44);
  if (i == 4) return vec2(0.975, -0.565);
  if (i == 5) return vec2(0.905, -0.665);
  if (i == 6) return vec2(0.9, -0.745);
  if (i == 7) return vec2(1.12, -0.785);
  if (i == 8) return vec2(1.42, -0.79);
  if (i == 9) return vec2(1.62, -0.812);""", """  if (i == 1) return vec2(1.035, -0.15);
  if (i == 2) return vec2(1.065, -0.3);
  if (i == 3) return vec2(1.09, -0.44);
  if (i == 4) return vec2(1.115, -0.56);
  if (i == 5) return vec2(1.15, -0.66);
  if (i == 6) return vec2(1.22, -0.735);
  if (i == 7) return vec2(1.36, -0.78);
  if (i == 8) return vec2(1.52, -0.8);
  if (i == 9) return vec2(1.64, -0.815);""")
rep("const SIT_K = [[0.988, 0.148], [1.0, 0], [1.04, -0.15], [1.055, -0.3], [1.035, -0.44], [0.975, -0.565], [0.905, -0.665], [0.9, -0.745], [1.12, -0.785], [1.42, -0.79], [1.62, -0.812], [0, -0.82], [-0.2, -0.82]];",
    "const SIT_K = [[0.988, 0.148], [1.0, 0], [1.035, -0.15], [1.065, -0.3], [1.09, -0.44], [1.115, -0.56], [1.15, -0.66], [1.22, -0.735], [1.36, -0.78], [1.52, -0.8], [1.64, -0.815], [0, -0.82], [-0.2, -0.82]];")
# a taller, gently gathered dome on top
rep("""  vec2 RY = vec2(r, d.y);
  if (d.y < 0.0) {""", """  vec2 RY = vec2(r, d.y);
  if (d.y >= 0.0) RY = mix(RY, vec2(r * (1.0 - 0.05 * d.y * d.y), d.y * 1.18), gJelly);
  else {""")
rep("""    let R = r, Y = dy;
    if (dy < 0) {""", """    let R = r, Y = dy;
    if (dy >= 0) { R += (r * (1 - 0.05 * dy * dy) - R) * J; Y += (dy * 1.18 - Y) * J; }
    else {""")
# alive: it breathes (taller and narrower, then back), and its upper body slowly bulges and leans, never quite the same shape
rep("""vec3 goo(vec3 p){
  p = jellyShape(p);
  float G = 0.82 * gFlat; // on the floor, the wobble and squash pivot on it, so the puddle stays put""",
"""vec3 goo(vec3 p){
  p = jellyShape(p);
  float G = 0.82 * gFlat; // on the floor, the wobble and squash pivot on it, so the puddle stays put
  { float br = 0.026 * sin(gT * 2.2) + 0.012 * sin(gT * 3.9 + 1.3), hg = smoothstep(-0.82, 1.2, p.y), an = atan(p.z, p.x);
    p.y = (p.y + G) * (1.0 + br * gJelly) - G; p.xz *= 1.0 - br * 0.55 * hg * gJelly;
    p.xz *= 1.0 + hg * gJelly * (0.03 * sin(an * 2.0 + gT * 0.9) + 0.02 * sin(an * 3.0 - gT * 1.3 + 2.0));
    p.x += hg * hg * gJelly * 0.035 * sin(gT * 0.75); p.z += hg * hg * gJelly * 0.025 * sin(gT * 0.6 + 1.0); }""")
rep("""  const G = 0.82 * g('gFlat');
  const ax = Math.abs(p.x);""", """  const G = 0.82 * g('gFlat');
  { const t = g('gT'), br = 0.026 * Math.sin(t * 2.2) + 0.012 * Math.sin(t * 3.9 + 1.3), hg = smoothstep(-0.82, 1.2, p.y), an = Math.atan2(p.z, p.x);
    p.y = (p.y + G) * (1 + br * J) - G; const k1 = (1 - br * 0.55 * hg * J) * (1 + hg * J * (0.03 * Math.sin(an * 2 + t * 0.9) + 0.02 * Math.sin(an * 3 - t * 1.3 + 2))); p.x *= k1; p.z *= k1;
    p.x += hg * hg * J * 0.035 * Math.sin(t * 0.75); p.z += hg * hg * J * 0.025 * Math.sin(t * 0.6 + 1); }
  const ax = Math.abs(p.x);""")

# ---- see-through jelly (Graphics mode) ----
rep("const RIG = { uRigK: { value: 1 },", "const RIG = { uGrab: { value: null }, uGrabK: { value: 0 }, uGrabPx: { value: new THREE.Vector2(1, 1) }, uRigK: { value: 1 },")
rep("""  vec3 rig = sat * uRigKeyC * wrapK * 0.42 + deep * (1.0 - wrapK) * 0.1 + uRigKeyC * spec * (0.6 + 0.4 * noInk) + mix(glow, vec3(1.0), 0.25) * uRigRimC * rim * 0.8;
  vec3 sss = glow * (0.05 * edge * edge + 0.2 * low * (0.3 + 0.7 * wrapK) + 0.1 * pud);
  totalEmissiveRadiance += rig * uRigK * mix(0.2, 1.0, noInk) + sss * gGlow * noInk;
  reflectedLight.directDiffuse *= 0.5; reflectedLight.indirectSpecular *= 1.0 - 0.45 * pud;
  reflectedLight.indirectDiffuse *= mix(vec3(1.0), deep / max(base, vec3(0.03)), 0.45) * 0.7;
}`;""", """  vec3 rigD = sat * uRigKeyC * wrapK * 0.42 + deep * (1.0 - wrapK) * 0.1, rigS = uRigKeyC * spec * (0.6 + 0.4 * noInk) + mix(glow, vec3(1.0), 0.25) * uRigRimC * rim * 0.8;
  vec3 sss = glow * (0.05 * edge * edge + 0.2 * low * (0.3 + 0.7 * wrapK) + 0.1 * pud);
  reflectedLight.directDiffuse *= 0.5; reflectedLight.indirectSpecular *= 1.0 - 0.45 * pud;
  reflectedLight.indirectDiffuse *= mix(vec3(1.0), deep / max(base, vec3(0.03)), 0.45) * 0.7;
  float tk = uGrabK * noInk;
  if (tk > 0.0) {
    // what's behind, bent through the jelly (a touch more for red than blue, like glass), tinted by it the more of it the light crosses,
    // around a soft glowing core; the opaque shading gives way to it, the outer layer's reflections stay on top
    float th = pow(ndv, 0.6) * (1.0 - 0.8 * pud);
    vec2 suv = gl_FragCoord.xy * uGrabPx, off = -N.xy * (0.018 + 0.05 * th) * vec2(uGrabPx.x / uGrabPx.y, 1.0) * 0.6;
    vec3 bg = vec3(texture2D(uGrab, suv + off * 1.08).r, texture2D(uGrab, suv + off).g, texture2D(uGrab, suv + off * 0.92).b);
    vec3 tint = clamp(sat * 1.15, 0.02, 1.0), seen = bg * pow(tint, vec3(0.35 + 2.2 * th)) * (1.0 + 0.5 * th);
    float core = smoothstep(0.25, 0.95, ndv) * (1.0 - pud) * smoothstep(-0.8, -0.3, vGooY);
    vec3 coreC = mix(sat, glow, 0.4) * (0.42 + 0.5 * wrapK) + glow * 0.12;
    vec3 trans = mix(seen, coreC, core * 0.62) + glow * (0.07 * edge + 0.12 * low * wrapK + 0.1 * pud);
    reflectedLight.directDiffuse *= 1.0 - tk; reflectedLight.indirectDiffuse *= 1.0 - tk;
    totalEmissiveRadiance += trans * tk * gGlow + rigD * uRigK * 0.35 * tk + rigS * uRigK;
    totalEmissiveRadiance += (rigD * uRigK * mix(0.2, 1.0, noInk) + sss * gGlow * noInk) * (1.0 - tk);
  } else totalEmissiveRadiance += (rigD + rigS) * uRigK * mix(0.2, 1.0, noInk) + sss * gGlow * noInk;
}`;""")
rep("uniform float gGlow, uRigK; uniform vec3 uRigKey, uRigKeyC, uRigRim, uRigRimC;\\n' + AO_GLSL)",
    "uniform float gGlow, uRigK, uGrabK; uniform vec3 uRigKey, uRigKeyC, uRigRim, uRigRimC; uniform sampler2D uGrab; uniform vec2 uGrabPx;\\n' + AO_GLSL)")

# ---- the grab: once a frame in Graphics mode, just before the first blob body draws, copy the frame so far ----
rep("  const mirRT = new THREE.WebGLRenderTarget(4, 4, {",
"""  const grabRT = new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType, minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, depthBuffer: false, generateMipmaps: false });
  const grab = { on: false, done: false };
  function doGrab() {
    grab.done = true; const gl = renderer.getContext(), st = renderer.state, mp = renderer.properties.get(main), gp = renderer.properties.get(grabRT);
    const src = mp.__webglMultisampledFramebuffer || mp.__webglFramebuffer, dst = gp.__webglFramebuffer; if (!src || !dst) return;
    st.bindFramebuffer(gl.READ_FRAMEBUFFER, src); st.bindFramebuffer(gl.DRAW_FRAMEBUFFER, dst);
    gl.blitFramebuffer(0, 0, main.width, main.height, 0, 0, grabRT.width, grabRT.height, gl.COLOR_BUFFER_BIT, gl.NEAREST);
    st.bindFramebuffer(gl.READ_FRAMEBUFFER, null); st.bindFramebuffer(gl.DRAW_FRAMEBUFFER, src);
    RIG.uGrabK.value = 1; RIG.uGrab.value = grabRT.texture;
  }
  // each blob body calls this as it's about to draw
  JELLY_GRAB.fn = () => { if (grab.on && !grab.done) doGrab(); };
  const mirRT = new THREE.WebGLRenderTarget(4, 4, {""")
rep("main.setSize(w, h); mirRT.setSize(", "main.setSize(w, h); grabRT.setSize(w, h); renderer.initRenderTarget(grabRT); RIG.uGrabPx.value.set(1 / w, 1 / h); mirRT.setSize(")
rep("      renderer.setRenderTarget(main); renderer.render(scene, camera); aoU.uMirK.value = 0; aoU.uMirror.value = blackT;",
    "      grab.on = !vic; grab.done = false; RIG.uGrabK.value = 0;\n      renderer.setRenderTarget(main); renderer.render(scene, camera); aoU.uMirK.value = 0; aoU.uMirror.value = blackT; grab.on = false; RIG.uGrabK.value = 0;")
rep("const CHAR_MATS = [];", "const CHAR_MATS = [], JELLY_GRAB = { fn: null }, jellyGrab = () => { if (JELLY_GRAB.fn) JELLY_GRAB.fn(); };")
# the bodies trigger it
rep("const dropMat = gooify(blobMat(C.ink)); const dropMesh = new THREE.Mesh(blobG, dropMat); dropMesh.castShadow = true; dropMesh.renderOrder = 32; body.add(dropMesh);",
    "const dropMat = gooify(blobMat(C.ink)); const dropMesh = new THREE.Mesh(blobG, dropMat); dropMesh.castShadow = true; dropMesh.renderOrder = 32; dropMesh.onBeforeRender = jellyGrab; body.add(dropMesh);")
rep("const cMat = gooify(blobMat(TEAMS[1].wet), false, undefined, gooU2); const cMesh = new THREE.Mesh(blobG, cMat); cMesh.castShadow = true; cMesh.renderOrder = 32; cBody.add(cMesh);",
    "const cMat = gooify(blobMat(TEAMS[1].wet), false, undefined, gooU2); const cMesh = new THREE.Mesh(blobG, cMat); cMesh.castShadow = true; cMesh.renderOrder = 32; cMesh.onBeforeRender = jellyGrab; cBody.add(cMesh);")
rep("  const mat = gooify(blobMat(color), false, undefined, U); const mesh = new THREE.Mesh(blobG, mat); mesh.castShadow = true; mesh.renderOrder = 32; body.add(mesh);",
    "  const mat = gooify(blobMat(color), false, undefined, U); const mesh = new THREE.Mesh(blobG, mat); mesh.castShadow = true; mesh.renderOrder = 32; mesh.onBeforeRender = jellyGrab; body.add(mesh);")
open(p, 'w').write(s)
print('ok')
