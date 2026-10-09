# the player under a floating platform: the platform should all but vanish, its shadow staying on the floor
import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.evaluate("window.__noLoop = true")
        for seed in [5151, 77, 1234, 42]:
            r = await pg.evaluate("""(seed) => { const T = __T, P = T.P; T.genWorld(seed, { themes: ['cathedral'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99);
              const fb = T.BOXES.find(b => b[4] > 0.5); if (!fb) return null; P.x = (fb[0] + fb[1]) / 2; P.z = (fb[2] + fb[3]) / 2; P.y = 0; P.vx = P.vz = 0; P.spd = 0;
              for (let i = 0; i < 40; i++) { T.step(0.016); P.x = (fb[0] + fb[1]) / 2; P.z = (fb[2] + fb[3]) / 2; T.visuals(0.016, 0.016); } document.getElementById('banner').style.display = 'none'; T.renderFrame(); return fb; }""", seed)
            if r: print(seed, r); await pg.screenshot(path=f'{SP}st/under_{seed}.png'); break
        await b.close()
asyncio.run(main())
