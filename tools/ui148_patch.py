#!/usr/bin/env python3
"""v220: feel and the lesson's pacing.
 - A long slingshot, and a roll out of a basin: the old jelly ball takes the axolotl's place for the quick part (a pop of paint each way);
   the axolotl itself never curls into a ball for them.
 - A jump: the legs tuck in once it's off the ground (tools/assets/axolife.js), reaching down again just before it lands.
 - The lesson: its first tip (steer and jump) waits a second and a half after you're out of the basin, so the slow motion isn't taken
   for your speed; a lesson done gets its praise on its own (after any banner), the next tip after it; the rival is brought round into
   view, near you, for the pound and the dodge (when it's far off and out of sight), and comes right up into the pound's reach before its
   tip; the roller pops up after a breath, its tip a moment later; once you're a roller, a quick tip to swipe up and roll over the rival,
   at full speed. The slow motion shows as a proper vignette, deeper at the moment to act.
 - In a real match, the first roller gets a one-time tip: swipe up to roll over rivals."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui147_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'reachL' in s, 'the tucking runtime is not in the build'
# ---- the ball: the old jelly in the axolotl's place for a long slingshot and a roll out of a basin
rep("  const tur = !!D.turret && D.st === 'play', on = L.roll < 0.5 && !tur && !(D === P && lookIntro && lookIntro.t < IN_LAND), was = I.root.visible;",
    "  // a long slingshot, and a roll out of a basin: the old jelly ball takes the axolotl's place for the quick part of it, a little pop of\n"
    "  // paint each way (the axolotl itself never curls up into one for them)\n"
    "  const flA0 = D.flung && V.vAir && D.st === 'play' && !D.slam && !D.missile && !D.rocket;\n"
    "  if (flA0 && !V.flOn) { V.flOn = true; V.flV0 = Math.max(1, D.vy || 1); } else if (!flA0) V.flOn = false;\n"
    "  const flK0 = flA0 ? smoothstep(0.3, 0.78, D.flingC || 0) * smoothstep(-0.15, 0.55, (D.vy || 0) / V.flV0) : 0;\n"
    "  const ballOn = I.kind === 'axo' && D.st === 'play' && (state === 'play' || state === 'dead') && (flK0 > (V.balled ? 0.12 : 0.3) || D.rollOutT > (V.balled ? 0.1 : 0.16));\n"
    "  if (ballOn !== !!V.balled) { V.balled = ballOn; if (D.st === 'play' && (I.root.visible || V.oldBlob.visible)) ballPoof(D, ballOn); }\n"
    "  if (V.balled) { U.gRise.value *= 0.3; U.gDrop.value *= 0.35; } // (a ball: drawn out along its flight only a little, never into a column)\n"
    "  const tur = !!D.turret && D.st === 'play', on = L.roll < 0.5 && !tur && !V.balled && !(D === P && lookIntro && lookIntro.t < IN_LAND), was = I.root.visible;")
rep("  o.blob = flK; o.blobSt = 0.3 * flK * clamp(flV, 0, 1);", "  o.blob = I.kind === 'axo' ? 0 : flK; o.blobSt = I.kind === 'axo' ? 0 : 0.3 * flK * clamp(flV, 0, 1);")
rep("function rollPoof(D, on) {",
    "// the old jelly ball taking the axolotl's place, or giving it back: a little pop of paint, thrown along with it\n"
    "function ballPoof(D, on) {\n"
    "  D.wob = Math.max(D.wob || 0, 0.7); const sp = (D.spd || 0) * 0.5, fx = Math.sin(D.yaw) * sp, fz = Math.cos(D.yaw) * sp;\n"
    "  for (let i = 0; i < 10; i++) { const a = i / 10 * 6.283 + Math.random() * 0.3, s = 1.4 + Math.random() * 1.2; spawnPart(D.x, D.y + 0.35, D.z, Math.cos(a) * s + fx, 0.8 + Math.random() * 1.6, Math.sin(a) * s + fz, 0.3 + Math.random() * 0.15, i % 3 ? tmat(D) : puHaloMat, 0.45 + Math.random() * 0.3); }\n"
    "  if (on && hearable(D)) AU.pop();\n}\n"
    "function rollPoof(D, on) {")
# ---- the lesson: the first tip a second and a half after you're out of the basin
rep("  if (tut.step < 0) { if (P.st === 'play' && !P.air && runT > 0.6) tutNext(); return; }",
    "  if (tut.step < 0) { if (tut.outAt === undefined) { if (P.st === 'play' && !P.air && runT > 0.3) tut.outAt = runT; } else if (runT - tut.outAt >= 1.5) tutNext(); return; } // (a moment at full speed first, so the slow motion isn't taken for your speed)")
# a lesson done: its praise on its own (after any banner up), then the next lesson
rep("  if (s.tick(dt)) { if (tut.step < TUT_REST && !s.id.startsWith('free')) tutReward(s.id, (s.id === 'dodge' || s.id === 'rocketdodge') && tut.hit && !tut.rolled); tutNext(); }",
    "  if (tut.gap > 0) { tut.gap -= dt; if (tut.gap <= 0) { tut.gap = 0; tutNext(); } return; } // (a lesson done: its praise has the screen to itself, then the next tip)\n"
    "  if (s.tick(dt)) { if (tut.step < TUT_REST && !s.id.startsWith('free')) { tutReward(s.id, (s.id === 'dodge' || s.id === 'rocketdodge') && tut.hit && !tut.rolled); if (s.exit) s.exit(); tut.exited = true; tutHide(); tut.slowK = 1; tut.gap = 1.2 + Math.max(0, bannerUntil - performance.now()) / 1000; } else tutNext(); }")
rep("function tutNext() { if (!tut) return; const cur = TUT_STEPS[tut.step]; if (cur && cur.exit) cur.exit();",
    "function tutNext() { if (!tut) return; const cur = TUT_STEPS[tut.step]; if (cur && cur.exit && !tut.exited) cur.exit(); tut.exited = false;")
rep("if (tut.st > TUT_STEPS[tut.step].max) tutNext(); }", "if (tut.st > TUT_STEPS[tut.step].max && !(tut.gap > 0)) tutNext(); }")
rep("restartCls(tutPraiseEl, 'on'); clearTimeout(tutPraiseEl._t); tutPraiseEl._t = setTimeout(() => tutPraiseEl.classList.remove('on'), 1150);",
    "clearTimeout(tutPraiseEl._t); clearTimeout(tutPraiseEl._t0); { const bw = Math.max(0, bannerUntil - performance.now()), go = () => { restartCls(tutPraiseEl, 'on'); tutPraiseEl._t = setTimeout(() => tutPraiseEl.classList.remove('on'), 1150); }; if (bw > 30) { tutPraiseEl.classList.remove('on'); tutPraiseEl._t0 = setTimeout(go, bw); } else go(); } // (after a banner, never under it)")
# the pound: the rival brought round into view when it's far off, and right up into the pound's reach before its tip
rep("if ((H.st === 'play' && hd < 4.5 && Math.abs(H.y - P.y) < 1.2) || tut.st > 12) tut.poundIn = true;",
    "if (!tut.poundIn && P.st === 'play') tutRivalIn(5.5); if ((H.st === 'play' && hd < SLAM_R + PR && Math.abs(H.y - P.y) < 1.2) || tut.st > 24) tut.poundIn = true;")
# the dodge: the rival brought round where you can see its pound coming
rep("tick() { if (H.st === 'play' && !H.slam && H.slamCD > 1.2) H.slamCD = 1.2;", "tick() { if (!H.slam && P.st === 'play') tutRivalIn(6.5); if (H.st === 'play' && !H.slam && H.slamCD > 1.2) H.slamCD = 1.2;")
# the roller: a breath first, then it pops up, then its tip
rep("{ id: 'item', max: 50, enter() { tut.items = true; tutSpawnRoller(); tut.slowK = 1; tut.sub = ''; },\n    tick() { const sub = P.held === 'roller' ? 'use' : 'grab';",
    "{ id: 'item', max: 50, enter() { tutHide(); tut.items = true; tut.slowK = 1; tut.sub = ''; tut.wait = 1.4; tut.tipIn = 0; itemSpawn.t = Math.max(itemSpawn.t, 14); }, /* (a breath, then the roller pops up; a moment to see it, then its tip) */\n"
    "    tick(dt) { if (tut.wait > 0) { tut.wait -= dt; if (tut.wait <= 0) { tutSpawnRoller(); tut.tipIn = 0.8; } return false; } if (tut.tipIn > 0 && !P.held) { tut.tipIn -= dt; return false; } const sub = P.held === 'roller' ? 'use' : 'grab';")
# once you're a roller: a quick tip to roll over the rival, at full speed
rep("{ id: 'free2', max: 99, enter() { tutHide(); tut.slowK = 1; tut.wait = 6; }, tick(dt) { tut.wait -= dt; return tut.wait <= 0; } },",
    "{ id: 'free2', max: 99, enter() { tutHide(); tut.slowK = 1; tut.wait = 6; tut.rTip = !!(P.power && P.power.type === 'roller'); tut.rTipT = 3.4; if (tut.rTip) tutShow(say('*SWIPE UP* to roll over the rival!', 'Press *SHIFT* to roll over the rival!'), null, 'rroll', true, true); }, /* (now a roller: a quick word on rolling over the rival, at full speed) */\n"
    "    tick(dt) { if (tut.rTip) { tut.rTipT -= dt; if (tut.rTipT <= 0 || P.rollT > 0 || !(P.power && P.power.type === 'roller')) { tut.rTip = false; tutHide(); } } tut.wait -= dt; return tut.wait <= 0; } },")
rep("const TUT_GEST = { move: 'steertap', sling: 'pull', dodgenow: 'swipe', rdodgenow: 'swipe',", "const TUT_GEST = { move: 'steertap', sling: 'pull', dodgenow: 'swipe', rdodgenow: 'swipe', rroll: 'swipe',")
rep("for (const k of ['steer', 'jump', 'hold', 'burst', 'roll', 'pound', 'missile', 'item', 'orb', 'rocket', 'airdash']) store.seen[k] = 1;",
    "for (const k of ['steer', 'jump', 'hold', 'burst', 'roll', 'pound', 'missile', 'item', 'orb', 'rocket', 'airdash', 'rroll']) store.seen[k] = 1;")
# a real match: the first roller's one-time tip, once its banner's gone
rep("banner('Roller!', 'Wide stripes. Paint refilled'); }",
    "banner('Roller!', 'Wide stripes. Paint refilled'); setTimeout(() => { if (state === 'play' && P.power && P.power.type === 'roller') hint('rroll', say('Swipe up to roll over rivals', 'Shift to roll over rivals'), 2.8); }, 2300); }")
# the rival brought round
rep("// the lesson's badges: one per lesson,",
    "// the lesson's rival, far off and out of sight: brought round to open ground a few steps ahead of you, in view (with a little pop of\n"
    "// paint), so what it does next happens where you can see it coming\n"
    "let tutRivT = -9;\n"
    "function tutRivalIn(dist) {\n"
    "  const D = H; if (!tut || !D || D.st !== 'play' || D.air || D.slam || D.rocket || D.turret || P.st !== 'play' || P.air || runT - tutRivT < 2.5) return false;\n"
    "  const far = Math.hypot(D.x - P.x, D.z - P.z); tv1.set(D.x, D.y + 0.3, D.z).project(camera); const seen = tv1.z < 1 && Math.abs(tv1.x) < 1 && Math.abs(tv1.y) < 1;\n"
    "  if (far < (seen ? 10 : 7.5)) return false;\n"
    "  for (const d of [dist, dist + 1, dist - 1, dist + 2, dist - 2]) for (const da of [0.45, -0.45, 0.25, -0.25, 0.7, -0.7, 0, 0.95, -0.95, 1.2, -1.2]) {\n"
    "    const a = P.yaw + da, x = P.x + Math.sin(a) * d, z = P.z + Math.cos(a) * d; if (Math.abs(x) > ARENA - 1.5 || Math.abs(z) > ARENA - 1.5) continue;\n"
    "    const y = surfaceUnder(x, z, P.y + 0.3); if (!(Math.abs(y - P.y) < 0.3) || blockedAt(x, z, y) || !lineClear(P, x, z, P.y)) continue;\n"
    "    if (pots.some(p => Math.hypot(p.x - x, p.z - z) < 2) || powers.some(o => Math.hypot(o.x - x, o.z - z) < 1.5) || rivals.some(r => Math.hypot(r.x - x, r.z - z) < r.rad + 1.2)) continue;\n"
    "    tv1.set(x, y + 0.3, z).project(camera); if (!(tv1.z < 1 && Math.abs(tv1.x) < 0.8 && tv1.y > -0.7 && tv1.y < 0.8)) continue;\n"
    "    D.x = x; D.z = z; D.y = y; D.vy = 0; D.air = false; D.spd = 0; D.kx = D.kz = 0; D.knockT = 0; D.yaw = Math.atan2(P.x - x, P.z - z); D.stroke++; if (D.charging) cancelCharge(D);\n"
    "    if (D.ai) { D.ai.plan = null; D.ai.path = null; } const V = vOf(D); if (V) { V.yawD = D.yaw; if (V.slime && V.slime.ax) V.slime.ax.fresh = true; }\n"
    "    ballPoof(D, true); tutRivT = runT; return true; }\n"
    "  return false;\n}\n"
    "// the lesson's badges: one per lesson,")
# the slow motion: a proper vignette, deeper at the moment to act
rep(".tutslow{position:absolute;inset:0;z-index:7;pointer-events:none;opacity:0;transition:opacity .4s;background:radial-gradient(ellipse at center,transparent 58%,rgba(23,19,32,.42) 100%);box-shadow:inset 0 0 0 3px var(--gold)}",
    ".tutslow{position:absolute;inset:0;z-index:7;pointer-events:none;opacity:0;transition:opacity .3s;background:radial-gradient(ellipse at center,transparent 34%,rgba(23,19,32,.3) 64%,rgba(23,19,32,.72) 100%);box-shadow:inset 0 0 0 3px var(--gold)}\n"
    ".tutslow::after{content:'';position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 24%,rgba(23,19,32,.3) 56%,rgba(23,19,32,.5) 100%);opacity:0;transition:opacity .2s}\n"
    ".tutslow.deep::after{opacity:1}")
rep("tutSlowEl.classList.toggle('on', on); AU.slow(on); } }", "tutSlowEl.classList.toggle('on', on); AU.slow(on); } const dp = on && tut.slowK < 0.2; if (tutSlowEl.classList.contains('deep') !== dp) tutSlowEl.classList.toggle('deep', dp); }")
rep('<p class="ver">Version 219</p>', '<p class="ver">Version 220</p>')
open(DST, 'w').write(s)
print('ui148 ok', n0, '->', len(s))
