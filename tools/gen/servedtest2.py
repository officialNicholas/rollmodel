import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('http://127.0.0.1:8765/pc_served_dbg.html', timeout=240000)
        await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.wait_for_timeout(4000)
        q = "() => { const T = __T, V = T.VP, I = V.slime; const vis = o => { for (; o; o = o.parent) if (!o.visible) return false; return true; }; return { ready: T.SLIME && T.SLIME.S.ready, failed: T.SLIME && T.SLIME.S.failed, attached: !!I, rootVis: I && I.root.visible, chain: I && vis(I.root), old: V.oldBlob && V.oldBlob.visible, drop: V.root.visible, state: T.state, look: T.lookOpen, op: V.mat.opacity, form: I && I.form, P: [T.P.x, T.P.y, T.P.z].map(v => +v.toFixed(2)), cam: [T.camera.position.x, T.camera.position.y, T.camera.position.z].map(v => +v.toFixed(2)), rs: I && [I.root.scale.x, I.root.scale.y], bodyS: V.body.scale.x }; }"
        print('boot', await pg.evaluate(q))
        await pg.mouse.click(195, 600); await pg.wait_for_timeout(6000)
        print('menu', await pg.evaluate(q))
        await pg.evaluate("() => { const b = document.getElementById('lookBtn'); if (b) b.click(); }")
        for i in range(4):
            await pg.wait_for_timeout(4000); print('look', i, await pg.evaluate(q))
        await pg.screenshot(path='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/served4.png', timeout=120000)
        print('errors', errs[:8]); await b.close()
asyncio.run(main())
