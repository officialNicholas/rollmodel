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
    key = np.round(P, 4); _, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True); own = (cnt[inv.ravel()] >= 3) & ((hw + gw) > 0.02)
    T = T[~own[T].any(1)]; A0, _ = adjacency(n, r['T'][(r['T'] < n).all(1)]); ring = ((A0 @ own.astype(float)) > 0) & ~own
    def open_near(TT, PP):
        E = np.concatenate([TT[:, [0, 1]], TT[:, [1, 2]], TT[:, [2, 0]]]); u_, c_ = np.unique(np.sort(E, 1), axis=0, return_counts=True); op = u_[c_ == 1]
        return int((np.linalg.norm(PP[op].mean(1) - C, axis=1) < 0.5).sum()) if len(op) else 0
    if verbose: print(f'{nm}: {n_all} verts -> lobes off {n}, retired stalk verts {int(own.sum())} dropped; {len(T)} tris, {int(ring.sum())} ring verts; open edges near the head before {open_near(r["T"][(r["T"] < n).all(1)], P)}, after the drop {open_near(T, P)}')
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
    low = neck_floor(P2)
    # the join smoothed: a few Laplacian steps over the blend's edge and the old rings (positions only; the ball's own surface untouched)
    A, deg = adjacency(n, T); edge = grp & (k > 0.02) & (k < 0.98); band = edge | ring | low
    for _ in range(3): band = band | ((A @ band.astype(float)) > 0) & grp & (k < 0.999)
    sm = band & ~own
    for _ in range(8):
        y_ = (A @ P2) / np.maximum(deg, 1)[:, None]; P2[sm] = 0.5 * P2[sm] + 0.5 * y_[sm]
    neck_floor(P2)
    core = (hw > 0.95) & ~own; qq = P2[core] - C
    if verbose:
        print(f'  slime ball hits {int(onball.sum())} of {int(grp.sum())} head-group verts; blended {int((k > 0.5).sum())}; neck floor on {int(low.sum())}; smoothed {int(sm.sum())}')
        print(f'  skull x {qq[:, 0].min():.3f}..{qq[:, 0].max():.3f} y {qq[:, 1].min():.3f}..{qq[:, 1].max():.3f} z {qq[:, 2].min():.3f}..{qq[:, 2].max():.3f}; moved mean {np.linalg.norm(P2 - P, axis=1)[core].mean() * 100:.1f} cm max {np.linalg.norm(P2 - P, axis=1)[core].max() * 100:.1f} cm')
    # ---- the attributes of the head: the head mask for the look (mat.y 0.2 on the skull, fading down the neck; the ears take 1.0) ----
    headK = ss((hw - 0.3) / 0.6); mat[:, 1] = np.clip(np.round(255 * 0.2 * headK), 0, 255).astype(np.uint8); jelly[ring, 2] = 0; fill[ring, 3] = 0
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
    cpb = cp[keep].copy()
    if nm == 'stand': cpb[:, :3] = np.clip(np.round(Pb / cps * 32767), -32767, 32767)
    else: cpb[:, :3] = np.clip(np.round((cp[keep, :3].astype(float) / 32767 * cps + (P2 - P)[keep]) / cps * 32767), -32767, 32767)
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
    _, vm = cKDTree(P.astype(np.float32)).query(Pt); miss = np.linalg.norm(P[vm] - Pt, axis=1); assert miss.max() < 1e-6, f'textured mesh is not a copy of the untextured one (max {miss.max()})'
    Tt = np.frombuffer(bt, np.uint16, mt['ni'], ot['index']).reshape(-1, 3).astype(np.int64); Tt = Tt[(Tt < nt).all(1)]
    uvt = np.frombuffer(bt, np.uint16, nt_all * 2, ot['uv']).reshape(nt_all, 2)[:nt]; texb = bt[ot['tex']:ot['tex'] + mt['texLen']]
    rd = lambda k_, dt, w: np.frombuffer(bt, dt, nt_all * w, ot[k_]).reshape(nt_all, w)[:nt]
    own_t = own[vm]; Tt = Tt[~own_t[Tt].any(1)]; used = np.zeros(nt, bool); used[Tt.ravel()] = True; keept = ~own_t & used
    o2nt = -np.ones(nt, np.int64); o2nt[keept] = np.arange(int(keept.sum())); ntb = int(keept.sum()); Tt2 = o2nt[Tt]; assert (Tt2 >= 0).all()
    Ptb = P2[vm][keept]; uvb = uvt[keept]; vmk = vm[keept]; ringt = ring[vmk]; vgroup_t = vgroup[o2n[vmk]]   # (the rims' copies and their holes)
    cen_t, fanTt, rep_t, chains_t = close_holes_tex(Ptb, Tt2, ringt, C, vgroup_t, cen); ncen_t = len(cen_t)
    sit = rd('skinIndex', np.uint8, 4)[keept]; swt = rd('skinWeight', np.uint8, 4)[keept]; jt = jelly[vm][keept]; ft = fill[vm][keept]; mtt = mat[vm][keept]
    cpt = r['cp'][:n][vm].copy()
    if nm == 'stand': cpt[:, :3] = np.clip(np.round(P2[vm] / cps * 32767), -32767, 32767)
    else: cpt[:, :3] = np.clip(np.round((cpt[:, :3].astype(float) / 32767 * cps + (P2 - P)[vm]) / cps * 32767), -32767, 32767)
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
    Ntb = vnormals(Ptb, Tt2); Nt_body = np.zeros((ntb, 4), np.int8); Nt_body[:, :3] = np.clip(np.round(Ntb * 127), -127, 127).astype(np.int8)
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
    capv = np.where(ringt)[0].tolist() + list(range(ntb - ncen_t, ntb)); json.dump({'cap_verts': capv, 'centres': list(range(ntb - ncen_t, ntb)), 'n_body': ntb}, open(f'{out}/axo_{nm}_caps.json', 'w'))
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
    for nm in ('stand', 'crawl'): reshape(nm, untex, tex, out, outsrc, s)
