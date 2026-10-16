"""v312: the Strokes page laid out like a gear screen, with a live demo of each transform.

- The page is a pale lime wall with faint zigzags and axolotl silhouettes (art/sg_bg.webp, made with Ludo). A black ink band
  (art/sg_ink.webp, Ludo) runs across it; the categories sit on it as tab cards: a black title band, a body striped in the category's
  colour (orange specials, teal skills, coral transforms), the stroke you have on, and a dot for each stroke in it (filled: yours).
  The open one is bigger and ringed in yellow.
- The strokes hang in a dark see-through panel, from a hanger bar taped at its top, three to a row: hang tags with a hook, a mottled
  cream card (art/sg_card.webp, Ludo) with the picture, and a lime strip with two icons for what the stroke is about. The one you're
  looking at has a magenta splat behind its picture, a thick yellow ring and sits a little bigger. A tag shows the rank a locked stroke
  opens at, the craft time of one to craft, the bench's countdown and bar on the one being crafted, a check stamp on the one you have
  on, and New.
- The stroke you're looking at is named on a black banner taped on with a pennant at its end, with a line on what it does and one
  button: Equip, Craft (and its time), or the bench's countdown and Skip. Info opens its sheet: what it does, its numbers, how you get
  it. A second tap on a tag you own puts it on.
- Transforms: the right of the screen (the top, upright) is a live demo drawn with the game itself. Your own axolotl (your colour and
  what you wear) uses the transform on a small pad against a rival: the Roller rolls out a stripe and crushes them in its roll, the
  Turret plants and fires till they're dry and out, the Paint Trap is set and goes off under them, the Whirlwind winds up and charges
  through them, the Boomerang loops out through them and comes back. It loops, swapping sides; a drag on it (or the round stick)
  turns the view. Test plays it from the start, bigger, with a caption for each step. It's drawn into the game's own canvas under a
  window in the page (the page's wall drawn there too, so there's no seam), only while it shows: not under the Info sheet, another
  screen or with the app away. Its own code makes no new objects per frame (the characters move by the game's own code, as in a
  match). If a quality step drops the sun's shadow map while the page is up, the map is made again (empty) before the demo draws:
  the lit shaders draw nothing without one.
- Specials and skills have no demo: the panel, the banner and the button are centred, the stroke's picture big above them upright.
- The back button is a purple circle with a curved arrow (bottom left; top left upright); Info and Test are dark slanted pills; a black
  badge at the top right shows your rank, or the bench's countdown while something's crafting (a tap goes to it).
- Ol' Bloop's Strokes lesson walks the new page: tap the Giant, Craft, Skip, Equip (sideways the page sits to the left while he
  talks, so his line never covers what he points at). The "Unlock everything" code link (v309) sits at the foot of the panel, small,
  as on Customize."""
import re


def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)


def region(s, a, b, new):
    assert s.count(a) == 1, (s.count(a), a[:120]); i = s.index(a); j = s.index(b, i); return s[:i] + new + s[j:]


SV_BACK = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M12.6 7.4 6.2 13.6l6.4 6.2" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M7.4 13.6h11.2a6.4 6.4 0 0 1 0 12.8h-4.4" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/></svg>'
SV_ROT = '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="5.2" fill="currentColor"/><path d="M6.6 12.4a10 10 0 0 1 17.6-3.2M25.4 19.6a10 10 0 0 1-17.6 3.2" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><path d="M24.6 4.6l.2 5.4-5.4.4M7.4 27.4l-.2-5.4 5.4-.4" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

MARKUP = """    <div class="mevents mstrokes sgp" id="mStrokes" hidden>
      <div class="sgbg" id="sgBg" aria-hidden="true"></div><div class="sgink" aria-hidden="true"></div>
      <h2 class="sgvh" id="stTitle">Strokes</h2>
      <button class="sgback" id="stBack" type="button" aria-label="Back to the lobby">__BACK__<span>Back</span></button>
      <button class="sgbadge" id="sgBadge" type="button"><span class="sgbi" id="sgBadgeI" aria-hidden="true"></span><b id="sgBadgeT">1</b></button>
      <div class="sgshow" id="sgShow">
        <div class="sgstage" id="sgStage"><span class="sgart" id="sgArt" aria-hidden="true"></span><p class="sgcap" id="sgCap" aria-live="polite"></p></div>
        <div class="sgban" id="sgBan"><small id="sgKind">Special stroke</small><b id="sgName">Rocket</b><i class="sgflag" aria-hidden="true"></i></div>
        <button class="sgrot" id="sgRot" type="button" aria-label="Turn the view" hidden>__ROT__</button>
        <div class="sgfoot"><p class="sgline" id="sgLine"></p>
          <div class="sgact"><span class="sgtimer" id="sgTimer" hidden><i aria-hidden="true">__GLASS__</i><b id="sgTime">0:00</b><span class="sgtbar" aria-hidden="true"><i id="sgBar"></i></span></span><button class="sgskip" id="sgSkip" type="button" hidden>Skip</button><button class="sgdo" id="sgDo" type="button">Equip</button></div>
          <p class="sgnote" id="sgNote" hidden></p></div>
      </div>
      <section class="sgpanel" id="stPanel" aria-labelledby="stCatH"><i class="sghang" aria-hidden="true"></i><h3 class="sgvh" id="stCatH">Special strokes</h3><p class="sgvh" id="stCatS">What the orb gives you</p>
        <div class="sgscroll" id="sgScroll">
          <div class="sggrid" id="stSpecialRail" role="tabpanel" aria-labelledby="stSpecial"></div>
          <div class="sggrid" id="stSkillRail" role="tabpanel" aria-labelledby="stSkill" hidden></div>
          <div class="sggrid" id="stItemRail" role="tabpanel" aria-labelledby="stItem" hidden></div>
__UCODE__        </div>
      </section>
      <div class="sgtabs" id="sgTabs" role="tablist" aria-label="Your loadout">
        <button class="sgtab" id="stSpecial" type="button" role="tab" data-cat="special" aria-controls="stSpecialRail"><b class="sgtt">Specials</b><span class="sgtb"><span class="sgti" id="stSpecialNow"></span><span class="sgdots" id="sgDots_special" aria-hidden="true"></span></span></button>
        <button class="sgtab" id="stSkill" type="button" role="tab" data-cat="skill" aria-controls="stSkillRail"><b class="sgtt">Skills</b><span class="sgtb"><span class="sgti" id="stSkillNow"></span><span class="sgdots" id="sgDots_skill" aria-hidden="true"></span></span></button>
        <button class="sgtab" id="stItem" type="button" role="tab" data-cat="item" aria-controls="stItemRail"><b class="sgtt">Transforms</b><span class="sgtb"><span class="sgti" id="stItemNow"></span><span class="sgdots" id="sgDots_item" aria-hidden="true"></span></span></button>
      </div>
      <div class="sgpills"><button class="sgpill" id="sgInfo" type="button" aria-haspopup="dialog"><span>Info</span></button><button class="sgpill" id="sgTest" type="button"><span>Test</span></button></div>
    </div>
"""

POP = """  <div class="modal stpopm sginfo" id="stPop" hidden><div class="stpop" role="dialog" aria-modal="true" aria-labelledby="stPopName">
    <div class="stphead"><b id="stPopKind">Skill</b><span class="stpown" id="stPopOwn" hidden></span><button class="stpx" id="stPopX" type="button" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></button></div>
    <div class="stpbody"><span class="stpart" id="stPopArt" aria-hidden="true"></span><h3 class="stpname" id="stPopName"></h3><p class="stpdesc" id="stPopDesc"></p>
      <ul class="stpdoes" id="stPopDoes" aria-label="What it does"></ul>
      <dl class="sgnums" id="sgNums" aria-label="Its numbers"></dl>
      <p class="sghow" id="sgHow"></p></div>
  </div></div>
"""

GLASS = '<svg viewBox="0 0 24 24"><path d="M6.5 3h11M6.5 21h11M8 3c0 5.2 8 5.6 8 9s-8 3.8-8 9M16 3c0 5.2-8 5.6-8 9s8 3.8 8 9" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>'

