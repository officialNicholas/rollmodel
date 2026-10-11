"""Paint Shop season banner: open the shop in portrait and landscape and shoot the top of it. usage: shopban.py [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for name, vp, orient in [('port', {'width': 390, 'height': 844}, 'port'), ('land', {'width': 844, 'height': 390}, 'land')]:
            ctx = await b.new_context(viewport=vp, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + orient + "', name:'Dusk', seen:{}, drops: 17, runs: 3, owned: ['bunny'], tut: { done: true } })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100)
            await pg.wait_for_timeout(2500); await ev("document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(3500)
            info = await ev("(() => { const b = document.querySelector('.shban'); if (!b) return null; const r = b.getBoundingClientRect(), t = b.querySelector('.sbtitle').getBoundingClientRect(), pm = b.querySelector('.sbpump'); return { w: Math.round(r.width), h: Math.round(r.height), title: Math.round(t.height), pump: pm.complete && pm.naturalWidth, prog: b.querySelector('.sbprog').textContent }; })()")
            print(name, info)
            await pg.screenshot(path=f'{WS}/ui/shopban_{TAG}_{name}.png'); print('errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
