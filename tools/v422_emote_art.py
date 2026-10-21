"""v422: painted art for the four victory emotes and the Whirlwind (the user: "get Ludo to generate some better graphics for these
emotes", and "a more premium logo for whirlwind"). Made with Ludo.ai in the Strokes stickers' style (chunky cartoon, thick ink outline,
flat bright colour), cut out and saved as 256px webp in game/art/:
  em_slam.webp    Slam: a fist slamming down into a red paint splat, impact burst
  em_hearts.webp  Lovestruck: a big heart with two little ones
  em_flip.webp    Backflip: a paint blob mid-flip in a swoosh
  em_spin.webp    Showstopper: a gold star in a spotlight sunburst
  it_whirl.webp   Whirlwind: a pink-magenta paint tornado with motion streaks
The emotes' cards in the Locker show the pictures instead of the drawn icons (the drawn ones stay as the fallback for any emote without
one). The Whirlwind's picture is on the Strokes page (in place of the old red tornado sticker), on the match's item button and on the
pointer to a pick-up (in place of the stacked rings drawn in your paint colour); there it sits in the same 40x40 svg box, so the
buttons' own sizes for their icons still apply. Each path is written out in full so the iOS pack finds the files."""
import re


def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)


EM_ART = """// (v422) the emotes' pictures (Ludo.ai, the Strokes stickers' style)
const EM_ART = { slam: 'art/em_slam.webp', hearts: 'art/em_hearts.webp', flip: 'art/em_flip.webp', spin: 'art/em_spin.webp' };
function emIcon(id) {
  if (EM_ART[id]) return '<img class="emico emart" src="' + EM_ART[id] + '" alt="" draggable="false">';
"""

CSS = """/* (v422) the emotes' pictures on their cards */
.lkcard .emico.emart{width:78%;height:78%;max-height:84%;object-fit:contain;-webkit-user-drag:none;user-select:none;filter:drop-shadow(1px 2px 0 rgba(23,19,32,.18))}
"""


def apply(s):
    # the emotes' cards
    s = rep(s, "function emIcon(id) {\n", EM_ART)
    s = rep(s, ".lkcard .emico{width:74%;height:auto;max-height:84%}\n", ".lkcard .emico{width:74%;height:auto;max-height:84%}\n" + CSS)
    # the Whirlwind: the item button and the pointer to a pick-up...
    a = re.findall(r"ITEM_ICON\.whirl = '<svg viewBox=\"0 0 40 40\" aria-hidden=\"true\">(?:<path d=\"[^\"]*\"/>)+</svg>'; // \(v271\)", s)
    assert len(a) == 1, len(a)
    s = rep(s, a[0], "ITEM_ICON.whirl = '<svg viewBox=\"0 0 40 40\" aria-hidden=\"true\"><image href=\"art/it_whirl.webp\" x=\"-2\" y=\"-2\" width=\"44\" height=\"44\"/></svg>'; // (v422: the painted tornado)")
    # ...and the Strokes page
    a = re.findall(r"ST_IMG\.whirl = 'data:image/webp;base64,[A-Za-z0-9+/=]+';", s)
    assert len(a) == 1, len(a)
    s = rep(s, a[0], "ST_IMG.whirl = 'art/it_whirl.webp'; /* (v422: the painted tornado) */")
    return s
