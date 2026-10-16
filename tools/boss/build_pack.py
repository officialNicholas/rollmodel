#!/usr/bin/env python3
"""The boss model, step 2: rig the owner's jellyfish (one welded mesh, no skeleton) and pack it for the game.

What it does, in order:
- welds the extracted corners by position, recomputes smooth normals (the file's are faceted in places);
- finds the parts on the one surface: the gloves by their white texture, every tube (tentacles, fingers and the thumb, the arms) by
  tracing rings of equal geodesic distance from its tip until the ring blows up where the tube joins something wider;
- builds the skeleton: a root and the bell, per arm a chain of six bones from under the bell to the wrist, the hand (the cuff rides
  on it) and three bones for each finger and the thumb, and a chain for each of the seven tentacles;
- labels every vertex with its part (geodesic regions, so an arm never takes a tentacle) and weights it along its tube's own
  bones, blended across each joint, then smoothed over the surface;
- marks how much of each vertex follows the bell's shader motion (the pulse, the skirt ripple, the wobble), and each tube's length
  coordinate and id (the tentacles' own wave in the shader);
- finds where the face's eye caps go on the bell's front, and presses the bell back under them (a sculpted lump of the dome would
  poke through an eye);
- simplifies the mesh to half for the outline and the shadow (edge collapses within each part, each kept vertex its own weights);
- fills the texture atlas's empty space (so no dark seams), paints the face patch pink and encodes it as WebP;
- writes the pack: 'RMB1', the header's length, the header (JSON), the data; raw (boss.pack) and as base64 text (boss-pack.txt).

usage: python3 -I build_pack.py <extracted dir> <out dir> [--debug <dir>] [--tex 1024]
(the extracted dir is what tools/boss/fbx_extract.mjs writes from the owner's FBX; the game's copy is game/boss-pack.txt)"""
import sys, os, io, json, math, base64, struct
import numpy as np
from PIL import Image
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

RAW, OUT = sys.argv[1], sys.argv[2]
DBG = sys.argv[sys.argv.index('--debug') + 1] if '--debug' in sys.argv else None
TEX = int(sys.argv[sys.argv.index('--tex') + 1]) if '--tex' in sys.argv else 1024
os.makedirs(OUT, exist_ok=True)
if DBG: os.makedirs(DBG, exist_ok=True)

# ---------------------------------------------------------------- the mesh, welded
Pc = np.fromfile(RAW + '/pos.f32', np.float32).reshape(-1, 3).astype(np.float64)
UVc = np.fromfile(RAW + '/uv.f32', np.float32).reshape(-1, 2).astype(np.float64)
nc = len(Pc); Tc = np.arange(nc).reshape(-1, 3)
_, first, cw = np.unique(np.round(Pc, 4), axis=0, return_index=True, return_inverse=True); cw = cw.reshape(-1)
V = Pc[first]; nv = len(V); T = cw[Tc]
keep = (T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 2] != T[:, 0]); T = T[keep]; Tc = Tc[keep]
print('corners', nc, 'welded', nv, 'tris', len(T))
E = np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1); E = np.unique(E, axis=0)
EL = np.linalg.norm(V[E[:, 0]] - V[E[:, 1]], axis=1)
G = coo_matrix((np.concatenate([EL, EL]), (np.concatenate([E[:, 0], E[:, 1]]), np.concatenate([E[:, 1], E[:, 0]]))), shape=(nv, nv)).tocsr()
def geo(src, limit=np.inf):
    return dijkstra(G, directed=False, indices=np.atleast_1d(src), limit=limit, min_only=True)
def smooth_vals(x, iters, mask=None, k=0.5):
    """average a per-vertex array with its neighbours (over the welded surface), optionally only where mask is set"""
    deg = np.asarray(G.astype(bool).sum(1)).ravel().astype(np.float64); A = G.astype(bool).astype(np.float64)
    for _ in range(iters):
        nb = (A @ x) / np.maximum(deg, 1)[:, None] if x.ndim == 2 else (A @ x) / np.maximum(deg, 1)
        y = x * (1 - k) + nb * k
        x = np.where(mask[:, None], y, x) if (mask is not None and x.ndim == 2) else (np.where(mask, y, x) if mask is not None else y)
    return x

# smooth normals over the welded surface (angle weighted)
def vnormals(V, T):
    N = np.zeros_like(V)
    for k in range(3):
        a, b, c = V[T[:, k]], V[T[:, (k + 1) % 3]], V[T[:, (k + 2) % 3]]
        e1, e2 = b - a, c - a; fn = np.cross(e1, e2)
        ang = np.arccos(np.clip((e1 * e2).sum(1) / np.maximum(1e-12, np.linalg.norm(e1, axis=1) * np.linalg.norm(e2, axis=1)), -1, 1))
        np.add.at(N, T[:, k], fn / np.maximum(1e-12, np.linalg.norm(fn, axis=1))[:, None] * ang[:, None])
    return N / np.maximum(1e-12, np.linalg.norm(N, axis=1))[:, None]
NV = vnormals(V, T)

