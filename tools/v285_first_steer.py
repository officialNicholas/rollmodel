"""v285: the lesson's first callout, "DRAG to steer, TAP to jump!", at full speed: the game no longer slows down under it (no slow
motion, no slowed music, no gold frame). It goes the moment you start steering, faded out rather than cut. The step still ends as
before (a steer and a jump, or a little way crawled)."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

FADE = """// (v285) the same, faded out rather than cut (the first callout goes as you start steering)
let tutFadeN = 0;
function tutFade() { if (!tutTip) return; tutHandAt(null); tutGest(null); if ($('tutGo').hidden) coachCorner(null); tutTip = null; tutEl.classList.add('fade'); tutEl.classList.remove('on'); tutDim.classList.remove('on');
  const n = ++tutFadeN; setTimeout(() => { if (n !== tutFadeN) return; tutEl.classList.remove('fade'); if (!tutTip) tutEl.hidden = true; }, 420); }
function tutHide() {"""

def apply(s):
    s = rep(s, "tut.slowK = TUT_SLOW; tutShow(say('*DRAG* to steer, *TAP* to jump!'", "tut.slowK = 1; tutShow(say('*DRAG* to steer, *TAP* to jump!'")
    s = rep(s, "      if (Math.abs(steerIn) > 0.3 || keyL || keyR) tut.steered = true;",
               "      if (Math.abs(steerIn) > 0.3 || keyL || keyR) tut.steered = true; if ((Math.abs(steerIn) > 0.12 || keyL || keyR) && tutTip && tutTip.key === 'move') tutFade(); // (v285: the callout goes as you start steering)")
    s = rep(s, "function tutHide() {", FADE)
    s = rep(s, ".tut.on{opacity:1}", ".tut.on{opacity:1}.tut.fade{transition:opacity .38s ease-out}")
    return s
