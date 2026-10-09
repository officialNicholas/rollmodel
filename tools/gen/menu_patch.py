import re
P = '/home/claude/paint-the-canvas.html'
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/menu/'
s = open(P).read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)
art = {k: open(SP + f).read().strip() for k, f in [('std', 'art_studio.svg'), ('s1', 'art_halloween.svg'), ('next', 'art_next.svg')]}

# ---------------- HTML ----------------
a = s.index('  <section class="menu" id="menu">'); b = s.index('  </section>', a) + len('  </section>')
old = s[a:b]
logo = old[old.index('    <h1 class="logo paint" id="logo">'):old.index('</h1>') + 5]
grab = lambda i: old[old.index('<svg', old.index(i)):old.index('</svg>', old.index(i)) + 6]
ICON_LOOK, ICON_SHUF, ICON_HOW = grab('id="lookBtn"'), grab('id="shuffleBtn"'), grab('id="howBtn"')
NAMETAG = old[old.index('      <button class="nametag"'):old.index('</button>', old.index('<button class="nametag"')) + 9].strip()
new = '''  <section class="menu" id="menu" data-page="home">
    <div class="mhome" id="mHome">
      ''' + NAMETAG + '''
''' + logo + '''
      <div class="mcta" id="mCta">
        <button class="rbtn hot" id="lookBtn" type="button" aria-haspopup="dialog"><span class="rd">''' + ICON_LOOK + '''</span><span class="rl">Customize</span></button>
        <button class="bigplay" id="homePlay" type="button" aria-label="Play"><span class="bpr"></span><svg class="bpd" viewBox="0 0 100 100" aria-hidden="true"><path d="M33 76v13a4.5 4.5 0 0 0 9 0V76z"/><path d="M48 78v19a5 5 0 0 0 10 0V78z"/><path d="M63 74v9a4 4 0 0 0 8 0v-9z"/></svg><span class="bpc"><svg class="bpt" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.6v12.8a1.6 1.6 0 0 0 2.4 1.4l10-6.4a1.6 1.6 0 0 0 0-2.8l-10-6.4A1.6 1.6 0 0 0 8 5.6z"/></svg></span><span class="bpl" aria-hidden="true">Play</span></button>
        <button class="rbtn" id="howBtn" type="button" aria-haspopup="dialog"><span class="rd">''' + ICON_HOW + '''</span><span class="rl">How to play</span></button>
      </div>
    </div>
    <div class="mworld" id="mWorld" hidden>
      <div class="whead"><button class="ibtn back" id="worldBack" type="button" aria-label="Back to the title screen"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 5.5 8 12l6.5 6.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></button><h2 id="worldTitle">Pick a world</h2></div>
      <div class="seg" id="modes" role="group" aria-label="Game mode"></div>
      <div class="gallery" id="stagePick" role="group" aria-labelledby="worldTitle">
        <button class="world" type="button" data-s="standard"><span class="frame">''' + art['std'] + '''<i class="wcheck" aria-hidden="true"></i></span><span class="plaque"><b class="wn">The Studio</b><span class="wsub">Always open</span><span class="wst" data-w="std"></span></span></button>
        <button class="world" type="button" data-s="season"><span class="frame">''' + art['s1'] + '''<i class="wcheck" aria-hidden="true"></i></span><span class="ribbon">Season 1</span><span class="plaque"><b class="wn">Halloween</b><span class="wsub">Four haunted canvases</span><span class="wst" data-w="s1"></span></span></button>
        <button class="world locked" type="button" data-s="next" aria-disabled="true"><span class="frame">''' + art['next'] + '''</span><span class="ribbon soon">Season 2</span><span class="plaque"><b class="wn">Coming soon</b><span class="wsub">New canvases and accessories</span></span></button>
      </div>
      <div class="gdots" id="gDots" aria-hidden="true"><i></i><i></i><i></i></div>
      <div class="wfoot">
        <div class="seg" id="stages" role="group" aria-label="How good the CPUs are"></div>
        <p class="snote" id="soloNote" hidden></p>
        <div class="wgo"><button class="ibtn" id="shuffleBtn" type="button" aria-label="Shuffle the canvas" title="Shuffle the canvas">''' + ICON_SHUF + '''</button><button class="btn play two" id="startBtn" type="button"><span id="startWord">Play</span><small id="cvName">The Studio</small></button></div>
      </div>
    </div>
  </section>'''
