"""v303: fixes from playing the first lesson through with real touches.

- A drag that starts slowly now steers. A finger that rested a moment before dragging (longer than the 150 ms that means "hold to
  stop") used to leave you braked, turning on the spot, until you lifted it. Now a clear sideways drag out of a hold you haven't
  pulled lets go of the brake and steers. Once you pull down for a fling, a sideways drag still aims it as before.
- Knocked out mid-lesson, you came back in a paint tub and nothing said how to get out. The step's own tip stayed up (the item
  step's "TAP it!" pointed at a button that is hidden while you're in a tub), and the step timed out while you sat there. Now the
  step waits: its clock stops, a "Swipe up to roll out of the tub!" callout shows with the swipe finger, and once you're out the
  step's tip comes back. The pound step already handles the tub itself; in the free play at the end the callout shows whenever
  nothing else is being said.
- The paint-tub step counts only a tub you roll into after running dry. Coming back from a fall straight into a tub used to tick the
  step off before its tip was ever shown.
- In the lesson's taught steps the canvas edge is a soft rail: crawling or rolling up to the drop stops you at the brink and turns
  you gently back toward the middle (as the knock-out camera already does with drops you can't see). Playing it through, most
  knock-outs were falls off the edge in the second after a slow-motion tip popped up, while the tip was being read. The free match at
  the end of the lesson, and every match after it, keep the edge as it is."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

STEER = r"""  // (v303) a clear sideways drag out of a hold that hasn't been pulled is a steer: let go of the brake and go (a finger that rested a
  // moment before dragging used to leave you braked, turning on the spot). Once the band is pulled down, sideways aims the fling.
  if (P.charging && holdCharge && !t.pulled && Math.abs(sx) > 28 && Math.abs(sx) > Math.abs(dy) * 1.6 && state === 'play') { cancelCharge(P); holdCharge = false; slingOff(); t.moved = true; t.steered = true; }
  if (P.charging && holdCharge && dy > PULL_DEAD) t.pulled = true;
"""

TUB = r"""  // (v303) back in a tub mid-lesson (knocked out, respawned): the step waits, its clock stopped, while a callout and the swipe finger
  // show the way out; out again, its own tip comes back. (The tub and pound steps deal with the tub themselves; in the free play at the
  // end, finale included, the callout shows only when nothing else is being said, and the match goes on.)
  const inTub = P.st === 'hide' && !(s.id === 'basin' && tut.basinTip) && s.id !== 'pound' && !(tut.gap > 0) && !tut.card;
  tut.tubHold = inTub && s.id !== 'rest';
  if (inTub) {
    if (s.id === 'rest' ? !tutTip : (!tutTip || tutTip.key !== 'tubout')) { if (tutTip && tutTip.key !== 'tubout') tut.tubTip = tutTip; tutShow(say('*SWIPE UP* to roll out of the tub!', 'Press *SHIFT* to roll out of the tub!'), null, 'tubout', true, true); }
    if (s.id !== 'rest') { tut.slowK = 1; return; } }
  else if (tutTip && tutTip.key === 'tubout') { const t0 = tut.tubTip; tut.tubTip = null; tutHide(); if (t0) tutShow(t0.text, t0.at, t0.key, t0.call, t0.nodim, t0.side, t0.loose, t0.low); }
"""

RAIL = "  if (D === P && !D.air && D.st === 'play' && tut && tut.step >= 0 && tut.step < TUT_REST && !kcam && surfaceUnder(D.x + fx * (0.45 + d), D.z + fz * (0.45 + d), D.y + STEP, true) === -Infinity) { D.spd = Math.min(D.spd, 1.2); D.yaw += wrapA(Math.atan2(-D.x, -D.z) - D.yaw) * Math.min(1, dt * 4); D.wob = Math.max(D.wob || 0, 0.25); return; } // (v303: the lesson's taught steps: the edge is a soft rail)\n"

def apply(s):
    a = "  if (Math.abs(sx) > 16 && !P.charging) t.steered = true;\n"
    s = rep(s, a, STEER + a)
    a = "  const s = TUT_STEPS[tut.step]; if (tut.step < TUT_REST && matchLeft < 20) matchLeft = 20; // (the lesson does not run out the clock)\n"
    s = rep(s, a, a + TUB)
    s = rep(s, "if (state === 'play' && tut.step >= 0) { tut.st += rdt; if (tut.st > TUT_STEPS[tut.step].max && !(tut.gap > 0)) tutNext(); }",
               "if (state === 'play' && tut.step >= 0 && !tut.tubHold) { tut.st += rdt; if (tut.st > TUT_STEPS[tut.step].max && !(tut.gap > 0)) tutNext(); }")
    a = "  if (D === P && kcam && !D.air && D.st === 'play' && surfaceUnder(D.x + fx * (0.3 + d), D.z + fz * (0.3 + d), D.y + STEP, true) === -Infinity) return; // (the kill cam: never rolled off a drop you can't see)\n"
    s = rep(s, a, a + RAIL)
    s = rep(s, "      return P.st === 'hide'; } },\n  { id: 'pound',", "      return P.st === 'hide' && tut.basinTip; } }, // (v303: a tub you rolled into, out of paint)\n  { id: 'pound',")
    # the swipe finger with the tub callout
    s = rep(s, "const TUT_GEST = { msling: 'pull', msling2: 'pull', move: 'steertap', sling: 'pull', dodgenow: 'swipe', rdodgenow: 'swipe', rroll: 'swipe',",
               "const TUT_GEST = { tubout: 'swipe', msling: 'pull', msling2: 'pull', move: 'steertap', sling: 'pull', dodgenow: 'swipe', rdodgenow: 'swipe', rroll: 'swipe',")
    return s
