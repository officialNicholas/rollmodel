"""v397: the locker page's + (get dabs) sits on the top-left corner of the dabs counter (the user: "Move the plus icon to the
top left corner of the 25 dabs icon. instead of the name container"). It was just left of the counter, over the end of the
name's banner in portrait. It is a size smaller there, a corner badge."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v397) the locker's + on the counter's top-left corner, a size smaller, with a bigger place to tap */
.dplus.lk{width:28px;height:28px;border-radius:8px}.dplus.lk svg{width:15px;height:15px}
.dplus.lk::after{content:"";position:absolute;inset:-8px}
"""

def apply(s):
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    s = rep(s, "b.style.left = (cr.left - pr.left - 36).toFixed(0) + 'px'; /* (just left of the counter, which sits in the page's corner) */ b.style.top = (cr.top - pr.top + (cr.height - 30) / 2).toFixed(0) + 'px';",
               "const ir = ($('lkCoinI') || c).getBoundingClientRect(); b.style.left = (Math.min(cr.left - 17, ir.left - 32) - pr.left).toFixed(0) + 'px'; /* (v397: on the counter's top-left corner, off the name's banner, clear of the coin) */ b.style.top = (cr.top - pr.top - 11).toFixed(0) + 'px';")
    return s