s = s[:a] + new + s[b:]

# ---------------- CSS ----------------
rep("/* menu: the logo up top, your blob and the holy water in the middle (that's the 3D scene), one dock of controls at your thumb */\n.menu{position:absolute;inset:0;z-index:4;display:flex;flex-direction:column;align-items:center;justify-content:space-between;box-sizing:border-box;padding:max(62px,calc(env(safe-area-inset-top) + 50px)) 16px max(16px,env(safe-area-inset-bottom));pointer-events:none}",
"/* menu, part one: the title screen. The logo up top, the 3D canvas behind, and at your thumb one big glossy Play\n   dripping paint, with Customize and How to play on either side */\n.menu{position:absolute;inset:0;z-index:4;pointer-events:none}\n.mhome{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:space-between;box-sizing:border-box;padding:max(70px,calc(env(safe-area-inset-top) + 58px)) 16px max(62px,calc(env(safe-area-inset-bottom) + 50px))}\n.mhome::before{content:\"\";position:absolute;inset:0;z-index:-1;pointer-events:none;background:linear-gradient(180deg,rgba(14,7,30,.55) 0,rgba(14,7,30,0) 32%,rgba(14,7,30,0) 50%,rgba(14,7,30,.75) 100%)}")
rep(".dock{pointer-events:auto;width:min(100%,420px);box-sizing:border-box;display:grid;gap:14px;padding:16px;background:rgba(33,21,60,.96);border:3px solid var(--line);border-radius:28px;box-shadow:0 6px 0 var(--line),0 24px 48px rgba(6,2,16,.5);animation:dockin .55s .08s cubic-bezier(.25,1.3,.45,1) both}\n", "")
rep(".nametag{justify-self:center;margin:-38px 0 -2px;display:inline-flex;", ".nametag{position:absolute;top:max(12px,env(safe-area-inset-top));left:max(14px,env(safe-area-inset-left));z-index:1;pointer-events:auto;max-width:calc(100% - 100px);display:inline-flex;")
rep(".nametag{position:absolute;top:max(12px,env(safe-area-inset-top));left:max(14px,env(safe-area-inset-left));z-index:1;pointer-events:auto;max-width:calc(100% - 100px);display:inline-flex;align-items:center;gap:8px;max-width:100%;", ".nametag{position:absolute;top:max(12px,env(safe-area-inset-top));left:max(14px,env(safe-area-inset-left));z-index:1;pointer-events:auto;display:inline-flex;align-items:center;gap:8px;max-width:calc(100% - 100px);")
rep(".dock{grid-template-columns:minmax(0,1fr)}\n", "")
rep(".menu.looking .logo,.menu.looking .dock{visibility:hidden}", ".menu.looking .mhome{visibility:hidden}")
a = s.index("@media (min-width:860px) and (min-aspect-ratio:1/1){\n  .menu{align-items:flex-start;")
b = s.index("/* cards: how to play and pause sit over a dimmed game */")
s = s[:a] + r'''/* the big Play: a cream ring, a glossy disc in your paint, drips running over the ring. One idle cue: a soft halo */
.mcta{position:relative;display:grid;grid-template-columns:1fr auto 1fr;align-items:end;column-gap:clamp(12px,5vw,30px);width:min(100%,430px);pointer-events:none;animation:dockin .55s .08s cubic-bezier(.25,1.3,.45,1) both}
.mcta>*{pointer-events:auto}
.bigplay{appearance:none;position:relative;display:block;width:clamp(148px,42vw,188px);aspect-ratio:1/1;padding:0;border:0;border-radius:50%;background:none;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:transform .14s cubic-bezier(.3,1.6,.5,1)}
.bigplay::before{content:"";position:absolute;inset:-16px;border-radius:50%;background:radial-gradient(circle,rgba(var(--ink-rgb),.5) 30%,rgba(var(--ink-rgb),0) 70%);animation:halo 2.8s ease-in-out infinite;pointer-events:none}
@keyframes halo{0%,100%{opacity:.3;transform:scale(.92)}50%{opacity:.85;transform:scale(1.06)}}
.bpr{position:absolute;inset:0;border-radius:50%;background:radial-gradient(circle at 50% 26%,#FFFDF6 0,#F6EAD0 46%,#D8BE92 100%);border:4px solid var(--line);box-shadow:0 8px 0 var(--line),0 22px 40px rgba(6,2,16,.55),inset 0 -8px 0 rgba(140,96,40,.3),inset 0 5px 0 rgba(255,255,255,.9);transition:box-shadow .14s}
.bpd{position:absolute;inset:0;width:100%;height:100%;overflow:visible;fill:var(--ink);stroke:var(--line);stroke-width:2.6;stroke-linejoin:round}
.bpc{position:absolute;inset:13%;display:grid;place-items:center;overflow:hidden;border-radius:50%;background:radial-gradient(circle at 36% 28%,var(--ink-hi) 0,var(--ink) 48%,var(--ink-lo) 100%);border:4px solid var(--line);box-shadow:inset 0 -10px 0 rgba(0,0,0,.2),inset 0 4px 0 rgba(255,255,255,.3)}
.bpc::before{content:"";position:absolute;left:17%;right:17%;top:6%;height:36%;border-radius:50%;background:linear-gradient(180deg,rgba(255,255,255,.6),rgba(255,255,255,0))}
.bpt{position:relative;width:46%;height:46%;margin-left:8%;fill:var(--white);stroke:var(--outline);stroke-width:1.9;stroke-linejoin:round;filter:drop-shadow(0 3px 0 rgba(26,16,48,.5))}
.bpl{position:absolute;left:50%;top:calc(100% + 18px);transform:translateX(-50%);font:400 28px/1 var(--font-display);color:var(--bone);text-shadow:var(--o3),0 4px 0 var(--outline);white-space:nowrap;pointer-events:none}
.bigplay:hover{transform:translateY(-2px) scale(1.02)}
.bigplay:active{transform:translateY(6px) scale(.97)}
.bigplay:active .bpr{box-shadow:0 2px 0 var(--line),0 10px 22px rgba(6,2,16,.5),inset 0 -8px 0 rgba(140,96,40,.3),inset 0 5px 0 rgba(255,255,255,.9)}
.bigplay:focus-visible{outline:none}
.bigplay:focus-visible .bpr{outline:4px solid var(--gold);outline-offset:5px}
/* round buttons: a cream ring around a plum disc, labelled underneath */
.rbtn{appearance:none;display:grid;justify-items:center;gap:9px;margin-bottom:-4px;padding:0;border:0;background:none;color:var(--bone);cursor:pointer;font:800 14px/1.1 var(--font-ui);text-align:center;-webkit-tap-highlight-color:transparent}
#lookBtn{justify-self:end}
#howBtn{justify-self:start}
.rd{position:relative;display:grid;place-items:center;width:64px;height:64px;box-sizing:border-box;border-radius:50%;background:radial-gradient(circle at 50% 30%,#4E3C8A 0,#30225A 56%,#1E1440 100%);border:4px solid var(--bone);box-shadow:0 0 0 3.5px var(--line),0 6px 0 3.5px var(--line),0 14px 24px rgba(6,2,16,.5),inset 0 -5px 0 rgba(0,0,0,.28),inset 0 3px 0 rgba(255,255,255,.2);transition:transform .14s cubic-bezier(.3,1.6,.5,1),box-shadow .14s}
.rd svg{width:30px;height:30px;color:var(--bone)}
.rl{text-shadow:var(--o2),0 3px 0 var(--outline);white-space:nowrap}
.rbtn:hover .rd{transform:translateY(-2px)}
.rbtn:active .rd{transform:translateY(4px);box-shadow:0 0 0 3.5px var(--line),0 2px 0 3.5px var(--line),0 6px 14px rgba(6,2,16,.5),inset 0 -5px 0 rgba(0,0,0,.28),inset 0 3px 0 rgba(255,255,255,.2)}
.rbtn:focus-visible{outline:none}
.rbtn:focus-visible .rd{outline:3px solid var(--gold);outline-offset:6px}
.rbtn.hot .rd{border-color:var(--pumpkin)}
.rbtn.hot .rd svg{color:var(--pumpkin)}
.rbtn.hot .rd::after{content:"New";position:absolute;top:-11px;right:-20px;padding:4px 7px 5px;border-radius:99px;background:var(--pumpkin);border:2.5px solid var(--line);color:var(--outline);font:900 11px/1 var(--font-ui)}
/* small round icon buttons (back, shuffle) */
.ibtn{appearance:none;flex:none;display:grid;place-items:center;width:52px;height:52px;box-sizing:border-box;padding:0;border-radius:50%;background:radial-gradient(circle at 50% 30%,#4E3C8A 0,#30225A 56%,#1E1440 100%);border:3.5px solid var(--bone);box-shadow:0 0 0 3px var(--line),0 5px 0 3px var(--line);color:var(--bone);cursor:pointer;transition:transform .12s}
.ibtn svg{width:24px;height:24px}
.ibtn:active{transform:translateY(3px);box-shadow:0 0 0 3px var(--line),0 2px 0 3px var(--line)}
.ibtn:focus-visible{outline:3px solid var(--gold);outline-offset:5px}

/* menu, part two: the world select, a gallery wall. Each world is a framed painting with a museum plaque under it
   (your best and your wins there), lit by its own spotlight. The season's next world hangs under a dust sheet */
.mworld{position:absolute;inset:0;pointer-events:auto;display:grid;grid-template-columns:minmax(0,1fr);grid-template-rows:auto auto minmax(0,1fr) auto auto;justify-items:center;align-items:center;box-sizing:border-box;padding:max(12px,env(safe-area-inset-top)) 0 max(16px,calc(env(safe-area-inset-bottom) + 10px));
  background:radial-gradient(ellipse 85% 46% at 50% -6%,rgba(255,214,160,.2),rgba(255,214,160,0) 72%),radial-gradient(ellipse 120% 40% at 50% 112%,rgba(5,2,14,.75),rgba(5,2,14,0) 70%),url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='84' viewBox='0 0 64 84'%3E%3Cg fill='none' stroke='%23fff' stroke-opacity='.045' stroke-width='2.2' stroke-linecap='round'%3E%3Cpath d='M32 8c9 10 9 22 0 31-9-9-9-21 0-31zM32 39c10 4 16 12 16 22M32 39c-10 4-16 12-16 22M32 47v28'/%3E%3Ccircle cx='32' cy='61' r='4.5'/%3E%3Cpath d='M0 42c7 0 11-5 11-12M64 42c-7 0-11-5-11-12'/%3E%3C/g%3E%3C/svg%3E"),linear-gradient(180deg,#311A4D 0,#26133F 60%,#1B0D2E 100%);animation:fadein .22s ease-out}
.whead{width:100%;box-sizing:border-box;display:grid;grid-template-columns:56px 1fr 56px;align-items:center;padding:0 max(14px,env(safe-area-inset-left))}
.whead h2{margin:0;text-align:center;font:400 clamp(26px,7.4vw,38px)/1 var(--font-display);color:var(--bone);text-shadow:var(--o3),0 5px 0 var(--outline)}
.mworld #modes{width:min(calc(100% - 32px),420px);margin-top:14px}
.gallery{width:100%;min-height:0;height:100%;box-sizing:border-box;display:flex;align-items:center;gap:clamp(16px,5vw,36px);overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;padding:20px max(12vw,calc(50% - 165px)) 8px;scrollbar-width:none;overscroll-behavior-x:contain;touch-action:pan-x}
.gallery::-webkit-scrollbar{display:none}
.world{appearance:none;position:relative;flex:none;width:min(76vw,330px);display:grid;justify-items:center;gap:16px;padding:0;border:0;background:none;color:inherit;font:inherit;cursor:pointer;scroll-snap-align:center;-webkit-tap-highlight-color:transparent;animation:hang .5s cubic-bezier(.25,1.35,.45,1) both}
.world:nth-child(2){animation-delay:.06s}
.world:nth-child(3){animation-delay:.12s}
@keyframes hang{from{opacity:0;transform:translateY(26px) rotate(-1.5deg)}}
.world::before{content:"";position:absolute;left:-14%;right:-14%;top:-40px;height:78%;background:radial-gradient(ellipse 46% 62% at 50% 0,rgba(255,236,190,.34),rgba(255,236,190,0) 72%);opacity:.45;transition:opacity .25s;pointer-events:none}
.world[aria-pressed="true"]::before{opacity:1}
.frame{position:relative;display:block;width:100%;aspect-ratio:320/220;box-sizing:border-box;padding:12px;border-radius:9px;background:linear-gradient(135deg,#FFEFB8 0,#F1C45E 20%,#B8822C 46%,#F7D47C 68%,#9C681E 100%);border:3px solid var(--line);box-shadow:0 7px 0 var(--line),0 20px 32px rgba(5,2,14,.55),inset 0 2px 0 rgba(255,255,255,.65),inset 0 -2px 0 rgba(90,55,10,.5);transition:transform .22s cubic-bezier(.3,1.5,.5,1),box-shadow .22s}
.frame::before{content:"";position:absolute;inset:7px;border:2px solid rgba(98,60,12,.6);border-radius:4px;pointer-events:none}
.frame .art{display:block;width:100%;height:100%;border-radius:2px;box-shadow:0 0 0 3px var(--line)}
.world[aria-pressed="true"] .frame{transform:translateY(-6px);box-shadow:0 13px 0 var(--line),0 30px 44px rgba(5,2,14,.6),inset 0 2px 0 rgba(255,255,255,.65),inset 0 -2px 0 rgba(90,55,10,.5)}
.wcheck{position:absolute;top:-14px;right:-14px;width:38px;height:38px;border-radius:50%;background:var(--ink) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M6 12.5l4 4 8-9' fill='none' stroke='%23fff' stroke-width='3.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/24px no-repeat;border:3.5px solid var(--line);box-shadow:0 3px 0 var(--line);transform:scale(0);transition:transform .25s cubic-bezier(.3,1.7,.5,1)}
.world[aria-pressed="true"] .wcheck{transform:scale(1)}
.ribbon{position:absolute;top:-15px;left:50%;z-index:1;transform:translateX(-50%) rotate(-2deg);padding:6px 14px 7px;border-radius:8px;background:var(--pumpkin);border:3px solid var(--line);box-shadow:0 3px 0 var(--line);color:var(--white);font:400 15px/1 var(--font-display);text-shadow:var(--o2);white-space:nowrap}
.ribbon.soon{background:#6E69C8}
.world[aria-pressed="true"] .ribbon{top:-21px}
.plaque{display:grid;justify-items:center;gap:5px;min-width:74%;max-width:100%;box-sizing:border-box;padding:9px 16px 10px;border-radius:10px;background:linear-gradient(180deg,#FFF9EC,#EADBBF);border:3px solid var(--line);box-shadow:0 4px 0 var(--line),inset 0 2px 0 #fff;color:var(--outline);text-align:center}
.wn{font:400 21px/1 var(--font-display)}
.wsub{font:800 13px/1.2 var(--font-ui);color:#675780}
.wst{display:flex;flex-wrap:wrap;justify-content:center;gap:4px 12px;font:800 13px/1 var(--font-ui);color:var(--outline)}
.wst span{display:inline-flex;align-items:center;gap:5px}
.wst svg{width:15px;height:15px;flex:none}
.wst .wdrop{fill:var(--ink);stroke:var(--line);stroke-width:2}
.wst .wcrown{fill:var(--gold);stroke:var(--line);stroke-width:2.4;stroke-linejoin:round}
.wst em{font-style:normal;color:#675780}
.world.locked{cursor:default}
.world.locked .plaque{background:linear-gradient(180deg,#E6E0F2,#CFC6E3)}
.world.locked .wn{color:#3A3260}
.world.nudge .frame{animation:nudge .4s ease-in-out}
@keyframes nudge{20%{transform:rotate(-2.5deg)}50%{transform:rotate(2deg)}80%{transform:rotate(-1deg)}}
.world:focus-visible{outline:none}
.world:focus-visible .frame{outline:3px solid var(--gold);outline-offset:6px}
.gdots{display:flex;gap:9px;padding:6px 0 4px}
.gdots i{width:9px;height:9px;border-radius:50%;background:rgba(246,238,223,.28);transition:background .2s,transform .2s}
.gdots i.on{background:var(--bone);transform:scale(1.3)}
.wfoot{width:min(calc(100% - 32px),440px);display:grid;gap:12px;margin-top:8px}
.wgo{display:flex;align-items:center;gap:14px}
.wgo .btn.play{flex:1;width:auto}
.wgo .ibtn{width:58px;height:58px}
.btn.play:disabled{background:#4A3E68;color:#B3A6D6;cursor:default;text-shadow:none;box-shadow:inset 0 -6px 0 rgba(0,0,0,.2),0 5px 0 var(--line)}
.btn.play:disabled:active{transform:none}
@media (min-width:860px) and (min-aspect-ratio:1/1){
  .mhome{padding-top:max(56px,6vh);padding-bottom:max(84px,10vh)}
  .gallery{overflow:visible;justify-content:center;padding:34px 24px 10px;scroll-snap-type:none}
  .world{width:min(27vw,330px)}
  .gdots{display:none}
}
@media (max-height:520px) and (min-aspect-ratio:1/1){
  /* landscape phones: the logo beside Play, and the gallery in one row with the controls tucked around it */
  .mhome{flex-direction:row;justify-content:center;gap:clamp(16px,5vw,60px);padding:max(10px,env(safe-area-inset-top)) max(64px,calc(env(safe-area-inset-right) + 52px)) max(34px,calc(env(safe-area-inset-bottom) + 24px)) max(16px,env(safe-area-inset-left))}
  .logo .l1{font-size:min(44px,9.5vh,5.2vw)}
  .logo .l2{font-size:min(96px,19vh,8.5vw)}
  .bigplay{width:min(150px,36vh)}
  .bpl{font-size:22px;top:calc(100% + 12px)}
  .mcta{width:auto}
  .mworld{grid-template-columns:auto minmax(0,1fr);grid-template-rows:auto minmax(0,1fr) auto;padding:max(8px,env(safe-area-inset-top)) max(64px,calc(env(safe-area-inset-right) + 52px)) max(8px,env(safe-area-inset-bottom)) max(12px,env(safe-area-inset-left))}
  .whead{grid-template-columns:52px auto;gap:12px;padding:0}
  .whead h2{font-size:24px}
  .mworld #modes{width:min(100%,330px);margin:0;justify-self:end}
  .gallery{grid-column:1/-1;overflow:visible;justify-content:center;padding:18px 0 4px;scroll-snap-type:none;gap:22px}
  .world{width:min(26vw,30vh*1.45,250px);gap:10px}
  .frame{padding:8px}
  .plaque{padding:5px 10px 6px;gap:3px}
  .wn{font-size:16px}
  .wsub{display:none}
  .gdots{display:none}
  .wfoot{grid-column:1/-1;width:min(100%,640px);grid-template-columns:1fr 1.15fr;align-items:center;margin:0;gap:12px}
  .wfoot .snote{min-height:0}
  .seg button{min-height:34px}
  .btn.play{min-height:50px;font-size:24px}
  .wgo .ibtn{width:48px;height:48px}
}
''' + s[b:]

