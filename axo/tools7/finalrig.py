# The game skeleton on the reposed model, in the game's frame (scaled, the shoulders at z = 0, the ground at y = 0): every bone of the
# v246 crawl by name, parent and order; joints from the reposed model's own anatomy; canonical frames carried over from the v246 crawl's
# (each turned by the shortest arc from the old bone's direction to the new one, so twist and flexion sides keep their sense), the digits
# taking their hand's / foot's frame as in v246, the ears built as v10 (Y down the ear, X toward +x on both sides).
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, json
import dqs
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
CUR = S + '/fable3/rt6/axo_crawl.json'
SCALE = 1.3
def mkframe(y, xhint):
    """Y along y, X as close to xhint as it can be, Z = X x Y (columns X, Y, Z) - the v10 ear frame"""
    y = y / np.linalg.norm(y); x = np.asarray(xhint, float) - y * (y @ xhint); x /= np.linalg.norm(x); z = np.cross(x, y); return np.stack([x, y, z], 1)
def find_ears(P, T, J, G=None):
    """each ear from its own shape (game frame): rings of geodesic distance from its lowest point; the flap's rings wide, then the
    narrow root that hangs it from the skull, then the skull's rings growing. The hinge: the root's narrowest ring; the vertices up to
    a little past it are the ear's"""
    import meshkit as mk, centerline as cl
    Gm, E = mk.graph(P, T); A = mk.adjacency(len(P), E); out = {}
    for s in 'LR':
        tipJ = J[f'earTip.{s}']; near = np.where(np.linalg.norm(P - tipJ, axis=1) < 0.15)[0]; v = near[np.argmin(P[near, 1])]
        seeds = np.where(np.linalg.norm(P - P[v], axis=1) < 0.03)[0]
        d, rows = cl.rings(P, Gm, E, A, seeds, step=0.03, width=0.06, maxd=0.8, rmax=0.5)
        dd = np.array([r[0] for r in rows]); cc = np.array([r[1] for r in rows]); rr = np.array([r[2] for r in rows])
        seg = np.where((dd > 0.33) & (dd < 0.62))[0]; kr = seg[np.argmin(rr[seg])]   # (the root: the narrowest ring between the flap and the skull)
        tip = cc[0]; hinge = cc[kr]; dl = dd[kr]
        km = np.argmin(np.abs(dd - 0.5 * dl)); mid = cc[km]
        out[s] = dict(hinge=hinge, mid=mid, tip=tip, d=d, droot=dl, verts=np.where(d < dl + 0.02)[0])
    return out