# texture colour per vertex (the 4096 base map), and the gloves: white islands
base = Image.open(RAW + '/base.png').convert('RGB'); BW, BH = base.size
bA = np.asarray(base).astype(np.float64) / 255
px = np.clip((UVc[:, 0] * BW).astype(int), 0, BW - 1); py = np.clip(((1 - UVc[:, 1]) * BH).astype(int), 0, BH - 1)
vc = np.zeros((nv, 3)); cnt = np.zeros(nv); np.add.at(vc, cw, bA[py, px]); np.add.at(cnt, cw, 1); vc /= np.maximum(cnt, 1)[:, None]
mxc, mnc = vc.max(1), vc.min(1); glove = (mxc > 0.72) & ((mxc - mnc) / np.maximum(mxc, 1e-6) < 0.2)
glove = smooth_vals(glove.astype(np.float64), 3) > 0.5

# ---------------------------------------------------------------- where things are (in the file's units; front is +z, up is +y)
band = (V[:, 1] > 30) & (V[:, 1] < 50)                            # (the skirt: above the arms' tops, below the dome's shoulder)
AX = np.array([(V[band, 0].min() + V[band, 0].max()) / 2, 0, (V[band, 2].min() + V[band, 2].max()) / 2])   # the bell's axis (x, z)
RIM_R = np.percentile(np.hypot(V[band, 0] - AX[0], V[band, 2] - AX[2]), 99.5)
Y_TOP = V[:, 1].max()
Y0 = 55.0                                                           # the pivot: the bell's middle, at the cavity's ceiling
BELL_W = 4.4                                                        # the bell's width in game units at scale 1
S = BELL_W / (2 * RIM_R)
C0 = np.array([AX[0], Y0, AX[2]])
print('bell axis', AX.round(2), 'rim radius', round(RIM_R, 2), 'top', round(Y_TOP, 2), 'scale', round(S, 5))
def near(p): return int(np.argmin(np.linalg.norm(V - np.array(p), axis=1)))

# ---------------------------------------------------------------- tubes: rings of equal geodesic distance
def rings(D, step, lo, hi):
    a, b = E[:, 0], E[:, 1]; da, db = D[a], D[b]; out = []; lv = lo + step * 0.5
    while lv < hi:
        m = np.isfinite(da) & np.isfinite(db) & (np.minimum(da, db) < lv) & (np.maximum(da, db) >= lv)
        if m.sum() < 3: break
        t = ((lv - da[m]) / (db[m] - da[m]))[:, None]; p = V[a[m]] * (1 - t) + V[b[m]] * t
        c = p.mean(0); out.append((lv, c, float(np.linalg.norm(p - c, axis=1).mean())))
        lv += step
    return out
def polyline(pts, n=64):
    """resample a polyline (list of points) to n points evenly by arc length, after a light smoothing"""
    P = np.array(pts, np.float64)
    for _ in range(3):
        Q = P.copy(); Q[1:-1] = P[1:-1] * 0.5 + (P[:-2] + P[2:]) * 0.25; P = Q
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], n); return np.stack([np.interp(t, s, P[:, k]) for k in range(3)], 1), s[-1]

# the tentacles: [name, tip, geodesic length to the root, bones]
TENT = [['tS', (-19.8, -74.6, -55.6), 112, 6], ['tR', (20.6, -50.6, -17.4), 116, 6], ['tL', (-26.9, -47.7, -10.4), 112, 6],
        ['tB', (5.6, -23.3, -49.4), 44, 3], ['tBL', (-16.0, -21.2, -61.2), 59, 4], ['tSL', (-39.8, -4.4, -37.2), 46, 3], ['tSR', (37.0, -16.6, -37.5), 35, 3]]
# the digits: per hand (R is +x, the boss's left), thumb then the three fingers, by their tips
# (L and R are the boss's own hands: it faces +z, so its left hand is on the +x side)
DIG = {'L': [['thumb', (29.9, -53.4, 47.9)], ['index', (36.4, -83.7, 68.3)], ['middle', (62.8, -94.9, 76.8)], ['pinky', (86.9, -81.3, 72.1)]],
       'R': [['thumb', (-33.2, -51.6, 54.3)], ['index', (-44.5, -77.7, 66.3)], ['middle', (-70.9, -84.2, 66.8)], ['pinky', (-88.4, -70.4, 62.7)]]}
ARM = {'R': {'wrist': 50.0, 'root': 140.0}, 'L': {'wrist': 50.0, 'root': 140.0}}

tubes = []   # dict: name, kind, side, cl (centerline root->tip, 64 pts), len, region mask, D (geodesic from the tip/source), rad (per cl pt)
for name, tip, L, nb in TENT:
    t = near(tip); D = geo(t, L + 40); R = rings(D, 1.5, 0, L)
    cl, ln = polyline([V[t]] + [r[1] for r in R]); cl = cl[::-1]   # (root -> tip)
    rad = np.interp(np.linspace(ln, 0, 64), [r[0] for r in R], [r[2] for r in R])
    tubes.append({'name': name, 'kind': 'tent', 'side': '', 'cl': cl, 'len': ln, 'D': D, 'Lgeo': L, 'nb': nb, 'rad': rad, 'tip': t})
