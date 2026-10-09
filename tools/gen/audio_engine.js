// ---------- sound: everything is synthesized, nothing to download ----------
// A little mixing desk. Effects sit in five stereo positions (the holy water is heard from where it is), music has its
// own bus that gets muffled on pause and ducks under big hits, everything shares a plate reverb and a tempo echo,
// and the master is EQ'd, compressed, softly clipped and limited so it stays loud and clean on a phone speaker.
function makeAudio() {
  let ctx = null, out, sfx, mus, musWet, musEcho, musLP, musDuck, verb, echo, pans = [], NZ = {}, timer = 0;
  let rollG, rollF, rollLfo, rainG, sizG, chA = null;
  const mood = { late: false, giant: false, sun: false, ot: false, rain: 0, sizzle: 0 };
  const CENTER = { p: 2, g: 1 }, MUS_PLAY = 0.12, MUS_MENU = 0.2;
  // trims from metering every effect against the music, so the important ones cut through and the frequent ones sit back
  const LVL = { go: 1, ui: 2.5, nope: 1.25, land: 0.83, splat: 1.36, fling: 1.26, whoosh: 5.5, swish: 5, brake: 1.4, notch: 1.6, enter: 0.8, glug: 1.4, pop: 1.8, power: 1.9, orb: 2, shrink: 1.4, die: 0.8, bonk: 0.87, spot: 2.2, ready: 2, danger: 6, low: 0.7, count: 2.5, tick: 2.8, horn: 1.1, draw: 2.5, heatOn: 4, dusk: 1.8, splashWater: 2.5, sprinkle: 3.2, sink: 0.63, rumble: 0.45, rise: 0.7, flip: 2, flipBack: 2 };
  let cur = CENTER, pend = null;
  const mf = m => 440 * Math.pow(2, (m - 69) / 12);
  let tOff = 0; const T = () => ctx.currentTime + tOff; // tOff only moves in tests
  const rnd = (a, b) => a + Math.random() * (b - a);
  const cl = (v, a, b) => v < a ? a : v > b ? b : v;

  // ---- building blocks ----
  function noiseBuf(kind) {
    const sr = ctx.sampleRate, n = sr * 2, b = ctx.createBuffer(1, n, sr), d = b.getChannelData(0);
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0, last = 0;
    for (let i = 0; i < n; i++) {
      const w = Math.random() * 2 - 1;
      if (kind === 'w') d[i] = w * 0.7;
      else if (kind === 'p') { b0 = 0.99886 * b0 + w * 0.0555179; b1 = 0.99332 * b1 + w * 0.0750759; b2 = 0.969 * b2 + w * 0.153852; b3 = 0.8665 * b3 + w * 0.3104856; b4 = 0.55 * b4 + w * 0.5329522; b5 = -0.7616 * b5 - w * 0.016898; d[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + w * 0.5362) * 0.12; b6 = w * 0.115926; }
      else { last = (last + 0.02 * w) / 1.02; d[i] = last * 3.2; }
    }
    return b;
  }
  // a plate: bright early, darker as it fades, slightly different left and right
  function plate(sec) {
    const sr = ctx.sampleRate, n = Math.floor(sr * sec), b = ctx.createBuffer(2, n, sr);
    for (let c = 0; c < 2; c++) {
      const d = b.getChannelData(c); let lp = 0;
      for (let i = 0; i < n; i++) { const t = i / n; lp += (Math.random() * 2 - 1 - lp) * (0.85 - 0.7 * t); d[i] = lp * Math.pow(1 - t, 3.4) * Math.min(1, i / (sr * 0.008)); }
      for (const [ms, g] of [[11, 0.5], [17, 0.35], [29, 0.3], [41, 0.22]]) { const k = Math.floor(sr * ms / 1000 * (c ? 1.13 : 1)); if (k < n) d[k] += g * (c ? -1 : 1); }
    }
    return b;
  }
  // where the next sound sits: one of five stereo spots, and how loud
  const dest = o => o.bus === 'mus' ? mus : (pans[o.p !== undefined ? o.p : cur.p] || sfx);
  // music sends go through their own send buses, so the music's reverb and echo follow its volume (and the pause)
  function sends(node, o) {
    const m = o.bus === 'mus';
    if (o.rv) { const s = ctx.createGain(); s.gain.value = o.rv; node.connect(s); s.connect(m ? musWet : verb); }
    if (o.ec) { const s = ctx.createGain(); s.gain.value = o.ec; node.connect(s); s.connect(m ? musEcho : echo); }
  }
  // quick rise, optional hold, then a natural exponential fall over dur
  function shape(g, t, a, v, hold, dur) {
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(v, t + a);
    const s = t + a + (hold || 0); if (hold) g.gain.setValueAtTime(v, s);
    g.gain.setTargetAtTime(0, s, Math.max(0.004, dur / 5));
    return s + dur;
  }
  function filt(spec, type, t, dur) {
    const f = ctx.createBiquadFilter(); f.type = type; f.frequency.setValueAtTime(spec[0], t);
    if (spec[1]) f.frequency.setTargetAtTime(spec[1], t + (spec[3] || 0), spec[4] || dur / 3);
    f.Q.value = spec[2] || 0.7; return f;
  }
  // one voice: f -> f1 glide, unison, FM, vibrato, a filter sweep, reverb and echo sends
  function tone(o) {
    if (!ctx) return;
    const t = T() + Math.max(0, o.d || 0) + 0.004, a = o.a || 0.004, dur = o.dur || 0.2, n = o.uni || 1;
    const v = (o.v == null ? 0.1 : o.v) * (o.bus === 'mus' ? 1 : cur.g) / Math.sqrt(n);
    const g = ctx.createGain(), end = shape(g, t, a, v, o.hold, dur) + 0.03;
    let head = g;
    const fs = o.lp ? [o.lp, 'lowpass'] : o.bp ? [o.bp, 'bandpass'] : o.hp ? [o.hp, 'highpass'] : null;
    if (fs) { const f = filt(fs[0], fs[1], t, dur); f.connect(g); head = f; }
    for (let k = 0; k < n; k++) {
      const os = ctx.createOscillator(); os.type = o.type || 'sine';
      os.frequency.setValueAtTime(o.f, t); if (o.f1) os.frequency.exponentialRampToValueAtTime(Math.max(1, o.f1), t + (o.glide || dur));
      os.detune.value = (n > 1 ? (k / (n - 1) - 0.5) * (o.spread || 16) : 0) + (o.det || 0);
      if (o.vib) { const l = ctx.createOscillator(), lg = ctx.createGain(); l.frequency.value = o.vib[0] * (1 + k * 0.07); lg.gain.setValueAtTime(0, t); lg.gain.linearRampToValueAtTime(o.vib[1], t + (o.vib[2] || 0.12)); l.connect(lg); lg.connect(os.detune); l.start(t); l.stop(end); }
      if (o.fm) { const m = ctx.createOscillator(), mg = ctx.createGain(); m.frequency.setValueAtTime(o.f * o.fm[0], t); if (o.f1) m.frequency.exponentialRampToValueAtTime(Math.max(1, o.f1 * o.fm[0]), t + (o.glide || dur)); mg.gain.setValueAtTime(o.f * o.fm[1], t); mg.gain.setTargetAtTime(o.f * (o.fm[2] || 0), t, o.fm[3] || dur / 3); m.connect(mg); mg.connect(os.frequency); m.start(t); m.stop(end); }
      os.connect(head); os.start(t); os.stop(end);
    }
    g.connect(dest(o)); sends(g, o);
  }
  // filtered noise: hiss, splash, crack, rumble
  function hiss(o) {
    if (!ctx) return;
    const t = T() + Math.max(0, o.d || 0) + 0.004, a = o.a || 0.002, dur = o.dur || 0.2;
    const v = (o.v == null ? 0.1 : o.v) * (o.bus === 'mus' ? 1 : cur.g);
    const s = ctx.createBufferSource(); s.buffer = NZ[o.k || 'w']; s.loop = true; if (o.rate) s.playbackRate.value = o.rate;
    const f = ctx.createBiquadFilter(); f.type = o.type || 'bandpass'; f.frequency.setValueAtTime(o.f || 1000, t);
    if (o.f1) f.frequency.exponentialRampToValueAtTime(Math.max(20, o.f1), t + (o.glide || dur)); f.Q.value = o.q || 0.8;
    const g = ctx.createGain(), end = shape(g, t, a, v, o.hold, dur) + 0.03;
    s.connect(f); f.connect(g); g.connect(dest(o)); sends(g, o);
    s.start(t, Math.random() * 1.5); s.stop(end);
  }
  // water drops: tiny sine chirps that rise, the sound of a liquid hitting things
  function drops(n, v, spread, d0, lo, hi) {
    for (let i = 0; i < n; i++) { const f = rnd(lo || 650, hi || 1500); tone({ d: (d0 || 0.015) + Math.random() * (spread || 0.18), f, f1: f * rnd(1.7, 2.5), glide: 0.03, dur: 0.045, v: v * rnd(0.55, 1), a: 0.001 }); }
  }
  function duck(amt, len) {
    if (!ctx) return; const t = T(), g = musDuck.gain;
    g.cancelScheduledValues(t); g.setValueAtTime(g.value, t); g.linearRampToValueAtTime(1 - amt, t + 0.02); g.setTargetAtTime(1, t + 0.08, Math.max(0.05, len / 3));
  }
  // a short warm brass voice (stingers)
  const brass = (d, m, len, v, bright) => tone({ d, type: 'sawtooth', uni: 3, spread: 14, f: mf(m), dur: 0.22, hold: len, a: 0.025, v: v || 0.07, lp: [600, bright || 2800, 1.4, 0, 0.06], vib: [5.2, 10, 0.25], rv: 0.22 });
  const bellFx = (d, m, len, v, rv) => tone({ d, f: mf(m), fm: [3.5, 1.5, 0, 0.12], dur: len, v, rv: rv == null ? 0.25 : rv });

  // ---- the music: a bouncy little danse macabre in A minor ----
  // sixteen bars: a celesta hook over oom-pah bass and off-beat stabs, then a theremin sings the bridge
  const CH = { Am: [45, [57, 60, 64]], F: [41, [57, 60, 65]], Dm: [38, [57, 62, 65]], E: [40, [56, 59, 64]], Bb: [46, [58, 62, 65]], E7: [40, [56, 62, 64]] };
  const BARS = [['Am'], ['F'], ['Dm'], ['E'], ['Am'], ['F'], ['Dm', 'E'], ['Am'], ['Dm'], ['Am'], ['Bb'], ['E'], ['Dm'], ['Am'], ['F', 'E'], ['E7']];
  const HOOK = [[0, 76, 2], [2, 81, 1], [3, 81, 1], [4, 84, 2], [6, 83, 2], [8, 81, 2], [10, 76, 2]];
  const LEAD = [
    HOOK,
    [[0, 77, 2], [2, 81, 1], [3, 81, 1], [4, 84, 2], [6, 86, 2], [8, 84, 2], [10, 81, 2]],
    [[0, 74, 2], [2, 77, 1], [3, 77, 1], [4, 81, 2], [6, 77, 2], [8, 86, 2], [10, 84, 2], [12, 81, 4]],
    [[0, 80, 2], [2, 83, 2], [4, 88, 2], [6, 86, 2], [8, 83, 2], [10, 80, 2], [12, 76, 4]],
    HOOK,
    [[0, 77, 2], [2, 81, 1], [3, 81, 1], [4, 84, 2], [6, 88, 2], [8, 86, 2], [10, 84, 2]],
    [[0, 86, 2], [2, 84, 2], [4, 81, 2], [6, 77, 2], [8, 76, 2], [10, 80, 2], [12, 83, 2], [14, 86, 2]],
    [[0, 84, 3], [3, 83, 1], [4, 81, 8]],
    [[0, 81, 4], [4, 77, 4], [8, 74, 4], [12, 77, 4]],
    [[0, 76, 6], [6, 72, 2], [8, 76, 4], [12, 81, 4]],
    [[0, 77, 4], [4, 74, 4], [8, 70, 4], [12, 74, 4]],
    [[0, 76, 8], [8, 80, 4], [12, 83, 4]],
    [[0, 81, 4], [4, 77, 4], [8, 86, 4], [12, 84, 4]],
    [[0, 84, 6], [6, 83, 2], [8, 81, 8]],
    [[0, 81, 4], [4, 84, 4], [8, 83, 4], [12, 80, 4]],
    [[0, 76, 12]],
  ];
  const M = 'mus';
  const I = {
    kick(d, v) { tone({ bus: M, d, f: 160, f1: 44, glide: 0.1, dur: 0.3, v: 0.62 * v, a: 0.0015 }); tone({ bus: M, d, type: 'triangle', f: 1400, f1: 180, glide: 0.018, dur: 0.025, v: 0.13 * v, a: 0.0008 }); },
    clap(d, v) { for (let i = 0; i < 3; i++) hiss({ bus: M, d: d + i * 0.0105, k: 'w', type: 'bandpass', f: 1250, q: 1.2, dur: i === 2 ? 0.15 : 0.022, v: 0.3 * v, rv: i === 2 ? 0.16 : 0 }); tone({ bus: M, d, type: 'triangle', f: 220, f1: 165, dur: 0.08, v: 0.12 * v }); },
    snap(d, v) { hiss({ bus: M, d, k: 'w', type: 'bandpass', f: 2600, q: 2.2, dur: 0.045, v: 0.22 * v, rv: 0.25 }); },
    hat(d, v, open) { hiss({ bus: M, d, k: 'w', type: 'highpass', f: 7600, q: 0.7, dur: open ? 0.26 : 0.04, v: 0.12 * v }); },
    shaker(d, v) { hiss({ bus: M, d, k: 'w', type: 'bandpass', f: 6800, q: 1.6, a: 0.014, dur: 0.05, v: 0.1 * v }); },
    crash(d, v) { hiss({ bus: M, d, k: 'w', type: 'highpass', f: 4800, q: 0.5, dur: 1.5, v: 0.14 * v, rv: 0.25 }); tone({ bus: M, d, type: 'square', f: 523, fm: [1.483, 2.5, 0.3, 0.5], dur: 0.9, v: 0.012 * v, hp: [2500] }); },
    tom(d, f, v) { tone({ bus: M, d, f, f1: f * 0.62, glide: 0.18, dur: 0.24, v: 0.42 * v }); hiss({ bus: M, d, k: 'p', type: 'lowpass', f: 1200, dur: 0.05, v: 0.1 * v }); },
    // pizzicato-ish bass: plucked saw through a closing filter, with a sine underneath for weight
    bass(d, m, len, v) { tone({ bus: M, d, type: 'sawtooth', f: mf(m), dur: len, v: 0.2 * v, a: 0.003, lp: [2400, 240, 2.5, 0, 0.05] }); tone({ bus: M, d, f: mf(m), dur: len * 1.1, v: 0.26 * v, a: 0.004 }); },
    stab(d, ch, v) { for (const m of ch) tone({ bus: M, d, type: 'sawtooth', f: mf(m + 12), dur: 0.1, v: 0.034 * v, a: 0.002, lp: [3400, 800, 1.2, 0, 0.035], rv: 0.12 }); },
    // celesta: FM bell, bright strike and a soft tail, with a pinch of echo
    bell(d, m, len, v) { tone({ bus: M, d, f: mf(m), fm: [3.5, 2.4, 0, 0.16], dur: Math.max(0.4, len * 1.7), v: 0.1 * v, a: 0.0015, rv: 0.2, ec: 0.14 }); tone({ bus: M, d, f: mf(m + 12), dur: 0.22, v: 0.02 * v }); },
    // theremin: a sine that slides between notes and wobbles
    theremin(d, m, len, v, from) { tone({ bus: M, d, f: mf(from || m), f1: mf(m), glide: from ? 0.09 : 0.001, dur: 0.35, hold: Math.max(0.05, len - 0.2), a: 0.06, v: 0.085 * v, vib: [5.6, 26, 0.3], rv: 0.32, ec: 0.16 }); tone({ bus: M, d, type: 'triangle', f: mf((from || m) + 12), f1: mf(m + 12), glide: from ? 0.09 : 0.001, dur: 0.3, hold: Math.max(0.05, len - 0.2), a: 0.08, v: 0.012 * v, vib: [5.6, 26, 0.3] }); },
    pad(d, ch, len, v) { for (const m of ch) tone({ bus: M, d, type: 'sawtooth', uni: 2, spread: 14, f: mf(m), dur: 0.45, hold: Math.max(0.1, len - 0.35), a: 0.22, v: 0.05 * v, lp: [1100, 0, 0.6], rv: 0.38 }); },
    arp(d, m, v) { tone({ bus: M, d, f: mf(m), fm: [3.5, 1.3, 0, 0.05], dur: 0.16, v: 0.04 * v, a: 0.001, ec: 0.22 }); },
    power(d, m, len) { tone({ bus: M, d, type: 'square', f: mf(m), dur: 0.12, hold: Math.max(0.03, len * 0.75), v: 0.035, a: 0.004, lp: [3200, 1500, 1, 0, 0.08], ec: 0.12 }); },
    drone(d, m, len) { tone({ bus: M, d, type: 'sawtooth', uni: 2, spread: 10, f: mf(m), dur: 0.5, hold: Math.max(0.1, len - 0.4), a: 0.35, v: 0.07, lp: [420, 0, 2], vib: [7, 9] }); },
  };
  let seqT = 0, seqS = 0, musOn = false, arr = 'menu', lastMode = 'none', bpm = 100, prevLead = 0, lastLow = -1;
  const s16 = () => 60 / bpm / 4;
  function playStep(s, t) {
    const bar = Math.floor(s / 16) % 16, e = s % 16, names = BARS[bar], ch = CH[names[e < 8 || names.length === 1 ? 0 : 1]], root = ch[0], tones = ch[1], hookBar = bar < 8;
    const play = arr === 'play', hot = play && (mood.late || mood.giant || mood.ot), d = t - T() + (e % 2 ? s16() * 0.12 : 0), fill = play && (bar === 7 || bar === 15) && e >= 12;
    if (play) {
      if (e === 0 || e === 8 || (e === 10 && bar % 2 === 1) || (hot && (e === 4 || e === 12))) I.kick(d, e === 0 ? 1 : 0.86);
      if ((e === 4 || e === 12) && !fill) I.clap(d, 1);
      if (fill) I.tom(d, [200, 168, 140, 112][e - 12], 0.85 + (e - 12) * 0.06);
      if (e % 2 === 0 || hot) I.hat(d, e % 4 === 2 ? 1 : e % 2 ? 0.42 : 0.66, false);
      if (e === 14 && bar % 2 === 1 && !fill) I.hat(d, 0.75, true);
      if (e === 0 && (bar === 0 || bar === 8)) I.crash(d, 1);
      if (e % 4 === 0) I.bass(d, root + (e % 8 === 4 ? 7 : 0), s16() * 1.5, 1);
      if (e === 15 && bar % 4 === 3) I.bass(d, root + 12, s16() * 0.8, 0.65);
      if (e % 4 === 2) I.stab(d, tones, e === 6 || e === 14 ? 1 : 0.8);
    } else {
      if (e === 0 || e === 8) I.kick(d, 0.5);
      if (e % 2 === 0) I.shaker(d, e % 4 === 2 ? 1 : 0.6);
      if (e === 4 || e === 12) I.snap(d, 0.7);
      if (e === 0 || e === 8) I.bass(d, root, s16() * 5, 0.6);
    }
    if (e === 0 || (e === 8 && names.length > 1)) I.pad(d, tones, s16() * (names.length > 1 ? 8 : 16), play ? 0.5 : 0.85);
    for (const n of LEAD[bar]) if (n[0] === e) {
      const len = n[2] * s16();
      if (hookBar) {
        const bv = play ? (mood.sun ? 0.6 : 1) : 0.75; I.bell(d, n[1], len, bv); if (play && mood.giant) I.power(d, n[1] + 12, len); prevLead = 0;
        if (Math.floor(s / 256) % 2 === 1) { let h = 0; for (const tn of tones) for (const o of [12, 24]) if (tn + o < n[1] - 1 && tn + o > h) h = tn + o; if (h) I.bell(d, h, len, bv * 0.5); }
      }
      else { I.theremin(d, n[1], len, play ? 1 : 0.8, prevLead); prevLead = n[1]; }
    }
    // sparkle arpeggio over the bridge, and on every 16th when it heats up
    if (play && (hot || !hookBar) && (hot || e % 2 === 0)) I.arp(d, tones[[0, 1, 2, 1][(hot ? e : e >> 1) % 4]] + 24, hot ? 0.85 : 0.55);
    if (play && mood.sun && e === 0) I.drone(d, root - 12 + 12 * (root < 40), s16() * 16);
  }
  function ambient() {
    // rain on the canvas: little drops all around, a cracking sizzle while the sun burns
    if (mood.rain > 0.05) for (let i = 0; i < 2; i++) if (Math.random() < mood.rain * 0.28) { const f = rnd(1800, 4200); tone({ p: (Math.random() * 5) | 0, d: Math.random() * 0.05, f, f1: f * 1.6, glide: 0.02, dur: 0.03, v: 0.022 * mood.rain, a: 0.001 }); }
    if (mood.sizzle > 0.1) for (let i = 0; i < 2; i++) if (Math.random() < 0.35 * mood.sizzle) hiss({ d: Math.random() * 0.05, k: 'w', type: 'highpass', f: rnd(2500, 6000), dur: 0.012, v: 0.07 * mood.sizzle });
  }
  function schedule(until) {
    if (!ctx) return;
    if (until === undefined) { if (ctx.state !== 'running') return; ambient(); }
    const ahead = until !== undefined ? until : T() + 0.16;
    if (seqT < T()) seqT = T() + 0.02;
    // the hurry-up: the tempo eases up in the last seconds and in overtime
    while (seqT < ahead) { const target = arr === 'menu' ? 100 : mood.ot ? 132 : mood.late ? 126 : 116; bpm += (target - bpm) * 0.03; if (musOn) playStep(seqS, seqT); seqS++; seqT += s16(); }
  }

  // ---- effects ----
  const fx = {
    go() { hiss({ k: 'p', type: 'bandpass', f: 300, f1: 4200, glide: 0.4, q: 1.4, dur: 0.45, v: 0.5 }); [69, 76, 81, 85].forEach(m => brass(0.38, m, 0.22, 0.05, 3400)); [93, 97, 100].forEach((m, i) => bellFx(0.4 + i * 0.05, m, 0.5, 0.06, 0.35)); },
    ui() { tone({ f: 700, f1: 1150, glide: 0.035, dur: 0.06, v: 0.11, fm: [2, 0.5, 0, 0.03] }); tone({ d: 0.025, f: 1760, dur: 0.06, v: 0.03 }); },
    nope() { tone({ type: 'triangle', f: 220, f1: 150, glide: 0.1, dur: 0.12, v: 0.16 }); tone({ d: 0.07, type: 'triangle', f: 180, f1: 130, glide: 0.1, dur: 0.12, v: 0.12 }); },
    jump() { const k = rnd(0.94, 1.06); tone({ f: 250 * k, f1: 700 * k, glide: 0.12, dur: 0.15, v: 0.24, a: 0.003, vib: [16, 25, 0.02] }); tone({ type: 'triangle', f: 500 * k, f1: 1350 * k, glide: 0.07, dur: 0.06, v: 0.05 }); hiss({ k: 'p', type: 'lowpass', f: 900, f1: 300, dur: 0.07, v: 0.1 }); },
    land(k) { k = cl(k || 0, 0, 1); tone({ f: 160, f1: 50, glide: 0.11, dur: 0.15, v: 0.2 + 0.3 * k }); hiss({ k: 'p', type: 'lowpass', f: 1500, f1: 240, dur: 0.11 + 0.08 * k, v: 0.16 + 0.22 * k }); if (k > 0.35) drops(2 + (k * 3 | 0), 0.05 * k, 0.15); },
    splat(k) { k = cl(k || 0.5, 0.2, 1.6); const r = rnd(0.9, 1.1); hiss({ k: 'w', type: 'bandpass', f: 2300 * r, f1: 360, glide: 0.11, q: 1.3, dur: 0.17 + 0.07 * k, v: 0.24 + 0.16 * k, rv: 0.05 }); hiss({ k: 'p', type: 'lowpass', f: 900, f1: 150, dur: 0.18, v: 0.18 + 0.12 * k }); tone({ f: 210 * r, f1: 68, glide: 0.08, dur: 0.11, v: 0.13 + 0.14 * k }); drops(3 + (k * 3 | 0), 0.055 + 0.03 * k, 0.2, 0.03); },
    slam() { duck(0.45, 0.6); tone({ f: 115, f1: 30, glide: 0.32, dur: 0.6, v: 0.7, a: 0.0015 }); tone({ type: 'triangle', f: 72, f1: 34, glide: 0.24, dur: 0.3, v: 0.24 }); hiss({ k: 'w', type: 'lowpass', f: 5200, f1: 120, glide: 0.38, dur: 0.48, v: 0.45, rv: 0.22 }); hiss({ k: 'w', type: 'highpass', f: 3200, dur: 0.05, v: 0.3 }); hiss({ k: 'b', type: 'lowpass', f: 420, dur: 0.9, v: 0.34, a: 0.02 }); drops(7, 0.06, 0.4, 0.05); },
    quake() { duck(0.75, 1.4); tone({ f: 78, f1: 24, glide: 0.9, dur: 1.4, v: 0.75 }); tone({ d: 0.02, type: 'triangle', f: 50, f1: 30, glide: 0.6, dur: 0.9, v: 0.28 }); hiss({ k: 'b', type: 'lowpass', f: 520, f1: 60, dur: 1.9, v: 0.6, a: 0.01, rv: 0.3 }); hiss({ k: 'w', type: 'lowpass', f: 6500, f1: 150, glide: 0.5, dur: 0.7, v: 0.45, rv: 0.3 }); for (let i = 0; i < 10; i++) hiss({ d: 0.08 + Math.random() * 1.1, k: 'w', type: 'bandpass', f: rnd(900, 3200), q: 2, dur: 0.05, v: 0.13 }); drops(10, 0.06, 0.9, 0.1); },
    burst(v) { v = v || 1; duck(0.35 * v, 0.4); hiss({ k: 'w', type: 'bandpass', f: 600, f1: 3400, glide: 0.12, q: 1, dur: 0.34, v: 0.44 * v, rv: 0.2 }); tone({ f: 95, f1: 380, glide: 0.17, dur: 0.28, v: 0.32 * v }); tone({ f: 72, f1: 34, glide: 0.2, dur: 0.34, v: 0.36 * v }); for (let i = 0; i < 11; i++) hiss({ d: Math.random() * 0.22, k: 'w', type: 'bandpass', f: rnd(1200, 4400), q: 3.2, dur: rnd(0.018, 0.05), v: 0.22 * v }); drops(6, 0.05 * v, 0.35, 0.06); },
    fling(c) { c = cl(c || 0, 0, 1); tone({ type: 'triangle', f: 180, f1: 600 + 700 * c, glide: 0.13, dur: 0.18, v: 0.22, lp: [4200] }); tone({ f: 90, f1: 260, glide: 0.09, dur: 0.11, v: 0.18 }); hiss({ k: 'w', type: 'highpass', f: 2500, dur: 0.015, v: 0.14 }); hiss({ k: 'p', type: 'bandpass', f: 500, f1: 3800, glide: 0.24, q: 1.7, dur: 0.3, v: 0.2 + 0.12 * c }); },
    whoosh() { hiss({ k: 'p', type: 'bandpass', f: 380, f1: 3200, glide: 0.3, q: 1.8, dur: 0.34, v: 0.24 }); hiss({ k: 'w', type: 'bandpass', f: 1500, f1: 6000, glide: 0.25, q: 2.5, dur: 0.22, v: 0.06 }); },
    swish() { hiss({ k: 'p', type: 'bandpass', f: 700, f1: 2800, glide: 0.25, q: 1.8, dur: 0.28, v: 0.18 }); },
    brake() { hiss({ k: 'p', type: 'bandpass', f: 1500, f1: 650, q: 2, dur: 0.11, v: 0.16 }); tone({ f: 300, f1: 160, glide: 0.08, dur: 0.09, v: 0.12 }); },
    notch(i) { bellFx(0, [72, 76, 79][Math.min(2, Math.max(0, (i | 0) - 1))] + 12, 0.18, 0.08, 0.08); },
    release() { hiss({ k: 'p', type: 'lowpass', f: 1200, f1: 400, dur: 0.06, v: 0.08 }); },
    chargeStart() {
      if (!ctx || chA) return; const g = ctx.createGain(); g.gain.value = 0; const f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 5; f.frequency.value = 300;
      const o1 = ctx.createOscillator(), o2 = ctx.createOscillator(); o1.type = o2.type = 'sawtooth'; o1.frequency.value = o2.frequency.value = 92; o2.detune.value = 16;
      o1.connect(f); o2.connect(f); f.connect(g); g.connect(pans[2]); o1.start(); o2.start(); chA = { g, f, o1, o2 };
    },
    chargeSet(c) { if (!chA) return; const t = T(); chA.f.frequency.setTargetAtTime(280 + c * 1400, t, 0.03); chA.o1.frequency.setTargetAtTime(88 + c * 130, t, 0.03); chA.o2.frequency.setTargetAtTime(88 + c * 130, t, 0.03); chA.g.gain.setTargetAtTime(c > 0.02 ? 0.05 + 0.13 * c : 0, t, 0.03); },
    chargeStop() { if (!chA) return; const a = chA; chA = null; const t = T(); a.g.gain.setTargetAtTime(0, t, 0.02); a.o1.stop(t + 0.15); a.o2.stop(t + 0.15); },
    enter() { tone({ type: 'sawtooth', f: 140, f1: 92, glide: 0.16, dur: 0.16, v: 0.06, bp: [900, 480, 6] }); hiss({ d: 0.11, k: 'p', type: 'lowpass', f: 750, f1: 150, dur: 0.15, v: 0.32 }); tone({ d: 0.11, f: 185, f1: 70, glide: 0.1, dur: 0.15, v: 0.32 }); tone({ d: 0.17, f: 240, f1: 125, dur: 0.07, v: 0.12 }); },
    glug(p) { const f = 180 + (p || 0) * 220 + rnd(-20, 40); tone({ f, f1: f * 1.9, glide: 0.055, dur: 0.075, v: 0.13, a: 0.003 }); if (Math.random() < 0.5) tone({ d: 0.03, f: f * 1.5, f1: f * 2.6, glide: 0.04, dur: 0.05, v: 0.05 }); },
    pop() { tone({ f: 520, f1: 1450, glide: 0.03, dur: 0.05, v: 0.17, a: 0.001 }); hiss({ k: 'w', type: 'highpass', f: 3500, dur: 0.02, v: 0.06 }); },
    power() { [72, 76, 79, 84, 88].forEach((m, i) => bellFx(i * 0.045, m + 12, 0.38, 0.075)); hiss({ k: 'w', type: 'highpass', f: 7000, f1: 11000, dur: 0.4, v: 0.05, a: 0.05, rv: 0.2 }); },
    orb() { [88, 91, 95, 100, 103].forEach((m, i) => bellFx(i * 0.06, m, 0.65, 0.055, 0.4)); tone({ type: 'sawtooth', uni: 3, spread: 20, f: mf(64), dur: 0.7, hold: 0.45, a: 0.3, v: 0.06, lp: [1800], rv: 0.5 }); },
    grow() { duck(0.45, 0.9); tone({ type: 'sawtooth', uni: 3, spread: 26, f: 110, f1: 440, glide: 0.45, dur: 0.5, hold: 0.25, v: 0.14, lp: [380, 4200, 2, 0, 0.18], a: 0.02 }); [57, 64, 69, 73, 76].forEach(m => tone({ d: 0.4, type: 'sawtooth', uni: 2, spread: 12, f: mf(m), dur: 0.9, v: 0.045, lp: [2800, 900], rv: 0.35 })); tone({ d: 0.4, f: 72, f1: 40, glide: 0.3, dur: 0.5, v: 0.45 }); hiss({ d: 0.4, k: 'w', type: 'highpass', f: 5200, dur: 0.6, v: 0.1, rv: 0.3 }); [81, 85, 88, 93].forEach((m, i) => bellFx(0.45 + i * 0.05, m, 0.5, 0.05)); },
    shrink() { tone({ type: 'triangle', f: 720, f1: 180, glide: 0.42, dur: 0.45, v: 0.16, vib: [11, 40, 0.05] }); hiss({ k: 'p', type: 'bandpass', f: 2000, f1: 400, q: 1.5, dur: 0.4, v: 0.08 }); },
    die(r) {
      hiss({ k: 'p', type: 'lowpass', f: 2300, f1: 200, dur: 0.38, v: 0.42 }); tone({ type: 'triangle', f: 540, f1: 90, glide: 0.5, dur: 0.55, v: 0.22, vib: [9, 45, 0.05] }); drops(5, 0.055, 0.3);
      if (r === 'sun') { hiss({ k: 'w', type: 'bandpass', f: 4600, f1: 900, q: 0.8, dur: 0.9, v: 0.32 }); tone({ type: 'sawtooth', f: 220, f1: 60, dur: 0.8, v: 0.06, lp: [1300, 200] }); }
      if (r === 'pound') tone({ f: 175, f1: 40, glide: 0.3, dur: 0.5, v: 0.42 });
      if (r === 'garlic' || r === 'brush') hiss({ k: 'w', type: 'bandpass', f: 2400, f1: 700, q: 1.3, dur: 0.3, v: 0.3 });
    },
    fall() { tone({ f: 1250, f1: 160, glide: 1.0, dur: 0.35, hold: 0.75, v: 0.13, vib: [7, 35, 0.2], a: 0.02 }); hiss({ k: 'p', type: 'bandpass', f: 2200, f1: 500, q: 2, dur: 0.9, v: 0.06 }); },
    squish() { hiss({ k: 'p', type: 'lowpass', f: 1700, f1: 150, dur: 0.3, v: 0.48 }); tone({ f: 320, f1: 65, glide: 0.24, dur: 0.28, v: 0.34 }); tone({ d: 0.03, type: 'square', f: 1100, f1: 420, glide: 0.12, dur: 0.12, v: 0.035, lp: [3000] }); drops(5, 0.06, 0.25); },
    bonk(k) { k = cl(k || 0, 0, 1); const r = rnd(0.92, 1.08); tone({ f: 330 * r, f1: 130 * r, glide: 0.075, dur: 0.11, v: 0.15 + 0.2 * k }); tone({ type: 'triangle', f: 660 * r, f1: 260, glide: 0.05, dur: 0.05, v: 0.04 + 0.05 * k }); hiss({ k: 'p', type: 'lowpass', f: 1400, f1: 300, dur: 0.07, v: 0.09 + 0.1 * k }); },
    spot() { tone({ f: mf(95), fm: [2.01, 1.2, 0, 0.08], dur: 0.16, v: 0.08 }); tone({ d: 0.08, f: mf(100), fm: [2.01, 1.2, 0, 0.08], dur: 0.32, v: 0.09, rv: 0.2 }); },
    ready() { bellFx(0, 84, 0.25, 0.08, 0.1); bellFx(0.07, 91, 0.5, 0.09); hiss({ d: 0.07, k: 'w', type: 'highpass', f: 8000, dur: 0.25, v: 0.035 }); },
    lead(up) { if (up) [79, 84, 88].forEach((m, i) => bellFx(i * 0.07, m, 0.4, 0.14)); else [76, 72, 69].forEach((m, i) => tone({ d: i * 0.09, type: 'triangle', f: mf(m), dur: 0.25, v: 0.2, rv: 0.2 })); },
    danger() { for (const d of [0, 0.11]) tone({ d, type: 'square', f: 990, f1: 930, dur: 0.07, v: 0.04, lp: [3000] }); },
    low() { if (T() - lastLow < 0.36) return; lastLow = T(); tone({ f: 72, f1: 44, glide: 0.08, dur: 0.12, v: 0.34 }); tone({ d: 0.15, f: 64, f1: 42, glide: 0.08, dur: 0.1, v: 0.24 }); },
    count(n) { const hi = n <= 3; tone({ f: hi ? 1047 : 784, fm: [2.4, 2.2, 0, 0.025], dur: 0.12, v: hi ? 0.13 : 0.1 }); tone({ type: 'square', f: hi ? 1047 : 784, dur: 0.08, v: 0.022, lp: [2600] }); },
    tick(i) { const sc = [0, 2, 4, 7, 9], k = (((i | 0) % 15) + 15) % 15, m = 76 + 12 * Math.floor(k / 5) + sc[k % 5]; tone({ f: mf(m), fm: [2, 0.7, 0, 0.04], dur: 0.12, v: 0.05 }); },
    // the buzzer at time up: a punchy brass blast and a low gong under it
    horn() { duck(0.7, 1.4); [57, 64, 69].forEach(m => brass(0, m, 0.32, 0.06, 2200)); tone({ f: 110, fm: [1.41, 3.2, 0.2, 0.9], dur: 1.8, v: 0.22, rv: 0.35 }); },
    fanfare() {
      [[0, 67], [0.11, 72], [0.22, 76]].forEach(([d, m]) => brass(d, m, 0.07, 0.075)); brass(0.33, 79, 0.18, 0.08); brass(0.56, 76, 0.07, 0.07); brass(0.68, 79, 0.95, 0.08, 3600);
      [60, 64, 67, 72].forEach(m => brass(0.68, m, 0.95, 0.04, 3200));
      [84, 88, 91, 96].forEach((m, i) => bellFx(0.74 + i * 0.07, m, 0.9, 0.055, 0.4));
      hiss({ d: 0.68, k: 'w', type: 'highpass', f: 5200, dur: 1.6, v: 0.12, rv: 0.3 }); tone({ d: 0.68, f: 98, f1: 58, glide: 0.4, dur: 0.6, v: 0.4 });
    },
    lose() { [[0, 64], [0.3, 63], [0.6, 62]].forEach(([d, m]) => tone({ d, type: 'sawtooth', uni: 2, spread: 10, f: mf(m), f1: mf(m) * 0.985, glide: 0.24, dur: 0.18, hold: 0.18, a: 0.03, v: 0.08, lp: [500, 1500, 2, 0, 0.07], vib: [5, 16, 0.15], rv: 0.25 })); tone({ d: 0.9, type: 'sawtooth', uni: 2, spread: 10, f: mf(61), f1: mf(59), glide: 1.0, dur: 0.4, hold: 0.7, a: 0.03, v: 0.085, lp: [500, 1500, 2, 0, 0.1], vib: [5, 30, 0.4], rv: 0.3 }); tone({ d: 0.9, f: mf(37), dur: 0.5, hold: 0.5, v: 0.22 }); },
    draw() { [69, 72, 76, 83].forEach((m, i) => bellFx(i * 0.1, m, 0.9, 0.06, 0.4)); },
    thunder() { hiss({ k: 'w', type: 'highpass', f: 1200, dur: 0.22, v: 0.22, rv: 0.4 }); hiss({ d: 0.05, k: 'b', type: 'lowpass', f: 600, f1: 80, glide: 1.6, dur: 2.2, v: 0.5, a: 0.06, rv: 0.4 }); hiss({ d: 0.5, k: 'b', type: 'lowpass', f: 300, dur: 1.3, v: 0.3, a: 0.3 }); },
    heatWarn() { for (let i = 0; i < 3; i++) { tone({ d: i * 0.9, f: 196, fm: [2.76, 3, 0.2, 1.0], dur: 2.0, v: 0.15, rv: 0.45 }); tone({ d: i * 0.9, f: 392, fm: [1.41, 1, 0, 0.5], dur: 1.1, v: 0.05, rv: 0.4 }); } tone({ type: 'sawtooth', uni: 3, spread: 18, f: 220, f1: 440, glide: 3.2, dur: 0.6, hold: 2.9, a: 0.6, v: 0.045, lp: [600, 2200, 1, 0, 1.2], rv: 0.3 }); },
    heatOn() { duck(0.4, 1); hiss({ k: 'p', type: 'bandpass', f: 300, f1: 2400, glide: 0.6, q: 0.8, dur: 1.1, v: 0.32, rv: 0.3 }); [69, 73, 76, 81].forEach(m => tone({ type: 'sawtooth', uni: 2, spread: 10, f: mf(m), dur: 0.7, hold: 0.55, a: 0.2, v: 0.035, bp: [1000, 1300, 2], rv: 0.5 })); },
    dusk() { [57, 60, 64, 69].forEach((m, i) => bellFx(i * 0.1, m + 12, 1.2, 0.055, 0.45)); },
    splashWater() { hiss({ k: 'w', type: 'bandpass', f: 2600, f1: 400, q: 1.2, dur: 0.5, v: 0.36, rv: 0.2 }); drops(10, 0.06, 0.5); },
    sprinkle(v) { v = v || 1; hiss({ k: 'w', type: 'highpass', f: 3500, dur: 0.45, v: 0.12 * v, a: 0.02 }); drops(14, 0.05 * v, 0.55, 0.02, 1200, 2600); },
    sink() { hiss({ k: 'b', type: 'bandpass', f: 320, f1: 120, q: 2, dur: 0.9, v: 0.38, a: 0.05 }); tone({ f: 120, f1: 40, glide: 0.8, dur: 0.85, v: 0.22 }); drops(4, 0.04, 0.6, 0.1); },
    rumble() { hiss({ k: 'b', type: 'lowpass', f: 240, f1: 110, dur: 1.5, v: 0.24, a: 0.3 }); tone({ f: 52, f1: 46, dur: 1.4, v: 0.16, a: 0.4 }); },
    rise() { tone({ f: 85, f1: 190, glide: 0.24, dur: 0.24, v: 0.32 }); hiss({ k: 'p', type: 'lowpass', f: 1500, f1: 180, dur: 0.42, v: 0.32 }); bellFx(0.16, 81, 0.3, 0.05, 0.2); },
    flip() { [74, 78, 81, 86].forEach((m, i) => bellFx(i * 0.05, m, 0.3, 0.08, 0.2)); },
    flipBack() { [81, 78, 74].forEach((m, i) => bellFx(i * 0.05, m, 0.25, 0.07, 0.15)); },
    brushWarn() { tone({ f: 1500, f1: 650, dur: 1.2, v: 0.05, a: 0.25 }); },
    brushDrop() { hiss({ k: 'p', type: 'lowpass', f: 900, f1: 110, dur: 0.28, v: 0.4 }); tone({ f: 150, f1: 48, dur: 0.26, v: 0.32 }); },
  };

  function build(c, live) {
    ctx = c;
    const lim = ctx.createDynamicsCompressor(); lim.threshold.value = -1.5; lim.knee.value = 0; lim.ratio.value = 20; lim.attack.value = 0.002; lim.release.value = 0.08; lim.connect(ctx.destination);
    const clip = ctx.createWaveShaper(), cv = new Float32Array(1025); for (let i = 0; i < 1025; i++) { const x = i / 512 - 1; cv[i] = Math.tanh(x * 1.3) / Math.tanh(1.3); } clip.curve = cv; clip.oversample = '2x'; clip.connect(lim);
    const comp = ctx.createDynamicsCompressor(); comp.threshold.value = -16; comp.knee.value = 8; comp.ratio.value = 3; comp.attack.value = 0.005; comp.release.value = 0.2; comp.connect(clip);
    const hi = ctx.createBiquadFilter(); hi.type = 'highshelf'; hi.frequency.value = 7500; hi.gain.value = 2; hi.connect(comp);
    const lo = ctx.createBiquadFilter(); lo.type = 'lowshelf'; lo.frequency.value = 110; lo.gain.value = 2.5; lo.connect(hi);
    const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 30; hp.connect(lo);
    out = ctx.createGain(); out.gain.value = store.muted ? 0 : 1; out.connect(hp);
    sfx = ctx.createGain(); sfx.gain.value = 0.95; sfx.connect(out);
    musLP = ctx.createBiquadFilter(); musLP.type = 'lowpass'; musLP.frequency.value = 20000; musLP.Q.value = 0.8; musLP.connect(out);
    musDuck = ctx.createGain(); musDuck.connect(musLP);
    mus = ctx.createGain(); mus.gain.value = 0.42; mus.connect(musDuck);
    musWet = ctx.createGain(); musWet.gain.value = 0.42; musEcho = ctx.createGain(); musEcho.gain.value = 0.42;
    const conv = ctx.createConvolver(); conv.buffer = plate(2.2); const vret = ctx.createGain(); vret.gain.value = 0.3; conv.connect(vret); vret.connect(out);
    verb = ctx.createGain(); const vhp = ctx.createBiquadFilter(); vhp.type = 'highpass'; vhp.frequency.value = 240; verb.connect(vhp); vhp.connect(conv);
    echo = ctx.createGain(); const dl = ctx.createDelay(1); dl.delayTime.value = 60 / 116 * 0.75; const fb = ctx.createGain(); fb.gain.value = 0.3; const dlp = ctx.createBiquadFilter(); dlp.type = 'lowpass'; dlp.frequency.value = 2600;
    echo.connect(dl); dl.connect(dlp); dlp.connect(fb); fb.connect(dl); const eret = ctx.createGain(); eret.gain.value = 0.45; dlp.connect(eret); eret.connect(musDuck);
    musWet.connect(verb); musEcho.connect(echo);
    pans = []; for (const p of [-0.7, -0.33, 0, 0.33, 0.7]) { let n; if (ctx.createStereoPanner) { n = ctx.createStereoPanner(); n.pan.value = p; } else n = ctx.createGain(); n.connect(sfx); pans.push(n); }
    NZ.w = noiseBuf('w'); NZ.p = noiseBuf('p'); NZ.b = noiseBuf('b');
    // rolling: a squelchy rumble that pulses faster the quicker you go
    { const s = ctx.createBufferSource(); s.buffer = NZ.b; s.loop = true; rollF = ctx.createBiquadFilter(); rollF.type = 'bandpass'; rollF.frequency.value = 300; rollF.Q.value = 1.1;
      const am = ctx.createGain(); am.gain.value = 0.72; rollLfo = ctx.createOscillator(); rollLfo.frequency.value = 4; const lg = ctx.createGain(); lg.gain.value = 0.28; rollLfo.connect(lg); lg.connect(am.gain);
      rollG = ctx.createGain(); rollG.gain.value = 0; s.connect(rollF); rollF.connect(am); am.connect(rollG); rollG.connect(pans[2]); s.start(); rollLfo.start(); }
    // rain: two decorrelated beds, left and right
    rainG = ctx.createGain(); rainG.gain.value = 0; rainG.connect(sfx);
    for (const p of [0, 4]) { const s = ctx.createBufferSource(); s.buffer = NZ.p; s.loop = true; const h = ctx.createBiquadFilter(); h.type = 'highpass'; h.frequency.value = 800; const l = ctx.createBiquadFilter(); l.type = 'lowpass'; l.frequency.value = 7000; const pn = ctx.createStereoPanner ? ctx.createStereoPanner() : ctx.createGain(); if (pn.pan) pn.pan.value = p ? 0.6 : -0.6; s.connect(h); h.connect(l); l.connect(pn); pn.connect(rainG); s.start(0, p ? 0.9 : 0); }
    { const s = ctx.createBufferSource(); s.buffer = NZ.w; s.loop = true; const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 4200; bp.Q.value = 1.1; sizG = ctx.createGain(); sizG.gain.value = 0; s.connect(bp); bp.connect(sizG); sizG.connect(sfx); s.start(); }
    seqT = T() + 0.1; seqS = 0;
    if (live) timer = setInterval(() => schedule(), 25);
  }
  // the next sound comes from here: panned by where it is relative to you and the camera, and a bit quieter far off
  function at(x, z) {
    if (x == null) { pend = null; return; }
    const dx = x - P.x, dz = z - P.z, dd = Math.hypot(dx, dz); if (dd < 1.5) { pend = null; return; }
    const e = camera.matrixWorld.elements, rl = Math.hypot(e[0], e[2]) || 1, side = (dx * e[0] + dz * e[2]) / rl / dd;
    pend = { p: cl(Math.round(side * 2 + 2), 0, 4), g: cl(1.15 - dd / 22, 0.45, 1) };
    Promise.resolve().then(() => { pend = null; });
  }
  const api = {
    init() {
      if (ctx) { if (ctx.state !== 'running') ctx.resume().catch(() => {}); return; }
      const AC = window.AudioContext || window.webkitAudioContext; if (!AC) return;
      let c; try { c = new AC({ latencyHint: 'interactive' }); } catch (e) { return; }
      build(c, true); if (lastMode !== 'none') { const m = lastMode; lastMode = 'none'; api.music(m); }
    },
    muted(m) { if (ctx) out.gain.setTargetAtTime(m ? 0 : 1, T(), 0.04); },
    suspend(h) { if (!ctx) return; if (h) ctx.suspend().catch(() => {}); else ctx.resume().catch(() => {}); },
    at,
    mood(late, giant, sun, ot) { mood.late = late; mood.giant = giant; mood.sun = sun; mood.ot = ot; },
    music(mode) {
      if (!ctx) { lastMode = mode; return; }
      const t = T(), vol = (v, tau) => { for (const n of [mus, musWet, musEcho]) { n.gain.cancelScheduledValues(t); n.gain.setTargetAtTime(v, t, tau); } };
      musLP.frequency.cancelScheduledValues(t); musLP.frequency.setTargetAtTime(mode === 'pause' ? 650 : 20000, t, mode === 'pause' ? 0.06 : 0.12);
      if (mode === 'pause') vol(MUS_PLAY * 0.7, 0.12);
      else if (mode === 'play') { if (lastMode !== 'pause') { arr = 'play'; seqS = 0; seqT = t + 0.06; } musOn = true; vol(MUS_PLAY, 0.15); }
      else if (mode === 'menu') { if (lastMode !== 'menu') { arr = 'menu'; seqS = 0; seqT = t + 0.1; } musOn = true; vol(MUS_MENU, 0.4); }
      else if (mode === 'end') { musOn = false; vol(0, 0.12); }
      lastMode = mode;
    },
    roll(spd, wide) { if (!ctx) return; const t = T(), on = spd > 0.3; rollG.gain.setTargetAtTime(on ? 0.12 + 0.22 * cl(spd / 6, 0, 1) + 0.1 * (wide || 0) : 0, t, 0.06); rollF.frequency.setTargetAtTime(230 + spd * 60 + (wide || 0) * 160, t, 0.08); rollLfo.frequency.setTargetAtTime(2.5 + spd * 1.1, t, 0.1); },
    rain(k) { if (!ctx) return; mood.rain = k; rainG.gain.setTargetAtTime(0.09 * k, T(), 0.25); },
    sizzle(k) { if (!ctx || mood.sizzle === k) return; mood.sizzle = k; sizG.gain.setTargetAtTime(0.12 * k, T(), 0.05); },
    // test hooks: render into an offline context and pump the sequencer by hand
    _build(c) { build(c, false); },
    _pump(sec) { schedule(sec); },
    _tone(o) { tone(o); }, _hiss(o) { hiss(o); }, _offset(x) { tOff = x; },
  };
  for (const k in fx) api[k] = function () { const pl = pend || CENTER; cur = { p: pl.p, g: pl.g * (LVL[k] || 1) }; pend = null; try { fx[k].apply(null, arguments); } finally { cur = CENTER; } };
  for (const k of ['chargeStart', 'chargeSet', 'chargeStop']) api[k] = fx[k];
  return api;
}
const AU = makeAudio();
