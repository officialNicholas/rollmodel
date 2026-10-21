"""v427: pick-ups, the orb and the special strokes online.

Online matches had none of them: the game left them out until it could show the server's. Now (with a server that knows the
item protocol, and every game in the match on this version or later):
- Everyone starts with the item they picked under Abilities (a CPU with one of the first three), as offline. The pick, the special
  and the skill go to the server with the match's stage.
- The pick-ups (Roller, Turret, Paint Trap, and now and then the Whirlwind and the Boomerang) come up where the server puts them,
  and the server decides who got one (and drops the one you held behind you, as offline). The orb comes up too; whoever reaches it
  gets their own special stroke (Giant, Rocket, Flash Freeze, Paint Storm, Paint Bomb) in the orb slot, for ten seconds (Deep
  Pockets: until used).
- Using one: it goes off on your screen at once and the server is told; everyone else sees it go off (the boomerang thrown the way
  you threw it, a storm's drops where yours fall, a rocket coming down where yours did).
- The hits: whoever's effect lands a hit (whirlwind, boomerang, turret glob, storm drop, bomb, rocket, a giant or a roller rolling
  over someone) tells the server, which checks it (the effect is live, the place is in its reach, the target was there as the
  attacker saw them) and rules, giving the target's own dodge a moment to arrive, like a pound. A Paint Trap is the server's own
  ruling (a knock-out, as offline; a roll through it pops it harmlessly). The Flash Freeze is the server's: everyone else out in the
  open is frozen where they stand, unless their roll began right at the flash; tapping out still gets you out up to a second sooner.
  A turret glob takes paint from the tank; three in a row stun; empty, it's a knock-out.
- The paint they leave counts for the score: your effects' splats go to the server, which stamps them within what each can paint.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""
// ---------- (v427) the game's pick-ups, the orb and the specials, online. The server hands them out, keeps the pockets and rules on every
// knock-out; this game shows its pick-ups and orb, sends what you (and the CPUs it drives) use, plays everyone's effects, and sends the
// hits and the paint your effects land, for the server to check ----------
const NMI = () => !!(NM && NM.rules && NM.rules.iv >= 2);
const netR = v => Math.round(v * 100) / 100;
const NET_CLAIM = { crush: 'crush', boom: 'boom', storm: 'storm', bomb: 'bomb', shot: 'shot' };
// what you take into a match: the item protocol this game speaks, your start item, special and skill
function netKit() { return { iv: 2, it: strokeItem() || undefined, sp: strokeSpecial() || undefined, sk: strokeSkill() || undefined }; }
// fire and forget (the claims, the paint, the relays)
function netTell(a, data, D) {
  if (!NM || !NM.net || !NM.net.tell) return; const nm = NM, back = netAhead * 1000, d = Object.assign({ ts: nm.net.serverNow() - back, vt: nm.net.renderTime() - back }, data || {});
  if (D && D !== P) { const slot = nm.slotOf.get(D); if (slot !== undefined && netMine(D)) nm.net.botTell(slot, a, d); return; }
  nm.net.tell(a, d);
}
// a hit one of yours landed (yours, or a CPU's this game drives): once a moment for each target and kind (each turret glob counts)
function netClaim(k, B, A, at) {
  if (!NMI() || !A || !B || !netMe(A) || ally(A, B)) return; const slot = NM.slotOf.get(B); if (slot === undefined) return;
  const now = performance.now(), ct = A.netClaimT || (A.netClaimT = {}), key = k + ':' + slot; if (k !== 'shot' && ct[key] > now - 450) return; ct[key] = now;
  const q = at || B; netTell('hit', { k, target: slot, x: netR(q.x), y: netR(q.y), z: netR(q.z) }, A);
}
// the paint an effect of yours leaves, sent in batches (now: at once)
function netPaint(k, x, y, z, D, now) {
  if (!NMI() || !D || !netMe(D) || !(y > -Infinity)) return; const Q = D.netPaintQ || (D.netPaintQ = {}), q = Q[k] || (Q[k] = []);
  q.push([netR(x), netR(y), netR(z)]); if (now || q.length >= 12) netPaintFlush(D, k);
}
function netPaintFlush(D, k) { const q = D.netPaintQ && D.netPaintQ[k]; if (!q || !q.length) return; D.netPaintQ[k] = []; netTell('paint', { k, pts: q }, D); }
function netFx(k, d, D) { if (NMI() && D && netMe(D)) netTell('fx', { k, d }, D); }
// another player's effect played here: nothing of it is sent
function netEcho(fn) { const was = NM.echo; NM.echo = true; try { fn(); } finally { NM.echo = was; } }
// ---- what the server says
function netItemSpawn(m) {
  if (!m || powers.some(q => q.id === m.id)) return; const dropped = Number.isInteger(m.dropped);
  const pw = { id: m.id, phase: Math.random() * 6, pop: 0, grace: dropped ? 2.5 : 0, owner: dropped ? netBlob(m.dropped) : null, age: 0 };
  placePower(pw, PU[m.kind] ? m.kind : 'roller', [m.x, m.y, m.z]); powers.push(pw);
  if (state === 'play' && !dropped && Math.hypot(P.x - m.x, P.z - m.z) < 16) AU.pop();
}
function netItemGone(m) {
  const pw = powers.find(q => q.id === m.id);
  if (pw) { const near = state === 'play' && Math.hypot(P.x - pw.x, P.z - pw.z) < 16; itemPop(pw); if (m.why === 'stale' && near) AU.pop(); return; }
  const T = trapList.find(q => q.id === m.id); if (T) trapPop(T, null, true);
}
function netItemTaken(m) {
  const D = netBlob(m.slot), pw = powers.find(q => q.id === m.id);
  if (!D || !ACTIVE.includes(D)) { if (pw) itemPop(pw); return; }
  D.held = null; D.held2 = null; // (what it held goes back on the stage: the server puts it there)
  if (pw) collectPower(D, pw); else { D.held = PU[m.kind] ? m.kind : 'roller'; D.heldT = 0; if (D === P) { AU.pop(); buzz(12); } }
}
function netItemUsed(m) {
  const D = netBlob(m.slot); if (!D || !ACTIVE.includes(D)) return;
  if (netMe(D)) { if (m.kind === 'trap' && m.trap) { for (let i = trapList.length - 1; i >= 0; i--) if (trapList[i].owner === D && !trapList[i].id) { trapList[i].id = m.trap; break; } } return; } // (yours went off when you used it)
  if (D.st !== 'play') return;
  if (Number.isFinite(m.yaw)) D.yaw = m.yaw;
  netEcho(() => {
    if (m.orb) { D.orbSaved = null; orbGift(D, m.kind); return; }
    if (!PU[m.kind]) return;
    D.held = m.kind; NM.echoBoom = m.kind === 'boom' ? { yaw: Number.isFinite(m.yaw) ? m.yaw : D.yaw, curve: m.curve === -1 ? -1 : 1, tgt: Number.isInteger(m.tgt) ? netBlob(m.tgt) : null } : null;
    try { useHeld(D); } finally { NM.echoBoom = null; }
    if (m.kind === 'trap') { const T = trapList[trapList.length - 1]; if (T && T.owner === D) { T.id = m.trap; if (Number.isFinite(m.x)) { T.x = m.x; T.z = m.z; T.g.position.set(T.x, T.y, T.z); } } }
  });
}
// a use the server refused (it saw something else going on): a trap dropped here for it is taken back up
function netUseRefused(D, why) { if (why === 'disconnected' || why === 'timeout') return; for (let i = trapList.length - 1; i >= 0; i--) if (trapList[i].owner === D && !trapList[i].id) { trapPop(trapList[i], null, true); break; } }
function netItemTrap(m) { const T = trapList.find(q => q.id === m.id); if (T) trapPop(T, netBlob(m.slot), !!m.safe); }
function netOrbSpawn(m) {
  orb.on = true; orb.k = 0; orb.pull = 0; orb.stay = true; orb.netId = m.id; orb.x = orb.tx = m.x; orb.z = orb.tz = m.z; orb.base = m.y; orb.y = m.y + 1.15; orb.ph = Math.random() * 6.28;
  orb.g.visible = true; orb.ring.visible = true; if (state === 'play') { AU.orb(); kick($('orbFlash'), 'on'); popText('Orb!'); }
  for (let i = 0; i < 16; i++) { const a = i / 16 * 6.283; spawnPart(orb.x, orb.y, orb.z, Math.cos(a) * 2.5, (Math.random() - 0.3) * 3, Math.sin(a) * 2.5, 0.5, orbPartMats[i % orbPartMats.length], 0.5); }
}
function netOrbTick(dt) { if (!orb.on) return; orb.k = Math.min(1, orb.k + dt * 1.8); orb.y = orb.base + 1.15 + Math.sin(runT * 2.2 + orb.ph) * 0.12; }
function netOrbTaken(m) {
  const D = netBlob(m.slot);
  if (orb.on) { orb.on = false; orb.pull = 0; orb.g.visible = false; orb.ring.visible = false; for (let i = 0; i < 26; i++) { const a = Math.random() * 6.283; spawnPart(orb.x, orb.y, orb.z, Math.cos(a) * 4, 1 + Math.random() * 4, Math.sin(a) * 4, 0.55, orbPartMats[i % orbPartMats.length], 0.6); } shockwave(orb.x, orb.base, orb.z, 2.6, 0xFFFFFF); }
  if (!D || !ACTIVE.includes(D) || m.at === 'now') return; // (one already in the slot: it went off at once; the server says how)
  const keep = !!m.keep; D.orbSaved = m.gift; D.orbT = keep ? Infinity : ORB_HOLD; if (D.ai) D.ai.orbWait = 0.5 + Math.random() * 2.2; emote(D, 'glee', 0.8);
  if (D === P) { AU.pop(); buzz([10, 20, 10]); const w = ORB_LBL[m.gift] || 'Orb'; banner(keep ? 'Orb saved!' : w + ' ready!', keep ? say('Keep it as long as you like. Tap it to use it', 'Keep it as long as you like. Press C to use it') : say('Tap it to use it', 'Press C to use it')); }
}
function netOrbLost(m) { const D = netBlob(m.slot); if (D && D.orbSaved) orbFade(D); }
function netFreeze(m) {
  const A = netBlob(m.by), left = Math.max(0.3, (m.until - netNow()) / 1000);
  for (const s of m.slots || []) { const B = netBlob(s); if (B && B.st === 'play') freezeOne(B, left); }
  for (const s of m.dodged || []) { const B = netBlob(s); if (B === P) { popText('Perfect dodge!'); buzz([8, 20, 8]); AU.ready && AU.ready(); } else if (B && A === P) popText(nameOf(B) + ' dodged it!'); }
  if (A === P) banner('Flash freeze!', (m.slots || []).length ? 'They’re frozen. Go get them' : 'Nobody caught');
}
function netShot(m) {
  const B = netBlob(m.slot), A = netBlob(m.by); if (!B || !A) return;
  const dx = B.x - A.x, dz = B.z - A.z, l = Math.hypot(dx, dz) || 1, nx = dx / l, nz = dz / l;
  if (netMe(B)) { if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); } B.paint = Math.min(B.paint, m.paint); if (B.paint <= 0.001 && !B.dry) { B.paint = 0; goDry(B); } B.kx = nx * SHOT_PUSH * 0.45; B.kz = nz * SHOT_PUSH * 0.45; B.lastHit = { by: A, t: runT }; }
  B.squash = 0.85; B.wob = 1; fxKnock(B, nx, nz, 0.35); emote(B, 'ouch', 0.7); emote(A, 'glee', 0.7); shockwave(B.x, B.y + 0.1, B.z, 1.1, TEAMS[A.team].wet);
  if (hearable(B)) AU.bonk(0.7);
  if (B === P) { shake = Math.max(shake, 0.22); buzz([15, 20, 15]); pingTank(1.2); } else if (A === P) buzz(10);
  if (m.stun) turretStun(B, A, nx, nz);
}
function netUnGiant(m) { const B = netBlob(m.slot), A = netBlob(m.by) || B; if (B && B.giantT > 0) { NM.rule = true; try { unGiant(B, A); } finally { NM.rule = false; } } }
// a storm's drop, where its caster's game dropped it
function netStormDrop(D, x, z, gy) {
  const S = stormList.find(q => q.by === D && !q.end); if (!S || !(gy > -Infinity)) return;
  const d = stormTake(D); d.x = x; d.z = z; d.gy = gy; d.t = 0; d.sx = S.cx + (Math.random() - 0.5) * 2.4; d.sz = S.cz + (Math.random() - 0.5) * 2.4; d.sy = S.cy - 0.9; d.dodge = null;
  d.ring.position.set(x, gy + 0.07, z); d.fill.position.set(x, gy + 0.06, z); d.ring.scale.setScalar(0.3); d.fill.scale.setScalar(0.3);
  S.drops.push(d);
}
function netFxIn(m) {
  const D = netBlob(m.slot); if (!D || netMe(D) || !ACTIVE.includes(D) || !Array.isArray(m.d)) return; const d = m.d;
  if (m.k === 'drop' && d.length >= 3) netStormDrop(D, +d[0], +d[1], +d[2]);
  else if (m.k === 'rland' && d.length >= 3 && D.rocket) { D.x = +d[0]; D.y = +d[1]; D.z = +d[2]; netEcho(() => rocketLand(D)); }
}
// another player's effects, played on its puppet (where it is is the server's)
function netFxPuppet(D, dt, f) {
  const F = RMNet.FLAGS;
  if (D.giantT > 0) { D.giantT -= dt; if (D.giantT <= 0) { D.giantT = 0; graceOut(D); D.wob = 1; } }
  if (f & F.GIANT) D.netGiant = true; else if (D.netGiant) { D.netGiant = false; if (D.giantT > 0.25) D.giantT = 0.25; } // (shrunk early: a pound)
  if (D.power) { D.power.t -= dt; if (D.power.t <= 0) { if (D.power.type === 'roller') graceOut(D); D.power = null; } }
  if (D.turret) stepTurret(D, dt);
  if (D.whirl) whirlTick(D, dt);
  if (D.rocket) { const R = D.rocket; R.t += dt; R.ph = D.vy > 2 ? 'up' : D.vy < -4 ? 'dive' : R.ph === 'dive' ? 'dive' : 'hover'; D.fxAcc = D.fxAcc || 0; rocketFx(D, dt); if (R.t > 14) D.rocket = null; }
  if (D.orbSaved && D.orbT < Infinity) { D.orbT -= dt; if (D.orbT <= -1) D.orbSaved = null; }
}
// each frame: the orb's bob, the pick-ups popping in, and what paint is waiting goes
function netItemsFrame(dt) {
  netOrbTick(dt);
  for (const pw of powers) { if (pw.pop < 1) pw.pop = Math.min(1, pw.pop + dt * 3); if (pw.grace > 0) pw.grace -= dt; }
  NM.paintT = (NM.paintT || 0) - dt;
  if (NM.paintT <= 0) { NM.paintT = 0.2; for (const D of [P, ...(NM.mine || [])]) if (D && D.netPaintQ) for (const k in D.netPaintQ) netPaintFlush(D, k); }
}
// back after a dropped connection: what's out there, and what's in your pockets
function netItemsResume(m) {
  if (!NMI() || !Array.isArray(m.items)) return;
  for (const pw of powers.slice()) if (!m.items.some(i => i.id === pw.id)) itemPop(pw);
  for (const i of m.items) netItemSpawn(i);
  if (m.orb) { if (!orb.on || orb.netId !== m.orb.id) netOrbSpawn(m.orb); } else if (orb.on) { orb.on = false; orb.g.visible = false; orb.ring.visible = false; }
  if (Array.isArray(m.pockets) && P.st === 'play') P.held = PU[m.pockets[NM.slot]] ? m.pockets[NM.slot] : null;
  if (m.myOrb && !P.orbSaved) { P.orbSaved = m.myOrb; P.orbT = ORB_HOLD; } else if (!m.myOrb) P.orbSaved = null;
}
"""

