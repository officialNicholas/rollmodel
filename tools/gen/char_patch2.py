# puddles under every blob, the studio light map for glossy character parts, and jelly glow per theme
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:100], c)
    s = s.replace(a, b)

rep("""const VP = { root: drop, body, mat: dropMat, U: gooU, look, shadow: shadowBlob, flatK: 0, gk: 1 }, VC = { root: cDrop, body: cBody, mat: cMat, U: gooU2, look: lookC, shadow: cShadow, flatK: 0, gk: 1 };""",
"""// ---------- the puddle each blob sits in: its own jelly melting out over the floor, wobbling at the edge ----------
const puddleG = (() => { const V2 = (x, y) => new THREE.Vector2(x, y), h = 0.11; return new THREE.LatheGeometry([V2(1.0, 0), V2(0.985, 0.32 * h), V2(0.95, 0.6 * h), V2(0.88, 0.82 * h), V2(0.76, 0.95 * h), V2(0.55, h), V2(0, h)], SEG(40)); })();
const PUDDLE_VS = `vec3 transformed = position; float pa = atan(position.z, position.x), pr = length(position.xz);
  float wv = 1.0 + 0.1 * sin(pa * 3.0 + pT * 1.1) + 0.055 * sin(pa * 5.0 - pT * 1.7 + 1.3) + 0.03 * sin(pa * 9.0 + pT * 2.3);
  transformed.xz *= mix(1.0, wv, smoothstep(0.3, 1.0, pr));`;
function makePuddle(color) {
  const U = { pT: { value: Math.random() * 10 } };
  const mat = HI ? charMat(new THREE.MeshPhysicalMaterial({ color, transparent: true, roughness: 0.18, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.04, envMapIntensity: 1.25 })) : toon(color, { transparent: true });
  mat.onBeforeCompile = sh => {
    sh.uniforms.pT = U.pT; sh.uniforms.gGlow = JGLOW;
    sh.vertexShader = 'uniform float pT;\\n' + sh.vertexShader.replace('#include <begin_vertex>', PUDDLE_VS);
    if (HI) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\\nuniform float gGlow;').replace('#include <aomap_fragment>', '#include <aomap_fragment>\\n{ vec3 jv = normalize(vViewPosition); float edge = 1.0 - saturate(dot(normal, jv)); totalEmissiveRadiance += diffuseColor.rgb * (1.12 + 0.55 * diffuseColor.rgb) * (0.3 + 0.3 * edge) * gGlow; }');
  };
  mat.customProgramCacheKey = () => 'puddle';
  const m = new THREE.Mesh(puddleG, mat); m.renderOrder = 12; m.receiveShadow = HI; m.visible = false; m.userData = { U, k: 0 }; scene.add(m); return m;
}
const VP = { root: drop, body, mat: dropMat, U: gooU, look, shadow: shadowBlob, flatK: 0, gk: 1, puddle: makePuddle(C.ink) }, VC = { root: cDrop, body: cBody, mat: cMat, U: gooU2, look: lookC, shadow: cShadow, flatK: 0, gk: 1, puddle: makePuddle(TEAMS[1].wet) };""")
rep("""  return { D, drop, body, mat, xrayMat, U, eyes, mouth, glint, glint2, shadow, look, blinkT: 1.7, blinkK: 0, V: { root: drop, body, mat, U, look, shadow, flatK: 0, gk: 1 },""",
    """  return { D, drop, body, mat, xrayMat, U, eyes, mouth, glint, glint2, shadow, look, blinkT: 1.7, blinkK: 0, V: { root: drop, body, mat, U, look, shadow, flatK: 0, gk: 1, puddle: makePuddle(color) },""")
rep("""  const gy = surfaceUnder(D.x, D.z, D.y + 0.3, true);
  if (gy > -Infinity && !hidden && D.st !== 'ko' && state !== 'menu') { V.shadow.visible = true;""",
"""  const gy = surfaceUnder(D.x, D.z, D.y + 0.3, true);
  // the puddle: full while it sits on the ground, drawn in as it leaves it, trailing back a little at speed
  const pd = V.puddle;
  if (pd) {
    const on = V.root.visible && !hidden && D.st !== 'ko' && gy > -Infinity, want = on ? clamp(1 - (D.y - gy) * 1.6, 0, 1) * L.flat : 0;
    pd.userData.k += (want - pd.userData.k) * Math.min(1, dt * (want > pd.userData.k ? 8 : 14));
    const pk = pd.userData.k * isc; pd.visible = pk > 0.04;
    if (pd.visible) {
      const sc = rad * 1.45 * (0.5 + 0.5 * pk) * (1 + 0.4 * fk), back = rad * 0.35 * L.spd;
      pd.position.set(D.x - Math.sin(D.yaw) * back, gy + 0.03, D.z - Math.cos(D.yaw) * back); pd.rotation.y = D.yaw;
      pd.scale.set(sc, rad * (0.45 + 0.55 * pk), sc * (1 + 0.45 * L.spd));
      pd.material.color.copy(V.mat.color); pd.material.opacity = V.mat.opacity; pd.userData.U.pT.value = clock + (D.cpu ? 2.3 * (D.team || 1) : 0);
    }
  }
  if (gy > -Infinity && !hidden && D.st !== 'ko' && state !== 'menu') { V.shadow.visible = true;""")

# the studio light map: soft boxes over the theme's sky, used for the highlights on everything glossy a character has
rep("""function themeEnv(T) {
  if (!HI) return;""", """const softbox = new THREE.Group(); softbox.visible = false; envScene.add(softbox);
{ const box = (w, h, x, y, z, k, round) => { const m = new THREE.Mesh(round ? new THREE.CircleGeometry(w, 32) : new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(k, k * 0.99, k * 0.97), side: THREE.DoubleSide })); m.position.set(x, y, z); m.lookAt(0, 0, 0); softbox.add(m); };
  box(5.2, 3.4, -4.5, 6.2, 4.2, 3.2); box(1.3, 6.5, 6.4, 3.6, -1.8, 1.8); box(1.6, 0, 0.6, 8.7, -2.4, 2.4, true); box(6.5, 1.1, 1.5, 2.0, -8.3, 1.5); box(3.2, 1.4, 2.5, 4.6, 7.6, 1.6); }
function themeEnv(T) {
  if (!HI) return;""")
rep("""    T.envRT = pmrem.fromScene(envScene, 0.02); T.envUp = new THREE.Color(e.top).lerp(new THREE.Color(e.hor), 0.4);
  }
  scene.environment = T.envRT.texture; envUp.copy(T.envUp);""", """    T.envRT = pmrem.fromScene(envScene, 0.02); T.envUp = new THREE.Color(e.top).lerp(new THREE.Color(e.hor), 0.4);
    softbox.visible = true; T.charRT = pmrem.fromScene(envScene, 0.02); softbox.visible = false;
  }
  scene.environment = T.envRT.texture; envUp.copy(T.envUp);
  for (const m of CHAR_MATS) if (m.envMap !== T.charRT.texture) { m.envMap = T.charRT.texture; m.needsUpdate = true; }""")
rep("""  themeEnv(T); if (post) post.grade(T);""", """  JGLOW.value = T.jglow != null ? T.jglow : 1; themeEnv(T); if (post) post.grade(T);""")
open(p,'w').write(s); print('char patch 2 ok')
