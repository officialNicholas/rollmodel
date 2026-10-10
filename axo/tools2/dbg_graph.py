import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from geo import M
from scipy.sparse.csgraph import dijkstra, connected_components
m = M('stand')
nc, lab = connected_components(m.G, directed=False); print('components', nc, 'sizes', np.bincount(lab))
for c in range(nc): print('  comp', c, 'bbox', m.P[lab == c].min(0).round(2), m.P[lab == c].max(0).round(2))
src = m.near([0.493, 0.741, 0.79]); d = dijkstra(m.G, indices=src)
eu = np.linalg.norm(m.P - m.P[src], axis=1); fin = np.isfinite(d) & (eu > 0.02)
r = d[fin] / eu[fin]; print('geo/euclid overall p50 p90', np.percentile(r, [50, 90]).round(2))
hand = fin & (np.linalg.norm(m.P - [0.5, 0.63, 0.81], axis=1) < 0.2); print('hand ratio p50 p90', np.percentile(d[hand] / eu[hand], [50, 90]).round(2))
# vertex degrees in the hand
deg = np.diff(m.G.indptr); print('degree hist overall', np.bincount(deg)[:12], 'hand', np.bincount(deg[hand])[:12])
# triangle quality in the hand: edge length distribution
E = m.E; eh = E[hand[E[:, 0]] & hand[E[:, 1]]]; el = np.linalg.norm(m.P[eh[:, 0]] - m.P[eh[:, 1]], axis=1); print('hand edge len p50 p90 max', np.percentile(el, [50, 90, 100]).round(4), 'n', len(eh))
# compare: does the ORIGINAL (unwelded) index buffer give the same? check how many triangles have 3 distinct welded ids
T = m.T; print('degenerate tris', int(((T[:, 0] == T[:, 1]) | (T[:, 1] == T[:, 2]) | (T[:, 0] == T[:, 2])).sum()), 'of', len(T))
# boundary edges (edges with only one adjacent triangle): a closed mesh has none
from collections import Counter
cnt = Counter(tuple(sorted(e)) for t in T for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])))
bd = sum(1 for v in cnt.values() if v == 1); print('boundary edges', bd, 'of', len(cnt), 'non-manifold', sum(1 for v in cnt.values() if v > 2))
# path from src to the farthest hand vertex
far = np.where(hand)[0][np.argmax(d[hand])]; print('farthest hand vertex', m.P[far].round(3), 'geo', d[far].round(3), 'euclid', eu[far].round(3))
dd, pred = dijkstra(m.G, indices=src, return_predecessors=True); path = []; v = far
while v != src and v >= 0: path.append(v); v = pred[v]
print('path len', len(path)); print(np.array([m.P[v].round(2) for v in path[::max(1, len(path) // 12)]]))
