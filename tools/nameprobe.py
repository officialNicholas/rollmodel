import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1000)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(800)
        out = await pg.evaluate("""(() => { const T = __T, H = T.H, r = []; const big = () => document.getElementById('bannerBig').textContent;
          T.knockOut(H, 'pound', T.P); r.push(big()); H.st = 'play'; H.koT = 0;
          T.knockOut(H, 'fall', T.P); r.push(big()); H.st = 'play'; H.koT = 0;
          T.knockOut(H, 'dry', T.P); r.push(big()); H.st = 'play'; H.koT = 0;
          T.flatten ? 0 : 0; return r; })()""")
        print(out, 'errors', errs[:2]); await b.close()
asyncio.run(main())
