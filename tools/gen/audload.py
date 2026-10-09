import asyncio
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/audiotest.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: errs.append(m.type + ': ' + m.text[:300]))
        await pg.goto(U); await asyncio.sleep(3)
        print('ready', await pg.evaluate('window.ready'), errs[:6]); await b.close()
asyncio.run(main())
