import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TH = sys.argv[1] if len(sys.argv) > 1 else 'cathedral'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.evaluate("window.__noLoop = true")
        r = await pg.evaluate("""(th) => { const T = __T; T.genWorld(5151, { themes: [th] }); T.mapUsed = false; T.start(); for (let i = 0; i < 30; i++) T.visuals(0.016, 0.016);
          let d = null; T.stageGroup.traverse(o => { if (o.isMesh && o.renderOrder === 5 && o.geometry.attributes.position.count === 4) d = o; }); if (!d) return null; d.geometry.computeBoundingSphere(); const c = d.geometry.boundingSphere.center;
          document.getElementById('hud').classList.add('off'); const cam = T.camera; cam.position.set(c.x, 9, c.z + 6.5); cam.lookAt(c.x, 0, c.z); T.renderFrame(); return [c.x, c.z]; }""", TH)
        print(r); await pg.screenshot(path=f'{SP}st/decal_{TH}.png'); await b.close()
asyncio.run(main())