gl_side = {s: np.where(glove & (np.sign(V[:, 0]) == (1 if s == 'L' else -1)))[0] for s in 'RL'}
for side in 'RL':
    # the digits: from the tip until the ring grows past 1.22 x its usual radius (the knuckle)
    for name, tip in DIG[side]:
        t = near(tip); D = geo(t, 80); R = rings(D, 1.0, 0, 60)
        r = np.array([x[2] for x in R]); lv = np.array([x[0] for x in R]); ref = np.median(r[(lv > 8) & (lv < 22)])
        j = next(k for k in range(len(R)) if lv[k] > 18 and r[k] > 1.22 * ref and r[min(k + 2, len(r) - 1)] > 1.22 * ref)
        L = float(lv[j]); cl, ln = polyline([V[t]] + [x[1] for x in R[:j + 1]]); cl = cl[::-1]
        tubes.append({'name': name, 'kind': 'digit', 'side': side, 'cl': cl, 'len': ln, 'D': D, 'Lgeo': L, 'nb': 3, 'rad': np.full(64, ref), 'tip': t})
    # the arm: rings from the glove up to its root under the bell
    D = geo(gl_side[side], 400); A = ARM[side]; R = rings(D, 2.0, 0, A['root'])
    cl, ln = polyline([x[1] for x in R if x[0] >= A['wrist'] - 1][::-1])     # root -> wrist
    rad = np.interp(np.linspace(A['root'], A['wrist'], 64), [x[0] for x in R], [x[2] for x in R])
    tubes.append({'name': 'arm', 'kind': 'arm', 'side': side, 'cl': cl, 'len': ln, 'D': D, 'Lgeo': A['root'], 'nb': 6, 'rad': rad,
                  'wristD': A['wrist'], 'neck': [x for x in R if x[0] < 6]})
for tb in tubes: print('%-6s %-4s %s len %.1f geo %.1f root %s' % (tb['kind'], tb['name'], tb['side'], tb['len'], tb['Lgeo'], tb['cl'][0].round(1)))

# ---------------------------------------------------------------- the hands: palm centre, palm normal, wrist
HAND = {}
for side in 'RL':
    digs = [tb for tb in tubes if tb['kind'] == 'digit' and tb['side'] == side]; arm = next(tb for tb in tubes if tb['kind'] == 'arm' and tb['side'] == side)
    knuck = np.array([tb['cl'][0] for tb in digs]); wrist = arm['cl'][-1]
    palm_c = knuck[1:].mean(0) * 0.75 + wrist * 0.25          # (between the knuckles and the wrist, toward the knuckles)
    g = V[gl_side[side]]; c = g.mean(0); u, s_, vt = np.linalg.svd(g - c, full_matrices=False); nrm = vt[2]
    fwd = knuck[1:].mean(0) - wrist; fwd /= np.linalg.norm(fwd); nrm = nrm - fwd * nrm.dot(fwd); nrm /= np.linalg.norm(nrm)
    # the palm faces down and back: with the fingers forward and the thumb on the inner side, that's the hand's own handedness
    # (for a left hand, forward x palm points away from the thumb)
    if nrm[1] > 0: nrm = -nrm
    side_k = np.cross(fwd, nrm).dot(digs[0]['cl'][-1] - palm_c)
    print('  handedness check', side, 'ok' if (side_k < 0) == (side == 'L') else 'MIRRORED')
    HAND[side] = {'palm': palm_c, 'n': nrm, 'fwd': fwd, 'wrist': wrist}
    print('hand', side, 'palm', palm_c.round(1), 'normal', nrm.round(3), 'fwd', fwd.round(3), 'wrist', wrist.round(1))

# ---------------------------------------------------------------- the skeleton (in the file's units; converted at the end)
bones = []
def frame(y, zhint):
    y = y / np.linalg.norm(y); z = zhint - y * zhint.dot(y)
    if np.linalg.norm(z) < 1e-6: z = np.array([1.0, 0, 0]) - y * y[0]
    z /= np.linalg.norm(z); x = np.cross(y, z); return np.stack([x, y, z], 1)
def add(name, parent, head, tail, zhint):
    R = frame(np.asarray(tail, float) - np.asarray(head, float), np.asarray(zhint, float))
    bones.append({'name': name, 'parent': parent, 'head': np.asarray(head, float), 'tail': np.asarray(tail, float), 'R': R}); return len(bones) - 1
def bidx(name): return next(i for i, b in enumerate(bones) if b['name'] == name)
def transport(Rprev, ynew):
    """the frame carried along a curve: the previous frame's z made perpendicular to the new direction"""
    return Rprev[:, 2]
add('root', None, C0, C0 + [0, 30, 0], [0, 0, 1]); add('bell', 'root', C0, C0 + [0, 30, 0], [0, 0, 1])
def chain(prefix, parent, cl, ln, nb, fr, zhint):
    """nb bones over the centerline at arc fractions fr (len nb+1, 0 root .. 1 tip)"""
    seg = np.linalg.norm(np.diff(cl, axis=0), axis=1); s = np.concatenate([[0], np.cumsum(seg)])
    J = np.stack([np.interp(np.array(fr) * s[-1], s, cl[:, k]) for k in range(3)], 1)
    ids = []; z = np.asarray(zhint, float); par = parent
    for k in range(nb):
        i = add('%s%d' % (prefix, k), par, J[k], J[k + 1], z); z = bones[i]['R'][:, 2]; ids.append(i); par = bones[i]['name']
    return ids, J, np.array(fr) * s[-1]
for tb in tubes:
    if tb['kind'] == 'tent':
        nb = tb['nb']; fr = np.linspace(0, 1, nb + 1) ** 0.92 if nb > 3 else np.linspace(0, 1, nb + 1)
        tb['bones'], tb['J'], tb['Js'] = chain(tb['name'] + '_', 'bell', tb['cl'], tb['len'], nb, fr, [0, 0, 1])
