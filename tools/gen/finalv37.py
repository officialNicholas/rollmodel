import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("Math.random = (()=>{ let s=4321; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ mode: 'trio', seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        r = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P, H=T.H, H2=T.H2; window.__noLoop = true; T.mode='trio'; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); T.aiReset(P);
          for (let i=0;i<1500;i++){ T.aiStep(P,0.012); T.steerIn=P.steer; T.step(0.012); if (P.st==='ko') { P.st='play'; P.koT=0; } }
          T.setWx('clear', 99); for (let i=0;i<60;i++) T.step(0.012); P.ai = null; const h = T.HOLES.find(h => h[6] !== 'c') || T.HOLES[0]; const x = (h[0]+h[1])/2, z = h[2] - 3.4;
          P.x=x; P.z=z; P.y=0; P.air=false; P.vy=0; P.yaw=0; P.spd=0; P.st='play';
          for (const [D, dx, dz] of [[H, -3.2, 2.4], [H2, 3.0, 3.0]]) { D.ai = null; D.x = x + dx; D.z = z + dz; D.y = 0; D.air=false; D.vy=0; D.st='play'; D.yaw = Math.PI; D.spd = 0; }
          for (let i=0;i<45;i++) { T.step(0.012); P.spd=0; P.x=x; P.z=z; P.yaw=0; T.visuals(0.016, 0.05); } T.renderFrame(); return [T.HOLES.length, T.mode]; })()""")
        print(r); await pg.wait_for_timeout(6500); await pg.evaluate('(()=>{ for (let i=0;i<10;i++) __T.visuals(0.016,0.016); __T.renderFrame(); })()'); await pg.screenshot(path='ui/v37_final.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
