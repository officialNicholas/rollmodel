"""v304: five small asks.

- The lesson's first callout, "DRAG to steer, TAP to jump!", stays up 2 seconds longer. It used to fade the instant you started
  steering, before there was time to read the "TAP to jump" half. Now the 2 seconds (game time) start at your first steer, or when
  the step is done if that comes first; then it fades, or, with the step done, goes with its "Nice!". The step itself is done by a
  steer and a jump again: the jump check had ended up inside a comment (v285), so only 14 m of crawling ever ended it.
- No "Now win it!" card. Where it used to come up (a beat after the gift), the lesson match is over: no "Time!", the lesson's own finish
  (Basics Complete) comes up, then the tally and the results as before. The first match stays a win. With no finale to win it in, the
  rival's trail thins out through the lesson as his score (paint plus the knock-out bonus, as the tally adds them up) comes within four
  points of yours, and stops one short of it. If his pounds or his rocket still have him level or ahead at the end, a burst of your
  paint round you puts you in front: real splats on the canvas, so the picture and the numbers agree.
- The locker lesson no longer makes you put the flower on. You put the fangs on, then the locker is yours to play with as before; the
  flower is in Headgear if you want it.
- Three turret hits in a row stun for a second and a half (stars over the head, can't move, the "Stunned!" banner). The three have to
  come from the same turret without one of its shots at you missing in between, and no more than half a second apart. Hits while
  stunned, and in the moment and a half after it (when it can't happen again, as with a roll stun), don't count toward the next one.
- The commissions coin claim runs smooth. The lobby's 3D view holds still under the Commissions window (it sat under a full-screen blur
  that had to be redone every frame as the lobby moved), and the coins fly as compositor animations instead of being moved by script
  every frame, so a busy frame no longer makes them stutter."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

MOVE = r"""    tick(dt) { if (P.st === 'play' && !P.air) tut.moved += Math.hypot(P.x - tut.lx, P.z - tut.lz); tut.lx = P.x; tut.lz = P.z;
      if (Math.abs(steerIn) > 0.3 || keyL || keyR) tut.steered = true; if (P.st === 'play' && P.air && P.vy > 3 && !P.flung && !P.slam) tut.jumped = true; // (a steer and a jump: that is the lesson. v304: the jump half counts again; it had ended up inside a comment, so only 14 m of crawling ended the step)
      const done = (tut.steered && tut.jumped) || tut.moved > 14;
      // (v304) the callout stays 2 seconds longer: from your first steer (it used to go the moment you steered) or from the step being
      // done, whichever comes first. Then it fades, or, with the step done, goes with its "Nice!"
      if (tut.moveFade < 0 && (done || ((Math.abs(steerIn) > 0.12 || keyL || keyR) && tutTip && tutTip.key === 'move'))) tut.moveFade = 2;
      if (tut.moveFade > 0) { tut.moveFade = Math.max(0, tut.moveFade - (dt || 0)); if (tut.moveFade === 0 && !done && tutTip && tutTip.key === 'move') tutFade(); }
      return done && tut.moveFade === 0; } },
