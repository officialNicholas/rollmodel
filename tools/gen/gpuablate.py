# what the frame's render costs with heavy paint, piece by piece (swiftshader, so relative): python3 gen/gpuablate.py [gfx] [stage] [secs]
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; STAGE = sys.argv[2] if len(sys.argv) > 2 else 'island'; SECS = float(sys.argv[3]) if len(sys.argv) > 3 else 70; PAGE = sys.argv[4] if len(sys.argv) > 4 else 'pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""([stage, secs]) => { const T = __T, R = T.renderer; window.__noLoop = true; R.info.autoReset = false;
          Math.random = (() => { let s = 777; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();
          T.mode = 'trio'; T.applyMode(); T.genWorld(4242, { themes: [stage] }); T.mapUsed = false; T.setDiff('hard'); T.start();
          T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.aiReset(T.P); T.setWx('clear', 999); const dt = 1 / 60, n = Math.round(secs / dt);
          for (let i = 0; i < n && T.state === 'play'; i++) { T.aiStep(T.P, dt); T.steerIn = T.P.steer; T.step(dt); if (i % 20 === 0) { T.visuals(dt * 20, dt * 20); T.flushTrail(); } T.matchLeft = 99; }
          T.visuals(dt, dt); T.flushTrail(); T.renderFrame(); T.renderFrame();
          const gl = R.getContext(), px = new Uint8Array(4), sync = () => { R.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
          const time = () => { T.renderFrame(); sync(); R.info.reset(); const t0 = performance.now(); for (let k = 0; k < 4; k++) T.renderFrame(); sync(); return { ms: Math.round((performance.now() - t0) / 4), calls: R.info.render.calls / 4 | 0, tris: R.info.render.triangles / 4 | 0 }; };
          const out = { paintV: T.chunkN, base: time() };
          T.paintMesh.visible = false; out.noPaint = time(); T.paintMesh.visible = true;
          const P = T.post; if (P) { P.mirror = false; out.noMirror = time(); P.mirror = true; P.bloom = false; out.noBloom = time(); P.bloom = true; }
          T.sun.castShadow = false; out.noShadow = time(); T.sun.castShadow = true;
          const pr = R.getPixelRatio(); R.setPixelRatio(pr * 0.5); if (P) P.resize(); out.halfRes = time(); R.setPixelRatio(pr); if (P) P.resize();
          T.setWx('rain', 999); for (let i = 0; i < 90; i++) { T.step(dt); T.matchLeft = 99; if (i % 10 === 0) T.visuals(dt * 10, dt * 10); } T.visuals(dt, dt); out.rain = time();
          T.paintMesh.visible = false; out.rainNoPaint = time(); T.paintMesh.visible = true;
          return out; }""", [STAGE, SECS])
        print(GFX, STAGE, json.dumps(r)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
