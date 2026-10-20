"""v391: Showdown online, for a party of three or four (and matchmaking's Showdown). Applied after v391_party, last.

The party's Ready plays the mode it voted for: two in Versus play each other, as the v306 match always could; three or four play a
Showdown (everyone for themselves, or 2v2), which the v306 match layer, made for one rival, couldn't. This brings over the online
Showdown made around v312 (its notes: docs/party-v312.md), on today's match code (the stage made before the versus card, v367;
the locker as a page, v327; skins, v387):
- Versus (1v1), as before.
- Showdown free-for-all: three or four people, three hearts each (the server says how many), the closing canvas, the last one
  standing wins.
- Showdown 2v2: two teams of two. Your teammate is the game's ally (H3), the other pair H and H2; each team wears its two players'
  colours mixed.
Each other player is one of the game's own rivals, dressed as they are (with their skin) and drawn from the server's snapshots, by
their handle. The server rules on everything that wins or loses: knock-outs and the hearts they cost, who is out and in what place,
the closing canvas, the end. The game shows its own Showdown around those rulings: the hearts across the top, the banners, watching
once you're out (Leave instead of Skip: the match runs on real time), and the standings at the end."""
import re

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def swap(s, name, new, decl='function'):
    """Replace a whole top-level function (or const) of the match block, from its first line to the line before the next top-level
    statement."""
    a = '\n' + decl + ' ' + name + (' ' if decl == 'const' else '(')
    i = s.index(a, s.index('// ---------- (v306) Online: a match against a person')) + 1
    m = re.compile(r'\n(?=function |const |let |var |window\.|// )').search(s, i + 1)
    return s[:i] + new.strip('\n') + '\n' + s[m.start() + 1:]

SEATS = r"""
// (v391) who is who: your slot is you (P); in 2v2 your teammate is the game's ally (H3) and the other pair H and H2; otherwise the
// others in slot order (H, H2, H3)
const NET_MODES = ['duel', 'ffa', 'duo'];
const netStartOf = D => D === P ? START : D === H ? CSTART : D === H2 ? CSTART2 : D === H3 ? CSTART3 : null;
const netLookOf = D => D === H ? LH : D === H2 ? L2 : D === H3 ? L3 : null;
function netSeats(m) {
  const me = m.players.find(p => p.slot === m.you), others = m.players.filter(p => p !== me).sort((a, b) => a.slot - b.slot), seats = new Map([[m.you, P]]);
  if (m.mode === 'duo') { const mate = others.find(p => p.side === me.side); if (mate) seats.set(mate.slot, H3); others.filter(p => p !== mate).forEach((p, i) => seats.set(p.slot, [H, H2][i])); }
  else others.forEach((p, i) => seats.set(p.slot, [H, H2, H3][i]));
  return seats;
}
// the coverage each blob's side has (by the game's team order: you, H, H2, H3)
const netCovOf = sides => { const s = Array.isArray(sides) ? sides : []; return [P, H, H2, H3].map(D => { const sl = NM.slotOf.get(D); return sl === undefined ? 0 : +s[NM.sides.get(sl)] || 0; }); };
"""

