"""v394: a party plays against people online too, and the host's events say plainly who plays (the user: "the two of you in a party.
You should be able to play against other online people too. Maybe you two play on a team against another team. Or you play free for
all, or are finding an additional to play 3way. Look at these online modes. Make selecting intuitive").

- The host's Choose Event, in a party, in two groups: With players online (the game server finds the rest) and Just your party.
  Two friends: Showdown 2v2 (you two as a team against a team found online), Versus 3-way (you two and one more), Showdown (you two and
  two more, each for their own), and Versus between the two of you. Three: a 3-way of your own, or a Showdown with one more. Four: a
  Showdown or a 2v2 of your own.
- Each card shows the line-up where its picture was: your face (ringed), your friends' faces, a ? for each player to be found, and a
  "vs" between the sides. So a team shows as you two together against two ?s, a free-for-all as each of you on your own.
- The 3-way for a party is new on the game server (v394): it offers it only when everyone in the party has this version or later of
  the game, which says so when it connects (client rm-394)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = r"""
/* (v394) the party's events: two groups, and each card's line-up (faces, a ? for each player to be found, vs between the sides) */
.pyevh{grid-column:1/-1;display:flex;align-items:center;gap:10px;margin:2px 2px -10px;font:800 12px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#C9C2DC}
.pyevh::after{content:"";flex:1;height:2px;border-radius:2px;background:rgba(255,255,255,.14)}
.pyevh+.pyevh,.evcard+.pyevh{margin-top:8px}
html.fh .pyevh{display:none}
.evart.pyart img{filter:brightness(.42) saturate(.85)}
.pyline{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:7px;transform:skewX(5deg);pointer-events:none}
.pyside{display:flex;align-items:center;padding:4px;border-radius:999px;background:rgba(23,19,32,.74);box-shadow:0 0 0 2px rgba(255,255,255,.16)}
.pyside>*+*{margin-left:-7px}
.pyf{display:grid;place-items:center;flex:none;border-radius:50%;background:#171320}
.pyf .frface{width:40px;height:40px}
.pyf.me{box-shadow:0 0 0 2.5px #FFD24A;z-index:1}
.pyline .onmys{width:38px;height:38px;color:#fff;opacity:.9;background:rgba(255,255,255,.08);font-size:18px}
.pyvs{font:400 15px/1 var(--font-display);font-style:normal;text-transform:uppercase;color:#FFD24A;text-shadow:0 2px 0 #171320,1.2px 0 0 #171320,-1.2px 0 0 #171320}
@media (max-height:520px) and (min-aspect-ratio:1/1){.pyf .frface{width:34px;height:34px}.pyline .onmys{width:32px;height:32px;font-size:15px}.pyside{padding:3px}}
"""

JS = r"""const PY_EV = { duel: { c: '#E3122F', ic: 'evVs', art: 'cathedral' }, trio: { c: '#D6336C', ic: 'evVs', art: 'raft' }, ffa: { c: '#8E5CFF', ic: 'evShow', art: 'manor' }, duo: { c: '#2E7BFF', ic: 'evShow', art: 'crypt' } };
const PY_NEED = { duel: 2, trio: 3, ffa: 4, duo: 4 };
// (v394) who plays, as each card shows it: the sides, each a list of the party's members (you first) and '?' for a player to be found
function ptEvSides(x, mem) {
  const Q = '?', find = k => Array.from({ length: Math.max(0, k) }, () => Q);
  if (x.mode === 'duo') return x.plan === 'private' ? [mem.slice(0, 2), mem.slice(2, 4)] : [mem.slice(0, 2), find(2)];
  return mem.concat(find(PY_NEED[x.mode] - mem.length)).map(e => [e]);
}
// what each card says: the strip above it, the line under its name, and its whole meaning for a screen reader
function ptEvWords(x, n) {
  const own = x.plan === 'private', more = PY_NEED[x.mode] - n, name = PY_FULL[x.mode] || x.mode;
  const bar = !x.on ? 'Coming soon' : own ? 'Just you ' + (['', '', 'two', 'three', 'four'][n] || 'all') : x.mode === 'duo' ? 'Finds a team online' : 'Finds ' + more + ' more online';
  const sub = x.mode === 'duel' || x.mode === 'trio' ? 'Most paint wins' : x.mode === 'ffa' ? 'Last one standing' : own ? 'Two teams, picked fair' : 'You two on one team';
  const say = name + ': ' + (x.mode === 'duo' ? (own ? 'two teams of your party' : 'you two as a team against a team found online')
    : (own ? 'just your party' : 'your party and ' + more + (more === 1 ? ' player' : ' players') + ' found online') + (x.mode === 'duel' ? ', one against one' : ', each for their own'));
  return { bar, sub, say };
}
// the party's event cards (again when the party changes), in two groups: with players online, then just your party. The page goes
// once there's nothing for the host to pick
function ptEvRender() {
  if (!ptEvOn()) return;
  const p = ON.party, me = ptMe();
  if (!ptOn() || ON.match || !me || p.leader !== me.id || me.ready || p.state !== 'idle') return closeEvents();
  const n = p.members.length, mem = [me].concat(p.members.filter(m => m !== me)), ic = id => { const e = $(id) && $(id).querySelector('.evic'); return e ? e.innerHTML : ''; };
  const face = e => e === '?' ? ON_MYS : '<span class="pyf' + (e === me ? ' me' : '') + '">' + frFace(e.look) + '</span>';
  const card = x => { const d = PY_EV[x.mode] || PY_EV.ffa, w = ptEvWords(x, n), art = stageArtOf(x.mode === 'duel' && VOTE_STAGES.includes(stageSel) ? stageSel : d.art);
    const line = ptEvSides(x, mem).map(s => '<span class="pyside">' + s.map(face).join('') + '</span>').join('<i class="pyvs">vs</i>');
    return '<div class="evcard evpy' + (x.on ? '' : ' soon') + '" data-pyev="' + x.mode + '" style="--ec:' + d.c + '"><button class="evmain" type="button" data-pyev="' + x.mode + '" aria-label="' + frEsc(w.say) + '"' + (x.on ? '' : ' aria-disabled="true"') + '>'
      + '<span class="evbar"><i>' + w.bar + '</i></span><span class="evtop"><span class="evic" aria-hidden="true">' + ic(d.ic) + '</span><span class="evtx"><b>' + frEsc(PY_FULL[x.mode] || x.mode) + '</b><small>' + w.sub + '</small></span></span>'
      + '<span class="evart pyart" aria-hidden="true"><img alt="" src="' + (art || '') + '"><span class="pyline">' + line + '</span></span></button></div>'; };
  const ord = (a, b) => ['duo', 'trio', 'ffa', 'duel'].indexOf(a.mode) - ['duo', 'trio', 'ffa', 'duel'].indexOf(b.mode);
  const online = p.modes.filter(x => x.plan !== 'private').sort(ord), own = p.modes.filter(x => x.plan === 'private');
  const h = (online.length ? '<h3 class="pyevh evpy">With players online</h3>' + online.map(card).join('') : '') + (own.length ? '<h3 class="pyevh evpy">Just your party</h3>' + own.map(card).join('') : '');
  const g = $('evGrid'); if (g._py === h) return; g._py = h;
  g.querySelectorAll('.evpy').forEach(e => e.remove()); g.insertAdjacentHTML('afterbegin', h);
}"""

def apply(s):
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    # the party's events: grouped, each with its line-up
    a = s.index("const PY_EV = { duel: { c: '#E3122F', ic: 'evVs', sub: '1v1' }")
    b = s.index("\n", a)
    s = s[:a] + JS.split('\n')[0] + "\nconst PY_NEED = { duel: 2, trio: 3, ffa: 4, duo: 4 };" + s[b:]
    a = s.index("// the party's event cards (again when the party changes); the page goes once there's nothing for the host to pick\nfunction ptEvRender() {")
    b = s.index("\n}\n", a) + 3
    rest = JS[JS.index("// (v394) who plays"):]
    s = s[:a] + rest + "\n" + s[b:]
    # this game plays the 3-way in a party: it says so to the game server
    s = rep(s, "token: store.netTok || null, client: 'rm-391',", "token: store.netTok || null, client: 'rm-394',")
    return s
