"""v393: Play online plays a 1v1, a 3-way or a free-for-all Showdown, and finds players near your rank first (the user: "Should allow
for a 1 v 1, 3-way, or free for all showdown. Searching for other players, doesn't have to be same levels, but try to find closer
levels. And if we can't find one, start finding anyone").

- The Online sheet: Versus (most paint wins) with 1 v 1 and 3-way, as Choose Event's Versus CPU has them, and Showdown, the
  free-for-all for up to four. (2v2 stays a party's: a party of two or four picks it.)
- 3-way online: you and two real rivals on one canvas, most paint wins. The game server always had it; the game now plays it (the
  stage's three start spots, the two others as the game's rivals H and H2, the versus card and results for three).
- The search: the game server (v393) looks for players within two ranks of yours first, then five, then ten, then anyone at all
  after 12 seconds; the sheet says how far it has got. The Choose Event card says what Play online has."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

EV_CARDS = r"""function onEvCards() {
  const ic = id => { const e = $(id), i = e && e.querySelector('.evic'); return i ? i.innerHTML : ''; };
  const vs = onModeOn('duel'), tri = onModeOn('trio'), ffa = onModeOn('ffa'), any = vs || tri;
  return '<div class="ongrid">'
    + '<div class="evcard onev' + (any ? ' open' : ' soon') + '" style="--ec:#E3122F"><div class="evmain">'
    + '<span class="evbar"><i>Most paint wins</i></span><span class="evtop"><span class="evic" aria-hidden="true">' + ic('evVs') + '</span><span class="evtx"><b>Versus</b><small>Real rivals, no CPUs</small></span></span><span class="evart" aria-hidden="true"><img data-art="cathedral" alt=""></span></div>'
    + (any ? '<div class="evdrop" role="group" aria-label="How many rivals"><button type="button" data-on="find" data-id="duel" data-f' + (vs ? '' : ' disabled') + ' aria-label="Versus 1 v 1: find one real rival"><b>1 v 1</b><small>One rival</small></button>'
      + '<button type="button" data-on="find" data-id="trio"' + (tri ? '' : ' disabled') + ' aria-label="Versus 3-way: find two real rivals"><b>3-way</b><small>Two rivals</small></button></div>' : '<i class="evsoon">Coming next</i>')
    + '</div>'
    + '<div class="evcard onev' + (ffa ? '' : ' soon') + '" style="--ec:#8E5CFF"><button class="evmain" data-on="find" data-id="ffa" type="button" aria-label="Showdown free-for-all: find a match for up to four"' + (ffa ? '' : ' disabled') + '>'
    + '<span class="evbar"><i>Last one standing</i></span><span class="evtop"><span class="evic" aria-hidden="true">' + ic('evShow') + '</span><span class="evtx"><b>Showdown</b><small>Free-for-all, up to four</small></span></span><span class="evart" aria-hidden="true"><img data-art="manor" alt=""></span></button>'
    + (ffa ? '' : '<i class="evsoon">Coming next</i>') + '</div>'
    + '</div>';
}
"""

def apply(s):
    # the sheet's events: Versus (1 v 1 or 3-way) and Showdown (free-for-all)
    a = s.index('function onEvCards() {'); b = s.index('\nfunction onRender(soft) {', a)
    s = s[:a] + EV_CARDS.rstrip('\n') + s[b:]
    s = rep(s, "// the choice, as Choose Event shows its events: Versus (one real rival: tap it to find one) and Showdown (Free-for-all for up to four,\n// or 2 v 2 with a teammate). A mode the game server doesn't offer yet is greyed and marked Coming next",
               "// the choice, as Choose Event shows its events (v393): Versus, 1 v 1 or a 3-way (most paint wins), and Showdown, the free-for-all\n// for up to four. A mode the game server doesn't offer yet is greyed and marked Coming next")
    # 3-way is one of the server's modes (the party modes are the ones a party can pick)
    s = rep(s, "const onModeOn = m => !!(ON.me ? (ON.me.partyModes || ['duel']).includes(m) : m === 'duel');",
               "const onModeOn = m => !!(ON.me ? (m === 'trio' ? ON.me.modes || [] : ON.me.partyModes || ['duel']).includes(m) : m === 'duel');")
    s = rep(s, "const PY_FULL = { duel: 'Versus', ffa: 'Showdown', duo: 'Showdown 2v2' };", "const PY_FULL = { duel: 'Versus', trio: 'Versus 3-way', ffa: 'Showdown', duo: 'Showdown 2v2' };")
    # the search: you and two to find
    s = rep(s, "const vs = qm === 'duel' ? onVs(me, ON_MYS) : qm === 'duo' ?", "const vs = qm === 'duel' ? onVs(me, ON_MYS) : qm === 'trio' ? '<span class=\"onvs\" aria-hidden=\"true\">' + me + ON_MYS + ON_MYS + '</span>' : qm === 'duo' ?")
    s = rep(s, "// where the search has got to: near you, then further, then everywhere (the server's stages: 4 s, 8 s, 12 s)\nconst onWhere = ms => ms < 4000 ? 'Looking for players near you…' : ms < 8000 ? 'Looking a little further away…' : 'Looking everywhere…';",
               "// where the search has got to: near your rank (and near you), then further, then anyone (the server's stages: 4 s, 8 s, 12 s)\nconst onWhere = ms => ms < 4000 ? 'Looking for players near your rank…' : ms < 8000 ? 'Looking a few ranks further…' : ms < 12000 ? 'Looking everywhere…' : 'Finding anyone who’s free…';")
    s = rep(s, "<p class=\"onhint onnear\">Real people, near you first, then from everywhere. Nobody waits long.</p>",
               "<p class=\"onhint onnear\">Real people, near your rank first, then anyone. Nobody waits long.</p>")
    # the match: three of you on the stage's three start spots, the two others as the game's rivals
    s = rep(s, "const NET_MODES = ['duel', 'ffa', 'duo'];", "const NET_MODES = ['duel', 'trio', 'ffa', 'duo'];")
    s = rep(s, "n > (m.mode === 'duel' ? 2 : 4)", "n > (m.mode === 'duel' ? 2 : m.mode === 'trio' ? 3 : 4)")
    s = rep(s, "const sp = NM.mode === 'duel' ? [START, CSTART] : [START, CSTART, CSTART2, CSTART3];",
               "const sp = NM.mode === 'duel' ? [START, CSTART] : NM.mode === 'trio' ? [START, CSTART, CSTART2] : [START, CSTART, CSTART2, CSTART3];")
    # Choose Event's card says what's in it
    s = rep(s, "<b>Play online</b><small>Versus and Showdown</small>", "<b>Play online</b><small>1v1, 3-way or Showdown</small>")
    s = rep(s, "'Play online: Versus and Showdown against real people'", "'Play online: 1v1, 3-way or Showdown against real people'")
    return s
