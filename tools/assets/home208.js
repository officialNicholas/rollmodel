// ---------- the home screen (v208): the floating power bar over your character (your rank, your paint filling toward the next one, your
// name on a strip of tape), your stats behind it, your dabs up top, a menu that slides open, friends and the spots beside you (soon) ----------
const pbar = $('pbar'), slotL = $('slotL'), slotR = $('slotR'), sideMenu = $('sideMenu');
const PBW = 150, PBH = 30, PBD = 16; // the track, and the room under it for the drips
const PB = { shown: 0, v: 0, lv: 0, frac: 0, dispLv: 0, t: 0, g: null, dpr: 0, top: 0, mT: 0, ret: null, docFrom: null, ink: '#E3122F', hi: '#FF6175', lo: '#99091F',
  drips: [{ u: 0.2, L: 5, A: 5, w: 0.8, p: 0.4, r: 2.4 }, { u: 0.55, L: 8, A: 6, w: 0.6, p: 2.1, r: 3 }, { u: 0.86, L: 4, A: 4, w: 1, p: 4, r: 2.2 }], bubs: [] };
for (let i = 0; i < 6; i++) PB.bubs.push({ u: Math.random(), y: 0.25 + Math.random() * 0.55, r: 0.7 + Math.random() * 1.3, s: 0.015 + Math.random() * 0.03 });
const pbV = new THREE.Vector3(), pbR = new THREE.Vector3();
// what it shows: your rank and the next one, your paint toward it (a rank up since it last showed runs the paint to the end first)
function paintPBar() {
  const r = repOf(store.xp || 0), cs = getComputedStyle(document.documentElement), n = playerName();
  PB.ink = cs.getPropertyValue('--ink').trim() || '#E3122F'; PB.hi = cs.getPropertyValue('--ink-hi').trim() || PB.ink; PB.lo = cs.getPropertyValue('--ink-lo').trim() || PB.ink;
  PB.lv = r.lv; PB.frac = r.x / r.need; if (!PB.dispLv || PB.dispLv > r.lv) { PB.dispLv = r.lv; PB.shown = PB.frac; PB.v = 0; }
  $('pbName').textContent = n; $('pbXp').innerHTML = r.x + '<small>/' + r.need + '</small>'; pbNums();
  pbar.setAttribute('aria-label', n + '. Rank ' + r.lv + ', ' + r.x + ' of ' + r.need + ' XP to rank ' + (r.lv + 1) + '. Your stats');
}
function pbNums() { $('pbLvl').textContent = PB.dispLv; $('pbNext').textContent = PB.dispLv + 1; }
function pbarOn() { return state === 'menu' && menuPage === 'home' && !lookOpen && !shopOpen && !irisBusy && $('orient').hidden && !menu.hidden && !!VP.slime; }
function pbRR(g, x, y, w, h, r) { g.beginPath(); g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r); g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath(); }
// the paint in the bar: a body of it with a wobbling front edge, a shine along its top, bubbles drifting in it, drips hanging off its underside
function pbDraw(rdt) {
  const cv = $('pbCanvas'), dpr = Math.min(2, window.devicePixelRatio || 1);
  if (PB.dpr !== dpr || !PB.g) { cv.width = Math.round(PBW * dpr); cv.height = Math.round((PBH + PBD) * dpr); PB.g = cv.getContext('2d'); PB.dpr = dpr; if (!PB.g) return; }
  const g = PB.g, dt = Math.min(0.05, rdt || 0); PB.t += dt;
  // the fill springs toward where it should be (sloshing a little past it); catching up a rank, it runs to the end, then the rank pops
  const catching = PB.dispLv < PB.lv, tgt = catching ? 1.04 : PB.frac;
  const a = 34 * (tgt - PB.shown) - 7.5 * PB.v; PB.v += a * dt; PB.shown = clamp(PB.shown + PB.v * dt, 0, 1);
  if (catching && PB.shown >= 0.999) { PB.dispLv++; PB.shown = 0; PB.v = 0; pbNums(); pbar.classList.remove('lvup'); void pbar.offsetWidth; pbar.classList.add('lvup'); try { AU.pop(); } catch (e) {} }
  g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, PBW, PBH + PBD);
  pbRR(g, 1.5, 1.5, PBW - 3, PBH - 3, 9); g.fillStyle = '#2A2437'; g.fill();
  const f = PB.shown, x0 = 3, x1 = 3 + (PBW - 6) * f, t = PB.t;
  g.save(); pbRR(g, 3, 3, PBW - 6, PBH - 6, 7); g.clip();
  if (f > 0.004) {
    g.beginPath(); g.moveTo(x0 - 2, 2);
    for (let i = 0; i <= 10; i++) { const y = 3 + (PBH - 6) * i / 10, w = Math.sin(t * 3 + i * 0.8) * 1.5 + Math.sin(t * 4.7 - i * 1.3) * 0.9 + PB.v * 5 * Math.sin(i * 0.45); g.lineTo(Math.max(x0, x1 + w), y); }
    g.lineTo(x0 - 2, PBH); g.closePath();
    const gr = g.createLinearGradient(0, 3, 0, PBH - 3); gr.addColorStop(0, PB.hi); gr.addColorStop(0.42, PB.ink); gr.addColorStop(1, PB.lo); g.fillStyle = gr; g.fill();
    g.globalAlpha = 0.5; g.fillStyle = '#fff'; pbRR(g, 8, 6.5, Math.max(0, x1 - 18), 3, 1.5); g.fill();
    g.globalAlpha = 0.85; g.beginPath(); g.ellipse(Math.max(9, x1 - 9 + Math.sin(t * 2) * 1.5), 8, 2.2, 1.4, 0, 0, 6.2832); g.fill();
    g.globalAlpha = 0.35; for (const b of PB.bubs) { b.u = (b.u + b.s * dt) % 1; const bx = x0 + 4 + (x1 - 10) * b.u; if (bx < x1 - 6) { g.beginPath(); g.arc(bx, 3 + (PBH - 6) * (b.y + 0.08 * Math.sin(t * 2 + b.u * 9)), b.r, 0, 6.2832); g.fill(); } }
    g.globalAlpha = 1;
  }
  g.globalAlpha = 0.35; g.fillStyle = '#000'; g.fillRect(0, 3, PBW, 2); g.globalAlpha = 1;
  g.restore();
  pbRR(g, 1.5, 1.5, PBW - 3, PBH - 3, 9); g.lineWidth = 3; g.strokeStyle = '#171320'; g.stroke();
  if (f > 0.06) for (const d of PB.drips) {
    const dx = x0 + 6 + (x1 - x0 - 14) * d.u, L = d.L + d.A * (0.5 + 0.5 * Math.sin(t * d.w + d.p)), y0 = PBH - 4, y1 = y0 + L;
    g.lineCap = 'round'; g.strokeStyle = '#171320'; g.lineWidth = d.r * 2 + 3; g.beginPath(); g.moveTo(dx, y0); g.lineTo(dx, y1); g.stroke();
    g.fillStyle = '#171320'; g.beginPath(); g.arc(dx, y1 + d.r * 0.3, d.r * 1.3 + 1.5, 0, 6.2832); g.fill();
    g.strokeStyle = PB.ink; g.lineWidth = d.r * 2; g.beginPath(); g.moveTo(dx, y0 - 2); g.lineTo(dx, y1); g.stroke();
    g.fillStyle = PB.ink; g.beginPath(); g.arc(dx, y1 + d.r * 0.3, d.r * 1.3, 0, 6.2832); g.fill();
    g.fillStyle = 'rgba(255,255,255,.55)'; g.beginPath(); g.arc(dx - d.r * 0.45, y1 - d.r * 0.1, d.r * 0.35, 0, 6.2832); g.fill();
  }
}
// where it floats: over your character's head (and its hat), never up into the top bar or the logo; the spots either side of it
function placePBar() {
  if (pbar.hidden) return;
  pbV.set(P.x, P.y + charTall(myLook) + 0.07, P.z).project(camera);
  let sx = (pbV.x * 0.5 + 0.5) * viewW, sy = (0.5 - pbV.y * 0.5) * viewH - 6;
  sx = clamp(sx, 118, viewW - 118); sy = Math.max(sy, PB.top + 62) + Math.sin(clock * 1.7) * 2.2;
  pbar.style.left = sx.toFixed(1) + 'px'; pbar.style.top = sy.toFixed(1) + 'px';
  pbR.setFromMatrixColumn(camera.matrixWorld, 0); pbR.y = 0; pbR.normalize();
  for (const [el, s] of [[slotL, -1], [slotR, 1]]) {
    pbV.set(P.x + pbR.x * s * 1.05, P.y + 0.28, P.z + pbR.z * s * 1.05).project(camera);
    el.style.left = clamp((pbV.x * 0.5 + 0.5) * viewW, 42, viewW - 42).toFixed(1) + 'px'; el.style.top = ((0.5 - pbV.y * 0.5) * viewH).toFixed(1) + 'px';
  }
}
function pbarTick(rdt) {
  const on = pbarOn();
  if (pbar.hidden === on) { pbar.hidden = !on; slotL.hidden = slotR.hidden = !on; }
  if (document.body.classList.contains('homeon') !== on) document.body.classList.toggle('homeon', on);
  if (!on) { if (!sideMenu.hidden && state !== 'menu') closeSide(true); return; }
  PB.mT -= rdt; if (PB.mT <= 0) { PB.mT = 0.5; let b = 0; for (const id of ['lobbyTop', 'logo']) { const e = $(id); if (e && e.offsetParent !== null) { const r = e.getBoundingClientRect(); if (r.height > 0) b = Math.max(b, r.bottom); } } PB.top = b; }
  pbDraw(rdt);
}
pbar.addEventListener('click', uiClick(() => openStats()));
// your stats: your rank and what's left to the next, wins, matches, win rate, best coverage; your name, and changing it
function paintStats() {
  const r = repOf(store.xp || 0); let wins = 0, vs = 0, best = 0;
  for (const k in store.wins || {}) wins += store.wins[k] || 0;
  for (const k in store.played || {}) if (k !== 'solo') vs += store.played[k] || 0;
  for (const k in store.bestCov || {}) best = Math.max(best, store.bestCov[k] || 0);
  $('stName').textContent = playerName(); $('stLvl').textContent = r.lv; $('stTitle').textContent = r.name; $('stXp').textContent = r.x + ' / ' + r.need + ' XP to rank ' + (r.lv + 1);
  $('stFill').style.width = (100 * r.x / r.need).toFixed(1) + '%';
  $('stWins').textContent = wins; $('stPlayed').textContent = store.runs || 0; $('stRate').textContent = (vs ? Math.round(100 * wins / vs) : 0) + '%'; $('stBest').textContent = best + '%';
}
function openStats() { if (state !== 'menu' || lookOpen) return; paintStats(); $('statsModal').hidden = false; setTimeout(() => $('statsClose').focus({ preventScroll: true }), 30); }
function closeStats() { if ($('statsModal').hidden) return; $('statsModal').hidden = true; pbar.focus({ preventScroll: true }); }
$('statsClose').addEventListener('click', uiClick(closeStats));
$('statsModal').addEventListener('click', e => { if (e.target === $('statsModal')) closeStats(); });
$('stRename').addEventListener('click', uiClick(() => { $('statsModal').hidden = true; openName(false); }));
// friends, and a friend joining your lobby: soon
function openFriends() { if (state !== 'menu') return; PB.ret = document.activeElement; $('friendsModal').hidden = false; setTimeout(() => $('friendsClose').focus({ preventScroll: true }), 30); }
function closeFriends() { if ($('friendsModal').hidden) return; $('friendsModal').hidden = true; if (PB.ret && PB.ret.focus) PB.ret.focus({ preventScroll: true }); }
$('friendsBtn').addEventListener('click', uiClick(openFriends));
for (const el of [slotL, slotR]) el.addEventListener('click', uiClick(openFriends));
$('friendsClose').addEventListener('click', uiClick(closeFriends));
$('friendsModal').addEventListener('click', e => { if (e.target === $('friendsModal')) closeFriends(); });
// the menu: slides in from the right (Settings, the sound; more to come)
function paintSide() { const off = !!store.sfxOff && !!store.musicOff; $('smSndL').textContent = off ? 'Sound off' : 'Sound on'; $('smSndI').innerHTML = off ? SM_SND_OFF : SM_SND_ON; $('smSnd').setAttribute('aria-pressed', String(!off)); }
function openSide() { if (state !== 'menu' || lookOpen || shopOpen) return; paintSide(); sideMenu.hidden = false; void sideMenu.offsetWidth; sideMenu.classList.add('on'); $('hamBtn').setAttribute('aria-expanded', 'true'); setTimeout(() => $('smSet').focus({ preventScroll: true }), 40); }
function closeSide(quiet) { if (sideMenu.hidden) return; sideMenu.classList.remove('on'); $('hamBtn').setAttribute('aria-expanded', 'false'); setTimeout(() => { if (!sideMenu.classList.contains('on')) sideMenu.hidden = true; }, reduceMotion ? 0 : 320); if (!quiet) $('hamBtn').focus({ preventScroll: true }); }
$('hamBtn').addEventListener('click', uiClick(() => sideMenu.hidden || !sideMenu.classList.contains('on') ? openSide() : closeSide()));
$('smClose').addEventListener('click', uiClick(() => closeSide()));
sideMenu.querySelector('.sscrim').addEventListener('click', () => closeSide());
$('smSet').addEventListener('click', uiClick(() => { closeSide(true); openSettings(); }));
$('smSnd').addEventListener('click', () => { toggleSound(); paintSide(); });
// the sound: the effects and the music each on or off (Settings); the menu's switch and the M key turn both off or back on together
function applyMix() { store.muted = !!store.sfxOff && !!store.musicOff; AU.mix(!store.musicOff, !store.sfxOff); paintSoundBtn(); }
for (const [id, key] of [['sfxPick', 'sfxOff'], ['musPick', 'musicOff']]) $(id).addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; const off = b.dataset.v === 'off'; if (!!store[key] === off) return; store[key] = off; save(); AU.init(); applyMix(); paintSettings(); if (key === 'sfxOff' && !off) AU.ui(); });
$('setBack').addEventListener('click', uiClick(doneSettings));
// the pages of words: the terms, the privacy note, the credits (each comes back to Settings)
const DOCS = {
  tos: ['Terms of Service', '<p>Roll Model is still in development. The full terms of service will be published here before the game launches.</p><p>Until then, play fair and have fun.</p>'],
  priv: ['Privacy Policy', '<p>Roll Model saves your progress (your name, dabs, items, ranks and settings) in this browser, on this device. You don’t need an account to play.</p><p>Clearing this browser’s site data resets your progress.</p><p>The full privacy policy will be published here before the game launches.</p>'],
  cred: ['Credits', '<h3>Roll Model</h3><p>Season 1: Halloween</p><h3>Built with</h3><p>three.js (MIT License)</p><h3>Type</h3><p>Bowlby One and Figtree (SIL Open Font License)</p><h3>Sound and voices</h3><p>Made with Ludo.ai</p><h3>3D items</h3><p>Made with Meshy</p><h3>Thanks</h3><p>To everyone who rolls through the paint.</p>']
};
function openDoc(k) { const d = DOCS[k]; if (!d) return; PB.docFrom = k; $('docTitle').textContent = d[0]; $('docBody').innerHTML = d[1]; $('docBody').scrollTop = 0; setModal.hidden = true; $('docModal').hidden = false; setTimeout(() => $('docClose').focus({ preventScroll: true }), 30); }
function closeDoc() { if ($('docModal').hidden) return; $('docModal').hidden = true; if (state === 'menu') { setModal.hidden = false; const b = $({ tos: 'tosBtn', priv: 'privBtn', cred: 'credBtn' }[PB.docFrom]); if (b) b.focus({ preventScroll: true }); } }
for (const [id, k] of [['tosBtn', 'tos'], ['privBtn', 'priv'], ['credBtn', 'cred']]) $(id).addEventListener('click', uiClick(() => openDoc(k)));
$('docClose').addEventListener('click', uiClick(closeDoc));
$('docModal').addEventListener('click', e => { if (e.target === $('docModal')) closeDoc(); });
