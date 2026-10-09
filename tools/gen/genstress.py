import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000)
        await pg.evaluate('window.__noLoop=true')
        r = await pg.evaluate("""(()=>{ const bad=[]; let maxMs=0; for (let i=0;i<400;i++){ const s=(Math.random()*4294967296)>>>0; const t0=performance.now(); try { __T.genWorld(s); __T.mapUsed=false; __T.showMenu(); } catch(e){ bad.push([s, String(e), (e.stack||'').split('\\n').slice(0,4).join(' / ')]); } maxMs=Math.max(maxMs, performance.now()-t0); } return {bad: bad.slice(0,5), nbad: bad.length, maxMs}; })()""")
        print(r)
        await b.close()
asyncio.run(main())
