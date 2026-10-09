import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ================= sizes, teams, timers =================
rep("const ARENA = 26.4;        // half size of the canvas floor", "let ARENA = 26.4; const ARENA_MAX = 33; // half size of the canvas floor (a 3-way canvas is 25% wider each way)")
rep("const CELL = 2, GN = Math.ceil(2 * ARENA / CELL) + 1;", "const CELL = 2, GN = Math.ceil(2 * ARENA_MAX / CELL) + 1;")
rep("{ name: 'holy water', wet: 0x2E9BFF, dry: 0x1C5592, css: '#2E9BFF' }];", "{ name: 'holy water', wet: 0x2E9BFF, dry: 0x1C5592, css: '#2E9BFF' }, { name: 'wolfsbane', wet: 0x8E5CFF, dry: 0x46297F, css: '#8E5CFF' }];")
rep("const OT_T = 10, MATCH_T = 90,", "const OT_T = 10, MATCH_T = 90, SOLO_T = 60,")
rep("const START = { x: 0, z: -20, yaw: 0 }, CSTART = { x: 0, z: 20, yaw: Math.PI };", "const START = { x: 0, z: -20, yaw: 0 }, CSTART = { x: 0, z: 20, yaw: Math.PI }, CSTART2 = { x: 20, z: 0, yaw: -Math.PI / 2 };")

# ================= three colors of paint =================
rep("const tcode = D => D.team + (D.dilT > 0 ? 2 : 0);", "const tcode = D => D.team + (D.dilT > 0 ? 3 : 0);")
rep("const tm = (team || 0) & 1, dil = (team || 0) >= 2, full = tm + 1, v = full + (dil ? 2 : 0),", "const tm = (team || 0) % 3, dil = (team || 0) >= 3, full = tm + 1, v = full + (dil ? 3 : 0),")
rep("let NS = 1, painted = new Uint8Array(1), paintedN = 0; const teamN = [0, 0, 0, 0, 0];", "let NS = 1, painted = new Uint8Array(1), paintedN = 0; const teamN = [0, 0, 0, 0, 0, 0, 0];")
rep("return v ? ((v - 1) % 2 === D.team ? 1 : -1) : 0; }", "return v ? ((v - 1) % 3 === D.team ? 1 : -1) : 0; }")
rep("return v === me || v === me + 2; }", "return v === me || v === me + 3; }")
rep("const teamCov = t => (teamN[t + 1] + 0.5 * teamN[t + 3]) / NS * 100;", "const teamCov = t => (teamN[t + 1] + 0.5 * teamN[t + 4]) / NS * 100;")
rep("const cellGain = (v, me, steal) => v === me ? 0 : !v ? 1 : v === me + 2 ? 0.5 : v === 5 - me ? (1 + steal) * 0.5 : steal;", "const cellGain = (v, me, steal) => v === me ? 0 : !v ? 1 : v === me + 3 ? 0.5 : v > 3 ? (1 + steal) * 0.5 : steal;")
rep("uniform vec3 uWetA[2]; uniform vec3 uDryA[2];", "uniform vec3 uWetA[3]; uniform vec3 uDryA[3];")
rep("""  float tm = mod(vTeam + 0.25, 2.0), dilA = vTeam > 1.5 ? 0.5 : 1.0;
  vec3 wetC = tm < 0.75 ? uWetA[0] : uWetA[1];
  vec3 dryC = tm < 0.75 ? uDryA[0] : uDryA[1];""", """  float tc = floor(mod(vTeam + 0.25, 3.0)), dilA = vTeam > 2.5 ? 0.5 : 1.0;
  vec3 wetC = tc < 0.5 ? uWetA[0] : tc < 1.5 ? uWetA[1] : uWetA[2];
  vec3 dryC = tc < 0.5 ? uDryA[0] : tc < 1.5 ? uDryA[1] : uDryA[2];""")
