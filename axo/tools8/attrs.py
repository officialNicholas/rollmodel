# The runtime's per-vertex look data for the new crawl body (the semantics of v246's, extras8.py and slimehead.py):
#   jelly: x belly (pale ventral side), y soft (1 - the rigid head; half on the digits), z thin (light passes through), w head (rigid head
#          and ears: the face is drawn where w > 0.72 and the skin has no jelly there)
#   fill:  x the crawl's paint-fill order (from the ground contacts up), y the stand's (the same here), z ambient occlusion, w free edge
#   mat:   x tail-fin height (0 bottom .. 1 top; 0.5 elsewhere), y the ear mask (1 the ears, 0.2 the skull, 0 the body), z wrinkle (joint
#          folds), w spot density
#   cpos:  xyz the canonical place (here the crawl's own rest: the stand never shows), w 'along' (arc coordinate down each chain)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy.spatial import cKDTree
import meshkit as mk
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def thickness(P, N, T, maxd=0.15):
    c = P[T].mean(1); kd = cKDTree(c); out = np.full(len(P), maxd); A, B, C = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]; e1 = B - A; e2 = C - A
    for i in range(len(P)):
        o = P[i] - N[i] * 1e-4; dv = -N[i]; cand = kd.query_ball_point(o + dv * maxd * 0.5, maxd * 0.75)
        if not cand: continue
        cand = np.array(cand); h = np.cross(dv, e2[cand]); a = (e1[cand] * h).sum(1); ok = np.abs(a) > 1e-12; f = np.where(ok, 1 / np.where(ok, a, 1), 0)
        s = o - A[cand]; u = f * (s * h).sum(1); q = np.cross(s, e1[cand]); v = f * (q @ dv); t = f * (q * e2[cand]).sum(1)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 2e-4) & (t < maxd)
        if hit.any(): out[i] = t[hit].min()
    return out
def ambient_occlusion(P, N, r=0.12):
    tree = cKDTree(P); occ = np.zeros(len(P)); pairs = tree.query_pairs(r, output_type='ndarray')
    d = P[pairs[:, 1]] - P[pairs[:, 0]]; L = np.linalg.norm(d, axis=1) + 1e-9; dh = d / L[:, None]; fall = 1 - L / r
    for a, b, sg in ((pairs[:, 0], pairs[:, 1], 1), (pairs[:, 1], pairs[:, 0], -1)):
        up = np.clip(np.einsum('ij,ij->i', N[a], dh * sg), 0, 1); num = np.zeros(len(P)); den = np.zeros(len(P)); np.add.at(num, a, up * fall); np.add.at(den, a, fall); occ += num / np.maximum(den, 1e-9)
    return np.clip(occ * 0.9, 0, 1)
CHAINS = [['hips', 'tail1', 'tail2', 'tail3', 'tail4', 'tail5', 'tail6'], ['hips', 'spine', 'spine1', 'chest', 'neck', 'head']]
for s in 'LR':
    CHAINS += [[f'shoulder.{s}', f'upperarm.{s}', f'forearm.{s}', f'hand.{s}'], [f'thigh.{s}', f'shin.{s}', f'foot.{s}', f'toes.{s}'], ['head', f'gill0.{s}.1', f'gill0.{s}.2']]
    for k in range(4): CHAINS += [[f'hand.{s}', f'finger{k}.{s}.1', f'finger{k}.{s}.2'], [f'toes.{s}', f'toe{k}.{s}.1', f'toe{k}.{s}.2']]
