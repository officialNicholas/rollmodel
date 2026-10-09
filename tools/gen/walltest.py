import asyncio, json, sys
from playwright.async_api import async_playwright
PAGE = sys.argv[1]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + PAGE
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.evaluate("(()=>{ window.__noLoop=true; __T.genWorld(11); __T.mapUsed=false; __T.showMenu(); __T.start(); })()")
        r = await pg.evaluate(r"""(() => { const T = __T, P = T.P, H = T.H; H.ai = null; H.st = 'ko'; H.koT = 1e9; H.x = 99; T.setWx('clear', 999);
          for (let i = 0; i < 200; i++) T.step(0.012);
          // a tall grounded box with a long -x face and open floor in front of it
          const bx = T.BOXES.filter(b => b[4] === 0 && b[5] > 1 && (b[3] - b[2]) > 3 && b[6] !== 'c' && b[6] !== 'g').find(b => { for (let d = 0.5; d < 4; d += 0.5) for (const zz of [-1, 0, 1]) { const x = b[0] - d, z = (b[2] + b[3]) / 2 + zz; if (T.surfaceUnder(x, z, 0.3) !== 0 || T.blockedAt(x, z, 0)) return false; } return true; });
          if (!bx) return 'nobox';
          const out = [];
          for (const ang of [0, 20, 45, 70]) {
            const cz = (bx[2] + bx[3]) / 2, a = Math.PI / 2 - ang * Math.PI / 180;   // yaw PI/2 = +x, straight into the face
            P.st = 'play'; P.air = false; P.y = 0; P.x = bx[0] - 1.6; P.z = cz - Math.cos(a) * 1.6 / Math.max(0.3, Math.sin(a)) * 0; P.yaw = a; P.spd = 6; P.turn = 0; P.kx = P.kz = 0; P.bonkCD = 0; P.stuck = 0; P.paint = 1; T.steerIn = 0;
            let hitT = null, y0 = P.yaw; const tr = [];
            for (let i = 0; i < 70; i++) { T.step(0.012); if (hitT === null && Math.abs(wr(P.yaw - y0)) > 0.05) hitT = i; tr.push([P.x, P.z]); }
            const after = tr[tr.length - 1], dxBack = (bx[0] - 0.34) - after[0];
            out.push({ ang, newHeadingVsWallDeg: +(Math.abs(wr(P.yaw - Math.PI / 2)) * 180 / Math.PI).toFixed(0), spd: +P.spd.toFixed(2), backFromWall: +dxBack.toFixed(2), along: +(after[1] - cz).toFixed(2) });
          }
          function wr(a) { return Math.atan2(Math.sin(a), Math.cos(a)); }
          return out; })()""")
        print(PAGE, json.dumps(r)); print(errs[:2]); await b.close()
asyncio.run(main())
