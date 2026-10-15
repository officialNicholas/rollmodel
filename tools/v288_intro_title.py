"""v288: the first launch's title, A Marcelin Game, sits nearer the middle of the screen over the night sky (its middle at 44% of the
screen's height, just above centre) instead of high up near the top. Same line, same timing and animation. A patch over the intro
(tools/v257_intro.js)."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, ".fltitle{position:absolute;left:0;right:0;top:calc(max(64px,calc(env(safe-area-inset-top) + 16px)) + 18%);",
               ".fltitle{position:absolute;left:0;right:0;top:max(44%,calc(env(safe-area-inset-top) + 40px));transform:translateY(-50%);")
    return s
