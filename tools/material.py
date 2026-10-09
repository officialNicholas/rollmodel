#!/usr/bin/env python3
"""The WET PAINT material kit: paint and paper, photographed, not illustrated. Flat Design for silhouettes, Photorealistic for materials.
Idempotent by request_id and output file."""
import os, subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
ART = S + '/art/mat'; LUDO = S + '/tools/ludo.py'; os.makedirs(ART, exist_ok=True)
V = 'rm6'
def run(name, itype, prompt, style, n=1, ar='default'):
    out = f'{ART}/{name}.png'
    if os.path.exists(out) or os.path.exists(out.replace('.png', '_1.png')): return
    r = subprocess.run(['python3', '-I', LUDO, 'gen', out, itype, prompt, '--style', style, '--n', str(n), '--ar', ar, '--rid', f'{V}-{name}'], capture_output=True, text=True, timeout=900)
    print(f'{name:14} {"ok" if r.returncode == 0 else "FAIL"} {(r.stderr.strip().splitlines() or [""])[-1][:120]}', flush=True)
J = [
 # the roller stroke: real paint, one solid color so it can be tinted (white, so multiply gives any ink)
 ('stroke_wet',  'sprite-vfx', 'a single thick horizontal paint roller stroke of glossy white paint on a transparent background, photographed from straight above, real wet paint texture with roller bristle streaks, a soft specular sheen and three heavy drips hanging from the lower edge, slightly ragged start and end, one solid white color, no outline, no other colors', 'Photorealistic 3D', 3),
 ('splat_wet',   'sprite-vfx', 'a single big splat of glossy white paint seen from straight above, thick wet paint with raised edges, specular highlights and a few flung droplets around it, one solid white color on a transparent background, no outline', 'Photorealistic 3D', 3),
 ('drip_wet',    'sprite-vfx', 'three long drips of glossy white paint running downward from a straight top edge, thick wet paint with rounded bulbs at the bottom, specular highlights, one solid white color on a transparent background, no outline', 'Photorealistic 3D', 2),
 # tape and paper
 ('tape_a',      'ui_asset', 'a strip of real beige masking tape, torn at both ends, slightly translucent with visible paper fiber texture, photographed flat, isolated on a transparent background, no text', 'Photorealistic 3D', 3),
 ('tape_b',      'ui_asset', 'a short strip of real cream washi masking tape torn at both ends, slightly translucent, paper fiber texture, photographed flat, isolated on a transparent background, no text', 'Photorealistic 3D', 2),
 ('paper_tear',  'ui_asset', 'a rectangular piece of thick cream watercolor paper with torn deckled edges on all four sides, subtle grain, photographed flat on a transparent background, no text, no drawing', 'Photorealistic 3D', 2),
 ('sticker_dot', 'ui_asset', 'a single round glossy bright red sticker dot, slightly peeling at one edge with a tiny white highlight, photographed flat, isolated on a transparent background', 'Photorealistic 3D', 2),
 ('frame_mat',   'ui_asset', 'an empty thin black wooden gallery picture frame with a wide white mat inside and an empty center, square, photographed straight on, isolated on a transparent background', 'Photorealistic 3D', 2),
 ('placard',     'ui_asset', 'a small blank white museum wall placard, a rectangular card with slightly rounded corners and a thin shadow, photographed straight on, isolated on a transparent background, no text', 'Photorealistic 3D', 2),
 ('polaroid',    'ui_asset', 'a blank instant photo print, white border with the wide bottom edge, slightly tilted, with a soft shadow, the picture area a plain mid grey, isolated on a transparent background, no text', 'Photorealistic 3D', 2),
 ('clipboard',   'ui_asset', 'a brown hardboard clipboard with a silver metal clip at the top holding a blank sheet of cream paper, photographed straight on, isolated on a transparent background, no text', 'Photorealistic 3D', 2),
 ('nametag',     'ui_asset', 'a blank white hello my name is style adhesive name badge with a red top band and a blank white writing area, photographed flat, isolated on a transparent background, no text', 'Photorealistic 3D', 2),
 # the gallery wall and the studio floor
 ('wall_gallery','fixed_background', 'a dark charcoal gallery wall lit by a single warm spotlight from above, empty, soft vignette, subtle plaster texture, no objects, no people, no text', 'Photorealistic 3D', 2, 'ar_9_16'),
 ('paper_bg',    'texture', 'seamless cream sketchbook paper texture with fine fiber grain and faint light grey grid lines, flat, evenly lit, no drawings', 'Photorealistic 3D', 2),
 ('flecks',      'texture', 'seamless texture of tiny sparse dark red paint speckles and flecks on a plain pure white background, very sparse, flat', 'Flat Design', 1),
]
for j in J: run(*j)
