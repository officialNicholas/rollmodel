"""v316: the boss demo's own sounds. The Jellyfish Boss and the Sunken Keep get sound effects of their own (Ludo.ai takes, two of each,
finished by tools/boss_sfx_build.py into game/sfx/b_*.mp3 and k_*.mp3; no music). All fetched as the demo starts and let go as it ends:
nothing else asks for them, so a normal match never fetches or plays one.

- No music on the keep (asked for: no music): its water, its slime and the boss are what you hear. The stage's song isn't fetched,
  and the game's stand-in synth tune doesn't play either.
- The keep: a calm underwater bed (deep muffled water, a soft distant rumble) loops the whole time you're on the stage, in as it opens,
  out as you leave, lower while paused. The slime pool bubbles, a loop of its own that's louder the nearer you are to the pool. A drop
  of slime landing near you plops (as the falls' drips let go, now and then). The caged skeleton's cage rattles when it shakes its bars,
  and it cackles when you fall in the slime; your fall into the pool is a gloopy splash, in place of the game's own fall.
- The boss's entrance: the pool churns, the gloves burst out of the slime, slam down on the curb and grip, it hauls itself up straining,
  one huge beat of its bell shoots it up (a deep whoomp with its slime bursting), it bumps its fists in sparks, and roars.
- Its moves: each beat of its bell as it swims (a soft whoomp, quieter the further off it is), the wind-up of a punch, slam or zap, a
  fist landing, both fists slamming, the sweep's swoosh, the zap's charging and its discharge, a hurt squelch, a dizzy warble when
  stunned, a mocking laugh, and the defeat's deflating gurgle (a last gloop as the slime closes over it). The ones heard most have two
  takes, played in turn. Each of the boss's hits sits where it lands (panned, a little quieter far off).
  Until a sound is in, the game's own plays, as before; your own bump when a hit knocks you back stays the game's.
- The sound's own: a looping effect (xloop: through the effects bus, in when it has decoded, back on a fresh audio context, its
  level eased, faded out and let go), letting go of decoded effects (xfree), one of the game's effects played as a recording of the
  demo's while it's on (xsub), and a one-off effect placed in the world and dipping the music (xplay's at and duck)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

# ---- the sound (makeAudio): loops of their own, letting go, stand-ins, a placed one-off
AU_LOOP = r"""
  // (v316) a looping effect of its own (the Sunken Keep's water and its slime pool): xloop(name, level, { a, b, fade }) plays
  // sfx/<name>.mp3 round its loop (a to b seconds; the whole file by default) through the effects bus, fading in over fade seconds from
  // the moment it has decoded (fetched now if it isn't, as soon as there's a context), and again on a fresh context. Its handle:
  // set(level, seconds) eases it to a level, stop(seconds) fades it out and lets it go (its nodes, and its hold on the sound). xfree(names)
  // lets go of decoded effects no loop is playing. xsub(effect, name, opts) has one of the game's own effects play that recording in its
  // place while it's set (when it's in), xsub(effect) undoes it
  const XL = new Set(), XS = {};
  function xlGo(L) {
    const b = XB[L.n]; if (!L.on || L.src || !ctx || !sfx || !b || b === 'busy') return;
    try { const src = ctx.createBufferSource(), g = ctx.createGain(), t = T() + 0.02, e = L.b > 0 ? Math.min(L.b, b.duration) : b.duration, a = Math.min(L.a, Math.max(0, e - 0.05));
      src.buffer = b; src.loop = true; src.loopStart = a; src.loopEnd = e; g.gain.value = 0; g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(L.v, t + L.fin); // (0 till then: read before its fade begins, or while the sound is held, its level is 0, not 1)
      src.connect(g); g.connect(sfx); src.start(t, a); L.src = src; L.g = g; L.fin = 0.4; } catch (e) {} } // (on a fresh context it comes back quicker)
  function xlKick() { for (const L of XL) xlGo(L); }
  function xlRenew() { for (const L of XL) { L.src = L.g = null; xGet(L.n); } xlKick(); } // (a fresh context: the old one's nodes went with it)
  function xLoop(n, v, o) {
    o = o || {}; const L = { n, v: v == null ? 1 : v, a: o.a || 0, b: o.b || 0, fin: o.fade == null ? 1.5 : Math.max(0.02, o.fade), on: true, src: null, g: null };
    XL.add(L); xGet(n); xlGo(L);
    return {
      set(v2, sec) { L.v = v2; const g = L.g; if (!g || !ctx) return; const t = T(); g.gain.cancelScheduledValues(t); g.gain.setValueAtTime(g.gain.value, t); g.gain.setTargetAtTime(v2, t, Math.max(0.01, (sec == null ? 0.25 : sec) / 3)); },
      stop(sec) { if (!L.on) return; L.on = false; XL.delete(L); const s = L.src, g = L.g; L.src = L.g = null; if (!s || !ctx) return;
        const t = T(), f = Math.max(0.02, sec == null ? 0.5 : sec); s.onended = () => { try { s.disconnect(); g.disconnect(); } catch (e) {} };
        try { g.gain.cancelScheduledValues(t); g.gain.setValueAtTime(g.gain.value, t); g.gain.linearRampToValueAtTime(0, t + f); s.stop(t + f + 0.05); } catch (e) { try { s.disconnect(); g.disconnect(); } catch (e2) {} } },
      get playing() { return !!L.src; }, get level() { return L.g ? L.g.gain.value : 0; }, get on() { return L.on; },
    };
  }
  function xFree(names) { const keep = new Set(); for (const L of XL) keep.add(L.n); for (const n of names || []) if (!keep.has(n)) delete XB[n]; }
