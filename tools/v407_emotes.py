"""v407: victory emotes (the user: "Currently, everyone has the same emotes when they win. They slam down on the ground. On the victory
page. Let's create three other emotes. So you have slam. Let's make two cool ones and a cute one. Users can set this emote in their
locker. Users can purchase new emotes in the shop.").

The winner's moment on the results is now an emote of its own, picked in the locker. All four keep the same beat, landing their big
moment where the slam always landed (so the music and the splat behind the name still hit together):
- Slam (everyone's, free): as before. Down low, a hand reared up and slammed down.
- Backflip (cool): it sinks down, springs up, tucks into a ball through a full backflip and lands hard (the splat and the ring burst
  out from under it), then stands its ground, a hand thrown up.
- Showstopper (cool): winds back, spins twice, faster and faster, ears flared, and stops dead facing you with a hand up high, held
  (a flash and the ring from it), then settles into the menace stance.
- Lovestruck (cute): three happy little bounces, rocking side to side, then a big wave at you, hearts popping out round its head.
Emotes are items (slot 'emote'): an Emotes row in My Locker (Slam always there, a tap on one plays it on you), Emotes in the Paint
Shop (its own filter; trying one on plays it). The one you pick is part of your saved look, and goes out with your look online, so
another player sees your emote when you win; anyone whose look has none (and older versions) slams. CPUs pick one of their own.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

ITEMS_JS = r"""// (v407) the victory emotes: things to buy that are not worn on the body. Slam is everyone's
const EMOTE_ITEMS = [{ id: 'slam', name: 'Slam', slot: 'emote', cat: 'emote', stage: 'blank', desc: 'Down low, a hand reared up and slammed down' },
  { id: 'hearts', name: 'Lovestruck', slot: 'emote', cat: 'emote', stage: 'blank', desc: 'A few happy bounces, a big wave and hearts' },
  { id: 'flip', name: 'Backflip', slot: 'emote', cat: 'emote', stage: 'blank', desc: 'Springs up, tucks into a backflip and lands hard' },
  { id: 'spin', name: 'Showstopper', slot: 'emote', cat: 'emote', stage: 'blank', desc: 'Spins up fast and stops dead, a hand held high' }];
