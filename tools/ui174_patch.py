#!/usr/bin/env python3
"""v240 onboarding tidy: in the locker the coach's tips about a category card come up from below the cards (the hand used to reach down
across the name pill), the NEW tags sit on the card's top edge instead of over its label, and the short lines read as sentences."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui173_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the NEW tag on a category card or tile: on the top edge, clear of the label
rep('content:"NEW"!important;position:absolute!important;top:-9px!important;right:-7px!important;left:auto!important;width:auto!important;height:auto!important;padding:3px 7px!important;border-radius:6px!important;border:0!important;background:var(--gold)!important;color:#171320!important;font:900 10px/1 var(--font-head)!important;',
    'content:"NEW"!important;position:absolute!important;top:-12px!important;right:-5px!important;left:auto!important;width:auto!important;height:auto!important;padding:3px 6px!important;border-radius:6px!important;border:0!important;background:var(--gold)!important;color:#171320!important;font:900 9px/1 var(--font-head)!important;')
# the locker's category tips: the hand lands on the left part of the card, clear of the name pill beside the cards
rep("const r = el.getBoundingClientRect(), cx = r.left - r0.left + r.width / 2, cw = Math.min(tutEl.offsetWidth, viewW - 24);",
    "const r = el.getBoundingClientRect(), cx = r.left - r0.left + r.width * (lookOpen && el.classList.contains('lcat') ? 0.28 : 0.5), cw = Math.min(tutEl.offsetWidth, viewW - 24); /* (a locker category card: the hand on its left part, clear of the name pill) */")
# the locker's category tips, as sentences
rep("if (lookCat !== 'face') return tutShow('Open Facial', 'lc-face', 'face'); return tutShow('Tap the fangs to wear them', () => tile('fangs'), 'wear'); }",
    "if (lookCat !== 'face') return tutShow('Open Facial. Your fangs are in there', 'lc-face', 'face'); return tutShow('Tap the fangs to put them on', () => tile('fangs'), 'wear'); }")
rep("if (lookCat !== 'head') return tutShow('Now your flower. Open Headgear', 'lc-head', 'headg'); return tutShow('Tap the flower to wear it', () => tile('flower'), 'wearf'); }",
    "if (lookCat !== 'head') return tutShow('Now the flower. Open Headgear', 'lc-head', 'headg'); return tutShow('Tap the flower to tuck it in', () => tile('flower'), 'wearf'); }")
rep("if (lookCat !== 'eyes') return tutShow('Open Eyes', 'lc-eyes', 'eyesz'); return tutShow('Tap the zombie eyes to wear them',",
    "if (lookCat !== 'eyes') return tutShow('Open Eyes and try them on', 'lc-eyes', 'eyesz'); return tutShow('Tap the zombie eyes to put them on',")
rep("tutShow('Open your locker to wear your fangs and flower', 'lookBtn', 'locker')", "tutShow('Open your locker and try on your fangs and flower', 'lookBtn', 'locker')")
open(DST, 'w').write(s)
print('ui174 ok', n0, '->', len(s))