rep("pTeam[nP] = team & 1; nP++;", "pTeam[nP] = team % 3; nP++;")
rep("hr: R * 0.78 + PR * 0.3, team: team & 1 });", "hr: R * 0.78 + PR * 0.3, team: team % 3 });")
rep("if (v === me) own++; else { if (v === me + 2) own += 0.5;", "if (v === me) own++; else { if (v === me + 3) own += 0.5;")
# the trailing side's pound comes back faster: trailing whoever leads
rep("D.slamCD - dt * (teamCov(D.team) + 3 < teamCov(1 - D.team) ? 1.25 : 1)", "D.slamCD - dt * (teamCov(D.team) + 3 < bestFoeCov(D) ? 1.25 : 1)")
rep("clamp((teamCov(1 - D.team) - teamCov(D.team)) / 6, 0, 0.8)", "clamp((bestFoeCov(D) - teamCov(D.team)) / 6, 0, 0.8)")

# ================= the third blob, modes, who's whose rival =================
rep("airSling: false, stunT: 0,", "airSling: false, kod: 0, flatted: 0, focus: null, stunT: 0,")
rep("const P = newBlob(0, false), H = newBlob(1, true); // you and the holy water\nconst other = D => D === P ? H : P;",
"""const P = newBlob(0, false), H = newBlob(1, true), H2 = newBlob(2, true); // you, the holy water, and in a 3-way, wolfsbane
// modes: solo (just you against the clock), duel (you vs the holy water), trio (all three, everyone for themselves, on a bigger canvas)
const MODES = [['solo', 'Solo', 'Just you, 60 seconds'], ['duel', '1v1', 'You vs the holy water'], ['trio', '3-way', 'You vs the holy water vs wolfsbane']];
let mode = MODES.some(m => m[0] === store.mode) ? store.mode : 'duel', ACTIVE = [P, H];
const NAMES = ['You', 'Holy water', 'Wolfsbane'], nameOf = D => NAMES[D.team];
function applyMode() { ARENA = mode === 'trio' ? ARENA_MAX : 26.4; VS_CFG.pots = mode === 'trio' ? 11 : 8; VS_CFG.rivals = mode === 'trio' ? 17 : 12; ACTIVE = mode === 'solo' ? [P] : mode === 'trio' ? [P, H, H2] : [P, H]; }
const foes = D => ACTIVE.filter(o => o !== D);
const inPlay = D => D.st === 'play' || D.st === 'hide';
// the one that matters to a blob: the holy water's focus (or yours), or whoever is closest
function nearestFoe(D) { let best = null, bd = 1e9; for (const o of foes(D)) { if (!inPlay(o)) continue; const d = Math.hypot(o.x - D.x, o.z - D.z); if (d < bd) { bd = d; best = o; } } return best || foes(D)[0] || (D === P ? H : P); }
function other(D) { if (mode !== 'trio') return D === P ? H : P; if (D.cpu && D.focus && D.focus !== D && ACTIVE.includes(D.focus) && inPlay(D.focus)) return D.focus; return nearestFoe(D); }
// a CPU in a 3-way picks who to deal with: close, and whoever is ahead, with a little extra pull toward you
function pickFocus(D) { let best = null, bs = -1e9; for (const o of foes(D)) { if (!inPlay(o)) continue; const s = -Math.hypot(o.x - D.x, o.z - D.z) + (o === P ? 3 : 0) + (teamCov(o.team) - teamCov(D.team)) * 0.4; if (s > bs) { bs = s; best = o; } } return best; }
const bestFoeCov = D => { let m = 0; for (const o of foes(D)) m = Math.max(m, teamCov(o.team)); return m; };
// the rival in front of you, roughly where you're pointing (aim assist and the missile's homing)
function coneFoe(D, cone, maxD) { let best = null; for (const O of foes(D)) { if (O.st !== 'play' || O.immuneT > 0.3) continue; const dx = O.x - D.x, dz = O.z - D.z, d = Math.hypot(dx, dz); if (d < 0.8 || d > maxD) continue; const err = wrapA(Math.atan2(dx, dz) - D.yaw); if (Math.abs(err) > cone) continue; if (!best || Math.abs(err) < Math.abs(best.err)) best = { O, d, err }; } return best; }""")
rep("let diff = DIFFS.some(d => d[0] === store.diff) ? store.diff : 'medium';", "let diff = DIFFS.some(d => d[0] === store.diff) ? store.diff : 'medium';")

