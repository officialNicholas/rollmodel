"""v443: the lesson, rethought (the user: "instead of slowing the game down to teach in the tutorial and instead of words popping up
during the match (because players don't have enough time to read) let's maybe stop the game and show visuals like a gif of what the
action does, and how to swipe ... first we are teaching how to move, so we do left and right and jumping. Then it shows a sensitivity
bar and invert, then shows a few hold rings from time trials. Basin. then the rival appears. Ground pound and dodging. That's it. It
needs to be very responsive, fun, not annoying and quick ... It needs to teach slingshotting too").

- Nothing is slowed down and nothing is said in the middle of play any more. Each lesson starts with the game stopped on a card: a
  title, a little looping scene of the move (the character from behind as the camera sees it, the floor rolling by) with a finger acting
  out the gesture in step with it, and a few words under it. Go (or a tap anywhere) and you're straight back in to do it. A row of dots
  shows how far along you are.
- The lessons, in order: Move (two scenes side by side: drag to steer, tap to jump); Your steering (the Turning bar and Invert steering,
  live, the same as in Settings); Rings (three of the time trial's gold rings come up ahead of you one after another, steer through
  them); Slingshot (hold, pull down, let go); Out of paint? (your tank runs dry and a basin comes up ahead: roll in, tap to hop out);
  then the rival climbs out of its basin; Ground pound (get close, tap Pound); Dodge (swipe up just before its pound lands). Then the
  match ends on Basics Complete. The orb and rocket lesson is gone.
- The two moves that are about timing stop the game at the moment itself: when the rival is in reach the game stops with the Pound
  button lit and a finger tapping it ("Tap!"), and tapping it pounds; when its pound is about to land the game stops on you with a
  finger swiping up ("Swipe up!"), and the swipe rolls you clear. Each of these comes at most twice.
- Left a few seconds without doing what a card showed, a finger acts it out over the game (no words); it goes once you do. Still in a
  tub after a knock-out, the finger shows the swipe out (it said so in words before).
- With a keyboard the words name the keys (A and D, SPACE, S, E, SHIFT) and the fingers are left out."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v443) the lesson's cards: the game stopped, a looping little scene of the move with a finger acting out the gesture */
.tlsn{position:absolute;inset:0;z-index:63;display:grid;place-items:center;padding:max(14px,env(safe-area-inset-top)) max(16px,env(safe-area-inset-right)) max(14px,env(safe-area-inset-bottom)) max(16px,env(safe-area-inset-left));box-sizing:border-box;background:rgba(23,19,32,.6);opacity:0;transition:opacity .16s;touch-action:none;-webkit-tap-highlight-color:transparent}
.tlsn.on{opacity:1}
.tlcard{position:relative;display:grid;justify-items:center;gap:10px;width:min(100%,400px);box-sizing:border-box;padding:14px 16px 16px;border-radius:18px;color:#fff;text-align:center;background:repeating-linear-gradient(-56deg,rgba(14,12,20,.97) 0 18px,rgba(44,40,54,.97) 18px 36px);box-shadow:0 0 0 2px rgba(255,255,255,.12),0 18px 40px rgba(0,0,0,.5)}
.tlsn.on .tlcard{animation:tutin .32s cubic-bezier(.2,1.2,.4,1) both}
.tldots{display:flex;gap:6px}
.tldots i{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.22)}
.tldots i.done{background:#3BE889}
.tldots i.now{background:#FFD23F;box-shadow:0 0 0 3px rgba(255,210,63,.28)}
.tlcard h2{margin:0;font:400 clamp(28px,7.5vw,38px)/1 var(--font-display);text-transform:uppercase;letter-spacing:.01em;color:#fff;-webkit-text-stroke:1.5px #2A1B4F;paint-order:stroke fill;text-shadow:0 4px 0 #2A1B4F}
.tlvis{display:grid;grid-template-columns:1fr;gap:10px;width:100%}
.tlvis.two{grid-template-columns:1fr 1fr}
.tlpan{display:grid;gap:8px;justify-items:center;align-content:start;min-width:0}
.tll{margin:0;font:400 17px/1.15 var(--font-display);color:#FFE08A;text-shadow:2px 2px 0 rgba(0,0,0,.7);text-wrap:balance}
.tlvis.two .tll{font-size:15.5px}
.tlgo{width:min(100%,240px)}
@media (max-height:520px) and (min-aspect-ratio:1/1){.tlcard{width:min(100%,560px);gap:7px;padding:10px 16px 12px}.tlcard h2{font-size:28px}.tlvis .tv{aspect-ratio:2/1}.tlvis.two .tv{aspect-ratio:4/3}.tlvis.two{width:min(100%,430px)}.tlvis:not(.two){width:min(100%,360px,calc((100vh - 200px) * 2))}.tll{font-size:15px}}
/* the scene: dark sky, the floor in perspective rolling toward you, you from behind (as the camera has you) */
.tv{position:relative;width:100%;aspect-ratio:16/10;border-radius:14px;overflow:hidden;background:linear-gradient(180deg,#5A4F78 0%,#3A3352 34%,#2A2539 100%);box-shadow:0 0 0 3px #171320,inset 0 0 0 2px rgba(255,255,255,.08);isolation:isolate;--pc:#E3122F;--rc:#2E7BFF}
.tlvis.two .tv{aspect-ratio:1/1}
.tv>i{position:absolute;display:block;font-style:normal}
.tvf{left:-80%;right:-80%;bottom:0;height:400%;transform-origin:50% 100%;transform:perspective(300px) rotateX(58deg);background-color:#EDE3D2;background-image:linear-gradient(rgba(23,19,32,.15) 2px,transparent 2px),linear-gradient(90deg,rgba(23,19,32,.15) 2px,transparent 2px);background-size:46px 46px;animation:tvroll .42s linear infinite}
@keyframes tvroll{from{background-position:0 0}to{background-position:0 46px}}
.tvme{left:50%;bottom:11%;width:21%;aspect-ratio:1;margin-left:-10.5%;z-index:3;border-radius:50%;background:radial-gradient(circle at 36% 30%,rgba(255,255,255,.6) 0 9%,rgba(255,255,255,0) 26%),radial-gradient(circle at 50% 120%,rgba(0,0,0,.22),rgba(0,0,0,0) 60%),var(--pc);box-shadow:0 0 0 3px #171320;animation:tvbob .42s ease-in-out infinite alternate}
.tvme::before,.tvme::after{content:"";position:absolute;top:-6%;width:34%;height:26%;border-radius:50% 50% 40% 40%;background:#FF9EC4;box-shadow:0 0 0 2.5px #171320}
.tvme::before{left:-14%;transform:rotate(-34deg)}
.tvme::after{right:-14%;transform:rotate(34deg)}
@keyframes tvbob{from{translate:0 0}to{translate:0 -4%}}
.tvsh{left:50%;bottom:8%;width:23%;height:7%;margin-left:-11.5%;z-index:2;border-radius:50%;background:rgba(23,19,32,.3)}
.tvh{left:50%;top:84%;width:21%;aspect-ratio:64/84;z-index:9;pointer-events:none}
.tlvis.two .tvh{width:27%}
.tvh svg{position:absolute;left:-43%;top:-95%;width:100%;height:100%;overflow:visible}
.tlsn.keys .tvh,.tlsn.keys .tvr,.tlsn.keys .tvtr{display:none!important}
.tvr{width:16%;aspect-ratio:1;margin:-8% 0 0 -8%;z-index:8;border-radius:50%;border:3.5px solid #fff;box-shadow:0 0 0 2px rgba(23,19,32,.45);opacity:0}
.tvtr{height:5px;border-radius:5px;z-index:8;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.85),rgba(255,255,255,0))}
.tvrv{left:50%;bottom:46%;width:18%;aspect-ratio:1;margin-left:-9%;z-index:2;border-radius:50%;background:radial-gradient(circle at 30% 28%,rgba(255,255,255,.5) 0 8%,rgba(255,255,255,0) 24%),var(--rc);box-shadow:0 0 0 3px #171320}
.tvrv::before,.tvrv::after{content:"";position:absolute;top:30%;width:22%;height:30%;border-radius:50%;background:#fff;box-shadow:0 0 0 2px #171320;background-image:radial-gradient(circle at 50% 62%,#171320 0 36%,transparent 38%)}
.tvrv::before{left:22%}
.tvrv::after{right:22%}
/* steer: the stick of the finger left and right, you lean into it, the floor swings round */
.tv[data-v="steer"] .tvf{animation:tvroll .42s linear infinite,tvswing 2.6s ease-in-out infinite}
@keyframes tvswing{0%,100%{transform:perspective(300px) rotateX(58deg) rotateZ(0)}25%{transform:perspective(300px) rotateX(58deg) rotateZ(-16deg)}75%{transform:perspective(300px) rotateX(58deg) rotateZ(16deg)}}
.tv[data-v="steer"] .tvme{animation:tvbob .42s ease-in-out infinite alternate,tvlean 2.6s ease-in-out infinite}
@keyframes tvlean{0%,100%{transform:translateX(0) rotate(0)}25%{transform:translateX(26%) rotate(14deg)}75%{transform:translateX(-26%) rotate(-14deg)}}
.tv[data-v="steer"] .tvsh{animation:tvshlean 2.6s ease-in-out infinite}
@keyframes tvshlean{0%,100%{transform:translateX(0)}25%{transform:translateX(24%)}75%{transform:translateX(-24%)}}
.tv[data-v="steer"] .tvme{bottom:30%}.tv[data-v="steer"] .tvsh{bottom:27%}
.tv[data-v="steer"] .tvh{top:95%;animation:tvhsteer 2.6s ease-in-out infinite}
@keyframes tvhsteer{0%,100%{left:50%}25%{left:76%}75%{left:24%}}
.tv[data-v="steer"] .tvtr{left:18%;right:18%;top:93%;opacity:.55}
/* jump: a tap, a hop */
.tv[data-v="jump"] .tvme{animation:tvhop 2.2s cubic-bezier(.3,0,.3,1) infinite}
@keyframes tvhop{0%,30%{transform:translateY(0) scale(1)}35%{transform:translateY(0) scale(1.16,.82)}44%{transform:translateY(-120%) scale(.94,1.06)}58%{transform:translateY(-135%) scale(1)}70%{transform:translateY(0) scale(1.2,.78)}78%,100%{transform:translateY(0) scale(1)}}
.tv[data-v="jump"] .tvsh{animation:tvhopsh 2.2s cubic-bezier(.3,0,.3,1) infinite}
@keyframes tvhopsh{0%,35%,72%,100%{transform:scale(1);opacity:1}48%,60%{transform:scale(.55);opacity:.5}}
.tv[data-v="jump"] .tvh{left:74%;top:66%;animation:tvhtap 2.2s ease-in-out infinite}
@keyframes tvhtap{0%,20%{transform:translateY(-14%) scale(1)}30%{transform:translateY(4%) scale(.92)}40%,100%{transform:translateY(-14%) scale(1)}}
.tv[data-v="jump"] .tvr{left:74%;top:66%;animation:tvring 2.2s ease-out infinite}
@keyframes tvring{0%,28%{opacity:0;transform:scale(.3)}31%{opacity:1;transform:scale(.45)}55%,100%{opacity:0;transform:scale(1.7)}}
/* rings: a gold arch comes up the floor at you and you roll through it */
.tvarch{left:50%;bottom:9%;width:46%;aspect-ratio:100/64;z-index:4;transform-origin:50% 100%;opacity:0;animation:tvarch 2.4s cubic-bezier(.45,0,.75,1) infinite}
.tvarch svg{width:100%;height:100%;overflow:visible;filter:drop-shadow(0 0 6px rgba(255,200,60,.7))}
@keyframes tvarch{0%{opacity:0;transform:translate(-50%,-123%) scale(.18)}8%{opacity:1}60%{opacity:1;transform:translate(-50%,-10%) scale(.9)}72%{opacity:1;transform:translate(-50%,12%) scale(1.3)}84%,100%{opacity:0;transform:translate(-50%,50%) scale(1.9)}}
.tv[data-v="rings"] .tvme{animation:tvbob .42s ease-in-out infinite alternate,tvdrift 2.4s ease-in-out infinite}
@keyframes tvdrift{0%,100%{transform:translateX(0)}30%{transform:translateX(-12%)}60%{transform:translateX(0)}}
.tvburst{left:50%;bottom:11%;width:40%;aspect-ratio:1;margin-left:-20%;z-index:5;border-radius:50%;border:4px dashed #FFD23F;opacity:0;animation:tvburst 2.4s ease-out infinite}
@keyframes tvburst{0%,68%{opacity:0;transform:scale(.4) rotate(0)}72%{opacity:1}92%,100%{opacity:0;transform:scale(1.9) rotate(40deg)}}
/* slingshot: press, pull down, let go, and away */
.tv[data-v="sling"] .tvme{animation:tvsling 2.8s cubic-bezier(.3,0,.3,1) infinite}
@keyframes tvsling{0%,10%{transform:translateY(0) scale(1);opacity:1}44%{transform:translateY(14%) scale(1.1,.86);opacity:1}50%{transform:translateY(0) scale(.9,1.12);opacity:1}74%{transform:translateY(-190%) scale(.35);opacity:1}80%{transform:translateY(-215%) scale(.28);opacity:0}86%{transform:translateY(0) scale(.6);opacity:0}96%,100%{transform:translateY(0) scale(1);opacity:1}}
.tv[data-v="sling"] .tvsh{animation:tvslingsh 2.8s cubic-bezier(.3,0,.3,1) infinite}
@keyframes tvslingsh{0%,48%{opacity:1;transform:none}74%{opacity:0;transform:translateY(-170%) scale(.3)}86%{opacity:0;transform:none}96%,100%{opacity:1;transform:none}}
.tvpin{left:60%;top:46%;width:13%;aspect-ratio:1;margin:-6.5% 0 0 -6.5%;z-index:7;border-radius:50%;border:4px solid var(--pc);box-shadow:0 0 0 2.5px #171320,inset 0 0 0 2px #171320;opacity:0;animation:tvpin 2.8s ease-out infinite}
@keyframes tvpin{0%,7%{opacity:0;transform:scale(.4)}11%,46%{opacity:1;transform:scale(1)}52%,100%{opacity:0;transform:scale(1.5)}}
.tvband{left:60%;top:46%;width:7px;margin-left:-3.5px;height:0;z-index:6;border-radius:5px;background:var(--pc);box-shadow:0 0 0 2.5px #171320;animation:tvband 2.8s cubic-bezier(.3,0,.3,1) infinite}
@keyframes tvband{0%,9%{height:0;opacity:0}10%{opacity:1}44%{height:30%;opacity:1}47%{opacity:1}48%,100%{height:0;opacity:0}}
.tv[data-v="sling"] .tvh{left:60%;top:46%;animation:tvhpull 2.8s cubic-bezier(.3,0,.3,1) infinite}
@keyframes tvhpull{0%{top:40%;opacity:0}6%{top:44%;opacity:1}10%{top:46%;transform:scale(.94)}44%{top:76%;transform:scale(.94);opacity:1}50%{top:72%;transform:scale(1);opacity:0}100%{top:40%;opacity:0}}
.tvlines{left:30%;right:30%;top:8%;bottom:30%;z-index:1;opacity:0;background:repeating-linear-gradient(90deg,transparent 0 16%,rgba(255,255,255,.6) 16% 18%,transparent 18% 34%);-webkit-mask:linear-gradient(transparent,#000 40%,#000 70%,transparent);mask:linear-gradient(transparent,#000 40%,#000 70%,transparent);animation:tvlines 2.8s linear infinite}
@keyframes tvlines{0%,50%{opacity:0;transform:translateY(-20%)}56%{opacity:1}76%{opacity:.8;transform:translateY(20%)}82%,100%{opacity:0;transform:translateY(30%)}}
/* out of paint: the tank runs dry, a basin comes up, in you go, the tank fills, a tap and out you hop */
.tvtank{left:6%;top:7%;width:38%;height:10%;z-index:6;border-radius:6px;background:#171320;box-shadow:0 0 0 2px rgba(255,255,255,.35);overflow:hidden}
.tvtank i{position:absolute;left:3px;top:3px;bottom:3px;width:calc(100% - 6px);border-radius:3px;background:#FFC21A;transform-origin:0 50%;animation:tvtank 3.6s linear infinite}
@keyframes tvtank{0%{transform:scaleX(1);background:#FFC21A}20%{transform:scaleX(.08);background:#FF4A4A}24%,56%{transform:scaleX(0);background:#FF4A4A}57%{background:#3BE889;transform:scaleX(0)}72%,100%{transform:scaleX(1);background:#3BE889}}
.tvtub,.tvtubf{left:50%;bottom:4%;width:46%;aspect-ratio:100/52;transform-origin:50% 100%;animation:tvtub 3.6s cubic-bezier(.4,0,.6,1) infinite}
.tvtub{z-index:2}
.tvtubf{z-index:4}
.tvtub svg,.tvtubf svg{width:100%;height:100%;overflow:visible}
@keyframes tvtub{0%{opacity:0;transform:translate(-50%,-165%) scale(.25)}8%{opacity:1}36%,80%{opacity:1;transform:translate(-50%,0) scale(1)}92%,100%{opacity:0;transform:translate(-50%,60%) scale(1.6)}}
.tv[data-v="basin"] .tvme{animation:tvdip 3.6s cubic-bezier(.4,0,.6,1) infinite}
@keyframes tvdip{0%,34%{transform:translateY(0) scale(1)}42%{transform:translateY(-30%) scale(.92)}48%,72%{transform:translateY(34%) scale(.82)}78%{transform:translateY(-110%) scale(1)}86%,100%{transform:translateY(0) scale(1)}}
.tv[data-v="basin"] .tvsh{animation:tvdipsh 3.6s linear infinite}
@keyframes tvdipsh{0%,38%,84%,100%{opacity:1}42%,80%{opacity:0}}
.tv[data-v="basin"] .tvh{left:78%;top:58%;animation:tvhtapb 3.6s ease-in-out infinite}
@keyframes tvhtapb{0%,58%{opacity:0;transform:translateY(-14%)}64%{opacity:1;transform:translateY(-14%)}72%{transform:translateY(4%) scale(.92)}78%{transform:translateY(-14%) scale(1);opacity:1}86%,100%{opacity:0}}
.tv[data-v="basin"] .tvr{left:78%;top:58%;animation:tvringb 3.6s ease-out infinite}
@keyframes tvringb{0%,71%{opacity:0;transform:scale(.3)}73%{opacity:1;transform:scale(.45)}90%,100%{opacity:0;transform:scale(1.7)}}
/* ground pound: tap Pound, up you go and down on him, splat */
.tvpb{right:5%;bottom:6%;width:22%;aspect-ratio:1;z-index:6;border-radius:50%;background:url(art/m_dot.webp) center/100% 100% no-repeat;filter:drop-shadow(2px 3px 0 rgba(23,19,32,.35));display:grid!important;place-items:center;animation:tvpb 2.8s ease-in-out infinite}
.tvpb svg{width:52%;height:52%;fill:#fff}
@keyframes tvpb{0%,22%,32%,100%{transform:scale(1)}26%{transform:scale(.88)}}
.tv[data-v="pound"] .tvh{left:84%;top:84%;animation:tvhtapp 2.8s ease-in-out infinite}
@keyframes tvhtapp{0%{opacity:0;transform:translateY(-16%)}10%{opacity:1;transform:translateY(-16%)}24%{transform:translateY(4%) scale(.92)}32%{transform:translateY(-16%) scale(1);opacity:1}42%,100%{opacity:0}}
.tv[data-v="pound"] .tvr{left:84%;top:84%;animation:tvringp 2.8s ease-out infinite}
@keyframes tvringp{0%,23%{opacity:0;transform:scale(.3)}25%{opacity:1;transform:scale(.45)}45%,100%{opacity:0;transform:scale(1.7)}}
.tv[data-v="pound"] .tvme{animation:tvpound 2.8s cubic-bezier(.3,0,.3,1) infinite}
@keyframes tvpound{0%,26%{transform:translateY(0) scale(1)}40%{transform:translateY(-105%) scale(.95,1.08)}46%{transform:translateY(-112%) scale(1)}50%{transform:translateY(0) scale(1.3,.7)}58%,100%{transform:translateY(0) scale(1)}}
.tvsplat{left:50%;bottom:9%;width:30%;aspect-ratio:2/1;margin-left:-15%;z-index:1;border-radius:50%;background:radial-gradient(closest-side,var(--pc) 0 70%,transparent 72%);opacity:0;animation:tvsplat 2.8s ease-out infinite}
@keyframes tvsplat{0%,48%{opacity:0;transform:scale(.2)}50%{opacity:1;transform:scale(.6)}62%{opacity:.95;transform:scale(2.9)}90%{opacity:.85;transform:scale(3.1)}100%{opacity:0;transform:scale(3.1)}}
.tv[data-v="pound"] .tvrv{left:31%;bottom:40%;width:16%;margin-left:-8%;animation:tvsquash 2.8s ease-out infinite}
.tv[data-v="pound"] .tvstars{left:31%;bottom:50%}
@keyframes tvsquash{0%,50%{transform:scale(1)}54%,88%{transform:translateY(34%) scale(1.5,.3)}96%,100%{transform:scale(1)}}
.tvstars{left:50%;bottom:45%;width:24%;height:12%;margin-left:-12%;z-index:5;opacity:0;background:radial-gradient(circle,#FFD23F 0 24%,transparent 26%) 0 50%/33% 100% repeat-x;animation:tvstars 2.8s linear infinite}
@keyframes tvstars{0%,54%{opacity:0;transform:rotate(0)}58%,86%{opacity:1;transform:rotate(14deg)}90%,100%{opacity:0}}
/* dodge: he leaps up, the red ring's on you, swipe up and roll clear, he lands on nothing */
.tv[data-v="dodge"] .tvrv{width:16%;margin-left:-8%;animation:tvleap 2.8s cubic-bezier(.4,0,.6,1) infinite}
@keyframes tvleap{0%,12%{bottom:56%;transform:scale(1);opacity:1}18%{bottom:56%;transform:scale(1.15,.8)}36%{bottom:92%;transform:scale(1.2)}54%{bottom:12%;transform:scale(1.5,1.2)}58%{bottom:12%;transform:scale(1.9,.9)}84%{bottom:12%;transform:scale(1.5,1.2);opacity:1}92%{bottom:56%;transform:scale(1);opacity:0}100%{bottom:56%;transform:scale(1);opacity:1}}
.tvwarn{left:50%;bottom:6%;width:36%;aspect-ratio:2/1;margin-left:-18%;z-index:1;border-radius:50%;border:4px solid #FF3B4E;background:rgba(255,59,78,.18);opacity:0;animation:tvwarn 2.8s linear infinite}
@keyframes tvwarn{0%,22%{opacity:0;transform:scale(.5)}30%,52%{opacity:1;transform:scale(1)}40%{opacity:.6}54%,100%{opacity:0;transform:scale(1.1)}}
.tv[data-v="dodge"] .tvsplat{background:radial-gradient(closest-side,var(--rc) 0 70%,transparent 72%);animation:tvsplatd 2.8s ease-out infinite}
@keyframes tvsplatd{0%,53%{opacity:0;transform:scale(.3)}56%{opacity:1;transform:scale(1.4)}64%,86%{opacity:.9;transform:scale(1.9)}96%,100%{opacity:0;transform:scale(1.9)}}
.tv[data-v="dodge"] .tvme{animation:tvroll2 2.8s cubic-bezier(.3,0,.3,1) infinite}
@keyframes tvroll2{0%,40%{left:50%;bottom:11%;transform:rotate(0);opacity:1}54%{left:22%;bottom:22%;transform:rotate(-340deg) scale(.9,1.05)}60%,88%{left:22%;bottom:22%;transform:rotate(-360deg);opacity:1}94%{left:22%;bottom:22%;opacity:0}95%{left:50%;bottom:11%;transform:rotate(0);opacity:0}100%{left:50%;bottom:11%;opacity:1}}
.tv[data-v="dodge"] .tvsh{animation:tvroll2sh 2.8s cubic-bezier(.3,0,.3,1) infinite}
@keyframes tvroll2sh{0%,40%{left:50%;bottom:8%;opacity:1}54%,88%{left:22%;bottom:19%;opacity:1}94%{opacity:0}95%{left:50%;bottom:8%;opacity:0}100%{left:50%;bottom:8%;opacity:1}}
.tv[data-v="dodge"] .tvh{left:56%;top:86%;animation:tvhswipe 2.8s cubic-bezier(.3,0,.2,1) infinite}
@keyframes tvhswipe{0%,30%{top:88%;opacity:0}36%{top:88%;opacity:1}46%{top:58%;opacity:1}52%,100%{top:54%;opacity:0}}
.tv[data-v="dodge"] .tvtr{left:56%;top:58%;width:5px;height:30%;margin-left:-2.5px;background:linear-gradient(0deg,rgba(255,255,255,0),rgba(255,255,255,.9));opacity:0;animation:tvtrswipe 2.8s linear infinite}
@keyframes tvtrswipe{0%,40%{opacity:0}46%{opacity:.9}56%,100%{opacity:0}}
/* Your steering: the Turning bar and Invert steering, live */
.tltune{display:grid;gap:9px;width:100%;padding:4px 2px 0;box-sizing:border-box;text-align:left}
.tlrow{display:flex;align-items:baseline;justify-content:space-between;gap:10px}
.tlk{font:400 15px/1 var(--font-display);text-transform:uppercase;letter-spacing:.03em;color:#fff;text-shadow:2px 2px 0 rgba(0,0,0,.6)}
.tlpct{font:400 15px/1 var(--font-display);color:#171320;background:#FFD23F;border-radius:7px;padding:5px 9px 4px;box-shadow:0 0 0 2px #171320;transform:skewX(-6deg)}
.tlrng{display:flex;align-items:center;gap:10px}
.tlrng span{font:400 12.5px/1 var(--font-display);text-transform:uppercase;color:rgba(255,255,255,.55)}
.tlrange{--v:41.7%;flex:1;min-width:0;-webkit-appearance:none;appearance:none;height:30px;margin:0;padding:0;background:none;cursor:pointer;touch-action:pan-y}
.tlrange:focus{outline:none}
.tlrange::-webkit-slider-runnable-track{height:16px;border-radius:9px;background:linear-gradient(90deg,#F2C14E 0,#FFE08A var(--v),#28243A var(--v));box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(0,0,0,.3)}
.tlrange::-moz-range-track{height:16px;border-radius:9px;background:linear-gradient(90deg,#F2C14E 0,#FFE08A var(--v),#28243A var(--v));box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(0,0,0,.3)}
.tlrange::-webkit-slider-thumb{-webkit-appearance:none;appearance:none;width:30px;height:30px;margin-top:-7px;border:0;border-radius:9px;background:linear-gradient(180deg,#FFE08A 0%,#F2C14E 100%);box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(255,255,255,.5),inset 0 -4px 0 rgba(0,0,0,.18),0 4px 0 #171320;transform:skewX(-6deg)}
.tlrange::-moz-range-thumb{width:30px;height:30px;border:0;border-radius:9px;background:linear-gradient(180deg,#FFE08A 0%,#F2C14E 100%);box-shadow:0 0 0 2.5px #171320,inset 0 3px 0 rgba(255,255,255,.5),inset 0 -4px 0 rgba(0,0,0,.18),0 4px 0 #171320}
.tltune .tog{margin-top:2px}
.tlnote{margin:2px 0 0;font:700 12.5px/1.3 var(--font-ui);color:rgba(255,255,255,.62);text-align:center}
/* the moment itself (pound, dodge): the game stopped, a spotlight, a finger and one word */
.tcue{position:absolute;inset:0;z-index:63;--cx:50%;--cy:50%;--cr:60px;background:radial-gradient(circle at var(--cx) var(--cy),rgba(23,19,32,0) 0 var(--cr),rgba(23,19,32,.55) calc(var(--cr) + 60px));opacity:0;transition:opacity .12s;touch-action:none;-webkit-tap-highlight-color:transparent}
.tcue.on{opacity:1}
.tcue>*{position:absolute;display:block;font-style:normal;pointer-events:none}
.tqring{left:var(--cx);top:var(--cy);width:calc(var(--cr) * 2);height:calc(var(--cr) * 2);margin:calc(var(--cr) * -1) 0 0 calc(var(--cr) * -1);border-radius:50%;box-sizing:border-box;border:5px solid #FFD23F;box-shadow:0 0 0 3px #171320,0 0 22px 6px rgba(255,210,63,.55);animation:tqpulse .7s ease-in-out infinite alternate}
@keyframes tqpulse{from{transform:scale(1)}to{transform:scale(1.08)}}
.tqring.nope{animation:tqnope .35s ease-out}
@keyframes tqnope{0%,100%{transform:translateX(0)}25%{transform:translateX(-8px)}75%{transform:translateX(8px)}}
.tqhand{width:58px;height:76px}
.tqhand svg{position:absolute;left:-43%;top:-95%;width:100%;height:100%;overflow:visible}
.tcue[data-k="pound"] .tqhand{left:var(--cx);top:var(--cy);animation:tqtap .9s ease-in-out infinite}
@keyframes tqtap{0%,100%{transform:translateY(-16px)}45%{transform:translateY(2px) scale(.94)}}
.tcue[data-k="dodge"] .tqhand{left:50%;top:78%;animation:tqswipe .95s cubic-bezier(.3,0,.2,1) infinite}
@keyframes tqswipe{0%{transform:translateY(0);opacity:0}15%{opacity:1}60%{transform:translateY(-110px);opacity:1}100%{transform:translateY(-120px);opacity:0}}
.tqtrail{left:50%;top:calc(78% - 120px);width:8px;height:120px;margin-left:-4px;border-radius:8px;background:linear-gradient(0deg,rgba(255,255,255,0),rgba(255,255,255,.9));opacity:0}
.tcue[data-k="dodge"] .tqtrail{animation:tqtrail .95s linear infinite}
@keyframes tqtrail{0%,20%{opacity:0}55%{opacity:.9}100%{opacity:0}}
.tcue.keys .tqhand,.tcue.keys .tqtrail{display:none}
.tqword{left:var(--cx);top:var(--cy);transform:translate(-50%,calc(var(--cr) * -1 - 64px));font:400 40px/1 var(--font-display);text-transform:uppercase;white-space:nowrap;color:#FFD23F;-webkit-text-stroke:2px #171320;paint-order:stroke fill;text-shadow:0 4px 0 #171320;animation:tqword .5s cubic-bezier(.2,1.6,.4,1) both}
.tcue[data-k="pound"] .tqword{left:min(var(--cx),calc(100% - 110px))}
@keyframes tqword{from{opacity:0;scale:.6}to{opacity:1;scale:1}}
@media (prefers-reduced-motion:reduce){.tv *,.tv>i{animation-duration:4.5s!important}.tvf{animation:none!important}}
"""

