# recorded music: the menu, the three stage themes, and the win and lose themes, each an intro then a loop cut to the sample
import json
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
L = json.load(open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/music_out/loops.json'))
LUFS = {'menu': -15.8, 'win': -16.8, 'lost': -16.6, 'halloween': -15.8, 'island': -15.6, 'blank': -14.5}
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)
norm = {k: round(10 ** ((-16.5 - LUFS[k]) / 20), 3) for k in LUFS}
trk = ',\n    '.join(f"{k}: {{ a: {L[k]['a']}, b: {L[k]['b']}, k: {norm[k]} }}" for k in ['menu', 'halloween', 'island', 'blank', 'win', 'lost'])
rep("  let tOff = 0; const T = () => ctx.currentTime + tOff; // tOff only moves in tests\n", """  let tOff = 0; const T = () => ctx.currentTime + tOff; // tOff only moves in tests
  // ---- recorded music: the menu theme, a theme for each kind of stage, and the win and lose themes. Each plays its intro once and then goes
  // round its loop (a and b, in seconds), which was cut to the sample so the seam can't be heard. k evens out their loudness. A track loads
  // in the background and is only decoded around when it's needed; until it's ready, the synth plays as it always has ----
  const TRK = {
    """ + trk + """,
  };
  const MUSIC_BASE = (typeof window !== 'undefined' && window.MUSIC_BASE) || 'music/', TRK_LVL = { menu: 0.62, play: 0.5, end: 0.62 };
  const STAGE_TRK = { spooky: 'halloween', tropical: 'island', pop: 'blank' };
  let trkBus = null, trk = null, trkWant = null;
  const stageTrk = () => STAGE_TRK[typeof MUSIC_STYLE === 'string' ? MUSIC_STYLE : ''] || null;
  function trkFetch(key) { const R = TRK[key]; if (!R || R.bytes || R.fetching || R.fail || typeof fetch !== 'function') return; R.fetching = true;
    fetch(MUSIC_BASE + key + '.mp3').then(r => { if (!r.ok) throw new Error('missing'); return r.arrayBuffer(); }).then(b => { R.bytes = b; R.fetching = false; if (R.wantDecode) trkDecode(key); }).catch(() => { R.fetching = false; R.fail = true; }); }
  function trkDecode(key) {
    const R = TRK[key]; if (!R || R.fail) return; R.wantDecode = true; if (R.buf || R.decoding) return; if (!R.bytes) { trkFetch(key); return; }
    let dc = ctx; if (!dc) { const OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext; if (!OAC) return; try { dc = new OAC(2, 1, 48000); } catch (e) { return; } }
    R.decoding = true;
    const ok = b => { R.decoding = false; if (!R.wantDecode) return; R.buf = b; if (trkWant === key && ctx && (!trk || trk.key !== key)) trkGo(key, 1.4, 1.2); }, bad = () => { R.decoding = false; R.fail = true; };
    try { const pr = dc.decodeAudioData(R.bytes.slice(0), ok, bad); if (pr && pr.catch) pr.catch(bad); } catch (e) { bad(); }
  }
  // let go of a decoded track that won't be needed for a while (its file stays, so it decodes again quickly)
  function trkDrop(key) { const R = TRK[key]; if (R && (!trk || trk.key !== key)) { R.buf = null; R.wantDecode = false; } }
  // start a track from its beginning, fading out whatever was playing (the synth steps aside)
  function trkGo(key, fadeOut, fadeIn) {
    const R = TRK[key]; if (!ctx || !R || !R.buf) return false; if (trk && trk.key === key) return true;
    trkStop(fadeOut || 0.6);
    const t = T(), src = ctx.createBufferSource(), g = ctx.createGain(), lvl = R.k * (key === 'menu' ? TRK_LVL.menu : key === 'win' || key === 'lost' ? TRK_LVL.end : TRK_LVL.play);
    src.buffer = R.buf; src.loop = true; src.loopStart = R.a; src.loopEnd = Math.min(R.b, R.buf.duration);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(lvl, t + (fadeIn || 0.03)); src.connect(g); g.connect(trkBus); src.start(t + 0.005);
    trk = { key, src, g }; musOn = false; mus.gain.cancelScheduledValues(t); mus.gain.setTargetAtTime(0, t, (fadeOut || 0.6) / 3); return true;
  }
  function trkStop(fade) { if (!trk) return; const t = T(), { src, g } = trk; g.gain.cancelScheduledValues(t); g.gain.setValueAtTime(g.gain.value, t); g.gain.linearRampToValueAtTime(0, t + fade); try { src.stop(t + fade + 0.05); } catch (e) {} trk = null; }
""")
rep("    musDuck = ctx.createGain(); musDuck.connect(musLP);\n", "    musDuck = ctx.createGain(); musDuck.connect(musLP);\n    trkBus = ctx.createGain(); trkBus.connect(musDuck);\n")
rep("""      kitGo = true; SM = {}; renderKit(false, [() => { PRE_IR.hall = PRE_IR.hall || hall(2.6); }, () => { PRE_IR.plate = PRE_IR.plate || plate(2.2); }]);
    },""", """      kitGo = true; SM = {}; renderKit(false, [() => { PRE_IR.hall = PRE_IR.hall || hall(2.6); }, () => { PRE_IR.plate = PRE_IR.plate || plate(2.2); }]);
      trkDecode('menu'); const sk = stageTrk(); if (sk) trkFetch(sk);
    },
    // the stage was picked: get its theme ready, and let go of the others
    prep() { const sk = stageTrk(); for (const k of ['halloween', 'island', 'blank']) if (k !== sk) trkDrop(k); if (sk) trkDecode(sk); },
    _trk(k) { return k ? !!(TRK[k] && TRK[k].buf) : trk && trk.key; },""")
