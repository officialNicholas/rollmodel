# The slime's head and floppy ears on the axolotl body (v10). The user: "take the old head and the ears and put it on top of this
# character". The axolotl's own skull (the v9 shaped dome) is re-laid onto the slime's head surface: every head vertex is cast from the
# face centre along its own direction onto the slime's head mesh (scaled about the slime's face centre, which lands on the axolotl's), so
# the surface IS the slime's own jelly ball, with its gently flattened face front, on the axolotl head's topology (its atlas UVs, skin
# weights, face frame and attributes survive). Where the slime's head ball ends (its underside runs straight into its body, which has no
# chin and a narrower neck than the axolotl's) the axolotl's own underside stays and the two are blended and smoothed, and the neck is
# never let get thinner than it is (the user: a thick neck flowing into the shoulders, no crease). The six v9b gill lobes go, and the old
# gill stalks (retired by v9b: collapsed into caps whose fans straddled the atlas) are dropped outright, each base ring's hole closed
# by a fresh fan in the ring's own chart. The slime's two ears come over as they are: its ear meshes (the 'rig' green channel, root 0 ..
# tip 1), scaled and placed with the head, bent into the slime's resting hang (its EAR_REST: tipped in toward the face and a little
# forward, more toward the tip), their root ring sunk a hair inside the skull, skinned to the head at the root and to the gill0 chain
# (.1 the upper half, .2 the lower half) with Y down the ear and X lateral, so the animator's flex swings an ear fore and aft and its
# swing sideways. The other four gill bones stay in the rig, at the ear's hinge, with no geometry.
# Reads the v9b meshes (fable2/rt3src untextured, rt3 textured) and writes fable3/rt4src and rt4 (the same layout, the atlas and
# texture bytes carried over; the old rings' texels repainted skin by capfix.py after this):
#   python3 -I slimehead.py [--untex S/fable2/rt3src] [--tex S/fable2/rt3] [--out S/fable3/rt4] [--outsrc S/fable3/rt4src] [--scale 0.87]
import sys, os, json, re, base64, struct
import numpy as np
from scipy.sparse import coo_matrix
from scipy.spatial import cKDTree
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
WORK = S + '/fable3'
sys.path.insert(0, '/home/user/rollmodel/axo/tools4')
import texbake as tb
SLIME_PACK = S + '/fable2/slime/slime-pack.txt'
SCALE = 0.87                                  # the slime's head at 0.87 of its size: its ball about the axolotl's present head (a touch narrower, taller)
SLIME_HEAD = np.array([0.0, 0.231, 0.547]); SLIME_R = 0.425; SLIME_EAR = np.array([0.37, 0.37, 0.48])   # its meta: the face centre, its radius, the ear hinge (+x side)
EAR_REST = (-0.3, 0.16)                       # the slime's ears at rest (its EAR_REST: flap about z, in toward the face; swing about x, forward), times the ear coordinate
RING_IN = 0.005                               # the ear root ring sunk this far into the skull; the root band lifted off the skull by RING_OUT so the two surfaces never fight
RING_OUT = 0.003                              # (a deep ring cut a visible groove along the root: the ear's outer surface diving into the skull)
N_LOBE = 1266                                 # the v9b lobes appended at the end of each mesh (6 x 211)
# ---- v10d, the lizard body (--lizard; the user: one body, head, neck and trunk; a bearded dragon's taper; the body a little bigger
# against the head): the trunk, limbs and tail K_BODY bigger (the head keeps headr), the trunk re-proportioned by station along its
# length (lateral mw, dorsoventral md: wide at the shoulders, tapering through the hips into the tail), the limb chains moved with
# the trunk's sides, the crawl's head brought back and down the neck axis by DROP, the head joint set just above the chest's end,
# and the join built as the union of the ball and a dome tangent to it (no fillet, no fold, no step) ----
LIZARD = False; K_BODY = 1.13; NECK_LEN = 0.02; BRIDGE = True
# (the v9b trunk is narrow: 0.19 to 0.22 across at the chest once scaled, against the ball's 0.365 at the join, so the shoulders go out
# to about 1.6 times; the stand's chest forward 1.15 and its back 1.35 (mdb), the crawl keeps its height)
# the trunk's target half extents by station (m, after the K_BODY scale; None keeps the trunk's own): wx across, the stand's zf forward
# and zb back of the spine; the multiplier at a station is the target over the trunk's own 95th-percentile extent measured there
# (v10e, the crawl only: the taper carried on through the hips into the tail's root (a bearded dragon's, not a step from the hips to a
# thin tail): stations behind tail_from measure the tail's own extents too; limb_meas, the limb weight under which a vertex counts as
# the trunk's when its extent is measured (at 0.6 the thighs' roots made the hips read wide, and the hips were pinched); tail_k, the
# tail's own scale (1: its old length; K_BODY's longer tail curled up over the head in the front views); and the back deepest just
# behind the front legs, sloping down to the hips: dst / dmul, the height above the belly line times dmul, by station along z, the
# belly kept on the ground)
LIZ = {'stand': dict(st=[0.40, 0.56, 0.667, 0.75, 0.82, 0.88, 0.94, 1.00], wx=[None, None, 0.27, 0.30, 0.33, 0.35, 0.36, None], zf=[None, None, None, 0.24, 0.25, 0.26, 0.27, None], zb=[None, None, None, 0.23, 0.24, 0.25, 0.26, None], drop=0.0, move=[0.0, 0.0, 0.07]),
       'crawl': dict(st=[-2.0, -1.8, -1.6, -1.45, -1.3, -1.15, -1.01, -0.878, -0.72, -0.58, -0.42, -0.28, -0.14, -0.08], wx=[None, 0.08, 0.105, 0.125, 0.155, 0.19, 0.23, 0.26, 0.29, 0.32, 0.35, 0.37, 0.37, None],
                     zf=[None] * 14, zb=[None] * 14, tail_from=-0.95, limb_meas=0.15, tail_k=1.0, dst=[-0.75, -0.6, -0.45, -0.3, -0.14, -0.06], dmul=[1.0, 1.06, 1.12, 1.15, 1.13, 1.0], drop=0.10)}
DJ = (0.21, 0.06, 0.10)                       # the join on the ball, this far below its centre: under the chin (front), the cheeks (side), the nape (back)
# ---- v10e, the bridge (the user: "it needs to look more like one body: the head, neck and body"; "more smooth"): the head's underside,
# the throat, the neck and the top of the trunk are thrown away as shapes and laid again as one surface, a loft of cubic curves (one per
# 2 degrees round an axis from the trunk to the face centre) from a loop on the ball (where the line from the trunk touches it, the
# convex hull, kept below the mouth) to the trunk's cross-section in a plane across it, tangent to the ball at the top and to the trunk at
# the bottom: no neck column, no fold, no step. The vertices between keep their order: the zone is cut open along the back and laid out
# flat (Tutte: each vertex the mean of its neighbours, the edges held), so no triangle turns over. The arms' roots ride with the loft.
# Per body: QB a point on the plane at the trunk's middle and nB its normal (toward the head), fwd the azimuth origin (the throat);
# elA_max / elA_min the loop's elevation limits (deg, front / side / back, about the axis); muA the curves' tangent at the ball (times
# the chord); limb_cut the arm weight above which a vertex is the arm's own (moved with it, not laid on the loft). The curves leave the
# trunk with no bend (flatB: a straight run on past the plane meets them with no step in the curvature, which read as a line across the
# back). The crawl's loop sits 30 degrees up at the front (it was 14): between 14 and about 35 degrees the slime's ball runs flatter, into
# its own neck, and the loft met it there in an S, a line just under the mouth; from 30 up the chin is round and the sweep from the mouth
# down the throat to the chest is one convex curve ----
BRIDGE_CFG = {'stand': dict(QB=[0.0, 0.93, 0.0], nB=[0.0, 1.0, 0.0], fwd=[0.0, 0.0, 1.0], elA_max=(-18, -12, -20), elA_min=(-18, -80, -80), muA=(0.7, 0.8, 0.8), limb_cut=0.7),
              'crawl': dict(QB=[0.0, 0.26, -0.14], nB=[0.0, 0.0, 1.0], fwd=[0.0, -1.0, 0.3], elA_max=(30, 0, 0), elA_min=(30, 0, -80), muA=(0.7, 0.8, 0.8), limb_cut=0.5)}
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def adjacency(n, T):
    e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = np.unique(np.sort(e, 1), axis=0)
    A = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr(); return A, np.asarray(A.sum(1)).ravel()
def mkframe(y, x_hint):
    """a canonical frame quaternion: Y along y, X as close to x_hint as it can be, Z = X x Y (columns X, Y, Z)"""
    y = unit(y); x = unit(x_hint - y * np.dot(x_hint, y)); z = np.cross(x, y); M = np.stack([x, y, z], 1)
    t = np.trace(M)
    if t > 0: sq = np.sqrt(t + 1) * 2; q = np.array([(M[2, 1] - M[1, 2]) / sq, (M[0, 2] - M[2, 0]) / sq, (M[1, 0] - M[0, 1]) / sq, 0.25 * sq])
    else:
        i = int(np.argmax(np.diag(M))); j, k = (i + 1) % 3, (i + 2) % 3; sq = np.sqrt(1 + M[i, i] - M[j, j] - M[k, k]) * 2; q = np.zeros(4)
        q[i] = 0.25 * sq; q[j] = (M[j, i] + M[i, j]) / sq; q[k] = (M[k, i] + M[i, k]) / sq; q[3] = (M[k, j] - M[j, k]) / sq
    return q / np.linalg.norm(q)
def rot_axis(v, axis, t):
    """Rodrigues: v (n, 3) turned about the unit axis by t (n,) or scalar"""
    axis = np.asarray(axis, float); t = np.asarray(t, float).reshape(-1, 1); c = np.cos(t); s = np.sin(t)
    return v * c + np.cross(axis, v) * s + axis * (v @ axis)[:, None] * (1 - c)
def vnormals(P, T):
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); vn = np.zeros_like(P)
    for k in range(3): np.add.at(vn, T[:, k], fn)
    return unit(vn)
def boundary_chains(T, cand):
    """the open edges of T (on one triangle only) whose both ends are candidates, as chains of directed edges (a -> b as the triangle
    has it): lists of vertex indices, closed when the last equals the first"""
    E = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); key = np.sort(E, 1); _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    inv = inv.ravel(); openE = E[(cnt[inv] == 1) & cand[E].all(1)]
    nxt = {}; [nxt.setdefault(int(a), []).append(int(b)) for a, b in openE]; used = set(); chains = []
    for a0 in list(nxt.keys()):
        for b0 in nxt[a0]:
            if (a0, b0) in used: continue
            ch = [a0, b0]; used.add((a0, b0)); a, b = a0, b0
            while b in nxt and b != a0:
                c = next((c for c in nxt[b] if (b, c) not in used), None)
                if c is None: break
                used.add((b, c)); ch.append(c); b = c
            # (an open chain: walk back from its start too)
            if ch[-1] != ch[0]:
                prev = {}; [prev.setdefault(int(b_), []).append(int(a_)) for a_, b_ in openE]; a = ch[0]
                while a in prev:
                    p = next((p for p in prev[a] if (p, a) not in used), None)
                    if p is None: break
                    used.add((p, a)); ch.insert(0, p); a = p
            chains.append(ch)
    return chains
def on_ball(P, vs, C):
    """a centre for the hole rimmed by vertices vs: their mean, pushed out onto the ball's surface over it"""
    c = P[vs].mean(0); rr = np.linalg.norm(P[vs] - c, axis=1).mean(); R = np.linalg.norm(c - C); sag = R - np.sqrt(max(R * R - rr * rr, 0.0)); return c + unit(c - C) * sag
