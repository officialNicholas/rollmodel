# wire the designed sound sheets into the game's audio engine (with the synth kept as the fallback), plus the slime's voice
import json, sys
p = '/home/claude/paint-the-canvas.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:140]); s = s.replace(old, new)

# 1. start downloading the sheets with the page, next to the menu song
rep("""window.__menuSong = (() => { try { if (location.protocol === 'file:' || typeof fetch !== 'function') return null; return fetch((window.MUSIC_BASE || 'music/') + 'menu.mp3').then(r => r.ok ? r.arrayBuffer() : null).catch(() => null); } catch (e) { return null; } })();
</script>""", """window.__menuSong = (() => { try { if (location.protocol === 'file:' || typeof fetch !== 'function') return null; return fetch((window.MUSIC_BASE || 'music/') + 'menu.mp3').then(r => r.ok ? r.arrayBuffer() : null).catch(() => null); } catch (e) { return null; } })();
// and the two sheets of sound effects
window.__sfxSheets = (() => { try { if (location.protocol === 'file:' || typeof fetch !== 'function') return null; const b = window.SFX_BASE || 'sfx/', f = n => fetch(b + n + '.mp3').then(r => r.ok ? r.arrayBuffer() : null).catch(() => null); return { m: f('m'), s: f('s') }; } catch (e) { return null; } })();
</script>""")

# 2. the sheet loader and player, just before the effects
rep("""  // ---- effects ----
  const fx = {""", """  // ---- designed effects: every effect was built offline (layered, processed, mixed and mastered) and packed into two sheets, one mono
  // and one stereo, fetched with the page and decoded while the menu is up. A sound has a few takes: one is picked at random (never the
  // same one twice running) and nudged in pitch, so repeats don't sound copied. Until the sheets are in (or if they can't be had), the
  // synth versions below play instead ----
  const SFXI = /*SFXI*/{}/*SFXI_END*/;
  const SFX_BASE = (typeof window !== 'undefined' && window.SFX_BASE) || 'sfx/';
  const SB = { m: null, s: null, off: { m: 0, s: 0 }, bytes: {}, busy: {}, fail: {}, last: {} };
  let LP = null, voxT = -9;
  function sbFetch(ch) {
    if (SB[ch] || SB.bytes[ch] || SB.busy[ch] || SB.fail[ch] || !SFXI.sheets) return;
    const pre = typeof window !== 'undefined' && window.__sfxSheets && window.__sfxSheets[ch];
    if (pre) { window.__sfxSheets[ch] = null; SB.busy[ch] = true; pre.then(b => { SB.busy[ch] = false; if (b) { SB.bytes[ch] = b; sbDecode(ch); } else sbFetch(ch); }, () => { SB.busy[ch] = false; sbFetch(ch); }); return; }
    if (typeof fetch !== 'function' || location.protocol === 'file:') { SB.fail[ch] = true; return; }
    SB.busy[ch] = true;
    fetch(SFX_BASE + ch + '.mp3').then(r => { if (!r.ok) throw new Error('missing'); return r.arrayBuffer(); }).then(b => { SB.busy[ch] = false; SB.bytes[ch] = b; sbDecode(ch); }).catch(() => { SB.busy[ch] = false; SB.fail[ch] = true; });
  }
  function sbDecode(ch) {
    if (SB[ch] || SB.busy[ch] || !SB.bytes[ch]) return;
    let dc = ctx; if (!dc) { const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext; if (!OAC) return; try { dc = new OAC(2, 1, 48000); } catch (e) { return; } }
    SB.busy[ch] = true;
    const ok = b => { SB.busy[ch] = false; SB.bytes[ch] = null; sbReady(ch, b); }, bad = () => { SB.busy[ch] = false; SB.bytes[ch] = null; SB.fail[ch] = true; };
    try { const pr = dc.decodeAudioData(SB.bytes[ch].slice(0), ok, bad); if (pr && pr.catch) pr.catch(bad); } catch (e) { bad(); }
  }
  // each sheet opens with a click at a known time: where it lands after decoding says how far the decoder shifted everything
  function sbReady(ch, b) {
    if (!b || !SFXI.sheets) return;
    const d = b.getChannelData(0), sr = b.sampleRate, lim = Math.min(d.length, Math.floor(sr * 0.3)); let i = 0; while (i < lim && Math.abs(d[i]) < 0.45) i++;
    SB.off[ch] = i < lim ? i / sr - SFXI.sheets[ch].mk : 0; SB[ch] = b;
    if (ctx) sbLoops();
  }
  function sbLoad() { sbFetch('m'); sbFetch('s'); }
  // play one take of a sound: o.v level, o.rate pitch, o.vary random pitch spread, o.d delay, o.p a stereo spot (else where it was heard from)
  function P_(name, o) {
    const e = SFXI.snd && SFXI.snd[name]; if (!e || !ctx) return false;
    const sh = e[0], buf = SB[sh]; if (!buf) return false;
    o = o || {};
    const tk = e[1], n = tk.length; let i = (Math.random() * n) | 0;
    if (n > 1 && SB.last[name] === i) i = (i + 1 + ((Math.random() * (n - 1)) | 0)) % n;
    SB.last[name] = i;
    const t = T() + Math.max(0, o.d || 0) + 0.004, src = ctx.createBufferSource(), g = ctx.createGain(), vr = o.vary == null ? 0.035 : o.vary;
    src.buffer = buf; src.playbackRate.value = (o.rate || 1) * (1 + vr * (Math.random() * 2 - 1));
    g.gain.value = (o.v == null ? 1 : o.v) * (e[2] || 1) * (o.raw ? 1 : cur.g0);
    src.connect(g); g.connect(pans[o.p !== undefined ? o.p : cur.p] || sfx);
    try { src.start(t, Math.max(0, tk[i][0] + SB.off[sh]), tk[i][1]); } catch (err) { return false; }
    return true;
  }
  // the running sounds (rolling, the roller, rain, a sizzle) move over to their recordings once the sheets are in
  function loopSrc(name) {
    const e = SFXI.snd && SFXI.snd[name]; if (!e || !SB[e[0]] || !ctx) return null;
    const sh = e[0], tk = e[1][0], src = ctx.createBufferSource(), g = ctx.createGain(); g.gain.value = 0;
    src.buffer = SB[sh]; src.loop = true; src.loopStart = Math.max(0, tk[0] + SB.off[sh]); src.loopEnd = src.loopStart + tk[1];
    src.connect(g); src.start(T() + 0.01, src.loopStart + Math.random() * tk[1] * 0.9);
    return { src, g, k: e[2] || 1 };
  }
  function sbLoops() {
    if (!ctx || !pans.length) return; LP = LP || {};
    for (const [k, to] of [['roll', 2], ['roller', 2], ['rain', -1], ['sizzle', 2]]) { if (LP[k]) continue; const L = loopSrc(k); if (!L) continue; LP[k] = L; L.g.connect(to < 0 ? sfx : pans[to]); }
    if (LP.rain) rainG.gain.value = 0; if (LP.sizzle) sizG.gain.value = 0;
  }

  // ---- effects (the synth versions) ----
  const fx = {""")

