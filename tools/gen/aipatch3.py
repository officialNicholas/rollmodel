f='/home/claude/paint-the-canvas.html'; s=open(f).read()
def rep(a,b,n=1):
    global s
    assert s.count(a)==n, (a[:90], s.count(a)); s=s.replace(a,b)

# ---- difficulty: how well it sees, hears and remembers you, and how much it plays against you ----
rep("plan: 0,    econ: 0, coffinHunt: 0,   coffinFlee: 0.1 },", "plan: 0,    econ: 0, coffinHunt: 0,   coffinFlee: 0.1,  sight: 14, fov: 150, hear: 2.5, poundHear: 9,  memory: 1.5, model: 0 },")
rep("plan: 0.3,  econ: 1, coffinHunt: 0.4, coffinFlee: 0.55 },", "plan: 0.3,  econ: 1, coffinHunt: 0.4, coffinFlee: 0.55, sight: 22, fov: 210, hear: 4,   poundHear: 15, memory: 3.5, model: 0.45 },")
rep("plan: 1,    econ: 1, coffinHunt: 1,   coffinFlee: 0.95 },", "plan: 1,    econ: 1, coffinHunt: 1,   coffinFlee: 0.95, sight: 32, fov: 270, hear: 6,   poundHear: 22, memory: 6,   model: 1 },")
rep("AI_LV.hardOld = Object.assign({}, AI_LV.hard, { plan: 0, econ: 0, coffinHunt: 0, coffinFlee: 0 });", "AI_LV.hardOld = Object.assign({}, AI_LV.hard, { plan: 0, econ: 0, coffinHunt: 0, coffinFlee: 0, model: 0 });")

