"""v256 screenshot sheets for the repo. usage: sheet256.py OUTDIR"""
import sys
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'; A = S + '/a254'; OUT = sys.argv[1]
def font(sz):
    for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf']:
        try: return ImageFont.truetype(f, sz)
        except Exception: pass
    return ImageFont.load_default()
F = font(17); BG = (23, 19, 32); TX = (255, 246, 216)
def row(items, path):
    W, H = 390, 780; gap = 14; cap = 34
    im = Image.new('RGB', (len(items) * (W + gap) + gap, H + cap + gap * 2), BG); d = ImageDraw.Draw(im)
    for i, (f, t) in enumerate(items):
        x = gap + i * (W + gap); im.paste(Image.open(A + '/' + f).convert('RGB').resize((W, H)), (x, gap))
        tw = d.textlength(t, font=F); d.text((x + (W - tw) / 2, gap + H + 8), t, fill=TX, font=F)
    im.save(path, quality=86); print(path, im.size)
def stack(items, path, W=780):
    parts = []
    for f, css_h, t in items:
        im = Image.open(A + '/' + f).convert('RGB'); k = im.size[0] / (390 if im.size[0] in (390, 780) else 320)
        k = im.size[0] / (390 if '_narrow' not in f else 320)
        c = im.crop((0, 0, im.size[0], int(css_h * k))); c = c.resize((int(c.size[0] * W / (390 * k)) if '_narrow' in f else W, int(c.size[1] * W / (390 * k))))
        parts.append((c, t))
    H = sum(c.size[1] + 40 for c, _ in parts) + 14
    out = Image.new('RGB', (W + 28, H), BG); d = ImageDraw.Draw(out); y = 14
    for c, t in parts:
        d.text((14, y), t, fill=TX, font=F); y += 26; out.paste(c, (14 + (W - c.size[0]) // 2, y)); y += c.size[1] + 14
    out.save(path, quality=88); print(path, out.size)
row([('t2_play_frozen.png', 'Frozen 5 s: tap fast to break out'), ('t2_play_orb4s.png', 'Orb in the slot, 10 s clock'),
     ('t2_play_trap.png', 'Paint Trap: darker, bigger'), ('t4_zone2_curtain.png', 'Showdown: the zone closing in'),
     ('ev256_events.png', 'Solo is now Time trial')], OUT + '/freeze-orb-zone-v256.jpg')
stack([('t2_duo_hud.png', 118, 'Showdown top bar before'), ('k1_duo_red.png', 70, 'After, 2v2: the time in the middle, your teammate in your colour'),
       ('h1_ffa_zone.png', 104, 'Free-for-all, a fighter out, the zone warning under the bar'), ('h2_narrow_hurt.png', 64, 'A 320-wide phone'),
       ('c256_duel_hud.png', 92, 'Duel: the rival score in the rival\'s own colour')], OUT + '/showdown-bar-v256.jpg')
