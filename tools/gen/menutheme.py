import asyncio, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', diff: 'medium', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(600)
        for i, th in enumerate(['studio', 'crypt', 'cathedral', 'manor', 'garden']):
            if th == 'studio':
                await pg.evaluate("(()=>{ document.querySelector('.world[data-s=standard]').click(); })()"); await pg.wait_for_timeout(300)
            else:
                await pg.evaluate(f"(()=>{{ const T=__T; T.genWorld(12345 + {i}, {{ themes: ['{th}'] }}); T.resetRun(); T.decorate(); T.menuPose(); }})()")
            for t in [0, 20]:
                await pg.evaluate(f"(()=>{{ __T.clock = {t}; for (let i=0;i<220;i++) __T.visuals(0.0001, 0.05); __T.renderFrame(); }})()")
                await pg.screenshot(path=f'ui/orb_{th}_{t}.png')
        print(errs[:3]); await b.close()
asyncio.run(main())
