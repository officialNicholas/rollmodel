import asyncio, json
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
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; T.setWx('clear', 999); window.__hai = H.ai; H.ai = null; H.x = 99; H.st = 'ko'; H.koT = 1e9;
          const boxes = T.BOXES.map((b, i) => ({ i, b, w: b[1] - b[0], d: b[3] - b[2] })).filter(o => o.b[4] > 0.1 && o.w > 3 && o.d > 3);
          const kinds = T.BOXES.map(b => [b[4].toFixed(1), b[5].toFixed(1), (b[1]-b[0]).toFixed(1), (b[3]-b[2]).toFixed(1)].join('/'));
          if (!boxes.length) return { none: true, kinds };
          const o = boxes[0], b = o.b, cx = (b[0] + b[1]) / 2, cz = (b[2] + b[3]) / 2;
          T.showBlobs(); P.st = 'play'; P.x = cx - o.w * 0.15; P.z = cz; P.y = b[5]; P.air = false; P.yaw = Math.PI / 2; P.spd = 4; P.paint = 1;
          const c0 = T.teamCov(0), v0 = T.chunkN; for (let i = 0; i < 60; i++) { T.step(0.012); P.yaw = Math.PI / 2; }
          const c1 = T.teamCov(0), v1 = T.chunkN; P.x = cx; P.z = cz; P.y = b[5]; P.air = false; P.spd = 0; P.slamCD = 0; const ok = T.useSlam(P); window.__ok = ok; for (let i = 0; i < 80; i++) { T.step(0.012); } window.__sl = P.slams;
          const c2 = T.teamCov(0), v2 = T.chunkN; P.st = 'ko'; P.koT = 1e9;
          window.__cam = [[cx - 4, b[5] + 7, cz - 6], [cx, b[5], cz]];
          return { ok: window.__ok, slams: window.__sl, box: b.map(v => +v.toFixed(2)), rollCov: +(c1 - c0).toFixed(3), rollVerts: v1 - v0, jumpCov: +(c2 - c1).toFixed(3), jumpVerts: v2 - v1, Py: +P.y.toFixed(2), kinds: kinds.slice(0, 12) }; })()""")
        print(json.dumps(r)); await pg.wait_for_timeout(500); await pg.screenshot(path='gen/s33_float.png'); print(errs); await b.close()
asyncio.run(main())
