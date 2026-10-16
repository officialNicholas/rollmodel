"""v316: the boss's health, as a bar of its paint across the top of the screen, under its name: Jellyfish Boss (for now).

- In the boss demo the bar takes the place of the coverage card at the top (Preview, its percent and Best mean nothing here).
- The bar is the boss's own pink paint in a dark tube: glossy, slowly flowing, its end a rounded bulge of paint, drips hanging off
  its underside. A little jellyfish and the name sit above it.
- It comes in with the boss. As the boss shoots up out of the pool in its entrance, the bar drops in and fills from empty to full.
  When the entrance plays again, or the boss comes back after a defeat, it goes and comes back the same way.
- Hurt takes a chunk off (12%). The bar jolts, flashes and throws a few drops of paint, and the lost part shows pale for a moment
  before it drains away. At zero, the boss is defeated by itself. Defeat drains whatever is left.
- Upright it sits between the pause and sound buttons; sideways it's wider, in the middle of the top."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HTML = ('<div class="cqbar" id="cqbBar" hidden role="img" aria-label="Jellyfish Boss health"><div class="cqbn"><svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path d="M3.5 12.5a8.5 8 0 0 1 17 0c-1.4.9-2.6.9-4.2 0-1.4.9-2.8.9-4.3 0-1.5.9-2.9.9-4.3 0-1.6.9-2.8.9-4.2 0z" fill="#F04FC0" stroke="#171320" stroke-width="2" stroke-linejoin="round"/>'
        '<path d="M8 14.5c-.8 2 .6 3.4-.4 5.6M12 14.5c-.8 2.3.7 3.8-.3 6.6M16 14.5c-.8 2 .6 3.4-.4 5.6" fill="none" stroke="#F04FC0" stroke-width="2.4" stroke-linecap="round"/>'
        '<circle cx="9.3" cy="9.6" r="1.25" fill="#171320"/><circle cx="14.7" cy="9.6" r="1.25" fill="#171320"/></svg><b>Jellyfish Boss</b></div>'
        '<div class="cqbt"><i class="cqbg"></i><i class="cqbf"></i><i class="cqbe"></i><span class="cqbd"><i style="left:21%"></i><i style="left:47%"></i><i style="left:76%"></i></span>'
        '<span class="cqbs"><i style="--dx:-10px;--dy:-16px"></i><i style="--dx:9px;--dy:-19px"></i><i style="--dx:14px;--dy:-6px"></i><i style="--dx:-4px;--dy:14px"></i><i style="--dx:11px;--dy:12px"></i></span></div></div>')

CSS = r"""
/* (v316) the boss's health: a bar of its pink paint across the top, under its name */
.cqbar{position:absolute;z-index:8;top:calc(env(safe-area-inset-top) + 12px);left:50%;width:min(calc(100% - 150px),300px);transform:translateX(-50%);pointer-events:none;--hp:1;--gh:1}
.cqbar.in{animation:cqbarin .55s cubic-bezier(.2,1.5,.35,1) both}
@keyframes cqbarin{from{opacity:0;transform:translateX(-50%) translateY(-26px) scale(.9)}}
.cqbn{display:flex;align-items:center;gap:5px;margin:0 0 5px 4px;color:#FFF8EA;font:400 14px/1 var(--font-display);letter-spacing:.04em;text-transform:uppercase;text-shadow:0 2px 0 #171320,0 0 8px rgba(23,19,32,.7);white-space:nowrap}
.cqbn svg{flex:none;width:20px;height:20px;margin-top:-3px;filter:drop-shadow(0 2px 0 #171320)}
.cqbt{position:relative;height:16px;border-radius:99px;background:#2A1240;border:3px solid #171320;box-shadow:0 3px 0 #171320,inset 0 3px 5px rgba(0,0,0,.5)}
.cqbt>i{position:absolute;left:0;top:0;bottom:0;border-radius:99px}
.cqbg{width:calc(var(--gh) * 100%);background:#FFE4F6}
.cqbf{width:calc(var(--hp) * 100%);background:linear-gradient(180deg,#FF9BE2,#F04FC0 46%,#A81C84);transition:filter .25s}
.cqbf::before{content:'';position:absolute;inset:0;border-radius:inherit;background:repeating-linear-gradient(115deg,transparent 0 9px,rgba(255,255,255,.16) 9px 12px,transparent 12px 22px);background-size:44px 100%;animation:cqbflow 1.8s linear infinite}
.cqbf::after{content:'';position:absolute;left:5px;right:7px;top:2px;height:3px;border-radius:99px;background:rgba(255,255,255,.6)}
@keyframes cqbflow{to{background-position:44px 0}}
.cqbe{left:min(calc(var(--hp) * 100% - 8px),calc(100% - 11px))!important;right:auto;top:-3px!important;bottom:-3px!important;width:11px;border-radius:45% 55% 55% 45%/50%!important;background:linear-gradient(180deg,#FF9BE2,#F04FC0 50%,#A81C84);box-shadow:inset -2px 0 0 rgba(255,255,255,.35);animation:cqbwob 1.3s ease-in-out infinite alternate;transform-origin:30% 50%}
@keyframes cqbwob{to{transform:scale(1.12,.9)}}
.cqbar.empty .cqbe,.cqbar.empty .cqbd{display:none}
.cqbd i{position:absolute;top:100%;width:6px;height:7px;margin-left:-3px;border-radius:50% 50% 50% 50%/35% 35% 65% 65%;background:#C42A9C;transform-origin:50% 0;animation:cqbdrip 2.4s ease-in-out infinite}
.cqbd i:nth-child(2){animation-delay:-.8s;height:9px}.cqbd i:nth-child(3){animation-delay:-1.6s}
.cqbd i.off{display:none}
@keyframes cqbdrip{50%{transform:scaleY(1.7)}}
.cqbs i{position:absolute;left:calc(var(--hp) * 100%);top:50%;width:6px;height:6px;margin:-3px;border-radius:50%;background:#F04FC0;opacity:0}
.cqbar.hit .cqbt{animation:cqbshake .38s ease-out}
.cqbar.hit .cqbf{filter:brightness(1.7) saturate(.8)}
.cqbar.hit .cqbs i{animation:cqbsplat .5s ease-out}
@keyframes cqbshake{20%{transform:translate(-4px,1px)}40%{transform:translate(4px,-1px)}60%{transform:translate(-2px,0)}80%{transform:translate(2px,0)}}
@keyframes cqbsplat{0%{opacity:1;transform:none}100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(.4)}}
.hud.cqbon .score{visibility:hidden}
@media (max-height:520px) and (min-aspect-ratio:1/1){.cqbar{top:calc(env(safe-area-inset-top) + 10px);width:min(46vw,420px)}.cqbt{height:18px}.cqbn{font-size:15px}}
@media (prefers-reduced-motion:reduce){.cqbar.in,.cqbf::before,.cqbe,.cqbd i,.cqbar.hit .cqbt{animation:none}}
"""

JS = r"""// (v316) the boss's health: a bar of its paint across the top, under its name. Full as it shoots up out of the pool (filling from
// empty), a chunk off for each Hurt (the lost part pale for a moment, then draining away), defeated by itself at zero; Defeat drains it
function cqbBar() {
  const Q = CQB; if (Q.bar) return Q.bar; const el = $('cqbBar'); if (!el) return null;
  return (Q.bar = { el, drips: [...el.querySelectorAll('.cqbd i')].map(e => [e, parseFloat(e.style.left) / 100]), hp: 1, gh: 0, hold: 0, vis: false, fillT: -1, defIn: 0, key: '', hud: null, hitT: 0 });
}
function cqbBarHit() { const B = CQB.bar; if (!B) return; B.el.classList.remove('hit'); void B.el.offsetWidth; B.el.classList.add('hit'); B.hitT = 0.5; }
function cqbBarEv(e, d) {
  const B = cqbBar(); if (!B) return;
  if (e === 'start' && d.move === 'emerge') { B.vis = false; B.hp = 0; B.gh = 0; B.fillT = -1; B.defIn = 0; }
  else if (e === 'launch' || (e === 'emergeDone' && !B.vis)) { B.vis = true; B.hp = 1; B.gh = 0; B.fillT = 0; B.el.classList.remove('in'); void B.el.offsetWidth; B.el.classList.add('in'); }
  else if (e === 'start' && d.move === 'hurt' && B.vis && B.hp > 0) { if (B.hold <= 0) B.gh = Math.max(B.gh, B.hp); B.hp = Math.max(0, B.hp - 0.12); B.hold = 0.5; B.fillT = -1; cqbBarHit(); if (B.hp <= 0.001) B.defIn = 0.75; }
  else if (e === 'start' && d.move === 'defeat' && B.vis) { if (B.hp > 0) { if (B.hold <= 0) B.gh = Math.max(B.gh, B.hp); B.hp = 0; B.hold = 0.35; B.fillT = -1; cqbBarHit(); } B.defIn = 0; }
}
function cqbBarTick(rdt) {
  const Q = CQB, B = Q && (Q.bar || (Q.on && cqbBar())); if (!B) return;
  const hud = !!Q.on; if (B.hud !== hud) { B.hud = hud; const h = $('hud'); if (h) h.classList.toggle('cqbon', hud); B.vis = false; B.hp = 0; B.gh = 0; B.fillT = -1; B.defIn = 0; B.hold = 0; } // (a new demo: no bar until the boss is up)
  const on = !!(Q.on && Q.boss && Q.boss.isReady && B.vis && (state === 'play' || state === 'reveal' || state === 'intro' || state === 'paused'));
  if (B.el.hidden === on) B.el.hidden = !on; if (!on) return;
  if (B.defIn > 0 && (B.defIn -= rdt) <= 0 && Q.boss.move !== 'defeat') cqbPlay('defeat');
  if (B.hitT > 0 && (B.hitT -= rdt) <= 0) B.el.classList.remove('hit');
  if (B.hold > 0) B.hold -= rdt; else if (B.gh > B.hp) B.gh = Math.max(B.hp, B.gh - rdt * 0.8);
  let f = B.hp; if (B.fillT >= 0) { B.fillT += rdt; const u = Math.min(1, B.fillT / 1.15); f = B.hp * (1 - Math.pow(1 - u, 3)); if (u >= 1) B.fillT = -1; }
  const g = Math.max(f, B.gh), key = f.toFixed(3) + '|' + g.toFixed(3);
  if (key !== B.key) { B.key = key; B.el.style.setProperty('--hp', f.toFixed(3)); B.el.style.setProperty('--gh', g.toFixed(3)); B.el.classList.toggle('empty', f < 0.01); for (const [e, p] of B.drips) e.classList.toggle('off', p > f - 0.04); }
}
"""


def apply(s):
    s = rep(s, '<div class="hud off" id="hud">', HTML + '<div class="hud off" id="hud">')
    s = rep(s, "function cqbEvent(e, d) {\n  const Q = CQB; if (!Q || !Q.on) return; const near = Q.cut ? 1 : 0;",
               JS + "function cqbEvent(e, d) {\n  const Q = CQB; if (!Q || !Q.on) return; const near = Q.cut ? 1 : 0; cqbBarEv(e, d); // (v316: the health bar)")
    s = rep(s, "function cqbTick(dt, rdt) {\n", "function cqbTick(dt, rdt) {\n  cqbBarTick(rdt); // (v316: the health bar)\n")
    s = rep(s, "/* (v315) the boss demo's panel:", CSS.strip() + "\n/* (v315) the boss demo's panel:")
    return s
