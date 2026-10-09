# Graphics mode paint: thick glossy ink with a lit rim, sky reflections, real shadows, AO and fog
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:90], c)
    s = s.replace(a, b)

rep("""const PAINT_VS = `attribute float birth; attribute float edge; attribute float team; uniform float uHardOn, uHardStart, uNow, uRewet; varying float vWet; varying float vEdge; varying float vTeam; varying vec3 vN; varying vec3 vW;
""", """const PAINT_VS = `attribute float birth; attribute float edge; attribute float team; uniform float uHardOn, uHardStart, uNow, uRewet; varying float vWet; varying float vEdge; varying float vTeam; varying vec3 vN; varying vec3 vW;
#ifdef HIQ
#include <common>
#include <shadowmap_pars_vertex>
#include <fog_pars_vertex>
#endif
""")
rep("""uRewet), 0.0); vec4 w = modelMatrix * vec4(p, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;""",
"""uRewet), 0.0); vec4 w = modelMatrix * vec4(p, 1.0); vW = w.xyz;
#ifdef HIQ
  vec4 worldPosition = w; vec3 transformedNormal = normalize(mat3(viewMatrix) * vec3(0.0, 1.0, 0.0));
  #include <shadowmap_vertex>
  #ifdef USE_FOG
  fogDepth = -(viewMatrix * w).z;
  #endif
#endif
  gl_Position = projectionMatrix * viewMatrix * w; }`;""")

rep("""const PAINT_FS = `uniform vec3 uLight; uniform vec3 uWetA[3]; uniform vec3 uDryA[3]; uniform sampler2D uCanvas; uniform float uTime; uniform float uHeat; uniform float uRewet;
varying float vWet; varying float vEdge; varying float vTeam; varying vec3 vN; varying vec3 vW;
""", """const PAINT_FS = `uniform vec3 uLight; uniform vec3 uWetA[3]; uniform vec3 uDryA[3]; uniform sampler2D uCanvas; uniform float uTime; uniform float uHeat; uniform float uRewet;
varying float vWet; varying float vEdge; varying float vTeam; varying vec3 vN; varying vec3 vW;
#ifdef HIQ
#include <common>
#include <packing>
#include <lights_pars_begin>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
#include <fog_pars_fragment>
uniform vec3 uShK, uSkyT, uSkyH, uSunC;
${HI ? AO_GLSL : ''}
#endif
""")
rep("""  float wetK = clamp(vWet, 0.0, 1.0), oldK = clamp(-vWet, 0.0, 1.0);
  float tc = floor(mod(vTeam + 0.25, 3.0)), dilA = vTeam > 2.5 ? 0.5 : 1.0;""",
"""  float wetK = clamp(vWet, 0.0, 1.0), oldK = clamp(-vWet, 0.0, 1.0);
#ifdef HIQ
  // thick ink: it swells up from its ragged rim, so the rim rounds over and catches the light like a glossy lip
  float th = smoothstep(0.0, 0.24, lim - vEdge);
  vec3 dpx = dFdx(vW), dpy = dFdy(vW), r1 = cross(dpy, n), r2 = cross(n, dpx); float det = dot(dpx, r1);
  vec3 sgr = abs(det) > 1e-10 ? (dFdx(th) * r1 + dFdy(th) * r2) / det : vec3(0.0);
  n = normalize(n - sgr * 0.075 * max(wetK, uRewet));
  float shade = getShadowMask(), ao = stageAO(vW, vec3(0.0, 1.0, 0.0));
#endif
  float tc = floor(mod(vTeam + 0.25, 3.0)), dilA = vTeam > 2.5 ? 0.5 : 1.0;""")
rep("""  vec3 wet = wetC * (0.8 + 0.22 * pool + 0.12 * dot(nb, L)) * (1.0 - 0.3 * border) + vec3(sparkle + soft + fres);
  vec3 wetFull = wet;""",
"""#ifdef HIQ
  // the sky in it: a soft reflection that grows toward the rim, and a hard highlight from the moon or sun (none in shade)
  vec3 R = reflect(-V, nb); float fr = 0.035 + 0.965 * pow(1.0 - max(dot(nb, V), 0.0), 5.0);
  vec3 env = mix(uSkyH, uSkyT, smoothstep(-0.1, 0.75, R.y));
  float hl = pow(max(dot(R, L), 0.0), 420.0);
  vec3 gloss = env * fr * 0.6 + (uSunC * (hl * 3.2 + soft * 1.4) + vec3(sparkle)) * shade;
  vec3 wet = wetC * (0.8 + 0.2 * pool) * (1.0 - 0.24 * border);
#else
  vec3 wet = wetC * (0.8 + 0.22 * pool + 0.12 * dot(nb, L)) * (1.0 - 0.3 * border) + vec3(sparkle + soft + fres);
#endif
  vec3 wetFull = wet;""")
rep("""  float drying = (1.0 - wetK) * step(0.0001, vWet) * (1.0 - step(0.0001, uRewet));
  wet *= 1.0 - 0.14 * drying * (0.5 + 0.5 * sin(uTime * 16.0));
  vec3 col = wet;""", """  float drying = (1.0 - wetK) * step(0.0001, vWet) * (1.0 - step(0.0001, uRewet));
  wet *= 1.0 - 0.14 * drying * (0.5 + 0.5 * sin(uTime * 16.0));
  vec3 col = wet; float glossK = 1.0;""")
rep("""    col = mix(dry, wet, smoothstep(0.0, 1.0, wetK));""", """    glossK = smoothstep(0.0, 1.0, wetK);
    col = mix(dry, wet, glossK);""")
