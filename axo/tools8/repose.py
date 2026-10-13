# Straighten Meshy's posed model into a symmetric crawl rest: the front body (chest, arms) turned 40 deg back into line with the hind body
# and the spine straightened, the head (face) turned 33 deg back to look straight ahead, the tail's sideways S taken out (its rise kept),
# each pair of limbs and the two ears set to the average of the two sides. Done as skinning: the game skeleton fitted to the source pose
# (rigspec.py), bone heat weights on the source mesh, each bone's rigid move from its source place to its target place, blended by dual
# quaternions. Writes fable4/work/reposed.npz (positions in the work frame's units, before the final scale and placement).
#   python3 -I repose.py
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, json
import meshkit as mk, rigspec as rs, boneheat as bh, dqs
W_ = rs.S + '/fable5/work'
MIR = np.array([-1.0, 1, 1])
# (source units: the game frame's (0.37, 0.11, -0.86) ankle; the knee's bulge up, back and a little out: the runtime takes each limb's
# bend from the rest (its pole), and in the air it tucks the foot up behind the hip, where a knee bulging straight up and back (v246's
# pole) swings this model's long thigh in across the belly; 20 deg further out it stays at the side)
LEG_ANKLE = [0.285, 0.0756, -0.138]; LEG_POLE = [0.32, 0.82, -0.47]
# the arms turned out about the shoulder (deg; the hands kept pointing ahead): the elbow then bends straight back, as v246's, so in the
# air tuck (the hand drawn up behind the shoulder) the elbow folds up and back over it instead of the arm rolling half a turn
ARM_YAW = 40.0
# the bones moved in the repose (digits ride on their hand / foot); each: (bone, end joint, part)
REPOSE = [('hips', 'spine', 'H'), ('spine', 'spine1', 'H'), ('spine1', 'chest', 'S'), ('chest', 'neck', 'F'), ('neck', 'head', 'K'), ('head', 'headTop', 'K'),
          ('thigh.L', 'shin.L', 'H'), ('shin.L', 'foot.L', 'H'), ('foot.L', 'toeEnd.L', 'H'), ('thigh.R', 'shin.R', 'H'), ('shin.R', 'foot.R', 'H'), ('foot.R', 'toeEnd.R', 'H'),
          ('shoulder.L', 'upperarm.L', 'F'), ('upperarm.L', 'forearm.L', 'F'), ('forearm.L', 'hand.L', 'F'), ('hand.L', 'handEnd.L', 'F'),
          ('shoulder.R', 'upperarm.R', 'F'), ('upperarm.R', 'forearm.R', 'F'), ('forearm.R', 'hand.R', 'F'), ('hand.R', 'handEnd.R', 'F'),
          ('tail1', 'tail2', 'H'), ('tail2', 'tail3', 'H'), ('tail3', 'tail4', 'H'), ('tail4', 'tail5', 'H'), ('tail5', 'tail6', 'H'), ('tail6', 'tailTip', 'H'),
          ('gill0.L.1', 'gill0.L.2', 'K'), ('gill0.L.2', 'earTip.L', 'K'), ('gill0.R.1', 'gill0.R.2', 'K'), ('gill0.R.2', 'earTip.R', 'K')]
PART_YAW = {'H': 0.0, 'S': 20.0, 'F': rs.FRONT_YAW, 'K': rs.HEAD_YAW}
def source():
    J = rs.source_joints()
    J['headTop'] = rs.from_part(np.array(rs.HEAD['head']) + [0, 0.3, 0], rs.HEAD_YAW)
    for s_ in 'LR':
        J[f'toeEnd.{s_}'] = np.mean(rs.TOE_TIPS[s_], 0) * [1, 0, 1] + [0, 0.03, 0]
        J[f'handEnd.{s_}'] = rs.from_part(np.array(rs.FINGER_TIPS[s_][1]) + [0, 0.01, 0], rs.FRONT_YAW)
    return J
