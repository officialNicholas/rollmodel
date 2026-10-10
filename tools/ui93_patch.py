#!/usr/bin/env python3
"""Onboarding. A new player's first match is a lesson on the blank canvas: a coach's tips with the game slowed down while one is up, the rival keeping away until the pound is taught, the roller, the orb (always the rocket, and only yours) and the flower turning up as they come up. After it the coach points to the shop (the flower at half the match's dabs, the fangs for what is left), the locker to wear them, and the canvases to vote, where the rival's Halloween vote is the one drawn. Settings can replay it. On top of ui92_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui92_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
CSS = open(S + '/tools/assets/tutorial.css').read()
JS = open(S + '/tools/assets/tutorial.js').read()
# ---- markup: the coach plate and the slow-down frame; a Settings row to replay ----
rep('<div class="hint" id="hint" aria-live="polite"><span id="hintText"></span></div>',
    '<div class="hint" id="hint" aria-live="polite"><span id="hintText"></span></div>\n  <div class="tutslow" id="tutSlow" aria-hidden="true"></div><div class="tutdim" id="tutDim" aria-hidden="true"></div><div class="tut" id="tut" hidden data-pos="top" role="status" aria-live="polite"><div class="tplate"><b class="tname">Coach</b><span class="tava" id="tutAva" aria-hidden="true"></span><span class="ttext" id="tutText"></span></div><p class="tcall" id="tutCall"></p><i class="thand" aria-hidden="true"><svg viewBox="0 0 64 84"><g fill="#F2C08A" stroke="#171320" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"><path d="M18 16c0-8 6-13 14-13h13c9 0 16 7 16 16v15c0 10-7 18-16 20H30c-6 0-10-3-12-9z"/><path d="M45 19c7-2 12 3 10 9M45 31c7-2 12 3 10 9M43 43c6-2 10 3 8 8" fill="none"/><path d="M18 16v53c0 6 4 11 9.5 11S37 75 37 69V34"/></g><ellipse cx="27.5" cy="71" rx="5" ry="4" fill="#E39A66"/></svg></i></div>')
rep('      </div>\n      <button class="btn play sm" id="setDone" type="button">Done</button>',
    '      <div class="sgrp">\n        <p class="lhead">Tutorial</p>\n        <button class="btn sm" id="tutReplay" type="button">Replay the tutorial</button>\n      </div>\n      </div>\n      <button class="btn play sm" id="setDone" type="button">Done</button>')
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + CSS + s[j:]
# ---- the clock: slowed while a lesson waits; the lesson's own step; the plate placed each frame ----
rep("else if (slow > 0) { slow -= rdt; dt = rdt * 0.35; }", "else if (slow > 0) { slow -= rdt; dt = rdt * 0.35; }\n  if (tut && tut.slowK < 1 && state === 'play') dt *= tut.slowK; // (the lesson: slowed right down while a tip waits on you)")
rep("blobContact(); updateOrb(dt); updateShots(dt);", "blobContact(); updateOrb(dt); updateShots(dt); if (tut) tutStep(dt);")
rep("  if (kof) kofFrame(rdt);\n", "  if (kof) kofFrame(rdt);\n  tutFrame(rdt);\n")
# ---- during the lesson: no one-time tips, no pound button until it is taught, no pick-ups until they are, the orb only yours and always the rocket ----
rep("function hint(id, text, dur) { if (store.seen[id] || hintTimer > 0.4) return;", "function hint(id, text, dur) { if (tut || store.seen[id] || hintTimer > 0.4) return;")
rep("const b = $('slamBtn'), show = state === 'play' && (P.st === 'play' || P.st === 'hide');", "const b = $('slamBtn'), show = state === 'play' && (P.st === 'play' || P.st === 'hide') && !(tut && tut.hidePound);")
rep("if (itemSpawn.t <= 0 && powers.length < cap", "if (itemSpawn.t <= 0 && !(tut && !tut.items) && powers.length < cap")
rep("for (const D of ACTIVE) { if (D.st !== 'play' || D.giantT > 0 || D.rocket || D.turret) continue; const h = Math.hypot(D.x - orb.x, D.z - orb.z), dy = orb.base - D.y;",
    "for (const D of ACTIVE) { if (D.st !== 'play' || D.giantT > 0 || D.rocket || D.turret || (tut && tut.orbMine && D !== P)) continue; const h = Math.hypot(D.x - orb.x, D.z - orb.z), dy = orb.base - D.y;")
rep("const gift = window.__orbKind || ['giant', 'rocket'][(Math.random() * 2) | 0];", "const gift = tut ? 'rocket' : window.__orbKind || ['giant', 'rocket'][(Math.random() * 2) | 0];")
# ---- the rival keeps its distance until the pound is taught ----
rep("  for (const p of pots) if (potUp(p) && p.ink > 0.02 && !p.occ) NAV.near(p.x, p.z, p.y, 1.15, n => { nMult[n.id] += 3; });\n",
    "  for (const p of pots) if (potUp(p) && p.ink > 0.02 && !p.occ) NAV.near(p.x, p.z, p.y, 1.15, n => { nMult[n.id] += 3; });\n  if (tut && tut.keepAway) NAV.near(O.x, O.z, O.y, 12, n => { nMult[n.id] += 9; }); // (the lesson: it stays out of your way)\n")
rep("if (D.st === 'ko') { ai.path = null; ai.plan = null; ai.flight = null; ai.evadeT = 0; ai.attackT = 0; ai.wasRdy = false; return; }",
    "if (D.st === 'ko') { ai.path = null; ai.plan = null; ai.flight = null; ai.evadeT = 0; ai.attackT = 0; ai.wasRdy = false; return; }\n  if (tut && tut.keepAway) ai.attackT = 0; if (tut && tut.drive === D && D.st === 'play' && !D.rocket && !D.turret) return tutDrive(D); // (the lesson: kept away, or driven at you for the dodge)")
# ---- the lesson match: no vote, its own reveal line, its own setup; the lobby put back after ----
rep("if (mode === 'solo' || window.__noVote) {", "if (mode === 'solo' || window.__noVote || tutMatchDue()) {")
rep("$('rvSub').textContent = (MODES.find(", "$('rvSub').textContent = tutMatchDue() ? 'Tutorial \\u00b7 learn the ropes' : (MODES.find(")
rep("giftPlan(); newItem = null;", "giftPlan(); newItem = null; tutBegin();")
rep("  if (shopOpen) closeShop(true); if (lookOpen) closeLook();\n  if (!mapUsed && GEN.key !== mapKey()) mapUsed = true;", "  if (shopOpen) closeShop(true); if (lookOpen) closeLook();\n  tutPrep();\n  if (!mapUsed && GEN.key !== mapKey()) mapUsed = true;")
rep("function showMenu() {\n  clearShot();", "function showMenu() {\n  tutLeave(); clearShot();")
rep("store.drops = (store.drops || 0) + drops; endInfo.drops = drops;\n  save();", "store.drops = (store.drops || 0) + drops; endInfo.drops = drops;\n  save(); tutEndMatch();")
# ---- the vote lesson: the rival votes a Halloween canvas, and that is the one drawn ----
rep("  who.slice(1).forEach((D, i) => at(1700 + i * 900 + Math.random() * 600, () => { votes.set(D, VOTE_STAGES[(Math.random() * VOTE_STAGES.length) | 0]); draw(); AU.plop(); }));",
    "  const tutV = tutPh() === 'vote' ? TUT_HALLO[(Math.random() * TUT_HALLO.length) | 0] : null; // (the lesson: the rival's vote is a Halloween canvas, and it is the one drawn)\n  who.slice(1).forEach((D, i) => at(1700 + i * 900 + Math.random() * 600, () => { votes.set(D, tutV && D === H ? tutV : VOTE_STAGES[(Math.random() * VOTE_STAGES.length) | 0]); draw(); AU.plop(); }));")
rep("const tickets = [...votes.values()], win = tickets[(Math.random() * tickets.length) | 0],", "const tickets = [...votes.values()], win = tutV || tickets[(Math.random() * tickets.length) | 0],")
# ---- the shop lesson's prices ----
rep("const PRICE = w => PRICES[w.id] || (w.season ? 1000 : w.slot === 'head' ? 600 : 300);",
    "const PRICE = w => { const t = store.tut && store.tut.price; if (t && t[w.id] >= 0) return t[w.id]; return PRICES[w.id] || (w.season ? 1000 : w.slot === 'head' ? 600 : 300); }; // (the lesson sets the flower's and the fangs' prices)")
# ---- the lesson's finish screen ----
rep('<section class="newitem" id="newItem" hidden', '<section class="tutwin" id="tutWin" hidden aria-labelledby="twTitle"><i class="twdark" aria-hidden="true"></i><i class="twrim" aria-hidden="true"></i><h2 class="twtitle" id="twTitle"><b>Basics</b><br><b class="g">Complete</b></h2><div class="twpanel"><div><p>Congratulations, you have learned the basics</p><ul id="twList"></ul></div></div><button class="btn play sm" id="twNext" type="button">Next</button></section>\n  <section class="newitem" id="newItem" hidden')
rep("function startTally() {\n  if (state !== 'dead' || vic || tal) return;", "function startTally() {\n  if (tutWinDue && state === 'dead' && !vic && !tal) { tutWinDue = false; return showTutWin(); } // (the lesson's own finish first; Next brings the tally)\n  if (state !== 'dead' || vic || tal) return;")
# ---- the module ----
rep("applyOrient(); showMenu();", JS + "applyOrient(); showMenu();")
rep('<p class="ver">Version 162</p>', '<p class="ver">Version 163</p>')
open(DST, 'w').write(s)
subprocess.run(['python3', '-I', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
print('ui93 ok', n0, '->', len(s))