rep("""    if (uRewet > 0.0) { float soak = smoothstep(0.0, 1.0, clamp(uRewet * 1.9 - 0.45 - (vnoise(vW.xz * 0.7 + 11.0) - 0.5) * 0.9, 0.0, 1.0)); col = mix(col, wetFull, soak); }
  }
  gl_FragColor = vec4(col * lit, dilA);
}`;""", """    if (uRewet > 0.0) { float soak = smoothstep(0.0, 1.0, clamp(uRewet * 1.9 - 0.45 - (vnoise(vW.xz * 0.7 + 11.0) - 0.5) * 0.9, 0.0, 1.0)); col = mix(col, wetFull, soak); glossK = max(glossK, soak); }
  }
#ifdef HIQ
  // lit like the ground it sits on: the same shadows and corners, with the shade tinted by the sky
  vec3 litK = mix(uShK, vec3(1.0), shade * clamp(dot(nb, L) / max(L.y, 0.3), 0.0, 1.3)) * mix(1.0, ao, 0.75);
  gl_FragColor = vec4(col * litK + gloss * glossK * mix(1.0, ao, 0.6), dilA);
  #ifdef USE_FOG
  float fogFactor = smoothstep(fogNear, fogFar, fogDepth);
  gl_FragColor.rgb = mix(gl_FragColor.rgb, fogColor, fogFactor);
  #endif
#else
  gl_FragColor = vec4(col * lit, dilA);
#endif
}`;""")
rep("""const paintMat = new THREE.ShaderMaterial({ uniforms: paintUniforms, vertexShader: PAINT_VS, fragmentShader: PAINT_FS, side: THREE.DoubleSide, depthWrite: false, blending: THREE.CustomBlending, blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneMinusSrcAlphaFactor, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 });""",
"""// Graphics mode: the paint takes the scene's lights (for shadows) and fog, and works out its own rim normals
if (HI) Object.assign(paintUniforms, THREE.UniformsUtils.clone(THREE.UniformsLib.lights), THREE.UniformsUtils.clone(THREE.UniformsLib.fog), { uShK: { value: new THREE.Color(0.4, 0.4, 0.5) }, uSkyT: { value: new THREE.Color() }, uSkyH: { value: new THREE.Color() }, uSunC: { value: new THREE.Color() } }, aoU);
const paintMat = new THREE.ShaderMaterial(Object.assign({ uniforms: paintUniforms, vertexShader: PAINT_VS, fragmentShader: PAINT_FS, side: THREE.DoubleSide, depthWrite: false, blending: THREE.CustomBlending, blendSrc: THREE.SrcAlphaFactor, blendDst: THREE.OneMinusSrcAlphaFactor, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 },
  HI ? { defines: { HIQ: '' }, lights: true, fog: true, extensions: { derivatives: true } } : {}));""")
rep("""const paintMesh = new THREE.Mesh(paintGeo, paintMat); paintMesh.frustumCulled = false; paintMesh.renderOrder = 10; scene.add(paintMesh);""",
"""const paintMesh = new THREE.Mesh(paintGeo, paintMat); paintMesh.frustumCulled = false; paintMesh.renderOrder = 10; paintMesh.receiveShadow = HI; scene.add(paintMesh);""")

# keep the paint's light in step with the scene's: shade ratio, sky colors, sun color
rep("""  sun.color.copy(NIGHT.key).lerp(DAY.key, dayK); sun.intensity = (NIGHT.keyI + (DAY.keyI - NIGHT.keyI) * dayK - 0.18 * rainK) * LK.key;
""", """  sun.color.copy(NIGHT.key).lerp(DAY.key, dayK); sun.intensity = (NIGHT.keyI + (DAY.keyI - NIGHT.keyI) * dayK - 0.18 * rainK) * LK.key;
  if (HI) paintLight();
""")
rep("""function applyThemeLook(T) {""", """// the paint shades itself to match the ground: how dark the shade is next to full light, what the sky looks like in it, how bright the sun is
const envUp = new THREE.Color(), tcA = new THREE.Color(), tcB = new THREE.Color();
function paintLight() {
  const U = paintUniforms, Ly = Math.max(0.3, U.uLight.value.y);
  tcA.copy(hemi.color).multiplyScalar(hemi.intensity).add(envUp); tcB.copy(sun.color).multiplyScalar(sun.intensity * Ly).add(tcA);
  U.uShK.value.setRGB(tcA.r / Math.max(tcB.r, 1e-3), tcA.g / Math.max(tcB.g, 1e-3), tcA.b / Math.max(tcB.b, 1e-3));
  U.uSunC.value.copy(sun.color).multiplyScalar(sun.intensity); U.uSkyT.value.copy(hemi.color).multiplyScalar(0.85); U.uSkyH.value.copy(scene.fog.color);
}
function applyThemeLook(T) {""")
rep("""    envU.top.value.set(e.top); envU.hor.value.set(e.hor); envU.gnd.value.set(e.gnd); envU.sunCol.value.set(e.sun); envU.sunK.value = e.sunK;
    T.envRT = pmrem.fromScene(envScene, 0.02);
  }
  scene.environment = T.envRT.texture;""", """    envU.top.value.set(e.top); envU.hor.value.set(e.hor); envU.gnd.value.set(e.gnd); envU.sunCol.value.set(e.sun); envU.sunK.value = e.sunK;
    T.envRT = pmrem.fromScene(envScene, 0.02); T.envUp = new THREE.Color(e.top).lerp(new THREE.Color(e.hor), 0.4);
  }
  scene.environment = T.envRT.texture; envUp.copy(T.envUp);""")
open(p,'w').write(s); print('patched')
