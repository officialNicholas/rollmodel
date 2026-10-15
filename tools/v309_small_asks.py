"""v309: a quicker launch, a roll when the slingshot has no paint, a clearer knock-out bonus, easier turret aiming, cool reputation
titles and two lesson fixes.

- Launch. The game used to make every shader a match could ever need (about 130) before the menu showed, behind "Lighting the
  gallery". The lobby needs about 10 of them. Now only those are made at launch (two lobby frames drawn behind the loading screen);
  the rest are made in pieces behind Choose Event (which covers the lobby, so nothing shows), or under the wipe into the first match
  if that comes first. Anything that rebuilds the canvas in the lobby before then waits for that too, instead of making everything at
  once in view.
- Out of paint, the slingshot used to refuse ("No paint"). Now the pull works as always and letting go rolls you forward: the dodge
  roll, a little shorter for a short pull and never faster than a roll. The aim ring shows about where it takes you. If the roll is
  still cooling down, a push off instead, so letting go always moves you. A one-time tip says so.
- The tally: the knock-outs are seen being added. "Knock-out bonus" and "+2% for every knock-out" go up over the bar, and each
  knock-out pops up as a star with its +2% over that side's number, flies down into the end of its paint on the bar and lands with a
  splat, the number and the bar going up as it lands. A little slower than before, so each one reads.
- The turret: no more range to set. Shots go onto a rival in front of you (a wider cone than before, at any distance in reach) or,
  with nobody there, sweep near to far to paint a strip. Turning is gentler, slow for small drags and quicker for big ones, so it can
  be aimed finely, and a rival near your line pulls the turret round onto them unless you steer away.
- Reputation: twelve titles, a new one every three ranks, from Fresh Paint to Masterpiece (it used to start at "Unknown").
- The first lesson: flattening the rival also finishes the roll-over step, and after your rocket the rival comes back from its
  knock-out and launches its own rocket in about two seconds instead of about ten.
- Showdown: three hearts each (was two).
- The turret: an X on the pound button takes you out of it (you used to be stuck in it until its time ran out).
- The Paint Trap knocks out whoever sets it off (it used to stun). Online, where only the game server knocks anyone out, it still stuns.
- Strokes: "Unlock everything" at the foot of the page, code 1234: every stroke, every item, and the rank every lock asks for.
- The crash that started the game over: iOS closes a web page that holds too much memory, and the app then loads the game again from
  the start. Two things grew with every match:
  - every canvas played kept its surfaces, lighting and floor art for the rest of the session (in Graphics mode 30 to 60 MB of GPU
    pictures and about 20 MB of page canvases each, eight canvases);
  - the refills, hot puddles and pick-ups were only taken off the scene, never disposed: about 80 meshes left behind per match.
  Now only the canvas in play and the one before keep their pictures (an older one makes them again when it comes round), what leaves
  the stage is disposed, and going to the background (or a memory warning from the phone) lets go of everything not on screen."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

REP = "['Fresh Paint', 'Drip Rookie', 'Splat Kid', 'Street Brush', 'Color Bandit', 'Ink Outlaw', 'Canvas Crusher', 'Neon Menace', 'Splash Tyrant', 'Paint Phantom', 'Chroma Legend', 'Masterpiece']"

LATE = r"""
// (v309) the shaders a match needs, made after launch: in pieces behind Choose Event (it covers the lobby; leaving it pauses them), or
// all at once under the wipe into the first match if that comes first (start, a rematch and an online match each make them there)
var LW = { done: false, busy: false, parts: null, i: 0, asked: false };
const lateWarmOk = () => state === 'menu' && menuPage === 'events' && !irisBusy && !building && !vic;
async function lateWarmBg() {
  if (LW.done || LW.busy || !lateWarmOk()) return; LW.busy = true; let first = true;
  try {
    if (!LW.asked) { LW.asked = true; try { await warmCompile(); } catch (e) {} } // (where the browser can build them in the background, it starts on all of them now)
    if (!LW.parts) { LW.parts = warmPieces(scene, 16); LW.i = 0; }
    while (LW.i < LW.parts.length && lateWarmOk() && !LW.done) { warmRender(LW.parts[LW.i], first ? 2 : 1); first = false; LW.i++; await gpuIdle(5000); }
    if (LW.i >= LW.parts.length && lateWarmOk() && !LW.done) {
      const fl = new Set(), fm = new Set(); for (const f of floaters) for (const m of f.mats) fm.add(m);
      scene.traverse(o => { if (o.material && [].concat(o.material).some(m => fm.has(m))) fl.add(o); });
      warmRender(fl); await gpuIdle(5000); LW.done = true;
    }
  } catch (e) {} finally { LW.busy = false; }
}
"""

DRY = r"""
// (v309) out of paint the slingshot can't throw you, but the pull isn't wasted: letting go rolls you forward (the dodge roll, a little
// shorter for a short pull, never faster than a roll). With the roll still cooling down, a push off instead, so letting go always moves you
function dryRoll(D, c) {
  if (!canAct(D) || D.air) return;
  const k = 0.7 + 0.3 * clamp((c - FLING_MIN) / (1 - FLING_MIN), 0, 1);
  if (dodgeRoll(D)) { D.rollV *= k; D.spd = D.rollV; }
  else if (!(D.rollBuf > 0)) { D.spd = Math.max(D.spd, cfg.speed * spdK(D) * (0.5 + 0.3 * k)); D.grace = 0.35; D.squash = Math.max(D.squash, 0.3); if (D === P) AU.release(); }
  if (D === P) hint('dryroll', 'Out of paint, a pull rolls you on. Refill at a ' + potWord() + ' or on your color', 3);
}
"""

TALLY = r"""
// (v309) each knock-out is seen being added: a star with its +2% pops up over that side's number, flies down into the end of its paint
// on the bar and lands with a splat, the number and the bar going up as it lands
function talKoFly(e) {
  e.shown++; buzz(8);
  if (reduceMotion) return talKoLand(e);
  const r0 = talEl.getBoundingClientRect(), nr = e.nu.getBoundingClientRect(), br = $('tyBar').getBoundingClientRect();
  const f = Math.min(1, (e.cov + (e.landed + 1) * KO_PCT) / tal.scale), fx = e.side === 'l' ? f : e.side === 'r' ? 1 - f : (e.c || 0.5) + f / 2;
  const x0 = nr.left + nr.width / 2 - r0.left, y0 = nr.top - r0.top - 4, x1 = br.left + br.width * fx - r0.left, y1 = br.top + br.height / 2 - r0.top;
  const q = document.createElement('i'), at = (x, y, s) => 'translate(' + x.toFixed(0) + 'px,' + y.toFixed(0) + 'px) scale(' + s + ')';
  q.className = 'tykofly'; q.innerHTML = KO_SVG + '<b>+' + KO_PCT + '%</b>'; q.style.transform = at(x0, y0, 0.4); talEl.appendChild(q);
  requestAnimationFrame(() => requestAnimationFrame(() => { q.style.transform = at(x0, y0 - 30, 1.15); }));
  const id = tal.id;
  setTimeout(() => { if (!tal || tal.id !== id) return q.remove(); q.classList.add('go'); q.style.transform = at(x1, y1, 0.55); }, 260);
  setTimeout(() => { q.remove(); if (tal && tal.id === id && e.landed < e.shown) talKoLand(e); }, 560);
}
function talKoLand(e) {
  e.landed++; AU.tslice(); buzz(12); restartCls(e.nu, 'tick');
  if (!e.chip) { e.chip = document.createElement('i'); e.chip.className = 'tyko'; e.nu.appendChild(e.chip); }
  e.chip.innerHTML = KO_SVG + '+' + (e.landed * KO_PCT) + '%'; restartCls(e.chip, 'pop');
  tySplat(e, Math.min(1, (e.cov + e.landed * KO_PCT) / tal.scale));
}
"""

UNLOCK = r"""
// (v309) Strokes: the code that unlocks everything, for testing (as Customize's does for items): every stroke owned and nothing on the
// bench, every item, and the rank every lock asks for (Strokes, the modes, commissions, each transform). A lesson under way is left alone
function stUnlockAll() {
  const d = strokesOf(); for (const o of [...SPECIALS, ...SKILLS, ...ST_ITEMS]) if (!d.own.includes(o.id)) d.own.push(o.id); d.craft = null;
  for (const w of ITEMS) { OWNED.add(w.id); BOUGHT.add(w.id); } store.owned = [...OWNED]; store.bought = [...BOUGHT];
  const need = Math.max(ABIL_RANK, COMM_RANK, ...ST_ITEMS.map(o => stRank(o))); if (repOf(store.xp || 0).lv < need) { let xp = 0; for (let l = 1; l < need; l++) xp += xpNeed(l); store.xp = xp; }
  save(); renderStrokes(); try { paintAbil(); paintPBar(); } catch (e) {}
}
setTimeout(() => {
  $('stUnlockLink').addEventListener('click', () => { AU.init(); AU.ui(); $('stUnlockLink').hidden = true; $('stUnlockForm').hidden = false; setTimeout(() => $('stUnlockCode').focus(), 30); });
  $('stUnlockCode').addEventListener('keydown', e => e.stopPropagation());
  $('stUnlockForm').addEventListener('submit', e => { e.preventDefault(); const v = $('stUnlockCode').value.trim();
    if (v === '1234') { stUnlockAll(); $('stUnlockCode').value = ''; $('stUnlockForm').hidden = true; $('stUnlockLink').hidden = false; AU.pop(); stToast('Everything is unlocked'); }
    else { AU.nope(); kick($('stUnlockForm'), 'nope'); stToast("That code doesn't work"); } });
}, 0);
"""

CSS = r"""
/* (v309) the turret's way out: an X on the pound button */
.slamBtn .sbx{display:none;position:absolute;left:50%;top:50%;width:44%;height:44%;transform:translate(-50%,-50%);pointer-events:none}
.slamBtn .sbx::before,.slamBtn .sbx::after{content:'';position:absolute;left:50%;top:50%;width:100%;height:20%;border-radius:99px;background:#fff;box-shadow:0 0 0 3px #171320;transform:translate(-50%,-50%) rotate(45deg)}
.slamBtn .sbx::after{transform:translate(-50%,-50%) rotate(-45deg)}
.slamBtn.tx .sbx{display:block}
.slamBtn.tx svg,.slamBtn.tx .sbdial{visibility:hidden}
/* (v309) Strokes: the unlock code at the foot of the page */
#mStrokes .stucode{grid-column:1/-1;margin:6px 0 4px}
/* (v309) the knock-out bonus, seen being added */
.tyword.ko{color:var(--gold);font-size:clamp(28px,8.4vw,54px)}
.tyword.ko svg{width:.8em;height:.8em;fill:var(--gold);stroke:var(--black);stroke-width:1.5px;vertical-align:-.1em;margin-right:.2em;filter:drop-shadow(2px 2px 0 var(--black))}
.tykofly{position:absolute;left:0;top:0;z-index:5;display:flex;align-items:center;gap:3px;margin:-18px 0 0 -34px;padding:4px 10px 4px 5px;border-radius:999px;background:var(--gold);border:2.5px solid var(--black);box-shadow:3px 3px 0 var(--black);font:400 21px/1 var(--font-display);color:#171320;pointer-events:none;white-space:nowrap;transition:transform .24s cubic-bezier(.2,1.6,.4,1);will-change:transform}
.tykofly svg{width:22px;height:22px;fill:#fff;stroke:var(--black);stroke-width:1.6px}
.tykofly b{font-weight:400}
.tykofly.go{transition:transform .3s cubic-bezier(.55,0,.85,.35)}
.tyko{font-size:22px}
.tyko svg{width:.9em;height:.9em;fill:var(--gold);stroke:var(--black);stroke-width:1.5px;vertical-align:-.12em;margin-right:2px}
"""

MEM = r"""
// (v309) memory. A phone gives the game only so much, and past that iOS closes it: it starts again from the loading screen. Every
// canvas played used to keep its surfaces, lighting and floor art for the rest of the session (in Graphics mode tens of MB of pictures
// each, eight canvases). Now the canvas in play and the one before it keep theirs; an older one lets go of them (made again, as on its
// first visit, if it comes round again). Going to the background, or a memory warning from the phone, lets go of all but the one in play
let thLru = [], thQ = 0;
function themeSoon() { clearTimeout(thQ); thQ = setTimeout(() => themeTrim(2), 0); } // (once the stage is built: a layout can try several canvases)
function themeTrim(keep) { if (!TH) return; thLru = [TH].concat(thLru.filter(T => T !== TH)); while (thLru.length > keep) themeFree(thLru.pop()); }
const texIn = (m, out) => { for (const k in m) { const v = m[k]; if (v && v.isTexture) out.add(v); } const u = m.uniforms; if (u) for (const k in u) { const v = u[k] && u[k].value; if (v && v.isTexture) out.add(v); } return out; };
function themeMatsOf(T, out) {
  const add = v => { if (!v) return; if (v.isMaterial) out.add(v); else if (Array.isArray(v)) v.forEach(add); else if (v instanceof Map) v.forEach((a, b) => { add(a); add(b); }); };
  if (T.mats) for (const k in T.mats) add(T.mats[k]); add(T.decal); add(T.scat); return out;
}
function themeFree(T) {
  if (!T || T === TH) return;
  try {
    // what's still in use stays: anything in the scene (the canvas in play, the characters, the lobby) and the other canvas kept
    const keepM = new Set(), keepT = new Set(); for (const K of thLru) if (K !== T) themeMatsOf(K, keepM);
    scene.traverse(o => { const m = o.material; if (m) for (const x of [].concat(m)) keepM.add(x); }); for (const m of keepM) texIn(m, keepT);
    const mine = themeMatsOf(T, new Set()), tex = new Set(), own = new Set(); for (const m of mine) texIn(m, tex);
    if (T.decal && T.decal.map) own.add(T.decal.map); if (T.scat && T.scat.map) own.add(T.scat.map);
    for (const id of new Set([...(T.sf || []), ...(T.sfUsed || [])])) { const sv = SURF[id]; if (!sv) continue; const ts = Object.values(sv).filter(v => v && v.isTexture);
      if (ts.some(t => keepT.has(t))) continue; ts.forEach(t => { tex.add(t); own.add(t); }); delete SURF[id]; }
    for (const m of mine) if (!keepM.has(m)) m.dispose();
    for (const t of tex) { if (keepT.has(t) || t.isRenderTargetTexture) continue; t.dispose(); const c = t.image; if (own.has(t) && c && c.getContext) c.width = c.height = 0; } // (its own pictures: their pixels go now, not whenever)
    T.mats = null; T.decal = null; T.scat = null; T.sfUsed = null;
    if (T.envRT) { T.envRT.dispose(); T.envRT = null; } if (T.charRT) { T.charRT.dispose(); T.charRT = null; }
  } catch (e) { console.warn('themeFree', e); }
}
function memTrim() { try { AU.trim(); } catch (e) {} themeTrim(1); }
"""

DROP = r"""
// (v309) what leaves the stage (the refills and hot puddles between matches, pick-ups as they're taken or replaced) gives back its GPU
// copy. They were only taken off the scene, and every match left about 80 meshes' worth behind. Pieces shared with what's still out stay
const dropQ = []; let dropT = 0;
function dropTree(list) {
  for (const r of list) if (r) { if (r.parent) r.parent.remove(r); r.traverse(o => { if (o.geometry) dropQ.push(o.geometry); }); }
  if (dropQ.length && !dropT) dropT = setTimeout(dropFlush, 0); // (once the new ones are out, so a piece they share is seen in use)
}
function dropFlush() { dropT = 0; if (!dropQ.length) return; const live = new Set(); scene.traverse(o => { if (o.geometry) live.add(o.geometry); }); for (const g of dropQ.splice(0)) if (!live.has(g)) g.dispose(); }
"""

def apply(s):
    # ---------------- launch: the lobby first, the rest later
    s = rep(s, "bootTo(Math.max(0.86, bootPos()), 0.93, 3500, 'Lighting the gallery'); await warmCompile(); // (v256)\n"
               "{ const p0 = Math.min(0.93, Math.max(0.86, bootPos())), p1 = FL && FL.due ? 0.96 : 0.99; // (v269: in pieces, the bar moving with them)\n"
               "  try { await warmSteps(p0, p1, 'Lighting the gallery'); } catch (e) { try { warmRender(); } catch (x) {} }\n"
               "  if (FL && FL.due && FL.prep) try { await FL.prep(p1, 0.99, 'Setting the scene'); } catch (e) {} }\n",
               "bootTo(Math.max(0.86, bootPos()), 0.93, 1500, 'Lighting the gallery');\n"
               "// (v309) only what the lobby shows is made at launch: two lobby frames drawn behind the loading screen (about ten shaders). The\n"
               "// other hundred and more, everything a match can need, are made behind Choose Event or under the wipe into the first match (lateWarmBg)\n"
               "try { renderFrame(); await gpuIdle(4000); renderFrame(); await gpuIdle(4000); } catch (e) {}\n"
               "{ const p1 = FL && FL.due ? 0.96 : 0.99; bootTo(p1, p1, 0, 'Lighting the gallery');\n"
               "  if (FL && FL.due && FL.prep) try { await FL.prep(p1, 0.99, 'Setting the scene'); } catch (e) {} }\n")
    s = rep(s, "let warmQ = 0, bootWarm = false; const queueWarm = () => { clearTimeout(warmQ); if (bootWarm) warmQ = setTimeout(warmRender, 30); };",
               LATE.lstrip('\n') + "let warmQ = 0, bootWarm = false; const queueWarm = () => { clearTimeout(warmQ); if (bootWarm && LW.done) warmQ = setTimeout(warmRender, 30); }; // (v309: until the late warm-up is done, a rebuilt canvas waits for it)")
    s = rep(s, "  warming = false; if (lobbyOn()) try { renderFrame(); } catch (e) {}\n}\n// (v269) the warm-up at the end of loading, in pieces.",
               "  warming = false; if (lobbyOn()) try { renderFrame(); } catch (e) {}\n  if (!only) LW.done = true; // (v309: the whole warm-up has run)\n}\n// (v269) the warm-up at the end of loading, in pieces.")
    s = rep(s, "evArt(); evFold(); evLockPaint(); acMatchPaint(); requestAnimationFrame(evMoreTick);",
               "evArt(); evFold(); evLockPaint(); acMatchPaint(); requestAnimationFrame(evMoreTick); setTimeout(lateWarmBg, 700); /* (v309: the match's shaders, behind this page) */")
    s = rep(s, "    if (mapUsed) { building = true; freshMap(); clearTimeout(warmQ); warmRender(); building = false; }\n    showVS(beginMatch);",
               "    if (mapUsed) { building = true; freshMap(); clearTimeout(warmQ); warmRender(); building = false; }\n    else if (!LW.done) { clearTimeout(warmQ); warmRender(); } // (v309: the first match makes what launch left for later)\n    showVS(beginMatch);")

    # ---------------- out of paint: the pull rolls you on
    s = rep(s, "  if (D.dry && D.st !== 'hide') { if (D === P) { (kick($('ttrack'), 'nope'), pingTank(1.6)); AU.nope(); popText('No paint'); } return; }",
               "  D.dryPull = false;\n  if (D.dry && D.st !== 'hide') { if (D !== P || D.ai) return; D.dryPull = true; } // (v309: out of paint the pull is still yours, and letting go rolls you on: dryRoll)")
    s = rep(s, "function fling(D, cIn) {\n  if (!D.charging) return;\n  let c = cIn !== undefined ? cIn : D.charge; clearCharge(D);",
               DRY.lstrip('\n') + "function fling(D, cIn) {\n  if (!D.charging) return;\n  let c = cIn !== undefined ? cIn : D.charge; clearCharge(D);\n  if (D.dryPull) { D.dryPull = false; if (D.dry && D.st === 'play') return dryRoll(D, c); }")
    s = rep(s, "    const aiming = P.charging && P.charge > 0.03;\n    if (aiming && P.air && P.airSling) {",
               "    const aiming = P.charging && P.charge > 0.03;\n"
               "    if (aiming && P.dryPull) { // (v309) out of paint: the ring sits about where the roll takes you, on the ground ahead, and no arc\n"
               "      const c = Math.max(FLING_MIN, P.charge), L = DRY_RING[0] + DRY_RING[1] * c, fx = Math.sin(P.yaw), fz = Math.cos(P.yaw), gy = surfaceUnder(P.x + fx * L, P.z + fz * L, P.y + STEP, true);\n"
               "      aimIn.material.color.setHex(0xFFFFFF); aimRing.position.set(P.x + fx * L, (gy > -Infinity ? gy : P.y) + 0.11, P.z + fz * L); aimRing.scale.setScalar(0.42 + 0.16 * c); aimRing.visible = true;\n"
               "      if (arcDots[0].visible) arcDots.forEach(d => { d.visible = false; });\n"
               "    } else if (aiming && P.air && P.airSling) {")
    s = rep(s, "function slingShow(cx, cy) { slingEl.style.setProperty('--sl', TEAMS[P.team].css);",
               "const DRY_RING = [1.5, 1.6]; // (v309: how far the roll goes, at the shortest pull and added at the full one)\nfunction slingShow(cx, cy) { slingEl.style.setProperty('--sl', P.dryPull ? '#8E899C' : TEAMS[P.team].css); /* (v309: grey with no paint in it) */")

    # ---------------- the tally: the knock-outs seen going in
    s = rep(s, "const KO0 = 2.7, KOD = 0.46, KOEND = KO0 + (koq.length ? koq.length * KOD + 0.7 : 0.8);",
               "const KO0 = 2.7, KOD = 0.62, KOEND = KO0 + (koq.length ? 0.4 + koq.length * KOD + 0.9 : 0.8); // (v309: a beat for the caption, and each one slow enough to read)")
    s = rep(s, "hi: colVars(D)[1], shown: 0, num: -1 }));", "hi: colVars(D)[1], shown: 0, landed: 0, num: -1 }));")
    s = rep(s, "$('tyGain').className = 'tygain'; talEl.querySelectorAll('.tyfly').forEach(q => q.remove());",
               "$('tyGain').className = 'tygain'; talEl.querySelectorAll('.tyfly,.tykofly').forEach(q => q.remove()); $('tyWord').className = 'tyword';")
    s = rep(s, "  const nk = t >= tal.KO0 ? clamp(Math.floor((t - tal.KO0) / tal.KOD) + 1, 0, tal.koq.length) : 0;\n"
               "  for (let i = tal.nk; i < nk; i++) { const e = tal.koq[i]; e.shown++; AU.tslice(); buzz(12); restartCls(e.nu, 'tick');\n"
               "    if (!e.chip) { e.chip = document.createElement('i'); e.chip.className = 'tyko'; e.nu.appendChild(e.chip); } e.chip.textContent = '+' + (e.shown * KO_PCT) + '%'; restartCls(e.chip, 'pop'); }\n"
               "  tal.nk = nk;\n"
               "  const segs = [];\n"
               "  for (const e of tal.ppl) { const cov = e.cov * k, f = Math.min(1, (cov + e.shown * KO_PCT) / tal.scale); segs.push(tySeg(e, f));\n"
               "    const num = Math.round(cov) + e.shown * KO_PCT; if (num !== e.num) { e.num = num; e.nu.firstChild.textContent = num + '%'; } }",
               "  if (t >= tal.KO0 && tal.koq.length && !tal.koCap) { tal.koCap = true; tal.sub0 = $('tySub').innerHTML; const w = $('tyWord'); w.innerHTML = KO_SVG + 'Knock-out bonus'; w.className = 'tyword ko'; restartCls(w, 'in'); $('tySub').innerHTML = '<b>+' + KO_PCT + '%</b> for every knock-out'; AU.pop(); } // (v309: said out loud first)\n"
               "  const nk = t >= tal.KO0 + 0.4 ? clamp(Math.floor((t - tal.KO0 - 0.4) / tal.KOD) + 1, 0, tal.koq.length) : 0;\n"
               "  for (let i = tal.nk; i < nk; i++) talKoFly(tal.koq[i]);\n"
               "  tal.nk = nk;\n"
               "  if (t >= tal.KOEND) for (const e of tal.ppl) while (e.landed < e.shown) talKoLand(e); // (skipped ahead: what's still in the air lands now)\n"
               "  const segs = [];\n"
               "  for (const e of tal.ppl) { const cov = e.cov * k, f = Math.min(1, (cov + e.landed * KO_PCT) / tal.scale); segs.push(tySeg(e, f));\n"
               "    const num = Math.round(cov) + e.landed * KO_PCT; if (num !== e.num) { e.num = num; e.nu.firstChild.textContent = num + '%'; } }")
    s = rep(s, "  if (t >= tal.KOEND && tal.phase === 2) { tal.phase = 3; talWinner(); }",
               "  if (t >= tal.KOEND && tal.phase === 2) { tal.phase = 3; if (tal.koCap) { const w = $('tyWord'); w.textContent = ''; w.className = 'tyword'; $('tySub').innerHTML = tal.sub0 || ''; } talWinner(); }")
    s = rep(s, "// a splash of its paint where a slice lands on the bar\nfunction tySplat(e, f) {",
               TALLY.lstrip('\n') + "// a splash of its paint where a slice lands on the bar\nfunction tySplat(e, f) {")

    # ---------------- the turret: automatic range, lock-on, gentle turning, a soft pull onto a rival
    s = rep(s, "banner('Turret!', say('Drag to aim, up and down for range', 'Arrow keys to aim'));",
               "banner('Turret!', say('Drag to turn. It locks onto rivals in front', 'Left and right to turn. It locks onto rivals in front'));")
    s = rep(s, "  if (D.ai) d = 7 + 5 * (0.5 + 0.5 * Math.sin(T.ph)); else d = TURRET_NEAR + (TURRET_FAR - TURRET_NEAR) * (T.aim === undefined ? 0.4 : T.aim);",
               "  if (D.ai) d = 7 + 5 * (0.5 + 0.5 * Math.sin(T.ph)); else d = TURRET_NEAR + 1.5 + (TURRET_FAR - TURRET_NEAR - 4) * (0.5 + 0.5 * Math.sin(T.ph * 0.8)); // (v309: yours sweep near to far too: no range to set)")
    s = rep(s, "  const tg = coneFoe(D, D.ai ? 0.22 : 0.3, TURRET_FAR + 1);\n  if (tg && (D.ai || Math.abs(tg.d - d) < 4.5)) {",
               "  const tg = coneFoe(D, D.ai ? 0.22 : 0.45, TURRET_FAR + 1);\n  if (tg) { /* (v309: yours lock onto a rival in front at any distance in reach) */")
    s = rep(s, "  if (!D.ai) T.aim = clamp((T.aim === undefined ? 0.4 : T.aim) + (aimKey || rangeIn) * dt * 1.2, 0, 1);",
               "  // (v309) a rival near your line pulls the turret round onto them (where they're going), less the harder you steer\n"
               "  if (!D.ai && D.st === 'play') { const tg = coneFoe(D, 0.75, TURRET_FAR + 1); if (tg) { const O = tg.O, lead = Math.min(0.6, tg.d / SHOT_V), err = wrapA(Math.atan2(O.x + Math.sin(O.yaw) * O.spd * lead - D.x, O.z + Math.cos(O.yaw) * O.spd * lead - D.z) - D.yaw), r = 2.4 * Math.max(0, 1 - Math.abs(steerIn) * 1.6 - (keyL || keyR ? 1 : 0)) * dt; D.yaw += clamp(err, -r, r); } }")
    s = rep(s, "agile = D.turret && !D.air ? 0.85 :",
               "agile = D.turret && !D.air ? (D === P && !P.ai ? 0.66 * Math.min(1, 0.3 + Math.abs(input)) : 0.85) :") # (v309: yours: slow for a small drag, quicker for a big one)

    # ---------------- reputation titles
    s = rep(s, "const REP_NAMES = ['Unknown', 'Local talent', 'Rising star', 'Crowd pleaser', 'Headliner', 'Master'];",
               "const REP_NAMES = " + REP + "; // (v309: a new one every three ranks)")
    s = rep(s, 'id="repName">Unknown<', 'id="repName">Fresh Paint<')
    s = rep(s, '<b id="repRowName">Unknown</b>', '<b id="repRowName">Fresh Paint</b>')

    # ---------------- the first lesson
    s = rep(s, "{ id: 'rollover', max: 45, enter() { tutHide(); tut.slowK = 1; tut.sub = ''; tut.rAim = true; tut.kos0 = P.kos;",
               "{ id: 'rollover', max: 45, enter() { tutHide(); tut.slowK = 1; tut.sub = ''; tut.rAim = true; tut.kos0 = P.kos; tut.flat0 = P.flatted;")
    s = rep(s, "tick(dt) { if (P.kos > tut.kos0) return true;",
               "tick(dt) { if (P.kos > tut.kos0 || P.flatted > (tut.flat0 || 0)) return true; /* (v309: flattening him does it too) */")
    s = rep(s, "{ id: 'free3', max: 99, enter() { tutHide(); tut.slowK = 1; tut.wait = 8; }",
               "{ id: 'free3', max: 99, enter() { tutHide(); tut.slowK = 1; tut.wait = 1.2; } /* (v309: was 8 s) */")
    s = rep(s, "    tick() { if (!tut.rkStarted && H.st === 'play' && !H.rocket) { H.paint = 1; startRocket(H); tut.rkStarted = true; }",
               "    tick() { if (!tut.rkStarted) { if (H.st === 'ko' && H.koT > 0.9) H.koT = 0.9; if (H.st === 'hide' && H.pot) exitPot(H); } // (v309: back quickly from your rocket's knock-out, and straight out of the basin)\n"
               "      if (!tut.rkStarted && H.st === 'play' && !H.rocket) { H.paint = 1; startRocket(H); tut.rkStarted = true; }")

    # ---------------- Showdown: three hearts each
    s = rep(s, "const SD_HEARTS = 2,", "const SD_HEARTS = 3, /* (v309: was 2) */")
    s = rep(s, "['ffa', 'Showdown', 'Four of you, two hearts each'], ['duo', 'Showdown 2v2', 'You and a teammate, two hearts each']",
               "['ffa', 'Showdown', 'Four of you, three hearts each'], ['duo', 'Showdown 2v2', 'You and a teammate, three hearts each']")
    s = rep(s, "'Two against two, two hearts each.", "'Two against two, three hearts each.")
    s = rep(s, "'Four of you, two hearts each. A knock-out", "'Four of you, three hearts each. A knock-out")
    s = rep(s, "<small>Two hearts each</small>", "<small>Three hearts each</small>")
    s = rep(s, "'Last one standing!', 'Two hearts each', true)", "'Last one standing!', 'Three hearts each', true)")

    # ---------------- the turret: an X on the pound button gets you out of it
    s = rep(s, "function useSlam(D) {\n", "function useSlam(D) {\n  if (D.turret && D === P && !D.ai && D.st === 'play') { D.turret.t = 0; AU.pop(); buzz(8); return true; } // (v309: the X: out of the turret now)\n")
    s = rep(s, "  const rk = P.rocket, ready = rk ? rk.ph === 'hover' || (rk.ph === 'dive' && rk.slow) : slamReady(P),",
               "  const tx = !!P.turret && P.st === 'play'; if (b._tx !== tx) { b._tx = tx; b.classList.toggle('tx', tx); if (tx && !b.querySelector('.sbx')) { const x = document.createElement('i'); x.className = 'sbx'; x.setAttribute('aria-hidden', 'true'); b.appendChild(x); } wasReady = null; } // (v309: in a turret the button is its way out)\n"
               "  const rk = P.rocket, ready = tx ? true : rk ? rk.ph === 'hover' || (rk.ph === 'dive' && rk.slow) : slamReady(P),")
    s = rep(s, "    if (!rk && P.st === 'play' && !P.slam && P.paint >= POUND_MIN && P.slamCD > 0 && P.slamMax > 0) {",
               "    if (!rk && !tx && P.st === 'play' && !P.slam && P.paint >= POUND_MIN && P.slamCD > 0 && P.slamMax > 0) {")
    s = rep(s, "b.setAttribute('aria-label', rk ? 'Boost down' :", "b.setAttribute('aria-label', tx ? 'Leave the turret' : rk ? 'Boost down' :")

    # ---------------- the Paint Trap knocks you out (online, where only the game server knocks anyone out, it still stuns)
    s = rep(s, "const KO_MSG = { zone: 'Caught outside!',", "const KO_MSG = { trap: 'Trapped!', zone: 'Caught outside!',")
    s = rep(s, "const CPU_KO_MSG = { zone: n => n + ' got caught outside',", "const CPU_KO_MSG = { trap: n => 'Trapped ' + n + '!', zone: n => n + ' got caught outside',")
    s = rep(s, "  if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }\n  const l = Math.hypot(B.x - T.x, B.z - T.z), nx = l > 0.05 ? (B.x - T.x) / l : Math.sin(B.yaw), nz = l > 0.05 ? (B.z - T.z) / l : Math.cos(B.yaw);\n  B.stunT = Math.max(B.stunT || 0, TRAP_STUN);",
               "  if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }\n  if (!NM) { emote(T.owner, 'glee', 0.9); hitStop(0.06, T.owner, B); return knockOut(B, 'trap', T.owner); } // (v309: a trap is a knock-out now)\n  const l = Math.hypot(B.x - T.x, B.z - T.z), nx = l > 0.05 ? (B.x - T.x) / l : Math.sin(B.yaw), nz = l > 0.05 ? (B.z - T.z) / l : Math.cos(B.yaw);\n  B.stunT = Math.max(B.stunT || 0, TRAP_STUN);")

    # ---------------- Strokes: a code that unlocks everything, for testing
    s = rep(s, "          <div class=\"strail\" id=\"stItemRail\" role=\"tabpanel\" aria-labelledby=\"stItem\" hidden></div>\n        </section>\n",
               "          <div class=\"strail\" id=\"stItemRail\" role=\"tabpanel\" aria-labelledby=\"stItem\" hidden></div>\n        </section>\n"
               "        <div class=\"ucode stucode\"><button class=\"ulink\" id=\"stUnlockLink\" type=\"button\">Unlock everything</button><form class=\"uform\" id=\"stUnlockForm\" hidden><input id=\"stUnlockCode\" type=\"text\" inputmode=\"numeric\" maxlength=\"8\" autocomplete=\"off\" placeholder=\"Code\" aria-label=\"Unlock code\"><button class=\"ugo\" type=\"submit\">Unlock</button></form></div>\n")
    s = rep(s, "function renderStrokes() {", UNLOCK.lstrip('\n') + "function renderStrokes() {")

    # ---------------- memory: only two canvases keep their pictures; the background and a memory warning let go of more
    s = rep(s, "const surf = id => SURF[id] || (SURF[id] = SURF_PAINT[id]());",
               "const surf = id => { try { if (TH) (TH.sfUsed || (TH.sfUsed = new Set())).add(id); } catch (e) {} return SURF[id] || (SURF[id] = SURF_PAINT[id]()); }; // (v309: which canvas asked, so it can let go)")
    s = rep(s, "function applyThemeLook(T) {\n  TH = T; MUSIC_STYLE", MEM.lstrip('\n') + "function applyThemeLook(T) {\n  TH = T; themeSoon(); MUSIC_STYLE")
    s = rep(s, "window.addEventListener('nativememory', () => AU.trim());",
               "window.addEventListener('nativememory', () => memTrim()); document.addEventListener('visibilitychange', () => { if (document.hidden) memTrim(); }); /* (v309) */")

    # ---------------- memory: what leaves the stage is disposed
    s = rep(s, "  pots.forEach(p => { scene.remove(p.g); scene.remove(p.tele); }); rivals.forEach(p => scene.remove(p.g)); pots = []; rivals = [];",
               "  dropTree(pots.flatMap(p => [p.g, p.tele]).concat(rivals.map(p => p.g))); pots = []; rivals = []; // (v309: disposed, not just taken off)")
    s = rep(s, "\nlet pots = [], rivals = [];\nfunction placeObjects(level) {", "\n" + DROP.strip('\n') + "\nlet pots = [], rivals = [];\nfunction placeObjects(level) {")
    s = rep(s, "function placePower(pw, type, spot) { if (pw.g) scene.remove(pw.g);", "function placePower(pw, type, spot) { if (pw.g) dropTree([pw.g]);")
    s = rep(s, "powers.forEach(pw => pw.g && scene.remove(pw.g)); powers = [];", "dropTree(powers.map(pw => pw.g)); powers = [];")
    s = rep(s, "puHaloMat, 0.4); } scene.remove(pw.g); pw.g = null; }", "puHaloMat, 0.4); } dropTree([pw.g]); pw.g = null; }")
    s = rep(s, "puHaloMat, 0.6); }\n  scene.remove(pw.g); pw.g = null;", "puHaloMat, 0.6); }\n  dropTree([pw.g]); pw.g = null;")

    # ---------------- the performance readout: a line for what the GPU holds
    s = rep(s, "    + 'draws ' + Math.round(PH.calls / f) + '   triangles ' + Math.round(PH.tris / f / 1000) + 'k';",
               "    + 'draws ' + Math.round(PH.calls / f) + '   triangles ' + Math.round(PH.tris / f / 1000) + 'k\\n'\n"
               "    + 'held ' + renderer.info.memory.textures + ' pictures, ' + renderer.info.memory.geometries + ' meshes, ' + thLru.length + ' canvases'; // (v309)")

    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