const emOk = v => typeof v === 'string' && EMOTE_ITEMS.some(w => w.id === v) ? v : null;
"""

AFTER_BOUGHT = r"""
OWNED.add('slam'); BOUGHT.add('slam'); Object.assign(PRICES, { hearts: 420, flip: 600, spin: 750 }); // (v407: Slam is everyone's; the others' prices)
"""

# the poses, the cues and the effects (beside the victory code)
POSE_JS = r"""// ---------- (v407) the victory emotes. Each one's time e runs from the end of its drop-in; its big moment at EM_HIT, where the slam
// has always landed. A pose writes the stance (o: the same fields as the victory's own pose) and the body's extras (ip: a flip, a
// roll, a hand, a wave, the ears, a tuck); k scales its height (the locker's window is closer) ----------
const EM_HIT = 0.91, VIC_E0 = VIC_SLAM - EM_HIT;
function emClear(ip) { ip.pitch = 0; ip.roll = 0; ip.hand = 0; ip.wave = 0; ip.earUp = 0; ip.curl = null; }
const EM_POSE = {
  slam(e, o) { const s0 = EM_HIT - 0.44; o.menace = smoothstep(-0.35, 0.1, e);
    if (e > s0 && e < EM_HIT - 0.06) o.slam = smoothstep(s0, EM_HIT - 0.16, e); else if (e >= EM_HIT - 0.06 && e < EM_HIT) o.slam = (EM_HIT - e) / 0.06;
    const k = e - EM_HIT; if (k > 0 && k < 0.5) o.sq += 0.3 * Math.exp(-k * 10) * Math.min(1, k / 0.03);
    o.expr = e > EM_HIT - 0.3 && e < EM_HIT + 0.5 ? 'angry' : 'menace'; },
  // sinks down, springs, a tucked backflip, a hard landing; then its ground held, a hand thrown up
  flip(e, o, ip, k) { const T0 = 0.38; o.menace = smoothstep(EM_HIT + 0.15, EM_HIT + 0.6, e); if (e < 0) return;
    if (e < T0) { const u = e / T0; o.sq = Math.max(o.sq, 0.55 * smoothstep(0, 1, u)); ip.earUp = -0.5 * u; o.expr = 'focus'; }
    else if (e < EM_HIT) { const u = (e - T0) / (EM_HIT - T0); o.hop = 0.8 * k * 4 * u * (1 - u); ip.pitch = -6.2832 * smoothstep(0.06, 0.94, u);
      ip.curl = Math.min(1, 1.7 * Math.sin(Math.PI * clamp((u - 0.08) / 0.84, 0, 1))); o.rise = u < 0.18 ? 0.55 * (1 - u / 0.18) : 0; ip.earUp = 0.8; o.expr = 'glee'; }
    else { const q = e - EM_HIT; o.sq = Math.max(o.sq, 0.75 * Math.exp(-q * 7) * Math.min(1, q / 0.03)); o.expr = q < 0.55 ? 'angry' : 'smirk';
      if (q > 0.85 && q < 1.8) ip.hand = smoothstep(0.85, 1.0, q) * (1 - smoothstep(1.55, 1.8, q)); } },
  // winds back, two spins faster and faster, ears out; stops dead facing you, a hand up high and held, then the menace stance
  spin(e, o, ip, k) { const T0 = 0.25; if (e < 0) return;
    if (e < T0) { const u = smoothstep(0, 1, e / T0); o.sq = 0.35 * u; o.spin = -0.55 * u; o.expr = 'smirk'; }
    else if (e < EM_HIT) { const u = (e - T0) / (EM_HIT - T0); o.spin = -0.55 + (0.55 + 6.2832 * 2) * Math.pow(u, 1.7); o.rise = 0.35 * Math.sin(Math.PI * u); o.hop = 0.12 * k * Math.sin(Math.PI * u); ip.earUp = 0.9 * Math.sin(Math.PI * Math.min(1, u * 1.15)); o.expr = 'glee'; }
    else { const q = e - EM_HIT; o.spin = 6.2832 * 2 + 0.22 * Math.sin(q * 18) * Math.exp(-q * 6); o.slam = smoothstep(0, 0.08, q) * (1 - smoothstep(1.4, 1.75, q)); o.menace = smoothstep(0.1, 0.5, q);
      o.sq = 0.4 * Math.exp(-q * 9) * Math.min(1, q / 0.03); o.expr = q < 1.5 ? 'smirk' : 'menace'; } },
  // three happy bounces rocking side to side; a big wave at you, ears up, hearts
  hearts(e, o, ip, k) { o.menace = 0; if (e < 0) return;
    if (e < EM_HIT) { const ph = e / 0.3, n = Math.floor(ph), u = ph - n; o.hop = n < 3 ? 0.2 * k * Math.sin(Math.PI * u) : 0; o.sq = u > 0.85 ? (u - 0.85) / 0.15 * 0.35 : u < 0.1 ? 0.35 * (1 - u / 0.1) : 0;
      ip.roll = 0.1 * Math.sin(e * 10.5); ip.earUp = 0.5 * Math.sin(Math.PI * u); o.expr = 'glee'; }
    else { const q = e - EM_HIT; ip.wave = smoothstep(0, 0.15, q) * (1 - smoothstep(1.6, 1.9, q)); ip.roll = 0.09 * Math.sin(q * 4.2) * smoothstep(0, 0.3, q); ip.earUp = 0.35;
      o.sq = 0.3 * Math.exp(-q * 8) * Math.min(1, q / 0.03); o.hop = q < 0.25 ? 0.12 * k * Math.sin(Math.PI * q / 0.25) : 0; o.expr = q < 1.9 ? 'cute' : 'content'; } } };
