#!/usr/bin/env python3
"""v203: the menu is quiet. Its backdrop scene still spawns items, but the 'something turned up' chime only plays in a match.
Tips in the shop and the locker dim without the blur (that half lives in tools/assets/tutorial.js and tutorial.css).
No rolling sound: the rolling bed (and the roller's) was filtered noise that read as hiss, worst under slow motion.
The locker's Halloween cut is rebuilt on the lobby song's clock (tools/music/build_spook.py): same tempo, same bars, a loop of
exactly the same length, so lobby to locker and back carries on from the very same spot, with an equal-power cross-fade."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui127_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("  if (Math.hypot(P.x - best[0], P.z - best[2]) < 16) AU.spot();\n}",
    "  if (state === 'play' && Math.hypot(P.x - best[0], P.z - best[2]) < 16) AU.spot(); /* (the menu's backdrop spawns them too, silently) */\n}")
def cut(start, end, new):
    """replace the one span that runs from start to the end of end"""
    global s
    assert s.count(start) == 1, f'start x{s.count(start)}: {start[:80]!r}'
    i = s.index(start); j = s.index(end, i); assert j - i < 4000, 'span too long'
    s = s[:i] + new + s[j + len(end):]
# ---- no rolling sound
rep("for (const [k, to] of [['roll', 2], ['roller', 2], ['rain', -1], ['sizzle', 2]])", "for (const [k, to] of [['rain', -1], ['sizzle', 2]])")
cut("    // rolling: a squelchy rumble that pulses faster the quicker you go\n", "rollG.connect(pans[2]); s.start(); rollLfo.start(); }\n",
    "    // (no rolling bed: its filtered noise read as hiss, worst in slow motion, when the music is muffled)\n")
rep("  let rollG, rollF, rollLfo, rainG, sizG, chA = null;", "  let rainG, sizG, chA = null;")
cut("    roll(spd, wide) { if (!ctx) return; const t = T(), on = spd > 0.3;\n", "rollLfo.frequency.setTargetAtTime(2.5 + spd * 1.1, t, 0.1); },\n",
    "    roll() {}, // (rolling is silent now: see the note where the beds are built)\n")
# ---- the Halloween cut on the lobby song's clock
rep("    spook: { a: 7.32, b: 46.21, k: 0.795 }, // the same song, the Halloween cut (trimmed so its bars line up with the menu song's)",
    "    spook: { a: 1, b: 37.79423, k: 0.785, file: 'spook2' }, // the same song, the Halloween cut, rebuilt on the menu song's own clock: same tempo, same bars, a loop exactly as long (a new file name, so a cached copy of the old cut never meets these loop points)")
rep("fetch(MUSIC_BASE + key + '.mp3')", "fetch(MUSIC_BASE + (R.file || key) + '.mp3')")
rep("  function trkPos() { if (!trk) return 0; const R = TRK[trk.key], p = T() - trk.t0, b = Math.min(R.b, trk.src.buffer.duration), len = b - R.a; return p <= b || len <= 0 ? p : R.a + ((p - R.a) % len); }\n"
    "  function carryOff(key) { if (!trk || SWAP[trk.key] !== key) return 0; const A = TRK[trk.key], B = TRK[key]; return Math.max(0, B.a + (trkPos() - A.a) / (A.b - A.a) * (B.b - B.a)); }\n",
    "  function trkPosAt(t) { if (!trk) return 0; const R = TRK[trk.key], p = t - trk.t0, b = Math.min(R.b, trk.src.buffer.duration), len = b - R.a; return p <= b || len <= 0 ? p : R.a + ((p - R.a) % len); }\n"
    "  function trkPos() { return trkPosAt(T()); }\n"
    "  // the two cuts keep one clock and their loops are the same length, so the same moment is the same distance into each loop\n"
    "  function carryOff(key) { if (!trk || SWAP[trk.key] !== key) return 0; const A = TRK[trk.key], B = TRK[key]; return B.a + Math.max(0, trkPos() - A.a) % (B.b - B.a); }\n"
    "  // lobby to locker or back: the other cut comes in at exactly the spot this one has reached, and the two cross over on an equal-power curve\n"
    "  const SWAP_X = 1.4;\n"
    "  function trkSwap(key) {\n"
    "    const R = TRK[key], A = trk; if (!ctx || !R || !R.buf || !A) return false;\n"
    "    const now = T(), t = now + 0.04, RA = TRK[A.key], off = R.a + Math.max(0, trkPosAt(t) - RA.a) % (R.b - R.a), lvl = R.k * TRK_LVL.menu, g0 = Math.max(0, A.g.gain.value);\n"
    "    const src = ctx.createBufferSource(), g = ctx.createGain(), n = 48, up = new Float32Array(n), dn = new Float32Array(n);\n"
    "    for (let i = 0; i < n; i++) { const x = i / (n - 1) * Math.PI / 2; up[i] = Math.sin(x) * lvl; dn[i] = Math.cos(x) * g0; }\n"
    "    src.buffer = R.buf; src.loop = true; src.loopStart = R.a; src.loopEnd = Math.min(R.b, R.buf.duration); g.gain.value = 0; src.connect(g); g.connect(trkBus);\n"
    "    g.gain.setValueCurveAtTime(up, t, SWAP_X); A.g.gain.cancelScheduledValues(now); A.g.gain.setValueAtTime(g0, now); A.g.gain.setValueCurveAtTime(dn, t, SWAP_X);\n"
    "    try { A.src.stop(t + SWAP_X + 0.05); } catch (e) {}\n"
    "    src.start(t, off); trk = { key, src, g, t0: t - off }; musOn = false; return true;\n"
    "  }\n")
rep("trkPend = null; const sw = !!(trk && SWAP[trk.key] === key); trkGo(key, sw ? 0.5 : 1.4, sw ? 0.5 : trk ? 1.2 : 0.6, false, carryOff(key)); }",
    "trkPend = null; if (trk && SWAP[trk.key] === key) trkSwap(key); else trkGo(key, 1.4, trk ? 1.2 : 0.6, false, 0); }")
rep("        const sw = !!(key && trk && SWAP[trk.key] === key); // (lobby to locker or back: a short cross-fade at the same bar)\n"
    "        if (key && TRK[key].buf) on = trkGo(key, sw ? 0.45 : mode === 'menu' ? 0.9 : 0.4, sw ? 0.45 : mode === 'menu' && lastMode !== 'none' ? 0.5 : 0.03, mode === 'play' && lastMode !== 'pause', carryOff(key));\n"
    "        else trkStop(mode === 'end' ? 0.25 : 0.7);\n",
    "        const sw = !!(key && trk && SWAP[trk.key] === key); // (lobby to locker or back: the other cut takes over at the same spot)\n"
    "        if (key && TRK[key].buf) on = sw ? trkSwap(key) : trkGo(key, mode === 'menu' ? 0.9 : 0.4, mode === 'menu' && lastMode !== 'none' ? 0.5 : 0.03, mode === 'play' && lastMode !== 'pause', 0);\n"
    "        else if (sw) on = true; /* (the other cut is still decoding: this one plays on and hands over the moment it is ready) */\n"
    "        else trkStop(mode === 'end' ? 0.25 : 0.7);\n")
rep('<p class="ver">Version 202</p>', '<p class="ver">Version 203</p>')
open(DST, 'w').write(s)
print('ui128 ok', n0, '->', len(s))
