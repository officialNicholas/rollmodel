"""v253: the Strokes page's pictures painted (Ludo.ai, in the game's own glossy icon style, backgrounds cut away): the Rocket, the Giant
(a happy axolotl swelling up between four arrows), Flash Freeze, Swim faster, Weather Repel, Deep Pockets and the More soon crate, in
place of the line drawings. The saved orb's button in a match shows the same pictures."""
import base64, os
A = os.path.dirname(os.path.abspath(__file__)) + '/assets/'
def apply(s):
    def rep(old, new, count=1):
        nonlocal s
        c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:100]!r}'
        s = s.replace(old, new)
    img = {k: 'data:image/webp;base64,' + base64.b64encode(open(A + k + '_256.webp', 'rb').read()).decode() for k in ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets', 'soon']}
    js = ("\n// (v253) the stroke pictures, painted (Ludo.ai, in the game's icon style) in place of the line drawings\n"
          "const ST_IMG = { " + ", ".join(f"{k}: '{v}'" for k, v in img.items()) + " }, stImg = k => '<img class=\"stimg\" src=\"' + ST_IMG[k] + '\" alt=\"\" draggable=\"false\">';\n"
          "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets']) STROKE_ICON[k] = stImg(k);\n")
    rep("stroke=\"#171320\" stroke-width=\"3\"/></svg>' });", "stroke=\"#171320\" stroke-width=\"3\"/></svg>' });" + js)
    rep('<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="20" fill="none" stroke="#8A8396" stroke-width="4" stroke-dasharray="7 7"/></svg>', "' + stImg('soon') + '", count=2)
    rep(".stic svg{width:52px;height:52px}", ".stic svg{width:52px;height:52px}.stic .stimg{width:62px;height:62px;object-fit:contain}")
    rep(".stopt svg{width:38px;height:38px}", ".stopt svg{width:38px;height:38px}.stopt .stimg{width:48px;height:48px;object-fit:contain;-webkit-user-drag:none;user-select:none}.stopt.soon .stimg{filter:grayscale(.9);opacity:.45}.stopt.lock .stimg{opacity:.45;filter:grayscale(1)}")
    rep(".orbBtn svg{width:30px;height:30px;margin-top:-10px}", ".orbBtn svg{width:30px;height:30px;margin-top:-10px}.orbBtn .stimg{position:relative;z-index:1;width:38px;height:38px;margin-top:-12px;object-fit:contain;filter:drop-shadow(0 2px 0 rgba(0,0,0,.25))}")
    return s
