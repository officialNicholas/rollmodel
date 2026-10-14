"""v282: Ol' Bloop's "New game modes!" card in the lobby (v273) loses its paragraph and its Later link: just the title and Show me,
which opens Choose event with the two new modes tagged New. The cards' shared filler hides the paragraph when a card has none."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "function tutCardText(t) { $('tgTitle').innerHTML = t[0]; $('tgText').textContent = t[1];",
               "function tutCardText(t) { $('tgTitle').innerHTML = t[0]; $('tgText').textContent = t[1] || ''; $('tgText').hidden = !t[1];")
    s = rep(s, "tutCardText(['New game <em>modes!</em>', 'Time trial and Showdown are open now. Time trial: paint all you can in 60 seconds and beat your best. Showdown: two hearts each, last one standing wins.', 'Show me', 'Later']);",
               "tutCardText(['New game <em>modes!</em>', '', 'Show me', '']); // (v282: just the news and the button)")
    return s
