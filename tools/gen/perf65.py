# where a frame goes, mid-match with three blobs: draw calls and triangles by what's being drawn (main pass and shadow pass), the JS time
# for the simulation and the visuals, and the render time (swiftshader: a stand-in for the GPU's load), per stage and graphics tier
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
STAGES = sys.argv[3].split(',') if len(sys.argv) > 3 else ['island', 'blank', 'crypt']
JS = r"""(stage) => { const T = __T, R = T.renderer, P = T.P; window.__noLoop = true; window.__fixedPR = true;
  Math.random = (() => { let s = 77; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  T.mode = 'trio'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(2468, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
  T.aiReset(P); for (let i = 0; i < 900; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); if (i % 10 === 0) T.visuals(1 / 6, 1 / 6); }
  for (let i = 0; i < 150; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); T.visuals(1 / 60, 1 / 60); if (i % 3 === 0) T.renderFrame(); } // (the shadow cache settles: what's still gets cached)
  // categorize each draw by the top-level thing it belongs to
  const cat = o => { let q = o, path = []; while (q && q.parent) { path.push(q); q = q.parent; } const top = path[path.length - 1] || o;
    if (o.isInstancedMesh) return 'instanced:' + (o.material.name || o.material.type) + (o.name ? ':' + o.name : '');
    if (path.some(x => x === T.stageGroup)) return 'stage:' + (o.material && o.material.customProgramCacheKey ? String(o.material.customProgramCacheKey()).slice(0, 18) : o.material.type);
    const lr = [T.VP && T.VP.slime && T.VP.slime.root, T.P && T.H && null]; let who = 'other';
    if (path.some(x => x.userData && x.userData.slime)) who = 'slime'; else if (o.material && /slime/.test(o.material.customProgramCacheKey ? String(o.material.customProgramCacheKey()) : '')) who = 'slime';
    return who + ':' + (top.name || top.type) + ':' + (o.material.customProgramCacheKey ? String(o.material.customProgramCacheKey()).slice(0, 16) : o.material.type); };
  const acc = { main: {}, shadow: {} }; const orig = R.renderBufferDirect.bind(R);
  R.renderBufferDirect = function (camera, scene, geometry, material, object, group) { const sh = camera.isOrthographicCamera || camera.isPerspectiveCamera && camera !== T.camera && camera.near > 0.4 && false;
    const key = R.getRenderTarget() && R.getRenderTarget().depthTexture === undefined && camera.isOrthographicCamera ? 'shadow' : 'main';
    const k = cat(object), a = acc[key][k] || (acc[key][k] = [0, 0]); const ix = geometry.index ? geometry.index.count : geometry.attributes.position.count, inst = object.isInstancedMesh ? object.count : (geometry.isInstancedBufferGeometry ? geometry.instanceCount : 1);
    const dr = geometry.drawRange, cnt = group ? group.count : Math.min(ix, dr.count === Infinity ? ix : dr.count); a[0]++; a[1] += Math.round(cnt / 3) * (inst || 1); return orig(camera, scene, geometry, material, object, group); };
  R.info.autoReset = false; R.info.reset(); T.renderFrame(); const calls = R.info.render.calls, tris = R.info.render.triangles; R.info.autoReset = true;
  R.renderBufferDirect = orig;
  // timing: the simulation and the visuals in JS; the render with the GPU flushed (swiftshader)
  const gl = R.getContext(), px = new Uint8Array(4), sync = () => gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
  let tStep = 0, tVis = 0, tRen = 0; const N = 40;
  for (let f = 0; f < N; f++) { let a = performance.now(); T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); tStep += performance.now() - a; a = performance.now(); T.visuals(1 / 60, 1 / 60); tVis += performance.now() - a; a = performance.now(); T.renderFrame(); sync(); tRen += performance.now() - a; }
  const top = o => Object.entries(o).sort((a, b) => b[1][1] - a[1][1]).slice(0, 14).map(([k, v]) => k + ' x' + v[0] + ' ' + (v[1] / 1000).toFixed(1) + 'k');
  return { stage, calls, tris: Math.round(tris / 1000) + 'k', stepMs: +(tStep / N).toFixed(2), visMs: +(tVis / N).toFixed(2), renderMs: +(tRen / N).toFixed(1), main: top(acc.main), shadow: top(acc.shadow), shadowCalls: Object.values(acc.shadow).reduce((s, v) => s + v[0], 0), mainCalls: Object.values(acc.main).reduce((s, v) => s + v[0], 0) }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', owned: ['tiara','tophat'], look: { head: 'tiara' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        for st in STAGES:
            r = await pg.evaluate(JS, st)
            print(GFX, json.dumps(r, indent=0)[:3000])
            await pg.evaluate("() => { __T.state = 'menu'; __T.showMenu(); }")
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
