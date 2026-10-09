#!/usr/bin/env python3
"""The currency is called dabs, and its icon is a coin with a splat on it. On top of ui31_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui31_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
OLD_SVG = '<svg class="dropi" viewBox="0 0 16 20" aria-hidden="true"><path d="M8 1.5C8 1.5 2 9 2 12.5a6 6 0 0 0 12 0C14 9 8 1.5 8 1.5z"/></svg>'
# a coin: a gold disc with a darker rim and an inner ring, a splat stamped in the middle in whatever colour the context gives the icon
NEW_SVG = ('<svg class="dropi" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9" fill="#F2C14E" stroke="#8A5A12" stroke-width="1.6"/>'
           '<circle cx="10" cy="10" r="6.7" fill="none" stroke="#C98E22" stroke-width="1"/>'
           '<path d="M10 5.2c.9 0 1.3 1.1 2 1.5 1 .5 2.2-.3 2.6.7.4 1-.9 1.6-.9 2.6s1.2 1.6.7 2.5c-.5.9-1.6.2-2.5.6-.8.4-1 1.7-1.9 1.7s-1.1-1.3-2-1.7c-.9-.4-2 .3-2.5-.6s.7-1.5.7-2.5-1.3-1.6-.9-2.6c.4-1 1.6-.2 2.6-.7.7-.4 1.1-1.5 2.1-1.5z"/></svg>')
rep(OLD_SVG, NEW_SVG, 3)
rep('.dropi{width:.8em;height:1em;fill:var(--ink);vertical-align:-.12em;filter:drop-shadow(1px 1px 0 rgba(23,19,32,.35))}', '.dropi{width:1.05em;height:1.05em;fill:var(--ink);vertical-align:-.16em;filter:drop-shadow(1px 1px 0 rgba(23,19,32,.35))}')
rep('.lkbal .dropi{width:13px;height:16px}', '.lkbal .dropi{width:16px;height:16px}')
rep('.ltile .ltag .dropi{fill:#fff;width:9px;height:11px;filter:none}', '.ltile .ltag .dropi{fill:#fff;width:12px;height:12px;filter:none}')
rep('.niprice .dropi{fill:#fff;width:9px;height:12px;filter:none}', '.niprice .dropi{fill:#fff;width:12px;height:12px;filter:none}')
rep('.lcol.right .plate.stat.drops b .dropi{width:13px;height:16px;filter:none}', '.lcol.right .plate.stat.drops b .dropi{width:17px;height:17px;filter:none}')
# the name
rep('<div class="plate stat drops" title="Drops">', '<div class="plate stat drops" title="Dabs">')
rep('</svg>0</b><span>Drops</span></div>', '</svg>0</b><span>Dabs</span></div>')
rep('<span class="lkbal" id="lkBal" aria-label="Drops">', '<span class="lkbal" id="lkBal" aria-label="Dabs">')
rep('<b class="dropgain" id="dropGain" hidden>+0<small>drops</small></b>', '<b class="dropgain" id="dropGain" hidden>+0<small>dabs</small></b>')
rep("dg.innerHTML = '+' + info.drops + DROP_SVG + '<small>drops</small>';", "dg.innerHTML = '+' + info.drops + DROP_SVG + '<small>dabs</small>';")
rep("sale ? ', ' + PRICE(w) + ' drops' : ', locked'", "sale ? ', ' + PRICE(w) + ' dabs' : ', locked'")
rep("note('Needs ' + (PRICE(w) - (store.drops || 0)) + ' more drops. Matches pay in drops.', true);", "note('Needs ' + (PRICE(w) - (store.drops || 0)) + ' more dabs. Matches pay in dabs.', true);")
rep('<p class="ver">Version 101</p>', '<p class="ver">Version 102</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
