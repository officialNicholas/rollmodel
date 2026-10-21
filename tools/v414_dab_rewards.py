"""v414: dabs by challenge, and dabs for a rank up (the user: "level ups should give you additional dabs. And when we get these
additional dabs, make sure we do the animation of them floating upwards towards the counter" and "a 1V1 with a CPU that's on hard
should give more than if it was on easy. And you should get the most dabs if you want a free for all on showdown, specially with real
people. Or if you had the CPU on hard. And even more if you also got the most kills ... time trial may not give a lot, but if you're
also getting a lot of the rings ... your amount of dabs go up").

Before, a match paid the same whoever you played: 8 + a third of your paint + 30 for a win (12 a draw) + 10 a new best (+6 in a
3-way); a Showdown 8 + 5 a KO + 30 a win (12 a draw) + 8 for second. Easy and hard CPUs paid alike, online paid like a CPU, rings
paid nothing, and a rank up paid nothing.

Now (docs/dab-rewards.md has the table):
- each mode has a base: Time trial 6, 1v1 8, 3-way 10, 2v2 10, Showdown 12;
- a painting mode adds a third of your paint (35% painted: +12); a KO is +4 (+5 in Showdown), and the most KOs alone +12;
- the place: 1v1 win 30; 3-way 1st 34, 2nd 12; 2v2 win 30; Showdown 1st 40, 2nd 14, 3rd 5; a draw for first 12-16;
- all that times the challenge: CPUs on easy x0.75, medium x1, hard x1.35, online x1.5 (the lessons count as medium);
- Time trial: no challenge factor, but each ring you go through +2, and a new best +10 (as before);
- Jackpot still pays half the match's dabs again on a win.
- a rank up pays 25 + 5 x the new rank (rank 10: 75), on the results as a "Rank N" tag whose dabs fly up to your dabs counter at
  the top (the commissions' coin flight), and from a commission's XP the same, on the commission's own flight.
The results show the reasons under the reputation row, a few short tags ("Hard CPU x1.35", "Most KOs +12", "Rings 8 +16")."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """/* (v414) why the dabs: short tags under the reputation row; a rank up's tag, and its dabs' flight to the counter */
.dabwhy{display:flex;flex-wrap:wrap;justify-content:center;gap:5px;margin:-4px 0 0;padding:0;list-style:none}
.dabwhy[hidden]{display:none}
.dabwhy li{display:inline-flex;align-items:center;gap:4px;padding:4px 8px 3px;border-radius:999px;background:rgba(244,238,227,.12);box-shadow:inset 0 0 0 1.5px rgba(244,238,227,.22);color:#F4EEE3;font:800 11px/1 var(--font-ui);letter-spacing:.02em;white-space:nowrap;animation:fadein .3s 1.4s both}
.dabwhy li b{color:#FFD24A;font-weight:900}
.dabwhy li.down b{color:#C9C2DC}
#repRow .rkdab{position:absolute;left:-6px;top:-30px;z-index:3;display:grid;justify-items:center;gap:1px;padding:6px 12px 5px;border-radius:8px;background:linear-gradient(180deg,#B9F3C8 0%,#46C96B 100%);color:#171320;box-shadow:0 0 0 3px #171320,3px 4px 0 rgba(0,0,0,.4);rotate:-5deg;animation:rkin .45s cubic-bezier(.3,1.6,.5,1) both}
#repRow .rkdab b{font:400 18px/1 var(--font-display);letter-spacing:.04em;text-transform:uppercase}
#repRow .rkdab i{display:inline-flex;align-items:center;gap:3px;font:900 13px/1 var(--font-head);font-style:normal}
#repRow .rkdab i .dropi{width:14px;height:14px}
#repRow .rkdab.out{transition:opacity .4s,transform .4s;opacity:0;transform:translateY(-8px)}
@keyframes rkin{from{opacity:0;transform:scale(.4)}}
#dabFly{position:fixed;inset:0;z-index:70;pointer-events:none}
#dabFly[hidden]{display:none}
#dabFly .cwallet{position:absolute!important;left:max(14px,calc(env(safe-area-inset-left) + 14px));top:max(12px,calc(env(safe-area-inset-top) + 10px));z-index:3;margin:0;pointer-events:none!important;animation:fadein .2s both;transition:opacity .4s}
#dabFly .cwallet.gone{opacity:0}
#dabFly .cwallet .dshop{display:none}
#dabFly .cwallet.cbump .dcoin{animation:cbump .22s ease-out}
#dabFly .cwallet.cbump b,#dabFly .cwallet.cbig b{animation:cbumpn .26s ease-out}
#dabFly .cwallet.cbig .dcoin{animation:cbig .45s cubic-bezier(.3,1.6,.5,1)}
#dabFly .ccoin{position:absolute;left:0;top:0;z-index:4;width:34px;height:34px;pointer-events:none;will-change:transform;filter:drop-shadow(0 2px 0 rgba(23,19,32,.35))}
#dabFly .ccoin svg{display:block;width:100%;height:100%}#dabFly .ccoin .dabk{fill:var(--ink)}
@media (prefers-reduced-motion:reduce){.dabwhy li,#repRow .rkdab{animation:none}}
"""

JS = r"""
// ---------- (v414) a match's dabs, by how hard it was: a base for the mode, the paint, the place, the KOs (the most KOs alone, more), all
// times the challenge (CPUs easy x0.75 .. hard x1.35, people online x1.5); a time trial adds its rings instead. docs/dab-rewards.md ----------
const DAB_BASE = { solo: 6, duel: 8, trio: 10, duo: 10, ffa: 12 };
const DAB_PLACE = { duel: [30], trio: [34, 12], duo: [30], ffa: [40, 14, 5] }; // first, second, third
const DAB_DRAW = { duel: 12, trio: 14, duo: 12, ffa: 16 };
const DAB_X = { easy: 0.75, medium: 1, hard: 1.35, online: 1.5 };
const DAB_MOSTK = 12, DAB_RING = 2, DAB_BEST = 10;
function dabPay(e, o) {
  const m = e.mode, show = m === 'ffa' || m === 'duo', solo = m === 'solo', many = m !== 'duel';
  const who = solo ? '' : NM ? 'online' : tut || tut2 || tut3 ? 'medium' : diff, x = solo ? 1 : DAB_X[who] || 1;
  const myK = solo ? 0 : P.kos | 0, mostK = !solo && myK > 0 && ACTIVE.every(D => D === P || (D.kos | 0) < myK);
  const place = solo ? 0 : o.win === 0 ? 0 : o.place | 0, outcome = solo ? 0 : o.win === 0 ? DAB_DRAW[m] || 0 : (DAB_PLACE[m] || [])[place - 1] || 0;
  const paint = show ? 0 : Math.round((o.cov || 0) * 0.35), kos = (show ? 5 : 4) * myK;
  const core = (DAB_BASE[m] || 8) + paint + outcome + kos + (mostK ? DAB_MOSTK : 0);
  const rings = solo ? DAB_RING * (e.rings | 0) : 0, best = o.newBest ? DAB_BEST : 0, total = Math.round(core * x) + rings + best;
  const why = [];
  if (x !== 1) why.push({ t: who === 'online' ? 'Online' : who[0].toUpperCase() + who.slice(1) + (many ? ' CPUs' : ' CPU'), v: 'x' + x, down: x < 1 });
  if (mostK) why.push({ t: 'Most KOs', v: '+' + DAB_MOSTK });
  if (rings) why.push({ t: 'Rings ' + (e.rings | 0), v: '+' + rings });
  if (myK && !mostK) why.push({ t: 'KOs ' + myK, v: '+' + kos });
  if (best) why.push({ t: 'New best', v: '+' + best });
  e.dabWhy = why.slice(0, 3); return total;
}
// a rank up pays: 25 + 5 x the rank reached, for each one passed
const rankPay = lv => 25 + 5 * lv;
function rankDabs(xp0, xp1) { const a = repOf(xp0).lv, b = repOf(xp1).lv; let n = 0; for (let l = a + 1; l <= b; l++) n += rankPay(l);
  if (n > 0) { store.drops = (store.drops || 0) + n; stEv({ k: 'earn', src: 'rank', n }); save(); } return { n, lv: b }; }
// the reasons, under the reputation row
function dabWhyPaint(info) {
  let el = $('dabWhy'); if (!el) { el = document.createElement('ul'); el.className = 'dabwhy'; el.id = 'dabWhy'; el.setAttribute('aria-label', 'Why these dabs'); $('repRow').insertAdjacentElement('afterend', el); }
  const w = info && info.drops > 0 && !$('repRow').hidden ? info.dabWhy || [] : []; el.hidden = !w.length;
  el.innerHTML = w.map(r => '<li' + (r.down ? ' class="down"' : '') + '>' + r.t + ' <b>' + r.v + '</b></li>').join('');
}
// the rank up's dabs: a tag on the reputation row, and the dabs flying up to your dabs counter (the commissions' flight)
function rkBeat(info) {
  if (!info || !(info.rkDabs > 0) || end.hidden) return; const row = $('repRow');
  for (const x of row.querySelectorAll('.rkdab')) x.remove();
  const tag = document.createElement('span'); tag.className = 'rkdab'; tag.innerHTML = '<b>Rank ' + info.rkLv + '</b><i>+' + info.rkDabs + DROP_SVG + '</i>'; row.appendChild(tag);
  let fly = $('dabFly'); if (!fly) { fly = document.createElement('div'); fly.id = 'dabFly'; fly.setAttribute('aria-hidden', 'true'); document.body.appendChild(fly); }
  for (const o of fly.querySelectorAll('.cwallet,.ccoin')) o.remove(); fly.hidden = false;
  const src = $('dabsBtn'), w = src ? src.cloneNode(true) : document.createElement('span'); for (const el of w.querySelectorAll('[id]')) el.removeAttribute('id');
  w.id = 'dabFlyWallet'; w.removeAttribute('title'); w.tabIndex = -1; w.classList.add('cwallet');
  fly.appendChild(w); // (placed where the lobby's counter sits: top left)
  const to = store.drops || 0, from = Math.max(0, to - info.rkDabs), b = w.querySelector('b'); if (b) b.textContent = String(from);
  setTimeout(() => { if (!tag.isConnected || end.hidden) { fly.hidden = true; return; } AU.xplay('coins', { v: 0.8 }) || AU.power(); hap('success'); commCoins(tag, from, to, 'dabFly');
    setTimeout(() => { tag.classList.add('out'); w.classList.add('gone'); }, 2300); setTimeout(() => { tag.remove(); w.remove(); if (!fly.querySelector('.ccoin')) fly.hidden = true; }, 2800); }, 550);
}
"""

def apply(s):
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    s = rep(s, "// (v404) Jackpot: a win (yours or your team's) pays half as many dabs again; a loss, nothing extra\nfunction jackpotPay(win) {",
               JS + "// (v404) Jackpot: a win (yours or your team's) pays half as many dabs again; a loss, nothing extra\nfunction jackpotPay(win) {")
    # the 1v1, the 3-way and the time trial
    s = rep(s, "  const drops = Math.round(8 + ry * 0.35 + (win > 0 ? 30 : win === 0 && mode !== 'solo' ? 12 : 0) + (newBest ? 10 : 0) + (mode === 'trio' ? 6 : 0)); store.drops = (store.drops || 0) + drops; endInfo.drops = drops; jackpotPay(win);",
               "  const drops = dabPay(endInfo, { cov: ry, win, newBest, place: win > 0 ? 1 : 1 + [rc, mode === 'trio' ? rc2 : -1].filter(v => v > ry).length }); store.drops = (store.drops || 0) + drops; endInfo.drops = drops; jackpotPay(win); // (v414: by the challenge)\n"
               "  { const r = rankDabs(endInfo.xp0, endInfo.xp0 + gain); endInfo.rkDabs = r.n; endInfo.rkLv = r.lv; } // (v414: a rank up pays)")
    # Showdown
    s = rep(s, "  const drops = Math.round(8 + 5 * P.kos + (win > 0 ? 30 : win === 0 ? 12 : 0) + (pl === 2 ? 8 : 0)); store.drops = (store.drops || 0) + drops; endInfo.drops = drops; jackpotPay(win);",
               "  const drops = dabPay(endInfo, { win, place: pl }); store.drops = (store.drops || 0) + drops; endInfo.drops = drops; jackpotPay(win); // (v414: by the challenge)\n"
               "  { const r = rankDabs(endInfo.xp0, endInfo.xp0 + gain); endInfo.rkDabs = r.n; endInfo.rkLv = r.lv; } // (v414: a rank up pays)")
    # the results: the reasons, and the rank up's dabs when the rank pops
    s = rep(s, "  const dg = $('dropGain'); dg.hidden = !(info.drops > 0); if (info.drops > 0) dg.innerHTML = '+' + info.drops + DROP_SVG + '<small>dabs</small>';",
               "  const dg = $('dropGain'); dg.hidden = !(info.drops > 0); if (info.drops > 0) dg.innerHTML = '+' + info.drops + DROP_SVG + '<small>dabs</small>'; dabWhyPaint(info); for (const x of row.querySelectorAll('.rkdab')) x.remove(); // (v414)")
    s = rep(s, "  if (!info || !(info.xp > 0)) { row.hidden = true; $('commDone').innerHTML = ''; return; }",
               "  if (!info || !(info.xp > 0)) { row.hidden = true; $('commDone').innerHTML = ''; if ($('dabWhy')) $('dabWhy').hidden = true; return; }")
    s = rep(s, "AU.fanfare(); AU.say('levelup'); }", "AU.fanfare(); AU.say('levelup'); rkBeat(info); }")
    # the tally's counter counts the match's dabs; the rank up's come after, on their own flight
    s = rep(s, "tal.from = Math.max(0, (store.drops || 0) - n);", "tal.from = Math.max(0, (store.drops || 0) - n - ((endInfo && endInfo.rkDabs) || 0));")
    # a commission's XP that reaches a rank: its dabs ride the commission's own flight
    s = rep(s, "c.claimed.push(id); const from = store.drops || 0; store.drops = from + COMM_DABS; stEv({ k: 'earn', src: 'comm', n: COMM_DABS }); store.xp = (store.xp || 0) + COMM_XP; save();",
               "c.claimed.push(id); const from = store.drops || 0; store.drops = from + COMM_DABS; stEv({ k: 'earn', src: 'comm', n: COMM_DABS }); store.xp = (store.xp || 0) + COMM_XP; save();\n"
               "  { const rk = rankDabs(store.xp - COMM_XP, store.xp); if (rk.n > 0) setTimeout(() => frToast('<span>Rank ' + rk.lv + '! <b>+' + rk.n + ' dabs</b></span>'), 900); } // (v414: a rank up pays, on the same flight)")
    return s
