#!/usr/bin/env python3
"""v209: Play opens Choose Event (Solo; Versus CPU, a 1v1 or a 3-way; Showdown, coming soon; the tutorial, out of Settings). An event
leads on to the canvas vote (the mode tabs gone; the CPU difficulty still there), and the canvases card leaves the home screen. On the
fight card nobody votes any more: a reel of the canvases spins to the right and lands with the one that got the most votes big in the
middle, its votes under it."""
import re, subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui136_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
css = open(S + '/tools/assets/events209.css').read(); js = open(S + '/tools/assets/events209.js').read()
assert '</style>' not in css and '</script>' not in js
# ---- the art: an icon for each event ----
ROLLER = ('<svg viewBox="0 0 64 64"><path d="M40 34v8c0 2-1.5 3-3.5 3H33v13" fill="none" stroke="#171320" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
          '<path d="M40 34v8c0 2-1.5 3-3.5 3H33v13" fill="none" stroke="#C9C2E4" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
          '<rect x="27.5" y="48" width="11" height="13" rx="4" fill="#5B5580" stroke="#171320" stroke-width="3"/>'
          '<rect x="6" y="14" width="40" height="20" rx="8" fill="#FFD84A" stroke="#171320" stroke-width="3.2"/><path d="M11 19h30" stroke="#fff" stroke-width="3" stroke-linecap="round" opacity=".7"/>'
          '<path d="M46 24h4c2 0 3 1 3 3v7h-13" fill="none" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/>'
          '<path d="M12 34v5a3 3 0 0 0 6 0v-5M26 34v8a3 3 0 0 0 6 0v-8" fill="#FFD84A" stroke="#171320" stroke-width="2.6"/></svg>')
