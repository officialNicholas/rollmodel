import asyncio, sys
from playwright.async_api import async_playwright
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
STAGE = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 195, 'height': 422}, device_scale_factor=1, has_touch=True, is_mobile=True, user_agent=UA)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'%s', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % STAGE)
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_perf.html', timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000); await pg.evaluate("window.__perfAI()")
        await pg.wait_for_timeout(4000)
        R = await pg.evaluate("""(() => { let n = 0, vis = 0, auto = 0, meshes = 0, visMesh = 0, byParent = new Map(); const sc = __T.scene;
          sc.traverseVisible(o => { vis++; if (o.matrixAutoUpdate) auto++; if (o.isMesh || o.isPoints || o.isLine || o.isSprite) visMesh++; });
          sc.traverse(o => { n++; if (o.isMesh) meshes++; });
          const top = sc.children.map(c => { let k = 0, kv = 0; c.traverse(() => k++); c.traverseVisible(() => kv++); return [c.type + (c.name ? ':' + c.name : ''), k, kv, c.visible]; }).sort((a, b) => b[1] - a[1]).slice(0, 15);
          // time updateMatrixWorld and a projection-only pass
          const t0 = performance.now(); for (let i = 0; i < 20; i++) sc.updateMatrixWorld(true); const umw = (performance.now() - t0) / 20;
          return { n, vis, auto, meshes, visMesh, top, umw, children: sc.children.length }; })()""")
        print(STAGE, {k: v for k, v in R.items() if k != 'top'}); [print('   ', t) for t in R['top']]
        await b.close()
asyncio.run(main())
