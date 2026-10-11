#!/usr/bin/env python3
"""v226: the canvas vote page, centred and refined. The carousel and its dots sit in the middle of the space between the title and the
footer (the hidden mode switch had pushed the paintings up under the title and left the dots floating in a gap); the count under the
title has its own line, clear of the season tape; each painting hangs under a warm gallery light with a brass name plate; round glass
arrows at the painting's own height; CPU difficulty is one dark switch with the pick on cream paper; the note under it is shorter."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui155_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = """
/* ---- the canvas vote page, refined (v226) ---- */
/* the paintings and their dots in the middle of the space between the title and the footer (portrait; the lesson keeps its own rows) */
@media (max-aspect-ratio:1/1){
  .menu:not(.tutoring) .mworld{grid-template-rows:auto auto minmax(6px,1fr) auto auto minmax(6px,1fr) auto}
  .menu:not(.tutoring) .mworld .whead{grid-row:1}
  .menu:not(.tutoring) .mworld #modes{grid-row:2}
  .menu:not(.tutoring) .mworld .gallery{grid-row:4;height:auto;padding-top:30px;padding-bottom:30px}
  .menu:not(.tutoring) .mworld #gDots{grid-row:5}
  .menu:not(.tutoring) .mworld .sgrid{grid-row:3/7;max-height:100%;overflow:auto}
  .menu:not(.tutoring) .mworld .wfoot{grid-row:7}
}
/* the count under the title on a line of its own */
.mworld .whead h2::after{position:static;display:block;transform:skewX(6deg);margin-top:10px;font:800 11px/1 var(--font-ui);letter-spacing:.22em;color:#CBC2DA}
/* a warm gallery light over the painting you're on */
.mworld .world::after{content:'';position:absolute;z-index:-1;left:-22%;right:-22%;top:-26%;bottom:-6%;background:radial-gradient(ellipse 50% 46% at 50% 38%,rgba(255,228,172,.26),rgba(255,228,172,.08) 52%,rgba(255,228,172,0) 72%);opacity:0;transition:opacity .35s;pointer-events:none}
.mworld .world[aria-pressed="true"]::after{opacity:1}
/* a brass name plate, screwed to the wall */
.mworld .plaque{position:relative;min-width:56%;padding:8px 30px 9px;border:0;border-radius:4px;background:linear-gradient(180deg,#F6E3AA 0%,#DDBB66 46%,#BF923A 54%,#DAB566 100%);box-shadow:inset 0 1px 0 rgba(255,255,255,.65),inset 0 -1px 0 rgba(96,64,12,.55),0 0 0 1.5px #4E360E,0 5px 12px rgba(0,0,0,.5)}
.mworld .plaque::before,.mworld .plaque::after{content:'';position:absolute;top:50%;width:6px;height:6px;margin-top:-3px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#FFF4CF,#8E6822 72%);box-shadow:0 0 0 1px rgba(70,46,8,.65)}
.mworld .plaque::before{left:10px}.mworld .plaque::after{right:10px}
.mworld .plaque .wn{color:#35240A;letter-spacing:.06em;text-shadow:0 1px 0 rgba(255,244,210,.65)}
.mworld .world.locked .plaque{background:linear-gradient(180deg,#D9D3E4,#B9B1CA 48%,#A39AB8 54%,#BEB6CF);box-shadow:inset 0 1px 0 rgba(255,255,255,.55),0 0 0 1.5px #3E3652,0 5px 12px rgba(0,0,0,.5)}
.mworld .world.locked .plaque .wn{color:#3E3652;text-shadow:0 1px 0 rgba(255,255,255,.5)}
/* round glass arrows at the painting's height */
.mworld .gnav{width:46px;height:46px;margin-top:-23px;border-radius:50%;background:rgba(23,19,32,.55);border:1.5px solid rgba(244,238,227,.32);color:#F4EEE3;box-shadow:0 8px 18px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.14);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);font:700 28px/1 var(--font-ui);display:grid;place-items:center;padding:0 0 3px}
.mworld .gnav.prev{left:10px;padding-right:2px}.mworld .gnav.next{right:10px;padding-left:2px}
.mworld .gnav:active{transform:scale(.92);box-shadow:0 4px 10px rgba(0,0,0,.45)}
.mworld .gnav[disabled]{opacity:0;pointer-events:none}
/* the dots: the one you're on a little bar */
.mworld .gdots{gap:7px;padding:10px 0 2px}
.mworld .gdots i{width:7px;height:7px;background:rgba(244,238,227,.26);transition:width .25s,background .25s}
.mworld .gdots i.on{width:22px;border-radius:4px;background:#F4EEE3;transform:none}
/* CPU difficulty: a heading between two fine rules, one dark switch, the pick on cream paper */
.mworld .lhead.critics{display:flex;align-items:center;justify-content:center;gap:12px;margin:0;font:800 11px/1 var(--font-ui);letter-spacing:.24em;color:#CBC2DA}
.mworld .lhead.critics::before,.mworld .lhead.critics::after{content:'';flex:0 1 64px;height:1px;background:linear-gradient(90deg,rgba(244,238,227,0),rgba(244,238,227,.4))}
.mworld .lhead.critics::after{background:linear-gradient(90deg,rgba(244,238,227,.4),rgba(244,238,227,0))}
.mworld #stages{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:5px;border-radius:14px;background:rgba(9,7,14,.62);box-shadow:inset 0 2px 7px rgba(0,0,0,.7),0 0 0 1px rgba(255,255,255,.09),0 1px 0 rgba(255,255,255,.06)}
.mworld #stages button{min-height:44px;margin:0;border:0;border-radius:10px;background:none;transform:none;box-shadow:none;color:#BDB4CC;font:900 15px/1 var(--font-head);letter-spacing:.05em;text-transform:uppercase;text-shadow:none;transition:background .2s,color .2s}
.mworld #stages button[aria-pressed="true"]{background:#F4EEE3 url(art/m_paperbg.webp) center/300px;color:#171320;box-shadow:0 3px 0 rgba(0,0,0,.5),inset 0 1px 0 rgba(255,255,255,.9)}
.mworld #stages button:not([aria-pressed="true"]):active{background:rgba(255,255,255,.06)}
/* the note: quieter, one run of text */
.mworld #soloNote{display:block;text-align:center;min-height:0;font:700 13px/1.4 var(--font-ui);color:#A79FB8}
.mworld #soloNote b{color:#E9E2F2}
.mworld .wfoot{gap:14px}
/* the footer stands on a little shade, apart from the wall */
.mworld::after{content:'';position:absolute;left:0;right:0;bottom:0;height:42%;background:linear-gradient(0deg,rgba(9,7,14,.7),rgba(9,7,14,0));pointer-events:none;z-index:0}
.mworld .wfoot{position:relative;z-index:1}
/* the versus card's canvas reel: its pictures share a class name with the player cards and took their padding and border, so they stood
   taller than the reel and the winner's bottom was cut off; now the pictures are their own size and the reel has room for the winner */
.vreel{height:140px}
.vtrack{margin-top:-41px}
.vreel .vcard{display:block;box-sizing:border-box;width:144px;height:82px;padding:0;border:0;border-radius:6px;animation:none;background:#2A2437}
.vreel .vcard.win{box-shadow:0 0 0 3px #FFD84A,0 0 0 5px #171320,0 10px 24px rgba(0,0,0,.6)}
.vreel .vcard .vcn{bottom:5px;font-size:13px}
@media (max-height:520px) and (min-aspect-ratio:1/1){.mworld .whead h2::after{margin-top:6px}.mworld #stages button{min-height:38px}.mworld::after{height:34%}}
"""
idx = s.rfind('</style>'); assert idx > 0 and s.count('</style>') == 3
s = s[:idx] + CSS.lstrip('\n') + s[idx:]
# the arrows at the painting's height (its frame's middle, not the gallery's)
rep("mw.style.setProperty('--gmid', Math.round(gr.top - mr.top + gr.height / 2) + 'px'); /* (the arrows' height: the middle of the gallery) */",
    "{ const ff = (on.querySelector('.frame') || on).getBoundingClientRect(); mw.style.setProperty('--gmid', Math.round((ff.height ? ff.top + ff.height / 2 : gr.top + gr.height / 2) - mr.top) + 'px'); } /* (the arrows' height: the middle of the painting) */")
# the note: the vote itself is on the Play button already
rep("'<b>Your vote:</b> ' + escAttr(TH.label) + '. Your rivals vote too. Most votes wins, and a tie is drawn.'",
    "'Your rivals vote too. <b>Most votes wins</b>, and a tie is drawn.'")
open(DST, 'w').write(s)
print('ui156 ok', n0, '->', len(s))
