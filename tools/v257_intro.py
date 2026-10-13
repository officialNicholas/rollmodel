"""v257: the first launch. A brand-new player (no name, no matches, the lesson still ahead) gets a scene of its own before the lobby: a
barrel of paint rocks, tips and pours; two eyes come up out of the puddle and look about; you pick their colour and style, then the
paint's colour (all live, on the game's own character); it climbs out, jumps clear and shakes the paint off; you name it; it winks and
jumps away, and the iris opens on the lobby with it jumping in. Then the lesson starts as it always has. The music is written on the
theme (its key, tempo, chords and main melody) and builds a layer with each pick, then a sting hands over to the menu song in time, at
its eighth bar. window.__introNow = true before load forces it. The JS and CSS live beside this file (v257_intro.js, v257_intro.css,
v257_intro_au.js); the music in music/intro_*.mp3, the effects in sfx/intro_fx.mp3."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def apply(s):
    rd = lambda n: open(os.path.join(HERE, n)).read()
    js, css, au = rd('v257_intro.js'), rd('v257_intro.css'), rd('v257_intro_au.js')
    # ---- the stylesheet
    s = rep(s, "\n</style>\n\n<div id=\"stage\">", "\n" + css + "</style>\n\n<div id=\"stage\">")
    # ---- the music: the intro's stems, its effects and the hand-over, inside the audio engine
    s = rep(s, "    _trk(k) { return k ? !!(TRK[k] && TRK[k].buf) : trk && trk.key; },\n", "    _trk(k) { return k ? !!(TRK[k] && TRK[k].buf) : trk && trk.key; },\n" + au)
    # ---- the intro itself, once everything it uses is in place (and before the lobby is first shown)
    s = rep(s, "applyOrient(); showMenu();\nawait bootStep(0.82, 0.93, 'Hanging the show');", js + "applyOrient(); showMenu();\nawait bootStep(0.82, 0.93, 'Hanging the show');")
    # ---- the lobby's song waits while the intro runs (it comes in on the beat after the sting)
    s = rep(s, "resetRun(); decorate(); renderStages(); AU.music('menu'); menuPose();", "resetRun(); decorate(); renderStages(); if (!(FL && FL.hush)) AU.music('menu'); menuPose();")
    # ---- at the end of loading: the intro for a new player (it asks for the orientation itself, first), the chooser as before otherwise
    s = rep(s, "if (!store.orient) { if (bootHold) {", "if (FL && FL.due) FL.boot(); else if (!store.orient) { if (bootHold) {")
    # ---- each frame: while it runs, the intro draws instead of the lobby; after it, it jumps in
    s = rep(s, "  if ((AXOC.S.ready || SLIME.S.ready) && !VP.slime && booted && state === 'menu' && !lookOpen && !irisBusy) { attachSlimes(); queueWarm(); }\n",
               "  if ((AXOC.S.ready || SLIME.S.ready) && !VP.slime && booted && state === 'menu' && !lookOpen && !irisBusy) { attachSlimes(); queueWarm(); }\n  if (FL && FL.frame(rdt)) { lastCpu = (performance.now() - cpu0) / 1000; return; } // (v257: the first launch's own scene)\n")
    s = rep(s, "  visuals(dt, rdt); flushTrail(); pbarTick(rdt); lockerTick(); dipTick(rdt);\n", "  visuals(dt, rdt); flushTrail(); pbarTick(rdt); lockerTick(); dipTick(rdt); if (FL && FL.jin) FL.after(rdt);\n")
    s = rep(s, "  const isc = D === P && lookIntro && state === 'menu' ? V.introSc : 1;\n", "  if (D === P && state === 'menu' && FL && FL.jin) { const q = FL.jin; hop = q.hop; sq = q.sq; rise = q.rise; spinY = 0; } // (v257: jumping in after the intro)\n  const isc = D === P && lookIntro && state === 'menu' ? V.introSc : 1;\n")
    # ---- the coach waits until it has landed
    s = rep(s, "  if (bootHold || !booted || !tutBootEl.classList.contains('gone')", "  if ((FL && FL.busy()) || bootHold || !booted || !tutBootEl.classList.contains('gone')")
    return s
