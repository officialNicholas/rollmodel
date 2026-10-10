#!/usr/bin/env python3
"""The tally as one bar at the foot of the screen, the Splatoon way: paint pours in from each end as the numbers climb, each elimination splashes another slice on, then the paint splashes over the screen and the winner screen follows. No faces, no rows, no separate screens. On top of ui47_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui47_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
def cut(a, b, new):
    global s
    i = s.index(a); j = s.index(b, i); s = s[:i] + new + s[j:]

# the markup
cut('  <section class="tally" id="tally" hidden aria-live="polite">', '  <section class="victory" id="victory"', '''  <section class="tally" id="tally" hidden aria-live="polite">
    <div class="tysplash" id="tySplash" aria-hidden="true"></div>
    <div class="tyhead"><b class="tyword" id="tyWord"></b><span class="tysub" id="tySub"></span></div>
    <div class="tystory">
      <div class="tynames"><span class="tyname l" id="tyNameL"></span><span class="tyname m" id="tyNameM" hidden></span><span class="tyname r" id="tyNameR"></span></div>
      <div class="tynums"><span class="tynum l" id="tyNumL"><b>0%</b></span><span class="tynum m" id="tyNumM" hidden><b>0%</b></span><span class="tynum r" id="tyNumR"><b>0%</b></span></div>
      <div class="tybar" id="tyBar" aria-hidden="true"></div>
      <p class="tytap">Tap to skip</p>
    </div>
  </section>
''')

# the code
cut("// ---------- the tally: everyone's paint counted up", "function showEnd(img) {", r'''// ---------- the tally: one bar at the foot of the screen tells it. Paint pours in from each end as the numbers climb, each
// elimination splashes another slice on, then the paint splashes over everything and the winner is up ----------
const talEl = $('tally'); let tal = null, tyLiq = null;
const tySeg = (e, f) => e.side === 'l' ? { x0: 0, x1: f, col: e.col } : e.side === 'r' ? { x0: 1 - f, x1: 1, col: e.col } : { x0: 0.5 - f / 2, x1: 0.5 + f / 2, col: e.col };
function startTally() {
  if (state !== 'dead' || vic || tal) return; const info = endInfo;
  if (info.mode === 'solo' || !info.tot || window.__instant) return startVictory();
  const trio = info.mode === 'trio', order = trio ? [P, H2, H] : [P, H]; // you from the left, the rival from the right (a 3-way: the second rival in the middle)
  const ppl = order.map((D, i) => ({ D, cov: Math.round([info.you, info.cpu, info.cpu2][D.team] || 0), kos: info.kos[D.team] || 0, tot: info.tot[D.team], side: trio ? 'lmr'[i] : i ? 'r' : 'l', col: TEAMS[D.team].css, hi: colVars(D)[1], shown: 0, num: -1 }));
  const sum = ppl.reduce((q, e) => q + e.tot, 0), scale = Math.min(100, Math.max(30, sum * 1.18)), koq = [], maxK = Math.max(0, ...ppl.map(e => e.kos));
  for (let k = 0; k < maxK; k++) for (const e of ppl) if (e.kos > k) koq.push(e); // (the eliminations land one at a time, taking turns)
  const KO0 = 2.7, KOD = 0.46, KOEND = KO0 + (koq.length ? koq.length * KOD + 0.7 : 0.8);
  tal = { t0: performance.now(), t: 0, ppl, scale, koq, nk: 0, T0: 0.55, T1: 2.3, KO0, KOD, KOEND, END: KOEND + 2.1, ticks: 0, phase: 0, id: runId, lastTick: 0 };
  for (const e of ppl) { const u = e.side.toUpperCase(), nm = $('tyName' + u), nu = $('tyNum' + u); nm.hidden = nu.hidden = false; nm.textContent = nameOf(e.D); nm.style.setProperty('--c', e.col); nu.style.setProperty('--c', e.col); nu.className = 'tynum ' + e.side; nu.innerHTML = '<b>0%</b>'; e.nu = nu; }
  if (!trio) $('tyNameM').hidden = $('tyNumM').hidden = true;
  $('tyWord').textContent = ''; $('tySub').textContent = TH.label + ' · ' + (MODES.find(m => m[0] === mode) || MODES[0])[1]; talEl.classList.remove('win'); $('tySplash').className = 'tysplash';
  if (!tyLiq) tyLiq = makeLiquid($('tyBar')); tyLiq.segs = []; tyLiq.drops.length = 0; tyLiq.set(ppl.map(e => tySeg(e, 0))); tyLiq.clear();
  talEl.classList.remove('out'); talEl.hidden = false; hud.classList.add('off'); hintEl.classList.remove('on'); reAdd.delete(bannerEl); bannerEl.classList.remove('on');
  AU.whoosh();
}
// a splash of its paint where a slice lands on the bar
function tySplat(e, f) { if (reduceMotion) return; const bar = $('tyBar'), x = e.side === 'l' ? f : e.side === 'r' ? 1 - f : 0.5 + f / 2, i = document.createElement('i'); i.className = 'tysplat'; i.style.cssText = '--c:' + e.col + ';left:' + (x * 100).toFixed(1) + '%'; bar.parentNode.appendChild(i); i.style.top = (bar.offsetTop + bar.offsetHeight / 2) + 'px'; setTimeout(() => i.remove(), 700); }
function talFrame() {
  if (!tal) return; if (state !== 'dead' || tal.id !== runId) return hideTally();
  const now = performance.now(), t = tal.t = (now - tal.t0) / 1000;
  const k0 = clamp((t - tal.T0) / (tal.T1 - tal.T0), 0, 1), k = 1 - Math.pow(1 - k0, 3);
  if (k0 > 0 && k0 < 1 && now - tal.lastTick > 85) { tal.lastTick = now; AU.tick(tal.ticks++); }
  if (k0 >= 1 && tal.phase === 0) { tal.phase = 1; AU.pop(); }
  if (t >= tal.KO0 && tal.phase === 1) tal.phase = 2;
  const nk = t >= tal.KO0 ? clamp(Math.floor((t - tal.KO0) / tal.KOD) + 1, 0, tal.koq.length) : 0;
  for (let i = tal.nk; i < nk; i++) { const e = tal.koq[i]; e.shown++; AU.splat(0.55); buzz(12); restartCls(e.nu, 'tick'); tySplat(e, (e.cov + e.shown * KO_PCT) / tal.scale);
    if (!e.chip) { e.chip = document.createElement('i'); e.chip.className = 'tyko'; e.nu.appendChild(e.chip); } e.chip.textContent = '+' + (e.shown * KO_PCT) + '%'; restartCls(e.chip, 'pop'); }
  tal.nk = nk;
  const segs = [];
  for (const e of tal.ppl) { const cov = e.cov * k, f = Math.min(1, (cov + e.shown * KO_PCT) / tal.scale); segs.push(tySeg(e, f));
    const num = Math.round(cov) + e.shown * KO_PCT; if (num !== e.num) { e.num = num; e.nu.firstChild.textContent = num + '%'; } }
  tyLiq.set(segs); tyLiq.tick(now);
  if (t >= tal.KOEND && tal.phase === 2) { tal.phase = 3; talWinner(); }
  if (t >= tal.END) { hideTally(); startVictory(); }
}
// the paint splashes over the screen in the winner's color and the word goes up
function talWinner() {
  const info = endInfo, w = info.winner, wk = w ? info.kos[w.team] : 0, e = w && tal.ppl.find(e => e.D === w);
  talEl.classList.add('win'); for (const q of tal.ppl) q.nu.classList.toggle('win', q.D === w);
  const sp = $('tySplash'); sp.style.setProperty('--c', e ? e.col : '#F4EEE3'); sp.className = 'tysplash'; void sp.offsetWidth; sp.className = 'tysplash go';
  const el = $('tyWord'); el.textContent = w === P ? 'You win!' : w ? nameOf(w) + ' wins' : 'Draw'; restartCls(el, 'in');
  $('tySub').innerHTML = w ? '<b>' + info.tot[w.team] + '%</b>' + (wk ? ' with ' + wk + (wk === 1 ? ' elimination' : ' eliminations') : ' of the canvas') : 'Dead even';
  AU.splat(1.2); buzz(w === P ? [30, 40, 30] : 20); flashScreen();
}
function hideTally() { if (!tal) return; tal = null; talEl.classList.add('out'); setTimeout(() => { if (!tal) talEl.hidden = true; }, 320); }
// a tap skips to the end of the step it is on
function talSkip() { if (!tal) return; const t = tal.t, to = t < tal.T1 ? tal.T1 : t < tal.KOEND ? tal.KOEND : tal.END; tal.t0 -= (to - t) * 1000 + 1; }
talEl.addEventListener('click', () => { AU.init(); talSkip(); });
''')

# the styles
cut('/* the tally: paint counted up, eliminations added on, then the winner */', '@media (prefers-reduced-motion:reduce){.tally,', '''/* the tally: one bar tells it */
.tally{position:absolute;inset:0;z-index:11;display:flex;flex-direction:column;justify-content:flex-end;box-sizing:border-box;padding:0 clamp(14px,4vw,40px) max(18px,calc(env(safe-area-inset-bottom) + 10px));background:linear-gradient(180deg,rgba(20,14,30,0) 28%,rgba(20,14,30,.5) 58%,rgba(20,14,30,.9) 100%);cursor:pointer;-webkit-tap-highlight-color:transparent;overflow:hidden;animation:fadein .3s both}
.tally.out{animation:vicout .3s ease-in forwards;pointer-events:none}
.tyhead{position:relative;display:grid;justify-items:center;gap:6px;text-align:center;margin-bottom:16px;min-height:58px}
.tyword{font:400 clamp(34px,10vw,66px)/.95 var(--font-display);color:var(--cream);text-shadow:.05em .06em 0 var(--ink),calc(.05em + 3px) calc(.06em + 3px) 0 var(--black);transform:rotate(-4deg)}
.tyword:empty{display:none}
.tyword.in{animation:vslam .45s cubic-bezier(.2,1.6,.4,1) both}
.tysub{font:800 12px/1.3 var(--font-ui);color:#B8B0C8;letter-spacing:.1em;text-transform:uppercase;text-shadow:0 1px 0 rgba(0,0,0,.5)}
.tysub b{color:var(--cream);font-weight:900}
.tystory{position:relative;display:grid;gap:3px;width:min(100%,640px);margin:0 auto;animation:vrise .45s .1s cubic-bezier(.3,1.5,.5,1) both}
.tynames,.tynums{display:grid;grid-template-columns:1fr auto 1fr;align-items:end;gap:8px;padding:0 4px}
.tyname{font:900 15px/1.1 var(--font-head);text-transform:uppercase;color:var(--c);text-shadow:.04em .04em 0 var(--black),2px 3px 0 rgba(0,0,0,.4);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tyname.m,.tynum.m{text-align:center;justify-self:center}
.tyname.r,.tynum.r{text-align:right;justify-self:end}
.tynum{display:flex;align-items:baseline;gap:6px;min-width:0;font:400 clamp(30px,9vw,54px)/1 var(--font-display);color:#fff;text-shadow:.045em .055em 0 var(--c),calc(.045em + 3px) calc(.055em + 3px) 0 var(--black);font-variant-numeric:tabular-nums}
.tynum.r{flex-direction:row-reverse}
.tynum b{font-weight:400}
.tynum.tick b{animation:tick .22s ease-out;display:inline-block}
.tynum.win b{color:var(--gold)}
.tyko{font:400 17px/1 var(--font-display);color:var(--gold);text-shadow:2px 2px 0 var(--black);position:relative;top:-.12em;white-space:nowrap}
.tyko.pop{animation:koin .4s cubic-bezier(.3,1.7,.5,1) both}
@keyframes koin{from{opacity:0;transform:scale(2.4) rotate(-50deg)}}
.tybar{position:relative;height:34px;margin:4px 6px 0;border:3px solid var(--black);border-radius:6px;background:#2A2338 repeating-linear-gradient(-55deg,rgba(255,255,255,.04) 0 6px,rgba(255,255,255,0) 6px 14px);transform:skewX(-12deg);overflow:hidden;box-shadow:4px 4px 0 var(--black),0 0 0 2px rgba(255,255,255,.1)}
.tybar .liq{position:absolute;inset:0;width:100%;height:100%;display:block}
.tysplat{position:absolute;width:72px;height:72px;margin:-36px 0 0 -36px;background:var(--c);-webkit-mask:url(art/m_splat2.webp) center/contain no-repeat;mask:url(art/m_splat2.webp) center/contain no-repeat;animation:tysplat .6s ease-out forwards;pointer-events:none;z-index:2}
@keyframes tysplat{from{transform:scale(.25) rotate(-30deg);opacity:1}55%{opacity:.95}to{transform:scale(1.5) rotate(10deg);opacity:0}}
.tysplash{position:absolute;left:50%;top:50%;width:170vmax;height:170vmax;margin:-85vmax 0 0 -85vmax;background:var(--c,#F4EEE3);-webkit-mask:url(art/m_splat.webp) center/contain no-repeat;mask:url(art/m_splat.webp) center/contain no-repeat;transform:scale(0);opacity:0;pointer-events:none}
.tysplash.go{animation:tysplash 1.25s cubic-bezier(.2,.9,.3,1) forwards}
@keyframes tysplash{0%{transform:scale(0) rotate(-25deg);opacity:1}40%{transform:scale(1) rotate(0);opacity:.96}100%{transform:scale(1.2) rotate(6deg);opacity:0}}
.tytap{position:relative;text-align:center;margin:8px 0 0;font:800 12px/1 var(--font-ui);color:#B8B0C8;opacity:0;animation:vtap 1.6s 1.4s ease-in-out infinite}
@media (max-height:520px) and (min-aspect-ratio:1/1){.tally{padding:0 max(24px,env(safe-area-inset-right)) max(10px,env(safe-area-inset-bottom)) max(24px,env(safe-area-inset-left))}.tyhead{margin-bottom:8px;min-height:44px;gap:3px}.tyword{font-size:min(54px,12vh)}.tysub{font-size:11px}.tystory{width:min(100%,560px)}.tyname{font-size:13px}.tynum{font-size:34px}.tybar{height:24px}.tytap{display:none}}
''')
rep("@media (prefers-reduced-motion:reduce){.tally,.tyrow,.tyword.in,.tykos svg,.tynum.tick,.tytap{animation:none}.tytap{opacity:.7}.tyrow{transition:none}}", "@media (prefers-reduced-motion:reduce){.tally,.tystory,.tyword.in,.tyko.pop,.tynum.tick b,.tytap,.tysplash.go{animation:none}.tytap{opacity:.7}}")

m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
