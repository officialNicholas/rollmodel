import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(2500)
        await pg.evaluate("window.__lt = []; new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt.push([+(e.startTime - window.__t0).toFixed(0), +e.duration.toFixed(0)]); }).observe({ entryTypes: ['longtask'] }); window.__noLoop = true;")
        await pg.wait_for_timeout(1500)
        # time AU.init itself, then watch the deferred kit jobs
        r = await pg.evaluate("(() => { window.__t0 = performance.now(); const t = performance.now(); __T.AU.init(); return +(performance.now() - t).toFixed(1); })()")
        await pg.wait_for_timeout(2500)
        lt = await pg.evaluate("window.__lt")
        print('init ms', r, 'long tasks after init [start, dur]', lt, 'errors', errs[:3])
        await b.close()
asyncio.run(main())
