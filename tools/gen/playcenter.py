import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(1200)
        r = await pg.evaluate("""(() => { const d = document.querySelector('.bpc').getBoundingClientRect(), path = document.querySelector('.bpt path'), t = path.getBoundingClientRect(), svg = path.ownerSVGElement, bb = path.getBBox(), m = svg.getScreenCTM();
          const pt = (x, y) => { const q = svg.createSVGPoint(); q.x = x; q.y = y; return q.matrixTransform(m); };
          const a = pt(6.8, 4.2), c = pt(6.8, 19.8), tip = pt(20.4, 12), cx = (a.x + c.x + tip.x) / 3;
          return { disc: [+(d.left + d.width / 2).toFixed(1), +(d.top + d.height / 2).toFixed(1)], triBoxCenter: [+(t.left + t.width / 2).toFixed(1), +(t.top + t.height / 2).toFixed(1)], triCentroidX: +cx.toFixed(1), screenCenterX: innerWidth / 2 }; })()""")
        print(r)
        btn = await pg.query_selector('#homePlay'); await btn.screenshot(path='ui/playcenter.png')
        await b.close()
asyncio.run(main())
