"""v432: the held item button. The Whirlwind's painted tornado was drawn a little larger than its box, so its top was cut off, and
long item names ran past the round button. The picture (whose painted outline was cropped flat at the top: art/it_whirl.webp now has its rounded top) now sits inside its box, and a long name is set smaller and tighter."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = ".itemBtn .ilbl.lng{font-size:8px;letter-spacing:0}@media (max-height:520px) and (min-aspect-ratio:1/1){.itemBtn .ilbl.lng{font-size:7px}}.itemBtn.ib2 .ilbl.lng,.itemBtn.orbBtn .ilbl.lng{font-size:7px;letter-spacing:0}\n"

def apply(s):
    s = rep(s, '<image href="art/it_whirl.webp" x="-2" y="-2" width="44" height="44"/>', '<image href="art/it_whirl.webp" x="2" y="1" width="36" height="36"/>')
    s = rep(s, "'<span class=\"ilbl\">' + PU[h2].name + '</span>'", "'<span class=\"ilbl' + (PU[h2].name.length > 7 ? ' lng' : '') + '\">' + PU[h2].name + '</span>'")
    s = rep(s, "'<span class=\"ilbl\">' + PU[held].name + '</span>'", "'<span class=\"ilbl' + (PU[held].name.length > 7 ? ' lng' : '') + '\">' + PU[held].name + '</span>'")
    i = s.index(".itemBtn.in{animation:slamin"); s = s[:i] + CSS + s[i:]
    return s
