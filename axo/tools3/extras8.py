# v7 per-vertex material data and the compact runtime format for both meshes (rig7stand.py and the grafted crawl: headgraft.py).
# (extras8: as extras7, with the crawl8 rig and the head's canonical map anchored on the face centre: the two heads are one head now)
# Attributes (all quantized):
#   position  f32 x3          normal  i8 x4 (xyz, 0)        skinIndex u8 x4      skinWeight u8 x4      index u16
#   cpos      i16 x4  xyz: the vertex's place on the canonical body (the standing rest; the crawl mesh is skinned into it, so procedural
#                     patterns land on the same spots on both meshes), w: 'along', the arc coordinate down its limb / tail / stalk chain
#   jelly     u8 x4   x belly (pale ventral side), y soft (jelly layer freedom), z thin (light passes through), w head (rigid head, the face)
#   fill      u8 x4   x crawl paint-fill order, y stand paint-fill order, z ambient occlusion, w the free edge of thin parts (fin rim)
#   mat       u8 x4   x tail-fin height (0 bottom edge .. 1 top crest; 0.5 elsewhere), y gill frill, z wrinkle (joint folds), w spot density
import sys, os, json, time
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2'); sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from mesh import Mesh
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
CP_SCALE = 4.0   # cpos: i16 normalized * CP_SCALE metres
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
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
def qrot(q, v):
    u = q[..., :3]; w = q[..., 3:4]; return v + 2 * np.cross(u, np.cross(u, v) + w * v)
SRC = {'stand': ('stand8_rig.npz', 'www/s8/axo_stand.json'), 'crawl': ('crawl8_rig.npz', 'www/c8/axo_crawl.json')}
# Weight hygiene (v7): a vertex blending two bones that are not neighbours in the hierarchy (the forearm and a fingertip, the thigh and a
# toe, the spine and the thigh) collapses under dual quaternion skinning once the two turn ~180 deg apart (a fist, a tucked knee): the blend
# flips side in one frame. pairs_ref.json holds, for every pair of bones sharing a vertex, the largest relative rotation measured over every
# state, gait and transition (out/probe_pairs_json.js); an influence more than one joint away from the vertex's dominant bone (siblings
# excepted) whose pair turns past 90 deg is handed to the dominant bone's neighbour on the way to it (the fingertip's share goes to the hand,
# the toe's to the foot), so every blend stays between adjacent bones.
PAIRS = json.load(open(O + 'pairs_ref.json')) if os.path.exists(O + 'pairs_ref.json') else {}
def clean_weights(W, meta, nm, lim=90.0):
    names = [b['name'] for b in meta['bones']]; bi = {k: i for i, k in enumerate(names)}
    par = [bi[b['parent']] if b.get('parent') else -1 for b in meta['bones']]
    ang = {}
    for a, b_, mx, mm, wh in PAIRS.get(nm, []): ang[(bi[a], bi[b_])] = ang[(bi[b_], bi[a])] = mx
    def anc(i):
        out = [i]
        while par[out[-1]] >= 0: out.append(par[out[-1]])
        return out
    def path(i, j):
        A, B = anc(i), anc(j); l = next(x for x in A if x in B); return A[:A.index(l) + 1] + B[:B.index(l)][::-1]
    W = W.copy(); moved = 0; cnt = {}
    for v in np.where((W > 0).sum(1) > 1)[0]:
        d = int(np.argmax(W[v]))
        for b in np.where(W[v] > 0)[0]:
            if b == d: continue
            pth = path(d, b)
            if len(pth) <= 2 or par[b] == par[d] or ang.get((d, b), 0) <= lim: continue
            W[v, pth[1]] += W[v, b]; W[v, b] = 0; moved += 1; k = (names[d], names[b], names[pth[1]]); cnt[k] = cnt.get(k, 0) + 1
    print(f'  {nm}: weight hygiene moved {moved} influences;', ', '.join(f'{a}+{b}->{c} x{n}' for (a, b, c), n in sorted(cnt.items(), key=lambda kv: -kv[1])[:12]))
    return W
