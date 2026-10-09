  const NO_SHUT = { glee: 1, hurt: 1, yawn: 1, dizzy: 1, brace: 1 }, ZERO3 = [0, 0, 0], PUP_C = {}, TUR_W = { yaw: 0, pitch: 0 };
  const clampS = (v, a, b) => v < a ? a : v > b ? b : v;
  // each frame. o: { dt, spd 0..1, lean -1..1, air 0..1 (eased), inAir, vy, height (above the ground), drop 0..1, squash, rise, wob,
  // pos [x, y, z] (world), yaw (the root's), look [x, y] or null, aimPitch, speed (units/s), rad (the body's scale), idle (a calm moment),
  // shove -1..1 (leaning itself over to one side, + to its right) and push -1..1 (the stub on the far side doing it, + its left one),
  // brace 0..1 (the ground coming up: it reaches down for it), wall 0..1 (about to run into something), flail 0..1 (tumbling, knocked
  // flying), curl 0..1 (tucked into a ball for a roll) }
  function update(I, o) {
    const dt = Math.min(0.05, o.dt || 0), s = I.st, U = I.U; s.t += dt;
    U.sT.value = s.t;
    // how it's moving in the world, in its own facing: x to its left, z ahead (from where it was last frame; a frozen frame changes nothing)
    const pos = o.pos || ZERO3, yaw = o.yaw || 0, pp = s.pp, vel = s.vel, acc = s.acc;
    if (!s.ppOk || Math.abs(pos[0] - pp[0]) + Math.abs(pos[1] - pp[1]) + Math.abs(pos[2] - pp[2]) > 3) { for (let i = 0; i < 3; i++) { pp[i] = pos[i]; vel[i] = 0; acc[i] = 0; } s.pyaw = yaw; s.yawV = 0; s.ppOk = true; }
    else if (dt > 0) {
      const kA = Math.min(1, dt * 14);
      for (let i = 0; i < 3; i++) { const v = (pos[i] - pp[i]) / dt; acc[i] += ((v - vel[i]) / dt - acc[i]) * kA; vel[i] = v; pp[i] = pos[i]; }
      let dy = yaw - s.pyaw; while (dy > Math.PI) dy -= 2 * Math.PI; while (dy < -Math.PI) dy += 2 * Math.PI; s.yawV += (dy / dt - s.yawV) * Math.min(1, dt * 12); s.pyaw = yaw;
    }
    const cy = Math.cos(yaw), sy = Math.sin(yaw), lax = acc[0] * cy - acc[2] * sy, laz = acc[0] * sy + acc[2] * cy, lvz = vel[0] * sy + vel[2] * cy, ay = acc[1];
    const spd = o.spd || 0, inAir = !!o.inAir, vy = o.vy || 0, idle = spd < 0.05 && !inAir, slug = I.form === 'slime';
    // ---- in the air: how long it's been up. Landing slaps the ears down, plants the stubs out flat, nods the head and carries the top on
    // over by as much as it was moving; then it all rocks back ----
    if (inAir) { s.airT += dt; s.lvy = vy; }
    else {
      if (s.wasAir && s.airT > 0.12) { const imp = Math.min(1, Math.max(0, -s.lvy) / 9);
        s.earKick = Math.max(s.earKick, 0.6 + 0.5 * imp);
        if (slug) { s.splat = Math.max(s.splat, 0.35 + 0.65 * Math.max(imp, s.brace)); s.bpV += clampS(lvz * 0.32, -3, 3) * (0.45 + 0.55 * imp); s.headV[1] -= 2 + 3 * imp; } }
      s.airT = 0;
    }
    s.wasAir = inAir;
    const h = o.height === undefined ? 9 : o.height;
    // (hovering in the countdown before a match it stays balled up; a roll tucks it into a ball, quickly, and it pops open after)
    const curl = slug ? (o.curl || 0) : 0, ballT = (o.hover && slug) || curl > 0.5 ? 1 : 0;
    // ---- the leap: going up it stretches out, head up and looking up, ears flung out and back, stubs reaching ahead, its body tipped up with
    // the tail trailing; coming down it tips forward and looks down at where it'll land; tipped less the nearer the ground ----
    const leapT = o.leap && slug && !o.hover ? 1 : 0, upK = ss(-2.5, 2.5, vy);
    s.leap += (leapT - s.leap) * Math.min(1, dt * (leapT > s.leap ? 12 : 18));
    const tipT = slug ? s.leap * Math.min(1, Math.max(0, h - 0.05) / 0.6) * (-0.22 + 0.6 * upK) : 0;
    s.tip += (tipT - s.tip) * Math.min(1, dt * 10); I.groups.slime.rotation.x = -s.tip;
    if (o.hover && slug) s.ball = 1;
    s.ball += (ballT - s.ball) * Math.min(1, dt * (ballT > s.ball ? (curl > 0.5 ? 26 : 7) : inAir ? 12 : s.slowT > 0 ? 5 : 22)); s.slowT = Math.max(0, s.slowT - dt);
    // (it builds just after leaving the ground and fades over a third of a second; never more than the height it has, so the tail can't dig in)
    s.tuck += ((inAir && vy > 0 && !slug ? ss(0, 0.05, s.airT) * Math.exp(-s.airT * 6.5) * Math.min(1, h / 0.4) : 0) - s.tuck) * Math.min(1, dt * 30);
    // ---- creeping: the squeeze wave runs faster the faster it goes, and the body curves along the arc of a turn ----
    s.ph = (s.ph + dt * (1.5 + 11 * spd)) % 6283.2;
    const bendT = !slug ? 0 : Math.max(-2.0, Math.min(2.0, s.yawV / Math.max(1.2, Math.abs(o.speed || 0)))) * 0.55 * (inAir ? 1 - s.ball : 1);
    s.bend += (bendT - s.bend) * Math.min(1, dt * 5);
    // how hard it slithers: a full snake's S at speed, less creeping slowly; none standing still (the tail rests) or in the air (balled up)
    const slT = slug && !inAir && !idle ? 0.35 + 0.65 * ss(0.02, 0.4, spd) : 0; s.slither += (slT - s.slither) * Math.min(1, dt * 4);
    U.sWave.value.set(s.ph, inAir || !slug ? 0 : spd, slug ? s.tuck : 0, s.slither * (1 - s.ball));
    // ---- crawling: its head and the top of its body push out ahead and draw back in, the stubs reaching out and pulling it along, a beat
    // for each pull; quicker and bigger the faster it goes, none standing still, in the air or balled up ----
    const gT = slug && !inAir && s.ball < 0.3 ? ss(0.03, 0.55, spd) : 0; s.gamp += (gT - s.gamp) * Math.min(1, dt * (gT > s.gamp ? 9 : 6));
    s.gph = (s.gph + dt * 6.2832 * (1.3 + 2.5 * Math.min(1.3, spd))) % 6.2832;
    // ---- reactions: bracing as the ground comes up (or a wall), planted flat as it lands, flailing in a tumble, pushing off ----
    const brT = slug ? (o.brace || 0) : 0, wlT = slug ? (o.wall || 0) : 0;
    s.brace += (brT - s.brace) * Math.min(1, dt * (brT > s.brace ? 18 : 7)); s.wallK = (s.wallK || 0) + (wlT - (s.wallK || 0)) * Math.min(1, dt * (wlT > (s.wallK || 0) ? 20 : 6));
    s.splat = Math.max(0, s.splat - dt * (inAir ? 9 : 3.2));
    const flT = slug ? (o.flail || 0) : 0; s.flail += (flT - s.flail) * Math.min(1, dt * (flT > s.flail ? 16 : 5)); s.flailK = Math.max(0, s.flailK - dt * 2.6);
    const flk = Math.min(1, Math.max(s.flail, s.flailK)) * (1 - s.ball), brk = Math.max(s.brace, s.wallK) * (1 - s.ball);
    s.flPh = (s.flPh + dt * (12 + 10 * flk)) % 6283.2; s.pushK = Math.max(0, s.pushK - dt * 6.5);
    U.sReact.value.set(s.splat > 0.02 ? -s.splat * (1 - s.ball) : brk, flk, s.flPh, s.pushK * (1 - s.ball));
    // ---- the stubs: fidgeting when it's still, paddling while it creeps, tucked away in the air (and held still while they're busy) ----
    s.stubPh = (s.stubPh + dt * (idle ? 2.3 + Math.sin(s.t * 0.4) * 0.8 : 5 + 9 * spd)) % 6283.2;
    U.sBall.value.set(s.ball, s.bend, s.stubPh, (inAir ? 0.1 : idle ? 0.75 + 0.25 * Math.sin(s.t * 0.9) : (0.55 + 0.45 * spd) * (1 - 0.65 * s.gamp)) * (1 - 0.8 * Math.max(brk, flk, Math.min(1, s.splat * 1.5))));
    // ---- the body's sway over its base: a soft spring. It leans into a speed-up and back as it brakes, the top carries on over as it lands,
    // a knock throws it over; it rocks past and settles, as a jelly does ----
    if (slug) {
      const tP = inAir ? 0 : clampS(laz * 0.006, -0.12, 0.1) * (1 - s.ball);
      s.bpV += ((tP - s.bp) * 125 - s.bpV * 7.5) * dt; s.bp += s.bpV * dt; s.brV += (-s.br * 125 - s.brV * 7.5) * dt; s.br += s.brV * dt;
      if (s.bp > 0.55) { s.bp = 0.55; if (s.bpV > 0) s.bpV *= -0.3; } else if (s.bp < -0.55) { s.bp = -0.55; if (s.bpV < 0) s.bpV *= -0.3; }
      if (s.br > 0.55) { s.br = 0.55; if (s.brV > 0) s.brV *= -0.3; } else if (s.br < -0.55) { s.br = -0.55; if (s.brV < 0) s.brV *= -0.3; }
    } else s.bp = s.bpV = s.br = s.brV = 0;
    U.sTilt.value.set(s.bp, 0, 0, 0);
    // shoving itself side to side (the game's wiggle): the body leans over from the ground up (its base stays put), the stub on the far side
    // doing the pushing
    const shv = o.shove || 0;
    U.sMove.value.set(spd, s.ph, (o.lean || 0) - shv * 0.9 + s.br / 0.14, slug ? s.leap * (1 - 0.75 * s.pushK) : 0);
    // squash and stretch, eased off while it's balled up (the ball keeps its shape); a sudden stop rocks it forward and back, setting off
    // from still it pushes off with its stubs
    { const ps = s.pSpd < 0 ? spd : s.pSpd; if (!inAir && slug) { if (ps > 0.42 && spd < 0.1) { s.setV += 7.5; s.blinkK = Math.max(s.blinkK, 0.09); } else if (ps < 0.05 && spd > 0.18) { s.setV -= 4.5; s.pushK = Math.max(s.pushK, 0.7); } }
      s.pSpd = spd; s.setV += (-s.setX * 210 - s.setV * 13) * dt; s.setX += s.setV * dt; }
    const bk = 1 - 0.6 * s.ball, sq = (o.squash || 0) + clampS(s.setX * 0.9, -0.12, 0.3), ri = ((o.rise || 0) + 0.08 * flk) * bk; U.sShape.value.set(sq, ri, (o.drop || 0) * (1 - 0.8 * s.ball), o.wob === undefined ? 1 : o.wob);
    // ---- where it's looking: now and then a new glance (the eyes get there first, the head follows), into turns while it moves ----
    const A = s.att; A.t -= dt;
    if (A.t <= 0) { A.t = 1.2 + Math.random() * 2.8; const r = Math.random(); if (r < 0.3) { A.yaw = 0; A.pit = 0.02; } else { A.yaw = (Math.random() * 2 - 1) * 0.55; A.pit = (Math.random() * 2 - 1) * 0.12; } A.eye[0] = A.yaw * 0.22; A.eye[1] = A.pit * 0.3; }
    const calm = idle ? 1 : 0.25;
    if (I.form === 'turret' && !o.watch) { TUR_W.yaw = 0.025 * Math.sin(s.t * 1.3); TUR_W.pitch = 0.02 * Math.sin(s.t * 2.1 + 1); }
    const W = o.watch || (I.form === 'turret' ? TUR_W : null), lead = clampS(s.yawV * 0.06, -0.45, 0.45) * (1 - s.ball);
    const yawT = W ? W.yaw : (-(o.lean || 0) * 0.3 + A.yaw * calm) * (1 - s.ball) + lead,
      pitT = (W ? W.pitch : 0.08 * ri - 0.12 * (o.drop || 0) + A.pit * calm - 0.25 * s.ball + s.leap * (-0.45 + 0.75 * upK) - Math.max(0, s.setX) * 0.55) - 0.14 * s.brace - 0.1 * s.wallK,
      rolT = W ? 0 : (o.lean || 0) * 0.1 + A.yaw * calm * -0.12 + lead * 0.25 - shv * 0.07;
    const H = s.head, HV = s.headV;
    HV[0] += ((yawT - H[0]) * 38 - HV[0] * 9) * dt; H[0] += HV[0] * dt;
    HV[1] += ((pitT - H[1]) * 38 - HV[1] * 9) * dt; H[1] += HV[1] * dt;
    HV[2] += ((rolT - H[2]) * 38 - HV[2] * 9) * dt; H[2] += HV[2] * dt;
    // on top of the spring: a tumble's head lolling loose, and the quick shake of the head coming round after it
    let shkY = 0; if (s.shk > 0) { s.shkT += dt; const u = s.shkT / 0.5; if (u >= 1) s.shk = 0; else shkY = Math.sin(s.shkT * 44) * 0.36 * s.shk * Math.min(1, u * 6) * (1 - u) * (1 - u); }
    const HD = s.hd || (s.hd = [0, 0, 0]);
    HD[0] = H[0] + shkY + flk * 0.26 * Math.sin(s.flPh * 0.61); HD[1] = H[1] - flk * (0.08 + 0.1 * Math.sin(s.flPh * 0.83)); HD[2] = H[2] + flk * 0.24 * Math.sin(s.flPh * 0.47 + 1.1) + shkY * 0.3;
    const br = 0.014 * Math.sin(s.t * 2.2) + 0.006 * Math.sin(s.t * 3.9 + 1.3);
    U.sHead.value.set(HD[0], HD[1], HD[2], br * (1 - s.ball));
    // ---- the ears: floppy weights on springs. They hang by the face; moving pulls them back, any lurch swings them the other way, a turn of
    // the head leaves them lagging, falling lets them float up and out, a landing slaps them down and they bounce. Now and then one twitches.
    // Bracing for the ground they flare up; about to hit a wall they pin back; tumbling they fling about ----
    const gr = o.grav || 9.8, gEff = Math.max(-0.5, Math.min(2.5, 1 + ay / gr)), kick = s.earKick; s.earKick = 0;
    s.twitch -= dt; let tw = 0, twSide = 0; if (s.twitch <= 0) { s.twitch = 2.5 + Math.random() * 5; if (idle) { tw = 1; twSide = Math.random() < 0.5 ? -1 : 1; } }
    s.flkT -= dt; let fkick = 0; if (flk > 0.25 && s.flkT <= 0) { s.flkT = 0.07 + Math.random() * 0.08; fkick = flk; if (slug) s.flV += (Math.random() < 0.5 ? -1 : 1) * 10 * flk; }
    const hv0 = HV[0] + (shkY !== 0 ? Math.cos(s.shkT * 44) * 44 * 0.36 * s.shk * (1 - s.shkT / 0.5) : 0);
    for (let i = 0; i < 2; i++) { const e = i ? s.earR : s.earL, sd = i ? 1 : -1;
      const out = -lax * sd * 0.022, back = -laz * 0.02 - Math.max(0, lvz) * 0.05, hl = -hv0 * sd * 0.35, spin = Math.abs(s.yawV) * 0.06;
      const float = (1 - Math.min(1, gEff)) * 0.75, ballWrap = s.ball * 0.25;
      const fT = clampS(EAR_REST.f * Math.max(0.4, gEff) + float + out + hl + spin + ballWrap + s.leap * 0.9 * (0.12 + 0.88 * upK) + 0.45 * s.brace + 0.7 * flk - 0.2 * s.wallK, -0.75, 1.5),
        sT = clampS(EAR_REST.s + back - float * 0.3 - s.ball * 0.4 - s.leap * 0.26 * upK - 0.6 * s.wallK + 0.12 * s.brace, -1.1, 0.8);
      if (kick) { e[1] -= kick * 5 * (0.8 + 0.4 * Math.random()); e[3] -= kick * 2.5; }
      if (fkick) { e[1] += (Math.random() * 2 - 1) * 7 * fkick; e[3] += (Math.random() * 2 - 1) * 5 * fkick; }
      if (tw && sd === twSide) e[1] += 6;
      e[1] += ((fT - e[0]) * 70 - e[1] * 4.2) * dt; e[0] += e[1] * dt; e[3] += ((sT - e[2]) * 55 - e[3] * 3.8) * dt; e[2] += e[3] * dt;
      e[0] = Math.max(-0.9, Math.min(1.7, e[0])); e[2] = Math.max(-1.3, Math.min(1.0, e[2]));
    }
    U.sEar.value.set(s.earL[0], s.earL[2], s.earR[0], s.earR[2]);
    // ---- the face: crossfade between expressions, blink now and then, pupils easing toward where it looks ----
    if (s.exprK < 1) { s.exprK = Math.min(1, s.exprK + dt / 0.12); if (s.exprK >= 1) s.expr = s.exprB; }
    if (s.flut > 0) { s.flutT -= dt; if (s.flutT <= 0) { s.blinkK = 0.075; s.flut--; s.flutT = 0.15; s.blinkT = Math.max(s.blinkT, 1.4); } }
    s.tbCool -= dt; if (Math.abs(s.yawV) > 3.2 && s.tbCool <= 0 && !inAir) { s.blinkK = Math.max(s.blinkK, 0.11); s.tbCool = 1.4; }
    s.blinkT -= dt; if (s.blinkT <= 0) { s.blinkK = 0.13; s.blinkT = Math.random() < 0.22 ? 0.26 : 1.6 + Math.random() * 3.4; } if (s.blinkK > 0) s.blinkK -= dt;
    s.dartT -= dt; if (s.dartT <= 0) { s.dartT = 0.35 + Math.random() * 0.9; s.dart[0] = idle ? (Math.random() * 2 - 1) * 0.035 : 0; s.dart[1] = idle ? (Math.random() * 2 - 1) * 0.02 : 0; }
    if (slug) {
      // the throat: two or three quick pumps every few seconds, mostly when it's still
      s.thrT -= dt * (idle ? 1 : 0.35);
      if (s.thrT <= 0) { s.thrT = 3.5 + Math.random() * 4.5; s.thrN = 2 + (Math.random() < 0.5 ? 1 : 0); s.thrU = 0; }
      let thr = 0; if (s.thrN > 0) { s.thrU += dt / 0.3; const u = s.thrU % 1; thr = Math.sin(u * Math.PI) * Math.sin(u * Math.PI); if (s.thrU >= s.thrN) s.thrN = 0; }
      // the tail's tip: a flick now and then as it goes (a spring that rings down); never while it's standing still
      s.flT -= dt * (idle ? 0 : 0.5);
      if (s.flT <= 0) { s.flT = 2 + Math.random() * 4; s.flV += (Math.random() < 0.5 ? -1 : 1) * (5 + Math.random() * 4); }
      s.flV += (-s.fl * 140 - s.flV * 7) * dt; s.fl += s.flV * dt;
      U.sMicro.value.set(thr * (1 - s.ball), s.fl * (1 - s.ball), (o.push || 0) * (1 - s.ball), s.gamp * (1 - s.ball));
    } else U.sMicro.value.set(0, 0, 0, 0);
    if (A.t > 1.0 && A.t < 1.08 && idle) s.blinkK = Math.max(s.blinkK, 0.1); // a blink with a new glance, as eyes do
    const shut = s.blinkK > 0 && !NO_SHUT[s.exprB], gl = o.look;
    const lt0 = (gl ? gl[0] : -(o.lean || 0) * 0.07) + (A.eye[0] + s.dart[0]) * calm, lt1 = (gl ? gl[1] : 0.02 * ri - 0.04 * (o.drop || 0)) + (A.eye[1] + s.dart[1]) * calm + s.leap * (-0.12 + 0.19 * upK) - 0.05 * s.brace; // (leaping: looking up, then down at the landing)
    s.look[0] += (lt0 - s.look[0]) * Math.min(1, dt * 26); s.look[1] += (lt1 - s.look[1]) * Math.min(1, dt * 26);
    const pa = pupilOf(s.expr), pb = pupilOf(s.exprB), k = s.exprK, fang = I.fangs ? 6 : 0;
    const ea = EXPR[s.expr], eb = EXPR[s.exprB], fm = ballForm(I) ? 'giantRoll' : I.form;
    U.fCells.value.set(ea[0], ea[1] + fang, eb[0], eb[1] + fang);
    U.fMix.value.set(k, shut ? 1 : 0, S.meta[fm].face[2], 6);
    U.fPupil.value.set(s.look[0], s.look[1], pa.pu + (pb.pu - pa.pu) * k, pa.py + (pb.py - pa.py) * k);
    // how much the head is still stretched (it gets only a little of the body's squash): the face is drawn back by all of it
    const HG = 0.18, sk = (0.25 * sq - 0.16 * ri - 0.12 * (o.drop || 0)) * HG; U.fComp.value.set(1 + sk, (1 - 1.5 * sk) * (1 - 0.06 * spd * HG), 0, 0);
