"""v418: one Back button everywhere (the user, of the purple round one on Strokes, the Locker and Friends: "I like this back
button, let's make that the default"). Choose Event, Settings and the Canvases page had their own (a dark square chevron, a dark
round chevron): they're the purple round button now, with the curled arrow and "Back" under it, the same size and press as the others.
They keep their places on their pages."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

INNER = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M12.6 7.4 6.2 13.6l6.4 6.2" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M7.4 13.6h11.2a6.4 6.4 0 0 1 0 12.8h-4.4" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/></svg><span>Back</span>'

CSS = """/* (v418) the purple round Back (as on Strokes, the Locker and Friends) on every page */
:is(#evBack,#setBack,#worldBack).pback{appearance:none;display:flex;flex-direction:column;align-items:center;justify-content:center;width:var(--pbk,56px);height:var(--pbk,56px);margin:0;padding:2px 0 0;border:0;border-radius:50%;background:radial-gradient(circle at 38% 28%,#A876FF,#7B3BEA 58%,#5F22C8);color:#fff;box-shadow:0 0 0 3px #171320,0 5px 0 #171320;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:transform .08s,box-shadow .08s}
:is(#evBack,#setBack,#worldBack).pback svg{width:46%;height:46%;flex:none}
:is(#evBack,#setBack,#worldBack).pback span{margin-top:-1px;font:400 11px/1 var(--font-display);letter-spacing:.01em}
:is(#evBack,#setBack,#worldBack).pback:active{transform:translateY(3px);box-shadow:0 0 0 3px #171320,0 2px 0 #171320}
:is(#evBack,#setBack,#worldBack).pback:focus-visible{outline:3px solid #fff;outline-offset:3px}
@media (max-height:520px) and (min-aspect-ratio:1/1){:is(#evBack,#setBack,#worldBack).pback{--pbk:48px}:is(#evBack,#setBack,#worldBack).pback span{font-size:10px}}
@media (max-aspect-ratio:1/1) and (max-height:700px){:is(#evBack,#setBack,#worldBack).pback{--pbk:50px}}
"""

def apply(s):
    s = rep(s, '<button class="sback" id="evBack" type="button" aria-label="Back to the lobby"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4.5 7.5 12l7.5 7.5" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>',
               '<button class="sback pback" id="evBack" type="button" aria-label="Back to the lobby">' + INNER + '</button>')
    s = rep(s, '<button class="sback" id="setBack" type="button" aria-label="Back"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4.5 7.5 12l7.5 7.5" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>',
               '<button class="sback pback" id="setBack" type="button" aria-label="Back">' + INNER + '</button>')
    s = rep(s, '<button class="ibtn back" id="worldBack" type="button" aria-label="Back to the title screen"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 5.5 8 12l6.5 6.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></button>',
               '<button class="ibtn back pback" id="worldBack" type="button" aria-label="Back to the title screen">' + INNER + '</button>')
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    return s
