#!/usr/bin/env python3
"""v253: the Strokes page icons, drawn by Ludo.ai in the game's house icon style (the UI kit's style reference). Four candidates each.
usage: strokeart.py [name ...]"""
import sys, os, subprocess, concurrent.futures as cf
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
OUT = S + '/art/stroke'; LUDO = S + '/tools/ludo.py'; REF = S + '/art/anchor_3.png'
STY = 'glossy toy-like stylized 3D mobile game UI, candy colors, thick dark navy outline, soft top highlight, small magenta and cyan paint splat flecks, Splatoon-inspired, clean silhouette, isolated on plain white background, no text'
ICO = 'single centered game ability icon object, chunky rounded shapes, glossy candy finish, thick dark navy outline, bright saturated colors, readable at small size, no frame, no badge, no background tile, ' + STY
JOBS = {
  'rocket':  'a chunky cartoon rocket blasting straight up, cream white body with bright red fins and a round sky blue window, a thick gush of glossy red paint pouring from its nozzle instead of fire, ' + ICO,
  'giant':   'a cute round pink axolotl head with big floppy ear-like gills and a big happy smile, swelling up huge, four bold yellow outward arrows around it, rainbow sparkles, ' + ICO,
  'freeze':  'a glowing ice blue six-pointed snowflake crystal over a bright white camera flash starburst, frosty sparkles, ' + ICO,
  'swim':    'a curling sky blue water wave with white foam and speed lines, a bold white forward arrow riding on the wave, ' + ICO,
  'repel':   'an open red and white striped umbrella, blue raindrops bouncing off its top, a small yellow sun peeking behind it, ' + ICO,
  'pockets': 'a bulging round brown leather pouch with a drawstring, stuffed with two glowing power-up orbs peeking out of the top, one red and one rainbow, ' + ICO,
  'soon':    'a wooden mystery crate with a big bold question mark on its front, lilac and purple, ' + ICO,
}
def run(name):
    out = f'{OUT}/{name}.png'
    if os.path.exists(out.replace('.png', '_1.png')): return name, 'exists'
    r = subprocess.run(['python3', '-I', LUDO, 'gen', out, 'icon', JOBS[name], '--ref', REF, '--n', '4', '--rid', f'st253-{name}'], capture_output=True, text=True)
    return name, ('ok' if r.returncode == 0 else 'FAIL ' + (r.stderr or r.stdout)[-300:])
names = sys.argv[1:] or list(JOBS)
with cf.ThreadPoolExecutor(4) as ex:
    for n, st in ex.map(run, names): print(n, st, flush=True)
