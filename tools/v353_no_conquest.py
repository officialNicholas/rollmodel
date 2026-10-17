"""v353: Season Conquest does not launch with the game. Its card is off the Choose Event page (no "Coming soon"), along with the
message a tap on it gave and the picture it showed.

Nothing of Conquest is deleted. The card's module (v300_quiet_hold_conquest.py, which also carries the quiet results and the hold fix)
stays in the build, and this module takes the card back out after it. The Conquest work itself (the Sunken Keep, its boss and the boss
demo: v309_conquest_stage.py, v311_conquest_boss.py, v315_boss_demo.py and the v316 to v319 modules) has been out of the build since
v320 and is untouched. To bring the card back, take 'v353_no_conquest' off the module list in q260.py.

With four events, Choose Event held sideways on a small phone (iPhone SE, 15, 16) fits both rows on the screen: the cards are a little
shorter there, so nothing fades out and no arrow says there's more below."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def cut_line(s, start):
    """the one whole line that starts with start"""
    c = s.count(start); assert c == 1, (c, start[:120])
    i = s.index(start); return s[:i] + s[s.index('\n', i) + 1:]

def apply(s):
    s = cut_line(s, '        <div class="evcard soon" data-ev="conquest"')       # the card
    s = cut_line(s, "$('evConq').addEventListener('click', ")                     # its "coming soon" message
    s = rep(s, " set('evConqArt', 'island');", "")                                # its picture
    assert 'onquest' not in s and 'evConq' not in s                               # nothing of it left in the game
    # four events now: held sideways on a small phone (an iPhone SE, 15 or 16) both rows fit, with no fade and no "more below" arrow
    s = rep(s, "</style>\n\n<div id=\"stage\">",
               "/* (v353) four events: held sideways on a small phone both rows fit, so nothing fades and no arrow says there's more below */\n"
               "@media (max-height:400px) and (min-aspect-ratio:1/1){.evgrid{row-gap:10px;padding-top:4px;padding-bottom:calc(max(8px,env(safe-area-inset-bottom)) + 8px)}"
               ".evbar{height:18px}.evtop{min-height:0;padding-top:5px;padding-bottom:5px}.evic{width:42px;height:42px}}\n"
               "</style>\n\n<div id=\"stage\">")
    return s
