import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)
# the graph's links packed into flat arrays for the route search
rep("  NAV.nodes = nodes; NAV.at = at; NAV.near = near; NAV.cell = cellOf; NN = nodes.length;",
    "  NAV.nodes = nodes; NAV.at = at; NAV.near = near; NAV.cell = cellOf; NN = nodes.length;\n  { let m = 0; for (const n of nodes) m += n.nb.length >> 1; const off = new Int32Array(NN + 1), to = new Int32Array(m), w = new Float32Array(m); let e = 0; for (const n of nodes) { off[n.id] = e; for (let q = 0; q < n.nb.length; q += 2) { to[e] = n.nb[q]; w[e] = n.nb[q + 1]; e++; } } off[NN] = e; NAV.nbOff = off; NAV.nbTo = to; NAV.nbW = w; }")
rep("""function dijkstra(src) {
  nDist.fill(Infinity); nPrev.fill(-1); let hn = 0;""", """function dijkstra(src, maxD) {
  const lim = maxD || Infinity, off = NAV.nbOff, to = NAV.nbTo, wt = NAV.nbW;
  nDist.fill(Infinity, 0, NN); nPrev.fill(-1, 0, NN); let hn = 0;""")
rep("""    if (d > nDist[i]) continue;
    const nb = NAV.nodes[i].nb;
    for (let e = 0; e < nb.length; e += 2) { const j = nb[e], nd = d + nb[e + 1] * nMult[j]; if (nd < nDist[j]) { nDist[j] = nd; nPrev[j] = i; nAcc[j] = nAcc[i] + nGain[j]; if (hn < hpI.length) push(j, nd); } }""",
"""    if (d > nDist[i]) continue;
    if (d > lim) break; // far enough: nothing past here is ever a target
    for (let e = off[i], e1 = off[i + 1]; e < e1; e++) { const j = to[e], nd = d + wt[e] * nMult[j]; if (nd < nDist[j]) { nDist[j] = nd; nPrev[j] = i; nAcc[j] = nAcc[i] + nGain[j]; if (hn < hpI.length) push(j, nd); } }""")
# the CPU's plan only looks this far (everywhere when it needs shade from the sun)
rep("  if (oThreat && AI.evade > 0 && ai.mode !== 'hunt' && !(slamReady(D) && D.paint > 0.45)) NAV.near(o.x, o.z, o.y, KO_R, n => { nMult[n.id] += 2.5 * AI.evade * (1 + AI.model * hunterP * 1.5); });\n  dijkstra(src.id);",
    "  if (oThreat && AI.evade > 0 && ai.mode !== 'hunt' && !(slamReady(D) && D.paint > 0.45)) NAV.near(o.x, o.z, o.y, KO_R, n => { nMult[n.id] += 2.5 * AI.evade * (1 + AI.model * hunterP * 1.5); });\n  dijkstra(src.id, sunny || wxPhase === 'warn' || AI.sunLead > 0 && timeToSun() < 12 ? 0 : 64);")
open(F, 'w').write(s)
print('ok')
