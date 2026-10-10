#!/usr/bin/env python3
"""v185: the tally ends with your dabs. A +N dabs pill pops under the bar (win or lose), the coins fly up to a dab bar that fades in at the top
and counts up, then it moves on to the winner screen."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui109_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# markup: the dab bar at the top, the gain pill under the bar
rep('    <div class="tysplash" id="tySplash" aria-hidden="true"></div>\n', '    <div class="tysplash" id="tySplash" aria-hidden="true"></div>\n    <div class="tydabs" id="tyDabs" aria-hidden="true"></div>\n')
rep('      <div class="tybar" id="tyBar" aria-hidden="true"></div>\n      <p class="tytap">Tap to skip</p>', '      <div class="tybar" id="tyBar" aria-hidden="true"></div>\n      <p class="tygain" id="tyGain"></p>\n      <p class="tytap">Tap to skip</p>')
rep(".tytap{position:relative;", ".tydabs{position:absolute;left:50%;top:calc(env(safe-area-inset-top,0px) + 16px);z-index:3;display:flex;align-items:center;gap:8px;padding:7px 16px 7px 9px;border-radius:999px;background:rgba(20,14,30,.88);border:2.5px solid var(--gold);box-shadow:0 4px 0 rgba(0,0,0,.35);color:#fff;font:400 22px/1 var(--font-display);font-variant-numeric:tabular-nums;opacity:0;transform:translate(-50%,-14px);transition:opacity .35s,transform .35s;pointer-events:none}\n"
    ".tydabs.on{opacity:1;transform:translate(-50%,0)}\n.tydabs .dropi{width:26px;height:26px}\n.tydabs.bump b{display:inline-block;animation:tydbump .22s ease-out}\n@keyframes tydbump{50%{transform:scale(1.18)}}\n"
    ".tygain{justify-self:center;display:flex;align-items:center;gap:6px;margin:12px 0 0;padding:6px 14px 6px 10px;border-radius:999px;background:var(--gold);color:#171320;font:400 22px/1 var(--font-display);box-shadow:0 4px 0 rgba(0,0,0,.35);opacity:0;transform:scale(.4);visibility:hidden}\n"
    ".tygain.on{visibility:visible;animation:tygain .45s cubic-bezier(.2,1.6,.4,1) forwards}\n.tygain .dropi{width:24px;height:24px}\n.tygain small{font:800 12px/1 var(--font-ui);letter-spacing:.08em;text-transform:uppercase}\n@keyframes tygain{to{opacity:1;transform:scale(1)}}\n"
    ".tyfly{position:absolute;left:0;top:0;z-index:4;width:24px;height:24px;margin:-12px 0 0 -12px;pointer-events:none;transition:transform .55s cubic-bezier(.45,0,.7,.25),opacity .18s .42s}\n.tyfly .dropi{width:100%;height:100%;display:block}\n"
    ".tytap{position:relative;")
# timeline: the dabs come after the winner is called
rep("tal = { t0: performance.now(), t: 0, ppl, scale, koq, nk: 0, T0: 0.55, T1: 2.3, KO0, KOD, KOEND, END: KOEND + 2.1,",
    "const DAB0 = KOEND + 0.6, DAB1 = DAB0 + 0.7, DAB2 = DAB1 + 1.5; /* (the dabs: the pill, then the coins fly up to the bar and it counts) */\n  tal = { t0: performance.now(), t: 0, ppl, scale, koq, nk: 0, T0: 0.55, T1: 2.3, KO0, KOD, KOEND, DAB0, DAB1, DAB2, END: DAB2 + 0.8,")
rep("talEl.classList.remove('win'); $('tySplash').className = 'tysplash';",
    "talEl.classList.remove('win'); $('tySplash').className = 'tysplash'; $('tyDabs').className = 'tydabs'; $('tyGain').className = 'tygain'; talEl.querySelectorAll('.tyfly').forEach(q => q.remove());")
rep("  if (t >= tal.KOEND && tal.phase === 2) { tal.phase = 3; talWinner(); }\n  if (t >= tal.END) { hideTally(); startVictory(); }",
    "  if (t >= tal.KOEND && tal.phase === 2) { tal.phase = 3; talWinner(); }\n  if (t >= tal.DAB0 && tal.phase === 3) { tal.phase = 4; talDabsShow(); }\n  if (t >= tal.DAB1 && tal.phase === 4) { tal.phase = 5; talDabsFly(); }\n  if (tal.phase === 5) talDabsCount(t);\n  if (t >= tal.END) { hideTally(); startVictory(); }")
rep("function hideTally() {",
"""// what the match paid, win or lose: a pill under the bar, then the coins fly up to your dab bar, which counts up
function talDabsShow() {
  const n = (endInfo && endInfo.drops) || 0; tal.gain = n; tal.from = Math.max(0, (store.drops || 0) - n); tal.shownD = -1;
  const g = $('tyGain'); g.innerHTML = '+' + n + DROP_SVG + '<small>dabs</small>'; restartCls(g, 'on'); AU.pop();
  const d = $('tyDabs'); d.innerHTML = DROP_SVG + '<b>' + tal.from + '</b>'; d.classList.add('on');
}
function talDabsFly() {
  if (reduceMotion || !tal.gain) return; const r0 = talEl.getBoundingClientRect(), g = $('tyGain').getBoundingClientRect(), d = $('tyDabs').querySelector('.dropi').getBoundingClientRect();
  const x0 = g.left + g.width / 2 - r0.left, y0 = g.top + g.height / 2 - r0.top, x1 = d.left + d.width / 2 - r0.left, y1 = d.top + d.height / 2 - r0.top, n = Math.min(12, Math.max(4, Math.round(tal.gain / 6)));
  for (let i = 0; i < n; i++) { const q = document.createElement('i'); q.className = 'tyfly'; q.innerHTML = DROP_SVG; const jx = (Math.random() - 0.5) * 60, jy = (Math.random() - 0.5) * 24;
    q.style.transform = 'translate(' + (x0 + jx).toFixed(0) + 'px,' + (y0 + jy).toFixed(0) + 'px)'; q.style.transitionDelay = (i * 0.07).toFixed(2) + 's,' + (i * 0.07 + 0.42).toFixed(2) + 's'; talEl.appendChild(q);
    requestAnimationFrame(() => requestAnimationFrame(() => { q.style.transform = 'translate(' + x1.toFixed(0) + 'px,' + y1.toFixed(0) + 'px) scale(.7)'; q.style.opacity = '0'; })); setTimeout(() => q.remove(), 1500); }
}
function talDabsCount(t) {
  const k = clamp((t - tal.DAB1 - 0.5) / (tal.DAB2 - tal.DAB1 - 0.5), 0, 1), v = tal.from + Math.round(tal.gain * k);
  if (v !== tal.shownD) { tal.shownD = v; const d = $('tyDabs'); d.querySelector('b').textContent = v; restartCls(d, 'bump'); if (k < 1) AU.ttick(tal.ticks++); else AU.tick(); }
  if (k >= 1) talEl.querySelectorAll('.tyfly').forEach(q => q.remove());
}
function hideTally() {""")
# a tap: past the winner it finishes the count, then moves on
rep("to = t < tal.T1 ? tal.T1 : t < tal.KOEND ? tal.KOEND : tal.END;", "to = t < tal.T1 ? tal.T1 : t < tal.KOEND ? tal.KOEND : t < tal.DAB2 ? tal.DAB2 : tal.END;")
rep('<p class="ver">Version 184</p>', '<p class="ver">Version 185</p>')
open(DST, 'w').write(s)
print('ui110 ok', n0, '->', len(s))
