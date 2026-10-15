    // (v257) the first launch's music, written on the theme: its key, its tempo (110.89 a minute), its chords and its main melody, in five
    // stems of one 8-bar loop on one clock (air, keys, low, tops, drive), brought in a layer at a time on the beat as the look comes
    // together. The loop's eight bars are the menu song's bars 9 to 16 (its melody, on the same chords), so at the end a riser leads into a
    // hit on a bar line (v263: voiced on that bar's chord), and on the hit the menu song carries on from that very bar, in time: the intro
    // flows straight into it. It plays through the track bus (the music switch and the pause muffle work on it as on any song); the intro's
    // effects go through the effects bus
    flm: (() => {
      const LOOP = { a: 0.25, b: 17.56444 }, BEAT = 60 / 110.89, BAR = BEAT * 4, LV = 0.21, MENU_AT = 17.627, STEMS = ['air', 'keys', 'low', 'tops', 'drive'];
      // (v263) the menu song's bar 8 starts at MENU_AT in its file (measured against the intro's own beat: 22 ms on from the kick-onset
      // estimate), so the loop's bar e is the song's bar 9 + e at MENU_AT + (1 + e) bars. The hit is one sprite: the riser and impact
      // (imp, the hit a bar in), then the pitched part on each of the loop's chords (each starting HIT_LEAD before its hit)
      const HIT = { imp: [0.0, 6.36429], dm: [6.51429, 4.8], am: [11.46429, 4.8], bb: [16.41429, 4.8], e: [21.36429, 4.8], f: [26.31429, 4.8] }, HIT_LEAD = 0.6;
      const CHORD = ['dm', 'am', 'bb', 'e', 'dm', 'am', 'f', 'e'];
      const FX = { wobble: [0, 0.524], tip: [0.824, 0.55], pour: [1.673, 3.919], eyes: [5.893, 0.393], form: [6.585, 1.255], sparkle: [8.14, 0.8], tumble: [9.24, 2.326] };
      // each layer: how loud each stem is (the air steps back a little as the rest come in)
      const LAY = [[1, 0, 0, 0, 0], [0.9, 1, 0, 0, 0], [0.8, 1, 1, 0, 0], [0.7, 1, 1, 1, 0], [0.55, 1, 1, 1, 1]];
      // (v267) the desert's own air under it all: a low wind over the sand, sand grains hissing, a soft gust now and then (Ludo.ai takes,
      // stitched into an 18.3 s loop that wraps seamlessly, held to an even level; tools/desert_wind.py). On the effects bus, so the
      // sound-effects switch silences it; in with the intro, out as the iris closes on the desert. The file is the loop with 0.4 s of
      // itself either side, so the loop points hold whatever the decoder's start offset
      const WIND = { a: 0.4, b: 18.7, lv: 0.13 };
      const B = {}, M = { on: false, lay: 0, S: null, W: null, gone: false };
      const dec = (bytes, done) => { let dc = ctx; if (!dc) { const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext; if (!OAC) return; try { dc = new OAC(2, 1, 44100); } catch (e) { return; } }
        try { const p = dc.decodeAudioData(bytes.slice(0), b => { if (!M.gone) done(b); }, () => {}); if (p && p.catch) p.catch(() => {}); } catch (e) {} };
      const get = (url, done) => fetch(url).then(r => r.ok ? r.arrayBuffer() : null).then(b => { if (b) dec(b, done); }).catch(() => {});
      const lvlOf = (k, n) => LAY[n][STEMS.indexOf(k)] * LV;
      // a stem joins the clock the moment it has decoded (silent unless its layer is in)
      function node(k) {
        const S = M.S, R = B[k]; if (!S || S.n[k] || !R) return;
        const src = ctx.createBufferSource(), g = ctx.createGain(); src.buffer = R; src.loop = true; src.loopStart = LOOP.a; src.loopEnd = Math.min(LOOP.b, R.duration);
        src.connect(g); g.connect(S.bus); g.gain.value = 0;
        const t = Math.max(T() + 0.05, S.t0), len = LOOP.b - LOOP.a, off = LOOP.a + ((t - S.t0) % len), v = lvlOf(k, M.lay);
        if (v > 0) { g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(v, t + (k === 'air' ? 2.4 : BEAT)); }
        src.start(t, off); S.n[k] = { src, g };
      }
      function wind() {
        if (!M.on || M.W || M.gone || !ctx || !B.wind || !sfx) return;
        const src = ctx.createBufferSource(), g = ctx.createGain(), t = T() + 0.05; src.buffer = B.wind; src.loop = true; src.loopStart = WIND.a; src.loopEnd = Math.min(WIND.b, B.wind.duration);
        g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(WIND.lv, t + 3); src.connect(g); g.connect(sfx); src.start(t, WIND.a); M.W = { src, g };
      }
      const windOut = (at, tc) => { const W = M.W; if (!W || !ctx) return; M.W = null; const g = W.g.gain, t = Math.max(T(), at); g.cancelScheduledValues(T()); g.setValueAtTime(g.value, T()); g.setTargetAtTime(0, t, tc); try { W.src.stop(t + tc * 7); } catch (e) {} };
      function begin() {
        if (M.S || !M.on || !ctx || !B.air || !trkBus) return;
        const bus = ctx.createGain(); bus.connect(trkBus); M.S = { t0: T() + 0.1, bus, n: {} };
        for (const k of STEMS) node(k);
      }
      // the next beat (or bar) from now on the loop's clock
      const next = (unit, lead) => { const S = M.S, t = T() + (lead || 0.04); if (!S) return t; return S.t0 + Math.ceil((t - S.t0) / unit) * unit; };
      function apply() {
        const S = M.S; if (!S) return; const t = next(BEAT);
        for (const k in S.n) { const g = S.n[k].g.gain; g.cancelScheduledValues(t); g.setTargetAtTime(lvlOf(k, M.lay), t, BEAT * 0.35); }
      }
      // the menu song from bar 9 + e (the bar the intro's loop had reached), starting at t on that bar's downbeat: the same tempo, the same
      // chord, the melody carrying on where the intro's had got to
      function menuAt(t, e) {
        const R = TRK.menu; if (!R || !R.buf) { setTimeout(() => { lastMode = 'none'; api.music('menu'); }, Math.max(0, (t - T()) * 1000)); return; }
        trkStop(0.3); const src = ctx.createBufferSource(), g = ctx.createGain(), lvl = R.k * TRK_LVL.menu;
        src.buffer = R.buf; src.loop = true; src.loopStart = R.a; src.loopEnd = Math.min(R.b, R.buf.duration);
        g.gain.setValueAtTime(0, t - 0.01); g.gain.linearRampToValueAtTime(lvl, t + 0.02); src.connect(g); g.connect(trkBus); const off = MENU_AT + (1 + e) * BAR; src.start(t - 0.01, off - 0.01);
        trk = { key: 'menu', src, g, t0: t - off }; M.hand = { e, off, at: t }; trkWant = 'menu'; trkPend = null; musOn = false; mus.gain.cancelScheduledValues(t); mus.gain.setTargetAtTime(0, t, 0.1); lastMode = 'menu';
      }
      return {
        // fetch and decode (the air first: the music can begin as soon as it's in); nothing here is asked for unless the intro runs
        load() { if (M.loaded || typeof fetch !== 'function' || location.protocol === 'file:') return; M.loaded = true; trkDecode('menu');
          get(SFX_BASE + 'intro_wind.mp3', b => { B.wind = b; wind(); });
          get(MUSIC_BASE + 'intro_air.mp3', b => { B.air = b; begin();
            for (const k of STEMS.slice(1)) get(MUSIC_BASE + 'intro_' + k + '.mp3', b2 => { B[k] = b2; node(k); });
            get(MUSIC_BASE + 'intro_sting.mp3', b2 => { B.sting = b2; }); get(SFX_BASE + 'intro_fx.mp3', b2 => { B.fx = b2; }); });
          // (going to the background lets go of every song not playing (v309's memTrim), the menu song with them, and the hand-over
          // carries on in it: back on screen before the hand-over, it's decoded again)
          document.addEventListener('visibilitychange', () => { if (!document.hidden && !M.gone && !M.sung && TRK.menu && !TRK.menu.buf) trkDecode('menu'); }); },
        play() { M.on = true; if (ctx) { begin(); wind(); } },
        wake() { if (M.on && !M.S) begin(); if (M.on && !M.W) wind(); },
        // (v260) the sound started afresh on a new context: the stems come back on it, with the layers that were in
        renew() { M.S = null; M.W = null; if (M.on) { begin(); wind(); } },
        layer(n) { n = Math.max(0, Math.min(LAY.length - 1, n | 0)); if (n <= M.lay) return; M.lay = n; apply(); },
        get lay() { return M.lay; },
        get hand() { return M.hand || null; }, // (v263, for tests: the bar it handed over on and the song's offset)
        get wind() { return M.W ? M.W.g.gain.value : 0; }, // (v267, for tests: the wind's level now, 0 when it isn't playing)
        // how many beats into the loop's clock it is (null when it isn't playing): the character nods along to it
        beat() { const S = M.S; return S && ctx ? (T() - S.t0) / BEAT : null; },
        // one of the intro's own effects (false if it isn't in yet, so the caller can use one of the game's)
        fx(k, v) { const R = B.fx, s = FX[k]; if (!ctx || !R || !s || !sfx || ctx.state !== 'running') return false;
          try { const src = ctx.createBufferSource(), g = ctx.createGain(); src.buffer = R; g.gain.value = (v == null ? 1 : v) * 0.9; src.connect(g); g.connect(sfx); src.start(T() + 0.005, s[0], s[1]); } catch (e) { return false; } return true; },
        // the reveal: the hit on the first bar line at least lead seconds away (its riser a bar before, its chord that bar's), the loop let
        // go on it, and on it the menu song from the same bar. How long until the hit, in seconds
        sting(lead) {
          M.on = false; M.sung = true; if (!ctx || ctx.state !== 'running') { windOut(T(), 0.1); return lead; }
          const S = M.S, hit = S ? next(BAR, lead) : T() + lead, e = S ? ((Math.round((hit - S.t0) / BAR) % 8) + 8) % 8 : 0;
          windOut(hit - 0.45, 0.3); // (the wind goes as the iris closes on the desert)
          // (one part of the sprite, from `at` seconds: started partway in if that's already gone by)
          const part = (k, at) => { const sg = HIT[k]; if (!sg) return; const src = ctx.createBufferSource(), g = ctx.createGain(); src.buffer = B.sting; g.gain.value = LV * 1.2; src.connect(g); g.connect(trkBus);
            const late = Math.max(0, T() - at); if (late < sg[1]) src.start(at + late, sg[0] + late, sg[1] - late); };
          if (B.sting && trkBus) { part('imp', hit - BAR); part(CHORD[e], hit - HIT_LEAD); }
          if (S) { for (const k in S.n) { const n = S.n[k]; n.g.gain.cancelScheduledValues(T()); n.g.gain.setTargetAtTime(n.g.gain.value * 1.08, hit - BAR, BEAT); n.g.gain.setTargetAtTime(0, hit - 0.01, 0.04); try { n.src.stop(hit + 0.5); } catch (e) {} } M.S = null; }
          menuAt(hit, e); return Math.max(0, hit - T());
        },
        end() { M.on = false; M.gone = true; windOut(T(), 0.15); const S = M.S; if (S && ctx) for (const k in S.n) { const n = S.n[k]; n.g.gain.cancelScheduledValues(T()); n.g.gain.setTargetAtTime(0, T(), 0.15); try { n.src.stop(T() + 0.8); } catch (e) {} }
          M.S = null; setTimeout(() => { for (const k in B) delete B[k]; }, 3000); },
      };
    })(),