MATCH_FOUND = r"""
function netMatchFound(m, net) {
  net = net || (typeof ON === 'object' && ON && ON.net); if (!net || !m || !Array.isArray(m.players)) return;
  const me = m.players.find(p => p.slot === m.you), n = m.players.length;
  if (!me || n < 2 || !NET_MODES.includes(m.mode) || n > (m.mode === 'duel' ? 2 : 4) || (m.mode === 'duo' && n !== 4)) { net.leaveMatch().catch(() => {}); return; } // (not a match this game plays)
  if (building || irisBusy) { setTimeout(() => netMatchFound(m, net), 120); return; }
  const prevMode = NM ? NM.prevMode : mode; if (NM && NM.unsub) NM.unsub();
  const seats = netSeats(m), slotOf = new Map([...seats].map(([s, D]) => [D, s])), others = [...seats.values()].filter(D => D !== P), fo = m.players.find(p => p.slot === slotOf.get(others[0]));
  NM = { net, m, id: m.matchId, mode: m.mode, slot: m.you, seats, slotOf, others, foe: fo.slot, side: me.side, foeSide: fo.side, sides: new Map(m.players.map(p => [p.slot, p.side])), prevMode, s: null, startAt: 0, endAt: 0, cov: null, wxI: -1, wx: [],
    live: false, rule: false, selfKo: null, res: null, corr: 0, refused: 0, why: [], phase: 'found', ranks: new Map(), foeVote: 0, unsub: null, t0: performance.now() };
  NM.unsub = netWire(net);
  if (menuPage === 'worlds') { menuPage = 'home'; menu.dataset.page = 'home'; $('mWorld').hidden = true; $('mHome').hidden = false; }
  if (menuPage === 'events') { menuPage = 'home'; menu.dataset.page = 'home'; evEl.hidden = true; $('mHome').hidden = false; } evFrom = false; document.body.classList.remove('evon');
  if (shopOpen) closeShop(true); if (lookOpen) closeLook(); if (lkOn()) closeLocker(true); if (!$('friendsModal').hidden) closeFriends();
  mode = m.mode; applyMode(); if (ACTIVE.length !== seats.size) ACTIVE = ACTIVE.filter(D => slotOf.has(D)); // (a Showdown of three: the fourth sits it out)
  for (const D of [H, H2, H3]) { D.cpu = !slotOf.has(D); D.netLive = false; } // (the rivals are people: no CPU mind, no CPU pace)
  netDress(m);
  AU.init(); AU.music('vs'); menu.classList.add('leaving'); setTimeout(() => menu.classList.remove('leaving'), 900);
  irisClose(() => {
    menu.hidden = true; end.hidden = true; pauseEl.hidden = true; howModal.hidden = true; hideTally();
    if (!NM) { showMenu(); camSnap = true; irisOpen(); return; } // (called off, or taken out, while the iris closed: back to the menu)
    if (NM.id !== m.matchId) return;
    prepMatch(() => genWorld(m.seed >>> 0, { easy: false, avoid: null, themes: NET_THEMES, flat: false })).then(() => { if (!NM || NM.id !== m.matchId) return; netSendLayout(); showVS(beginMatch); });
  }, null, 'New canvas');
}
"""

SEND_LAYOUT = r"""
function netSendLayout() {
  const sp = NM.mode === 'duel' ? [START, CSTART] : [START, CSTART, CSTART2, CSTART3]; // (every phone builds the same stage: the spots in the stage's own order)
  const L = RMNet.layoutFromStage({ arena: ARENA, boxes: BOXES, ramps: RAMPS, holes: HOLES, pots: POTS.slice(0, VS_CFG.pots), powers: POWER_SPOTS, spawns: sp, puddles: RIVALS.slice(0, VS_CFG.rivals) });
  NM.net.sendLayout(L);
  // the server puts slot i on spot i: you on yours, each of the others on theirs
  const at = sp.map(q => ({ x: q.x, z: q.z, yaw: q.yaw }));
  for (const [s, D] of NM.seats) { const S = netStartOf(D); if (S && at[s]) Object.assign(S, at[s]); }
}
"""

DRESS = r"""
// each of the others as they dressed: their name, paint (set apart from yours, and from each other's), eyes, wearables and rank
function netDress(m) {
  const ok = (w, v, slot) => typeof v === 'string' && WEAR.some(x => x.id === v && x.slot === slot) ? v : null;
  for (const p of m.players) {
    const D = NM.seats.get(p.slot), Lk = netLookOf(D); if (!D || D === P || !Lk) continue;
    const L = p.look && typeof p.look === 'object' ? p.look : {}, w = L.w && typeof L.w === 'object' ? L.w : {};
    NAMES[D.team] = p.name ? hdOf(String(p.name).slice(0, 16)) : 'Rival'; // (a person, by their handle: v311_handles)
    const c = typeof L.c === 'string' && rivalColOf(L.c); if (c) rivalCol[D.team] = c;
    Lk.wearing = { head: ok(w, w.head, 'head'), back: ok(w, w.back, 'back'), mouth: ok(w, w.mouth, 'mouth'), eye: ok(w, w.eye, 'eye'), side: ok(w, w.side, 'side'), neck: ok(w, w.neck, 'neck'), lash: ok(w, w.lash, 'lash'), arms: ok(w, w.arms, 'arms'), skin: ok(w, w.skin, 'skin'), iris: EYE_KEYS.includes(w.iris) ? w.iris : 'brown', eyes: EYE_STYLES[L.e] ? L.e : 'round' };
    NM.ranks.set(D, clamp(L.r | 0, 1, 999) || 1);
  }
  teamTint = true; teamHues();
}
"""

