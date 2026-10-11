#!/usr/bin/env python3
"""v226: the onboarding's first word. The lobby shows clean for a second first; then the dark and the blur come in slowly over the page,
and Ol' Bloop's plate slides up into place (the hand with it) once they are most of the way in. (Before, the tip popped up over the lobby
the instant it appeared.)"""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui158_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# a second of the lobby first
rep("let tut2 = null, tut = null, tutPrev = null, tutTip = null, tutWinDue = false, tutNiAt = 0;",
    "let tut2 = null, tut = null, tutPrev = null, tutTip = null, tutWinDue = false, tutNiAt = 0, tutFirstAt = 0; // tutFirstAt: when the lobby first stood clear for the onboarding's first word (it waits a second)")
rep("  if (ph === 'match') { if (state === 'menu' && menuPage === 'home' && !lookOpen && !shopOpen && !irisBusy && setModal.hidden && nameModal.hidden && howModal.hidden) tutShow('Hey, rookie! Ready to roll? Your first match is a little training session. Tap Play and show me what you\\u2019ve got!', 'homePlay', 'first'); else tutHide(); return; }",
    "  if (ph === 'match') { if (state === 'menu' && menuPage === 'home' && !lookOpen && !shopOpen && !irisBusy && setModal.hidden && nameModal.hidden && howModal.hidden) { if (!tutFirstAt) tutFirstAt = performance.now(); if (performance.now() - tutFirstAt < 1000) return tutHide(); /* (a second of the lobby first) */ tutShow('Hey, rookie! Ready to roll? Your first match is a little training session. Tap Play and show me what you\\u2019ve got!', 'homePlay', 'first'); } else tutHide(); return; }")
# the first word comes in slowly: the dark and the blur ease in, the plate slides up after them
rep("tutEl.dataset.style = call ? 'call' : 'coach';",
    "tutEl.dataset.style = call ? 'call' : 'coach'; { const fw = key === 'first'; if (tutEl.classList.contains('swipe') !== fw) tutEl.classList.toggle('swipe', fw); if (tutDim.classList.contains('slow') !== fw) tutDim.classList.toggle('slow', fw); }")
CSS = """
/* the onboarding's first word: the dark and the blur ease in over the lobby, then the plate slides up into place, the hand with it */
.tutdim.slow>b{transition:opacity .9s ease,-webkit-backdrop-filter .9s ease,backdrop-filter .9s ease,top .22s,left .22s,width .22s,height .22s;-webkit-backdrop-filter:blur(0px);backdrop-filter:blur(0px)}
.tutdim.slow.on>b{-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px)}
.tut.swipe.on .tplate{animation:tutup .6s cubic-bezier(.2,1,.3,1) .75s both}
.tut.swipe.on .thand{animation:tutup .6s cubic-bezier(.2,1,.3,1) .75s both,tutbob .6s ease-in-out 1.35s infinite alternate}
@keyframes tutup{from{translate:0 70px;opacity:0}to{translate:0 0;opacity:1}}
@media (prefers-reduced-motion:reduce){.tutdim.slow>b{transition:opacity .3s}.tut.swipe.on .tplate,.tut.swipe.on .thand{animation:none}}
"""
idx = s.rfind('</style>'); assert idx > 0 and s.count('</style>') == 3
s = s[:idx] + CSS.lstrip('\n') + s[idx:]
open(DST, 'w').write(s)
print('ui159 ok', n0, '->', len(s))
