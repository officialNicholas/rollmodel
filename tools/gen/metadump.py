import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 300, 'height': 300})
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""() => { const M = __T.SLIME.S.meta.slime; const I = __T.VP.slime; return { meta: M, rootScale: I.root.scale.toArray(), grpScale: I.groups.slime.scale.toArray(), body: __T.VP.root ? __T.VP.root.scale.toArray() : null }; }""")
        print(json.dumps(r)[:3000]); await b.close()
asyncio.run(main())