# a reset puts everyone in place, and anyone not in this mode sits out
rep("  resetBlob(P, START.x, START.z, START.yaw); resetBlob(H, CSTART.x, CSTART.z, CSTART.yaw); aiReset(H);\n  for (const D of [P, H]) { D.slamCD = D.slamMax = SLAM_FIRST; }",
    "  resetBlob(P, START.x, START.z, START.yaw); resetBlob(H, CSTART.x, CSTART.z, CSTART.yaw); aiReset(H); resetBlob(H2, CSTART2.x, CSTART2.z, CSTART2.yaw); aiReset(H2);\n  if (mode === 'solo') H.st = 'out'; if (mode !== 'trio') H2.st = 'out';\n  for (const D of [P, H, H2]) { D.slamCD = D.slamMax = SLAM_FIRST; }")
rep("  drop.visible = true; shadowBlob.visible = true; cDrop.visible = true; cShadow.visible = true;",
    "  drop.visible = true; shadowBlob.visible = true; LH.drop.visible = LH.shadow.visible = mode !== 'solo'; L2.drop.visible = L2.shadow.visible = mode === 'trio'; Object.assign(L2.look, { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 }); hud.classList.toggle('trio', mode === 'trio'); hud.classList.toggle('solo', mode === 'solo');")
rep("  runT = 0; matchLeft = MATCH_T;", "  runT = 0; matchLeft = mode === 'solo' ? SOLO_T : MATCH_T;")
rep("  if (D.dry && (D.paint >= DRY_OUT || D.giantT > 0 || D.st === 'ko')) { D.dry = false;  }", "  if (D.st === 'out') return;\n  if (D.dry && (D.paint >= DRY_OUT || D.giantT > 0 || D.st === 'ko')) { D.dry = false;  }")
rep("function aiStep(D, dt) {\n  const ai = D.ai; if (!ai) return;", "function aiStep(D, dt) {\n  const ai = D.ai; if (!ai || D.st === 'out') return;\n  if (mode === 'trio' && (ai.focusT = (ai.focusT || 0) - dt) <= 0) { ai.focusT = 1.2 + Math.random() * 0.8; const f = pickFocus(D); if (f && f !== D.focus) { D.focus = f; ai.o = null; ai.seenT = 0; } }")

# spawns: a third one for the 3-way, as far from the other two as the map allows
rep("  const dH = navField([[sH.id, 0]]);", "  const dH = navField([[sH.id, 0]]);\n  let sH2 = null; if (mode === 'trio') { let b2 = -1; for (const n of nodes) { if (!spawnOK(n) || !(dP[n.id] < 1e6) || !(dH[n.id] < 1e6)) continue; const sc2 = Math.min(dP[n.id], dH[n.id]) + R() * 2; if (sc2 > b2) { b2 = sc2; sH2 = n; } } if (!sH2) return false; }")
rep("  Object.assign(START, { x: sP.x, z: sP.z, yaw: Math.atan2(-sP.x, -sP.z) });", "  if (sH2) Object.assign(CSTART2, { x: sH2.x, z: sH2.z, yaw: Math.atan2(-sH2.x, -sH2.z) });\n  Object.assign(START, { x: sP.x, z: sP.z, yaw: Math.atan2(-sP.x, -sP.z) });")
rep("const nearSpawn = (n, r) => dist2(n, sP) < r || dist2(n, sH) < r;", "const nearSpawn = (n, r) => dist2(n, sP) < r || dist2(n, sH) < r || (sH2 && dist2(n, sH2) < r);")

