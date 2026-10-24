"""v447: Ol' Bloop's second button (Just play, Later) is a real button, not small underlined text; How to play leaves Settings;
Paint the Stage says "your rivals".

- The user: "the just play button is too small. Teach me is fine to be larger, but I can barely see just play". It's an outlined
  pill now, under the paint button: smaller than Teach me, so Teach me still leads, but big enough to read and to hit.
- Settings' help row loses How to play (the user: "remove the how to play button from settings"): Replay tutorial, Terms and Privacy,
  or just Terms and Privacy during a match. The page itself stays in the game, nothing links to it from here.
- The Paint the Stage card: "Cover more floor than your rivals" (the user: "then your rivals" rather than cpu)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """
/* (v447) the card's second choice (Just play, Later): an outlined pill, quieter than the paint button but easy to see and tap */
.tutgo .tgcard #tgLater{width:min(100%,220px);min-height:48px;padding:12px 20px;margin-top:2px;border:2px solid rgba(255,255,255,.72);border-radius:14px;background:rgba(255,255,255,.1);color:#fff;font:800 18px/1 var(--font-ui);letter-spacing:.02em;text-decoration:none;touch-action:manipulation;transition:transform .12s,background-color .12s}
.tutgo .tgcard #tgLater:active{transform:scale(.96);background:rgba(255,255,255,.2)}
.tutgo .tgcard #tgLater:focus-visible{outline:3px solid #ffd76a;outline-offset:2px}
@media (max-height:520px) and (min-aspect-ratio:1/1){.tutgo .tgcard #tgLater{min-height:40px;padding:9px 18px;margin-top:0;font-size:16px}}
/* (v447) Settings' help row without How to play: Replay tutorial, Terms, Privacy (two in a match) */
#setModal .sbtns.four{grid-template-columns:repeat(3,minmax(0,1fr))}
#setModal .sbtns.four:has(#tutAgain[hidden]){grid-template-columns:repeat(2,minmax(0,1fr))}
"""

def apply(s):
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    s = rep(s, '<button class="sbtn" id="howOpen" type="button"', '<button class="sbtn" id="howOpen" type="button" hidden')
    s = rep(s, '<small>Cover more floor than the CPUs</small>', '<small>Cover more floor than your rivals</small>')
    return s
