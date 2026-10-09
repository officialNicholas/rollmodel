# V66: a CPU's think, lighter. The per-spot paint tally reads flat arrays instead of each spot's own list; the search for shade only looks at
# the spots that have it; the route scoring reads the graph's flat neighbour arrays. Same answers, in the same order
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:160])
    src = src.replace(old, new)
rep("off[NN] = e; NAV.nbOff = off; NAV.nbTo = to; NAV.nbW = w; }",
    "off[NN] = e; NAV.nbOff = off; NAV.nbTo = to; NAV.nbW = w; }\n"
    "  // the paint samples each spot sums, flat (spot i's are smIdx[smOff[i] .. smOff[i + 1])), and the spots in shade\n"
    "  { let m = 0; for (const n of nodes) m += n.smp.length; const so = new Int32Array(NN + 1), si = new Int32Array(m); let e = 0; for (const n of nodes) { so[n.id] = e; for (let q = 0; q < n.smp.length; q++) si[e++] = n.smp[q]; } so[NN] = e; NAV.smOff = so; NAV.smIdx = si; NAV.shadeN = nodes.filter(n => n.shade); }")
rep("  for (const n of NAV.nodes) {\n    let g = 0, own = 0; const sm = n.smp; for (let q = 0; q < sm.length; q++) { const v = painted[sm[q]]; own += ownT[v]; g += gainT[v]; }\n    nGain[n.id] = g; nMult[n.id] = 1 + 0.55 * own / (sm.length || 1) + 3 * n.edge;\n  }",
    "  { const nodes = NAV.nodes, so = NAV.smOff, si = NAV.smIdx;\n"
    "    for (let k = 0; k < nodes.length; k++) { const n = nodes[k], id = n.id, a = so[id], b = so[id + 1];\n"
    "      let g = 0, own = 0; for (let q = a; q < b; q++) { const v = painted[si[q]]; own += ownT[v]; g += gainT[v]; }\n"
    "      nGain[id] = g; nMult[id] = 1 + 0.55 * own / ((b - a) || 1) + 3 * n.edge; } }")
rep("  if (hardPhase) for (const n of NAV.nodes) if (dryAt(n.x, n.z, n.h, 0.25, -1) && !(Math.random() < AI.slip)) nMult[n.id] += 7;",
    "  if (hardPhase) { const nodes = NAV.nodes; for (let k = 0; k < nodes.length; k++) { const n = nodes[k]; if (dryAt(n.x, n.z, n.h, 0.25, -1) && !(Math.random() < AI.slip)) nMult[n.id] += 7; } }")
rep("    for (const n of NAV.nodes) if (n.shade && nDist[n.id] < sd) { sd = nDist[n.id]; shelter = n; }",
    "    { const sn = NAV.shadeN; for (let k = 0; k < sn.length; k++) { const n = sn[k]; if (nDist[n.id] < sd) { sd = nDist[n.id]; shelter = n; } } }")
rep("  for (const n of NAV.nodes) {\n    const d = nDist[n.id]; if (!(d < Infinity) || d < 2.2 || d > 26) continue;\n    let v = nGain[n.id]; const nb = n.nb; for (let e = 0; e < nb.length; e += 2) v += nGain[nb[e]] * 0.5;",
    "  const nodesA = NAV.nodes, nbO = NAV.nbOff, nbT = NAV.nbTo;\n"
    "  for (let k = 0; k < nodesA.length; k++) { const n = nodesA[k];\n    const d = nDist[n.id]; if (!(d < Infinity) || d < 2.2 || d > 26) continue;\n    let v = nGain[n.id]; for (let e = nbO[n.id], e1 = nbO[n.id + 1]; e < e1; e++) v += nGain[nbT[e]] * 0.5;")
open(P, 'w').write(src)
print('ok', len(src))
