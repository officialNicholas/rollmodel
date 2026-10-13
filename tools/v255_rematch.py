"""v255: Rematch (New canvas) on the results goes to the canvas vote for the same event first, where you can pick another canvas or
change how hard the CPUs are; Play goes on from there as always (the fight card, then everyone's votes). Back from it goes to the
events. The onboarding keeps its own way on. And the fight card's top labels keep clear of whatever sits over the page's top edge (a
phone's notch, or the Claude app's own bar with its close button), the way the game's other screens already do."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def apply(s):
    s = rep(s, "$('endBtn').addEventListener('click', uiClick(start));", "$('endBtn').addEventListener('click', uiClick(rematchVote));")
    s = rep(s, "const toMenu = () => irisClose(() => { showMenu(); camSnap = true; irisOpen(); });\n",
               "const toMenu = () => irisClose(() => { showMenu(); camSnap = true; irisOpen(); });\n"
               "// (v255) Rematch, new canvas: the canvas vote for the same event first (another canvas, the CPUs easier or harder), then Play as\n"
               "// always; its back button goes to the events. The onboarding's own matches go straight on, as before.\n"
               "function rematchVote() { if (building || irisBusy) return; if (tutPh() !== 'done') return start(); irisClose(() => { showMenu(); camSnap = true; openWorlds(); evFrom = true; irisOpen(); }); }\n")
    s = rep(s, "\n</style>\n\n<div id=\"stage\">",
               "\n/* (v255) the fight card's labels along the top edge keep clear of the notch or the app's bar over it */\n"
               ".vsx .vsrow:not(.rows) .vhead{padding-top:calc(8px + env(safe-area-inset-top,0px))}\n"
               ".vsrow.rows .vcol:first-child .vhead{padding-top:calc(9px + env(safe-area-inset-top,0px))}\n</style>\n\n<div id=\"stage\">")
    return s
