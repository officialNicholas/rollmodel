"""v269: the Tutorial event goes (Choose event keeps Versus, Showdown and Time trial; a new player's first match is still the lesson), and
Settings gets a small "Restart Game" under the Terms row: a first tap asks ("Tap again to erase all progress"), a second within 4 s
puts everything back to a first launch (name, look, rank, dabs, items, skills, the lesson, the intro) and keeps the sound, music,
screen and graphics settings. The app's own copy of the save is replaced along with the web view's, so it can't bring the old progress
back. Then the game starts again from the top."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
CSS = """.sreset{grid-column:1/-1;justify-self:center;margin:4px 0 0;padding:6px 12px;border:0;background:none;font:700 12px/1.2 var(--font-ui);color:rgba(255,255,255,.55);text-decoration:underline;text-underline-offset:3px;cursor:pointer;-webkit-tap-highlight-color:transparent}
.sreset.arm{color:#FF7A8A;text-decoration:none}
"""
JS = """
// (v269) Restart Game: back to a first launch, the sound, music, screen and graphics settings kept. A first tap asks, a second within a few
// seconds does it. The save goes to the app too (at once, not after the usual short wait), so the app's own copy can't bring it back
{ const b = $('resetBtn'); let armT = 0;
  const disarm = () => { if (armT) clearTimeout(armT); armT = 0; b.classList.remove('arm'); b.textContent = 'Restart Game'; };
  b.addEventListener('click', () => {
    if (!armT) { b.classList.add('arm'); b.textContent = 'Tap again to erase all progress'; AU.nope && AU.nope(); buzz(8); armT = setTimeout(disarm, 4000); return; }
    disarm(); b.disabled = true;
    const keep = {}; for (const k of ['muted', 'sfxOff', 'musicOff', 'gfx', 'orient']) if (store[k] !== undefined) keep[k] = store[k];
    for (const k of Object.keys(store)) delete store[k];
    Object.assign(store, { level: 0, sel: 0, best: {}, stars: {}, seen: {}, muted: false, runs: 0, tut: { ph: 'match' } }, keep); // (as a first launch starts: the lesson first)
    save(); saveSend(); try { AU.trim && AU.trim(); } catch (e) {}
    setTimeout(() => location.reload(), 150);
  });
  $('setDone').addEventListener('click', disarm); $('setBack').addEventListener('click', disarm); }"""
def apply(s):
    # the Tutorial card, its picture and its button
    i = s.index('        <div class="evcard" data-ev="tut"'); j = s.index('</button></div>\n', i) + len('</button></div>\n')
    assert 'id="evTut"' in s[i:j] and s[i:j].count('class="evcard"') == 1; s = s[:i] + s[j:]
    s = rep(s, " set('evTutArt', 'island');", "")
    i = s.index("$('evTut').addEventListener('click', uiClick(() => {"); j = s.index('\n', i); assert 'start(); }));' in s[i:j]
    s = s[:i] + "// (v269: the Tutorial event is gone; a new player's first match is still the lesson)" + s[j:]
    # Restart Game
    s = rep(s, '        <p class="sver" id="setVer"></p>\n', '        <button class="sreset" id="resetBtn" type="button">Restart Game</button>\n        <p class="sver" id="setVer"></p>\n')
    s = rep(s, ".sver{grid-column:1/-1;", CSS + ".sver{grid-column:1/-1;")
    s = rep(s, "const tutPh = () => store.tut.ph,", JS.lstrip('\n') + "\nconst tutPh = () => store.tut.ph,")
    return s
