import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_timeout(2000)
        r = await pg.evaluate("""(()=>{ const out=[]; for (let s=1;s<=12;s++){ const L=__T.genLayout(s*1000+7); __T.applyLayout(L); __T.rebuildSamples(); __T.buildNav();
            const N=__T.NAVo.nodes.length, c=__T.navCore(__T.rng(s)); let ok; try { ok=__T.placeItems(L, __T.rng(s*31)); } catch(e){ ok='ERR '+e.message; }
            out.push({s, sym:L.sym, arch:L.arch, boxes:L.boxes.length, ramps:L.ramps.length, holes:L.holes.length, clouds:L.clouds.length, N, core:c.count, ok, pots:__T.POTS.length, riv:__T.RIVALS.length}); } return out; })()""")
        for x in r: print(x)
        print(errs)
        await b.close()
asyncio.run(main())
