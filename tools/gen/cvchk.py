import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(800)
        q = "(() => { const s = document.getElementById('cvName'), r = s.getBoundingClientRect(), cs = getComputedStyle(s); return [s.textContent, s.className, Math.round(r.width), Math.round(r.height), cs.display, cs.opacity, cs.visibility, cs.transform, document.getElementById('shuffleBtn').getBoundingClientRect().width|0]; })()"
        print('before', await pg.evaluate(q))
        await pg.click('#shuffleBtn'); await pg.wait_for_timeout(100); print('100ms', await pg.evaluate(q))
        await pg.wait_for_timeout(1000); print('1.1s', await pg.evaluate(q))
        await pg.click('#stages button[data-d="hard"]'); await pg.wait_for_timeout(300); print('diff', await pg.evaluate(q))
        print(errs); await b.close()
asyncio.run(main())
