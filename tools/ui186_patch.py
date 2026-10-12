#!/usr/bin/env python3
"""v246 (with the stages): the character never stands. It crawls, swims, or rolls up as a ball, everywhere: the win screen's jumps are
hops on all fours (the big one curls into the ball in the air and opens out to land), and it rides the rocket on all fours."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui185_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- one body: on all fours always (never the upright one, not for the win, not on the rocket)
rep("""  // which of its states fits what the blob is doing: on all fours nearly all the time (the menus, the locker, a match); up on its hind legs
  // only for its big moments (the victory, riding the rocket)
  function stateFor(I, o) {
    const D = o.D;
    if (D && vic && D.vicPose) return D.vicPose.stand === false ? 'crawl' : 'victory'; // (the win screen: up from all fours for its jumps, back down between them)
    if (D && D.rocket && D.st === 'play') return 'jetpack';
    return 'crawl';
  }""", """  // which of its states fits what the blob is doing: on all fours, always. It crawls, it swims, or it rolls up into a ball (the game swaps
  // in the ball); it never gets up on its hind legs, not for a win and not riding the rocket
  function stateFor(I, o) { return 'crawl'; }""")
# ---- the win screen: hops on all fours; the big happy jump curls into the ball at the top and opens out to land
rep("    if (vic.happy) { if (c < 1.08) { vicJump(c, 0.47, 0.26, 0.62, o, dir); o.side = dir; }", "    if (vic.happy) { if (c < 1.08) { vicJump(c, 0.47, 0.26, 0.62, o, dir); o.side = dir; o.ball = c > 0.36 && c < 0.74; }")
rep("""  // up on its hind legs for the jumps (rising a beat before them), down on all fours from the drop and between rounds
  { const T = vic.happy ? VIC_T : VIC_TS, c = tt - VIC_C0 < 0 ? tt - VIC_C0 : (tt - VIC_C0) % T; o.stand = tt > 0.6 && (c < 0 || c < (vic.happy ? 2.3 : 1.9) || c > T - 1.0); }""",
    """  o.stand = false; // (on all fours the whole time)""")
rep("const ballOn = I.kind === 'axo' && D.st === 'play' && (state === 'play' || state === 'dead') && (flK0 > (V.balled ? 0.12 : 0.3) || D.rollOutT > (V.balled ? 0.1 : 0.16) || D.rollT > (V.balled ? ROLL_T - ROLL_DASH : ROLL_T - ROLL_DASH + 0.06));",
    "const ballOn = I.kind === 'axo' && ((D.st === 'play' && (state === 'play' || state === 'dead') && (flK0 > (V.balled ? 0.12 : 0.3) || D.rollOutT > (V.balled ? 0.1 : 0.16) || D.rollT > (V.balled ? ROLL_T - ROLL_DASH : ROLL_T - ROLL_DASH + 0.06))) || !!(vic && D.vicPose && D.vicPose.ball));")
# ---- the rebuilt crawl body (head, throat and trunk one smooth form, a lizard's taper, a deeper trunk, the dorsal band up over the head):
# its pack, and the neck accessories' anchor moved back onto its throat
rep("const axoLoad = AXOC.load(window.AXO_PACK || 'axo-pack-241.txt')", "const axoLoad = AXOC.load(window.AXO_PACK || 'axo-pack-246.txt')")
rep("    H.neck.set(0, -0.84 * H.r, 0.57 * H.r).applyQuaternion(H.q).add(H.c); /* (the neck accessories' anchor, on the fuller throat) */", "    H.neck.set(0, -0.73 * H.r, 0.49 * H.r).applyQuaternion(H.q).add(H.c); /* (the neck accessories' anchor, on the throat) */")
open(DST, 'w').write(s); print('ui186 ok', n0, '->', len(s))
