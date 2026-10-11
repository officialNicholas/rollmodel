#!/usr/bin/env python3
"""v193: on an upright screen the fight card stacks the fighters in full-width rows (one above the other) instead of narrow columns,
and each one is shot close on the face, so nobody's cut off and you see who you're up against."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui117_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# a face shot: aimed at the head, close, a touch above eye level (a tall hat still gets most of itself in)
rep("const tv = Math.tan(portCam.fov * Math.PI / 360), d = tall / (2 * tv * (o.zoom || 0.8)), ly = tall * 0.46,",
    "const tv = Math.tan(portCam.fov * Math.PI / 360), d = o.face ? (0.84 + (tall - 0.92) * 0.6) / (2 * tv * Math.min(1, W / Hh / 1.25)) : tall / (2 * tv * (o.zoom || 0.8)), ly = o.face ? 0.5 + (tall - 0.92) * 0.4 : tall * 0.46,")
rep("for (const [D, el, pose] of q.list) { if (!el) continue; const c = portraitOf(D, 600, 720, pose); el.replaceChildren(c); }",
    "{ const rows = $('vsRow').classList.contains('rows'); for (const [D, el, pose] of q.list) { if (!el) continue; const r = el.getBoundingClientRect(), fw = 720, fh = Math.max(240, Math.min(900, Math.round(fw * (r.height || 360) / (r.width || 480)))); /* (the shot takes the row's own shape: nothing cropped) */\n      const c = rows ? portraitOf(D, fw, fh, Object.assign({}, pose, { face: true, yaw: 0 })) : portraitOf(D, 600, 720, pose); el.replaceChildren(c); } }")
rep("$('vsRow').innerHTML = h; $('vsRow').classList.toggle('trio', mode === 'trio');",
    "$('vsRow').innerHTML = h; $('vsRow').classList.toggle('trio', mode === 'trio'); $('vsRow').classList.toggle('rows', viewH > viewW && mode !== 'solo'); /* (upright: one fighter per row, shot on the face) */")
rep("\n</style>\n", """
.vsx .vsrow.rows{flex-direction:column;bottom:20%}
.vsrow.rows .vcol{animation-name:rowin}
.vsrow.rows .vcol.foe,.vsrow.rows .vcol.foe2{animation-name:rowinr}
@keyframes rowin{from{transform:translateX(-100%)}}
@keyframes rowinr{from{transform:translateX(100%)}}
.vsrow.rows .vcol+.vcol{box-shadow:0 -4px 0 var(--cream),0 -9px 14px rgba(0,0,0,.35)}
.vsrow.rows .vseam{display:none}
.vsrow.rows .vhead{position:absolute;left:0;top:0;min-height:0;padding:9px 18px 8px 14px;justify-items:start;text-align:left;border-radius:0 0 14px 0}
.vsrow.rows .vcol.foe .vhead,.vsrow.rows .vcol.foe2 .vhead{left:auto;right:0;justify-items:end;text-align:right;border-radius:0 0 0 14px;padding:9px 14px 8px 18px}
.vsrow.rows .vhead b{font-size:clamp(20px,7vw,32px)}
.vsrow.rows .vhead::after{right:auto;left:auto;top:4px;width:36px;height:36px}
.vsx .vsrow.rows .vcol .vbox,.vsx .vsrow.rows.trio .vcol .vbox{left:0;top:0;right:0;bottom:0;width:auto;height:auto;aspect-ratio:auto;transform:none;margin:0;animation:figrow .6s .18s cubic-bezier(.2,1.2,.35,1) both}
.vsrow.rows .vcol .vbox canvas{object-fit:cover;object-position:50% 50%}
@keyframes figrow{from{opacity:0;transform:scale(1.08)}}
.vsrow.rows.trio .vhead b{font-size:clamp(16px,5.6vw,26px)}
</style>
""")
rep('<p class="ver">Version 192</p>', '<p class="ver">Version 193</p>')
open(DST, 'w').write(s)
print('ui118 ok', n0, '->', len(s))
