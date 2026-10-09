import asyncio, json, sys
from playwright.async_api import async_playwright
B='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
f = sys.argv[1]; seed = int(sys.argv[2])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844})
        await ctx.add_init_script("Math.random = (()=>{ let s=%d; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })();" % seed)
        pg = await ctx.new_page(); msgs=[]; pg.on('pageerror', lambda e: msgs.append('PE '+str(e.stack)[:900])); pg.on('console', lambda m: msgs.append(m.type+' '+m.text[:200]))
        await pg.goto(B+f)
        await pg.wait_for_timeout(8000)
        print(await pg.evaluate("[document.readyState, typeof THREE, typeof __T, !!document.getElementById('menu')]"))
        for m in msgs[:10]: print(m)
        await b.close()
asyncio.run(main())
