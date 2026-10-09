import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(900); await pg.evaluate('window.__noLoop = true')
        r = await pg.evaluate("""(() => { const d = document.querySelector('.dock'), out = { dock: [d.getBoundingClientRect().width, d.scrollWidth], vw: innerWidth, docW: document.documentElement.scrollWidth };
          for (const c of d.children) { const r = c.getBoundingClientRect(); out[c.id || c.className] = [Math.round(r.left), Math.round(r.width), c.scrollWidth]; }
          for (const c of document.querySelector('.mfoot').children) { const r = c.getBoundingClientRect(); out['f:' + c.id] = [Math.round(r.left), Math.round(r.width), c.hidden]; }
          return out; })()""")
        print(json.dumps(r, indent=0)); await b.close()
asyncio.run(main())
