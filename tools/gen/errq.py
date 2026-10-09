import asyncio, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':1280,'height':760})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e) + ' ' + (e.stack or '')[:600]))
        pg.on('console', lambda m: m.type in ('error','warning') and errs.append(m.type + ' ' + m.text[:1500]))
        await pg.goto(U)
        try: await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        except Exception as e: print('no __T')
        await pg.wait_for_timeout(1500)
        for e in errs[:8]: print(e); print('---')
        await b.close()
asyncio.run(main())
