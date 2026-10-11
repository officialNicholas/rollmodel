#!/usr/bin/env python3
"""v216: the locker's dabs and shop. Your dabs sit over the top of the locker view in the home screen's own coin-and-tab counter (a tap
opens the Paint Shop); a big Shop button stands in the bottom right corner of the view, just above the locker panel (beside it, when the
panel sits at the side). The little dabs pill in the panel's header goes."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui143_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the home screen's counter, its markup as it is (own ids)
i0 = s.index('<button class="dabs" id="dabsBtn"'); i1 = s.index('</button>', i0) + len('</button>')
dabs = s[i0:i1].replace('id="dabsBtn"', 'id="lkDabs" hidden').replace('id="statDrops"', 'id="lkDabsN"')
assert 'id="lkDabsN"' in dabs
SHOP_SVG = ('<svg viewBox="0 0 48 40" aria-hidden="true"><rect x="8" y="15" width="32" height="21" rx="2" fill="#F4EEE3" stroke="#171320" stroke-width="2.4"/>'
            '<rect x="19.5" y="22" width="9" height="14" rx="1.6" fill="#38334E" stroke="#171320" stroke-width="2"/><circle cx="26" cy="29.5" r="1" fill="#F2C14E"/>'
            '<rect x="11.5" y="20.5" width="6" height="6" rx="1" fill="#A9DDF2" stroke="#171320" stroke-width="1.6"/><rect x="30.5" y="20.5" width="6" height="6" rx="1" fill="#A9DDF2" stroke="#171320" stroke-width="1.6"/>'
            + ''.join(f'<path class="{"aw" if k % 2 == 0 else "aw2"}" d="M{3 + 8.4 * k:.1f} 9h8.4v6.4a4.2 3.6 0 0 1-8.4 0z" stroke="#171320" stroke-width="2" stroke-linejoin="round"/>' for k in range(5))
            + '<rect x="2.5" y="5" width="43" height="5" rx="2" fill="#171320"/></svg>')
rep('  <section class="sheet lookp" id="look" hidden role="dialog" aria-labelledby="lookTitle">',
    '  ' + dabs + '\n  <button class="lkshop" id="lkShop" type="button" hidden aria-haspopup="dialog" aria-label="Open the Paint Shop">' + SHOP_SVG + '<b>Shop</b></button>\n'
    '  <section class="sheet lookp" id="look" hidden role="dialog" aria-labelledby="lookTitle">')
CSS = """
/* the locker: your dabs over the top of the view, a big Shop button in its bottom right corner (both placed by lockerTick) */
#lkDabs{position:absolute;z-index:6;left:0;top:max(10px,calc(env(safe-area-inset-top,0px) + 8px))}
.lkshop{appearance:none;position:absolute;z-index:6;left:0;top:0;display:grid;justify-items:center;align-content:end;width:92px;height:76px;margin:0;padding:0 0 10px;border:0;border-radius:16px;background:linear-gradient(180deg,#4F4A69 0%,#38334E 58%,#2B273D 100%);box-shadow:0 0 0 2.5px #171320,inset 0 2px 0 rgba(255,255,255,.2),inset 0 -4px 0 rgba(0,0,0,.25),0 5px 0 #171320,0 12px 20px rgba(23,19,32,.3);cursor:pointer;font:inherit;-webkit-tap-highlight-color:transparent;transition:transform .14s cubic-bezier(.3,1.6,.5,1)}
.lkshop svg{position:absolute;left:50%;top:-24px;width:74px;height:62px;transform:translateX(-50%);filter:drop-shadow(0 3px 0 rgba(23,19,32,.35));pointer-events:none}
.lkshop .aw{fill:var(--ink)}.lkshop .aw2{fill:#fff}
.lkshop b{font:400 19px/1 var(--font-display);color:#fff;letter-spacing:.04em;text-transform:uppercase;text-shadow:0 2px 0 #171320,1.5px 0 0 #171320,-1.5px 0 0 #171320,0 -1.5px 0 #171320}
.lkshop:hover{transform:translateY(-2px)}.lkshop:active{transform:translateY(3px)}
.lkshop:focus-visible{outline:3px solid var(--gold);outline-offset:4px}
#lkBal{display:none}
"""
rep("/* abilities: violet construction paper", CSS.lstrip('\n') + "/* abilities: violet construction paper")
JS = """
// the locker's dabs and shop: shown while it's open (not under the shop), the counter centred over the view, the button in the view's
// bottom right corner just above the panel (or beside it, when the panel stands at the side)
function lockerTick() {
  const on = lookOpen && !shopOpen && !lookEl.hidden && state === 'menu', dB = $('lkDabs'), sB = $('lkShop');
  if (dB.hidden === on) { dB.hidden = sB.hidden = !on; }
  if (!on) return;
  const r = stage.getBoundingClientRect(), k = lookEl.getBoundingClientRect(), side = k.left - r.left > r.width * 0.4 && k.height > r.height * 0.5;
  const viewR = side ? k.left - r.left : r.width, dw = dB.offsetWidth || 150;
  dB.style.left = Math.max(8, viewR / 2 - dw / 2).toFixed(1) + 'px';
  const sw = sB.offsetWidth || 92, sh = sB.offsetHeight || 76;
  if (side) { sB.style.left = (k.left - r.left - sw - 18).toFixed(1) + 'px'; sB.style.top = (k.bottom - r.top - sh - 6).toFixed(1) + 'px'; }
  else { sB.style.left = (Math.min(r.width, k.right - r.left) - sw - 16).toFixed(1) + 'px'; sB.style.top = (k.top - r.top - sh - 20).toFixed(1) + 'px'; }
}
$('lkDabs').addEventListener('click', () => { AU.init(); AU.ui(); openShop('look'); });
$('lkShop').addEventListener('click', () => { AU.init(); AU.ui(); openShop('look'); });
"""
rep("$('lkBal').addEventListener('click', () => { AU.init(); AU.ui(); openShop('look'); });",
    "$('lkBal').addEventListener('click', () => { AU.init(); AU.ui(); openShop('look'); });" + JS.rstrip('\n'))
rep("visuals(dt, rdt); flushTrail(); pbarTick(rdt);", "visuals(dt, rdt); flushTrail(); pbarTick(rdt); lockerTick();")
# the counter keeps count; the focus, the purchase's kick and the onboarding's pointer go to the new pieces
rep("if ($('lkBalN')) $('lkBalN').textContent = String(n); }", "if ($('lkBalN')) $('lkBalN').textContent = String(n); if ($('lkDabsN')) $('lkDabsN').textContent = String(n); }")
rep("if (lookOpen) { renderLook(); railEdge(); setTimeout(() => $('lkBal').focus({ preventScroll: true }), 30); }", "if (lookOpen) { renderLook(); railEdge(); setTimeout(() => $('lkShop').focus({ preventScroll: true }), 30); }")
n_kick = s.count("kick($('lkBal'),"); assert n_kick >= 1
s = s.replace("kick($('lkBal'),", "kick($('lkDabs'),")
rep("if (lookOpen) return tutShow('Open the Paint Shop', 'lkBal', 'shop');", "if (lookOpen) return tutShow('Open the Paint Shop', 'lkShop', 'shop');")
rep('<p class="ver">Version 215</p>', '<p class="ver">Version 216</p>')
open(DST, 'w').write(s)
print('ui144 ok', n0, '->', len(s), 'kicks', n_kick)
