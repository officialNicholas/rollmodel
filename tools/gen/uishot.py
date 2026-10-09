import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
SIZES = [(390,844,'m'),(1400,900,'d')] if len(sys.argv) < 2 else [tuple(int(v) if v.isdigit() else v for v in a.split('x')) for a in sys.argv[1:]]
async def settle(pg, n=160):
    await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.0001, 0.05); __T.renderFrame(); }})()")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for (W,H,tag) in SIZES:
            mobile = W < 600
            ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2 if mobile else 1, has_touch=mobile, is_mobile=mobile)
            pg = await ctx.new_page(); errs=[]
            pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_' not in m.text and errs.append(m.text))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
            await pg.wait_for_timeout(1500); await settle(pg)
            print(tag, 'errors', errs[:5], await pg.evaluate("[__T.camera.fov.toFixed(1), __T.camera.position.toArray().map(v=>v.toFixed(2)), __T.P.x.toFixed(2), __T.P.z.toFixed(2), __T.H.x.toFixed(2), __T.H.z.toFixed(2)]"))
            await pg.screenshot(path=f'ui/{tag}_menu.png')
        await b.close()
asyncio.run(main())
