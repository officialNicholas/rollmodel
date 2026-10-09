import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); await pg.wait_for_timeout(300)
        out = []
        for who in ['P', 'H']:
            r = await pg.evaluate("""(who) => { const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<120;i++) T.step(0.012);
              let spot=null, bc=-1; for (const n of T.NAVo.nodes) { if (n.h!==0||n.edge!==0) continue; let mc=99; for (let a=0;a<12;a++){ let c=0; for (let d=0.5; d<=9; d+=0.5){ const x=n.x+Math.sin(a/12*6.283)*d, z=n.z+Math.cos(a/12*6.283)*d; if (T.surfaceUnder(x,z,0.3)!==0||T.blockedAt(x,z,0)) break; c=d; } mc=Math.min(mc,c); } if (mc>bc) { bc=mc; spot=n; } }
              const A = who === 'P' ? P : H, B = who === 'P' ? H : P;
              for (const D of [P, H]) Object.assign(D, { st: 'play', y: 0, air: false, vy: 0, slam: false, missile: false, rollT: 0, rollCD: 0, stunT: 0, stunGuard: 0, immuneT: 0, flatT: 0, charging: false, giantT: 0, power: null, paint: 1, dry: false, passT: 0 });
              H.ai = null; P.ai = null; T.steerIn = 0;
              Object.assign(A, { x: spot.x, z: spot.z - 3.2, yaw: 0, spd: 5.4 }); Object.assign(B, { x: spot.x + 0.15, z: spot.z, yaw: Math.PI, spd: 0 });
              T.dodgeRoll(A); const y0 = A.yaw; let stunAt = -1, sp0 = 0, log = [];
              for (let i = 0; i < 90; i++) { if (A === H) H.steer = 0; T.step(0.012); B.spd = 0; if (stunAt < 0 && B.stunT > 0) { stunAt = i; sp0 = A.spd; } if (i % 10 === 0) log.push([+A.z.toFixed(2), +A.spd.toFixed(2)]); }
              return { who, stunned: stunAt >= 0, yawChange: +(A.yaw - y0).toFixed(3), spdAtStun: +sp0.toFixed(2), spdAfter: +A.spd.toFixed(2), passedB: A.z > B.z + 0.8, az: +A.z.toFixed(2), bz: +B.z.toFixed(2), bStun: +B.stunT.toFixed(2), log }; }""", who)
            out.append(r)
        print(json.dumps(out, indent=1), errs[:3]); await b.close()
asyncio.run(main())
