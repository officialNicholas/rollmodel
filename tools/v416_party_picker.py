"""v416: the party's Choose Event, shorter (the user: "the match modes when online is too long. Could we not just see 'vs' and choose
online or with cpu when in a party?"). v413 listed every way to play, in three groups (up to seven cards for two friends). Now there is
one card per event (Versus 1v1, Versus 3-way, Showdown, Showdown 2v2) and a switch on top: Online players | CPUs. Online, each card
finds the missing players online; CPUs, it fills them with CPUs and starts at once. An event that's just your party (a 1v1 for two
friends, a 3-way for three, a Showdown for four) is the same either way: it says "Just you two" and stays. The switch is remembered;
with a game server that offers no CPUs it isn't shown."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """/* (v416) the party's events: one card each, and the Online | CPUs switch above them */
.pywho{grid-column:1/-1;justify-self:center;display:flex;gap:4px;margin:0 0 2px;padding:4px;border-radius:999px;background:rgba(23,19,32,.62);box-shadow:inset 0 0 0 2px rgba(255,255,255,.12)}
.pywho button{appearance:none;display:inline-flex;align-items:center;gap:7px;min-width:132px;justify-content:center;height:38px;margin:0;padding:0 18px;border:0;border-radius:999px;background:transparent;color:#C9C2DC;font:900 14px/1 var(--font-head);letter-spacing:.06em;text-transform:uppercase;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:background .15s,color .15s}
.pywho button[aria-pressed="true"]{background:#FFD24A;color:#171320;box-shadow:0 3px 0 rgba(0,0,0,.35)}
.pywho button svg{width:17px;height:17px}
@media (max-width:359px){.pywho button{min-width:112px;padding:0 12px;font-size:12.5px}}
@media (max-height:520px) and (min-aspect-ratio:1/1){.pywho button{height:32px}}
"""

JS = r"""
// (v416) one card per event; the switch says whether the missing players are found online or are CPUs
const PY_WHO_IC = { online: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.6" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M3.6 12h16.8M12 3.4c2.6 2.6 3.6 5.4 3.6 8.6s-1 6-3.6 8.6c-2.6-2.6-3.6-5.4-3.6-8.6s1-6 3.6-8.6z" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
  cpu: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="7" width="14" height="12" rx="3" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="9.5" cy="12.6" r="1.6" fill="currentColor"/><circle cx="14.5" cy="12.6" r="1.6" fill="currentColor"/><path d="M12 7V3.8M10 16.2h4" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>' };
"""

def apply(s):
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    s = rep(s, "function ptEvRender() {", JS + "function ptEvRender() {")
    old = ("  const ord = (a, b) => ['duo', 'trio', 'ffa', 'duel'].indexOf(a.mode) - ['duo', 'trio', 'ffa', 'duel'].indexOf(b.mode);\n"
           "  const online = p.modes.filter(x => x.plan !== 'private').sort(ord), own = p.modes.filter(x => x.plan === 'private'), cpus = p.modes.filter(x => x.cpus > 0).sort((a, b) => ['trio', 'ffa', 'duo'].indexOf(a.mode) - ['trio', 'ffa', 'duo'].indexOf(b.mode));\n"
           "  const h = (online.length ? '<h3 class=\"pyevh evpy\">With players online</h3>' + online.map(x => card(x, false)).join('') : '') + (cpus.length ? '<h3 class=\"pyevh evpy\">Play now with CPUs</h3>' + cpus.map(x => card(x, true)).join('') : '') + (own.length ? '<h3 class=\"pyevh evpy\">Just your party</h3>' + own.map(x => card(x, false)).join('') : '');\n")
    new = ("  const ord = ['duel', 'trio', 'ffa', 'duo'], canCpu = p.modes.some(x => x.cpus > 0), who = canCpu && store.pyWho === 'cpu' ? 'cpu' : 'online';\n"
           "  // (v416) one card per event: just your party as it is; otherwise found online, or CPUs (with the switch on CPUs, where the event has room for them)\n"
           "  const list = p.modes.slice().sort((a, b) => ord.indexOf(a.mode) - ord.indexOf(b.mode)).map(x => x.plan === 'private' ? card(x, false) : who === 'cpu' ? (x.cpus > 0 ? card(x, true) : '') : card(x, false)).join('');\n"
           "  const sw = canCpu ? '<div class=\"pywho evpy\" role=\"group\" aria-label=\"Who fills the other places\">' + ['online', 'cpu'].map(k => '<button type=\"button\" data-pywho=\"' + k + '\" aria-pressed=\"' + (who === k) + '\">' + PY_WHO_IC[k] + (k === 'cpu' ? 'CPUs' : 'Online') + '</button>').join('') + '</div>' : '';\n"
           "  const h = sw + list;\n")
    s = rep(s, old, new)
    s = rep(s, "$('evGrid').addEventListener('click', e => { const b = e.target.closest('.evpy [data-pyev]'); if (!b || !ptEvOn()) return;",
               "$('evGrid').addEventListener('click', e => { const sw = e.target.closest('.pywho [data-pywho]'); if (sw && ptEvOn()) { AU.init(); AU.ui(); store.pyWho = sw.dataset.pywho; save(); ptEvRender(); return; } // (v416)\n"
               "  const b = e.target.closest('.evpy [data-pyev]'); if (!b || !ptEvOn()) return;")
    # (the switch says CPUs: the titles don't repeat it; the line-up shows each CPU)
    s = rep(s, "frEsc((PY_FULL[x.mode] || x.mode) + (cpu ? ptCpuWith(x.cpus) : ''))", "frEsc(PY_FULL[x.mode] || x.mode)")
    return s
