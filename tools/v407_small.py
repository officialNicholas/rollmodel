"""v407: three asks.
- The hard paint labels go (the user: "Remove the hard paint label, and the paint softens labels"): no "Hard paint 5s" chip after a
  heat wave, and no "Hard paint softens" / "Hard paint slows you until the rain." under the weather banners.
- Turning the phone on the main menu (the user: "if I'm in portrait, I turn it landscape, ask the player if they would like to switch
  to that orientation instead ... you will need to change it in settings if you are in a match"): the app says which way the phone
  is held ('nativeturn', from its orientation bridge; the screen itself stays locked to the choice), and on the main menu, with
  nothing else open, a card asks "Play wide?" (or "Play upright?"): Switch, or Not now (then not asked again for 20 seconds, or until
  the phone goes back and turns again). Turn back before answering and the card goes by itself. Anywhere else, Settings as before.
- The beep when the music comes back on iOS (after Control Centre, the notification shade, or a trip out of the app): the sound was
  stopped and started again (the app's resume does a suspend and resume, and iOS interrupts the audio for Control Centre) while it was
  playing at full, and iOS can play back the last slice it had already made when it starts again: a short blip of the music. Now the
  game's output goes silent first (for a tenth of a second before any suspend it makes), stays silent while the sound is away, and
  fades back in over a quarter second once the clock is moving again, so whatever slice iOS replays is silence."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

TURN_HTML = '''  <div class="modal" id="turnModal" hidden>
    <div class="card" role="alertdialog" aria-modal="true" aria-labelledby="turnTitle" aria-describedby="turnNote">
      <h2 class="ctitle" id="turnTitle">Play wide?</h2>
      <p class="cnote" id="turnNote"></p>
      <button class="btn play sm" id="turnYes" type="button">Switch</button>
      <button class="btn" id="turnNo" type="button">Not now</button>
    </div>
  </div>

  <div class="modal" id="noteModal" hidden>'''

TURN_JS = r"""
// (v407) turning the phone on the main menu: offered the other way round (the app tells the game how it's held: 'nativeturn')
{ const el = $('turnModal'); let want = '', quietTill = 0;
  const free = () => state === 'menu' && menuPage === 'home' && !building && !lookOpen && !lkOn() && $('orient').hidden && !menu.classList.contains('tutoring') && !document.querySelector('.modal:not([hidden]):not(#turnModal)');
  const close = () => { if (!el.hidden) el.hidden = true; want = ''; };
  window.addEventListener('nativeturn', e => { const way = e && e.detail && e.detail.way; if (way !== 'port' && way !== 'land') return;
    if (way === store.orient) { close(); quietTill = 0; return; } // (back the way it plays: the card goes, and the next turn may ask again)
    if (!store.orient || roomy() || performance.now() < quietTill || !free()) return;
    want = way; $('turnTitle').textContent = way === 'land' ? 'Play wide?' : 'Play upright?';
    $('turnNote').textContent = 'You turned your phone. Switch the game to ' + (way === 'land' ? 'landscape' : 'portrait') + '? You can change it any time in Settings.';
    el.hidden = false; AU.ui(); setTimeout(() => $('turnYes').focus({ preventScroll: true }), 30); });
  $('turnYes').addEventListener('click', () => { const w = want; close(); if (!w) return; AU.init(); AU.ui(); setOrient(w); });
  $('turnNo').addEventListener('click', () => { close(); AU.ui(); quietTill = performance.now() + 20000; });
  el.addEventListener('click', e => { if (e.target === el) { close(); quietTill = performance.now() + 20000; } }); }
