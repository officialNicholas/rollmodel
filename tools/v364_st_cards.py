"""v364: the Strokes page's cards show their pictures on an iPhone, and the taped bar over them is gone.

- A stroke you haven't crafted yet (the Giant and Flash Freeze while the Rocket is yours, say) shows its picture greyed and faded. The
  grey and the fade were a filter on the picture's frame, round a picture with a filter of its own (its drop shadow), and an iPhone drew
  none of it: the card came up blank. The grey and the fade now go on the picture itself (and on the splat behind a picked card), so
  nothing is filtered twice. The same for the locked cards in the Paint Shop ("Find it"), and the "More soon" card. They look as before.
- The dark taped bar at the top of the Strokes page's sheet (the rail the cards seemed to hang from) is gone."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # ---- the taped bar over the cards
    s = rep(s, '<section class="sgpanel" id="stPanel" aria-labelledby="stCatH"><i class="sghang" aria-hidden="true"></i>',
               '<section class="sgpanel" id="stPanel" aria-labelledby="stCatH">')
    s = rep(s, "#mStrokes.sgp .sghang{position:absolute;left:50%;top:-8px;z-index:2;width:40%;max-width:190px;height:17px;border-radius:999px;background:linear-gradient(#3A3A42,#232328);box-shadow:inset 0 1.5px 0 rgba(255,255,255,.16),0 0 0 2px var(--ink0),0 3px 0 rgba(0,0,0,.35);transform:translateX(-50%)}\n"
               "#mStrokes.sgp .sghang::after{content:\"\";position:absolute;left:58%;top:-9px;width:62px;height:21px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:rotate(-7deg);filter:drop-shadow(0 1px 0 rgba(23,19,32,.2))}\n", "")
    # ---- greyed pictures: on the picture, not its frame (the splat behind a picked card takes the grey its filter gave it)
    s = rep(s, ":is(#mStrokes,#mLocker).sgp .sgcard.lock .sgca,:is(#mStrokes,#mLocker).sgp .sgcard.raw .sgca{filter:grayscale(.85) opacity(.6)}",
               ":is(#mStrokes,#mLocker).sgp .sgcard:is(.lock,.raw) .sgca>*{opacity:.6}:is(#mStrokes,#mLocker).sgp .sgcard:is(.lock,.raw) .sgca .stimg{filter:grayscale(.85) drop-shadow(1px 2px 0 rgba(23,19,32,.22))}"
               ":is(#mStrokes,#mLocker).sgp .sgcard:is(.lock,.raw) .sgca svg{filter:grayscale(.85)}:is(#mStrokes,#mLocker).sgp .sgcard:is(.lock,.raw) .sgca::before{background:#725764;opacity:.6} /* (v364: a filter on the frame round a picture with its own drew nothing on an iPhone) */")
    s = rep(s, ":is(#mStrokes,#mLocker).sgp .sgcard.soon .sgca{opacity:.35;filter:grayscale(1)}",
               ":is(#mStrokes,#mLocker).sgp .sgcard.soon .sgca>*{opacity:.35}:is(#mStrokes,#mLocker).sgp .sgcard.soon .sgca .stimg{filter:grayscale(1) drop-shadow(1px 2px 0 rgba(23,19,32,.22))}:is(#mStrokes,#mLocker).sgp .sgcard.soon .sgca svg{filter:grayscale(1)}")
    s = rep(s, "#mLocker.sgp .sgcard.lock .sgca{filter:grayscale(.9) opacity(.55)}",
               "#mLocker.sgp .sgcard.lock .sgca>*{opacity:.55}#mLocker.sgp .sgcard.lock .sgca .stimg{filter:grayscale(.9) drop-shadow(1px 2px 0 rgba(23,19,32,.22))}#mLocker.sgp .sgcard.lock .sgca svg{filter:grayscale(.9)}#mLocker.sgp .sgcard.lock .sgca::before{background:#6B5962;opacity:.55}")
    return s
