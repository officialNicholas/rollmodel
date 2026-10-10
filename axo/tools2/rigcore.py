# shared rig-building pieces: colour sampling, geometric segmentation (digits, gills, tail), chain weights, frames, export
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np, json, colorsys
from PIL import Image
from geo import M, D
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import dijkstra, connected_components

def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v) + 1e-12)
def smooth(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)

def vertex_colours(m, texpath):
    im = Image.open(texpath).convert('RGB'); a = np.asarray(im).astype(np.float32) / 255; h, w = a.shape[:2]
    uv = m.UV; px = np.clip((uv[:, 0] * (w - 1)).round().astype(int), 0, w - 1); py = np.clip((uv[:, 1] * (h - 1)).round().astype(int), 0, h - 1)
    c = a[py, px]; cw = np.zeros((m.n, 3)); cnt = np.zeros(m.n); np.add.at(cw, m.wid, c); np.add.at(cnt, m.wid, 1); cw /= cnt[:, None]
    hsv = np.array([colorsys.rgb_to_hsv(*x) for x in cw]); return cw, hsv

class Rig:
    def __init__(s): s.J = {}; s.PAR = {}; s.ORDER = []; s.END = {}; s.UP = {}
    def add(s, name, pos, par, end=None):
        s.J[name] = np.asarray(pos, float); s.PAR[name] = par; s.ORDER.append(name)
        if end is not None: s.END[name] = np.asarray(end, float)
    def kids(s, k): return [c for c in s.ORDER if s.PAR[c] == k]
    def endp(s, k):
        if k in s.END: return s.END[k]
        ch = s.kids(k)
        if ch: return np.mean([s.J[c] for c in ch], 0)
        return s.J[k] + np.array([0, 0.02, 0])
    def dirn(s, k): return unit(s.endp(k) - s.J[k])

