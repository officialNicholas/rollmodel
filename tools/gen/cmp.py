import sys
from PIL import Image
tag = sys.argv[1]
ims = [Image.open('char/ref_orange.png'), Image.open(f'char/{tag}_orange-round-None-None_hero0.png'), Image.open(f'char/{tag}_orange-round-None-None_hero1.png'),
       Image.open('char/ref_red.png'), Image.open(f'char/{tag}_red-round-None-wings_hero0.png'), Image.open(f'char/{tag}_purple-happy-hat-None_hero0.png')]
th = 480; ims = [im.convert('RGB').resize((int(im.size[0] * th / im.size[1]), th)) for im in ims]
rows = [ims[:3], ims[3:]]; w = max(sum(i.size[0] for i in r) + 12 for r in rows)
o = Image.new('RGB', (w, th * 2 + 6), (14, 14, 14)); y = 0
for r in rows:
    x = 0
    for im in r: o.paste(im, (x, y)); x += im.size[0] + 6
    y += th + 6
o.save(f'char/{tag}_compare.png')
