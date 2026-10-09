#!/usr/bin/env python3
"""The hero's speech bubble keeps clear of the lobby chrome. On top of ui15_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui15_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# the tail follows the head: its x is a CSS var, and both sides share one transform
rep('.lsay::after{content:"";position:absolute;left:14px;bottom:-11px;', '.lsay::after{content:"";position:absolute;left:var(--tx,14px);bottom:-11px;')
rep('.lsay.flip{transform:translate(-100%,-100%)}', '.lsay.flip{transform:translate(0,-100%)}')
rep('.lsay.flip::after{left:auto;right:14px;transform:skewX(-20deg) rotate(-45deg)}', '.lsay.flip::after{transform:skewX(-20deg) rotate(-45deg)}')
rep('@keyframes sayinf{from{opacity:0;transform:translate(-100%,-100%) scale(.6)}}', '@keyframes sayinf{from{opacity:0;transform:translate(0,-100%) scale(.6)}}')
rep('.lsay{position:absolute;z-index:3;max-width:min(52vw,220px);', '.lsay{position:absolute;z-index:3;max-width:min(60vw,220px);')

# placement: start above the head, then slide out of the lobby plates and the window edges
OLD = "  if (!heroSay.hidden) { const h = tv2.set(P.x, 0.98, P.z).project(camera), sx = (h.x * 0.5 + 0.5) * viewW, sy = (0.5 - h.y * 0.5) * viewH, flip = sx > viewW * 0.58; heroSay.classList.toggle('flip', flip); heroSay.style.left = (flip ? sx - 14 : sx + 14).toFixed(0) + 'px'; heroSay.style.top = (sy - 8).toFixed(0) + 'px'; }"
NEW = "  if (!heroSay.hidden) placeSay();"
rep(OLD, NEW)
rep("let sayT = 0, sayLast = -1;", '''let sayT = 0, sayLast = -1, sayObs = [], sayObsT = 0;
// the lobby pieces the bubble must not cover (measured when it appears, then every half second)
function sayObstacles() {
  const out = [], ids = ['lobbyTop', 'logo', 'lobbyBot'], els = [...ids.map(id => $(id)), ...$('lobbyRail').children, ...$('lobbyRight').children];
  for (const el of els) { if (!el || el.hidden) continue; const r = el.getBoundingClientRect(); if (r.width > 0 && r.height > 0) out.push({ l: r.left, t: r.top, r: r.right, b: r.bottom }); }
  return out;
}
function placeSay() {
  const h = tv2.set(P.x, 0.98, P.z).project(camera), sx = (h.x * 0.5 + 0.5) * viewW, sy = (0.5 - h.y * 0.5) * viewH;
  const now = performance.now(); if (now > sayObsT) { sayObs = sayObstacles(); sayObsT = now + 500; }
  const bw = heroSay.offsetWidth || 160, bh = heroSay.offsetHeight || 40, M = 8, flip = sx > viewW * 0.58;
  let left = flip ? sx - 14 - bw : sx + 14, top = sy - 8 - bh;
  // keep inside the window
  left = clamp(left, M, viewW - bw - M); top = Math.max(M, top);
  const hit = o => left < o.r + M && left + bw > o.l - M && top < o.b + M && top + bh > o.t - M;
  for (let pass = 0; pass < 3; pass++) {
    for (const o of sayObs) {
      if (!hit(o)) continue;
      const dxL = left + bw - (o.l - M), dxR = (o.r + M) - left, dy = (o.b + M) - top; // how far to slide left, right, or down to clear it
      const roomL = left - dxL >= M, roomR = left + dxR + bw <= viewW - M;
      if (dy <= Math.min(dxL, dxR) * 0.6 || (!roomL && !roomR)) top += dy;
      else if (dxL <= dxR ? roomL : !roomR) left -= dxL; else left += dxR;
    }
  }
  // the tail points at the head wherever the bubble ended up
  const tx = clamp(sx - left - 8, 12, bw - 30);
  heroSay.classList.toggle('flip', tx > bw * 0.5); heroSay.style.setProperty('--tx', tx.toFixed(0) + 'px');
  heroSay.style.left = left.toFixed(0) + 'px'; heroSay.style.top = (top + bh).toFixed(0) + 'px';
}''')
rep("function heroSpeak(t) { $('heroSayTxt').textContent = t; heroSay.hidden = false;", "function heroSpeak(t) { $('heroSayTxt').textContent = t; heroSay.hidden = false; sayObsT = 0; placeSay();")
rep('<p class="ver">Version 85</p>', '<p class="ver">Version 86</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
