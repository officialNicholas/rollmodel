import asyncio, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 375, 'height': 600}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ gfx: 'perf', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""() => { const w = document.querySelector('#stagePick .world'), cs = getComputedStyle(w); const kids = [...w.children].map(k => [k.className, k.getBoundingClientRect().height | 0]);
          return { w: w.getBoundingClientRect().width, h: w.getBoundingClientRect().height, width: cs.width, minW: cs.minWidth, kids }; }""")
        print(json.dumps(r)); await b.close()
asyncio.run(main())
