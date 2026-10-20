"""v405: steadier frames in a busy match (the user: "FPS needs to be smooth and consistent").

Measured in a four-player Showdown driven by the game's own AI, drawing off: most of the slow frames were a CPU planning its route,
and the game made about 20 MB of short-lived garbage a second, the most of it in the planner. The planner is one very large function,
too large for the browser to optimize, so its two loops over every spot on the canvas (4,000 and more) ran in the slowest tier: slow,
and making garbage with every sum. They are small functions of their own now, which the engine does optimize; what they work out is
exactly as before. Smaller, per frame: the CPUs' look-ahead for hazards, the wearables' sizing and the particles' speed no longer make
garbage. And a knock-out's respawn no longer re-surveys every basin on the canvas (a hitch each time anyone came back): only the
basin it picks."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

GAINS = """  { const nodes = NAV.nodes, so = NAV.smOff, si = NAV.smIdx;
    for (let k = 0; k < nodes.length; k++) { const n = nodes[k], id = n.id, a = so[id], b = so[id + 1];
      let g = 0, own = 0; for (let q = a; q < b; q++) { const v = painted[si[q]]; own += ownT[v]; g += gainT[v]; }
      nGain[id] = g; nMult[id] = 1 + 0.55 * own / ((b - a) || 1) + 3 * n.edge; } }"""

SCORE = """  const nodesA = NAV.nodes, nbO = NAV.nbOff, nbT = NAV.nbTo;
  for (let k = 0; k < nodesA.length; k++) { const n = nodesA[k];
    const d = nDist[n.id]; if (!(d < Infinity) || d < 2.2 || d > 26) continue;
    let v = nGain[n.id]; for (let e = nbO[n.id], e1 = nbO[n.id + 1]; e < e1; e++) v += nGain[nbT[e]] * 0.5;
    const turn = Math.abs(wrapA(Math.atan2(n.x - D.x, n.z - D.z) - D.yaw)) / Math.PI, p = (n.i + n.j) % 2 ? 0 : pv(n);
    const rv = (nAcc[n.id] + 0.7 * v) / (d + 2.5) * (1 - 0.4 * turn); if (rv > rollBest) rollBest = rv;
    const sc = (nAcc[n.id] + 0.7 * v + p) / (d + 2.5) * (1 - 0.4 * turn);
    if (nTop < K || sc > topS[nTop - 1]) { let q = nTop < K ? nTop++ : nTop - 1; while (q > 0 && topS[q - 1] < sc) { topS[q] = topS[q - 1]; topI[q] = topI[q - 1]; topP[q] = topP[q - 1]; topT[q] = topT[q - 1]; q--; } topS[q] = sc; topI[q] = n.id; topP[q] = p; topT[q] = turn; }
  }"""

FUNCS = """
// (v405) the planner's two loops over every spot, as small functions of their own (see aiThink): the planner is too big for the engine
// to optimize, and in its slowest tier each of these sums made garbage. What they work out is as before.
function aiNodeGains() {
  const nodes = NAV.nodes, so = NAV.smOff, si = NAV.smIdx;
  for (let k = 0; k < nodes.length; k++) { const n = nodes[k], id = n.id, a = so[id], b = so[id + 1];
    let g = 0, own = 0; for (let q = a; q < b; q++) { const v = painted[si[q]]; own += ownT[v]; g += gainT[v]; }
    nGain[id] = g; nMult[id] = 1 + 0.55 * own / ((b - a) || 1) + 3 * n.edge; }
}
const AISC = { nTop: 0, rollBest: 0 };
function aiScoreNodes(D, K, pv) {
  let rollBest = 0, nTop = 0; const nodesA = NAV.nodes, nbO = NAV.nbOff, nbT = NAV.nbTo;
  for (let k = 0; k < nodesA.length; k++) { const n = nodesA[k];
    const d = nDist[n.id]; if (!(d < Infinity) || d < 2.2 || d > 26) continue;
    let v = nGain[n.id]; for (let e = nbO[n.id], e1 = nbO[n.id + 1]; e < e1; e++) v += nGain[nbT[e]] * 0.5;
    const turn = Math.abs(wrapA(Math.atan2(n.x - D.x, n.z - D.z) - D.yaw)) / Math.PI, p = (n.i + n.j) % 2 ? 0 : pv(n);
    const rv = (nAcc[n.id] + 0.7 * v) / (d + 2.5) * (1 - 0.4 * turn); if (rv > rollBest) rollBest = rv;
    const sc = (nAcc[n.id] + 0.7 * v + p) / (d + 2.5) * (1 - 0.4 * turn);
    if (nTop < K || sc > topS[nTop - 1]) { let q = nTop < K ? nTop++ : nTop - 1; while (q > 0 && topS[q - 1] < sc) { topS[q] = topS[q - 1]; topI[q] = topI[q - 1]; topP[q] = topP[q - 1]; topT[q] = topT[q - 1]; q--; } topS[q] = sc; topI[q] = n.id; topP[q] = p; topT[q] = turn; }
  }
  AISC.nTop = nTop; AISC.rollBest = rollBest;
}
"""

def apply(s):
    s = rep(s, GAINS, "  aiNodeGains(); // (v405)")
    s = rep(s, SCORE, "  aiScoreNodes(D, K, pv); nTop = AISC.nTop; rollBest = AISC.rollBest; // (v405)")
    s = rep(s, "function aiThink(D) {", FUNCS.lstrip('\n') + "function aiThink(D) {")
    s = rep(s, "    for (const n of NAV.nodes) { if (!pudNear[n.id]) continue; const d = nDist[n.id];",
               "    for (let k = 0, NA = NAV.nodes; k < NA.length; k++) { const n = NA[k]; if (!pudNear[n.id]) continue; const d = nDist[n.id];")
    # the look-ahead for hazards (several times a frame for each CPU): no iterator, no hypot
    s = rep(s, "    if (avoidPots) for (const p of pots) if (potUp(p) && !p.occ && p.ink > 0.02 && p.cool <= 0 && Math.hypot(x - p.x, z - p.z) < 0.85 && Math.abs(p.y - s) < 0.5) { score += 4 * w * 0.5; break; }\n"
               "    if (av) for (const T of av) if (Math.abs(T.y - s) < 0.6 && Math.hypot(x - T.x, z - T.z) < TRAP_R + 0.45) { score += 5 * w * 0.5; break; }",
               "    if (avoidPots) for (let i = 0; i < pots.length; i++) { const p = pots[i], ex = x - p.x, ez = z - p.z; if (ex * ex + ez * ez < 0.7225 && potUp(p) && !p.occ && p.ink > 0.02 && p.cool <= 0 && Math.abs(p.y - s) < 0.5) { score += 4 * w * 0.5; break; } }\n"
               "    if (av) for (let i = 0; i < av.length; i++) { const T = av[i], ex = x - T.x, ez = z - T.z; if (Math.abs(T.y - s) < 0.6 && ex * ex + ez * ez < (TRAP_R + 0.45) * (TRAP_R + 0.45)) { score += 5 * w * 0.5; break; } }")
    # the wearables' sizing, every frame for every character: from a list made once, not the map's iterator
    s = rep(s, "  for (const [o, bs] of W.bs) if (o.visible) o.scale.set(bs.x * pk, bs.y * pk, bs.z * pk);",
               "  { const A = W.bsA || (W.bsA = Array.from(W.bs)); for (let i = 0; i < A.length; i++) { const o = A[i][0]; if (o.visible) { const bs = A[i][1]; o.scale.set(bs.x * pk, bs.y * pk, bs.z * pk); } } } // (v405)")
    s = rep(s, "sp = p.rest ? 0 : Math.hypot(p.vx, p.vy, p.vz);", "sp = p.rest ? 0 : Math.sqrt(p.vx * p.vx + p.vy * p.vy + p.vz * p.vz);", 2)
    # a knock-out's respawn: the basins are judged by the survey of their ways out made for this canvas (kept up to date by the last
    # fresh look at each), and only the one chosen is looked at afresh (the puddles may have moved). Every basin's 24 runs, every time
    # anyone came back, was a hitch
    s = rep(s, "R = potUp(p) ? startRoom(p, true) : null, run = R ? R.run : 6;", "R = potUp(p) ? startRoom(p) : null, run = R ? R.run : 6; /* (v405: the survey on file) */")
    return s
