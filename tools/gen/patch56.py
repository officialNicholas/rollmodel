import sys
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:150])); sys.exit(1)
    s = s.replace(a, b)

# ---------- the CPU winds up before it rolls at you (a beat to react), and the warning shows during it ----------
rep("rollSafe(D) && Math.random() < dt * (big ? 2.5 : 1.2) * AI.ram) { if (D.charging) cancelCharge(D); if (dodgeRoll(D)) return true; }",
    "rollSafe(D) && Math.random() < dt * (big ? 2.5 : 1.2) * AI.ram) { if (D.charging) cancelCharge(D); ai.rollWind = ROLL_WIND; ai.rollAt = O; D.squash = Math.max(D.squash, 0.4); return true; }")
rep("function aiEvade(D, dt) {\n", """const ROLL_WIND = 0.28;
function aiEvade(D, dt) {
  if (D.ai.rollWind > 0) { const ai = D.ai, O = ai.rollAt || other(D); ai.rollWind -= dt; D.steer = -clamp(wrapA(Math.atan2(O.x - D.x, O.z - D.z) - D.yaw) * 3, -1, 1); D.squash = Math.max(D.squash, 0.35); D.wob = Math.max(D.wob, 0.3); if (ai.rollWind <= 0) { ai.rollWind = 0; dodgeRoll(D); } return true; }
""")
rep("  if (D.flatT > 0) { D.steer = 0; ai.plan = null; return; }", "  if (D.flatT > 0 || D.stunT > 0) { D.steer = 0; ai.plan = null; ai.rollWind = 0; return; }")

# ---------- what's coming at you ----------
rep("// ---------- visuals each frame ----------", """// incoming: a missile whose blast would catch you, or a roll lined up on you (including the CPU's wind-up before it)
let threat = null, threatShown = '', threatOn = false;
function detectThreat(playing) {
  threat = null; if (!playing || P.st !== 'play') return;
  for (const F of foes(P)) {
    if (F.st !== 'play') continue;
    if (F.missile && F.slam) { const c = missileHit(F); if (c && Math.hypot(c.x - P.x, c.z - P.z) < MISSILE_R + PR + 1.2) { threat = { F, k: 'missile' }; return; } }
    const dx = P.x - F.x, dz = P.z - F.z, d = Math.hypot(dx, dz), aimed = Math.abs(wrapA(Math.atan2(dx, dz) - F.yaw)) < 0.6 && Math.abs(P.y - F.y) < 1;
    if (!threat && ((F.rollT > ROLL_T - ROLL_DASH && d < 5 && aimed) || (F.ai && F.ai.rollWind > 0 && F.ai.rollAt === P && d < 5))) threat = { F, k: 'roll' };
  }
}
function threatUI() {
  const el = $('threat'), ar = $('threatArrow'), on = !!threat;
  if (on && !threatOn) { AU.alert(); buzz([15, 40, 15]); }
  threatOn = on;
  const tx = on ? (threat.k === 'missile' ? 'Missile!' : 'Rolling at you!') : '';
  if (tx !== threatShown) { threatShown = tx; if (tx) $('threatText').textContent = tx; el.classList.toggle('on', on); ar.classList.toggle('on', on); }
  if (!on || !drop.visible) return;
  // a marker beside your blob, on the side it's coming from
  const F = threat.F, r = stage.getBoundingClientRect(), dx = F.x - P.x, dz = F.z - P.z, dl = Math.hypot(dx, dz) || 1;
  tv1.copy(drop.position).project(camera); tv2.set(P.x + dx / dl * 1.5, drop.position.y, P.z + dz / dl * 1.5).project(camera);
  let sx = tv2.x - tv1.x, sy = -(tv2.y - tv1.y); const sl = Math.hypot(sx, sy) || 1; sx /= sl; sy /= sl;
  const px = (tv1.x * 0.5 + 0.5) * r.width + sx * 70, py = (-tv1.y * 0.5 + 0.5) * r.height + sy * 70;
  ar.style.transform = 'translate(' + px.toFixed(1) + 'px,' + py.toFixed(1) + 'px)'; ar.children[1].style.transform = 'rotate(' + (Math.atan2(sx, -sy) * 180 / Math.PI).toFixed(0) + 'deg)';
}
// ---------- visuals each frame ----------""")
rep("  const ke = 1 - Math.exp(-dt * 10), kf = 1 - Math.exp(-dt * 16), playing = state === 'play', pIn = playing && (P.st === 'play' || P.st === 'hide');",
    "  const ke = 1 - Math.exp(-dt * 10), kf = 1 - Math.exp(-dt * 16), playing = state === 'play', pIn = playing && (P.st === 'play' || P.st === 'hide');\n  detectThreat(playing);")