for side in 'RL':
    arm = next(tb for tb in tubes if tb['kind'] == 'arm' and tb['side'] == side); H = HAND[side]
    arm['bones'], arm['J'], arm['Js'] = chain('arm%s_' % side, 'bell', arm['cl'], arm['len'], 6, np.linspace(0, 1, 7), [0, 1, 0])
    hand = add('hand' + side, 'arm%s_5' % side, H['wrist'], H['palm'], H['n'])
    neck = np.array([x[1] for x in arm['neck']]).mean(0) if arm['neck'] else H['wrist'] + (H['palm'] - H['wrist']) * 0.3
    add('cuff' + side, 'hand' + side, H['wrist'], neck, H['n'])
    for tb in [t for t in tubes if t['kind'] == 'digit' and t['side'] == side]:
        tb['bones'], tb['J'], tb['Js'] = chain('%s%s_' % (tb['name'], side), 'hand' + side, tb['cl'], tb['len'], 3, [0, 0.4, 0.72, 1.0], H['n'])
print('bones', len(bones))

# ---------------------------------------------------------------- parts: geodesic regions
label = np.full(nv, -1)       # -1 bell; otherwise an index into tubes; palms are -2 (R) / -3 (L)
for i, tb in enumerate(tubes):
    if tb['kind'] == 'tent': m = (tb['D'] <= tb['Lgeo']) & ~glove
    elif tb['kind'] == 'digit': m = (tb['D'] <= tb['Lgeo'] + 1.0) & glove
    else: m = (tb['D'] <= tb['Lgeo']) & ~glove
    free = m & (label == -1); label[free] = i
    clash = m & (label >= 0) & (label != i)
    if clash.any():   # (two tubes reach the same vertex: the nearer tip wins)
        for v in np.where(clash)[0]:
            j = label[v]
            if tb['D'][v] < tubes[j]['D'][v]: label[v] = i
for side, code in (('R', -2), ('L', -3)): label[gl_side[side][label[gl_side[side]] == -1]] = code
for i, tb in enumerate(tubes): print('  part %-6s %-4s %s  verts %d' % (tb['kind'], tb['name'], tb['side'], (label == i).sum()))
print('  palms', (label == -2).sum(), (label == -3).sum(), ' bell', (label == -1).sum())

# ---------------------------------------------------------------- weights
W = np.zeros((nv, len(bones)))
bell_i, root_i = bidx('bell'), bidx('root')
def proj(points, cl):
    """arc length of each point's nearest spot on the polyline (and its distance to it)"""
    seg = cl[1:] - cl[:-1]; sl = np.linalg.norm(seg, axis=1); s0 = np.concatenate([[0], np.cumsum(sl)])
    best = np.full(len(points), np.inf); bs = np.zeros(len(points))
    for k in range(len(seg)):
        t = np.clip(((points - cl[k]) @ seg[k]) / max(sl[k] ** 2, 1e-12), 0, 1); q = cl[k] + t[:, None] * seg[k]
        d = np.linalg.norm(points - q, axis=1); u = d < best; best[u] = d[u]; bs[u] = s0[k] + t[u] * sl[k]
    return bs, best
def ss(e0, e1, x): t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
for i, tb in enumerate(tubes):
    m = np.where(label == i)[0]
    if not len(m): continue
    s, _ = proj(V[m], tb['cl']); tb['s'] = (m, s)
    Js, ids = tb['Js'], tb['bones']; rad = float(np.median(tb['rad']))
    w = np.zeros((len(m), len(bones)))
    # bone k covers [Js[k], Js[k+1]]; across each inner joint a smooth hand-over, as wide as the tube is thick (capped by the bones' lengths)
    seg_owner = np.clip(np.searchsorted(Js, s, side='right') - 1, 0, len(ids) - 1)
    w[np.arange(len(m)), np.array(ids)[seg_owner]] = 1
    for k in range(1, len(ids)):
        hw = min(0.9 * rad, 0.45 * (Js[k] - Js[k - 1]), 0.45 * (Js[k + 1] - Js[k]))
        t = ss(Js[k] - hw, Js[k] + hw, s); near_ = np.abs(s - Js[k]) < hw
        w[near_, ids[k - 1]] = 1 - t[near_]; w[near_, ids[k]] = t[near_]
        for j in range(len(ids)):
            if j not in (k - 1, k): w[near_, ids[j]] = 0
    # into the parent at the root: the bell for tentacles and arms, the hand for the digits
    par = bidx('hand' + tb['side']) if tb['kind'] == 'digit' else bell_i
    hw0 = (0.8 if tb['kind'] == 'digit' else 1.2) * rad
    t = ss(0, hw0, s); w *= t[:, None]; w[:, par] += 1 - t
    W[m] = w
for side, code in (('R', -2), ('L', -3)):
    m = label == code; W[m, bidx('hand' + side)] = 1
    # the cuff: the arm's last stretch (from the glove up to the wrist joint) rides on the cuff bone, which rides on the hand
    arm = next(tb for tb in tubes if tb['kind'] == 'arm' and tb['side'] == side)
    am = np.where((arm['D'] < arm['wristD'] + 1.5) & ~glove & (label == tubes.index(arm)))[0]
    W[am] = 0; W[am, bidx('cuff' + side)] = 1; label[am] = -4 if side == 'R' else -5
    # the wrist joint: from the top of the cuff rings onto the arm's last bone
    ai = tubes.index(arm); mi, si = arm['s']; top = arm['len']
    k = (si > top - 9)
    t = ss(top - 9, top - 1.5, si[k]); idx = mi[k]
    Wc = W[idx].copy() * (1 - t)[:, None]; Wc[:, bidx('cuff' + side)] += t; W[idx] = Wc
