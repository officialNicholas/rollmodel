"""v328: a tap on your character: one reaction at a time, and a different one each time.

- The lobby: a tap used to start the hop again on every touch, so a run of taps kept it bouncing in mid-air. Now each tap plays one
  reaction and taps do nothing until it's done. The first tap is a hop; after that it goes through the moods it already does by itself
  (a wave, a blep, chin up with a smirk, a wet-dog shake, peekaboo behind its ears, a sneeze, a wag, a tilt of the head, a look round, a
  wiggle), shuffled, never the same one twice running, the hop coming round again once a round.
- The locker page's window: the same rule, with what that character can do: a hop, a wave, a hand up, ears up in surprise, a blep, a
  smirk, a sneeze (a puff of paint), a wet-dog shake, a twirl. A drag still spins you, and stops a reaction under way."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

LOBBY = r'''// (v328) a tap on you in the lobby: one reaction at a time, and taps do nothing until it's done (a run of taps used to start the hop again
// in mid-air, over and over); and not the same thing each time: the first tap is a hop, then it goes through the moods it already has
// (a wave, a blep, chin up, a wet-dog shake, peekaboo, a sneeze, a wag, a tilt of the head, a look round, a wiggle), shuffled, never the
// same one twice running. [name, seconds]
const POKE_AXO = [['hop', 0.7], ['wave', 1.8], ['blep', 1.6], ['proud', 1.6], ['shake', 1.4], ['peek', 1.9], ['sneeze', 2.0], ['wag', 1.3], ['tilt', 1.25], ['look', 1.5], ['wiggle', 1.2]];
const POKE_SLIME = [['hop', 0.7], ['wag', 1.3], ['peek', 1.9], ['look', 1.5], ['wiggle', 1.2], ['face', 1.4]]; // (the slime, if the axolotl isn't in: the moods it has)
// the next in the round: a fresh shuffle when it runs out (not starting with the last one), the hop first the very first time
function pokeNext(S, acts) {
  if (!S.q.length) { const a = acts.filter(x => x[0] !== S.last); for (let i = a.length - 1; i > 0; i--) { const j = (Math.random() * (i + 1)) | 0, t = a[i]; a[i] = a[j]; a[j] = t; }
    if (!S.n) { const h = a.findIndex(x => x[0] === 'hop'); if (h > 0) a.unshift(a.splice(h, 1)[0]); } S.q = a; }
  const n = S.q.shift(); S.last = n[0]; S.n++; return n;
}
const LOBBY_POKE = { q: [], last: '', n: 0, until: 0 };
function lobbyPoke() {
  const now = performance.now(); if (now < LOBBY_POKE.until || menuReact > 0 || lkDip) return; // (still busy with the last one)
  const [act, dur] = pokeNext(LOBBY_POKE, AXOC.S.ready ? POKE_AXO : POKE_SLIME); LOBBY_POKE.until = now + (dur + 0.3) * 1000;
  if (act === 'hop') { idle.act = null; menuReact = 0.7; AU.pop(); AU.vox(['hup', 'whee', 'hoh'][(Math.random() * 3) | 0], 0.8); return; }
  idle.act = act; idle.dur = dur; idle.u = 0; idle.b0 = beatNow(); idle.f1 = idle.f2 = false; idle.side = Math.random() < 0.5 ? -1 : 1;
  if (act === 'face') emote(P, ['glee', 'smug', 'bonk'][(Math.random() * 3) | 0], dur * 0.8);
  AU.pop(); const v = { wave: 'hoh', proud: 'hoh', tilt: 'ooh', blep: 'giggle', wag: 'giggle', wiggle: 'giggle', look: 'ooh' }[act]; if (v) setTimeout(() => AU.vox(v, 0.7), 140);
}
'''

DRESS = r'''// (v328) a tap on you in the locker's window: the same rule, with what this character can do: a hop, a wave, a hand up, ears up in
// surprise, a blep, a smirk, a sneeze, a wet-dog shake, a twirl. One at a time; taps do nothing until it's done; never the same twice running
const POKE_DRESS = [['hop', 0.75], ['wave', 1.6], ['hand', 1.3], ['ears', 1.3], ['blep', 1.4], ['smirk', 1.4], ['sneeze', 1.9], ['shake', 1.3], ['twirl', 1.1]];
const DRESS_POKE = { q: [], last: '', n: 0, until: 0 };
function sgActEnd() { const a = SGD.act; SGD.act = null; SGD.actFace = null; if (!a || !SGD.built) return; const ip = SGD.A.D.ip; ip.hop = 0; ip.wave = 0; ip.hand = 0; ip.earUp = 0; ip.sq = null; ip.rise = null; }
function sgDressPoke() {
  if (!SGD.built) return; const now = performance.now(); if (now < DRESS_POKE.until) return; // (still busy with the last one)
  const [k, dur] = pokeNext(DRESS_POKE, reduceMotion ? POKE_DRESS.filter(x => x[0] !== 'twirl') : POKE_DRESS); DRESS_POKE.until = now + (dur + 0.25) * 1000;
  sgActEnd(); SGD.act = { k, dur, t: 0, f1: false, side: Math.random() < 0.5 ? -1 : 1, y0: wrapA(SGD.dyaw) }; SGD.moodT = 0; SGD.fzT = 0;
  if (k === 'twirl') { SGD.dyaw = SGD.act.y0; SGD.dyawTo = null; SGD.dV = 0; }
  AU.pop(); const v = { hop: ['hup', 'whee'], wave: ['hoh'], hand: ['ooh'], ears: ['eep'], blep: ['giggle'], smirk: ['hoh'], twirl: ['whee'] }[k];
  if (v) setTimeout(() => { if (lkOn()) AU.vox(v[(Math.random() * v.length) | 0], 0.75); }, 90);
}
// each frame of it: the body's part here (its pose, a hand, the ears, a twirl); its face goes on over the mood's
function sgActStep(dt) {
  const a = SGD.act; if (!a) return; a.t += dt; const u = Math.min(1, a.t / a.dur), D = SGD.A.D, ip = D.ip, k = smoothstep(0.04, 0.2, u) * (1 - smoothstep(0.78, 0.96, u)), I = SGD.A.V.slime, AX = I && I.ax && I.ax.A;
  ip.hop = 0; ip.wave = 0; ip.hand = 0; ip.earUp = 0; ip.sq = null; ip.rise = null; SGD.actFace = null;
  if (a.k === 'hop') { ip.hop = Math.sin(u * Math.PI) * 0.42; ip.sq = u > 0.84 ? (u - 0.84) / 0.16 * 0.45 : null; SGD.actFace = 'glee'; if (u > 0.9 && !a.f1) { a.f1 = true; D.wob = Math.max(D.wob, 0.5); } }
  else if (a.k === 'wave') { ip.wave = k; SGD.actFace = k > 0.2 ? 'happy' : null; }
  else if (a.k === 'hand') { ip.hand = a.side * k; SGD.actFace = k > 0.2 ? 'curious' : null; }
  else if (a.k === 'ears') { ip.earUp = k; SGD.actFace = u < 0.55 ? 'startle' : 'cute'; if (!a.f1) { a.f1 = true; if (AX) AX.kickGills(0, 1.0); } }
  else if (a.k === 'blep') { SGD.actFace = k > 0.25 ? 'blep' : null; if (u > 0.12 && !a.f1) { a.f1 = true; if (AX) AX.twT = 0; } }
  else if (a.k === 'smirk') { ip.rise = 0.1 * k; SGD.actFace = k > 0.3 ? 'smirk' : null; }
  else if (a.k === 'sneeze') { const pre = (0.55 * smoothstep(0.08, 0.2, u) + 0.45 * smoothstep(0.27, 0.4, u)) * (u < 0.45 ? 1 : 0), hit = u >= 0.45 ? Math.exp(-(u - 0.45) * 12) : 0;
    ip.rise = 0.12 * pre; ip.sq = 0.4 * hit; SGD.actFace = u < 0.08 ? null : u < 0.45 ? 'sneeze' : u < 0.62 ? 'dizzy' : 'cute';
    if (u >= 0.45 && !a.f1) { a.f1 = true; AU.pop(); AU.splat(0.3); if (AX) AX.kickGills(0, -1.3); const fx = Math.sin(D.yaw), fz = Math.cos(D.yaw); // (a puff of paint from its nose)
      if (!reduceMotion) for (let i = 0; i < 8; i++) sgPart(fx * 0.32, 0.42, fz * 0.32, fx * (1.4 + Math.random()) + (Math.random() - 0.5), 0.5 + Math.random() * 0.8, fz * (1.4 + Math.random()) + (Math.random() - 0.5), 0.32, SGD.A.col, 0.3 + Math.random() * 0.2); } }
  else if (a.k === 'shake') { if (!a.f1) { a.f1 = true; if (I && I.shake) I.shake(0.9); AU.vox('brr', 0.6); } SGD.actFace = 'shake'; }
  else if (a.k === 'twirl') { const e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2; SGD.dyaw = a.y0 + a.side * 6.2832 * e; SGD.dHold = 0.4; SGD.actFace = 'glee'; if (u >= 1) SGD.dyaw = a.y0; }
  if (u >= 1) sgActEnd();
}
'''

def apply(s):
    # ---- the lobby: the tap plays one reaction from the round
    s = rep(s, "const endLookDrag = e => {", LOBBY + "const endLookDrag = e => {")
    s = rep(s, "AU.init(); menuReact = 0.7; AU.pop(); if (Math.random() < 0.6) AU.vox(['hup', 'whee', 'giggle', 'hoh'][(Math.random() * 4) | 0]); } lookDrag = null; } };",
        "AU.init(); lobbyPoke(); } lookDrag = null; } }; // (v328)")
    # ---- the locker page's window
    s = rep(s, "function sgDressPoke() { if (!SGD.built) return; const D = SGD.A.D; D.squash = 0.7; D.wob = 1; SGD.mood = ['glee', 'smirk', 'blep', 'cute'][(Math.random() * 4) | 0]; SGD.moodT = 1; AU.pop(); if (Math.random() < 0.7) AU.vox(['hup', 'whee', 'giggle', 'hoh'][(Math.random() * 4) | 0]); }\n", DRESS)
    s = rep(s, "function sgDress(dt) {\n  const A = SGD.A, D = A.D; SGD.t += dt; if (SGD.shk > 0) SGD.shk = Math.max(0, SGD.shk - dt * 3);\n",
        "function sgDress(dt) {\n  const A = SGD.A, D = A.D; SGD.t += dt; if (SGD.shk > 0) SGD.shk = Math.max(0, SGD.shk - dt * 3);\n  sgActStep(dt); // (v328: a tap's reaction)\n")
    s = rep(s, "  if (SGD.moodT > 0) { SGD.moodT -= dt; D.ip.expr = SGD.mood; } else D.ip.expr = SGD.dDrag ? 'curious' : 'happy';\n",
        "  if (SGD.moodT > 0) { SGD.moodT -= dt; D.ip.expr = SGD.mood; } else D.ip.expr = SGD.dDrag ? 'curious' : 'happy';\n  if (SGD.actFace) D.ip.expr = SGD.actFace;\n")
    # what else happens to you (a try-on, a new paint or eyes, a purchase) takes over from a tap's reaction
    s = rep(s, "function sgDressReact(w) {\n  if (!SGD.built) return; const D = SGD.A.D;", "function sgDressReact(w) {\n  if (!SGD.built) return; sgActEnd(); const D = SGD.A.D;")
    s = rep(s, "function sgDressFace() { if (!SGD.built) return; const D = SGD.A.D;", "function sgDressFace() { if (!SGD.built) return; sgActEnd(); const D = SGD.A.D;")
    s = rep(s, "  if (burst) { const D = SGD.A.D; if (!reduceMotion) sgBurst(", "  if (burst) { sgActEnd(); const D = SGD.A.D; if (!reduceMotion) sgBurst(")
    s = rep(s, "function sgDressCheer() { if (!SGD.built) return; const D = SGD.A.D;", "function sgDressCheer() { if (!SGD.built) return; sgActEnd(); const D = SGD.A.D;")
    s = rep(s, "SGD.dk = 0.6; SGD.popId = null; SGD.mood = 'glee';", "SGD.dk = 0.6; SGD.popId = null; SGD.act = null; SGD.actFace = null; SGD.mood = 'glee';")
    # a drag that gets going stops a reaction under way (a tap doesn't: it waits its turn)
    s = rep(s, "st.addEventListener('pointermove', e => { const g = SGD.dDrag; if (!g || g.id !== e.pointerId) return; const now = performance.now(),",
        "st.addEventListener('pointermove', e => { const g = SGD.dDrag; if (!g || g.id !== e.pointerId) return; if (SGD.act && Math.abs(e.clientX - g.x0) > 6) { sgActEnd(); SGD.dyaw = wrapA(SGD.dyaw); g.y0 = SGD.dyaw; g.x0 = e.clientX; } const now = performance.now(),")
    return s
