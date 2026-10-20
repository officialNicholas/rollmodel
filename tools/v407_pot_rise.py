"""v407: the basins come up out of the ground in the stage reveal (the user: "when we're showing the stage and the stage's name
appears, that you start seeing the basins rising out of the ground. One by one. so that they're not already placed").

While the camera sweeps over the canvas and the name card is up, every basin (paint can, tiki, tank, drum, barrel or coffin) starts
down in the ground and bursts up after the one before it, the same twist-and-overshoot a basin makes when it comes back in a match,
with a puff of dust and its rumble. They come up from the near side of the sweep to the far, yours last, as the camera comes down to
it; all of them are up a beat before the count. Only the look moves: where each basin is, and what it does, is as before. Its ring on
the floor shows once it's up, and the eyes of whoever is waiting in it only after that. No sweep (online, reduced motion, tests),
no rise: the basins are simply there."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""
// (v407) the basins rise one by one in the stage reveal: p.rvAt is when (in revealT), only the look moves (p.st stays 'up')
const RV_D = 0.75, RV_T0 = 0.35;
function potRiseStart() {
  const a = revealA0, R = ARENA * 1.5, cx = Math.sin(a) * R, cz = Math.cos(a) * R, mine = P.pot;
  const up = pots.filter(p => potUp(p) && p.g.visible && p !== mine).sort((p, q) => Math.hypot(p.x - cx, p.z - cz) - Math.hypot(q.x - cx, q.z - cz));
  if (mine && potUp(mine) && mine.g.visible) up.push(mine);
  const n = up.length, gap = n > 1 ? Math.min(0.24, (REVEAL_T - 0.25 - RV_D - RV_T0) / (n - 1)) : 0;
  up.forEach((p, i) => { p.rvAt = RV_T0 + i * gap; p.rvN = i; p.g.visible = false; });
}
function potRiseStep() {
  for (const p of pots) { if (p.rvAt === undefined) continue;
    if (!p.g.visible && revealT >= p.rvAt) { p.g.visible = true; shockwave(p.x, p.y, p.z, 1.3, 0xB89B82);
      for (let i = 0; i < 12; i++) { const a = Math.random() * 6.283, sp = 1.2 + Math.random() * 2; spawnPart(p.x + Math.cos(a) * 0.6, p.y + 0.1, p.z + Math.sin(a) * 0.6, Math.cos(a) * sp, 1.6 + Math.random() * 2, Math.sin(a) * sp, 0.5 + Math.random() * 0.35, dustMat, 0.7 + Math.random() * 0.6); }
      if (p.rvN % 2 === 0 || p === P.pot) { AU.at(p.x, p.z); AU.rise(); } }
    if (revealT >= p.rvAt + RV_D) delete p.rvAt; }
}
function potRiseEnd() { for (const p of pots) if (p.rvAt !== undefined) { delete p.rvAt; if (potUp(p)) p.g.visible = true; } }
const potRiseK = p => { const u = clamp((revealT - p.rvAt) / RV_D, 0, 1) - 1; return -(2.70158 * u * u * u + 1.70158 * u * u); };
"""

def apply(s):
    s = rep(s, "revealShow(); irisOpen(); AU.whoosh(); return; }", "potRiseStart(); revealShow(); irisOpen(); AU.whoosh(); return; }")
    s = rep(s, "function revealStep(rdt) { revealT += rdt;", JS + "function revealStep(rdt) { revealT += rdt; potRiseStep();")
    s = rep(s, "if (revealT >= REVEAL_T) { state = 'intro'; introT = 0;", "if (revealT >= REVEAL_T) { potRiseEnd(); state = 'intro'; introT = 0;")
    s = rep(s, "function abortReveal() { if (state === 'reveal') { state = 'intro'; introT = 0; }", "function abortReveal() { potRiseEnd(); if (state === 'reveal') { state = 'intro'; introT = 0; }")
    s = rep(s, "else if (p.st === 'rise') { const u = Math.min(1, p.t / RISE_T) - 1; sk = -(2.70158 * u * u * u + 1.70158 * u * u); }",
               "else if (p.st === 'rise') { const u = Math.min(1, p.t / RISE_T) - 1; sk = -(2.70158 * u * u * u + 1.70158 * u * u); }\n    if (p.rvAt !== undefined) sk = potRiseK(p); // (v407: coming up in the reveal)")
    s = rep(s, "p.ring.visible = p.ink > 0.02 && potUp(p);", "p.ring.visible = p.ink > 0.02 && potUp(p) && p.rvAt === undefined;")
    s = rep(s, "show = (D.st === 'hide' || !!cr) && !!p && (state !== 'intro' || D.peeked);", "show = (D.st === 'hide' || !!cr) && !!p && p.rvAt === undefined && (state !== 'intro' || D.peeked);")
    return s