VS = ('<svg viewBox="0 0 64 64"><path d="M32 3l7 12 13-4-3 13 12 7-12 7 3 13-13-4-7 12-7-12-13 4 3-13L3 31l12-7-3-13 13 4z" fill="#fff" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/>'
      '<path d="M17 24l5 16 5-16M45 25.5c-1.6-1.6-6-2.2-8 .4-2.4 3 1 5 4 6.4 3.4 1.6 4.4 4.2 1.8 6.6-2.4 2-6.6 1-8.6-.8" fill="none" stroke="#171320" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round"/>'
      '<path d="M17 24l5 16 5-16M45 25.5c-1.6-1.6-6-2.2-8 .4-2.4 3 1 5 4 6.4 3.4 1.6 4.4 4.2 1.8 6.6-2.4 2-6.6 1-8.6-.8" fill="none" stroke="#E3122F" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
SKULL = ('<svg viewBox="0 0 64 64"><path d="M32 6C18 6 9 15.5 9 28c0 7 3 12 8 15v7c0 2.5 2 4 4.5 4h21c2.5 0 4.5-1.5 4.5-4v-7c5-3 8-8 8-15C55 15.5 46 6 32 6z" fill="#fff" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/>'
         '<path d="M18.5 25l8 8M26.5 25l-8 8M37.5 25l8 8M45.5 25l-8 8" stroke="#171320" stroke-width="4.2" stroke-linecap="round"/><path d="M29 41l3-4 3 4z" fill="#171320" stroke="#171320" stroke-width="2" stroke-linejoin="round"/>'
         '<path d="M25 54v-5M32 54v-5M39 54v-5" stroke="#171320" stroke-width="2.8" stroke-linecap="round"/><path d="M16 18a17 17 0 0 1 10-7" fill="none" stroke="#D9D2F0" stroke-width="3" stroke-linecap="round"/></svg>')
CAP = ('<svg viewBox="0 0 64 64"><path d="M32 10 4 22l28 12 28-12z" fill="#2A2437" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/><path d="M14 27v12c0 5 8 9 18 9s18-4 18-9V27l-18 7z" fill="#3C3859" stroke="#171320" stroke-width="3.2" stroke-linejoin="round"/>'
       '<path d="M32 22l20 6v14" fill="none" stroke="#171320" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><path d="M32 22l20 6v14" fill="none" stroke="#FFD84A" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
       '<path d="M48 42h8l-2 9h-4z" fill="#FFD84A" stroke="#171320" stroke-width="2.6" stroke-linejoin="round"/><path d="M14 20 32 13l18 7" fill="none" stroke="#7C76A0" stroke-width="2.4" stroke-linecap="round"/></svg>')
BACK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4.5 7.5 12l7.5 7.5" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
def card(id_, ev, col, icon, title, sub, bar, art_id, extra='', soon=False):
    return (f'<div class="evcard{" soon" if soon else ""}" data-ev="{ev}" style="--ec:{col}"><button class="evmain" id="{id_}" type="button"{extra}><span class="evbar"><i>{bar}</i></span>'
            f'<span class="evtop"><span class="evic" aria-hidden="true">{icon}</span><span class="evtx"><b>{title}</b><small>{sub}</small></span></span>'
            f'<span class="evart" aria-hidden="true"><img id="{art_id}" alt=""></span></button>')
EVENTS = ('    <div class="mevents" id="mEvents" hidden><div class="evwash" aria-hidden="true"><i></i></div>\n'
          '      <div class="evhead"><button class="sback" id="evBack" type="button" aria-label="Back to the lobby">' + BACK + '</button><h2 id="evTitle">Choose event</h2></div>\n'
          '      <div class="evgrid" id="evGrid" role="group" aria-labelledby="evTitle">\n'
          '        ' + card('evSolo', 'solo', '#F29A3A', ROLLER, 'Solo', 'Just you, 60 seconds', 'Beat your best', 'evSoloArt') + '</div>\n'
          '        ' + card('evVs', 'vs', '#E3122F', VS, 'Versus CPU', '1v1 or a 3-way', 'Most paint wins', 'evVsArt', ' aria-expanded="false" aria-controls="evVsPick"') +
          '<div class="evdrop" id="evVsPick" hidden role="group" aria-label="How many rivals"><button type="button" data-m="duel"><b>1 v 1</b><small>You and one rival</small></button>'
          '<button type="button" data-m="trio"><b>3-way</b><small>You and two rivals</small></button></div></div>\n'
          '        ' + card('evShow', 'showdown', '#8E5CFF', SKULL, 'Showdown', 'Last one painting', 'Coming soon', 'evShowArt', ' aria-disabled="true"', soon=True) + '<i class="evsoon">Coming soon</i></div>\n'
          '        ' + card('evTut', 'tut', '#2E9BFF', CAP, 'Tutorial', 'Learn the moves', 'With your coach', 'evTutArt') + '</div>\n'
          '      </div>\n    </div>\n')
rep('    <div class="mworld" id="mWorld" hidden>', EVENTS + '    <div class="mworld" id="mWorld" hidden>')
rep(".comms{display:grid;gap:10px}\n", ".comms{display:grid;gap:10px}\n" + css)
# ---- Play opens the events (the lesson, while it's due, still goes straight in) ----
rep("$('homePlay').addEventListener('click', () => { AU.init(); if (state !== 'menu' || building || lookOpen || shopOpen) return; AU.pop(); start(); });",
    "$('homePlay').addEventListener('click', () => { AU.init(); if (state !== 'menu' || building || lookOpen || shopOpen) return; AU.pop(); if (tutMatchDue()) start(); else openEvents(); });")
rep("  if (menuPage === 'worlds') { menuPage = 'home'; menu.dataset.page = 'home'; $('mWorld').hidden = true; $('mHome').hidden = false; }\n  if (shopOpen) closeShop(true);",
    "  if (menuPage === 'worlds') { menuPage = 'home'; menu.dataset.page = 'home'; $('mWorld').hidden = true; $('mHome').hidden = false; }\n"
    "  if (menuPage === 'events') { menuPage = 'home'; menu.dataset.page = 'home'; evEl.hidden = true; $('mHome').hidden = false; } evFrom = false; document.body.classList.remove('evon');\n  if (shopOpen) closeShop(true);")
# ---- the canvases: what it's for in its title; back goes back to the events ----
rep("  renderModes(); renderStages();\n  centerWorld(worldBtns.find(b => b.dataset.s === stageSel), false); renderWorlds();",
    "  renderModes(); renderStages(); $('worldTitle').textContent = mode === 'solo' ? 'Pick a canvas' : 'Vote for a canvas';\n  centerWorld(worldBtns.find(b => b.dataset.s === stageSel), false); renderWorlds();")
rep("$('worldTitle').textContent = 'Canvases'; $('worldBack').setAttribute('aria-label', 'Back to the title screen');",
    "$('worldTitle').textContent = mode === 'solo' ? 'Pick a canvas' : 'Vote for a canvas'; $('worldBack').setAttribute('aria-label', 'Back');")
rep("  setTimeout(() => $('homePlay').focus({ preventScroll: true }), 30);\n}\n$('gPrev')",
    "  setTimeout(() => $('homePlay').focus({ preventScroll: true }), 30);\n  if (evFrom) { evFrom = false; openEvents(); } // (picked from the events: back to them)\n}\n$('gPrev')")
rep("  if (!(state === 'menu' && menuPage === 'worlds')) renderFrame();", "  if (!(state === 'menu' && (menuPage === 'worlds' || menuPage === 'events'))) renderFrame();")
rep("  if (state === 'menu' && menuPage === 'worlds') { if (k === 'Escape' || k === 'Backspace') { e.preventDefault(); closeWorlds(); return; }",
    "  if (state === 'menu' && menuPage === 'events') { if (k === 'Escape' || k === 'Backspace') { e.preventDefault(); closeEvents(); } return; }\n"
    "  if (state === 'menu' && menuPage === 'worlds') { if (k === 'Escape' || k === 'Backspace') { e.preventDefault(); closeWorlds(); return; }")
# ---- the tutorial lives in the events now, not Settings ----
rep('<div class="sbtns"><button class="sbtn" id="howOpen" type="button" aria-haspopup="dialog"><span>How to play</span></button><button class="sbtn" id="tutReplay" type="button"><span>Replay tutorial</span></button></div>',
    '<div class="sbtns"><button class="sbtn" id="howOpen" type="button" aria-haspopup="dialog"><span>How to play</span></button></div>')
rep("$('tutReplay').addEventListener('click', () => { AU.init(); AU.ui(); store.tut = { ph: 'match' }; save(); closeSettings(); });\n", "")
# (the coach: after the shop and the locker, the real match goes Play, Versus CPU, 1 v 1, then the canvases)
rep("  return tutShow('Time for a real match. Pick a canvas to vote for', 'stageBtn', 'pick');",
    "  if (menuPage === 'events') return $('evVsPick').hidden ? tutShow('Play the CPU: tap *Versus CPU*', 'evVs', 'evvs') : tutShow('Tap *1 v 1*', () => $('evVsPick').querySelector('[data-m=\"duel\"]'), 'ev1v1');\n"
    "  return tutShow('Time for a real match. Tap *Play*', 'homePlay', 'pick');")
rep("    if (menuPage === 'worlds') return tutShow('Back to the lobby', 'worldBack', 'back');\n    return tutShow('You earned dabs. Open the Paint Shop', 'dabsBtn', 'shop');",
    "    if (menuPage === 'worlds') return tutShow('Back to the lobby', 'worldBack', 'back');\n    if (menuPage === 'events') return tutShow('Back to the lobby', 'evBack', 'back');\n    return tutShow('You earned dabs. Open the Paint Shop', 'dabsBtn', 'shop');")
rep("    if (menuPage === 'worlds') return tutShow('Back to the lobby', 'worldBack', 'back');\n    return tutShow('Open your locker to wear your fangs and flower', 'lookBtn', 'locker');",
    "    if (menuPage === 'worlds') return tutShow('Back to the lobby', 'worldBack', 'back');\n    if (menuPage === 'events') return tutShow('Back to the lobby', 'evBack', 'back');\n    return tutShow('Open your locker to wear your fangs and flower', 'lookBtn', 'locker');")
# ---- the vote: no voting on the fight card; a reel spins right and lands on the canvas with the most votes ----
a = s.index('function openVote(id, done) {'); b = s.index('function beginMatch() {', a)
VOTE = r'''function openVote(id, done) {
  const box = $('vvote'), who = [P, H]; if (mode === 'trio') who.push(H2);
  // your vote is the canvas you picked; the rivals' are their own (the lesson: the rival's is a Halloween canvas, and it's the one drawn)
  const votes = new Map(); votes.set(P, VOTE_STAGES.includes(stageSel) ? stageSel : VOTE_STAGES[(Math.random() * VOTE_STAGES.length) | 0]);
  const tutV = tutPh() === 'vote' ? TUT_HALLO[(Math.random() * TUT_HALLO.length) | 0] : null;
  for (const D of who.slice(1)) votes.set(D, tutV && D === H ? tutV : VOTE_STAGES[(Math.random() * VOTE_STAGES.length) | 0]);
  const tally = {}; for (const v of votes.values()) tally[v] = (tally[v] || 0) + 1; const top = Math.max(...Object.values(tally)), lead = Object.keys(tally).filter(k => tally[k] === top);
  const win = tutV || (lead.length === 1 ? lead[0] : lead[(Math.random() * lead.length) | 0]);
  // the reel: the canvases round and round; it spins right, slowing, and stops with the winner in the middle
  const NV = VOTE_STAGES.length, REP = 12, wi = (REP - 5) * NV + VOTE_STAGES.indexOf(win); let h = '';
  for (let r = 0; r < REP; r++) for (const sid of VOTE_STAGES) h += '<span class="vcard" data-s="' + sid + '"><img alt="" src="' + stageArtOf(sid) + '"><b class="vcn">' + escAttr(themeLabel(sid)) + '</b></span>';
  $('vts').innerHTML = '<div class="vreel" id="vreel"><div class="vtrack" id="vtrack">' + h + '</div></div><div class="vtally" id="vtally" aria-live="polite"></div>';
  $('vvLbl').textContent = 'The votes are in'; $('vvWin').textContent = ''; box.classList.remove('ticking', 'done'); box.classList.add('reel'); box.hidden = false; $('vsx').classList.add('voting');
  const st = voteState = { id, votes, open: false, timers: [] };
  const at = (ms, fn) => st.timers.push(setTimeout(() => { if (st !== voteState || id !== runId) return; fn(); }, ms));
  const reel = $('vreel'), track = $('vtrack'), cards = [...track.children];
  const land = () => {
    reel.classList.add('landed'); cards[wi].classList.add('win'); box.classList.add('done'); AU.pop(); buzz([14, 30, 14]);
    $('vvLbl').textContent = 'The canvas is'; $('vvWin').textContent = themeLabel(win);
    const n = tally[win], chips = [...votes].filter(([, v]) => v === win).map(([D]) => '<i style="--c:' + TEAMS[D.team].css + '"></i>').join('');
    $('vtally').innerHTML = '<span class="vchips">' + chips + '</span><b>' + n + (n === 1 ? ' vote' : ' votes') + '</b>';
    at(260, () => { $('vtally').classList.add('on'); AU.say('ready'); });
    at(1900, () => { voteState = null; done(win); });
  };
  requestAnimationFrame(() => { box.classList.add('on'); requestAnimationFrame(() => {
    const w0 = cards[0].offsetWidth, cw = w0 + 10, rw = reel.clientWidth, end = rw / 2 - (wi * cw + w0 / 2), start = end - cw * (NV * 3 + 2), T = reduceMotion ? 0.01 : 3.2, t0 = performance.now(); let last = null;
    track.style.transform = 'translateX(' + start.toFixed(1) + 'px)';
    const ease = u => 1 - Math.pow(1 - u, 3.2);
    const step = now => { if (st !== voteState || id !== runId) return; const u = Math.min(1, (now - t0) / 1000 / T), x = start + (end - start) * ease(u);
      track.style.transform = 'translateX(' + x.toFixed(1) + 'px)'; const ci = Math.round((rw / 2 - x - w0 / 2) / cw); if (ci !== last) { last = ci; if (u < 1 && AU.tick) AU.tick(0); }
      if (u < 1) requestAnimationFrame(step); else land(); };
    at(350, () => requestAnimationFrame(step)); }); });
}
'''
s = s[:a] + VOTE + s[b:]
# ---- the code ----
rep("$('docModal').addEventListener('click', e => { if (e.target === $('docModal')) closeDoc(); });\n",
    "$('docModal').addEventListener('click', e => { if (e.target === $('docModal')) closeDoc(); });\n" + js)
rep('<p class="ver">Version 208</p>', '<p class="ver">Version 209</p>')
open(DST, 'w').write(s)
print('ui137 ok', n0, '->', len(s))
