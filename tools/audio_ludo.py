#!/usr/bin/env python3
"""Ludo audio for Roll Model: announcer voice candidates, the blob's little voice, and the gameplay effects. Idempotent by output file."""
import os, subprocess, sys
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
LA = S + '/la'; LUDO = S + '/tools/ludo.py'
for d in ('voice', 'vox', 'sfx'): os.makedirs(f'{LA}/{d}', exist_ok=True)
def run(out, args, timeout=600):
    if os.path.exists(out): return True
    r = subprocess.run(['python3', '-I', LUDO] + args, capture_output=True, text=True, timeout=timeout)
    print(os.path.basename(out), 'ok' if r.returncode == 0 else 'FAIL', (r.stderr.strip().splitlines() or [''])[-1][:120], flush=True)
    return r.returncode == 0
STAGE = sys.argv[1] if len(sys.argv) > 1 else 'all'
# 1. the announcer: three takes on the voice, the best (deepest, punchiest) becomes the sample the lines are cut from
ANN = [('a', 'a deep, booming boxing ring announcer, huge chest voice, hype and action packed, rolling his words like a championship fight introduction'),
       ('b', 'a legendary fight night ring announcer with an extremely deep, gravelly bass voice, dramatic, drawn-out, electrifying, arena microphone'),
       ('c', 'an over-the-top wrestling and boxing announcer, deep powerful baritone, explosive energy, shouting the names of champions into a stadium')]
if STAGE in ('all', 'ann'):
    for k, desc in ANN: run(f'{LA}/voice/ann_{k}.mp3', ['voice', f'{LA}/voice/ann_{k}.mp3', desc, "Ladies and gentlemen! Are you ready? Let's get ready to ROLL!", '--type', 'human', '--rid', 'rm7-ann-' + k])
# 2. the blob: a small rubbery jelly creature, each cue twice
VOX = [('whee', 'Wheeee!'), ('hup', 'Hup!'), ('hyah', 'Hyah!'), ('oof', 'Oof!'), ('waah', 'Waaah!'), ('yay', 'Yay!'), ('ooh', 'Ooh?'), ('giggle', 'Hee hee hee!'), ('eep', 'Eep!'), ('brr', 'Brrrr!'), ('hoh', 'Ho ho!'), ('ahh', 'Aaahh!')]
VDESC = 'a tiny bouncy jelly blob creature, squeaky, cute, playful, rubbery, short excited yelps'
if STAGE in ('all', 'vox'):
    for k, t in VOX:
        for v in (1, 2): run(f'{LA}/vox/vox_{k}_{v}.mp3', ['voice', f'{LA}/vox/vox_{k}_{v}.mp3', VDESC, t if v == 1 else t.rstrip('!?') + '!', '--rid', f'rm7-vox-{k}-{v}'])