WIRE = r"""
function netWire(net) {
  const offs = [], on = (ev, fn) => offs.push(net.on(ev, m => { if (!NM || NM.net !== net) return; try { fn(m); } catch (e) { frameErr(e); } }));
  on('start', m => { if (m.matchId !== NM.id) return; NM.s = m; NM.startAt = m.startAt; NM.endAt = m.endAt; NM.rules = m.rules || {}; NM.wx = Array.isArray(m.weather) ? m.weather : [];
    for (const q of m.spawns || []) { const S = netStartOf(netBlob(q.slot)); if (S) Object.assign(S, { x: q.x, z: q.z, yaw: q.yaw }); } });
  on('correction', netCorrect); on('ko', netKo); on('respawn', netRespawn); on('flat', netFlat); on('push', netPush); on('dodged', netDodged);
  on('pot', netPot); on('potEject', netEject); on('act', netFoeAct); on('resume', netResume); on('out', netOut);
  on('coverage', m => { NM.cov = netCovOf(m.sides); });
  on('snapshot', s => { const me = (s.players || []).find(q => q.slot === NM.slot); if (me) NM.srvPaint = me.paint; }); // (the referee's paint meter, for the pound)
  on('overtime', m => { NM.endAt = m.endAt; if (state === 'play') { banner('Overtime!', (m.secs | 0) + ' more seconds', true); AU.horn(); buzz([30, 40, 30]); lastCount = 99; } });
  on('matchEnd', netEnd); on('matchCancelled', netCancelled); on('matchClosed', netClosed); on('rematch', netVotes);
  on('playerAway', m => { const D = netBlob(m.slot); if (D && D !== P && state === 'play') popText(nameOf(D) + ' lost connection'); });
  on('playerBack', m => { const D = netBlob(m.slot); if (D && D !== P && state === 'play') popText(nameOf(D) + ' is back'); });
  on('playerLeft', m => { const D = netBlob(m.slot); if (!D) return;
    if (D === P && state !== 'play') { // (taken out before the match began on this screen: back to the lobby, not into a match you're no longer in)
      if (NM.phase !== 'end') { netLeave(); popText(m.reason === 'kicked' ? 'Removed from the match' : 'Away too long'); netToMenu(); }
      return; }
    if (state !== 'play') return;
    if (D === P) { // (the server took you out: away too long, or not moving. In a Showdown the rest play on; you watch, or Leave)
      if (isShow() && P.st !== 'out') { banner(m.reason === 'kicked' ? 'Removed from the match' : 'Away too long', 'You’re out of this one', true); P.hearts = 0; P.koT = 0; if (P.rag) ragEnd(P); sdOut(P); }
      return; }
    if (NM.mode === 'duel') return banner(nameOf(D) + ' left', 'The match is yours', true);
    popText(nameOf(D) + ' left'); if (isShow() && D.st !== 'out') { D.hearts = 0; D.koT = 0; if (D.rag) ragEnd(D); sdOut(D); } });
  on('close', m => { if (state === 'play' && m && m.willReconnect) popText('Reconnecting…'); });
  return () => { for (const f of offs) f(); };
}
"""

BLOB = r"""
const netBlob = slot => (NM && NM.seats.get(slot)) || null;
"""

GO = r"""
function netGo() { for (const D of ACTIVE) { D.held = null; D.held2 = null; D.heldT = 0; } for (const D of NM.others) D.rank = NM.ranks.get(D) || 1; NM.wxI = -1; NM.phase = 'play'; }
"""

PUPPET = r"""
function netPuppet(D, dt) {
  if (D.wob > 0) D.wob = Math.max(0, D.wob - dt * 2.5); if (D.squash > 0) D.squash = Math.max(0, D.squash - dt * 4.2); if (D.bonkCD > 0) D.bonkCD -= dt;
  if (D.flatT > 0) { D.flatT = Math.max(0, D.flatT - dt); if (D.flatT === 0) { D.squash = 0.9; D.wob = 1; } }
  if (D.st === 'ko' || D.st === 'out') { if (D.rag) ragStep(D, dt); return; } // (gone until the server brings it back)
  const r = NM.net.remote(NM.slotOf.get(D)), F = RMNet.FLAGS; if (!r) return;
  if (!D.netLive) { if (r.t > NM.startAt + 30) D.netLive = true; else return netDrop(D, dt); } // (until its first move after Go: still dropping onto its spot)
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
"""