W[label == -1, bell_i] = 1
# smoothing across the part seams (a few passes of neighbour averaging where the weights change), then the four strongest, normalized
seam = np.zeros(nv, bool)
for a, b in E:
    if np.abs(W[a] - W[b]).max() > 0.3: seam[a] = seam[b] = True
seam = smooth_vals(seam.astype(np.float64), 2) > 0.01
W = smooth_vals(W, 4, seam, 0.5)
order = np.argsort(-W, axis=1)[:, :4]; Wt = np.take_along_axis(W, order, 1); Wt /= Wt.sum(1, keepdims=True)
print('max influences used', (Wt > 0.01).sum(1).max())

# ---------------------------------------------------------------- extras: the bell's share of the shader motion, the tube coordinate, the part
info = np.zeros((nv, 4))
info[:, 0] = W[:, bell_i] + W[:, root_i]
for i, tb in enumerate(tubes):
    if 's' not in tb: continue
    m, s = tb['s']
    if tb['kind'] == 'tent': info[m, 1] = np.clip(s / tb['len'], 0, 1); info[m, 2] = (TENT.index(next(x for x in TENT if x[0] == tb['name'])) + 1) / 16
    if tb['kind'] == 'arm': info[m, 1] = np.clip(s / tb['len'], 0, 1); info[m, 2] = (9 if tb['side'] == 'L' else 10) / 16
# part: 0 bell outside, 1 bell underside, 2 tentacle, 3 arm, 4 cuff, 5 glove
part = np.zeros(nv, int)
outer = (label == -1) & (((V - [AX[0], 20, AX[2]]) * NV).sum(1) > 0) & (V[:, 1] > 15)
part[(label == -1) & ~outer] = 1
for i, tb in enumerate(tubes):
    part[label == i] = 2 if tb['kind'] == 'tent' else 3 if tb['kind'] == 'arm' else 5
part[(label == -4) | (label == -5)] = 4; part[glove] = 5
info[:, 3] = part / 8.0

# ---------------------------------------------------------------- the face: anchors on the front of the bell (eyes and brows)
def ray_front(x, y):
    """the outermost surface point on the bell's front at (x, y): a ray from far in front, back along -z"""
    o = np.array([x, y, 300.0]); d = np.array([0, 0, -1.0]); best = None
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    e1, e2 = b - a, c - a; pv = np.cross(d, e2); det = (e1 * pv).sum(1); ok = np.abs(det) > 1e-9
    inv_ = np.where(ok, 1 / np.where(ok, det, 1), 0); tv = o - a; u = (tv * pv).sum(1) * inv_; qv = np.cross(tv, e1); v = (qv * d).sum(1) * inv_; t = (e2 * qv).sum(1) * inv_
    hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 0)
    k = np.where(hit)[0][np.argmin(t[hit])]; p = o + d * t[k]
    w = np.array([1 - u[k] - v[k], u[k], v[k]]); n = (NV[T[k]] * w[:, None]).sum(0); n /= np.linalg.norm(n)
    return p, n
def disc_normal(p):
    # (the dome's own outward direction from its middle: the sculpted lumps on its face would tilt a surface normal every which way)
    n = p - np.array([AX[0], 40.0, AX[2]]); return n / np.linalg.norm(n)
FACE = {}
EYE_X, EYE_Y, BROW_Y = 15.5, 45.0, 57.0
for nm, x, y in (('eye', EYE_X, EYE_Y), ('brow', EYE_X * 1.05, BROW_Y), ('mid', 0.0, EYE_Y)):
    pa, _ = ray_front(AX[0] + x, y); pb, _ = ray_front(AX[0] - x, y)
    na, nb_ = disc_normal(pa), disc_normal(pb)
    z = (pa[2] + pb[2]) / 2; n = np.array([(na[0] - nb_[0]) / 2, (na[1] + nb_[1]) / 2, (na[2] + nb_[2]) / 2]); n /= np.linalg.norm(n)
    if x == 0: FACE[nm] = (np.array([AX[0], y, z]), np.array([0, n[1], n[2]]) / np.linalg.norm([0, n[1], n[2]]))
    else:
        FACE[nm + 'L'] = (np.array([AX[0] + x, y, z]), n); FACE[nm + 'R'] = (np.array([AX[0] - x, y, z]), n * [-1, 1, 1])
for k, v in FACE.items(): print('face', k, v[0].round(2), v[1].round(3))
# the eyes are caps laid on the bell (in the runtime): where a sculpted lump of the dome would poke through one, the bell's surface is
# pressed back under the cap (the cap hides it), so each eye sits whole. The cap: half-widths w, h and depth d (game units), its middle
# 0.82 d out from the anchor, its rim sunk 0.18 d in.
EYE_W, EYE_H, EYE_D = 0.42, 0.47, 0.17
moved = 0
for side in 'LR':
    p, n = FACE['eye' + side]
    ex = np.cross([0, 1.0, 0], n); ex /= np.linalg.norm(ex); ey = np.cross(n, ex)
    rel = V - p; lx, ly, lz = rel @ ex * S / EYE_W, rel @ ey * S / EYE_H, rel @ n * S
    r = np.hypot(lx, ly); m = (label == -1) & (r < 1.18) & (lz > -0.6)
    cap = (np.sqrt(np.clip(1 - np.minimum(r, 1) ** 2, 0, 1)) - 0.18) * EYE_D - 0.03   # (the cap's height there, less a margin)
    cap = np.where(r < 1, cap, -0.18 * EYE_D - 0.03 - (r - 1) * 0.5)
    push = np.where(m & (lz > cap), lz - cap, 0) * (1 - np.clip((r - 1.0) / 0.18, 0, 1))
    V[:] = V - (push / S)[:, None] * n[None, :]; moved += int((push > 1e-4).sum())
