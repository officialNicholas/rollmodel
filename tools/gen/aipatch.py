f='/home/claude/paint-the-canvas.html'; s=open(f).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n, (a[:90], s.count(a)); s=s.replace(a,b)
rep("grab: 0.3, pivot: false, speed: 0.9,  slip: 0.35 },", "grab: 0.3, pivot: false, speed: 0.9,  slip: 0.35, plan: 0,    econ: 0, coffinHunt: 0,   coffinFlee: 0.1 },")
rep("grab: 0.7, pivot: false,  speed: 0.97, slip: 0.06 },", "grab: 0.7, pivot: false,  speed: 0.97, slip: 0.06, plan: 0.45, econ: 1, coffinHunt: 0.4, coffinFlee: 0.55 },")
rep("grab: 1,   pivot: false,  speed: 1.0,  slip: 0 },", "grab: 1,   pivot: false,  speed: 1.0,  slip: 0,    plan: 1,    econ: 1, coffinHunt: 1,   coffinFlee: 0.95 },")
rep("let AI = AI_LV.medium;", "AI_LV.hardOld = Object.assign({}, AI_LV.hard, { plan: 0, econ: 0, coffinHunt: 0, coffinFlee: 0 }); // the previous hard CPU, kept for testing\nlet AI = AI_LV.medium;")
rep("  NAV.nodes = nodes; NAV.at = at; NAV.near = near; NAV.cell = cellOf; NN = nodes.length;",
"""  // for each spot, the spots a pound there would cover (same level, inside the splat)
  const dOff = [0], dIds = [], PR2 = 4.4 * 4.4;
  for (const n of nodes) { for (let dj = -5; dj <= 5; dj++) for (let di = -5; di <= 5; di++) for (const m of cellOf(n.i + di, n.j + dj)) if (Math.abs(m.h - n.h) < 0.35 && (m.x - n.x) ** 2 + (m.z - n.z) ** 2 < PR2) dIds.push(m.id); dOff.push(dIds.length); }
  NAV.dOff = Int32Array.from(dOff); NAV.dIds = Int32Array.from(dIds);
  NAV.nodes = nodes; NAV.at = at; NAV.near = near; NAV.cell = cellOf; NN = nodes.length;""")
rep("  if (nDist.length < NN) { const c = NN + 512; nDist = new Float32Array(c);", "  if (nDist.length < NN) { const c = NN + 512; pudNear = new Uint8Array(c); nDist = new Float32Array(c);")
rep("let NN = 0, nDist = new Float32Array(1),", "let NN = 0, pudNear = new Uint8Array(1), nDist = new Float32Array(1),")
rep("const potNode = p => NAV.at(p.x, p.z, p.y);", "const potNode = p => NAV.at(p.x, p.z, p.y);\n// what a pound at node n would paint, counting stolen ground at the steal weight\nfunction poundVal(id) { let v = 0; const o = NAV.dOff, ids = NAV.dIds; for (let k = o[id]; k < o[id + 1]; k++) v += nGain[ids[k]]; return v; }")
rep("""  const need = (coffin ? cl / (cfg.speed * 0.85) * cfg.drain * 1.2 : 0.3) + AI.inkPad + 0.06; ai.need = need;""",
"""  let need = (coffin ? cl / (cfg.speed * 0.85) * cfg.drain * 1.2 : 0.3) + AI.inkPad + 0.06;
  // enough blood to last the match: no more trips to a coffin
  if (AI.econ && D.paint > matchLeft * cfg.drain * 1.1 + 0.05) need = -1;
  ai.need = need;""")
rep("""  if (o.st === 'play' && o.imm <= 0.5) {
    const od = Math.hypot(o.x - D.x, o.z - D.z),""", """  // hiding in a coffin is no protection: pound it, as long as the sun isn't out
  if (o.st === 'hide' && O.st === 'hide' && o.imm <= 0.3 && AI.coffinHunt > 0 && wxPhase !== 'sun' && wxPhase !== 'warn' && D.paint > SLAM_COST + 0.08) {
    const pn = NAV.at(o.x, o.z, o.y), pd = pn ? nDist[pn.id] : Infinity;
    if (pn && pd < 16 && D.slamCD <= pd / speed + 0.3 && Math.random() < AI.coffinHunt) return aiGo(D, pn, 'hunt');
  }
  if (o.st === 'play' && o.imm <= 0.5) {
    const od = Math.hypot(o.x - D.x, o.z - D.z),""")
