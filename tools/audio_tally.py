#!/usr/bin/env python3
"""Ludo sounds for the tally and the knock-out flood. Idempotent by output file."""
import os, subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
LA = S + '/la/sfx2'; LUDO = S + '/tools/ludo.py'
def run(out, args, timeout=600):
    if os.path.exists(out): return True
    r = subprocess.run(['python3', '-I', LUDO] + args, capture_output=True, text=True, timeout=timeout)
    print(os.path.basename(out), 'ok' if r.returncode == 0 else 'FAIL', (r.stderr.strip().splitlines() or [''])[-1][:160], flush=True)
    return r.returncode == 0
SFX = [
 ('tpour', 2, 2.4, 'thick wet paint pouring steadily into a glass tank, smooth gloopy liquid pour, no music, cartoon game sound'),
 ('ttick', 2, 0.25, 'a tiny wet bubble pop, a single soft tick of a counter made of paint, very short, cartoon game sound'),
 ('tslice', 2, 0.6, 'a dollop of thick paint splatting onto a surface with a wet slap and a little splash, short, cartoon game sound'),
 ('tsplash', 2, 1.6, 'a giant wave of thick paint splashing across a wall, huge gloopy whoosh and splash with droplets raining, cartoon game sound'),
 ('tsettle', 1, 1.2, 'thick paint sloshing and settling in a tank, wet liquid wobble, cartoon game sound'),
 ('kflood', 2, 1.1, 'a rush of thick paint flooding over a window, gloopy liquid wave covering everything, cartoon game sound'),
 ('kpart', 2, 0.9, 'a sheet of thick paint tearing open with a wet peel and a splash, cartoon game sound'),
]
for k, n, dur, desc in SFX:
    for v in range(1, n + 1): run(f'{LA}/{k}_{v}.mp3', ['sfx', f'{LA}/{k}_{v}.mp3', desc, '--dur', str(dur), '--rid', f'rm9-{k}-{v}'])
