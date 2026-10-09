# what each Graphics mode feature costs in a frame (swiftshader, so relative only): python3 gen/perfbreak.py [theme]
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TH = sys.argv[1] if len(sys.argv) > 1 else 'cathedral'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 120, 'height': 260}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""(th) => { const T = __T, R = T.renderer; window.__noLoop = true; R.info.autoReset = false;
          T.genWorld(77, { themes: [th] }); T.mapUsed = false; T.start(); for (let i = 0; i < 240; i++) { T.step(0.016); if (i % 3 === 2) { T.visuals(0.048, 0.048); T.flushTrail(); } } T.renderFrame(); T.renderFrame();
          const gl = R.getContext(), px = new Uint8Array(4), sync = () => { R.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
          const time = () => { T.renderFrame(); sync(); R.info.reset(); const t0 = performance.now(); for (let k = 0; k < 4; k++) T.renderFrame(); sync(); return { ms: Math.round((performance.now() - t0) / 4), calls: R.info.render.calls / 4 | 0, tris: R.info.render.triangles / 4 | 0 }; };
          const out = { base: time() }; const P = T.post, ivy = []; T.stageGroup.traverse(o => { if (o.isMesh && o.material && o.material.alphaTest > 0 && o.geometry.index && o.geometry.attributes.color) ivy.push(o); });
          P.mirror = false; out.noMirror = time(); P.mirror = true;
          ivy.forEach(o => o.visible = false); out.noIvy = time(); ivy.forEach(o => o.visible = true);
          const dz = P.dofK.z; P.dof = false; out.noDof = time(); P.dof = true;
          P.bloom = false; out.noBloom = time(); P.bloom = true;
          T.sun.castShadow = false; out.noShadow = time(); T.sun.castShadow = true;
          out.ivyLeaves = T.IVY.L.length; return out; }""", TH)
        print(TH, json.dumps(r)); await b.close()
asyncio.run(main())