"""

LEAD = r"""// (v304) the lesson ends with the gift now, with no finale to win it in, and your first match is a win. Through the lesson the rival's
// trail thins out as his score (paint plus the knock-out bonus, as the tally adds them up) comes within four points of yours, and he
// lays none from about two short of it (his first two points he paints freely). His tank only spends what his trail lays, so he
// doesn't run dry for it. tutLead, as the match ends: if his pounds or his
// rocket still have him level or ahead, a burst of your paint round you puts you in front, real splats, so the canvas and the
// numbers agree
function tutRivK() { const me = teamCov(0) + (P.kos | 0) * KO_PCT, him = teamCov(1) + (H.kos | 0) * KO_PCT, k = clamp((me - 1 - him) / 3, 0, 1); return him < 2 ? 1 : k < 0.3 ? 0 : k; } // (his trail's width, and the paint it uses up)
function tutLead() {
  const short = () => Math.round(teamCov(1)) + (H.kos | 0) * KO_PCT - Math.round(teamCov(0)) - (P.kos | 0) * KO_PCT; // (0 or more: not ahead)
  if (short() < 0) return;
  const on = (P.st === 'play' || P.st === 'hide') && Math.abs(P.x) < ARENA && Math.abs(P.z) < ARENA, cx = on ? P.x : 0, cz = on ? P.z : 0, cy = on ? P.y : surfaceUnder(0, 0, 60, true);
  let n = 0;
  for (let ring = 0; ring <= 6 && short() >= 0; ring++) { const r = ring * 2.2, m = ring ? 6 * ring : 1;
    for (let q = 0; q < m && short() >= 0; q++) { const a = (q + 0.5 * (ring & 1)) / m * 6.2832, x = cx + Math.sin(a) * r, z = cz + Math.cos(a) * r; if (Math.abs(x) > ARENA - 0.6 || Math.abs(z) > ARENA - 0.6) continue;
      const g = surfaceUnder(x, z, cy + 2, true); if (!(g > -Infinity)) continue; addSplat(x, g, z, a, 1.55 + Math.random() * 0.35, dryClock, false, !ring, P.team); n++; } }
  if (!n) return;
  shockwave(cx, cy + 0.1, cz, 2.5 + Math.sqrt(n) * 0.9, TEAMS[P.team].wet); AU.burst(1); AU.splat(1.3); shake = Math.max(shake, 0.25);
  for (let i = 0; i < 24; i++) { const a = i / 24 * 6.2832, v = 3 + Math.random() * 4; spawnPart(cx, cy + 0.3, cz, Math.cos(a) * v, 2 + Math.random() * 3, Math.sin(a) * v, 0.5, tmat(P), 0.6); }
}
"""

STUN = r"""// (v304) three hits in a row from the same turret: seeing stars where you stand for a second and a half, as a roll stun but shorter
// (with the same moment after it when it can't happen again). A shot of that turret's at you that misses breaks the run, and so does
// half a second without a hit
const TURRET_STREAK = 3, TURRET_STUN = 1.5, TURRET_GAP = 0.5;
function turretStun(B, A, nx, nz) {
  if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }
  B.stunT = TURRET_STUN; B.spd = 0; B.turn = 0; B.kx = B.kz = 0; B.squash = 0.8; B.wob = 1; fxKnock(B, nx, nz, 0.6);
  for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; spawnPart(B.x, B.y + 0.5, B.z, Math.cos(a) * 2.6, 1 + Math.random() * 1.5, Math.sin(a) * 2.6, 0.4, puHaloMat, 0.5); }
  if (hearable(A) || hearable(B)) { AU.bonk(1); AU.pop(); } emote(A, 'glee', 1.1);
  if (B === P) { AU.vox('oof'); hitEdge(A); shake = Math.max(shake, 0.3); buzz([25, 30, 25]); banner('Stunned!'); }
  else if (A === P) { buzz(18); banner('Stunned ' + nameOf(B) + '!'); }
}
"""

COINS = r"""function commCoins(btn, from, to) {
  const m = $('commModal'), w = $('commWallet'), num = w && w.querySelector('b'); if (!w || !num || reduceMotion) { if (num) num.textContent = String(to); if (w) kick(w, 'cbump'); return; }
  const mr = m.getBoundingClientRect(), br = btn.getBoundingClientRect(), dc = w.querySelector('.dcoin') || w, wr = dc.getBoundingClientRect(), svg = (dc.querySelector('svg') || {}).outerHTML || '';
  const tx = wr.left + wr.width / 2 - mr.left, ty = wr.top + wr.height / 2 - mr.top, sx = br.left + br.width * 0.5 - mr.left, sy = br.top + br.height * 0.5 - mr.top, N = 10;
  // (v304) each coin's flight is laid down at the start as keyframes along its curve and played by the compositor, so a busy frame
  // can't make it stutter; only the landings (the count, the bump, the clink) run here
  w.dataset.fly = '1'; let landed = 0;
  const land = () => { landed++; const on = !m.hidden; num.textContent = String(Math.round(from + (to - from) * landed / N));
    if (on) { kick(w, 'cbump'); AU.xplay('coin', { v: 0.5, rate: 0.96 + landed * 0.035 }) || (landed % 3 === 1 && AU.pop()); }
    if (landed === N) { num.textContent = String(to); delete w.dataset.fly; if (on) { kick(w, 'cbig'); buzz(15); } } };
  for (let i = 0; i < N; i++) { const el = document.createElement('i'); el.className = 'ccoin'; el.innerHTML = svg; el.style.opacity = '0'; m.appendChild(el);
    const a = -Math.PI / 2 + (Math.random() - 0.5) * 2.6, sp = 60 + Math.random() * 90, x0 = sx + (Math.random() - 0.5) * br.width * 0.5, y0 = sy + (Math.random() - 0.5) * 10, cx = sx + Math.cos(a) * sp * 1.5, cy = sy + Math.sin(a) * sp - 40, s0 = 0.85 + Math.random() * 0.35, rot = (Math.random() - 0.5) * 540, kf = [];
    for (let k = 0; k <= 16; k++) { const u = k / 16, v = 1 - u, x = v * v * x0 + 2 * v * u * cx + u * u * tx, y = v * v * y0 + 2 * v * u * cy + u * u * ty;
      kf.push({ opacity: 1, transform: 'translate(' + (x - 17).toFixed(1) + 'px,' + (y - 17).toFixed(1) + 'px) rotate(' + (rot * u).toFixed(0) + 'deg) scale(' + (s0 * (1 - 0.4 * u * u)).toFixed(3) + ')' }); }
    let an = null; try { an = el.animate(kf, { duration: 600 + Math.random() * 250, delay: i * 50, easing: 'linear' }); } catch (e) {}
    if (!an) { el.remove(); land(); continue; }
    an.onfinish = () => { el.remove(); land(); }; }
}
"""

def apply(s):
    # 1) the steer and jump callout: 2 seconds more (and the jump half of the step counts again)
    s = rep(s, "{ id: 'move', max: 40, enter() { tut.moved = 0; tut.steered = false;",
               "{ id: 'move', max: 40, enter() { tut.moveFade = -1; tut.moved = 0; tut.steered = false;")
    a = s.index("    tick() { if (P.st === 'play' && !P.air) tut.moved += Math.hypot(P.x - tut.lx, P.z - tut.lz);"); b = s.index("      return (tut.steered && tut.jumped) || tut.moved > 14; } },\n", a)
    assert b - a < 900, b - a
    s = s[:a] + MOVE + s[b + len("      return (tut.steered && tut.jumped) || tut.moved > 14; } },\n"):]

    # 2) the lesson ends where the "Now win it!" card came up: straight to Basics Complete, and a win
    s = rep(s, "  { id: 'rest', max: 1e9, enter() { tutHide(); tut.slowK = 1; tut.noTurret = false; if (matchLeft < 28) matchLeft = 28; tut.cardIn = 1.1; tut.card = false; },\n"
               "    tick(dt) { if (tut.cardIn > 0) { tut.cardIn -= dt; if (tut.cardIn <= 0) tutCard(true); }\n"
               "      if (tut.fin) tutFinTick(dt);\n"
               "      const lead = teamCov(0) - teamCov(1), close = lead < 7; TUT_AI.speed = close ? 0.58 : 0.8; TUT_AI.steal = close ? 0.25 : 0.7; TUT_AI.pound = close ? 0 : 0.45; return false; } } // (a beat for the new item banner, then the card; then the rival eases off whenever it is close, so the first win is yours)\n",
               "  { id: 'rest', max: 1e9, enter() { tutHide(); tut.slowK = 1; if (matchLeft < 28) matchLeft = 28; tut.cardIn = 1.1; tut.card = false; },\n"
               "    tick(dt) { if (tut.cardIn > 0) { tut.cardIn -= dt; if (tut.cardIn <= 0) matchLeft = 0; } return false; } } // (a beat for the new item banner, then the match is over. v304: no \"Now win it!\" card and no finale after it: endMatch makes sure you're ahead (tutLead), then the lesson's finish, Basics Complete, then the tally)\n")
    # the tub callout isn't needed in the beat before the end
    s = rep(s, "  const inTub = P.st === 'hide' && !(s.id === 'basin' && tut.basinTip) && s.id !== 'pound' && !(tut.gap > 0) && !tut.card;\n",
               "  const inTub = P.st === 'hide' && !(s.id === 'basin' && tut.basinTip) && s.id !== 'pound' && s.id !== 'rest' && !(tut.gap > 0) && !tut.card; // (v304: the rest step is only the beat before the end now)\n")
    a = "function tutEndMatch() { // (as a match ends)\n"
    s = rep(s, a, LEAD + a)
    s = rep(s, "  if (isShow()) return endShowdown(true);\n  const you = teamCov(0), cpu = teamCov(1), cpu2 = teamCov(2), id = runId,",
               "  if (isShow()) return endShowdown(true);\n  if (tut) tutLead(); // (v304: the lesson's a win)\n  const you = teamCov(0), cpu = teamCov(1), cpu2 = teamCov(2), id = runId,")
    s = rep(s, "  banner(mode === 'solo' ? \"Time's up!\" : 'Time!', '', false); buzz([40, 30, 40]); slow = 0.6;\n",
               "  if (!tutWinDue) banner(mode === 'solo' ? \"Time's up!\" : 'Time!', '', false); buzz([40, 30, 40]); slow = 0.6; // (v304: the lesson ends on its own word, Basics Complete)\n")
    s = rep(s, "  if (mode === 'solo' ? newBest : win > 0) celebrating = true;\n  setTimeout(() => { if (id !== runId || state !== 'dead') return; startTally(); }, 1450);\n}",
               "  if (mode === 'solo' ? newBest : win > 0) celebrating = true;\n  setTimeout(() => { if (id !== runId || state !== 'dead') return; startTally(); }, tutWinDue ? 800 : 1450); // (v304: and that comes up a little sooner)\n}")
    # the rival's trail in the lesson
    s = rep(s, "fy = hugY(fx, fz, D.y); while (D.dist >= SPACING) { D.dist -= SPACING; addPoint(fx, fy, fz",
               "fy = hugY(fx, fz, D.y), rk = tut && D !== P ? tutRivK() : 1; while (D.dist >= SPACING) { D.dist -= SPACING; if (!rk) { D.stroke++; continue; } /* (v304: the lesson's rival, close to your score) */ addPoint(fx, fy, fz")
    s = rep(s, " * (D === P && tut2 ? 0.6 : 1); }", " * (D === P && tut2 ? 0.6 : 1) * (tut && D !== P ? tutRivK() : 1); } /* (v304: and the lesson's rival only uses the paint he lays) */")
    s = rep(s, " * fk, tcode(D), D.rb, [D.x, D.y, D.z]); } }", " * fk * rk, tcode(D), D.rb, [D.x, D.y, D.z]); } }")

    # 3) the flower is yours to wear or not: the locker lesson asks only for the fangs
    s = rep(s, "      if (bought('flower') && myLook.side !== 'flower') { if (lookCat !== 'head') return tutShow('Now the flower. Open Headgear', 'lc-head', 'headg'); return tutShow('Tap the flower to tuck it in', () => tile('flower'), 'wearf'); } // (and the flower, found in the lesson)\n",
               "      // (v304: the flower, found in the lesson, is yours to wear or not: it's in Headgear, nobody makes you)\n")
    s = rep(s, "return tutShow('Open your locker and try on your fangs and flower', 'lookBtn', 'locker');",
               "return tutShow('Open your locker and try on your fangs', 'lookBtn', 'locker');")

    # 4) three turret hits in a row: stunned for a second and a half
    s = rep(s, "  if (B.giantT > 0 || B.immuneT > 0 || safe(B)) { B.wob = 1; return; } // a giant just shrugs it off\n",
               "  if (B.giantT > 0 || B.immuneT > 0 || safe(B)) { B.wob = 1; if (B.tStreak && B.tStreak.by === A) B.tStreak = null; return; } // a giant just shrugs it off (and a roll dodges it: either way the run of hits is broken)\n")
    s = rep(s, "  const stunNow = false;\n",
               "  let stunNow = false; // (v304: hits in a row. Those while seeing stars, or in the moment after, don't count toward the next stun)\n"
               "  if (B.stunT > 0 || B.stunGuard > 0) B.tStreak = null;\n"
               "  else { const k = B.tStreak = B.tStreak && B.tStreak.by === A && runT - B.tStreak.t < TURRET_GAP ? B.tStreak : { by: A, n: 0, t: 0 }; k.n++; k.t = runT; if (k.n >= TURRET_STREAK && B.flatT <= 0 && !B.slam && B.st === 'play') { stunNow = true; B.tStreak = null; } }\n")
    s = rep(s, "  if (B === P) { shake = Math.max(shake, 0.22); buzz([15, 20, 15]); pingTank(1.2); } else if (A === P) buzz(10);\n}\n",
               "  if (B === P) { shake = Math.max(shake, 0.22); buzz([15, 20, 15]); pingTank(1.2); } else if (A === P) buzz(10);\n  if (stunNow) turretStun(B, A, nx, nz);\n}\n" + STUN)
    s = rep(s, "by: D, team: D.team, life: 4,", "by: D, team: D.team, tg: tt.foe, life: 4,")  # (the foe it was aimed at)
    s = rep(s, "    if (gone) shots.splice(i, 1);\n",
               "    if (gone) { if (s.tg && hit !== s.tg && s.tg.tStreak && s.tg.tStreak.by === s.by) s.tg.tStreak = null; shots.splice(i, 1); } // (v304: a shot at someone that missed them breaks their run of hits)\n")

    # 5) the commissions coin claim: smooth
    i = s.index("function commCoins(btn, from, to) {\n"); j = s.index("\nfunction commXp(btn)", i)
    s = s[:i] + COINS.rstrip('\n') + s[j:]
    s = rep(s, "  if (!(state === 'menu' && (menuPage === 'worlds' || menuPage === 'events' || menuPage === 'strokes'))) renderFrame();\n",
               "  if (!(state === 'menu' && (menuPage === 'worlds' || menuPage === 'events' || menuPage === 'strokes' || !commModalEl.hidden))) renderFrame(); // (v304: under Commissions the lobby holds still behind the blur)\n")
    a = "function frameBody(t) {\n"
    s = rep(s, a, "const commModalEl = $('commModal');\n" + a)
    return s
