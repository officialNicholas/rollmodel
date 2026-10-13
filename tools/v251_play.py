"""v251 gameplay: the second match on Sludge Sewer; three skills (Swim faster, Weather Repel, Deep Pockets), each tapped open on the Strokes
page to show what it does; everyone 6% quicker; the Paint Trap pick-up; the Flash Freeze special."""

ICON_REPEL = ('<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M32 33v15a5.5 5.5 0 0 1-11 0" fill="none" stroke="#171320" stroke-width="3.6" stroke-linecap="round"/>'
    '<path d="M7 33a25 23 0 0 1 50 0q-6.25-5-12.5 0-6.25-5-12.5 0-6.25-5-12.5 0Q13.25 28 7 33z" fill="#7CC8FF" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/>'
    '<path d="M32 10.5q-9 9-8 22M32 10.5q9 9 8 22" fill="none" stroke="#171320" stroke-width="2.2" opacity=".5"/><path d="M14 22q5-8 13-10" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" opacity=".85"/>'
    '<path d="M32 10.5V6" stroke="#171320" stroke-width="3.2" stroke-linecap="round"/><path d="M11 44l-2.5 5M53 41l-2.5 5M47 52l-2 4.4" stroke="#3E9BE0" stroke-width="3" stroke-linecap="round"/></svg>')
ICON_POCKETS = ('<svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="23" cy="19" r="9" fill="#B98CFF" stroke="#171320" stroke-width="3.2"/><circle cx="20" cy="16" r="2.6" fill="#fff" opacity=".85"/>'
    '<rect x="33" y="7" width="20" height="10" rx="5" fill="#F4EEE3" stroke="#171320" stroke-width="3.2"/><path d="M43 17v10" stroke="#171320" stroke-width="3.2" stroke-linecap="round"/>'
    '<path d="M11 27h42l-4 25a5 5 0 0 1-5 4.4H20a5 5 0 0 1-5-4.4z" fill="#C98B4E" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/>'
    '<path d="M11 27h42v6.5H11z" fill="#A86B34" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/><path d="M20 43h24" stroke="#F4EEE3" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="3 4" opacity=".85"/></svg>')
ICON_TRAP = ('<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M8 25a11 11 0 1 1 22 0c0 2.6-.8 4.8-2.1 6.5l.7 3.3a1.6 1.6 0 0 1-3 .7l-1.1-2.7a11 11 0 0 1-9.8.1l-1.2 2.8a1.6 1.6 0 0 1-3-.7l.8-3.6A11 11 0 0 1 8 25z"/>'
    '<path d="M24.5 14.5c1.6-3 4-4.4 7-4" fill="none" stroke-width="2.6" stroke-linecap="round"/><path d="M33 3.5l1.2 2.8 3 .3-2.3 2 .7 3-2.6-1.6-2.6 1.6.7-3-2.3-2 3-.3z" fill="#F2C14E" stroke-width="1.4"/>'
    '<circle cx="15" cy="20.5" r="2.6" fill="#fff" stroke="none" opacity=".75"/></svg>')

JS_SKILLS = r"""// v251: three skills, one on at a time; tap one on the Strokes page to see what it does
const SKILLS = [
  { id: 'swim', name: 'Swim faster', desc: 'Built for speed, wet or dry.', up: ['8% more pace every time you glide', 'Twice as fast when the rain comes'], down: ['Rain still waters your paint down'] },
  { id: 'repel', name: 'Weather Repel', desc: 'Rain and heat roll right off you.', up: ['Rain and its puddles never water your paint down', 'The sun’s heat can’t burn you'], down: ['20% slower, all match long', 'No speed-up in the rain'] },
  { id: 'pockets', name: 'Deep Pockets', desc: 'Carry more, use it when you like.', up: ['Hold two power-ups and use either one', 'Save an orb for later: tap it when you want it', 'With one saved, the next orb goes off right away'], down: ['No speed-up in the rain'] }];
const FZ_ARM = 'M32 32V7M32 15l-6.5-5.5M32 15l6.5-5.5M32 24l-5-4.2M32 24l5-4.2';
Object.assign(STROKE_ICON, { repel: '__REPEL__', pockets: '__POCKETS__',
  freeze: '<svg viewBox="0 0 64 64" aria-hidden="true"><g fill="none" stroke-linecap="round" stroke-linejoin="round">' + [['#171320', 9], ['#7CC8FF', 5], ['#EAF7FF', 1.8]].map(([c, w]) => [0, 60, 120, 180, 240, 300].map(a => '<path d="' + FZ_ARM + '" stroke="' + c + '" stroke-width="' + w + '" transform="rotate(' + a + ' 32 32)"/>').join('')).join('') + '</g><circle cx="32" cy="32" r="6" fill="#EAF7FF" stroke="#171320" stroke-width="3"/></svg>' });
// everyone's pace: 6% quicker than before; the rain's speed-up only with Swim faster (CPUs swim); Weather Repel a fifth slower
const MOVE_K = 1.06, REPEL_SPD = 0.8, rainFast = D => !D.skill || D.skill === 'swim', spdK = D => MOVE_K * (rainFast(D) ? speedMul : 1) * (D.skill === 'repel' ? REPEL_SPD : 1);
const spName = id => (SPECIALS.find(x => x.id === id) || { name: id }).name, ORB_LBL = { rocket: 'Rocket', giant: 'Giant', freeze: 'Freeze' };"""

JS_SKILLCARD = r"""let stSkillSel = null; // (the skill whose breakdown shows: the equipped one when the page opens)
function skillCard() {
  const eq = strokeSkill(), o = SKILLS.find(x => x.id === (stSkillSel || eq)) || SKILLS[0], on = o.id === eq;
  $('stSkillNow').innerHTML = '<span class="stic">' + STROKE_ICON[o.id] + '</span><span><span class="stname">' + o.name + '</span><span class="stdesc">' + o.desc + '</span>' + (on ? '<span class="ststamp">Equipped</span>' : '<button class="stequip" type="button" data-eq="' + o.id + '">Equip</button>') + '</span>'
    + '<ul class="stperks" aria-label="' + escAttr('What ' + o.name + ' does') + '">' + o.up.map(t => '<li class="up">' + t + '</li>').join('') + o.down.map(t => '<li class="dn">' + t + '</li>').join('') + '</ul>';
}
function equipSkill(id) { const d = strokesOf(); if (!d.own.includes(id) || d.skill === id) return; d.skill = id; stSkillSel = id; save(); AU.ready && AU.ready(); buzz(8); renderStrokes(); stToast(SKILLS.find(x => x.id === id).name + ' is your skill'); }
function renderStrokes() {"""

