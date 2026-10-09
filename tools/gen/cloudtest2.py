# A drifting cloud right behind the player (between them and the camera): it should fade so you and the floor show through
import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
JS = """(seed) => { const T = __T, P = T.P; T.genWorld(seed, { themes: ['cathedral'] }); Object.assign(T.myLook, { head: 'hat', eyes: 'round' }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
  const m = T.movers.find(q => q.on); if (!m) return null;
  for (let i = 0; i < 90; i++) { T.step(0.016); const yaw = 2.4; P.yaw = yaw; P.x = m.cx + Math.sin(yaw) * 2.3; P.z = m.cz + Math.cos(yaw) * 2.3; P.y = 0; P.spd = 0; P.vx = P.vz = 0; T.camYaw = yaw; T.visuals(0.016, 0.016); }
  document.getElementById('banner').style.display = 'none'; T.renderFrame(); return [m.cx, m.cz, T.moverMeshes.map(g => +g.userData.fade.toFixed(2))]; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for name in sys.argv[1:]:
            ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); await pg.goto('file://' + SP + name + '.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
            await pg.evaluate("window.__noLoop = true"); await pg.wait_for_timeout(300)
            for seed in [77, 5151, 1234, 42, 9]:
                r = await pg.evaluate(JS, seed)
                if r: print(name, seed, r); await pg.screenshot(path=f'{SP}st/cloud_{name}.png'); break
            await ctx.close()
        await b.close()
asyncio.run(main())
