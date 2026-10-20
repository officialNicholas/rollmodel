"""v404: two new skills, bought with dabs (the user).

- Paint Boost (400 dabs): "reduces your paint usage and lets you go for longer without running out of paint as fast". Your trail
  takes 30% less paint, and so do rolls and pounds. Offline (as the other skills).
- Jackpot (500 dabs): "1.5x the amount of dabs when equipped, but it only pays out if you or your team wins". Win (or your team
  does) and you get half as many dabs again; lose and nothing extra. On the results, once the dabs are in, an extra beat: a gold
  JACKPOT stamp, a ring of coins, and the dabs count up again with the jackpot added.
Both on the Strokes page with Ludo-drawn pictures in the same style as the others."""
import base64, os

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets') + '/'

JS = r"""
// (v404) Paint Boost: the trail, rolls and pounds take less paint (offline, as the other skills)
const PBOOST_K = 0.7, pbK = D => (D.skill === 'pboost' && !NM ? PBOOST_K : 1);
// (v404) Jackpot: a win (yours or your team's) pays half as many dabs again; a loss, nothing extra
function jackpotPay(win) {
  endInfo.jack = 0; if (P.skill !== 'jackpot' || !(win > 0) || mode === 'solo' || tut || tut2 || tut3) return;
  const j = Math.max(1, Math.round((endInfo.drops || 0) * 0.5)); store.drops = (store.drops || 0) + j; endInfo.jack = j; save();
}
// the results' extra beat: a gold JACKPOT stamp over the dabs, coins round it, and the dabs counting up again
function jackBeat(info, wait) {
  setTimeout(() => {
    const dg = $('dropGain'), row = $('repRow'); if (!dg || dg.hidden || end.hidden || !info.jack) return;
    const st = document.createElement('span'); st.className = 'jackpot'; st.innerHTML = '<b>Jackpot!</b><i>+' + info.jack + '</i>'; row.appendChild(st);
    AU.xplay && AU.xplay('coins', { v: 0.9 }) || AU.power(); buzz([15, 25, 15]); hap && hap('success');
    for (let i = 0; i < 10; i++) { const c = document.createElement('i'); c.className = 'jcoin'; c.innerHTML = DROP_SVG; c.style.setProperty('--a', (i / 10 * 360 + Math.random() * 20).toFixed(0) + 'deg'); c.style.setProperty('--d', (0.05 * i).toFixed(2) + 's'); st.appendChild(c); }
    const from = info.drops, to = info.drops + info.jack, t0 = performance.now(), dur = 900; let last = from;
    const step = () => { const u = Math.min(1, (performance.now() - t0 - 350) / dur); if (u < 0) return requestAnimationFrame(step);
      const v = Math.round(from + (to - from) * (1 - Math.pow(1 - u, 2))); if (v !== last) { last = v; dg.innerHTML = '+' + v + DROP_SVG + '<small>dabs</small>'; if (AU.xplay) AU.xplay('coin', { v: 0.35, rate: 1 + (v - from) / Math.max(1, to - from) * 0.4 }); }
      if (u < 1) requestAnimationFrame(step); else { kick(dg, 'cbig'); setTimeout(() => st.classList.add('out'), 1500); setTimeout(() => st.remove(), 2100); } };
    requestAnimationFrame(step);
  }, wait);
}
"""

CSS = r"""
/* (v404) the Jackpot beat on the results: a gold stamp over the dabs, coins bursting off it */
#repRow{position:relative}
#repRow .jackpot{position:absolute;right:-6px;top:-30px;z-index:3;display:grid;justify-items:center;gap:1px;padding:6px 12px 5px;border-radius:8px;background:linear-gradient(180deg,#FFE58A 0%,#F2B92E 100%);color:#171320;box-shadow:0 0 0 3px #171320,3px 4px 0 3px rgba(0,0,0,.45);transform:rotate(-6deg);animation:jackin .55s cubic-bezier(.2,1.5,.4,1) both;pointer-events:none}
#repRow .jackpot b{font:400 20px/1 var(--font-display);letter-spacing:.04em;text-transform:uppercase}
#repRow .jackpot i{font:900 13px/1 var(--font-head);font-style:normal}
#repRow .jackpot.out{animation:jackout .5s ease-in both}
#repRow .jackpot .jcoin{position:absolute;left:50%;top:50%;width:18px;height:18px;margin:-9px;animation:jcoin .8s var(--d) cubic-bezier(.2,.8,.3,1) both}
#repRow .jackpot .jcoin svg{width:100%;height:100%;fill:#F2B92E;filter:drop-shadow(1px 1px 0 #171320)}
@keyframes jackin{0%{opacity:0;transform:rotate(-6deg) scale(2.4)}60%{opacity:1;transform:rotate(-6deg) scale(.9)}100%{transform:rotate(-6deg) scale(1)}}
@keyframes jackout{to{opacity:0;transform:rotate(-6deg) scale(.6) translateY(10px)}}
@keyframes jcoin{0%{opacity:1;transform:rotate(var(--a)) translateY(0) scale(.6)}100%{opacity:0;transform:rotate(var(--a)) translateY(-62px) scale(1)}}
@media (prefers-reduced-motion:reduce){#repRow .jackpot,#repRow .jackpot .jcoin{animation:none}}
"""