CSS = r"""
/* (v312) the Strokes page as a gear screen: a lime wall, an ink band with a tab card per category, a dark panel of hang-tag cards,
   the stroke you're looking at named on a taped banner, and for a transform a live demo in a window drawn by the game itself.
   Upright it's a column: the stroke (and its demo) up top, the tabs on the band, the panel, Info and Test */
#mStrokes.sgp{--lime:#CBE45A;--sel:#FFE23C;--mag:#E8308A;--ink0:#111014;--panel:rgba(28,28,33,.86);--kc:#FFA526;
  --gx:max(14px,env(safe-area-inset-left));--gr:max(14px,env(safe-area-inset-right));--gt:max(12px,env(safe-area-inset-top));--gb:env(safe-area-inset-bottom,0px);
  --bk:56px;--tabw:104px;--pillh:40px;--panh:min(31vh,262px);
  display:flex;flex-direction:column;box-sizing:border-box;padding:var(--gt) var(--gr) calc(var(--gb) + 12px) var(--gx);background:none;color:var(--black);overflow:hidden;-webkit-user-select:none;user-select:none}
#mStrokes.sgp[hidden]{display:none}
#mStrokes.sgp::before{display:none}
#mStrokes.sgp[data-cat="skill"]{--kc:#1FC4B4}
#mStrokes.sgp[data-cat="item"]{--kc:#FF5A5F}
#mStrokes.sgp .sgvh{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
#mStrokes.sgp .sgbg{position:absolute;inset:0;z-index:0;background:var(--lime) url(art/sg_bg.webp) 0 0/560px 560px repeat}
#mStrokes.sgp .sgink{display:none;position:absolute;left:-30px;right:-30px;z-index:2;pointer-events:none;background:url(art/sg_ink.webp) 0 50%/auto 100% repeat-x}
/* the stroke you're looking at: its stage (the demo's window, or its picture), the banner and the button over it */
#mStrokes.sgp .sgshow{position:relative;z-index:4;flex:1 1 auto;min-height:170px;pointer-events:none}
#mStrokes.sgp .sgshow>*{pointer-events:auto}
#mStrokes.sgp .sgstage{position:absolute;inset:0;touch-action:none}
#mStrokes.sgp .sgban{position:absolute;left:50%;top:6px;z-index:2;display:flex;flex-direction:column;align-items:flex-start;gap:3px;max-width:calc(100% - 2 * (var(--bk) + 16px));box-sizing:border-box;padding:7px 28px 8px 18px;background:var(--ink0);color:#fff;transform:translateX(-50%) skewX(-11deg);box-shadow:5px 5px 0 rgba(23,19,32,.22)}
#mStrokes.sgp .sgban>small,#mStrokes.sgp .sgban>b{transform:skewX(11deg)}
#mStrokes.sgp .sgban small{font:800 10px/1 var(--font-ui);letter-spacing:.16em;text-transform:uppercase;color:var(--kc);white-space:nowrap}
#mStrokes.sgp .sgban b{max-width:100%;overflow:hidden;font:400 24px/1.04 var(--font-display);letter-spacing:.01em;white-space:nowrap;text-overflow:ellipsis}
#mStrokes.sgp .sgban::before{content:"";position:absolute;left:-18px;top:-10px;width:58px;height:20px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:skewX(11deg) rotate(-24deg);filter:drop-shadow(0 1px 0 rgba(23,19,32,.18))}
#mStrokes.sgp .sgban .sgflag{position:absolute;right:-19px;top:50%;width:22px;height:30px;margin-top:-15px;transform:skewX(11deg)}
#mStrokes.sgp .sgban .sgflag::before{content:"";position:absolute;left:0;top:0;width:3px;height:30px;border-radius:2px;background:var(--ink0)}
#mStrokes.sgp .sgban .sgflag::after{content:"";position:absolute;left:3px;top:1px;width:18px;height:14px;background:var(--kc);clip-path:polygon(0 0,100% 50%,0 100%);animation:sgflag 2.4s ease-in-out infinite;transform-origin:0 50%}
@keyframes sgflag{50%{transform:scaleX(.82) skewY(4deg)}}
#mStrokes.sgp .sgart{position:absolute;left:0;right:0;top:64px;bottom:76px;display:flex;align-items:center;justify-content:center;pointer-events:none}
#mStrokes.sgp.sgnoted .sgart{bottom:94px}
#mStrokes.sgp.sgnoted:not(.sgtest) .sgrot{bottom:100px}
#mStrokes.sgp .sgart::after{content:"";position:absolute;left:50%;bottom:0;width:min(46%,200px);height:min(9%,22px);margin-left:calc(min(46%,200px) / -2);border-radius:50%;background:radial-gradient(closest-side,rgba(23,19,32,.24),rgba(23,19,32,0));z-index:0}
#mStrokes.sgp .sgart .stimg{position:relative;z-index:1;width:auto;height:min(92%,230px);max-width:70%;object-fit:contain;filter:drop-shadow(2px 4px 0 rgba(23,19,32,.18));animation:sgbob 3.2s ease-in-out infinite}
#mStrokes.sgp .sgart svg{position:relative;z-index:1;width:min(60%,160px);height:auto}
@keyframes sgbob{50%{transform:translateY(-5px) rotate(-1.5deg)}}
#mStrokes.sgp .sgart.sgpopin .stimg{animation:sgpop .42s cubic-bezier(.2,1.6,.4,1) both,sgbob 3.2s .42s ease-in-out infinite}
@keyframes sgpop{from{transform:scale(.6) rotate(-6deg);opacity:0}}
#mStrokes.sgp.sgdemo .sgart{display:none}
#mStrokes.sgp .sgcap{position:absolute;left:50%;bottom:10px;z-index:2;max-width:92%;margin:0;padding:7px 13px 8px;border-radius:10px;background:rgba(17,16,20,.88);color:#fff;font:700 14px/1.25 var(--font-ui);text-align:center;transform:translateX(-50%);opacity:0;transition:opacity .2s;pointer-events:none;text-wrap:balance}
#mStrokes.sgp.sgtest .sgcap.on{opacity:1}
#mStrokes.sgp .sgrot{appearance:none;position:absolute;right:0;bottom:84px;z-index:3;display:grid;place-items:center;width:42px;height:42px;margin:0;padding:0;border:0;border-radius:50%;background:radial-gradient(circle at 50% 40%,#3A3A42,#1A1A1F);color:#E9E9EE;box-shadow:0 0 0 2px var(--ink0),inset 0 0 0 3px rgba(255,255,255,.1),0 3px 0 rgba(0,0,0,.35);cursor:pointer}
#mStrokes.sgp .sgrot[hidden]{display:none}
#mStrokes.sgp .sgrot svg{width:26px;height:26px}
#mStrokes.sgp .sgfoot{position:absolute;left:0;right:0;bottom:4px;z-index:2;display:flex;flex-direction:column;align-items:center;gap:6px}
#mStrokes.sgp .sgline{margin:0;max-width:min(100%,420px);font:800 14px/1.25 var(--font-ui);color:var(--black);text-align:center;text-wrap:balance;text-shadow:0 1px 0 rgba(255,255,255,.35)}
#mStrokes.sgp .sgact{display:flex;align-items:center;justify-content:center;gap:10px}
#mStrokes.sgp .sgdo{appearance:none;position:relative;min-width:120px;height:38px;margin:0;padding:0 20px;border:0;border-radius:10px;background:var(--sel);color:var(--ink0);font:400 16px/1 var(--font-display);letter-spacing:.01em;transform:skewX(-12deg);box-shadow:0 0 0 2.5px var(--ink0),0 4px 0 var(--ink0);cursor:pointer;-webkit-tap-highlight-color:transparent}
#mStrokes.sgp .sgdo>span{display:inline-flex;align-items:center;gap:6px;transform:skewX(12deg)}
#mStrokes.sgp .sgdo small{padding:3px 6px 2px;border-radius:6px;background:rgba(17,16,20,.16);font:800 11px/1 var(--font-ui)}
#mStrokes.sgp .sgdo svg{width:15px;height:15px}
#mStrokes.sgp .sgdo.craft{background:#5BE07E}
#mStrokes.sgp .sgdo:active:not(:disabled){transform:skewX(-12deg) translateY(3px);box-shadow:0 0 0 2.5px var(--ink0),0 1px 0 var(--ink0)}
#mStrokes.sgp .sgdo:disabled{background:#E9E4D6;color:#6E6680;cursor:default}
#mStrokes.sgp .sgdo.on:disabled{background:var(--ink0);color:var(--sel)}
#mStrokes.sgp .sgdo[hidden],#mStrokes.sgp .sgskip[hidden],#mStrokes.sgp .sgtimer[hidden]{display:none}
#mStrokes.sgp .sgtimer{display:flex;align-items:center;gap:7px;height:34px;padding:0 12px 0 10px;border-radius:10px;background:var(--ink0);color:#fff;font:400 16px/1 var(--font-display);font-variant-numeric:tabular-nums;box-shadow:0 3px 0 rgba(0,0,0,.3)}
#mStrokes.sgp .sgtimer i{display:grid;color:var(--sel)}#mStrokes.sgp .sgtimer svg{width:15px;height:15px}
#mStrokes.sgp .sgtbar{width:54px;height:6px;border-radius:999px;background:rgba(255,255,255,.18);overflow:hidden}
#mStrokes.sgp .sgtbar i{display:block;height:100%;width:var(--p,0%);background:var(--sel);transition:width .5s linear}
#mStrokes.sgp .sgskip{appearance:none;height:36px;margin:0;padding:0 18px 2px;border:0;border-radius:0;background:url(art/m_tape3.webp) center/100% 100% no-repeat;color:#2A2437;font:900 14px/1 var(--font-head);letter-spacing:.06em;text-transform:uppercase;rotate:-3deg;cursor:pointer;filter:drop-shadow(0 2px 0 rgba(23,19,32,.25))}
#mStrokes.sgp .sgskip:active{transform:translateY(2px)}
#mStrokes.sgp .sgnote{margin:0;font:700 12px/1.2 var(--font-ui);color:rgba(23,19,32,.72);text-align:center}
#mStrokes.sgp .sgnote[hidden]{display:none}
/* the tabs: one card per category on the ink band (upright the band is the tab row's own) */
#mStrokes.sgp .sgtabs{position:relative;z-index:5;order:2;flex:none;align-self:center;display:flex;align-items:flex-end;gap:16px;margin:12px 0 0}
#mStrokes.sgp .sgtabs::before{content:"";position:absolute;left:50%;top:50%;z-index:-1;width:100vw;height:calc(100% + 46px);transform:translate(-50%,-48%);background:url(art/sg_ink.webp) 0 50%/auto 100% repeat-x;pointer-events:none}
#mStrokes.sgp .sgtab{appearance:none;position:relative;display:flex;flex-direction:column;width:var(--tabw);margin:0;padding:0;border:0;border-radius:12px;background:var(--ink0);color:#fff;text-align:center;cursor:pointer;
  box-shadow:0 0 0 2px var(--ink0),0 5px 0 rgba(0,0,0,.4);transform-origin:50% 100%;transition:transform .16s cubic-bezier(.2,1.4,.4,1),box-shadow .16s,filter .16s;-webkit-tap-highlight-color:transparent}
#mStrokes.sgp .sgtab[data-cat="special"]{--tc:#FFA526;--tc2:#F28C0C}
#mStrokes.sgp .sgtab[data-cat="skill"]{--tc:#22C9B8;--tc2:#12AE9E}
#mStrokes.sgp .sgtab[data-cat="item"]{--tc:#FF5F62;--tc2:#EC4248}
#mStrokes.sgp .sgtab .sgtt{display:block;padding:5px 4px 4px;font:400 12px/1 var(--font-display);letter-spacing:.01em;color:#fff;white-space:nowrap}
#mStrokes.sgp .sgtab .sgtb{position:relative;display:flex;flex-direction:column;align-items:center;gap:4px;margin:0 3px 3px;padding:5px 4px 6px;border-radius:0 0 9px 9px;background:repeating-linear-gradient(135deg,var(--tc) 0 7px,var(--tc2) 7px 14px)}
#mStrokes.sgp .sgtab .sgti{display:grid;place-items:center;width:44px;height:38px}
#mStrokes.sgp .sgtab .sgti .stimg{width:40px;height:40px;object-fit:contain;filter:drop-shadow(1px 2px 0 rgba(23,19,32,.3))}
#mStrokes.sgp .sgtab .sgti svg{width:34px;height:34px}
#mStrokes.sgp .sgdots{display:flex;gap:4px;justify-content:center}
#mStrokes.sgp .sgdots i{width:9px;height:9px;border-radius:50%;background:rgba(17,16,20,.28);box-shadow:inset 0 0 0 1.6px rgba(17,16,20,.55)}
#mStrokes.sgp .sgdots i.own{background:#fff;box-shadow:0 0 0 1.6px var(--ink0)}
#mStrokes.sgp .sgdots i.cr{background:var(--sel);box-shadow:0 0 0 1.6px var(--ink0)}
#mStrokes.sgp .sgtab:not(.on){filter:brightness(.8) saturate(.9)}
#mStrokes.sgp .sgtab.on{transform:scale(1.08);box-shadow:0 0 0 3px var(--sel),0 0 0 5.5px var(--ink0),0 7px 0 rgba(0,0,0,.4);z-index:1}
#mStrokes.sgp .sgtab:active{transform:scale(.96)}
#mStrokes.sgp .sgtab.on:active{transform:scale(1.04)}
#mStrokes.sgp .sgtab.fresh::after{content:"";position:absolute;right:-4px;top:-4px;width:13px;height:13px;border-radius:50%;background:#FF2D55;box-shadow:0 0 0 2.5px var(--ink0);animation:stdot 1.2s ease-in-out infinite}
#mStrokes.sgp .sgtab:focus-visible,#mStrokes.sgp .sgcard:focus-visible,#mStrokes.sgp .sgpill:focus-visible,#mStrokes.sgp .sgback:focus-visible,#mStrokes.sgp .sgdo:focus-visible{outline:3px solid #fff;outline-offset:3px}
/* the panel: dark and see-through, the tags hung from a bar taped at its top */
#mStrokes.sgp .sgpanel{position:relative;z-index:3;order:3;flex:0 1 auto;max-height:var(--panh);min-height:0;margin-top:24px;display:flex;flex-direction:column;border-radius:22px;background:var(--panel);box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.07),0 8px 22px rgba(23,19,32,.22)}
#mStrokes.sgp .sghang{position:absolute;left:50%;top:-8px;z-index:2;width:40%;max-width:190px;height:17px;border-radius:999px;background:linear-gradient(#3A3A42,#232328);box-shadow:inset 0 1.5px 0 rgba(255,255,255,.16),0 0 0 2px var(--ink0),0 3px 0 rgba(0,0,0,.35);transform:translateX(-50%)}
#mStrokes.sgp .sghang::after{content:"";position:absolute;left:58%;top:-9px;width:62px;height:21px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:rotate(-7deg);filter:drop-shadow(0 1px 0 rgba(23,19,32,.2))}
#mStrokes.sgp .sgscroll{flex:1 1 auto;min-height:0;overflow-x:hidden;overflow-y:auto;overscroll-behavior:contain;padding:22px 14px 18px;-webkit-mask:linear-gradient(transparent,#000 12px,#000 calc(100% - 18px),transparent);mask:linear-gradient(transparent,#000 12px,#000 calc(100% - 18px),transparent);scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.4) transparent;-webkit-overflow-scrolling:touch}
#mStrokes.sgp .sgscroll::-webkit-scrollbar{width:5px}
#mStrokes.sgp .sgscroll::-webkit-scrollbar-thumb{border-radius:999px;background:rgba(255,255,255,.38)}
#mStrokes.sgp .sggrid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px 12px;padding:2px 2px 4px}
#mStrokes.sgp .sggrid[hidden]{display:none}
#mStrokes.sgp .sggrid.in .sgcard{animation:sgin .3s cubic-bezier(.2,1.2,.35,1) both}
#mStrokes.sgp .sggrid.in .sgcard:nth-child(2){animation-delay:.03s}#mStrokes.sgp .sggrid.in .sgcard:nth-child(3){animation-delay:.06s}#mStrokes.sgp .sggrid.in .sgcard:nth-child(4){animation-delay:.09s}#mStrokes.sgp .sggrid.in .sgcard:nth-child(5){animation-delay:.12s}#mStrokes.sgp .sggrid.in .sgcard:nth-child(6){animation-delay:.15s}
@keyframes sgin{from{opacity:0;transform:translateY(-8px) rotate(-3deg)}}
/* a hang tag: a hook, the mottled card with the picture, a lime strip with two icons */
#mStrokes.sgp .sgcard{appearance:none;position:relative;display:flex;flex-direction:column;min-width:0;margin:0;padding:10px 0 0;border:0;background:none;color:var(--black);cursor:pointer;transform-origin:50% 0;transition:transform .15s cubic-bezier(.2,1.3,.4,1);-webkit-tap-highlight-color:transparent}
#mStrokes.sgp .sgcard .sghook{position:absolute;left:50%;top:0;z-index:2;width:14px;height:16px;margin-left:-7px;border-radius:50% 50% 45% 45%;box-shadow:inset 0 0 0 2.6px #A9A9B2,0 1px 0 rgba(0,0,0,.4)}
#mStrokes.sgp .sgcard .sgcb{position:relative;display:block;aspect-ratio:1/.64;border-radius:11px 11px 3px 3px;background:#F7F1E3 url(art/sg_card.webp) 30% 20%/260% auto;box-shadow:inset 0 0 0 1.5px rgba(23,19,32,.14)}
#mStrokes.sgp .sgcard:nth-child(3n+2) .sgcb{background-position:70% 60%}#mStrokes.sgp .sgcard:nth-child(3n) .sgcb{background-position:10% 85%}
#mStrokes.sgp .sgcard .sgcb::before{content:"";position:absolute;left:50%;top:5px;width:8px;height:8px;margin-left:-4px;border-radius:50%;background:#6A6A72;box-shadow:inset 0 1.5px 0 rgba(0,0,0,.35)}
#mStrokes.sgp .sgcard .sgca{position:absolute;left:13%;right:13%;top:8%;bottom:7%;isolation:isolate}
#mStrokes.sgp .sgcard .sgca .stimg{position:absolute;inset:0;z-index:1;width:100%;height:100%;object-fit:contain;filter:drop-shadow(1px 2px 0 rgba(23,19,32,.22))}
#mStrokes.sgp .sgcard .sgca svg{position:absolute;inset:12%;z-index:1;width:76%;height:76%}
#mStrokes.sgp .sgcard .sgcf{display:flex;justify-content:center;gap:6px;padding:4px 0 5px;border-radius:3px 3px 11px 11px;background:#A9DC2C;box-shadow:inset 0 1.5px 0 rgba(255,255,255,.4),inset 0 -2px 0 rgba(0,0,0,.12)}
#mStrokes.sgp .sgcard .sgcf i{display:grid;place-items:center;width:21px;height:21px;border-radius:6px;background:#1E1E23;color:#fff;box-shadow:0 1.5px 0 rgba(0,0,0,.3)}
#mStrokes.sgp .sgcard .sgcf svg{width:14px;height:14px}
#mStrokes.sgp .sgcard:active{transform:scale(.95)}
/* the one you're looking at: a magenta splat behind it, a thick yellow ring, a touch bigger */
#mStrokes.sgp .sgcard.sel{transform:scale(1.06);z-index:1}
#mStrokes.sgp .sgcard.sel::after{content:"";position:absolute;left:-4px;right:-4px;top:7px;bottom:-4px;border-radius:14px;box-shadow:0 0 0 4px var(--sel),0 0 0 6px var(--ink0);pointer-events:none}
#mStrokes.sgp .sgcard.sel .sgca::before{content:"";position:absolute;inset:-6% -10%;z-index:0;background:var(--mag);-webkit-mask:url(art/m_splat.webp) center/contain no-repeat;mask:url(art/m_splat.webp) center/contain no-repeat}
/* what a tag says: the rank it opens at, its craft time, the bench's countdown, New, and a stamp on the one you have on */
#mStrokes.sgp .sgcard .sgst{position:absolute;left:50%;bottom:6%;z-index:2;display:flex;align-items:center;gap:3px;padding:3px 7px 3px 6px;border-radius:999px;background:var(--ink0);color:#fff;font:800 10px/1 var(--font-ui);letter-spacing:.04em;white-space:nowrap;transform:translateX(-50%)}
#mStrokes.sgp .sgcard .sgst svg{width:10px;height:10px}
#mStrokes.sgp .sgcard .sgst.cr{background:var(--sel);color:var(--ink0);font-variant-numeric:tabular-nums}
#mStrokes.sgp .sgcard .sgpb{position:absolute;left:10%;right:10%;bottom:3px;z-index:2;height:4px;border-radius:999px;background:rgba(23,19,32,.15);overflow:hidden}
#mStrokes.sgp .sgcard .sgpb i{display:block;height:100%;width:var(--p,0%);background:var(--ink0);transition:width .5s linear}
#mStrokes.sgp .sgcard .sgeq{position:absolute;right:-5px;top:2px;z-index:3;display:grid;place-items:center;width:24px;height:24px;border-radius:7px;background:var(--ink0);color:var(--sel);transform:rotate(8deg);box-shadow:0 2px 0 rgba(0,0,0,.3)}
#mStrokes.sgp .sgcard .sgeq svg{width:15px;height:15px}
#mStrokes.sgp .sgcard .sgnew{position:absolute;left:-5px;top:4px;z-index:3;padding:4px 6px 3px;border-radius:6px;background:#FF2D55;color:#fff;font:400 10px/1 var(--font-display);transform:rotate(-8deg);box-shadow:0 0 0 2px var(--ink0)}
#mStrokes.sgp .sgcard.lock .sgca,#mStrokes.sgp .sgcard.raw .sgca{filter:grayscale(.85) opacity(.6)}
#mStrokes.sgp .sgcard.lock .sgcb{background-color:#E2DCCF}
#mStrokes.sgp .sgcard.lock .sgcf{background:#8DA65A}
#mStrokes.sgp .sgcard.lock .sgcf i{opacity:.55}
#mStrokes.sgp .sgcard.soon{cursor:default}
#mStrokes.sgp .sgcard.soon .sgcb{background:transparent;box-shadow:inset 0 0 0 2px rgba(255,255,255,.22)}
#mStrokes.sgp .sgcard.soon .sgca{opacity:.35;filter:grayscale(1)}
#mStrokes.sgp .sgcard.soon .sgcf{background:rgba(255,255,255,.1);box-shadow:none;color:rgba(255,255,255,.55);font:800 10px/14px var(--font-ui);letter-spacing:.08em;text-transform:uppercase;min-height:21px;align-items:center}
#mStrokes.sgp .sgcard.soon .sghook{box-shadow:inset 0 0 0 2.6px rgba(255,255,255,.25)}
/* back, Info and Test, and the badge */
#mStrokes.sgp .sgback{appearance:none;position:absolute;z-index:6;left:var(--gx);top:var(--gt);display:flex;flex-direction:column;align-items:center;justify-content:center;width:var(--bk);height:var(--bk);margin:0;padding:2px 0 0;border:0;border-radius:50%;background:radial-gradient(circle at 38% 28%,#A876FF,#7B3BEA 58%,#5F22C8);color:#fff;box-shadow:0 0 0 3px var(--ink0),0 5px 0 var(--ink0);cursor:pointer;-webkit-tap-highlight-color:transparent}
#mStrokes.sgp .sgback svg{width:46%;height:46%}
#mStrokes.sgp .sgback span{margin-top:-1px;font:400 11px/1 var(--font-display);letter-spacing:.01em}
#mStrokes.sgp .sgback:active{transform:translateY(3px);box-shadow:0 0 0 3px var(--ink0),0 2px 0 var(--ink0)}
#mStrokes.sgp .sgpills{position:relative;z-index:6;order:4;flex:none;align-self:center;display:flex;gap:14px;margin-top:16px}
#mStrokes.sgp .sgpill{appearance:none;min-width:92px;height:var(--pillh);margin:0;padding:0 18px;border:0;border-radius:10px;background:linear-gradient(#4A4A52,#34343B);color:#fff;font:400 16px/1 var(--font-display);transform:skewX(-14deg);box-shadow:0 0 0 2.5px var(--ink0),0 4px 0 var(--ink0);cursor:pointer;-webkit-tap-highlight-color:transparent}
#mStrokes.sgp .sgpill>span{display:inline-block;transform:skewX(14deg)}
#mStrokes.sgp .sgpill:active{transform:skewX(-14deg) translateY(3px);box-shadow:0 0 0 2.5px var(--ink0),0 1px 0 var(--ink0)}
#mStrokes.sgp .sgpill[hidden]{display:none}
#mStrokes.sgp.sgtest #sgTest{background:linear-gradient(#FFE97A,#FFD93B);color:var(--ink0)}
#mStrokes.sgp .sgbadge{appearance:none;position:absolute;z-index:6;right:var(--gr);top:calc(var(--gt) + 4px);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-width:50px;height:50px;margin:0;padding:0 6px;border:0;border-radius:12px;background:var(--ink0);color:#fff;font:400 13px/1 var(--font-display);font-variant-numeric:tabular-nums;box-shadow:0 3px 0 rgba(0,0,0,.3);cursor:pointer}
#mStrokes.sgp .sgbadge .sgbi{display:grid;place-items:center;width:20px;height:22px;color:var(--sel)}
#mStrokes.sgp .sgbadge .sgbi svg,#mStrokes.sgp .sgbadge .sgbi .stimg{width:22px;height:22px;object-fit:contain}
#mStrokes.sgp .sgbadge.cr{background:var(--sel);color:var(--ink0);box-shadow:0 0 0 2px var(--ink0),0 3px 0 rgba(0,0,0,.3)}
#mStrokes.sgp .stucode{position:relative;display:flex;flex-direction:column;align-items:center;gap:8px;margin:12px 0 2px}
#mStrokes.sgp .stucode .ulink{color:rgba(255,255,255,.62);font-size:12px}
#mStrokes.sgp .stucode .uform input{border-color:#fff;background:#fff;color:var(--black)}
#mStrokes.sgp .sttoast{bottom:auto;top:calc(var(--gt) + 64px);z-index:9}
/* (Test: the demo bigger, the panel and the tabs out of its way) */
#mStrokes.sgp.sgtest .sgpanel,#mStrokes.sgp.sgtest .sgtabs,#mStrokes.sgp.sgtest .sgfoot{display:none}
#mStrokes.sgp.sgtest .sgrot{bottom:12px}
/* landscape: the panel on the left, the stroke on the right (a transform's demo), the ink band along the bottom with the tabs on it,
   back at its left and Info and Test at its right */
@media (min-aspect-ratio:1/1){
  #mStrokes.sgp{--bk:clamp(54px,16vh,72px);--band:clamp(70px,20vh,100px);--tabw:clamp(84px,12vw,116px);--pillh:clamp(32px,9.5vh,40px);--panw:55%;display:block;padding:0}
  #mStrokes.sgp .sgink{display:block;bottom:calc(var(--gb) - var(--band) * .18);height:calc(var(--band) * 1.5)}
  #mStrokes.sgp .sgtabs::before{display:none}
  #mStrokes.sgp .sgback{top:auto;bottom:calc(var(--gb) + 8px)}
  #mStrokes.sgp .sgtabs{position:absolute;left:calc(var(--gx) + var(--bk) + 22px);bottom:calc(var(--gb) + 8px);margin:0;gap:14px}
  #mStrokes.sgp .sgtab .sgtt{padding:4px 4px 3px;font-size:clamp(10px,2.9vh,13px)}
  #mStrokes.sgp .sgtab .sgtb{gap:3px;padding:4px 4px 5px}
  #mStrokes.sgp .sgtab .sgti{height:clamp(24px,7.2vh,38px)}
  #mStrokes.sgp .sgtab .sgti .stimg{width:clamp(26px,8vh,40px);height:clamp(26px,8vh,40px)}
  #mStrokes.sgp .sgdots i{width:7px;height:7px}
  #mStrokes.sgp .sgpills{position:absolute;left:auto;right:var(--gr);bottom:calc(var(--gb) + var(--band) * .26);margin:0;gap:12px}
  #mStrokes.sgp .sgpill{min-width:clamp(76px,10vw,96px)}
  #mStrokes.sgp .sgpanel{position:absolute;top:calc(var(--gt) + 10px);bottom:calc(var(--gb) + var(--band) + 6px);left:var(--gx);width:calc(var(--panw) - var(--gx));max-height:none;margin:0}
  #mStrokes.sgp .sgscroll{padding:21px 14px 18px}
  #mStrokes.sgp .sggrid{gap:12px 14px}
  #mStrokes.sgp .sgcard .sgcb{aspect-ratio:auto;height:clamp(52px,18.5vh,96px)}
  #mStrokes.sgp .sgshow{position:absolute;left:calc(var(--panw) + 12px);right:var(--gr);top:var(--gt);bottom:calc(var(--gb) + var(--band) + 12px);min-height:0}
  #mStrokes.sgp .sgban{left:14px;top:6px;max-width:calc(100% - 100px);transform:skewX(-11deg)}
  #mStrokes.sgp .sgbadge{top:calc(var(--gt) + 10px);flex-direction:row;gap:5px;min-width:0;height:34px;padding:0 10px 0 7px;border-radius:10px;font-size:15px}
  #mStrokes.sgp .sgrot{bottom:52px;right:0}
  #mStrokes.sgp.sgnoted:not(.sgtest) .sgrot{bottom:72px}
  #mStrokes.sgp .sgfoot{bottom:0;flex-direction:row;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:4px 10px}
  #mStrokes.sgp .sgline{flex:1 1 150px;text-align:left;font-size:13px}
  #mStrokes.sgp .sgnote{order:-1;flex-basis:100%;text-align:right}
  #mStrokes.sgp .sttoast{top:auto;bottom:calc(var(--gb) + var(--band) + 12px)}
  #mStrokes.sgp .sgart{top:56px;bottom:52px}
  #mStrokes.sgp.sgnoted .sgart{bottom:70px}
  /* (specials and skills: no demo, everything centred) */
  #mStrokes.sgp:not(.sgx) .sgpanel{left:50%;width:min(64%,580px);transform:translateX(-50%);top:calc(var(--gt) + 60px);bottom:calc(var(--gb) + var(--band) + 54px)}
  #mStrokes.sgp:not(.sgx) .sgshow{left:var(--gx)}
  #mStrokes.sgp:not(.sgx) .sgban{left:50%;transform:translateX(-50%) skewX(-11deg);max-width:calc(100% - 2 * 130px)}
  #mStrokes.sgp:not(.sgx) .sgstage{display:none}
  #mStrokes.sgp:not(.sgx) .sgfoot{left:50%;right:auto;width:min(64%,580px);transform:translateX(-50%);bottom:6px}
  #mStrokes.sgp:not(.sgx) .sgcard .sgcb{height:clamp(52px,21vh,104px)}
  #mStrokes.sgp:not(.sgx) .sgfoot{display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:12px;row-gap:2px;align-items:center}
  #mStrokes.sgp:not(.sgx) .sgline{grid-column:1;grid-row:1 / 3;align-self:center;max-width:none}
  #mStrokes.sgp.sgnoted:not(.sgx) .sgline{grid-row:1;align-self:end}
  #mStrokes.sgp:not(.sgx) .sgact{grid-column:2;grid-row:1 / 3}
  #mStrokes.sgp:not(.sgx) .sgnote{grid-column:1;grid-row:2;align-self:start;text-align:left}
  #mStrokes.sgp.sglearn:not(.sgx) .sgpanel{left:var(--gx);transform:none}
  #mStrokes.sgp.sglearn:not(.sgx) .sgban{left:calc(min(64vw,580px) / 2)}
  #mStrokes.sgp.sglearn:not(.sgx) .sgfoot{left:0;right:0;width:auto;transform:none}
  #mStrokes.sgp.sgtest .sgshow{left:var(--gx);bottom:calc(var(--gb) + var(--band) * .26 + var(--pillh) + 14px)}
  #mStrokes.sgp.sgtest .sgban{left:50%;transform:translateX(-50%) skewX(-11deg)}
  #mStrokes.sgp.sgtest .sgink{display:none}
}
@media (min-aspect-ratio:1/1) and (max-height:430px){#mStrokes.sgp .sgcard .sgcf{padding:3px 0 4px}#mStrokes.sgp .sgcard .sgcf i{width:18px;height:18px;border-radius:5px}#mStrokes.sgp .sgcard .sgcf svg{width:12px;height:12px}#mStrokes.sgp .sgban b{font-size:21px}#mStrokes.sgp .sgban{padding:6px 26px 6px 17px}}
@media (max-aspect-ratio:1/1) and (max-height:700px){#mStrokes.sgp{--panh:min(30vh,210px);--bk:50px}#mStrokes.sgp .sgban b{font-size:20px}}
@media (max-width:359px){#mStrokes.sgp{--tabw:90px}#mStrokes.sgp .sgtabs{gap:10px}#mStrokes.sgp .sggrid{gap:12px 9px}}
/* the Info sheet: the stroke's numbers and how you get it */
#stPop.sginfo .sgnums{display:grid;grid-template-columns:repeat(auto-fit,minmax(76px,1fr));justify-self:stretch;gap:8px;margin:2px 0 0;padding:0;text-align:left}
#stPop.sginfo .sgnums div{display:flex;flex-direction:column;gap:3px;padding:8px 10px 9px;border:2px solid var(--black);border-radius:6px;background:#fff;box-shadow:3px 3px 0 var(--black)}
#stPop.sginfo .sgnums dt{font:800 10px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:var(--sk-deep,#8A5A0E)}
#stPop.sginfo .sgnums dd{margin:0;font:900 15px/1.15 var(--font-head);color:var(--black)}
#stPop.sginfo .sghow{display:flex;align-items:center;gap:8px;margin:4px 0 2px;padding:9px 12px;border-radius:6px;background:rgba(23,19,32,.07);font:700 13px/1.3 var(--font-ui);color:var(--black)}
#stPop.sginfo .sghow svg{flex:none;width:16px;height:16px}
#stPop.sginfo .stpbtns,#stPop.sginfo .stptimer,#stPop.sginfo .stpnote{display:none}
@media (min-aspect-ratio:1/1) and (max-height:600px){#stPop.sginfo .stpop{max-height:calc(100% - 8px)}#stPop.sginfo .stphead{padding-top:10px}#stPop.sginfo .stpbody{grid-template-areas:"art name" "art desc" "art does" "how nums";row-gap:7px}#stPop.sginfo .stpname{font-size:28px}#stPop.sginfo .sgnums{grid-area:nums;grid-template-columns:repeat(auto-fit,minmax(92px,1fr))}#stPop.sginfo .sgnums div{padding:6px 8px 7px}#stPop.sginfo .sgnums dd{font-size:13px}#stPop.sginfo .sghow{grid-area:how;align-self:stretch;flex-direction:column;align-items:flex-start;justify-content:center;gap:4px;margin:2px 0 0;padding:7px 9px;font-size:12px}#stPop.sginfo .sghow svg{width:14px;height:14px}}
@media (prefers-reduced-motion:reduce){#mStrokes.sgp .sgtab,#mStrokes.sgp .sgcard,#mStrokes.sgp .sggrid.in .sgcard,#mStrokes.sgp .sgart .stimg,#mStrokes.sgp .sgban .sgflag::after,#mStrokes.sgp .sgtab.fresh::after{animation:none;transition:none}}
"""

