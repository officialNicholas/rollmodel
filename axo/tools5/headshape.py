# The head with a shape (v9). The v8 head (headdome.py) is one ellipsoid about the face centre, which the user found too close to a
# perfect sphere. Here the dome's radius is modulated by direction, smoothly, about the same centre (so the drawn face, placed by angle
# about that centre, lands where it did): a flatter, wider top (a superellipsoid blend toward the top, the pole itself a little lower),
# broader cheeks at the gill roots, a gentle brow over the eyes, a soft rounded muzzle low on the front with the forehead sloping back
# a touch, and the lower back of the skull drawn in toward the neck. Every term is a wide smooth lobe: no rims, no plate.
# And the gills brought forward: the stalks are welded into the skull, so the whole gill strip (stalks, fronds, their base rings and the
# skin round them) turns forward about the dome's vertical axis by one angle, rigid on the stalks, and the turn fades out smoothly over
# the skin toward the face and the back midline (a yaw field whose slope stays under 1, so the skin ahead squeezes and the skin behind
# stretches but never folds). The gill bones' joints, ends and canonical frames turn by the same yaw, so the rig stays exactly consistent
# (names, count, order unchanged; the crawl rest pose relative to the stand's is unchanged since both bodies turn alike).
# Reads the domed untextured meshes and the textured ones baked from them, writes the textured meshes with the new positions, normals
# and canonical places in place (same layout: the UV atlas and the texture bytes untouched) plus the untextured ones for reference:
#   python3 -I headshape.py [--untex S/fable/rt2src] [--tex S/fable/rt2] [--out S/fable2/rt3] [--outsrc S/fable2/rt3src]
import sys, os, json
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.spatial import cKDTree
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
WORK = S + '/fable2'
sys.path.insert(0, '/home/user/rollmodel/axo/tools4')
import texbake as tb
RADII = np.array([0.38, 0.34, 0.345])      # the v8 dome's half width, height, depth (headdome.py)
# the shape (fractions of the dome radius, by direction on the unit sphere d = (dx right, dy up, dz forward))
SHAPE = dict(
    box_p=2.5,        # superellipsoid exponent reached toward the top (2 = the ellipsoid): a flatter, fuller-shouldered crown
    box_front=0.55,   # how much the boxing is held back over the face (the front stays round)
    top=-0.045,       # the pole itself lowered
    cheek=0.055,      # the sides fuller round the gill roots
    brow=0.017,       # a soft ridge over the eyes
    muzzle=0.06,      # the lower front brought forward
    forehead=-0.025,  # the upper front sloped back
    neck=-0.05,       # the lower back drawn in toward the neck
)
GILL_YAW = 24.0       # degrees the gill strip turns forward about the dome's vertical axis
# the hang (v9b, the user's reference: the stalks drooping down the sides of the head like locks of hair): per stalk (top, middle,
# bottom), the direction of its first segment, of its second, and its stretch along its length; (out, up, forward) on the left side
HANG = [((0.62, -0.62, 0.22), (0.18, -1.0, 0.12), 1.32),
        ((0.7, -0.6, 0.0), (0.26, -1.0, -0.06), 1.08),
        ((0.75, -0.55, -0.22), (0.32, -1.0, -0.2), 0.9)]
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def adjacency(n, T):
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = np.unique(np.sort(e, 1), axis=0)
    A = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr(); return A, np.asarray(A.sum(1)).ravel()
def smooth_field(A, deg, x, mask, iters=8, lam=0.5):
    x = x.copy()
    for _ in range(iters):
        y = (A @ x) / np.maximum(deg, 1)[:, None]; x[mask] = (1 - lam) * x[mask] + lam * y[mask]
    return x
