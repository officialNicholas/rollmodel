"""The first real match after the lesson (tut2): bring the gift's time forward and check it appears near you with no page errors.
usage: giftcheck.py [page]"""
import asyncio, sys
from playwright.async_api import async_playwright
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', runs: 1, drops: 120, stage: 'crypt', tut: { ph: 'match2' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        async def wait(js, t=240000): await pg.wait_for_function(js, timeout=t, polling=100)
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.evaluate("__T.stageSel = 'crypt'; __T.start()"); await wait("__T.state === 'play'"); await wait("!!__T.tut2")
        print('tut2 phase', await pg.evaluate("__T.tut2.ph"))
        await pg.evaluate("(() => { const g = __T.gift; g.id = 'zombie'; g.got = false; g.on = false; g.at = __T.runT + 0.5; })(); 0")
        try:
            await wait("__T.gift && __T.gift.on", 60000)
            print('gift on', await pg.evaluate("[__T.gift.id, +Math.hypot(__T.gift.x - __T.P.x, __T.gift.z - __T.P.z).toFixed(1)]"))
        except Exception as e:
            print('gift did not appear')
        uniq = sorted(set(errs)); el = await pg.evaluate("(() => { const e = document.getElementById('errLine'); return e && !e.hidden ? e.textContent.slice(0, 160) : null; })()"); print('page errors', len(errs), uniq[:3], '| on-screen error box:', el); await b.close()
asyncio.run(main())
