# close and far crops of the last skinshot run, one sheet: front 3/4, back 3/4 (close), the far view and the gameplay view (zoomed)
import sys
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
tag = sys.argv[1]
a = Image.open(SP + 'rx/_k_front.png'); b = Image.open(SP + 'rx/_k_back.png'); c = Image.open(SP + 'rx/_k_far.png'); d = Image.open(SP + 'rx/_k_island_play.png')
W, H = a.size
fr = a.crop((0, int(H * 0.25), W, int(H * 0.85))); bk = b.crop((0, int(H * 0.25), W, int(H * 0.85)))
far = c.crop((int(W * 0.25), int(H * 0.4), int(W * 0.75), int(H * 0.6))).resize((W, int(W * 0.2 * H / (0.5 * W))))
ply = d.crop((int(W * 0.35), int(H * 0.6), int(W * 0.85), int(H * 0.82))).resize((W, int(W * 0.22 * H / (0.5 * W))))
s = Image.new('RGB', (W * 2, fr.size[1] + max(far.size[1], ply.size[1])), (16, 12, 24))
s.paste(fr, (0, 0)); s.paste(bk, (W, 0)); s.paste(far, (0, fr.size[1])); s.paste(ply, (W, fr.size[1]))
s.save(SP + 'rx/%s_crops.png' % tag); print(s.size)
