#!/usr/bin/env python3
"""v222: the versus card's portraits. Each face is shot on a long lens from well back (a portrait lens, not a wide one up close), so it
reads flat and true instead of bulging; the see-through copy each axolotl keeps for being seen behind walls is put away for the shot (up
close it showed its own far side through its face); and each face is set in what its panel actually shows: under its name plate, clear of
the title band at the foot of the card, a little away from the plate's side, sized with room for whatever is on its head."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui149_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# the lens and the framing: a framed face (o.fd: how much of the shot's height it fills, o.fx / o.fy: where its middle goes) on a 13 degree
# lens from well back, aimed at the head itself; the whole-body shots on a longer lens than before too
rep("  const tv = Math.tan(portCam.fov * Math.PI / 360), d = o.face ?",
    "  const SI = (vOf(D) || {}).slime, VB = (vOf(D) || {}).body, faceShot = !!(o.fd && SI && SI.kind === 'axo' && VB);\n"
    "  portCam.fov = faceShot ? 13 : 22;\n"
    "  const tv = Math.tan(portCam.fov * Math.PI / 360), d = o.face ?")
rep("  portCam.aspect = W / Hh; portCam.updateProjectionMatrix(); portCam.position.set(D.x + fx * d, ly + d * (0.2 - 0.3 * low), D.z + fz * d); portCam.up.set(0, 1, 0); portCam.lookAt(D.x, ly - 0.03 + 0.1 * low, D.z); portCam.updateMatrixWorld();",
    "  portCam.aspect = W / Hh; portCam.updateProjectionMatrix(); portCam.position.set(D.x + fx * d, ly + d * (0.2 - 0.3 * low), D.z + fz * d); portCam.up.set(0, 1, 0); portCam.lookAt(D.x, ly - 0.03 + 0.1 * low, D.z); portCam.updateMatrixWorld();\n"
    "  if (faceShot) { // (the head: its middle and size in the world, the way its face points; framed from the chin to the top of whatever it wears)\n"
    "    SI.root.updateWorldMatrix(true, true); VB.updateWorldMatrix(true, false); const hq = new THREE.Quaternion(), hc = AXOC.headTop(SI, new THREE.Vector3(), hq, 0).applyMatrix4(VB.matrixWorld);\n"
    "    const ws = VB.getWorldScale(new THREE.Vector3()).y, Rw = AXOC.headSize(SI) * ws, fw = new THREE.Vector3(0, 0, 1).applyQuaternion(hq).applyQuaternion(VB.getWorldQuaternion(new THREE.Quaternion()));\n"
    "    const hatK = look.head === 'hat' ? 1.5 : look.head === 'tophat' ? 1.45 : look.head === 'pirate' ? 1.32 : look.head === 'bunny' ? 1.4 : look.head ? 1.24 : 1.08, ext = Rw * hatK, cy = hc.y + Rw * (hatK - 1);\n"
    "    const dist = ext / (o.fd * tv), a = Math.atan2(fw.x, fw.z) + (o.turn || 0), el = 0.06;\n"
    "    portCam.position.set(hc.x + Math.sin(a) * Math.cos(el) * dist, cy + Math.sin(el) * dist, hc.z + Math.cos(a) * Math.cos(el) * dist); portCam.lookAt(hc.x, cy, hc.z);\n"
    "    portCam.setViewOffset(W, Hh, (0.5 - o.fx) * W, (0.5 - o.fy) * Hh, W, Hh); portCam.updateMatrixWorld(); }")
# the see-through copies away for the shot (up close one shows the axolotl's own far side through its face)
rep("  for (const o of [P, H, H2]) vicLayer(o, o === D);\n  const shWas = lobbyShadow.visible,",
    "  for (const o of [P, H, H2]) vicLayer(o, o === D);\n"
    "  const ghosts = []; for (const o of [P, H, H2]) { const s2 = o && (vOf(o) || {}).slime; if (s2 && s2.ax && s2.ax.ghosts) for (const g of s2.ax.ghosts) { ghosts.push([g, g.visible]); g.visible = false; } }\n"
    "  const shWas = lobbyShadow.visible,")
rep("  lobbyShadow.visible = shWas; strand.visible = stWas; for (const o of [P, H, H2]) vicLayer(o, o === P && state === 'menu');",
    "  lobbyShadow.visible = shWas; strand.visible = stWas; for (const o of [P, H, H2]) vicLayer(o, o === P && state === 'menu'); for (const [g, v] of ghosts) g.visible = v; portCam.clearViewOffset();")
# each face set in what its panel shows: under the name plate, above the title band, a little away from the plate's side
rep("      const c = rows ? portraitOf(D, fw, fh, Object.assign({}, pose, { face: true, yaw: 0 })) : portraitOf(D, 600, 720, pose); el.replaceChildren(c); } }",
    "      let fr = null; { const col = el.closest('.vcol'); if (col) { const cr = col.getBoundingClientRect(), hd = col.querySelector('.vhead'), hr = hd && hd.getBoundingClientRect(), wide = !!(hr && hr.width > cr.width * 0.7); let bot = cr.bottom;\n"
    "        for (const b of document.querySelectorAll('#vsx .vband.bot, #vsx .vstitle')) { const br = b.getBoundingClientRect(); if (br.height > 0 && br.top < cr.bottom && br.bottom > cr.top) bot = Math.min(bot, br.top + 4); }\n"
    "        const plL = hr && hr.width ? (hr.left + hr.right) / 2 < (cr.left + cr.right) / 2 : true; let top = cr.top + (hr && hr.height ? (wide ? hr.height + 4 : hr.height * 0.35) : 0), L = cr.left, R = cr.right;\n"
    "        top = Math.max(top, r.top); bot = Math.min(bot, r.bottom); L = Math.max(L, r.left); R = Math.min(R, r.right); /* (what of the shot its panel shows) */\n"
    "        const rh = r.height || fh, rw = r.width || (rows ? fw : 600), vis = Math.max(60, bot - top), tx = L + (R - L) * (wide ? 0.5 : plL ? 0.57 : 0.43), ty = top + vis * (wide ? 0.5 : 0.54);\n"
    "        fr = { fd: Math.min(0.9, vis * (wide ? 0.4 : 0.64) / rh), fx: (tx - r.left) / rw, fy: (ty - r.top) / rh, turn: wide ? (D === P ? -0.3 : 0.3) : plL ? -0.3 : 0.3 }; } }\n"
    "      const c = rows ? portraitOf(D, fw, fh, Object.assign({}, pose, { face: true, yaw: 0 }, fr)) : portraitOf(D, 600, 720, Object.assign({}, pose, fr)); el.replaceChildren(c); } }")
# the faces finished changing for the shot: the expression each was just given is snapped to (its crossfade takes an eighth of a second,
# and the shot is two frames on, so it caught two expressions over each other), and none caught mid-blink
rep("  const q = vsSnap; if (--q.t > 0) return; vsSnap = null;",
    "  const q = vsSnap; if (--q.t > 0) { for (const [D] of q.list) { const lk = ((vOf(D) || {}).slime || {}).ax && vOf(D).slime.ax.look; if (lk) { if (lk.exprK < 1) { lk.exprK = 1; lk.expr = lk.exprB; } lk.blinkK = 0; lk.blinkT = Math.max(lk.blinkT || 0, 1.2); } } return; } vsSnap = null;")
rep('<p class="ver">Version 221</p>', '<p class="ver">Version 222</p>')
open(DST, 'w').write(s)
print('ui150 ok', n0, '->', len(s))