# everyone-loops
s = s.replace("![P, H].some(D => D.st !== 'ko' && Math.hypot(D.x - r.x, D.z -", "!ACTIVE.some(D => D.st !== 'ko' && Math.hypot(D.x - r.x, D.z -")
rep("< ARENA - 4 && [P, H].every(D => ", "< ARENA - 4 && ACTIVE.every(D => ")
rep("  for (const D of [P, H]) { if (D.st !== 'play' || D.giantT > 0) continue; if (Math.hypot(D.x - orb.x,", "  for (const D of ACTIVE) { if (D.st !== 'play' || D.giantT > 0) continue; if (Math.hypot(D.x - orb.x,")
rep("  for (const B of [P, H]) if (B.ai) B.ai.thinkT = 0;", "  for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0;")
rep("  state = 'dead'; for (const D of [P, H]) if (D.charging) clearCharge(D);", "  state = 'dead'; for (const D of ACTIVE) if (D.charging) clearCharge(D);")
rep("  for (const D of [P, H]) { D.y = 6.5; D.air = true; D.vy = -1; D.freeLand = true; D.stroke++; }", "  for (const D of ACTIVE) { D.y = 6.5; D.air = true; D.vy = -1; D.freeLand = true; D.stroke++; }")

# ================= hits land on everyone in range =================
rep("""  const O = other(D);
  if (O.ai) aiNotePound(O, D);
  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - p.x, O.z - p.z) < KO_R + 1 && Math.abs(O.y - p.y) < 1.6) { if (O.rollT > 0) dodgedPound(O, D); else burstPush(O, p, D); }""",
"""  for (const O of foes(D)) {
    if (O.ai && other(O) === D) aiNotePound(O, D);
    if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - p.x, O.z - p.z) < KO_R + 1 && Math.abs(O.y - p.y) < 1.6) { if (O.rollT > 0) dodgedPound(O, D); else burstPush(O, p, D); }
  }""")
rep("""    const B = other(D), bd = Math.hypot(B.x - D.x, B.z - D.z);
    if (B.st === 'play'""", """    for (const B of foes(D)) { const bd = Math.hypot(B.x - D.x, B.z - D.z);
    if (B.st === 'play'""")
rep("B.vy = 3 + 3.5 * (1 - bd / 16); B.knockT = 0.35; B.wob = 1; B.squash = 0.7; }\n  }", "B.vy = 3 + 3.5 * (1 - bd / 16); B.knockT = 0.35; B.wob = 1; B.squash = 0.7; } }\n  }")
rep("""  const O = other(D);
  if (O.ai) aiNotePound(O, D);
  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < koR) {
    const og = O.air ? surfaceUnder(O.x, O.z, O.y + STEP, true) : O.y, base = og > -Infinity ? og : O.y, lift = O.air ? O.y - base : 0;
    if (Math.abs(base - D.y) < 1.4) { if (lift > 0.6 || O.rollT > 0) dodgedPound(O, D); else poundHit(O, D, O.st === 'hide' ? 'coffin' : 'pound'); }
  }""", """  for (const O of foes(D)) {
    if (O.ai && other(O) === D) aiNotePound(O, D);
    if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < koR) {
      const og = O.air ? surfaceUnder(O.x, O.z, O.y + STEP, true) : O.y, base = og > -Infinity ? og : O.y, lift = O.air ? O.y - base : 0;
      if (Math.abs(base - D.y) < 1.4) { if (lift > 0.6 || O.rollT > 0) dodgedPound(O, D); else poundHit(O, D, O.st === 'hide' ? 'coffin' : 'pound'); }
    }
  }""")
