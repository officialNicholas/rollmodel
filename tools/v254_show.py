"""v254: Showdown. Four fighters on the bigger canvas, free-for-all or 2v2, two hearts each; the last one (or pair) standing wins.
A fourth fighter (H3, its look L3), a fourth paint colour, sides (SIDE: who's with whom; nobody hurts a teammate), hearts and
elimination, a spectator camera once you're out, the hearts across the top, the fight card, the victory screen and the results for
four, and the event card's two ways to play. The JS and CSS live beside this file (v254_show.js, v254_show.css)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def apply(s):
    js = open(os.path.join(HERE, 'v254_show.js')).read(); css = open(os.path.join(HERE, 'v254_show.css')).read()
    # ---- the stylesheet
    s = rep(s, "\n</style>\n\n<div id=\"stage\">", "\n" + css + "</style>\n\n<div id=\"stage\">")
    # ---- a fourth paint colour, and a fourth start
    s = rep(s, "{ name: 'rival 2', wet: 0x8E5CFF, dry: 0x46297F, css: '#8E5CFF' }];", "{ name: 'rival 2', wet: 0x8E5CFF, dry: 0x46297F, css: '#8E5CFF' }, { name: 'rival 3', wet: 0x19C9A6, dry: 0x0E6B58, css: '#19C9A6' }];")
    s = rep(s, "CSTART2 = { x: 20, z: 0, yaw: -Math.PI / 2 };", "CSTART2 = { x: 20, z: 0, yaw: -Math.PI / 2 }, CSTART3 = { x: -20, z: 0, yaw: Math.PI / 2 };")
    # ---- the paint: four sides' colours (codes 1-4 full, 5-8 watered down); a teammate's paint is as good as your own
    s = rep(s, "const teamN = [0, 0, 0, 0, 0, 0, 0];", "const teamN = [0, 0, 0, 0, 0, 0, 0, 0, 0];")
    s = rep(s, "const tcode = D => D.team + (D.dilT > 0 ? 3 : 0);", "const tcode = D => D.team + (D.dilT > 0 ? 4 : 0);")
    s = rep(s, "const tm = (team || 0) % 3, dil = (team || 0) >= 3, full = tm + 1, v = full + (dil ? 3 : 0),", "const tm = (team || 0) % 4, dil = (team || 0) >= 4, full = tm + 1, v = full + (dil ? 4 : 0),")
    s = rep(s, "return v ? ((v - 1) % 3 === D.team ? 1 : -1) : 0; }", "return v ? (SIDE[(v - 1) % 4] === SIDE[D.team] ? 1 : -1) : 0; }")
    s = rep(s, "return v === me || v === me + 3; }", "return !!v && SIDE[(v - 1) % 4] === SIDE[D.team]; }")
    s = rep(s, "const teamCov = t => (teamN[t + 1] + 0.5 * teamN[t + 4]) / NS * 100;", "const teamCov = t => (teamN[t + 1] + 0.5 * teamN[t + 5]) / NS * 100;")
    s = rep(s, "cellGain = (v, me, steal) => v === me ? 0 : !v ? 1 : v === me + 3 ? 0.5 : v > 3 ? (1 + steal) * 0.5 : steal;", "cellGain = (v, me, steal) => v === me ? 0 : !v ? 1 : v === me + 4 ? 0.5 : v > 4 ? (1 + steal) * 0.5 : steal;")
    s = rep(s, "uniform vec3 uWetA[3]; uniform vec3 uDryA[3];", "uniform vec3 uWetA[4]; uniform vec3 uDryA[4];")
    s = rep(s, "float tc = floor(mod(vTeam + 0.25, 3.0)), dilA = vTeam > 2.5 ? 0.5 : 1.0;", "float tc = floor(mod(vTeam + 0.25, 4.0)), dilA = vTeam > 3.5 ? 0.5 : 1.0;")
    s = rep(s, "vec3 wetC = tc < 0.5 ? uWetA[0] : tc < 1.5 ? uWetA[1] : uWetA[2];", "vec3 wetC = tc < 0.5 ? uWetA[0] : tc < 1.5 ? uWetA[1] : tc < 2.5 ? uWetA[2] : uWetA[3];")
    s = rep(s, "vec3 dryC = tc < 0.5 ? uDryA[0] : tc < 1.5 ? uDryA[1] : uDryA[2];", "vec3 dryC = tc < 0.5 ? uDryA[0] : tc < 1.5 ? uDryA[1] : tc < 2.5 ? uDryA[2] : uDryA[3];")
    s = rep(s, "pTeam[nP] = team % 3;", "pTeam[nP] = team % 4;")
    s = rep(s, "const splCol = t => { splTmp.set(TEAMS[t % 3].wet); if (t >= 3) splTmp.lerp(COLW, 0.45); return splTmp; }", "const splCol = t => { splTmp.set(TEAMS[t % 4].wet); if (t >= 4) splTmp.lerp(COLW, 0.45); return splTmp; }")
    s = rep(s, "potClaim(p, team % 3)", "potClaim(p, team % 4)")
    s = rep(s, "team: team % 3 });", "team: team % 4 });")
    s = rep(s, "const v = painted[k]; if (v < 1 || v > 3 || v - 1 === D.team || Math.abs(sY[k] - y) > 1.2) continue;", "const v = painted[k]; if (v < 1 || v > 4 || SIDE[v - 1] === SIDE[D.team] || Math.abs(sY[k] - y) > 1.2) continue;")
    s = rep(s, "teamN[v]--; painted[k] = v + 3; teamN[v + 3]++; n++;", "teamN[v]--; painted[k] = v + 4; teamN[v + 4]++; n++;")
    s = rep(s, "const t = vTeamA[q]; if (t >= 3 || t === D.team) continue;", "const t = vTeamA[q]; if (t >= 4 || SIDE[t] === SIDE[D.team]) continue;")
    s = rep(s, "vTeamA[q] = t + 3; teamAllDirty = true;", "vTeamA[q] = t + 4; teamAllDirty = true;")
    s = rep(s, "for (const pass of [0, 1]) for (let t = 0; t < 3; t++) {", "for (const pass of [0, 1]) for (let t = 0; t < 4; t++) {")
    s = rep(s, "if (!v || (v - 1) % 3 !== t) continue; const dil = v > 3,", "if (!v || (v - 1) % 4 !== t) continue; const dil = v > 4,")
    s = rep(s, "const t = (v - 1) % 3, h1 = ", "const t = (v - 1) % 4, h1 = ")
    s = rep(s, "g.fillStyle = cols[t]; g.globalAlpha = v > 3 ? 0.6 : 1;", "g.fillStyle = cols[t]; g.globalAlpha = v > 4 ? 0.6 : 1;")
    # (the CPU's worth of a cell: a teammate's paint counts as its own)
    s = rep(s, "for (let v = 0; v < 16; v++) { gainT[v] = cellGain(v, me, stealW); ownT[v] = v === me ? 1 : v === me + 3 ? 0.5 : 0; }", "for (let v = 0; v < 16; v++) { gainT[v] = sdGain(v, D, stealW); ownT[v] = sdOwn(v, D); }")
    s = rep(s, "g += cellGain(painted[k], me, AI.steal);", "g += sdGain(painted[k], D, AI.steal);")
    # ---- the fourth fighter
    s = rep(s, "const P = newBlob(0, false), H = newBlob(1, true), H2 = newBlob(2, true);", "const P = newBlob(0, false), H = newBlob(1, true), H2 = newBlob(2, true), H3 = newBlob(3, true);")
    s = rep(s, "steer: 0, kos: 0, flats: 0, outs: 0, outWhy: {},", "steer: 0, kos: 0, flats: 0, outs: 0, outWhy: {}, hearts: 0, selfOuts: 0, elimNow: false, elimAt: -1, elimBy: null, place: 0,")
    s = rep(s, "const L2 = makeCpuLook(H2, TEAMS[2].wet);\nH.look = LH; H2.look = L2;", "const L2 = makeCpuLook(H2, TEAMS[2].wet), L3 = makeCpuLook(H3, TEAMS[3].wet);\nH.look = LH; H2.look = L2; H3.look = L3; L3.wear = makeWear(L3.body); L3.wearing = { head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null, iris: 'brown' };")
    s = rep(s, "for (const L of [LH, L2]) { const head =", "for (const L of [LH, L2, L3]) { const head =")
    s = rep(s, "attachSlime(L2.V, L2.wear, L2.mat.color);", "attachSlime(L2.V, L2.wear, L2.mat.color); attachSlime(L3.V, L3.wear, L3.mat.color);")
    s = rep(s, "cpuLook(L2, dt, rdt, ke, kf, playing); iceFrame(rdt);", "cpuLook(L2, dt, rdt, ke, kf, playing); cpuLook(L3, dt, rdt, ke, kf, playing); iceFrame(rdt);")
    s = rep(s, "function lodPass() { blobLOD(body); blobLOD(cBody); blobLOD(L2.body); }", "function lodPass() { blobLOD(body); blobLOD(cBody); blobLOD(L2.body); blobLOD(L3.body); }")
    s = rep(s, "const lookOf = D => D === P ? myLook : D === H ? LH.wearing : L2.wearing;", "const lookOf = D => D === P ? myLook : D === H ? LH.wearing : D === H3 ? L3.wearing : L2.wearing;")
    s = rep(s, "L2.drop, L2.shadow, L2.warn, L2.warnFill, L2.mark, L2.foeMark, L2.stars,", "L2.drop, L2.shadow, L2.warn, L2.warnFill, L2.mark, L2.foeMark, L2.stars, L3.drop, L3.shadow, L3.warn, L3.warnFill, L3.mark, L3.foeMark, L3.stars,")
    s = rep(s, "L2.drop.visible = L2.shadow.visible = false; // the studio shows your blob alone", "L2.drop.visible = L2.shadow.visible = false; L3.drop.visible = L3.shadow.visible = false; // the studio shows your blob alone")
    for a in ["kcamEnd(); kcamUsed = false; for (const D of [P, H, H2]) {", "puffIM.visible = false; for (const D of [P, H, H2]) if (D) D.smk = null; }", "grvGeo.setDrawRange(0, 0); for (const D of [P, H, H2]) if (D && D.grv)",
              "camSnap = true;\n  for (const D of [P, H, H2]) if (D) {", "portCam.updateMatrixWorld(); }\n  for (const o of [P, H, H2]) vicLayer(o, o === D);", "const ghosts = []; for (const o of [P, H, H2]) {",
              "strand.visible = stWas; for (const o of [P, H, H2]) vicLayer(o,", "if (post) try { const ds = [P, H, H2];"]:
        s = rep(s, a, a.replace('[P, H, H2]', '[P, H, H2, H3]'))
    s = rep(s, "for (const D of [H, H2]) D.rank = clamp(", "for (const D of [H, H2, H3]) D.rank = clamp(")
    s = rep(s, "const NAMES = ['You', 'Smudge', 'Doodle'],", "const NAMES = ['You', 'Smudge', 'Doodle', 'Blot'],")
    s = rep(s, "NAMES[2] = pool[Math.floor(Math.random() * pool.length)]; rollRivalRanks(); }", "NAMES[2] = pool.splice(Math.floor(Math.random() * pool.length), 1)[0]; NAMES[3] = pool[Math.floor(Math.random() * pool.length)]; rollRivalRanks(); }")
    s = rep(s, "const colVars = D => D === P ? ['var(--ink)', 'var(--ink-hi)'] : D === H ? ['var(--holy)', 'var(--holy-hi)'] : ['var(--wolf)', 'var(--wolf-hi)'];", "const colVars = D => D === P ? ['var(--ink)', 'var(--ink-hi)'] : D === H ? ['var(--holy)', 'var(--holy-hi)'] : D === H3 ? ['var(--fox)', 'var(--fox-hi)'] : ['var(--wolf)', 'var(--wolf-hi)'];")
    # ---- the modes, the sides
    s = rep(s, "['trio', '3-way', 'You and two rivals']];", "['trio', '3-way', 'You and two rivals'], ['ffa', 'Showdown', 'Four of you, two hearts each'], ['duo', 'Showdown 2v2', 'You and a teammate, two hearts each']];")
    s = rep(s, "let mode = MODES.some(m => m[0] === store.mode) ? store.mode : 'duel', ACTIVE = [P, H];", "let mode = MODES.some(m => m[0] === store.mode) ? store.mode : 'duel', ACTIVE = [P, H], SIDE = [0, 1, 2, 3]; // (SIDE: who's with whom, by team; in 2v2 you and your teammate are one side)\nfunction isShow() { return mode === 'ffa' || mode === 'duo'; }\nconst sideOf = D => SIDE[D.team], ally = (A, B) => !!A && !!B && A !== B && SIDE[A.team] === SIDE[B.team];")
    s = rep(s, "function applyMode() { ARENA = mode === 'trio' ? ARENA_MAX : 26.4; VS_CFG.pots = mode === 'trio' ? 11 : 8; VS_CFG.rivals = mode === 'trio' ? 17 : 12; ACTIVE = mode === 'solo' ? [P] : mode === 'trio' ? [P, H, H2] : [P, H]; }",
               "function applyMode() { const sd = isShow(); ARENA = mode === 'trio' || sd ? ARENA_MAX : 26.4; VS_CFG.pots = mode === 'trio' ? 11 : sd ? 12 : 8; VS_CFG.rivals = mode === 'trio' || sd ? 17 : 12; ACTIVE = mode === 'solo' ? [P] : mode === 'trio' ? [P, H, H2] : sd ? [P, H, H2, H3] : [P, H]; SIDE = mode === 'duo' ? [0, 1, 1, 0] : [0, 1, 2, 3]; teamHues(); }")
    s = rep(s, "f = ACTIVE.filter(o => o !== D); foesC.set(D, f);", "f = ACTIVE.filter(o => o !== D && SIDE[o.team] !== SIDE[D.team]); foesC.set(D, f);")
    s = rep(s, "function other(D) { if (mode !== 'trio') return D === P ? H : P;", "function other(D) { if (mode !== 'trio' && !isShow()) return D === P ? H : P;")
    s = rep(s, "const s = -Math.hypot(o.x - D.x, o.z - D.z) + (o === P ? 3 : 0) + (teamCov(o.team) - teamCov(D.team)) * 0.4;", "const s = -Math.hypot(o.x - D.x, o.z - D.z) + (o === P ? (isShow() ? 1.5 : 3) : 0) + (isShow() ? (SD_HEARTS - (o.hearts | 0)) * 2.5 : (teamCov(o.team) - teamCov(D.team)) * 0.4);")
    s = rep(s, "if (mode === 'trio' && (ai.focusT = (ai.focusT || 0) - dt) <= 0)", "if ((mode === 'trio' || isShow()) && (ai.focusT = (ai.focusT || 0) - dt) <= 0)")
    s = rep(s, "const atYou = mode !== 'trio' || other(D) === P;", "const atYou = (mode !== 'trio' && !isShow()) || other(D) === P;")
    s = rep(s, "cap = mode === 'trio' ? 2 : 1;", "cap = mode === 'trio' || isShow() ? 2 : 1;")
    s = rep(s, "banner(mode === 'trio' && other(D) !== P ? nameOf(D) + ' took a rocket' : 'Rocket incoming!', 'Stay out of the ring');", "banner((mode === 'trio' || isShow()) && other(D) !== P ? (ally(D, P) ? 'Your teammate took a rocket' : nameOf(D) + ' took a rocket') : 'Rocket incoming!', ally(D, P) ? 'It won\\'t hit you' : 'Stay out of the ring');")
    s = rep(s, "else if (mode !== 'trio' || other(D) === P) banner('Turret!', 'Keep out of its shots');", "else if ((mode !== 'trio' && !isShow()) || other(D) === P) banner('Turret!', 'Keep out of its shots');")
    # ---- the start: four starts on the map, two heartbeats each, the bigger clock
    s = rep(s, "let sH2 = null; if (mode === 'trio') {", "let sH2 = null, sH3 = null; if (mode === 'trio' || isShow()) {")
    s = rep(s, "if (sH2) Object.assign(CSTART2, { x: sH2.x, z: sH2.z, yaw: Math.atan2(-sH2.x, -sH2.z) });",
               "if (sH2 && isShow()) { const d2 = navField([[sH2.id, 0]]); let b3 = -1; for (const n of nodes) { if (!spawnOK(n) || !(dP[n.id] < 1e6) || !(dH[n.id] < 1e6) || !(d2[n.id] < 1e6)) continue; const sc3 = Math.min(dP[n.id], dH[n.id], d2[n.id]) + R() * 2; if (sc3 > b3) { b3 = sc3; sH3 = n; } } if (!sH3) return false; Object.assign(CSTART3, { x: sH3.x, z: sH3.z, yaw: Math.atan2(-sH3.x, -sH3.z) }); }\n  if (sH2) Object.assign(CSTART2, { x: sH2.x, z: sH2.z, yaw: Math.atan2(-sH2.x, -sH2.z) });")
    s = rep(s, "const nearSpawn = (n, r) => dist2(n, sP) < r || dist2(n, sH) < r || (sH2 && dist2(n, sH2) < r);", "const nearSpawn = (n, r) => dist2(n, sP) < r || dist2(n, sH) < r || (sH2 && dist2(n, sH2) < r) || (sH3 && dist2(n, sH3) < r);")
    s = rep(s, "if ([START, CSTART, CSTART2].some(s =>", "if ([START, CSTART, CSTART2, CSTART3].some(s =>")
    s = rep(s, "resetBlob(H2, CSTART2.x, CSTART2.z, CSTART2.yaw); aiReset(H2);\n  if (mode === 'solo') H.st = 'out'; if (mode !== 'trio') H2.st = 'out';",
               "resetBlob(H2, CSTART2.x, CSTART2.z, CSTART2.yaw); aiReset(H2); resetBlob(H3, CSTART3.x, CSTART3.z, CSTART3.yaw); aiReset(H3);\n  if (mode === 'solo') H.st = 'out'; if (mode !== 'trio' && !isShow()) H2.st = 'out'; if (!isShow()) H3.st = 'out'; for (const D of ACTIVE) D.hearts = isShow() ? SD_HEARTS : 0; sdEndT = 0; sdSpecEnd(); { const el = $('sdBar'); if (el) { el._built = false; el._sig = ''; } }")
    s = rep(s, "L2.drop.visible = L2.shadow.visible = mode === 'trio'; Object.assign(L2.look, { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 }); hud.classList.toggle('trio', mode === 'trio');",
               "L2.drop.visible = L2.shadow.visible = mode === 'trio' || isShow(); Object.assign(L2.look, { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 }); L3.drop.visible = L3.shadow.visible = isShow(); Object.assign(L3.look, { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0, flatK: 0 }); hud.classList.toggle('trio', mode === 'trio'); hud.classList.toggle('sdmode', isShow());")
    s = rep(s, "matchLeft = mode === 'solo' ? SOLO_T : MATCH_T;", "matchLeft = mode === 'solo' ? SOLO_T : isShow() ? SD_T : MATCH_T;")
    # (2v2: your teammate starts in the basin nearest yours)
    s = rep(s, "  order.forEach((D, i) => { if (best[i]) got.set(D, best[i]); });\n  return got;",
               "  if (mode === 'duo' && best.length >= 4) { const b0 = best[0], rest = best.slice(1).sort((a, b) => Math.hypot(a.x - b0.x, a.z - b0.z) - Math.hypot(b.x - b0.x, b.z - b0.z)); got.set(P, b0); got.set(H3, rest[0]); got.set(H, rest[1]); got.set(H2, rest[2]); return got; }\n  order.forEach((D, i) => { if (best[i]) got.set(D, best[i]); });\n  return got;")
    # (the CPUs: keener on knock-outs)
    s = rep(s, "closeSide(true); AI = AI_LV[diff]; mapUsed = true;", "closeSide(true); AI = isShow() ? Object.assign({}, AI_LV[diff], SD_AI[diff]) : AI_LV[diff]; mapUsed = true;")
    # (and they go looking for a fight: they sense a rival within a radius, wall or no wall, and with enough in the tank they head for it)
    s = rep(s, "  const O = other(D), ai = D.ai, vis = aiCanSee(D, O), was = ai.o && ai.o.st !== 'lost';", "  const O = other(D), ai = D.ai, vis = aiCanSee(D, O) || sdSense(D, O), was = ai.o && ai.o.st !== 'lost';")
    s = rep(s, "  // 5) a roller nearby is free paint\n", "  // (v254) Showdown: paint is only fuel; with enough in the tank it goes looking for its rival\n  if (isShow() && AI.seek && !sunNow && D.paint > Math.max(0.4, need + 0.12) && O.st === 'play' && O.immuneT <= 0.5 && Math.random() < AI.seek) { const sn = NAV.at(O.x, O.z, O.y); if (sn && nDist[sn.id] < Infinity && nDist[sn.id] > 3) return aiGo(D, sn, 'seek'); }\n  // 5) a roller nearby is free paint\n")
    # ---- teammates never hurt each other: traps, the freeze, turret shots, bumping into each other
    s = rep(s, "if (D === T.owner || D.st !== 'play' || D.rocket || D.turret || D.immuneT > 0 || D.dashT > 0) continue;", "if (D === T.owner || ally(D, T.owner) || D.st !== 'play' || D.rocket || D.turret || D.immuneT > 0 || D.dashT > 0) continue;")
    s = rep(s, "for (const B of ACTIVE) if (B !== D && B.ai) F.roll.set(B,", "for (const B of ACTIVE) if (B !== D && !ally(B, D) && B.ai) F.roll.set(B,")
    s = rep(s, "if (B === D || B.st !== 'play' || B.rocket) continue; // (down in a basin", "if (B === D || ally(B, D) || B.st !== 'play' || B.rocket) continue; // (down in a basin")
    s = rep(s, "else { banner(nameOf(D) + '’s flash freeze!',", "else if (ally(D, P)) banner(nameOf(D) + '’s flash freeze!', 'It freezes your rivals'); else { banner(nameOf(D) + '’s flash freeze!',")
    s = rep(s, "let hit = null; for (const B of ACTIVE) { if (B === s.by || B.st !== 'play' || B.rocket) continue;", "let hit = null; for (const B of ACTIVE) { if (B === s.by || ally(B, s.by) || B.st !== 'play' || B.rocket) continue;")
    s = rep(s, "  const dx = H.x - P.x, dz = H.z - P.z, d = Math.hypot(dx, dz), dy = H.y - P.y, gP = P.giantT > 0, gH = H.giantT > 0;\n",
               "  const dx = H.x - P.x, dz = H.z - P.z, d = Math.hypot(dx, dz), dy = H.y - P.y, gP = P.giantT > 0, gH = H.giantT > 0;\n"
               "  if (SIDE[P.team] === SIDE[H.team]) { if (d > PR * 2 || Math.abs(dy) > 0.95 || P.air || H.air) return; const nx = dx / (d || 1), nz = dz / (d || 1), push = (PR * 2 - d) / 2 + 0.02; for (const [D, sx] of [[P, -1], [H, 1]]) { const x = D.x + nx * push * sx, z = D.z + nz * push * sx; if (!blockedAt(x, z, D.y)) { D.x = x; D.z = z; } } return; } // (teammates just nudge past each other)\n")
    # ---- knock-outs: a heart each; with none left, out
    s = rep(s, "function knockOut(D, reason, by) {\n  if (D.st === 'ko' || state !== 'play') return;\n", "function knockOut(D, reason, by) {\n  if (D.st === 'ko' || state !== 'play') return;\n  const sdLast = isShow() && sdHit(D, by);\n")
    s = rep(s, "D.koT = by ? RESPAWN_T : SELF_RESPAWN_T;", "D.koT = sdLast ? SD_OUT_T : by ? RESPAWN_T : SELF_RESPAWN_T;")
    s = rep(s, "if (mode !== 'trio' || by === P) banner((reason === 'fall' && by ?", "if (isShow()) {} else if (mode !== 'trio' || by === P) banner((reason === 'fall' && by ?")
    s = rep(s, "if (by === P) buzz([20, 30, 20]); }\n}\nfunction openRun(", "if (by === P) buzz([20, 30, 20]); }\n  if (isShow()) { sdCheck(); sdKoNote(D, reason, by); sdHud(); }\n}\nfunction openRun(")
    s = rep(s, "if (D.st === 'ko') { if (D.rag) ragStep(D, dt); D.koT -= dt; if (D.koT <= 0) { if (D.rag) ragEnd(D); respawnBlob(D); } return; }", "if (D.st === 'ko') { if (D.rag) ragStep(D, dt); D.koT -= dt; if (D.koT <= 0) { if (D.rag) ragEnd(D); if (D.elimNow) sdOut(D); else respawnBlob(D); } return; }")
    # ---- the clock, the end
    s = rep(s, "runT += dt; matchLeft -= dt;", "runT += dt; if (!(sdEndT > 0)) matchLeft -= dt;")
    s = rep(s, "leadAcc += dt; if (mode !== 'solo' && leadAcc > 0.3 && runT > 8)", "leadAcc += dt; if (mode !== 'solo' && !isShow() && leadAcc > 0.3 && runT > 8)")
    s = rep(s, "    if (matchLeft <= 0) { matchLeft = 0; if (!ACTIVE.some(pounding)) endMatch(); }\n  } else if (state === 'dead')", "    if (matchLeft <= 0) { matchLeft = 0; if (!ACTIVE.some(pounding)) endMatch(); }\n    if (sdEndT > 0 && state === 'play') { sdEndT -= dt; if (sdEndT <= 0) endShowdown(false); }\n  } else if (state === 'dead')")
    s = rep(s, "function endMatch() {\n  if (state !== 'play') return;\n", "function endMatch() {\n  if (state !== 'play') return;\n  if (isShow()) return endShowdown(true);\n")
    s = rep(s, "setTimeout(() => { if (state === 'play' && !tut) banner('Paint it ' + colorOf().name.toLowerCase() + '!',", "setTimeout(() => { if (state === 'play' && !tut && isShow()) banner(mode === 'duo' ? 'Last pair standing!' : 'Last one standing!', 'Two hearts each', true); else if (state === 'play' && !tut) banner('Paint it ' + colorOf().name.toLowerCase() + '!',")
    s = rep(s, "  $('howGoal').textContent = mode === 'solo' ?", "  $('howGoal').textContent = isShow() ? (mode === 'duo' ? 'Two against two, two hearts each. A knock-out costs a heart and with none left you\\'re out. The last pair standing wins.' : 'Four of you, two hearts each. A knock-out costs a heart and with none left you\\'re out. The last one standing wins.') : mode === 'solo' ?")
    # ---- the hearts on the scoreboard, kept up with the score
    s = rep(s, '<div class="tug" id="meter"><i class="tYou" id="tugYou"></i><i class="tCpu" id="tugCpu"></i><i class="tCpu2" id="tugCpu2"></i></div>',
               '<div class="tug" id="meter"><i class="tYou" id="tugYou"></i><i class="tCpu" id="tugCpu"></i><i class="tCpu2" id="tugCpu2"></i></div>\n        <div class="sdbar" id="sdBar" hidden role="img" aria-label="Hearts"></div>')
    s = rep(s, "  if (ct !== lastClock) { lastClock = ct; const ce = $('clock'); ce.textContent = ct; ce.classList.toggle('hurry', t <= 10 && state === 'play'); }\n}",
               "  if (ct !== lastClock) { lastClock = ct; const ce = $('clock'); ce.textContent = ct; ce.classList.toggle('hurry', t <= 10 && state === 'play'); }\n  sdHud();\n}")
    s = rep(s, '<div class="orbs" id="orbs"></div>', '<div class="sdspec" id="sdSpec" hidden aria-live="polite"><span><span id="sdSpecW">Watching</span><b id="sdSpecN"></b></span><button type="button" id="sdSkip" aria-label="Skip ahead: the rest of the match at high speed"><svg viewBox="0 0 24 16" aria-hidden="true"><path d="M1.5 1.5 11 8l-9.5 6.5zM12.5 1.5 22 8l-9.5 6.5z"/></svg><span id="sdSkipL">Skip</span></button></div>\n  <div class="orbs" id="orbs"></div>')
    # ---- a third rival's pointer at the edge
    s = rep(s, '<div class="foeptr two" id="foePtr2"><i></i><u><b></b></u></div>', '<div class="foeptr two" id="foePtr2"><i></i><u><b></b></u></div>\n  <div class="foeptr three" id="foePtr3"><i></i><u><b></b></u></div>')
    s = rep(s, "  if (dt > 0) { const n = Math.ceil(dt / 0.012); for (let i = 0; i < n; i++) step(dt / n); }\n  visuals(dt, rdt); flushTrail(); pbarTick(rdt); lockerTick(); dipTick(rdt);",
               "  const ffK = spec && spec.ff && state === 'play' && dt > 0 ? SD_FF : 1; dt *= ffK; // (v254: a Showdown you're out of, skipped ahead)\n  if (dt > 0) { const n = Math.ceil(dt / 0.012); for (let i = 0; i < n; i++) step(dt / n); }\n  if (ffK > 1) dt = Math.min(dt, 0.05); // (the drawing's own timing no faster than a slow frame's)\n  visuals(dt, rdt); flushTrail(); pbarTick(rdt); lockerTick(); dipTick(rdt);")
    s = rep(s, "      const yTop = Math.min(0.7, 1 - 200 / Hh), m =", "      const yTop = Math.min(0.7, 1 - (isShow() ? 2 * (sdCardBot() + 30) : 200) / Hh), m =") # (the Showdown card is taller: the pins stay below it)
    s = rep(s, "foePointer($('foePtr2'), H2, playing && mode === 'trio');", "foePointer($('foePtr2'), H2, playing && (mode === 'trio' || isShow())); foePointer($('foePtr3'), H3, playing && mode === 'ffa');")
    # ---- tags: your teammate's too, and everyone's hearts
    s = rep(s, "const playing = state === 'play', fs = playing ? foes(P) : [], cp = camera.position, vis = [];", "const playing = state === 'play', fs = playing ? ACTIVE.filter(D => D !== P) : [], cp = camera.position, vis = [];")
    s = rep(s, "<span class=\"ntn\"></span>';\n  ntagsEl.appendChild(el); t = { el, rk: el.querySelector('b'), nm: el.querySelector('.ntn'),", "<span class=\"ntn\"></span><span class=\"nth\"></span>';\n  ntagsEl.appendChild(el); t = { el, rk: el.querySelector('b'), nm: el.querySelector('.ntn'), ht: el.querySelector('.nth'), hp: -2, al: false,")
    s = rep(s, "    const nm = nameOf(D), rk = rankOf(D), col = TEAMS[D.team].css;\n",
               "    const nm = nameOf(D), rk = rankOf(D), col = TEAMS[D.team].css;\n    { const hp = isShow() ? Math.max(0, D.hearts | 0) : -1; if (t.hp !== hp) { t.hp = hp; let hh = ''; if (hp >= 0) for (let i = 0; i < SD_HEARTS; i++) hh += HEART_SVG.replace('<svg', '<svg class=\"' + (i < hp ? 'on' : 'off') + '\"'); t.ht.innerHTML = hh; } const al = ally(D, P); if (t.al !== al) { t.al = al; t.el.classList.toggle('ally', al); } }\n")
    s = rep(s, "want = t.see * (1 - smoothstep(NTAG_NEAR, NTAG_FAR, t.d));", "want = (spec && spec.D === D ? 1 : t.see) * (1 - smoothstep(NTAG_NEAR, NTAG_FAR, t.d)); // (the one you're watching keeps its tag)")
    # ---- the knock-out flood when it was your last heart
    s = rep(s, '<span class="kofn" id="kofN">3</span><i>Respawn</i>', '<span class="kofn" id="kofN">3</span><i id="kofL">Respawn</i>')
    s = rep(s, "  kofEl.style.setProperty('--kc', col); kofEl.hidden = false; kofEl.classList.remove('badge', 'out');\n}",
               "  kofEl.style.setProperty('--kc', col); kofEl.hidden = false; kofEl.classList.remove('badge', 'out');\n"
               "  const el = isShow() && D.elimNow; kofEl.classList.toggle('elim', !!el); $('kofL').textContent = el ? (mode === 'duo' && ACTIVE.some(B => ally(B, P) && sdAlive(B)) ? 'Your teammate fights on' : 'Place') : 'Respawn';\n"
               "  if (el) { $('kofSmall').textContent = by ? 'Eliminated by' : 'Out of hearts'; kof.elim = true; kof.elimTxt = 'Out'; $('kofN').textContent = 'Out'; }\n}")
    s = rep(s, "if (kof.ph !== 'out') { const n = String(Math.max(1, Math.ceil(P.koT)));", "if (kof.ph !== 'out') { const n = kof.elim ? kof.elimTxt : String(Math.max(1, Math.ceil(P.koT)));")
    # ---- the camera once you're out: on someone still in it
    s = rep(s, "  else if (state === 'dead' || state === 'paused') {\n    if (state === 'dead' && outro)", "  else if (state === 'play' && spec && P.st === 'out' && specCam(rdt)) {}\n  else if (state === 'dead' || state === 'paused') {\n    if (state === 'dead' && outro)")
    # ---- the fight card, the vote: four
    s = rep(s, "foe2: { yaw: 0.38, low: 0.7, zoom: 0.96, ip: { expr: 'happy', wave: 1, roll: -0.12 } } };", "foe2: { yaw: 0.38, low: 0.7, zoom: 0.96, ip: { expr: 'happy', wave: 1, roll: -0.12 } }, foe3: { yaw: -0.36, low: 0.55, zoom: 0.97, ip: { expr: 'smirk', roll: 0.1 } }, ally: { yaw: 0.48, low: 0.85, zoom: 0.96, ip: { expr: 'glee', hand: 1, hop: 0.04, roll: -0.08 } } };")
    s = rep(s, "<small>' + (cls === 'me' ? 'You' : 'CPU') + '</small>", "<small>' + (cls === 'me' ? 'You' : cls === 'me ally' ? 'Teammate' : 'CPU') + '</small>")
    s = rep(s, "let h = card(P, playerName(), 'me'); if (mode !== 'solo') { h += card(H, NAMES[1], 'foe'); if (mode === 'trio') h += card(H2, NAMES[2], 'foe2'); }",
               "let h = card(P, playerName(), 'me'); if (mode === 'duo') h += card(H3, NAMES[3], 'me ally') + card(H, NAMES[1], 'foe') + card(H2, NAMES[2], 'foe2'); else if (mode !== 'solo') { h += card(H, NAMES[1], 'foe'); if (mode === 'trio' || mode === 'ffa') h += card(H2, NAMES[2], 'foe2'); if (mode === 'ffa') h += card(H3, NAMES[3], 'foe3'); }")
    s = rep(s, "$('vsRow').classList.toggle('trio', mode === 'trio');", "$('vsRow').classList.toggle('trio', mode === 'trio'); $('vsRow').classList.toggle('quad', isShow()); $('vsRow').classList.toggle('duo', mode === 'duo');")
    s = rep(s, "if (mode === 'trio') list.push([H2, $('vbox2'), VS_POSE.foe2]);", "if (mode === 'trio' || isShow()) list.push([H2, $('vbox2'), VS_POSE.foe2]); if (isShow()) list.push([H3, $('vbox3'), mode === 'duo' ? VS_POSE.ally : VS_POSE.foe3]);")
    s = rep(s, "who = [P, H]; if (mode === 'trio') who.push(H2);", "who = [P, H]; if (mode === 'trio' || isShow()) who.push(H2); if (isShow()) who.push(H3);")
    s = rep(s, "paintPath(u => pts[Math.min(pts.length - 1, Math.floor(u * (pts.length - 1)))], -7 + k, mode === 'solo' ? 0 : k % (mode === 'trio' ? 3 : 2));", "paintPath(u => pts[Math.min(pts.length - 1, Math.floor(u * (pts.length - 1)))], -7 + k, mode === 'solo' ? 0 : k % (mode === 'trio' ? 3 : mode === 'ffa' ? 4 : 2));")
    s = rep(s, "false, false, mode === 'solo' ? 0 : i % (mode === 'trio' ? 3 : 2)); }", "false, false, mode === 'solo' ? 0 : i % (mode === 'trio' ? 3 : mode === 'ffa' ? 4 : 2)); }")
    # ---- the victory screen for a Showdown
    s = rep(s, "board = ACTIVE.map(D => ({ D, pct: solo ? Math.round(info.you) : info.tot[D.team] })).sort((a, b) => b.pct - a.pct);", "board = ACTIVE.map(D => ({ D, pct: info.show ? 9 - (info.places[D.team] || 4) : solo ? Math.round(info.you) : info.tot[D.team] })).sort((a, b) => b.pct - a.pct);")
    s = rep(s, "  for (const e of board) e.place = 1 + board.filter(o => o.pct > e.pct).length;\n  let feat;", "  for (const e of board) e.place = info.show ? info.places[e.D.team] || 4 : 1 + board.filter(o => o.pct > e.pct).length;\n  let feat;")
    s = rep(s, "  if (solo || info.winner) feat = [solo ? P : info.winner];", "  if (info.show) feat = info.winners.slice().sort((a, b) => (b === P) - (a === P) || ally(b, P) - ally(a, P)).slice(0, 2);\n  else if (solo || info.winner) feat = [solo ? P : info.winner];")
    s = rep(s, "const happy = solo ? info.newBest : !!info.winner,", "const happy = info.show ? !info.draw : solo ? info.newBest : !!info.winner,")
    s = rep(s, "vicEl.style.setProperty('--vc-hi', lead === P ? 'var(--ink-hi)' : lead === H ? 'var(--holy-hi)' : 'var(--wolf-hi)');", "vicEl.style.setProperty('--vc-hi', colVars(lead)[1]);")
    s = rep(s, "  if (solo) { pl.className = 'vplace word'; pl.textContent = Math.round(info.you) + '%';", "  if (info.show) sdVicWords(info, feat, me);\n  else if (solo) { pl.className = 'vplace word'; pl.textContent = Math.round(info.you) + '%';")
    s = rep(s, "style=\"--cc:' + (e.D === P ? 'var(--ink-hi)' : e.D === H ? 'var(--holy-hi)' : 'var(--wolf-hi)') + ';animation-delay:", "style=\"--cc:' + colVars(e.D)[1] + ';animation-delay:")
    s = rep(s, "<b class=\"vcp\">' + e.pct + '%</b>", "<b class=\"vcp\">' + (info.show ? sdCardStat(e.D) : e.pct + '%') + '</b>")
    s = rep(s, "const won = solo ? info.newBest : info.winner === P;", "const won = solo ? info.newBest : info.show ? info.win > 0 : info.winner === P;")
    # ---- the results for a Showdown: no paint bar; the fighters, where they finished, their knock-outs and self-eliminations
    s = rep(s, "  const ppl = (solo ? [P] : trio ? [P, H, H2] : [P, H]).map(D => ({ D, pct:",
               "  if (info.show) { const sb = sdBoard(info), bd = $('board'); bd.className = 'board sd'; bd.innerHTML = sb.h; bd.hidden = false; $('judge').setAttribute('aria-label', sb.says.join('. ')); end.classList.add('sd'); end.dataset.next = ''; $('replayBtn').hidden = false; $('endBtn').querySelector('small').textContent = 'New canvas'; end.hidden = false; measureOutro(); setTimeout(() => $('endBtn').focus({ preventScroll: true }), 30); return; }\n  end.classList.remove('sd');\n  const ppl = (solo ? [P] : trio ? [P, H, H2] : [P, H]).map(D => ({ D, pct:")
    # ---- the event card
    s = rep(s, '<div class="evcard soon" data-ev="showdown" style="--ec:#8E5CFF"><button class="evmain" id="evShow" type="button" aria-disabled="true"><span class="evbar"><i>Coming soon</i></span>',
               '<div class="evcard" data-ev="showdown" style="--ec:#8E5CFF"><button class="evmain" id="evShow" type="button" aria-expanded="false" aria-controls="evShowPick"><span class="evbar"><i>Last one standing</i></span>')
    s = rep(s, '<span class="evtx"><b>Showdown</b><small>Last one painting</small></span>', '<span class="evtx"><b>Showdown</b><small>Two hearts each</small></span>')
    s = rep(s, '<img id="evShowArt" alt=""></span></button><i class="evsoon">Coming soon</i></div>',
               '<img id="evShowArt" alt=""></span></button><div class="evdrop" id="evShowPick" hidden role="group" aria-label="Which Showdown"><button type="button" data-m="ffa"><b>Free-for-all</b><small>Four of you, one left</small></button><button type="button" data-m="duo"><b>2 v 2</b><small>You and a teammate</small></button></div></div>')
    s = rep(s, "function evFold() { $('evVs').closest('.evcard').classList.remove('open'); $('evVsPick').hidden = true; $('evVs').setAttribute('aria-expanded', 'false'); }",
               "function evFold() { $('evVs').closest('.evcard').classList.remove('open'); $('evVsPick').hidden = true; $('evVs').setAttribute('aria-expanded', 'false'); evFoldShow(); }\nfunction evFoldShow() { $('evShow').closest('.evcard').classList.remove('open'); $('evShowPick').hidden = true; $('evShow').setAttribute('aria-expanded', 'false'); }")
    a0 = "$('evShow').addEventListener('click', () => { AU.init(); AU.nope(); const c = $('evShow').closest('.evcard'), old = c.querySelector('.evtoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'evtoast'; t.textContent = 'Showdown is coming soon'; c.appendChild(t); setTimeout(() => t.remove(), 1700); });"
    s = rep(s, a0, "$('evShow').addEventListener('click', uiClick(() => { const c = $('evShow').closest('.evcard'), open = !c.classList.contains('open'); if (open) { $('evVs').closest('.evcard').classList.remove('open'); $('evVsPick').hidden = true; $('evVs').setAttribute('aria-expanded', 'false'); } c.classList.toggle('open', open); $('evShowPick').hidden = !open; $('evShow').setAttribute('aria-expanded', String(open)); if (open) setTimeout(() => $('evShowPick').querySelector('[data-m=\"' + (mode === 'duo' ? 'duo' : 'ffa') + '\"]').focus({ preventScroll: true }), 30); }));\n$('evShowPick').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; AU.init(); AU.pop(); evPick(b.dataset.m); });")
    s = rep(s, "$('evVs').addEventListener('click', uiClick(() => { const c = $('evVs').closest('.evcard'), open = !c.classList.contains('open');", "$('evVs').addEventListener('click', uiClick(() => { evFoldShow(); const c = $('evVs').closest('.evcard'), open = !c.classList.contains('open');")
    # ---- the colours: the rivals' set with yours, and per mode
    old = s[s.index("  const wolf = c.id === 'purple' ? { wet: 0x19C9A6"):s.index("  const r = document.documentElement.style;\n  r.setProperty('--ink', css);")]
    assert old.count('\n') == 5, old
    s = s.replace(old, "  teamHues();\n")
    # ---- the Showdown code itself, before the event screen
    s = rep(s, "// ---------- Choose Event (v209): Play opens it.", js + "\n// ---------- Choose Event (v209): Play opens it.")
    # (its own small helpers the paint and the AI lean on)
    s = rep(s, "// ---------- Choose Event (v209): Play opens it.", """// a painted cell's worth to a blob, and how much it counts as its own: its side's paint (its own or a teammate's) is nothing to gain
