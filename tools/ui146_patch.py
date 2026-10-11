#!/usr/bin/env python3
"""v218: Choose Event runs Versus CPU, Matchmaking (coming soon, greyed like Showdown), Showdown, Solo, Tutorial. On the home screen
Abilities is always there (greyed out until rank 3), and the Friends button and the spots beside you show through the onboarding too;
in portrait Friends stands lower, clear of the logo, just over the spot at your right."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui145_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- Choose Event: the cards' order, and Matchmaking
g0 = s.index('<div class="evgrid" id="evGrid" role="group" aria-labelledby="evTitle">\n') + len('<div class="evgrid" id="evGrid" role="group" aria-labelledby="evTitle">\n')
g1 = s.index('      </div>\n', g0)
cards = s[g0:g1].split('\n'); cards = [c for c in cards if c.strip()]
by = {}
for c in cards:
    k = c.split('data-ev="')[1].split('"')[0]; by[k] = c
assert set(by) == {'solo', 'vs', 'showdown', 'tut'}, by.keys()
MM_ICON = ('<svg viewBox="0 0 64 64"><circle cx="32" cy="28" r="22" fill="#8FDCF3" stroke="#171320" stroke-width="3.2"/>'
           '<path d="M10 28h44M32 6c-8 7-8 37 0 44M32 6c8 7 8 37 0 44M14 16h36M14 40h36" fill="none" stroke="#171320" stroke-width="2.4"/>'
           '<circle cx="15" cy="49" r="9" fill="#E3122F" stroke="#171320" stroke-width="3"/><circle cx="49" cy="49" r="9" fill="#2E9BFF" stroke="#171320" stroke-width="3"/>'
           '<circle cx="12.5" cy="47.5" r="1.6" fill="#171320"/><circle cx="17.5" cy="47.5" r="1.6" fill="#171320"/><circle cx="46.5" cy="47.5" r="1.6" fill="#171320"/><circle cx="51.5" cy="47.5" r="1.6" fill="#171320"/></svg>')
mm = ('        <div class="evcard soon" data-ev="match" style="--ec:#19B7A5"><button class="evmain" id="evMatch" type="button" aria-disabled="true"><span class="evbar"><i>Coming soon</i></span>'
      '<span class="evtop"><span class="evic" aria-hidden="true">' + MM_ICON + '</span><span class="evtx"><b>Matchmaking</b><small>Play people online</small></span></span>'
      '<span class="evart" aria-hidden="true"><img id="evMatchArt" alt=""></span></button><i class="evsoon">Coming soon</i></div>')
s = s[:g0] + '\n'.join([by['vs'], mm, by['showdown'], by['solo'], by['tut']]) + '\n' + s[g1:]
rep("set('evShowArt', 'manor'); set('evTutArt', 'island'); }", "set('evShowArt', 'manor'); set('evTutArt', 'island'); set('evMatchArt', 'crypt'); }")
rep("$('evShow').addEventListener('click', () => {",
    "$('evMatch').addEventListener('click', () => { AU.init(); AU.nope(); const c = $('evMatch').closest('.evcard'), old = c.querySelector('.evtoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'evtoast'; t.textContent = 'Matchmaking is coming soon'; c.appendChild(t); setTimeout(() => t.remove(), 1700); });\n"
    "$('evShow').addEventListener('click', () => {")
rep(".evcard:nth-child(4){animation-delay:.15s}", ".evcard:nth-child(4){animation-delay:.15s}.evcard:nth-child(5){animation-delay:.2s}")
# ---- the home screen through the onboarding: Abilities, Friends and the spots beside you stay (only Commissions waits for the end)
rep(".menu.tutoring #commBtn,.menu.tutoring #abilBtn{display:none}", ".menu.tutoring #commBtn{display:none}")
rep(".menu.tutoring #friendsBtn,.menu.tutoring .slot{display:none}", "")
# locked Abilities: greyed out, paper and all
rep(".plate.abil.locked .abart{opacity:.6;filter:saturate(.35)}",
    ".plate.abil.locked .abart{opacity:.55;filter:grayscale(1)}\n.plate.abil.locked .abpaper{filter:grayscale(1) brightness(1.12) drop-shadow(2px 3px 0 rgba(23,19,32,.22))}\n.plate.abil.locked{color:#F1EEF4}")
# ---- the power bar, the spots beside you and Friends, placed together: the spots by your sides; Friends (portrait) lower in its column,
# clear of the logo, just over the spot at your right; the bar over your head, kept between the rails and under the logo, a little smaller
# on a narrow phone so it fits between them
p0 = s.index("function placePBar() {"); p1 = s.index("\n}\n", p0) + 3
s = s[:p0] + """function placePBar() {
  if (pbar.hidden) return;
  pbR.setFromMatrixColumn(camera.matrixWorld, 0); pbR.y = 0; pbR.normalize();
  for (const [el, s] of [[slotL, -1], [slotR, 1]]) {
    pbV.set(P.x + pbR.x * s * 1.05, P.y + 0.28, P.z + pbR.z * s * 1.05).project(camera);
    el.style.left = clamp((pbV.x * 0.5 + 0.5) * viewW, 42, viewW - 42).toFixed(1) + 'px'; el.style.top = ((0.5 - pbV.y * 0.5) * viewH).toFixed(1) + 'px';
  }
  const sr = stage.getBoundingClientRect();
  // (portrait: Friends stands lower in its column, clear of the logo, just over the spot at your right)
  { const fb = $('friendsBtn'), col = $('lobbyRight'); if (fb && col && fb.offsetParent !== null) { let dy = 0;
    if (viewH > viewW && !slotR.hidden) { const natTop = col.getBoundingClientRect().top - sr.top + fb.offsetTop, h = fb.offsetHeight || 62, slotTop = parseFloat(slotR.style.top) - (slotR.offsetHeight || 46) / 2;
      dy = Math.max(0, Math.max(slotTop - 18 - h, logoBottom() - sr.top + 42) - natTop); }
    if (Math.abs((fb._dy || 0) - dy) > 0.5) { fb._dy = dy; fb.style.setProperty('--fdy', dy.toFixed(1) + 'px'); } } }
  // the bar over your head, under the logo, between whatever stands beside it at its height (the rail's plates, Friends)
  pbV.set(P.x, P.y + charTall(myLook) + 0.07, P.z).project(camera);
  let sx = (pbV.x * 0.5 + 0.5) * viewW, sy = (0.5 - pbV.y * 0.5) * viewH - 6;
  sy = Math.max(sy, PB.top + 62) + Math.sin(clock * 1.7) * 2.2;
  const bw = pbar.offsetWidth || 216, bh = pbar.offsetHeight || 54; let lo = 10, hi = viewW - 10;
  for (const e of [...$('lobbyRail').children, $('friendsBtn')]) { if (!e || e.hidden || e.offsetParent === null) continue;
    const r = e.getBoundingClientRect(), t = r.top - sr.top - (e.id === 'friendsBtn' ? 30 : 0), b = r.bottom - sr.top + 10; if (b < sy - bh - 4 || t > sy + 4 || !(r.width > 0)) continue;
    if ((r.left + r.right) / 2 - sr.left < viewW / 2) lo = Math.max(lo, r.right - sr.left + 8); else hi = Math.min(hi, r.left - sr.left - 8); }
  const k = clamp((hi - lo) / bw, 0.7, 1), half = bw * k / 2; sx = clamp(sx, lo + half, Math.max(lo + half, hi - half));
  pbar.style.left = sx.toFixed(1) + 'px'; pbar.style.top = sy.toFixed(1) + 'px';
  const ks = k.toFixed(3); if (pbar._k !== ks) { pbar._k = ks; pbar.style.transformOrigin = '50% 100%'; pbar.style.transform = k < 0.999 ? 'translate(-50%,-100%) scale(' + ks + ')' : ''; }
}
""" + s[p1:]
rep("/* abilities: violet construction paper", "#friendsBtn{translate:0 var(--fdy,0px)}\n/* abilities: violet construction paper")
rep('<p class="ver">Version 217</p>', '<p class="ver">Version 218</p>')
open(DST, 'w').write(s)
print('ui146 ok', n0, '->', len(s))
