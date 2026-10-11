# post-process of each exported mesh (.bin/.json from rigstand.py / rigcrawl.py), rebuilding the .bin:
#   - smooth welded normals (both meshes) and, on the crawl sculpt, a softened belly crease (the sculpt's underside was pressed flat)
#   - webbing membranes between adjacent toes (and fingers), skinned to the two digits and the foot / hand
#   - per-vertex extras appended after the indices:
#       jelly (4 x uint8): x belly (breathing expand / satin region), y soft (jelly layer freedom), z thin (gills, fins, webs), w head weight
#       fill  (2 x uint8): x crawl fill order (paint rises from the ground contacts), y stand fill order (from the feet, hands last)
#       xtra  (2 x uint8): x ambient occlusion (0 open .. 1 buried: creases, armpits, between the toes), y webbing
import sys, os, json; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from scipy.spatial import cKDTree
from geo import M, D
from rigcore import thin_mask, laplacian_smooth_weights, unit
W_ = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo2/'
def smooth_scalar(m, x, iters=3):
    X = x[:, None].astype(float).copy(); laplacian_smooth_weights(m, X, np.arange(m.n), iters=iters, lam=0.5); return X[:, 0]
def welded_normals(m, P):
    T = m.T; fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); vn = np.zeros((len(P), 3))
    for k in range(3): np.add.at(vn, T[:, k], fn)
    return vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)
def taubin(m, P, wt, iters=14, lam=0.5, mu=-0.53):
    """Taubin smoothing of the welded positions, weighted per vertex by wt (0 = fixed)"""
    from scipy.sparse import coo_matrix, csr_matrix
    e = m.E; n = m.n; A = csr_matrix(coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)))
    deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1; P = P.copy()
    for it in range(iters):
        for k in (lam, mu): P += k * wt[:, None] * ((A @ P) / deg[:, None] - P)
    return P
def ambient_occlusion(P, N, r=0.1):
    """cavity term on the welded cloud: how much nearby surface sits above the tangent plane (0 open .. 1 buried)"""
    tree = cKDTree(P); occ = np.zeros(len(P))
    pairs = tree.query_pairs(r, output_type='ndarray')
    d = P[pairs[:, 1]] - P[pairs[:, 0]]; L = np.linalg.norm(d, axis=1) + 1e-9; dh = d / L[:, None]; fall = (1 - L / r)
    for a, b, sgn in ((pairs[:, 0], pairs[:, 1], 1), (pairs[:, 1], pairs[:, 0], -1)):
        up = np.clip(np.einsum('ij,ij->i', N[a], dh * sgn), 0, 1); num = np.zeros(len(P)); den = np.zeros(len(P))
        np.add.at(num, a, up * fall); np.add.at(den, a, fall); occ += num / np.maximum(den, 1e-9)
    return np.clip(occ * 0.9, 0, 1)
def polyline_at(pts, s):
    """point at normalized arc length s on a polyline"""
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); L = seg.sum(); t = s * L
    for k in range(len(seg)):
        if t <= seg[k] or k == len(seg) - 1: return pts[k] + (pts[k + 1] - pts[k]) * (min(t, seg[k]) / max(seg[k], 1e-9))
        t -= seg[k]
