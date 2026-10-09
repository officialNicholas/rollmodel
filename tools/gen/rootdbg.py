import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
SETUP = open(SP + 'gen/skinshot.py').read().split('SETUP = r"""')[1].split('"""')[0]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'red', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(800)
        await pg.evaluate(SETUP, 'island')
        r = await pg.evaluate("""() => { const T = __T, P = T.P, n0 = window.__n0, out = [];
          for (let i = 0; i < 160; i++) { T.steerIn = 0; P.spd = T.cfg.speed * 0.9; P.paint = 999; P.vy = 0; P.air = false; T.step(1 / 60); P.x = n0.x; P.z = n0.z; P.yaw = 0.6; T.visuals(1 / 60, 1 / 60);
            if (i % 20 === 0) out.push([i, T.state, P.st, +P.y.toFixed(2), +T.VP.root.position.y.toFixed(2), +(P.stepOff || 0).toFixed(2), P.air, +(P.vy || 0).toFixed(2), +P.spd.toFixed(2)]); }
          return out; }""")
        for x in r: print(x)
        await b.close()
asyncio.run(main())
