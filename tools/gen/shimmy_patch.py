# no more turning on the spot by magic: in Customize and on the winner screen it shimmies itself round with its stubs, and when you drag it
# round in Customize it shimmies along as you turn it
P = '/home/claude/paint-the-canvas.html'
src = open(P).read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, (n, old[:140])
    src = src.replace(old, new)

# the shimmy: a turn made in little shoves (each push of a stub moves it on), its stubs taking turns and its body rocking with them
rep("const idle = { t: 2.5, act: null, u: 0, dur: 1, sway: 0, push: 0, hop: 0, spin: 0, sq: 0, rise: 0 };",
    """const idle = { t: 2.5, act: null, u: 0, dur: 1, sway: 0, push: 0, hop: 0, spin: 0, sq: 0, rise: 0 };
// turning itself round with its stubs: it heads for tgt (radians) in little shoves, a step with each push, the stub on the outside of the
// turn pushing harder, its body rocking with each one. yaw is where it's got to; push and shove drive its stubs and its lean
const newShim = () => ({ yaw: 0, tgt: 0, vel: 0, ph: 0, push: 0, shove: 0 });
const shim = newShim();
function shimStep(S, dt) {
  dt = Math.min(dt, 0.05); const d = S.tgt - S.yaw, want = clamp(d * 4.5, -3, 3), go = Math.abs(d) > 0.004 || Math.abs(S.vel) > 0.02;
  if (go) S.ph += dt * (7 + Math.abs(want) * 2.4);
  const step = 0.35 + 0.65 * Math.pow(Math.abs(Math.sin(S.ph)), 0.7);
  S.vel += (want * step - S.vel) * Math.min(1, dt * 14); S.yaw += S.vel * dt;
  const k = clamp(Math.abs(S.vel) / 1.1, 0, 1), sg = S.vel >= 0 ? 1 : -1;
  S.push = clamp((Math.sin(S.ph) * 0.8 + 0.3 * sg) * k, -1, 1); S.shove = Math.sin(S.ph - 0.9) * k * 0.7;
}""")
# Customize: no turning by itself; dragging sets where it turns to (all the way round if you like), and it shimmies there
rep("  if (lookOpen && state === 'menu') { if (!lookDrag) lookSpin += rdt * 0.45; P.yaw = hero.yaw + Math.sin(lookSpin) * 0.95; }",
    "  if (lookOpen && state === 'menu') { shimStep(shim, rdt); P.yaw = hero.yaw + shim.yaw; P.shimNow = shim; } else if (P.shimNow === shim) P.shimNow = null;")
rep("lookName.placeholder = playerName(); lookEl.hidden = false; drop.visible = true; P.y = 0; heroT = 0; lookSpin = 0; startIntro();",
    "lookName.placeholder = playerName(); lookEl.hidden = false; drop.visible = true; P.y = 0; heroT = 0; lookSpin = 0; Object.assign(shim, newShim()); startIntro();")
rep("if (w.slot === 'back' && myLook.back) lookSpin = Math.PI / 2; });", "if (w.slot === 'back' && myLook.back) shim.tgt = Math.round(shim.tgt / 6.2832) * 6.2832 + 2.6; });")
rep("canvas.addEventListener('pointermove', e => { if (lookOpen && lookDrag && lookDrag.id === e.pointerId) { lookSpin += (e.clientX - lookDrag.x) * 0.012; lookDrag.x = e.clientX; } });",
    "canvas.addEventListener('pointermove', e => { if (lookOpen && lookDrag && lookDrag.id === e.pointerId) { shim.tgt += (e.clientX - lookDrag.x) * 0.012; lookDrag.x = e.clientX; idle.t = Math.max(idle.t, 3); } });")
# its idle bits: no spinning round; now and then it shimmies a little to one side (back toward facing you if it's been turned away)
rep("const IDLE_ACTS = [['bounce', 0.9], ['look', 1.7], ['wiggle', 1.3], ['yawn', 1.9], ['spin', 0.85], ['look', 1.7], ['bounce', 0.9], ['wiggle', 1.3]];",
    "const IDLE_ACTS = [['bounce', 0.9], ['look', 1.7], ['wiggle', 1.3], ['yawn', 1.9], ['shimmy', 1.2], ['look', 1.7], ['bounce', 0.9], ['shimmy', 1.2]];")
