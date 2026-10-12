#!/usr/bin/env python3
"""v247: the Sludge Sewer gets its own song (Sewer Circuit: an intro, then a 16-bar loop cut to the sample with its seam faded across), the
Fishing Raft keeps the island song; and the raft dressed far more densely, toward the concept (its pieces live in tools/stage/raft.js)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui186_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- a stage can name its own song (the sewer); otherwise its style picks one as before. If its song can't be had, the style's plays
rep("let MUSIC_STYLE = 'spooky';", "let MUSIC_STYLE = 'spooky', MUSIC_TRK = null;")
rep("  TH = T; MUSIC_STYLE = musicStyleOf(T.id);", "  TH = T; MUSIC_STYLE = musicStyleOf(T.id); MUSIC_TRK = T.music || null;")
rep("    island: { a: 9.97837, b: 50.85615, k: 0.933 },", "    island: { a: 9.97837, b: 50.85615, k: 0.933 },\n    sewer: { a: 22.99298, b: 59.303, k: 0.807 },")
rep("  const stageTrk = () => STAGE_TRK[typeof MUSIC_STYLE === 'string' ? MUSIC_STYLE : ''] || null;",
    "  const stageTrk = () => (typeof MUSIC_TRK === 'string' && TRK[MUSIC_TRK] && !TRK[MUSIC_TRK].fail ? MUSIC_TRK : STAGE_TRK[typeof MUSIC_STYLE === 'string' ? MUSIC_STYLE : ''] || null);")
rep("for (const k of ['halloween', 'island', 'blank']) if (k !== sk) trkDrop(k);", "for (const k of ['halloween', 'island', 'blank', 'sewer']) if (k !== sk) trkDrop(k);")
# ---- a theme can ask for more pieces on its floor (the raft's crates)
rep("  const target = (2 * ARENA) * (2 * ARENA) * (EZ ? rr(0.11, 0.15) : rr(0.13, 0.19)), ezFill", "  const target = (2 * ARENA) * (2 * ARENA) * (EZ ? rr(0.11, 0.15) : rr(0.13, 0.19)) * (theme.fillMul || 1), ezFill")
rep("  for (let t = 0; t < 120 && area() < target; t++) {", "  for (let t = 0, tN = 120 * (theme.fillMul || 1); t < tN && area() < target; t++) {")
rep('<p class="ver">Version 246</p>', '<p class="ver">Version 247</p>')
open(DST, 'w').write(s); print('ui187 ok', n0, '->', len(s))
