"""The locker's opening on the axolotl: samples its paint coat, the burst timer and the intro clock every quarter second, with shots."""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'li'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=1)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000)
        for i in range(150):
            if await pg.evaluate("typeof __T === 'object' && !!__T.VP && !!__T.VP.slime"): break
            await pg.wait_for_timeout(2000)
        await pg.wait_for_timeout(2500)
        await pg.evaluate("(() => { const I = __T.VP.slime, X = I.ax; window.__pops = 0; const pi = I.popIn; I.popIn = () => { window.__pops++; pi(); }; })()")
        await pg.evaluate("(() => { try { __T.openLook(); } catch (e) {} })()")
        q = "(() => { const I = __T.VP.slime, X = I.ax; return [+performance.now().toFixed(0), I.root.visible, +X.coat.toFixed(2), +X.burstT.toFixed(2), +X.fadeT.toFixed(2), window.__pops, +(X.wade||0).toFixed(2), X.A.state]; })()"
        for k in range(24):
            print(json.dumps(await pg.evaluate(q)))
            if k in (4, 6, 8, 12): await pg.screenshot(path=f'{OUT}/{TAG}_{k:02d}.png')
            await pg.wait_for_timeout(250)
        print('errors', errs[:5])
        await b.close()
asyncio.run(main())