TV_ARCH = ('<svg viewBox="0 0 100 64" aria-hidden="true"><path d="M10 62V40a40 40 0 0 1 80 0v22" fill="none" stroke="#171320" stroke-width="15" stroke-linecap="round"/>'
           '<path d="M10 62V40a40 40 0 0 1 80 0v22" fill="none" stroke="#FFC21A" stroke-width="8.5" stroke-linecap="round"/><path d="M16 36a34 34 0 0 1 22-26" fill="none" stroke="#FFF4C4" stroke-width="3" stroke-linecap="round"/></svg>')
TV_TUB = ('<svg viewBox="0 0 100 52" aria-hidden="true"><ellipse cx="50" cy="26" rx="47" ry="22" fill="#6B5444" stroke="#171320" stroke-width="4"/><ellipse cx="50" cy="24" rx="39" ry="15" fill="var(--pc)" stroke="#171320" stroke-width="2.5"/>'
          '<ellipse cx="40" cy="20" rx="12" ry="4" fill="rgba(255,255,255,.35)"/></svg>')
TV_TUBF = '<svg viewBox="0 0 100 52" aria-hidden="true"><path d="M3 26a47 22 0 0 0 94 0" fill="none" stroke="#171320" stroke-width="4"/><path d="M7 28a43 18 0 0 0 86 0" fill="none" stroke="#6B5444" stroke-width="6"/></svg>'
TV_PB = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M14 3h12v13h7.5L20 30.5 6.5 16H14z"/></svg>'

