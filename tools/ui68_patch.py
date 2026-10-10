#!/usr/bin/env python3
"""The results tell it on the one bar: the names sit inside the paint, the crown on the winner's, and each side's eliminations sit next to its percentage. The score rows below, which said the same again, are gone (their words go to the bar's label for screen readers). On top of ui67_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui67_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

rep('<div class="judge" id="judge" aria-hidden="true"><div class="jnums" id="jNums"></div><div class="jbar" id="jBar"></div></div>',
    '<div class="judge" id="judge" role="img" aria-label="Scores"><div class="jnums" id="jNums"></div><div class="jbar" id="jBar"></div><div class="jlab" id="jLab" aria-hidden="true"></div></div>')
# the numbers carry the eliminations; the names go on the bar
rep("  let jb = '', jn = '';\n  if (solo) {", "  let jb = '', jn = '', jl = ''; const kosOf = D => info.kos ? info.kos[D.team] : D.kos || 0;\n  if (solo) {")
rep("""    jn = '<b data-to="' + Math.round(you) + '" data-a="left" style="--chi:var(--ink-hi)">0%</b>' + (best ? '<b data-a="right" style="--chi:var(--gold)"><small>' + (info.newBest ? 'Old best' : 'Best') + '</small>' + best + '%</b>' : '');""",
    """    jn = '<b data-to="' + Math.round(you) + '" data-a="left" style="--chi:var(--ink-hi)"><span class="jv">0%</span></b>' + (best ? '<b data-a="right" style="--chi:var(--gold)"><small>' + (info.newBest ? 'Old best' : 'Best') + '</small><span class="jv">' + best + '%</span></b>' : '');
    jl = '<span class="jl" data-a="left">' + escAttr(playerName()) + '</span>';""")
rep("""      jn += '<b data-to="' + Math.round(covOf(D)) + '" data-a="' + o + '" data-x="' + (x + sh / 2).toFixed(3) + '" style="--chi:' + hi + '">0%</b>';""",
    """      jn += '<b data-to="' + Math.round(covOf(D)) + '" data-a="' + o + '" data-x="' + (x + sh / 2).toFixed(3) + '" style="--chi:' + hi + '"><span class="jv">0%</span><small class="jko">' + KO_SVG + kosOf(D) + '</small></b>';
      jl += '<span class="jl' + (D === P ? ' me' : '') + '" data-a="' + o + '" data-x="' + (x + sh / 2).toFixed(3) + '">' + (info.winner === D ? CROWN_SVG : '') + escAttr(D === P ? playerName() : nameOf(D)) + '</span>';""")
rep("  $('jBar').innerHTML = jb; $('jNums').innerHTML = jn; $('judge').classList.remove('go');", "  $('jBar').innerHTML = jb; $('jNums').innerHTML = jn; $('jLab').innerHTML = jl; $('judge').classList.remove('go');")
# the rows below said it again: gone, their words on the bar for screen readers
rep("  ppl.forEach((e, i) => {\n    const D = e.D, me = D === P, [c, hi] = colVars(D), top = topK === D, nm = me ? playerName() : nameOf(D);",
    "  const says = [];\n  ppl.forEach((e, i) => {\n    const D = e.D, me = D === P, [c, hi] = colVars(D), top = topK === D, nm = me ? playerName() : nameOf(D);")
rep("    h += '<div class=\"brow' + (me ? ' you' : '') + '\" role=\"listitem\" aria-label=\"' + escAttr(say) + '\"", "    says.push(say); h += '<div class=\"brow' + (me ? ' you' : '') + '\" role=\"listitem\" aria-label=\"' + escAttr(say) + '\"")
rep("  const bd = $('board'); bd.className = 'board' + (solo ? ' solo' : ''); bd.innerHTML = h;",
    "  const bd = $('board'); bd.className = 'board' + (solo ? ' solo' : ''); bd.innerHTML = ''; bd.hidden = true; $('judge').setAttribute('aria-label', says.join('. ') + (solo && (info.newBest ? info.prevBest : info.best) ? '. ' + (info.newBest ? 'Old best ' : 'Your best ') + (info.newBest ? info.prevBest : info.best) + '%' : ''));")
# the count-up writes into the number alone, and the names are placed like the numbers
rep("  for (const b of nums) if (b.dataset.to) b.textContent = b.dataset.to + '%';\n  const ws = nums.map(b => b.offsetWidth);",
    "  const jv = b => b.querySelector('.jv') || b; for (const b of nums) if (b.dataset.to) jv(b).textContent = b.dataset.to + '%';\n  const ws = nums.map(b => b.offsetWidth);\n  { const lab = $('jLab'), ls = Array.from(lab.children), LW = lab.offsetWidth, lw = ls.map(l => l.offsetWidth), ln = ls.length - 1; ls.forEach((l, i) => { const a = l.dataset.a; l.style.left = l.style.right = ''; if (a === 'right') l.style.right = 'var(--in)'; else if (a === 'center') { const lo = lw[0] + 24, hi = LW - lw[ln] - 24 - lw[i]; l.style.left = clamp(parseFloat(l.dataset.x) / 100 * LW - lw[i] / 2, lo, Math.max(lo, hi)).toFixed(1) + 'px'; } else l.style.left = 'var(--in)'; }); }")
rep("  for (const b of counted) b.textContent = '0%';\n  void box.offsetWidth;", "  for (const b of counted) jv(b).textContent = '0%';\n  void box.offsetWidth;")
rep("for (const b of counted) b.textContent = Math.round(+b.dataset.to * k) + '%'; if (u < 1) requestAnimationFrame(tick); };", "for (const b of counted) jv(b).textContent = Math.round(+b.dataset.to * k) + '%'; if (u < 1) requestAnimationFrame(tick); };")
css = '''
/* the results bar tells it all: names in the paint, eliminations by the numbers */
#end .judge{--jh:42px;position:relative;gap:6px;grid-template-columns:minmax(0,1fr)}
#end .jnums{grid-row:1;grid-column:1}
#end .jbar{height:var(--jh);grid-row:2;grid-column:1}
#end .jlab{position:relative;z-index:1;grid-row:2;grid-column:1;pointer-events:none} /* (the same cell as the bar, so it sits over it whatever the row's size) */
#end .jl{position:absolute;top:50%;transform:translateY(-50%);--in:calc(var(--jh) * .25 + 10px);display:inline-flex;align-items:center;gap:5px;max-width:46%;font:900 14px/1 var(--font-head);text-transform:uppercase;letter-spacing:.02em;color:#fff;text-shadow:-1.5px -1.5px 0 var(--black),1.5px -1.5px 0 var(--black),-1.5px 1.5px 0 var(--black),1.5px 1.5px 0 var(--black),0 2.5px 0 var(--black);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;opacity:0;transition:opacity .4s .9s}
#end .judge.go .jl{opacity:1}
#end .jl .crown{width:18px;height:15px;flex:none;fill:var(--gold);stroke:var(--black);stroke-width:2;stroke-linejoin:round;filter:none;position:static;margin:0}
#end .jnums b .jko{display:inline-flex;align-items:center;gap:3px;margin:0 0 0 7px;font:800 13px/1 var(--font-ui);color:#D9D2E6;text-shadow:none;vertical-align:5px}
#end .jnums b .jko svg{width:13px;height:13px;fill:var(--gold);stroke:var(--black);stroke-width:1.4;stroke-linejoin:round}
#end .board[hidden]{display:none}
@media (max-height:720px) and (max-aspect-ratio:1/1){#end .judge{--jh:34px}#end .jl{font-size:12.5px}}
@media (max-height:520px) and (min-aspect-ratio:1/1){#end .judge{--jh:30px}#end .jl{font-size:12px}#end .jnums b .jko{font-size:12px}}
@media (prefers-reduced-motion:reduce){#end .jl{transition:none}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
