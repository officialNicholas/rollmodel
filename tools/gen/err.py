import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844})
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + (sys.argv[1] if len(sys.argv) > 1 else 'hi') + "', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); msgs = []
        pg.on('pageerror', lambda e: msgs.append('PAGEERROR ' + str(e)[:600])); pg.on('console', lambda m: m.type == 'error' and msgs.append('ERR ' + m.text[:600]))
        await pg.goto('file://' + SP + 'pc_t.html'); await pg.wait_for_timeout(8000)
        print('\n'.join(msgs[:6])); await b.close()
asyncio.run(main())