# reduced motion
rep("  .logo,.dock,.card,.modal,", "  .logo,.mcta,.world,.mworld,.bigplay::before,.card,.modal,")

# ---------------- JS ----------------
rep("  $('startBtn').textContent = 'Play';\n}", "}")
rep("""  $('cvName').textContent = TH.label; $('shuffleBtn').setAttribute('aria-label', 'Shuffle the canvas. Now: ' + TH.label);
}""", """  $('cvName').textContent = TH.label; $('shuffleBtn').setAttribute('aria-label', 'Shuffle the canvas. Now: ' + TH.label);
  renderWorlds();
}""")
rep("""$('stagePick').addEventListener('click', e => { const t = e.target.closest('button'); if (!t || t.dataset.s === stageSel || building) return; AU.init(); AU.ui(); stageSel = t.dataset.s; store.stage = stageSel; save();
  if (state === 'menu') { freshMap(); resetRun(); decorate(); menuPose(); kick($('cvName'), 'bump'); }
  renderStages(); });""",
"""// ---------- the world select: a gallery of framed paintings. On a phone it's a carousel, and the painting in the middle is the one you'll play ----------
let menuPage = 'home', galT = 0;
const gallery = $('stagePick'), worldBtns = [...gallery.querySelectorAll('.world')];
const W_DROP = '<svg class="wdrop" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.8c3.6 4.5 6.3 8 6.3 11.4a6.3 6.3 0 0 1-12.6 0c0-3.4 2.7-6.9 6.3-11.4z"/></svg>', W_CROWN = '<svg class="wcrown" viewBox="0 0 30 24" aria-hidden="true"><path d="M3.5 20.5 2 7l7.2 5.2L15 3l5.8 9.2L28 7l-1.5 13.5z"/></svg>';
const worldKey = () => GEN.std ? 'std' : 's' + SEASON.n;
const galScrolls = () => gallery.scrollWidth > gallery.clientWidth + 4;
function worldAt() { if (!galScrolls()) return null; const mid = gallery.scrollLeft + gallery.clientWidth / 2; let best = null, bd = 1e9; for (const b of worldBtns) { const d = Math.abs(b.offsetLeft + b.offsetWidth / 2 - mid); if (d < bd) { bd = d; best = b; } } return best; }
function renderWorlds() {
  const W = store.world || {};
  for (const b of worldBtns) {
    b.setAttribute('aria-pressed', String(b.dataset.s === stageSel));
    const st = b.querySelector('.wst'); if (!st) continue; const w = W[st.dataset.w];
    st.innerHTML = w && w.played ? '<span>' + W_DROP + '<em>Best</em> ' + w.best + '%</span><span>' + W_CROWN + w.wins + ' <em>' + (w.wins === 1 ? 'win' : 'wins') + '</em></span>' : '<span><em>No paintings yet</em></span>';
  }
  const at = worldAt(), locked = !!(at && at.dataset.s === 'next'), go = $('startBtn');
  go.disabled = locked; $('startWord').textContent = locked ? 'Coming soon' : 'Play';
  go.querySelector('small').hidden = locked; $('shuffleBtn').hidden = locked || stageSel !== 'season';
  const dots = $('gDots').children, idx = at ? worldBtns.indexOf(at) : worldBtns.findIndex(b => b.dataset.s === stageSel);
  for (let i = 0; i < dots.length; i++) dots[i].classList.toggle('on', i === idx);
}
function selectWorld(s) {
  if (s === stageSel || s === 'next' || building) return; AU.init(); AU.ui(); stageSel = s; store.stage = stageSel; save();
  renderStages();
  // the new canvas builds just after, so the tap answers first
  if (state === 'menu') setTimeout(() => { if (state !== 'menu' || building || stageSel !== s) return; freshMap(); resetRun(); decorate(); menuPose(); renderStages(); kick($('cvName'), 'bump'); }, 40);
}
function centerWorld(b, smooth) { if (!galScrolls() || !b) return; gallery.scrollTo({ left: b.offsetLeft + b.offsetWidth / 2 - gallery.clientWidth / 2, behavior: smooth ? 'smooth' : 'auto' }); }
gallery.addEventListener('click', e => {
  const t = e.target.closest('.world'); if (!t) return;
  if (t.dataset.s === 'next') { AU.init(); AU.nope(); t.classList.remove('nudge'); void t.offsetWidth; t.classList.add('nudge'); centerWorld(t, true); return; }
  centerWorld(t, true); selectWorld(t.dataset.s); renderWorlds();
});
gallery.addEventListener('scroll', () => { renderWorlds(); clearTimeout(galT); galT = setTimeout(() => { const b = worldAt(); if (b && b.dataset.s !== 'next' && b.dataset.s !== stageSel) selectWorld(b.dataset.s); renderWorlds(); }, 140); }, { passive: true });
function openWorlds() {
  if (state !== 'menu' || building || lookOpen || menuPage === 'worlds') return;
  menuPage = 'worlds'; menu.dataset.page = 'worlds'; $('mHome').hidden = true; $('mWorld').hidden = false;
  renderModes(); renderStages();
  centerWorld(worldBtns.find(b => b.dataset.s === stageSel), false); renderWorlds();
  setTimeout(() => $('startBtn').focus({ preventScroll: true }), 40);
}
function closeWorlds() {
  if (menuPage !== 'worlds') return; menuPage = 'home'; menu.dataset.page = 'home'; $('mWorld').hidden = true; $('mHome').hidden = false; heroT = 0;
  setTimeout(() => $('homePlay').focus({ preventScroll: true }), 30);
}
function stepWorld(dir) { const open = worldBtns.filter(b => b.dataset.s !== 'next'), i = open.findIndex(b => b.dataset.s === stageSel), b = open[clamp(i + dir, 0, open.length - 1)]; if (b) { centerWorld(b, true); selectWorld(b.dataset.s); renderWorlds(); } }
$('homePlay').addEventListener('click', () => { AU.init(); AU.ui(); openWorlds(); });
$('worldBack').addEventListener('click', () => { AU.init(); AU.ui(); closeWorlds(); });
window.addEventListener('resize', () => { if (menuPage === 'worlds') { centerWorld(worldBtns.find(b => b.dataset.s === stageSel), false); renderWorlds(); } });""")
# hero framing follows the new title screen
rep("const r = stage.getBoundingClientRect(), d = menu.querySelector('.dock').getBoundingClientRect(), l = $('logo').getBoundingClientRect(), W = r.width, Hh = r.height;\n  if (!(d.height > 0)) return heroDist;\n  const side = sideMQ.matches; let tx, ty, freeW;",
    "const r = stage.getBoundingClientRect(), d = $('mCta').getBoundingClientRect(), l = $('logo').getBoundingClientRect(), W = r.width, Hh = r.height;\n  if (!(d.height > 0)) return heroDist;\n  const side = false; let tx, ty, freeW;")
