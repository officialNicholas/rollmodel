"""v386: Get dabs' Go ad-free plate at 65% of its v383 size (the user: "make it 35 percent smaller").

- Everything on it is scaled by 0.65: the plate's height, padding and corners, the stamp, the two lines, the sparkles and the light.
- It no longer runs the card's full width: it sits in the middle (the stamp's overhang counted in), as wide as 65% of the card or its
  text, whichever is more ("Thanks for your support" is the longer line once paid)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, ".dsnoads{position:relative;display:flex;align-items:center;min-height:58px;margin:6px 4px 2px 22px;padding:6px 16px 6px 52px;border:3px solid #171320;border-radius:14px;",
               ".dsnoads{position:relative;display:flex;align-items:center;justify-self:center;width:fit-content;min-width:65%;max-width:calc(100% - 17px);box-sizing:border-box;min-height:38px;margin:4px 0 2px 17px;padding:4px 30px 4px 34px;border:2.5px solid #171320;border-radius:9px;")
    s = rep(s, "box-shadow:inset 0 2px 0 rgba(255,255,255,.65),inset 0 -3px 0 rgba(150,90,10,.35),0 4px 0 #171320;rotate:-1.2deg;",
               "box-shadow:inset 0 1px 0 rgba(255,255,255,.65),inset 0 -2px 0 rgba(150,90,10,.35),0 3px 0 #171320;rotate:-1.2deg;")
    s = rep(s, ".dsnoads::before{content:\"\";position:absolute;inset:0;border-radius:11px;", ".dsnoads::before{content:\"\";position:absolute;inset:0;border-radius:7px;")
    s = rep(s, ".dsseal{position:absolute;left:-26px;top:50%;width:70px;height:70px;translate:0 -50%;rotate:-12deg;filter:drop-shadow(0 3px 0 rgba(23,19,32,.9))}",
               ".dsseal{position:absolute;left:-17px;top:50%;width:46px;height:46px;translate:0 -50%;rotate:-12deg;filter:drop-shadow(0 2px 0 rgba(23,19,32,.9))}")
    s = rep(s, ".dsnat small{font:900 11px/1 var(--font-head);letter-spacing:.14em;", ".dsnat small{font:900 7.5px/1 var(--font-head);letter-spacing:.13em;white-space:nowrap;")
    s = rep(s, ".dsnat b{font:400 26px/1.02 var(--font-display);color:#fff;letter-spacing:.01em;text-shadow:0 3px 0 #171320,2px 0 0 #171320,-2px 0 0 #171320,0 -2px 0 #171320,2px 2px 0 #171320,-2px 2px 0 #171320,2px -2px 0 #171320,-2px -2px 0 #171320}",
               ".dsnat b{font:400 17px/1.02 var(--font-display);color:#fff;letter-spacing:.01em;white-space:nowrap;text-shadow:0 2px 0 #171320,1.4px 0 0 #171320,-1.4px 0 0 #171320,0 -1.4px 0 #171320,1.4px 1.4px 0 #171320,-1.4px 1.4px 0 #171320,1.4px -1.4px 0 #171320,-1.4px -1.4px 0 #171320}")
    s = rep(s, ".dsspark{position:absolute;right:16px;top:9px;width:14px;height:14px;", ".dsspark{position:absolute;right:10px;top:6px;width:9px;height:9px;")
    s = rep(s, ".dsspark.b{right:40px;top:auto;bottom:9px;width:9px;height:9px;", ".dsspark.b{right:22px;top:auto;bottom:6px;width:6px;height:6px;")
    # short screens (landscape phones) had their own smaller plate: scaled the same
    s = rep(s, ".dsnoads{min-height:46px;padding-block:3px}.dsseal{width:56px;height:56px;left:-22px}.dsnat b{font-size:21px}",
               ".dsnoads{min-height:30px;padding-block:2px}.dsseal{width:37px;height:37px;left:-14px}.dsnat b{font-size:14px}")
    return s
