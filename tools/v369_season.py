"""v369: no carousel arrows on a season's page.

- The canvas carousel's arrows (previous and next) stayed on screen over a season's page (Spooky SZN: The Crypt, The Cathedral, The
  Manor, All three), sitting on the corners of the top two pictures. There they still worked the carousel hidden behind the page: the
  left one quietly picked the canvas before the season (Fishing Raft), so nothing on the page was picked any more, and the right one
  did nothing. The page shows all its canvases at once and has its own way back, so the arrows go while it's open (the arrow keys too)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, ".mworld.sopen .gallery,.mworld.sopen .gdots{display:none}",
               ".mworld.sopen .gallery,.mworld.sopen .gdots{display:none}\n"
               "/* (v369) nor the carousel's arrows over a season's page: it shows all its canvases at once */\n"
               ".mworld.sopen .gnav{display:none}")
    s = rep(s, "function stepWorld(dir) { const open = worldBtns",
               "// (v369) not while a season's page is open: the carousel is hidden behind it\n"
               "function stepWorld(dir) { if (seasonOpen()) return; const open = worldBtns")
    return s
