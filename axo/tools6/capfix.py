# The old gill stalks' caps repainted skin (v10). v9b retired the six stalks by collapsing each into a cap on the skull (its base ring and
# a centre), and their texels kept the sculpt's own red gill-root shading, which headtex.py left alone ("their colour belongs to the
# stalks"). With the slime's ears over them those reds peeked out beside the ear roots. Each cap's texels (the triangles on the cap verts
# slimehead.py lists) take the mean colour of the plain head texels in a ring 10 to 25 cm round the cap, with a tenth of their own detail.
# Reads the slimehead meshes (fable3/rt4) and the atlas they carry (the PNG headtex.py wrote, fable2/rt3/axo_{nm}_tex.png), rewrites the
# meshes with the repainted texture inside and the PNG beside them:
#   python3 -I capfix.py [--src S/fable3/rt4] [--tex S/fable2/rt3] [--out S/fable3/rt4]
import sys, os, json
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import binary_dilation
from PIL import Image
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
WORK = S + '/fable3'
sys.path.insert(0, '/home/user/rollmodel/axo/tools4')
import texbake as tb
def lin(x): return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
def srgb(x): x = np.clip(x, 0, 1); return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)
def fix(nm, src, texdir, out, verbose=True):
    meta = json.load(open(f'{src}/axo_{nm}.json')); b = bytearray(open(f'{src}/axo_{nm}.bin', 'rb').read()); o = meta['off7']; n = meta['n']
    caps = json.load(open(f'{src}/axo_{nm}_caps.json')); cv = np.zeros(n, bool); cv[caps['cap_verts']] = True; nb = caps['n_body']
    P = np.frombuffer(bytes(b), np.float32, n * 3, o['position']).reshape(n, 3).astype(float)
    T = np.frombuffer(bytes(b), np.uint16, meta['ni'], o['index']).reshape(-1, 3).astype(np.int64)
    uv = np.frombuffer(bytes(b), np.uint16, n * 2, o['uv']).reshape(n, 2).astype(float) / 65535
    si = np.frombuffer(bytes(b), np.uint8, n * 4, o['skinIndex']).reshape(n, 4); sw = np.frombuffer(bytes(b), np.uint8, n * 4, o['skinWeight']).reshape(n, 4)
    names = [x['name'] for x in meta['bones']]; W = np.zeros((n, len(names)))
    for c in range(4): np.add.at(W, (np.arange(n), si[:, c].astype(int)), sw[:, c] / 255)
    bi = {k: i for i, k in enumerate(names)}; hw = W[:, bi['head']] + W[:, bi['headfront']]
    body = np.arange(n) < nb; span = np.max(np.max(uv[T], 1) - np.min(uv[T], 1), 1); small = span < 0.05   # (never a triangle straddling the atlas)
    capT = cv[T].any(1) & body[T].all(1) & small; headT = (hw[T] > 0.5).all(1) & ~cv[T].any(1) & body[T].all(1) & small
    res = meta['texRes']; img = tb.load_tex(f'{texdir}/axo_{nm}_tex.png', fill_gutters=False); assert img.shape[0] == res
    ty, tx, tt, tb_ = tb.rasterize(uv, T, res, capT); hy, hx, ht, hb_ = tb.rasterize(uv, T, res, headT)
    qc = (P[T[tt]] * tb_[:, :, None]).sum(1); qh = (P[T[ht]] * hb_[:, :, None]).sum(1); colh = lin(img[hy, hx].astype(np.float64)); colc = lin(img[ty, tx].astype(np.float64))
    kd = cKDTree(qh); new = colc.copy()
    # per hole (its texels are those nearest its centre): the plain head texels in a ring 10 to 25 cm round it
    cen = P[caps['centres']]
    if len(qc) and len(cen):
        _, labels = cKDTree(cen).query(qc)
        for k in range(len(cen)):
            m = labels == k
            if not m.any(): continue
            c = cen[k]; near = kd.query_ball_point(c, 0.25); near = [j for j in near if np.linalg.norm(qh[j] - c) > 0.1]
            target = colh[near].mean(0) if len(near) > 50 else colh.mean(0)
            new[m] = target[None, :] + (colc[m] - colc[m].mean(0)) * 0.1
    img2 = img.copy(); img2[ty, tx] = srgb(new).astype(np.float32)
    cov = np.zeros((res, res), np.float32); cov[ty, tx] = 1; cov[hy, hx] = 1
    ring = binary_dilation(cov > 0, iterations=6) & (cov == 0); fill = tb.dilate(img2, cov, rounds=8); img2[ring] = fill[ring]
    os.makedirs(out, exist_ok=True); Image.fromarray(np.clip(np.round(img2 * 255), 0, 255).astype(np.uint8)).save(f'{out}/axo_{nm}_tex.png')
    tbytes = tb.encode(img2); open(f'{out}/axo_{nm}_tex.webp', 'wb').write(tbytes)
    assert o['tex'] + meta['texLen'] <= len(b) and max(v for k2, v in o.items() if k2 != 'tex') < o['tex']
    b2 = bytes(b[:o['tex']]) + tbytes; b2 += b'\0' * ((-len(b2)) % 4)
    meta2 = dict(meta); meta2['texLen'] = len(tbytes)
    open(f'{out}/axo_{nm}.bin', 'wb').write(b2); json.dump(meta2, open(f'{out}/axo_{nm}.json', 'w'))
    if verbose: print(f'{nm}: {int(capT.sum())} cap triangles, {len(ty)} texels repainted from {len(hy)} head texels; {out}/axo_{nm}.bin {len(b2)} bytes (texture {len(tbytes) // 1024} KB)')
if __name__ == '__main__':
    a = sys.argv[1:]; src = WORK + '/rt4'; texdir = S + '/fable2/rt3'; out = WORK + '/rt4'
    while a:
        k = a.pop(0)
        if k == '--src': src = a.pop(0)
        elif k == '--tex': texdir = a.pop(0)
        elif k == '--out': out = a.pop(0)
    for nm in ('stand', 'crawl'): fix(nm, src, texdir, out)