# 3. the beach ball gets its own sound (the synth falls back to the plop)
rep("""    plop() { hiss({ k: 'p', type: 'lowpass', f: 1300, f1: 300, dur: 0.12, v: 0.16 }); tone({ f: 330 + Math.random() * 120, f1: 160, glide: 0.07, dur: 0.08, v: 0.07 }); },""",
    """    plop() { hiss({ k: 'p', type: 'lowpass', f: 1300, f1: 300, dur: 0.12, v: 0.16 }); tone({ f: 330 + Math.random() * 120, f1: 160, glide: 0.07, dur: 0.08, v: 0.07 }); },
    ball() { fx.plop(); },""")

# 4. charging: the stretched rubber band from the sheet when it's there
rep("""    chargeStart() {
      if (!ctx || chA) return; const g = ctx.createGain(); g.gain.value = 0;""", """    chargeStart() {
      if (!ctx || chA) return;
      { const L = loopSrc('charge'); if (L) { L.g.connect(pans[2]); chA = { L }; return; } }
      const g = ctx.createGain(); g.gain.value = 0;""")
rep("""    chargeSet(c) { if (!chA) return; const t = T(); chA.f.frequency""", """    chargeSet(c) { if (!chA) return; const t = T(); if (chA.L) { chA.L.src.playbackRate.setTargetAtTime(0.7 + 0.85 * c, t, 0.04); chA.L.g.gain.setTargetAtTime(c > 0.02 ? (0.35 + 0.65 * c) * chA.L.k : 0, t, 0.03); return; } chA.f.frequency""")
rep("""    chargeStop() { if (!chA) return; const a = chA; chA = null; const t = T(); a.g.gain""", """    chargeStop() { if (!chA) return; const a = chA; chA = null; const t = T(); if (a.L) { a.L.g.gain.setTargetAtTime(0, t, 0.02); try { a.L.src.stop(t + 0.15); } catch (e) {} return; } a.g.gain""")

