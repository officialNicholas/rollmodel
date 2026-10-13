# v250 gallery art, applied by ui190_patch.py: fresh whole-stage photos (no characters) for Palette Island and the Blank Canvas, and the
# Season 1 frame showing the three Spooky SZN stages side by side (the 'All three' art, re-rendered from today's stages, as are the
# season grid's own photos). Each image is a WebP in S/tools/stage/art/<name>.b64 (the 720x495 frames; *_s: the grid's 440x302)
import os, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
ART = S + '/tools/stage/art/'
def apply(s):
    def swap(kind, wrap, sid, name):
        nonlocal s
        p = ART + name + '.b64'
        if not os.path.exists(p): print('  (art: no', name, 'yet, kept)'); return
        b = open(p).read().strip()
        pat = re.compile(r'(<button class="' + kind + r'" type="button" data-s="' + sid + r'"><span class="' + wrap + r'"><img class="art" src="data:image/webp;base64,)([A-Za-z0-9+/=]+)(")')
        m = pat.findall(s); assert len(m) == 1, (kind, sid, len(m))
        s = pat.sub(lambda mm: mm.group(1) + b + mm.group(3), s, count=1)
    for sid in ('island', 'blank', 'season'): swap('world', 'frame', sid, sid)
    for sid in ('crypt', 'cathedral', 'manor', 'season'): swap('stg', 'sfr', sid, sid + '_s')
    return s
