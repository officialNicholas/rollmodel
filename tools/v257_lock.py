"""v257: Time trial and Showdown open at rank 2, the rank the Strokes open at. Before that their cards on Choose Event are greyed with
a 'Rank 2' tag, and a tap says what it takes; a save left on one of them goes back to Versus. Bloop's rank-2 card says they're open,
and each wears a 'New!' tag until it's picked."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
JS = r"""// (v257) Time trial and Showdown open at rank 2, with the Strokes: until then their cards are greyed with a lock tag
const EV_LOCKED = ['solo', 'showdown'], evUnlocked = () => repOf(store.xp || 0).lv >= ABIL_RANK;
function evLockPaint() {
  const on = evUnlocked();
  for (const k of EV_LOCKED) { const c = evEl.querySelector('.evcard[data-ev="' + k + '"]'); if (!c) continue;
    if (!c.querySelector('.evlock')) c.insertAdjacentHTML('beforeend', '<i class="evlock" aria-hidden="true">' + ABIL_LOCK + 'Rank ' + ABIL_RANK + '</i><i class="evnew" aria-hidden="true">New!</i>');
    c.classList.toggle('lock', !on); c.classList.toggle('fresh', on && !!(store.evNew && store.evNew[k]));
    const b = c.querySelector('.evmain'); if (on) b.removeAttribute('aria-disabled'); else b.setAttribute('aria-disabled', 'true'); }
}
function evLockNote(k) {
  if (evUnlocked()) { if (store.evNew && store.evNew[k]) { delete store.evNew[k]; save(); } return false; }
  AU.nope(); buzz(8); const c = evEl.querySelector('.evcard[data-ev="' + k + '"]'), old = c.querySelector('.evtoast'); if (old) old.remove();
  const t = document.createElement('span'); t.className = 'evtoast'; t.setAttribute('role', 'status'); t.textContent = 'Reach rank ' + ABIL_RANK + ' to unlock ' + (k === 'solo' ? 'Time trial' : 'Showdown'); c.appendChild(t); setTimeout(() => t.remove(), 1700); return true;
}
const evGate = (k, fn) => () => { AU.init(); if (evLockNote(k)) return; AU.ui(); fn(); };
function evModeGuard() { if (!evUnlocked() && ['solo', 'ffa', 'duo'].includes(mode)) { mode = 'duel'; store.mode = 'duel'; } } // (a save left on one of them before rank 2: back to Versus)
"""
CSS = r"""/* (v257) Time trial and Showdown before rank 2: greyed, with a lock tag; just opened: a New! tag */
.evcard.lock .evtop,.evcard.lock .evart{filter:grayscale(1) brightness(.62)}
.evcard.lock .evbar{color:#7E7690}
.evlock{position:absolute;right:16px;bottom:14px;z-index:2;display:flex;align-items:center;gap:5px;padding:5px 10px 4px;border-radius:5px;background:#171320;color:#F4EEE3;font:900 11px/1 var(--font-head);letter-spacing:.08em;text-transform:uppercase;transform:rotate(4deg);box-shadow:0 0 0 2.5px #F4EEE3,0 3px 0 #171320;pointer-events:none}
.evlock svg{width:11px;height:11px;color:var(--gold)}
.evcard:not(.lock) .evlock{display:none}
.evnew{position:absolute;left:12px;top:-10px;z-index:3;padding:5px 10px 4px;border-radius:999px;background:#E3122F;color:#fff;font:900 11px/1 var(--font-head);letter-spacing:.08em;text-transform:uppercase;box-shadow:0 0 0 2.5px #171320;transform:rotate(-5deg);animation:evnew 1.4s ease-in-out infinite;pointer-events:none}
@keyframes evnew{50%{transform:rotate(-5deg) scale(1.12)}}
.evcard:not(.fresh) .evnew{display:none}
@media (prefers-reduced-motion:reduce){.evnew{animation:none}}"""
def apply(s):
    s = rep(s, "// an event picked: its mode, then the canvases to vote on (back comes here)\nfunction evPick(m) {", JS + "// an event picked: its mode, then the canvases to vote on (back comes here)\nfunction evPick(m) {")
    s = rep(s, "evArt(); evFold(); requestAnimationFrame(evMoreTick);", "evArt(); evFold(); evLockPaint(); requestAnimationFrame(evMoreTick);")
    s = rep(s, "$('evSolo').addEventListener('click', uiClick(() => evPick('solo')));", "$('evSolo').addEventListener('click', evGate('solo', () => evPick('solo')));")
    s = rep(s, "$('evShow').addEventListener('click', uiClick(() => { const c = $('evShow').closest('.evcard')", "$('evShow').addEventListener('click', evGate('showdown', () => { const c = $('evShow').closest('.evcard')")
    s = rep(s, "  teamTint = false; tutLeave(); clearShot();", "  teamTint = false; evModeGuard(); tutLeave(); clearShot();")
    # Bloop's rank-2 card: the Strokes, and the two events opening with them
    s = rep(s, "'You’ve unlocked Strokes: your special move, and a skill. Come see.'", "'You’ve unlocked Strokes: your special move, and a skill. Time trial and Showdown are open now too. Strokes first: come see.'")
    s = rep(s, "if (n === 1) { AU.fanfare && AU.fanfare(); AU.bloop(0.55); menu.classList.add('tutoring'); }", "if (n === 1) { store.evNew = { solo: 1, showdown: 1 }; AU.fanfare && AU.fanfare(); AU.bloop(0.55); menu.classList.add('tutoring'); }")
    s = rep(s, "\n</style>\n\n<div id=\"stage\">", "\n" + CSS.strip() + "\n</style>\n\n<div id=\"stage\">")
    return s