JS = r"""
// ---------- (v443) the lesson's cards and cues: the game stopped on a looping little scene of the move (a finger acting out the gesture
// in step with it) and a few words; at the two moments that are about timing (pound, dodge), stopped on the moment itself ----------
const LSN_ORDER = ['move', 'tune', 'rings', 'sling', 'basin', 'pound', 'dodge'];
const LSN = {
  move: { t: 'Move', two: true, p: [['steer', 'Drag to steer', 'A and D steer'], ['jump', 'Tap to jump', 'SPACE jumps']] },
  tune: { t: 'Your steering', tune: true, go: 'Done' },
  rings: { t: 'Rings', p: [['rings', 'Steer through 3 rings', 'Steer through 3 rings']] },
  sling: { t: 'Slingshot', p: [['sling', 'Hold, pull down, let go', 'Hold S, then let go']] },
  basin: { t: 'Out of paint?', p: [['basin', 'Roll into the basin. Tap to hop out', 'Roll into the basin. SPACE hops out']] },
  pound: { t: 'Ground pound', p: [['pound', 'Get close, then tap Pound', 'Get close, then press E']] },
  dodge: { t: 'Dodge', p: [['dodge', 'Swipe up just before it lands', 'SHIFT just before it lands']] }
};
const TV = {
  steer: '<i class="tvf"></i><i class="tvsh"></i><i class="tvme"></i><i class="tvtr"></i><i class="tvh">%H%</i>',
  jump: '<i class="tvf"></i><i class="tvsh"></i><i class="tvme"></i><i class="tvr"></i><i class="tvh">%H%</i>',
  rings: '<i class="tvf"></i><i class="tvsh"></i><i class="tvme"></i><i class="tvarch">%ARCH%</i><i class="tvburst"></i>',
  sling: '<i class="tvf"></i><i class="tvlines"></i><i class="tvsh"></i><i class="tvband"></i><i class="tvme"></i><i class="tvpin"></i><i class="tvh">%H%</i>',
  basin: '<i class="tvf"></i><i class="tvtub">%TUB%</i><i class="tvsh"></i><i class="tvme"></i><i class="tvtubf">%TUBF%</i><i class="tvtank"><i></i></i><i class="tvr"></i><i class="tvh">%H%</i>',
  pound: '<i class="tvf"></i><i class="tvsplat"></i><i class="tvrv"></i><i class="tvstars"></i><i class="tvsh"></i><i class="tvme"></i><i class="tvpb">%PB%</i><i class="tvr"></i><i class="tvh">%H%</i>',
  dodge: '<i class="tvf"></i><i class="tvwarn"></i><i class="tvsplat"></i><i class="tvsh"></i><i class="tvme"></i><i class="tvrv"></i><i class="tvtr"></i><i class="tvh">%H%</i>'
};
const LSN_TUNE = '<div class="tltune"><div class="tlrow"><span class="tlk">Turning</span><b class="tlpct" id="tlTurnV"></b></div>'
  + '<div class="tlrng"><span aria-hidden="true">Gentle</span><input type="range" class="tlrange" id="tlTurn" min="40" max="100" step="5" aria-label="Turning speed"><span aria-hidden="true">Quick</span></div>'
  + '<div class="tlrow"><span class="tlk">Invert steering</span></div><div class="seg duo tog pick" id="tlInv" role="group" aria-label="Invert steering"><button type="button" data-v="off"><span>Normal</span></button><button type="button" data-v="on"><span>Inverted</span></button></div>'
  + '<p class="tlnote">Change these any time in Settings</p></div>';
const lsnEl = document.createElement('section'); lsnEl.className = 'tlsn'; lsnEl.hidden = true; lsnEl.setAttribute('role', 'dialog'); lsnEl.setAttribute('aria-modal', 'true'); lsnEl.setAttribute('aria-labelledby', 'tlTitle');
lsnEl.innerHTML = '<div class="tlcard"><div class="tldots" aria-hidden="true"></div><h2 id="tlTitle"></h2><div class="tlvis"></div><button class="btn play sm tlgo" id="tlGo" type="button">Go!</button></div>';
const cueEl = document.createElement('div'); cueEl.className = 'tcue'; cueEl.hidden = true; cueEl.setAttribute('role', 'status');
cueEl.innerHTML = '<i class="tqring"></i><i class="tqtrail"></i><i class="tqhand"></i><b class="tqword"></b>';
const CUE = { k: null, x0: 0, y0: 0, down: false, at: 0 }; let lsnAt = 0;
const lsnHand = () => { const h = tutEl.querySelector('.thand'); return h ? h.innerHTML : ''; };
// the game stopped (or going again): no finger left steering or holding the band, no keys held
function lsnFreeze(k) {
  if (!tut) return; tut.lsn = k || null; tut.slowK = k ? 0 : 1;
  if (k) { touches.clear(); if (steerId !== null) { steerId = null; steerIn = 0; rangeIn = 0; if (holdCharge) cancelCharge(P); holdCharge = false; slingOff(); } keyL = keyR = false; P.preJ = 0; tutGest(null); }
}
function lsnDue(k) { if (tut) tut.lsnDue = k; }
function lsnShow(k) {
  const L = LSN[k]; if (!L || !tut || state !== 'play') return; if (!lsnEl.parentNode) stage.appendChild(lsnEl);
  lsnFreeze(k); lsnEl.dataset.k = k; lsnEl.classList.toggle('keys', !!keysUI);
  lsnEl.style.setProperty('--pc', TEAMS[P.team].css); lsnEl.style.setProperty('--rc', TEAMS[(H || P).team].css);
  const i0 = LSN_ORDER.indexOf(k); lsnEl.querySelector('.tldots').innerHTML = LSN_ORDER.map((x, i) => '<i class="' + (i < i0 ? 'done' : i === i0 ? 'now' : '') + '"></i>').join('');
  lsnEl.querySelector('#tlTitle').textContent = L.t;
  const vis = lsnEl.querySelector('.tlvis'), hand = lsnHand(); vis.className = 'tlvis' + (L.two ? ' two' : '');
  vis.innerHTML = L.tune ? LSN_TUNE : L.p.map(([v, w, wk]) => '<div class="tlpan"><div class="tv" data-v="' + v + '" aria-hidden="true">' + TV[v].replace('%H%', hand).replace('%ARCH%', TV_ARCH).replace('%TUB%', TV_TUB).replace('%TUBF%', TV_TUBF).replace('%PB%', TV_PB) + '</div><p class="tll">' + escAttr(keysUI ? wk : w) + '</p></div>').join('');
  if (k === 'basin') { const w = vis.querySelector('.tll'), pw = potWord(); if (w) w.textContent = say('Roll into the ' + pw + '. Tap to hop out', 'Roll into the ' + pw + '. SPACE hops out'); }
  lsnEl.querySelector('#tlGo').textContent = L.go || 'Go!';
  lsnEl.hidden = false; lsnEl.classList.remove('on'); void lsnEl.offsetWidth; lsnEl.classList.add('on'); lsnAt = performance.now();
  if (L.tune) lsnTuneInit();
  if (AU.plop) AU.plop(); else AU.ui(); setTimeout(() => { if (!lsnEl.hidden) lsnEl.querySelector('#tlGo').focus({ preventScroll: true }); }, 60);
}
function lsnGo() { if (lsnEl.hidden || performance.now() - lsnAt < 800) return; /* (a tap meant for the game just before the card came up never skips it) */ lsnEl.classList.remove('on'); lsnEl.hidden = true; lsnEl.querySelector('.tlvis').innerHTML = ''; AU.init(); AU.pop(); lsnFreeze(null); if (tut) tut.ghostT = 0; }
lsnEl.addEventListener('click', e => { if (e.target.closest('.tltune')) return; lsnGo(); }); // (Go, or a tap anywhere but on the Turning bar and Invert)
function lsnTuneInit() {
  const r = $('tlTurn'), v = $('tlTurnV'), inv = $('tlInv'); if (!r) return;
  const paint = () => { const p = turnPct(); r.value = String(p); r.style.setProperty('--v', ((p - 40) / 60 * 100).toFixed(1) + '%'); v.textContent = p + '%'; r.setAttribute('aria-valuetext', p + '%'); for (const b of inv.children) b.setAttribute('aria-pressed', String((b.dataset.v === 'on') === !!store.steerInv)); };
  let last = turnPct();
  r.addEventListener('input', () => { const p = clamp(Math.round(+r.value / 5) * 5, 40, 100); if (p === 65) delete store.turn; else store.turn = p; paint(); if (p !== last) { last = p; try { AU.tick && AU.tick(0); } catch (e) {} } });
  r.addEventListener('change', () => { save(); if (window.__turnShow) window.__turnShow(); });
  inv.addEventListener('click', e => { const b = e.target.closest('button[data-v]'); if (!b) return; AU.init(); AU.ui(); invSet(b.dataset.v === 'on'); paint(); });
  paint();
}
// the moment itself: the game stopped where it is, a spotlight on the Pound button (or on you), a finger, one word. Doing it goes on
function lsnCue(k) {
  if (!tut || state !== 'play') return; if (!cueEl.parentNode) stage.appendChild(cueEl); const hd = cueEl.querySelector('.tqhand'); if (!hd.firstChild) hd.innerHTML = lsnHand();
  lsnFreeze(k); CUE.k = k; CUE.at = performance.now(); CUE.down = false; cueEl.dataset.k = k; cueEl.classList.toggle('keys', !!keysUI);
  const r0 = stage.getBoundingClientRect(); let cx, cy, cr;
  if (k === 'pound') { const b = $('slamBtn').getBoundingClientRect(); cx = b.left + b.width / 2 - r0.left; cy = b.top + b.height / 2 - r0.top; cr = Math.max(40, Math.max(b.width, b.height) * 0.62); }
  else { tv1.set(P.x, P.y + 0.4, P.z).project(camera); cx = (tv1.x * 0.5 + 0.5) * viewW; cy = (-tv1.y * 0.5 + 0.5) * viewH; cr = 64; }
  cueEl.style.setProperty('--cx', cx.toFixed(0) + 'px'); cueEl.style.setProperty('--cy', cy.toFixed(0) + 'px'); cueEl.style.setProperty('--cr', cr.toFixed(0) + 'px');
  cueEl.querySelector('.tqword').textContent = k === 'pound' ? say('Tap!', 'Press E!') : say('Swipe up!', 'Press Shift!');
  cueEl.hidden = false; cueEl.classList.remove('on'); void cueEl.offsetWidth; cueEl.classList.add('on'); if (AU.plop) AU.plop(); else AU.ui(); buzz(12);
}
function lsnCueDo() { const k = CUE.k; if (!k) return; CUE.k = null; CUE.down = false; cueEl.classList.remove('on'); cueEl.hidden = true; lsnFreeze(null);
  if (k === 'pound') { tutGivePound(); useSlam(P); } else if (k === 'dodge') { P.rollCD = 0; dodgeRoll(P); } }
cueEl.addEventListener('pointerdown', e => { e.preventDefault(); e.stopPropagation(); if (!CUE.k || performance.now() - CUE.at < 120) return; AU.init(); CUE.down = true; CUE.x0 = e.clientX; CUE.y0 = e.clientY;
  if (CUE.k === 'pound') { const b = $('slamBtn').getBoundingClientRect(), pad = 48; if (e.clientX > b.left - pad && e.clientX < b.right + pad && e.clientY > b.top - pad && e.clientY < b.bottom + pad) lsnCueDo(); else { kick(cueEl.querySelector('.tqring'), 'nope'); AU.nope && AU.nope(); } } });
cueEl.addEventListener('pointermove', e => { if (!CUE.down || CUE.k !== 'dodge') return; const up = CUE.y0 - e.clientY; if (up > 24 && up > Math.abs(e.clientX - CUE.x0) * 1.1) lsnCueDo(); });
for (const t of ['pointerup', 'pointercancel']) cueEl.addEventListener(t, () => { CUE.down = false; });
// keys: Enter or Space go on from a card; E pounds, Shift (or Q) dodges at a cue; nothing else reaches the game meanwhile
window.addEventListener('keydown', e => {
  const k = e.key;
  if (lsnEl.parentNode && !lsnEl.hidden) { if (e.target && e.target.closest && e.target.closest('.tltune') && k !== 'Enter') return; if (k === 'Enter' || k === ' ' || k === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); lsnGo(); } else if (k === 'p' || k === 'P') { e.preventDefault(); e.stopImmediatePropagation(); } return; }
  if (CUE.k) { e.preventDefault(); e.stopImmediatePropagation(); if ((CUE.k === 'pound' && (k === 'e' || k === 'E')) || (CUE.k === 'dodge' && (k === 'Shift' || k === 'q' || k === 'Q'))) lsnCueDo(); }
}, true);
function lsnOff() { CUE.k = null; cueEl.hidden = true; cueEl.classList.remove('on'); lsnEl.hidden = true; lsnEl.classList.remove('on'); lsnEl.querySelector('.tlvis').innerHTML = ''; if (tut) { tut.lsn = null; tut.lsnDue = null; } }
// a few seconds into a lesson without doing it: the finger acts it out over the game (no words), and goes once you do
function lsnGhost(kind, dt) { if (!tut) return; tut.ghostT = (tut.ghostT || 0) + (dt || 0); const g = kind && tut.ghostT > 3.5 ? kind : ''; if ((tutGestEl.dataset.g || '') !== g) tutGest(g || null); }
"""

