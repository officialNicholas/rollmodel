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
          const log = []; let maxN = 0; for (let i = 0; i < 90; i++) { H.spd = 0; const before = T.shots.slice(); T.step(0.016); maxN = Math.max(maxN, T.shots.length); for (const s of before) if (!T.shots.includes(s)) log.push([i, +s.x.toFixed(1), +s.y.toFixed(2), +s.z.toFixed(1), +s.life.toFixed(2)]); }
          const bx = T.BOXES.filter(b => -1.3 > b[0] - 0.3 && -1.3 < b[1] + 0.3 && -14.5 > b[2] - 0.3 && -14.5 < b[3] + 0.3).map(b => b.slice(0, 6).map(v => +(+v).toFixed(2))); return { bx, maxN, log: log.slice(0, 10), P: [+P.x.toFixed(1), +P.z.toFixed(1)], H: [+H.x.toFixed(1), +H.z.toFixed(1)], stun: H.stunT }; }""")
        print(r, errs[:3]); await b.close()
asyncio.run(main())