def apply(s):
    img = {k: 'data:image/webp;base64,' + base64.b64encode(open(A + k + '_flat_256.webp', 'rb').read()).decode() for k in ['pboost', 'jackpot']}
    s = rep(s, "SKILLS.push({ id: 'shock', name: 'Aftershock',",
               "SKILLS.push({ id: 'pboost', name: 'Paint Boost', desc: 'Your paint goes further.', does: ['Your trail uses less paint as you go', 'Rolls and pounds cost less paint too', 'Fewer trips back to a basin'] }); // (v404)\n"
               "SKILLS.push({ id: 'jackpot', name: 'Jackpot', desc: 'Win, and the dabs pay out big.', does: ['Win the match (or your team does) and get 1.5x the dabs', 'Lose, and it pays nothing extra', 'The jackpot comes in on the results'] }); // (v404)\n"
               "SKILLS.push({ id: 'shock', name: 'Aftershock',")
    s = rep(s, "storm: 600, bomb: 600 };", "storm: 600, bomb: 600, pboost: 400, jackpot: 500 };")
    s = rep(s, "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets', 'storm', 'shock', 'bomb']) STROKE_ICON[k] = stImg(k);",
               "ST_IMG.pboost = '" + img['pboost'] + "'; ST_IMG.jackpot = '" + img['jackpot'] + "'; // (v404: Ludo.ai, the same style)\n"
               "for (const k of ['rocket', 'giant', 'freeze', 'swim', 'repel', 'pockets', 'storm', 'shock', 'bomb', 'pboost', 'jackpot']) STROKE_ICON[k] = stImg(k);")
    s = rep(s, "swim: [['Glide', 'Much faster than normal'],", "pboost: [['Paint use', 'About a third less'], ['Rolls and pounds', 'Cheaper too']], jackpot: [['On a win', '1.5x the dabs'], ['On a loss', 'Nothing extra']], swim: [['Glide', 'Much faster than normal'],")
    # Paint Boost: the trail, rolls and pounds
    s = rep(s, "else D.paint -= cfg.drain * dt * ", "else D.paint -= cfg.drain * dt * pbK(D) * ")
    s = rep(s, "D.paint = Math.max(0.001, D.paint - ROLL_COST)", "D.paint = Math.max(0.001, D.paint - ROLL_COST * pbK(D))")
    s = rep(s, "if (D.giantT <= 0) D.paint -= Math.min(SLAM_COST, D.paint - 0.08);", "if (D.giantT <= 0) D.paint -= Math.min(SLAM_COST * pbK(D), D.paint - 0.08);")
    # Jackpot: paid with the dabs, shown after them
    s = rep(s, "store.drops = (store.drops || 0) + drops; endInfo.drops = drops;", "store.drops = (store.drops || 0) + drops; endInfo.drops = drops; jackpotPay(win);", 2)
    s = rep(s, "  row.classList.remove('lv'); repAnim = requestAnimationFrame(step);\n}", "  row.classList.remove('lv'); repAnim = requestAnimationFrame(step);\n  for (const x of row.querySelectorAll('.jackpot')) x.remove(); if (info.jack > 0) jackBeat(info, 900 + dur + 500); // (v404)\n}")
    s = rep(s, "\n// ---------- (v404) Paint Bomb:", JS + "\n// ---------- (v404) Paint Bomb:")
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
