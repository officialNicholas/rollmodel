#!/usr/bin/env python3
"""Four things in play. Turning is tighter, and when you are plainly steering into a basin, a pick-up, the orb or a ramp the game leans the turn the rest of the way. The sun no longer kills: out in the open it drains your paint fast and leaves you dried up. The pound's timer sits on the corner of the pound button, not by your character (the floating dial keeps the power-ups only). And the missile's homing only takes hold on a rival who is close and roughly ahead of you. On top of ui87_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui87_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- turning: tighter, with a lean toward what you are plainly turning into ----
rep("const TURN = 3.4;", "const TURN = 3.9;")
rep("function coffinTarget(D, cone) {", r'''// what you look to be turning into: a free basin, a pick-up, the orb or a ramp, near and off to the side you are steering toward
function steerTarget(D, input) {
  let best = null; const want = -Math.sign(input); // (a positive steer turns the heading negative)
  const take = (x, z, maxD, w) => { const dx = x - D.x, dz = z - D.z, d = Math.hypot(dx, dz); if (d < 0.7 || d > maxD) return; const err = wrapA(Math.atan2(dx, dz) - D.yaw); if (Math.sign(err) !== want || Math.abs(err) < 0.12 || Math.abs(err) > 1.25) return; const sc = Math.abs(err) * 0.6 + d / maxD * w; if (!best || sc < best.sc) best = { err, d, sc }; };
  for (const p of pots) if (potUp(p) && !p.occ && p.cool <= 0 && p.ink > 0.05) take(p.x, p.z, 7, 1);
  for (const pw of powers) if (pw.g && pw.pop >= 0.5) take(pw.x, pw.z, 7, 1);
  if (orb.on && orb.k > 0.5 && D.giantT <= 0) take(orb.x, orb.z, 7, 1);
  for (const r of RAMPS) take((r[0] + r[1]) / 2, (r[2] + r[3]) / 2, 8, 1.4);
  return best;
}
function coffinTarget(D, cone) {''')
rep("  D.turn += (want - D.turn) * Math.min(1, dt * (D === P && !P.ai ? (want * D.turn < 0 ? 50 : 36) : 20));",
    "  if (D === P && !P.ai && !D.air && !D.charging && Math.abs(input) > 0.4 && D.spd > 0.8) { const st = steerTarget(D, input); if (st) want += -clamp(st.err, -1, 1) * TURN * 0.6 * Math.min(1, Math.abs(input) * 1.4); } // (the lean the rest of the way)\n  D.turn += (want - D.turn) * Math.min(1, dt * (D === P && !P.ai ? (want * D.turn < 0 ? 50 : 36) : 20));")
# ---- the sun drains you dry; it no longer knocks you out ----
rep("if (D.exposed) { D.paint -= BURN_RATE * dt; burnFx(D, dt); if (D.paint <= 0) { D.paint = 0; return knockOut(D, 'sun'); } }",
    "if (D.exposed) { D.paint -= BURN_RATE * 2.4 * dt; burnFx(D, dt); if (D.paint <= 0) { D.paint = 0; if (!D.dry && D.st === 'play') goDry(D); } } // (the sun dries you out; it no longer knocks you out)")
rep("' or your color in ' + DRY_KO + ' seconds', 3.4); }", "' or your color to refill', 3.4); }")
# ---- the pound's timer on the corner of its button ----
rep('<button class="slamBtn" id="slamBtn" type="button" aria-label="Ground pound" hidden><i class="sdisc" aria-hidden="true"></i>',
    '<button class="slamBtn" id="slamBtn" type="button" aria-label="Ground pound" hidden><i class="sdisc" aria-hidden="true"></i><i class="sbdial" id="sbDial" aria-hidden="true" hidden><i id="sbRing"></i><b id="sbN"></b></i>')
rep("  if (b._cd !== cd) { b._cd = cd; b.style.setProperty('--cd', cd); }",
    r'''  if (b._cd !== cd) { b._cd = cd; b.style.setProperty('--cd', cd); }
  { const dl = $('sbDial'); let frac = -1, n = '', kind = ''; // the dial on the button's corner: short of paint it shows a drop and your paint, else the cooldown's count
    if (!rk && P.st === 'play' && !P.slam) { if (P.paint < POUND_MIN) { frac = Math.min(1, P.paint / POUND_MIN); kind = 'paint'; } else if (P.slamCD > 0 && P.slamMax > 0) { frac = 1 - P.slamCD / P.slamMax; n = String(Math.ceil(P.slamCD)); kind = 'cd'; } }
    if (frac < 0) { if (!dl.hidden) dl.hidden = true; } else { if (dl.hidden) dl.hidden = false; if (dl.dataset.k !== kind) dl.dataset.k = kind; const deg = (clamp(frac, 0, 1) * 360).toFixed(0); if (dl.dataset.d !== deg) { dl.dataset.d = deg; $('sbRing').style.background = 'conic-gradient(var(--pc) ' + deg + 'deg, rgba(23,19,32,.35) 0)'; }
      const v = kind === 'paint' ? '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5C9.2 7.2 6.4 10.6 6.4 14.1a5.6 5.6 0 0 0 11.2 0c0-3.5-2.8-6.9-5.6-11.6z"/></svg>' : n; if ($('sbN').dataset.v !== v) { $('sbN').dataset.v = v; $('sbN').innerHTML = v; } } }''')
rep("      else if (P.paint < POUND_MIN && !P.slam) { frac = Math.min(1, P.paint / POUND_MIN); n = ''; kind = 'paint'; } // (short of paint: the dial fills with your paint, a drop in it, no count)\n      else if (P.slamCD > 0 && P.slamMax > 0) { frac = 1 - P.slamCD / P.slamMax; n = Math.ceil(P.slamCD); kind = 'cd'; }",
    "      // (the pound's own timer lives on the pound button)")
# ---- the missile's homing: close and roughly ahead, or not at all ----
rep("const t = assistTarget(D, 0.6, 16); if (!t) return;", "const t = assistTarget(D, 0.42, 9); if (!t) return;")
rep("const t = coneFoe(D, 1.15, 16); if (!t || safe(t.O)) return; const err = t.err;", "const t = coneFoe(D, 0.6, 9); if (!t || safe(t.O)) return; const err = t.err;")
css = '''
/* the pound's timer on the corner of its button */
.sbdial{position:absolute;left:-8px;top:-8px;width:38px;height:38px;pointer-events:none;--pc:var(--gold);z-index:2}
.sbdial[hidden]{display:none}
.sbdial i{position:absolute;inset:0;border-radius:50%;background:conic-gradient(var(--pc) 360deg,rgba(23,19,32,.35) 0);border:2.5px solid var(--black);box-shadow:0 2px 0 var(--black),0 0 0 2px rgba(255,255,255,.35)}
.sbdial i::after{content:"";position:absolute;inset:5px;border-radius:50%;background:rgba(23,19,32,.82)}
.sbdial b{position:absolute;inset:0;display:grid;place-items:center;font:400 15px/1 var(--font-display);color:var(--gold);text-shadow:0 1.5px 0 var(--black)}
.sbdial[data-k="paint"]{--pc:#CFC6E0}
.sbdial[data-k="paint"] b svg{width:14px;height:14px;fill:#fff;filter:drop-shadow(0 1.5px 0 var(--black))}
.slamBtn.off .sbdial{opacity:1}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
