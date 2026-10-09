# side by side: a reference screen above, ours below, three columns (results, picker, locker)
from PIL import Image, ImageDraw
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/'
R = S + 'ref/'; U = S + 'ws/ui/'
pairs = [(R + 'splatoon-2-level-completed.jpg', U + 'v75l_end.png', U + 'v75p_end.png'),
         (R + 'splatoon-2-level-select.jpg', U + 'v75l/06_world.png', U + 'v75p/06_world.png'),
         (R + 'splatoon-2-cloth-shop.jpg', U + 'v75l_look.png', U + 'v75p/05_look.png')]
H = 440; cols = []
for ref, land, port in pairs:
    a = Image.open(ref).convert('RGB'); a = a.resize((int(a.width * H / a.height), H))
    b = Image.open(land).convert('RGB'); b = b.resize((int(b.width * H / b.height), H))
    c = Image.open(port).convert('RGB'); c = c.resize((int(c.width * (2 * H + 16) / c.height), 2 * H + 16))
    w = max(a.width, b.width) + 16 + c.width
    col = Image.new('RGB', (w, 2 * H + 16), (20, 17, 26)); col.paste(a, (0, 0)); col.paste(b, (0, H + 16)); col.paste(c, (max(a.width, b.width) + 16, 0)); cols.append(col)
W = sum(c.width for c in cols) + 24 * (len(cols) - 1)
out = Image.new('RGB', (W, 2 * H + 16), (20, 17, 26)); x = 0
for c in cols: out.paste(c, (x, 0)); x += c.width + 24
out.save('/home/user/rollmodel/sidebyside-v75.jpg', quality=82); print(out.size)