# 5. the sample versions, tried first; each returns true if it played
rep("""  function build(c, live) {
    ctx = c;""", """  // the designed versions: each returns true when it played, otherwise the synth version above plays
  const sx = {
    go() { if (!P_('go', { vary: 0 })) return false; duck(0.5, 1.2); return true; },
    ui() { return P_('ui', { vary: 0.02 }); },
    nope() { return P_('nope', { vary: 0.015 }); },
    jump() { return P_('jump'); },
    land(k) { k = cl(k || 0, 0, 1); return P_(k > 0.5 ? 'land_h' : 'land_s', { v: 0.6 + 0.5 * k }); },
    splat(k) { k = cl(k || 0.5, 0.2, 1.6); return P_(k < 0.6 ? 'splat_s' : k < 1.1 ? 'splat_m' : 'splat_l', { v: 0.75 + 0.25 * Math.min(1, k) }); },
    slam() { if (!P_('slam')) return false; duck(0.45, 0.6); return true; },
    quake() { if (!P_('quake', { vary: 0.02 })) return false; duck(0.75, 1.4); return true; },
    burst(v) { v = v || 1; if (!P_('burst', { v })) return false; duck(0.35 * v, 0.4); return true; },
    fling(c) { c = cl(c || 0, 0, 1); return P_(c < 0.35 ? 'fling_s' : c < 0.7 ? 'fling_m' : 'fling_l', { v: 0.8 + 0.3 * c }); },
    whoosh() { return P_('whoosh'); },
    swish() { return P_('swish'); },
    rocket() { return P_('rocket', { vary: 0.02 }); },
    alert() { return P_('alert', { vary: 0 }); },
    dash() { return P_('dash'); },
    brake() { return P_('brake'); },
    notch(i) { return P_('notch' + Math.min(3, Math.max(1, i | 0)), { vary: 0 }); },
    release() { return P_('release'); },
    enter() { return P_('enter'); },
    glug(p) { return P_('glug', { rate: 0.85 + 0.45 * cl(p || 0, 0, 1), vary: 0.04 }); },
    pop() { return P_('pop', { vary: 0.04 }); },
    power() { return P_('power', { vary: 0 }); },
    orb() { return P_('orb', { vary: 0 }); },
    grow() { if (!P_('grow', { vary: 0 })) return false; duck(0.45, 0.9); return true; },
    shrink() { return P_('shrink'); },
    die(r) { if (!P_('die')) return false; if (r === 'sun') P_('die_sun'); else if (r === 'pound') P_('die_pound'); else if (r === 'garlic' || r === 'brush' || r === 'dry') P_('die_dry'); return true; },
    fall() { return P_('fall', { vary: 0.02 }); },
    squish() { return P_('squish'); },
    bonk(k) { k = cl(k || 0, 0, 1); return P_(k > 0.55 ? 'bonk_h' : 'bonk_s', { v: 0.65 + 0.4 * k }); },
    spot() { return P_('spot', { vary: 0 }); },
    ready() { return P_('ready', { vary: 0 }); },
    lead(up) { return P_(up ? 'lead_up' : 'lead_down', { vary: 0 }); },
    danger() { return P_('danger'); },
    low() { if (!SB.m) return false; if (T() - lastLow < 0.36) return true; lastLow = T(); return P_('low'); },
    count(n) { return P_(n <= 3 ? 'count_hi' : 'count_lo', { vary: 0 }); },
    tick(i) { const sc = [0, 2, 4, 7, 9], k = (((i | 0) % 15) + 15) % 15; return P_(['tick_a', 'tick_b', 'tick_c'][Math.floor(k / 5)], { rate: Math.pow(2, sc[k % 5] / 12), vary: 0 }); },
    horn() { if (!P_('horn', { vary: 0 })) return false; duck(0.7, 1.4); return true; },
    cd(n) { return P_('cd' + Math.min(3, Math.max(1, n | 0)), { vary: 0 }); },
    sting(kind) { if (!P_(kind === 'win' ? 'sting_win' : kind === 'lose' ? 'sting_lose' : 'sting_draw', { vary: 0 })) return false; duck(kind === 'lose' ? 0.5 : 0.38, kind === 'lose' ? 1.9 : 1.1); return true; },
    turret() { return P_('turret', { vary: 0.02 }); },
    shoot() { return P_('shoot'); },
    plop() { return P_('plop'); },
    ball() { return P_('ball'); },
    boost() { return P_('boost', { vary: 0.02 }); },
    fanfare() { return P_('fanfare', { vary: 0 }); },
    thunder() { return P_('thunder', { vary: 0.03 }); },
    heatWarn() { return P_('heatwarn', { vary: 0 }); },
    heatOn() { if (!P_('heaton', { vary: 0 })) return false; duck(0.4, 1); return true; },
    dusk() { return P_('dusk', { vary: 0 }); },
    splashWater() { return P_('splash'); },
    sprinkle(v) { return P_('sprinkle', { v: v || 1 }); },
    sink() { return P_('sink', { vary: 0.03 }); },
    rumble() { return P_('rumble', { vary: 0.03 }); },
    rise() { return P_('rise', { vary: 0.03 }); },
    flip() { return P_('flip', { vary: 0 }); },
    flipBack() { return P_('flipback', { vary: 0 }); },
  };

  function build(c, live) {
    ctx = c;""")

