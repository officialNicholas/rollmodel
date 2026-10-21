"""v425: new photos for Blank Canvas and Palette Island (the user's renders), on the canvas vote page's frames. 720x495 WebP, in tools/art."""
import base64, os, re
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'art')

def apply(s):
    for sid in ('island', 'blank'):
        b = base64.b64encode(open(os.path.join(ART, 'v425_%s.webp' % sid), 'rb').read()).decode()
        pat = re.compile(r'(<button class="world" type="button" data-s="' + sid + r'"><span class="frame"><img class="art" src="data:image/webp;base64,)([A-Za-z0-9+/=]+)(")')
        assert len(pat.findall(s)) == 1, sid
        s = pat.sub(lambda m: m.group(1) + b + m.group(3), s, count=1)
    return s
