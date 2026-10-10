import numpy as np, colorsys
from PIL import Image
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
s = np.load(D + 'stand_src.npz', allow_pickle=True); P, UV, JN, WT, names = s['P'], s['UV'], s['JN'], s['WT'], list(s['names'])
im = Image.open(D + 'stand_tex.png').convert('RGB'); a = np.asarray(im).astype(np.float32) / 255
px = np.clip((UV[:, 0] * 4095).round().astype(int), 0, 4095); py = np.clip((UV[:, 1] * 4095).round().astype(int), 0, 4095); col = a[py, px]
hsv = np.array([colorsys.rgb_to_hsv(*c) for c in col])
print('colour stats: sat p50/p90', np.percentile(hsv[:, 1], [50, 90]).round(2))
W = np.zeros((len(P), len(names)))
for c in range(4): np.add.at(W, (np.arange(len(P)), JN[:, c]), WT[:, c])
dom = W.argmax(1); LS = names.index('mixamorig:LeftShoulder'); HD = names.index('mixamorig:Head')
for thr in (0.35, 0.45, 0.55):
    red = (hsv[:, 1] > thr) & ((hsv[:, 0] > 0.9) | (hsv[:, 0] < 0.05)) & (P[:, 1] > 1.1)
    print('sat>', thr, 'red high verts', red.sum(), 'of which LeftShoulder-dominant', (red & (dom == LS)).sum(), 'Head-dominant', (red & (dom == HD)).sum(), ' x<0:', (red & (P[:, 0] < 0)).sum(), 'x>0:', (red & (P[:, 0] > 0)).sum())
ls = dom == LS; print('LeftShoulder-dominant: red frac', red[ls].mean().round(2), 'x>0 frac', (P[ls, 0] > 0).mean().round(2), 'y>1.1 frac', (P[ls, 1] > 1.1).mean().round(2))
# how many of the LS-dominant verts are NOT red and where are they
nr = ls & ~red; print('LS-dominant non-red', nr.sum(), 'bbox', P[nr].min(0).round(2), P[nr].max(0).round(2))
# head-dominant verts in the left region (x>0.3)
hl = (dom == HD) & (P[:, 0] > 0.3); print('Head-dominant with x>0.3', hl.sum())
