# side by side: reference crops on top, lab views below (python3 gen/labcmp.py lab.png out.png)
import sys
from PIL import Image
lab = Image.open(sys.argv[1]).convert('RGB'); out = sys.argv[2]
R = 'lab/ref/'
refs = [Image.open(R + k + '.png') for k in ('front', 'q34', 'side', 'back')]
W = 1536 / 4.6; H = 1024 * 0.42
tiles = [lab.crop((int(i * W), 0, int((i + 1) * W), int(H))) for i in range(4)]
th = 330
def fit(im): return im.resize((int(im.width * th / im.height), th))
row1 = [fit(r) for r in refs]; row2 = [fit(t) for t in tiles]
w = max(sum(i.width for i in row1), sum(i.width for i in row2))
c = Image.new('RGB', (w, th * 2), (30, 30, 35)); x = 0
for i in row1: c.paste(i, (x, 0)); x += i.width
x = 0
for i in row2: c.paste(i, (x, th)); x += i.width
c.save(out)
