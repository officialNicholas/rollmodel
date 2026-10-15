"""v297: in the first match (the lesson) rivals can't squish or stomp you.

- A rival's ground pound landing on you, landing on you from a jump, ramming into you, rolling over you or a giant flattening you
  leaves you unhurt: you wobble and keep going (a moment of protection so it can't repeat on the next frame). No knock-out, no pancake.
- The lesson's dodge step still has the rival pound at you so you learn the swipe-up dodge. A miss now just counts as a miss
  ("Too late! Swipe up a beat sooner") and, as before, the step moves on after two tries or one good dodge.
- Only the lesson, and only you: everything else (missiles, falling off, the weather) works as before, and from the second match on
  rivals pound and stomp as usual."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HELPER = r"""// (v297) the lesson: a rival's pound, stomp, ram or roll leaves you unhurt (a wobble, a moment's cover; in the dodge step a miss counts)
function tutSpare(by, reason) {
  P.immuneT = Math.max(P.immuneT, 0.6); P.wob = 1; P.squash = Math.max(P.squash || 0, 0.35); buzz(10);
  if (tut && tut.driveMode === 'fight' && (reason === 'pound' || reason === 'coffin')) { tut.hits = (tut.hits || 0) + 1; popText('Too late! Swipe up a beat sooner'); }
}
"""

def apply(s):
    s = rep(s, "function flatten(B, A, how) {\n  if (B.charging) clearCharge(B);",
               HELPER + "function flatten(B, A, how) {\n  if (tut && B === P && A && A !== P) return tutSpare(A, how); // (v297: not in the lesson)\n  if (B.charging) clearCharge(B);")
    s = rep(s, "function knockOut(D, reason, by) {\n  if (D.st === 'ko' || state !== 'play') return;",
               "function knockOut(D, reason, by) {\n  if (D.st === 'ko' || state !== 'play') return;\n  if (tut && D === P && by && by !== P && (reason === 'pound' || reason === 'coffin' || reason === 'crush')) return tutSpare(by, reason); // (v297: not in the lesson)")
    return s
