# the new title card (logo) and the new Halloween painting in the world select
import re, base64
p='/home/claude/paint-the-canvas.html'; s=open(p).read()
SP='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
logo = base64.b64encode(open(SP + '/logo/logo_1100.webp', 'rb').read()).decode()
art = base64.b64encode(open(SP + '/logo/halloween_art.webp', 'rb').read()).decode()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (a[:90], c); s = s.replace(a, b)

# CSS: the card is one image, kept once in a variable and used by the title screen and the loading screen
rep(""".logo{margin:0;display:flex;flex-direction:column;align-items:center;text-align:center;font-weight:400;animation:logoin .7s cubic-bezier(.25,1.5,.45,1) both}""",
""":root{--tcard:url("data:image/webp;base64,""" + logo + """")}
.tcard{display:block;aspect-ratio:1100/771;background:var(--tcard) center/contain no-repeat}
.logo{margin:0;display:flex;flex-direction:column;align-items:center;text-align:center;font-weight:400;animation:logoin .7s cubic-bezier(.25,1.5,.45,1) both}
.logo .tcard{width:min(88vw,430px,calc((100dvh - 330px) * 1.427));min-width:min(62vw,250px);margin:-6px 0 0;filter:drop-shadow(0 10px 16px rgba(6,2,16,.5))}
.logo.paint .tcard{animation:tcardpop .55s cubic-bezier(.3,1.6,.5,1) both}
@keyframes tcardpop{0%{transform:scale(.88,.94)}55%{transform:scale(1.04,.98)}}
.boot .boottc{width:min(64vw,300px);margin-bottom:6px}
.frame img.art{aspect-ratio:auto;height:100%;object-fit:cover;border:0;background:#1F0C42}""")
rep("""  .logo .l1{font-size:min(44px,9.5vh,5.2vw)}
  .logo .l2{font-size:min(96px,19vh,8.5vw)}""", """  .logo .tcard{width:min(40vw,60vh * 1.427);min-width:0}""")
rep(""".logo,.mcta,.world,.mworld,.bigplay::before,.card,.modal,.logo.paint .sf,.logo.paint .sx,.logo.paint .drip,.logo.paint .cw,""",
    """.logo,.mcta,.world,.mworld,.bigplay::before,.card,.modal,.logo.paint .tcard,""")

# HTML: the title card replaces the drawn logo (the season tag stays under it)
m = re.search(r'<h1 class="logo paint" id="logo">.*?</h1>', s, re.S); assert m
old = m.group(0); tag = re.search(r'<span class="season" id="seasonTag">.*?</span></span>|<span class="season" id="seasonTag">.*?</span>', old, re.S)
season = re.search(r'<span class="season" id="seasonTag"><b>Season 1</b>Halloween</span>', old); assert season, 'season tag'
s = s.replace(old, '<h1 class="logo paint" id="logo"><span class="tcard" role="img" aria-label="Roll Model"></span>' + season.group(0) + '</h1>')
rep('<div class="boot" id="boot" role="status"><span class="bootdrop" aria-hidden="true"></span>', '<div class="boot" id="boot" role="status"><span class="tcard boottc" aria-hidden="true"></span><span class="bootdrop" aria-hidden="true"></span>')

# the Halloween world's painting
m = re.search(r'(<button class="world" type="button" data-s="season"><span class="frame">)(<svg class="art".*?</svg>)', s, re.S); assert m
s = s.replace(m.group(2), '<img class="art" src="data:image/webp;base64,' + art + '" alt="" width="720" height="495" decoding="async">')
open(p,'w').write(s); print('ok', len(s) // 1024, 'KB')