def shape_factor(d, K=SHAPE):
    """the radius multiplier for unit directions d (n, 3) about the dome centre"""
    dx, dy, dz = d[:, 0], d[:, 1], d[:, 2]; ax = np.abs(dx)
    # the superellipsoid: p rises toward the top, less over the face
    p = 2.0 + (K['box_p'] - 2.0) * ss((dy - 0.05) / 0.6) * (1.0 - K['box_front'] * ss((dz - 0.15) / 0.55))
    r = (ax ** p + np.abs(dy) ** p + np.abs(dz) ** p) ** (-1.0 / p)   # (= 1 on the ellipsoid for p = 2)
    f = r
    f += K['top'] * ss((dy - 0.55) / 0.45) ** 1.0
    f += K['cheek'] * np.exp(-((dy + 0.02) / 0.42) ** 2) * np.exp(-((dz + 0.05) / 0.5) ** 2) * ss((ax - 0.45) / 0.5)
    f += K['brow'] * np.exp(-((dy - 0.47) / 0.19) ** 2) * ss((dz - 0.1) / 0.5) * (1.0 - ss((ax - 0.55) / 0.3))
    f += K['muzzle'] * np.exp(-((dy + 0.32) / 0.42) ** 2) * ss((dz - 0.3) / 0.6) * (1.0 - 0.4 * ss((ax - 0.5) / 0.4))
    f += K['forehead'] * ss((dy - 0.3) / 0.5) * ss((dz - 0.2) / 0.55)
    f += K['neck'] * ss((-dy - 0.35) / 0.5) * ss((-dz - 0.05) / 0.5)
    return f
def yaw_field(P, C, roots, theta, phi_lo, phi_hi, y_lo, y_hi):
    """the turn (rad) of each point about the dome's vertical axis: theta on the gill strip, fading to 0 over the skin"""
    q = P - C; phi = np.degrees(np.arctan2(np.abs(q[:, 0]), q[:, 2]))   # 0 front, 180 back, both sides alike
    sgn = np.sign(q[:, 0]); sgn[sgn == 0] = 1
    bphi = ss((phi - (phi_lo - 80)) / 80) * (1.0 - ss((phi - phi_hi) / max(1e-3, 178 - phi_hi)))   # (an 80 degree ramp ahead: the skin there squeezes to 0.6, not 0.4)
    by = ss((q[:, 1] - (y_lo - 0.2)) / 0.2) * (1.0 - ss((q[:, 1] - y_hi) / 0.16))
    return theta * bphi * by * sgn   # (the left side turns forward one way, the right the other)
def quat_from_to(a, b):
    a = unit(a); b = unit(b); c = np.cross(a, b); d = float(np.dot(a, b))
    if d < -0.999999: ax = unit(np.cross(a, [1, 0, 0]) if abs(a[0]) < 0.9 else np.cross(a, [0, 1, 0])); return np.array([ax[0], ax[1], ax[2], 0.0])
    q = np.array([c[0], c[1], c[2], 1.0 + d]); return q / np.linalg.norm(q)
def qrot(q, v):
    x, y, z, w = q; u = np.array([x, y, z]); v = np.asarray(v, float)
    return v + 2.0 * np.cross(u, np.cross(u, v) + w * v)
def mkframe(y, x_hint):
    """a canonical frame quaternion: Y along y, X as close to x_hint as it can be, Z = X x Y (columns X, Y, Z)"""
    y = unit(y); x = unit(x_hint - y * np.dot(x_hint, y)); z = np.cross(x, y); M = np.stack([x, y, z], 1)
    t = np.trace(M)
    if t > 0: sq = np.sqrt(t + 1) * 2; q = np.array([(M[2, 1] - M[1, 2]) / sq, (M[0, 2] - M[2, 0]) / sq, (M[1, 0] - M[0, 1]) / sq, 0.25 * sq])
    else:
        i = int(np.argmax(np.diag(M))); j, k = (i + 1) % 3, (i + 2) % 3; sq = np.sqrt(1 + M[i, i] - M[j, j] - M[k, k]) * 2; q = np.zeros(4)
        q[i] = 0.25 * sq; q[j] = (M[j, i] + M[i, j]) / sq; q[k] = (M[k, i] + M[i, k]) / sq; q[3] = (M[k, j] - M[j, k]) / sq
    return q / np.linalg.norm(q)