def webbing(meta, Pw, Nw, labels_w, m, fill_w, bi, nm):
    """membranes between adjacent digits: a 6 x 4 grid per web, two copies (top / underside), skinned to the two digits and their parent bone"""
    B = {b['name']: b for b in meta['bones']}; out = dict(P=[], N=[], UV=[], idx=[], w=[], I=[], fill=[], base=[])
    palm = meta.get('palm', {})
    for pre, par in (('toe', 'toes'), ('finger', 'hand')):
        for s in 'LR':
            pb = B[f'{par}.{s}']; lines = []; rad = []; uvs = []
            for k in range(4):
                b1, b2 = B.get(f'{pre}{k}.{s}.1'), B.get(f'{pre}{k}.{s}.2')
                if not b1 or not b2: continue
                pts = np.array([b1['pos'], b2['pos'], b2['end']], float); vs = np.where(labels_w == f'{pre}{k}.{s}')[0]
                if len(vs) < 4: continue
                ax = unit(pts[-1] - pts[0]); dv = Pw[vs] - pts[0]; dist = np.linalg.norm(dv - np.outer(dv @ ax, ax), axis=1); r = float(np.percentile(dist, 70))
                near = vs[np.argmin(np.linalg.norm(Pw[vs] - pts[0], axis=1))]; split = np.where(m.wid == near)[0][0]
                lines.append((k, pts)); rad.append(r); uvs.append((m.UV[split], fill_w[near]))
            if len(lines) < 2: continue
            tips = np.array([l[1][-1] for l in lines]); fwd = unit(tips.mean(0) - np.array(pb['pos']))
            up = -unit(np.array(palm[f'hand.{s}'])) if (pre == 'finger' and f'hand.{s}' in palm) else np.array([0, 1.0, 0])
            lat = unit(np.cross(up, fwd)); order = np.argsort(tips @ lat)
            fweb = 0.72 if pre == 'toe' else 0.5
            for oa, ob in zip(order[:-1], order[1:]):
                (ka, pa), (kb, pbb) = lines[oa], lines[ob]; ra, rb = rad[oa], rad[ob]
                if np.linalg.norm(pa[-1] - pbb[-1]) > 0.3: continue   # not neighbours
                grid = np.zeros((6, 4, 3)); wts = np.zeros((6, 4, 4)); bones = np.zeros((6, 4, 4), int)
                for j, t in enumerate(np.linspace(0, 1, 4)):
                    smax = fweb * (1 - 0.3 * np.sin(np.pi * t))
                    for i, si in enumerate(np.linspace(0, 1, 6)):
                        sv = si * smax; A = polyline_at(pa, sv); Bp = polyline_at(pbb, sv); dab = Bp - A; axn = unit(dab)
                        A2 = A + axn * ra * 0.75 - up * ra * 0.15; B2 = Bp - axn * rb * 0.75 - up * rb * 0.15
                        if np.linalg.norm(dab) < (ra + rb) * 0.9: A2 = B2 = (A + Bp) / 2 - up * (ra + rb) * 0.2
                        grid[i, j] = (1 - t) * A2 + t * B2
                        g = 0.25 + 0.75 * min(1, sv / 0.3); seg = min(1, max(0, (sv - 0.4) / 0.2)); wa, wb = (1 - t) * g, t * g
                        if seg <= 0: bones[i, j] = [bi[f'{pre}{ka}.{s}.1'], bi[f'{pre}{kb}.{s}.1'], bi[f'{par}.{s}'], bi[f'{par}.{s}']]; wts[i, j] = [wa, wb, 1 - g, 0]
                        else: bones[i, j] = [bi[f'{pre}{ka}.{s}.1'], bi[f'{pre}{ka}.{s}.2'], bi[f'{pre}{kb}.{s}.1'], bi[f'{pre}{kb}.{s}.2']]; wts[i, j] = [wa * (1 - seg), wa * seg, wb * (1 - seg), wb * seg]
                uv = uvs[oa][0]; fl = (uvs[oa][1] + uvs[ob][1]) / 2
                for side in (1, -1):
                    n0 = len(out['P']); nrm = up * side
                    for i in range(6):
                        for j in range(4): out['P'].append(grid[i, j]); out['N'].append(nrm); out['UV'].append(uv); out['idx'].append(bones[i, j]); out['w'].append(wts[i, j]); out['fill'].append(fl); out['base'].append(side)
                    for i in range(5):
                        for j in range(3):
                            a, b, c, d = n0 + i * 4 + j, n0 + i * 4 + j + 1, n0 + (i + 1) * 4 + j, n0 + (i + 1) * 4 + j + 1
                            for tri in ((a, c, b), (b, c, d)):
                                p = np.array([out['P'][x] for x in tri]); fn = np.cross(p[1] - p[0], p[2] - p[0])
                                out['I'].extend(tri if fn @ nrm >= 0 else tri[::-1])
    print(f'  {nm}: webbing {len(out["P"])} verts, {len(out["I"]) // 3} tris')
    return out