# ---- perception: replaces the old all-seeing snapshot ----
old_see = s[s.index("function aiSee(D) {"):s.index("\n", s.index("function aiSee(D) {"))+1]
rep(old_see, """// ---------- what the CPU knows about you: only what it can actually see or hear ----------
// It sees in a cone in front of its face, out to a range, and only if nothing solid is in the way. It hears you rolling close by,
// hears (and sees) a pound from much farther, and knockouts are announced to everyone. Everything else is memory: where it last
// saw you and which way you were heading, fading after a few seconds. It never knows your blood level or exactly when your pound
// is ready; it estimates that from the last pound it noticed.
function losClear(ax, ay, az, bx, by, bz) {
  const n = Math.max(1, Math.ceil(Math.hypot(bx - ax, bz - az) / 0.45));
  for (let k = 1; k < n; k++) {
    const t = k / n, x = ax + (bx - ax) * t, z = az + (bz - az) * t, y = ay + (by - ay) * t;
    for (const b of BOXES) if (y > b[4] && y < b[5] && inR(x, z, b)) return false;
    for (const r of RAMPS) if (inR(x, z, r) && y < rampH(r, x, z)) return false;
  }
  return true;
}
function aiCanSee(D, O) {
  if (O.st === 'ko') return true; // a knockout is announced to everyone
  const dx = O.x - D.x, dz = O.z - D.z, d = Math.hypot(dx, dz);
  if (d < AI.hear && Math.abs(O.y - D.y) < 2) return true;     // close enough to hear you rolling
  if (d > (O.slam ? Math.max(AI.sight, AI.poundHear) : AI.sight)) return false;
  if (!O.slam && Math.abs(wrapA(Math.atan2(dx, dz) - D.yaw)) > AI.fov * Math.PI / 360) return false; // a pound leap is loud enough to turn its head
  return losClear(D.x, D.y + 0.55, D.z, O.x, O.y + 0.45, O.z);
}
function aiSee(D) {
  const O = other(D), ai = D.ai, vis = aiCanSee(D, O), was = ai.o && ai.o.st !== 'lost';
  ai.oVis = vis;
  if (vis) {
    ai.o = { x: O.x, z: O.z, y: O.y, yaw: O.yaw, spd: O.charging ? 0 : O.spd, st: O.st, slam: O.slam, air: O.air, flat: O.flatT, imm: O.immuneT, charging: O.charging, charge: O.charge, slowed: O.slowed, t: runT };
    ai.oPot = O.st === 'hide' ? O.pot : null;
    if (!was && O.st !== 'ko') ai.alert = { k: '!', t: 1.1 }; // spotted you
    return;
  }
  const o = ai.o; if (!o) { ai.o = { x: 0, z: 0, y: 0, yaw: 0, spd: 0, st: 'lost', slam: false, air: false, flat: 0, imm: 0, charging: false, charge: 0, slowed: false, t: -99 }; return; }
  const age = runT - o.t;
  if (o.st === 'ko' && O.st !== 'ko') o.st = 'lost'; // you came back somewhere it didn't see
  else if (o.st === 'play') {
    // keep guessing for a moment along the way you were going, then you're gone
    if (age < 1.2) { const k = Math.min(AI.react, 0.25); o.x += Math.sin(o.yaw) * o.spd * k; o.z += Math.cos(o.yaw) * o.spd * k; o.spd *= 0.85; }
    if (age > AI.memory) o.st = 'lost';
  } else if (o.st === 'hide') {
    // it remembers the coffin it saw you get into, until it can see that coffin is empty
    const p = ai.oPot;
    if (age > AI.memory * 2.5 || !p || !potUp(p) || (p.occ !== O && losClear(D.x, D.y + 0.55, D.z, p.x, p.y + 0.5, p.z) && Math.hypot(p.x - D.x, p.z - D.z) < AI.sight)) o.st = 'lost';
  }
  o.slam = false; o.charging = false; o.slowed = false;
  if (was && o.st === 'lost') ai.alert = { k: '?', t: 1.1 }; // lost track of you
}
// what it has noticed about how you play
function aiNotePound(D, O) {
  const ai = D.ai; if (!ai) return;
  const d = Math.hypot(O.x - D.x, O.z - D.z);
  if (!(d < AI.poundHear || aiCanSee(D, O))) return;
  const om = ai.om; om.readyAt = runT + SLAM_CD; om.pounds++;
  if (d < KO_R + 3) om.aimed++; // that one was meant for it
  ai.o = { x: O.x, z: O.z, y: O.y, yaw: O.yaw, spd: 0, st: O.st, slam: false, air: false, flat: 0, imm: O.immuneT, charging: false, charge: 0, slowed: false, t: runT };
}
const oPoundIn = D => Math.max(0, D.ai.om.readyAt - runT); // its estimate of when your pound is back
""")
rep("function aiReset(D) { D.ai = { poundAt: -1,", "function aiReset(D) { D.ai = { om: { readyAt: SLAM_FIRST, pounds: 0, aimed: 0 }, oVis: false, oPot: null, alert: null, poundAt: -1,")
# hearing pounds
rep("  const O = other(D);\n  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide')", "  const O = other(D);\n  if (O.cpu) aiNotePound(O, D);\n  if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide')")

# ---- thinking: hidden info replaced by what it knows, plus playing against you ----
rep("  const oThreat = o.st === 'play' && O.slamCD <= 0.6 && O.paint >= POUND_MIN;",
"""  const om = ai.om, oKnown = o.st === 'play' && runT - o.t < 1.5;
  const oThreat = oKnown && oPoundIn(D) <= 0.6;
  // how it reads you: someone who keeps aiming pounds at it gets a wide berth; someone who just paints gets hunted
  const hunterP = om.pounds ? om.aimed / Math.max(2, om.pounds) : 0.3;
  const lead = teamCov(O.team) - teamCov(D.team);""")
rep("    let g = 0, own = 0; for (const k of n.smp) { const v = painted[k]; if (v === me) own++; else g += v ? AI.steal : 1; }",
    "    let g = 0, own = 0; for (const k of n.smp) { const v = painted[k]; if (v === me) own++; else g += v ? stealW : 1; }")
