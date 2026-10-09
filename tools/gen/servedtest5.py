import asyncio, time
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True, reduced_motion='reduce')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); logs = []; t0 = time.time()
        pg.on('pageerror', lambda e: logs.append('PAGE ' + str(e)[:300]))
        pg.on('console', lambda m: logs.append('%.1fs %s %s' % (time.time() - t0, m.type, m.text[:160])) if ('slime' in m.text.lower() or m.type == 'error') and 'TUNNEL' not in m.text else None)
        pg.on('requestfinished', lambda r: logs.append('%.1fs got %s' % (time.time() - t0, r.url.split('/')[-1])) if r.url.endswith(('.txt', '.pack')) else None)
        await pg.goto('http://127.0.0.1:8765/pc_served_dbg.html', timeout=240000)
        await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=300000)
        q = "() => { const T = __T, V = T.VP, I = V.slime; return { ready: T.SLIME.S.ready, failed: T.SLIME.S.failed, attached: !!I, meshes: Object.keys(T.SLIME.S.geo).length, tex: Object.keys(T.SLIME.S.tex).length }; }"
        print('at __T (%.1fs)' % (time.time() - t0), await pg.evaluate(q))
        await pg.mouse.click(195, 600)
        await pg.wait_for_function('__T.SLIME.S.ready && !!__T.VP.slime', polling=500, timeout=400000)
        print('attached at %.1fs' % (time.time() - t0), await pg.evaluate(q)); await pg.wait_for_timeout(3000)
        await pg.evaluate("() => { const b = document.getElementById('lookBtn'); if (b) b.click(); }"); await pg.wait_for_timeout(9000)
        print('look', await pg.evaluate("() => { const V = __T.VP, I = V.slime; return { rootVis: I && I.root.visible, old: V.oldBlob && V.oldBlob.visible, look: __T.lookOpen }; }"))
        await pg.screenshot(path='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/served5.png', timeout=120000)
        for l in logs[:12]: print(l)
        await b.close()
asyncio.run(main())