rep("function splashPush(A, R, fk) {\n  const B = other(A); if (B.st !== 'play'", "function splashPush(A, R, fk) { for (const B of foes(A)) splashPush1(A, B, R, fk); }\nfunction splashPush1(A, B, R, fk) {\n  if (B.st !== 'play'")
rep("function blobContact() {\n  if (P.st !== 'play' || H.st !== 'play') return;", "// every pair that can touch (P and H here are just the two in this pair)\nfunction blobContact() { for (let i = 0; i < ACTIVE.length; i++) for (let j = i + 1; j < ACTIVE.length; j++) pairContact(ACTIVE[i], ACTIVE[j]); }\nfunction pairContact(P, H) {\n  if (P.st !== 'play' || H.st !== 'play') return;")
rep("  if (hearable(H)) AU.bonk(0.6);\n}", "  if (hearable(H) || hearable(P)) AU.bonk(0.6);\n}")
rep("  const O = other(D); if (D.ai || O.st !== 'play' || O.immuneT > 0.3) return null;\n  const dx = O.x - D.x, dz = O.z - D.z, d = Math.hypot(dx, dz); if (d < 1.2 || d > maxD) return null;\n  const err = wrapA(Math.atan2(dx, dz) - D.yaw); if (Math.abs(err) > cone) return null;\n  return { O, d, err };",
    "  if (D.ai) return null; const t = coneFoe(D, cone, maxD); return t && t.d >= 1.2 ? t : null;")
rep("  const O = other(D); if (O.st !== 'play' || O.immuneT > 0.3 || O.rollT > 0) return;\n  const dx = O.x - D.x, dz = O.z - D.z, d = Math.hypot(dx, dz); if (d < 0.8 || d > 16) return;\n  const err = wrapA(Math.atan2(dx, dz) - D.yaw); if (Math.abs(err) > 1.15) return;\n  const rate",
    "  const t = coneFoe(D, 1.15, 16); if (!t || t.O.rollT > 0) return; const err = t.err;\n  const rate")
rep("function aiEvade(D, dt) {\n  const ai = D.ai, O = other(D), o = ai.o;", "function aiEvade(D, dt) {\n  const ai = D.ai, O = foes(D).find(f => f.slam && f.st === 'play') || other(D), o = ai.o;")
rep("p.ring.material.color.copy(p.occ === H ? COL_HOLY : COL_INK);", "p.ring.material.color.copy(p.occ ? TEAM_COLS[p.occ.team] : COL_INK);")
# knockouts and flattenings, counted both ways
rep("  if (by) by.kos++; D.outs++;", "  if (by) { by.kos++; D.kod++; } D.outs++;")
rep("else { if (by === P) { hold = Math.max(hold, 0.09); shake = Math.max(shake, 0.3); } cDrop.visible = false; cShadow.visible = false; banner((reason === 'fall' && by ? 'Knocked it off!' : CPU_KO_MSG[reason]) || 'Got it!'); if (by === P) buzz([20, 30, 20]); }",
    "else { if (by === P) { hold = Math.max(hold, 0.09); shake = Math.max(shake, 0.3); } D.look.drop.visible = false; D.look.shadow.visible = false; if (mode !== 'trio' || by === P) banner((reason === 'fall' && by ? 'Knocked it off!' : CPU_KO_MSG[reason]) || 'Got it!'); else if (loud) popText(nameOf(D) + ' is out'); if (by === P) buzz([20, 30, 20]); }")
rep("  else cDrop.visible = true;", "  else D.look.drop.visible = true;")
rep("B.flatT = FLAT_T; B.spd = 0; B.turn = 0; B.slam = false; B.squash = 1; B.wob = 1; B.flats++;", "B.flatT = FLAT_T; B.spd = 0; B.turn = 0; B.slam = false; B.squash = 1; B.wob = 1; B.flats++; A.flatted++;")

# ================= the step =================
rep("""    for (const D of [P, H]) if (pounding(D)) stepBlob(D, dt);
    if (!pounding(P) && !pounding(H)) endMatch();""", """    for (const D of ACTIVE) if (pounding(D)) stepBlob(D, dt);
    if (!ACTIVE.some(pounding)) endMatch();""")
