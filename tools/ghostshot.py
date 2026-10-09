import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
HIDE = "(on) => { const I = __T.VP.slime; let n = 0; I.root.traverse(o => { if (o.isMesh && o.material && o.material.depthFunc === 4) { o.visible = on; n++; } }); return n; }"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['flower','lashes'], bought:['flower','lashes'], look:{eyes:'dot', iris:'violet', head:'flower', lash:'lashes'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(9000); await pg.evaluate("window.__idleForce = 'still'"); await pg.wait_for_timeout(1200)
        await pg.screenshot(path=f'{WS}/ui/ghost_locker_a.png', clip={'x': 100, 'y': 60, 'width': 190, 'height': 170})
        print('xray meshes', await pg.evaluate("(" + HIDE + ")(false)")); await pg.wait_for_timeout(600)
        await pg.screenshot(path=f'{WS}/ui/ghost_locker_b.png', clip={'x': 100, 'y': 60, 'width': 190, 'height': 170})
        await pg.evaluate("(" + HIDE + ")(true)"); await pg.evaluate("window.__idleForce = null; document.getElementById('lookDone').click()"); await pg.wait_for_timeout(400)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1400); await pg.screenshot(path=f'{WS}/ui/ghost_card.png', clip={'x': 0, 'y': 60, 'width': 195, 'height': 420})
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
