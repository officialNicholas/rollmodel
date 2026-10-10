"""v186: the commissions board shows XP and dabs on each card."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, drops: 40, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        await pg.evaluate("document.getElementById('commBtn').click()"); await pg.wait_for_timeout(1500)
        print('cards', await pg.evaluate("[...document.querySelectorAll('#commList .comm .cr')].map(c => c.textContent)"), await pg.evaluate("document.querySelector('.cnote.small').textContent"))
        await pg.screenshot(path=S + '/ws/ui/comms.png'); print('errors', errs); await b.close()
asyncio.run(main())
