import asyncio, json, sys
sys.path.insert(0,'gen')
from v20test import page
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg, errs = await page(b)
        await pg.evaluate("__flat()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; const c = 1, off = 2.4; const n = __open(9);
            const L = T.flightFor(c, 0).d; __place(P, n.x - L * 0.5, n.z, n.h, Math.PI / 2); __place(H, n.x - L * 0.5 + L, n.z + off, n.h, 0); __freezeAI(); const h0x = H.x, h0z = H.z;
            T.flingIt(P, c); let k = 0, log = []; while (P.air && k < 400) { H.x = h0x; H.z = h0z; H.spd = 0; H.yaw = 0; const pre = { px: +P.x.toFixed(2), py: +P.y.toFixed(2), fc: P.flingC, fl: P.freeLand, hst: H.st, hair: H.air, hy: +H.y.toFixed(2), slam: H.slam, imm: H.immuneT, flat: H.flatT }; T.step(0.012); k++; if (!P.air) log.push(pre, { kx: H.kx, kz: H.kz, d: Math.hypot(H.x - P.x, H.z - P.z), knock: H.knockT, flat: H.flatT, py: P.y, hy: H.y }); }
            return log; })()""")
        print(json.dumps(r)); print(errs)
        await b.close()
asyncio.run(main())
