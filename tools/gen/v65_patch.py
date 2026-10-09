# V65: the winner screen shows the plain character (never mid-turret or mid-rocket); Customize compressed: the name is a button, the
# accessories sit in three sliding categories (Headgear, Facial, Clothing: one headgear and one piece of clothing at a time, facial
# things mix and match), a locked one says where to find it, and the character is framed bigger; at the start of a match the blob
# leaps out of its basin during the countdown, so it's on the floor and ready at Go; the play camera is a little closer and tipped up
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()
def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:150])
    src = src.replace(old, new)

# ================= the winner screen: its plain self =================
rep("st: 'play', paint: 1, power: null, giantT: 0, slam: false, missile: false, charging: false, flatT: 0, stunT: 0, rollT: 0, immuneT: 0, air: false, vy: 0, exposed: false, dry: false, dilT: 0, spd: 0, turn: 0, squash: 0, wob: 0 });",
    "st: 'play', paint: 1, power: null, giantT: 0, slam: false, missile: false, charging: false, flatT: 0, stunT: 0, rollT: 0, immuneT: 0, air: false, vy: 0, exposed: false, dry: false, dilT: 0, spd: 0, turn: 0, squash: 0, wob: 0, turret: null, rocket: null, tGuard: 0, knockT: 0, flung: false, airSling: false, dashT: 0, dashDir: 0, kx: 0, kz: 0 });")
rep("    const V = D === P ? VP : D.look.V; Object.assign(V.look, { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0 }); V.flatK = 0; V.gk = 1; V.misK = 0; // its plain round self, not mid-roll or still a roller",
    "    const V = D === P ? VP : D.look.V; Object.assign(V.look, { spd: 0, lean: 0, drop: 0, flat: 1, roll: 0 }); V.flatK = 0; V.gk = 1; V.misK = 0; V.turPitch = 0; // its plain round self, not mid-roll or still a roller\n    if (V.slime) V.slime.setForm('slime'); // (and not still a turret, a giant or a rocket)")

# ================= Customize: compact =================
rep('''    <h2 class="ctitle" id="lookTitle">Customize</h2>
    <div class="lgroup"><p class="lhead">Name</p>''', '''    <div class="lktop"><h2 class="ctitle" id="lookTitle">Customize</h2><button class="lnbtn" id="lookNameBtn" type="button" aria-label="Change your name"><span id="lookNameTxt">You</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 19.5l1-4.2L15.4 5.4a1.9 1.9 0 0 1 2.7 0l.5.5a1.9 1.9 0 0 1 0 2.7L8.7 18.5z" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"/><path d="M13.6 7.2l3.2 3.2" stroke="currentColor" stroke-width="2.2"/></svg></button></div>
    <div class="lgroup" hidden><p class="lhead">Name</p>''')
a = src.index('    <div class="lgroup" hidden><p class="lhead">Name</p>'); b = src.index('\n', a)
src = src[:a] + src[b + 1:]  # (the old name field goes)
rep('''    <div class="lgroup"><p class="lhead">Color <b id="lookColor">Red</b></p><div class="swatches" id="swatches" role="group" aria-label="Your color"></div></div>''',
    '''    <div class="swatches" id="swatches" role="group" aria-label="Your color"></div>''')
a = src.index('    <div class="lgroup" hidden><p class="lhead">Eyes <b id="lookEyes">Round</b></p>'); b = src.index('    <button class="btn play sm" id="lookDone" type="button">Done</button>', a)
src = src[:a] + '''    <div class="seg lcats" id="lookCats" role="tablist" aria-label="Accessories"><button class="lcat" type="button" role="tab" id="lc-head" data-cat="head" aria-controls="lookRail" aria-selected="true">Headgear</button><button class="lcat" type="button" role="tab" id="lc-face" data-cat="face" aria-controls="lookRail" aria-selected="false" tabindex="-1">Facial</button><button class="lcat" type="button" role="tab" id="lc-cloth" data-cat="cloth" aria-controls="lookRail" aria-selected="false" tabindex="-1">Clothing</button></div>
    <div class="lrail" id="lookRail" role="tabpanel" aria-labelledby="lc-head"></div>
''' + src[b:]