class Rig:
    def __init__(self, JT, digits, Pw, ears=None):
        self.cur = json.load(open(CUR)); self.order = [(b['name'], b['parent']) for b in self.cur['bones']]
        self.Z0 = JT['upperarm.L'][2]; self.Y0 = float(Pw[:, 1].min())
        G = self.G = lambda p: (np.asarray(p, float) - np.array([0.0, self.Y0, self.Z0])) * SCALE
        J = {k: G(v) for k, v in JT.items()}; self.J = J; self.P = G(Pw)
        B = {}
        B['hips'] = (J['hips'], J['spine']); B['spine'] = (J['spine'], J['spine1']); B['spine1'] = (J['spine1'], J['chest']); B['chest'] = (J['chest'], J['neck'])
        B['neck'] = (J['neck'], J['head']); B['head'] = (J['head'], J['head'] + [0, 0.3, 0])
        self.dig = {}
        for s in 'LR':
            m = 1 if s == 'L' else -1
            B[f'shoulder.{s}'] = (J[f'shoulder.{s}'], J[f'upperarm.{s}']); B[f'upperarm.{s}'] = (J[f'upperarm.{s}'], J[f'forearm.{s}']); B[f'forearm.{s}'] = (J[f'forearm.{s}'], J[f'hand.{s}'])
            B[f'thigh.{s}'] = (J[f'thigh.{s}'], J[f'shin.{s}']); B[f'shin.{s}'] = (J[f'shin.{s}'], J[f'foot.{s}'])
            for kind, hb, n_ in (('finger', f'hand.{s}', 0.115), ('toe', f'foot.{s}', 0.085)):
                tips = [G(d['tip']) for d in digits[hb]]; wr = J[hb]
                cen = np.mean(tips, 0); cen[1] = 0
                # each digit: from its tip back toward the hand's middle, lying on the ground at the digit's own middle height
                ch = []
                for t in tips:
                    dr = t - (wr * [1, 0, 1] + cen) / 2; dr[1] = 0; dr /= np.linalg.norm(dr); tip = t - dr * 0.025 + [0, 0.045 - t[1], 0]
                    base = tip - dr * n_ * SCALE; ch.append((base, 0.5 * (base + tip), tip))
                # order: the outer / rear digit first (finger0, toe0), the inner / front one last (finger3, toe3)
                key = (lambda c: -m * c[2][0]) if kind == 'finger' else (lambda c: c[2][2])
                ch.sort(key=key); self.dig[hb] = ch
            mid = self.dig[f'hand.{s}'][1]
            B[f'hand.{s}'] = (J[f'hand.{s}'], mid[0])
            for k, ci in ((0, 0), (1, 1), (2, 1), (3, 2)):
                b0, b1, b2 = self.dig[f'hand.{s}'][ci]; B[f'finger{k}.{s}.1'] = (b0, b1); B[f'finger{k}.{s}.2'] = (b1, b2)
            # the foot: the ankle to the ball of the foot (the toes' bases), the toes on along the same line (collinear, as v246)
            tb = np.mean([c[0] for c in self.dig[f'foot.{s}']], 0); tt = np.mean([c[2] for c in self.dig[f'foot.{s}']], 0)
            fd = tb - J[f'foot.{s}']; L1 = np.linalg.norm(fd); fd /= L1; L2 = max(0.04, (tt - tb) @ fd)
            B[f'foot.{s}'] = (J[f'foot.{s}'], J[f'foot.{s}'] + fd * L1); B[f'toes.{s}'] = (J[f'foot.{s}'] + fd * L1, J[f'foot.{s}'] + fd * (L1 + L2))
            for k, ci in ((0, 0), (1, 1), (2, 1), (3, 2)):
                b0, b1, b2 = self.dig[f'foot.{s}'][ci]; B[f'toe{k}.{s}.1'] = (b0, b1); B[f'toe{k}.{s}.2'] = (b1, b2)
            if ears is not None:   # (the ear chain from the ear's own shape: the hinge at its narrow root, the middle of the flap, the tip)
                e = ears[s]; J[f'gill0.{s}.1'], J[f'gill0.{s}.2'], J[f'earTip.{s}'] = e['hinge'], e['mid'], e['tip']
            for k in range(3):
                B[f'gill{k}.{s}.1'] = (J[f'gill0.{s}.1'], J[f'gill0.{s}.2']); B[f'gill{k}.{s}.2'] = (J[f'gill0.{s}.2'], J[f'earTip.{s}'])
        tl = ['tail1', 'tail2', 'tail3', 'tail4', 'tail5', 'tail6', 'tailTip']
        for a, b in zip(tl[:-1], tl[1:]): B[a] = (J[a], J[b])
        self.B = B
    def set_headfront(self, face_c, face_front_z):
        p = np.array([0.0, self.B['head'][0][1] + 0.016, face_front_z - 0.066]); self.B['headfront'] = (p, p + [0, 0, 0.066])
    def frames(self):
        cb = {b['name']: b for b in self.cur['bones']}; F = {}
        for nm, _ in self.order:
            pos, end = self.B[nm]; o = cb[nm]; Fo = dqs.qmat(o['q']); do = np.array(o['end']) - np.array(o['pos']); dn = end - pos
            if nm == 'head': F[nm] = np.eye(3)
            elif nm.startswith('gill'): F[nm] = mkframe(dn, [1.0, 0, 0])
            elif np.linalg.norm(do) < 1e-9 or np.linalg.norm(dn) < 1e-9: F[nm] = Fo
            else: F[nm] = dqs.arc(do, dn) @ Fo
        # the two-bone limbs in the IK's own convention (Puppet.ik2: the hinge X = (root->end) x (the bulge), the upper bone's Z = (sU X) x Y,
        # the lower's (-X) x Y; sU +1 legs, -1 arms), so the rest pose is exactly what the IK makes of the rest contacts (v246's are)
        for s in 'LR':
            for up, lo, en, sU in ((f'thigh.{s}', f'shin.{s}', f'foot.{s}', 1), (f'upperarm.{s}', f'forearm.{s}', f'hand.{s}', -1)):
                a = self.B[up][0]; k = self.B[lo][0]; e = self.B[en][0]; n = (e - a) / np.linalg.norm(e - a); pp = (k - a) - n * ((k - a) @ n); pp /= np.linalg.norm(pp)
                X = np.cross(n, pp); X /= np.linalg.norm(X)
                for b, sg in ((up, sU), (lo, -1)):
                    y = self.B[b][1] - self.B[b][0]; y /= np.linalg.norm(y); z = np.cross(sg * X, y); z /= np.linalg.norm(z); F[b] = np.stack([np.cross(y, z), y, z], 1)
        # the hands and feet level (Y along the ground, Z straight down), Y along the heading of the hand's / foot's own mesh (build.py:
        # flat): planted, the runtime aims each one level along the gait's direction (the left hand's digits' direction, mirrored for the
        # right), so a frame tied to its own mesh lays both hands (feet) the same way, flat on the ground, however Meshy splayed them
        for nm, h in getattr(self, 'flat', {}).items():
            y = np.array([h[0], 0.0, h[2]]); y /= np.linalg.norm(y); z = np.array([0.0, -1.0, 0.0]); F[nm] = np.stack([np.cross(y, z), y, z], 1)
        # digits and toes take their parent's frame (v246: a digit's frame is its hand's / foot's)
        for nm, par in self.order:
            if nm.startswith(('finger', 'toe')) and not nm.startswith('toes'):
                root = nm.split('.')[0][:-1]; side = nm.split('.')[1]; F[nm] = F[('hand.' if nm.startswith('finger') else 'toes.') + side]
            if nm.startswith('toes'): F[nm] = F['foot.' + nm[-1]]
        return F
    def meta_bones(self):
        F = self.frames(); out = []
        for nm, par in self.order:
            pos, end = self.B[nm]; out.append({'name': nm, 'parent': par, 'pos': np.round(pos, 5).tolist(), 'end': np.round(end, 5).tolist(), 'q': np.round(dqs.mat2quat(F[nm]), 6).tolist()})
        return out
