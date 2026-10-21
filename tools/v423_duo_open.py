"""v423: iPhone Duo opened flat (about 951 x 669 points in landscape) and other tall landscape screens.

- Settings: on a landscape screen taller than 560 points the rows sat in the top third and the rest was empty. There the page now reads
  as three bands down the screen: sound and visuals, then turning and the help pages, each under a thin rule, with bigger toggles,
  buttons, slider and labels, and Restart Game with the version as a footer just above Done. Phones held sideways (520 points tall or
  less) keep their layout as it was.
- Settings has one way out, Back (top left). Done (bottom right) did the same thing, so it is gone on every layout (phone upright and
  sideways, iPhone Duo open and closed) and the rows get its room at the foot of the page. Back already did what Done did (a changed
  Visuals restarts the game); the focus Settings gave Done (opened from the pause menu, and after closing Delete account) goes to Back,
  and Restart Game's second-tap guard disarms on Back alone. Done used to read Restart to apply once Visuals changed; the note under
  Visuals now says the game restarts when you go back.
- Results beside the painting (a landscape screen taller than a phone's: iPhone Duo open, a tablet): the title is one line that never
  wraps, at up to 64 points, and the panel's single column was sized by its widest piece. VICTORY! (and NEW BEST! in a time trial) came
  out wider than the 361-point panel on iPhone Duo open, so the column grew past the panel, and everything in it (the score bar, the
  dabs on the reputation row, the big button) ran out past its right edge, where the panel cuts off what overflows. The column now
  stays the panel's width whatever is in it, and the title is sized to the panel (it shrinks only when it would not fit). The panel
  also keeps clear of a right-hand safe area. Phones held sideways get the same fixed column (their title is small, so nothing moves).
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v423) Settings on a tall landscape screen (iPhone Duo opened flat, a tablet): three bands down the page instead of a block at the
   top, sound and visuals, turning and the help pages, each under a thin rule, with bigger controls; Restart Game and the version as a
   footer above Done. A phone held sideways (520 points tall or less) never gets here */
/* (v423) no Done button: the rows run down to the foot of the page */
#setModal .card>#srows{bottom:max(8px,env(safe-area-inset-bottom))}
@media (min-aspect-ratio:1/1) and (min-height:561px){
  #setModal .card>#setTitle{font-size:44px;line-height:52px}
  #setModal .card>#srows{top:calc(max(12px,env(safe-area-inset-top)) + 76px);bottom:calc(max(12px,env(safe-area-inset-bottom)) + 14px);padding-left:max(32px,env(safe-area-inset-left));padding-right:max(32px,env(safe-area-inset-right))}
  #setModal #sfit{position:relative;min-height:100%;padding-bottom:58px;box-sizing:border-box;align-content:center;row-gap:clamp(32px,8vh,72px);column-gap:20px}
  #setModal .sopt{position:relative;gap:10px;padding-top:18px;border-top:1.5px solid rgba(255,255,255,.12)}
  #setModal .sopt::before{content:"";position:absolute;left:0;top:-2.5px;width:34px;height:3.5px;border-radius:2px;background:#F2C14E;transform:skewX(-14deg)}
  #setModal .slab{font-size:16px}
  #setModal .tog,#setModal .tog button{height:58px}
  #setModal .tog button{font-size:19px!important}
  #setModal .tog.pick button{font-size:16px!important}
  #setModal .sopt .gnote{font-size:12.5px}
  #setModal .trn{height:56px;gap:14px}
  #setModal .trnl{font-size:13px}
  #setModal .trnv{font-size:14px;padding:5px 10px 4px}
  #setModal .trndef{font-size:12.5px;padding:6px 11px 5px}
  #setModal .sdocs{align-self:stretch;display:grid;align-content:end}
  #setModal .sbtns.four{gap:12px}
  #setModal .sbtns.four .sbtn{min-height:64px;padding:4px 6px;font-size:13px;line-height:1.15}
  #setModal .sfoot{position:absolute;left:0;right:0;bottom:0;padding-top:14px;border-top:1.5px solid rgba(255,255,255,.12)}
  #setModal .sfoot .sreset{font-size:14px}
  #setModal .sfoot .sver{font-size:12px}
}
/* (v423) the results beside the painting: one column the panel's width, whatever is in it (VICTORY! at 64 points was wider than the
   panel on iPhone Duo open and pushed the score bar, the dabs and the big button out past the panel's right edge), the title sized to
   the panel, and clear of a right-hand safe area */
@media (min-aspect-ratio:1/1){#end{grid-template-columns:minmax(0,1fr)}#end>*{min-width:0}}
@media (min-aspect-ratio:1/1) and (min-height:521px){
  #end{container-type:inline-size}
  #end .rtitle{font-size:min(clamp(44px,13vw,64px),15cqi)}
}
@media (min-width:860px) and (min-aspect-ratio:1/1) and (min-height:521px){#end{right:max(clamp(24px,4vw,56px),calc(env(safe-area-inset-right,0px) + 16px))}}
"""

def no_done(s):
    s = rep(s, '      <button class="btn play sm" id="setDone" type="button">Done</button>\n', '')
    s = rep(s, "setPlayRows(true); if (window.__turnShow) window.__turnShow(); setModal.hidden = false; setFit();\n  setTimeout(() => $('setDone').focus({ preventScroll: true }), 30);",
               "setPlayRows(true); if (window.__turnShow) window.__turnShow(); setModal.hidden = false; setFit();\n  setTimeout(() => $('setBack').focus({ preventScroll: true }), 30); // (v423: Back, the one way out)")
    s = rep(s, "store.gfx = gfxPick; save(); $('setDone').disabled = true; $('setDone').textContent = 'Restarting';",
               "store.gfx = gfxPick; save(); $('setBack').disabled = true; $('setBack').setAttribute('aria-label', 'Restarting');")
    s = rep(s, "$('setDone').addEventListener('click', uiClick(doneSettings));", "")
    # (Done said "Restart to apply" once Visuals changed: the note under Visuals says it now)
    s = rep(s, "$('gfxNote').textContent = GFX_NOTE[gfxPick]; $('setDone').textContent = gfxPick === GFX ? 'Done' : 'Restart to apply';",
               "$('gfxNote').textContent = GFX_NOTE[gfxPick] + (gfxPick === GFX ? '' : ' The game restarts when you go back.');")
    s = rep(s, "  $('setDone').addEventListener('click', disarm); $('setBack').addEventListener('click', disarm); }\n",
               "  $('setBack').addEventListener('click', disarm); }\n")
    s = rep(s, "(b.hidden ? $('setDone') : b).focus({ preventScroll: true });", "(b.hidden ? $('setBack') : b).focus({ preventScroll: true });")
    assert "$('setDone')" not in s and 'id="setDone"' not in s
    return s

def apply(s):
    s = no_done(s)
    i = s.rfind("</style>"); s = s[:i] + CSS + s[i:]
    return s
