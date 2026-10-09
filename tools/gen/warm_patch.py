# No shader compiles mid-match. The old warm-up compiled for the screen, but Graphics mode draws into an HDR target, which needs
# different programs, so the first power-up, orb, giant slam (and ~18 things at the start of every match) still compiled on the spot,
# each a hitch on a phone. Now, whenever a canvas is built (it waits in the menu), one hidden frame is drawn through the real pipeline
# with everything the match could show made visible (and the floaters in their see-through state too), then a normal frame over it
# in the same task, so nothing flashes. Power-ups also reuse their meshes' geometry instead of making new buffers on every respawn.
p = '/home/claude/paint-the-canvas.html'
s = open(p).read()
def rep(old, new, count=1):
    global s
    n = s.count(old); assert n == count, (n, old[:120]); s = s.replace(old, new)

rep("""// compile every shader up front (including the ones only a giant slam, the orb or a burst uses) so nothing hitches mid-game
(function warmUp() {""",
"""// draw one hidden frame with everything visible (and the floaters see-through), so every shader the match can need is compiled
// now, through the same passes (shadow, mirror, the HDR target) as in play; then a normal frame, in the same task, so nothing shows
function warmRender() {
  if (vic) return; const hid = [], fc = [], fm = [];
  scene.traverse(o => { if (!o.visible) { hid.push(o); o.visible = true; } if (o.frustumCulled) { fc.push(o); o.frustumCulled = false; } });
  for (const f of floaters) for (const m of f.mats) if (!m.transparent) { m.transparent = true; m.needsUpdate = true; fm.push(m); }
  sun.shadow.needsUpdate = true;
  try { renderFrame(); } catch (e) {}
  for (const o of hid) o.visible = false; for (const o of fc) o.frustumCulled = true; for (const m of fm) { m.transparent = false; m.needsUpdate = true; }
  sun.shadow.needsUpdate = true;
  try { renderFrame(); } catch (e) {}
}
let warmQ = 0; const queueWarm = () => { clearTimeout(warmQ); warmQ = setTimeout(warmRender, 30); };
// compile every shader up front (including the ones only a giant slam, the orb or a burst uses) so nothing hitches mid-game
(function warmUp() {""")
rep("  try { renderer.compile(scene, camera); } catch (e) {}\n  [SLAM_R * GIANT_SLAM",
    "  if (!HI) try { renderer.compile(scene, camera); } catch (e) {}\n  [SLAM_R * GIANT_SLAM")
# a canvas was just built: warm it up while it waits in the menu (or right before the match starts)
rep("function freshMap() { genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id, themes: stageThemes() }); mapUsed = false; }",
    "function freshMap() { genWorld((Math.random() * 4294967296) >>> 0, { avoid: TH.id, themes: stageThemes() }); mapUsed = false; queueWarm(); }")
rep("setTimeout(() => { genWorld(sd, op); mapUsed = false; building = false; start(); }, 60);",
    "setTimeout(() => { genWorld(sd, op); mapUsed = false; warmRender(); building = false; start(); }, 60);")
rep("setTimeout(() => { freshMap(); building = false; start(); }, 60); return; }",
    "setTimeout(() => { freshMap(); clearTimeout(warmQ); warmRender(); building = false; start(); }, 60); return; }")
rep("showMenu();\nrequestAnimationFrame(frame);\n})();", "showMenu();\nwarmRender();\nrequestAnimationFrame(frame);\n})();")

# power-ups: one set of shapes, shared by every respawn
rep("function makePowerMesh(type) {",
    "const PU_G = { roll: new THREE.CylinderGeometry(0.2, 0.2, 0.7, 24), stick: new THREE.CylinderGeometry(0.04, 0.04, 0.34, 8), tip: new THREE.ConeGeometry(0.27, 0.36, 20), neck: new THREE.CylinderGeometry(0.1, 0.1, 0.27, 14) };\nfunction makePowerMesh(type) {")
rep("  if (type === 'roller') { add(new THREE.CylinderGeometry(0.2, 0.2, 0.7, 24), puIconMat, V(0, 0, 0), [0, 0, Math.PI / 2]); add(new THREE.CylinderGeometry(0.04, 0.04, 0.34, 8), puHaloMat, V(0, 0.26, 0)); }\n  else { add(new THREE.ConeGeometry(0.27, 0.36, 20), puIconMat, V(0, -0.13, 0), [Math.PI, 0, 0]); add(new THREE.CylinderGeometry(0.1, 0.1, 0.27, 14), puIconMat, V(0, 0.18, 0)); }",
    "  if (type === 'roller') { add(PU_G.roll, puIconMat, V(0, 0, 0), [0, 0, Math.PI / 2]); add(PU_G.stick, puHaloMat, V(0, 0.26, 0)); }\n  else { add(PU_G.tip, puIconMat, V(0, -0.13, 0), [Math.PI, 0, 0]); add(PU_G.neck, puIconMat, V(0, 0.18, 0)); }")
open(p, 'w').write(s)
print('ok')
