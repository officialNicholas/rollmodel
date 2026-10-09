import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:110])); sys.exit(1)
    s = s.replace(a, b)

# giant lasts 5 seconds
rep("const GIANT_T = 4, GIANT_K = 3, ORB_R = 0.42;", "const GIANT_T = 5, GIANT_K = 3, ORB_R = 0.42;")
rep("banner('The holy water went giant!', 'Keep away for 4 seconds.');", "banner('The holy water went giant!', 'Keep away for 5 seconds.');")
rep("to grow three times your size for 4 seconds, with a full blood meter", "to grow three times your size for 5 seconds, with a full blood meter")

# ---- jumping toward the orb carries you to it ----
rep("  D.air = true; D.vy = JUMP_V; D.stroke++; D.squash = 0; D.buf = 0; if (D === P) AU.jump();\n}",
    """  D.air = true; D.vy = JUMP_V; D.stroke++; D.squash = 0; D.buf = 0; if (D === P) AU.jump();
  if (!D.ai) orbJumpAssist(D);
}
// you jumped roughly toward the orb: turn you onto it and carry you there at the top of the hop
function orbJumpAssist(D) {
  if (!orb.on || orb.k < 0.5 || D.giantT > 0) return;
  const dx = orb.x - D.x, dz = orb.z - D.z, d = Math.hypot(dx, dz), up = orb.y - D.y; if (d > 5.5 || up > 2.3 || up < -0.3) return;
  const err = wrapA(Math.atan2(dx, dz) - D.yaw); if (Math.abs(err) > 0.8 && d > 1) return;
  D.yaw += err * 0.75; D.spd = clamp(d / 0.38, Math.min(D.spd, 1.5), 9.5); D.turn = 0;
}
// and in the air (a hop or a fling) it keeps pulling you onto it
function orbHome(D, dt) {
  const dx = orb.x - D.x, dz = orb.z - D.z, d = Math.hypot(dx, dz); if (d < 0.25 || d > 7 || orb.y - D.y < -0.5) return;
  const err = wrapA(Math.atan2(dx, dz) - D.yaw); if (Math.abs(err) < 0.8 || d < 1.6) D.yaw += clamp(err, -2.6 * dt, 2.6 * dt);
}""")
rep("if (!D.ai && D.flung && !D.slam) homeIn(D, dt, 0.5, 0.35, true); }",
    "if (!D.ai && D.flung && !D.slam) homeIn(D, dt, 0.5, 0.35, true); if (!D.ai && orb.on && D.giantT <= 0 && !D.slam) orbHome(D, dt); }")
# slingshots aimed near the orb bend onto it too (an arc that passes through it, so no power change)
rep("  // a free coffin roughly where you're aiming: a lighter nudge toward it\n",
    "  if (orb.on && orb.k > 0.5 && D.giantT <= 0) { const dO = Math.hypot(orb.x - D.x, orb.z - D.z); if (dO < flightFor(c, D.y - orb.base).d + 1) cands.push({ x: orb.x, z: orb.z, y: orb.base, cone: 0.4, bend: 0.65, pow: 0, short: 0, enemy: false, orb: true }); }\n  // a free coffin roughly where you're aiming: a lighter nudge toward it\n")
rep("    if (Math.abs(flightFor(c, D.y - t.y).d - d) > Math.max(3.5, d * 0.4)) continue;", "    if (!t.orb && Math.abs(flightFor(c, D.y - t.y).d - d) > Math.max(3.5, d * 0.4)) continue;")
rep("return { yaw: yaw + best.err * best.t.bend, c: want > 0 ? clamp(c + (want - c) * best.t.pow, FLING_MIN, 1) : c, lock: true, coffin: !best.t.enemy };",
    "return { yaw: yaw + best.err * best.t.bend, c: want > 0 ? clamp(c + (want - c) * best.t.pow, FLING_MIN, 1) : c, lock: true, coffin: !best.t.enemy && !best.t.orb, orb: !!best.t.orb };")
rep("aimIn.material.color.setHex(as.lock ? (as.coffin ? 0xFF9DB0 : 0xFFD23F) : 0xFFFFFF);", "aimIn.material.color.setHex(as.lock ? (as.orb ? 0x9FFFE0 : as.coffin ? 0xFF9DB0 : 0xFFD23F) : 0xFFFFFF);")