def close_holes(P, T, cand, C):
    """every hole rimmed by candidate vertices closed with a fan to one new centre vertex (on the ball's surface over it): chains of
    open edges that share a vertex are one hole. Returns the centres (new vertices numbered from len(P)), the fan triangles, per
    centre a rim vertex to copy attributes from, and per vertex the hole it rims (-1 elsewhere)"""
    chains = boundary_chains(T, cand); parent = list(range(len(chains)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    seen = {}
    for ci, ch in enumerate(chains):
        for v in set(ch):
            if v in seen: parent[find(ci)] = find(seen[v])
            else: seen[v] = ci
    roots = sorted(set(find(i) for i in range(len(chains)))); gid = {r: k for k, r in enumerate(roots)}; cg = [gid[find(i)] for i in range(len(chains))]
    vgroup = -np.ones(len(P), np.int64); cen = []; rep = []
    for k in range(len(roots)):
        vs = sorted(set(v for ci, ch in enumerate(chains) if cg[ci] == k for v in ch)); vgroup[vs] = k; cen.append(on_ball(P, vs, C)); rep.append(vs[0])
    tris = [[b, a, len(P) + cg[ci]] for ci, ch in enumerate(chains) for a, b in zip(ch[:-1], ch[1:])]   # (each edge the other way round: wound with the skin it borders)
    return np.array(cen).reshape(-1, 3), np.array(tris, np.int64).reshape(-1, 3), rep, vgroup
def close_holes_tex(P, T, cand, C, vgroup, centres):
    """the textured mesh's holes: its rim copies chain per chart; every chain of a hole fans to its own copy of the hole's one centre (the
    copy carries the chart's uv), so the fans tile the hole with no sliver. Returns the centre copies, the fans, per copy a rim vertex
    to copy attributes from, and per copy its chain (for the uv)"""
    chains = boundary_chains(T, cand); cen = []; rep = []; tris = []; src = []
    for ch in chains:
        gs = [int(vgroup[v]) for v in ch if vgroup[v] >= 0]
        if not gs: continue
        g = max(set(gs), key=gs.count); i = len(P) + len(cen); cen.append(centres[g]); rep.append(ch[0]); src.append(ch)
        for a, b in zip(ch[:-1], ch[1:]): tris.append([b, a, i])
    return np.array(cen).reshape(-1, 3), np.array(tris, np.int64).reshape(-1, 3), rep, src
# ---------------- the slime ----------------
def load_slime():
    t = re.sub(r'[^A-Za-z0-9+/=]', '', open(SLIME_PACK).read()); buf = base64.b64decode(t); assert buf[:4] == b'RMS1'
    hl = struct.unpack('<I', buf[4:8])[0]; head = json.loads(buf[8:8 + hl]); base = 8 + hl; m = head['meshes']['slime']; v = m['v']
    P = np.frombuffer(buf, np.uint16, v * 3, base + m['pos']).reshape(v, 3).astype(float) / 65535 * (np.array(m['mx']) - np.array(m['mn'])) + np.array(m['mn'])
    T = np.frombuffer(buf, np.uint16, m['i'], base + m['idx']).reshape(-1, 3).astype(np.int64)
    rig = np.frombuffer(buf, np.uint8, v * 4, base + m['rig']).reshape(v, 4) / 255.0; rig2 = np.frombuffer(buf, np.uint8, v * 4, base + m['rig2']).reshape(v, 4) / 255.0
    meta = head['meta']['slime']; assert np.allclose(meta['head'][:3], SLIME_HEAD) and np.allclose(meta['ears'], SLIME_EAR)
    return dict(P=P, T=T, hw=rig[:, 0], ew=rig[:, 1], stub=rig2[:, 1])
def cast(orig, dirs, V, F, attr):
    """the first hit along each ray (orig + t dirs, t > 0.05) on triangles F of V: t (inf where none) and attr interpolated at the hit"""
    n = len(dirs); best = np.full(n, np.inf); hit_a = np.zeros(n); A = V[F[:, 0]]; E1 = V[F[:, 1]] - A; E2 = V[F[:, 2]] - A; a0, a1, a2 = attr[F[:, 0]], attr[F[:, 1]], attr[F[:, 2]]
    for c0 in range(0, n, 512):
        d = dirs[c0:c0 + 512]; m = len(d)
        pv = np.cross(d[:, None, :], E2[None, :, :]); det = (E1[None] * pv).sum(2); ok = np.abs(det) > 1e-9; inv = 1.0 / np.where(ok, det, 1.0)
        tv = orig[None, None, :] - A[None]; u = (tv * pv).sum(2) * inv; qv = np.cross(tv, E1[None]); vv = (d[:, None, :] * qv).sum(2) * inv; t = (E2[None] * qv).sum(2) * inv
        good = ok & (u >= -1e-4) & (vv >= -1e-4) & (u + vv <= 1 + 1e-4) & (t > 0.05); t = np.where(good, t, np.inf); j = np.argmin(t, 1); tb_ = t[np.arange(m), j]
        w = np.clip(u[np.arange(m), j], 0, 1); w2 = np.clip(vv[np.arange(m), j], 0, 1)
        best[c0:c0 + m] = tb_; hit_a[c0:c0 + m] = (1 - w - w2) * a0[j] + w * a1[j] + w2 * a2[j]
    return best, hit_a
def cast_from(origs, dirs, V, F, attr):
    """cast() with its own start per ray (t > 1e-3): t (inf where none) and attr at the hit"""
    n = len(dirs); best = np.full(n, np.inf); hit_a = np.zeros(n); A = V[F[:, 0]]; E1 = V[F[:, 1]] - A; E2 = V[F[:, 2]] - A; a0, a1, a2 = attr[F[:, 0]], attr[F[:, 1]], attr[F[:, 2]]
    for c0 in range(0, n, 256):
        d = dirs[c0:c0 + 256]; o = origs[c0:c0 + 256]; m = len(d)
        pv = np.cross(d[:, None, :], E2[None, :, :]); det = (E1[None] * pv).sum(2); ok = np.abs(det) > 1e-9; inv = 1.0 / np.where(ok, det, 1.0)
        tv = o[:, None, :] - A[None]; u = (tv * pv).sum(2) * inv; qv = np.cross(tv, E1[None]); vv = (d[:, None, :] * qv).sum(2) * inv; t = (E2[None] * qv).sum(2) * inv
        good = ok & (u >= -1e-4) & (vv >= -1e-4) & (u + vv <= 1 + 1e-4) & (t > 1e-3); t = np.where(good, t, np.inf); j = np.argmin(t, 1); tb_ = t[np.arange(m), j]
        w = np.clip(u[np.arange(m), j], 0, 1); w2 = np.clip(vv[np.arange(m), j], 0, 1)
        best[c0:c0 + m] = tb_; hit_a[c0:c0 + m] = (1 - w - w2) * a0[j] + w * a1[j] + w2 * a2[j]
    return best, hit_a
def lizard_body(P, W, meta, names, bi, hw, nm, verbose=True):
    """v10d: the body K_BODY bigger about the origin (the skull not), the trunk re-proportioned by station (x by mw, the stand's z by md
    about the spine), each limb chain moved sideways with the trunk's side at its root, the crawl's head back and down the neck axis,
    the head joint NECK_LEN above the chest's end. Returns the positions, the bones, the face centre, and the numbers for the report"""
    L = LIZ[nm]; k = K_BODY; B0 = {b['name']: b for b in meta['bones']}; C0 = np.array(meta['face']['c'], float)
    hs = ss((hw - 0.1) / 0.8); sv = k - (k - 1) * hs; P = P * sv[:, None]
    bones = []
    for b in meta['bones']:
        b = dict(b); b['pos'] = (np.array(b['pos']) * k).tolist(); b['end'] = (np.array(b['end']) * k).tolist(); bones.append(b)
    B = {b['name']: b for b in bones}; ax = 1 if nm == 'stand' else 2
    st = P[:, ax]; zs = B['spine']['pos'][2] if nm == 'stand' else 0.0
    arm_all = W[:, [i for i, q in enumerate(names) if q.startswith(('upperarm', 'forearm', 'hand', 'finger'))]].sum(1); leg_all = W[:, [i for i, q in enumerate(names) if q.startswith(('thigh', 'shin', 'foot', 'toes', 'toe'))]].sum(1)
    tail_all = W[:, [i for i, q in enumerate(names) if q.startswith('tail')]].sum(1)
    lm_ = L.get('limb_meas', 0.6)                                                 # (the crawl measures its trunk clear of the thighs' roots: its hips were read wide, and pinched)
    tm = (arm_all + leg_all < lm_) & (hw < 0.3) & (tail_all < 0.3) & (W[:, [i for i, q in enumerate(names) if q.startswith('gill')]].sum(1) < 0.02)   # (the trunk's own vertices, for its extents)
    tmx = tm | ((arm_all + leg_all < lm_) & (hw < 0.3) & (tail_all >= 0.3))                                      # (and the tail's own, for stations behind tail_from)
    def mult(key, val):
        m_ = []; e_ = []
        for s0, w0 in zip(L['st'], L[key]):
            if w0 is None: m_.append(1.0); e_.append(None); continue
            band = (tmx if s0 < L.get('tail_from', -1e9) else tm) & (np.abs(st - s0) < 0.035); e = np.percentile(val[band], 95) if band.sum() > 8 else np.nan
            if np.isfinite(e) and e > 0.02: m_.append(float(w0 / e)); e_.append(float(e))
            else: m_.append(m_[-1] if m_ else 1.0); e_.append(e_[-1] if e_ else None)   # (no trunk vertices at this station: carry the last one on)
        return np.interp(st, L['st'], m_), [round(x, 2) for x in m_], e_
    mw, mw_t, ex_ = mult('wx', np.abs(P[:, 0])); md, md_t, _ = mult('zf', np.maximum(P[:, 2] - zs, 0)); mdb, mdb_t, _ = mult('zb', np.maximum(zs - P[:, 2], 0))
    if verbose: print(f'  lizard multipliers by station {L["st"]}: across {mw_t} (own extents {[round(e, 3) if e else None for e in ex_]}), forward {md_t}, back {mdb_t}')
    arm = lambda sd: W[:, [i for i, q in enumerate(names) if q.startswith(('upperarm', 'forearm', 'hand', 'finger')) and f'.{sd}' in q]].sum(1)
    leg = lambda sd: W[:, [i for i, q in enumerate(names) if q.startswith(('thigh', 'shin', 'foot', 'toes', 'toe')) and f'.{sd}' in q]].sum(1)
    lw = {('arm', 'L'): arm('L'), ('arm', 'R'): arm('R'), ('leg', 'L'): leg('L'), ('leg', 'R'): leg('R')}
    trunk = np.clip(1 - sum(lw.values()), 0, 1) * (1 - hs)
    Pn = P.copy(); Pn[:, 0] = P[:, 0] * (1 + (mw - 1) * trunk)
    if nm == 'stand': Pn[:, 2] = zs + (P[:, 2] - zs) * (1 + (np.where(P[:, 2] > zs, md, mdb) - 1) * trunk)
    if 'dst' in L:                                                                # (the crawl's back raised over the belly line, by station)
        yb_ = []
        for s0 in L['dst']:
            band = tm & (np.abs(st - s0) < 0.035); yb_.append(float(np.percentile(P[band, 1], 3)) if band.sum() > 8 else (yb_[-1] if yb_ else 0.0))
        yb = np.interp(st, L['dst'], yb_); mdep = np.interp(st, L['dst'], L['dmul'])
        Pn[:, 1] = yb + (P[:, 1] - yb) * (1 + (mdep - 1) * trunk)
        if verbose: print(f'  lizard depth by station {L["dst"]}: x{L["dmul"]} over the belly line {np.round(yb_, 3).tolist()}')
    moved = {}
    for sd in 'LR':
        for kind, root, chain in (('arm', 'shoulder', ('upperarm', 'forearm', 'hand', 'finger')), ('leg', 'thigh', ('thigh', 'shin', 'foot', 'toes', 'toe'))):
            rb = B[f'{root}.{sd}']; rp = np.array(rb['end'] if root == 'shoulder' else rb['pos']); wt_ = np.interp(rp[ax], L['st'], [w if w is not None else np.nan for w in L['wx']])
            ex0 = np.interp(rp[ax], L['st'], [e if e is not None else np.nan for e in ex_]); dx = float(np.clip(wt_ - ex0, -0.05, 0.25)) if np.isfinite(wt_ + ex0) else 0.0
            dx = min(dx, wt_ - 0.06 - abs(rp[0])) if np.isfinite(wt_) else dx; dx = dx * np.sign(rp[0]); dv = np.array([dx, 0.0, 0.0])
            if kind == 'arm' and BRIDGE: dv[:] = 0.0; dx = 0.0   # (the arms go where the bridge's shoulders put them, below)
            if root == 'shoulder': rb['end'] = (np.array(rb['end']) + dv).tolist()
            for b in bones:
                if b['name'].startswith(chain) and f'.{sd}' in b['name']: b['pos'] = (np.array(b['pos']) + dv).tolist(); b['end'] = (np.array(b['end']) + dv).tolist()
            Pn += dv[None, :] * lw[(kind, sd)][:, None]; moved[f'{kind}.{sd}'] = round(float(dx), 4)
    if 'tail_k' in L:                                                             # (the crawl's tail kept its own length: K_BODY's longer tail curled up over the head in front views)
        ct = L['tail_k'] / k; r0 = np.array(B['tail1']['pos'], float); tw_ = np.clip(tail_all, 0, 1)
        Pn[:, 1:] += tw_[:, None] * (r0[None, 1:] + (Pn[:, 1:] - r0[None, 1:]) * ct - Pn[:, 1:])
        for b in bones:
            if b['name'].startswith('tail'):
                for key_ in ('pos', 'end'): q_ = np.array(b[key_], float); q_[1:] = r0[1:] + (q_[1:] - r0[1:]) * ct; b[key_] = q_.round(5).tolist()
        if verbose: print(f'  lizard: the tail scaled x{ct:.3f} (height and length) about its root {r0.round(3).tolist()}')
    nax = unit(np.array(B['neck']['end']) - np.array(B['neck']['pos'])); drop = L['drop']; mv = np.array(L.get('move', [0.0, 0.0, 0.0])) - drop * nax; C = C0 + mv
    Pn += mv[None, :] * hs[:, None]
    hbj = np.array(B['chest']['end']) + NECK_LEN * nax; hb0 = np.array(B0['head']['pos'])
    B['neck']['pos'] = list(B['chest']['end']); B['neck']['end'] = hbj.round(5).tolist()
    B['head']['pos'] = hbj.round(5).tolist(); B['head']['end'] = (hbj + np.array(B0['head']['end']) - hb0).round(5).tolist()
    for q in ('headfront',): B[q]['pos'] = (C + np.array(B0[q]['pos']) - C0).round(5).tolist(); B[q]['end'] = (C + np.array(B0[q]['end']) - C0).round(5).tolist()
    info = dict(C=C.round(4).tolist(), hbj=hbj.round(4).tolist(), headc=(C - hbj).round(4).tolist(), limbs=moved, drop=drop, k=k,
                hand=np.array(B['hand.L']['end']).round(3).tolist(), hand0=(np.array(B0['hand.L']['end'])).round(3).tolist(), foot=np.array(B['toes.L']['end']).round(3).tolist(), foot0=np.array(B0['toes.L']['end']).round(3).tolist())
    if verbose: print(f'  lizard: body x{k}, limb roots moved {moved}; head drop {drop} along the neck axis; face.c {info["C"]} head joint {info["hbj"]} headc {info["headc"]}; hand.L end {info["hand0"]} -> {info["hand"]}, toes.L end {info["foot0"]} -> {info["foot"]}')
    return Pn, bones, C, info
def circ_smooth(y, w=3):
    """a moving average round a closed loop (y sampled over 360 degrees)"""
    if w <= 0: return y
    k = np.ones(2 * w + 1) / (2 * w + 1); yy = np.concatenate([y[-w:], y, y[:w]], 0)
    if yy.ndim == 1: return np.convolve(yy, k, 'valid')
    return np.stack([np.convolve(yy[:, j], k, 'valid') for j in range(yy.shape[1])], 1)
def lowpass(y, keep=8):
    """a closed loop sampled round 360 degrees, its Fourier series cut after `keep` harmonics"""
    Fy = np.fft.rfft(y, axis=0); Fy[keep + 1:] = 0; return np.fft.irfft(Fy, n=len(y), axis=0)
def hermite(A, tA, B, tB, t, mu=1.0, mu1=None, flatB=False):
    """the cubic from A (leaving along tA) to B (arriving along tB), its end tangents mu (mu1 at B) times the chord. flatB: no bend left
    at B (the quintic with the cubic's own start, its second derivative at B taken away by t^3 (1 - t)^2 / 2), so a straight run on past B
    meets it with no step in the curvature either"""
    L = np.linalg.norm(B - A, axis=-1, keepdims=True); t = t[..., None]; m0 = np.asarray(mu, float); m1 = m0 if mu1 is None else np.asarray(mu1, float)
    if m0.ndim: m0 = m0.reshape(m0.shape + (1,) * (L.ndim - m0.ndim))
    if m1.ndim: m1 = m1.reshape(m1.shape + (1,) * (L.ndim - m1.ndim))
    h00 = 2 * t ** 3 - 3 * t ** 2 + 1; h10 = t ** 3 - 2 * t ** 2 + t; h01 = -2 * t ** 3 + 3 * t ** 2; h11 = t ** 3 - t ** 2
    out = h00 * A + h10 * L * m0 * tA + h01 * B + h11 * L * m1 * tB
    if flatB: out = out - (6 * A + 2 * L * m0 * tA - 6 * B + 4 * L * m1 * tB) * (t ** 3 * (1 - t) ** 2 / 2)
    return out
def solve_fixed(Adj, fixed, X0):
    """each free vertex the mean of its neighbours (the graph Laplacian), the fixed ones held: X (n, k)"""
    from scipy.sparse import diags
    from scipy.sparse.linalg import splu
    deg = np.asarray(Adj.sum(1)).ravel(); L = (diags(deg) - Adj).tocsr(); free = ~fixed; X = X0.copy()
    lu = splu(L[free][:, free].tocsc()); rhs = -L[free][:, fixed] @ X0[fixed]; X[free] = np.stack([lu.solve(np.ascontiguousarray(rhs[:, j])) for j in range(X0.shape[1])], 1); return X
class Loft:
    """the bridge: a cubic per meridian (NPH round the axis) from A on the ball to B on the trunk, arc-length tables for each; at(phi, t)
    the surface at azimuths phi (deg) and arc-length fractions t, t < 0 running on up the ball's own profile and t > 1 on down the trunk"""
    def __init__(s, PH, A, tA, B, tB, mu, mu1=1.0, ball=None, nt=97, flatB=False):
        s.PH = PH; s.ts = np.linspace(0, 1, nt); s.A, s.tA, s.B, s.tB, s.ball, s.flatB = A, tA, B, tB, ball, flatB
        s.mu = np.broadcast_to(np.asarray(mu, float), (len(PH),)).copy(); s.mu1 = np.broadcast_to(np.asarray(mu1, float), (len(PH),)).copy()
        s.Cv = hermite(A[:, None], tA[:, None], B[:, None], -tB[:, None], np.broadcast_to(s.ts, (len(PH), nt)), s.mu[:, None], s.mu1[:, None], flatB)
        seg = np.linalg.norm(np.diff(s.Cv, axis=1), axis=-1); cum = np.concatenate([np.zeros((len(PH), 1)), np.cumsum(seg, 1)], 1); s.len = cum[:, -1]; s.cum = cum / cum[:, -1:]
    def at(s, phi, t):
        step = 360.0 / len(s.PH); f = (phi - s.PH[0]) / step; j0 = np.floor(f).astype(int) % len(s.PH); j1 = (j0 + 1) % len(s.PH); w = (f - np.floor(f))[:, None]
        def on(j):
            out = np.zeros((len(t), 3))
            for jj in np.unique(j):
                m = j == jj; tp = np.interp(np.clip(t[m], 0, 1), s.cum[jj], s.ts); out[m] = hermite(s.A[jj][None], s.tA[jj][None], s.B[jj][None], -s.tB[jj][None], tp, s.mu[jj], s.mu1[jj], s.flatB)
                lo = m & (t < 0); hi = m & (t > 1)
                if lo.any(): fn, elA, R = s.ball; out[lo] = fn(np.full(lo.sum(), s.PH[jj]), elA[jj] + np.degrees(-t[lo] * s.len[jj] / R))
                if hi.any(): out[hi] = s.B[jj][None] - s.tB[jj][None] * ((t[hi] - 1) * s.len[jj])[:, None]
            return out
        return on(j0) * (1 - w) + on(j1) * w
    def closest(s, X):
        _, k = cKDTree(s.Cv.reshape(-1, 3)).query(X); j, i = np.divmod(k, len(s.ts)); return s.PH[j], s.cum[j, i]
def bridge_join(P, T, W, names, C, nm, V, F, slhw, onball, tfield, grp, hw, cfg, verbose=True):
    """v10e: the zone between the ball (above a loop on it) and the trunk (behind a plane across it) laid again as the loft. Returns the
    new positions, the zone, each vertex's place on the loft (t: 0 at the ball's loop, 1 at the trunk's plane; phi), a band round the zone
    (smoothed with it), the arms' sideways moves and the numbers for the report"""
    P = P.copy(); n = len(P); used = np.zeros(n, bool); used[T.ravel()] = True
    g = lambda pre: W[:, [i for i, q in enumerate(names) if q.startswith(pre)]].sum(1)
    armw = g(('upperarm', 'forearm', 'hand', 'finger')); legw = g(('thigh', 'shin', 'foot', 'toe')); tailw = g('tail')
    QB = np.array(cfg['QB'], float); nB = unit(np.array(cfg['nB'], float)); fw0 = np.array(cfg['fwd'], float)
    nax = unit(C - QB); fwd = unit(fw0 - nax * (fw0 @ nax)); side = np.cross(nax, fwd)
    def coords(X):
        rel = X - C; a = rel @ nax; rad = rel - np.outer(a, nax)
        return np.degrees(np.arctan2(rad @ side, rad @ fwd)), np.degrees(np.arcsin(np.clip(a / np.maximum(np.linalg.norm(rel, axis=1), 1e-9), -1, 1)))
    phi, el = coords(P); hB = (P - QB) @ nB
    NPH = 180; PH = np.arange(NPH) * 360.0 / NPH - 180.0; pr = np.radians(PH); dperp = np.cos(pr)[:, None] * fwd + np.sin(pr)[:, None] * side; dproj = unit(dperp - np.outer(dperp @ nB, nB))
    blend = lambda ph, f, s_, b: np.where(np.abs(ph) < 90, f + (s_ - f) * ss(np.abs(ph) / 90), s_ + (b - s_) * ss((np.abs(ph) - 90) / 90))
    # ---- B: the trunk's cross-section in the plane and its direction there (toward the head), low-passed round the loop ----
    Ft = T[(armw[T] < 0.5).all(1) & (legw[T] < 0.5).all(1) & (tailw[T] < 0.5).all(1) & ~(onball[T]).all(1)]
    def trunk_at(off):
        o = QB + off * nB; t, _ = cast_from(np.repeat(o[None], NPH, 0), dproj, P, Ft, np.zeros(n)); X = o + dproj * t[:, None]; ok = np.isfinite(t) & (t < 0.9)
        for j in range(3): X[:, j] = np.interp(PH, PH[ok], X[ok, j], period=360)
        return X
    B = trunk_at(0.0); B1 = trunk_at(-0.06); K = cfg.get('harmonics', 8); tB = unit(lowpass(unit(circ_smooth(B - B1, 3)), K)); B = lowpass(circ_smooth(B, 2), K)
    # ---- A: the ball's profile per azimuth (rays from the face centre onto the slime's ball; its ear roots' holes filled in), the loop
    # where the line from B touches it, within the limits ----
    els = np.arange(-85, 40.1, 1.0); dirs = (np.cos(np.radians(els))[None, :, None] * dperp[:, None, :] + np.sin(np.radians(els))[None, :, None] * nax[None, None, :]).reshape(-1, 3)
    tball, hb = cast(C, dirs, V, F, slhw); tb2 = np.where(np.isfinite(tball) & (hb > 0.6), tball, np.nan).reshape(NPH, len(els))
    for j in range(NPH):
        okr = np.isfinite(tb2[j])
        if okr.sum() > 3: inside = els >= els[okr].min(); tb2[j, inside & ~okr] = np.interp(els[inside & ~okr], els[okr], tb2[j, okr])
    elmin = np.array([els[np.isfinite(tb2[j])].min() if np.isfinite(tb2[j]).any() else 0.0 for j in range(NPH)]); elmin = np.maximum(elmin, circ_smooth(elmin, 3))
    for e in range(len(els)):
        okc = np.isfinite(tb2[:, e])
        if okc.sum() > 3 and (~okc).any(): tb2[~okc, e] = np.where(els[e] >= elmin[~okc], np.interp(PH[~okc], PH[okc], tb2[okc, e], period=360), np.nan)
    Xp = C + dirs.reshape(NPH, len(els), 3) * tb2[..., None]
    rho = ((Xp - C) * dperp[:, None, :]).sum(-1); hh = (Xp - C) @ nax; rhoB = ((B - C) * dperp).sum(-1); hBc = (B - C) @ nax
    ang = np.where(np.isfinite(tb2), np.degrees(np.arctan2(rho - rhoB[:, None], hh - hBc[:, None])), -np.inf)
    elA_hull = circ_smooth(els[np.argmax(ang, 1)].astype(float), 6)
    elA = np.maximum(np.maximum(np.minimum(elA_hull, blend(PH, *cfg['elA_max'])), blend(PH, *cfg['elA_min'])), elmin + 4.0); elA = lowpass(circ_smooth(elA, 5), K)
    tbf = np.where(np.isfinite(tb2), tb2, np.nanmax(tb2, 1, keepdims=True))
    def ball_at(e, j=None):
        j = np.arange(NPH) if j is None else j; t = np.array([np.interp(e[i], els, tbf[j[i]]) for i in range(len(e))])
        d = np.cos(np.radians(e))[:, None] * dperp[j] + np.sin(np.radians(e))[:, None] * nax; return C + d * t[:, None]
    Rb = float(np.nanmedian(tb2)); ball_pe = lambda ph, e: ball_at(e, np.round((ph - PH[0]) / (360.0 / NPH)).astype(int) % NPH)
    if verbose: print(f'  bridge: axis {np.round(nax, 3).tolist()}; loop on the ball (deg about it) hull {np.round(elA_hull[::15], 0).tolist()} -> {np.round(elA[::15], 0).tolist()} (phi {PH[::15].astype(int).tolist()}); the trunk at the plane, radius {np.round(rhoB[::15], 3).tolist()}')
    # ---- the zone: between the ball above the loop (on the ball: put onto it outright near the loop) and the trunk behind the plane ----
    elAv = np.interp(phi, PH, elA, period=360); okball = onball & np.isfinite(tfield)
    ballkeep = used & grp & (hB > 0.02) & (el > elAv) & (okball | (el > elAv + 20))
    onb = ballkeep & okball & (el < elAv + 35); P[onb] = C + unit(P[onb] - C) * tfield[onb][:, None]
    limbx = used & (armw > cfg['limb_cut']); trunkkeep = used & (hB < 0) & ~ballkeep & ~limbx; zone = used & ~ballkeep & ~trunkkeep & ~limbx
    Adj, _ = adjacency(n, T); nbr = lambda m: (Adj @ m.astype(float)) > 0
    # (a piece of the zone that never reaches the trunk (a few head vertices round an ear root, off the slime's ball and less than 20
    # degrees above the loop) stays with the head: laid out on its own it had nothing to hold it and went to the loop's origin, the chin)
    from scipy.sparse.csgraph import connected_components
    iz0 = np.where(zone)[0]; ncz, labz = connected_components(Adj[iz0][:, iz0], directed=False); reach = np.zeros(ncz, bool)
    np.logical_or.at(reach, labz, ((Adj @ trunkkeep.astype(float)) > 0)[iz0]); stray = iz0[~reach[labz]]; zone[stray] = False; ballkeep[stray] = True
    bball = ballkeep & nbr(zone); btrunk = trunkkeep & nbr(zone); ring = zone & nbr(limbx)
    # ---- the loft, from the loop on the ball to the trunk's plane ----
    A = ball_at(elA); tA = unit(circ_smooth(unit(ball_at(elA - 3.0) - ball_at(elA + 3.0)), 3)); muAv = blend(PH, *cfg['muA'])
    L = Loft(PH, A, tA, B, tB, muAv, cfg.get('muB', 1.0), ball=(ball_pe, elA, Rb), flatB=cfg.get('flatB', True))
    Lv = np.interp(phi, PH, L.len, period=360); t0 = np.zeros(n); t0[bball] = -Rb * np.radians(np.maximum(el - elAv, 0))[bball] / Lv[bball]; t0[btrunk] = (1 + np.maximum(-hB, 0) / Lv)[btrunk]
    sub = zone | bball | btrunk; idx = np.where(sub)[0]
    tz = np.zeros(n); tz[idx] = solve_fixed(Adj[idx][:, idx], (bball | btrunk)[idx], t0[idx, None])[:, 0]   # (t alone first: the cut follows it)
    # ---- the zone cut open along the back, from the ball's edge to the trunk's, and laid out flat in (phi, t) ----
    from scipy.sparse.csgraph import dijkstra
    Ez = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); Ez = Ez[sub[Ez].all(1)]; phm, _ = coords(0.5 * (P[Ez[:, 0]] + P[Ez[:, 1]]))
    wE = np.linalg.norm(P[Ez[:, 0]] - P[Ez[:, 1]], axis=1) * (1 + 0.5 * (180 - np.abs(phm)))
    G = coo_matrix((np.r_[wE, wE], (np.r_[Ez[:, 0], Ez[:, 1]], np.r_[Ez[:, 1], Ez[:, 0]])), shape=(n, n)).tocsr()
    cb = np.where(bball)[0]; cb = cb[np.argmax(np.abs(phi[cb]))]; ct = np.where(btrunk)[0]; ct = ct[np.argmax(np.abs(phi[ct]))]
    _, pred = dijkstra(G, indices=cb, return_predecessors=True); path = [ct]
    while path[-1] != cb and pred[path[-1]] >= 0: path.append(pred[path[-1]])
    path = np.array(path[::-1]); onpath = np.zeros(n, bool); onpath[path] = True; cp_of = -np.ones(n, int); cp_of[path] = n + np.arange(len(path)); N2 = n + len(path)
    p360 = lambda x: np.mod(x, 360.0); tp = tz[path]; o_ = np.argsort(tp); cutf = lambda tt: np.interp(tt, tp[o_], p360(phi[path])[o_])
    Tz = T[sub[T].all(1)].copy(); phc, _ = coords(P[Tz].mean(1)); left = p360(phc) > cutf(tz[Tz].mean(1))
    for c in range(3): m = onpath[Tz[:, c]] & left; Tz[m, c] = cp_of[Tz[m, c]]
    rings = []
    for sd in 'LR':
        armS = W[:, [i for i, q_ in enumerate(names) if q_.startswith(('upperarm', 'forearm', 'hand', 'finger')) and f'.{sd}' in q_]].sum(1); rs = np.where(ring & (armS > 0.05))[0]
        if len(rs): rings.append(rs)
    NV = N2 + len(rings); E2 = np.concatenate([Tz[:, [0, 1]], Tz[:, [1, 2]], Tz[:, [2, 0]]])
    for k_, rs in enumerate(rings): E2 = np.concatenate([E2, np.stack([np.full(len(rs), N2 + k_), rs], 1)])   # (each limb's hole fanned to a centre)
    E2 = np.unique(np.sort(E2, 1), axis=0); A2 = coo_matrix((np.ones(2 * len(E2)), (np.r_[E2[:, 0], E2[:, 1]], np.r_[E2[:, 1], E2[:, 0]])), shape=(NV, NV)).tocsr()
    X0 = np.zeros((NV, 2)); fx = np.zeros(NV, bool); bnd = bball | btrunk; fx[:n] = bnd; X0[:n, 1] = t0
    X0[:n, 0] = np.where(np.abs(phi) > 90, np.where(p360(phi) > cutf(t0), p360(phi) - 360, p360(phi)), phi)   # (the back's azimuths unwrapped to their side of the cut)
    X0[path, 0] = p360(phi[path]); X0[path, 1] = np.where(bnd[path], t0[path], tz[path]); fx[path] = True; X0[cp_of[path]] = X0[path] - [360.0, 0.0]; fx[cp_of[path]] = True
    inv = np.zeros(NV, bool); inv[:n] = sub; inv[n:] = True; ii = np.where(inv)[0]; A3 = A2[ii][:, ii]
    Xs = np.zeros((NV, 2)); Xs[ii] = solve_fixed(A3, fx[ii], X0[ii])
    # (each limb's hole drifts with the zone's own spacing: moved back to where its limb meets the loft by a harmonic offset, fading to
    # nothing at the ball, the trunk and the cut)
    for k_, rs in enumerate(rings):
        phr, tr = L.closest(P[rs]); dlt = np.array([((phr - Xs[rs, 0] + 180) % 360 - 180).mean(), (tr - Xs[rs, 1]).mean()])
        fk = fx.copy(); fk[rs] = True; fk[N2 + k_] = True; w0 = np.zeros((NV, 1)); w0[rs] = 1; w0[N2 + k_] = 1; Xs[ii] += solve_fixed(A3, fk[ii], w0[ii]) * dlt[None, :]
    # (any triangle still folded in (phi, t): its free corners and their neighbours relaxed toward their neighbours' mean)
    Tin = Tz[np.isin(Tz, ii).all(1)]; deg2 = np.asarray(A2.sum(1)).ravel(); freev = np.zeros(NV, bool); freev[ii] = ~fx[ii]
    def area(X): p_ = X[Tin]; return (p_[:, 1, 0] - p_[:, 0, 0]) * (p_[:, 2, 1] - p_[:, 0, 1]) - (p_[:, 2, 0] - p_[:, 0, 0]) * (p_[:, 1, 1] - p_[:, 0, 1])
    sg0 = np.sign(np.median(area(Xs))); nfl0 = int((np.sign(area(Xs)) != sg0).sum())
    for it in range(200):
        bad = np.sign(area(Xs)) != sg0
        if not bad.any(): break
        mv = np.zeros(NV, bool); mv[Tin[bad].ravel()] = True
        for _ in range(2): mv = mv | ((A2 @ mv.astype(float)) > 0)
        mv &= freev; avg = (A2 @ Xs) / np.maximum(deg2, 1)[:, None]; Xs[mv] = 0.5 * Xs[mv] + 0.5 * avg[mv]
    nfl1 = int((np.sign(area(Xs)) != sg0).sum()); phz = (Xs[:n, 0] + 180) % 360 - 180; tz = Xs[:n, 1].copy()
    iz = np.where(zone)[0]; newp = L.at(phz[iz], tz[iz]); disp = np.zeros((n, 3)); disp[iz] = newp - P[iz]; P[iz] = newp
    # ---- the arms: the shoulder joint set its rest inset inside the loft, straight out to the side; the arm's own vertices take the zone's
    # displacement from their ring, eased into that plain move down the upper arm (a harmonic field held at the ring and the forearm on) ----
    moved = {}
    for sd in 'LR':
        J = cfg['joints'][f'upperarm.{sd}']; phj, tj = L.closest(J[None]); Q = L.at(phj, tj)[0]; nr = unit(np.cross(L.at(phj, tj + 0.02)[0] - Q, L.at(phj + 2.0, tj)[0] - Q))
        if nr @ (Q - J) < 0: nr = -nr
        moved[sd] = float((Q - cfg.get('arm_inset', 0.03) * nr)[0] - J[0])
    dxs = 0.5 * (moved['L'] - moved['R']); moved = {'L': round(dxs, 4), 'R': round(-dxs, 4)}   # (the two arms the same, mirrored: the rig stays symmetric)
    for sd in 'LR':
        armS = W[:, [i for i, q_ in enumerate(names) if q_.startswith(('upperarm', 'forearm', 'hand', 'finger')) and f'.{sd}' in q_]].sum(1); dx = moved[sd]
        lm = limbx & (armS > cfg['limb_cut'] * 0.5); dist_ = W[:, [i for i, q_ in enumerate(names) if q_.startswith(('forearm', 'hand', 'finger')) and f'.{sd}' in q_]].sum(1) > 0.3
        rim = nbr(lm) & ~lm & used; dom = lm | rim; fixd = rim | (lm & dist_); d0 = np.zeros((n, 3)); d0[zone] = disp[zone]; d0[lm & dist_] = [dx, 0.0, 0.0]   # (held at every neighbour: the zone's by its own move, the rest still)
        id_ = np.where(dom)[0]; dsol = solve_fixed(Adj[id_][:, id_], fixd[id_], d0[id_]); P[id_[~fixd[id_]]] += dsol[~fixd[id_]]
        P[lm & dist_] += [dx, 0.0, 0.0]                                           # (the forearm on: the plain move)
    # ---- the trunk just behind the plane eased onto the loft's own continuation (the low-passed loop meets the trunk with no step), then
    # the zone and a band round it smoothed (Taubin: no shrinking), the ball beyond the band and the trunk held ----
    bandB = trunkkeep & (hB > -0.08) & ~limbx; ib = np.where(bandB)[0]
    if len(ib): tb_ = 1 + (-hB[ib]) / np.interp(phi[ib], PH, L.len, period=360); wb = 1 - ss(-hB[ib] / 0.08); P[ib] += wb[:, None] * (L.at(phi[ib], tb_) - P[ib])
    band = zone | bandB
    for _ in range(cfg.get('band_rings', 5)): band = band | (nbr(band) & used & ~limbx)
    armb = ring.copy()                                                            # (and the arms' roots: two rings onto the arm, so it meets the loft in a fillet)
    for _ in range(cfg.get('arm_rings', 2)): armb = armb | (nbr(armb) & used)
    band = band | armb
    deg = np.asarray(Adj.sum(1)).ravel()
    for _ in range(cfg.get('taubin', 30)):
        for lam in (0.5, -0.53): avg = (Adj @ P) / np.maximum(deg, 1)[:, None]; P[band] += lam * (avg[band] - P[band])
    # (a triangle in the band still turned over against the triangles round it (the arms' roots' creases): its corners eased toward
    # their neighbours' mean until none is)
    Tb_ = T[band[T].any(1)]; nflip0 = None
    for it in range(40):
        fn_ = np.cross(P[Tb_[:, 1]] - P[Tb_[:, 0]], P[Tb_[:, 2]] - P[Tb_[:, 0]]); vs_ = np.zeros((n, 3))
        for c_ in range(3): np.add.at(vs_, Tb_[:, c_], fn_)
        ring_ = vs_[Tb_].sum(1) - 3 * fn_; bad_ = (fn_ * ring_).sum(1) < 0
        if nflip0 is None: nflip0 = int(bad_.sum())
        if not bad_.any(): break
        mv_ = np.zeros(n, bool); mv_[Tb_[bad_].ravel()] = True; mv_ &= band; avg = (Adj @ P) / np.maximum(deg, 1)[:, None]; P[mv_] = 0.5 * P[mv_] + 0.5 * avg[mv_]
    if verbose: print(f'  bridge band: {nflip0} triangles turned over after the smoothing, {int(bad_.sum())} after easing their corners ({it} rounds)')
    # (t carried out over the band: the distance over the surface from the zone, a third of a metre to one unit of t, down on the ball's side
    # and up on the trunk's: the texture's blend and the masks fade out over it)
    from scipy.sparse.csgraph import dijkstra as _dj
    Eb = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); Eb = Eb[(band | zone)[Eb].all(1)]; wb_ = np.linalg.norm(P[Eb[:, 0]] - P[Eb[:, 1]], axis=1) + 1e-6
    Gb = coo_matrix((np.r_[wb_, wb_], (np.r_[Eb[:, 0], Eb[:, 1]], np.r_[Eb[:, 1], Eb[:, 0]])), shape=(n, n)).tocsr(); dz = _dj(Gb, indices=np.where(zone)[0], min_only=True)
    tt = np.where(zone, tz, np.where(ballkeep, -1.0, 2.0)); bb = band & ~zone & np.isfinite(dz)
    tt[bb & ballkeep] = np.maximum(-1.0, np.minimum(tz[bb & ballkeep], 0) - dz[bb & ballkeep] / 0.3); tt[bb & ~ballkeep] = np.minimum(2.0, 1.0 + dz[bb & ~ballkeep] / 0.3)
    if verbose: print(f'  bridge zone {int(zone.sum())} verts (ball edge {int(bball.sum())}, trunk edge {int(btrunk.sum())}, arm rings {int(ring.sum())}; {len(stray)} stray head verts left on the head); cut {len(path)}; folds {nfl0} -> {nfl1}; arms out {moved}; band {int(band.sum())}')
    return P, zone, tt, band, moved, dict(nax=nax.round(4).tolist(), QB=QB.tolist(), elA=np.round(elA[::15], 1).tolist(), rhoB=np.round(rhoB[::15], 3).tolist(), arms=moved, zone=int(zone.sum()), folds=nfl1)
