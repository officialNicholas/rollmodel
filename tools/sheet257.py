"""v257 screenshot sheets for the repo. usage: sheet257.py OUTDIR"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'; A = S + '/a257s'; OUT = sys.argv[1]
def font(sz):
    for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf']:
        try: return ImageFont.truetype(f, sz)
        except Exception: pass
    return ImageFont.load_default()
F = font(17); BG = (23, 19, 32); TX = (255, 246, 216)
def row(items, path, W=390, H=780):
    items = [(f, t) for f, t in items if os.path.exists(A + '/' + f)]; gap = 14; cap = 34
    im = Image.new('RGB', (len(items) * (W + gap) + gap, H + cap + gap * 2), BG); d = ImageDraw.Draw(im)
    for i, (f, t) in enumerate(items):
        x = gap + i * (W + gap); im.paste(Image.open(A + '/' + f).convert('RGB').resize((W, H)), (x, gap))
        tw = d.textlength(t, font=F); d.text((x + (W - tw) / 2, gap + H + 8), t, fill=TX, font=F)
    im.save(path, quality=86); print(path, im.size)
row([('s1_port_page.png', 'The page: only Equipped on tiles'), ('s1_port_pop_raw.png', 'Tap a skill: its card, Craft, Equip'),
     ('s1_port_pop_crafting.png', 'Crafting: countdown and Skip'), ('s1_port_pop_ready.png', 'Crafted: Equip is on'),
     ('s1_port_pop_special.png', 'Special strokes too')], OUT + '/skills-v257.jpg')
row([('s2_land_page.png', 'Wide: the page'), ('s2_land_pop_raw.png', 'Wide: a skill card')], OUT + '/skills-wide-v257.jpg', W=780, H=390)
row([('s4_lesson_giant.png', 'Lesson: tap the Giant'), ('s4_lesson_craft.png', 'Tap Craft'), ('s4_lesson_skip.png', 'Skip, on Bloop'),
     ('s4_lesson_equip.png', 'Tap Equip'), ('s4_lesson_done.png', 'Giant it is')], OUT + '/skills-lesson-v257.jpg')
row([('k257_locked.png', 'Below rank 2: locked'), ('k257_open.png', 'Rank 2: open, marked New')], OUT + '/events-rank2-v257.jpg')