rep("""  // 6) paint: the route that sweeps through the most fresh and stolen ground for its length
  const cand = [];
  for (const n of NAV.nodes) {
    const d = nDist[n.id]; if (!(d < Infinity) || d < 2.2 || d > 26) continue;
    let v = nGain[n.id]; const nb = n.nb; for (let e = 0; e < nb.length; e += 2) v += nGain[nb[e]] * 0.5;
    const turn = Math.abs(wrapA(Math.atan2(n.x - D.x, n.z - D.z) - D.yaw)) / Math.PI;
    cand.push([(nAcc[n.id] + 0.7 * v) / (d + 2.5) * (1 - 0.4 * turn), n.id]);
  }""", """  // 6) paint: the route that sweeps through the most fresh and stolen ground for its length.
  //    With a pound coming up, a spot also counts what pounding it would paint (a pound covers as much as ~15 s of rolling),
  //    and a pound next to boiling water refills the tank too.
  const cand = [], sunNow = wxPhase === 'sun' || wxPhase === 'warn';
  const planOK = AI.plan > 0 && !sunNow && (D.paint > SLAM_COST + Math.max(0.12, need * 0.6) || D.paint < 0.6);
  if (planOK) { pudNear.fill(0, 0, NN); for (const r of rivals) if (r.on) NAV.near(r.x, r.z, r.y, SLAM_R * 0.5 + r.rad - 0.6, n => { if (Math.hypot(n.x - r.x, n.z - r.z) > r.hit + 0.35) pudNear[n.id] = 1; }); }
  const refillV = 220 * clamp(1 - D.paint, 0, 1), richOK = D.paint > SLAM_COST + Math.max(0.12, need * 0.6);
  const pv = n => { if (!planOK) return 0; const d = nDist[n.id]; if (D.slamCD > d / speed + 0.25) return 0; const pu = pudNear[n.id]; if (!pu && !richOK) return 0; return (poundVal(n.id) + (pu ? refillV : 0)) * AI.plan; };
  for (const n of NAV.nodes) {
    const d = nDist[n.id]; if (!(d < Infinity) || d < 2.2 || d > 26) continue;
    let v = nGain[n.id]; const nb = n.nb; for (let e = 0; e < nb.length; e += 2) v += nGain[nb[e]] * 0.5;
    const turn = Math.abs(wrapA(Math.atan2(n.x - D.x, n.z - D.z) - D.yaw)) / Math.PI, p = (n.i + n.j) % 2 ? 0 : pv(n);
    cand.push([(nAcc[n.id] + 0.7 * v + p) / (d + 2.5) * (1 - 0.4 * turn), n.id, p]);
  }""")
rep("""    const cur = (nAcc[n.id] + 0.7 * v) / (nDist[n.id] + 2.5) * (1 - 0.4 * Math.abs(wrapA(Math.atan2(n.x - D.x, n.z - D.z) - D.yaw)) / Math.PI); if (cur > pick[0] * 0.78) pick = [cur, ai.tgt];
  }
  const tn = NAV.nodes[pick[1]];""", """    const p = ai.poundAt === ai.tgt ? pv(n) : 0, cur = (nAcc[n.id] + 0.7 * v + p) / (nDist[n.id] + 2.5) * (1 - 0.4 * Math.abs(wrapA(Math.atan2(n.x - D.x, n.z - D.z) - D.yaw)) / Math.PI); if (cur > pick[0] * 0.78) pick = [cur, ai.tgt, p];
  }
  const tn = NAV.nodes[pick[1]];
  const poundAt = pick[2] > 0 && pick[2] > 0.35 * (pick[0] * (nDist[tn.id] + 2.5)) ? tn.id : -1;""")
rep("ai.plan = { kind: 'nav', yaw, c, t: 0 }; ai.mode = 'paint'; ai.tgt = tn.id; return; } } }", "ai.plan = { kind: 'nav', yaw, c, t: 0 }; ai.mode = 'paint'; ai.tgt = tn.id; ai.poundAt = poundAt; return; } } }")
rep("  aiGo(D, tn, 'paint');\n}", "  aiGo(D, tn, 'paint'); ai.poundAt = poundAt;\n}")
rep("function aiReset(D) { D.ai = { mode: 'paint',", "function aiReset(D) { D.ai = { poundAt: -1, fleeRolled: false, mode: 'paint',")
rep("ai.path = path; ai.pi = 0; ai.tgt = n.id; ai.mode = mode; ai.atShelter = false; ai.goPot = null;", "ai.path = path; ai.pi = 0; ai.tgt = n.id; ai.mode = mode; ai.atShelter = false; ai.goPot = null; ai.poundAt = -1;")
rep("""  if (o && o.st === 'play' && O.st === 'play' && o.imm <= 0.45 && Math.abs(o.y - D.y) < 1.2) {
    const T = 0.55, sp = o.flat > 0 ? 0 : o.spd, px = o.x + Math.sin(o.yaw) * sp * T, pz = o.z + Math.cos(o.yaw) * sp * T;""", """  if (ai.poundAt >= 0 && ai.mode === 'paint') {
    const n = NAV.nodes[ai.poundAt];
    if (n && Math.hypot(n.x - D.x, n.z - D.z) < 0.95 && Math.abs(n.h - D.y) < 0.3) { ai.poundAt = -1; ai.thinkT = 0; if (D.paint > SLAM_COST + 0.03 || pudNear[n.id]) return useSlam(D); }
  }
  if (o && (o.st === 'play' || (o.st === 'hide' && AI.coffinHunt > 0)) && (O.st === 'play' || O.st === 'hide') && o.imm <= 0.45 && Math.abs(o.y - D.y) < 1.2) {
    const T = 0.55, sp = o.flat > 0 || o.st === 'hide' ? 0 : o.spd, px = o.x + Math.sin(o.yaw) * sp * T, pz = o.z + Math.cos(o.yaw) * sp * T;""")