JS_TILE = r"""// (v312) the gear screen: a hang tag per stroke, a tab card per category, the stroke you're looking at up front
const ST_HAMMER = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12.6 3.6l7.8 7.8-2.5 2.5-2.1-2.1-8.4 8.4a1.9 1.9 0 0 1-2.7-2.7l8.4-8.4-2.1-2.1z" fill="currentColor"/></svg>';
const ST_GLASS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 3h11M6.5 21h11M8 3c0 5.2 8 5.6 8 9s-8 3.8-8 9M16 3c0 5.2-8 5.6-8 9s8 3.8 8 9" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>';
const ST_CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 12.5l4.6 4.6L19.5 6.7" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const stPct = o => (100 * (1 - craftLeft() / (o.craft * 60000))).toFixed(1) + '%';
const ST_CATS = { special: { h: 'Special strokes', s: 'What the orb gives you', rail: 'stSpecialRail', slot: 'stSpecial', kind: 'Special stroke' }, skill: { h: 'Skills', s: 'Always on, all match', rail: 'stSkillRail', slot: 'stSkill', kind: 'Skill' }, item: { h: 'Transforms', s: 'You start every match holding it', rail: 'stItemRail', slot: 'stItem', kind: 'Transform' } };
let stCat = 'special';
const stCatOf = id => stIsItem(id) ? 'item' : stIsSkill(id) ? 'skill' : 'special';
const stListOf = cat => cat === 'item' ? ST_ITEMS : cat === 'skill' ? SKILLS : SPECIALS;
const stOnOf = cat => cat === 'item' ? strokeItem() : cat === 'skill' ? strokeSkill() : strokeSpecial();
// the icons on a tag's strip: what the stroke is about (two each)
const SG_TRAIT = {
  ko: ['Knocks rivals out', '<path d="M12 2.6l2.3 5 5.4-1.3-2.4 5 4.3 3.3-5.4.7.4 5.5L12 17.5l-4.6 3.3.4-5.5-5.4-.7 4.3-3.3-2.4-5 5.4 1.3z" fill="currentColor"/>'],
  wide: ['Paints wide', '<path d="M3 15c3-4 6 1 9-3s6 1 9-3" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round"/>'],
  time: ['Lasts a while', '<circle cx="12" cy="12" r="8.4" fill="none" stroke="currentColor" stroke-width="2.6"/><path d="M12 7.4V12l3.2 2.2" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/>'],
  aim: ['Fires at rivals', '<circle cx="12" cy="12" r="7.6" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="12" cy="12" r="2.4" fill="currentColor"/><path d="M12 1.8v4.4M12 17.8v4.4M1.8 12h4.4M17.8 12h4.4" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/>'],
  mine: ['Waits on the floor', '<path d="M4 18.5a8 8 0 0 1 16 0z" fill="currentColor"/><path d="M12 10.5V7.4M12 7.4l3-2.6" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/><circle cx="16.2" cy="4" r="1.7" fill="currentColor"/>'],
  dash: ['Charges ahead', '<path d="M4 7l6 5-6 5M12 7l6 5-6 5" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'],
  loop: ['Comes back to you', '<path d="M5 15.5a7 7 0 1 1 7 4.5H8" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><path d="M10.6 16.8 7.4 20l3.2 3" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'],
  fly: ['Up high', '<path d="M12 3c3.2 2.4 4.6 6 4.6 10.2V16H7.4v-2.8C7.4 9 8.8 5.4 12 3z" fill="currentColor"/><path d="M9.6 18.4h4.8L12 22z" fill="currentColor"/>'],
  big: ['Grows big', '<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="12" r="3.4" fill="currentColor"/>'],
  freeze: ['Freezes rivals', '<path d="M12 2.5v19M3.8 7.2l16.4 9.6M3.8 16.8l16.4-9.6M9.4 4.3 12 6.6l2.6-2.3M9.4 19.7 12 17.4l2.6 2.3" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'],
  speed: ['Faster', '<path d="M13.5 3 6 13.5h5.5L10 21l8-11h-5.6z" fill="currentColor"/>'],
  rain: ['In the rain', '<path d="M7 14.5a4.2 4.2 0 0 1-.4-8.4 5.6 5.6 0 0 1 10.6 1.4 3.5 3.5 0 0 1 .3 7z" fill="currentColor"/><path d="M8.5 17.5l-1 2.6M12.5 17.5l-1 2.6M16.5 17.5l-1 2.6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'],
  sun: ['The sun can’t burn you', '<circle cx="12" cy="12" r="4.2" fill="currentColor"/><path d="M12 2.6v2.6M12 18.8v2.6M2.6 12h2.6M18.8 12h2.6M5.4 5.4l1.8 1.8M16.8 16.8l1.8 1.8M5.4 18.6l1.8-1.8M16.8 7.2l1.8-1.8" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/>'],
  two: ['Two at once', '<rect x="3" y="7" width="8.4" height="10" rx="2.4" fill="currentColor"/><rect x="12.6" y="7" width="8.4" height="10" rx="2.4" fill="none" stroke="currentColor" stroke-width="2.2"/>'],
  orb: ['Keeps the orb', '<circle cx="12" cy="12.6" r="6.6" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M12 8.2l1.2 2.7 2.9.3-2.2 1.9.7 2.9-2.6-1.6-2.6 1.6.7-2.9-2.2-1.9 2.9-.3z" fill="currentColor"/>']
};
const SG_TRAITS = { rocket: ['fly', 'ko'], giant: ['big', 'wide'], freeze: ['freeze', 'time'], swim: ['speed', 'rain'], repel: ['rain', 'sun'], pockets: ['two', 'orb'], roller: ['wide', 'ko'], turret: ['aim', 'time'], trap: ['mine', 'ko'], whirl: ['dash', 'ko'], boom: ['loop', 'ko'] };
const sgTraits = id => (SG_TRAITS[id] || ['wide', 'ko']).map(k => '<i title="' + SG_TRAIT[k][0] + '"><svg viewBox="0 0 24 24" aria-hidden="true">' + SG_TRAIT[k][1] + '</svg></i>').join('');
// the stroke you're looking at in each tab (null: the one you have on)
const SG_PICK = { special: null, skill: null, item: null };
const sgSelId = cat => { const p = SG_PICK[cat]; return p && stListOf(cat).some(o => o.id === p) ? p : stOnOf(cat); };
function stSetCat(cat, quiet) {
  if (!ST_CATS[cat]) cat = 'special'; const was = stCat; stCat = cat;
  for (const k in ST_CATS) { const on = k === cat, sl = $(ST_CATS[k].slot), r = $(ST_CATS[k].rail); sl.classList.toggle('on', on); sl.setAttribute('aria-selected', on ? 'true' : 'false'); sl.tabIndex = on ? 0 : -1; r.hidden = !on; }
  const pg = $('mStrokes'); if (pg.dataset.cat !== cat) pg.dataset.cat = cat; pg.classList.toggle('sgx', cat === 'item'); $('stPanel').dataset.cat = cat; $('stCatH').textContent = ST_CATS[cat].h; $('stCatS').textContent = ST_CATS[cat].s;
  if (was !== cat) { if (SGD.test) sgTestEnd(true); if (!quiet) { AU.ui(); buzz(5); const r = $(ST_CATS[cat].rail); r.classList.remove('in'); void r.offsetWidth; r.classList.add('in'); $('sgScroll').scrollTop = 0; } sgShowRender(); }
}
function stTile(o, skill) {
  const d = strokesOf(), item = skill === 'item', cat = item ? 'item' : skill ? 'skill' : 'special', own = d.own.includes(o.id), on = own && stOnOf(cat) === o.id, cr = !!d.craft && d.craft.id === o.id, ready = own && !on && d.fresh === o.id, lock = !own && !cr && !stDue(o), sel = sgSelId(cat) === o.id;
  const st = on ? 'equipped' : cr ? 'crafting, ' + mmss(craftLeft()) + ' left' : own ? (ST_STARTERS.includes(o.id) ? 'yours' : 'owned') : lock ? 'locked until rank ' + stRank(o) : 'craft it in ' + o.craft + ' minutes';
  const tag = cr ? '<span class="sgst cr">' + ST_GLASS + '<b>' + mmss(craftLeft()) + '</b></span><i class="sgpb"><i></i></i>' : lock ? '<span class="sgst lk">' + STROKE_LOCK + 'Rank ' + stRank(o) + '</span>' : !own ? '<span class="sgst raw">' + ST_GLASS + o.craft + ' min</span>' : '';
  return '<button class="sgcard' + (on ? ' on' : '') + (cr ? ' crafting' : '') + (ready ? ' ready' : '') + (!own && !cr ? ' raw' : '') + (lock ? ' lock' : '') + (sel ? ' sel' : '') + '" type="button" data-' + (item ? 'it' : skill ? 'sk' : 'st') + '="' + o.id + '" aria-pressed="' + sel + '" aria-label="' + escAttr(o.name + ', ' + st) + '"' + (cr ? ' style="--p:' + stPct(o) + '"' : '') + '>'
    + '<i class="sghook" aria-hidden="true"></i><span class="sgcb"><span class="sgca">' + STROKE_ICON[o.id] + '</span>' + tag + '</span><span class="sgcf" aria-hidden="true">' + sgTraits(o.id) + '</span>'
    + (on ? '<i class="sgeq" aria-hidden="true">' + ST_CHECK + '</i>' : '') + (ready ? '<i class="sgnew" aria-hidden="true">New</i>' : '') + '</button>';
}
"""