# The crawl's back behind the neck carried stray head weight (up to 0.4, a remnant of grafting the stand's head on): the upper back then
# swung with every turn of the head. Behind the neck joint and on the dorsal side the head's share is capped (smoothly, 0 a hand's width
# behind the neck), the excess handed to the neck; the throat and jaw underneath keep theirs.
def cap_crawl_nape(P, W, meta):
    names = [b['name'] for b in meta['bones']]; J = {b['name']: np.array(b['pos']) for b in meta['bones']}; hi, ni = names.index('head'), names.index('neck')
    ax = unit(J['head'] - J['chest']); dd = unit(np.cross(ax, [1.0, 0, 0])); dd = dd if dd[1] > 0 else -dd
    d = P - J['neck']; along = d @ ax; dors = d @ dd
    cap = 1 - ss((dors - 0.02) / 0.08) * (1 - ss((along + 0.10) / 0.12))
    ex = np.clip(W[:, hi] - cap, 0, None); W = W.copy(); W[:, hi] -= ex; W[:, ni] += ex
    print(f'  crawl: nape head weight capped on {int((ex > 1e-3).sum())} verts (max excess {ex.max():.2f})')
    return W
# Digit weights far from the digit: on the stand a wrist vertex carried a third of its weight on the thumb's tip bone, so a fist (the
# thumb curled 150 deg) flung it 10 cm out into a shard. A digit's share of a vertex fades with the vertex's distance from the digit's
# whole bone chain (kept within 4.5 cm, gone by 7.5 cm: the stand's digit bones do not run down the middle of the digits, so the margin is
# wide; only real strays move) and goes to the hand / the toes' base.
def seg_dist(X, a, b):
    ab = b - a; t = np.clip(((X - a) @ ab) / max(ab @ ab, 1e-12), 0, 1); return np.linalg.norm(X - (a + t[:, None] * ab), axis=1)
def digit_cap(P, W, meta, nm, r0=0.045, r1=0.075):
    names = [b['name'] for b in meta['bones']]; bi = {k: i for i, k in enumerate(names)}; B = {b['name']: b for b in meta['bones']}
    W = W.copy(); moved = 0
    for s_ in ('L', 'R'):
        for kind, root in (('finger', 'hand.' + s_), ('toe', 'toes.' + s_)):
            for k in range(4):
                b1, b2 = f'{kind}{k}.{s_}.1', f'{kind}{k}.{s_}.2'; i1, i2, ir = bi[b1], bi[b2], bi[root]
                v = np.where((W[:, i1] > 0) | (W[:, i2] > 0))[0]
                a0, a1, a2 = np.array(B[b1]['pos']), np.array(B[b2]['pos']), np.array(B[b2]['end'])
                d = np.minimum(seg_dist(P[v], a0, a1), seg_dist(P[v], a1, a2)); f = ss((d - r0) / (r1 - r0))
                for i in (i1, i2): mv = W[v, i] * f; W[v, i] -= mv; W[v, ir] += mv; moved += int((mv > 0.02).sum())
    print(f'  {nm}: digit weights far from their digit handed back on {moved} vertex-bone pairs')
    return W
