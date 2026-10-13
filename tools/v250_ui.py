# v250 economy, weather, cue and screen changes, applied by ui190_patch.py: less paint used, shop prices down about 15%, the rain
# waters paint down, a soft pointer to the nearest basin, the winner screen's framing in portrait, and a smoother canvas vote page
def apply(s):
    def rep(old, new, count=1):
        nonlocal s
        c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
        s = s.replace(old, new)

    # ---- paint lasts longer: rolling drains about 30% slower, splats and dodge rolls cost a quarter less (the pound's one bar is kept)
    rep("const VS_CFG = { rivals: 12, pots: 8, speed: 5.4, drain: 1 / 15, brushes: 0 };", "const VS_CFG = { rivals: 12, pots: 8, speed: 5.4, drain: 1 / 21, brushes: 0 };")
    rep("speed: 5.06, drain: 1 / 14, brushes: 0 },", "speed: 5.06, drain: 1 / 20, brushes: 0 },")
    rep("speed: 5.4, drain: 1 / 13, brushes: 0 },", "speed: 5.4, drain: 1 / 18, brushes: 0 },")
    rep("speed: 5.75, drain: 1 / 12, brushes: 0 },", "speed: 5.75, drain: 1 / 17, brushes: 0 },")
    rep("speed: Math.min(6.7, 5.75 + k * 0.17), drain: 1 / 12, brushes: 0 }", "speed: Math.min(6.7, 5.75 + k * 0.17), drain: 1 / 17, brushes: 0 }")
    rep("const SPLAT_R = 1.35, SPLAT_COST = 0.08,", "const SPLAT_R = 1.35, SPLAT_COST = 0.06,")
    rep("ROLL_COST = 0.04;", "ROLL_COST = 0.03;")

    # ---- the Paint Shop about 15% cheaper across the board (rounded to fives)
    rep("const PRICES = { sly: 640, flower: 170, pearls: 190, scarf: 210, bowtie: 220, stache: 230, beanie: 240, party: 280, monocle: 340, lashes: 260, glasses: 320, patch: 390, fangs: 470, tiara: 560, tophat: 680, bunny: 760, pirate: 820, hockey: 900, skull: 980, halo: 1000, zombie: 1150, hat: 1300 };",
        "const PRICES = { sly: 545, flower: 145, pearls: 160, scarf: 180, bowtie: 185, stache: 195, beanie: 205, party: 240, monocle: 290, lashes: 220, glasses: 270, patch: 330, fangs: 400, tiara: 475, tophat: 580, bunny: 645, pirate: 695, hockey: 765, skull: 835, halo: 850, zombie: 975, hat: 1105 };")
    rep("return PRICES[w.id] || (w.season ? 1000 : w.slot === 'head' ? 600 : 300); };", "return PRICES[w.id] || (w.season ? 850 : w.slot === 'head' ? 510 : 255); };")

    # ---- the rain waters your paint down like a puddle does: the whole shower and a little after (under a roof, or in a basin, you stay dry)
    rep("function dilute(D) {", "const RAIN_DIL = 2.5, roofOver = D => { for (const b of qcell(qgB, D.x, D.z)) if (b[4] > D.y + 0.6 && inR(D.x, D.z, b)) return true; return false; };\nfunction dilute(D, rain) {")
    rep("hint('dilute', 'Puddles water your paint down', 2.6);", "hint(rain ? 'rdilute' : 'dilute', rain ? 'Rain waters your paint down' : 'Puddles water your paint down', 2.6);")
    rep("  if (D.exposed) { D.paint -= BURN_RATE * 2.4 * dt; burnFx(D, dt); if (D.paint <= 0) { D.paint = 0; if (!D.dry && D.st === 'play') goDry(D); } } // (the sun dries you out; it no longer knocks you out)\n",
        "  if (D.exposed) { D.paint -= BURN_RATE * 2.4 * dt; burnFx(D, dt); if (D.paint <= 0) { D.paint = 0; if (!D.dry && D.st === 'play') goDry(D); } } // (the sun dries you out; it no longer knocks you out)\n"
        "  if (wxPhase === 'rain' && !roofOver(D)) { if (D.dilT <= 0) dilute(D, true); D.dilT = Math.max(D.dilT, RAIN_DIL); } // (out in the rain: watered down till a moment after it stops)\n")
    rep("wxBanner('Rain!', rainsSeen++ ? '' : 'Everyone speeds up');", "wxBanner('Rain!', rainsSeen++ ? '' : 'Faster, but your paint thins');")

    # ---- the way to paint: a soft double chevron on the floor by you, pointing at the nearest basin you can get into, when you're out of
    # paint (or nearly) or the heat is on its way (or burning you); it fades once you're close, or safe
    rep("function visuals(dt, rdt) {\n",
        "const potCue = (() => { const sh = new THREE.Shape(); sh.moveTo(-0.24, -0.15); sh.lineTo(0, 0.03); sh.lineTo(0.24, -0.15); sh.lineTo(0.24, -0.02); sh.lineTo(0, 0.16); sh.lineTo(-0.24, -0.02); sh.closePath();\n"
        "  const geo = new THREE.ShapeGeometry(sh); geo.rotateX(Math.PI / 2); const g = new THREE.Group(); g.visible = false;\n"
        "  for (let i = 0; i < 2; i++) { const c = new THREE.Group(), mk = (col, o) => new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide })), dk = mk(0x1A1030), wt = mk(0xFFF6EA);\n"
        "    dk.scale.set(1.32, 1, 1.32); dk.position.y = -0.004; dk.renderOrder = 3; wt.renderOrder = 4; c.add(dk, wt); g.add(c); }\n"
        "  scene.add(g); return g; })();\n"
        "let potCueK = 0, potCueT = 0, potCueYaw = 0, potCueTo = null, potCueAt = -9;\n"
        "function potCueTick(dt) {\n"
        "  const sunny = wxPhase === 'warn' || wxPhase === 'sun', want = state === 'play' && P.st === 'play' && !tut && !P.rocket && !P.turret && P.giantT <= 0 && !kcam && tutArrowEl.hidden && (P.dry || P.paint < 0.1 || wxPhase === 'warn' || (wxPhase === 'sun' && P.exposed));\n"
        "  if (want && clock - potCueAt > 0.25) { potCueAt = clock; let bd = 1e9; potCueTo = null; for (const p of pots) { if (!potUp(p) || p.occ || p.cool > 0 || (!sunny && p.ink <= 0.05)) continue; const d = Math.hypot(p.x - P.x, p.z - P.z) + Math.abs(p.y - P.y) * 1.5; if (d < bd) { bd = d; potCueTo = p; } } }\n"
        "  const p = potCueTo, on = want && !!p && Math.hypot(p.x - P.x, p.z - P.z) > 2.6, was = potCueK;\n"
        "  potCueK += ((on ? 1 : 0) - potCueK) * Math.min(1, dt * (on ? 3 : 6));\n"
        "  if (potCueK < 0.01) { if (potCue.visible) potCue.visible = false; return; }\n"
        "  potCue.visible = true; if (p) { const a = Math.atan2(p.x - P.x, p.z - P.z); potCueYaw = was < 0.01 ? a : potCueYaw + wrapA(a - potCueYaw) * Math.min(1, dt * 8); }\n"
        "  potCueT = (potCueT + dt * 0.85) % 1; const sx = Math.sin(potCueYaw), sz = Math.cos(potCueYaw);\n"
        "  potCue.children.forEach((c, i) => { const u = (potCueT + i * 0.5) % 1, r = 1.0 + 0.7 * u, x = P.x + sx * r, z = P.z + sz * r, g = surfaceUnder(x, z, P.y + 0.6, true), k = g > -Infinity ? potCueK * Math.sin(u * Math.PI) : 0;\n"
        "    c.position.set(x, (g > -Infinity ? g : P.y) + 0.05, z); c.rotation.y = potCueYaw; c.children[0].material.opacity = 0.26 * k; c.children[1].material.opacity = 0.7 * k; });\n"
        "}\n"
        "function visuals(dt, rdt) {\n")
    rep("  detectThreat(playing);\n", "  detectThreat(playing); potCueTick(dt);\n")

    # ---- the winner screen in portrait: the whole character, floor to hat, in the open space between the words up top and the slanted
    # band behind the bottom row (the band used to cover its hands and body)
    rep("  if (!vic) return; const top = vicEl.querySelector('.vtop'), foot = vicEl.querySelector('.vfoot'), y0 = top.offsetTop + top.offsetHeight, y1 = foot.offsetTop, Hh = Math.max(1, viewH);\n"
        "  vic.cy = clamp(((y0 + y1) / 2 + 10) / Hh, 0.26, 0.5); vic.room = clamp((y1 - y0) / Hh, 0.12, 1);\n",
        "  if (!vic) return; const top = vicEl.querySelector('.vtop'), foot = vicEl.querySelector('.vfoot'), rib = vicEl.querySelector('.vrib'), y0 = top.offsetTop + top.offsetHeight, Hh = Math.max(1, viewH);\n"
        "  // (down to the band's top edge where it crosses the middle, less a little for its slope across the character; layout offsets, so its slide-in doesn't count)\n"
        "  const y1 = Math.min(foot.offsetTop, rib ? rib.offsetTop - 12 : 1e9);\n"
        "  vic.cy = clamp((y0 + y1) / 2 / Hh, 0.2, 0.5); vic.room = clamp((y1 - y0) / Hh, 0.12, 1);\n")
    rep("  const vk = VP.slime && VP.slime.kind === 'axo' ? 1.38 : 1; // (the axolotl celebrates standing up: taller than the slime)\n"
        "  // close enough that the winner fills the shot, far enough that it (or the pair) fits across a narrow phone screen\n"
        "  const tv = Math.tan(fov * Math.PI / 360), th = tv * W / Hh, dist = Math.max(0.86 / tv, (n > 1 ? 1.08 : 0.6) / th, land ? 0 : 0.5 / (tv * (vic.room || 1))) * (1.07 - 0.07 * Math.min(1, t / 4)) * vk, a = vic.yaw + Math.sin(t * 0.4) * 0.05;\n"
        "  vicCam.position.set(mx + Math.sin(a) * dist, my + 0.3 * vk, mz + Math.cos(a) * dist); vicCam.lookAt(mx, my + 0.44 * vk, mz);\n",
        "  const vk = VP.slime && VP.slime.kind === 'axo' ? 1.38 : 1, tv = Math.tan(fov * Math.PI / 360), th = tv * W / Hh, a = vic.yaw + Math.sin(t * 0.4) * 0.05, ease = 1.07 - 0.07 * Math.min(1, t / 4);\n"
        "  if (land) { // close enough that the winner fills the shot, far enough that it (or the pair) fits across the screen\n"
        "    const dist = Math.max(0.86 / tv, (n > 1 ? 1.08 : 0.6) / th) * ease * vk; vicCam.position.set(mx + Math.sin(a) * dist, my + 0.3 * vk, mz + Math.cos(a) * dist); vicCam.lookAt(mx, my + 0.44 * vk, mz);\n"
        "  } else { // portrait: floor to hat (VIC_HT) fitted to the open space and centred in it, and the pair across a narrow screen\n"
        "    const dist = Math.max((n > 1 ? 1.08 : 0.6) / th, (VIC_HT + 0.06) / (2 * tv * (vic.room || 0.4))) * ease;\n"
        "    vicCam.position.set(mx + Math.sin(a) * dist, my + VIC_HT * 0.62, mz + Math.cos(a) * dist); vicCam.lookAt(mx, my + VIC_HT * 0.5, mz);\n"
        "  }\n")
    rep("const VIC_C0 = 1.9, VIC_T = 5.2, VIC_TS = 4.2;", "const VIC_HT = 1.25; // (the character from the floor to the top of a tall hat: the portrait framing fits this)\nconst VIC_C0 = 1.9, VIC_T = 5.2, VIC_TS = 4.2;")

    # ---- the canvas vote page: the painting reaching the middle is picked at once (one light pass a frame, not after the scroll settles), and
    # the canvas behind the menu (not drawn on this page) is built when you leave it rather than mid-scroll; Play builds the pick anyway
    rep("gallery.addEventListener('scroll', () => { renderGo(); clearTimeout(galT); galT = setTimeout(() => { const b = worldAt(); if (b && b.dataset.s !== 'next' && b.dataset.s !== stageSel) selectWorld(b.dataset.s); renderGo(); }, 140); }, { passive: true });",
        "gallery.addEventListener('scroll', () => { if (galT) return; galT = requestAnimationFrame(() => { galT = 0; const b = worldAt(); if (b && b.dataset.s !== 'next' && b.dataset.s !== stageSel) selectWorld(b.dataset.s); else renderGo(); }); }, { passive: true });\n"
        "let worldDirty = false;\n"
        "function worldBuild(s) { if (state !== 'menu') return; if (menuPage === 'worlds') { worldDirty = true; return; } setTimeout(() => { if (state !== 'menu' || building || (s && stageSel !== s)) return; freshMap(); resetRun(); decorate(); menuPose(); renderStages(); kick($('cvName'), 'bump'); }, 40); }")
    rep("  if (state === 'menu') setTimeout(() => { if (state !== 'menu' || building || stageSel !== s) return; freshMap(); resetRun(); decorate(); menuPose(); renderStages(); kick($('cvName'), 'bump'); }, 40);",
        "  worldBuild(s); kick($('cvName'), 'bump');")
    rep("  if (state === 'menu') setTimeout(() => { if (state !== 'menu' || building || stageSel !== t.dataset.s) return; freshMap(); resetRun(); decorate(); menuPose(); renderStages(); kick($('cvName'), 'bump'); }, 40); });",
        "  worldBuild(t.dataset.s); kick($('cvName'), 'bump'); });")
    rep("  if (menuPage !== 'worlds') return; closeSeason(); menuPage = 'home'; menu.dataset.page = 'home'; $('mWorld').hidden = true; $('mHome').hidden = false; heroT = 0;",
        "  if (menuPage !== 'worlds') return; closeSeason(); menuPage = 'home'; menu.dataset.page = 'home'; $('mWorld').hidden = true; $('mHome').hidden = false; heroT = 0;\n"
        "  if (worldDirty) { worldDirty = false; if (GEN.key !== mapKey()) worldBuild(); } // (the pick's canvas, built now that it shows)")
    rep("$('cvName').textContent = (mode === 'solo' ? '' : 'Your vote \\u00b7 ') + TH.label; $('shuffleBtn').setAttribute('aria-label', (mode === 'solo' ? 'Shuffle the canvas. Now: ' : 'Shuffle your vote. Now: ') + TH.label);",
        "$('cvName').textContent = (mode === 'solo' ? '' : 'Your vote \\u00b7 ') + pickLabel(); $('shuffleBtn').setAttribute('aria-label', (mode === 'solo' ? 'Shuffle the canvas. Now: ' : 'Shuffle your vote. Now: ') + pickLabel());")
    rep("'<b>Your canvas:</b> ' + escAttr(TH.label) + '. Solo plays", "'<b>Your canvas:</b> ' + escAttr(pickLabel()) + '. Solo plays")
    rep("function renderStages() {\n", "// the pick's name (the canvas behind the menu can lag behind it while you browse the paintings)\nconst pickLabel = () => { const t = STAGE_THEMES[stageSel]; return t && THEME_BY[t[0]] ? THEME_BY[t[0]].label : stageSel === 'season' ? SEASON.name : TH.label; };\nfunction renderStages() {\n")
    rep("  menuPage = 'worlds'; menu.dataset.page = 'worlds'; $('mHome').hidden = true; $('mWorld').hidden = false;\n",
        "  menuPage = 'worlds'; menu.dataset.page = 'worlds'; $('mHome').hidden = true; $('mWorld').hidden = false; for (const im of $('mWorld').querySelectorAll('img.art')) if (im.decode) im.decode().catch(() => {});\n")
    rep("  renderWorlds(); if (typeof renderLobbyUI === 'function' && $('lobbyStage')) renderLobbyUI();\n}", "  renderWorlds(); if (typeof renderLobbyUI === 'function' && $('lobbyStage') && menuPage !== 'worlds') renderLobbyUI(); // (the lobby's card catches up when you leave the paintings)\n}")
    rep("  if (worldDirty) { worldDirty = false; if (GEN.key !== mapKey()) worldBuild(); } // (the pick's canvas, built now that it shows)", "  if (worldDirty) { worldDirty = false; if (GEN.key !== mapKey()) worldBuild(); } // (the pick's canvas, built now that it shows)\n  renderLobbyUI();")
    rep(' data-sub="5 canvases unlocked"', '')
    rep("</style>\n\n<div id=\"stage\">",
        "/* v250: the canvas vote page: no count under the title, the title a little lower, and the painting in the middle comes forward quickly */\n"
        ".mworld .whead h2::after{content:none;display:none}\n"
        ".mworld .whead{margin-top:clamp(10px,2.6vh,24px)}\n"
        ".mworld .world{transition:transform .2s var(--eo),opacity .18s,filter .18s;will-change:transform}\n"
        ".mworld .world::after{transition:opacity .2s}\n"
        "</style>\n\n<div id=\"stage\">")
    return s
