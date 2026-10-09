import asyncio
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); for (let i = 0; i < 120; i++) T.step(0.016);
          const P = T.P, H = T.H; H.ai = null; H.x = P.x + Math.sin(P.yaw) * 9; H.z = P.z + Math.cos(P.yaw) * 9; H.y = T.surfaceUnder(H.x, H.z, 5, true); H.spd = 0; H.steer = 0; H.immuneT = 0; T.startTurret(P);
          const log = []; for (let i = 0; i < 60; i++) { T.step(0.016); if (i % 6 === 0) log.push([+P.turret.cd.toFixed(2), T.shots.length, T.shots[0] ? [+T.shots[0].vx.toFixed(1), +T.shots[0].vy.toFixed(1), +T.shots[0].y.toFixed(1)] : null, P.st, P.air, P.flatT, P.stunT]); }
          return log; }""")
        for x in r: print(x)
        print(errs[:3]); await b.close()
asyncio.run(main())
