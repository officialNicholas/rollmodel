import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 300})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); logs = []
        pg.on('console', lambda m: logs.append(m.text) if m.type in ('error', 'warning') and ('Shader' in m.text or 'ERROR' in m.text or 'shader' in m.text.lower()) else None)
        pg.on('pageerror', lambda e: logs.append('PAGE ' + str(e)[:500]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("() => { const T = __T; T.mode = 'solo'; T.applyMode(); T.start(); }")
        await pg.wait_for_timeout(4000)
        for l in logs[:4]:
            # print the error lines and a bit of context around ERROR markers
            lines = l.split('\n'); errs = [i for i, x in enumerate(lines) if 'ERROR' in x]
            print('----', lines[0][:200])
            for i in errs[:6]:
                for k in range(max(0, i - 1), min(len(lines), i + 2)): print('   ', lines[k][:260])
            if not errs: print('\n'.join(x[:200] for x in lines[:12]))
        await b.close()
asyncio.run(main())
