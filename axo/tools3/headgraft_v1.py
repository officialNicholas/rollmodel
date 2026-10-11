# Stage 3 of the crawl head (v7): the very same head in both states. The crawl's skull behind the face is first moved onto the stand's skull
# (its face already lies on it: headmorph.py), then the stand's gills, with a collar of skull round their roots, replace the crawl's: both
# meshes are cut along the same line (a fixed distance from the union of the two gill sets, on two skulls that now coincide), the stand's
# patch is moved in (translation t: face centre onto face centre; the heads' frames agree) and zipped to the crawl's hole, the seam band
# faired and remeshed. Done on the left halves (the gills keep clear of the midline) and mirrored. The crawl's rig is kept; its gill joints,
# ends and frames become the stand's, so the gills ride the same bones in both states.
import sys, json, time
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2'); sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu
from remesh import Surface, remesh, compact, edges_of, quality, unit, vert_normals
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
DBG = True
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
    he = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); key = set(map(tuple, he))
    nxt = {}
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
    """triangles joining loop A (a directed boundary cycle of one part) to loop B (of the other, running the other way along it)"""
    Br = B[::-1]
    # start both at the closest pair; parametrize by normalized arc length
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
    """connected components of the vertices in mask (edges between masked vertices), as a label array (-1 outside)"""
    from scipy.sparse.csgraph import connected_components
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = e[mask[e[:, 0]] & mask[e[:, 1]]]
    A = coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)).tocsr(); _, lab = connected_components(A, directed=False)
    lab = np.where(mask, lab, -1); return lab
HOLE = 120
GROW = 4.0
def clean_region(n, T, U, maxhole=10 ** 9):
    """per side the largest connected piece of the region, with every hole in it filled"""
    out = np.zeros(n, bool); used = np.zeros(n, bool); used[T.ravel()] = True
    lab = components(n, T, U & used); ids, cnt = np.unique(lab[lab >= 0], return_counts=True)
    for k in ids[np.argsort(-cnt)][:2]: out |= lab == k          # the two largest: one per side
    lab2 = components(n, T, ~out & used); ids2, cnt2 = np.unique(lab2[lab2 >= 0], return_counts=True)
    big = ids2[np.argmax(cnt2)]
    for k, n_ in zip(ids2, cnt2):
        if k != big and n_ <= maxhole: out |= lab2 == k             # the other pieces of the outside are holes (stalks): fill them
    return out
