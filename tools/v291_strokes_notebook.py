"""v291: the Strokes page's two levels look like two different things, made by hand (on top of v287's paper look).

- The categories up top (Special, Skill, Transform) are cards of coloured construction paper, one colour each (gold, blue, red), each
  named by a strip of masking tape. The one open sits up straight and lifted with a paper arrow pointing down at its page; the other
  two sit back, darker.
- What's in the open category is a sheet of lined notebook paper (pale blue rules, a red margin line) taped down at its top corners.
  Its heading is written on it in ink with a swipe of highlighter in the category's colour. The strokes are stickers stuck on the page
  with their names written under them: the equipped one is ringed in marker; ones still to craft or locked are faded stickers;
  More soon is a pencilled box.
- A craft on the bench is a sticky note, taped at its top.
- New asset: art/m_cpaper_g.webp, a neutral construction-paper grain (made from art/m_cpaper.webp) that takes each card's colour."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

RING = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M80 19C63 5 24 7 12 33S22 92 52 90 98 64 89 36C85 22 71 12 49 11' "
        "fill='none' stroke='%23000' stroke-width='4.6' stroke-linecap='round'/%3E%3C/svg%3E\")")

CSS = r"""
/* (v291) two levels, two things: the categories are cards of coloured construction paper; what's in the open one is a taped sheet of
   lined notebook paper with the strokes stuck on it as stickers */
#mStrokes{--skp:#E3A12C;--skt:#2A1A04}
#mStrokes [data-cat="skill"]{--skp:#3A84D4;--skt:#FFF8EA}
#mStrokes [data-cat="item"]{--skp:#D33A4C;--skt:#FFF8EA}
#mStrokes .stslot{background:url(art/m_cpaper_g.webp) center/180px,var(--skp);background-blend-mode:multiply;border-radius:2px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08),4px 5px 0 rgba(0,0,0,.45);filter:brightness(.82) saturate(.9);scale:.95;transition:transform .16s ease,box-shadow .2s ease,rotate .2s ease,scale .2s ease,filter .2s ease}
#mStrokes .stslot .stic::before{display:none}
#mStrokes .stslot .stname{color:var(--skt);text-shadow:0 1px 0 rgba(0,0,0,.18)}
#mStrokes .stslot.on{filter:none;scale:1;rotate:0deg;translate:0 -3px;background:url(art/m_cpaper_g.webp) center/180px,var(--skp);background-blend-mode:multiply;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08),6px 8px 0 rgba(0,0,0,.5)}
#mStrokes .stslot:not(.on){filter:brightness(.82) saturate(.9)}
#mStrokes .stslot.on::after{bottom:-11px;width:18px;height:18px;margin-left:-9px;background:url(art/m_cpaper_g.webp) center/180px,var(--skp);background-blend-mode:multiply;box-shadow:3px 3px 0 0 rgba(0,0,0,.35)}
#mStrokes .stslot.fresh::before{box-shadow:0 0 0 2px var(--skp)}
/* the open category: a sheet of lined notebook paper, taped at its top corners */
#mStrokes .stpanel{position:relative;gap:6px;padding:24px 12px 16px 30px;border-radius:2px;color:var(--black);
  background:linear-gradient(90deg,transparent 21px,rgba(226,72,88,.6) 21px,rgba(226,72,88,.6) 23px,transparent 23px),
    repeating-linear-gradient(180deg,transparent 0 27px,rgba(84,140,205,.3) 27px 28px),#FCFAF2;
  background-position:0 0,0 6px,0 0;box-shadow:inset 0 0 0 1px rgba(23,19,32,.06),4px 6px 0 rgba(0,0,0,.42);rotate:-.4deg}
