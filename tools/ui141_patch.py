#!/usr/bin/env python3
"""v213: Abilities, a square of violet construction paper on the lobby rail where How to play used to be (cut by hand, a little crooked,
taped down at two corners; art/m_cpaper.webp from tools/mk_cpaper.py). Locked until rank 3, and past that, coming soon: a tap says which.
Your rank now survives a reload (the loader was clearing xp). Commissions are a set of three for the day: a finished one stays on the board with a Completed stripe across it, and nothing is dealt in
its place until the fresh set at midnight."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui140_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# ---- Abilities ----
BOLT = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.2 1.6 4.4 13.7h6.5l-1.2 8.7 9.9-12.6h-6.6l1.2-8.2z" fill="#F2C14E"/>'
        '<path d="M14.2 1.6 4.4 13.7h2.1l7.1-8.9z" fill="#FFE39A"/><path d="M20.6 3.2l.5 1.4 1.4.5-1.4.5-.5 1.4-.5-1.4-1.4-.5 1.4-.5z" fill="#FFF6E4"/></svg>')
rep('<i class="pbadge" id="commBadge" hidden></i><b class="ctimer" id="commTimer" aria-hidden="true"></b></button>\n',
    '<i class="pbadge" id="commBadge" hidden></i><b class="ctimer" id="commTimer" aria-hidden="true"></b></button>\n'
    '        <button class="plate abil locked" id="abilBtn" type="button" aria-label="Abilities, locked until rank 3"><span class="abpaper" aria-hidden="true"></span><span class="abart" aria-hidden="true">' + BOLT + '</span><span>Abilities</span><b class="abtag" id="abilTag" aria-hidden="true"></b></button>\n')
rep(".menu.tutoring #commBtn{display:none}", ".menu.tutoring #commBtn,.menu.tutoring #abilBtn{display:none}")
CSS = """
/* abilities: violet construction paper, cut by hand, set crooked and taped down at two corners; locked until rank 3, then coming soon */
.plate.abil{width:70px;min-height:76px;padding:14px 4px 13px;align-content:center;border-radius:0;background:none;box-shadow:none;color:#FFF6E4;text-shadow:0 1px 0 rgba(23,19,32,.5);transform:rotate(-4deg);animation:abilidle 4.6s -.8s ease-in-out infinite}
.plate.abil .abpaper{position:absolute;inset:0;z-index:-1;background:url(art/m_cpaper.webp) center/100% 100% no-repeat;filter:drop-shadow(2px 3px 0 rgba(23,19,32,.22))} /* (the shadow on a layer of its own: a filter on the button would clip the note that pops out of it) */
.plate.abil::before{left:-11px;top:-1px;width:38px;height:14px;margin:0;background:url(art/m_tape1.webp) center/100% 100% no-repeat;transform:rotate(-41deg)}
.plate.abil::after{content:"";position:absolute;right:-12px;bottom:5px;width:38px;height:14px;background:url(art/m_tape2.webp) center/100% 100% no-repeat;transform:rotate(-40deg);pointer-events:none}
.plate.abil .abart{display:grid;place-items:center;transform:rotate(9deg)}
.plate.abil .abart svg{width:31px;height:31px;filter:drop-shadow(0 1.5px 0 rgba(23,19,32,.4))}
.plate.abil.locked .abart{opacity:.6;filter:saturate(.35)}
.plate.abil .abtag{position:absolute;z-index:2;left:50%;bottom:-9px;display:flex;align-items:center;gap:3px;padding:3px 6px 2px;border-radius:999px;background:#171320;color:#F4EEE3;font:900 10px/1 var(--font-head);font-style:normal;letter-spacing:.02em;white-space:nowrap;text-shadow:none;transform:translateX(-50%) rotate(4deg);box-shadow:0 2px 0 rgba(23,19,32,.25)}
.plate.abil .abtag svg{width:9px;height:9px;color:var(--gold)}
.plate.abil:not(.locked) .abtag{background:var(--gold);color:#171320;letter-spacing:.08em}
.plate.abil:active{animation:none;transform:rotate(-4deg) translate(1px,2px)}
.plate.abil:active .abpaper{filter:drop-shadow(1px 1px 0 rgba(23,19,32,.22))}
@media (hover:hover){.plate.abil:hover{animation:none;transform:rotate(-4deg) translateY(-2px)}}
.plate.abil.abnudge .abtag{animation:abnudge .45s ease}
.lcol.abup{z-index:4}
.abtoast{position:absolute;left:calc(100% + 14px);top:50%;z-index:6;padding:8px 12px 7px;border-radius:8px;background:#171320;color:#fff;font:800 12.5px/1.2 var(--font-ui);text-transform:none;text-shadow:none;letter-spacing:0;white-space:nowrap;box-shadow:0 0 0 2px var(--gold);transform:translateY(-50%) rotate(4deg);animation:abtoast 1.9s ease both;pointer-events:none}
.abtoast::before{content:"";position:absolute;left:-7px;top:50%;margin-top:-6px;border:6px solid transparent;border-left:0;border-right:7px solid var(--gold)}
@keyframes abilidle{0%,100%{transform:rotate(-4deg)}50%{transform:rotate(-3.3deg) translateY(-1px)}}
@keyframes abnudge{0%,100%{transform:translateX(-50%) rotate(4deg)}25%{transform:translateX(-58%) rotate(-4deg)}60%{transform:translateX(-44%) rotate(9deg)}}
@keyframes abtoast{0%{opacity:0;transform:translate(-8px,-50%) rotate(4deg)}10%,82%{opacity:1;transform:translate(0,-50%) rotate(4deg)}100%{opacity:0;transform:translate(4px,-50%) rotate(4deg)}}
@media (prefers-reduced-motion:reduce){.plate.abil{animation:none}.abtoast{animation-duration:2.4s}}
"""
rep("@keyframes plateidle{0%,100%{transform:rotate(0)}50%{transform:rotate(.6deg) translateY(-1px)}}\n",
    "@keyframes plateidle{0%,100%{transform:rotate(0)}50%{transform:rotate(.6deg) translateY(-1px)}}\n" + CSS.lstrip('\n'))
LOCK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.5 10.5V7.8a4.5 4.5 0 0 1 9 0v2.7" fill="none" stroke="currentColor" stroke-width="3"/><rect x="4.5" y="10" width="15" height="12" rx="2.6" fill="currentColor"/></svg>'
JS = """
// abilities: on the rail, locked until rank 3; past that, coming soon (a tap says which)
const ABIL_RANK = 3, ABIL_LOCK = '""" + LOCK + """';
function paintAbil() { const b = $('abilBtn'), on = repOf(store.xp || 0).lv >= ABIL_RANK; b.classList.toggle('locked', !on); $('abilTag').innerHTML = on ? 'Soon' : ABIL_LOCK + 'Rank ' + ABIL_RANK; b.setAttribute('aria-label', on ? 'Abilities, coming soon' : 'Abilities, locked until rank ' + ABIL_RANK); }
let abilT = 0;
$('abilBtn').addEventListener('click', () => { AU.init(); AU.nope(); const b = $('abilBtn'), rail = b.parentElement, on = !b.classList.contains('locked'), old = b.querySelector('.abtoast'); if (old) old.remove();
  const t = document.createElement('span'); t.className = 'abtoast'; t.setAttribute('role', 'status'); t.textContent = on ? 'Abilities are coming soon' : 'Reach rank ' + ABIL_RANK + ' to unlock Abilities'; b.appendChild(t); kick(b, 'abnudge');
  rail.classList.add('abup'); clearTimeout(abilT); abilT = setTimeout(() => { t.remove(); rail.classList.remove('abup'); }, 2000); }); // (the rail lifts over the spots beside you while its note shows)
"""
rep("$('commModal').addEventListener('click', e => { if (e.target === $('commModal')) closeComms(); });\n",
    "$('commModal').addEventListener('click', e => { if (e.target === $('commModal')) closeComms(); });\n" + JS.lstrip('\n'))
rep("function renderLobbyUI() {\n  const r = repOf(store.xp || 0);", "function renderLobbyUI() {\n  paintAbil(); const r = repOf(store.xp || 0);")

# ---- your rank survives a reload: the loader still cleared xp, a leftover from an old daily streak, so the rank went back to 1 every time ----
rep("for (const k of ['xp', 'daily', 'lastDay', 'dayStreak', 'streak', 'bestStreak']) delete d[k];", "for (const k of ['daily', 'lastDay', 'dayStreak', 'streak', 'bestStreak']) delete d[k]; // (xp is the rank's now, and is kept)")

# ---- commissions: the day's three stay put; a finished one is striped, not replaced ----
rep("for (const id of c.active) { const k = COMMS.find(x => x.id === id); if (!k) continue; let p = c.prog[id] || 0;",
    "for (const id of c.active) { const k = COMMS.find(x => x.id === id); if (!k || c.done.includes(id)) continue; let p = c.prog[id] || 0;")
rep("for (const k of fin) { c.active = c.active.filter(x => x !== k.id); c.done.push(k.id); delete c.prog[k.id]; }",
    "for (const k of fin) { c.done.push(k.id); delete c.prog[k.id]; } // (it keeps its place in the day's set, striped)")
OLD_R = s[s.index("function renderComms() {"):s.index("\n", s.index("function renderComms() {"))]
assert "Every commission done. The critics are speechless." in OLD_R
rep(OLD_R, """function renderComms() { const c = commState(), seen = store.commSeen || 0, note = '<p class="cnote">Every commission done. The critics are speechless.</p>';
  const cards = c.active.map(id => { const k = COMMS.find(x => x.id === id), di = c.done.indexOf(id), fin = di >= 0, p = fin ? k.n : c.prog[id] || 0;
    return '<div class="comm' + (fin ? ' fin' + (di >= seen ? ' fresh' : '') : '') + '" style="--p:' + Math.round(100 * p / k.n) + '"><div class="ring" data-n="' + p + '/' + k.n + '"></div><div class="ct"><b>' + k.t + '</b><small>' + k.d + '</small></div><b class="cr"><span>+' + COMM_XP + ' XP</span><span>+' + COMM_DABS + DROP_SVG + '</span></b>' + (fin ? '<i class="cstripe"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 12.5l4.6 4.6L19.5 6.7" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>Completed</i>' : '') + '</div>'; }).join('');
  $('commList').innerHTML = cards + (!cards || c.active.every(id => c.done.includes(id)) ? note : ''); }""")
rep('<p class="cnote small">Three jobs at a time, fresh every day. Each one pays XP and dabs, and a new one comes in.</p>',
    '<p class="cnote small">Three jobs a day. Each one pays XP and dabs once.</p>')
CSS2 = """.comm{position:relative}
.comm.fin{background:#F4F1EA}
.comm.fin>.ct,.comm.fin>.cr{opacity:.55;filter:grayscale(.6)}
.comm.fin .ring{background:#2DBE60}
.comm.fin .ring::after{color:#1C7A3D}
.comm .cstripe{position:absolute;left:-8px;right:-8px;top:66%;display:flex;align-items:center;justify-content:center;gap:7px;padding:5px 0 4px;background:#2DBE60;color:#fff;font:900 13px/1 var(--font-head);font-style:normal;letter-spacing:.26em;text-transform:uppercase;text-shadow:0 1.5px 0 rgba(23,19,32,.35);border-block:2.5px solid var(--black);box-shadow:0 3px 0 rgba(23,19,32,.22);transform:translateY(-50%) rotate(-3deg);pointer-events:none}
.comm .cstripe svg{width:14px;height:14px;flex:none;filter:drop-shadow(0 1.5px 0 rgba(23,19,32,.35))}
.comm.fresh .cstripe{animation:cstripe .5s .25s cubic-bezier(.3,1.3,.5,1) both}
@keyframes cstripe{from{clip-path:inset(0 100% 0 0);transform:translateY(-50%) rotate(-3deg) scale(1.12)}to{clip-path:inset(0 0 0 0)}}
@media (prefers-reduced-motion:reduce){.comm.fresh .cstripe{animation:none}}
"""
rep(".comm.done{background:var(--gold)}\n.comm.done .cr{color:var(--black)}\n", CSS2)
rep('<p class="ver">Version 212</p>', '<p class="ver">Version 213</p>')
open(DST, 'w').write(s)
print('ui141 ok', n0, '->', len(s))
