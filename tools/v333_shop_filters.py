"""v333: the Paint Shop gets filters, and the locker page's wall takes your paint's colour.

- Filters: a row of chips under the Paint Shop's heading: All, Spooky SZN, Headgear, Facial, Clothing (and Eyes while there are eyes to
  buy), each with how many things it holds; a dot on one with a new find in it. All is the shop as it was. Spooky SZN is the season's
  banner and its finds. A kind (Headgear, say) is all of that kind, the season's first, under their own small headings. The row stays at
  the top of the panel as you scroll down (on a paper strip once it's over the cards), and a pick keeps it where it is. The page opens
  on All; the lesson's shop has no row (its tips point at the flower and the fangs). In the locker, an empty kind's "The Paint Shop has
  N" opens the shop on that kind.
- The wall: the lime wall becomes a light tint of your paint (a table, one per paint), with the same chevrons and axolotls drawn over it
  in white (art/lk_wall.webp, made from the Strokes wall). The window in the wall draws its part of the wall with the same layer and
  the same sums, so the two still meet without a seam. Picking a new paint fades the wall over to its tint in about half a second, the
  page and the window in step. The Strokes page and the Friends page keep the lime."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

# the chips' pictures (24 x 24, drawn in the text colour)
ICONS = {
    'all': '<rect x="4" y="4" width="7" height="7" rx="2" fill="currentColor"/><rect x="13" y="4" width="7" height="7" rx="2" fill="currentColor"/><rect x="4" y="13" width="7" height="7" rx="2" fill="currentColor"/><rect x="13" y="13" width="7" height="7" rx="2" fill="currentColor"/>',
    'season': '<path d="M12 8.2c-1.3-.9-3.4-1-4.9-.1C5 9.3 4.2 11.6 4.2 13.6c0 3.3 2.2 5.9 5 5.9.9 0 1.9-.3 2.8-.8.9.5 1.9.8 2.8.8 2.8 0 5-2.6 5-5.9 0-2-.8-4.3-2.9-5.5-1.5-.9-3.6-.8-4.9.1z" fill="#FF8A2A"/><path d="M12 8.8v9.6M12 8.3c0-1.8.6-3.1 2-3.9"/>',
    'head': '<path d="M3.5 18.2h17"/><path d="M7.2 18.2V8.4c0-1.1.9-2 2-2h5.6c1.1 0 2 .9 2 2v9.8"/><path d="M7.2 14.6h9.6"/>',
    'face': '<circle cx="7.3" cy="13.4" r="3.7"/><circle cx="16.7" cy="13.4" r="3.7"/><path d="M11 12.8c.7-.6 1.3-.6 2 0M3.7 12.4 2.6 9.8M20.3 12.4l1.1-2.6"/>',
    'cloth': '<path d="M10.2 12 4.2 8.3v7.4zM13.8 12l6-3.7v7.4z"/><rect x="10.2" y="10.2" width="3.6" height="3.6" rx="1" fill="currentColor"/>',
    'eyes': '<path d="M2.8 12.2s3.4-5.4 9.2-5.4 9.2 5.4 9.2 5.4-3.4 5.4-9.2 5.4-9.2-5.4-9.2-5.4z"/><circle cx="12" cy="12.2" r="2.7" fill="currentColor"/>',
}
SVG = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">'

CSS = r'''
/* ---- (v333) the Paint Shop's filters: a row of paper chips under its heading (ink when picked), held at the top of the panel as the
   cards scroll under it; and the locker page's wall in your paint (a tint of it, the Strokes wall's pattern over it in white) */
#mLocker.sgp .lkchips{position:sticky;top:0;z-index:4;margin:-10px -16px 0;padding:6px 0 3px;border-radius:22px 22px 0 0}
#mLocker.sgp .lkchipr{position:relative;display:flex;gap:7px;padding:6px 16px 5px;overflow-x:auto;overflow-y:hidden;scrollbar-width:none;overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch}
#mLocker.sgp .lkchipr::-webkit-scrollbar{display:none}
#mLocker.sgp .lkchipr.mr{-webkit-mask-image:linear-gradient(90deg,#000 calc(100% - 44px),transparent);mask-image:linear-gradient(90deg,#000 calc(100% - 44px),transparent)}
#mLocker.sgp .lkchipr.ml{-webkit-mask-image:linear-gradient(90deg,transparent,#000 44px);mask-image:linear-gradient(90deg,transparent,#000 44px)}
#mLocker.sgp .lkchipr.ml.mr{-webkit-mask-image:linear-gradient(90deg,transparent,#000 44px,#000 calc(100% - 44px),transparent);mask-image:linear-gradient(90deg,transparent,#000 44px,#000 calc(100% - 44px),transparent)}
#mLocker.sgp .lkchips.stuck{background:#F6F1E8;box-shadow:0 2px 0 rgba(23,19,32,.08),0 9px 12px -8px rgba(23,19,32,.28)}
#mLocker.sgp .lkchip{appearance:none;position:relative;flex:none;display:inline-flex;align-items:center;gap:5px;height:32px;margin:0;padding:0 11px 0 9px;border:0;border-radius:999px;background:#fff;color:var(--black);font:400 13px/1 var(--font-display);letter-spacing:.01em;white-space:nowrap;box-shadow:0 0 0 2px var(--ink0),2px 3px 0 rgba(23,19,32,.2);cursor:pointer;-webkit-tap-highlight-color:transparent;transition:transform .12s cubic-bezier(.2,1.3,.4,1)}
#mLocker.sgp .lkchip svg{flex:none;width:17px;height:17px}
#mLocker.sgp .lkchip span{padding-top:1px}
#mLocker.sgp .lkchip i{font-style:normal;padding:3px 5px 2px;border-radius:999px;background:rgba(23,19,32,.1);font-size:11px;font-variant-numeric:tabular-nums}
#mLocker.sgp .lkchip[aria-pressed="true"]{background:var(--ink0);color:#fff;transform:translateY(-1px)}
#mLocker.sgp .lkchip[aria-pressed="true"] svg{color:var(--sel)}
#mLocker.sgp .lkchip[aria-pressed="true"] i{background:rgba(255,255,255,.18)}
#mLocker.sgp .lkchip:active{transform:translate(1px,2px);box-shadow:0 0 0 2px var(--ink0),1px 1px 0 rgba(23,19,32,.2)}
#mLocker.sgp .lkchip.fresh::after{content:"";position:absolute;right:-3px;top:-4px;width:10px;height:10px;border-radius:50%;background:#FF2D55;box-shadow:0 0 0 2px var(--ink0)}
#mLocker.sgp.lkchipped .sgscroll{padding-top:0;-webkit-mask:linear-gradient(#000,#000 calc(100% - 18px),transparent);mask:linear-gradient(#000,#000 calc(100% - 18px),transparent)}
#mLocker.sgp.lkchipped #lkPaneShop{padding-top:22px}
@media (max-aspect-ratio:1/1) and (max-height:700px){#mLocker.sgp.lkchipped #lkPaneShop{padding-top:20px}}
#mLocker.sgp .lksec svg{flex:none;width:15px;height:15px;margin:-3px -2px -3px 0;color:#171320}
@media (max-width:359px){#mLocker.sgp .lkchip{height:30px;padding:0 9px 0 8px;font-size:12px}#mLocker.sgp .lkchip svg{width:15px;height:15px}}
#mLocker.sgp .sgbg{background:var(--wall,#CBE45A)}
#mLocker.sgp .sgbg::before,#mLocker.sgp .lkwx::before{content:"";position:absolute;inset:0;background:url(art/lk_wall.webp) 0 0/560px 560px repeat;opacity:var(--wk,.34)}
#mLocker.sgp .lkwx{position:absolute;inset:0;background:var(--wall1,#CBE45A);opacity:0;pointer-events:none}
#mLocker.sgp .lkwx::before{opacity:var(--wk1,.34)}
#mLocker.sgp .lkwx.go{will-change:opacity}
#mLocker.sgp .sgfoot .sgline{text-shadow:0 0 3px var(--wallhi,#F4FAD8),0 0 7px var(--wallhi2,rgba(244,250,216,.85))}
'''

WALL_JS = r'''
// (v333) the locker page's wall in your paint: a light tint of it (LK_WALL), with the Strokes wall's chevrons and axolotls over it in
// white (art/lk_wall.webp: its alpha is how much lighter than the lime each spot of that wall is, over LK_WALL_AS, so it's drawn at
// LK_WALL_AS times the strength). The strength is evened out so the pattern stands out from each tint as much as from the lime. The
// window draws its part of the wall with the same layer and the same sums; a new paint fades the wall over, the page and the window in step
const LK_WALL = { red: 0xFFAAA4, grey: 0xC4B6D9, gold: 0xFFE19E, green: 0x8FEB9C, purple: 0xCCABFE, pink: 0xFFAFCF }, LK_WALL_AS = 0.34;
const LKW = { w: null, w1: null, t0: 0, mix: 0 };
function lkWallOf(id) {
  const hx = LK_WALL[id] || 0xCBE45A, r = (hx >> 16) & 255, g = (hx >> 8) & 255, b = hx & 255, y = 0.2126 * r + 0.7152 * g + 0.0722 * b;
  const hi = c => Math.round(c + (255 - c) * 0.8), gr = c => Math.round(c * 0.55 + 90), H = hi(r) + ',' + hi(g) + ',' + hi(b);
  return { id, hx, css: '#' + hx.toString(16).padStart(6, '0'), k: Math.min(1, 42.3 / Math.max(1, 255 - y)) * LK_WALL_AS, rgb: [r / 255, g / 255, b / 255], hi: 'rgb(' + H + ')', hi2: 'rgba(' + H + ',.85)', gr: (gr(r) << 16) | (gr(g) << 8) | gr(b) };
}
// straight to it (the page opening, a fade done)
function lkWallSet(id) {
  const w = lkWallOf(id), pg = $('mLocker'), x = $('lkWx'); LKW.w = w; LKW.w1 = null; LKW.mix = 0;
  pg.style.setProperty('--wall', w.css); pg.style.setProperty('--wk', w.k.toFixed(4)); pg.style.setProperty('--wallhi', w.hi); pg.style.setProperty('--wallhi2', w.hi2);
  x.style.opacity = '0'; x.classList.remove('go');
}
// fading over to a new paint's (only while the window draws, to keep the two in step; else straight to it)
function lkWallTo(id) {
  if (LKW.w1) lkWallSet(LKW.w1.id);
  if (!LKW.w || !SGD.on || reduceMotion) return lkWallSet(id);
  const w = lkWallOf(id), x = $('lkWx'), pg = $('mLocker'); if (w.hx === LKW.w.hx) return lkWallSet(id);
  LKW.w1 = w; LKW.t0 = performance.now(); LKW.mix = 0;
  x.style.setProperty('--wall1', w.css); x.style.setProperty('--wk1', w.k.toFixed(4)); x.style.opacity = '0'; x.classList.add('go');
  pg.style.setProperty('--wallhi', w.hi); pg.style.setProperty('--wallhi2', w.hi2);
}
function lkWallTick() { if (!LKW.w1) return; const u = Math.min(1, (performance.now() - LKW.t0) / 560); if (u >= 1) return lkWallSet(LKW.w1.id); LKW.mix = u * u * (3 - 2 * u); $('lkWx').style.opacity = LKW.mix.toFixed(4); }
// the window's part of it (the Strokes page: its own lime picture)
function lkWallU() {
  const U = SGD.bgU, w = lkOn() && LKW.w; U.uMode.value = w ? 1 : 0; if (!w) return; const w1 = LKW.w1 || w;
  U.uW0.value.fromArray(w.rgb); U.uW1.value.fromArray(w1.rgb); U.uK0.value = w.k; U.uK1.value = w1.k; U.uMix.value = LKW.w1 ? LKW.mix : 0;
}
'''

FILT_JS = r'''
// ---------- (v333) the Paint Shop's filters: All, the season, and each kind (the season's own of that kind first, under a heading) ----------
const LK_FILT = [['all', 'All'], ['season', 'Spooky SZN'], ['head', 'Headgear'], ['face', 'Facial'], ['cloth', 'Clothing'], ['eyes', 'Eyes']];
const LK_FI = ''' + repr(ICONS) + r''', LK_FSVG = ''' + repr(SVG) + r''';
const lkInF = (w, f) => f === 'all' || (f === 'season' ? !!w.season : w.cat === f);
const lkFound = w => !bought(w.id) && owns(w.id) && needFind(w); // (a find that's for sale now: its tag says New)
// the row: shown with more than one way to look (not in the lesson's shop, where the tips point at the flower and the fangs)
function lkChipsHtml(listed, f) {
  return '<div class="lkchips"><div class="lkchipr" role="group" aria-label="Show in the shop">' + LK_FILT.filter(([k]) => k === 'all' || listed.some(w => lkInF(w, k))).map(([k, n]) => {
    const c = listed.filter(w => lkInF(w, k)), on = k === f, fresh = !on && k !== 'all' && c.some(lkFound);
    return '<button class="lkchip' + (fresh ? ' fresh' : '') + '" type="button" data-f="' + k + '" aria-pressed="' + on + '" aria-label="' + n + (k === 'all' ? '' : ', ' + c.length) + (fresh ? ', something new' : '') + '">' + LK_FSVG + LK_FI[k] + '</svg><span>' + n + '</span>' + (k === 'all' ? '' : '<i>' + c.length + '</i>') + '</button>'; }).join('') + '</div></div>';
}
// the shop: the season's finds first, under their banner, then everything else for sale (what this visit bought stays, as yours);
// or just the season's, or one kind
function lkShopHtml() {
  const grid = l => '<div class="sggrid lkgrid' + (LKR.anim ? ' in' : '') + '">' + l.map(w => lkCard(w, 'shop')).join('') + '</div>', by = (a, b) => PRICE(a) - PRICE(b), cnt = ITEMS.filter(lkForSale).length;
  const listed = ITEMS.filter(w => !bought(w.id) || LKR.got.has(w.id)), kinds = LK_FILT.filter(([k]) => k !== 'all' && listed.some(w => lkInF(w, k))).length, chips = tutPh() !== 'shop' && kinds > 1;
  const f = chips && listed.some(w => lkInF(w, LKR.filt)) ? LKR.filt : 'all';
  let h = '<div class="lkhd"><h4 class="lkh">Paint Shop</h4>' + (cnt ? '<span class="lkcnt">' + cnt + ' in stock</span>' : '') + '</div>';
  if (chips) h += lkChipsHtml(listed, f);
  if (f === 'all' || f === 'season') {
    const sz = listed.filter(w => w.season).sort(by);
    if (sz.length) { const all = ITEMS.filter(w => w.season), got = all.filter(w => bought(w.id) || owns(w.id)).length;
      h += '<div class="lkszn" role="heading" aria-level="4"><span class="sbart" style="--sbbg:url(art/shop_hw_bg.webp)"></span><span class="lkszt"><i>Season One</i><b>Spooky SZN</b><small><u style="--p:' + (all.length ? got / all.length : 0).toFixed(3) + '"></u>' + got + ' of ' + all.length + ' found</small></span><img class="lkpump" src="art/shop_hw_pump.webp" alt="" draggable="false"></div>' + grid(sz); }
    if (f === 'all') for (const c of ['head', 'face', 'cloth', 'eyes']) { const l = listed.filter(w => !w.season && w.cat === c).sort(by); if (l.length) h += '<p class="lksec">' + LK_CAT[c] + '</p>' + grid(l); }
  } else {
    const sz = listed.filter(w => w.season && w.cat === f).sort(by), yr = listed.filter(w => !w.season && w.cat === f).sort(by);
    if (sz.length) h += '<p class="lksec">' + LK_FSVG + LK_FI.season + '</svg>Spooky SZN</p>' + grid(sz);
    if (yr.length) h += (sz.length ? '<p class="lksec">All year</p>' : '') + grid(yr);
  }
  if (!listed.length) h += '<p class="lkempty">' + SHOP_ICON + 'Nothing left to buy.<br>Everything is in your locker.</p>';
  return h;
}
// a pick: the list under it changes and the row stays where it is (at the top of the panel once it's held there)
function lkFilt(f) {
  if (f === LKR.filt) { AU.ui(); buzz(3); const b = $('lkPaneShop').querySelector('.lkchip[data-f="' + f + '"]'); if (b) kick(b, 'tpop'); return; }
  const sc = $('lkScroll'), st = sc.scrollTop; LKR.filt = f; LKR.anim = true; AU.ui(); buzz(4);
  lkPaneRender(); if (st > LKR.stickY) { sc.scrollTop = LKR.stickY; lkStuck(); }
}
// (where the row starts being held at the top: its heading scrolled away; the row is on paper while it's over the cards)
function lkStickMeasure() { const sc = $('lkScroll'), hd = LKR.tab === 'shop' && $('lkPaneShop').querySelector('.lkhd'); LKR.stickY = hd ? Math.round(hd.getBoundingClientRect().bottom - sc.getBoundingClientRect().top + sc.scrollTop) : 0; }
function lkStuck() { const row = LKR.tab === 'shop' && $('lkPaneShop').querySelector('.lkchips'), on = !!row && $('lkScroll').scrollTop >= LKR.stickY - 2; if (row && row.classList.contains('stuck') !== on) row.classList.toggle('stuck', on); }
// after the pane is drawn again: the row as it was (scrolled sideways, the picked chip in view, focus kept), the panel told it has one
function lkChipEdge(row) { const max = row.scrollWidth - row.clientWidth - 4; row.classList.toggle('ml', row.scrollLeft > 4); row.classList.toggle('mr', row.scrollLeft < max); }
function lkChipsAfter(el, cx, fchip) {
  const row = LKR.tab === 'shop' && el.querySelector('.lkchipr'); $('mLocker').classList.toggle('lkchipped', !!row); if (!row) return;
  row.scrollLeft = cx; const b = row.querySelector('[aria-pressed="true"]');
  if (b) { if (b.offsetLeft < row.scrollLeft + 48) row.scrollLeft = Math.max(0, b.offsetLeft - 48); else if (b.offsetLeft + b.offsetWidth > row.scrollLeft + row.clientWidth - 48) row.scrollLeft = b.offsetLeft + b.offsetWidth - row.clientWidth + 48; }
  if (fchip) { const n = row.querySelector('[data-f="' + fchip + '"]'); if (n) n.focus({ preventScroll: true }); }
  lkChipEdge(row); row.addEventListener('scroll', () => lkChipEdge(row), { passive: true }); lkStickMeasure(); lkStuck();
}
$('lkScroll').addEventListener('scroll', () => { if (LKR.tab === 'shop') lkStuck(); }, { passive: true });
addEventListener('resize', () => { if (lkOn()) setTimeout(() => { if (lkOn()) { lkStickMeasure(); lkStuck(); } }, 80); });
'''

def apply(s):
    # ---- the wall: a layer for the fade, the pattern art, the tint
    s = rep(s, '<div class="sgbg" id="lkBg" aria-hidden="true"></div>', '<div class="sgbg" id="lkBg" aria-hidden="true"><i class="lkwx" id="lkWx"></i></div>')
    s = rep(s, '/* (v331) the portraits, and the soft round placeholder', CSS.lstrip('\n') + '/* (v331) the portraits, and the soft round placeholder')
    s = rep(s, "const sgH = () => lkOn()", WALL_JS.lstrip('\n') + "const sgH = () => lkOn()")
    # the window's wall: the lime picture (the Strokes page) or the pattern over your paint's tint, faded as the page fades
    s = rep(s, "  SGD.bgU = { uTex: { value: tex }, uOk: { value: 0 },",
        "  const pat = new THREE.TextureLoader().load('art/lk_wall.webp', () => { SGD.bgU.uPOk.value = 1; }); pat.wrapS = pat.wrapT = THREE.RepeatWrapping; pat.colorSpace = THREE.NoColorSpace; pat.generateMipmaps = true; pat.minFilter = THREE.LinearMipmapLinearFilter; // (v333: the locker's wall)\n"
        "  SGD.bgU = { uPat: { value: pat }, uPOk: { value: 0 }, uMode: { value: 0 }, uW0: { value: new THREE.Vector3(0.8, 0.9, 0.35) }, uW1: { value: new THREE.Vector3(0.8, 0.9, 0.35) }, uK0: { value: 0.34 }, uK1: { value: 0.34 }, uMix: { value: 0 }, uTex: { value: tex }, uOk: { value: 0 },")
    s = rep(s, "uniform sampler2D uTex; uniform float uOk, uTile, uH; uniform vec3 uBase; void main(){ vec2 p = vec2(gl_FragCoord.x, uH - gl_FragCoord.y) / uTile; vec3 c = uOk > 0.5 ? texture2D(uTex, vec2(p.x, 1.0 - p.y)).rgb : uBase; gl_FragColor = vec4(c, 1.0); }",
        "uniform sampler2D uTex, uPat; uniform float uOk, uTile, uH, uMode, uPOk, uK0, uK1, uMix; uniform vec3 uBase, uW0, uW1; void main(){ vec2 p = vec2(gl_FragCoord.x, uH - gl_FragCoord.y) / uTile, q = vec2(p.x, 1.0 - p.y); vec3 c; "
        "if (uMode > 0.5) { float a = uPOk > 0.5 ? texture2D(uPat, q).a : 0.0; c = mix(mix(uW0, vec3(1.0), a * uK0), mix(uW1, vec3(1.0), a * uK1), uMix); } else c = uOk > 0.5 ? texture2D(uTex, q).rgb : uBase; gl_FragColor = vec4(c, 1.0); }")
    s = rep(s, "SGD.bgU.uTile.value = 560 * pr; SGD.bgU.uH.value = H * pr; renderer.render(SGD.bgS, SGD.bgC);", "SGD.bgU.uTile.value = 560 * pr; SGD.bgU.uH.value = H * pr; lkWallU(); renderer.render(SGD.bgS, SGD.bgC);")
    s = rep(s, "hemi.groundColor.setHex(0xC9DB86)", "hemi.groundColor.setHex(lkOn() && LKW.w ? LKW.w.gr : 0xC9DB86)")
    s = rep(s, "function sgDress(dt) {\n", "function sgDress(dt) {\n  lkWallTick(); // (v333)\n")
    s = rep(s, "function sgPause() { if (!SGD.on) return; SGD.on = false; sgHole(false); }", "function sgPause() { if (LKW.w1) lkWallSet(LKW.w1.id); if (!SGD.on) return; SGD.on = false; sgHole(false); }")
    s = rep(s, "LKR.scr.mine = LKR.scr.shop = 0; LKR.anim = true;", "LKR.scr.mine = LKR.scr.shop = 0; LKR.anim = true; LKR.filt = 'all'; lkWallSet(colorId);")
    s = rep(s, "if (id !== colorId) { setColor(id); store.color = colorId; save();", "if (id !== colorId) { setColor(id); lkWallTo(colorId); store.color = colorId; save();")
    # ---- the filters
    s = rep(s, "const LKR = { tab: 'mine',", "const LKR = { filt: 'all', stickY: 0, tab: 'mine',")
    a = s.index('function lkShopHtml() {'); b = s.index('function lkPaneRender() {')
    old = s[a:b]; assert old.count('\n}\n') == 1 and old.endswith('\n}\n'), old[-80:]
    s = s[:a] + FILT_JS.lstrip('\n') + s[b:]
    s = rep(s, "  el.innerHTML = LKR.tab === 'shop' ? lkShopHtml() : lkMineHtml(); LKR.anim = false; nmSet($('lkNameT'), playerName());\n"
        "  sc.scrollTop = top; if (fk) { const f = el.querySelector('[data-k=\"' + fk + '\"]'); if (f) f.focus({ preventScroll: true }); }\n",
        "  const ox = el.querySelector('.lkchipr'), cx = ox ? ox.scrollLeft : 0, fchip = ae && ae.classList && ae.classList.contains('lkchip') && el.contains(ae) ? ae.dataset.f : ''; // (v333)\n"
        "  el.innerHTML = LKR.tab === 'shop' ? lkShopHtml() : lkMineHtml(); LKR.anim = false; nmSet($('lkNameT'), playerName());\n"
        "  sc.scrollTop = top; if (fk) { const f = el.querySelector('[data-k=\"' + fk + '\"]'); if (f) f.focus({ preventScroll: true }); } lkChipsAfter(el, cx, fchip);\n")
    s = rep(s, "$('lkPanel').addEventListener('click', e => { const t = e.target.closest('[data-k], [data-go], #lkNameBtn');", "$('lkPanel').addEventListener('click', e => { const t = e.target.closest('[data-k], [data-go], [data-f], #lkNameBtn');")
    s = rep(s, "if (t.dataset.go) { lkSetTab(t.dataset.go); return; } lkTap(t.dataset.k); });",
        "if (t.dataset.go) { if (t.dataset.f) { LKR.filt = t.dataset.f; LKR.scr.shop = 0; } lkSetTab(t.dataset.go); return; } if (t.dataset.f) { lkFilt(t.dataset.f); return; } lkTap(t.dataset.k); });")
    s = rep(s, "data-go=\"shop\">The Paint Shop has ", "data-go=\"shop\" data-f=\"' + c + '\">The Paint Shop has ")
    # something picked from outside the panel shows in the shop whatever the filter
    s = rep(s, "function lkSelect(id, quiet) {\n  const w = lkItem(id); if (!w) return;\n", "function lkSelect(id, quiet) {\n  const w = lkItem(id); if (!w) return; if (!lkInF(w, LKR.filt)) LKR.filt = 'all'; // (v333)\n")
    return s
