import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ---------- a pound into a puddle washes everyone else's paint nearby down to half strength ----------
rep("function flushTrail() {\n  if (dirtyV < nV) {", "let teamAllDirty = false;\nfunction flushTrail() {\n  if (teamAllDirty) { teamAllDirty = false; dirtyV = 0; }\n  if (dirtyV < nV) {")
rep("function flushTrail() {", """// the water sloshes out over 1.5x the pound's circle: every other color in it drops to its watered-down, half-value version
const WASH_K = 1.5;
function washOut(D, x, y, z, R) {
  const r2 = R * R, i0 = clamp(Math.floor((x - R + ARENA) / CELL), 0, GN - 1), i1 = clamp(Math.floor((x + R + ARENA) / CELL), 0, GN - 1), j0 = clamp(Math.floor((z - R + ARENA) / CELL), 0, GN - 1), j1 = clamp(Math.floor((z + R + ARENA) / CELL), 0, GN - 1);
  let n = 0;
  for (let j = j0; j <= j1; j++) for (let i = i0; i <= i1; i++) for (const k of grid[j * GN + i]) {
    const v = painted[k]; if (v < 1 || v > 3 || v - 1 === D.team || Math.abs(sY[k] - y) > 1.2) continue;
    const dx = sX[k] - x, dz = sZ[k] - z; if (dx * dx + dz * dz > r2) continue;
    teamN[v]--; painted[k] = v + 3; teamN[v + 3]++; n++;
  }
  // and the paint you see goes thin to match
  for (let q = 0; q < nV; q++) { const t = vTeamA[q]; if (t >= 3 || t === D.team) continue; const dx = vPos[q * 3] - x, dz = vPos[q * 3 + 2] - z; if (dx * dx + dz * dz < r2 && Math.abs(vPos[q * 3 + 1] - y) < 1.2) { vTeamA[q] = t + 3; teamAllDirty = true; } }
  shockwave(x, y, z, R, 0xBFE8FF); shockwave(x, y, z, R * 0.7, 0xFFFFFF);
  for (let q = 0; q < 26; q++) { const a = q / 26 * 6.2832, sp = 3 + Math.random() * 4; spawnPart(x + Math.cos(a) * 0.8, y + 0.2, z + Math.sin(a) * 0.8, Math.cos(a) * sp, 1.5 + Math.random() * 2.5, Math.sin(a) * sp, 0.6, boilPartMat, 0.6 + Math.random() * 0.4); }
  return n;
}
function flushTrail() {""")
rep("  if (hitP.length) { hitP.forEach(splashPuddle); D.inkRush = true; if (hearable(D)) AU.sprinkle(D === P ? 1 : 0.6); }",
    "  if (hitP.length) { hitP.forEach(splashPuddle); D.inkRush = true; if (hearable(D)) AU.sprinkle(D === P ? 1 : 0.6); const n = washOut(D, p.x, p.y, p.z, SLAM_R * WASH_K); if (D === P && n > 10) popText('Watered down!'); }")
rep("  if (hitP.length) { hitP.forEach(splashPuddle); D.inkRush = true; if (hearable(D)) AU.sprinkle(D === P ? 1 : 0.6); if (D === P) { AU.splashWater(); setTimeout(() => AU.power(), 180); popText('Refilled!'); } }",
    "  if (hitP.length) { hitP.forEach(splashPuddle); D.inkRush = true; if (hearable(D)) AU.sprinkle(D === P ? 1 : 0.6); const wn = washOut(D, D.x, D.y, D.z, R * WASH_K); if (D === P) { AU.splashWater(); setTimeout(() => AU.power(), 180); popText(wn > 10 ? 'Watered down!' : 'Refilled!'); } }")
rep("Rain: everyone speeds up and puddles water your paint down.</span>", "Rain: everyone speeds up and puddles water your paint down. Pound a puddle to water down their paint all around it.</span>")
open(F, 'w').write(s)
print('ok')
