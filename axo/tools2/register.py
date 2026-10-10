# register the unrigged stand sculpt onto the rigged one (similarity ICP), then fit the colour map rigged -> unrigged on close pairs
import numpy as np
from scipy.spatial import cKDTree
from PIL import Image
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
r = np.load(D + 'stand_src.npz', allow_pickle=True); u = np.load(D + 'standu_src.npz')
Pr, Pu = r['P'].astype(float), u['P'].astype(float)
# principal axes to guess the rotation; both are upright characters: try the 24 axis permutations/signs that keep y up
def ext(P): return P.max(0) - P.min(0)
print('ext rigged', ext(Pr).round(3), 'ext unrigged', ext(Pu).round(3))
best = None
cr = (Pr.max(0) + Pr.min(0)) / 2; Pr0 = Pr - cr
for perm in ([0, 1, 2], [2, 1, 0], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1]):
    for sx in (1, -1):
        for sy in (1, -1):
            for sz in (1, -1):
                Q = Pu[:, perm] * np.array([sx, sy, sz]); Q = Q - (Q.max(0) + Q.min(0)) / 2
                s = np.linalg.norm(ext(Pr0)) / np.linalg.norm(ext(Q)); Q = Q * s
                d, _ = cKDTree(Q).query(Pr0[::7]); e = np.median(d)
                if best is None or e < best[0]: best = (e, perm, (sx, sy, sz), s)
print('best axis guess', best)
e, perm, sg, s = best; Q = Pu[:, perm] * np.array(sg); Q = (Q - (Q.max(0) + Q.min(0)) / 2) * s
# similarity ICP (Umeyama) on subsampled points
src = Q.copy()
for it in range(40):
    tree = cKDTree(src); d, idx = tree.query(Pr0); keep = d < np.percentile(d, 70)
    A = src[idx[keep]]; B = Pr0[keep]; ma, mb = A.mean(0), B.mean(0); H = (A - ma).T @ (B - mb) / len(A)
    U, Sg, Vt = np.linalg.svd(H); Dm = np.eye(3); Dm[2, 2] = np.sign(np.linalg.det(U @ Vt)); Rm = Vt.T @ Dm @ U.T
    sc = np.trace(np.diag(Sg) @ Dm) / ((A - ma) ** 2).sum() * len(A); t = mb - sc * Rm @ ma
    src = (sc * (Rm @ src.T)).T + t
d, idx = cKDTree(src).query(Pr0); print('after ICP: nearest dist p50/p80/p95', np.percentile(d, [50, 80, 95]).round(4), 'frac<0.01', (d < 0.01).mean().round(3), 'frac<0.02', (d < 0.02).mean().round(3))
np.save(D + 'standu_aligned.npy', src + cr)
def samp(im, uv):
    a = np.asarray(im).astype(np.float32) / 255; h, w = a.shape[:2]; px = np.clip((uv[:, 0] * (w - 1)).round().astype(int), 0, w - 1); py = np.clip((uv[:, 1] * (h - 1)).round().astype(int), 0, h - 1); return a[py, px]
imr = Image.open(D + 'stand_tex.png').convert('RGB'); imu = Image.open(D + 'standu_tex.png').convert('RGB')
cr_ = samp(imr, r['UV']); cu_ = samp(imu, u['UV'])
ok = d < 0.012; A = cr_[ok]; B = cu_[idx[ok]]; print('pairs', ok.sum(), 'rigged mean', A.mean(0).round(3), 'unrigged mean', B.mean(0).round(3))
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def srgb(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)
X = np.c_[A, np.ones(len(A))]; M, *_ = np.linalg.lstsq(X, B, rcond=None); print('srgb affine rms', np.sqrt(((X @ M - B) ** 2).mean()).round(4)); print(M.round(3))
Xl = np.c_[lin(A), np.ones(len(A))]; Ml, *_ = np.linalg.lstsq(Xl, lin(B), rcond=None); pl = srgb(np.clip(Xl @ Ml, 0, 1)); print('lin affine rms', np.sqrt(((pl - B) ** 2).mean()).round(4)); print(Ml.round(3))
# per-channel 1D curves (lookup) : is it a simple per-channel tone curve?
for ch in range(3):
    xs = A[:, ch]; ys = B[:, ch]; bins = np.linspace(0, 1, 21); dig = np.digitize(xs, bins); cur = [(ys[dig == k].mean().round(3) if (dig == k).sum() > 20 else None) for k in range(1, 21)]
    print('ch', ch, cur)
# quadratic polynomial in sRGB with cross terms
def feats(C): return np.c_[C, C ** 2, C[:, [0]] * C[:, [1]], C[:, [1]] * C[:, [2]], C[:, [0]] * C[:, [2]], np.ones(len(C))]
F = feats(A); Mq, *_ = np.linalg.lstsq(F, B, rcond=None); print('quadratic rms', np.sqrt(((F @ Mq - B) ** 2).mean()).round(4))
np.save(D + 'colfit.npy', {'srgb_affine': M, 'lin_affine': Ml, 'quad': Mq}, allow_pickle=True)
