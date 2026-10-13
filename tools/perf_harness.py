"""Builds ws/pc_perf.html: the test harness with per-stage timers wired in, inside the game's own scope (its functions are local there,
so they are rebound in place), plus window.__perfAI() to hand the player to the game's own AI"""
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
src = open(WS + '/pc_h.html').read()
names = ['step', 'visuals', 'renderFrame', 'flushTrail', 'aiStep', 'aiThink', 'updateParts', 'updateTrail', 'stepBalls', 'updateBrushes', 'updateWeather', 'detectThreat', 'idleStep', 'placeFace',
         'blobVisual', 'cpuLook', 'lodPass', 'tutFrame', 'stepCoffins', 'itemTick', 'stepGift', 'updatePuffs', 'updateFx', 'updateConfetti', 'updateDebris', 'updateBoom', 'updateSprinkle', 'updateCrowns',
         'flushGrooves', 'smokeStep', 'slimeVisual', 'updateShots', 'updateOrb', 'updateSlamBtn', 'tunePerf', 'checkHold', 'stepBlob', 'moveBlob', 'paintBlob', 'stampTrail', 'updateMovers', 'stepRivals', 'aiFlingPaint', 'dijkstra', 'aiPlan', 'aiPick', 'aiGo', 'aiFollow', 'aiSteer', 'aiSafe', 'losClear', 'lineClear', 'stageTick', 'coneTick', 'steamTick', 'renderFrame', 'mirrorPass', 'covTick', 'teamCov', 'splashPush', 'addSplat', 'stamp']
inj = "const __pf = window.__pf = { fb: [], st: {}, cur: null, on: false, wrapped: [] };\n" \
      "const __pw = (name, f) => function () { if (!__pf.cur) return f.apply(this, arguments); const t0 = performance.now(); try { return f.apply(this, arguments); } finally { __pf.cur[name] = (__pf.cur[name] || 0) + performance.now() - t0; } };\n"
for n in names:
    inj += f"try {{ if (typeof {n} === 'function') {{ {n} = __pw('{n}', {n}); __pf.wrapped.push('{n}'); }} }} catch (e) {{}}\n"
inj += "{ const fb0 = frameBody; frameBody = function (t) { if (!__pf.on) return fb0.apply(this, arguments); __pf.cur = {}; const t0 = performance.now(); try { return fb0.apply(this, arguments); } finally { const __d = performance.now() - t0; __pf.fb.push(__d); if (__d > 6) (__pf.slow || (__pf.slow = [])).push([+__d.toFixed(1), Object.fromEntries(Object.entries(__pf.cur).filter(e => e[1] > 0.4).map(e => [e[0], +e[1].toFixed(1)]))]); for (const k in __pf.cur) (__pf.st[k] || (__pf.st[k] = [])).push(__pf.cur[k]); __pf.cur = null; } }; }\n" \
       "window.__perfAI = () => { P.cpu = true; aiReset(P); };\n"
inj += "try { aiSafe = (o => function (D, want) { const r = o.apply(this, arguments); if (window.__trace && D === window.__traceD) window.__lastSafe = [want, r]; return r; })(aiSafe); aiSteer = (o => function (D, tx, tz, dt, urgent, precise) { window.__lastSafe = null; const r = o.apply(this, arguments); if (window.__trace && D === window.__traceD) __trace.push([+runT.toFixed(3), +tx.toFixed(2), +tz.toFixed(2), +D.x.toFixed(2), +D.z.toFixed(2), +D.yaw.toFixed(3), +D.steer.toFixed(3), D.ai.mode, urgent ? 1 : 0, precise ? 1 : 0, window.__lastSafe ? +window.__lastSafe[0].toFixed(3) : null, window.__lastSafe ? +window.__lastSafe[1].toFixed(3) : null, D.charging ? 1 : 0, +D.spd.toFixed(2), D.ai.pi, D.ai.path ? D.ai.path.length : 0, D.ai.tgt, +D.turn.toFixed(2)]); return r; })(aiSteer); } catch (e) { console.error('trace wrap', e); }\n"
inj += "try { const __tp0 = tunePerf; tunePerf = ft => { if (!window.__tpManual) __tp0(ft); }; window.__tp = ft => __tp0(ft); window.__setCpu = v => { lastCpu = v; }; window.__q = () => ({ lvl: qLvl, n: Q_LAD.length, lad: Q_LAD, pr: curPR, post: post && { b: post.bloom, d: post.dof, m: post.mirror }, sh: shadowLite, ban: qBan.slice(), capped: qCapped, win: qWin, state }); } catch (e) {}\n"
# (harness only) when the game's AI drives you, your blob takes the AI's steering instead of the finger's
OLDIN = "let input = D === P ? (keyL || keyR ? (keyR ? 1 : 0) - (keyL ? 1 : 0) : steerIn) : D.steer;"
assert src.count(OLDIN) == 1
src = src.replace(OLDIN, "let input = D === P && !P.cpu ? (keyL || keyR ? (keyR ? 1 : 0) - (keyL ? 1 : 0) : steerIn) : D.steer;")
anchor = "window.__orbKind = window.__orbKind === undefined"
assert src.count(anchor) == 1
src = src.replace(anchor, inj + anchor)
open(WS + '/pc_perf.html', 'w').write(src); print('ok', len(src))
