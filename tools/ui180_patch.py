#!/usr/bin/env python3
"""v242: Strokes open at rank 2 (the Giant free to craft then, the lesson then); Commissions open at rank 3. The commissions plate sits
locked on the rail till then (greyed, a Rank 3 tag, a tap says so), and Ol' Bloop's "Commissions are open!" card comes at rank 3, not after
the first real match (which now goes straight back to the plain lobby)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui179_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- the ranks
rep("const ABIL_RANK = 3, ABIL_LOCK =", "const ABIL_RANK = 2, COMM_RANK = 3, ABIL_LOCK =")
rep('<button class="plate abil locked" id="abilBtn" type="button" aria-label="Abilities, locked until rank 3">', '<button class="plate abil locked" id="abilBtn" type="button" aria-label="Strokes, locked until rank 2">')
# ---- the commissions plate: locked till rank 3
rep("/* abilities: violet construction paper, cut by hand,", """/* commissions: locked till rank 3, greyed with a tag like the strokes plate */
#commBtn.locked{color:#8A8396;filter:grayscale(1) brightness(1.05)}
#commBtn.locked .cring{opacity:.55}
#commBtn.locked .ctimer{display:none}
#commBtn .ctag{position:absolute;z-index:2;left:50%;bottom:-9px;display:none;align-items:center;gap:3px;padding:3px 6px 2px;border-radius:999px;background:#171320;color:#F4EEE3;font:900 10px/1 var(--font-head);letter-spacing:.02em;white-space:nowrap;transform:translateX(-50%);box-shadow:0 2px 0 rgba(23,19,32,.25)}
#commBtn .ctag svg{width:9px;height:9px;color:var(--gold)}
#commBtn.locked .ctag{display:flex}
/* abilities: violet construction paper, cut by hand,""")
rep('<i class="pbadge" id="commBadge" hidden></i><b class="ctimer" id="commTimer" aria-hidden="true"></b></button>', '<i class="pbadge" id="commBadge" hidden></i><b class="ctimer" id="commTimer" aria-hidden="true"></b><b class="ctag" id="commTag" aria-hidden="true"></b></button>')
rep("function paintAbil() {", """const commsDue = () => repOf(store.xp || 0).lv >= COMM_RANK; // (commissions open at rank 3)
function paintComm() { const b = $('commBtn'), on = commsDue(); b.classList.toggle('locked', !on); if (!on) { $('commTag').innerHTML = ABIL_LOCK + 'Rank ' + COMM_RANK; $('commBadge').hidden = true; } b.setAttribute('aria-label', on ? 'Commissions' : 'Commissions, locked until rank ' + COMM_RANK); }
let commT = 0;
function paintAbil() { paintComm();""")
rep("$('commBtn').addEventListener('click', () => { AU.init(); AU.ui(); openComms(); });",
    "$('commBtn').addEventListener('click', () => { AU.init(); if (!commsDue()) { AU.nope(); const b = $('commBtn'), rail = b.parentElement, old = b.querySelector('.abtoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'abtoast'; t.setAttribute('role', 'status'); t.textContent = 'Reach rank ' + COMM_RANK + ' to open Commissions'; b.appendChild(t); kick(b, 'abnudge'); rail.classList.add('abup'); clearTimeout(commT); commT = setTimeout(() => { t.remove(); rail.classList.remove('abup'); }, 2000); return; } AU.ui(); openComms(); });")
rep("function openComms() { if (state !== 'menu' || lookOpen) return;", "function openComms() { if (state !== 'menu' || lookOpen || !commsDue()) return;")
# ---- the lesson: the first real match goes back to a plain lobby; the commissions card comes at rank 3 (after the strokes lesson if both are due)
rep("if (tutPh() === 'match2') { tut2 = null; tutHide(); delete store.tut.price; tutSet('welcome'); save(); }", "if (tutPh() === 'match2') { tut2 = null; tutHide(); delete store.tut.price; tutSet('done'); save(); }")
rep("function tutStrokesDue() { return tutPh() === 'done' && !store.tut.strokes && strokesDue() &&",
    "function tutCommsDue() { return tutPh() === 'done' && !store.tut.comms && commsDue() && (store.tut.strokes === 1 || !strokesDue()) && state === 'menu' && menuPage === 'home' && !lookOpen && !shopOpen && !building && !irisBusy && setModal.hidden && nameModal.hidden && howModal.hidden && $('tutGo').hidden && !vic; }\nfunction tutStrokesDue() { return tutPh() === 'done' && !store.tut.strokes && strokesDue() &&")
rep("  if (tutPh() === 'done' && tutStrokesDue()) { if (!tutStrokesAt) tutStrokesAt = performance.now(); if (performance.now() - tutStrokesAt > 1200) tutStrokesCard(1); return; } /* (a beat of the lobby, then the praise) */",
    "  if (tutPh() === 'done' && tutStrokesDue()) { if (!tutStrokesAt) tutStrokesAt = performance.now(); if (performance.now() - tutStrokesAt > 1200) tutStrokesCard(1); return; } /* (a beat of the lobby, then the praise) */\n  if (tutPh() === 'done' && tutCommsDue()) { if (!tutCommsAt) tutCommsAt = performance.now(); if (performance.now() - tutCommsAt > 1200) { menu.classList.add('tutoring'); tutWelcome(); } return; } /* (rank 3: commissions open) */")
rep("let tutStrokesAt = 0, tutSDone = 0;", "let tutStrokesAt = 0, tutSDone = 0, tutCommsAt = 0;")
rep("function tutWelcomeDone(open) { const el = $('tutGo'); el.classList.remove('on'); el.hidden = true; coachCorner(null); el.dataset.mode = ''; tutSet('done');",
    "function tutWelcomeDone(open) { const el = $('tutGo'); el.classList.remove('on'); el.hidden = true; coachCorner(null); el.dataset.mode = ''; store.tut.comms = 1; tutSet('done'); save(); paintComm();")
# the old welcome phase (saves from before): straight to done in the lobby, no card
rep("    tutHide(); if (state === 'menu' && menuPage === 'home' && !lookOpen && !shopOpen && !building && !irisBusy) tutWelcome(); return; }",
    "    tutHide(); if (state === 'menu') tutSet('done'); return; }")
rep("return tutShow('Back to the lobby. Something new is waiting', 'menuBtn', 'welback');", "return tutShow('Back to the lobby', 'menuBtn', 'welback');")
# the lesson's plain lobby hides the plate; past the lessons, the plate shows (locked or not)
rep('<p class="ver">Version 241</p>', '<p class="ver">Version 242</p>')
open(DST, 'w').write(s)
print('ui180 ok', n0, '->', len(s))
