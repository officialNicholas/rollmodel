# The final skin weights on the reposed model (game frame): bone heat over the bones that carry skin (the middle digit on finger1 / toe1,
# split with finger2 / toe2 after), then: the head made rigid (the face is drawn on it, from the rest pose), the ears hinged at their
# roots onto the head, influences cut to four and renormalized.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import boneheat as bh, meshkit as mk
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
HEAT_SKIP = ('headfront', 'gill1', 'gill2', 'finger2', 'toe2')
def heat_bones(rig):
    names = [n for n, _ in rig.order if not n.startswith(HEAT_SKIP)]; segs = []
    for n in names:
        a, b = rig.B[n]; segs.append((a, b))
    return names, segs
def compute(rig, Pw, Tw, ears=None, verbose=True):
    names_all = [n for n, _ in rig.order]; ia = {n: i for i, n in enumerate(names_all)}
    names, segs = heat_bones(rig); Nw = mk.vertex_normals(Pw, Tw)
    allowed = None
    if ears is not None:
        # the ear bones only on the ears (an ear's hinge sits by the skull: the skull's side would see it), the ears only on their own
        # bones and the head
        allowed = np.ones((len(Pw), len(names)), bool); jn = {n: j for j, n in enumerate(names)}
        for s in 'LR':
            ev = np.zeros(len(Pw), bool); ev[ears[s]['verts']] = True; g = [jn[f'gill0.{s}.1'], jn[f'gill0.{s}.2']]
            allowed[~ev][:, g] = False; allowed[np.ix_(~ev, g)] = False
            keep = np.zeros(len(names), bool); keep[g] = True; keep[jn['head']] = True; allowed[np.ix_(ev, ~keep)] = False
    Wh, near = bh.bone_heat(Pw, Tw, Nw, segs, allowed=allowed, kvis=6)
    W = np.zeros((len(Pw), len(names_all)))
    for j, n in enumerate(names): W[:, ia[n]] = Wh[:, j]
    # the middle digit: half on finger1 / toe1, half on finger2 / toe2 (their spreads cancel: it curls straight)
    for s in 'LR':
        for kind in ('finger', 'toe'):
            for seg in ('1', '2'):
                a, b = ia[f'{kind}1.{s}.{seg}'], ia[f'{kind}2.{s}.{seg}']; W[:, b] = 0.5 * W[:, a]; W[:, a] *= 0.5
    W = limb_cut(W, names_all, Pw, Tw, rig)
    W = chain_window(W, names_all, Pw, rig)
    W = root_fade(W, names_all, Pw, rig)
    W = axial_partition(W, names_all, Pw, rig)
    W = head_cut(W, names_all, Pw, rig)
    return W, names_all, near
def head_cut(W, names, P, rig, verbose=True):
    """above the neck only the neck, the head and the ears: the big head overhangs the shoulders, and over the back and sides of the skull
    (far from the head bone, near the shoulders') bone heat let the shoulders' and the chest's weight climb up, so a turn of the head left
    them behind (spikes). Past the plane square to the neck through its root, over a band, the trunk's and limbs' share goes to the neck and
    the head (more to the head the further up)"""
    ia = {n: i for i, n in enumerate(names)}; W = W.copy()
    j, e = rig.B['neck']; ax = (e - j) / np.linalg.norm(e - j); t = (P - j) @ ax
    k = ss((t - 0.03) / 0.10); kh = ss((t - 0.05) / 0.15)
    keep = [i for n, i in ia.items() if n in ('neck', 'head', 'headfront') or n.startswith('gill')]
    other = np.ones(len(names), bool); other[keep] = False
    lost = (W[:, other] * k[:, None]).sum(1); W[:, other] *= (1 - k)[:, None]
    h, nk = ia['head'], ia['neck']; hn = W[:, [h, nk]]; s_ = hn.sum(1)
    fh = np.where(s_ > 1e-6, (hn[:, 0] / np.maximum(s_, 1e-12)) * 0.5 + 0.5 * kh, kh)
    W[:, h] += lost * fh; W[:, nk] += lost * (1 - fh)
    if verbose: print(f'  head cut: {int((lost > 0.02).sum())} vertices above the neck gave their trunk / limb share to the neck and head')
    return W