"""

def apply(s):
    # the hard paint labels
    s = rep(s, "wxPhase === 'dusk' ? 'Hard paint ' + Math.ceil(wxLeft) + 's' : ", "wxPhase === 'dusk' ? '' : ")
    s = rep(s, "const wx = $('wx'), wxOn = wxPhase !== 'clear' && !(bannerWx && performance.now() < bannerUntil);",
               "const wx = $('wx'), wxOn = wxPhase !== 'clear' && wxPhase !== 'dusk' && !(bannerWx && performance.now() < bannerUntil); // (v407: no hard paint chip)")
    s = rep(s, "sunsSeen > 1 ? '' : 'Hard paint slows you until the rain.'", "''", 2)
    s = rep(s, "wxBanner('Rain!', rainsSeen++ ? '' : 'Hard paint softens');", "rainsSeen++; wxBanner('Rain!', '');")
    s = rep(s, "prev === 'dusk' ? (n ? '' : 'Hard paint softens') : ", "prev === 'dusk' ? '' : ")
    # the turn card
    s = rep(s, '  <div class="modal" id="noteModal" hidden>', TURN_HTML)
    s = rep(s, "function setOrient(v) { store.orient = v; save(); applyOrient(); heroT = 0; }", "function setOrient(v) { store.orient = v; save(); applyOrient(); heroT = 0; }" + TURN_JS)
    # the music's blip on coming back: silent before any stop, silent while away, faded back in once it runs
    s = rep(s, "  function build(c, live) {\n    ctx = c;", "  let wakeG = null; // (v407: the output's own gate, shut while the sound is away so a restart can't blip)\n"
               "  function hush() { if (!ctx || !wakeG) return; const t = ctx.currentTime; wakeG.gain.cancelScheduledValues(t); wakeG.gain.setValueAtTime(0, t); }\n"
               "  function unhush() { if (!ctx || !wakeG || ctx.state !== 'running') return; const t = ctx.currentTime; wakeG.gain.cancelScheduledValues(t); wakeG.gain.setValueAtTime(0, t); wakeG.gain.setValueAtTime(0, t + 0.12); wakeG.gain.linearRampToValueAtTime(1, t + 0.4); }\n"
               "  function build(c, live) {\n    ctx = c;")
    s = rep(s, "out = ctx.createGain(); out.gain.value = store.muted ? 0 : 1; out.connect(hp);",
               "wakeG = ctx.createGain(); wakeG.gain.value = 1; wakeG.connect(hp); out = ctx.createGain(); out.gain.value = store.muted ? 0 : 1; out.connect(wakeG);")
    s = rep(s, "function watch(c) { c.onstatechange = () => { if (c === ctx && c.state === 'interrupted') awayHid = true; }; }",
               "function watch(c) { c.onstatechange = () => { if (c !== ctx) return; if (c.state === 'interrupted') awayHid = true; if (c.state === 'running') unhush(); else hush(); }; }")
    # a fresh context starts shut and opens once it runs
    s = rep(s, "    build(c, true); watch(c);\n    const rain = mood.rain", "    build(c, true); watch(c); if (c.state === 'running') unhush(); else hush();\n    const rain = mood.rain")
    # going away: shut, then suspend a beat later (the last slice made is silence)
    s = rep(s, "suspend(h) { if (!ctx) return; if (h) { awayHid = true; ctx.suspend().catch(() => {}); } else api.wake(); },",
               "suspend(h) { if (!ctx) return; if (h) { awayHid = true; hush(); const c = ctx; setTimeout(() => { if (c === ctx && document.hidden) c.suspend().catch(() => {}); }, 100); } else api.wake(); },")
    # the app's stop-and-start on coming back: shut first, then the restart, then open
    s = rep(s, "      const go = () => { if (!ctx || ctx.state === 'running') return after(); ctx.resume().then(after, () => {}); };\n      if (kick && ctx.state === 'running') ctx.suspend().then(go, go); else go();",
               "      const go = () => { if (!ctx || ctx.state === 'running') { unhush(); return after(); } ctx.resume().then(() => { unhush(); after(); }, () => {}); };\n"
               "      hush(); if (kick && ctx.state === 'running') { const c = ctx; setTimeout(() => { if (c === ctx) c.suspend().then(go, go); }, 100); } else go();")
    return s
