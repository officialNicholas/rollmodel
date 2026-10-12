#!/usr/bin/env python3
"""v231: the swim's pull carries the body forward and it settles back (the animator); the paint stream flows from under the belly (laid a
little ahead of the blob's centre, tapering in over a shorter run, so it reaches full width at the hips rather than behind the tail's
root); the lobby frames the axolotl by its width as well as its height (on a wider screen it filled the view); the sound has headroom
(no bass and treble boost into the master's soft clipper, a quieter feed into it, a limiter that catches earlier); and the onboarding's
"take a look around" is the locker's, not the shop's: the shop points at Back again, the locker lets you play once your fangs and
flower are on, and closing it goes on with the lesson."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui163_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'swTan' in s and 'kickGills(0, -0.28' in s
# ---- the lobby: by width too (the crawl's head and gills spread wide: at most a bit under half the screen's width)
rep("  const tv = Math.tan(heroFov() * Math.PI / 360), dist = clamp(tall * Hh / (2 * tv * px), 1.65, 12), ly = 0.36;",
    "  const tv = Math.tan(heroFov() * Math.PI / 360), asp = W / Math.max(1, Hh), wide = VP.slime && VP.slime.kind === 'axo' ? 0.9 : 0.8, dist = clamp(Math.max(tall * Hh / (2 * tv * px), wide / (2 * tv * asp * 0.46)), 1.65, 12), ly = 0.36; /* (by width too: on a wider screen the height alone made it fill the view) */")
# ---- the paint stream: from under the belly
rep("const TAPER_N = 9, TAPER_NMAX = 22, TAPER_TIP = 0.3;", "const TAPER_N = 5, TAPER_NMAX = 22, TAPER_TIP = 0.3, TRAIL_FWD = 0.1; /* (the stream laid a touch ahead of the blob's centre, under its chin, and full width by its hips) */")
rep("      if (D.flatT <= 0 && !D.dry) { D.dist += D.spd * dt; while (D.dist >= SPACING) { D.dist -= SPACING; addPoint(D.x, D.y, D.z, D.yaw,",
    "      if (D.flatT <= 0 && !D.dry) { D.dist += D.spd * dt; const fx = D.x + Math.sin(D.yaw) * TRAIL_FWD, fz = D.z + Math.cos(D.yaw) * TRAIL_FWD, fy = hugY(fx, fz, D.y); while (D.dist >= SPACING) { D.dist -= SPACING; addPoint(fx, fy, fz, D.yaw,")
# ---- the master: headroom
rep("const lim = ctx.createDynamicsCompressor(); lim.threshold.value = -1.5; lim.knee.value = 0; lim.ratio.value = 20; lim.attack.value = 0.002; lim.release.value = 0.08; lim.connect(ctx.destination);",
    "const lim = ctx.createDynamicsCompressor(); lim.threshold.value = -4; lim.knee.value = 2; lim.ratio.value = 20; lim.attack.value = 0.001; lim.release.value = 0.12; const trimO = ctx.createGain(); trimO.gain.value = 0.9; lim.connect(trimO); trimO.connect(ctx.destination); /* (headroom: the limiter catches earlier, and the output sits under full scale) */")
rep("const hi = ctx.createBiquadFilter(); hi.type = 'highshelf'; hi.frequency.value = 7500; hi.gain.value = 2; hi.connect(comp);",
    "const hi = ctx.createBiquadFilter(); hi.type = 'highshelf'; hi.frequency.value = 7500; hi.gain.value = 0; hi.connect(comp);")
rep("const lo = ctx.createBiquadFilter(); lo.type = 'lowshelf'; lo.frequency.value = 110; lo.gain.value = 2.5; lo.connect(hi);",
    "const lo = ctx.createBiquadFilter(); lo.type = 'lowshelf'; lo.frequency.value = 110; lo.gain.value = 0; lo.connect(hi);")
rep("const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 30; hp.connect(lo);",
    "const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 45; const trimI = ctx.createGain(); trimI.gain.value = 0.7; hp.connect(trimI); trimI.connect(lo); /* (a quieter feed into the bus: about 3 dB under where it was, so the clipper stays out of the way) */")
# ---- the onboarding: the shop points at Back again; the locker's the place to look around
rep("    if (shopOpen) { if (!tutBrowseAt) tutBrowseAt = performance.now(); if (performance.now() - tutBrowseAt > 4200) return tutHide(); return tutShow('Take a look around, squirt. Express yourself!', null, 'browse', false, true, null, true); } /* (a free look round the shop: no pointing at Back, he steps aside after a few seconds; leaving on your own goes on to the locker) */",
    "    if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back');")
rep("      tutSet('vote'); return tutShow('Looking sharp, squirt. Done.', 'lookDone', 'done'); }",
    "      tutSet('vote'); tutBrowseAt = performance.now(); return tutShow('Take a look around, squirt. Express yourself!', null, 'browse', false, true, null, true); } /* (dressed: the locker's yours to play with; he steps aside after a few seconds, and closing it goes on with the lesson) */")
rep("  if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back'); if (lookOpen) return tutShow('Done', 'lookDone', 'done');",
    "  if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back'); if (lookOpen) { if (tutBrowseAt && performance.now() - tutBrowseAt < 4200) return tutShow('Take a look around, squirt. Express yourself!', null, 'browse', false, true, null, true); return tutHide(); } /* (no nudge at Done: closing the locker is up to you) */")
rep('<p class="ver">Version 230</p>', '<p class="ver">Version 231</p>')
open(DST, 'w').write(s)
print('ui164 ok', n0, '->', len(s))
