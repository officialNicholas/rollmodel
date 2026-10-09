# the heaviest things drawn, by triangles submitted in one mid-match frame: each mesh's triangle count, what it is, where it sits
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'
GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'
STAGE = sys.argv[3] if len(sys.argv) > 3 else 'island'
JS = r"""(stage) => { const T = __T, R = T.renderer, P = T.P; window.__noLoop = true; window.__fixedPR = true;
  Math.random = (() => { let s = 77; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
  T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
  T.mode = 'trio'; T.applyMode(); T.setStage(stage === 'island' || stage === 'blank' ? stage : 'season'); T.genWorld(2468, { themes: [stage] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
  T.aiReset(P); for (let i = 0; i < 600; i++) { T.aiStep(P, 1 / 60); T.steerIn = P.steer; T.step(1 / 60); if (i % 10 === 0) T.visuals(1 / 6, 1 / 6); }
  T.visuals(1 / 60, 1 / 60);
  const rows = new Map(), orig = R.renderBufferDirect.bind(R);
  const desc = o => { const m = o.material, key = m && m.customProgramCacheKey ? String(m.customProgramCacheKey()).replace(/\s+/g, ' ').slice(0, 30) : (m && m.type); const g = o.geometry; let chain = []; let q = o; while (q && q !== T.scene) { chain.push(q.name || q.type); q = q.parent; }
    return (o.isInstancedMesh ? 'INST ' : '') + key + ' | ' + chain.slice(0, 4).join('<') + ' | attrs ' + Object.keys(g.attributes).join(',') + ' | layers ' + o.layers.mask + ' | ro ' + o.renderOrder; };
  R.renderBufferDirect = function (camera, scene, geometry, material, object, group) {
    const ix = geometry.index ? geometry.index.count : geometry.attributes.position.count, dr = geometry.drawRange, cnt = group ? group.count : Math.min(ix, dr.count === Infinity ? ix : dr.count), inst = object.isInstancedMesh ? object.count : 1;
    const t = Math.round(cnt / 3) * inst, k = desc(object) + (camera === T.camera ? '' : ' [' + camera.type + ']'), r = rows.get(k) || { n: 0, t: 0, pos: [object.position.x, object.position.y, object.position.z].map(v => +v.toFixed(1)) }; r.n++; r.t += t; rows.set(k, r);
    return orig(camera, scene, geometry, material, object, group); };
  T.renderFrame(); R.renderBufferDirect = orig;
  return [...rows.entries()].sort((a, b) => b[1].t - a[1].t).slice(0, 30).map(([k, v]) => (v.t / 1000).toFixed(1) + 'k x' + v.n + '  ' + k + '  @' + v.pos.join(',')); }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        r = await pg.evaluate(JS, STAGE)
        for row in r: print(row[:300])
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
