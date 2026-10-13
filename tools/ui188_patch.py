#!/usr/bin/env python3
"""v248: smoother play, above all on the Sludge Sewer and the Fishing Raft. The stages' merged meshes stay indexed (each vertex shaded once,
not once per triangle), the new stages' props lose triangles nobody could see (barrel hoops as bands, small floats with fewer sides, far
scenery built coarser: tools/stage), steam stops filling the screen when the camera passes through it, and the quality tuning stops
trading notches back and forth in the middle of a match (each stage remembers the notch it needs, set during the intro)."""
import subprocess, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui187_patch.py'], check=True, env=dict(os.environ))
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)
# ---- the stage's merged meshes, kept indexed
rep("""const XA = new THREE.Vector3(1, 0, 0);
function beamGeo(""", """// mergeGeos kept indexed: where triangles share a vertex it is shaded once, not once for each of them (on the stages' round pieces a
// fifth of the vertex work), from buffers a third the size. For the stage's merged pieces, its one shadow draw and its ink hulls
function mergeIdx(list, withUV) {
  let nv = 0, ni = 0; for (const g of list) { const k = g.attributes.position.count; nv += k; ni += g.index ? g.index.count : k; }
  const pos = new Float32Array(nv * 3), nor = new Float32Array(nv * 3), uv = withUV ? new Float32Array(nv * 2) : null, idx = nv > 65535 ? new Uint32Array(ni) : new Uint16Array(ni); let o = 0, oi = 0;
  for (const g of list) { const k = g.attributes.position.count; pos.set(g.attributes.position.array.subarray(0, k * 3), o * 3); if (g.attributes.normal) nor.set(g.attributes.normal.array.subarray(0, k * 3), o * 3); if (uv && g.attributes.uv) uv.set(g.attributes.uv.array.subarray(0, k * 2), o * 2);
    if (g.index) { const I = g.index.array, n = g.index.count; for (let q = 0; q < n; q++) idx[oi + q] = I[q] + o; oi += n; } else { for (let q = 0; q < k; q++) idx[oi + q] = o + q; oi += k; }
    o += k; }
  const m = new THREE.BufferGeometry(); m.setAttribute('position', new THREE.BufferAttribute(pos, 3)); m.setAttribute('normal', new THREE.BufferAttribute(nor, 3)); if (uv) m.setAttribute('uv', new THREE.BufferAttribute(uv, 2)); m.setIndex(new THREE.BufferAttribute(idx, 1));
  return m;
}
const XA = new THREE.Vector3(1, 0, 0);
function beamGeo(""")
rep("""  for (const [mat, list] of bag) { const m = new THREE.Mesh(mergeGeos(list, true), mat); m.receiveShadow = true; m.layers.enable(3); stageGroup.add(m); if (!noCast.has(mat)) shadowG.push(m.geometry); }
  if (shadowG.length) stageGroup.add(shadowOnly(new THREE.Mesh(mergeGeos(shadowG), shadowOnlyMat))); // the whole stage casts in one draw""",
    """  for (const [mat, list] of bag) { const m = new THREE.Mesh(mergeIdx(list, true), mat); m.receiveShadow = true; m.layers.enable(3); stageGroup.add(m); if (!noCast.has(mat)) shadowG.push(m.geometry); }
  if (shadowG.length) stageGroup.add(shadowOnly(new THREE.Mesh(mergeIdx(shadowG), shadowOnlyMat))); // the whole stage casts in one draw""")
