import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + SP + 'pc_t.html'); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
        r = await pg.evaluate("""() => { const T = __T, out = []; for (const sd of [5151, 77, 1234]) { T.genWorld(sd, { themes: ['cathedral'] }); const L = T.IVY.L; out.push([sd, L.length, T.BOXES.length, T.BOXES.filter(b => b[4] <= 0 && b[6] !== 'c' && b[6] !== 'g' && b[5] - b[4] > 0.45).length, T.LIGHTS.length, T.GLOWS.length, T.ARENA]); } return out; }""")
        print(r, errs)
        await b.close()
asyncio.run(main())