STEPS = r"""const TUT_STEPS = [
  // (v443) each lesson opens on its card (lsnDue): the game stopped, the move shown; nothing slowed and nothing said in play
  { id: 'move', max: 45, enter() { tut.moved = 0; tut.steered = false; tut.jumped = false; tut.lx = P.x; tut.lz = P.z; tut.slowK = 1; tutHide(); lsnDue('move'); },
    tick(dt) { if (P.st === 'play' && !P.air) tut.moved += Math.hypot(P.x - tut.lx, P.z - tut.lz); tut.lx = P.x; tut.lz = P.z;
      if (Math.abs(steerIn) > 0.3 || keyL || keyR) tut.steered = true; if (P.st === 'play' && P.air && P.vy > 3 && !P.flung && !P.slam) tut.jumped = true;
      lsnGhost(!tut.steered ? 'steertap' : !tut.jumped ? 'tap' : null, dt);
      return (tut.steered && tut.jumped) || tut.moved > 45; } },
  { id: 'freetune', max: 99, enter() { tutHide(); lsnDue('tune'); }, tick() { return true; } }, // (Your steering: the card is the lesson)
  // three of the time trial's rings, one after another, close ahead of you
  { id: 'rings', max: 50, enter() { tutHide(); tut.ringsOn = false; lsnDue('rings'); },
    tick(dt) { if (!tut.ringsOn) { tut.ringsOn = true; tut.rings = true; TR.n = 0; TR.last.length = 0; TR.on = false; TR.wait = 0.05; } lsnGhost(null, dt); return TR.n >= 3; },
    exit() { tut.rings = false; TR.wait = 0; if (TR.on) { TR.on = false; TR.out = 1; } } },
  { id: 'sling', max: 40, enter() { tutHide(); lsnDue('sling'); },
    tick(dt) { lsnGhost(P.charging ? null : 'pull', dt); return P.st === 'play' && P.air && P.flung && (P.flingC || 0) > 0.1; } },
  // out of paint: your tank empties, one basin comes up a few steps ahead of you (the only one about), and the way to it is shown
  { id: 'basin', max: 55, enter() { tut.slowK = 1; tut.basinTip = false; tut.basinT = 0; tut.basinSw = false; tut.potQ = null; tut.potTry = 0; tutHide(); lsnDue('basin'); },
    exit() { tut.potQ = null; },
    tick(dt) { if (P.dryT) P.dryT = 0; /* (no running dry into a knock-out in the lesson) */
      if (!tut.potQ && P.st === 'play' && !P.air && (tut.potTry -= dt) <= 0) { tut.potTry = 0.3; tut.potQ = tutRaisePot(); }
      if (P.st === 'play') P.paint = tut.basinTip ? Math.min(P.paint, 0.02) : Math.max(0, P.paint - dt * 1.1);
      if (tut.basinTip && !tut.basinSw) { tut.basinT += dt; if (tut.basinT > 3 && P.st === 'play') { tut.basinSw = true; tutGest('swipe'); } } /* (not there yet: a finger shows the swipe up, a roll gets you there faster) */
      if (!tut.basinTip && P.paint <= 0.02) { tut.basinTip = true; pingTank(4); }
      return P.st === 'hide' && tut.basinTip; } },
  // full again, you jump out (a tap, the finger shows it) and stop where you land; the view cuts to a second basin across the canvas,
  // the rival climbs out of it, and the view cuts back to you, turned to face him
  { id: 'rival', max: 60, enter() { tutHide(); tut.slowK = 1; tut.sub = 'tub'; tut.rvT = 0; tut.outTip = false; tut.tubT = 0; },
    exit() { tutRevealEnd(); },
    tick(dt) {
      if (tut.sub === 'tub') {
        if (P.st === 'hide' && P.pot) { P.pot.ink = Math.max(P.pot.ink, 0.3);
          if (!tut.outTip && P.paint >= 0.97) { tut.outTip = true; tutGest('tap'); }
          if (tut.outTip && (tut.tubT += dt) > 9) jump(P);
          return false; }
        if (P.st !== 'play') return false; tutHide(); tut.sub = 'land'; }
      if (tut.sub === 'land') { if (P.air) return false; tut.sub = 'stop'; tut.rvT = 0; tut.hold = true; }
      tut.rvT += dt;
      if (tut.sub === 'stop') { if (tut.rvT < 0.6 || P.spd > 0.3) return false; tut.sub = tutRivalUp() ? 'peek' : 'look'; tut.rvT = 0; return false; }
      if (tut.sub === 'peek') { if (tut.rvT < 0.8) return false; if (H.st === 'hide' && H.pot) introCrawl(H); tut.sub = 'climb'; tut.rvT = 0; return false; }
      if (tut.sub === 'climb') { if (H.introCrawl && tut.rvT < 4) return false; tut.sub = 'look'; tut.rvT = 0; return false; }
      return tut.rvT > 1.1; } },
  // the pound: he comes over and circles in close; the first time he's in reach the game stops on the Pound button (lsnCue)
  { id: 'pound', max: 80, exit() { tut.drive = null; tut.driveMode = null; TUT_AI.speed = 0.8; },
    enter() { tut.hidePound = false; tut.keepAway = false; tut.drive = H; tut.driveMode = 'near'; TUT_AI.speed = 0.62; tutGivePound(); tut.kos0 = P.kos; tut.flat0 = P.flatted; tut.slowK = 1; tut.cueN = 0; tut.cueAt = -99; tut.cueSlow = 0; tutHide(); lsnDue('pound'); },
    tick(dt) { if (P.slamCD > 1.5) P.slamCD = 1.5; // (the pound keeps coming back until one lands)
      const hd = Math.hypot(H.x - P.x, H.z - P.z); TUT_AI.speed = hd > 8 ? 1.3 : hd > 5 ? 0.9 : 0.62; if (tut.cueSlow > 0) { tut.cueSlow -= dt; TUT_AI.speed = 0.12; } /* (just pounded at the cue: he stays put for it) */
      if (P.st === 'play' && hd > 6) tutRivalIn(5.5);
      const reach = H.st === 'play' && hd < SLAM_R - 0.5 && Math.abs(H.y - P.y) < 1.2;
      if (reach && tut.cueN < 2 && runT - tut.cueAt > 6 && P.st === 'play' && !P.air && !P.slam && !P.charging) { tut.cueN++; tut.cueAt = runT; tut.cueSlow = 1.2; tutGivePound(); lsnCue('pound'); }
      return P.kos > tut.kos0 || P.flatted > tut.flat0; } },
  // the dodge: he comes at you and jump-pounds; the moment before it lands the game stops on you (lsnCue) and a swipe up rolls you clear
  { id: 'dodge', max: 60, enter() { tut.noPound = true; Object.assign(TUT_AI, TUT_AI_FIGHT); tut.drive = H; tut.driveMode = 'fight'; H.slamCD = 0; if (H.paint < 0.8) H.paint = 1; if (H.ai) { H.ai.plan = null; H.ai.path = null; } tut.rolled = false; tut.hits = 0; tut.wasKo = false; tut.escaped = false; tut.thr = false; tut.slamW = false; tut.h0 = 0; tut.slowK = 1; tut.cueN = 0; tut.slamNo = 0; tut.cueNo = -1; tutHide(); lsnDue('dodge'); },
    tick(dt) { if (!H.slam && P.st === 'play') tutRivalIn(6.5); if (H.st === 'play' && !H.slam && H.slamCD > 1.2) H.slamCD = 1.2; if (H.paint < 0.5) H.paint = 1;
      const d = Math.hypot(H.x - P.x, H.z - P.z), eta = H.slam ? H.slamEta - H.slamT : 9, coming = H.slam && H.st === 'play' && P.st === 'play' && !P.air && d < slamRadius(H) + PR + 2.5;
      if (coming && P.rollT <= 0 && !tut.rolled) P.rollCD = 0; /* (an early swipe never leaves you without a roll for the drop) */
      if (coming && P.rollT > 0 && !tut.rolled) tut.rolled = true; // (a roll while its pound is in the air: that is the timing)
      if (tut.rolled && H.slam && P.rollT > 0 && P.rollT < 0.05) P.rollT = 0.05; /* (and it holds you clear till the pound lands) */
      if (P.st === 'ko' && !tut.wasKo) tut.hits++; tut.wasKo = P.st === 'ko';
      if (H.slam && !tut.slamW) { tut.h0 = tut.hits; tut.slamNo++; } if (H.slam && H.st === 'play' && d < slamRadius(H) + PR + 6) tut.thr = true;
      if (tut.slamW && !H.slam) { if (tut.thr && tut.hits === tut.h0 && H.st === 'play' && P.st === 'play') tut.escaped = true; tut.thr = false; } tut.slamW = !!H.slam; /* (it came down and missed you: a swipe, a jump, a fling or just getting out of its way, any of them) */
      if (coming && eta < 0.45 && !tut.rolled && P.rollT <= 0 && tut.cueN < 2 && tut.cueNo !== tut.slamNo) { tut.cueN++; tut.cueNo = tut.slamNo; lsnCue('dodge'); }
      return (tut.rolled || tut.escaped || tut.hits >= 2) && P.st === 'play' && !H.slam; },
    exit() { Object.assign(TUT_AI, TUT_AI_CALM); tut.drive = null; tut.noPound = false; } },
  { id: 'rest', max: 1e9, enter() { tutHide(); tut.slowK = 1; if (matchLeft < 28) matchLeft = 28; tut.cardIn = 1.1; tut.card = false; },
    tick(dt) { if (tut.cardIn > 0) { tut.cardIn -= dt; if (tut.cardIn <= 0) matchLeft = 0; } return false; } } // (a beat for the last praise, then the match is over: Basics Complete, then the tally)
];
const TUT_REST = TUT_STEPS.length - 1;"""

