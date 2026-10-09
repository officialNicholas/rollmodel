import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', stage:'crypt', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        await pg.wait_for_function("!!__T.vic", timeout=40000, polling=200); await pg.wait_for_timeout(1200)
        await pg.tap('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=10000); await pg.wait_for_timeout(2500)
        print(await pg.evaluate("(() => { const j = document.getElementById('jBar'), cs = j.querySelectorAll('canvas'); const c = cs[cs.length - 1]; let a = 0; if (c && c.width) { const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; for (let i = 3; i < d.length; i += 4 * 97) a += d[i] > 0 ? 1 : 0; } const r = j.getBoundingClientRect(); return { canvases: cs.length, cw: c && c.width, ch: c && c.height, alphaHits: a, jbar: Math.round(r.width) + 'x' + Math.round(r.height), cls: j.className, cliW: j.clientWidth, cliH: j.clientHeight, hudCanvas: !!document.querySelector('#meter canvas'), hudCls: document.getElementById('meter').className }; })()"))
        print(await pg.evaluate("JSON.stringify([window.__liqCalls, window.__liqState, window.__liqT, window.__liqDbg()])"))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
