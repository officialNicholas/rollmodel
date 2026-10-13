"""The Season 1 frame: the three Spooky SZN stages side by side in slanted panels (crypt, cathedral, manor), each panel the middle of its
stage's photo, thin dark gaps between, at the gallery frame's size. usage: triptych.py crypt.png cathedral.png manor.png out.png [W H]"""
import sys
from PIL import Image, ImageDraw
a, b, c, out = sys.argv[1:5]; W, H = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (720, 495)
ims = [Image.open(x).convert('RGB').resize((W, H), Image.LANCZOS) for x in (a, b, c)]
k = W / 440; slant = 45 * k; gap = 5 * k   # (the dividers lean like the old art's: about 45 px across its height at 440 wide)
xs = [W * 0.385, W * 0.715]                # (where each divider crosses the top edge)
canvas = Image.new('RGB', (W, H), (14, 10, 22))
def poly(x0, x1):  # (a panel between two dividers, each leaning left toward the bottom)
    return [(x0, 0), (x1, 0), (x1 - slant, H), (x0 - slant, H)]
bounds = [(-W, xs[0] - gap / 2), (xs[0] + gap / 2, xs[1] - gap / 2), (xs[1] + gap / 2, 2 * W)]
centers = [(-W + xs[0]) / 2, (xs[0] + xs[1]) / 2 - slant / 2, (xs[1] + W) / 2 - slant / 2]
for im, (x0, x1), cx in zip(ims, bounds, [W * 0.17, W * 0.53, W * 0.84]):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon(poly(x0, x1), fill=255)
    sh = int(cx - W / 2)   # (each stage's own middle under its panel)
    src = Image.new('RGB', (W, H)); src.paste(im, (sh, 0)); canvas.paste(src, (0, 0), m)
canvas.save(out); print('saved', out, canvas.size)