def chain_window(W, names, P, rig, verbose=True):
    """each limb bone's share kept near its own segment: bone heat spreads a bone's weight a long way down a thin limb (the upper arm's
    reached the fingers), so in a deep bend (the air tuck) the hand smears with the shoulder's turn. Along the limb (the arclength of a
    vertex's nearest point on the shoulder-elbow-wrist-hand line) the upper bone's share ends a third of the way down the lower one, the
    lower one's starts a third of the way up the upper one and ends a third of the way into the hand; what is cut goes to the others there"""
    ia = {n: i for i, n in enumerate(names)}; W = W.copy(); cut = 0
    for s in 'LR':
        for up, lo, en in (('upperarm', 'forearm', 'hand'), ('thigh', 'shin', 'foot')):
            r, k = rig.B[f'{up}.{s}']; k2, w = rig.B[f'{lo}.{s}']; w2, e = rig.B[f'{en}.{s}']
            pts = [r, k, w, e]; L = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(3)]; U = np.r_[0, np.cumsum(L)]
            best = np.full(len(P), np.inf); u = np.zeros(len(P))
            for i in range(3):
                a, b = pts[i], pts[i + 1]; ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1); d = np.linalg.norm(P - (a + t[:, None] * ab), axis=1)
                better = d < best; best[better] = d[better]; u[better] = U[i] + t[better] * L[i]
            lim = W[:, [ia[f'{up}.{s}'], ia[f'{lo}.{s}'], ia[f'{en}.{s}']]].sum(1) > 0.01
            f_up = 1 - ss((u - (U[1] + 0.33 * L[1])) / (0.3 * L[1]))
            f_lo = ss((u - (U[1] - 0.66 * L[0])) / (0.3 * L[0])) * (1 - ss((u - (U[2] + 0.33 * L[2])) / (0.3 * L[2])))
            f_en = ss((u - (U[2] - 0.66 * L[1])) / (0.3 * L[1]))
            # (what a bone loses goes to its neighbour along the limb on that side: the upper bone's to the lower, the lower's to the end
            # bone past the wrist / ankle and to the upper bone above the elbow / knee, the end bone's to the lower)
            iu, il, ie = ia[f'{up}.{s}'], ia[f'{lo}.{s}'], ia[f'{en}.{s}']
            for j, f, to in ((iu, f_up, np.full(len(P), il)), (il, f_lo, np.where(u > U[2], ie, iu)), (ie, f_en, np.full(len(P), il))):
                lost = np.where(lim, W[:, j] * (1 - f), 0.0); W[:, j] -= lost; np.add.at(W, (np.arange(len(P)), to), lost); cut += int((lost > 0.02).sum())
    if verbose: print(f'  chain window: {cut} limb shares cut away from their own segments')
    return W
