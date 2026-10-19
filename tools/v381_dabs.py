"""v381: dabs you can buy, a free spin a day, no ads once you've bought any, and a short ad now and then for everyone else.

- A green + at the end of your dabs (in the lobby, where the Shop tag was; and beside the Locker and Paint Shop's counter) opens Get dabs: four packs bought with Apple's in-app
  purchase, and the day's free spin. A red dot on the + while today's spin is waiting.
- The packs, from what's for sale: every outfit (10,330 dabs, the season's finds counted once found) and every stroke (2,600) come to
  12,930 dabs, and a match pays 30 to 60. So:
    $0.99   400 dabs    (a hat or two)
    $4.99   2,500 dabs
    $9.99   5,500 dabs  (Popular)
    $19.99  12,000 dabs (Best value: nearly the whole catalogue)
  Each step up gives more dabs per dollar (404, 501, 551, 600). The prices shown are Apple's, in the player's own currency, once the app
  has them.
- Any pack bought makes the game ad-free for good: no more short ads, and the Giant's craft (the one stroke still crafted) is instant, as
  is Skip on one already on the bench, with no ad. It's kept in the save, so it follows the player's account to a new phone.
- The daily spin: once a day (from midnight, the phone's time), free. Most spins pay a little: 10 (40%), 20 (28%), 30 (15%), 50 (10%),
  100 (5%) or 150 (2%), about 27 dabs on average, less than one match, so it's a reason to come back without standing in for a pack.
  The dabs are added (and saved) as the wheel starts turning, so closing the app mid-spin loses nothing and can't spin again.
  For a player who hasn't bought dabs, about one day in three the spin plays the short ad first (decided once a day, so closing and
  opening the wheel doesn't change it): never on the very first spin, never within 10 minutes of another ad, and only if one is
  already loaded (no waiting: without one the wheel just spins). It counts as an ad for the matches' count too. Bought dabs: no ad.
- The short ad: one every 10 to 20 matches (a new number each time), after Play and before you pick what to play. Only an
  interstitial picture ad (the AdMob unit set to display only), only if one is already loaded (it never makes you wait), never in the
  tutorial, never for a player who has bought dabs. Any rewarded ad watched (the craft's Skip) starts the count again, so nobody sees
  two ads close together.
- The spin's wheel: Ludo's gold rim with its bulbs (blinking, faster while it turns), a red pin that flicks at each slice, a gold hub to
  tap, light rays turning behind it on a deep purple stage; glossy slices with a dab coin over each amount; the slice that comes up
  flashes and confetti falls.
- The Friends button is a size smaller (74 by 48, was 94 by 62).
- In a browser (no app), the packs show their prices and say they're bought in the iPhone app; the spin works."""

import os, re

HERE = os.path.dirname(os.path.abspath(__file__))

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def art(name):
    return 'data:image/webp;base64,' + open(os.path.join(HERE, 'v381_art', name + '.b64')).read().strip()

PLUS_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4.5v15M4.5 12h15" fill="none" stroke="currentColor" stroke-width="4.2" stroke-linecap="round"/></svg>'
X_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>'

