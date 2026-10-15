// ---------- (v311) the Conquest boss: the owner's jellyfish with boxing gloves, rigged, with physics, a face and a full set of moves ----------
//
// The model is the owner's (one welded mesh, 17,100 triangles), rigged offline by tools/boss/build_pack.py into boss-pack.txt (fetched
// the first time a boss is made, about 0.95 MB of text): 73 bones (a root and the bell; per arm six bones, the hand, its cuff and three
// bones for each finger and the thumb; seven tentacle chains), four weights a vertex, and a mesh half as fine for the outline and the
// shadow. Nothing here makes objects per frame. The whole boss is about 29,900 triangles in 5 draws (and the outline's shadow).
//
//   const boss = makeBoss({ scale: 1, hover: 5.6, floorY: 0, poolY: -0.14, poolR: 4, glove: 1.3, glow: 1 });
//   boss.ready.then(() => ...)                          // (or boss.isReady); a Group (boss.group) to add to the scene
//   boss.group.position.set(x, floorY, z)               // its home: the floor under the middle of the bell (the pool's middle)
//   boss.update(dt, { player, camera })                 // each frame; player: a Vector3 (world), looked at and turned to unless lookAt says;
//                                                       // camera: the sparks face it (else the camera that last drew the boss)
//   boss.play(name, opts) -> the move's length (s)      // see MOVES below; plays over idle, returns to idle when done
//   boss.busy, boss.move                                // true while a move other than idle runs, and which
//   boss.lookAt(x, y, z) / boss.lookAt(null)            // where the eyes (and slowly the body) turn; null: back to the player
//   boss.face(expr, hold)                               // angry (default), glare, charging, glow, hurt, dizzy, smug, defeated, surprised
//   boss.hand(side, pose)                               // 'L' | 'R' | 'both', 'fist' | 'open' | 'relax' | 'point' | 'spread' | null (the move's)
//   boss.onHit(cb)                                      // cb({ move, hand, x, y, z, r, ring, power }) when a fist (or the zap) lands
//   boss.on(event, cb) / boss.off(event, cb)            // every event below
//   boss.fist(side, out) / boss.fistR                   // a fist's centre (world) and radius, for the fight's collisions
//   boss.bellPoint(out) / boss.bellR                    // the bell's centre (world) and radius (where the player hits it)
//   boss.stats                                          // { tris, draws, cpuMs } (cpuMs: the last update's cost)
//   boss.dispose()
//
// Moves (opts.speed scales the timing: 1 normal, 1.4 a harder fight; x, z are the target on the floor, in world units):
//   idle                 the hover: a slow bob, the bell pulsing, tentacles flowing, arms drifting, fists flexing, sparks, blinks
//   intro    {}          rises out of the pool (from under opts.poolY), shakes off the slime, bumps its fists with a spark burst
//   punch    {hand, x, z, speed}  hand 'L' | 'R' | 'auto' (the side nearer the target): wind-up, strike, impact, recovery
//   slam     {x, z, speed}        both fists up high, then down onto the target with a big shockwave
//   sweep    {hand, dir, x, z, speed}  one arm sweeps low across the floor in an arc through the target (dir 1 / -1, default inward)
//   zap      {x, z, speed}        charges between its fists, then a lightning bolt to the target
//   hurt     {x, z}               a flinch away from where the hit came from, a flash and a wobble
//   stunned  {time}               sinks low, dizzy, fists resting on the floor (the opening), then recovers
//   taunt    {}                   wags a finger, beckons with the other glove, smug
//   defeat   {}                   deflates and sinks into the pool in a cloud of bubbles (and stays down until the intro)
//
// Events (cb gets { move, ... }): start, windup, strike, hit (also to onHit), recover, done (any move ends), sweep (each frame of a
// sweep's low pass: { x, z } the fist on the floor), zap (the bolt fires), stunStart, stunEnd, introRise, introShake, introBump,
// introDone, defeated.
var BOSS = (() => {
  const V3 = THREE.Vector3, Q4 = THREE.Quaternion, M4 = THREE.Matrix4;
  const HIQ = typeof HI !== 'undefined' ? HI : true;
  const INK_C = typeof C !== 'undefined' && C.outline !== undefined ? C.outline : 0x1A1030;
  const INK_W = typeof GLINE !== 'undefined' ? GLINE : { value: 0.0042 };
  const clamp01 = x => x < 0 ? 0 : x > 1 ? 1 : x, lerp = (a, b, t) => a + (b - a) * t, sstep = (a, b, x) => { const t = clamp01((x - a) / (b - a)); return t * t * (3 - 2 * t); };
  const eIn = t => t * t, eOut = t => 1 - (1 - t) * (1 - t), eIO = t => t < 0.5 ? 2 * t * t : 1 - 2 * (1 - t) * (1 - t), eBack = (t, k = 1.7) => 1 + (k + 1) * Math.pow(t - 1, 3) + k * Math.pow(t - 1, 2);
  const S = { pack: null, loading: null, url: 'boss-pack.txt' };

  // ---------------------------------------------------------------- the pack: 'RMB1', the header's length, the header (JSON), the data
  const fromB64 = t => { t = t.replace(/[^A-Za-z0-9+/=]/g, ''); if (typeof Uint8Array.fromBase64 === 'function') return Uint8Array.fromBase64(t).buffer;
    const s = atob(t), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u.buffer; };
  function load(url) {
    if (S.loading) return S.loading;
    S.loading = (async () => {
      const r = await fetch(url || S.url); if (!r.ok) throw new Error('boss pack ' + r.status);
      const buf = fromB64(await r.text()), dv = new DataView(buf);
      if (String.fromCharCode(dv.getUint8(0), dv.getUint8(1), dv.getUint8(2), dv.getUint8(3)) !== 'RMB1') throw new Error('not a boss pack');
      const hl = dv.getUint32(4, true), H = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 8, hl))), base = 8 + hl, o = H.off, n = H.n;
      const at = (k, T, len) => new T(buf, base + o[k], len);
      // positions (quantized to the box), normals (i8), uvs (u16), skin (u8), the extras (u8: the bell's share, the tube coordinate, the tube, the part)
      const qp = at('pos', Uint16Array, n * 3), P = new Float32Array(n * 3), mn = H.bbox[0], mx = H.bbox[1];
      for (let i = 0; i < n * 3; i++) { const k = i % 3; P[i] = mn[k] + qp[i] / 65535 * (mx[k] - mn[k]); }
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(P, 3));
      g.setAttribute('normal', new THREE.InterleavedBufferAttribute(new THREE.InterleavedBuffer(at('nrm', Int8Array, n * 4), 4), 3, 0, true));
      g.setAttribute('uv', new THREE.BufferAttribute(at('uv', Uint16Array, n * 2), 2, true));
      g.setAttribute('skinIndex', new THREE.BufferAttribute(at('si', Uint8Array, n * 4), 4));
      g.setAttribute('skinWeight', new THREE.BufferAttribute(at('sw', Uint8Array, n * 4), 4, true));
      g.setAttribute('aInfo', new THREE.BufferAttribute(at('info', Uint8Array, n * 4), 4, true));
      g.setIndex(new THREE.BufferAttribute(at('idx', Uint16Array, H.ni), 1));
      g.boundingSphere = new THREE.Sphere(new V3(0, -1, 0), 9); g.boundingBox = new THREE.Box3(new V3(-8, -9, -8), new V3(8, 4, 8));
      const tex = (typeof AXO !== 'undefined' && AXO.texFromBytes) ? AXO.texFromBytes(new Uint8Array(buf, base + o.tex, H.texLen), H.texMime) : texFromBytes(new Uint8Array(buf, base + o.tex, H.texLen), H.texMime);
      // the outline's lighter mesh (half the triangles; the shadow is cast from it too), on the same skeleton
      let hg = g;
      if (H.hn) {
        const hn = H.hn, hq = at('hpos', Uint16Array, hn * 3), HP = new Float32Array(hn * 3);
        for (let i = 0; i < hn * 3; i++) { const k = i % 3; HP[i] = mn[k] + hq[i] / 65535 * (mx[k] - mn[k]); }
        hg = new THREE.BufferGeometry(); hg.setAttribute('position', new THREE.BufferAttribute(HP, 3));
        hg.setAttribute('normal', new THREE.InterleavedBufferAttribute(new THREE.InterleavedBuffer(at('hnrm', Int8Array, hn * 4), 4), 3, 0, true));
        hg.setAttribute('skinIndex', new THREE.BufferAttribute(at('hsi', Uint8Array, hn * 4), 4)); hg.setAttribute('skinWeight', new THREE.BufferAttribute(at('hsw', Uint8Array, hn * 4), 4, true));
        hg.setAttribute('aInfo', new THREE.BufferAttribute(at('hinfo', Uint8Array, hn * 4), 4, true)); hg.setIndex(new THREE.BufferAttribute(at('hidx', Uint16Array, H.hni), 1));
        hg.boundingSphere = g.boundingSphere.clone(); hg.boundingBox = g.boundingBox.clone();
      }
      S.pack = { H, geo: g, hgeo: hg, tex }; return S.pack;
    })();
    return S.loading;
  }
  function texFromBytes(bytes, mime) {
    const t = new THREE.Texture(); t.colorSpace = THREE.SRGBColorSpace; t.flipY = false; t.anisotropy = 4;
    const blob = new Blob([bytes], { type: mime || 'image/webp' });
    createImageBitmap(blob, { imageOrientation: 'none', premultiplyAlpha: 'none', colorSpaceConversion: 'none' }).then(img => { t.image = img; t.needsUpdate = true; t.userData.ready = true; });
    return t;
  }

  // ---------------------------------------------------------------- the shader motion every pass shares (body, outline, shadow)
  // The bell's own motion runs here, on the rest shape, before the skin: the pulse (the dome contracts first and the rim follows a
  // moment later: the rim pulls in and the dome rises, then it all flows back out), the skirt's ripples (round the rim and down it,
  // bigger as the pulse flows out), the jelly wobble (two ring modes and a squash, set off by hits and quick moves), the top lagging
  // behind a sideways move, and the slump when it's beaten. Each vertex takes it by its share of the bell (aInfo.x: whole on the bell,
  // fading out where the tubes leave it). The tentacles get a small travelling wave of their own on top of their bones (aInfo.y: how
  // far along, aInfo.z: which one).
  const DEF_GLSL = `
attribute vec4 aInfo;
uniform vec4 bBell;   // rim height, top height, rim radius, time
uniform vec4 bPulse;  // contraction at the top, at the rim (later), skirt ripple strength, slump (0 .. 1)
uniform vec4 bSquash; // vertical scale, top's lag x, top's lag z, swell (round the waist)
uniform vec4 bWob;    // ring mode 2 (amount, angle), ring mode 3 (amount, angle)
uniform vec4 bTent;   // tentacle wave: amount, speed, 0, 0
vec3 bossDef(vec3 p) {
  vec3 q = p; float w = aInfo.x;
  if (w > 0.002) {
    float h = clamp((p.y - bBell.x) / (bBell.y - bBell.x), 0.0, 1.0), rim = 1.0 - h, r = length(p.xz), th = atan(p.z, p.x);
    vec2 dir = r > 1e-4 ? p.xz / r : vec2(0.0);
    float c = mix(bPulse.y, bPulse.x, smoothstep(0.0, 0.85, h));
    float pull = c * (0.17 * rim * rim + 0.035);
    float lift = c * (0.13 * h * h + 0.05 * h) * (bBell.y - bBell.x);
    float sk = smoothstep(0.42, 0.0, h);
    float rip = sin(th * 7.0 - bBell.w * 2.3 + h * 6.0) * 0.6 + sin(th * 4.0 + bBell.w * 1.6 - h * 4.0) * 0.4;
    float dr = -r * pull + bPulse.z * sk * rip * 0.05 * bBell.z;
    dr += r * (bWob.x * cos(2.0 * (th - bWob.y)) + bWob.z * cos(3.0 * (th - bWob.w))) * (0.35 + 0.65 * rim);
    dr += r * bSquash.w * sin(h * 3.14159);
    float dy = lift + bPulse.z * sk * cos(th * 7.0 - bBell.w * 2.3 + h * 6.0) * 0.022 * bBell.z;
    // the slump: the dome sags and spreads, the skirt hangs
    dy -= bPulse.w * (0.55 * h * h * (bBell.y - bBell.x) + 0.25 * rim * (bBell.y - bBell.x));
    dr += bPulse.w * r * 0.22 * h;
    q.xz += dir * dr * w; q.y += dy * w;
    // squash and stretch about the middle (keeping its volume), the top lagging behind a move
    float sy = mix(1.0, bSquash.x, w);
    q.y *= sy; q.xz *= mix(1.0, inversesqrt(max(bSquash.x, 0.2)), w);
    q.xz += bSquash.yz * h * h * w;
  }
  if (aInfo.z > 0.01 && aInfo.z < 0.55) {
    float s = aInfo.y, ph = aInfo.z * 40.0, a = bTent.x * s * s;
    q.x += a * sin(s * 7.0 - bBell.w * bTent.y + ph);
    q.z += a * 0.8 * sin(s * 5.0 - bBell.w * bTent.y * 0.8 + ph * 1.7);
  }
  return q;
}
vec3 bossDefN(vec3 p, vec3 n) {
  vec3 t1 = normalize(abs(n.y) < 0.95 ? cross(n, vec3(0.0, 1.0, 0.0)) : cross(n, vec3(1.0, 0.0, 0.0))), t2 = cross(n, t1);
  vec3 a = bossDef(p), b = bossDef(p + t1 * 0.03), c = bossDef(p + t2 * 0.03), m = normalize(cross(b - a, c - a));
  return dot(m, n) < 0.0 ? -m : m;
}`;
  // the same motion in JS, for the points that ride on the bell: the arms' and tentacles' roots, the face
  function defJS(U, p, out) {
    const B = U.bBell.value, Pp = U.bPulse.value, Sq = U.bSquash.value, Wb = U.bWob.value;
    let x = p.x, y = p.y, z = p.z;
    const h = clamp01((p.y - B.x) / (B.y - B.x)), rim = 1 - h, r = Math.hypot(p.x, p.z), th = Math.atan2(p.z, p.x), dx = r > 1e-4 ? p.x / r : 0, dz = r > 1e-4 ? p.z / r : 0;
    const c = lerp(Pp.y, Pp.x, sstep(0, 0.85, h)), pull = c * (0.17 * rim * rim + 0.035), lift = c * (0.13 * h * h + 0.05 * h) * (B.y - B.x);
    const sk = sstep(0.42, 0, h), rip = Math.sin(th * 7 - B.w * 2.3 + h * 6) * 0.6 + Math.sin(th * 4 + B.w * 1.6 - h * 4) * 0.4;
    let dr = -r * pull + Pp.z * sk * rip * 0.05 * B.z;
    dr += r * (Wb.x * Math.cos(2 * (th - Wb.y)) + Wb.z * Math.cos(3 * (th - Wb.w))) * (0.35 + 0.65 * rim) + r * Sq.w * Math.sin(h * Math.PI);
    let dy = lift + Pp.z * sk * Math.cos(th * 7 - B.w * 2.3 + h * 6) * 0.022 * B.z;
    dy -= Pp.w * (0.55 * h * h * (B.y - B.x) + 0.25 * rim * (B.y - B.x)); dr += Pp.w * r * 0.22 * h;
    x += dx * dr; z += dz * dr; y += dy;
    const sy = Sq.x, sx = 1 / Math.sqrt(Math.max(Sq.x, 0.2)); y *= sy; x *= sx; z *= sx; x += Sq.y * h * h; z += Sq.z * h * h;
    return out.set(x, y, z);
  }

  // ---------------------------------------------------------------- materials
  // The jelly: the texture's own colours, glossy, lit from inside (a soft glow of its own, light wrapping round into the shadow side and
  // shining through the thin edges), a bright rim at grazing angles, deeper and richer where you look straight in. The gloves stay
  // a clean glossy white (the rim and the glow are the jelly's only); the cuffs are glossy rubber. A flash on hits and a purple charge
  // glow ride on top; below the pool's surface it isn't drawn (rising out of it, sinking into it), with a band of slime at the line.
  const LOOK_U = () => ({ bFlash: { value: new THREE.Vector4(0, 0, 0, 0) }, bGlow: { value: new THREE.Vector4(0.62, 1, 0, 0) }, bClip: { value: new THREE.Vector4(-1e4, 0, 0, 0) } });
  const BODY_VS_PARS = DEF_GLSL + '\nvarying vec4 vInfo; varying vec3 vWp;';
  const BODY_FS_PARS = `varying vec4 vInfo; varying vec3 vWp; uniform vec4 bFlash, bGlow, bClip;`;
  const BODY_FS_MAIN = `
{ float part = vInfo.w * 8.0, glove = smoothstep(4.5, 5.0, part), cuff = smoothstep(3.5, 4.0, part) * (1.0 - glove), jelly = 1.0 - smoothstep(3.5, 4.0, part);
  vec3 Vd = normalize(vViewPosition), Nn = normalize(nonPerturbedNormal);
  float ndv = clamp(abs(dot(Nn, Vd)), 0.0, 1.0), fr = pow(1.0 - ndv, 2.6);
  vec3 base = diffuseColor.rgb;
  // its own light: richer straight on, a bright pink-white rim at the edges, brighter toward the tentacles' tips
  vec3 deep = base * (base * 1.1 + 0.18);
  float tip = smoothstep(0.55, 1.0, vInfo.y) * step(0.01, vInfo.z) * step(vInfo.z, 0.55);
  totalEmissiveRadiance += jelly * (deep * (0.55 + 0.25 * tip) * bGlow.x + mix(base, vec3(1.0, 0.82, 0.97), 0.45) * fr * 1.05 * bGlow.y);
  totalEmissiveRadiance += cuff * base * 0.12 + glove * vec3(0.10, 0.09, 0.14) * (0.5 + fr);
  // the purple charge (pulsing), the hit flash
  totalEmissiveRadiance += vec3(0.62, 0.22, 1.0) * bGlow.z * (0.55 + 0.45 * sin(bGlow.w)) * (0.4 + fr) * (jelly + 0.35 * glove);
  totalEmissiveRadiance += bFlash.rgb * bFlash.a * (0.5 + 0.5 * fr);
  // the pool's line: a glowing band of slime just above it
  float sl = bClip.y > 0.0 ? 1.0 - smoothstep(0.0, bClip.y, vWp.y - bClip.x) : 0.0;
  totalEmissiveRadiance = mix(totalEmissiveRadiance, vec3(0.35, 1.0, 0.25), sl * 0.85);
}`;
  function patchBody(sh, U) {
    Object.assign(sh.uniforms, U);
    sh.vertexShader = BODY_VS_PARS + '\n' + sh.vertexShader
      .replace('#include <beginnormal_vertex>', 'vec3 objectNormal = bossDefN(position, normal);')
      .replace('#include <begin_vertex>', 'vec3 transformed = bossDef(position); vInfo = aInfo;')
      .replace('#include <project_vertex>', '#include <project_vertex>\n vWp = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = BODY_FS_PARS + '\n' + sh.fragmentShader
      .replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\n if (vWp.y < bClip.x) discard;')
      // (the jelly a little pinker and lighter than the texture, whose patches lean blue: closer to the picture)
      .replace('#include <map_fragment>', '#include <map_fragment>\n { float jj = 1.0 - smoothstep(3.5, 4.0, vInfo.w * 8.0); diffuseColor.rgb = mix(diffuseColor.rgb, diffuseColor.rgb * vec3(1.14, 0.9, 0.97) + vec3(0.05, 0.012, 0.04), jj * 0.75); }')
      .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\n' + BODY_FS_MAIN);
    return sh;
  }
  // (in r186 the skinned vertex shader includes skinning after begin_vertex; the world position used above is after the skin, since it's
  // taken at project_vertex where transformed already holds the skinned position)
  function bodyMat(U, tex) {
    let m;
    if (HIQ) m = new THREE.MeshPhysicalMaterial({ map: tex, roughness: 0.3, metalness: 0, clearcoat: 0.85, clearcoatRoughness: 0.12, envMapIntensity: 0.9, sheen: 0.35, sheenRoughness: 0.5, sheenColor: new THREE.Color(1, 0.8, 0.95) });
    else m = new THREE.MeshToonMaterial({ map: tex, gradientMap: typeof grad !== 'undefined' ? grad : null });
    m.onBeforeCompile = sh => patchBody(sh, U);
    m.customProgramCacheKey = () => 'boss-body-' + (HIQ ? 'hi' : 'lo');
    return m;
  }
  // the outline: the back faces pushed out along the moved normals, as wide (on screen) as the game's own outlines
  function inkMat(U) {
    const m = new THREE.MeshBasicMaterial({ color: INK_C, side: THREE.BackSide });
    m.onBeforeCompile = sh => {
      Object.assign(sh.uniforms, U, { gLine: INK_W });
      sh.vertexShader = BODY_VS_PARS + '\nuniform float gLine;\n' + sh.vertexShader
        .replace('#include <beginnormal_vertex>', 'vec3 objectNormal = bossDefN(position, normal);')
        .replace('#include <begin_vertex>', 'vec3 transformed = bossDef(position); vInfo = aInfo;')
        .replace('#include <project_vertex>', `{ float iS = length(modelMatrix[0].xyz), iD = -(modelViewMatrix * vec4(transformed, 1.0)).z;
  float wd = clamp(gLine * iD / max(iS, 1e-3), 0.004, 0.07) * (aInfo.w * 8.0 > 4.5 ? 0.85 : 1.0);
  transformed += normalize(objectNormal) * wd; }
#include <project_vertex>
vWp = (modelMatrix * vec4(transformed, 1.0)).xyz;`);
      sh.fragmentShader = BODY_FS_PARS + '\n' + sh.fragmentShader.replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\n if (vWp.y < bClip.x) discard;');
    };
    m.customProgramCacheKey = () => 'boss-ink';
    return m;
  }
  function depthMat(U) {
    const m = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking });
    m.onBeforeCompile = sh => { Object.assign(sh.uniforms, U); sh.vertexShader = DEF_GLSL + '\n' + sh.vertexShader.replace('#include <begin_vertex>', 'vec3 transformed = bossDef(position);'); };
    m.customProgramCacheKey = () => 'boss-depth';
    return m;
  }

  // ---------------------------------------------------------------- the face: two eyes and two brows on the front of the bell
  // The model has no face, so it gets one: each eye a white cap bulging out of the jelly, drawn in its shader (the upper lid's slant for
  // anger, a lower lid for squints, the pupil with its shine, spiral eyes when dizzy, "> <" when hurt, a glow when charged), and each
  // brow a thick jelly ridge with an ink outline that rides on the upper lid. One mesh, one draw: each piece has its own transform.
  const EYE = { w: 0.42, h: 0.47, d: 0.17 }, BROW = { len: 0.74, r: 0.1 };
  function faceGeo() {
    const P = [], N = [], F = [], I = [];
    const vert = (p, n, f) => { P.push(p.x, p.y, p.z); N.push(n.x, n.y, n.z); F.push(f[0], f[1], f[2], f[3]); return P.length / 3 - 1; };
    // an eye: the front of an ellipsoid (a little past its equator, so it sinks into the bell all round)
    for (const part of [0, 1]) {
      const R = 12, A = 22, base = P.length / 3;
      for (let i = 0; i <= R; i++) { const ph = i / R * 1.95; for (let j = 0; j <= A; j++) { const th = j / A * Math.PI * 2, sx = Math.sin(ph) * Math.cos(th), sy = Math.sin(ph) * Math.sin(th), sz = Math.cos(ph);
        const p = new V3(sx * EYE.w, sy * EYE.h, (sz - 0.18) * EYE.d), n = new V3(sx / EYE.w, sy / EYE.h, sz / EYE.d).normalize();
        vert(p, n, [part, sx, sy, 0]); } }
      for (let i = 0; i < R; i++) for (let j = 0; j < A; j++) { const a = base + i * (A + 1) + j, b = a + A + 1; I.push(a, b, a + 1, b, b + 1, a + 1); }
    }
    // a brow: a tube along a shallow arch with rounded ends, fatter in the middle; and its outline (pushed out, faces turned round)
    for (const part of [2, 3]) for (const ink of [0, 1]) {
      const L = 16, A = 10, base = P.length / 3, out = ink ? 0.026 : 0;
      for (let i = 0; i <= L; i++) {
        const u = i / L, x = (u - 0.5) * BROW.len, y = 0.06 * (1 - Math.pow(2 * u - 1, 2)), cap = Math.sin(Math.min(1, Math.min(u, 1 - u) / 0.16) * Math.PI / 2);
        const rad = BROW.r * (0.75 + 0.25 * Math.sin(u * Math.PI)) * Math.max(0.12, cap);
        const tx = 1, ty = -0.24 * (2 * u - 1), tl = Math.hypot(tx, ty), T1 = new V3(tx / tl, ty / tl, 0), Nn = new V3(-T1.y, T1.x, 0), Bn = new V3(0, 0, 1);
        for (let j = 0; j <= A; j++) { const th = j / A * Math.PI * 2, c = Math.cos(th), s2 = Math.sin(th);
          const n = new V3().addScaledVector(Nn, c).addScaledVector(Bn, s2 * 1.25).normalize();
          const p = new V3(x, y, 0.035).addScaledVector(Nn, c * rad).addScaledVector(Bn, s2 * rad * 0.85).addScaledVector(n, out);
          if (u === 0 || u === 1) p.set(x + (u === 0 ? -1 : 1) * out * 0.6, y, 0.035);
          vert(p, n, [part, u, (j / A), ink]); }
      }
      for (let i = 0; i < L; i++) for (let j = 0; j < A; j++) { const a = base + i * (A + 1) + j, b = a + A + 1; if (ink) I.push(a, a + 1, b, b, a + 1, b + 1); else I.push(a, b, a + 1, b, b + 1, a + 1); }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); g.setAttribute('normal', new THREE.Float32BufferAttribute(N, 3)); g.setAttribute('aF', new THREE.Float32BufferAttribute(F, 4)); g.setIndex(I);
    g.boundingSphere = new THREE.Sphere(new V3(0, 0, 0), 20); return g;
  }
  const FACE_VS = `attribute vec4 aF; varying vec4 vF; varying vec3 vFw; uniform mat4 fM[4];`;
  const FACE_FS_PARS = `varying vec4 vF; varying vec3 vFw; uniform vec4 fEA[2], fEB[2], fEC[2], bClip; uniform vec3 fSkin, fBrow, fInk; uniform vec4 fT;
float segD(vec2 p, vec2 a, vec2 b) { vec2 pa = p - a, ba = b - a; return length(pa - ba * clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0)); }`;
  // the eye, drawn: e is the spot on the eye in its own ellipse (-1 .. 1). A: the upper lid's height, its slant (down toward the nose),
  // the lower lid's height, its slant; B: the pupil (x, y, size), the glow; C: "> <", spirals, which way the nose is (1 / -1)
  const FACE_FS = `
vec3 fCol = diffuseColor.rgb; float fUnlit = 0.0; vec3 fEmi = vec3(0.0); float fInkK = 0.0;
if (vF.x < 1.5) {
  vec4 A = vF.x < 0.5 ? fEA[0] : fEA[1], B = vF.x < 0.5 ? fEB[0] : fEB[1], Cc = vF.x < 0.5 ? fEC[0] : fEC[1];
  vec2 e = vF.yz; float r = length(e), ui = e.x * Cc.z;
  float yl = A.x - A.y * ui, yb = A.z + A.w * ui;
  float lidU = smoothstep(-0.015, 0.015, e.y - yl), lidB = smoothstep(-0.015, 0.015, yb - e.y), lid = max(lidU, lidB);
  // the white: a little grey under the lid's edge and round the rim
  vec3 white = vec3(0.98, 0.97, 1.0) * (1.0 - 0.22 * smoothstep(0.62, 1.0, r)) * (1.0 - 0.28 * smoothstep(-0.32, 0.0, e.y - yl));
  // the pupil: dark, a deep violet rim, two catch-lights
  vec2 pc = B.xy; vec2 dp = (e - pc) * vec2(1.0, 0.87); float pd = length(dp), pr = B.z;
  float pup = 1.0 - smoothstep(pr - 0.02, pr + 0.02, pd);
  vec3 pcol = mix(vec3(0.05, 0.02, 0.10), vec3(0.20, 0.07, 0.30), smoothstep(pr * 0.55, pr, pd));
  float hl = 1.0 - smoothstep(0.0, 0.035, length(e - pc - vec2(-0.32, 0.36) * pr) - pr * 0.27), hl2 = 1.0 - smoothstep(0.0, 0.02, length(e - pc - vec2(0.3, -0.3) * pr) - pr * 0.11);
  pcol = mix(pcol, vec3(1.0), max(hl, hl2 * 0.8));
  // spirals for dizzy
  float an = atan(e.y - pc.y * 0.4, e.x - pc.x * 0.4), sp = fract(an / 6.2832 + r * 2.4 - fT.x * 1.3), spiral = smoothstep(0.42, 0.36, abs(sp - 0.5)) * (1.0 - smoothstep(0.78, 0.86, r));
  vec3 col = mix(white, pcol, pup * (1.0 - Cc.y));
  col = mix(col, vec3(0.12, 0.05, 0.2), spiral * Cc.y);
  // the glow: the open part burns pink-white, no pupil
  float gl = B.w; col = mix(col, vec3(1.0, 0.86, 1.0), gl); fEmi += vec3(1.0, 0.35, 0.95) * gl * 2.2 * (1.0 - lid);
  // the lids: the bell's own pink, shaded under the brow; an ink line along each edge and round the rim
  vec3 skin = fSkin * (0.78 + 0.22 * smoothstep(0.0, 0.5, e.y - yl));
  col = mix(col, skin, lid);
  float lineU = 1.0 - smoothstep(0.045, 0.075, abs(e.y - yl)), lineB = (1.0 - smoothstep(0.03, 0.055, abs(e.y - yb))) * step(-0.98, A.z);
  float rim = smoothstep(0.86, 0.93, r) * (1.0 - lid * 0.6);
  float ink = max(max(lineU, lineB * 0.9), rim);
  // "> <": two strokes meeting toward the nose, on the shut lids
  float xa = segD(vec2(ui, e.y), vec2(0.5, 0.0), vec2(-0.45, 0.45)), xb = segD(vec2(ui, e.y), vec2(0.5, 0.0), vec2(-0.45, -0.45));
  float xx = (1.0 - smoothstep(0.075, 0.11, min(xa, xb))) * Cc.x;
  ink = max(ink * (1.0 - Cc.x * 0.85), xx);
  fCol = mix(col, fInk, ink); fUnlit = mix(0.6 * (1.0 - lid), 0.85, ink); fInkK = ink;
} else if (vF.w < 0.5) {
  fCol = fBrow * (0.9 + 0.1 * vF.z); fUnlit = 0.0;
} else { fCol = fInk; fUnlit = 1.0; fInkK = 1.0; }
diffuseColor.rgb = fCol;`;
  function faceMat(FU) {
    const m = HIQ ? new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.22, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.06, envMapIntensity: 0.8 })
      : new THREE.MeshToonMaterial({ color: 0xffffff, gradientMap: typeof grad !== 'undefined' ? grad : null });
    m.onBeforeCompile = sh => {
      Object.assign(sh.uniforms, FU);
      sh.vertexShader = FACE_VS + '\n' + sh.vertexShader
        .replace('#include <beginnormal_vertex>', 'mat4 fMx = aF.x < 0.5 ? fM[0] : aF.x < 1.5 ? fM[1] : aF.x < 2.5 ? fM[2] : fM[3]; vec3 objectNormal = normalize(mat3(fMx) * normal);')
        .replace('#include <begin_vertex>', 'vec3 transformed = (fMx * vec4(position, 1.0)).xyz; vF = aF;')
        .replace('#include <project_vertex>', '#include <project_vertex>\n vFw = (modelMatrix * vec4(transformed, 1.0)).xyz;');
      sh.fragmentShader = FACE_FS_PARS + '\n' + sh.fragmentShader
        .replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\n if (vFw.y < bClip.x) discard;')
        .replace('#include <color_fragment>', '#include <color_fragment>\n' + FACE_FS)
        .replace('#include <opaque_fragment>', 'outgoingLight = mix(outgoingLight, fCol * (fInkK > 0.5 ? 1.0 : 0.92), fUnlit) + fEmi;\n#include <opaque_fragment>');
    };
    m.customProgramCacheKey = () => 'boss-face-' + (HIQ ? 'hi' : 'lo');
    return m;
  }

  // ---------------------------------------------------------------- the lightning, glows and shockwave rings: one dynamic mesh, one draw
  // Arcs are jagged polylines drawn as ribbons that face the camera (a hot white core inside a soft purple glow), re-formed many times a
  // second: rings of them hugging each fist's outline, bolts for the zap, bursts that spray out from an impact. Glows are soft discs
  // that face the camera; rings lie flat on the floor and spread. Everything is written into fixed buffers each frame.
  const ARC_N = 36, ARC_P = 14, GLOW_N = 6, RING_N = 4;
  const FX_VS = `attribute vec4 aS; attribute vec3 aT; varying vec4 vS;
void main() {
  vS = aS; vec4 mv = modelViewMatrix * vec4(position, 1.0); float layer = aS.y, ks = length(modelMatrix[0].xyz);
  if (layer < 1.5) {
    vec4 mt = modelViewMatrix * vec4(position + aT * 0.05, 1.0); vec2 d = mt.xy - mv.xy; d = length(d) > 1e-6 ? normalize(d) : vec2(1.0, 0.0);
    float w = (layer < 0.5 ? 0.042 : 0.21) * aS.z * ks;
    mv.xy += vec2(-d.y, d.x) * aS.x * w;
  } else if (layer < 2.5) { mv.xy += vec2(aS.x, aS.z) * aT.x * ks; }
  else { mv = modelViewMatrix * vec4(position + vec3(aS.x, 0.0, aS.z) * aT.x, 1.0); }
  gl_Position = projectionMatrix * mv;
}`;
  const FX_FS = `varying vec4 vS;
void main() {
  float layer = vS.y, a = 0.0; vec3 c = vec3(0.0);
  if (layer < 0.5) { float s = abs(vS.x); a = (1.0 - s * s) * vS.w; c = mix(vec3(0.78, 0.38, 1.0), vec3(1.0, 0.96, 1.0), 1.0 - smoothstep(0.0, 0.65, s)) * 2.1; }
  else if (layer < 1.5) { float s = abs(vS.x); a = exp(-s * s * 3.5) * 0.55 * vS.w; c = vec3(0.64, 0.24, 1.0); }
  else if (layer < 2.5) { float r = length(vec2(vS.x, vS.z)); a = exp(-r * r * 4.0) * vS.w; c = vec3(0.7, 0.3, 1.0) * (1.0 + 0.8 * exp(-r * r * 30.0)); }
  else { float r = length(vec2(vS.x, vS.z)); float ring = exp(-pow((r - 0.86) / 0.07, 2.0)) + 0.18 * (1.0 - smoothstep(0.0, 0.86, r)); a = ring * vS.w * (1.0 - smoothstep(0.95, 1.0, r)); c = mix(vec3(0.62, 0.25, 1.0), vec3(1.0, 0.9, 1.0), exp(-pow((r - 0.86) / 0.035, 2.0))); }
  if (a < 0.004) discard;
  gl_FragColor = vec4(c * a, a);
}`;
  function makeFX() {
    const nArcV = ARC_N * 2 * ARC_P * 2, nV = nArcV + (GLOW_N + RING_N) * 4;
    const pos = new Float32Array(nV * 3), aS = new Float32Array(nV * 4), aT = new Float32Array(nV * 3), idx = [];
    // arc k, layer l (core, glow): ARC_P points, two verts each (the ribbon's two sides)
    for (let k = 0; k < ARC_N; k++) for (let l = 0; l < 2; l++) { const b = (k * 2 + l) * ARC_P * 2; for (let i = 0; i < ARC_P - 1; i++) { const a = b + i * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); } }
    for (let q = 0; q < GLOW_N + RING_N; q++) { const a = nArcV + q * 4; idx.push(a, a + 1, a + 2, a, a + 2, a + 3); }
    const g = new THREE.BufferGeometry();
    const pA = new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage), sA = new THREE.BufferAttribute(aS, 4).setUsage(THREE.DynamicDrawUsage), tA = new THREE.BufferAttribute(aT, 3).setUsage(THREE.DynamicDrawUsage);
    g.setAttribute('position', pA); g.setAttribute('aS', sA); g.setAttribute('aT', tA); g.setIndex(idx); g.boundingSphere = new THREE.Sphere(new V3(), 1e4);
    const mat = new THREE.ShaderMaterial({ vertexShader: FX_VS, fragmentShader: FX_FS, transparent: true, depthWrite: false, side: THREE.DoubleSide, blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendEquation: THREE.AddEquation, fog: false });
    const mesh = new THREE.Mesh(g, mat); mesh.frustumCulled = false; mesh.renderOrder = 40;
    const arcs = []; for (let k = 0; k < ARC_N; k++) arcs.push({ on: false, life: 0, t: 0, kind: 0, hand: -1, int: 0, pts: new Float32Array(ARC_P * 3), regen: 0, A: new V3(), B: new V3(), w: 1 });
    const glows = []; for (let k = 0; k < GLOW_N; k++) glows.push({ on: false, p: new V3(), size: 1, int: 0 });
    const rings = []; for (let k = 0; k < RING_N; k++) rings.push({ on: false, p: new V3(), r: 0, r1: 1, t: 0, life: 0.6, int: 1 });
    return { mesh, g, pA, sA, tA, pos, aS, aT, arcs, glows, rings, nArcV };
  }

  // ---------------------------------------------------------------- particles: bubbles, slime drops, jelly drips and sparkles (one draw)
  const PT_N = 140;
  const PT_VS = `attribute vec4 aP; attribute vec3 aC; varying vec4 vP; varying vec3 vC; uniform float ptPx;
void main() { vP = aP; vC = aC; vec4 mv = modelViewMatrix * vec4(position, 1.0); gl_Position = projectionMatrix * mv; gl_PointSize = aP.x * ptPx * length(modelMatrix[0].xyz) / max(0.1, -mv.z); }`;
  const PT_FS = `varying vec4 vP; varying vec3 vC;
void main() {
  vec2 q = gl_PointCoord * 2.0 - 1.0; q.y = -q.y; float r = length(q); if (r > 1.0 || vP.y < 0.004) discard;
  float a; vec3 c;
  if (vP.z < 0.5) { float rim = smoothstep(0.62, 0.95, r) * (1.0 - smoothstep(0.95, 1.0, r)); float hl = 1.0 - smoothstep(0.0, 0.28, length(q - vec2(-0.35, 0.38)));
    a = (rim * 0.75 + 0.12 + hl * 0.9) * vP.y; c = mix(vC, vec3(1.0), hl * 0.8 + rim * 0.25); }
  else if (vP.z < 2.5) { float sh = clamp(dot(normalize(vec3(q, sqrt(max(0.0, 1.0 - r * r)))), normalize(vec3(-0.4, 0.5, 0.75))), 0.0, 1.0);
    a = (1.0 - smoothstep(0.85, 1.0, r)) * vP.y; c = vC * (0.55 + 0.6 * sh) + pow(sh, 18.0) * 0.8; }
  else { a = exp(-r * r * 4.0) * vP.y; c = vC * 1.6; }
  gl_FragColor = vec4(c, a);
}`;
  function makeParticles() {
    const pos = new Float32Array(PT_N * 3), aP = new Float32Array(PT_N * 4), aC = new Float32Array(PT_N * 3);
    const g = new THREE.BufferGeometry();
    const pA = new THREE.BufferAttribute(pos, 3).setUsage(THREE.DynamicDrawUsage), PA = new THREE.BufferAttribute(aP, 4).setUsage(THREE.DynamicDrawUsage), CA = new THREE.BufferAttribute(aC, 3).setUsage(THREE.DynamicDrawUsage);
    g.setAttribute('position', pA); g.setAttribute('aP', PA); g.setAttribute('aC', CA); g.boundingSphere = new THREE.Sphere(new V3(), 1e4);
    const U = { ptPx: { value: 400 } };
    const mat = new THREE.ShaderMaterial({ uniforms: U, vertexShader: PT_VS, fragmentShader: PT_FS, transparent: true, depthWrite: false, fog: false });
    const pts = new THREE.Points(g, mat); pts.frustumCulled = false; pts.renderOrder = 39;
    const P = []; for (let i = 0; i < PT_N; i++) P.push({ on: false, p: new V3(), v: new V3(), t: 0, life: 1, size: 0.1, type: 0, c: new THREE.Color(), g: 0, drag: 1, a: 1, wob: Math.random() * 6 });
    return { pts, g, pA, PA, CA, pos, aP, aC, P, U, next: 0 };
  }

  // ---------------------------------------------------------------- the rig's fixed data (once per pack)
  function rigData(H) {
    const nb = H.bones.length, idx = {}; H.bones.forEach((b, i) => { idx[b.name] = i; });
    const R = { nb, idx, bind: [], binv: [], rp: [], rq: [], ep: [], len: [], par: [], loc: [] }, one = new V3(1, 1, 1);
    for (let i = 0; i < nb; i++) {
      const b = H.bones[i], p = new V3().fromArray(b.pos), q = new Q4().fromArray(b.q), e = new V3().fromArray(b.end), m = new M4().compose(p, q, one);
      R.bind.push(m); R.binv.push(m.clone().invert()); R.rp.push(p); R.rq.push(q); R.ep.push(e); R.len.push(e.distanceTo(p)); R.par.push(b.parent ? idx[b.parent] : -1);
    }
    for (let i = 0; i < nb; i++) R.loc.push(R.par[i] >= 0 ? R.binv[R.par[i]].clone().multiply(R.bind[i]) : R.bind[i].clone());
    R.tent = H.tent.map((t, k) => {
      const ids = t.bones.map(n => idx[n]), J = ids.map(i => R.rp[i].clone()); J.push(R.ep[ids[ids.length - 1]].clone());
      const L = []; for (let j = 0; j < ids.length; j++) L.push(J[j + 1].distanceTo(J[j]));
      return { ids, J, L, name: t.name, rad: t.rad, n: ids.length, k };
    });
    R.arm = {};
    for (const s of SIDES) {
      const A = H.arms[s], ids = A.bones.map(n => idx[n]), J = ids.map(i => R.rp[i].clone()); J.push(R.ep[ids[5]].clone());
      const t0 = J[1].clone().sub(J[0]).normalize(), t1 = J[6].clone().sub(J[5]).normalize(), chord = J[6].distanceTo(J[0]);
      // the rest curve as a cubic: the handle lengths that best fit the six rest joints
      let best = 1e9, l0 = 0.3 * chord, l1 = 0.3 * chord; const tmp = new V3(), P1 = new V3(), P2 = new V3(), pts = [];
      for (let a = 1; a <= 16; a++) for (let b = 1; b <= 16; b++) {
        const L0 = a / 16 * 1.2 * chord, L1 = b / 16 * 1.2 * chord; P1.copy(J[0]).addScaledVector(t0, L0); P2.copy(J[6]).addScaledVector(t1, -L1);
        pts.length = 0; for (let i = 0; i <= 30; i++) pts.push(bez(J[0], P1, P2, J[6], i / 30, new V3()));
        const cum = [0]; for (let i = 1; i <= 30; i++) cum.push(cum[i - 1] + pts[i].distanceTo(pts[i - 1]));
        let e = 0; for (let k = 1; k < 6; k++) { at(pts, cum, k / 6, tmp); e += tmp.distanceToSquared(J[k]); }
        if (e < best) { best = e; l0 = L0; l1 = L1; }
      }
      let restLen = 0; for (let k = 0; k < 6; k++) restLen += J[k + 1].distanceTo(J[k]);
      const qRel = R.rq[ids[5]].clone().invert().multiply(R.rq[idx[A.hand]]);
      const dig = {}; for (const d in A.digits) dig[d] = A.digits[d].map(n => idx[n]);
      R.arm[s] = { ids, J, t0, t1, l0, l1, restLen, hand: idx[A.hand], cuff: idx[A.cuff], dig, rad: A.rad, qRel, palmN: new V3().fromArray(A.palmN), fwd: new V3().fromArray(A.fwd), sgn: s === 'L' ? 1 : -1 };
      // each finger's turn (about the palm's normal) that lines it up with the middle finger: how far it closes up in a fist
      const mid = R.rq[dig.middle[0]], mY = new V3(0, 1, 0).applyQuaternion(mid);
      R.arm[s].tog = {}; for (const d in dig) { const q = R.rq[dig[d][0]], Y = new V3(0, 1, 0).applyQuaternion(q), Z = new V3(0, 0, 1).applyQuaternion(q), X = new V3(1, 0, 0).applyQuaternion(q);
        R.arm[s].tog[d] = d === 'thumb' ? 0 : Math.atan2(-mY.dot(X), mY.dot(Y)); }
    }
    return R;
  }
  function bez(a, b, c, d, t, out) { const u = 1 - t, w0 = u * u * u, w1 = 3 * u * u * t, w2 = 3 * u * t * t, w3 = t * t * t;
    return out.set(a.x * w0 + b.x * w1 + c.x * w2 + d.x * w3, a.y * w0 + b.y * w1 + c.y * w2 + d.y * w3, a.z * w0 + b.z * w1 + c.z * w2 + d.z * w3); }
  function at(pts, cum, f, out) { const L = f * cum[cum.length - 1]; let i = 1; while (i < cum.length - 1 && cum[i] < L) i++;
    const t = (L - cum[i - 1]) / Math.max(1e-9, cum[i] - cum[i - 1]); return out.copy(pts[i - 1]).lerp(pts[i], clamp01(t)); }

  // hand poses: per digit, per joint [flex, spread, twist] (radians; flex curls toward the palm, spread turns about the palm's normal)
  const POSE = {
    open:   { f: [[0.05, 0, 0], [0.05, 0, 0], [0.04, 0, 0]], t: [[0.0, 0, 0], [0.05, 0, 0], [0.05, 0, 0]], tog: 0 },
    relax:  { f: [[0.32, 0, 0], [0.42, 0, 0], [0.3, 0, 0]], t: [[0.12, 0.1, 0], [0.25, 0, 0], [0.2, 0, 0]], tog: 0.35 },
    // (the fist: curled just short of the fingers pressing into the palm, which would show the outline through the creases; the thumb's
    // angles were fitted on the rig so it wraps round the side and tucks over the curled index, as on the owner's sheet, a little long)
    fist:   { f: [[1.3, 0, 0], [1.25, 0, 0], [0.85, 0, 0]], t: [[0.911, 0.876, -0.447], [0.694, 0, 0], [0.158, 0, 0]], tst: 1.25, tog: 0.85 },
    spread: { f: [[-0.16, 0, 0], [-0.1, 0, 0], [-0.05, 0, 0]], t: [[-0.1, -0.15, 0], [-0.05, 0, 0], [0, 0, 0]], tog: -0.3 },
  };
  const POSE_NAMES = ['open', 'relax', 'fist', 'point', 'spread'];
  const DIG_ORDER = ['thumb', 'index', 'middle', 'pinky'], SIDES = ['L', 'R'];
  // (point: the index straight, the rest a fist)
  function poseAngles(name, d, j, out) {
    const P = name === 'point' ? (d === 'index' ? POSE.open : POSE.fist) : POSE[name];
    const a = d === 'thumb' ? P.t[j] : P.f[j]; out[0] = a[0]; out[1] = a[1]; out[2] = a[2];
    // (the close-up turn; for the thumb this channel carries its stretch instead: a cartoon thumb reaches round the fist)
    out[3] = d === 'thumb' ? (P.tst || 1) - 1 : (name === 'point' ? (d === 'index' ? 0.1 : 0.9) : P.tog);
    if (name === 'point' && d === 'thumb') { out[0] *= 0.9; }
    return out;
  }

  // the expressions: the upper lid's height and slant (down toward the nose), the lower lid's, the pupil's size, a glow, "> <", spirals,
  // the brows' tilt (inner end down) for the left and the right, how high they ride, a squint of the eye cap
  const EXPR = {
    angry:     { lid: 0.32, sl: 0.62, low: -1.3, lsl: 0, pr: 0.31, glow: 0, xx: 0, dz: 0, bL: 0.42, bR: 0.42, bY: 0.0, gx: 0 },
    glare:     { lid: 0.2, sl: 0.55, low: -0.6, lsl: 0.12, pr: 0.27, glow: 0, xx: 0, dz: 0, bL: 0.5, bR: 0.5, bY: -0.02, gx: 0.34 },
    charging:  { lid: 0.24, sl: 0.5, low: -0.78, lsl: 0.1, pr: 0.24, glow: 0.35, xx: 0, dz: 0, bL: 0.58, bR: 0.58, bY: -0.03, gx: 0 },
    glow:      { lid: 0.3, sl: 0.46, low: -0.62, lsl: 0.12, pr: 0.24, glow: 1, xx: 0, dz: 0, bL: 0.6, bR: 0.6, bY: -0.03, gx: 0 },
    hurt:      { lid: 0.02, sl: 0.0, low: -0.02, lsl: 0, pr: 0.3, glow: 0, xx: 1, dz: 0, bL: -0.42, bR: -0.42, bY: 0.07, gx: 0 },
    dizzy:     { lid: 0.64, sl: 0.05, low: -1.3, lsl: 0, pr: 0.3, glow: 0, xx: 0, dz: 1, bL: -0.25, bR: 0.15, bY: 0.05, gx: 0 },
    smug:      { lid: 0.0, sl: -0.14, low: -0.6, lsl: -0.1, pr: 0.27, glow: 0, xx: 0, dz: 0, bL: 0.36, bR: -0.22, bY: 0.02, gx: -0.12 },
    defeated:  { lid: 0.08, sl: -0.48, low: -1.3, lsl: 0, pr: 0.22, glow: 0, xx: 0, dz: 0, bL: -0.5, bR: -0.5, bY: 0.05, gx: 0 },
    surprised: { lid: 1.08, sl: 0.0, low: -1.3, lsl: 0, pr: 0.2, glow: 0, xx: 0, dz: 0, bL: -0.15, bR: -0.15, bY: 0.14, gx: 0 },
    neutral:   { lid: 0.72, sl: 0.12, low: -1.3, lsl: 0, pr: 0.3, glow: 0, xx: 0, dz: 0, bL: 0.12, bR: 0.12, bY: 0.04, gx: 0 },
  };
  const EKEYS = ['lid', 'sl', 'low', 'lsl', 'pr', 'glow', 'xx', 'dz', 'bL', 'bR', 'bY', 'gx'];
  const wn = (t, a, b, c) => Math.sin(t * a) * 0.5 + Math.sin(t * b + 1.7) * 0.3 + Math.sin(t * c + 4.1) * 0.2;   // (a smooth wander, -1 .. 1)

  // ---------------------------------------------------------------- a boss
  function makeBoss(opts) {
    opts = opts || {};
    const group = new THREE.Group(), model = new THREE.Group(); group.add(model); group.name = 'boss';
    const scale = opts.scale || 1, HOVER = opts.hover || 5.6, FLOOR = opts.floorY || 0, FIST_R = 0.5, GLOVE = opts.glove || 1.3, GLOW = opts.glow || 1;
    group.scale.setScalar(scale);
    const B = { group, isReady: false, busy: false, scale, stats: { tris: 0, draws: 0, cpuMs: 0 }, fistR: 0.6 * scale, bellR: 2.2 * scale, move: 'idle' };
    const evs = {};
    B.on = (n, f) => { (evs[n] || (evs[n] = [])).push(f); return B; };
    B.off = (n, f) => { const L = evs[n]; if (L) { const i = L.indexOf(f); if (i >= 0) L.splice(i, 1); } return B; };
    B.onHit = f => B.on('hit', f);
    const emit = (n, d) => { const L = evs[n]; if (L) for (let i = 0; i < L.length; i++) { try { L[i](d); } catch (e) { console.error(e); } } };
    let queued = [], built = null;
    B.ready = load(opts.url).then(pack => { built = build(pack); B.isReady = true; const q = queued; queued = null; for (const a of q) B.play(a[0], a[1]); return B; });
    B.ready.catch(e => console.warn('boss', e));
    B.play = (name, o) => { if (!built) { if (queued) queued.push([name, o]); return 0; } return built.play(name, o || {}); };
    B.update = (dt, ctx) => { if (built) built.update(dt, ctx || {}); };
    B.lookAt = (x, y, z) => { if (built) built.lookAt(x, y, z); else if (x === null || x === undefined) {} };
    B.face = (e, hold) => { if (built) built.face(e, hold); };
    B.hand = (s, p) => { if (built) built.hand(s, p); };
    B.fist = (s, out) => built ? built.fist(s, out) : (out || new V3()).copy(group.position);
    B.bellPoint = out => built ? built.bellPoint(out) : (out || new V3()).copy(group.position);
    B.dispose = () => { if (built) built.dispose(); group.removeFromParent(); };
    return B;

    function build(pack) {
      const H = pack.H, R = pack.rig || (pack.rig = rigData(H)), nb = R.nb;
      // ---- the shader motion's uniforms (shared by the body, its outline and its shadow) and the look's
      const U = Object.assign({ bBell: { value: new THREE.Vector4(H.bell.yRim, H.bell.yTop, H.bell.rRim, 0) }, bPulse: { value: new THREE.Vector4() }, bSquash: { value: new THREE.Vector4(1, 0, 0, 0) },
        bWob: { value: new THREE.Vector4() }, bTent: { value: new THREE.Vector4(0.05, 2.2, 0, 0) } }, LOOK_U());
      // ---- the skeleton: our own matrices go straight into its texture (three's per-bone update is switched off)
      const bones = []; for (let i = 0; i < nb; i++) bones.push(new THREE.Bone());
      const skel = new THREE.Skeleton(bones, R.binv.map(m => m.clone())); skel.computeBoneTexture(); skel.update = () => {};
      const ident = new M4();
      const body = new THREE.SkinnedMesh(pack.geo, bodyMat(U, pack.tex)); body.bindMode = THREE.DetachedBindMode; body.bind(skel, ident);
      body.frustumCulled = false; body.castShadow = false; body.renderOrder = 30;
      const hull = new THREE.SkinnedMesh(pack.hgeo, inkMat(U)); hull.castShadow = true; hull.customDepthMaterial = depthMat(U); hull.bindMode = THREE.DetachedBindMode; hull.bind(skel, ident); hull.frustumCulled = false; hull.renderOrder = 29;
      const FU = { fM: { value: [new M4(), new M4(), new M4(), new M4()] }, fEA: { value: [new THREE.Vector4(), new THREE.Vector4()] }, fEB: { value: [new THREE.Vector4(), new THREE.Vector4()] },
        fEC: { value: [new THREE.Vector4(0, 0, -1, 0), new THREE.Vector4(0, 0, 1, 0)] }, fSkin: { value: new THREE.Color(0xEE6CC9).convertSRGBToLinear() }, fBrow: { value: new THREE.Color(0xF58AD6).convertSRGBToLinear() },
        fInk: { value: new THREE.Color(INK_C).convertSRGBToLinear() }, fT: { value: new THREE.Vector4() }, bClip: U.bClip };
      if (H.face.size) { EYE.w = H.face.size[0]; EYE.h = H.face.size[1]; EYE.d = H.face.size[2]; }   // (the eyes the pack was made for: the bell is pressed back under them)
      const face = new THREE.Mesh(pack.faceGeo || (pack.faceGeo = faceGeo()), faceMat(FU)); face.frustumCulled = false; face.renderOrder = 31;
      const fx = makeFX(), pt = makeParticles();
      model.add(hull, body, face, fx.mesh, pt.pts);
      B.stats.tris = (H.ni + (H.hni || H.ni) + face.geometry.index.count) / 3 + (ARC_N * 2 * (ARC_P - 1) * 2 + (GLOW_N + RING_N) * 2); B.stats.draws = 5;   // (+ the shadow pass)

      // ---- the pose: each bone's matrix (model space), then times its inverse bind into the skin's texture
      const Mb = []; for (let i = 0; i < nb; i++) Mb.push(new M4());
      const _v = new V3(), _v2 = new V3(), _v3 = new V3(), _v4 = new V3(), _q = new Q4(), _q2 = new Q4(), _q3 = new Q4(), _m = new M4(), _m2 = new M4(), _e = new THREE.Euler();
      const X = new V3(), Y = new V3(), Z = new V3(), _s = new V3();
      const AX_X = new V3(1, 0, 0), AX_Y = new V3(0, 1, 0), AX_Z = new V3(0, 0, 1);
      const setFrame = (m, x, y, z, p, sx, sy, sz) => { const e = m.elements; e[0] = x.x * sx; e[1] = x.y * sx; e[2] = x.z * sx; e[3] = 0; e[4] = y.x * sy; e[5] = y.y * sy; e[6] = y.z * sy; e[7] = 0;
        e[8] = z.x * sz; e[9] = z.y * sz; e[10] = z.z * sz; e[11] = 0; e[12] = p.x; e[13] = p.y; e[14] = p.z; e[15] = 1; return m; };
      // parallel transport: the last frame's z, laid square to the new direction y
      const transport = (zPrev, y, outZ) => { outZ.copy(zPrev).addScaledVector(y, -zPrev.dot(y)); if (outZ.lengthSq() < 1e-8) outZ.set(y.y, -y.x, 0).cross(y); return outZ.normalize(); };

      // ---- state
      const st = {
        t: 0, root: new V3(0, HOVER, 0), rootV: new V3(), rootA: new V3(), yaw: 0, yawV: 0, lean: 0, leanV: 0, roll: 0, rollV: 0,
        tilt: new V3(), tiltV: new V3(), sq: 1, sqV: 0, wob: [0, 0, 0, 0], wobV: [0, 0], wobAng: [0, 0], ph: Math.random(), c: 0, cLag: 0, cPrev: 0, rip: 0.4,
        gPos: new V3(), gVel: new V3(), gAcc: new V3(), gFirst: true, flash: 0, charge: 0, chargePh: 0,
        look: new V3(0, HOVER, 12), lookSet: false, lookW: new V3(), camM: new V3(0, 6, 20), camOK: false,
      };
      const mkArm = s => ({ s, W: new V3(), Wv: new V3(), H1: new V3(), H1v: new V3(), H2: new V3(), H2v: new V3(), Qh: new Q4(), init: false, ang: new Float32Array(4 * 3 * 3), angV: new Float32Array(4 * 3 * 3), tog: new Float32Array(4), togV: new Float32Array(4),
        pw: new Float32Array(5), pwOld: new Float32Array(5), pwNew: new Float32Array(5), pwT: -10, sq: 0, sqV: 0, cuff: new V3(), cuffV: new V3(), cs: 0, csV: 0, fc: new V3(), fcPrev: new V3(), fcV: new V3(), scale: 1, spark: 0, landed: false, lastY: 0,
        pts: new Array(25).fill(0).map(() => new V3()), cum: new Float32Array(25), J: new Array(7).fill(0).map(() => new V3()), handOverride: null, off: new V3(0, -1, 0), scl: GLOVE, landV: 0 });
      const arms = { L: mkArm('L'), R: mkArm('R') };
      const mkAT = () => ({ w: new V3(), t0: new V3(), t1: new V3(), l0: 1.5, l1: 1.4, k: 1, z: 0.55, hd: new V3(0, 0, 1), hp: new V3(0, -1, 0), hw: 0.8, pose: new Float32Array(5), scale: 1, spark: 0.45, wobK: 1, fcP: new V3(), fcK: 0 });
      const T = { off: new V3(), yaw: null, lean: 0, roll: 0, pulse: 1, pulseAmp: 1, squash: 1, slump: 0, flash: 0, charge: 0, clipY: -1e4, clipBand: 0, expr: 'angry', lookOv: null, arm: { L: mkAT(), R: mkAT() }, tentW: 1, tentG: 1, rootK: 1, eyeGlow: 0 };
      const tents = R.tent.map((c, k) => ({ c, x: new Float32Array((c.n + 1) * 3), xp: new Float32Array((c.n + 1) * 3), init: false, ph: k * 1.37 + 0.3, ph2: k * 2.11 + 1.1, dirA: k * 0.9 + 0.4, hPrev: 1 / 60, anc: new V3(), ancPrev: new V3(),
        stiff: Array.from({ length: c.n + 1 }, (_, j) => j === 0 ? 1 : (c.n > 4 ? (j <= 2 ? 0.22 : 0.05 * Math.pow(1 - (j - 2) / (c.n - 1), 1.5) + 0.006) : 0.08 * Math.pow(1 - (j - 1) / c.n, 1.3) + 0.01)) }));
      const E = {}; for (const k of EKEYS) E[k] = EXPR.angry[k];
      const face_ = { expr: 'angry', hold: 0, hold2: null, blink: 0, blinkT: 2, blinkDir: 0, pup: [0, 0, 0, 0], pupV: [0, 0, 0, 0], sac: [0, 0], sacT: 1 };
      let cur = null; // the move playing: { name, t, len, o, M, flags }

      // ---- the group's world matrix (and its inverse), the camera (from the last draw), everything in the model's own space
      const G = new M4(), Gi = new M4(), Gq = new Q4(), Gs = new V3(), Gp = new V3();
      let pxScale = 500;
      fx.mesh.onBeforeRender = (r, sc, cam) => { st.camM.setFromMatrixPosition(cam.matrixWorld).applyMatrix4(Gi); st.camOK = true;
        const h = r.getDrawingBufferSize ? r.getDrawingBufferSize(_v4).y : 800; pxScale = cam.projectionMatrix.elements[5] * h * 0.5; pt.U.ptPx.value = pxScale; };

      // ---------------------------------------------------------------- idle: the hover (written first every frame; a move writes over it)
      function idle(t) {
        T.off.set(0.05 * wn(t, 0.31, 0.53, 0.89), 0.1 * wn(t, 0.41, 0.23, 0.71), 0.05 * wn(t, 0.27, 0.61, 0.37)); T.yaw = null; T.lean = 0.04 * wn(t, 0.35, 0.57, 0.91); T.roll = 0.035 * wn(t, 0.29, 0.47, 0.83);
        T.pulse = 1; T.pulseAmp = 1; T.squash = 1; T.slump = 0; T.flash = 0; T.charge = 0; T.expr = 'angry'; T.lookOv = null; T.tentW = 1; T.tentG = 1; T.rootK = 1; T.eyeGlow = 0; T.clipY = -1e4; T.clipBand = 0;
        for (const s of SIDES) {
          const a = T.arm[s], g = s === 'L' ? 1 : -1, ph = g > 0 ? 0 : 2.1;
          // (as in the picture: each arm rises up and out from the bell's side in a high arch, then comes down to its cuff; the fists held
          // out wide at mid height, knuckles to the front)
          a.w.set(g * (3.45 + 0.16 * wn(t + ph, 0.37, 0.61, 0.23)), -1.45 + 0.18 * wn(t + ph, 0.43, 0.29, 0.67), 0.95 + 0.16 * wn(t + ph, 0.33, 0.51, 0.19));
          a.t0.set(g * 0.5, 0.86, 0.1).normalize(); a.t1.set(g * 0.06, -1, 0.1).normalize(); a.l0 = 2.3; a.l1 = 1.9; a.k = 1; a.z = 0.5;
          a.hd.set(g * 0.1, -0.42, 1).normalize(); a.hp.set(0, -1, -0.35).normalize(); a.hw = 0.9; a.scale = GLOVE; a.spark = 0.45; a.wobK = 1;
          // the fists flex now and then: a squeeze, a loosening
          const flex = clamp01(0.5 + 0.9 * wn(t * 0.7 + ph * 3, 0.9, 1.7, 2.3));
          a.pose.fill(0); a.pose[2] = 1 - 0.3 * flex; a.pose[1] = 0.3 * flex;
        }
      }
      // the arms' targets are written in the boss's own frame (x its left, y up, z its front, from the root); toModel turns them into
      // the model's space for the physics (by where the root is and which way it faces). A move can ask for a fist's middle at a point
      // instead (fcP, model space, with a weight fcK): the wrist is worked out from the hand's asked-for turn (the fist sits along the
      // knuckles' direction from the wrist).
      const yawQ = new Q4(), yawQi = new Q4(), rootQ = new Q4(), bellQ = new Q4(), Mbell = new M4();
      const palmL = {}; for (const s of SIDES) palmL[s] = new V3().fromArray(H.arms[s].palm).applyMatrix4(R.binv[R.arm[s].hand]);
      function handQ(a, out) { _v.copy(a.hd).normalize(); _v2.copy(a.hp).addScaledVector(_v, -a.hp.dot(_v)); if (_v2.lengthSq() < 1e-8) _v2.set(0, -1, 0).addScaledVector(_v, _v.y); _v2.normalize(); _v3.crossVectors(_v, _v2); return quatFromAxes(_v3, _v, _v2, out); }
      function toModel() {
        for (const s of SIDES) { const a = T.arm[s];
          a.w.applyQuaternion(yawQ).add(st.root); a.t0.applyQuaternion(yawQ); a.t1.applyQuaternion(yawQ); a.hd.applyQuaternion(yawQ); a.hp.applyQuaternion(yawQ);
          if (a.fcK > 0) { handQ(a, _q3); _v4.copy(palmL[s]).multiplyScalar(arms[s].scl || a.scale).applyQuaternion(_q3); _v.copy(a.fcP).sub(_v4); a.w.lerp(_v, Math.min(1, a.fcK)); a.fcK = 0; } }
      }
      // the floor under a point (model space): none over the pool (its hole), so the boss can rise out of it and sink into it
      const POOL_R = opts.poolR === undefined ? 4.0 : opts.poolR, POOL_Y = opts.poolY === undefined ? -0.14 : opts.poolY;
      const floorAt = (x, z) => x * x + z * z < POOL_R * POOL_R ? POOL_Y - 50 : FLOOR;

      // ---------------------------------------------------------------- physics: one small step
      const spr = (x, v, target, w, z, h) => v + (w * w * (target - x) - 2 * z * w * v) * h;   // (the new velocity)
      function springV(p, v, tgt, w, z, h, ax, ay, az) {
        v.x += (w * w * (tgt.x - p.x) - 2 * z * w * v.x - ax) * h; v.y += (w * w * (tgt.y - p.y) - 2 * z * w * v.y - ay) * h; v.z += (w * w * (tgt.z - p.z) - 2 * z * w * v.z - az) * h;
        p.addScaledVector(v, h);
      }
      const S_ = { L: new V3(), R: new V3() }, H1t = new V3(), H2t = new V3();
      function bellFrame() {
        _e.set(st.lean, st.yaw, st.roll, 'YXZ'); rootQ.setFromEuler(_e);
        _e.set(st.lean + st.tilt.x * 0.55, st.yaw, st.roll + st.tilt.z * 0.55, 'YXZ'); bellQ.setFromEuler(_e);
        Mbell.compose(st.root, bellQ, _s.set(1, 1, 1));
      }
      function step(h) {
        // the root: springs to where the move wants it; each beat of the pulse pushes it up a little (it swims)
        _v.copy(T.off).applyQuaternion(yawQ); _v.y += HOVER;
        const rw = 5.2 * T.rootK, rz = 0.8;
        const ax = st.gAcc.x * 0.25, ay = st.gAcc.y * 0.25, az = st.gAcc.z * 0.25;
        const v0x = st.rootV.x, v0y = st.rootV.y, v0z = st.rootV.z;
        springV(st.root, st.rootV, _v, rw, rz, h, 0, 0, 0);
        st.rootA.set((st.rootV.x - v0x) / h + ax, (st.rootV.y - v0y) / h + ay, (st.rootV.z - v0z) / h + az);
        // which way it faces: a slow turn toward the look target (or the move's own heading)
        let ty = T.yaw; if (ty === null) ty = Math.atan2(st.look.x - st.root.x, st.look.z - st.root.z);
        let dy = ty - st.yaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy));
        st.yawV += (2.6 * 2.6 * dy - 2 * 0.9 * 2.6 * st.yawV) * h; st.yaw += st.yawV * h;
        st.leanV = spr(st.lean, st.leanV, T.lean, 6.5, 0.7, h); st.lean += st.leanV * h;
        st.rollV = spr(st.roll, st.rollV, T.roll, 6.5, 0.7, h); st.roll += st.rollV * h;
        // the jelly: the bell tips against its acceleration and wobbles back; squash and two ring modes ring down
        _v2.copy(st.rootA); _q.copy(yawQ).invert(); _v2.applyQuaternion(_q);
        st.tiltV.x += (-49 * st.tilt.x - 2 * 0.32 * 7 * st.tiltV.x - _v2.z * 0.035) * h; st.tiltV.z += (-49 * st.tilt.z - 2 * 0.32 * 7 * st.tiltV.z + _v2.x * 0.035) * h;
        st.tilt.x += st.tiltV.x * h; st.tilt.z += st.tiltV.z * h; st.tilt.x = Math.max(-0.5, Math.min(0.5, st.tilt.x)); st.tilt.z = Math.max(-0.5, Math.min(0.5, st.tilt.z));
        st.sqV = spr(st.sq, st.sqV, T.squash, 9, 0.28, h) - _v2.y * 0.004 * h;
        if (st.sq < 0.86) st.sqV += (0.86 - st.sq) * 420 * h; else if (st.sq > 1.2) st.sqV -= (st.sq - 1.2) * 420 * h;   // (stiffer toward its limits: jelly, not a pancake)
        st.sq = Math.max(0.72, Math.min(1.32, st.sq + st.sqV * h));
        for (let k = 0; k < 2; k++) { const w = k ? 15 : 11; st.wobV[k] += (-w * w * st.wob[k * 2] - 2 * 0.12 * w * st.wobV[k]) * h; st.wob[k * 2] += st.wobV[k] * h; }
        bellFrame();
        // the arms: the wrist springs to its target (lagging, overshooting, dragged by the group's own motion), each handle a little looser
        for (const s of SIDES) {
          const a = T.arm[s], A = arms[s], RA = R.arm[s], S0 = S_[s];
          defJS(U, RA.J[0], S0); S0.applyMatrix4(Mbell);
          if (!A.init) { A.W.copy(a.w); A.H1.copy(S0).addScaledVector(a.t0, a.l0); A.H2.copy(a.w).addScaledVector(a.t1, -a.l1); A.init = true; }
          const w = 2 * Math.PI * 1.15 * a.k, z = a.z;
          const vy0 = A.Wv.y;
          springV(A.W, A.Wv, a.w, w, z, h, ax, ay, az);
          // the floor: the fist (not the wrist) stops on it, and says so if it came down hard
          const minY = floorAt(A.W.x + A.off.x, A.W.z + A.off.z) + FIST_R * A.scl - A.off.y;
          if (A.W.y < minY) { if (A.Wv.y < -3 && !A.landed) { A.landed = true; A.landV = -A.Wv.y; } A.W.y = minY; if (A.Wv.y < 0) A.Wv.y = 0; A.Wv.x *= 0.86; A.Wv.z *= 0.86; }
          H1t.copy(S0).addScaledVector(a.t0, a.l0); H2t.copy(A.W).addScaledVector(a.t1, -a.l1);
          springV(A.H1, A.H1v, H1t, w * 0.85, 0.62, h, ax, ay, az); springV(A.H2, A.H2v, H2t, w * 0.9, 0.58, h, ax, ay, az);
          // the fingers: each eases toward the pose a moment after the last (the index first, the pinky last; closing, the thumb comes
          // over last, onto the curled fingers), then each joint springs onto it, the tips a touch quicker than the knuckles
          const closing = A.pwT[2] + A.pwT[3] > A.pwD[2] + A.pwD[3] + 0.02;
          for (let d = 0; d < 4; d++) {
            const tau = d === 0 ? (closing ? 0.12 : 0.04) : TAU_D[d], k1 = 1 - Math.exp(-h / tau), base = d * 5;
            for (let p = 0; p < 5; p++) A.pwD[base + p] += (A.pwT[p] - A.pwD[base + p]) * k1;
          }
          for (let d = 0; d < 4; d++) for (let j = 0; j < 3; j++) for (let c = 0; c < 3; c++) {
            const i = (d * 3 + j) * 3 + c; let tg = 0; for (let p = 0; p < 5; p++) { const wgt = A.pwD[d * 5 + p]; if (wgt > 1e-4) tg += wgt * POSE_TAB[p][(d * 3 + j) * 4 + c]; }
            A.angV[i] = spr(A.ang[i], A.angV[i], tg, JW[j], 0.5, h); A.ang[i] += A.angV[i] * h;
          }
          for (let d = 0; d < 4; d++) { let tg = 0; for (let p = 0; p < 5; p++) tg += A.pwD[d * 5 + p] * POSE_TAB[p][(d * 3) * 4 + 3]; A.togV[d] = spr(A.tog[d], A.togV[d], tg, 24, 0.55, h); A.tog[d] += A.togV[d] * h; }
          // the fist's squash on a landing, the cuff's jiggle (it swings against the fist's acceleration)
          A.sqV = spr(A.sq, A.sqV, 0, 22, 0.3, h); A.sq += A.sqV * h;
          A.cuffV.x += (-18 * 18 * A.cuff.x - 2 * 0.18 * 18 * A.cuffV.x - A.fcA.z * 0.012) * h; A.cuffV.z += (-18 * 18 * A.cuff.z - 2 * 0.18 * 18 * A.cuffV.z + A.fcA.x * 0.012) * h;
          A.cuff.x += A.cuffV.x * h; A.cuff.z += A.cuffV.z * h; A.cuff.clampScalar(-0.35, 0.35);
          A.csV = spr(A.cs, A.csV, 0, 24, 0.22, h); A.cs += A.csV * h;
        }
      }
      // the hand poses as a table: [pose][(digit * 3 + joint) * 4 + (flex, spread, twist, close-up)]
      const POSE_TAB = POSE_NAMES.map(() => new Float32Array(48)), TAU_D = [0, 0.03, 0.05, 0.075], JW = [19, 23, 28];
      function fillPoses() { const o = [0, 0, 0, 0]; POSE_NAMES.forEach((p, k) => { const t = POSE_TAB[k]; DIG_ORDER.forEach((d, di) => { for (let j = 0; j < 3; j++) { poseAngles(p, d, j, o); for (let c = 0; c < 4; c++) t[(di * 3 + j) * 4 + c] = o[c]; } }); }); }
      fillPoses();
      for (const s of SIDES) { arms[s].pwD = new Float32Array(20); arms[s].pwT = new Float32Array(5); arms[s].fcA = new V3(); for (let d = 0; d < 4; d++) arms[s].pwD[d * 5 + 2] = 1; arms[s].pwT[2] = 1; }

      // ---------------------------------------------------------------- the pose: every bone's matrix from the state
      const qX = new Q4(), qY = new Q4(), qZ = new Q4(), qF = new Q4(), qT = new Q4(), mBasis = new M4(), restZ0 = {};
      for (const s of SIDES) restZ0[s] = new V3(0, 0, 1).applyQuaternion(R.rq[R.arm[s].ids[0]]);
      const quatFromAxes = (x, y, z, out) => { const e = mBasis.elements; e[0] = x.x; e[1] = x.y; e[2] = x.z; e[4] = y.x; e[5] = y.y; e[6] = y.z; e[8] = z.x; e[9] = z.y; e[10] = z.z; return out.setFromRotationMatrix(mBasis); };
      function pose(dt) {
        Mb[0].compose(st.root, rootQ, _s.set(1, 1, 1)); Mb[1].copy(Mbell);
        for (const s of SIDES) {
          const a = T.arm[s], A = arms[s], RA = R.arm[s], S0 = S_[s];
          // the arm: a cubic from the shoulder through the two handles to the wrist, cut into six even bones; each stretches (and thins)
          const pts = A.pts, cum = A.cum; cum[0] = 0;
          for (let i = 0; i <= 24; i++) { bez(S0, A.H1, A.H2, A.W, i / 24, pts[i]); if (i) cum[i] = cum[i - 1] + pts[i].distanceTo(pts[i - 1]); }
          for (let k = 0; k <= 6; k++) at(pts, cum, k / 6, A.J[k]);
          Z.copy(restZ0[s]).applyQuaternion(bellQ);
          for (let k = 0; k < 6; k++) {
            Y.subVectors(A.J[k + 1], A.J[k]); const L = Y.length(); Y.divideScalar(Math.max(L, 1e-6));
            transport(Z, Y, Z); X.crossVectors(Y, Z);
            const sy = L / R.len[RA.ids[k]], th = Math.max(0.8, Math.min(1.12, Math.pow(Math.max(0.3, sy), -0.3)));   // (stretched, it thins a little: jelly keeps some of its volume)
            setFrame(Mb[RA.ids[k]], X, Y, Z, A.J[k], th, sy, th);
          }
          // the hand: following the arm's end, turned toward the move's own heading for the fist; squashed on a landing
          quatFromAxes(X, Y, Z, qF); qF.multiply(RA.qRel);
          _v.copy(a.hd).normalize(); _v2.copy(a.hp).addScaledVector(_v, -a.hp.dot(_v)).normalize(); _v3.crossVectors(_v, _v2);
          quatFromAxes(_v3, _v, _v2, qT); qF.slerp(qT, a.hw);
          if (A.handOverrideQ) qF.copy(A.handOverrideQ);
          A.Qh.slerp(qF, 1 - Math.exp(-dt * 18));
          A.scl += (a.scale - A.scl) * (1 - Math.exp(-dt * 7));
          const sc = A.scl * (1 + 0.04 * A.cs), sq = A.sq;
          Mb[RA.hand].compose(A.W, A.Qh, _s.set(sc * (1 + 0.5 * sq), sc * (1 - sq), sc * (1 + 0.5 * sq)));
          // the digits: each joint bent from its rest place (spread about the palm's normal, then the curl, then a twist)
          for (let d = 0; d < 4; d++) {
            const ids = RA.dig[DIG_ORDER[d]], stt = d === 0 ? Math.max(0.8, 1 + A.tog[0]) : 1; let parent = Mb[RA.hand];
            for (let j = 0; j < 3; j++) {
              // (the left hand's bone frames are the mirror of the right's, so its spread and twist turn the other way)
              const i = (d * 3 + j) * 3, mir = -RA.sgn; let spread = A.ang[i + 1] * mir; if (j === 0) spread += A.tog[d] * RA.tog[DIG_ORDER[d]];
              qZ.setFromAxisAngle(AX_Z, spread); qX.setFromAxisAngle(AX_X, A.ang[i]); qY.setFromAxisAngle(AX_Y, A.ang[i + 2] * mir);
              _q.copy(qZ).multiply(qX).multiply(qY); _m.makeRotationFromQuaternion(_q);
              _m2.copy(R.loc[ids[j]]); if (j > 0 && stt !== 1) { const e = _m2.elements; e[12] *= stt; e[13] *= stt; e[14] *= stt; }   // (a stretched thumb puts its next joint further out)
              Mb[ids[j]].multiplyMatrices(parent, _m2).multiply(_m); parent = Mb[ids[j]];
            }
            if (stt !== 1) for (let j = 0; j < 3; j++) Mb[ids[j]].scale(_s.set(1, stt, 1));
          }
          // the cuff rides on the hand, with a jiggle of its own
          _e.set(A.cuff.x, 0, A.cuff.z); _q.setFromEuler(_e); _m.compose(_v.set(0, 0, 0), _q, _s.set(1 + 0.06 * A.cs, 1 - 0.04 * A.cs, 1 + 0.06 * A.cs));
          Mb[RA.cuff].multiplyMatrices(Mb[RA.hand], R.loc[RA.cuff]).multiply(_m);
          // the fist's middle (model space) and how it's moving (for the cuff, the sparks and the fight)
          A.fcPrev.copy(A.fc); _v.fromArray(H.arms[s].palm).applyMatrix4(R.binv[RA.hand]).applyMatrix4(Mb[RA.hand]); A.fc.copy(_v);
          const v2 = _v2.copy(A.fc).sub(A.fcPrev).divideScalar(Math.max(dt, 1e-3)); A.fcA.copy(v2).sub(A.fcV).divideScalar(Math.max(dt, 1e-3)).clampLength(0, 300); A.fcV.copy(v2);
          A.off.copy(A.fc).sub(A.W); A.scale = sc;
        }
      }
      // ---------------------------------------------------------------- the tentacles: chains of points in the water (world space)
      // Each point keeps its distance from the one above (the root rides on the bell); it is pulled back toward the tentacle's own shape a
      // little (stiff near the bell, loose at the tip), sinks slowly, is slowed by the water, and a wave of its own travels down it (its
      // own speed and phase, two directions at once, never in step with the others). Moving the boss drags them behind it.
      const GV = 1.6, DRAG = 2.2;
      function tentacles(dt) {
        const n = Math.max(1, Math.ceil(dt * 120)), h = dt / n, sc = Gs.x, t = st.t;
        for (const tn of tents) {
          const c = tn.c, x = tn.x, xp = tn.xp, N = c.n;
          tn.ancPrev.copy(tn.anc); defJS(U, c.J[0], tn.anc); tn.anc.applyMatrix4(Mbell).applyMatrix4(G);
          if (!tn.init) { tn.ancPrev.copy(tn.anc); for (let j = 0; j <= N; j++) { _v.copy(c.J[j]).applyMatrix4(Mbell).applyMatrix4(G); x[j * 3] = xp[j * 3] = _v.x; x[j * 3 + 1] = xp[j * 3 + 1] = _v.y; x[j * 3 + 2] = xp[j * 3 + 2] = _v.z; } tn.init = true; }
          _q.copy(Gq).multiply(bellQ);
          const ratio = h / tn.hPrev; tn.hPrev = h;
          for (let k = 0; k < n; k++) {
            const u = (k + 1) / n; _v.copy(tn.ancPrev).lerp(tn.anc, u); x[0] = _v.x; x[1] = _v.y; x[2] = _v.z;
            const damp = Math.exp(-DRAG * h) * (k === 0 ? ratio : 1), tt = t - dt + h * (k + 1);
            for (let j = 1; j <= N; j++) {
              const o = j * 3, f = j / N, amp = 2.4 * sc * T.tentW * Math.pow(f, 1.1);
              const w1 = Math.sin(tt * (1.15 + 0.13 * tn.c.k) - j * 0.95 + tn.ph), w2 = Math.sin(tt * (0.83 + 0.11 * tn.c.k) - j * 0.7 + tn.ph2);
              const ca = Math.cos(tn.dirA + 0.4 * Math.sin(tt * 0.21 + tn.ph)), sa = Math.sin(tn.dirA + 0.4 * Math.sin(tt * 0.21 + tn.ph));
              const fxw = amp * (w1 * ca - 0.7 * w2 * sa), fzw = amp * (w1 * sa + 0.7 * w2 * ca);
              const vx = (x[o] - xp[o]) * damp, vy = (x[o + 1] - xp[o + 1]) * damp, vz = (x[o + 2] - xp[o + 2]) * damp;
              xp[o] = x[o]; xp[o + 1] = x[o + 1]; xp[o + 2] = x[o + 2];
              x[o] += vx + fxw * h * h; x[o + 1] += vy - GV * sc * T.tentG * h * h; x[o + 2] += vz + fzw * h * h;
              // back toward its own shape, hanging from the point above
              _v.subVectors(c.J[j], c.J[j - 1]).applyQuaternion(_q).multiplyScalar(sc);
              const ks = tn.stiff[j] * (T.tentW < 0.5 ? 0.4 : 1);
              x[o] += (x[o - 3] + _v.x - x[o]) * ks; x[o + 1] += (x[o - 2] + _v.y - x[o + 1]) * ks; x[o + 2] += (x[o - 1] + _v.z - x[o + 2]) * ks;
            }
            // each link its own length (follow the leader), then the floor
            for (let j = 1; j <= N; j++) {
              const o = j * 3; let dx = x[o] - x[o - 3], dy = x[o + 1] - x[o - 2], dz = x[o + 2] - x[o - 1]; const d = Math.hypot(dx, dy, dz) || 1e-6, L = c.L[j - 1] * sc, k2 = L / d;
              const nx = x[o - 3] + dx * k2, ny = x[o - 2] + dy * k2, nz = x[o - 1] + dz * k2;
              xp[o] += (nx - x[o]) * 0.85; xp[o + 1] += (ny - x[o + 1]) * 0.85; xp[o + 2] += (nz - x[o + 2]) * 0.85;
              x[o] = nx; x[o + 1] = ny; x[o + 2] = nz;
              _v4.set(x[o], x[o + 1], x[o + 2]).applyMatrix4(Gi); const fy = Gp.y + (floorAt(_v4.x, _v4.z) + 0.1) * sc;
              if (x[o + 1] < fy) { x[o + 1] = fy; xp[o + 1] = fy; xp[o] += (x[o] - xp[o]) * 0.25; xp[o + 2] += (x[o + 2] - xp[o + 2]) * 0.25; }
            }
          }
          // the bones, in the model's space: each from its point to the next, its twist carried down from the root's
          Z.set(0, 0, 1).applyQuaternion(R.rq[c.ids[0]]).applyQuaternion(bellQ);
          for (let j = 0; j < N; j++) {
            _v.set(x[j * 3], x[j * 3 + 1], x[j * 3 + 2]).applyMatrix4(Gi); _v2.set(x[j * 3 + 3], x[j * 3 + 4], x[j * 3 + 5]).applyMatrix4(Gi);
            Y.subVectors(_v2, _v); const L = Y.length(); Y.divideScalar(Math.max(L, 1e-6)); transport(Z, Y, Z); X.crossVectors(Y, Z);
            setFrame(Mb[c.ids[j]], X, Y, Z, _v, 1, L / c.L[j], 1);
          }
        }
      }
      // a shove for every tentacle point (a hit, a sudden stop): dv in world units per second
      function tentKick(dvx, dvy, dvz, rnd) {
        for (const tn of tents) { const N = tn.c.n; for (let j = 1; j <= N; j++) { const o = j * 3, f = j / N, h = 1 / 120, r = rnd ? (Math.random() - 0.5) * rnd : 0;
          tn.xp[o] -= (dvx + r) * f * h; tn.xp[o + 1] -= dvy * f * h; tn.xp[o + 2] -= (dvz - r) * f * h; } }
      }
      // ---------------------------------------------------------------- into the skin
      function writeSkin() {
        const bm = skel.boneMatrices;
        for (let i = 0; i < nb; i++) { _m.multiplyMatrices(Mb[i], R.binv[i]); const e = _m.elements, o = i * 16; for (let k = 0; k < 16; k++) bm[o + k] = e[k]; }
        if (skel.boneTexture) skel.boneTexture.needsUpdate = true;
      }

      // ---------------------------------------------------------------- once a frame: the pulse, the jelly's uniforms, the hands' targets
      // the pulse: a quick contraction (the top first, the rim a beat later), a slow flow back out; each beat lifts it a little
      function frameSetup(dt) {
        const t = st.t;
        st.ph = (st.ph + dt * 0.66 * T.pulse) % 1;
        const ph = st.ph, shape = ph < 0.3 ? eOut(ph / 0.3) : 1 - eIO((ph - 0.3) / 0.7), c = shape * 0.85 * T.pulseAmp, dc = (c - st.c) / dt;
        st.c = c; st.cLag += (c - st.cLag) * (1 - Math.exp(-dt / 0.15));
        st.rip += (0.3 + Math.min(2.2, Math.abs(dc) * 0.55) - st.rip) * (1 - Math.exp(-dt / 0.3));
        if (dc > 0) st.rootV.y += dc * 0.16 * dt * T.pulseAmp;
        st.slump = (st.slump || 0) + (T.slump - (st.slump || 0)) * (1 - Math.exp(-dt * 1.4));
        st.flash = Math.max(T.flash, st.flash * Math.exp(-dt * 7));
        st.charge += (T.charge - st.charge) * (1 - Math.exp(-dt * 5)); st.chargePh += dt * (5 + 9 * st.charge);
        U.bBell.value.w = t;
        U.bPulse.value.set(c, st.cLag, st.rip * (0.4 + 0.6 * T.pulseAmp), st.slump);
        U.bSquash.value.set(st.sq, -st.tilt.z * 0.9, st.tilt.x * 0.9, 0.04 * (1 - st.sq) * 0);
        U.bWob.value.set(st.wob[0], st.wobAng[0], st.wob[2], st.wobAng[1]);
        U.bTent.value.set(0.06 * T.tentW, 2.4, 0, 0);
        U.bFlash.value.set(1, 0.6, 0.92, st.flash);
        U.bGlow.value.set(GLOW * (0.75 + 0.1 * Math.sin(t * 1.3)), GLOW, st.charge, st.chargePh);
        U.bClip.value.set(T.clipY < -1e3 ? -1e4 : Gp.y + T.clipY * Gs.x, T.clipBand * Gs.x, 0, 0);   // (the pool's line, in world units)
        for (const s of SIDES) { const A = arms[s], a = T.arm[s]; let sum = 0;
          if (A.handOverride) { A.pwT.fill(0); A.pwT[POSE_NAMES.indexOf(A.handOverride)] = 1; }
          else { for (let p = 0; p < 5; p++) sum += Math.max(0, a.pose[p]); for (let p = 0; p < 5; p++) A.pwT[p] = sum > 1e-4 ? Math.max(0, a.pose[p]) / sum : (p === 2 ? 1 : 0); } }
      }
      // a knock to the jelly: k about 1 for a punch landing, 2 for a big hit
      function wobble(k, ang) {
        st.wobV[0] += 0.9 * k * (0.6 + 0.4 * Math.random()); st.wobAng[0] = ang === undefined ? Math.random() * 6.28 : ang;
        st.wobV[1] += 0.6 * k * (0.6 + 0.4 * Math.random()); st.wobAng[1] = Math.random() * 6.28;
        st.sqV -= 0.75 * Math.min(k, 2);
      }

      // ---------------------------------------------------------------- the face
      const eyeP = [new V3().fromArray(H.face.eyeL.p), new V3().fromArray(H.face.eyeR.p)], eyeQ = [new Q4(), new Q4()];
      for (let i = 0; i < 2; i++) { const n = new V3().fromArray((i ? H.face.eyeR : H.face.eyeL).n), x = new V3(0, 1, 0).cross(n).normalize(), y = n.clone().cross(x); quatFromAxes(x, y, n, eyeQ[i]); }
      const fT = new M4(), fR = new Q4();
      function faceUpdate(dt) {
        const fe = face_; fe.hold -= dt;
        const name = fe.hold > 0 && fe.hold2 ? fe.hold2 : T.expr, tg = EXPR[name] || EXPR.angry, k = 1 - Math.exp(-dt * 13);
        for (let i = 0; i < EKEYS.length; i++) { const key = EKEYS[i]; E[key] += (tg[key] - E[key]) * k; }
        const glow = Math.max(E.glow, T.eyeGlow);
        // blinks (now and then a double), none while shut, glowing or dizzy
        const canBlink = E.xx < 0.3 && glow < 0.4 && E.dz < 0.3;
        fe.blinkT -= dt;
        if (fe.blinkT <= 0) { if (canBlink && fe.blinkDir === 0) fe.blinkDir = 1; fe.blinkT = Math.random() < 0.18 ? 0.28 : 1.8 + Math.random() * 3.2; }
        if (fe.blinkDir > 0) { fe.blink += dt / 0.055; if (fe.blink >= 1) { fe.blink = 1; fe.blinkDir = -1; } } else if (fe.blinkDir < 0) { fe.blink -= dt / 0.1; if (fe.blink <= 0) { fe.blink = 0; fe.blinkDir = 0; } }
        const bk = eIO(fe.blink);
        // where the pupils look: the target in each eye's frame, a quick critically damped ease, and tiny darts now and then
        fe.sacT -= dt; if (fe.sacT <= 0) { fe.sacT = 0.4 + Math.random() * 1.6; fe.sac[0] = (Math.random() - 0.5) * 0.08; fe.sac[1] = (Math.random() - 0.5) * 0.05; }
        const lk = T.lookOv || st.look;
        for (let i = 0; i < 2; i++) {
          _q.copy(bellQ).multiply(eyeQ[i]); _v.copy(eyeP[i]).applyMatrix4(Mbell); _v2.copy(lk).sub(_v); _q2.copy(_q).invert(); _v2.applyQuaternion(_q2);
          const zz = Math.max(0.3, _v2.z), inner = (i ? 1 : -1) * 0.06;
          let px = Math.max(-0.5, Math.min(0.5, _v2.x / zz * 0.9 + E.gx)) + inner + fe.sac[0], py = Math.max(-0.42, Math.min(0.42, _v2.y / zz * 0.9)) - 0.06 + fe.sac[1];
          if (name === 'defeated') { py -= 0.25; } if (name === 'smug' || name === 'glare') px += (i ? 0 : 0) + 0.0;
          const w = 32; for (let c = 0; c < 2; c++) { const j = i * 2 + c, g = c ? py : px, x0 = fe.pup[j] - g, cc = fe.pupV[j] + w * x0, e = Math.exp(-w * dt); fe.pup[j] = g + (x0 + cc * dt) * e; fe.pupV[j] = (fe.pupV[j] - cc * w * dt) * e; }
          // the eye: on the bell (moving with its pulse and squash), turned with it
          defJS(U, eyeP[i], _v3); _v3.applyMatrix4(Mbell);
          FU.fM.value[i].compose(_v3, _q, _s.set(1, lerp(1, st.sq, 0.6), 1));
          const lid = lerp(E.lid, -0.2, bk), low = lerp(E.low, -0.25, bk);
          FU.fEA.value[i].set(lid, E.sl * (1 - bk), Math.min(low, lid - 0.02), E.lsl * (1 - bk));
          FU.fEB.value[i].set(fe.pup[i * 2], fe.pup[i * 2 + 1], E.pr * (1 - 0.25 * st.charge), glow);
          FU.fEC.value[i].set(E.xx, E.dz, i ? 1 : -1, 0);
          // the brow: along the top of the eye, riding the lid; tipped down toward the nose when cross
          const side = i ? -1 : 1, bl = Math.min(E.lid, 1.05) - 0.06 * bk, ang = (i ? -E.bR : E.bL);
          const bz = EYE.d * (Math.sqrt(Math.max(0, 1 - Math.min(1, bl * bl))) - 0.18) + 0.035;
          fR.setFromAxisAngle(AX_Z, ang); fT.compose(_v4.set(-side * 0.035, bl * EYE.h + 0.075 + E.bY, bz), fR, _s.set(1, 1, 1));
          FU.fM.value[2 + i].multiplyMatrices(FU.fM.value[i], fT);
        }
        FU.fT.value.x = st.t;
      }

      // ---------------------------------------------------------------- the lightning, glows and rings
      const ARC_HAND = 9, BOLT0 = 18, BOLT_N = 6, BURST0 = 24;
      const zap = { on: false, A: new V3(), B: new V3(), t: 0, life: 0 }, _a = new V3(), _b = new V3(), _c = new V3(), _d = new V3(), _hx = new V3(), _hy = new V3(), _hz = new V3(), _hc = new V3(), _u = new V3();
      // the arcs hug the glove's outline: the glove as an ellipsoid in its own frame (rounder and shorter as a fist, longer open), its
      // outline in the plane facing the camera found from its half-widths along each of the hand's axes
      function gloveShape(s, A) {
        const e = Mb[R.arm[s].hand].elements, sc = A.scl, f = clamp01(A.pwD[12] + A.pwD[13]);   // (how curled: the middle finger's fist and point weights)
        _hx.set(e[0], e[1], e[2]).normalize(); _hy.set(e[4], e[5], e[6]).normalize(); _hz.set(e[8], e[9], e[10]).normalize();
        _hc.copy(A.fc).addScaledVector(_hy, lerp(0.42, 0.12, f) * sc).addScaledVector(_hz, lerp(0.02, 0.14, f) * sc);
        return f;
      }
      const silR = (u, s, f) => { const rx = lerp(0.95, 0.66, f) * s, ry = lerp(1.0, 0.62, f) * s, rz = lerp(0.36, 0.56, f) * s, a = u.dot(_hx) * rx, b = u.dot(_hy) * ry, c = u.dot(_hz) * rz; return Math.sqrt(a * a + b * b + c * c); };
      function formRing(arc, s, k, n, cam) {
        // round the glove in the plane facing the camera: a jagged run along its outline (a share of the way round each, so together they
        // ring it), or now and then a spike forking straight out from the edge. Kept relative to the fist's middle, so it rides along.
        const A = arms[s], f = gloveShape(s, A), sc = A.scl;
        _d.subVectors(cam, _hc).normalize(); _a.crossVectors(_d, AX_Y); if (_a.lengthSq() < 1e-6) _a.set(1, 0, 0); _a.normalize(); _b.crossVectors(_a, _d);
        const p = arc.pts, spike = Math.random() < 0.2, a0 = (k + Math.random() * 0.6) / n * 6.283, span = 6.283 / n * (1.15 + Math.random() * 0.6);
        let rad = 0, jit = 0;
        for (let i = 0; i < ARC_P; i++) {
          const u = i / (ARC_P - 1); let th, rk;
          jit = jit * 0.45 + (Math.random() - 0.5) * 0.22;   // (a short random walk: crackle, not a regular zigzag)
          if (spike) { th = a0 + jit * 0.6; rk = 1.02 + u * 0.7; }
          else { th = a0 + span * u + jit * 0.25; rk = 1.1 + jit * 0.6; }
          _u.copy(_a).multiplyScalar(Math.cos(th)).addScaledVector(_b, Math.sin(th)); rad = silR(_u, sc, f) * rk;
          const dz = 0.25 * rad;
          p[i * 3] = _hc.x - A.fc.x + _u.x * rad + _d.x * dz; p[i * 3 + 1] = _hc.y - A.fc.y + _u.y * rad + _d.y * dz; p[i * 3 + 2] = _hc.z - A.fc.z + _u.z * rad + _d.z * dz;
        }
        arc.int = 0.6 + Math.random() * 0.4; arc.regen = 0.04 + Math.random() * 0.06; arc.w = spike ? 0.75 : 0.9 + Math.random() * 0.5;
      }
      function formBolt(arc, A, Bp, amp) {
        _c.subVectors(Bp, A); const L = _c.length(); _c.divideScalar(L || 1); _a.crossVectors(_c, AX_Y); if (_a.lengthSq() < 1e-6) _a.set(1, 0, 0); _a.normalize(); _b.crossVectors(_a, _c);
        const p = arc.pts; let ox = 0, oy = 0;
        for (let i = 0; i < ARC_P; i++) { const u = i / (ARC_P - 1), env = Math.sin(u * Math.PI);
          ox = ox * 0.35 + (Math.random() - 0.5) * 2 * amp * L; oy = oy * 0.35 + (Math.random() - 0.5) * 2 * amp * L;
          p[i * 3] = A.x + _c.x * L * u + (_a.x * ox + _b.x * oy) * env; p[i * 3 + 1] = A.y + _c.y * L * u + (_a.y * ox + _b.y * oy) * env; p[i * 3 + 2] = A.z + _c.z * L * u + (_a.z * ox + _b.z * oy) * env; }
        arc.int = 0.7 + Math.random() * 0.3; arc.regen = 0.04 + Math.random() * 0.03; arc.w = 1 + Math.random() * 0.4;
      }
      // a burst: n short arcs flying out from p (along the floor if flat), with a flash and (big) a ring
      function burst(p, n, len, flat, ring) {
        let made = 0;
        for (let k = BURST0; k < ARC_N && made < n; k++) { const arc = fx.arcs[k]; if (arc.on && arc.life > 0.12) continue;
          const th = Math.random() * 6.283, el = flat ? 0.05 + Math.random() * 0.35 : (Math.random() - 0.3) * 1.4;
          _d.set(Math.cos(th) * Math.cos(el), Math.sin(el), Math.sin(th) * Math.cos(el)); arc.A.copy(p); arc.B.copy(p).addScaledVector(_d, len * (0.6 + Math.random() * 0.7));
          formBolt(arc, arc.A, arc.B, 0.13); arc.on = true; arc.kind = 2; arc.life = 0.28 + Math.random() * 0.2; arc.t = 0; made++; }
        for (let k = 4; k < GLOW_N; k++) { const g = fx.glows[k]; if (!g.on || g.t > 0.15) { g.on = true; g.kind = 2; g.p.copy(p); g.size = len * 0.9; g.int = 1.4; g.life = 0.35; g.t = 0; break; } }
        if (ring) for (const r of fx.rings) if (!r.on) { r.on = true; r.p.set(p.x, FLOOR + 0.05, p.z); r.r1 = ring; r.t = 0; r.life = 0.55 + ring * 0.06; r.int = 1; break; }
      }
      function fxUpdate(dt) {
        const cam = st.camOK ? st.camM : _c.set(0, 6, 20);
        for (const s of SIDES) {
          const A = arms[s], a = T.arm[s], i0 = s === 'L' ? 0 : ARC_HAND, rr = 0.56 * A.scale;
          const want = Math.min(1.6, a.spark + st.charge * 0.6); A.spark += (want - A.spark) * (1 - Math.exp(-dt * 9));
          const nOn = A.spark < 0.03 ? 0 : Math.min(ARC_HAND, Math.round(2.5 + A.spark * 4.5)), nRing = Math.max(3, nOn - 1);
          for (let k = 0; k < ARC_HAND; k++) { const arc = fx.arcs[i0 + k]; arc.kind = 0; arc.hand = s === 'L' ? 0 : 1;
            if (k >= nOn) { arc.on = false; continue; }
            arc.regen -= dt; if (!arc.on || arc.regen <= 0) { formRing(arc, s, k % nRing, nRing, cam); arc.on = Math.random() < 0.7 + 0.3 * Math.min(1, A.spark); arc.regen = arc.on ? arc.regen : 0.02 + Math.random() * 0.04; } }
          const g = fx.glows[s === 'L' ? 0 : 1]; g.on = true; g.kind = 0; g.p.copy(A.fc); g.size = rr * (1.7 + 0.6 * A.spark); g.int = Math.min(1.2, 0.18 + 0.45 * A.spark) * (0.85 + 0.15 * Math.random());
        }
        // the zap's bolts
        zap.t += dt; const zOn = zap.on && zap.t < zap.life;
        for (let k = 0; k < BOLT_N; k++) { const arc = fx.arcs[BOLT0 + k]; arc.kind = 1;
          if (!zOn || k >= (zap.n || 3)) { arc.on = false; continue; }
          arc.regen -= dt; if (!arc.on || arc.regen <= 0) { formBolt(arc, zap.A, zap.B, zap.amp || 0.07); arc.on = true; } arc.int = (0.7 + Math.random() * 0.3) * (1 - sstep(zap.life * 0.7, zap.life, zap.t)); }
        if (zap.on && !zOn) zap.on = false;
        const ball = zap.ball > 0.02, gz = fx.glows[2]; gz.on = ball || (zOn && zap.hitOn); gz.kind = 0;
        if (gz.on) { gz.p.copy(ball ? zap.G : zap.A); gz.size = ball ? 0.45 + 1.35 * zap.ball : 1.3; gz.int = ball ? (0.35 + 1.05 * zap.ball) * (0.85 + 0.15 * Math.random()) : 1.2 * (1 - zap.t / zap.life); }
        const gz2 = fx.glows[3]; gz2.on = zOn && zap.hitOn; gz2.kind = 0; if (gz2.on) { gz2.p.copy(zap.B); gz2.size = 1.8; gz2.int = 1.3 * (1 - zap.t / zap.life); }
        for (let k = BURST0; k < ARC_N; k++) { const arc = fx.arcs[k]; if (!arc.on) continue; arc.t += dt; if (arc.t >= arc.life) { arc.on = false; continue; }
          arc.regen -= dt; if (arc.regen <= 0) formBolt(arc, arc.A, arc.B, 0.13); arc.int = 1 - arc.t / arc.life; }
        for (const g of fx.glows) if (g.on && g.kind === 2) { g.t += dt; g.int = 1.4 * (1 - g.t / g.life); if (g.t >= g.life) g.on = false; }
        for (const r of fx.rings) if (r.on) { r.t += dt; if (r.t >= r.life) r.on = false; }
        writeFX(cam);
      }
      function writeFX(cam) {
        const P = fx.pos, S2 = fx.aS, Tn = fx.aT;
        for (let k = 0; k < ARC_N; k++) {
          const arc = fx.arcs[k], on = arc.on, hand = arc.kind === 0, base = hand ? arms[arc.hand ? 'R' : 'L'].fc : null;
          const inten = on ? arc.int * (hand ? Math.min(1.5, 0.6 + arms[arc.hand ? "R" : "L"].spark * 0.7) : 1) : 0;
          for (let l = 0; l < 2; l++) { const b = (k * 2 + l) * ARC_P * 2;
            for (let i = 0; i < ARC_P; i++) {
              const p = arc.pts, i0 = Math.max(0, i - 1) * 3, i1 = Math.min(ARC_P - 1, i + 1) * 3;
              let px = p[i * 3], py = p[i * 3 + 1], pz = p[i * 3 + 2]; if (base) { px += base.x; py += base.y; pz += base.z; }
              const tx = p[i1] - p[i0], ty = p[i1 + 1] - p[i0 + 1], tz = p[i1 + 2] - p[i0 + 2], taper = Math.sin((i + 0.5) / ARC_P * Math.PI) * 0.7 + 0.3;
              for (let sd = 0; sd < 2; sd++) { const v = b + i * 2 + sd;
                P[v * 3] = px; P[v * 3 + 1] = py; P[v * 3 + 2] = pz; Tn[v * 3] = tx; Tn[v * 3 + 1] = ty; Tn[v * 3 + 2] = tz;
                S2[v * 4] = sd ? 1 : -1; S2[v * 4 + 1] = l; S2[v * 4 + 2] = on ? arc.w * taper * (l ? 1 : 1) : 0; S2[v * 4 + 3] = inten; }
            }
          }
        }
        let q = fx.nArcV;
        for (let k = 0; k < GLOW_N; k++) { const g = fx.glows[k]; q = fxQuad(q, g.p, 2, g.on ? g.size : 0, g.on ? g.int : 0); }
        for (let k = 0; k < RING_N; k++) { const r = fx.rings[k], u = r.on ? r.t / r.life : 1; q = fxQuad(q, r.p, 3, r.on ? r.r1 * eOut(Math.min(1, u * 1.15)) : 0, r.on ? r.int * (1 - u) * (1 - u) : 0); }
        fx.pA.needsUpdate = true; fx.sA.needsUpdate = true; fx.tA.needsUpdate = true;
      }
      // a glow (layer 2, facing the camera) or a ring on the floor (layer 3): four corners from vertex q on; returns the next free vertex
      function fxQuad(q, p, layer, size, inten) {
        const P = fx.pos, S2 = fx.aS, Tn = fx.aT;
        for (let c = 0; c < 4; c++) { const v = q + c, cx = c === 0 || c === 3 ? -1 : 1, cz = c < 2 ? -1 : 1;
          P[v * 3] = p.x; P[v * 3 + 1] = p.y; P[v * 3 + 2] = p.z; S2[v * 4] = cx; S2[v * 4 + 1] = layer; S2[v * 4 + 2] = cz; S2[v * 4 + 3] = inten; Tn[v * 3] = size; Tn[v * 3 + 1] = 0; Tn[v * 3 + 2] = 0; }
        return q + 4;
      }

      // ---------------------------------------------------------------- particles
      const C_BUB = new THREE.Color(0.7, 0.85, 1.0), C_SLIME = new THREE.Color(0.35, 1.0, 0.3), C_JELLY = new THREE.Color(0.95, 0.4, 0.85), C_SPARK = new THREE.Color(0.75, 0.4, 1.0), C_STAR = new THREE.Color(1.0, 0.92, 0.45);
      function spawn(type, p, vx, vy, vz, size, life, col) {
        const q = pt.P[pt.next]; pt.next = (pt.next + 1) % PT_N;
        q.on = true; q.type = type; q.p.copy(p); q.v.set(vx, vy, vz); q.size = size; q.life = life; q.t = 0; q.c.copy(col); q.g = type === 0 ? -0.6 : type === 3 ? -0.2 : 2.2; q.drag = type === 0 ? 1.2 : 0.8;
      }
      let bubT = 0, dripT = 0;
      function ptUpdate(dt) {
        // a few bubbles always drift up round it; drips fall from the tentacles now and then
        bubT -= dt; if (bubT <= 0 && st.root.y > -2) { bubT = 0.25 + Math.random() * 0.4; const a = Math.random() * 6.28, r = 1.2 + Math.random() * 2.8;
          _v.set(st.root.x + Math.cos(a) * r, st.root.y - 2.5 + Math.random() * 3, st.root.z + Math.sin(a) * r); spawn(0, _v, 0, 0.5 + Math.random() * 0.5, 0, 0.07 + Math.random() * 0.1, 3 + Math.random() * 2, C_BUB); }
        dripT -= dt; if (dripT <= 0 && st.root.y > -2) { dripT = 0.6 + Math.random() * 1.4; const tn = tents[(Math.random() * tents.length) | 0], N = tn.c.n;
          _v.set(tn.x[N * 3], tn.x[N * 3 + 1], tn.x[N * 3 + 2]).applyMatrix4(Gi); spawn(2, _v, 0, -0.2, 0, 0.09 + Math.random() * 0.06, 1.4, C_JELLY); }
        const P = pt.pos, A = pt.aP, Cc = pt.aC;
        for (let i = 0; i < PT_N; i++) {
          const q = pt.P[i];
          if (q.on) { q.t += dt; if (q.t >= q.life) q.on = false; else {
            q.v.y -= q.g * dt; const dk = Math.exp(-q.drag * dt); q.v.multiplyScalar(dk);
            if (q.type === 0) { q.v.x += Math.sin(st.t * 3 + q.wob) * 0.4 * dt; q.v.z += Math.cos(st.t * 2.6 + q.wob) * 0.4 * dt; }
            q.p.addScaledVector(q.v, dt); if (q.type !== 0 && q.type !== 3 && q.p.y < FLOOR + 0.03) { q.p.y = FLOOR + 0.03; q.v.set(0, 0, 0); } } }
          const u = q.t / q.life, fade = q.on ? Math.min(1, q.t * 8) * (1 - u * u) : 0;
          P[i * 3] = q.p.x; P[i * 3 + 1] = q.p.y; P[i * 3 + 2] = q.p.z;
          A[i * 4] = q.size * (q.type === 0 ? 1 + 0.4 * u : 1); A[i * 4 + 1] = fade; A[i * 4 + 2] = q.type; A[i * 4 + 3] = 0;
          Cc[i * 3] = q.c.r; Cc[i * 3 + 1] = q.c.g; Cc[i * 3 + 2] = q.c.b;
        }
        pt.pA.needsUpdate = true; pt.PA.needsUpdate = true; pt.CA.needsUpdate = true;
      }

      // ---------------------------------------------------------------- the moves
      // A move writes its targets over the hover's each frame (blending in at its start and back out at its end), fires each of its
      // events once, and lasts len seconds at speed 1 (opts.speed runs it faster). The springs underneath give every change its weight,
      // its overshoot and its settle, so one move can cut into another at any moment and the body still flows.
      const mv = { name: 'idle', t: 0, len: 0, sp: 1, o: {}, fired: 0, M: null, P: new V3(), C: new V3(), side: 'L', g: 1, a0: 0, a1: 0, ar: 0, dir: 1, hold: 3, yaw: 0, lunge: 0, dist: 0, dripT: 0 };
      const mA = new V3(), mB = new V3(), mC = new V3(), mE = new V3(), hitW = new V3();
      const evOf = extra => { const d = { move: mv.name }; if (extra) for (const k in extra) d[k] = extra[k]; return d; };
      function fire(bit, name, hand) { if (mv.fired & bit) return false; mv.fired |= bit; const d = { move: mv.name }; if (hand) d.hand = hand; emit(name, d); return true; }   // (the event's object is made only when it fires)
      const wIO = (t, L, a, b) => sstep(0, a, t) * (1 - sstep(L - b, L, t));
      // the floor point a move aims at (world x, z; the player when not given), in the model's space
      function aim(o, out) { if (o && typeof o.x === 'number' && typeof o.z === 'number') out.set(o.x, Gp.y, o.z).applyMatrix4(Gi); else out.copy(st.look); out.y = FLOOR; return out; }
      const yawTo = p => Math.atan2(p.x - st.root.x, p.z - st.root.z);
      const dlerp = (v, x, y, z, k) => { mE.set(x, y, z).normalize(); v.lerp(mE, k); if (v.lengthSq() < 1e-6) v.copy(mE); return v.normalize(); };
      // the writers: a wrist (the boss's frame), a fist's middle (the model's space), the hand's turn (knuckles along h, the palm facing p,
      // the boss's frame), the arm's curve (the tangents leaving the shoulder and arriving at the wrist, and their reach), the hand's pose,
      // the arm's spring (how fast and how bouncy), the root's offset
      function wrist(s, x, y, z, k) { const a = T.arm[s].w; a.x = lerp(a.x, x, k); a.y = lerp(a.y, y, k); a.z = lerp(a.z, z, k); }
      function fistAt(s, p, k) { if (k <= 0) return; const a = T.arm[s]; a.fcP.copy(p); a.fcK = k; }
      function turn(s, hx, hy, hz, px, py, pz, hw, k) { const a = T.arm[s]; dlerp(a.hd, hx, hy, hz, k); dlerp(a.hp, px, py, pz, k); a.hw = lerp(a.hw, hw, k); }
      function curve(s, ax, ay, az, bx, by, bz, l0, l1, k) { const a = T.arm[s]; dlerp(a.t0, ax, ay, az, k); dlerp(a.t1, bx, by, bz, k); a.l0 = lerp(a.l0, l0, k); a.l1 = lerp(a.l1, l1, k); }
      function grip(s, name, k) { const a = T.arm[s], j = POSE_NAMES.indexOf(name); for (let p = 0; p < 5; p++) a.pose[p] = lerp(a.pose[p], p === j ? 1 : 0, k); }
      function springy(s, kk, z, k) { const a = T.arm[s]; a.k = lerp(a.k, kk, k); a.z = lerp(a.z, z, k); }
      function off(x, y, z, k) { T.off.x = lerp(T.off.x, x, k); T.off.y = lerp(T.off.y, y, k); T.off.z = lerp(T.off.z, z, k); }
      const boss2m = (x, y, z, out) => out.set(x, y, z).applyQuaternion(yawQ).add(st.root);   // (a point in the boss's frame, in the model's space)
      const dirB = (v, out) => out.copy(v).applyQuaternion(yawQi);                              // (a model-space direction in the boss's frame)
      const FR = () => FIST_R * GLOVE;
      // a fist can only reach so far (its arm stretches to about two and a half times its length); past that it stops short, in the air
      function reach(s, p) {
        const S0 = S_[s], max = 2.5 * R.arm[s].restLen; mE.copy(p).sub(S0); const L = mE.length();
        if (L > max) p.copy(S0).addScaledVector(mE, max / L);
        p.y = Math.max(p.y, floorAt(p.x, p.z) + FR() * 0.9); return p;
      }
      // a fist lands: the sparks and the ring on the floor, the jolt through the jelly, the hit (in world units) for the fight
      function land(s, bit, ring, power, name) {
        if (mv.fired & bit) return; mv.fired |= bit;
        const A = arms[s]; A.landed = false;
        mC.copy(A.fc); mC.y = Math.max(floorAt(mC.x, mC.z) + 0.04, mC.y - FIST_R * A.scl * 0.9);
        burst(mC, 6, 1.25 + 0.35 * power, mC.y < FLOOR + 0.3, ring);
        wobble(0.8 * power, Math.atan2(A.fc.z - st.root.z, A.fc.x - st.root.x)); A.sqV -= 7 * power; A.spark = 1.9; tentKick(0, 2.4 * power, 0, 1.4 * power);
        for (let i = 0; i < 6; i++) spawn(3, mC, (Math.random() - 0.5) * 3, 1 + Math.random() * 2, (Math.random() - 0.5) * 3, 0.1 + Math.random() * 0.08, 0.5, C_SPARK);
        if (name) { hitW.copy(A.fc).applyMatrix4(G); emit(name, evOf({ hand: s, x: hitW.x, y: hitW.y, z: hitW.z, r: FIST_R * A.scl * Gs.x, ring: ring * Gs.x, power })); }
      }
      const evSweep = { move: 'sweep', hand: 'L', x: 0, y: 0, z: 0, r: 0 };   // (the one sweep event, reused every frame of the pass)
      const zapG = new V3(); zap.ball = 0; zap.G = zapG;
      const MOVES = {
        // ---- punch: wind-up (the arm draws back and up, the glove crackles), a fast straight strike to the floor, the impact, recovery
        punch: { len: 2.0,
          init(m) { aim(m.o, m.P); toBossP(m.P, mA); m.side = m.o.hand === 'L' || m.o.hand === 'R' ? m.o.hand : mA.x >= 0 ? 'L' : 'R'; m.g = m.side === 'L' ? 1 : -1;
            m.yaw = yawTo(m.P); m.dist = Math.hypot(m.P.x - st.root.x, m.P.z - st.root.z); m.lunge = Math.min(2.6, Math.max(0, m.dist - 4.4) * 0.62); },
          run(m, t) {
            const s = m.side, o = s === 'L' ? 'R' : 'L', g = m.g, w = wIO(t, 2.0, 0.15, 0.75);
            const kW = sstep(0, 0.42, t) * (1 - sstep(0.5, 0.57, t)), kS = sstep(0.5, 0.56, t), kH = sstep(0.62, 0.8, t);
            T.yaw = m.yaw + g * (0.34 * kW - 0.16 * kS * (1 - 0.6 * kH)) * w;
            off(-g * 0.35 * kW, 0.4 * kW - 0.5 * kS, -0.7 * kW + m.lunge * kS, w);
            T.lean = lerp(T.lean, -0.15 * kW + 0.26 * kS, w); T.roll = lerp(T.roll, g * (0.09 * kW - 0.07 * kS), w); T.squash = lerp(T.squash, 1 + 0.07 * kW - 0.06 * kS, w);
            wrist(s, g * 3.1, 0.95, -1.35, kW * w); curve(s, g * 0.6, 0.75, -0.3, g * 0.3, 0.45, -1, 1.5, 1.3, kW * w); turn(s, g * 0.35, 0.45, 1, 0, -1, 0.45, 0.95, kW * w);
            grip(s, 'fist', w); T.arm[s].spark = lerp(T.arm[s].spark, 1.35 - 0.45 * kH, w);
            if (kS > 0) {
              mB.copy(m.P); mB.y = FLOOR + FR() * 0.92; reach(s, mB); fistAt(s, mB, kS * w); springy(s, 2.9 - 1.5 * kH, 0.8 + 0.15 * kH, kS * w);
              mC.copy(mB).sub(S_[s]); dirB(mC, mC).normalize();
              turn(s, mC.x, mC.y, mC.z, 0, -1, -0.3, 1, kS * w); curve(s, mC.x + g * 0.3, mC.y + 0.2, mC.z, mC.x, mC.y, mC.z, 0.35 * m.dist, 0.3 * m.dist, kS * w);
            }
            wrist(o, -g * 2.3, -1.9 + 0.35 * kW, 1.5 - 1.9 * kS, w); grip(o, 'fist', w); turn(o, -g * 0.2, 0.1, 1, 0, -1, 0.2, 0.9, w);
            T.expr = kS > 0.5 ? (kH > 0.5 ? 'glare' : 'angry') : 'charging';
            fire(1, 'windup', s); if (t >= 0.5) fire(2, 'strike', s);
            if (!(m.fired & 4) && t > 0.5 && (arms[s].landed || arms[s].fc.distanceTo(mB) < 0.4 || t > 0.8)) land(s, 4, 3.0, 1, 'hit');
            if (t >= 1.15) fire(8, 'recover', s);
          } },
        // ---- double slam: both fists up high (the bell stretches, the eyes glow), then down onto the target together: a shockwave
        slam: { len: 2.7,
          init(m) { aim(m.o, m.P); m.yaw = yawTo(m.P); m.dist = Math.hypot(m.P.x - st.root.x, m.P.z - st.root.z); m.lunge = Math.min(2.4, Math.max(0, m.dist - 4.2) * 0.55); },
          run(m, t) {
            const w = wIO(t, 2.7, 0.2, 0.8), kW = sstep(0, 0.72, t) * (1 - sstep(0.85, 0.94, t)), kS = sstep(0.85, 0.92, t), kH = sstep(1.0, 1.2, t);
            T.yaw = m.yaw; off(0, 0.7 * kW - 1.0 * kS, -0.5 * kW + m.lunge * kS, w);
            T.lean = lerp(T.lean, -0.22 * kW + 0.3 * kS, w); T.squash = lerp(T.squash, 1 + 0.13 * kW - 0.12 * kS * (1 - kH), w);
            T.charge = lerp(T.charge, 0.85 * kW, w); T.eyeGlow = Math.max(T.eyeGlow, sstep(0.3, 0.7, t) * (1 - sstep(1.1, 1.5, t)) * w);
            for (const s of SIDES) {
              const g = s === 'L' ? 1 : -1;
              wrist(s, g * 1.05, 2.95, -0.35, kW * w); curve(s, g * 0.6, 1, 0, -g * 0.25, 1, 0.15, 1.3, 1.1, kW * w); turn(s, -g * 0.25, 1, 0.25, 0, 0.3, 1, 0.95, kW * w);
              grip(s, 'fist', w); T.arm[s].spark = lerp(T.arm[s].spark, 1.55 - 0.5 * kH, w);
              if (kS > 0) {
                mB.set(g * 0.62, 0, 0).applyQuaternion(yawQ).add(m.P); mB.y = FLOOR + FR() * 0.95; reach(s, mB); fistAt(s, mB, kS * w); springy(s, 2.7 - 1.4 * kH, 0.82 + 0.1 * kH, kS * w);
                turn(s, 0, -1, 0.55, -g, -0.3, 0, 1, kS * w); curve(s, g * 0.3, 0.6, 1, 0, -1, 0.5, 1.2, 0.9, kS * w);
              }
            }
            T.expr = t < 0.85 ? (t < 0.35 ? 'charging' : 'glow') : (kH > 0.5 ? 'glare' : 'angry');
            fire(1, 'windup'); if (t >= 0.85) fire(2, 'strike');
            if (!(m.fired & 4) && t > 0.86 && ((arms.L.landed && arms.R.landed) || t > 1.02)) {
              m.fired |= 4; land('L', 16, 0, 1.3, null); land('R', 32, 0, 1.3, null);
              mC.copy(arms.L.fc).add(arms.R.fc).multiplyScalar(0.5); mC.y = FLOOR; burst(mC, 4, 2.2, true, 5.6);
              wobble(1.8); st.flash = Math.max(st.flash, 0.35);
              hitW.copy(mC).applyMatrix4(G); emit('hit', evOf({ hand: 'both', x: hitW.x, y: hitW.y, z: hitW.z, r: 1.5 * Gs.x, ring: 5.6 * Gs.x, power: 2 }));
            }
            if (t >= 1.75) fire(8, 'recover');
          } },
        // ---- sweep: one arm reaches out to the side, then sweeps an arc low across the floor (an open glove, palm first) through the target
        sweep: { len: 2.5,
          init(m) { aim(m.o, m.P); toBossP(m.P, mA); m.side = m.o.hand === 'L' || m.o.hand === 'R' ? m.o.hand : mA.x >= 0 ? 'L' : 'R'; m.g = m.side === 'L' ? 1 : -1;
            m.C.copy(st.root); m.C.y = FLOOR; const ang = Math.atan2(m.P.x - m.C.x, m.P.z - m.C.z);
            m.dir = m.o.dir === 1 || m.o.dir === -1 ? m.o.dir : -m.g; m.ar = Math.max(POOL_R + 1.2, Math.min(8.5, Math.hypot(m.P.x - m.C.x, m.P.z - m.C.z)));
            m.a0 = ang - m.dir * 1.3; m.a1 = ang + m.dir * 1.3; m.yaw = ang; evSweep.hand = m.side; },
          run(m, t) {
            const s = m.side, o = s === 'L' ? 'R' : 'L', g = m.g, w = wIO(t, 2.5, 0.2, 0.8);
            const kW = sstep(0, 0.55, t), kS = sstep(0.55, 0.64, t), u = eIO(clamp01((t - 0.6) / 0.62)), kF = sstep(1.2, 1.55, t);
            const a = lerp(m.a0 - m.dir * 0.15 * (1 - kS), m.a1 + m.dir * 0.3 * kF, u), sn = Math.sin(a), cs = Math.cos(a);
            T.yaw = lerp(m.a0, m.a1, u) + m.dir * 0.35 * (1 - u) * kW;
            off(0, -0.55 * kW, 0.4 * kS * (1 - kF), w); T.lean = lerp(T.lean, 0.12 * kW, w); T.roll = lerp(T.roll, -m.dir * 0.12 * kS * (1 - kF), w);
            mB.set(m.C.x + sn * m.ar, FLOOR + FR() * 0.85 + (1.5 * (1 - kS) + 1.1 * kF), m.C.z + cs * m.ar); reach(s, mB); fistAt(s, mB, kW * w);
            springy(s, 1.9, 0.72, kW * w);
            mC.set(sn, -0.3, cs); dirB(mC, mC); mA.set(cs * m.dir, 0, -sn * m.dir); dirB(mA, mA);
            turn(s, mC.x, mC.y, mC.z, mA.x, mA.y, mA.z, 1, kW * w); curve(s, g * 0.8, 0.1, 0.4, mC.x, mC.y, mC.z, 1.6, 1.0, kW * w);
            grip(s, kS > 0.5 && kF < 0.5 ? 'spread' : 'open', w); T.arm[s].spark = lerp(T.arm[s].spark, 1.2, w);
            wrist(o, -g * 2.8, -1.4, -0.9 + 0.8 * kS, w); grip(o, 'fist', w);
            T.expr = kS > 0.5 ? 'angry' : 'charging';
            fire(1, 'windup', s); if (t >= 0.6) fire(2, 'strike', s);
            if (t >= 0.6 && t <= 1.22) {
              const A = arms[s]; hitW.copy(A.fc).applyMatrix4(G); evSweep.x = hitW.x; evSweep.y = hitW.y; evSweep.z = hitW.z; evSweep.r = FIST_R * 1.6 * A.scl * Gs.x; emit('sweep', evSweep);
              if (Math.random() < 0.5) { mA.copy(A.fc); mA.y = FLOOR + 0.1; spawn(3, mA, (Math.random() - 0.5) * 2, 0.6 + Math.random(), (Math.random() - 0.5) * 2, 0.09, 0.5, C_SPARK); }
            }
            if (t >= 1.25) fire(8, 'recover', s);
          } },
        // ---- zap: the fists come together in front, a ball of lightning grows between them (the eyes glow, the bell beats fast), then a bolt
        zap: { len: 2.9,
          init(m) { aim(m.o, m.P); m.yaw = yawTo(m.P); },
          run(m, t) {
            const w = wIO(t, 2.9, 0.2, 0.8), kC = sstep(0, 0.6, t), kF = sstep(1.25, 1.31, t), kR = sstep(1.4, 1.95, t);
            T.yaw = m.yaw; off(0, -0.2 * kC + 0.25 * kF * (1 - kR), -0.75 * kF * (1 - kR), w);
            T.lean = lerp(T.lean, 0.08 * kC - 0.22 * kF * (1 - kR), w);
            for (const s of SIDES) {
              const g = s === 'L' ? 1 : -1;
              wrist(s, g * (1.25 - 0.2 * kF), -2.5 + 0.15 * kC, 1.9 + 0.6 * kF * (1 - kR), w); curve(s, g * 0.7, -0.3, 0.8, -g * 0.5, 0.1, 1, 1.3, 1.0, w);
              turn(s, -g * 0.55, 0.05, 0.85, -g, 0, -0.2, 0.95, w * (1 - kF)); turn(s, -g * 0.1, 0.05, 1, 0, -0.2, 1, 1, w * kF);
              grip(s, kF > 0.5 ? 'spread' : 'relax', w); T.arm[s].spark = lerp(T.arm[s].spark, 1.6 * kC * (1 - kR) + 0.3, w);
            }
            T.charge = lerp(T.charge, kC * (1 - kR), w); T.pulse = lerp(T.pulse, 2.3, w * kC * (1 - kF)); T.pulseAmp = lerp(T.pulseAmp, 0.55, w * kC * (1 - kF));
            T.expr = t < 0.3 ? 'charging' : t < 1.95 ? 'glow' : 'angry';
            zapG.copy(arms.L.fc).add(arms.R.fc).multiplyScalar(0.5); zap.ball = kC * (1 - kF) * w;
            if (t < 1.25) { zap.A.copy(arms.L.fc); zap.B.copy(arms.R.fc); zap.on = kC > 0.3; zap.t = 0; zap.life = 9; zap.n = 2; zap.amp = 0.16; zap.hitOn = false; }
            fire(1, 'windup');
            if (t >= 1.25 && fire(2, 'strike')) {
              zap.on = true; zap.t = 0; zap.life = 0.62; zap.n = 5; zap.amp = 0.055; zap.hitOn = true; zap.A.copy(zapG); zap.B.copy(m.P); zap.B.y = FLOOR + 0.2;
              burst(zap.B, 7, 1.6, true, 2.8); wobble(1.1); st.sqV -= 1.2;
              hitW.copy(zap.B).applyMatrix4(G); emit('zap', evOf({ x: hitW.x, y: hitW.y, z: hitW.z, r: 1.1 * Gs.x })); emit('hit', evOf({ hand: 'zap', x: hitW.x, y: hitW.y, z: hitW.z, r: 1.1 * Gs.x, ring: 2.8 * Gs.x, power: 1.5 }));
            }
            if (zap.on && zap.hitOn) zap.A.copy(zapG);
            if (t >= 1.4) fire(8, 'recover');
          } },
        // ---- hurt: a flinch away from the hit, a flash, the jelly wobbling, "> <", the gloves flung open
        hurt: { len: 1.15,
          init(m) { aim(m.o, m.P); mA.copy(st.root).sub(m.P); mA.y = 0; if (mA.lengthSq() < 1e-6) mA.set(0, 0, -1); mA.normalize();
            st.rootV.addScaledVector(mA, 3.4); st.rootV.y += 1.5; wobble(1.9, Math.atan2(mA.z, mA.x)); st.sqV -= 1.2; st.flash = 1; tentKick(mA.x * 4, 2.2, mA.z * 4, 2.5);
            for (const s of SIDES) { arms[s].Wv.addScaledVector(mA, 3); arms[s].Wv.y += 4; } },
          run(m, t) {
            const w = wIO(t, 1.15, 0.04, 0.5), kO = 1 - sstep(0.3, 0.62, t);
            T.expr = t < 0.62 ? 'hurt' : 'angry';
            for (const s of SIDES) { const g = s === 'L' ? 1 : -1; wrist(s, g * 3.7, -1.5, 0.2, w * kO); grip(s, 'spread', w * kO); T.arm[s].spark = lerp(T.arm[s].spark, 0.08, w * kO); }
            T.lean = lerp(T.lean, -0.22 * kO, w); T.pulseAmp = lerp(T.pulseAmp, 0.3, w * kO);
          } },
        // ---- stunned: it sinks low, the gloves flop onto the floor round it (the opening), dizzy spirals; then it shakes it off and rises
        stunned: { len: 5.4,
          init(m) { m.hold = Math.max(0.6, m.o.time || 3); m.len = 0.9 + m.hold + 1.4; },
          run(m, t) {
            const L = m.len, w = wIO(t, L, 0.1, 0.9), kD = sstep(0, 0.85, t), kU = sstep(0.9 + m.hold, 0.9 + m.hold + 0.9, t), k = kD * (1 - kU);
            off(0, -(HOVER - 3.2) * k, 0.3 * k, w);
            for (const s of SIDES) {
              const g = s === 'L' ? 1 : -1;
              boss2m(g * 4.3, 0, 2.4, mB); const r = Math.hypot(mB.x, mB.z), rMin = POOL_R + 1.1; if (r < rMin) { mB.x *= rMin / Math.max(r, 1e-3); mB.z *= rMin / Math.max(r, 1e-3); }
              mB.y = FLOOR + FR() * 0.8; fistAt(s, mB, k * w); springy(s, 0.75, 0.5, k * w);
              turn(s, g * 0.35, -0.3, 1, 0, -1, 0, 0.9, k * w); grip(s, 'relax', k * w); T.arm[s].spark = lerp(T.arm[s].spark, 0.04, k * w);
            }
            T.slump = lerp(T.slump, 0.32, k * w); T.pulse = lerp(T.pulse, 0.35, k * w); T.pulseAmp = lerp(T.pulseAmp, 0.45, k * w);
            T.tentW = lerp(T.tentW, 0.3, k * w); T.tentG = lerp(T.tentG, 2.4, k * w);
            const sw = t - 0.9; T.roll += 0.1 * Math.sin(sw * 2.4) * k * w; T.lean += 0.08 * Math.cos(sw * 2.4) * k * w;
            const shake = kU > 0 && kU < 1 ? Math.sin((t - 0.9 - m.hold) * 26) * Math.sin(kU * Math.PI) : 0; T.yaw = st.yaw + 0.0; if (shake) { T.roll += 0.14 * shake; }
            T.expr = k > 0.35 ? 'dizzy' : kU > 0 ? 'angry' : 'surprised';
            if (k > 0.6 && Math.random() < 0.25) { mA.set(st.root.x + (Math.random() - 0.5) * 2.4, st.root.y + 1.5 + Math.random() * 0.4, st.root.z + (Math.random() - 0.5) * 2.4); spawn(3, mA, 0, 0.25, 0, 0.12 + Math.random() * 0.06, 0.7, C_STAR); }
            if (t >= 0.85) fire(1, 'stunStart'); if (t >= 0.9 + m.hold) fire(2, 'stunEnd');
          } },
        // ---- taunt: one glove wags a finger at the player ("no, no, no"), the other beckons (palm up, the fingers curling in twice), a
        // smug chuckle
        taunt: { len: 2.8,
          run(m, t) {
            const w = wIO(t, 2.8, 0.35, 0.6), env = sstep(0.4, 0.6, t) * (1 - sstep(2.0, 2.3, t)), wag = 0.5 * Math.sin((t - 0.45) * Math.PI * 2 * 2.1) * env;
            wrist('R', -2.25, -0.95, 1.75, w); turn('R', Math.sin(wag) * 0.9, Math.cos(wag), 0.15, 0, 0, 1, 1, w); grip('R', 'point', w); curve('R', -0.7, 0.4, 0.5, 0, 1, 0.2, 1.5, 1.1, w);
            wrist('L', 2.3, -2.0, 1.9, w); turn('L', -0.35, 0.2, 1, 0, 1, -0.2, 1, w); grip('L', 'open', w);
            const bk = env * (0.5 - 0.5 * Math.cos((t - 0.5) * Math.PI * 2 * 1.4)); grip('L', 'fist', w * bk * 0.85);
            off(0, 0.1 * Math.abs(Math.sin(t * 8.5)) * env, -0.15, w); T.squash = lerp(T.squash, 1 - 0.04 * Math.abs(Math.sin(t * 8.5)) * env, w); T.lean = lerp(T.lean, -0.1, w);
            T.arm.R.spark = lerp(T.arm.R.spark, 0.7, w); T.expr = 'smug';
          } },
        // ---- intro: it rises out of the pool with its arms spread wide, shakes the slime off, then bumps its fists with a spark burst
        intro: { len: 5.0,
          init(m) { st.root.set(0, POOL_Y - 4.6, 0); st.rootV.set(0, 0, 0); st.yaw = yawTo(st.look); m.yaw = st.yaw; snap(); },
          run(m, t) {
            const w = 1 - sstep(4.3, 5.0, t), kR = clamp01(t / 1.7), rise = kR < 1 ? eBack(kR, 1.2) : 1, kSh = sstep(2.0, 2.15, t) * (1 - sstep(2.7, 2.95, t));
            const kB = sstep(3.0, 3.3, t), kBump = sstep(3.3, 3.42, t);
            T.rootK = lerp(1, 2.6, 1 - sstep(1.8, 2.2, t));
            off(0, (POOL_Y - 4.6 - HOVER) * (1 - rise) - 0.35 * kSh, 0, w);
            T.clipY = t < 2.6 ? POOL_Y : -1e4; T.clipBand = 0.35;
            const sh = Math.sin((t - 2.0) * Math.PI * 2 * 4.2) * kSh; T.yaw = m.yaw + 0.42 * sh; T.roll = lerp(T.roll, -0.16 * sh, w); T.squash = lerp(T.squash, 1 + 0.12 * (1 - kR) * (t < 1.7 ? 1 : 0) + 0.05 * sh, w);
            for (const s of SIDES) {
              const g = s === 'L' ? 1 : -1, kOut = 1 - kB;
              wrist(s, g * (2.3 + 2.0 * sstep(0.75, 1.5, t)), 0.9 - 2.0 * kSh, 0.5, w * kOut); turn(s, g * 0.9, 0.35, 0.4, 0, 0.3, 1, 0.9, w * kOut); grip(s, 'spread', w * kOut * (1 - kSh)); grip(s, 'relax', w * kSh);
              boss2m(g * (1.6 - 0.98 * kBump), -1.9, 2.2, mB); fistAt(s, mB, kB * w); turn(s, -g, 0.1, 0.25, 0, -1, 0, 1, kB * w); grip(s, 'fist', kB * w);
              springy(s, 1.8, 0.62, kB * w); T.arm[s].spark = lerp(T.arm[s].spark, t < 2.95 ? 0.05 : 1.45, w);
            }
            T.expr = t < 0.9 ? 'neutral' : t < 2.0 ? 'glare' : t < 2.9 ? 'hurt' : 'angry'; if (t > 3.35 && t < 3.9) T.eyeGlow = 1;
            if (t < 1.9 && T.off.y + HOVER > POOL_Y - 3 && Math.random() < 0.6) { const a = Math.random() * 6.283, r = 1.4 + Math.random() * 1.1;
              mA.set(st.root.x + Math.cos(a) * r, POOL_Y + 0.05, st.root.z + Math.sin(a) * r); spawn(1, mA, Math.cos(a) * 1.4, 2.4 + Math.random() * 2.2, Math.sin(a) * 1.4, 0.1 + Math.random() * 0.1, 1.1, C_SLIME); }
            if (kSh > 0.2 && Math.random() < 0.7) { const a = Math.random() * 6.283; mA.set(st.root.x + Math.cos(a) * 2.1, st.root.y - 0.8 + Math.random() * 1.6, st.root.z + Math.sin(a) * 2.1);
              spawn(1, mA, Math.cos(a) * 4 - Math.sin(a) * 2 * sh, 1.5 + Math.random() * 1.5, Math.sin(a) * 4 + Math.cos(a) * 2 * sh, 0.08 + Math.random() * 0.08, 0.9, C_SLIME); }
            if (fire(1, 'introRise')) {} if (t >= 2.0) fire(2, 'introShake');
            if (t >= 3.4 && fire(4, 'introBump')) { mC.copy(arms.L.fc).add(arms.R.fc).multiplyScalar(0.5); burst(mC, 9, 1.4, false, 0); wobble(1.2); st.flash = Math.max(st.flash, 0.25); arms.L.spark = arms.R.spark = 2; }
            if (t >= 4.95) fire(8, 'introDone');
          } },
        // ---- defeat: a last flinch, then it deflates (the bell sags, the arms go limp, the sparks die) and sinks into the pool in bubbles
        defeat: { len: 4.2, stay: true,
          init(m) { st.flash = 1; wobble(2.2); st.sqV -= 1.2; tentKick(0, 3, 0, 3); },
          run(m, t) {
            const kF = 1 - sstep(0.35, 0.7, t), kD = sstep(0.5, 1.7, t), kS = sstep(1.7, 4.0, t);
            T.expr = t < 0.6 ? 'hurt' : 'defeated';
            off(0, -1.0 * kD + (POOL_Y - 5.2 - HOVER + 1.0) * kS * kS, 0, 1);
            T.slump = kD; T.pulseAmp = lerp(1, 0.12, kD); T.pulse = lerp(1, 0.3, kD); T.tentW = lerp(1, 0.25, kD); T.tentG = lerp(1, 2.6, kD); T.rootK = 1 + kS;
            T.clipY = kS > 0 ? POOL_Y : -1e4; T.clipBand = 0.3;
            for (const s of SIDES) { const g = s === 'L' ? 1 : -1;
              wrist(s, g * 3.4, 0.2, 0.4, kF); grip(s, 'spread', kF);
              wrist(s, g * 2.4, -3.2, 0.7, kD); springy(s, 0.6, 0.45, kD); grip(s, 'relax', kD); turn(s, g * 0.2, -1, 0.3, 0, -0.3, -1, 0.9, kD); T.arm[s].spark = lerp(T.arm[s].spark, 0, Math.max(kD, 1 - kF)); }
            if (kS > 0 && kS < 0.98 && Math.random() < 0.85) { const a = Math.random() * 6.283, r = Math.random() * 2.2;
              mA.set(st.root.x + Math.cos(a) * r, POOL_Y + 0.05 + Math.random() * 0.3, st.root.z + Math.sin(a) * r); spawn(0, mA, 0, 0.9 + Math.random() * 1.2, 0, 0.08 + Math.random() * 0.14, 1.6 + Math.random(), C_BUB); }
            if (t >= 4.2) fire(1, 'defeated');
          } },
      };
      // a point in the model's space, in the boss's own frame (relative to the root, unturned)
      function toBossP(p, out) { return out.copy(p).sub(st.root).applyQuaternion(yawQi); }
      // everything back on its targets at once (the intro starts the boss out of sight, so nothing may trail in from where it was)
      function snap() { for (const s of SIDES) { arms[s].init = false; arms[s].Wv.set(0, 0, 0); arms[s].H1v.set(0, 0, 0); arms[s].H2v.set(0, 0, 0); } for (const tn of tents) tn.init = false; st.tilt.set(0, 0, 0); st.tiltV.set(0, 0, 0); }

      // ---------------------------------------------------------------- each frame
      const gLast = new V3(), gV = new V3(); let gInit = false, lookOn = false; const lookWv = new V3();
      function syncG() { model.updateWorldMatrix(true, false); G.copy(model.matrixWorld); Gi.copy(G).invert(); G.decompose(Gp, Gq, Gs); }
      function update(dt, ctx) {
        const c0 = performance.now();
        dt = dt > 0 ? Math.min(dt, 0.1) : 1 / 60;
        st.t += dt; syncG();
        // the group's own motion (when the fight moves it): its acceleration, in the model's frame, drags the arms behind it
        if (!gInit) { gLast.copy(Gp); gV.set(0, 0, 0); gInit = true; }
        _v.copy(Gp).sub(gLast).divideScalar(dt); st.gAcc.copy(_v).sub(gV).divideScalar(dt).clampLength(0, 80); gV.copy(_v); gLast.copy(Gp);
        _q.copy(Gq).invert(); st.gAcc.applyQuaternion(_q).divideScalar(Math.max(Gs.x, 1e-3));
        // where it looks: where it was told, or the player; the camera (if given) for the sparks, which face it
        if (lookOn) st.look.copy(lookWv).applyMatrix4(Gi); else if (ctx.player) st.look.copy(ctx.player).applyMatrix4(Gi);
        if (ctx.camera) { st.camM.setFromMatrixPosition(ctx.camera.matrixWorld).applyMatrix4(Gi); st.camOK = true; }
        yawQ.setFromAxisAngle(AX_Y, st.yaw); yawQi.copy(yawQ).invert();
        // the hover, then the move over it
        idle(st.t); zap.ball = 0; if (mv.name !== 'zap' && !zap.hitOn) zap.on = false;
        if (mv.M) {
          mv.t += dt * mv.sp; const M = mv.M; M.run(mv, M.stay ? Math.min(mv.t, mv.len) : mv.t);
          if (mv.t >= mv.len && !M.stay && mv.M === M) { const n = mv.name; mv.M = null; mv.name = 'idle'; B.busy = false; B.move = 'idle'; emit('done', { move: n }); }
        }
        if (!mv.M) for (const s of SIDES) arms[s].landed = false;
        toModel(); frameSetup(dt);
        const n = Math.max(1, Math.ceil(dt * 120)), h = dt / n;
        for (let i = 0; i < n; i++) step(h);
        pose(dt); tentacles(dt); writeSkin(); faceUpdate(dt); fxUpdate(dt); ptUpdate(dt);
        B.stats.cpuMs = performance.now() - c0;
      }
      function play(name, o) {
        syncG(); yawQ.setFromAxisAngle(AX_Y, st.yaw); yawQi.copy(yawQ).invert();
        const M = MOVES[name];
        if (!M) { if (mv.M && mv.name !== 'defeat') { const n = mv.name; mv.M = null; mv.name = 'idle'; B.busy = false; B.move = 'idle'; emit('done', { move: n, cut: true }); } return 0; }
        if (mv.M && mv.name === 'defeat' && name !== 'intro') return 0;   // (beaten: only the intro brings it back)
        if (mv.M) emit('done', { move: mv.name, cut: true });
        mv.name = name; mv.M = M; mv.o = o || {}; mv.t = 0; mv.fired = 0; mv.sp = Math.max(0.4, Math.min(3, +mv.o.speed || 1)); mv.len = M.len;
        for (const s of SIDES) arms[s].landed = false;
        if (M.init) M.init(mv, mv.o);
        B.busy = true; B.move = name; emit('start', { move: name });
        return mv.len / mv.sp;
      }
      B.fistR = FIST_R * GLOVE * scale; B.bellR = H.bell.rRim * scale; B.moves = Object.keys(MOVES);
      B._dbg = { FU, U, E, face_, T, st, arms, mv, R, H, tents, Mb, tex: pack.tex, POSE, fillPoses, fns: { update, step, pose, tentacles, faceUpdate, fxUpdate, ptUpdate, frameSetup, idle, writeFX, writeSkin, toModel } };   // (for the viewer and tests)
      return {
        play, update,
        lookAt(x, y, z) { if (x === null || x === undefined) { lookOn = false; return; } if (typeof x === 'object') lookWv.copy(x); else lookWv.set(x, y, z); lookOn = true; },
        face(e, hold) { if (!e) { face_.hold = 0; face_.hold2 = null; return; } face_.hold2 = EXPR[e] ? e : 'angry'; face_.hold = hold === undefined ? 1e9 : hold; },
        hand(s, p) { const P = POSE_NAMES.indexOf(p) >= 0 ? p : null; if (s === 'both' || !s) { arms.L.handOverride = arms.R.handOverride = P; } else if (arms[s]) arms[s].handOverride = P; },
        fist(s, out) { return (out || new V3()).copy(arms[s === 'R' ? 'R' : 'L'].fc).applyMatrix4(G); },
        bellPoint(out) { return (out || new V3()).set(0, 0.25, 0).applyMatrix4(Mbell).applyMatrix4(G); },
        dispose() { for (const m of [body.material, hull.material, face.material, fx.mesh.material, pt.pts.material, hull.customDepthMaterial]) m.dispose(); fx.g.dispose(); pt.g.dispose(); skel.dispose(); },
      };
    }
  }

  return { makeBoss, load, EXPR: Object.keys(EXPR), POSES: POSE_NAMES };
})();
const makeBoss = o => BOSS.makeBoss(o);