NV = vnormals(V, T)
print('bell pressed back under the eyes at', moved, 'vertices')

# ---------------------------------------------------------------- the texture: fill the atlas's empty space, paint the face patch, WebP
def raster_cov(N):
    """which texels of an N x N map any triangle covers (by uv), with its triangle's 3D point there (for the face patch)"""
    cov = np.zeros((N, N), bool); P3 = np.zeros((N, N, 3))
    U = UVc[Tc.reshape(-1)].reshape(-1, 3, 2) * [N, N]; U[:, :, 1] = N - U[:, :, 1]
    X3 = V[T]
    for k in range(len(U)):
        u = U[k]; x0, y0 = np.floor(u.min(0)).astype(int); x1, y1 = np.ceil(u.max(0)).astype(int)
        x0, y0 = max(x0 - 1, 0), max(y0 - 1, 0); x1, y1 = min(x1 + 1, N - 1), min(y1 + 1, N - 1)
        if x1 < x0 or y1 < y0: continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        a, b, c = u[0], u[1], u[2]; den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-12: continue
        l0 = ((b[1] - c[1]) * (gx - c[0]) + (c[0] - b[0]) * (gy - c[1])) / den; l1 = ((c[1] - a[1]) * (gx - c[0]) + (a[0] - c[0]) * (gy - c[1])) / den; l2 = 1 - l0 - l1
        e = 1.2 / max(1.0, np.abs(den) ** 0.5)
        ins = (l0 >= -e) & (l1 >= -e) & (l2 >= -e)
        cov[y0:y1 + 1, x0:x1 + 1] |= ins
        P3[y0:y1 + 1, x0:x1 + 1][ins] = (l0[ins, None] * X3[k, 0] + l1[ins, None] * X3[k, 1] + l2[ins, None] * X3[k, 2])
    return cov, P3
def push_pull(img, cov):
    """fill the uncovered texels from the covered ones: averages down a pyramid, then back up (no dark bleed at the seams)"""
    lv = [(img * cov[..., None], cov.astype(np.float64))]
    while lv[-1][1].shape[0] > 1:
        c, w = lv[-1]; h = c.shape[0] // 2
        c2 = c.reshape(h, 2, h, 2, 3).sum((1, 3)); w2 = w.reshape(h, 2, h, 2).sum((1, 3)); lv.append((c2, w2))
    fill = lv[-1][0] / np.maximum(lv[-1][1], 1e-9)[..., None]
    for c, w in lv[-2::-1]:
        up = np.repeat(np.repeat(fill, 2, 0), 2, 1); own = c / np.maximum(w, 1e-9)[..., None]
        fill = np.where((w > 0)[..., None], own, up)
    return fill
NT = 2048
cov, P3 = raster_cov(NT)
img = np.asarray(base.resize((NT, NT), Image.LANCZOS)).astype(np.float64) / 255
img = push_pull(img, cov)
# the face patch: a soft pink around the eyes (the concept's face is a lighter pink than the mottled dome)
FACE_PINK = np.array([0xF2, 0x6E, 0xC8]) / 255
mid = FACE['mid'][0]
dx = (P3[..., 0] - mid[0]) / 30.0; dy = (P3[..., 1] - (mid[1] + 3)) / 16.0; dz = np.clip((P3[..., 2] - (mid[2] - 22)) / 12.0, 0, 1)
k = np.clip(1 - np.sqrt(dx * dx + dy * dy), 0, 1); k = (k * k * (3 - 2 * k)) * dz * cov * 0.85
lum = img.mean(2, keepdims=True); pink = FACE_PINK * (0.82 + 0.3 * (lum - lum.mean()))
img = img * (1 - k[..., None]) + pink * k[..., None]
tex = Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8)).resize((TEX, TEX), Image.LANCZOS)
bio = io.BytesIO(); tex.save(bio, 'WEBP', quality=82, method=6); texb = bio.getvalue()
print('texture', TEX, len(texb), 'bytes')
if DBG: tex.save(DBG + '/tex.png')

