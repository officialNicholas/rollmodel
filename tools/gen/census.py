import asyncio, sys, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + (sys.argv[1] if len(sys.argv)>1 else 'pc_t.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        r = await pg.evaluate("""(()=>{ window.__noLoop=true; const T=__T, R=T.renderer; T.genWorld(5131); T.mapUsed=false; T.showMenu(); const th = T.genLayout(5131).theme;
          T.camera.position.set(0, 30, 44); T.camera.lookAt(0, -2, 2); T.camera.updateMatrixWorld();
          const sm = R.shadowMap.enabled; R.info.reset(); R.render(T.scene, T.camera); const all = R.info.render.calls; R.shadowMap.enabled = false; R.info.reset(); R.render(T.scene, T.camera); const noSh = R.info.render.calls; R.shadowMap.enabled = sm;
          const c = {}; T.scene.traverseVisible(o => { if (o.isMesh || o.isSprite || o.isPoints) { let p = o, tag = ''; while (p.parent && p.parent !== T.scene) p = p.parent; tag = (p.name || p.type) + ':' + (o.isSprite ? 'sprite' : o.material.type); c[tag] = (c[tag] || 0) + 1; } });
          return { th, all, noSh, top: Object.entries(c).sort((a, b) => b[1] - a[1]).slice(0, 14) }; })()""")
        print(json.dumps(r))
        await b.close()
asyncio.run(main())
