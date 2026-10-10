// ---------- onboarding ----------
// Your first match is a lesson on the blank canvas: a coach's tips, the game slowed right down while one is up, the rival keeping its
// distance until you have the pound, and each thing (the roller, the orb, the flower) turning up when it is taught. After it: the shop
// (the flower at half what the match paid, the fangs for the rest), the locker to wear them, and the vote before a real match, which
// always lands on a Halloween canvas. Settings can start it over.
if (!store.tut || typeof store.tut !== 'object' || !store.tut.ph) store.tut = { ph: (store.runs || 0) > 0 ? 'done' : 'match' };
const tutHandEl = $('tutHand'), tutEl = $('tut'), tutTxt = $('tutText'), tutCall = $('tutCall'), tutSlowEl = $('tutSlow'), tutDim = $('tutDim'), tutAva = $('tutAva');
let tut = null, tutPrev = null, tutTip = null, tutWinDue = false, tutNiAt = 0; // tutNiAt: when the new item card came up (the coach waits for the item to land) // tutWinDue: the lesson's finish screen is owed, before the tally // tut: the scripted match; tutPrev: the mode, level and canvas to put back after it; tutTip: the tip up now
const tutPh = () => store.tut.ph, tutSet = ph => { if (store.tut.ph === ph) return; store.tut.ph = ph; save(); };
const tutMatchDue = () => tutPh() === 'match';
const TUT_SLOW = 0.35, TUT_HALLO = ['crypt', 'cathedral', 'manor'];
const TUT_AI = Object.assign({}, AI_LV.easy, { pound: 0, attack: 0, dodge: 0, evade: 0, orb: 0, grab: 0, hunt: 0, ram: 0, speed: 0.8, steal: 0.7, trap: 0, airSling: 0, coffinHunt: 0, covPound: 0 });
const TUT_AI_FIGHT = { speed: 1.08, dodge: 0, evade: 0 }; // (the dodge lesson: driven straight at you, a touch quicker)
// the dodge lesson's rival: steered at you, and a jump pound once it is close enough and you are on the floor
function tutDrive(D) {
  const dx = P.x - D.x, dz = P.z - D.z, d = Math.hypot(dx, dz); if (D.charging) cancelCharge(D);
  D.steer = D.slam ? 0 : -clamp(wrapA(Math.atan2(dx, dz) - D.yaw) * 3, -1, 1);
  if (!D.air && !D.slam && P.st === 'play' && !P.air && d < 3.4 && d > 0.6 && Math.abs(P.y - D.y) < 0.8 && slamReady(D)) useSlam(D);
}
const TUT_AI_CALM = { speed: 0.8, pound: 0.45, poundR: 1.5, attack: 0.08, hunt: 0.025, dodge: 0, evade: 0 };
// a tip: the coach's plate (an explanation, its face and name) or, with call set, a short line for an action, *the words that matter* in red
function tutShow(text, at, key, call, nodim, side) {
  if (tutTip && tutTip.key === key) return;
  tutTip = { text, at: at || null, key, call: !!call, nodim: !!nodim, side: side || null }; tutEl.dataset.style = call ? 'call' : 'coach'; if (call) tutCall.innerHTML = escAttr(text).replace(/\*([^*]+)\*/g, '<em>$1</em>'); else tutTxt.textContent = text; try { tutAva.innerHTML = '<span class="bico" style="--cd:#8C6A14">' + slimeIcon(0xF2C14E, lookOf(P)) + '</span>'; } catch (e) {} tutEl.hidden = false; tutEl.classList.remove('on'); void tutEl.offsetWidth; tutEl.classList.add('on');
  const el = tutAt(); if (el) tutReveal(el);
  tutPlace(); tutDim.classList.toggle('on', !nodim && state !== 'play'); AU.plop(); // (no dim in a match: the play must stay clear)
}
// bring a card or tile into the middle of its own scroller (the shop grid down, the locker rail across), and nothing else: scrollIntoView would scroll the page too on a phone
function tutReveal(el) {
  const sc = el.closest('.shgrid, .lrail'); if (!sc) return; const r = el.getBoundingClientRect(), g = sc.getBoundingClientRect();
  if (sc.classList.contains('lrail')) sc.scrollLeft += (r.left + r.width / 2) - (g.left + g.width / 2); else sc.scrollTop += (r.top + r.height / 2) - (g.top + g.height / 2);
}
// the loose hand: over a control, fingertip on its top edge
function tutHandAt(el, r0) {
  if (!el) { if (!tutHandEl.hidden) tutHandEl.hidden = true; return; }
  if (!tutHandEl.firstChild) tutHandEl.innerHTML = tutEl.querySelector('.thand').innerHTML;
  const r = el.getBoundingClientRect(), x = (r.left - r0.left + r.width / 2 - 22).toFixed(0) + 'px', y = (r.top - r0.top - 62).toFixed(0) + 'px';
  if (tutHandEl.hidden) tutHandEl.hidden = false; if (tutHandEl.style.left !== x) tutHandEl.style.left = x; if (tutHandEl.style.top !== y) tutHandEl.style.top = y;
}
function tutHide() { tutHandAt(null); if (!tutTip) return; tutTip = null; tutEl.classList.remove('on'); tutEl.hidden = true; tutDim.classList.remove('on'); }
function tutWindow(x, y, w, h) { const x0 = x.toFixed(0), y0 = y.toFixed(0), x1 = (x + w).toFixed(0), y1 = (y + h).toFixed(0), c = x0 + ' ' + y0 + ' ' + x1 + ' ' + y1; if (tutDim.dataset.w === c) return; tutDim.dataset.w = c;
  tutDim.style.clipPath = 'polygon(evenodd,0 0,100% 0,100% 100%,0 100%,0 0,' + x0 + 'px ' + y0 + 'px,' + x0 + 'px ' + y1 + 'px,' + x1 + 'px ' + y1 + 'px,' + x1 + 'px ' + y0 + 'px,' + x0 + 'px ' + y0 + 'px)'; }
