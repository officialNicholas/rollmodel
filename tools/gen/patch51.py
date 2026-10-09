import sys, re
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:140])); sys.exit(1)
    s = s.replace(a, b)

# ---------- the missile: faster and flatter, and a little heat-seeking ----------
rep("const MISSILE_DIVE = 0.7; // drop per unit forward (about 35 degrees)",
    "const MISSILE_DIVE = 0.58, MISSILE_SPD = 2.0; // drop per unit forward (about 30 degrees), and it flies at twice your rolling speed")
rep("  const h = D.missile ? D.spd : Math.max(D.spd, cfg.speed * 1.7);", "  const h = D.missile ? D.spd : Math.max(D.spd, cfg.speed * MISSILE_SPD);")
rep("D.vy = 0; D.slamHang = 0; D.spd = Math.max(D.spd, cfg.speed * 1.7); D.turn = 0; D.buf = 0; if (!D.ai) missileAssist(D);",
    "D.vy = 0; D.slamHang = 0; D.spd = Math.max(D.spd, cfg.speed * MISSILE_SPD); D.turn = 0; D.buf = 0; if (!D.ai) missileAssist(D);")
rep("hh = Math.max(launchSpd(c), cfg.speed * 1.7);", "hh = Math.max(launchSpd(c), cfg.speed * MISSILE_SPD);")
rep("function homeIn(D, dt, rate, cone, coffins) {",
    """// in flight a missile bends toward the other blob while it's roughly ahead, but only so fast: a side-step or a roll still beats it, and a roll makes it lose you
function missileSeek(D, dt) {
  const O = other(D); if (O.st !== 'play' || O.immuneT > 0.3 || O.rollT > 0) return;
  const dx = O.x - D.x, dz = O.z - D.z, d = Math.hypot(dx, dz); if (d < 0.8 || d > 16) return;
  const err = wrapA(Math.atan2(dx, dz) - D.yaw); if (Math.abs(err) > 1.15) return;
  const rate = D.ai ? 1.2 : 1.6; D.yaw += clamp(err, -rate * dt, rate * dt);
}
function homeIn(D, dt, rate, cone, coffins) {""")
rep("D.y += D.vy * dt; if (!D.ai) homeIn(D, dt, 1.0, 0.6); }", "D.y += D.vy * dt; missileSeek(D, dt); }")

# the pound button's arrow turns forward when a pound would fire a missile
rep('<path d="M14 3h12v13h7.5L20 30.5 6.5 16H14z"/><path d="M6 36h28M7 30l-3.5-3M33 30l3.5-3" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>',
    '<path d="M14 3h12v13h7.5L20 30.5 6.5 16H14z"/><path class="gnd" d="M6 36h28M7 30l-3.5-3M33 30l3.5-3" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/><path class="trail" d="M14 31v6M20 32.5v6M26 31v6" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>')
rep(".slamBtn.up svg path:first-child{transform:rotate(180deg)}",
    ".slamBtn.up svg path:first-child{transform:rotate(180deg)}\n.slamBtn svg .gnd,.slamBtn svg .trail{transition:opacity .18s}\n.slamBtn svg .trail{opacity:0}\n.slamBtn.fwd svg path:first-child{transform:translateY(-2px) rotate(180deg)}\n.slamBtn.fwd svg .gnd{opacity:0}\n.slamBtn.fwd svg .trail{opacity:1}")
rep("""  const up = P.st === 'hide';
  if (b._up !== up) { b._up = up; b.classList.toggle('up', up); wasReady = null; }""",
    """  const up = P.st === 'hide', fwd = !up && ((P.air && (P.flingC || 0) > 0.15 && !P.slam) || (P.slam && P.missile));
  if (b._up !== up) { b._up = up; b.classList.toggle('up', up); wasReady = null; }
  if (b._fwd !== fwd) { b._fwd = fwd; b.classList.toggle('fwd', fwd); wasReady = null; }""")
rep("b.setAttribute('aria-label', ready ? (up ? 'Burst out of the coffin' : 'Ground pound')", "b.setAttribute('aria-label', ready ? (up ? 'Burst out of the coffin' : fwd ? 'Fire a missile' : 'Ground pound')")

# teach it once, the first time you're mid-fling with the pound ready
rep("    if (runT > 16 && slamReady(P) && H.st === 'play'",
    "    if (runT > 6 && P.air && (P.flingC || 0) > 0.3 && !P.slam && P.vy < 2 && slamReady(P)) hint('missile', say('Pound now to fire a missile', 'E now to fire a missile'), 2.2);\n    if (runT > 16 && slamReady(P) && H.st === 'play'")
rep("<li><span class=\"dot hand\">➚</span><span>Fling into the holy water to knock it flying. Ram it while you're faster, or land on it, to flatten it.</span></li>",
    "<li><span class=\"dot hand\">➚</span><span>Fling into the holy water to knock it flying, or pound mid-fling to fire a missile that steers toward it. Ram it while you're faster, or land on it, to flatten it.</span></li>")

# a roll never sets up a flattening ram: the roller and its target can't flatten each other until a moment after the roll
rep("  const rolling = P.rollT > 0 || H.rollT > 0; // a roll bumps, it never flattens (either way)",
    "  const rolling = P.rollT > 0 || H.rollT > 0 || P.rollCD > ROLL_CD - 0.6 || H.rollCD > ROLL_CD - 0.6; // a roll bumps, it never flattens (either way), even just after it")
open(F, 'w').write(s)
print('ok')