rep("  for (const n of NAV.nodes) {\n    let g = 0, own = 0; for (const k of n.smp)",
    "  // when you're ahead it goes after your paint harder: taking yours back is worth double in a race\n  const stealW = AI.steal * (1 + AI.model * clamp((teamCov(1 - D.team) - teamCov(D.team)) / 6, 0, 0.8));\n  for (const n of NAV.nodes) {\n    let g = 0, own = 0; for (const k of n.smp)")
rep("if (oThreat && AI.evade > 0 && ai.mode !== 'hunt') NAV.near(o.x, o.z, o.y, KO_R, n => { nMult[n.id] += 2.5 * AI.evade; });",
    "if (oThreat && AI.evade > 0 && ai.mode !== 'hunt') NAV.near(o.x, o.z, o.y, KO_R, n => { nMult[n.id] += 2.5 * AI.evade * (1 + AI.model * hunterP * 1.5); });")
rep("  if (o.st === 'hide' && O.st === 'hide' && o.imm <= 0.3 && AI.coffinHunt > 0", "  if (o.st === 'hide' && o.imm <= 0.3 && AI.coffinHunt > 0")
rep("""  if (o.st === 'play' && o.imm <= 0.5) {
    const od = Math.hypot(o.x - D.x, o.z - D.z), behind = teamCov(D.team) < teamCov(O.team), aggro = behind ? 1.4 : matchLeft < 10 ? 0.6 : 1;
    const pn = NAV.at(o.x, o.z, o.y), pd = pn ? nDist[pn.id] : Infinity;
    const stuck = o.flat > 0 || O.slowed || o.charging;""", """  if (oKnown && o.imm <= 0.5) {
    const od = Math.hypot(o.x - D.x, o.z - D.z), behind = lead > 0;
    let aggro = behind ? 1.4 : matchLeft < 10 ? 0.6 : 1;
    if (AI.model > 0) {
      if (oPoundIn(D) > 1.5) aggro *= 1 + 2 * AI.model;          // it saw you pound: you can't hit back for a few seconds, so it comes now
      aggro *= 1 + AI.model * (0.5 - hunterP);                   // hunts a painter, steers clear of a hunter
      if (matchLeft < 15 && lead < -3) aggro *= 1 - 0.7 * AI.model; // ahead late: no need to take risks
      if (matchLeft < 15 && lead > 2) aggro *= 1 + AI.model;        // behind late: it needs a swing
    }
    // with a model of you, aim for where you're going to be, not where you are
    const leadT = AI.model > 0.5 && o.flat <= 0 ? Math.min(1, od / (speed + 0.1)) * AI.model : 0;
    const pn = NAV.at(o.x + Math.sin(o.yaw) * o.spd * leadT, o.z + Math.cos(o.yaw) * o.spd * leadT, o.y) || NAV.at(o.x, o.z, o.y), pd = pn ? nDist[pn.id] : Infinity;
    const stuck = o.flat > 0 || o.slowed || o.charging;""")

# ---- pounding at you needs a fresh sighting, and the coffin it saw you take ----
rep("  const reserve = AI.coffinHunt > 0 && O.st === 'hide' && O.immuneT <= 0.3 && !sunny && Math.hypot(O.x - D.x, O.z - D.z) < 14;",
    "  const reserve = AI.coffinHunt > 0 && o && o.st === 'hide' && o.imm <= 0.3 && !sunny && Math.hypot(o.x - D.x, o.z - D.z) < 14;")
rep("  if (o && (o.st === 'play' || (o.st === 'hide' && AI.coffinHunt > 0)) && (O.st === 'play' || O.st === 'hide') && o.imm <= 0.45 && Math.abs(o.y - D.y) < 1.2) {",
    "  if (o && ((o.st === 'play' && runT - o.t < 0.5) || (o.st === 'hide' && AI.coffinHunt > 0)) && o.imm <= 0.45 && Math.abs(o.y - D.y) < 1.2) {")
