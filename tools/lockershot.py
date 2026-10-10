import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
W, H, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'%s', name:'Juliana', seen:{steer:1,look:1}, owned:['flower'], bought:[], drops:68, look:{head:null, eyes:'edgy', iris:'violet'}, colorId:'pink' })); } catch (e) {}" % ('land' if W > H else 'port'))
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{WS}/ui/locker_{tag}.png')
        print(tag, await pg.evaluate("(() => { const q = s => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; }; return { look: q('#look'), top: q('.lktop'), sw: q('#swatches'), cats: q('#lookCats'), cat: q('#lc-eyes'), rail: q('#lookRail'), done: q('#lookDone'), unlock: q('#look .unlockall, #look .lkall, #unlockAll') }; })()"), errs[:2])
        await b.close()
asyncio.run(main())
