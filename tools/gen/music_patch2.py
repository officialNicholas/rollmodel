P = '/home/claude/paint-the-canvas.html'
s = open(P).read()
a = s.index("  // the drum kit, synthesized once sample by sample")
b = s.index("  // play a kit sample into a music bus")
new_kit = r"""  // the drum kit, synthesized once sample by sample: each hit can be layered, saturated and roomy and still cost one node
  // to play. Live, it renders one drum at a time between frames (menu drums first) so starting the sound never stalls
  function renderKit(sync) {
    const sr = ctx.sampleRate, NT = new Float32Array(1 << 16); for (let i = 0; i < NT.length; i++) NT[i] = Math.random() * 2 - 1;
    let ni = 0; const N = () => NT[(ni = (ni + 1) & 65535)];
    const mk = (sec, ch) => ctx.createBuffer(ch || 1, Math.max(2, Math.floor(sr * sec)), sr);
    const dk = tau => Math.exp(-1 / (tau * sr));   // per-sample decay
    function bq(type, f, q) {   // a biquad, one sample at a time
      const w = 2 * Math.PI * Math.min(f, sr * 0.45) / sr, cs = Math.cos(w), al = Math.sin(w) / (2 * q), a0 = 1 + al;
      const b0 = type === 'lp' ? (1 - cs) / 2 : type === 'hp' ? (1 + cs) / 2 : al, b1 = type === 'lp' ? 1 - cs : type === 'hp' ? -(1 + cs) : 0, b2 = type === 'bp' ? -al : b0;
      const B0 = b0 / a0, B1 = b1 / a0, B2 = b2 / a0, A1 = -2 * cs / a0, A2 = (1 - al) / a0; let x1 = 0, x2 = 0, y1 = 0, y2 = 0;
      return x => { const y = B0 * x + B1 * x1 + B2 * x2 - A1 * y1 - A2 * y2; x2 = x1; x1 = x; y2 = y1; y1 = y; return y; };
    }
    function room(d, c, amt) {   // a few early reflections, different on each side, so a dry hit sits in a room
      const src = d.slice(), lp = bq('lp', 4500, 0.7), k = (c ? [11.7, 19.3, 33.1, 47] : [14.2, 22.9, 29.7, 43]).map(ms => Math.floor(ms * sr / 1000));
      for (let i = 0; i < d.length; i++) d[i] += lp(((i >= k[0] ? src[i - k[0]] * 0.32 : 0) + (i >= k[1] ? src[i - k[1]] * 0.22 : 0) + (i >= k[2] ? src[i - k[2]] * 0.13 : 0) + (i >= k[3] ? src[i - k[3]] * 0.08 : 0)) * amt);
    }
    function fin(b, pk) {   // normalize, and fade the last few ms so nothing clicks
      let m = 0; for (let c = 0; c < b.numberOfChannels; c++) { const d = b.getChannelData(c); for (let i = 0; i < d.length; i++) { const x = d[i] < 0 ? -d[i] : d[i]; if (x > m) m = x; } }
      const k = pk / (m || 1), f = Math.floor(sr * 0.005);
      for (let c = 0; c < b.numberOfChannels; c++) { const d = b.getChannelData(c), n = d.length; for (let i = 0; i < n; i++) d[i] *= k * (i >= n - f ? (n - i) / f : 1); }
      return b;
    }
    // six detuned square waves: the classic drum machine metal
    function metalSrc(F) { const ph = new Float64Array(6); for (let k = 0; k < 6; k++) ph[k] = Math.random(); return () => { let m = 0; for (let k = 0; k < 6; k++) { let p = ph[k] + F[k]; if (p >= 1) p -= 1; ph[k] = p; m += p < 0.5 ? 1 : -1; } return m; }; }
    function metal(sec, tau, ch) {
      const b = mk(sec, ch), kd = dk(tau), att = sr * 0.0005;
      for (let c = 0; c < (ch || 1); c++) {
        const d = b.getChannelData(c), ms = metalSrc([205.3, 304.4, 369.6, 522.7, 540, 800].map(x => x * (1.72 + 0.02 * c) / sr)), bp = bq('bp', 9800, 1), hp = bq('hp', 7000, 0.7), hp2 = bq('hp', 7000, 0.7);
        let e = 1;
        for (let i = 0; i < d.length; i++) { d[i] = hp2(hp(bp(ms() * 0.11 + N() * 0.42))) * (i < att ? i / att : 1) * e; e *= kd; }
      }
      return fin(b, 0.85);
    }
    const crash = mk(2, 2);
    function crashSide(c) {
      const d = crash.getChannelData(c), ms = metalSrc([245, 321, 397, 515, 607, 781].map(x => x * (2.04 + 0.035 * c) / sr)), hp = bq('hp', 4200, 0.6), bp = bq('bp', 7200, 0.5), lp = bq('lp', 12500, 0.7), k1 = dk(0.07), k2 = dk(0.6), att = sr * 0.0015;
      let e1 = 0.4, e2 = 0.6;
      for (let i = 0; i < d.length; i++) { const x = ms() * 0.08 + N() * 0.6; d[i] = lp(hp(x) * 0.55 + bp(x) * 0.75) * (i < att ? i / att : 1) * (e1 + e2); e1 *= k1; e2 *= k2; }
    }
    const jobs = [
      // kick: a sine that drops from a punchy 250 Hz to a 46 Hz boom, saturated so a phone speaker hears it, plus a click
      () => { const b = mk(0.48), d = b.getChannelData(0), hp = bq('hp', 2400, 0.8), k1 = dk(0.02), k2 = dk(0.1), k3 = dk(0.125), kc = dk(0.003), hold = Math.floor(sr * 0.03), att = sr * 0.0012;
        let ph = 0, e1 = 1, e2 = 1, env = 1, ec = 1;
        for (let i = 0; i < d.length; i++) {
          ph += 2 * Math.PI * (46 + 200 * e1 + 28 * e2) / sr; e1 *= k1; e2 *= k2; if (i >= hold) env *= k3;
          d[i] = Math.tanh(Math.sin(ph) * env * (i < att ? i / att : 1) * 2) * 0.85 + hp(N()) * ec * 0.45; ec *= kc;
        }
        SM.kick = fin(b, 0.95); },
      // shaker: a soft swell of bright noise
      () => { const b = mk(0.13), d = b.getChannelData(0), bp = bq('bp', 7400, 1.3), hp = bq('hp', 4000, 0.7), att = sr * 0.013, kd = dk(0.024); let e = 1;
        for (let i = 0; i < d.length; i++) { const a = i < att ? i / att : 1; d[i] = hp(bp(N())) * a * a * e; if (i >= att) e *= kd; }
        SM.shaker = fin(b, 0.8); },
      // finger snap: a tight crack and a click in a small room
      () => { const b = mk(0.32, 2), k1 = dk(0.01), k2 = dk(0.022), k3 = dk(0.0045), w = 2 * Math.PI * 1720 / sr;
        for (let c = 0; c < 2; c++) {
          const d = b.getChannelData(c), bp = bq('bp', 2700, 2.4), bp2 = bq('bp', 1300, 1.4); let e1 = 1, e2 = 1, e3 = 1;
          for (let i = 0; i < d.length; i++) { d[i] = bp(N()) * e1 * 1.3 + bp2(N()) * e2 * 0.45 + Math.sin(w * i) * e3 * 0.25; e1 *= k1; e2 *= k2; e3 *= k3; }
          room(d, c, 1.2);
        }
        SM.snap = fin(b, 0.85); },
      // clap: four hands a few ms apart and a little body under them, in a small room, slightly different left and right
      () => { const b = mk(0.5, 2), kq = dk(0.0045), kt = dk(0.08), kb = dk(0.028), w = 2 * Math.PI * 188 / sr;
        for (let c = 0; c < 2; c++) {
          const d = b.getChannelData(c), bp = bq('bp', 1180 + 70 * c, 1.15), hp = bq('hp', 650, 0.7), tk = [0, 0.0102 + 0.0011 * c, 0.0198, 0.0302 + 0.0008 * c].map(x => Math.floor(x * sr));
          let e0 = 0, e3 = 0, eb = 1;
          for (let i = 0; i < d.length; i++) {
            if (i === tk[0] || i === tk[1] || i === tk[2]) e0 += 0.8; if (i === tk[3]) e3 = 1;
            d[i] = hp(bp(N())) * (e0 + e3) + Math.sin(w * i) * eb * 0.12; e0 *= kq; e3 *= kt; eb *= kb;
          }
          room(d, c, 1);
        }
        SM.clap = fin(b, 0.9); },
      () => { SM.hat = metal(0.11, 0.016); },
      () => { SM.ohat = metal(0.5, 0.17, 2); },
      // tom: a sine that settles from a thump to its note, with a stick on the skin
      () => { const b = mk(0.5), d = b.getChannelData(0), bp = bq('bp', 1500, 1), k1 = dk(0.022), k2 = dk(0.14), k3 = dk(0.011); let ph = 0, e1 = 1, e2 = 1, e3 = 1;
        for (let i = 0; i < d.length; i++) { ph += 2 * Math.PI * 150 * (1 + 0.6 * e1) / sr; d[i] = Math.tanh(Math.sin(ph) * e2 * 1.7) + bp(N()) * e3 * 0.5; e1 *= k1; e2 *= k2; e3 *= k3; }
        SM.tom = fin(b, 0.9); },
      () => crashSide(0),
      () => { crashSide(1); SM.crash = fin(crash, 0.85); },
      // the same crash backwards: a swell that sucks into the next downbeat
      () => { const r = mk(1.1, 2), n = r.length, f = sr * 0.3;
        for (let c = 0; c < 2; c++) { const s = SM.crash.getChannelData(c), d = r.getChannelData(c); for (let i = 0; i < n; i++) d[i] = s[n - 1 - i] * (i < f ? i / f : 1); }
        SM.rev = fin(r, 0.85); },
    ];
    if (sync) { for (const j of jobs) j(); return; }
    let i = 0; const next = () => { if (ctx && i < jobs.length) { try { jobs[i++](); } finally { setTimeout(next, 0); } } }; next();
  }
"""
s = s[:a] + new_kit + s[b:]
old = "    SM = renderKit();\n  }"
assert s.count(old) == 1
s = s.replace(old, "    SM = {}; renderKit(!live);\n  }")
old = "  function buildMusic() {"; assert s.count(old) == 1; s = s.replace(old, "  function buildMusic(live) {")
old = "    buildMusic();"; assert s.count(old) == 1; s = s.replace(old, "    buildMusic(live);")
open(P, 'w').write(s); print('ok')
