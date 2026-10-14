"""v285: the first launch, turning it round to have a look at it (a patch over the intro, tools/v257_intro.js).
Once it's out of the paint and standing on its spot (naming it, "All set?", and the picks again after "Not yet"), a drag across the
scene, anywhere but the cards, turns it round as the locker does: the same feel (it follows the finger, a flick sends it gliding on),
and the game's own animator curls its body, tail and ears with the turn. While it's being turned the camera eases back, slowly, the
longer it goes on. Let go and it glides to a stop, a beat, then it turns itself back round to face you (the short way, at its own
pace, with a blink), and as it comes round the camera eases back in. Leaving its spot (Let's roll) it's straightened up first."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

TURN = r"""  // (v285) turning it round to have a look at it, as in the locker: a drag across the scene (anywhere but the cards) while it stands on
  // its spot. The camera eases back, slowly, the longer it's turned; let go and it glides on, then after a beat it turns itself back
  // round to face you (the short way, at its own pace), and the camera comes back in as it does
  const TURN = { k: 0.012, beat: 0.45, out: 0.42, zOut: 0.45, zIn: 1.3 };
  const turnOk = () => !!X && X.stood && X.hold.visible && (X.ph === 'iris' || X.ph === 'style' || X.ph === 'paint' || X.ph === 'name' || X.ph === 'confirm');
  const tnOf = () => X.tn || (X.tn = { tgt: 0, yaw: 0, vel: 0, z: 0, drag: null, wait: 0, back: true, moved: 0 });
  const TAU = Math.PI * 2, homeOf = y => Math.round(y / TAU) * TAU;
  function turnUi(el) {
    el.addEventListener('pointerdown', e => { if (!turnOk() || e.target.closest('.flpanel') || (e.button || 0) !== 0) return; const T = tnOf();
      T.drag = { id: e.pointerId, x: e.clientX, tm: performance.now(), v: 0 }; T.wait = 0; T.back = false; T.moved = 0; });
    el.addEventListener('pointermove', e => { const T = X && X.tn, d = T && T.drag; if (!d || d.id !== e.pointerId) return; if (!turnOk()) { T.drag = null; return; }
      const now = performance.now(), dx = e.clientX - d.x; d.v = d.v * 0.5 + 0.5 * dx / Math.max(4, now - d.tm); d.tm = now; T.tgt += dx * TURN.k; T.moved += Math.abs(dx); d.x = e.clientX; });
    const end = e => { const T = X && X.tn, d = T && T.drag; if (!d || d.id !== e.pointerId) return;
      if (e.type === 'pointerup' && performance.now() - d.tm < 90) T.tgt += clamp(d.v * TURN.k * 160, -2.6, 2.6); /* (let go mid-swipe: it glides on round) */ T.drag = null; T.wait = 0; };
    el.addEventListener('pointerup', end); el.addEventListener('pointercancel', end);
  }
  // how far it's turned from facing you (added to its heading), stepped once a frame; and how far out the camera has eased (0 to 1)
  function turnTick(dt) {
    const T = tnOf(), ok = turnOk(); if (!ok) T.drag = null;
    if (!T.drag) { const off = Math.abs(T.yaw - homeOf(T.yaw)) > 0.04, still = Math.abs(T.vel) < 0.3 && Math.abs(T.tgt - T.yaw) < 0.1;
      if (!ok) { if (off || T.tgt !== homeOf(T.tgt)) { T.tgt = homeOf(T.yaw); T.back = true; } } // (off its spot: straightened up, now)
      else if (!T.back && still) { T.wait += dt; if (T.wait > TURN.beat) { T.tgt = homeOf(T.yaw); T.back = true; if (off && X.I.blink) X.I.blink(); } } }
    const ret = T.back && !T.drag, d = T.tgt - T.yaw, g = !ok ? 7 : ret ? 2.6 : 4.5, cap = !ok ? 9 : ret ? 3.2 : 6;
    T.vel += (clamp(d * g, -cap, cap) - T.vel) * Math.min(1, dt * (ret ? 6 : 10)); T.yaw += T.vel * dt;
    if (ret && Math.abs(d) < 0.002 && Math.abs(T.vel) < 0.01) { T.yaw = T.tgt = homeOf(T.tgt); T.vel = 0; }
    // the camera: out while it's being turned (or gliding round), very slowly; back in once it's coming back round to face you
    const out = ok && ((T.drag && T.moved > 6) || (!T.back && Math.abs(T.vel) > 0.3) || (T.z > 0 && !T.back));
    const inK = T.back && Math.abs(T.tgt - T.yaw) < 0.7 ? TURN.zIn : !ok ? TURN.zIn * 2 : 0;
    if (out) T.z += (1 - T.z) * Math.min(1, dt * TURN.zOut); else if (inK) T.z += (0 - T.z) * Math.min(1, dt * inK);
    return T.yaw;
  }
  function buildUi() {"""

def apply(s):
    s = rep(s, "  function buildUi() {", TURN)
    s = rep(s, "stage.appendChild(el); UI = { el, cur: null };", "stage.appendChild(el); UI = { el, cur: null }; turnUi(el);")
    # its heading, plus however far it's been turned round
    s = rep(s, "bob = c.pop > 0 ? Math.sin((1 - c.pop / 1.4) * Math.PI) * 0.03 * c.pop : 0, yw = c.yaw, sc",
               "bob = c.pop > 0 ? Math.sin((1 - c.pop / 1.4) * Math.PI) * 0.03 * c.pop : 0, yw = c.yaw + turnTick(dt), sc")
    # the shot widens as the camera eases out
    s = rep(s, "d = Math.max(0.6, s.r * H / (Math.tan(X.pc.fov * Math.PI / 360) * 0.86 * Math.min(fw, fh)))",
               "d = Math.max(0.6, s.r * (X.tn ? 1 + TURN.out * X.tn.z : 1) * H / (Math.tan(X.pc.fov * Math.PI / 360) * 0.86 * Math.min(fw, fh)))")
    return s
