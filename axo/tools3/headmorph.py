# Stage 2 of the crawl rebuild: the same head in both states. The crawl head's face, top, sides and chin are moved onto the stand head's shell
# (both in one head-local frame: the stand's face-sphere centre and the matching point on the crawl, the crawl in its export scale 1.15), the
# move fading out toward the back of the skull, the throat and the neck; the gills ride on their roots and grow with the head.
import sys, os, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2'); sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu
from headmap import ray_hits, fit_sphere
from headana import heads
from crawlbuild import load_old
from straighten import write_view
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
SC = 1.15                                           # crawl export scale
CS = np.array([0.021, 1.19, 0.041]); RS = 0.329      # the stand's face sphere (stand export coordinates)
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def graph_lap(n, T):
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = np.unique(np.sort(e, 1), axis=0)
    A = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr(); deg = np.asarray(A.sum(1)).ravel(); return A, deg
def harmonic_fill(n, T, known, vals, reg=1e-4):
    """smooth interpolation of vals (k x d) at known vertices over the mesh graph (Laplace with the knowns fixed)"""
    A, deg = graph_lap(n, T); L = (diags(deg) - A).tocsr(); un = np.where(~known)[0]; kn = np.where(known)[0]
    M = (L[un][:, un] + diags(np.full(len(un), reg))).tocsc(); lu = splu(M); rhs = -(L[un][:, kn] @ vals[known])
    out = np.zeros((n, vals.shape[1])); out[known] = vals[known]; out[un] = np.stack([lu.solve(rhs[:, k]) for k in range(vals.shape[1])], 1); return out
def biharmonic_fill(n, T, known, vals, reg=1e-7):
    A, deg = graph_lap(n, T); L = (diags(deg) - A).tocsr(); Bm = (L.T @ diags(1.0 / np.maximum(deg, 1)) @ L).tocsr()
    un = np.where(~known)[0]; kn = np.where(known)[0]; Mu = (Bm[un][:, un] + diags(np.full(len(un), reg))).tocsc(); lu = splu(Mu)
    rhs = -(Bm[un][:, kn] @ vals[kn]); out = vals.copy(); out[un] = np.stack([lu.solve(rhs[:, k]) for k in range(vals.shape[1])], 1); return out
