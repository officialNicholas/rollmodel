# The model's baked base colour for the game: Meshy's 4096 atlas recoloured into the runtime's native pink (the look shader turns the
# texel's chroma along the native pink's direction to each team's hue: a texel off that direction keeps its own hue under every team, so
# the model's magenta would tint unevenly), the empty space between the atlas charts filled outward from the charts (no dark rims where a
# mip level blends a chart's edge with the black gap), scaled down and encoded as WebP.
#   python3 -I texture.py <in.png> <out.webp> [res 2048] [quality 82]
import sys
import numpy as np
from PIL import Image, ImageDraw
def srgb2lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def lin2srgb(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)
NATIVE = np.array([0.98, 0.60, 0.66])     # (look10: NATIVE_SKIN, sRGB)
def native_dir():
    c = srgb2lin(NATIVE); Y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; d = np.array([c[0] - Y, c[2] - Y]); return d / np.linalg.norm(d)
def recolor(rgb, keep=0.0, ygamma=1.0, cscale=1.0):
    """each texel's chroma (r - Y, b - Y in linear light) turned onto the native pink's direction, its length and its luminance kept
    (keep: the share of its own hue left)"""
    c = srgb2lin(rgb); Y = c @ np.array([0.2126, 0.7152, 0.0722]); ch = np.stack([c[..., 0] - Y, c[..., 2] - Y], -1)
    d0 = native_dir(); mag = np.linalg.norm(ch, axis=-1); a = ch @ d0; sgn = np.where(a >= 0, 1.0, -1.0)
    ch2 = ((1 - keep) * (sgn * mag)[..., None] * d0 + keep * ch) * cscale
    Y = np.power(np.clip(Y, 0, 1), ygamma)   # (the model's darker baked skin lifted toward the runtime's native pink, its light and dark kept in order)
    r = Y + ch2[..., 0]; b = Y + ch2[..., 1]; g = (Y - 0.2126 * r - 0.0722 * b) / 0.7152
    out = np.stack([r, g, b], -1)
    # (out of gamut: pulled toward the grey of the same luminance until it fits)
    lo = out.min(-1); k = np.where(lo < 0, Y / np.maximum(Y - lo, 1e-9), 1.0)[..., None]; out = Y[..., None] + (out - Y[..., None]) * k
    hi = out.max(-1); k = np.where(hi > 1, (1 - Y) / np.maximum(hi - Y, 1e-9), 1.0)[..., None]; out = Y[..., None] + (out - Y[..., None]) * k
    return lin2srgb(out)
def chart_mask(UV, T, res):
    im = Image.new('L', (res, res), 0); dr = ImageDraw.Draw(im)
    for tri in T:
        pts = [(float(UV[v, 0] * res), float(UV[v, 1] * res)) for v in tri]; dr.polygon(pts, fill=255, outline=255)
    return np.asarray(im) > 0
def fill_gaps(img, mask):
    """push-pull: the empty texels take the average of the chart texels around them, coarse to fine"""
    levels = [(img * mask[..., None], mask.astype(float))]
    while levels[-1][1].shape[0] > 4:
        c, w = levels[-1]; h = c.shape[0] // 2
        c2 = c[:2 * h, :2 * h].reshape(h, 2, h, 2, 3).sum((1, 3)); w2 = w[:2 * h, :2 * h].reshape(h, 2, h, 2).sum((1, 3)); levels.append((c2, w2))
    c, w = levels[-1]; col = c / np.maximum(w, 1e-9)[..., None]
    for c, w in reversed(levels[:-1]):
        up = np.repeat(np.repeat(col, 2, 0), 2, 1)[:c.shape[0], :c.shape[1]]; own = c / np.maximum(w, 1e-9)[..., None]; k = np.clip(w, 0, 1)[..., None]
        col = own * k + up * (1 - k)
    return col
def build(src_png, UV, T, res=2048, quality=82, keep=0.0, ygamma=1.0, cscale=1.0):
    """the gaps between the charts filled at the atlas's own size first (so no chart texel, however thin the chart, mixes with the gap
    when it is scaled down), then scaled down by area and recoloured"""
    im = Image.open(src_png).convert('RGB'); big = im.size[0]
    src = np.asarray(im).astype(np.float32) / 255
    mb = chart_mask(UV, T, big)
    # (each gap texel takes its nearest chart texel's colour: next to a chart, the gap is that chart's own edge, so its border texels
    # stay its colour in the downscale and under bilinear filtering; a blur of the neighbours there would bring in other charts' colours)
    from scipy.ndimage import distance_transform_edt
    _, (iy, ix) = distance_transform_edt(~mb, return_indices=True)
    src = src[iy, ix]; del iy, ix
    k = big // res
    rgb = src[:res * k, :res * k].reshape(res, k, res, k, 3).mean((1, 3)).astype(np.float64) if k > 1 else src.astype(np.float64)
    m = chart_mask(UV, T, res)
    # (further out, where no sample reaches, the gap smoothed over instead (push-pull): it only feeds the small mip levels, and compresses)
    from scipy.ndimage import binary_dilation
    rgb = fill_gaps(rgb, binary_dilation(m, iterations=3))
    rgb = recolor(rgb, keep, ygamma, cscale)
    return Image.fromarray(np.clip(np.round(rgb * 255), 0, 255).astype(np.uint8)), m
if __name__ == '__main__':
    pass
