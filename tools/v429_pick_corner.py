"""v429: on Pick a canvas, the sound button sits level with the Back button (same centre height), on every screen shape."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""
// (v429) while the canvas picker is open, the corner's sound button is moved down (or up) so its centre lines up with Back's
function worldCornerAlign() {
  const c = $('soundBtn') && $('soundBtn').parentElement; if (!c) return;
  c.style.translate = '';
  if (menuPage !== 'worlds' || $('mWorld').hidden) return;
  const a = $('worldBack').getBoundingClientRect(), b = $('soundBtn').getBoundingClientRect();
  if (!a.height || !b.height) return;
  const d = Math.round((a.top + a.bottom) / 2 - (b.top + b.bottom) / 2); if (d) c.style.translate = '0 ' + d + 'px';
}
addEventListener('resize', () => requestAnimationFrame(worldCornerAlign));
"""

def apply(s):
    s = rep(s, "  centerWorld(worldBtns.find(b => b.dataset.s === stageSel), false); renderWorlds();\n  setTimeout(() => $('startBtn').focus({ preventScroll: true }), 40);\n}\n",
               "  centerWorld(worldBtns.find(b => b.dataset.s === stageSel), false); renderWorlds();\n  setTimeout(() => $('startBtn').focus({ preventScroll: true }), 40);\n"
               "  worldCornerAlign(); requestAnimationFrame(worldCornerAlign); // (v429: sound level with Back)\n}\n" + JS)
    s = rep(s, "  if (menuPage !== 'worlds') return; closeSeason(); menuPage = 'home'; menu.dataset.page = 'home'; $('mWorld').hidden = true; $('mHome').hidden = false; heroT = 0;\n",
               "  if (menuPage !== 'worlds') return; closeSeason(); menuPage = 'home'; menu.dataset.page = 'home'; $('mWorld').hidden = true; $('mHome').hidden = false; heroT = 0; worldCornerAlign();\n")
    return s