# the kinds: one headgear at a time, one piece of clothing at a time, facial things mix and match by where they sit
rep("const WEAR_WHERE = { island: 'Palette Island', blank: 'Blank Canvas', halloween: 'the Halloween stages' };",
    "const WEAR_WHERE = { island: 'Palette Island', blank: 'Blank Canvas', halloween: 'the Halloween stages' };\nconst WEAR_CAT = { head: 'head', eye: 'face', lash: 'face', mouth: 'face', side: 'face', neck: 'cloth', back: 'cloth' };\nfor (const w of WEAR) w.cat = WEAR_CAT[w.slot] || 'face';\nlet lookCat = 'head'; // the category open in Customize")

# the sheet: header with the name button, swatches, the three categories, the open one's slider
a = src.index('function renderLook() {'); b = src.index('\nfunction saveLook()', a)
src = src[:a] + r'''function renderLook() {
  const fresh = new Set(store.fresh || []);
  for (const b of document.querySelectorAll('#lookCats .lcat')) { const c = b.dataset.cat, sel = c === lookCat; b.setAttribute('aria-selected', String(sel)); b.tabIndex = sel ? 0 : -1;
    b.classList.toggle('fresh', WEAR.some(w => w.cat === c && owns(w.id) && fresh.has(w.id))); }
  const rail = $('lookRail'); rail.setAttribute('aria-labelledby', 'lc-' + lookCat);
  rail.innerHTML = WEAR.filter(w => w.cat === lookCat).map(w => { const own = owns(w.id), fr = own && fresh.has(w.id);
    return '<button class="ltile' + (own ? '' : ' locked') + (fr ? ' fresh' : '') + '" type="button" data-w="' + w.id + '"' + (own ? ' aria-pressed="' + (myLook[w.slot] === w.id) + '"' : ' aria-disabled="true"') + ' aria-label="' + w.name + (own ? (fr ? ', new' : '') : ', locked') + '"><svg viewBox="0 0 40 40" aria-hidden="true">' + WEAR_ICON[w.id] + '</svg><span class="ltn">' + w.name + '</span>' + (own ? '' : LOCK_ICON) + '</button>'; }).join('');
  railEdge(); $('lookNameTxt').textContent = playerName();
  $('unlockLink').parentNode.hidden = WEAR.every(w => owns(w.id)); // (nothing left to unlock: no link)
}
const LOCK_ICON = '<span class="lk" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M4.5 7V5.2a3.5 3.5 0 0 1 7 0V7" fill="none" stroke="currentColor" stroke-width="2"/><rect x="3" y="7" width="10" height="7.5" rx="2" fill="currentColor"/></svg></span>';
// a soft fade on whichever side of the slider has more to see
function railEdge() { const r = $('lookRail'), max = r.scrollWidth - r.clientWidth; r.classList.toggle('more', max > 4 && r.scrollLeft < max - 4); r.classList.toggle('less', max > 4 && r.scrollLeft > 4); }
$('lookRail').addEventListener('scroll', railEdge, { passive: true });
function openCat(c, focus) { if (c === lookCat) return; AU.init(); AU.ui(); lookCat = c; renderLook(); $('lookRail').scrollLeft = 0; restartCls($('lookRail'), 'in'); if (focus) $('lc-' + c).focus(); }
$('lookCats').addEventListener('click', e => { const b = e.target.closest('.lcat'); if (b) openCat(b.dataset.cat); });
$('lookCats').addEventListener('keydown', e => { const cats = ['head', 'face', 'cloth'], i = cats.indexOf(lookCat); if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); e.stopPropagation(); openCat(cats[(i + (e.key === 'ArrowRight' ? 1 : 2)) % 3], true); } });''' + src[b:]
rep("lookOpen = true; menu.classList.add('looking'); renderSwatches(); renderLook(); lookName.value = cleanName(store.name) || ''; lookName.placeholder = playerName(); lookEl.hidden = false;",
    "lookOpen = true; menu.classList.add('looking'); renderSwatches(); renderLook(); lookEl.hidden = false;")
