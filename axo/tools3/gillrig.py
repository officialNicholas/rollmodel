# The stand's gills re-rigged (v7): in the v6 / stand7 rig the gill bones sat at the far ends of the stalks and held only some of the frond
# lobes (with weights crossing from one stalk to the next), the rods themselves rigid with the head; so the gills could neither sway as a
# whole nor fold back (the ground pound), and strong gill motion tore the lobes into shards.
# Here each stalk is found from the geometry: the pieces sticking out of the skull (geodesic distance from the skull core, gillseg.py), the
# fused top / middle pair split by its two far tips, every vertex given to the stalk whose axis (root -> tip) is nearest. Joints: .1 at the
# root on the skull, .2 at 45 % of the stalk, the end at the tip; weights head -> .1 -> .2 smoothly along the stalk. Left side, mirrored.
# Writes stand8_rig.npz and www/s8/axo_stand.json (headgraft.py then copies these gills onto the crawl).
import sys, json, os
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from scipy.sparse.csgraph import dijkstra
from gillseg import segment, graph, O
from mesh import mirror_map
def ss(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def unit(v): return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def qmat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
def mat2quat(M):
    t = np.trace(M)
    if t > 0: s = np.sqrt(t + 1) * 2; return np.array([(M[2, 1] - M[1, 2]) / s, (M[0, 2] - M[2, 0]) / s, (M[1, 0] - M[0, 1]) / s, 0.25 * s])
    i = int(np.argmax(np.diag(M)))
    if i == 0: s = np.sqrt(1 + M[0, 0] - M[1, 1] - M[2, 2]) * 2; return np.array([0.25 * s, (M[0, 1] + M[1, 0]) / s, (M[0, 2] + M[2, 0]) / s, (M[2, 1] - M[1, 2]) / s])
    if i == 1: s = np.sqrt(1 + M[1, 1] - M[0, 0] - M[2, 2]) * 2; return np.array([(M[0, 1] + M[1, 0]) / s, 0.25 * s, (M[1, 2] + M[2, 1]) / s, (M[0, 2] - M[2, 0]) / s])
    s = np.sqrt(1 + M[2, 2] - M[0, 0] - M[1, 1]) * 2; return np.array([(M[0, 2] + M[2, 0]) / s, (M[1, 2] + M[2, 1]) / s, 0.25 * s, (M[1, 0] - M[0, 1]) / s])
def seg_dist(X, a, b):
    """distance of points X to the segment a-b, and the parameter along it (unclamped)"""
    ab = b - a; t = ((X - a) @ ab) / (ab @ ab); tc = np.clip(t, 0, 1); return np.linalg.norm(X - (a + tc[:, None] * ab), axis=1), t
def main():
    z = segment(0.38, 0.03, verbose=False); P, T, C, W, names, d, lab = z['P'], z['T'], z['C'], z['W'], z['names'], z['d'], z['lab']
    bi = {k: i for i, k in enumerate(names)}; meta = json.load(open(O + 'www/s7/axo_stand.json')); B = {b['name']: b for b in meta['bones']}
    comps = [k for k, c in z['comps'] if P[lab == k][:, 0].mean() > 0]   # the left side's pieces
    G = graph(P, T, z['headish'])
    rods = []   # (root, tip, vertex mask)
    sizes = sorted([(lab == k).sum() for k in comps], reverse=True)
    for k in comps:
        v = np.where(lab == k)[0]; dv = d[v]
        base = v[dv < np.percentile(dv, 6)]; root = P[base].mean(0)
        t1 = v[np.argmax(dv)]
        # the big piece holds two stalks fused at the base (top and middle), the small one the bottom stalk
        if len(v) == sizes[0]:
            g1 = dijkstra(G, indices=t1)[v]; far = dv > 0.35 * dv.max(); cand = v[far]; t2 = cand[np.argmax(g1[far])]; tips = [t1, t2]
        else: tips = [t1]
        if len(tips) == 1: rods.append([root, P[t1], v]); continue
        # two stalks from one base: each vertex to the nearer axis
        dd = np.stack([seg_dist(P[v], root, P[t])[0] for t in tips], 1); own = np.argmin(dd, 1)
        for j, t in enumerate(tips):
            vj = v[own == j]; bj = vj[d[vj] < np.percentile(d[vj], 8)]; rj = P[bj].mean(0) if len(bj) else root
            rods.append([rj, P[t], vj])
    print(f'{len(rods)} stalks (left):', [(np.round(r[0], 3).tolist(), np.round(r[1], 3).tolist(), len(r[2])) for r in rods])
    assert len(rods) == 3, 'expected three stalks a side'
    # name them top to bottom by their roots' height: gill0 the top stalk, gill1 the middle, gill2 the bottom (the animator's convention)
    hy = [r[0][1] for r in rods]; order = {k: int(j) for k, j in enumerate(np.argsort(hy)[::-1])}
    print('stalk -> rod', order)
    # weights along each stalk: head -> .1 over the first 15 %, .1 -> .2 around 45 %
    Wn = W.copy(); gb = [bi[n] for n in names if n.startswith('gill')]
    side = P[:, 0] > 1e-6
    # vertices to re-weight: the stalk pieces, and their root band (head-ish, near a root, outside the core)
    for k in range(3):
        root, tip, v = rods[order[k]]; ax = tip - root; L = np.linalg.norm(ax)
        _, t = seg_dist(P[v], root, tip); t = np.clip(t, -0.2, 1.2)
        wh = 1 - ss((t + 0.08) / 0.3); w2 = (1 - wh) * ss((t - 0.35) / 0.25); w1 = 1 - wh - w2
        i1, i2, ih = bi[f'gill{k}.L.1'], bi[f'gill{k}.L.2'], bi['head']
        Wn[v] = 0; Wn[v, ih] = wh; Wn[v, i1] = w1; Wn[v, i2] = w2
        # the bones
        j1 = root; j2 = root + 0.45 * ax; yv = unit(ax); Fo = qmat(B[f'gill{k}.L.1']['q']); zo = Fo[:, 2]; zz = unit(zo - yv * (zo @ yv)); xx = np.cross(yv, zz)
        q = mat2quat(np.stack([xx, yv, zz], 1))
        for nm, pos, end in ((f'gill{k}.L.1', j1, j2), (f'gill{k}.L.2', j2, tip)):
            B[nm]['pos'] = [round(float(x), 5) for x in pos]; B[nm]['end'] = [round(float(x), 5) for x in end]; B[nm]['q'] = [round(float(x), 6) for x in q]
        print(f'  gill{k}.L: root {np.round(root, 3)} tip {np.round(tip, 3)} length {L:.3f}, {len(v)} verts')
    # the other gill weights that stray outside the stalk pieces (the old lobes' cross-talk) go back to the head
    stalk = np.zeros(len(P), bool)
    for r in rods: stalk[r[2]] = True
    stray = side & ~stalk & (W[:, gb].sum(1) > 0)
    Wn[stray, bi['head']] += Wn[stray][:, gb].sum(1); Wn[np.ix_(stray, gb)] = 0
    # a little smoothing across the stalks' boundaries (graph Laplacian on the left gill / head area)
    nb = (np.linalg.norm(P - C, axis=1) < 0.9) & side & z['headish']
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = e[nb[e[:, 0]] & nb[e[:, 1]]]
    for _ in range(3):
        acc = np.zeros_like(Wn); cnt = np.zeros(len(P))
        np.add.at(acc, e[:, 0], Wn[e[:, 1]]); np.add.at(acc, e[:, 1], Wn[e[:, 0]]); np.add.at(cnt, e[:, 0], 1); np.add.at(cnt, e[:, 1], 1)
        m_ = nb & (cnt > 0); Wn[m_] = 0.5 * Wn[m_] + 0.5 * acc[m_] / cnt[m_, None]
    # mirror: the right side from the left, bone for bone
    mm = mirror_map(P); mb = np.array([bi[n.replace('.L', '.#').replace('.R', '.L').replace('.#', '.R')] for n in names])
    right = P[:, 0] < -1e-6; Wn[right] = Wn[mm[right]][:, mb]
    for k in range(3):
        for j in (1, 2):
            L_, R_ = B[f'gill{k}.L.{j}'], B[f'gill{k}.R.{j}']
            R_['pos'] = [-L_['pos'][0], L_['pos'][1], L_['pos'][2]]; R_['end'] = [-L_['end'][0], L_['end'][1], L_['end'][2]]
            Fl = qmat(L_['q']); Mx = np.diag([-1, 1, 1]); Fr = Mx @ Fl @ Mx; R_['q'] = [round(float(x), 6) for x in mat2quat(Fr)]
    # four influences
    top = np.argsort(-Wn, 1)[:, :4]; w4 = np.take_along_axis(Wn, top, 1); w4 = np.clip(w4, 0, None); w4 /= w4.sum(1, keepdims=True)
    s = np.load(O + 'stand7_rig.npz', allow_pickle=True); out = {k: s[k] for k in s.files}; out['idx'] = top.astype(np.uint8); out['w'] = w4.astype(np.float32)
    np.savez(O + 'stand8_rig.npz', **out)
    os.makedirs(O + 'www/s8', exist_ok=True); meta['bones'] = [B[b['name']] for b in meta['bones']]; json.dump(meta, open(O + 'www/s8/axo_stand.json', 'w'))
    print('wrote stand8_rig.npz, www/s8/axo_stand.json')
if __name__ == '__main__': main()
