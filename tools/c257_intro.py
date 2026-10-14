#!/usr/bin/env python3
"""v257 intro: the screenshot composites (intro-v257-*.jpg at the repo root) from a p257_intro.py run. Usage: c257_intro.py <run dir>"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
D = sys.argv[1]; ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def font(sz):
    for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf']:
        if os.path.exists(f): return ImageFont.truetype(f, sz)
    return ImageFont.load_default()
def comp(name, items, cols, scale, title):
    ims = [(lab, Image.open(os.path.join(D, f)).convert('RGB')) for f, lab in items if os.path.exists(os.path.join(D, f))]
    w, h = ims[0][1].size; W, H = int(w * scale), int(h * scale); pad, head, cap = 14, 56, 30; rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (pad + cols * (W + pad), head + rows * (H + cap + pad)), (23, 19, 32)); d = ImageDraw.Draw(S)
    d.text((pad, 16), title, fill=(244, 238, 227), font=font(24))
    for i, (lab, im) in enumerate(ims):
        x, y = pad + (i % cols) * (W + pad), head + (i // cols) * (H + cap + pad)
        d.text((x, y + 4), f'{i + 1}. {lab}', fill=(242, 193, 78), font=font(15)); S.paste(im.resize((W, H), Image.LANCZOS), (x, y + cap))
    out = os.path.join(ROOT, name); S.save(out, quality=86); print(out, S.size, os.path.getsize(out))
P = [('a0_sky', 'Stars over the canyon'), ('a1_title', 'A Marcelin Game'), ('a2_pan', 'The pan down'), ('a_barrel', 'Down on the drum'), ('a3_thump', 'A thump inside'), ('b_wobble', 'It rocks'), ('c_tip', 'Over it goes'), ('d_pour', 'It pours'), ('f_eyes', 'Eyes pop up'),
     ('g_look', 'A look round'), ('h_iris', 'Eye color'), ('h2_blue', 'Live on the face'), ('i_style', 'Eye style'), ('j_paintcard', 'The paint'), ('k_purple', 'Puddle and all'),
     ('l_rise', 'It rises'), ('m_jump', 'Jumps clear'), ('o_shake', 'Shakes it off'), ('p_namecard', 'Name it'), ('p2_confirm', 'All set?'), ('q_wink', 'A wink, the send-off'),
     ('s_reveal', 'The iris opens'), ('t_jumpin', 'It jumps in'), ('v_coach', 'The lesson starts')]
comp('intro-v257-portrait.jpg', [(f'port_inset_{k}.png', l) for k, l in P], 8, 0.5, 'v257 first launch, portrait 390x780 (app insets: top 59, bottom 34)')
comp('intro-v257-landscape.jpg', [(f'land_inset_{k}.png', l) for k, l in P], 6, 0.5, 'v257 first launch, landscape 780x390 (app insets: top 59, bottom 34)')
comp('intro-v257-cards.jpg', [('port_inset_h2_blue.png', 'Eye color'), ('port_inset_i_style.png', 'Eye style'), ('port_inset_k_purple.png', 'Paint'), ('port_inset_p_namecard.png', 'Name'), ('port_inset_p2_confirm.png', 'All set?'), ('port_inset_q_wink.png', 'Send-off')], 6, 0.6, 'v257 first launch: the cards, portrait')
comp('intro-v257-cards-wide.jpg', [('land_inset_h2_blue.png', 'Eye color'), ('land_inset_i_style.png', 'Eye style'), ('land_inset_k_purple.png', 'Paint'), ('land_inset_p_namecard.png', 'Name'), ('land_inset_p2_confirm.png', 'All set?'), ('land_inset_q_wink.png', 'Send-off')], 3, 0.6, 'v257 first launch: the cards, landscape')
