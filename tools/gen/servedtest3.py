import asyncio, sys, time
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        await ctx.add_init_script("window.__t0 = performance.now(); const _f = window.fetch; window.fetch = function(u) { const t = performance.now(); return _f.apply(this, arguments).then(r => { console.log('fetch ' + u + ' ' + Math.round(performance.now() - window.__t0) + 'ms (took ' + Math.round(performance.now() - t) + ')'); return r; }); };")
        pg = await ctx.new_page(); logs = []; t0 = time.time()
        pg.on('pageerror', lambda e: logs.append('PAGE ' + str(e)[:300]))
        pg.on('console', lambda m: logs.append('%.1fs %s %s' % (time.time() - t0, m.type, m.text[:200])) if 'GPU stall' not in m.text and 'AudioContext' not in m.text else None)
        await pg.goto('http://127.0.0.1:8765/pc_served_dbg.html', timeout=240000)
        await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        print('T at %.1fs' % (time.time() - t0))
        r = await pg.evaluate("async () => { const t = performance.now(); await __T.SLIME.load('slime.pack'); return Math.round(performance.now() - t); }")
        print('reload took ms', r)
        for l in logs[:20]: print(l)
        await b.close()
asyncio.run(main())
