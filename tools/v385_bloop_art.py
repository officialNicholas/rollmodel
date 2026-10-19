#!/usr/bin/env python3
"""v385: Ol' Bloop's three pictures (the user's art: normal, talking and making a point; serious, arms crossed; laughing), backgrounds
cut away with Ludo.ai, set in the game's 640x596 coach frame, standing on its bottom edge like the old picture.
usage: v385_bloop_art.py normal.png serious.png laugh.png  ->  game/art/coach.webp, coach_serious.webp, coach_laugh.webp"""
import sys, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); W, H = 640, 596
for src, name in zip(sys.argv[1:4], ['coach', 'coach_serious', 'coach_laugh']):
    im = Image.open(src).convert('RGBA'); k = W / im.width; im = im.resize((W, round(im.height * k)), Image.LANCZOS)
    if im.height > H: im = im.crop((0, im.height - H, W, im.height))
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c.paste(im, (0, H - im.height), im)
    out = os.path.join(HERE, '..', 'game', 'art', name + '.webp'); c.save(out, 'WEBP', quality=88, method=6); print(name, os.path.getsize(out))
