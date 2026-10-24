"""v472: the results bar, polished. The user: "Make this bar more polished".

- The paint now sits in a glass tube: a heavier ink frame with a thin light rim round it, a darker recessed inside (a soft shadow
  along the top edge, so the paint reads as sitting in a channel), a lifted drop shadow under the bar, and a curved glass highlight
  across the top half that catches over the paint. A faint dashed line marks halfway, so who's ahead reads at a glance.
- The liquid paint itself (its sloshing edges, surface, drops) is unchanged.
"""

CSS = """
/* (v472) the results bar as a glass tube of paint */
#end .jbar{border:3px solid #120E1A;border-radius:12px;background:linear-gradient(180deg,#120E19 0%,#221B2F 55%,#1A1425 100%);
  box-shadow:0 0 0 2px rgba(255,255,255,.16),0 5px 0 #0B0811,0 10px 18px rgba(0,0,0,.45),inset 0 5px 10px rgba(0,0,0,.7),inset 0 -2px 0 rgba(255,255,255,.06)}
#end .jbar::after{left:7px;right:7px;top:3px;height:42%;border-radius:9px 9px 16px 16px / 9px 9px 7px 7px;background:linear-gradient(180deg,rgba(255,255,255,.36) 0,rgba(255,255,255,.08) 70%,rgba(255,255,255,0) 100%);opacity:1;mix-blend-mode:normal;z-index:2}
#end .jbar::before{content:"";position:absolute;left:50%;top:3px;bottom:3px;width:0;border-left:2px dashed rgba(255,255,255,.38);z-index:2;pointer-events:none}
"""

def apply(s):
    i = s.rfind("</style>"); return s[:i] + CSS + s[i:]