JS_ITEMS = r"""
// ---------- v251: Deep Pockets: the second pocket and the saved orb ----------
function useHeld2(D) { if (!D.held2) return false; const a = D.held; D.held = D.held2; D.held2 = null; if (useHeld(D)) { D.held = a; return true; } D.held2 = D.held; D.held = a; return false; }
function useOrb(D) {
  if (!D.orbSaved || D.st !== 'play' || D.flatT > 0 || D.stunT > 0 || D.rocket || D.turret || D.giantT > 0 || D.knockT > 0) return false;
  const g = D.orbSaved; D.orbSaved = null; shockwave(D.x, D.y + 0.1, D.z, 2.2, 0xFFFFFF); orbGift(D, g); return true;
}
function cpuGift() { return !tut && !tut2 && !tut3 && Math.random() < 0.2 ? 'freeze' : ['giant', 'rocket'][(Math.random() * 2) | 0]; }
function pocketHud() {
  const b2 = $('itemBtn2'), h2 = state === 'play' && P.st === 'play' ? P.held2 : null; if (b2.hidden === !!h2) b2.hidden = !h2;
  if (h2 && b2.dataset.k !== h2) { b2.dataset.k = h2; b2.innerHTML = '<i class="sdisc" aria-hidden="true"></i>' + ITEM_ICON[h2] + '<span class="ilbl">' + PU[h2].name + '</span>'; b2.setAttribute('aria-label', 'Use the ' + PU[h2].name.toLowerCase()); restartCls(b2, 'in'); } else if (!h2) b2.dataset.k = '';
  const ob = $('orbBtn'), os = state === 'play' && P.st === 'play' ? P.orbSaved : null; if (ob.hidden === !!os) ob.hidden = !os; if (ob.classList.contains('up') !== !!h2) ob.classList.toggle('up', !!h2);
  if (os && ob.dataset.k !== os) { ob.dataset.k = os; ob.innerHTML = '<i class="sdisc" aria-hidden="true"></i>' + (STROKE_ICON[os] || '') + '<span class="ilbl">' + (ORB_LBL[os] || 'Orb') + '</span>'; ob.setAttribute('aria-label', 'Use your saved ' + (ORB_LBL[os] || 'orb').toLowerCase()); restartCls(ob, 'in'); } else if (!os) ob.dataset.k = '';
}
// ---------- v251: the Paint Trap. Dropped where you stand, it arms in a beat; the next rival over it sets it off: a burst of your paint, and
// they're stunned and popped up. A dodge roll through it sets it off harmlessly (a CPU heading for one sometimes knows to); your own can't
// catch you, and a jump clears it. Two down at most each (a third pops the oldest); left alone it fizzles out after TRAP_LIFE seconds ----------
const TRAP_R = 0.75, TRAP_ARM = 0.6, TRAP_LIFE = 45, TRAP_MAX = 2, TRAP_STUN = 1.5, TRAP_SPLAT = SPLAT_R * 1.7;
const trapMatC = new Map(), trapMat = col => { let o = trapMatC.get(col); if (!o) { o = { m: toon(col), ring: new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.55, depthWrite: false }) }; trapMatC.set(col, o); } return o; };
function makeTrapMesh(D) {
  const g = new THREE.Group(), M = trapMat(TEAMS[D.team].wet);
  const dome = new THREE.Mesh(TRAP_G.dome, M.m), hull = new THREE.Mesh(TRAP_G.dome, outlineMat); dome.scale.set(1, 0.62, 1); dome.castShadow = true; hull.scale.set(1.09, 0.7, 1.09); g.add(hull, dome);
  for (let i = 0; i < 5; i++) { const a = i / 5 * 6.283 + 0.4, d = new THREE.Mesh(TRAP_G.drip, M.m); d.position.set(Math.sin(a) * 0.31, 0.012, Math.cos(a) * 0.31); d.scale.set(1.3, 0.32, 1.3); g.add(d); }
  const cap = new THREE.Mesh(TRAP_G.cap, trapCapM), light = new THREE.Mesh(TRAP_G.light, trapLightOff); cap.position.y = 0.23; light.position.y = 0.3; g.add(cap, light);
  const ring = new THREE.Mesh(TRAP_G.ring, M.ring); ring.position.y = 0.03; ring.renderOrder = 3; g.add(ring);
  g.userData.light = light; g.userData.ring = ring; return g;
}
function dropTrap(D) {
  const gy = surfaceUnder(D.x, D.z, D.y + 0.4, true), y = gy > -Infinity ? gy : D.y, mine = trapList.filter(T => T.owner === D);
  if (mine.length >= TRAP_MAX) trapPop(mine[0], null, true);
  const T = { owner: D, x: D.x, y, z: D.z, arm: TRAP_ARM, t: 0, code: tcode(D), dec: {}, seen: false, g: makeTrapMesh(D) }; T.g.position.set(T.x, y, T.z); scene.add(T.g); trapList.push(T);
  shockwave(T.x, y + 0.05, T.z, 0.9, TEAMS[D.team].wet); D.squash = Math.max(D.squash, 0.4); emote(D, 'glee', 0.6);
  if (hearable(D)) { AU.at(T.x, T.z); AU.plop(); }
  if (D === P) { buzz(10); popText('Trap set!'); }
}
function trapTick(dt) {
  for (let i = trapList.length - 1; i >= 0; i--) {
    const T = trapList[i]; T.t += dt; if (T.arm > 0) T.arm -= dt;
    const u = T.g.userData; u.light.material = (T.arm > 0 ? (T.t * 10) % 1 < 0.5 : (T.t * 1.4) % 1 < 0.2) ? trapLightOn : trapLightOff; u.ring.scale.setScalar(1 + 0.07 * Math.sin(T.t * 5));
    if (T.t > TRAP_LIFE) { trapPop(T, null, true); continue; }
    if (T.arm > 0 || state !== 'play') continue;
    if (T.owner !== P && !T.seen && P.st === 'play' && Math.hypot(P.x - T.x, P.z - T.z) < 9) { T.seen = true; hint('trapdodge', say('A trap! Swipe up to roll through it safely', 'A trap! Shift to roll through it safely'), 3.2); }
    for (const D of ACTIVE) {
      if (D === T.owner || D.st !== 'play' || D.rocket || D.turret || D.immuneT > 0 || D.dashT > 0) continue; // (a roll still sets it off: harmlessly, below)
      const dx = D.x - T.x, dz = D.z - T.z, d = Math.hypot(dx, dz);
      // a CPU heading straight for it may roll through (more often the harsher the critics)
      if (D.ai && !D.air && !(D.rollT > 0) && d < 1.7 && d > TRAP_R && D.spd > 1.2 && Math.abs(wrapA(Math.atan2(-dx, -dz) - D.yaw)) < 0.6) { const k = 'r' + D.team; if (T.dec[k] === undefined) T.dec[k] = Math.random() < (diff === 'easy' ? 0.3 : diff === 'hard' ? 0.8 : 0.55); if (T.dec[k]) dodgeRoll(D); }
      if (d > TRAP_R || Math.abs(D.y - T.y) > 0.8 || (D.air && D.y - T.y > 0.3)) continue;
      trapPop(T, D, D.rollT > 0 || D.giantT > 0); break;
    }
  }
}
function trapPop(T, B, harmless) {
  const i = trapList.indexOf(T); if (i >= 0) trapList.splice(i, 1); scene.remove(T.g);
  if (!B && harmless) { for (let k = 0; k < 8; k++) { const a = Math.random() * 6.283; spawnPart(T.x, T.y + 0.2, T.z, Math.cos(a) * 0.7, 0.8 + Math.random() * 0.8, Math.sin(a) * 0.7, 0.3, steamMat, 0.7); } return; } // (fizzled out)
  const col = TEAMS[T.owner.team].wet;
  addSplat(T.x, T.y, T.z, Math.random() * 6.283, TRAP_SPLAT, dryClock, false, false, T.code);
  shockwave(T.x, T.y + 0.1, T.z, 2.8, col); shockwave(T.x, T.y + 0.1, T.z, 1.5, 0xFFFFFF);
  for (let k = 0; k < 22; k++) { const a = Math.random() * 6.283, v = 2.5 + Math.random() * 4.5; spawnPart(T.x, T.y + 0.3, T.z, Math.cos(a) * v, 2 + Math.random() * 4, Math.sin(a) * v, 0.35 + Math.random() * 0.3, tmat(T.owner), 0.55 + Math.random() * 0.4); }
  if (Math.hypot(T.x - P.x, T.z - P.z) < 20) { AU.at(T.x, T.z); AU.burst(0.8); AU.splat(0.9); }
  if (!B) return;
  if (harmless) { B.wob = Math.max(B.wob, 0.7); if (B === P) { popText('Dodged the trap!'); buzz(8); } else if (T.owner === P) popText(nameOf(B) + ' rolled right through'); return; }
  if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }
  const l = Math.hypot(B.x - T.x, B.z - T.z), nx = l > 0.05 ? (B.x - T.x) / l : Math.sin(B.yaw), nz = l > 0.05 ? (B.z - T.z) / l : Math.cos(B.yaw);
  B.stunT = Math.max(B.stunT || 0, TRAP_STUN); B.tGuard = TRAP_STUN + 0.9; B.spd = 0; B.turn = 0; B.kx = nx * 3.4; B.kz = nz * 3.4; B.slam = false; B.missile = false; B.rollT = 0;
  B.squash = 0.9; B.wob = 1; fxKnock(B, nx, nz, 0.8); if (!B.air) { B.air = true; B.stroke++; } B.vy = Math.max(B.vy || 0, 5.5); B.lastHit = { by: T.owner, t: runT };
  emote(B, 'ouch', 1); emote(T.owner, 'glee', 0.9); hitStop(0.06, T.owner, B);
  if (B === P) { shake = Math.max(shake, 0.35); buzz([20, 25, 20]); popText('Trapped!'); } else if (T.owner === P) { buzz(12); popText('Trapped ' + nameOf(B) + '!'); }
}
function clearTraps() { for (const T of trapList) scene.remove(T.g); trapList.length = 0; }
// ---------- v251: Flash Freeze. A beat to wind up (frost creeps in at the edges, a shimmer rises round whoever cast it), then a flash over
// the whole canvas and everyone else is frozen solid for FREEZE_T seconds. Safe: anyone down in a basin, anyone up in a rocket, and anyone
// whose dodge roll starts in the last FREEZE_SWEET seconds before the flash (a timing that's hard to master) ----------
const FREEZE_WIND = 0.9, FREEZE_T = 3, FREEZE_SWEET = 0.12, COL_ICE = new THREE.Color(0xCFEFFF), frzList = [];
const ICE_G = new THREE.IcosahedronGeometry(0.6, 1), iceShellM = toon(0xE2F6FF, { transparent: true, opacity: 0.6, depthWrite: false });
let frostHeld = false;
function startFreeze(D) {
  const F = { by: D, t: 0, fx: 0, roll: new Map() };
  for (const B of ACTIVE) if (B !== D && B.ai) F.roll.set(B, Math.random() < (diff === 'easy' ? 0.1 : diff === 'hard' ? 0.45 : 0.25)); // (a CPU sometimes nails the roll)
  frzList.push(F); D.wob = 1; D.squash = 0.7; emote(D, 'glee', 1.2); AU.whoosh();
  $('frost').classList.add('wind');
  if (D === P) { shake = Math.max(shake, 0.15); buzz([10, 40, 10]); banner('Flash freeze!', 'Here it comes'); }
  else { banner(nameOf(D) + '’s flash freeze!', say('Roll right at the flash, or hide in a ' + potWord(), 'Shift right at the flash, or hide in a ' + potWord())); AU.spot(); }
  for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0;
}
function freezeTick(dt) {
  for (let i = frzList.length - 1; i >= 0; i--) {
    const F = frzList[i], D = F.by; F.t += dt;
    if (state !== 'play') { frzList.splice(i, 1); $('frost').classList.remove('wind'); continue; }
    F.fx -= dt; if (F.fx <= 0) { F.fx = 0.14; shockwave(D.x, D.y + 0.1, D.z, 0.8 + 2.2 * F.t / FREEZE_WIND, 0xBFE9FF); for (let k = 0; k < 4; k++) { const a = Math.random() * 6.283; spawnPart(D.x + Math.cos(a) * 0.5, D.y + 0.3, D.z + Math.sin(a) * 0.5, Math.cos(a) * 0.6, 1.6 + Math.random(), Math.sin(a) * 0.6, 0.18, boilPartMat, 0.7); } }
    for (const [B, ok] of F.roll) if (ok && F.t >= FREEZE_WIND - 0.06 && B.st === 'play' && !(B.rollT > 0)) { F.roll.set(B, false); dodgeRoll(B); }
    if (F.t < FREEZE_WIND) continue;
    frzList.splice(i, 1); freezeFlash(F);
  }
}
function freezeFlash(F) {
  const D = F.by, fl = $('flash'), fr = $('frost'); let n = 0;
  if (!frzList.length) fr.classList.remove('wind');
  if (!reduceMotion) { fl.classList.add('ice'); restartCls(fl, 'on'); clearTimeout(freezeFlash.t); freezeFlash.t = setTimeout(() => fl.classList.remove('ice'), 950); }
  shockwave(D.x, D.y + 0.2, D.z, ARENA * 1.6, 0xDDF3FF); shockwave(D.x, D.y + 0.2, D.z, ARENA * 0.8, 0xFFFFFF); AU.burst(1); hitStop(0.06, D);
  for (const B of ACTIVE) {
    if (B === D || B.st !== 'play' || B.rocket) continue; // (down in a basin, knocked out, or up in a rocket: untouched)
    if (B.rollT > ROLL_T - FREEZE_SWEET) { if (B === P) { popText('Perfect dodge!'); buzz([8, 20, 8]); AU.ready && AU.ready(); } else if (D === P) popText(nameOf(B) + ' dodged it!'); continue; }
    if (B.charging) clearCharge(B); if (B === P) { holdCharge = false; slingOff(); }
    B.frozenT = FREEZE_T; B.stunT = Math.max(B.stunT || 0, FREEZE_T); B.spd = 0; B.turn = 0; B.kx = B.kz = 0; B.slam = false; B.missile = false; B.rollT = 0; B.wob = 1; n++;
    for (let k = 0; k < 10; k++) { const a = Math.random() * 6.283; spawnPart(B.x, B.y + 0.4, B.z, Math.cos(a) * 2, 1 + Math.random() * 2, Math.sin(a) * 2, 0.22, k % 2 ? boilPartMat : puHaloMat, 0.6); }
    if (B === P) { shake = Math.max(shake, 0.3); buzz([30, 30, 30]); popText('Frozen!'); fr.classList.add('held'); frostHeld = true; }
  }
  if (D === P) banner('Flash freeze!', n ? 'They’re frozen. Go get them' : 'Nobody caught');
  else if (P.st === 'hide') popText('Safe in the ' + potWord());
  for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0;
}
function thawFx(D) {
  for (let k = 0; k < 14; k++) { const a = Math.random() * 6.283, v = 1.5 + Math.random() * 2.5; spawnPart(D.x, D.y + 0.4, D.z, Math.cos(a) * v, 1.5 + Math.random() * 2.5, Math.sin(a) * v, 0.2 + Math.random() * 0.15, k % 2 ? boilPartMat : puHaloMat, 0.5 + Math.random() * 0.3); }
  if (hearable(D)) AU.pop();
}
function iceFrame(rdt) {
  for (const D of ACTIVE) {
    const on = D.frozenT > 0 && D.st === 'play';
    if (!on && !D.iceG) continue;
    if (!D.iceG) { const m = new THREE.Mesh(ICE_G, iceShellM); m.renderOrder = 9; m.visible = false; scene.add(m); D.iceG = m; D.iceK = 0; }
    D.iceK += ((on ? 1 : 0) - D.iceK) * Math.min(1, rdt * (on ? 16 : 22)); const m = D.iceG; m.visible = D.iceK > 0.02; if (!m.visible) continue;
    const gk = D === P ? (VP.gk || 1) : (D.look && D.look.V ? D.look.V.gk || 1 : 1), k = gk * (0.6 + 0.4 * D.iceK);
    m.position.set(D.x, D.y + 0.28 * gk, D.z); m.rotation.set(0.15, D.yaw + 0.4, 0.1); m.scale.set(k, 0.66 * k, 1.35 * k);
  }
  if (frostHeld && !(P.frozenT > 0 && state === 'play')) { frostHeld = false; $('frost').classList.remove('held'); }
}
"""