CONTACT = r"""
function netContact() { for (const B of NM.others) if (ACTIVE.includes(B)) netTouch(P, B); }
function netTouch(A, B) {
  if (A.st !== 'play' || B.st !== 'play') return;
  const dx = B.x - A.x, dz = B.z - A.z, d = Math.hypot(dx, dz), dy = A.y - B.y, now = performance.now();
  if (!ally(A, B) && A.air && A.vy < -0.5 && dy > 0.25 && dy < 0.95 && d < PR * 2 && !A.slam && !(A.assistT > 0) && B.flatT <= 0 && !(NM.stompAt > now - 400)) {
    NM.stompAt = now; netAct('stomp', { target: NM.slotOf.get(B) }); A.vy = 6.5; A.air = true; A.y = Math.max(A.y, B.y + 0.3); fxLaunch(A, 0.8); return;
  }
  if (d > PR * 2 || Math.abs(dy) > 0.95 || A.air || B.air || B.flatT > 0) return;
  const nx = dx / (d || 1), nz = dz / (d || 1), push = PR * 2 - d + 0.01, x = A.x - nx * push, z = A.z - nz * push;
  if (!blockedAt(x, z, A.y)) { A.x = x; A.z = z; }
  if (A.bonkCD <= 0 && A.spd > 1) { fxKnock(A, -nx, -nz, clamp(A.spd / 10, 0.25, 0.6)); A.spd *= 0.65; A.bonkCD = 0.25; A.squash = Math.max(A.squash, 0.45); A.wob = 1; AU.bonk(0.6); }
}
"""

KO = r"""
function netKo(m) {
  const D = netBlob(m.slot), by = netBlob(m.by); if (!D) return;
  const sd = isShow() && Number.isFinite(m.hearts); if (sd) D.hearts = m.hearts + 1; // (the game takes a heart off as it knocks one out: it lands where the server says)
  if (D.st !== 'ko' && D.st !== 'out') { if (D !== P && D.st !== 'hide') { D.x = m.x; D.y = m.y; D.z = m.z; } NM.rule = true; try { knockOut(D, m.reason, by); } finally { NM.rule = false; } }
  if (sd) { D.hearts = m.hearts; if (m.out && !D.elimNow && D.st !== 'out') { D.elimNow = true; D.elimAt = runT; D.elimBy = by || null; } sdHud(true); }
  D.koT = m.respawnAt ? Math.max(0.3, (m.respawnAt - netNow()) / 1000) : 99; if (D === P) NM.selfKo = null;
}
// out of hearts, for good (the server says when, and the place it got)
function netOut(m) { const D = netBlob(m.slot); if (!D || D.st === 'out' || !isShow()) return; if (m.place) D.place = m.place; if (D.rag) ragEnd(D); D.koT = 0; D.hearts = 0; sdOut(D); }
"""

FLAT = r"""
function netFlat(m) {
  const D = netBlob(m.slot), A = netBlob(m.by) || (D === P ? NM.others[0] : P); if (!D) return;
  if (D === P) { P.x = m.x; P.y = m.y; P.z = m.z; P.spd = 0; P.vy = 0; P.air = false; }
  NM.rule = true; try { flatten(D, A, 'stomp'); } finally { NM.rule = false; }
  D.flatT = Math.max(0.2, (m.until - netNow()) / 1000);
}
"""

PUSH = r"""
function netPush(m) {
  if (m.slot !== NM.slot) { const B = netBlob(m.slot); if (B) { B.wob = 1; B.squash = 0.8; } return; }
  if (P.charging) clearCharge(P); holdCharge = false; slingOff();
  P.yaw = Math.atan2(m.dx, m.dz); P.spd = m.spd; P.vy = m.vy; P.air = true; P.stroke++; P.slam = false; P.missile = false; P.flatT = 0; P.turn = 0; P.knockT = 0.9; P.flung = false; P.flingC = 0; P.wob = 1; P.squash = 0.8;
  const by = netBlob(m.by); P.lastHit = by && by !== P ? { by, t: runT } : null; fxTumble(P, 0.8, Math.random() - 0.5); shake = Math.max(shake, 0.45); buzz([30, 20, 30]); banner(m.why === 'burst' ? 'Blasted!' : 'Knocked back!');
}
"""

