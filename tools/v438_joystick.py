"""v438: a steering stick in landscape. Steering was already a floating stick (press anywhere, drag sideways; the centre follows a
finger that drags past the edge), but nothing on screen showed it. Held sideways, a small stick now appears under the steering thumb
once it moves: a see-through dark disc with a thin white rim where you pressed, and a knob in your paint colour that follows the thumb
(sideways as far as steering goes, a little up and down for the feel; fully up and down while aiming a turret). The disc slides along
when the thumb runs past its edge, as the steering centre does. It fades out on letting go, while the slingshot's band is out (that has
its own ring), and between matches. A quick tap (a jump) never shows it. Upright play is unchanged."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v438) the steering stick in landscape: a small see-through disc under the thumb and a knob in the paint colour */
.joy{--joy:84px;position:absolute;left:0;top:0;width:var(--joy);height:var(--joy);margin:calc(var(--joy) / -2) 0 0 calc(var(--joy) / -2);border-radius:50%;pointer-events:none;opacity:0;transition:opacity .14s ease-out;
  background:radial-gradient(circle,rgba(23,19,32,.10) 0 55%,rgba(23,19,32,.24) 100%);box-shadow:inset 0 0 0 2px rgba(255,255,255,.55),0 0 0 1.5px rgba(23,19,32,.3);will-change:transform}
.joy.on{opacity:.92}
.joy i{position:absolute;left:50%;top:50%;width:40%;height:40%;margin:-20% 0 0 -20%;border-radius:50%;background:var(--jk,#fff);box-shadow:0 0 0 2.5px #fff,0 0 0 4.5px rgba(23,19,32,.5),0 3px 6px rgba(0,0,0,.22);will-change:transform}
@media (min-aspect-ratio:1/1) and (min-height:561px){.joy{--joy:96px}}
@media (orientation:portrait){.joy{display:none}}
"""

JS = r"""
// (v438) the steering stick, drawn in landscape: where the steering thumb pressed (the steering centre, which slides along when the
// thumb runs past the edge), its knob following the thumb. Shown once the thumb moves (never for a tap), hidden while the slingshot's
// band is out, on letting go, and out of play.
const joyEl = $('joy'), joyK = $('joyK'); let joyOn = false, joyRaf = 0;
function joyHide() { if (joyOn) { joyOn = false; joyEl.classList.remove('on'); } }
function joyTick() { joyRaf = 0; if (!joyOn) return; if (steerId === null || state !== 'play' || P.charging || innerWidth <= innerHeight) { joyHide(); return; } joyRaf = requestAnimationFrame(joyTick); }
canvas.addEventListener('pointermove', e => {
  if (e.pointerId !== steerId) return; const t = touches.get(e.pointerId); if (!t) return;
  if (innerWidth <= innerHeight || state !== 'play' || P.charging || !t.moved || P.st === 'out') { joyHide(); return; }
  const r = slingRect(), tr = joyEl.offsetWidth * 0.3;
  const kx = clamp((e.clientX - anchorX) / MAX_DRAG, -1, 1) * tr, ky = clamp((e.clientY - anchorY) / MAX_DRAG, -1, 1) * tr * (P.turret ? 1 : 0.45);
  joyEl.style.transform = 'translate(' + (anchorX - r.left).toFixed(1) + 'px,' + (anchorY - r.top).toFixed(1) + 'px)';
  joyK.style.transform = 'translate(' + kx.toFixed(1) + 'px,' + ky.toFixed(1) + 'px)';
  if (!joyOn) { joyOn = true; joyEl.style.setProperty('--jk', TEAMS[P.team].css); joyEl.classList.add('on'); if (!joyRaf) joyRaf = requestAnimationFrame(joyTick); }
});
"""

def apply(s):
    s = rep(s, '<circle id="slA" r="15"/><circle id="slB" r="11"/></svg>',
            '<circle id="slA" r="15"/><circle id="slB" r="11"/></svg>   <div class="joy" id="joy" aria-hidden="true"><i id="joyK"></i></div>')
    a = "canvas.addEventListener('contextmenu', e => e.preventDefault());"
    s = rep(s, a, a + JS)
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    return s
