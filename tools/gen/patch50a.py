import sys, re, math
F = '/home/claude/paint-the-canvas.html'
s = open(F).read()
def rep(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        print('MISMATCH', c, repr(a[:120])); sys.exit(1)
    s = s.replace(a, b)

def ring(r, col='var(--outline)', n=16):
    return ','.join(f"{r*math.cos(2*math.pi*k/n):.2f}px {r*math.sin(2*math.pi*k/n):.2f}px 0 {col}" for k in range(n))

# ---------- fonts: two families, Bowlby One loud, Figtree for reading ----------
rep('family=Bowlby+One&family=Creepster&family=Figtree:wght@600;700;800;900', 'family=Bowlby+One&family=Figtree:wght@600;700;800;900')

CSS = r"""
/* Paint the World: a gothic toy box. The 3D night stage is the hero; the UI floats over it as chunky outlined pieces with a dark lip, like parts of a toy.
   Your paint color runs through the logo swash, Play, your score and the blood tube. The holy water is always blue. Bowlby One for anything loud, Figtree for anything you read. */
:root{
  --sky:#120A24;
  --plum:#21153C;
  --plum-2:#2D1F50;
  --glass:rgba(17,9,34,.86);
  --line:#0C0620;
  --outline:#1A1030;
  --bone:#F6EEDF;
  --muted:#B3A6D6;
  --gold:#FFD86B;
  --rival:#FFD86B;
  --holy:#2E9BFF;
  --holy-hi:#7CC4FF;
  --ink:#E3122F;
  --ink-hi:#FF6175;
  --ink-lo:#99091F;
  --ink-rgb:227,18,47;
  --white:#FFFFFF;
  --wood:#B48A3C;
  --wood-deep:#6E5020;
  --font-display:"Bowlby One","Arial Black",system-ui,sans-serif;
  --font-ui:"Figtree",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --o2:__O2__;
  --o3:__O3__;
  --o4:__O4__;
  color-scheme:dark;
}
[hidden]{display:none!important}
html,body{height:100%}
body{margin:0;background:var(--sky);color:var(--bone);font-family:var(--font-ui);overflow:hidden;-webkit-user-select:none;user-select:none;-webkit-tap-highlight-color:transparent;-webkit-touch-callout:none}
#stage{position:relative;height:100%;width:100%;overflow:hidden;touch-action:none}
canvas{position:absolute;inset:0;width:100%;height:100%;display:block}
button{font-family:var(--font-ui)}
.ib:focus-visible,.btn:focus-visible,.sw:focus-visible,.seg button:focus-visible,.chipbtn:focus-visible,.slamBtn:focus-visible{outline:3px solid var(--gold);outline-offset:3px}

/* screen tints */
.vig{position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity .18s;background:radial-gradient(ellipse 75% 70% at 50% 50%,transparent 55%,rgba(35,38,74,.6) 100%)}
.vig.low{opacity:1;background:radial-gradient(ellipse 75% 70% at 50% 50%,transparent 58%,rgba(var(--ink-rgb),.55) 100%);animation:throb .7s ease-in-out infinite}
.vig.danger{opacity:1;background:radial-gradient(ellipse 75% 70% at 50% 50%,transparent 50%,rgba(35,38,74,.62) 100%);animation:none}
.vig.heat{opacity:1;background:radial-gradient(ellipse 75% 70% at 50% 50%,transparent 42%,rgba(255,120,30,.6) 100%);animation:throb .45s ease-in-out infinite}
@keyframes throb{50%{opacity:.45}}
.flash{position:absolute;inset:0;pointer-events:none;background:var(--white);opacity:0}
.flash.on{animation:flash .4s ease-out}
@keyframes flash{0%{opacity:.75}100%{opacity:0}}
.orbflash{position:absolute;inset:0;pointer-events:none;z-index:5;opacity:0}
.orbflash.on{animation:orbflash 1.8s ease-out}
@keyframes orbflash{0%{opacity:1;box-shadow:inset 0 0 70px 22px #FF4D6D}25%{opacity:.9;box-shadow:inset 0 0 70px 22px #FFD23F}50%{opacity:.75;box-shadow:inset 0 0 70px 22px #4DA6FF}75%{opacity:.5;box-shadow:inset 0 0 70px 22px #C77DFF}100%{opacity:0;box-shadow:inset 0 0 70px 22px #4DFFB8}}

/* HUD: one scoreboard up top, the pound button and your blood down at your thumb */
.hud{position:absolute;inset:0;pointer-events:none;display:flex;flex-direction:column;align-items:center;padding:max(12px,env(safe-area-inset-top)) 14px max(18px,env(safe-area-inset-bottom));transition:opacity .3s}
.hud.off{opacity:0}
.hud.off .ib,.hud.off .slamBtn{pointer-events:none}
.top{width:100%;display:grid;grid-template-columns:44px 1fr 44px;align-items:start;gap:10px}
.left{display:flex;flex-direction:column;align-items:center;gap:8px}
.score{grid-column:2;justify-self:center;width:min(100%,262px);box-sizing:border-box;display:grid;gap:7px;padding:7px 12px 9px;background:var(--glass);border:3px solid var(--line);border-radius:20px;box-shadow:0 4px 0 var(--line)}
.vsrow{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:10px}
.vsn{font:400 28px/1 var(--font-display);font-variant-numeric:tabular-nums;text-shadow:0 3px 0 var(--line)}
.vsn.you{text-align:right;color:var(--ink-hi)}
.vsn.cpu{text-align:left;color:var(--holy-hi)}
.vsn.tick{animation:tick .22s ease-out}
.vsn.down{animation:down .4s ease-out}
.clock{font:800 16px/1 var(--font-ui);color:var(--bone);font-variant-numeric:tabular-nums;min-width:3.1ch;text-align:center;padding:5px 8px;border-radius:10px;background:rgba(255,255,255,.08)}
.clock.hurry{background:var(--ink);color:var(--white);animation:tick .5s ease-in-out infinite}
.tug{position:relative;height:8px;border-radius:99px;background:rgba(255,255,255,.12);overflow:hidden}
.tug i{position:absolute;top:0;bottom:0;width:0;transition:width .3s ease-out}
.tug .tYou{left:0;background:var(--ink)}
.tug .tCpu{right:0;background:var(--holy)}
@keyframes tick{40%{transform:scale(1.13)}}
@keyframes down{25%{transform:translateX(-5px)}50%{transform:translateX(5px)}75%{transform:translateX(-3px)}}
.ib{pointer-events:auto;appearance:none;width:44px;height:44px;border-radius:50%;border:3px solid var(--line);background:var(--glass);color:var(--bone);display:grid;place-items:center;padding:0;cursor:pointer;box-shadow:0 3px 0 var(--line)}
.ib:active{transform:translateY(2px);box-shadow:0 1px 0 var(--line)}
.ib svg{width:20px;height:20px;fill:currentColor;stroke:currentColor}
.corner{position:absolute;top:max(12px,env(safe-area-inset-top));right:14px;z-index:8}
.chips{display:flex;gap:8px;margin-top:10px;min-height:30px}
.chip{display:inline-flex;align-items:center;gap:6px;font:800 14px/1 var(--font-ui);color:var(--white);background:var(--glass);padding:6px 12px;border:2.5px solid var(--line);border-radius:99px;animation:chipin .35s cubic-bezier(.3,1.6,.5,1)}
@keyframes chipin{0%{transform:scale(.4);opacity:0}}
.chip svg{width:16px;height:16px;fill:currentColor;stroke:currentColor}
.chip.wx.warn{background:#C9721F}
.chip.wx.sun{background:#C2461F}
.chip.wx.sun.burn{animation:redflash .3s steps(2) infinite}
.chip.wx.sun.safe{background:#2A7356}
.chip.wx.rain{background:#2F6A9E}
.chip.wx.dusk{background:#4E3790}
.chip.pw{background:var(--ink)}
.chip.pw i{width:14px;height:14px;border-radius:50%;background:conic-gradient(var(--white) 360deg,rgba(255,255,255,.3) 0)}
@keyframes redflash{50%{filter:brightness(1.4)}}
.spacer{flex:1}
.tube{display:flex;align-items:center;width:min(78%,330px)}
.tdrop{flex:none;width:28px;height:28px;margin-right:-14px;z-index:1;background:var(--ink);transition:background .3s;border:3px solid var(--line);border-radius:50% 50% 50% 0;transform:rotate(-45deg);box-shadow:inset 4px -4px 0 rgba(255,255,255,.22)}
.ttrack{flex:1;height:30px;box-sizing:border-box;display:flex;gap:4px;padding:5px 7px 5px 18px;background:var(--glass);border:3px solid var(--line);border-radius:99px;box-shadow:0 3px 0 var(--line)}
.ttrack span{position:relative;flex:1;background:rgba(255,255,255,.1);border-radius:5px;overflow:hidden}
.ttrack span:last-child{border-radius:5px 99px 99px 5px}
.ttrack i{display:block;height:100%;width:100%;background:linear-gradient(180deg,rgba(255,255,255,.34) 0 34%,transparent 34%) var(--ink);transform-origin:left center;transform:scaleX(0)}
.ttrack span.full{animation:segpop .4s cubic-bezier(.3,1.8,.5,1)}
.ttrack span.empty{animation:segdrain .45s ease-out}
@keyframes segpop{40%{transform:scale(1.12,1.35)}}
@keyframes segdrain{20%{transform:translateY(3px) rotate(-4deg)}60%{transform:translateY(-1px) rotate(2deg)}}
.ttrack.nope{animation:nope .35s}
@keyframes nope{25%{transform:translateX(-6px)}50%{transform:translateX(6px)}75%{transform:translateX(-3px)}}
.tube.low{animation:wobble .35s ease-in-out infinite}
@keyframes wobble{25%{transform:rotate(-1.4deg)}75%{transform:rotate(1.4deg)}}
.tube.giant .ttrack i{background:linear-gradient(90deg,#FF4D6D,#FFD23F,#4DFFB8,#4DA6FF,#C77DFF,#FF4D6D);background-size:200% 100%;animation:orbflow .9s linear infinite}
.tube.giant .ttrack{box-shadow:0 3px 0 var(--line),0 0 14px rgba(255,255,255,.55)}
.tube.giant .tdrop{animation:orbhue 1.2s linear infinite}
.tube.dry .tdrop{filter:grayscale(1) brightness(.75)}
.tube.dry .ttrack span{background:rgba(255,255,255,.05)}
@keyframes orbflow{to{background-position:-200% 0}}
@keyframes orbhue{to{filter:hue-rotate(360deg)}}
.tube.fill .ttrack i{background:repeating-linear-gradient(-45deg,transparent 0 10px,rgba(255,255,255,.35) 10px 20px) var(--ink);background-size:28px 28px;animation:stripes .5s linear infinite}
@keyframes stripes{to{background-position:28px 0}}
.tube.heat .tdrop,.tube.heat .ttrack i{background:#FF9A3C;animation:redflash .3s steps(2) infinite}
.tube.heat .ttrack span::after{content:"";position:absolute;inset:0;opacity:.8;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='20'%3E%3Cpath d='M0 11l7-3 5 6 9-9 6 8 10-5 7 6 9-7 11 4M21 5l3-5M37 9l-3 11M12 14l-3 6M50 7l2-7' fill='none' stroke='%2323264A' stroke-width='1.7' stroke-linejoin='round'/%3E%3C/svg%3E") repeat-x}
.lives{display:flex;flex-direction:column;gap:5px;align-items:center}
.lives i{display:block;width:15px;height:15px;background:var(--ink);border:2.5px solid var(--line);border-radius:50% 50% 50% 0;transform:rotate(-45deg)}
.slamBtn{position:relative;flex:none;margin-bottom:12px;width:72px;height:72px;border-radius:50%;border:3px solid var(--line);background:var(--ink);box-shadow:inset 0 -6px 0 rgba(0,0,0,.2),inset 0 3px 0 rgba(255,255,255,.3),0 5px 0 var(--line);display:grid;place-items:center;padding:0;cursor:pointer;pointer-events:auto;touch-action:none;animation:slamin .4s cubic-bezier(.3,1.7,.5,1)}
.slamBtn:active{transform:translateY(4px);box-shadow:inset 0 -6px 0 rgba(0,0,0,.2),inset 0 3px 0 rgba(255,255,255,.3),0 1px 0 var(--line)}
.slamBtn svg{width:40px;height:40px;fill:var(--white);stroke:var(--line);stroke-width:2;stroke-linejoin:round}
.slamBtn svg path:first-child{transition:transform .22s cubic-bezier(.3,1.7,.5,1);transform-box:view-box;transform-origin:20px 16.75px}
.slamBtn.up svg path:first-child{transform:rotate(180deg)}
.slamBtn::after{content:"";position:absolute;inset:0;border-radius:50%;background:conic-gradient(rgba(17,9,34,.62) var(--cd,0deg),transparent 0);pointer-events:none}
.slamBtn.off{background:#4A3E6E;animation:none}
.slamBtn.off svg{opacity:.55}
.slamBtn.ready{animation:slamin .4s cubic-bezier(.3,1.7,.5,1),glow 1.4s ease-in-out .4s infinite}
.slamBtn.press::before{content:"";position:absolute;inset:-6px;border-radius:50%;border:3px solid var(--ink);animation:ring .4s ease-out forwards;pointer-events:none}
@keyframes ring{from{transform:scale(.8);opacity:1}to{transform:scale(1.45);opacity:0}}
@keyframes slamin{0%{transform:scale(.2)}100%{transform:none}}
@keyframes glow{50%{box-shadow:inset 0 -6px 0 rgba(0,0,0,.2),inset 0 3px 0 rgba(255,255,255,.3),0 5px 0 var(--line),0 0 0 9px rgba(var(--ink-rgb),.35)}}
.orbs{position:absolute;inset:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;left:-7px;top:-7px;width:14px;height:14px;border-radius:50%;background:var(--ink);border:2.5px solid var(--line);box-sizing:border-box;transition:transform .5s cubic-bezier(.55,0,.8,.4),opacity .5s ease-in;will-change:transform}
.orbptr{position:absolute;left:0;top:0;width:40px;height:40px;margin:-20px 0 0 -20px;pointer-events:none;z-index:6;display:none;will-change:transform}
.orbptr.on{display:block}
.orbptr i{position:absolute;inset:7px;border-radius:50%;border:3px solid var(--line);background:conic-gradient(#FF4D6D,#FFD23F,#4DFFB8,#4DA6FF,#C77DFF,#FF4D6D);box-shadow:0 0 14px 5px rgba(255,255,255,.65);animation:orbspin 1.1s linear infinite}
.orbptr u{position:absolute;inset:0}
.orbptr b{position:absolute;left:50%;top:-9px;margin-left:-9px;width:0;height:0;border-left:9px solid transparent;border-right:9px solid transparent;border-bottom:13px solid #fff;filter:drop-shadow(0 0 2px rgba(20,10,40,.9))}
.orbptr.edge i{animation:orbspin 1.1s linear infinite,orbpulse .7s ease-in-out infinite alternate}
.foeptr{position:absolute;left:0;top:0;width:42px;height:42px;margin:-21px 0 0 -21px;pointer-events:none;z-index:6;display:none;will-change:transform}
.foeptr.on{display:block}
.foeptr i{position:absolute;inset:9px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid var(--line);background:var(--holy);box-shadow:0 0 0 2.5px rgba(255,255,255,.8),0 0 10px 2px rgba(46,155,255,.6)}
.foeptr u{position:absolute;inset:0}
.foeptr b{position:absolute;left:50%;top:-8px;margin-left:-8px;width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;border-bottom:12px solid #fff;filter:drop-shadow(0 0 2px rgba(20,10,40,.9))}
.foeptr.warn i{background:#FF3B5C;animation:foewarn .35s ease-in-out infinite alternate}
.foeptr.warn b{border-bottom-color:#FF3B5C}
@keyframes foewarn{to{box-shadow:0 0 14px 6px rgba(255,59,92,.85)}}
@keyframes orbspin{to{transform:rotate(360deg)}}
@keyframes orbpulse{to{box-shadow:0 0 22px 9px rgba(255,255,255,.9)}}
.sling{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;opacity:0;transition:opacity .12s ease-out;overflow:visible}
.sling.on{opacity:1}
.sling line{stroke-linecap:round}
.sling #slBand{stroke:#fff}
.sling #slBandO{stroke:var(--outline)}
.sling #slA{fill:none;stroke:#fff;stroke-width:4;filter:drop-shadow(0 0 1.5px var(--outline)) drop-shadow(0 2px 0 var(--outline))}
.sling #slB{fill:var(--sl,var(--ink));stroke:#fff;stroke-width:3.5;filter:drop-shadow(0 0 1.5px var(--outline)) drop-shadow(0 2px 0 var(--outline))}
.pop{position:absolute;left:50%;top:92px;transform:translateX(-50%);pointer-events:none;font:400 21px/1 var(--font-display);color:var(--gold);opacity:0;text-shadow:var(--o2),0 4px 0 var(--outline)}
.pop.on{animation:rise .9s ease-out}
@keyframes rise{0%{opacity:0;transform:translate(60%,10px) scale(.7)}15%{opacity:1;transform:translate(60%,0) scale(1.1)}100%{opacity:0;transform:translate(60%,-34px)}}
.hint{position:absolute;left:16px;right:16px;top:142px;display:flex;justify-content:center;pointer-events:none}
.hint span{background:var(--glass);border:2.5px solid var(--line);color:var(--white);font-size:15px;font-weight:700;line-height:1.35;padding:8px 15px;border-radius:99px;max-width:32ch;text-align:center;opacity:0;transform:translateY(-6px);transition:opacity .2s,transform .2s;text-wrap:balance;box-shadow:0 3px 0 var(--line)}
.hint.on span{opacity:1;transform:none}
.banner{position:absolute;left:16px;right:16px;top:30%;display:flex;flex-direction:column;align-items:center;gap:8px;pointer-events:none;opacity:0;text-align:center}
.banner.on{animation:banner 2.1s ease forwards}
.banner.on.long{animation-duration:3.4s}
.banner p{margin:0}
#bannerBig{font:400 clamp(36px,11vw,54px)/1.02 var(--font-display);color:var(--gold);text-wrap:balance;text-shadow:var(--o3),0 7px 0 var(--outline)}
#bannerSmall{font-size:16px;font-weight:800;color:var(--white);background:var(--glass);border:2.5px solid var(--line);padding:6px 14px;border-radius:99px;max-width:30ch}
#bannerSmall:empty{display:none}
@keyframes banner{0%{opacity:0;transform:scale(.5)}12%{opacity:1;transform:scale(1.08)}20%{transform:scale(1)}82%{opacity:1;transform:none}100%{opacity:0;transform:translateY(-14px)}}

/* menu: the logo up top, your blob and the holy water in the middle (that's the 3D scene), one dock of controls at your thumb */
.menu{position:absolute;inset:0;z-index:4;display:flex;flex-direction:column;align-items:center;justify-content:space-between;box-sizing:border-box;padding:max(62px,calc(env(safe-area-inset-top) + 50px)) 16px max(16px,env(safe-area-inset-bottom));pointer-events:none}
.logo{margin:0;display:flex;flex-direction:column;align-items:center;text-align:center;font-weight:400;animation:logoin .7s cubic-bezier(.25,1.5,.45,1) both}
.logo .l1{font:400 clamp(27px,8.6vw,44px)/1 var(--font-display);color:var(--bone);text-shadow:var(--o3),0 5px 0 var(--outline)}
.logo .l2{position:relative;display:grid;place-items:center;width:4.7em;height:1.3em;margin:.02em 0 .5em;font:400 clamp(52px,16.6vw,96px)/1 var(--font-display);transform:rotate(-3deg)}
.swash{position:absolute;left:0;top:0;width:100%;height:auto;overflow:visible;pointer-events:none}
.swash .sd{fill:var(--outline);stroke:var(--outline);stroke-width:14;stroke-linejoin:round;transform:translateY(9px)}
.swash .so{fill:var(--outline);stroke:var(--outline);stroke-width:14;stroke-linejoin:round}
.swash .sf{fill:var(--ink)}
.swash .sh{fill:none;stroke:var(--ink-hi);stroke-width:8;stroke-linecap:round;opacity:.7}
.swash .sl{fill:none;stroke:var(--ink-lo);stroke-width:3.5;stroke-linecap:round;opacity:.55}
.swash .drip{transform-box:fill-box;transform-origin:50% 0}
.cw{position:relative;color:var(--bone);line-height:1;padding-bottom:.04em;text-shadow:var(--o4),0 6px 0 var(--outline)}
.logo.paint .sf,.logo.paint .sx{animation:wipe .55s cubic-bezier(.3,.7,.3,1) both}
.logo.paint .drip{animation:drip .7s cubic-bezier(.3,.8,.35,1) both;animation-delay:var(--dd,.3s)}
.logo.paint .cw{animation:wordpop .45s .12s cubic-bezier(.3,1.7,.5,1) both}
@keyframes wipe{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes drip{from{transform:scaleY(0)}}
@keyframes wordpop{from{transform:scale(.7)}}
@keyframes logoin{from{opacity:0;transform:translateY(-26px) scale(.92)}}
.dock{pointer-events:auto;width:min(100%,420px);box-sizing:border-box;display:grid;gap:14px;padding:16px;background:rgba(33,21,60,.96);border:3px solid var(--line);border-radius:28px;box-shadow:0 6px 0 var(--line),0 24px 48px rgba(6,2,16,.5);animation:dockin .55s .08s cubic-bezier(.25,1.3,.45,1) both}
@keyframes dockin{from{opacity:0;transform:translateY(44px)}}
.swatches{display:flex;justify-content:space-between;padding:2px 6px 0}
.sw{appearance:none;width:44px;height:48px;padding:0;border:0;background:none;cursor:pointer;display:grid;place-items:center;transition:transform .2s cubic-bezier(.3,1.6,.5,1)}
.sw i{display:block;width:26px;height:26px;margin-top:6px;background:var(--c);border:3px solid var(--line);border-radius:50% 50% 50% 0;transform:rotate(135deg);box-shadow:inset 0 -5px 0 rgba(255,255,255,.26)}
.sw:hover{transform:translateY(-2px)}
.sw[aria-pressed="true"]{transform:scale(1.22)}
.sw[aria-pressed="true"] i{box-shadow:inset 0 -5px 0 rgba(255,255,255,.26),0 0 0 3px var(--bone),0 0 0 6px var(--line)}
.seg{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;padding:4px;background:var(--line);border-radius:16px}
.seg button{appearance:none;border:0;border-radius:12px;min-height:42px;padding:0 6px;background:transparent;color:var(--muted);font:800 16px/1 var(--font-ui);cursor:pointer;transition:background .15s,color .15s}
.seg button:hover{color:var(--bone)}
.seg button[aria-pressed="true"]{background:var(--bone);color:var(--outline);box-shadow:0 3px 0 rgba(0,0,0,.45)}
.btn{appearance:none;display:flex;align-items:center;justify-content:center;gap:8px;width:100%;min-height:52px;box-sizing:border-box;padding:10px 16px;border:3px solid var(--line);border-radius:18px;background:var(--plum-2);color:var(--bone);font:800 17px/1 var(--font-ui);cursor:pointer;box-shadow:inset 0 2px 0 rgba(255,255,255,.08),0 4px 0 var(--line);transition:transform .06s,box-shadow .06s}
.btn:active{transform:translateY(3px);box-shadow:inset 0 2px 0 rgba(255,255,255,.08),0 1px 0 var(--line)}
.btn.play{min-height:64px;border-radius:20px;background:var(--ink);color:var(--white);font:400 30px/1 var(--font-display);letter-spacing:.01em;text-shadow:var(--o2),0 3px 0 var(--outline);box-shadow:inset 0 -6px 0 rgba(0,0,0,.2),inset 0 3px 0 rgba(255,255,255,.3),0 5px 0 var(--line)}
.btn.play:active{transform:translateY(4px);box-shadow:inset 0 -6px 0 rgba(0,0,0,.2),inset 0 3px 0 rgba(255,255,255,.3),0 1px 0 var(--line)}
.btn.play.sm{min-height:56px;font-size:24px}
.btn.two{flex-direction:column;gap:5px}
.btn.two small{font:800 12px/1 var(--font-ui);letter-spacing:.01em;opacity:.92;text-shadow:none}
.mfoot{display:flex;justify-content:center;gap:10px}
.chipbtn{appearance:none;display:inline-flex;align-items:center;gap:7px;min-width:0;min-height:40px;padding:0 14px;border-radius:99px;border:2px solid rgba(255,255,255,.14);background:rgba(255,255,255,.04);color:var(--bone);font:700 14px/1 var(--font-ui);cursor:pointer}
.chipbtn svg{width:17px;height:17px;flex:none}
.chipbtn span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.chipbtn:hover{border-color:rgba(255,255,255,.3)}
.chipbtn:active{transform:translateY(1px);background:rgba(255,255,255,.1)}
#cvName.pop{display:inline-block;animation:cvpop .35s cubic-bezier(.3,1.7,.5,1)}
@keyframes cvpop{0%{transform:scale(.82)}60%{transform:scale(1.06)}100%{transform:none}}
.note{margin:0;font-size:14px;line-height:1.4;color:var(--muted);font-weight:700;text-wrap:pretty;text-align:center}
@media (min-width:860px) and (min-aspect-ratio:1/1){
  .menu{align-items:flex-start;justify-content:center;gap:clamp(8px,2vh,24px);padding:40px 0 40px clamp(40px,6vw,96px)}
  .logo{align-items:flex-start;text-align:left}
  .logo .l2{margin-left:-.12em}
  .dock{width:420px}
}

/* cards: how to play and pause sit over a dimmed game */
.modal{position:absolute;inset:0;z-index:12;display:grid;place-items:center;padding:16px;box-sizing:border-box;background:rgba(9,4,22,.62);animation:fadein .18s ease-out}
@keyframes fadein{from{opacity:0}}
.card{width:min(100%,420px);max-height:100%;overflow:auto;box-sizing:border-box;display:grid;gap:14px;padding:20px 18px 18px;background:var(--plum);border:3px solid var(--line);border-radius:26px;box-shadow:0 6px 0 var(--line),0 24px 48px rgba(6,2,16,.55);animation:cardin .3s cubic-bezier(.25,1.4,.45,1);touch-action:pan-y}
@keyframes cardin{from{opacity:0;transform:translateY(18px) scale(.96)}}
.ctitle{margin:0;font:400 30px/1 var(--font-display);color:var(--bone);text-align:center;text-shadow:var(--o2),0 4px 0 var(--outline)}
.rules{list-style:none;margin:0;padding:0;display:grid;gap:12px}
.rules li{display:grid;grid-template-columns:30px 1fr;align-items:start;gap:12px;font-size:15px;font-weight:600;line-height:1.4;color:var(--bone)}
.dot{width:30px;height:30px;border-radius:10px;border:2.5px solid var(--line);box-sizing:border-box;display:grid;place-items:center;font-size:14px;font-weight:800}
.dot.hand{background:var(--bone);color:var(--outline)}
.dot.ink{background:var(--ink)}
.dot.holy{background:var(--holy)}
.dot.sun{background:#F29A3A}
.dot.orbd{background:conic-gradient(#FF4D6D,#FFD23F,#4DFFB8,#4DA6FF,#C77DFF,#FF4D6D);border-radius:50%}
kbd{display:inline-block;min-width:1.4em;padding:1px 5px;margin:0 1px;border:2px solid var(--line);border-bottom-width:3px;border-radius:6px;background:var(--bone);color:var(--outline);font:800 11px/1.3 var(--font-ui);text-align:center;vertical-align:1px}
.row{display:flex;gap:10px}
.pscore{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:12px;padding:12px 14px;border-radius:16px;background:rgba(255,255,255,.05)}
.pscore b{font:400 30px/1 var(--font-display);font-variant-numeric:tabular-nums}
.pscore .you{text-align:right;color:var(--ink-hi)}
.pscore .cpu{text-align:left;color:var(--holy-hi)}
.pscore span{font:700 14px/1.25 var(--font-ui);color:var(--muted);text-align:center}

/* end: the canvas you painted, framed with a museum placard, and the score as two paint sample cards */
.sheet{position:absolute;left:50%;bottom:0;transform:translateX(-50%);width:min(100%,520px);box-sizing:border-box;z-index:4;display:grid;gap:14px;padding:20px 16px max(18px,env(safe-area-inset-bottom));max-height:90%;overflow:auto;touch-action:pan-y;background:var(--plum);border:3px solid var(--line);border-bottom:0;border-radius:28px 28px 0 0;box-shadow:0 -10px 40px rgba(6,2,16,.45);animation:sheetin .38s cubic-bezier(.2,1.2,.4,1)}
@keyframes sheetin{from{transform:translate(-50%,48px);opacity:0}}
@media (min-width:700px){.sheet{bottom:20px;border-bottom:3px solid var(--line);border-radius:28px;box-shadow:0 6px 0 var(--line),0 24px 48px rgba(6,2,16,.55)}}
.rtitle{margin:0;text-align:center;font:400 clamp(32px,9.6vw,44px)/1.02 var(--font-display);color:var(--gold);text-wrap:balance;text-shadow:var(--o3),0 6px 0 var(--outline)}
.rtitle.lose{color:var(--holy-hi)}
.rtitle.draw{color:var(--bone)}
.endgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px;align-items:center}
.frame{margin:0;display:grid;gap:8px}
.frame .wood{padding:7px;border-radius:6px;border:3px solid var(--line);background:linear-gradient(135deg,#E8C77E,var(--wood) 40%,var(--wood-deep));box-shadow:0 4px 0 var(--line)}
.frame img{display:block;width:100%;aspect-ratio:1;object-fit:cover;border:5px solid var(--white);box-sizing:border-box;background:var(--sky)}
.placard{background:var(--bone);color:var(--outline);border:2px solid var(--line);border-radius:6px;padding:6px 8px;display:grid;gap:2px}
.placard b{font-size:12px;font-weight:900;line-height:1.2;text-wrap:balance}
.placard span{font-size:11px;font-weight:700;color:#5D5378;line-height:1.25}
.scores{display:grid;gap:12px;align-content:center}
.pchip{position:relative;display:grid;grid-template-columns:14px 1fr;gap:12px;padding:10px 12px 10px 10px;background:var(--plum-2);border:3px solid var(--line);border-radius:16px;box-shadow:0 3px 0 var(--line)}
.pchip i{border-radius:7px;background:var(--ink);border:2px solid var(--line)}
.pchip.cpu i{background:var(--holy)}
.pchip b{display:block;font:400 clamp(28px,8.6vw,38px)/1 var(--font-display);color:var(--ink-hi);font-variant-numeric:tabular-nums}
.pchip.cpu b{color:var(--holy-hi)}
.pchip span{display:block;margin-top:5px;font:700 13px/1.1 var(--font-ui);color:var(--muted)}
.pchip svg{position:absolute;right:10px;top:-15px;width:30px;height:24px;display:none;fill:var(--gold);stroke:var(--line);stroke-width:2.2;stroke-linejoin:round}
.pchip.win svg{display:block;animation:crownin .5s .35s cubic-bezier(.3,1.7,.5,1) both}
@keyframes crownin{from{transform:translateY(-10px) rotate(-20deg) scale(.4);opacity:0}}
.pill{justify-self:start;font:800 12px/1 var(--font-ui);padding:6px 10px;border-radius:99px;border:2px solid var(--line);background:var(--gold);color:var(--outline)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.stat{padding:10px 6px 9px;border-radius:14px;background:rgba(255,255,255,.05);border:2px solid rgba(255,255,255,.07);text-align:center}
.stat b{display:block;font:400 22px/1 var(--font-display);color:var(--bone);font-variant-numeric:tabular-nums}
.stat b .y{color:var(--ink-hi)}
.stat b .c{color:var(--holy-hi)}
.stat b em{font-style:normal;color:var(--muted);padding:0 .14em}
.stat span{display:block;margin-top:6px;font:700 12px/1.15 var(--font-ui);color:var(--muted)}

@media (prefers-reduced-motion:reduce){
  .clock.hurry,.vsn.tick,.vsn.down{animation:none}
  .hint span,.btn,.tug i{transition:none}
  .orb{transition:none}
  .chip,.chip.wx.sun.burn,.ttrack span.full,.ttrack span.empty,.ttrack.nope,.slamBtn.press::before{animation:none}
  .orbptr i,.orbflash.on,.tube.giant .ttrack i,.tube.giant .tdrop,.tube.low,.vig.low,.vig.heat,.sheet,.tube.fill .ttrack i,.slamBtn,.slamBtn.ready,.tube.heat .tdrop,.tube.heat .ttrack i{animation:none}
  .logo,.dock,.card,.modal,.logo.paint .sf,.logo.paint .sx,.logo.paint .drip,.logo.paint .cw,.pchip.win svg,#cvName.pop{animation:none}
  .sw{transition:none}
}
"""
CSS = CSS.replace('__O2__', ring(2.2)).replace('__O3__', ring(3)).replace('__O4__', ring(4))
i = s.index('<style>') + len('<style>'); j = s.index('</style>')
s = s[:i] + CSS + s[j:]

# ---------- markup ----------
SW_BODY = "M16 34C70 18 150 26 236 20C316 14 392 22 446 16C462 22 466 40 456 52C468 64 464 86 452 98C396 108 330 100 256 108C186 116 108 106 44 114C24 116 10 106 16 92C4 82 6 58 16 48C10 44 10 38 16 34Z"
DRIPS = [("M99 96L99 150A14 14 0 1 0 121 150L121 96Z", '.34s'), ("M251 100L251 172A14 14 0 1 0 273 172L273 100Z", '.44s'), ("M380 94L380 128A12 12 0 1 0 398 128L398 94Z", '.54s')]
def layer(cls):
    return f'<g class="{cls}"><path d="{SW_BODY}"/>' + ''.join(f'<path class="drip" style="--dd:{dd}" d="{d}"/>' for d, dd in DRIPS) + '</g>'
SWASH = ('<svg class="swash" viewBox="0 0 470 200" aria-hidden="true">' + layer('sd') + layer('so') + layer('sf') +
         '<g class="sx"><path class="sh" d="M42 38C120 27 222 34 300 28C352 24 402 28 432 26"/><path class="sl" d="M60 92C150 98 240 88 330 93C370 95 410 90 436 86M110 66C200 72 290 62 404 68"/></g></svg>')

SHUF = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 7h3.5c2 0 3.2 1 4.3 2.6l2.4 3.8C14.3 15 15.5 16 17.5 16H21M3 16h3.5c1.4 0 2.4-.5 3.2-1.4M13.3 8.4c.8-.9 1.8-1.4 3.2-1.4H21M18 4l3 3-3 3M18 13l3 3-3 3" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
QM = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9.2" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M9.6 9.5a2.5 2.5 0 1 1 3.6 2.2c-.8.4-1.2 1-1.2 1.8v.5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="17" r="1.35" fill="currentColor"/></svg>'
CROWN = '<svg viewBox="0 0 30 24" aria-hidden="true"><path d="M3.5 20.5 2 7l7.2 5.2L15 3l5.8 9.2L28 7l-1.5 13.5z"/></svg>'

i = s.index('  <section class="sheet" id="menu">'); j = s.index('</div>\n\n<script')
NEW = f"""  <section class="menu" id="menu">
    <h1 class="logo paint" id="logo"><span class="l1">Paint the World</span><span class="l2">{SWASH}<span class="cw" id="logoWord">Red</span></span></h1>
    <div class="dock">
      <div class="swatches" id="swatches" role="group" aria-label="Your color"></div>
      <div class="seg" id="stages" role="group" aria-label="How good the holy water is"></div>
      <button class="btn play" id="startBtn" type="button">Play</button>
      <div class="mfoot">
        <button class="chipbtn" id="shuffleBtn" type="button" aria-label="Shuffle the canvas">{SHUF}<span id="cvName">The Studio</span></button>
        <button class="chipbtn" id="howBtn" type="button" aria-haspopup="dialog">{QM}<span>How to play</span></button>
      </div>
      <p class="note" id="menuNote" hidden></p>
    </div>
  </section>

  <div class="modal" id="howModal" hidden>
    <div class="card" role="dialog" aria-modal="true" aria-labelledby="howTitle">
      <h2 class="ctitle" id="howTitle">How to play</h2>
      <ul class="rules">
        <li><span class="dot hand">↔</span><span id="howCtl">Drag sideways to steer. Tap to jump, swipe up to roll. Hold to stop, then pull down and let go to fling. The arrow button pounds.</span></li>
        <li><span class="dot holy"></span><span>Cover more of the canvas than the holy water in 90 seconds. Paint over its color to take ground back.</span></li>
        <li><span class="dot ink"></span><span>Your color is a fast lane that refills your blood. Its color slows you down. Run dry and you crawl until a coffin or your own color fills you up.</span></li>
        <li><span class="dot hand">↓</span><span>Pound to splat a circle. Anything inside is out for a few seconds. Jump or roll to dodge one coming at you.</span></li>
        <li><span class="dot hand">➚</span><span>Fling into the holy water to knock it flying. Ram it while you're faster, or land on it, to flatten it.</span></li>
        <li><span class="dot sun"></span><span>Sunrise: hide in a coffin or a shadow. Rain: everyone speeds up and puddles water your paint down.</span></li>
        <li><span class="dot orbd"></span><span>Grab the glowing orb to go giant for 5 seconds.</span></li>
      </ul>
      <button class="btn play sm" id="howClose" type="button">Got it</button>
    </div>
  </div>

  <div class="modal" id="pause" hidden>
    <div class="card" role="dialog" aria-modal="true" aria-labelledby="pauseTitle">
      <h2 class="ctitle" id="pauseTitle">Paused</h2>
      <div class="pscore"><b class="you" id="pauseYou">0%</b><span id="pauseClock">1:30 left</span><b class="cpu" id="pauseCpu">0%</b></div>
      <button class="btn play sm" id="resumeBtn" type="button">Resume</button>
      <div class="row"><button class="btn" id="restartBtn" type="button">Restart</button><button class="btn" id="quitBtn" type="button">Menu</button></div>
    </div>
  </div>

  <section class="sheet" id="end" hidden>
    <h2 class="rtitle" id="endTitle">You win!</h2>
    <div class="endgrid">
      <figure class="frame" id="frame">
        <div class="wood"><img id="paintImg" alt="Top view of the canvas you painted this match"></div>
        <figcaption class="placard"><b id="pTitle">Nocturne in Crimson No. 1</b><span id="pMeta">Blood on canvas</span></figcaption>
      </figure>
      <div class="scores">
        <div class="pchip you" id="chipYou"><i></i><div><b id="endPct">0%</b><span>You</span></div>{CROWN}</div>
        <div class="pchip cpu" id="chipCpu"><i></i><div><b id="endPctC">0%</b><span>Holy water</span></div>{CROWN}</div>
        <span class="pill" id="endPill" hidden>New best</span>
      </div>
    </div>
    <div class="stats" id="endStats"></div>
    <button class="btn play two" id="endBtn" type="button"><span>Rematch</span><small>New canvas</small></button>
    <div class="row"><button class="btn" id="replayBtn" type="button">Same canvas</button><button class="btn" id="menuBtn" type="button">Menu</button></div>
  </section>
"""
s = s[:i] + NEW + s[j:]
open(F, 'w').write(s)
print('ok')
