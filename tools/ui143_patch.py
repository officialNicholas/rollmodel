#!/usr/bin/env python3
"""v215: the home screen inside the Claude app. On a phone there the page's own padding for the notch and the home bar sat on top of the
game's (every bar and button already keeps clear of them), so the space between the logo and Play shrank, the axolotl was framed into it
too big and its power bar slid up over the logo. The game handles the notch itself now (the page's padding is zeroed); the logo is
measured by what's drawn of it (its title card and season tag: the heading's own box has no height), for the framing and for how high the
bar may go; and the axolotl is framed so its head stays under the room kept for the bar."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui142_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the notch once: the game's bars and buttons each keep clear of the safe areas, so the page itself takes no padding for them
rep("<title>Roll Model</title>\n", "<title>Roll Model</title>\n<style>/* (the game keeps clear of the notch and the home bar itself, bar by bar: the page's own padding for them would count them twice) */:root{padding-top:0!important;padding-bottom:0!important}</style>\n")
# the logo as drawn: its title card and season tag (the heading's own box is empty)
rep("  const top = rc('lobbyTop'), lg = rc('logo'), L = rc('lobbyRail'), R = rc('lobbyRight'), bot = rc('lobbyBot');\n"
    "  const x0 = (L.right || r.left) - r.left + 6, x1 = (R.left || r.right) - r.left - 6, y0 = Math.max(top.bottom, lg.bottom || 0) - r.top + 58, y1 = (bot.top || r.bottom) - r.top;",
    "  const top = rc('lobbyTop'), L = rc('lobbyRail'), R = rc('lobbyRight'), bot = rc('lobbyBot');\n"
    "  const x0 = (L.right || r.left) - r.left + 6, x1 = (R.left || r.right) - r.left - 6, y0 = Math.max(top.bottom, logoBottom()) - r.top + 58, y1 = (bot.top || r.bottom) - r.top;")
# its head kept under the room left for the bar (its feet sit 0.86 of the way down)
rep("  const px = Math.min(fh * (land ? 0.9 : 0.92), fw * 0.74, Hh * 0.6);", "  const px = Math.min(fh * (land ? 0.84 : 0.84), fw * 0.74, Hh * 0.6);")
rep("// where the blob stands: the space the top bar, the side plates and the dock leave, its feet low in it\nfunction lobbyFrame() {",
    "// the bottom of the logo as drawn (its title card and the season tag under it; the heading's own box has no height)\n"
    "function logoBottom() { let b = 0; for (const e of document.querySelectorAll('#logo .tcard, #logo .season')) { if (e.offsetParent === null) continue; const r = e.getBoundingClientRect(); if (r.height > 0) b = Math.max(b, r.bottom); } return b; }\n"
    "// where the blob stands: the space the top bar, the side plates and the dock leave, its feet low in it\nfunction lobbyFrame() {")
rep("PB.mT -= rdt; if (PB.mT <= 0) { PB.mT = 0.5; let b = 0; for (const id of ['lobbyTop', 'logo']) { const e = $(id); if (e && e.offsetParent !== null) { const r = e.getBoundingClientRect(); if (r.height > 0) b = Math.max(b, r.bottom); } } PB.top = b; }",
    "PB.mT -= rdt; if (PB.mT <= 0) { PB.mT = 0.5; let b = logoBottom(); { const e = $('lobbyTop'); if (e && e.offsetParent !== null) { const r = e.getBoundingClientRect(); if (r.height > 0) b = Math.max(b, r.bottom); } } PB.top = b - stage.getBoundingClientRect().top; }")
rep('<p class="ver">Version 214</p>', '<p class="ver">Version 215</p>')
open(DST, 'w').write(s)
print('ui143 ok', n0, '->', len(s))
