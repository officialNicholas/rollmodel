import asyncio, time
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        bad = 0
        for i in range(60):
            pg = await b.new_page(viewport={'width':390,'height':844})
            logs=[]; pg.on('pageerror', lambda e: logs.append('ERR '+str(e)+' | '+(e.stack or '')[:400])); pg.on('console', lambda m: logs.append('CON '+m.type+' '+m.text[:200]))
            t0=time.time()
            try:
                await pg.goto(U, timeout=30000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=15000)
            except Exception as e:
                bad += 1; print(i, 'FAILED after', round(time.time()-t0,1), 's', str(e)[:100]); print('   ', [l for l in logs if 'TUNNEL' not in l][:5])
                try:
                    st = await pg.evaluate("document.readyState + ' three=' + (typeof THREE)", )
                    print('   state', st)
                except Exception as e2: print('   eval failed', str(e2)[:100])
            await pg.close()
        print('bad', bad)
        await b.close()
asyncio.run(main())
