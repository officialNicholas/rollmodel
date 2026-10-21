"""v433: the Time trial board's prize line said "When the week turns: 350 · 200 · 100 dabs", which didn't say what the numbers were.
Now it reads as weekly prizes by place: "Weekly prizes", then 1st 350, 2nd 200, 3rd 100, each with the dab coin, and a short line that
they're paid when the week ends."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = (".ttprz{flex-wrap:wrap;align-items:center;gap:6px 8px}.ttprz .pzh{flex-basis:100%;font:800 11px/1 var(--font-ui);letter-spacing:.08em;text-transform:uppercase;color:#5E566E}"
       ".ttprz .pz{display:inline-flex;align-items:center;gap:5px;padding:4px 9px 4px 5px;border-radius:999px;background:#F1EADB;box-shadow:inset 0 0 0 1.5px rgba(23,19,32,.14);font:800 12.5px/1 var(--font-ui);color:var(--black)}"
       ".ttprz .pz i{display:grid;place-items:center;min-width:26px;height:18px;padding:0 4px;border-radius:999px;font:900 10px/1 var(--font-ui);font-style:normal;color:#2B2400}"
       ".ttprz .pz.g i{background:#F2C12E}.ttprz .pz.s i{background:#C9CED6}.ttprz .pz.b i{background:#D08A4E;color:#2E1604}"
       ".ttprz .pzd{font:700 11.5px/1 var(--font-ui);color:#5E566E}.ttprz .pzn{flex-basis:100%;font:600 11px/1.3 var(--font-ui);color:#7A7288}\n")

def apply(s):
    s = rep(s, "<p class=\"ttprz\">When the week turns: <b>' + P3[0] + '</b> · <b>' + P3[1] + '</b> · <b>' + P3[2] + '</b> dabs</p>';",
               "<p class=\"ttprz\"><span class=\"pzh\">Weekly prizes</span><span class=\"pz g\"><i>1st</i>' + P3[0] + '</span><span class=\"pz s\"><i>2nd</i>' + P3[1] + '</span><span class=\"pz b\"><i>3rd</i>' + P3[2] + '</span><span class=\"pzd\">dabs</span><span class=\"pzn\">Paid to the top three when the week ends.</span></p>';")
    i = s.index(".ttprz{display:flex"); j = s.index("}", s.index(".ttprz b{")) + 1; s = s[:j] + CSS + s[j:]
    return s
