import asyncio, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
TAG = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for W, H, dev in [(390, 844, 'phone'), (1280, 760, 'desk'), (844, 390, 'land')]:
            mobile = dev != 'desk'
            ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2 if mobile else 1, has_touch=mobile, is_mobile=mobile)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(1600)
            await pg.screenshot(path=f'menu/{TAG}_{dev}_title.png')
            await pg.click('#homePlay'); await pg.wait_for_timeout(1200)
            await pg.screenshot(path=f'menu/{TAG}_{dev}_worlds.png')
            print(dev, errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