# Where two parts meet in a deep fold (the armpits, the arm lying against the side; the tail's root against the seat) the weights changed
# from one part to the other within one row of triangles, so opening the fold (the elbows out akimbo, the tail curled under or down to the
# floor) stretched that single row into a white sliver. The weights there are smoothed over a few rings (the fold opens as a soft web).
def soften_folds(P, T, W, meta, nm, iters=8):
    names = [b['name'] for b in meta['bones']]; bi = {k: i for i, k in enumerate(names)}
    torso = [bi[k] for k in ('hips', 'spine', 'spine1', 'chest')]
    n = len(P); E = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); E = np.unique(np.sort(E, 1), axis=0)
    A = coo_matrix((np.ones(len(E) * 2), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr(); deg = np.maximum(np.asarray(A.sum(1)).ravel(), 1)
    tw = W[:, torso].sum(1); reg = np.zeros(n, bool)
    for s_ in ('L', 'R'): reg |= (W[:, bi['upperarm.' + s_]] > 0.02) & (tw > 0.02)
    reg |= (W[:, bi['tail1']] > 0.02) & (W[:, bi['hips']] > 0.02)
    for _ in range(2): reg = reg | (A @ reg.astype(float) > 0)
    W = W.copy()
    for _ in range(iters): Wn = (A @ W) / deg[:, None]; W[reg] = 0.5 * W[reg] + 0.5 * Wn[reg]
    print(f'  {nm}: weights softened across {int(reg.sum())} fold vertices (armpits, tail root)')
    return W
def load(nm):
    z = np.load(O + SRC[nm][0], allow_pickle=True); meta = json.load(open(O + SRC[nm][1]))
    W = np.zeros((len(z['P']), len(meta['bones'])))
    for c in range(4): np.add.at(W, (np.arange(len(z['P'])), z['idx'][:, c].astype(int)), z['w'][:, c])
    W = digit_cap(z['P'], W, meta, nm)
    W = clean_weights(W, meta, nm)
    if nm == 'stand': W = soften_folds(z['P'], z['T'], W, meta, nm)
    if nm == 'crawl': W = cap_crawl_nape(z['P'], W, meta)
    idx = np.argsort(-W, 1)[:, :4]; w = np.take_along_axis(W, idx, 1); w = np.clip(w, 0, None); w /= w.sum(1, keepdims=True)
    return z['P'], z['T'], W, idx.astype(np.uint8), w.astype(np.float32), meta, np.array([str(l) for l in z['labels']])
def dqs_map(P, W, maps):
    """dual-quaternion blend of per-bone rigid maps (R_b as quaternion q_b, translation t_b: p -> R p + t)"""
    q = np.array([m[0] for m in maps]); t = np.array([m[1] for m in maps])
    d = np.stack([0.5 * (q[:, 3] * t[:, 0] + t[:, 1] * q[:, 2] - t[:, 2] * q[:, 1]), 0.5 * (q[:, 3] * t[:, 1] + t[:, 2] * q[:, 0] - t[:, 0] * q[:, 2]),
                  0.5 * (q[:, 3] * t[:, 2] + t[:, 0] * q[:, 1] - t[:, 1] * q[:, 0]), -0.5 * (t * q[:, :3]).sum(1)], 1)
    dom = np.argmax(W, 1); sgn = np.sign((q[None, :, :] * q[dom][:, None, :]).sum(2)); sgn[sgn == 0] = 1
    Wq = W * sgn; br = Wq @ q; bd = Wq @ d; l = np.linalg.norm(br, axis=1, keepdims=True); br /= l; bd /= l
    Pr = qrot(br, P); tr = 2 * (br[:, 3:4] * bd[:, :3] - bd[:, 3:4] * br[:, :3] + np.cross(br[:, :3], bd[:, :3]))
    return Pr + tr, br
def smooth_scalar(m, x, iters=3, lam=0.5):
    E = m.E; n = m.n; A = coo_matrix((np.ones(2 * len(E)), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr(); deg = np.maximum(np.asarray(A.sum(1)).ravel(), 1)
    x = x.astype(float).copy()
    for _ in range(iters): x = (1 - lam) * x + lam * (A @ x) / deg
    return x
def thickness(P, N, T, maxd=0.12):
    """distance from each vertex to the surface behind it (along -normal): ray / triangle intersection against nearby triangles"""
    c = P[T].mean(1); kd = cKDTree(c); out = np.full(len(P), maxd)
    A, B, C = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]; e1 = B - A; e2 = C - A
    for i in range(len(P)):
        o = P[i] + N[i] * -1e-4; dvec = -N[i]; cand = kd.query_ball_point(o + dvec * maxd * 0.5, maxd * 0.75)
        if not cand: continue
        cand = np.array(cand); h = np.cross(dvec, e2[cand]); a = (e1[cand] * h).sum(1); ok = np.abs(a) > 1e-12; f = np.zeros_like(a); f[ok] = 1 / a[ok]
        s = o - A[cand]; u = f * (s * h).sum(1); qv = np.cross(s, e1[cand]); v = f * (qv * dvec).sum(1); t = f * (qv * e2[cand]).sum(1)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 2e-4) & (t < maxd)
        if hit.any(): out[i] = t[hit].min()
    return out
def ambient_occlusion(P, N, r=0.1):
    tree = cKDTree(P); occ = np.zeros(len(P)); pairs = tree.query_pairs(r, output_type='ndarray')
    d = P[pairs[:, 1]] - P[pairs[:, 0]]; L = np.linalg.norm(d, axis=1) + 1e-9; dh = d / L[:, None]; fall = (1 - L / r)
    for a, b, sgn in ((pairs[:, 0], pairs[:, 1], 1), (pairs[:, 1], pairs[:, 0], -1)):
        up = np.clip(np.einsum('ij,ij->i', N[a], dh * sgn), 0, 1); num = np.zeros(len(P)); den = np.zeros(len(P))
        np.add.at(num, a, up * fall); np.add.at(den, a, fall); occ += num / np.maximum(den, 1e-9)
    return np.clip(occ * 0.9, 0, 1)
CHAINS = [['hips', 'tail1', 'tail2', 'tail3', 'tail4', 'tail5', 'tail6'], ['hips', 'spine', 'spine1', 'chest', 'neck', 'head', 'headfront']]
for s in 'LR':
    CHAINS += [[f'shoulder.{s}', f'upperarm.{s}', f'forearm.{s}', f'hand.{s}'], [f'thigh.{s}', f'shin.{s}', f'foot.{s}', f'toes.{s}']]
    for k in range(4): CHAINS += [[f'hand.{s}', f'finger{k}.{s}.1', f'finger{k}.{s}.2'], [f'toes.{s}', f'toe{k}.{s}.1', f'toe{k}.{s}.2']]
    for k in range(3): CHAINS += [[f'head', f'gill{k}.{s}.1', f'gill{k}.{s}.2']]
def build(nm, cano):
    t0 = time.time(); P, T, W, idx, w, meta, labels = load(nm); names = [b['name'] for b in meta['bones']]; bi = {k: i for i, k in enumerate(names)}
    m = Mesh(P, T); N = m.N; n = len(P)
    Fm = [qmat(b['q']) for b in meta['bones']]; Jm = np.array([b['pos'] for b in meta['bones']])
    Fc = [qmat(b['q']) for b in cano['bones']]; Jc = np.array([b['pos'] for b in cano['bones']])
    # 1. the canonical place (the standing rest): each bone's rest frame onto the stand's rest frame, dual-quaternion blended
    maps = []
    fcm, fcc = np.array(meta['face']['c']), np.array(cano['face']['c'])
    for i in range(len(names)):
        R = Fc[i] @ Fm[i].T
        if names[i] in ('head', 'headfront'): maps.append((mat2quat(R), fcc - R @ fcm))   # the face centre onto the face centre
        else: maps.append((mat2quat(R), Jc[i] - R @ Jm[i]))
    cp, br = dqs_map(P, W, maps); cn = unit(qrot(br, N))
    # 'along': arc coordinate down each chain in canonical space (continuous across the chain's joints), blended by the weights
    endc = {b['name']: np.array(b['end']) for b in cano['bones']}; along_b = np.zeros(len(names)); axis_b = np.zeros((len(names), 3)); seen = set()
    for ch in CHAINS:
        acc = along_b[bi[ch[0]]] if ch[0] in seen else 0.0
        for j, k in enumerate(ch):
            if j > 0: acc += np.linalg.norm(Jc[bi[k]] - Jc[bi[ch[j - 1]]])
            if k not in seen:
                along_b[bi[k]] = acc; nxt = Jc[bi[ch[j + 1]]] if j + 1 < len(ch) else endc[k]; axis_b[bi[k]] = unit(nxt - Jc[bi[k]]); seen.add(k)
    for i, k in enumerate(names):
        if k not in seen: axis_b[i] = unit(endc[k] - Jc[i]); along_b[i] = 0.0
    along_v = np.stack([along_b[b] + ((cp - Jc[b]) * axis_b[b]).sum(1) for b in range(len(names))], 1)
    along = (W * along_v).sum(1)
    # 2. regions from the weights
    wsum = lambda pre: np.clip(sum(W[:, bi[k]] for k in names if k.startswith(pre)), 0, 1)
    head = np.clip(W[:, bi['head']] + W[:, bi['headfront']] + wsum('gill'), 0, 1); gillW = wsum('gill')
    digit = np.clip(sum(W[:, bi[k]] for k in names if k.startswith('finger') or (k.startswith('toe') and not k.startswith('toes'))), 0, 1)
    tailW = wsum('tail'); limbW = np.clip(sum(W[:, bi[k]] for k in names if k.startswith(('upperarm', 'forearm', 'hand', 'thigh', 'shin', 'foot', 'toes'))), 0, 1)
    trunkW = np.clip(W[:, bi['hips']] + W[:, bi['spine']] + W[:, bi['spine1']] + W[:, bi['chest']] + W[:, bi['neck']] + 0.0, 0, 1)
    # 3. belly: the side facing each bone's ventral axis (canonical Z), strongest on the trunk, the throat and under the tail's root; mild on limbs
    Zc = np.array([Fc[i][:, 2] for i in range(len(names))]); vz = unit(W @ Zc); vent = (cn * vz).sum(1)
    headC = Jc[bi['head']]; chin = (cp[:, 1] < headC[1] - 0.05) * ss((headC[1] - 0.05 - cp[:, 1]) / 0.12)
    belly = ss((vent + 0.05) / 0.6) * np.clip(trunkW + 0.8 * W[:, bi['tail1']] + 0.4 * W[:, bi['tail2']] + 0.45 * limbW, 0, 1) * (1 - gillW)
    belly = np.maximum(belly, 0.85 * chin * np.clip(W[:, bi['head']] + W[:, bi['neck']], 0, 1) * (1 - gillW) * ss((-cn[:, 1] + 0.2) / 0.6))
    belly = np.clip(smooth_scalar(m, belly, 3) * 1.1, 0, 1)
    soft = np.clip(1 - head, 0, 1) * (1 - 0.5 * digit)
    # 4. thin parts: thickness behind the surface (fin, frills, toe webs)
    th = thickness(P, N, T); thin = 1 - ss((th - 0.012) / 0.045); thin = np.clip(smooth_scalar(m, thin, 2), 0, 1)
    # the free edge of a thin part (fin rim, frill edges): within a thin region, where the normals turn sharply over a short distance
    # (the rim: the surface folds over within one or two edges there; on a thin part's flat sides neighbouring normals agree)
    e_ = m.E; dots = (N[e_[:, 0]] * N[e_[:, 1]]).sum(1); mind = np.ones(n); np.minimum.at(mind, e_[:, 0], dots); np.minimum.at(mind, e_[:, 1], dots)
    edge = ss((0.55 - mind) / 0.6) * ss((thin - 0.3) / 0.4); edge = np.clip(smooth_scalar(m, edge, 1) * 1.3, 0, 1)
    # 5. occlusion
    ao = smooth_scalar(m, ambient_occlusion(P, N, r=0.1), 1)
    # 6. tail fin height (canonical: per slab along the tail, 0 bottom .. 1 top), 0.5 off the tail
    finh = np.full(n, 0.5); tv = tailW > 0.3
    if tv.any():
        zz = cp[tv, 2]; yy = cp[tv, 1]; bins = np.linspace(zz.min() - 1e-6, zz.max() + 1e-6, 40); lo = np.zeros(len(bins) - 1); hi = np.zeros(len(bins) - 1)
        for k in range(len(bins) - 1):
            s_ = (zz >= bins[k]) & (zz < bins[k + 1]); lo[k], hi[k] = (yy[s_].min(), yy[s_].max()) if s_.any() else (np.nan, np.nan)
        ok = np.isfinite(lo); cz = 0.5 * (bins[1:] + bins[:-1]); lo = np.interp(cp[:, 2], cz[ok], lo[ok]); hi = np.interp(cp[:, 2], cz[ok], hi[ok])
        fh = np.clip((cp[:, 1] - lo) / np.maximum(hi - lo, 1e-3), 0, 1); k_ = ss((tailW - 0.2) / 0.5); finh = 0.5 + (fh - 0.5) * k_
    # 7. gill frill: the stalks' thin fronds (the stalk core stays skin)
    # (the frill colour on the thin frond lobes only: the stalks' rods stay spotted skin, as in the reference; v8 rigs weight the whole stalk
    # to the gill bones, so the lobes come from the label)
    fr = smooth_scalar(m, (labels == 'gill').astype(float), 2); gill = np.clip(fr * ss((thin - 0.15) / 0.5) + 0.35 * fr, 0, 1)
    # 8. wrinkles: where a limb / digit / neck joint blends two bones (4 w_a w_b), plus the knuckles' digit-hand blends
    pairs = [(bi['chest'], bi['neck']), (bi['neck'], bi['head'])]
    for ch in CHAINS:
        if ch[0] in ('hips', 'head') or ch[0].startswith('shoulder'): continue   # trunk, tail, gills: no folds; the shoulder's root neither
        for a, b in zip(ch[:-1], ch[1:]): pairs.append((bi[a], bi[b]))
    for s_ in 'LR': pairs.append((bi[f'upperarm.{s_}'], bi[f'forearm.{s_}']))
    wr = np.zeros(n)
    for a, b in pairs: wr = np.maximum(wr, 4 * W[:, a] * W[:, b])
    wr = np.clip(smooth_scalar(m, wr, 2) * 1.2, 0, 1) * (1 - gillW)
    # 9. spot density: the back and flanks, the limbs' tops and the tail's upper half; few on the belly, the face and the frills
    faceZone = W[:, bi['head']] * ss((cp[:, 2] - (headC[2] + 0.05)) / 0.15)
    spots = (1 - belly) * (1 - 0.8 * faceZone) * (1 - 0.6 * gill) * (1 - 0.5 * digit)
    spots = np.clip(smooth_scalar(m, spots, 2), 0, 1)
    # 10. paint fill orders (as v6: the crawl's from the ground contacts up, the stand's from the feet up, hands last)
    feet = (W[:, bi['foot.L']] + W[:, bi['foot.R']] + W[:, bi['toes.L']] + W[:, bi['toes.R']]) > 0.3
    hands = (W[:, bi['hand.L']] + W[:, bi['hand.R']] + sum(W[:, bi[k]] for k in names if k.startswith('finger'))) > 0.3
    src = P[:, 1] < (0.075 if nm == 'crawl' else 0.06)
    d = m.geo(np.where(src)[0], limit=6.0); d[~np.isfinite(d)] = d[np.isfinite(d)].max(); crawlO = smooth_scalar(m, d / d.max(), 2)
    standO = np.clip(cp[:, 1] / 1.78, 0, 1) + 0.3 * hands + 0.1 * (gillW > 0.3); standO = smooth_scalar(m, np.clip(standO, 0, 1.3), 2); standO /= standO.max()
    if nm == 'stand': crawlO, standO = smooth_scalar(m, np.clip(cp[:, 1] / 1.78, 0, 1), 1), standO   # (the stand mesh shows the stand order; keep both defined)
    print(f'  {nm}: belly>0.5 {int((belly > 0.5).sum())} thin>0.5 {int((thin > 0.5).sum())} edge>0.5 {int((edge > 0.5).sum())} gill>0.5 {int((gill > 0.5).sum())} wrinkle>0.3 {int((wr > 0.3).sum())} '
          f'ao p50/p99 {np.percentile(ao, 50):.2f}/{np.percentile(ao, 99):.2f}; along {along.min():.2f}..{along.max():.2f}; cpos {cp.min(0).round(2)}..{cp.max(0).round(2)} ({time.time() - t0:.1f}s)')
    return dict(P=P, N=N, T=T, idx=idx, w=w, cp=cp, along=along, jelly=np.stack([belly, soft, thin, head], 1), fill=np.stack([crawlO, standO, ao, edge], 1),
                mat=np.stack([finh, gill, wr, spots], 1), meta=meta)
def export(nm, d, out):
    q8 = lambda a: np.clip(np.round(np.asarray(a) * 255), 0, 255).astype(np.uint8)
    n = len(d['P']); Nq = np.zeros((n, 4), np.int8); Nq[:, :3] = np.clip(np.round(d['N'] * 127), -127, 127).astype(np.int8)
    wq = np.round(d['w'] * 255).astype(np.int32); wq[:, 0] += 255 - wq.sum(1); wq = np.clip(wq, 0, 255).astype(np.uint8)
    cq = np.zeros((n, 4), np.int16); cq[:, :3] = np.clip(np.round(d['cp'] / CP_SCALE * 32767), -32767, 32767); cq[:, 3] = np.clip(np.round(d['along'] / CP_SCALE * 32767), -32767, 32767)
    parts = [('position', d['P'].astype(np.float32)), ('normal', Nq), ('skinIndex', d['idx'].astype(np.uint8)), ('skinWeight', wq), ('index', d['T'].astype(np.uint16).ravel()),
             ('cpos', cq), ('jelly', q8(d['jelly'])), ('fill', q8(d['fill'])), ('mat', q8(d['mat']))]
    off = {}; o = 0; blobs = []
    for k, a in parts:
        b = a.tobytes(); off[k] = o; blobs.append((o, b)); o += len(b); o += (-o) % 4
    buf = bytearray(o)
    for of, b in blobs: buf[of:of + len(b)] = b
    meta = dict(d['meta']); meta.update({'fmt': 'axo7', 'n': n, 'ni': int(d['T'].size), 'i32': False, 'off7': off, 'cpScale': CP_SCALE, 'bbox': [d['P'].min(0).round(4).tolist(), d['P'].max(0).round(4).tolist()]})
    meta.pop('off', None); meta.pop('uv16', None)
    open(out + '.bin', 'wb').write(buf); json.dump(meta, open(out + '.json', 'w'))
    print(f' {nm}: {out}.bin {len(buf)} bytes ({len(buf) / 1024:.0f} KB), {n} verts, {int(d["T"].shape[0])} tris')
if __name__ == '__main__':
    cano = json.load(open(O + 'www/s8/axo_stand.json'))
    outdir = sys.argv[1] if len(sys.argv) > 1 else O + 'www/t10/'
    os.makedirs(outdir, exist_ok=True)
    for nm in ('stand', 'crawl'):
        d = build(nm, cano); export(nm, d, outdir + f'axo_{nm}')
        np.savez(O + f'{nm}8_extras.npz', **{k: v for k, v in d.items() if k != 'meta'})
