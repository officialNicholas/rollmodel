#!/usr/bin/env python3
"""Room around the locker's buttons: the colour row clears the slot cards (the dot under your colour no longer sits on them), the cards keep a clear gap from each other and from Done, and Done's drips no longer run into the unlock link. The short landscape layout trims the cards and the button to make that room. On top of ui64_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui64_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
css = '''
/* the locker: room around its buttons */
.lookp{gap:12px}
.lookp[data-tab="paint"] .swatches{padding:4px 0 12px}
.lookp[data-tab="eyes"] .leyes{margin:4px 0 6px}
.seg.lcats{gap:10px}
.lookp .btn.play.sm{margin-top:8px}
.lookp .ulink{margin-top:14px}
.lookp .ctitle{white-space:nowrap;font-size:clamp(19px,5.6vw,26px)}
.lookp .lktop{align-items:center;min-width:0}
.lookp .lktop .ctitle{flex:0 0 auto}
.lookp .lktop .lkbal{flex:0 0 auto}
.lookp .lktop .lnbtn{flex:0 1 auto;min-width:0;max-width:none}
@media (max-aspect-ratio:1/1){.lookp .ctitle{font-size:20px}.lookp .lktop{gap:8px}}
@media (max-height:520px) and (min-aspect-ratio:1/1){.sheet.lookp{align-content:space-between}.lookp{gap:8px}.lookp[data-tab="paint"] .swatches{padding:0 0 9px}.lookp .sw{height:40px}.seg.lcats{gap:8px}.seg.lcats button,.seg.lcats button[aria-selected="true"]{min-height:58px;padding:4px 3px 5px}.lookp .btn.play.sm{min-height:44px;margin-top:4px;padding-top:0;padding-bottom:0}.lookp .ulink{margin-top:11px}.lookp .ctitle{font-size:20px}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
