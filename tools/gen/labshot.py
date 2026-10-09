# the lab sheet: python3 gen/labshot.py out.png [query] [js]
import asyncio, sys
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1]; Q = sys.argv[2] if len(sys.argv) > 2 else ''; JS = sys.argv[3] if len(sys.argv) > 3 else 'LAB.sheet()'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        w = 1536; h = 1024
        for kv in Q.split('&'):
            if kv.startswith('w='): w = int(kv[2:])
            if kv.startswith('h='): h = int(kv[2:])
        pg = await b.new_page(viewport={'width': w, 'height': h}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: m.type in ('error', 'warning') and errs.append(m.text[:600]))
        await pg.goto(SP + 'lab/index.html?' + Q, timeout=120000); await pg.wait_for_function('window.LAB_READY === true', timeout=120000)
        await pg.evaluate('() => { ' + JS + ' }')
        await pg.screenshot(path=OUT)
        for e in errs[:6]: print('ERR', e)
        await b.close()
asyncio.run(main())
