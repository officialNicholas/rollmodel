import asyncio, json, sys
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SEED = "(() => { let s = 12345; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
        await pg.evaluate("""(seed) => { const T = __T, P = T.P; window.__noLoop = true; eval(seed);
              T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.start(); window.__noStep = false;
              P.cpu = true; T.aiReset(P); window.__run = (n) => { for (let i = 0; i < n; i++) { T.steerIn = P.steer || 0; T.step(0.016); T.visuals(0.016, 0.016); T.flushTrail(); } };
              document.getElementById('banner').style.display = 'none'; document.getElementById('hud').classList.add('off'); }""", SEED)
        for n in [70, 140, 140, 70]:
            await pg.evaluate(f"__run({n})")
            await pg.evaluate("__T.renderFrame()"); 
            info = await pg.evaluate("""(() => { const T = __T, m = T.paintMesh.material, u = T.paintUniforms; return { clock: T.clock.toFixed(2), uTime: u.uTime.value.toFixed(2), uNow: u.uNow.value.toFixed(2), hardOn: u.uHardOn.value, hardStart: u.uHardStart.value, rewet: u.uRewet.value, wx: T.wx, transp: m.transparent, dt: m.depthTest, dw: m.depthWrite, po: m.polygonOffset, pof: m.polygonOffsetFactor, pou: m.polygonOffsetUnits, ro: T.paintMesh.renderOrder, recv: T.paintMesh.receiveShadow }; })()""")
            print(n, json.dumps(info))
            await pg.screenshot(path=f'fin/bi_post_{n}_{info["clock"]}.png')
        # same state: plain render, no post
        await pg.evaluate("(() => { const T = __T; T.renderer.setRenderTarget(null); T.renderer.render(T.scene, T.camera); })()")
        await pg.screenshot(path='fin/bi_direct.png')
        await pg.evaluate("(() => { const T = __T; T.stageGroup.visible = false; T.renderer.setRenderTarget(null); T.renderer.render(T.scene, T.camera); T.stageGroup.visible = true; })()")
        await pg.screenshot(path='fin/bi_nostage.png')
        lst = await pg.evaluate("""(() => { const T = __T, out = []; T.scene.traverse(o => { if (o.isMesh && o.visible && o.material && !Array.isArray(o.material) && o.material.transparent) out.push((o.name || o.geometry.type) + ':' + o.renderOrder + ':' + (o.material.type) ); }); return out.slice(0, 40); })()""")
        print('transparent meshes', lst)
        print(errs[:3]); await b.close()
asyncio.run(main())
