"""v411: no "The Paint Shop has N" lines in My Locker (the user: "Remove these, the paint shop has six or has three more messages,
it's cluttering up the space. We don't need to know that"). Under Emotes the "has N more" link goes; a category you own nothing in
(Skins, Headgear, Facial, Clothing) isn't shown at all, rather than a heading over "Nothing here yet". The old look panel's empty line
loses its count too."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, " + (sale ? '<p class=\"lknone\"><button class=\"lkgo\" type=\"button\" data-go=\"shop\" data-f=\"emote\">The Paint Shop has ' + sale + ' more</button></p>' : ''); }",
               "; } // (v411: no 'the Paint Shop has' line)")
    s = rep(s, "    h += '<p class=\"lksec\">' + LK_CAT[c] + (mine.length ? '<i>' + mine.length + '</i>' : '') + '</p>' + (mine.length ? grid(mine.map(w => lkCard(w, 'mine')).join('')) : '<p class=\"lknone\">Nothing here yet.' + (sale ? ' <button class=\"lkgo\" type=\"button\" data-go=\"shop\" data-f=\"' + c + '\">The Paint Shop has ' + sale + '</button>' : '') + '</p>'); }",
               "    if (mine.length) h += '<p class=\"lksec\">' + LK_CAT[c] + '<i>' + mine.length + '</i></p>' + grid(mine.map(w => lkCard(w, 'mine')).join('')); } // (v411: a category you own nothing in isn't shown)")
    s = rep(s, "'<p class=\"lnone\">Nothing here yet. The Paint Shop has ' + forSale + ' to buy.</p>'", "'<p class=\"lnone\">Nothing here yet.</p>'")
    return s
