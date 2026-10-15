"""v285: the mid-match notices (a knock-out, "Roller!", "Whirlwind!", the weather...), refined. They were a big dark billboard with a
cream rim, a heavy drop shadow, a wallpaper of paint marks and a large square emblem. Now a slim strip you can see through (its panel
about 85%), about a quarter smaller: the fighter's colour (or the event's: heat orange, rain blue) as a slanted block at its start with
a small mark in it, clean italic type on one line (a long name shrinks it to fit) with a quiet line under it, a hairline edge and one soft sheen as it lands. It slides in, sits,
and lifts away about 20% sooner than before (1.7 s, a long one 2.8 s, a quick one 1.3 s). A knock-out takes the knocked-out fighter's
colour."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """
/* (v285) the mid-match notices, refined: a slim strip you can see through, the fighter's (or the event's) colour as a slanted block at
   its start with a small mark in it, clean type, a hairline edge and one soft sheen as it lands; in, a beat, and lifted away */
.banner{top:22%}
@media (min-aspect-ratio:1/1){.banner{top:17%}}
.banner .plate{min-height:0;max-width:min(86vw,420px);background:rgba(18,14,24,.84);border-radius:6px;box-shadow:inset 0 0 0 1.5px rgba(244,238,227,.16),0 8px 22px rgba(0,0,0,.28);transform:skewX(-10deg)}
.banner .plate::before{display:none}
.banner .plate::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,rgba(255,255,255,0) 35%,rgba(255,255,255,.13) 48%,rgba(255,255,255,0) 61%);transform:translateX(-110%);pointer-events:none}
.banner.on .plate::after{animation:feedsheen .75s .1s cubic-bezier(.3,.6,.3,1) both}
.banner .pem{width:52px;background:var(--acc,var(--ink));box-shadow:none;opacity:.95}
.banner .pem i{width:26px;height:26px;transform:skewX(10deg) rotate(-8deg);filter:none}
.banner .pem[data-k="drip"] i{width:20px;height:28px}
.banner .pem[data-k="stroke"] i{width:34px;height:20px}
.banner .ptxt{gap:5px;padding:10px 20px 11px 15px;transform:skewX(10deg)}
#bannerBig{font:900 clamp(18px,5.6vw,26px)/1 var(--font-head);font-style:italic;letter-spacing:.005em;text-shadow:0 2px 0 rgba(0,0,0,.35);white-space:nowrap;text-wrap:nowrap}
.banner .ptxt{justify-items:start;text-align:left}
#bannerSmall{font:800 10.5px/1.25 var(--font-ui);letter-spacing:.14em;color:rgba(244,238,227,.68);opacity:1;padding:0;text-wrap:balance}
.banner.on .plate,.banner.on.long .plate{animation:feedin 1.7s cubic-bezier(.2,.9,.25,1) forwards}
.banner.on.long .plate{animation-duration:2.8s}
.banner.on.quick .plate,.banner.on.long.quick .plate{animation-duration:1.3s}
@keyframes feedin{0%{opacity:0;transform:translateX(-22px) skewX(-10deg)}12%{opacity:1;transform:translateX(3px) skewX(-10deg)}20%{transform:translateX(0) skewX(-10deg)}84%{opacity:1;transform:translateX(0) skewX(-10deg)}100%{opacity:0;transform:translate(0,-12px) skewX(-10deg)}}
@keyframes feedsheen{to{transform:translateX(110%)}}
@keyframes feedfade{0%,100%{opacity:0;transform:skewX(-10deg)}10%,85%{opacity:1;transform:skewX(-10deg)}}
@media (prefers-reduced-motion:reduce){.banner.on .plate,.banner.on.long .plate,.banner.on.quick .plate{animation-name:feedfade}.banner.on .plate::after{animation:none}}
"""

def apply(s):
    s = rep(s, ".banner.on .plate::before{animation:platedrift 12s linear infinite}\n", ".banner.on .plate::before{animation:platedrift 12s linear infinite}\n" + CSS.lstrip('\n'))
    # shorter on screen, and an accent colour when it's about a fighter
    s = rep(s, "function banner(big, small, long, quick) { bannerUntil = performance.now() + (quick ? 1700 : long ? 3400 : 2100);",
               "function banner(big, small, long, quick, acc) { bannerUntil = performance.now() + (quick ? 1300 : long ? 2800 : 1700); if (acc) bannerEl.style.setProperty('--acc', acc); else bannerEl.style.removeProperty('--acc'); // (v285: 20% shorter; acc: the fighter's colour)\n ")
    s = rep(s, "if (by === P) banner(nameOf(D) + ' is out!', 'Eliminated', false);", "if (by === P) banner(nameOf(D) + ' is out!', 'Eliminated', false, false, TEAMS[D.team].css);")
    s = rep(s, "else banner(nameOf(D) + ' is out!', by ? (by === P ? 'By you' : 'Taken out by ' + sdName(by)) : reason === 'fall' ? 'Fell off the canvas' : 'Knocked themselves out', false);",
               "else banner(nameOf(D) + ' is out!', by ? (by === P ? 'By you' : 'Taken out by ' + sdName(by)) : reason === 'fall' ? 'Fell off the canvas' : 'Knocked themselves out', false, false, TEAMS[D.team].css);")
    s = rep(s, "if (by === P) banner('Got ' + nameOf(D) + '!', D.hearts + (D.hearts === 1 ? ' heart left' : ' hearts left'), false);",
               "if (by === P) banner('Got ' + nameOf(D) + '!', D.hearts + (D.hearts === 1 ? ' heart left' : ' hearts left'), false, false, TEAMS[D.team].css);")
    s = rep(s, "else if (mine) banner(nameOf(D) + ' lost a heart', by ? 'Got by ' + sdName(by) : '', false, true);",
               "else if (mine) banner(nameOf(D) + ' lost a heart', by ? 'Got by ' + sdName(by) : '', false, true, TEAMS[D.team].css);")
    # the headline on one line: a long name shrinks it to fit the strip rather than wrapping it onto a second line
    s = rep(s, "$('bannerBig').textContent = big;",
               "{ const B = $('bannerBig'); B.textContent = big; B.style.fontSize = ''; const room = Math.min(innerWidth * 0.86, 420) - 52 - 38, w = B.scrollWidth; if (w > room) B.style.fontSize = Math.max(13, parseFloat(getComputedStyle(B).fontSize) * room / w).toFixed(1) + 'px'; }")
    return s
