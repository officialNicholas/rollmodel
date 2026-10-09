import asyncio, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
TAG = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for W, H, tag, mobile in [(390, 844, 'phone', True), (1280, 800, 'desk', False), (844, 390, 'land', True), (375, 667, 'se', True)]:
            ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2 if mobile else 1, has_touch=mobile, is_mobile=mobile)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', diff: 'medium', seen: {}, wins: { medium: 4 }, played: { medium: 9 }, bestCov: { medium: 31 }, world: { std: { best: 34, wins: 3, played: 5 } } })); } catch (e) {}")
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_' not in m.text and errs.append(m.text))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(900)
            await pg.evaluate("(()=>{ for (let i=0;i<160;i++) __T.visuals(0.0001, 0.05); __T.renderFrame(); })()")
            await pg.wait_for_timeout(700)
            await pg.screenshot(path=f'ui/{TAG}_{tag}_home.png')
            await pg.click('#homePlay'); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'ui/{TAG}_{tag}_world.png')
            print(tag, errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