function sdGain(v, D, steal) { if (!v) return 1; const t = (v - 1) % 4, dil = v > 4; return SIDE[t] === SIDE[D.team] ? (dil ? 0.5 : 0) : dil ? (1 + steal) * 0.5 : steal; }
function sdOwn(v, D) { if (!v) return 0; return SIDE[(v - 1) % 4] === SIDE[D.team] ? (v > 4 ? 0.5 : 1) : 0; }
// the rivals' colours: the third always stands apart from yours; in 2v2 your teammate wears your colour and both rivals the blue
const FOX = { wet: 0x19C9A6, dry: 0x0E6B58, css: '#19C9A6', hi: '#7FE8D3' }, FOX2 = { wet: 0xFFB21A, dry: 0x8E6200, css: '#FFB21A', hi: '#FFD27A' };
function teamHues() {
  const c = colorOf(), wolf = c.id === 'purple' ? { wet: 0x19C9A6, dry: 0x0E6B58, css: '#19C9A6', hi: '#7FE8D3' } : { wet: 0x8E5CFF, dry: 0x46297F, css: '#8E5CFF', hi: '#C4A8FF' };
  const fox = c.id === 'purple' || c.id === 'green' ? FOX2 : FOX, duo = mode === 'duo';
  const t2 = duo ? { wet: 0x2E9BFF, dry: 0x1C5592, css: '#2E9BFF', hi: '#7CC4FF' } : wolf, t3 = duo ? { wet: TEAMS[0].wet, dry: TEAMS[0].dry, css: TEAMS[0].css, hi: c.hi } : fox;
  for (const [i, t, L] of [[2, t2, L2], [3, t3, L3]]) {
    TEAMS[i].wet = t.wet; TEAMS[i].dry = t.dry; TEAMS[i].css = t.css; TEAM_COLS[i].setHex(t.wet); paintUniforms.uWetA.value[i].setHex(t.wet); paintUniforms.uDryA.value[i].setHex(t.dry);
    teamMats[i].color.setHex(t.wet); crownMats[i].color.setHex(t.wet); crownMats[i].emissive.setHex(t.wet).multiplyScalar(0.18); L.col.setHex(t.wet); L.xrayMat.color.setHex(t.wet);
    const wc = new THREE.Color(t.wet).lerp(COL_WHITE, 0.5); L.warn.material.color.copy(wc); L.warnFill.material.color.copy(wc); if (L.warnBase) L.warnBase.copy(wc); partPool(colMat(t.wet));
  }
  const r = document.documentElement.style; r.setProperty('--wolf', t2.css); r.setProperty('--wolf-hi', t2.hi); r.setProperty('--fox', t3.css); r.setProperty('--fox-hi', t3.hi);
  recolorSplashes();
}
$('sdSkip').addEventListener('click', () => { AU.init(); AU.ui(); if (state === 'play' && isShow() && P.st === 'out') sdSkipOn(); });
// ---------- Choose Event (v209): Play opens it.""")
    return s
