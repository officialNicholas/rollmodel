#!/usr/bin/env python3
"""The menu song plays on, treble down, through the fight card and the vote; the announcer's ready call lands just before the countdown. On top of ui16_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui16_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# a 'vs' mode for the music: the track keeps going, the top end comes down (less than pause), a touch quieter
rep("musLP.frequency.setTargetAtTime(mode === 'pause' ? 650 : 20000, t, mode === 'pause' ? 0.06 : 0.12);",
    "musLP.frequency.setTargetAtTime(mode === 'pause' ? 650 : mode === 'vs' ? 2600 : 20000, t, mode === 'pause' ? 0.06 : mode === 'vs' ? 0.25 : 0.12);")
rep("trkBus.gain.setTargetAtTime(mode === 'pause' ? 0.7 : 1, t, 0.12);\n      if (mode === 'pause') { if (trk) { lastMode = mode; return true; } }",
    "trkBus.gain.setTargetAtTime(mode === 'pause' ? 0.7 : mode === 'vs' ? 0.82 : 1, t, mode === 'vs' ? 0.3 : 0.12);\n      if (mode === 'pause' || mode === 'vs') { if (trk || (trkPend === 'menu' && mode === 'vs')) { lastMode = mode; return true; } }")
rep("      if (mode === 'pause') vol(MUS_PLAY * 0.7, 0.12);\n", "      if (mode === 'pause') vol(MUS_PLAY * 0.7, 0.12);\n      else if (mode === 'vs') vol(MUS_MENU * 0.8, 0.3);\n")
# Play: the song stays on under the fight card and the vote
rep("  rollRivalLooks(); AU.init(); AU.music('end'); menu.classList.add('leaving');", "  rollRivalLooks(); AU.init(); AU.music('vs'); menu.classList.add('leaving');")
# the fight card no longer calls 'ready'; the clip is warmed with the count
rep("el.hidden = false; AU.whoosh(); for (const k of ['cd3', 'cd2', 'cd1', 'go']) AU.say(k, 0); setTimeout(() => AU.say('ready'), 350); buzz([15, 30, 15]);",
    "el.hidden = false; AU.whoosh(); for (const k of ['ready', 'cd3', 'cd2', 'cd1', 'go']) AU.say(k, 0); buzz([15, 30, 15]);")
# the song fades as the wipe takes us to the canvas
rep("  const id = runId, wipe = win => slashWipe({ dur: 1.0, onPeak: () => {", "  const id = runId, wipe = win => { AU.music('end'); slashWipe({ dur: 1.0, onPeak: () => {")
rep("    cb(); } });\n  if (mode === 'solo' || window.__noVote) {", "    cb(); } }); };\n  if (mode === 'solo' || window.__noVote) {")
# 'ready' lands as the canvas is decided (or a beat into a solo card): about two seconds before the count starts
rep("  if (mode === 'solo' || window.__noVote) { setTimeout(() => { if (id !== runId && state !== 'menu') { el.hidden = true; return cb(); } wipe(null); }, 2100); return; }",
    "  if (mode === 'solo' || window.__noVote) { setTimeout(() => { if (!(id !== runId && state !== 'menu')) AU.say('ready'); }, 900); setTimeout(() => { if (id !== runId && state !== 'menu') { el.hidden = true; return cb(); } wipe(null); }, 2100); return; }")
rep("box.classList.add('done'); $('vvWin').textContent = themeLabel(win); AU.pop(); buzz([14, 30, 14]); });",
    "box.classList.add('done'); $('vvWin').textContent = themeLabel(win); AU.pop(); AU.say('ready'); buzz([14, 30, 14]); });")
rep('<p class="ver">Version 86</p>', '<p class="ver">Version 87</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
