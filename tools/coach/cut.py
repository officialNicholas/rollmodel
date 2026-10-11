"""the Coach half-body: crop the user's render to head, gills, beard, the raised finger and chest; drop the tail piece and stray specks"""
import sys, numpy as np
from PIL import Image, ImageDraw
src = Image.open(sys.argv[1]).convert('RGBA')
c = src.crop((400, 0, 1237, 780)); a = np.array(c)
solid = (a[:, :, 3] > 10).astype(np.uint8) * 255
# stray specks: any shape under 60 px that isn't joined to the body
lab = np.zeros(solid.shape, np.int32); keep = (a[:, :, 3] > 10); H, W = keep.shape; nxt = 1; sizes = {}
for y in range(H):
    row = keep[y]
    for x in np.nonzero(row & (lab[y] == 0))[0]:
        if lab[y, x]: continue
        st = [(y, x)]; lab[y, x] = nxt; n = 0
        while st:
            py, px = st.pop(); n += 1
            for qy, qx in ((py - 1, px), (py + 1, px), (py, px - 1), (py, px + 1)):
                if 0 <= qy < H and 0 <= qx < W and keep[qy, qx] and not lab[qy, qx]: lab[qy, qx] = nxt; st.append((qy, qx))
        sizes[nxt] = n; nxt += 1
small = [k for k, n in sizes.items() if n < 60]; tail = int(lab[740, 40]); print('shapes', len(sizes), 'small', len(small), 'largest', max(sizes.values()), 'tail', sizes.get(tail))
drop = small + ([tail] if tail and sizes[tail] < 100000 else [])  # the tail: its own shape in the bottom-left corner
if drop: a[np.isin(lab, drop), 3] = 0
out = Image.fromarray(a, 'RGBA'); bb = out.getbbox(); print('bbox', bb)
out.save(sys.argv[2])
w = 640; h = round(out.height * w / out.width); sm = out.resize((w, h), Image.LANCZOS); sm.save(sys.argv[3], 'WEBP', quality=84, alpha_quality=92, method=6); print('webp', sm.size)