rep("      build(c, true); if (lastMode !== 'none') { const m = lastMode; lastMode = 'none'; api.music(m); }",
    "      build(c, true); trkDecode('menu'); { const sk = stageTrk(); if (sk) trkDecode(sk); } if (lastMode !== 'none') { const m = lastMode; lastMode = 'none'; api.music(m); }")
rep("""    music(mode) {
      if (!ctx) { lastMode = mode; return; }
      const t = T(), vol = (v, tau) => { mus.gain.cancelScheduledValues(t); mus.gain.setTargetAtTime(v, t, tau); };
      musLP.frequency.cancelScheduledValues(t); musLP.frequency.setTargetAtTime(mode === 'pause' ? 650 : 20000, t, mode === 'pause' ? 0.06 : 0.12);""",
"""    music(mode) {
      if (!ctx) { lastMode = mode; if (mode === 'menu') trkDecode('menu'); return false; }
      const t = T(), vol = (v, tau) => { mus.gain.cancelScheduledValues(t); mus.gain.setTargetAtTime(v, t, tau); };
      musLP.frequency.cancelScheduledValues(t); musLP.frequency.setTargetAtTime(mode === 'pause' ? 650 : 20000, t, mode === 'pause' ? 0.06 : 0.12);
      // a recorded track for this moment, when there's one ready: the synth steps aside for it
      trkBus.gain.cancelScheduledValues(t); trkBus.gain.setTargetAtTime(mode === 'pause' ? 0.7 : 1, t, 0.12);
      if (mode === 'pause') { if (trk) { lastMode = mode; return true; } }
      else {
        const key = mode === 'menu' ? 'menu' : mode === 'play' ? stageTrk() : mode === 'win' || mode === 'lost' ? mode : null; trkWant = key;
        if (key) trkDecode(key);
        if (mode === 'play') { trkDecode('win'); trkDecode('lost'); } else if (mode === 'menu') { trkDrop('win'); trkDrop('lost'); }
        if (key && TRK[key].buf) { if (!(trk && trk.key === key && mode === 'play' && lastMode === 'pause')) trkGo(key, mode === 'menu' ? 0.9 : 0.4, mode === 'menu' && lastMode !== 'none' ? 0.5 : 0.03); lastMode = mode; return true; }
        trkStop(mode === 'end' ? 0.25 : 0.7);
        if (mode === 'win' || mode === 'lost') { lastMode = mode; return false; }
      }""")
# the end of the synth's music(): it returns false (the synth is playing, not a track)
rep("""      else if (mode === 'end') { musOn = false; vol(0, 0.12); }
      lastMode = mode;
    },""", """      else if (mode === 'end') { musOn = false; vol(0, 0.12); }
      lastMode = mode; return false;
    },""")
# the stage's theme gets ready as soon as the stage is known
rep("  TH = T; MUSIC_STYLE = musicStyleOf(T.id); HOR.set(T.hor);", "  TH = T; MUSIC_STYLE = musicStyleOf(T.id); try { AU.prep(); } catch (e) {} HOR.set(T.hor);")
# the end of a match: the win or lose theme (the old stingers if it isn't ready)
rep("  setTimeout(() => { if (!vic || id !== runId) return; if (happy) { AU.fanfare(); buzz([30, 40, 30]); } else if (!info.winner) AU.draw(); else AU.lose(); }, 640);",
    "  setTimeout(() => { if (!vic || id !== runId) return; const th = AU.music(happy ? 'win' : 'lost'); if (happy) { if (!th) AU.fanfare(); buzz([30, 40, 30]); } else if (!th) { if (!info.winner) AU.draw(); else AU.lose(); } }, 640);")
open(p, 'w').write(s)
print('ok', norm)
