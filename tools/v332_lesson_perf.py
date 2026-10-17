"""v332: the first lesson's slow-motion parts and first-time moments run smoothly on a phone.

- The slow-motion vignette (the darkened edges and the gold frame while a tip waits on you) was a full-screen page layer over the live
  3D view, plus a second one for the deeper slow motion. On a phone every layer over the moving view is blended in again each frame,
  and each was painted whole when it appeared. It is now drawn in the frame's last pass, as the low-paint and hit edges already are
  (v293): the same gradients, the same gold edge, the same fades.
- Far-off characters step their pose 30 times a second (v296). That was 30 a second of game time, so in the lesson's slow motion the
  rival moved its limbs, ears and face 10 times a second (under 5 in the deepest slow motion) while the screen ran at 60. It is now 30
  a second of real time.
- The warm-up while loading draws everything once so the phone has set up how to draw it before play. The effects that start empty (the
  smoke puffs behind a fling, the paint drops and splashes, the sprinkles and the like, and the paint on the floor before any is laid)
  drew nothing, so the phone set them up the first time each turned up mid-match: in the lesson, the first time you did each thing.
  They are drawn once, with one instance, while warming up. So are the slingshot ball's lower-detail spheres, which only show once
  it's small on screen in flight.
- The tutorial's hands, arrow and Ol' Bloop had their shadows as filters on layers that move all the time, which a phone redraws every
  frame. The hands' and the arrow's shadows are now part of their drawings, and Ol' Bloop's soft shadow is drawn into his picture once.
- Smaller: in a match a tip's place is measured a few times a second, not every frame (each measure laid the page out again
  mid-frame); the slingshot band measures the screen once a pull, not on every finger move; the music's slow-motion muffle ends on its
  value when it's done, so the filter isn't worked out sample by sample from then on; Restart Game keeps how the phone's graphics
  settled (as it keeps the graphics choice), so a replayed lesson doesn't tune them all over again mid-lesson."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

SLOWA = ("uniform vec4 uSlowV; uniform vec2 uSlowPx;\n"
         "    // (v332) the lesson's slow-motion vignette, as the page drew it: x the darkening (its two gradients, normal and dark), y the gold frame, z the deeper\n"
         "    vec3 slowA(vec2 uv){ float t = length(uv * 2.0 - 1.0) * 0.7071068, k = uSlowV.x;\n"
         "      float a = uSlowV.z > 0.5 ? mix(0.34, 0.66, clamp((t - 0.3) / 0.7, 0.0, 1.0)) : t < 0.64 ? 0.3 * clamp((t - 0.34) / 0.3, 0.0, 1.0) : 0.3 + 0.42 * clamp((t - 0.64) / 0.36, 0.0, 1.0);\n"
         "      float d = t < 0.56 ? 0.3 * clamp((t - 0.24) / 0.32, 0.0, 1.0) : 0.3 + 0.2 * clamp((t - 0.56) / 0.44, 0.0, 1.0); vec2 e = min(uv, 1.0 - uv) / uSlowPx;\n"
         "      return vec3(a, 1.0 - step(1.0, min(e.x, e.y)), d * uSlowV.y) * k; }\n")
INK = "vec3(0.0902, 0.0745, 0.1255)"   # rgba(23,19,32): the vignette's ink
GOLD = "vec3(0.949, 0.757, 0.306)"     # var(--gold), #F2C14E

def apply(s):
    # ---- the slow-motion vignette: out of the page, into the frame's last pass
    s = rep(s, "uVigC: { value: new THREE.Vector3() } };",
               "uVigC: { value: new THREE.Vector3() }, uSlowV: { value: new THREE.Vector4() }, uSlowPx: { value: new THREE.Vector2(0.008, 0.004) } };")
    s = rep(s, "uniform sampler2D tEdge; uniform vec4 uEdgeK, uEdgeV; uniform vec3 uEdgeC, uHitC, uVigC;",
               "uniform sampler2D tEdge; uniform vec4 uEdgeK, uEdgeV; uniform vec3 uEdgeC, uHitC, uVigC; " + SLOWA + "   ", 2)
    # Graphics mode: over everything, last (the page layer was over the whole view)
    s = rep(s, "      c += (fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) - 0.5) / 255.0;\n",
               "      if (uSlowV.x > 0.003) { vec3 sv = slowA(vUv); c = mix(c, " + INK + ", sv.x); c = mix(c, " + GOLD + ", sv.y); c = mix(c, " + INK + ", sv.z); }\n"
               "      c += (fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) - 0.5) / 255.0;\n")
    # Performance mode: the light overlay pass, over what it already lays
    s = rep(s, "          gl_FragColor = acc; }` });",
               "          if (uSlowV.x > 0.003) { vec3 sv = slowA(vUv); acc = over(acc, " + INK + ", sv.x); acc = over(acc, " + GOLD + ", sv.y); acc = over(acc, " + INK + ", sv.z); }\n"
               "          gl_FragColor = acc; }` });")
    s = rep(s, "  if (EDGE.on || heatK > 0.02) edgeOverlay();",
               "  if (EDGE.on || heatK > 0.02 || EDGE_U.uSlowV.value.x > 0.003) edgeOverlay();")
    s = rep(s, "  edgeTick();\n  if (post) {", "  edgeTick(); slowTick();\n  if (post) {")
    s = rep(s, "function edgeReset() {",
               "// (v332) the lesson's slow-motion vignette: on and deeper fade as the page's did (CSS ease, 0.3 s and 0.2 s); the lesson still says\n"
               "// which by the page element's classes (on, deep, dark), now never shown\n"
               "const cssEase = x => { let t = x; for (let i = 0; i < 6; i++) { const u = 1 - t, f = 0.75 * u * u * t + 0.75 * u * t * t + t * t * t - x, d = 0.75 * u * u + 2.25 * t * t; if (Math.abs(f) < 1e-4 || d < 1e-6) break; t = Math.min(1, Math.max(0, t - f / d)); } const u = 1 - t; return 0.3 * u * u * t + 3 * u * t * t + t * t * t; };\n"
               "const SLOWF = [{ v: 0, a: 0, b: 0, t0: 0, d: 300 }, { v: 0, a: 0, b: 0, t0: 0, d: 200 }]; let slowEl = null;\n"
               "const slowStep = (c, to, now) => { if (c.b !== to) { c.a = c.v; c.b = to; c.t0 = now; } c.v = c.a + (c.b - c.a) * cssEase(Math.min(1, (now - c.t0) / c.d)); return c.v; };\n"
               "function slowTick() {\n"
               "  const el = slowEl || (slowEl = document.getElementById('tutSlow')), U = EDGE_U.uSlowV.value, now = performance.now(); if (!el) return;\n"
               "  const on = el.classList.contains('on'); U.x = slowStep(SLOWF[0], on ? 1 : 0, now); U.y = slowStep(SLOWF[1], on && el.classList.contains('deep') ? 1 : 0, now); U.z = el.classList.contains('dark') ? 1 : 0;\n"
               "  EDGE_U.uSlowPx.value.set(3 / Math.max(1, viewW), 3 / Math.max(1, viewH)); // (its gold frame: 3 points in from each edge)\n"
               "}\n"
               "function edgeReset() {")
    s = rep(s, ".tutslow.dark{background:radial-gradient(ellipse at center,rgba(23,19,32,.34) 30%,rgba(23,19,32,.66) 100%)}",
               ".tutslow.dark{background:radial-gradient(ellipse at center,rgba(23,19,32,.34) 30%,rgba(23,19,32,.66) 100%)}\n"
               ".tutslow{display:none!important} /* (v332: drawn in the 3D frame's last pass; the classes still say when) */")

    # ---- far-off characters: 30 poses a second of real time
    s = rep(s, "{ const adt = D && D.frozenT > 0 ? 0 : dt; if (!I.lodFar) { X.aAcc = 0; A.update(adt); } else { X.aAcc = (X.aAcc || 0) + adt; if (X.aAcc >= ANIM_FAR - 0.003) { A.update(Math.min(0.05, X.aAcc)); X.aAcc = 0; } } } /* (v296: far off, the pose at 30 a second) */",
               "{ const adt = D && D.frozenT > 0 ? 0 : dt; if (!I.lodFar) { X.aAcc = 0; A.update(adt); } else { X.aAcc = (X.aAcc || 0) + adt; const aNow = performance.now(); if (X.aAcc > 0 && (aNow - (X.aAt || 0) >= ANIM_FAR * 1000 - 3 || X.aAcc >= 0.05)) { A.update(Math.min(0.05, X.aAcc)); X.aAcc = 0; X.aAt = aNow; } } } /* (v296: far off, the pose at 30 a second; v332: 30 a second of real time, so slow motion doesn't make it 10) */")

    # ---- the warm-up: what starts empty is drawn once too, and the ball's lower-detail spheres
    s = rep(s, "function lodPass() { blobLOD(body); blobLOD(cBody); blobLOD(L2.body); blobLOD(L3.body); }",
               "let warmLod = false; // (v332: while the warm-up draws the ball's other spheres, the size check leaves them be)\n"
               "function lodPass() { if (warmLod) return; blobLOD(body); blobLOD(cBody); blobLOD(L2.body); blobLOD(L3.body); }")
    s = rep(s, "function warmRender(only, piece) {\n  if (vic) return; const hid = [], fc = [], fm = [], off = [];\n"
               "  scene.traverse(o => { if (!o.visible) { hid.push(o); o.visible = true; } if (o.frustumCulled) { fc.push(o); o.frustumCulled = false; }\n"
               "    if (only && (o.isMesh || o.isPoints || o.isLine || o.isSprite) && !only.has(o)) { off.push(o, o.layers.mask); o.layers.mask = 0; } });\n",
               "// (v332) what starts empty (an effect's pool with nothing in it, the floor's paint before any is laid) draws nothing, so the phone set it\n"
               "// up the first time it turned up mid-match; for the warm frame it has one instance (or one piece) to draw\n"
               "function warmRender(only, piece) {\n  if (vic) return; const hid = [], fc = [], fm = [], off = [], one = [], rng = new Map();\n"
               "  scene.traverse(o => { if (!o.visible) { hid.push(o); o.visible = true; } if (o.frustumCulled) { fc.push(o); o.frustumCulled = false; }\n"
               "    if (only && (o.isMesh || o.isPoints || o.isLine || o.isSprite) && !only.has(o)) { off.push(o, o.layers.mask); o.layers.mask = 0; }\n"
               "    else if (o.isInstancedMesh && o.count === 0) { one.push(o); o.count = 1; }\n"
               "    else if ((o.isMesh || o.isPoints || o.isLine) && o.geometry && o.geometry.drawRange.count === 0 && !rng.has(o.geometry)) { rng.set(o.geometry, 0); o.geometry.drawRange.count = o.isPoints ? 1 : o.isLine ? 2 : 3; } });\n")
    s = rep(s, "  try { renderFrame(); if (piece !== 1) { sun.shadow.needsUpdate = true; renderFrame(); } } catch (e) {}\n"
               "  shadowCache.on = scOn; for (let i = 0; i < off.length; i += 2) off[i].layers.mask = off[i + 1];\n",
               "  try { renderFrame(); if (piece !== 1) { sun.shadow.needsUpdate = true; renderFrame(); } warmLods(only); } catch (e) {}\n"
               "  for (const o of one) o.count = 0; for (const [g, n] of rng) g.drawRange.count = n;\n"
               "  shadowCache.on = scOn; for (let i = 0; i < off.length; i += 2) off[i].layers.mask = off[i + 1];\n")
    s = rep(s, "// (v269) the warm-up at the end of loading, in pieces.",
               "// (v332) the slingshot ball's lower-detail spheres: it changes to them once it's small on screen, in flight; the warm frame drew it as it was\n"
               "function warmLods(only) {\n"
               "  if (!BLOB_LODS) return; const ms = [];\n"
               "  for (const b of [body, cBody, L2.body, L3.body]) if (b) b.traverse(m => { if (m.isMesh && (BLOB_LODS.includes(m.geometry) || m.userData.lod) && (!only || only.has(m))) ms.push([m, m.geometry]); });\n"
               "  if (!ms.length) return; warmLod = true;\n"
               "  try { for (const L of [0, 1, 2]) { for (const [m, g] of ms) m.geometry = BLOB_LODS.includes(g) ? BLOB_LODS[L] : m.userData.lod[L >= 2 ? 1 : 0]; sun.shadow.needsUpdate = true; renderFrame(); } }\n"
               "  finally { for (const [m, g] of ms) m.geometry = g; warmLod = false; }\n"
               "}\n"
               "// (v269) the warm-up at the end of loading, in pieces.")

    # ---- the tutorial's hands, arrow and coach: shadows drawn in, not filters on layers that move all the time
    s = rep(s, '<i class="thand" aria-hidden="true"><svg viewBox="0 0 64 84"><g fill="#F2C08A"',
               '<i class="thand" aria-hidden="true"><svg viewBox="0 0 64 84"><g opacity=".35" transform="translate(3.6 4.8)" fill="#000" stroke="#000" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"><path d="M18 16c0-8 6-13 14-13h13c9 0 16 7 16 16v15c0 10-7 18-16 20H30c-6 0-10-3-12-9z"/><path d="M18 16v53c0 6 4 11 9.5 11S37 75 37 69V34"/></g><g fill="#F2C08A"')
    for sel in ('.tut .thand svg', '.tuthand svg', '.tutgest .ghand svg'):
        s = rep(s, sel + '{width:100%;height:100%;filter:drop-shadow(3px 4px 0 rgba(0,0,0,.35))}', sel + '{width:100%;height:100%;overflow:visible}')
    s = rep(s, '<svg viewBox="0 0 48 48"><path d="M8 17h18V7l17 17-17 17V31H8z"/></svg>',
               '<svg viewBox="0 0 48 48"><path class="sh" d="M8 17h18V7l17 17-17 17V31H8z" transform="translate(1.66 2.48)"/><path d="M8 17h18V7l17 17-17 17V31H8z"/></svg>')
    s = rep(s, "stroke:#171320;stroke-width:2.4;stroke-linejoin:round;filter:drop-shadow(2px 3px 0 rgba(0,0,0,.4));animation:tutnudge .55s ease-in-out infinite alternate}",
               "stroke:#171320;stroke-width:2.4;stroke-linejoin:round;overflow:visible;animation:tutnudge .55s ease-in-out infinite alternate}\n"
               ".tutarrow svg .sh{fill:#000;stroke:#000;opacity:.4}")
    s = rep(s, ".coachpop[data-side=\"l\"] b{scale:-1 1}",
               ".coachpop[data-side=\"l\"] b{scale:-1 1}\n.coachpop b.baked{filter:none}")
    s = rep(s, "coachEl.innerHTML = '<b></b>';",
               "coachEl.innerHTML = '<b></b>';\n"
               "// (v332) his soft shadow drawn into his picture once (the same blur, about 10 points round him): as a filter on a layer that bobs all\n"
               "// the time, a phone drew it again every frame\n"
               "{ const im = new Image(); im.onload = () => { try { const W = im.naturalWidth, H = im.naturalHeight, c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');\n"
               "    g.shadowColor = 'rgba(23,19,32,.35)'; g.shadowBlur = Math.round(W / 16); g.drawImage(im, 0, 0);\n"
               "    c.toBlob(bl => { if (!bl) return; const b = coachEl.firstChild; b.style.backgroundImage = 'url(' + URL.createObjectURL(bl) + ')'; b.classList.add('baked'); }, 'image/png'); } catch (e) {} };\n"
               "  im.src = 'art/coach.webp'; }")

    # ---- smaller: a tip's place in a match a few times a second; the slingshot band measures once a pull
    s = rep(s, "  if (tutTip) tutPlace(); else if (popMoved) { popMoved = false; $('pop').style.top = ''; }",
               "  if (tutTip) { if (state !== 'play' || tutPlaceDue()) tutPlace(); } else if (popMoved) { popMoved = false; $('pop').style.top = ''; }")
    s = rep(s, "let popMoved = false;\n",
               "let popMoved = false;\n"
               "// (v332) in a match a tip, its hand and the pop text sit still: measured a few times a second (and at once when the tip or the screen\n"
               "// changes), not every frame, each measure having made the page lay itself out again mid-frame\n"
               "let tutPlaceAt = 0, tutPlaceK = '';\n"
               "function tutPlaceDue() { const n = performance.now(), k = tutTip.key + '|' + viewW + 'x' + viewH + '|' + tutEl.className; if (k === tutPlaceK && n - tutPlaceAt < 250) return false; tutPlaceK = k; tutPlaceAt = n; return true; }\n")
    s = rep(s, "function slingDraw(cx, cy) {\n  const r = stage.getBoundingClientRect(),",
               "let slR = null; const slingRect = () => slR || (slR = stage.getBoundingClientRect()); window.addEventListener('resize', () => { slR = null; }); // (v332: once a pull, not on every move of the finger)\n"
               "function slingDraw(cx, cy) {\n  const r = slingRect(),")
    s = rep(s, "function beginHold(t, x, y) { startCharge(P);", "function beginHold(t, x, y) { slR = null; startCharge(P);")

    # ---- the music's slow-motion muffle ends on its value
    s = rep(s, "musLP.frequency.cancelScheduledValues(t); musLP.frequency.setTargetAtTime(on ? 1100 : 20000, t, on ? 0.07 : 0.18); trkBus.gain.cancelScheduledValues(t); trkBus.gain.setTargetAtTime(on ? 0.72 : 1, t, on ? 0.08 : 0.2);",
               "musLP.frequency.cancelScheduledValues(t); musLP.frequency.setTargetAtTime(on ? 1100 : 20000, t, on ? 0.07 : 0.18); trkBus.gain.cancelScheduledValues(t); trkBus.gain.setTargetAtTime(on ? 0.72 : 1, t, on ? 0.08 : 0.2);"
               " musLP.frequency.setValueAtTime(on ? 1100 : 20000, t + (on ? 0.42 : 1.08)); trkBus.gain.setValueAtTime(on ? 0.72 : 1, t + (on ? 0.48 : 1.2)); /* (v332: each sweep ends on its value, so the filter isn't worked out sample by sample from then on) */")

    # ---- Restart Game (and a fresh start after logging out) keep how this phone's graphics settled
    s = rep(s, "for (const k of ['muted', 'sfxOff', 'musicOff', 'gfx', 'orient'])", "for (const k of ['muted', 'sfxOff', 'musicOff', 'gfx', 'orient', 'qLv', 'qSt'])", 2)
    return s