def dqs(P, W, bones_rt, verbose_name=''):
    """dual quaternion skinning of points P (n, 3) by per-vertex bone weights W (n, nb) and per-bone rigid moves bones_rt: {b: (q, t)}
    (rotation q about the origin then translation t, i.e. p' = R p + t); bones not listed are the identity"""
    n, nb = W.shape; Q = np.zeros((nb, 4)); Q[:, 3] = 1; Tt = np.zeros((nb, 3))
    for b, (q, t) in bones_rt.items(): Q[b] = q; Tt[b] = t
    # dual parts: d = 0.5 * t * q (quaternion product with t as a pure quaternion)
    tx, ty, tz = Tt[:, 0], Tt[:, 1], Tt[:, 2]; qx, qy, qz, qw = Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 3]
    D = 0.5 * np.stack([tx * qw + ty * qz - tz * qy, ty * qw + tz * qx - tx * qz, tz * qw + tx * qy - ty * qx, -(tx * qx + ty * qy + tz * qz)], 1)
    # per vertex: the weights of the (few) bones that move, sign-corrected against the heaviest, the rest of the weight as the identity
    moving = np.array(sorted(bones_rt.keys())); Wm = W[:, moving]; wid = 1.0 - Wm.sum(1)
    ref = Q[moving[np.argmax(Wm, 1)]]; sgn = np.sign((Q[moving][None, :, :] * ref[:, None, :]).sum(2)); sgn[sgn == 0] = 1
    bq = (Wm * sgn)[:, :, None] * Q[moving][None]; bd = (Wm * sgn)[:, :, None] * D[moving][None]
    idq = np.zeros(4); idq[3] = 1; isg = np.sign(ref[:, 3]); isg[isg == 0] = 1
    qb = bq.sum(1) + (wid * isg)[:, None] * idq[None]; db = bd.sum(1)
    l = np.linalg.norm(qb, axis=1, keepdims=True); qb = qb / np.maximum(l, 1e-9); db = db / np.maximum(l, 1e-9)
    # p' = rot(qb, p) + 2 * (w * d.xyz - d.w * q.xyz + cross(q.xyz, d.xyz))
    u = qb[:, :3]; w = qb[:, 3:4]; rp = P + 2.0 * np.cross(u, np.cross(u, P) + w * P)
    tr = 2.0 * (w * db[:, :3] - db[:, 3:4] * u + np.cross(u, db[:, :3]))
    return rp + tr
def rot_y(a):
    c, s = np.cos(a), np.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz])
