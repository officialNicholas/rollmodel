import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
tag = sys.argv[1] if len(sys.argv) > 1 else 'a'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for name, vw, vh, orient in [('port', 390, 780, 'port'), ('land', 844, 390, 'land'), ('wide', 1280, 720, 'land')]:
            ctx = await b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + orient + "', name:'Dusk', seen:{steer:1,look:1}, owned:['hat'], bought:['hat'], drops:240, look:{iris:'violet'} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            await pg.evaluate("__T.heroSpeak('The critics are watching.')")
            await pg.wait_for_timeout(900)
            r = await pg.evaluate("(() => { const q = id => { const e = document.getElementById(id); if (!e) return null; const r = e.getBoundingClientRect(); return [r.left|0, r.top|0, r.right|0, r.bottom|0]; }; return { say: q('heroSay'), stat: q('statDrops'), logo: q('mLogo'), ltop: (document.querySelector('.ltop') || {getBoundingClientRect(){return{}}}).getBoundingClientRect().bottom }; })()")
            print(name, r, errs[:2])
            await pg.screenshot(path=f'{WS}/ui/say_{name}_{tag}.png')
            await ctx.close()
        await b.close()
asyncio.run(main())
