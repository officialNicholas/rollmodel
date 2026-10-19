"""v367: ready for iPhone Duo (and any screen that changes size or shape while the game runs).

- A near-square screen (long side under 1.6 times the short one: iPhone Duo open or folded, an iPad, a square window) suits either
  way round, so the game never asks which way the player holds it (the chooser at the first launch, the Screen row in Settings) and
  never asks for a turn. It takes whatever shape it's given; the iPhone shell lets such a screen turn freely too. Phone-shaped
  screens keep the choice as before.
- A match draws at most about 1.2 million pixels a frame on a phone. iPhone Duo's open screen holds half as much again as the biggest
  iPhone's, at the same sharpness, with a phone's chip: it now draws a little softer (1.37x its points rather than 1.6x) instead of
  running hotter. Every iPhone today is under the line and unchanged; iPads are left as they were.
- The screen changing shape mid-match (iPhone Duo folded or opened, the phone turned, a window resized by a lot) pauses the match, so the
  player gets a moment to settle their grip, and the match's resolution is worked out again for the new size.
- The season's canvases (Spooky SZN) sit in one row on a landscape screen between a phone's height and a big tablet's (iPhone Duo
  open, a small tablet): 2 x 2 they pushed Play off the bottom of the screen.
- After a match, on a wide screen under about 850 high (iPhone Duo open, a small tablet, a laptop), the results beside the painting
  showed Rematch cut off and no Same canvas or Menu: the panel was held to the lower half of the screen and the rest only scrolled
  into view. It now takes the height it needs, centred.
- iPhone Duo keeps its camera (and status bar) along one side of the screen, held upright too, so its safe area is lopsided. The game
  kept clear of side insets only on a phone held sideways; now the match's controls, the canvas vote page, Settings' Done and the
  lobby's friend spots keep clear of them in every layout. A phone held upright has no side insets, so nothing moves there."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # Settings: no Screen row on a roomy screen (the rows reflow: Sound, Music and Visuals, then Turning beside the links when wide)
    s = rep(s, "#setModal .sopt{gap:5px}",
               "#setModal .sopt{gap:5px}\n"
               "html.roomy #setModal .sopt:has(#orientPick){display:none}")

    # the season's canvases (Spooky SZN) on a landscape screen too short for its 2 x 2: one row, clear of the arrows
    s = rep(s, ".hud.lesson .top .score{visibility:hidden}\n</style>",
               ".hud.lesson .top .score{visibility:hidden}\n"
               "/* (v367) a landscape screen too short for the season's canvases 2 x 2 (iPhone Duo open, a small tablet): the four in one row, so Play\n"
               "   stays on the screen */\n"
               "@media (min-aspect-ratio:1/1) and (min-height:521px) and (max-height:760px){.mworld .sgrid{grid-template-columns:repeat(4,minmax(0,1fr));width:min(calc(100% - 120px),860px);gap:16px}}\n"
               "/* (v367) the results beside the painting on a wide screen take the height they need, centred: they were held to the lower half of the\n"
               "   screen (a tablet's bottom edge still set), so on anything under about 850 high (iPhone Duo open, a small tablet, a laptop) Same\n"
               "   canvas and Menu sat out of sight below Rematch */\n"
               "@media (min-width:860px) and (min-aspect-ratio:1/1) and (min-height:521px){#end{bottom:auto}}\n"
               "/* (v367) iPhone Duo keeps its camera (and its status bar) along one side of the screen, upright too, so its safe area is lopsided:\n"
               "   the match's controls, the canvas vote and Settings' Done keep clear of the side insets in every layout, not only on a phone held\n"
               "   sideways (a phone held upright has none, so nothing moves there) */\n"
               "@media not ((max-height:520px) and (min-aspect-ratio:1/1)){\n"
               "  .hud{padding-left:max(14px,calc(env(safe-area-inset-left) + 8px));padding-right:max(14px,calc(env(safe-area-inset-right) + 8px))}\n"
               "  .mworld{padding-left:env(safe-area-inset-left);padding-right:env(safe-area-inset-right)}\n"
               "  #setModal #setDone{right:max(16px,calc(env(safe-area-inset-right) + 12px))}\n"
               "}\n"
               "</style>")

    # the lobby's friend spots and the bar over your head are placed by hand: clear of the side insets too
    s = rep(s, "// (v352) sideways, where the spot at your left may start: clear of the lobby's left column\nfunction slotLo() {",
               "// (v367) the screen's side insets (iPhone Duo keeps its camera along one side, upright too), for what's placed by hand\n"
               "const SAI = { l: 0, r: 0 };\n"
               "{ const pr = document.createElement('div'); pr.style.cssText = 'position:fixed;left:0;top:0;width:0;height:0;visibility:hidden;pointer-events:none;padding-left:env(safe-area-inset-left,0px);padding-right:env(safe-area-inset-right,0px)'; document.body.appendChild(pr);\n"
               "  const read = () => { const c = getComputedStyle(pr); SAI.l = parseFloat(c.paddingLeft) || 0; SAI.r = parseFloat(c.paddingRight) || 0; }; read(); addEventListener('resize', () => setTimeout(read, 0)); }\n"
               "// (v352) sideways, where the spot at your left may start: clear of the lobby's left column\nfunction slotLo() {")
    s = rep(s, "el.style.left = clamp((pbV.x * 0.5 + 0.5) * viewW, s < 0 ? PB.slotLo || 42 : 42, viewW - 42).toFixed(1) + 'px';",
               "el.style.left = clamp((pbV.x * 0.5 + 0.5) * viewW, Math.max(s < 0 ? PB.slotLo || 42 : 42, 42 + SAI.l), viewW - 42 - SAI.r).toFixed(1) + 'px';")
    s = rep(s, "const bw = pbar.offsetWidth || 216, bh = pbar.offsetHeight || 54; let lo = 10, hi = viewW - 10;",
               "const bw = pbar.offsetWidth || 216, bh = pbar.offsetHeight || 54; let lo = 10 + SAI.l, hi = viewW - 10 - SAI.r;")

    s = rep(s, "const touchy = () => matchMedia('(pointer: coarse)').matches;",
               "const touchy = () => matchMedia('(pointer: coarse)').matches;\n"
               "// (v367) a near-square screen (iPhone Duo open or folded, an iPad, a square window) suits either way round: the game never asks which\n"
               "// way it's held, or for a turn, and takes whatever shape it's given (the iPhone shell lets it turn freely as well)\n"
               "const roomy = () => { const a = innerWidth, b = innerHeight, k = Math.min(a, b); return k > 0 && Math.max(a, b) / k < 1.6; };\n"
               "{ const mark = () => document.documentElement.classList.toggle('roomy', roomy()); mark(); addEventListener('resize', mark); }")
    s = rep(s, "if (!want || !touchy() || !$('orient').hidden || window.__noRotate) { el.hidden = true; return; }",
               "if (!want || !touchy() || !$('orient').hidden || window.__noRotate || roomy()) { el.hidden = true; return; }")
    s = rep(s, "function openOrient() { const el = $('orient');",
               "function openOrient() { if (roomy()) return; const el = $('orient');")

    # the pixel budget
    s = rep(s, "const qWarm = () => !!(NATIVE && (NATIVE.thermal || 0) >= 1), qMatchPR = () => (isShow() ? 1.5 : 1.6) * (qWarm() ? 0.9 : 1);",
               "// (v367) and at most about 1.2 million pixels a frame on a phone: iPhone Duo's open screen holds half as much again as the biggest\n"
               "// iPhone's at the same sharpness, with a phone's chip, so it draws a little softer instead of running hotter (iPads as they were)\n"
               "const Q_PIX = 1.2e6;\n"
               "const qWarm = () => !!(NATIVE && (NATIVE.thermal || 0) >= 1), qMatchPR = () => Math.min((isShow() ? 1.5 : 1.6) * (qWarm() ? 0.9 : 1), window.__noRotate ? 9 : Math.sqrt(Q_PIX / Math.max(1, viewW * viewH)));")

    # a new shape mid-match: pause, and the match's resolution again for the new size
    s = rep(s, "window.addEventListener('resize', () => setTimeout(checkRotate, 0));",
               "window.addEventListener('resize', () => setTimeout(checkRotate, 0));\n"
               "// (v367) the screen changed shape mid-match (iPhone Duo folded or opened, the phone turned, a window resized by a lot): the match pauses so\n"
               "// the player can settle their grip, and its resolution is worked out again for the new size\n"
               "{ let w0 = innerWidth, h0 = innerHeight;\n"
               "  addEventListener('resize', () => { const w = innerWidth, h = innerHeight, turned = (w > h) !== (w0 > h0), big = Math.abs(w * h - w0 * h0) > 0.25 * w0 * h0; w0 = w; h0 = h;\n"
               "    if (state === 'play' && !NM && (turned || big)) pause();\n"
               "    if (qInMatch && MOBILE) setQ(qLvl); }); }")
    return s