rep("    aiStep(H, dt);\n    stepBlob(P, dt); stepBlob(H, dt);", "    for (const D of ACTIVE) if (D.cpu) aiStep(D, dt);\n    for (const D of ACTIVE) stepBlob(D, dt);")
rep("leadAcc += dt; if (leadAcc > 0.3 && runT > 8) { leadAcc = 0; const a = Math.round(teamCov(0)), c = Math.round(teamCov(1)), ld = a > c ? 1 : c > a ? -1 : 0; if (ld && ld !== lastLead) { if (lastLead && clock - lastLeadT > 3) { popText(ld > 0 ? 'You lead!' : 'It leads'); AU.lead(ld > 0); } lastLead = ld; lastLeadT = clock; } }",
    "leadAcc += dt; if (mode !== 'solo' && leadAcc > 0.3 && runT > 8) { leadAcc = 0; const cs = ACTIVE.map(D => Math.round(teamCov(D.team))), top = Math.max(...cs), lead = cs.filter(c => c === top).length === 1 ? ACTIVE[cs.indexOf(top)] : null, ld = lead ? lead.team + 1 : 0; if (ld && ld !== lastLead) { if (lastLead && clock - lastLeadT > 3) { popText(lead === P ? 'You lead!' : mode === 'trio' ? nameOf(lead) + ' leads' : 'It leads'); AU.lead(lead === P); } lastLead = ld; lastLeadT = clock; } }")
rep("    if (matchLeft <= 0) { matchLeft = 0; if (!pounding(P) && !pounding(H)) endMatch(); }", "    if (matchLeft <= 0) { matchLeft = 0; if (!ACTIVE.some(pounding)) endMatch(); }")

# ================= end of a match =================
rep("""  const you = teamCov(0), cpu = teamCov(1), id = runId, ry = Math.round(you), rc = Math.round(cpu), win = ry > rc ? 1 : rc > ry ? -1 : 0; // decided on the whole numbers everyone sees
  // dead even at the buzzer: ten more seconds, once
  if (!win && !overtimeUsed) {""", """  const you = teamCov(0), cpu = teamCov(1), cpu2 = teamCov(2), id = runId, ry = Math.round(you), rc = Math.round(cpu), rc2 = Math.round(cpu2); // decided on the whole numbers everyone sees
  const rest = mode === 'trio' ? Math.max(rc, rc2) : rc, win = mode === 'solo' ? 1 : ry > rest ? 1 : rest > ry ? -1 : 0, winner = win > 0 ? P : win < 0 ? (mode === 'trio' && rc2 > rc ? H2 : H) : null;
  // dead even at the buzzer: ten more seconds, once
  if (mode !== 'solo' && !win && !overtimeUsed) {""")
rep("""  endInfo = { you, cpu, win, time: runT };
  store.wins = store.wins || {}; store.played = store.played || {};
  store.played[diff] = (store.played[diff] || 0) + 1; if (win > 0) store.wins[diff] = (store.wins[diff] || 0) + 1;
  store.runs = (store.runs || 0) + 1;
  store.bestCov = store.bestCov || {}; const newBest = ry > (store.bestCov[diff] || 0); if (newBest) store.bestCov[diff] = ry;
  endInfo.newBest = newBest;
  save();
  const [a, b] = fmtPair(you, cpu);
  banner(win > 0 ? 'You win!' : win < 0 ? 'Holy water wins' : 'Draw', a + ' vs ' + b, true);
  if (win > 0) {""", """  endInfo = { you, cpu, cpu2, win, winner, time: runT, mode };
  const key = mode === 'duel' ? '' : mode; // a best and a win count per mode (and per skill, against CPUs)
  store.wins = store.wins || {}; store.played = store.played || {}; store.bestCov = store.bestCov || {};
  const slot = mode === 'solo' ? 'solo' : key + diff, prev = store.bestCov[slot] || 0, newBest = ry > prev; endInfo.best = Math.max(prev, ry); endInfo.prevBest = prev;
  store.played[slot] = (store.played[slot] || 0) + 1; if (win > 0 && mode !== 'solo') store.wins[slot] = (store.wins[slot] || 0) + 1;
  store.runs = (store.runs || 0) + 1;
  if (newBest) store.bestCov[slot] = ry;
  endInfo.newBest = newBest;
  save();
  const [a, b] = fmtPair(you, cpu);
  if (mode === 'solo') banner(newBest ? 'New best!' : 'Time!', a + ' covered', true);
  else banner(win > 0 ? 'You win!' : win < 0 ? nameOf(winner) + ' wins' : 'Draw', mode === 'trio' ? a + ' / ' + b + ' / ' + Math.round(cpu2) + '%' : a + ' vs ' + b, true);
  if (mode === 'solo' ? newBest : win > 0) {""")