rep("  updateSpeedLines(dt, spK); updateSlamBtn();", "  updateSpeedLines(dt, spK); updateSlamBtn(); threatUI();")
# the edge marker turns red for these too, and the missile's landing ring goes red when it's going to get you
rep("      const warn = (H.slam && dHP < slamRadius(H) + PR + 3) ||", "      const warn = (threat && threat.F === H) || (H.slam && dHP < slamRadius(H) + PR + 3) ||")
rep("    if (D.slam) { L.warn.visible = true;", "    if (!L.warnBase) L.warnBase = L.warn.material.color.clone();\n    L.warn.material.color.copy(threat && threat.F === D && threat.k === 'missile' ? (Math.sin(clock * 30) > 0 ? COL_DANGER : COL_WHITE) : L.warnBase);\n    if (D.slam) { L.warn.visible = true;")
rep("const COL_DULL = new THREE.Color(0x6A6370),", "const COL_DANGER = new THREE.Color(0xFF3B5C), COL_DULL = new THREE.Color(0x6A6370),")
rep("flip: 2, flipBack: 2, dash: 2.4, rocket: 2.6 };", "flip: 2, flipBack: 2, dash: 2.4, rocket: 2.6, alert: 2.2 };")
rep("    dash() {", "    alert() { for (const d of [0, 0.11]) tone({ d, type: 'triangle', f: 1180, f1: 1420, glide: 0.05, dur: 0.075, v: 0.12, a: 0.002 }); },\n    dash() {")

# markup and look
rep('  <div class="hint" id="hint" aria-live="polite"><span id="hintText"></span></div>',
    '  <div class="hint" id="hint" aria-live="polite"><span id="hintText"></span></div>\n  <div class="threat" id="threat" aria-live="assertive"><b>!</b><span id="threatText">Missile!</span></div>\n  <div class="threatArrow" id="threatArrow" aria-hidden="true"><i>!</i><u><b></b></u></div>')
rep(".banner{position:absolute;", """.threat{position:absolute;left:50%;bottom:calc(160px + env(safe-area-inset-bottom));display:flex;align-items:center;gap:8px;padding:7px 15px 7px 8px;border-radius:99px;background:#FF3B5C;border:3px solid var(--line);box-shadow:0 4px 0 var(--line);color:var(--white);font:800 16px/1 var(--font-ui);pointer-events:none;opacity:0;transform:translate(-50%,10px) scale(.8);transition:opacity .12s,transform .16s cubic-bezier(.3,1.6,.5,1);z-index:6}
.threat b{display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:var(--white);color:#FF3B5C;font:400 15px/1 var(--font-display)}
.threat.on{opacity:1;transform:translate(-50%,0);animation:threatPulse .4s ease-in-out infinite alternate}
@keyframes threatPulse{to{background:#FF6B84}}
.threatArrow{position:absolute;left:0;top:0;width:34px;height:34px;margin:-17px 0 0 -17px;pointer-events:none;z-index:6;display:none;will-change:transform}
.threatArrow.on{display:block}
.threatArrow i{position:absolute;inset:4px;display:grid;place-items:center;border-radius:50%;background:#FF3B5C;border:3px solid var(--white);box-shadow:0 0 0 2px var(--line),0 0 14px 4px rgba(255,59,92,.7);color:var(--white);font:400 14px/1 var(--font-display);font-style:normal;animation:foewarn .3s ease-in-out infinite alternate}
.threatArrow u{position:absolute;inset:0}
.threatArrow b{position:absolute;left:50%;top:-9px;margin-left:-8px;width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;border-bottom:12px solid #FF3B5C;filter:drop-shadow(0 0 1.5px #fff) drop-shadow(0 0 2px rgba(20,10,40,.9))}
.banner{position:absolute;""")
rep("  .logo,.dock,.card,.modal,", "  .threat.on,.threatArrow i{animation:none}\n  .logo,.dock,.card,.modal,")
open(F, 'w').write(s)
print('ok')
