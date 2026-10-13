# Rotations and dual quaternion skinning helpers (numpy).
import numpy as np
def qmat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
def mat2quat(M):
    t = np.trace(M)
    if t > 0: s = np.sqrt(t + 1) * 2; q = np.array([(M[2, 1] - M[1, 2]) / s, (M[0, 2] - M[2, 0]) / s, (M[1, 0] - M[0, 1]) / s, 0.25 * s])
    else:
        i = int(np.argmax(np.diag(M)))
        if i == 0: s = np.sqrt(1 + M[0, 0] - M[1, 1] - M[2, 2]) * 2; q = np.array([0.25 * s, (M[0, 1] + M[1, 0]) / s, (M[0, 2] + M[2, 0]) / s, (M[2, 1] - M[1, 2]) / s])
        elif i == 1: s = np.sqrt(1 + M[1, 1] - M[0, 0] - M[2, 2]) * 2; q = np.array([(M[0, 1] + M[1, 0]) / s, 0.25 * s, (M[1, 2] + M[2, 1]) / s, (M[0, 2] - M[2, 0]) / s])
        else: s = np.sqrt(1 + M[2, 2] - M[0, 0] - M[1, 1]) * 2; q = np.array([(M[0, 2] + M[2, 0]) / s, (M[1, 2] + M[2, 1]) / s, 0.25 * s, (M[1, 0] - M[0, 1]) / s])
    return q / np.linalg.norm(q)
def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return np.array([aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx, aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz])
def qinv(q): return np.array([-q[0], -q[1], -q[2], q[3]])
def qrot(q, v):
    u = q[..., :3]; w = q[..., 3:4]; return v + 2 * np.cross(u, np.cross(u, v) + w * v)
def arc(a, b):
    """the shortest rotation (matrix) taking direction a to direction b"""
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = float(a @ b)
    if c < -0.999999:
        ax = np.cross(a, [1, 0, 0]); ax = ax if np.linalg.norm(ax) > 1e-6 else np.cross(a, [0, 1, 0]); ax /= np.linalg.norm(ax); return 2 * np.outer(ax, ax) - np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]); return np.eye(3) + K + K @ K / (1 + c)
def frame(y, zref):
    """a bone frame: Y along y, Z toward zref (made square to y), X = Y x Z; as a rotation matrix (columns X, Y, Z)"""
    y = y / np.linalg.norm(y); z = zref - y * (zref @ y)
    if np.linalg.norm(z) < 1e-6: z = np.cross(y, [1.0, 0, 0])
    z /= np.linalg.norm(z); x = np.cross(y, z); return np.stack([x, y, z], 1)
def dqs_deform(P, W, Rs, ts, N=None):
    """blend per-bone rigid maps p -> R p + t by dual quaternions with weights W (n x nb); returns the new positions (and normals)"""
    q = np.array([mat2quat(R) for R in Rs]); t = np.asarray(ts, float)
    d = np.stack([0.5 * (q[:, 3] * t[:, 0] + t[:, 1] * q[:, 2] - t[:, 2] * q[:, 1]), 0.5 * (q[:, 3] * t[:, 1] + t[:, 2] * q[:, 0] - t[:, 0] * q[:, 2]),
                  0.5 * (q[:, 3] * t[:, 2] + t[:, 0] * q[:, 1] - t[:, 1] * q[:, 0]), -0.5 * (t * q[:, :3]).sum(1)], 1)
    dom = np.argmax(W, 1); sgn = np.sign((q[None, :, :] * q[dom][:, None, :]).sum(2)); sgn[sgn == 0] = 1
    Wq = W * sgn; br = Wq @ q; bd = Wq @ d; l = np.linalg.norm(br, axis=1, keepdims=True); br /= l; bd /= l
    Pr = qrot(br, P) + 2 * (br[:, 3:4] * bd[:, :3] - bd[:, 3:4] * br[:, :3] + np.cross(br[:, :3], bd[:, :3]))
    return (Pr, qrot(br, N)) if N is not None else Pr
def rigid_fit(A, B, w=None):
    """least-squares rotation R and translation t with R A + t ~ B (Kabsch)"""
    w = np.ones(len(A)) if w is None else w; ca = (A * w[:, None]).sum(0) / w.sum(); cb = (B * w[:, None]).sum(0) / w.sum()
    H = ((A - ca) * w[:, None]).T @ (B - cb); U, s, Vt = np.linalg.svd(H); D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T; return R, cb - R @ ca
def icp(A, B, iters=30):
    """rigid R, t taking point set A onto point set B (nearest neighbours, both ways)"""
    from scipy.spatial import cKDTree
    tb = cKDTree(B); R = np.eye(3); t = B.mean(0) - A.mean(0)
    for _ in range(iters):
        X = A @ R.T + t; _, j = tb.query(X); ta = cKDTree(X); _, i = ta.query(B)
        src = np.r_[A, A[i]]; dst = np.r_[B[j], B]; R, t = rigid_fit(src, dst)
    X = A @ R.T + t; d, _ = tb.query(X); return R, t, float(np.sqrt((d ** 2).mean()))
def rot_power(R, k):
    """R^k for a rotation matrix (k a fraction), through its axis and angle"""
    q = mat2quat(R); ang = 2 * np.arccos(np.clip(q[3], -1, 1)); s = np.sqrt(max(1 - q[3] ** 2, 1e-16)); ax = q[:3] / s if s > 1e-8 else np.array([1.0, 0, 0])
    a = ang * k; return qmat(np.r_[ax * np.sin(a / 2), np.cos(a / 2)])
