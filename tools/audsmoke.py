import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); logs = []; pg.on('console', lambda m: logs.append(m.text[:160]) if m.type == 'error' and 'CORS' not in m.text else None)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2000)
        await pg.tap('#setBtn'); await pg.wait_for_timeout(300); await pg.tap('#setDone'); await pg.wait_for_timeout(9000)
        print(await pg.evaluate("(() => { const A = __T.AU; A.init(); return { vox: ['hyah','whee','oof','yay'].map(k => A.vox(k)), say: ['cd3','go','victory','final'].map(k => A.say(k)), cues: ['splat','jump','slam','go','bonk','power'].map(k => A[k] ? A[k](1) : 'no fn') }; })()"))
        await pg.wait_for_timeout(2500); print('errors', errs[:3], logs[:5]); await b.close()
asyncio.run(main())