JS_POP = r"""// (v312) a stroke's Info sheet: what it does, its numbers and how you get it (the page's own button crafts and equips)
let stPopId = null, stPopT = 0;
const SG_NUMS = {
  rocket: [['Hovers', '4.5 s'], ['Splash', 'Knocks out'], ['Steer', 'Your mark']],
  giant: [['Lasts', '5 s'], ['Size', '3 times'], ['Pound', '1.5 times as wide']],
  freeze: [['Frozen', '5 s'], ['Reach', 'Every rival'], ['Wind-up', '0.9 s']],
  swim: [['Glide', '8% faster'], ['In the rain', 'Twice as fast']],
  repel: [['Rain', 'Can’t water you down'], ['Sun', 'Can’t burn you'], ['Pace', 'A fifth slower']],
  pockets: [['Holds', '2 power-ups'], ['Orb', 'Kept till used']],
  roller: [['Lasts', '9 s'], ['Paint', 'Refilled'], ['Roll over', 'Knocks out']],
  turret: [['Lasts', '7 s'], ['Each hit', '7% of their paint'], ['3 in a row', 'Seeing stars'], ['Empty', 'Knocked out']],
  trap: [['Arms in', '0.6 s'], ['Down at once', '2'], ['Set off', 'Knocks out']],
  whirl: [['Wind-up', '1.3 s'], ['Charge', '1.1 s'], ['In its path', 'Knocked out']],
  boom: [['Out and back', 'About 2 s'], ['Paints', 'Its whole loop'], ['Clipped', 'Knocked out']]
};
function stPopTick() {}
function stPopRender() {
  if (!stPopId) return; const id = stPopId, o = stDef(id); if (!o) return closeStPop(true);
  const d = strokesOf(), skill = stIsSkill(id), item = stIsItem(id), own = d.own.includes(id), on = own && stOnOf(stCatOf(id)) === id, cr = !!d.craft && d.craft.id === id;
  const card = $('stPop').querySelector('.stpop'); card.classList.toggle('skill', skill || item); card.dataset.cat = stCatOf(id); card.dataset.id = id;
  $('stPopKind').textContent = item ? 'Transform' : skill ? 'Skill' : 'Special stroke';
  const ow = $('stPopOwn'); ow.hidden = !own; ow.innerHTML = ST_CHECK + (on ? 'Equipped' : ST_STARTERS.includes(id) ? 'Yours' : 'Crafted');
  if ($('stPopArt').dataset.id !== id) { $('stPopArt').dataset.id = id; $('stPopArt').innerHTML = STROKE_ICON[id]; }
  $('stPopName').textContent = o.name; $('stPopDesc').textContent = o.desc;
  $('stPopDoes').innerHTML = o.does.map(t => '<li>' + t + '</li>').join('');
  $('sgNums').innerHTML = (SG_NUMS[id] || []).map(n => '<div><dt>' + n[0] + '</dt><dd>' + n[1] + '</dd></div>').join('');
  const how = ST_STARTERS.includes(id) ? 'Yours from the start' : own ? 'Crafted: it’s yours' : cr ? 'On the bench: ' + mmss(craftLeft()) + ' to go' : (item ? 'Opens at rank ' + stRank(o) + ', then craft it in ' + o.craft + ' minutes' : 'Craft it in ' + o.craft + ' minutes, from rank ' + stRank(o));
  $('sgHow').innerHTML = (own ? ST_CHECK : cr ? ST_GLASS : stDue(o) ? ST_HAMMER : STROKE_LOCK) + '<span>' + how + '</span>';
}
function openStPop(id) {
  if (!stDef(id) || !strokesOpen()) return; if (SGD.test) sgTestEnd(true);
  clearTimeout(stPopT); stPopId = id; const m = $('stPop'), was = m.hidden; m.hidden = false; stPopRender(); AU.ui(); buzz(6);
  if (was) { const c = m.querySelector('.stpop'); c.style.animation = 'none'; void c.offsetWidth; c.style.animation = ''; }
  setTimeout(() => { if (stPopId === id) $('stPopX').focus({ preventScroll: true }); }, 40);
}
function closeStPop(quiet) { clearTimeout(stPopT); if (!stPopId) return; stPopId = null; $('stPop').hidden = true; if (!quiet) AU.ui(); if (strokesOpen()) $('sgInfo').focus({ preventScroll: true }); }
"""

JS_RENDER = r"""// (v312) the page: the tabs (what you have on in each, a dot per stroke), the tags, the badge, the stroke you're looking at
function sgTabs() {
  const d = strokesOf();
  for (const k in ST_CATS) { const list = stListOf(k), on = list.find(x => x.id === stOnOf(k)) || list[0], el = $(ST_CATS[k].slot + 'Now');
    if (el.dataset.id !== on.id) { el.dataset.id = on.id; el.innerHTML = STROKE_ICON[on.id]; }
    $(ST_CATS[k].slot).setAttribute('aria-label', ST_CATS[k].kind + ': ' + on.name); $(ST_CATS[k].slot).classList.toggle('fresh', !!d.fresh && stCatOf(d.fresh) === k);
    $('sgDots_' + k).innerHTML = list.map(o => '<i class="' + (d.own.includes(o.id) ? 'own' : d.craft && d.craft.id === o.id ? 'cr' : '') + '"></i>').join(''); }
}
const SG_RANK = '<svg viewBox="0 0 46 54" aria-hidden="true"><path d="M23 2.6 43 8.6V29c0 11.4-9 18.6-20 22.6C12 47.6 3 40.4 3 29V8.6z" fill="currentColor"/><path d="M23 14l3.4 7 7.6 1-5.5 5.2 1.4 7.6-6.9-3.7-6.9 3.7 1.4-7.6L12 22l7.6-1z" fill="#111014"/></svg>';
function sgBadge() {
  const d = strokesOf(), b = $('sgBadge'), c = d.craft, lv = repOf(store.xp || 0).lv;
  b.classList.toggle('cr', !!c);
  if (c) { if ($('sgBadgeI').dataset.k !== c.id) { $('sgBadgeI').dataset.k = c.id; $('sgBadgeI').innerHTML = STROKE_ICON[c.id]; } $('sgBadgeT').textContent = mmss(craftLeft()); b.setAttribute('aria-label', spName(c.id) + ' on the bench, ' + mmss(craftLeft()) + ' to go'); }
  else { if ($('sgBadgeI').dataset.k !== 'rank') { $('sgBadgeI').dataset.k = 'rank'; $('sgBadgeI').innerHTML = SG_RANK; } $('sgBadgeT').textContent = lv; b.setAttribute('aria-label', 'Your rank: ' + lv); }
}
// the stroke you're looking at: its banner, its line, its picture (or the demo), and one button: Equip, Craft, or the bench and Skip
function sgShowRender() {
  const cat = stCat, id = sgSelId(cat), o = stDef(id); if (!o) return;
  const d = strokesOf(), own = d.own.includes(id), on = own && stOnOf(cat) === id, cr = !!d.craft && d.craft.id === id, busy = !!d.craft && !cr, due = stDue(o);
  $('sgKind').textContent = ST_CATS[cat].kind; $('sgName').textContent = o.name; $('sgLine').textContent = o.desc; sgFitName();
  const art = $('sgArt'); if (art.dataset.id !== id) { const first = !art.dataset.id; art.dataset.id = id; art.innerHTML = STROKE_ICON[id]; if (!first) { art.classList.remove('sgpopin'); void art.offsetWidth; art.classList.add('sgpopin'); } }
  const b = $('sgDo'), tm = $('sgTimer'), sk = $('sgSkip');
  tm.hidden = sk.hidden = !cr; b.hidden = cr; b.classList.toggle('craft', !own && !cr && due && !busy); b.classList.toggle('on', on);
  if (own) { b.disabled = on; b.innerHTML = '<span>' + (on ? ST_CHECK + 'Equipped' : 'Equip') + '</span>'; b.setAttribute('aria-label', on ? o.name + ' is equipped' : 'Equip ' + o.name); }
  else if (!cr) { b.disabled = busy || !due; b.innerHTML = '<span>' + (due ? 'Craft<small>' + o.craft + ' min</small>' : STROKE_LOCK + 'Rank ' + stRank(o)) + '</span>'; b.setAttribute('aria-label', due ? 'Craft ' + o.name + ', ' + o.craft + ' minutes' : o.name + ' opens at rank ' + stRank(o)); }
  if (cr) sgBench(o);
  const note = own || cr ? '' : !due ? 'Reach rank ' + stRank(o) + ' to craft it' : busy ? 'One craft at a time: ' + spName(d.craft.id) + ' is on the bench' : '';
  $('sgNote').hidden = !note; $('sgNote').textContent = note; $('mStrokes').classList.toggle('sgnoted', !!note);
  $('sgTest').hidden = cat !== 'item'; SGD.rectDirty = true;
  sgDemoPick(cat === 'item' ? id : null);
}
function sgFitName() { const nb = $('sgName'); nb.style.fontSize = ''; if (!nb.clientWidth) return; let fs = parseFloat(getComputedStyle(nb).fontSize) || 24, n = 0; while (nb.scrollWidth > nb.clientWidth + 1 && fs > 13 && n++ < 10) { fs -= 1.5; nb.style.fontSize = fs + 'px'; } }
function sgBench(o) { $('sgTime').textContent = mmss(craftLeft()); $('sgBar').style.setProperty('--p', stPct(o)); }
// a tag picked: the one to look at; the one you're already looking at, if it's yours, goes on
function sgPick(id, quiet) {
  const cat = stCatOf(id), o = stDef(id); if (!o || !strokesOpen()) return; const d = strokesOf();
  if (cat !== stCat) stSetCat(cat, true);
  if (sgSelId(cat) === id && !quiet) { if (d.own.includes(id) && stOnOf(cat) !== id) sgEquip(id); else { AU.ui(); buzz(4); kick($('sgBan'), 'bump'); } return; }
  SG_PICK[cat] = id; if (d.fresh === id) { d.fresh = null; save(); }
  if (!quiet) { AU.ui(); buzz(5); }
  for (const el of $(ST_CATS[cat].rail).querySelectorAll('.sgcard')) { const on = (el.dataset.st || el.dataset.sk || el.dataset.it) === id; el.classList.toggle('sel', on); el.setAttribute('aria-pressed', on ? 'true' : 'false'); }
  renderStrokes();
}
function sgEquip(id) { if (stIsItem(id)) equipItem(id); else if (stIsSkill(id)) equipSkill(id); else equipSpecial(id); }
function renderStrokes() {
  const d = strokesOf(); craftTick();
  sgTabs(); sgBadge();
  const soon = '<span class="sgcard soon" aria-hidden="true"><i class="sghook"></i><span class="sgcb"><span class="sgca">' + stImg('soon') + '</span></span><span class="sgcf">More soon</span></span>';
  $('stSpecialRail').innerHTML = SPECIALS.map(o => stTile(o, false)).join('') + (SPECIALS.length % 3 ? soon : '');
  $('stSkillRail').innerHTML = SKILLS.map(o => stTile(o, true)).join('') + (SKILLS.length % 3 ? soon : ''); $('stItemRail').innerHTML = ST_ITEMS.map(o => stTile(o, 'item')).join('') + (ST_ITEMS.length % 3 ? soon : '');
  stSetCat(stCat, true); sgShowRender(); paintAbil(); stPopRender();
}
function strokesFrame() { if (!strokesOpen()) return; const d = strokesOf(); if (d.craft) { const id = d.craft.id; if (!craftTick()) { renderStrokes(); stToast(stReady(id)); } else { const sp = stDef(id), p = stPct(sp), t = mmss(craftLeft()); for (const el of document.querySelectorAll('#mStrokes .sgcard.crafting')) { el.style.setProperty('--p', p); const b = el.querySelector('.sgst b'); if (b) b.textContent = t; } $('sgBadgeT').textContent = t; if (sgSelId(stCat) === id) sgBench(sp); if (stPopId === id) stPopRender(); } } }
function openStrokes() {
  if (state !== 'menu' || building || lookOpen || shopOpen || strokesOpen()) return;
  if (menuPage === 'worlds') { closeSeason(); $('mWorld').hidden = true; } if (menuPage === 'events') closeEvents();
  if (!store.abilSeen) { store.abilSeen = 1; save(); } /* (v306: having seen it opens Play online) */ stSkillSel = null; stCat = 'special'; SG_PICK.special = SG_PICK.skill = SG_PICK.item = null; SGD.yaw = SG_YAW0; menuPage = 'strokes'; menu.dataset.page = 'strokes'; $('mHome').hidden = true; $('mStrokes').hidden = false; document.body.classList.add('evon', 'stpage'); closeSide(true); renderStrokes();
  for (const c of $('mStrokes').querySelectorAll('.sgtab')) { c.style.animation = 'none'; void c.offsetWidth; c.style.animation = ''; } { const r = $('stSpecialRail'); r.classList.remove('in'); void r.offsetWidth; r.classList.add('in'); }
  clearInterval(stTick); stTick = setInterval(strokesFrame, 500); SGD.rectDirty = true; setTimeout(() => $('stBack').focus({ preventScroll: true }), 40);
}
function closeStrokes() { if (!strokesOpen()) return; closeStPop(true); sgTestEnd(true); sgStop(); clearInterval(stTick); $('mStrokes').hidden = true; $('mStrokes').classList.remove('sglearn'); document.body.classList.remove('evon', 'stpage'); menuPage = 'home'; menu.dataset.page = 'home'; $('mHome').hidden = false; paintAbil(); renderLobbyUI && renderLobbyUI(); setTimeout(() => $('abilBtn').focus({ preventScroll: true }), 40); }
"""

