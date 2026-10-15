"""v306 (online match): a 1v1 against a person, refereed by the game server (server/).

- The stage comes from the server's seed: both phones run the game's own generator with the same fixed options (no easy mode, no
  avoided look, the seven vote canvases) and send what they built back, and the server compares them before the match starts.
- The start is on the server's clock: the versus card waits for the server's start, then the 3, 2, 1 lands exactly on its Go. Both
  blobs drop onto their spots (no basin intro online: the server places you at your spot).
- Your blob is yours: it moves at once on your phone, and every move goes to the server, which checks it. Your rival is drawn from
  the server's snapshots a moment in the past, smoothly, with its paint trail, hops, rolls, flings and pounds.
- The server decides everything that wins or loses: knock-outs, flattenings, who's in which pot, pots breaking and coming back,
  coverage (the HUD shows the server's numbers), the clock, the weather (its schedule), overtime and the result. Locally the game
  never knocks out, flattens, stuns or rams the rival online.
- No time tricks online (hit-stop, slow motion, the kill cam, pausing): the server runs on real time. Pause shows the menu while the
  match goes on; Leave forfeits.
- No pick-ups, orbs, rare finds or the Swim faster bonus online for now (the server doesn't hand them out yet).
- After the match: the usual tally and winner screen, then Rematch (both have to say yes) or Menu.

The lobby (tools/v306_lobby.py) finds the match and calls netMatchFound(m); this module calls onlineAfterMatch() when the player
is back in the menu."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""
// ---------- (v306) Online: a match against a person, refereed by the game server. Your blob moves at once on your phone and the
// server checks every move; your rival is drawn from the server's snapshots, a moment in the past. The server decides what wins or
// loses (knock-outs, flattenings, pots, coverage, the clock, the result); this side applies its rulings ----------
var NM = null; // the online match under way (null offline)
let netAhead = 0; // (while a frame is stepped in pieces: how much of the frame's time is still to come, in seconds)
const NET_THEMES = ['island', 'blank', 'sewer', 'raft', 'crypt', 'cathedral', 'manor']; // (the same list on every phone: the stage must come out the same)
function netMatchFound(m, net) {
  net = net || (typeof ON === 'object' && ON && ON.net); if (!net || !m || !Array.isArray(m.players)) return;
  const me = m.players.find(p => p.slot === m.you), fo = m.players.find(p => p.slot !== m.you); if (!me || !fo) return;
  if (building || irisBusy) { setTimeout(() => netMatchFound(m, net), 120); return; }
  const prevMode = NM ? NM.prevMode : mode; if (NM && NM.unsub) NM.unsub();
  NM = { net, m, id: m.matchId, slot: m.you, foe: fo.slot, side: me.side, foeSide: fo.side, prevMode, s: null, startAt: 0, endAt: 0, cov: null, wxI: -1, wx: [],
    live: false, foeLive: false, rule: false, selfKo: null, res: null, corr: 0, refused: 0, why: [], phase: 'found', foeRank: 1, unsub: null, t0: performance.now() };
  NM.unsub = netWire(net);
  if (menuPage === 'worlds') { menuPage = 'home'; menu.dataset.page = 'home'; $('mWorld').hidden = true; $('mHome').hidden = false; }
  if (menuPage === 'events') { menuPage = 'home'; menu.dataset.page = 'home'; evEl.hidden = true; $('mHome').hidden = false; } evFrom = false; document.body.classList.remove('evon');
  if (shopOpen) closeShop(true); if (lookOpen) closeLook(); if (!$('friendsModal').hidden) closeFriends();
  mode = 'duel'; applyMode(); H.cpu = false; // (the rival is a person: no CPU mind, no CPU pace)
  netRival(fo);
  AU.init(); AU.music('vs'); menu.classList.add('leaving'); setTimeout(() => menu.classList.remove('leaving'), 900);
  irisClose(() => {
    menu.hidden = true; end.hidden = true; pauseEl.hidden = true; howModal.hidden = true; hideTally();
    if (!NM || NM.id !== m.matchId) return;
    building = true; genWorld(m.seed >>> 0, { easy: false, avoid: null, themes: NET_THEMES, flat: false }); mapUsed = false; clearTimeout(warmQ); warmRender(); building = false;
    netSendLayout(); showVS(beginMatch);
  }, null, 'New canvas');
}
window.netMatchFound = netMatchFound; // (the lobby calls this when the server has found a match)
// the stage as built goes back to the server, which compares everyone's; then you're at your slot's spot, the rival at theirs
function netSendLayout() {
  const L = RMNet.layoutFromStage({ arena: ARENA, boxes: BOXES, ramps: RAMPS, holes: HOLES, pots: POTS.slice(0, VS_CFG.pots), powers: POWER_SPOTS, spawns: [START, CSTART], puddles: RIVALS.slice(0, VS_CFG.rivals) });
  NM.net.sendLayout(L);
  if (NM.slot === 1) { const a = Object.assign({}, START); Object.assign(START, CSTART); Object.assign(CSTART, a); }
}
// the rival as they dressed: their name, paint (set apart from yours if it's the same), eyes, wearables and rank
function netRival(fo) {
  const L = fo.look && typeof fo.look === 'object' ? fo.look : {}, w = L.w && typeof L.w === 'object' ? L.w : {}, ok = (v, slot) => typeof v === 'string' && WEAR.some(x => x.id === v && x.slot === slot) ? v : null;
  NAMES[1] = String(fo.name || 'Rival').slice(0, 16);
  const c = typeof L.c === 'string' && rivalColOf(L.c); if (c) rivalCol[1] = c;
  LH.wearing = { head: ok(w.head, 'head'), back: ok(w.back, 'back'), mouth: ok(w.mouth, 'mouth'), eye: ok(w.eye, 'eye'), side: ok(w.side, 'side'), neck: ok(w.neck, 'neck'), lash: ok(w.lash, 'lash'), arms: ok(w.arms, 'arms'), iris: EYE_KEYS.includes(w.iris) ? w.iris : 'brown', eyes: EYE_STYLES[L.e] ? L.e : 'round' };
  NM.foeRank = clamp(L.r | 0, 1, 999) || 1; teamTint = true; teamHues();
}
// the versus card stays up until the server says go (and at least a moment, to see who it is)
function netVsWait(fn) {
  const t0 = performance.now(), id = NM && NM.id;
  (function check() { if (!NM || NM.id !== id) return; if (NM.s && performance.now() - t0 > 1400) return fn(); setTimeout(check, 100); })();
}
function netWire(net) {
  const offs = [], on = (ev, fn) => offs.push(net.on(ev, m => { if (!NM || NM.net !== net) return; try { fn(m); } catch (e) { frameErr(e); } }));
  on('start', m => { if (m.matchId !== NM.id) return; NM.s = m; NM.startAt = m.startAt; NM.endAt = m.endAt; NM.rules = m.rules || {}; NM.wx = Array.isArray(m.weather) ? m.weather : [];
    for (const q of m.spawns || []) { const S = q.slot === NM.slot ? START : q.slot === NM.foe ? CSTART : null; if (S) Object.assign(S, { x: q.x, z: q.z, yaw: q.yaw }); } });
  on('correction', netCorrect); on('ko', netKo); on('respawn', netRespawn); on('flat', netFlat); on('push', netPush); on('dodged', netDodged);
  on('pot', netPot); on('potEject', netEject); on('act', netFoeAct); on('resume', netResume);
  on('coverage', m => { NM.cov = [+(m.sides || [])[NM.side] || 0, +(m.sides || [])[NM.foeSide] || 0]; });
  on('snapshot', s => { const me = (s.players || []).find(q => q.slot === NM.slot); if (me) NM.srvPaint = me.paint; }); // (the referee's paint meter, for the pound)
  on('overtime', m => { NM.endAt = m.endAt; if (state === 'play') { banner('Overtime!', (m.secs | 0) + ' more seconds', true); AU.horn(); buzz([30, 40, 30]); lastCount = 99; } });
  on('matchEnd', netEnd); on('matchCancelled', netCancelled); on('matchClosed', netClosed); on('rematch', netVotes);
  on('playerAway', m => { if (m.slot === NM.foe && state === 'play') popText(nameOf(H) + ' lost connection'); });
  on('playerBack', m => { if (m.slot === NM.foe && state === 'play') popText(nameOf(H) + ' is back'); });
  on('playerLeft', m => { if (m.slot === NM.foe && state === 'play') banner(nameOf(H) + ' left', 'The match is yours', true); });
  on('close', m => { if (state === 'play' && m && m.willReconnect) popText('Reconnecting…'); });
  return () => { for (const f of offs) f(); };
}
const netNow = () => NM.net.serverNow(), netLeft = () => Math.max(0, (NM.endAt - netNow()) / 1000);
const netBlob = slot => slot === NM.slot ? P : slot === NM.foe ? H : null;
// your moves go to the referee as they happen
function netAct(a, data) {
  if (!NM || !NM.net) return; const nm = NM;
  // where you are right now goes first, so the referee judges the move from here (on a slow frame you may have come
  // a long way since the last report)
  // (stamped with when it happened: inside a long frame, that's before the frame's end)
  const back = netAhead * 1000, ts = nm.net.serverNow() - back;
  if (nm.live && state === 'play' && (P.st === 'play' || P.st === 'hide')) nm.net.sendState(netState(), true, ts);
  nm.net.action(a, Object.assign({ ts, vt: nm.net.renderTime() - back }, data || {})).then(r => { if (NM !== nm || r.ok) return; nm.refused++; nm.why.push(a + ':' + r.reason); if (nm.why.length > 8) nm.why.shift(); if (a === 'enterPot' && P.st === 'hide' && r.reason !== 'disconnected' && r.reason !== 'timeout') netUnPot(r.reason); });
}
// a dive into a pot the referee didn't allow: back where you were, on the ground (no hop out: the server never had you in it)
function netPre() { NM.pre = { x: P.x, y: P.y, z: P.z, yaw: P.yaw, air: P.air }; }
function netUnPot(why) {
  const p = P.pot, q = NM.pre; if (p) { if (p.occ === P) p.occ = null; p.cool = 0.6; p.bounce = 0.6; } P.pot = null; P.st = 'play'; P.stroke++; P.spd = 0; P.vy = 0; P.wob = 1;
  if (q) { P.x = q.x; P.z = q.z; P.yaw = q.yaw; } const g = surfaceUnder(P.x, P.z, (q ? q.y : P.y) + STEP, true); if (g > -Infinity && (!q || !q.air)) { P.y = g; P.air = false; } else { P.y = q ? q.y : P.y; P.air = true; }
  if (P.charging) clearCharge(P); if (why === 'occupied') popText('Taken!');
}
// each frame: where you are, to the server (after you've landed from the drop at Go)
function netFrame() {
  if (!NM || !NM.net) return;
  if (state === 'play' && !NM.live && NM.phase !== 'end' && NM.startAt && P.st === 'play' && !P.air && netNow() >= NM.startAt) NM.live = true;
  if (!NM.live || state !== 'play' || (P.st !== 'play' && P.st !== 'hide')) return;
  NM.net.sendState(netState());
}
const netState = () => ({ x: P.x, y: P.y, z: P.z, yaw: P.yaw, spd: P.st === 'hide' ? 0 : P.spd, vy: P.vy, air: P.air, rolling: P.rollT > 0, charging: P.charging, slam: !!P.slam, hidden: P.st === 'hide', flung: !!P.flung, dry: !!P.dry, missile: !!P.missile, paint: clamp(P.paint, 0, 1), aim: P.charging ? clamp(P.charge || 0, 0, 1) : 0 });
// at Go: no pick-ups online, the rival's rank on its tag, the weather from the start
function netGo() { for (const D of ACTIVE) { D.held = null; D.held2 = null; D.heldT = 0; } H.rank = NM.foeRank; NM.wxI = -1; NM.phase = 'play'; }
// the weather on the server's schedule (the same turns as the game's own: a heat wave and its rain, rain, clear)
function netWeather() {
  const W = NM.wx; if (!W.length || !NM.startAt) return;
  const t = (netNow() - NM.startAt) / 1000; let i = NM.wxI;
  while (i + 1 < W.length && t >= W[i + 1].at) { i++; netWx(W[i], i > 0 ? W[i - 1].ph : 'clear', i + 1 < W.length && t >= W[i + 1].at); }
  NM.wxI = i; if (i >= 0) wxLeft = Math.max(0.01, W[i].at + W[i].dur - t);
}
function netWx(p, prev, quiet) {
  const ph = p.ph, dur = +p.dur || 1;
  if (ph === 'warn') { setWx('warn', dur); if (!quiet) { AU.heatWarn(); wxBanner('Heat wave in ' + SUN_WARN, P.skill === 'repel' ? 'Weather Repel: the heat can’t touch you' : sunsSeen ? '' : 'Hide in a ' + potWord() + ' or the shade', true); } }
  else if (ph === 'sun') { setWx('sun', dur); dryPuddles(); sunsSeen++; hardPhase = true; hardStart = dryClock; if (!quiet) { AU.heatOn(); flashScreen(); } }
  else if (ph === 'dusk') { setWx('dusk', dur); if (!quiet) { AU.dusk(); wxBanner('The heat breaks', sunsSeen > 1 ? '' : 'Hard paint slows you until the rain.'); } }
  else if (ph === 'rain') { setWx('rain', dur); if (prev === 'dusk') rewetAll(); if (!quiet) { AU.thunder(); const n = rainsSeen++; wxBanner('Rain!', prev === 'dusk' ? (n ? '' : 'Hard paint softens') : P.skill === 'repel' ? 'Weather Repel: it rolls right off you' : n ? '' : rainFast(P) ? 'Faster, but your paint thins' : 'Your paint thins'); } rainPuddles(); }
  else { if (hardPhase) rewetAll(); setWx('clear', dur); }
}
// ---- the rival, drawn from the server's snapshots
function netPuppet(D, dt) {
  if (D.wob > 0) D.wob = Math.max(0, D.wob - dt * 2.5); if (D.squash > 0) D.squash = Math.max(0, D.squash - dt * 4.2); if (D.bonkCD > 0) D.bonkCD -= dt;
  if (D.flatT > 0) { D.flatT = Math.max(0, D.flatT - dt); if (D.flatT === 0) { D.squash = 0.9; D.wob = 1; } }
  if (D.st === 'ko' || D.st === 'out') { if (D.rag) ragStep(D, dt); return; } // (gone until the server brings it back)
  const r = NM.net.remote(NM.foe), F = RMNet.FLAGS; if (!r) return;
  if (!NM.foeLive) { if (r.t > NM.startAt + 30) NM.foeLive = true; else return netDrop(D, dt); } // (until its first move after Go: still dropping onto its spot)
  const f = r.flags; D.paint = r.paint; D.immuneT = f & F.IMMUNE ? 0.4 : 0; D.charging = !!(f & F.CHARGE); D.charge = r.aim;
  if (D.st === 'hide') { D.yaw = r.yaw; return; } // (sat in its pot: the server's pot messages move it in and out)
  const px = D.x, pz = D.z, jump = Math.hypot(r.x - px, r.z - pz) > 3, dyaw = wrapA(r.yaw - D.yaw);
  D.x = r.x; D.y = r.y; D.z = r.z; D.yaw = r.yaw; D.turn = dt > 0 ? D.turn * 0.5 + clamp(dyaw / dt, -TURN, TURN) * 0.5 : D.turn; D.spd = Math.max(0, r.spd); D.vy = r.vy;
  const air = !!(f & F.AIR); if (air && !D.air) D.stroke++; else if (!air && D.air && !jump) netLanded(D); D.air = air;
  const roll = !!(f & F.ROLL); if (roll && !D.netRoll) { D.rollT = ROLL_T; if (hearable(D)) AU.dash(); } else if (roll) D.rollT = Math.max(0.02, D.rollT - dt); else D.rollT = 0; D.netRoll = roll;
  const slam = !!(f & F.SLAM); if (slam && !D.slam) { D.slam = true; D.slamT = 0; D.missile = !!(f & F.MISSILE); } else if (!slam && D.slam) { D.slam = false; D.missile = false; } if (D.slam) D.slamT += dt;
  D.flung = !!(f & F.FLUNG); const dry = !!(f & F.DRY); if (dry && !D.dry) { D.dry = true; D.wob = 1; } else if (!dry) D.dry = false;
  netTrail(D, jump ? 0 : Math.hypot(D.x - px, D.z - pz), dt, jump);
}
// its trail, painted here as it goes (just for the look: the score is the server's)
function netTrail(D, moved, dt, gap) {
  if (D.air || D.flatT > 0 || D.dry || D.st !== 'play' || gap) { D.dist = 0; if (!D.netGap) { D.netGap = true; D.stroke++; } return; }
  if (D.netGap) { D.netGap = false; D.stroke++; }
  if (D.flowT > 0) { D.flowT -= dt; D.dist = 0; if (D.flowT <= 0) D.stroke++; return; }
  D.flowK = Math.min(1, (D.flowK === undefined ? 1 : D.flowK) + dt / 0.5); const fk = 0.3 + 0.7 * D.flowK * D.flowK * (3 - 2 * D.flowK);
  D.dist += moved; const fx = D.x + Math.sin(D.yaw) * TRAIL_FWD, fz = D.z + Math.cos(D.yaw) * TRAIL_FWD, fy = hugY(fx, fz, D.y);
  while (D.dist >= SPACING) { D.dist -= SPACING; addPoint(fx, fy, fz, D.yaw, dryClock, D.stroke, (D.rollT > ROLL_T - ROLL_DASH ? 0.45 : 1) * fk, tcode(D), D.rb, [D.x, D.y, D.z]); }
}
function netLanded(D) {
  D.squash = 0.6; if (hearable(D)) AU.land(0.4);
  const fk = D.flingC || 0; if (fk > 0.2 && !D.slam) { const Rr = SPLAT_R * flingSplatK(fk); addSplat(D.x, D.y, D.z, D.yaw, Rr, dryClock, false, false, tcode(D), 0.12 + 0.3 * fk); splash(D, 1 + fk); if (fk > 0.25) shockwave(D.x, D.y, D.z, Rr * 1.1, TEAMS[D.team].wet); }
  D.flingC = 0;
}
// the drop at Go, before the rival's first move arrives
function netDrop(D, dt) {
  if (!D.air) return; D.y += D.vy * dt; D.vy -= GRAV * 1.45 * dt; const g = surfaceUnder(D.x, D.z, D.y + STEP, true);
  if (D.vy <= 0 && g > -Infinity && D.y <= g) { D.y = g; D.vy = 0; D.air = false; D.squash = 0.8;
    if (D.freeLand) { D.freeLand = false; if (D.wearOff) { D.wearOff = false; D.wearPop = -0.14; } addSplat(D.x, D.y, D.z, D.yaw, SPLAT_R * 1.15, dryClock, false, false, tcode(D)); splash(D, 1.5); shockwave(D.x, D.y, D.z, 2); } }
}
// you and the rival touching: land on its head and the referee rules on the stomp (you bounce off at once, as the game does);
// otherwise you just don't pass through it (rams and roll stuns aren't refereed yet, so they're off online)
function netContact() {
  const A = P, B = H; if (A.st !== 'play' || B.st !== 'play') return;
  const dx = B.x - A.x, dz = B.z - A.z, d = Math.hypot(dx, dz), dy = A.y - B.y, now = performance.now();
  if (A.air && A.vy < -0.5 && dy > 0.25 && dy < 0.95 && d < PR * 2 && !A.slam && !(A.assistT > 0) && B.flatT <= 0 && !(NM.stompAt > now - 400)) {
    NM.stompAt = now; netAct('stomp', { target: NM.foe }); A.vy = 6.5; A.air = true; A.y = Math.max(A.y, B.y + 0.3); fxLaunch(A, 0.8); return;
  }
  if (d > PR * 2 || Math.abs(dy) > 0.95 || A.air || B.air || B.flatT > 0) return;
  const nx = dx / (d || 1), nz = dz / (d || 1), push = PR * 2 - d + 0.01, x = A.x - nx * push, z = A.z - nz * push;
  if (!blockedAt(x, z, A.y)) { A.x = x; A.z = z; }
  if (A.bonkCD <= 0 && A.spd > 1) { fxKnock(A, -nx, -nz, clamp(A.spd / 10, 0.25, 0.6)); A.spd *= 0.65; A.bonkCD = 0.25; A.squash = Math.max(A.squash, 0.45); A.wob = 1; AU.bonk(0.6); }
}
// ---- the referee's rulings
function netCorrect(m) {
  NM.corr++; if (P.st !== 'play') return;
  if (P.charging) clearCharge(P);
  P.x = m.x; P.y = m.y; P.z = m.z; P.yaw = m.yaw; P.spd = 0; P.vy = 0; P.kx = P.kz = 0; P.slam = false; P.missile = false; P.rollT = 0; P.dashT = 0; P.flung = false; P.flingC = 0; P.stroke++;
  const g = surfaceUnder(P.x, P.z, P.y + STEP, true); P.air = !(g > -Infinity && P.y - g < 0.06); if (!P.air) P.y = g;
}
function netKo(m) {
  const D = netBlob(m.slot), by = netBlob(m.by); if (!D) return;
  if (D.st !== 'ko') { if (D === H && D.st !== 'hide') { D.x = m.x; D.y = m.y; D.z = m.z; } NM.rule = true; try { knockOut(D, m.reason, by); } finally { NM.rule = false; } }
  D.koT = m.respawnAt ? Math.max(0.3, (m.respawnAt - netNow()) / 1000) : 99; if (D === P) NM.selfKo = null;
}
function netRespawn(m) {
  const D = netBlob(m.slot), p = pots[m.pot]; if (!D || !p) return;
  if (D.rag) ragEnd(D); if (D.st === 'hide' && D.pot && D.pot !== p) { D.pot.occ = null; D.pot = null; }
  if (p.st !== 'up') { p.next = [p.x, p.y, p.z]; riseCoffin(p); p.st = 'up'; } p.ink = Math.max(p.ink, 1);
  D.immuneT = Math.max(0.5, (m.immuneUntil - netNow()) / 1000); D.vy = 0; D.air = false; D.slam = false; D.spd = 0; D.flatT = 0; D.paint = Math.max(D.paint, 0.5); p.cool = 0; D.spawnImm = true; D.flowArm = true; D.st = 'play';
  enterPot(D, p); const R = startRoom(p, true); D.yaw = R.run >= 3.4 ? R.yaw : potRun(p, 9).yaw;
  if (D === P) { drop.visible = true; camYaw = D.yaw; camYawV = 0; camSnap = true; AU.flip(); if (kof) kofOpen(); else flashScreen(); hintEl.classList.remove('on'); } else D.look.drop.visible = true;
  for (let i = 0; i < 16; i++) { const a = Math.random() * 6.283; spawnPart(p.x, p.y + 0.7, p.z, Math.cos(a) * 2.6, 2.5 + Math.random() * 2, Math.sin(a) * 2.6, 0.5, tmat(D), 0.75); }
}
function netFlat(m) {
  const D = netBlob(m.slot), A = netBlob(m.by) || (D === P ? H : P); if (!D) return;
  if (D === P) { P.x = m.x; P.y = m.y; P.z = m.z; P.spd = 0; P.vy = 0; P.air = false; }
  NM.rule = true; try { flatten(D, A, 'stomp'); } finally { NM.rule = false; }
  D.flatT = Math.max(0.2, (m.until - netNow()) / 1000);
}
function netPush(m) {
  if (m.slot !== NM.slot) { if (m.slot === NM.foe) { H.wob = 1; H.squash = 0.8; } return; }
  if (P.charging) clearCharge(P); holdCharge = false; slingOff();
  P.yaw = Math.atan2(m.dx, m.dz); P.spd = m.spd; P.vy = m.vy; P.air = true; P.stroke++; P.slam = false; P.missile = false; P.flatT = 0; P.turn = 0; P.knockT = 0.9; P.flung = false; P.flingC = 0; P.wob = 1; P.squash = 0.8;
  P.lastHit = m.by === NM.foe ? { by: H, t: runT } : null; fxTumble(P, 0.8, Math.random() - 0.5); shake = Math.max(shake, 0.45); buzz([30, 20, 30]); banner(m.why === 'burst' ? 'Blasted!' : 'Knocked back!');
}
function netDodged(m) { const D = netBlob(m.slot), A = netBlob(m.by); if (D && A && D.st !== 'ko') dodgedPound(D, A); }
function netPot(m) {
  const p = pots[m.i]; if (!p) return;
  if (typeof m.ink === 'number') p.ink = m.ink;
  if (m.up === false) { if (p.occ === H) netFoeOut(p); if (p.st === 'up') sinkCoffin(p); p.next = [p.x, p.y, p.z]; return; }
  if (m.up && p.st !== 'up' && p.st !== 'rise') { p.next = [p.x, p.y, p.z]; riseCoffin(p); }
  if (m.occ === NM.foe) { if (H.pot !== p && H.st !== 'ko' && H.st !== 'out') { if (H.pot) netFoeOut(H.pot); enterPot(H, p); } }
  else if (p.occ === H) netFoeOut(p);
}
function netFoeOut(p) { if (H.pot !== p) return; p.occ = null; p.cool = 1.0; p.bounce = 0.7; H.pot = null; H.st = 'play'; H.stroke++; H.wob = 1; H.spawnImm = false; fxLaunch(H, 0.8); }
function netEject(m) {
  if (m.slot !== NM.slot || P.st !== 'hide') return;
  const by = netBlob(m.by); if (m.why === 'bumped' && by && by !== P) bumpFromCoffin(P, by); else exitPot(P);
}
// the rival's moves, for their effects (where it is comes from the snapshots)
function netFoeAct(m) {
  if (m.slot !== NM.foe) return; const D = H;
  if (m.a === 'jump') fxLaunch(D, 1);
  else if (m.a === 'fling') { const c = clamp(+m.c || 0.5, 0, 1); D.flingC = c; D.flung = true; burst2(D, 10 + (c * 10 | 0)); if (hearable(D)) AU.fling(c * 0.5); }
  else if (m.a === 'pound') { if (D.st === 'hide') netFoeBurst(); else if (hearable(D)) AU.whoosh(); }
  else if (m.a === 'slam') netSlamFx(D, m);
}
// its pound lands: the blast where the server says, in its paint
function netSlamFx(D, m) {
  const R = +m.r || SLAM_R, x = +m.x, y = +m.y, z = +m.z, missile = R > SLAM_R + 0.5;
  coneBlast(x, y, z, R); addSplat(x, y, z, D.yaw, R, dryClock, false, true, tcode(D)); shockwave(x, y, z, R, 0xBFE3FF); shockwave(x, y, z, R * 0.6);
  const sx = D.x, sy = D.y, sz = D.z; D.x = x; D.y = y; D.z = z; splash(D, missile ? 3.5 : 2); burst2(D, missile ? 50 : 30); D.x = sx; D.y = sy; D.z = sz;
  for (const r of rivals) if (r.on && Math.abs(r.y - y) < 0.3 && Math.hypot(r.x - x, r.z - z) < R * 0.5 + r.rad) splashPuddle(r);
  const dp = Math.hypot(x - P.x, z - P.z); if (dp < 18) { shake = Math.max(shake, 0.4 * (1 - dp / 18)); AU.at(x, z); AU.slam(); }
  D.slam = false; D.missile = false; D.squash = 1;
}
// it bursts out of its pot: the pot flies apart (the server breaks it too)
function netFoeBurst() {
  const D = H, p = D.pot; if (!p) return; netFoeOut(p);
  D.air = true; D.y = p.y + 0.35; D.vy = 13.5; D.freeLand = true;
  addSplat(p.x, p.y, p.z, D.yaw, SLAM_R, dryClock, false, true, tcode(D)); shockwave(p.x, p.y, p.z, SLAM_R, 0xBFE3FF); shockwave(p.x, p.y, p.z, SLAM_R * 0.6, TEAMS[D.team].wet);
  breakCoffin(p, D); const dp = Math.hypot(p.x - P.x, p.z - P.z); if (dp < 20) { shake = Math.max(shake, 0.45 * (1 - dp / 20)); AU.at(p.x, p.z); AU.burst(0.6); }
}
// back after a dropped connection: where the server has you
function netResume(m) {
  if (m.matchId !== NM.id || !m.self) return; NM.endAt = m.endAt || NM.endAt;
  if (Array.isArray(m.cov) && m.cov.length) NM.cov = [m.cov[NM.side] || 0, m.cov[NM.foeSide] || 0];
  for (const q of m.pots || []) netPot({ i: q.i, occ: q.occ, up: q.up, ink: q.ink });
  if (state === 'play' && P.st === 'play' && m.self.st === 'play') netCorrect({ x: m.self.x, y: m.self.y, z: m.self.z, yaw: m.self.yaw });
}
// ---- the end, and after
function netEnd(m) {
  if (m.matchId && m.matchId !== NM.id) return; const res = Array.isArray(m.results) ? m.results : [];
  const me = res.find(r => r.slot === NM.slot), fo = res.find(r => r.slot === NM.foe); if (!me || !fo) return;
  NM.res = { win: m.winner < 0 ? 0 : m.winner === NM.side ? 1 : -1, reason: m.reason, m }; NM.cov = [+me.sideCoverage || 0, +fo.sideCoverage || 0]; P.kos = me.kos | 0; H.kos = fo.kos | 0; NM.live = false; NM.phase = 'end';
  if (state !== 'play') { if (state !== 'dead') { popText(m.reason === 'forfeit' ? nameOf(H) + ' left' : 'Match over'); toMenu(); } return; }
  for (const D of ACTIVE) if (D.rag) ragEnd(D);
  endMatch();
  if (m.reason === 'forfeit' && !me.left) setTimeout(() => { if (NM && NM.phase === 'end') banner(nameOf(H) + ' left', 'You win!', true); }, 300);
}
function netCancelled() {
  if (!NM) return; const was = NM.phase; netLeave(); $('vsx').hidden = true; popText(was === 'found' ? 'The match was called off' : 'Match over');
  if (state !== 'menu' || menu.hidden) toMenu();
}
function netClosed(m) { if (!NM) return; NM.closed = true; NM.closedWhy = m && m.reason; if (NM.phase === 'end') netEndButtons(); else if (state === 'play') { popText('Match over'); toMenu(); } }
// the end screen: Rematch (the same rival, if they want it too) or Menu
function netEndButtons() {
  const b = $('endBtn'), wait = NM && NM.voted, gone = !NM || NM.closed; $('replayBtn').hidden = true; $('replayBtn').closest('.row').hidden = false; end.classList.remove('gate');
  if (!b.querySelector('small')) b.innerHTML = '<span>Rematch</span><small></small>';
  b.querySelector('span').textContent = gone ? (NM && NM.closedWhy === 'rematch_timeout' ? 'Rematch closed' : 'Rival left') : wait ? 'Waiting…' : 'Rematch'; b.querySelector('small').textContent = gone ? 'Back to the menu' : wait ? 'for ' + nameOf(H) : NM && NM.foeVote ? nameOf(H) + ' wants one!' : 'Same rival, new canvas'; b.disabled = !!wait && !gone; // (when the rival's gone it takes you back to the menu)
}
function netRematch() { if (!NM || NM.closed) return toMenu(); if (NM.voted) return; NM.voted = true; NM.net.rematch(true); netEndButtons(); }
function netVotes(m) { if (!NM || !Array.isArray(m.votes)) return; NM.foeVote = m.votes[NM.foe] === true; if (m.votes[NM.foe] === false) NM.closed = true; if (NM.phase === 'end') netEndButtons(); }
// out of the match for good (the menu, a forfeit, a cancelled match): tell the server, put the offline game back as it was
function netLeave() {
  const nm = NM; if (!nm) return; NM = null;
  try { if (nm.phase === 'end') nm.net.rematch(false); else nm.net.leaveMatch().catch(() => {}); } catch (e) {}
  if (nm.unsub) nm.unsub(); mode = nm.prevMode || mode; H.cpu = true; mapUsed = true;
  const b = $('endBtn'); b.disabled = false; b.innerHTML = '<span>Rematch</span><small>New canvas</small>';
  setTimeout(() => { if (typeof onlineAfterMatch === 'function') onlineAfterMatch(); }, 0);
}
// pausing online: the menu comes up, the match goes on
function netPause() { $('pauseYou').textContent = fmtPair(teamCov(0), teamCov(1))[0]; $('pauseCpu').textContent = fmtPair(teamCov(0), teamCov(1))[1]; $('pauseClock').textContent = fmtClock(matchLeft) + ' left'; $('quitBtn').textContent = 'Leave match'; pauseEl.hidden = false; }
"""

