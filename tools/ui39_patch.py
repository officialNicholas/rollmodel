#!/usr/bin/env python3
"""Prices on locked tiles too; the blob's outline thinned by about a third. On top of ui38_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui38_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# every item you do not own shows its price, found or not; a locked one's tag is muted
rep("+ (sale ? '<span class=\"ltag\">' + DROP_SVG + PRICE(w) + '</span>' : '') + '<svg viewBox=\"0 0 40 40\" aria-hidden=\"true\">' + WEAR_ICON[w.id]",
    "+ (own ? '' : '<span class=\"ltag\">' + DROP_SVG + PRICE(w) + '</span>') + '<svg viewBox=\"0 0 40 40\" aria-hidden=\"true\">' + WEAR_ICON[w.id]")
css = '''
.ltile.locked .ltag{background:#8E8698;color:#fff}
.ltile.locked .ltag .dropi{opacity:.85}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]
# the slime's ink line: about a third thinner
rep("transformed += sN * clamp(0.34 * sLine * dz / max(sc, 1e-3), 0.004, 0.019); }", "transformed += sN * clamp(0.24 * sLine * dz / max(sc, 1e-3), 0.003, 0.0135); }")
rep('<p class="ver">Version 108</p>', '<p class="ver">Version 109</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