rep("    if (Math.hypot(px - D.x, pz - D.z) < AI.poundR && (!hiding || O.exposed) && Math.random() < Math.min(1, dt * AI.pound)) return useSlam(D);",
    "    if (Math.hypot(px - D.x, pz - D.z) < AI.poundR && (!hiding || (ai.oVis && O.exposed)) && Math.random() < Math.min(1, dt * AI.pound)) return useSlam(D);")
rep("&& Math.hypot(O.x - D.x, O.z - D.z) > 9 && localGain(D, 4.2) > AI.covPound", "&& !(o && o.st === 'play' && runT - o.t < 3 && Math.hypot(o.x - D.x, o.z - D.z) < 9) && localGain(D, 4.2) > AI.covPound")
# in the air: steer by what it sees
rep("""  const ai = D.ai, O = other(D);
  if (O.st === 'play' && O.immuneT <= 0.35) {
    const dx = O.x - D.x, dz = O.z - D.z, d = Math.hypot(dx, dz);""", """  const ai = D.ai, o = ai.o;
  if (o && o.st === 'play' && runT - o.t < 0.6 && o.imm <= 0.35) {
    const dx = o.x - D.x, dz = o.z - D.z, d = Math.hypot(dx, dz);""")
# dodging needs to notice the pound
rep("""  if (o.slam && O.slam) {
    const d = Math.hypot(O.x - D.x, O.z - D.z);
    if (d < KO_R + 1.3 && !ai.evadeRolled) { ai.evadeRolled = true; if (Math.random() < AI.evade) { ai.evadeT = 0.7; ai.evX = O.x; ai.evZ = O.z; return true; } }
  } else if (!O.slam) ai.evadeRolled = false;""", """  if (o.slam && O.slam && ai.oVis) {
    const d = Math.hypot(o.x - D.x, o.z - D.z);
    if (d < KO_R + 1.3 && !ai.evadeRolled) { ai.evadeRolled = true; if (Math.random() < AI.evade) { ai.evadeT = 0.7; ai.evX = o.x; ai.evZ = o.z; return true; } }
  } else if (!O.slam) ai.evadeRolled = false;""")
# in a coffin: only a threat it can see coming
rep("const od = Math.hypot(O.x - D.x, O.z - D.z), threat = O.st === 'play' && !O.slam && slamReady(O) && od < KO_R + 1.5 && D.immuneT <= 0.2;",
    "const o = ai.o, od = o ? Math.hypot(o.x - D.x, o.z - D.z) : 99, threat = !!o && o.st === 'play' && runT - o.t < 0.8 && !o.slam && oPoundIn(D) <= 0.4 && od < KO_R + 1.5 && D.immuneT <= 0.2;")
rep("if (!ai.exitPlan || !ai.exitPlan.flee) ai.exitPlan = { yaw: exitYaw(D, Math.atan2(D.x - O.x, D.z - O.z)), t: 0, flee: true };", "if (!ai.exitPlan || !ai.exitPlan.flee) ai.exitPlan = { yaw: exitYaw(D, Math.atan2(D.x - o.x, D.z - o.z)), t: 0, flee: true };")
rep("else if (leave && AI.camp > 0 && !AI.coffinFlee && O.st === 'play' && slamReady(O) && od < 3.6 && ai.campT < AI.camp)", "else if (leave && AI.camp > 0 && !AI.coffinFlee && o && o.st === 'play' && oPoundIn(D) <= 0.4 && od < 3.6 && ai.campT < AI.camp)")
# hunting closes in on what it sees
rep("    if (o && (o.st === 'play' || o.st === 'hide') && Math.hypot(o.x - D.x, o.z - D.z) < 3.2) {", "    if (o && ((o.st === 'play' && runT - o.t < 0.6) || o.st === 'hide') && Math.hypot(o.x - D.x, o.z - D.z) < 3.2) {")
open(f,'w').write(s)
print('patched')
