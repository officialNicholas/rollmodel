# spawns that can't kill you: the basins you start in and come back in are ones with a long open run of floor in front, you face the
# longest run, and for a couple of seconds after you hop out the game steers you away from any drop ahead. Also: nothing worn shows
# while you're down in a basin (just the eyes); it all pops back on as you jump out. And the flower sits a touch further forward
import json, re
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:150])
    src = src.replace(old, new)

# ---- how far you can roll from a basin's rim in a direction before the floor ends, you hit something or a hazard ----
rep("function respawnBlob(D) {", r"""function openRun(x, z, y, a, r0, L) {
  const dx = Math.sin(a), dz = Math.cos(a); let d = 0;
  for (let r = r0; r <= L + 1e-6; r += 0.5) { const px = x + dx * r, pz = z + dz * r, g = surfaceUnder(px, pz, y + STEP);
    if (g === -Infinity || Math.abs(g - y) > 0.4 || blockedAt(px, pz, y) || rivals.some(q => Math.hypot(px - q.x, pz - q.z) < q.rad + 0.5)) break; d = r; }
  return d;
}
// the best way out of a basin: the longest open run (up to L), and that run
function potRun(p, L) { let yaw = 0, run = -1; for (let k = 0; k < 24; k++) { const a = k / 24 * 6.2832, d = openRun(p.x, p.z, p.y, a, 1.0, L || 9); if (d > run + 0.01) { run = d; yaw = a; } } return { yaw, run }; }
function respawnBlob(D) {""")
rep("""    const full = potUp(p) && p.ink > 0.3, dO = Math.hypot(px - O.x, pz - O.z), dS = Math.hypot(px - D.x, pz - D.z);
    const sc = (full ? 0 : -40) + Math.min(dO, 14) * 1.5 - dS * 0.25;""",
"""    const full = potUp(p) && p.ink > 0.3, dO = Math.hypot(px - O.x, pz - O.z), dS = Math.hypot(px - D.x, pz - D.z), run = potUp(p) ? potRun(p, 9).run : 6;
    const sc = (full ? 0 : -40) + Math.min(dO, 14) * 1.5 - dS * 0.25 + (run < 4 ? -60 : 0) + Math.min(run, 9) * 1.4; // (never one you'd roll straight off from)""")
rep("""  // face the most open direction so hopping out doesn't drop you straight into a hole
  let bestYaw = D.yaw, bestD = -1;
  for (let k = 0; k < 16; k++) {
    const a = k / 16 * 6.2832; let d = 0;
    for (let st = 1; st <= 14; st++) { const x = best.x + Math.sin(a) * st * 0.5, z = best.z + Math.cos(a) * st * 0.5, g = surfaceUnder(x, z, best.y + STEP); if (g === -Infinity || Math.abs(g - best.y) > 0.4 || blockedAt(x, z, best.y) || rivals.some(r => r.on && Math.hypot(x - r.x, z - r.z) < r.rad + 0.3)) break; d = st; }
    if (d > bestD) { bestD = d; bestYaw = a; }
  }
  D.yaw = bestYaw;""", """  // face the longest open run so hopping out doesn't drop you straight into a hole or off an edge
  const bestYaw = potRun(best, 9).yaw; D.yaw = bestYaw;""")
# ---- after hopping out of a spawn basin: a couple of seconds where the game steers you clear of drops ----
rep("  if (D.spawnImm) { D.spawnImm = false; D.immuneT = SPAWN_GRACE; } // a moment of safety after coming back\n  if (p.ink <= 0.02) sinkCoffin(p);\n}",
    "  if (D.spawnImm) { D.spawnImm = false; D.immuneT = SPAWN_GRACE; D.spawnGuard = 2.4; D.spd = cfg.speed * 0.6; } // a moment of safety after coming back\n  if (p.ink <= 0.02) sinkCoffin(p);\n}")
