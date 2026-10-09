import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true;
          T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.start(); window.__noStep = false;
          for (let i = 0; i < 60; i++) { T.step(0.016); T.visuals(0.016, 0.016); }
          document.getElementById('hud').classList.add('off'); document.getElementById('banner').style.display = 'none';
          const h = T.HOLES[0]; const c = T.camera; const hx = h.x !== undefined ? h.x : h[0], hz = h.z !== undefined ? h.z : (h[2] !== undefined ? h[2] : h[1]);
          c.position.set(hx + 3.5, 6.5, hz + 5.5); c.lookAt(hx, -0.4, hz); T.renderFrame(); return [JSON.stringify(h).slice(0, 120), hx, hz]; }""")
        print(r); await pg.screenshot(path='fin/hole_close.png'); print(errs[:3]); await b.close()
asyncio.run(main())
