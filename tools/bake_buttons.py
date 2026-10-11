"""v205: the round in-match buttons as plain pictures. Safari punched a hole in the masked, colour-blended disc wherever the icon
(on its own layer) sat, so the game showed through the middle of the pound button. These are the same discs, worked out the way the
browser did (luminosity blend of the sticker over the colour, the sticker as the mask, the brightness/saturate/grayscale filters,
the drop shadow), baked into webp: the pound button's ready, recharging, boost, boost recharging and locked looks, and the item
button's cream disc."""
import numpy as np
from PIL import Image
SRC = '/home/user/rollmodel/game/art/m_dot.webp'; OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/btnart/'
im = np.asarray(Image.open(SRC).convert('RGBA')).astype(np.float64) / 255; H, W = im.shape[:2]
Cs, As = im[..., :3], im[..., 3:4]
hexc = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float64) / 255
def lum(C): return C[..., 0:1] * 0.3 + C[..., 1:2] * 0.59 + C[..., 2:3] * 0.11
def clip(C):
    l = lum(C); n = C.min(-1, keepdims=True); x = C.max(-1, keepdims=True)
    C = np.where(n < 0, l + (C - l) * l / np.maximum(l - n, 1e-9), C)
    C = np.where(x > 1, l + (C - l) * (1 - l) / np.maximum(x - l, 1e-9), C)
    return C
def luminosity_over(cb):  # background: url(sticker), <colour>; background-blend-mode: luminosity; then the sticker as the mask
    Cb = np.broadcast_to(cb, Cs.shape); B = clip(Cb + (lum(Cs) - lum(Cb)))
    return np.concatenate([As * B + (1 - As) * Cb, As], -1)
def brightness(img, k): out = img.copy(); out[..., :3] = np.clip(out[..., :3] * k, 0, 1); return out
def saturate(img, s):
    M = np.array([[0.213 + 0.787 * s, 0.715 - 0.715 * s, 0.072 - 0.072 * s], [0.213 - 0.213 * s, 0.715 + 0.285 * s, 0.072 - 0.072 * s], [0.213 - 0.213 * s, 0.715 - 0.715 * s, 0.072 + 0.928 * s]])
    out = img.copy(); out[..., :3] = np.clip(img[..., :3] @ M.T, 0, 1); return out
def grayscale(img):
    M = np.array([[0.2126, 0.7152, 0.0722]] * 3); out = img.copy(); out[..., :3] = np.clip(img[..., :3] @ M.T, 0, 1); return out
def radial(stops, cx, cy):  # radial-gradient(circle at cx cy, ...) over the box, farthest-corner
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64); px, py = cx * W, cy * H
    R = max(np.hypot(px - x, py - y) for x in (0, W) for y in (0, H)); t = np.hypot(xx - px, yy - py) / R
    out = np.zeros((H, W, 3))
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1); f = ((t - t0) / (t1 - t0))[..., None]; out = np.where(m[..., None], hexc(c0) * (1 - f) + hexc(c1) * f, out)
    return out
def with_shadow(img, css_w, css_dx=4, css_dy=6, col='#171320', a=0.3):  # filter: drop-shadow(4px 6px 0 rgba(23,19,32,.3)), the box grown to hold it
    dx, dy = round(css_dx * W / css_w), round(css_dy * H / css_w)
    out = np.zeros((H + dy, W + dx, 4)); sh = np.zeros_like(out); sh[dy:, dx:, :3] = hexc(col); sh[dy:, dx:, 3:4] = img[..., 3:4] * a
    top = np.zeros_like(out); top[:H, :W] = img
    ao = top[..., 3:4] + sh[..., 3:4] * (1 - top[..., 3:4]); co = (top[..., :3] * top[..., 3:4] + sh[..., :3] * sh[..., 3:4] * (1 - top[..., 3:4])) / np.maximum(ao, 1e-9)
    return np.concatenate([co, ao], -1), (dx, dy)
def save(img, name):
    a = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8); Image.fromarray(a, 'RGBA').save(OUT + name, 'WEBP', quality=92, method=6, exact=True)
red = luminosity_over(hexc('#E3122F')); boost = luminosity_over(hexc('#FF7A1F'))
looks = {'sd_red': red, 'sd_off': saturate(brightness(red, 0.5), 0.55), 'sd_boost': boost, 'sd_boostoff': saturate(brightness(boost, 0.5), 0.55), 'sd_grey': grayscale(red)}
for name, img in looks.items():
    out, d = with_shadow(img, 96); save(out, name + '.webp'); print(name, out.shape[1], 'x', out.shape[0], 'shadow px', d)
cream = np.concatenate([radial([(0, '#FFFCF5'), (0.62, '#F3EBDC'), (1, '#D8CCB6')], 0.36, 0.30), As], -1)
out, d = with_shadow(cream, 80); save(out, 'sd_cream.webp'); print('sd_cream', out.shape[1], 'x', out.shape[0], 'shadow px', d)
