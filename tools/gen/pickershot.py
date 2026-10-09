# the world picker (no Season 2, names only), the Halloween grid after tapping its card, a canvas picked; Customize with the name field
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'pk'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h in [(390, 844), (844, 390)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'perf', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
            await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
            await pg.wait_for_timeout(1500)
            await pg.screenshot(path=f'st/{TAG}_home_{w}.png')
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'st/{TAG}_worlds_{w}.png')
            await pg.evaluate("document.querySelector('#stagePick .world[data-s=season]').click()"); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'st/{TAG}_grid_{w}.png')
            await pg.evaluate("document.querySelector('#seasonGrid .stg[data-s=manor]').click()"); await pg.wait_for_timeout(1800)
            st = await pg.evaluate("() => ({ sel: __T.stageSel, theme: __T.TH.id, title: document.getElementById('worldTitle').textContent, cv: document.getElementById('cvName').textContent })")
            await pg.screenshot(path=f'st/{TAG}_picked_{w}.png')
            await pg.evaluate("document.getElementById('worldBack').click()"); await pg.wait_for_timeout(500)
            st2 = await pg.evaluate("() => ({ sel: __T.stageSel, title: document.getElementById('worldTitle').textContent, page: __T.menuPage, gridHidden: document.getElementById('seasonGrid').hidden })")
            await pg.evaluate("document.getElementById('worldBack').click()"); await pg.wait_for_timeout(500)
            await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(1500)
            await pg.screenshot(path=f'st/{TAG}_look_{w}.png')
            nm = await pg.evaluate("() => { const i = document.getElementById('lookName'); const v0 = i.value; i.value = 'Blobby'; i.dispatchEvent(new Event('input')); return [v0, JSON.parse(localStorage.getItem('paint-world-red.v1')).name]; }")
            print(w, h, json.dumps(st), json.dumps(st2), json.dumps(nm), errs[:3])
            await ctx.close()
        await b.close()
asyncio.run(main())
