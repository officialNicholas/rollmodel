    // (v257) the first launch's music, written on the theme: its key, its tempo (110.89 a minute), its chords and its main melody, in five
    // stems of one 8-bar loop on one clock (air, keys, low, tops, drive), brought in a layer at a time on the beat as the look comes
    // together. At the end a riser into the sting (the E major hit the theme's A minor answers), and a bar later the menu song comes in on
    // the downbeat of its eighth bar, where its melody starts, so it carries on in time. It plays through the track bus (the music switch
    // and the pause muffle work on it as on any song); the intro's effects go through the effects bus
    flm: (() => {
      const LOOP = { a: 0.25, b: 17.56444 }, BEAT = 60 / 110.89, BAR = BEAT * 4, LV = 0.21, MENU_AT = 17.605, STEMS = ['air', 'keys', 'low', 'tops', 'drive'];
      const FX = { wobble: [0, 0.524], tip: [0.824, 0.55], pour: [1.673, 3.919], eyes: [5.893, 0.393], form: [6.585, 1.255], sparkle: [8.14, 0.8], tumble: [9.24, 2.326] };
      // each layer: how loud each stem is (the air steps back a little as the rest come in)
      const LAY = [[1, 0, 0, 0, 0], [0.9, 1, 0, 0, 0], [0.8, 1, 1, 0, 0], [0.7, 1, 1, 1, 0], [0.55, 1, 1, 1, 1]];
      const B = {}, M = { on: false, lay: 0, S: null, gone: false };
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
      // the menu song from its eighth bar, starting at t (in time with the intro: they share the tempo)
      function menuAt(t) {
        const R = TRK.menu; if (!R || !R.buf) { setTimeout(() => { lastMode = 'none'; api.music('menu'); }, Math.max(0, (t - T()) * 1000)); return; }
        trkStop(0.3); const src = ctx.createBufferSource(), g = ctx.createGain(), lvl = R.k * TRK_LVL.menu;
        src.buffer = R.buf; src.loop = true; src.loopStart = R.a; src.loopEnd = Math.min(R.b, R.buf.duration);
        g.gain.setValueAtTime(0, t - 0.01); g.gain.linearRampToValueAtTime(lvl, t + 0.02); src.connect(g); g.connect(trkBus); src.start(t - 0.01, MENU_AT - 0.01);
        trk = { key: 'menu', src, g, t0: t - MENU_AT }; trkWant = 'menu'; trkPend = null; musOn = false; mus.gain.cancelScheduledValues(t); mus.gain.setTargetAtTime(0, t, 0.1); lastMode = 'menu';
      }
      return {
        // fetch and decode (the air first: the music can begin as soon as it's in); nothing here is asked for unless the intro runs
        load() { if (M.loaded || typeof fetch !== 'function' || location.protocol === 'file:') return; M.loaded = true; trkDecode('menu');
          get(MUSIC_BASE + 'intro_air.mp3', b => { B.air = b; begin();
            for (const k of STEMS.slice(1)) get(MUSIC_BASE + 'intro_' + k + '.mp3', b2 => { B[k] = b2; node(k); });
            get(MUSIC_BASE + 'intro_sting.mp3', b2 => { B.sting = b2; }); get(SFX_BASE + 'intro_fx.mp3', b2 => { B.fx = b2; }); }); },
        play() { M.on = true; if (ctx) begin(); },
        wake() { if (M.on && !M.S) begin(); },
        layer(n) { n = Math.max(0, Math.min(LAY.length - 1, n | 0)); if (n <= M.lay) return; M.lay = n; apply(); },
        get lay() { return M.lay; },
        // one of the intro's own effects (false if it isn't in yet, so the caller can use one of the game's)
        fx(k, v) { const R = B.fx, s = FX[k]; if (!ctx || !R || !s || !sfx || ctx.state !== 'running') return false;
          try { const src = ctx.createBufferSource(), g = ctx.createGain(); src.buffer = R; g.gain.value = (v == null ? 1 : v) * 0.9; src.connect(g); g.connect(sfx); src.start(T() + 0.005, s[0], s[1]); } catch (e) { return false; } return true; },
        // the reveal: the hit on the first bar line at least lead seconds away (its riser a bar before), the loop let go on it, and the menu
        // song a bar after. How long until the hit, in seconds
        sting(lead) {
          M.on = false; if (!ctx || ctx.state !== 'running') return lead;
          const S = M.S, hit = S ? next(BAR, lead) : T() + lead;
          if (B.sting && trkBus) { const src = ctx.createBufferSource(), g = ctx.createGain(); src.buffer = B.sting; g.gain.value = LV * 1.2; src.connect(g); g.connect(trkBus); const st = hit - BAR;
            if (st >= T()) src.start(st); else src.start(T(), T() - st); }
          if (S) { for (const k in S.n) { const n = S.n[k]; n.g.gain.cancelScheduledValues(T()); n.g.gain.setTargetAtTime(n.g.gain.value * 1.08, hit - BAR, BEAT); n.g.gain.setTargetAtTime(0, hit - 0.01, 0.04); try { n.src.stop(hit + 0.5); } catch (e) {} } M.S = null; }
          menuAt(hit + BAR); return Math.max(0, hit - T());
        },
        end() { M.on = false; M.gone = true; const S = M.S; if (S && ctx) for (const k in S.n) { const n = S.n[k]; n.g.gain.cancelScheduledValues(T()); n.g.gain.setTargetAtTime(0, T(), 0.15); try { n.src.stop(T() + 0.8); } catch (e) {} }
          M.S = null; setTimeout(() => { for (const k in B) delete B[k]; }, 3000); },
      };
    })(),
