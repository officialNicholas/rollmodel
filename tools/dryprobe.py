import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,dry:1,jump:1,hold:1,roll:1,pound:1,missile:1}, runs: 5, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1000)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=90000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=200)
        await pg.evaluate("__T.matchLeft = 400; __T.P.paint = 0.0;"); await pg.wait_for_function("__T.P.dry", timeout=60000, polling=100)
        print('dry', await pg.evaluate("[__T.P.st, document.getElementById('tdryN').textContent, document.getElementById('tdryW').textContent]"))
        await pg.wait_for_function("__T.P.st === 'ko'", timeout=200000, polling=100)
        print('ko', await pg.evaluate("[__T.P.st, __T.P.reason, document.getElementById('kof').hidden]"))
        await pg.wait_for_function("__T.P.st !== 'ko'", timeout=200000, polling=100)
        print('back', await pg.evaluate("[__T.P.st, __T.P.dry, +__T.P.paint.toFixed(2), document.getElementById('kof').hidden]")); print('errors', errs[:3]); await b.close()
asyncio.run(main())