# 6. once the graph exists, the running sounds take their recordings if the sheets came in first
rep("""    seqT = T() + 0.1; seqS = 0;
    if (live) timer = setInterval(() => schedule(), 25);
  }""", """    seqT = T() + 0.1; seqS = 0;
    LP = null; if (SB.m || SB.s) sbLoops();
    if (live) timer = setInterval(() => schedule(), 25);
  }""")

# 7. load the sheets with the kit (menu idle) and with the first tap
rep("""      trkDecode('menu'); const sk = stageTrk(); if (sk) trkFetch(sk);
    },""", """      trkDecode('menu'); const sk = stageTrk(); if (sk) trkFetch(sk); sbLoad();
    },""")
rep("""      build(c, true); trkDecode('menu');""", """      build(c, true); sbLoad(); for (const ch of ['m', 's']) if (SB.bytes[ch]) sbDecode(ch); trkDecode('menu');""")

# 8. the running sounds drive the recordings when they're there
rep("""    roll(spd, wide) { if (!ctx) return; const t = T(), on = spd > 0.3; rollG""", """    roll(spd, wide) { if (!ctx) return; const t = T(), on = spd > 0.3;
      if (LP && LP.roll) { const L = LP.roll, k = cl(spd / 6, 0, 1); L.g.gain.setTargetAtTime(on ? (0.45 + 0.75 * k + 0.25 * (wide || 0)) * L.k : 0, t, 0.06); L.src.playbackRate.setTargetAtTime(0.75 + 0.5 * k, t, 0.1);
        if (LP.roller) LP.roller.g.gain.setTargetAtTime(on && wide ? (0.5 + 0.5 * k) * (wide || 0) * LP.roller.k : 0, t, 0.08); rollG.gain.setTargetAtTime(0, t, 0.05); return; }
      rollG""")
rep("""    rain(k) { if (!ctx) return; mood.rain = k; rainG""", """    rain(k) { if (!ctx) return; mood.rain = k; if (LP && LP.rain) { LP.rain.g.gain.setTargetAtTime(k * LP.rain.k, T(), 0.25); return; } rainG""")
rep("""    sizzle(k) { if (!ctx || mood.sizzle === k) return; mood.sizzle = k; sizG""", """    sizzle(k) { if (!ctx || mood.sizzle === k) return; mood.sizzle = k; if (LP && LP.sizzle) { LP.sizzle.g.gain.setTargetAtTime(k * LP.sizzle.k, T(), 0.05); return; } sizG""")

