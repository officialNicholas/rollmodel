import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ---------- edge help grows with speed: reaches further, kicks in on a lighter steer, turns tighter, brakes harder ----------
rep("""  if (D === P && !P.ai && !D.air && D.st === 'play' && !D.charging && Math.abs(input) > 0.5 && D.spd > 1.5) {
    const reach = Math.min(3.4, 1 + D.spd * 0.35), ahead = voidAhead(D, D.yaw, reach);
    if (ahead > 0) { const side = voidAhead(D, D.yaw - Math.sign(input) * 0.75, reach); if (side < ahead) { const k = (ahead - side) * Math.min(1, (Math.abs(input) - 0.5) * 3); scaleBy *= 1 + 0.5 * k; D.spd = Math.max(cfg.speed * 0.55, D.spd - D.spd * 1.8 * k * dt); } }
  }""", """  if (D === P && !P.ai && !D.air && D.st === 'play' && !D.charging && D.spd > 1.5) {
    const sf = clamp((D.spd - cfg.speed * 0.8) / (cfg.speed * 1.2), 0, 1); // 0 at a normal roll, 1 at about twice that
    const reach = Math.min(3.4 + 2.6 * sf, 1 + D.spd * 0.35), ahead = voidAhead(D, D.yaw, reach), need = 0.5 - 0.3 * sf;
    if (ahead > 0 && Math.abs(input) > need) { const side = voidAhead(D, D.yaw - Math.sign(input) * 0.75, reach); if (side < ahead) { const k = (ahead - side) * Math.min(1, (Math.abs(input) - need) * 3) * (1 + sf); scaleBy *= 1 + 0.5 * k; D.spd = Math.max(cfg.speed * 0.55, D.spd - D.spd * (1.8 + 1.4 * sf) * Math.min(1, k) * dt); } }
    else if (ahead > 0.25 && sf > 0) D.spd -= Math.max(0, D.spd - cfg.speed) * 2.6 * sf * ahead * dt; // flying at a drop without steering: bleed off the extra speed so there's time to turn
  }""")

# ---------- the CPU can't see your pound meter: it plays as if your pound could be up at any moment ----------
rep("const oPoundIn = D => Math.max(0, D.ai.om.readyAt - runT); // its estimate of when your pound is back",
    "const oPoundIn = D => 0; // it can't tell whether your pound is ready, so it always assumes it might be")
rep("    if (stuck && !slamReady(D) && od < 7 && !(AI.model > 0 && oPoundIn(D) <= 0.6) && Math.random() < AI.ram * 0.6 && pn) return aiGo(D, pn, 'hunt');",
    "    if (stuck && !slamReady(D) && od < 7 && Math.random() < AI.ram * 0.6 && pn) return aiGo(D, pn, 'hunt');")
rep("(near && O.slamCD <= 0.5 ? Math.min(12, Math.hypot(x - o.x, z - o.z)) * 3 : 0)", "(near ? Math.min(12, Math.hypot(x - o.x, z - o.z)) * 3 : 0)")

# ---------- rolling into an occupied coffin boots whoever's in it, and you take the coffin ----------
rep("  if (D.flung && D.st === 'play') for (const p of pots) if (p.occ && p.occ !== D &&",
    """  if (D.rollT > 0 && D.st === 'play' && !D.air && D.giantT <= 0) for (const p of pots) if (p.occ && p.occ !== D && !(p.occ.spawnImm && p.occ.immuneT > 0) && potUp(p) && Math.abs(D.y - p.y) < 0.9 && Math.hypot(D.x - p.x, D.z - p.z) < 0.6 + PR) { rollIntoCoffin(D, p); break; }
  if (D.flung && D.st === 'play') for (const p of pots) if (p.occ && p.occ !== D &&""")
rep("function bumpFromCoffin(O, D) {", """function rollIntoCoffin(D, p) {
  const O = p.occ; bumpFromCoffin(O, D);
  if (p.ink <= 0.02) return; // nothing left in it: you just bounce off like a fling
  D.rollT = 0; D.dashT = 0; D.flung = false; D.spd = 0; enterPot(D, p); p.cool = 0;
  if (D === P) popText('Took it!'); else if (O === P) banner('Booted out!');
}
function bumpFromCoffin(O, D) {""")
open(F, 'w').write(s)
print('ok')