def compute(P, T, W, names, B, ears, verbose=True):
    n = len(P); ia = {k: i for i, k in enumerate(names)}; E = mk.edges(T); N = mk.vertex_normals(P, T)
    sm = lambda x, it=2: mk.smooth_scalar(E, n, x, iters=it)
    grp = lambda pre: np.clip(sum(W[:, i] for k, i in ia.items() if k.startswith(pre)), 0, 1)
    head = W[:, ia['head']]; gill = grp('gill'); digit = np.clip(grp('finger') + sum(W[:, i] for k, i in ia.items() if k.startswith('toe') and not k.startswith('toes')), 0, 1)
    tailW = grp('tail'); limbW = np.clip(sum(grp(p) for p in ('shoulder', 'upperarm', 'forearm', 'hand', 'thigh', 'shin', 'foot', 'toes')), 0, 1)
    trunkW = np.clip(sum(W[:, ia[k]] for k in ('hips', 'spine', 'spine1', 'chest', 'neck')), 0, 1)
    hw = np.clip(head + gill, 0, 1)
    # ---- jelly ----
    belly = ss((-N[:, 1] - 0.15) / 0.6) * np.clip(trunkW + tailW + 0.45 * limbW, 0, 1) * (1 - hw)
    chestF = ss((N[:, 2] - 0.2) / 0.6) * ss((-N[:, 1] + 0.3) / 0.8) * np.clip(W[:, ia['chest']] + W[:, ia['neck']] + 0.6 * W[:, ia['spine1']], 0, 1) * (1 - hw)   # (the round chest under the head)
    belly = np.clip(sm(np.maximum(belly, 0.7 * chestF), 3) * 1.1, 0, 1)
    soft = (1 - hw) * (1 - 0.5 * digit)
    th = thickness(P, N, T); thin = 1 - ss((th - 0.016) / 0.06); thin = np.clip(sm(thin, 2), 0, 1)
    # (the ears: a little light through their lower ends, as v10)
    ew = np.zeros(n)
    for s in 'LR':
        e = ears[s]; v = np.asarray(e['verts']); d = np.asarray(e['d'])[v]; ew[v] = np.clip(1 - d / max(e['droot'], 1e-6), 0, 1)
    thin = np.maximum(thin * (1 - gill), 0.3 * ss((ew - 0.6) / 0.4) * (gill > 0.3))
    jelly = np.stack([belly, soft, thin, hw], 1)
    # ---- fill ----
    G, _ = mk.graph(P, T); src = np.where(P[:, 1] < 0.07)[0]; d = mk.geodesic(G, src); d[~np.isfinite(d)] = np.nanmax(d[np.isfinite(d)]); order = sm(d / d.max(), 2)
    ao = sm(ambient_occlusion(P, N), 1)
    E2 = E; dots = (N[E2[:, 0]] * N[E2[:, 1]]).sum(1); mind = np.ones(n); np.minimum.at(mind, E2[:, 0], dots); np.minimum.at(mind, E2[:, 1], dots)
    edge = np.clip(sm(ss((0.55 - mind) / 0.6) * ss((thin - 0.3) / 0.4), 1) * 1.3, 0, 1)
    fill = np.stack([order, order, ao, edge], 1)
    # ---- mat ----
    finh = np.full(n, 0.5); tv = tailW > 0.3
    if tv.any():
        zz = P[tv, 2]; yy = P[tv, 1]; bins = np.linspace(zz.min() - 1e-6, zz.max() + 1e-6, 40); lo = np.full(len(bins) - 1, np.nan); hi = lo.copy()
        for k in range(len(bins) - 1):
            s_ = (zz >= bins[k]) & (zz < bins[k + 1])
            if s_.any(): lo[k], hi[k] = yy[s_].min(), yy[s_].max()
        ok = np.isfinite(lo); cz = 0.5 * (bins[1:] + bins[:-1]); lo = np.interp(P[:, 2], cz[ok], lo[ok]); hi = np.interp(P[:, 2], cz[ok], hi[ok])
        fh = np.clip((P[:, 1] - lo) / np.maximum(hi - lo, 1e-3), 0, 1); finh = 0.5 + (fh - 0.5) * ss((tailW - 0.2) / 0.5)
    finh = finh * (1 - gill)
    earm = np.where(gill > 0.02, 0.2 + 0.8 * ss(gill / 0.5), 0.2 * ss((head - 0.3) / 0.6))
    pairs = [(ia['chest'], ia['neck']), (ia['neck'], ia['head'])]
    for ch in CHAINS:
        if ch[0] in ('hips', 'head') or ch[0].startswith('shoulder'): continue
        for a, b in zip(ch[:-1], ch[1:]): pairs.append((ia[a], ia[b]))
    for s in 'LR': pairs.append((ia[f'upperarm.{s}'], ia[f'forearm.{s}']))
    wr = np.zeros(n)
    for a, b in pairs: wr = np.maximum(wr, 4 * W[:, a] * W[:, b])
    wr = np.clip(sm(wr, 2) * 1.2, 0, 1) * (1 - hw)
    faceZone = head * ss((N[:, 2] - 0.3) / 0.5)
    spots = np.clip(sm((1 - belly) * (1 - 0.55 * faceZone) * (1 - 0.1 * gill) * (1 - 0.5 * digit), 2), 0, 1)
    mat = np.stack([finh, earm, wr, spots], 1)
    # ---- cpos: the rest place and the arc coordinate down each chain ----
    Jp = {k: np.asarray(v[0]) for k, v in B.items()}; Je = {k: np.asarray(v[1]) for k, v in B.items()}
    along_b = {}; axis_b = {}
    for chn in CHAINS:
        acc = along_b.get(chn[0], 0.0)
        for j, k in enumerate(chn):
            if j > 0: acc += np.linalg.norm(Jp[k] - Jp[chn[j - 1]])
            if k not in along_b: along_b[k] = acc; ax = Je[k] - Jp[k]; axis_b[k] = ax / max(np.linalg.norm(ax), 1e-9)
    along = np.zeros(n)
    for k, i in ia.items():
        if k not in along_b: continue
        along += W[:, i] * (along_b[k] + (P - Jp[k]) @ axis_b[k])
    cpos = np.c_[P, along]
    if verbose: print(f'  attrs: belly>0.5 {int((belly > 0.5).sum())} thin>0.5 {int((thin > 0.5).sum())} head/ear (w) >0.9 {int((hw > 0.9).sum())} ears>0.5 {int((gill > 0.5).sum())} wrinkle>0.3 {int((wr > 0.3).sum())} ao p50/p99 {np.percentile(ao, 50):.2f}/{np.percentile(ao, 99):.2f} along {along.min():.2f}..{along.max():.2f}')
    return jelly, fill, mat, cpos, N
