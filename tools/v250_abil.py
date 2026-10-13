# v250 Strokes lesson (the first time the abilities page shows), applied by ui190_patch.py: it opened with a lobby tip flashing for a
# quarter second before the page, then Ol' Bloop's line jumped to a new place at every step (over the title, mid-page over the cards,
# back up), the ring and the hand jumping with it. Now the page opens straight from his card, and on the page his line sits still at its
# foot for the whole lesson, above where the page's own notes pop up; only the hand and the ring move to what each step is about.
def apply(s):
    def rep(old, new, count=1):
        nonlocal s
        c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
        s = s.replace(old, new)
    rep("function tutShow(text, at, key, call, nodim, side, loose) {", "function tutShow(text, at, key, call, nodim, side, loose, low) {")
    rep("tutTip = { text, at: at || null, key, call: !!call, nodim: !!(nodim || loose), side: side || null, loose: !!loose };",
        "tutTip = { text, at: at || null, key, call: !!call, nodim: !!(nodim || loose), side: side || null, loose: !!loose, low: !!low }; /* (low: down at the page's foot, still) */")
    rep("  if (state === 'play' || tutTip.loose) { // (in a match, or a loose tip: up top, the hand loose over the control, no dim)",
        "  if (tutTip.low && state !== 'play') { // (a page with room at its foot: the line sits there, still, step after step; the hand and the ring go to what it's about)\n"
        "    if (tutEl.dataset.pos !== 'low') { tutEl.dataset.pos = 'low'; tutEl.style.cssText = ''; } if (tutEl.dataset.cside !== 'l') tutEl.dataset.cside = 'l';\n"
        "    const t = (viewH - tutEl.offsetHeight - Math.max(14, parseFloat(getComputedStyle(stage).paddingBottom) || 0) - 58).toFixed(0) + 'px'; if (tutEl.style.top !== t) tutEl.style.top = t; // (clear of the page's own notes at the very bottom)\n"
        "    const blk = block && !tutTip.nodim; if (tutDim.classList.contains('block') !== blk) tutDim.classList.toggle('block', blk); for (const k of ['noblur', 'clear']) if (!tutDim.classList.contains(k)) tutDim.classList.add(k);\n"
        "    const vis = el && !el.closest('[hidden]') && el.getClientRects().length > 0, r = vis ? el.getBoundingClientRect() : null;\n"
        "    if (r) tutWindow(r.left - r0.left - 10, r.top - r0.top - 10, r.width + 20, r.height + 20); else tutWindow(viewW / 2, viewH / 2, 0, 0);\n"
        "    tutHandAt(r ? el : null, r0); return;\n"
        "  }\n"
        "  if (state === 'play' || tutTip.loose) { // (in a match, or a loose tip: up top, the hand loose over the control, no dim)")
    rep("tutShow('Crafting takes 20 minutes. Tap Skip, this one’s on me', 'stSkip', 'sSkip');", "tutShow('Crafting takes 20 minutes. Tap Skip, this one’s on me', 'stSkip', 'sSkip', false, false, null, false, true);")
    rep("tutShow('Your Special Stroke is what the orb gives you. The Giant is yours now: tap it to craft it', giant, 'sGiant');", "tutShow('Your Special Stroke is what the orb gives you. The Giant is yours now: tap it to craft it', giant, 'sGiant', false, false, null, false, true);")
    rep("tutShow('It’s ready! Tap the Giant to make it your special stroke', giant, 'sEquip');", "tutShow('It’s ready! Tap the Giant to make it your special stroke', giant, 'sEquip', false, false, null, false, true);")
    rep("tutShow('Giant it is! Grab the orb in a match and go big. Your Skill is below: Swim faster is on', null, 'sDone', false, true, null, true);", "tutShow('Giant it is! Grab the orb in a match and go big. Your Skill is below: Swim faster is on', null, 'sDone', false, true, null, false, true);")
    rep("store.tut.strokes = 'on'; tutSet('strokes'); setTimeout(() => openStrokes(), 250); }", "store.tut.strokes = 'on'; tutSet('strokes'); openStrokes(); } /* (straight onto the page: no lobby tip flashing up first) */")
    rep("/* v250: the canvas vote page:", "/* v250: the Strokes lesson's line, still at the page's foot */\n.tut[data-pos=\"low\"]{left:50%;transform:translateX(-50%);max-width:min(92vw,460px)}\n/* v250: the canvas vote page:")
    return s
