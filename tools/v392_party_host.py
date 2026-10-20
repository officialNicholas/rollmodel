"""v392: in a party the host picks the event (the user: no mode vote cards; for the friends Play becomes Ready, and they wait for the host;
the host's Play shows the game modes as usual, but only the multiplayer ones: no Time trial, no Versus CPU).

- The lobby's mode vote cards are gone. In their place, between Leave and the reactions, a line says what the party is waiting on:
  "You pick the event" (the host), "@name picks the event" (the others), and once it's picked, the event.
- The friends' big button is Ready: tap it to say you're ready, and again to undo it. Ready, it says it's waiting for the host.
- The host's big button is Play (and says who isn't ready yet). It opens Choose Event with the events this party can play together, as
  cards like the usual ones: Versus (a party of two), Showdown and Showdown 2v2 (just the party, or with players found online). Picking
  one readies the host up: with everyone ready the match starts, otherwise it starts as the last friend readies up (tap Play again to
  cancel).
- The game server (v392) plays the host's pick, and the host picking no longer un-readies the others."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v392) the party: a line on what it's waiting on, where the mode vote was; Choose Event with the party's events alone */
.pynote{justify-self:center;min-width:0;max-width:100%;margin:0;padding:7px 13px 6px;box-sizing:border-box;border-radius:999px;background:rgba(23,19,32,.84);color:#FFF8EA;font:800 12.5px/1.1 var(--font-ui);letter-spacing:.01em;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;box-shadow:0 3px 0 rgba(23,19,32,.22)}
.pynote:empty{visibility:hidden}
.mevents.evparty .evcard:not(.evpy),.mevents:not(.evparty) .evpy{display:none}
"""

JS = r"""
// ---- (v392) the host picks the event: their Play opens Choose Event with the events the party can play together (the
// multiplayer ones, for its size); a pick readies the host up. The others say Ready and wait for it
const PY_EV = { duel: { c: '#E3122F', ic: 'evVs', sub: '1v1' }, ffa: { c: '#8E5CFF', ic: 'evShow', sub: 'Free for all' }, duo: { c: '#2E7BFF', ic: 'evShow', sub: 'Teams of two' } };
function ptHost() { const me = ptMe(), p = ON.party; return !!(me && p && p.leader === me.id); }
function ptTogether() { return 'Your party plays together: ' + (ptHost() ? 'press Play to pick the event' : 'ready up, and the host picks the event'); }
// the line beside the big button: who picks, or what was picked
function ptNote() {
  const p = ON.party, me = ptMe(); if (!p || !me) return '';
  const lead = p.members.find(m => m.id === p.leader);
  if (p.state === 'starting' || p.state === 'queued' || (lead && lead.ready)) return PY_FULL[p.mode] || '';
  return lead && lead.id === me.id ? 'You pick the event' : lead ? hdOf(lead.name) + ' picks the event' : '';
}
// the big button in a party: the host's opens the party's events; anyone else's is Ready (and undoes it); a pick or a start is cancelled
function ptPlayTap() {
  const me = ptMe(), p = ON.party; if (!me || !p || p.state === 'match') return;
  if (p.leader === me.id && !me.ready && p.state === 'idle') {
    if (!p.modes.some(x => x.on)) { AU.nope(); return frToast('<span>No event fits a party this size yet</span>'); }
    AU.pop(); PY.evGo = true; try { openEvents(); } finally { PY.evGo = false; }
    if (menuPage === 'events') setTimeout(() => { const b = evEl.querySelector('.evpy .evmain'); if (b) b.focus({ preventScroll: true }); }, 60);
    return;
  }
  AU.pop(); ptReady();
}
function ptEvOn() { return menuPage === 'events' && evEl.classList.contains('evparty'); }
// the party's event cards (again when the party changes); the page goes once there's nothing for the host to pick
function ptEvRender() {
  if (!ptEvOn()) return;
  const p = ON.party, me = ptMe();
  if (!ptOn() || ON.match || !me || p.leader !== me.id || me.ready || p.state !== 'idle') return closeEvents();
  const n = p.members.length, ic = id => { const e = $(id) && $(id).querySelector('.evic'); return e ? e.innerHTML : ''; };
  const art = { duel: stageArtOf(VOTE_STAGES.includes(stageSel) ? stageSel : 'cathedral'), ffa: stageArtOf('manor'), duo: stageArtOf('crypt') };
  const h = p.modes.map(x => { const d = PY_EV[x.mode] || PY_EV.ffa, own = x.plan === 'private';
    const bar = !x.on ? 'Coming soon' : own ? 'Just your party' : x.mode === 'duo' ? 'Finds a team online' : 'Finds ' + (4 - n) + ' more online';
    const sub = x.mode === 'duel' ? 'You two, 1v1' : x.mode === 'duo' ? (own ? 'Two teams of you' : 'You two vs two') : own ? 'All four of you' : d.sub;
    return '<div class="evcard evpy' + (x.on ? '' : ' soon') + '" data-pyev="' + x.mode + '" style="--ec:' + d.c + '"><button class="evmain" type="button" data-pyev="' + x.mode + '"' + (x.on ? '' : ' aria-disabled="true"') + '>'
      + '<span class="evbar"><i>' + bar + '</i></span><span class="evtop"><span class="evic" aria-hidden="true">' + ic(d.ic) + '</span><span class="evtx"><b>' + frEsc(PY_FULL[x.mode] || x.mode) + '</b><small>' + sub + '</small></span></span>'
      + '<span class="evart" aria-hidden="true"><img alt="" src="' + (art[x.mode] || '') + '"></span></button></div>'; }).join('');
  const g = $('evGrid'); if (g._py === h) return; g._py = h;
  g.querySelectorAll('.evpy').forEach(e => e.remove()); g.insertAdjacentHTML('afterbegin', h);
}
// a pick: the party's event, and the host is ready (the friends who are ready already start it)
async function ptEvPick(m) {
  const p = ON.party, me = ptMe(), x = p && p.modes.find(q => q.mode === m);
  if (!p || !me || !ON.net || p.leader !== me.id || p.state !== 'idle') return closeEvents();
  if (!x || !x.on) { AU.nope(); buzz(8); return frToast('<span>' + (x ? 'Coming soon' : 'Not for a party this size') + '</span>'); }
  AU.pop(); buzz(12); closeEvents();
  try { await ON.net.partyVote(m); await ON.net.partyReady(true); } catch (e) { frToast('<span>' + frEsc(onReqText(e)) + '</span>'); }
}
$('evGrid').addEventListener('click', e => { const b = e.target.closest('.evpy [data-pyev]'); if (!b || !ptEvOn()) return; AU.init(); ptEvPick(b.dataset.pyev); });
"""