def main():
    t0 = time.time()
    s = np.load(O + 'stand7_rig.npz', allow_pickle=True); c = np.load(O + 'crawl7_rig.npz', allow_pickle=True)
    sm = json.load(open(O + 'www/s7/axo_stand.json')); cm = json.load(open(O + 'www/c7/axo_crawl.json'))
    names = [b['name'] for b in cm['bones']]; bi = {k: i for i, k in enumerate(names)}; NB = len(names)
    assert names == [b['name'] for b in sm['bones']]
    Ws, Wc = dense(s, NB), dense(c, NB); gb = [bi[k] for k in names if k.startswith('gill')]
    t = c['C'] - s['C']; C = c['C']; print('t', t.round(4))
    Ps = s['P'] + t; Ts = s['T']; Pc = c['P'].copy(); Tc = c['T']
    gWs, gWc = Ws[:, gb].sum(1), Wc[:, gb].sum(1)
    hWs = Ws[:, bi['head']] + Ws[:, bi['headfront']] + gWs; hWc = Wc[:, bi['head']] + Wc[:, bi['headfront']] + gWc
    # ---- 1. the crawl's skull behind the face onto the stand's skull (a smooth displacement, fading toward the neck and the face)
    skull_s = Ts[(gWs[Ts] < 0.5).all(1) & (hWs[Ts] > 0.12).all(1)]; Ssk = Surface(Ps, skull_s)
    q = Pc - C; r = np.linalg.norm(q, axis=1); yaw = np.degrees(np.arctan2(np.abs(q[:, 0]), q[:, 2]))
    cand = (gWc < 0.3) & (hWc > 0.02) & (r < 0.7)
    d = np.zeros_like(Pc); d[cand] = Ssk.project(Pc[cand]) - Pc[cand]
    f = ss((yaw - 70) / 30) * ss((hWc - 0.05) / 0.45) * (np.linalg.norm(d, axis=1) < 0.15) * cand
    D = d * f[:, None]
    # fair it: the face cap and everything with no head weight stay put, the rest a smooth (biharmonic) blend of the projected moves
    keep = (f > 0.6) | (hWc < 0.01) | (yaw < 68) | (gWc > 0.3)
    D = fill(len(Pc), Tc, ~keep, D, order=2)
    from mesh import mirror_map
    mm = mirror_map(Pc); D = 0.5 * (D + D[mm] * np.array([-1, 1, 1]))   # exactly symmetric (the midline stays on x = 0)
    Pc2 = Pc + D; Pc2[np.abs(Pc[:, 0]) < 1e-9, 0] = 0
    mv = np.linalg.norm(D, axis=1); print(f'1. skull moved: {int((mv > 0.002).sum())} verts, max {mv.max() * 1000:.0f} mm, p95 {np.percentile(mv[mv > 0.002], 95) * 1000:.0f} mm')
    # ---- 2. the graft region: an egg in yaw / pitch about the face centre round both meshes' gill roots (out/graft_angles.png), on the skull
    # (where the two skulls now coincide), plus each mesh's own gill stalks
    EG = (130.0, 23.0, 30.0, 37.0)   # centre yaw, pitch; half-widths sideways, up (deg)
    def inside(P, rmax, grow=0.0):
        """an ellipse on the sphere of directions about the face centre (in the tangent plane at its centre direction u0), kept off the midline"""
        q = P - C; r = np.linalg.norm(q, axis=1); u = q / r[:, None]; u[:, 0] = np.abs(u[:, 0])
        yc, pc = np.radians(EG[0]), np.radians(EG[1]); u0 = np.array([np.sin(yc) * np.cos(pc), np.sin(pc), np.cos(yc) * np.cos(pc)])
        e1 = np.array([0, 1, 0]) - u0 * u0[1]; e1 /= np.linalg.norm(e1); e2 = np.cross(u0, e1)          # e1: up on the sphere, e2: sideways
        ang_ = np.degrees(np.arccos(np.clip(u @ u0, -1, 1))); v = u - (u @ u0)[:, None] * u0; vn = np.linalg.norm(v, axis=1) + 1e-12
        a1 = ang_ * (v @ e1) / vn; a2 = ang_ * (v @ e2) / vn
        return ((a1 / (EG[3] + grow)) ** 2 + (a2 / (EG[2] + grow)) ** 2 < 1) & (r < rmax) & (np.abs(q[:, 0]) > 0.07 - grow * 0.004)
    # (the gill stalks join the rest only through their roots inside the egg: filling the region's holes takes them in, whole)
    Us = clean_region(len(Ps), Ts, inside(Ps, 0.95) | (gWs > 0.15), maxhole=HOLE); Uc = clean_region(len(Pc2), Tc, inside(Pc2, 0.62, grow=GROW), maxhole=HOLE)   # a little wider: the hole rings the patch
    for nm_, U_, g_ in (('stand', Us, gWs > 0.3), ('crawl', Uc, gWc > 0.3)): print(f'   {nm_}: gill verts outside the region {int((g_ & ~U_).sum())}')
    print(f'2. region: stand {Us.sum()} verts (min |x| {np.abs(Ps[Us, 0]).min():.3f}), crawl {Uc.sum()} verts (min |x| {np.abs(Pc2[Uc, 0]).min():.3f})')
    # ---- 3. left halves: the crawl without the region, the stand's patch
    Lc = Pc2[:, 0] >= -1e-9; Tcl = Tc[Lc[Tc].all(1)]; Tck = Tcl[~Uc[Tcl].any(1)]
    Tsp = Ts[(Us[Ts].all(1)) & (Ps[Ts][:, :, 0] > 0).all(1)]
    # stitch: one vertex array (crawl first, then the stand), faces of both, zipper between the matching loops
    nc = len(Pc2); Pall = np.vstack([Pc2, Ps]); Tall = np.vstack([Tck, Tsp + nc])
    src = np.r_[np.zeros(nc, int), np.ones(len(Ps), int)]; oid = np.r_[np.arange(nc), np.arange(len(Ps))]
    Lk = [L for L in loops_of(Tck) if (np.abs(Pc2[L, 0]) > 1e-6).all()]   # the hole loops (not the midline seam)
    Lp = loops_of(Tsp)
    print(f'3. crawl hole loops {[len(L) for L in Lk]}, stand patch loops {[len(L) for L in Lp]}')
    if DBG: np.savez(O + 'out/graft_loops.npz', Pc2=Pc2, Ps=Ps, Lk=np.array(Lk, dtype=object), Lp=np.array(Lp, dtype=object), C=C, Us=Us, Uc=Uc)
    zt = []
    used = set()
    for L in Lk:
        cA = Pc2[L].mean(0); j = int(np.argmin([np.linalg.norm(Ps[M].mean(0) - cA) if k not in used else 1e9 for k, M in enumerate(Lp)])); used.add(j)
        M = Lp[j] + nc; zt.append(zipper(Pall, L, M))
        gap = np.linalg.norm(Pall[L][:, None] - Pall[M][None], axis=2).min(1); print(f'   loop {len(L)} <-> {len(M)}: gap p50 {np.median(gap) * 1000:.1f} max {gap.max() * 1000:.1f} mm')
    assert len(used) == len(Lp), 'unmatched stand loops'
    Z = np.vstack(zt); Tall = np.vstack([Tall, Z])
    P1, T1, ex = compact(Pall, Tall, {'src': src, 'oid': oid}); src1, oid1 = ex['src'], ex['oid']
    E_, _, _, cnt_, _ = edges_of(T1); ob = E_[cnt_ == 1]; off_ = ob[(np.abs(P1[ob[:, 0], 0]) > 1e-9) | (np.abs(P1[ob[:, 1], 0]) > 1e-9)]
    print(f'   merged: open edges {len(ob)} (off the midline {len(off_)}), non-manifold {int((cnt_ > 2).sum())}')
    if DBG and len(off_):
        for a_, b_ in off_[:12]:
            q_ = P1[a_] - C; r_ = np.linalg.norm(q_); print(f'      open edge {a_}-{b_} src {src1[a_]}{src1[b_]}  x {P1[a_, 0]:.3f}  yaw {np.degrees(np.arctan2(abs(q_[0]), q_[2])):.0f} pitch {np.degrees(np.arcsin(q_[1] / r_)):.0f} r {r_:.3f}')
    nm_e = E_[cnt_ > 2]
    for a_, b_ in nm_e:
        fa = np.where((T1 == a_).any(1) & (T1 == b_).any(1))[0]; q_ = P1[a_] - C; r_ = np.linalg.norm(q_)
        print(f'      non-manifold edge {a_}-{b_} src {src1[a_]}{src1[b_]}: faces {fa.tolist()} (zipper faces start at {len(Tck) + len(Tsp)}) yaw {np.degrees(np.arctan2(abs(q_[0]), q_[2])):.0f} pitch {np.degrees(np.arcsin(q_[1] / r_)):.0f} r {r_:.3f}')
    zn = np.cross(Pall[Z[:, 1]] - Pall[Z[:, 0]], Pall[Z[:, 2]] - Pall[Z[:, 0]]); zc = Pall[Z].mean(1) - C
    print(f'   zipper: {len(Z)} tris, facing out {(np.einsum("ij,ij->i", zn, zc) > 0).mean() * 100:.0f}%')
    qa = quality(Pc, Tc); print(f'   (the crawl as it was: quality min {qa.min():.3f}, {int((qa < 0.05).sum())} below 0.05)')
    for nm_, L_ in (('hole', Lk), ('patch', Lp)):
        for L in L_: print(f'   {nm_} loop {len(L)} verts, unique {len(set(L.tolist()))}')
    # the zipper vertices and the band round them (3 rings): faired positions
    zv = np.zeros(len(Pall), bool); zv[Z.ravel()] = True; used_ = np.zeros(len(Pall), bool); used_[Tall.ravel()] = True; remap = -np.ones(len(Pall), int); remap[used_] = np.arange(used_.sum())
    band = np.zeros(len(P1), bool); band[remap[np.where(zv)[0]]] = True
    A, _ = adjacency(len(P1), T1)
    for _ in range(3): band = band | (A @ band.astype(float) > 0)
    E1, _, _, cnt1, _ = edges_of(T1); bv = np.zeros(len(P1), bool); bv[E1[cnt1 == 1].ravel()] = True
    free = band & ~bv
    P1 = fill(len(P1), T1, free, P1, order=2)
    print(f'4. merged left half: {len(P1)} verts, {len(T1)} tris; band {band.sum()} verts faired')
    # ---- 4. remesh the band (the rest frozen) to even triangles at the local size
    E, t2, o2, cnt, _ = edges_of(T1); el = np.linalg.norm(P1[E[:, 0]] - P1[E[:, 1]], axis=1); Lf = np.zeros(len(P1)); k_ = np.zeros(len(P1))
    np.add.at(Lf, E[:, 0], el); np.add.at(Lf, E[:, 1], el); np.add.at(k_, E[:, 0], 1); np.add.at(k_, E[:, 1], 1); Lf /= np.maximum(k_, 1)
    head_ = (np.linalg.norm(P1 - C, axis=1) < 0.6) & ~band; Lf = np.where(band, np.median(Lf[head_]), Lf)
    frozen = ~band; carry = np.arange(len(P1))
    P2, T2, car = remesh(P1, T1, Lf, frozen=frozen, iters=4, labels=carry, verbose=True)
    src2, oid2 = src1[car], oid1[car]
    q2 = quality(P2, T2); print(f'   quality after: min {q2.min():.3f} p1 {np.percentile(q2, 1):.3f}')
    # ---- 5. mirror to the full mesh
    seam = np.abs(P2[:, 0]) < 1e-9; n2 = len(P2); ns = np.where(~seam)[0]; mir = np.arange(n2); mir[ns] = n2 + np.arange(len(ns))
    P3 = np.vstack([P2, P2[ns] * np.array([-1, 1, 1])]); T3 = np.vstack([T2, mir[T2][:, ::-1]]); src3 = np.r_[src2, src2[ns]]; oid3 = np.r_[oid2, oid2[ns]]; side = np.r_[np.ones(n2), -np.ones(len(ns))]
    # ---- 6. weights: the stand's on its patch, the crawl's elsewhere (the right half mirrored bone for bone), faired across the seam band
    mirror_b = np.array([bi[k.replace('.L', '.#').replace('.R', '.L').replace('.#', '.R')] for k in names])
    W3 = np.zeros((len(P3), NB))
    for i in range(n2): W3[i] = Ws[oid3[i]] if src3[i] == 1 else Wc[oid3[i]]   # the left half (the stand's patch came from its left side)
    for i in range(n2, len(P3)): W3[i] = W3[ns[i - n2]][mirror_b]              # the right half: its left partner's, bone for bone
    # band in the merged half (vertices created by the remesh or touching the other source)
    A3, _ = adjacency(len(P3), T3); mixed = np.zeros(len(P3), bool)
    for a_, b_ in edges_of(T3)[0]:
        if src3[a_] != src3[b_]: mixed[a_] = mixed[b_] = True
    bandL = mixed.copy()
    for _ in range(3): bandL = bandL | (A3 @ bandL.astype(float) > 0)
    W3 = fill(len(P3), T3, bandL, W3, order=1)
    W3 = np.clip(W3, 0, None)
    top = np.argsort(-W3, 1)[:, :4]; w4 = np.take_along_axis(W3, top, 1); w4 /= w4.sum(1, keepdims=True)
    lab_s = s['labels']; lab_c = c['labels']
    lab3 = np.array([('gill' if gWs[o] > 0.5 else str(lab_s[o])) if sr == 1 else str(lab_c[o]) for sr, o in zip(src3, oid3)])
    gill3 = np.array([(gWs[o] > 0.5) if sr == 1 else bool(c['gill'][o]) for sr, o in zip(src3, oid3)])
    # ---- 7. the rig: the crawl's, with the stand's gill bones (moved by t)
    meta = json.loads(json.dumps(cm)); sb = {b['name']: b for b in sm['bones']}
    for b in meta['bones']:
        if b['name'].startswith('gill'):
            o = sb[b['name']]; b['pos'] = [round(float(v), 5) for v in np.array(o['pos']) + t]; b['end'] = [round(float(v), 5) for v in np.array(o['end']) + t]; b['q'] = o['q']
    import os; os.makedirs(O + 'www/c8', exist_ok=True)
    meta['n'] = len(P3); meta['ni'] = int(T3.size); meta['bbox'] = [P3.min(0).round(4).tolist(), P3.max(0).round(4).tolist()]
    json.dump(meta, open(O + 'www/c8/axo_crawl.json', 'w'))
    np.savez(O + 'crawl8_rig.npz', P=P3, T=T3, idx=top.astype(np.uint8), w=w4.astype(np.float32), labels=lab3, names=np.array(names), gill=gill3, C=c['C'], R=c['R'], src=src3)
    q3 = quality(P3, T3); E3, _, _, cnt3, _ = edges_of(T3)
    print(f'7. crawl8: {len(P3)} verts {len(T3)} tris; open edges {(cnt3 == 1).sum()}, non-manifold {(cnt3 > 2).sum()}; quality min {q3.min():.3f}; ({time.time() - t0:.1f}s)')
if __name__ == '__main__': main()
