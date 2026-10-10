import asyncio, time
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__skipIntro = false; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1000)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        await pg.wait_for_function("__T.tut && __T.tut.step >= 0", timeout=400000, polling=100)
        print('first tip', await pg.evaluate("[__T.tut.bannerSeen, performance.now() > __T.bannerUntil, +__T.runT.toFixed(1), __T.tutTip && __T.tutTip.key, document.getElementById('bannerBig').textContent]"))
        seen = [('', '', '', '', '', document_text) for document_text in ['']]
        print('banner text seen', sorted(set(s[5] for s in seen))[:3], 'samples', len(seen)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
