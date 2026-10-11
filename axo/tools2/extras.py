# per-vertex extras for the jelly layer, the face and the paint coat, appended to each mesh's .bin:
#   jelly (4 x uint8): x belly (breathing expand), y soft (how much the jelly layer may move it: 0 on the head / gills), z thin (gills, fins), w head weight
#   fill  (2 x uint8): x crawl fill order (paint rises from the ground contacts), y stand fill order (from the feet, hands last)
import sys, json; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from geo import M, D
from rigcore import thin_mask, laplacian_smooth_weights
W_ = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo2/'
def smooth_scalar(m, x, iters=3):
    X = x[:, None].astype(float).copy(); laplacian_smooth_weights(m, X, np.arange(m.n), iters=iters, lam=0.5); return X[:, 0]
for nm in ('stand', 'crawl'):
    meta = json.load(open(W_ + f'axo_{nm}.json')); m = M(nm); r = np.load(D + f'{nm}_rig.npz', allow_pickle=True); names = list(r['names']); labels = np.array([str(x) for x in r['labels']])
    Wd = np.zeros((m.n, len(names)))
    for c in range(4): np.add.at(Wd, (np.arange(m.n), r['idx'][:, c]), r['w'][:, c])
    bi = {k: i for i, k in enumerate(names)}; wsum = lambda ks: sum(Wd[:, bi[k]] for k in ks if k in bi)
    N = m.N; P = m.P; sc = 1.15 if nm == 'crawl' else 1.0; Pe = P * sc + (np.array(meta['bbox'][0]) - P.min(0) * sc)   # exported coordinates
    head = np.clip(wsum(['head', 'headfront']) + wsum([k for k in names if k.startswith('gill')]), 0, 1)
    trunk = np.clip(wsum(['spine', 'spine1', 'chest']) + 0.5 * wsum(['hips']), 0, 1)
    digit = wsum([k for k in names if k.startswith('finger') or (k.startswith('toe') and not k.startswith('toes'))])
    ventral = np.array([0, 0, 1.0]) if nm == 'stand' else np.array([0, -1.0, 0])
    belly = np.clip(trunk * (0.3 + 0.7 * np.clip(N @ ventral, 0, 1) + 0.35 * np.abs(N[:, 0])), 0, 1)
    soft = np.clip(1 - head, 0, 1) * (1 - 0.5 * digit)
    thin = thin_mask(m, np.ones(m.n, bool), r=0.045 if nm == 'stand' else 0.04).astype(float); thin = np.clip(smooth_scalar(m, thin, 2) * 1.3, 0, 1)
    islab = lambda pre: np.array([l.startswith(pre) for l in labels])
    hands = (wsum(['hand.L', 'hand.R']) > 0.3) | islab('finger'); feet = (wsum(['foot.L', 'foot.R', 'toes.L', 'toes.R']) > 0.3) | (islab('toe') & ~islab('toes'))
    if nm == 'stand':
        bellyC = (trunk > 0.4) & (N[:, 2] > 0.3) & (Pe[:, 1] > 0.45) & (Pe[:, 1] < 1.0)
        src = hands | feet | bellyC
        standO = np.clip(Pe[:, 1] / 1.78, 0, 1) + 0.3 * (wsum(['hand.L', 'hand.R', 'forearm.L', 'forearm.R']) > 0.3) + 0.3 * islab('finger') + 0.1 * islab('gill')
    else:
        src = Pe[:, 1] < 0.075
        d = m.geo(np.where(feet)[0], limit=5.0); d[~np.isfinite(d)] = d[np.isfinite(d)].max(); standO = d / d.max() + 0.35 * (hands | (wsum(['forearm.L', 'forearm.R']) > 0.3))
    d = m.geo(np.where(src)[0], limit=5.0); d[~np.isfinite(d)] = d[np.isfinite(d)].max(); crawlO = d / d.max()
    crawlO = smooth_scalar(m, crawlO, 2); standO = smooth_scalar(m, np.clip(standO, 0, 1), 2); standO = standO / standO.max()
    jelly = np.stack([belly, soft, thin, head], 1)[m.wid]; fill = np.stack([crawlO, standO], 1)[m.wid]
    q = lambda a: np.clip(np.round(a * 255), 0, 255).astype(np.uint8)
    buf = bytearray(open(W_ + f'axo_{nm}.bin', 'rb').read()); o = meta['off'][:6]; end = len(buf); end += (-end) % 4; buf = buf[:end] if len(buf) >= end else buf + bytes(end - len(buf))
    o.append(len(buf)); buf += q(jelly).tobytes(); buf += bytes((-len(buf)) % 4); o.append(len(buf)); buf += q(fill).tobytes(); buf += bytes((-len(buf)) % 4)
    open(W_ + f'axo_{nm}.bin', 'wb').write(buf); meta['off'] = o; json.dump(meta, open(W_ + f'axo_{nm}.json', 'w'))
    print(nm, 'bin', len(buf), 'belly>0.5', int((belly > 0.5).sum()), 'thin>0.5', int((thin > 0.5).sum()), 'head>0.5', int((head > 0.5).sum()), 'contact src', int(src.sum()))