# the name: a button that opens the name card
rep("""// your name: typed straight into Customize (saved as you go), or a random one from the dice
const lookName = $('lookName');
function saveLookName() { const v = cleanName(lookName.value); if (v && v !== store.name) { store.name = v; save(); paintName(); } }
lookName.addEventListener('input', saveLookName);
lookName.addEventListener('change', () => { saveLookName(); lookName.value = cleanName(store.name) || ''; });
lookName.addEventListener('keydown', e => { e.stopPropagation(); if (e.key === 'Enter' || e.key === 'Escape') { e.preventDefault(); lookName.blur(); } });
$('lookDice').addEventListener('click', () => { AU.init(); AU.pop(); lookName.value = randomName(); saveLookName(); menuReact = 0.7; });""",
"""// your name: a button showing it, opening the name card (with its dice)
$('lookNameBtn').addEventListener('click', () => { AU.init(); AU.ui(); openName(false); });""")
rep("function paintName() { const n = playerName(); NAMES[0] = n; $('nameShow').textContent = store.name ? n : 'Add your name'; }",
    "function paintName() { const n = playerName(); NAMES[0] = n; $('nameShow').textContent = store.name ? n : 'Add your name'; const lt = $('lookNameTxt'); if (lt) lt.textContent = n; }")
rep("$('eyeOpts').addEventListener('click', e => { const b = e.target.closest('.lopt'); if (!b) return; AU.init(); myLook.eyes = b.dataset.e; saveLook(); renderLook(); lookPop(); });\n", "")
# picking: a locked one says where it's found; one headgear and one piece of clothing at a time
rep("""const wearPick = e => { const b = e.target.closest('.lopt'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w);
  if (!owns(w.id)) { AU.nope(); kick(b, 'nope'); note('The ' + w.name.toLowerCase() + ' turns up on ' + WEAR_WHERE[w.stage] + ' now and then. Grab it when you see it.'); return; }
  if (store.fresh && store.fresh.includes(w.id)) store.fresh = store.fresh.filter(x => x !== w.id);
  myLook[w.slot] = myLook[w.slot] === w.id ? null : w.id; saveLook(); renderLook(); lookPop(); heroT = 0;""",
"""const wearPick = e => { const b = e.target.closest('.ltile'); if (!b) return; AU.init(); const w = WEAR.find(x => x.id === b.dataset.w); if (!w) return;
  if (!owns(w.id)) { AU.nope(); kick(b, 'nope'); note('Find the ' + w.name.toLowerCase() + ' on ' + WEAR_WHERE[w.stage] + '.'); return; }
  if (store.fresh && store.fresh.includes(w.id)) store.fresh = store.fresh.filter(x => x !== w.id);
  const on = myLook[w.slot] !== w.id;
  if (on && w.cat !== 'face') for (const o of WEAR) if (o.cat === w.cat && o.slot !== w.slot && myLook[o.slot] === o.id) myLook[o.slot] = null; // (one of each)
  myLook[w.slot] = on ? w.id : null; saveLook(); const sl = $('lookRail').scrollLeft; renderLook(); $('lookRail').scrollLeft = sl; railEdge(); lookPop(); heroT = 0;""")
rep("$('wearOpts').addEventListener('click', wearPick); $('wearIsl').addEventListener('click', wearPick); $('wearBlk').addEventListener('click', wearPick);",
    "$('lookRail').addEventListener('click', wearPick);")
