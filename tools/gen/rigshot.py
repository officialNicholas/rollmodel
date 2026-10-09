import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'rig'; HEAD = sys.argv[2] if len(sys.argv) > 2 else 'hat'; BACK = sys.argv[3] if len(sys.argv) > 3 else 'null'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 600, 'height': 600}, device_scale_factor=2)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', look: { eyes: 'round', head: '" + HEAD + "', back: " + ("'" + BACK + "'" if BACK != 'null' else 'null') + ", mouth: null }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.add_style_tag(content='.hud,.corner,#banner,#hint,.pop,#vig,#threat,#threatArrow{display:none !important}')
        r = await pg.evaluate("""() => { const T = __T, P = T.P; window.__noLoop = true; T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99); for (let i = 0; i < 120; i++) { T.step(0.016); T.visuals(0.016, 0.016); }
          P.power = { type: 'roller', t: 30 }; P.spd = 0; for (let i = 0; i < 90; i++) { T.step(0.016); T.visuals(0.016, 0.016); } return { look: JSON.stringify(T.myLook), st: P.st, x: P.x, z: P.z }; }""")
        print(r, errs[:2])
        for k, (a, d, h) in enumerate([(0.45, 2.2, 0.9), (2.6, 3.4, 3.2), (-1.1, 2.0, 0.6)]):
            await pg.evaluate("""([a, d, h]) => { const T = __T, c = T.camera, P = T.P; T.visuals(0.016, 0.016); const yaw = P.yaw + a; c.position.set(P.x + Math.sin(yaw) * d, P.y + h, P.z + Math.cos(yaw) * d); c.lookAt(P.x, P.y + 0.3, P.z); c.fov = 45; c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); c.fov = 60; c.updateProjectionMatrix(); }""", [a, d, h])
            await pg.screenshot(path=f'st/{TAG}_{k}.png', timeout=180000)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
