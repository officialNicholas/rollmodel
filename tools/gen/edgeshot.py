import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        for k, tag in [(0, 'edge_hole'), (1, 'edge_rim')]:
            r = await pg.evaluate(r"""(k)=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); H.ai=null; H.x = P.x + 30;
              let x, z, yaw;
              if (k === 0) { const h = T.HOLES[0]; const cx=(h[0]+h[1])/2, cz=(h[2]+h[3])/2, r=(h[1]-h[0])/2; x = cx; z = h[2] - 2.2; yaw = 0; }
              else { x = 4; z = T.ARENA - 5; yaw = 0.5; }
              P.x=x; P.z=z; P.y=0; P.air=false; P.vy=0; P.yaw=yaw; P.st='play'; P.spd=0;
              for (let i=0;i<60;i++) { T.step(0.012); P.spd=0; P.x=x; P.z=z; P.yaw=yaw; T.visuals(0.012, 0.05); } T.renderFrame(); return T.HOLES.length; }""", k)
            print(tag, r); await pg.wait_for_timeout(150); await pg.screenshot(path=f'ui/{tag}.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
