import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, xp: 140, drops: 168, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000)
        for i in range(6):
            print(i, await pg.evaluate("[__T.store.xp, document.getElementById('pbLvl').textContent, document.getElementById('pbNext').textContent, document.getElementById('pbXp').textContent, document.getElementById('repLvl').textContent, JSON.parse(localStorage.getItem('paint-world-red.v1')).xp]"))
            await pg.wait_for_timeout(1500)
        print(errs); await b.close()
asyncio.run(main())
