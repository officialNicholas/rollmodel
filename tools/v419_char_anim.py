"""v419: the character's animation, cleaned up and polished (the user: "Polish the character animations. Sometimes the finger
placement or the sway of the body, the animations on the main menus, control. When picking stuff on the locker. Clean that and
polish"). Watched first, frame by frame at 60 fps (the lobby's idle moods, picks in the locker, the window spun by hand, crawling,
turning, stopping and starting in a match); what was off, and what changed:
- The locker's turntable leapt off at full speed and crept in at the end: a side or back item turned you at 200 degrees a second from
  the first frame, a skin's spin at 1650, and the way back to the front after a hold started at full speed too. Every turn of the
  window (a pick, a skin's spin, the back button, the way home) now eases in and out on a minimum-jerk curve from where it is, at the
  speed it already has, so a quick second pick bends the turn instead of jerking it.
- A reaction cut short snapped: a pick or a drag mid-hop dropped the body to the floor in one frame (and the camera with it), and an
  emote cut off mid-spin or mid-flip jumped back to facing you, upright, in one frame. A hop cut short now falls the rest of the way
  and lands; an emote's turn carries into the turntable, which eases it home; its flip settles upright on a spring.
- The squash and stretch had one-frame pops: the lobby's idle moods replaced the breathing squash instead of adding to it (a jump as
  each mood began and ended), and the stretch (rise) went straight into the body's scale, so a tap's hop lost 12% of its height in
  one frame half way up. The breathing now goes on under the moods, and the stretch eases like the squash does.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

LK_TURN = r"""
// (v419) the window's turntable: a turn to show something, a skin's spin, the back button, the way home to the front, all ease in and
// out on a minimum-jerk curve from where it is, at the speed it already has (a new goal mid-turn picks up from there; a turn set from
// outside, a skin's extra spin, starts afresh). True when it's there
function lkTurn(goal, T0, k, dt, wrap) {
  let w = SGD.tw;
  if (!w || w.b !== goal || Math.abs(SGD.dyaw - w.y) > 1e-6) {
    if (wrap) SGD.dyaw = wrapA(SGD.dyaw); const d = goal - SGD.dyaw;
    w = SGD.tw = { a: SGD.dyaw, b: goal, v: clamp(SGD.dW || 0, -14, 14), t: 0, T: reduceMotion ? 0.12 : Math.min(1.5, T0 + k * Math.abs(d)), y: 0 };
  }
  w.t += dt; const u = Math.min(1, w.t / w.T), u3 = u * u * u, s = u3 * (10 - 15 * u + 6 * u * u), h = u - 6 * u3 + 8 * u3 * u - 3 * u3 * u * u;
  SGD.dyaw = w.y = w.a + (w.b - w.a) * s + w.v * w.T * h;
  if (u >= 1) { SGD.dyaw = w.b; SGD.tw = null; return true; } return false;
}
// (v419) what a reaction cut short leaves behind: a hop falls the rest of the way down and lands; a flip cut off mid-air settles upright
// on a spring (an emote's turn goes to the turntable, see sgActEnd)
function lkSettle(dt) {
  const D = SGD.A.D, ip = D.ip, F = SGD.fall, emo = !!(SGD.act && SGD.act.k === 'emote');
  if (F) { F.v -= 9 * dt; F.h += F.v * dt;
    if (F.h <= 0) { SGD.fall = null; D.squash = Math.max(D.squash, 0.3 * Math.min(1, -F.v / 2)); if (!SGD.act) ip.hop = 0; }
    else ip.hop = SGD.act ? Math.max(ip.hop || 0, F.h) : F.h; }
  const R = SGD.pr; if (R) { const w = 13, h = Math.min(dt, 1 / 30); R.v += (-w * w * R.x - 2 * w * R.v) * h; R.x += R.v * h;
    if (Math.abs(R.x) < 0.002 && Math.abs(R.v) < 0.02) { SGD.pr = null; if (!emo) ip.pitch = 0; } else ip.pitch = (emo ? ip.pitch || 0 : 0) + R.x; }
  const hp = ip.hop || 0; SGD.hopV = dt > 0 ? (hp - (SGD.hopP || 0)) / dt : 0; SGD.hopP = hp;
}
"""

def apply(s):
    # ---- the locker's turntable: eased turns (a drag and a flick stay as they were: under your finger, then coasting to a stop)
    s = rep(s, """  sgActStep(dt); // (v328: a tap's reaction)
  if (!SGD.dDrag) {
    if (SGD.dV) { SGD.dyaw += SGD.dV * dt; SGD.dV *= Math.exp(-dt * 2.6); if (Math.abs(SGD.dV) < 0.08) SGD.dV = 0; }
    else if (SGD.dyawTo !== null) { const e = SGD.dyawTo - SGD.dyaw; SGD.dyaw += e * Math.min(1, dt * (reduceMotion ? 30 : 5)); if (Math.abs(e) < 0.01) { SGD.dyaw = SGD.dyawTo; SGD.dyawTo = null; } }
    else if ((SGD.dHold -= dt) <= 0 && SGD.dyaw) { SGD.dyaw = wrapA(SGD.dyaw); SGD.dyaw -= SGD.dyaw * Math.min(1, dt * (reduceMotion ? 30 : 2.4)); if (Math.abs(SGD.dyaw) < 0.003) SGD.dyaw = 0; }
  }
