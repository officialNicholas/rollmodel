# one frame's draw calls and triangles, per render pass and per object kind, in a paint-heavy match (optionally raining)
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'; SECS = float(sys.argv[3]) if len(sys.argv) > 3 else 70; RAIN = len(sys.argv) > 4 and sys.argv[4] == 'rain'; PAGE = sys.argv[5] if len(sys.argv) > 5 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""([stage, secs, rain]) => { const T = __T, R = T.renderer; window.__noLoop = true;
          Math.random = (() => { let s = 777; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
          T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('hard'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.aiReset(T.P); T.setWx('clear', 999); const dt = 1 / 60, n = Math.round(secs / dt);
          for (let i = 0; i < n && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 20 === 0) { T.visuals(dt * 20, dt * 20); T.flushTrail(); } T.matchLeft = 99; }
          if (rain) { T.setWx('rain', 999); for (let i = 0; i < 120; i++) { T.step(dt); T.matchLeft = 99; if (i % 10 === 0) T.visuals(dt * 10, dt * 10); } }
          T.visuals(dt, dt); T.flushTrail(); T.renderFrame();
          const stats = {}, orig = R.renderBufferDirect.bind(R);
          const tagOf = o => { let p = o, path = []; while (p && p !== T.scene) { if (p.name) path.push(p.name); p = p.parent; } const top = (() => { let q = o; while (q.parent && q.parent !== T.scene) q = q.parent; return q; })(); return (o.name || (top.name || top.type)) + '|' + (o.isInstancedMesh ? 'inst' : o.type) + '|' + (o.material ? o.material.type : '') + (o === T.paintMesh ? '|PAINT' : ''); };
          R.renderBufferDirect = function (camera, scene, geometry, material, object, group) {
            const rt = R.getRenderTarget(); const pass = !rt ? 'screen' : rt.depthTexture ? 'depthtex' : (rt.isWebGLCubeRenderTarget ? 'cube' : (rt.width === rt.height && rt.width >= 512 && !rt.samples ? 'shadow?' : (rt.samples ? 'main' : 'rt' + rt.width + 'x' + rt.height)));
            const idx = geometry.index, cnt = idx ? idx.count : (geometry.attributes.position ? geometry.attributes.position.count : 0);
            let n = Math.min(cnt, geometry.drawRange.count === Infinity ? cnt : geometry.drawRange.count); if (group) n = Math.min(n, group.count);
            const inst = object.isInstancedMesh ? object.count : 1, tris = (object.isLine || object.isLineSegments) ? 0 : n / 3 * inst;
            const key = pass + ' :: ' + tagOf(object); const s = stats[key] || (stats[key] = { calls: 0, tris: 0 }); s.calls++; s.tris += tris;
            return orig(camera, scene, geometry, material, object, group); };
          T.renderFrame(); R.renderBufferDirect = orig;
          const byPass = {}; for (const [k, v] of Object.entries(stats)) { const p = k.split(' :: ')[0]; const b = byPass[p] || (byPass[p] = { calls: 0, tris: 0 }); b.calls += v.calls; b.tris += v.tris; }
          const top = Object.entries(stats).sort((a, b) => b[1].tris - a[1].tris).slice(0, 30).map(([k, v]) => [k, v.calls, Math.round(v.tris)]);
          const topCalls = Object.entries(stats).sort((a, b) => b[1].calls - a[1].calls).slice(0, 15).map(([k, v]) => [k, v.calls, Math.round(v.tris)]);
          return { byPass, top, topCalls, paintV: T.chunkN }; }""", [STAGE, SECS, RAIN])
        print(json.dumps(r['byPass'])); print('paint verts', r['paintV'])
        print('-- by triangles'); [print('  ', x) for x in r['top']]
        print('-- by calls'); [print('  ', x) for x in r['topCalls']]
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