rep("if (idle.act === 'yawn') emote(P, 'yawn', a[1]); } }",
    "if (idle.act === 'yawn') emote(P, 'yawn', a[1]); if (idle.act === 'shimmy') { const home = Math.round(shim.tgt / 6.2832) * 6.2832, off = shim.tgt - home; shim.tgt = Math.abs(off) > 0.8 ? shim.tgt - Math.sign(off) * (0.55 + Math.random() * 0.25) : home + clamp(off + (Math.random() < 0.5 ? -1 : 1) * (0.35 + Math.random() * 0.25), -0.7, 0.7); } } }")
rep("      else if (idle.act === 'spin') { idle.spin = u * u * (3 - 2 * u) * 6.2832; idle.hop = Math.sin(u * Math.PI) * 0.22; idle.sq = u > 0.9 ? 0.3 : 0; }\n", "")
# picking a color: it hops for joy (no spin)
rep("if (D === P && menuReact > 0) { const u = 1 - menuReact / 0.7; hop = Math.sin(u * Math.PI) * 0.6; spinY = u * 6.2832; sq = u > 0.85 ? (u - 0.85) / 0.15 * 0.5 : 0; rise = u < 0.4 ? 0.7 : 0; }",
    "if (D === P && menuReact > 0) { const u = 1 - menuReact / 0.7; hop = Math.sin(u * Math.PI) * 0.6; sq = u > 0.85 ? (u - 0.85) / 0.15 * 0.5 : 0; rise = u < 0.4 ? 0.7 : 0; }")
# the winner screen: happy hops, and between them a shimmy one way then the other (no spinning round)
rep("    if (vic.happy && c < 0.64) { const u = c / 0.64; hop = Math.sin(u * Math.PI) * 0.6; spin = (1 - Math.cos(u * Math.PI)) * Math.PI; sq = u > 0.88 ? (u - 0.88) * 3 : 0; rise = u < 0.45 ? 0.6 : 0; }",
    "    if (vic.happy && c < 0.64) { const u = c / 0.64; hop = Math.sin(u * Math.PI) * 0.6; sq = u > 0.88 ? (u - 0.88) * 3 : 0; rise = u < 0.45 ? 0.6 : 0; }")
rep("  vic.feat.forEach((D, i) => { D.vicPose = vicPose(i, t); });",
    """  vic.feat.forEach((D, i) => { D.vicPose = vicPose(i, t); const S = D.shim || (D.shim = newShim()), tt = t - 0.1 - i * 0.14, cyc = Math.floor((tt - 0.78 - 0.9) / 2.7);
    S.tgt = cyc >= 0 ? (cyc % 2 ? 0.34 : -0.34) * (vic.happy ? 1 : 0.6) : 0; shimStep(S, rdt); D.vicPose.spin = S.yaw; D.shimNow = S; });""")
rep("function restoreVictory() {\n  for (const s0 of vic.saved) { const D = s0.D; Object.assign(D, { x: s0.x, y: s0.y, z: s0.z, yaw: s0.yaw, st: s0.st, paint: s0.paint, power: s0.power }); D.vicPose = null;",
    "function restoreVictory() {\n  for (const s0 of vic.saved) { const D = s0.D; Object.assign(D, { x: s0.x, y: s0.y, z: s0.z, yaw: s0.yaw, st: s0.st, paint: s0.paint, power: s0.power }); D.vicPose = null; D.shim = null; if (D.shimNow !== shim) D.shimNow = null;")
# its stubs and lean: the wiggle's and the shimmy's together
rep("D.yaw + spinY, D === P && idle.sway ? idle.sway * 0.06 : 0);", "D.yaw + spinY, (D === P && idle.sway ? idle.sway * 0.06 : 0) + (D.shimNow ? D.shimNow.shove * 0.05 : 0));")
rep("shove: D === P ? idle.sway : 0, push: D === P ? idle.push : 0,", "shove: clamp((D === P ? idle.sway : 0) + (D.shimNow ? D.shimNow.shove : 0), -1, 1), push: clamp((D === P ? idle.push : 0) + (D.shimNow ? D.shimNow.push : 0), -1, 1),")
open(P, 'w').write(src)
print('ok')
