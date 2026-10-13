import asyncio, json, sys
from playwright.async_api import async_playwright
PAGE = sys.argv[1]; TAG = sys.argv[2]
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/a252'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for orient, vp in [('port', (390, 844)), ('land', (844, 390))]:
            ctx = await b.new_context(viewport={'width': vp[0], 'height': vp[1]}, device_scale_factor=2, has_touch=True, is_mobile=True)
            save = { 'orient': orient, 'name': 'Dusk', 'seen': {'look': 1}, 'runs': 9, 'xp': 2400, 'drops': 168, 'tut': { 'ph': 'done', 'strokes': 1, 'comms': 1, 'm3': 2 },
                     'strokes': { 'special': 'giant', 'skill': 'swim', 'own': ['rocket', 'giant', 'swim', 'repel', 'pockets'] } }
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + json.dumps(save) + ")); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=500); await pg.wait_for_timeout(1200)
            await pg.evaluate("__T.ev('openStrokes()')"); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=f'{OUT}/{TAG}_strokes_{orient}.png')
            await pg.evaluate("(() => { const b = document.querySelector('[data-sk=\"pockets\"]'); if (b) b.click(); })()"); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'{OUT}/{TAG}_strokes_{orient}_pockets.png')
            print(orient, 'errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