def apply(s):
    # ---- the + by your dabs: the lobby's pill, and the Locker / Paint Shop page's counter
    s = rep(s, '<b id="statDrops">0</b><i class="dshop">Shop</i></span></button>',
               '<b id="statDrops">0</b><i class="dshop">Shop</i></span></button><button class="dplus" id="dabsPlus" type="button" aria-label="Get dabs">' + PLUS_SVG + '<i class="dpdot" hidden></i></button>')
    s = rep(s, '<b id="lkCoinN">0</b></button>',
               '<b id="lkCoinN">0</b></button><button class="dplus lk" id="lkPlus" type="button" aria-label="Get dabs">' + PLUS_SVG + '<i class="dpdot" hidden></i></button>')
    # ---- Get dabs, and the spin, as panels over everything (after the commissions' one)
    s = rep(s, '      <button class="btn play sm" id="commClose" type="button">Back to the studio</button>\n    </div>\n  </div>\n',
               '      <button class="btn play sm" id="commClose" type="button">Back to the studio</button>\n    </div>\n  </div>\n'
               '  <div class="modal" id="dabStore" hidden>\n'
               '    <div class="card dscard" role="dialog" aria-modal="true" aria-labelledby="dsTitle">\n'
               '      <button class="ttx dsx" id="dsX" type="button" aria-label="Close">' + X_SVG + '</button>\n'
               '      <h2 class="ctitle" id="dsTitle">Get dabs</h2>\n'
               '      <div class="dsspin" id="dsSpin"><img class="dswheel" alt="" src="' + art('wheel') + '"><div class="dsst"><b>Daily spin</b><small id="dsSpinNote">Free, once a day</small></div><button class="dsgo" id="dsSpinGo" type="button">Spin</button></div>\n'
               '      <p class="dsnoads" id="dsNoAds"></p>\n'
               '      <div class="dspacks" id="dsPacks"></div>\n'
               '      <p class="dsfine" id="dsFine">Bought with your Apple account. Dabs are for Roll Model only.</p>\n'
               '      <p class="dstoast" id="dsToast" role="status" hidden></p>\n'
               '    </div>\n'
               '  </div>\n'
               '  <div class="modal" id="spinModal" hidden>\n'
               '    <div class="card spcard" role="dialog" aria-modal="true" aria-labelledby="spTitle">\n'
               '      <h2 class="ctitle" id="spTitle">Daily spin</h2>\n'
               '      <div class="spstage"><i class="sprays" aria-hidden="true"></i><div class="spwrap"><svg class="spwheel" id="spWheel" viewBox="-100 -100 200 200" aria-hidden="true"></svg><img class="sprim" alt="" src="' + art('rim') + '"><i class="spbulbs" aria-hidden="true"></i><img class="sppin" alt="" src="' + art('pin') + '"><button class="sphub" id="spHub" type="button"><img alt="" src="' + art('hub') + '"><b>Spin</b></button></div><i class="spconf" id="spConf" aria-hidden="true"></i></div>\n'
               '      <p class="spres" id="spRes" aria-live="polite"></p>\n'
               '      <button class="btn play sm" id="spDone" type="button" hidden>Collect</button>\n'
               '    </div>\n'
               '  </div>\n')
    # ---- their looks: the coin flights and the counter copy as the commissions have them, the packs on navy, the price on lime
    m = re.findall(r'\n(#commModal \.(?:cwallet|ccoin)[^\n]*)', s)
    assert len(m) >= 6, len(m)
    copies = '\n'.join(l.replace('#commModal', '#dabStore') + '\n' + l.replace('#commModal', '#spinModal') for l in m)
    s = rep(s, '@media (prefers-reduced-motion:reduce){.comm .cclaim,#commModal .cwallet',
               '/* (v381) the + by your dabs; Get dabs (the packs, the daily spin); the spin */\n'
               + copies + '\n'
               '.dplus{appearance:none;position:relative;flex:none;display:grid;place-items:center;width:34px;height:34px;margin:0 0 0 4px;padding:0;border:2.5px solid #171320;border-radius:9px;background:linear-gradient(#7BE36A,#3FB54A);color:#fff;cursor:pointer;pointer-events:auto;box-shadow:0 3px 0 #171320,inset 0 2px 0 rgba(255,255,255,.45);transform:rotate(-3deg);-webkit-tap-highlight-color:transparent;transition:transform .14s cubic-bezier(.3,1.6,.5,1)}\n'
               '.dplus svg{width:18px;height:18px;filter:drop-shadow(0 1.5px 0 rgba(23,19,32,.55))}\n'
               '.dplus:active{transform:rotate(-3deg) translateY(2px) scale(.95)}.dplus:focus-visible{outline:3px solid var(--gold);outline-offset:3px}\n'
               '#dabsBtn .dshop{display:none}#dabsBtn .dtab{padding-right:26px}#dabsPlus{z-index:2;margin-left:-20px} /* (the Shop tag gone: the + at the end of the pill) */\n'
               '.dplus.lk{position:absolute;z-index:7;width:30px;height:30px;margin:0}\n'
               '.dplus .dpdot{position:absolute;right:-6px;top:-6px;width:13px;height:13px;border:2px solid #171320;border-radius:50%;background:var(--ink);animation:dpdot 1.6s ease-in-out infinite}\n'
               '@keyframes dpdot{50%{transform:scale(1.25)}}\n'
               '#dabStore,#spinModal{z-index:60}\n'
               '#dabStore .dscard{position:relative;width:min(560px,100%);max-height:calc(100% - 8px);overflow:auto;box-sizing:border-box;gap:10px}\n'
               '#dabStore .dsx{position:absolute;right:10px;top:10px}\n'
               '.dsspin{display:flex;align-items:center;gap:12px;padding:8px 12px 8px 8px;border:2.5px solid #171320;border-radius:14px;background:linear-gradient(100deg,#F2C14E,#FFD86B);box-shadow:0 3px 0 #171320}\n'
               '.dsspin .dswheel{flex:none;width:58px;height:58px;filter:drop-shadow(0 2px 0 rgba(23,19,32,.35))}\n'
               '.dsspin.ready .dswheel{animation:dswheel 4s linear infinite}@keyframes dswheel{to{transform:rotate(360deg)}}\n'
               '.dsst{flex:1;min-width:0;display:grid;gap:2px;color:#171320}.dsst b{font:400 20px/1 var(--font-display)}.dsst small{font:800 12.5px/1.2 var(--font-head)}\n'
               '.dsgo{appearance:none;flex:none;min-width:96px;height:42px;padding:0 14px;border:2.5px solid #171320;border-radius:10px;background:linear-gradient(#7BE36A,#3FB54A);color:#fff;font:400 20px/1 var(--font-display);text-shadow:0 2px 0 #171320;box-shadow:0 3px 0 #171320;cursor:pointer}\n'
               '.dsgo:disabled{background:#CFC8BC;color:#6E6878;text-shadow:none;font:900 12px/1.1 var(--font-head);cursor:default}\n'
               '.dsnoads{margin:0;padding:7px 10px;border-radius:10px;background:#171320;color:#F4EEE3;font:800 12.5px/1.3 var(--font-head);text-align:center}\n'
               '.dsnoads b{color:#7BE36A}\n'
               '.dspacks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}\n'
               '@media (min-width:620px){.dspacks{grid-template-columns:repeat(4,minmax(0,1fr))}}\n'
               '.dspack{position:relative;display:grid;justify-items:center;gap:4px;padding:10px 8px 8px;border:2.5px solid #171320;border-radius:14px;background:radial-gradient(circle at 50% 35%,#3A2F63,#1C1633 70%);box-shadow:0 3px 0 #171320;color:#fff;min-width:0}\n'
               '.dspack img{width:min(100%,104px);aspect-ratio:1;object-fit:contain;filter:drop-shadow(0 4px 0 rgba(0,0,0,.35))}\n'
               '.dspack .dsn{display:flex;align-items:center;gap:5px;font:400 24px/1 var(--font-display);text-shadow:0 2px 0 #000}.dspack .dsn svg{width:20px;height:20px}\n'
               '.dspack .dsnm{font:800 11.5px/1.1 var(--font-head);color:#CFC6E6;text-align:center}\n'
               '.dspack .dsbuy{appearance:none;width:100%;height:40px;margin-top:2px;border:2.5px solid #171320;border-radius:10px;background:linear-gradient(#7BE36A,#3FB54A);color:#fff;font:400 20px/1 var(--font-display);text-shadow:0 2px 0 #171320;box-shadow:0 3px 0 #171320;cursor:pointer}\n'
               '.dspack .dsbuy:active{transform:translateY(2px)}.dspack .dsbuy[aria-busy="true"]{opacity:.6}\n'
               '.dspack .dstag{position:absolute;top:-9px;right:-6px;padding:4px 8px 3px;border:2px solid #171320;border-radius:6px;background:var(--gold);color:#171320;font:900 10.5px/1 var(--font-head);letter-spacing:.04em;text-transform:uppercase;transform:rotate(4deg)}\n'
               '.dsfine{margin:0;font:700 11px/1.3 var(--font-head);color:#6E6878;text-align:center}\n'
               '.dstoast{position:sticky;bottom:0;margin:0;padding:9px 12px;border-radius:10px;background:#171320;color:#fff;font:800 13px/1.3 var(--font-head);text-align:center;animation:fadein .2s both}\n'
               '#spinModal .spcard{position:relative;width:min(380px,100%);display:grid;justify-items:center;gap:10px;overflow:hidden}\n'
               '.spstage{position:relative;display:grid;place-items:center;width:calc(100% + 32px);margin:0 -16px;padding:18px 0 14px;background:radial-gradient(circle at 50% 46%,#3C3270 0,#211A45 52%,#120E28 100%);border-block:3px solid #171320;overflow:hidden}\n'
               '.sprays{position:absolute;left:50%;top:46%;width:180%;aspect-ratio:1;translate:-50% -50%;background:repeating-conic-gradient(rgba(255,226,140,.16) 0 9deg,rgba(255,226,140,0) 9deg 22.5deg);-webkit-mask:radial-gradient(circle,#000 18%,transparent 62%);mask:radial-gradient(circle,#000 18%,transparent 62%);animation:sprays 26s linear infinite;pointer-events:none}\n'
               '.spstage.go .sprays{animation-duration:5s}@keyframes sprays{to{rotate:360deg}}\n'
               '.spwrap{position:relative;width:min(300px,76vw,54vh);aspect-ratio:1}\n'
               '.spwrap::before{content:"";position:absolute;inset:4%;border-radius:50%;box-shadow:0 0 40px 10px rgba(255,200,80,.35),0 14px 0 rgba(0,0,0,.35)}\n'
               '.spwheel{position:absolute;left:50%;top:50%;width:66%;height:66%;translate:-50% -50%;overflow:visible}\n'
               '.sprim{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;filter:drop-shadow(0 4px 0 rgba(0,0,0,.35))}\n'
               '.spbulbs{position:absolute;inset:0;border-radius:50%;pointer-events:none;background:radial-gradient(circle,transparent 62%,rgba(255,240,170,.0) 70%,rgba(255,240,170,.55) 78%,transparent 86%);mix-blend-mode:screen;opacity:.5;animation:spbulbs 1.2s ease-in-out infinite}\n'
               '.spstage.go .spbulbs{animation-duration:.25s}@keyframes spbulbs{50%{opacity:.05}}\n'
               '.sppin{position:absolute;left:50%;top:-7%;z-index:3;width:17%;translate:-50% 0;filter:drop-shadow(0 4px 0 rgba(0,0,0,.4));transform-origin:50% 22%}\n'
               '.sppin.tick{animation:sptick .12s ease-out}@keyframes sptick{40%{rotate:-14deg}}\n'
               '.sphub{appearance:none;position:absolute;left:50%;top:50%;z-index:2;width:27%;aspect-ratio:1;translate:-50% -50%;padding:0;border:0;border-radius:50%;background:none;cursor:pointer;filter:drop-shadow(0 4px 0 rgba(0,0,0,.4));transition:scale .15s}\n'
               '.sphub img{position:absolute;inset:0;width:100%;height:100%}\n'
               '.sphub b{position:relative;display:block;font:400 clamp(15px,4.6vw,20px)/1 var(--font-display);color:#fff;text-shadow:0 2px 0 #171320,1.5px 0 0 #171320,-1.5px 0 0 #171320,0 -1.5px 0 #171320;letter-spacing:.02em}\n'
               '.sphub:not(:disabled){animation:sphub 1.1s ease-in-out infinite}@keyframes sphub{50%{scale:1.08}}\n'
               '.sphub:disabled{cursor:default}.sphub:disabled b{opacity:0}\n'
               '.spwin{animation:spwin .32s ease-in-out 4 alternate}@keyframes spwin{to{opacity:.15}}\n'
               '.spconf{position:absolute;inset:0;pointer-events:none;overflow:hidden}\n'
               '.spconf i{position:absolute;top:-12px;width:9px;height:14px;border-radius:2px;animation:spconf 1.6s cubic-bezier(.3,.6,.6,1) forwards}\n'
               '@keyframes spconf{to{transform:translate(var(--dx),420px) rotate(var(--r));opacity:0}}\n'
               '.spres{min-height:1.3em;margin:0;font:400 30px/1.1 var(--font-display);color:#171320;text-align:center}\n'
               '.spres.big{animation:spbig .5s cubic-bezier(.3,1.6,.5,1)}@keyframes spbig{from{transform:scale(.4)}}\n'
               '.gtoast{position:fixed;left:50%;bottom:calc(18px + env(safe-area-inset-bottom,0px));z-index:70;max-width:min(420px,calc(100% - 32px));transform:translateX(-50%);padding:10px 14px;border-radius:10px;background:#171320;color:#fff;font:800 13.5px/1.3 var(--font-head);text-align:center;box-shadow:0 4px 0 rgba(0,0,0,.25);animation:fadein .2s both;pointer-events:none}\n'
               '@media (max-height:520px){#dabStore .dscard{gap:6px;padding-top:10px;padding-bottom:10px}#dabStore .ctitle{font-size:22px}.dsspin{padding:4px 10px 4px 6px}.dsspin .dswheel{width:40px;height:40px}.dsgo{height:36px}.dsnoads{padding:5px 8px}.dspack{gap:2px;padding:6px 6px 6px}.dspack img{width:56px}.dspack .dsn{font-size:20px}.dspack .dsbuy{height:34px;font-size:17px}.dsfine{display:none}}\n'
               '@media (prefers-reduced-motion:reduce){.dplus .dpdot,.dsspin.ready .dswheel,.spres.big,.sprays,.spbulbs,.sphub,.sppin.tick,.spwin{animation:none!important}.spconf{display:none}}\n'
               '.friends{width:74px;height:48px;margin-top:24px;padding-bottom:7px;border-radius:10px}.friends .ffaces{top:-24px;width:70px;height:36px}.friends b{font-size:12px} /* (v381: Friends smaller) */\n'
               '@media (max-height:520px) and (min-aspect-ratio:1/1){.friends{margin-top:20px}}\n'
               '@media (prefers-reduced-motion:reduce){.comm .cclaim,#commModal .cwallet')
    # ---- the commissions' counter copy and coin flights, for any panel (the commissions' own stay as they were)
    s = rep(s, "function commWallet(on) {\n  const m = $('commModal'); let w = $('commWallet'); if (!on) { if (w) w.remove(); return; }",
               "function commWallet(on, mid) {\n  const m = $(mid || 'commModal'), wid = mid ? mid + 'Wallet' : 'commWallet'; let w = $(wid); if (!on) { if (w) w.remove(); return; }")
    s = rep(s, "w.id = 'commWallet'; w.removeAttribute('title');", "w.id = wid; w.removeAttribute('title');")
    s = rep(s, "function commCoins(btn, from, to) {\n  const m = $('commModal'), w = $('commWallet'),",
               "function commCoins(btn, from, to, mid) {\n  const m = $(mid || 'commModal'), w = $(mid ? mid + 'Wallet' : 'commWallet'),")
    # ---- bought anything: no ads (the craft's Skip is free), and a craft is done the moment it starts
    s = rep(s, "const adFree = () => ADS.mode === 'none';", "const adFree = () => ADS.mode === 'none' || !!store.paid; // (v381: or dabs bought)")
    s = rep(s, "d.craft = { id, end: Date.now() + sp.craft * 60000 };", "d.craft = { id, end: Date.now() + (store.paid ? 0 : sp.craft * 60000) }; /* (v381: instant once dabs are bought) */")
    # ---- matches counted for the short ad; Play shows it when one's due
    s = rep(s, "store.runs = (store.runs || 0) + 1; if (store.itemIn > 0) store.itemIn--;",
               "store.runs = (store.runs || 0) + 1; if (store.itemIn > 0) store.itemIn--; interCount(); // (v381)", n=2)
    s = rep(s, "if (tutMatchDue()) start(); else openEvents(); })", "if (tutMatchDue()) start(); else playEvents(); })")
    s = rep(s, "function renderLobbyUI() {\n", "function renderLobbyUI() {\n  dsDotPaint(); interWarm(); // (v381)\n")
    s = rep(s, "function openLocker(tab, id) {\n", "function openLocker(tab, id) {\n  setTimeout(lkPlusPlace, 80); setTimeout(lkPlusPlace, 500); // (v381: the + at the end of the counter)\n")
    s = rep(s, "function showDrops() { const n = store.drops || 0;", "function showDrops() { setTimeout(() => { if (typeof lkPlusPlace === 'function') lkPlusPlace(); }, 0); const n = store.drops || 0;")
    # ---- the code
    s = rep(s, "window.addEventListener('nativead', e => adOn((e && e.detail) || {}));\n",
               "window.addEventListener('nativead', e => adOn((e && e.detail) || {}));\n" + JS)
    return s

