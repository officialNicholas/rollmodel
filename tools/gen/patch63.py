import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ---------- 1) stage queries look only at the pieces near the point (a coarse grid), not every box on the map ----------
rep("// ---------- stage queries ----------\nfunction floorAt(x, z) { if (Math.abs(x) > ARENA || Math.abs(z) > ARENA) return -Infinity; for (const h of HOLES) if (inR(x, z, h)) return -Infinity; return 0; }",
"""// ---------- stage queries ----------
// a coarse grid over the stage: each cell lists the boxes, ramps and holes within reach of it, so a point query checks a handful
const QG_C = 2, QG_O = 40, QG_N = 40, QG_M = 0.75, QG_EMPTY = [];
let qgB = [], qgR = [], qgH = [];
function buildQGrid() {
  const mk = () => { const g = new Array(QG_N * QG_N); for (let i = 0; i < g.length; i++) g[i] = QG_EMPTY; return g; };
  qgB = mk(); qgR = mk(); qgH = mk();
  const add = (g, r) => { const i0 = Math.max(0, Math.floor((r[0] - QG_M + QG_O) / QG_C)), i1 = Math.min(QG_N - 1, Math.floor((r[1] + QG_M + QG_O) / QG_C)), j0 = Math.max(0, Math.floor((r[2] - QG_M + QG_O) / QG_C)), j1 = Math.min(QG_N - 1, Math.floor((r[3] + QG_M + QG_O) / QG_C));
    for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) { const k = j * QG_N + i; if (g[k] === QG_EMPTY) g[k] = []; g[k].push(r); } };
  for (const b of BOXES) add(qgB, b); for (const r of RAMPS) add(qgR, r); for (const h of HOLES) add(qgH, h);
}
const qcell = (g, x, z) => { const i = Math.floor((x + QG_O) / QG_C), j = Math.floor((z + QG_O) / QG_C); return i < 0 || j < 0 || i >= QG_N || j >= QG_N ? QG_EMPTY : g[j * QG_N + i]; };
function floorAt(x, z) { if (Math.abs(x) > ARENA || Math.abs(z) > ARENA) return -Infinity; for (const h of qcell(qgH, x, z)) if (inR(x, z, h)) return -Infinity; return 0; }""")
rep("  for (const b of BOXES) if (b[5] <= maxY && b[5] > best && inR(x, z, b)) best = b[5];\n  for (const r of RAMPS) if (inR(x, z, r)) { const h = rampH(r, x, z); if (h <= maxY && h > best) best = h; }",
    "  for (const b of qcell(qgB, x, z)) if (b[5] <= maxY && b[5] > best && inR(x, z, b)) best = b[5];\n  for (const r of qcell(qgR, x, z)) if (inR(x, z, r)) { const h = rampH(r, x, z); if (h <= maxY && h > best) best = h; }")
rep("  for (const b of BOXES) if (y < b[5] - STEP && y + 0.8 > b[4] && inR(x, z, b, m)) return true;\n  for (const r of RAMPS) if (inR(x, z, r, m * 0.3)) {",
    "  for (const b of qcell(qgB, x, z)) if (y < b[5] - STEP && y + 0.8 > b[4] && inR(x, z, b, m)) return true;\n  for (const r of qcell(qgR, x, z)) if (inR(x, z, r, m * 0.3)) {")
rep("function solidThrough(x, z, y) { for (const b of BOXES) if (", "function solidThrough(x, z, y) { for (const b of qcell(qgB, x, z)) if (")
rep("    for (const b of BOXES) if (py > b[4] && py < b[5] && inR(px, pz, b)) return true;\n    if (!noDyn)", "    for (const b of qcell(qgB, px, pz)) if (py > b[4] && py < b[5] && inR(px, pz, b)) return true;\n    if (!noDyn)")
rep("    for (const b of BOXES) if (y > b[4] && y < b[5] && inR(x, z, b)) return false;\n    for (const r of RAMPS) if (inR(x, z, r) && y < rampH(r, x, z)) return false;",
    "    for (const b of qcell(qgB, x, z)) if (y > b[4] && y < b[5] && inR(x, z, b)) return false;\n    for (const r of qcell(qgR, x, z)) if (inR(x, z, r) && y < rampH(r, x, z)) return false;")
rep("    if (D.vy > 0) for (const b of BOXES) if (b[4] > 0 &&", "    if (D.vy > 0) for (const b of qcell(qgB, D.x, D.z)) if (b[4] > 0 &&")
rep("  HOLES.push(...L.holes.map(h => h.slice())); BOXES.push(...L.boxes.map(b => b.slice())); RAMPS.push(...L.ramps.map(r => r.slice()));",
    "  HOLES.push(...L.holes.map(h => h.slice())); BOXES.push(...L.boxes.map(b => b.slice())); RAMPS.push(...L.ramps.map(r => r.slice())); buildQGrid();")

# ---------- 2) never read layout mid-frame: the view size is cached when it changes ----------
rep("function resize() { const b = stage.getBoundingClientRect(); renderer.setSize(b.width, b.height, false);",
    "let viewW = 1, viewH = 1, pctRect = null;\nfunction resize() { const b = stage.getBoundingClientRect(); viewW = Math.max(1, b.width); viewH = Math.max(1, b.height); pctRect = null; renderer.setSize(b.width, b.height, false);")
