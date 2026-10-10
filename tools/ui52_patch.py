#!/usr/bin/env python3
"""Knocked out, the Splatoon way: the paint of whoever got you floods the screen, a badge says who with the count to your comeback, and when you come back the paint parts round a ragged hole to show your spawn. On top of ui51_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui51_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

rep('  <div class="hud off" id="hud">', '''  <div class="kof" id="kof" hidden aria-live="polite"><canvas id="kofC" aria-hidden="true"></canvas><div class="kofb"><small id="kofSmall">Splatted by</small><b id="kofBy"></b><span class="kofn" id="kofN">3</span><i>Respawn</i></div></div>
  <div class="hud off" id="hud">''')
rep("  if (D === P) { drop.visible = false; shadowBlob.visible = false; AU.roll(0, 0); hold = 0.08; slow = 0.35; shake = 0.4; buzz([40, 30, 40]); banner((reason === 'fall' && by ? 'Knocked off!' : koLine(reason, true)) || 'Out!'); }",
    "  if (D === P) { drop.visible = false; shadowBlob.visible = false; AU.roll(0, 0); hold = 0.08; slow = 0.35; shake = 0.4; buzz([40, 30, 40]); kofStart(D, reason, by); }")
rep("  if (D === P) { drop.visible = true; camYaw = bestYaw; camYawV = 0; AU.flip(); flashScreen(); hintEl.classList.remove('on'); }",
    "  if (D === P) { drop.visible = true; camYaw = bestYaw; camYawV = 0; camSnap = true; AU.flip(); if (kof) kofOpen(); else flashScreen(); hintEl.classList.remove('on'); }")
rep("    const kt = P.st === 'ko' ? 'Back in ' + Math.max(1, Math.ceil(P.koT)) : '';", "    const kt = P.st === 'ko' && !kof ? 'Back in ' + Math.max(1, Math.ceil(P.koT)) : '';")
rep("  if (tal) talFrame();\n", "  if (tal) talFrame();\n  if (kof) kofFrame(rdt);\n")
rep("function resetRun() {\n  abortVictory();", "function resetRun() {\n  abortVictory(); kofEnd();")
rep("function abortVictory() {", r'''// ---------- knocked out: the paint of whoever got you floods the screen, a badge says who with the count to your comeback, and when
// you come back the paint parts round a ragged hole to show where ----------
const kofEl = $('kof'), kofC = $('kofC'), kofG = kofC.getContext('2d'); let kof = null;
function kofStart(D, reason, by) {
  const col = by ? TEAMS[by.team].css : reason === 'sun' ? '#F0DDA8' : reason === 'dry' ? '#5E4F5C' : hexCss(new THREE.Color(TEAMS[D.team].wet).multiplyScalar(0.5).getHex());
  kof = { ph: 'in', t: 0, col, cx: viewW * 0.5, cy: viewH * 0.5, seed: Math.random() * 100 };
  $('kofSmall').textContent = by ? 'Splatted by' : reason === 'fall' ? 'Fell off' : reason === 'sun' ? 'Baked' : reason === 'dry' ? 'Dried up' : 'Knocked out';
  $('kofBy').textContent = by ? nameOf(by) : (koLine(reason, true) || 'Out!'); $('kofN').textContent = Math.max(1, Math.ceil(D.koT));
  kofEl.style.setProperty('--kc', col); kofEl.hidden = false; kofEl.classList.remove('badge', 'out');
}
function kofBlob(g, r, ph) { for (let i = 0; i <= 56; i++) { const a = i / 56 * 6.2832, rr = r * (1 + 0.08 * Math.sin(a * 5 + ph) + 0.05 * Math.sin(a * 9 - ph * 1.7) + 0.03 * Math.sin(a * 17 + ph * 0.6)), x = kof.cx + Math.cos(a) * rr, y = kof.cy + Math.sin(a) * rr; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.closePath(); }
function kofFrame(rdt) {
  if (!kof) return; kof.t += rdt; const W = viewW, Hh = viewH, dpr = Math.min(2, window.devicePixelRatio || 1), g = kofG, t = kof.t, R = Math.hypot(W, Hh) * 0.6;
  if (kofC.width !== (W * dpr | 0) || kofC.height !== (Hh * dpr | 0)) { kofC.width = W * dpr | 0; kofC.height = Hh * dpr | 0; }
  g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, Hh);
  if (kof.ph === 'in') { const u = Math.min(1, t / 0.5), e = 1 - Math.pow(1 - u, 3); g.fillStyle = kof.col; g.beginPath(); kofBlob(g, R * e * 1.15, kof.seed + t * 2); g.fill(); if (u >= 1) { kof.ph = 'hold'; kofEl.classList.add('badge'); } }
  else if (kof.ph === 'hold') { g.fillStyle = kof.col; g.fillRect(0, 0, W, Hh); g.globalAlpha = 0.1; g.fillStyle = '#000'; for (let k = 0; k < 3; k++) { g.beginPath(); g.ellipse(W * (0.25 + 0.25 * k) + Math.sin(t * 0.6 + k) * 50, Hh * (0.42 + 0.14 * Math.sin(t * 0.45 + k * 2)), W * 0.34, Hh * 0.11, 0.25 * k - 0.3, 0, 6.2832); g.fill(); } g.globalAlpha = 1; } // (a slow swirl of darker paint)
  else { const u = Math.min(1, t / 0.65), e = u * u * (3 - 2 * u); g.fillStyle = kof.col; g.fillRect(0, 0, W, Hh);
    g.globalCompositeOperation = 'destination-out'; g.beginPath(); kofBlob(g, R * e * 1.25, kof.seed + t * 3); g.fill(); g.globalCompositeOperation = 'source-over';
    if (u < 1) { g.strokeStyle = 'rgba(0,0,0,.2)'; g.lineWidth = 9; g.beginPath(); kofBlob(g, R * e * 1.25, kof.seed + t * 3); g.stroke(); } else return kofEnd(); }
  if (kof.ph !== 'out') { const n = String(Math.max(1, Math.ceil(P.koT))); const el = $('kofN'); if (el.textContent !== n) { el.textContent = n; restartCls(el, 'tick'); } }
}
function kofOpen() { if (!kof) return; kof.ph = 'out'; kof.t = 0; kofEl.classList.remove('badge'); kofEl.classList.add('out'); AU.splat(0.9); }
function kofEnd() { kof = null; kofEl.hidden = true; kofEl.classList.remove('badge', 'out'); }
function abortVictory() {''')
css = '''
/* knocked out: the flood of paint and the badge */
.kof{position:absolute;inset:0;pointer-events:none}
.kof canvas{position:absolute;inset:0;width:100%;height:100%;display:block}
.kofb{position:absolute;left:50%;top:46%;transform:translate(-50%,-50%) scale(.5);opacity:0;display:grid;justify-items:center;gap:8px;text-align:center;transition:opacity .25s,transform .4s cubic-bezier(.3,1.5,.5,1)}
.kof.badge .kofb{opacity:1;transform:translate(-50%,-50%)}
.kofb small{font:800 12px/1 var(--font-ui);letter-spacing:.14em;text-transform:uppercase;color:#fff;padding:7px 13px;border-radius:99px;background:rgba(23,19,32,.6)}
.kofb b{font:400 clamp(36px,11vw,68px)/1 var(--font-display);color:#fff;text-shadow:.05em .06em 0 var(--black),calc(.05em + 3px) calc(.06em + 3px) 0 rgba(0,0,0,.35);max-width:90vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.kofn{display:grid;place-items:center;width:66px;height:66px;margin-top:6px;border-radius:50%;background:#fff;color:var(--black);border:3px solid var(--black);box-shadow:4px 4px 0 var(--black);font:400 32px/1 var(--font-display)}
.kofn.tick{animation:tick .22s ease-out}
.kofb i{font:800 11px/1 var(--font-ui);letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.85);font-style:normal}
@media (max-height:520px) and (min-aspect-ratio:1/1){.kofb{gap:5px}.kofb b{font-size:min(60px,13vh)}.kofn{width:52px;height:52px;font-size:26px;margin-top:2px}}
@media (prefers-reduced-motion:reduce){.kofb{transition:none}.kofn.tick{animation:none}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
