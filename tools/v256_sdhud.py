"""v256: the Showdown's top bar gives the fight more room. No paper card and no tape: just each fighter's face in its ring with
its hearts tucked under it, your side on the left, the others on the right, and the time between them (no VS). The names go
from the bar (each fighter's tag over its head still says who it is)."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
CSS = r"""/* (v256) the Showdown's top bar: the faces and their hearts straight over the canvas, the time in the middle (sized by the screen's width
   so four faces and the time fit between the pause and sound buttons on a 320-wide phone) */
.hud.sdmode{--sdb:clamp(25px,8.2vw,34px)}
.hud.sdmode .score{display:grid;width:auto;max-width:100%;padding:0;gap:5px;background:none;border:0;border-radius:0;box-shadow:none;transform:none}
.hud.sdmode .score::before,.hud.sdmode .score::after{content:none;display:none}
.hud.sdmode .score>.vsrow,.hud.sdmode .score>.sdbar{grid-area:1/1}
.hud.sdmode .score>.zchip{grid-row:2}
.hud.sdmode .score>.vsrow{z-index:1;justify-self:center;align-self:start;height:var(--sdb);pointer-events:none}
.hud.sdmode .clock{min-width:0;padding:0 2px;border-radius:0;background:none;transform:none;font:900 clamp(17px,5.6vw,22px)/1 var(--font-head);font-style:italic;font-variant-numeric:tabular-nums;letter-spacing:.01em;color:#fff;text-shadow:0 2px 0 #171320,2px 0 0 #171320,-2px 0 0 #171320,0 -2px 0 #171320,1.5px 1.5px 0 #171320,-1.5px 1.5px 0 #171320,1.5px -1.5px 0 #171320,-1.5px -1.5px 0 #171320,0 3.5px 0 #171320}
.hud.sdmode .clock.hurry{background:none;color:#FF4D6A}
.hud.sdmode .sdbar{display:grid;grid-template-columns:1fr auto 1fr;align-items:start;gap:0;margin:0}
.hud.sdmode .sdbar[hidden]{display:none}
.sdside{display:flex;align-items:flex-start;gap:clamp(4px,1.8vw,8px)}
.sdside.l{justify-content:flex-end}
.sdside.r{justify-content:flex-start}
.sdmid{display:block;width:clamp(46px,15.5vw,64px)}
.hud.sdmode .sdc{width:calc(var(--sdb) + 4px);gap:0;filter:drop-shadow(0 2px 0 rgba(23,19,32,.45))}
.hud.sdmode .sdc .bico{width:var(--sdb);height:var(--sdb)}
.hud.sdmode .sdn{display:none}
.hud.sdmode .sdh{position:relative;z-index:1;margin-top:-6px}
.hud.sdmode .sdh svg{fill:rgba(255,255,255,.42);stroke:#171320;stroke-width:2.6}
.hud.sdmode .sdh svg.on{fill:#FF3B5C}
@media (max-height:520px) and (min-aspect-ratio:1/1){.hud.sdmode{--sdb:28px}.hud.sdmode .clock{font-size:18px}.sdside{gap:6px}.sdmid{width:54px}}"""
def apply(s):
    # the bar is built in two halves round a gap the time sits over: your side, then the others (a pair against a pair in 2v2)
    s = rep(s, "    let h = ''; order.forEach((D, i) => { if (mode === 'duo' && i === 2) h += '<b class=\"sdvs\" aria-hidden=\"true\">VS</b>';\n",
               "    const half = Math.ceil(order.length / 2); let h = '<span class=\"sdside l\">'; order.forEach((D, i) => { if (i === half) h += '</span><i class=\"sdmid\" aria-hidden=\"true\"></i><span class=\"sdside r\">'; // (v256: the time sits over the gap)\n")
    s = rep(s, "    el.innerHTML = h; }\n  for (const D of order) {\n    const c = el.querySelector('.sdc[data-t=\"' + D.team + '\"]');",
               "    el.innerHTML = h + '</span>'; }\n  for (const D of order) {\n    const c = el.querySelector('.sdc[data-t=\"' + D.team + '\"]');")
    s = rep(s, "\n</style>\n\n<div id=\"stage\">", "\n" + CSS.strip() + "\n</style>\n\n<div id=\"stage\">")
    return s
