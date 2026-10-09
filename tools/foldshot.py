import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, tag in [(390, 780, 'port'), (844, 390, 'land')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{steer:1,look:1}, owned:['flower','pirate'], bought:['flower'], drops:200, look:{head:'flower', eyes:'edgy', iris:'violet'} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(7500)
            print(tag, await pg.evaluate("(() => { const r = document.getElementById('look').getBoundingClientRect(); return { sheetTop: Math.round(r.top), frac: +(r.height / innerHeight).toFixed(3), stage: +(r.top / innerHeight).toFixed(3), tab: document.getElementById('look').dataset.tab, scroll: document.getElementById('look').scrollHeight > document.getElementById('look').clientHeight }; })()"))
            await pg.screenshot(path=f'{WS}/ui/fold_{tag}_paint.png')
            for cat in ['eyes', 'head']:
                await pg.evaluate("document.getElementById('lc-" + cat + "').click()"); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{WS}/ui/fold_{tag}_{cat}.png')
            print(tag, 'errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
