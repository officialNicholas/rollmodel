import asyncio, json, sys
from playwright.async_api import async_playwright
B='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
f = sys.argv[1]; seed = int(sys.argv[2])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844})
        await ctx.add_init_script("Math.random = (()=>{ let s=%d; return ()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; }; })();" % seed)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:200]))
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Debugger.enable')
        paused = asyncio.get_event_loop().create_future()
        cdp.on('Debugger.paused', lambda e: paused.done() or paused.set_result(e))
        await pg.goto(B+f, wait_until='commit')
        try:
            await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=20000); print('loaded ok', errs[:3])
        except Exception as e:
            print('timeout -> pausing'); await cdp.send('Debugger.pause'); ev = await asyncio.wait_for(paused, 10)
            print(len(ev['callFrames']), ev.get('reason')); [print(fr['functionName'], fr['location']['lineNumber'], fr['location'].get('columnNumber'), fr.get('url','')[-30:]) for fr in ev['callFrames'][:15]]; st = ev.get('asyncStackTrace'); print(st and [c['functionName'] for c in st['callFrames'][:10]])
        await b.close()
asyncio.run(main())
