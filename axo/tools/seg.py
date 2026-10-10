import numpy as np, sys, colorsys
from PIL import Image
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo')
from geo import M, D
for nm in ('stand', 'crawl'):
    im = Image.open(D + f'{nm}_tex0.png').convert('RGB'); sm = im.resize((1024, 1024), Image.LANCZOS); sm.save(D + f'{nm}_1k.png'); sm.save(D + f'{nm}_1k.webp', quality=88)
    a = np.asarray(sm).astype(np.float32) / 255; m = M(nm)
    uv = m.UV; px = np.clip((uv[:, 0] * 1023).astype(int), 0, 1023); py = np.clip((uv[:, 1] * 1023).astype(int), 0, 1023)  # (glTF uv: v down from top)
    col = a[py, px]; cw = np.zeros((len(m.P), 3)); cnt = np.zeros(len(m.P)); np.add.at(cw, m.wid, col); np.add.at(cnt, m.wid, 1); cw /= cnt[:, None]
    hsv = np.array([colorsys.rgb_to_hsv(*c) for c in cw]); h, s_, v = hsv[:, 0], hsv[:, 1], hsv[:, 2]
    gill = (s_ > 0.62) & ((h > 0.93) | (h < 0.03)) & (v > 0.45)
    np.savez(D + nm + '_col.npz', col=cw, hsv=hsv, gill=gill)
    print(nm, 'gill verts', gill.sum(), 'of', len(m.P), 'gill bbox', m.P[gill].min(0).round(2), m.P[gill].max(0).round(2))
    print(nm, 'sample sat/hue: belly', np.round(hsv[m.near((0.2, -0.3, 0.45) if nm == 'stand' else (-0.2, -0.33, 0.3))], 2), 'body', np.round(hsv[m.near((0.2, -0.3, -0.05) if nm == 'stand' else (0.0, -0.08, 0.0))], 2))