# trying on a new find: Customize opens on its category, scrolled to it
rep("const id = newItem, w = WEAR.find(x => x.id === id); hideNewItem(); if (w) { myLook[w.slot] = w.id; store.fresh = (store.fresh || []).filter(x => x !== id); saveLook(); }",
    "const id = newItem, w = WEAR.find(x => x.id === id); hideNewItem(); if (w) { if (w.cat !== 'face') for (const o of WEAR) if (o.cat === w.cat && o.slot !== w.slot) myLook[o.slot] = null; myLook[w.slot] = w.id; lookCat = w.cat; store.fresh = (store.fresh || []).filter(x => x !== id); saveLook(); }")
rep("  irisClose(() => { end.hidden = true; showMenu(); camSnap = true; irisOpen(); openLook(); }); });",
    "  irisClose(() => { end.hidden = true; showMenu(); camSnap = true; irisOpen(); openLook(); const t = w && $('lookRail').querySelector('[data-w=\"' + w.id + '\"]'); if (t) { const r = $('lookRail'); r.scrollLeft = Math.max(0, t.offsetLeft - (r.clientWidth - t.offsetWidth) / 2); railEdge(); } }); });")
# the character framed bigger in the space above the sheet
rep("if (side) { fw = Math.max(80, k.left - r.left); fh = Hh; tx = fw / 2; ty = Hh * 0.5; } else { fh = Math.max(80, k.top - r.top); fw = W; tx = W / 2; ty = fh * 0.56; }",
    "if (side) { fw = Math.max(80, k.left - r.left); fh = Hh; tx = fw / 2; ty = Hh * 0.5; } else { fh = Math.max(80, k.top - r.top); fw = W; tx = W / 2; ty = fh * 0.55; }")
rep("heroDist = clamp(Math.max(tall * Hh / (2 * tv * 0.6 * fh), wide * W / (2 * tv * asp * 0.7 * fw)), 2.3, 9);",
    "heroDist = clamp(Math.max(tall * Hh / (2 * tv * 0.78 * fh), wide * W / (2 * tv * asp * 0.94 * fw)), 1.65, 9);")
