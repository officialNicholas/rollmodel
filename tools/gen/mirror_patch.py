# Reflections: in Graphics mode on newer phones, the stage is drawn a second time from a camera mirrored under the floor (at half size,
# cut off just above the floor so only what stands on it shows), and polished floors look it up instead of the sky's blurred light: blocks,
# pillars, flames and players stand on their reflections in the marble. Rougher spots (grout, cracks) fall back to the sky as before.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

rep("uMacro: { value: 0.12 } };", "uMacro: { value: 0.12 }, uMirror: { value: null }, uMirM: { value: new THREE.Matrix4() }, uMirK: { value: 0 } };")
rep("sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uLitMap = aoU.uLitMap; sh.uniforms.uAORect = aoU.uAORect; sh.uniforms.uMacro = aoU.uMacro;\n  sh.vertexShader",
    "sh.uniforms.uAOMap = aoU.uAOMap; sh.uniforms.uLitMap = aoU.uLitMap; sh.uniforms.uAORect = aoU.uAORect; sh.uniforms.uMacro = aoU.uMacro;\n"
    "  if (sh.defines && sh.defines.MIRROR) { sh.uniforms.uMirror = aoU.uMirror; sh.uniforms.uMirM = aoU.uMirM; sh.uniforms.uMirK = aoU.uMirK;\n"
    "    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\nuniform sampler2D uMirror; uniform mat4 uMirM; uniform float uMirK;').replace('#include <lights_fragment_maps>', '#include <lights_fragment_maps>\\n' + MIRROR_GLSL); }\n"
    "  sh.vertexShader")
rep("function aoHook(sh) {", """// the mirrored stage under a polished floor: where this spot's reflection lands in the mirror camera's picture, nudged by the surface's
// relief, blurrier the rougher it is; it takes over from the sky's light on smooth spots, fading out toward the picture's edges
const MIRROR_GLSL = `if (uMirK > 0.0) { vec3 wn = (vec4(normal, 0.0) * viewMatrix).xyz; vec4 mc = uMirM * vec4(vAOw, 1.0); vec2 muv = mc.xy / mc.w + wn.xz * 0.05;
  float k = uMirK * (1.0 - smoothstep(0.16, 0.5, material.roughness)) * step(vAOw.y, 0.06) * smoothstep(0.0, 0.04, muv.x) * smoothstep(1.0, 0.96, muv.x) * smoothstep(0.0, 0.04, muv.y) * smoothstep(1.0, 0.96, muv.y);
  if (k > 0.001) { vec3 mir = textureLod(uMirror, muv, clamp(material.roughness * 10.0 - 0.6, 0.0, 6.0)).rgb; radiance = mix(radiance, mir, k); } }`;
function aoHook(sh) {""")
# the floor material asks for it on themes with polished floors
rep("  if (HI) {\n    const tr = T.trim || { c: 0x2C2F3B, m: 0.5, r: 0.4 };",
    "  if (HI && T.mirror) { T.mats.floor.defines = Object.assign(T.mats.floor.defines || {}, { MIRROR: 1 }); T.mats.floor.needsUpdate = true; }\n  if (HI) {\n    const tr = T.trim || { c: 0x2C2F3B, m: 0.5, r: 0.4 };")
# the mirror pass in the Graphics mode frame
rep("  const sz = new THREE.Vector2();\n  const P0 = {",
"""  const sz = new THREE.Vector2();
  const mirRT = new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType, minFilter: THREE.LinearMipmapLinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: true, depthBuffer: true });
  const mirCam = new THREE.PerspectiveCamera(), mv = new THREE.Vector3(), mt = new THREE.Vector3(), mq = new THREE.Vector4(), mp = new THREE.Plane(), mrot = new THREE.Matrix4(), blackT = new THREE.DataTexture(new Uint8Array(4), 1, 1); blackT.needsUpdate = true;
  aoU.uMirror.value = blackT;
  const MIR_Y = 0.05;
  function mirrorPass() {
    camera.updateMatrixWorld(); const cp = mv.setFromMatrixPosition(camera.matrixWorld);
    mrot.extractRotation(camera.matrixWorld); mt.set(0, 0, -1).applyMatrix4(mrot).add(cp);
    mirCam.position.set(cp.x, -cp.y, cp.z); mirCam.up.set(0, 1, 0).applyMatrix4(mrot); mirCam.up.y = -mirCam.up.y; mirCam.lookAt(mt.x, -mt.y, mt.z);
    mirCam.far = camera.far; mirCam.near = camera.near; mirCam.updateMatrixWorld(); mirCam.projectionMatrix.copy(camera.projectionMatrix); mirCam.projectionMatrixInverse.copy(camera.projectionMatrixInverse);
    aoU.uMirM.value.set(0.5, 0, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0, 0.5, 0.5, 0, 0, 0, 1).multiply(mirCam.projectionMatrix).multiply(mirCam.matrixWorldInverse);
    // oblique near plane on the floor (Lengyel): nothing under it ends up in the reflection
    mp.setFromNormalAndCoplanarPoint(tv1.set(0, 1, 0), tv2.set(0, MIR_Y, 0)).applyMatrix4(mirCam.matrixWorldInverse);
    const pm = mirCam.projectionMatrix.elements, cpl = mq.set(mp.normal.x, mp.normal.y, mp.normal.z, mp.constant), q = tv3.set((Math.sign(cpl.x) + pm[8]) / pm[0], (Math.sign(cpl.y) + pm[9]) / pm[5], -1);
    const qw = (1 + pm[10]) / pm[14], sc = 2 / (cpl.x * q.x + cpl.y * q.y + cpl.z * q.z + cpl.w * qw); cpl.multiplyScalar(sc);
    pm[2] = cpl.x; pm[6] = cpl.y; pm[10] = cpl.z + 1; pm[14] = cpl.w;
    const sha = renderer.shadowMap.autoUpdate; renderer.shadowMap.autoUpdate = false;
    renderer.setRenderTarget(mirRT); renderer.clear(); renderer.render(scene, mirCam); renderer.shadowMap.autoUpdate = sha;
  }
  const P0 = {""")
rep("main.setSize(w, h); A.setSize(w >> 1, h >> 1);", "main.setSize(w, h); mirRT.setSize(Math.max(4, w >> 1), Math.max(4, h >> 1)); A.setSize(w >> 1, h >> 1);")
rep("    render() {\n      renderer.setRenderTarget(main); renderer.render(scene, camera);",
    "    mirror: DEV_TIER >= 3,\n    render() {\n      const mOn = P0.mirror && TH.mirror && !vic; aoU.uMirK.value = mOn ? 1 : 0; aoU.uMirror.value = mOn ? mirRT.texture : blackT; if (mOn) mirrorPass();\n      renderer.setRenderTarget(main); renderer.render(scene, camera); aoU.uMirK.value = 0; aoU.uMirror.value = blackT;")
open(p, 'w').write(s)
print('ok')
