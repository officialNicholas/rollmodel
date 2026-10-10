import numpy as np, sys
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/'
for nm in ('stand', 'crawl'):
    m = np.load(D + nm + '_mesh.npz'); P, I = m['P'], m['I'].reshape(-1, 3)
    # weld by position (Meshy splits UV seams)
    key = np.round(P, 5); _, wid = np.unique(key, axis=0, return_inverse=True); wid = wid.ravel()
    T = wid[I]; e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); n = wid.max() + 1
    A = coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)); nc, lab = connected_components(A, directed=False)
    vl = lab[wid]; sizes = np.bincount(vl)
    print('==', nm, 'welded', n, 'of', len(P), 'components', nc)
    for c in np.argsort(-sizes)[:14]:
        q = P[vl == c]; print(f'  comp {c} verts {sizes[c]} min {q.min(0).round(2)} max {q.max(0).round(2)}')
