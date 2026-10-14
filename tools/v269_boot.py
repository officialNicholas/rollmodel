"""v269: the loading screen no longer ends on a long freeze. The warm-up at the end of loading (every shader the game can need, made and
drawn once) went to the GPU in one go, and the GPU then took its time over it after "Ready": until it was done the page could show
nothing new, so the bar sat full with the menu song already playing, sometimes for many seconds on a cold start, and "Tap to start"
wasn't drawn though a tap still worked. Now the warm-up goes a few materials at a time, each piece waited on (a GPU fence, and a
frame drawn) before the next, with the bar moving through "Lighting the gallery" as they finish. Where the browser can build shaders
in the background (KHR_parallel_shader_compile) it still does that first. A brand-new player's intro scene is built and warmed the
same way during loading too, instead of after it."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

WARM_OLD = """function warmRender() {
  if (vic) return; const hid = [], fc = [], fm = [];
  scene.traverse(o => { if (!o.visible) { hid.push(o); o.visible = true; } if (o.frustumCulled) { fc.push(o); o.frustumCulled = false; } });
  for (const f of floaters) for (const m of f.mats) if (!m.transparent) { m.transparent = true; m.needsUpdate = true; fm.push(m); }
  sun.shadow.needsUpdate = true;
  // twice: three draws the shadows before it sets up the frame's lights, so the first pass makes its shadow shaders for the lights of the
  // last frame drawn, and only the second makes the ones every frame of play will ask for
  const scOn = shadowCache.on; shadowCache.on = false; warming = true; // (and with the shadow cache off, so everything is drawn into the shadows both times)
  try { renderFrame(); sun.shadow.needsUpdate = true; renderFrame(); } catch (e) {}
  shadowCache.on = scOn;
"""
WARM_NEW = """// (v269: given a set, only those are drawn in the warm passes: the rest are kept out of every pass by their layers, which children don't
// inherit. With piece set it stops there, drawn once (piece 1, when the frame before was a warm one, its lights the same) or twice)
function warmRender(only, piece) {
  if (vic) return; const hid = [], fc = [], fm = [], off = [];
  scene.traverse(o => { if (!o.visible) { hid.push(o); o.visible = true; } if (o.frustumCulled) { fc.push(o); o.frustumCulled = false; }
    if (only && (o.isMesh || o.isPoints || o.isLine || o.isSprite) && !only.has(o)) { off.push(o, o.layers.mask); o.layers.mask = 0; } });
  if (!piece) for (const f of floaters) for (const m of f.mats) if (!m.transparent) { m.transparent = true; m.needsUpdate = true; fm.push(m); }
  sun.shadow.needsUpdate = true;
  // twice: three draws the shadows before it sets up the frame's lights, so the first pass makes its shadow shaders for the lights of the
  // last frame drawn, and only the second makes the ones every frame of play will ask for
  const scOn = shadowCache.on; shadowCache.on = false; warming = true; // (and with the shadow cache off, so everything is drawn into the shadows both times)
  try { renderFrame(); if (piece !== 1) { sun.shadow.needsUpdate = true; renderFrame(); } } catch (e) {}
  shadowCache.on = scOn; for (let i = 0; i < off.length; i += 2) off[i].layers.mask = off[i + 1];
  if (piece) { warming = false; for (const o of hid) o.visible = false; for (const o of fc) o.frustumCulled = true; sun.shadow.needsUpdate = true; return; }
"""

STEPS = """
// (v269) the warm-up at the end of loading, in pieces. In one go it handed the GPU every shader and every first draw at once, and the
// GPU then took its time over them after "Ready": the page could show nothing new until it was done (the bar sat full, the menu song
// already playing, "Tap to start" not drawn). Now a few materials at a time, each piece finished (its fence passed, a frame drawn)
// before the next, the bar moving as they go; then the passes only the whole warm-up covers
function gpuIdle(cap) {
  return new Promise(res => {
    let gl = null, fs = null; try { gl = renderer.getContext(); if (gl.fenceSync) { fs = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0); gl.flush(); } } catch (e) { fs = null; }
    const t0 = performance.now(), poll = () => {
      let ok = !fs; try { if (fs && gl.getSyncParameter(fs, gl.SYNC_STATUS) === gl.SIGNALED) ok = true; } catch (e) { ok = true; }
      if (ok || performance.now() - t0 > cap) { try { if (fs) gl.deleteSync(fs); } catch (e) {} return res(); }
      setTimeout(poll, 16);
    };
    requestAnimationFrame(() => setTimeout(poll, 0));
  });
}
// a scene's drawables grouped by material, in a few even pieces
function warmPieces(root, most) {
  const by = new Map(); root.traverse(o => { if (!(o.isMesh || o.isPoints || o.isLine || o.isSprite)) return; const m = Array.isArray(o.material) ? o.material[0] : o.material, k = m ? m.uuid : ''; let g = by.get(k); if (!g) by.set(k, g = []); g.push(o); });
  const G = [...by.values()], n = Math.max(1, Math.min(most, Math.ceil(G.length / 24))), per = Math.ceil(G.length / n), out = [];
  for (let i = 0; i < n; i++) { const s = new Set(); for (const g of G.slice(i * per, (i + 1) * per)) for (const o of g) s.add(o); if (s.size) out.push(s); }
  return out;
}
async function warmSteps(p0, p1, msg) {
  if (vic) return warmRender();
  const parts = warmPieces(scene, 16), n = parts.length, at = i => p0 + (p1 - p0) * i / (n + 1);
  for (let i = 0; i < n; i++) { warmRender(parts[i], i ? 1 : 2); bootTo(at(i + 1), at(i + 2), 2500, msg); await gpuIdle(5000); }
  // then what only the whole pass covers: the floaters see-through, the victory pose, the edge, a normal frame and the lobby's
  const fl = new Set(), fm = new Set(); for (const f of floaters) for (const m of f.mats) fm.add(m);
  scene.traverse(o => { if (o.material && [].concat(o.material).some(m => fm.has(m))) fl.add(o); });
  warmRender(fl); bootTo(p1, p1, 0, msg); await gpuIdle(5000);
}
// the same for a scene drawn straight to the screen (the first launch's): everything shown, a few materials at a time
async function warmScene(sc, cam, p0, p1, msg) {
  const parts = warmPieces(sc, 8), n = parts.length, at = i => p0 + (p1 - p0) * i / (n + 1);
  const draw = only => {
    const hid = [], fc = [], off = [];
    sc.traverse(o => { if (!o.visible) { hid.push(o); o.visible = true; } if (o.frustumCulled) { fc.push(o); o.frustumCulled = false; }
      if (only && (o.isMesh || o.isPoints || o.isLine || o.isSprite) && !only.has(o)) { off.push(o, o.layers.mask); o.layers.mask = 0; } });
    try { renderer.setRenderTarget(null); renderer.render(sc, cam); } catch (e) {}
    for (let i = 0; i < off.length; i += 2) off[i].layers.mask = off[i + 1]; for (const o of hid) o.visible = false; for (const o of fc) o.frustumCulled = true;
  };
  for (let i = 0; i < n; i++) { draw(parts[i]); bootTo(at(i + 1), at(i + 2), 2500, msg); await gpuIdle(5000); }
  draw(null); bootTo(p1, p1, 0, msg); await gpuIdle(5000);
}
"""

def apply(s):
    s = rep(s, WARM_OLD, WARM_NEW)
    a = "let warmQ = 0, bootWarm = false;"; i = s.index(a); s = s[:i] + STEPS.lstrip('\n') + s[i:]
    # compileAsync: only where the browser really builds them in the background; elsewhere it made them all at once too
    s = rep(s, "async function warmCompile() {\n  if (typeof renderer.compileAsync !== 'function') return;",
            "async function warmCompile() {\n  if (typeof renderer.compileAsync !== 'function' || !renderer.extensions.has('KHR_parallel_shader_compile')) return; // (v269: without it, compileAsync made every one at once: the warm-up's pieces make them instead)")
    s = rep(s, """bootTo(0.93, 0.99, 3500, 'Lighting the gallery'); await warmCompile(); // (v256)
warmRender(); bootWarm = true;
""", """bootTo(Math.max(0.86, bootPos()), 0.93, 3500, 'Lighting the gallery'); await warmCompile(); // (v256)
{ const p0 = Math.min(0.93, Math.max(0.86, bootPos())), p1 = FL && FL.due ? 0.96 : 0.99; // (v269: in pieces, the bar moving with them)
  try { await warmSteps(p0, p1, 'Lighting the gallery'); } catch (e) { try { warmRender(); } catch (x) {} }
  if (FL && FL.due && FL.prep) try { await FL.prep(p1, 0.99, 'Setting the scene'); } catch (e) {} }
bootWarm = true;
""")
    return s
