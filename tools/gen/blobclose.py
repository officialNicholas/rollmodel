import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':900,'height':560}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(800)
        for i, col in enumerate(sys.argv[1:] or ['red']):
            await pg.evaluate(f"""(()=>{{ __T.setColor('{col}'); document.getElementById('menu').style.display='none'; const P=__T.P, H=__T.H; const mx=(P.x+H.x)/2, mz=(P.z+H.z)/2, a=Math.atan2(Math.sin(P.yaw)+Math.sin(H.yaw), Math.cos(P.yaw)+Math.cos(H.yaw)); window.__cam=[[mx+Math.sin(a)*2.3, 0.85, mz+Math.cos(a)*2.3],[mx, 0.36, mz]]; for (let k=0;k<30;k++) __T.visuals(0.0001,0.05); __T.camera.clearViewOffset(); __T.renderFrame(); }})()""")
            await pg.wait_for_timeout(500)
            await pg.screenshot(path=f'ui/blob_{col}.png')
        print('errors', errs)
        await b.close()
asyncio.run(main())
