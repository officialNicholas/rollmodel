# The same song in three dresses, picked by the stage (it switches on the next bar line):
#  - Halloween (the Crypt, the Cathedral, the Manor): unchanged, the celesta hook and the theremin bridge
#  - Palette Island: tropical. A steel pan plays the hook (long notes rolled, as a panist holds them), an island flute sings the bridge,
#    ukulele strums on the off-beats, a round plucked bass in a calypso step, marimba patter, a soca kick with a dembow rim click,
#    congas and shaker, and a little more swing
#  - Blank Canvas (and any standard stage): a regular pop version. Electric piano on the hook, a smooth synth lead in the bridge,
#    piano stabs, a punchy synth bass in a 3-3-2 rhythm, pluck arpeggios, the usual kit
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

# which version plays: set by the stage on show, read by the sequencer at each bar line
rep("const THEMES = [", "// the music's version for each stage: the Halloween canvases keep the original, the island goes tropical, the rest get the pop version\nlet MUSIC_STYLE = 'spooky';\nconst musicStyleOf = id => id === 'island' ? 'tropical' : ['crypt', 'cathedral', 'manor'].includes(id) ? 'spooky' : 'pop';\nconst THEMES = [")
rep("  TH = T; HOR.set(T.hor);", "  TH = T; MUSIC_STYLE = musicStyleOf(T.id); HOR.set(T.hor);")

