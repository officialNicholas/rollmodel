import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':700,'height':500}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', stage: 'standard', seen: {} })); } catch (e) {}")
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        await pg.add_style_tag(content="#stage > :not(canvas){visibility:hidden !important}")
        for k, (ink, hide) in enumerate([(1, False), (0.4, False), (1, True)]):
            await pg.evaluate(f"""(() => {{ const T = __T; window.__noLoop = true; T.start(); for (let i = 0; i < 80; i++) T.step(0.012);
              const p = T.pots2[1]; p.ink = {ink}; T.H.st = 'out';
              if ({str(hide).lower()}) {{ T.enterPot2(T.P, p); }}
              for (let i = 0; i < 20; i++) T.visuals(0.016, 0.016);
              const c = T.camera; c.clearViewOffset(); c.fov = 40; c.aspect = 700 / 500; c.updateProjectionMatrix(); c.position.set(p.x + 2.2, p.y + 1.8, p.z + 2.6); c.lookAt(p.x, p.y + 0.25, p.z); T.renderFrame(); }})()""")
            await pg.screenshot(path=f'ui/can_{k}.png')
        print(errs[:3]); await b.close()
asyncio.run(main())
