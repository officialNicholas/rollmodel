"""v277: the Strokes pictures redrawn flat. Every picture on the Strokes page (the Rocket, the Giant, Flash Freeze, Swim faster,
Weather Repel, Deep Pockets, the More soon crate and the start items: Roller, Paint Trap, Turret, Whirlwind) made again with Ludo.ai
in one much simpler style: solid flat colours, a thick dark outline inside a thin cream sticker edge (so they read on the
dark tiles), no gloss, sparkles or splatter. The Giant is now her own face
(Ludo, drawn from the character in the lobby: the round dome head, the long floppy ears, the heavy-lidded eyes and the smirk) with
four arrows pushing out, where it used to be a generic gilled axolotl. The soft blurred shadows under the pictures on the Strokes page
become a hard flat drop to match. The orb button in a match uses the same pictures."""
import base64, os, re
A = os.path.dirname(os.path.abspath(__file__)) + '/assets/'
KEYS = ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets', 'soon', 'roller', 'trap', 'turret']
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def uri(k):
    return 'data:image/webp;base64,' + base64.b64encode(open(A + k + '_flat_256.webp', 'rb').read()).decode()
def apply(s):
    for k in KEYS:
        pat = re.compile(r"\b" + k + r": 'data:image/webp;base64,[A-Za-z0-9+/=]+'")
        assert len(pat.findall(s)) == 1, k
        s = pat.sub(lambda m: k + ": '" + uri(k) + "'", s)
    pat = re.compile(r"ST_IMG\.whirl = 'data:image/[a-z]+;base64,[A-Za-z0-9+/=]+'")
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: "ST_IMG.whirl = '" + uri('whirl') + "'", s)
    # flat pictures sit on a hard drop rather than a soft blur
    s = rep(s, "#mStrokes .stslot .stic .stimg{width:60px;height:60px;object-fit:contain;filter:drop-shadow(0 4px 6px rgba(0,0,0,.45))}",
               "#mStrokes .stslot .stic .stimg{width:60px;height:60px;object-fit:contain;filter:drop-shadow(0 3px 0 rgba(0,0,0,.4))}")
    s = rep(s, "#mStrokes .stopt .stoi .stimg{width:56px;height:56px;object-fit:contain;filter:drop-shadow(0 4px 5px rgba(0,0,0,.45))}",
               "#mStrokes .stopt .stoi .stimg{width:56px;height:56px;object-fit:contain;filter:drop-shadow(0 3px 0 rgba(0,0,0,.4))}")
    s = rep(s, "#mStrokes .stopt.raw .stoi .stimg,#mStrokes .stopt.lock .stoi .stimg{opacity:.92;filter:grayscale(.75) brightness(.78) drop-shadow(0 4px 5px rgba(0,0,0,.45))}",
               "#mStrokes .stopt.raw .stoi .stimg,#mStrokes .stopt.lock .stoi .stimg{opacity:.92;filter:grayscale(.75) brightness(.78) drop-shadow(0 3px 0 rgba(0,0,0,.4))}")
    s = rep(s, "#stPop .stpart .stimg{width:112px;height:112px;filter:drop-shadow(0 8px 10px rgba(0,0,0,.5))}",
               "#stPop .stpart .stimg{width:112px;height:112px;filter:drop-shadow(0 5px 0 rgba(0,0,0,.4))}")
    return s
