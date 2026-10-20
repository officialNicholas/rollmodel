"""v414: commissions for online play, and the week's board from a Time trial's results.
- Online commissions (the user: "Create a couple commissions based on online play. But simple stuff"): Go online (play a match
  online), Online win (win a match online) and Party up (play an online match in a party). They come into the day's set only once
  Play online is open to you (rank 2 and the Strokes page seen, as Play online itself), and Party up only once you have a friend, so
  nobody gets a job they can't do. Same reward as the others. (And Harsh critics no longer finishes on a Time trial: a Time trial
  always ends happy, so with the CPU set to harsh it used to count as a win against it.)
- The board (the user: "There should be a quick way to see a leaderboard in the results page after doing a time trial"): the results
  of a Time trial have a See the board button under the week's rows, and the results sheet after them a Board button between
  Rematch and Menu. Either opens this canvas's weekly leaderboard (the same one as the lobby's strip) with this run marked Latest;
  closing it goes back to the results."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

TROPHY = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3.5h10v5.2a5 5 0 0 1-10 0z" fill="currentColor"/><path d="M7 5.2H4.3v1.6a3.6 3.6 0 0 0 3.4 3.6M17 5.2h2.7v1.6a3.6 3.6 0 0 1-3.4 3.6" '
          'fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/><path d="M12 13.7v3.6M8.2 20.5h7.6M9.4 17.3h5.2v3.2H9.4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')

CSS = """/* (v414) a Time trial's results: the week's board, one tap away */
#victory .vttb{appearance:none;align-self:flex-start;display:inline-flex;align-items:center;gap:7px;margin:8px 0 2px;padding:7px 12px 6px 10px;border:1.5px solid rgba(245,240,232,.34);border-radius:999px;background:rgba(245,240,232,.07);color:var(--vbone);font:800 12px/1 var(--font-ui);letter-spacing:.1em;text-transform:uppercase;cursor:pointer;animation:vup .45s 1.5s cubic-bezier(.2,.9,.25,1) both;-webkit-tap-highlight-color:transparent}
#victory .vttb svg{width:16px;height:16px;color:var(--vc-hi)}
#victory .vttb i{font-style:normal;opacity:.6}
#victory .vttb:active{transform:translateY(1px);background:rgba(245,240,232,.14)}
#victory .vttb:focus-visible{outline:2px solid var(--vc-hi);outline-offset:2px}
#victory.land .vttb{margin-top:6px;padding:6px 11px 5px 9px}
#end .row #endTT{display:inline-flex;align-items:center;justify-content:center;gap:6px}
#end .row #endTT[hidden]{display:none}
#end .row #endTT svg{flex:none;width:17px;height:17px;color:#C8901E}
#end .row .btn{min-width:0}
@media (max-width:379px){#end .row #endTT{flex:0 0 54px;padding-left:0;padding-right:0}#end .row #endTT .ettx{display:none}#end .row #endTT svg{width:20px;height:20px}}
"""

COMM_JS = """
// (v414) online jobs: only offered once Play online is open (and Party up once you have a friend), so nobody gets one they can't do
const commFrHas = () => { try { return !!((FR.box && FR.box.friends && FR.box.friends.length) || store.frHad); } catch (e) { return !!store.frHad; } };
const commCan = x => { if (!x.on) return true; try { return !!NET_URL && mpOpen() && (x.k !== 'party' || commFrHas()); } catch (e) { return false; } };
"""

def apply(s):
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    # the online commissions
    s = rep(s, ", { id: 'hard1', t: 'Harsh critics', d: 'Win with the CPU on harsh', n: 1, k: 'hard' }];",
               ", { id: 'hard1', t: 'Harsh critics', d: 'Win with the CPU on harsh', n: 1, k: 'hard' },\n"
               "  { id: 'online1', t: 'Go online', d: 'Play a match online', n: 1, k: 'online', on: 1 }, { id: 'onwin1', t: 'Online win', d: 'Win a match online', n: 1, k: 'onwin', on: 1 }, { id: 'party1', t: 'Party up', d: 'Play an online match in a party', n: 1, k: 'party', on: 1 }]; // (v414: the last three online)" + COMM_JS)
    s = rep(s, "while (c.active.length < 3) { const pool = COMMS.filter(x => !c.active.includes(x.id) && !c.done.includes(x.id));",
               "while (c.active.length < 3) { const pool = COMMS.filter(x => !c.active.includes(x.id) && !c.done.includes(x.id) && commCan(x));")
    s = rep(s, "function commProgress(info) {\n  const c = commState(), fin = [];",
               "function commProgress(info) {\n  const c = commState(), fin = [], online = info.diff === 'online', party = online && (() => { try { return !!(ON.party && ON.party.members.length > 1); } catch (e) { return false; } })();")
    s = rep(s, "else if (k.k === 'hard' && info.diff === 'hard' && info.win > 0) p = 1;",
               "else if (k.k === 'hard' && info.diff === 'hard' && info.mode !== 'solo' && info.win > 0) p = 1;\n"
               "    else if (k.k === 'online' && online) p = 1; else if (k.k === 'onwin' && online && info.win > 0) p = 1; else if (k.k === 'party' && party) p = 1; /* (v414) */")
    # remembered: you have a friend (the list may not be in yet when the day's set is picked)
    s = rep(s, "const b = await frInbox(); FR.box = b;",
               "const b = await frInbox(); FR.box = b; { const had = b && b.friends && b.friends.length ? 1 : 0; if ((store.frHad || 0) !== had) { store.frHad = had; save(); } } /* (v414) */")
    # the victory screen: See the board, under the week's rows
    s = rep(s, "+ '<span class=\"vn\">' + escAttr(ttWhen(r.t)) + (r.t === hi ? '<em>This run</em>' : '') + '</span><b class=\"vp\">' + r.p + '<small>%</small></b></div>').join(''); }",
               "+ '<span class=\"vn\">' + escAttr(ttWhen(r.t)) + (r.t === hi ? '<em>This run</em>' : '') + '</span><b class=\"vp\">' + r.p + '<small>%</small></b></div>').join('')\n"
               "    + '<button class=\"vttb\" type=\"button\" aria-label=\"This week’s leaderboard for this canvas\">" + TROPHY + "See the board<i>›</i></button>'; } // (v414)\n"
               "$('vCards').addEventListener('click', e => { const b = e.target.closest('.vttb'); if (!b) return; e.stopPropagation(); AU.init(); const i = endInfo || {}; if (i.sid) openTT(i.sid, i.tt && i.tt.t); });")
    # the results sheet: Board, between Rematch and Menu (a Time trial's only)
    s = rep(s, '<button class="btn" id="replayBtn" type="button">Rematch</button><button class="btn" id="menuBtn" type="button">Menu</button>',
               '<button class="btn" id="replayBtn" type="button">Rematch</button><button class="btn" id="endTT" type="button" hidden aria-label="This week’s leaderboard for this canvas">' + TROPHY + '<span class="ettx">Board</span></button><button class="btn" id="menuBtn" type="button">Menu</button>')
    s = rep(s, "  end.dataset.next = ''; $('replayBtn').hidden = false;",
               "  end.dataset.next = ''; $('replayBtn').hidden = false; $('endTT').hidden = !(solo && info.sid); /* (v414) */")
    s = rep(s, "$('replayBtn').addEventListener('click', uiClick(replay));",
               "$('replayBtn').addEventListener('click', uiClick(replay));\n$('endTT').addEventListener('click', () => { AU.init(); const i = endInfo || {}; if (i.sid) openTT(i.sid, i.tt && i.tt.t); }); /* (v414) */")
    # online results: no board
    s = rep(s, "  $('replayBtn').hidden = true; $('replayBtn').closest('.row').hidden = false;",
               "  $('replayBtn').hidden = true; $('endTT').hidden = true; $('replayBtn').closest('.row').hidden = false;")
    return s
