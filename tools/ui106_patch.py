#!/usr/bin/env python3
"""v181: the New item! screen shows the shop's real item renders, and can show two items at once (the lesson's gift gives the flower and the fangs)."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui105_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
rep('<p class="nikick">New item!</p>', '<p class="nikick" id="niKick">New item!</p>')
rep('<div class="nibadge"><svg id="niIcon" viewBox="0 0 40 40" aria-hidden="true"></svg></div>', '<div class="nibadges" id="niBadges"><div class="nibadge"></div></div>')
rep(".nibadge svg{width:68%;height:68%;filter:drop-shadow(0 4px 0 rgba(12,6,32,.35))}",
    ".nibadge svg{width:68%;height:68%;filter:drop-shadow(0 4px 0 rgba(12,6,32,.35))}\n"
    ".nibadges{display:flex;justify-content:center;align-items:center;gap:clamp(14px,5vw,26px);max-width:100%}\n"
    ".nibadge img{width:84%;height:84%;object-fit:contain;filter:drop-shadow(0 5px 0 rgba(12,6,32,.3))}\n"
    ".nibadges.two .nibadge{width:min(150px,38vw)}\n"
    ".nibadges.two .nibadge:nth-child(2){animation-delay:.45s,1.3s}\n"
    "@media (max-height:520px) and (min-aspect-ratio:1/1){.nibody{gap:6px}.nibadge{width:min(150px,34vh);margin:2px 0}.nibadges.two .nibadge{width:min(100px,25vh)}.nibl{font-size:13px;bottom:-12px}.niname{font-size:clamp(22px,6.5vh,30px);white-space:nowrap}.niwhere{display:none}.nibtns{gap:6px}}\n"
    ".nibl{position:absolute;left:50%;bottom:-16px;transform:translateX(-50%);padding:4px 12px;border-radius:999px;background:var(--line);color:var(--bone);font:400 15px/1 var(--font-display);white-space:nowrap;box-shadow:0 0 0 3px var(--gold)}")
rep("""function showNewItem(id) {
  const w = ITEMS.find(x => x.id === id), el = $('newItem'); if (!w) return showEnd(endImg);
  $('niIcon').innerHTML = WEAR_ICON[w.id]; $('niName').textContent = w.name; $('niWhere').innerHTML = 'Found on ' + escAttr(WEAR_WHERE[w.stage].replace(/^the /, 'the ')) + '<span class="niprice">' + DROP_SVG + PRICE(w) + '</span>'; $('niTry').textContent = bought(w.id) ? 'Try it on' : 'See it in the shop';""",
"""function showNewItem(id) {
  const ws = [].concat(id).map(x => ITEMS.find(w => w.id === x)).filter(Boolean), w = ws[0], el = $('newItem'), two = ws.length > 1; if (!w) return showEnd(endImg);
  const pic = it => { let u = ''; try { u = shopPic(it); } catch (e) { u = ''; } return u ? '<img src="' + u + '" alt="">' : '<svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[it.id] + '</svg>'; }; /* (the shop's own render of the item, the flat icon only if that fails) */
  $('niBadges').className = 'nibadges' + (two ? ' two' : ''); $('niBadges').innerHTML = ws.map(it => '<div class="nibadge">' + pic(it) + (two ? '<b class="nibl">' + escAttr(it.name) + '</b>' : '') + '</div>').join(''); $('niKick').textContent = two ? 'New items!' : 'New item!';
  $('niName').textContent = ws.map(it => it.name).join(' + '); $('niWhere').innerHTML = two ? 'Two new items for your locker' : 'Found on ' + escAttr(WEAR_WHERE[w.stage].replace(/^the /, 'the ')) + '<span class="niprice">' + DROP_SVG + PRICE(w) + '</span>'; $('niTry').textContent = ws.every(it => bought(it.id)) ? 'Try it on' : two ? 'See them in the shop' : 'See it in the shop';""")
rep("$('niTry').addEventListener('click', () => { AU.init(); AU.ui(); const id = newItem, w = ITEMS.find(x => x.id === id);", "$('niTry').addEventListener('click', () => { AU.init(); AU.ui(); const id = [].concat(newItem)[0], w = ITEMS.find(x => x.id === id);")
rep("const w = WEAR.find(x => x.id === gift.id); banner('New item!', w ? w.name : '', true);", "const w = WEAR.find(x => x.id === gift.id); banner(tut && gift.id === 'flower' ? 'New items!' : 'New item!', tut && gift.id === 'flower' ? 'Flower + Fangs' : w ? w.name : '', true);")
rep('<p class="ver">Version 180</p>', '<p class="ver">Version 181</p>')
open(DST, 'w').write(s)
print('ui106 ok', n0, '->', len(s))