# styles
rep(".lookp{gap:12px;padding-top:16px}\n.lookp .ctitle{font-size:26px}", """.lookp{gap:12px;padding-top:14px}
.lookp .ctitle{font-size:24px;text-align:left;margin:0}
.lktop{display:flex;align-items:center;justify-content:space-between;gap:12px;min-height:44px}
.lnbtn{appearance:none;display:inline-flex;align-items:center;gap:8px;min-width:0;max-width:60%;height:44px;padding:0 13px 0 16px;box-sizing:border-box;border-radius:14px;border:3px solid var(--line);background:var(--bone);color:var(--outline);font:400 19px/1 var(--font-display);cursor:pointer;box-shadow:0 3px 0 var(--line);transition:transform .12s}
.lnbtn span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;padding-top:2px}
.lnbtn svg{flex:none;width:18px;height:18px;color:var(--plum-2)}
.lnbtn:active{transform:translateY(2px);box-shadow:0 1px 0 var(--line)}
.lnbtn:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.seg button[aria-selected="true"]{background:var(--bone);color:var(--outline);box-shadow:0 3px 0 rgba(0,0,0,.45)}
.lcats button{position:relative;min-height:40px;font-size:15px}
.lcat.fresh::after{content:"";position:absolute;top:7px;right:8px;width:8px;height:8px;border-radius:50%;background:var(--gold);box-shadow:0 0 0 2px var(--line)}
.lrail{display:flex;gap:8px;overflow-x:auto;overflow-y:hidden;overscroll-behavior-x:contain;scroll-snap-type:x proximity;scroll-padding-inline:2px;padding:3px 2px 4px;margin:-3px -2px -4px;scrollbar-width:none;touch-action:pan-x}
.lrail::-webkit-scrollbar{display:none}
.lrail.more{-webkit-mask:linear-gradient(90deg,#000 calc(100% - 40px),transparent);mask:linear-gradient(90deg,#000 calc(100% - 40px),transparent)}
.lrail.less{-webkit-mask:linear-gradient(90deg,transparent,#000 40px);mask:linear-gradient(90deg,transparent,#000 40px)}
.lrail.more.less{-webkit-mask:linear-gradient(90deg,transparent,#000 40px,#000 calc(100% - 40px),transparent);mask:linear-gradient(90deg,transparent,#000 40px,#000 calc(100% - 40px),transparent)}
.lrail.in .ltile{animation:tilein .34s cubic-bezier(.2,1.3,.4,1) backwards}
.lrail.in .ltile:nth-child(2){animation-delay:.03s}.lrail.in .ltile:nth-child(3){animation-delay:.06s}.lrail.in .ltile:nth-child(4){animation-delay:.09s}.lrail.in .ltile:nth-child(5){animation-delay:.12s}
@keyframes tilein{from{opacity:0;transform:translateX(22px)}}
.ltile{appearance:none;position:relative;flex:0 0 auto;width:80px;height:80px;scroll-snap-align:start;display:grid;grid-template-rows:1fr auto;justify-items:center;align-items:center;gap:3px;padding:9px 4px 8px;box-sizing:border-box;border-radius:16px;border:2px solid rgba(255,255,255,.1);background:rgba(255,255,255,.05);color:var(--bone);cursor:pointer;transition:transform .15s,border-color .15s,background .15s}
.ltile svg{width:38px;height:38px;display:block}
.ltn{font:800 12px/1 var(--font-ui);color:var(--muted);white-space:nowrap}
.ltile:hover{border-color:rgba(255,255,255,.28)}
.ltile[aria-pressed="true"]{border-color:var(--gold);background:rgba(255,216,107,.14);transform:translateY(-2px)}
.ltile[aria-pressed="true"] .ltn{color:var(--gold)}
.ltile:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.ltile:active{transform:translateY(1px)}
.ltile.locked{background:rgba(0,0,0,.18);border-style:dashed;border-color:rgba(255,255,255,.14)}
.ltile.locked svg{filter:grayscale(1) brightness(.62);opacity:.38}
.ltile.locked .ltn{opacity:.6}
.ltile .lk{position:absolute;right:6px;top:6px;width:17px;height:17px;display:grid;place-items:center;border-radius:6px;background:var(--line);color:var(--muted)}
.ltile .lk svg{width:11px;height:11px;filter:none;opacity:1}
.ltile.fresh::after{content:"";position:absolute;top:6px;right:6px;width:10px;height:10px;border-radius:50%;background:var(--gold);box-shadow:0 0 0 2.5px var(--plum),0 0 10px 2px rgba(255,216,107,.6)}
.ltile.nope,.uform.nope{animation:nope .35s}""")
rep("  .orbptr i,.orbptr.edge i,.giftptr i,.giftptr.edge i,.lopt.fresh::after,", "  .orbptr i,.orbptr.edge i,.giftptr i,.giftptr.edge i,.lopt.fresh::after,.lrail.in .ltile,.ltile.nope,.uform.nope,")

# ================= the start: out of the basin before Go =================
rep("potClaim(p, D.team); p.paintC.copy(TEAM_COLS[D.team]); p.slosh = 0; D.popAt = D === P ? 0.5 : 0.62 + Math.random() * 0.35; continue; }",
    "potClaim(p, D.team); p.paintC.copy(TEAM_COLS[D.team]); p.slosh = 0; D.popAt = D === P ? 0.32 : 0.36 + Math.random() * 0.16; D.leapAt = D.popAt + (D === P ? 0.95 : 0.95 + Math.random() * 0.12); continue; }")
