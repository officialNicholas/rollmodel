# The game skeleton (the v246 crawl's bones: names, parents, roles) fitted to the new model in its source pose (the work frame of
# prep.py), measured part by part: the hind body (hips, hind legs, tail) in the work frame itself; the front body (chest, arms) in
# a frame turned 40 deg about the vertical (Meshy posed the front half of the body turned to the character's left), its mirror plane at
# x = -0.125; the head (head, ears) in a frame turned 33 deg (the flat face's own normal), its mirror plane at x = -0.065.
import numpy as np, json
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
CUR = S + '/fable3/rt6/axo_crawl.json'          # the v246 crawl (bone names, parents, order)
def ry(a): c, s = np.cos(a), np.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
PIV = np.array([0.0, 0.2, 0.1])
FRONT_YAW, HEAD_YAW = 40.0, 33.0
def from_part(p, yaw): return (np.asarray(p, float) - PIV) @ ry(np.radians(yaw)).T + PIV
def to_part(p, yaw): return (np.asarray(p, float) - PIV) @ ry(np.radians(-yaw)).T + PIV
def bones_order():
    m = json.load(open(CUR)); return [(b['name'], b['parent']) for b in m['bones']]
# ---- the source joints (each bone's head; ends are its child's head or listed in ENDS) ----
HIND = {
    'hips': [0.0, 0.21, -0.12],
    'thigh.L': [0.12, 0.17, -0.10], 'shin.L': [0.27, 0.12, -0.15], 'foot.L': [0.43, 0.075, -0.19], 'toes.L': [0.50, 0.045, -0.17],
    'thigh.R': [-0.13, 0.165, -0.07], 'shin.R': [-0.27, 0.12, -0.12], 'foot.R': [-0.42, 0.075, -0.19], 'toes.R': [-0.49, 0.045, -0.18],
}
TOE_TIPS = {'L': [[0.613, 0.012, -0.243], [0.619, 0.012, -0.101], [0.493, 0.012, -0.039]], 'R': [[-0.484, 0.012, -0.300], [-0.596, 0.012, -0.196], [-0.508, 0.012, -0.088]]}
# (toe order: the rear / outer toe first (toe0), the middle (toe1 and toe2 share it), the front / inner one last (toe3), as the v246 feet)
FRONT = {   # (wf40)
    'chest': [-0.125, 0.24, 0.47],
    'shoulder.L': [-0.06, 0.27, 0.48], 'upperarm.L': [0.055, 0.245, 0.50], 'forearm.L': [0.175, 0.15, 0.53], 'hand.L': [0.21, 0.08, 0.65],
    'shoulder.R': [-0.19, 0.27, 0.48], 'upperarm.R': [-0.30, 0.28, 0.50], 'forearm.R': [-0.458, 0.152, 0.493], 'hand.R': [-0.40, 0.06, 0.685],
}
FINGER_TIPS = {'L': [[0.362, 0.025, 0.801], [0.256, 0.025, 0.89], [0.068, 0.025, 0.878]], 'R': [[-0.611, 0.025, 0.812], [-0.481, 0.025, 0.845], [-0.366, 0.025, 0.757]]}
HEAD = {    # (wf33)
    'neck': [-0.065, 0.33, 0.62], 'head': [-0.065, 0.42, 0.66],
    'gill0.L.1': [0.15, 0.76, 0.55], 'gill0.L.2': [0.24, 0.55, 0.47], 'earTip.L': [0.28, 0.34, 0.40],
    'gill0.R.1': [-0.28, 0.76, 0.56], 'gill0.R.2': [-0.38, 0.56, 0.50], 'earTip.R': [-0.43, 0.41, 0.45],
}
TAIL_PTS = [[0.0, 0.235, -0.30], [0.012, 0.21, -0.45], [0.045, 0.195, -0.60], [0.09, 0.205, -0.73], [0.125, 0.235, -0.86], [0.145, 0.285, -0.97], [0.147, 0.36, -1.07], [0.14, 0.45, -1.13], [0.12, 0.56, -1.19]]
def resample(pts, n):
    pts = np.asarray(pts, float); seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); cum = np.r_[0, np.cumsum(seg)]; s = np.linspace(0, cum[-1], n)
    return np.array([np.interp(s, cum, pts[:, k]) for k in range(3)]).T
def source_joints():
    J = {k: np.array(v) for k, v in HIND.items()}
    for k, v in FRONT.items(): J[k] = from_part(v, FRONT_YAW)
    for k, v in HEAD.items(): J[k] = from_part(v, HEAD_YAW)
    # the spine: a curve from the hips joint out of the hind body (along +z) into the chest (along the front body's own forward)
    h = J['hips']; c = J['chest']; fwd = ry(np.radians(FRONT_YAW)) @ np.array([0, 0, 1.0])
    L = np.linalg.norm(c - h); b1 = h + np.array([0, 0, 1.0]) * L * 0.4; b2 = c - fwd * L * 0.35
    bez = lambda t: (1 - t) ** 3 * h + 3 * (1 - t) ** 2 * t * b1 + 3 * (1 - t) * t ** 2 * b2 + t ** 3 * c
    J['spine'] = bez(0.36); J['spine1'] = bez(0.68)
    tl = resample(TAIL_PTS, 7)
    for k in range(6): J[f'tail{k + 1}'] = tl[k]
    J['tailTip'] = tl[6]
    for s_ in 'LR':
        J[f'earTip.{s_}'] = J.pop(f'earTip.{s_}')
    return J
