#!/usr/bin/env python3
"""v214: the axolotl comes alive on its feet (tools/assets/axolife.js, built into its runtime by tools/mk_axo_embed.py; the adapter,
tools/assets/axoc.js, tells it how the ground moves under it). Its feet stay where they land whatever its speed or turn; its stride and step
rate come from its speed, from a slow creep to a lizard's scurry, with a salamander's S-wave through its back and tail; its head leads into
turns and leans with them, its gills swing out round them and overshoot; stopped, it breathes and resettles a stretched foot. A jump: it
pushes off, tucks, reaches for the ground, and one hand takes the landing before the others come down. A long slingshot pull curls it into
a ring that rolls through the air as fast as it flies, opening out to land."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui141_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
assert 'Animator.prototype.crawl = function' in s and 'A.motion.carry = carry;' in s, 'the new runtime and adapter are not in the build'
# shown again (popping out of the roller, back from a hidden spell): the axolotl's feet start again under it
rep("if (!was) { if (lookIntro) {", "if (!was) { if (I.kind === 'axo') I.ax.fresh = true; if (lookIntro) {")
rep('<p class="ver">Version 213</p>', '<p class="ver">Version 214</p>')
open(DST, 'w').write(s)
print('ui142 ok', n0, '->', len(s))
