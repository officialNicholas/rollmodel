"""v390: the lesson's Basics Complete screen plays the match's win song (the user), coming in as its fanfare lands. It plays on through
the new items and the tally after it (the tally's own start of the win song carries on from where it is)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "el.classList.add('on'); AU.fanfare(); setTimeout(() => AU.power(), 500); buzz([20, 40, 20]);\n  setTimeout(() => $('twNext').focus",
               "el.classList.add('on'); AU.fanfare(); setTimeout(() => AU.power(), 500); buzz([20, 40, 20]);\n"
               "  setTimeout(() => { if (!el.hidden && el.classList.contains('on')) AU.music('win'); }, 900); // (v390: the win song, as the fanfare lands)\n"
               "  setTimeout(() => $('twNext').focus")
    return s