def bridge_weights(si, sw, W, names, bi, zone, tt, P, T):
    """the skin weights across the bridge by its t (0 at the ball's loop, 1 at the trunk's plane): the head's at the ball, the trunk edge's
    own (its nearest vertex behind the plane) at the plane, a share on the neck between, so a turn of the head spreads over the whole
    bridge; whatever the vertex had on the arms is kept as it was"""
    n = len(P); A, _ = adjacency(n, T); edge = (tt >= 1.0) & ~zone & ((A @ zone.astype(float)) > 0); ie = np.where(edge)[0]; kd = cKDTree(P[ie])
    armset = np.array([q.startswith(('upperarm', 'forearm', 'hand', 'finger', 'shoulder')) for q in names]); si = si.copy(); sw = sw.copy()
    # (the head above the loop turns with the head alone: whatever share it had on the neck or the trunk goes to the head, so the bridge
    # below it is the only place a turn of the head bends; its face (headfront) and the old stalks' shares stay as they are)
    keepset = np.array([q in ('head', 'headfront') or q.startswith('gill') for q in names]); hb = bi['head']; nmoved = 0
    for v in np.where((tt < 0) & ~zone)[0]:
        s_, w_ = si[v].astype(int), sw[v].astype(int); m_ = (w_ > 0) & ~keepset[s_]
        if not m_.any(): continue
        acc = {}
        for b_, ww in zip(np.where(m_, hb, s_), w_):
            if ww > 0: acc[int(b_)] = acc.get(int(b_), 0) + int(ww)
        items = sorted(acc.items(), key=lambda kv: -kv[1])[:4]; si[v] = 0; sw[v] = 0
        for j_, (b_, ww) in enumerate(items): si[v, j_] = b_; sw[v, j_] = ww
        sw[v, 0] += 255 - int(sw[v].sum()); nmoved += 1
    for v in np.where(zone)[0]:
        a = float(ss(np.clip(tt[v], 0, 1))); acc = {}
        for b_, w_ in zip(si[v], sw[v]):
            if w_ > 0 and armset[b_]: acc[int(b_)] = acc.get(int(b_), 0) + w_ / 255.0
        rest = max(0.0, 1.0 - sum(acc.values())); _, j = kd.query(P[v]); e = ie[j]; te = {}
        for b_, w_ in zip(si[e], sw[e]):
            if w_ > 0 and not armset[b_]: te[int(b_)] = te.get(int(b_), 0) + w_ / 255.0
        tsum = sum(te.values()) or 1.0
        for b_, w_ in ((bi['head'], (1 - a) ** 2), (bi['neck'], 2 * a * (1 - a))): acc[b_] = acc.get(b_, 0) + rest * w_
        for b_, w_ in te.items(): acc[b_] = acc.get(b_, 0) + rest * a * a * w_ / tsum
        items = sorted(acc.items(), key=lambda kv: -kv[1])[:4]; tot = sum(w for _, w in items) or 1.0
        q = [int(round(255 * w / tot)) for _, w in items]; q[0] += 255 - sum(q); si[v] = 0; sw[v] = 0
        for j_, ((b_, _), w_) in enumerate(zip(items, q)): si[v, j_] = b_; sw[v, j_] = w_
    print(f'  bridge weights: {int(zone.sum())} zone verts by t; {nmoved} head verts above the loop given to the head alone')
    return si, sw