rep("""  stageGroup.add(new THREE.Mesh(mergeGeos(hulls), outlineMat));""", """  stageGroup.add(new THREE.Mesh(mergeIdx(hulls), outlineMat));""")
# ---- quality tuning without mid-match flip-flops. In a match it only ever steps down (a step up is a gamble: the frame's graphics side
# can't be seen, and a step that fails costs a hitch going up, a second of late frames and another hitch coming back). The notch a stage
# settles on is remembered, and the next match there starts at it, set during the intro where the switch can't be felt; a match that never
# had to step down lets the next one there try a notch better
rep("""const qKey = GFX + (MOBILE ? 'm' : 'd');""", """const qKey = GFX + (MOBILE ? 'm' : 'd');
let qPlayDown = false; // (stepped down during this match)
const qStage = () => { const o = store.qSt; return o && o.key === qKey && o.lv ? o.lv : (store.qSt = { key: qKey, lv: {} }).lv; };
function qMatchStart() { qPlayDown = false; try { const n = qStage()[TH.id]; if (typeof n === 'number' && n > qLvl) setQ(Math.min(n, Q_LAD.length - 1)); } catch (e) {} }
function qMatchEnd() { try { const L = qStage(), n = L[TH.id]; if (!qPlayDown && typeof n === 'number' && n > 0) { L[TH.id] = n - 1; save(); } } catch (e) {} }""")
rep("""    qDownFrom = qLvl; qDownAt = qWin; setQ(qLvl + 1); qClean = 0; qSave();""",
    """    qDownFrom = qLvl; qDownAt = qWin; setQ(qLvl + 1); qClean = 0; if (state === 'play') { qPlayDown = true; try { const L = qStage(); L[TH.id] = Math.max(L[TH.id] || 0, qLvl); } catch (e) {} } qSave();""")
rep("""    if (++qClean >= 8 && qLvl > 0 && cpuK < 0.5 && qWin >= (qBan[qLvl - 1] || 0)) { setQ(qLvl - 1); qUpAt = qWin; qClean = 0; qSave(); }""",
    """    if (++qClean >= 8 && qLvl > 0 && cpuK < 0.5 && qWin >= (qBan[qLvl - 1] || 0) && state !== 'play' && state !== 'paused') { setQ(qLvl - 1); qUpAt = qWin; qClean = 0; qSave(); }""")
rep("""  state = 'dead'; for (const D of ACTIVE) if (D.charging) clearCharge(D);""", """  state = 'dead'; qMatchEnd(); for (const D of ACTIVE) if (D.charging) clearCharge(D);""")
rep("""resetRun(); gyCam = 0; state = 'intro'; introT = 0; introN = 0; introUp = 0;""", """resetRun(); gyCam = 0; state = 'intro'; qMatchStart(); introT = 0; introN = 0; introUp = 0;""")
# ---- the item pick-ups (the roller, the turret) in the warm-up too: the first one of a session built its bubble's shader mid-match
rep("""  const dummy = new THREE.Group(); dummy.visible = false; crownMats.forEach(m => dummy.add(new THREE.Mesh(partG, m))); dummy.add(new THREE.Mesh(partG, crownHullMat)); scene.add(dummy);""",
    """  const dummy = new THREE.Group(); dummy.visible = false; crownMats.forEach(m => dummy.add(new THREE.Mesh(partG, m))); dummy.add(new THREE.Mesh(partG, crownHullMat)); scene.add(dummy);
  for (const t of ['roller', 'turret']) try { makePowerMesh(t).g.visible = false; } catch (e) {} // (hidden for good: the warm frame shows them)""")
# ---- the CPU's slingshot search: from straight ahead outward, and it stops at 3.5 ms with the cheapest turns priced (it could run past 14)
rep("""  for (let k = 0; k < 16; k++) {
    const yaw = k / 16 * 6.2832, turnT = Math.abs(wrapA(yaw - D.yaw)) / (TURN * 0.75) + 0.3;
    for (const c of FL_POW) {""", """  const t0 = performance.now();
  for (let j = 0; j < 16; j++) {
    if (j >= 6 && performance.now() - t0 > 3.5) break;
    const k = j & 1 ? (j + 1) >> 1 : -(j >> 1), yaw = D.yaw + k / 16 * 6.2832, turnT = Math.abs(wrapA(yaw - D.yaw)) / (TURN * 0.75) + 0.3;
    for (const c of FL_POW) {""")
rep('<p class="ver">Version 247</p>', '<p class="ver">Version 248</p>')
open(DST, 'w').write(s); print('ui188 ok', n0, '->', len(s))