rep("    if (D.introOut) { D.introOut = false; continue; } // already out and on the floor",
    "    if (D.introOut) { D.introOut = false; D.spawnGuard = 2.4; continue; } // already out and on the floor (steered clear of drops for a moment)")
rep("function steerAndTurn(D, dt, scaleBy) {\n  let input = D === P ? (keyL || keyR ? (keyR ? 1 : 0) - (keyL ? 1 : 0) : steerIn) : D.steer;",
    """function steerAndTurn(D, dt, scaleBy) {
  let input = D === P ? (keyL || keyR ? (keyR ? 1 : 0) - (keyL ? 1 : 0) : steerIn) : D.steer;
  // just out of a spawn basin: if the floor runs out ahead, turn for the side that has more of it (whatever the stick says)
  if (D.spawnGuard > 0) { D.spawnGuard -= dt;
    if (D.st === 'play' && !D.air && D.spd > 0.5) { const reach = 2.6 + D.spd * 0.45, ahead = voidAhead(D, D.yaw, reach);
      if (ahead > 0) { const r = voidAhead(D, D.yaw - 0.8, reach), l = voidAhead(D, D.yaw + 0.8, reach); input = r <= l ? 1 : -1; scaleBy *= 1.25; D.spd = Math.max(cfg.speed * 0.5, D.spd - D.spd * 2.5 * ahead * dt); } } }""")
# the intro basins: only ones with a long run of floor out front (the leap faces it)
rep("  const cand = pots.filter(p => potUp(p) && !p.occ).sort(() => Math.random() - 0.5), got = new Map();",
    "  const all = pots.filter(p => potUp(p) && !p.occ).sort(() => Math.random() - 0.5), runs = new Map(all.map(p => [p, potRun(p, 9).run])), got = new Map();\n  const cand = all.filter(p => runs.get(p) >= 6).concat(all.filter(p => runs.get(p) < 6).sort((a, b) => runs.get(b) - runs.get(a)));")
rep("    const v = Math.cos(a - want) * 2 + Math.cos(a - toC) * 0.6; if (v > bs) { bs = v; best = a; }",
    "    const v = Math.cos(a - want) * 2 + Math.cos(a - toC) * 0.6 + Math.min(openRun(p.x, p.z, p.y, a, 1.0, 9), 9) * 0.55; if (v > bs) { bs = v; best = a; }")

# ---- in a basin nothing worn shows, just the eyes; it all pops back on as you jump out ----
rep("  const t = clock + (D.cpu ? 1.9 * D.team : 0), off = !!D.wearOff || (D.wearPop !== undefined && D.wearPop < 0);",
    """  if (D.st === 'hide' && D.pot) D.wearHid = true; else if (D.wearHid) { D.wearHid = false; if (!D.wearOff) D.wearPop = Math.min(D.wearPop === undefined ? 1 : D.wearPop, 0); }
  const t = clock + (D.cpu ? 1.9 * D.team : 0), off = !!D.wearOff || !!D.wearHid || (D.wearPop !== undefined && D.wearPop < 0);""")

# ---- the flower a touch further forward (still clear of the ear), and a little bigger now it's headgear ----
m = re.search(r'(<script type="application/json" id="wearPack">)(.*?)(</script>)', src, re.S)
pack = json.loads(m.group(2)); spot = {"p": [-0.2138, 0.3398, 0.1235], "n": [-0.4884, 0.8336, 0.2581]}
pack['patch']['flower'] = spot; pack['patch']['flowerLow'] = spot
src = src[:m.start(2)] + json.dumps(pack, separators=(',', ':')) + src[m.end(2):]
rep("W.flower.scale.multiplyScalar(mk * 0.2 * (1 + 0.04 * Math.sin(t * 2.3)));", "W.flower.scale.multiplyScalar(mk * 0.23 * (1 + 0.04 * Math.sin(t * 2.3)));")
open(P, 'w').write(src)
print('ok', len(src))
