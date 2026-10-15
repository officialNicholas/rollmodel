// ---------- (v311, test builds only) the boss viewer: the Sunken Keep's stage preview with the boss over the pool ----------
// bossView({ auto, scale, cam }) from the console (or __T.ev): the stage preview opens (you on the floor, the game's own camera), the
// boss rises out of the pool and, with auto, goes through every move in turn, a label naming each. BV.cam picks the view: null for the
// game's own camera, 'fight' (further back and up, the boss and you in one frame, like the owner's picture), or { p, l, fov }.
let BV = null;
window.bossView = (o = {}) => {
  if (BV) return BV;
  BV = { o, boss: null, auto: o.auto !== false, cam: o.cam === undefined ? 'fight' : o.cam, i: 0, wait: 0.6, P: new THREE.Vector3(), log: [], el: null, frozen: false, look: new THREE.Vector3() };
  if (state === 'menu') conqPreview();
  const el = document.createElement('div'); el.id = 'bossLabel';
  el.style.cssText = 'position:fixed;left:10px;top:calc(env(safe-area-inset-top) + 64px);z-index:60;font:700 15px/1.3 system-ui,sans-serif;color:#fff;background:rgba(20,8,40,.62);padding:6px 10px;border-radius:10px;pointer-events:none;white-space:pre';
  document.body.appendChild(el); BV.el = el;
  return BV;
};
// the cycle: each step a move (with its options) and how long to hover after it
const BV_SEQ = [['intro', {}, 1.2], ['punch', { hand: 'L' }, 0.6], ['punch', { hand: 'R' }, 0.8], ['slam', {}, 0.8], ['sweep', { hand: 'L' }, 0.6],
  ['sweep', { hand: 'R', dir: 1 }, 0.8], ['zap', {}, 0.8], ['hurt', {}, 0.6], ['stunned', { time: 2.5 }, 0.8], ['taunt', {}, 0.8], ['defeat', {}, 1.0]];
function bvTick(rdt) {
  if (!BV) return;
  if (!BV.boss && (state === 'play' || state === 'intro')) {
    const b = makeBoss({ scale: BV.o.scale || 1, poolY: -0.14 }); BV.boss = b; scene.add(b.group); b.group.position.set(0, 0, 0);
    b.group.traverse(m => { if (m.isSkinnedMesh && m.castShadow) m.receiveShadow = false; });
    for (const e of ['start', 'windup', 'strike', 'hit', 'zap', 'recover', 'stunStart', 'stunEnd', 'introRise', 'introShake', 'introBump', 'introDone', 'defeated'])
      b.on(e, d => { BV.log.push(e + (d.hand ? ' ' + d.hand : '')); if (BV.log.length > 4) BV.log.shift(); });
    b.ready.then(() => { if (BV.auto) { BV.i = 0; BV.wait = 0.3; } });
  }
  const b = BV.boss; if (!b || !b.isReady) return;
  const dt = BV.frozen ? 0 : rdt;
  // the cycle
  if (BV.auto && !BV.frozen && !b.busy) { BV.wait -= rdt; if (BV.wait <= 0) { const s = BV_SEQ[BV.i % BV_SEQ.length]; b.play(s[0], Object.assign({}, s[1])); BV.wait = s[2]; BV.i++; } }
  else if (BV.auto && !BV.frozen && b.move === 'defeat' && b.busy) { BV.wait -= rdt; if (BV.wait < -5.4) { b.play('intro', {}); BV.wait = 1.2; BV.i = 1; } }
  // the camera: the game's own, or the fight's (back and up behind you, looking at a point between you and the boss), or a set one
  const c = BV.cam;
  if (c === 'fight') { const yaw = Math.atan2(-P.x, -P.z), d = 6.4; camera.position.set(P.x - Math.sin(yaw) * d, 3.1, P.z - Math.cos(yaw) * d); BV.look.set(P.x * 0.35, 3.3, P.z * 0.35); camera.up.set(0, 1, 0); camera.lookAt(BV.look); camera.fov = camera.aspect < 0.8 ? 66 : 54; camera.updateProjectionMatrix(); }
  else if (c && c.p) { camera.position.fromArray(c.p); camera.up.set(0, 1, 0); camera.lookAt(BV.look.fromArray(c.l)); if (c.fov) { camera.fov = c.fov; camera.updateProjectionMatrix(); } }
  camera.updateMatrixWorld();
  if (dt > 0) b.update(dt, { player: BV.P.set(P.x, (P.y || 0) + 0.45, P.z), camera });
  if (BV.el) BV.el.textContent = 'Boss: ' + (b.busy ? b.move : 'idle') + (BV.log.length ? '\n' + BV.log.join(' · ') : '') + '\n' + b.stats.tris + ' tris · ' + b.stats.draws + ' draws · update ' + b.stats.cpuMs.toFixed(2) + ' ms';
}
