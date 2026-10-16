"""v323: a stroke card's lime strip says what matters.

The two little trait icons on each card's strip are gone. The strip now says:
- the craft time ("10 min") on a stroke still to craft (it was a pill over the picture),
- the countdown while it's on the bench (the thin progress bar stays along the picture's foot),
- "Equipped" on the one you have on,
- and nothing otherwise: yours but not on, or locked (the lock and its rank stay on the picture).
The strip keeps its height, so the cards still line up."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the picture loses the craft-time pill (the bench keeps its progress bar); the strip gets the words
    s = rep(s, """  const tag = cr ? '<span class="sgst cr">' + ST_GLASS + '<b>' + mmss(craftLeft()) + '</b></span><i class="sgpb"><i></i></i>' : lock ? '<span class="sgst lk">' + STROKE_LOCK + 'Rank ' + stRank(o) + '</span>' : !own ? '<span class="sgst raw">' + ST_GLASS + o.craft + ' min</span>' : '';""",
        """  const tag = cr ? '<i class="sgpb"><i></i></i>' : lock ? '<span class="sgst lk">' + STROKE_LOCK + 'Rank ' + stRank(o) + '</span>' : '';
  // (v323) the strip: Equipped, the craft time, the bench's countdown, or nothing
  const foot = on ? 'Equipped' : cr ? '<b>' + mmss(craftLeft()) + '</b>' : !own && !lock ? o.craft + ' min' : '';""")
    s = rep(s, """'</span><span class="sgcf" aria-hidden="true">' + sgTraits(o.id) + '</span>'""", """'</span><span class="sgcf" aria-hidden="true">' + foot + '</span>'""")
    # the countdown ticks in the strip now
    s = rep(s, "const b = el.querySelector('.sgst b'); if (b) b.textContent = t;", "const b = el.querySelector('.sgcf b'); if (b) b.textContent = t;")
    # the icons' tables go with them
    a = s.index("// the icons on a tag's strip: what the stroke is about (two each)\nconst SG_TRAIT = {"); b = s.index("const sgTraits = id =>", a); b = s.index("\n", b) + 1
    cut = s[a:b]; assert cut.count('const ') == 3 and 'const SG_TRAITS = ' in cut, cut[:200]
    s = s[:a] + s[b:]
    assert 'sgTraits' not in s and 'SG_TRAIT' not in s
    # the strip's look: the same lime strip and height, its words in the display face
    s = rep(s, "/* a hang tag: a hook, the mottled card with the picture, a lime strip with two icons */", "/* a hang tag: a hook, the mottled card with the picture, a lime strip with a word or two (v323) */")
    s = rep(s, "#mStrokes.sgp .sgcard .sgcf{display:flex;justify-content:center;gap:6px;padding:4px 0 5px;border-radius:3px 3px 11px 11px;background:#A9DC2C;box-shadow:inset 0 1.5px 0 rgba(255,255,255,.4),inset 0 -2px 0 rgba(0,0,0,.12)}\n#mStrokes.sgp .sgcard .sgcf i{display:grid;place-items:center;width:21px;height:21px;border-radius:6px;background:#1E1E23;color:#fff;box-shadow:0 1.5px 0 rgba(0,0,0,.3)}\n#mStrokes.sgp .sgcard .sgcf svg{width:14px;height:14px}\n",
        "#mStrokes.sgp .sgcard .sgcf{display:flex;align-items:center;justify-content:center;min-height:21px;padding:4px 4px 5px;border-radius:3px 3px 11px 11px;background:#A9DC2C;box-shadow:inset 0 1.5px 0 rgba(255,255,255,.4),inset 0 -2px 0 rgba(0,0,0,.12);color:var(--ink0);font:400 12px/1 var(--font-display);letter-spacing:.01em;white-space:nowrap;overflow:hidden}\n#mStrokes.sgp .sgcard .sgcf b{font-weight:400;font-variant-numeric:tabular-nums}\n")
    s = rep(s, "#mStrokes.sgp .sgcard.lock .sgcf{background:#8DA65A}\n#mStrokes.sgp .sgcard.lock .sgcf i{opacity:.55}\n", "#mStrokes.sgp .sgcard.lock .sgcf{background:#8DA65A}\n")
    s = rep(s, "#mStrokes.sgp .sgcard .sgcf{padding:3px 0 4px}#mStrokes.sgp .sgcard .sgcf i{width:18px;height:18px;border-radius:5px}#mStrokes.sgp .sgcard .sgcf svg{width:12px;height:12px}",
        "#mStrokes.sgp .sgcard .sgcf{min-height:18px;padding:3px 4px 4px;font-size:11px}#mStrokes.sgp .sgcard.soon .sgcf{min-height:18px}")
    # (the crafting pill's own look is no longer used on a card; the lock pill keeps the shared one)
    s = rep(s, "#mStrokes.sgp .sgcard .sgst.cr{background:var(--sel);color:var(--ink0);font-variant-numeric:tabular-nums}\n", "")
    return s
