#!/usr/bin/env python3
"""v208: the axolotl is the character. Its runtime (tools/assets/axo_embed.js, made by tools/mk_axo_embed.py from the axolotl pipeline's
axo.js) and the stand-in that answers the slime's calls (tools/assets/axoc.js) go in after the slime; its two bodies load from
axo-pack.txt (tools/mk_axo_pack.py), and the slime's pack is only fetched if that never arrives. Everything that made, drove or dressed
the slime asks whichever one the blob wears."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui133_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
embed = open(S + '/tools/assets/axo_embed.js').read(); axoc = open(S + '/tools/assets/axoc.js').read()
assert '</script>' not in embed and '</script>' not in axoc
# the runtime and the stand-in after the slime; the axolotl's pack first, the slime's only if it never comes
rep("  return { S, load, make, update, EXPR, headTop, headSize, bodyPoint, SCALE_K };\n})();",
    "  return { S, load, make, update, EXPR, headTop, headSize, bodyPoint, SCALE_K, get headR0() { return S.meta ? S.meta.slime.head[3] : 0.425; } };\n})();")
rep("const slimeLoad = SLIME.load(window.SLIME_PACK || 'slime-pack.txt').catch(e => { SLIME.S.failed = true; console.warn('slime pack:', e && e.message); });",
    embed + axoc +
    "const axoLoad = AXOC.load(window.AXO_PACK || 'axo-pack.txt').catch(e => { AXOC.S.failed = true; console.warn('axolotl pack:', e && e.message); });\n"
    "// (the slime only comes in if the axolotl never arrives)\n"
    "const slimeLoad = axoLoad.then(() => AXOC.S.ready ? null : SLIME.load(window.SLIME_PACK || 'slime-pack.txt')).catch(e => { SLIME.S.failed = true; console.warn('slime pack:', e && e.message); });")
# making one, attaching them, and the menu noticing they've arrived
rep("  const I = SLIME.make({ color }); I.root.visible = false; V.body.add(I.root);", "  const I = (AXOC.S.ready ? AXOC : SLIME).make({ color }); I.root.visible = false; V.body.add(I.root);")
rep("  if (!SLIME.S.ready || VP.slime) return;", "  if (!(AXOC.S.ready || SLIME.S.ready) || VP.slime) return;")
rep("  if (SLIME.S.ready && !VP.slime && booted && state === 'menu' && !lookOpen && !irisBusy) { attachSlimes(); queueWarm(); }",
    "  if ((AXOC.S.ready || SLIME.S.ready) && !VP.slime && booted && state === 'menu' && !lookOpen && !irisBusy) { attachSlimes(); queueWarm(); }")
# driving it: the blob goes along so the axolotl can see what it's up to
rep("  SLIME.update(I, o);\n", "  o.D = D; (I.kind === 'axo' ? AXOC : SLIME).update(I, o);\n")
# dressing it: the head's place and size, and the throat, from whichever it is
rep("    const hs = SLIME.headSize(SI) * 1.3; SLIME.headTop(SI, tv3, wearQ);", "    const CH = SI.kind === 'axo' ? AXOC : SLIME, hs = CH.headSize(SI) * 1.3; CH.headTop(SI, tv3, wearQ);")
rep("    const plain = SI.form === 'slime' && !SI.st.formNext, mk = SLIME.headSize(SI) / SLIME.S.meta.slime.head[3];", "    const plain = SI.form === 'slime' && !SI.st.formNext, mk = CH.headSize(SI) / CH.headR0;")
rep("    if (W.glasses.visible || W.hockey.visible || W.flower.visible) { SLIME.headTop(SI, wv1, wq1, 0);", "    if (W.glasses.visible || W.hockey.visible || W.flower.visible) { CH.headTop(SI, wv1, wq1, 0);")
rep("    if (W.bow.visible && SLIME.bodyPoint(SI, 0, -0.03, 0.835, wv1)) {", "    if (W.bow.visible && CH.bodyPoint(SI, 0, -0.03, 0.835, wv1)) {")
rep("    if (W.pearls.visible && SLIME.bodyPoint(SI, 0, -0.03, 0.835, wv1)) {", "    if (W.pearls.visible && CH.bodyPoint(SI, 0, -0.03, 0.835, wv1)) {")
# framing it in the menus: how tall it stands with what's on its head (the axolotl on all fours is lower than the slime, its head bigger, so
# a hat adds more)
TALL = "myLook.head === 'hat' ? 1.25 : myLook.head === 'tophat' ? 1.18 : myLook.head === 'tiara' ? 1.05 : myLook.head === 'pirate' ? 1.12 : myLook.head ? 1.05 : 0.88"
rep(TALL, "charTall(myLook)", 2)
rep("function lookFrame() {", """function charTall(look) {
  const t = look.head === 'hat' ? 1.25 : look.head === 'tophat' ? 1.18 : look.head === 'tiara' ? 1.05 : look.head === 'pirate' ? 1.12 : look.head ? 1.05 : 0.88;
  return VP.slime && VP.slime.kind === 'axo' ? 0.7 + (t - 0.88) * 1.59 : t;
}
function lookFrame() {""")
# the rocket's pack on its back (the axolotl stands up to ride it), and the victory shot pulled back to fit it standing up
rep("  if (V.rk && V.rk.visible) V.rk.position.set(0, 0.3, -0.62);", "  if (V.rk && V.rk.visible) { if (I.kind === 'axo') { AXOC.backPoint(I, V.rk.position); V.rk.scale.multiplyScalar(1.45); } else V.rk.position.set(0, 0.3, -0.62); } // (the axolotl's bigger: a bigger pack)")
rep("land ? 0 : 0.5 / (tv * (vic.room || 1))) * (1.07 - 0.07 * Math.min(1, t / 4)), a = vic.yaw + Math.sin(t * 0.4) * 0.05;",
    "land ? 0 : 0.5 / (tv * (vic.room || 1))) * (1.07 - 0.07 * Math.min(1, t / 4)) * vk, a = vic.yaw + Math.sin(t * 0.4) * 0.05;")
rep("  let mx = 0, mz = 0, my = 0; for (const D of vic.feat) { mx += D.x; mz += D.z; my += D.y; } const n = vic.feat.length; mx /= n; mz /= n; my /= n;",
    "  let mx = 0, mz = 0, my = 0; for (const D of vic.feat) { mx += D.x; mz += D.z; my += D.y; } const n = vic.feat.length; mx /= n; mz /= n; my /= n;\n  const vk = VP.slime && VP.slime.kind === 'axo' ? 1.38 : 1; // (the axolotl celebrates standing up: taller than the slime)")
rep("vicCam.position.set(mx + Math.sin(a) * dist, my + 0.3, mz + Math.cos(a) * dist); vicCam.lookAt(mx, my + 0.44, mz);",
    "vicCam.position.set(mx + Math.sin(a) * dist, my + 0.3 * vk, mz + Math.cos(a) * dist); vicCam.lookAt(mx, my + 0.44 * vk, mz);")
rep('<p class="ver">Version 207</p>', '<p class="ver">Version 208</p>')
open(DST, 'w').write(s)
print('ui134 ok', n0, '->', len(s))
