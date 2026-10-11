# Stage 3 of the crawl head (v7): the very same head in both states. The crawl's face already lies on the stand's (headmorph.py); here its
# skull round the gill roots is moved onto the stand's skull, then the stand's gills, with the skull they grow from, replace the crawl's:
#  - the graft region is an ellipse on the sphere of directions about the face centre (round both meshes' gill roots, out/graft_angles.png),
#    each mesh's gill stalks with it whole; both meshes are cut exactly along it (the crawl along a slightly larger one, so its hole rings the
#    patch by ~2 cm), the stand's patch is moved in (translation t: face centre onto face centre; the two heads' frames agree) and zipped
#    to the crawl's hole, the seam band faired (biharmonic) and remeshed to even triangles;
#  - done on the left halves (the region keeps clear of the midline) and mirrored, so the result is exactly symmetric;
#  - the rig is the crawl's, except the gill joints, ends and frames, which become the stand's (moved by t): the gills ride the same bones in
#    both states; weights: the stand's on the patch, the crawl's elsewhere, faired across the seam band.
import sys, json, time, os
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2'); sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu
from remesh import Surface, remesh, compact, edges_of, quality, unit
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
DBG = True
EG = (130.0, 23.0, 30.0, 37.0)   # the graft ellipse: centre yaw, pitch (deg, left side); half-widths sideways, up (deg)
RHO_C = 1.09                     # the crawl's cut: a slightly larger ellipse (its hole rings the stand's patch)
def ss(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def adjacency(n, T):
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = np.unique(np.sort(e, 1), axis=0)
    A = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr(); return A, np.asarray(A.sum(1)).ravel()
def fill(n, T, free, vals, order=2, reg=1e-9):
    """values on the free vertices from the fixed ones: harmonic (order 1) or biharmonic (order 2) over the mesh graph"""
    A, deg = adjacency(n, T); L = (diags(deg) - A).tocsr()
    M = L if order == 1 else (L.T @ diags(1.0 / np.maximum(deg, 1)) @ L).tocsr()
    un = np.where(free)[0]; kn = np.where(~free)[0]
    if len(un) == 0: return vals.copy()
    lu = splu((M[un][:, un] + diags(np.full(len(un), reg))).tocsc()); rhs = -(M[un][:, kn] @ vals[kn])
    out = vals.copy(); out[un] = np.stack([lu.solve(rhs[:, k]) for k in range(vals.shape[1])], 1); return out
def dense(z, nb):
    W = np.zeros((len(z['P']), nb))
    for k in range(4): np.add.at(W, (np.arange(len(z['P'])), z['idx'][:, k].astype(int)), z['w'][:, k])
    return W
def loops_of(T):
    """directed boundary cycles (half-edges without a twin), as vertex lists"""
    he = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); key = set(map(tuple, he)); nxt = {}
    for a, b in he:
        if (b, a) not in key: nxt[a] = b
    out = []; seen = set()
    for a in list(nxt):
        if a in seen: continue
        cyc = [a]; seen.add(a); b = nxt[a]
        while b != a and b not in seen: cyc.append(b); seen.add(b); b = nxt.get(b, a)
        out.append(np.array(cyc))
    return out
def zipper(P, A, B):
    """triangles joining loop A (a directed boundary cycle of one part) to loop B (of the other part, running the other way along it)"""
    Br = B[::-1]
    d = np.linalg.norm(P[A][:, None] - P[Br][None], axis=2); i0, j0 = np.unravel_index(np.argmin(d), d.shape)
    A = np.roll(A, -i0); Br = np.roll(Br, -j0)
    def param(L):
        seg = np.linalg.norm(P[np.roll(L, -1)] - P[L], axis=1); c = np.r_[0, np.cumsum(seg)]; return c / c[-1]
    sa, sb = param(A), param(Br); na, nb = len(A), len(Br); i = j = 0; tris = []
    while i < na or j < nb:
        a0, a1 = A[i % na], A[(i + 1) % na]; b0, b1 = Br[j % nb], Br[(j + 1) % nb]
        if j >= nb or (i < na and sa[i + 1] <= sb[j + 1]): tris.append((a1, a0, b0)); i += 1
        else: tris.append((b0, b1, a0)); j += 1
    return np.array(tris)
