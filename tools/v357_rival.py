"""v357: the first lesson as the user laid it out: move, jump and sling on your own; your tank runs dry and one basin comes up for it;
you roll in, fill up and jump out; you stop, the view cuts to a second basin across the canvas and the rival climbs out of it; then the
ground pound (on him), dodging his pound, and the special orb, which is the end.

- Before the rival comes: only you in the match (as in v356), the start basin and the refill basin the only ones that show, the top bar
  hidden (no timer, no coverage) for the whole lesson.
- The refill: your tank drains in under a second, a basin comes up a few steps ahead of you, and the arrow (and after a moment the
  swipe finger) shows the way. In it, it fills you up; once you're full, "TAP to jump out!" (no "Full tank! Tap POUND to burst out").
- The rival's entrance: as you land you stop and the controls go; a beat later the view cuts (bars in, controls hidden) to a basin about
  nine metres ahead of you, turned so he comes out on your side, his eyes peeking out of his paint. He climbs out the way you do at a
  match's start, shakes himself off, and the view cuts back to you, turned to face him. Then the pound, the dodge and the orb, as the
  lesson had them before v356, and the match ends.
- Basins in the lesson: one nobody is in and nobody is near sinks (the start one, the refill, his, any you or he came back in after a
  fall). Your tank and his stay full but for the refill lesson itself.
- Basics Complete lists Steering and jumping, Flinging, Refilling, The pound, Dodging and The orb.
- Anywhere: a swipe up to roll into a basin that only lands once you're in it no longer rolls you straight back out; and in a basin a
  slow tap (held just past the point a press turns into aiming a fling) still hops you out."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def cut(s, a, b, new=''):
    """Replace the text from marker a (included) up to marker b (kept) with new."""
    assert s.count(a) == 1 and s.count(b) == 1, (s.count(a), s.count(b), a[:80], b[:80])
    i, j = s.index(a), s.index(b); assert i < j, (a[:60], b[:60]); return s[:i] + new + s[j:]

STEPS = r"""  // (v357) out of paint: your tank empties, one basin comes up a few steps ahead of you (the only one about), and the way to it is shown
  { id: 'basin', max: 55, enter() { tut.slowK = 1; tut.basinTip = false; tut.basinT = 0; tut.basinSw = false; tut.potQ = null; tut.potTry = 0; tutHide(); },
    exit() { tut.potQ = null; },
    tick(dt) { if (P.dryT) P.dryT = 0; /* (no running dry into a knock-out in the lesson) */
      if (!tut.potQ && P.st === 'play' && !P.air && (tut.potTry -= dt) <= 0) { tut.potTry = 0.3; tut.potQ = tutRaisePot(); } /* (once you're down from the fling: its spot is found on your level) */
      if (P.st === 'play') P.paint = tut.basinTip ? Math.min(P.paint, 0.02) : Math.max(0, P.paint - dt * 1.1); /* (the tank empties in under a second and stays out till you refill) */
      if (tut.basinTip && !tut.basinSw) { tut.basinT += dt; if (tut.basinT > 2.5 && P.st === 'play') { tut.basinSw = true; tutGest('swipe'); } } /* (not there yet: a finger shows the swipe up, a roll gets you there faster) */
      if (!tut.basinTip && P.paint <= 0.02) { tut.basinTip = true; pingTank(4); tutShow('Out of paint! Roll into a *' + potWord().toUpperCase() + '* to refill', null, 'basin', true, true); }
      return P.st === 'hide' && tut.basinTip; } },
  // (v357) full again, you jump out (a tap) and stop where you land; the view cuts to a second basin across the canvas, the rival climbs
  // out of it, and the view cuts back to you, turned to face him
  { id: 'rival', max: 60, enter() { tutHide(); tut.slowK = 1; tut.sub = 'tub'; tut.rvT = 0; tut.outTip = false; tut.tubT = 0; },
    exit() { tutRevealEnd(); },
    tick(dt) {
      if (tut.sub === 'tub') {
        if (P.st === 'hide' && P.pot) { P.pot.ink = Math.max(P.pot.ink, 0.3); /* (it keeps some paint: a basin drunk dry throws you out itself) */
          if (!tut.outTip && P.paint >= 0.97) { tut.outTip = true; tutShow(say('*TAP* to jump out!', 'Press *SPACE* to jump out!'), null, 'jumpout', true, true); }
          if (tut.outTip && (tut.tubT += dt) > 9) jump(P); /* (left in there a good while: out it hops) */
          return false; }
        if (P.st !== 'play') return false; tutHide(); tut.sub = 'land'; }
      if (tut.sub === 'land') { if (P.air) return false; tut.sub = 'stop'; tut.rvT = 0; tut.hold = true; }
      tut.rvT += dt;
      if (tut.sub === 'stop') { if (tut.rvT < 0.6 || P.spd > 0.3) return false; tut.sub = tutRivalUp() ? 'peek' : 'look'; tut.rvT = 0; return false; }
      if (tut.sub === 'peek') { if (tut.rvT < 0.8) return false; if (H.st === 'hide' && H.pot) introCrawl(H); tut.sub = 'climb'; tut.rvT = 0; return false; }
      if (tut.sub === 'climb') { if (H.introCrawl && tut.rvT < 4) return false; tut.sub = 'look'; tut.rvT = 0; return false; }
      return tut.rvT > 1.1; } }, // (out and shaking himself off: a moment, then back to you)
  // the pound, on the rival: he comes over and circles in close, and once he's in reach the tip comes up. In the air after a fling the
  // button fires a missile instead: close to him that's what the tip says, further off it says nothing till you're down. Knocking him out
  // or flattening him does it
  { id: 'pound', max: 80, exit() { tut.drive = null; tut.driveMode = null; TUT_AI.speed = 0.8; }, enter() { tut.hidePound = false; tut.keepAway = false; tut.drive = H; tut.driveMode = 'near'; TUT_AI.speed = 0.62; tutGivePound(); tut.kos0 = P.kos; tut.flat0 = P.flatted; tut.slowK = 1; tut.slowT = 0; tut.poundIn = false; tut.poundShown = false; tut.sub = ''; tutHide(); },
    tick(dt) { if (tut.slowT > 0) { tut.slowT -= dt / Math.max(tut.slowK, 0.05); if (tut.slowT <= 0) tut.slowK = 1; }
      if (P.slamCD > 1.5) P.slamCD = 1.5; // (the pound keeps coming back until one lands)
      const hd = Math.hypot(H.x - P.x, H.z - P.z), near = H.st === 'play' && hd < 11; TUT_AI.speed = hd > 8 ? 1.3 : hd > 5 ? 0.9 : 0.62; /* (hurries over, then eases in) */ if (!tut.poundIn && P.st === 'play') tutRivalIn(5.5); if ((H.st === 'play' && hd < SLAM_R + PR && Math.abs(H.y - P.y) < 1.2) || tut.st > 24) tut.poundIn = true; /* (the tip waits for the rival to come close) */
      const fwd = P.air && (P.flingC || 0) > 0.15 && !P.slam, sub = fwd ? (near && P.flung ? 'missile' : 'wait') : tut.poundIn ? 'pound' : 'wait';
      if (sub !== tut.sub) { const first = sub === 'pound' && !tut.poundShown; tut.sub = sub; tutGivePound();
        if (sub === 'wait') { tutHide(); if (tut.slowT <= 0) tut.slowK = 1; }
        if (first) { tut.poundShown = true; tut.slowK = TUT_SLOW; tut.slowT = 3.5; }
        if (sub === 'missile') { tut.slowK = 0.3; tutShow(say('*POUND* now to fire a missile!', 'Press *E* now to fire a missile!'), 'slamBtn', 'missile', true); }
        else if (sub === 'pound') { if (tut.slowT <= 0) tut.slowK = 1; tutShow(hd < 6 ? say('Your Pound splats everything round you. The rival’s close, tap it!', 'Your Pound (E) splats everything round you. The rival’s close, press E!') : say('Your Pound splats everything round you. Get close to the rival and tap it!', 'Your Pound (E) splats everything round you. Get close to the rival and press E!'), 'slamBtn', 'pound'); } }
      return P.kos > tut.kos0 || P.flatted > tut.flat0; } },
  { id: 'dodge', max: 60, enter() { tut.noPound = true; Object.assign(TUT_AI, TUT_AI_FIGHT); tut.drive = H; tut.driveMode = 'fight'; H.slamCD = 0; if (H.paint < 0.8) H.paint = 1; if (H.ai) { H.ai.plan = null; H.ai.path = null; } tut.rolled = false; tut.hits = 0; tut.wasKo = false; tut.slowK = 1; tut.sub = ''; tutShow(say('Rivals pound too. Swipe up just before it lands to dodge', 'Rivals pound too. Shift just before it lands to dodge'), null, 'dodge', false, true); },
    tick(dt) { if (!H.slam && P.st === 'play') tutRivalIn(6.5); if (H.st === 'play' && !H.slam && H.slamCD > 1.2) H.slamCD = 1.2; if (H.paint < 0.5) H.paint = 1;
      const d = Math.hypot(H.x - P.x, H.z - P.z), eta = H.slam ? H.slamEta - H.slamT : 9, coming = H.slam && H.st === 'play' && P.st === 'play' && !P.air && d < slamRadius(H) + PR + 2.5;
      if (coming && P.rollT <= 0 && !tut.rolled) P.rollCD = 0; /* (an early swipe never leaves you without a roll for the drop) */
      if (coming && P.rollT > 0 && !tut.rolled) { tut.rolled = true; tut.rollRT = 0; } // (a roll while its pound is in the air: that is the timing)
      if (tut.rolled) tut.rollRT = (tut.rollRT || 0) + (dt || 0) / Math.max(tut.slowK, 0.05); /* (real seconds since the swipe) */
      if (tut.rolled && H.slam && P.rollT > 0 && P.rollT < 0.05) P.rollT = 0.05; /* (and it holds you clear till the pound lands) */
      if (P.st === 'ko' && !tut.wasKo) tut.hits++; tut.wasKo = P.st === 'ko';
      const now = coming && eta < 0.42, base = now ? 0.14 : coming ? 0.45 : 1, back = tut.rolled ? Math.min(1, Math.max(0, (tut.rollRT - 1) / 0.25)) : 0; tut.slowK = base + (1 - base) * back; /* (swiped clear: a second more, then back to speed) */
      const sub = now ? 'now' : 'dodge'; if (sub !== tut.sub) { tut.sub = sub; if (now) tutShow(say('*NOW!* Swipe up!', '*NOW!* Shift!'), null, 'dodgenow', true, true); else tutShow(say('Rivals pound too. Swipe up just before it lands to dodge', 'Rivals pound too. Shift just before it lands to dodge'), null, 'dodge', false, true); }
      return (tut.rolled || tut.hits >= 2) && P.st === 'play' && !H.slam; },
    exit() { Object.assign(TUT_AI, TUT_AI_CALM); tut.drive = null; tut.noPound = false; } },
  { id: 'orb', max: 55, enter() { orb.spawnT = 0; tut.orbMine = true; tut.hadRocket = false; tut.slowK = 1; tutShow('A special orb! Roll up to it for a super move', null, 'orb', false, true); },
    tick() { if (P.rocket && !tut.hadRocket) { tut.hadRocket = true; tut.slowK = 1; /* (full speed: the rocket ride is the fun part) */ tutShow(say('Steer over the rival, then tap Boost', 'Steer over the rival, then press E to boost'), 'slamBtn', 'rocket'); }
      const cross = !!P.rocket; if (cross && tut.driveMode !== 'cross') { tut.drive = H; tut.driveMode = 'cross'; if (H.ai) { H.ai.plan = null; H.ai.path = null; } } else if (!cross && tut.driveMode === 'cross') { tut.drive = null; tut.driveMode = null; TUT_AI.speed = 0.8; } /* (the rival walks into your crosshair) */
      return tut.hadRocket && !P.rocket; },
    exit() { tut.orbMine = false; TUT_AI.orb = 0.35; } },
