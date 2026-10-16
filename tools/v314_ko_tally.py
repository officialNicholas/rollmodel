"""v314: the knock-out bonus in the tally is small, and stays with each side's paint.

- No headline any more ("Knock-out bonus" was as big as the result itself). The paint result stays the story.
- Under the bar, each side gets a small row: "KO" and a star for each of its knock-outs, dim at first. In turn each star fills gold,
  a little "+2%" rises off it, and that side's paint on the bar and its number go up by 2 at once (a small splat where it lands).
  The row ends on the total ("+6%"), and stays there, small, under the bar through to the winner.
- Quicker: about a third of a second a knock-out (was 0.62 s), the two sides taking turns.
- Nothing flies across the screen, and the number keeps no badge: the row under the bar says it all."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def region(s, a, b, new):
    assert s.count(a) == 1, (s.count(a), a[:120]); i = s.index(a); j = s.index(b, i); return s[:i] + new + s[j:]

JS = r"""// (v314) the knock-outs under the bar: a small row for each side, "KO" and a dim star for each of its knock-outs; in turn each star
// fills, a little "+2%" rises off it, and that side's paint and number go up at once (a small splat where it lands). The row ends on
// the total and stays, small, through to the winner
function talKoRows() {
  const box = $('tyKos'); box.innerHTML = ''; box.hidden = false; restartCls(box, 'in');
  for (const e of tal.ppl) {
    const r = document.createElement('span'); r.className = 'tykr ' + e.side; r.style.setProperty('--c', e.col);
    if (!e.kos) { r.classList.add('none'); box.appendChild(r); e.kr = null; continue; }
    let h = '<small>KO</small>'; for (let i = 0; i < e.kos; i++) h += '<i class="tkt">' + KO_SVG + '</i>';
    r.innerHTML = h + '<b class="tkp"></b>'; box.appendChild(r); e.kr = r;
  }
}
function talKoTok(e) {
  e.shown++; e.landed++; AU.tslice(); buzz(8); restartCls(e.nu, 'tick');
  const r = e.kr; if (r) { const t = r.querySelectorAll('.tkt')[e.landed - 1]; if (t) { t.classList.add('on');
      if (!reduceMotion) { const f = document.createElement('i'); f.className = 'tkf'; f.textContent = '+' + KO_PCT + '%'; r.appendChild(f); f.style.left = (t.offsetLeft + t.offsetWidth / 2) + 'px'; setTimeout(() => f.remove(), 700); } }
    const p = r.querySelector('.tkp'); if (p) { p.textContent = '+' + (e.landed * KO_PCT) + '%'; restartCls(p, 'pop'); } }
  tyKoSplat(e, Math.min(1, (e.cov + e.landed * KO_PCT) / tal.scale));
}
// a small splash of the side's paint where its bar grows
function tyKoSplat(e, f) { if (reduceMotion) return; const bar = $('tyBar'), x = e.side === 'l' ? f : e.side === 'r' ? 1 - f : (e.c || 0.5) + f / 2, i = document.createElement('i'); i.className = 'tysplat sm'; i.style.cssText = '--c:' + e.col + ';left:' + (x * 100).toFixed(1) + '%'; bar.parentNode.appendChild(i); i.style.top = (bar.offsetTop + bar.offsetHeight / 2) + 'px'; setTimeout(() => i.remove(), 700); }
"""

CSS = r"""
/* (v314) the knock-outs: a small row under the bar for each side, a star per knock-out, filled as it's counted */
.tykos{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:8px;min-height:22px;margin:7px 6px 0;padding:0 2px}
.tykos.in{animation:fadein .25s ease-out both}
.tykr{position:relative;display:flex;align-items:center;gap:3px;min-width:0;white-space:nowrap}
.tykr.l{grid-column:1;justify-self:start}
.tykr.m{grid-column:2;justify-self:center}
.tykr.r{grid-column:3;justify-self:end;flex-direction:row-reverse}
.tykr small{margin:0 3px;font:800 10.5px/1 var(--font-ui);letter-spacing:.12em;color:#B8B0C8;text-shadow:0 1px 0 rgba(0,0,0,.5)}
.tykr .tkt{display:block;width:15px;height:15px;transition:transform .2s cubic-bezier(.3,1.8,.5,1)}
.tykr .tkt svg{display:block;width:100%;height:100%;fill:rgba(255,255,255,.1);stroke:rgba(255,255,255,.38);stroke-width:1.6px}
.tykr .tkt.on{transform:scale(1.18)}
.tykr .tkt.on svg{fill:var(--gold);stroke:var(--black);filter:drop-shadow(1px 1px 0 var(--black))}
.tykr .tkp{margin:0 4px;font:400 15px/1 var(--font-display);color:var(--gold);text-shadow:1.5px 1.5px 0 var(--black);font-variant-numeric:tabular-nums}
.tykr .tkp:empty{display:none}
.tykr .tkp.pop{animation:tick .22s ease-out}
.tykr .tkf{position:absolute;bottom:100%;margin-left:-14px;width:28px;text-align:center;font:400 12px/1 var(--font-display);color:var(--gold);text-shadow:1px 1px 0 var(--black);pointer-events:none;animation:tkf .65s ease-out forwards}
@keyframes tkf{from{opacity:0;transform:translateY(4px)}25%{opacity:1}to{opacity:0;transform:translateY(-14px)}}
.tysplat.sm{width:34px;height:34px;margin:-17px 0 0 -17px}
@media (max-height:520px) and (min-aspect-ratio:1/1){.tykos{min-height:18px;margin-top:5px}.tykr .tkt{width:13px;height:13px}.tykr .tkp{font-size:13px}}
@media (prefers-reduced-motion:reduce){.tykos.in,.tykr .tkp.pop{animation:none}.tykr .tkt{transition:none}}
"""

def apply(s):
    s = rep(s, '<div class="tybar" id="tyBar" aria-hidden="true"></div>', '<div class="tybar" id="tyBar" aria-hidden="true"></div><div class="tykos" id="tyKos" hidden></div>')
    s = rep(s, "const KO0 = 2.7, KOD = 0.62, KOEND = KO0 + (koq.length ? 0.4 + koq.length * KOD + 0.9 : 0.8); // (v309: a beat for the caption, and each one slow enough to read)",
               "const KO0 = 2.6, KOD = 0.34, KOEND = KO0 + (koq.length ? 0.25 + koq.length * KOD + 0.45 : 0.6); // (v314: quick, and small: the paint's the story)")
    s = rep(s, "talEl.querySelectorAll('.tyfly,.tykofly').forEach(q => q.remove()); $('tyWord').className = 'tyword';",
               "talEl.querySelectorAll('.tyfly,.tykofly').forEach(q => q.remove()); $('tyWord').className = 'tyword'; $('tyKos').innerHTML = ''; $('tyKos').hidden = true;")
    s = rep(s, "  if (t >= tal.KO0 && tal.koq.length && !tal.koCap) { tal.koCap = true; tal.sub0 = $('tySub').innerHTML; const w = $('tyWord'); w.innerHTML = KO_SVG + 'Knock-out bonus'; w.className = 'tyword ko'; restartCls(w, 'in'); $('tySub').innerHTML = '<b>+' + KO_PCT + '%</b> for every knock-out'; AU.pop(); } // (v309: said out loud first)\n"
               "  const nk = t >= tal.KO0 + 0.4 ? clamp(Math.floor((t - tal.KO0 - 0.4) / tal.KOD) + 1, 0, tal.koq.length) : 0;\n"
               "  for (let i = tal.nk; i < nk; i++) talKoFly(tal.koq[i]);\n"
               "  tal.nk = nk;\n"
               "  if (t >= tal.KOEND) for (const e of tal.ppl) while (e.landed < e.shown) talKoLand(e); // (skipped ahead: what's still in the air lands now)\n",
               "  if (t >= tal.KO0 && tal.koq.length && !tal.koRow) { tal.koRow = true; talKoRows(); } // (v314: a small row under the bar, not a headline)\n"
               "  const nk = t >= tal.KO0 + 0.25 ? clamp(Math.floor((t - tal.KO0 - 0.25) / tal.KOD) + 1, 0, tal.koq.length) : 0;\n"
               "  for (let i = tal.nk; i < nk; i++) talKoTok(tal.koq[i]);\n"
               "  tal.nk = nk;\n")
    s = rep(s, "  if (t >= tal.KOEND && tal.phase === 2) { tal.phase = 3; if (tal.koCap) { const w = $('tyWord'); w.textContent = ''; w.className = 'tyword'; $('tySub').innerHTML = tal.sub0 || ''; } talWinner(); }",
               "  if (t >= tal.KOEND && tal.phase === 2) { tal.phase = 3; talWinner(); }")
    s = region(s, "// (v309) each knock-out is seen being added: a star with its +2% pops up over that side's number, flies down into the end of its paint",
               "// a splash of its paint where a slice lands on the bar\nfunction tySplat(e, f) {", JS)
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
