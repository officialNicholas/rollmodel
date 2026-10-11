// ---------- the axolotl in the game: the slime's stand-in, answering the same calls (make, update, headTop, headSize, bodyPoint and each
// character's own) on the axolotl runtime (AXO). Its two bodies (on all fours to get about, upright in the menus and its big moments)
// come from axo-pack.txt; if that never arrives the slime carries on as before ----------
const AXOC = (() => {
  const S = { ready: false, failed: false, pack: null, list: [] };
  const fromB64 = t => { t = t.replace(/[^A-Za-z0-9+/=]/g, ''); if (typeof Uint8Array.fromBase64 === 'function') return Uint8Array.fromBase64(t).buffer;
    const s = atob(t), u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u.buffer; };
  // the pack: 'RMA1', the header's length, the header (each body's metadata and where its data sits), the data
  async function load(url) {
    let buf; if (window.AXO_PACK_BUF) buf = window.AXO_PACK_BUF.buffer.slice(window.AXO_PACK_BUF.byteOffset, window.AXO_PACK_BUF.byteOffset + window.AXO_PACK_BUF.byteLength);
    else { const r = await fetch(url); if (!r.ok) throw new Error('axolotl pack ' + r.status); buf = fromB64(await r.text()); }
    const dv = new DataView(buf);
    if (String.fromCharCode(dv.getUint8(0), dv.getUint8(1), dv.getUint8(2), dv.getUint8(3)) !== 'RMA1') throw new Error('not an axolotl pack');
    const hl = dv.getUint32(4, true), head = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 8, hl))), base = 8 + hl;
    S.pack = {}; for (const [name, m] of Object.entries(head.meshes)) S.pack[name] = { name, meta: m.meta, buf: buf.slice(base + m.off, base + m.off + m.len) };
    S.ready = true;
  }
  // its metres in the blob's body space (the body is scaled by the blob's radius), where it stands (the old blob's ground) and how far its
  // middle sits ahead of its own origin (so the blob's middle is the axolotl's)
  const AXO_M = 0.7, SC = AXO_M / PR, GROUND = -0.82, MID_Z = 0.12;
  // accessories are placed by head size relative to the slime's head (its radius in the slime's own model), so the same fits work
  const HEAD_R0 = 0.425;
  const _m = new THREE.Matrix4(), _mi = new THREE.Matrix4(), _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _k = new THREE.Vector3();
  const SUN_DIR = new THREE.Vector3();
  function make(opt) {
    opt = opt || {};
    const col = new THREE.Color(opt.color || 0xE3122F), look = new AXO.Look({ color: col.getHex(), faceCell: HI ? 320 : 176 });
    const Sm = AXO.meshFrom(S.pack.stand, null, { look, name: 'stand' }), Cm = AXO.meshFrom(S.pack.crawl, null, { look, name: 'crawl' });
    const P = new AXO.Puppet({ stand: Sm, crawl: Cm }), A = new AXO.Animator(P); A.setLook(look);
    const g = new THREE.Group(); g.scale.setScalar(SC); g.position.set(0, GROUND, MID_Z * SC);
    const xray = new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.55, depthWrite: false, depthFunc: THREE.GreaterDepth }), ghosts = [];
    for (const M of [Sm, Cm]) { const me = M.mesh; g.add(me); me.renderOrder = 32; me.layers.enable(3); charMat(me.material);
      if (!HI) { me.material.clearcoat = 0; me.material.sheen = 0; } // (a phone: no clearcoat or sheen layers, a much cheaper shader)
      // (behind a wall you still see where it is: a flat see-through copy in its team's color, drawn only where something is in front)
      const gm = AXO.dqsMaterial(xray.clone(), M.meta), gh = new THREE.SkinnedMesh(me.geometry, gm); gm.customProgramCacheKey = () => 'axo-xray';
      gh.bind(me.skeleton, me.bindMatrix); gh.frustumCulled = false; gh.renderOrder = 30; me.add(gh); ghosts.push(gh); M.ghost = gh; }
    const I = { kind: 'axo', root: new THREE.Group(), color: col, form: 'slime', fangs: false, mats: {}, parts: {}, groups: { slime: g },
      U: { sRim: { value: new THREE.Vector4() } }, st: { formK: 1, pop: 0, earKick: 0, formNext: null, t: Math.random() * 10 },
      ax: { look, P, A, S: Sm, C: Cm, g, state: null, wet: 0, coat: 0, wade: 0, burstT: -1, fadeT: 0, fade0: 0, flat: 0, sq: 0, frame: -1,
        head: { c: new THREE.Vector3(), q: new THREE.Quaternion(), r: 0.3, neck: new THREE.Vector3(), ok: false } } };
    I.root.add(g); I.ax.ghosts = ghosts;
    // (it's made on all fours: the change from the upright body it's built in is run through ahead, out of sight)
    A.update(1 / 60); A.set('crawl'); for (let i = 0; i < 44 && A.state !== 'crawl'; i++) A.update(1 / 20); for (let i = 0; i < 10; i++) A.update(1 / 20);
    const X = I.ax; X.state = 'crawl';
    I.setColor = c => { if (I.color.equals(c)) return; I.color.copy(c); look.setColor(c.getHex()); for (const gh of ghosts) gh.material.color.copy(c); };
    I.setPaint = c => { look.U.uPaint.value.copy(c); };
    I.setWade = w => { X.wade = w; };
    I.setFangs = on => { I.fangs = !!on; look.setFangs(!!on); };
    I.setLashes = (l, r) => look.setLashes(l, r === undefined ? l : r);
    I.setPatch = k => { look.U.fLash.value.z = k; };
    I.setIris = c => { look.U.fIris.value.set(c[0], c[1], c[2]); };
    I.setEyeStyle = k => look.setEyeStyle(k);
    I.setExpression = name => look.setExpression(name);
    I.blink = () => look.blink();
    I.flutter = n => look.flutter(n || 3);
    I.shut = () => { look.blinkK = Math.max(look.blinkK, 0.06); };
    I.fire = () => {};
    I.setForm = f => { I.formWanted = f; }; // (a giant is the same axolotl, bigger: it keeps its own head and what it wears)
    // the reactions: a knock rocks it and throws the gills and the tail; a push-off squashes it down a moment; a shake after a tumble
    I.impact = (x, z, k) => { if (!(k > 0)) return; k = Math.min(1.2, k); A.kickGills(-x * k, -z * k); A.sqPush[0] += 1.6 * k; for (let i = 0; i < 6; i++) A.tailPush[i * 2] += x * 45 * k; };
    I.launch = k => { A.sqPush[0] += 2.2 * k; };
    I.shakeOff = k => { A.kickGills(0, 0.8 * k); look.blink(); };
    I.shake = k => { A.kickGills(0.6, 1); for (let i = 0; i < 6; i++) A.tailPush[i * 2] += (i % 2 ? -60 : 60); look.blink(); };
    I.popIn = () => { A.sqPush[0] += 3.5; A.kickGills(0, 1); look.blinkK = Math.max(look.blinkK, 0.38); X.coat = Math.max(X.coat, 0.001); X.rise = 2.2; X.burstT = 0.72; X.fadeT = 0; }; // (the paint washes up over it, then bursts off)
    // its paint: all over it (c), then splashing off (burst), or running off over a while (fade); wet from it (soak)
    I.coatOn = () => { X.coat = 1; X.rise = 0; X.burstT = -1; X.fadeT = 0; };
    I.coatShape = () => {};
    I.coatBurst = delay => { if (X.coat > 0 && X.burstT < 0 && X.fadeT <= 0) X.burstT = Math.max(0.001, delay); else if (X.burstT > 0) X.burstT = Math.min(X.burstT, Math.max(0.001, delay)); };
    I.coated = () => X.coat > 0.001;
    I.coatFade = T => { if (X.coat > 0) { X.fadeT = T; X.fade0 = T; X.burstT = -1; } };
    I.soak = k => { X.wet = Math.max(X.wet, k === undefined ? 1 : k); };
    I.setColor(col);
    S.list.push(I);
    return I;
  }
  // which of its states fits what the blob is doing: on all fours nearly all the time (the menus, the locker, a match); up on its hind legs
  // only for its big moments (the victory, riding the rocket)
  function stateFor(I, o) {
    const D = o.D;
    if (D && vic && D.vicPose) return 'victory';
    if (D && D.rocket && D.st === 'play') return 'jetpack';
    return 'crawl';
  }
  // how high the paint it wades through washes up it at the most (the fill order: the crawl's from where it touches the ground, the stand's
  // from its feet): over its feet and hands, up its legs and under its belly
  const WADE_CRAWL = 0.3, WADE_STAND = 0.3;
  function update(I, o) {
    const X = I.ax, A = X.A, look = X.look, D = o.D, dt = Math.min(0.05, o.dt || 0); I.st.t += dt;
    // the state, then how it moves: its stride with its speed, bending into the turns, breathing harder worn out
    const st = stateFor(I, o); if (st !== X.state) { X.state = st; A.set(st); }
    const busy = D && D.st === 'play' && state !== 'menu', inAir = !!o.inAir, charging = busy && D.charging && !D.air;
    A.motion.speed = inAir || charging ? 0 : clamp((o.spd || 0) * 1.5, 0, 1.5);
    A.motion.turn = clamp(-(o.lean || 0) * 1.2, -1, 1);
    A.motion.exert = Math.max(o.tired ? 1 : 0, charging ? 0.4 + 0.6 * (D.charge || 0) : 0, busy && D.spd > 4 ? 0.3 : 0);
    // where it looks: at a rival close by, or wherever the game has it watching
    const W = o.watch; A.look.yaw = W ? W.yaw * 57.3 : (o.glance || 0) * 57.3 * 0.7; A.look.pitch = W ? (W.pitch - 0.85) * 57.3 : 0;
    // in the menus it looks up at you (the head takes 0.6 of the look, the neck the rest)
    if (!W && state === 'menu') { I.root.updateWorldMatrix(true, false); _v.setFromMatrixPosition(I.root.matrixWorld); _v2.setFromMatrixPosition(camera.matrixWorld).sub(_v);
      _v2.transformDirection(_mi.copy(I.root.matrixWorld).invert());
      X.lookY = clamp(Math.atan2(_v2.x, _v2.z) * 57.3, -55, 55); X.lookP = clamp(Math.atan2(_v2.y, Math.hypot(_v2.x, _v2.z)) * 57.3, -10, 32);
      A.look.yaw = X.lookY / 0.6 * 0.8 + A.look.yaw * 0.2; A.look.pitch = X.lookP / 0.6 * 0.85; }
    // the menu's dance: its head tips side to side and nods to the beat, it sways its head with the shimmy; its little hops kick up its gills
    // going up and squash it landing
    A.look.roll = (o.headRoll || 0) * 57.3 * 1.4; A.look.pitch += (o.headPitch || 0) * 57.3 * 1.2; A.look.yaw += (o.shove || 0) * 22;
    if (state === 'menu') { const up = !!o.inAir; if (up && !X.hopUp) { A.sqPush[0] -= 2; A.kickGills(0, -0.5); X.hopT = 0; } if (up) X.hopT += dt;
      else if (X.hopUp && X.hopT > 0.1) { A.sqPush[0] += 4; A.kickGills(0, 0.9); for (let i = 0; i < 6; i++) A.tailPush[i * 2 + 1] -= 40; } X.hopUp = up; }
    // squashed: flattened by a pound (a pancake), or the game's own squash and stretch (landing, winding up a fling)
    X.flat += ((D && D.flatT > 0 ? 1 : 0) - X.flat) * Math.min(1, dt * (D && D.flatT > 0 ? 22 : 7));
    X.sq += (clamp(o.squash || 0, -0.3, 0.6) - X.sq) * Math.min(1, dt * 18);
    const sy = (1 - 0.32 * X.sq + 0.18 * (o.rise || 0)) * (1 - 0.72 * X.flat), sxz = (1 + 0.16 * X.sq) * (1 + 0.4 * X.flat);
    I.root.scale.set(sxz, sy, sxz);
    // the paint: all over it until it bursts off or runs off; wading through it, it washes up its legs and belly; wet, it shines
    if (X.rise > 0) { X.coat = Math.min(1, X.coat + X.rise * dt); if (X.coat >= 1) X.rise = 0; }
    if (X.burstT > 0) { X.burstT -= dt; if (X.burstT <= 0) { X.burstT = -1; X.fadeT = 0.16; X.fade0 = 0.16; if (I.onBurst) I.onBurst(); } }
    if (X.fadeT > 0) { X.fadeT = Math.max(0, X.fadeT - dt); X.coat = X.fade0 > 0 ? Math.min(X.coat, X.fadeT / X.fade0) : 0; }
    X.wet = Math.max(0, X.wet - dt / 2.6);
    look.setPaint(X.coat); look.U.uCoat.value.w = clamp(X.wade || 0, 0, 1) * (A.mesh === 'crawl' ? WADE_CRAWL : WADE_STAND);
    look.U.uCoat.value.z = Math.max(X.wet, X.coat > 0.5 ? 1 : 0);
    // the light it's lit by, in the camera's space (its fin glows from behind, its rim catches it)
    SUN_DIR.copy(sun.position).sub(sun.target.position).normalize().transformDirection(camera.matrixWorldInverse); look.U.uKeyDir.value.copy(SUN_DIR);
    A.update(dt);
    // which body shows (both while it changes over between them), with the animator's jelly squash
    const cur = X.P.m[A.mesh].mesh, oth = X.P.m[A.mesh === 'stand' ? 'crawl' : 'stand'].mesh;
    cur.visible = true; oth.visible = A.fade < 1; cur.scale.set(1, A.squash, 1); oth.scale.set(1, A.squash, 1);
    for (const M of [X.S, X.C]) M.ghost.visible = !I.noGhost && M.mesh === cur;
    X.frame = -1; // (the head's place is worked out again when it's next asked for)
  }
  // the head, in the blob's body space: its middle (the face sphere's centre), how it's turned (up its top, forward its face) and its size
  function headFrame(I) {
    const X = I.ax, H = X.head; if (X.frame === 0) return H;
    const M = X.P.m[X.A.mesh], hb = M.byName.head, fc = M.meta.face ? M.meta.face.c : M.meta.headAbs, ri = X.P.idx.head;
    hb.updateWorldMatrix(true, false); _mi.copy(I.root.matrixWorld).invert(); _m.multiplyMatrices(_mi, hb.matrixWorld).premultiply(I.root.matrix); // (just the chain down to the head)
    H.c.set(fc[0], fc[1], fc[2]).sub(M.rest[ri]).applyMatrix4(_m);
    _m.decompose(_v, _q, _s); H.q.copy(_q);
    H.r = (M.meta.face ? M.meta.face.r : M.meta.headr) * SC * I.root.scale.y * (M.mesh.scale.y || 1);
    // under its chin (the bow tie, the pearls): low on the front of the head, where they show over its chest from the front
    H.neck.set(0, -0.84 * H.r, 0.5 * H.r).applyQuaternion(H.q).add(H.c);
    X.frame = 0; H.ok = true; return H;
  }
  function headTop(I, out, quat, up) {
    const H = headFrame(I); out.copy(_k.set(0, H.r * (up === undefined ? 0.94 : up), 0).applyQuaternion(H.q)).add(H.c);
    if (quat) quat.copy(H.q); return out;
  }
  const headSize = I => headFrame(I).r;
  // its back, between the shoulders (the rocket's paint pack): the chest joint, d behind it (in the blob's body space)
  function backPoint(I, out, d) {
    const X = I.ax, M = X.P.m[X.A.mesh], cb = M.byName.chest || M.byName.spine1 || M.byName.head;
    cb.updateWorldMatrix(true, false); _mi.copy(I.root.matrixWorld).invert(); _m.multiplyMatrices(_mi, cb.matrixWorld).premultiply(I.root.matrix);
    out.setFromMatrixPosition(_m); out.z -= d === undefined ? 0.5 : d; return out;
  }
  function bodyPoint(I, x, y, z, out) { const H = headFrame(I); return out.copy(H.neck); }
  return { S, load, make, update, headTop, headSize, bodyPoint, backPoint, headR0: HEAD_R0 };
})();
