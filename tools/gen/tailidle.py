import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 600}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.openLook(); const rows = [];
          for (let s = 0; s < 24; s++) { for (let i = 0; i < 6; i++) { T.idle.t = Math.max(T.idle.t, 5); T.visuals(1 / 60, 1 / 60); } const U = T.VP.slime.U; rows.push([+T.VP.U.gSpd.value.toFixed(2), T.VP.slime.root.visible ? 1 : 0, +U.sWave.value.w.toFixed(3), +U.sMicro.value.y.toFixed(3), +U.sMicro.value.w.toFixed(3), +U.sBall.value.y.toFixed(3)]); }
          return rows; }""")
        print('idle [slither, tailFlick, crawl, bend] each second', r); print('errors', errs[:3]); await b.close()
asyncio.run(main())
