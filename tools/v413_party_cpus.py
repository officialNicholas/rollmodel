"""v413: a party plays against CPUs online (the user: "I'm not seeing how to play with a friend in my party, but also go against
CPU. So let's say it's me and one other person. And I'm trying to play a three-way with a CPU or a four-way showdown with two
CPUs. Either I'm not seeing how to do that, and it's not intuitive, or it's not in place, and we need to add it").

The game server has had it since v404 (the leader's pick says "against CPUs", the match starts at once, unrated, and one of the
party's games drives the CPU players: their states and moves go to the server from that game, which referees them like anyone),
but the game never finished its side: it still said it was v394 when it connected, so the server never offered CPUs, and nothing
drove them. Now:
- The host's Choose Event in a party has a group of its own, "Play now with CPUs": two of you get a 3-way with 1 CPU, a Showdown
  with 2 CPUs and a 2v2 (you two against two CPUs); three of you a Showdown with 1 CPU and a 2v2 with 1 CPU. Each card's line-up
  shows a CPU badge in each CPU's place (a ? is still a person to be found). Picking one tells the server "against CPUs" (any
  other card says "not"), and the friends see it beside their Ready: "Showdown with 2 CPUs".
- The game says it is this version when it connects (client rm-413), so the server offers CPUs to a party whose games all can, and
  fills a long matchmaking wait (two people or more) with CPUs.
- The game picked to drive the CPUs (the one with the steadiest connection) runs them with its own CPU minds (medium), as it does
  offline, in their places on the stage, and sends each one's state every frame and its moves (jump, roll, fling, pound, landings,
  pots, stomps, falls) as their own; the referee's rulings for them (corrections, knock-outs, pots, flattenings, pushes, respawns)
  come back to it. On the other phones they're drawn like any rival, by their CPU names (no @). If the game driving them leaves,
  they leave with it (the server's rule).
- While a party of two or more searches, its Play button says CPUs fill in if it takes a while."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

import re

CSS = """/* (v413) a CPU in a party event card's line-up */
.pyf.pycpu{width:40px;height:40px;background:linear-gradient(180deg,#4B4560,#2A2537);box-shadow:inset 0 0 0 2px rgba(255,255,255,.22);color:#E8E2F6;font:900 10.5px/1 var(--font-head);letter-spacing:.06em}
@media (max-height:520px) and (min-aspect-ratio:1/1){.pyf.pycpu{width:34px;height:34px;font-size:9.5px}}
.evpy.pyc .evbar{background:#3BB273}
"""

EV_JS = r"""function ptEvRender() {
  if (!ptEvOn()) return;
  const p = ON.party, me = ptMe();
  if (!ptOn() || ON.match || !me || p.leader !== me.id || me.ready || p.state !== 'idle') return closeEvents();
  const n = p.members.length, mem = [me].concat(p.members.filter(m => m !== me)), ic = id => { const e = $(id) && $(id).querySelector('.evic'); return e ? e.innerHTML : ''; };
  const face = e => e === '?' ? ON_MYS : e === 'C' ? PY_CPU : '<span class="pyf' + (e === me ? ' me' : '') + '">' + frFace(e.look) + '</span>';
  const card = (x, cpu) => { const d = PY_EV[x.mode] || PY_EV.ffa, w = cpu ? ptEvCpuWords(x, n) : ptEvWords(x, n), art = stageArtOf(x.mode === 'duel' && VOTE_STAGES.includes(stageSel) ? stageSel : d.art);
    const line = (cpu ? ptEvCpuSides(x, mem) : ptEvSides(x, mem)).map(s => '<span class="pyside">' + s.map(face).join('') + '</span>').join('<i class="pyvs">vs</i>');
    return '<div class="evcard evpy' + (cpu ? ' pyc' : '') + (x.on ? '' : ' soon') + '" data-pyev="' + x.mode + '"' + (cpu ? ' data-cpu="1"' : '') + ' style="--ec:' + d.c + '"><button class="evmain" type="button" data-pyev="' + x.mode + '"' + (cpu ? ' data-cpu="1"' : '') + ' aria-label="' + frEsc(w.say) + '"' + (x.on ? '' : ' aria-disabled="true"') + '>'
      + '<span class="evbar"><i>' + w.bar + '</i></span><span class="evtop"><span class="evic" aria-hidden="true">' + ic(d.ic) + '</span><span class="evtx"><b>' + frEsc((PY_FULL[x.mode] || x.mode) + (cpu ? ptCpuWith(x.cpus) : '')) + '</b><small>' + w.sub + '</small></span></span>'
      + '<span class="evart pyart" aria-hidden="true"><img alt="" src="' + (art || '') + '"><span class="pyline">' + line + '</span></span></button></div>'; };
  const ord = (a, b) => ['duo', 'trio', 'ffa', 'duel'].indexOf(a.mode) - ['duo', 'trio', 'ffa', 'duel'].indexOf(b.mode);
  const online = p.modes.filter(x => x.plan !== 'private').sort(ord), own = p.modes.filter(x => x.plan === 'private'), cpus = p.modes.filter(x => x.cpus > 0).sort((a, b) => ['trio', 'ffa', 'duo'].indexOf(a.mode) - ['trio', 'ffa', 'duo'].indexOf(b.mode));
  const h = (online.length ? '<h3 class="pyevh evpy">With players online</h3>' + online.map(x => card(x, false)).join('') : '') + (cpus.length ? '<h3 class="pyevh evpy">Play now with CPUs</h3>' + cpus.map(x => card(x, true)).join('') : '') + (own.length ? '<h3 class="pyevh evpy">Just your party</h3>' + own.map(x => card(x, false)).join('') : '');
  const g = $('evGrid'); if (g._py === h) return; g._py = h;
  g.querySelectorAll('.evpy').forEach(e => e.remove()); g.insertAdjacentHTML('afterbegin', h);
}
// (v413) a party against CPUs: the line-up (a CPU badge for each CPU), the words, and the pick
const PY_CPU = '<span class="pyf pycpu" aria-hidden="true">CPU</span>';
const ptCpuWith = k => ' with ' + k + (k === 1 ? ' CPU' : ' CPUs');
function ptEvCpuSides(x, mem) {
  const C = Array.from({ length: Math.max(0, x.cpus | 0) }, () => 'C');
  if (x.mode === 'duo') { const all = mem.concat(C); return [all.slice(0, 2), all.slice(2, 4)]; }
  return mem.concat(C).map(e => [e]);
}
function ptEvCpuWords(x, n) {
  const k = x.cpus | 0, cw = k === 1 ? '1 CPU' : k + ' CPUs', who = ['', '', 'you two', 'you three'][n] || 'your party';
  const bar = !x.on ? 'Coming soon' : 'Starts now · no wait';
  const sub = x.mode === 'duo' ? (n === 2 ? 'You two vs ' + cw : n === 3 ? 'Two of you vs one and a CPU' : 'Two teams') : x.mode === 'trio' ? 'Most paint wins' : 'Last one standing';
  const say = (PY_FULL[x.mode] || x.mode) + ' with ' + cw + ': ' + who + ' and ' + cw + ', no waiting' + (x.mode === 'duo' ? ', on two teams' : ', each for their own');
  return { bar, sub, say };
}
// a pick: the party's event (against CPUs or not), and the host is ready (the friends who are ready already start it)
async function ptEvPick(m, cpu) {
  const p = ON.party, me = ptMe(), x = p && p.modes.find(q => q.mode === m);
  if (!p || !me || !ON.net || p.leader !== me.id || p.state !== 'idle') return closeEvents();
  if (!x || !x.on || (cpu && !(x.cpus > 0))) { AU.nope(); buzz(8); return frToast('<span>' + (x ? 'Coming soon' : 'Not for a party this size') + '</span>'); }
  AU.pop(); buzz(12); closeEvents();
  try { await ON.net.partyVote(m, !!cpu); await ON.net.partyReady(true); } catch (e) { frToast('<span>' + frEsc(onReqText(e)) + '</span>'); }
}
$('evGrid').addEventListener('click', e => { const b = e.target.closest('.evpy [data-pyev]'); if (!b || !ptEvOn()) return; AU.init(); ptEvPick(b.dataset.pyev, b.dataset.cpu === '1'); });
"""

NET_JS = r"""// (v413) the CPU players this game drives in an online match (NM.mine): their own CPU minds, their moves and states sent as theirs
const netMine = D => !!(NM && NM.mine && NM.mine.has(D));
const netMe = D => D === P || netMine(D);
const netStateOf = D => ({ x: D.x, y: D.y, z: D.z, yaw: D.yaw, spd: D.st === 'hide' ? 0 : D.spd, vy: D.vy, air: D.air, rolling: D.rollT > 0, charging: D.charging, slam: !!D.slam, hidden: D.st === 'hide', flung: !!D.flung, dry: !!D.dry, missile: !!D.missile, paint: clamp(D.paint, 0, 1), aim: D.charging ? clamp(D.charge || 0, 0, 1) : 0 });
function netBotAct(D, a, data) {
  const nm = NM, slot = nm.slotOf.get(D); if (slot === undefined) return;
  const back = netAhead * 1000, ts = nm.net.serverNow() - back;
  if (D.netSend && state === 'play' && (D.st === 'play' || D.st === 'hide')) nm.net.sendBotState(slot, netStateOf(D), true, ts);
  nm.net.botAction(slot, a, Object.assign({ ts, vt: nm.net.renderTime() - back }, data || {})).then(r => { if (NM !== nm || !r || r.ok) return; nm.refused++; nm.why.push('cpu ' + a + ':' + r.reason); if (nm.why.length > 8) nm.why.shift(); if (a === 'enterPot' && D.st === 'hide' && r.reason !== 'disconnected' && r.reason !== 'timeout') netUnPot(r.reason, D); });
}
function netBotsFrame() {
  for (const D of NM.mine) {
    const slot = NM.slotOf.get(D); if (slot === undefined || !ACTIVE.includes(D)) continue;
    if (!D.netSend && state === 'play' && NM.phase !== 'end' && NM.startAt && netNow() >= NM.startAt && D.st === 'play' && !D.air) D.netSend = true;
    if (D.netSend && state === 'play' && NM.phase !== 'end' && (D.st === 'play' || D.st === 'hide')) NM.net.sendBotState(slot, netStateOf(D));
  }
}
// the referee puts one of them back where it says (as netCorrect does for you)
function netBotCorrect(m) {
  const D = netBlob(m.slot); if (!D || !netMine(D) || D.st !== 'play') return; NM.corr++;
  if (D.charging) clearCharge(D);
  D.x = m.x; D.y = m.y; D.z = m.z; D.yaw = m.yaw; D.spd = 0; D.vy = 0; D.kx = D.kz = 0; D.slam = false; D.missile = false; D.rollT = 0; D.dashT = 0; D.flung = false; D.flingC = 0; D.stroke++;
  const g = surfaceUnder(D.x, D.z, D.y + STEP, true); D.air = !(g > -Infinity && D.y - g < 0.06); if (!D.air) D.y = g;
}
function netBotPush(D, m) {
  if (D.charging) clearCharge(D);
  D.yaw = Math.atan2(m.dx, m.dz); D.spd = m.spd; D.vy = m.vy; D.air = true; D.stroke++; D.slam = false; D.missile = false; D.flatT = 0; D.turn = 0; D.knockT = 0.9; D.flung = false; D.flingC = 0; D.wob = 1; D.squash = 0.8;
  fxTumble(D, 0.8, Math.random() - 0.5);
}
"""

def apply(s):
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    # the SDK: the leader's pick says against CPUs or not; the hello says which game this is
    s = rep(s, "partyVote(mode) { return this._request({ t: 'partyVote', mode }); }",
               "partyVote(mode, cpu) { return this._request(typeof cpu === 'boolean' ? { t: 'partyVote', mode, cpu } : { t: 'partyVote', mode }); } // (v413: cpu, the leader's pick)")
    s = rep(s, "client: 'rm-394'", "client: 'rm-413'")
    # the party's events: a group of CPU cards
    i = s.index("function ptEvRender() {"); j = s.index("$('evGrid').addEventListener('click', e => { const b = e.target.closest('.evpy [data-pyev]');")
    j = s.index("\n", j) + 1
    assert s.count("function ptEvRender() {") == 1
    s = s[:i] + EV_JS + s[j:]
    # what the friends see beside their Ready
    s = rep(s, "if (p.state === 'starting' || p.state === 'queued' || (lead && lead.ready)) return PY_FULL[p.mode] || '';",
               "if (p.state === 'starting' || p.state === 'queued' || (lead && lead.ready)) { const x = p.cpu && p.modes.find(q => q.mode === p.mode); return (PY_FULL[p.mode] || '') + (x && x.cpus > 0 ? ptCpuWith(x.cpus) : ''); }")
    s = rep(s, "else if (p.state === 'queued') { t = 'Finding'; s = 'Tap to cancel'; cls = 'pygo'; }",
               "else if (p.state === 'queued') { t = 'Finding'; s = p.members.length >= 2 && p.mode !== 'duel' ? 'CPUs fill in if it’s slow · tap to cancel' : 'Tap to cancel'; cls = 'pygo'; }")
    # the match: which CPUs are this game's, their minds, their names
    s = rep(s, "  for (const D of [H, H2, H3]) { D.cpu = !slotOf.has(D); D.netLive = false; } // (the rivals are people: no CPU mind, no CPU pace)",
               "  NM.mine = new Set((net.bots ? net.bots() : []).map(sl => seats.get(sl)).filter(D => D && D !== P)); // (v413: the CPU players this game drives)\n"
               "  for (const D of [H, H2, H3]) { D.cpu = !slotOf.has(D) || NM.mine.has(D); D.netLive = false; D.netSend = false; D.netSelfKo = null; D.netStompAt = 0; } // (the rivals are people: no CPU mind, no CPU pace; but the CPUs this game drives think as CPUs)")
    s = rep(s, "NAMES[D.team] = p.name ? hdOf(String(p.name).slice(0, 16)) : 'Rival';",
               "NAMES[D.team] = p.cpu && p.name ? String(p.name).slice(0, 16) : p.name ? hdOf(String(p.name).slice(0, 16)) : 'Rival'; // (v413: a CPU by its name, no @)")
    s = rep(s, "AI = isShow() ? Object.assign({}, AI_LV[diff], SD_AI[diff]) : AI_LV[diff];",
               "AI = isShow() ? Object.assign({}, AI_LV[NM ? 'medium' : diff], SD_AI[NM ? 'medium' : diff]) : AI_LV[NM ? 'medium' : diff]; // (v413: online CPUs are medium)")
    s = rep(s, "for (const D of ACTIVE) if (NM && D !== P) netPuppet(D, dt); else stepBlob(D, dt);",
               "for (const D of ACTIVE) if (NM && D !== P && !netMine(D)) netPuppet(D, dt); else stepBlob(D, dt);")
    # their moves, as yours are sent
    n0 = s.count("if (NM && D === P) netAct(")
    s, n = re.subn(r"if \(NM && D === P\) netAct\('(\w+)'((?:, \{[^}]*\})?)\)", lambda m: "if (NM && netMe(D)) netAct('%s'%s, D)" % (m.group(1), m.group(2) or ', null'), s)
    assert n == n0 == 11, (n, n0)
    s = rep(s, "if (NM && D === P) netPre();", "if (NM && netMe(D)) netPre(D);")
    s = rep(s, "if (NM) { if (D === P && p.ink > 0.02) { D.rollT = 0; D.dashT = 0; D.flung = false; D.spd = 0; netPre(); enterPot(D, p); p.cool = 0; netAct('enterPot', { pot: pots.indexOf(p) }); } }",
               "if (NM) { if (netMe(D) && p.ink > 0.02) { D.rollT = 0; D.dashT = 0; D.flung = false; D.spd = 0; netPre(D); enterPot(D, p); p.cool = 0; netAct('enterPot', { pot: pots.indexOf(p) }, D); } }")
    s = rep(s, "if (NM && !NM.rule) { if (D === P && !NM.selfKo && (reason === 'fall' || reason === 'dry')) { NM.selfKo = reason; netAct('selfKo', { reason }); } return; }",
               "if (NM && !NM.rule) { if (D === P && !NM.selfKo && (reason === 'fall' || reason === 'dry')) { NM.selfKo = reason; netAct('selfKo', { reason }); } else if (netMine(D) && !D.netSelfKo && (reason === 'fall' || reason === 'dry')) { D.netSelfKo = reason; netAct('selfKo', { reason }, D); } return; }")
    s = rep(s, "function netAct(a, data) {\n  if (!NM || !NM.net) return; const nm = NM;\n",
               "function netAct(a, data, D) {\n  if (!NM || !NM.net) return; const nm = NM;\n  if (D && D !== P) return netMine(D) ? netBotAct(D, a, data) : undefined; // (v413: one of the CPUs this game drives)\n")
    # pots: a refused dive puts that one back where it was
    i = s.index("function netPre() {"); j = s.index("// each frame: where you are, to the server")
    s = s[:i] + r"""function netPre(D) { D = D || P; const q = { x: D.x, y: D.y, z: D.z, yaw: D.yaw, air: D.air }; if (D === P) NM.pre = q; else D.netPre0 = q; }
function netUnPot(why, D) {
  D = D || P; const p = D.pot, q = D === P ? NM.pre : D.netPre0; if (p) { if (p.occ === D) p.occ = null; p.cool = 0.6; p.bounce = 0.6; } D.pot = null; D.st = 'play'; D.stroke++; D.spd = 0; D.vy = 0; D.wob = 1;
  if (q) { D.x = q.x; D.z = q.z; D.yaw = q.yaw; } const g = surfaceUnder(D.x, D.z, (q ? q.y : D.y) + STEP, true); if (g > -Infinity && (!q || !q.air)) { D.y = g; D.air = false; } else { D.y = q ? q.y : D.y; D.air = true; }
  if (D.charging) clearCharge(D); if (why === 'occupied' && D === P) popText('Taken!');
}
""" + s[j:]
    s = rep(s, "function netFrame() {\n  if (!NM || !NM.net) return;\n", "function netFrame() {\n  if (!NM || !NM.net) return;\n  if (NM.mine && NM.mine.size) netBotsFrame(); // (v413)\n")
    s = rep(s, "const netState = () => ({ x: P.x,", NET_JS + "const netState = () => ({ x: P.x,")
    # contact: theirs too (a CPU landing on someone's head stomps)
    s = rep(s, "function netContact() { for (const B of NM.others) if (ACTIVE.includes(B)) netTouch(P, B); }",
               "function netContact() { for (const B of NM.others) if (ACTIVE.includes(B)) netTouch(P, B); for (const A of NM.mine || []) if (ACTIVE.includes(A)) for (const B of ACTIVE) if (B !== A) netTouch(A, B); }")
    s = rep(s, "  if (!ally(A, B) && A.air && A.vy < -0.5 && dy > 0.25 && dy < 0.95 && d < PR * 2 && !A.slam && !(A.assistT > 0) && B.flatT <= 0 && !(NM.stompAt > now - 400)) {\n    NM.stompAt = now; netAct('stomp', { target: NM.slotOf.get(B) });",
               "  if (!ally(A, B) && A.air && A.vy < -0.5 && dy > 0.25 && dy < 0.95 && d < PR * 2 && !A.slam && !(A.assistT > 0) && B.flatT <= 0 && !((A === P ? NM.stompAt : A.netStompAt) > now - 400)) {\n    if (A === P) NM.stompAt = now; else A.netStompAt = now; netAct('stomp', { target: NM.slotOf.get(B) }, A);")
    s = rep(s, "A.bonkCD = 0.25; A.squash = Math.max(A.squash, 0.45); A.wob = 1; AU.bonk(0.6); }",
               "A.bonkCD = 0.25; A.squash = Math.max(A.squash, 0.45); A.wob = 1; if (A === P || hearable(A)) AU.bonk(0.6); }")
    # the referee's rulings for them
    s = rep(s, "  on('correction', netCorrect);", "  on('correction', netCorrect); on('botCorrection', netBotCorrect);")
    s = rep(s, "  if (D === P) { P.x = m.x; P.y = m.y; P.z = m.z; P.spd = 0; P.vy = 0; P.air = false; }\n  NM.rule = true; try { flatten(D, A, 'stomp'); }",
               "  if (D === P || netMine(D)) { D.x = m.x; D.y = m.y; D.z = m.z; D.spd = 0; D.vy = 0; D.air = false; }\n  NM.rule = true; try { flatten(D, A, 'stomp'); }")
    s = rep(s, "  if (m.slot !== NM.slot) { const B = netBlob(m.slot); if (B) { B.wob = 1; B.squash = 0.8; } return; }",
               "  if (m.slot !== NM.slot) { const B = netBlob(m.slot); if (B && netMine(B)) return netBotPush(B, m); if (B) { B.wob = 1; B.squash = 0.8; } return; }")
    s = rep(s, "; if (D === P) NM.selfKo = null;\n}", "; if (D === P) NM.selfKo = null; else D.netSelfKo = null;\n}")
    s = rep(s, "  const occ = p.occ && p.occ !== P ? p.occ : null;", "  const occ = p.occ && p.occ !== P && !netMine(p.occ) ? p.occ : null; // (v413: this game's CPUs go in and out of pots themselves)")
    s = rep(s, "  if (B && B !== P) { if (occ && occ !== B) netFoeOut(occ, p);", "  if (B && B !== P && !netMine(B)) { if (occ && occ !== B) netFoeOut(occ, p);")
    s = rep(s, "  if (m.slot !== NM.slot || P.st !== 'hide') return;\n",
               "  { const Db = netBlob(m.slot); if (Db && netMine(Db)) { if (Db.st !== 'hide') return; const by = netBlob(m.by); if (m.why === 'bumped' && by && by !== Db) bumpFromCoffin(Db, by); else exitPot(Db); return; } } // (v413)\n  if (m.slot !== NM.slot || P.st !== 'hide') return;\n")
    # the search screen and the found card: a CPU by its name
    s = rep(s, "'<b>Match found!</b><p>' + (o ? 'You vs ' + frEsc(hdOf(o.name)) : 'Get ready') + '</p></div>';",
               "'<b>Match found!</b><p>' + (o ? 'You vs ' + frEsc(o.cpu ? o.name + ' (CPU)' : hdOf(o.name)) : 'Get ready') + '</p></div>';")
    return s