# 9. the voice, test hooks, and the wrapper that tries the designed version first
rep("""    _tone(o) { tone(o); }, _hiss(o) { hiss(o); }, _offset(x) { tOff = x; }, _mute(ks) { for (const k of ks) I[k] = () => {}; },
  };""", """    _tone(o) { tone(o); }, _hiss(o) { hiss(o); }, _offset(x) { tOff = x; }, _mute(ks) { for (const k of ks) I[k] = () => {}; },
    _sb(ch, b) { sbReady(ch, b); }, _sfxi() { return SFXI; }, _sbOn() { return { m: !!SB.m, s: !!SB.s, off: SB.off, fail: SB.fail }; },
    // the slime's little voice: one line at a time, never in a rush
    vox(name, v) { if (!ctx || T() - voxT < 0.45) return false; const ok = P_('vox_' + name, { v: v == null ? 1 : v, vary: 0.04, p: 2, raw: true }); if (ok) voxT = T(); return ok; },
  };""")
rep("""  for (const k in fx) api[k] = function () { const pl = pend || CENTER; cur = { p: pl.p, g: pl.g * (LVL[k] || 1) }; pend = null; try { fx[k].apply(null, arguments); } finally { cur = CENTER; } };""",
    """  for (const k in fx) api[k] = function () { const pl = pend || CENTER; cur = { p: pl.p, g: pl.g * (LVL[k] || 1), g0: pl.g }; pend = null; try { if (!(sx[k] && sx[k].apply(null, arguments))) fx[k].apply(null, arguments); } finally { cur = CENTER; } };""")
rep("""  const CENTER = { p: 2, g: 1 }, MUS_PLAY""", """  const CENTER = { p: 2, g: 1, g0: 1 }, MUS_PLAY""")

# ---------------------------------------------------------------- the game: voice lines and the beach ball
rep("""  if (hearable(B)) { AU.shrink(); AU.bonk(1); } hitStop(0.1, A, B);""", """  if (hearable(B)) { AU.shrink(); AU.bonk(1); } if (B === P) AU.vox('eep'); hitStop(0.1, A, B);""")
rep("""D.air = true; D.vy = JUMP_V; D.stroke++; D.squash = 0; D.buf = 0; fxLaunch(D, 1); if (D === P) AU.jump();""", """D.air = true; D.vy = JUMP_V; D.stroke++; D.squash = 0; D.buf = 0; fxLaunch(D, 1); if (D === P) { AU.jump(); if (Math.random() < 0.18) AU.vox('hup', 0.8); }""")
rep("""  if (D === P) { shake = Math.max(shake, 0.05 + 0.08 * c); fovKick = 6 + 6 * c; AU.fling(c); buzz(12); } else if (hearable(D)) AU.fling(c * 0.5);""",
    """  if (D === P) { shake = Math.max(shake, 0.05 + 0.08 * c); fovKick = 6 + 6 * c; AU.fling(c); buzz(12); if (c > 0.62) AU.vox('whee'); else if (c > 0.3 && Math.random() < 0.5) AU.vox('hup'); } else if (hearable(D)) AU.fling(c * 0.5);""")
rep("""  if (D === P) { AU.enter(); buzz(10); }""", """  if (D === P) { AU.enter(); buzz(10); if (Math.random() < 0.3) AU.vox('ahh'); }""")
rep("""D.slamEta = 0.3 + D.slamHang + Math.max(0, D.y - (surfaceUnder(D.x, D.z, D.y, true) > -Infinity ? surfaceUnder(D.x, D.z, D.y, true) : D.y)) / 20; D.spd = 0; D.turn = 0; D.buf = 0; if (hearable(D)) AU.whoosh(); }""",
    """D.slamEta = 0.3 + D.slamHang + Math.max(0, D.y - (surfaceUnder(D.x, D.z, D.y, true) > -Infinity ? surfaceUnder(D.x, D.z, D.y, true) : D.y)) / 20; D.spd = 0; D.turn = 0; D.buf = 0; if (hearable(D)) AU.whoosh(); if (D === P && Math.random() < 0.6) AU.vox('hyah'); }""")
rep("""D.slamEta = 0.43 + D.slamHang; D.stroke++; D.spd = 0; D.turn = 0; D.buf = 0; if (D.charging) clearCharge(D); if (hearable(D)) AU.whoosh(); }""",
    """D.slamEta = 0.43 + D.slamHang; D.stroke++; D.spd = 0; D.turn = 0; D.buf = 0; if (D.charging) clearCharge(D); if (hearable(D)) AU.whoosh(); if (D === P && Math.random() < 0.6) AU.vox('hyah'); }""")