""", """  sgActStep(dt); // (v328: a tap's reaction)
  lkSettle(dt); // (v419)
  if (!SGD.dDrag) {
    if (SGD.dV) { SGD.tw = null; SGD.dyaw += SGD.dV * dt; SGD.dV *= Math.exp(-dt * 2.6); if (Math.abs(SGD.dV) < 0.08) SGD.dV = 0; }
    else if (SGD.dyawTo !== null) { if (lkTurn(SGD.dyawTo, 0.4, 0.12, dt, false)) SGD.dyawTo = null; } // (v419: eased, see lkTurn)
    else if ((SGD.dHold -= dt) <= 0 && SGD.dyaw) { if (lkTurn(0, 0.55, 0.2, dt, true)) SGD.dyaw = 0; }
    else SGD.tw = null;
  } else SGD.tw = null;
  SGD.dW = dt > 0 ? wrapA(SGD.dyaw - (SGD.dwP === undefined ? SGD.dyaw : SGD.dwP)) / dt : 0; SGD.dwP = SGD.dyaw; // (v419: how fast the window turns)
""")
    s = rep(s, "\nfunction sgDress(dt) {\n", LK_TURN + "function sgDress(dt) {\n")
    # ---- a reaction cut short: the hop falls the rest of the way, an emote's spin goes to the turntable, its flip settles
    s = rep(s, "function sgActEnd() { const a = SGD.act; SGD.act = null; SGD.actFace = null; if (!a || !SGD.built) return; const ip = SGD.A.D.ip; ip.hop = 0;",
               "function sgActEnd() { const a = SGD.act; SGD.act = null; SGD.actFace = null; if (!a || !SGD.built) return; const ip = SGD.A.D.ip;\n"
               "  if ((ip.hop || 0) > 0.004) SGD.fall = { h: ip.hop, v: clamp(SGD.hopV || 0, -3, 3) }; // (v419: cut short in the air, it comes down)\n"
               "  if (a.k === 'emote' && a.t < a.dur) { const vp = SGD.A.D.vicPose; if (vp && vp.spin) { const sp = wrapA(vp.spin), V = SGD.A.V; SGD.dyaw += sp; if (V.yawD !== undefined) V.yawD += sp; SGD.tw = null; if (SGD.dyawTo === null && !SGD.dDrag) SGD.dyawTo = 0; } if (Math.abs(wrapA(ip.pitch || 0)) > 0.01) SGD.pr = { x: wrapA(ip.pitch), v: 0 }; }\n"
               "  ip.hop = 0;")
    # ---- the lobby: the breathing squash under the idle moods (not swapped out for them); the stretch eased like the squash
    s = rep(s, "sq = idle.sq || 0.04 + 0.035 * Math.sin(clock * 2.3); rise = idle.rise;",
               "sq = idle.sq + 0.04 + 0.035 * Math.sin(clock * 2.3); rise = idle.rise;")
    s = rep(s, "    const sy = (1 - 0.32 * X.sq + 0.18 * (o.rise || 0)) * (1 - 0.72 * X.flat)",
               "    X.ri = X.ri === undefined ? (o.rise || 0) : X.ri + ((o.rise || 0) - X.ri) * Math.min(1, dt * 20); // (v419: eased like the squash: no one-frame pop)\n"
               "    const sy = (1 - 0.32 * X.sq + 0.18 * X.ri) * (1 - 0.72 * X.flat)")
    # ---- the crawl: a planted hand or foot holds its heading on the ground round a turn
    s = rep(s, '    { const r = Math.hypot(LB.fwd.x, LB.fwd.z), a0 = Math.atan2(LB.fwd.x, LB.fwd.z), a = a0 + (Math.PI - 0.08 - a0) * tk; out.contact(l.en, tp, LV2.set(l.m * Math.sin(a) * r * (1 - wvk) + l.m * 0.2 * wvk, -0.35 * lift * (1 - tk) * (1 - wvk) + 0.85 * wvk, Math.cos(a) * r * (1 - wvk) + 0.5 * wvk), LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1); }',
               "    { const r = Math.hypot(LB.fwd.x, LB.fwd.z), a0 = Math.atan2(LB.fwd.x, LB.fwd.z), a = a0 + (Math.PI - 0.08 - a0) * tk; LV2.set(l.m * Math.sin(a) * r * (1 - wvk) + l.m * 0.2 * wvk, -0.35 * lift * (1 - tk) * (1 - wvk) + 0.85 * wvk, Math.cos(a) * r * (1 - wvk) + 0.5 * wvk);\n      // (v419) a planted hand or foot keeps its heading on the ground while the body turns over it (carried round with the ground, as its\n      // place is), up to a comfortable twist of the wrist; lifted, it eases back to the way the body points. The fingers and toes no\n      // longer swivel on the floor round a turn\n      { const ad = Math.atan2(LV2.x, LV2.z), pl = !air && l.st === 'stance' && l.lift < 0.02 && sl < 0.05 && tk < 0.02 && wvk < 0.002 && !(L.settle && L.settle.l === l), wr = x => Math.atan2(Math.sin(x), Math.cos(x));\n        if (l.hy === undefined || air) l.hy = ad; else if (pl) l.hy += C ? -yr * h : 0; else l.hy += wr(ad - l.hy) * Math.min(1, dt * 12);\n        const dA = Math.max(-0.6, Math.min(0.6, wr(l.hy - ad))); if (pl) l.hy = ad + dA;\n        if (dA > 1e-4 || dA < -1e-4) { const c = Math.cos(dA), sn = Math.sin(dA), x = LV2.x, z = LV2.z; LV2.x = x * c + z * sn; LV2.z = z * c - x * sn; } }\n      out.contact(l.en, tp, LV2, LV3.set(LB.pole.x * l.m, LB.pole.y, LB.pole.z), 1); }")
    return s