rep("""  if (AI.covPound && ai.covT <= 0) { ai.covT = 0.45; if (!sunny && ai.mode !== 'shelter' && D.paint - SLAM_COST > (ai.need || 0.3) + 0.12 && Math.hypot(O.x - D.x, O.z - D.z) > 9 && localGain(D, 4.2) > AI.covPound) return useSlam(D); }""",
"""  if (AI.covPound && ai.covT <= 0) { ai.covT = 0.45; const endgame = AI.econ && matchLeft < 7 && D.paint > SLAM_COST; if (!sunny && ai.mode !== 'shelter' && (endgame || D.paint - SLAM_COST > (ai.need || 0.3) + 0.12) && Math.hypot(O.x - D.x, O.z - D.z) > 9 && localGain(D, 4.2) > AI.covPound * (endgame ? 0.5 : 1)) return useSlam(D); }""")
rep("""  let leave = !sunny && (D.paint > 0.95 || p.ink < 0.03 || (matchLeft < 8 && D.paint > 0.45));
  if (leave && AI.camp > 0 && O.st === 'play' && slamReady(O) && Math.hypot(O.x - D.x, O.z - D.z) < 3.6 && ai.campT < AI.camp) { ai.campT += dt; leave = false; }
  if (!leave) return;""", """  let leave = !sunny && (D.paint > 0.95 || p.ink < 0.03 || (matchLeft < 8 && D.paint > 0.45));
  // you're coming with the pound ready: a coffin is a trap now, so get out the far side
  const od = Math.hypot(O.x - D.x, O.z - D.z), threat = O.st === 'play' && !O.slam && slamReady(O) && od < 4.4 && D.immuneT <= 0.2;
  if (threat && !ai.fleeRolled) { ai.fleeRolled = true; ai.flee = Math.random() < AI.coffinFlee && (!sunny || (od < 2.4 && D.paint > 0.5)); }
  if (!threat) ai.fleeRolled = false;
  if (threat && ai.flee) { if (!ai.exitPlan || !ai.exitPlan.flee) ai.exitPlan = { yaw: Math.atan2(D.x - O.x, D.z - O.z), t: 0, flee: true }; leave = true; }
  else if (leave && AI.camp > 0 && !AI.coffinFlee && O.st === 'play' && slamReady(O) && od < 3.6 && ai.campT < AI.camp) { ai.campT += dt; leave = false; }
  if (!leave) return;""")
rep("""  const ep = ai.exitPlan; ep.t += dt;
  const err = wrapA(ep.yaw - D.yaw); D.steer = -clamp(err * 3, -1, 1);
  if (Math.abs(err) < 0.35 || ep.t > 1.2) { ai.exitPlan = null; ai.campT = 0; ai.thinkT = 0.15; jump(D); }""", """  const ep = ai.exitPlan; ep.t += dt;
  const err = wrapA(ep.yaw - D.yaw); D.steer = -clamp(err * 3, -1, 1);
  if (Math.abs(err) < (ep.flee ? 1.3 : 0.35) || ep.t > (ep.flee ? 0.3 : 1.2)) { ai.exitPlan = null; ai.campT = 0; ai.thinkT = ep.flee ? 0 : 0.15; ai.fleeRolled = false; jump(D); }""")
rep("    if (o && o.st === 'play' && Math.hypot(o.x - D.x, o.z - D.z) < 3.2) { const lead = o.flat > 0 ? 0 : o.spd * 0.35;", "    if (o && (o.st === 'play' || o.st === 'hide') && Math.hypot(o.x - D.x, o.z - D.z) < 3.2) { const lead = o.flat > 0 || o.st === 'hide' ? 0 : o.spd * 0.35;")
rep("    if (!o || o.st !== 'play') { ai.mode = 'paint'; ai.thinkT = 0; }", "    if (!o || (o.st !== 'play' && !(o.st === 'hide' && AI.coffinHunt > 0))) { ai.mode = 'paint'; ai.thinkT = 0; }")
open(f,'w').write(s)
print('patched')