def limb_cut(W, names, P, T, rig, verbose=True):
    """each limb's weights kept to the limb itself: bone heat lets a limb's weight seep across onto the trunk where the trunk's own bone
    is far (this body is wide, its spine a thin line down the middle) and the limb lies close beside it (the upper arm runs back along
    the flank). The limb is what lies on the hand's (foot's) side of its root ring, by distance over the surface from the forearm and
    hand (shin and foot): past the ring, over a short band, its share goes to the trunk bones there"""
    ia = {n: i for i, n in enumerate(names)}; W = W.copy(); G, E = mk.graph(P, T); moved = 0
    for s in 'LR':
        for up, mid, en, dig, give in (('upperarm', 'forearm', 'hand', 'finger', (f'shoulder.{s}', 'chest', 'spine1', 'spine')), ('thigh', 'shin', 'foot', 'toe', ('hips', 'spine', 'tail1'))):
            lb = [ia[n] for n in names if n in (f'{up}.{s}', f'{mid}.{s}', f'{en}.{s}') or (n.startswith(dig) and n.endswith(f'.{s}.1') or n.startswith(dig) and n.endswith(f'.{s}.2')) or n == f'toes.{s}']
            dist = [ia[n] for n in names if n in (f'{mid}.{s}', f'{en}.{s}') or n.startswith(dig) and f'.{s}.' in n or n == f'toes.{s}']
            seeds = np.where(W[:, dist].sum(1) > 0.5)[0]
            g = mk.geodesic(G, seeds)
            j, e = rig.B[f'{up}.{s}']; L = np.linalg.norm(e - j); ax = (e - j) / L; t = (P - j) @ ax; r = np.linalg.norm((P - j) - t[:, None] * ax, axis=1)
            own = (W[:, ia[f'{up}.{s}']] > 0.5) & (t > 0.1 * L) & (t < 0.4 * L); rad = float(np.median(r[own])) if own.any() else 0.08
            ring = (np.abs(t) < 0.035) & (r < 1.6 * rad) & np.isfinite(g)
            g0 = float(np.median(g[ring])); band = 0.6 * rad
            m = 1 - ss((g - (g0 - band)) / (2 * band)); m[~np.isfinite(g)] = 0
            lost = (W[:, lb] * (1 - m)[:, None]).sum(1); W[:, lb] *= m[:, None]
            gi = [ia[x] for x in give]; gw = W[:, gi]; gs = gw.sum(1, keepdims=True)
            share = np.where(gs > 1e-6, gw / np.maximum(gs, 1e-12), np.eye(len(gi))[0]); W[:, gi] += share * lost[:, None]; moved += int((lost > 0.02).sum())
            # (and the other way: well inside the limb, short of its root band, only the limb's own bones: the knee sits by the tail's
            # root and took some of the tail's weight)
            m2 = 1 - ss((g - (g0 - 3 * band)) / (2 * band)); m2[~np.isfinite(g)] = 0
            nl = np.ones(len(names), bool); nl[lb] = False
            lost2 = (W[:, nl] * m2[:, None]).sum(1); W[:, nl] *= (1 - m2)[:, None]
            lw = W[:, lb]; ls = lw.sum(1, keepdims=True); near_b = np.argmax(lw, 1)
            share2 = np.where(ls > 1e-6, lw / np.maximum(ls, 1e-12), 0); share2[ls[:, 0] <= 1e-6, 0] = 1.0
            W[:, lb] += share2 * lost2[:, None]
            if verbose: print(f'  limb cut {up}.{s}: radius {rad:.3f}, root ring {int(ring.sum())} verts at {g0:.3f} from the {mid} / {en}; {int((lost > 0.02).sum())} vertices gave up their limb share')
    return W
def root_fade(W, names, P, rig, verbose=True):
    """a limb bone's share fades out behind its own root along its axis (the flank and the chest beside a hip or a shoulder must not
    swing out with the thigh or the upper arm): what it loses goes to the trunk bones there, in their own proportion"""
    ia = {n: i for i, n in enumerate(names)}; W = W.copy(); moved = 0
    for s in 'LR':
        for b, give, (a0, a1) in ((f'thigh.{s}', ('hips', 'spine', 'tail1'), (0.0, 0.07)), (f'upperarm.{s}', (f'shoulder.{s}',), (-0.02, 0.05))):
            j, e = rig.B[b]; ax = (e - j) / np.linalg.norm(e - j); t = (P - j) @ ax; k = ss((t - a0) / (a1 - a0))
            lost = W[:, ia[b]] * (1 - k); W[:, ia[b]] *= k; g = [ia[x] for x in give]; gw = W[:, g]; gs = gw.sum(1, keepdims=True)
            share = np.where(gs > 1e-6, gw / np.maximum(gs, 1e-12), 1.0 / len(g)); W[:, g] += share * lost[:, None]; moved += int((lost > 0.02).sum())
    if verbose: print(f'  root fade: {moved} vertex shares moved off the thighs and upper arms behind their roots')
    return W