JS_HANDLERS = r"""$('stBack').addEventListener('click', () => { AU.init(); if (stPopId) return closeStPop(); if (SGD.test) { AU.ui(); return sgTestEnd(); } AU.ui(); closeStrokes(); });
$('sgSkip').addEventListener('click', () => { AU.init(); craftSkip(); });
for (const k of ['special', 'skill', 'item']) $(ST_CATS[k].slot).addEventListener('click', () => { AU.init(); stSetCat(k); });
$('sgTabs').addEventListener('keydown', e => { const ks = ['special', 'skill', 'item'], i = ks.indexOf(stCat), dl = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0; if (!dl) return; e.preventDefault(); const k = ks[(i + dl + 3) % 3]; stSetCat(k); $(ST_CATS[k].slot).focus(); });
for (const k of ['special', 'skill', 'item']) $(ST_CATS[k].rail).addEventListener('click', e => { const b = e.target.closest('.sgcard[data-st], .sgcard[data-sk], .sgcard[data-it]'); if (!b) return; AU.init(); sgPick(b.dataset.st || b.dataset.sk || b.dataset.it); });
$('sgDo').addEventListener('click', () => { AU.init(); const id = sgSelId(stCat), d = strokesOf(), o = stDef(id); if (!o) return;
  if (d.own.includes(id)) { if (stOnOf(stCat) !== id) sgEquip(id); return; }
  if (d.craft) { AU.nope(); stToast('One craft at a time'); return; } if (!stDue(o)) { AU.nope(); stToast('Reach rank ' + stRank(o) + ' to craft ' + spName(id)); return; } craftStart(id); });
$('sgInfo').addEventListener('click', () => { AU.init(); openStPop(sgSelId(stCat)); });
$('sgTest').addEventListener('click', () => { AU.init(); AU.ui(); if (SGD.test) sgTestEnd(); else sgTestStart(); });
$('sgBadge').addEventListener('click', () => { AU.init(); const d = strokesOf(); if (d.craft) { sgPick(d.craft.id, true); AU.ui(); return; } AU.ui(); stToast('Rank ' + repOf(store.xp || 0).lv); });
$('stPopX').addEventListener('click', () => { AU.init(); closeStPop(); });
$('stPop').addEventListener('click', e => { if (e.target === $('stPop')) { AU.init(); closeStPop(); } });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && stPopId) { e.preventDefault(); e.stopPropagation(); closeStPop(); } }, true);
// (the demo: a drag on it, or the round stick, turns the view)
{ const st = $('sgStage');
  st.addEventListener('pointerdown', e => { if (!SGD.on) return; SGD.yawTo = null; SGD.drag = { x: e.clientX, y0: SGD.yaw, id: e.pointerId }; try { st.setPointerCapture(e.pointerId); } catch (x) {} });
  st.addEventListener('pointermove', e => { const g = SGD.drag; if (!g || g.id !== e.pointerId) return; SGD.yaw = g.y0 - (e.clientX - g.x) * 0.012; });
  const up = e => { if (SGD.drag && SGD.drag.id === e.pointerId) SGD.drag = null; }; st.addEventListener('pointerup', up); st.addEventListener('pointercancel', up); }
$('sgRot').addEventListener('click', () => { AU.init(); AU.ui(); buzz(4); SGD.yawTo = SGD.yaw - Math.PI / 4; });
"""

