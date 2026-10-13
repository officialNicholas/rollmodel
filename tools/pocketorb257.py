"""Deep Pockets picture: the denim pocket (Ludo.ai) with the game's own orb (rendered with its shader) in place of the rainbow ball.
usage: pocketorb257.py T  (the orb's colour moment, as rendered by orbshot257.py)"""
import sys, colorsys
import numpy as np
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'; T = sys.argv[1] if len(sys.argv) > 1 else '4.5'
P = np.asarray(Image.open(S + '/art/stroke257/pocketsA_3_cut.png').convert('RGBA')).astype(float) / 255
H, W = P.shape[:2]; rgb = P[..., :3]; A = P[..., 3]
mx = rgb.max(2); mn = rgb.min(2); V = mx; Sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
r_, g_, b_ = rgb[..., 0], rgb[..., 1], rgb[..., 2]
hue = np.zeros_like(V); d = np.maximum(mx - mn, 1e-6)
hue = np.where(mx == r_, ((g_ - b_) / d) % 6, np.where(mx == g_, (b_ - r_) / d + 2, (r_ - g_) / d + 4)) * 60
# the rainbow ball: bright, saturated, not denim blue, in the upper part
ball = (A > 0.9) & (Sat > 0.45) & (V > 0.45) & ((hue < 170) | (hue > 250)); ball[int(H * 0.55):, :] = False
ys, xs = np.nonzero(ball); x0, x1, y0 = xs.min(), xs.max(), ys.min(); r = (x1 - x0) / 2; cx = (x0 + x1) / 2; cy = y0 + r
print('ball', round(cx, 1), round(cy, 1), round(r, 1))
# the front rim's top edge: in columns clear of the ball, scan up from inside the rim band to the first pixel that isn't light denim
rimlike = (A > 0.9) & (r_ < 0.36) & (g_ > 0.70) & (b_ > 0.80)   # (the rim's light denim, ~#30C8EB; the ball's own blue band is deeper)
dark = (A > 0.9) & (V < 0.36)
pts = []
for x in range(int(cx - r * 2.2), int(cx + r * 2.2)):
    if abs(x - cx) < r + 14 or x < 0 or x >= W: continue
    y = int(cy + r * 0.25)
    if not rimlike[y, x]: continue
    while y > 0 and rimlike[y - 1, x]: y -= 1
    if dark[max(0, y - 3), x]: pts.append((x, y))   # (only where the opening's dark inside sits above it)
pts = np.array(pts); co = np.polyfit(pts[:, 0], pts[:, 1], 2); rim = np.polyval(co, np.arange(W))
# under the ball the rim's real top edge too, then one smooth curve through every edge point
edge = [tuple(q) for q in pts]
for x in range(int(cx - r - 18), int(cx + r + 19)):
    for y in range(int(rim[x]) - 14, int(rim[x]) + 10):
        if rimlike[y:y + 3, x].all(): edge.append((x, y)); break
edge = np.array(edge, dtype=float); co = np.polyfit(edge[:, 0], edge[:, 1], 3); rim = np.polyval(co, np.arange(W))
print('edge pts', len(edge), 'at ball', round(float(np.polyval(co, cx)), 1))
yy, xx = np.mgrid[0:H, 0:W]; dist = np.hypot(xx - cx, yy - cy); above = np.clip(rim[None, :] - yy + 0.5, 0, 1)
# fill the ball (and its own dark halo) with the inside of the pocket: each row blended across from either side of it
R2 = r + 18; out = P.copy(); xl, xr = int(cx - R2 - 6), int(cx + R2 + 6)
for y in range(max(0, int(cy - R2)), min(H, int(cy + R2) + 1)):
    cl, cr = rgb[y, xl], rgb[y, xr]
    for x in range(max(0, int(cx - R2)), min(W, int(cx + R2) + 1)):
        if dist[y, x] > R2 or above[y, x] <= 0: continue
        if dist[y, x] > r + 2 and rimlike[y, x]: continue   # (the back rim stays)
        t = (x - xl) / (xr - xl); c = cl * (1 - t) + cr * t; k = above[y, x]
        out[y, x, :3] = out[y, x, :3] * (1 - k) + c * k
# the orb: its glow added over the inside, then the orb itself, both behind the front rim
ob = np.asarray(Image.open(f'{S}/art/orb257/core_{T}_b.png').convert('RGB')).astype(float) / 255
ow = np.asarray(Image.open(f'{S}/art/orb257/core_{T}_w.png').convert('RGB')).astype(float) / 255
og = np.asarray(Image.open(f'{S}/art/orb257/glow_{T}.png').convert('RGB')).astype(float) / 255
oa = np.clip(1 - (ow - ob).mean(2), 0, 1); oc = np.clip(ob / np.maximum(oa[..., None], 1e-3), 0, 1)
N = ob.shape[0]; hull_px = 0.42 * 1.1 / 1.9 * N; OS, OUP = float(sys.argv[2]) if len(sys.argv) > 2 else 1.15, float(sys.argv[3]) if len(sys.argv) > 3 else 0.16  # (a touch bigger than the ball it replaces, and riding higher: it reads at tile size)
sc = r * OS / hull_px; M = int(round(N * sc))
def place(arr):
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype('uint8')).resize((M, M), Image.LANCZOS); a = np.asarray(im).astype(float) / 255
    full = np.zeros((H, W) + a.shape[2:]); ox, oy = int(round(cx - M / 2)), int(round(cy - M / 2 - r * OUP))
    sx0, sy0 = max(0, -ox), max(0, -oy); dx0, dy0 = max(0, ox), max(0, oy); w_ = min(M - sx0, W - dx0); h_ = min(M - sy0, H - dy0)
    full[dy0:dy0 + h_, dx0:dx0 + w_] = a[sy0:sy0 + h_, sx0:sx0 + w_]; return full
G = place(og) * above[..., None]; CA = place(oa)[..., None] * above[..., None] if place(oa).ndim == 2 else place(oa)[..., :1]; CC = place(oc)
if CA.ndim == 2: CA = CA[..., None]
base_a = out[..., 3:4]; col = out[..., :3] * base_a + G            # (premultiplied: the glow is light added)
na = np.clip(base_a + G.max(2, keepdims=True), 0, 1)
col = col * (1 - CA) + CC * CA; na = na * (1 - CA) + CA
res = np.concatenate([np.clip(col / np.maximum(na, 1e-4), 0, 1), na], 2)
img = Image.fromarray((res * 255).astype('uint8'), 'RGBA'); img.save(f'{S}/art/stroke257/pocket_orb_{T}.png')
bb = img.getbbox(); c = img.crop(bb); c.thumbnail((244, 244), Image.LANCZOS); can = Image.new('RGBA', (256, 256), (0, 0, 0, 0)); can.paste(c, ((256 - c.size[0]) // 2, (256 - c.size[1]) // 2), c)
can.save(f'{S}/tools/assets/pockets257_256.webp', 'WEBP', quality=88, method=6); print('saved', can.getbbox())
