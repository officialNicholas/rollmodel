"""v407: the grey paint's swatch in the locker could hardly be seen on the paper (the user: "The grey color is kind of hard to see"):
its splat is drawn a few shades deeper (a soft violet grey, still plainly the pale one) with a slightly firmer shadow, so it reads like
the others. The paint itself is unchanged. (A drawn rim came out jagged round the splat's edge.)"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    a = '.sw[aria-pressed="true"]{transform:scale(1.28)}'
    return rep(s, a, a + '\n.sw[data-c="grey"] i{background:#BEB5D3;filter:drop-shadow(1px 2px 0 rgba(23,19,32,.38))} /* (v407: the pale pearl, deeper so it shows on the paper) */')
