#!/usr/bin/env python3
"""The hit banners name the rival instead of calling it "it". On top of ui24_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui24_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("  else banner('It went giant!', 'Keep away');", "  else banner(nameOf(D) + ' went giant!', 'Keep away');")
rep("else if (D === P) { shake = Math.max(shake, 0.3); buzz(20); banner('Blasted it!'); }", "else if (D === P) { shake = Math.max(shake, 0.3); buzz(20); banner('Blasted ' + nameOf(O) + '!'); }")
rep("else if (A === P) { shake = Math.max(shake, 0.35); buzz(20); banner('Shrunk it!'); }", "else if (A === P) { shake = Math.max(shake, 0.35); buzz(20); banner('Shrunk ' + nameOf(B) + '!'); }")
rep("  else if (D === P) { shake = Math.max(shake, 0.25); buzz(20); banner('Bounced it out!'); }", "  else if (D === P) { shake = Math.max(shake, 0.25); buzz(20); banner('Bounced ' + nameOf(O) + ' out!'); }")
rep("  else if (A === P) { shake = Math.max(shake, 0.25); buzz(18); popText('Bounced it!'); }", "  else if (A === P) { shake = Math.max(shake, 0.25); buzz(18); popText('Bounced ' + nameOf(B) + '!'); }")
rep("  else if (A === P) { shake = Math.max(shake, 0.2); buzz(18); banner('Stunned it!', 'Pound it!'); }", "  else if (A === P) { shake = Math.max(shake, 0.2); buzz(18); banner('Stunned ' + nameOf(B) + '!', 'Pound ' + nameOf(B) + '!'); }")
rep("banner((reason === 'fall' && by ? 'Knocked it off!' : koLine(reason, false)) || 'Got it!');", "banner((reason === 'fall' && by ? 'Knocked ' + nameOf(D) + ' off!' : koLine(reason, false, nameOf(D))) || 'Got ' + nameOf(D) + '!');")
# the knockout lines take a name too
rep("const CPU_KO_MSG = { pound: 'Got it!', coffin: 'Nailed it!', fall: 'It fell off', sun: 'Baked it!', crush: 'Crushed it!', dry: 'It dried up!' };",
    "const CPU_KO_MSG = { pound: n => 'Got ' + n + '!', coffin: n => 'Nailed ' + n + '!', fall: n => n + ' fell off', sun: n => 'Baked ' + n + '!', crush: n => 'Crushed ' + n + '!', dry: n => n + ' dried up!' };")
rep("const koLine = (reason, mine) => reason === 'coffin' && TH.pot === 'can' ? (mine ? 'Canned!' : 'Canned it!') : reason === 'coffin' && (TH.pot === 'tiki' || TH.pot === 'tank') ? (mine ? 'Dunked!' : 'Dunked it!') : (mine ? KO_MSG : CPU_KO_MSG)[reason];",
    "const koLine = (reason, mine, n) => reason === 'coffin' && TH.pot === 'can' ? (mine ? 'Canned!' : 'Canned ' + n + '!') : reason === 'coffin' && (TH.pot === 'tiki' || TH.pot === 'tank') ? (mine ? 'Dunked!' : 'Dunked ' + n + '!') : mine ? KO_MSG[reason] : CPU_KO_MSG[reason] && CPU_KO_MSG[reason](n);")
rep('<p class="ver">Version 94</p>', '<p class="ver">Version 95</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