def ear_piece(sl, sgn, C, s):
    """one of the slime's ears (+x side: sgn 1), scaled and placed about the axolotl's face centre C and bent into its resting hang:
    P, T (local indices), ew, the hinge, and the chain's joints (the hinge, the middle of the ear, its tip)"""
    P, T, ew, hw = sl['P'], sl['T'], sl['ew'], sl['hw']
    side = (P[:, 0] * sgn > 0); et = ((ew[T] > 0.001).any(1)) & side[T].all(1); vid = np.unique(T[et]); loc = -np.ones(len(P), np.int64); loc[vid] = np.arange(len(vid))
    Pe = (P[vid] - SLIME_HEAD) * s + C; Te = loc[T[et]]; ewe = ew[vid]; hinge = (np.array([sgn, 1, 1]) * SLIME_EAR - SLIME_HEAD) * s + C
    # the rest hang (the slime's shader: v = rotA(v, z, sd * f * ew); v = rotA(v, x, -sw * ew) about the hinge)
    v = Pe - hinge; v = rot_axis(v, [0, 0, 1], sgn * EAR_REST[0] * ewe); v = rot_axis(v, [1, 0, 0], -EAR_REST[1] * ewe); Pe = hinge + v
    mid = Pe[(ewe > 0.42) & (ewe < 0.58)].mean(0); tip = Pe[ewe > 0.95].mean(0)
    return dict(P=Pe, T=Te, ew=ewe, hinge=hinge, mid=mid, tip=tip, sgn=sgn, length=float(np.linalg.norm(mid - hinge) + np.linalg.norm(tip - mid)))
