"""v327: My Locker and the Paint Shop become one page, on the Strokes page's base.

- One page with two tabs on the ink band: My Locker and Paint Shop. The lime wall, Back, the taped banner, the window and the band are
  the Strokes page's own (its styles are shared now); the panel is the locker's graph paper, with the locker's headings.
- The window shows you, the game's own character on the Strokes pad, in your paint and wearing what you have on. In the locker a tap
  puts a thing on; in the shop a tap tries it on, and Buy keeps it on. Drag spins you round; the round button turns you to the back.
- Your paint, your eyes (style and colour) and what you own are in the locker; what's for sale (the Spooky SZN finds first, under
  their banner) is in the shop. Fresh things say New. The unlock code moves here too.
- The lessons (buy the flower and the fangs, put the fangs on, the zombie eyes) point at the new page.
The old locker sheet and shop stay in the page but nothing opens them any more."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

ROT = '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="5.2" fill="currentColor"/><path d="M6.6 12.4a10 10 0 0 1 17.6-3.2M25.4 19.6a10 10 0 0 1-17.6 3.2" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><path d="M24.6 4.6l.2 5.4-5.4.4M7.4 27.4l-.2-5.4 5.4-.4" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
BACK = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M12.6 7.4 6.2 13.6l6.4 6.2" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/><path d="M7.4 13.6h11.2a6.4 6.4 0 0 1 0 12.8h-4.4" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round"/></svg>'

HTML = r'''    <div class="mevents sgp sgx lkp" id="mLocker" hidden data-tab="mine">
      <div class="sgbg" id="lkBg" aria-hidden="true"></div><div class="sgink" aria-hidden="true"></div>
      <h2 class="sgvh" id="lkTitle">My Locker and the Paint Shop</h2>
      <button class="sgback" id="lkBack" type="button" aria-label="Back to the lobby">''' + BACK + r'''<span>Back</span></button>
      <button class="sgbadge lkcoin" id="lkCoin" type="button" aria-label="Dabs. Open the Paint Shop"><span class="sgbi" id="lkCoinI" aria-hidden="true"></span><b id="lkCoinN">0</b></button>
      <div class="sgshow" id="lkShow">
        <div class="sgstage" id="lkStage"><span class="sgart" id="lkArt" aria-hidden="true"></span><i class="sgflash" id="lkFlash" aria-hidden="true"></i></div>
        <div class="sgban" id="lkBan"><small id="lkKind">My Locker</small><b id="lkName">You</b><i class="sgflag" aria-hidden="true"></i></div>
        <button class="sgrot" id="lkRot" type="button" aria-label="Turn around" hidden>''' + ROT + r'''</button>
        <div class="sgfoot"><p class="sgline" id="lkLine"></p>
          <div class="sgact"><button class="sgdo" id="lkDo" type="button" hidden>Equip</button><button class="sgib" id="lkOff" type="button" hidden><span>Take off</span></button></div>
          <p class="sgnote" id="lkNote" hidden></p></div>
      </div>
      <section class="sgpanel" id="lkPanel" aria-labelledby="lkPanH"><i class="sghang" aria-hidden="true"></i><h3 class="sgvh" id="lkPanH">My Locker</h3>
        <div class="sgscroll" id="lkScroll">
          <div class="lkpane" id="lkPaneMine" role="tabpanel" aria-labelledby="lkTabMine"></div>
          <div class="lkpane" id="lkPaneShop" role="tabpanel" aria-labelledby="lkTabShop" hidden></div>
          <div class="ucode stucode" id="lkUcode"><button class="ulink" id="lkUnlockLink" type="button">Unlock all items</button><form class="uform" id="lkUnlockForm" hidden><input id="lkUnlockCode" type="text" inputmode="numeric" maxlength="8" autocomplete="off" placeholder="Code" aria-label="Unlock code"><button class="ugo" type="submit">Unlock</button></form></div>
        </div>
      </section>
      <div class="sgtabs" id="lkTabs" role="tablist" aria-label="Your locker and the Paint Shop">
        <button class="sgtab" id="lkTabMine" type="button" role="tab" data-tab="mine" aria-controls="lkPaneMine"><b class="sgtt">My Locker</b><span class="sgtb"><span class="sgti" id="lkTabMineI"></span><span class="lktn" id="lkTabMineN"></span></span></button>
        <button class="sgtab" id="lkTabShop" type="button" role="tab" data-tab="shop" aria-controls="lkPaneShop"><b class="sgtt">Paint Shop</b><span class="sgtb"><span class="sgti" id="lkTabShopI"></span><span class="lktn" id="lkTabShopN"></span></span></button>
      </div>
    </div>
'''

CSS = r'''
/* ---- (v327) My Locker and the Paint Shop as one page on the Strokes page's base (its rules above are shared): the lime wall, the window
   with you in it on the pad, the taped banner, the ink band with a tab for each. The panel is the locker's graph paper: its headings,
   your paint and eyes, and the hang tags with an inked edge and a strip that says what each is to you */
#mLocker.sgp{--kc:#2FD1C0;--panh:min(38vh,318px);--tabw:112px}
#mLocker.sgp[data-tab="shop"]{--kc:#FFC61A}
#mLocker.sgp .sgtab[data-tab="mine"]{--tc:#22C9B8;--tc2:#12AE9E}
#mLocker.sgp .sgtab[data-tab="shop"]{--tc:#FFC61A;--tc2:#F2A900}
#mLocker.sgp .sgtab .sgti .frface{width:38px;height:38px;filter:drop-shadow(1px 2px 0 rgba(23,19,32,.3))}
#mLocker.sgp .sgtab .sgti>svg{width:34px;height:34px;filter:drop-shadow(1px 2px 0 rgba(23,19,32,.3))}
#mLocker.sgp .lktn{display:block;padding:3px 7px 2px;border-radius:999px;background:var(--ink0);color:#fff;font:400 11px/1 var(--font-display);letter-spacing:.01em;white-space:nowrap;font-variant-numeric:tabular-nums}
/* the badge: your dabs (a tap opens the shop) */
#mLocker.sgp .lkcoin .sgbi svg{width:20px;height:20px}
#mLocker.sgp .lkcoin.bump,#mLocker.sgp .sgban.bump,#mLocker.sgp .tpop{animation:tilepop .42s cubic-bezier(.2,1.6,.4,1)}
#mLocker.sgp .sgdo.nope{animation:lknope .35s}
@keyframes lknope{25%{translate:-5px 0}50%{translate:5px 0}75%{translate:-2px 0}}
#mLocker.sgp .sgdo small{display:inline-flex;align-items:center;gap:3px;font-size:12px}
#mLocker.sgp .sgdo .dropi{width:14px;height:14px}
#mLocker.sgp .sgdo:disabled .dropi{opacity:.8}
/* the window: before the character is in, your face on the wall */
#mLocker.sgp .sgart .frface{position:relative;z-index:1;width:min(40%,150px);height:auto;filter:drop-shadow(3px 5px 0 rgba(23,19,32,.18));animation:sgbob 3.2s ease-in-out infinite}
/* the panel: graph paper, hung from the bar */
#mLocker.sgp .sgpanel{background:#F6F1E8 url(art/m_paperbg.webp) center/420px;box-shadow:0 0 0 2.5px var(--ink0),0 7px 0 rgba(23,19,32,.28),0 14px 26px rgba(23,19,32,.18)}
#mLocker.sgp .sgscroll{padding:22px 16px 18px;scrollbar-color:rgba(23,19,32,.35) transparent}
#mLocker.sgp .sgscroll::-webkit-scrollbar-thumb{background:rgba(23,19,32,.3)}
#mLocker.sgp .lkpane{display:grid;grid-template-columns:minmax(0,1fr);gap:10px}
#mLocker.sgp .lkpane[hidden]{display:none}
#mLocker.sgp .lkhd{display:flex;align-items:center;gap:10px;min-width:0;padding:2px 2px 0}
#mLocker.sgp .lkh{margin:0;font:900 24px/.95 var(--font-head);text-transform:uppercase;letter-spacing:0;color:var(--black);white-space:nowrap;transform:skewX(-6deg);text-shadow:.04em .04em 0 #FFF8EA,.08em .08em 0 var(--black)}
#mLocker.sgp .lkname{appearance:none;display:inline-flex;align-items:center;gap:6px;min-width:0;max-width:56%;height:32px;margin:0 0 0 auto;padding:0 10px 0 12px;border:0;border-radius:8px;background:#fff;color:var(--black);font:400 15px/1 var(--font-display);box-shadow:0 0 0 2px var(--ink0),2px 3px 0 rgba(23,19,32,.22);cursor:pointer;-webkit-tap-highlight-color:transparent}
#mLocker.sgp .lkname span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding-top:1px}
#mLocker.sgp .lkname svg{flex:none;width:15px;height:15px}
#mLocker.sgp .lkname:active{transform:translate(1px,2px);box-shadow:0 0 0 2px var(--ink0),1px 1px 0 rgba(23,19,32,.22)}
#mLocker.sgp .lkcnt{margin-left:auto;padding:4px 9px 3px;border-radius:999px;background:var(--ink0);color:#fff;font:400 13px/1 var(--font-display);white-space:nowrap}
#mLocker.sgp .lksec{display:flex;align-items:center;gap:8px;margin:8px 0 0;font:800 11px/1 var(--font-ui);letter-spacing:.16em;text-transform:uppercase;color:#5E566E}
#mLocker.sgp .lksec::after{content:"";flex:1;height:2px;border-radius:2px;background:rgba(23,19,32,.12)}
#mLocker.sgp .lksec i{font-style:normal;padding:2px 6px 1px;border-radius:999px;background:rgba(23,19,32,.1);letter-spacing:.04em}
/* your paint: the six splats */
#mLocker.sgp .lkpaints{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:4px;justify-items:center;padding:2px 0}
#mLocker.sgp .lkpaints .sw{width:100%;max-width:52px;height:48px}
/* your eyes: the styles, then their colours */
#mLocker.sgp .lkeyes{display:grid;grid-template-columns:minmax(0,1fr);gap:10px;padding:2px 2px 4px}
#mLocker.sgp .lkstyles,#mLocker.sgp .lkirises{display:flex;flex-wrap:wrap;align-items:center;gap:10px}
#mLocker.sgp .lkstyles .eyes{width:44px;height:44px;border-radius:9px;box-shadow:0 0 0 2px var(--ink0),2px 3px 0 rgba(23,19,32,.2)}
#mLocker.sgp .lkstyles .eyes svg{width:36px;height:36px}
#mLocker.sgp .lkstyles .eyes[aria-pressed="true"]{box-shadow:0 0 0 3px var(--sel),0 0 0 5.5px var(--ink0);transform:translateY(-2px)}
#mLocker.sgp .lkstyles .eyes .lk{right:-6px;top:-6px}
#mLocker.sgp .lkirises .eyec{width:34px;height:34px}
#mLocker.sgp .lkirises.off{opacity:.32;filter:grayscale(1)}
#mLocker.sgp .lknone{margin:0;padding:2px 2px 4px;font:700 13px/1.35 var(--font-ui);color:#5E566E}
#mLocker.sgp .lkgo{appearance:none;margin:0;padding:0;border:0;background:none;color:var(--black);font:800 13px/1.35 var(--font-ui);text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:3px;cursor:pointer}
#mLocker.sgp .lkempty{display:grid;justify-items:center;gap:8px;margin:0;padding:16px 8px 6px;text-align:center;font:800 14px/1.35 var(--font-ui);color:#5E566E}
#mLocker.sgp .lkempty svg{width:46px;height:46px}
/* the hang tags on paper */
#mLocker.sgp .sggrid{gap:18px 14px}
#mLocker.sgp .sgcard::before{content:"";position:absolute;left:0;right:0;top:10px;bottom:0;border-radius:11px;box-shadow:0 0 0 2px var(--ink0),3px 4px 0 rgba(23,19,32,.16);pointer-events:none}
#mLocker.sgp .sgcard .sghook{box-shadow:inset 0 0 0 2.6px #55555E,0 1px 0 rgba(0,0,0,.25)}
#mLocker.sgp .sgcard .sgca .stimg{inset:-4% -6%;width:112%;height:108%}
#mLocker.sgp .sgcard .sgca svg{inset:6%;width:88%;height:88%}
#mLocker.sgp .sgcard .sgcf{gap:4px;min-height:21px}
#mLocker.sgp .sgcard .sgcf b{font-weight:400}
#mLocker.sgp .sgcard .sgcf .dropi{width:13px;height:13px;flex:none}
#mLocker.sgp .sgcard .sgcf .lk{display:grid;place-items:center;width:12px;height:12px}
#mLocker.sgp .sgcard .sgcf .lk svg{width:11px;height:11px}
#mLocker.sgp .sgcard.sale .sgcf{background:#FFD34D}
#mLocker.sgp .sgcard.broke .sgcf{background:#E9E4D6;color:#6E6680}
#mLocker.sgp .sgcard.lock .sgcb{background-color:#E2DCCF}
#mLocker.sgp .sgcard.lock .sgca{filter:grayscale(.9) opacity(.55)}
#mLocker.sgp .sgcard.lock .sgcf{background:#CFC8DC;color:#3E3850}
#mLocker.sgp .sgcard.on .sgcf{background:var(--ink0);color:var(--sel)}
/* the Spooky SZN finds: a short banner over them */
#mLocker.sgp .lkszn{position:relative;display:block;min-height:86px;margin:4px 0 4px;border-radius:14px;background:#2A1846;box-shadow:0 0 0 2.5px var(--ink0),0 5px 0 var(--ink0);color:#fff;isolation:isolate;overflow:hidden}
#mLocker.sgp .lkszn .sbart{position:absolute;inset:0;z-index:-1;background:#2A1846 var(--sbbg) 72% 36%/cover no-repeat}
#mLocker.sgp .lkszn .sbart::before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(22,10,38,.94) 0%,rgba(22,10,38,.72) 46%,rgba(22,10,38,.12) 82%)}
#mLocker.sgp .lkszt{position:relative;display:flex;flex-direction:column;align-items:flex-start;gap:5px;max-width:calc(100% - 86px);padding:10px 14px 11px;box-sizing:border-box}
#mLocker.sgp .lkszt i{padding:4px 8px 3px;border-radius:5px;background:#FFF1D2;color:#171320;font:800 9.5px/1 var(--font-ui);font-style:normal;letter-spacing:.2em;text-transform:uppercase;transform:rotate(-3deg);box-shadow:2px 2px 0 rgba(0,0,0,.45)}
#mLocker.sgp .lkszt b{font:400 27px/.95 var(--font-display);letter-spacing:.01em;text-transform:uppercase;white-space:nowrap;background:linear-gradient(180deg,#FFFBE0 0%,#FFE266 30%,#FFB429 62%,#FF6A1A 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 2px 0 #171320)}
#mLocker.sgp .lkszt small{display:flex;align-items:center;gap:7px;font:800 11px/1 var(--font-ui);color:#FFD27A;text-shadow:0 1px 0 rgba(0,0,0,.5)}
#mLocker.sgp .lkszt small u{position:relative;display:block;width:62px;height:8px;border-radius:5px;background:rgba(0,0,0,.45);box-shadow:inset 0 0 0 1.5px rgba(255,255,255,.12)}
#mLocker.sgp .lkszt small u::after{content:"";position:absolute;left:2px;top:2px;bottom:2px;width:calc((100% - 4px) * var(--p,0));min-width:4px;border-radius:3px;background:linear-gradient(180deg,#FFD04A,#FF7A1A)}
#mLocker.sgp .lkszn .lkpump{position:absolute;right:-4px;bottom:-12px;width:94px;height:auto;pointer-events:none;filter:drop-shadow(0 4px 0 rgba(23,19,32,.5))}
/* the code that unlocks everything, at the foot of the paper */
#mLocker.sgp .stucode .ulink{color:#6E6680}
#mLocker.sgp .stucode .uform input{border-color:var(--ink0)}
/* a word from the page */
#mLocker .sttoast{position:absolute;left:50%;top:calc(var(--gt) + 64px);z-index:9;transform:translateX(-50%);padding:9px 14px;border-radius:999px;background:#171320;color:#fff;font:800 13px/1 var(--font-ui);box-shadow:0 0 0 2px var(--gold);white-space:nowrap;animation:sttoast 2.2s ease both;pointer-events:none}
#mLocker.sgp .sgfoot .sgline{min-height:1.25em;text-shadow:0 0 3px #F4FAD8,0 0 7px rgba(244,250,216,.85)}
@media (min-aspect-ratio:1/1){
  #mLocker.sgp{--panw:52%}
  #mLocker.sgp .sttoast{left:calc(var(--panw) + (100% - var(--panw)) / 2);top:calc(var(--gt) + 62px);bottom:auto}
  #mLocker.sgp .sgtab .sgti .frface{width:clamp(24px,7.4vh,38px);height:clamp(24px,7.4vh,38px)}
  #mLocker.sgp .sgtab .sgti>svg{width:clamp(22px,7vh,34px);height:clamp(22px,7vh,34px)}
}
@media (max-aspect-ratio:1/1) and (max-height:700px){#mLocker.sgp{--panh:min(31vh,236px)}#mLocker.sgp .sgscroll{padding-top:20px}}
@media (min-aspect-ratio:1/1) and (max-height:430px){#mLocker.sgp .lkh{font-size:20px}#mLocker.sgp .lkszn{min-height:72px}#mLocker.sgp .lkszt b{font-size:22px}#mLocker.sgp .lkszn .lkpump{width:78px}#mLocker.sgp .lktn{font-size:10px}}
@media (max-width:359px){#mLocker.sgp{--tabw:100px}#mLocker.sgp .lkh{font-size:20px}#mLocker.sgp .lkstyles,#mLocker.sgp .lkirises{gap:8px}#mLocker.sgp .lkstyles .eyes{width:38px;height:38px}#mLocker.sgp .lkstyles .eyes svg{width:30px;height:30px}#mLocker.sgp .lkirises .eyec{width:30px;height:30px}#mLocker.sgp .lkszt b{font-size:23px}}
@media (prefers-reduced-motion:reduce){#mLocker.sgp .sgart .frface,#mLocker.sgp .lkcoin.bump,#mLocker.sgp .sgban.bump,#mLocker.sgp .tpop,#mLocker.sgp .sgdo.nope{animation:none}}
'''

JS = r'''
// ---------- (v327) My Locker and the Paint Shop, one page on the Strokes page's base. The window shows you (the demo's own character, in
// your paint, on its pad) wearing what you have on; in the shop, what you're trying on. In the locker a tap puts a thing on; in the shop
// a tap tries it on and Buy keeps it on. Drag spins you round, and you turn back to face the front after a moment ----------
const LKR = { tab: 'mine', sel: null, prev: null, got: new Set(), scr: { mine: 0, shop: 0 }, anim: false, from: 'mine', toastT: 0 };
function lkOn() { return menuPage === 'locker'; }
const LK_CAT = { head: 'Headgear', face: 'Facial', cloth: 'Clothing', eyes: 'Eyes' };
const LK_POP = { tophat: 'top', bowtie: 'bow' }; // (the piece a wearable is, where its name isn't the item's)
const LK_PAD = 0.62; // (the pad in dress mode: a podium, this much of the demo's)
const LK_PEN = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 19.5l1-4.2L15.4 5.4a1.9 1.9 0 0 1 2.7 0l.5.5a1.9 1.9 0 0 1 0 2.7L8.7 18.5z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/><path d="M13.6 7.2l3.2 3.2" stroke="currentColor" stroke-width="2.4"/></svg>';
const lkItem = id => ITEMS.find(w => w.id === id);
const lkWorn = w => w.slot === 'eyes' ? myLook.eyes === w.id : myLook[w.slot] === w.id;
const lkForSale = w => !bought(w.id) && (owns(w.id) || !needFind(w));
// how you'd look with it on: one thing per category (the face's spots apart), as the locker always had it
function lkWith(look, w) { const L = Object.assign({}, look); if (w.slot === 'eyes') { L.eyes = w.id; return L; } if (w.cat !== 'face') for (const o of WEAR) if (o.cat === w.cat && o.slot !== w.slot && L[o.slot] === o.id) L[o.slot] = null; L[w.slot] = w.id; return L; }
// what the window's character wears: the try-on, else what you have on
function lkDress() { if (SGD.built) SGD.A.L.wearing = LKR.prev || myLook; }
// (each item's picture once as a short blob link, not its whole image inline: the panel is redrawn on every tap)
const LK_PICS = new Map();
function lkPicUrl(w) { if (LK_PICS.has(w.id)) return LK_PICS.get(w.id); let u = ''; try { u = shopPic(w); } catch (e) { u = ''; } if (!u) return '';
  if (u.startsWith('data:') && window.Blob && window.URL && URL.createObjectURL) try { const b = atob(u.slice(u.indexOf(',') + 1)), a = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); u = URL.createObjectURL(new Blob([a], { type: 'image/png' })); } catch (e) {}
  LK_PICS.set(w.id, u); return u; }
function lkPic(w) { if (w.slot === 'eyes') return ES_ICON_T[w.id] || ''; const u = lkPicUrl(w); return u ? '<img class="stimg" src="' + u + '" alt="" draggable="false">' : '<svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg>'; }
// a hang tag: the item's picture, and a strip: Equipped, its price, or Find it
function lkCard(w, tab) {
  const own = bought(w.id), found = own || owns(w.id) || !needFind(w), on = own && lkWorn(w), n = store.drops || 0, broke = !own && found && n < PRICE(w), sel = LKR.sel === 'w:' + w.id;
  const fresh = tab === 'mine' ? own && (store.fresh || []).includes(w.id) : !own && owns(w.id) && needFind(w);
  const foot = own ? (on ? 'Equipped' : tab === 'shop' ? 'Yours' : '') : found ? DROP_SVG + '<b>' + PRICE(w) + '</b>' : LOCK_ICON + 'Find it';
  const lab = w.name + (own ? (on ? ', equipped' : ', yours') : found ? ', ' + PRICE(w) + ' dabs' + (broke ? ', ' + (PRICE(w) - n) + ' more needed' : '') : ', locked. Find it on ' + WEAR_WHERE[w.stage]) + (fresh ? ', new' : '');
  return '<button class="sgcard lkcard' + (sel ? ' sel' : '') + (own ? (on ? ' own on' : ' own') : found ? ' sale' : ' lock') + (broke ? ' broke' : '') + '" type="button" data-k="w:' + w.id + '" aria-pressed="' + sel + '" aria-label="' + escAttr(lab) + '"><i class="sghook"></i><span class="sgcb"><span class="sgca">' + lkPic(w) + '</span></span><span class="sgcf">' + foot + '</span>' + (fresh ? '<span class="sgnew">New</span>' : '') + '</button>';
}
// the locker: your paint, your eyes, and what you own (a tap puts it on)
function lkMineHtml() {
  const fresh = new Set(store.fresh || []), grid = l => '<div class="sggrid lkgrid' + (LKR.anim ? ' in' : '') + '">' + l + '</div>';
  let h = '<div class="lkhd"><h4 class="lkh">My Locker</h4><button class="lkname" id="lkNameBtn" type="button" aria-label="Change your name"><span id="lkNameT"></span>' + LK_PEN + '</button></div>';
  h += '<p class="lksec">Paint</p><div class="lkpaints" role="group" aria-label="Your paint">' + PALETTE.map(c => '<button class="sw" type="button" data-k="c:' + c.id + '" aria-label="' + c.name + ' paint" aria-pressed="' + (c.id === colorId) + '" style="--c:#' + c.hex.toString(16).padStart(6, '0') + '"><i></i></button>').join('') + '</div>';
  h += '<p class="lksec">Eyes</p><div class="lkeyes"><div class="lkstyles" role="group" aria-label="Eye style">' + Object.keys(EYE_STYLES).map(k => { const it = EXTRA.find(x => x.id === k), lk = !!it && !bought(k);
    return '<button class="eyes' + (lk ? ' locked' : '') + (it && !lk && fresh.has(k) ? ' fresh' : '') + '" type="button" data-k="e:' + k + '" aria-label="' + EYE_STYLES[k] + ' eyes' + (lk ? ', in the Paint Shop' : '') + '" aria-pressed="' + (myLook.eyes === k) + '">' + ES_ICON_T[k] + (lk ? LOCK_ICON : '') + '</button>'; }).join('') + '</div>';
  const ni = NO_IRIS(myLook.eyes); h += '<div class="lkirises' + (ni ? ' off' : '') + '" role="group" aria-label="Eye colour"' + (ni ? ' aria-disabled="true"' : '') + '>' + EYE_KEYS.map(k => '<button class="eyec" type="button" data-k="i:' + k + '" style="--ic:' + EYE_COLS[k].css + '" aria-label="' + EYE_COLS[k].name + ' eyes" aria-pressed="' + (myLook.iris === k) + '"><i></i></button>').join('') + '</div></div>';
  for (const c of ['head', 'face', 'cloth']) { const mine = WEAR.filter(w => w.cat === c && bought(w.id)).sort((a, b) => PRICE(a) - PRICE(b)), sale = WEAR.filter(w => w.cat === c && lkForSale(w)).length;
    h += '<p class="lksec">' + LK_CAT[c] + (mine.length ? '<i>' + mine.length + '</i>' : '') + '</p>' + (mine.length ? grid(mine.map(w => lkCard(w, 'mine')).join('')) : '<p class="lknone">Nothing here yet.' + (sale ? ' <button class="lkgo" type="button" data-go="shop">The Paint Shop has ' + sale + '</button>' : '') + '</p>'); }
  return h;
}
// the shop: the season's finds first, under their banner, then everything else for sale (what this visit bought stays, as yours)
function lkShopHtml() {
  const grid = l => '<div class="sggrid lkgrid' + (LKR.anim ? ' in' : '') + '">' + l + '</div>', list = c => ITEMS.filter(w => (c === 'season' ? !!w.season : !w.season && w.cat === c) && (!bought(w.id) || LKR.got.has(w.id))).sort((a, b) => PRICE(a) - PRICE(b)), cnt = ITEMS.filter(lkForSale).length;
  let h = '<div class="lkhd"><h4 class="lkh">Paint Shop</h4>' + (cnt ? '<span class="lkcnt">' + cnt + ' in stock</span>' : '') + '</div>', any = false;
  const sz = list('season'); if (sz.length) { any = true; const all = ITEMS.filter(w => w.season), got = all.filter(w => bought(w.id) || owns(w.id)).length;
    h += '<div class="lkszn" role="heading" aria-level="4"><span class="sbart" style="--sbbg:url(art/shop_hw_bg.webp)"></span><span class="lkszt"><i>Season One</i><b>Spooky SZN</b><small><u style="--p:' + (all.length ? got / all.length : 0).toFixed(3) + '"></u>' + got + ' of ' + all.length + ' found</small></span><img class="lkpump" src="art/shop_hw_pump.webp" alt="" draggable="false"></div>' + grid(sz.map(w => lkCard(w, 'shop')).join('')); }
  for (const c of ['head', 'face', 'cloth', 'eyes']) { const l = list(c); if (!l.length) continue; any = true; h += '<p class="lksec">' + LK_CAT[c] + '</p>' + grid(l.map(w => lkCard(w, 'shop')).join('')); }
  if (!any) h += '<p class="lkempty">' + SHOP_ICON + 'Nothing left to buy.<br>Everything is in your locker.</p>';
  return h;
}
function lkPaneRender() {
  const sc = $('lkScroll'), top = sc.scrollTop, ae = document.activeElement, fk = ae && ae.dataset && ae.dataset.k && sc.contains(ae) ? ae.dataset.k : '', el = LKR.tab === 'shop' ? $('lkPaneShop') : $('lkPaneMine');
  el.innerHTML = LKR.tab === 'shop' ? lkShopHtml() : lkMineHtml(); LKR.anim = false; nmSet($('lkNameT'), playerName());
  sc.scrollTop = top; if (fk) { const f = el.querySelector('[data-k="' + fk + '"]'); if (f) f.focus({ preventScroll: true }); }
}
function lkTabs() {
  for (const b of $('lkTabs').querySelectorAll('.sgtab')) { const on = b.dataset.tab === LKR.tab; b.classList.toggle('on', on); b.setAttribute('aria-selected', String(on)); b.tabIndex = on ? 0 : -1; }
  const mine = ITEMS.filter(w => bought(w.id)).length, sale = ITEMS.filter(lkForSale).length;
  $('lkTabMineI').innerHTML = frFace({ c: colorId }); $('lkTabMineN').textContent = mine + (mine === 1 ? ' item' : ' items'); $('lkTabShopN').textContent = sale ? sale + ' to buy' : 'All yours';
  $('lkTabMine').classList.toggle('fresh', LKR.tab !== 'mine' && (store.fresh || []).some(id => bought(id))); $('lkTabShop').classList.toggle('fresh', LKR.tab !== 'shop' && (store.fresh || []).some(id => !bought(id)));
  if (LKR.tab === 'shop' && (store.fresh || []).some(id => !bought(id))) { store.fresh = store.fresh.filter(id => bought(id)); save(); } // (seen in the shop: the dot goes; their tags still say New until bought)
}
function lkRender() {
  lkTabs(); const n = store.drops || 0; $('lkCoinN').textContent = String(n); $('lkCoin').setAttribute('aria-label', 'Dabs: ' + n + '. Open the Paint Shop');
  $('lkPanH').textContent = LKR.tab === 'shop' ? 'Paint Shop' : 'My Locker'; lkPaneRender(); $('lkArt').innerHTML = frFace({ c: colorId });
  $('lkUcode').hidden = ITEMS.every(w => bought(w.id)); lkShowRender();
}
function lkFitName() { const nb = $('lkName'); nb.style.fontSize = ''; if (!nb.clientWidth) return; let fs = parseFloat(getComputedStyle(nb).fontSize) || 24, i = 0; while (nb.scrollWidth > nb.clientWidth + 1 && fs > 13 && i++ < 10) { fs -= 1.5; nb.style.fontSize = fs + 'px'; } }
// the banner, its line, and the button: Equip, Equipped (and Take off), Buy, the price you can't reach yet, or Find it
function lkShowRender() {
  const s = LKR.sel, k = s ? s.slice(0, 1) : '', id = s ? s.slice(2) : '', w = k === 'w' ? lkItem(id) : null, n = store.drops || 0;
  let kind = '', name = '', line = '', note = '', doH = '', doCls = '', doDis = false, doLab = '', off = false;
  if (w) { const own = bought(w.id), found = own || owns(w.id) || !needFind(w), on = own && lkWorn(w), where = WEAR_WHERE[w.stage], p = PRICE(w);
    kind = w.season ? 'Spooky SZN · ' + LK_CAT[w.cat] : LK_CAT[w.cat]; name = w.name;
    line = own ? (needFind(w) ? 'Found on ' + where : 'From the Paint Shop') : found ? (owns(w.id) && needFind(w) ? 'You found it on ' + where : 'In stock now') : 'Found on ' + where + ' only';
    if (own) { if (on) { doH = ST_CHECK + 'Equipped'; doCls = 'on'; doDis = true; doLab = w.name + ' is equipped'; off = w.slot !== 'eyes'; } else { doH = 'Equip'; doLab = 'Put on the ' + w.name.toLowerCase(); } }
    else if (found) { if (n >= p) { doH = 'Buy<small>' + DROP_SVG + p + '</small>'; doCls = 'craft'; doLab = 'Buy the ' + w.name.toLowerCase() + ' for ' + p + ' dabs'; } else { doH = DROP_SVG + p; doDis = true; doLab = w.name + ', ' + p + ' dabs'; note = 'You need ' + (p - n) + ' more dabs. Matches pay in dabs'; } }
    else { doH = STROKE_LOCK + 'Find it'; doDis = true; doLab = w.name + ' is locked'; note = 'Find it on ' + where + ', then it’s for sale here'; } }
  else if (k === 'c') { const c = PALETTE.find(q => q.id === id) || colorOf(); kind = 'Your paint'; name = c.name; line = 'Everything you roll over turns ' + c.name.toLowerCase(); }
  else if (k === 'e') { kind = 'Your eyes'; name = EYE_STYLES[id] || 'Round'; line = NO_IRIS(id) ? 'These eyes keep their own colour' : 'Pick their colour under them'; }
  else if (k === 'i') { kind = 'Eye colour'; name = (EYE_COLS[id] || EYE_COLS.brown).name; line = 'The colour in the middle of your eyes'; }
  else if (LKR.tab === 'shop') { kind = 'Paint Shop'; name = 'Try it on'; line = 'Tap anything to see it on you'; }
  else { kind = 'My Locker'; name = playerName(); line = 'Tap to put it on. Drag to spin around'; }
  $('lkKind').textContent = kind; nmSet($('lkName'), name); $('lkName').dataset.def = !s && LKR.tab === 'mine' ? '1' : ''; $('lkLine').textContent = line; lkFitName();
  const b = $('lkDo'); b.hidden = !doH; if (doH) { b.className = 'sgdo' + (doCls ? ' ' + doCls : ''); b.innerHTML = '<span>' + doH + '</span>'; b.disabled = doDis; b.setAttribute('aria-label', doLab); }
  $('lkOff').hidden = !off; $('lkNote').hidden = !note; $('lkNote').textContent = note; $('mLocker').classList.toggle('sgnoted', !!note); SGD.rectDirty = true;
}
function lkToast(msg) { const pg = $('mLocker'), old = pg.querySelector('.sttoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'sttoast'; t.setAttribute('role', 'status'); t.textContent = msg; pg.appendChild(t); clearTimeout(LKR.toastT); LKR.toastT = setTimeout(() => t.remove(), 2300); }
// (the lesson's Buy step: under the button, so you still see yourself in the window: upright Ol' Bloop, sideways just the words)
function lkBuyTip(t, tc, key) { return innerWidth > innerHeight ? tutShow(tc, 'lkDo', key, true, false, 'below') : tutShow(t, 'lkDo', key, false, false, 'below'); }
function lkKick(key) { const el = $('lkScroll').querySelector('[data-k="' + key + '"]'); if (el) kick(el, 'tpop'); }
function lkReveal() { const sc = $('lkScroll'), el = LKR.sel && sc.querySelector('[data-k="' + LKR.sel + '"]'); if (!el) return; const r = el.getBoundingClientRect(), g = sc.getBoundingClientRect(); if (r.top < g.top + 8 || r.bottom > g.bottom - 8) sc.scrollTop += (r.top + r.height / 2) - (g.top + g.height / 2); }
function lkFreshOff(id) { if (store.fresh && store.fresh.includes(id)) { store.fresh = store.fresh.filter(x => x !== id); save(); } }
// putting a thing of yours on
function lkPutOn(w) { Object.assign(myLook, lkWith(myLook, w)); lkFreshOff(w.id); saveLook(); LKR.prev = null; lkDress(); sgDressReact(w); }
// buying the one you're trying on: paid for, and it stays on
function lkBuy(w) {
  if (!owns(w.id) && needFind(w)) { AU.nope(); kick($('lkDo'), 'nope'); lkToast('Find it on ' + WEAR_WHERE[w.stage] + ' first'); return; }
  const p = PRICE(w); if (!buyItem(w.id)) { AU.nope(); kick($('lkDo'), 'nope'); lkToast('You need ' + Math.max(1, p - (store.drops || 0)) + ' more dabs'); return; }
  LKR.got.add(w.id); Object.assign(myLook, lkWith(myLook, w)); lkFreshOff(w.id); saveLook(); LKR.prev = null; lkDress();
  AU.power(); buzz([12, 30, 18]); showDrops(); kick($('lkCoin'), 'bump'); sgDressCheer(); lkToast('Bought! It’s in your locker');
  lkRender(); lkKick('w:' + w.id);
}
// a pick in the panel
function lkTap(key) {
  AU.init(); const k = key.slice(0, 1), id = key.slice(2);
  if (k === 'c') return lkPaint(id);
  if (k === 'e') return lkEyes(id);
  if (k === 'i') return lkIris(id);
  const w = lkItem(id); if (!w) return; const again = LKR.sel === key; LKR.sel = key;
  if (LKR.tab === 'mine') { if (!lkWorn(w)) { lkPutOn(w); AU.pop(); buzz(5); } else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); lkFreshOff(w.id); } }
  else if (!again) { LKR.prev = bought(w.id) ? null : lkWith(myLook, w); lkDress(); sgDressReact(w); AU.pop(); buzz(5); }
  else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); }
  lkTabs(); lkPaneRender(); lkShowRender(); lkKick(key);
}
function lkPaint(id) {
  LKR.sel = 'c:' + id; LKR.prev = null; lkDress();
  if (id !== colorId) { setColor(id); store.color = colorId; save(); kick($('logo'), 'paint'); AU.pop(); AU.splat(0.8); buzz(6); if (SGD.built) { SGD.A.col.set(TEAMS[0].wet); sgDressPaint(true); } $('lkArt').innerHTML = frFace({ c: colorId }); }
  else { AU.ui(); buzz(4); }
  lkTabs(); lkPaneRender(); lkShowRender(); lkKick('c:' + id);
}
function lkEyes(id) {
  const it = EXTRA.find(x => x.id === id);
  if (it && !bought(id)) { lkSetTab('shop'); lkSelect(id); return; } // (not yours yet: over to the shop, where you can try them on)
  LKR.sel = 'e:' + id; LKR.prev = null; lkDress();
  if (myLook.eyes !== id) { myLook.eyes = id; lkFreshOff(id); saveLook(); AU.pop(); buzz(5); sgDressFace(); } else { AU.ui(); buzz(4); }
  lkPaneRender(); lkShowRender(); lkKick('e:' + id);
}
function lkIris(id) {
  if (NO_IRIS(myLook.eyes)) { AU.nope(); lkToast(EYE_STYLES[myLook.eyes] + ' eyes keep their own colour'); return; }
  LKR.sel = 'i:' + id; LKR.prev = null; lkDress();
  if (myLook.iris !== id) { myLook.iris = id; saveLook(); AU.pop(); buzz(5); sgDressFace(); } else { AU.ui(); buzz(4); }
  lkPaneRender(); lkShowRender(); lkKick('i:' + id);
}
// picking one from outside the panel (a new find's "See it in the shop", a locked eye style in the locker): tried on in the shop
function lkSelect(id, quiet) {
  const w = lkItem(id); if (!w) return;
  if (LKR.tab === 'mine' && w.slot === 'eyes') LKR.sel = 'e:' + id;
  else { LKR.sel = 'w:' + id; LKR.prev = LKR.tab === 'shop' && !bought(id) ? lkWith(myLook, w) : null; lkDress(); if (SGD.on) sgDressReact(w); else SGD.pend = w; }
  if (!quiet) { AU.pop(); buzz(5); } lkPaneRender(); lkShowRender(); lkReveal();
}
function lkSetTab(t, quiet) {
  t = t === 'shop' ? 'shop' : 'mine'; if (t === LKR.tab) return;
  LKR.scr[LKR.tab] = $('lkScroll').scrollTop; LKR.tab = t; LKR.sel = null; LKR.prev = null; LKR.anim = true; lkDress(); SGD.fzT = 0;
  $('mLocker').dataset.tab = t; $('lkPaneMine').hidden = t !== 'mine'; $('lkPaneShop').hidden = t !== 'shop';
  if (!quiet) { AU.ui(); buzz(4); }
  lkRender(); $('lkScroll').scrollTop = LKR.scr[t] || 0;
}
function openLocker(tab, id) {
  if (state !== 'menu' || building) return;
  if (lkOn()) { lkSetTab(tab); if (id) lkSelect(id); return; }
  if (strokesOpen()) closeStrokes(); if (menuPage === 'worlds') { closeSeason(); $('mWorld').hidden = true; } if (menuPage === 'events') closeEvents();
  closeSide(true); if (lookOpen) closeLook(); else if (shopOpen) closeShop(true); // (the old sheets, never open now)
  LKR.tab = LKR.from = tab === 'shop' ? 'shop' : 'mine'; LKR.sel = null; LKR.prev = null; LKR.got.clear(); LKR.scr.mine = LKR.scr.shop = 0; LKR.anim = true;
  menuPage = 'locker'; menu.dataset.page = 'locker'; $('mHome').hidden = true; const pg = $('mLocker'); pg.dataset.tab = LKR.tab; pg.hidden = false; document.body.classList.add('evon', 'stpage');
  $('lkPaneMine').hidden = LKR.tab !== 'mine'; $('lkPaneShop').hidden = LKR.tab !== 'shop'; $('lkUnlockForm').hidden = true; $('lkUnlockLink').hidden = false;
  SGD.kind = 'dress'; SGD.id = null; SGD.started = false; SGD.pend = null; SGD.rectDirty = true;
  if (!store.seen.look) { store.seen.look = 1; save(); $('lookBtn').classList.remove('hot'); }
  lkRender(); $('lkScroll').scrollTop = 0; if (id) lkSelect(id, true);
  for (const c of pg.querySelectorAll('.sgtab')) { c.style.animation = 'none'; void c.offsetWidth; c.style.animation = ''; }
  AU.music('shop'); setTimeout(() => $('lkBack').focus({ preventScroll: true }), 40);
}
function closeLocker(quiet) {
  if (!lkOn()) return; LKR.prev = null; lkDress(); sgStop(); SGD.kind = ''; SGD.dDrag = null;
  const pg = $('mLocker'); pg.hidden = true; pg.classList.remove('sgnoted'); { const t = pg.querySelector('.sttoast'); if (t) t.remove(); } $('lkUnlockForm').hidden = true; $('lkUnlockLink').hidden = false;
  document.body.classList.remove('evon', 'stpage'); menuPage = 'home'; menu.dataset.page = 'home'; $('mHome').hidden = false;
  if (quiet) return; AU.music('menu'); renderLobbyUI(); setTimeout(() => $(LKR.from === 'shop' ? 'dabsBtn' : 'lookBtn').focus({ preventScroll: true }), 40);
}
$('lkCoinI').innerHTML = DROP_SVG; $('lkTabShopI').innerHTML = SHOP_ICON;
$('lkBack').addEventListener('click', () => { AU.init(); AU.ui(); closeLocker(); });
$('lkCoin').addEventListener('click', () => { AU.init(); if (LKR.tab !== 'shop') lkSetTab('shop'); else { AU.ui(); kick($('lkCoin'), 'bump'); lkToast((store.drops || 0) + ' dabs to spend. Matches pay in dabs'); } });
$('lkTabs').addEventListener('click', e => { const b = e.target.closest('.sgtab'); if (b) { AU.init(); lkSetTab(b.dataset.tab); } });
$('lkTabs').addEventListener('keydown', e => { const dl = e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === 'ArrowLeft' || e.key === 'ArrowUp'; if (!dl) return; e.preventDefault(); e.stopPropagation(); const t = LKR.tab === 'mine' ? 'shop' : 'mine'; AU.init(); lkSetTab(t); $(t === 'shop' ? 'lkTabShop' : 'lkTabMine').focus(); });
$('lkPanel').addEventListener('click', e => { const t = e.target.closest('[data-k], [data-go], #lkNameBtn'); if (!t || !$('lkPanel').contains(t)) return; AU.init();
  if (t.id === 'lkNameBtn') { AU.ui(); openName(false); return; } if (t.dataset.go) { lkSetTab(t.dataset.go); return; } lkTap(t.dataset.k); });
$('lkDo').addEventListener('click', () => { AU.init(); const w = LKR.sel && LKR.sel[0] === 'w' && lkItem(LKR.sel.slice(2)); if (!w) return;
  if (bought(w.id)) { if (!lkWorn(w)) { lkPutOn(w); AU.pop(); buzz(5); lkTabs(); lkPaneRender(); lkShowRender(); } return; } lkBuy(w); });
$('lkOff').addEventListener('click', () => { AU.init(); const w = LKR.sel && LKR.sel[0] === 'w' && lkItem(LKR.sel.slice(2)); if (!w || w.slot === 'eyes' || !lkWorn(w)) return;
  myLook[w.slot] = null; saveLook(); LKR.prev = null; lkDress(); AU.ui(); buzz(4); if (SGD.built) { const D = SGD.A.D; D.squash = Math.max(D.squash, 0.3); SGD.mood = 'pout'; SGD.moodT = 0.9; }
  lkTabs(); lkPaneRender(); lkShowRender(); setTimeout(() => { if (lkOn() && !$('lkDo').hidden) $('lkDo').focus({ preventScroll: true }); }, 30); });
$('lkUnlockLink').addEventListener('click', () => { AU.init(); AU.ui(); $('lkUnlockLink').hidden = true; $('lkUnlockForm').hidden = false; setTimeout(() => $('lkUnlockCode').focus(), 30); });
$('lkUnlockCode').addEventListener('keydown', e => e.stopPropagation());
$('lkUnlockForm').addEventListener('submit', e => { e.preventDefault(); AU.init(); const v = $('lkUnlockCode').value.trim();
  if (v === '1234') { for (const w of ITEMS) { OWNED.add(w.id); BOUGHT.add(w.id); } store.owned = [...OWNED]; store.bought = [...BOUGHT]; save(); $('lkUnlockCode').value = ''; $('lkUnlockForm').hidden = true; $('lkUnlockLink').hidden = false; AU.power(); lkRender(); lkToast('Every item is unlocked'); }
  else { AU.nope(); kick($('lkUnlockForm'), 'nope'); lkToast('That code doesn’t work'); } });
// the window: a drag spins you round (a flick carries on), a tap gets a hop; the round button turns you to show your back
{ const st = $('lkStage');
  st.addEventListener('pointerdown', e => { if (!SGD.on || SGD.kind !== 'dress') return; const now = performance.now(); SGD.dDrag = { id: e.pointerId, x: e.clientX, x0: e.clientX, y0: SGD.dyaw, t: now, tm: now, v: 0 }; SGD.dyawTo = null; SGD.dV = 0; try { st.setPointerCapture(e.pointerId); } catch (x) {} });
  st.addEventListener('pointermove', e => { const g = SGD.dDrag; if (!g || g.id !== e.pointerId) return; const now = performance.now(), dm = Math.max(4, now - g.tm); g.v = g.v * 0.5 + 0.5 * (e.clientX - g.x) * 0.012 / (dm / 1000); g.tm = now; lookSwiped += Math.abs(e.clientX - g.x); g.x = e.clientX; SGD.dyaw = g.y0 + (e.clientX - g.x0) * 0.012; });
  const up = e => { const g = SGD.dDrag; if (!g || g.id !== e.pointerId) return; SGD.dDrag = null; const now = performance.now();
    if (e.type === 'pointerup' && Math.abs(e.clientX - g.x0) < 8 && now - g.t < 400) sgDressPoke(); else { SGD.dV = now - g.tm < 90 ? clamp(g.v, -14, 14) : 0; SGD.dHold = 2.6; } };
  st.addEventListener('pointerup', up); st.addEventListener('pointercancel', up);
  if (window.ResizeObserver) try { new ResizeObserver(() => { SGD.rectDirty = true; }).observe(st); } catch (e) {} }
$('lkRot').addEventListener('click', () => { AU.init(); AU.ui(); buzz(4); const back = Math.abs(wrapA(SGD.dyaw)) > 1.6; SGD.dyaw = wrapA(SGD.dyaw); SGD.dV = 0; SGD.dyawTo = back ? 0 : Math.PI; SGD.dHold = 4; });
addEventListener('resize', () => { if (lkOn()) setTimeout(lkFitName, 60); });
// ---- the window in dress mode: you alone in the middle of the pad, facing out, the camera in close (closer still on your face)
function sgDressStart() {
  const A = SGD.A, B = SGD.B; SGD.t = 0; SGD.ev = {}; sgReset(A); sgReset(B); B.show = false; B.L.drop.visible = false;
  SGD.trap.visible = SGD.wg.visible = SGD.lane.visible = SGD.boom.visible = false; SGD.mk.visible = SGD.mkF.visible = SGD.mkB.visible = SGD.ice.visible = false; SGD.iceK = 0; SGD.zk = 0; SGD.sp = {}; for (const q of SGD.shots) q.on = false; if (SGD.bm) SGD.bm.on = false; if (SGD.whirl) SGD.whirl.ph = '';
  for (const [m, sc] of SGD.padMs) m.scale.set(sc.x * LK_PAD, sc.y, sc.z * LK_PAD); SGD.padR2 = (SG_R * LK_PAD) ** 2;
  A.col.set(TEAMS[0].wet); lkDress(); sgAt(A, 0, 0); A.D.yaw = sgYawCam(A); A.V.yawD = undefined;
  SGD.dyaw = 0; SGD.dV = 0; SGD.dyawTo = null; SGD.dHold = 0; SGD.dDrag = null; SGD.fz = 0; SGD.fzT = 0; SGD.dk = 0.6; SGD.popId = null; SGD.mood = 'glee'; SGD.moodT = 0.9; A.D.squash = 0.6; A.D.wob = 0.8;
  sgDressPaint(false); sgRing(0, 0, 0.7, TEAMS[0].wet);
  if (SGD.pend) { const w = SGD.pend; SGD.pend = null; sgDressReact(w); }
}
function sgDress(dt) {
  const A = SGD.A, D = A.D; SGD.t += dt; if (SGD.shk > 0) SGD.shk = Math.max(0, SGD.shk - dt * 3);
  if (!SGD.dDrag) {
    if (SGD.dV) { SGD.dyaw += SGD.dV * dt; SGD.dV *= Math.exp(-dt * 2.6); if (Math.abs(SGD.dV) < 0.08) SGD.dV = 0; }
    else if (SGD.dyawTo !== null) { const e = SGD.dyawTo - SGD.dyaw; SGD.dyaw += e * Math.min(1, dt * (reduceMotion ? 30 : 5)); if (Math.abs(e) < 0.01) { SGD.dyaw = SGD.dyawTo; SGD.dyawTo = null; } }
    else if ((SGD.dHold -= dt) <= 0 && SGD.dyaw) { SGD.dyaw = wrapA(SGD.dyaw); SGD.dyaw -= SGD.dyaw * Math.min(1, dt * (reduceMotion ? 30 : 2.4)); if (Math.abs(SGD.dyaw) < 0.003) SGD.dyaw = 0; }
  }
  const y0 = D.yaw, yt = sgYawCam(A) + SGD.dyaw; D.yaw = yt; D.turn = clamp(wrapA(yt - y0) / Math.max(dt, 1e-3) / 9, -1, 1); D.spd = 0;
  D.ip.expr = null; D.ip.watch = null; if (Math.abs(wrapA(SGD.dyaw)) < 0.55 && !SGD.dDrag) sgWatch(A, null);
  if (SGD.moodT > 0) { SGD.moodT -= dt; D.ip.expr = SGD.mood; } else D.ip.expr = SGD.dDrag ? 'curious' : 'happy';
  if (SGD.fzT > 0) SGD.fzT -= dt; SGD.fz += ((SGD.fzT > 0 ? 1 : 0) - SGD.fz) * Math.min(1, dt * 3); SGD.dk += (1 - SGD.dk) * Math.min(1, dt * 3.2);
}
// a thing put on or tried on: it pops in, a hop and a happy face; on the face, the camera comes in close; worn at the side or
// on the back, you turn to show it, then back
function sgDressReact(w) {
  if (!SGD.built) return; const D = SGD.A.D;
  SGD.popId = w.slot === 'eyes' || w.id === 'lashes' || w.id === 'patch' ? null : w.id; SGD.popT = 0;
  D.squash = Math.max(D.squash, 0.45); D.wob = Math.max(D.wob, 0.7); SGD.mood = w.slot === 'eyes' ? 'smirk' : 'glee'; SGD.moodT = 1.1;
  SGD.fzT = w.cat === 'face' || w.slot === 'eyes' ? 2.6 : 0;
  SGD.dV = 0; SGD.dyaw = wrapA(SGD.dyaw); SGD.dyawTo = w.slot === 'back' ? 2.7 : w.slot === 'side' ? -0.8 : w.slot === 'arms' ? 0.75 : 0; SGD.dHold = SGD.dyawTo ? 2.2 : 0;
  sgRing(0, 0, 0.6, 0xFFFFFF); if (!reduceMotion) sgBurst(0, 0, COL_WHITE, 6, 2.4, 1.2);
  setTimeout(() => { if (lkOn()) AU.vox(w.cat === 'cloth' ? 'giggle' : 'ooh', 0.9); }, 110);
}
function sgDressFace() { if (!SGD.built) return; const D = SGD.A.D; SGD.fzT = 2.4; SGD.mood = ['curious', 'smirk', 'glee'][(Math.random() * 3) | 0]; SGD.moodT = 1.3; D.squash = Math.max(D.squash, 0.3); SGD.dyawTo = 0; SGD.dHold = 0; SGD.dV = 0; }
// your paint: a splat of it under you; a new one splashes up round you as you hop
function sgDressPaint(burst) {
  sgPaintClear(); sgSplat(0, 0, 0.62 / LK_PAD, TEAMS[0].css); // (drawn on the full pad's map: the pad is smaller)
  if (burst) { const D = SGD.A.D; if (!reduceMotion) sgBurst(0, 0, SGD.A.col, 18, 3.4, 2.0); sgRing(0, 0, 0.75, TEAMS[0].wet); sgRing(0, 0, 0.45, 0xFFFFFF); D.squash = 0.8; D.wob = 1; SGD.mood = 'glee'; SGD.moodT = 1.2; SGD.fzT = 0; }
}
function sgDressCheer() { if (!SGD.built) return; const D = SGD.A.D; sgRing(0, 0, 0.75, 0xFFE23C); sgRing(0, 0, 0.5, 0xFFFFFF); if (!reduceMotion) { sgBurst(0, 0, COL_WHITE, 10, 4, 1.8); sgBurst(0, 0, SGD.A.col, 14, 4.4, 2.2); sgShk(0.35); } sgFlash('w'); D.squash = 0.85; D.wob = 1; SGD.mood = 'glee'; SGD.moodT = 1.6; }
function sgDressPoke() { if (!SGD.built) return; const D = SGD.A.D; D.squash = 0.7; D.wob = 1; SGD.mood = ['glee', 'smirk', 'blep', 'cute'][(Math.random() * 4) | 0]; SGD.moodT = 1; AU.pop(); if (Math.random() < 0.7) AU.vox(['hup', 'whee', 'giggle', 'hoh'][(Math.random() * 4) | 0]); }
'''

def apply(s):
    # ---- the page, after the Strokes page
    s = rep(s, '    <div class="mevents" id="mEvents" hidden><div class="evwash" aria-hidden="true"><i></i></div>\n', HTML + '    <div class="mevents" id="mEvents" hidden><div class="evwash" aria-hidden="true"><i></i></div>\n')
    # ---- the look: the Strokes page's rules shared with it, then its own
    c = s.count('#mStrokes.sgp'); assert c == 202, c
    s = s.replace('#mStrokes.sgp', ':is(#mStrokes,#mLocker).sgp')
    s = rep(s, '#mStrokes .sgflash', ':is(#mStrokes,#mLocker) .sgflash', 5)
    s = rep(s, '@media (prefers-reduced-motion:reduce){#friendsModal.frpage{animation:none}#friendsModal .frflag::after{animation:none}}\n</style>',
        '@media (prefers-reduced-motion:reduce){#friendsModal.frpage{animation:none}#friendsModal .frflag::after{animation:none}}\n' + CSS + '</style>')
    # ---- the demo window, for either page: its elements are the open page's own
    s = rep(s, "const SG_PAPER = '#F6F0E2';\n", "const SG_PAPER = '#F6F0E2';\n"
        "// (v327) the window's page: the Strokes page, or the locker's\n"
        "const SGH = { st: { pg: $('mStrokes'), stage: $('sgStage'), ban: $('sgBan'), rot: $('sgRot'), bg: $('sgBg'), flash: $('sgFlash'), foot: $('mStrokes').querySelector('.sgfoot') } };\n"
        "const sgH = () => lkOn() ? SGH.lk || (SGH.lk = { pg: $('mLocker'), stage: $('lkStage'), ban: $('lkBan'), rot: $('lkRot'), bg: $('lkBg'), flash: $('lkFlash'), foot: $('mLocker').querySelector('.sgfoot') }) : SGH.st;\n")
    s = rep(s, "  SGD.rectDirty = false; const el = $('sgStage'), r = el.getBoundingClientRect(),", "  SGD.rectDirty = false; const H0 = sgH(), el = H0.stage, r = el.getBoundingClientRect(),")
    s = rep(s, "  const bn = $('sgBan').getBoundingClientRect(), ft = $('mStrokes').querySelector('.sgfoot').getBoundingClientRect();", "  const bn = H0.ban.getBoundingClientRect(), ft = H0.foot.getBoundingClientRect();")
    s = rep(s, "SGD.insB = ft.height > 0 ? clamp(r.bottom - ft.top + 2, 0, h * 0.4) : 0; $('sgRot').style.bottom =", "SGD.insB = ft.height > 0 ? clamp(r.bottom - ft.top + 2, 0, h * 0.4) : 0; H0.rot.style.bottom =")
    s = rep(s, "  if (hole !== SGD.hole) { SGD.hole = hole; $('sgBg').style.clipPath = hole; }", "  if (hole !== SGD.hole) { SGD.hole = hole; H0.bg.style.clipPath = hole; }")
    s = rep(s, "function sgHole(on) { const pg = $('mStrokes'); pg.classList.toggle('sghole', on); pg.classList.toggle('sgdemo', on); $('sgRot').hidden = !on; if (on) SGD.rectDirty = true; else { SGD.hole = ''; $('sgBg').style.clipPath = ''; } }",
        "function sgHole(on) { const H0 = sgH(), pg = H0.pg; pg.classList.toggle('sghole', on); pg.classList.toggle('sgdemo', on); H0.rot.hidden = !on; if (on) SGD.rectDirty = true; else { SGD.hole = ''; H0.bg.style.clipPath = ''; } }")
    s = rep(s, "function sgFlash(kind) { const f = $('sgFlash'); if (!f) return;", "function sgFlash(kind) { const f = sgH().flash; if (!f) return;")
    # it runs for the locker too (in dress mode); dress mode starts its own way, and the demos get your current paint and look back
    s = rep(s, "const sgWant = () => strokesOpen() && stCat !== 'skill' && !!SGD.kind && $('stPop').hidden && !document.hidden",
        "const sgWant = () => (strokesOpen() ? stCat !== 'skill' && !!SGD.kind && $('stPop').hidden : lkOn() && SGD.kind === 'dress') && !document.hidden")
    s = rep(s, "  if (!reduceMotion) sgStep(dt);\n  sgVis(dt); sgRender();", "  if (SGD.kind === 'dress') sgDress(dt); else if (!reduceMotion) sgStep(dt);\n  sgVis(dt); sgRender();")
    s = rep(s, "function sgLoop() {\n  // (the ones that travel start the next time from the other side)\n",
        "function sgLoop() {\n  if (SGD.kind === 'dress') return sgDressStart(); SGD.dk = SGD.fz = 0; for (const [m, sc] of SGD.padMs) m.scale.copy(sc); SGD.padR2 = SG_R * SG_R; SGD.A.col.set(TEAMS[0].wet); SGD.A.L.wearing = myLook; // (v327: the locker's dress mode; the demos in your paint as it is now)\n  // (the ones that travel start the next time from the other side)\n")
    # the camera in dress mode: in on you, lower and closer (closer still on your face)
    s = rep(s, "  const vt = Math.tan(C.fov * Math.PI / 360), ht = vt * asp, el = 0.48, R = SG_R * 1.04, dist = Math.max(R / (0.94 * ht), (R * Math.sin(el) + 0.55) / (0.9 * vt * fh / r.h)) * (1 + 0.14 * (SGD.zk || 0)), cy = Math.sin(el) * dist, cz = Math.cos(el) * dist;\n"
        "  C.position.set(SG_X + Math.sin(SGD.yaw) * cz, cy + 0.2, SG_Z + Math.cos(SGD.yaw) * cz);",
        "  const dk = SGD.kind === 'dress' ? SGD.dk || 0 : 0, fz = dk ? SGD.fz || 0 : 0, ty = 0.2 + (0.26 + 0.12 * fz - 0.2) * dk, R0 = SG_R * 1.04, Rd = SG_R * LK_PAD * 1.04 * (1 - fz) + 0.74 * fz; // (v327: dress mode: the small pad whole, or your face)\n"
        "  const vt = Math.tan(C.fov * Math.PI / 360), ht = vt * asp, el = 0.48 + (0.38 - 0.1 * fz - 0.48) * dk, R = R0 + (Rd - R0) * dk, hc = 0.55 + (0.62 - 0.3 * fz - 0.55) * dk, dist = Math.max(R / (0.94 * ht), (R * Math.sin(el) + hc) / (0.9 * vt * fh / r.h)) * (1 + 0.14 * (SGD.zk || 0)), cy = Math.sin(el) * dist, cz = Math.cos(el) * dist;\n"
        "  C.position.set(SG_X + Math.sin(SGD.yaw) * cz, cy + ty, SG_Z + Math.cos(SGD.yaw) * cz);")
    s = rep(s, "root.add(top, side, rim, gsh); SGD.pad = top;", "root.add(top, side, rim, gsh); SGD.pad = top; SGD.padMs = [top, side, rim, gsh].map(m => [m, m.scale.clone()]); SGD.padR2 = SG_R * SG_R; // (v327: the pad's pieces, made smaller in dress mode)")
    s = rep(s, "if (p.y < 0.04 && p.x * p.x + p.z * p.z < SG_R * SG_R) {", "if (p.y < 0.04 && p.x * p.x + p.z * p.z < SGD.padR2) {")
    s = rep(s, "C.up.set(0, 1, 0); C.lookAt(SG_X, 0.2 + 0.3 * (SGD.zk || 0), SG_Z);", "C.up.set(0, 1, 0); C.lookAt(SG_X, ty + 0.3 * (SGD.zk || 0), SG_Z);")
    # a thing put on pops in on its own (the rest stay as they are)
    s = rep(s, "  sgShots(dt); sgFx(dt);\n}", "  sgShots(dt); sgFx(dt);\n"
        "  if (SGD.popId && SGD.kind === 'dress') { SGD.popT += dt; const u = Math.min(1, SGD.popT / 0.6), k = Math.max(0.001, easeElastic(u)), W = SGD.A.L.wear, o = W[LK_POP[SGD.popId] || SGD.popId]; for (const m of [].concat(o || [])) if (m && m.visible && W.bs && W.bs.has(m)) m.scale.multiplyScalar(k); if (u >= 1) SGD.popId = null; } // (v327)\n}")
    # the lobby holds still under the page, as under the Strokes page, and the window draws
    s = rep(s, "menuPage === 'events' || menuPage === 'strokes' || !commModalEl.hidden", "menuPage === 'events' || menuPage === 'strokes' || menuPage === 'locker' || !commModalEl.hidden")
    s = rep(s, "renderFrame(); else if (state === 'menu' && menuPage === 'strokes') sgTick(rdt);", "renderFrame(); else if (state === 'menu' && (menuPage === 'strokes' || menuPage === 'locker')) sgTick(rdt);")
    # ---- the page's code, after the old locker's
    s = rep(s, "canvas.addEventListener('pointerup', endLookDrag); canvas.addEventListener('pointercancel', endLookDrag);\n",
        "canvas.addEventListener('pointerup', endLookDrag); canvas.addEventListener('pointercancel', endLookDrag);\n" + JS)
    # ---- the ways in: the lobby's locker button and dabs, a new find's button
    s = rep(s, "$('lookBtn').addEventListener('click', () => { AU.init(); AU.ui(); openLook(); });", "$('lookBtn').addEventListener('click', () => { AU.init(); AU.ui(); openLocker('mine'); });")
    s = rep(s, "$('dabsBtn').addEventListener('click', () => { AU.init(); AU.ui(); openShop('lobby'); });", "$('dabsBtn').addEventListener('click', () => { AU.init(); AU.ui(); openLocker('shop'); });")
    s = rep(s, "  irisClose(() => { end.hidden = true; showMenu(); camSnap = true; irisOpen(); if (w && !bought(w.id)) { openShop('lobby'); return; } openLook(); const t = w && $('lookRail').querySelector('[data-w=\"' + w.id + '\"]'); if (t) { const r = $('lookRail'); r.scrollLeft = Math.max(0, t.offsetLeft - (r.clientWidth - t.offsetWidth) / 2); railEdge(); } }); });",
        "  irisClose(() => { end.hidden = true; showMenu(); camSnap = true; irisOpen(); openLocker(w && !bought(w.id) ? 'shop' : 'mine', w ? w.id : null); }); }); // (v327: tried on in the shop, or picked out in the locker)")
    # ---- the page counts as open where the old locker and shop did
    s = rep(s, "  if (state !== 'menu' || building || lookOpen || shopOpen || strokesOpen()) return;", "  if (state !== 'menu' || building || lookOpen || shopOpen || strokesOpen() || lkOn()) return;")
    s = rep(s, "  if (state !== 'menu' || building || lookOpen || menuPage === 'worlds') return;", "  if (state !== 'menu' || building || lookOpen || menuPage === 'worlds' || lkOn()) return;")
    s = rep(s, "$('homePlay').addEventListener('click', () => { AU.init(); if (state !== 'menu' || building || lookOpen || shopOpen) return;", "$('homePlay').addEventListener('click', () => { AU.init(); if (state !== 'menu' || building || lookOpen || shopOpen || lkOn()) return;")
    s = rep(s, "function openComms() { if (state !== 'menu' || lookOpen || !commsDue()) return;", "function openComms() { if (state !== 'menu' || lookOpen || lkOn() || !commsDue()) return;")
    s = rep(s, "const onCalm = () => state === 'menu' && !lookOpen && !shopOpen && !irisBusy", "const onCalm = () => state === 'menu' && !lookOpen && !shopOpen && !lkOn() && !irisBusy")
    s = rep(s, "function openSettings() { if (state !== 'menu' || lookOpen || shopOpen) return;", "function openSettings() { if (state !== 'menu' || lookOpen || shopOpen || lkOn()) return;")
    s = rep(s, "function openStats() { if (state !== 'menu' || lookOpen) return;", "function openStats() { if (state !== 'menu' || lookOpen || lkOn()) return;")
    s = rep(s, "function openSide() { if (state !== 'menu' || lookOpen || shopOpen) return;", "function openSide() { if (state !== 'menu' || lookOpen || shopOpen || lkOn()) return;")
    s = rep(s, "  if (state !== 'menu' || building || lookOpen || shopOpen || menuPage === 'events') return;", "  if (state !== 'menu' || building || lookOpen || shopOpen || lkOn() || menuPage === 'events') return;")
    s = rep(s, "if (shopOpen) closeShop(true); if (lookOpen) closeLook();", "if (shopOpen) closeShop(true); if (lookOpen) closeLook(); if (lkOn()) closeLocker(true);", 2)
    # keys: Escape closes the page; and no key starts a match from under a page (only the canvases page's start does)
    s = rep(s, "  if (lookOpen) { if (e.key === 'Escape') { e.preventDefault(); closeLook(); } return; }\n",
        "  if (lookOpen) { if (e.key === 'Escape') { e.preventDefault(); closeLook(); } return; }\n  if (state === 'menu' && lkOn()) { if (e.key === 'Escape') { e.preventDefault(); closeLocker(); } return; } // (v327)\n")
    s = rep(s, "if (state === 'menu') { if (menuPage === 'home') openWorlds(); else if ($('startBtn').disabled) return;", "if (state === 'menu') { if (menuPage === 'home') openWorlds(); else if (menuPage !== 'worlds' || $('startBtn').disabled) return;")
    # your dabs and your name on the page
    s = rep(s, "if ($('lkDabsN')) $('lkDabsN').textContent = String(n); }", "if ($('lkDabsN')) $('lkDabsN').textContent = String(n); if ($('lkCoinN')) $('lkCoinN').textContent = String(n); }")
    s = rep(s, "nmSet($('pbName'), n); nmSet($('lookNameTxt'), n); }", "nmSet($('pbName'), n); nmSet($('lookNameTxt'), n); nmSet($('lkNameT'), n); { const b = $('lkName'); if (b && b.dataset.def === '1') nmSet(b, n); } }")
    # ---- the lessons, on the new page
    s = rep(s, "key === 'browse' && lookOpen ? 'spin' : null);", "key === 'browse' && (lookOpen || lkOn()) ? 'spin' : null);")
    s = rep(s, "  const sc = el.closest('.shgrid, .lrail'); if (!sc) return;", "  const sc = el.closest('.shgrid, .lrail, #lkScroll'); if (!sc) return;")
    s = rep(s, "{ const nb = shopOpen || lookOpen || strokesOpen();", "{ const nb = shopOpen || lookOpen || strokesOpen() || lkOn();")
    s = rep(s, "if (vis && block) { const sc = el.closest('.shgrid, .lrail');", "if (vis && block) { const sc = el.closest('.shgrid, .lrail, #lkScroll');")
    s = rep(s, "  if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back'); if (lookOpen) return tutShow('Back to the lobby', 'lkDone', 'back');\n",
        "  if (lkOn()) return tutShow('Back to the lobby', 'lkBack', 'back');\n")
    s = rep(s, "  if (!lookOpen || lookSwiped - tutSpin0 > 40) return tutGest(null);\n",
        "  if (!(lookOpen || lkOn()) || lookSwiped - tutSpin0 > 40) return tutGest(null);\n"
        "  if (lkOn()) { if (!SGD.on) return; const r = SGD.rect, D = SGD.A.D; tutGV.set(D.x, 0.35, D.z).project(SGD.cam); tutGestEl.style.left = (r.x + (tutGV.x + 1) / 2 * r.w).toFixed(0) + 'px'; tutGestEl.style.top = (r.y + (1 - tutGV.y) / 2 * r.h).toFixed(0) + 'px'; return; } // (v327: on you in the page's window)\n")
    s = rep(s, "t.fangs = store.drops || 0; save(); if (shopOpen) renderShop(); }", "t.fangs = store.drops || 0; save(); if (shopOpen) renderShop(); if (lkOn()) lkRender(); }")
    s = rep(s, "    if (state === 'menu' && lookOpen && store.zombieDeal && bought('zombie') && myLook.eyes !== 'zombie') { if (lookCat !== 'eyes') return tutShow('Open Eyes and try them on', 'lc-eyes', 'eyesz'); return tutShow('Tap the zombie eyes to put them on', () => $('eyeStyles').querySelector('[data-es=\"zombie\"]'), 'wearz'); } /* (bought just now: the shop's Back brought you here to put them on) */",
        "    if (state === 'menu' && lkOn() && store.zombieDeal && bought('zombie') && myLook.eyes !== 'zombie') { if (LKR.tab !== 'mine') return tutShow('Open your locker and put them on', 'lkTabMine', 'eyesz'); return tutShow('Tap the zombie eyes to put them on', () => $('lkPaneMine').querySelector('[data-k=\"e:zombie\"]'), 'wearz'); } /* (v327: bought, they go straight on; taken off again, they're in your locker) */")
    s = rep(s, "  const card = id => $('shopGrid').querySelector('.shitem[data-w=\"' + id + '\"]'), tile = id => $('lookRail').querySelector('.ltile[data-w=\"' + id + '\"]');",
        "  const card = id => $('lkPaneShop').querySelector('.sgcard[data-k=\"w:' + id + '\"]'), tile = id => $('lkPaneMine').querySelector('.sgcard[data-k=\"w:' + id + '\"]'); // (v327: the page's tags)")
    s = rep(s, "    if (shopOpen) { if (!bought('flower')) return tutShow('You found a flower! It\\u2019s half price today. Buy it', () => card('flower'), 'buyflower');\n"
        "      if (!bought('fangs')) { tutFangsSale(); return tutShow('It\\u2019s Spooky SZN! Fangs are also on sale! Grab it', () => card('fangs'), 'buyfangs'); }\n"
        "      tutSet('locker'); return; }\n"
        "    if (lookOpen) return tutShow('Open the Paint Shop', 'lkShop', 'shop');\n",
        "    if (lkOn() && LKR.tab === 'shop') { if (!bought('flower')) return LKR.sel !== 'w:flower' ? tutShow('You found a flower! It\\u2019s half price today. Tap it to try it on', () => card('flower'), 'buyflower') : lkBuyTip('Looking good! Buy it', 'Looking good! *Buy it*', 'buyflower2');\n"
        "      if (!bought('fangs')) { tutFangsSale(); return LKR.sel !== 'w:fangs' ? tutShow('It\\u2019s Spooky SZN! Fangs are also on sale! Try them on', () => card('fangs'), 'buyfangs') : lkBuyTip('Grab them! Buy the fangs', '*Grab them!*', 'buyfangs2'); }\n"
        "      tutSet('locker'); return; }\n"
        "    if (lkOn()) return tutShow('Open the Paint Shop', 'lkTabShop', 'shop');\n")
    s = rep(s, "    if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back');\n"
        "    if (lookOpen) {\n"
        "      if (myLook.mouth !== 'fangs') { if (lookCat !== 'face') return tutShow('Open Facial. Your fangs are in there', 'lc-face', 'face'); return tutShow('Tap the fangs to put them on', () => tile('fangs'), 'wear'); }\n",
        "    if (lkOn()) {\n"
        "      if (LKR.tab !== 'mine') return tutShow('All yours! Now open your locker', 'lkTabMine', 'tomine');\n"
        "      if (myLook.mouth !== 'fangs') return tutShow('Tap the fangs to put them on', () => tile('fangs'), 'wear');\n")
    s = rep(s, "  if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back'); if (lookOpen) { if (tutBrowseAt && performance.now() - tutBrowseAt < 4200) return tutShow('Take a look around, squirt. Express yourself!', null, 'browse', false, true, null, true); return tutHide(); } /* (no nudge at Done: closing the locker is up to you) */",
        "  if (lkOn()) { if (tutBrowseAt && performance.now() - tutBrowseAt < 4200) return tutShow('Take a look around, squirt. Express yourself!', null, 'browse', false, true, null, true); return tutHide(); } /* (no nudge at Back: closing the page is up to you) */")
    for k in ("$('shopGrid').querySelector", "'lkShop', 'shop'", "'lc-face'", "'lkDone'"):
        assert k not in s, k
    return s
