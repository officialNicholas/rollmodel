import asyncio
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.genWorld(5151, { themes: ['blank'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999); for (let i = 0; i < 120; i++) T.step(0.016);
          const P = T.P, H = T.H; H.ai = null; H.x = P.x + Math.sin(P.yaw) * 9; H.z = P.z + Math.cos(P.yaw) * 9; H.y = T.surfaceUnder(H.x, H.z, 5, true); T.startTurret(P);
          let e = null; try { T.fireShot(P); } catch (x) { e = String(x); } const s = T.shots[T.shots.length - 1];
          const o = { e, n: T.shots.length, s: s ? { x: s.x, y: s.y, z: s.z, vx: s.vx, vy: s.vy, vz: s.vz } : null };
          const x = s.x + s.vx * 0.016, z = s.z + s.vz * 0.016, y = s.y + (s.vy - 18 * 0.016) * 0.016; o.blocked = T.blockedAt(x, z, y - 0.35); o.g = T.surfaceUnder(x, z, s.y + 0.05, true); o.Py = P.y; o.Hd = Math.hypot(H.x - P.x, H.z - P.z); o.Hy = H.y; T.updateShots(0.016); o.after = T.shots.length; return o; }""")
        print(r, errs[:3]); await b.close()
asyncio.run(main())
