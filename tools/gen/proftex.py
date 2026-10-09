import asyncio, time
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for gfx in ['hi', 'perf']:
            ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + gfx + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); await pg.goto('file://' + SP + 'pc_t.html', timeout=180000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000)
            r = await pg.evaluate("""() => { const T = __T, out = {}; const tm = (k, f) => { const t = performance.now(); f(); out[k] = Math.round(performance.now() - t); };
              for (const id of ['marble', 'ashlar', 'cobble', 'brick', 'parquet', 'damask', 'moss', 'hedge', 'sand', 'plank', 'blank', 'blankSide']) { delete T.SURF[id]; tm(id, () => T.surf(id)); }
              tm('genCath', () => T.genWorld(5, { themes: ['cathedral'] })); tm('genGarden', () => T.genWorld(5, { themes: ['garden'] })); tm('render', () => T.renderFrame()); return out; }""")
            print(gfx, r); await ctx.close()
        await b.close()
asyncio.run(main())
