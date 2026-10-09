import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]
        pg.on('console', lambda m: (m.type in ('error','warning')) and errs.append(m.text[:300]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(2500)
        print(await pg.evaluate("THREE.ShaderChunk.shadowmap_pars_fragment.includes('mix( mix( texture2DCompare')"))
        # force hardened paint render (heat) to compile the dry branch
        await pg.evaluate("(()=>{ const T=__T; window.__noLoop=true; T.start(); for (let i=0;i<200;i++) T.step(0.012); T.forceSun && T.forceSun(); T.setWx('sun', 10); for (let i=0;i<200;i++) T.step(0.012); T.visuals(0.016,0.016); T.renderFrame(); })()")
        await pg.wait_for_timeout(500)
        print(errs[:5]); await b.close()
asyncio.run(main())
