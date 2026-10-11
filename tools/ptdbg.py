import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', runs: 4, drops: 50, stage: 'blank', tut: { ph: 'done' }, seen: { steer:1, jump:1, hold:1, burst:1, roll:1, pound:1, missile:1, item:1, orb:1, rocket:1, airdash:1, look:1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=120000)
        for i in range(14):
            await pg.wait_for_timeout(3000)
            print(i, await pg.evaluate("[+__T.runT.toFixed(1), JSON.stringify(__T.tutPT), __T.tutTip && __T.tutTip.key, __T.P.st, __T.P.flung, __T.store.slingTips, __T.store.flings, __T.tutPh(), !!__T.tut, !!__T.tut2, +__T.matchLeft.toFixed(1)]"))
        print('errors', errs); await b.close()
asyncio.run(main())
