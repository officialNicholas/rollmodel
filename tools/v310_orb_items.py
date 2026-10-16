"""v310: the orb stays out of the walls, and a pick-up nobody takes is swapped for something else.

- The orb drifts from spot to spot. It used to check its way only at the height of where it was going, so heading for the top of a
  tall block (taller than it can float up) it slid in at floor height and stayed inside, out of reach. A pull toward a blob checked
  only the halfway point, so it could be dragged through a corner, and from inside a block every way out looked shut. Now:
  - a drift is only taken if the orb can follow it, step by step: each step on a surface it can rise onto, never into a wall, never
    over a hole;
  - a pull stops at a wall (the blob has to come round), and only a blob with an open way to it pulls at all;
  - it only comes up on open ground;
  - it rises onto a block a little before its edge instead of sliding through the corner;
  - and if it ever ends up inside anything, it pops back out moments later at the nearest open spot, with a sparkle.
- A pick-up nobody takes for 15 seconds (was 25) pops, and a moment later something else comes up instead: a different kind, where
  whoever has waited longest for one can get to it (or where the old one was). The kind nobody took is also less likely next time."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

ORB = r"""
// (v310) can the orb follow this line? Step by step from where it is: each step on a surface it can float up onto (2.2 at the most),
// never into a wall, never over a hole. (It floats at its surface, so checking only where it's going let it slide into a tall block.)
function orbPathOk(x0, z0, b0, x1, z1) {
  const d = Math.hypot(x1 - x0, z1 - z0), n = Math.max(1, Math.ceil(d / 0.3)); let b = b0;
  for (let i = 1; i <= n; i++) { const t = i / n, x = x0 + (x1 - x0) * t, z = z0 + (z1 - z0) * t, g = surfaceUnder(x, z, b + 2.2, true);
    if (g === -Infinity || blockedAt(x, z, g + 0.05)) return false; b = g; }
  return true;
}
// (v310) inside something after all (shoved, or a layout it didn't expect): out at the nearest open spot, with a sparkle at both ends
function orbUnstick() {
  let best = null, bd = 1e9; const E = zoneEdge() - 3;
  for (const q of COF_SPOTS) { if (!q || Math.max(Math.abs(q[0]), Math.abs(q[2])) > E || solidThrough(q[0], q[2], q[1] + 0.5) || blockedAt(q[0], q[2], q[1] + 0.05)) continue; const d = Math.hypot(q[0] - orb.x, q[2] - orb.z); if (d < bd) { bd = d; best = q; } }
  const fx = (x, y, z) => { for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; spawnPart(x, y, z, Math.cos(a) * 2.2, (Math.random() - 0.3) * 2.5, Math.sin(a) * 2.2, 0.45, orbPartMats[i % orbPartMats.length], 0.45); } };
  fx(orb.x, orb.y, orb.z);
  if (!best) { orbReset(); orb.spawnT = 1; return; }
  orb.x = orb.tx = best[0]; orb.z = orb.tz = best[2]; orb.base = best[1]; orb.y = best[1] + 1.15; orb.pull = 0; orb.inT = 0; fx(orb.x, orb.y, orb.z);
  if (state === 'play' && Math.hypot(P.x - orb.x, P.z - orb.z) < 18) AU.pop();
  if (!orb.stay) orbPickTarget();
}
"""

ITEMS = r"""
// (v310) nobody took it: a moment later something else comes up instead, a different kind, where whoever has waited longest for one
// can get to it (or where the old one was)
function itemTypeNot(t) { for (let k = 0; k < 12; k++) { const q = itemType(); if (q !== t) return q; } return ['roller', 'turret', 'trap', 'whirl', 'boom'].find(q => q !== t); }
function itemSwap(old) {
  const IS = itemSpawn; if (IS.pend || matchLeft <= 6) return;
  let R = null; for (const D of ACTIVE) if (D.st === 'play' && !hasItem(D) && (!R || (D.handT || 0) > (R.handT || 0))) R = D;
  const sp = (R && itemSpot(R)) || [old.x, old.y, old.z];
  IS.pend = { x: sp[0], y: sp[1], z: sp[2], t: 0, R, type: itemTypeNot(old.type) }; IS.last = old.type; // (and the kind nobody took is less likely next time)
  if (state === 'play' && Math.hypot(P.x - sp[0], P.z - sp[2]) < 18) AU.spot();
}
"""

def apply(s):
    # ---------------- the orb: only lines it can follow, no pulls through walls, open ground to come up on, and out if ever in
    s = rep(s, "// drift toward another reachable spot a few units away, with nothing tall in the way\nfunction orbPickTarget() {",
               ORB.lstrip('\n') + "// drift toward another reachable spot a few units away, with nothing tall in the way\nfunction orbPickTarget() {")
    s = rep(s, "    let ok = true; for (let t = 0.1; t <= 1.001 && ok; t += 0.1) { const x = orb.x + (c[0] - orb.x) * t, z = orb.z + (c[2] - orb.z) * t; if (blockedAt(x, z, Math.max(orb.base, c[1]) + 0.9)) ok = false; }",
               "    let ok = orbPathOk(orb.x, orb.z, orb.base, c[0], c[2]); // (v310: a line it can follow, not just open where it's going)")
    s = rep(s, "    if (h < pd && dy > -1.1 && dy < 1.3 && !blockedAt((D.x + orb.x) / 2, (D.z + orb.z) / 2, Math.max(D.y, orb.base) + 0.5)) { pd = h; puller = D; } }",
               "    if (h < pd && dy > -1.1 && dy < 1.3 && orbPathOk(orb.x, orb.z, orb.base, D.x, D.z)) { pd = h; puller = D; } } // (v310: an open way to it, not just the halfway point)")
    s = rep(s, "    orb.x += (tx - orb.x) * k; orb.z += (tz - orb.z) * k; orb.tx = orb.x; orb.tz = orb.z;",
               "    { const nx = orb.x + (tx - orb.x) * k, nz = orb.z + (tz - orb.z) * k; if (orbPathOk(orb.x, orb.z, orb.base, nx, nz)) { orb.x = nx; orb.z = nz; } } orb.tx = orb.x; orb.tz = orb.z; // (v310: a wall stops it)")
    s = rep(s, "  const g = surfaceUnder(orb.x, orb.z, orb.base + 2.2, true); if (g > -Infinity) orb.base += (g - orb.base) * Math.min(1, dt * 4);",
               "  let g = surfaceUnder(orb.x, orb.z, orb.base + 2.2, true);\n"
               "  if (d > 0.01 && !orb.pull) { const ga = surfaceUnder(orb.x + dx / d * 0.6, orb.z + dz / d * 0.6, orb.base + 2.2, true); if (ga > g) g = ga; } // (v310: up before the edge, not through it)\n"
               "  if (g > -Infinity) orb.base += (g - orb.base) * Math.min(1, dt * (g > orb.base ? 7 : 4));\n"
               "  if (solidThrough(orb.x, orb.z, orb.base + 0.5) && solidThrough(orb.x, orb.z, orb.y)) { orb.inT = (orb.inT || 0) + dt; if (orb.inT > 0.4) { orbUnstick(); if (!orb.on) return; } } else orb.inT = 0; // (v310)")
    s = rep(s, "if (q && Math.max(Math.abs(q[0]), Math.abs(q[2])) < ARENA - 4 && ACTIVE.every(D => D.st === 'ko' || Math.hypot(D.x - q[0], D.z - q[2]) > 7)) c = q; }",
               "if (q && Math.max(Math.abs(q[0]), Math.abs(q[2])) < ARENA - 4 && !solidThrough(q[0], q[2], q[1] + 0.5) && !blockedAt(q[0], q[2], q[1] + 0.05) && ACTIVE.every(D => D.st === 'ko' || Math.hypot(D.x - q[0], D.z - q[2]) > 7)) c = q; } // (v310: open ground only)")

    # ---------------- pick-ups: 15 seconds untaken and it's swapped for something else
    s = rep(s, "const ITEM_WARN = 1.2, ITEM_STALE = 25;", "const ITEM_WARN = 1.2, ITEM_STALE = 15; // (v310: was 25)")
    s = rep(s, "  for (let i = powers.length - 1; i >= 0; i--) { const pw = powers[i]; if (pw.g && (pw.age > ITEM_STALE || zoneLost(pw.x, pw.z))) itemPop(pw); }",
               "  for (let i = powers.length - 1; i >= 0; i--) { const pw = powers[i]; if (pw.g && (pw.age > ITEM_STALE || zoneLost(pw.x, pw.z))) { const stale = pw.age > ITEM_STALE; itemPop(pw); if (stale) { if (state === 'play' && Math.hypot(P.x - pw.x, P.z - pw.z) < 16) AU.pop(); itemSwap(pw); } } } // (v310: swapped)")
    s = rep(s, "// it pops (nobody took it, or the Showdown line closed over it)\nfunction itemPop(pw) {",
               ITEMS.lstrip('\n') + "// it pops (nobody took it, or the Showdown line closed over it)\nfunction itemPop(pw) {")
    return s
