#!/usr/bin/env python3
"""The tally: after the buzzer a screen counts up everyone's paint, then adds each elimination on top (worth a slice of the canvas), then shows the winner. Eliminations now count toward who wins. On top of ui44_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui44_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# the screen
rep('  <section class="victory" id="victory" hidden aria-live="polite">',
    '''  <section class="tally" id="tally" hidden aria-live="polite">
    <div class="tyhead"><b class="tyword" id="tyWord">Paint</b><span class="tysub" id="tySub"></span></div>
    <div class="tyrows" id="tyRows" role="list"></div>
    <p class="tytap">Tap to skip</p>
  </section>
  <section class="victory" id="victory" hidden aria-live="polite">''')

# what one elimination is worth
rep("const NAMES = ['You', 'Smudge', 'Doodle'], nameOf = D => D === P ? playerName() : NAMES[D.team];",
    "const NAMES = ['You', 'Smudge', 'Doodle'], nameOf = D => D === P ? playerName() : NAMES[D.team];\nconst KO_PCT = 2; // each elimination counts for this much of the canvas at the tally")

# the winner: paint plus eliminations
rep("  const rest = mode === 'trio' ? Math.max(rc, rc2) : rc, win = mode === 'solo' ? 1 : ry > rest ? 1 : rest > ry ? -1 : 0, winner = win > 0 ? P : win < 0 ? (mode === 'trio' && rc2 > rc ? H2 : H) : null;",
    "  const kos = [P.kos | 0, H.kos | 0, mode === 'trio' ? H2.kos | 0 : 0], tot = [ry + kos[0] * KO_PCT, rc + kos[1] * KO_PCT, mode === 'trio' ? rc2 + kos[2] * KO_PCT : 0], sy = tot[0], sc = tot[1], sc2 = tot[2];\n  const rest = mode === 'trio' ? Math.max(sc, sc2) : sc, win = mode === 'solo' ? 1 : sy > rest ? 1 : rest > sy ? -1 : 0, winner = win > 0 ? P : win < 0 ? (mode === 'trio' && sc2 > sc ? H2 : H) : null;")
rep("  endInfo = { you, cpu, cpu2, win, winner, time: runT, mode };", "  endInfo = { you, cpu, cpu2, win, winner, time: runT, mode, kos, tot };")
rep("  setTimeout(() => { if (id !== runId || state !== 'dead') return; startVictory(); }, 1450);\n}",
    "  setTimeout(() => { if (id !== runId || state !== 'dead') return; startTally(); }, 1450);\n}")

# the winner screen and the results board read the totals
rep("  const info = endInfo, solo = info.mode === 'solo', board = ACTIVE.map(D => ({ D, pct: Math.round(teamCov(D.team)) })).sort((a, b) => b.pct - a.pct);",
    "  const info = endInfo, solo = info.mode === 'solo', board = ACTIVE.map(D => ({ D, pct: solo ? Math.round(info.you) : info.tot[D.team] })).sort((a, b) => b.pct - a.pct);")
rep("  else { const tie = board.find(e => e.D !== P && e.pct === Math.round(info.you)); feat = tie ? [P, tie.D] : [P]; }",
    "  else { const tie = board.find(e => e.D !== P && e.pct === info.tot[0]); feat = tie ? [P, tie.D] : [P]; }")
rep("vicName(nameOf(lead)); $('vSub').innerHTML = '<b>' + board[0].pct + '%</b> of the canvas'; }",
    "vicName(nameOf(lead)); $('vSub').innerHTML = '<b>' + board[0].pct + '%</b>' + (info.kos[lead.team] ? ' with ' + info.kos[lead.team] + (info.kos[lead.team] === 1 ? ' elimination' : ' eliminations') : ' of the canvas'); }")
rep("  const ppl = (solo ? [P] : trio ? [P, H, H2] : [P, H]).map(D => ({ D, pct: Math.round(covOf(D)), kos: D.kos || 0 }));",
    "  const ppl = (solo ? [P] : trio ? [P, H, H2] : [P, H]).map(D => ({ D, pct: solo ? Math.round(covOf(D)) : info.tot[D.team], kos: info.kos ? info.kos[D.team] : D.kos || 0 }));")
rep("<span>Eliminations</span><span>Paint</span></div>';", "<span>Eliminations</span><span>Score</span></div>';")
rep("    const say = ordinal(e.place) + ', ' + nm + (me ? ' (you)' : '') + ', ' + e.pct + '% painted' + (solo ? '' : ', ' + e.kos",
    "    const say = ordinal(e.place) + ', ' + nm + (me ? ' (you)' : '') + ', ' + e.pct + (solo ? '% painted' : '% score') + (solo ? '' : ', ' + e.kos")

# the frame hook, and the reset
rep("  if (vic) vicFrame(rdt);", "  if (tal) talFrame();\n  if (vic) vicFrame(rdt);")
rep("function abortVictory() { if (vic) restoreVictory(); vicEl.hidden = true; vicEl.classList.remove('out'); }",
    "function abortVictory() { if (vic) restoreVictory(); vicEl.hidden = true; vicEl.classList.remove('out'); if (tal) hideTally(); }")

# the tally itself
rep("function showEnd(img) {", r'''// ---------- the tally: everyone's paint counted up, then each elimination laid on top of it, then the winner ----------
const talEl = $('tally'); let tal = null;
function startTally() {
  if (state !== 'dead' || vic || tal) return; const info = endInfo;
  if (info.mode === 'solo' || !info.tot || window.__instant) return startVictory();
  const ppl = ACTIVE.map(D => ({ D, cov: Math.round([info.you, info.cpu, info.cpu2][D.team] || 0), kos: info.kos[D.team] || 0, tot: info.tot[D.team] })).sort((a, b) => b.cov - a.cov || (b.D === P) - (a.D === P));
  const maxK = Math.max(0, ...ppl.map(e => e.kos)), scale = Math.min(100, Math.max(12, Math.max(...ppl.map(e => e.tot)) * 1.12));
  const KO0 = 2.5, KOD = 0.42, KOEND = KO0 + (maxK ? maxK * KOD + 0.6 : 1);
  tal = { t0: performance.now(), t: 0, ppl, scale, maxK, T0: 0.55, T1: 2.05, KO0, KOD, KOEND, END: KOEND + 1.7, ticks: 0, phase: 0, id: runId, lastTick: 0 };
  $('tyRows').innerHTML = ppl.map((e, i) => { const [c, hi] = colVars(e.D), me = e.D === P;
    return '<div class="tyrow' + (me ? ' you' : '') + '" role="listitem" style="--c:' + c + ';--chi:' + hi + ';--d:' + (0.1 + i * 0.1).toFixed(2) + 's">' + faceIcon(e.D, false)
      + '<div class="tymain"><div class="tyname"><b>' + escAttr(nameOf(e.D)) + '</b>' + (me ? '<i>You</i>' : '') + '<span class="tykos" aria-hidden="true"></span></div><div class="tybar" aria-hidden="true"><i class="tyf"></i><i class="tyk"></i></div></div><b class="tynum">0%</b></div>'; }).join('');
  ppl.forEach((e, i) => { const r = $('tyRows').children[i]; e.el = r; e.f = r.querySelector('.tyf'); e.k = r.querySelector('.tyk'); e.n = r.querySelector('.tynum'); e.s = r.querySelector('.tykos'); e.shown = 0; e.num = -1; });
  $('tyRows').classList.remove('set'); talHead('Paint', 'How much of the canvas');
  talEl.classList.remove('out'); talEl.hidden = false; hud.classList.add('off'); hintEl.classList.remove('on'); reAdd.delete(bannerEl); bannerEl.classList.remove('on');
  AU.whoosh();
}
function talHead(w, sub) { const el = $('tyWord'); el.textContent = w; restartCls(el, 'in'); $('tySub').innerHTML = sub; }
function talFrame() {
  if (!tal) return; if (state !== 'dead' || tal.id !== runId) return hideTally();
  const now = performance.now(), t = tal.t = (now - tal.t0) / 1000;
  const k0 = clamp((t - tal.T0) / (tal.T1 - tal.T0), 0, 1), k = 1 - Math.pow(1 - k0, 3);
  if (k0 > 0 && k0 < 1 && now - tal.lastTick > 85) { tal.lastTick = now; AU.tick(tal.ticks++); }
  if (k0 >= 1 && tal.phase === 0) { tal.phase = 1; AU.pop(); }
  if (t >= tal.KO0 && tal.phase === 1) { tal.phase = 2; talHead('Eliminations', tal.maxK ? '<b>+' + KO_PCT + '%</b> of the canvas each' : 'None this match'); AU.whoosh(); }
  for (const e of tal.ppl) {
    const cov = e.cov * k, n = t >= tal.KO0 ? clamp(Math.floor((t - tal.KO0) / tal.KOD) + 1, 0, e.kos) : 0, x = cov / tal.scale * 100;
    e.f.style.width = x.toFixed(2) + '%'; e.k.style.left = x.toFixed(2) + '%'; e.k.style.width = (n * KO_PCT / tal.scale * 100).toFixed(2) + '%'; e.k.style.display = n ? '' : 'none';
    if (n !== e.shown) { e.shown = n; e.s.innerHTML = KO_SVG.repeat(n); AU.pop(); restartCls(e.n, 'tick'); if (!reduceMotion) { const up = document.createElement('em'); up.className = 'tyup'; up.textContent = '+' + KO_PCT + '%'; e.el.appendChild(up); setTimeout(() => up.remove(), 900); } }
    const num = Math.round(cov) + n * KO_PCT; if (num !== e.num) { e.num = num; e.n.textContent = num + '%'; }
  }
  if (t >= tal.KOEND && tal.phase === 2) { tal.phase = 3; talWinner(); }
  if (t >= tal.END) { hideTally(); startVictory(); }
}
// the rows settle into their final order, the winner takes the crown
function talWinner() {
  const info = endInfo, ppl = tal.ppl, order = ppl.slice().sort((a, b) => b.tot - a.tot || (b.D === P) - (a.D === P));
  const before = ppl.map(e => e.el.getBoundingClientRect().top);
  $('tyRows').classList.add('set'); order.forEach((e, i) => { e.el.style.order = i; });
  ppl.forEach((e, i) => { const d = before[i] - e.el.getBoundingClientRect().top; if (Math.abs(d) > 1 && !reduceMotion) { e.el.style.transition = 'none'; e.el.style.transform = 'translateY(' + d + 'px)'; void e.el.offsetHeight; e.el.style.transition = ''; e.el.style.transform = ''; } });
  const w = info.winner, wk = w ? info.kos[w.team] : 0;
  if (w) { const e = ppl.find(e => e.D === w); e.el.classList.add('win'); e.el.querySelector('.bico').insertAdjacentHTML('beforeend', CROWN_SVG); }
  talHead(w === P ? 'You win!' : w ? nameOf(w) + ' wins' : 'Draw', w ? '<b>' + info.tot[w.team] + '%</b>' + (wk ? ' with ' + wk + (wk === 1 ? ' elimination' : ' eliminations') : ' of the canvas') : 'Dead even');
  AU.splat(1); buzz(w === P ? [30, 40, 30] : 20); flashScreen();
}
function hideTally() { if (!tal) return; tal = null; talEl.classList.add('out'); setTimeout(() => { if (!tal) talEl.hidden = true; }, 320); }
// a tap skips to the end of the step it is on
function talSkip() { if (!tal) return; const t = tal.t, to = t < tal.T1 ? tal.T1 : t < tal.KOEND ? tal.KOEND : tal.END; tal.t0 -= (to - t) * 1000 + 1; }
talEl.addEventListener('click', () => { AU.init(); talSkip(); });
function showEnd(img) {''')

css = '''
/* the tally: paint counted up, eliminations added on, then the winner */
.tally{position:absolute;inset:0;z-index:11;display:flex;flex-direction:column;justify-content:center;gap:18px;box-sizing:border-box;padding:max(20px,env(safe-area-inset-top)) clamp(16px,5vw,48px) max(20px,env(safe-area-inset-bottom));background:rgba(20,14,30,.84);cursor:pointer;-webkit-tap-highlight-color:transparent;animation:fadein .3s both}
.tally::before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 60% 50% at 50% 40%,rgba(255,255,255,.08),rgba(255,255,255,0) 70%);pointer-events:none}
.tally.out{animation:vicout .3s ease-in forwards;pointer-events:none}
.tyhead{position:relative;display:grid;justify-items:center;gap:8px;text-align:center}
.tyword{font:400 clamp(30px,8.5vw,58px)/.95 var(--font-display);color:var(--cream);text-shadow:.05em .06em 0 var(--ink),calc(.05em + 3px) calc(.06em + 3px) 0 var(--black);transform:rotate(-4deg)}
.tyword.in{animation:vslam .45s cubic-bezier(.2,1.6,.4,1) both}
.tysub{font:800 13px/1.3 var(--font-ui);color:#B8B0C8;letter-spacing:.08em;text-transform:uppercase}
.tysub b{color:var(--cream);font-weight:900}
.tyrows{position:relative;display:grid;gap:12px;width:min(100%,520px);margin:0 auto}
.tyrow{position:relative;display:grid;grid-template-columns:46px minmax(0,1fr) auto;align-items:center;gap:10px;padding:8px 12px 8px 8px;border:2.5px solid var(--black);border-radius:8px;background:var(--paper);color:var(--black);box-shadow:5px 5px 0 rgba(255,255,255,.18);transition:transform .55s cubic-bezier(.3,1.3,.4,1);animation:rowin .5s cubic-bezier(.2,1.2,.35,1) both;animation-delay:var(--d,0s)}
.tyrows.set .tyrow{animation:none}
.tyrow.you{box-shadow:5px 5px 0 rgba(255,255,255,.18),0 0 0 2.5px var(--ink)}
.tyrow.win{box-shadow:5px 5px 0 rgba(255,255,255,.18),0 0 0 3px var(--gold)}
.tyrow.win.you{box-shadow:5px 5px 0 rgba(255,255,255,.18),0 0 0 2.5px var(--ink),0 0 0 5.5px var(--gold)}
.tyrow .bico{width:46px;height:46px;border-color:var(--black)}
.tyrow .bico .crown{top:-18px;stroke:var(--black);animation-delay:.1s}
.tymain{min-width:0}
.tyname{display:flex;align-items:center;gap:6px;min-width:0}
.tyname b{min-width:0;font:900 15px/1.1 var(--font-head);text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tyname i{flex:none;font:800 10px/1 var(--font-ui);font-style:normal;padding:3px 6px;border-radius:99px;background:var(--ink);color:#fff}
.tykos{display:inline-flex;flex-wrap:wrap;justify-content:flex-end;gap:1px;margin-left:auto}
.tykos:empty{display:none}
.tykos svg{width:17px;height:17px;fill:var(--gold);stroke:var(--black);stroke-width:1.6;stroke-linejoin:round;animation:koin .35s cubic-bezier(.3,1.7,.5,1) both}
@keyframes koin{from{opacity:0;transform:scale(2.4) rotate(-50deg)}}
.tybar{position:relative;height:16px;margin-top:6px;border:2px solid var(--black);border-radius:4px;background:#fff;overflow:hidden}
.tybar i{position:absolute;top:0;bottom:0;left:0;width:0}
.tybar .tyf{background:var(--c)}
.tybar .tyk{background:repeating-linear-gradient(-45deg,var(--chi) 0 5px,var(--c) 5px 10px);border-left:2px solid var(--black);box-sizing:border-box}
.tynum{font:400 30px/1 var(--font-display);color:var(--c);text-shadow:2px 2px 0 var(--black);font-variant-numeric:tabular-nums;min-width:2.3em;text-align:right}
.tynum.tick{animation:tick .22s ease-out}
.tyup{position:absolute;right:8px;top:-4px;font:400 20px/1 var(--font-display);color:var(--gold);text-shadow:2px 2px 0 var(--black);animation:tyup .85s ease-out forwards;pointer-events:none}
@keyframes tyup{from{opacity:0;transform:translateY(10px) scale(.6)}25%{opacity:1;transform:scale(1.25)}to{opacity:0;transform:translateY(-36px)}}
.tytap{position:relative;text-align:center;margin:0;font:800 13px/1 var(--font-ui);color:#B8B0C8;opacity:0;animation:vtap 1.6s 1.4s ease-in-out infinite}
@media (max-height:520px) and (min-aspect-ratio:1/1){.tally{gap:10px;padding:max(10px,env(safe-area-inset-top)) max(24px,env(safe-area-inset-right)) max(8px,env(safe-area-inset-bottom)) max(24px,env(safe-area-inset-left))}.tyhead{gap:4px}.tyword{font-size:min(48px,11vh)}.tysub{font-size:12px}.tyrows{gap:8px;width:min(100%,560px)}.tyrow{padding:5px 10px 5px 6px;grid-template-columns:36px minmax(0,1fr) auto}.tyrow .bico{width:36px;height:36px}.tyrow .bico .crown{top:-14px;width:20px;height:16px;margin-left:-10px}.tybar{height:12px;margin-top:4px}.tynum{font-size:24px}.tyname b{font-size:13px}.tykos svg{width:14px;height:14px}.tytap{display:none}}
@media (prefers-reduced-motion:reduce){.tally,.tyrow,.tyword.in,.tykos svg,.tynum.tick,.tytap{animation:none}.tytap{opacity:.7}.tyrow{transition:none}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
import re
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