rep("  else { buzz([40, 30, 60]); setTimeout(() => { if (id === runId) win < 0 ? AU.lose() : AU.draw(); }, 350); }",
    "  else { buzz([40, 30, 60]); setTimeout(() => { if (id === runId) win < 0 ? AU.lose() : AU.draw(); }, 350); }")

# ================= the end screen =================
rep("""  const { you, cpu, win, time } = endInfo, n = store.runs || 1, lv = DIFFS.find(d => d[0] === diff), w = colorOf().words;
  const t = $('endTitle'); t.textContent = win > 0 ? 'You win!' : win < 0 ? 'Holy water wins' : 'Draw'; t.className = 'rtitle' + (win < 0 ? ' lose' : win === 0 ? ' draw' : '');
  const [a, b] = fmtPair(you, cpu); $('endPct').textContent = a; $('endPctC').textContent = b;
  $('chipYou').classList.toggle('win', win > 0); $('chipCpu').classList.toggle('win', win < 0);
  const pair = (y, c) => '<span class="y">' + y + '</span><em>-</em><span class="c">' + c + '</span>';
  $('endStats').innerHTML = '<div class="stat"><b>' + pair(P.kos, H.kos) + '</b><span>Knockouts</span></div><div class="stat"><b>' + pair(H.flats, P.flats) + '</b><span>Flattened</span></div><div class="stat"><b>' + ((store.bestCov && store.bestCov[diff]) || 0) + '%</b><span>Best on ' + lv[1] + '</span></div>';""",
"""  const { you, cpu, cpu2, win, winner, time } = endInfo, n = store.runs || 1, lv = DIFFS.find(d => d[0] === diff), w = colorOf().words, solo = endInfo.mode === 'solo', trio = endInfo.mode === 'trio';
  const t = $('endTitle'); t.textContent = solo ? (endInfo.newBest ? 'New best!' : 'Time!') : win > 0 ? 'You win!' : win < 0 ? nameOf(winner) + ' wins' : 'Draw'; t.className = 'rtitle' + (!solo && win < 0 ? (winner === H2 ? ' lose2' : ' lose') : !solo && win === 0 ? ' draw' : '');
  const [a, b] = fmtPair(you, cpu); $('endPct').textContent = a;
  $('chipCpu').className = 'pchip ' + (solo ? 'best' : 'cpu'); $('chipCpuName').textContent = solo ? (endInfo.newBest ? 'Old best' : 'Your best') : 'Holy water'; $('endPctC').textContent = solo ? (endInfo.newBest ? endInfo.prevBest : endInfo.best) + '%' : b;
  $('chipCpu2').hidden = !trio; $('endPctC2').textContent = Math.round(cpu2) + '%';
  $('chipYou').classList.toggle('win', solo ? endInfo.newBest : win > 0); $('chipCpu').classList.toggle('win', !solo && winner === H); $('chipCpu2').classList.toggle('win', winner === H2);
  const pair = (y, c, cc) => '<span class="y">' + y + '</span><em>-</em><span class="' + (cc || 'c') + '">' + c + '</span>';
  $('endStats').innerHTML = solo
    ? '<div class="stat"><b>' + a + '</b><span>Covered</span></div><div class="stat"><b>' + endInfo.best + '%</b><span>Best</span></div><div class="stat"><b>' + P.slams + '</b><span>Pounds</span></div>'
    : '<div class="stat"><b>' + pair(P.kos, P.kod, trio ? 'm' : 'c') + '</b><span>Knockouts</span></div><div class="stat"><b>' + pair(P.flatted, P.flats, trio ? 'm' : 'c') + '</b><span>Flattened</span></div><div class="stat"><b>' + endInfo.best + '%</b><span>Best on ' + lv[1] + '</span></div>';""")
