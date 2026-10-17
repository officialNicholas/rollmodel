"""v334: the lobby's Friends button keeps its three drawn faces (the red, the blue and the purple axolotl heads it was made with); v331
had swapped them for portraits. Only that button: everywhere else the portraits stay."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "// (v331) the lobby's Friends button: three portraits for its three drawn faces\n"
               "{ const ff = document.querySelector('#friendsBtn .ffaces'); if (ff) { const fb = [...ff.children].map(e => e.outerHTML); ff.innerHTML = [[0xE3122F, 'round'], [0x2479D6, 'dot'], [0x7A4FE0, 'sly']].map(([h, e], i) => ptHtml(ptSpec(h, { eyes: e }), 'ffc', fb[i] || '')).join(''); } }\n",
               "// (v334) the lobby's Friends button keeps its three drawn faces (v331 had put portraits there)\n")
    return s
