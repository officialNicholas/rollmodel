"""Construction paper for the lobby's Abilities square: a hand-cut sheet (not quite square, edges a touch uneven, fibres fraying out
of the cut), dyed through with soft mottling, the grain and the fibres and flecks of pulp you see in coarse coloured paper, and a faint
curl of light across it. Baked once to a webp with its own alpha.
usage: mk_cpaper.py <out.webp> [hex colour] [seed]"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
OUT = sys.argv[1]; HEX = sys.argv[2] if len(sys.argv) > 2 else '7458C2'; SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 7
rng = np.random.default_rng(SEED); W = H = 256; SS = 4  # (the edge is drawn 4x and brought down, so it is smooth where it should be)
base = np.array([int(HEX[i:i + 2], 16) for i in (0, 2, 4)], float) / 255
from scipy.ndimage import gaussian_filter
def field(r):
    f = gaussian_filter(rng.random((H, W)), r, mode='wrap'); return (f - f.mean()) / (f.std() + 1e-9)
# tone: dyed through, a little uneven (mottling), fine grain, and a soft curl of light from the top left
tone = 1 + 0.035 * field(18) + 0.02 * field(5) + 0.018 * rng.standard_normal((H, W))
yy, xx = np.mgrid[0:H, 0:W] / W; tone *= 1.05 - 0.09 * (0.6 * xx + 0.8 * yy)
img = np.clip(base[None, None, :] * tone[..., None], 0, 1)
# fibres: short wavy hairs, most a shade lighter (the pulp shows through), a few darker
fib = Image.new('L', (W * 2, H * 2), 0); dk = Image.new('L', (W * 2, H * 2), 0); fd, dd = ImageDraw.Draw(fib), ImageDraw.Draw(dk)
for i in range(1500):
    x, y = rng.random() * W * 2, rng.random() * H * 2; a = rng.random() * np.pi; L = rng.uniform(5, 22); bend = rng.normal(0, 0.35)
    pts = [(x + np.cos(a + bend * t) * L * t, y + np.sin(a + bend * t) * L * t) for t in np.linspace(0, 1, 6)]
    (dd if rng.random() < 0.22 else fd).line(pts, fill=int(rng.uniform(70, 170)), width=1)
fib = np.asarray(fib.resize((W, H), Image.LANCZOS), float) / 255; dk = np.asarray(dk.resize((W, H), Image.LANCZOS), float) / 255
img = img + (1 - img) * fib[..., None] * 0.2 - img * dk[..., None] * 0.16
# flecks of pulp: soft specks, lighter and darker, now and then one of another dye
fl = np.zeros((H * 3, W * 3, 4), float); flI = Image.new('RGBA', (W * 3, H * 3), (0, 0, 0, 0)); fdr = ImageDraw.Draw(flI)
for i in range(120):
    x, y = rng.uniform(4, W * 3 - 4), rng.uniform(4, H * 3 - 4); rx, ry = rng.uniform(0.8, 2.2), rng.uniform(0.6, 1.6)
    c = (255, 250, 240) if rng.random() < 0.5 else tuple(int(v * 255 * 0.5) for v in base) if rng.random() < 0.75 else (240, 200, 90)
    fdr.ellipse([x - rx, y - ry, x + rx, y + ry], fill=c + (int(rng.uniform(50, 120)),))
flA = np.asarray(flI.resize((W, H), Image.LANCZOS), float) / 255
img = img * (1 - flA[..., 3:]) + flA[..., :3] * flA[..., 3:]
# the cut: four corners nudged off square, each side wavering a little, a few fibres frayed out of the edge
m = Image.new('L', (W * SS, H * SS), 0); md = ImageDraw.Draw(m); pad = 7
cs = [(pad + rng.uniform(-2, 2.5), pad + rng.uniform(-2, 2.5)), (W - pad + rng.uniform(-2.5, 2), pad + rng.uniform(-2, 2.5)), (W - pad + rng.uniform(-2.5, 2), H - pad + rng.uniform(-2.5, 2)), (pad + rng.uniform(-2, 2.5), H - pad + rng.uniform(-2.5, 2))]
poly = []
for i in range(4):
    (x0, y0), (x1, y1) = cs[i], cs[(i + 1) % 4]; nx, ny = y1 - y0, x0 - x1; nl = np.hypot(nx, ny); nx, ny = nx / nl, ny / nl
    ph = rng.random() * 6.28
    for t in np.linspace(0, 1, 60, endpoint=False):
        w = 0.55 * np.sin(t * 9.4 + ph) + 0.35 * np.sin(t * 23 + ph * 2) + rng.normal(0, 0.18)
        poly.append(((x0 + (x1 - x0) * t + nx * w) * SS, (y0 + (y1 - y0) * t + ny * w) * SS))
md.polygon(poly, fill=255)
for i in range(110):
    j = rng.integers(len(poly)); (px, py) = poly[j]; (qx, qy) = poly[(j + 1) % len(poly)]; tx, ty = qx - px, qy - py; tl = np.hypot(tx, ty) + 1e-9
    ox, oy = ty / tl, -tx / tl; a = rng.normal(0, 0.6); L = rng.uniform(1.2, 3.2) * SS
    ex, ey = px + (ox * np.cos(a) - oy * np.sin(a)) * L, py + (ox * np.sin(a) + oy * np.cos(a)) * L
    md.line([(px - ox * SS, py - oy * SS), (ex, ey)], fill=int(rng.uniform(120, 230)), width=max(1, SS // 2))
alpha = np.asarray(m.resize((W, H), Image.LANCZOS), float) / 255
# the cut edge catches a little light
edge = np.clip(alpha - np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)), float) / 255, 0, 1)
img = img + (1 - img) * edge[..., None] * 0.18
out = np.dstack([np.clip(img, 0, 1), alpha]); Image.fromarray((out * 255).round().astype(np.uint8), 'RGBA').save(OUT, quality=88, method=6)
print('ok', OUT, HEX)
