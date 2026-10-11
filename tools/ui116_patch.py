#!/usr/bin/env python3
"""v191: the canvases page, tidied for the onboarding vote. Upright, the coach sits under the header in the room the hidden mode tabs
leave and the paintings centre in the space below (hiding the tabs had pulled the gallery out of its stretching row); the vote note the
finger covered goes (the Play button already names your vote). On a short wide screen the title gives way to a one-line callout. And
for everyone, the gallery's side padding fits the painting's real width, so the chosen painting can sit dead centre."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui115_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep("\n</style>\n", """
@media (max-aspect-ratio:1/1){
  .menu.tutoring .mworld #modes{display:block!important;visibility:hidden;height:126px;margin:0;pointer-events:none}
  .menu.tutoring .mworld .gallery{grid-row:3}
  .menu.tutoring .mworld #gDots{grid-row:4}
  .menu.tutoring .mworld .wfoot{grid-row:5}
  .menu.tutoring #soloNote{display:none}
  .mworld .gnav{top:var(--gmid,54%)}
  .menu.tutoring .mworld .wfoot{margin-top:18px}
}
@media (min-aspect-ratio:1/1) and (max-height:520px){.menu.tutoring .mworld .whead h2{visibility:hidden}}
#stagePick .world{scroll-snap-align:none}
#stagePick .world .frame{scroll-snap-align:center}
</style>
""")
rep("const gallery = $('stagePick'), worldBtns = [...gallery.querySelectorAll('.world')];",
    "const gallery = $('stagePick'), worldBtns = [...gallery.querySelectorAll('.world')];\n"
    "/* the side padding matches the painting's real width (it changes with the screen), so the first and last can sit dead centre too */\n"
    "{ let gpW = 0, gpQ = 0; const gpFit = () => { gpQ = 0; const on = worldBtns.find(b => b.getAttribute('aria-pressed') === 'true') || worldBtns[0]; if (!on || !gallery.clientWidth || !on.offsetWidth) return;\n"
    "    const mw = $('mWorld'), gr = gallery.getBoundingClientRect(), mr = mw.getBoundingClientRect(); mw.style.setProperty('--gmid', Math.round(gr.top - mr.top + gr.height / 2) + 'px'); /* (the arrows' height: the middle of the gallery) */\n"
    "    const fr = on.querySelector('.frame') || on, fl = fr === on ? 0 : fr.offsetLeft, fw = fr.offsetWidth, ww = on.offsetWidth, cw = gallery.clientWidth; /* (the frame can be wider than its button: centre the frame) */\n"
    "    const pl = Math.max(12, Math.round(cw / 2 - fl - fw / 2)), pr = Math.max(12, Math.round(cw / 2 + fl + fw / 2 - ww)); if (pl + ',' + pr !== gpW) { gpW = pl + ',' + pr; gallery.style.paddingLeft = pl + 'px'; gallery.style.paddingRight = pr + 'px'; }\n"
    "    if (gallery.scrollWidth > cw + 4) gallery.scrollLeft = on.offsetLeft + fl + fw / 2 - cw / 2; };\n"
    "  const gpSoon = () => { if (!gpQ) gpQ = requestAnimationFrame(gpFit); }; /* (next frame, never inside the resize callback: no observer loop) */\n"
    "  if (window.ResizeObserver) new ResizeObserver(gpSoon).observe(gallery); addEventListener('resize', gpSoon); window.__gpFit = gpSoon; }")
rep("function centerWorld(b, smooth) { if (!galScrolls() || !b) return; gallery.scrollTo({ left: b.offsetLeft + b.offsetWidth / 2 - gallery.clientWidth / 2,", "function centerWorld(b, smooth) { if (!galScrolls() || !b) return; const fr = b.querySelector('.frame'); gallery.scrollTo({ left: b.offsetLeft + (fr ? fr.offsetLeft + fr.offsetWidth / 2 : b.offsetWidth / 2) - gallery.clientWidth / 2,")
rep('<p class="ver">Version 190</p>', '<p class="ver">Version 191</p>')
open(DST, 'w').write(s)
print('ui116 ok', n0, '->', len(s))
