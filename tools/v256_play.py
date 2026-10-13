"""v256 gameplay. Flash Freeze holds for 5 s, and a frozen fighter can tap fast to crack the ice and get out a second sooner (the
CPUs: never on easy, half the time on medium, always on hard). An orb goes into the slot on the left when you take it and fades after
10 s (a small clock beside it runs down, no numbers); using it late doesn't shorten what it does; Deep Pockets keeps it till you use
it. The Paint Trap is a much darker shade of its owner's paint, and bigger. The turret no longer stuns: each hit drains the paint
tank, and a hit with the tank empty knocks you out. Showdown CPUs keep the pound for rivals (no pounding, missiles or flings just
to paint the floor; a pound on boiling water to refill still counts). With a lobby lesson waiting (the Strokes page, commissions),
the results offer only Main menu. Solo is now called Time trial."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
CSS = r"""
/* (v256) frozen: each tap cracks the frost */
.frost.held.crk{animation:frcrk .2s ease-out}
@keyframes frcrk{40%{opacity:.72}}
/* (v256) an orb in your slot: a little clock beside it runs down over its 10 seconds (none with Deep Pockets) */
.orbBtn .oclk{position:absolute;right:-5px;top:-5px;z-index:2;width:22px;height:22px;border-radius:50%;background:conic-gradient(#FFF6D8 calc(var(--of,1) * 360deg),rgba(23,19,32,.6) 0);box-shadow:0 0 0 2.5px var(--line),0 2px 0 2.5px var(--line);transform:scaleX(-1)}
.orbBtn.low .oclk{background:conic-gradient(#FF3B5C calc(var(--of,1) * 360deg),rgba(23,19,32,.6) 0);animation:oclk .45s ease-in-out infinite alternate}
@keyframes oclk{to{transform:scaleX(-1) scale(1.16)}}
.orbBtn.keep .oclk{display:none}
"""
JS = r"""
// ---------- (v256) frozen: tap fast (or mash keys) to crack the ice and get out up to a second sooner ----------
const ICE_TAP = 0.1, ICE_TAP_MAX = 1;
function iceTap(D) {
  if (!(D.frozenT > 0) || D.st !== 'play') return;
  D.iceShk = 1; const got = D.iceTap || 0, k = Math.min(ICE_TAP, ICE_TAP_MAX - got);
  if (k > 0.001) { D.iceTap = got + k; D.frozenT = Math.max(0.02, D.frozenT - k); D.stunT = Math.max(0.02, (D.stunT || 0) - k); }
  for (let i = 0; i < 3; i++) { const a = Math.random() * 6.283, v = 1.2 + Math.random() * 1.6; spawnPart(D.x + Math.cos(a) * 0.4, D.y + 0.45, D.z + Math.sin(a) * 0.4, Math.cos(a) * v, 1.4 + Math.random() * 1.6, Math.sin(a) * v, 0.12 + Math.random() * 0.08, i % 2 ? boilPartMat : puHaloMat, 0.45); }
  if (D === P) { buzz(6); if (AU.tick) AU.tick(); restartCls($('frost'), 'crk'); } else if (hearable(D) && Math.random() < 0.35) { AU.at(D.x, D.z); if (AU.tick) AU.tick(); }
}
addEventListener('pointerdown', e => { if (state === 'play' && P.frozenT > 0 && P.st === 'play' && !(e.target && e.target.closest && e.target.closest('#pauseBtn, .corner'))) iceTap(P); }, true);
addEventListener('keydown', e => { if (state === 'play' && P.frozenT > 0 && P.st === 'play' && !e.repeat && e.key !== 'Escape' && e.key !== 'p' && e.key !== 'P') iceTap(P); }, true);
// ---------- (v256) an orb waits in your slot for ORB_HOLD seconds, then fades (Deep Pockets: as long as you like) ----------
const ORB_HOLD = 10;
function orbFade(D) {
  D.orbSaved = null; D.orbT = 0;
  for (let i = 0; i < 12; i++) { const a = Math.random() * 6.283; spawnPart(D.x, D.y + 0.6, D.z, Math.cos(a) * 1.2, 0.8 + Math.random(), Math.sin(a) * 1.2, 0.22, orbPartMats[i % orbPartMats.length], 0.5); }
  if (D === P) { popText('Your orb faded'); if (AU.nope) AU.nope(); }
}
// ---------- (v256) a lesson waiting in the lobby (the Strokes page, commissions): the results lead only back to the lobby ----------
function endGate() {
  const due = tutPh() === 'done' && ((!store.tut.strokes && strokesDue()) || (!store.tut.comms && commsDue())), eb = $('endBtn');
  end.classList.toggle('gate', due); eb.innerHTML = due ? '<span>Main menu</span><small>Something new in the lobby</small>' : '<span>Rematch</span><small>New canvas</small>';
  $('replayBtn').closest('.row').hidden = due;
  setTimeout(() => eb.focus({ preventScroll: true }), 30);
}
"""
def apply(s):
    s = rep(s, "\n</style>\n\n<div id=\"stage\">", "\n" + CSS.strip() + "\n</style>\n\n<div id=\"stage\">")
    # ---- Flash Freeze: 5 s; each one frozen gets its way out (yours: tapping)
    s = rep(s, "const FREEZE_WIND = 0.9, FREEZE_T = 3, FREEZE_SWEET = 0.12,", "const FREEZE_WIND = 0.9, FREEZE_T = 5, FREEZE_SWEET = 0.12,")
    s = rep(s, "B.frozenT = FREEZE_T; B.stunT = Math.max(B.stunT || 0, FREEZE_T); B.spd = 0; B.turn = 0; B.kx = B.kz = 0; B.slam = false; B.missile = false; B.rollT = 0; B.wob = 1; n++;",
               "B.frozenT = FREEZE_T; B.stunT = Math.max(B.stunT || 0, FREEZE_T); B.spd = 0; B.turn = 0; B.kx = B.kz = 0; B.slam = false; B.missile = false; B.rollT = 0; B.wob = 1; n++;\n"
               "    B.iceTap = 0; B.iceShk = 0; B.iceMash = B.ai && (diff === 'hard' || (diff === 'medium' && Math.random() < 0.5)) ? 1 : 0; B.iceMashT = 0.45 + Math.random() * 0.4; // (v256: a CPU taps its way out on hard, half the time on medium, never on easy)")
    s = rep(s, "if (B === P) { shake = Math.max(shake, 0.3); buzz([30, 30, 30]); popText('Frozen!'); fr.classList.add('held'); frostHeld = true; }",
               "if (B === P) { shake = Math.max(shake, 0.3); buzz([30, 30, 30]); popText('Frozen! Tap fast to break out'); fr.classList.add('held'); frostHeld = true; }")
    s = rep(s, "  if (D.frozenT > 0) { D.frozenT -= dt; if (D.frozenT <= 0) { D.frozenT = 0; thawFx(D); } }\n",
               "  if (D.frozenT > 0 && D.iceMash) { D.iceMashT -= dt; if (D.iceMashT <= 0) { D.iceMashT = 0.17 + Math.random() * 0.13; iceTap(D); } }\n"
               "  if (D.frozenT > 0) { D.frozenT -= dt; if (D.frozenT <= 0) { D.frozenT = 0; thawFx(D); } }\n")
    # (the ice shell jolts with each tap)
    s = rep(s, "    m.position.set(D.x, D.y + 0.28 * gk, D.z); m.rotation.set(0.15, D.yaw + 0.4, 0.1); m.scale.set(k, 0.66 * k, 1.35 * k);",
               "    const sh = D.iceShk || 0; if (sh > 0) D.iceShk = Math.max(0, sh - rdt * 5); const jx = sh * 0.07 * Math.sin(clock * 97), jz = sh * 0.07 * Math.cos(clock * 83);\n"
               "    m.position.set(D.x + jx, D.y + 0.28 * gk, D.z + jz); m.rotation.set(0.15 + sh * 0.14 * Math.sin(clock * 71), D.yaw + 0.4, 0.1 + sh * 0.14 * Math.cos(clock * 89)); m.scale.set(k * (1 + 0.05 * sh), 0.66 * k, 1.35 * k);")
    # ---- the orb: into your slot, a clock on it, fading after ORB_HOLD (the lessons keep it going off at once)
    s = rep(s, "  // Deep Pockets: the first orb goes in your pocket for later; with one already saved, the next goes off at once\n"
               "  if (D.skill === 'pockets' && !D.orbSaved && !tut && !tut2 && !tut3) { D.orbSaved = gift; emote(D, 'glee', 0.8); if (D === P) { AU.pop(); buzz([10, 20, 10]); const w = (ORB_LBL[gift] || 'orb').toLowerCase(); banner('Orb saved!', say('Tap it when you want the ' + w, 'Press C for the ' + w)); } for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return; }\n",
               "  // (v256) the orb goes in your slot, to use when you like: it fades after ORB_HOLD seconds, and Deep Pockets keeps it till you use it;\n"
               "  // with one already in the slot, the next goes off at once (the lessons have theirs go off at once too)\n"
               "  if (!D.orbSaved && !tut && !tut2 && !tut3) { const keep = D.skill === 'pockets'; D.orbSaved = gift; D.orbT = keep ? Infinity : ORB_HOLD; if (D.ai) D.ai.orbWait = 0.5 + Math.random() * 2.2; emote(D, 'glee', 0.8);\n"
               "    if (D === P) { AU.pop(); buzz([10, 20, 10]); const w = ORB_LBL[gift] || 'Orb'; banner(keep ? 'Orb saved!' : w + ' ready!', keep ? say('Keep it as long as you like. Tap it to use it', 'Keep it as long as you like. Press C to use it') : say('Tap it to use it', 'Press C to use it')); }\n"
               "    for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return; }\n")
    s = rep(s, "function stepBlob(D, dt) {\n  if (D.st === 'out') return;\n",
               "function stepBlob(D, dt) {\n  if (D.st === 'out') return;\n"
               "  if (D.orbSaved && state === 'play') { if (D.orbT < Infinity) { D.orbT -= dt; if (D.orbT <= 0) orbFade(D); } if (D.orbSaved && D.ai && (D.ai.orbWait = (D.ai.orbWait || 0) - dt) <= 0 && !useOrb(D)) D.ai.orbWait = 0.3; } // (v256: the orb in the slot; a CPU holds its own a moment, then uses it)\n")
    s = rep(s, "  if (os && ob.dataset.k !== os) { ob.dataset.k = os; ob.innerHTML = '<i class=\"sdisc\" aria-hidden=\"true\"></i>' + (STROKE_ICON[os] || '') + '<span class=\"ilbl\">' + (ORB_LBL[os] || 'Orb') + '</span>'; ob.setAttribute('aria-label', 'Use your saved ' + (ORB_LBL[os] || 'orb').toLowerCase()); restartCls(ob, 'in'); } else if (!os) ob.dataset.k = '';\n}",
               "  if (os && ob.dataset.k !== os) { ob.dataset.k = os; ob.innerHTML = '<i class=\"sdisc\" aria-hidden=\"true\"></i>' + (STROKE_ICON[os] || '') + '<span class=\"ilbl\">' + (ORB_LBL[os] || 'Orb') + '</span><i class=\"oclk\" aria-hidden=\"true\"></i>'; ob.setAttribute('aria-label', 'Use the ' + (ORB_LBL[os] || 'orb').toLowerCase()); restartCls(ob, 'in'); } else if (!os) ob.dataset.k = '';\n"
               "  if (os) { const keep = !(P.orbT < Infinity), f = keep ? 1 : clamp(P.orbT / ORB_HOLD, 0, 1); if (ob._keep !== keep) { ob._keep = keep; ob.classList.toggle('keep', keep); } if (!keep && Math.abs((ob._f === undefined ? 2 : ob._f) - f) > 0.003) { ob._f = f; ob.style.setProperty('--of', f.toFixed(3)); ob.classList.toggle('low', f < 0.3); } } else ob._f = undefined; // (v256: the orb's clock)\n}")
    # ---- the Paint Trap: much darker, and bigger
    s = rep(s, "const TRAP_R = 0.75, TRAP_ARM", "const TRAP_R = 0.92, TRAP_ARM")
    s = rep(s, "const g = new THREE.Group(), M = trapMat(TEAMS[D.team].wet);", "const g = new THREE.Group(), M = trapMat(trapDark(TEAMS[D.team].wet));")
    s = rep(s, "  g.userData.light = light; g.userData.ring = ring; return g;\n}\n",
               "  g.userData.light = light; g.userData.ring = ring; g.scale.setScalar(TRAP_SCALE); return g;\n}\n"
               "// (v256) a trap is a much darker shade of its owner's paint, and bigger, so it stands out on a painted floor\n"
               "const TRAP_SCALE = 1.3, trapDark = h => (Math.round(((h >> 16) & 255) * 0.4) << 16) | (Math.round(((h >> 8) & 255) * 0.4) << 8) | Math.round((h & 255) * 0.4);\n")
    # ---- the turret: hits drain the paint tank like health; a hit on an empty tank knocks out. No stun
    s = rep(s, "SHOT_STUN = 1.1, SHOT_PUSH = 4.6;", "SHOT_STUN = 1.1, SHOT_PUSH = 4.6, SHOT_DMG = 0.07; // (v256: SHOT_DMG, the paint a hit takes; no more stun)")
    s = rep(s, "  const stunNow = !(B.tGuard > 0); // one stun at a time: shots right after only shove\n"
               "  if (stunNow) { B.stunT = Math.max(B.stunT || 0, SHOT_STUN); B.tGuard = SHOT_STUN + 0.9; B.spd = 0; B.turn = 0; }\n"
               "  B.kx = nx * SHOT_PUSH * (stunNow ? 1 : 0.6); B.kz = nz * SHOT_PUSH * (stunNow ? 1 : 0.6); B.slam = false; B.missile = false; B.squash = 0.8; B.wob = 1; fxKnock(B, nx, nz, stunNow ? 0.65 : 0.4);\n"
               "  if (!B.air) { B.air = true; B.stroke++; B.vy = 2.2; } B.lastHit = { by: A, t: runT };\n",
               "  // (v256) no stun: the paint tank is the health bar. A hit takes SHOT_DMG of it; a hit with nothing left knocks you out there and then\n"
               "  if (B.dry || (B.paint || 0) <= 0.01) { B.lastHit = { by: A, t: runT }; shockwave(B.x, B.y + 0.1, B.z, 1.6, TEAMS[A.team].wet); hitStop(0.06, A, B); return knockOut(B, 'shot', A); }\n"
               "  B.paint = Math.max(0, B.paint - SHOT_DMG); if (B.paint <= 0.001 && !B.dry) { B.paint = 0; goDry(B); }\n"
               "  const stunNow = false;\n"
               "  B.kx = nx * SHOT_PUSH * 0.45; B.kz = nz * SHOT_PUSH * 0.45; B.squash = 0.85; B.wob = 1; fxKnock(B, nx, nz, 0.35); B.lastHit = { by: A, t: runT };\n")
    s = rep(s, "  if (B === P) { shake = Math.max(shake, 0.22); buzz([15, 20, 15]); if (stunNow) popText('Splatted!'); } else if (A === P) { buzz(10); if (stunNow) popText('Hit!'); }\n}",
               "  if (B === P) { shake = Math.max(shake, 0.22); buzz([15, 20, 15]); pingTank(1.2); } else if (A === P) buzz(10);\n}")
    s = rep(s, "const KO_MSG = { pound: 'Pounded!',", "const KO_MSG = { shot: 'Shot down!', pound: 'Pounded!',")
    s = rep(s, "const CPU_KO_MSG = { pound: n => 'Got ' + n + '!',", "const CPU_KO_MSG = { shot: n => 'Shot down ' + n + '!', pound: n => 'Got ' + n + '!',")
    # ---- Showdown CPUs: no pounding (or missiles, or flings) just to paint the floor
    s = rep(s, "const SD_AI = { easy: { hunt: 0.09, attack: 0.3, ram: 0.3, sense: 12, seek: 0.25 }, medium: { hunt: 0.42, attack: 0.7, ram: 0.7, flingAtk: 0.45, sense: 24, seek: 0.55 }, hard: { hunt: 0.7, attack: 0.9, ram: 1, sense: 34, seek: 0.85 } };",
               "const SD_NOPAINT = { covPound: 0, missileCov: 0, flingPaint: 0 }; // (v256: in a Showdown paint is only fuel)\n"
               "const SD_AI = { easy: Object.assign({ hunt: 0.09, attack: 0.3, ram: 0.3, sense: 12, seek: 0.25 }, SD_NOPAINT), medium: Object.assign({ hunt: 0.42, attack: 0.7, ram: 0.7, flingAtk: 0.45, sense: 24, seek: 0.55 }, SD_NOPAINT), hard: Object.assign({ hunt: 0.7, attack: 0.9, ram: 1, sense: 34, seek: 0.85 }, SD_NOPAINT) };")
    s = rep(s, "  const poundAt = pick[2] > 0 && pick[2] > 0.35 * (pick[0] * (nDist[tn.id] + 2.5)) ? tn.id : -1;",
               "  const poundAt = !isShow() && pick[2] > 0 && pick[2] > 0.35 * (pick[0] * (nDist[tn.id] + 2.5)) ? tn.id : -1; // (v256: never in a Showdown)")
    s = rep(s, "    if (AI.plan > 0.8 && slamReady(D) && !sunny && D.paint - SLAM_COST > 0.45 && localGain(D, SLAM_R * 0.84) > AI.covPound * COV_K * 0.75) useSlam(D); else jump(D);",
               "    if (AI.plan > 0.8 && slamReady(D) && !sunny && D.paint - SLAM_COST > 0.45 && (isShow() ? foes(D).some(F => F.st === 'play' && Math.hypot(F.x - D.x, F.z - D.z) < SLAM_R * 1.05 && Math.abs(F.y - D.y) < 1.2) : localGain(D, SLAM_R * 0.84) > AI.covPound * COV_K * 0.75)) useSlam(D); else jump(D); // (v256: in a Showdown, a burst out only to catch someone)")
    # ---- the results with a lobby lesson waiting: only Main menu
    s = rep(s, "measureOutro(); setTimeout(() => $('endBtn').focus({ preventScroll: true }), 30); return; }", "measureOutro(); endGate(); return; }")
    s = rep(s, "  end.hidden = false; measureOutro(); judgeGo();\n  setTimeout(() => $('endBtn').focus({ preventScroll: true }), 30);\n}", "  end.hidden = false; measureOutro(); judgeGo();\n  endGate();\n}")
    s = rep(s, "function rematchVote() { if (building || irisBusy) return; if (tutPh() !== 'done') return start();", "function rematchVote() { if (building || irisBusy) return; if (end.classList.contains('gate')) return toMenu(); if (tutPh() !== 'done') return start();")
    # ---- Solo is Time trial
    s = rep(s, "['solo', 'Solo', 'Just you, 60 seconds']", "['solo', 'Time trial', 'Just you, 60 seconds']")
    s = rep(s, '<span class="evtx"><b>Solo</b><small>Just you, 60 seconds</small></span>', '<span class="evtx"><b>Time trial</b><small>Just you, 60 seconds</small></span>')
    s = rep(s, "t: 'Solo show', d: 'Cover 30% in a solo match'", "t: 'Beat the clock', d: 'Cover 30% in a Time trial'")
    s = rep(s, "'. Solo plays the canvas you choose.'", "'. A Time trial plays the canvas you choose.'")
    s = rep(s, "(mode === 'solo' ? 'Solo, 60 seconds' :", "(mode === 'solo' ? 'Time trial, 60 seconds' :")
    s = rep(s, "mode === 'solo' ? 'Solo \\u00b7 60 seconds' :", "mode === 'solo' ? 'Time trial \\u00b7 60 seconds' :")
    s = rep(s, "(mode === 'solo' ? 'Solo' : 'CPU ' +", "(mode === 'solo' ? '60 seconds' : 'CPU ' +")
    s = rep(s, "(solo ? 'Solo' : (MODES.find(m => m[0] === mode)", "(solo ? 'Time trial' : (MODES.find(m => m[0] === mode)")
    # ---- the code above, before the event screen
    s = rep(s, "// ---------- Choose Event (v209): Play opens it.", JS.strip() + "\n// ---------- Choose Event (v209): Play opens it.")
    return s