# ---- a pointer that shows where the orb is, and a rainbow flash when it shows up ----
rep('  <div class="vig" id="vig"></div>\n', '  <div class="vig" id="vig"></div>\n  <div class="orbflash" id="orbFlash"></div>\n  <div class="orbptr" id="orbPtr"><i></i><u><b></b></u></div>\n')
rep(".tube.low{animation:wobble .35s ease-in-out infinite}\n",
    """.tube.low{animation:wobble .35s ease-in-out infinite}
.orbptr{position:absolute;left:0;top:0;width:40px;height:40px;margin:-20px 0 0 -20px;pointer-events:none;z-index:6;display:none;will-change:transform}
.orbptr.on{display:block}
.orbptr i{position:absolute;inset:7px;border-radius:50%;border:3px solid var(--outline);background:conic-gradient(#FF4D6D,#FFD23F,#4DFFB8,#4DA6FF,#C77DFF,#FF4D6D);box-shadow:0 0 14px 5px rgba(255,255,255,.65);animation:orbspin 1.1s linear infinite}
.orbptr u{position:absolute;inset:0}
.orbptr b{position:absolute;left:50%;top:-9px;margin-left:-9px;width:0;height:0;border-left:9px solid transparent;border-right:9px solid transparent;border-bottom:13px solid #fff;filter:drop-shadow(0 0 2px rgba(20,10,40,.9))}
.orbptr.edge i{animation:orbspin 1.1s linear infinite,orbpulse .7s ease-in-out infinite alternate}
@keyframes orbspin{to{transform:rotate(360deg)}}
@keyframes orbpulse{to{box-shadow:0 0 22px 9px rgba(255,255,255,.9)}}
.orbflash{position:absolute;inset:0;pointer-events:none;z-index:5;opacity:0}
.orbflash.on{animation:orbflash 1.8s ease-out}
@keyframes orbflash{0%{opacity:1;box-shadow:inset 0 0 70px 22px #FF4D6D}25%{opacity:.9;box-shadow:inset 0 0 70px 22px #FFD23F}50%{opacity:.75;box-shadow:inset 0 0 70px 22px #4DA6FF}75%{opacity:.5;box-shadow:inset 0 0 70px 22px #C77DFF}100%{opacity:0;box-shadow:inset 0 0 70px 22px #4DFFB8}}
""")
rep(".tube.giant .ttrack i,.tube.giant .tdrop,.tube.low,", ".orbptr i,.orbflash.on,.tube.giant .ttrack i,.tube.giant .tdrop,.tube.low,")
rep("  orb.g.visible = true; orb.ring.visible = true; AU.orb();", "  orb.g.visible = true; orb.ring.visible = true; AU.orb(); kick($('orbFlash'), 'on'); popText('Giant orb!');")
rep("  // rain puddles: a soft rim, and steam curling up while one dries",
    """  // the orb pointer: rides above the orb when it's on screen and far off, sits on the screen edge pointing at it when it isn't
  const opEl = $('orbPtr');
  if (orb.on && playing && P.st !== 'ko' && P.giantT <= 0) {
    tv1.set(orb.x, orb.y, orb.z).project(camera);
    const W = canvas.clientWidth, Hh = canvas.clientHeight, behind = tv1.z > 1; let x = behind ? -tv1.x : tv1.x, y = behind ? -tv1.y : tv1.y;
    const on = !behind && Math.abs(x) < 0.9 && Math.abs(y) < 0.78, far = Math.hypot(orb.x - P.x, orb.z - P.z) > 6;
    if (on && !far) { if (opEl._on) { opEl._on = false; opEl.classList.remove('on'); } }
    else {
      let px, py, rot;
      if (on) { px = (x * 0.5 + 0.5) * W; py = (-y * 0.5 + 0.5) * Hh - 44 - Math.abs(Math.sin(clock * 5)) * 6; rot = 180; }
      else { const m = Math.max(Math.abs(x) / 0.86, Math.abs(y) / 0.72, 1e-3); x /= m; y /= m; px = (x * 0.5 + 0.5) * W; py = (-y * 0.5 + 0.5) * Hh; rot = Math.atan2(x, y) * 180 / Math.PI; }
      if (!opEl._on) { opEl._on = true; opEl.classList.add('on'); }
      opEl.classList.toggle('edge', !on);
      opEl.style.transform = 'translate(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px)'; opEl.children[1].style.transform = 'rotate(' + rot.toFixed(0) + 'deg)';
    }
  } else if (opEl._on) { opEl._on = false; opEl.classList.remove('on'); }
  // rain puddles: a soft rim, and steam curling up while one dries""")
open(F, 'w').write(s)
print('ok')
