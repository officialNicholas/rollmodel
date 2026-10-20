"""v410: commissions, all done (the user: "All three commissions are completed, but the ring doesn't show as completed. Also, if all
three is completed ... a stamp on it that says done for the day ... simplify the page now so it doesn't have the three banners and
just let the user know that it's all done").
- The ring on the lobby's Commissions plate is the day's jobs now (each job's share, part-done ones in part), not the time left: all
  three done, it's a full green ring, and a green DONE stamp sits on the plate. The countdown tag under it stays.
- The panel, every job done and claimed: no cards, a big "Done for the day" stamp (it thumps down the first time you see it, or the
  moment you claim the last one), a line under it, and the fresh-set countdown. A finished job you haven't claimed yet still shows its
  card and its Claim button until you do."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

CSS = """/* (v410) commissions all done: the panel's stamp, and the plate's full ring and DONE stamp */
#commModal .card.alldone>.cnote.small{display:none}
.cdone{display:grid;justify-items:center;gap:12px;padding:14px 0 8px}
.cstampbig{display:inline-flex;flex-direction:column;align-items:center;gap:4px;padding:14px 22px 12px;border:4px solid #1C9E4B;border-radius:12px;color:#1C9E4B;font:900 30px/1 var(--font-head);letter-spacing:.03em;text-transform:uppercase;text-align:center;rotate:-6deg;box-shadow:inset 0 0 0 3px #F6F1E6,inset 0 0 0 5px #1C9E4B;background:rgba(45,190,96,.08);mix-blend-mode:multiply}
.cstampbig svg{width:34px;height:34px}
.cstampbig small{font:900 13px/1 var(--font-head);letter-spacing:.14em;opacity:.85}
.cdone.thump .cstampbig{animation:cthump .5s cubic-bezier(.2,1.5,.4,1) both}
@keyframes cthump{0%{opacity:0;transform:scale(2.2)}55%{opacity:1;transform:scale(.94)}100%{opacity:1;transform:scale(1)}}
.cdone .cnote{margin:0;max-width:300px}
@media (prefers-reduced-motion:reduce){.cdone.thump .cstampbig{animation:none}}
#commBtn .cdst{position:absolute;z-index:3;top:4px;right:2px;display:none;padding:3px 5px 2px;border:2px solid #1C9E4B;border-radius:5px;background:#F6F1E6;color:#1C9E4B;font:900 10px/1 var(--font-head);letter-spacing:.08em;rotate:12deg;box-shadow:0 2px 0 rgba(23,19,32,.18);pointer-events:none}
#commBtn.alldone:not(.locked) .cdst{display:block}
"""

JS = """
// (v410) the day's jobs done: each job's share (part-done ones in part) for the plate's ring; all done and claimed for the panel's stamp
function commFrac() { const c = commState(); if (!c.active.length) return 0; let f = 0; for (const id of c.active) { const k = COMMS.find(x => x.id === id); f += c.done.includes(id) ? 1 : k ? Math.min(1, (c.prog[id] || 0) / k.n) : 0; } return f / c.active.length; }
const commAllDone = () => { const c = commState(); return c.active.length > 0 && c.active.every(id => c.done.includes(id)); };
function commRingPaint() { const f = commFrac(), b = $('commBtn'); $('commArc').setAttribute('stroke-dasharray', (100 * f).toFixed(2) + ' 100'); b.classList.toggle('alldone', f >= 1);
  if (!b.querySelector('.cdst')) { const st = document.createElement('i'); st.className = 'cdst'; st.setAttribute('aria-hidden', 'true'); st.textContent = 'Done'; b.appendChild(st); } }
"""

def apply(s):
    s = rep(s, "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n",
               "@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}\n" + CSS)
    # the panel: all done and claimed, the stamp in place of the cards
    s = rep(s, "  $('commList').innerHTML = cards + (!cards || c.active.every(id => c.done.includes(id)) ? note : ''); }",
               "  const all = c.active.length > 0 && c.active.every(id => c.done.includes(id) && c.claimed.includes(id)); $('commModal').querySelector('.card').classList.toggle('alldone', all);\n"
               "  if (all) { const thump = store.commStamp !== c.day; if (thump) { store.commStamp = c.day; save(); } // (v410: done for the day; it thumps down once a day)\n"
               "    $('commList').innerHTML = '<div class=\"cdone' + (thump ? ' thump' : '') + '\"><b class=\"cstampbig\" role=\"img\" aria-label=\"Done for the day\">' + COMM_CHECK + 'Done for the day<small>All three commissions</small></b><p class=\"cnote\">The critics are speechless. A fresh set of jobs comes in when the clock runs out.</p></div>';\n"
               "    if (thump && !reduceMotion) setTimeout(() => { if (!$('commModal').hidden) { AU.xplay('ribbon', { v: 0.7 }) || AU.pop(); hap('success'); } }, 260); commRingPaint(); return; }\n"
               "  $('commList').innerHTML = cards + (!cards || c.active.every(id => c.done.includes(id)) ? note : ''); commRingPaint(); }")
    s = rep(s, "function renderComms() {", JS + "function renderComms() {")
    # the last claim: the cards go and the stamp comes down
    s = rep(s, "  setTimeout(() => { if (card.isConnected) { card.classList.remove('claim'); card.classList.add('got'); btn.remove(); } }, 1350); // (the button folds away; the card is a finished one)\n}",
               "  setTimeout(() => { if (card.isConnected) { card.classList.remove('claim'); card.classList.add('got'); btn.remove(); } }, 1350); // (the button folds away; the card is a finished one)\n"
               "  if (c.active.every(k => c.claimed.includes(k))) setTimeout(() => { if (!$('commModal').hidden) renderComms(); }, 1700); // (v410: that was the last: done for the day)\n}")
    # the plate's ring: the day's jobs, not the clock
    s = rep(s, "$('commNext').textContent = txt; $('commArc').setAttribute('stroke-dasharray', (100 * ms / 864e5).toFixed(2) + ' 100');",
               "$('commNext').textContent = txt; commRingPaint();")
    s = rep(s, "function commBadgePaint() { const n = commsDue() ? commUnclaimed().length : 0, b = $('commBadge');",
               "function commBadgePaint() { commRingPaint(); const n = commsDue() ? commUnclaimed().length : 0, b = $('commBadge');")
    return s
