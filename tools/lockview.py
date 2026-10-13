import asyncio, sys
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
async def main():
    async with async_playwright() as p:
        b = await launch(p); ctx, pg, errs = await boot(b, sys.argv[1], SAVE)
        await pg.evaluate("document.getElementById('lookBtn').click()")
        await pg.wait_for_function("__T.ev('!lookIntro && lookOpen')", timeout=60000, polling=100); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{OUT}/lockview.png'); print(await pg.evaluate("__scr(0.2)"), errs[:3]); await b.close()
asyncio.run(main())