def rigid_head(W, names, P, rig, lo=0.35, hi=0.7):
    ia = {n: i for i, n in enumerate(names)}; h = ia['head']; g = [ia[n] for n in names if n.startswith('gill0')]
    hk = ss((W[:, h] - lo) / (hi - lo)); keep_ear = W[:, g].sum(1)
    # (the ears keep their own weights; the head share elsewhere is pushed to 1 over the head, eased through the neck)
    W2 = W.copy(); others = [i for i in range(len(names)) if i != h and i not in g]
    rest = W2[:, others].sum(1); tgt = np.where(keep_ear > 0.01, W[:, h], np.maximum(W[:, h], hk))
    scale = np.where(rest > 1e-9, np.clip((1 - tgt - keep_ear) / np.maximum(rest, 1e-9), 0, None), 0)
    W2[:, others] *= scale[:, None]; W2[:, h] = tgt
    s = W2.sum(1, keepdims=True); return W2 / np.maximum(s, 1e-12)
def top4(W, thresh=0.01):
    idx = np.argsort(-W, 1)[:, :4]; w = np.take_along_axis(W, idx, 1); w[w < thresh] = 0; w /= np.maximum(w.sum(1, keepdims=True), 1e-12)
    Wo = np.zeros_like(W); np.put_along_axis(Wo, idx, w, 1); return Wo

AXIAL = ['tail6', 'tail5', 'tail4', 'tail3', 'tail2', 'tail1', 'hips', 'spine', 'spine1', 'chest']
def axial_partition(W, names, P, rig, k=0.4, verbose=True):
    """the trunk's and the tail's share split along the body as a clean chain: bone heat over this wide body and thick tail blurred each
    vertex over three or four of them (in the ball curl that folded the pelvis and the tail's root); each vertex's axial share now goes
    to the one or two bones its place along the body (the nearest point on the chain of joints from the tail tip to the neck) lies
    between, blended over k of the shorter bone's length either side of each joint"""
    ia = {n: i for i, n in enumerate(names)}; W = W.copy(); B = rig.B
    pts = [B['tail6'][1]] + [B[f'tail{i}'][0] for i in range(6, 0, -1)] + [B['hips'][0], B['spine'][0], B['spine1'][0], B['chest'][0], B['chest'][1]]
    pts = [np.asarray(p, float) for p in pts]; L = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]; U = np.r_[0, np.cumsum(L)]
    # (bone spans along u: tail6 .. tail1 one segment each, hips two (the pelvis behind the hips joint and the back ahead of it), then one each)
    span = {'tail6': (U[0], U[1]), 'tail5': (U[1], U[2]), 'tail4': (U[2], U[3]), 'tail3': (U[3], U[4]), 'tail2': (U[4], U[5]), 'tail1': (U[5], U[6]),
            'hips': (U[6], U[8]), 'spine': (U[8], U[9]), 'spine1': (U[9], U[10]), 'chest': (U[10], U[11])}
    best = np.full(len(P), np.inf); u = np.zeros(len(P))
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; ab = b - a; t = np.clip(((P - a) @ ab) / (ab @ ab), 0, 1); d = np.linalg.norm(P - (a + t[:, None] * ab), axis=1)
        better = d < best; best[better] = d[better]; u[better] = U[i] + t[better] * L[i]
    A = np.zeros((len(P), len(AXIAL)))
    for j, b in enumerate(AXIAL):
        lo, hi = span[b]; f = np.ones(len(P))
        if j > 0:
            h = k * min(hi - lo, span[AXIAL[j - 1]][1] - span[AXIAL[j - 1]][0]); f *= ss((u - (lo - h)) / (2 * h))
        if j < len(AXIAL) - 1:
            h = k * min(hi - lo, span[AXIAL[j + 1]][1] - span[AXIAL[j + 1]][0]); f *= 1 - ss((u - (hi - h)) / (2 * h))
        A[:, j] = f
    A /= np.maximum(A.sum(1, keepdims=True), 1e-12)
    ax = [ia[b] for b in AXIAL]; share = W[:, ax].sum(1, keepdims=True); W[:, ax] = share * A
    if verbose: print(f'  axial partition: {int((share[:, 0] > 0.01).sum())} vertices, chain length {U[-1]:.2f}')
    return W
