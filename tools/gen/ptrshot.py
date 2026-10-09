import asyncio
from playwright.async_api import async_playwright
src = open('gen/v20test.py').read(); HELP = src.split('HELP = r"""')[1].split('"""')[0]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("__T.setDiff('hard')"); await pg.click('#startBtn'); await pg.wait_for_timeout(2600)
        await pg.evaluate("window.__noStep=true"); await pg.evaluate(HELP)
        await pg.evaluate("(()=>{ const op = window.__place; window.__place = (...a) => { __T.showBlobs(); op(...a); }; })()")
        # orb behind and to the right of you: the pointer sits on the edge
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H, o = T.orb; T.setWx('clear', 999); window.__hai = H.ai; H.ai = null; H.st = 'ko'; H.koT = 1e9;
          const n = __open(5) || __open(4); __place(P, n.x, n.z, n.h, 0); P.charging = true;
          T.orbSpawn(); o.k = 1; o.x = n.x + 9; o.z = n.z - 4; o.base = n.h; o.tx = o.x; o.tz = o.z; for (let i = 0; i < 10; i++) { P.spd = 0; T.step(0.012); o.tx = o.x; o.tz = o.z; }
          return 'ok'; })()""")
        await pg.wait_for_timeout(350); await pg.screenshot(path='gen/s26_edge.png')
        # orb ahead but far: the marker rides above it
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, o = T.orb; o.x = P.x + 1.5; o.z = P.z + 13; o.tx = o.x; o.tz = o.z; const g = T.surfaceUnder(o.x, o.z, 10, true); o.base = g > -Infinity ? g : P.y; for (let i = 0; i < 10; i++) { P.spd = 0; T.step(0.012); o.tx = o.x; o.tz = o.z; } return 'ok'; })()""")
        await pg.wait_for_timeout(1900); await pg.screenshot(path='gen/s26_far.png')
        print('errors', errs); await b.close()
asyncio.run(main())