JS_DEMO = r"""
// ---------- (v312) the transform demo: your own axolotl (your colour and what you wear) using the transform you're looking at, on a
// small pad against a rival, looping. It's drawn with the game itself (the same character, the same roller, turret, trap, tornado and
// boomerang, posed by the same code that draws them in a match) into the game's canvas, under a window cut in the page's wall: the
// wall's own picture is drawn there first, so the two meet without a seam. Only while it shows (the Transforms tab, nothing over it,
// the app in view); its own code makes no new objects per frame. It lives far off every stage, on a layer of its own (5) that sees the
// lobby's lights ----------
const SG_L = 5, SG_X = 640, SG_Z = 640, SG_R = 1.8, SG_YAW0 = 0.42;
const SGD = { built: false, on: false, ready: false, kind: '', id: null, t: 0, loop: 0, side: 1, yaw: SG_YAW0, yawTo: null, drag: null, test: false, rectDirty: true, rect: { x: 0, y: 0, w: 0, h: 0 }, insT: 0, insB: 0, hole: '', ev: {}, calls: 0, cpu: 0, frames: 0 };
const sgT1 = new THREE.Vector3(), sgT2 = new THREE.Vector3(), sgT3 = new THREE.Vector3(), sgM = new THREE.Matrix4(), sgQ = new THREE.Quaternion(), sgS = new THREE.Vector3(), sgVp = new THREE.Vector4(), sgSc = new THREE.Vector4(), sgCol = new THREE.Color(), sgHemiC = new THREE.Color(), sgHemiG = new THREE.Color(), sgSunC = new THREE.Color(), sgSunP = new THREE.Vector3(), sgSunT = new THREE.Vector3(), sgRimP = new THREE.Vector3(), sgRimT = new THREE.Vector3(), sgRimC = new THREE.Color(), sgRigC = new THREE.Color(), sgDir = new THREE.Vector3();
const SG_PAPER = '#F6F0E2';
// the steps Test captions, from each transform's own lines
const SG_CAP = { roller: [[0.7, 0], [1.9, 1], [3.6, 2]], turret: [[0.5, 0], [1.0, 1], [2.3, 2]], trap: [[0.8, 0], [2.6, 1], [3.6, 2]], whirl: [[0.3, 0], [1.9, 1], [2.6, 2]], boom: [[0.7, 0], [1.3, 1], [2.3, 2]] };
const SG_T = { roller: 6.2, turret: 5.6, trap: 6.4, whirl: 6.0, boom: 5.4 };
function sgLayer(o) { o.traverse(m => { if (m.material && m.material.depthFunc === THREE.GreaterDepth) { m.layers.mask = 0; return; } m.layers.set(SG_L); }); }
// a character for the demo: the game's own (made as a CPU's is), in a team's colour
function sgActor(team, mine) {
  const D = newBlob(team, true); D.st = 'play'; ipReset(D);
  const L = makeCpuLook(D, TEAMS[team].wet); D.look = L; L.wear = makeWear(L.body);
  L.wearing = mine ? myLook : { eyes: 'round', head: null, back: null, mouth: null, eye: null, side: null, neck: null, lash: null, arms: null, iris: 'brown' };
  attachSlime(L.V, L.wear, L.mat.color);
  for (const o of [L.shadow, L.warn, L.warnFill, L.foeMark, L.mark, L.V.puddle]) if (o) { scene.remove(o); o.visible = false; } L.V.puddle = null;
  sgLayer(L.drop); sgLayer(L.stars); L.drop.visible = false; L.stars.visible = false;
  // its own soft shadow on the pad
  const sh = new THREE.Mesh(SGD.shG, lobbyShadow.material); sh.layers.set(SG_L); sh.renderOrder = 2; SGD.root.add(sh);
  return { D, L, V: L.V, team, mine, sh, show: true, ko: 0, kx: 0, kz: 0, pop: 0, col: new THREE.Color(TEAMS[team].wet), wt: { yaw: 0, pitch: 0.85, look: [0, 0.1] } };
}
function sgBuild() {
  if (SGD.built) return true;
  if (!VP.slime || !(AXOC.S.ready || SLIME.S.ready)) return false; // (the characters' bodies aren't in yet)
  SGD.built = true;
  const root = SGD.root = new THREE.Group(); root.position.set(SG_X, 0, SG_Z); root.visible = false; scene.add(root); SGD.shG = new THREE.PlaneGeometry(1, 1).rotateX(-Math.PI / 2);
  // the pad: a thick disc of paper with an inked edge, on a soft shadow of its own; its top is a canvas the demo paints on
  const cv = document.createElement('canvas'); cv.width = cv.height = 256; SGD.pcv = cv; SGD.pg = cv.getContext('2d');
  const base = document.createElement('canvas'); base.width = base.height = 256; { const g = base.getContext('2d'); g.fillStyle = SG_PAPER; g.fillRect(0, 0, 256, 256); g.strokeStyle = 'rgba(80,110,170,.13)'; g.lineWidth = 1.2; for (let i = 8; i < 256; i += 16) { g.beginPath(); g.moveTo(i, 0); g.lineTo(i, 256); g.moveTo(0, i); g.lineTo(256, i); g.stroke(); } } SGD.base = base;
  SGD.ptex = new THREE.CanvasTexture(cv); SGD.ptex.colorSpace = THREE.SRGBColorSpace; SGD.ptex.anisotropy = 4;
  const top = new THREE.Mesh(new THREE.CircleGeometry(SG_R, 72).rotateX(-Math.PI / 2), toon(0xFFFFFF, { map: SGD.ptex })); top.renderOrder = 1;
  const side = new THREE.Mesh(new THREE.CylinderGeometry(SG_R + 0.02, SG_R * 0.96, 0.3, 72, 1, true).translate(0, -0.15, 0), toon(0x2A2437));
  const rim = new THREE.Mesh(new THREE.RingGeometry(SG_R - 0.05, SG_R + 0.025, 72).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: 0x171320 })); rim.position.y = 0.006; rim.renderOrder = 3;
  const gsh = new THREE.Mesh(SGD.shG, lobbyShadow.material); gsh.position.y = -0.31; gsh.scale.set(SG_R * 2.9, 1, SG_R * 2.3); gsh.renderOrder = 0;
  root.add(top, side, rim, gsh); SGD.pad = top;
  // the characters: you and a rival
  SGD.A = sgActor(0, true); SGD.B = sgActor(1, false); SGD.AB = [SGD.A, SGD.B];
  // drops of paint (the game's own drop, in one draw), rings (the game's shockwave), shots (the turret's own glob and its outline)
  const PN = 72; SGD.pim = new THREE.InstancedMesh(partG, toon(0xFFFFFF), PN); SGD.pim.instanceMatrix.setUsage(THREE.DynamicDrawUsage); SGD.pim.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(PN * 3), 3); SGD.pim.instanceColor.setUsage(THREE.DynamicDrawUsage); SGD.pim.frustumCulled = false; SGD.pim.count = 0; SGD.pim.renderOrder = 8; root.add(SGD.pim);
  SGD.parts = []; for (let i = 0; i < PN; i++) SGD.parts.push({ x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, life: 0, sz: 1, r: 1, g: 1, b: 1, rest: false }); SGD.pi = 0;
  SGD.rings = []; for (let i = 0; i < 4; i++) { const m = new THREE.Mesh(fxRingG, new THREE.MeshBasicMaterial({ color: 0xFFFFFF, transparent: true, opacity: 1, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -10, polygonOffsetUnits: -10, fog: false })); m.rotation.x = -Math.PI / 2; m.renderOrder = 7; m.visible = false; root.add(m); SGD.rings.push({ m, t: 1, r: 1 }); }
  const SN = 14; SGD.sim = new THREE.InstancedMesh(shotGeo, shotIM.material, SN); SGD.sink = new THREE.InstancedMesh(shotGeo, shotInkM, SN); SGD.sim.instanceColor = new THREE.InstancedBufferAttribute(new Float32Array(SN * 3).fill(1), 3);
  for (const im of [SGD.sim, SGD.sink]) { im.instanceMatrix.setUsage(THREE.DynamicDrawUsage); im.frustumCulled = false; im.count = 0; root.add(im); } SGD.sim.renderOrder = 33; SGD.sink.renderOrder = 32.6;
  SGD.shots = []; for (let i = 0; i < SN; i++) SGD.shots.push({ on: false, x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, t: 0, ph: Math.random() * 6, hit: false });
  // the transforms' own pieces: the trap, the tornado and its lane, the boomerang
  SGD.trap = makeTrapMesh(SGD.A.D); SGD.trap.visible = false; root.add(SGD.trap);
  SGD.wg = new THREE.Group(); SGD.wspin = new THREE.Group(); SGD.wg.add(SGD.wspin); SGD.wpm = whirlPaintM.clone(); SGD.wsm = whirlStreakM.clone(); { const a = new THREE.Mesh(WHIRL_G.paint, SGD.wpm), b = new THREE.Mesh(WHIRL_G.streak, SGD.wsm); a.renderOrder = 36; b.renderOrder = 37; a.frustumCulled = b.frustumCulled = false; SGD.wspin.add(a, b); } SGD.wg.visible = false; root.add(SGD.wg);
  { const N = 10, pos = new Float32Array((N + 1) * 6), uv = new Float32Array((N + 1) * 4), idx = []; for (let i = 0; i <= N; i++) { uv.set([i / N, 0, i / N, 1], i * 4); if (i < N) { const k = i * 2; idx.push(k, k + 1, k + 2, k + 1, k + 3, k + 2); } }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); g.setIndex(idx); SGD.lane = new THREE.Mesh(g, whirlLaneM.clone()); SGD.lane.frustumCulled = false; SGD.lane.renderOrder = 7; SGD.lane.visible = false; SGD.laneP = pos; root.add(SGD.lane); }
  { const M = boomMesh(tmat(SGD.A.D)); SGD.boom = M.g; SGD.bspin = M.spin; SGD.boom.visible = false; root.add(SGD.boom); }
  sgLayer(root);
  // the camera, and the wall's picture drawn in screen space (the same tile, the same size, from the same corner as the page's)
  SGD.cam = new THREE.PerspectiveCamera(30, 1, 0.1, 60); SGD.cam.layers.set(SG_L);
  const tex = new THREE.TextureLoader().load('art/sg_bg.webp', () => { SGD.bgU.uOk.value = 1; }); tex.wrapS = tex.wrapT = THREE.RepeatWrapping; tex.colorSpace = THREE.NoColorSpace; tex.generateMipmaps = true; tex.minFilter = THREE.LinearMipmapLinearFilter;
  SGD.bgU = { uTex: { value: tex }, uOk: { value: 0 }, uTile: { value: 560 }, uH: { value: 800 }, uBase: { value: new THREE.Vector3(0xCB / 255, 0xE4 / 255, 0x5A / 255) } };
  const tri = new THREE.BufferGeometry(); tri.setAttribute('position', new THREE.Float32BufferAttribute([-1, -1, 0, 3, -1, 0, -1, 3, 0], 3));
  const bm = new THREE.ShaderMaterial({ uniforms: SGD.bgU, depthTest: false, depthWrite: false, vertexShader: 'void main(){ gl_Position = vec4(position.xy, 0.0, 1.0); }',
    fragmentShader: 'precision highp float; uniform sampler2D uTex; uniform float uOk, uTile, uH; uniform vec3 uBase; void main(){ vec2 p = vec2(gl_FragCoord.x, uH - gl_FragCoord.y) / uTile; vec3 c = uOk > 0.5 ? texture2D(uTex, vec2(p.x, 1.0 - p.y)).rgb : uBase; gl_FragColor = vec4(c, 1.0); }' });
  const q = new THREE.Mesh(tri, bm); q.frustumCulled = false; SGD.bgS = new THREE.Scene(); SGD.bgS.add(q); SGD.bgC = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  hemi.layers.enable(SG_L); sun.layers.enable(SG_L); vicRim.layers.enable(SG_L); // (the lobby's lights: the shaders the lobby made fit)
  if (HI && TH) try { themeEnv(TH); } catch (e) {}
  sgPaintClear();
  // the shaders it needs and the lobby hasn't made yet: made in the background where the browser can
  SGD.ready = true;
  try { if (renderer.compileAsync && renderer.extensions.has('KHR_parallel_shader_compile')) { SGD.ready = false; root.visible = true; for (const A of SGD.AB) { A.L.drop.visible = true; A.V.rig.visible = A.V.tur.visible = true; } SGD.trap.visible = SGD.wg.visible = SGD.boom.visible = SGD.lane.visible = true;
    const p = renderer.compileAsync(root, SGD.cam, scene), p2 = renderer.compileAsync(SGD.A.L.drop, SGD.cam, scene), p3 = renderer.compileAsync(SGD.B.L.drop, SGD.cam, scene), p4 = renderer.compileAsync(SGD.bgS, SGD.bgC);
    root.visible = false; for (const A of SGD.AB) { A.L.drop.visible = false; A.V.rig.visible = A.V.tur.visible = false; } SGD.trap.visible = SGD.wg.visible = SGD.boom.visible = SGD.lane.visible = false;
    Promise.all([p, p2, p3, p4]).catch(() => {}).then(() => { SGD.ready = true; }); setTimeout(() => { SGD.ready = true; }, 4000); } } catch (e) { SGD.ready = true; }
  return true;
}
// ---- the pad's paint
function sgPaintClear() { const g = SGD.pg; g.globalAlpha = 1; g.globalCompositeOperation = 'source-over'; g.drawImage(SGD.base, 0, 0); SGD.pdirty = true; }
function sgPaintFade(k) { const g = SGD.pg; g.globalAlpha = k; g.drawImage(SGD.base, 0, 0); g.globalAlpha = 1; SGD.pdirty = true; }
const sgPx = v => 128 + v * 128 / SG_R;
function sgDab(x, z, r, css) { const g = SGD.pg; g.fillStyle = css; g.beginPath(); g.arc(sgPx(x), sgPx(z), r * 128 / SG_R, 0, 6.2832); g.fill(); SGD.pdirty = true; }
function sgStripe(x0, z0, x1, z1, w, css) { const g = SGD.pg; g.strokeStyle = css; g.lineCap = 'round'; g.lineWidth = w * 128 / SG_R; g.beginPath(); g.moveTo(sgPx(x0), sgPx(z0)); g.lineTo(sgPx(x1), sgPx(z1)); g.stroke();
  const l = Math.hypot(x1 - x0, z1 - z0); if (l > 0.02 && Math.random() < 0.7) { const nx = -(z1 - z0) / l, nz = (x1 - x0) / l, s = Math.random() < 0.5 ? -1 : 1; sgDab(x1 + nx * s * w * (0.42 + Math.random() * 0.14), z1 + nz * s * w * (0.42 + Math.random() * 0.14), w * (0.06 + Math.random() * 0.08), css); } SGD.pdirty = true; }
function sgSplat(x, z, r, css) { sgDab(x, z, r * 0.62, css); for (let i = 0; i < 9; i++) { const a = Math.random() * 6.2832, d = r * (0.45 + Math.random() * 0.5); sgDab(x + Math.cos(a) * d, z + Math.sin(a) * d, r * (0.12 + Math.random() * 0.2), css); } for (let i = 0; i < 6; i++) { const a = Math.random() * 6.2832, d = r * (1 + Math.random() * 0.45); sgDab(x + Math.cos(a) * d, z + Math.sin(a) * d, r * (0.04 + Math.random() * 0.06), css); } }
// ---- drops, rings, shots (positions on the pad: x right, z toward you, y up from its top)
function sgPart(x, y, z, vx, vy, vz, life, c, sz) { const p = SGD.parts[SGD.pi]; SGD.pi = (SGD.pi + 1) % SGD.parts.length; p.x = x; p.y = y; p.z = z; p.vx = vx; p.vy = vy; p.vz = vz; p.life = life; p.sz = sz || 1; p.r = c.r; p.g = c.g; p.b = c.b; p.rest = false; }
function sgBurst(x, z, c, n, up, out) { for (let i = 0; i < n; i++) { const a = Math.random() * 6.2832, s = (out || 2.6) * (0.5 + Math.random() * 0.8); sgPart(x, 0.3, z, Math.cos(a) * s, (up || 3) * (0.6 + Math.random() * 0.8), Math.sin(a) * s, 0.55 + Math.random() * 0.4, c, 0.6 + Math.random() * 0.6); } }
function sgRing(x, z, r, hex) { let f = SGD.rings[0]; for (const q of SGD.rings) if (q.t > f.t) f = q; f.t = 0; f.r = r; f.m.position.set(x, 0.03, z); f.m.material.color.setHex(hex); f.m.visible = true; }
function sgFx(dt) {
  const P0 = SGD.parts, im = SGD.pim, ca = im.instanceColor.array; let n = 0;
  for (let i = 0; i < P0.length; i++) { const p = P0[i]; if (p.life <= 0) continue; p.life -= dt; if (p.life <= 0) continue;
    if (!p.rest) { p.vy -= 12 * dt; p.x += p.vx * dt; p.y += p.vy * dt; p.z += p.vz * dt; if (p.y < 0.04 && p.x * p.x + p.z * p.z < SG_R * SG_R) { p.y = 0.04; p.vx = p.vy = p.vz = 0; p.rest = true; } else if (p.y < -3) p.life = 0; }
    const sc = Math.max(0.01, Math.min(1, p.life * 2)) * p.sz * 0.9, sp = p.rest ? 0 : Math.hypot(p.vx, p.vy, p.vz);
    sgT1.set(p.x, p.y, p.z); if (sp > 0.6) { sgT2.set(p.vx, p.vy, p.vz).normalize(); sgQ.setFromUnitVectors(sgT3.set(0, 0, 1), sgT2); sgS.set(sc * 0.85, sc * 0.85, sc * (1 + sp * 0.09)); } else { sgQ.identity(); sgS.set(sc * 1.15, sc * 0.6, sc * 1.15); }
    sgM.compose(sgT1, sgQ, sgS); im.setMatrixAt(n, sgM); ca[n * 3] = p.r; ca[n * 3 + 1] = p.g; ca[n * 3 + 2] = p.b; n++; }
  im.count = n; im.visible = n > 0; if (n) { im.instanceMatrix.needsUpdate = true; im.instanceColor.needsUpdate = true; }
  for (const f of SGD.rings) { if (f.t >= 1) continue; f.t = Math.min(1, f.t + dt / 0.6); const e = 1 - Math.pow(1 - f.t, 3); f.m.scale.setScalar(0.3 + e * f.r); f.m.material.opacity = 1 - f.t; if (f.t >= 1) f.m.visible = false; }
}
// ---- the characters on the pad
function sgAt(A, x, z, yaw) { const D = A.D; D.x = SG_X + x; D.z = SG_Z + z; D.y = 0; if (yaw !== undefined) D.yaw = yaw; D.spd = 0; D.turn = 0; A.V.yawD = undefined; }
const sgLX = A => A.D.x - SG_X, sgLZ = A => A.D.z - SG_Z;
function sgFace(A, yaw, dt, k) { const D = A.D, e = wrapA(yaw - D.yaw), r = (k || 7) * dt, step = clamp(e, -r, r); D.yaw += step; D.turn = clamp(step / Math.max(dt, 1e-3) / 9, -1, 1); return Math.abs(e) < 0.05; }
function sgGo(A, tx, tz, spd, dt) { const D = A.D, dx = tx - sgLX(A), dz = tz - sgLZ(A), d = Math.hypot(dx, dz); if (d < 0.03) { D.spd = Math.max(0, D.spd - dt * 12); return true; } sgFace(A, Math.atan2(dx, dz), dt, 6); const s = Math.min(spd, d / Math.max(dt, 1e-3), D.spd + dt * 14); D.spd = s; D.x += Math.sin(D.yaw) * s * dt; D.z += Math.cos(D.yaw) * s * dt; return false; }
function sgHalt(A, dt) { A.D.spd = Math.max(0, A.D.spd - dt * 10); A.D.turn *= 0.8; }
const sgYawTo = (A, B) => Math.atan2(sgLX(B) - sgLX(A), sgLZ(B) - sgLZ(A));
const sgYawCam = A => Math.atan2(Math.sin(SGD.yaw) * 9 - sgLX(A), Math.cos(SGD.yaw) * 9 - sgLZ(A)); // (toward the camera, wherever it's been turned)
function sgWatch(A, B) { const D = A.D, rel = wrapA((B ? Math.atan2(B.D.x - D.x, B.D.z - D.z) : sgYawCam(A)) - D.yaw), w = A.wt; w.yaw = clamp(rel, -1.2, 1.2) * 0.85; w.pitch = B ? 0.85 : 1.0; w.look[0] = clamp(rel * 0.1, -0.12, 0.12); w.look[1] = B ? 0.1 : 0.14; D.ip.watch = w; }
function sgKO(B, c) { const x = sgLX(B), z = sgLZ(B); B.show = false; B.ko = 1; B.D.st = 'ko'; sgBurst(x, z, B.col, 22, 4.2, 3.2); sgRing(x, z, 1.25, 0xFFFFFF); sgSplat(x, z, 0.42, c); B.L.drop.visible = false; B.L.stars.visible = false; }
function sgBack(B, x, z, yaw) { sgAt(B, x, z, yaw); const D = B.D; D.st = 'play'; D.paint = 1; D.dry = false; D.flatT = 0; D.stunT = 0; D.squash = 0.8; D.wob = 1; D.emoT = 0; B.show = true; B.ko = 0; B.pop = 0; ipReset(D); sgRing(x, z, 0.8, TEAMS[B.team].wet); sgBurst(x, z, B.col, 10, 2.6, 1.6); }
function sgReset(A) { const D = A.D; D.st = 'play'; D.power = null; D.turret = null; D.rollT = 0; D.flatT = 0; D.stunT = 0; D.paint = 1; D.dry = false; D.squash = 0; D.wob = 0; D.spd = 0; D.turn = 0; D.air = false; D.vy = 0; D.emoT = 0; A.show = true; A.ko = 0; ipReset(D); }
// ---- each transform, start to end, then again from the other side
function sgLoop() {
  // (the ones that travel start the next time from the other side)
  const k = SGD.kind, s = SGD.side = k === 'turret' || k === 'boom' ? 1 : SGD.loop++ % 2 ? -1 : 1, A = SGD.A, B = SGD.B; SGD.t = 0; SGD.ev = {};
  sgReset(A); sgReset(B); SGD.trap.visible = SGD.wg.visible = SGD.lane.visible = SGD.boom.visible = false; for (const q of SGD.shots) q.on = false; if (SGD.bm) SGD.bm.on = false; if (SGD.whirl) SGD.whirl.ph = '';
  if (k === 'roller') { sgAt(A, -1.3 * s, 0.3); sgAt(B, 0.55 * s, -0.12); }
  else if (k === 'turret') { sgAt(A, -1.05 * s, 0.25); sgAt(B, 0.95 * s, -0.2); }
  else if (k === 'trap') { sgAt(A, -1.3 * s, 0.16); sgAt(B, 0.6 * s, -1.15); }
  else if (k === 'whirl') { sgAt(A, -1.3 * s, 0.12); sgAt(B, 0.65 * s, 0.04); }
  else { sgAt(A, -1.1 * s, 0.33); sgAt(B, 0.9 * s, -0.25); }
  A.D.yaw = sgYawCam(A); B.D.yaw = sgYawTo(B, A); A.V.yawD = B.V.yawD = undefined;
  SGD.capI = -1; sgCap();
}
const sgOnce = k => SGD.ev[k] ? false : (SGD.ev[k] = true);
function sgStep(dt) {
  SGD.t += dt; const t = SGD.t, s = SGD.side, A = SGD.A, B = SGD.B, DA = A.D, DB = B.D, cA = TEAMS[0].css, cB = TEAMS[1].css;
  DA.ip.expr = null; DB.ip.expr = null; DA.ip.watch = DB.ip.watch = null;
  if (B.show && DB.st === 'play') { if (!(DB.stunT > 0) && DB.spd < 0.1) sgFace(B, sgYawTo(B, A) + 0.18 * Math.sin(t * 1.3), dt, 3); sgWatch(B, A); DB.ip.expr = DB.stunT > 0 ? 'dizzy' : DB.paint < 0.6 ? 'scared' : t < 0.6 ? 'curious' : null; }
  if (DB.stunT > 0) DB.stunT = Math.max(0, DB.stunT - dt);
  const k = SGD.kind;
  if (k === 'roller') {
    if (t < 0.7) { sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'ready'; }
    else if (sgOnce('on')) { DA.power = { type: 'roller', t: 9 }; DA.paint = 1; emote(DA, 'glee', 0.9); sgRing(sgLX(A), sgLZ(A), 1.1, TEAMS[0].wet); sgBurst(sgLX(A), sgLZ(A), A.col, 12, 3, 2.4); }
    if (t >= 0.7 && t < 3.4) { const lx = sgLX(A), lz = sgLZ(A), fin = 1.3 * s;
      if (t < 1.05) sgFace(A, Math.atan2(s, 0), dt, 8);
      else if ((fin - lx) * s > 0.02) { const roll = DA.rollT > 0, sp = roll ? 4.2 : 2.3; sgGo(A, fin, lz, sp, dt);
        if (!roll && B.show && Math.abs(sgLX(B) - lx) < 1.0 && sgOnce('roll')) { DA.rollT = ROLL_T; DA.squash = 0.5; }
        sgStripe(lx, lz, sgLX(A), sgLZ(A), 0.95, cA);
        if (B.show && roll && Math.hypot(sgLX(B) - sgLX(A), sgLZ(B) - sgLZ(A)) < 0.5) { sgKO(B, cA); emote(DA, 'glee', 1.2); } }
      else sgHalt(A, dt);
      if (DA.rollT > 0) DA.rollT = Math.max(0, DA.rollT - dt); }
    if (t >= 3.4 && t < 3.6) { sgHalt(A, dt); sgFace(A, sgYawCam(A), dt, 5); }
    if (t >= 3.6) { if (sgOnce('off')) { DA.power = null; sgRing(sgLX(A), sgLZ(A), 0.9, 0xFFFFFF); } sgFace(A, sgYawCam(A), dt, 5); sgWatch(A, null); DA.ip.expr = 'glee'; }
    if (t >= 4.1 && sgOnce('back')) sgBack(B, -0.55 * s, -0.12, sgYawTo(B, A));
  } else if (k === 'turret') {
    if (t < 0.5) { sgFace(A, sgYawCam(A) + wrapA(sgYawTo(A, B) - sgYawCam(A)) * 0.5, dt, 4); sgWatch(A, B); DA.ip.expr = 'ready'; }
    else if (sgOnce('plant')) { DA.turret = { t: TURRET_T, cd: 0.45, kick: 0, ph: 0, aim: 0.4 }; DA.squash = 0.8; DA.wob = 1; emote(DA, 'glee', 0.8); sgRing(sgLX(A), sgLZ(A), 1.3, TEAMS[0].wet); sgBurst(sgLX(A), sgLZ(A), A.col, 12, 2.6, 2.4); }
    if (DA.turret) { const T = DA.turret; sgFace(A, B.show ? sgYawTo(A, B) : DA.yaw + 0.25 * dt, dt, 4); T.kick = Math.max(0, T.kick - dt * 6); T.t = TURRET_T * clamp(1 - (t - 0.5) / 2.9, 0.03, 1);
      if (t > 0.95 && t < 3.2) { T.cd -= dt; if (T.cd <= 0) { T.cd = 0.15; sgShoot(A, B); } }
      if (t >= 3.4) { DA.turret = null; DA.squash = 0.7; DA.wob = 1; sgRing(sgLX(A), sgLZ(A), 0.9, 0xFFFFFF); sgBurst(sgLX(A), sgLZ(A), A.col, 8, 2.4, 2); } }
    else if (t >= 3.4) { sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'glee'; }
    if (t >= 4.3 && sgOnce('back')) sgBack(B, 0.95 * s, -0.2, sgYawTo(B, A));
  } else if (k === 'trap') {
    const tx = -0.12 * s, tz = 0.12;
    if (t < 0.3) { sgFace(A, sgYawCam(A), dt, 4); DA.ip.expr = 'ready'; }
    else if (t < 1.25) sgGo(A, tx, tz, 2.0, dt);
    else if (sgOnce('drop')) { SGD.trap.position.set(tx, 0, tz); SGD.trap.visible = true; SGD.trapT = 0; DA.squash = 0.4; emote(DA, 'glee', 0.6); sgRing(tx, tz, 0.9, TEAMS[0].wet); }
    if (t >= 1.35 && t < 2.6) { if (sgGo(A, 1.3 * s, 0.16, 1.9, dt)) sgFace(A, sgYawTo(A, B), dt, 5); }
    if (t >= 2.6) { sgHalt(A, dt); sgFace(A, B.show ? sgYawTo(A, B) : sgYawCam(A), dt, 4); sgWatch(A, B.show ? B : null); DA.ip.expr = B.show ? 'smirk' : 'glee'; }
    if (SGD.trap.visible) { SGD.trapT += dt; const u = SGD.trap.userData; u.light.material = (SGD.trapT < TRAP_ARM ? (SGD.trapT * 10) % 1 < 0.5 : (SGD.trapT * 1.4) % 1 < 0.2) ? trapLightOn : trapLightOff; u.ring.scale.setScalar(1 + 0.07 * Math.sin(SGD.trapT * 5)); SGD.trap.scale.setScalar(TRAP_SCALE * Math.min(1, easeBack(Math.min(1, SGD.trapT / 0.25)))); }
    if (t >= 2.4 && B.show && SGD.trap.visible) { sgGo(B, tx + 1.6 * s * 0.0, tz + 0.0, 1.5, dt); DB.ip.expr = 'curious';
      if (Math.hypot(sgLX(B) - tx, sgLZ(B) - tz) < TRAP_R * 0.45) { SGD.trap.visible = false; sgSplat(tx, tz, 0.75, cA); sgRing(tx, tz, 2.0, TEAMS[0].wet); sgRing(tx, tz, 1.1, 0xFFFFFF); sgBurst(tx, tz, A.col, 18, 4, 3.4); sgKO(B, cA); emote(DA, 'glee', 1.2); } }
    if (t >= 4.4 && sgOnce('back')) sgBack(B, -0.6 * s, -1.15, sgYawTo(B, A));
  } else if (k === 'whirl') {
    const W = SGD.whirl || (SGD.whirl = { ph: '', t: 0, spin: 0, k: 0, lx: 0, lz: 0 }), fin = 1.3 * s;
    if (t < 0.3) { sgFace(A, Math.atan2(s, 0), dt, 5); W.ph = ''; DA.ip.expr = 'ready'; }
    else if (sgOnce('wind')) { W.ph = 'wind'; W.t = 0; W.spin = 0; SGD.wpm.uniforms.uCol.value.copy(A.col); SGD.wg.visible = true; emote(DA, 'glee', 1); }
    if (W.ph) { W.t += dt; const fx = Math.sin(DA.yaw), fz = Math.cos(DA.yaw);
      if (W.ph === 'wind') { W.k = Math.min(1, W.t / 1.3); W.spin += dt * (8 + 24 * W.k); DA.ip.expr = 'focus'; sgFace(A, Math.atan2(s, 0), dt, 6); sgLane(A, Math.min(1, W.t / 1.3), W.t > 0.85);
        if (Math.random() < dt * 30) { const a = Math.random() * 6.283; sgPart(sgLX(A) + Math.cos(a) * 1.1, 0.5 + Math.sin(a) * 0.4, sgLZ(A) + Math.sin(a) * 1.1, -Math.cos(a) * 2.6, 0.3, -Math.sin(a) * 2.6, 0.3, COL_WHITE, 0.35); }
        if (W.t >= 1.3) { W.ph = 'dash'; W.t = 0; W.lx = sgLX(A); W.lz = sgLZ(A); } }
      else if (W.ph === 'dash') { W.spin += dt * 22; const lx0 = sgLX(A), lz0 = sgLZ(A); DA.spd = 3.3; DA.x += fx * 3.3 * dt; DA.z += fz * 3.3 * dt; sgStripe(lx0, lz0, sgLX(A), sgLZ(A), 1.45, cA); sgLane(A, 1, true, Math.max(0, 1 - W.t / 0.5));
        if (Math.random() < dt * 60) { const a = W.spin + Math.random() * 6.283; sgPart(sgLX(A) - fx * 0.5 + Math.cos(DA.yaw) * Math.cos(a) * 0.9, 0.42 + Math.max(-0.3, Math.sin(a) * 0.9), sgLZ(A) - fz * 0.5 - Math.sin(DA.yaw) * Math.cos(a) * 0.9, -fx * 2 + Math.cos(DA.yaw) * -Math.sin(a) * 3.4, 1 + Math.cos(a) * 3, -fz * 2 - Math.sin(DA.yaw) * -Math.sin(a) * 3.4, 0.45, A.col, 0.6); }
        if (B.show && Math.hypot(sgLX(B) - sgLX(A), sgLZ(B) - sgLZ(A)) < 0.85) { sgKO(B, cA); emote(DA, 'glee', 1.2); }
        if ((fin - sgLX(A)) * s <= 0 || W.t > 1.1) { W.ph = 'end'; W.t = 0; DA.spd = 0; sgSplat(sgLX(A), sgLZ(A), 0.85, cA); sgRing(sgLX(A), sgLZ(A), 1.9, TEAMS[0].wet); sgBurst(sgLX(A), sgLZ(A), A.col, 16, 3.6, 3); SGD.lane.visible = false; } }
      else if (W.ph === 'end') { W.spin += dt * 12; W.k = W.t / 0.4; if (W.t >= 0.4) { W.ph = ''; SGD.wg.visible = false; } }
      if (W.ph) { SGD.wg.position.set(sgLX(A), 0.55, sgLZ(A)); SGD.wg.rotation.set(0, DA.yaw, 0); SGD.wspin.rotation.z = W.spin; const sc = 1.15 * (W.ph === 'wind' ? 0.35 + 0.6 * W.k : W.ph === 'dash' ? 1 + 0.05 * Math.sin(W.t * 30) : 1 + 0.7 * W.k);
        SGD.wg.scale.set(sc * 0.85, sc * 0.85 * 0.8, (W.ph === 'wind' ? 0.45 + 0.4 * W.k : W.ph === 'end' ? 1 - 0.3 * W.k : 1) * 0.85); const al = W.ph === 'end' ? Math.max(0, 1 - W.k) : W.ph === 'wind' ? 0.4 + 0.6 * W.k : 1; SGD.wpm.uniforms.uA.value = al; SGD.wpm.uniforms.uT.value = W.spin; SGD.wsm.uniforms.uA.value = al * (W.ph === 'dash' ? 1 : 0.5); } }
    if (t >= 3.0) { sgHalt(A, dt); sgFace(A, sgYawCam(A), dt, 5); sgWatch(A, null); DA.ip.expr = 'glee'; }
    if (t >= 3.7 && sgOnce('back')) sgBack(B, -0.65 * s, 0.04, sgYawTo(B, A));
  } else {
    const BM = SGD.bm || (SGD.bm = { on: false, t: 0, x: 0, z: 0, px: 0, pz: 0 }), T0 = 0.8, TT = 1.6;
    if (t < T0) { sgFace(A, sgYawTo(A, B), dt, 5); sgWatch(A, B); DA.ip.expr = 'ready'; }
    else if (sgOnce('throw')) { BM.on = true; BM.t = 0; SGD.boom.visible = true; DA.squash = 0.4; DA.wob = 0.6; emote(DA, 'glee', 0.8); BM.px = sgLX(A); BM.pz = sgLZ(A); }
    if (BM.on) { BM.t += dt; const u = Math.min(1, BM.t / TT), ax = sgLX(A), az = sgLZ(A), dx = sgLX(B) - ax, dz = sgLZ(B) - az, dl = Math.max(0.5, Math.hypot(dx, dz)), fx = dx / dl, fz = dz / dl, L = dl + 0.5, Wd = 0.8 * s;
      const out = Math.sin(Math.PI * u), sw = smoothstep(0.32, 0.62, u) * out, x = ax + fx * (0.35 + L * out) - fz * Wd * sw, z = az + fz * (0.35 + L * out) + fx * Wd * sw; // (straight out through them, round on one side and home)
      sgStripe(BM.px, BM.pz, x, z, 0.55, cA); BM.px = x; BM.pz = z; SGD.boom.position.set(x, BOOM_H, z); SGD.bspin.rotation.y += dt * 24;
      if (Math.random() < dt * 24) sgPart(x, BOOM_H, z, (Math.random() - 0.5) * 2, 1 + Math.random(), (Math.random() - 0.5) * 2, 0.4, A.col, 0.35);
      if (B.show && Math.hypot(sgLX(B) - x, sgLZ(B) - z) < 0.55) { sgKO(B, cA); emote(DA, 'glee', 1.2); }
      sgFace(A, Math.atan2(x - ax, z - az), dt, 5); DA.ip.expr = 'focus';
      if (u >= 1) { BM.on = false; SGD.boom.visible = false; DA.squash = 0.3; DA.wob = 0.5; sgBurst(ax, az, A.col, 8, 1.6, 2.2); } }
    if (t >= T0 + TT + 0.1) { sgFace(A, sgYawCam(A), dt, 4); sgWatch(A, null); DA.ip.expr = 'glee'; }
    if (t >= 3.4 && sgOnce('back')) sgBack(B, 0.9 * s, -0.25, sgYawTo(B, A));
  }
  // (the last moment of each: the paint fades, then the other side)
  const T = SG_T[k] || 6; if (t > T - 0.7) sgPaintFade(Math.min(0.35, dt * 6)); if (t >= T) { sgPaintClear(); sgLoop(); }
  if (SGD.test) sgCap();
}
// the whirlwind's lane: a strip on the pad that fills as it winds, a little brighter once it locks
function sgLane(A, fill, lock, a) { const L = SGD.lane, x0 = sgLX(A), z0 = sgLZ(A), fx = Math.sin(A.D.yaw), fz = Math.cos(A.D.yaw), rx = Math.cos(A.D.yaw), rz = -Math.sin(A.D.yaw), hw = 0.68, len = 2.6, P0 = SGD.laneP;
  for (let i = 0; i <= 10; i++) { const d = len * i / 10, px = x0 + fx * d, pz = z0 + fz * d; P0[i * 6] = px - rx * hw; P0[i * 6 + 1] = 0.035; P0[i * 6 + 2] = pz - rz * hw; P0[i * 6 + 3] = px + rx * hw; P0[i * 6 + 4] = 0.035; P0[i * 6 + 5] = pz + rz * hw; }
  L.geometry.attributes.position.needsUpdate = true; const u = L.material.uniforms; u.uCol.value.copy(A.col); u.uFill.value = fill; u.uT.value = SGD.t; u.uLock.value = lock ? 0.6 : 0; u.uA.value = a === undefined ? Math.min(1, fill * 4) : a; u.uLen.value = len; L.visible = u.uA.value > 0.01; }
// the turret's shots: a lob from the barrel onto the rival (or, with them gone, on along its line)
function sgShoot(A, B) {
  let q = null; for (const s of SGD.shots) if (!s.on) { q = s; break; } if (!q) return;
  const D = A.D, k = PR, cy = Math.cos(D.yaw), sy = Math.sin(D.yaw), tp = TURRET_RIG.tip, x0 = sgLX(A) + (tp.x * cy + tp.z * sy) * k, y0 = (tp.y + 0.82 + 0.3) * k, z0 = sgLZ(A) + (-tp.x * sy + tp.z * cy) * k;
  const tx = B.show ? sgLX(B) : x0 + sy * 1.6, tz = B.show ? sgLZ(B) : z0 + cy * 1.6, ty = B.show ? PR * 0.7 : 0, d = Math.hypot(tx - x0, tz - z0), tf = Math.max(0.16, d / 6.5), g = 18;
  q.on = true; q.hit = B.show; q.x = x0; q.y = y0; q.z = z0; q.vx = (tx - x0) / tf; q.vz = (tz - z0) / tf; q.vy = (ty - y0 + 0.5 * g * tf * tf) / tf; q.t = 0;
  D.turret.kick = 1; D.squash = Math.max(D.squash, 0.2); sgPart(x0, y0, z0, sy * 2.4, 0.8, cy * 2.4, 0.22, A.col, 0.4);
}
function sgShots(dt) {
  const A = SGD.A, B = SGD.B, ca = SGD.sim.instanceColor.array; let n = 0;
  for (const s of SGD.shots) { if (!s.on) continue; s.t += dt; s.vy -= 18 * dt; s.x += s.vx * dt; s.y += s.vy * dt; s.z += s.vz * dt;
    if (s.hit && B.show && Math.hypot(sgLX(B) - s.x, sgLZ(B) - s.z) < PR + 0.2 && s.y < PR * 1.6) { s.on = false; sgHit(B, s); continue; }
    if (s.y <= 0.02) { s.on = false; sgSplat(s.x, s.z, 0.22, TEAMS[0].css); sgBurst(s.x, s.z, A.col, 4, 1.6, 1.4); continue; }
    sgT1.set(s.x, s.y, s.z); sgT2.set(s.vx, s.vy, s.vz).normalize(); sgQ.setFromUnitVectors(sgT3.set(0, 0, 1), sgT2); sgS.setScalar(SHOT_SC * (1 + 0.13 * Math.sin(SGD.t * 34 + s.ph))); sgM.compose(sgT1, sgQ, sgS); SGD.sim.setMatrixAt(n, sgM); SGD.sink.setMatrixAt(n, sgM);
    ca[n * 3] = A.col.r; ca[n * 3 + 1] = A.col.g; ca[n * 3 + 2] = A.col.b; n++; }
  SGD.sim.count = SGD.sink.count = n; SGD.sim.visible = SGD.sink.visible = n > 0; if (n) { SGD.sim.instanceMatrix.needsUpdate = SGD.sink.instanceMatrix.needsUpdate = true; SGD.sim.instanceColor.needsUpdate = true; }
}
// a hit: a jolt and a splash; three in a row and they see stars; each takes their paint, and one with none left is out
function sgHit(B, s) {
  const D = B.D, v = Math.hypot(s.vx, s.vz) || 1, nx = s.vx / v, nz = s.vz / v; sgSplat(sgLX(B), sgLZ(B), 0.2, TEAMS[0].css); sgBurst(sgLX(B), sgLZ(B), SGD.A.col, 5, 2, 1.6);
  if (D.paint <= 0.01) { sgKO(B, TEAMS[0].css); emote(SGD.A.D, 'glee', 1); return; }
  D.paint = Math.max(0, D.paint - 0.13); if (D.paint <= 0.01) { D.paint = 0; D.dry = true; }
  D.hits = (D.hits || 0) + 1; if (D.hits === 3) { D.stunT = 1.5; }
  D.squash = 0.85; D.wob = 1; fxKnock(D, nx, nz, 0.35); emote(D, 'ouch', 0.6); D.x += nx * 0.03; D.z += nz * 0.03; sgRing(sgLX(B), sgLZ(B), 0.7, TEAMS[0].wet);
}
// the captions Test shows, a line of the transform's own for each step
function sgCap() { const cap = $('sgCap'), o = stDef(SGD.id); if (!SGD.test || !o || !SG_CAP[SGD.kind]) { cap.classList.remove('on'); return; } let i = -1; for (let j = 0; j < SG_CAP[SGD.kind].length; j++) if (SGD.t >= SG_CAP[SGD.kind][j][0]) i = SG_CAP[SGD.kind][j][1]; if (i === SGD.capI) return; SGD.capI = i; if (i < 0) { cap.classList.remove('on'); return; } cap.textContent = o.does[i] || ''; cap.classList.add('on'); }
// ---- each frame: the characters drawn by the game's own code (as in a match), then the window drawn
function sgVis(dt) {
  const ke = 1 - Math.exp(-dt * 10), kf = 1 - Math.exp(-dt * 16), st0 = state, nl = window.__noLod; state = 'play'; window.__noLod = true;
  try {
    for (let i = 0; i < 2; i++) { const A = SGD.AB[i], L = A.L, D = A.D;
      L.drop.visible = A.show; if (!A.show) { L.stars.visible = false; A.sh.visible = false; continue; }
      if (D.squash > 0) D.squash = Math.max(0, D.squash - dt * 3); if (D.wob > 0) D.wob = Math.max(0, D.wob - dt * 1.6); if (D.emoT > 0) D.emoT -= dt;
      sgCol.copy(A.col); if (D.dry) sgCol.lerp(COL_DULL, 0.74); else if (D.paint < 1) sgCol.lerp(COL_DULL, (1 - D.paint) * 0.4); if (D.stunT > 0) sgCol.lerp(COL_WHITE, 0.12 + 0.1 * Math.sin(SGD.t * 30));
      L.mat.color.copy(sgCol); L.mat.emissive.copy(sgCol).multiplyScalar(0.22);
      blobVisual(D, A.V, dt, ke, kf); placeFaceCpu(L, dt); placeStars(L.stars, D, A.V);
      const sk = 0.95 + 0.25 * (A.V.turK || 0); A.sh.visible = true; A.sh.position.set(D.x - SG_X, 0.012, D.z - SG_Z); A.sh.scale.set(sk, 1, sk * 0.85); }
  } finally { state = st0; window.__noLod = nl; }
  sgShots(dt); sgFx(dt);
}
// (the pad framed in what the banner above it and the button below it leave clear of the window)
function sgCamFit() {
  const r = SGD.rect, C = SGD.cam, asp = r.w / Math.max(1, r.h), fh = Math.max(40, r.h - SGD.insT - SGD.insB); C.aspect = asp; C.fov = 30;
  if (SGD.yawTo !== null) { SGD.yaw += (SGD.yawTo - SGD.yaw) * 0.18; if (Math.abs(SGD.yawTo - SGD.yaw) < 0.002) { SGD.yaw = SGD.yawTo; SGD.yawTo = null; } }
  const vt = Math.tan(C.fov * Math.PI / 360), ht = vt * asp, el = 0.48, R = SG_R * 1.04, dist = Math.max(R / (0.94 * ht), (R * Math.sin(el) + 0.55) / (0.9 * vt * fh / r.h)), cy = Math.sin(el) * dist, cz = Math.cos(el) * dist;
  C.position.set(SG_X + Math.sin(SGD.yaw) * cz, cy + 0.2, SG_Z + Math.cos(SGD.yaw) * cz); C.up.set(0, 1, 0); C.lookAt(SG_X, 0.2, SG_Z);
  C.setViewOffset(r.w, r.h, 0, -(SGD.insT - SGD.insB) / 2, r.w, r.h); C.updateProjectionMatrix(); C.updateMatrixWorld();
}
function sgRectUpdate() {
  SGD.rectDirty = false; const el = $('sgStage'), r = el.getBoundingClientRect(), r0 = stage.getBoundingClientRect(), x = Math.round(r.left - r0.left), y = Math.round(r.top - r0.top), w = Math.round(r.width), h = Math.round(r.height);
  SGD.rect.x = x; SGD.rect.y = y; SGD.rect.w = w; SGD.rect.h = h;
  const bn = $('sgBan').getBoundingClientRect(), ft = $('mStrokes').querySelector('.sgfoot').getBoundingClientRect();
  SGD.insT = bn.height > 0 ? clamp(bn.bottom - r.top + 4, 0, h * 0.4) : 0; SGD.insB = ft.height > 0 ? clamp(r.bottom - ft.top + 2, 0, h * 0.4) : 0;
  const hole = w > 4 && h > 4 ? 'polygon(evenodd, 0 0, 100% 0, 100% 100%, 0 100%, 0 0, ' + x + 'px ' + y + 'px, ' + (x + w) + 'px ' + y + 'px, ' + (x + w) + 'px ' + (y + h) + 'px, ' + x + 'px ' + (y + h) + 'px, ' + x + 'px ' + y + 'px)' : '';
  if (hole !== SGD.hole) { SGD.hole = hole; $('sgBg').style.clipPath = hole; }
}
function sgRender() {
  const r = SGD.rect, H = stage.clientHeight, pr = renderer.getPixelRatio(), t0 = performance.now(); sgCamFit();
  const ac = renderer.autoClear, sha = renderer.shadowMap.autoUpdate, sct = renderer.getScissorTest(); renderer.getViewport(sgVp); renderer.getScissor(sgSc);
  const gk = RIG.uGrabK.value, gfn = JELLY_GRAB.fn, hi = hemi.intensity, si = sun.intensity, ri = vicRim.intensity; sgHemiC.copy(hemi.color); sgHemiG.copy(hemi.groundColor); sgSunC.copy(sun.color); sgSunP.copy(sun.position); sgSunT.copy(sun.target.position); sgRimP.copy(vicRim.position); sgRimT.copy(vicRim.target.position); sgRimC.copy(vicRim.color); sgRigC.copy(RIG.uRigRimC.value);
  let calls = 0;
  try {
    renderer.setRenderTarget(null); renderer.autoClear = false; renderer.shadowMap.autoUpdate = false; const y0 = H - r.y - r.h;
    renderer.setViewport(r.x - 1, y0 - 1, r.w + 2, r.h + 2); renderer.setScissor(r.x - 1, y0 - 1, r.w + 2, r.h + 2); renderer.setScissorTest(true);
    // (a quality step can drop the sun's shadow map, and the lobby that makes it again isn't drawn under the page. The lit shaders draw
    // nothing without one, so it's made here: empty, from the lobby's sun, with nothing of the demo in it)
    if (sun.castShadow && !sun.shadow.map) { renderer.shadowMap.needsUpdate = true; sun.shadow.needsUpdate = true; renderer.render(scene, SGD.cam); }
    SGD.bgU.uTile.value = 560 * pr; SGD.bgU.uH.value = H * pr; renderer.render(SGD.bgS, SGD.bgC); calls += renderer.info.render.calls;
    renderer.clearDepth(); renderer.setViewport(r.x, y0, r.w, r.h);
    // (the lobby's lights, turned for the pad: a warm key from the front, a cool rim from behind)
    const yw = SGD.yaw; hemi.intensity = 0.95 * LIGHT_K; hemi.color.setHex(0xFFFFFF); hemi.groundColor.setHex(0xC9DB86); sun.intensity = 1.25 * LIGHT_K; sun.color.setHex(0xFFF1E2);
    sun.position.set(SG_X + Math.sin(yw - 0.7) * 4, 6.5, SG_Z + Math.cos(yw - 0.7) * 4); sun.target.position.set(SG_X, 0.3, SG_Z); sun.target.updateMatrixWorld();
    vicRim.intensity = 0.7 * LIGHT_K; vicRim.color.setHex(0xE4ECFF); vicRim.position.set(SG_X - Math.sin(yw) * 4, 3, SG_Z - Math.cos(yw) * 4); vicRim.target.position.set(SG_X, 0.3, SG_Z); vicRim.target.updateMatrixWorld();
    RIG.uRigRimC.value.set(0xE8F0FF); RIG.uGrabK.value = 0; JELLY_GRAB.fn = null;
    sgDir.copy(sun.position).sub(sun.target.position).normalize().transformDirection(SGD.cam.matrixWorldInverse); for (let i = 0; i < 2; i++) { const I = SGD.AB[i].V.slime; if (I && I.ax && I.ax.look) I.ax.look.U.uKeyDir.value.copy(sgDir); }
    if (SGD.pdirty) { SGD.pdirty = false; SGD.ptex.needsUpdate = true; }
    SGD.root.visible = true; renderer.render(scene, SGD.cam); calls += renderer.info.render.calls;
  } finally {
    SGD.root.visible = false; SGD.A.L.drop.visible = SGD.B.L.drop.visible = false; SGD.A.L.stars.visible = SGD.B.L.stars.visible = false;
    hemi.intensity = hi; sun.intensity = si; vicRim.intensity = ri; hemi.color.copy(sgHemiC); hemi.groundColor.copy(sgHemiG); sun.color.copy(sgSunC); sun.position.copy(sgSunP); sun.target.position.copy(sgSunT); sun.target.updateMatrixWorld(); vicRim.position.copy(sgRimP); vicRim.target.position.copy(sgRimT); vicRim.target.updateMatrixWorld(); vicRim.color.copy(sgRimC); RIG.uRigRimC.value.copy(sgRigC); RIG.uGrabK.value = gk; JELLY_GRAB.fn = gfn;
    renderer.setScissorTest(sct); renderer.setViewport(sgVp); renderer.setScissor(sgSc); renderer.autoClear = ac; renderer.shadowMap.autoUpdate = sha;
  }
  SGD.calls = calls; SGD.cpu = performance.now() - t0; SGD.frames++;
}
// ---- when it runs: the Transforms tab up, nothing over the page, the app in view
const sgWant = () => strokesOpen() && stCat === 'item' && !!SGD.kind && $('stPop').hidden && !document.hidden && state === 'menu' && !building && !irisBusy && !lobbyCovered() && commModalEl.hidden && friendsModalEl.hidden && onModalEl.hidden && !vic;
function sgDemoPick(id) { const k = id && SG_T[id] ? id : ''; if (k === SGD.kind && id === SGD.id) return; SGD.kind = k; SGD.id = id; if (k && SGD.built) { sgPaintClear(); SGD.loop = 0; sgLoop(); } }
function sgTick(rdt) {
  if (!sgWant()) { if (SGD.on) sgPause(); return; }
  if (!SGD.built && !sgBuild()) return; if (!SGD.ready) return;
  if (!SGD.on) { SGD.on = true; sgHole(true); if (!SGD.started || SGD.startedK !== SGD.kind) { SGD.started = true; SGD.startedK = SGD.kind; sgPaintClear(); SGD.loop = 0; sgLoop(); } }
  if (SGD.rectDirty) sgRectUpdate(); if (SGD.rect.w < 8 || SGD.rect.h < 8) return;
  const dt = Math.min(0.05, Math.max(0, rdt));
  if (!reduceMotion || SGD.test) sgStep(dt);
  sgVis(dt); sgRender();
}
// the window in the page's wall: open while the demo draws, shut (the wall whole again) while it doesn't
function sgHole(on) { const pg = $('mStrokes'); pg.classList.toggle('sghole', on); pg.classList.toggle('sgdemo', on); $('sgRot').hidden = !on; if (on) SGD.rectDirty = true; else { SGD.hole = ''; $('sgBg').style.clipPath = ''; } }
function sgPause() { if (!SGD.on) return; SGD.on = false; sgHole(false); }
function sgStop() { sgPause(); SGD.started = false; if (SGD.built) { SGD.root.visible = false; SGD.A.L.drop.visible = SGD.B.L.drop.visible = false; } }
function sgTestStart() { if (stCat !== 'item' || !SGD.kind) return; SGD.test = true; $('mStrokes').classList.add('sgtest'); SGD.rectDirty = true; SGD.loop = 0; if (SGD.built) { sgPaintClear(); sgLoop(); } $('sgTest').setAttribute('aria-pressed', 'true'); }
function sgTestEnd(quiet) { if (!SGD.test) return; SGD.test = false; $('mStrokes').classList.remove('sgtest'); $('sgCap').classList.remove('on'); SGD.rectDirty = true; $('sgTest').setAttribute('aria-pressed', 'false'); if (!quiet) $('sgTest').focus({ preventScroll: true }); }
window.addEventListener('resize', () => { SGD.rectDirty = true; if (strokesOpen()) setTimeout(sgFitName, 60); });
if (window.ResizeObserver) try { new ResizeObserver(() => { SGD.rectDirty = true; }).observe($('sgStage')); } catch (e) {}
"""


