import asyncio, json
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/a252'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        save = { 'orient': 'port', 'name': 'Dusk', 'mode': 'solo', 'seen': {'steer':1,'jump':1,'hold':1,'roll':1,'missile':1,'pound':1,'burst':1,'orb':1,'look':1,'items':1}, 'xp': 2400, 'tut': { 'ph': 'done', 'strokes': 1, 'comms': 1, 'm3': 2 }, 'strokes': { 'special': 'giant', 'skill': 'pockets', 'own': ['rocket', 'giant', 'swim', 'repel', 'pockets'] } }
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + json.dumps(save) + ")); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_253.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=500)
        await pg.evaluate("__T.renderer.render = () => {}; __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=200000, polling=200); await pg.wait_for_timeout(800)
        for k in ['giant', 'freeze', 'rocket']:
            await pg.evaluate(f"__T.ev(`P.orbSaved = '{k}'; pocketHud()`)"); await pg.wait_for_timeout(400)
            r = await pg.evaluate("(() => { const e = document.getElementById('orbBtn'); const q = e.getBoundingClientRect(); return [q.left, q.top, q.width, q.height, getComputedStyle(e).display]; })()")
            print(k, r)
            await pg.screenshot(path=f'{OUT}/v253_orbbtn_{k}.png', clip={'x': max(0, r[0] - 60), 'y': max(0, r[1] - 60), 'width': 200, 'height': 180})
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