rep("  for (const D of ACTIVE) { const p = basins.get(D); D.stroke++; D.wearOff = true; D.peeked = false;",
    "  for (const D of ACTIVE) { const p = basins.get(D); D.stroke++; D.wearOff = true; D.peeked = false; D.introLeap = null; D.introOut = false;")
# (a quicker look round: one way, the other, ahead, then the leap)
rep("  const yaw = (0.8 * k(0.32, 0.56) - 1.55 * k(0.82, 1.1) + 0.75 * k(1.38, 1.62)) * s;",
    "  const yaw = (0.8 * k(0.16, 0.32) - 1.55 * k(0.42, 0.6) + 0.75 * k(0.7, 0.84)) * s;")
rep("""      continue; }
    D.fV += ((D.fT - D.formK) * 170 - D.fV * 13) * Math.min(rdt, 0.033);""", """      if (D.peeked && introT >= D.leapAt) introLeap(D);
      continue; }
    if (D.introLeap) { introFly(D, rdt); continue; }
    if (D.introOut) { D.squash = Math.max(0, D.squash - rdt * 2.5); D.wob = Math.max(0, D.wob - rdt * 1.4); continue; } // out and waiting for Go
    D.fV += ((D.fT - D.formK) * 170 - D.fV * 13) * Math.min(rdt, 0.033);""")
rep("function goTime() {", r"""// up and out of the basin in the countdown: an arc onto the floor in front, the paint flying off it, a splat in its color where it lands
// (its accessories pop on), then it waits there for Go
function introLeap(D) {
  const p = D.pot, x0 = p.x, z0 = p.z, y0 = p.y + 0.55, x1 = p.x + Math.sin(D.yaw) * LEAP_D, z1 = p.z + Math.cos(D.yaw) * LEAP_D, y1 = Math.max(0, surfaceUnder(x1, z1, p.y + 1, true)), vy = JUMP_V * 1.05;
  const T = (vy + Math.sqrt(vy * vy + 2 * GRAV * Math.max(0, y0 - y1))) / GRAV;
  exitPot(D); Object.assign(D, { x: x0, z: z0, y: y0, vy, air: true, spd: LEAP_D / T, freeLand: false, wob: 0.7, squash: 0.4 });
  D.introLeap = { t: 0, T, x0, z0, y0, x1, z1, y1, vy }; p.slosh = 1.3;
  if (Math.abs(p.x - P.x) + Math.abs(p.z - P.z) < 22) for (let i = 0; i < 12; i++) { const a = Math.random() * 6.283, sp = 0.8 + Math.random() * 1.4; spawnPart(p.x + Math.cos(a) * 0.25, p.y + 0.6, p.z + Math.sin(a) * 0.25, Math.cos(a) * sp + Math.sin(D.yaw) * 1.2, 2 + Math.random() * 2, Math.sin(a) * sp + Math.cos(D.yaw) * 1.2, 0.5, tmat(D), 0.4 + Math.random() * 0.3); }
}
function introFly(D, dt) {
  const L = D.introLeap; L.t += dt; const t = Math.min(L.t, L.T), u = t / L.T;
  D.x = L.x0 + (L.x1 - L.x0) * u; D.z = L.z0 + (L.z1 - L.z0) * u; D.y = Math.max(L.y1, L.y0 + L.vy * t - 0.5 * GRAV * t * t); D.vy = L.vy - GRAV * t;
  if (L.t < L.T) return;
  D.introLeap = null; D.introOut = true; D.y = L.y1; D.vy = 0; D.air = false; D.spd = 0; D.squash = 0.85; D.wob = 0.9;
  if (D.wearOff) { D.wearOff = false; D.wearPop = -0.14; }
  addSplat(D.x, D.y, D.z, D.yaw, SPLAT_R * 1.15, dryClock, false, false, tcode(D)); splash(D, 1.5); sandBurst(D, 0.7); shockwave(D.x, D.y, D.z, 2);
  if (D === P) { AU.land(0.8); AU.splat(1); buzz(12); shake = Math.max(shake, 0.1); } else if (hearable(D)) AU.land(0.4);
}
function goTime() {""")
rep("""  for (const D of ACTIVE) { if (D.st === 'out') continue;
    if (D.pot) { const p = D.pot; exitPot(D);""", """  for (const D of ACTIVE) { if (D.st === 'out') continue;
    if (D.introOut) { D.introOut = false; continue; } // already out and on the floor
    if (D.introLeap) { D.introLeap = null; D.freeLand = true; continue; } // (still coming down: the game takes the rest of the arc)
    if (D.pot) { const p = D.pot; exitPot(D);""")
