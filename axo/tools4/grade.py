# The stand's baked texture (from the paler rigged biped) graded to the crawl's palette (the user's crawl sculpt, the look the game is
# after), so the two bodies agree through the morph: a class-wise colour transfer. Each covered texel is softly sorted into the skin's pink,
# the belly's white and the fin's blue by its chroma; per class the stand's mean and spread (linear RGB) are moved onto the crawl's, and
# the texel takes the blend of its classes' transforms. The crawl atlas is the reference, so the statistics are surface-weighted alike.
# Rewrites <dir>/axo_stand_tex.{png,webp} and re-exports <dir>/axo_stand.bin/.json with the graded texture inside.
#   python3 -I grade.py [bake dir = S/look/rt1] [the meshes the bake textured = ws/axo]
# (the second argument is the bake's INPUT mesh folder, never its output: the exported bin is rebuilt from the untextured mesh)
import sys, os, json
import numpy as np
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import texbake as tb
def lin(x): return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
def srgb(x): x = np.clip(x, 0, 1); return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)
def classes(c):
    """soft weights (pink skin, white, blue) from a texel's linear colour"""
    Y = c @ np.array([0.2126, 0.7152, 0.0722]); cr = c[:, 0] - Y; cb = c[:, 2] - Y
    pink = np.clip((cr - 0.04) / 0.12, 0, 1); blue = np.clip((cb - 0.02) / 0.1, 0, 1)
    pink *= 1 - blue; white = np.clip(1 - pink - blue, 0, 1)
    return np.stack([pink, white, blue], 1)
def stats(c, w):
    out = []
    for k in range(w.shape[1]):
        wk = w[:, k:k + 1]; m = (c * wk).sum(0) / max(wk.sum(), 1e-6); sd = np.sqrt(((c - m) ** 2 * wk).sum(0) / max(wk.sum(), 1e-6)); out.append((m, sd, wk.sum()))
    return out
def grade(src_img, src_cov, ref_img, ref_cov, keep_spread=0.85):
    s = lin(src_img[src_cov > 0].reshape(-1, 3)); r = lin(ref_img[ref_cov > 0].reshape(-1, 3))
    ws = classes(s); wr = classes(r); st = stats(s, ws); rt = stats(r, wr)
    for k, nm in enumerate(('pink', 'white', 'blue')): print(f'  {nm:5s}: stand mean {srgb(st[k][0]).round(3)} sd {st[k][1].round(3)} ({st[k][2] / len(s) * 100:.0f}%)  ->  crawl mean {srgb(rt[k][0]).round(3)} sd {rt[k][1].round(3)} ({rt[k][2] / len(r) * 100:.0f}%)')
    out = np.zeros_like(s)
    for k in range(3):
        m0, sd0, _ = st[k]; m1, sd1, _ = rt[k]; g = np.clip(sd1 / np.maximum(sd0, 1e-4), 0.6, 1.8) ** keep_spread
        out += ws[:, k:k + 1] * (m1 + (s - m0) * g)
    img = src_img.copy(); img[src_cov > 0] = srgb(out).astype(np.float32); return img
if __name__ == '__main__':
    d = sys.argv[1] if len(sys.argv) > 1 else S + '/look/rt1'
    ref = tb.load_tex(d + '/axo_crawl_tex.png'); zr = np.load(d + '/bake_crawl.npz'); zs = np.load(d + '/bake_stand.npz')
    src = tb.load_tex(d + '/axo_stand_tex_raw.png')   # (the bake's own output, before any grade)
    img = grade(src, zs['cov'], ref, zr['cov'])
    img = tb.dilate(img, zs['cov'])
    Image.fromarray(np.clip(np.round(img * 255), 0, 255).astype(np.uint8)).save(d + '/axo_stand_tex.png')
    tbytes = tb.encode(img); open(d + '/axo_stand_tex.webp', 'wb').write(tbytes)
    r = tb.load_rt('stand', d=sys.argv[2] if len(sys.argv) > 2 else tb.RT); B = dict(r=r, vm=zs['vm'], T2=zs['T2'], uv=zs['uv'], img=img)
    tb.export('stand', B, d + '/axo_stand', tbytes)