# 3. the effects: thick wet paint, rubber and splashes; two takes each where it repeats a lot
SFX = [
 ('splat_s', 2, 1, 'a small wet paint droplet splatting onto a canvas, short gloopy splat, cartoon game sound'),
 ('splat_m', 2, 1, 'a thick wet paint splat hitting a canvas, gloopy, juicy, short, cartoon game sound effect'),
 ('splat_l', 2, 1.5, 'a huge bucket of thick wet paint splashing down onto a floor, heavy gloopy splat with splashing droplets, cartoon game sound'),
 ('plop', 2, 0.6, 'a single small drop of thick paint plopping, tiny cute plop, cartoon'),
 ('land_s', 2, 0.6, 'a soft rubbery jelly ball landing on a floor, short squishy thump, cartoon game sound'),
 ('land_h', 2, 0.8, 'a heavy wet jelly blob slamming down onto a floor, deep squishy thud with a wet splash, cartoon game sound'),
 ('jump', 2, 0.6, 'a rubbery jelly creature boinging up into a jump, quick cartoon spring boing with a wet pop'),
 ('glug', 2, 0.6, 'a single short glug of thick liquid paint being gulped from a bucket, cartoon'),
 ('squish', 2, 0.9, 'a jelly blob being squashed flat with a wet squelch and splatter, cartoon game sound'),
 ('whoosh', 2, 0.8, 'a fast heavy whoosh of something big swinging past, cartoon game sound, airy'),
 ('swish', 2, 0.5, 'a quick light swish of air, short, soft, cartoon game sound'),
 ('dash', 2, 0.7, 'a fast wet zip, a jelly creature dashing forward with a slippery squeal and a splash of paint, cartoon game sound'),
 ('brake', 2, 0.6, 'a short wet rubbery skid, a jelly blob stopping suddenly on a wet floor, cartoon'),
 ('fling_s', 2, 0.8, 'a small wet flick of paint being flung through the air, short splatty whoosh, cartoon game sound'),
 ('fling_m', 2, 1, 'a jelly blob being flung from a slingshot, stretchy rubber twang then a wet whoosh, cartoon game sound'),
 ('fling_l', 2, 1.3, 'a huge rubber slingshot launch, deep stretchy twang, massive wet whoosh and a splash, cartoon game sound'),
 ('bonk_s', 2, 0.5, 'two rubber balls bumping into each other, short soft bonk, cartoon game sound'),
 ('bonk_h', 2, 0.6, 'a hard rubbery bonk, two heavy jelly blobs crashing together with a wet smack, cartoon game sound'),
 ('slam', 2, 1.6, 'a heavy ground pound: a big wet blob smashing down onto the floor with a deep boom and a splash of paint, cartoon game sound'),
 ('quake', 1, 2.2, 'a giant impact shaking the ground, deep rumbling boom with a wet splash, cartoon game sound'),
 ('burst', 2, 1.3, 'a giant paint balloon bursting outward, big wet explosive splash with droplets raining down, cartoon game sound'),
 ('die', 2, 1.3, 'a jelly creature deflating and popping with a sad wet splat, cartoon game sound'),
 ('die_pound', 1, 0.7, 'a blob being flattened by a heavy pound, wet squash and pop, cartoon game sound'),
 ('die_dry', 1, 0.8, 'a dried-up blob cracking and crumbling to dust, cartoon game sound'),
 ('pop', 2, 0.5, 'a quick bubbly wet pop, cartoon game sound'),
 ('power', 2, 1, 'a magical power-up pickup, bright sparkly ascending chime with a wet bubbly pop, cartoon game sound'),
 ('orb', 1, 1.6, 'a magical glowing orb being absorbed, rising shimmering swell into a deep thump, cartoon game sound'),
 ('grow', 1, 1.4, 'a blob inflating huge, stretchy rubber swelling up with a rising whoosh, cartoon game sound'),
 ('shrink', 1, 1, 'a blob deflating back to small, descending rubbery squeak with a puff of air, cartoon game sound'),
 ('splash', 2, 1, 'a blob diving into a bucket of thick paint, deep gloopy splash, cartoon game sound'),
 ('enter', 1, 1, 'a blob sinking down into a bucket of thick paint with a gloopy slurp, cartoon game sound'),
 ('horn', 1, 1.5, 'a final round boxing bell ringing three times fast, arena, bright and urgent'),
 ('fanfare', 1, 2.5, 'a short triumphant victory fanfare, brass stab and a cymbal crash, game show win, bright and punchy'),
 ('go', 1, 1.2, 'a boxing round start bell ding with a cymbal crash and a crowd roar, short, exciting'),
 ('heaton', 1, 1.5, 'a blazing sun flare whoosh with a hot sizzle, heat wave rising, game sound'),
 ('rocket', 1, 1.5, 'a cartoon rocket launching with a wet whoosh and a rising whistle, game sound'),
 ('shoot', 2, 0.6, 'a cannon shooting a blob of paint, short wet thunk and whoosh, cartoon game sound'),
 ('turret', 1, 1, 'a mechanical turret locking on with a clunky click and a wet gurgle, cartoon game sound'),
]
if STAGE in ('all', 'sfx'):
    for name, takes, dur, desc in SFX:
        for v in range(1, takes + 1): run(f'{LA}/sfx/{name}_{v}.mp3', ['sfx', f'{LA}/sfx/{name}_{v}.mp3', desc + (' (take two, slightly different)' if v == 2 else ''), '--dur', str(dur), '--rid', f'rm7-sfx-{name}-{v}'])
print('done', STAGE)