def pack(parts_):
    off = {}; o = 0; blobs = []
    for k_, arr in parts_:
        bb = np.ascontiguousarray(arr).tobytes(); off[k_] = o; blobs.append((o, bb)); o += len(bb); o += (-o) % 4
    buf = bytearray(o)
    for of, bb in blobs: buf[of:of + len(bb)] = bb
    return buf, off
def reshape(nm, untex, tex, out, outsrc, s=SCALE, verbose=True):
    r = tb.load_rt(nm, d=untex); n_all = r['n']; names = r['names']; bi = {k: i for i, k in enumerate(names)}; meta = dict(r['meta']); C = np.array(meta['face']['c'], float); cps = meta['cpScale']
    gidx = [i for i, k in enumerate(names) if k.startswith('gill')]
    # ---- the v9b lobes off (the last N_LOBE vertices and every triangle on them); the retired stalks' own vertices off outright ----
    n = n_all - N_LOBE; assert (r['si'][n:, 0] == bi['head']).all() and (r['si'][:n, 0] != bi['head']).any(); P = r['P'][:n].astype(float); T = r['T'][(r['T'] < n).all(1)]
    W = r['W'][:n]; hw = W[:, bi['head']] + W[:, bi['headfront']]; gw = W[:, gidx].sum(1)
    jelly = r['jelly'][:n].copy(); fill = r['fill'][:n].copy(); mat = r['mat'][:n].copy(); si = r['si'][:n].copy(); sw = r['sw'][:n].copy(); cp = r['cp'][:n].copy()
    # (the retired stalks: v9b collapsed each stalk's vertices onto one point, so they are the vertices stacked three or more deep on a
    # point; the ring round each is whatever still touches them)
    # (stacked within 1.5 mm, not bit-identical: v9b's smoothing nudged a few of them apart, and those few, with their mixed stalk and
    # head weights, opened into a long sliver textured across the atlas whenever the ear bones moved: the lobby's pale spike)
    kd0 = cKDTree(P); stack = np.array([len(kd0.query_ball_point(p, 0.0015)) for p in P]); own = (stack >= 3) & ((hw + gw) > 0.02)
    T = T[~own[T].any(1)]; A0, _ = adjacency(n, r['T'][(r['T'] < n).all(1)]); ring = ((A0 @ own.astype(float)) > 0) & ~own
    def open_near(TT, PP):
        E = np.concatenate([TT[:, [0, 1]], TT[:, [1, 2]], TT[:, [2, 0]]]); u_, c_ = np.unique(np.sort(E, 1), axis=0, return_counts=True); op = u_[c_ == 1]
        return int((np.linalg.norm(PP[op].mean(1) - C, axis=1) < 0.5).sum()) if len(op) else 0
    if verbose: print(f'{nm}: {n_all} verts -> lobes off {n}, retired stalk verts {int(own.sum())} dropped; {len(T)} tris, {int(ring.sum())} ring verts; open edges near the head before {open_near(r["T"][(r["T"] < n).all(1)], P)}, after the drop {open_near(T, P)}')
    # (v10d: the lizard body, on the positions the stacked vertices were found on; the textured copy maps by the original positions)
    P_orig = P.copy(); LZ = None
    if LIZARD:
        P, meta['bones'], C, LZ = lizard_body(P, W, meta, names, bi, hw, nm, verbose); meta['face'] = {'c': C.round(4).tolist(), 'r': meta['face']['r']}
        meta['headc'] = (C - np.array([b for b in meta['bones'] if b['name'] == 'head'][0]['pos'])).round(4).tolist()
    # ---- the skull onto the slime's head: each head vertex cast from C along its own direction onto the slime's head surface ----
    sl = load_slime(); body = (sl['ew'] < 0.001) & (sl['stub'] < 0.01); F = sl['T'][body[sl['T']].all(1)]; V = (sl['P'] - SLIME_HEAD) * s + C
    q = P - C; dist = np.linalg.norm(q, axis=1); d = q / np.maximum(dist, 1e-9)[:, None]; grp = (hw > 0.02) & ~own
    tcast, hwhit = cast(C, d[grp], V, F, sl['hw']); tfield = np.full(n, np.inf); hfield = np.zeros(n); tfield[grp] = tcast; hfield[grp] = hwhit
    onball = np.isfinite(tfield) & (hfield > 0.6)        # (the slime's head ball itself, not its body under it)
    k = ss((hw - 0.25) / 0.7) * ss((hfield - 0.6) / 0.35) * onball
    newr = np.where(onball, tfield, dist); P2 = C + d * (dist + k * (newr - dist))[:, None]
    # the neck never thinner than it was (the slime's trunk is narrower than the axolotl's neck: the ball's underside flows into the
    # axolotl's own thick neck instead of pinching in to the slime's): on the neck side of the head group (down and back, not the
    # cheeks) each vertex keeps at least its old distance from the neck axis, a touch more below the chin; applied again after the smoothing
    hbj = np.array([b for b in meta['bones'] if b['name'] == 'head'][0]['pos']); nkb = np.array([b for b in meta['bones'] if b['name'] == 'neck'][0]['pos']); nax = unit(hbj - nkb)
    def axial(PP): rel = PP - hbj; al = rel @ nax; rad = rel - np.outer(al, nax); return al, rad
    al0, rad0 = axial(P); r0 = np.linalg.norm(rad0, axis=1); downish = grp & (al0 < -0.12) & ((d @ nax) < -0.5)
    floor = r0 * np.where(al0 < -0.22, 1.04, 1.0)
    def neck_floor(PP):
        al1, rad1 = axial(PP); r1 = np.linalg.norm(rad1, axis=1); low = downish & (r1 < floor) & (r1 > 1e-4)
        PP[low] += (rad1[low] / r1[low, None]) * (floor[low] - r1[low])[:, None]; return low
    low = neck_floor(P2) if not LIZARD else np.zeros(n, bool)
    # the join smoothed: a few Laplacian steps over the blend's edge and the old rings (positions only; the ball's own surface untouched)
    A, deg = adjacency(n, T); edge = grp & (k > 0.02) & (k < 0.98); band = edge | ring | low
    for _ in range(3): band = band | ((A @ band.astype(float)) > 0) & grp & (k < 0.999)
    sm = band & ~own
    for _ in range(8):
        y_ = (A @ P2) / np.maximum(deg, 1)[:, None]; P2[sm] = 0.5 * P2[sm] + 0.5 * y_[sm]
    if not LIZARD: neck_floor(P2)
    # ---- the junction (v10b, the user: "the neck area is off"): the ball's underside had closed to a ledge over a neck column half its
    # width, a crease ring under the chin and behind. Now a target radius about the neck axis per height and direction (front, side,
    # back, blended by azimuth): the ball's own radius down to its lower third, then a concave fillet into a neck nearly that wide, which
    # eases out into the chest and the shoulders. Applied as a floor (the ball above and the flat chin keep their own surface; only
    # what lies inside the target comes out to it), then smoothed for a continuous surface, the floor applied once more ----
    # (and the chest and upper trunk a little fuller below it, the user: "make the chest a little larger to flow better into the neck":
    # wider across the shoulders and deeper at the top of the trunk, easing to nothing by the hips; the arms, hips and tail untouched)
    if LIZARD:
        # (v10e: the bridge instead of the fillet; the arms' bones go out with their roots; the skin weights across the bridge by its t:
        # the head's at the ball, the trunk edge's own at the plane, a share on the neck between; the arms' own weights kept)
        cfgb = dict(BRIDGE_CFG[nm]); cfgb['joints'] = {f'upperarm.{sd}': np.array([b for b in meta['bones'] if b['name'] == f'upperarm.{sd}'][0]['pos'], float) for sd in 'LR'}
        P2, zone, tbr, bandz, armdx, BR = bridge_join(P2, T, W, names, C, nm, V, F, sl['hw'], onball, tfield, grp, hw, cfgb, verbose)
        for b in meta['bones']:
            for sd in 'LR':
                if (b['name'].startswith(('upperarm', 'forearm', 'hand', 'finger')) and f'.{sd}' in b['name']): b['pos'] = [b['pos'][0] + armdx[sd]] + list(b['pos'][1:]); b['end'] = [b['end'][0] + armdx[sd]] + list(b['end'][1:])
                if b['name'] == f'shoulder.{sd}': b['end'] = [b['end'][0] + armdx[sd]] + list(b['end'][1:])
        si, sw = bridge_weights(si, sw, W, names, bi, zone, tbr, P2, T)
        if LZ is not None: LZ['bridge'] = BR
        jz = np.clip(np.where(zone, 1.0, 0.0), 0, 1)
        Az_, dz_ = adjacency(n, T)
        for _ in range(4): jz = np.maximum(jz, 0.6 * (Az_ @ jz) / np.maximum(dz_, 1))
        fill[:, 2] = np.clip(np.round(fill[:, 2] * (1 - jz)), 0, 255).astype(np.uint8); mat[:, 2] = np.clip(np.round(mat[:, 2] * (1 - jz)), 0, 255).astype(np.uint8)
        # (the bridge's rigidity (jelly.w: the head rigid, the body soft) and its body channel (jelly.y: 0 on the head, 1 on the body) by t,
        # smooth from the head's to the trunk's; as the old neck's own they came in uneven: the face skin's mask (which needs jelly.w) ended
        # in a hard arc under the chin, and the soft body's squash had soft and rigid vertices side by side across the throat)
        tz_ = np.clip(tbr, 0, 1); jelly[zone, 3] = np.round(255 * (1 - ss(tz_[zone] / 0.6))).astype(np.uint8); jelly[zone, 1] = np.round(255 * ss((tz_[zone] - 0.15) / 0.45)).astype(np.uint8)
    else:
        fwdv = unit(np.array([0.0, 0.0, 1.0]) - nax * nax[2]); sidev = np.cross(nax, fwdv); nw = W[:, bi['neck']]; cw = W[:, bi['chest']]; s1w = W[:, bi['spine1']]
        armw = W[:, [i for i, k in enumerate(names) if k.startswith(('upperarm', 'shoulder', 'forearm', 'hand', 'finger'))]].sum(1)
        # (v10c: the profiles run on up to al 0.20, where they lie just inside the ball's own surface, so the fillet's lift fades out
        # tangentially into the ball; the back no longer steps in 5 cm between al 0.08 and 0.04, which read as a ring round the nape)
        AL = np.array([-0.56, -0.52, -0.48, -0.44, -0.40, -0.36, -0.32, -0.28, -0.24, -0.20, -0.16, -0.12, -0.08, -0.04, 0.00, 0.04, 0.08, 0.12, 0.16, 0.20])
        PROF = {'stand': {'front': [0.218, 0.232, 0.232, 0.224, 0.215, 0.205, 0.196, 0.190, 0.190, 0.192, 0.200, 0.215, 0.242, 0.258, 0.279, 0.321, 0.353, 0.366, 0.384, 0.395],
                          'side':  [0.250, 0.238, 0.228, 0.218, 0.215, 0.218, 0.225, 0.232, 0.238, 0.244, 0.250, 0.256, 0.262, 0.270, 0.282, 0.300, 0.328, 0.348, 0.372, 0.378],
                          'back':  [0.440, 0.441, 0.446, 0.424, 0.352, 0.295, 0.256, 0.215, 0.190, 0.180, 0.182, 0.189, 0.200, 0.214, 0.230, 0.248, 0.266, 0.277, 0.284, 0.292]},
                'crawl': {'front': [0.040, 0.062, 0.085, 0.110, 0.138, 0.150, 0.165, 0.175, 0.183, 0.190, 0.198, 0.215, 0.250, 0.290, 0.328, 0.344, 0.357, 0.357, 0.356, 0.343],
                          'side':  [0.100, 0.118, 0.165, 0.178, 0.185, 0.195, 0.205, 0.215, 0.222, 0.228, 0.234, 0.240, 0.248, 0.258, 0.268, 0.309, 0.334, 0.334, 0.350, 0.375],
                          'back':  [0.496, 0.454, 0.410, 0.373, 0.333, 0.299, 0.265, 0.234, 0.217, 0.192, 0.182, 0.188, 0.199, 0.212, 0.226, 0.240, 0.254, 0.266, 0.277, 0.286]}}[nm]
        def frame(PP):
            rel = PP - hbj; al = rel @ nax; rad = rel - np.outer(al, nax); rr = np.linalg.norm(rad, axis=1); phi = np.degrees(np.abs(np.arctan2(rad @ sidev, rad @ fwdv)))
            return al, rad, rr, phi
        blend = lambda phi, a, b_, c_: np.where(phi < 90, a + (b_ - a) * ss(phi / 90), b_ + (c_ - b_) * ss((phi - 90) / 90))
        if not LIZARD:
            def junction(PP):
                al, rad, rr, phi = frame(PP); rf, rs, rb = (np.interp(al, AL, PROF[k]) for k in ('front', 'side', 'back'))
                return al, rad, rr, blend(phi, rf, rs, rb)
            al_, rad_, rr_, rt_ = junction(P2)
            zone = ((hw + nw + cw + s1w) > 0.02) & ~own & (al_ > -0.54) & (al_ < 0.18) & (gw < 0.02) & (armw < 0.3)
        else:
            # the union of the ball and the trunk (v10d): for a vertex at height al in direction phi, the ball's radius there (a ray out from
            # the axis onto the slime head) against a dome: from the trunk's own envelope a quarter metre below the join (its radius and slope,
            # measured per 30-degree sector) a cubic up to the ball at the join, with the ball's own slope there, so the trunk runs into the
            # ball with no fold; the join sits under the chin at the front, high on the cheeks at the sides, at the nape behind
            alc = float((C - hbj) @ nax); rball_ = SLIME_R * s
            al_, rad_, rr_, phi_ = frame(P2); dj_ = blend(phi_, *DJ); alj_ = alc - dj_; allow_ = alj_ - 0.25
            zone = ((hw + nw + cw + s1w) > 0.02) & ~own & (al_ > allow_ - 0.06) & (al_ < alc + 0.12) & (gw < 0.02) & (armw < 0.3)
            envm = (gw < 0.02) & (armw < 0.3) & (hw < 0.3) & ~own; sec_ = np.clip((phi_ // 30).astype(int), 0, 5); PH = np.arange(6) * 30 + 15; Rlow = np.zeros(6); Slow = np.zeros(6)
            for q in range(6):
                a_low = alc - float(blend(np.array([PH[q]]), *DJ)[0]) - 0.25
                def env(a):
                    m = envm & (sec_ == q) & (np.abs(al_ - a) < 0.03); return float(np.percentile(rr_[m], 95)) if m.sum() > 5 else np.nan
                r1, r2 = env(a_low - 0.04), env(a_low + 0.04); Rlow[q] = np.nanmean([r1, r2]); Slow[q] = float(np.clip((r2 - r1) / 0.08, -0.3, 0.6)) if np.isfinite(r1 + r2) else 0.0
            Rlow = np.where(np.isfinite(Rlow), Rlow, np.nanmean(Rlow))
            def junction(PP):
                al, rad, rr, phi = frame(PP); ru = rad / np.maximum(rr, 1e-9)[:, None]; aj = alc - blend(phi, *DJ); alo = aj - 0.25
                idx = np.where(zone)[0]; rt = np.zeros(len(PP))
                tb, hb = cast_from(hbj + np.outer(al[idx], nax), ru[idx], V, F, sl['hw']); rb_ = np.where(np.isfinite(tb) & (hb > 0.6) & (tb < 0.6), tb, 0.0)
                tj, hj = cast_from(hbj + np.outer(aj[idx], nax), ru[idx], V, F, sl['hw']); Rj = np.where(np.isfinite(tj) & (hj > 0.6) & (tj < 0.6), tj, 0.0)
                Sj = (alc - aj[idx]) / np.sqrt(np.maximum(rball_ ** 2 - (alc - aj[idx]) ** 2, 1e-4))
                Rl = np.interp(phi[idx], PH, Rlow); Sl = np.interp(phi[idx], PH, Slow); h = aj[idx] - alo[idx]; t = np.clip((al[idx] - alo[idx]) / h, 0, 1)
                dome = (2 * t ** 3 - 3 * t ** 2 + 1) * Rl + (t ** 3 - 2 * t ** 2 + t) * h * Sl + (-2 * t ** 3 + 3 * t ** 2) * Rj + (t ** 3 - t ** 2) * h * Sj
                dome = np.where((al[idx] >= alo[idx]) & (al[idx] <= aj[idx]), np.clip(dome, 0, 0.6), 0.0); rt[idx] = np.maximum(rb_, dome)
                return al, rad, rr, rt
            al_, rad_, rr_, rt_ = junction(P2)
            if verbose:
                lift0 = zone & (rr_ < rt_); dl = (rt_ - rr_)[lift0]; j_ = np.argmax(dl) if len(dl) else 0; vi = np.where(lift0)[0][j_] if len(dl) else 0
                print(f'  lizard join: ball centre at al {alc:.3f}; the join below it by {DJ} (front/side/back); trunk envelope a quarter below the join per sector {np.round(Rlow, 3).tolist()} slopes {np.round(Slow, 2).tolist()}; largest lift {dl.max() if len(dl) else 0:.3f} at al {al_[vi]:.2f} phi {phi_[vi]:.0f} rr {rr_[vi]:.3f} -> {rt_[vi]:.3f}')
        def fillet(PP, k=1.0):
            al, rad, rr, rt = junction(PP); lift = zone & (rr < rt * k) & (rr > 1e-4); PP[lift] += (rad[lift] / rr[lift, None]) * (rt[lift] * k - rr[lift])[:, None]; return lift
        lifted = fillet(P2)
        if LIZARD: chin = zone & (al_ > alj_ - 0.03) & ((rad_ @ fwdv) > 0.6 * rr_); smz = zone & ~chin & (armw < 0.05)
        else: chin = zone & (al_ > -0.07) & ((rad_ @ fwdv) > 0.6 * rr_); smz = zone & ~chin & ((al_ < 0.06) | ((rad_ @ fwdv) < 0) & (al_ < 0.10)) & (armw < 0.05)   # (the flat chin front keeps its surface)
        for _ in range(8):
            y_ = (A @ P2) / np.maximum(deg, 1)[:, None]; P2[smz] = 0.5 * P2[smz] + 0.5 * y_[smz]
        fillet(P2, 0.985)
        # no baked shadow and no wrinkle rings round the join: its shading is the surface's own
        jz = (ss((alj_ + 0.08 - al_) / 0.1) * ss((al_ - allow_ + 0.1) / 0.1) if LIZARD else ss((0.06 - al_) / 0.1) * ss((al_ + 0.36) / 0.1)) * zone; fill[:, 2] = np.clip(np.round(fill[:, 2] * (1 - jz)), 0, 255).astype(np.uint8); mat[:, 2] = np.clip(np.round(mat[:, 2] * (1 - jz)), 0, 255).astype(np.uint8)
        if verbose:
            alf, radf, rrf, rtf = junction(P2)
            print(f'  junction: {int(zone.sum())} verts in the zone, {int(lifted.sum())} brought out to the fillet (mean {np.linalg.norm((P2 - P)[lifted], axis=1).mean() * 100:.1f} cm); side radius now at al 0 / -0.08 / -0.2: ' + ' / '.join(f'{np.median(rrf[zone & (np.abs(alf - a) < 0.02) & (np.abs(radf @ sidev) > 0.9 * rrf)]):.3f}' for a in (0.0, -0.08, -0.2)))
    # ---- the limbs a touch fuller to go with the chest (v10b): the upper arms and thighs grow about their bone's axis over the middle
    # of the bone, easing to nothing at both joints, by the vertex's own weight on that bone, so the joints, the hands and feet and every
    # contact stay where they are (the crawl a little less than the stand) ----
    FULL = {'upperarm': 0.10 if nm == 'stand' else 0.06, 'thigh': 0.08 if nm == 'stand' else 0.06}; grown = 0
    for part, frac in FULL.items():
        for s_ in 'LR':
            bn = [b for b in meta['bones'] if b['name'] == f'{part}.{s_}'][0]; j0 = np.array(bn['pos']); ax = unit(np.array(bn['end']) - j0); L = float(np.linalg.norm(np.array(bn['end']) - j0))
            wb = W[:, bi[f'{part}.{s_}']]; m = (wb > 0.05) & ~own; rel = P2[m] - j0; al = rel @ ax; rad = rel - np.outer(al, ax); rr = np.linalg.norm(rad, axis=1)
            taper = ss(al / (0.3 * L)) * (1 - ss((al - 0.7 * L) / (0.3 * L))); P2[m] += rad * (frac * taper * wb[m] / np.maximum(rr, 1e-6) * rr)[:, None]; grown += int(m.sum())
    if verbose: print(f'  limbs: {grown} upper arm and thigh verts grown ({FULL})')
    core = (hw > 0.95) & ~own; qq = P2[core] - C
    if verbose:
        print(f'  slime ball hits {int(onball.sum())} of {int(grp.sum())} head-group verts; blended {int((k > 0.5).sum())}; neck floor on {int(low.sum())}; smoothed {int(sm.sum())}')
        print(f'  skull x {qq[:, 0].min():.3f}..{qq[:, 0].max():.3f} y {qq[:, 1].min():.3f}..{qq[:, 1].max():.3f} z {qq[:, 2].min():.3f}..{qq[:, 2].max():.3f}; moved mean {np.linalg.norm(P2 - P, axis=1)[core].mean() * 100:.1f} cm max {np.linalg.norm(P2 - P, axis=1)[core].max() * 100:.1f} cm')
    # ---- the attributes of the head: the head mask for the look (mat.y 0.2 on the skull, fading down the neck; the ears take 1.0) ----
    headK = ss((hw - 0.3) / 0.6) * ((1 - ss(np.clip(tbr, 0, 1) / 0.7)) if LIZARD else ss((al_ + 0.10) / 0.16)); mat[:, 1] = np.clip(np.round(255 * 0.2 * headK), 0, 255).astype(np.uint8); jelly[ring, 2] = 0; fill[ring, 3] = 0
    # the old base rings shared their weight with the stalks' bones: that share goes to the head now (the ear bones must not dent the skull)
    gset = np.zeros(len(names), bool); gset[gidx] = True; hidx = bi['head']; moved = 0
    for v in np.where(gw > 0)[0]:
        s_, w_ = si[v].astype(int), sw[v].astype(int); s_[gset[s_] & (w_ > 0)] = hidx; acc = {}
        for a_, b_ in zip(s_, w_):
            if b_ > 0: acc[int(a_)] = acc.get(int(a_), 0) + int(b_)
        items = sorted(acc.items(), key=lambda kv: -kv[1])[:4]; si[v] = 0; sw[v] = 0
        for j, (a_, b_) in enumerate(items): si[v, j] = a_; sw[v, j] = b_
        sw[v, 0] += 255 - int(sw[v].sum()); moved += 1
    W = W.copy(); W[:, gidx] = 0; gw0 = gw.copy(); gw = np.zeros(n)   # (no body vertex carries gill weight any more; gw0 keeps the old share for the masks below)
    if verbose: print(f'  {moved} ring vertices: their stalk-bone share moved to the head')
    # ---- the old rings' holes closed (the untextured mesh): a fan to a centre on the ball, the centre's attributes its ring's ----
    keep = ~own; o2n = -np.ones(n, np.int64); o2n[keep] = np.arange(int(keep.sum())); nb_ = int(keep.sum()); T2 = o2n[T]
    # (the rims: the dropped vertices' neighbours, which is exactly where the drop left open edges; the untextured mesh has no seams)
    Pb = P2[keep]; cen, fanT, rep, vgroup = close_holes(Pb, T2, ring[keep], C); ncen = len(cen)
    def rep_attrs(rep, arrs): return [arr[rep].reshape(-1, arr.shape[1]) if len(rep) else np.zeros((0, arr.shape[1]), arr.dtype) for arr in arrs]
    sib, swb, jb, fb, mb = si[keep], sw[keep], jelly[keep], fill[keep], mat[keep]
    cpw = cp[:, :3].astype(float) / 32767 * cps + (P2 - P_orig)                 # (the crawl: the canonical place moved with each vertex)
    if LIZARD and nm == 'crawl':
        # (v10e: the bridge's canonical place (the frame of the skin's procedural detail and of the paint coat's lumps) laid again from its
        # edges, harmonic over the zone: as the old neck's own, moved with each vertex, it tore along the loop and across the throat)
        Azz, _ = adjacency(n, T); ez_ = (~zone) & ((Azz @ zone.astype(float)) > 0); ii_ = np.where(zone | ez_)[0]; cpw[ii_] = solve_fixed(Azz[ii_][:, ii_], ez_[ii_], cpw[ii_])
    cpb = cp[keep].copy()
    if nm == 'stand': cpb[:, :3] = np.clip(np.round(Pb / cps * 32767), -32767, 32767)
    else: cpb[:, :3] = np.clip(np.round(cpw[keep] / cps * 32767), -32767, 32767)
    si_c, sw_c, j_c, f_c, m_c, cp_c = rep_attrs(rep, [sib, swb, jb, fb, mb, cpb])
    if ncen: cp_c = cp_c.copy(); cp_c[:, :3] = np.array([cpb[vgroup == k, :3].astype(float).mean(0) for k in range(ncen)]).round().astype(np.int16)
    Pb = np.vstack([Pb, cen]); T2 = np.vstack([T2, fanT]); nb_ += ncen
    sib = np.vstack([sib, si_c]); swb = np.vstack([swb, sw_c]); jb = np.vstack([jb, j_c]); fb = np.vstack([fb, f_c]); mb = np.vstack([mb, m_c]); cpb = np.vstack([cpb, cp_c])
    if verbose: print(f'  {ncen} old stalk holes closed ({len(fanT)} fan tris), rims of {sorted(np.bincount(vgroup[vgroup >= 0]).tolist(), reverse=True)}; open edges near the head now {open_near(T2, Pb)}')
    Nb = vnormals(Pb, T2)
    # ---- the ears ----
    EARS = [ear_piece(sl, sgn, C, s) for sgn in (1.0, -1.0)]
    hv = np.where((hw[keep] > 0.95) & (gw[keep] < 0.02))[0]; kd_head = cKDTree(Pb[hv]); newb = {}; parts = []
    for E in EARS:
        Pe, Te, ew, sgn = E['P'], E['T'], E['ew'], E['sgn']; m = len(Pe); s_ = 'L' if sgn > 0 else 'R'
        # the root ring sunk into the skull, the root band lifted a hair off it; the ear's own normals, eased into the skull's near the root
        _, nh = kd_head.query(Pe); hn = Nb[hv[nh]]; rootK = 1.0 - ss(ew / 0.15)
        Pe = Pe - hn * (RING_IN * (ew < 0.001))[:, None] + hn * (RING_OUT * rootK * (ew >= 0.001))[:, None]
        Ne = vnormals(Pe, Te); Ne = unit(Ne * (1 - 0.7 * rootK)[:, None] + hn * (0.7 * rootK)[:, None])
        i1 = bi[f'gill0.{s_}.1']; i2 = bi[f'gill0.{s_}.2']
        wh = 1.0 - ss(ew / 0.22); w1 = ss(ew / 0.22) * (1.0 - ss((ew - 0.42) / 0.3)); w2 = ss((ew - 0.42) / 0.3); Wl = np.stack([wh, w1, w2], 1); Wl /= Wl.sum(1, keepdims=True)
        wq = np.clip(np.round(Wl * 255), 0, 255).astype(np.uint8)
        for i in range(m): wq[i, int(np.argmax(wq[i]))] += np.uint8(255 - int(wq[i].sum()))
        si_e = np.zeros((m, 4), np.uint8); sw_e = np.zeros((m, 4), np.uint8); si_e[:, 0] = bi['head']; si_e[:, 1] = i1; si_e[:, 2] = i2; sw_e[:, :3] = wq
        _, hroot = kd_head.query(E['hinge']); hroot = hv[hroot]
        jelly_e = np.zeros((m, 4), np.uint8); jelly_e[:, 3] = 255; jelly_e[:, 2] = np.clip(np.round(255 * 0.3 * ss((ew - 0.6) / 0.4)), 0, 255)   # (a little light through the tips)
        fr = fb[hroot].astype(float); fill_e = np.zeros((m, 4), np.uint8); fill_e[:, 0] = np.clip(fr[0] + 16 * ew, 0, 255); fill_e[:, 1] = np.clip(fr[1] + 16 * ew, 0, 255); fill_e[:, 2] = np.clip(np.round(40 * (1 - ew)), 0, 255)
        mat_e = np.zeros((m, 4), np.uint8); mat_e[:, 1] = np.clip(np.round(255 * (0.2 + 0.8 * ss(ew / 0.08))), 0, 255); mat_e[:, 3] = 230
        cpl = (Pe - C) + (cpb[hroot, :3].astype(float) / 32767 * cps - (Pb[hroot] - C)) if nm == 'crawl' else Pe.copy()
        cp_e = np.zeros((m, 4), np.int16); cp_e[:, :3] = np.clip(np.round(cpl / cps * 32767), -32767, 32767); cp_e[:, 3] = np.clip(np.round((ew * E['length'] + 1.1) / cps * 32767), -32767, 32767)
        # the chain: the hinge, the middle of the ear, the tip; Y down the ear, X the hinge along +x on BOTH sides (the puppet's mirror
        # convention: a mirrored bone keeps the hinge's world direction, so one flex angle swings both ears the same way fore and aft;
        # Z = X x Y points back on both, so one swing angle moves both tips to the same side)
        j1, e1, e2 = E['hinge'], E['mid'], E['tip']; t1 = unit(e1 - j1); t2 = unit(e2 - e1)
        for k_ in range(3):   # (gill1 and gill2 keep the rig's place with no geometry: at the hinge, the same frames)
            newb[f'gill{k_}.{s_}.1'] = dict(pos=j1, end=e1, q=mkframe(t1, [1.0, 0, 0])); newb[f'gill{k_}.{s_}.2'] = dict(pos=e1, end=e2, q=mkframe(t2, [1.0, 0, 0]))
        parts.append(dict(P=Pe, N=Ne, T=Te, si=si_e, sw=sw_e, jelly=jelly_e, fill=fill_e, mat=mat_e, cp=cp_e, hroot=hroot, ew=ew))
        if verbose: print(f'  ear {s_}: {m} verts {len(Te)} tris; hinge rel C {np.round(j1 - C, 3).tolist()} mid {np.round(e1 - C, 3).tolist()} tip {np.round(e2 - C, 3).tolist()}; x {Pe[:, 0].min() - C[0]:.3f}..{Pe[:, 0].max() - C[0]:.3f} y {Pe[:, 1].min() - C[1]:.3f}..{Pe[:, 1].max() - C[1]:.3f}')
    Pl = np.vstack([E['P'] for E in parts]); Nl = np.vstack([E['N'] for E in parts]); offs = np.cumsum([0] + [len(E['P']) for E in parts])
    T_l = np.vstack([E['T'] + nb_ + offs[i] for i, E in enumerate(parts)]); nl = len(Pl)
    Pf = np.vstack([Pb, Pl]); Nf = np.vstack([Nb, Nl]); Tf = np.vstack([T2, T_l]); n2 = len(Pf)
    sif = np.vstack([sib] + [E['si'] for E in parts]); swf = np.vstack([swb] + [E['sw'] for E in parts]); jf = np.vstack([jb] + [E['jelly'] for E in parts]); ff = np.vstack([fb] + [E['fill'] for E in parts]); mf = np.vstack([mb] + [E['mat'] for E in parts]); cpf = np.vstack([cpb] + [E['cp'] for E in parts])
    Nq = np.zeros((n2, 4), np.int8); Nq[:, :3] = np.clip(np.round(Nf * 127), -127, 127).astype(np.int8)
    # ---- the meta: the bones, the face radius (the slime's, scaled: the hat anchor at 0.94 r sits just under the crown as it did on the slime) ----
    bones = []
    for b in meta['bones']:
        b = dict(b)
        if b['name'] in newb: nb2 = newb[b['name']]; b['pos'] = np.round(nb2['pos'], 4).tolist(); b['end'] = np.round(nb2['end'], 4).tolist(); b['q'] = np.round(nb2['q'], 4).tolist()
        bones.append(b)
    meta['bones'] = bones; meta['bbox'] = [Pf.min(0).round(4).tolist(), Pf.max(0).round(4).tolist()]; meta['face'] = {'c': meta['face']['c'], 'r': round(SLIME_R * s, 4)}; meta['headr'] = round(SLIME_R * s, 4)
    if verbose:
        for b in bones:
            if b['name'].startswith('gill0.L'): print(f'  {b["name"]}: pos {b["pos"]} end {b["end"]} q {b["q"]}')
        print(f'  face.c {meta["face"]["c"]} r {meta["face"]["r"]}; headc {meta["headc"]} headr {meta["headr"]}; crown rel C {qq[:, 1].max():.3f}, hat anchor at {0.94 * meta["face"]["r"]:.3f}')
    os.makedirs(outsrc, exist_ok=True); os.makedirs(out, exist_ok=True)
    buf, off = pack([('position', Pf.astype(np.float32)), ('normal', Nq), ('skinIndex', sif), ('skinWeight', swf), ('index', Tf.astype(np.uint16).ravel()), ('cpos', cpf), ('jelly', jf), ('fill', ff), ('mat', mf)])
    m2 = dict(meta); m2['off7'] = off; m2['n'] = n2; m2['ni'] = int(Tf.size); open(f'{outsrc}/axo_{nm}.bin', 'wb').write(buf); json.dump(m2, open(f'{outsrc}/axo_{nm}.json', 'w'))
    # ---- the textured mesh: its vertices are copies of the untextured ones (by exact position, before the move), the lobes at its end too;
    # its own holes closed the same way (a ring copy per chart, so each fan stays in one chart) ----
    mt = json.load(open(f'{tex}/axo_{nm}.json')); bt = bytes(open(f'{tex}/axo_{nm}.bin', 'rb').read()); ot = mt['off7']; nt_all = mt['n']; nt = nt_all - N_LOBE
    Pt = np.frombuffer(bt, np.float32, nt_all * 3, ot['position']).reshape(nt_all, 3)[:nt]
    _, vm = cKDTree(P_orig.astype(np.float32)).query(Pt); miss = np.linalg.norm(P_orig[vm] - Pt, axis=1); assert miss.max() < 1e-6, f'textured mesh is not a copy of the untextured one (max {miss.max()})'
    Tt = np.frombuffer(bt, np.uint16, mt['ni'], ot['index']).reshape(-1, 3).astype(np.int64); Tt = Tt[(Tt < nt).all(1)]
    uvt = np.frombuffer(bt, np.uint16, nt_all * 2, ot['uv']).reshape(nt_all, 2)[:nt]; texb = bt[ot['tex']:ot['tex'] + mt['texLen']]
    rd = lambda k_, dt, w: np.frombuffer(bt, dt, nt_all * w, ot[k_]).reshape(nt_all, w)[:nt]
    own_t = own[vm]; Tt = Tt[~own_t[Tt].any(1)]; used = np.zeros(nt, bool); used[Tt.ravel()] = True; keept = ~own_t & used
    o2nt = -np.ones(nt, np.int64); o2nt[keept] = np.arange(int(keept.sum())); ntb = int(keept.sum()); Tt2 = o2nt[Tt]; assert (Tt2 >= 0).all()
    Ptb = P2[vm][keept]; uvb = uvt[keept]; vmk = vm[keept]; ringt = ring[vmk]; vgroup_t = vgroup[o2n[vmk]]   # (the rims' copies and their holes)
    cen_t, fanTt, rep_t, chains_t = close_holes_tex(Ptb, Tt2, ringt, C, vgroup_t, cen); ncen_t = len(cen_t)
    sit = si[vm][keept]; swt = sw[vm][keept]; jt = jelly[vm][keept]; ft = fill[vm][keept]; mtt = mat[vm][keept]   # (the weights with the stalk share moved to the head, not the file's own copies)
    cpt = r['cp'][:n][vm].copy()
    if nm == 'stand': cpt[:, :3] = np.clip(np.round(P2[vm] / cps * 32767), -32767, 32767)
    else: cpt[:, :3] = np.clip(np.round(cpw[vm] / cps * 32767), -32767, 32767)
    cpt = cpt[keept]
    si_c, sw_c, j_c, f_c, m_c, cp_c, uv_c = rep_attrs(rep_t, [sit, swt, jt, ft, mtt, cpt, uvb])
    if ncen_t:
        cp_c = cp_c.copy(); cp_c[:, :3] = np.array([cpt[ch, :3].astype(float).mean(0) for ch in chains_t]).round().astype(np.int16)
        uv_c = np.array([uvb[ch].astype(float).mean(0) for ch in chains_t]).round().astype(np.uint16)
        spread = [float(np.ptp(uvb[ch].astype(float) / 65535, axis=0).max()) for ch in chains_t]
        if verbose: print(f'  textured: {ncen_t} rim chains fanned, of {sorted([len(c) for c in chains_t], reverse=True)[:12]}..., uv spread max {max(spread):.3f}')
    Ptb = np.vstack([Ptb, cen_t]); Tt2 = np.vstack([Tt2, fanTt]); uvb = np.vstack([uvb, uv_c]); ntb += ncen_t
    if verbose: print(f'  textured: open edges near the head now {open_near(Tt2, Ptb)} (seam copies count as open)')
    sit = np.vstack([sit, si_c]); swt = np.vstack([swt, sw_c]); jt = np.vstack([jt, j_c]); ft = np.vstack([ft, f_c]); mtt = np.vstack([mtt, m_c]); cpt = np.vstack([cpt, cp_c])
    # the textured copies take the welded mesh's normals (a split mesh's own would break along every atlas seam: dark and pale lines
    # over the chest, shoulders and arms); the hole centres' copies take their hole's
    Nt_body = np.zeros((ntb, 4), np.int8); Nt_body[:ntb - ncen_t, :3] = np.clip(np.round(Nb[o2n[vmk]] * 127), -127, 127).astype(np.int8)
    if ncen_t: _, jc = cKDTree(cen).query(cen_t); Nt_body[ntb - ncen_t:, :3] = np.clip(np.round(Nb[nb_ - ncen + jc] * 127), -127, 127).astype(np.int8)
    # the ears' uv: the skin's texel nearest the hinge (the look colours the ear from it)
    ht = np.where((hw[vm][keept] > 0.95) & (gw[vm][keept] < 0.02))[0]; kd_t = cKDTree(Ptb[ht]); uv_l = np.zeros((nl, 2), np.uint16); o_ = 0
    for E in parts:
        m = len(E['P']); _, j = kd_t.query(Pb[E['hroot']]); uv_l[o_:o_ + m] = uvb[ht[j]]; o_ += m
    Pt2 = np.vstack([Ptb, Pl]).astype(np.float32); Nt2 = np.vstack([Nt_body, Nq[n2 - nl:]]); cqt = np.vstack([cpt] + [E['cp'] for E in parts])
    sit = np.vstack([sit] + [E['si'] for E in parts]); swt = np.vstack([swt] + [E['sw'] for E in parts]); jt = np.vstack([jt] + [E['jelly'] for E in parts]); ft = np.vstack([ft] + [E['fill'] for E in parts]); mtt = np.vstack([mtt] + [E['mat'] for E in parts])
    uvt2 = np.vstack([uvb, uv_l]); Tt3 = np.vstack([Tt2, T_l - nb_ + ntb])
    buf2, off2 = pack([('position', Pt2), ('normal', Nt2), ('skinIndex', sit), ('skinWeight', swt), ('index', Tt3.astype(np.uint16).ravel()), ('cpos', cqt), ('jelly', jt), ('fill', ft), ('mat', mtt), ('uv', uvt2), ('tex', np.frombuffer(texb, np.uint8))])
    for k_ in ('bones', 'bbox', 'face', 'headc', 'headr'): mt[k_] = meta[k_]
    mt['off7'] = off2; mt['n'] = ntb + nl; mt['ni'] = int(Tt3.size)
    open(f'{out}/axo_{nm}.bin', 'wb').write(buf2); json.dump(mt, open(f'{out}/axo_{nm}.json', 'w'))
    # (the old rings and the new centres of the textured mesh, for capfix.py: their texels get repainted skin)
    capv = np.where(ringt)[0].tolist() + list(range(ntb - ncen_t, ntb))
    json.dump({'cap_verts': capv, 'centres': list(range(ntb - ncen_t, ntb)), 'n_body': ntb, 'neck_verts': np.where(((bandz | zone) if LIZARD else (zone & (al_ > -0.3)))[vmk])[0].tolist(), 'neck_t': (np.clip(tbr[vmk][np.where(((bandz | zone) if LIZARD else zone)[vmk])[0]], -1, 2).round(3).tolist() if LIZARD else None), 'neck_axis': {'o': hbj.tolist(), 'n': nax.tolist()}, 'lizard': LZ}, open(f'{out}/axo_{nm}_caps.json', 'w'))
    if verbose: print(f'  {out}/axo_{nm}.bin {len(buf2)} bytes ({ntb + nl} verts: body {ntb} + ears {nl}, {len(Tt3)} tris; was {nt_all}); {outsrc}/axo_{nm}.bin ({n2} verts, {len(Tf)} tris)')
if __name__ == '__main__':
    a = sys.argv[1:]; untex = S + '/fable2/rt3src'; tex = S + '/fable2/rt3'; out = WORK + '/rt4'; outsrc = WORK + '/rt4src'; s = SCALE
    while a:
        k = a.pop(0)
        if k == '--untex': untex = a.pop(0)
        elif k == '--tex': tex = a.pop(0)
        elif k == '--out': out = a.pop(0)
        elif k == '--outsrc': outsrc = a.pop(0)
        elif k == '--scale': s = float(a.pop(0))
        elif k == '--lizard': LIZARD = True; out = WORK + '/rt6'; outsrc = WORK + '/rt6src'
    for nm in ('stand', 'crawl'): reshape(nm, untex, tex, out, outsrc, s)