def apply(s):
    # the markup: the page and the Info sheet (the v309 unlock code link, if it's in, moves to the foot of the panel)
    i = s.index('    <div class="mevents mstrokes" id="mStrokes" hidden>'); j = s.index('    <div class="mevents" id="mEvents" hidden>', i)
    old = s[i:j]; m = re.search(r'\n(\s*<div class="ucode stucode">.*?</form></div>)\n', old)
    ucode = ('          ' + m.group(1).strip() + '\n') if m else ''
    mk = MARKUP.replace('__BACK__', SV_BACK).replace('__ROT__', SV_ROT).replace('__GLASS__', GLASS).replace('__UCODE__', ucode)
    s = s[:i] + mk + s[j:]
    s = region(s, '  <div class="modal stpopm" id="stPop" hidden>', '  <div class="modal" id="commModal" hidden>', POP)
    # the style, last of all
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    # the page's code
    s = region(s, 'const ST_HAMMER = ', "// (v257) a stroke's card, over the page", JS_TILE)
    s = region(s, 'let stPopId = null, stPopT = 0;', 'function skillCard() {}', JS_POP)
    s = region(s, 'function renderStrokes() {', "$('stBack').addEventListener('click',", JS_RENDER)
    s = region(s, "$('stBack').addEventListener('click',", '\n\n// abilities: on the rail, locked until rank 3', JS_HANDLERS + JS_DEMO)
    # each frame on the page: the demo (the lobby isn't drawn under it)
    a = "lobbyCovered()))) renderFrame();"
    s = rep(s, a, a + " else if (state === 'menu' && menuPage === 'strokes') sgTick(rdt); // (v312: the transform demo)")
    # Ol' Bloop's lesson walks the new page: the Giant's tag, Craft, Skip, Equip (the page's own button and the bench's Skip)
    s = rep(s, "  const d = strokesOf(), giant = () => $('stSpecialRail').querySelector('.stopt[data-st=\"giant\"]');\n"
               "  if (stPopId && stPopId !== 'giant' && !(d.craft && d.craft.id === stPopId)) closeStPop(true); // (v257: the lesson walks the Giant's card)\n",
               "  const d = strokesOf(), giant = () => $('stSpecialRail').querySelector('.sgcard[data-st=\"giant\"]'), onG = sgSelId('special') === 'giant';\n"
               "  if (stPopId) closeStPop(true); if (SGD.test) sgTestEnd(true); if (!$('mStrokes').classList.contains('sglearn')) $('mStrokes').classList.add('sglearn'); // (v312: the lesson walks the page itself, laid out to leave him room)\n")
    s = rep(s, "function tutStrokesEnd() { tutSDone = 0;", "function tutStrokesEnd() { $('mStrokes').classList.remove('sglearn'); tutSDone = 0;")
    s = rep(s, "if (d.craft) return tutShow('Crafting takes 20 minutes. Tap Skip, this one’s on me', stPopId === d.craft.id ? 'stPopSkip' : 'stSkip', 'sSkip',",
               "if (d.craft) { if (d.craft.id === 'giant' && !onG) sgPick('giant', true); return tutShow('Crafting takes 20 minutes. Tap Skip, this one’s on me', d.craft.id === 'giant' ? 'sgSkip' : 'sgBadge', 'sSkip',")
    s = rep(s, "'sSkip', false, false, null, false, true);\n    if (stPopId === 'giant') return tutShow('Tap Craft to start on it', 'stPopCraftBtn', 'sCraft',",
               "'sSkip', false, false, null, false, true); }\n    if (onG) return tutShow('Tap Craft to start on it', 'sgDo', 'sCraft',")
    s = rep(s, "if (strokeSpecial() !== 'giant') { if (stPopId === 'giant') return tutShow('It’s ready! Tap Equip to make it your special stroke', 'stPopEquip', 'sEquip',",
               "if (strokeSpecial() !== 'giant') { if (onG) return tutShow('It’s ready! Tap Equip to make it your special stroke', 'sgDo', 'sEquip',")
    s = rep(s, "  if (stPopId) return; // (Equipped shows on the card for a beat, then it goes)\n", "")
    # (his tips keep below the page's header: the new back button counts when it's up top, as it is upright)
    s = rep(s, "for (const e of document.querySelectorAll('.evhead, .sback')) { if (e.offsetParent === null) continue; const r = e.getBoundingClientRect(); if (r.height > 0) b = Math.max(b, r.bottom - r0.top); }",
               "for (const e of document.querySelectorAll('.evhead, .sback, .sgback')) { if (e.offsetParent === null) continue; const r = e.getBoundingClientRect(); if (r.height > 0 && r.top - r0.top < r0.height / 2) b = Math.max(b, r.bottom - r0.top); }")
    s = rep(s, "'Giant it is! Grab the orb in a match and go big. Skills and transforms have their own tabs up top'",
               "'Giant it is! Grab the orb in a match and go big. Skills and transforms have their own tabs'")
    return s
