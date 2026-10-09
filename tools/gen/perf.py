import asyncio
from playwright.async_api import async_playwright
import sys
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + (sys.argv[1] if len(sys.argv) > 1 else 'pc_t.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100)
        await pg.evaluate('window.__noLoop=true; window.__fixedPR=true; __T.AU.init(); for (const k in __T.AU) if (typeof __T.AU[k] === "function") __T.AU[k] = () => {};')
        r = await pg.evaluate("""(()=>{ const T=__T; T.setDiff('hard'); T.start(); T.setAI('hard'); T.aiReset(T.P); for (let i=0;i<2500;i++){ T.setAI('hard'); T.aiStep(T.P,0.012); T.steerIn=T.P.steer; T.step(0.012); }
          let t0=performance.now(); for (let i=0;i<100;i++) T.aiThink(T.H); const think=(performance.now()-t0)/100;
          t0=performance.now(); for (let i=0;i<500;i++) T.step(0.012); const step=(performance.now()-t0)/500;
          t0=performance.now(); for (let i=0;i<5;i++) T.genWorld(1000+i); const gen=(performance.now()-t0)/5;
          return {think, step, gen}; })()""")
        print(r)
        await b.close()
asyncio.run(main())