for nm in ('stand', 'crawl'):
    meta = json.load(open(D + f'{nm}_export.json')); m = M(nm); r = np.load(D + f'{nm}_rig.npz', allow_pickle=True); names = list(r['names']); labels = np.array([str(x) for x in r['labels']])
    buf = open(D + f'{nm}_export.bin', 'rb').read(); n = meta['n']; o = meta['off'][:6]   # the pristine rig export (first six sections)
    P = np.frombuffer(buf, np.float32, n * 3, o[0]).reshape(n, 3).copy(); N = np.frombuffer(buf, np.float32, n * 3, o[1]).reshape(n, 3).copy(); UV = np.frombuffer(buf, np.float32, n * 2, o[2]).reshape(n, 2).copy()
    idx = np.frombuffer(buf, np.uint8, n * 4, o[3]).reshape(n, 4).copy(); wq = np.frombuffer(buf, np.uint8, n * 4, o[4]).reshape(n, 4).copy(); I = np.frombuffer(buf, np.uint16, meta['ni'], o[5]).copy()
    Wd = np.zeros((m.n, len(names)))
    for c in range(4): np.add.at(Wd, (np.arange(m.n), r['idx'][:, c]), r['w'][:, c])
    bi = {k: i for i, k in enumerate(names)}; wsum = lambda ks: sum(Wd[:, bi[k]] for k in ks if k in bi)
    Pw = P[m.uidx].astype(float)   # welded positions in exported coordinates
    head = np.clip(wsum(['head', 'headfront']) + wsum([k for k in names if k.startswith('gill')]), 0, 1)
    trunk = np.clip(wsum(['spine', 'spine1', 'chest']) + 0.5 * wsum(['hips']), 0, 1)
    digit = wsum([k for k in names if k.startswith('finger') or (k.startswith('toe') and not k.startswith('toes'))])
    ventral = np.array([0, 0, 1.0]) if nm == 'stand' else np.array([0, -1.0, 0])
    if nm == 'crawl':
        # the sculpt's belly was pressed flat against the ground with a hard crease along the flank: round it off
        Nw0 = welded_normals(m, Pw); down = np.clip(Nw0 @ ventral, 0, 1)
        wt = np.clip(trunk + 0.6 * wsum(['tail1', 'tail2']), 0, 1) * np.clip((down - 0.05) / 0.4, 0, 1) * (1 - head) * (1 - np.clip(digit, 0, 1)) * (1 - 0.8 * np.clip(wsum([k for k in names if k.startswith(('thigh', 'shin', 'foot', 'toes', 'upperarm', 'forearm', 'hand'))]), 0, 1))
        wt = smooth_scalar(m, wt, 2); Pn = taubin(m, Pw, wt, iters=16)
        print('  crawl belly rounded:', int((wt > 0.3).sum()), 'verts, max move', np.linalg.norm(Pn - Pw, axis=1).max().round(4))
        Pw = Pn; P = Pw[m.wid].astype(np.float32)
    Nw = welded_normals(m, Pw); ang = np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', Nw[m.wid], N), -1, 1)))
    print(f'  {nm}: welded normals vs exported: mean {ang.mean():.1f} deg, 95% {np.percentile(ang, 95):.1f}')
    if nm == 'crawl' or os.environ.get('NORMALS') == 'welded': N = Nw[m.wid].astype(np.float32)
    trunkAny = np.clip(wsum(['hips', 'spine', 'spine1', 'chest', 'neck']) + 0.6 * wsum(['tail1', 'tail2']) + 0.3 * wsum(['tail3']), 0, 1)
    gillW = np.clip(wsum([k for k in names if k.startswith('gill')]), 0, 1); limbW = np.clip(wsum([k for k in names if k.startswith(('upperarm', 'forearm', 'hand', 'thigh', 'shin', 'foot', 'toes'))]), 0, 1)
    vent = np.clip((Nw @ ventral + 0.15) / 0.65, 0, 1)
    # the pale satin underside: the standing mesh's trunk front (its face also faces +z); the prone sculpt's whole underside, throat included
    belly = trunkAny * vent if nm == 'stand' else vent * (1 - gillW) * (1 - np.clip(digit, 0, 1)) * (1 - 0.6 * limbW)
    belly = np.clip(smooth_scalar(m, np.clip(belly, 0, 1), 2) * 1.15, 0, 1)
    soft = np.clip(1 - head, 0, 1) * (1 - 0.5 * digit)
    thin = thin_mask(m, np.ones(m.n, bool), r=0.045 if nm == 'stand' else 0.04).astype(float); thin = np.clip(smooth_scalar(m, thin, 2) * 1.3, 0, 1)
    islab = lambda pre: np.array([l.startswith(pre) for l in labels])
    hands = (wsum(['hand.L', 'hand.R']) > 0.3) | islab('finger'); feet = (wsum(['foot.L', 'foot.R', 'toes.L', 'toes.R']) > 0.3) | (islab('toe') & ~islab('toes'))
    if nm == 'stand':
        bellyC = (trunk > 0.4) & (Nw[:, 2] > 0.3) & (Pw[:, 1] > 0.45) & (Pw[:, 1] < 1.0)
        src = hands | feet | bellyC
        standO = np.clip(Pw[:, 1] / 1.78, 0, 1) + 0.3 * (wsum(['hand.L', 'hand.R', 'forearm.L', 'forearm.R']) > 0.3) + 0.3 * islab('finger') + 0.1 * islab('gill')
    else:
        src = Pw[:, 1] < 0.075
        d = m.geo(np.where(feet)[0], limit=5.0); d[~np.isfinite(d)] = d[np.isfinite(d)].max(); standO = d / d.max() + 0.35 * (hands | (wsum(['forearm.L', 'forearm.R']) > 0.3))
    d = m.geo(np.where(src)[0], limit=5.0); d[~np.isfinite(d)] = d[np.isfinite(d)].max(); crawlO = d / d.max()
    crawlO = smooth_scalar(m, crawlO, 2); standO = smooth_scalar(m, np.clip(standO, 0, 1), 2); standO = standO / standO.max()
    ao = ambient_occlusion(Pw, Nw, r=0.1); ao = smooth_scalar(m, ao, 1)
    print(f'  {nm}: ao percentiles 50/90/99: {np.percentile(ao, [50, 90, 99]).round(2)}')
    fill_w = np.stack([crawlO, standO], 1)
    jelly = np.stack([belly, soft, thin, head], 1)[m.wid]; fill = fill_w[m.wid]; xtra = np.stack([ao, np.zeros(m.n)], 1)[m.wid]
    web = webbing(meta, Pw, Nw, labels, m, fill_w, bi, nm); nw = len(web['P'])
    if nw:
        P = np.vstack([P, np.array(web['P'], np.float32)]); N = np.vstack([N, np.array(web['N'], np.float32)]); UV = np.vstack([UV, np.array(web['UV'], np.float32)])
        ww = np.array(web['w'], float); ww /= ww.sum(1, keepdims=True); wq8 = np.round(ww * 255).astype(np.int32); wq8[:, 0] += 255 - wq8.sum(1)
        idx = np.vstack([idx, np.array(web['idx'], np.uint8)]); wq = np.vstack([wq, np.clip(wq8, 0, 255).astype(np.uint8)])
        I = np.concatenate([I, (np.array(web['I'], np.int64) + n).astype(np.uint16)])   # web indices are relative to the web block
        jelly = np.vstack([jelly, np.tile([0, 0.3, 1.0, 0], (nw, 1))]); fill = np.vstack([fill, np.array(web['fill'])]); xtra = np.vstack([xtra, np.tile([0.5, 1.0], (nw, 1))])
    q = lambda a: np.clip(np.round(a * 255), 0, 255).astype(np.uint8)
    n = len(P); parts = [P.astype(np.float32).tobytes(), N.astype(np.float32).tobytes(), np.clip(np.round(UV * 65535), 0, 65535).astype(np.uint16).tobytes(), idx.astype(np.uint8).tobytes(), wq.astype(np.uint8).tobytes(), I.astype(np.uint16).tobytes(), q(jelly).tobytes(), q(fill).tobytes(), q(xtra).tobytes()]
    off = []; o = 0
    for b in parts: off.append(o); o += len(b); o += (-o) % 4
    out = bytearray(o)
    for b, of in zip(parts, off): out[of:of + len(b)] = b
    meta.update({'n': n, 'ni': len(I), 'i32': False, 'uv16': True, 'off': off, 'bbox': [P.min(0).round(4).tolist(), P.max(0).round(4).tolist()]})
    open(W_ + f'axo_{nm}.bin', 'wb').write(out); json.dump(meta, open(W_ + f'axo_{nm}.json', 'w'))
    print(nm, 'bin', len(out), 'verts', n, 'tris', len(I) // 3, 'belly>0.5', int((belly > 0.5).sum()), 'thin>0.5', int((thin > 0.5).sum()), 'head>0.5', int((head > 0.5).sum()))
