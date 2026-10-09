import asyncio
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/oldtest.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); await pg.goto(U); await pg.wait_for_function('window.ready === true')
        for n, a in [('jump', []), ('splat', [1]), ('slam', []), ('fling', [1]), ('bonk', [1]), ('power', []), ('fanfare', []), ('ui', []), ('tick', [4])]:
            print('old', n, await pg.evaluate("([n, a]) => oldFx(n, a)", [n, a]))
        for m in ['menu', 'play']: print('old music', m, await pg.evaluate("(m) => oldMusic(m, 10)", m))
        print(errs[:3]); await b.close()
asyncio.run(main())
