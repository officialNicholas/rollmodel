# extract the unrigged stand and crawl models (mesh + base texture), compare rigged vs unrigged stand textures via nearest-vertex colour correspondence
import sys, io, numpy as np
from PIL import Image
from scipy.spatial import cKDTree
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo')
import glb
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
U = '/root/.claude/uploads/5c52352e-692f-5301-ac55-ec4d2c708f3e/'
def get(path, nm):
    j, bn = glb.load(path); pr = j['meshes'][0]['primitives'][0]
    P = glb.acc(j, bn, pr['attributes']['POSITION']); N = glb.acc(j, bn, pr['attributes']['NORMAL']); UV = glb.acc(j, bn, pr['attributes']['TEXCOORD_0']); I = glb.acc(j, bn, pr['indices'])
    np.savez(D + nm + '_src.npz', P=P, N=N, UV=UV, I=I)
    im = Image.open(io.BytesIO(glb.image(j, bn, 0))).convert('RGB'); im.save(D + nm + '_tex.png'); print(nm, 'verts', len(P), 'bbox', P.min(0).round(3), P.max(0).round(3), 'tex', im.size)
    return P, UV, im
Pu, UVu, imu = get(U + 'ad5ebce6-Meshy_AI_Axolotl_Under_12k_Mes_1010150411_texture.glb', 'standu')
Pc, UVc, imc = get(U + 'dece5028-Meshy_AI_Axolotl_Crawl_Sub12k__1010171817_texture.glb', 'crawl')
s = np.load(D + 'stand_src.npz', allow_pickle=True); Pr, UVr = s['P'], s['UV']; imr = Image.open(D + 'stand_tex.png').convert('RGB')
def samp(im, uv):
    a = np.asarray(im).astype(np.float32) / 255; h, w = a.shape[:2]; px = np.clip((uv[:, 0] * (w - 1)).round().astype(int), 0, w - 1); py = np.clip((uv[:, 1] * (h - 1)).round().astype(int), 0, h - 1); return a[py, px]
cr, cu = samp(imr, UVr), samp(imu, UVu)
# same shape? compare bboxes & nearest distances
d, idx = cKDTree(Pu).query(Pr); print('rigged->unrigged nearest dist p50/p95/max', np.percentile(d, 50).round(4), np.percentile(d, 95).round(4), d.max().round(4))
# is the UV layout identical? (if so, uv of nearest vertices agree)
print('uv diff of nearest', np.abs(UVr - UVu[idx]).mean().round(4))
ok = d < 0.01; A = cr[ok]; B = cu[idx[ok]]
print('rigged colour mean', A.mean(0).round(3), 'unrigged colour mean', B.mean(0).round(3))
# fit per-channel affine and a 3x3 linear map (in sRGB) from rigged -> unrigged
X = np.c_[A, np.ones(len(A))]; M, *_ = np.linalg.lstsq(X, B, rcond=None); pred = X @ M; print('affine fit rms', np.sqrt(((pred - B) ** 2).mean()).round(4)); print(M.round(3))
# also test the hypothesis base*(1+k) (emissive adds base) in linear space
def lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
def srgb(c): return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)
for k in (0.5, 0.8, 1.0, 1.2):
    pr_ = srgb(np.clip(lin(A) * (1 + k), 0, 1)); print('k', k, 'rms', np.sqrt(((pr_ - B) ** 2).mean()).round(4))
Xl = np.c_[lin(A), np.ones(len(A))]; Ml, *_ = np.linalg.lstsq(Xl, lin(B), rcond=None); print('linear-space affine rms (srgb)', np.sqrt(((srgb(np.clip(Xl @ Ml, 0, 1)) - B) ** 2).mean()).round(4)); print(Ml.round(3))
np.save(D + 'colfit.npy', {'srgb_affine': M, 'lin_affine': Ml}, allow_pickle=True)
