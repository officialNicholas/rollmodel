# Close views of the built crawl mesh's face (fable4/rt/axo_crawl): textured, grey (shape only), coloured by normal x, and the UV seams,
# to tell a crease in the shape from a seam in the texture.   python3 -I look_face.py [tag]
import sys, os, io; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import viewlib as V, axo7io, meshkit as mk
from PIL import Image
S = V.S; tag = sys.argv[1] if len(sys.argv) > 1 else 'facechk'
d = axo7io.read(S + '/fable4/rt/axo_crawl'); P, N, T, UV = d['P'], d['N'], d['T'], d['uv']
Image.open(io.BytesIO(d['tex'])).convert('RGB').save(S + f'/fable4/view/{tag}_tex.jpg', quality=92)
# seam edges: edges of the split mesh used by one triangle only, where the welded mesh has two (i.e. UV seams)
key = np.round(P * 1e5).astype(np.int64); _, wid = np.unique(key, axis=0, return_inverse=True); wid = wid.ravel()
E = np.sort(np.r_[T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]], 1); Ew = np.sort(wid[E], 1)
u, c = np.unique(E, axis=0, return_counts=True); uw, cw = np.unique(Ew, axis=0, return_counts=True)
bnd = u[c == 1]; bw = np.sort(wid[bnd], 1); cnt = dict(zip(map(tuple, uw), cw)); seam = np.array([b for b, bb in zip(bnd, bw) if cnt[tuple(bb)] >= 2])
L = np.c_[P[seam[:, 0]], P[seam[:, 1]]] if len(seam) else None
nx = N[:, 0]; col = np.stack([0.5 + 2.5 * nx, 0.5 + 0 * nx, 0.5 - 2.5 * nx], 1).clip(0, 1)
V.write(tag, P, N, UV, T, col=col, lines=L, lcol=np.tile([0, 1, 0], (len(L) * 2, 1)) if L is not None else None)
fc = [0.0, 0.78]; h = 0.36
cells = [('front tex', V.ortho('front', fc, h, 'tex', lines=False)), ('front grey', V.ortho('front', fc, h, 'grey', lines=False)), ('front normal x (red +x)', V.ortho('front', fc, h, 'col', lines=False)),
         ('front tex + uv seams', V.ortho('front', fc, h, 'tex', lines=True)), ('wire', V.ortho('front', fc, h, 'wire', lines=False)), ('from above-front, tex', V.persp([0.2, 1.6, 1.9], [0, 0.75, 0.3], 'tex', lines=False))]
V.shoot(tag, S + f'/fable4/shots/{tag}.jpg', cells, W=560, H=560, ncol=3, tex=f'{tag}_tex.jpg')
