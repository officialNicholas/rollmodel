"""v325: the Strokes page loses Test, and Info moves up beside the main button.

- Test (the button under the panel that replayed the demo with captions) is gone, with the mode it opened: its captions, the
  layout that hid the panel for it, and its timings.
- Info now sits beside the main button (Equip, Craft, the rank it opens at, or the bench's Skip), the same height and slant, in
  the dark of the old pill. Upright, the row under the panel is gone and the stroke's window takes the room; sideways, the band
  keeps just Back and the tabs.
The demo plays as before (and stays still with reduced motion, as it did without Test)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def cut_lines(s, start, last_start):
    # remove from the line starting with `start` through the end of the line starting with `last_start`
    a = s.index(start); b = s.index(last_start, a); b = s.index("\n", b) + 1
    return s[:a] + s[b:]

def apply(s):
    # ---- the page: no caption over the demo, no row under the panel; Info beside the main button
    s = rep(s, '<p class="sgcap" id="sgCap" aria-live="polite"></p>', '')
    s = rep(s, '<button class="sgdo" id="sgDo" type="button">Equip</button></div>', '<button class="sgdo" id="sgDo" type="button">Equip</button><button class="sgib" id="sgInfo" type="button" aria-haspopup="dialog"><span>Info</span></button></div>')
    s = rep(s, '      <div class="sgpills"><button class="sgpill" id="sgInfo" type="button" aria-haspopup="dialog"><span>Info</span></button><button class="sgpill" id="sgTest" type="button"><span>Test</span></button></div>\n', '')
    # ---- the look
    s = rep(s, "   Upright it's a column: the stroke (and its demo) up top, the tabs on the band, the panel, Info and Test */", "   Upright it's a column: the stroke (and its demo) up top, the tabs on the band, the panel (v325: Info beside the stroke's button) */")
    s = rep(s, "--bk:56px;--tabw:104px;--pillh:40px;--panh:min(31vh,262px);", "--bk:56px;--tabw:104px;--panh:min(31vh,262px);")
    s = rep(s, "#mStrokes.sgp.sgnoted:not(.sgtest) .sgrot{bottom:100px}", "#mStrokes.sgp.sgnoted .sgrot{bottom:100px}")
    s = cut_lines(s, "#mStrokes.sgp .sgcap{position:absolute;", "#mStrokes.sgp.sgtest .sgcap.on{opacity:1}")
    s = rep(s, "#mStrokes.sgp .sgtab:focus-visible,#mStrokes.sgp .sgcard:focus-visible,#mStrokes.sgp .sgpill:focus-visible,", "#mStrokes.sgp .sgtab:focus-visible,#mStrokes.sgp .sgcard:focus-visible,#mStrokes.sgp .sgib:focus-visible,")
    s = cut_lines(s, "#mStrokes.sgp .sgpills{position:relative;", "#mStrokes.sgp.sgtest #sgTest{")
    s = cut_lines(s, "/* (Test: the demo bigger, the panel and the tabs out of its way) */", "#mStrokes.sgp.sgtest .sgrot{bottom:12px}")
    s = rep(s, "   back at its left and Info and Test at its right */", "   back at its left */")
    s = rep(s, "--tabw:clamp(84px,12vw,116px);--pillh:clamp(32px,9.5vh,40px);--panw:55%;", "--tabw:clamp(84px,12vw,116px);--panw:55%;")
    s = cut_lines(s, "  #mStrokes.sgp .sgpills{position:absolute;", "  #mStrokes.sgp .sgpill{min-width:")
    s = rep(s, "  #mStrokes.sgp.sgnoted:not(.sgtest) .sgrot{bottom:72px}", "  #mStrokes.sgp.sgnoted .sgrot{bottom:72px}")
    s = cut_lines(s, "  #mStrokes.sgp.sgtest .sgshow{", "  #mStrokes.sgp.sgtest .sgink{display:none}")
    # Info: a dark button beside the main one, its height and slant
    s = rep(s, "#mStrokes.sgp .sgdo[hidden],#mStrokes.sgp .sgskip[hidden],#mStrokes.sgp .sgtimer[hidden]{display:none}\n",
        "#mStrokes.sgp .sgdo[hidden],#mStrokes.sgp .sgskip[hidden],#mStrokes.sgp .sgtimer[hidden]{display:none}\n"
        "#mStrokes.sgp .sgib{appearance:none;position:relative;flex:none;min-width:72px;height:38px;margin:0;padding:0 15px;border:0;border-radius:10px;background:linear-gradient(#4A4A52,#34343B);color:#fff;font:400 16px/1 var(--font-display);letter-spacing:.01em;transform:skewX(-12deg);box-shadow:0 0 0 2.5px var(--ink0),0 4px 0 var(--ink0);cursor:pointer;-webkit-tap-highlight-color:transparent}\n"
        "#mStrokes.sgp .sgib>span{display:inline-block;transform:skewX(12deg)}\n"
        "#mStrokes.sgp .sgib:active{transform:skewX(-12deg) translateY(3px);box-shadow:0 0 0 2.5px var(--ink0),0 1px 0 var(--ink0)}\n"
        "@media (max-width:379px){#mStrokes.sgp .sgtimer .sgtbar{display:none}} /* (a narrow phone: the bench's row fits with Info; the card keeps its bar) */\n")
    # ---- the code: Test's button, mode, captions and timings go
    s = rep(s, "$('sgTest').addEventListener('click', () => { AU.init(); AU.ui(); if (SGD.test) sgTestEnd(); else sgTestStart(); });\n", "")
    s = rep(s, "  $('sgTest').hidden = cat === 'skill'; SGD.rectDirty = true;\n", "  SGD.rectDirty = true;\n")
    s = rep(s, "  if (was !== cat) { if (SGD.test) sgTestEnd(true); if (!quiet) {", "  if (was !== cat) { if (!quiet) {")
    s = rep(s, "if (!stDef(id) || !strokesOpen()) return; if (SGD.test) sgTestEnd(true);", "if (!stDef(id) || !strokesOpen()) return;")
    s = rep(s, "closeStPop(true); sgTestEnd(true); sgStop();", "closeStPop(true); sgStop();")
    s = rep(s, "if (SGD.test) { AU.ui(); return sgTestEnd(); } ", "")
    s = rep(s, "if (stPopId) closeStPop(true); if (SGD.test) sgTestEnd(true); if (!$('mStrokes').classList.contains('sglearn'))", "if (stPopId) closeStPop(true); if (!$('mStrokes').classList.contains('sglearn'))")
    s = cut_lines(s, "// the steps Test captions, from each transform's own lines\nconst SG_CAP = {", "const SG_CAP = {")
    s = rep(s, "  SGD.capI = -1; sgCap();\n", "")
    s = rep(s, "  if (SGD.test) sgCap();\n", "")
    s = cut_lines(s, "// the captions Test shows, a line of the transform's own for each step\nfunction sgCap() {", "function sgCap() {")
    s = rep(s, "  if (!reduceMotion || SGD.test) sgStep(dt);", "  if (!reduceMotion) sgStep(dt);")
    s = cut_lines(s, "function sgTestStart() {", "function sgTestEnd(quiet) {")
    s = rep(s, "yawTo: null, drag: null, test: false, rectDirty: true,", "yawTo: null, drag: null, rectDirty: true,")
    # the turn-the-view button sits just above the words and buttons under the demo, however tall they run (a two-line line, a note)
    s = rep(s, "SGD.insB = ft.height > 0 ? clamp(r.bottom - ft.top + 2, 0, h * 0.4) : 0;", "SGD.insB = ft.height > 0 ? clamp(r.bottom - ft.top + 2, 0, h * 0.4) : 0; $('sgRot').style.bottom = ft.height > 0 ? Math.round(r.bottom - ft.top + 8) + 'px' : '';")
    for k in ('sgTest', 'SGD.test', 'sgCap', 'SG_CAP', 'sgtest', 'sgpill', '--pillh'):
        assert k not in s, k
    return s
