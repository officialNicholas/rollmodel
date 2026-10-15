"""v287: the Strokes page in the studio's own look, like the lobby, Commissions and the rest. It had its own dark glossy panels.

- The three loadout slots are cards of the studio's graph paper, a touch crooked, each held down by a strip of masking tape that
  names it (Special, Skill, Transform). The one you're looking at sits straight, outlined in ink.
- The collection's heading is a tape label. Each stroke is a paper tile outlined in ink with a hard shadow, like the Commissions rows;
  its picture sits on a dab of its slot's colour (gold specials, blue skills, red transforms). The equipped one is taped down and
  washed in its colour; ones still to craft or locked are greyed paper; More soon is a dashed outline.
- The bench is a paper strip, its bar filling in the slot's colour; Skip is a tape button.
- A stroke's card is a sheet of the graph paper with tape across its top edge, ink type, what it does in an outlined white box, and
  the stroke button (your paint, with its drip) for Craft and Equip. Equipped, it's the slot's colour."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v287) the Strokes page in the studio's look: graph paper held down with masking tape, ink type, the slot's colour as a dab of paint
   behind each picture, and the stroke button (your paint) for Craft and Equip */
#mStrokes .stslot{padding:18px 6px 11px;border-radius:3px;background:#FBF8F1 url(art/m_paperbg.webp) center/300px;color:var(--black);box-shadow:0 1px 0 rgba(255,255,255,.7) inset,4px 5px 0 rgba(0,0,0,.42);rotate:-1.4deg;transition:transform .16s ease,box-shadow .2s ease,rotate .2s ease}
#mStrokes .stslot:nth-child(2){rotate:1.1deg}#mStrokes .stslot:nth-child(3){rotate:-.7deg}
#mStrokes .stslot .stk{position:absolute;left:50%;top:-9px;align-self:auto;width:max-content;padding:5px 12px 6px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;color:#2A2437;font:900 10px/1 var(--font-head);letter-spacing:.12em;transform:translateX(-50%) rotate(-3deg)}
#mStrokes .stslot:nth-child(2) .stk{transform:translateX(-50%) rotate(2deg)}
#mStrokes .stslot .stk::before{background:var(--sk-deep)}
#mStrokes .stslot .stic,#mStrokes .stopt .stoi{background:none;isolation:isolate}
#mStrokes .stslot .stic::before,#mStrokes .stopt .stoi::before{content:"";position:absolute;inset:2px;z-index:-1;background:var(--sk);-webkit-mask:url(art/m_splat.webp) center/contain no-repeat;mask:url(art/m_splat.webp) center/contain no-repeat;opacity:.5}
#mStrokes .stopt .stoi{position:relative}
#mStrokes .stslot .stic .stimg,#mStrokes .stopt .stoi .stimg{position:relative;filter:drop-shadow(1px 2px 0 rgba(23,19,32,.22))}
#mStrokes .stslot .stname,#mStrokes .stopt .stn{font:900 14px/1.02 var(--font-head);font-style:normal;letter-spacing:.01em;color:var(--black)}
#mStrokes .stslot.on{rotate:0deg;background:#fff url(art/m_paperbg.webp) center/300px;box-shadow:0 0 0 3px var(--black),5px 6px 0 rgba(0,0,0,.5)}
#mStrokes .stslot.on::after{bottom:-10px;background:#fff;box-shadow:3px 3px 0 0 var(--black)}
#mStrokes .stslot.fresh::before{box-shadow:0 0 0 2px #FBF8F1}
#mStrokes .stslot:focus-visible,#mStrokes .stopt:focus-visible{outline:3px solid #FFF1C4;outline-offset:4px}
/* the heading: a tape label */
#mStrokes .stphd{align-items:center}
#mStrokes .stphd h3{padding:7px 15px 8px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;color:#2A2437;font:900 14px/1 var(--font-head);font-style:normal;letter-spacing:.06em;transform:rotate(-2deg)}
#mStrokes .stphd small{color:rgba(244,238,227,.72)}
/* the tiles: paper, outlined in ink, a hard shadow */
#mStrokes .stopt{padding:12px 6px 10px;border:2.5px solid var(--black);border-radius:8px;background:#fff url(art/m_paperbg.webp) center/300px;color:var(--black);box-shadow:3px 4px 0 rgba(0,0,0,.45)}
#mStrokes .stopt .stost{color:var(--muted)}
#mStrokes .stopt .stost.on{background:var(--sk);color:var(--black);box-shadow:0 0 0 2px var(--black)}
#mStrokes .stopt .stost.raw{color:var(--black)}
#mStrokes .stopt .stost.raw svg{color:var(--sk-deep)}
#mStrokes .stopt .stost.new{background:#E8364F;color:#fff}
#mStrokes .stopt .stost.lk{color:var(--muted)}
#mStrokes .stopt .stost.cr{color:var(--black)}
#mStrokes .stopt .stcb{background:rgba(23,19,32,.12)}
#mStrokes .stopt.on{background:linear-gradient(rgba(var(--skrgb),.2),rgba(var(--skrgb),.2)),#fff url(art/m_paperbg.webp) center/300px;box-shadow:3px 4px 0 rgba(0,0,0,.45)}
#mStrokes .stopt.on::before{content:"";position:absolute;left:50%;top:-9px;width:58px;height:17px;margin-left:-29px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:rotate(-4deg);pointer-events:none}
#mStrokes .stopt.raw,#mStrokes .stopt.lock{background:#EDE7DC url(art/m_paperbg.webp) center/300px}
#mStrokes .stopt.raw .stoi .stimg,#mStrokes .stopt.lock .stoi .stimg{opacity:.9;filter:grayscale(.8) drop-shadow(1px 2px 0 rgba(23,19,32,.18))}
#mStrokes .stopt.raw .stoi::before,#mStrokes .stopt.lock .stoi::before{opacity:.22}
#mStrokes .stopt.raw .stn,#mStrokes .stopt.lock .stn{color:#5A5266}
#mStrokes .stopt.crafting{border-color:var(--sk-deep);box-shadow:3px 4px 0 rgba(0,0,0,.45)}
#mStrokes .stopt.ready::after{box-shadow:0 0 0 2px #fff}
#mStrokes .stopt.soon{border:2.5px dashed rgba(244,238,227,.28);background:transparent;box-shadow:none}
#mStrokes .stopt.soon .stoi::before{display:none}
#mStrokes .stopt.soon .stn{color:rgba(244,238,227,.4)}
/* the bench: a paper strip, taped at its corner */
#mStrokes .stcraft{border-radius:3px;background:#FBF8F1 url(art/m_paperbg.webp) center/300px;color:var(--black);box-shadow:4px 5px 0 rgba(0,0,0,.42)}
#mStrokes .stcraft::before{content:"";position:absolute;left:-10px;top:-8px;width:52px;height:17px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:rotate(-16deg);pointer-events:none}
#mStrokes .stcraft .stct{font:900 15px/1.05 var(--font-head);font-style:normal;color:var(--black)}
#mStrokes .stcraft .stct small{color:var(--sk-deep)}
#mStrokes .stctime{font:900 22px/1 var(--font-head);font-style:normal;color:var(--black)}
#mStrokes .stcraft .stbar,#stPop .stptimer .stbar{background:rgba(23,19,32,.12);box-shadow:inset 0 0 0 1.5px rgba(23,19,32,.18)}
#mStrokes .stcraft .stbar i,#stPop .stptimer .stbar i{background:var(--sk);box-shadow:none}
/* Skip: a tape button */
#mStrokes .stskip,#stPop .stskip{padding:9px 16px 10px;border-radius:0;background:url(art/m_tape3.webp) center/100% 100% no-repeat;color:#2A2437;font:900 13px/1 var(--font-head);font-style:normal;letter-spacing:.06em;box-shadow:none;rotate:2deg}
#mStrokes .stskip:active,#stPop .stskip:active{transform:translateY(2px);box-shadow:none}
/* the card: a sheet of the graph paper with tape across its top edge */
#stPop .stpop{border-radius:4px 4px 0 0;background:#F6F1E8 url(art/m_paperbg.webp) center/420px;color:var(--black);box-shadow:0 -10px 40px rgba(0,0,0,.45)}
#stPop .stpop::before{top:-3px;width:112px;height:28px;margin-left:-56px;border-radius:0;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:rotate(-2deg)}
#stPop .stphead{padding-top:22px}
#stPop .stphead b{color:var(--sk-deep)}
#stPop .stpown{background:rgba(23,19,32,.08);color:var(--black)}
#stPop .stpown svg{color:#1E8A45}
#stPop .stpx{background:var(--black);color:var(--cream);box-shadow:2px 2px 0 rgba(23,19,32,.22)}
#stPop .stpart{position:relative;background:none;isolation:isolate}
#stPop .stpart::before{content:"";position:absolute;inset:4px;z-index:-1;background:var(--sk);-webkit-mask:url(art/m_splat.webp) center/contain no-repeat;mask:url(art/m_splat.webp) center/contain no-repeat;opacity:.55}
#stPop .stpart .stimg{filter:drop-shadow(2px 3px 0 rgba(23,19,32,.22))}
#stPop .stpname{font:900 32px/.95 var(--font-head);font-style:normal;letter-spacing:.01em;text-transform:uppercase;color:var(--black)}
#stPop .stpdesc{color:#4A4358}
#stPop .stpdoes{padding:2px 12px;border:2px solid var(--black);border-radius:6px;background:#fff;box-shadow:3px 3px 0 var(--black)}
#stPop .stpdoes li{color:var(--black);border-top:1px solid rgba(23,19,32,.12)}
#stPop .stpdoes li::before{background:var(--sk);box-shadow:0 0 0 2px var(--black)}
#stPop .stpdoes li::after{display:none}
#stPop .stptimer{border:2px solid var(--black);border-radius:6px;background:#fff;box-shadow:3px 3px 0 var(--black)}
#stPop .stptimer .stpt{color:var(--sk-deep)}
#stPop .stptimer .stpt b{font:900 26px/1 var(--font-head);font-style:normal;color:var(--black)}
#stPop .stpnote{color:var(--muted)}
/* Craft and Equip: the stroke button, in your paint */
#stPop .stpbtns{margin:6px 0 14px}
#stPop .stpb.stroke{min-height:60px;padding:10px 26px 14px;border-radius:0;background:none;box-shadow:none;font:900 20px/1 var(--font-head);font-style:normal;letter-spacing:.03em;color:#fff}
#stPop .stpb.stroke:active:not(:disabled){transform:translateY(3px) scale(.985);box-shadow:none}
#stPop .stpb.stroke small{padding:4px 8px 3px;border-radius:999px;background:rgba(0,0,0,.24);color:#fff;text-shadow:none}
#stPop .stpb.stroke:disabled{color:#7D7489;text-shadow:none;cursor:default}
#stPop .stpb.stroke:disabled::before{background:#D9D0C0}
#stPop .stpb.stroke.on:disabled{color:var(--black)}
#stPop .stpb.stroke.on:disabled::before{background:var(--sk)}
#stPop .stpb.stroke.on:disabled svg{color:var(--black)}
@media (min-aspect-ratio:1/1) and (max-height:600px){#stPop .stpop{border-radius:4px}#stPop .stpop::before{display:block}#stPop .stpbtns{margin-bottom:12px}#stPop .stpb.stroke{min-height:50px;font-size:18px}}
@media (prefers-reduced-motion:reduce){#mStrokes .stslot{transition:none}}
"""

def apply(s):
    a = "@media (prefers-reduced-motion:reduce){#mStrokes .stslot,#mStrokes .strail.in .stopt,#stPop .stpop,#mStrokes .stslot.fresh::before{animation:none}}"
    s = rep(s, a, a + CSS.rstrip('\n'))
    s = rep(s, '<button class="stpb craft" id="stPopCraftBtn" type="button">Craft</button><button class="stpb equip" id="stPopEquip" type="button">Equip</button>',
               '<button class="stpb craft stroke" id="stPopCraftBtn" type="button">Craft</button><button class="stpb equip stroke" id="stPopEquip" type="button">Equip</button>')
    return s