# ---------- digits ----------
def segment_digits(m, wrist, region, axis=None, nmax=5, verbose='', step=0.005, min_verts=4, ext=0.04, distal_frac=0.55, seeds=None):
    """digits of a hand/foot on a coarse mesh: sweep the geodesic distance d from the wrist downward; each new cap component is a digit tip,
    the level where it touches another digit or the palm is its web level (persistence = tip - web). Each digit is then extended `ext` below
    its web level by flooding through the mesh surface (nearest digit wins), so a digit gets its base without leaking up the limb.
    returns list of dicts {verts, tip, base, axis, L}, d, hand axis"""
    reg = region.copy(); src = np.where(reg)[0]; src = src[np.argmin(np.linalg.norm(m.P[src] - wrist, axis=1))]; wp = m.P[src]
    d = m.geo(src, limit=0.8); d[~np.isfinite(d)] = -1; reg &= d >= 0; dmax = d[reg].max()
    PALM = -2; label = np.full(m.n, -1)
    # candidate tips by fanning: distal vertices (far from the wrist, beyond it along the hand axis) sorted by azimuth in the palm plane,
    # split at the largest angular gaps into nmax groups; a group's farthest vertex is its digit tip
    ax0 = unit(axis) if axis is not None else unit(m.P[reg][d[reg] > 0.8 * dmax].mean(0) - wp)
    Pr = m.P[reg] - wp; c_ = Pr.mean(0); u_, s_, vt = np.linalg.svd(Pr - c_, full_matrices=False); nrm = vt[2]; side = unit(np.cross(nrm, ax0)); ax1 = np.cross(side, nrm)
    distal = reg & (d > distal_frac * dmax) & (((m.P - wp) @ ax0) > 0.03); dv = np.where(distal)[0]
    ang = np.arctan2((m.P[dv] - wp) @ side, (m.P[dv] - wp) @ ax1); o_ = np.argsort(ang); dv = dv[o_]; ang = ang[o_]
    gaps = np.diff(ang); cuts = np.sort(np.argsort(-gaps)[:nmax - 1]) + 1 if len(dv) > nmax else np.array([], int)
    groups = np.split(np.arange(len(dv)), cuts); tips = []
    for g_ in groups:
        if len(g_) < 3: continue
        vs_ = dv[g_]; tips.append(int(vs_[np.argmax(d[vs_])]))
    if verbose: print(f'  {verbose} fan: distal {len(dv)} gaps {np.round(np.sort(gaps)[::-1][:nmax], 2).tolist()} tips {[np.round(m.P[t], 2).tolist() for t in tips]}')
    if seeds is not None:   # authored tips (inspected close-ups): snap to the nearest region vertex
        rv_ = np.where(reg)[0]; tips = [int(rv_[np.argmin(np.linalg.norm(m.P[rv_] - np.asarray(sd), axis=1))]) for sd in seeds]
    tracks = [{'tip': t} for t in tips]; tips = list(range(len(tips)))
    # flood the basins from the accepted tips only (watershed on d); a vertex that sees two basins is the web
    label = np.full(m.n, -1); web = {}; order = np.where(reg)[0]; order = order[np.argsort(-d[order])]; nb = m.G.tolil().rows
    for i, k in enumerate(tips): label[tracks[k]['tip']] = i
    for v in order:
        if label[v] >= 0: continue
        ls = set(int(label[u]) for u in nb[v] if label[u] >= 0 and d[u] >= d[v]); hasp = any(label[u] == PALM and d[u] >= d[v] for u in nb[v])
        if len(ls) == 1 and not hasp: label[v] = ls.pop()
        elif ls or hasp:
            for a_ in ls: web.setdefault(a_, float(d[v]))
            label[v] = PALM
    keep = [i for i in range(len(tips)) if i in web and (label == i).sum() >= min_verts]
    tracks = [{'tip': tracks[k]['tip'], 'web': web.get(i, None)} for i, k in enumerate(tips)]
    lab2 = np.full(m.n, -1); best = np.full(m.n, np.inf)
    for k in keep:
        band = reg & (label == PALM) & (d > tracks[k]['web'] - ext) & (d <= tracks[k]['web'] + 0.001); seeds = np.where(label == k)[0]
        g = m.geo(seeds, limit=ext * 2.5, mask=band | (label == k)); better = (g < best) & band; best[better] = g[better]; lab2[better] = k
    out = []
    for k in keep:
        vs = np.where((label == k) | (lab2 == k))[0]; o_ = np.argsort(d[vs]); base = m.P[vs[o_[:max(3, len(vs) // 5)]]].mean(0); tipc = m.P[vs[o_[-max(3, len(vs) // 6):]]].mean(0)
        adir = unit(tipc - base); Ld = float(((m.P[vs] - base) @ adir).max())
        out.append({'verts': vs, 'tip': tracks[k]['tip'], 'base': base, 'axis': adir, 'L': Ld})
    if axis is None: axis = unit(np.mean([m.P[g['tip']] for g in out], 0) - wp) if out else np.array([0, 0, 1.0])
    if verbose: print(f'  {verbose}: dmax {dmax:.3f} tracks {len(tracks)} digits {len(out)} ' + ' '.join(f'[n={len(g["verts"])} L={g["L"]:.3f} base={np.round(g["base"], 2).tolist()}]' for g in out))
    return out, d, unit(axis)

def digit_chain(g):
    base = g['base']; tip = base + g['axis'] * g['L']; return base, base + g['axis'] * g['L'] * 0.48, tip

def digit_weights(m, g, bones, hand_bone, W, blend=0.25):
    """weights for one digit: proximal / distal phalanx by the parameter u along the digit's axis, a smooth falloff into the hand at the knuckle"""
    vs = g['verts']; u = np.clip(((m.P[vs] - g['base']) @ g['axis']) / max(g['L'], 1e-6), 0, 1); p1, p2 = bones
    w2 = smooth((u - 0.5) / 0.24 + 0.5); wh = 1 - smooth(u / blend)
    W[vs, :] = 0; W[vs, hand_bone] = wh; W[vs, p1] = (1 - wh) * (1 - w2); W[vs, p2] = (1 - wh) * w2

# ---------- gills ----------
def thin_mask(m, cand, r=0.045, dot=-0.25, red=None, up=(0, 1, 0)):
    """vertices of thin parts (stems, frills): an opposite-facing neighbour within r OF THE SAME COLOUR CLASS (a pale stem's other side,
    a red frill's other side). Pale body skin lying under a red frill is not thin, and upward-facing smooth dorsal skin never is."""
    from scipy.spatial import cKDTree
    tree = cKDTree(m.P); out = np.zeros(m.n, bool); up = np.asarray(up, float)
    for v in np.where(cand)[0]:
        if red is not None and not red[v] and m.N[v] @ up > 0.7: continue
        nb = [u for u in tree.query_ball_point(m.P[v], r) if u != v and (red is None or red[u] == red[v])]
        if nb and min(m.N[v] @ m.N[u] for u in nb) < dot: out[v] = True
    return out

def segment_gills(m, hsv, rgb, head_c, head_r, extra_mask, sat=0.42):
    red = (hsv[:, 1] > sat) & ((hsv[:, 0] > 0.9) | (hsv[:, 0] < 0.05)) & extra_mask
    dh = np.linalg.norm(m.P - head_c, axis=1); red &= dh > head_r * 0.6
    nc, lab = m.comps(red); sizes = np.bincount(lab[lab >= 0]); keep = np.where(sizes >= 40)[0]
    gill = np.isin(lab, keep); print('  gills: red verts', int(red.sum()), 'components', [int(sizes[k]) for k in keep])
    return gill, lab

def split_stalks(m, gill, head_c, up, left, side_sign, k=3, nonred_d=None):
    """the stalks of one side: cluster the stem roots (gill verts touching the head skin) into k groups, then assign every gill vertex of
    that side to the root group it is geodesically closest to (inside the gill surface), so each frill follows the stem it grows from"""
    side = gill & (((m.P - head_c) @ left) * side_sign > 0); g = np.where(side)[0]
    roots = g[nonred_d[g] < np.quantile(nonred_d[g], 0.12)]; pts = m.P[roots]; el = (pts - head_c) @ up
    cent = pts[np.argsort(el)[[int(len(el) * 0.85), int(len(el) * 0.5), int(len(el) * 0.15)]]].copy(); L = np.zeros(len(roots), int)
    for it in range(50):
        L = np.argmin(np.linalg.norm(pts[:, None] - cent[None], axis=2), axis=1)
        for j in range(k):
            if (L == j).any(): cent[j] = pts[L == j].mean(0)
    best = np.full(m.n, np.inf); lab = np.full(m.n, -1)
    for j in range(k):
        d = m.geo(roots[L == j], limit=1.5, mask=side); better = d < best; best[better] = d[better]; lab[better] = j
    left_ = g[lab[g] < 0]   # gill skin not reached from any root inside the gill surface: nearest root cluster by distance
    if len(left_): lab[left_] = np.argmin(np.linalg.norm(m.P[left_][:, None] - cent[None], axis=2), axis=1)
    groups = [g[lab[g] == j] for j in range(k)]
    groups.sort(key=lambda q: -float(((m.P[q].mean(0) - head_c) @ up)))
    return groups   # top stalk first

def stalk_chain(m, vs, head_c, nonred_d):
    """root = stalk verts closest (geodesically) to non-gill skin; axis by PCA; returns root, mid, tip"""
    dd = nonred_d[vs]; root = m.P[vs[dd <= np.quantile(dd, 0.08)]].mean(0)
    pts = m.P[vs]; far = pts[np.argmax(np.linalg.norm(pts - root, axis=1))]
    axis = unit(far - root); proj = (pts - root) @ axis; L = np.quantile(proj, 0.97)
    tip = root + axis * L; return root, root + axis * L * 0.5, tip, axis, L

def stalk_weights(m, vs, root, axis, L, bones, head_bone, W, blend=0.18):
    u = np.clip(((m.P[vs] - root) @ axis) / L, 0, 1); b1, b2 = bones
    w2 = smooth((u - 0.5) / 0.3 + 0.5); wh = 1 - smooth(u / blend)
    W[vs, :] = 0; W[vs, head_bone] = wh; W[vs, b1] = (1 - wh) * (1 - w2); W[vs, b2] = (1 - wh) * w2

# ---------- chains (tail, limbs, trunk) ----------
def polyline_param(P, pts):
    """nearest point on a polyline for each P: returns arc-length parameter s (0..total) and the distance"""
    seg = np.diff(pts, axis=0); L = np.linalg.norm(seg, axis=1); cum = np.r_[0, np.cumsum(L)]
    best_s = np.zeros(len(P)); best_d = np.full(len(P), np.inf)
    for i in range(len(seg)):
        a = pts[i]; v = seg[i]; t = np.clip(((P - a) @ v) / max(L[i] ** 2, 1e-12), 0, 1); q = a + t[:, None] * v; dd = np.linalg.norm(P - q, axis=1)
        better = dd < best_d; best_d[better] = dd[better]; best_s[better] = cum[i] + t[better] * L[i]
    return best_s, best_d, cum

def chain_weights(P, vs, pts, bone_ids, W, band=0.06, base_bone=None, base_blend=0.0):
    """vertices vs weighted along a polyline chain (joint positions pts, len(pts) = len(bone_ids)+1): each bone owns its segment with a
    smooth crossfade of width `band` at the joints; at the start of the chain the first bone fades into base_bone over base_blend"""
    s, dd, cum = polyline_param(P[vs], pts); W[vs, :] = 0; nb = len(bone_ids)
    for j in range(nb):
        s0, s1 = cum[j], cum[j + 1]
        lo = smooth((s - s0) / band + 0.5) if j > 0 else np.ones_like(s)
        hi = 1 - smooth((s - s1) / band + 0.5) if j < nb - 1 else np.ones_like(s)
        W[vs, bone_ids[j]] = lo * hi
    if base_bone is not None and base_blend > 0:
        wb = 1 - smooth(s / base_blend); W[vs, :] *= (1 - wb)[:, None]; W[vs, base_bone] += wb
    return s

def ring_centerline(m, src_mask, limit, nsteps, mask=None, rmax=0.3):
    """ring centroids of geodesic distance from a source vertex set, in order of increasing distance"""
    src = np.where(src_mask)[0]; d = m.geo(src, limit=limit + 0.05, mask=mask); fin = np.isfinite(d); dmax = min(limit, d[fin].max())
    ts = np.linspace(0, dmax, nsteps); pts = []; prev = m.P[src].mean(0); step = ts[1] - ts[0]
    for t in ts:
        sel = fin & (np.abs(d - t) < step * 0.6); q = m.P[sel]
        if len(q) == 0: pts.append(prev.copy()); continue
        if len(pts): q = q[np.linalg.norm(q - prev, axis=1) < rmax]
        c = q.mean(0) if len(q) else prev; pts.append(c); prev = c
    return np.array(pts), d

def laplacian_smooth_weights(m, W, vs, iters=3, lam=0.5):
    """smooth the weight rows of vertices vs using the welded graph (only among vs)"""
    keep = np.zeros(m.n, bool); keep[vs] = True
    E = m.E; e = E[keep[E[:, 0]] & keep[E[:, 1]]]
    n = m.n; A = csr_matrix(coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)))
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1
    for it in range(iters):
        avg = (A @ W) / deg[:, None]; W[vs] = (1 - lam) * W[vs] + lam * avg[vs]
    return W

def finalize(W, maxinf=4, prune=0.02, P=None, joints=None):
    """normalize, keep the top 4 influences, prune tiny ones; a vertex with no weight at all takes its nearest joint"""
    W = np.clip(W, 0, None); empty = np.where(W.sum(1) <= 1e-9)[0]
    if len(empty):
        print(f'  !!! {len(empty)} vertices had no weights -> nearest joint')
        if P is not None and joints is not None: W[empty, np.argmin(np.linalg.norm(P[empty][:, None] - joints[None], axis=2), axis=1)] = 1
        else: W[empty, 0] = 1
    top = np.argsort(-W, axis=1)[:, :maxinf]; tw = np.take_along_axis(W, top, 1)
    tw[tw < prune * tw.max(1, keepdims=True)] = 0; s = tw.sum(1, keepdims=True); s[s == 0] = 1; tw /= s
    return top.astype(np.uint8), tw.astype(np.float32)

# ---------- frames ----------
def mkframe(y, zref):
    y = unit(y); z = np.asarray(zref, float); z = z - (z @ y) * y
    if np.linalg.norm(z) < 1e-6: z = np.cross(y, [1, 0, 0])
    z = unit(z); x = np.cross(y, z); return np.stack([x, y, z], 1)
def quat(Mx):
    t = np.trace(Mx)
    if t > 0: s_ = np.sqrt(t + 1) * 2; return np.array([(Mx[2, 1] - Mx[1, 2]) / s_, (Mx[0, 2] - Mx[2, 0]) / s_, (Mx[1, 0] - Mx[0, 1]) / s_, 0.25 * s_])
    i = int(np.argmax(np.diag(Mx))); j, k = (i + 1) % 3, (i + 2) % 3
    s_ = np.sqrt(1 + Mx[i, i] - Mx[j, j] - Mx[k, k]) * 2; q = np.zeros(4); q[i] = 0.25 * s_; q[j] = (Mx[j, i] + Mx[i, j]) / s_; q[k] = (Mx[k, i] + Mx[i, k]) / s_; q[3] = (Mx[k, j] - Mx[j, k]) / s_
    return q

def export(m, R, F, idx, w, out, extra=None, scale=1.0, shift=(0, 0, 0)):
    names = R.ORDER; shift = np.asarray(shift, float)
    for k in list(R.J): R.J[k] = R.J[k] * scale + shift
    for k in list(R.END): R.END[k] = R.END[k] * scale + shift
    m.P0 = m.P0 * scale + shift
    bones = [{'name': k, 'parent': R.PAR[k], 'pos': [round(float(x), 5) for x in R.J[k]], 'end': [round(float(x), 5) for x in R.endp(k)], 'q': [round(float(x), 6) for x in quat(F[k])]} for k in names]
    idx = idx[m.wid]; w = w[m.wid]; wq = np.round(w * 255).astype(np.int32); wq[:, 0] += 255 - wq.sum(1); wq = np.clip(wq, 0, 255).astype(np.uint8)
    P = m.P0.astype(np.float32); N = m.N0.astype(np.float32); UV = m.UV.astype(np.float32); I = m.I0.reshape(-1).astype(np.uint16 if len(P) < 65536 else np.uint32)
    parts = [P.tobytes(), N.tobytes(), UV.tobytes(), idx.astype(np.uint8).tobytes(), wq.tobytes(), I.tobytes()]; off = []; o = 0
    for b in parts: off.append(o); o += len(b); o += (-o) % 4
    buf = bytearray(o)
    for b, of in zip(parts, off): buf[of:of + len(b)] = b
    open(out + '.bin', 'wb').write(buf)
    meta = {'n': len(P), 'ni': len(I), 'i32': len(P) >= 65536, 'off': off, 'bones': bones, 'bbox': [P.min(0).round(4).tolist(), P.max(0).round(4).tolist()]}
    if extra: meta.update(extra)
    json.dump(meta, open(out + '.json', 'w'))
    print(' exported', out, len(buf), 'bytes', len(P), 'verts', len(names), 'bones')