def target(J):
    T = {}; T['hips'] = J['hips'].copy()
    for a, b in (('hips', 'spine'), ('spine', 'spine1'), ('spine1', 'chest')):
        v = J[b] - J[a]; L = np.linalg.norm(v); dy = v[1]; T[b] = T[a] + np.array([0, dy, np.sqrt(max(L * L - dy * dy, 1e-9))])
    shift_f = T['chest'] - np.array(rs.FRONT['chest'])
    for k, v in rs.FRONT.items(): T[k] = np.array(v) + shift_f
    T['handEnd.L'] = np.array(rs.FINGER_TIPS['L'][1]) + [0, 0.01, 0] + shift_f; T['handEnd.R'] = np.array(rs.FINGER_TIPS['R'][1]) + [0, 0.01, 0] + shift_f
    h = rs.to_part(J['head'], rs.FRONT_YAW) + shift_f; h[0] = 0.0; shift_h = h - np.array(rs.HEAD['head'])
    for k, v in rs.HEAD.items(): T[k] = np.array(v) + shift_h
    T['headTop'] = T['head'] + [0, 0.3, 0]
    for k in ('thigh.L', 'shin.L', 'foot.L', 'toes.L', 'thigh.R', 'shin.R', 'foot.R', 'toes.R', 'toeEnd.L', 'toeEnd.R'): T[k] = J[k].copy()
    # the tail: its sideways bends taken out, each segment's length and rise kept
    tl = ['tail1', 'tail2', 'tail3', 'tail4', 'tail5', 'tail6', 'tailTip']; T['tail1'] = J['tail1'] * [0, 1, 1]
    for a, b in zip(tl[:-1], tl[1:]):
        v = J[b] - J[a]; L = np.linalg.norm(v); T[b] = T[a] + np.array([0, v[1], -np.sqrt(max(L * L - v[1] ** 2, 1e-9))])
    # the two sides averaged (the left one and the mirrored right one)
    for k in list(T):
        if k.endswith('.L') or '.L.' in k:
            r = k.replace('.L', '.R'); a = 0.5 * (T[k] + T[r] * MIR); T[k] = a; T[r] = a * MIR
    # the arms turned out about the shoulder joint (forearm, wrist and hand with them), the hand turned back to point ahead
    if ARM_YAW:
        for s_, m in (('L', 1), ('R', -1)):
            piv = T[f'upperarm.{s_}'].copy(); R = rs.ry(np.radians(ARM_YAW * m))
            for k in (f'forearm.{s_}', f'hand.{s_}', f'handEnd.{s_}'): T[k] = piv + R @ (T[k] - piv)
            T[f'handEnd.{s_}'] = T[f'hand.{s_}'] + rs.ry(np.radians(-ARM_YAW * m)) @ (T[f'handEnd.{s_}'] - T[f'hand.{s_}'])
    # the hind legs: the ankle drawn in toward where the gait plants the foot, the knee bent up and back over it (a clear bulge for the
    # IK's pole, as v246's legs: a straight rest leg leaves the IK no side to fold the knee to)
    if LEG_ANKLE is not None:
        for s_, m in (('L', 1), ('R', -1)):
            hip = T[f'thigh.{s_}']; an = np.array(LEG_ANKLE) * [m, 1, 1]; d_an = an - T[f'foot.{s_}']
            L1 = np.linalg.norm(J[f'shin.{s_}'] - J[f'thigh.{s_}']); L2 = np.linalg.norm(J[f'foot.{s_}'] - J[f'shin.{s_}'])
            n = an - hip; d = np.linalg.norm(n); n /= d; pole = np.array(LEG_POLE) * [m, 1, 1]; pp = pole - n * (pole @ n); pp /= np.linalg.norm(pp)
            ca = np.clip((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1); kn = hip + L1 * (n * ca + pp * np.sqrt(1 - ca * ca))
            T[f'shin.{s_}'] = kn
            for k2 in (f'foot.{s_}', f'toes.{s_}', f'toeEnd.{s_}'): T[k2] = T[k2] + d_an
    return T
def flat_yaw(v): return np.arctan2(v[0], v[2])
def bone_maps(J, T, extra=None):
    """each bone's rigid move (R, t): its part's turn, then the shortest arc onto the target direction; the hands and feet (flat on the
    ground in both poses) only turn about the vertical, from their own heading to the target's; extra: {bone: (R, t)} applied after"""
    Rs, ts = [], []
    for b, e, part in REPOSE:
        if b.startswith(('hand.', 'foot.')):
            R = rs.ry(flat_yaw(T[e] - T[b]) - flat_yaw(J[e] - J[b]))
        else:
            Rp = rs.ry(np.radians(-PART_YAW[part])); ds = Rp @ (J[e] - J[b]); dt = T[e] - T[b]; R = dqs.arc(ds, dt) @ Rp
        t = T[b] - R @ J[b]
        if extra and b in extra: R2, t2 = extra[b]; R, t = R2 @ R, R2 @ t + t2
        Rs.append(R); ts.append(t)
    return Rs, ts
def half(R, t):
    """H with H o H = (R, t)"""
    Rh = dqs.rot_power(R, 0.5); th = np.linalg.solve(Rh + np.eye(3), t); return Rh, th
def ear_extra(P, W, bones):
    """move the two ears to their average: the mirrored right ear fitted onto the left one (ICP), each moved half way"""
    bi = {b: i for i, b in enumerate(bones)}; gL = W[:, bi['gill0.L.1']] + W[:, bi['gill0.L.2']]; gR = W[:, bi['gill0.R.1']] + W[:, bi['gill0.R.2']]
    A = P[gR > 0.6] * MIR; B = P[gL > 0.6]; R, t, err = dqs.icp(A, B)
    Rh, th = half(R, t); Ri = Rh.T; ti = -Ri @ th          # H^-1 for the left ear
    M = np.diag(MIR); Rr = M @ Rh @ M; tr = M @ th           # mirror(H) for the right ear
    ang = np.degrees(2 * np.arccos(min(1, abs(dqs.mat2quat(R)[3])))); print(f'  ears: the mirrored right ear sat {ang:.1f} deg / {np.linalg.norm(B.mean(0) - A.mean(0)):.3f} from the left (rms {err:.4f}); both moved half way')
    return {'gill0.L.1': (Ri, ti), 'gill0.L.2': (Ri, ti), 'gill0.R.1': (Rr, tr), 'gill0.R.2': (Rr, tr)}
if __name__ == '__main__':
    import symmetrize as sy
    z = np.load(W_ + '/work.npz'); P, N, UV, Tri, wid, rep = z['P'], z['N'], z['UV'], z['T'], z['wid'], z['rep']
    Pw = P[rep]; Tw = wid[Tri]; Nw = mk.vertex_normals(Pw, Tw)
    J = source(); T = target(J); bones = [b for b, _, _ in REPOSE]
    segs = [(J[b], J[e]) for b, e, _ in REPOSE]
    Wt, near = bh.bone_heat(Pw, Tw, Nw, segs)
    Rs, ts = bone_maps(J, T); P1 = dqs.dqs_deform(Pw, Wt, Rs, ts)
    ex = ear_extra(P1, Wt, bones); Rs, ts = bone_maps(J, T, ex); P2 = dqs.dqs_deform(Pw, Wt, Rs, ts)
    bi = {b: i for i, b in enumerate(bones)}; ext = Wt[:, [bi[b] for b in ('hand.L', 'hand.R', 'foot.L', 'foot.R')]].sum(1)
    P3 = sy.symmetrize(P2, Tw, iters=int(os.environ.get('SYM_ITERS', 4)), k=0.5, mask=np.clip(1 - 1.5 * ext, 0, 1))   # (hands and feet: their own shapes)
    # (the soles on the ground: nothing below it; the few vertices the knee bend and the hands' turn pushed under are lifted onto it and
    # their neighbours eased)
    low = P3[:, 1] < 0; P3[low, 1] = 0.0; Eg = mk.edges(Tw); Ag = mk.adjacency(len(P3), Eg); dg = np.maximum(np.asarray(Ag.sum(1)).ravel(), 1)
    near = (Ag @ low.astype(float) > 0) | low
    for _ in range(2):
        avg = (Ag @ P3) / dg[:, None]; P3[near & ~low, 1] = 0.5 * P3[near & ~low, 1] + 0.5 * np.maximum(avg[near & ~low, 1], 0)
    print(f'  {int(low.sum())} vertices under the ground lifted onto it')
    # (triangles the bend or the mirroring turned over, against their orientation on the source model, eased out)
    P3 = mk.untangle(P3, Tw, ref_fn=None)
    Nt = mk.vertex_normals(P3, Tw)
    np.savez(W_ + '/reposed.npz', Pw=P3, Pw_nosym=P2, Nw=Nt, Tw=Tw, wid=wid, rep=rep, UV=UV, T=Tri, W=Wt, J=json.dumps({k: v.tolist() for k, v in J.items()}), JT=json.dumps({k: v.tolist() for k, v in T.items()}), bones=json.dumps(bones))
    print('reposed: bbox', P3.min(0).round(3), P3.max(0).round(3))
    # the digit tips carried to the reposed hands and feet (for the digit bones): each source tip moved by its hand's / foot's map
    import centerline as cl
    G, E = mk.graph(P3, Tw); bi = {b: i for i, b in enumerate(bones)}; dig = {}
    tips_src = {'hand.L': [rs.from_part(p, rs.FRONT_YAW) for p in rs.FINGER_TIPS['L']], 'hand.R': [rs.from_part(p, rs.FRONT_YAW) for p in rs.FINGER_TIPS['R']],
                'foot.L': [np.array(p) for p in rs.TOE_TIPS['L']], 'foot.R': [np.array(p) for p in rs.TOE_TIPS['R']]}
    for hb, tl in tips_src.items():
        R, t = Rs[bi[hb]], ts[bi[hb]]; dig[hb] = []
        for p in tl:
            q = R @ p + t; near = np.where(np.linalg.norm(P3 - q, axis=1) < 0.06)[0]
            v = near[np.argmin(P3[near, 1] + 0.0 * P3[near, 0])] if len(near) else np.argmin(np.linalg.norm(P3 - q, axis=1))
            # (the digit's own tip: of the vertices near the carried tip, the one farthest from the hand's wrist)
            wr = T[hb]; v = near[np.argmax(np.linalg.norm((P3[near] - wr) * [1, 0, 1], axis=1))] if len(near) else v
            dig[hb].append({'tip': P3[v].tolist()})
    json.dump(dig, open(W_ + '/digits_rep.json', 'w'))