rep("const PT_A = ['Nocturne'", "const PT_A = ['Nocturne'")

# ================= the HUD =================
rep('<span class="vsn cpu" id="pctC" aria-label="Holy water coverage">0%</span></div>\n        <div class="tug" id="meter"><i class="tYou" id="tugYou"></i><i class="tCpu" id="tugCpu"></i></div>',
    '<span class="vsr"><span class="vsn cpu" id="pctC" aria-label="Holy water coverage">0%</span><span class="vsn cpu2" id="pctC2" aria-label="Wolfsbane coverage">0%</span></span></div>\n        <div class="tug" id="meter"><i class="tYou" id="tugYou"></i><i class="tCpu" id="tugCpu"></i><i class="tCpu2" id="tugCpu2"></i></div>')
rep("""  const vc = Math.floor(cpu), ec = $('pctC'); if (vc !== lastPctC) { if (lastPctC >= 0 && vc < lastPctC) kick(ec, 'down'); else if (lastPctC >= 0) kick(ec, 'tick'); lastPctC = vc; } if (ec.textContent !== b) ec.textContent = b;
  $('tugYou').style.width = you.toFixed(2) + '%'; $('tugCpu').style.width = cpu.toFixed(2) + '%';""",
"""  const ec = $('pctC');
  if (mode === 'solo') { const best = (store.bestCov && store.bestCov.solo) || 0, bt = best ? best + '%' : '-'; if (ec.textContent !== bt) ec.textContent = bt; $('tugYou').style.width = Math.min(100, you / Math.max(best, 10) * 100).toFixed(2) + '%'; }
  else {
    const vc = Math.floor(cpu); if (vc !== lastPctC) { if (lastPctC >= 0 && vc < lastPctC) kick(ec, 'down'); else if (lastPctC >= 0) kick(ec, 'tick'); lastPctC = vc; } if (ec.textContent !== b) ec.textContent = b;
    $('tugYou').style.width = you.toFixed(2) + '%'; $('tugCpu').style.width = cpu.toFixed(2) + '%';
    if (mode === 'trio') { const c2 = teamCov(2), t2 = Math.round(c2) + '%', e2 = $('pctC2'); if (e2.textContent !== t2) e2.textContent = t2; const tc2 = $('tugCpu2'); tc2.style.width = c2.toFixed(2) + '%'; tc2.style.right = cpu.toFixed(2) + '%'; }
  }""")
rep('<div class="foeptr" id="foePtr"><i></i><u><b></b></u></div>', '<div class="foeptr" id="foePtr"><i></i><u><b></b></u></div>\n  <div class="foeptr two" id="foePtr2"><i></i><u><b></b></u></div>')
# the edge markers: one per rival on the canvas
# the edge markers: one per rival on the canvas
bi = s.index("  const fpEl = $('foePtr');\n"); be = s.index("  } else if (fpEl._on) { fpEl._on = false; fpEl.classList.remove('on'); }\n", bi) + len("  } else if (fpEl._on) { fpEl._on = false; fpEl.classList.remove('on'); }\n")
block = s[bi:be]
body = block.replace("  const fpEl = $('foePtr');\n", "").replace("if (playing && H.st === 'play' && P.st !== 'ko') {", "if (on && H.st === 'play' && P.st !== 'ko') {")
s = s[:bi] + "  foePointer($('foePtr'), H, playing && mode !== 'solo'); foePointer($('foePtr2'), H2, playing && mode === 'trio');\n" + s[be:]
fn = "// a rival off screen: an edge marker, red when its pound is coming down near you or it's lining up a fling at you\nfunction foePointer(fpEl, H, on) {\n" + body + "}\n"
k = s.index("// ---------- visuals each frame ----------"); s = s[:k] + fn + s[k:]
open(F, 'w').write(s)
print('ok part 1')
