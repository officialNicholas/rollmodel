# colour-correct the rigged stand texture so the character matches the unrigged stand sculpt (same character, plain base-colour material like the crawl):
# area-weighted samples of both surfaces -> per-channel quantile matching in linear light, applied as a 3 x 256 LUT to the texture
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from PIL import Image
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def srgb(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
def surface_samples(npz, texpng, n=400000, seed=1):
    m = np.load(npz, allow_pickle=True); P, UV, I = m['P'], m['UV'], m['I'].reshape(-1, 3)
    a = np.asarray(Image.open(texpng).convert('RGB')).astype(np.float32) / 255; h, w = a.shape[:2]
    area = 0.5 * np.linalg.norm(np.cross(P[I[:, 1]] - P[I[:, 0]], P[I[:, 2]] - P[I[:, 0]]), axis=1); rng = np.random.default_rng(seed)
    tri = rng.choice(len(I), n, p=area / area.sum()); r1, r2 = rng.random(n), rng.random(n); s1 = np.sqrt(r1); b = np.c_[1 - s1, s1 * (1 - r2), s1 * r2]
    uv = (UV[I[tri]] * b[:, :, None]).sum(1); px = np.clip((uv[:, 0] * (w - 1)).round().astype(int), 0, w - 1); py = np.clip((uv[:, 1] * (h - 1)).round().astype(int), 0, h - 1)
    return a[py, px]
A = surface_samples(D + 'stand_src.npz', D + 'stand_tex.png'); B = surface_samples(D + 'standu_src.npz', D + 'standu_tex.png'); C = surface_samples(D + 'crawl_src.npz', D + 'crawl_tex.png')
print('surface mean colour  rigged', A.mean(0).round(3), ' unrigged', B.mean(0).round(3), ' crawl', C.mean(0).round(3))
qs = np.linspace(0, 1, 513); lut = np.zeros((3, 256))
for ch in range(3):
    qa = np.quantile(lin(A[:, ch]), qs); qb = np.quantile(lin(B[:, ch]), qs)
    x = lin(np.arange(256) / 255); lut[ch] = srgb(np.interp(x, qa, qb)) * 255
np.save(D + 'lut.npy', lut)
print('lut samples (in->out, sRGB 0-255):'); [print(' ch', ch, [(v, int(round(lut[ch][v]))) for v in (60, 100, 128, 160, 190, 220, 250)]) for ch in range(3)]
im = np.asarray(Image.open(D + 'stand_tex.png').convert('RGB')); out = np.stack([np.clip(lut[ch][im[:, :, ch]], 0, 255) for ch in range(3)], -1).astype(np.uint8)
Image.fromarray(out).save(D + 'stand_tex_cc.png')
A2 = surface_samples(D + 'stand_src.npz', D + 'stand_tex_cc.png'); print('corrected rigged surface mean', A2.mean(0).round(3), 'p10/p90 per channel', np.percentile(A2, [10, 90], axis=0).round(3).tolist(), 'unrigged', np.percentile(B, [10, 90], axis=0).round(3).tolist())
