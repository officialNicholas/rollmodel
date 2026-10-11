"""Builds ws/pc_perf.html: the test harness with per-stage timers wired in, inside the game's own scope (its functions are local there,
so they are rebound in place), plus window.__perfAI() to hand the player to the game's own AI"""
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
src = open(WS + '/pc_h.html').read()
names = ['step', 'visuals', 'renderFrame', 'flushTrail', 'aiStep', 'aiThink', 'updateParts', 'updateTrail', 'stepBalls', 'updateBrushes', 'updateWeather', 'detectThreat', 'idleStep', 'placeFace',
         'blobVisual', 'cpuLook', 'lodPass', 'tutFrame', 'stepCoffins', 'itemTick', 'stepGift', 'updatePuffs', 'updateFx', 'updateConfetti', 'updateDebris', 'updateBoom', 'updateSprinkle', 'updateCrowns',
         'flushGrooves', 'smokeStep', 'slimeVisual', 'updateShots', 'updateOrb', 'updateSlamBtn', 'tunePerf', 'checkHold', 'stepBlob', 'moveBlob', 'paintBlob', 'stampTrail', 'updateMovers', 'stepRivals']
inj = "const __pf = window.__pf = { fb: [], st: {}, cur: null, on: false, wrapped: [] };\n" \
      "const __pw = (name, f) => function () { if (!__pf.cur) return f.apply(this, arguments); const t0 = performance.now(); try { return f.apply(this, arguments); } finally { __pf.cur[name] = (__pf.cur[name] || 0) + performance.now() - t0; } };\n"
for n in names:
    inj += f"try {{ if (typeof {n} === 'function') {{ {n} = __pw('{n}', {n}); __pf.wrapped.push('{n}'); }} }} catch (e) {{}}\n"
inj += "{ const fb0 = frameBody; frameBody = function (t) { if (!__pf.on) return fb0.apply(this, arguments); __pf.cur = {}; const t0 = performance.now(); try { return fb0.apply(this, arguments); } finally { __pf.fb.push(performance.now() - t0); for (const k in __pf.cur) (__pf.st[k] || (__pf.st[k] = [])).push(__pf.cur[k]); __pf.cur = null; } }; }\n" \
       "window.__perfAI = () => { P.cpu = true; aiReset(P); };\n"
inj += "try { window.__tp = ft => tunePerf(ft); window.__setCpu = v => { lastCpu = v; }; window.__q = () => ({ lvl: qLvl, n: Q_LAD.length, lad: Q_LAD, pr: curPR, post: post && { b: post.bloom, d: post.dof, m: post.mirror }, sh: shadowLite, ban: qBan.slice(), capped: qCapped, win: qWin, state }); } catch (e) {}\n"
anchor = "window.__orbKind = window.__orbKind === undefined"
assert src.count(anchor) == 1
src = src.replace(anchor, inj + anchor)
open(WS + '/pc_perf.html', 'w').write(src); print('ok', len(src))
