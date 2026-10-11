#!/usr/bin/env python3
"""v226: hard paint lasts 2 seconds less (the dusk between the heat and the rain: 7 s to 5 s). And a pound assist: roll into a rival and
stun them with your pound ready, and the roll carries you up off them into a quick little hop, the pound button lit and pulsing; press it
and you come straight down on them, leave it and you just land. Never forced, never in the way."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui156_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- hard paint: 2 seconds shorter
rep("const SUN_WARN = 4, SUN_TIME = 7, SUN_CHANCE = 0.45, DUSK_TIME = 7,", "const SUN_WARN = 4, SUN_TIME = 7, SUN_CHANCE = 0.45, DUSK_TIME = 5,")

# ---- the pound assist
# (queued at the stun, so it starts as the hit stop lets go: the bump, then up)
rep("  if (hearable(A) || hearable(B)) { AU.bonk(1); AU.pop(); } if (B === P) { AU.vox('oof'); hitEdge(A); } hitStop(0.07, A, B);",
    "  if (hearable(A) || hearable(B)) { AU.bonk(1); AU.pop(); } if (B === P) { AU.vox('oof'); hitEdge(A); } hitStop(0.07, A, B);\n"
    "  if (A === P && !A.ai) { A.assistQ = 0.02; A.assistB = B; }")
rep("  if (D.passT > 0) D.passT -= dt;",
    "  if (D.passT > 0) D.passT -= dt;\n"
    "  if (D.assistQ > 0) { D.assistQ -= dt; if (D.assistQ <= 0) { D.assistQ = 0; poundAssist(D); } }\n"
    "  if (D.assistT > 0) { D.assistT -= dt; if (!D.air || D.slam || D.st !== 'play') D.assistT = 0; }")
rep("// rolled into: seeing stars for 2 seconds, can't move or act (a pound will finish you), then a moment where it can't happen again",
    """// the pound assist: you rolled into a rival and stunned it, your pound ready: the roll carries you up off it into a quick little hop (most of
// the roll's speed goes into the lift, so you stay over them, landing just past), the pound button pulsing. Press it and you come straight down on them;
// don't, and you just land. (Not in the lesson's dodge steps, where the pound is locked, nor before the lesson has given you the pound.)
const ASSIST_VY = 6.2, ASSIST_SPD = 2.6;
function poundAssist(D) {
  const B = D.assistB; D.assistB = null;
  if (state !== 'play' || D.st !== 'play' || D.air || D.slam || D.rocket || D.turret || D.giantT > 0 || D.charging || !slamReady(D) || (tut && (tut.noPound || tut.hidePound)) || !B || !(B.stunT > 0.8)) return;
  D.rollT = 0; D.air = true; D.vy = ASSIST_VY; D.spd = Math.min(D.spd, ASSIST_SPD); D.turn = 0; D.buf = 0; D.stroke++; D.squash = Math.max(D.squash, 0.45); D.assistT = 1.2;
  fxLaunch(D, 0.6); if (hearable(D)) AU.jump(); if (D === P) buzz(10);
}
// rolled into: seeing stars for 2 seconds, can't move or act (a pound will finish you), then a moment where it can't happen again""")
# the button: pulsing with a ring while the hop lasts
rep("  const up = P.st === 'hide', fwd = !up &&",
    "  { const as = P.assistT > 0 && !P.slam; if (b._as !== as) { b._as = as; b.classList.toggle('assist', as); } }\n"
    "  const up = P.st === 'hide', fwd = !up &&")
rep(".slamBtn::after{display:none} /* (the cooldown is the corner dial's; no pie over the disc) */",
    ".slamBtn::after{display:none} /* (the cooldown is the corner dial's; no pie over the disc) */\n"
    ".slamBtn.assist{animation:sbassist .26s ease-in-out infinite alternate}\n"
    "@keyframes sbassist{from{transform:scale(1.04)}to{transform:scale(1.16)}}\n"
    ".slamBtn.assist::after{display:block;content:'';position:absolute;inset:-7px;border-radius:50%;background:none;border:4px solid #FFD84A;box-shadow:0 0 18px rgba(255,216,74,.85);animation:sbring .55s ease-out infinite;pointer-events:none}\n"
    "@keyframes sbring{from{transform:scale(.92);opacity:1}to{transform:scale(1.32);opacity:0}}\n"
    "@media (prefers-reduced-motion:reduce){.slamBtn.assist,.slamBtn.assist::after{animation:none}}")
# (left alone, the hop just comes back down: no stomp off the rival's head on the way, it lands a little past them)
rep("  for (let s = 0, A = P, B = H; s < 2; s++, A = H, B = P) if (A.air && A.vy < -0.5 && A.y > B.y + 0.25 && !A.slam && B.flatT <= 0",
    "  for (let s = 0, A = P, B = H; s < 2; s++, A = H, B = P) if (A.air && A.vy < -0.5 && A.y > B.y + 0.25 && !A.slam && !(A.assistT > 0) && B.flatT <= 0")
open(DST, 'w').write(s)
print('ui157 ok', n0, '->', len(s))
