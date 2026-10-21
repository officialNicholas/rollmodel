"""v417: a polish pass on the menus (the user: "Get two other agents to look at different parts of the game and polish. Polish spacing,
continuity, corners, performance and radius. Micro animations. Everything that makes this game feel very premium"). This one is the
pages outside a match; the match and its results are the other pass's. Most pages already press, lift and slide in; what was missing
or off:
- Motion tokens on :root (--ease-out, --ease-pop, --d-fast/--d-med/--d-slow) so the new motion here shares one timing; reduced
  motion turns all of it off.
- Lobby: the Strokes plate said "Strokes" twice (its own label, and the tag under it repeating it). The tag now shows only when it
  says something (locked: the rank it opens at; New!).
- Friends: the sheet's title and rows sat 16 px in, the Locker's 22; now 22 upright, the same as the Locker's panel.
- Commissions: the three jobs come up one after another (a short rise, 60 ms apart) instead of all at once.
- Time trial leaderboard: the You / Friends / Global tabs press in; the rows come in one after another when the board changes.
- The party's Online | CPUs switch: the side you pick pops as it turns yellow, and both press in.
- Close buttons (the round X on the leaderboard, the dab store and the stroke card): a press that scales them in, like every other
  button.
- The dab store's Spin button presses down like its Buy buttons beside it; the commission cards press in a touch (scale .985)
  instead of not at all."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """/* (v417) menu polish: one set of motion tokens, the Strokes plate's tag only when it says something, the Friends sheet's inset,
   the commissions and leaderboard rows coming in one by one, press states where they were missing */
:root{--ease-out:cubic-bezier(.2,.8,.2,1);--ease-pop:cubic-bezier(.3,1.55,.5,1);--d-fast:.12s;--d-med:.24s;--d-slow:.38s}
#abilBtn:not(.locked):not(.fresh) .abtag{display:none}
@media (max-aspect-ratio:1/1){#friendsModal .frsheet{padding-left:max(22px,var(--gx));padding-right:max(22px,var(--gr))}}
@keyframes p17rise{from{opacity:0;transform:translateY(10px) scale(.98)}}
#commList>.comm{animation:p17rise var(--d-slow) var(--ease-out) both}
#commList>.comm:nth-child(2){animation-delay:.06s}
#commList>.comm:nth-child(3){animation-delay:.12s}
#commList>.comm:nth-child(4){animation-delay:.18s}
.ttrow{animation:p17rise var(--d-med) var(--ease-out) both}
.ttrow:nth-child(2){animation-delay:.04s}.ttrow:nth-child(3){animation-delay:.08s}.ttrow:nth-child(4){animation-delay:.12s}.ttrow:nth-child(5){animation-delay:.16s}.ttrow:nth-child(n+6){animation-delay:.2s}
.tttabs button:active{translate:0 2px;filter:brightness(.94)}
@keyframes p17pop{0%{transform:scale(.88)}60%{transform:scale(1.05)}100%{transform:scale(1)}}
.pywho button[aria-pressed="true"]{animation:p17pop var(--d-med) var(--ease-pop)}
.pywho button:active{transform:scale(.95)}
.ttx{transition:transform var(--d-fast) var(--ease-out),background-color var(--d-fast)}
.ttx:active{transform:scale(.88);background-color:rgba(23,19,32,.08)}
.comm{transition:transform var(--d-fast) var(--ease-out)}
.comm:active{transform:scale(.985)}
.dsgo:not(:disabled):active{transform:translateY(2px);box-shadow:0 1px 0 #171320}
@media (prefers-reduced-motion:reduce){#commList>.comm,.ttrow,.pywho button[aria-pressed="true"]{animation:none}.ttx,.comm{transition:none}}
"""

def apply(s):
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    return s