CSS = r"""/* v251: skills open up when tapped (what each one does, then Equip); the second item and the saved orb sit by the item button; Flash Freeze */
.stopt .stn{text-align:center;line-height:1.05}
.stopt.sel{box-shadow:0 0 0 3px #7CC8FF,0 0 0 5.5px #171320,3px 3px 0 rgba(23,19,32,.25)}
.stopt.sel .sts{background:#7CC8FF;color:#171320}
.stnow .stperks{grid-column:1/-1;display:grid;gap:7px;margin:0;padding:11px 12px;list-style:none;border-radius:12px;background:#fff;box-shadow:inset 0 0 0 2px rgba(23,19,32,.14)}
.stnow .stperks li{position:relative;padding-left:26px;font:700 13px/1.3 var(--font-ui);color:#2E2840}
.stnow .stperks li::before{content:"+";position:absolute;left:0;top:-1px;display:grid;place-items:center;width:18px;height:18px;border-radius:50%;background:#46E07A;color:#0B2A14;font:900 14px/1 var(--font-head);box-shadow:0 0 0 2px #171320}
.stnow .stperks li.dn::before{content:"\2212";background:#FF6B7D;color:#3A0710}
.stnow .stequip{appearance:none;display:inline-block;margin-top:8px;padding:8px 16px 7px;border:0;border-radius:999px;background:var(--gold);color:#171320;font:900 12px/1 var(--font-head);letter-spacing:.1em;text-transform:uppercase;box-shadow:0 0 0 2px #171320,0 3px 0 #171320;cursor:pointer;-webkit-tap-highlight-color:transparent}
.stnow .stequip:active{transform:translateY(2px);box-shadow:0 0 0 2px #171320,0 1px 0 #171320}
.itemBtn.ib2,.itemBtn.orbBtn{left:max(30px,calc(env(safe-area-inset-left) + 22px));width:64px;height:64px;bottom:calc(max(24px,calc(env(safe-area-inset-bottom) + 16px)) + 92px)}
.itemBtn.orbBtn.up{bottom:calc(max(24px,calc(env(safe-area-inset-bottom) + 16px)) + 166px)}
.itemBtn.ib2 svg,.itemBtn.orbBtn svg{width:30px;height:30px;margin-top:-10px}
.itemBtn.ib2 .ilbl,.itemBtn.orbBtn .ilbl{bottom:10px;font-size:8.5px}
@media (max-height:520px) and (min-aspect-ratio:1/1){.itemBtn.ib2,.itemBtn.orbBtn{left:auto;right:calc(max(156px,calc(env(safe-area-inset-right) + 148px)) + 80px);bottom:calc(max(22px,calc(env(safe-area-inset-bottom) + 14px)) + 3px);width:64px;height:64px}.itemBtn.orbBtn.up{right:calc(max(156px,calc(env(safe-area-inset-right) + 148px)) + 154px)}}
.flash.ice{background:radial-gradient(circle at 50% 45%,#FFFFFF 0,#DDF3FF 45%,#9ED8FF 100%)}
.flash.ice.on{animation:flashice .9s ease-out}
@keyframes flashice{0%{opacity:.95}35%{opacity:.7}100%{opacity:0}}
.frost{position:absolute;inset:0;pointer-events:none;opacity:0;transition:opacity .35s;background:radial-gradient(ellipse 80% 75% at 50% 50%,transparent 46%,rgba(190,235,255,.6) 78%,rgba(240,252,255,.95) 100%)}
.frost.wind{opacity:1;transition:opacity .9s ease-in}
.frost.held{opacity:1;transition:opacity .15s}
@media (prefers-reduced-motion:reduce){.flash.ice.on{animation:none}}
"""

