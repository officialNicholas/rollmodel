# The head's texture evened out (v9). Turning the gill strip forward squeezes the skin ahead of it and stretches the skin behind, and
# the sculpt's own shading round its gill roots (a darker, redder band baked into the atlas) gets squeezed into a stripe down the side
# of the head. Here the head's texels lose their mid-scale structure: each texel's colour is taken relative to a local mean over the
# head's surface (a Gaussian a few cm wide, computed in 3D on the reshaped head so it follows the squeeze), and that mean is replaced by
# a much broader one (20 cm), so the pores and the mottling (under 2 cm) and the head's overall gradient stay while bands a hand wide go.
# Reads the reshaped textured meshes and the atlases they carry, rewrites the atlas and the mesh with the new texture bytes inside:
#   python3 -I headtex.py [--src S/fable2/rt3] [--tex S/fable/rt2] [--out S/fable2/rt3] [--sigma 0.05] [--wide 0.2]
# (the atlas PNGs come from the bake folder: axo_{stand,crawl}_tex.png there are what the bins carry, WebP-encoded)
import sys, os, json, io
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
WORK = S + '/fable2'
sys.path.insert(0, '/home/user/rollmodel/axo/tools4')
import texbake as tb
def lin(x): return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
def srgb(x): x = np.clip(x, 0, 1); return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def even(nm, src, texdir, out, sigma=0.05, wide=0.2, verbose=True):
    meta = json.load(open(f'{src}/axo_{nm}.json')); b = bytearray(open(f'{src}/axo_{nm}.bin', 'rb').read()); o = meta['off7']; n = meta['n']
    P = np.frombuffer(bytes(b), np.float32, n * 3, o['position']).reshape(n, 3).astype(float)
    T = np.frombuffer(bytes(b), np.uint16, meta['ni'], o['index']).reshape(-1, 3).astype(np.int64)
    uv = np.frombuffer(bytes(b), np.uint16, n * 2, o['uv']).reshape(n, 2).astype(float) / 65535
    si = np.frombuffer(bytes(b), np.uint8, n * 4, o['skinIndex']).reshape(n, 4); sw = np.frombuffer(bytes(b), np.uint8, n * 4, o['skinWeight']).reshape(n, 4)
    names = [x['name'] for x in meta['bones']]; W = np.zeros((n, len(names)))
    for c in range(4): np.add.at(W, (np.arange(n), si[:, c].astype(int)), sw[:, c] / 255)
    bi = {k: i for i, k in enumerate(names)}; hw = W[:, bi['head']] + W[:, bi['headfront']]; gw = W[:, [i for i, k in enumerate(names) if k.startswith('gill')]].sum(1)
    C = np.array(meta['face']['c'], float)
    # the head's texels: triangles whose corners all carry the head (the base rings of the gills left out: their colour belongs to the stalks)
    head_v = (hw > 0.3) & (gw < 0.05); keep = head_v[T].all(1)
    res = meta['texRes']; img = tb.load_tex(f'{texdir}/axo_{nm}_tex.png', fill_gutters=False); assert img.shape[0] == res
    ty, tx, tt, tb_ = tb.rasterize(uv, T, res, keep)
    V = T[tt]; q = (P[V] * tb_[:, :, None]).sum(1); wq = (hw[V] * tb_).sum(1)   # the texel's point on the head and its head weight
    col = lin(img[ty, tx].astype(np.float64))
    # local means on a 1 cm voxel grid of the texel points (blurred sums over blurred counts), at two widths
    lo = q.min(0) - 4 * wide; cell = 0.01; dims = np.ceil((q.max(0) + 4 * wide - lo) / cell).astype(int) + 1
    idx = np.floor((q - lo) / cell).astype(int); flat = np.ravel_multi_index(idx.T, dims)
    cnt = np.bincount(flat, minlength=int(np.prod(dims))).reshape(dims).astype(np.float64)
    acc = np.stack([np.bincount(flat, weights=col[:, k], minlength=int(np.prod(dims))).reshape(dims) for k in range(3)], -1)
    def local_mean(sig):
        cs = gaussian_filter(cnt, sig / cell, mode='constant'); out = np.stack([gaussian_filter(acc[:, :, :, k], sig / cell, mode='constant') for k in range(3)], -1)
        return out[idx[:, 0], idx[:, 1], idx[:, 2]] / np.maximum(cs[idx[:, 0], idx[:, 1], idx[:, 2]], 1e-9)[:, None]
    m_near = local_mean(sigma); m_wide = local_mean(wide)
    k = ss((wq - 0.3) / 0.5)[:, None]   # (fades out toward the neck, where the head weight fades)
    new = col + (m_wide - m_near) * k
    # round the gill roots the sculpt's own root shading (a saturated red patch) goes almost entirely: the broad mean with a little detail
    roots = np.array([b['pos'] for b in meta['bones'] if b['name'].startswith('gill') and b['name'].endswith('.1')])
    dr = np.min(np.linalg.norm(q[:, None, :] - roots[None, :, :], axis=2), axis=1); kr = (1.0 - ss((dr - 0.12) / 0.07))[:, None] * k
    # (the colour of the skin round the patch, from an annulus 16 to 26 cm out, takes the patch's place, with a tenth of its own detail)
    ann = (dr > 0.16) & (dr < 0.26) & (wq > 0.8); target = col[ann].mean(0) if ann.sum() > 100 else m_wide.mean(0)
    new = new + kr * ((target[None, :] + (col - m_near) * 0.1) - new)
    if verbose:
        d = np.abs(m_near - m_wide).max(1); print(f'{nm}: {len(ty)} head texels; band removed: mean {d.mean() * 100:.1f}% of linear, p99 {np.percentile(d, 99) * 100:.1f}%, max {d.max() * 100:.1f}%')
    img2 = img.copy(); img2[ty, tx] = srgb(new).astype(np.float32)
    # the gutters round the head's charts refilled from the new colours (bilinear taps and mipmaps near chart borders)
    cov = np.zeros((res, res), np.float32); cov[ty, tx] = 1
    from scipy.ndimage import binary_dilation
    ring = binary_dilation(cov > 0, iterations=6) & (cov == 0)
    fill = tb.dilate(img2, cov, rounds=8); img2[ring] = fill[ring]
    os.makedirs(out, exist_ok=True)
    Image.fromarray(np.clip(np.round(img2 * 255), 0, 255).astype(np.uint8)).save(f'{out}/axo_{nm}_tex.png')
    tbytes = tb.encode(img2); open(f'{out}/axo_{nm}_tex.webp', 'wb').write(tbytes)
    # the mesh with the new texture bytes (the tex section is the last one)
    assert o['tex'] + meta['texLen'] <= len(b) and max(v for k2, v in o.items() if k2 != 'tex') < o['tex']
    b2 = bytes(b[:o['tex']]) + tbytes; b2 += b'\0' * ((-len(b2)) % 4)
    meta2 = dict(meta); meta2['texLen'] = len(tbytes)
    open(f'{out}/axo_{nm}.bin', 'wb').write(b2); json.dump(meta2, open(f'{out}/axo_{nm}.json', 'w'))
    if verbose: print(f'  {out}/axo_{nm}.bin {len(b2)} bytes (texture {len(tbytes) // 1024} KB, was {meta["texLen"] // 1024} KB)')
if __name__ == '__main__':
    a = sys.argv[1:]; src = WORK + '/rt3'; texdir = S + '/fable/rt2'; out = WORK + '/rt3'; sigma = 0.05; wide = 0.2
    while a:
        k = a.pop(0)
        if k == '--src': src = a.pop(0)
        elif k == '--tex': texdir = a.pop(0)
        elif k == '--out': out = a.pop(0)
        elif k == '--sigma': sigma = float(a.pop(0))
        elif k == '--wide': wide = float(a.pop(0))
    for nm in ('stand', 'crawl'): even(nm, src, texdir, out, sigma, wide)
