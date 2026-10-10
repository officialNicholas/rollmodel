#!/usr/bin/env python3
"""The Paint Shop, done properly: every item shown as it really looks, rendered on your blob (greyed out until it is yours to buy), on tall cards with a paper plate for the name and the price; the season's finds first under their own banner, then headgear, facial, clothing and eyes. On top of ui59_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui59_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
def cut(a, b, new):
    global s
    i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j:]

cut('  <section class="shop" id="shop" hidden role="dialog" aria-labelledby="shopTitle">', '  <section class="sheet lookp" id="look"', '''  <section class="shop" id="shop" hidden role="dialog" aria-labelledby="shopTitle">
    <div class="shtop"><h2 class="ctitle" id="shopTitle">Paint Shop</h2><span class="lkbal shbal" id="shBal" aria-label="Dabs"></span><button class="btn sm shback" id="shopBack" type="button">Back</button></div>
    <div class="shgrid" id="shopGrid" role="list"></div>
    <p class="shnote" id="shopNote" aria-live="polite"></p>
  </section>
''')
cut("const SHOP_CATS = [['head', 'Headgear'], ['face', 'Facial'], ['cloth', 'Clothing'], ['eyes', 'Eyes']];", "function openShop(from) {", r'''const SHOP_CATS = [['season', 'Season One · Halloween'], ['head', 'Headgear'], ['face', 'Facial'], ['cloth', 'Clothing'], ['eyes', 'Eyes']];
function shopNote(t, bad) { const el = $('shopNote'); el.textContent = t; el.classList.toggle('bad', !!bad); restartCls(el, 'on'); clearTimeout(shopNoteT); shopNoteT = setTimeout(() => el.classList.remove('on'), 3200); }
// each item as it looks on you: your blob wearing it, rendered once and kept (again if your paint changes)
const shopPics = new Map(); let shopPicKey = '';
function shopPic(w) {
  const key = colorId + ':' + (myLook.eyes || '') + ':' + (myLook.iris || ''); if (shopPicKey !== key) { shopPics.clear(); shopPicKey = key; }
  if (shopPics.has(w.id)) return shopPics.get(w.id);
  const saved = Object.assign({}, myLook), base = { head: null, side: null, eye: null, lash: null, mouth: null, neck: null, back: null };
  Object.assign(myLook, base, w.slot === 'eyes' ? { eyes: w.id } : { [w.slot]: w.id }); if (w.slot === 'eyes') myLook.iris = saved.iris;
  const propsOn = lobbyProps.visible; lobbyProps.visible = false; // (the locker's set dressing stays out of the shot)
  let c = null; try { visuals(0, 0); c = portraitOf(P, 220, 260, { zoom: w.cat === 'cloth' ? 0.78 : w.cat === 'head' ? 0.86 : 0.9, low: w.cat === 'cloth' ? 0.55 : w.cat === 'head' ? -0.05 : 0.06 }); } catch (e) { c = null; }
  lobbyProps.visible = propsOn; Object.assign(myLook, saved); try { visuals(0, 0); } catch (e) {}
  const url = c ? c.toDataURL('image/png') : ''; shopPics.set(w.id, url); return url;
}
function renderShop() {
  const n = store.drops || 0; $('shBal').innerHTML = DROP_SVG + '<b>' + n + '</b>';
  let h = '', any = false; const done = new Set();
  for (const [c, label] of SHOP_CATS) { const items = ITEMS.filter(w => !bought(w.id) && !done.has(w.id) && (c === 'season' ? !!w.season : w.cat === c)); if (!items.length) continue; any = true; for (const w of items) done.add(w.id);
    h += '<div class="shcat' + (c === 'season' ? ' season' : '') + '"><b>' + label + '</b>' + (c === 'season' ? '<small>Found on the Halloween canvases</small>' : '') + '</div>' + items.map(w => { const found = owns(w.id) || !needFind(w), broke = found && n < PRICE(w), where = WEAR_WHERE[w.stage], pic = shopPic(w);
      return '<button class="shitem' + (found ? (broke ? ' broke' : '') : ' locked') + (found && owns(w.id) && needFind(w) && !bought(w.id) ? ' fresh' : '') + '" type="button" role="listitem" data-w="' + w.id + '" aria-label="' + escAttr(w.name + ', ' + PRICE(w) + ' dabs' + (found ? (broke ? ', ' + (PRICE(w) - n) + ' more needed' : '') : ', locked. Find it on ' + where)) + '">'
        + '<span class="shin"><span class="shpic">' + (pic ? '<img src="' + pic + '" alt="">' : '<svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg>') + (found ? '' : LOCK_ICON) + '</span>'
        + '<span class="shplate"><b class="shn">' + w.name + '</b><span class="shw">' + (found ? (broke ? 'Need ' + (PRICE(w) - n) + ' more' : owns(w.id) && needFind(w) ? 'Found on ' + where : 'In stock') : 'Find it on ' + where) + '</span><span class="shp">' + DROP_SVG + PRICE(w) + '</span></span></span></button>'; }).join(''); }
  $('shopGrid').innerHTML = any ? h : '<p class="shempty">' + SHOP_ICON + 'Nothing left to buy.<br>Everything is in your locker.</p>';
}
''')
cut('/* the locker is yours; the Paint Shop sells the rest */', '.menu.shopping .mhome{visibility:hidden}', '''/* the locker is yours; the Paint Shop sells the rest */
.lkbal{appearance:none;border:0;cursor:pointer;font-family:var(--font-head)}
.lkbal small{font:800 9px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:var(--ink);margin-left:3px;padding-left:7px;border-left:2px solid rgba(23,19,32,.18)}
.lkbal:focus-visible{outline:3px solid var(--ink);outline-offset:2px}
.lcol.right .plate.stat.drops{cursor:pointer}
.lcol.right .plate.stat.drops:active b{transform:translateY(1px)}
.lcol.right .plate.stat.drops:focus-visible{outline:3px solid var(--ink);outline-offset:2px;border-radius:6px}
.shoptag{display:inline-block;font-style:normal;margin-left:3px;padding:2px 5px 2px;border-radius:3px;background:var(--ink);color:#fff;letter-spacing:.1em;vertical-align:1px}
.ltile.shopgo{border:2px dashed rgba(23,19,32,.3);background:var(--paper-2)}
.ltile.shopgo .ltn{color:var(--ink)}
.ltile.shopgo .ltag.n{background:var(--ink);color:#fff;min-width:16px;justify-content:center}
.shop{position:absolute;inset:0;z-index:13;display:flex;flex-direction:column;gap:10px;box-sizing:border-box;padding:max(14px,env(safe-area-inset-top)) max(16px,env(safe-area-inset-right)) max(12px,env(safe-area-inset-bottom)) max(16px,env(safe-area-inset-left));background:#17131F url(art/m_wall.webp) center top/cover no-repeat;color:var(--cream);animation:fadein .25s both}
.shop::before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 70% 40% at 50% 0%,rgba(255,138,31,.16),rgba(255,255,255,0) 70%);pointer-events:none}
.shtop{position:relative;display:flex;align-items:center;gap:12px;min-height:44px}
.shtop .ctitle{margin:0;font-size:28px;color:var(--cream);text-align:left;text-shadow:.05em .06em 0 var(--ink)}
.shbal{margin-left:auto;margin-right:0;cursor:default}
.shback{min-height:40px;padding:0 16px;font-size:15px}
.shgrid{position:relative;display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));grid-auto-rows:max-content;gap:12px;align-content:start;overflow:auto;overscroll-behavior:contain;padding:6px 2px 18px;margin:0 -2px;min-height:0;flex:1;scrollbar-width:none;-webkit-mask:linear-gradient(#000 calc(100% - 18px),transparent);mask:linear-gradient(#000 calc(100% - 18px),transparent)}
.shgrid::-webkit-scrollbar{display:none}
.shcat{grid-column:1/-1;display:flex;align-items:baseline;gap:10px;margin:8px 0 -2px;font:800 11px/1 var(--font-ui);letter-spacing:.16em;text-transform:uppercase;color:#B8B0C8}
.shcat small{font:800 10px/1 var(--font-ui);letter-spacing:.04em;text-transform:none;color:#8E8698}
.shcat.season{margin-top:0;padding:10px 14px;border-radius:6px;background:var(--ink);color:#fff;box-shadow:4px 4px 0 rgba(0,0,0,.35);transform:rotate(-1deg)}
.shcat.season b{font:400 18px/1 var(--font-display);letter-spacing:0;text-transform:none;text-shadow:2px 2px 0 rgba(0,0,0,.35)}
.shcat.season small{color:rgba(255,255,255,.8)}
.shitem{appearance:none;position:relative;display:block;width:100%;padding:0;margin:0;background:#fff url(art/m_paperbg.webp) center/300px;border:2.5px solid var(--black);border-radius:10px;box-shadow:4px 4px 0 rgba(255,255,255,.18);color:var(--black);cursor:pointer;text-align:center;overflow:hidden;transition:transform .15s}
.shitem:active{transform:translateY(1px)}
.shitem:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.shin{display:grid;grid-template-rows:auto auto}
.shpic{position:relative;display:block;height:clamp(140px,46vw,200px);background:radial-gradient(ellipse 70% 55% at 50% 60%,#FFF6EC,#E9DFD0);border-bottom:2.5px solid var(--black)}
.shpic img,.shpic svg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.shpic svg{padding:22%;box-sizing:border-box}
.shplate{display:grid;justify-items:center;gap:5px;padding:9px 8px 10px}
.shn{font:900 14px/1.1 var(--font-head);text-transform:uppercase}
.shw{font:800 10.5px/1.2 var(--font-ui);color:var(--muted);min-height:1.2em}
.shp{display:inline-flex;align-items:center;gap:4px;padding:6px 11px 6px 8px;border-radius:99px;background:var(--ink);color:#fff;font:900 13px/1 var(--font-head)}
.shp .dropi{width:15px;height:15px}
.shitem.broke .shp{background:#8E8698}
.shitem.locked .shpic{background:radial-gradient(ellipse 70% 55% at 50% 60%,#D9D2C8,#B9B1A6)}
.shitem.locked .shpic img,.shitem.locked .shpic svg{filter:grayscale(1) brightness(.62) contrast(1.15);opacity:.9}
.shitem.locked .shn{opacity:.75}
.shitem.locked .shp{background:#8E8698}
.shitem .lk{position:absolute;right:8px;top:8px;width:22px;height:22px;display:grid;place-items:center;border-radius:7px;background:var(--black);color:var(--cream);box-shadow:2px 2px 0 rgba(255,255,255,.25)}
.shitem .lk svg{position:static;width:13px;height:13px;padding:0;filter:none;opacity:1}
.shitem.fresh::after{content:"NEW";position:absolute;left:-2px;top:10px;padding:4px 9px 4px 11px;background:var(--gold);color:var(--black);font:900 10px/1 var(--font-head);letter-spacing:.1em;border:2px solid var(--black);border-left:0;border-radius:0 6px 6px 0;box-shadow:2px 2px 0 var(--black)}
.shitem.got{border-color:var(--gold);box-shadow:4px 4px 0 rgba(255,255,255,.18),0 0 0 3px var(--gold)}
.shitem.got .shw{color:#8A5A12}
.shitem.got .shp{background:var(--gold);color:var(--black)}
.shitem.nope{animation:nope .35s}
.shitem.tpop{animation:tilepop .42s cubic-bezier(.2,1.6,.4,1)}
.shempty{grid-column:1/-1;display:grid;justify-items:center;gap:10px;padding:28px 16px;font:800 15px/1.4 var(--font-ui);color:#B8B0C8;text-align:center}
.shempty svg{width:56px;height:56px}
.shnote{position:absolute;left:50%;bottom:max(18px,env(safe-area-inset-bottom));transform:translate(-50%,8px);max-width:min(88vw,420px);margin:0;padding:9px 14px;border-radius:6px;background:var(--paper);color:var(--black);border:2px solid var(--black);box-shadow:3px 3px 0 var(--black);font:800 13px/1.3 var(--font-ui);text-align:center;opacity:0;pointer-events:none;transition:opacity .2s,transform .2s}
.shnote.on{opacity:1;transform:translate(-50%,0)}
.shnote.bad{background:var(--ink);color:#fff}
@media (max-height:520px) and (min-aspect-ratio:1/1){.shop{gap:6px}.shtop{min-height:38px}.shtop .ctitle{font-size:22px}.shgrid{grid-template-columns:repeat(auto-fill,minmax(128px,1fr));gap:8px}.shpic{height:clamp(96px,34vh,150px)}.shplate{padding:6px 6px 8px;gap:3px}.shn{font-size:12px}.shcat.season{padding:6px 12px}}
@media (prefers-reduced-motion:reduce){.shop,.shitem.tpop,.shitem.nope{animation:none}}
''')
# a bought item is in stock in the locker now
rep("AU.power(); b.classList.add('got'); b.querySelector('.shw').textContent = 'In your locker';", "AU.power(); b.classList.add('got'); b.classList.remove('fresh'); b.querySelector('.shw').textContent = 'In your locker';")

m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