# ---------------------------------------------------------------- the outline's own lighter mesh (and the shadow's)
# The outline (the back faces pushed out) needs the silhouette, not every detail, so it gets the mesh simplified to half: edges
# collapse onto one of their ends (so every kept vertex keeps its own weights), cheapest first by the quadric error of the planes
# round them, never across two parts (an arm stays an arm), never flipping a face or pinching the surface.
def simplify(V, T, label, target):
    nv = len(V); F = [list(f) for f in T]; alive = [True] * len(F)
    vf = [set() for _ in range(nv)]
    for i, f in enumerate(F):
        for v in f: vf[v].add(i)
    Q = np.zeros((nv, 4, 4))
    for f in F:
        a, b, c = V[f[0]], V[f[1]], V[f[2]]; n = np.cross(b - a, c - a); ar = np.linalg.norm(n)
        if ar < 1e-12: continue
        n /= ar; p = np.append(n, -n.dot(a)); K = np.outer(p, p) * ar
        for v in f: Q[v] += K
    import heapq
    def nbrs(v): return {w for fi in vf[v] for w in F[fi] if w != v}
    def cost(a, b):
        q = Q[a] + Q[b]; h = np.append(V[b], 1.0); c = float(h @ q @ h)
        return c * (1.0 if label[a] == label[b] else 1e6)
    heap = []; stamp = [0] * nv
    for a in range(nv):
        for b in nbrs(a):
            heapq.heappush(heap, (cost(a, b), a, b, 0, 0))
    nf = len(F)
    while nf > target and heap:
        c, a, b, sa, sb = heapq.heappop(heap)
        if not vf[a] or not vf[b] or sa != stamp[a] or sb != stamp[b] or b not in nbrs(a): continue
        if label[a] != label[b]: continue
        # the link condition (two shared neighbours on a closed surface), so the surface doesn't pinch
        if len(nbrs(a) & nbrs(b)) != 2: continue
        shared = [fi for fi in vf[a] if b in F[fi]]; ok = True
        for fi in vf[a]:
            if fi in shared: continue
            f = F[fi]; P0 = [V[x] for x in f]; P1 = [V[b] if x == a else V[x] for x in f]
            n0 = np.cross(P0[1] - P0[0], P0[2] - P0[0]); n1 = np.cross(P1[1] - P1[0], P1[2] - P1[0])
            l0, l1 = np.linalg.norm(n0), np.linalg.norm(n1)
            if l1 < 1e-10 or (l0 > 1e-10 and n0.dot(n1) / (l0 * l1) < 0.25): ok = False; break
        if not ok: continue
        for fi in shared: alive[fi] = False; nf -= 1; [vf[x].discard(fi) for x in F[fi]]
        for fi in list(vf[a]):
            F[fi] = [b if x == a else x for x in F[fi]]; vf[b].add(fi)
        vf[a].clear(); Q[b] += Q[a]; stamp[b] += 1
        for w in nbrs(b):
            heapq.heappush(heap, (cost(w, b), w, b, stamp[w], stamp[b])); heapq.heappush(heap, (cost(b, w), b, w, stamp[b], stamp[w]))
    Fk = np.array([F[i] for i in range(len(F)) if alive[i]]); used = np.unique(Fk); remap = -np.ones(nv, int); remap[used] = np.arange(len(used))
    return used, remap[Fk]
HV, HF = simplify(V, T, label, int(len(T) * 0.5))
print('outline mesh', len(HV), 'vertices', len(HF), 'tris')

# ---------------------------------------------------------------- vertices: one per (position, uv); everything in game units from here
key = np.concatenate([cw[:, None].astype(np.float64), np.round(UVc * 8192)], 1)
uk, vfirst, vinv = np.unique(key, axis=0, return_index=True, return_inverse=True); vinv = vinv.reshape(-1)
wid = cw[vfirst]; n = len(uk)
Pm = (V[wid] - C0) * S; Nm = NV[wid]; UVm = UVc[vfirst]
IDX = vinv[Tc].reshape(-1)
SI = order[wid].astype(np.uint8); SW = np.round(Wt[wid] * 255).astype(np.int32)
SW[:, 0] += 255 - SW.sum(1); SW = np.clip(SW, 0, 255).astype(np.uint8)
INFO = np.clip(np.round(info[wid] * 255), 0, 255).astype(np.uint8)
print('vertices', n, 'indices', len(IDX), 'tris', len(IDX) // 3)
assert n < 65536
def M(p): return ((np.asarray(p) - C0) * S).round(5).tolist()
def quat(R):
    m = R; tr = m[0, 0] + m[1, 1] + m[2, 2]
    if tr > 0: s = math.sqrt(tr + 1) * 2; w = 0.25 * s; x = (m[2, 1] - m[1, 2]) / s; y = (m[0, 2] - m[2, 0]) / s; z = (m[1, 0] - m[0, 1]) / s
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]: s = math.sqrt(1 + m[0, 0] - m[1, 1] - m[2, 2]) * 2; w = (m[2, 1] - m[1, 2]) / s; x = 0.25 * s; y = (m[0, 1] + m[1, 0]) / s; z = (m[0, 2] + m[2, 0]) / s
    elif m[1, 1] > m[2, 2]: s = math.sqrt(1 + m[1, 1] - m[0, 0] - m[2, 2]) * 2; w = (m[0, 2] - m[2, 0]) / s; x = (m[0, 1] + m[1, 0]) / s; y = 0.25 * s; z = (m[1, 2] + m[2, 1]) / s
    else: s = math.sqrt(1 + m[2, 2] - m[0, 0] - m[1, 1]) * 2; w = (m[1, 0] - m[0, 1]) / s; x = (m[0, 2] + m[2, 0]) / s; y = (m[1, 2] + m[2, 1]) / s; z = 0.25 * s
    q = np.array([x, y, z, w]); return (q / np.linalg.norm(q)).round(6).tolist()