POT = r"""
function netPot(m) {
  const p = pots[m.i]; if (!p) return;
  if (typeof m.ink === 'number') p.ink = m.ink;
  const occ = p.occ && p.occ !== P ? p.occ : null;
  if (m.up === false) { if (occ) netFoeOut(occ, p); if (p.st === 'up') sinkCoffin(p); p.next = [p.x, p.y, p.z]; return; }
  if (m.up && p.st !== 'up' && p.st !== 'rise') { p.next = [p.x, p.y, p.z]; riseCoffin(p); }
  const B = m.occ >= 0 ? netBlob(m.occ) : null;
  if (B && B !== P) { if (occ && occ !== B) netFoeOut(occ, p); if (B.pot !== p && B.st !== 'ko' && B.st !== 'out') { if (B.pot) netFoeOut(B, B.pot); enterPot(B, p); } }
  else if (occ) netFoeOut(occ, p);
}
"""

FOE_OUT = r"""
function netFoeOut(D, p) { if (!D || D.pot !== p) return; p.occ = null; p.cool = 1.0; p.bounce = 0.7; D.pot = null; D.st = 'play'; D.stroke++; D.wob = 1; D.spawnImm = false; fxLaunch(D, 0.8); }
"""

FOE_ACT = r"""
function netFoeAct(m) {
  const D = netBlob(m.slot); if (!D || D === P) return;
  if (m.a === 'jump') fxLaunch(D, 1);
  else if (m.a === 'fling') { const c = clamp(+m.c || 0.5, 0, 1); D.flingC = c; D.flung = true; burst2(D, 10 + (c * 10 | 0)); if (hearable(D)) AU.fling(c * 0.5); }
  else if (m.a === 'pound') { if (D.st === 'hide') netFoeBurst(D); else if (hearable(D)) AU.whoosh(); }
  else if (m.a === 'slam') netSlamFx(D, m);
}
"""

FOE_BURST = r"""
function netFoeBurst(D) {
  const p = D.pot; if (!p) return; netFoeOut(D, p);
  D.air = true; D.y = p.y + 0.35; D.vy = 13.5; D.freeLand = true;
  addSplat(p.x, p.y, p.z, D.yaw, SLAM_R, dryClock, false, true, tcode(D)); shockwave(p.x, p.y, p.z, SLAM_R, 0xBFE3FF); shockwave(p.x, p.y, p.z, SLAM_R * 0.6, TEAMS[D.team].wet);
  breakCoffin(p, D); const dp = Math.hypot(p.x - P.x, p.z - P.z); if (dp < 20) { shake = Math.max(shake, 0.45 * (1 - dp / 20)); AU.at(p.x, p.z); AU.burst(0.6); }
}
"""

RESUME = r"""
function netResume(m) {
  if (m.matchId !== NM.id || !m.self) return; NM.endAt = m.endAt || NM.endAt;
  if (Array.isArray(m.cov) && m.cov.length) NM.cov = netCovOf(m.cov);
  for (const q of m.pots || []) netPot({ i: q.i, occ: q.occ, up: q.up, ink: q.ink });
  if (isShow()) { // (the hearts as they are now, and who went out while this phone was away)
    if (Number.isFinite(m.self.hearts)) P.hearts = m.self.hearts;
    for (const o of m.others || []) { const D = netBlob(o.slot); if (!D) continue; if (Number.isFinite(o.hearts)) D.hearts = o.hearts; if ((o.st === 'out' || o.st === 'left') && D.st !== 'out') { D.koT = 0; if (D.rag) ragEnd(D); sdOut(D); } }
    sdHud(true);
  }
  if (state === 'play' && P.st === 'play' && m.self.st === 'play') netCorrect({ x: m.self.x, y: m.self.y, z: m.self.z, yaw: m.self.yaw });
}
"""

