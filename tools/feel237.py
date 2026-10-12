"""v237 animator and adapter: the feel pass. A crouch the moment a finger lands (the jump's anticipation, and instant feedback), a spring off
the ground, the tail whipped and the nose arcing through a jump, a braced, wider, deeper landing from a hard fall; a lurch forward on
braking; the swim's first pull stronger; a decisive tuck into the ball (the planted limbs let go at once)."""
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
def edit(path, pairs):
    s = open(path).read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:90]); s = s.replace(a, b)
    open(path, 'w').write(s)
edit(S + '/tools/assets/axolife.js', [
  # the crouch, the lurch and the first-pull emphasis need state
  ("ht: { x: 0, v: 0 }, bd: { x: 0, v: 0 }, vc: 0, bend: 0, dip: { x: 0, v: 0 }, dipR: { x: 0, v: 0 }, arch: { x: 0, v: 0 }, limbs: [] };",
   "ht: { x: 0, v: 0 }, bd: { x: 0, v: 0 }, vc: 0, bend: 0, dip: { x: 0, v: 0 }, dipR: { x: 0, v: 0 }, arch: { x: 0, v: 0 }, limbs: [], cr: { x: 0, v: 0 }, lu: { x: 0, v: 0 }, vcP: 0, acc: 0 };"),
  # the swim's first pull: stronger
  ("    if (want && !SL.on) { SL.on = true; if (SL.k < 0.05) SL.u = 0.86; }",
   "    if (want && !SL.on) { SL.on = true; if (SL.k < 0.05) { SL.u = 0.86; SL.first = 1; } }"),
  ("    out.root.z += (0.1 * lg - 0.03 * gat) * sl; /* (a smaller lunge of the body: the whole blob surges with the pull now, see strokeMul) */",
   "    SL.first = Math.max(0, (SL.first || 0) - dt / 1.1); const fst = 1 + 0.7 * SL.first; /* (the first pull out of the crawl: a bigger launch) */\n    out.root.z += (0.1 * lg * fst - 0.03 * gat) * sl; /* (a smaller lunge of the body: the whole blob surges with the pull now, see strokeMul) */"),
  ("    const hp = (0.1 * Math.sin(Math.PI * clamp01(u / 0.26)) - 0.05 * g + 0.035 * (1 - g) * Math.sin(th + 0.6)) * sl;",
   "    const hp = (0.1 * fst * Math.sin(Math.PI * clamp01(u / 0.26)) - 0.05 * g + 0.035 * (1 - g) * Math.sin(th + 0.6)) * sl;"),
  # the jump: a spring off the ground, the tail whipped down then up, the nose arcing over the flight
  ("  const fallK = air && (M.vy || 0) < 0 ? 1 - smooth(clamp01(((M.tl === undefined ? 1 : M.tl) - 0.05) / 0.4)) : 0;\n  rot(out, I.chest, -arch * 0.12 + dip * 0.1 - 4.5 * brI, 0, 0); rot(out, sp[2], -2 * brI, 0, 0); rot(out, I.head, 2 - arch * 0.1 - Math.min(0, dip) * 0.05 + (air ? -7 + 15 * fallK : 0), 0, 0);",
   "  const fallK = air && (M.vy || 0) < 0 ? 1 - smooth(clamp01(((M.tl === undefined ? 1 : M.tl) - 0.05) / 0.4)) : 0, riseK = air ? 1 - smooth(clamp01(L.airT / 0.3)) : 0; // (riseK: the push-off, fading over the first third of a second)\n  if (air) out.root.y += -0.03 * (1 - smooth(clamp01(L.airT / 0.06))) + 0.02 * Math.sin(Math.PI * clamp01((L.airT - 0.04) / 0.16)); /* (the spring off the ground: a last dip, then thrown up past its line) */\n  rot(out, I.chest, -arch * 0.12 + dip * 0.1 - 4.5 * brI - 4 * riseK, 0, 0); rot(out, sp[2], -2 * brI, 0, 0); rot(out, I.head, 2 - arch * 0.1 - Math.min(0, dip) * 0.05 + (air ? -9 - 5 * riseK + 20 * fallK : 0), 0, 0);"),
  ("  if (air) { rot(out, sp[1], -4 + 7 * fallK, 0, 0); rot(out, sp[2], -4 + 6 * fallK, 0, 0); }",
   "  if (air) { rot(out, sp[1], -5 - 3 * riseK + 9 * fallK, 0, 0); rot(out, sp[2], -4 - 2 * riseK + 7 * fallK, 0, 0); }"),
  ("  this.tailWave(2 * Math.PI * L.ph + Math.PI * 0.85, ((4 + 15 * clamp01(v / 6.5)) * act + 1.5), 0.75, air ? -3 : 0);",
   "  this.tailWave(2 * Math.PI * L.ph + Math.PI * 0.85, ((4 + 15 * clamp01(v / 6.5)) * act + 1.5), 0.75, air ? -11 * riseK + 4 * (1 - riseK) + 5 * fallK : 0); // (the tail whipped down with the push-off, lifting through the flight, trailing up on the way down)"),
  # the landing: a deeper dip from a hard fall, the limbs set wider
  ("    L.dip.v -= 34 * k; L.dipR.v += 40 * k * L.lead; L.landK = k;",
   "    L.dip.v -= 44 * k; L.dipR.v += 40 * k * L.lead; L.landK = k;"),
  ("      if (Z.t >= z.d) { l.st = 'stance'; l.p.copy(l.tgt); l.fresh = true; }",
   "      l.tgt.x += (l.arm ? 0.07 : 0.05) * Math.min(1, L.landK) * l.m; /* (a braced landing: the limbs set wider, the harder the fall) */\n      if (Z.t >= z.d) { l.st = 'stance'; l.p.copy(l.tgt); l.fresh = true; }"),
  # the crouch (a finger just landed) and the lurch (braking): on springs
  ("  // the bob of each pair's footfall, the push-off's arch, the landing's dip onto the lead hand (on springs: they overshoot and settle)",
   """  // a finger has landed and may be a jump: a quick crouch, the body dropped and gathered, the head up, ready to spring (or to ease back
  // out of it if the finger steers instead); and braking hard, the body lurches forward onto its hands, the head dipping, then settles
  { const cr = spr(L.cr, air ? 0 : clamp01(M.crouch || 0), 420, 28, dt); if (Math.abs(cr) > 0.002) { out.root.y -= 0.045 * cr; out.root.z -= 0.02 * cr; this.pitchTurn(out, I.neck, -0.1 * cr); this.pitchTurn(out, I.head, -0.1 * cr); this.pitchTurn(out, sp[2], 0.06 * cr); }
    const acc = (L.vc - L.vcP) / Math.max(dt, 1e-3); L.vcP = L.vc; L.acc += (acc - L.acc) * Math.min(1, dt * 20);
    const lu = spr(L.lu, air ? 0 : clamp01(-L.acc / 22) * on, 150, 14, dt); if (Math.abs(lu) > 0.002) { out.root.z += 0.045 * lu; out.root.y -= 0.012 * lu; this.pitchTurn(out, sp[3], 0.06 * lu); this.pitchTurn(out, I.neck, 0.14 * lu); this.pitchTurn(out, I.head, 0.1 * lu); } }
  // the bob of each pair's footfall, the push-off's arch, the landing's dip onto the lead hand (on springs: they overshoot and settle)"""),
  # the ball: the planted limbs let go at once
  ("    for (const k in out.contacts) out.contacts[k].w *= (1 - b) * (1 - b);",
   "    for (const k in out.contacts) out.contacts[k].w *= (1 - b) * (1 - b) * (1 - b); // (the planted limbs let go at once: no fight between the tuck and the ground)"),
])
edit(S + '/tools/assets/axoc.js', [
  ("    A.motion.speed = inAir || charging ? 0 : clamp((o.spd || 0) * 1.5, 0, 1.5); A.motion.dry = !!(D && D.dry && D.st === 'play');",
   "    A.motion.speed = inAir || charging ? 0 : clamp((o.spd || 0) * 1.5, 0, 1.5); A.motion.dry = !!(D && D.dry && D.st === 'play'); A.motion.crouch = D && D.preJ > 0 && D.st === 'play' && !D.air && !D.charging ? 1 : 0; // (a finger just landed: it may be a jump)"),
])
print('feel237 ok')
