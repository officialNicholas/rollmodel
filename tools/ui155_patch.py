#!/usr/bin/env python3
"""v226: the Paint Shop's season banner, twice the size and a proper event banner: a Halloween night scene (Ludo art) in a thick
framed card, a SEASON ONE tag, HALLOWEEN in big glowing letters, where to find the items and how many you've found, and a paint
dripped jack-o'-lantern bursting out over its corner; a shine sweeps across it now and then. More room around it."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui154_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = """
/* the Paint Shop's season banner: a framed night scene, the season's name in big glowing letters, a jack-o'-lantern over its corner */
.shcat.season.shban{position:relative;display:block;min-height:150px;margin:14px 0 14px;padding:0;border-radius:18px;background:#2A1846;box-shadow:0 0 0 3px #171320,0 6px 0 3px #171320,0 18px 30px rgba(0,0,0,.5);transform:rotate(-.6deg);color:#fff;letter-spacing:0;text-transform:none;isolation:isolate}
.shcat.season.shban .sbart{position:absolute;inset:0;border-radius:18px;overflow:hidden;z-index:-1;background:#2A1846 var(--sbbg) 72% 36%/cover no-repeat}
.shcat.season.shban .sbart::before{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(22,10,38,.94) 0%,rgba(22,10,38,.78) 38%,rgba(22,10,38,.18) 70%,rgba(22,10,38,0) 100%),linear-gradient(0deg,rgba(22,10,38,.55),rgba(22,10,38,0) 45%)}
.shcat.season.shban .sbart::after{content:'';position:absolute;top:-20%;bottom:-20%;left:-40%;width:28%;background:linear-gradient(100deg,rgba(255,255,255,0),rgba(255,240,210,.32) 50%,rgba(255,255,255,0));transform:skewX(-18deg);animation:sbshine 5.2s ease-in-out 1.2s infinite}
@keyframes sbshine{0%{left:-40%}28%,100%{left:130%}}
.shcat.season.shban .sbrim{position:absolute;inset:0;border-radius:18px;box-shadow:inset 0 2px 0 rgba(255,255,255,.28),inset 0 0 0 2px rgba(255,190,90,.35),inset 0 -10px 24px rgba(255,120,30,.18);pointer-events:none}
.shcat.season.shban .sbtx{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:7px;padding:18px 20px;max-width:calc(100% - min(128px,34%) - 6px);box-sizing:border-box}
.shcat.season.shban .sbkick{display:inline-block;padding:5px 10px 4px;border-radius:5px;background:#FFF1D2;color:#171320;font:800 11px/1 var(--font-ui);letter-spacing:.22em;text-transform:uppercase;box-shadow:2px 3px 0 rgba(0,0,0,.45);transform:rotate(-3deg);font-style:normal}
.shcat.season.shban .sbtitle{display:block;margin:2px 0 0;font:400 clamp(28px,8.4vw,46px)/.95 var(--font-display);letter-spacing:.01em;text-transform:uppercase;white-space:nowrap;background:linear-gradient(180deg,#FFFBE0 0%,#FFE266 30%,#FFB429 62%,#FF6A1A 100%);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-stroke:1.5px #171320;filter:drop-shadow(0 3px 0 #171320) drop-shadow(0 0 12px rgba(255,150,40,.6))}
.shcat.season.shban small{display:block;font:800 13px/1.25 var(--font-ui);letter-spacing:.01em;text-transform:none;color:#F6E9FF;text-shadow:0 2px 0 rgba(0,0,0,.5)}
.shcat.season.shban .sbprog{display:flex;align-items:center;gap:8px;margin-top:2px;font:800 12px/1 var(--font-ui);color:#FFD27A;text-shadow:0 2px 0 rgba(0,0,0,.5)}
.shcat.season.shban .sbprog i{position:relative;display:block;width:86px;height:10px;border-radius:6px;background:rgba(0,0,0,.45);box-shadow:inset 0 0 0 2px rgba(255,255,255,.12)}
.shcat.season.shban .sbprog i::after{content:'';position:absolute;left:2px;top:2px;bottom:2px;width:calc((100% - 4px) * var(--p,0));min-width:6px;border-radius:4px;background:linear-gradient(180deg,#FFD04A,#FF7A1A);box-shadow:0 0 8px rgba(255,150,40,.8)}
.shcat.season.shban .sbpump{position:absolute;right:-10px;bottom:-14px;width:min(128px,34%);height:auto;pointer-events:none;filter:drop-shadow(0 6px 0 rgba(23,19,32,.55)) drop-shadow(0 0 18px rgba(255,140,30,.55));animation:sbbob 2.6s ease-in-out infinite;transform-origin:50% 90%}
@keyframes sbbob{0%,100%{transform:translateY(0) rotate(4deg)}50%{transform:translateY(-6px) rotate(1deg)}}
@media (min-aspect-ratio:1/1){.shcat.season.shban .sbart{background-size:auto 210%;background-position:right 32%}}
@media (prefers-reduced-motion:reduce){.shcat.season.shban .sbart::after,.shcat.season.shban .sbpump{animation:none}}
@media (max-height:520px) and (min-aspect-ratio:1/1){.shcat.season.shban{min-height:104px;margin:6px 0 8px}.shcat.season.shban .sbtx{padding:12px 16px;gap:5px}.shcat.season.shban .sbtitle{font-size:32px}.shcat.season.shban .sbpump{width:110px;bottom:-10px}}
"""
rep("/* abilities: violet construction paper", CSS.lstrip('\n') + "/* abilities: violet construction paper")
# the banner's markup (the art beside the page: art/shop_hw_bg.webp, art/shop_hw_pump.webp)
rep("""    h += '<div class="shcat' + (c === 'season' ? ' season' : '') + '"><b>' + label + '</b>' + (c === 'season' ? '<small>Found on the Halloween canvases</small>' : '') + '</div>' + items.map(""",
    """    if (c === 'season') { const all = ITEMS.filter(w => w.season), got = all.filter(w => bought(w.id) || owns(w.id) || !needFind(w)).length;
      h += '<div class="shcat season shban" role="heading" aria-level="2"><span class="sbart" style="--sbbg:url(art/shop_hw_bg.webp)"></span><span class="sbrim"></span>'
        + '<span class="sbtx"><i class="sbkick">Season One</i><b class="sbtitle">Halloween</b><small>Find these on the Halloween canvases</small>'
        + '<span class="sbprog"><i style="--p:' + (all.length ? got / all.length : 0).toFixed(3) + '"></i>' + got + ' of ' + all.length + ' found</span></span>'
        + '<img class="sbpump" src="art/shop_hw_pump.webp" alt="" draggable="false"></div>'; }
    else h += '<div class="shcat"><b>' + label + '</b></div>';
    h += items.map(""")
open(DST, 'w').write(s)
print('ui155 ok', n0, '->', len(s))