# the new voices, alongside the originals
rep("    drone(d, m, len) { tone({ bus: M, mb: 'pad', d, type: 'sawtooth', uni: 3, spread: 12, f: mf(m), dur: 0.6, hold: Math.max(0.1, len - 0.5), a: 0.4, v: 0.06, lp: [420, 0, 2], vib: [7, 9] }); },\n  };",
"""    drone(d, m, len) { tone({ bus: M, mb: 'pad', d, type: 'sawtooth', uni: 3, spread: 12, f: mf(m), dur: 0.6, hold: Math.max(0.1, len - 0.5), a: 0.4, v: 0.06, lp: [420, 0, 2], vib: [7, 9] }); },
    // ---- the island's band ----
    // steel pan: a struck note with the pan's bright harmonics (FM at 1:1, the index falling as it rings), the octave partial
    // blooming just after, a little stick noise; long notes are rolled, the way a panist holds one
    steel(d, m, len, v) {
      const f = mf(m), sx = s16(); v *= hum(0.94, 1.04);
      const hit = (dd, vv) => {
        tone({ bus: M, d: dd, f: f * 1.008, f1: f, glide: 0.025, fm: [1, 1.7, 0.3, 0.16], dur: 0.7, v: 0.088 * vv, a: 0.0015, rv: 0.18, ec: 0.1 });
        tone({ bus: M, d: dd, f: f * 2, det: 4, dur: 0.45, v: 0.026 * vv, a: 0.01, pan: -0.2 });
        tone({ bus: M, d: dd, f: f * 3.01, dur: 0.16, v: 0.01 * vv, a: 0.002, pan: 0.2 });
        hiss({ bus: M, d: dd, k: 'w', type: 'bandpass', f: Math.min(9000, f * 5), q: 2, dur: 0.012, v: 0.012 * vv });
      };
      hit(d, v);
      if (len >= sx * 3.5) for (let k = 1, n = Math.floor(len / sx * 1.5) - 1; k < n; k++) hit(d + k * sx / 1.5, v * (k % 2 ? 0.4 : 0.48));
    },
    // the island flute (the bridge): a soft sine with a breathy edge, sliding into each note, a slow vibrato
    flute(d, m, len, v, from) {
      const f0 = mf(from || m), f1 = mf(m), gl = from ? 0.06 : 0.001, hold = Math.max(0.05, len - 0.12);
      tone({ bus: M, mb: 'wide', d, f: f0, f1, glide: gl, dur: 0.22, hold, a: 0.035, v: 0.078 * v, vib: [5.2, 14, 0.35], rv: 0.3, ec: 0.16 });
      tone({ bus: M, mb: 'wide', d, type: 'triangle', f: f0 * 2, f1: f1 * 2, glide: gl, dur: 0.16, hold: hold * 0.7, a: 0.05, v: 0.009 * v, pan: 0.3 });
      hiss({ bus: M, mb: 'wide', d, k: 'w', type: 'bandpass', f: f1 * 2.1, q: 2.5, dur: 0.12, hold: Math.min(hold, 0.25), a: 0.02, v: 0.016 * v, rv: 0.2 });
    },
    // ukulele on the off-beats: each string a plucked saw through a closing filter, a few ms apart, down-strums and up-strums
    uke(d, ch, v, up) {
      const notes = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[0] + 24], ord = up ? notes.slice().reverse() : notes;
      ord.forEach((m, k) => tone({ bus: M, mb: 'wide', d: d + k * 0.011, type: 'sawtooth', f: mf(m), dur: 0.15, v: 0.026 * v * (up ? 0.8 : 1), a: 0.002, lp: [3400, 650, 1.1, 0, 0.05], pan: 0.28, rv: 0.1 }));
    },
    // a round island bass: a sine with a soft plucked edge
    ibass(d, m, len, v) { const f = mf(m); tone({ bus: M, mb: 'bas', d, f, dur: len * 1.1, v: 0.27 * v, a: 0.005 }); tone({ bus: M, mb: 'bas', d, type: 'triangle', f, dur: len * 0.8, v: 0.1 * v, a: 0.003, lp: [1500, 320, 1.2, 0, 0.05] }); },
    // marimba: a woody strike (FM at 4:1, gone in a few ms) and a soft body
    marimba(d, m, v, k) { const f = mf(m); tone({ bus: M, d, f, fm: [4, 1.2, 0, 0.012], dur: 0.26, v: 0.075 * v, a: 0.001, ec: 0.16, pan: k % 2 ? 0.34 : -0.34 }); tone({ bus: M, d, f: f * 4, dur: 0.035, v: 0.01 * v, a: 0.0008 }); },
    // a soft warm pad under it all: two triangles a note through a gentle filter
    ipad(d, ch, len, v) { const hold = Math.max(0.1, len - 0.4); for (const m of ch) tone({ bus: M, mb: 'pad', d, type: 'triangle', uni: 2, spread: 14, f: mf(m), dur: 0.6, hold, a: 0.35, v: 0.045 * v, lp: [1400], rv: 0.4 }); },
    conga(d, f, v) { smp('tom', { d: d + hum(0, 0.004), v: 0.22 * v, rate: f / 150, pan: f > 300 ? 0.32 : -0.24 }); },
    rim(d, v) { smp('snap', { d: d + hum(0, 0.003), v: 0.12 * v, rate: 1.25, pan: 0.12, rv: 0.12 }); },
    // ---- the pop version's band ----
    // electric piano: a warm FM tine (1:1, mellowing as it rings), a little bark on the attack, a glock an octave up
    ep(d, m, len, v) {
      const f = mf(m); v *= hum(0.95, 1.03);
      tone({ bus: M, d, f, fm: [1, 1.15, 0.12, 0.28], dur: Math.max(0.55, len * 1.7), v: 0.09 * v, a: 0.002, rv: 0.16, ec: 0.1 });
      tone({ bus: M, d, f, fm: [14, 0.42, 0, 0.018], dur: 0.06, v: 0.026 * v, a: 0.001 });
      tone({ bus: M, d, f: f * 2, fm: [3.5, 1.1, 0, 0.05], dur: 0.28, v: 0.014 * v, a: 0.001, pan: 0.3 });
    },
    // the bridge: a smooth synth lead, two saws through a soft filter and a square under it, sliding between notes
    slead(d, m, len, v, from) {
      const f0 = mf(from || m), f1 = mf(m), gl = from ? 0.06 : 0.001, hold = Math.max(0.05, len - 0.1);
      tone({ bus: M, mb: 'wide', d, type: 'sawtooth', uni: 2, spread: 10, f: f0, f1, glide: gl, dur: 0.2, hold, a: 0.02, v: 0.05 * v, lp: [1900, 1300, 0.8, 0, 0.3], vib: [5.4, 9, 0.35], rv: 0.24, ec: 0.18 });
      tone({ bus: M, mb: 'wide', d, type: 'square', f: f0 / 2, f1: f1 / 2, glide: gl, dur: 0.18, hold, a: 0.02, v: 0.012 * v, lp: [900] });
    },
    // piano-ish chord stabs on the off-beats
    epstab(d, ch, v) { ch.forEach((m, k) => tone({ bus: M, mb: 'wide', d: d + k * 0.004, f: mf(m), fm: [1, 1.0, 0.1, 0.06], dur: 0.2, v: 0.03 * v, a: 0.002, pan: k === 1 ? 0 : k ? 0.3 : -0.3, rv: 0.1 })); },
    // synth bass: a sine under a saw through a closing filter
    sbass(d, m, len, v) { const f = mf(m); tone({ bus: M, mb: 'bas', d, f, dur: len * 1.05, v: 0.24 * v, a: 0.004 }); tone({ bus: M, mb: 'bas', d, type: 'sawtooth', f, dur: len * 0.9, v: 0.13 * v, a: 0.003, lp: [1800, 320, 1.6, 0, 0.06] }); },
    pluck(d, m, v, k) { tone({ bus: M, d, type: 'triangle', f: mf(m), dur: 0.16, v: 0.07 * v, a: 0.001, lp: [5000, 1500, 1, 0, 0.05], ec: 0.22, pan: k % 2 ? 0.36 : -0.36 }); },
  };""")
