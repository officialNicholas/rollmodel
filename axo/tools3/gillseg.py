# segment the stand's gill stalks geometrically: the skull core (close to the face centre), the geodesic distance out from it, the protruding
# pieces per side; prints the components and writes a debug colouring
import numpy as np, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
def load():
    s = np.load(O + 'stand7_rig.npz', allow_pickle=True); m = json.load(open(O + 'www/s7/axo_stand.json'))
    names = [b['name'] for b in m['bones']]; P = s['P']; T = s['T']; C = np.array(m['face']['c'])
    W = np.zeros((len(P), len(names)))
    for k in range(4): np.add.at(W, (np.arange(len(P)), s['idx'][:, k].astype(int)), s['w'][:, k])
    return s, m, names, P, T, C, W
def graph(P, T, mask=None):
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = np.unique(np.sort(e, 1), axis=0)
    if mask is not None: e = e[mask[e[:, 0]] & mask[e[:, 1]]]
    L = np.linalg.norm(P[e[:, 0]] - P[e[:, 1]], axis=1); n = len(P)
    return coo_matrix((np.r_[L, L], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr()
def segment(R0=0.40, OUT=0.03, verbose=True):
    s, m, names, P, T, C, W = load(); bi = {k: i for i, k in enumerate(names)}
    gb = [bi[k] for k in names if k.startswith('gill')]; headish = (W[:, bi['head']] + W[:, gb].sum(1)) > 0.5
    r = np.linalg.norm(P - C, axis=1); core = headish & (r < R0)
    G = graph(P, T, headish); d = dijkstra(G, indices=np.where(core)[0], min_only=True)
    prot = headish & (d > OUT) & np.isfinite(d)
    ncomp, lab = connected_components(graph(P, T, prot), directed=False); lab = np.where(prot, lab, -1)
    ids, cnt = np.unique(lab[lab >= 0], return_counts=True)
    comps = [(k, c) for k, c in zip(ids, cnt) if c >= 30]
    if verbose:
        for k, c in sorted(comps, key=lambda x: -x[1]):
            v = lab == k; q = P[v] - C
            print(f'  comp {k}: {c} verts, side {np.sign(q[:, 0].mean()):+.0f}, centroid {P[v].mean(0).round(3)}, r {r[v].min():.2f}..{r[v].max():.2f}, geo {d[v].max():.2f}')
    return dict(P=P, T=T, C=C, W=W, names=names, d=d, lab=lab, comps=comps, core=core, headish=headish)
if __name__ == '__main__':
    R0 = float(sys.argv[1]) if len(sys.argv) > 1 else 0.40; OUT = float(sys.argv[2]) if len(sys.argv) > 2 else 0.03
    z = segment(R0, OUT)
    col = np.tile(np.array([235, 200, 205], np.uint8), (len(z['P']), 1)); pal = [(230, 60, 60), (60, 170, 60), (60, 90, 230), (250, 160, 60), (150, 80, 200), (60, 200, 200), (200, 200, 60)]
    for j, (k, c) in enumerate(sorted(z['comps'], key=lambda x: -x[1])): col[z['lab'] == k] = pal[j % len(pal)]
    col[z['core']] = (180, 180, 180); col.tofile(O + 'www/dbg/stand_g.col')
