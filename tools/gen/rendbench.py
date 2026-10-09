import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for page in sys.argv[1:]:
            for W, H, dsf in [(390, 844, 2), (1280, 760, 1)]:
                ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=dsf)
                await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
                pg = await ctx.new_page(); await pg.goto(SP + page); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(800)
                r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; const out = {};
                  const gl = T.renderer.getContext(), px = new Uint8Array(4), sync = () => { T.renderer.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); }; const time = (n) => { sync(); const t0 = performance.now(); for (let i = 0; i < n; i++) { T.renderFrame(); sync(); } return +((performance.now() - t0) / n).toFixed(0); };
                  T.renderFrame(); out.menu = time(4);
                  T.genWorld(77, { themes: ['garden'] }); T.mapUsed = false; T.start(); for (let i = 0; i < 60; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame();
                  out.play = time(4); const P = T.post; if (P) { const b0 = P.bloom, d0 = P.dof; P.bloom = false; P.dof = false; out.playNoPost = time(3); P.bloom = b0; P.dof = d0; }
                  T.sun.castShadow = false; T.renderFrame(); out.playNoShadow = time(3); T.sun.castShadow = true;
                  return out; }""")
                print(page, W, H, json.dumps(r)); await ctx.close()
        await b.close()
asyncio.run(main())
