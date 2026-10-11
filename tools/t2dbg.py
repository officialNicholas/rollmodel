import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', runs: 1, drops: 120, stage: 'crypt', tut: { ph: 'match2' }, owned: ['flower', 'fangs'], bought: ['flower', 'fangs'], look: { mouth: 'fangs', side: 'flower' }, seen: { steer:1, jump:1, hold:1, burst:1, roll:1, pound:1, missile:1, item:1, orb:1, rocket:1, airdash:1, look:1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: m.type == 'error' and errs.append('console: ' + m.text[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.evaluate("__T.stageSel = 'crypt'; document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play' && !!__T.tut2", timeout=240000)
        await pg.evaluate("__T.matchLeft = 44; 0"); await pg.wait_for_function("__T.tutTip && __T.tutTip.key === 'wxsun'", timeout=60000)
        print('shade', await pg.evaluate("[__T.tut2.shade, __T.P.x, __T.P.z, __T.P.y]"))
        await pg.evaluate("(() => { const t = __T.tut2, P = __T.P; P.x = t.shade[0]; P.z = t.shade[1]; })(); 0")
        for i in range(10):
            await pg.wait_for_timeout(700)
            print(i, await pg.evaluate("[__T.tut2.sub, +__T.tut2.subT.toFixed(2), __T.tutTip && __T.tutTip.key, __T.inShadow(__T.P.x, __T.P.z, __T.P.y), +__T.P.x.toFixed(2), +__T.P.z.toFixed(2), +__T.P.spd.toFixed(2), __T.P.st, __T.tut2.slowK, +__T.runT.toFixed(2)]"))
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