FREEZE_ONE = r"""
// (v427) frozen where it stands, for t seconds (offline at the flash; online when the server says)
function freezeOne(B, t) {
  const fr = $('frost');
"""

def apply(s):
    # ---- the kit goes with the stage; the server's pockets at Go
    s = rep(s, "  NM.net.sendLayout(L);", "  NM.net.sendLayout(L, netKit()); // (v427: and what you take into it)")
    s = rep(s, "function netGo() { for (const D of ACTIVE) { D.held = null; D.held2 = null; D.heldT = 0; } for (const D of NM.others) D.rank = NM.ranks.get(D) || 1; NM.wxI = -1; NM.phase = 'play'; }\n",
               "function netGo() { for (const D of ACTIVE) { D.held = null; D.held2 = null; D.heldT = 0; } for (const D of NM.others) D.rank = NM.ranks.get(D) || 1; NM.wxI = -1; NM.phase = 'play';\n"
               "  // (v427) the server's pockets: what each starts with\n"
               "  const pk = NM.s && NM.s.pockets; if (NMI() && Array.isArray(pk)) for (const [slot, D] of NM.seats) if (ACTIVE.includes(D) && PU[pk[slot]]) { D.held = pk[slot]; if (D !== P) D.heldT = -(2 + Math.random() * 6); } }\n" + JS)
    # ---- a use the server refused: undone here where it can be
    s = rep(s, "if (NM !== nm || r.ok) return; nm.refused++; nm.why.push(a + ':' + r.reason);", "if (NM !== nm || r.ok) return; nm.refused++; nm.why.push(a + ':' + r.reason); if (a === 'use') netUseRefused(P, r.reason);")
    s = rep(s, "if (NM !== nm || !r || r.ok) return; nm.refused++; nm.why.push('cpu ' + a + ':' + r.reason);", "if (NM !== nm || !r || r.ok) return; nm.refused++; nm.why.push('cpu ' + a + ':' + r.reason); if (a === 'use') netUseRefused(D, r.reason);")
    # ---- the server's messages
    s = rep(s, "  on('pot', netPot); on('potEject', netEject); on('act', netFoeAct); on('resume', netResume); on('out', netOut);\n",
               "  on('pot', netPot); on('potEject', netEject); on('act', netFoeAct); on('resume', netResume); on('out', netOut);\n"
               "  on('itemSpawn', netItemSpawn); on('itemGone', netItemGone); on('itemTaken', netItemTaken); on('itemUsed', netItemUsed); on('itemTrap', netItemTrap); // (v427)\n"
               "  on('orbSpawn', netOrbSpawn); on('orbTaken', netOrbTaken); on('orbLost', netOrbLost); on('freeze', netFreeze); on('shot', netShot); on('unGiant', netUnGiant); on('fx', netFxIn);\n")
    s = rep(s, "  if (state === 'play' && P.st === 'play' && m.self.st === 'play') netCorrect({ x: m.self.x, y: m.self.y, z: m.self.z, yaw: m.self.yaw });\n}",
               "  if (state === 'play' && P.st === 'play' && m.self.st === 'play') netCorrect({ x: m.self.x, y: m.self.y, z: m.self.z, yaw: m.self.yaw });\n  netItemsResume(m); // (v427)\n}")
    # ---- each frame online: the items' bits; the others' effects on their puppets
    s = rep(s, "    if (NM) netContact(); else { blobContact(); updateOrb(dt);", "    if (NM) { netContact(); if (NMI()) netItemsFrame(dt); } else { blobContact(); updateOrb(dt);")
    s = rep(s, "  D.flung = !!(f & F.FLUNG); const dry = !!(f & F.DRY); if (dry && !D.dry) { D.dry = true; D.wob = 1; } else if (!dry) D.dry = false;\n  netTrail(",
               "  D.flung = !!(f & F.FLUNG); const dry = !!(f & F.DRY); if (dry && !D.dry) { D.dry = true; D.wob = 1; } else if (!dry) D.dry = false;\n  if (NMI()) netFxPuppet(D, dt, f); // (v427)\n  netTrail(")
    # ---- only the server hands out pick-ups and the orb online
    s = rep(s, "  if (D.st === 'play') for (const pw of powers) if (pw.g && !(pw.grace > 0 && pw.owner === D)",
               "  if (D.st === 'play' && !NM) for (const pw of powers) if (pw.g && !(pw.grace > 0 && pw.owner === D)")
    s = rep(s, "function orbPound(D, R) { if (orb.on", "function orbPound(D, R) { if (NM) return; if (orb.on")
    # ---- using one: it goes off here at once, and the server is told
    s = rep(s, "function useHeld(D) {\n  if (!D.held || D.whirl ||", "function useHeld(D) {\n  const echo = !!(NM && NM.echo); // (v427: another player's, played here)\n  if (!echo && (!D.held || D.whirl ||")
    s = rep(s, "D.giantT > 0 || D.knockT > 0) return false;\n  const type = D.held; if ((type === 'turret' || type === 'whirl') && D.air) return false;\n  D.held = null; D.heldT = 0;\n",
               "D.giantT > 0 || D.knockT > 0)) return false;\n  const type = D.held; if (!echo && (type === 'turret' || type === 'whirl') && D.air) return false;\n  D.held = null; D.heldT = 0;\n"
               "  if (!echo && NMI() && netMe(D) && type !== 'boom') netAct('use', { yaw: netR(D.yaw) }, D); // (v427; the boomerang says how it was thrown)\n")
    s = rep(s, "  const yaw = tgt ? Math.atan2(tgt.x - D.x, tgt.z - D.z) : D.yaw, curve = Math.abs(D.turn || 0) > 0.3 ? Math.sign(D.turn) : (boomSide = -boomSide);\n",
               "  let yaw = tgt ? Math.atan2(tgt.x - D.x, tgt.z - D.z) : D.yaw, curve = Math.abs(D.turn || 0) > 0.3 ? Math.sign(D.turn) : (boomSide = -boomSide);\n"
               "  if (NM && NM.echo && NM.echoBoom) { const e = NM.echoBoom; yaw = e.yaw; curve = e.curve; tgt = e.tgt && e.tgt.st === 'play' ? e.tgt : null; } // (v427: another player's, thrown as they threw it)\n"
               "  else if (NMI() && netMe(D)) netAct('use', { yaw: netR(yaw), curve, tgt: tgt ? NM.slotOf.get(tgt) : undefined }, D);\n")
    s = rep(s, "  const g = D.orbSaved; D.orbSaved = null; shockwave(D.x, D.y + 0.1, D.z, 2.2, 0xFFFFFF); orbGift(D, g); return true;",
               "  const g = D.orbSaved; D.orbSaved = null; if (NMI() && netMe(D)) netAct('use', { orb: 1, yaw: netR(D.yaw) }, D); shockwave(D.x, D.y + 0.1, D.z, 2.2, 0xFFFFFF); orbGift(D, g); return true;")
    # ---- the hits: online, a claim for the server (yours only); never a knock-out here
    s = rep(s, "  if (NM && !NM.rule) { if (D === P && !NM.selfKo",
               "  if (NM && !NM.rule) { if (by && NET_CLAIM[reason]) netClaim(NET_CLAIM[reason], D, by); /* (v427) */ if (D === P && !NM.selfKo")
    s = rep(s, "function poundHit(O, D, reason) { if (O.giantT > 0)", "function poundHit(O, D, reason) { if (NM && !NM.rule) return knockOut(O, reason, D); if (O.giantT > 0)")
    s = rep(s, "      knockOut(F, 'boom', O); if (O === P)", "      if (NM) netClaim('boom', F, O, B); else knockOut(F, 'boom', O); if (O === P)")
    s = rep(s, "    poundHit(O, D, 'storm');", "    if (NM) netClaim('storm', O, D, { x, y: gy, z }); else poundHit(O, D, 'storm');")
    s = rep(s, "    poundHit(O, D, 'bomb'); kos++;", "    if (NM) netClaim('bomb', O, D, { x, y: gy, z }); else poundHit(O, D, 'bomb'); kos++;")
    s = rep(s, "    if (hit) { shotHit(hit, s);", "    if (hit) { if (NM) { netClaim('shot', hit, s.by, s); hit.wob = Math.max(hit.wob || 0, 0.6); } else shotHit(hit, s);")
    s = rep(s, "  for (const O of foes(D)) {\n    if (!NM && matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && !O.rocket",
               "  for (const O of foes(D)) {\n    if (NM) { if (matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && Math.hypot(O.x - D.x, O.z - D.z) < koR + 0.4) netClaim('rocket', O, D, D); continue; } // (v427)\n    if (!NM && matchLeft > 0 && (O.st === 'play' || O.st === 'hide') && !O.rocket")
    s = rep(s, "  // the ground heaves: anyone standing nearby gets bounced off their feet\n  for (const B of foes(D)) { const bd = Math.hypot(B.x - D.x, B.z - D.z);", "  // the ground heaves: anyone standing nearby gets bounced off their feet\n  for (const B of foes(D)) { if (NM) break; const bd = Math.hypot(B.x - D.x, B.z - D.z); // (v427: online, nobody's thrown about by it)")
    s = rep(s, "function rocketLand(D) {\n", "function rocketLand(D) {\n  if (NMI() && netMe(D)) { netFx('rland', [netR(D.x), netR(D.y), netR(D.z)], D); netPaint('rocket', D.x, D.y, D.z, D, true); } // (v427: where it came down)\n")
    # a giant or a roller rolling into a rival, and a giant walking into one
    s = rep(s, "function netTouch(A, B) {\n  if (A.st !== 'play' || B.st !== 'play') return;\n",
               "function netTouch(A, B) {\n  if (A.st !== 'play' || B.st !== 'play') return;\n"
               "  if (NMI() && !ally(A, B) && Math.abs(A.y - B.y) < 1.6) { const dd = Math.hypot(B.x - A.x, B.z - A.z), g = A.giantT > 0, rl = !!(A.power && A.power.type === 'roller'); // (v427)\n"
               "    if ((g || rl) && A.rollT > 0 && dd < (g ? PR * GIANT_K : PR) + PR + 0.1) netClaim('crush', B, A, A); else if (g && dd < PR * GIANT_K + PR + 0.1 && !(B.flatT > 0)) netClaim('squash', B, A, A); }\n")
    # ---- the paint they leave
    s = rep(s, "addSplat(D.x, D.y, D.z, D.yaw, WHIRL_TRAIL, dryClock, false, false, tcode(D), 0.25); }", "addSplat(D.x, D.y, D.z, D.yaw, WHIRL_TRAIL, dryClock, false, false, tcode(D), 0.25); netPaint('whirl', D.x, D.y, D.z, D); }")
    s = rep(s, "  addSplat(D.x, D.y, D.z, D.yaw, WHIRL_TRAIL * 1.45, dryClock, false, false, tcode(D), 0.15);", "  addSplat(D.x, D.y, D.z, D.yaw, WHIRL_TRAIL * 1.45, dryClock, false, false, tcode(D), 0.15); netPaint('whirlEnd', D.x, D.y, D.z, D, true);")
    s = rep(s, "addPoint(B.x, gy, B.z, B.yaw, dryClock, B.stroke, BOOM_W, tcode(O), B.rb, [B.x, gy, B.z]); }", "addPoint(B.x, gy, B.z, B.yaw, dryClock, B.stroke, BOOM_W, tcode(O), B.rb, [B.x, gy, B.z]); netPaint('boom', B.x, gy, B.z, O); }")
    s = rep(s, "  if (!(y > -Infinity)) return;\n  addSplat(s.x, y, s.z,", "  if (!(y > -Infinity)) return;\n  netPaint('shot', s.x, y, s.z, s.by);\n  addSplat(s.x, y, s.z,")
    s = rep(s, "  const D = S.by, x = d.x, z = d.z, gy = d.gy;\n", "  const D = S.by, x = d.x, z = d.z, gy = d.gy; netPaint('storm', x, gy, z, D, true);\n")
    s = rep(s, "  addSplat(x, gy, z, Math.random() * 6.2832, BOMB_R, dryClock, false, true, tcode(D));", "  addSplat(x, gy, z, Math.random() * 6.2832, BOMB_R, dryClock, false, true, tcode(D)); netPaint('bomb', x, gy, z, D, true);")
    # ---- storms: the caster's game drops them, the others are told where
    s = rep(s, "    while (live && S.t >= S.next) {", "    while (live && S.t >= S.next && !(NMI() && !netMe(D))) {")
    s = rep(s, "    S.drops.push(d); return;\n", "    S.drops.push(d); netFx('drop', [netR(x), netR(z), netR(gy)], D); return;\n")
    # ---- traps: the server's ruling online (a knock-out; a roll through it pops it)
    s = rep(s, "    if (state !== 'play') continue; const armed = !(T.arm > 0);", "    if (state !== 'play' || NM) continue; const armed = !(T.arm > 0); // (v427: online, the server says when one goes off)")
    s = rep(s, "  if (!NM) { emote(T.owner, 'glee', 0.9); hitStop(0.06, T.owner, B); return knockOut(B, 'trap', T.owner); } // (v309: a trap is a knock-out now)\n",
               "  if (!NM) { emote(T.owner, 'glee', 0.9); hitStop(0.06, T.owner, B); return knockOut(B, 'trap', T.owner); } // (v309: a trap is a knock-out now)\n"
               "  if (NM) { emote(T.owner, 'glee', 0.9); hitStop(0.06, T.owner, B); return; } // (v427: online the server knocks them out)\n")
    # ---- the Flash Freeze: online the server says who; tapping out early tells it
    i = s.index("function freezeFlash(F) {")
    a0 = s.index("    if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }\n    B.frozenT = FREEZE_T;", i)
    a1 = s.index("frostHeld = true; }\n", a0) + len("frostHeld = true; }\n")
    block = s[a0:a1]
    assert block.count("B.frozenT = FREEZE_T; B.stunT = Math.max(B.stunT || 0, FREEZE_T);") == 1 and block.count(" n++;") == 1
    body = block.replace("B.frozenT = FREEZE_T; B.stunT = Math.max(B.stunT || 0, FREEZE_T);", "B.frozenT = t; B.stunT = Math.max(B.stunT || 0, t);").replace(" n++;", "")
    s = s[:a0] + "    freezeOne(B, FREEZE_T); n++;\n" + s[a1:]
    s = rep(s, "function freezeFlash(F) {", FREEZE_ONE.lstrip('\n') + body + "}\nfunction freezeFlash(F) {")
    s = rep(s, "    if (B === D || ally(B, D) || B.st !== 'play' || B.rocket) continue; // (down in a basin, knocked out, or up in a rocket: untouched)\n",
               "    if (B === D || ally(B, D) || B.st !== 'play' || B.rocket) continue; // (down in a basin, knocked out, or up in a rocket: untouched)\n    if (NM) continue; // (v427: online the server says who)\n")
    s = rep(s, "  if (D === P) banner('Flash freeze!', n ? ", "  if (D === P && !NM) banner('Flash freeze!', n ? ")
    s = rep(s, "  if (D.frozenT > 0) { D.frozenT -= dt; if (D.frozenT <= 0) { D.frozenT = 0; thawFx(D); } }",
               "  if (D.frozenT > 0) { D.frozenT -= dt; if (D.frozenT <= 0) { D.frozenT = 0; thawFx(D); if (NMI() && netMe(D) && D.iceTap > 0) netAct('thaw', null, D); } } // (v427: tapped out early: the server's told)")
    return s