def apply(s):
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    # the vote cards go: the line on what the party's waiting on takes their place
    s = rep(s, '<div class="pymodes" id="pyModes" role="radiogroup" aria-label="Vote for a mode"></div>',
               '<p class="pynote" id="pyNote" aria-live="polite"></p>')
    a = s.index("  // the mode vote: the modes that fit the party, each with who voted for it\n  if (inp) {")
    b = s.index("  ptPlay();\n  // the name plates", a)
    s = s[:a] + "  // (v392) what the party's waiting on (the host picks the event)\n  if (inp) { const t = ptNote(), el = $('pyNote'); if (el.textContent !== t) el.textContent = t; }\n" + s[b:]
    s = rep(s, "  ptPlay();\n  // the name plates", "  ptPlay(); ptEvRender();\n  // the name plates")
    # the big button: Play for the host (to pick the event), Ready for everyone else
    s = rep(s, """    const p = ON.party, me = ptMe(), wait = p.members.filter(m => !m.ready).length;
    if (p.state === 'starting') { t = 'Starting'; s = 'Tap to stop'; cls = 'pygo'; }
    else if (p.state === 'queued') { t = 'Finding'; s = 'Tap to cancel'; cls = 'pygo'; }
    else if (me && me.ready) { t = 'Ready!'; s = wait ? 'Waiting for ' + wait + ' · tap to undo' : ''; cls = 'pyready'; }
    else { t = 'Ready'; s = p.mode ? '' : 'No mode for ' + p.members.length + ' yet'; }""",
               """    const p = ON.party, me = ptMe(), wait = p.members.filter(m => !m.ready).length, lead = p.members.find(m => m.id === p.leader), host = !!me && lead === me;
    if (p.state === 'starting') { t = 'Starting'; s = 'Tap to stop'; cls = 'pygo'; }
    else if (p.state === 'queued') { t = 'Finding'; s = 'Tap to cancel'; cls = 'pygo'; }
    else if (host && me.ready) { t = 'Ready!'; s = 'Waiting for ' + wait + ' · tap to cancel'; cls = 'pyready'; }
    else if (host) { const o = wait - 1; t = 'Play'; s = !p.mode ? 'No event for ' + p.members.length + ' yet' : o > 0 ? o + ' not ready yet' : 'Everyone’s ready'; }
    else if (me && me.ready) { t = 'Ready!'; s = (lead && !lead.ready ? 'Waiting for the host' : 'Waiting for ' + wait) + ' · tap to undo'; cls = 'pyready'; }
    else { t = 'Ready'; s = ''; }""")
    s = rep(s, "  if (!p.mode && !me.ready) { AU.nope(); return frToast('<span>None of these modes fit your party yet</span>'); }\n", "")
    s = rep(s, "if (ptOn() && !ON.match) { if (state === 'menu' && !building && !lookOpen && !shopOpen && !lkOn()) { AU.pop(); ptReady(); } return; }",
               "if (ptOn() && !ON.match) { if (state === 'menu' && !building && !lookOpen && !shopOpen && !lkOn()) ptPlayTap(); return; }")
    # Choose Event shows the party's events when the host opens it (and the usual ones any other time)
    s = rep(s, "  menuPage = 'events'; menu.dataset.page = 'events'; $('mHome').hidden = true; evEl.hidden = false;",
               "  menuPage = 'events'; evEl.classList.toggle('evparty', !!PY.evGo); if (PY.evGo) ptEvRender(); menu.dataset.page = 'events'; $('mHome').hidden = true; evEl.hidden = false;")
    s = rep(s, "  setTimeout(() => $('evVs').focus({ preventScroll: true }), 40);\n}\nfunction closeEvents()",
               "  if (!PY.evGo) setTimeout(() => $('evVs').focus({ preventScroll: true }), 40);\n}\nfunction closeEvents()")
    # what the game says about playing as a party
    s = rep(s, "frToast('<span>Your party plays together: vote and ready up in the lobby</span>')", "frToast('<span>' + ptTogether() + '</span>')", 2)
    s = rep(s, "'Your party plays together: vote and ready up in the lobby.'", "ptTogether() + '.'")
    s = rep(s, "frToast('<span>It’s quiet right now. Keep looking, or vote Versus to play each other</span>')",
               "frToast('<span>It’s quiet right now. Keep looking, or ' + (ptHost() ? 'cancel and pick Versus' : 'the host can pick Versus') + ' to play each other</span>')")
    s = rep(s, "// ---------- screen orientation: picked on the first launch", JS.lstrip('\n') + "\n// ---------- screen orientation: picked on the first launch")
    return s