OLD_TUB = """  if (inTub) {
    if (s.id === 'rest' ? !tutTip : (!tutTip || tutTip.key !== 'tubout')) { if (tutTip && tutTip.key !== 'tubout') tut.tubTip = tutTip; tutShow(say('*SWIPE UP* to roll out of the tub!', 'Press *SHIFT* to roll out of the tub!'), null, 'tubout', true, true); }
    if (s.id !== 'rest') { tut.slowK = 1; return; } }
  else if (tutTip && tutTip.key === 'tubout') { const t0 = tut.tubTip; tut.tubTip = null; tutHide(); if (t0) tutShow(t0.text, t0.at, t0.key, t0.call, t0.nodim, t0.side, t0.loose, t0.low); }
"""
NEW_TUB = """  if (inTub) { if (!tut.tubG) { tut.tubG = true; tutGest('swipe'); } if (s.id !== 'rest') { tut.slowK = 1; return; } } /* (v443: the finger shows the swipe out, no words) */
  else if (tut.tubG) { tut.tubG = false; tutGest(null); }
  // (v443) a lesson's card waits for a calm moment (you on the floor, no kill cam, no banner up), and the lesson waits for the card
  if (tut.lsnDue) { if (!kcam && P.st === 'play' && !P.air && !(tut.gap > 0) && performance.now() > bannerUntil) { const k = tut.lsnDue; tut.lsnDue = null; lsnShow(k); } return; }
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    a = s.index("const TUT_STEPS = ["); b = s.index("const TUT_REST = TUT_STEPS.length - 1;") + len("const TUT_REST = TUT_STEPS.length - 1;")
    import json
    js = JS.lstrip('\n') + 'const TV_ARCH = ' + json.dumps(TV_ARCH) + ', TV_TUB = ' + json.dumps(TV_TUB) + ', TV_TUBF = ' + json.dumps(TV_TUBF) + ', TV_PB = ' + json.dumps(TV_PB) + '; // (the scenes\' drawn parts)\n'
    s = s[:a] + js + STEPS + s[b:]
    # the game stopped while a card or a cue is up (whatever else is going on, a kill cam included)
    s = rep(s, "  if (kcam) {} else if (tut && tut.slowK < 1 && state === 'play') dt *= tut.slowK;",
               "  if (tut && tut.lsn && state === 'play') dt = 0; else if (kcam) {} else if (tut && tut.slowK < 1 && state === 'play') dt *= tut.slowK; /* (v443: a lesson's card or cue: stopped) */")
    s = rep(s, "if (state === 'play' && tut.step >= 0 && !tut.tubHold) { tut.st += rdt;", "if (state === 'play' && tut.step >= 0 && !tut.tubHold && !tut.lsn && !tut.lsnDue) { tut.st += rdt;")
    s = rep(s, "const on = state === 'play' && tut.slowK < 1 && !tut.card;", "const on = state === 'play' && tut.slowK < 1 && !tut.card && !tut.lsn;")
    s = rep(s, OLD_TUB, NEW_TUB)
    # the rings in the lesson: the time trial's, close ahead, no +2 seconds (a count instead), no words
    s = rep(s, "if (mode === 'solo' && !tut) trialTick(dt);", "if ((mode === 'solo' && !tut) || (tut && tut.rings)) trialTick(dt);")
    s = rep(s, "  TR.on = false; TR.out = 1; TR.n++; TR.wait = 0.4; matchLeft += TR_ADD;",
               "  TR.on = false; TR.out = 1; TR.n++; TR.wait = tut ? (TR.n < 3 ? 0.3 : 0) : 0.4; if (!tut) matchLeft += TR_ADD; else popText(TR.n + ' / 3'); /* (v443: the lesson's three) */")
    s = rep(s, "  if (tv1.z < 1) { el.innerHTML = '+' + TR_ADD + '<small>s</small>';", "  if (tv1.z < 1 && !tut) { el.innerHTML = '+' + TR_ADD + '<small>s</small>';")
    s = rep(s, "const ck = $('clock'), ca = $('clkAdd'); restartCls(ck, 'bonus');\n  if (ca) {", "const ck = $('clock'), ca = $('clkAdd'); if (!tut) restartCls(ck, 'bonus');\n  if (ca && !tut) {")
    s = rep(s, "  if (TR.n === 0) hint('rings',", "  if (TR.n === 0 && !tut) hint('rings',")
    s = rep(s, "const first = TR.n === 0, lo = first ? 6 : 9,", "const first = TR.n === 0 || !!tut, lo = first ? 6 : 9,")
    s = rep(s, "pips: new Set(), bonus: 0, praiseN: 0 }; tutPipsDraw();", "pips: new Set(), bonus: 0, praiseN: 0 }; tutPipsDraw(); if (AU.xwant) AU.xwant('t_ring'); /* (v443: the rings' chime) */")
    s = rep(s, "const TUT_PIP = { move: 0, sling: 1,", "const TUT_PIP = { move: 0, rings: 7, sling: 1,")
    # leaving the lesson: no card or cue left up
    s = rep(s, "function tutLeave() {", "function tutLeave() { lsnOff();")
    a = "tutCard(false); tut = null; tutHide(); if (tutSlowEl.classList.contains('on')) AU.slow(false, true); tutSlowEl.classList.remove('on'); tutPipsEl.classList.remove('on');"
    s = rep(s, a, "lsnOff(); " + a, 2)
    # Basics Complete: what the lesson taught now (rings in place of the orb), and nothing handed out
    s = rep(s, "const TW_LIST = ['Steering and jumping', 'Flinging', 'Refilling', 'The pound', 'Dodging', 'The orb'];", "const TW_LIST = ['Steering and jumping', 'Rings', 'Flinging', 'Refilling', 'The pound', 'Dodging'];")
    s = rep(s, "rw.push('<span style=\"--i:2\">Flower + Fangs found</span>');", "")
    # the card's words: what the lesson is now
    s = rep(s, "function tutBasicsCard() {\n  const el = $('tutGo'); if (!el.hidden) return;", "function tutBasicsCard() {\n  const el = $('tutGo'); if (!el.hidden || menu.hidden || state !== 'menu' || building || irisBusy) return; /* (v443: never again on the way into the match) */")
    s = rep(s, "  tutHide(); /* (nothing from the lobby carries into the match) */", "  tutHide(); /* (nothing from the lobby carries into the match) */ { const g = $('tutGo'); if (g.dataset.mode === 'basics') { g.classList.remove('on'); g.hidden = true; g.dataset.mode = ''; coachCorner(null); } } /* (v443) */")
    s = rep(s, "'A quick training match shows you how to roll, fling, pound and dodge. Or skip it and jump straight in.'",
               "'A quick training match: steer, jump, slingshot, pound and dodge. Or skip it and jump straight in.'")
    return s