"""

def apply_audio(s):
    # no music on the Sunken Keep (its theme's noMusic): its water, its slime and the boss instead. Its song isn't fetched or decoded,
    # and a match there plays as the end of a match does: no song, and not the synth tune that plays when a song is missing
    s = rep(s, "noSea: true, mirror: true, noClouds: true, noMarks: true,", "noSea: true, noMusic: true, mirror: true, noClouds: true, noMarks: true,")
    s = rep(s, "  const stageTrk = () => (typeof MUSIC_TRK", "  const stageTrk = () => (TH && TH.noMusic ? null : typeof MUSIC_TRK")
    s = rep(s, "    music(mode) {\n      if (!ctx) { lastMode = mode;", "    music(mode) {\n      if (mode === 'play' && TH && TH.noMusic) mode = 'end'; // (v316: a stage with no music)\n      if (!ctx) { lastMode = mode;")
    # a fetch let go of (xfree) while it was on its way is dropped when it lands; a decoded sound starts the loops waiting for it
    s = rep(s, ".then(buf => { XB[n] = buf; }).catch(() => { XB[n] = null; }); }",
               ".then(buf => { if (XB[n] !== 'busy') return; XB[n] = buf; xlKick(); }).catch(() => { if (XB[n] === 'busy') XB[n] = null; }); }")
    # xplay: o.at [x, z] places it (panned, quieter far off: at()'s spots); o.duck [amount, seconds] dips the music under it
    s = rep(s, "  function xPlay(n, o) { o = o || {}; const b = XB[n]; if (!ctx || !b || b === 'busy' || ctx.state !== 'running') { xGet(n); return false; }\n"
               "    try { const src = ctx.createBufferSource(), g = ctx.createGain(); src.buffer = b; src.playbackRate.value = o.rate || 1; g.gain.value = (o.v == null ? 1 : o.v) * cur.g0; src.connect(g); g.connect(sfx); src.start(T() + (o.d || 0) + 0.004); } catch (e) { return false; } return true; }\n",
               "  function xPlay(n, o) { o = o || {}; const b = XB[n]; if (!ctx || !b || b === 'busy' || ctx.state !== 'running') { xGet(n); return false; }\n"
               "    let p = null, g0 = cur.g0; if (o.at) { at(o.at[0], o.at[1]); if (pend) { p = pend.p; g0 *= pend.g; } pend = null; } // (v316: o.at, o.duck)\n"
               "    try { const src = ctx.createBufferSource(), g = ctx.createGain(); src.buffer = b; src.playbackRate.value = o.rate || 1; g.gain.value = (o.v == null ? 1 : o.v) * g0; src.connect(g); g.connect(p != null && pans[p] || sfx); src.start(T() + (o.d || 0) + 0.004); if (o.duck) duck(o.duck[0], o.duck[1]); } catch (e) { return false; } return true; }\n"
               + AU_LOOP)
    # a fresh context (the first, or one in place of a stuck one): the loops start, or come back, on it
    s = rep(s, "    if (live) timer = setInterval(() => schedule(), 25);\n  }\n", "    if (live) timer = setInterval(() => schedule(), 25);\n    if (live) xlRenew(); // (v316)\n  }\n")
    # the game's own effect, or the recording standing in for it
    s = rep(s, "try { if (!(sx[k] && sx[k].apply(null, arguments))) fx[k].apply(null, arguments); } finally { cur = CENTER; } };",
               "try { if (!(XS[k] && xPlay(XS[k][0], XS[k][1])) && !(sx[k] && sx[k].apply(null, arguments))) fx[k].apply(null, arguments); } finally { cur = CENTER; } };")
    s = rep(s, "    xwant(n) { xGet(n); }, xplay(n, o) { return xPlay(n, o); }, // (v276)\n",
               "    xwant(n) { xGet(n); }, xplay(n, o) { return xPlay(n, o); }, // (v276)\n"
               "    xloop(n, v, o) { return xLoop(n, v, o); }, xfree(names) { xFree(names); }, xsub(k, n, o) { if (n) { XS[k] = [n, o || {}]; xGet(n); } else delete XS[k]; }, // (v316)\n"
               "    _xb() { const o = {}; for (const n in XB) { const b = XB[n]; o[n] = b && b.duration ? +b.duration.toFixed(3) : b; } return { xb: o, loops: [...XL].map(L => [L.n, !!L.src]), subs: Object.keys(XS) }; }, // (v316, for tests)\n")
    return s

# ---- the demo: its sounds
JS = r"""// ---------- (v316) the boss demo's sounds: the Jellyfish Boss's and the Sunken Keep's own (Ludo.ai takes, finished by
// tools/boss_sfx_build.py). Fetched as the demo starts, let go as it ends. The keep's water (a bed, looping: in as the stage opens, out
// as you leave, lower while paused) and its slime pool (looping, louder the nearer you are to it); the boss's entrance and moves on its
// events (cqbEvent), and each beat of its bell as it swims (quiet, quieter far off); the caged skeleton's rattle and cackle, a drop of
// slime landing near you, and your fall into the pool (standing in for the game's own fall). (var: the frame can come before these run)
var CQB_SFX = ['b_churn', 'b_burst', 'b_grab', 'b_haul', 'b_launch', 'b_bump', 'b_roar', 'b_pulse', 'b_pulse2', 'b_windup', 'b_windup2', 'b_punch', 'b_slam', 'b_sweep',
  'b_charge', 'b_zap', 'b_hurt', 'b_hurt2', 'b_dizzy', 'b_taunt', 'b_defeat', 'k_amb', 'k_bubble', 'k_drip', 'k_drip2', 'k_cage', 'k_laugh', 'k_fall'];
