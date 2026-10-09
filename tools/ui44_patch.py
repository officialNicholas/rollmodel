#!/usr/bin/env python3
"""The locker folds into categories: Paint, Eyes, Head, Face, Clothing tabs with one row of content, so the stage keeps 55 percent of a phone screen. On top of ui43_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui43_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# two more tabs in front: paint and eyes
rep('<div class="seg lcats" id="lookCats" role="tablist" aria-label="Accessories"><button class="lcat" type="button" role="tab" id="lc-head" data-cat="head" data-label="Headgear" aria-controls="lookRail" aria-selected="true">Headgear</button>',
    '<div class="seg lcats" id="lookCats" role="tablist" aria-label="Your look"><button class="lcat" type="button" role="tab" id="lc-paint" data-cat="paint" data-label="Paint" aria-controls="swatches" aria-selected="true">Paint</button><button class="lcat" type="button" role="tab" id="lc-eyes" data-cat="eyes" data-label="Eyes" aria-controls="eyeStyles" aria-selected="false" tabindex="-1">Eyes</button><button class="lcat" type="button" role="tab" id="lc-head" data-cat="head" data-label="Headgear" aria-controls="lookRail" aria-selected="false" tabindex="-1">Headgear</button>')
rep("let lookCat = 'head'; // the category open in Customize", "let lookCat = 'paint'; // the category open in the locker")
# the tab faces: paint shows your colour, eyes your eye style, the rest what is worn
rep("""    const worn = WEAR.filter(w => w.cat === c && myLook[w.slot] === w.id), w0 = worn[0];
    b.innerHTML = '<small>' + b.dataset.label + '</small><span class="lci">' + (w0 ? '<svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w0.id] + '</svg>' : '<i class="none"></i>') + '</span><b>' + (w0 ? (worn.length > 1 ? w0.name + ' +' + (worn.length - 1) : w0.name) : 'Nothing on') + '</b>'; }""",
    """    if (c === 'paint') { b.innerHTML = '<small>Paint</small><span class="lci"><i class="dab" style="--c:' + TEAMS[0].css + '"></i></span><b>' + colorOf().name + '</b>'; continue; }
    if (c === 'eyes') { b.innerHTML = '<small>Eyes</small><span class="lci">' + ES_ICON_T[myLook.eyes || 'round'] + '</span><b>' + (EYE_STYLES[myLook.eyes || 'round'] || 'Round') + '</b>'; continue; }
    const worn = WEAR.filter(w => w.cat === c && myLook[w.slot] === w.id), w0 = worn[0];
    b.innerHTML = '<small>' + b.dataset.label + '</small><span class="lci">' + (w0 ? '<svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w0.id] + '</svg>' : '<i class="none"></i>') + '</span><b>' + (w0 ? (worn.length > 1 ? w0.name + ' +' + (worn.length - 1) : w0.name) : 'Nothing on') + '</b>'; }
  $('look').dataset.tab = lookCat;""")
# the eye style icons are drawn where the tab can reach them
rep("  const ES_ICON = { round:", "  const ES_ICON = ES_ICON_T; void 0 && { round:")
rep("function renderLook() {\n  const fresh = new Set(store.fresh || []);", "function renderLook() {\n  const fresh = new Set(store.fresh || []);\n  if (!['paint', 'eyes', 'head', 'face', 'cloth'].includes(lookCat)) lookCat = 'paint';")
rep("$('lookCats').addEventListener('keydown', e => { const cats = ['head', 'face', 'cloth'], i = cats.indexOf(lookCat); if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); e.stopPropagation(); openCat(cats[(i + (e.key === 'ArrowRight' ? 1 : 2)) % 3], true); } });",
    "$('lookCats').addEventListener('keydown', e => { const cats = ['paint', 'eyes', 'head', 'face', 'cloth'], i = cats.indexOf(lookCat); if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); e.stopPropagation(); openCat(cats[(i + (e.key === 'ArrowRight' ? 1 : 4)) % 5], true); } });")
# the eye style icon table becomes a constant above the locker code (it was declared inside renderSwatches' scope)
a = s.index("  const ES_ICON = ES_ICON_T; void 0 && { round:"); b = s.index("};\n", a) + 3
icons = s[s.index("{ round:", a):b - 1]
s = s[:a] + "  const ES_ICON = ES_ICON_T;\n" + s[b:]
s = s.replace("function renderLook() {\n  const fresh = new Set(store.fresh || []);", "const ES_ICON_T = " + icons.rstrip() + ";\nfunction renderLook() {\n  const fresh = new Set(store.fresh || []);", 1)
css = '''
/* the locker, folded: one strip of tabs, one row of what the tab holds */
.lookp{gap:8px;padding-top:10px}
@media (max-aspect-ratio:1/1){.sheet.lookp{max-height:45%}}
.lookp .lktop{min-height:38px}
.lookp .ctitle{font-size:22px}
.lnbtn{height:38px;font-size:15px}
.lookp .swatches,.lookp .leyes,.lookp .lrail{display:none}
.lookp[data-tab="paint"] .swatches{display:flex;justify-content:space-around;padding:6px 0 2px}
.lookp[data-tab="eyes"] .leyes{display:flex;justify-content:space-between;margin:4px 0 0}
.lookp[data-tab="eyes"] .leyes .lhead{display:none}
.lookp[data-tab="head"] .lrail,.lookp[data-tab="face"] .lrail,.lookp[data-tab="cloth"] .lrail{display:flex}
.seg.lcats{grid-template-columns:repeat(5,1fr);gap:5px}
.seg.lcats button,.seg.lcats button[aria-selected="true"]{min-height:58px;padding:5px 2px 6px;gap:2px}
.seg.lcats button small{font-size:7.5px;letter-spacing:.1em}
.seg.lcats button .lci{width:24px;height:24px}
.seg.lcats button .lci svg{width:22px;height:22px}
.seg.lcats button b{font-size:9px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.seg.lcats button .lci .dab{display:block;width:24px;height:24px;background:var(--c);-webkit-mask:url(art/m_splat2.webp) center/contain no-repeat;mask:url(art/m_splat2.webp) center/contain no-repeat}
.sw{width:44px;height:44px}
.sw i{width:38px;height:38px}
.ltile{width:76px;height:80px}
.lookp .btn.play.sm{min-height:44px}
.ucode{margin-top:-6px}
.ulink{font-size:12px;padding:2px 8px}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + css + s[j:]
rep('<p class="ver">Version 113</p>', '<p class="ver">Version 114</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
