import asyncio, collections
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat','lashes'], look:{head:'hat',lash:'lashes',iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); pg.on('pageerror', lambda e: print('PAGEERROR', str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(3000)
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Profiler.enable')
        async def prof(label, ms):
            await cdp.send('Profiler.start'); await pg.wait_for_timeout(ms); r = await cdp.send('Profiler.stop'); prof = r['profile']
            nodes = {n['id']: n for n in prof['nodes']}; selfT = collections.Counter(); dts = prof['timeDeltas']; samples = prof['samples']
            for sid, dt in zip(samples, dts): n = nodes[sid]; cf = n['callFrame']; selfT[(cf['functionName'] or '(anon)') + ':' + str(cf['lineNumber'])] += dt
            tot = sum(selfT.values()); print(label, 'total ms', tot // 1000); [print('  %6d ms  %s' % (v // 1000, k)) for k, v in selfT.most_common(12)]
        await prof('menu', 2500)
        await pg.evaluate("document.getElementById('homePlay').click()")
        await pg.wait_for_function("__T.state === 'play'", timeout=60000)
        await prof('play', 4000)
        await b.close()
asyncio.run(main())
