// ---------- (v254) Showdown: four on the bigger canvas, everyone for themselves or two against two. Two hearts each: a knock-out
// costs one, and with none left you're out. Paint is fuel, not points. The last one (or the last pair) standing wins; if the clock runs
// out first, the most hearts left wins, then the most knock-outs ----------
const SD_HEARTS = 2, SD_T = 180, SD_END_T = 1.7, SD_OUT_T = 2.4, SD_FF = 8; // (SD_FF: how much faster the rest of a match runs once you skip ahead)
const sdAlive = D => (D.hearts || 0) > 0 && D.st !== 'out';
function sdSides() { const s = new Set(); for (const D of ACTIVE) if (sdAlive(D)) s.add(sideOf(D)); return s; }
let sdEndT = 0, spec = null;
// the order the hearts read in: you, your teammate, then the rest
const sdOrder = () => [P, ...ACTIVE.filter(D => D !== P && ally(D, P)), ...ACTIVE.filter(D => D !== P && !ally(D, P))];
const sdName = D => D === P ? playerName() : nameOf(D);
const ORD = n => n + (n % 100 >= 11 && n % 100 <= 13 ? 'th' : ['th', 'st', 'nd', 'rd'][n % 10] || 'th');
// a knock-out in a Showdown: a heart gone, and out of the match if that was the last
function sdHit(D, by) {
  D.hearts = Math.max(0, (D.hearts || 0) - 1); if (!by) D.selfOuts++;
  if (D.hearts > 0) return false;
  D.elimNow = true; D.elimAt = runT; D.elimBy = by || null; return true;
}
// who's left: a side with no hearts is out, and takes the place after everyone still in; one side left and it's over
function sdCheck() {
  if (!isShow() || state !== 'play') return;
  const alive = sdSides();
  for (const D of ACTIVE) if (!sdAlive(D) && !D.place && !alive.has(sideOf(D))) for (const B of ACTIVE) if (sideOf(B) === sideOf(D)) B.place = alive.size + 1;
  if (alive.size <= 1 && sdEndT <= 0) { sdEndT = SD_END_T; if (spec) { spec.ff = false; $('sdSpec').hidden = true; } } // (the last knock-out at its own speed)
}
// a heart lost (or the last one): said on screen, loudest for you and whoever you took out
function sdKoNote(D, reason, by) {
  const out = !!D.elimNow, me = D === P, mine = ally(D, P);
  if (out && me) { if (kof) { kof.elim = true; kof.elimTxt = D.place ? ORD(D.place) : 'Out'; } return; }
  if (out) {
    if (by === P) banner(nameOf(D) + ' is out!', 'Eliminated', false);
    else banner(nameOf(D) + ' is out!', by ? (by === P ? 'By you' : 'Taken out by ' + sdName(by)) : reason === 'fall' ? 'Fell off the canvas' : 'Knocked themselves out', false);
    AU.horn && AU.horn(); buzz([18, 30, 18]); return;
  }
  if (me) return; // (the flood says it)
  if (by === P) banner('Got ' + nameOf(D) + '!', D.hearts + (D.hearts === 1 ? ' heart left' : ' hearts left'), false);
  else if (mine) banner(nameOf(D) + ' lost a heart', by ? 'Got by ' + sdName(by) : '', false, true);
  else if (hearable(D)) popText(nameOf(D) + ' lost a heart');
}
// out of hearts: off the canvas for good (its things go with it); for you, the camera goes over to someone still in it
function sdOut(D) {
  D.elimNow = false; D.st = 'out'; D.pot = null; D.rag = null; D.held = null; D.held2 = null; D.orbSaved = null; D.power = null; D.rocket = null; D.turret = null; D.giantT = 0; D.frozenT = 0; D.stunT = 0;
  if (D === P) { drop.visible = false; shadowBlob.visible = false; if (kof) kofOpen(); sdSpecStart(); }
  else { D.look.drop.visible = false; D.look.shadow.visible = false; if (spec && spec.D === D) sdSpecPick(); }
  sdHud(true);
}
// watching after you're out: your teammate if they're still in, whoever got you, or anyone left. Skip runs the rest through at speed,
// so it still ends the way it would have
function sdSpecStart() { spec = { D: null, t: 0, ff: false }; sdSpecPick(P.elimBy); hud.classList.add('spec'); const el = $('sdSpec'); el.classList.remove('ff'); el.hidden = false; $('sdSkip').disabled = false; $('sdSkipL').textContent = 'Skip'; camSnap = true; }
function sdSkipOn() { if (!spec || spec.ff || state !== 'play' || sdEndT > 0) return; spec.ff = true; $('sdSpec').classList.add('ff'); $('sdSkip').disabled = true; $('sdSkipL').textContent = SD_FF + '\u00d7'; $('sdSpecW').textContent = 'Fast-forward'; }
function sdSpecPick(pref) {
  if (!spec) return; const c = ACTIVE.filter(D => D !== P && sdAlive(D)); let S = c.find(D => ally(D, P)) || (pref && c.includes(pref) ? pref : null) || c[0] || null;
  spec.D = S; if (S) { camYaw = S.yaw; camYawV = 0; camSnap = true; $('sdSpecN').textContent = nameOf(S); $('sdSpecW').textContent = spec.ff ? 'Fast-forward' : ally(S, P) ? 'Your teammate' : 'Watching'; }
}
function sdSpecEnd() { spec = null; hud.classList.remove('spec'); $('sdSpec').hidden = true; }
// the clock ran out, or only one side is left: the standings, the end
function endShowdown(timeUp) {
  if (state !== 'play') return; sdEndT = 0;
  const alive = [...sdSides()], stat = s => { let h = 0, k = 0, so = 0; for (const D of ACTIVE) if (sideOf(D) === s) { h += Math.max(0, D.hearts || 0); k += D.kos; so += D.selfOuts; } return { s, h, k, so }; };
  const st = alive.map(stat).sort((a, b) => b.h - a.h || b.k - a.k || a.so - b.so), same = (a, b) => a.h === b.h && a.k === b.k && a.so === b.so;
  let winSides = [];
  if (st.length) { winSides = st.filter(e => same(e, st[0])).map(e => e.s); let place = 1; for (let i = 0; i < st.length;) { let j = i; while (j < st.length && same(st[j], st[i])) j++; for (let q = i; q < j; q++) for (const D of ACTIVE) if (sideOf(D) === st[q].s) D.place = place; place += j - i; i = j; } }
  else { const last = Math.max(...ACTIVE.map(D => D.elimAt)); winSides = [...new Set(ACTIVE.filter(D => D.elimAt === last).map(sideOf))]; for (const D of ACTIVE) if (winSides.includes(sideOf(D))) D.place = 1; }
  const draw = winSides.length > 1, mine = sideOf(P), win = draw ? (winSides.includes(mine) ? 0 : -1) : winSides[0] === mine ? 1 : -1, winners = ACTIVE.filter(D => winSides.includes(sideOf(D)));
  const id = runId; state = 'dead'; qMatchEnd(); for (const D of ACTIVE) if (D.charging) clearCharge(D);
  aimRing.visible = false; arrow.visible = false; hintEl.classList.remove('on'); if (kof) kofOpen(); sdSpecEnd();
  AU.chargeStop(); AU.roll(0, 0); AU.sizzle(0); AU.music('end'); AU.horn();
  if (!hardPhase) { hardPhase = true; hardStart = dryClock; }
  const per = f => [P, H, H2, H3].map(f);
  endInfo = { mode, show: true, win, winner: draw ? null : winners.includes(P) ? P : winners[0], winners, draw, timeUp, time: runT, you: teamCov(0), cpu: teamCov(1), cpu2: teamCov(2), kos: per(D => D.kos | 0), selfs: per(D => D.selfOuts | 0), hearts: per(D => Math.max(0, D.hearts | 0)), places: per(D => D.place || 0), tot: null, newBest: false };
  store.wins = store.wins || {}; store.played = store.played || {}; const slot = mode + diff; store.played[slot] = (store.played[slot] || 0) + 1; if (win > 0) store.wins[slot] = (store.wins[slot] || 0) + 1;
  store.runs = (store.runs || 0) + 1; if (store.itemIn > 0) store.itemIn--;
  store.world = store.world || {}; const wk = worldKey(), wr = store.world[wk] = store.world[wk] || { best: 0, wins: 0, played: 0 }; wr.played++; if (win > 0) wr.wins++;
  endInfo.diff = diff; const pl = P.place || 4; let gain = Math.round(18 + 9 * P.kos + (win > 0 ? 40 : win === 0 ? 14 : 0) + (pl === 2 ? 12 : pl === 3 ? 5 : 0) + 4 * Math.max(0, P.hearts | 0));
  const fin = commProgress(endInfo); gain += fin.length * COMM_XP; endInfo.xp0 = store.xp || 0; store.xp = endInfo.xp0 + gain; endInfo.xp = gain; endInfo.comms = fin;
  const drops = Math.round(8 + 5 * P.kos + (win > 0 ? 30 : win === 0 ? 12 : 0) + (pl === 2 ? 8 : 0)) + fin.length * COMM_DABS; store.drops = (store.drops || 0) + drops; endInfo.drops = drops;
  save(); tutEndMatch();
  const duo = mode === 'duo';
  if (win > 0) banner(duo ? 'Your team wins!' : 'Last one standing!', timeUp ? 'Most hearts left' : '', false);
  else if (win === 0) banner('Draw!', timeUp ? 'Dead even at the buzzer' : 'Out together', false);
  else banner(timeUp ? 'Time!' : (duo ? sdName(winners[0]) + ' & ' + sdName(winners[1] || winners[0]) + ' win' : sdName(winners[0]) + ' wins'), timeUp ? 'Most hearts left wins' : '', false);
  buzz([40, 30, 40]); slow = 0.6; if (win > 0) celebrating = true;
  setTimeout(() => { if (id !== runId || state !== 'dead') return; startTally(); }, 1450);
}
// the hearts across the top: a face for each fighter, its hearts under it; out of it, greyed with a cross; a pair against a pair in 2v2
const HEART_SVG = '<svg viewBox="0 0 24 22" aria-hidden="true"><path d="M12 20.6C5.6 15.6 1.6 11.8 1.6 7.2 1.6 4 4 1.6 7 1.6c2 0 3.8 1.1 5 2.8 1.2-1.7 3-2.8 5-2.8 3 0 5.4 2.4 5.4 5.6 0 4.6-4 8.4-10.4 13.4z"/></svg>';
function sdHud(force) {
  const el = $('sdBar'); if (!el) return;
  const on = isShow() && (state === 'play' || state === 'intro' || state === 'reveal' || state === 'paused');
  if (el.hidden === on) el.hidden = !on; if (!on) return;
  const order = sdOrder(), sig = order.map(D => D.team + (D.st === 'out' || D.elimNow ? 'o' : D.st === 'ko' ? 'k' : '') + Math.max(0, D.hearts | 0)).join(',') + (spec && spec.D ? spec.D.team : '');
  if (sig === el._sig && !force) return;
  if (!el._built || el._mode !== mode) { el._built = true; el._mode = mode; el._h = new Map();
    let h = ''; order.forEach((D, i) => { if (mode === 'duo' && i === 2) h += '<b class="sdvs" aria-hidden="true">VS</b>';
      h += '<span class="sdc' + (D === P ? ' me' : ally(D, P) ? ' ally' : '') + '" data-t="' + D.team + '" style="--c:' + TEAMS[D.team].css + '">' + faceIcon(D, false) + '<span class="sdh">' + HEART_SVG.repeat(SD_HEARTS) + '</span><span class="sdn">' + escAttr(sdName(D)) + '</span></span>'; });
    el.innerHTML = h; }
  for (const D of order) {
    const c = el.querySelector('.sdc[data-t="' + D.team + '"]'); if (!c) continue;
    const hp = Math.max(0, D.hearts | 0), was = el._h.get(D), out = D.st === 'out' || !!D.elimNow;
    c.classList.toggle('out', out); c.classList.toggle('ko', !out && D.st === 'ko'); c.classList.toggle('watch', !!(spec && spec.D === D));
    const hs = c.querySelectorAll('.sdh svg'); hs.forEach((s, i) => { const full = i < hp; s.classList.toggle('on', full); if (was !== undefined && !full && i < was) restartCls(s, 'lose'); });
    el._h.set(D, hp);
  }
  el.setAttribute('aria-label', order.map(D => sdName(D) + ' ' + (D.st === 'out' ? 'out' : Math.max(0, D.hearts | 0) + ' hearts')).join(', '));
  el._sig = sig;
}
// the CPUs in a Showdown come for you more: knock-outs are the whole game (their paint is just to keep them going)
const SD_AI = { easy: { hunt: 0.09, attack: 0.3, ram: 0.3, sense: 12, seek: 0.25 }, medium: { hunt: 0.42, attack: 0.7, ram: 0.7, flingAtk: 0.45, sense: 24, seek: 0.55 }, hard: { hunt: 0.7, attack: 0.9, ram: 1, sense: 34, seek: 0.85 } };
// (they hear a fight: a rival within this radius is known, wall or no wall)
const sdSense = (D, O) => isShow() && AI.sense > 0 && O.st === 'play' && Math.abs(O.y - D.y) < 4 && Math.hypot(O.x - D.x, O.z - D.z) < AI.sense;
// the results: no paint tally, the fighters by where they finished, with their knock-outs and the times they took themselves out
const SELF_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.5c-5.2 0-8.8 3.6-8.8 8.3 0 2.9 1.4 5.3 3.6 6.7v3.1h10.4v-3.1c2.2-1.4 3.6-3.8 3.6-6.7 0-4.7-3.6-8.3-8.8-8.3z"/><circle cx="8.6" cy="11.4" r="1.9" fill="#171320" stroke="none"/><circle cx="15.4" cy="11.4" r="1.9" fill="#171320" stroke="none"/></svg>';
function sdBoard(info) {
  const ppl = [P, H, H2, H3].filter(D => ACTIVE.includes(D)).map(D => ({ D, place: info.places[D.team] || 4, kos: info.kos[D.team] || 0, self: info.selfs[D.team] || 0, hp: info.hearts[D.team] || 0 }));
  ppl.sort((a, b) => a.place - b.place || b.kos - a.kos || (b.D === P) - (a.D === P));
  const maxK = Math.max(0, ...ppl.map(e => e.kos)), tops = ppl.filter(e => e.kos === maxK), topK = maxK > 0 && tops.length === 1 ? tops[0].D : null;
  let h = '<div class="bhead" aria-hidden="true"><span></span><span></span><span></span><span>KOs</span><span>Self-outs</span></div>'; const says = [];
  ppl.forEach((e, i) => {
    const D = e.D, me = D === P, [c, hi] = colVars(D), nm = sdName(D), top = topK === D, win = info.winners.includes(D);
    const say = ordinal(e.place) + ', ' + nm + (me ? ' (you)' : ally(D, P) ? ' (your teammate)' : '') + ', ' + e.kos + (e.kos === 1 ? ' knock-out' : ' knock-outs') + ', ' + e.self + ' self-eliminated' + (e.hp ? ', ' + e.hp + (e.hp === 1 ? ' heart left' : ' hearts left') : '');
    says.push(say);
    h += '<div class="brow' + (me ? ' you' : '') + '" role="listitem" aria-label="' + escAttr(say) + '" style="--c:' + c + ';--chi:' + hi + ';--d:' + (0.22 + i * 0.09).toFixed(2) + 's">'
      + '<b class="brank" aria-hidden="true">' + e.place + '</b>' + faceIcon(D, win && !info.draw)
      + '<span class="bname" aria-hidden="true"><span class="bn"><b>' + escAttr(nm) + '</b>' + (me ? '<i>You</i>' : ally(D, P) ? '<i>Team</i>' : '') + '</span>'
      + '<span class="bhp">' + (e.hp ? HEART_SVG.repeat(e.hp) : '<em>Out</em>') + (top ? '<em class="medal">' + MEDAL_SVG + 'Most KOs</em>' : '') + '</span></span>'
      + '<span class="bko' + (top ? ' most' : '') + '" aria-hidden="true">' + KO_SVG + '<b>' + e.kos + '</b></span>'
      + '<span class="bko bself" aria-hidden="true">' + SELF_SVG + '<b>' + e.self + '</b></span></div>';
  });
  return { h, says };
}
// the victory screen's words for a Showdown
function sdVicWords(info, feat, me) {
  const pl = $('vPlace'), lead = feat[0], duo = info.mode === 'duo', inWin = info.winners.includes(P);
  if (info.draw) { pl.className = 'vplace word'; pl.textContent = 'Draw'; vicTag(info.timeUp ? 'Dead even' : 'Out together', false); vicName(feat.map(sdName).join(' & ')); $('vSub').innerHTML = '<b>Even</b>on hearts and knock-outs'; return; }
  pl.className = 'vplace'; pl.innerHTML = '1<small>st</small>';
  vicTag(inWin ? (duo ? 'Your team wins' : 'Last one standing') : 'You came ' + ORD(me ? me.place : 4), inWin);
  vicName(duo ? sdName(feat[0]) + ' & ' + sdName(feat[1] || feat[0]) : sdName(lead));
  const k = feat.reduce((s, D) => s + (info.kos[D.team] || 0), 0), hp = feat.reduce((s, D) => s + (info.hearts[D.team] || 0), 0);
  $('vSub').innerHTML = '<b>' + k + (k === 1 ? ' KO' : ' KOs') + '</b>' + (hp ? hp + (hp === 1 ? ' heart left' : ' hearts left') : 'down to the wire');
}
const sdCardStat = D => { const k = endInfo && endInfo.kos ? endInfo.kos[D.team] || 0 : D.kos; return k + '\u00a0KO'; };
// how far down the screen the scoreboard reaches (looked at now and then: it only changes with the layout)
let sdCardY = 0, sdCardAt = -9;
function sdCardBot() { if (Math.abs(clock - sdCardAt) > 0.5) { sdCardAt = clock; const c = hud.querySelector('.score'), r = c && c.getBoundingClientRect(), b = stage.getBoundingClientRect(); sdCardY = r && r.height ? r.bottom - b.top : 130; } return sdCardY; }
// the spectator's camera: behind whoever it's watching, the way the game's own follows you
function specCam(rdt) {
  const S = spec.D; if (!S) return false;
  let dy = S.yaw - camYaw; dy = Math.atan2(Math.sin(dy), Math.cos(dy)); [camYaw, camYawV] = sdamp(camYaw, camYaw + dy, camYawV, 0.35, Math.min(rdt, 0.05));
  gyCam += ((S.air ? Math.min(S.y, gyCam + 1.3) : S.y) - gyCam) * (1 - Math.exp(-rdt * 5));
  const fx = Math.sin(camYaw), fz = Math.cos(camYaw), far = S.st === 'ko' ? 1 : 0;
  dPos.set(S.x - fx * (6.2 + far * 3), gyCam + 8.2 + far * 4, S.z - fz * (6.2 + far * 3)); dLook.set(S.x + fx * 3.2, gyCam - 0.25, S.z + fz * 3.2);
  return true;
}
