"""v338: the locker's sheet without the black bar and tape at its top.

- The sheet under the locker's window (My Locker and the Paint Shop) hung from a black rounded bar with a strip of tape across it, as
  the Strokes page's does. The locker's goes, for a cleaner look: only the sheet's own top edge is left. The Strokes page keeps its bar."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, '<section class="sgpanel" id="lkPanel" aria-labelledby="lkPanH"><i class="sghang" aria-hidden="true"></i>',
               '<section class="sgpanel" id="lkPanel" aria-labelledby="lkPanH">')
    s = rep(s, ':is(#mStrokes,#mLocker).sgp .sghang{', '#mStrokes.sgp .sghang{')
    s = rep(s, ':is(#mStrokes,#mLocker).sgp .sghang::after{', '#mStrokes.sgp .sghang::after{')
    return s
