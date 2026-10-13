# Views of the reposed mesh (fable4/work/reposed.npz): textured, and coloured by its remaining mirror gap
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, json
import viewlib as V, repose as rp, symmetrize as sy, meshkit as mk
S = V.S; tag = sys.argv[1] if len(sys.argv) > 1 else 'rep2'
z = np.load(S + '/fable4/work/reposed.npz'); Pt, Tw, wid, UV, T = z['Pw'], z['Tw'], z['wid'], z['UV'], z['T']
Nt = mk.vertex_normals(Pt, Tw); _, d = sy.mirror_partner(Pt, Tw, Nt); d = np.where(np.isfinite(d), d, 0.2); print('gap mean', d.mean().round(4), 'p95', np.percentile(d, 95).round(4))
k = np.clip(d / 0.05, 0, 1); col = np.stack([k, 0.2 + 0 * k, 1 - k], 1)
JT = {kk: np.array(v) for kk, v in json.loads(str(z['JT'])).items()}
L = [np.r_[JT[b], JT[e]] for b, e, _ in rp.REPOSE]; C = [[1, 0, 0] * 2 if '.L' in b else [0, 0, 1] * 2 if '.R' in b else [0, 0.6, 0] * 2 for b, e, _ in rp.REPOSE]
V.write(tag, Pt[wid], Nt[wid], UV, T, col=col[wid], lines=L, lcol=C, tex=S + '/fable4/view/src_tex.jpg')
cells = [('top', V.ortho('top', [0, -0.15], 1.2, 'tex', lines=False)), ('side', V.ortho('side', [-0.15, 0.42], 1.2, 'tex', lines=False)), ('front', V.ortho('front', [0, 0.42], 0.75, 'tex', lines=False)), ('3/4', V.persp([2.2, 1.6, 2.4], [0, 0.3, -0.1], 'tex', lines=False)),
         ('gap top (red 0.05+)', V.ortho('top', [0, -0.15], 1.2, 'col', lines=False)), ('gap front', V.ortho('front', [0, 0.42], 0.75, 'col', lines=False)), ('back', V.ortho('back', [0, 0.42], 0.75, 'tex', lines=False)), ('3/4 back', V.persp([-2.0, 1.4, -2.2], [0, 0.3, -0.1], 'tex', lines=False)),
         ('front skeleton', V.ortho('front', [0, 0.42], 0.75, 'grey')), ('side skeleton', V.ortho('side', [-0.15, 0.42], 1.2, 'grey')), ('low front', V.persp([0.0, 0.25, 2.4], [0, 0.4, 0.2], 'tex', lines=False)), ('above', V.persp([0.0, 3.0, -0.3], [0, 0.2, -0.2], 'tex', lines=False))]
V.shoot(tag, S + f'/fable4/shots/{tag}.jpg', cells, W=560, H=560, ncol=4)