// the sounds and the hearts before and after the big moment (the moment itself: the victory's own, or the locker's)
const EM_CUES = { flip: [[0.38, 'whoosh']], spin: [[0.25, 'whoosh'], [0.62, 'whoosh']], hearts: [[0.3, 'bop'], [0.6, 'bop'], [EM_HIT + 0.45, 'heart'], [EM_HIT + 0.95, 'heart'], [EM_HIT + 1.45, 'heart']] };
function emCueRun(id, e0, e1, fire) { for (const [at, k] of EM_CUES[id] || []) if (e0 < at && e1 >= at) fire(k); }
const EM_HEART = '<svg viewBox="0 0 26 24" aria-hidden="true"><path d="M13 22.2C6.2 17.4 1.6 13.2 1.6 8.1 1.6 4.6 4.3 2 7.6 2c2.2 0 4.2 1.2 5.4 3.1C14.2 3.2 16.2 2 18.4 2c3.3 0 6 2.6 6 6.1 0 5.1-4.6 9.3-11.4 14.1z" fill="#FF5C9A" stroke="#171320" stroke-width="2.2" stroke-linejoin="round"/><path d="M6.4 6.6c.7-1 1.8-1.5 3-1.3" fill="none" stroke="#FFD0E2" stroke-width="2" stroke-linecap="round"/></svg>';
// hearts popping out from a point on the screen, drifting up and away
function emHearts(x, y, n, sc) {
  if (!(x >= 0) || !(y >= 0)) return; for (let i = 0; i < n; i++) { const h = document.createElement('i'), a = (i / Math.max(1, n - 1) - 0.5) * 2;
    h.className = 'emheart'; h.innerHTML = EM_HEART; h.style.left = (x + a * 18) + 'px'; h.style.top = y + 'px';
    h.style.setProperty('--dx', Math.round(a * 46 + (Math.random() - 0.5) * 16) + 'px'); h.style.setProperty('--dy', Math.round(-70 - Math.random() * 40) + 'px'); h.style.setProperty('--r', Math.round(a * 16) + 'deg'); h.style.setProperty('--s', String(sc || 1)); h.style.animationDelay = (i * 0.07).toFixed(2) + 's';
    document.body.appendChild(h); setTimeout(() => h.remove(), 1900); } }
