import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("window.__noStep=true")
        for paint in [0.20, 0.249, 0.30, 0.45, 0.80]:
            r = await pg.evaluate("""(pt)=>{ const T=__T, P=T.P, H=T.H; T.setWx('clear', 60); H.st='ko'; H.koT=99;
              const n=T.NAVo.nodes.find(m=>m.h===0&&m.edge===0&&!T.rivals.some(r=>Math.hypot(r.x-m.x,r.z-m.z)<4));
              P.st='play'; P.x=n.x; P.z=n.z; P.y=0; P.air=false; P.spd=0; P.slamCD=0; P.paint=pt; P.slam=false; P.inkRush=false;
              const ready=T.slamReadyP; const ok=T.useSlam(P); const after=P.paint; let k=0; while((P.air||P.slam)&&k<300){ T.step(0.012); k++; }
              return {paint:pt, ready, pounded:ok, afterPound:+after.toFixed(3), landed:P.st}; }""", paint)
            print(r)
        # button shows ready on exactly one bar
        await pg.evaluate("""(()=>{ const T=__T, P=T.P; P.paint=0.25; P.slamCD=0; P.st='play'; P.air=false; P.slam=false; })()""")
        await pg.wait_for_timeout(300)
        print('button classes at one bar:', await pg.evaluate("document.getElementById('slamBtn').className"), '|', await pg.evaluate("document.getElementById('slamBtn').getAttribute('aria-label')"))
        await pg.screenshot(path='gen/onebar.png')
        await pg.evaluate("__T.P.paint=0.2"); await pg.wait_for_timeout(300)
        print('button classes below one bar:', await pg.evaluate("document.getElementById('slamBtn').className"), '|', await pg.evaluate("document.getElementById('slamBtn').getAttribute('aria-label')"))
        print('errors', errs)
        await b.close()
asyncio.run(main())
