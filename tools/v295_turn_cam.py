"""v295: gentler turning and a calmer camera (a player said the view made them dizzy).

- Turning is about 10% slower by default: the turn rate at any swipe is 0.89 of what it was, and the steering helpers that lean you
  the rest of the way scale with it. The kill cam's own steering and the CPUs are unchanged.
- A Turning slider in Settings, 50% to 150% in steps of 5 (100% is the new default), from Gentle to Quick. It's saved with the game
  and takes effect at once.
- The camera eases after you instead of snapping round with you. Its swing behind you starts and stops more gently (it settles in
  0.3 s, was 0.21 s), with a little more lead into the turn so it only trails a few degrees further than before. A spin on the spot
  can't whip the view round faster than 250 degrees a second. Its position and aim trail a touch more softly. It no longer tilts the
  horizon as you lean into a turn, since rolling the view is one of the surest ways to make someone queasy."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

SLIDER = ('<div class="sopt wide"><p class="slab">Turning <b class="trnv" id="turnVal">100%</b></p>'
          '<div class="trn"><span class="trnl" aria-hidden="true">Gentle</span><input type="range" id="turnPick" min="50" max="150" step="5" value="100" aria-label="Turning speed" aria-describedby="turnNote"><span class="trnl" aria-hidden="true">Quick</span></div>'
          '<p class="gnote" id="turnNote">How fast you turn when you swipe.</p></div>\n        ')

CSS = r"""
/* (v295) the Turning slider: a dark slot like the toggles, filled gold up to a chunky gold knob */
.trn{display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:10px;height:46px}
.trnl{font:400 11px/1 var(--font-display);letter-spacing:.04em;text-transform:uppercase;color:rgba(255,255,255,.55)}
.trnv{margin-left:auto;padding:4px 8px 3px;border-radius:6px;background:linear-gradient(180deg,#FFE08A 0%,#F2C14E 100%);color:#171320;font:400 12px/1 var(--font-display);text-shadow:none;box-shadow:0 0 0 2px #171320;transform:skewX(-6deg)}
#turnPick{--v:50%;-webkit-appearance:none;appearance:none;width:100%;height:30px;margin:0;padding:0;background:none;cursor:pointer;touch-action:pan-y}
#turnPick:focus{outline:none}
#turnPick::-webkit-slider-runnable-track{height:16px;border-radius:9px;background:linear-gradient(90deg,#F2C14E 0,#FFE08A var(--v),#28243A var(--v));box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(0,0,0,.3)}
#turnPick::-moz-range-track{height:16px;border-radius:9px;background:linear-gradient(90deg,#F2C14E 0,#FFE08A var(--v),#28243A var(--v));box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(0,0,0,.3)}
#turnPick::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:30px;height:30px;margin-top:-7px;border:0;border-radius:9px;background:linear-gradient(180deg,#FFE08A 0%,#F2C14E 100%);box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(255,255,255,.5),inset 0 -4px 0 rgba(0,0,0,.18),0 4px 0 #171320;transform:skewX(-6deg)}
#turnPick::-moz-range-thumb{width:30px;height:30px;border:0;border-radius:9px;background:linear-gradient(180deg,#FFE08A 0%,#F2C14E 100%);box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(255,255,255,.5),inset 0 -4px 0 rgba(0,0,0,.18),0 4px 0 #171320}
#turnPick:focus-visible::-webkit-slider-thumb{outline:3px solid var(--gold);outline-offset:3px}
@media (max-height:520px) and (min-aspect-ratio:1/1){.trn{height:40px}}
"""

JS = r"""
// (v295) the Turning slider in Settings
{ const el = $('turnPick'), show = () => { const v = turnPct(); el.value = String(v); el.style.setProperty('--v', ((v - 50) / 100 * 100).toFixed(1) + '%'); $('turnVal').textContent = v + '%'; el.setAttribute('aria-valuetext', v + '%'); };
  let last = turnPct();
  el.addEventListener('input', () => { const v = Math.round(+el.value / 5) * 5; store.turn = clamp(v, 50, 150); show(); if (v !== last) { last = v; try { AU.tick && AU.tick(0); } catch (e) {} } });
  el.addEventListener('change', () => { save(); });
  window.__turnShow = show; show(); }
"""

def apply(s):
    # the player's turn rate, 10% gentler by default and set from Settings
    s = rep(s, "const TURN = 3.9;", "const turnPct = () => { const v = +store.turn; return v >= 50 && v <= 150 ? Math.round(v / 5) * 5 : 100; }, turnK = () => 0.89 * turnPct() / 100; // (v295: 100% turns about 10% slower than before; the steering helpers make up a little of it)\nconst TURN = 3.9;")
    s = rep(s, "want = input * TURN * scaleBy * agile;", "want = input * TURN * scaleBy * agile * (D === P && !P.ai && !kcam ? turnK() : 1);")
    s = rep(s, "lean = -clamp(st.err, -1, 1) * TURN * 0.6 * Math.min(1, Math.abs(input) * 1.4);", "lean = -clamp(st.err, -1, 1) * TURN * turnK() * 0.6 * Math.min(1, Math.abs(input) * 1.4);")
    # the camera eases after you, with a cap on how fast it swings, and never rolls the horizon
    s = rep(s, "let dy = P.yaw - camTurnS * 0.085 - camYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); [camYaw, camYawV] = sdamp(camYaw, camYaw + dy, camYawV, 0.21, Math.min(rdt, 0.05));",
               "let dy = P.yaw - camTurnS * 0.14 - camYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); { const y0 = camYaw, dtc = Math.min(rdt, 0.05); [camYaw, camYawV] = sdamp(camYaw, camYaw + dy, camYawV, 0.3, dtc); const lim = CAM_SWING * dtc; if (camYaw - y0 > lim) camYaw = y0 + lim; else if (y0 - camYaw > lim) camYaw = y0 - lim; camYawV = clamp(camYawV, -CAM_SWING, CAM_SWING); } // (v295: eased in and out of turns, with a little more lead so it keeps up as before; quick spins capped at 250 degrees a second)")
    s = rep(s, "const sdamp = (cur, tgt, vel, st, dt) =>", "const CAM_SWING = 4.4; // (v295) the fastest the play camera swings round after you, radians a second (250 degrees: above an ordinary turn, below a spin on the spot)\nconst sdamp = (cur, tgt, vel, st, dt) =>")
    s = rep(s, "if (playing) camera.rotateZ(-look.lean * 0.03);", "/* (v295: the view no longer rolls as you lean into a turn) */")
    s = rep(s, "smoothDamp(camPos, camVel, dPos, 0.09, rdt); smoothDamp(camLook, lookVel, dLook, 0.07, rdt);", "smoothDamp(camPos, camVel, dPos, 0.12, rdt); smoothDamp(camLook, lookVel, dLook, 0.1, rdt);")
    # the slider, between Visuals and Help
    s = rep(s, '<div class="sopt wide"><p class="slab">Help</p>', SLIDER + '<div class="sopt wide"><p class="slab">Help</p>')
    s = rep(s, "function openSettings() { if (state !== 'menu' || lookOpen || shopOpen) return; gfxPick = GFX; paintSettings();",
               "function openSettings() { if (state !== 'menu' || lookOpen || shopOpen) return; gfxPick = GFX; paintSettings(); if (window.__turnShow) window.__turnShow();")
    a = "$('gfxPick').addEventListener('click', e => {"
    s = rep(s, a, JS.lstrip('\n') + a)
    b = "@media (prefers-reduced-motion:reduce){#mStrokes .stslot,#mStrokes .stopt{transition:none}}"
    s = rep(s, b, b + CSS.rstrip('\n'))
    return s