const tutAt = () => !tutTip || !tutTip.at ? null : typeof tutTip.at === 'string' ? $(tutTip.at) : typeof tutTip.at === 'function' ? tutTip.at() : tutTip.at;
// the plate sits over what it is about, pointing down at it (or under it, pointing up, when there is no room above); with nothing to point at it sits up top
function tutPlace() {
  if (!tutTip) return; if (window.scrollY || window.scrollX) try { window.scrollTo(0, 0); } catch (e) {} // (a phone's page scroll would put the hand off its mark)
  const el = tutAt(), r0 = stage.getBoundingClientRect(), block = state !== 'play';
  if (state === 'play') { // (in a match: up under the score, the hand loose over the control, no dim)
    if (tutDim.classList.contains('on')) tutDim.classList.remove('on');
    if (tutEl.dataset.pos !== 'play') { tutEl.dataset.pos = 'play'; tutEl.style.cssText = ''; }
    const sc = document.querySelector('#hud .score'), sb = sc && sc.getBoundingClientRect(), t = ((sb && sb.height ? sb.bottom - r0.top : 90) + 10).toFixed(0) + 'px'; if (tutEl.style.top !== t) tutEl.style.top = t;
    tutHandAt(el && !el.closest('[hidden]') && el.getClientRects().length ? el : null, r0); return;
  }
  tutHandAt(null); if (tutDim.classList.contains('block') !== block) tutDim.classList.toggle('block', block); // (between matches only the instructed control takes a tap)
  const vis = el && !el.closest('[hidden]') && el.getClientRects().length > 0;
  if (!vis) { if (tutEl.dataset.pos !== 'top') { tutEl.dataset.pos = 'top'; tutEl.style.cssText = ''; } tutWindow(viewW / 2, viewH / 2, 0, 0); return; }
  const r = el.getBoundingClientRect(), cx = r.left - r0.left + r.width / 2, cw = Math.min(tutEl.offsetWidth, viewW - 24);
  tutWindow(r.left - r0.left - 10, r.top - r0.top - 10, r.width + 20, r.height + 20);
  const ph = tutEl.offsetHeight, roomUp = r.top - r0.top, roomDn = viewH - (r.bottom - r0.top), above = tutTip.side ? tutTip.side === 'above' : roomUp >= ph + 90 || (roomDn < ph + 90 && roomUp > roomDn); // (the side asked for, else whichever has the room)
  const left = clamp(cx - cw / 2, 12, Math.max(12, viewW - cw - 12)); let y = above ? roomUp - 84 : r.bottom - r0.top + 84; // (the hand's fingertip lands on the edge of the thing, not over it)
  y = above ? Math.max(y, ph + 4) : Math.min(y, viewH - ph - 8);
  const pos = above ? 'above' : 'below'; if (tutEl.dataset.pos !== pos) tutEl.dataset.pos = pos;
  const l = left.toFixed(0) + 'px', t = y.toFixed(0) + 'px', ax = (cx - left).toFixed(0) + 'px';
  if (tutEl.style.left !== l) tutEl.style.left = l; if (tutEl.style.top !== t) tutEl.style.top = t; if (tutEl.style.getPropertyValue('--ax') !== ax) tutEl.style.setProperty('--ax', ax);
}
// the lesson, one step at a time: each one says what to do, waits for it (slowed down while it waits), then the next. max: real seconds before it moves on anyway
const TUT_STEPS = [
  { id: 'move', max: 40, enter() { tut.moved = 0; tut.steered = false; tut.jumped = false; tut.lx = P.x; tut.lz = P.z; tut.slowK = TUT_SLOW; tutShow(say('*DRAG* to steer, *TAP* to jump!', '*A* and *D* steer, *SPACE* jumps!'), null, 'move', true); },
    tick() { if (P.st === 'play' && !P.air) tut.moved += Math.hypot(P.x - tut.lx, P.z - tut.lz); tut.lx = P.x; tut.lz = P.z;
      if (Math.abs(steerIn) > 0.3 || keyL || keyR) tut.steered = true; if (P.st === 'play' && P.air && P.vy > 3 && !P.flung && !P.slam) tut.jumped = true; // (a steer and a jump: that is the lesson, done the moment both have happened)
      return (tut.steered && tut.jumped) || tut.moved > 14; } },
  { id: 'free0', max: 99, enter() { tutHide(); tut.slowK = 1; tut.wait = 3.5; }, tick(dt) { tut.wait -= dt; return tut.wait <= 0; } },
  { id: 'sling', max: 40, enter() { tut.slowK = TUT_SLOW; tutShow(say('*HOLD*, *PULL DOWN*, then let go to fling!', 'Hold *S*, then let go to fling!'), null, 'sling', true); },
    tick() { return P.st === 'play' && P.air && P.flung && (P.flingC || 0) > 0.1; } },
  { id: 'free1', max: 99, enter() { tutHide(); tut.slowK = 1; tut.wait = 7; }, tick(dt) { tut.wait -= dt; return tut.wait <= 0; } },
  { id: 'basin', max: 45, enter() { if (P.paint > 0.42) P.paint = 0.42; pingTank(4); tut.slowK = 1; /* (a trip, not a move: full speed) */ tutShow('Low paint! Drop into a *' + potWord().toUpperCase() + '* to refill', 'bar', 'basin', true, true); },
    tick() { return P.st === 'hide'; } },
  { id: 'pound', max: 80, enter() { tut.hidePound = false; tut.keepAway = false; tutGivePound(); tut.kos0 = P.kos; tut.flat0 = P.flatted; tut.slowK = TUT_SLOW; tut.slowT = 3.5; tut.sub = ''; },
    tick(dt) { if (tut.slowT > 0) { tut.slowT -= dt / Math.max(tut.slowK, 0.05); if (tut.slowT <= 0) tut.slowK = 1; }
      if (P.st === 'play' && P.paint < 0.6) P.paint = Math.min(1, P.paint + dt * 1.6); if (P.slamCD > 1.5) P.slamCD = 1.5; // (paint and the pound keep coming back until one lands)
      const near = H.st === 'play' && Math.hypot(H.x - P.x, H.z - P.z) < 11, sub = P.st === 'hide' ? 'burst' : P.air && P.flung && (P.flingC || 0) > 0.15 && near && !P.slam ? 'missile' : 'pound';
      if (sub !== tut.sub) { tut.sub = sub; tutGivePound();
        if (sub === 'burst') tutShow(say('Full tank! Tap *POUND* to burst out', 'Full tank! Press *E* to burst out'), 'slamBtn', 'burst', true);
        else if (sub === 'missile') { tut.slowK = 0.3; tutShow(say('*POUND* now to fire a missile!', 'Press *E* now to fire a missile!'), 'slamBtn', 'missile', true); }
        else { if (tut.slowT <= 0) tut.slowK = 1; tutShow(say('Your Pound splats everything round you. Get close to the rival and tap it!', 'Your Pound (E) splats everything round you. Get close to the rival and press E!'), 'slamBtn', 'pound'); } }
      return P.kos > tut.kos0 || P.flatted > tut.flat0; } },
  { id: 'dodge', max: 60, enter() { Object.assign(TUT_AI, TUT_AI_FIGHT); tut.drive = H; H.slamCD = 0; if (H.paint < 0.8) H.paint = 1; if (H.ai) { H.ai.plan = null; H.ai.path = null; } tut.rolled = false; tut.hits = 0; tut.wasKo = false; tut.slowK = 1; tut.sub = ''; tutShow(say('Rivals pound too. Swipe up just before it lands to dodge', 'Rivals pound too. Shift just before it lands to dodge'), null, 'dodge', false, true); },
    tick() { if (H.st === 'play' && !H.slam && H.slamCD > 1.2) H.slamCD = 1.2; if (H.paint < 0.5) H.paint = 1;
      const d = Math.hypot(H.x - P.x, H.z - P.z), eta = H.slam ? H.slamEta - H.slamT : 9, coming = H.slam && H.st === 'play' && P.st === 'play' && !P.air && d < slamRadius(H) + PR + 2.5;
      if (coming && P.rollT > 0) tut.rolled = true; // (a roll while its pound is in the air: that is the timing)
      if (P.st === 'ko' && !tut.wasKo) tut.hits++; tut.wasKo = P.st === 'ko';
      const now = coming && eta < 0.62; tut.slowK = now ? 0.14 : coming ? 0.45 : 1;
      const sub = now ? 'now' : 'dodge'; if (sub !== tut.sub) { tut.sub = sub; if (now) tutShow(say('*NOW!* Swipe up!', '*NOW!* Shift!'), null, 'dodgenow', true, true); else tutShow(say('Rivals pound too. Swipe up just before it lands to dodge', 'Rivals pound too. Shift just before it lands to dodge'), null, 'dodge', false, true); }
      return (tut.rolled || tut.hits >= 2) && P.st === 'play' && !H.slam; },
    exit() { Object.assign(TUT_AI, TUT_AI_CALM); tut.drive = null; } },
  { id: 'item', max: 50, enter() { tut.items = true; tutSpawnRoller(); tut.slowK = 1; tut.sub = ''; },
    tick() { const sub = P.held === 'roller' ? 'use' : 'grab'; if (sub !== tut.sub) { tut.sub = sub; if (sub === 'grab') { tut.slowK = 1; tutShow('Roll over the *ROLLER* to pick it up!', null, 'item', true, true); } else { tut.slowK = 0.35; tutShow(say('*TAP* the roller to use it!', 'Press *F* to use it!'), 'itemBtn', 'use', true); } }
      return !!(P.power && P.power.type === 'roller'); } },
  { id: 'free2', max: 99, enter() { tutHide(); tut.slowK = 1; tut.wait = 6; }, tick(dt) { tut.wait -= dt; return tut.wait <= 0; } },
  { id: 'orb', max: 55, enter() { orb.spawnT = 0; tut.orbMine = true; tut.hadRocket = false; tut.slowK = 1; tutShow('A special orb! Roll up to it for a super move', null, 'orb', false, true); },
    tick() { if (P.rocket && !tut.hadRocket) { tut.hadRocket = true; tut.slowK = 0.6; tutShow(say('Steer over the rival, then tap Boost', 'Steer over the rival, then press E to boost'), 'slamBtn', 'rocket'); }
      return tut.hadRocket && !P.rocket; },
    exit() { tut.orbMine = false; TUT_AI.orb = 0.35; } },
  { id: 'free3', max: 99, enter() { tutHide(); tut.slowK = 1; tut.wait = 8; }, tick(dt) { tut.wait -= dt; return tut.wait <= 0; } },
  { id: 'rocketdodge', max: 50, enter() { tut.drive = null; if (orb.on) tutOrbOff(); orb.spawnT = 1e9; if (H.st === 'play' && !H.rocket) { H.paint = 1; startRocket(H); } tut.rolled = false; tut.hit = false; tut.wasKo = false; tut.sub = ''; tut.slowK = 1;
      tutShow(say('The rival has a rocket too. When it drops on you, swipe up to roll clear', 'The rival has a rocket too. When it drops on you, press Shift to roll clear'), null, 'rdodge', false, true); },
    tick() { const R = H.rocket, d = Math.hypot(H.x - P.x, H.z - P.z), diving = !!R && R.ph === 'dive' && H.st === 'play' && P.st === 'play' && !P.air && d < 6;
      if (diving && P.rollT > 0) tut.rolled = true; if (P.st === 'ko' && !tut.wasKo) tut.hit = true; tut.wasKo = P.st === 'ko';
      const now = diving && H.y - P.y < 7; tut.slowK = now ? 0.14 : 1;
      const sub = now ? 'now' : 'wait'; if (sub !== tut.sub) { tut.sub = sub; if (now) tutShow(say('*NOW!* Swipe up!', '*NOW!* Shift!'), null, 'rdodgenow', true, true); else tutShow(say('The rival has a rocket too. When it drops on you, swipe up to roll clear', 'The rival has a rocket too. When it drops on you, press Shift to roll clear'), null, 'rdodge', false, true); }
      return (tut.rolled || tut.hit) && !H.rocket && P.st === 'play'; } },
  { id: 'flower', max: 40, enter() { if (orb.on) tutOrbOff(); orb.spawnT = 1e9; gift.id = 'flower'; gift.at = runT; tut.slowK = 1; tutShow('A flower! *GRAB IT* to unlock it!', null, 'flower', true, true); }, tick() { return gift.got; },
    exit() { if (!gift.got) { gift.got = true; gift.on = false; giftM.visible = giftRing.visible = giftBeam.visible = false; unlockItem('flower'); newItem = 'flower'; } orb.spawnT = 8; } },
  { id: 'rest', max: 1e9, enter() { tut.slowK = 1; tut.noTurret = false; if (matchLeft < 28) matchLeft = 28; tut.restT = 6; tutShow('Now beat him and cover as much of the canvas as you can. Bonus points every time you take him out', null, 'rest', false, true); },
    tick(dt) { if (tut.restT > 0) { tut.restT -= dt; if (tut.restT <= 0) tutHide(); } return false; } }
];
const TUT_REST = TUT_STEPS.length - 1;
// the pound handed over ready the moment its tip is up, even mid-cooldown or short of paint
function tutGivePound() { if (P.st !== 'play' && P.st !== 'hide') return; P.slamCD = 0; if (P.paint < POUND_MIN + 0.05) P.paint = 1; }
function tutOrbOff() { orb.on = false; orb.pull = 0; orb.g.visible = false; orb.ring.visible = false; }
function tutSpawnRoller() {
  const spots = POWER_SPOTS.filter(sp => !powers.some(o => Math.hypot(o.x - sp[0], o.z - sp[2]) < 3)); if (!spots.length) return;
  let best = null, bs = 1e9; for (const sp of spots) { const d = Math.hypot(P.x - sp[0], P.z - sp[2]), sc = d < 4 ? d + 20 : d; if (sc < bs) { bs = sc; best = sp; } }
  const pw = { phase: Math.random() * 6, pop: 0, grace: 0, owner: null }; placePower(pw, 'roller', best); powers.push(pw); itemSpawn.last = 'roller'; itemSpawn.t = 12; AU.spot();
}
function tutStep(dt) {
  if (!tut || state !== 'play') return;
  if (tut.step < 0) { if (P.st === 'play' && !P.air && runT > 0.6) tutNext(); return; }
  const s = TUT_STEPS[tut.step]; if (tut.step < TUT_REST && matchLeft < 20) matchLeft = 20; // (the lesson does not run out the clock)
  if (s.tick(dt)) { if (tut.step < TUT_REST && !s.id.startsWith('free')) { popText('Nice!'); AU.pop(); } tutNext(); }
}
function tutNext() { if (!tut) return; const cur = TUT_STEPS[tut.step]; if (cur && cur.exit) cur.exit(); if (tut.step >= TUT_REST) return; tut.step++; tut.st = 0; TUT_STEPS[tut.step].enter(); }
function tutFrame(rdt) {
  if (tut) { if (state === 'play' && tut.step >= 0) { tut.st += rdt; if (tut.st > TUT_STEPS[tut.step].max) tutNext(); } const on = state === 'play' && tut.slowK < 1; if (tutSlowEl.classList.contains('on') !== on) tutSlowEl.classList.toggle('on', on); }
  else { if (tutSlowEl.classList.contains('on')) tutSlowEl.classList.remove('on'); tutMenuTick(); }
  if (tutTip) tutPlace();
}
// the lesson match plays as a duel on the blank canvas against a gentle CPU, whatever the lobby was set to; it all goes back after
function tutPrep() { if (!tutMatchDue()) return; if (!tutPrev) tutPrev = { mode, diff, stageSel }; mode = 'duel'; diff = 'easy'; stageSel = 'blank'; applyMode(); }
function tutRestore() { if (!tutPrev) return; mode = tutPrev.mode; diff = tutPrev.diff; stageSel = tutPrev.stageSel; tutPrev = null; applyMode(); }
function tutBegin() { // (as a match begins)
  if (tutPh() === 'vote') tutSet('match2');
  if (!tutMatchDue()) { tut = null; return; }
  Object.assign(TUT_AI, TUT_AI_CALM, { pound: 0, attack: 0, orb: 0 }); AI = TUT_AI;
  tut = { step: -1, st: 0, slowK: 1, hidePound: true, keepAway: true, items: false, orbMine: false, drive: null, noTurret: true };
  wxLeft = 1e9; orb.spawnT = 1e9; Object.assign(gift, { id: 'flower', on: false, got: false, pop: 0, at: 1e9 }); giftM.visible = giftRing.visible = giftBeam.visible = false;
}
function tutLeave() { tut = null; tutHide(); tutSlowEl.classList.remove('on'); tutRestore(); tutWinDue = false; const tw = $('tutWin'); tw.classList.remove('on'); tw.hidden = true; }
function tutEndMatch() { // (as a match ends)
  if (tut) {
    tut = null; tutHide(); tutSlowEl.classList.remove('on');
    if (!owns('flower')) unlockItem('flower'); if (!newItem) newItem = 'flower';
    store.tut.price = { flower: Math.max(1, Math.round((endInfo.drops || 0) / 2)) }; // (half what this match paid)
    for (const k of ['steer', 'jump', 'hold', 'burst', 'roll', 'pound', 'missile', 'item', 'orb', 'rocket', 'airdash']) store.seen[k] = 1; // (taught: the one-time tips stay down)
    tutSet('shop'); save(); tutWinDue = true; return;
  }
  if (tutPh() === 'match2') { delete store.tut.price; tutSet('done'); save(); }
}
function tutFangsSale() { const t = store.tut.price || (store.tut.price = {}); if (t.fangs >= 0) return; if (!OWNED.has('fangs')) { OWNED.add('fangs'); store.owned = [...OWNED]; } t.fangs = store.drops || 0; save(); if (shopOpen) renderShop(); }
// between matches the coach points the way: the shop for the flower and the fangs, the locker to wear them, then the canvases to vote
function tutMenuTick() {
  const ph = tutPh(); if (menu.classList.contains('tutoring') !== (ph !== 'done')) menu.classList.toggle('tutoring', ph !== 'done'); // (the lesson keeps the lobby simple: no commissions, no how-to)
  if (ph === 'match') { if (state === 'menu' && menuPage === 'home' && !lookOpen && !shopOpen && !irisBusy && setModal.hidden && nameModal.hidden && howModal.hidden) tutShow('Your first match is a lesson. Tap Play', 'homePlay', 'first'); else tutHide(); return; }
  if (ph !== 'shop' && ph !== 'locker' && ph !== 'vote') return tutHide();
  if (state === 'dead') { if (ph === 'shop' && !$('newItem').hidden) { if (!tutNiAt) tutNiAt = performance.now(); if (performance.now() - tutNiAt < 1600) return tutHide(); return tutShow('Tap to see your new flower in the shop', 'niTry', 'ni', false, false, 'below'); } tutNiAt = 0; if (!end.hidden) return tutShow('Head back to the lobby', 'menuBtn', 'tomenu'); return tutHide(); }
  if (state !== 'menu' || building || irisBusy || !setModal.hidden || !nameModal.hidden || !howModal.hidden) return tutHide();
  const card = id => $('shopGrid').querySelector('.shitem[data-w="' + id + '"]'), tile = id => $('lookRail').querySelector('.ltile[data-w="' + id + '"]');
  if (ph === 'shop') {
    if (shopOpen) { if (!bought('flower')) return tutShow('Buy the flower you found. It is half price today', () => card('flower'), 'buyflower');
      if (!bought('fangs')) { tutFangsSale(); return tutShow('It is the Halloween season: fangs are on sale for the rest of your dabs', () => card('fangs'), 'buyfangs'); }
      tutSet('locker'); return; }
    if (lookOpen) return tutShow('Open the Paint Shop', 'lkBal', 'shop');
    if (menuPage === 'worlds') return tutShow('Back to the lobby', 'worldBack', 'back');
    return tutShow('You earned dabs. Open the Paint Shop', 'dabsBtn', 'shop');
  }
  if (ph === 'locker') {
    if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back');
    if (lookOpen) { if (lookCat !== 'face') return tutShow('Open Facial', 'lc-face', 'face'); if (myLook.mouth !== 'fangs') return tutShow('Tap the fangs to wear them', () => tile('fangs'), 'wear'); tutSet('vote'); return tutShow('Looking sharp. Done', 'lookDone', 'done'); }
    if (menuPage === 'worlds') return tutShow('Back to the lobby', 'worldBack', 'back');
    return tutShow('Open your locker to put the fangs on', 'lookBtn', 'locker');
  }
  if (shopOpen) return tutShow('Back to the lobby', 'shopBack', 'back'); if (lookOpen) return tutShow('Done', 'lookDone', 'done');
  if (menuPage === 'worlds') return tutShow('Pick a canvas: that is your vote. Rivals vote too, and one vote is drawn. Then Start', 'startBtn', 'start');
  return tutShow('Time for a real match. Pick a canvas to vote for', 'stageBtn', 'pick');
}
$('tutReplay').addEventListener('click', () => { AU.init(); AU.ui(); store.tut = { ph: 'match' }; save(); closeSettings(); });
// the lesson's finish, in place of the tally for a beat: the canvas through the window, the title, and what was learned ticked off; Next goes on to the tally
const TW_LIST = ['Steering', 'Flinging', 'Refilling', 'The pound', 'Dodging', 'The roller', 'The orb', 'Finding items'];
// (the finish page pulls the camera wide over the canvas, as the results do)
function showTutWin() {
  const el = $('tutWin'); $('twList').innerHTML = TW_LIST.map((t, i) => '<li style="--i:' + i + '"><i><svg viewBox="0 0 24 24"><path d="M4.5 12.5l5 5L20 7"/></svg></i>' + t + '</li>').join('');
  outro = true; outroT = 0; outroBase = Math.round(camYaw / (Math.PI / 2)) * (Math.PI / 2); // (the view pulls back over the whole canvas)
  hud.classList.add('off'); hintEl.classList.remove('on'); el.hidden = false; el.classList.remove('on'); void el.offsetWidth; el.classList.add('on'); AU.fanfare(); setTimeout(() => AU.power(), 500); buzz([20, 40, 20]);
  setTimeout(() => $('twNext').focus({ preventScroll: true }), 80);
}
$('twNext').addEventListener('click', () => { AU.init(); AU.ui(); const el = $('tutWin'); el.classList.remove('on'); setTimeout(() => { el.hidden = true; }, 300); if (state === 'dead') startTally(); });