def components(n, T, mask):
    from scipy.sparse.csgraph import connected_components
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = e[mask[e[:, 0]] & mask[e[:, 1]]]
    A = coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)).tocsr(); _, lab = connected_components(A, directed=False)
    return np.where(mask, lab, -1)
def clean_region(n, T, U, maxhole=120):
    """the largest connected piece of the region on each side, with its holes (pieces of the outside it encloses: the gill stalks) filled"""
    out = np.zeros(n, bool); used = np.zeros(n, bool); used[T.ravel()] = True
    lab = components(n, T, U & used); ids, cnt = np.unique(lab[lab >= 0], return_counts=True)
    for k in ids[np.argsort(-cnt)][:2]: out |= lab == k
    lab2 = components(n, T, ~out & used); ids2, cnt2 = np.unique(lab2[lab2 >= 0], return_counts=True); big = ids2[np.argmax(cnt2)]
    for k, n_ in zip(ids2, cnt2):
        if k != big and n_ <= maxhole: out |= lab2 == k
    return out
def ellipse_rho(P, C):
    """the graft ellipse's normalized radius (1 on its edge) for each point's direction from the face centre (both sides folded onto the left)"""
    q = P - C; r = np.linalg.norm(q, axis=1); u = q / r[:, None]; u[:, 0] = np.abs(u[:, 0])
    yc, pc = np.radians(EG[0]), np.radians(EG[1]); u0 = np.array([np.sin(yc) * np.cos(pc), np.sin(pc), np.cos(yc) * np.cos(pc)])
    e1 = np.array([0, 1, 0]) - u0 * u0[1]; e1 /= np.linalg.norm(e1); e2 = np.cross(u0, e1)
    ang = np.degrees(np.arccos(np.clip(u @ u0, -1, 1))); v = u - (u @ u0)[:, None] * u0; vn = np.linalg.norm(v, axis=1) + 1e-12
    return np.sqrt((ang * (v @ e1) / vn / EG[3]) ** 2 + (ang * (v @ e2) / vn / EG[2]) ** 2), r
def cut(P, T, phi, attrs):
    """split the mesh exactly along phi = 0 (linear on edges): returns P, T, side (per face: True where phi < 0) and the attributes
    carried to the new vertices (lerped)"""
    phi = np.where(np.abs(phi) < 1e-9, 1e-9, phi); neg = phi < 0; newv = {}; P = list(P); A = {k: list(v) for k, v in attrs.items()}
    def vid(a, b):
        k = (min(a, b), max(a, b))
        if k not in newv:
            u = phi[a] / (phi[a] - phi[b]); newv[k] = len(P); P.append(P[a] + u * (P[b] - P[a]))
            for kk in A: A[kk].append(A[kk][a] + u * (A[kk][b] - A[kk][a]))
        return newv[k]
    Tn, side = [], []
    for t in T:
        s = neg[t]; c = s.sum()
        if c == 0 or c == 3: Tn.append(tuple(t)); side.append(bool(c == 3)); continue
        # the lone vertex (the one on its own side), rotated to the front, orientation kept
        k = int(np.where(s == (c == 1))[0][0]); a, b, d = t[k], t[(k + 1) % 3], t[(k + 2) % 3]
        ab, ad = vid(a, b), vid(a, d); lone = bool(neg[a])
        Tn.append((a, ab, ad)); side.append(lone); Tn.append((ab, b, d)); side.append(not lone); Tn.append((ab, d, ad)); side.append(not lone)
    return np.array(P), np.array(Tn), np.array(side), {k: np.array(v) for k, v in A.items()}

