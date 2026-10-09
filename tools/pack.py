#!/usr/bin/env python3
"""Trim, resize and pack the Ludo art into /home/claude/ui/*.webp (what the game loads)."""
import os, glob, json, sys
from PIL import Image, ImageFilter
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
ART = S + '/art'; OUT = '/home/claude/art'
os.makedirs(OUT, exist_ok=True)
RULES = [  # (prefix, mode, size, quality)
    ('ic_', 'square', 176, 86), ('btn_round', 'square', 320, 86), ('btn_', 'trimh', 144, 88), ('panel_', 'trim', 640, 84), ('tab_bar', 'trimh', 144, 86), ('pill_hud', 'trimh', 112, 86),
    ('badge_', 'trim', 420, 86), ('splat_', 'trim', 420, 84), ('drip_top', 'trim', 900, 84), ('podium', 'trim', 640, 84),
    ('card_', 'fit', 520, 82), ('bg_menu_p', 'fit', 1280, 80), ('bg_menu_l', 'fit', 1400, 80), ('bg_', 'fit', 1280, 78), ('tex_', 'fit', 512, 84),
]
def trim(im, pad=2):
    a = im.split()[3].point(lambda v: 255 if v > 8 else 0)
    bb = a.getbbox()
    if not bb: return im
    x0, y0, x1, y1 = bb
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))
def square(im):
    s = max(im.width, im.height); sq = Image.new('RGBA', (s, s), (0, 0, 0, 0)); sq.paste(im, ((s - im.width) // 2, (s - im.height) // 2)); return sq
info = {}
only = sys.argv[1:]
for f in sorted(glob.glob(ART + '/*.webp')):
    name = os.path.basename(f)[:-5]
    if only and name not in only: continue
    rule = next((r for r in RULES if name.startswith(r[0])), None)
    if not rule: continue
    _, mode, size, q = rule
    im = Image.open(f).convert('RGBA')
    if mode == 'square': im = square(trim(im)); im = im.resize((size, size), Image.LANCZOS)
    elif mode == 'trimh': im = trim(im); im = im.resize((max(1, round(im.width * size / im.height)), size), Image.LANCZOS)
    elif mode == 'trim': im = trim(im); k = size / max(im.width, im.height); im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS) if k < 1 else im
    elif mode == 'fit': k = size / max(im.width, im.height); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS) if k < 1 else im
    out = f'{OUT}/{name}.webp'
    im.save(out, 'WEBP', quality=q, method=6)
    info[name] = [im.width, im.height, os.path.getsize(out)]
    print(f'{name:16} {im.width}x{im.height} {os.path.getsize(out)//1024}KB')
print('total KB', sum(v[2] for v in info.values()) // 1024)
json.dump(info, open(OUT + '/_info.json', 'w'))