"""

HELPERS = r"""// (v357) the rival's entrance. Where: a few strides off (8 to 11 m, so he comes out about 6 m from you), as near dead ahead as there's
// room, on level clear floor, with the shot's spot on your side of it clear. A basin that's down comes up there (turned so he climbs out
// on your side, away from its dispenser) with him already in it, and the view cuts to it: the bars come in and the controls go
const RV_CAM = [5.4, 1.5, 1.9, 7.6]; // (the shot: how far out from the basin on your side, how far off to one side, how high, and how far
// it may ease back to keep him in the picture as he climbs out toward it)
function tutRivalUp() {
  const lvl = (x, z, y0) => { const y = surfaceUnder(x, z, y0 + 0.5); return Math.abs(y - y0) < 0.05 ? y : null; }; let S = null;
  for (const d of [9, 10, 8.5, 11, 8]) { for (const da of [0, 0.3, -0.3, 0.6, -0.6, 0.9, -0.9, 1.25, -1.25, 1.6, -1.6, 2, -2, 2.5, -2.5, 3.1]) {
      const a = P.yaw + da, x = P.x + Math.sin(a) * d, z = P.z + Math.cos(a) * d; if (Math.abs(x) > ARENA - 3 || Math.abs(z) > ARENA - 3) continue;
      const y = lvl(x, z, P.y); if (y === null || !NAV.at(x, z, y) || blockedAt(x, z, y)) continue;
      let ok = true; for (let k = 0; k < 12 && ok; k++) { const b = k * 0.5236; for (const r of [1.1, 2.4]) { const xx = x + Math.cos(b) * r, zz = z + Math.sin(b) * r; if (lvl(xx, zz, y) === null || blockedAt(xx, zz, y)) ok = false; } } if (!ok) continue;
      if (pots.some(o => o.g.visible && Math.hypot(o.x - x, o.z - z) < 3.5) || rivals.some(r => Math.hypot(r.x - x, r.z - z) < r.rad + 2) || powers.some(w => Math.hypot(w.x - x, w.z - z) < 2.5)) continue;
      const fx = (P.x - x) / d, fz = (P.z - z) / d; let side = 0;
      const dm = Math.min(RV_CAM[3], d - 1.2); // (the furthest back the shot goes: still in front of you)
      for (const sd of [1, -1]) { let clear = true; for (const cd of [RV_CAM[0], (RV_CAM[0] + dm) / 2, dm]) { /* (where it starts, and on its way back) */
          const cx = x + fx * cd + fz * sd * RV_CAM[1], cz = z + fz * cd - fx * sd * RV_CAM[1], cy = y + RV_CAM[2]; if (Math.abs(cx) > ARENA + 1 || Math.abs(cz) > ARENA + 1) { clear = false; break; }
          for (let k = 0; k <= 12 && clear; k++) { const t = k / 12; if (blockedAt(cx + (x - cx) * t, cz + (z - cz) * t, cy - 0.6 + (y + 0.6 - cy) * t)) clear = false; } if (!clear) break; }
        if (clear) { side = sd; break; } }
      if (side) { S = { x, y, z, fx, fz, side, dm }; break; } } if (S) break; }
  if (!S) return false;
  const q = pots.find(o => !o.occ && !o.g.visible && o !== tut.potQ) || pots.find(o => !o.occ && o !== P.pot && o !== tut.potQ); if (!q) return false;
  q.next = [S.x, S.y, S.z]; riseCoffin(q); q.st = 'up';
  if (q.inner) { q.g.rotation.y = 0; q.g.updateMatrixWorld(true); const b = q.inner.localToWorld(tv1.set(0, 0, -0.725)); q.g.rotation.y = wrapA(Math.atan2(-S.fx, -S.fz) - Math.atan2(b.x - q.x, b.z - q.z)); q.g.updateMatrixWorld(true); } // (its back, the dispenser, away from you)
  enterPot(H, q); q.lastOcc = H; q.paintC.copy(TEAM_COLS[H.team]); q.slosh = 1.2;
  Object.assign(H, { yaw: Math.atan2(S.fx, S.fz), steer: 0, turn: 0, spd: 0, paint: 1, dry: false, dryT: 0, immuneT: 9, flatT: 0, stunT: 0, kx: 0, kz: 0, knockT: 0, wearOff: true, peeked: true, introCrawl: null, introOut: false, introShake: null, ip: null });
  H.rimInfo = basinRim(q, S.fx, S.fz); { const V = vOf(H); if (V) { V.yawD = H.yaw; if (V.slime && V.slime.ax) V.slime.ax.fresh = true; } }
  if (H.ai) { H.ai.plan = null; H.ai.path = null; } LH.drop.visible = LH.shadow.visible = true; ACTIVE = [P, H];
  tut.rvPot = q; tut.rvCam = { x: S.x, y: S.y, z: S.z, fx: S.fx, fz: S.fz, side: S.side, dm: S.dm, d: RV_CAM[0], w: 0, t: 0 }; camSnap = true;
  if (!kcBarsEl.parentNode) stage.appendChild(kcBarsEl); kcBarsEl.classList.add('on'); hud.classList.add('kc'); document.body.classList.add('rvon'); AU.whoosh();
  return true;
}
// the end of the entrance (or of the step, cut short): the view back on you, turned to face him, the controls back. With no room found for
// the shot he simply arrives in front of you; cut short in his basin or mid-climb, he's out on the floor at once
function tutRevealEnd() {
  if (!tut) return; tut.hold = false; tutRevealOff();
  if (H.st === 'out') { H.st = 'play'; H.paint = 1; H.immuneT = 1; LH.drop.visible = LH.shadow.visible = true; ACTIVE = [P, H]; if (H.ai) { H.ai.plan = null; H.ai.path = null; } tutRivalIn(7); }
  if (H.st === 'hide' && H.pot && H.pot === tut.rvPot) exitPot(H);
  if (H.introCrawl) { const C = H.introCrawl; H.x = C.cx + C.fx * C.s1; H.z = C.cz + C.fz * C.s1; H.introCrawl = null; H.spd = 0; }
  if (H.introOut) { H.introOut = false; H.introShake = null; H.ip = null; }
  H.spawnGuard = 2.4; H.immuneT = Math.min(H.immuneT || 0, 0.8);
  if (P.st === 'play' && H.st !== 'out') { P.yaw = Math.atan2(H.x - P.x, H.z - P.z); P.turn = 0; const V = vOf(P); if (V) V.yawD = P.yaw; }
  camYaw = P.yaw; camYawV = 0; camSnap = true;
}
function tutRevealOff() { if (tut) tut.rvCam = null; kcBarsEl.classList.remove('on'); hud.classList.remove('kc'); document.body.classList.remove('rvon'); }
"""

TAP_CSS = """.tutgest[data-g="tap"]{top:70%} /* (v357: a tap, for jumping out of a basin) */
.tutgest[data-g="tap"] .ghand{animation:gtap 1.3s ease-in-out infinite}
.tutgest[data-g="tap"] .gring{animation:gtapr 1.3s ease-out infinite}
@keyframes gtap{0%,100%{transform:translateY(-14px)}30%,46%{transform:translateY(0) scale(.88)}}
@keyframes gtapr{0%,30%{opacity:0;transform:scale(.4)}36%{opacity:1;transform:scale(.6)}70%,100%{opacity:0;transform:scale(1.7)}}
body.rvon .corner{opacity:0;pointer-events:none} /* (v357: the rival's entrance in the lesson: nothing over the shot) */"""

def apply(s):
    # ---- the steps: after the sling, the refill, the rival's entrance, the pound, the dodge and the orb (v356's own pound, the Roller, its
    # orb, the gap and the gift go)
    s = cut(s, "  // (v356) the pound, on your own: once you're down from the fling", "  { id: 'rest', max: 1e9,", STEPS)
    s = rep(s, "const TW_LIST = ['Steering and jumping', 'Flinging', 'The pound', 'Transforms', 'The orb', 'Finding items'];",
               "const TW_LIST = ['Steering and jumping', 'Flinging', 'Refilling', 'The pound', 'Dodging', 'The orb'];")
    # ---- the entrance's helpers, after the refill basin's own
    s = rep(s, "// where to point in the basin lesson: its own basin (or the mark it is coming up on), else the nearest one\n",
               HELPERS + "// where to point in the basin lesson: its own basin (or the mark it is coming up on), else the nearest one\n")
    # ---- the refill basin: in this lesson the basins are all down, so any free one will do; and it's let up (the rest stay down)
    s = rep(s, "  let q = null, bd = -1; for (const o of pots) { if (o.st !== 'up' || o.occ) continue; const d = Math.hypot(o.x - P.x, o.z - P.z); if (d > bd) { bd = d; q = o; } }",
               "  let q = null, bd = -1; for (const o of pots) { if (o.occ || o === P.pot) continue; const d = o.st === 'down' ? 1e9 : Math.hypot(o.x - P.x, o.z - P.z); if (d > bd) { bd = d; q = o; } } // (v357: one that's down first)")
    s = rep(s, "  q.st = 'down'; q.g.visible = false; if (q.ring) q.ring.visible = false; q.occ = null; q.next = spot; q.t = DOWN_T - 0.6;",
               "  q.st = 'down'; q.g.visible = false; if (q.ring) q.ring.visible = false; q.occ = null; q.next = spot; q.t = DOWN_T - 0.6; q.tutRise = true;")
    s = rep(s, "return !pots.some(o => Math.hypot(o.x - x, o.z - z) < 3) && !rivals.some(r => Math.hypot(r.x - x, r.z - z) < r.rad + 1.6)",
               "return !pots.some(o => o.g.visible && Math.hypot(o.x - x, o.z - z) < 3) && !rivals.some(r => Math.hypot(r.x - x, r.z - z) < r.rad + 1.6)")
    s = rep(s, "  for (const pass of [0, 1]) { for (const d of pass ? [9.5, 8.5, 7.5, 6.5, 5.5, 5, 4.5] : [9.5, 10.5, 8.5, 11.5, 7.5, 6.5]) { for (const da of [0, 0.25, -0.25, 0.5, -0.5, 0.8, -0.8]) {",
               "  for (const pass of [0, 1, 2]) { for (const d of pass ? [9.5, 8.5, 7.5, 6.5, 5.5, 5, 4.5] : [9.5, 10.5, 8.5, 11.5, 7.5, 6.5]) { for (const da of pass > 1 ? [1.1, -1.1, 1.5, -1.5, 2, -2, 2.5, -2.5, 3.1] : [0, 0.25, -0.25, 0.5, -0.5, 0.8, -0.8]) { /* (v357: no room ahead, beside or behind you) */")
    s = rep(s, "    if (p.st === 'down' && tut && tutFlat) continue;", "    if (p.st === 'down' && tut && tutFlat && !p.tutRise) continue;")
    s = rep(s, "  p.st = 'rise'; p.t = 0; p.g.visible = true; p.tele.visible = false; p.bounce = 0;",
               "  p.st = 'rise'; p.t = 0; p.g.visible = true; p.tele.visible = false; p.bounce = 0; p.tutRise = false;")
    # ---- the lesson's tanks and basins
    s = rep(s, "  if (tutFlat) { if (P.st === 'play') P.paint = 1; /* (v356: no basins, so the tank stays full) */ if (P.st === 'play') for (const p of pots) if (potUp(p) && Math.hypot(p.x - P.x, p.z - P.z) > 3.2) sinkCoffin(p); } // (and a basin you're out of goes: the one you start in, or one you came back in)\n",
               "  if (tutFlat) { const sid = tut.step >= 0 ? TUT_STEPS[tut.step].id : ''; // (v357)\n"
               "    if (P.st === 'play' && sid !== 'basin') P.paint = 1; /* (your tank stays full but for the refill lesson) */ if (H.st === 'play' && H.paint < 0.6) H.paint = 1; /* (and his: there are no basins to go back to) */\n"
               "    for (const p of pots) if (potUp(p) && !p.occ && p !== tut.potQ && Math.hypot(p.x - P.x, p.z - P.z) > 3.2 && !(H.st === 'play' && Math.hypot(p.x - H.x, p.z - H.z) < 3.2)) sinkCoffin(p); } // (a basin nobody's in or near goes: the one you start in, the refill, his, one either of you came back in)\n")
    # (in a basin in the entrance step, that step does the talking: "TAP to jump out!", not the swipe callout)
    s = rep(s, "const inTub = P.st === 'hide' && !(s.id === 'basin' && tut.basinTip) && s.id !== 'rest'",
               "const inTub = P.st === 'hide' && !(s.id === 'basin' && tut.basinTip) && s.id !== 'rival' && s.id !== 'rest'")
    # ---- held still for the entrance: no steering, no moves, the roll eased to a stop
    s = rep(s, "const canAct = D => D.st === 'play' && D.flatT <= 0 && !(D.stunT > 0) && !D.rocket && !D.turret && !D.whirl;",
               "const canAct = D => D.st === 'play' && D.flatT <= 0 && !(D.stunT > 0) && !D.rocket && !D.turret && !D.whirl && !(D === P && tut && tut.hold); // (v357: tut.hold, the lesson's rival entrance)")
    s = rep(s, "  if (D === P && kcam && kcam.yaw !== undefined && D.st === 'play') { input = kcamSteer(D, dt);",
               "  if (D === P && tut && tut.hold) input = 0; // (v357: held still while the rival comes in)\n"
               "  if (D === P && kcam && kcam.yaw !== undefined && D.st === 'play') { input = kcamSteer(D, dt);")
    s = rep(s, "  else if ((D.slam && !D.missile) || D.flatT > 0 || D.stunT > 0) D.spd = 0;",
               "  else if (D === P && tut && tut.hold && !D.air) D.spd *= Math.exp(-dt * 9); // (v357: eased to a stop for the rival's entrance)\n"
               "  else if ((D.slam && !D.missile) || D.flatT > 0 || D.stunT > 0) D.spd = 0;")
    # ---- his climb out, in play: driven here as the intro drives it at a match's start (never set in play otherwise), with no mind of his own
    # meanwhile, nor in his basin before it
    s = rep(s, "  if (D.st === 'out') return;\n",
               "  if (D.st === 'out') return;\n"
               "  if (state === 'play' && (D.introCrawl || D.introOut)) { if (D.introCrawl) crawlOut(D, dt); else D.spd = 0; return; } // (v357: the lesson's rival climbing out of his basin)\n")
    s = rep(s, "  const ai = D.ai; if (!ai || D.st === 'out') return;",
               "  const ai = D.ai; if (!ai || D.st === 'out' || D.introCrawl || D.introOut || (D === H && tut && tut.rvCam)) return; // (v357: not while the lesson's rival makes his entrance)")
    # ---- the entrance's shot: from your side of his basin, easing back as he climbs out toward it
    s = rep(s, "  else if (state === 'play' && spec && P.st === 'out' && specCam(rdt)) {}",
               "  else if (state === 'play' && tut && tut.rvCam) { // (v357) the lesson's rival entrance\n"
               "    const R = tut.rvCam; R.t += rdt; const u = smoothstep(0, 3.5, R.t), nx = R.fz * R.side, nz = -R.fx * R.side, out = H.st === 'play', k = 1 - Math.exp(-rdt * 2.4);\n"
               "    const sH = out ? (H.x - R.x) * R.fx + (H.z - R.z) * R.fz : 0; R.d += (Math.min(R.dm, Math.max(RV_CAM[0] + 0.5 * u, sH + 4.4)) - R.d) * k; R.w += ((out ? 0.75 : 0) - R.w) * k; // (out and coming your way: it eases back and turns with him)\n"
               "    dPos.set(R.x + R.fx * R.d + nx * RV_CAM[1], R.y + RV_CAM[2] + 0.15 * u, R.z + R.fz * R.d + nz * RV_CAM[1]); dLook.set(R.x + (H.x - R.x) * R.w, R.y + 0.55, R.z + (H.z - R.z) * R.w);\n"
               "  }\n"
               "  else if (state === 'play' && spec && P.st === 'out' && specCam(rdt)) {}")
    # ---- leaving the lesson any way at all: no bars or hidden controls left behind
    s = rep(s, "function tutLeave() { clearTimeout(tutPraiseEl._t0);", "function tutLeave() { tutRevealOff(); clearTimeout(tutPraiseEl._t0);")
    # ---- a tap for the finger to show
    s = rep(s, "const TUT_GEST = { tubout: 'swipe',", "const TUT_GEST = { jumpout: 'tap', tubout: 'swipe',")
    s = rep(s, '.tutgest[data-g="pull"]{top:74%;left:62%}', '.tutgest[data-g="pull"]{top:74%;left:62%}\n' + TAP_CSS)
    # ---- a swipe up to roll into a basin that lands once you're already in it no longer rolls you straight back out: a flick that began
    # before you got in, in the moment you got in, is spent (anywhere, not just in the lesson). One begun in the basin rolls you out as ever
    s = rep(s, "if (D === P) { AU.enter(); buzz(10);", "if (D === P) { D.potAt = performance.now(); AU.enter(); buzz(10);")
    s = rep(s, "if (up > 44 && up > side * 1.5) { t.rolled = true; t.moved = true; t.steered = true; dodgeRoll(P); }",
               "if (up > 44 && up > side * 1.5) { t.rolled = true; t.moved = true; t.steered = true; if (!(P.st === 'hide' && h0[2] < (P.potAt || 0) && now - P.potAt < 350)) dodgeRoll(P); }")
    # ---- the entrance held sideways: a longer lens (the view's height is all the shot has there, so at the same lens he'd be half the
    # size he is upright), in and out with the cuts rather than a zoom
    s = rep(s, "  const fovT = state === 'menu' ? heroFov() : (playing ? playFov : baseFov)",
               "  const rvL = state === 'play' && !!tut && !!tut.rvCam && viewW > viewH; // (v357: the rival's entrance, sideways)\n"
               "  const fovT = rvL ? playFov * 0.62 : state === 'menu' ? heroFov() : (playing ? playFov : baseFov)")
    s = rep(s, "  if (Math.abs(camera.fov - fovT) > 0.05) { camera.fov += (fovT - camera.fov) * Math.min(1, rdt * 6); camera.updateProjectionMatrix(); }",
               "  if (rvL !== camRvL) { camRvL = rvL; camera.fov = fovT; camera.updateProjectionMatrix(); }\n"
               "  if (Math.abs(camera.fov - fovT) > 0.05) { camera.fov += (fovT - camera.fov) * Math.min(1, rdt * 6); camera.updateProjectionMatrix(); }")
    s = rep(s, "let baseFov = 70, playFov = 64;", "let baseFov = 70, playFov = 64, camRvL = false;")
    # ---- in a basin a tap held a touch too long (over 0.15 s, when a press turns into aiming a fling) is still a tap: let go without
    # pulling and out you hop, as "TAP to jump out!" says. A longer press let go without a pull still does nothing
    s = rep(s, "if (P.charging && holdCharge) { if (pullTgt >= FLING_MIN) fling(P, pullTgt); else cancelCharge(P); }",
               "if (P.charging && holdCharge) { if (pullTgt >= FLING_MIN) fling(P, pullTgt); else { cancelCharge(P); if (P.st === 'hide' && !t.moved && performance.now() - t.t < 450 && state === 'play') jump(P); } }")
    return s