names = [b['name'] for b in bones]
head = {'v': 1, 'n': int(n), 'ni': int(len(IDX)), 'scale': S, 'bellW': BELL_W,
        'bones': [{'name': b['name'], 'parent': b['parent'], 'pos': M(b['head']), 'end': M(b['tail']), 'q': quat(b['R'])} for b in bones],
        'tent': [{'name': tb['name'], 'bones': [names[i] for i in tb['bones']], 'len': round(tb['len'] * S, 4), 'rad': round(float(np.median(tb['rad'])) * S, 4)} for tb in tubes if tb['kind'] == 'tent'],
        'arms': {s: {'bones': [names[i] for i in next(tb for tb in tubes if tb['kind'] == 'arm' and tb['side'] == s)['bones']], 'hand': 'hand' + s, 'cuff': 'cuff' + s,
                     'digits': {tb['name']: [names[i] for i in tb['bones']] for tb in tubes if tb['kind'] == 'digit' and tb['side'] == s},
                     'palm': M(HAND[s]['palm']), 'palmN': HAND[s]['n'].round(5).tolist(), 'fwd': HAND[s]['fwd'].round(5).tolist(),
                     'rad': round(float(np.median(next(tb for tb in tubes if tb['kind'] == 'arm' and tb['side'] == s)['rad'])) * S, 4)} for s in 'RL'},
        'bell': {'yRim': round((26.0 - Y0) * S, 4), 'yTop': round((Y_TOP - Y0) * S, 4), 'rRim': round(RIM_R * S, 4), 'yCeil': round((57.0 - Y0) * S, 4)},
        'face': dict({k: {'p': M(v[0]), 'n': v[1].round(5).tolist()} for k, v in FACE.items()}, size=[EYE_W, EYE_H, EYE_D]),
        'texRes': TEX, 'texMime': 'image/webp'}
# ---------------------------------------------------------------- the pack
mn, mx = Pm.min(0), Pm.max(0); head['bbox'] = [mn.round(5).tolist(), mx.round(5).tolist()]
qp = np.round((Pm - mn) / np.maximum(mx - mn, 1e-9) * 65535).astype(np.uint16)
qn = np.zeros((n, 4), np.int8); qn[:, :3] = np.clip(np.round(Nm * 127), -127, 127)
qu = np.round(np.clip(np.stack([UVm[:, 0], 1 - UVm[:, 1]], 1), 0, 1) * 65535).astype(np.uint16)   # (v from the top row, as the game's textures)
parts = [('pos', qp.tobytes()), ('nrm', qn.tobytes()), ('uv', qu.tobytes()), ('si', SI.tobytes()), ('sw', SW.tobytes()), ('info', INFO.tobytes()), ('idx', IDX.astype(np.uint16).tobytes()), ('tex', texb)]
# the outline's mesh: its own vertices (a subset of the welded ones, each with its own weights), the same box
hP = (V[HV] - C0) * S; hq = np.round((hP - mn) / np.maximum(mx - mn, 1e-9) * 65535).astype(np.uint16)
hn_ = np.zeros((len(HV), 4), np.int8); hn_[:, :3] = np.clip(np.round(NV[HV] * 127), -127, 127)
hSW = np.round(Wt[HV] * 255).astype(np.int32); hSW[:, 0] += 255 - hSW.sum(1); hSW = np.clip(hSW, 0, 255).astype(np.uint8)
parts += [('hpos', hq.tobytes()), ('hnrm', hn_.tobytes()), ('hsi', order[HV].astype(np.uint8).tobytes()), ('hsw', hSW.tobytes()),
          ('hinfo', np.clip(np.round(info[HV] * 255), 0, 255).astype(np.uint8).tobytes()), ('hidx', HF.astype(np.uint16).reshape(-1).tobytes())]
head['hn'] = int(len(HV)); head['hni'] = int(HF.size)
blob = b''; off = {}
for k, b in parts:
    blob += b'\0' * ((-len(blob)) % 8); off[k] = len(blob); blob += b
head['off'] = off; head['texLen'] = len(texb)
hj = json.dumps(head, separators=(',', ':')).encode(); hj += b' ' * ((-(8 + len(hj))) % 8)
pack = b'RMB1' + struct.pack('<I', len(hj)) + hj + blob
open(OUT + '/boss.pack', 'wb').write(pack); b64 = base64.b64encode(pack).decode(); open(OUT + '/boss-pack.txt', 'w').write(b64)
print('pack', len(pack), 'bytes;', len(b64), 'as text')
if DBG:
    np.save(DBG + '/label.npy', label); np.save(DBG + '/V.npy', V); np.save(DBG + '/part.npy', part)
    rng = np.random.default_rng(3); pal = rng.random((64, 3)) * 0.8 + 0.2
    C = np.zeros((nv, 3)); C[label == -1] = [0.35, 0.35, 0.45]; C[label == -2] = [1, 1, 1]; C[label == -3] = [0.9, 0.9, 0.7]; C[label <= -4] = [1, 0.5, 0.1]
    for i in range(len(tubes)): C[label == i] = pal[i]
    np.asarray(C[cw], np.float32).tofile(DBG + '/col_label.f32')
    dom = order[:, 0]; C2 = pal[dom % 64] * (0.4 + 0.6 * Wt[:, :1]); np.asarray(C2[cw], np.float32).tofile(DBG + '/col_bone.f32')
    json.dump({'bones': [{'name': b['name'], 'head': b['head'].tolist(), 'tail': b['tail'].tolist()} for b in bones]}, open(DBG + '/bones.json', 'w'))
