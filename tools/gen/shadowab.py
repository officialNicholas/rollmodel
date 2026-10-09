import asyncio, json
from playwright.async_api import async_playwright
B='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for f, tag in [('pc_t.html','new'), ('pc_t_old.html','old')]:
            ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("Math.random = (()=>{ let s=4242; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })(); try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(B+f); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
            r = await pg.evaluate(r"""(()=>{ const T=__T, P=T.P, H=T.H; window.__noLoop = true; T.mode='duel'; T.applyMode(); T.mapUsed=true; T.freshMap(); T.showMenu(); T.start(); for (let i=0;i<110;i++) T.step(0.012); T.showBlobs(); H.ai=null; H.x=P.x+40;
              let best=null; for (const b of T.BOXES) if (b[4] > 0.5) { best=b; break; } if (!best) best = T.BOXES[0];
              const x=(best[0]+best[1])/2 - 1.5, z=(best[2]+best[3])/2 - 4; P.x=x; P.z=z; P.y=0; P.yaw=0.3; P.spd=0; P.st='play';
              for (let i=0;i<60;i++) { T.step(0.012); P.spd=0; P.x=x; P.z=z; P.yaw=0.3; T.visuals(0.012, 0.05); } T.renderFrame(); return [best, T.BOXES.length]; })()""")
            print(tag, r); await pg.wait_for_timeout(200); await pg.screenshot(path=f'ui/shadow_{tag}.png'); await ctx.close()
        await b.close()
asyncio.run(main())
