import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:400])); pg.on('console', lambda m: m.type in ('error', 'warning') and errs.append(m.type + ' ' + m.text[:300]))
        await pg.goto('file://' + SP + (sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html'), timeout=120000); await pg.wait_for_timeout(12000)
        print(await pg.evaluate("() => typeof __T"), errs[:8]); await b.close()
asyncio.run(main())