// which emote a winner does: its own (yours, or another player's as their look says), else a CPU's pick for this match
function vicEmOf(D) { const w = lookOf(D), v = w && emOk(w.emote); if (v) return v; if (D === P || NM) return 'slam'; return ['slam', 'slam', 'flip', 'spin', 'hearts', 'slam'][((runId || 0) * 7 + D.team * 5) % 6]; }
// the victory's cues: a whoosh, a bop, hearts round its head
function emVicCue(k, n) { if (!vic) return; if (k === 'whoosh') AU.whoosh(); else if (k === 'bop') AU.pop(); else if (k === 'heart') { const D = vic.feat[0]; vicV.set(D.x, D.y + 0.72, D.z).project(vicCam); emHearts((vicV.x * 0.5 + 0.5) * viewW, (0.5 - vicV.y * 0.5) * viewH, n || 2, 1); if (n) return; AU.pop(); } }
// the icons on their tags
function emIcon(id) {
  const ink = '#171320', g = {
    slam: '<path d="M6 31.5c3-2.4 6.2-3.1 9.4-2.1M34 31.5c-3-2.4-6.2-3.1-9.4-2.1M9 24.5l3.4 2.2M31 24.5l-3.4 2.2" stroke="#FFD23F" stroke-width="2.6" stroke-linecap="round" fill="none"/><ellipse cx="20" cy="33" rx="13" ry="3.4" fill="#FF5C5C" stroke="' + ink + '" stroke-width="2.2"/><path d="M20 4v20" stroke="' + ink + '" stroke-width="7" stroke-linecap="round"/><path d="M20 4v20" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/><path d="M12.5 18.5 20 27l7.5-8.5z" fill="#FFFFFF" stroke="' + ink + '" stroke-width="2.4" stroke-linejoin="round"/>',
    flip: '<path d="M29.6 12.4A11 11 0 1 0 31 22" fill="none" stroke="' + ink + '" stroke-width="7" stroke-linecap="round"/><path d="M29.6 12.4A11 11 0 1 0 31 22" fill="none" stroke="#5BE07E" stroke-width="3.2" stroke-linecap="round"/><path d="M24.5 11.6l6.6 1.6 1.2-6.8" fill="none" stroke="' + ink + '" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="20" cy="18" r="4.2" fill="#FFFFFF" stroke="' + ink + '" stroke-width="2.2"/>',
    spin: '<path d="M20 6.5l3.2 8.3 8.3 3.2-8.3 3.2L20 29.5l-3.2-8.3L8.5 18l8.3-3.2z" fill="#FFD23F" stroke="' + ink + '" stroke-width="2.3" stroke-linejoin="round"/><path d="M6.5 30.5c4.6 3.4 22.4 3.4 27 0M9 9c-3.5 3-4.8 6.4-4.1 10" fill="none" stroke="#7CC8FF" stroke-width="2.6" stroke-linecap="round"/><path d="M31.5 7.5l.9 2.3 2.3.9-2.3.9-.9 2.3-.9-2.3-2.3-.9 2.3-.9z" fill="#FFFFFF"/>',
    hearts: '<g transform="translate(5 8) scale(1.15)">' + EM_HEART.replace(/^<svg[^>]*>|<\/svg>$/g, '') + '</g><g transform="translate(25 4) scale(.48) rotate(14)">' + EM_HEART.replace(/^<svg[^>]*>|<\/svg>$/g, '') + '</g>' }[id] || '';
  return '<svg class="emico" viewBox="0 0 40 40" aria-hidden="true">' + g + '</svg>';
}
"""

LOCKER_JS = r"""// (v407) an emote on you in the locker's window: tried on or picked, it plays; its big moment with the window's own rings and bursts
function sgEmote(id) {
  const dur = EM_HIT + 2.15; SGD.act = { k: 'emote', id, dur, t: 0, e: -9 }; SGD.moodT = 0; SGD.fzT = 0; SGD.dV = 0; SGD.dyaw = wrapA(SGD.dyaw); SGD.dyawTo = 0; SGD.dHold = 0;
  DRESS_POKE.until = performance.now() + dur * 1000; AU.pop();
}
function emLocker(a, D, ip) {
  const e = a.t - 0.2, e0 = a.e, o = D.vicPose || (D.vicPose = {}); a.e = e;
  Object.assign(o, { hop: 0, sq: 0, rise: 0, spin: 0, coil: 0, kick: 0, leap: false, side: 1, twirl: 0, ball: false, stand: false, menace: 0, slam: 0, em: a.id, expr: null });
  emClear(ip); (EM_POSE[a.id] || EM_POSE.slam)(e, o, ip, 0.55);
  ip.hop = o.hop; o.hop = 0; SGD.actFace = o.expr || (a.id === 'hearts' ? 'happy' : 'smirk'); // (the hop on the body's own, so the window rises with it)
  emCueRun(a.id, e0, e, k => { if (k === 'whoosh') AU.whoosh(); else if (k === 'bop') AU.pop(); else if (k === 'heart') emStageHearts(2); });
  if (e0 < EM_HIT && e >= EM_HIT) { const c = SGD.A.col;
    if (a.id === 'hearts') { emStageHearts(4); AU.pop(); AU.vox('giggle', 0.8); }
    else if (a.id === 'spin') { sgRing(0, 0, 0.9, 0xFFE23C); sgRing(0, 0, 0.55, 0xFFFFFF); sgFlash('w'); if (!reduceMotion) sgBurst(0, 0, COL_WHITE, 10, 3.6, 2.2); AU.power(); AU.vox('hoh', 0.8); }
    else { sgRing(0, 0, 0.95, TEAMS[0].wet); sgRing(0, 0, 0.55, 0xFFFFFF); if (!reduceMotion) { sgBurst(0, 0, c, 14, 3.8, 2.4); sgShk(0.35); } AU.slam(); AU.splat(1); AU.vox('hyah', 0.7); } }
}
function emStageHearts(n) { const r = $('lkStage').getBoundingClientRect(); if (r.width) emHearts(r.left + r.width / 2, r.top + r.height * 0.36, n, 0.9); }
function emEnd(D) { D.vicPose = null; if (D.ip) emClear(D.ip); }
"""

CSS = """/* (v407) the victory emotes: hearts popping out, and their icons on the tags */
.emheart{position:fixed;z-index:400;width:26px;height:24px;margin:-12px 0 0 -13px;pointer-events:none;opacity:0;animation:emheart 1.5s cubic-bezier(.2,.7,.3,1) forwards}
.emheart svg{display:block;width:100%;height:100%;filter:drop-shadow(0 2px 0 rgba(23,19,32,.3))}
@keyframes emheart{0%{transform:translate(0,0) scale(.2) rotate(var(--r));opacity:0}16%{transform:translate(calc(var(--dx) * .3),-16px) scale(calc(var(--s) * 1.18)) rotate(var(--r));opacity:1}72%{opacity:1}100%{transform:translate(var(--dx),var(--dy)) scale(calc(var(--s) * .8)) rotate(calc(var(--r) * -1));opacity:0}}
@media (prefers-reduced-motion:reduce){.emheart{animation-duration:.9s}}
.lkcard .emico{width:74%;height:auto;max-height:84%}
"""

LK_FI_EMOTE = """LK_FI.emote = '<path d="M17.6 7.2A7 7 0 1 0 18.6 14" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/><path d="M14.2 6.6l4 .9.8-4.1" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="11" r="2.4" fill="#FF7BC8"/>'; // (v407)
"""

def apply(s):
    # the items: emotes beside the eyes (not worn), Slam everyone's, the prices
    s = rep(s, "const EXTRA = [{ id: 'zombie', name: 'Zombie eyes'", ITEMS_JS + "const EXTRA = [{ id: 'zombie', name: 'Zombie eyes'")
    s = rep(s, "stage: 'halloween', gift: 1 }], ITEMS = WEAR.concat(EXTRA);", "stage: 'halloween', gift: 1 }].concat(EMOTE_ITEMS), ITEMS = WEAR.concat(EXTRA);")
    s = rep(s, "const bought = id => BOUGHT.has(id);\n", "const bought = id => BOUGHT.has(id);" + AFTER_BOUGHT)
    s = rep(s, "iris: ['brown', 'blue', 'green', 'violet', 'gold'].includes(l.iris) ? l.iris : 'brown' }; })();",
               "iris: ['brown', 'blue', 'green', 'violet', 'gold'].includes(l.iris) ? l.iris : 'brown', emote: (v => v && (v === 'slam' || BOUGHT.has(v)) ? v : null)(emOk(l.emote)) }; })();")
    # the locker and the shop
    s = rep(s, "const lkWorn = w => w.slot === 'eyes' ? myLook.eyes === w.id : myLook[w.slot] === w.id;",
               "const lkWorn = w => w.slot === 'eyes' ? myLook.eyes === w.id : w.slot === 'emote' ? (myLook.emote || 'slam') === w.id : myLook[w.slot] === w.id;")
    s = rep(s, "function lkPic(w) { if (w.slot === 'eyes')", "function lkPic(w) { if (w.slot === 'emote') return emIcon(w.id); if (w.slot === 'eyes')")
    s = rep(s, "const LK_CAT = { skin: 'Skins', head: 'Headgear', face: 'Facial', cloth: 'Clothing', eyes: 'Eyes' };",
               "const LK_CAT = { skin: 'Skins', head: 'Headgear', face: 'Facial', cloth: 'Clothing', eyes: 'Eyes', emote: 'Emotes' };")
    s = rep(s, "['face', 'Facial'], ['cloth', 'Clothing'], ['eyes', 'Eyes']];\nconst LK_FI", "['face', 'Facial'], ['cloth', 'Clothing'], ['eyes', 'Eyes'], ['emote', 'Emotes']];\nconst LK_FI")
    s = rep(s, "const lkInF = (w, f) =>", LK_FI_EMOTE + "const lkInF = (w, f) =>")
    s = rep(s, "for (const c of ['skin', 'head', 'face', 'cloth', 'eyes'])", "for (const c of ['skin', 'emote', 'head', 'face', 'cloth', 'eyes'])")
    s = rep(s, "  for (const c of ['skin', 'head', 'face', 'cloth']) { const mine = WEAR.filter(",
               "  { const ems = EMOTE_ITEMS.filter(w => bought(w.id)).sort((a, b) => a.id === 'slam' ? -1 : b.id === 'slam' ? 1 : PRICE(a) - PRICE(b)), sale = EMOTE_ITEMS.filter(lkForSale).length; // (v407: your emotes, Slam first)\n"
               "    h += '<p class=\"lksec\">' + LK_CAT.emote + '<i>' + ems.length + '</i></p>' + grid(ems.map(w => lkCard(w, 'mine')).join('')) + (sale ? '<p class=\"lknone\"><button class=\"lkgo\" type=\"button\" data-go=\"shop\" data-f=\"emote\">The Paint Shop has ' + sale + ' more</button></p>' : ''); }\n"
               "  for (const c of ['skin', 'head', 'face', 'cloth']) { const mine = WEAR.filter(")
    s = rep(s, "if (w.slot === 'skin') line = w.desc;", "if (w.slot === 'skin' || w.slot === 'emote') line = w.desc;")
    s = rep(s, "off = w.slot !== 'eyes'; }", "off = w.slot !== 'eyes' && w.slot !== 'emote'; }")
    s = rep(s, "const off = bought(w.id) && lkWorn(w) && w.slot !== 'eyes';", "const off = bought(w.id) && lkWorn(w) && w.slot !== 'eyes' && w.slot !== 'emote';")
    s = rep(s, "else if (off) lkTakeOff(w); else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); lkFreshOff(w.id); } }",
               "else if (off) lkTakeOff(w); else { if (w.slot === 'emote') sgDressReact(w); else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); } lkFreshOff(w.id); } } // (v407: an emote on already plays again)")
    s = rep(s, "  else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); }\n", "  else if (w.slot === 'emote') sgDressReact(w);\n  else { AU.ui(); buzz(4); kick($('lkBan'), 'bump'); }\n")
    s = rep(s, "if (!w || w.slot === 'eyes' || !lkWorn(w)) return;", "if (!w || w.slot === 'eyes' || w.slot === 'emote' || !lkWorn(w)) return;")
    # the locker's window plays it
    s = rep(s, "function sgDressReact(w) {\n  if (!SGD.built) return; sgActEnd(); const D = SGD.A.D;", LOCKER_JS + "function sgDressReact(w) {\n  if (!SGD.built) return; sgActEnd(); if (w.slot === 'emote') return sgEmote(w.id); const D = SGD.A.D;")
    s = rep(s, "function sgActEnd() { const a = SGD.act; SGD.act = null; SGD.actFace = null; if (!a || !SGD.built) return; const ip = SGD.A.D.ip; ip.hop = 0; ip.wave = 0; ip.hand = 0; ip.earUp = 0; ip.sq = null; ip.rise = null; }",
               "function sgActEnd() { const a = SGD.act; SGD.act = null; SGD.actFace = null; if (!a || !SGD.built) return; const ip = SGD.A.D.ip; ip.hop = 0; ip.wave = 0; ip.hand = 0; ip.earUp = 0; ip.sq = null; ip.rise = null; if (a.k === 'emote') emEnd(SGD.A.D); }")
    s = rep(s, "  if (a.k === 'hop') { ip.hop = Math.sin(u * Math.PI) * 0.42;", "  if (a.k === 'emote') emLocker(a, D, ip);\n  else if (a.k === 'hop') { ip.hop = Math.sin(u * Math.PI) * 0.42;")
    # the body takes a pose wherever one is set (the victory, or the locker's window), and its flip and roll at the victory too
    s = rep(s, "vic && D.vicPose", "D.vicPose", 7)
    s = rep(s, "const IPr = state === 'intro' || state === 'play' ? D.ip : null;", "const IPr = state === 'intro' || state === 'play' || D.vicPose ? D.ip : null;")
    # the victory: each winner's emote, its pose, its face, its moment
    s = rep(s, "function vicPose(i, t) {", POSE_JS + "function vicPose(i, t) {")
    s = rep(s, "  o.menace = (vic.happy ? 1 : 0.45) * smoothstep(0.4, 0.85, tt);\n",
               "  { const D = vic.feat[i], em = vic.happy && D.vicEm && D.vicEm !== 'slam' ? D.vicEm : ''; if (D.ip) emClear(D.ip); // (v407: an emote of its own)\n"
               "    if (em) { o.em = em; EM_POSE[em](tt - VIC_E0, o, D.ip, 1); o.rise += 0.045 * Math.sin(t * 2.3) * o.menace; return o; } }\n"
               "  o.menace = (vic.happy ? 1 : 0.45) * smoothstep(0.4, 0.85, tt);\n")
    s = rep(s, "  const side = vic.happy ? (tt < VIC_SLAM - 0.4 ?", "  const em = D.vicPose && D.vicPose.em, side = em ? 0 : vic.happy ? (tt < VIC_SLAM - 0.4 ?")
    s = rep(s, "tgt = two && tt < VIC_SLAM - 0.3 ? toO : toCam", "tgt = two && tt < (em ? 0.6 : VIC_SLAM - 0.3) ? toO : toCam")
    s = rep(s, "  ip.expr = !vic.happy ? 'focus' :", "  ip.expr = em ? D.vicPose.expr || (em === 'hearts' ? 'happy' : 'menace') : !vic.happy ? 'focus' :")
    s = rep(s, "    lookRoot(D).visible = true; vicLayer(D, true);\n", "    lookRoot(D).visible = true; vicLayer(D, true); D.vicEm = vicEmOf(D); // (v407)\n")
    s = rep(s, "  if (vic.happy && !vic.slamAt && t >= VIC_SLAM + 0.1) { vic.slamAt = t; const D = vic.feat[0];\n"
               "    vicV.set(D.x + Math.sin(D.yaw) * 0.3, D.y + 0.05, D.z + Math.cos(D.yaw) * 0.3).project(vicCam); const ux = vicV.x * 0.5 + 0.5, uy = vicV.y * 0.5 + 0.5;\n"
               "    vicU.uShock.value.set(ux, uy, t, 1); vicU.uSplat.value.set(vicU.uCen.value.x, vicU.uCen.value.y + 0.07, t, land ? 0.62 : 0.48); // (the splat bursts out round it, the ring from its hand)\n"
               "    AU.slam(); AU.splat(1.4); AU.vox('hyah'); buzz([45]); }\n",
               "  const em0 = vic.happy ? vic.feat[0].vicEm || 'slam' : ''; // (v407: the lead winner's emote: its cues, and its big moment)\n"
               "  if (em0) { const e = t - 0.1 - VIC_E0, e0 = vic.emE === undefined ? -9 : vic.emE; vic.emE = e; emCueRun(em0, e0, e, k => emVicCue(k)); }\n"
               "  if (vic.happy && !vic.slamAt && t >= VIC_SLAM + 0.1) { vic.slamAt = t; const D = vic.feat[0];\n"
               "    if (em0 === 'hearts') { vic.soft = true; emVicCue('heart', 4); AU.pop(); AU.vox('giggle'); buzz([12, 40, 12]); }\n"
               "    else { const sp = em0 === 'spin', fl = em0 === 'flip';\n"
               "    vicV.set(D.x + (sp || fl ? 0 : Math.sin(D.yaw) * 0.3), D.y + (sp ? 0.45 : 0.05), D.z + (sp || fl ? 0 : Math.cos(D.yaw) * 0.3)).project(vicCam); const ux = vicV.x * 0.5 + 0.5, uy = vicV.y * 0.5 + 0.5;\n"
               "    vicU.uShock.value.set(ux, uy, t, 1); vicU.uSplat.value.set(vicU.uCen.value.x, vicU.uCen.value.y + 0.07, t, land ? 0.62 : 0.48); // (the splat bursts out round it, the ring from its hand)\n"
               "    if (sp) { AU.power(); AU.splat(0.9); AU.vox('hoh'); buzz([25, 30, 45]); } else { AU.slam(); AU.splat(1.4); AU.vox('hyah'); buzz([45]); } } }\n")
    s = rep(s, "vicU.uFlash.value = vic.slamAt && !reduceMotion ? 0.2 *", "vicU.uFlash.value = vic.slamAt && !vic.soft && !reduceMotion ? (em0 === 'spin' ? 0.3 : 0.2) *")
    s = rep(s, "const sk = vic.slamAt ? Math.max", "const sk = vic.slamAt && !vic.soft ? Math.max")
    # online: your emote goes out with your look; theirs comes in with theirs
    s = rep(s, "const frLook = () => ({ c: colorId, e: myLook.eyes, w: frWear() });", "const frLook = () => ({ c: colorId, e: myLook.eyes, w: frWear(), m: myLook.emote || undefined }); // (v407: m, your emote)")
    s = rep(s, "JSON.stringify(frWear());", "JSON.stringify(frWear()) + '|' + (myLook.emote || '');")
    s = rep(s, "NM.ranks.set(D, clamp(L.r | 0, 1, 999) || 1);", "Lk.wearing.emote = emOk(L.m); NM.ranks.set(D, clamp(L.r | 0, 1, 999) || 1);")
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    return s
