import asyncio
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); for (let i = 0; i < 100; i++) T.step(0.016);
          const P = T.P; T.H.x = 40; T.H.z = 40; T.startTurret(P); P.turret.aim = 0.2; const s0 = T.splatN, c0 = T.teamCov(0); const land = [];
          const seen = new Set(); for (let i = 0; i < 150; i++) { const before = new Set(T.shots); T.step(0.016); for (const s of before) if (!T.shots.includes(s)) land.push([+(Math.hypot(s.x - P.x, s.z - P.z)).toFixed(1), +s.y.toFixed(2)]); }
          return { splats: T.splatN - s0, cov: +(T.teamCov(0) - c0).toFixed(3), landed: land.slice(0, 8), n: land.length, Py: P.y }; }""")
        print(r, errs[:3]); await b.close()
asyncio.run(main())
