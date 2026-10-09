import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_TUNNEL' not in m.text and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_timeout(2500)
        print('errors', errs)
        if errs: await b.close(); return
        g = await pg.evaluate("({...__T.GEN, boxes:__T.BOXES.length, ramps:__T.RAMPS.length, holes:__T.HOLES.length, pots:__T.POTS.length, rivals:__T.RIVALS.length, pw:__T.POWER_SPOTS.length, cof:__T.COF_SPOTS.length, nodes:__T.NNodes, NS:__T.NSv, start:__T.START, cstart:__T.CSTART})")
        print(json.dumps(g))
        await pg.screenshot(path='gen/menu.png')
        await b.close()
asyncio.run(main())
