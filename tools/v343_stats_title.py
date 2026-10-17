"""v343: the Stats card's rank title shows again (it said "Unknown").

- The Stats card's title by your rank badge (Fresh Paint, Drip Rookie, Splat Kid ...) and the Strokes page's hidden heading had the
  same id, and the page's came first, so the rank's name went to that heading and the card kept "Unknown". The card's has its own id
  now, and the Strokes page's heading keeps saying Strokes."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, '<span class="strt"><b id="stTitle">Unknown</b>', '<span class="strt"><b id="stRankName">Fresh Paint</b>')
    s = rep(s, "$('stTitle').textContent = r.name;", "$('stRankName').textContent = r.name; /* (v343: its own id, the Strokes page has stTitle) */")
    return s