rep("""  if (D === P) { shake = 0.6; hold = 0.06; fovKick = 12; AU.burst(1); buzz([20, 20, 45]); flashScreen(); }""", """  if (D === P) { shake = 0.6; hold = 0.06; fovKick = 12; AU.burst(1); AU.vox('hyah'); buzz([20, 20, 45]); flashScreen(); }""")
rep("""  if (reason === 'fall') { if (loud) AU.fall(); }""", """  if (reason === 'fall') { if (loud) AU.fall(); if (D === P) AU.vox('waah', 0.8); }""")
rep("""if (loud) AU.die(reason === 'coffin' || reason === 'crush' ? 'pound' : reason); if (reason === 'coffin' && pot) pot.bounce = 1; }""",
    """if (loud) AU.die(reason === 'coffin' || reason === 'crush' ? 'pound' : reason); if (D === P) AU.vox('waah'); if (reason === 'coffin' && pot) pot.bounce = 1; }""")
rep("""  if (hearable(B)) AU.squish();
  hitStop(how === 'giant'""", """  if (hearable(B)) AU.squish(); if (B === P) AU.vox('oof');
  hitStop(how === 'giant'""")
rep("""  if (hearable(A) || hearable(B)) { AU.bonk(1); AU.pop(); } hitStop(0.07, A, B);
  if (B === P) { shake = Math.max(shake, 0.3); buzz([25, 30, 25]); banner('Stunned!'); }""", """  if (hearable(A) || hearable(B)) { AU.bonk(1); AU.pop(); } if (B === P) AU.vox('oof'); hitStop(0.07, A, B);
  if (B === P) { shake = Math.max(shake, 0.3); buzz([25, 30, 25]); banner('Stunned!'); }""")
rep("""emote(D, 'glee', 1.1); AU.grow(); // a full tank""", """emote(D, 'glee', 1.1); AU.grow(); if (D === P) AU.vox('hoh'); // a full tank""")
# the customize screen: a new hat gets an "ooh", something new to wear gets a giggle
rep("""idle.side = w.slot === 'side' ? 1 : -idle.side || 1; idle.t = 2.8; menuReact = 0; AU.pop(); }""", """idle.side = w.slot === 'side' ? 1 : -idle.side || 1; idle.t = 2.8; menuReact = 0; AU.pop(); setTimeout(() => AU.vox('ooh', 0.9), 120); }""")
rep("""idle.dur = 1.15; idle.u = 0; idle.t = 2.8; menuReact = 0; emote(P, 'glee', 1.0); AU.pop(); }""", """idle.dur = 1.15; idle.u = 0; idle.t = 2.8; menuReact = 0; emote(P, 'glee', 1.0); AU.pop(); setTimeout(() => AU.vox('giggle', 0.9), 90); }""")
# the wet-dog shake after the climb out of the basin
rep("""if (!A.shook) { A.shook = true; const V = vOf(D); if (V && V.slime) { V.slime.shakeOff(1); V.slime.blink(); } if (D === P) { AU.pop(); buzz(6); } }""",
    """if (!A.shook) { A.shook = true; const V = vOf(D); if (V && V.slime) { V.slime.shakeOff(1); V.slime.blink(); } if (D === P) { AU.pop(); AU.vox('brr'); buzz(6); } }""")
# a win gets a little cheer after the sting
rep("""AU.sting(won ? 'win' : info.winner ? 'lose' : 'draw');""", """AU.sting(won ? 'win' : info.winner ? 'lose' : 'draw'); if (won) setTimeout(() => AU.vox('yay'), 380);""")
# the beach balls: a hollow plastic bounce rather than a paint plop
s = s.replace("""Math.hypot(b.x - P.x, b.z - P.z) < 14) { AU.at(b.x, b.z); AU.plop(); b.hitT = 0.15; }""", """Math.hypot(b.x - P.x, b.z - P.z) < 14) { AU.at(b.x, b.z); AU.ball(); b.hitT = 0.15; }""")
rep("""if (vn > 2 && b.hitT <= 0) { if (Math.hypot(b.x - P.x, b.z - P.z) < 14) { AU.at(b.x, b.z); AU.plop(); }""", """if (vn > 2 && b.hitT <= 0) { if (Math.hypot(b.x - P.x, b.z - P.z) < 14) { AU.at(b.x, b.z); AU.ball(); }""")
assert s.count('AU.ball()') == 3, s.count('AU.ball()')
open(p, 'w', encoding='utf-8').write(s)
print('patched')