#mStrokes .stpanel::before,#mStrokes .stpanel::after{content:"";position:absolute;top:-10px;width:70px;height:22px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;pointer-events:none;filter:drop-shadow(0 1px 0 rgba(23,19,32,.12))}
#mStrokes .stpanel::before{left:-18px;transform:rotate(-32deg)}
#mStrokes .stpanel::after{right:-18px;transform:rotate(30deg)}
#mStrokes .stphd{flex-direction:column;align-items:flex-start;justify-content:flex-start;gap:5px;padding:0 2px 6px}
#mStrokes .stphd h3{position:relative;isolation:isolate;padding:0 2px;background:none;color:var(--black);font:400 19px/1 var(--font-display);letter-spacing:.01em;text-transform:uppercase;transform:rotate(-1deg)}
#mStrokes .stphd h3::after{content:"";position:absolute;left:-7px;right:-9px;bottom:-3px;height:13px;z-index:-1;background:var(--sk);opacity:.6;-webkit-mask:url(art/m_stroke2.webp) center/100% 100% no-repeat;mask:url(art/m_stroke2.webp) center/100% 100% no-repeat}
#mStrokes .stphd small{color:#6E6680;font-style:italic;text-align:left}
#mStrokes .stphd h3{white-space:nowrap}
/* the strokes: stickers on the page, their names written under them */
#mStrokes .strail{gap:6px 8px}
#mStrokes .stopt,#mStrokes .stopt.on,#mStrokes .stopt.raw,#mStrokes .stopt.lock,#mStrokes .stopt.crafting{padding:8px 4px 6px;border:0;border-radius:10px;background:none;box-shadow:none}
#mStrokes .stopt.on::before{display:none}
#mStrokes .stopt:active{transform:scale(.95)}
#mStrokes .stopt .stoi{width:72px;height:72px}
#mStrokes .stopt .stoi .stimg{width:62px;height:62px;filter:drop-shadow(1px 2px 1px rgba(23,19,32,.28))}
#mStrokes .stopt .stoi::before{opacity:.32}
#mStrokes .stopt.on .stoi::after{content:"";position:absolute;inset:-7px -9px -6px -7px;background:var(--sk-deep);-webkit-mask:__RING__ center/100% 100% no-repeat;mask:__RING__ center/100% 100% no-repeat;transform:rotate(-8deg);pointer-events:none}
#mStrokes .stopt .stn{color:var(--black);min-height:2.04em}
#mStrokes .stopt .stost{height:16px;padding:0;background:none;box-shadow:none;color:#6E6680}
#mStrokes .stopt .stost.on{color:var(--sk-deep);background:none;box-shadow:none}
#mStrokes .stopt .stost.raw{color:var(--black)}
#mStrokes .stopt .stost.new{padding:0 7px;background:#E8364F;color:#fff;border-radius:999px}
#mStrokes .stopt.raw .stoi .stimg,#mStrokes .stopt.lock .stoi .stimg{opacity:.6;filter:grayscale(.7) drop-shadow(1px 2px 1px rgba(23,19,32,.2))}
#mStrokes .stopt.raw .stoi::before,#mStrokes .stopt.lock .stoi::before{opacity:.12}
#mStrokes .stopt.raw .stn,#mStrokes .stopt.lock .stn{color:#6E6680}
#mStrokes .stopt .stcb{background:rgba(23,19,32,.12)}
#mStrokes .stopt.soon{border:2px dashed rgba(23,19,32,.22);border-radius:10px;background:none}
#mStrokes .stopt.soon .stimg{opacity:.3}
#mStrokes .stopt.soon .stn{color:rgba(23,19,32,.35)}
#mStrokes .stopt:focus-visible{outline:3px solid var(--sk-deep);outline-offset:2px}
/* the bench: a sticky note, taped at its top */
#mStrokes .stcraft{border-radius:0;background:linear-gradient(180deg,#FFE896 0%,#FFE07A 70%,#F6D466 100%);box-shadow:0 12px 12px -9px rgba(0,0,0,.55);rotate:.8deg}
#mStrokes .stcraft::before{left:50%;top:-9px;width:64px;height:19px;margin-left:-32px;transform:rotate(-3deg)}
@media (min-aspect-ratio:1/1) and (max-height:600px){#mStrokes .stpanel{padding:20px 10px 12px 28px}#mStrokes .stopt .stoi{width:60px;height:60px}#mStrokes .stopt .stoi .stimg{width:52px;height:52px}#mStrokes .stslot{scale:.97}#mStrokes .stslot.on{scale:1}}
@media (prefers-reduced-motion:reduce){#mStrokes .stslot,#mStrokes .stopt{transition:none}}
""".replace('__RING__', RING)

def apply(s):
    a = "#mStrokes .stslot.fresh::before{box-shadow:0 0 0 2px #FBF8F1}"  # (v287's last block is in; this goes after the whole v287 CSS)
    assert s.count(a) == 1
    b = "@media (prefers-reduced-motion:reduce){#mStrokes .stslot{transition:none}}"
    assert s.count(b) == 1, s.count(b)
    s = s.replace(b, b + CSS.rstrip('\n'))
    return s