def main():
    t0 = time.time()
    s = np.load(O + 'stand8_rig.npz', allow_pickle=True); c = np.load(O + 'crawl7_rig.npz', allow_pickle=True)
    sm = json.load(open(O + 'www/s8/axo_stand.json')); cm = json.load(open(O + 'www/c7/axo_crawl.json'))
    names = [b['name'] for b in cm['bones']]; bi = {k: i for i, k in enumerate(names)}; NB = len(names)
    assert names == [b['name'] for b in sm['bones']]
    Ws, Wc = dense(s, NB), dense(c, NB); gb = [bi[k] for k in names if k.startswith('gill')]
    t = c['C'] - s['C']; C = c['C']; print('t', t.round(4))
    Ps = s['P'] + t; Ts = s['T']; Pc = c['P'].copy(); Tc = c['T']
    gWs, gWc = Ws[:, gb].sum(1), Wc[:, gb].sum(1); hWs = Ws[:, bi['head']] + Ws[:, bi['headfront']] + gWs; hWc = Wc[:, bi['head']] + Wc[:, bi['headfront']] + gWc
    # ---- 1. the crawl's skull round the graft region onto the stand's skull: a smooth move, full over the region and a little beyond, gone
    # by 1.8 x its size (the face, the back of the skull and the neck keep the crawl's own shape)
    skull_s = Ts[(gWs[Ts] < 0.5).all(1) & (hWs[Ts] > 0.12).all(1)]; Ssk = Surface(Ps, skull_s)
    rho_c, r_c = ellipse_rho(Pc, C); cand = (gWc < 0.3) & (rho_c < 1.9) & (r_c < 0.7)
    d = np.zeros_like(Pc); d[cand] = Ssk.project(Pc[cand]) - Pc[cand]
    f = ss((1.8 - rho_c) / 0.6) * (np.linalg.norm(d, axis=1) < 0.15) * cand
    D = d * f[:, None]; keep = (f > 0.9) | (rho_c > 1.85) | (gWc > 0.3)
    D = fill(len(Pc), Tc, ~keep, D, order=2)
    # ... and the face's lower half, mouth and chin onto the stand's (the face caps are one sphere only down to -16 deg; below it the crawl's
    # chin edge carried an 8 mm ridge at the midline that put a kink in the mouth): a window in yaw / pitch, faded over 10 deg
    q = Pc - C; r_ = np.linalg.norm(q, axis=1); yw = np.degrees(np.arctan2(q[:, 0], q[:, 2])); pt = np.degrees(np.arcsin(np.clip(q[:, 1] / r_, -1, 1)))
    head_s = Ts[(gWs[Ts] < 0.5).all(1) & (hWs[Ts] > 0.3).all(1)]; Shd = Surface(Ps, head_s)
    win = ss((55 - np.abs(yw)) / 10) * ss((pt + 48) / 10) * ss((0 - pt) / 10) * (r_ < 0.5) * (gWc < 0.3)
    cf = win > 0; d2 = np.zeros_like(Pc); d2[cf] = Shd.project(Pc[cf]) - Pc[cf]; ok2 = np.linalg.norm(d2, axis=1) < 0.03
    D = D + d2 * (win * ok2)[:, None]
    print(f'   face / chin: {int((win * ok2 > 0.01).sum())} verts moved, max {np.linalg.norm(d2 * (win * ok2)[:, None], axis=1).max() * 1000:.1f} mm')
    from mesh import mirror_map
    mm = mirror_map(Pc); D = 0.5 * (D + D[mm] * np.array([-1, 1, 1])); Pc2 = Pc + D; Pc2[np.abs(Pc[:, 0]) < 1e-9, 0] = 0
    mv = np.linalg.norm(D, axis=1); print(f'1. skull moved: {int((mv > 0.002).sum())} verts, max {mv.max() * 1000:.0f} mm, p95 {np.percentile(mv[mv > 0.002], 95) * 1000:.0f} mm')
    # ---- 2. the regions (vertex level, cleaned: the stalks taken in whole), then the exact cuts along the ellipses
    rs, r_s = ellipse_rho(Ps, C); rc2, r_c2 = ellipse_rho(Pc2, C)
    Us = clean_region(len(Ps), Ts, ((rs < 1) & (r_s < 0.95)) | (gWs > 0.15)); Uc = clean_region(len(Pc2), Tc, ((rc2 < RHO_C) & (r_c2 < 0.62)) | (gWc > 0.3))
    for nm_, U_, g_ in (('stand', Us, gWs > 0.15), ('crawl', Uc, gWc > 0.3)): print(f'   {nm_}: region {int(U_.sum())} verts, gill verts outside it {int((g_ & ~U_).sum())}, min |x| {np.abs((Ps if nm_ == "stand" else Pc2)[U_, 0]).min():.3f}')
    # phi < 0 inside: the ellipse's own value where the region follows it, pinned inside / outside where the region took stalks in
    phs = np.where(Us, np.minimum(rs - 1, -1e-3), np.maximum(rs - 1, 1e-3)); phc = np.where(Uc, np.minimum(rc2 - RHO_C, -1e-3), np.maximum(rc2 - RHO_C, 1e-3))
    # left halves
    Ls = (Ps[Ts][:, :, 0] > -1e-9).all(1); Lc = (Pc2[Tc][:, :, 0] > -1e-9).all(1)
    frs = (s['labels'] == 'gill').astype(float)[:, None]; frc = np.array([str(l).startswith('gill') for l in c['labels']], float)[:, None]
    Ps_, Ts_, sides, As = cut(Ps, Ts[Ls], phs, {'W': Ws, 'fr': frs})
    Pc_, Tc_, sidec, Ac = cut(Pc2, Tc[Lc], phc, {'W': Wc, 'fr': frc})
    Tpatch = Ts_[sides]; Tkeep = Tc_[~sidec]
    Tpatch = Tpatch[(Ps_[Tpatch][:, :, 0] > 1e-6).all(1)]   # the stand's patch on the left only
    nc = len(Pc_); Pall = np.vstack([Pc_, Ps_]); Tall = np.vstack([Tkeep, Tpatch + nc]); Wall = np.vstack([Ac['W'], As['W']]); FRall = np.vstack([Ac['fr'], As['fr']])
    src = np.r_[np.zeros(nc, int), np.ones(len(Ps_), int)]
    Lk = [L for L in loops_of(Tkeep) if (np.abs(Pc_[L, 0]) > 1e-6).all()]; Lp = loops_of(Tpatch)
    print(f'2. cut: crawl hole loops {[len(L) for L in Lk]}, stand patch loops {[len(L) for L in Lp]}')
    assert len(Lk) == 1 and len(Lp) == 1, 'expected one loop each'
    L = Lk[0]; M = Lp[0] + nc
    gap = np.linalg.norm(Pall[L][:, None] - Pall[M][None], axis=2).min(1); print(f'   loops {len(L)} <-> {len(M)}: gap p50 {np.median(gap) * 1000:.1f} min {gap.min() * 1000:.1f} max {gap.max() * 1000:.1f} mm')
    Z = zipper(Pall, L, M); Tall = np.vstack([Tall, Z])
    zn = np.cross(Pall[Z[:, 1]] - Pall[Z[:, 0]], Pall[Z[:, 2]] - Pall[Z[:, 0]]); zc = Pall[Z].mean(1) - C
    print(f'   zipper: {len(Z)} tris, facing out {(np.einsum("ij,ij->i", zn, zc) > 0).mean() * 100:.0f}%')
    if DBG: np.savez(O + 'out/graft_loops.npz', Pc2=Pc2, Ps=Ps, Pc_=Pc_, Ps_=Ps_, L=L, M=M - nc, C=C, Us=Us, Uc=Uc)
    P1, T1, ex = compact(Pall, Tall, {'src': src, 'W': Wall, 'fr': FRall}); src1, W1, FR1 = ex['src'], ex['W'], ex['fr']
    E_, _, _, cnt_, _ = edges_of(T1); ob = E_[cnt_ == 1]; off_ = ob[(np.abs(P1[ob[:, 0], 0]) > 1e-9) | (np.abs(P1[ob[:, 1], 0]) > 1e-9)]
    print(f'   merged left half: {len(P1)} verts {len(T1)} tris; open edges off the midline {len(off_)}, non-manifold {int((cnt_ > 2).sum())}')
    # ---- 3. the seam band: the zipper and 3 rings round it (the cut slivers among them); faired, then remeshed to even triangles (the rest frozen)
    used_ = np.zeros(len(Pall), bool); used_[Tall.ravel()] = True; remap = -np.ones(len(Pall), int); remap[used_] = np.arange(used_.sum())
    band = np.zeros(len(P1), bool); band[remap[np.unique(Z.ravel())]] = True
    A1, _ = adjacency(len(P1), T1)
    for _ in range(3): band = band | (A1 @ band.astype(float) > 0)
    bv = np.zeros(len(P1), bool); bv[ob.ravel()] = True
    P1 = fill(len(P1), T1, band & ~bv, P1, order=2)
    E, _, _, cnt, _ = edges_of(T1); el = np.linalg.norm(P1[E[:, 0]] - P1[E[:, 1]], axis=1); Lf = np.zeros(len(P1)); k_ = np.zeros(len(P1))
    np.add.at(Lf, E[:, 0], el); np.add.at(Lf, E[:, 1], el); np.add.at(k_, E[:, 0], 1); np.add.at(k_, E[:, 1], 1); Lf /= np.maximum(k_, 1)
    head_ = (np.linalg.norm(P1 - C, axis=1) < 0.6) & ~band; Lf = np.where(band, np.median(Lf[head_]), Lf)
    P2, T2, car = remesh(P1, T1, Lf, frozen=~band, iters=4, labels=np.arange(len(P1)), verbose=True)
    # weights and source onto the remeshed vertices (closest point of the faired surface, barycentric)
    S1 = Surface(P1, T1); bt, bc, _ = S1.project_bary(P2); W2 = np.einsum('ij,ijk->ik', bc, W1[T1[bt]]); FR2 = np.einsum('ij,ijk->ik', bc, FR1[T1[bt]]); src2 = np.round(np.einsum('ij,ij->i', bc, src1[T1[bt]].astype(float))).astype(int)
    q2 = quality(P2, T2); print(f'   after remesh: {len(P2)} verts, quality min {q2.min():.3f} p1 {np.percentile(q2, 1):.3f}')
    # ---- 4. mirror to the full mesh
    seam = np.abs(P2[:, 0]) < 1e-9; n2 = len(P2); ns = np.where(~seam)[0]; mir = np.arange(n2); mir[ns] = n2 + np.arange(len(ns))
    P3 = np.vstack([P2, P2[ns] * np.array([-1, 1, 1])]); T3 = np.vstack([T2, mir[T2][:, ::-1]]); src3 = np.r_[src2, src2[ns]]
    mirror_b = np.array([bi[k.replace('.L', '.#').replace('.R', '.L').replace('.#', '.R')] for k in names])
    W3 = np.vstack([W2, W2[ns][:, mirror_b]]); FR3 = np.r_[FR2[:, 0], FR2[ns, 0]]
    # ---- 5. weights faired across the seam band (both halves at once: the problem is symmetric), four influences
    mixed = np.zeros(len(P3), bool); E3 = edges_of(T3)[0]; m_ = src3[E3[:, 0]] != src3[E3[:, 1]]; mixed[E3[m_].ravel()] = True
    A3, _ = adjacency(len(P3), T3); bandW = mixed.copy()
    for _ in range(3): bandW = bandW | (A3 @ bandW.astype(float) > 0)
    W3 = np.clip(fill(len(P3), T3, bandW, W3, order=1), 0, None)
    top = np.argsort(-W3, 1)[:, :4]; w4 = np.take_along_axis(W3, top, 1); w4 /= w4.sum(1, keepdims=True)
    gill3 = (W3[:, gb].sum(1) > 0.5)
    # ---- 6. the rig: the crawl's, with the stand's gill bones (moved by t)
    meta = json.loads(json.dumps(cm)); sb = {b['name']: b for b in sm['bones']}
    for b in meta['bones']:
        if b['name'].startswith('gill'):
            o = sb[b['name']]; b['pos'] = [round(float(v), 5) for v in np.array(o['pos']) + t]; b['end'] = [round(float(v), 5) for v in np.array(o['end']) + t]; b['q'] = o['q']
    os.makedirs(O + 'www/c8', exist_ok=True)
    meta['n'] = len(P3); meta['ni'] = int(T3.size); meta['bbox'] = [P3.min(0).round(4).tolist(), P3.max(0).round(4).tolist()]
    json.dump(meta, open(O + 'www/c8/axo_crawl.json', 'w'))
    np.savez(O + 'crawl8_rig.npz', P=P3, T=T3, idx=top.astype(np.uint8), w=w4.astype(np.float32), labels=np.where(FR3 > 0.5, 'gill', 'body'), names=np.array(names), gill=gill3, C=c['C'], R=c['R'], src=src3)
    q3 = quality(P3, T3); E3, _, _, cnt3, _ = edges_of(T3)
    print(f'6. crawl8: {len(P3)} verts {len(T3)} tris; open edges {(cnt3 == 1).sum()}, non-manifold {(cnt3 > 2).sum()}; quality min {q3.min():.3f} p1 {np.percentile(q3, 1):.3f} ({time.time() - t0:.1f}s)')
if __name__ == '__main__': main()