END = r"""
function netEnd(m) {
  if (m.matchId && m.matchId !== NM.id) return; const res = Array.isArray(m.results) ? m.results : [];
  const me = res.find(r => r.slot === NM.slot); if (!me) return;
  NM.res = { win: m.winner < 0 ? 0 : m.winner === NM.side ? 1 : -1, reason: m.reason, m, places: new Map() };
  NM.cov = [P, H, H2, H3].map(D => { const r = res.find(q => q.slot === NM.slotOf.get(D)); return r ? +r.sideCoverage || 0 : 0; });
  for (const r of res) { const D = netBlob(r.slot); if (!D) continue; D.kos = r.kos | 0; if (isShow()) { D.hearts = Math.max(0, r.hearts | 0); if (r.place) { D.place = r.place; NM.res.places.set(D, r.place); } } }
  NM.live = false; NM.phase = 'end';
  const gone = res.filter(r => r.left && r.slot !== NM.slot).map(r => netBlob(r.slot)).filter(Boolean);
  if (state !== 'play') { if (state !== 'dead') { popText(m.reason === 'forfeit' && gone.length ? nameOf(gone[0]) + ' left' : 'Match over'); netLeave(); netToMenu(); } return; } // (over before it began here: no standings, back to the lobby)
  if (isShow() && m.reason === 'last_standing') { sdEndT = SD_END_T; if (spec) { spec.ff = false; $('sdSpec').hidden = true; } } // (the last knock-out at its own speed, as against the CPU, then the standings)
  else { for (const D of ACTIVE) if (D.rag) ragEnd(D); if (isShow()) endShowdown(m.reason === 'time'); else endMatch(); }
  if (m.reason === 'forfeit' && !me.left && gone.length) setTimeout(() => { if (NM && NM.phase === 'end') banner(NM.mode === 'duel' || gone.length === 1 ? nameOf(gone[0]) + ' left' : 'The others left', NM.res.win > 0 ? 'You win!' : '', true); }, 300);
}
"""

END_BUTTONS = r"""
function netEndButtons() {
  const b = $('endBtn'), wait = NM && NM.voted, gone = !NM || NM.closed, duel = !NM || NM.mode === 'duel', who = NM && duel ? nameOf(NM.others[0]) : 'the others';
  $('replayBtn').hidden = true; $('replayBtn').closest('.row').hidden = false; end.classList.remove('gate');
  if (!b.querySelector('small')) b.innerHTML = '<span>Rematch</span><small></small>';
  b.querySelector('span').textContent = gone ? (NM && NM.closedWhy === 'rematch_timeout' ? 'Rematch closed' : duel ? 'Rival left' : 'No rematch') : wait ? 'Waiting…' : 'Rematch';
  b.querySelector('small').textContent = gone ? 'Back to the menu' : wait ? 'for ' + who : NM && NM.foeVote ? (duel ? who + ' wants one!' : NM.foeVote + ' of ' + NM.others.length + ' want one') : duel ? 'Same rival, new canvas' : 'Same players, new canvas';
  b.disabled = !!wait && !gone; // (when it's off it takes you back to the menu)
}
"""

VOTES = r"""
function netVotes(m) { if (!NM || !Array.isArray(m.votes)) return; const o = NM.others.map(D => m.votes[NM.slotOf.get(D)]); NM.foeVote = o.filter(v => v === true).length; if (o.some(v => v === false)) NM.closed = true; if (NM.phase === 'end') netEndButtons(); }
"""

CANCELLED = r"""
// back to the menu before a match is played. The versus card holds the iris shut until the start, so from the card the menu comes up
// from under it; otherwise the iris closes over whatever shows, once it's free
function netToMenu() {
  if (!$('vsx').hidden && irisBusy) { $('vsx').hidden = true; showMenu(); camSnap = true; irisOpen(); return; }
  $('vsx').hidden = true; (function go() { if (state === 'menu' && !menu.hidden) return; if (!toMenu()) setTimeout(go, 150); })();
}
function netCancelled() {
  if (!NM) return; const was = NM.phase; netLeave(); popText(was === 'found' ? 'The match was called off' : 'Match over'); netToMenu();
}
"""

LEAVE = r"""
function netLeave() {
  const nm = NM; if (!nm) return; NM = null;
  try { if (nm.phase === 'end') nm.net.rematch(false); else nm.net.leaveMatch().catch(() => {}); } catch (e) {}
  if (nm.unsub) nm.unsub(); mode = nm.prevMode || mode; applyMode(); H.cpu = H2.cpu = H3.cpu = true; mapUsed = true; // (the offline game as it was: its mode, its field, CPU rivals)
  const b = $('endBtn'); b.disabled = false; b.innerHTML = '<span>Rematch</span><small>New canvas</small>';
  setTimeout(() => { if (typeof onlineAfterMatch === 'function') onlineAfterMatch(); }, 0);
}
"""