def reshape(nm, untex, tex, out, outsrc, verbose=True):
    r = tb.load_rt(nm, d=untex); P = r['P'].astype(float); T = r['T']; n = r['n']; W = r['W']; names = r['names']; bi = {k: i for i, k in enumerate(names)}
    meta = dict(r['meta']); C = np.array(meta['face']['c'], float)
    hw = W[:, bi['head']] + W[:, bi['headfront']]; gidx = [i for i, k in enumerate(names) if k.startswith('gill')]; gw = W[:, gidx].sum(1)
    # (gill weight counts only on the gills' own side of the head: the crawl's skin carries a few per cent of it down on the neck)
    q0 = P - C; phi0 = np.degrees(np.arctan2(np.abs(q0[:, 0]), q0[:, 2])); gw = gw * ((q0[:, 1] > -0.16) & (phi0 > 95) & (np.abs(q0[:, 0]) > 0.2))
    skin = gw < 0.02; s = ss((hw - 0.5) / 0.45) * skin
    # ---- the gill strip: its extent from the stalks' base rings (the verts that share their weight with the head) ----
    base = (gw >= 0.02) & (gw < 0.6); bq = P[base] - C; phi_b = np.degrees(np.arctan2(np.abs(bq[:, 0]), bq[:, 2]))
    phi_lo, phi_hi = phi_b.min() - 4, phi_b.max() + 4; y_lo, y_hi = bq[:, 1].min() - 0.02, bq[:, 1].max() + 0.03
    if verbose: print(f'{nm}: gill base ring phi {phi_b.min():.0f}..{phi_b.max():.0f} deg, y {bq[:, 1].min():.3f}..{bq[:, 1].max():.3f}; strip phi {phi_lo:.0f}..{phi_hi:.0f}, y {y_lo:.3f}..{y_hi:.3f}; stalks {int((gw >= 0.02).sum())} verts')
    th = -np.radians(GILL_YAW)   # (about +y a negative turn carries the +x side forward)
    roots = {k: np.array([b['pos'] for b in meta['bones'] if b['name'] == k][0]) for k in names if k.startswith('gill')}
    ang = yaw_field(P, C, roots, th, phi_lo, phi_hi, y_lo, y_hi)
    ang[gw >= 0.02] = th * np.sign(P[gw >= 0.02, 0] - C[0])   # (the stalks and their base rings: exactly rigid)
    # (the head group only: the neck and body never turn)
    ang *= ((hw + gw) > 0.02)
    q = P - C; cs, sn = np.cos(ang), np.sin(ang)
    Ps = np.stack([q[:, 0] * cs + q[:, 2] * sn, q[:, 1], -q[:, 0] * sn + q[:, 2] * cs], 1) + C   # (turned about the vertical axis through C)
    # ---- the shape: radial about C, on the turned skull; the stalks take their root's change as one shift each ----
    u = Ps - C; dist = np.linalg.norm(u, axis=1); d = u / np.maximum(dist, 1e-9)[:, None]
    f = shape_factor(d); delta_shape = (f - 1.0)[:, None] * u
    # each stalk vertex: the shift of the skin point under its own root (the nearest root joint's direction), so a stalk moves as one
    rp = np.array([roots[k] for k in names if k.startswith('gill') and k.endswith('.1')]); rq = rp - C
    rq = np.stack([rq[:, 0] * np.cos(th * np.sign(rq[:, 0])) + rq[:, 2] * np.sin(th * np.sign(rq[:, 0])), rq[:, 1], -rq[:, 0] * np.sin(th * np.sign(rq[:, 0])) + rq[:, 2] * np.cos(th * np.sign(rq[:, 0]))], 1)
    rd = unit(rq); rf = shape_factor(rd); rshift = (rf - 1.0)[:, None] * rq   # (per root: the radial change at the root's direction)
    _, nearest = cKDTree(rq + C).query(Ps); gk = np.clip((gw - 0.02) / 0.5, 0, 1); ws = np.maximum(s, np.clip(gw / 0.02, 0, 1))
    delta = (delta_shape * (1 - gk)[:, None] + rshift[nearest] * gk[:, None]) * ws[:, None]
    A, deg = adjacency(n, T); band = skin & (hw > 0.02) & (hw < 0.98)
    delta = smooth_field(A, deg, delta, band, iters=10)
    P2 = Ps + delta
    # ---- the gill bones so far: turned with the strip and shifted with their root's skin (the same as the bones block below) ----
    gb = {}
    for b in meta['bones']:
        if not b['name'].startswith('gill'): continue
        sgn = 1.0 if b['pos'][0] > 0 else -1.0; R = rot_y(th * sgn); root = roots[b['name'] if b['name'].endswith('.1') else b['name'][:-1] + '1']
        rq1 = R @ (root - C); shift = (shape_factor(unit(rq1)[None])[0] - 1.0) * rq1
        gb[b['name']] = dict(pos=R @ (np.array(b['pos']) - C) + C + shift, end=R @ (np.array(b['end']) - C) + C + shift, sgn=sgn)
    # ---- the hang: each stalk posed to droop down the side of the head (its first segment turned to HANG's first direction about its
    # root, its second bent on to the second direction, the whole stalk stretched along itself), and that pose baked into the rest
    # geometry through the mesh's own skin weights with dual quaternion blending, so the base rings and the fronds shared between
    # stalks blend exactly as the runtime's skinning blends them: no tearing. The bones take the posed joints and ends, and explicit new
    # canonical frames: Y down the stalk, X lateral (so the animator's flex swings the hanging stalk fore and aft, its swing sideways)
    moves = {}; newb = {}
    for k in range(3):
        for sgn in (1.0, -1.0):
            s_ = 'L' if sgn > 0 else 'R'; b1 = gb[f'gill{k}.{s_}.1']; b2 = gb[f'gill{k}.{s_}.2']; (o1, u1, f1), (o2, u2, f2), st = HANG[k]
            t1 = unit([sgn * o1, u1, f1]); t2 = unit([sgn * o2, u2, f2])
            d1 = unit(b1['end'] - b1['pos']); q1 = quat_from_to(d1, t1); j1 = b1['pos']
            d2w = qrot(q1, unit(b2['end'] - b2['pos'])); q2 = quat_from_to(d2w, t2)   # (the bend, on top of the first turn)
            j2 = j1 + qrot(q1, b2['pos'] - j1); e1 = j1 + (j2 - j1) * st; L2 = np.linalg.norm(b2['end'] - b2['pos']) * st
            Q2 = qmul(q2, q1); e2 = e1 + t2 * L2   # (the second joint sits where the stretched first segment ends)
            i1 = bi[f'gill{k}.{s_}.1']; i2 = bi[f'gill{k}.{s_}.2']
            # rigid moves (rotation about the origin + translation) for the dqs: segment 1 about j1; segment 2: its rotation Q2 about j2,
            # landing at e1 (the stretch of segment 1 is put in as a translation of segment 2 and as a per-vertex stretch below)
            moves[i1] = (q1, j1 - qrot(q1, j1)); moves[i2] = (Q2, e1 - qrot(Q2, b2['pos']))
            newb[f'gill{k}.{s_}.1'] = dict(pos=j1, end=e1, q=mkframe(t1, [sgn, 0, 0])); newb[f'gill{k}.{s_}.2'] = dict(pos=e1, end=e2, q=mkframe(t2, [sgn, 0, 0]))
    Pg = dqs(P2, W, moves)
    # the stretch along each stalk: a vertex moves out along its stalk's first direction by (st - 1) times how far along it sits
    for k in range(3):
        for sgn in (1.0, -1.0):
            s_ = 'L' if sgn > 0 else 'R'; i1 = bi[f'gill{k}.{s_}.1']; i2 = bi[f'gill{k}.{s_}.2']; st = HANG[k][2]; nb1 = newb[f'gill{k}.{s_}.1']
            wk = W[:, i1] + W[:, i2]; ax = unit(nb1['end'] - nb1['pos']); along = (Pg - nb1['pos']) @ ax
            Pg += (wk * (st - 1.0) * np.clip(along, 0, None))[:, None] * ax[None]
    P2 = Pg
    # ---- diagnostics: the skull's new extents, the roots, triangle quality ----
    core = (s > 0.99); qq = P2[core] - C
    def edge_stats(PP):
        e = np.concatenate([PP[T[:, 1]] - PP[T[:, 0]], PP[T[:, 2]] - PP[T[:, 1]], PP[T[:, 0]] - PP[T[:, 2]]]); return np.linalg.norm(e, axis=1)
    e0, e1 = edge_stats(P), edge_stats(P2); hm = ((hw + gw) > 0.02)[T].any(1); ratio = (e1 / np.maximum(e0, 1e-6)).reshape(3, -1).T[hm]
    moved = np.linalg.norm(P2 - P, axis=1)
    if verbose:
        print(f'  skull x {qq[:, 0].min():.3f}..{qq[:, 0].max():.3f} y {qq[:, 1].min():.3f}..{qq[:, 1].max():.3f} z {qq[:, 2].min():.3f}..{qq[:, 2].max():.3f}; '
              f'head verts moved mean {moved[core].mean() * 100:.1f} cm max {moved[core].max() * 100:.1f} cm; stalks moved mean {moved[gw > 0.5].mean() * 100:.1f} cm')
        print(f'  head-group edge length ratio new/old: min {ratio.min():.2f} p1 {np.percentile(ratio, 1):.2f} p99 {np.percentile(ratio, 99):.2f} max {ratio.max():.2f}')
        ht = np.where(hm)[0]; rr = ratio.ravel(); worst = np.argsort(np.abs(np.log(rr)))[-6:]
        for w in worst:
            ti = ht[w // 3]; a, b = T[ti, w % 3], T[ti, (w % 3 + 1) % 3]
            print(f'    edge ratio {rr[w]:.2f}: v{a} relC {np.round(P[a] - C, 3).tolist()} gw {gw[a]:.2f} hw {hw[a]:.2f} s {s[a]:.2f} | v{b} relC {np.round(P[b] - C, 3).tolist()} gw {gw[b]:.2f} hw {hw[b]:.2f} s {s[b]:.2f}')
    # ---- normals (area weighted), the canonical place, the bones, the meta ----
    fn = np.cross(P2[T[:, 1]] - P2[T[:, 0]], P2[T[:, 2]] - P2[T[:, 0]]); vn = np.zeros((n, 3))
    for k in range(3): np.add.at(vn, T[:, k], fn)
    N = unit(vn); Nq = np.zeros((n, 4), np.int8); Nq[:, :3] = np.clip(np.round(N * 127), -127, 127).astype(np.int8)
    cps = meta['cpScale']; cp = r['cp'].astype(float) / 32767 * cps; dP = P2 - P
    if nm == 'stand': cp[:, :3] = P2
    else: cp[:, :3] += dP
    cq = np.zeros((n, 4), np.int16); cq[:, :3] = np.clip(np.round(cp[:, :3] / cps * 32767), -32767, 32767); cq[:, 3] = r['cp'][:, 3]
    bones = []
    for b in meta['bones']:
        b = dict(b)
        if b['name'].startswith('gill'):
            nb_ = newb[b['name']]; b['pos'] = np.round(nb_['pos'], 4).tolist(); b['end'] = np.round(nb_['end'], 4).tolist(); b['q'] = np.round(nb_['q'], 4).tolist()
        bones.append(b)
    meta['bones'] = bones; meta['bbox'] = [P2.min(0).round(4).tolist(), P2.max(0).round(4).tolist()]
    if verbose:
        for b in bones:
            if b['name'].startswith('gill') and '.L' in b['name']: print(f'  {b["name"]}: pos {b["pos"]} end {b["end"]} q {b["q"]} (rel C {np.round(np.array(b["pos"]) - C, 3).tolist()}, tip rel C {np.round(np.array(b["end"]) - C, 3).tolist()})')
    # ---- the untextured mesh (reference) ----
    os.makedirs(outsrc, exist_ok=True)
    parts = [('position', P2.astype(np.float32)), ('normal', Nq), ('skinIndex', r['si']), ('skinWeight', r['sw']), ('index', T.astype(np.uint16).ravel()), ('cpos', cq), ('jelly', r['jelly']), ('fill', r['fill']), ('mat', r['mat'])]
    off = {}; o = 0; blobs = []
    for k, arr in parts:
        bb = np.ascontiguousarray(arr).tobytes(); off[k] = o; blobs.append((o, bb)); o += len(bb); o += (-o) % 4
    buf = bytearray(o)
    for of, bb in blobs: buf[of:of + len(bb)] = bb
    m2 = dict(meta); m2['off7'] = off; open(f'{outsrc}/axo_{nm}.bin', 'wb').write(buf); json.dump(m2, open(f'{outsrc}/axo_{nm}.json', 'w'))
    # ---- the textured mesh: its vertices are copies of these (texbake's vm), found by exact position; the three sections rewritten in place ----
    mt = json.load(open(f'{tex}/axo_{nm}.json')); bt = bytearray(open(f'{tex}/axo_{nm}.bin', 'rb').read()); ot = mt['off7']; n2 = mt['n']
    Pt = np.frombuffer(bytes(bt), np.float32, n2 * 3, ot['position']).reshape(n2, 3)
    _, vm = cKDTree(P.astype(np.float32)).query(Pt); miss = np.linalg.norm(P[vm] - Pt, axis=1)
    assert miss.max() < 1e-6, f'textured mesh is not a copy of the untextured one (max {miss.max()})'
    bt[ot['position']:ot['position'] + n2 * 12] = P2.astype(np.float32)[vm].tobytes()
    bt[ot['normal']:ot['normal'] + n2 * 4] = Nq[vm].tobytes()
    bt[ot['cpos']:ot['cpos'] + n2 * 8] = cq[vm].tobytes()
    for k in ('bones', 'bbox', 'face', 'headc', 'headr'): mt[k] = meta[k]
    os.makedirs(out, exist_ok=True); open(f'{out}/axo_{nm}.bin', 'wb').write(bt); json.dump(mt, open(f'{out}/axo_{nm}.json', 'w'))
    if verbose: print(f'  {out}/axo_{nm}.bin {len(bt)} bytes ({n2} verts), {outsrc}/axo_{nm}.bin {len(buf)} bytes ({n} verts); face c {meta["face"]["c"]} r {meta["face"]["r"]}; headc {meta["headc"]} headr {meta["headr"]}')
if __name__ == '__main__':
    a = sys.argv[1:]; untex = S + '/fable/rt2src'; tex = S + '/fable/rt2'; out = WORK + '/rt3'; outsrc = WORK + '/rt3src'
    while a:
        k = a.pop(0)
        if k == '--untex': untex = a.pop(0)
        elif k == '--tex': tex = a.pop(0)
        elif k == '--out': out = a.pop(0)
        elif k == '--outsrc': outsrc = a.pop(0)
        elif k == '--yaw': GILL_YAW = float(a.pop(0))
        elif k.startswith('--') and k[2:] in SHAPE: SHAPE[k[2:]] = float(a.pop(0))
    for nm in ('stand', 'crawl'): reshape(nm, untex, tex, out, outsrc)
