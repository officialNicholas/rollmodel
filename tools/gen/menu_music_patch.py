# the main menu gets its own version: ethereal, chords only (no melody). Wide slow pads, a soft choir, a warm low root,
# and a glassy rolled chord on each change, left to shimmer in the reverb and echo
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
rep("""    // ---- the pop version's band ----""", """    // ---- the menu's ethereal band ----
    // a wide slow pad: four detuned saws a note, the filter opening as the chord swells
    ether(d, ch, len, v) { const hold = Math.max(0.2, len - 0.9); for (const m of ch) tone({ bus: M, mb: 'pad', d, type: 'sawtooth', uni: 4, spread: 26, f: mf(m), dur: 1.3, hold, a: 0.9, v: 0.05 * v, lp: [480, 1500, 0.6, 0.2, Math.max(0.4, len * 0.45)], rv: 0.6, ec: 0.08 }); },
    // a soft choir an octave up: triangles that breathe with a slow vibrato
    choir(d, ch, len, v) { const hold = Math.max(0.2, len - 1.1); ch.forEach((m, k) => tone({ bus: M, mb: 'wide', d: d + k * 0.05, type: 'triangle', uni: 2, spread: 9, f: mf(m + 12), dur: 1.5, hold, a: 1.1, v: 0.034 * v, lp: [2300], vib: [4.4, 7, 1.2], rv: 0.7, pan: (k - 1) * 0.4 })); },
    // the root underneath, warm and round
    sub(d, m, len, v) { const hold = Math.max(0.2, len - 0.8); tone({ bus: M, mb: 'bas', d, f: mf(m), dur: 1.1, hold, a: 0.5, v: 0.17 * v }); tone({ bus: M, mb: 'bas', d, type: 'triangle', f: mf(m + 12), dur: 0.9, hold: hold * 0.8, a: 0.7, v: 0.03 * v, lp: [900] }); },
    // glass: a chord rolled from the bottom up, a soft bell on each note, ringing off into the echo
    glass(d, ch, v) { [...ch, ch[0] + 12].forEach((m, k) => tone({ bus: M, d: d + k * 0.075, f: mf(m + 12), fm: [2, 0.9, 0, 0.35], dur: 2.4, v: 0.028 * v * (1 - k * 0.1), a: 0.004, rv: 0.6, ec: 0.26, pan: k % 2 ? 0.45 : -0.45 })); },
    // a breath of air between sections
    air(d, len, v) { hiss({ bus: M, mb: 'wide', d, k: 'p', type: 'bandpass', f: 900, f1: 2600, glide: len * 0.6, q: 0.9, a: len * 0.45, dur: len * 0.5, v: 0.03 * v, rv: 0.5 }); },
    // ---- the pop version's band ----""")
rep("""  function playStep(s, t) {
    if (s % 16 === 0) style = typeof MUSIC_STYLE === 'string' ? MUSIC_STYLE : 'spooky';
    if (style !== 'spooky') return playStepAlt(s, t);""", """  function playStep(s, t) {
    if (s % 16 === 0) style = typeof MUSIC_STYLE === 'string' ? MUSIC_STYLE : 'spooky';
    if (arr === 'menu') return playStepMenu(s, t);
    if (style !== 'spooky') return playStepAlt(s, t);""")
rep("""  // the island (tropical) and pop versions: the same bars, chords and melody, their own band and groove""", """  // the menu: the same chords, no melody and no drums, in an ethereal haze
  function playStepMenu(s, t) {
    const bar = Math.floor(s / 16) % 16, e = s % 16, names = BARS[bar], two = names.length > 1, ch = CH[names[e < 8 || !two ? 0 : 1]], root = ch[0], tones = ch[1], d = t - T();
    if (e === 0 || (e === 8 && two)) { const len = s16() * (two ? 8 : 16); I.ether(d, tones, len, 1); I.choir(d, tones, len, 1); I.sub(d, root, len, 1); I.glass(d, tones, e === 0 && bar % 8 === 0 ? 1 : 0.75); }
    else if (e === 8) I.glass(d, tones.map(m => m + 12), 0.4);
    if (e === 0 && bar % 4 === 0) I.air(d, s16() * 16, 1);
    if (e === 8 && (bar === 7 || bar === 15)) I.swell(d, s16() * 8, 0.55);
  }
  // the island (tropical) and pop versions: the same bars, chords and melody, their own band and groove""")
open(p, 'w').write(s)
print('ok')