def apply(s):
    # ---- the match layer, for up to four
    a = "function netMatchFound(m, net) {"
    s = rep(s, a, SEATS.lstrip('\n') + a)
    s = swap(s, 'netMatchFound', MATCH_FOUND)
    s = swap(s, 'netSendLayout', SEND_LAYOUT)
    s = swap(s, 'netRival', DRESS)
    s = rep(s, "// the rival as they dressed: their name, paint (set apart from yours if it's the same), eyes, wearables and rank\n", "")
    s = swap(s, 'netWire', WIRE)
    s = swap(s, 'netBlob', BLOB, 'const')
    s = swap(s, 'netGo', GO)
    s = swap(s, 'netPuppet', PUPPET)
    s = swap(s, 'netContact', CONTACT)
    s = swap(s, 'netKo', KO)
    s = swap(s, 'netFlat', FLAT)
    s = swap(s, 'netPush', PUSH)
    s = swap(s, 'netPot', POT)
    s = swap(s, 'netFoeOut', FOE_OUT)
    s = swap(s, 'netFoeAct', FOE_ACT)
    s = swap(s, 'netFoeBurst', FOE_BURST)
    s = swap(s, 'netResume', RESUME)
    s = swap(s, 'netEnd', END)
    s = swap(s, 'netEndButtons', END_BUTTONS)
    s = swap(s, 'netVotes', VOTES)
    s = swap(s, 'netLeave', LEAVE)
    s = swap(s, 'netCancelled', CANCELLED)
    for k in ["NM.foeLive", "NM.foeRank", "netRival("]:
        assert k not in s, k
    # ---- the simulation: every other player is a puppet; the clock (and the closing canvas on it) is the server's; a Showdown ends
    # when the server says
    s = rep(s, "    for (const D of ACTIVE) if (NM && D === H) netPuppet(D, dt); else stepBlob(D, dt);", "    for (const D of ACTIVE) if (NM && D !== P) netPuppet(D, dt); else stepBlob(D, dt);")
    s = rep(s, "    runT += dt; if (NM) matchLeft = netLeft();", "    runT += dt; if (NM && NM.startAt) runT = Math.max(0, (netNow() - NM.startAt) / 1000); if (NM) matchLeft = netLeft();")
    s = rep(s, "    if (sdEndT > 0 && state === 'play') { sdEndT -= dt; if (sdEndT <= 0) endShowdown(false); }", "    if (sdEndT > 0 && state === 'play' && (!NM || NM.phase === 'end')) { sdEndT -= dt; if (sdEndT <= 0) endShowdown(false); }")
    # ---- 2v2: two people on a team wear their colours mixed (the game's plan for online)
    s = rep(s, "const slotHuman = i => i === 0,", "const slotHuman = i => i === 0 || !!NM,")
    # ---- a Showdown of three: the fourth rival sits it out
    s = rep(s, "if (!isShow()) H3.st = 'out'; for (const D of ACTIVE) D.hearts = isShow() ? SD_HEARTS : 0;",
               "if (!isShow() || !ACTIVE.includes(H3)) H3.st = 'out'; for (const D of ACTIVE) D.hearts = isShow() ? (NM && NM.rules && NM.rules.hearts) || SD_HEARTS : 0; /* (online, the server's hearts) */")
    s = rep(s, "L3.drop.visible = L3.shadow.visible = isShow();", "L3.drop.visible = L3.shadow.visible = isShow() && ACTIVE.includes(H3);")
    s = rep(s, "if (mode === 'trio' || mode === 'ffa') h += card(H2, NAMES[2], 'foe2'); if (mode === 'ffa') h += card(H3, NAMES[3], 'foe3'); }",
               "if (mode === 'trio' || mode === 'ffa') h += card(H2, NAMES[2], 'foe2'); if (mode === 'ffa' && ACTIVE.includes(H3)) h += card(H3, NAMES[3], 'foe3'); }")
    s = rep(s, "$('vsRow').classList.toggle('trio', mode === 'trio'); $('vsRow').classList.toggle('quad', isShow());",
               "$('vsRow').classList.toggle('trio', mode === 'trio' || (isShow() && ACTIVE.length === 3)); $('vsRow').classList.toggle('quad', isShow() && ACTIVE.length === 4);")
    s = rep(s, "if (isShow()) list.push([H3, $('vbox3'), mode === 'duo' ? VS_POSE.ally : VS_POSE.foe3]);", "if (isShow() && ACTIVE.includes(H3)) list.push([H3, $('vbox3'), mode === 'duo' ? VS_POSE.ally : VS_POSE.foe3]);")
    # ---- the end of a Showdown online: the server's places; it counts as an online match
    s = rep(s, "  const draw = winSides.length > 1, mine = sideOf(P), win = draw ? (winSides.includes(mine) ? 0 : -1) : winSides[0] === mine ? 1 : -1, winners = ACTIVE.filter(D => winSides.includes(sideOf(D)));",
               "  if (NM && NM.res && NM.res.places.size) { for (const D of ACTIVE) { const pl = NM.res.places.get(D); if (pl) D.place = pl; } winSides = [...new Set(ACTIVE.filter(D => D.place === 1).map(sideOf))]; } // (v391: online, the server's standings)\n"
               "  const draw = winSides.length > 1, mine = sideOf(P), win = draw ? (winSides.includes(mine) ? 0 : -1) : winSides[0] === mine ? 1 : -1, winners = ACTIVE.filter(D => winSides.includes(sideOf(D)));")
    s = rep(s, "store.wins = store.wins || {}; store.played = store.played || {}; const slot = mode + diff;", "store.wins = store.wins || {}; store.played = store.played || {}; const slot = NM ? 'online' : mode + diff;")
    # (a win online isn't a win against the critics on harsh: the CPU's setting doesn't count for the day's commissions)
    s = rep(s, "  endInfo.diff = diff; let gain = Math.round(16 + ry * 0.9", "  endInfo.diff = NM ? 'online' : diff; let gain = Math.round(16 + ry * 0.9")
    s = rep(s, "  endInfo.diff = diff; const pl = P.place || 4;", "  endInfo.diff = NM ? 'online' : diff; const pl = P.place || 4;")
    # (the end screen's Showdown branch returned before the online buttons: Rematch for everyone or Menu, no Same canvas)
    s = rep(s, "end.classList.add('sd'); end.dataset.next = ''; $('replayBtn').hidden = false; $('endBtn').querySelector('small').textContent = 'New canvas'; end.hidden = false; measureOutro(); endGate(); return; }",
               "end.classList.add('sd'); end.dataset.next = ''; $('replayBtn').hidden = false; $('endBtn').querySelector('small').textContent = 'New canvas'; end.hidden = false; measureOutro(); endGate(); if (NM) netEndButtons(); return; }")
    # ---- out of a Showdown online: watch the rest, or leave (no skipping ahead: the match runs on real time)
    s = rep(s, "function sdSkipOn() { if (!spec || spec.ff || state !== 'play' || sdEndT > 0) return;", "function sdSkipOn() { if (NM) { if (state === 'play' && P.st === 'out') toMenu(); return; } if (!spec || spec.ff || state !== 'play' || sdEndT > 0) return;")
    s = rep(s, "$('sdSkip').disabled = false; $('sdSkipL').textContent = 'Skip'; camSnap = true; }", "$('sdSkip').disabled = false; $('sdSkipL').textContent = NM ? 'Leave' : 'Skip'; $('sdSkip').setAttribute('aria-label', NM ? 'Leave the match: you’re out' : 'Skip ahead: the rest of the match at high speed'); camSnap = true; }")
    # ---- banners are set in capitals; the people in an online match go by their handles (v311_handles), which keep their small letters
    s = rep(s, "function banner(big, small, long, quick, acc) {", "// (a line that may name people: each handle in it keeps its small letters)\nconst hdLine = t => escAttr(t).replace(/@[A-Za-z0-9_]+/g, '<bdi class=\"hd\">$&</bdi>');\nfunction banner(big, small, long, quick, acc) {")
    s = rep(s, "{ const B = $('bannerBig'); B.textContent = big; B.style.fontSize = '';", "{ const B = $('bannerBig'); B.innerHTML = hdLine(big); B.style.fontSize = '';")
    s = rep(s, "$('bannerSmall').textContent = small || '';", "$('bannerSmall').innerHTML = hdLine(small || '');")
    return s
