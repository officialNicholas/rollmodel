#!/usr/bin/env python3
"""The results painting is a print of the canvas: the stage's own floor texture laid flat, the holes cut out, the blocks and ramps raised on it, and the paint splattered over it where it landed, each side's colour with a darker rim. A beat after the results come up the camera clicks: a flash in the frame, the shutter, and the print fades in over the live view. On top of ui66_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui66_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

# the picture inside the frame, and the flash
rep('<div class="gframe" id="gframe" hidden aria-hidden="true"><div class="gplac" id="gPlac">', '<div class="gframe" id="gframe" hidden aria-hidden="true"><img class="gpic" id="gpic" alt="" hidden><span class="gflash" aria-hidden="true"></span><div class="gplac" id="gPlac">')
# the sound
rep("    kpart() { if (!P_('kpart', { vary: 0.03 })) api.whoosh(); },", "    kpart() { if (!P_('kpart', { vary: 0.03 })) api.whoosh(); },\n    shutter() { if (!P_('shutter', { vary: 0.02 })) api.tick(); },")
# the print
rep("let snapRT = null;\n", r'''// ---------- the print of the canvas: the stage's floor laid flat with the paint splattered over it where it landed ----------
function paintingArt(S, aspect) {
  S = S || 1024; aspect = aspect || 1; const W = aspect >= 1 ? S : Math.round(S * aspect), Hh = aspect >= 1 ? Math.round(S / aspect) : S, c = document.createElement('canvas'); c.width = W; c.height = Hh; const g = c.getContext('2d'), A = ARENA + 0.8, k = Math.min(W, Hh) / (2 * A), X = x => W / 2 + x * k, Z = z => Hh / 2 - z * k; // (fitted to the frame; north, where the rivals start, at the top)
  const css = h => '#' + (h | 0).toString(16).padStart(6, '0'), T = TH, M = themeMats(T), tex = M.floor.map && M.floor.map.image, us = T.uv || 0.25;
  g.fillStyle = css(T.sea ? T.low : (T.low !== undefined ? T.low : 0x1C1238)); g.fillRect(0, 0, W, Hh);
  const shapeOf = (r, m) => { if (r[6] === 'c') { const cx = (r[0] + r[1]) / 2, cz = (r[2] + r[3]) / 2, rr = (r[1] - r[0]) / 2 + (m || 0); g.moveTo(X(cx) + rr * k, Z(cz)); g.arc(X(cx), Z(cz), rr * k, 0, 6.2832); } else { const m0 = m || 0; g.rect(X(r[0] - m0), Z(r[3] + m0), (r[1] - r[0] + 2 * m0) * k, (r[3] - r[2] + 2 * m0) * k); } };
  const pat = tex ? g.createPattern(tex, 'repeat') : null; if (pat && pat.setTransform) { const sc = k / us / tex.width; pat.setTransform(new DOMMatrix([sc, 0, 0, sc, X(0), Z(0)])); }
  const floorFill = (tint, dark) => { if (pat) { g.fillStyle = pat; g.fill(); } g.globalCompositeOperation = 'multiply'; g.fillStyle = css(tint); g.fill(); g.globalCompositeOperation = 'source-over'; if (dark) { g.fillStyle = 'rgba(0,0,0,' + dark + ')'; g.fill(); } };
  // the floor, with the holes cut out
  g.save(); g.beginPath(); g.rect(X(-ARENA), Z(ARENA), 2 * ARENA * k, 2 * ARENA * k); for (const h of HOLES) shapeOf(h); g.clip('evenodd'); g.beginPath(); g.rect(0, 0, W, Hh); floorFill(T.ft, 0); g.restore();
  // the edge of the floor, and of each hole: a dark lip
  g.save(); g.lineWidth = Math.max(2, 0.14 * k); g.strokeStyle = 'rgba(0,0,0,.4)'; g.beginPath(); g.rect(X(-ARENA), Z(ARENA), 2 * ARENA * k, 2 * ARENA * k); for (const h of HOLES) shapeOf(h); g.stroke(); g.restore();
  // the blocks and ramps raised on it: lighter on top, a shadow down their south side
  for (const b of BOXES.slice().sort((p, q) => p[5] - q[5])) { g.save(); g.beginPath(); shapeOf(b, 0.1); g.fillStyle = 'rgba(0,0,0,.35)'; g.translate(0.18 * k, 0.26 * k); g.fill(); g.restore(); g.save(); g.beginPath(); shapeOf(b); g.clip(); g.beginPath(); g.rect(0, 0, W, Hh); floorFill(M.top ? Math.min(0xFFFFFF, T.ft) : T.ft, 0); g.restore(); g.save(); g.beginPath(); shapeOf(b); g.lineWidth = Math.max(1.5, 0.1 * k); g.strokeStyle = 'rgba(0,0,0,.45)'; g.stroke(); g.restore(); }
  for (const r of RAMPS) { g.save(); g.beginPath(); shapeOf(r); g.clip(); g.beginPath(); g.rect(0, 0, W, Hh); floorFill(T.st, 0.12); g.restore(); }
  // the paint: every painted sample a soft splat in its side's colour, a darker rim under them all so each colour reads as one shape
  const rr = 0.38 * k, cols = TEAMS.map(t => css(t.wet)), rims = TEAMS.map(t => css(t.dry));
  for (const pass of [0, 1]) for (let t = 0; t < 3; t++) { g.fillStyle = pass ? cols[t] : rims[t]; for (let i = 0; i < NS; i++) { const v = painted[i]; if (!v || (v - 1) % 3 !== t) continue; const dil = v > 3, r = (pass ? rr : rr + 0.14 * k) * (dil ? 0.8 : 1) * (0.92 + 0.16 * ((i * 7919) % 13) / 13); g.globalAlpha = dil ? (pass ? 0.6 : 0.5) : 1; g.beginPath(); g.arc(X(sX[i]), Z(sZ[i]), r, 0, 6.2832); g.fill(); } }
  // stray drops flung out round the paint
  for (let i = 0; i < NS; i += 7) { const v = painted[i]; if (!v) continue; const t = (v - 1) % 3, h1 = ((i * 2654435761) >>> 0) / 4294967296, h2 = ((i * 40503 + 7) * 2246822519 >>> 0) / 4294967296, a = h1 * 6.2832, d = (0.55 + h2 * 0.9) * k; g.fillStyle = cols[t]; g.globalAlpha = v > 3 ? 0.6 : 1; g.beginPath(); g.arc(X(sX[i]) + Math.cos(a) * d, Z(sZ[i]) + Math.sin(a) * d, (0.07 + 0.09 * h2) * k, 0, 6.2832); g.fill(); }
  g.globalAlpha = 1;
  // a wet shine across the paint, and the paper's grain over it all
  g.globalCompositeOperation = 'overlay'; const sh = g.createLinearGradient(0, 0, W, Hh); sh.addColorStop(0, 'rgba(255,255,255,.18)'); sh.addColorStop(0.5, 'rgba(255,255,255,0)'); sh.addColorStop(1, 'rgba(0,0,0,.12)'); g.fillStyle = sh; g.fillRect(0, 0, W, Hh); g.globalCompositeOperation = 'source-over';
  return c;
}
let shotT = null;
function takeShot() {
  shotT = null; if (state !== 'dead' || end.hidden) return; const gf = $('gframe'), img = $('gpic');
  const bw = img.clientWidth || gf.clientWidth, bh = img.clientHeight || gf.clientHeight, aspect = bw > 0 && bh > 0 ? clamp(bw / bh, 0.5, 2) : 1;
  try { img.src = paintingArt(1024, aspect).toDataURL('image/jpeg', 0.9); } catch (e) { return; }
  img.hidden = false; gf.classList.remove('shot'); void gf.offsetWidth; gf.classList.add('shot'); AU.shutter(); buzz(12);
}
function clearShot() { if (shotT) clearTimeout(shotT); shotT = null; const gf = $('gframe'), img = $('gpic'); gf.classList.remove('shot'); img.hidden = true; img.removeAttribute('src'); }
let snapRT = null;
''')
rep("  $('pMeta').textContent = TH.label + ', ' + fmtTime(info.time); $('gpT').textContent = $('pTitle').textContent; $('gpM').textContent = 'Paint on canvas. ' + TH.label + ', ' + fmtTime(info.time);",
    "  $('pMeta').textContent = TH.label + ', ' + fmtTime(info.time); $('gpT').textContent = $('pTitle').textContent; $('gpM').textContent = 'Paint on canvas. ' + TH.label + ', ' + fmtTime(info.time);\n  clearShot(); shotT = setTimeout(takeShot, 1100); // (a beat after the frame hangs, the camera clicks)")
rep("  $('gframe').hidden = true; $('gwall').hidden = true; pickRivalNames();", "  clearShot(); $('gframe').hidden = true; $('gwall').hidden = true; pickRivalNames();")
rep("  $('gframe').hidden = true; $('gwall').hidden = true;\n", "  clearShot(); $('gframe').hidden = true; $('gwall').hidden = true;\n")
css = '''
/* the print in the frame, and the flash as it is taken */
.gframe .gpic{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;opacity:0;transform:scale(1.03);transition:opacity .45s ease .12s,transform .6s cubic-bezier(.2,.9,.3,1) .12s}
.gframe .gpic[hidden]{display:none}
.gframe.shot .gpic{opacity:1;transform:none}
.gframe .gflash{position:absolute;inset:0;background:#fff;opacity:0;pointer-events:none}
.gframe.shot .gflash{animation:gflash .55s ease-out both}
@keyframes gflash{0%{opacity:1}30%{opacity:.85}100%{opacity:0}}
@media (prefers-reduced-motion:reduce){.gframe .gpic{transition:none}.gframe.shot .gflash{animation:none}}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
