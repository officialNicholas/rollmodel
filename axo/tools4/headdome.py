# The head as one bulbous dome (v8). The v7 head was the biped's skull with a spherical face cap pressed onto its front (face_cap in
# rig7crawl.py): a smaller sphere than the skull behind it, so from the side the face read as a plate with a rim round it. Here the whole
# skull is moved onto one smooth ellipsoid about a centre a little above the old face centre: radially, so nothing folds, the skull fully,
# the neck band fading out with the head's skin weight, the gill stalks carried with the skin they grow from (a harmonic fill over the
# mesh graph from the skull's own displacement), the two bodies alike (the same shell sits in both, their head frames are the identity).
# The face centre and radius (face.c / face.r, headc / headr) move to the dome's centre and depth, so the drawn face sits on the front of
# the curve, the eyes and mouth placed by angle as before, and the top of the head is where the game's hats expect it.
# Reads the v7 runtime meshes, writes the same format (new positions, normals, the crawl's canonical place moved along) to the output dir:
#   python3 -I headdome.py [src dir = S/look/backup] [out dir = S/look/rt2]
import sys, os, json
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import texbake as tb
OFF = np.array([0.0, 0.13, -0.01])        # the dome's centre, from the old face centre (up into the skull's middle)
RADII = np.array([0.38, 0.34, 0.345])      # its half width, height, depth (m, the standing body's metres)
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def adjacency(n, T):
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = np.unique(np.sort(e, 1), axis=0)
    A = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr(); return A, np.asarray(A.sum(1)).ravel()
def harmonic(n, T, free, vals, reg=1e-9):
    A, deg = adjacency(n, T); L = (diags(deg) - A).tocsr(); un = np.where(free)[0]; kn = np.where(~free)[0]
    if len(un) == 0: return vals.copy()
    lu = splu((L[un][:, un] + diags(np.full(len(un), reg))).tocsc()); rhs = -(L[un][:, kn] @ vals[kn])
    out = vals.copy(); out[un] = np.stack([lu.solve(rhs[:, k]) for k in range(vals.shape[1])], 1); return out
def smooth_field(A, deg, x, mask, iters=8, lam=0.5):
    """a few Laplacian steps of a vector field on the masked vertices (the rest held)"""
    x = x.copy()
    for _ in range(iters):
        y = (A @ x) / np.maximum(deg, 1)[:, None]; x[mask] = (1 - lam) * x[mask] + lam * y[mask]
    return x
def dome(nm, src, out):
    r = tb.load_rt(nm, d=src); P = r['P'].astype(float); T = r['T']; n = r['n']; W = r['W']; names = r['names']; bi = {k: i for i, k in enumerate(names)}
    hw = W[:, bi['head']] + W[:, bi['headfront']]; gw = W[:, [i for i, k in enumerate(names) if k.startswith('gill')]].sum(1)
    meta = dict(r['meta']); C = np.array(meta['face']['c'], float); Cp = C + OFF; a, b, c = RADII
    u = P - Cp; d = np.linalg.norm(u, axis=1); dr = u / np.maximum(d, 1e-9)[:, None]
    rho = 1.0 / np.sqrt((dr[:, 0] / a) ** 2 + (dr[:, 1] / b) ** 2 + (dr[:, 2] / c) ** 2)
    tgt = Cp + dr * rho[:, None]
    skin = gw < 0.02; s = ss((hw - 0.5) / 0.45) * skin
    delta = (tgt - P) * s[:, None]
    A, deg = adjacency(n, T); band = skin & (hw > 0.02) & (hw < 0.98)
    delta = smooth_field(A, deg, delta, band, iters=10)
    delta = harmonic(n, T, ~skin, delta)   # the gills: carried with the skin at their roots
    P2 = P + delta
    core = s > 0.99; dev = np.abs(np.linalg.norm(P2[core] - Cp, axis=1) - rho[core])
    print(f'{nm}: skull {int(core.sum())} verts moved {np.linalg.norm(delta[core], axis=1).mean() * 100:.1f} cm (max {np.linalg.norm(delta[core], axis=1).max() * 100:.1f}); '
          f'band {int(band.sum())}, gills {int((~skin).sum())} moved {np.linalg.norm(delta[~skin], axis=1).mean() * 100:.1f} cm; dome fit max dev {dev.max() * 1000:.2f} mm')
    # normals (area weighted, smooth), the canonical place along, the meta
    fn = np.cross(P2[T[:, 1]] - P2[T[:, 0]], P2[T[:, 2]] - P2[T[:, 0]]); vn = np.zeros((n, 3))
    for k in range(3): np.add.at(vn, T[:, k], fn)
    N = unit(vn); Nq = np.zeros((n, 4), np.int8); Nq[:, :3] = np.clip(np.round(N * 127), -127, 127).astype(np.int8)
    cps = meta['cpScale']; cp = r['cp'].astype(float) / 32767 * cps
    if nm == 'stand': cp[:, :3] = P2
    else: cp[:, :3] += delta
    cq = np.zeros((n, 4), np.int16); cq[:, :3] = np.clip(np.round(cp[:, :3] / cps * 32767), -32767, 32767); cq[:, 3] = r['cp'][:, 3]
    hb = [x for x in meta['bones'] if x['name'] == 'head'][0]; J = np.array(hb['pos'])
    meta['face'] = {'c': Cp.round(4).tolist(), 'r': round(float(c), 4)}; meta['headc'] = (Cp - J).round(4).tolist(); meta['headr'] = round(float(c), 4)
    meta['bbox'] = [P2.min(0).round(4).tolist(), P2.max(0).round(4).tolist()]
    parts = [('position', P2.astype(np.float32)), ('normal', Nq), ('skinIndex', r['si']), ('skinWeight', r['sw']), ('index', T.astype(np.uint16).ravel()),
             ('cpos', cq), ('jelly', r['jelly']), ('fill', r['fill']), ('mat', r['mat'])]
    off = {}; o = 0; blobs = []
    for k, arr in parts:
        bb = np.ascontiguousarray(arr).tobytes(); off[k] = o; blobs.append((o, bb)); o += len(bb); o += (-o) % 4
    buf = bytearray(o)
    for of, bb in blobs: buf[of:of + len(bb)] = bb
    meta['off7'] = off; os.makedirs(out, exist_ok=True)
    open(f'{out}/axo_{nm}.bin', 'wb').write(buf); json.dump(meta, open(f'{out}/axo_{nm}.json', 'w'))
    print(f'  {out}/axo_{nm}.bin {len(buf)} bytes; face c {meta["face"]["c"]} r {meta["face"]["r"]}; headc {meta["headc"]}')
if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else S + '/look/backup'; out = sys.argv[2] if len(sys.argv) > 2 else S + '/look/rt2'
    for nm in ('stand', 'crawl'): dome(nm, src, out)
