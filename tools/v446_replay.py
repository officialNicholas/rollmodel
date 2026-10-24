"""v446: no Rings card, each lesson clip starts at its first frame, and the tutorial can be replayed from Settings.

- The rings have no card any more (the user: "remove rings as a gif tip"): after Your steering, the three gold rings simply come up
  ahead of you, the pointer showing the way to each. The row of dots on the cards counts six lessons now. Its clip is gone from art/.
- A card's clip always plays from its first frame. An animated image is one picture shared by every place it's shown, so a clip that
  had already been fetched (they're all fetched as the lesson starts) could come up partway through its loop. Each one is now kept as
  its own data and handed to the card under a new address every time it's shown, which a browser treats as a new picture, played
  from the start; the address is let go as the card closes.
- Settings has Replay tutorial (beside How to play, Terms and Privacy; not during a match): it closes Settings and starts the training
  match straight away. A replay hands out no lesson dabs (no "+5"), and afterwards you're back where you were (no second-match tips)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

TV = """const TV_SRC = { steer: 'art/l_steer.webp', jump: 'art/l_jump.webp', sling: 'art/l_sling.webp', basin: 'art/l_basin.webp', pound: 'art/l_pound.webp', dodge: 'art/l_dodge.webp' };
const TV = {}; for (const k in TV_SRC) TV[k] = '<img class="tvclip" data-k="' + k + '" alt="">'; // (v446: the address is set as the card shows)
// (v446) each clip kept as its own data, so every showing gets a fresh address and plays from its first frame
const LSN_BLOB = {};
function lsnFetch() { for (const k in TV_SRC) { if (LSN_BLOB[k]) continue; try { fetch(TV_SRC[k]).then(r => r.ok ? r.blob() : null).then(b => { if (b) LSN_BLOB[k] = b; }).catch(() => {}); } catch (e) {} } }
function lsnClips(on) { for (const im of lsnEl.querySelectorAll('img.tvclip')) {
    if (!on) { if (im.dataset.u) { try { URL.revokeObjectURL(im.dataset.u); } catch (e) {} delete im.dataset.u; } continue; }
    const k = im.dataset.k, b = LSN_BLOB[k]; let u = null; if (b) try { u = URL.createObjectURL(b); } catch (e) {}
    if (u) { im.dataset.u = u; im.src = u; } else im.src = TV_SRC[k]; } }
"""

ROW = '<button class="sbtn" id="tutAgain" type="button"><span>Replay tutorial</span></button>'

JS = r"""
// (v446) Replay tutorial, from Settings in the lobby: the training match again, straight away. No lesson dabs the second time round,
// and after it you're back where you were
$('tutAgain').addEventListener('click', () => { AU.init(); AU.ui(); if (state !== 'menu' || setInPlay || building) return;
  store.tut.replay = 1; delete store.tut.skipped; tutSet('match'); save(); closeSettings();
  setTimeout(() => { if (state === 'menu' && !building && tutMatchDue()) start(); }, 260); });
"""

def apply(s):
    # ---- no Rings card (the rings themselves stay)
    s = rep(s, "const LSN_ORDER = ['move', 'tune', 'rings', 'sling', 'basin', 'pound', 'dodge'];", "const LSN_ORDER = ['move', 'tune', 'sling', 'basin', 'pound', 'dodge']; /* (v446: no Rings card) */")
    s = rep(s, "  rings: { t: 'Rings', p: [['rings', 'Steer through 3 rings', 'Steer through 3 rings']] },\n", "")
    s = rep(s, "{ id: 'rings', max: 50, enter() { tutHide(); tut.ringsOn = false; lsnDue('rings'); },", "{ id: 'rings', max: 50, enter() { tutHide(); tut.ringsOn = false; tut.ghostT = 0; },")
    # ---- the clips: their own data, a fresh address each showing
    a = s.index("const TV = { // (v445)"); b = s.index("const LSN_TUNE = ")
    s = s[:a] + TV + s[b:]
    s = rep(s, "for (const k in TV) { const im = new Image(); im.src = TV[k].match(/src=\"([^\"]+)\"/)[1]; } /* (v445: the clips) */", "lsnFetch(); /* (v446: the clips, as data) */")
    s = rep(s, "  if (k === 'basin') { const w = vis.querySelector('.tll'), pw = potWord();", "  lsnClips(true); /* (v446: from their first frame) */\n  if (k === 'basin') { const w = vis.querySelector('.tll'), pw = potWord();")
    s = rep(s, "lsnEl.classList.remove('on'); lsnEl.hidden = true; lsnEl.querySelector('.tlvis').innerHTML = ''; AU.init(); AU.pop();",
               "lsnEl.classList.remove('on'); lsnEl.hidden = true; lsnClips(false); lsnEl.querySelector('.tlvis').innerHTML = ''; AU.init(); AU.pop();")
    s = rep(s, "lsnEl.hidden = true; lsnEl.classList.remove('on'); lsnEl.querySelector('.tlvis').innerHTML = '';", "lsnEl.hidden = true; lsnEl.classList.remove('on'); lsnClips(false); lsnEl.querySelector('.tlvis').innerHTML = '';")
    # ---- Replay tutorial in Settings (lobby only)
    s = rep(s, '<div class="sbtns four"><button class="sbtn" id="howOpen"', '<div class="sbtns four">' + ROW + '<button class="sbtn" id="howOpen"')
    s = rep(s, "$('resetBtn').hidden = on; if (on) $('delAcBtn').hidden = true; else delPaint();", "$('resetBtn').hidden = on; $('tutAgain').hidden = on; if (on) $('delAcBtn').hidden = true; else delPaint();")
    i = s.rfind("</style>"); s = s[:i] + "\n/* (v446) Settings' help row: Replay tutorial, How to play, Terms, Privacy (three when Replay is hidden in a match) */\n#setModal .sbtns.four{grid-template-columns:repeat(4,minmax(0,1fr))}\n#setModal .sbtns.four:has(#tutAgain[hidden]){grid-template-columns:repeat(3,minmax(0,1fr))}\n" + s[i:]
    a = "$('setBtn').addEventListener('click', uiClick(openSettings));"
    s = rep(s, a, a + JS)
    # a replay: no lesson dabs, no "+5", and back to done afterwards (skipping it too)
    s = rep(s, "const bonus = tut.bonus || 0; if (bonus) {", "const bonus = store.tut.replay ? 0 : (tut.bonus || 0); if (bonus) {")
    s = rep(s, "endInfo.lesson = true; tutSet('match2'); save(); tutWinDue = true; return;", "endInfo.lesson = true; tutSet(store.tut.replay ? 'done' : 'match2'); delete store.tut.replay; save(); tutWinDue = true; return;")
    s = rep(s, "if (sce && state === 'play') { const r0 = stage.getBoundingClientRect(), r = sce.getBoundingClientRect(), pl = document.createElement('p'); pl.className = 'tutplus';",
               "if (sce && state === 'play' && !store.tut.replay) { const r0 = stage.getBoundingClientRect(), r = sce.getBoundingClientRect(), pl = document.createElement('p'); pl.className = 'tutplus';")
    s = rep(s, "  store.tut.skipped = 1; store.tut.m3 = 2; store.tut.comms = 1;", "  delete store.tut.replay; store.tut.skipped = 1; store.tut.m3 = 2; store.tut.comms = 1;")
    return s
