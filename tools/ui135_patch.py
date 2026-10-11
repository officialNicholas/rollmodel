#!/usr/bin/env python3
"""v208, the lobby: How to play leaves the lobby's rail for Settings (a row there opens the guide, and closing it comes back to Settings);
the Commissions plate shows when the day's set turns over, a green ring round its clipboard draining through the day and a tag under it
counting down (hours and minutes, then minutes and seconds in the last hour), and the Commissions card says it too."""
import re, subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui134_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- How to play: off the rail, into Settings ----
m = re.findall(r'\n        <button class="plate" id="howBtn"[^\n]*</button>', s); assert len(m) == 1
s = s.replace(m[0], '')
rep("#howBtn{justify-self:start}\n", "")
rep(".menu.tutoring #commBtn,.menu.tutoring #howBtn{display:none}", ".menu.tutoring #commBtn{display:none}")
# (one Help row: the guide and the tutorial side by side, so Settings keeps its four rows on a short wide screen)
rep("""      <div class="sgrp">
        <p class="lhead">Tutorial</p>
        <button class="btn sm" id="tutReplay" type="button">Replay the tutorial</button>""", """      <div class="sgrp">
        <p class="lhead">Help</p>
        <div class="seg duo" role="group" aria-label="Help"><button type="button" id="howOpen" aria-haspopup="dialog">How to play</button><button type="button" id="tutReplay">Replay tutorial</button></div>""")
rep("function closeHow() { if (howModal.hidden) return; howModal.hidden = true; $('howBtn').focus({ preventScroll: true }); }",
    "function closeHow() { if (howModal.hidden) return; howModal.hidden = true; if (state === 'menu') { setModal.hidden = false; $('howOpen').focus({ preventScroll: true }); } } // (it's opened from Settings: back there)")
rep("$('howBtn').addEventListener('click', uiClick(openHow));",
    "$('howOpen').addEventListener('click', uiClick(() => { if (state !== 'menu') return; setModal.hidden = true; openHow(); }));")
# ---- Commissions: the refresh ring and countdown ----
rep('<button class="plate" id="commBtn" type="button" aria-haspopup="dialog"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4.5" y="4"',
    '<button class="plate" id="commBtn" type="button" aria-haspopup="dialog"><span class="cring" aria-hidden="true"><svg class="cring-r" viewBox="0 0 44 44"><circle class="t" cx="22" cy="22" r="19"/><circle class="a" id="commArc" cx="22" cy="22" r="19" pathLength="100" stroke-dasharray="100 100" transform="rotate(-90 22 22)"/></svg><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4.5" y="4"')
rep('stroke-linejoin="round"/></svg><span>Commissions</span><i class="pbadge" id="commBadge" hidden></i></button>',
    'stroke-linejoin="round"/></svg></span><span>Commissions</span><i class="pbadge" id="commBadge" hidden></i><b class="ctimer" id="commTimer" aria-hidden="true"></b></button>')
rep('<p class="cnote small">Three jobs at a time, fresh every day. Each one pays XP and dabs, and a new one comes in.</p>',
    '<p class="cnote small">Three jobs at a time, fresh every day. Each one pays XP and dabs, and a new one comes in.</p>\n      <p class="cnext">Fresh set in <b id="commNext"></b></p>')
rep(".comms{display:grid;gap:10px}", """.comms{display:grid;gap:10px}
/* when the day's commissions turn over: a ring round the plate's clipboard that drains through the day, a tag under the plate counting down */
.plate .cring{position:relative;display:grid;place-items:center;width:40px;height:40px;margin:-4px 0 -2px}
.plate .cring svg{width:21px;height:21px}
.plate .cring svg.cring-r{position:absolute;inset:0;width:100%;height:100%;overflow:visible}
.cring-r circle{fill:none;stroke-width:4.2}
.cring-r .t{stroke:rgba(23,19,32,.13)}
.cring-r .a{stroke:#2DBE60;stroke-linecap:round;transition:stroke-dasharray .8s ease}
#commBtn{padding-bottom:13px}
.plate .ctimer{position:absolute;left:50%;bottom:-9px;transform:translateX(-50%);padding:3px 6px 2px;text-transform:none;border-radius:999px;background:#171320;color:#F4EEE3;font:900 10px/1 var(--font-head);font-style:normal;font-variant-numeric:tabular-nums;letter-spacing:.01em;white-space:nowrap;box-shadow:0 2px 0 rgba(23,19,32,.22)}
.plate .ctimer:empty{display:none}
.cnext{margin:-2px 0 2px;justify-self:center;display:inline-flex;align-items:center;gap:7px;font:800 12px/1 var(--font-ui);color:var(--muted)}
.cnext b{padding:4px 8px 3px;border-radius:999px;background:#171320;color:#F4EEE3;font:900 11px/1 var(--font-head);font-variant-numeric:tabular-nums;letter-spacing:.01em}
.cnext b:empty{display:none}
@media (max-height:520px) and (min-aspect-ratio:1/1){#commModal .cnote.small{display:none}} /* (a short wide screen: the countdown in place of the note) */""")
rep("$('commModal').addEventListener('click', e => { if (e.target === $('commModal')) closeComms(); });",
    """$('commModal').addEventListener('click', e => { if (e.target === $('commModal')) closeComms(); });
// when the commissions turn over (midnight, when the day's set is replaced): the ring on the plate drains through the day and the tag counts
// down to it, hours and minutes, then minutes and seconds in the last hour
const commLeft = () => { const n = new Date(); return Math.max(0, new Date(n.getFullYear(), n.getMonth(), n.getDate() + 1) - n); };
const commFmt = ms => { const s = Math.ceil(ms / 1000), h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), p = v => String(v).padStart(2, '0'); return h ? p(h) + 'h' + p(m) + 'm' : p(m) + 'm' + p(s % 60) + 's'; };
let commDay = '', commTxt = '';
function commTick() {
  const ms = commLeft(), txt = commFmt(ms);
  if (txt !== commTxt) { commTxt = txt; $('commTimer').textContent = txt; $('commNext').textContent = txt; $('commArc').setAttribute('stroke-dasharray', (100 * ms / 864e5).toFixed(2) + ' 100');
    const h = Math.floor(ms / 36e5), mi = Math.floor(ms % 36e5 / 6e4); $('commBtn').setAttribute('aria-label', 'Commissions. A fresh set in ' + (h ? h + ' h ' : '') + mi + ' min'); }
  const day = new Date().toDateString(); if (day !== commDay) { const first = !commDay; commDay = day; if (!first && state === 'menu') { renderLobbyUI(); if (!$('commModal').hidden) renderComms(); } } // (a new day: the new set)
}
commTick(); setInterval(() => { if (state === 'menu' && !document.hidden) commTick(); }, 1000);""")
open(DST, 'w').write(s)
print('ui135 ok', n0, '->', len(s))
