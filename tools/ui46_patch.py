#!/usr/bin/env python3
"""My locker (what you own) and the Paint Shop (what is for sale), reached from the locker or by tapping your dabs. The shop and locker play the spooky cut of the menu song, picked up at the same bar, and the lobby song comes back at the same bar on the way out. On top of ui45_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui45_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- the music: the spooky cut of the menu song, swapped at the same bar ----
rep("    menu: { a: 6.928, b: 43.72223, k: 0.923 },", "    menu: { a: 6.928, b: 43.72223, k: 0.923 },\n    spook: { a: 7.32, b: 46.21, k: 0.795 }, // the same song, the Halloween cut (trimmed so its bars line up with the menu song's)")
rep("  function trkStop(fade) { if (!trk) return;",
    """  // the lobby song and the locker song are one tune in two moods: moving between them carries on from the same bar
  const SWAP = { menu: 'spook', spook: 'menu' };
  function trkPos() { if (!trk) return 0; const R = TRK[trk.key], p = T() - trk.t0, b = Math.min(R.b, trk.src.buffer.duration), len = b - R.a; return p <= b || len <= 0 ? p : R.a + ((p - R.a) % len); }
  function carryOff(key) { if (!trk || SWAP[trk.key] !== key) return 0; const A = TRK[trk.key], B = TRK[key]; return Math.max(0, B.a + (trkPos() - A.a) / (A.b - A.a) * (B.b - B.a)); }
  function trkStop(fade) { if (!trk) return;""")
rep("const ok = b => { R.decoding = false; if (!R.wantDecode) return; R.buf = b; if (trkWant === key && ctx && (!trk || trk.key !== key) && lastMode !== 'pause') { trkPend = null; trkGo(key, 1.4, trk ? 1.2 : 0.6); } }",
    "const ok = b => { R.decoding = false; if (!R.wantDecode) return; R.buf = b; if (trkWant === key && ctx && (!trk || trk.key !== key) && lastMode !== 'pause') { trkPend = null; const sw = !!(trk && SWAP[trk.key] === key); trkGo(key, sw ? 0.5 : 1.4, sw ? 0.5 : trk ? 1.2 : 0.6, false, carryOff(key)); } }")
rep("lvl = R.k * (key === 'menu' ? TRK_LVL.menu :", "lvl = R.k * (key === 'menu' || key === 'spook' ? TRK_LVL.menu :")
rep("        const key = mode === 'menu' ? 'menu' : mode === 'play' ? stageTrk() : mode === 'win' || mode === 'lost' ? mode : null; trkWant = key; trkPend = null;",
    "        const key = mode === 'menu' ? 'menu' : mode === 'shop' ? 'spook' : mode === 'play' ? stageTrk() : mode === 'win' || mode === 'lost' ? mode : null; trkWant = key; trkPend = null;")
rep("        if (key && TRK[key].buf) on = trkGo(key, mode === 'menu' ? 0.9 : 0.4, mode === 'menu' && lastMode !== 'none' ? 0.5 : 0.03, mode === 'play' && lastMode !== 'pause');",
    "        const sw = !!(key && trk && SWAP[trk.key] === key); // (lobby to locker or back: a short cross-fade at the same bar)\n        if (key && TRK[key].buf) on = trkGo(key, sw ? 0.45 : mode === 'menu' ? 0.9 : 0.4, sw ? 0.45 : mode === 'menu' && lastMode !== 'none' ? 0.5 : 0.03, mode === 'play' && lastMode !== 'pause', carryOff(key));")
rep("        if (mode === 'menu') { trkDrop('win'); trkDrop('lost'); }", "        if (mode === 'menu') { trkDrop('win'); trkDrop('lost'); trkDecode('spook'); } // (the locker's cut gets ready while you are in the lobby)")
rep("        if (key && !TRK[key].fail && (mode === 'menu' || mode === 'play')) { trkPend = mode;", "        if (key && !TRK[key].fail && (mode === 'menu' || mode === 'shop' || mode === 'play')) { trkPend = mode;")
rep("      else if (mode === 'menu') { if (lastMode !== 'menu') { arr = 'menu'; seqS = 0; seqT = t + 0.1; } musOn = true; vol(MUS_MENU, 0.4); }",
    "      else if (mode === 'menu' || mode === 'shop') { if (lastMode !== 'menu' && lastMode !== 'shop') { arr = 'menu'; seqS = 0; seqT = t + 0.1; } musOn = true; vol(MUS_MENU, 0.4); }")
rep("  function trkFallback(key) { if (trkPend && trkWant === key && ctx) {", "  function trkFallback(key) { if (key === 'spook' && trkPend === 'shop' && ctx) { trkPend = null; return; } if (trkPend && trkWant === key && ctx) {") # (no spooky cut to be had: the lobby song simply carries on)

# ---- the lobby: your dabs open the shop ----
rep('<div class="plate stat drops" title="Dabs"><b id="statDrops">', '<button class="plate stat drops" id="dabsBtn" type="button" title="Dabs. Open the Paint Shop" aria-haspopup="dialog"><b id="statDrops">')
rep('<path d="M10 5.2c.9 0 1.3 1.1 2 1.5 1 .5 2.2-.3 2.6.7.4 1-.9 1.6-.9 2.6s1.2 1.6.7 2.5c-.5.9-1.6.2-2.5.6-.8.4-1 1.7-1.9 1.7s-1.1-1.3-2-1.7c-.9-.4-2 .3-2.5-.6s.7-1.5.7-2.5-1.3-1.6-.9-2.6c.4-1 1.6-.2 2.6-.7.7-.4 1.1-1.5 2.1-1.5z"/></svg>0</b><span>Dabs</span></div>',
    '<path d="M10 5.2c.9 0 1.3 1.1 2 1.5 1 .5 2.2-.3 2.6.7.4 1-.9 1.6-.9 2.6s1.2 1.6.7 2.5c-.5.9-1.6.2-2.5.6-.8.4-1 1.7-1.9 1.7s-1.1-1.3-2-1.7c-.9-.4-2 .3-2.5-.6s.7-1.5.7-2.5-1.3-1.6-.9-2.6c.4-1 1.6-.2 2.6-.7.7-.4 1.1-1.5 2.1-1.5z"/></svg>0</b><span>Dabs <i class="shoptag">Shop</i></span></button>')

# ---- the locker: what you own; its dabs badge opens the shop ----
rep('<div class="lktop"><h2 class="ctitle" id="lookTitle">Locker</h2><span class="lkbal" id="lkBal" aria-label="Dabs">', '<div class="lktop"><h2 class="ctitle" id="lookTitle">My locker</h2><button class="lkbal" id="lkBal" type="button" aria-label="Dabs. Open the Paint Shop" aria-haspopup="dialog">')
rep('<b id="lkBalN">0</b></span><button class="lnbtn" id="lookNameBtn"', '<b id="lkBalN">0</b><small>Shop</small></button><button class="lnbtn" id="lookNameBtn"')
rep("    b.classList.toggle('fresh', WEAR.some(w => w.cat === c && owns(w.id) && fresh.has(w.id)));", "    b.classList.toggle('fresh', WEAR.some(w => w.cat === c && bought(w.id) && fresh.has(w.id)));")
rep("  rail.innerHTML = WEAR.filter(w => w.cat === lookCat).map(w => { const found = owns(w.id), own = found && bought(w.id), sale = found && !own, fr = own && fresh.has(w.id), broke = sale && (store.drops || 0) < PRICE(w);",
    "  const mine = WEAR.filter(w => w.cat === lookCat && bought(w.id)), forSale = WEAR.filter(w => w.cat === lookCat && !bought(w.id)).length;\n  rail.innerHTML = mine.map(w => { const found = owns(w.id), own = found && bought(w.id), sale = found && !own, fr = own && fresh.has(w.id), broke = sale && (store.drops || 0) < PRICE(w);")
rep("<svg viewBox=\"0 0 40 40\" aria-hidden=\"true\">' + WEAR_ICON[w.id] + '</svg><span class=\"ltn\">' + w.name + '</span>' + (found ? '' : LOCK_ICON) + '</button>'; }).join('');",
    "<svg viewBox=\"0 0 40 40\" aria-hidden=\"true\">' + WEAR_ICON[w.id] + '</svg><span class=\"ltn\">' + w.name + '</span>' + (found ? '' : LOCK_ICON) + '</button>'; }).join('')\n    + (forSale ? '<button class=\"ltile shopgo\" type=\"button\" data-shop=\"1\" aria-label=\"' + (mine.length ? '' : 'Nothing here yet. ') + 'Paint Shop, ' + forSale + ' for sale\">' + SHOP_ICON + '<span class=\"ltn\">' + (mine.length ? 'Shop' : 'Paint Shop') + '</span><span class=\"ltag n\">' + forSale + '</span></button>' : '');")
rep("const wearPick = e => { const b = e.target.closest('.ltile'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w); if (!w) return;",
    "const wearPick = e => { const b = e.target.closest('.ltile'); if (!b) return; AU.init(); if (b.dataset.shop) { AU.ui(); openShop('look'); return; } const w = WEAR.find(x => x.id === b.dataset.w); if (!w) return;")
# the locker plays the spooky cut; the lobby song comes back on the way out
rep("  lookOpen = true; menu.classList.add('looking'); renderSwatches(); renderLook(); lookEl.hidden = false;", "  lookOpen = true; menu.classList.add('looking'); renderSwatches(); renderLook(); lookEl.hidden = false; AU.music('shop');")
rep("function closeLook() { if (!lookOpen) return; lookOpen = false;", "function closeLook() { if (!lookOpen) return; if (shopOpen) closeShop(true); lookOpen = false; AU.music('menu');")
rep("$('lookBtn').addEventListener('click', () => { AU.init(); AU.ui(); openLook(); });", "$('lookBtn').addEventListener('click', () => { AU.init(); AU.ui(); openLook(); });\n$('lkBal').addEventListener('click', () => { AU.init(); AU.ui(); openShop('look'); });\n$('dabsBtn').addEventListener('click', () => { AU.init(); AU.ui(); openShop('lobby'); });")
# a new item found on a canvas: it is in the shop now
rep("$('niTry').textContent = bought(w.id) ? 'Try it on' : 'See it in the locker';", "$('niTry').textContent = bought(w.id) ? 'Try it on' : 'See it in the shop';")
rep("  irisClose(() => { end.hidden = true; showMenu(); camSnap = true; irisOpen(); openLook(); const t = w && $('lookRail').querySelector('[data-w=\"' + w.id + '\"]'); if (t) {",
    "  irisClose(() => { end.hidden = true; showMenu(); camSnap = true; irisOpen(); if (w && !bought(w.id)) { openShop('lobby'); return; } openLook(); const t = w && $('lookRail').querySelector('[data-w=\"' + w.id + '\"]'); if (t) {")
# nothing else opens over the shop
rep("function openSettings() { if (state !== 'menu' || lookOpen) return;", "function openSettings() { if (state !== 'menu' || lookOpen || shopOpen) return;")
rep("$('homePlay').addEventListener('click', () => { AU.init(); if (state !== 'menu' || building || lookOpen) return;", "$('homePlay').addEventListener('click', () => { AU.init(); if (state !== 'menu' || building || lookOpen || shopOpen) return;")
rep("  if (lookOpen) closeLook();\n", "  if (shopOpen) closeShop(true); if (lookOpen) closeLook();\n")
rep("  if (lookOpen) { if (e.key === 'Escape') { e.preventDefault(); closeLook(); } return; }", "  if (shopOpen) { if (e.key === 'Escape' || e.key === 'Backspace') { e.preventDefault(); closeShop(); } return; }\n  if (lookOpen) { if (e.key === 'Escape') { e.preventDefault(); closeLook(); } return; }")

# ---- the shop ----
rep('  <section class="sheet lookp" id="look" hidden role="dialog" aria-labelledby="lookTitle">', '''  <section class="shop" id="shop" hidden role="dialog" aria-labelledby="shopTitle">
    <div class="shtop"><h2 class="ctitle" id="shopTitle">Paint Shop</h2><span class="lkbal shbal" id="shBal" aria-label="Dabs"></span><button class="btn sm shback" id="shopBack" type="button">Back</button></div>
    <p class="shsub">Items found on the canvases go on sale here. Matches pay in dabs.</p>
    <div class="shgrid" id="shopGrid" role="list"></div>
    <p class="shnote" id="shopNote" aria-live="polite"></p>
  </section>
  <section class="sheet lookp" id="look" hidden role="dialog" aria-labelledby="lookTitle">''')
rep("function openLook() {", r'''// ---------- the Paint Shop: everything not yet bought, found or still out on a canvas; no blob here, just the goods ----------
const SHOP_ICON = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M9 15h22l-1.6 16.5a2 2 0 0 1-2 1.8H12.6a2 2 0 0 1-2-1.8z" fill="#F2C14E" stroke="#171320" stroke-width="2.4" stroke-linejoin="round"/><path d="M14.5 15v-2.5a5.5 5.5 0 0 1 11 0V15" fill="none" stroke="#171320" stroke-width="2.4" stroke-linecap="round"/><path d="M15 21.5c1.4 0 1.4 1.6 2.8 1.6s1.4-1.6 2.8-1.6 1.4 1.6 2.8 1.6 1.4-1.6 2.8-1.6" fill="none" stroke="#171320" stroke-width="2" stroke-linecap="round"/></svg>';
let shopOpen = false, shopFrom = 'lobby', shopNoteT = 0;
const SHOP_CATS = [['head', 'Headgear'], ['face', 'Facial'], ['cloth', 'Clothing']];
function shopNote(t, bad) { const el = $('shopNote'); el.textContent = t; el.classList.toggle('bad', !!bad); restartCls(el, 'on'); clearTimeout(shopNoteT); shopNoteT = setTimeout(() => el.classList.remove('on'), 3200); }
function renderShop() {
  const n = store.drops || 0; $('shBal').innerHTML = DROP_SVG + '<b>' + n + '</b>';
  let h = '', any = false;
  for (const [c, label] of SHOP_CATS) { const items = WEAR.filter(w => w.cat === c && !bought(w.id)); if (!items.length) continue; any = true;
    h += '<p class="shcat">' + label + '</p>' + items.map(w => { const found = owns(w.id), broke = found && n < PRICE(w), where = WEAR_WHERE[w.stage];
      return '<button class="shitem' + (found ? (broke ? ' broke' : '') : ' locked') + '" type="button" role="listitem" data-w="' + w.id + '" aria-label="' + escAttr(w.name + ', ' + PRICE(w) + ' dabs' + (found ? (broke ? ', ' + (PRICE(w) - n) + ' more needed' : '') : ', locked. Find it on ' + where)) + '">' + (found ? '' : LOCK_ICON)
        + '<svg class="ic" viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg><b class="shn">' + w.name + '</b><span class="shw">' + (found ? (broke ? 'Need ' + (PRICE(w) - n) + ' more' : 'Found on ' + where) : 'Find it on ' + where) + '</span><span class="shp">' + DROP_SVG + PRICE(w) + '</span></button>'; }).join(''); }
  $('shopGrid').innerHTML = any ? h : '<p class="shempty">' + SHOP_ICON + 'Nothing left to buy.<br>Everything is in your locker.</p>';
}
function openShop(from) {
  if (state !== 'menu' || building || shopOpen) return; shopOpen = true; shopFrom = from || (lookOpen ? 'look' : 'lobby');
  renderShop(); $('shop').hidden = false; menu.classList.add('shopping'); AU.music('shop'); setTimeout(() => $('shopBack').focus({ preventScroll: true }), 30);
}
// back to where you came from: the locker (its song carries on) or the lobby (the lobby song comes back at the same bar)
function closeShop(quiet) {
  if (!shopOpen) return; shopOpen = false; $('shop').hidden = true; menu.classList.remove('shopping'); $('shopNote').classList.remove('on');
  if (quiet) return;
  if (lookOpen) { renderLook(); railEdge(); setTimeout(() => $('lkBal').focus({ preventScroll: true }), 30); }
  else { AU.music('menu'); renderLobbyUI(); setTimeout(() => $('dabsBtn').focus({ preventScroll: true }), 30); }
}
$('shopBack').addEventListener('click', () => { AU.init(); AU.ui(); closeShop(); });
$('shopGrid').addEventListener('click', e => { const b = e.target.closest('.shitem'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w); if (!w) return;
  if (!owns(w.id)) { AU.nope(); kick(b, 'nope'); shopNote('Find the ' + w.name.toLowerCase() + ' on ' + WEAR_WHERE[w.stage] + ' first.'); return; }
  if (!buyItem(w.id)) { AU.nope(); kick(b, 'nope'); shopNote('Needs ' + (PRICE(w) - (store.drops || 0)) + ' more dabs. Matches pay in dabs.', true); return; }
  AU.power(); b.classList.add('got'); b.querySelector('.shw').textContent = 'In your locker'; kick(b, 'tpop'); showDrops(); $('shBal').innerHTML = DROP_SVG + '<b>' + (store.drops || 0) + '</b>'; kick($('shBal'), 'bump'); $('lookBtn').classList.add('hot');
  shopNote('Bought the ' + w.name.toLowerCase() + '! It is in your locker.'); setTimeout(() => { if (shopOpen) renderShop(); }, 1400); });
function openLook() {''')

css = '''
/* the locker is yours; the Paint Shop sells the rest */
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
.shop::before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 60% 50% at 50% 30%,rgba(255,255,255,.08),rgba(255,255,255,0) 70%);pointer-events:none}
.shtop{position:relative;display:flex;align-items:center;gap:12px;min-height:44px}
.shtop .ctitle{margin:0;font-size:26px;color:var(--cream);text-align:left;text-shadow:.05em .06em 0 var(--ink)}
.shbal{margin-left:auto;margin-right:0;cursor:default}
.shback{min-height:40px;padding:0 16px;font-size:15px}
.shsub{position:relative;margin:0;font:800 12px/1.3 var(--font-ui);color:#B8B0C8}
.shgrid{position:relative;display:grid;grid-template-columns:repeat(auto-fill,minmax(132px,1fr));gap:10px;align-content:start;overflow:auto;overscroll-behavior:contain;padding:6px 2px 14px;margin:0 -2px;min-height:0;flex:1;scrollbar-width:none;-webkit-mask:linear-gradient(#000 calc(100% - 18px),transparent);mask:linear-gradient(#000 calc(100% - 18px),transparent)}
.shgrid::-webkit-scrollbar{display:none}
.shcat{grid-column:1/-1;margin:6px 0 -2px;font:800 11px/1 var(--font-ui);letter-spacing:.16em;text-transform:uppercase;color:#B8B0C8}
.shitem{appearance:none;position:relative;display:grid;justify-items:center;gap:6px;padding:14px 10px 12px;background:#fff url(art/m_paperbg.webp) center/300px;border:2.5px solid var(--black);border-radius:8px;box-shadow:4px 4px 0 rgba(255,255,255,.18);color:var(--black);cursor:pointer;text-align:center;transition:transform .15s}
.shitem:active{transform:translateY(1px)}
.shitem:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.shitem svg.ic{width:56px;height:56px;display:block}
.shn{font:900 14px/1.1 var(--font-head);text-transform:uppercase}
.shw{font:800 10.5px/1.25 var(--font-ui);color:var(--muted);min-height:2.5em;display:grid;align-items:center}
.shp{display:inline-flex;align-items:center;gap:4px;padding:6px 11px 6px 8px;border-radius:99px;background:var(--ink);color:#fff;font:900 13px/1 var(--font-head)}
.shp .dropi{width:15px;height:15px}
.shitem.broke .shp{background:#8E8698}
.shitem.locked{border-style:dashed;background:var(--paper-2)}
.shitem.locked svg.ic{filter:grayscale(1) brightness(.62);opacity:.42}
.shitem.locked .shn{opacity:.7}
.shitem.locked .shp{background:#8E8698}
.shitem .lk{position:absolute;right:8px;top:8px;width:19px;height:19px;display:grid;place-items:center;border-radius:6px;background:var(--black);color:var(--cream)}
.shitem .lk svg{width:12px;height:12px}
.shitem.got{border-color:var(--gold);box-shadow:4px 4px 0 rgba(255,255,255,.18),0 0 0 3px var(--gold)}
.shitem.got .shw{color:var(--gold-lo,#8A5A12)}
.shitem.got .shp{background:var(--gold);color:var(--black)}
.shitem.nope{animation:nope .35s}
.shitem.tpop{animation:tilepop .42s cubic-bezier(.2,1.6,.4,1)}
.shempty{grid-column:1/-1;display:grid;justify-items:center;gap:10px;padding:28px 16px;font:800 15px/1.4 var(--font-ui);color:#B8B0C8;text-align:center}
.shempty svg{width:56px;height:56px}
.shnote{position:absolute;left:50%;bottom:max(18px,env(safe-area-inset-bottom));transform:translate(-50%,8px);max-width:min(88vw,420px);margin:0;padding:9px 14px;border-radius:6px;background:var(--paper);color:var(--black);border:2px solid var(--black);box-shadow:3px 3px 0 var(--black);font:800 13px/1.3 var(--font-ui);text-align:center;opacity:0;pointer-events:none;transition:opacity .2s,transform .2s}
.shnote.on{opacity:1;transform:translate(-50%,0)}
.shnote.bad{background:var(--ink);color:#fff}
.menu.shopping .mhome{visibility:hidden}
@media (max-height:520px) and (min-aspect-ratio:1/1){.shop{gap:6px}.shtop{min-height:38px}.shtop .ctitle{font-size:22px}.shsub{display:none}.shgrid{grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px}.shitem{padding:10px 8px 9px;gap:4px}.shitem svg.ic{width:44px;height:44px}.shw{min-height:0}}
@media (prefers-reduced-motion:reduce){.shop,.shitem.tpop,.shitem.nope{animation:none}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