# the sequencer: the version changes on a bar line; the island and pop versions have their own step
rep("  let seqT = 0, seqS = 0, musOn = false, arr = 'menu', lastMode = 'none', bpm = 100, prevLead = 0, lastLow = -1;",
    "  let seqT = 0, seqS = 0, musOn = false, arr = 'menu', lastMode = 'none', bpm = 100, prevLead = 0, lastLow = -1, style = 'spooky';")
rep("""  function playStep(s, t) {
    const bar = Math.floor(s / 16) % 16, e = s % 16,""",
"""  function playStep(s, t) {
    if (s % 16 === 0) style = typeof MUSIC_STYLE === 'string' ? MUSIC_STYLE : 'spooky';
    if (style !== 'spooky') return playStepAlt(s, t);
    const bar = Math.floor(s / 16) % 16, e = s % 16,""")
rep("""  function ambient() {""",
"""  // the island (tropical) and pop versions: the same bars, chords and melody, their own band and groove
  function playStepAlt(s, t) {
    const bar = Math.floor(s / 16) % 16, e = s % 16, names = BARS[bar], ch = CH[names[e < 8 || names.length === 1 ? 0 : 1]], root = ch[0], tones = ch[1], hookBar = bar < 8, trop = style === 'tropical';
    const play = arr === 'play', hot = play && (mood.late || mood.giant || mood.ot), d = t - T() + (e % 2 ? s16() * (trop ? 0.17 : 0.1) : 0), fill = play && (bar === 7 || bar === 15) && e >= 12;
    if (trop) {
      if (play) {
        if (e % 4 === 0) I.kick(d, e === 0 ? 0.9 : 0.72);
        if ((e === 3 || e === 6 || e === 11 || e === 14) && !fill) I.rim(d, e === 6 || e === 14 ? 1 : 0.8);
        if (fill) I.conga(d, [340, 310, 280, 250][e - 12], 0.9 + (e - 12) * 0.05);
        else if (e === 7 || e === 13) I.conga(d, 330, 0.75); else if (e === 10) I.conga(d, 255, 0.85); else if (e === 15) I.conga(d, 300, 0.5);
        I.shaker(d, e % 4 === 2 ? 1 : e % 2 ? 0.55 : 0.75);
        if (e === 12 && hot) I.clap(d, 0.8);
        if (e === 0 && (bar === 0 || bar === 8)) { I.crash(d, 0.7); if (s > 0) I.impact(d, 0.8); }
        if (e === 0 || e === 8) I.ibass(d, root, s16() * 2.6, 1);
        if (e === 6) I.ibass(d, root + 7, s16() * 1.6, 0.8);
        if (e === 14) I.ibass(d, root + (bar % 2 ? 12 : 7), s16() * 1.6, 0.7);
        if (e % 4 === 2) I.uke(d, tones, e === 6 || e === 14 ? 1 : 0.8, e % 8 === 6);
        if (e === 8 && (bar === 7 || bar === 15)) I.swell(d, s16() * 8, 0.8);
        if (e === 8 && bar === 15) I.riser(d, s16() * 8, 0.8);
      } else {
        if (e === 0 || e === 8) I.kick(d, 0.35);
        if (e % 2 === 0) I.shaker(d, e % 4 === 2 ? 1 : 0.6);
        if (e === 6 || e === 14) I.rim(d, 0.6);
        if (e === 10) I.conga(d, 270, 0.45);
        if (e === 0 || e === 8) I.ibass(d, root, s16() * 5, 0.6);
        if (e % 8 === 6) I.uke(d, tones, 0.55, false);
        if (e === 8 && (bar === 7 || bar === 15)) I.swell(d, s16() * 8, 0.8);
      }
      if (e === 0 || (e === 8 && names.length > 1)) I.ipad(d, tones, s16() * (names.length > 1 ? 8 : 16), play ? 0.45 : 0.8);
    } else {
      if (play) {
        if (e === 0 || e === 8 || (e === 10 && bar % 2 === 1) || (hot && (e === 4 || e === 12))) I.kick(d, e === 0 ? 1 : 0.86);
        if ((e === 4 || e === 12) && !fill) I.clap(d, 1);
        if (fill) I.tom(d, [200, 168, 140, 112][e - 12], 0.85 + (e - 12) * 0.06);
        if (e % 2 === 0 || hot) I.hat(d, e % 4 === 2 ? 1 : e % 2 ? 0.42 : 0.66, false);
        if (e === 14 && bar % 2 === 1 && !fill) I.hat(d, 0.75, true);
        if (e === 0 && (bar === 0 || bar === 8)) { I.crash(d, 1); if (s > 0) I.impact(d, 1); }
        if (e === 0 || e === 3 || e === 6 || e === 8 || e === 11 || e === 14) I.sbass(d, root + (e === 14 && bar % 2 ? 12 : 0), s16() * (e === 0 || e === 8 ? 2.4 : 1.6), e === 0 || e === 8 ? 1 : 0.75);
        if (e % 4 === 2) I.epstab(d, tones, e === 6 || e === 14 ? 1 : 0.8);
        if (e === 8 && (bar === 7 || bar === 15)) I.swell(d, s16() * 8, 1);
        if (e === 8 && bar === 15) I.riser(d, s16() * 8, 1);
      } else {
        if (e === 0 || e === 8) I.kick(d, 0.4);
        if (e % 2 === 0) I.hat(d, e % 4 === 2 ? 0.6 : 0.35, false);
        if (e === 4 || e === 12) I.snap(d, 0.7);
        if (e === 0 || e === 8) I.sbass(d, root, s16() * 5, 0.6);
        if (e === 8 && (bar === 7 || bar === 15)) I.swell(d, s16() * 8, 1);
      }
      if (e === 0 || (e === 8 && names.length > 1)) I.pad(d, tones, s16() * (names.length > 1 ? 8 : 16), play ? 0.42 : 0.8);
    }
    const hook = trop ? I.steel : I.ep, sing = trop ? I.flute : I.slead;
    for (const n of LEAD[bar]) if (n[0] === e) {
      const len = n[2] * s16();
      if (hookBar) {
        const bv = play ? (mood.sun ? 0.6 : 1) : 0.75; hook(d, n[1], len, bv); if (play && mood.giant) I.power(d, n[1] + 12, len); prevLead = 0;
        if (Math.floor(s / 256) % 2 === 1) { let h = 0; for (const tn of tones) for (const o of [12, 24]) if (tn + o < n[1] - 1 && tn + o > h) h = tn + o; if (h) hook(d, h, len, bv * 0.45); }
      } else { sing(d, n[1], len, play ? 1 : 0.8, prevLead); prevLead = n[1]; }
    }
    // marimba patter all through the island version (soft under the hook); plucks over the pop bridge, and on every 16th when it heats up
    if (play && (hot || !hookBar || trop) && (hot || e % 2 === 0)) { const m = tones[[0, 1, 2, 1][(hot ? e : e >> 1) % 4]] + (trop ? 12 : 24), k = hot ? e : e >> 1, vv = hot ? 0.85 : trop && hookBar ? 0.32 : 0.55; if (trop) I.marimba(d, m, vv, k); else I.pluck(d, m, vv, k); }
    if (play && mood.sun && e === 0) I.drone(d, root - 12 + 12 * (root < 40), s16() * 16);
  }
  function ambient() {""")
open(p, 'w').write(s)
print('ok')
