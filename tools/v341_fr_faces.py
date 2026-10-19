"""v341: the two faces on the Friends and account messages are the drawn ones again.

- The pair of faces over the Friends page's and the account form's messages (Make an account, Can't connect, No friends yet, and the
  online sheet's) became portraits in v331. They're the two drawn axolotl faces again, green and purple. Every other portrait stays."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "const FR_FACES = '<span class=\"ffaces\" aria-hidden=\"true\">' + [['green', 'round'], ['purple', 'sly']].map(([c, e]) => frFace({ c, e })).join('') + '</span>';",
               "const FR_FACES = '<span class=\"ffaces\" aria-hidden=\"true\">' + ['green', 'purple'].map(c => frFaceSvg({ c })).join('') + '</span>'; // (v341: the two drawn faces again, not portraits)")
    return s
