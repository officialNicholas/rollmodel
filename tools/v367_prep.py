"""v367: no more long frozen stretch on "New canvas" (or "Same canvas"), on any device.

- Before a match, under the closed wipe, the game built the canvas and then made every shader the match could need in one go. The first
  match after a launch, and every first lesson (the tutorial never goes past Choose Event, where the late warm-up runs), compiled them all
  there: some 115 programs, seconds of a screen that couldn't draw, longer still in the Simulator. The same one-go warm-up ran after a
  canvas vote, for an online match and for Same canvas.
- Now one step does it, a piece at a time (prepMatch): the canvas built, the shader compile handed to the browser to do in the
  background where it can (warmCompile), then the late warm-up's pieces carried on from wherever they'd got to, each piece finished (its
  fence passed) before the next. A slim bar under the wipe's words fills as they go, with a sheen running along it, so the screen is
  plainly loading, never stuck. With the late warm-up already done a new canvas takes a few pieces, not all of them.
- While the wipe is shut the scene isn't drawn every frame as well (nothing of it shows, and those frames only competed with the pieces).
- A canvas rebuilt in the menu once everything's warm (the shuffle, the characters' models arriving) warms in a few pieces between frames,
  each followed by a normal frame, instead of one long one."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the bar under the wipe's words
    s = rep(s, ".iris.txt b{opacity:.92;transform:translateY(-50%) scale(1)}\n",
               ".iris.txt b{opacity:.92;transform:translateY(-50%) scale(1)}\n"
               "/* (v367) the work under the wipe before a match: a slim bar under its words, filling as the pieces are done, a sheen running along it */\n"
               ".iris .irbar{position:absolute;left:50%;top:calc(50% + 32px);width:min(176px,46vw);height:6px;transform:translateX(-50%);border-radius:6px;background:rgba(255,241,223,.14);overflow:hidden;opacity:0;transition:opacity .25s}\n"
               ".iris.work .irbar{opacity:1}\n"
               ".iris .irbar span{position:absolute;inset:0;border-radius:6px;background:linear-gradient(90deg,#E3122F,#FF6175);transform-origin:0 50%;transform:scaleX(var(--k,0));transition:transform .35s cubic-bezier(.25,.8,.3,1);overflow:hidden}\n"
               ".iris .irbar span::after{content:'';position:absolute;top:0;bottom:0;left:0;width:60%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.5),transparent);animation:irsheen 1.1s linear infinite}\n"
               "@keyframes irsheen{from{transform:translateX(-100%)}to{transform:translateX(180%)}}\n"
               "@media (prefers-reduced-motion:reduce){.iris .irbar span::after{animation:none}}\n")
    s = rep(s, '<div class="iris" id="iris" hidden aria-hidden="true"><i></i><b id="irisText"></b></div>',
               '<div class="iris" id="iris" hidden aria-hidden="true"><i></i><b id="irisText"></b><span class="irbar"><span></span></span></div>')

    # the step itself, by the late warm-up it carries on
    s = rep(s, "let warmQ = 0, bootWarm = false; const queueWarm = () => { clearTimeout(warmQ); if (bootWarm && LW.done) warmQ = setTimeout(warmRender, 30); };",
               "let warmQ = 0, bootWarm = false; const queueWarm = () => { clearTimeout(warmQ); if (bootWarm && LW.done) warmQ = setTimeout(bgWarm, 30); };\n"
               "// (v367) the floaters' see-through pass and what only a whole warm-up covers (the victory pose, the edge, a normal frame)\n"
               "const floatSet = () => { const fl = new Set(), fm = new Set(); for (const f of floaters) for (const m of f.mats) fm.add(m); scene.traverse(o => { if (o.material && [].concat(o.material).some(m => fm.has(m))) fl.add(o); }); return fl; };\n"
               "// (v367) before a match, under the closed wipe: the canvas built (make), then the shaders a piece at a time, each piece finished before\n"
               "// the next, the bar under the wipe's words filling as they go. In one go this froze the screen for seconds: the first match after a\n"
               "// launch (and every first lesson, which never passes Choose Event where the late warm-up runs) made some 115 programs there\n"
               "let prepOn = false;\n"
               "const irisBarK = k => { const s = irisEl.querySelector('.irbar span'); if (s) s.style.setProperty('--k', Math.max(0, Math.min(1, k)).toFixed(3)); };\n"
               "const twoFrames = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r())));\n"
               "async function prepMatch(make, text) {\n"
               "  if (!make && LW.done) return; prepOn = true; building = true; clearTimeout(warmQ);\n"
               "  irisBarK(0); if (text || make) { $('irisText').textContent = text || 'New canvas'; irisEl.classList.add('txt'); } else if (!$('irisText').textContent) { $('irisText').textContent = 'Getting ready'; irisEl.classList.add('txt'); }\n"
               "  irisEl.classList.add('work');\n"
               "  try {\n"
               "    let k0 = 0;\n"
               "    if (make) { await twoFrames(); make(); mapUsed = false; clearTimeout(warmQ); LW.parts = null; k0 = 0.12; irisBarK(k0); await twoFrames(); } // (the bar shows before the build; a new canvas, new pieces)\n"
               "    const lw = !LW.done;\n"
               "    if (lw && !LW.asked) { LW.asked = true; try { await warmCompile(); } catch (e) {} } // (where the browser builds them in the background, every one asked for now)\n"
               "    const parts = lw ? (LW.parts || (LW.i = 0, LW.parts = warmPieces(scene, 16))) : warmPieces(scene, 6);\n"
               "    for (let i = lw ? LW.i : 0; i < parts.length; i++) { warmRender(parts[i], i ? 1 : 2); if (lw) LW.i = i + 1; irisBarK(k0 + (1 - k0) * 0.92 * (i + 1) / parts.length); await gpuIdle(2500); }\n"
               "    warmRender(floatSet()); irisBarK(1); await gpuIdle(2500);\n"
               "    if (lw) LW.done = true;\n"
               "  } catch (e) { console.error(e); }\n"
               "  finally { building = false; prepOn = false; irisEl.classList.remove('work'); }\n"
               "}\n"
               "// (v367) a canvas rebuilt in the menu once everything's warm (the shuffle, the characters' models in): a few pieces between frames,\n"
               "// each followed by a normal frame (a warm frame shows everything at once), not one long freeze\n"
               "let bgW = 0;\n"
               "async function bgWarm() {\n"
               "  const id = ++bgW, ok = () => id === bgW && !building && !irisBusy && !prepOn && !vic, parts = warmPieces(scene, 6);\n"
               "  for (let i = 0; i < parts.length; i++) { if (!ok()) return; warmRender(parts[i], i ? 1 : 2); try { renderFrame(); } catch (e) {} await gpuIdle(2500); }\n"
               "  if (ok()) warmRender(floatSet());\n"
               "}")

    # the scene isn't drawn while the wipe is shut on that work
    s = rep(s, "  if (!(state === 'menu' && (menuPage === 'worlds' || menuPage === 'events' || menuPage === 'strokes' || menuPage === 'locker' || !commModalEl.hidden || !friendsModalEl.hidden || !onModalEl.hidden || lobbyCovered()))) renderFrame();",
               "  if (prepOn) {} else if (!(state === 'menu' && (menuPage === 'worlds' || menuPage === 'events' || menuPage === 'strokes' || menuPage === 'locker' || !commModalEl.hidden || !friendsModalEl.hidden || !onModalEl.hidden || lobbyCovered()))) renderFrame();")

    # the places that did it all in one go
    s = rep(s, "    if (mapUsed) { building = true; freshMap(); clearTimeout(warmQ); warmRender(); building = false; }\n"
               "    else if (!LW.done) { clearTimeout(warmQ); warmRender(); } // (v309: the first match makes what launch left for later)\n"
               "    showVS(beginMatch);\n"
               "  }, null, mapUsed ? 'New canvas' : '');",
               "    const go = () => showVS(beginMatch); clearTimeout(warmQ);\n"
               "    if (mapUsed || !LW.done) prepMatch(mapUsed ? freshMap : null).then(go); else go(); // (v367: in pieces, a bar filling; v309: the first match makes what launch left for later)\n"
               "  }, null, mapUsed ? 'New canvas' : LW.done ? '' : 'Getting ready');")
    s = rep(s, "  irisClose(() => { menu.hidden = true; end.hidden = true; pauseEl.hidden = true; hud.classList.add('off'); building = true; genWorld(sd, op); mapUsed = false; warmRender(); building = false; beginMatch(); }, null, 'Same canvas');",
               "  irisClose(() => { menu.hidden = true; end.hidden = true; pauseEl.hidden = true; hud.classList.add('off'); prepMatch(() => genWorld(sd, op), 'Same canvas').then(beginMatch); }, null, 'Same canvas');")
    s = rep(s, "    if (win && TH.id !== win) { building = true; genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id, themes: [win] }); mapUsed = false; clearTimeout(warmQ); warmRender(); building = false; }\n"
               "    cb(); } }); };",
               "    if (win && TH.id !== win) prepMatch(() => genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id, themes: [win] })).then(cb); else cb(); } }); }; // (v367: the wipe is still shut under the vote)")
    s = rep(s, "    building = true; genWorld(m.seed >>> 0, { easy: false, avoid: null, themes: NET_THEMES, flat: false }); mapUsed = false; clearTimeout(warmQ); warmRender(); building = false;\n"
               "    netSendLayout(); showVS(beginMatch);",
               "    prepMatch(() => genWorld(m.seed >>> 0, { easy: false, avoid: null, themes: NET_THEMES, flat: false })).then(() => { if (!NM || NM.id !== m.matchId) return; netSendLayout(); showVS(beginMatch); });")
    return s
