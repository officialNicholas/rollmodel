import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000)
        await pg.evaluate('window.__noLoop=true')
        r = await pg.evaluate("""(()=>{ const out={}; for (let s=1;s<300;s++){ const L=__T.genLayout(s); const k=L.arch+'/'+L.theme; if(!out[k]) out[k]=s; } return out; })()""")
        print(json.dumps(r))
        await b.close()
asyncio.run(main())