def main(zc=None, yc=None, show=True):
    H = heads(); Ps, Ts, _ = H['stand']
    z = np.load(O + 'crawl_sym.npz', allow_pickle=True); P = z['P'].copy(); T = z['T']; src = z['src']; m, W, names, lab = load_old()
    a = src[:, 0].astype(int); b = src[:, 1].astype(int); u = src[:, 2]; labc = np.where(u < 0.5, lab[a], lab[b]); isg = np.array([l.startswith('gill') for l in labc])
    n = len(P)
    # free gill parts = the old gill labels that are also thin (an opposite-facing surface within 3.5 cm): the old 'gill2' label also covered
    # a patch of neck skin behind the head (the sculpt's lowest stalk lies fused on the neck), which must move as skin
    Tn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); Nv = np.zeros((n, 3))
    for k in range(3): np.add.at(Nv, T[:, k], Tn)
    Nv = unit(Nv); kdp = cKDTree(P); thin = np.zeros(n, bool)
    for i in np.where(isg)[0]:
        j = kdp.query_ball_point(P[i], 0.035)
        if len(j) > 1 and (Nv[j] @ Nv[i]).min() < -0.3: thin[i] = True
    print(f'  gill labels {int(isg.sum())}, thin (free) {int(thin.sum())}')
    isg = isg & thin
    # the crawl head-local origin (sym units): its face front at the snout, the sphere radius in sym units = RS / SC
    R = RS / SC; zfront = P[~isg & (np.abs(P[:, 0]) < 0.05), 2].max(); zc = zfront - R if zc is None else zc; yc = 0.05 if yc is None else yc
    Cc = np.array([0.0, yc, zc]); print(f'crawl face centre (sym) {Cc.round(3)} R {R:.3f}; snout front z {zfront:+.3f}')
    # the stand head shell in the crawl's sym frame
    Pst = (Ps - CS) / SC + Cc
    # which crawl vertices move: the skull around the face (the old head label and the skin near it), by direction from the centre
    d = P - Cc; dist = np.linalg.norm(d, axis=1); dirs = d / dist[:, None]
    yaw = np.degrees(np.arctan2(dirs[:, 0], dirs[:, 2])); pitch = np.degrees(np.arcsin(np.clip(dirs[:, 1], -1, 1)))
    # keep the crawl's own neck: directions within ~45 deg of the neck axis (back and down) are not moved, full move beyond ~85 deg
    nax = unit(np.array([0.0, -0.55, -1.0])); ang = np.degrees(np.arccos(np.clip(dirs @ nax, -1, 1)))
    wdir = ss((ang - 45) / 40) * ss((pitch + 62) / 22)
    near = dist < R * 1.9; cand = near & ~isg & (wdir > 0.001)
    # target: where the ray from the centre through the vertex meets the stand shell (outermost hit)
    tgt = P.copy(); hit = np.zeros(n, bool); ci = np.where(cand)[0]
    r, _ = ray_hits(Pst, Ts, Cc, dirs[ci])
    ok = np.isfinite(r); tgt[ci[ok]] = Cc + dirs[ci[ok]] * r[ok, None]; hit[ci[ok]] = True
    disp = np.zeros((n, 3)); disp[hit] = (tgt[hit] - P[hit])
    print(f'  shell targets: {int(hit.sum())} of {len(ci)} candidates; |move| mean {np.linalg.norm(disp[hit], axis=1).mean() * 100:.1f} cm max {np.linalg.norm(disp[hit], axis=1).max() * 100:.1f} cm')
    # the move as a smooth (biharmonic) field: the head's core pinned to the stand shell, the body beyond the neck pinned in place, the band
    # between solved C1-smooth (a harmonic fill kinks at the edge of what it is pinned to: that was the chevron on the neck)
    tdist = np.linalg.norm(tgt - Cc, axis=1)
    core = hit & (wdir > 0.92) & (dist < R * 1.3) & (np.abs(tdist - dist) < 0.5 * R)   # the skull itself, not the neck behind it
    far = (dist > R * 2.3) & ~isg
    known = core | far; vals = np.zeros((n, 3)); vals[core] = disp[core]
    field = biharmonic_fill(n, T, known, vals)   # the gills are free: the field runs smoothly out along them (they grow with the head)
    print(f'  core (pinned skull) {int(core.sum())} verts; gill move mean {np.linalg.norm(field[isg], axis=1).mean() * 100:.1f} cm')
    # overlapping sheets (frills fused onto the neck lie on top of its skin, unconnected in the mesh) must move together: smooth the field in 3D
    # (Gaussian over Euclidean neighbours, 4 cm) everywhere but the pinned skull and the free frill tips
    kd = cKDTree(P); prs = kd.query_ball_point(P, 0.045); skv = np.where(~isg)[0]; dsk, _ = cKDTree(P[skv]).query(P)
    keep = core | (isg & (dsk > 0.03))
    for it in range(3):
        f2 = field.copy()
        for i in np.where(~keep)[0]:
            j = np.array(prs[i]); w = np.exp(-(np.linalg.norm(P[j] - P[i], axis=1) / 0.025) ** 2); f2[i] = (w[:, None] * field[j]).sum(0) / w.sum()
        field = f2
    P2 = P + field
    # grow each stalk (a connected component of gill skin on one side) about where it leaves the head, the tip the most
    from scipy.sparse.csgraph import connected_components
    A, deg = graph_lap(n, T); grow = 1.6; ng = 0
    gl = np.where(isg)[0]; sub = A[gl][:, gl]; nc, lab_ = connected_components(sub, directed=False)
    for c in range(nc):
        gv = gl[lab_ == c]
        if len(gv) < 12: continue
        nb = np.unique(A[gv].indices); base = nb[~isg[nb]]
        if len(base) == 0: continue
        root = P2[base].mean(0); dskin, _ = cKDTree(P[~isg]).query(P[gv]); k = ss((dskin - 0.012) / 0.05)   # lying on the skin: stays
        P2[gv] = P2[gv] + (P2[gv] - root) * (grow - 1) * k[:, None]; ng += 1
    print(f'  {ng} gill parts grown x{grow}')
    if show:
        np.savez(O + 'crawl_head.npz', P=P2, T=T, src=src, Cc=Cc, R=R)
        class MM: pass
        mm = MM(); mm.T = T; write_view(O + 'www/rb/', 'headm', mm, P2)
        Pst_v = Pst; mm2 = MM(); mm2.T = Ts; write_view(O + 'www/rb/', 'standshell', mm2, Pst_v)
    return P2
if __name__ == '__main__': main()