def apply(s):
    import re
    def rep(old, new, count=1):
        nonlocal s
        c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
        s = s.replace(old, new)

    # ---- the second match: Sludge Sewer (the lesson's vote lands on it)
    rep("const TUT_SLOW = 0.35, TUT_HALLO = ['crypt', 'cathedral', 'manor'];", "const TUT_SLOW = 0.35, TUT_M2 = 'sewer'; // (the canvas the lesson's vote lands on: the second match is on Sludge Sewer)")
    rep("const tutV = tutPh() === 'vote' ? TUT_HALLO[(Math.random() * TUT_HALLO.length) | 0] : null;", "const tutV = tutPh() === 'vote' ? TUT_M2 : null;")
    rep("(the lesson: the rival's is a Halloween canvas, and it's the one drawn)", "(the lesson: the rival's is Sludge Sewer, and it's the one drawn)")

    # ---- skills and specials on the Strokes page
    rep("const SKILLS = [{ id: 'swim', name: 'Swim faster', desc: 'A touch more pace every time you glide.' }];", JS_SKILLS.replace('__REPEL__', ICON_REPEL).replace('__POCKETS__', ICON_POCKETS))
    rep("{ id: 'giant', name: 'Giant', desc: 'Grow huge, paint wide, stomp rivals flat.', craft: 20 }];",
        "{ id: 'giant', name: 'Giant', desc: 'Grow huge, paint wide, stomp rivals flat.', craft: 20 }, { id: 'freeze', name: 'Flash Freeze', desc: 'A flash over the canvas: every rival frozen solid for 3 seconds.', craft: 25 }];")
    rep("for (const k of ['rocket', 'swim']) if (!d.own.includes(k)) d.own.push(k);", "for (const k of ['rocket', 'swim', 'repel', 'pockets']) if (!d.own.includes(k)) d.own.push(k); if (!SKILLS.some(x => x.id === d.skill)) d.skill = 'swim';")
    rep("function renderStrokes() {", JS_SKILLCARD)
    rep("now(strokeSpecial(), SPECIALS, $('stSpecialNow')); now(strokeSkill(), SKILLS, $('stSkillNow'));", "now(strokeSpecial(), SPECIALS, $('stSpecialNow')); skillCard();")
    rep("$('stSkillRail').innerHTML = SKILLS.map(o => '<button class=\"stopt on\" type=\"button\" data-sk=\"' + o.id + '\" aria-pressed=\"true\" aria-label=\"' + escAttr(o.name + ', equipped') + '\">' + STROKE_ICON[o.id] + '<span class=\"stn\">' + o.name + '</span><span class=\"sts\">Equipped</span></button>').join('')",
        "$('stSkillRail').innerHTML = SKILLS.map(o => { const on = strokeSkill() === o.id, sel = (stSkillSel || strokeSkill()) === o.id; return '<button class=\"stopt' + (on ? ' on' : '') + (sel && !on ? ' sel' : '') + '\" type=\"button\" data-sk=\"' + o.id + '\" aria-pressed=\"' + sel + '\" aria-label=\"' + escAttr(o.name + (on ? ', equipped' : ', see what it does')) + '\">' + STROKE_ICON[o.id] + '<span class=\"stn\">' + o.name + '</span><span class=\"sts\">' + (on ? 'Equipped' : sel ? 'Showing' : 'Tap to see') + '</span></button>'; }).join('')")
    rep("if (crafting) { const sp = SPECIALS.find(x => x.id === crafting.id), tot = sp.craft * 60000; $('stCraftT').textContent = mmss(left);",
        "if (crafting) { const sp = SPECIALS.find(x => x.id === crafting.id), tot = sp.craft * 60000; $('stCraftT').textContent = mmss(left); { const ct = cEl.querySelector('.stct'); if (ct && ct.firstChild && ct.firstChild.nodeType === 3) ct.firstChild.nodeValue = 'Crafting the ' + sp.name; }")
    rep("d.craft.end = Date.now(); craftTick(); AU.ui(); buzz([10, 30, 10]); renderStrokes(); stToast('The Giant is ready!'); }", "const cn = spName(d.craft.id); d.craft.end = Date.now(); craftTick(); AU.ui(); buzz([10, 30, 10]); renderStrokes(); stToast('The ' + cn + ' is ready!'); }")
    rep("const d = strokesOf(); if (d.craft) { if (!craftTick()) { renderStrokes(); stToast('The Giant is ready!'); }", "const d = strokesOf(); if (d.craft) { const cn = spName(d.craft.id); if (!craftTick()) { renderStrokes(); stToast('The ' + cn + ' is ready!'); }")
    rep("stToast('Reach rank ' + ABIL_RANK + ' to craft the ' + id);", "stToast('Reach rank ' + ABIL_RANK + ' to craft the ' + spName(id));")
    rep("menuPage = 'strokes'; menu.dataset.page = 'strokes';", "stSkillSel = null; menuPage = 'strokes'; menu.dataset.page = 'strokes';")
    rep("$('stSkillRail').addEventListener('click', e => { if (e.target.closest('.stopt[data-sk]')) { AU.init(); AU.ui(); } });",
        "$('stSkillRail').addEventListener('click', e => { const b = e.target.closest('.stopt[data-sk]'); if (!b) return; AU.init(); const id = b.dataset.sk;\n"
        "  if ((stSkillSel || strokeSkill()) === id) { if (strokeSkill() !== id) equipSkill(id); else AU.ui(); return; } // (a second tap on the one showing equips it)\n"
        "  stSkillSel = id; AU.ui(); buzz(6); renderStrokes(); });\n"
        "$('stSkillNow').addEventListener('click', e => { const b = e.target.closest('.stequip'); if (!b) return; AU.init(); equipSkill(b.dataset.eq); });")

    # ---- pace: everyone 6% quicker; the rain's speed-up with Swim faster only; Weather Repel a fifth slower
    rep("const base = cfg.speed * speedMul * (D.cpu ? AI.speed : 1) * (D.dry ? 0.7 : 1);", "const base = cfg.speed * spdK(D) * (D.cpu ? AI.speed : 1) * (D.dry ? 0.7 : 1);")
    rep("D.spd = Math.max(D.spd, cfg.speed * speedMul * 0.5);", "D.spd = Math.max(D.spd, cfg.speed * spdK(D) * 0.5);")
    rep("A.spd > cfg.speed * speedMul * 1.15 && B.immuneT", "A.spd > cfg.speed * spdK(A) * 1.15 && B.immuneT")
    rep("let tgt = cfg.speed * (giant ? 1 : speedMul) * slopeK(D)", "let tgt = cfg.speed * (giant ? MOVE_K : spdK(D)) * slopeK(D)")
    rep("if (giant) tgt = Math.min(tgt * GIANT_SPD, cfg.speed * 1.9);", "if (giant) tgt = Math.min(tgt * GIANT_SPD, cfg.speed * 1.9 * MOVE_K);")
    rep("if (D.flung && !D.air && D.spd < cfg.speed * speedMul * 1.15) D.flung = false;", "if (D.flung && !D.air && D.spd < cfg.speed * spdK(D) * 1.15) D.flung = false;")
    rep("const speed = cfg.speed * AI.speed * speedMul;", "const speed = cfg.speed * AI.speed * spdK(D);")
    rep("(playing ? (speedMul - 1) * 12 + fovKick", "(playing ? ((rainFast(P) ? speedMul : 1) - 1) * 12 + fovKick")
    rep("P.spd / (cfg.speed * speedMul)", "P.spd / (cfg.speed * spdK(P))")
    assert 'cfg.speed * speedMul' not in s, 'a speedMul use left'

    # ---- Weather Repel: no sun burn, no rain or puddle watering down; told so; no basin pointer for the heat
    rep("D.exposed = wxPhase === 'sun' && D.giantT <= 0 &&", "D.exposed = wxPhase === 'sun' && D.skill !== 'repel' && D.giantT <= 0 &&")
    rep("if (wxPhase === 'rain' && !roofOver(D)) { if (D.dilT <= 0) dilute(D, true);", "if (wxPhase === 'rain' && D.skill !== 'repel' && !roofOver(D)) { if (D.dilT <= 0) dilute(D, true);")
    rep("if (D.inBoil) { if (D.dilT <= 0) dilute(D); D.dilT = DIL_T; }", "if (D.inBoil && D.skill !== 'repel') { if (D.dilT <= 0) dilute(D); D.dilT = DIL_T; }")
    rep("(P.dry || P.paint < 0.1 || wxPhase === 'warn' || (wxPhase === 'sun' && P.exposed))", "(P.dry || P.paint < 0.1 || (wxPhase === 'warn' && P.skill !== 'repel') || (wxPhase === 'sun' && P.exposed))")
    rep("wxBanner('Heat wave in ' + SUN_WARN, sunsSeen ? '' : 'Hide in a ' + potWord() + ' or the shade', true);", "wxBanner('Heat wave in ' + SUN_WARN, P.skill === 'repel' ? 'Weather Repel: the heat can\\u2019t touch you' : sunsSeen ? '' : 'Hide in a ' + potWord() + ' or the shade', true);")
    rep("wxBanner('Rain!', rainsSeen++ ? '' : 'Faster, but your paint thins');", "{ const n = rainsSeen++; wxBanner('Rain!', P.skill === 'repel' ? 'Weather Repel: it rolls right off you' : n ? '' : rainFast(P) ? 'Faster, but your paint thins' : 'Your paint thins'); }")

    # ---- each blob's skill for the match (the lesson always swims; CPUs swim); fresh pockets, no frost
    rep("D.swimBoost = D === P && strokeSkill() === 'swim' ? SWIM_BOOST : 1; }", "D.skill = D === P ? (tut ? 'swim' : strokeSkill()) : 'swim'; D.swimBoost = D === P && D.skill === 'swim' ? SWIM_BOOST : 1; D.frozenT = 0; }")
    rep("D.held = null; D.heldT = 0; } // the pound builds up before the first one", "D.held = null; D.heldT = 0; D.held2 = null; D.orbSaved = null; D.frozenT = 0; } // the pound builds up before the first one")
    rep("D.exposed = false; D.spd = 0; D.vy = 0; D.slowed = false; D.inBoil = false;", "D.exposed = false; D.spd = 0; D.vy = 0; D.slowed = false; D.inBoil = false; D.frozenT = 0;")

    # ---- Deep Pockets: the second item, the saved orb
    rep("  if (D.held) dropHeld(D);\n  D.held = type; D.heldT = 0;",
        "  if (D.skill === 'pockets' && D.held) { if (D.held2) { dropHeld(D); D.held = D.held2; } D.held2 = type; } // (Deep Pockets: a second one goes in the other pocket; a third drops the oldest)\n  else { if (D.held) dropHeld(D); D.held = type; }\n  D.heldT = 0;")
    rep("window.__orbKind || (D === P ? strokeSpecial() : ['giant', 'rocket'][(Math.random() * 2) | 0]);", "window.__orbKind || (D === P ? strokeSpecial() : cpuGift());")
    rep("  if (gift === 'rocket') { startRocket(D); for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return; }",
        "  // Deep Pockets: the first orb goes in your pocket for later; with one already saved, the next goes off at once\n"
        "  if (D.skill === 'pockets' && !D.orbSaved && !tut && !tut2 && !tut3) { D.orbSaved = gift; emote(D, 'glee', 0.8); if (D === P) { AU.pop(); buzz([10, 20, 10]); const w = (ORB_LBL[gift] || 'orb').toLowerCase(); banner('Orb saved!', say('Tap it when you want the ' + w, 'Press C for the ' + w)); } for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return; }\n"
        "  orbGift(D, gift);\n}\n"
        "function orbGift(D, gift) {\n"
        "  if (gift === 'freeze') { startFreeze(D); return; }\n"
        "  if (gift === 'rocket') { startRocket(D); for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return; }")
    rep('<button class="itemBtn" id="itemBtn" type="button" aria-label="Use item" hidden></button>',
        '<button class="itemBtn" id="itemBtn" type="button" aria-label="Use item" hidden></button><button class="itemBtn ib2" id="itemBtn2" type="button" aria-label="Use your second item" hidden></button><button class="itemBtn orbBtn" id="orbBtn" type="button" aria-label="Use your saved orb" hidden></button>')
    rep("{ const ib = $('itemBtn'), held = state === 'play' && P.st === 'play' ? P.held : null;", "pocketHud(); { const ib = $('itemBtn'), held = state === 'play' && P.st === 'play' ? P.held : null;")
    rep("$('itemBtn').addEventListener('click', e => { e.preventDefault(); if (state === 'play' && e.detail === 0) useHeld(P); });",
        "$('itemBtn').addEventListener('click', e => { e.preventDefault(); if (state === 'play' && e.detail === 0) useHeld(P); });\n"
        "$('itemBtn2').addEventListener('pointerdown', e => { e.preventDefault(); e.stopPropagation(); AU.init(); if (state === 'play' && !useHeld2(P)) { AU.nope(); kick($('itemBtn2'), 'nope'); } });\n"
        "$('itemBtn2').addEventListener('click', e => { e.preventDefault(); if (state === 'play' && e.detail === 0) useHeld2(P); });\n"
        "$('orbBtn').addEventListener('pointerdown', e => { e.preventDefault(); e.stopPropagation(); AU.init(); if (state === 'play' && !useOrb(P)) { AU.nope(); kick($('orbBtn'), 'nope'); } });\n"
        "$('orbBtn').addEventListener('click', e => { e.preventDefault(); if (state === 'play' && e.detail === 0) useOrb(P); });")
    rep("  if ((k === 'f' || k === 'F') && !e.repeat) { e.preventDefault(); if (state === 'play' && !useHeld(P)) AU.nope(); return; }",
        "  if ((k === 'f' || k === 'F') && !e.repeat) { e.preventDefault(); if (state === 'play' && !useHeld(P)) AU.nope(); return; }\n"
        "  if ((k === 'g' || k === 'G') && !e.repeat) { e.preventDefault(); if (state === 'play' && !useHeld2(P)) AU.nope(); return; }\n"
        "  if ((k === 'c' || k === 'C') && !e.repeat) { e.preventDefault(); if (state === 'play' && !useOrb(P)) AU.nope(); return; }")

    # ---- the Paint Trap pick-up
    rep("  slam: { name: 'Slam', dur: 0, tip: 'Slam saved! Tap the slam button to smash down a huge circle.' },\n};",
        "  slam: { name: 'Slam', dur: 0, tip: 'Slam saved! Tap the slam button to smash down a huge circle.' },\n  trap: { name: 'Paint Trap', dur: 0, tip: 'Paint Trap! Drop it, and the next rival over it gets splatted.' },\n};")
    rep("let powers = [];", "let powers = [], trapList = []; const TRAP_G = { ball: new THREE.SphereGeometry(0.24, 20, 14), cap: new THREE.CylinderGeometry(0.07, 0.08, 0.08, 12), fuse: new THREE.CylinderGeometry(0.02, 0.02, 0.16, 6), spark: new THREE.SphereGeometry(0.05, 8, 6), drip: new THREE.SphereGeometry(0.1, 10, 6), dome: new THREE.SphereGeometry(0.34, 20, 10, 0, Math.PI * 2, 0, Math.PI / 2), light: new THREE.SphereGeometry(0.055, 10, 8), ring: new THREE.RingGeometry(0.52, 0.66, 40).rotateX(-Math.PI / 2) }, trapSparkM = new THREE.MeshBasicMaterial({ color: 0xFFD54F }), trapCapM = toon(0x2A2436), trapLightOn = new THREE.MeshBasicMaterial({ color: 0xFFFFFF }), trapLightOff = new THREE.MeshBasicMaterial({ color: 0x5A1428 });")
    rep("  else { add(PU_G.tip, puIconMat, V(0, -0.13, 0), [Math.PI, 0, 0]); add(PU_G.neck, puIconMat, V(0, 0.18, 0)); }",
        "  else if (type === 'trap') { add(TRAP_G.ball, puIconMat, V(0, -0.04, 0)); add(TRAP_G.cap, trapCapM, V(0, 0.22, 0)); add(TRAP_G.fuse, trapCapM, V(0.05, 0.31, 0), [0, 0, -0.5]); add(TRAP_G.drip, puIconMat, V(-0.13, -0.24, 0.06)); add(TRAP_G.drip, puIconMat, V(0.12, -0.23, -0.05)); const sp = new THREE.Mesh(TRAP_G.spark, trapSparkM); sp.position.set(0.1, 0.39, 0); spin.add(sp); }\n"
        "  else { add(PU_G.tip, puIconMat, V(0, -0.13, 0), [Math.PI, 0, 0]); add(PU_G.neck, puIconMat, V(0, 0.18, 0)); }")
    rep("  D.held = null; D.heldT = 0;\n  if (type === 'turret') { startTurret(D);", "  D.held = null; D.heldT = 0;\n  if (type === 'trap') { dropTrap(D); for (const B of ACTIVE) if (B.ai) B.ai.thinkT = 0; return true; }\n  if (type === 'turret') { startTurret(D);")
    rep("const type = tut && tut.noTurret ? 'roller' : itemSpawn.last === 'roller' ? (Math.random() < 0.65 ? 'turret' : 'roller') : (Math.random() < 0.65 ? 'roller' : 'turret');",
        "const type = tut && tut.noTurret ? 'roller' : (tut || tut2 || tut3) ? (itemSpawn.last === 'roller' ? (Math.random() < 0.65 ? 'turret' : 'roller') : (Math.random() < 0.65 ? 'roller' : 'turret')) : (() => { const w = { roller: 0.42, turret: 0.3, trap: 0.28 }; if (w[itemSpawn.last]) w[itemSpawn.last] *= 0.45; let r = Math.random() * (w.roller + w.turret + w.trap); for (const k of ['roller', 'turret', 'trap']) if ((r -= w[k]) <= 0) return k; return 'roller'; })(); // (the lessons keep to rollers and turrets)")
    rep("  powers.forEach(pw => pw.g && scene.remove(pw.g)); powers = [];", "  clearTraps(); powers.forEach(pw => pw.g && scene.remove(pw.g)); powers = [];")
    rep("  itemTick(dt);", "  itemTick(dt); trapTick(dt); freezeTick(dt);")
    rep("(D.held === 'turret' ? (near && D.heldT > 0.6) || D.heldT > 6 : D.heldT > 1 + Math.random() * 1.5)",
        "(D.held === 'turret' ? (near && D.heldT > 0.6) || D.heldT > 6 : D.held === 'trap' ? (O && O.st === 'play' && Math.hypot(O.x - D.x, O.z - D.z) < 7 && D.heldT > 0.8) || D.heldT > 6 : D.heldT > 1 + Math.random() * 1.5)")
    m = re.search(r"\nconst ITEM_ICON = \{[^\n]*\};\n", s); assert m, 'ITEM_ICON line'
    s = s[:m.end()] + "ITEM_ICON.trap = '" + ICON_TRAP + "';\n" + s[m.end():]

    # ---- Flash Freeze: the frozen look (an ice shell, an icy tint, the pose held, no stun stars), the thaw, the frost on screen
    rep("  if (D.stunT > 0) { D.stunT -= dt; D.spd = 0; D.turn = 0;", "  if (D.frozenT > 0) { D.frozenT -= dt; if (D.frozenT <= 0) { D.frozenT = 0; thawFx(D); } }\n  if (D.stunT > 0) { D.stunT -= dt; D.spd = 0; D.turn = 0;")
    rep("A.update(dt); if (D) D.strokeK =", "A.update(D && D.frozenT > 0 ? 0 : dt); if (D) D.strokeK =")
    rep("const on = (D.stunT > 0 && D.st === 'play') || !!(D.ip && D.ip.stars);", "const on = (D.stunT > 0 && D.st === 'play' && !(D.frozenT > 0)) || !!(D.ip && D.ip.stars);")
    rep("if (safe(P) && P.st === 'play') tmpCol.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));", "if (safe(P) && P.st === 'play') tmpCol.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));\n    if (P.frozenT > 0) tmpCol.lerp(COL_ICE, 0.8);")
    rep("if (safe(D) && D.st === 'play') tmpCol2.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));", "if (safe(D) && D.st === 'play') tmpCol2.lerp(COL_WHITE, 0.32 + 0.14 * Math.sin(clock * 40));\n    if (D.frozenT > 0) tmpCol2.lerp(COL_ICE, 0.8);")
    rep("cpuLook(LH, dt, rdt, ke, kf, playing); cpuLook(L2, dt, rdt, ke, kf, playing);", "cpuLook(LH, dt, rdt, ke, kf, playing); cpuLook(L2, dt, rdt, ke, kf, playing); iceFrame(rdt);")
    rep('<div class="flash" id="flash"></div>', '<div class="flash" id="flash"></div>\n  <div class="frost" id="frost" aria-hidden="true"></div>')

    # ---- the new code itself, and its styles
    rep("\n// ---------- the giant orb: a glowing, color-shifting orb", JS_ITEMS + "\n// ---------- the giant orb: a glowing, color-shifting orb")
    rep(".mworld .world::after{transition:opacity .2s}\n", ".mworld .world::after{transition:opacity .2s}\n" + CSS)
    return s