JS = r"""
// ---------- (v381) dabs to buy, the daily spin, ad-free, and the short ad after Play ----------
// the packs (App Store Connect has these product IDs, as Consumables; the app's PurchaseBridge has the same table)
const DAB_PACKS = [
  { id: 'studio.primeshots.rollmodel.dabs400', n: 400, usd: '$0.99', c: 99, name: 'A handful', art: '""" + "{p1}" + r"""' },
  { id: 'studio.primeshots.rollmodel.dabs2500', n: 2500, usd: '$4.99', c: 499, name: 'A bucketful', art: '""" + "{p2}" + r"""' },
  { id: 'studio.primeshots.rollmodel.dabs5500', n: 5500, usd: '$9.99', c: 999, name: 'A crateful', tag: 'Popular', art: '""" + "{p3}" + r"""' },
  { id: 'studio.primeshots.rollmodel.dabs12000', n: 12000, usd: '$19.99', c: 1999, name: 'A treasure chest', tag: 'Best value', art: '""" + "{p4}" + r"""' }];
// the spin: what each slice pays and how likely it is (out of 100); laid round the wheel small, big, small...
const SPIN = [{ n: 10, w: 40, c: '#E3122F' }, { n: 100, w: 5, c: '#2E9BFF' }, { n: 20, w: 28, c: '#F2C14E' }, { n: 150, w: 2, c: '#8E5CFF' }, { n: 30, w: 15, c: '#3FB54A' }, { n: 50, w: 10, c: '#FF8A1F' }];
const IAP = { prices: {}, busy: null, asked: false };
const iapNative = () => !!(window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.iap);
const dayKey = (t) => { const d = t ? new Date(t) : new Date(); return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); };
const spinReady = () => store.spinDay !== dayKey();
function spinWait() { const d = new Date(), m = new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1); const s = Math.max(0, Math.round((m - d) / 1000)), h = Math.floor(s / 3600), mi = Math.floor(s % 3600 / 60); return h ? h + 'h ' + mi + 'm' : mi + 'm'; }
function gToast(msg) { const o = document.querySelector('.gtoast'); if (o) o.remove(); const t = document.createElement('p'); t.className = 'gtoast'; t.setAttribute('role', 'status'); t.textContent = msg; document.body.appendChild(t); setTimeout(() => t.remove(), 3200); }
function dsToast(msg) { const t = $('dsToast'); if ($('dabStore').hidden) return gToast(msg); t.textContent = msg; t.hidden = false; clearTimeout(t._t); t._t = setTimeout(() => { t.hidden = true; }, 3600); }
// the red dot on the +: today's spin is waiting (once the first lessons are done)
function lkPlusPlace() { const c = $('lkCoin'), b = $('lkPlus'); if (!c || !b || !c.offsetParent || !b.offsetParent) return; const cr = c.getBoundingClientRect(), pr = b.offsetParent.getBoundingClientRect(); if (!(cr.width > 0)) return; b.style.left = (cr.left - pr.left - 36).toFixed(0) + 'px'; /* (just left of the counter, which sits in the page's corner) */ b.style.top = (cr.top - pr.top + (cr.height - 30) / 2).toFixed(0) + 'px'; }
function dsDotPaint() { lkPlusPlace(); const on = spinReady() && store.tut && store.tut.ph === 'done'; for (const b of [$('dabsPlus'), $('lkPlus')]) { const d = b && b.querySelector('.dpdot'); if (d) d.hidden = !on; } }
// ---- Get dabs
function dsPaint() {
  const ready = spinReady(), sp = $('dsSpin'); sp.classList.toggle('ready', ready); $('dsSpinGo').disabled = !ready; $('dsSpinGo').textContent = ready ? 'Spin' : 'Back in ' + spinWait();
  $('dsSpinNote').textContent = ready ? 'Free, once a day' : 'Spun today. A new one at midnight';
  $('dsNoAds').innerHTML = store.paid ? '<b>Ad-free.</b> Thanks for backing Roll Model!' : 'Any pack turns the ads off for good, <b>and crafting is instant</b>';
  $('dsPacks').innerHTML = DAB_PACKS.map(p => '<div class="dspack">' + (p.tag ? '<i class="dstag">' + p.tag + '</i>' : '') + '<img alt="" src="' + p.art + '"><b class="dsn">' + DROP_SVG + p.n.toLocaleString('en-US') + '</b><small class="dsnm">' + p.name + '</small>'
    + '<button class="dsbuy" type="button" data-id="' + p.id + '" aria-label="' + p.n + ' dabs for ' + escAttr(IAP.prices[p.id] || p.usd) + '"' + (IAP.busy === p.id ? ' aria-busy="true"' : '') + '>' + escAttr(IAP.prices[p.id] || p.usd) + '</button></div>').join('');
  $('dsFine').textContent = iapNative() ? 'Bought with your Apple account. Dabs are for Roll Model only.' : 'Dab packs are bought in the Roll Model app on iPhone.';
}
function openDabs() { if (!$('spinModal').hidden) return; AU.init(); AU.ui(); iapHello(); dsPaint(); $('dsToast').hidden = true; $('dabStore').hidden = false; commWallet(true, 'dabStore'); stEv({ k: 'view', i: 'dabstore', a: true }); setTimeout(() => $('dsX').focus({ preventScroll: true }), 40); dsWarmSpin(); }
function closeDabs() { $('dabStore').hidden = true; commWallet(false, 'dabStore'); dsDotPaint(); }
$('dabsPlus').addEventListener('click', e => { e.stopPropagation(); if (state !== 'menu') return; openDabs(); });
$('lkPlus').addEventListener('click', e => { e.stopPropagation(); openDabs(); });
$('dsX').addEventListener('click', () => { AU.ui(); closeDabs(); });
$('dabStore').addEventListener('click', e => { if (e.target === $('dabStore')) closeDabs(); });
$('dsSpinGo').addEventListener('click', () => { if (!spinReady()) return; AU.ui(); openSpin(); });
function dsWarmSpin() { if (spinReady() && spinAdDue()) { adHello(); nativeSay('ads', { interWarm: true, kid: adKid() }); } }
$('dsPacks').addEventListener('click', e => { const b = e.target.closest('.dsbuy'); if (!b) return; AU.init(); AU.ui(); iapBuy(b.dataset.id); });
window.addEventListener('resize', () => { lkPlusPlace(); if (!$('dabStore').hidden) commWallet(true, 'dabStore'); if (!$('spinModal').hidden) commWallet(true, 'spinModal'); });
// ---- buying, through the app (Apple's in-app purchase)
function iapHello() { if (IAP.asked || !iapNative()) return; IAP.asked = true; nativeSay('iap', { ready: true }); }
function iapBuy(id) {
  const p = DAB_PACKS.find(x => x.id === id); if (!p) return;
  if (!iapNative()) return dsToast('Dab packs are bought in the Roll Model app on iPhone');
  if (IAP.busy) return; IAP.busy = id; dsPaint(); stEv({ k: 'view', i: 'pack' + p.n, a: true });
  clearTimeout(IAP.t); IAP.t = setTimeout(() => { if (IAP.busy === id) { IAP.busy = null; if (!$('dabStore').hidden) dsPaint(); } }, 90000); // (Apple's sheet left open: the button comes back)
  nativeSay('iap', { buy: id });
}
// a purchase Apple has confirmed: the dabs added and saved, then the app's told to close it (so a crash in between loses nothing, and
// the same purchase is never added twice: the transactions added are remembered)
function iapGot(m) {
  const p = DAB_PACKS.find(x => x.id === m.id), tx = String(m.tx || ''); if (!p || !tx) return;
  const done = store.iapTx || (store.iapTx = []);
  if (!done.includes(tx)) {
    const from = store.drops || 0, was = !!store.paid; store.drops = from + p.n; store.paid = true; done.push(tx); if (done.length > 200) done.splice(0, done.length - 200);
    stEv({ k: 'iap', pr: p.id, c: p.c }); stEv({ k: 'earn', src: 'iap', n: p.n }); save(); showDrops();
    if (!was) { interReset(); sgSkipPaint(); }
    if (!$('dabStore').hidden) { const b = $('dsPacks').querySelector('.dsbuy[data-id="' + p.id + '"]') || $('dsX'); AU.xplay('coins', { v: 0.8 }) || AU.power(); hap('success'); commCoins(b, from, store.drops, 'dabStore'); dsToast('+' + p.n.toLocaleString('en-US') + ' dabs!' + (was ? '' : ' And no more ads.')); }
    else gToast('+' + p.n.toLocaleString('en-US') + ' dabs added' + (was ? '' : '. No more ads!'));
  }
  nativeSay('iap', { finish: tx });
  if (IAP.busy === m.id) IAP.busy = null; if (!$('dabStore').hidden) dsPaint(); renderLobbyUI();
}
function iapOn(m) {
  if (m.e === 'products') { for (const it of m.list || []) if (it && it.id && it.price) IAP.prices[it.id] = String(it.price); if (!$('dabStore').hidden) dsPaint(); return; }
  if (m.e === 'bought') return iapGot(m);
  if (m.e === 'fail') { if (IAP.busy === m.id) IAP.busy = null; if (!$('dabStore').hidden) dsPaint();
    if (m.why === 'pending') dsToast('Waiting for approval. Your dabs arrive as soon as it goes through');
    else if (m.why !== 'cancel') dsToast(m.why === 'unavailable' ? 'The App Store isn’t answering. Try again soon' : 'That didn’t go through. You haven’t been charged'); }
}
window.addEventListener('nativeiap', e => iapOn((e && e.detail) || {}));
// (a purchase made just before the app closed, or approved later by a parent, is handed over once the lobby's up)
setTimeout(iapHello, 2500);
// ---- the daily spin
function spinDraw() {
  const n = SPIN.length, a = 2 * Math.PI / n, R = 100; let defs = '<defs><radialGradient id="spShade" r="1"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".32"/></radialGradient><radialGradient id="spGloss" cx=".5" cy=".18" r=".75"><stop offset="0" stop-color="#fff" stop-opacity=".35"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/></radialGradient><radialGradient id="spCoin" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#FFF0B0"/><stop offset=".55" stop-color="#F2C14E"/><stop offset="1" stop-color="#B07A1C"/></radialGradient>', h = '';
  const shade = (hex, k) => { const c = parseInt(hex.slice(1), 16), f = v => Math.max(0, Math.min(255, Math.round(v * k))); return 'rgb(' + f(c >> 16) + ',' + f(c >> 8 & 255) + ',' + f(c & 255) + ')'; };
  for (let i = 0; i < n; i++) { const g = 'spG' + i; defs += '<radialGradient id="' + g + '" r="1"><stop offset="0" stop-color="' + shade(SPIN[i].c, 1.35) + '"/><stop offset=".7" stop-color="' + SPIN[i].c + '"/><stop offset="1" stop-color="' + shade(SPIN[i].c, .72) + '"/></radialGradient>';
    const a0 = -Math.PI / 2 + (i - 0.5) * a, a1 = a0 + a, p = 'M0 0L' + (Math.cos(a0) * R).toFixed(2) + ' ' + (Math.sin(a0) * R).toFixed(2) + 'A' + R + ' ' + R + ' 0 0 1 ' + (Math.cos(a1) * R).toFixed(2) + ' ' + (Math.sin(a1) * R).toFixed(2) + 'Z';
    h += '<path id="spS' + i + '" d="' + p + '" fill="url(#' + g + ')"/>';
    const am = -90 + i * 360 / n, big = SPIN[i].n >= 100;
    h += '<g transform="rotate(' + am.toFixed(1) + ') translate(60 0) rotate(90)"><circle cy="-15" r="9" fill="url(#spCoin)" stroke="#171320" stroke-width="2"/><path transform="translate(-6 -21) scale(.6)" d="M10 5.2c.9 0 1.3 1.1 2 1.5 1 .5 2.2-.3 2.6.7.4 1-.9 1.6-.9 2.6s1.2 1.6.7 2.5c-.5.9-1.6.2-2.5.6-.8.4-1 1.7-1.9 1.7s-1.1-1.3-2-1.7c-.9-.4-2 .3-2.5-.6s.7-1.5.7-2.5-1.3-1.6-.9-2.6c.4-1 1.6-.2 2.6-.7.7-.4 1.1-1.5 2.1-1.5z" fill="#171320"/>'
      + '<text y="9" text-anchor="middle" dominant-baseline="central" font-family="Bowlby One, Arial Black, sans-serif" font-size="' + (big ? 21 : 25) + '" fill="#fff" stroke="#171320" stroke-width="6" stroke-linejoin="round" paint-order="stroke">' + SPIN[i].n + '</text></g>'; }
  for (let i = 0; i < n; i++) { const t = -Math.PI / 2 + (i - 0.5) * a; h += '<line x1="0" y1="0" x2="' + (Math.cos(t) * R).toFixed(2) + '" y2="' + (Math.sin(t) * R).toFixed(2) + '" stroke="#171320" stroke-width="5"/><line x1="0" y1="0" x2="' + (Math.cos(t) * R).toFixed(2) + '" y2="' + (Math.sin(t) * R).toFixed(2) + '" stroke="#F2C14E" stroke-width="2"/>'; }
  h += '<circle r="' + R + '" fill="url(#spShade)"/><circle r="' + R + '" fill="url(#spGloss)"/><path id="spHi" d="" fill="#fff" opacity="0"/>';
  $('spWheel').innerHTML = defs + '</defs><g id="spRot">' + h + '</g>';
}
// the win: the slice that came up flashes, and confetti in the wheel's colours
function spinWin(i) { const sl = $('spS' + i), hi = $('spHi'); if (sl && hi) { hi.setAttribute('d', sl.getAttribute('d')); hi.removeAttribute('class'); void hi.getBBox; hi.setAttribute('opacity', '.55'); hi.setAttribute('class', 'spwin'); }
  if (reduceMotion) return; const box = $('spConf'); box.innerHTML = ''; for (let k = 0; k < 36; k++) { const e = document.createElement('i'); e.style.left = (Math.random() * 100).toFixed(1) + '%'; e.style.background = SPIN[k % SPIN.length].c; e.style.setProperty('--dx', ((Math.random() - 0.5) * 120).toFixed(0) + 'px'); e.style.setProperty('--r', ((Math.random() - 0.5) * 900).toFixed(0) + 'deg'); e.style.animationDelay = (Math.random() * 0.35).toFixed(2) + 's'; box.appendChild(e); }
  setTimeout(() => { box.innerHTML = ''; }, 2600); }
const SPN = { rot: 0, on: false };
function openSpin() { if (!spinReady()) return; if (spinAdDue()) { adHello(); nativeSay('ads', { interWarm: true, kid: adKid() }); } spinDraw(); $('spRes').textContent = ''; $('spRes').className = 'spres'; $('spDone').hidden = true; $('spHub').disabled = false; $('spConf').innerHTML = ''; $('spinModal').querySelector('.spstage').classList.remove('go');
  SPN.rot = 0; $('spRot').setAttribute('transform', 'rotate(0)'); $('spinModal').hidden = false; commWallet(true, 'spinModal'); setTimeout(() => $('spHub').focus({ preventScroll: true }), 40); }
function closeSpin() { if (SPN.on) return; $('spinModal').hidden = true; commWallet(false, 'spinModal'); dsDotPaint(); if (!$('dabStore').hidden) dsPaint(); }
function spinPick() { let r = Math.random() * SPIN.reduce((t, x) => t + x.w, 0); for (let i = 0; i < SPIN.length; i++) { r -= SPIN[i].w; if (r < 0) return i; } return 0; }
function spinGo() {
  if (SPN.on || !spinReady()) return; SPN.on = true; AU.init(); const i = spinPick(), won = SPIN[i].n, from = store.drops || 0;
  // (paid out and saved now: closing the app mid-spin loses nothing and can't spin again)
  store.spinDay = dayKey(); store.spins = (store.spins || 0) + 1; store.drops = from + won; stEv({ k: 'earn', src: 'spin', n: won }); save();
  $('spHub').disabled = true; $('spinModal').querySelector('.spstage').classList.add('go');
  const n = SPIN.length, seg = 360 / n, jitter = (Math.random() - 0.5) * seg * 0.7, end = 360 * 5 + (360 - i * seg) + jitter, T = reduceMotion ? 0.01 : 4.6, t0 = performance.now(); let last = 0;
  const step = now => { const u = Math.min(1, (now - t0) / 1000 / T), e = 1 - Math.pow(1 - u, 4), r = end * e; SPN.rot = r; $('spRot').setAttribute('transform', 'rotate(' + r.toFixed(2) + ')');
    const k = Math.floor((r + seg / 2) / seg); if (k !== last) { last = k; AU.ui(); if (u < 0.9) buzz(4); const pin = $('spinModal').querySelector('.sppin'); pin.classList.remove('tick'); void pin.offsetWidth; pin.classList.add('tick'); }
    if (u < 1) return requestAnimationFrame(step);
    SPN.on = false; $('spinModal').querySelector('.spstage').classList.remove('go'); spinWin(i); const res = $('spRes'); res.textContent = '+' + won + ' dabs'; res.className = 'spres big'; hap('success'); AU.xplay('coins', { v: 0.8 }) || AU.power();
    commCoins($('spHub'), from, store.drops, 'spinModal'); showDrops(); $('spDone').hidden = false; setTimeout(() => $('spDone').focus({ preventScroll: true }), 60); dsDotPaint(); };
  requestAnimationFrame(step);
}
// (the day's spin, for a player who hasn't bought dabs: about one day in three the short ad comes first; decided once a day, never the
// first spin, never within 10 minutes of another ad, and only one already loaded; it starts the matches' count again too)
const SPIN_AD = 0.34, AD_GAP = 10 * 60000;
function spinAdDue() { if (adFree() || ADS.mode !== 'app') return false; const d = dayKey(); if (!store.spinAd || store.spinAd.day !== d) { store.spinAd = { day: d, ad: (store.spins || 0) > 0 && Math.random() < SPIN_AD }; save(); }
  return !!store.spinAd.ad && Date.now() - (store.adAt || 0) > AD_GAP; }
function spinTap() { if (SPN.on || !spinReady() || INTER.wait) return; AU.init();
  if (!spinAdDue()) return spinGo();
  $('spHub').disabled = true; INTER.then = () => { $('spHub').disabled = false; spinGo(); }; clearTimeout(INTER.wait); INTER.wait = setTimeout(() => { INTER.wait = 0; const f = INTER.then; INTER.then = null; if (f) f(); }, 1200);
  nativeSay('ads', { inter: 'spin', kid: adKid() }); }
$('spHub').addEventListener('click', spinTap);
$('spDone').addEventListener('click', () => { AU.ui(); closeSpin(); });
$('spinModal').addEventListener('click', e => { if (e.target === $('spinModal')) closeSpin(); });
document.addEventListener('keydown', e => { if (e.key !== 'Escape') return; if (!$('spinModal').hidden) closeSpin(); else if (!$('dabStore').hidden) closeDabs(); });
// ---- the short ad after Play: one every 10 to 20 matches, only an interstitial already loaded, never after a rewarded one
const INTER = { wait: 0, warmed: false, then: null };
const interN = () => 10 + Math.floor(Math.random() * 11);
function interReset() { store.adm = 0; store.adn = interN(); INTER.warmed = false; save(); }
function interCount() { if (!(store.adn > 0)) store.adn = interN(); store.adm = (store.adm || 0) + 1; }
const interOk = () => ADS.mode === 'app' && !adFree() && store.tut && store.tut.ph === 'done' && !tutMatchDue();
const interDue = () => interOk() && (store.adm || 0) >= (store.adn || 15) && Date.now() - (store.adAt || 0) > 10 * 60000;
function interWarm() { if (INTER.warmed || !interOk() || (store.adm || 0) < (store.adn || 15) - 1) return; INTER.warmed = true; adHello(); nativeSay('ads', { interWarm: true, kid: adKid() }); }
function playEvents() {
  if (!interDue()) return openEvents();
  INTER.then = openEvents; clearTimeout(INTER.wait); INTER.wait = setTimeout(() => { INTER.wait = 0; const f = INTER.then; INTER.then = null; if (f) f(); }, 1200); // (none on screen by then: on with the game)
  nativeSay('ads', { inter: 'play', kid: adKid() });
}
function interOn(m) {
  const pl = m.p === 'spin' ? 'spin' : 'inter';
  if (m.e === 'open') { clearTimeout(INTER.wait); INTER.wait = -1; interReset(); store.adAt = Date.now(); save(); stEv({ k: 'ad', pl, r: 'shown' }); AU.suspend(true); return; }
  if (m.e === 'close' || m.e === 'fail') { if (m.e === 'fail') stEv({ k: 'ad', pl, r: 'fail' }); if (INTER.wait) { clearTimeout(INTER.wait); INTER.wait = 0; const f = INTER.then; INTER.then = null; if (f) setTimeout(f, m.e === 'close' ? 350 : 0); } }
}
window.addEventListener('nativead', e => { const m = (e && e.detail) || {}; if (m.p === 'inter' || m.p === 'spin') return interOn(m); if (m.e === 'open') { interReset(); store.adAt = Date.now(); save(); } }); // (any rewarded ad starts the count again)
"""

# the pack pictures, put into the code
for k in ('p1', 'p2', 'p3', 'p4'):
    JS = JS.replace('{' + k + '}', art(k))
