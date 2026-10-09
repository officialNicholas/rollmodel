#!/usr/bin/env python3
"""The iris colours grey out while the dot eyes are on. On top of ui27_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui27_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
css = '''
/* dot eyes have no iris: the colours stand down until another style is picked */
.irises.off{opacity:.32;filter:grayscale(1);pointer-events:none;transition:opacity .25s,filter .25s}
.irises.off .eyec{cursor:default;transform:none}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]
rep("aria-pressed=\"' + (myLook.iris === k) + '\"><i></i></button>').join('');\n  railEdge();",
    "aria-pressed=\"' + (myLook.iris === k) + '\"><i></i></button>').join(''); $('irises').classList.toggle('off', myLook.eyes === 'dot'); $('irises').setAttribute('aria-disabled', myLook.eyes === 'dot' ? 'true' : 'false');\n  railEdge();")
rep("$('irises').addEventListener('click', e => { const b = e.target.closest('.eyec'); if (!b || b.dataset.i === myLook.iris) return;",
    "$('irises').addEventListener('click', e => { const b = e.target.closest('.eyec'); if (!b || b.dataset.i === myLook.iris || myLook.eyes === 'dot') return;")
rep('<p class="ver">Version 97</p>', '<p class="ver">Version 98</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
