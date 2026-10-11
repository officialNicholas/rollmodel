// ---------- Choose Event (v209): Play opens it. Solo and Versus CPU (a 1v1 or a 3-way) go on to the canvas vote; Showdown is coming;
// the tutorial plays the lesson again ----------
const evEl = $('mEvents');
let evFrom = false; // (the canvases were opened from here: their back button comes back here)
function evArt() { const set = (id, sid) => { const im = $(id), src = stageArtOf(sid); if (src && im.getAttribute('src') !== src) im.src = src; }; set('evSoloArt', 'blank'); set('evVsArt', VOTE_STAGES.includes(stageSel) ? stageSel : 'cathedral'); set('evShowArt', 'manor'); set('evTutArt', 'island'); }
function evFold() { $('evVs').closest('.evcard').classList.remove('open'); $('evVsPick').hidden = true; $('evVs').setAttribute('aria-expanded', 'false'); }
function openEvents() {
  if (state !== 'menu' || building || lookOpen || shopOpen || menuPage === 'events') return;
  if (menuPage === 'worlds') { closeSeason(); $('mWorld').hidden = true; }
  menuPage = 'events'; menu.dataset.page = 'events'; $('mHome').hidden = true; evEl.hidden = false; document.body.classList.add('evon'); closeSide(true); evArt(); evFold();
  for (const c of evEl.querySelectorAll('.evcard')) { c.style.animation = 'none'; void c.offsetWidth; c.style.animation = ''; }
  setTimeout(() => $('evVs').focus({ preventScroll: true }), 40);
}
function closeEvents() { if (menuPage !== 'events') return; evFold(); evEl.hidden = true; document.body.classList.remove('evon'); menuPage = 'home'; menu.dataset.page = 'home'; $('mHome').hidden = false; heroT = 0; setTimeout(() => $('homePlay').focus({ preventScroll: true }), 30); }
// an event picked: its mode, then the canvases to vote on (back comes here)
function evPick(m) { if (building) return; evFold(); evEl.hidden = true; document.body.classList.remove('evon'); menuPage = 'home'; if (mode !== m) setMode(m); evFrom = true; openWorlds(); }
$('evBack').addEventListener('click', uiClick(closeEvents));
$('evSolo').addEventListener('click', uiClick(() => evPick('solo')));
$('evVs').addEventListener('click', uiClick(() => { const c = $('evVs').closest('.evcard'), open = !c.classList.contains('open'); c.classList.toggle('open', open); $('evVsPick').hidden = !open; $('evVs').setAttribute('aria-expanded', String(open)); if (open) setTimeout(() => $('evVsPick').querySelector('[data-m="' + (mode === 'trio' ? 'trio' : 'duel') + '"]').focus({ preventScroll: true }), 30); }));
$('evVsPick').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; AU.init(); AU.pop(); evPick(b.dataset.m); });
$('evShow').addEventListener('click', () => { AU.init(); AU.nope(); const c = $('evShow').closest('.evcard'), old = c.querySelector('.evtoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'evtoast'; t.textContent = 'Showdown is coming soon'; c.appendChild(t); setTimeout(() => t.remove(), 1700); });
$('evTut').addEventListener('click', uiClick(() => { if (building) return; store.tut = { ph: 'match' }; save(); evFold(); evEl.hidden = true; document.body.classList.remove('evon'); menuPage = 'home'; menu.dataset.page = 'home'; $('mHome').hidden = false; start(); }));
