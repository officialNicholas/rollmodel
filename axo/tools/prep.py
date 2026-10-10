# normalize both meshes into a shared space: hips over the origin, feet on y=0, crawl scaled up; per-vertex colours for gill detection
import numpy as np, colorsys, sys
from PIL import Image
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/'
CS = 1.25  # crawl scale
mx = np.load(D + 'stand_mixamo.npz'); hips = mx['pos'][0]
TR = {'sn': (1.0, np.array([-hips[0], -0.023, -hips[2]])), 'cn': (CS, None)}
for src, nm in (('stand', 'sn'), ('crawl', 'cn')):
    m = np.load(D + src + '_mesh.npz'); P = m['P'].astype(np.float64); s, t = TR[nm]
    if t is None:
        # crawl: hips guess in the raw mesh at (0.02,-0.2,-0.18)
        t = -np.array([0.02, P.min(0)[1], -0.18])
    P = (P + t) * s
    np.savez(D + nm + '_mesh.npz', P=P.astype(np.float32), N=m['N'], UV=m['UV'], I=m['I'])
    print(nm, 'bbox', P.min(0).round(3), P.max(0).round(3), 'scale', s, 'shift', t.round(3))
    if nm == 'sn':
        jp = (mx['pos'] + t) * s; np.savez(D + 'sn_mixamo.npz', JN=mx['JN'], WT=mx['WT'], pos=jp, names=mx['names'], par=mx['par'])
    im = Image.open(D + f'{src}_1k.png').convert('RGB'); a = np.asarray(im).astype(np.float32) / 255
    sys.path.insert(0, D); from geo import M
    mm = M(nm); uv = mm.UV; px = np.clip((uv[:, 0] * 1023).astype(int), 0, 1023); py = np.clip((uv[:, 1] * 1023).astype(int), 0, 1023)
    col = a[py, px]; cw = np.zeros((len(mm.P), 3)); cnt = np.zeros(len(mm.P)); np.add.at(cw, mm.wid, col); np.add.at(cnt, mm.wid, 1); cw /= cnt[:, None]
    hsv = np.array([colorsys.rgb_to_hsv(*c) for c in cw])
    np.savez(D + nm + '_col.npz', col=cw, hsv=hsv)
    red = (hsv[:, 1] > 0.6) & ((hsv[:, 0] > 0.93) | (hsv[:, 0] < 0.03)) & (cw[:, 1] < 0.42)
    print(nm, 'red verts', red.sum())