# showMenu lands on the title screen
rep("function showMenu() {\n  state = 'menu'; applyMode(); renderModes(); menu.hidden = false;", "function showMenu() {\n  state = 'menu'; menuPage = 'home'; menu.dataset.page = 'home'; $('mHome').hidden = false; $('mWorld').hidden = true; applyMode(); renderModes(); menu.hidden = false;")
# per-world stats
rep("  if (newBest) store.bestCov[slot] = ry;\n  endInfo.newBest = newBest;",
    "  if (newBest) store.bestCov[slot] = ry;\n  endInfo.newBest = newBest;\n  store.world = store.world || {}; const wk = worldKey(), wr = store.world[wk] = store.world[wk] || { best: 0, wins: 0, played: 0 }; // and a best and a win count per world, for its plaque\n  wr.played++; if (ry > wr.best) wr.best = ry; if (win > 0 && mode !== 'solo') wr.wins++;")
# keys: Esc steps back from the gallery, Enter goes forward, arrows walk the gallery
rep("  if (!howModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeHow(); } return; }",
    "  if (!howModal.hidden) { if (k === 'Escape') { e.preventDefault(); closeHow(); } return; }\n  if (state === 'menu' && menuPage === 'worlds') { if (k === 'Escape' || k === 'Backspace') { e.preventDefault(); closeWorlds(); return; } if ((k === 'ArrowLeft' || k === 'ArrowRight') && !e.repeat) { e.preventDefault(); stepWorld(k === 'ArrowLeft' ? -1 : 1); return; } }")
rep("    if (state === 'menu') { if (!store.name) openName(true); else start(); }", "    if (state === 'menu') { if (menuPage === 'home') openWorlds(); else if ($('startBtn').disabled) return; else if (!store.name) openName(true); else start(); }")
# the gallery covers the 3D canvas: no need to draw it underneath
rep("  if (shadowLite >= 2) sun.shadow.needsUpdate = (++frameNo & 1) === 0;\n  renderFrame();", "  if (shadowLite >= 2) sun.shadow.needsUpdate = (++frameNo & 1) === 0;\n  if (!(state === 'menu' && menuPage === 'worlds')) renderFrame();")
open(P, 'w').write(s); print('ok', len(s))