rep("    const W = canvas.clientWidth, Hh = canvas.clientHeight, behind = tv1.z > 1; let x = behind ? -tv1.x : tv1.x, y = behind ? -tv1.y : tv1.y;",
    "    const W = viewW, Hh = viewH, behind = tv1.z > 1; let x = behind ? -tv1.x : tv1.x, y = behind ? -tv1.y : tv1.y;", 2)
rep("if (heroK > 0.003) { const vw = canvas.clientWidth || 1, vh = canvas.clientHeight || 1;", "if (heroK > 0.003) { const vw = viewW, vh = viewH;")
rep("  const F = threat.F, r = stage.getBoundingClientRect(), dx = F.x - P.x,", "  const F = threat.F, r = { width: viewW, height: viewH }, dx = F.x - P.x,")
rep("  tv1.copy(drop.position).project(camera); const r = stage.getBoundingClientRect(), pr = $('pct').getBoundingClientRect();\n  const sx = (tv1.x + 1) / 2 * r.width, sy = (1 - tv1.y) / 2 * r.height, tx = pr.left - r.left + pr.width / 2, ty = pr.top - r.top + pr.height * 0.55;",
    "  tv1.copy(drop.position).project(camera);\n  if (!pctRect) { const r0 = stage.getBoundingClientRect(), p0 = $('pct').getBoundingClientRect(); pctRect = { x: p0.left - r0.left + p0.width / 2, y: p0.top - r0.top + p0.height * 0.55 }; }\n  const sx = (tv1.x + 1) / 2 * viewW, sy = (1 - tv1.y) / 2 * viewH, tx = pctRect.x, ty = pctRect.y;")

# ---------- 3) the opponent lists are made once per mode, not every call ----------
rep("const foes = D => ACTIVE.filter(o => o !== D);",
    "let foesFor = null, foesC = new Map();\nconst foes = D => { if (foesFor !== ACTIVE) { foesFor = ACTIVE; foesC = new Map(); } let f = foesC.get(D); if (!f) { f = ACTIVE.filter(o => o !== D); foesC.set(D, f); } return f; };")

# ---------- 4) the CPU's route planning: table lookups for paint value, and only the best few targets kept (no big sort) ----------
rep("""  for (const n of NAV.nodes) {
    let g = 0, own = 0; for (const k of n.smp) { const v = painted[k]; if (v === me) own++; else { if (v === me + 3) own += 0.5; g += cellGain(v, me, stealW); } }
    nGain[n.id] = g; nMult[n.id] = 1 + 0.55 * own / (n.smp.length || 1) + 3 * n.edge;
  }""", """  for (let v = 0; v < 16; v++) { gainT[v] = cellGain(v, me, stealW); ownT[v] = v === me ? 1 : v === me + 3 ? 0.5 : 0; }
  for (const n of NAV.nodes) {
    let g = 0, own = 0; const sm = n.smp; for (let q = 0; q < sm.length; q++) { const v = painted[sm[q]]; own += ownT[v]; g += gainT[v]; }
    nGain[n.id] = g; nMult[n.id] = 1 + 0.55 * own / (sm.length || 1) + 3 * n.edge;
  }""")
rep("function aiThink(D) {\n", "const gainT = new Float64Array(16), ownT = new Float64Array(16), topS = new Float64Array(8), topI = new Int32Array(8), topP = new Float64Array(8);\nfunction aiThink(D) {\n")
rep("""  let rollBest = 0; const cand = [], planOK""", """  let rollBest = 0, nTop = 0; const K = Math.max(1, Math.min(8, AI.pick | 0)), planOK""")
rep("""    cand.push([(nAcc[n.id] + 0.7 * v + p) / (d + 2.5) * (1 - 0.4 * turn), n.id, p]);
  }
  if (!cand.length) { ai.path = null; return; }
  cand.sort((a, b) => b[0] - a[0]);
  let pick = cand[Math.min(cand.length - 1, (Math.random() * Math.min(AI.pick, cand.length)) | 0)];""",
"""    const sc = (nAcc[n.id] + 0.7 * v + p) / (d + 2.5) * (1 - 0.4 * turn);
    if (nTop < K || sc > topS[nTop - 1]) { let q = nTop < K ? nTop++ : nTop - 1; while (q > 0 && topS[q - 1] < sc) { topS[q] = topS[q - 1]; topI[q] = topI[q - 1]; topP[q] = topP[q - 1]; q--; } topS[q] = sc; topI[q] = n.id; topP[q] = p; }
  }
  if (!nTop) { ai.path = null; return; }
  const pq = Math.min(nTop - 1, (Math.random() * Math.min(AI.pick, nTop)) | 0);
  let pick = [topS[pq], topI[pq], topP[pq]];""")

# ---------- 5) two CPUs never plan in the same step: the second waits one step, so the work doesn't pile into one frame ----------
rep("  if (ai.thinkT <= 0 || !ai.path) { ai.thinkT =", "  if ((ai.thinkT <= 0 || !ai.path) && ai.path && thinkStep === stepNo && thinkBy !== D) { ai.thinkT = 0.0001; }\n  else if (ai.thinkT <= 0 || !ai.path) { thinkStep = stepNo; thinkBy = D; ai.thinkT =")
rep("function aiStep(D, dt) {", "let stepNo = 0, thinkStep = -1, thinkBy = null;\nfunction aiStep(D, dt) {")
rep("function step(dt) {\n  clock += dt;", "function step(dt) {\n  clock += dt; stepNo++;")
open(F, 'w').write(s)
print('ok')
