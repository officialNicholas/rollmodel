"""v352: the Whirlwind goes off sooner, Ol' Bloop stops covering his own cards held sideways, and the sideways layouts are tidied.

- The Whirlwind's wind-up is 1.0 s (was 1.3 s). Its lane still locks 0.45 s before it goes, so the tell rivals read is the same. The
  Strokes page says 1 s, and its demo winds up for the same time as a match.
- Ol' Bloop's cards in the lobby ("Look at you, rookie!", "Commissions are open!", "New game modes!") and the lesson's last card: held
  sideways, Ol' Bloop stood over the card at several times his size. The online card's class (.oncard, v306) was the same name as the
  one the coach takes beside a card, so the online card's width (up to 620 px sideways) went to him. The coach's is .atcard now.
  Sideways the card is laid out beside him: he's in the bottom corner on the left, a little bigger, and the card is centred in the
  room to his right, more compact, so the longest card fits on an iPhone SE.
- Held sideways, the rest of the app is tidied (from a sweep of every screen sideways on an iPhone SE, 15, 15 Pro Max and an iPad):
  - the lobby's left column (Locker, Commissions, Strokes) is spaced out: Commissions' countdown no longer runs into the Strokes
    card, and the "+" spot at your left keeps clear of the column;
  - Commissions fits the screen with Back to the studio on it (it was below the bottom edge on an iPhone SE and cut in half on an
    iPhone 15), and Stats does too;
  - the Terms, Privacy and Credits pages keep their Back button on screen, the text scrolling above it;
  - the Time trial board's "New week in" stays inside its card;
  - the login form sits in the middle of its card (it hugged the left);
  - the canvases are centred between the arrows: the picked canvas and the Spooky SZN four (the left arrow covered "The Crypt");
  - the locker's line ("Tap to put it on") clears its window's edge;
  - How to play's cards are laid out picture beside text, so a card and Got it fit on the screen (the cards ran off the bottom);
  - "Commissions" fits its card in the lobby, upright too."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- the Whirlwind: a 1.0 s wind-up (the lock still 0.45 s before the dash)
    s = rep(s, "const WHIRL_WIND = 1.3, WHIRL_DASH = 1.1,", "const WHIRL_WIND = 1.0, WHIRL_DASH = 1.1,") # (v352: 1.3 s felt long; the lock's tell is unchanged)
    s = rep(s, "  whirl: [['Wind-up', '1.3 s'],", "  whirl: [['Wind-up', '1 s'],")
    s = rep(s, "W.k = Math.min(1, W.t / 1.3); W.spin += dt * (8 + 24 * W.k); DA.ip.expr = 'focus'; sgFace(A, Math.atan2(s, 0), dt, 6); sgLane(A, Math.min(1, W.t / 1.3), W.t > 0.85);",
               "W.k = Math.min(1, W.t / WHIRL_WIND); W.spin += dt * (8 + 24 * W.k); DA.ip.expr = 'focus'; sgFace(A, Math.atan2(s, 0), dt, 6); sgLane(A, W.k, W.t > WHIRL_WIND - WHIRL_LOCK);")
    s = rep(s, "        if (W.t >= 1.3) { W.ph = 'dash'; W.t = 0; W.lx = sgLX(A); W.lz = sgLZ(A); } }",
               "        if (W.t >= WHIRL_WIND) { W.ph = 'dash'; W.t = 0; W.lx = sgLX(A); W.lz = sgLZ(A); } } // (v352: the match's own wind-up)")

    # ---- Ol' Bloop beside his card: his own class name (the online card's .oncard sized him), and the card laid out beside him sideways
    s = rep(s, "if (coachEl.classList.contains('oncard') !== !!top) coachEl.classList.toggle('oncard', !!top);",
               "if (coachEl.classList.contains('atcard') !== !!top) coachEl.classList.toggle('atcard', !!top); /* (v352: not .oncard, the online card's) */")
    s = rep(s, ".coachpop.oncard{z-index:63}", ".coachpop.atcard{z-index:63}")
    s = rep(s, "@media (max-height:520px) and (min-aspect-ratio:1/1){.coachpop{width:clamp(104px,32vh,168px)}}",
               "@media (max-height:520px) and (min-aspect-ratio:1/1){.coachpop{width:clamp(104px,32vh,168px)}\n"
               "  /* (v352) sideways, a card of his: him in the corner on the left, a little bigger, and the card compact, centred in the room to his right */\n"
               "  :root{--tgcw:clamp(120px,40vh,184px)}\n"
               "  .coachpop.atcard{width:var(--tgcw)}\n"
               "  .tutgo{padding:12px max(16px,calc(env(safe-area-inset-right,0px) + 10px)) max(12px,env(safe-area-inset-bottom,0px)) calc(env(safe-area-inset-left,0px) + var(--tgcw) + 14px)}\n"
               "  .tutgo.peek{padding:12px 24px}\n"
               "  .tutgo .tgcard{width:min(100%,460px);gap:9px;padding:18px 22px 16px}\n"
               "  .tutgo h2{font-size:clamp(26px,9.5vh,38px)}\n"
               "  .tutgo p{font-size:17px}\n"
               "  .tutgo #tgGo{margin-top:2px}\n"
               "  .tutgo #tgLater{padding:4px 6px}}")

    # ---- the rest of the app held sideways (after every other rule, so these win)
    s = rep(s, "@media (prefers-reduced-motion:reduce){.ptin{animation:none}}\n</style>\n\n<div id=\"stage\">",
               "@media (prefers-reduced-motion:reduce){.ptin{animation:none}}\n"
               "/* (v352) held sideways: the lobby's left column spaced out; Commissions, Stats and the Terms fit the screen with their buttons on it;\n"
               "   the Time trial board's footer inside its card; the login form centred in its card; the canvases centred between the arrows;\n"
               "   the locker's line clear of its window's edge */\n"
               "@media (max-height:520px) and (min-aspect-ratio:1/1){\n"
               "  #lobbyRail{gap:15px}\n"
               "  #commModal,#statsModal,#docModal{padding-top:10px;padding-bottom:10px}\n"
               "  #commModal .card{gap:7px;padding-top:14px;padding-bottom:14px}\n"
               "  #commModal .comms{gap:7px}\n"
               "  #commModal .comm{padding:5px 10px 5px 6px}\n"
               "  #commModal .comm .ring{width:38px;height:38px}\n"
               "  #commModal .comm .ring::after{width:26px;height:26px}\n"
               "  #statsModal .card{gap:9px;padding-top:16px}\n"
               "  #docModal .card{max-height:100%;grid-template-rows:auto minmax(0,1fr) auto}\n"
               "  #docModal .docb{min-height:0}\n"
               "  .ttbody{min-height:min(276px,30vh)}\n"
               "  .acform.acin{justify-self:center;width:100%}\n"
               "  .mworld{padding-right:max(12px,env(safe-area-inset-right))}\n"
               "  .mworld .sgrid{box-sizing:border-box;padding-left:56px;padding-right:56px}\n"
               "  #mLocker.sgp .sgfoot{box-sizing:border-box;padding:0 10px 5px 12px}\n"
               "  #howModal{padding:10px max(16px,env(safe-area-inset-right)) 10px max(16px,env(safe-area-inset-left))}\n"
               "  #howModal .card{width:min(100%,780px);gap:6px}\n"
               "  #howModal .ctitle{font-size:26px;margin-bottom:0}\n"
               "  #howModal .pols{padding:10px 16px 16px}\n"
               "  #howModal .pol{flex-basis:min(62vw,400px);grid-template-columns:36% minmax(0,1fr);grid-template-rows:none;align-items:center;column-gap:12px;padding:10px}\n"
               "  #howModal .pol .pic{aspect-ratio:1/.8}\n"
               "  #howModal .pol p{font-size:12.5px;line-height:1.35}\n"
               "  #howModal .btn.play{min-height:46px}\n"
               "}\n"
               "@media (max-height:520px) and (min-aspect-ratio:1/1) and (max-width:720px){.mworld .sgrid{gap:10px;padding-left:50px;padding-right:50px}.mworld .sgrid .stg b{font-size:12.5px;padding-left:7px;padding-right:7px}} /* (a small phone: \"The Cathedral\" still fits) */\n"
               "/* (v352) Commissions' label fits its card (it ran a little past both sides) */\n"
               "#commBtn{padding-left:1px;padding-right:1px}\n"
               "#commBtn>span:not([class]){font-size:9px;letter-spacing:-.02em}\n"
               "</style>\n\n<div id=\"stage\">")

    # ---- the lobby's "+" spot at your left stays clear of the left column held sideways (it ran into Commissions on small phones)
    s = rep(s, "  for (const [el, s] of [[slotL, -1], [slotR, 1]]) {\n    pbV.set(P.x + pbR.x * s * 1.05, P.y + 0.28, P.z + pbR.z * s * 1.05).project(camera);\n    el.style.left = clamp((pbV.x * 0.5 + 0.5) * viewW, 42, viewW - 42).toFixed(1) + 'px';",
               "  for (const [el, s] of [[slotL, -1], [slotR, 1]]) {\n    pbV.set(P.x + pbR.x * s * 1.05, P.y + 0.28, P.z + pbR.z * s * 1.05).project(camera);\n    el.style.left = clamp((pbV.x * 0.5 + 0.5) * viewW, s < 0 ? PB.slotLo || 42 : 42, viewW - 42).toFixed(1) + 'px';")
    s = rep(s, "PB.top = b - stage.getBoundingClientRect().top; }",
               "PB.top = b - stage.getBoundingClientRect().top; PB.slotLo = slotLo(); }")
    s = rep(s, "// where it floats: over your character's head (and its hat), never up into the top bar or the logo; the spots either side of it\n",
               "// (v352) sideways, where the spot at your left may start: clear of the lobby's left column\n"
               "function slotLo() { if (viewW <= viewH) return 42; const sl = stage.getBoundingClientRect().left; let r = 0;\n"
               "  for (const e of $('lobbyRail').children) { if (e.hidden || e.offsetParent === null) continue; const q = e.getBoundingClientRect(); if (q.width > 0) r = Math.max(r, q.right - sl); }\n"
               "  return Math.max(42, r + 10 + (slotL.offsetWidth || 64) / 2); }\n"
               "// where it floats: over your character's head (and its hat), never up into the top bar or the logo; the spots either side of it\n")
    return s