# the camera follows it out of the basin and settles where the swing round to behind it starts at Go
rep("""  if (P.pot) { const a = P.yaw + 0.66 - 0.14 * t, d = 3.3 - 0.5 * t; dPos.set(P.x + Math.sin(a) * d, gy + 1.62 - 0.22 * t, P.z + Math.cos(a) * d); dLook.set(P.x, gy + 0.62, P.z); }""",
"""  if (P.pot) { const a = P.yaw + 0.66 - 0.14 * t, d = 3.3 - 0.5 * t; dPos.set(P.x + Math.sin(a) * d, gy + 1.62 - 0.22 * t, P.z + Math.cos(a) * d); dLook.set(P.x, gy + 0.62, P.z); }
  else if (P.introLeap || P.introOut) { const u = clamp((introT - (P.leapAt || 0)) / Math.max(0.3, INTRO_AT[3] - (P.leapAt || 0)), 0, 1), e = u * u * (3 - 2 * u), a = P.yaw + 0.12 + 0.45 * (1 - e), d = 2.35 + 0.75 * (1 - e);
    dPos.set(P.x + Math.sin(a) * d, gy + 1.45 + 0.15 * (1 - e), P.z + Math.cos(a) * d); dLook.set(P.x, Math.max(gy, P.y - 0.25) + INTRO_LK, P.z); }""")
# out of the basin it's itself again: no drop shape, no paint coat, not balled up like the drops that fall at Go
rep("U.gDrop.value = D.missile && D.slam ? 0 : state === 'intro' && !D.pot ? 0.62 + 0.08 * Math.sin(clock * 5 + D.team) : L.drop;",
    "U.gDrop.value = D.missile && D.slam ? 0 : state === 'intro' && !D.pot && !D.introLeap && !D.introOut ? 0.62 + 0.08 * Math.sin(clock * 5 + D.team) : L.drop;")
rep("  const soaked = state === 'intro' || D.st === 'hide';", "  const soaked = (state === 'intro' && !D.introLeap && !D.introOut) || D.st === 'hide';")
rep("hover: state === 'intro' && !D.pot, maxBall:", "hover: state === 'intro' && !D.pot && !D.introLeap && !D.introOut, maxBall:")

# ================= the play camera: about 10% closer, tipped up to see more ahead =================
rep("h = 8.8 + camCharge * 3 + look.roll * 1.2", "h = 7.75 + camCharge * 3 + look.roll * 1.2")
rep(", back = 6.1 + camCharge * 1.5 + ko * 3", ", back = 5.65 + camCharge * 1.5 + ko * 3")
rep("const ahead = 2.9 + 0.9 * clamp(P.spd / cfg.speed - 1, 0, 1) + camTur * 4.5", "const ahead = 3.5 + 0.9 * clamp(P.spd / cfg.speed - 1, 0, 1) + camTur * 4.5")
rep("dLook.set(P.x + fx * ahead + fz * look.lean * -0.5 + fdx * inFront, gyCam - 0.4,", "dLook.set(P.x + fx * ahead + fz * look.lean * -0.5 + fdx * inFront, gyCam - 0.25,")
open(P, 'w').write(src)
print('ok', len(src))
