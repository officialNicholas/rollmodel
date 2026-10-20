#!/usr/bin/env python3
"""v404: the Paint Boost picture for the Strokes page, made the way v277 made the others: drawn flat by Ludo.ai (solid
flat colours, one thick navy outline, no gloss), the white background cut away, then a thin cream sticker edge so they read on the
dark tiles. Writes tools/assets/pboost_flat_256.webp.
usage: v404_bomb_art.py gen | cut pboost=N"""
import sys, os, subprocess, concurrent.futures as cf
import numpy as np
from PIL import Image
from scipy import ndimage as nd
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/v404/ludo2'; LUDO = HERE + '/ludo.py'
STY = ('flat vector game icon, solid flat colors only, no gradients, no gloss, no highlights, no texture, no sparkles, no splatter, one thick '
       'uniform dark navy outline around the whole shape, very simple bold shapes, minimal detail, centered, plain white background')
JOBS = {
  'pboost': 'a big glossy hot pink paint drop with a bold lime green arrow pointing up beside it, and a small yellow lightning bolt on the drop. ' + STY,
}
T, R = 256, 9
def gen(name):
    r = subprocess.run(['python3', '-I', LUDO, 'gen', f'{OUT}/{name}.png', 'icon', JOBS[name], '--style', 'Flat Design', '--n', '4'], capture_output=True, text=True)
    return name, 'ok' if r.returncode == 0 else 'FAIL ' + (r.stderr or r.stdout)[-300:]
def cut(src):
    # the white around it: whatever light area touches the edge; the fringe takes the outline's colour so no white halo is left
    im = np.asarray(Image.open(src).convert('RGB')).astype(float); H, W, _ = im.shape
    lum = im.mean(2); lab, n = nd.label(im.min(2) > 170); edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge)); F = np.median(im[lum < 70], 0)
    fr = nd.binary_dilation(bg, iterations=3) & ~bg; a = np.ones((H, W)); a[bg] = 0
    a[fr] = np.minimum(1, np.clip((255 - lum) / (255 - F.mean()), 0, 1)[fr] * 1.05)
    out = np.dstack([im, a * 255]).astype(np.uint8); m = fr & (a < 0.98)
    for c in range(3): out[..., c][m] = F[c]
    return Image.fromarray(out, 'RGBA')
def sticker(im):
    a = np.asarray(im.getchannel('A')).astype(float) / 255; ring = np.clip(R + 0.5 - nd.distance_transform_edt(a < 0.5), 0, 1)
    base = np.zeros((im.size[1], im.size[0], 4), np.uint8); base[..., :3] = (244, 238, 227); base[..., 3] = (np.maximum(ring, a) * 255).astype(np.uint8)
    b = Image.fromarray(base, 'RGBA'); b.alpha_composite(im); return b
def finish(name, k):
    im = cut(f'{OUT}/{name}_{k}.png'); im = im.crop(im.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
    s = (T - 20 - 2 * R) / max(im.size); im = im.resize((round(im.size[0] * s), round(im.size[1] * s)), Image.LANCZOS)
    c = Image.new('RGBA', (T, T), (0, 0, 0, 0)); c.paste(im, ((T - im.size[0]) // 2, (T - im.size[1]) // 2))
    sticker(c).save(f'{HERE}/assets/{name}_flat_256.webp', 'WEBP', quality=88, method=6); return name, 'ok'
if __name__ == '__main__':
    if sys.argv[1] == 'gen':
        os.makedirs(OUT, exist_ok=True)
        with cf.ThreadPoolExecutor(2) as ex:
            for n, st in ex.map(gen, list(JOBS)): print(n, st, flush=True)
    else:
        for a in sys.argv[2:]: print(*finish(*a.split('=')), flush=True)