// the loops: each file is its loop with 0.4 s of itself either side (a to b, the loop); v its level (the pool's, right at its rim)
var CQB_LOOP = { amb: { n: 'k_amb', a: 0.4, b: 10.85002, v: 0.28 }, bub: { n: 'k_bubble', a: 0.4, b: 7.08, v: 0.55 } };
var CQB_TWO = { b_pulse: 0, b_windup: 0, b_hurt: 0, k_drip: 0 }; // (two takes: played in turn)
// one of the demo's sounds (false if it isn't in yet: the caller plays the game's own)
function cqbSfx(n, o) { if (n in CQB_TWO && (CQB_TWO[n] ^= 1)) n += '2'; return AU.xplay(n, o); }
function cqbSfxOn() {
  const Q = CQB; for (const n of CQB_SFX) AU.xwant(n);
  const S = Q.sfx || (Q.sfx = { amb: null, bub: null, ph: 1, bubV: -1, lv: 1, sk: null, laugh: false, rattle: 0, drips: [], dripT: 0, wantT: 0 });
  const A = CQB_LOOP.amb, B = CQB_LOOP.bub;
  if (!S.amb) S.amb = AU.xloop(A.n, A.v, { a: A.a, b: A.b, fade: 3 });
  if (!S.bub) S.bub = AU.xloop(B.n, B.v * 0.1, { a: B.a, b: B.b, fade: 2.5 });
  AU.xsub('fall', 'k_fall'); // (your fall into the pool: the only fall the keep has)
}
function cqbSfxOff() {
  const Q = CQB, S = Q && Q.sfx; AU.xsub('fall', null); if (!S) return;
  if (S.amb) S.amb.stop(0.8); if (S.bub) S.bub.stop(0.6); Q.sfx = null;
  AU.xfree(CQB_SFX); // (the loops fade out on their own hold of their sound; nothing of the demo's stays decoded)
}
function cqbSfxTick(dt, rdt) {
  const Q = CQB, S = Q.sfx, b = Q.boss; if (!S) return;
  if (S.wantT >= 0 && (S.wantT += rdt) > 2.5) { S.wantT = -1; for (const n of CQB_SFX) AU.xwant(n); } // (once more, in case the sound had only just started)
  // the water: lower while paused (not while its entrance holds you); the pool's bubbling by how near you are to its rim (half 3 out,
  // a tenth or so by the wall)
  const lv = state === 'paused' && !Q.paused ? 0.5 : 1, e = Math.max(0, Math.hypot(P.x - Q.pool.x, P.z - Q.pool.z) - 4.35), bv = CQB_LOOP.bub.v * lv * Math.max(0.08, 1 / (1 + Math.pow(e / 3, 1.5)));
  if (S.amb && lv !== S.lv) S.amb.set(CQB_LOOP.amb.v * lv, 0.6); S.lv = lv;
  if (S.bub && Math.abs(bv - S.bubV) > 0.008) { S.bub.set(bv, S.bubV < 0 ? 2.5 : 0.3); S.bubV = bv; }
  // each beat of its bell as it swims (the phase wrapping round), quieter the further off it is
  const st = b && b.isReady && b._dbg ? b._dbg.st : null;
  if (st) { const ph = st.ph;
    if (ph < S.ph - 0.5 && b.group.visible && !b.busy && b.move === 'idle') { const g = b.group.position, dd = Math.hypot(P.x - g.x, P.z - g.z); cqbSfx('b_pulse', { v: 0.8 * clamp(1.3 - dd / 16, 0.3, 1), rate: 0.94 + Math.random() * 0.12, at: [g.x, g.z] }); }
    S.ph = ph; }
  // the skeleton: its cage rattling as it shakes the bars, its cackle when you fall in the slime (as its own animation goes)
  const Sk = typeof CQ_CAGE !== 'undefined' ? CQ_CAGE.skel : null, c0 = Sk && CQ_CAGE.list.find(c => c.kind === 'skeleton');
  if (c0) { if (S.sk !== Sk) { S.sk = Sk; S.laugh = Sk.laugh > 0; S.rattle = Sk.rattle; } // (a skeleton new since the last look: from where it is)
    const lf = Sk.laugh > 0; if (lf && !S.laugh) cqbSfx('k_laugh', { v: 0.95, d: 0.3, at: [c0.x, c0.z] }); S.laugh = lf;
    if (Sk.rattle > S.rattle + 1) cqbSfx('k_cage', { v: 0.9, at: [c0.x, c0.z] }); S.rattle = Sk.rattle; }
  // a drop of slime landing near you (the falls' drips, each in its own time: the goo's period, phase and landing), now and then (not
  // while the entrance's camera is away from you)
  const U = typeof GOO_U !== 'undefined' ? GOO_U : null, R = U && U.uDr && U.uDr.value, Dl = U && U.uDl && U.uDl.value;
  if (R && Dl) { const t = U.uTime.value; S.dripT -= rdt;
    for (let i = 0; i < R.length; i++) { const d = R[i]; if (!(d.z > 0)) continue; const k = Math.floor((t + d.w - Dl[i]) / d.z);
      if (S.drips[i] !== undefined && k !== S.drips[i] && S.dripT <= 0 && !Q.cut) { const dd = Math.hypot(P.x - d.x, P.z - d.y); if (dd < 8) { S.dripT = 1.4; cqbSfx('k_drip', { v: 1.1 - dd / 8 * 0.75, rate: 0.9 + Math.random() * 0.2, at: [d.x, d.y] }); } }
      S.drips[i] = k; } }
}
"""

def apply(s):
    s = apply_audio(s)
    a = "// ---------- the axolotl in the game: the slime's stand-in"
    s = rep(s, a, JS + a)
    # the demo: its sounds start with it (the wind-ups heard too), stop and are let go with it, and run each frame
    s = rep(s, "b.on(e, d => cqbEvent(e, d));\n  }\n", "b.on(e, d => cqbEvent(e, d));\n    b.on('windup', d => cqbEvent('windup', d)); // (v316: for its sound)\n  }\n")
    s = rep(s, "  cqbPanel();\n}\n", "  cqbPanel(); cqbSfxOn(); // (v316: its sounds)\n}\n")
    s = rep(s, "function cqbEnd() {\n  if (!CQB) return; const Q = CQB;", "function cqbEnd() {\n  if (!CQB) return; const Q = CQB; cqbSfxOff(); // (v316: its sounds stopped and let go)")
    s = rep(s, "  if (Q.kcd > 0) Q.kcd -= rdt;\n", "  if (Q.kcd > 0) Q.kcd -= rdt;\n  cqbSfxTick(dt, rdt); // (v316: the boss's and the keep's sounds)\n")
    # the events: its own sounds in place of the game's (which still play while one isn't in)
    s = rep(s, "  if (e === 'emergeChurn') { AU.rumble(); Q.rumble = 1.6; }", "  if (e === 'emergeChurn') { cqbSfx('b_churn') || AU.rumble(); Q.rumble = 1.6; }")
    s = rep(s, "  else if (e === 'emergeHands') { AU.splashWater(); Q.shake", "  else if (e === 'emergeHands') { cqbSfx('b_burst') || AU.splashWater(); Q.shake")
    s = rep(s, "  else if (e === 'grab') { AU.slam(); Q.shake", "  else if (e === 'grab') { cqbSfx('b_grab', { duck: [0.45, 0.6] }) || AU.slam(); Q.shake")
    s = rep(s, "  else if (e === 'emergeHaul') { AU.rumble(); Q.rumble = 1.8; }", "  else if (e === 'emergeHaul') { cqbSfx('b_haul') || AU.rumble(); Q.rumble = 1.8; }")
    s = rep(s, "  else if (e === 'launch') { AU.quake(); AU.splashWater(); AU.boost(); Q.shake", "  else if (e === 'launch') { if (!cqbSfx('b_launch', { duck: [0.7, 1.4] })) { AU.quake(); AU.splashWater(); AU.boost(); } Q.shake")
    s = rep(s, "  else if (e === 'emergeBump') { AU.thunder(); AU.burst(0.7); Q.shake", "  else if (e === 'emergeBump') { if (!cqbSfx('b_bump', { duck: [0.35, 0.5] })) { AU.thunder(); AU.burst(0.7); } cqbSfx('b_roar', { d: 0.4 }); Q.shake")
    s = rep(s, "if (d.hand === 'zap') AU.thunder(); else if (p > 1.2) AU.quake(); else AU.slam();",
               "const at = [d.x, d.z]; if (d.hand === 'zap') cqbSfx('b_zap', { at }) || AU.thunder(); else if (p > 1.2) cqbSfx('b_slam', { at, duck: [0.75, 1.4] }) || AU.quake(); else cqbSfx('b_punch', { at, rate: 0.95 + Math.random() * 0.1, duck: [0.45, 0.6] }) || AU.slam();")
    s = rep(s, "  else if (e === 'start') { if (d.move === 'sweep') AU.whoosh(); if (d.move === 'hurt') { AU.bonk(1); AU.squish(); } if (d.move === 'taunt') AU.bloop(); cqbNow(d.move); }",
               "  else if (e === 'start') { if (d.move === 'sweep') cqbSfx('b_sweep', { d: 0.4 }) || AU.whoosh(); if (d.move === 'hurt' && !cqbSfx('b_hurt')) { AU.bonk(1); AU.squish(); } if (d.move === 'taunt') cqbSfx('b_taunt') || AU.bloop();\n"
               "    if (d.move === 'zap') cqbSfx('b_charge'); if (d.move === 'defeat') { cqbSfx('b_hurt', { v: 0.85 }); cqbSfx('b_defeat', { d: 0.45 }); } cqbNow(d.move); }")
    s = rep(s, "  else if (e === 'done') cqbNow('idle');\n",
               "  else if (e === 'done') cqbNow('idle');\n  else if (e === 'windup') { if (d.move === 'punch' || d.move === 'slam' || d.move === 'zap') cqbSfx('b_windup', { v: d.move === 'zap' ? 0.75 : 1 }); }\n")
    s = rep(s, "  else if (e === 'stunStart') AU.sink();\n", "  else if (e === 'stunStart') cqbSfx('b_dizzy') || AU.sink();\n")
    s = rep(s, "  else if (e === 'defeated') AU.sink();\n", "  else if (e === 'defeated') cqbSfx('k_drip', { v: 0.8, rate: 0.7 }) || AU.sink(); // (the slime closing over it)\n")
    return s