def apply(s):
    # the module, after the Friends client
    a = "if (SB_CFG) $('ttModal').classList.add('frlive');\n"
    s = rep(s, a, a + JS.lstrip('\n'))
    # ---- the simulation: the clock, the weather and the rival come from the server; no local ending, no CPU, no pick-ups
    s = rep(s, "  if (state === 'play' && matchLeft <= 0) {", "  if (state === 'play' && matchLeft <= 0 && !NM) {")
    s = rep(s, "    dryClock += dt; updateWeather(dt);", "    dryClock += dt; if (NM) netWeather(); else updateWeather(dt);")
    s = rep(s, "    runT += dt; if (!(sdEndT > 0)) matchLeft -= dt;", "    runT += dt; if (NM) matchLeft = netLeft(); else if (!(sdEndT > 0)) matchLeft -= dt;")
    s = rep(s, "    for (const D of ACTIVE) stepBlob(D, dt);\n    blobContact(); updateOrb(dt);",
               "    for (const D of ACTIVE) if (NM && D === H) netPuppet(D, dt); else stepBlob(D, dt);\n    if (NM) netContact(); else { blobContact(); updateOrb(dt); }")
    s = rep(s, "    if (matchLeft <= 0) { matchLeft = 0; if (!ACTIVE.some(pounding)) endMatch(); }", "    if (matchLeft <= 0) { matchLeft = 0; if (!NM && !ACTIVE.some(pounding)) endMatch(); }")
    s = rep(s, "  itemTick(dt); trapTick(dt); freezeTick(dt); zoneTick(dt);", "  if (!NM) itemTick(dt); trapTick(dt); freezeTick(dt); zoneTick(dt);")
    # ---- the frame: real time online (no hit-stop or slow motion), and your state to the server
    s = rep(s, "  const rdt = paced(Math.min(0.05, Math.max(0, (t - last) / 1000))); last = t;", "  const rawDt = Math.max(0, (t - last) / 1000), rdt = paced(Math.min(0.05, rawDt)); last = t;")
    # (a slow frame offline plays in slow motion, capped at 50 ms; online the match keeps the server's real time, so a slow
    # phone's frame catches up, up to a quarter second, and only the drawing keeps the cap)
    s = rep(s, "  if (state === 'paused') dt = 0; else if (hold > 0) {", "  if (NM && (state === 'play' || state === 'intro')) { hold = 0; slow = 0; if (rawDt > dt) dt = Math.min(rawDt, 0.25); } // (v306: online the server runs on real time)\n  if (state === 'paused') dt = 0; else if (hold > 0) {")
    s = rep(s, "  if (ffK > 1) dt = Math.min(dt, 0.05); // (the drawing's own timing no faster than a slow frame's)", "  if (ffK > 1 || NM) dt = Math.min(dt, 0.05); // (the drawing's own timing no faster than a slow frame's)")
    s = rep(s, "  if (dt > 0) { const n = Math.ceil(dt / 0.012); for (let i = 0; i < n; i++) step(dt / n); }\n",
               "  if (dt > 0) { const n = Math.ceil(dt / 0.012); for (let i = 0; i < n; i++) { if (NM) netAhead = dt * (n - i) / n; step(dt / n); } netAhead = 0; }\n  if (NM) netFrame();\n")
    s = rep(s, "function goTime() {\n  showCount('Go!', true);", "function goTime() {\n  if (NM && NM.phase === 'end') return; // (v306: the server ended it while this phone was still in the intro)\n  showCount('Go!', true);")
    s = rep(s, "const slamReady = D => D.slamCD <= 0 && D.paint >= POUND_MIN && !D.slam && (canAct(D) || D.st === 'hide');",
               "const slamReady = D => D.slamCD <= 0 && D.paint >= POUND_MIN && !D.slam && (canAct(D) || D.st === 'hide') && !(NM && D === P && NM.srvPaint !== undefined && NM.srvPaint < POUND_MIN - 0.005);")
    s = rep(s, "function kcamStart(V) {\n  if (kcamUsed ||", "function kcamStart(V) {\n  if (NM || kcamUsed ||")
    # ---- your blob: its moves go to the referee; a knock-out, a respawn or a flattening only when the server says
    s = rep(s, "if (D.koT <= 0) { if (D.rag) ragEnd(D); if (D.elimNow) sdOut(D); else respawnBlob(D); } return; }",
               "if (D.koT <= 0) { if (D.rag) ragEnd(D); if (NM) D.koT = 0; else if (D.elimNow) sdOut(D); else respawnBlob(D); } return; }")
    s = rep(s, "D.yaw = exitYaw(D, D.yaw); D.turn = 0; exitPot(D); } } else D.emptyT = 0;",
               "D.yaw = exitYaw(D, D.yaw); D.turn = 0; exitPot(D); if (NM && D === P) netAct('exitPot'); } } else D.emptyT = 0;")
    s = rep(s, "{ rollIntoCoffin(D, p); break; }", "{ if (NM) { if (D === P && p.ink > 0.02) { D.rollT = 0; D.dashT = 0; D.flung = false; D.spd = 0; netPre(); enterPot(D, p); p.cool = 0; netAct('enterPot', { pot: pots.indexOf(p) }); } } else rollIntoCoffin(D, p); break; }")
    s = rep(s, "  if (D.flung && D.st === 'play') for (const p of pots)", "  if (D.flung && D.st === 'play' && !NM) for (const p of pots)")
    s = rep(s, "&& Math.hypot(D.x - p.x, D.z - p.z) < 0.5 + PR * 0.95) { enterPot(D, p); break; }",
               "&& Math.hypot(D.x - p.x, D.z - p.z) < 0.5 + PR * 0.95) { if (NM && D === P) netPre(); enterPot(D, p); if (NM && D === P) netAct('enterPot', { pot: pots.indexOf(p) }); break; }")
    s = rep(s, "function jump(D) {\n  if (D.st === 'hide') return exitPot(D);", "function jump(D) {\n  if (D.st === 'hide') { if (NM && D === P) netAct('jump'); return exitPot(D); }")
    s = rep(s, "  D.air = true; D.vy = JUMP_V; D.airSling = true; D.airBack = false; D.stroke++;", "  if (NM && D === P) netAct('jump');\n  D.air = true; D.vy = JUMP_V; D.airSling = true; D.airBack = false; D.stroke++;")
    s = rep(s, "  D.airSling = false; D.airBack = false; D.vy = vy; D.spd = dist / Math.max(0.2, T);", "  if (NM && D === P) netAct('roll');\n  D.airSling = false; D.airBack = false; D.vy = vy; D.spd = dist / Math.max(0.2, T);")
    s = rep(s, "  if (D.st === 'hide') { exitPot(D, true); return false; }", "  if (D.st === 'hide') { if (NM && D === P) netAct('roll'); exitPot(D, true); return false; }")
    s = rep(s, "  D.rollT = ROLL_T; D.rollCD = ROLL_CD; D.rollBuf = 0; D.rollV =", "  if (NM && D === P) netAct('roll');\n  D.rollT = ROLL_T; D.rollCD = ROLL_CD; D.rollBuf = 0; D.rollV =")
    s = rep(s, "    const s = airShot(D, c, D.yaw); D.airSling = false; D.vy = s.v0;", "    if (NM && D === P) netAct('fling', { c });\n    const s = airShot(D, c, D.yaw); D.airSling = false; D.vy = s.v0;")
    s = rep(s, "  D.air = true; D.vy = launchV(c); D.spd = launchSpd(c);", "  if (NM && D === P) netAct('fling', { c });\n  D.air = true; D.vy = launchV(c); D.spd = launchSpd(c);")
    s = rep(s, "  if (D.giantT <= 0) D.paint -= Math.min(SLAM_COST, D.paint - 0.08); D.slamCD = D.slamMax = SLAM_CD; D.slams++; if (D === P) buzz(15);",
               "  if (D.giantT <= 0) D.paint -= Math.min(SLAM_COST, D.paint - 0.08); D.slamCD = D.slamMax = SLAM_CD; D.slams++; if (D === P) buzz(15); if (NM && D === P) netAct('pound');")
    s = rep(s, "function slamLand(D) {\n", "function slamLand(D) {\n  if (NM && D === P) netAct('land', { x: D.x, y: D.y, z: D.z }); // (v306: online the server rules on who it caught)\n")
    s = rep(s, "    if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && !O.rocket && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < koR) {",
               "    if (!NM && matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && !O.rocket && O.immuneT <= 0 && Math.hypot(O.x - D.x, O.z - D.z) < koR) {", 2)
    s = rep(s, "    if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - p.x, O.z - p.z) < KO_R + 1 && Math.abs(O.y - p.y) < 1.6) {",
               "    if (!NM && matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && O.immuneT <= 0 && Math.hypot(O.x - p.x, O.z - p.z) < KO_R + 1 && Math.abs(O.y - p.y) < 1.6) {")
    s = rep(s, "function knockOut(D, reason, by) {\n  if (D.st === 'ko' || state !== 'play') return;\n",
               "function knockOut(D, reason, by) {\n  if (D.st === 'ko' || state !== 'play') return;\n"
               "  if (NM && !NM.rule) { if (D === P && !NM.selfKo && (reason === 'fall' || reason === 'dry')) { NM.selfKo = reason; netAct('selfKo', { reason }); } return; } // (v306: online only the server knocks anyone out; yours, it's told)\n")
    s = rep(s, "function flatten(B, A, how) {\n", "function flatten(B, A, how) {\n  if (NM && !NM.rule) return; // (v306: online only the server flattens)\n")
    s = rep(s, "  if (mode !== 'solo' && !win && !overtimeUsed) {", "  if (mode !== 'solo' && !win && !overtimeUsed && !NM) {")
    s = rep(s, "win = mode === 'solo' ? 1 : sy > rest ? 1 : rest > sy ? -1 : 0,", "win = NM && NM.res ? NM.res.win : mode === 'solo' ? 1 : sy > rest ? 1 : rest > sy ? -1 : 0,")
    s = rep(s, "const slot = mode === 'solo' ? 'solo' : key + diff,", "const slot = NM ? 'online' : mode === 'solo' ? 'solo' : key + diff,")
    # ---- the start: no basins and no fly-over online; the count on the server's clock; no pick-ups, no Swim faster bonus
    s = rep(s, "  const basins = introBasins();", "  const basins = NM ? new Map() : introBasins();")
    s = rep(s, "  if (!reduceMotion && !window.__noReveal) { state = 'reveal';", "  if (!reduceMotion && !window.__noReveal && !NM) { state = 'reveal';")
    s = rep(s, "function introStep(rdt) {\n  introT += rdt;", "function introStep(rdt) {\n  introT = NM && NM.startAt ? INTRO_AT[3] - (NM.startAt - netNow()) / 1000 : introT + rdt; // (v306: online Go lands on the server's start)")
    s = rep(s, "D.swimBoost = D === P && D.skill === 'swim' ? SWIM_BOOST : 1;", "D.swimBoost = D === P && D.skill === 'swim' && !NM ? SWIM_BOOST : 1;")
    s = rep(s, "  startItems();\n  for (const D of ACTIVE) { if (D.st === 'out') continue;", "  if (NM) netGo(); else startItems();\n  for (const D of ACTIVE) { if (D.st === 'out') continue;")
    s = rep(s, "  Object.assign(gift, { id: null, on: false, got: false, pop: 0 }); giftM.visible = giftRing.visible = giftBeam.visible = false;\n",
               "  Object.assign(gift, { id: null, on: false, got: false, pop: 0 }); giftM.visible = giftRing.visible = giftBeam.visible = false;\n  if (NM) return; // (v306: no rare finds online)\n")
    s = rep(s, "const easyOn = () => diff === 'easy' && mode !== 'solo',", "const easyOn = () => !NM && diff === 'easy' && mode !== 'solo',")
    # the versus card: your rival by name, no vote, and up until the server says go
    s = rep(s, "(cls === 'me' ? 'You' : cls === 'me ally' ? 'Teammate' : 'CPU')", "(cls === 'me' ? 'You' : cls === 'me ally' ? 'Teammate' : NM ? 'Online' : 'CPU')")
    s = rep(s, "md[1] + ', CPU ' + (CRITICS[diff] || 'fair').toLowerCase())", "(NM ? md[1] + ', online' : md[1] + ', CPU ' + (CRITICS[diff] || 'fair').toLowerCase()))")
    s = rep(s, "&& !window.__noVote && !tutMatchDue()); /* (v284: the vote to come) */", "&& !window.__noVote && !tutMatchDue() && !NM); /* (v284: the vote to come) */")
    s = rep(s, "  if (mode === 'solo' || window.__noVote || tutMatchDue()) { setTimeout(",
               "  if (NM) { netVsWait(() => { if (id !== runId && state !== 'menu') { el.hidden = true; return cb(); } wipe(null); }); return; } // (v306: up until the server's start)\n  if (mode === 'solo' || window.__noVote || tutMatchDue()) { setTimeout(")
    # ---- the score is the server's
    s = rep(s, "const teamCov = t => (teamN[t + 1] + 0.5 * teamN[t + 5]) / NS * 100;", "const teamCov = t => NM && NM.cov ? NM.cov[t] || 0 : (teamN[t + 1] + 0.5 * teamN[t + 5]) / NS * 100;")
    # ---- pots stay where they are online, and come back when the server says
    s = rep(s, "function pickCoffinSpot(p) {\n", "function pickCoffinSpot(p) {\n  if (NM) return [p.x, p.y, p.z]; // (v306: online a pot comes back where it was)\n")
    s = rep(s, "      if (p.t >= DOWN_T) riseCoffin(p);", "      if (p.t >= DOWN_T && !NM) riseCoffin(p);")
    # ---- pause, the end screen, and leaving
    s = rep(s, "function pause() {\n  if (state !== 'play') return; state = 'paused';", "function pause() {\n  if (state !== 'play') return; if (NM) return netPause(); state = 'paused';")
    s = rep(s, "function resume() { if (state !== 'paused') return;", "function resume() { if (NM && state === 'play') { pauseEl.hidden = true; return; } if (state !== 'paused') return;")
    s = rep(s, "  end.hidden = false; measureOutro(); judgeGo();\n  endGate();\n", "  end.hidden = false; measureOutro(); judgeGo();\n  endGate(); if (NM) netEndButtons(); // (online: Rematch or Menu, whatever the lobby has waiting)\n")
    s = rep(s, "function rematchVote() { if (building || irisBusy) return;", "function rematchVote() { if (NM) return netRematch(); if (building || irisBusy) return;")
    s = rep(s, "function showMenu() {\n  teamTint = false;", "function showMenu() {\n  if (NM) netLeave(); teamTint = false;")
    return s
